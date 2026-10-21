"""
CIVICLENS TN — Phase 13.3 Scheme and Budget Impact Analysis Test Suite.
Verifies transparent, non-causal fiscal tracking, multi-tier metric distinction,
compatibility auditing, and epistemic guardrails.
"""

import pytest
from backend.database.session import SessionLocal
from backend.services.scheme_budget_impact_service import (
    SchemeBudgetImpactService,
    IncompatibleMetricComparisonError,
    EPISTEMIC_ALLOCATION_VS_EXPENDITURE,
    EPISTEMIC_CORRELATION_VS_CAUSATION,
    EPISTEMIC_ABSENCE_OF_EVIDENCE,
)


@pytest.fixture
def service():
    db = SessionLocal()
    svc = SchemeBudgetImpactService(db)
    yield svc
    db.close()


def test_1_metric_separation_and_guardrails(service):
    """
    Instruction 4 & 5: Distinguish BE, RE, AE, Beneficiary counts, Reported Output, Measured Outcome.
    Verify that allocation != expenditure and expenditure != proof of impact.
    """
    analysis = service.analyze_scheme_impact("SCH-TN-KMUT")

    # 1. Scheme Identity
    ident = analysis["scheme_identity"]
    assert ident["canonical_code"] == "SCH-TN-KMUT"
    assert "Magalir" in ident["scheme_name"]
    assert "Social Welfare" in ident["department_name"]

    # 2. Financial Inputs (BE, RE, AE)
    financials = analysis["financial_inputs"]
    assert financials["currency_unit"] == "RUPEES_CRORE"
    assert EPISTEMIC_ALLOCATION_VS_EXPENDITURE in financials["epistemic_guardrail"]

    timeline = financials["financial_timeline"]
    assert len(timeline) >= 2

    # Check FY 2023-24 (has BE, RE, AE)
    fy23 = next((t for t in timeline if t["financial_year"] == "2023-24"), None)
    assert fy23 is not None
    assert fy23["budget_allocation_cr"] == 7000.0
    assert fy23["revised_estimate_cr"] == 7997.0
    assert fy23["actual_expenditure_cr"] == 7995.12
    # Utilization calculated strictly against allocation
    assert fy23["utilization_rate_pct"] == 114.22
    assert fy23["expenditure_status"] == "ACTUALS_AUDITED_AND_CLOSED"

    # 3. Verified Beneficiary Counts
    ben = analysis["verified_beneficiaries"]
    assert ben["primary_metric"] is not None
    assert ben["primary_metric"]["verified_beneficiaries_count"] == 10650000.0
    assert ben["primary_metric"]["unit"] == "COUNT"

    # Unit cost analysis: 7995.12 Cr / 10,650,000 = ~7507.15 INR
    unit_cost = ben["unit_cost_analysis"]
    assert unit_cost is not None
    assert unit_cost["annual_cost_per_beneficiary_inr"] == 7507.15
    assert unit_cost["monthly_benefit_equivalent_inr"] == 625.60

    # 4. Measured Outcomes & Non-Causal Epistemic Classification
    outcomes = analysis["measured_outcomes"]
    assert outcomes["outcomes_count"] >= 1
    assert EPISTEMIC_CORRELATION_VS_CAUSATION in outcomes["epistemic_guardrail"]

    primary_outcome = outcomes["items"][0]
    assert primary_outcome["epistemic_classification"] == "DESCRIPTIVE_ASSOCIATION_OR_OBSERVED_CHANGE"
    assert "Causal attribution requires counterfactual" in primary_outcome["methodological_caveat"]


def test_2_missing_and_unclosed_fiscal_periods(service):
    """
    Instruction 7 & 10: Explain missing periods, unclosed accounts, and absence of data.
    FY 2024-25 has BE & RE, but AE is pending AG audit closure.
    """
    analysis = service.analyze_scheme_impact("SCH-TN-KMUT")
    timeline = analysis["financial_inputs"]["financial_timeline"]

    fy24 = next((t for t in timeline if t["financial_year"] == "2024-25"), None)
    assert fy24 is not None
    assert fy24["budget_allocation_cr"] == 13720.0
    assert fy24["revised_estimate_cr"] == 13720.0
    assert fy24["actual_expenditure_cr"] is None
    # Must NOT fabricate utilization rate or treat missing as zero
    assert fy24["utilization_rate_pct"] is None
    assert fy24["expenditure_status"] == "REVISED_ESTIMATE_PUBLISHED_PENDING_ACTUALS"

    limitations = analysis["data_completeness_and_limitations"]
    assert any("actual expenditure is pending" in note for note in limitations["notes"])
    assert EPISTEMIC_ABSENCE_OF_EVIDENCE in limitations["absence_of_data_principle"]


def test_3_accessible_sources_and_citations(service):
    """
    Instruction 3 & 9: Make underlying records and sources accessible with dates, pages, and URLs.
    """
    analysis = service.analyze_scheme_impact("SCH-TN-KMUT")
    timeline = analysis["financial_inputs"]["financial_timeline"]

    # Verify source citations exist on financial timeline
    all_sources = [s for t in timeline for s in t.get("sources", [])]
    assert len(all_sources) >= 1
    sample_src = all_sources[0]
    assert "title" in sample_src
    assert "official_url" in sample_src
    assert sample_src["official_url"].startswith("http")


def test_4_scheme_comparison_compatible(service):
    """
    Instruction 6 & 8: Structured multi-scheme comparison with compatibility checks.
    """
    comp = service.compare_schemes_impact(["SCH-TN-KMUT", "SCH-TN-CM-BREAKFAST"], financial_year="2023-24")
    assert comp["comparison_financial_year"] == "2023-24"
    assert len(comp["comparison_matrix"]) == 2

    kmut_row = next((r for r in comp["comparison_matrix"] if "KMUT" in r["canonical_code"] or "Magalir" in r["scheme_name"]), None)
    brk_row = next((r for r in comp["comparison_matrix"] if "BREAKFAST" in r["canonical_code"] or "Breakfast" in r["scheme_name"]), None)

    assert kmut_row is not None
    assert brk_row is not None

    # KMUT has verified beneficiaries
    assert kmut_row["actual_expenditure_cr"] == 7995.12
    assert kmut_row["verified_beneficiaries"] == 10650000.0
    assert kmut_row["unit_cost_per_beneficiary_inr"] == 7507.15

    # Breakfast has expenditure, but no beneficiary count in DB -> must be None, NOT zero or fabricated
    assert brk_row["actual_expenditure_cr"] == 498.2
    assert brk_row["verified_beneficiaries"] is None
    assert brk_row["unit_cost_per_beneficiary_inr"] is None


def test_5_scheme_comparison_incompatible_rejection(service):
    """
    Instruction 6: Reject comparison when fewer than 2 schemes are provided.
    """
    with pytest.raises(IncompatibleMetricComparisonError) as exc_info:
        service.compare_schemes_impact(["SCH-TN-KMUT"])
    assert "At least two schemes are required" in str(exc_info.value)


def test_6_unknown_scheme_handling(service):
    """
    Edge case: Nonexistent scheme identifier must raise clear ValueError without silent fabrication.
    """
    with pytest.raises(ValueError) as exc_info:
        service.analyze_scheme_impact("NON_EXISTENT_SCHEME_9999")
    assert "could not be resolved" in str(exc_info.value)


def test_7_api_endpoint_scheme_impact_analysis(api_client):
    """
    Verify GET /api/schemes/<scheme_id>/impact-analysis endpoint.
    """
    res = api_client.get("/api/schemes/SCH-TN-KMUT/impact-analysis")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["scheme_identity"]["canonical_code"] == "SCH-TN-KMUT"
    assert "financial_inputs" in data
    assert "verified_beneficiaries" in data
    assert "measured_outcomes" in data


def test_8_api_endpoint_compare_impact(api_client):
    """
    Verify GET /api/schemes/compare-impact endpoint.
    """
    res = api_client.get("/api/schemes/compare-impact?ids=SCH-TN-KMUT,SCH-TN-CM-BREAKFAST")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "comparison_matrix" in data
    assert len(data["comparison_matrix"]) == 2


def test_9_api_endpoint_compare_mode_delegate(api_client):
    """
    Verify GET /api/schemes/compare?ids=...&mode=impact delegates to impact analysis.
    """
    res = api_client.get("/api/schemes/compare?ids=SCH-TN-KMUT,SCH-TN-CM-BREAKFAST&mode=impact")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "comparison_matrix" in data


def test_10_api_endpoint_budget_scheme_impact_analysis(api_client):
    """
    Verify GET /api/budget/schemes/<scheme_id>/impact-analysis endpoint.
    """
    res = api_client.get("/api/budget/schemes/SCH-TN-KMUT/impact-analysis")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert data["scheme_identity"]["canonical_code"] == "SCH-TN-KMUT"
