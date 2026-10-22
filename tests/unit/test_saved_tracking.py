"""
CIVICLENS TN — Unit Tests for Saved Civic Tracking and Live Updates
Phase 13.8: Citizen Record Tracking, Change Detection, and Privacy Controls.

Verifies:
1. Supported tracking categories catalog and privacy-conscious local storage model.
2. Record resolution across all five civic domains:
   - Election manifesto promises (PoliticalPromise)
   - Government welfare schemes (HistoricalScheme / PolicyRegistryEntry)
   - Elected representatives (Representative)
   - Public claim assessments (Claim / ClaimAssessmentService)
   - Civic grievances and municipal complaints (CivicIssue)
3. Reference validity and resilient handling of retired or deleted records.
4. Genuine change detection:
   - Status transition alerts with change date, source, and description.
   - Zero false-positive notifications on page reload / re-query.
   - Deletion / archival alerts with one-click cleanup guidance.
5. Batch deduplication and empty state handling.
6. Cross-user isolation: local-first stateless design ensures users cannot access other citizens' saved items.
7. Outbound delivery safeguards: confirms email/push notifications are disabled/unconfigured.
8. REST API Endpoints:
   - GET /api/tracking/types
   - POST /api/tracking/validate (single and batch)
   - POST /api/tracking/check-updates
   - GET /api/tracking/item/<record_type>/<record_id>
   - 400 error handling on missing fields
"""

import pytest
from backend.services.saved_tracking_service import SavedCivicTrackingService
from backend.api.app import create_app


@pytest.fixture
def service():
    return SavedCivicTrackingService()


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# 1. Catalog, Capabilities & Privacy Model
# =====================================================================

def test_get_supported_tracking_types(service):
    """Verify supported record types and privacy model disclosures."""
    meta = service.get_supported_tracking_types()

    assert "supported_record_types" in meta
    types = meta["supported_record_types"]
    assert "promise" in types
    assert "scheme" in types
    assert "representative" in types
    assert "claim" in types
    assert "civic" in types

    # Verify privacy model: no mandatory user accounts or profiling
    privacy = meta["privacy_model"]
    assert privacy["requires_account"] is False
    assert "Browser localStorage" in privacy["architecture"]
    assert privacy["telemetry_tracking"] == "Disabled (Zero profiling or behavioral tracking)"

    # Verify notification infrastructure safeguards: outbound is disabled
    notif = meta["notification_infrastructure"]
    assert notif["outbound_email_enabled"] is False
    assert notif["outbound_push_enabled"] is False
    assert notif["in_app_change_detection_enabled"] is True


# =====================================================================
# 2. Record Resolution Across All 5 Domains
# =====================================================================

def test_validate_existing_promise(service):
    """Verify resolution of an existing or canonical election promise."""
    res = service.validate_and_resolve_record("promise", "PRM-DMK-2021-001")

    assert res["is_valid"] is True
    assert res["record_type"] == "promise"
    assert "₹1,000" in res["title"]
    assert res["detail_url"] == "/promises/PRM-DMK-2021-001"
    assert res["current_status"] in ("PARTIALLY_FULFILLED", "IMPLEMENTED", "ANNOUNCED")


def test_validate_existing_scheme(service):
    """Verify resolution of an existing welfare scheme."""
    res = service.validate_and_resolve_record("scheme", "SCH-TN-KMUT")

    assert res["is_valid"] is True
    assert res["record_type"] == "scheme"
    assert "Kalaignar Magalir" in res["title"]
    assert res["detail_url"] == "/schemes/SCH-TN-KMUT"
    assert res["current_status"] is not None


def test_validate_existing_representative(service):
    """Verify resolution of an elected representative (MLA)."""
    res = service.validate_and_resolve_record("representative", "REP-MLA-013")

    assert res["is_valid"] is True
    assert res["record_type"] == "representative"
    assert "MLA" in res["title"]
    assert res["detail_url"] == "/representatives/REP-MLA-013"
    assert res["current_status"] == "INCUMBENT_MLA"


def test_validate_existing_claim(service):
    """Verify resolution of a public claim verification dossier."""
    res = service.validate_and_resolve_record("claim", "CLM-TN-2024-001")

    assert res["is_valid"] is True
    assert res["record_type"] == "claim"
    assert len(res["title"]) > 10
    assert res["detail_url"] == "/claims/CLM-TN-2024-001"
    assert "SUPPORTED" in res["current_status"]


def test_validate_existing_civic_issue(service):
    """Verify resolution of a civic complaint / grievance."""
    res = service.validate_and_resolve_record("civic", "CIV-2024-0891")

    assert res["is_valid"] is True
    assert res["record_type"] == "civic"
    assert "water" in res["title"].lower() or "grievance" in res["title"].lower()
    assert res["detail_url"] == "/civic/CIV-2024-0891"
    assert res["current_status"] is not None


# =====================================================================
# 3. Invalid & Retired Record Handling
# =====================================================================

def test_validate_nonexistent_record(service):
    """Verify non-existent or deleted records return is_valid=False with removal prompt."""
    res = service.validate_and_resolve_record("scheme", "SCH-DOES-NOT-EXIST-999")

    assert res["is_valid"] is False
    assert res["can_remove"] is True
    assert "not found" in res["error_message"].lower()


def test_validate_unsupported_type(service):
    """Verify unsupported record types fail validation gracefully."""
    res = service.validate_and_resolve_record("unsupported_category", "ITEM-001")

    assert res["is_valid"] is False
    assert "unsupported" in res["error_message"].lower()


# =====================================================================
# 4. Change Detection & Notification Suppression
# =====================================================================

def test_change_detection_status_transition(service):
    """
    Verify change detection flags genuine status transitions with date, source, and description.
    """
    # User saved promise when it was originally 'ANNOUNCED'
    res = service.check_record_update(
        record_type="promise",
        record_id="PRM-DMK-2021-001",
        last_known_status="ANNOUNCED",
    )

    assert res["has_update"] is True
    assert res["update_event"] is not None
    event = res["update_event"]
    assert event["change_type"] == "STATUS_TRANSITION"
    assert event["previous_status"] == "ANNOUNCED"
    assert event["new_status"] == "PARTIALLY_FULFILLED"
    assert event["change_source"] is not None
    assert "Status updated" in event["change_description"]


def test_change_detection_no_change_when_reloaded(service):
    """
    Instruction 7: Do NOT generate notifications merely because a page was viewed or a record reloaded.
    """
    # Look up current status first
    valid = service.validate_and_resolve_record("promise", "PRM-DMK-2021-001")
    current_status = valid["current_status"]

    # Check update with last_known_status identical to current_status
    res = service.check_record_update(
        record_type="promise",
        record_id="PRM-DMK-2021-001",
        last_known_status=current_status,
        saved_at=valid["last_updated_at"],
    )

    assert res["has_update"] is False
    assert res["update_event"] is None


def test_change_detection_for_archived_record(service):
    """Verify retired/deleted record generates an actionable cleanup notification."""
    res = service.check_record_update(
        record_type="scheme",
        record_id="SCH-ARCHIVED-000",
        last_known_status="ACTIVE",
    )

    assert res["is_valid"] is False
    assert res["has_update"] is True
    event = res["update_event"]
    assert event["change_type"] == "RECORD_DELETED_OR_ARCHIVED"
    assert event["action_required"] == "REMOVE_FROM_SAVED_LIST"


# =====================================================================
# 5. Batch Synchronization & Deduplication
# =====================================================================

def test_batch_check_updates_empty_state(service):
    """Verify empty input returns clear empty state and privacy message."""
    res = service.batch_check_updates([])

    assert res["empty_state"] is True
    assert res["total_tracked"] == 0
    assert "No civic records" in res["empty_message"]
    assert "CIVICLENS TN does not collect" in res["privacy_statement"]


def test_batch_check_updates_deduplication(service):
    """Verify duplicate items in user saved list are deduplicated."""
    items = [
        {"record_type": "promise", "record_id": "PRM-DMK-2021-001", "last_known_status": "ANNOUNCED"},
        {"record_type": "promise", "record_id": "PRM-DMK-2021-001", "last_known_status": "ANNOUNCED"},
        {"record_type": "scheme", "record_id": "SCH-TN-KMUT", "last_known_status": "ACTIVE_DISBURSEMENT"},
    ]

    res = service.batch_check_updates(items)
    assert res["total_tracked"] == 2
    assert len(res["results"]) == 2


def test_batch_check_updates_mixed(service):
    """Verify mixed batch with valid, invalid, and updated records."""
    items = [
        # Updated promise
        {"record_type": "promise", "record_id": "PRM-DMK-2021-001", "last_known_status": "ANNOUNCED"},
        # Unchanged scheme
        {"record_type": "scheme", "record_id": "SCH-TN-KMUT", "last_known_status": "ACTIVE_DISBURSEMENT"},
        # Deleted / invalid record
        {"record_type": "representative", "record_id": "REP-FAKE-9999", "last_known_status": "INCUMBENT"},
    ]

    res = service.batch_check_updates(items)
    assert res["total_tracked"] == 3
    assert res["valid_records_count"] == 2
    assert res["invalid_records_count"] == 1
    assert res["items_with_updates_count"] >= 2  # The updated promise + the deleted record


# =====================================================================
# 6. Privacy & Cross-User Isolation
# =====================================================================

def test_cross_user_isolation_and_privacy_controls(service):
    """
    Verify that saved records are strictly client-provided and stateless:
    User A's query cannot access or leak User B's saved list.
    """
    user_a_items = [{"record_type": "promise", "record_id": "PRM-DMK-2021-001"}]
    user_b_items = [{"record_type": "representative", "record_id": "REP-MLA-013"}]

    res_a = service.batch_check_updates(user_a_items)
    res_b = service.batch_check_updates(user_b_items)

    assert len(res_a["results"]) == 1
    assert res_a["results"][0]["record_id"] == "PRM-DMK-2021-001"

    assert len(res_b["results"]) == 1
    assert res_b["results"][0]["record_id"] == "REP-MLA-013"

    # Confirms no persistent user records leaked across invocations
    assert res_a["results"][0]["record_id"] not in [r["record_id"] for r in res_b["results"]]


# =====================================================================
# 7. REST API Endpoints
# =====================================================================

def test_api_get_tracking_types(test_client):
    """GET /api/tracking/types returns 200 with catalog and privacy model."""
    res = test_client.get("/api/tracking/types")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    data = json_data["data"]
    assert "supported_record_types" in data
    assert "privacy_model" in data
    assert data["privacy_model"]["requires_account"] is False


def test_api_post_validate_single(test_client):
    """POST /api/tracking/validate with single record returns 200."""
    res = test_client.post(
        "/api/tracking/validate",
        json={"record_type": "scheme", "record_id": "SCH-TN-KMUT"},
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["is_valid"] is True
    assert json_data["data"]["record_type"] == "scheme"


def test_api_post_validate_batch(test_client):
    """POST /api/tracking/validate with batch items returns 200."""
    res = test_client.post(
        "/api/tracking/validate",
        json={
            "items": [
                {"record_type": "promise", "record_id": "PRM-DMK-2021-001"},
                {"record_type": "claim", "record_id": "CLM-TN-2024-001"},
            ]
        },
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["count"] == 2


def test_api_post_check_updates(test_client):
    """POST /api/tracking/check-updates returns 200 and sync analysis."""
    res = test_client.post(
        "/api/tracking/check-updates",
        json={
            "items": [
                {
                    "record_type": "promise",
                    "record_id": "PRM-DMK-2021-001",
                    "last_known_status": "ANNOUNCED",
                    "saved_at": "2023-01-01T00:00:00Z",
                }
            ]
        },
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    data = json_data["data"]
    assert data["total_tracked"] == 1
    assert data["items_with_updates_count"] == 1


def test_api_get_tracked_item(test_client):
    """GET /api/tracking/item/<type>/<id> returns 200."""
    res = test_client.get("/api/tracking/item/claim/CLM-TN-2024-001")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["is_valid"] is True
    assert json_data["data"]["record_id"] == "CLM-TN-2024-001"


def test_api_validation_errors(test_client):
    """POST /api/tracking/validate with missing parameters returns 400."""
    res = test_client.post("/api/tracking/validate", json={})
    assert res.status_code == 400
    json_data = res.get_json()
    assert json_data["status"] == "error"
    assert "Both 'record_type' and 'record_id' are required" in json_data["message"]
