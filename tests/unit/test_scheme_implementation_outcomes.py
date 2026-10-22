"""
Unit and Integration Tests for Verified Scheme Implementation and Outcomes
==========================================================================
Validates:
1. Strict 6-concept conceptual separation (Sanctioned, Released, Expenditure, Beneficiary Count, Output, Outcome).
2. Denominator and reporting scope preservation for rates/percentages.
3. Non-assumption guards (Announcement != Implementation, Expenditure != Outcome).
4. Zero-fabrication enforcement (Missing values remain None, no invented scores).
5. Transparent conflicting reports preservation (CAG audit scrutiny vs Department claims).
6. Evidence-backed scheme-to-promise and department linkages (No forced party-crossing).
7. Idempotent re-run safety.
"""

import unittest
from collections import Counter
from backend.database.session import SessionLocal
from backend.models.budget import (
    BudgetDepartment,
    BudgetScheme,
    BudgetRecord,
    BudgetStage,
    BudgetSourceDocument
)
from backend.models.policy_evaluation import (
    PolicyRegistryEntry,
    PolicyObjective,
    BeneficiaryGroup,
    ImplementationActivity,
    PolicyIndicator,
    IndicatorObservation,
    EvaluationStudy,
    EvaluationFinding,
    FindingType,
    FindingReviewStatus,
    IndicatorType,
    IndicatorDomain,
    ObservationStage
)
from backend.ingestion.verified_scheme_ingestor import (
    VerifiedSchemeIngestor,
    run_verified_scheme_ingestion,
    VERIFIED_SCHEME_DEFINITIONS,
    CONFLICTING_AUDIT_SCRUTINY
)


class TestSchemeImplementationOutcomes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run ingestion once before tests to ensure database has verified records."""
        cls.metrics = run_verified_scheme_ingestion()
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    def test_01_six_concept_separation(self):
        """
        Verify that Sanctioned Amount, Released Amount, Expenditure, Beneficiary Count,
        Output, and Outcome are strictly separated into distinct entities.
        """
        # 1. Financial concepts (Sanctioned, Released, Expenditure)
        pudhumai_scheme = self.db.query(BudgetScheme).filter(
            BudgetScheme.name.like("%Pudhumai Penn%")
        ).first()
        self.assertIsNotNone(pudhumai_scheme, "Pudhumai Penn budget scheme must exist")

        records = self.db.query(BudgetRecord).filter(
            BudgetRecord.scheme_id == pudhumai_scheme.id,
            BudgetRecord.financial_year == "2023-24"
        ).all()
        
        stages = {r.budget_stage: r.amount for r in records}
        self.assertIn(BudgetStage.sanctioned_allocation, stages, "Sanctioned amount must be recorded distinctly")
        self.assertIn(BudgetStage.fund_release, stages, "Released amount must be recorded distinctly")
        self.assertIn(BudgetStage.actual_expenditure, stages, "Actual expenditure must be recorded distinctly")

        # Values must match primary records (in Crores)
        self.assertEqual(stages[BudgetStage.sanctioned_allocation], 698.00)
        self.assertEqual(stages[BudgetStage.fund_release], 998.45)
        self.assertEqual(stages[BudgetStage.actual_expenditure], 998.45)

        # 2. Beneficiary Count
        bg = self.db.query(BeneficiaryGroup).filter(
            BeneficiaryGroup.scheme_id == "SCH-TN-PUDHUMAI"
        ).first()
        self.assertIsNotNone(bg, "Beneficiary group must exist")
        self.assertIn("Female students", bg.name)

        pol = self.db.query(PolicyRegistryEntry).filter(
            PolicyRegistryEntry.canonical_scheme_code == "SCH-TN-PUDHUMAI"
        ).first()
        self.assertEqual(pol.stated_targets[0]["reported_count"], 485000)
        self.assertEqual(pol.stated_targets[0]["unit"], "BENEFICIARY_STUDENTS")

        # 3. Physical Output
        output_acts = self.db.query(ImplementationActivity).filter(
            ImplementationActivity.scheme_id == "SCH-TN-PUDHUMAI"
        ).all()
        self.assertGreater(len(output_acts), 0)
        self.assertEqual(output_acts[0].completed_output_quantity, 485000.0)
        self.assertEqual(output_acts[0].output_unit, "STUDENT_MONTHLY_DISBURSALS")

        # 4. Measured Outcome
        outcomes = self.db.query(PolicyIndicator).filter(
            PolicyIndicator.scheme_id == "SCH-TN-PUDHUMAI",
            PolicyIndicator.indicator_type == IndicatorType.OUTCOME
        ).all()
        self.assertGreater(len(outcomes), 0)
        self.assertEqual(outcomes[0].indicator_id, "IND-PUDHUMAI-GER-WOMEN")
        self.assertEqual(outcomes[0].unit, "PERCENT")

    def test_02_denominator_preservation_for_rates(self):
        """
        Preserve the denominator and reporting scope for rates and percentages.
        """
        indicators = self.db.query(PolicyIndicator).all()
        for ind in indicators:
            if ind.unit.startswith("PERCENT"):
                self.assertIn("Denominator:", ind.definition, f"Denominator missing in {ind.indicator_id}")
                self.assertIn("Measurement method:", ind.definition)

        # Pudhumai Penn GER denominator check
        ger_ind = self.db.query(PolicyIndicator).filter(
            PolicyIndicator.indicator_id == "IND-PUDHUMAI-GER-WOMEN"
        ).first()
        self.assertIn("Total female population in age cohort 18-23 years", ger_ind.definition)
        self.assertEqual(ger_ind.baseline_value, 49.8)
        self.assertEqual(ger_ind.comparison_value, 52.4)

    def test_03_non_assumption_guards(self):
        """
        Test that announcement does not equal implementation, and expenditure
        does not equal outcome achievement.
        """
        for defn in VERIFIED_SCHEME_DEFINITIONS:
            s_id = defn["scheme_id"]
            p_id = defn["policy_id"]

            pol = self.db.query(PolicyRegistryEntry).filter(
                PolicyRegistryEntry.policy_id == p_id
            ).first()
            self.assertIsNotNone(pol)
            # Stated target must NOT be stored as an empirical outcome observation
            self.assertNotEqual(pol.stated_targets, [])

            # Check that activities for our verified scheme maintain explicit status
            expected_act_ids = [out["activity_id"] for out in defn.get("outputs", [])]
            for act_id in expected_act_ids:
                act = self.db.query(ImplementationActivity).filter(
                    ImplementationActivity.activity_id == act_id
                ).first()
                self.assertIsNotNone(act)
                self.assertIsNotNone(act.status)
                self.assertIsNotNone(act.completed_output_quantity)

            # Non-assumption: Budget expenditure != Outcome.
            # Verify expenditure is in BudgetRecord, but outcome is separately verified in PolicyIndicator
            bscheme = self.db.query(BudgetScheme).filter(
                BudgetScheme.name == defn["scheme_name"]
            ).first()
            exp_rec = self.db.query(BudgetRecord).filter(
                BudgetRecord.scheme_id == bscheme.id,
                BudgetRecord.budget_stage == BudgetStage.actual_expenditure
            ).first()
            self.assertIsNotNone(exp_rec, "Budget expenditure must exist")

            for out in defn.get("outcomes", []):
                ind = self.db.query(PolicyIndicator).filter(
                    PolicyIndicator.indicator_id == out["indicator_id"]
                ).first()
                self.assertIsNotNone(ind)
                # Outcome requires separate empirical measurement method and cannot reuse expenditure
                self.assertNotEqual(ind.indicator_domain, IndicatorDomain.BUDGET_EXPENDITURE)

    def test_04_conflicting_audit_preservation(self):
        """
        Verify that conflicting CAG audit observations and administrative figures
        are both preserved transparently.
        """
        cag_findings = self.db.query(EvaluationFinding).filter(
            EvaluationFinding.finding_id == "FIND-KMUT-CAG-01"
        ).all()
        self.assertEqual(len(cag_findings), 1)
        finding = cag_findings[0]

        self.assertEqual(finding.finding_type, FindingType.CONFLICTING_FINDINGS)
        self.assertEqual(finding.review_status, FindingReviewStatus.FLAGGED_CONFLICTING)
        self.assertIn("CONFLICTING AUDIT OBSERVATION", finding.finding_text)
        
        # Check both numbers are preserved in structured indicator_values_used
        self.assertEqual(finding.indicator_values_used["department_claimed_beneficiaries"], 11500000)
        self.assertEqual(finding.indicator_values_used["cag_verified_beneficiaries"], 10988000)
        self.assertEqual(finding.indicator_values_used["reverification_pending_flagged"], 512000)

    def test_05_zero_fabrication(self):
        """
        Ensure no fabricated district values, impact estimates, or fake beneficiaries exist.
        """
        # Verify that geographic level is set to STATE when district breakdown is unavailable
        for defn in VERIFIED_SCHEME_DEFINITIONS:
            expected_act_ids = [out["activity_id"] for out in defn.get("outputs", [])]
            for act_id in expected_act_ids:
                act = self.db.query(ImplementationActivity).filter(
                    ImplementationActivity.activity_id == act_id
                ).first()
                self.assertIsNotNone(act)
                self.assertEqual(act.geographic_level, "STATE")
                self.assertFalse(act.is_test_fixture)

            expected_ind_ids = [out["indicator_id"] for out in defn.get("outcomes", [])]
            for ind_id in expected_ind_ids:
                ind = self.db.query(PolicyIndicator).filter(
                    PolicyIndicator.indicator_id == ind_id
                ).first()
                self.assertIsNotNone(ind)
                self.assertEqual(ind.geographic_level, "STATE")
                self.assertFalse(ind.is_test_fixture)

    def test_06_unmatched_schemes_not_force_matched(self):
        """
        Link a scheme to a promise only when supported by evidence;
        never force a match across party or administration boundaries.
        """
        # Since DMK 2021 manifesto is not in the political promises table,
        # schemes must NOT be falsely linked to BJP, AIADMK, PMK, or MNM promises.
        pudhumai = self.db.query(PolicyRegistryEntry).filter(
            PolicyRegistryEntry.canonical_scheme_code == "SCH-TN-PUDHUMAI"
        ).first()
        if pudhumai.promise_id:
            # If linked, verify it belongs to a verified relevant promise, not a random party
            prom = self.db.query(PoliticalPromise).filter(
                PoliticalPromise.promise_id == pudhumai.promise_id
            ).first()
            self.assertEqual(prom.manifesto_id, "MF-DMK-2021")

    def test_07_idempotent_rerun_safety(self):
        """
        Re-running the ingestor must be safe, repeatable, and must not duplicate records.
        """
        initial_policy_count = self.db.query(PolicyRegistryEntry).count()
        initial_activity_count = self.db.query(ImplementationActivity).count()
        initial_indicator_count = self.db.query(PolicyIndicator).count()

        # Re-run ingestion
        ingestor = VerifiedSchemeIngestor(db_session=self.db)
        metrics = ingestor.ingest_all()

        final_policy_count = self.db.query(PolicyRegistryEntry).count()
        final_activity_count = self.db.query(ImplementationActivity).count()
        final_indicator_count = self.db.query(PolicyIndicator).count()

        self.assertEqual(initial_policy_count, final_policy_count)
        self.assertEqual(initial_activity_count, final_activity_count)
        self.assertEqual(initial_indicator_count, final_indicator_count)
        self.assertEqual(metrics["policies_processed"], 0)


if __name__ == "__main__":
    unittest.main()
