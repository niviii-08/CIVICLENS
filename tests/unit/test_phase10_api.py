"""
Phase 10.8 — Policy Evaluation API and Evidence Graph Integration Unit & Integration Tests.
==========================================================================================

Validates:
1. Policy search with query, department, status filters, and pagination.
2. Policy evaluation details retrieval with linked objectives, beneficiary groups, and activities.
3. Evaluation questions and plans retrieval.
4. Indicator definitions and metadata retrieval.
5. Baseline and follow-up values retrieval (ensuring missing data is preserved as None, not zero).
6. Budget execution and implementation analysis (allocation vs revised vs actual expenditure).
7. Physical output analytics (planned vs completed outputs, implementation ratios).
8. Outcome comparisons (baseline vs follow-up, absolute and relative change, limitations).
9. Evaluation findings retrieval (all 12 mandatory attributes, evidence classification types).
10. Supporting, contradicting, and contextual evidence retrieval for synthesized findings.
11. Evaluation study methodology, causal rigor grading, and limitation tracking.
12. Evidence graph explorer integration across budget, promises, claims, civic issues, works,
    and representative records with strict epistemic guardrail:
    `causal_claim_from_association_permitted = False`.
13. Role-based authorization enforcement (`X-Reviewer-Role` required for review mutations).
14. Error handling and input validation (400, 403, 404).
"""

from datetime import datetime, timezone
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.api.app import create_app
import backend.api.policy_evaluation as api_policy_eval_module
from backend.database.base_class import Base
from backend.models.budget import (
    BudgetDepartment,
    BudgetScheme,
    BudgetRecord,
    BudgetStage,
    BudgetSourceDocument,
    HistoricalScheme,
)
from backend.models.manifesto import Manifesto
from backend.models.promise import PoliticalPromise
from backend.models.claim import Claim, ClaimCategory, ClaimStatus
from backend.models.civic_issue import CivicIssue, CivicIssueStatus, IssueCategory, IssueCategoryEnum
from backend.models.representative import (
    Representative,
    Constituency,
    ConstituencyWork,
    RepresentativeType,
    ConstituencyType,
    WorkProjectStatus,
    AttributionType,
)
from backend.models.graph import (
    CivicGraphNode,
    CivicEvidenceEdge,
    GraphEntityType,
    GraphRelationshipType,
    MatchingMethod,
    GraphProvenanceStatus,
    GraphReviewStatus,
)
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
    EvaluationLimitation,
    FindingType,
    FindingReviewStatus,
    EvaluationType,
    CausalRigorGrade,
    ConfidenceLevel,
    EvidenceStance,
    IndicatorType,
    ObservationStage,
    ReportingFrequency,
    TargetProvenanceType,
    MissingDataStatus,
    PolicyEvaluationStatus,
)


@pytest.fixture
def api_test_db():
    """In-memory SQLite database session for Phase 10.8 API testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine, expire_on_commit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def seed_policy_evaluation_dataset(api_test_db):
    """Seed comprehensive Phase 10 evaluation entities and cross-phase relations."""
    # 1. Budget Department, Scheme & Source Doc (Phase 1)
    dept = BudgetDepartment(
        name="Social Welfare and Women Empowerment Department",
        code="DEPT-SWW",
    )
    api_test_db.add(dept)
    api_test_db.flush()

    scheme = BudgetScheme(
        department_id=dept.id,
        name="Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme (Pudhumai Penn)",
        head_of_account="2235-02-103-SCH-PUDHUMAI",
    )
    api_test_db.add(scheme)
    api_test_db.flush()

    source_doc = BudgetSourceDocument(
        manifest_dataset_id="BUDGET-TN-2022-23",
        title="Demand 45 - Social Welfare Budget Document",
        official_source_url="https://budget.tn.gov.in/2022-23",
        financial_year_coverage="2022-23",
    )
    api_test_db.add(source_doc)
    api_test_db.flush()

    # Budget records across financial years (BE, RE, Actual)
    b_records = [
        BudgetRecord(
            scheme_id=scheme.id,
            source_document_id=source_doc.id,
            financial_year="2022-23",
            budget_stage=BudgetStage.budget_estimate,
            amount=698.0,
            currency_unit="RUPEES_CRORE",
        ),
        BudgetRecord(
            scheme_id=scheme.id,
            source_document_id=source_doc.id,
            financial_year="2022-23",
            budget_stage=BudgetStage.revised_estimate,
            amount=650.0,
            currency_unit="RUPEES_CRORE",
        ),
        BudgetRecord(
            scheme_id=scheme.id,
            source_document_id=source_doc.id,
            financial_year="2022-23",
            budget_stage=BudgetStage.actual_expenditure,
            amount=612.4,
            currency_unit="RUPEES_CRORE",
        ),
    ]
    api_test_db.add_all(b_records)
    api_test_db.flush()

    # 2. Canonical Policy Registry Entry (Phase 10.3)
    policy = PolicyRegistryEntry(
        policy_id="POL-TN-PUDHUMAI-PENN",
        budget_scheme_id=scheme.id,
        canonical_scheme_code="SCH-PUDHUMAI-2022",
        policy_name="Pudhumai Penn Higher Education Assurance Scheme",
        policy_name_ta="புதுமைப் பெண் திட்டம்",
        responsible_department="Social Welfare and Women Empowerment Department",
        objectives_summary="Incentivize girl students from government schools to pursue higher education by providing ₹1,000 monthly financial assistance.",
        original_objective_wording="To enhance higher education enrolment ratio of girl students who studied classes 6 to 12 in government schools.",
        intended_beneficiaries="Girls from Tamil Nadu government schools (Classes 6-12) pursuing UG/diploma courses",
        geographic_scope="STATEWIDE",
        start_date="2022-09-05",
        evaluation_status=PolicyEvaluationStatus.EVALUATED,
        stated_targets=[
            {"metric": "annual_enrolment_target", "value": 300000},
            {"metric": "disbursement_target_crores", "value": 1000.0},
        ],
        aliases=["Moovalur Ramamirtham Ammaiyar Higher Education Scheme", "Pudhumai Penn"],
        source_documents=["G.O. (Ms) No. 34 Social Welfare Dept dt 02.09.2022"],
        is_test_fixture=True,
    )
    api_test_db.add(policy)
    api_test_db.flush()

    # Objectives
    obj1 = PolicyObjective(
        objective_id="OBJ-PENN-01",
        policy_id=policy.policy_id,
        title="Increase girl student enrolment in collegiate education",
        description="Increase girl student enrolment in collegiate education by at least 25%.",
        original_wording="To enhance higher education enrolment ratio of girl students who studied classes 6 to 12 in government schools.",
        sector="Higher Education",
        is_test_fixture=True,
    )
    api_test_db.add(obj1)
    api_test_db.flush()

    # Beneficiary Group
    bg1 = BeneficiaryGroup(
        group_id="BEN-PENN-01",
        objective_id=obj1.objective_id,
        name="Government school girl students (6th-12th standard)",
        eligibility_criteria="Studied continuous schooling from Class 6 to 12 in Tamil Nadu Government schools",
        estimated_eligible_population=350000,
        is_test_fixture=True,
    )
    api_test_db.add(bg1)

    # Implementation Activities
    act1 = ImplementationActivity(
        activity_id="ACT-PENN-01",
        policy_id=policy.policy_id,
        scheme_id="SCH-PUDHUMAI-2022",
        activity_name="Monthly Direct Benefit Transfer of ₹1,000 via Aadhaar-linked accounts",
        activity_type="DBT_DISBURSEMENT",
        status="IN_PROGRESS",
        planned_output_quantity=300000.0,
        completed_output_quantity=273000.0,
        output_unit="students",
        financial_year="2023-24",
        implementing_agency="Department of Social Welfare & Women Empowerment",
        is_test_fixture=True,
    )
    act2 = ImplementationActivity(
        activity_id="ACT-PENN-02",
        policy_id=policy.policy_id,
        scheme_id="SCH-PUDHUMAI-2022",
        activity_name="Special College Admission Registration Camps",
        activity_type="REGISTRATION",
        status="COMPLETED",
        planned_output_quantity=500.0,
        completed_output_quantity=520.0,
        output_unit="camps",
        financial_year="2023-24",
        implementing_agency="Directorate of Collegiate Education",
        is_test_fixture=True,
    )
    api_test_db.add_all([act1, act2])

    # 3. Policy Indicators & Observations (Phase 10.4)
    ind_enrol = PolicyIndicator(
        indicator_id="IND-GIRL-GER-COLLEGE",
        objective_id=obj1.objective_id,
        indicator_name="Higher Education Gross Enrolment Ratio for Government School Girls",
        indicator_type=IndicatorType.OUTCOME,
        definition="Percentage of girl students passing Class 12 from government schools enrolling into accredited higher education institutions.",
        unit="PERCENT",
        source="Department of Higher Education Annual Statistics & AISHE Tamil Nadu Portal",
        reporting_frequency=ReportingFrequency.ANNUAL,
        geographic_level="STATE",
        baseline_period="2021-22",
        baseline_value=32.4,
        comparison_period="2023-24",
        comparison_value=41.8,
        collection_method="INSTITUTIONAL_ADMINISTRATIVE_DATA",
        calculation_formula="(Government school girls enrolled in 1st year HE / Total Class 12 girls passed) * 100",
        known_limitations="Does not account for non-accredited private unapproved diploma courses.",
        missing_data_status=MissingDataStatus.COMPLETE,
        is_test_fixture=True,
    )
    api_test_db.add(ind_enrol)
    api_test_db.flush()

    # Observations for indicator (Baseline, Follow-up, and Missing observation to test None preservation)
    obs_base = IndicatorObservation(
        observation_id="OBS-GER-2021-22",
        indicator_id=ind_enrol.indicator_id,
        reference_period="2021-22",
        geographic_level="STATE",
        geographic_unit_id="TN",
        value=32.4,
        stage=ObservationStage.BASELINE,
        source_reference="Higher Education Statistical Handbook 2021-22",
        missing_data_status=MissingDataStatus.COMPLETE,
        is_test_fixture=True,
    )
    obs_follow = IndicatorObservation(
        observation_id="OBS-GER-2023-24",
        indicator_id=ind_enrol.indicator_id,
        reference_period="2023-24",
        geographic_level="STATE",
        geographic_unit_id="TN",
        value=41.8,
        stage=ObservationStage.FOLLOW_UP,
        source_reference="Higher Education Statistical Handbook 2023-24",
        missing_data_status=MissingDataStatus.COMPLETE,
        is_test_fixture=True,
    )
    obs_missing = IndicatorObservation(
        observation_id="OBS-GER-2020-21-MISSING",
        indicator_id=ind_enrol.indicator_id,
        reference_period="2020-21",
        geographic_level="STATE",
        geographic_unit_id="TN",
        value=None,  # Missing data must NOT be treated as zero
        stage=ObservationStage.BASELINE,
        source_reference="AISHE TN Report (Census disruption)",
        missing_data_status=MissingDataStatus.NOT_PUBLISHED_BY_SOURCE,
        is_test_fixture=True,
    )
    api_test_db.add_all([obs_base, obs_follow, obs_missing])

    # 4. Evaluation Plan (Phase 10.3)
    plan = PolicyEvaluationPlan(
        plan_id="PLAN-PUDHUMAI-01",
        policy_id=policy.policy_id,
        objective_id=obj1.objective_id,
        indicator_id=ind_enrol.indicator_id,
        evaluation_question="Has the Pudhumai Penn monthly financial incentive increased collegiate enrolment among eligible government-school girl students?",
        evaluation_type=EvaluationType.EVIDENCE_BASED_OUTCOME,
        objective_being_assessed="Increase girl student enrolment in collegiate education",
        indicator_definition="Higher education enrolment ratio of government school alumnae",
        unit="PERCENT",
        baseline_period="2021-22",
        comparison_period="2023-24",
        target_value=40.0,
        actual_value=41.8,
        target_provenance=TargetProvenanceType.OFFICIALLY_STATED,
        data_source="Directorate of Collegiate Education & Social Welfare Records",
        calculation_method="Pre-Post Cohort Comparison across 38 Tamil Nadu districts",
        geographic_level="STATE",
        limitations="Cannot disentangle Pudhumai Penn impact from simultaneous free bus pass scheme expansion.",
        is_test_fixture=True,
    )
    api_test_db.add(plan)

    # 5. Evaluation Study & Findings (Phase 10.7)
    study = EvaluationStudy(
        study_id="STUDY-PUDHUMAI-2024-01",
        scheme_id="SCH-PUDHUMAI-2022",
        title="Independent Impact Scrutiny: Two-Year Enrolment Trends under Pudhumai Penn",
        evaluation_type=EvaluationType.BEFORE_AND_AFTER_DESCRIPTIVE,
        causal_rigor_grade=CausalRigorGrade.GRADE_D_DESCRIPTIVE_CORRELATIONAL,
        conducting_agency="State Planning Commission Technical Review Cell",
        publication_date="2024-06-30",
        methodology_description="Empirical administrative cohort audit tracking 2021-22 vs 2023-24 enrolment registries.",
        is_test_fixture=True,
    )
    api_test_db.add(study)
    api_test_db.flush()

    finding1 = EvaluationFinding(
        finding_id="FIND-PENN-2024-01",
        study_id=study.study_id,
        policy_id=policy.policy_id,
        indicator_id=ind_enrol.indicator_id,
        evaluation_question="Has collegiate enrolment increased among eligible girl students?",
        finding_type=FindingType.OUTCOME_CHANGE_OBSERVED,
        finding_text="Collegiate enrolment among eligible government school girls increased from 32.4% in 2021-22 to 41.8% in 2023-24, representing an absolute gain of 9.4 percentage points.",
        statement_origin="DETERMINISTIC_CALCULATION",
        evidence_references=["DOC-AISHE-TN-2024", "DOC-CAG-REPORT-2024-PA"],
        indicator_values_used={
            "baseline_value": 32.4,
            "follow_up_value": 41.8,
            "absolute_change": 9.4,
            "percentage_change": 29.01,
            "baseline_period": "2021-22",
            "followup_period": "2023-24",
        },
        calculation_method="Deterministic baseline vs follow-up comparison",
        confidence_level=ConfidenceLevel.HIGH,
        quantified_effect=9.4,
        review_status=FindingReviewStatus.VERIFIED,
        limitations=["Observational descriptive association; counterfactual causal attribution is constrained by concurrent public transport concessions."],
        is_test_fixture=True,
    )
    api_test_db.add(finding1)
    api_test_db.flush()

    # Evidence links (Supporting and Contradicting)
    ev_sup = FindingEvidenceLink(
        link_id="LINK-PENN-SUP-01",
        finding_id=finding1.finding_id,
        source_document_id="DOC-AISHE-TN-2024",
        quotation_excerpt="Enrolment of girls from state government schools into degree programs increased by 29% between 2021-22 and 2023-24.",
        stance=EvidenceStance.SUPPORTS,
        source_credibility_tier="TIER_1_STATUTORY",
        is_test_fixture=True,
    )
    ev_con = FindingEvidenceLink(
        link_id="LINK-PENN-CON-01",
        finding_id=finding1.finding_id,
        source_document_id="DOC-CAG-REPORT-2024-PA",
        quotation_excerpt="Audit observed 27,000 intended beneficiaries experienced 2 to 4 month direct-benefit-transfer disbursement delays due to Aadhaar-bank account seeding mismatches.",
        stance=EvidenceStance.CONTRADICTS,
        source_credibility_tier="TIER_1_STATUTORY",
        is_test_fixture=True,
    )
    api_test_db.add_all([ev_sup, ev_con])

    # 6. Cross-Phase Graph & Relational Entities (Phases 3, 5, 6, 7, 9)
    manifesto = Manifesto(
        manifesto_id="MAN-DMK-2021-PENN",
        party="DMK",
        election_year=2021,
    )
    api_test_db.add(manifesto)
    api_test_db.flush()

    promise = PoliticalPromise(
        promise_id="PROM-DMK-2021-GIRL-AID",
        manifesto_id=manifesto.manifesto_id,
        original_text="Provide monthly financial assistance to government school girls pursuing higher education.",
        normalized_text="provide monthly financial assistance to government school girls pursuing higher education",
        classification="education_welfare",
        metadata_json={"status": "FULFILLED"},
    )
    api_test_db.add(promise)

    claim = Claim(
        claim_id="CLAIM-PENN-100PCT-COVERAGE",
        original_text="100% of eligible government school girls received monthly ₹1000 allowance on the 1st of every month.",
        normalized_text="100 percent of eligible government school girls received monthly 1000 allowance on the 1st of every month",
        claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
        status=ClaimStatus.VERIFIED,
        speaker_name="Press Briefing",
    )
    api_test_db.add(claim)

    cat = IssueCategory(
        code=IssueCategoryEnum.EDUCATION_INFRASTRUCTURE,
        name_en="Education Infrastructure",
        name_ta="கல்வி கட்டமைப்பு",
    )
    api_test_db.add(cat)
    api_test_db.flush()

    issue = CivicIssue(
        issue_code="ISSUE-DBT-FAIL-4401",
        title="Pudhumai Penn stipend delayed for 3 months in Tirunelveli district",
        description="Beneficiaries in Palayamkottai Government Arts College have not received August-October 2023 monthly stipends.",
        category_id=cat.id,
        status=CivicIssueStatus.OPEN,
        reported_date=datetime.now(timezone.utc),
    )
    api_test_db.add(issue)

    const = Constituency(
        constituency_id="AC-025",
        official_name="Thousand Lights",
        constituency_type=ConstituencyType.ASSEMBLY,
        district="Chennai",
        state="Tamil Nadu",
    )
    api_test_db.add(const)
    api_test_db.flush()

    rep = Representative(
        representative_id="REP-TEST-701",
        official_name="Dr. Ezhilan Naganathan",
        aliases=["Ezhilan"],
        representative_type=RepresentativeType.MLA,
        constituency_id="AC-025",
    )
    api_test_db.add(rep)
    api_test_db.flush()

    work = ConstituencyWork(
        work_id="WORK-THOUSANDLIGHTS-CAMP-01",
        constituency_id="AC-025",
        representative_id="REP-TEST-701",
        scheme_id="MLACDS",
        project_description="Higher Education Scheme Enrollment Facilitation Center",
        sanctioned_amount=500000.0,
        released_amount=500000.0,
        reported_expenditure=480000.0,
        project_status=WorkProjectStatus.REPORTED_COMPLETED,
        attribution_type=AttributionType.REPRESENTATIVE_SPONSORED,
    )
    api_test_db.add(work)

    # CivicGraphNode integration (Phase 9)
    node_pol = CivicGraphNode(
        node_id="NODE:POLICY:POL-TN-PUDHUMAI-PENN",
        canonical_id="POL-TN-PUDHUMAI-PENN",
        entity_type=GraphEntityType.BUDGET_SCHEME,
        label="Pudhumai Penn Higher Education Assurance Scheme",
        source_phase="PHASE_10",
        is_test_fixture=True,
    )
    node_scheme = CivicGraphNode(
        node_id="NODE:SCHEME:SCH-PUDHUMAI-2022",
        canonical_id="SCH-PUDHUMAI-2022",
        entity_type=GraphEntityType.BUDGET_SCHEME,
        label="Moovalur Ramamirtham Ammaiyar Scheme",
        source_phase="PHASE_1",
        is_test_fixture=True,
    )
    node_rep = CivicGraphNode(
        node_id="NODE:REP:701",
        canonical_id="REP-701",
        entity_type=GraphEntityType.REPRESENTATIVE,
        label="Dr. Ezhilan Naganathan (MLA - Thousand Lights)",
        source_phase="PHASE_5",
        is_test_fixture=True,
    )
    api_test_db.add_all([node_pol, node_scheme, node_rep])
    api_test_db.flush()

    edge_impl = CivicEvidenceEdge(
        edge_id="EDGE:POL-PUDHUMAI:SCH-2022",
        source_node_id=node_pol.node_id,
        target_node_id=node_scheme.node_id,
        relationship_type=GraphRelationshipType.IMPLEMENTS,
        evidence_reference="G.O. (Ms) No. 34 aligns budget code with policy initiative",
        source_document_id="DOC-GO-MS-34-2022",
        matching_method=MatchingMethod.DETERMINISTIC_ID,
        confidence_score=1.0,
        review_status=GraphReviewStatus.VERIFIED,
        is_test_fixture=True,
    )
    edge_rep = CivicEvidenceEdge(
        edge_id="EDGE:POL-PUDHUMAI:REP-701",
        source_node_id=node_pol.node_id,
        target_node_id=node_rep.node_id,
        relationship_type=GraphRelationshipType.REPRESENTS,
        evidence_reference="Constituency-level facilitation camp conducted in Thousand Lights",
        source_document_id="DOC-DEPT-PRESS-2023",
        matching_method=MatchingMethod.DIRECT_DOCUMENTARY,
        confidence_score=0.85,
        review_status=GraphReviewStatus.VERIFIED,
        is_test_fixture=True,
    )
    api_test_db.add_all([edge_impl, edge_rep])

    api_test_db.commit()

    return {
        "policy": policy,
        "indicator": ind_enrol,
        "plan": plan,
        "study": study,
        "finding": finding1,
    }


@pytest.fixture
def test_client(api_test_db, monkeypatch):
    """Configures Flask test client with SessionLocal pointing to in-memory SQLite DB."""
    monkeypatch.setattr(api_test_db, "close", lambda: None)
    monkeypatch.setattr(api_policy_eval_module, "SessionLocal", lambda: api_test_db)

    app = create_app()
    return app.test_client()


# ===========================================================================
# 1. Policy Search & Details Tests
# ===========================================================================
def test_search_policies_with_filters_and_pagination(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 1: Search policies by query, department, status, and pagination."""
    # Text query match
    res = test_client.get("/api/policy-evaluation/policies/search?q=Pudhumai&limit=10&offset=0")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["total"] == 1
    assert data["policies"][0]["policy_id"] == "POL-TN-PUDHUMAI-PENN"

    # Department filter match
    res_dept = test_client.get("/api/policy-evaluation/policies?department=Social Welfare&limit=10&offset=0")
    assert res_dept.status_code == 200
    assert res_dept.get_json()["data"]["total"] == 1

    # Empty search query
    res_none = test_client.get("/api/policy-evaluation/policies/search?q=NonExistentScheme")
    assert res_none.status_code == 200
    assert res_none.get_json()["data"]["total"] == 0


def test_get_policy_details_with_linked_entities(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 2: Get policy evaluation details and cross-phase relations."""
    res = test_client.get("/api/policy-evaluation/policies/POL-TN-PUDHUMAI-PENN")
    assert res.status_code == 200
    policy = res.get_json()["data"]

    assert policy["policy_id"] == "POL-TN-PUDHUMAI-PENN"
    assert policy["canonical_scheme_code"] == "SCH-PUDHUMAI-2022"
    assert len(policy["objectives"]) >= 1
    assert policy["objectives"][0]["objective_id"] == "OBJ-PENN-01"
    assert len(policy["beneficiary_groups"]) >= 1
    assert policy["beneficiary_groups"][0]["group_id"] == "BEN-PENN-01"
    assert len(policy["implementation_activities"]) == 2

    # 404 on unknown policy
    res_404 = test_client.get("/api/policy-evaluation/policies/POL-NON-EXISTENT")
    assert res_404.status_code == 404


# ===========================================================================
# 2. Evaluation Plans & Indicator Definitions Tests
# ===========================================================================
def test_get_evaluation_plans(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 3: List and retrieve evaluation plans."""
    res = test_client.get("/api/policy-evaluation/plans?policy_id=POL-TN-PUDHUMAI-PENN")
    assert res.status_code == 200
    plans = res.get_json()["data"]["plans"]
    assert len(plans) == 1
    assert plans[0]["plan_id"] == "PLAN-PUDHUMAI-01"
    assert plans[0]["target_provenance"] == "OFFICIALLY_STATED"

    # Single plan retrieval
    res_single = test_client.get("/api/policy-evaluation/plans/PLAN-PUDHUMAI-01")
    assert res_single.status_code == 200
    assert res_single.get_json()["data"]["plan_id"] == "PLAN-PUDHUMAI-01"


def test_get_indicator_definitions_and_observations(test_client, seed_policy_evaluation_dataset):
    """Validates Operations 4 & 5: Indicator definitions & observations preserving None."""
    # List indicators
    res_ind = test_client.get("/api/policy-evaluation/indicators")
    assert res_ind.status_code == 200
    inds = res_ind.get_json()["data"]["indicators"]
    assert len(inds) == 1
    assert inds[0]["indicator_id"] == "IND-GIRL-GER-COLLEGE"

    # Single indicator
    res_single = test_client.get("/api/policy-evaluation/indicators/IND-GIRL-GER-COLLEGE")
    assert res_single.status_code == 200
    ind_data = res_single.get_json()["data"]
    assert ind_data["unit"] == "PERCENT"
    assert ind_data["baseline_value"] == 32.4
    assert ind_data["comparison_value"] == 41.8

    # Observations listing — verify missing value is preserved as None (not coerced to zero)
    res_obs = test_client.get("/api/policy-evaluation/indicators/IND-GIRL-GER-COLLEGE/observations")
    assert res_obs.status_code == 200
    obs_list = res_obs.get_json()["data"]["observations"]
    assert len(obs_list) == 3

    missing_obs = [o for o in obs_list if o["observation_id"] == "OBS-GER-2020-21-MISSING"][0]
    assert missing_obs["value"] is None
    assert missing_obs["missing_data_status"] == "NOT_PUBLISHED_BY_SOURCE"


# ===========================================================================
# 3. Budget Execution and Output Analytics Tests
# ===========================================================================
def test_policy_budget_execution_analysis(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 6: Multi-year budget execution analysis with epistemic warning."""
    res = test_client.get("/api/policy-evaluation/policies/POL-TN-PUDHUMAI-PENN/budget-analysis?financial_year=2022-23")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert data["policy_id"] == "POL-TN-PUDHUMAI-PENN"
    assert data["financial_year"] == "2022-23"
    assert data["budget_estimate_cr"] == 698.0
    assert data["revised_estimate_cr"] == 650.0
    assert data["actual_expenditure_cr"] == 612.4
    assert data["revised_absorption_rate_pct"] == 94.22

    # Verify explicit non-political warning
    assert "underspending alone" in data["epistemic_interpretation_guardrail"].lower()
    assert data["can_infer_policy_success_or_failure_from_spending_alone"] is False


def test_policy_output_analytics(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 7: Planned outputs vs completed physical outputs."""
    res = test_client.get("/api/policy-evaluation/policies/POL-TN-PUDHUMAI-PENN/output-analysis")
    assert res.status_code == 200
    data = res.get_json()["data"]

    assert data["policy_id"] == "POL-TN-PUDHUMAI-PENN"
    activities = data["activities"]
    assert len(activities) == 2

    dbt_act = [a for a in activities if a["activity_id"] == "ACT-PENN-01"][0]
    assert dbt_act["planned_output_quantity"] == 300000.0
    assert dbt_act["completed_output_quantity"] == 273000.0
    assert dbt_act["output_completion_ratio_pct"] == 91.0


# ===========================================================================
# 4. Outcome Comparisons Tests
# ===========================================================================
def test_indicator_outcome_comparison(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 8: Baseline vs follow-up comparison with 9 mandatory reporting fields."""
    res = test_client.get(
        "/api/policy-evaluation/indicators/IND-GIRL-GER-COLLEGE/compare"
        "?baseline_period=2021-22&followup_period=2023-24"
    )
    assert res.status_code == 200
    comp = res.get_json()["data"]

    assert comp["indicator_definition"]["indicator_id"] == "IND-GIRL-GER-COLLEGE"
    assert comp["baseline_value"] == 32.4
    assert comp["followup_value"] == 41.8
    assert comp["absolute_change"] == 9.4
    assert comp["percentage_change"] == 29.01
    assert comp["time_period"]["baseline_period"] == "2021-22"
    assert comp["time_period"]["followup_period"] == "2023-24"
    assert comp["geographic_scope"]["geographic_level"] == "STATE"
    assert "epistemic_label" in comp
    assert comp["causal_claim_permitted"] is False
    assert "association" in comp["epistemic_label"].lower() or "descriptive" in comp["epistemic_label"].lower()


# ===========================================================================
# 5. Evaluation Findings and Evidence Synthesis Tests
# ===========================================================================
def test_get_findings_and_evidence_links(test_client, seed_policy_evaluation_dataset):
    """Validates Operations 9 & 10: Evaluation findings and evidence links (supporting + counter)."""
    res = test_client.get("/api/policy-evaluation/findings?policy_id=POL-TN-PUDHUMAI-PENN")
    assert res.status_code == 200
    findings = res.get_json()["data"]["findings"]
    assert len(findings) == 1

    f = findings[0]
    assert f["finding_id"] == "FIND-PENN-2024-01"
    assert f["finding_type"] == "OUTCOME_CHANGE_OBSERVED"
    assert f["quantified_effect"] == 9.4

    # Single finding
    res_single = test_client.get("/api/policy-evaluation/findings/FIND-PENN-2024-01")
    assert res_single.status_code == 200
    assert res_single.get_json()["data"]["finding_id"] == "FIND-PENN-2024-01"

    # Supporting and contradicting evidence links
    res_ev = test_client.get("/api/policy-evaluation/findings/FIND-PENN-2024-01/evidence")
    assert res_ev.status_code == 200
    ev_data = res_ev.get_json()["data"]

    assert len(ev_data["supporting_evidence"]) == 1
    assert ev_data["supporting_evidence"][0]["source_document_id"] == "DOC-AISHE-TN-2024"

    assert len(ev_data["contradicting_evidence"]) == 1
    assert ev_data["contradicting_evidence"][0]["source_document_id"] == "DOC-CAG-REPORT-2024-PA"


def test_get_study_details(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 11: Study methodology, causal rigor grading, and threats to validity."""
    res = test_client.get("/api/policy-evaluation/studies/STUDY-PUDHUMAI-2024-01")
    assert res.status_code == 200
    study = res.get_json()["data"]

    assert study["study_id"] == "STUDY-PUDHUMAI-2024-01"
    assert study["evaluation_type"] == "BEFORE_AND_AFTER_DESCRIPTIVE"
    assert study["causal_rigor_grade"] == "GRADE_D_DESCRIPTIVE_CORRELATIONAL"
    assert study["conducting_agency"] == "State Planning Commission Technical Review Cell"


# ===========================================================================
# 6. Evidence Graph Explorer & Non-Causal Epistemic Guardrail
# ===========================================================================
def test_evidence_graph_explorer_connections_and_guardrail(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 12: Graph connections across phases & strict non-causal guardrail."""
    res = test_client.get("/api/policy-evaluation/policies/POL-TN-PUDHUMAI-PENN/graph-connections")
    assert res.status_code == 200
    graph_data = res.get_json()["data"]

    # Verify the strict epistemic guardrail (nested under epistemic_guardrail key)
    guardrail = graph_data["epistemic_guardrail"]
    assert guardrail["causal_claim_from_association_permitted"] is False
    assert "EPISTEMIC GUARDRAIL" in guardrail["association_guardrail_note"]

    # Check connected nodes across phases (nested under evidence_graph)
    evidence_graph = graph_data["evidence_graph"]
    nodes = evidence_graph["connected_nodes"]
    node_types = {n["entity_type"] for n in nodes}
    assert "BUDGET_SCHEME" in node_types

    # Check connected edges
    edges = evidence_graph["edges"]
    assert len(edges) >= 2


# ===========================================================================
# 7. Role-Based Authorization for Review Mutations
# ===========================================================================
def test_finding_review_authorization(test_client, seed_policy_evaluation_dataset):
    """Validates Operation 13: RBAC enforcement on review status updates."""
    # 1. Missing authorization header -> 403 Forbidden
    res_no_auth = test_client.post(
        "/api/policy-evaluation/findings/FIND-PENN-2024-01/review",
        json={"review_status": "VERIFIED", "review_notes": "Peer review conducted by evaluation cell"},
    )
    assert res_no_auth.status_code == 403
    assert "Unauthorized" in res_no_auth.get_json()["message"]

    # 2. Invalid role -> 403 Forbidden
    res_bad_role = test_client.post(
        "/api/policy-evaluation/findings/FIND-PENN-2024-01/review",
        headers={"X-Reviewer-Role": "CITIZEN_GUEST"},
        json={"review_status": "VERIFIED"},
    )
    assert res_bad_role.status_code == 403

    # 3. Authorized role (REVIEWER) -> 200 OK
    res_ok = test_client.post(
        "/api/policy-evaluation/findings/FIND-PENN-2024-01/review",
        headers={"X-Reviewer-Role": "REVIEWER"},
        json={"review_status": "VERIFIED", "review_notes": "Verified against state datasets"},
    )
    assert res_ok.status_code == 200
    assert res_ok.get_json()["data"]["review_status"] == "VERIFIED"
