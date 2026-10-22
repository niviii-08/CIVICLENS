"""
CIVICLENS TN — Budget and Public Finance Ingestion Test Suite
============================================================
Validation tests for:
1. Strict separation of financial measures (BE, RE, AE, Releases, Allocations, Commitments).
2. Explicit tested unit transformations (Crores, Lakhs, Thousands, Absolute INR).
3. Preservation of missing/unreported values as None (never coerced to zero).
4. Validation against malformed financial years and missing provenance.
5. Incompatibility qualification between periods and accounting categories.
6. Sub-head to major-head reconciliation.
7. Non-causal epistemic boundary assertions.
8. Idempotent rerun safety.
"""

import unittest
from sqlalchemy.orm import Session
from backend.database.session import SessionLocal
from backend.models.budget import (
    BudgetRecord,
    BudgetStage,
    BudgetDepartment,
    BudgetScheme,
    BudgetSourceDocument,
    BudgetImportBatch
)
from backend.ingestion.budget_transform import (
    CurrencyUnit,
    convert_currency,
    normalize_unit_string,
    validate_financial_year,
    validate_comparability,
    reconcile_subhead_totals
)
from backend.ingestion.verified_budget_ingestor import (
    VerifiedBudgetIngestor,
    run_verified_budget_ingestion
)


class TestBudgetExpenditureIngestion(unittest.TestCase):
    """Test suite validating budget and expenditure ingestion rules."""

    @classmethod
    def setUpClass(cls):
        # Ingest verified budget data
        cls.metrics = run_verified_budget_ingestion()

    def setUp(self):
        self.db: Session = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_stage_separation(self):
        """Requirement 4: BE, RE, Actuals, Releases, Allocations, Commitments must remain strictly distinct."""
        records = self.db.query(BudgetRecord).all()
        stages_present = {r.budget_stage for r in records}

        # Verify multiple discrete stages are preserved in DB
        self.assertIn(BudgetStage.budget_estimate, stages_present)
        self.assertIn(BudgetStage.revised_estimate, stages_present)
        self.assertIn(BudgetStage.actual_expenditure, stages_present)
        self.assertIn(BudgetStage.fund_release, stages_present)
        self.assertIn(BudgetStage.sanctioned_allocation, stages_present)
        self.assertIn(BudgetStage.commitment, stages_present)

        # Ensure no record combines stages into a generic bucket
        for r in records:
            self.assertIsInstance(r.budget_stage, BudgetStage)
            self.assertIn(r.budget_stage.value, [
                "budget_estimate",
                "revised_estimate",
                "actual_expenditure",
                "sanctioned_allocation",
                "fund_release",
                "commitment"
            ])

    def test_unit_conversions_crore_lakh_thousand_absolute(self):
        """Requirement 5: Explicit, tested transformations between currency units."""
        # 1 Crore = 100 Lakhs = 10,000 Thousands = 10,000,000 Absolute INR
        amt_cr = 15.5  # Rs 15.5 Crore

        # Crore to Lakh
        amt_lakh = convert_currency(amt_cr, "RUPEES_CRORE", "RUPEES_LAKH")
        self.assertEqual(amt_lakh, 1550.0)

        # Crore to Thousand
        amt_thousand = convert_currency(amt_cr, "RUPEES_CRORE", "RUPEES_THOUSAND")
        self.assertEqual(amt_thousand, 155000.0)

        # Crore to Absolute
        amt_abs = convert_currency(amt_cr, "RUPEES_CRORE", "RUPEES_ABSOLUTE")
        self.assertEqual(amt_abs, 155_000_000.0)

        # Reverse: Absolute to Crore
        self.assertEqual(convert_currency(155_000_000.0, "RUPEES_ABSOLUTE", "RUPEES_CRORE"), 15.5)

        # Reverse: Lakh to Crore
        self.assertEqual(convert_currency(1550.0, "RUPEES_LAKH", "RUPEES_CRORE"), 15.5)

        # Reverse: Thousand to Crore
        self.assertEqual(convert_currency(155000.0, "RUPEES_THOUSAND", "RUPEES_CRORE"), 15.5)

    def test_null_amounts_preserved_never_coerced_to_zero(self):
        """Requirement 6: Never treat missing, unavailable, or unreported values as zero."""
        null_records = self.db.query(BudgetRecord).filter(BudgetRecord.amount.is_(None)).all()
        self.assertGreater(len(null_records), 0, "Database must preserve records with unclosed actuals as None")

        for r in null_records:
            self.assertIsNone(r.amount, f"Record {r.id} must be None, not 0.0 or falsy float")
            self.assertNotEqual(r.amount, 0.0)

        # Unit conversion must also preserve None
        self.assertIsNone(convert_currency(None, "RUPEES_CRORE", "RUPEES_LAKH"))
        self.assertIsNone(convert_currency(None, "RUPEES_ABSOLUTE", "RUPEES_CRORE"))

    def test_financial_year_validation(self):
        """Requirement 9: Detect malformed financial years."""
        # Valid FY patterns
        self.assertTrue(validate_financial_year("2023-24"))
        self.assertTrue(validate_financial_year("2024-25"))
        self.assertTrue(validate_financial_year("2026-27"))
        self.assertTrue(validate_financial_year("1999-00"))

        # Malformed FY patterns
        self.assertFalse(validate_financial_year("2023"))           # Single calendar year
        self.assertFalse(validate_financial_year("2023-2024"))      # 4-digit end year
        self.assertFalse(validate_financial_year("2023/24"))        # Slash delimiter
        self.assertFalse(validate_financial_year("2023-25"))        # Non-consecutive year jump
        self.assertFalse(validate_financial_year("FY24"))           # Informal prefix
        self.assertFalse(validate_financial_year(""))               # Empty string
        self.assertFalse(validate_financial_year(None))             # None type

    def test_incompatible_accounting_category_comparability(self):
        """Requirement 7: Do not compare incompatible accounting categories without clear qualification."""
        # Valid cross-stage comparison under same category
        valid, reason = validate_comparability(
            stage_a="budget_estimate",
            stage_b="actual_expenditure",
            category_a="Revenue Expenditure",
            category_b="Revenue Expenditure"
        )
        self.assertTrue(valid)
        self.assertIsNone(reason)

        # Incompatible: Capital Outlay vs Revenue Expenditure
        invalid_cat, reason_cat = validate_comparability(
            stage_a="budget_estimate",
            stage_b="actual_expenditure",
            category_a="Capital Outlay",
            category_b="Revenue Expenditure"
        )
        self.assertFalse(invalid_cat)
        self.assertIn("Incompatible accounting categories", reason_cat)

        # Invalid: Comparing identical stage to itself
        invalid_stage, reason_stage = validate_comparability(
            stage_a="budget_estimate",
            stage_b="budget_estimate"
        )
        self.assertFalse(invalid_stage)
        self.assertIn("Cannot compare identical budget stages", reason_stage)

    def test_subhead_reconciliation(self):
        """Requirement 8: Reconcile sub-head line items against reported totals."""
        # Case 1: Perfectly balanced sub-heads
        subheads = [120.0, 30.5, 49.5]  # sum = 200.0
        reported = 200.0
        result = reconcile_subhead_totals(subheads, reported)
        self.assertTrue(result["is_balanced"])
        self.assertEqual(result["reconciliation_status"], "RECONCILED")
        self.assertEqual(result["variance"], 0.0)

        # Case 2: Discrepancy detected exceeding tolerance
        subheads_disc = [120.0, 30.0]  # sum = 150.0
        reported_disc = 175.0
        result_disc = reconcile_subhead_totals(subheads_disc, reported_disc)
        self.assertFalse(result_disc["is_balanced"])
        self.assertEqual(result_disc["reconciliation_status"], "DISCREPANCY_DETECTED")
        self.assertEqual(result_disc["variance"], -25.0)

        # Case 3: Preserving missing subheads without crashing
        subheads_with_none = [100.0, None, 50.0]
        result_none = reconcile_subhead_totals(subheads_with_none, 150.0)
        self.assertTrue(result_none["is_balanced"])
        self.assertEqual(result_none["subhead_count_missing"], 1)

    def test_non_causal_disclaimer_preservation(self):
        """Requirement 10: Do not claim spending caused an outcome; verify epistemic disclaimers."""
        records = self.db.query(BudgetRecord).filter(BudgetRecord.source_metadata.isnot(None)).all()
        self.assertGreater(len(records), 0)

        for r in records[:20]:
            meta = r.source_metadata
            self.assertIn("epistemic_disclaimer", meta)
            self.assertIn(
                "does NOT prove that a physical policy outcome was achieved",
                meta["epistemic_disclaimer"]
            )

    def test_provenance_fields_preservation(self):
        """Requirement 3: Preserve publication date, source URL, page number, and document reference."""
        records = self.db.query(BudgetRecord).limit(30).all()
        for r in records:
            self.assertIsNotNone(r.financial_year)
            self.assertIsNotNone(r.budget_stage)
            self.assertIsNotNone(r.currency_unit)
            self.assertIsNotNone(r.source_document)
            self.assertTrue(r.source_document.official_source_url.startswith("http"))
            self.assertTrue(len(r.source_document.title) > 5)

    def test_idempotent_ingestion(self):
        """Requirement 9: Repeatable imports and safe re-runs without duplicating records."""
        initial_count = self.db.query(BudgetRecord).count()
        run_verified_budget_ingestion()
        new_count = self.db.query(BudgetRecord).count()
        self.assertEqual(initial_count, new_count, "Re-running ingestion must not duplicate records")


if __name__ == "__main__":
    unittest.main()
