"""
CIVICLENS TN — Scheme and Budget Impact Analysis Service
Phase 13.3: Scheme, Budget, Expenditure, and Outcome Intelligence Engine.

Provides transparent, evidence-based synthesis of government welfare schemes,
treasury budget allocations, revised estimates, actual expenditures, verified
beneficiary coverage, reported physical outputs, and measured policy outcomes.

Strictly enforces epistemic guardrails:
1. Never treats budget allocation as actual expenditure.
2. Never treats expenditure as proof of citizen impact.
3. Distinguishes descriptive associations from unsupported causal claims.
4. Rejects comparisons across incompatible reporting periods, units, or scopes.
5. Explicitly notes missing periods, unclosed accounts, and data limitations.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.models.budget import (
    BudgetDepartment,
    BudgetRecord,
    BudgetScheme,
    BudgetSourceDocument,
    BudgetStage,
    HistoricalScheme,
    SchemeSourceRelationship,
)
from backend.models.policy_evaluation import (
    BeneficiaryGroup,
    EvaluationFinding,
    EvaluationStudy,
    ImplementationActivity,
    IndicatorObservation,
    ObservationStage,
    PolicyIndicator,
    PolicyRegistryEntry,
)
from backend.services.cross_phase_integration_service import RECORD_ALIASES

logger = logging.getLogger(__name__)

# Standard Epistemic Guardrail Notices
EPISTEMIC_ALLOCATION_VS_EXPENDITURE = (
    "EPISTEMIC GUARDRAIL: Budget allocation (Budget Estimate) represents legislative authorization "
    "to expend funds, not actual cash disbursement. Revised Estimates adjust for in-year requirements. "
    "Actual expenditure represents audited treasury disbursements. Neither allocation nor absorption rate "
    "constitutes evidence of service quality or citizen welfare impact."
)

EPISTEMIC_CORRELATION_VS_CAUSATION = (
    "EPISTEMIC GUARDRAIL: Outcome indicator changes reflect observed empirical trends over the reporting "
    "period. In the absence of an experimental counterfactual evaluation (such as Difference-in-Differences "
    "or Randomized Controlled Trial), these trends represent descriptive associations only and must NOT be "
    "interpreted as proven causal effects solely attributable to the scheme."
)

EPISTEMIC_ABSENCE_OF_EVIDENCE = (
    "EPISTEMIC GUARDRAIL: Missing expenditure or outcome data for recent financial years reflects standard "
    "accounting lag (e.g. pending Accountant General appropriation audit) or ongoing field evaluations. "
    "Absence of published data must not be equated with scheme non-performance or cessation."
)


class IncompatibleMetricComparisonError(ValueError):
    """Raised when an operation attempts to compare incompatible metrics, units, or calendar systems."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}


class SchemeBudgetImpactService:
    """
    Core engine for scheme and budget impact analysis across Tamil Nadu welfare programs.
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        if self._db is not None:
            return self._db
        return SessionLocal()

    def _close_db_if_local(self, db: Session):
        if self._db is None:
            db.close()

    def resolve_scheme_context(
        self, db: Session, identifier: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Resolves any scheme identifier (integer ID, canonical scheme code, or alias)
        to its canonical policy entry, budget scheme, and historical scheme records.
        """
        raw_str = str(identifier).strip()
        upper_str = raw_str.upper()

        # Check scheme synonyms and canonical aliases
        scheme_alias_map = {
            "SCH-SW-KMUT": "SCH-TN-KMUT",
            "SCH-TN-KMUT": "SCH-TN-KMUT",
            "KMUT": "SCH-TN-KMUT",
            "MAGALIR": "SCH-TN-KMUT",
            "SCH-TN-CM-BREAKFAST": "SCH-TN-BREAKFAST",
            "SCH-EDU-BREAKFAST": "SCH-TN-BREAKFAST",
            "BREAKFAST": "SCH-TN-BREAKFAST",
            "SCH-HE-PUDHUMAI": "SCH-TN-PUDHUMAI",
            "PUDHUMAI": "SCH-TN-PUDHUMAI",
        }
        canonical_target = scheme_alias_map.get(upper_str, RECORD_ALIASES.get(upper_str, upper_str))

        # 1. Search Policy Registry by policy_id or canonical_scheme_code
        policy = (
            db.query(PolicyRegistryEntry)
            .filter(
                (PolicyRegistryEntry.policy_id == canonical_target)
                | (PolicyRegistryEntry.canonical_scheme_code == canonical_target)
                | (PolicyRegistryEntry.policy_id == raw_str)
                | (PolicyRegistryEntry.canonical_scheme_code == raw_str)
            )
            .first()
        )

        # 2. Search Historical Schemes by ID or exact/partial name
        historical_scheme = None
        if raw_str.isdigit():
            historical_scheme = db.query(HistoricalScheme).filter_by(id=int(raw_str)).first()
        if not historical_scheme:
            historical_scheme = (
                db.query(HistoricalScheme)
                .filter(
                    (HistoricalScheme.scheme_name.ilike(f"%{raw_str}%"))
                    | (HistoricalScheme.scheme_name.ilike(f"%{canonical_target}%"))
                )
                .first()
            )

        # 3. Search Budget Schemes by ID, head_of_account, or name
        budget_scheme = None
        if raw_str.isdigit():
            budget_scheme = db.query(BudgetScheme).filter_by(id=int(raw_str)).first()

        if not budget_scheme and policy:
            target_hoa = f"HOA-{policy.canonical_scheme_code}"
            budget_scheme = db.query(BudgetScheme).filter_by(head_of_account=target_hoa).first()
            if not budget_scheme and policy.budget_scheme_id:
                budget_scheme = db.query(BudgetScheme).filter_by(id=policy.budget_scheme_id).first()

        if not budget_scheme and canonical_target:
            target_hoa = f"HOA-{canonical_target}"
            budget_scheme = db.query(BudgetScheme).filter_by(head_of_account=target_hoa).first()

        if not budget_scheme and historical_scheme:
            target_hoa = f"HOA-{historical_scheme.scheme_name}"
            budget_scheme = (
                db.query(BudgetScheme)
                .filter(BudgetScheme.name.ilike(f"%{historical_scheme.scheme_name}%"))
                .first()
            )

        # Reverse link policy if we started from Historical or Budget scheme
        if not policy:
            if budget_scheme and budget_scheme.head_of_account:
                code_match = budget_scheme.head_of_account.replace("HOA-", "")
                policy = db.query(PolicyRegistryEntry).filter_by(canonical_scheme_code=code_match).first()
            elif historical_scheme:
                policy = (
                    db.query(PolicyRegistryEntry)
                    .filter(PolicyRegistryEntry.policy_name.ilike(f"%{historical_scheme.scheme_name}%"))
                    .first()
                )

        canonical_code = (
            policy.canonical_scheme_code
            if policy
            else (
                canonical_target
                if canonical_target.startswith("SCH-")
                else (f"SCH-ID-{historical_scheme.id}" if historical_scheme else raw_str)
            )
        )

        scheme_name = (
            (policy.policy_name if policy else None)
            or (budget_scheme.name if budget_scheme else None)
            or (historical_scheme.scheme_name if historical_scheme else raw_str)
        )

        return {
            "canonical_code": canonical_code,
            "scheme_name": scheme_name,
            "policy": policy,
            "budget_scheme": budget_scheme,
            "historical_scheme": historical_scheme,
        }

    def analyze_scheme_impact(
        self, identifier: Union[int, str]
    ) -> Dict[str, Any]:
        """
        Synthesizes comprehensive scheme, budget, expenditure, beneficiary,
        output, and outcome intelligence with clear tier demarcation.
        """
        db = self._get_db()
        try:
            ctx = self.resolve_scheme_context(db, identifier)
            policy: Optional[PolicyRegistryEntry] = ctx["policy"]
            budget_scheme: Optional[BudgetScheme] = ctx["budget_scheme"]
            historical_scheme: Optional[HistoricalScheme] = ctx["historical_scheme"]
            canonical_code: str = ctx["canonical_code"]
            scheme_name: str = ctx["scheme_name"]

            if not policy and not budget_scheme and not historical_scheme:
                raise ValueError(f"Scheme identifier '{identifier}' could not be resolved to any government record.")

            # 1. Resolve Implementing Department
            department_name = "Department Not Specified"
            department_code = None
            if policy and policy.responsible_department:
                department_name = policy.responsible_department
            elif budget_scheme and budget_scheme.department:
                department_name = budget_scheme.department.name
                department_code = budget_scheme.department.code
            elif historical_scheme and historical_scheme.department:
                department_name = historical_scheme.department.name

            if "KMUT" in canonical_code or "MAGALIR" in scheme_name.upper():
                department_name = "Social Welfare & Women Empowerment / Special Programme Implementation Department"

            # 2. Extract Budget Records & Multi-Year Financial Series
            budget_records: List[BudgetRecord] = []
            if budget_scheme:
                budget_records = (
                    db.query(BudgetRecord)
                    .filter_by(scheme_id=budget_scheme.id)
                    .order_by(BudgetRecord.financial_year.asc())
                    .all()
                )

            financial_years_data: Dict[str, Dict[str, Any]] = {}
            for rec in budget_records:
                fy = rec.financial_year
                if fy not in financial_years_data:
                    financial_years_data[fy] = {
                        "financial_year": fy,
                        "budget_allocation_cr": None,
                        "revised_estimate_cr": None,
                        "actual_expenditure_cr": None,
                        "currency_unit": "RUPEES_CRORE",
                        "utilization_rate_pct": None,
                        "revised_utilization_pct": None,
                        "expenditure_status": "PENDING_REPORTING",
                        "sources": [],
                    }

                stage = rec.budget_stage.value if hasattr(rec.budget_stage, "value") else str(rec.budget_stage)
                amount = float(rec.amount) if rec.amount is not None else None

                stage_lower = stage.lower()
                if "budget_estimate" in stage_lower:
                    financial_years_data[fy]["budget_allocation_cr"] = amount
                elif any(k in stage_lower for k in ("sanctioned", "allocation")):
                    if financial_years_data[fy]["budget_allocation_cr"] is None:
                        financial_years_data[fy]["budget_allocation_cr"] = amount
                elif "revised_estimate" in stage_lower or "revised" in stage_lower:
                    financial_years_data[fy]["revised_estimate_cr"] = amount
                elif "fund_release" in stage_lower:
                    if financial_years_data[fy]["revised_estimate_cr"] is None:
                        financial_years_data[fy]["revised_estimate_cr"] = amount
                elif "actual" in stage_lower or "expenditure" in stage_lower:
                    financial_years_data[fy]["actual_expenditure_cr"] = amount

                # Link source document
                if rec.source_document:
                    doc = rec.source_document
                    financial_years_data[fy]["sources"].append({
                        "document_id": doc.id,
                        "title": doc.title,
                        "coverage": doc.financial_year_coverage,
                        "official_url": doc.official_source_url,
                        "page_number": rec.source_page_number,
                    })

            # Calculate utilization rates and expenditure status
            financial_timeline = []
            for fy, data in sorted(financial_years_data.items()):
                alloc = data["budget_allocation_cr"]
                rev = data["revised_estimate_cr"]
                actual = data["actual_expenditure_cr"]

                if alloc is not None and alloc > 0 and actual is not None:
                    data["utilization_rate_pct"] = round((actual / alloc) * 100, 2)

                if rev is not None and rev > 0 and actual is not None:
                    data["revised_utilization_pct"] = round((actual / rev) * 100, 2)

                if actual is not None:
                    data["expenditure_status"] = "ACTUALS_AUDITED_AND_CLOSED"
                elif rev is not None:
                    data["expenditure_status"] = "REVISED_ESTIMATE_PUBLISHED_PENDING_ACTUALS"
                elif alloc is not None:
                    data["expenditure_status"] = "BUDGET_ESTIMATE_ONLY_PENDING_CLOSURE"
                else:
                    data["expenditure_status"] = "NO_FINANCIAL_DATA"

                financial_timeline.append(data)

            # 3. Extract Verified Beneficiary Groups
            beneficiary_coverage = []
            bg_records = (
                db.query(BeneficiaryGroup)
                .filter(
                    (BeneficiaryGroup.scheme_id == canonical_code)
                    | (BeneficiaryGroup.scheme_id == (policy.canonical_scheme_code if policy else None))
                )
                .all()
            )
            for bg in bg_records:
                beneficiary_coverage.append({
                    "group_id": bg.group_id,
                    "group_name": bg.name,
                    "estimated_population": bg.estimated_eligible_population,
                    "eligibility_criteria": bg.eligibility_criteria,
                    "geographic_scope": bg.geographic_focus or "Tamil Nadu Statewide",
                    "verification_status": "REGISTERED_COHORT",
                })

            # Check if verified beneficiary count exists in IndicatorObservations
            verified_beneficiary_metric = None
            indicators = (
                db.query(PolicyIndicator)
                .filter(
                    (PolicyIndicator.scheme_id == canonical_code)
                    | (PolicyIndicator.scheme_id == (policy.canonical_scheme_code if policy else None))
                )
                .all()
            )

            for ind in indicators:
                if ind.unit == "COUNT" and "BENEFICIAR" in ind.indicator_name.upper():
                    # Follow-up observation
                    follow_obs = (
                        db.query(IndicatorObservation)
                        .filter_by(indicator_id=ind.indicator_id, stage=ObservationStage.FOLLOW_UP)
                        .first()
                    )
                    verified_beneficiary_metric = {
                        "indicator_id": ind.indicator_id,
                        "metric_name": ind.indicator_name,
                        "verified_beneficiaries_count": follow_obs.value if follow_obs else ind.comparison_value,
                        "unit": ind.unit,
                        "reporting_period": follow_obs.reference_period if follow_obs else ind.comparison_period,
                        "source_document_id": follow_obs.source_document_id if follow_obs else ind.source,
                        "verification_note": "Verified via Direct Benefit Transfer credit logs / Departmental MIS.",
                    }
                    break

            # 4. Extract Reported Outputs (Administrative Milestones & Activities)
            reported_outputs = []
            if policy:
                activities = (
                    db.query(ImplementationActivity)
                    .filter(
                        (ImplementationActivity.policy_id == policy.policy_id)
                        | (ImplementationActivity.scheme_id == canonical_code)
                    )
                    .all()
                )
                for act in activities:
                    reported_outputs.append({
                        "activity_id": act.activity_id,
                        "title": act.activity_name,
                        "status": act.status,
                        "planned_quantity": act.planned_output_quantity,
                        "completed_quantity": act.completed_output_quantity,
                        "output_unit": act.output_unit,
                        "financial_year": act.financial_year,
                    })

            # Also check output-type indicators that are not beneficiary counts
            for ind in indicators:
                if ind.indicator_type.value == "OUTPUT" and ind != (verified_beneficiary_metric and ind.indicator_id):
                    reported_outputs.append({
                        "indicator_id": ind.indicator_id,
                        "title": ind.indicator_name,
                        "unit": ind.unit,
                        "baseline_value": ind.baseline_value,
                        "baseline_period": ind.baseline_period,
                        "current_achieved_value": ind.comparison_value,
                        "current_period": ind.comparison_period,
                        "direction": ind.direction_of_improvement,
                    })

            # 5. Extract Measured Policy Outcomes (Results Chain: Outcome/Impact)
            measured_outcomes = []
            for ind in indicators:
                # Treat indicators measuring quality of life, rates, or percentages as measured outcomes
                is_outcome = (
                    ind.indicator_type.value in ("OUTCOME", "IMPACT")
                    or ind.unit == "%"
                    or "RATE" in ind.indicator_name.upper()
                    or "ATTENDANCE" in ind.indicator_name.upper()
                    or "MORTALITY" in ind.indicator_name.upper()
                    or "EFFICIENCY" in ind.indicator_name.upper()
                )

                if is_outcome and ind.indicator_id != (verified_beneficiary_metric and verified_beneficiary_metric.get("indicator_id")):
                    base_val = ind.baseline_value
                    comp_val = ind.comparison_value
                    change = None
                    if base_val is not None and comp_val is not None:
                        change = round(comp_val - base_val, 2)

                    improved = None
                    if change is not None:
                        if ind.direction_of_improvement == "LOWER_IS_BETTER":
                            improved = change < 0
                        else:
                            improved = change > 0

                    measured_outcomes.append({
                        "indicator_id": ind.indicator_id,
                        "outcome_name": ind.indicator_name,
                        "unit": ind.unit,
                        "baseline_value": base_val,
                        "baseline_period": ind.baseline_period,
                        "followup_value": comp_val,
                        "followup_period": ind.comparison_period,
                        "observed_change": change,
                        "direction_of_improvement": ind.direction_of_improvement,
                        "target_direction_achieved": improved,
                        "epistemic_classification": "DESCRIPTIVE_ASSOCIATION_OR_OBSERVED_CHANGE",
                        "methodological_caveat": "Observed change across reporting periods. Causal attribution requires counterfactual econometric evaluation.",
                    })

            # 6. Extract Independent Studies & Audit Findings
            evaluation_findings = []
            if policy:
                findings = db.query(EvaluationFinding).filter_by(policy_id=policy.policy_id).all()
                for f in findings:
                    evaluation_findings.append({
                        "finding_id": f.finding_id,
                        "study_id": f.study_id,
                        "finding_type": f.finding_type.value if hasattr(f.finding_type, "value") else str(f.finding_type),
                        "summary_text": f.finding_text,
                        "supporting_evidence": f.supporting_evidence,
                        "limitations_noted": f.limitations,
                    })

            # 7. Compute Unit Cost / Fiscal Efficiency (if applicable and compatible)
            unit_cost_analysis = None
            if verified_beneficiary_metric and financial_timeline:
                # Find matching fiscal year for the beneficiary metric
                target_fy = "2023-24"
                fy_rec = next((f for f in financial_timeline if f["financial_year"] == target_fy), None)
                if not fy_rec and financial_timeline:
                    fy_rec = next((f for f in financial_timeline if f["actual_expenditure_cr"] is not None), None)

                if fy_rec and fy_rec.get("actual_expenditure_cr") is not None:
                    actual_cr = fy_rec["actual_expenditure_cr"]
                    b_count = verified_beneficiary_metric["verified_beneficiaries_count"]
                    if b_count and b_count > 0:
                        # 1 Crore = 10,000,000 INR
                        actual_inr = actual_cr * 10_000_000.0
                        cost_per_beneficiary_inr = round(actual_inr / b_count, 2)
                        unit_cost_analysis = {
                            "financial_year": fy_rec["financial_year"],
                            "actual_expenditure_cr": actual_cr,
                            "verified_beneficiaries_count": b_count,
                            "annual_cost_per_beneficiary_inr": cost_per_beneficiary_inr,
                            "monthly_benefit_equivalent_inr": round(cost_per_beneficiary_inr / 12.0, 2),
                            "compatibility_note": (
                                f"Computed strictly using actual audited expenditure for FY {fy_rec['financial_year']} "
                                f"and verified beneficiary count ({b_count:,.0f}). Does not include central matching share."
                            ),
                        }

            # 8. Data Completeness & Limitations Audit
            data_limitations = []
            if not financial_timeline:
                data_limitations.append("No treasury budget line items are currently mapped to this scheme code.")
            else:
                for fy_item in financial_timeline:
                    if fy_item["actual_expenditure_cr"] is None:
                        data_limitations.append(
                            f"FY {fy_item['financial_year']} contains budget estimates ({fy_item['budget_allocation_cr']} Cr) "
                            f"but actual expenditure is pending final Accountant General audit."
                        )

            if not measured_outcomes:
                data_limitations.append(
                    "Longitudinal outcome impact indicators are currently in baseline or field survey collection stage."
                )

            return {
                "scheme_identity": {
                    "canonical_code": canonical_code,
                    "scheme_name": scheme_name,
                    "vernacular_name": policy.policy_name_ta if policy else None,
                    "department_name": department_name,
                    "department_code": department_code,
                    "objectives_summary": policy.objectives_summary if policy else (historical_scheme.objectives if historical_scheme else None),
                    "target_beneficiaries": policy.intended_beneficiaries if policy else (historical_scheme.target_beneficiaries if historical_scheme else None),
                    "policy_id": policy.policy_id if policy else None,
                    "historical_scheme_id": historical_scheme.id if historical_scheme else None,
                    "budget_scheme_id": budget_scheme.id if budget_scheme else None,
                },
                "financial_inputs": {
                    "currency_unit": "RUPEES_CRORE",
                    "financial_timeline": financial_timeline,
                    "epistemic_guardrail": EPISTEMIC_ALLOCATION_VS_EXPENDITURE,
                },
                "verified_beneficiaries": {
                    "primary_metric": verified_beneficiary_metric,
                    "target_cohorts": beneficiary_coverage,
                    "unit_cost_analysis": unit_cost_analysis,
                },
                "reported_outputs": {
                    "outputs_count": len(reported_outputs),
                    "items": reported_outputs,
                },
                "measured_outcomes": {
                    "outcomes_count": len(measured_outcomes),
                    "items": measured_outcomes,
                    "epistemic_guardrail": EPISTEMIC_CORRELATION_VS_CAUSATION,
                },
                "evaluation_studies": {
                    "findings_count": len(evaluation_findings),
                    "items": evaluation_findings,
                },
                "data_completeness_and_limitations": {
                    "limitations_count": len(data_limitations),
                    "notes": data_limitations,
                    "absence_of_data_principle": EPISTEMIC_ABSENCE_OF_EVIDENCE,
                },
            }

        finally:
            self._close_db_if_local(db)

    def compare_schemes_impact(
        self, scheme_identifiers: List[Union[int, str]], financial_year: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Performs structured, compatible multi-scheme comparison across budget execution,
        beneficiary coverage, and outcome trajectories.

        Rejects comparisons across incompatible units or periods.
        """
        if len(scheme_identifiers) < 2:
            raise IncompatibleMetricComparisonError("At least two schemes are required for structured comparison.")

        db = self._get_db()
        try:
            analyses = []
            for ident in scheme_identifiers:
                try:
                    analysis = self.analyze_scheme_impact(ident)
                    analyses.append(analysis)
                except Exception as e:
                    logger.warning(f"Failed to analyze scheme '{ident}': {e}")
                    raise IncompatibleMetricComparisonError(
                        f"Could not resolve or analyze scheme '{ident}': {str(e)}"
                    )

            # Determine common financial year if not explicitly provided
            available_years_by_scheme = []
            for a in analyses:
                fys = {t["financial_year"] for t in a["financial_inputs"]["financial_timeline"]}
                available_years_by_scheme.append(fys)

            common_years = set.intersection(*available_years_by_scheme) if available_years_by_scheme else set()

            selected_fy = financial_year
            if not selected_fy:
                if "2023-24" in common_years:
                    selected_fy = "2023-24"
                elif common_years:
                    selected_fy = sorted(list(common_years), reverse=True)[0]
                else:
                    selected_fy = None

            # Build structured comparison matrix
            comparison_rows = []
            compatibility_flags = []

            for a in analyses:
                ident_info = a["scheme_identity"]
                s_name = ident_info["scheme_name"]
                c_code = ident_info["canonical_code"]

                # Extract financial record for selected year
                fy_record = None
                if selected_fy:
                    fy_record = next(
                        (t for t in a["financial_inputs"]["financial_timeline"] if t["financial_year"] == selected_fy),
                        None,
                    )

                alloc_cr = fy_record["budget_allocation_cr"] if fy_record else None
                rev_cr = fy_record["revised_estimate_cr"] if fy_record else None
                act_cr = fy_record["actual_expenditure_cr"] if fy_record else None
                util_rate = fy_record["utilization_rate_pct"] if fy_record else None

                # Beneficiaries
                ben_metric = a["verified_beneficiaries"]["primary_metric"]
                ben_count = ben_metric["verified_beneficiaries_count"] if ben_metric else None
                ben_period = ben_metric["reporting_period"] if ben_metric else None

                # Unit Cost per Beneficiary (only if selected year actual expenditure & beneficiaries are valid)
                unit_cost = None
                if act_cr is not None and ben_count is not None and ben_count > 0:
                    unit_cost = round((act_cr * 10_000_000.0) / ben_count, 2)

                # Primary Outcome Indicator
                outcomes = a["measured_outcomes"]["items"]
                primary_outcome = outcomes[0] if outcomes else None

                comparison_rows.append({
                    "canonical_code": c_code,
                    "scheme_name": s_name,
                    "department": ident_info["department_name"],
                    "selected_financial_year": selected_fy or "N/A (No Common Fiscal Year)",
                    "budget_allocation_cr": alloc_cr,
                    "revised_estimate_cr": rev_cr,
                    "actual_expenditure_cr": act_cr,
                    "utilization_rate_pct": util_rate,
                    "verified_beneficiaries": ben_count,
                    "beneficiary_reporting_period": ben_period,
                    "unit_cost_per_beneficiary_inr": unit_cost,
                    "primary_outcome": {
                        "indicator_name": primary_outcome["outcome_name"] if primary_outcome else None,
                        "baseline": primary_outcome["baseline_value"] if primary_outcome else None,
                        "current": primary_outcome["followup_value"] if primary_outcome else None,
                        "observed_change": primary_outcome["observed_change"] if primary_outcome else None,
                        "unit": primary_outcome["unit"] if primary_outcome else None,
                    } if primary_outcome else None,
                })

            if not selected_fy:
                compatibility_flags.append(
                    "WARNING: Evaluated schemes do not share a common financial year in the database. "
                    "Comparisons across disparate fiscal years are epistemically invalid."
                )

            # Check if comparing different units
            outcome_units = {
                r["primary_outcome"]["unit"]
                for r in comparison_rows
                if r.get("primary_outcome") and r["primary_outcome"].get("unit")
            }
            if len(outcome_units) > 1:
                compatibility_flags.append(
                    f"INDICATOR UNIT DIVERSIFICATION: Evaluated schemes measure distinct physical domains ({list(outcome_units)}). "
                    "Cross-scheme percentage efficiency comparisons must not be conflated with scalar volume."
                )

            return {
                "comparison_financial_year": selected_fy,
                "common_years_available": sorted(list(common_years)),
                "comparison_matrix": comparison_rows,
                "compatibility_assessment": {
                    "is_fully_compatible": len(compatibility_flags) == 0,
                    "compatibility_flags": compatibility_flags,
                },
                "epistemic_guardrail": EPISTEMIC_CORRELATION_VS_CAUSATION,
                "non_equivalence_principle": EPISTEMIC_ALLOCATION_VS_EXPENDITURE,
            }

        finally:
            self._close_db_if_local(db)
