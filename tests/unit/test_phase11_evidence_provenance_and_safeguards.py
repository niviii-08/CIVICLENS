"""
Unit Tests for Phase 11.1, 11.6 & 11.7 — Provenance, Grievance Sync & Safeguards
"""
import pytest
from datetime import datetime, timezone
from backend.models.provenance import (
    GranularExtractionLineage, RightOfReplyRegistry, PublicCorrectionNotice,
    DPDPAComplianceRequest, LinkHealthStatus, RightOfReplyStatus, DPDPAStatus,
    DataSubjectRequestType
)
from backend.services.grievance_sync_service import GrievanceSyncService, SyncEventType
from backend.services.evidence_graph_expansion_service import EvidenceGraphExpansionService


def test_extraction_lineage_registration(db_session):
    """Verify granular extraction lineage recording page, table, and row coordinates."""
    lineage = GranularExtractionLineage(
        target_table="budget_records",
        target_record_id="REC-2024-001",
        source_document_title="Demand 19 School Education FY 2024-25",
        source_url="https://tn.gov.in/budget/demand19.pdf",
        document_sha256="abc123sha256demo",
        page_number=18,
        table_index=2,
        row_number=5,
        column_name="Actuals 2022-23",
        extracted_verbatim_text="Rs. 44,042.88 crore",
        link_health=LinkHealthStatus.ONLINE_VERIFIED,
    )
    db_session.add(lineage)
    db_session.commit()
    assert lineage.id is not None
    assert lineage.page_number == 18
    assert lineage.row_number == 5


def test_dpdpa_data_subject_request(db_session):
    """Verify DPDPA 2023 / DPDP Rules 2025 compliance request logging."""
    req = DPDPAComplianceRequest(
        request_reference="DPDPA-2024-001",
        request_type=DataSubjectRequestType.ERASURE_PII,
        data_principal_hash="hash_pseudonym_citizen_99",
        affected_record_table="civic_issues",
        affected_record_id="ISSUE-2024-991",
        status=DPDPAStatus.ACTION_TAKEN_REDACTED,
        resolution_notes="Removed citizen phone number and house address from public issue description.",
    )
    db_session.add(req)
    db_session.commit()
    assert req.id is not None
    assert req.status == DPDPAStatus.ACTION_TAKEN_REDACTED


def test_grievance_appellate_sync_discipline(db_session):
    """Verify grievance sync service prevents assuming rejection during quarterly appellate window."""
    # When sync is older than 7 days, status must be explicitly PENDING_APPELLATE_REVIEW
    res = GrievanceSyncService.evaluate_appeal_status_discipline(
        db=db_session,
        issue_id="ISSUE-APPEAL-01",
        days_since_last_sync=14,
    )
    assert res["epistemic_status"] == "PENDING_APPELLATE_REVIEW"
    assert res["assumed_rejected"] is False
    assert res["is_closed"] is False
    assert "EPISTEMIC GUARDRAIL" in res["guideline"]


def test_graph_coverage_metrics(db_session):
    """Verify evidence graph coverage and connectivity metrics calculation."""
    metrics = EvidenceGraphExpansionService.get_graph_coverage_metrics(db_session)
    assert "total_nodes" in metrics
    assert "total_edges" in metrics
    assert "connectivity_coverage_pct" in metrics
    assert metrics["max_supported_traversal_hops"] == 4
