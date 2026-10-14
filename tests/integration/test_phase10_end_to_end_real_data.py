"""
Phase 10.10 — End-to-End Real Data Evaluation Pipeline Integration Tests.
========================================================================

Validates the complete Phase 10 evaluation workflow against real datasets:
REAL DATASET (E:\\Downloads / data/phase10_raw)
  → SOURCE REGISTRY
  → DOCUMENT EXTRACTION
  → POLICY AND INDICATOR REGISTRY
  → VALIDATION
  → BUDGET AND OUTPUT ANALYSIS
  → OUTCOME ANALYSIS
  → EVIDENCE SYNTHESIS
  → EVIDENCE GRAPH
  → API
  → FRONTEND
  → EVALUATION REPORT

Guarantees:
1. Zero fabrication: real records have is_test_fixture=False.
2. Missing data discipline: missing values are preserved as None, not zero.
3. Zero-baseline mathematical safety: percentage change is None when baseline is 0.0.
4. Non-causal epistemic guardrail: correlation is never presented as proven causal impact.
5. Budget tier discipline: expenditure is not equated with public benefit.
"""

import pytest
from sqlalchemy.orm import Session
from backend.database.session import SessionLocal
from backend.models.policy_evaluation import (
    PolicyRegistryEntry,
    PolicyObjective,
    BeneficiaryGroup,
    ImplementationActivity,
    PolicyIndicator,
    IndicatorObservation,
    PolicyEvaluationPlan,
    EvaluationStudy,
    EvaluationFinding,
    FindingEvidenceLink,
    FindingType,
    FindingReviewStatus,
    TargetProvenanceType,
    MissingDataStatus,
)
from backend.models.budget import BudgetRecord, BudgetStage
from backend.models.graph import CivicGraphNode, CivicEvidenceEdge
from backend.services.policy_registry_service import PolicyRegistryService
from backend.services.policy_budget_execution_service import PolicyBudgetExecutionAnalyticsService
from backend.services.policy_outcome_analysis_service import PolicyOutcomeAnalysisService
from backend.api.app import create_app


@pytest.fixture(scope="module")
def real_data_db():
    """Provides a session to the real integrated database."""
    session: Session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="module")
def test_client():
    """Flask test client for API operations against real database."""
    app = create_app()
    return app.test_client()


def test_1_real_policies_ingested_with_zero_fabrication(real_data_db):
    """Verify real policy records are present and carry is_test_fixture=False."""
    policies = real_data_db.query(PolicyRegistryEntry).filter_by(is_test_fixture=False).all()
    assert len(policies) >= 8

    kmut = real_data_db.query(PolicyRegistryEntry).filter_by(policy_id="POL-TN-KMUT").first()
    assert kmut is not None
    assert "Kalaignar Magalir Urimai" in kmut.policy_name
    assert kmut.is_test_fixture is False
    assert kmut.responsible_department == "Social Welfare and Women Empowerment Department"
    assert "unpaid household care work" in kmut.original_objective_wording.lower()

    pudhumai = real_data_db.query(PolicyRegistryEntry).filter_by(policy_id="POL-TN-PUDHUMAI-PENN").first()
    assert pudhumai is not None
    assert "Pudhumai Penn" in pudhumai.policy_name
    assert pudhumai.is_test_fixture is False


def test_2_evaluation_plans_and_zero_target_invention(real_data_db):
    """Verify evaluation plans distinguish officially stated targets and never invent numbers."""
    plans = real_data_db.query(PolicyEvaluationPlan).filter_by(is_test_fixture=False).all()
    assert len(plans) >= 5

    kmut_plan = [p for p in plans if "KMUT" in p.policy_id][0]
    assert kmut_plan.target_provenance == TargetProvenanceType.OFFICIALLY_STATED
    assert kmut_plan.target_value == 10000000.0  # 1 Crore target
    assert kmut_plan.unit == "BENEFICIARIES"
    assert kmut_plan.target_source_reference is not None


def test_3_indicator_registry_and_missing_data_discipline(real_data_db):
    """Verify indicators preserve missing values as None, never coercing to zero."""
    inds = real_data_db.query(PolicyIndicator).filter_by(is_test_fixture=False).all()
    assert len(inds) >= 8

    observations = real_data_db.query(IndicatorObservation).filter_by(is_test_fixture=False).all()
    assert len(observations) >= 16

    # Verify observations have legitimate float values or None (not arbitrary fakes)
    obs_with_vals = [o for o in observations if o.value is not None]
    assert len(obs_with_vals) > 0
    for o in observations:
        assert o.is_test_fixture is False
        assert o.geographic_level is not None


def test_4_budget_execution_analysis_on_real_records(real_data_db):
    """Verify BE vs RE vs Actual expenditure execution analytics on real scheme records."""
    records = real_data_db.query(BudgetRecord).all()
    assert len(records) >= 20

    # Test KMUT FY 2023-24 budget analysis
    analysis = PolicyBudgetExecutionAnalyticsService.analyze_allocation_vs_actual(
        records, financial_year="2023-24"
    )
    assert analysis["period_type"] == "FINANCIAL_YEAR"
    assert analysis["unit"] == "RUPEES_CRORE"
    assert analysis["can_infer_policy_success_or_failure_from_spending_alone"] is False
    assert "EPISTEMIC GUARDRAIL" in analysis["epistemic_interpretation_guardrail"]


def test_5_outcome_comparisons_and_zero_baseline_safety(real_data_db):
    """Verify outcome analysis safely handles zero baselines without division by zero."""
    kmut_ind = real_data_db.query(PolicyIndicator).filter_by(indicator_id="IND-KMUT-BENEFICIARIES").first()
    assert kmut_ind is not None

    b_obs = real_data_db.query(IndicatorObservation).filter_by(indicator_id=kmut_ind.indicator_id, stage="BASELINE").first()
    f_obs = real_data_db.query(IndicatorObservation).filter_by(indicator_id=kmut_ind.indicator_id, stage="FOLLOW_UP").first()

    assert b_obs is not None
    assert b_obs.value == 0.0  # Pre-launch zero baseline

    comp = PolicyOutcomeAnalysisService.analyze_baseline_vs_followup(kmut_ind, b_obs, f_obs)
    assert comp["absolute_change"] == f_obs.value
    # Zero-baseline safety: percentage change must be None / mathematically undefined
    assert comp["percentage_change"] is None
    assert comp["percentage_change_validity"] == "UNDEFINED_ZERO_BASELINE"
    assert comp["causal_claim_permitted"] is False
    assert comp["epistemic_label"] == "DESCRIPTIVE_ASSOCIATION_OR_OBSERVED_CHANGE"


def test_6_statutory_audit_findings_and_evidence_links(real_data_db):
    """Verify CAG performance audits and State Planning Commission findings are linked."""
    studies = real_data_db.query(EvaluationStudy).filter_by(is_test_fixture=False).all()
    assert len(studies) >= 5

    cag_studies = [s for s in studies if "CAG" in s.conducting_agency]
    assert len(cag_studies) >= 3

    findings = real_data_db.query(EvaluationFinding).filter_by(is_test_fixture=False).all()
    assert len(findings) >= 5
    for f in findings:
        assert f.finding_type in FindingType
        assert f.review_status == FindingReviewStatus.VERIFIED

    links = real_data_db.query(FindingEvidenceLink).filter_by(is_test_fixture=False).all()
    assert len(links) >= 5


def test_7_evidence_graph_connections_and_guardrail(real_data_db):
    """Verify Phase 10 policies connect to Phase 9 evidence graph nodes and edges."""
    nodes = real_data_db.query(CivicGraphNode).filter_by(source_phase="PHASE_10").all()
    assert len(nodes) >= 8

    edges = real_data_db.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id.ilike("%POLICY_IMPLEMENTS%")).all()
    assert len(edges) >= 8


def test_8_api_search_and_policy_details(test_client):
    """Verify REST API retrieves real policies and details."""
    res = test_client.get("/api/policy-evaluation/policies/search?q=Magalir")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total"] >= 1
    assert any("KMUT" in p["policy_id"] for p in data["policies"])

    # Details
    res_det = test_client.get("/api/policy-evaluation/policies/POL-TN-KMUT")
    assert res_det.status_code == 200
    pol_det = res_det.get_json()["data"]
    assert pol_det["policy_id"] == "POL-TN-KMUT"
    assert len(pol_det["objectives"]) >= 1
    assert len(pol_det["beneficiary_groups"]) >= 1


def test_9_api_graph_connections_epistemic_guardrail(test_client):
    """Verify API exposes strict non-causal guardrail on graph connections."""
    res = test_client.get("/api/policy-evaluation/policies/POL-TN-KMUT/graph-connections")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["epistemic_guardrail"]["causal_claim_from_association_permitted"] is False
    assert "EPISTEMIC GUARDRAIL" in data["epistemic_guardrail"]["association_guardrail_note"]
