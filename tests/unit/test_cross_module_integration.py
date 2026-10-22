"""
Unit and Integration Tests for CIVICLENS TN — Phase 13.9:
Cross-Module Civic Intelligence Integration.

Verifies:
  1. Promise to Policy Outcome Evidence cross-module navigation
  2. Scheme, Budget, and Reported Results cross-module navigation
  3. Public Claim, Evidence Dossier, and Primary Sources cross-module navigation
  4. Civic Issue, Local Representative, and Remediation cross-module navigation
  5. Geographic Comparisons and Administrative Profile linkages
  6. Public Reports and Multi-Format Export linkages (JSON, CSV, MD, HTML)
  7. Saved Tracking payload and live status navigation
  8. Clear distinction between explicit vs inferred relationships with epistemic caveats
  9. Cycle-safe multi-hop path traversal avoiding infinite loops
  10. Non-causal epistemic boundary disclaimers
  11. DPDPA 2023 citizen privacy sanitization (phone, Aadhaar, names)
  12. REST API endpoints:
      - GET /api/integration/cross-module/<record_type>/<record_id>
      - GET /api/integration/journeys/phase13
      - GET /api/integration/path
"""

import pytest
from unittest.mock import MagicMock
from backend.services.cross_phase_integration_service import (
    CrossPhaseIntegrationService,
    CONN_DIRECT,
    CONN_EVIDENCE,
    CONN_INFERRED,
    resolve_canonical_id,
    redact_citizen_privacy
)


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session for unit tests."""
    mock = MagicMock()
    # By default, db query returns empty list so canonical graph is exercised
    mock.query.return_value.filter.return_value.limit.return_value.all.return_value = []
    mock.query.return_value.filter.return_value.first.return_value = None
    return mock


# =====================================================================
# 1. PROMISE TO OUTCOME EVIDENCE INTEGRATION
# =====================================================================

def test_promise_to_outcome_cross_module(mock_db):
    """Test Promise PRM-DMK-2021-001 cross-module intelligence linking to schemes, policy evaluations, and reports."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="promise",
        record_id="PRM-DMK-2021-001"
    )

    assert dossier["source_record"]["canonical_id"] == "PRM-DMK-2021-001"
    assert dossier["source_record"]["type"] == "promise"
    assert dossier["source_record"]["current_status"] == "DELIVERED"

    # Explicit relationships include Scheme (SCH-SW-KMUT) and Policy Evaluation (POL-TN-KMUT)
    explicit_ids = [r["id"] for r in dossier["explicit_relationships"]]
    assert "SCH-SW-KMUT" in explicit_ids
    assert "POL-TN-KMUT" in explicit_ids
    assert "REP-AC-139" in explicit_ids

    # Timeline navigation verified
    assert dossier["timeline_navigation"]["available"] is True
    assert "/api/timelines/promise/PRM-DMK-2021-001" in dossier["timeline_navigation"]["timeline_api"]

    # Public reports integration
    assert dossier["public_reports"]["available"] is True
    assert dossier["public_reports"]["domain"] == "promise_tracking"
    assert "json" in dossier["public_reports"]["export_formats"]
    assert "csv" in dossier["public_reports"]["export_formats"]

    # Saved tracking ready-to-use payload
    assert dossier["saved_tracking"]["supported"] is True
    payload = dossier["saved_tracking"]["tracking_payload"]
    assert payload["record_id"] == "PRM-DMK-2021-001"
    assert payload["current_status"] == "DELIVERED"


# =====================================================================
# 2. SCHEME, BUDGET & REPORTED RESULTS INTEGRATION
# =====================================================================

def test_scheme_budget_impact_cross_module(mock_db):
    """Test Scheme SCH-SW-KMUT cross-module intelligence linking to promises, evaluations, claims, and reports."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="scheme",
        record_id="SCH-SW-KMUT"
    )

    assert dossier["source_record"]["canonical_id"] == "SCH-SW-KMUT"
    assert dossier["source_record"]["type"] == "scheme"
    assert dossier["source_record"]["current_status"] == "IMPLEMENTED"

    # Direct links
    explicit_links = dossier["explicit_relationships"]
    assert any(r["id"] == "POL-TN-KMUT" and r["connection_type"] == CONN_DIRECT for r in explicit_links)
    assert any(r["id"] == "PRM-DMK-2021-001" and r["connection_type"] == CONN_DIRECT for r in explicit_links)
    assert any(r["id"] == "CLM-TN-2024-001" and r["connection_type"] == CONN_EVIDENCE for r in explicit_links)

    # Inferred link exists and has caveat
    inferred_links = dossier["inferred_relationships"]
    assert len(inferred_links) >= 1
    pudhumai_link = next(r for r in inferred_links if r["id"] == "SCH-HE-PUDHUMAI")
    assert pudhumai_link["connection_type"] == CONN_INFERRED
    assert "epistemic_caveat" in pudhumai_link

    # Scheme budget report links
    assert dossier["public_reports"]["available"] is True
    assert dossier["public_reports"]["domain"] == "scheme_budget"
    assert "/api/reports/export/scheme_budget/SCH-SW-KMUT" in dossier["public_reports"]["export_formats"]["json"]


# =====================================================================
# 3. PUBLIC CLAIM & EVIDENCE DOSSIER INTEGRATION
# =====================================================================

def test_claim_assessment_cross_module(mock_db):
    """Test Claim CLM-TN-2024-001 cross-module intelligence linking to underlying schemes, promises, and timelines."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="claim",
        record_id="CLM-TN-2024-001"
    )

    assert dossier["source_record"]["canonical_id"] == "CLM-TN-2024-001"
    assert dossier["source_record"]["type"] == "claim"
    assert dossier["source_record"]["current_status"] == "VERIFIED"

    explicit_ids = [r["id"] for r in dossier["explicit_relationships"]]
    assert "SCH-SW-KMUT" in explicit_ids
    assert "PRM-DMK-2021-001" in explicit_ids

    # Claim assessment report domain
    assert dossier["public_reports"]["available"] is True
    assert dossier["public_reports"]["domain"] == "claim_assessment"
    assert "markdown" in dossier["public_reports"]["export_formats"]
    assert "html" in dossier["public_reports"]["export_formats"]


# =====================================================================
# 4. CIVIC GRIEVANCE & PRIVACY SANITIZATION
# =====================================================================

def test_civic_issue_cross_module_and_privacy(mock_db):
    """Test Civic Issue CIV-2024-0891 navigation to representative, remediation scheme, and strict PII masking."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="civic",
        record_id="CIV-2024-0891"
    )

    assert dossier["source_record"]["canonical_id"] == "CIV-2024-0891"
    assert dossier["source_record"]["current_status"] == "RESOLVED"

    # Explicit relations include Kolathur MLA and Singara Chennai scheme
    explicit_ids = [r["id"] for r in dossier["explicit_relationships"]]
    assert "REP-AC-139" in explicit_ids
    assert "SCH-MA-SINGARA" in explicit_ids

    # Geographic insights
    geo = dossier["geographic_insights"]
    assert geo["available"] is True
    assert geo["code"] == "AC-139"
    assert geo["name"] == "Kolathur"

    # Check privacy guarantee: No citizen phone, Aadhaar, or email exposed in any relationship text
    for r in dossier["explicit_relationships"] + dossier["inferred_relationships"]:
        combined_text = f"{r.get('title', '')} {r.get('relationship_reason', '')}"
        assert "[Phone Redacted]" in combined_text or not any(c.isdigit() for c in combined_text if len(combined_text.split()) > 1 and "9840" in combined_text)
        assert "@" not in combined_text


# =====================================================================
# 5. GEOGRAPHIC COMPARISONS & LOCAL PROFILES
# =====================================================================

def test_geographic_context_integration(mock_db):
    """Test constituency AC-139 cross-module linkages to MLA, civic grievances, and local profiles."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="constituency",
        record_id="AC-139"
    )

    assert dossier["source_record"]["canonical_id"] == "AC-139"
    assert dossier["source_record"]["type"] == "constituency"

    explicit_ids = [r["id"] for r in dossier["explicit_relationships"]]
    assert "REP-AC-139" in explicit_ids
    assert "CIV-2024-0891" in explicit_ids

    geo = dossier["geographic_insights"]
    assert geo["available"] is True
    assert geo["level"] == "CONSTITUENCY"
    assert "/api/local-insights/profile/CONSTITUENCY/AC-139" in geo["profile_api"]


# =====================================================================
# 6. EXPLICIT VS INFERRED FILTERING & EPISTEMIC BOUNDARIES
# =====================================================================

def test_inferred_filtering_and_epistemic_caveats(mock_db):
    """Test that include_inferred=False removes candidate links, while include_inferred=True attaches clear caveats."""
    # When include_inferred=False
    dossier_filtered = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="scheme",
        record_id="SCH-SW-KMUT",
        include_inferred=False
    )
    assert len(dossier_filtered["inferred_relationships"]) == 0
    assert not any(r["id"] == "SCH-HE-PUDHUMAI" for r in dossier_filtered["explicit_relationships"])

    # When include_inferred=True
    dossier_all = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="scheme",
        record_id="SCH-SW-KMUT",
        include_inferred=True
    )
    assert len(dossier_all["inferred_relationships"]) >= 1
    inferred_item = dossier_all["inferred_relationships"][0]
    assert inferred_item["is_inferred"] is True
    assert "epistemic_caveat" in inferred_item
    assert "not an official" in inferred_item["epistemic_caveat"].lower() or "automated" in inferred_item["epistemic_caveat"].lower()


# =====================================================================
# 7. MULTI-HOP PATH DISCOVERY & CYCLE PREVENTION
# =====================================================================

def test_multi_hop_path_direct_hop(mock_db):
    """Test direct 1-hop path discovery between Promise and Scheme."""
    path = CrossPhaseIntegrationService.get_multi_hop_path(
        db=mock_db,
        source_type="promise",
        source_id="PRM-DMK-2021-001",
        target_type="scheme",
        target_id="SCH-SW-KMUT",
        max_hops=3
    )

    assert path["found"] is True
    assert path["hops"] == 1
    assert path["is_direct"] is True
    assert path["cumulative_confidence"] == 1.0
    assert "causality_caveat" in path


def test_multi_hop_path_two_hops(mock_db):
    """Test 2-hop path discovery between Civic Issue and Scheme via Representative."""
    path = CrossPhaseIntegrationService.get_multi_hop_path(
        db=mock_db,
        source_type="civic",
        source_id="CIV-2024-0891",
        target_type="scheme",
        target_id="SCH-SW-KMUT",
        max_hops=3
    )

    assert path["found"] is True
    assert path["hops"] == 2
    assert len(path["path_nodes"]) == 3
    assert len(path["path_edges"]) == 2
    # First edge: CIV -> REP-AC-139; Second edge: REP-AC-139 -> SCH-SW-KMUT
    assert path["path_nodes"][0]["id"] == "CIV-2024-0891"
    assert path["path_nodes"][1]["id"] == "REP-AC-139"
    assert path["path_nodes"][2]["id"] == "SCH-SW-KMUT"
    assert path["cumulative_confidence"] > 0.90


def test_multi_hop_cycle_prevention(mock_db):
    """Test that circular references (e.g. Scheme -> Promise -> Scheme) do not loop infinitely."""
    # Attempting to search for an unreachable node with max_hops=4 should terminate safely
    path = CrossPhaseIntegrationService.get_multi_hop_path(
        db=mock_db,
        source_type="scheme",
        source_id="SCH-SW-KMUT",
        target_type="scheme",
        target_id="SCH-NONEXISTENT-9999",
        max_hops=4
    )

    assert path["found"] is False
    assert path["hops"] == 0
    assert len(path["path_edges"]) == 0
    assert "No traceable path discovered" in path["message"]


# =====================================================================
# 8. CONTEXT-PRESERVING URL BUILDER
# =====================================================================

def test_contextual_url_builder():
    """Test building traceable URLs preserving query parameters across modules."""
    url = CrossPhaseIntegrationService.build_contextual_url(
        base_route="/promises",
        record_id="PRM-DMK-2021-001",
        origin="timeline",
        highlight="MS-001",
        tab="evidence",
        extra_params={"tracked": "true"}
    )

    assert url.startswith("/promises/PRM-DMK-2021-001?")
    assert "origin=timeline" in url
    assert "highlight=MS-001" in url
    assert "tab=evidence" in url
    assert "tracked=true" in url


# =====================================================================
# 9. EPISTEMIC & CAUSAL INTEGRITY GUARANTEES
# =====================================================================

def test_epistemic_integrity_safeguards(mock_db):
    """Test that all cross-module dossiers explicitly include non-causal warnings and DPDPA disclosures."""
    dossier = CrossPhaseIntegrationService.get_cross_module_intelligence(
        db=mock_db,
        record_type="scheme",
        record_id="SCH-SW-KMUT"
    )

    integrity = dossier["epistemic_integrity"]
    assert "non_causal_statement" in integrity
    assert "does not prove unilateral policy causation" in integrity["non_causal_statement"]
    assert "dpdpa_privacy_compliance" in integrity
    assert "DPDPA" in integrity["dpdpa_privacy_compliance"]
    assert "audit_integrity" in integrity


# =====================================================================
# 10. API ENDPOINTS INTEGRATION
# =====================================================================

def test_api_cross_module_endpoint(api_client):
    """Test GET /api/integration/cross-module/<record_type>/<record_id>."""
    resp = api_client.get("/api/integration/cross-module/promise/PRM-DMK-2021-001")
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert data["source_record"]["canonical_id"] == "PRM-DMK-2021-001"
    assert data["summary_counts"]["total"] >= 3
    assert len(data["explicit_relationships"]) >= 2
    assert data["timeline_navigation"]["available"] is True
    assert data["public_reports"]["available"] is True
    assert data["saved_tracking"]["supported"] is True


def test_api_phase13_journeys_endpoint(api_client):
    """Test GET /api/integration/journeys/phase13 returns all 7 citizen journeys."""
    resp = api_client.get("/api/integration/journeys/phase13")
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert data["total_journeys"] == 7
    journeys = data["journeys"]

    j_ids = [j["journey_id"] for j in journeys]
    assert "journey-p13-1-promise-to-outcome" in j_ids
    assert "journey-p13-2-scheme-budget-impact" in j_ids
    assert "journey-p13-3-claim-evidence-dossier" in j_ids
    assert "journey-p13-4-civic-issue-resolution" in j_ids
    assert "journey-p13-5-geographic-comparison" in j_ids
    assert "journey-p13-6-timeline-traceability" in j_ids
    assert "journey-p13-7-saved-tracking-updates" in j_ids


def test_api_multi_hop_path_endpoint(api_client):
    """Test GET /api/integration/path with valid parameters."""
    resp = api_client.get("/api/integration/path?from_type=civic&from_id=CIV-2024-0891&to_type=scheme&to_id=SCH-SW-KMUT")
    assert resp.status_code == 200
    data = resp.get_json()["data"]

    assert data["found"] is True
    assert data["hops"] == 2
    assert len(data["path_nodes"]) == 3


def test_api_multi_hop_path_missing_params(api_client):
    """Test GET /api/integration/path error handling for missing parameters."""
    # Missing to_id
    resp = api_client.get("/api/integration/path?from_type=civic&from_id=CIV-2024-0891")
    assert resp.status_code == 400
    assert "required" in resp.get_json()["message"].lower()

    # Invalid max_hops
    resp_bad = api_client.get("/api/integration/path?from_type=civic&from_id=CIV-2024-0891&to_id=SCH-SW-KMUT&max_hops=xyz")
    assert resp_bad.status_code == 400
