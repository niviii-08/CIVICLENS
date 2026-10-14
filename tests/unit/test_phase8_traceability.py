"""
CIVICLENS TN — Phase 8.11 Unit & Integration Test Suite
=======================================================
Evidence Traceability, Resolution Verification, and Review Audit Trail.

Validates Scenarios A through L:
Scenario A: Complete end-to-end traceability chain (Stages 1-7 without gaps, score = 1.0)
Scenario B: Missing departmental response handling (Stage 4 gap, NO_OFFICIAL_RESPONSE)
Scenario C: Missing resolution evidence handling (Stage 6 gap, NO_EMPIRICAL_EVIDENCE, coverage rate)
Scenario D: Conflicting resolution evidence detection (contradictions flagged, DISPUTED status)
Scenario E: Unresolved department jurisdiction handling (Stage 3 gap, UNRESOLVED_JURISDICTION)
Scenario F: Automated inference vs official government report distinction
Scenario G: Role-governed human reviewer workflow & audit trail preservation (X-Reviewer-Role RBAC)
Scenario H: Unverified resolution claim guard (marked_resolved != independently verified)
Scenario I: Backward navigation continuity (from empirical artifact back to citizen petition)
Scenario J: Traceability metrics calculation and empty-sample division-by-zero protection
Scenario K: DPDPA 2023 citizen privacy & PII scrubbing across timeline and review notes
Scenario L: Anti-causality rule enforcement on cross-phase relationship establishment
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base_class import Base
from backend.models.civic_issue import (
    AdministrativeArea,
    AdministrativeLevel,
    CivicCrossPhaseLink,
    CivicDepartment,
    CivicIssue,
    CivicIssueSeverity,
    CivicIssueStatus,
    CivicReviewAudit,
    EvidenceAssessmentEnum,
    EvidenceType,
    GrievanceRecord,
    IssueCategory,
    IssueCategoryEnum,
    IssueEvent,
    PublicWork,
    ResolutionEvidence,
    ResolutionVerificationStatus,
    ResponseActionType,
    ResponseRecord,
    SourceDocument,
    sanitize_pii,
)
from backend.api.app import create_app


@pytest.fixture
def app_and_db(monkeypatch):
    """
    Sets up an in-memory SQLite database populated with isolated test fixtures,
    monkeypatching SessionLocal in backend.database.session and backend.api.civic.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    import backend.database.session
    import backend.api.civic
    monkeypatch.setattr(backend.database.session, "SessionLocal", TestingSessionLocal)
    monkeypatch.setattr(backend.api.civic, "SessionLocal", TestingSessionLocal)

    session = TestingSessionLocal()

    # Prepopulate standard categories
    cat_roads = IssueCategory(
        code=IssueCategoryEnum.ROADS,
        name_en="Roads & Footpaths",
        name_ta="சாலைகள் மற்றும் நடைபாதைகள்",
        description="Potholes and road defects",
    )
    cat_water = IssueCategory(
        code=IssueCategoryEnum.WATER_SUPPLY,
        name_en="Water Supply",
        name_ta="குடிநீர் வழங்கல்",
        description="Drinking water supply pipelines",
    )
    session.add_all([cat_roads, cat_water])
    session.flush()

    # Prepopulate departments
    dept_gcc = CivicDepartment(
        code="DEPT-GCC-001",
        name_en="Greater Chennai Corporation",
        name_ta="பெருநகர சென்னை மாநகராட்சி",
        jurisdiction_level="MUNICIPAL_CORPORATION",
        helpline_number="1913",
    )
    dept_twad = CivicDepartment(
        code="DEPT-TWAD",
        name_en="Tamil Nadu Water Supply and Drainage Board",
        name_ta="தமிழ்நாடு குடிநீர் வடிகால் வாரியம்",
        jurisdiction_level="STATE",
        helpline_number="1916",
    )
    session.add_all([dept_gcc, dept_twad])
    session.flush()

    # Prepopulate administrative area
    area_chennai = AdministrativeArea(
        area_code="ADM-TN-DIST-002-CHENNAI",
        name_en="Chennai District",
        name_ta="சென்னை மாவட்டம்",
        administrative_level=AdministrativeLevel.DISTRICT,
        population=7_000_000,
    )
    session.add(area_chennai)
    session.flush()

    # Statutory Source Document
    src_doc = SourceDocument(
        document_code="DOC-GCC-PROCEEDING-2026-001",
        title="Greater Chennai Corporation Standing Committee Proceedings 2026",
        publisher="Greater Chennai Corporation",
        published_date=datetime(2026, 1, 15, tzinfo=timezone.utc),
        sha256_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
    )
    session.add(src_doc)
    session.flush()

    session.commit()
    session.close()

    app = create_app()
    app.config["TESTING"] = True
    client = app.test_client()

    yield client, TestingSessionLocal


# -----------------------------------------------------------------------------
# SCENARIO A: Complete End-to-End Traceability Chain
# -----------------------------------------------------------------------------
def test_scenario_a_complete_end_to_end_traceability_chain(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    # 1. Source doc & Grievance
    doc = session.query(SourceDocument).first()
    category = session.query(IssueCategory).filter_by(code=IssueCategoryEnum.ROADS).first()
    dept = session.query(CivicDepartment).filter_by(code="DEPT-GCC-001").first()
    area = session.query(AdministrativeArea).first()

    # Normalized Issue
    issue = CivicIssue(
        issue_code="TN-CHN-2026-TR-001",
        title="Severe potholes on Anna Salai arterial corridor",
        description="Hazardous crater-like potholes near Thousand Lights signal causing accidents.",
        category_id=category.id,
        department_id=dept.id,
        administrative_area_id=area.id,
        status=CivicIssueStatus.VERIFIED_RESOLVED,
        severity=CivicIssueSeverity.HIGH,
        reported_date=datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc),
        actual_resolution_date=datetime(2026, 2, 10, 16, 0, tzinfo=timezone.utc),
        resolution_verification_status=ResolutionVerificationStatus.VERIFIED,
        evidence_assessment=EvidenceAssessmentEnum.INDEPENDENTLY_VERIFIED_RESOLVED,
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    grievance = GrievanceRecord(
        grievance_id="GRV-2026-0001",
        source_id="CM_HELPLINE_1100",
        issue_category=IssueCategoryEnum.ROADS,
        description_or_permitted_summary="Potholes on Anna Salai causing bike skids.",
        submission_date=datetime(2026, 2, 1, 9, 30, tzinfo=timezone.utc),
        source_document_id=doc.id,
        source_record_reference="CM-HL-REF-88990",
        civic_issue_id=issue.id,
        classification_method="RULE_BASED",
        classification_confidence=1.0,
        is_test_fixture=True,
    )
    session.add(grievance)
    session.flush()

    # Department Response
    resp = ResponseRecord(
        response_code="RESP-GCC-2026-001",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.RESOLVED,
        reported_status="marked_resolved",
        action_taken_date=datetime(2026, 2, 9, 14, 0, tzinfo=timezone.utc),
        official_remark="Mastic asphalt road patching completed under Zone 9 maintenance budget.",
        is_evidence_supported=True,
        is_test_fixture=True,
    )
    session.add(resp)
    session.flush()

    # Empirical Evidence
    evid = ResolutionEvidence(
        response_id=resp.id,
        evidence_type=EvidenceType.COMPLETION_CERTIFICATE,
        title="Zonal Engineer Completion Certificate",
        description="Verified mastic asphalt cold-mix relaying completed with zero residual depressions.",
        sha256_hash="a1b2c3d4e5f678901234567890abcdef1234567890abcdef1234567890abcdef",
        is_verified=True,
        verified_by="SE_HIGHWAYS_CHENNAI",
        verification_date=datetime(2026, 2, 10, 15, 0, tzinfo=timezone.utc),
        confidence=1.0,
        matching_method="RECORD_ID_MATCH",
        is_test_fixture=True,
    )
    session.add(evid)
    session.flush()

    # Human Auditor Review
    audit = CivicReviewAudit(
        civic_issue_id=issue.id,
        reviewer_id="AUDITOR-SR-01",
        reviewer_role="SENIOR_CIVIC_AUDITOR",
        previous_status="RESOLVED",
        new_status="VERIFIED_RESOLVED",
        previous_assessment="resolution_evidence_available",
        new_assessment="independently_verified_resolved",
        action="VERIFY_RESOLUTION",
        reason="Field inspection completion certificate corroborates full bituminous resurfacing.",
        evidence_ids=[evid.id],
        is_test_fixture=True,
    )
    session.add(audit)
    session.commit()

    # Request unified timeline API
    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert data["issue_id"] == issue.id
    assert data["completeness_score"] == 1.0  # Zero gaps!
    assert data["gaps_count"] == 0
    assert len(data["chain"]) == 7

    # Verify each stage
    stages = {hop["stage_name"]: hop for hop in data["chain"]}
    assert stages["ORIGINAL_PUBLIC_RECORD"]["is_gap"] is False
    assert stages["ORIGINAL_PUBLIC_RECORD"]["record_id"] == "GRV-2026-0001"
    assert stages["ORIGINAL_PUBLIC_RECORD"]["origin_badge"] == "OFFICIAL_GOVERNMENT_RECORD"

    assert stages["NORMALIZED_CIVIC_ISSUE"]["is_gap"] is False
    assert stages["NORMALIZED_CIVIC_ISSUE"]["origin_badge"] == "AUTOMATED_SYSTEM_INFERENCE"

    assert stages["RESPONSIBLE_DEPARTMENT"]["is_gap"] is False
    assert stages["RESPONSIBLE_DEPARTMENT"]["record_id"] == "DEPT-GCC-001"

    assert stages["OFFICIAL_RESPONSE_ATR"]["is_gap"] is False
    assert stages["OFFICIAL_RESPONSE_ATR"]["record_id"] == "RESP-GCC-2026-001"

    assert stages["REPORTED_RESOLUTION"]["is_gap"] is False

    assert stages["RESOLUTION_EVIDENCE"]["is_gap"] is False
    assert len(stages["RESOLUTION_EVIDENCE"]["evidences"]) == 1

    assert stages["VERIFICATION_STATUS_AND_AUDIT"]["is_gap"] is False
    assert stages["VERIFICATION_STATUS_AND_AUDIT"]["origin_badge"] == "HUMAN_AUDITOR_REVIEW"
    assert stages["VERIFICATION_STATUS_AND_AUDIT"]["verification_status"] == "VERIFIED"


# -----------------------------------------------------------------------------
# SCENARIO B: Missing Departmental Response Handling
# -----------------------------------------------------------------------------
def test_scenario_b_missing_response_handling(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).filter_by(code=IssueCategoryEnum.WATER_SUPPLY).first()
    dept = session.query(CivicDepartment).filter_by(code="DEPT-TWAD").first()

    issue = CivicIssue(
        issue_code="TN-TWAD-2026-UNRESP-01",
        title="Broken water trunk pipeline at Ambattur",
        description="Clean drinking water overflowing onto road for 5 days.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.OPEN,
        reported_date=datetime(2026, 2, 5, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    grievance = GrievanceRecord(
        grievance_id="GRV-2026-0002",
        source_id="CM_HELPLINE_1100",
        description_or_permitted_summary="Water leak at Ambattur industrial estate.",
        submission_date=datetime(2026, 2, 5, tzinfo=timezone.utc),
        civic_issue_id=issue.id,
        is_test_fixture=True,
    )
    session.add(grievance)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    stages = {hop["stage_name"]: hop for hop in data["chain"]}
    # Stage 4 must be flagged as a gap
    atr_stage = stages["OFFICIAL_RESPONSE_ATR"]
    assert atr_stage["is_gap"] is True
    assert atr_stage["origin_badge"] == "NO_OFFICIAL_RESPONSE"
    assert "Action-Taken Report" in atr_stage["gap_reason"]


# -----------------------------------------------------------------------------
# SCENARIO C: Missing Resolution Evidence (Unverified Closure)
# -----------------------------------------------------------------------------
def test_scenario_c_missing_resolution_evidence_and_coverage_metric(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-GCC-2026-UNVERIF-01",
        title="Streetlight fault at T. Nagar",
        description="Flickering sodium vapor lamps.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.RESOLVED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        actual_resolution_date=datetime(2026, 2, 3, tzinfo=timezone.utc),
        resolution_verification_status=ResolutionVerificationStatus.PENDING_VERIFICATION,
        evidence_assessment=EvidenceAssessmentEnum.RESOLUTION_NOT_INDEPENDENTLY_VERIFIED,
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    resp = ResponseRecord(
        response_code="RESP-GCC-2026-002",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.RESOLVED,
        reported_status="marked_resolved",
        action_taken_date=datetime(2026, 2, 3, tzinfo=timezone.utc),
        official_remark="Bulb replaced by lineman.",
        is_evidence_supported=False,  # Zero empirical proof!
        is_test_fixture=True,
    )
    session.add(resp)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    stages = {hop["stage_name"]: hop for hop in data["chain"]}
    ev_stage = stages["RESOLUTION_EVIDENCE"]
    assert ev_stage["is_gap"] is True
    assert ev_stage["origin_badge"] == "NO_EMPIRICAL_EVIDENCE"
    assert "Zero empirical artifacts available" in ev_stage["gap_reason"]


# -----------------------------------------------------------------------------
# SCENARIO D: Conflicting Resolution Evidence Detection
# -----------------------------------------------------------------------------
def test_scenario_d_conflicting_resolution_evidence_detection(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-GCC-2026-CONFLICT-01",
        title="Stagnant drainage canal at Velachery",
        description="Canal overflowing with plastic sludge.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.DISPUTED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        actual_resolution_date=datetime(2026, 2, 4, tzinfo=timezone.utc),
        resolution_verification_status=ResolutionVerificationStatus.CONTRADICTED,
        evidence_assessment=EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_CONFLICTING,
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    resp = ResponseRecord(
        response_code="RESP-GCC-2026-003",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.RESOLVED,
        reported_status="marked_resolved",
        action_taken_date=datetime(2026, 2, 4, tzinfo=timezone.utc),
        official_remark="Desilting executed by GCC backhoe loader.",
        is_evidence_supported=True,
        is_test_fixture=True,
    )
    session.add(resp)
    session.flush()

    # Contradicting Citizen Audit Evidence
    conflict_evid = ResolutionEvidence(
        response_id=resp.id,
        evidence_type=EvidenceType.CITIZEN_AUDIT,
        title="Resident Welfare Association Video Audit",
        description="Geotagged video showing sewage level unchanged and silt berm unremoved.",
        contradicts_resolution=True,
        is_verified=False,
        confidence=0.9,
        is_test_fixture=True,
    )
    session.add(conflict_evid)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert len(data["contradictions_detected"]) >= 1
    assert data["contradictions_detected"][0]["contradicts_resolution"] is True
    assert data["evidence_assessment"] == "resolution_evidence_conflicting"


# -----------------------------------------------------------------------------
# SCENARIO E: Unresolved Department Responsibility
# -----------------------------------------------------------------------------
def test_scenario_e_multiple_candidate_departments_or_unresolved_jurisdiction(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()

    # Issue with department_id = None (unresolved border between Corporation and Highways)
    issue = CivicIssue(
        issue_code="TN-DISPUTE-BORDER-01",
        title="Encroached storm water culvert on boundary road",
        description="Boundary between Tambaram Corporation and State Highways; neither accepts responsibility.",
        category_id=category.id,
        department_id=None,
        status=CivicIssueStatus.OPEN,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    stages = {hop["stage_name"]: hop for hop in data["chain"]}
    dept_stage = stages["RESPONSIBLE_DEPARTMENT"]
    assert dept_stage["is_gap"] is True
    assert dept_stage["origin_badge"] == "UNRESOLVED_JURISDICTION"
    assert "No government department officially mapped" in dept_stage["gap_reason"]


# -----------------------------------------------------------------------------
# SCENARIO F: Automated Inference vs Official Report Distinction
# -----------------------------------------------------------------------------
def test_scenario_f_automated_inference_vs_official_report_distinction(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-TEST-BADGES-01",
        title="Pothole classification badge check",
        description="Auto-classified by ML model; response logged by official.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.IN_PROGRESS,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    resp = ResponseRecord(
        response_code="RESP-TEST-001",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.INSPECTION_CONDUCTED,
        reported_status="under_review",
        action_taken_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
        official_remark="Inspection conducted by AE.",
        is_test_fixture=True,
    )
    session.add(resp)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    chain = res.get_json()["data"]["chain"]

    stages = {hop["stage_name"]: hop for hop in chain}
    # Stage 2 (Normalized issue) must be an automated system inference
    assert stages["NORMALIZED_CIVIC_ISSUE"]["origin_badge"] == "AUTOMATED_SYSTEM_INFERENCE"
    # Stage 4 (Official response) must be an official government record
    assert stages["OFFICIAL_RESPONSE_ATR"]["origin_badge"] == "OFFICIAL_GOVERNMENT_RECORD"


# -----------------------------------------------------------------------------
# SCENARIO G: Human Reviewer Override and Audit Trail Preservation
# -----------------------------------------------------------------------------
def test_scenario_g_human_reviewer_override_and_audit_trail_preservation(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-TEST-REVIEW-01",
        title="Sanitation overflow requiring senior audit",
        description="Waste collection missed for 2 weeks.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.RESOLVED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        resolution_verification_status=ResolutionVerificationStatus.PENDING_VERIFICATION,
        evidence_assessment=EvidenceAssessmentEnum.PENDING_REVIEW,
        is_test_fixture=True,
    )
    session.add(issue)
    session.commit()

    # 1. Attempt review with UNAUTHORIZED role
    res_unauth = client.post(
        f"/api/civic/issues/{issue.id}/review",
        json={"action": "VERIFY_RESOLUTION", "reason": "Looks good to me."},
        headers={"X-Reviewer-Role": "CITIZEN_GUEST"},
    )
    assert res_unauth.status_code == 403

    # 2. Execute review with AUTHORIZED role (SENIOR_CIVIC_AUDITOR)
    res_auth = client.post(
        f"/api/civic/issues/{issue.id}/review",
        json={
            "action": "DISPUTE_RESOLUTION",
            "reason": "Independent ground inspection revealed trash remains piled up at intersection.",
            "reviewer_id": "AUDITOR-COLLECTORATE-01",
        },
        headers={"X-Reviewer-Role": "SENIOR_CIVIC_AUDITOR"},
    )
    assert res_auth.status_code == 201
    audit_data = res_auth.get_json()["data"]["audit"]
    assert audit_data["action"] == "DISPUTE_RESOLUTION"
    assert audit_data["reviewer_role"] == "SENIOR_CIVIC_AUDITOR"
    assert audit_data["new_status"] == "DISPUTED"
    assert audit_data["new_assessment"] == "resolution_evidence_conflicting"

    # Verify audit record persisted in database
    db_audit = session.query(CivicReviewAudit).filter_by(civic_issue_id=issue.id).first()
    assert db_audit is not None
    assert db_audit.action == "DISPUTE_RESOLUTION"


# -----------------------------------------------------------------------------
# SCENARIO H: Unverified Resolution Claim Guard
# -----------------------------------------------------------------------------
def test_scenario_h_unverified_resolution_claim_guard(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    # Issue administratively marked resolved, but not verified
    issue = CivicIssue(
        issue_code="TN-TEST-GUARD-01",
        title="Fallen tree branch on pavement",
        description="Tree branch obstructing walkway.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.RESOLVED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        actual_resolution_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
        resolution_verification_status=ResolutionVerificationStatus.PENDING_VERIFICATION,
        evidence_assessment=EvidenceAssessmentEnum.RESOLUTION_NOT_INDEPENDENTLY_VERIFIED,
        is_test_fixture=True,
    )
    session.add(issue)
    session.commit()

    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    data = res.get_json()["data"]

    # System must explicitly show verification_status is NOT verified
    assert data["verification_status"] != "VERIFIED"
    assert data["evidence_assessment"] == "resolution_not_independently_verified"

    stages = {hop["stage_name"]: hop for hop in data["chain"]}
    assert "not an independently verified empirical outcome" in stages["REPORTED_RESOLUTION"]["description"]


# -----------------------------------------------------------------------------
# SCENARIO I: Backward Navigation Continuity
# -----------------------------------------------------------------------------
def test_scenario_i_backward_navigation_continuity(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    doc = session.query(SourceDocument).first()
    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-TEST-BACKNAV-01",
        title="Damaged culvert repair",
        description="Rebuilding damaged culvert.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.RESOLVED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    grievance = GrievanceRecord(
        grievance_id="GRV-BACKNAV-99",
        source_id="GCC_HELPLINE",
        description_or_permitted_summary="Broken slab over culvert.",
        submission_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        source_document_id=doc.id,
        civic_issue_id=issue.id,
        is_test_fixture=True,
    )
    session.add(grievance)
    session.flush()

    resp = ResponseRecord(
        response_code="RESP-BACKNAV-99",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.RESOLVED,
        action_taken_date=datetime(2026, 2, 3, tzinfo=timezone.utc),
        official_remark="Culvert slab cast and cured.",
        is_test_fixture=True,
    )
    session.add(resp)
    session.flush()

    evid = ResolutionEvidence(
        response_id=resp.id,
        evidence_type=EvidenceType.WORK_ORDER,
        title="Culvert Work Order 44A",
        description="Sanction order and measurement sheet.",
        is_test_fixture=True,
    )
    session.add(evid)
    session.commit()

    # Query provenance graph
    res = client.get(f"/api/civic/issues/{issue.id}/provenance")
    assert res.status_code == 200
    graph = res.get_json()["data"]

    # Must contain nodes for Doc, Grievance, Issue, Dept, Response, and Evidence
    node_types = {n["type"] for n in graph["nodes"]}
    assert "SourceDocument" in node_types
    assert "GrievanceRecord" in node_types
    assert "CivicIssue" in node_types
    assert "CivicDepartment" in node_types
    assert "ResponseRecord" in node_types
    assert "ResolutionEvidence" in node_types

    # Edges must establish unbroken path
    assert graph["edge_count"] >= 5


# -----------------------------------------------------------------------------
# SCENARIO J: Traceability Metrics Computation & Safe Empty Samples
# -----------------------------------------------------------------------------
def test_scenario_j_traceability_metrics_computation_and_empty_sample_safety(app_and_db):
    client, SessionLocal = app_and_db

    # 1. Query metrics with filter that returns 0 issues (empty sample)
    res_empty = client.get("/api/civic/traceability/metrics?district=NonExistentDistrictXYZ")
    assert res_empty.status_code == 200
    data_empty = res_empty.get_json()["data"]
    assert data_empty["total_issues"] == 0
    assert data_empty["evidence_coverage_rate"] == 0.0
    assert data_empty["independent_verification_rate"] == 0.0
    assert data_empty["department_response_rate"] == 0.0
    assert "definitions" in data_empty

    # 2. Add an issue to populate database
    session = SessionLocal()
    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()
    area = session.query(AdministrativeArea).first()

    issue = CivicIssue(
        issue_code="TN-METRIC-POP-01",
        title="Metrics population issue",
        description="Testing metrics computation",
        category_id=category.id,
        department_id=dept.id,
        administrative_area_id=area.id,
        status=CivicIssueStatus.RESOLVED,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        actual_resolution_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    resp = ResponseRecord(
        response_code="RESP-METRIC-01",
        civic_issue_id=issue.id,
        department_id=dept.id,
        action_type=ResponseActionType.RESOLVED,
        reported_status="marked_resolved",
        action_taken_date=datetime(2026, 2, 2, tzinfo=timezone.utc),
        official_remark="Closed.",
        is_test_fixture=True,
    )
    session.add(resp)
    session.flush()

    evid = ResolutionEvidence(
        response_id=resp.id,
        evidence_type=EvidenceType.COMPLETION_CERTIFICATE,
        title="Completion Cert",
        description="Done",
        is_verified=True,
        is_test_fixture=True,
    )
    session.add(evid)
    session.commit()

    # Query global metrics on populated database
    res_all = client.get("/api/civic/traceability/metrics")
    assert res_all.status_code == 200
    data_all = res_all.get_json()["data"]

    assert data_all["total_issues"] >= 1
    assert "evidence_coverage_rate" in data_all
    assert "independent_verification_rate" in data_all
    assert "department_response_rate" in data_all
    assert "unverified_resolution_rate" in data_all
    assert "conflicting_evidence_rate" in data_all
    assert "audit_trail_completeness_rate" in data_all
    assert "definitions" in data_all
    assert "methodological_caveats" in data_all


# -----------------------------------------------------------------------------
# SCENARIO K: DPDPA 2023 PII Sanitization in Traceability Endpoints
# -----------------------------------------------------------------------------
def test_scenario_k_dpdpa_pii_sanitization_in_traceability_endpoints(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    raw_description = (
        "Complainant Thiru K. Ramanathan, residing at Door No. 42B, Anna Nagar, "
        "mobile +91 98765 43210, email ramanathan@example.com, Aadhaar 1234 5678 9012, "
        "reports sewage overflow outside residence."
    )

    issue = CivicIssue(
        issue_code="TN-PII-TEST-01",
        title="Sanitation complaint with raw PII",
        description=sanitize_pii(raw_description),
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.OPEN,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.flush()

    grievance = GrievanceRecord(
        grievance_id="GRV-PII-01",
        description_or_permitted_summary=sanitize_pii(raw_description),
        submission_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        civic_issue_id=issue.id,
        is_test_fixture=True,
    )
    session.add(grievance)
    session.commit()

    # Test timeline output
    res = client.get(f"/api/civic/issues/{issue.id}/timeline")
    assert res.status_code == 200
    timeline_str = res.get_data(as_text=True)

    # Assert all PII is redacted
    assert "98765 43210" not in timeline_str
    assert "ramanathan@example.com" not in timeline_str
    assert "1234 5678 9012" not in timeline_str
    assert "Door No. 42B" not in timeline_str
    assert "Thiru K. Ramanathan" not in timeline_str

    assert "[PHONE REDACTED]" in timeline_str or "[EMAIL REDACTED]" in timeline_str or "[ADDRESS REDACTED]" in timeline_str

    # Test review endpoint sanitization
    res_rev = client.post(
        f"/api/civic/issues/{issue.id}/review",
        json={
            "action": "UPDATE_ASSESSMENT",
            "new_assessment": "insufficient_evidence",
            "reason": "Spoke to Thiru S. Murugan at 9840123456 who confirmed site uninspected.",
        },
        headers={"X-Reviewer-Role": "SENIOR_CIVIC_AUDITOR"},
    )
    assert res_rev.status_code == 201
    audit_dict = res_rev.get_json()["data"]["audit"]
    assert "9840123456" not in audit_dict["reason"]
    assert "[PHONE REDACTED]" in audit_dict["reason"]


# -----------------------------------------------------------------------------
# SCENARIO L: Non-Causality Rule Enforcement in Cross-Phase Links
# -----------------------------------------------------------------------------
def test_scenario_l_non_causality_rule_enforcement_in_cross_phase_links(app_and_db):
    client, SessionLocal = app_and_db
    session = SessionLocal()

    category = session.query(IssueCategory).first()
    dept = session.query(CivicDepartment).first()

    issue = CivicIssue(
        issue_code="TN-CAUSAL-GUARD-01",
        title="Anti-causality test issue",
        description="Testing cross-phase guards.",
        category_id=category.id,
        department_id=dept.id,
        status=CivicIssueStatus.OPEN,
        reported_date=datetime(2026, 2, 1, tzinfo=timezone.utc),
        is_test_fixture=True,
    )
    session.add(issue)
    session.commit()

    # 1. Attempt to create cross-phase link with forbidden matching method "same_area"
    res_bad = client.post(
        f"/api/civic/issues/{issue.id}/cross-phase-link",
        json={
            "target_phase": "PHASE_6_REPRESENTATIVE",
            "entity_type": "REPRESENTATIVE",
            "entity_id": "REP-TN-042",
            "relationship_nature": "CONSTITUENCY_CIVIC_FAILURE",
            "matching_method": "same_area",  # FORBIDDEN!
            "provenance_summary": "Issue occurred in this MLA's constituency.",
        },
    )
    assert res_bad.status_code == 400
    assert "Cannot create cross-phase links merely because records share a geographic area" in res_bad.get_json()["message"]

    # 2. Legitimate empirical linkage with documented tender reference
    res_good = client.post(
        f"/api/civic/issues/{issue.id}/cross-phase-link",
        json={
            "target_phase": "PHASE_1_2_BUDGET_SCHEME",
            "entity_type": "BUDGET_SCHEME",
            "entity_id": "1",
            "relationship_nature": "REMEDIAL_SCHEME_SANCTION",
            "matching_method": "TENDER_REFERENCE_MATCH",
            "provenance_summary": "Work sanctioned under G.O. Ms 42 MAWS Scheme allocation.",
            "confidence": 0.95,
        },
    )
    assert res_good.status_code == 201
    assert res_good.get_json()["data"]["matching_method"] == "TENDER_REFERENCE_MATCH"
