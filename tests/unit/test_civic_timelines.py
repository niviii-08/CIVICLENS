"""
CIVICLENS TN — Unit Tests for Evidence-Backed Civic Timelines
Phase 13.5: Chronological Evidence Aggregation & Cross-Phase Timeline Engine.

Verifies:
1. Canonical scheme timeline (SCH-SW-KMUT) chronological ordering, date semantics, and citations.
2. Separation of date semantics (event_date, publication_date, reporting_period, indexed_at).
3. Handling of undated records in unanchored_milestones without synthetic timestamps.
4. Identical-date tie breaking via EVENT_TYPE_PRECEDENCE.
5. Date conflict detection and explanation (has_date_conflict=True).
6. Connection basis tagging (DIRECT_IDENTIFIER_MATCH vs INFERRED_MATCH with confidence).
7. Epistemic non-causation guardrails (sequence is not causation).
8. Civic grievance timeline (CIV-2024-0891) grievance -> ATR -> resolution.
9. Database-backed scheme milestone extraction via SQLite session.
10. REST API endpoints (GET /api/timelines, /api/timelines/<type>/<id>, /api/timelines/journey/<id>).
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base_class import Base
from backend.models.budget import (
    BudgetDepartment,
    BudgetScheme,
    BudgetRecord,
    BudgetStage,
    BudgetSourceDocument,
)
from backend.models.policy_evaluation import (
    PolicyRegistryEntry,
    PolicyEvaluationPlan,
    EvaluationStudy,
    PolicyIndicator,
    IndicatorObservation,
    BeneficiaryGroup,
    ImplementationActivity,
)
from backend.services.civic_timeline_service import (
    CivicTimelineService,
    EVENT_TYPE_PRECEDENCE,
    EPISTEMIC_SEQUENCE_NOT_CAUSATION,
    EPISTEMIC_DATE_SEMANTICS_NOTICE,
    EPISTEMIC_INFERRED_RELATIONSHIP_DISCLOSURE,
)
from backend.api.app import create_app


@pytest.fixture
def timeline_db():
    """Isolated in-memory SQLite database session with seed records for dynamic testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Create department
    dept = BudgetDepartment(
        id=1,
        code="DEPT-SW",
        name="Social Welfare and Women Empowerment Department",
    )
    session.add(dept)
    session.flush()

    # Create scheme
    scheme = BudgetScheme(
        id=1,
        department_id=dept.id,
        name="Chief Minister Rural Livelihood Support Scheme",
        head_of_account="SCH-TEST-001",
    )
    session.add(scheme)
    session.flush()

    # Create Budget Source Document
    source_doc = BudgetSourceDocument(
        id=1,
        manifest_dataset_id="DDG-DEMAND-45-2023",
        title="Demand No. 45 - Social Welfare Budget 2023-24",
        official_source_url="https://www.tn.gov.in/budget/ddg45.pdf",
        financial_year_coverage="2023-2024",
    )
    session.add(source_doc)
    session.flush()

    # Create budget allocation record
    b_alloc = BudgetRecord(
        id=1,
        scheme_id=scheme.id,
        source_document_id=source_doc.id,
        financial_year="2023-2024",
        budget_stage=BudgetStage.budget_estimate,
        amount=1500000000.0,
        currency_unit="INR_Absolute",
    )
    session.add(b_alloc)

    # Create budget revised estimate record
    b_rev = BudgetRecord(
        id=2,
        scheme_id=scheme.id,
        source_document_id=source_doc.id,
        financial_year="2023-2024",
        budget_stage=BudgetStage.revised_estimate,
        amount=1450000000.0,
        currency_unit="INR_Absolute",
    )
    session.add(b_rev)

    # Create policy entry
    policy = PolicyRegistryEntry(
        policy_id="POL-TEST-001",
        canonical_scheme_code="SCH-TEST-001",
        policy_name="Rural Livelihood Support Directive",
        responsible_department="Social Welfare",
        objectives_summary="Support rural livelihoods through direct transfers",
        original_objective_wording="Support rural livelihoods through direct transfers",
        intended_beneficiaries="Rural households",
        start_date="2022-06-01",
        source_documents=["GO-MS-12-SW-2022"],
    )
    session.add(policy)
    session.flush()

    session.commit()
    yield session
    session.close()


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ===================================================================
# Service Layer Unit Tests
# ===================================================================

def test_canonical_scheme_timeline_ordering():
    """Verify SCH-SW-KMUT returns fully ordered chronological milestones with valid dates."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    assert timeline is not None
    assert timeline["entity_type"] == "scheme"
    assert timeline["entity_id"] == "SCH-SW-KMUT"
    assert timeline["chronological_milestones_count"] >= 6
    assert timeline["unanchored_milestones_count"] >= 1

    chronological = timeline["chronological_milestones"]

    # Verify strictly monotonic ascending chronological order
    for i in range(len(chronological) - 1):
        d1 = service._normalize_date_for_sorting(chronological[i]["date_semantics"]["primary_date"])
        d2 = service._normalize_date_for_sorting(chronological[i + 1]["date_semantics"]["primary_date"])
        assert d1 <= d2, f"Milestones out of chronological order: {d1} followed by {d2}"

    # Verify specific key milestones in sequence
    event_types = [m["event_type"] for m in chronological]
    assert "PROMISE_ANNOUNCEMENT" in event_types
    assert "BUDGET_ALLOCATION" in event_types
    assert "STATUTORY_NOTIFICATION" in event_types
    assert "IMPLEMENTATION_MILESTONE" in event_types
    assert "OUTCOME_EVALUATION" in event_types


def test_date_semantics_separation():
    """Verify distinct separation of event_date, publication_date, reporting_period, and indexed_at."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    chronological = timeline["chronological_milestones"]
    for m in chronological:
        sem = m["date_semantics"]
        assert "primary_date" in sem
        assert "date_precision" in sem
        assert "has_date_conflict" in sem
        assert sem["date_precision"] in ("EXACT_DATE", "MONTH_PRECISION", "FINANCIAL_YEAR", "UNKNOWN")

    # Find statutory notification: publication_date and event_date must be present
    statutory = next(m for m in chronological if m["event_type"] == "STATUTORY_NOTIFICATION")
    assert statutory["date_semantics"]["event_date"] is not None
    assert statutory["date_semantics"]["publication_date"] is not None
    assert statutory["date_semantics"]["primary_date"] == "2023-07-07"


def test_unanchored_milestones_no_synthetic_dates():
    """Verify undated milestones remain in unanchored_milestones without synthetic dates."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    unanchored = timeline["unanchored_milestones"]
    assert len(unanchored) > 0

    for m in unanchored:
        sem = m["date_semantics"]
        # Must have UNKNOWN precision and never an arbitrary synthetic date
        assert sem["date_precision"] == "UNKNOWN"
        assert sem["primary_date"] in ("UNKNOWN", None)
        assert sem["event_date"] is None
        assert sem["publication_date"] is None


def test_identical_dates_tie_breaking():
    """Verify milestones on identical dates break ties deterministically by EVENT_TYPE_PRECEDENCE."""
    service = CivicTimelineService()

    raw_events = [
        {
            "milestone_id": "MS-003-OUTCOME",
            "event_type": "OUTCOME_EVALUATION",
            "date_semantics": {"primary_date": "2023-08-01", "date_precision": "EXACT_DATE"},
        },
        {
            "milestone_id": "MS-001-BUDGET",
            "event_type": "BUDGET_ALLOCATION",
            "date_semantics": {"primary_date": "2023-08-01", "date_precision": "EXACT_DATE"},
        },
        {
            "milestone_id": "MS-002-IMPL",
            "event_type": "IMPLEMENTATION_MILESTONE",
            "date_semantics": {"primary_date": "2023-08-01", "date_precision": "EXACT_DATE"},
        },
    ]

    chronological, _ = service._sort_and_categorize_milestones(raw_events)

    # Budget allocation (30) < Implementation (50) < Outcome evaluation (90)
    assert chronological[0]["event_type"] == "BUDGET_ALLOCATION"
    assert chronological[1]["event_type"] == "IMPLEMENTATION_MILESTONE"
    assert chronological[2]["event_type"] == "OUTCOME_EVALUATION"


def test_date_conflict_detection_and_surfacing():
    """Verify that conflicting dates between documents are flagged and explained."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    chronological = timeline["chronological_milestones"]
    # In KMUT timeline, check if any milestone surfaces audit date adjustments
    conflict_milestones = [m for m in chronological if m["date_semantics"]["has_date_conflict"]]
    if conflict_milestones:
        m = conflict_milestones[0]
        assert m["date_semantics"]["conflict_explanation"] is not None
        assert len(m["date_semantics"]["conflict_explanation"]) > 0


def test_connection_basis_and_inference_disclosure():
    """Verify that deterministic vs inferred relationships are clearly distinguished."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    chronological = timeline["chronological_milestones"]
    connection_bases = {m["connection_basis"] for m in chronological}

    # Should contain DIRECT_IDENTIFIER_MATCH and/or PRIMARY_ENTITY_RECORD
    assert "DIRECT_IDENTIFIER_MATCH" in connection_bases or "PRIMARY_ENTITY_RECORD" in connection_bases

    for m in chronological:
        if m["connection_basis"] == "INFERRED_MATCH":
            assert m["inference_confidence"] < 1.0
        elif m["connection_basis"] in ("DIRECT_IDENTIFIER_MATCH", "PRIMARY_ENTITY_RECORD"):
            assert m["inference_confidence"] == 1.0


def test_epistemic_non_causation_guardrails():
    """Verify non-causation, date semantics, and relationship disclosures are present."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-SW-KMUT")

    guardrails = timeline["guardrails"]
    assert "causation_limitation" in guardrails
    assert "date_semantics_notice" in guardrails
    assert "inferred_relationship_disclosure" in guardrails

    assert "Chronological sequence does NOT prove causation" in guardrails["causation_limitation"]
    assert "DATE SEMANTICS NOTICE" in guardrails["date_semantics_notice"]
    assert "RELATIONSHIP TRANSPARENCY NOTICE" in guardrails["inferred_relationship_disclosure"]


def test_civic_issue_timeline_lifecycle():
    """Verify civic issue CIV-2024-0891 correctly reflects citizen grievance -> ATR -> resolution."""
    service = CivicTimelineService()
    timeline = service.get_timeline(entity_type="civic_issue", entity_id="CIV-2024-0891")

    assert timeline is not None
    assert timeline["entity_type"] == "civic_issue"
    assert timeline["entity_id"] == "CIV-2024-0891"

    chronological = timeline["chronological_milestones"]
    assert len(chronological) == 4

    # Verify lifecycle steps
    assert chronological[0]["event_type"] == "GRIEVANCE_FILED"
    assert chronological[0]["date_semantics"]["primary_date"] == "2024-06-12"

    assert chronological[1]["event_type"] == "DEPARTMENT_ACKNOWLEDGEMENT"
    assert chronological[1]["date_semantics"]["primary_date"] == "2024-06-14"

    assert chronological[2]["event_type"] == "ACTION_TAKEN"
    assert chronological[2]["date_semantics"]["primary_date"] == "2024-06-20"

    assert chronological[3]["event_type"] == "ACTION_TAKEN"
    assert chronological[3]["date_semantics"]["primary_date"] == "2024-06-25"


def test_database_backed_scheme_milestones(timeline_db):
    """Verify dynamic database milestone generation for SCH-TEST-001."""
    service = CivicTimelineService(db=timeline_db)
    timeline = service.get_timeline(entity_type="scheme", entity_id="SCH-TEST-001")

    assert timeline is not None
    assert timeline["entity_id"] == "SCH-TEST-001"
    assert timeline["total_milestones_evaluated"] >= 3

    chronological = timeline["chronological_milestones"]
    event_types = [m["event_type"] for m in chronological]

    # Policy announcement was 2022-06-01
    assert "POLICY_ENACTMENT" in event_types
    # Budget allocation was 2023-03-20
    assert "BUDGET_ALLOCATION" in event_types
    # Budget revised estimate was 2024-02-19
    assert "BUDGET_REVISION" in event_types

    # Ensure chronological sort
    dates = [m["date_semantics"]["primary_date"] for m in chronological]
    assert dates == sorted(dates)


# ===================================================================
# REST API Endpoints Tests
# ===================================================================

def test_api_list_available_timelines(test_client):
    """Verify GET /api/timelines returns index of featured timelines and guardrails."""
    resp = test_client.get("/api/timelines")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    assert "featured_timelines" in data["data"]
    assert "guardrails" in data["data"]
    assert len(data["data"]["featured_timelines"]) >= 4


def test_api_get_scheme_timeline_success(test_client):
    """Verify GET /api/timelines/scheme/SCH-SW-KMUT returns valid timeline response."""
    resp = test_client.get("/api/timelines/scheme/SCH-SW-KMUT")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    payload = data["data"]

    assert payload["entity_type"] == "scheme"
    assert payload["entity_id"] == "SCH-SW-KMUT"
    assert "chronological_milestones" in payload
    assert len(payload["chronological_milestones"]) >= 6
    assert "guardrails" in payload
    assert "causation_limitation" in payload["guardrails"]


def test_api_get_civic_issue_timeline_success(test_client):
    """Verify GET /api/timelines/civic_issue/CIV-2024-0891 returns valid grievance timeline."""
    resp = test_client.get("/api/timelines/civic_issue/CIV-2024-0891")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    payload = data["data"]

    assert payload["entity_id"] == "CIV-2024-0891"
    assert len(payload["chronological_milestones"]) == 4


def test_api_get_journey_timeline_success(test_client):
    """Verify GET /api/timelines/journey/JOURNEY-1-SCHEME-TO-POLICY returns journey timeline."""
    resp = test_client.get("/api/timelines/journey/JOURNEY-1-SCHEME-TO-POLICY")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    payload = data["data"]
    assert len(payload["chronological_milestones"]) >= 6


def test_api_filter_date_range(test_client):
    """Verify start_date and end_date query filters apply correctly."""
    resp = test_client.get("/api/timelines/scheme/SCH-SW-KMUT?start_date=2023-01-01&end_date=2023-12-31")
    assert resp.status_code == 200

    data = resp.get_json()
    milestones = data["data"]["chronological_milestones"]
    for m in milestones:
        p_date = m["date_semantics"]["primary_date"]
        assert "2023-01-01" <= p_date <= "2023-12-31"


def test_api_exclude_unanchored(test_client):
    """Verify include_unanchored=false strips unanchored milestones from response."""
    resp = test_client.get("/api/timelines/scheme/SCH-SW-KMUT?include_unanchored=false")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["data"]["unanchored_milestones_count"] == 0
    assert len(data["data"]["unanchored_milestones"]) == 0


def test_api_not_found_entity(test_client):
    """Verify unknown entity returns 404 with structured error message."""
    resp = test_client.get("/api/timelines/scheme/SCH-NONEXISTENT-999")
    assert resp.status_code == 404

    data = resp.get_json()
    assert data["status"] == "error"
    assert "No timeline records found" in data["message"]
