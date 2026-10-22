"""
CIVICLENS TN — Unit Tests for Dataset Freshness & Update Operations
===================================================================
All tests evaluate cadence-adjusted freshness, failure diagnostics,
partial import recovery, citizen-facing labels, and REST endpoints.
Uses isolated synthetic timestamps without fabricating production data.
"""

import pytest
from datetime import datetime, timezone, timedelta
from backend.ops.freshness_manager import (
    DatasetFreshnessManager,
    SourceUpdateMethod,
    PublicationCadence,
    IngestionHealthStatus,
    HealthIssueType,
    VERIFIED_SOURCES_CATALOG,
    SourceFreshnessConfig,
)
from backend.api.app import create_app


@pytest.fixture
def freshness_manager():
    """Isolated DatasetFreshnessManager instance."""
    return DatasetFreshnessManager()


@pytest.fixture
def test_client():
    """Flask test client with registered freshness endpoints."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# -----------------------------------------------------------------------------
# Test Cases
# -----------------------------------------------------------------------------

def test_verified_source_catalog_cadences_and_methods(freshness_manager):
    """Verify all 22 verified sources are cataloged with authentic update methods and non-daily cadences."""
    catalog = freshness_manager.catalog
    assert len(catalog) >= 22

    # Check Budget Demands (Annual, Manual)
    bud = catalog["SRC-BUD-001"]
    assert bud.update_method == SourceUpdateMethod.MANUAL
    assert bud.expected_cadence == PublicationCadence.ANNUAL
    assert bud.freshness_threshold_days == 400

    # Check Gazette (Weekly, Scheduled)
    gaz = catalog["SRC-GOV-001"]
    assert gaz.update_method == SourceUpdateMethod.SCHEDULED
    assert gaz.expected_cadence == PublicationCadence.WEEKLY
    assert gaz.freshness_threshold_days == 14

    # Check Elections (5-Year Event Driven)
    elc = catalog["SRC-ELC-001"]
    assert elc.update_method == SourceUpdateMethod.EVENT_DRIVEN
    assert elc.expected_cadence == PublicationCadence.EVENT_DRIVEN
    assert elc.freshness_threshold_days == 1825

    # Check Grievances (Unavailable for automated scraping under DPDPA)
    grv = catalog["SRC-GRV-001"]
    assert grv.update_method == SourceUpdateMethod.UNAVAILABLE


def test_freshness_evaluation_healthy(freshness_manager):
    """Verify an annual source within threshold is assessed as HEALTHY and not stale."""
    # Annual budget imported within 400 days is healthy
    fixed_now = datetime(2026, 10, 22, 12, 0, 0, tzinfo=timezone.utc)
    report = freshness_manager.assess_source_freshness("SRC-BUD-001", current_time=fixed_now)

    assert report.health_status == IngestionHealthStatus.HEALTHY.value
    assert report.is_stale is False
    assert report.record_count == 680
    assert "Official Annual Release" in report.citizen_freshness_label


def test_freshness_evaluation_stale_detection(freshness_manager):
    """Verify a dataset exceeding its cadence threshold is correctly flagged as STALE."""
    # Advance time to 500 days after last import (Oct 21, 2026 + 500 days = March 2028)
    simulated_future = datetime(2028, 3, 5, 0, 0, 0, tzinfo=timezone.utc)
    report = freshness_manager.assess_source_freshness("SRC-BUD-001", current_time=simulated_future)

    assert report.is_stale is True
    assert report.health_status == IngestionHealthStatus.STALE.value
    assert "Awaiting State Publication" in report.citizen_freshness_label


def test_event_driven_sources_not_falsely_stale(freshness_manager):
    """Verify 5-year election records do not become stale after ordinary monthly or annual intervals."""
    # 2 years after 2021 election
    two_years_later = datetime(2023, 5, 2, 0, 0, 0, tzinfo=timezone.utc)
    report = freshness_manager.assess_source_freshness("SRC-ELC-001", current_time=two_years_later)

    assert report.is_stale is False
    assert report.health_status == IngestionHealthStatus.HEALTHY.value
    assert "Current 16th Legislative Assembly Election Cycle" in report.citizen_freshness_label


def test_failed_download_diagnostics(freshness_manager):
    """Verify failed downloads are recorded with issue types and sanitized messages."""
    raw_error = (
        "HTTP 502 Bad Gateway connecting to https://tnbudget.tn.gov.in/ddg.pdf "
        "with internal_token='secret_auth_token_xyz987'"
    )
    report = freshness_manager.diagnose_and_record_failure(
        source_id="SRC-BUD-001",
        issue_type=HealthIssueType.FAILED_DOWNLOAD,
        diagnostic_payload={"http_status": 502, "endpoint": "https://tnbudget.tn.gov.in/ddg.pdf"},
        error_message=raw_error
    )

    assert report.health_status == IngestionHealthStatus.FAILED.value
    assert "secret_auth_token_xyz987" not in report.last_error
    assert "[REDACTED_SECRET]" in report.last_error or "502" in report.last_error
    assert report.diagnostic_details["issue_type"] == HealthIssueType.FAILED_DOWNLOAD.value
    assert "Update Temporarily Interrupted" in report.citizen_freshness_label


def test_partial_import_and_schema_change_diagnostics(freshness_manager):
    """Verify partial imports mark status as DEGRADED and schema changes mark as FAILED."""
    # 1. Partial Import
    rep_partial = freshness_manager.diagnose_and_record_failure(
        source_id="SRC-GEO-001",
        issue_type=HealthIssueType.PARTIAL_IMPORT,
        diagnostic_payload={"expected_records": 38, "processed_records": 25},
        error_message="Batch interrupted at record 25 of 38 due to timeout."
    )
    assert rep_partial.health_status == IngestionHealthStatus.DEGRADED.value
    assert rep_partial.diagnostic_details["processed_records"] == 25

    # 2. Schema Change
    rep_schema = freshness_manager.diagnose_and_record_failure(
        source_id="SRC-GEO-001",
        issue_type=HealthIssueType.SCHEMA_CHANGE,
        diagnostic_payload={"missing_columns": ["lgd_code", "district_name"]},
        error_message="Unexpected CSV headers: missing lgd_code."
    )
    assert rep_schema.health_status == IngestionHealthStatus.FAILED.value


def test_recovery_from_failed_update(freshness_manager):
    """Verify successful import restores health status from FAILED to HEALTHY and clears error state."""
    # Step 1: Record failure
    freshness_manager.diagnose_and_record_failure(
        source_id="SRC-AUD-001",
        issue_type=HealthIssueType.HTTP_ERROR,
        diagnostic_payload={"status_code": 503},
        error_message="Service Unavailable"
    )
    failed_rep = freshness_manager.assess_source_freshness("SRC-AUD-001")
    assert failed_rep.health_status == IngestionHealthStatus.DEGRADED.value

    # Step 2: Ingest recovered batch
    recovered_rep = freshness_manager.record_successful_import(
        source_id="SRC-AUD-001",
        record_count=15,
        source_publication_date="2025-02-15"
    )
    assert recovered_rep.health_status == IngestionHealthStatus.HEALTHY.value
    assert recovered_rep.record_count == 15
    assert recovered_rep.last_error is None
    assert recovered_rep.diagnostic_details is None


def test_citizen_freshness_labels(freshness_manager):
    """Verify citizen freshness labels correctly reflect publisher cadences or missing timestamps."""
    # Protected/Unavailable source
    grv_rep = freshness_manager.assess_source_freshness("SRC-GRV-001")
    assert "Departmental Verification Feed Only (DPDPA Protected)" in grv_rep.citizen_freshness_label

    # Source without import timestamps
    custom_catalog = {
        "SRC-UNINDEXED": SourceFreshnessConfig(
            source_id="SRC-UNINDEXED",
            name="Unindexed Test Source",
            publisher="Test Agency",
            update_method=SourceUpdateMethod.MANUAL,
            expected_cadence=PublicationCadence.ANNUAL,
            freshness_threshold_days=365,
            official_url="https://example.gov.in",
            licence_terms="Open Data"
        )
    }
    custom_mgr = DatasetFreshnessManager(catalog=custom_catalog)
    unindexed_rep = custom_mgr.assess_source_freshness("SRC-UNINDEXED")
    assert unindexed_rep.citizen_freshness_label == "Timestamp Unavailable / Ingestion Pending"


def test_system_wide_freshness_assessment(freshness_manager):
    """Verify system-wide assessment aggregates all sources into structured summary."""
    summary = freshness_manager.assess_all_sources()

    assert "total_verified_sources" in summary
    assert summary["total_verified_sources"] >= 22
    assert "healthy_sources" in summary
    assert "stale_sources" in summary
    assert "unavailable_sources" in summary
    assert len(summary["sources"]) >= 22


def test_freshness_api_endpoints(test_client):
    """Verify Flask API endpoints for overview, individual source, and diagnostics."""
    # 1. Overview
    res = test_client.get("/api/freshness")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total_verified_sources"] >= 22

    # 2. Individual Source
    res_single = test_client.get("/api/freshness/SRC-BUD-001")
    assert res_single.status_code == 200
    single_data = res_single.get_json()["data"]
    assert single_data["source_id"] == "SRC-BUD-001"
    assert single_data["publisher"] == "Finance Department, Government of Tamil Nadu"

    # 3. Non-existent Source
    res_404 = test_client.get("/api/freshness/SRC-NON-EXISTENT")
    assert res_404.status_code == 404

    # 4. Diagnostics
    res_diag = test_client.get("/api/freshness/diagnostics")
    assert res_diag.status_code == 200
    diag_data = res_diag.get_json()["data"]
    assert "flagged_sources_count" in diag_data
