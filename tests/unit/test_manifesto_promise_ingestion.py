"""
CIVICLENS TN — Manifesto and Promise Ingestion Test Suite
=========================================================
Tests for source attribution, verbatim language preservation (Tamil/English),
derived content labelling, measurable target tracking, review status flagging,
epistemic non-causal separation, and referential integrity.
"""

import re
import json
import unittest
from backend.database.session import SessionLocal
from backend.models.manifesto import ManifestoSource, ManifestoDocument, Manifesto
from backend.models.promise import (
    PoliticalPromise,
    PromiseCategory,
    PromiseCategoryMapping,
    PromiseSchemeLink,
    PromiseAssessment
)
from backend.models.budget import HistoricalScheme
from backend.ingestion.manifesto_promise_ingestor import (
    ManifestoPromiseIngestor,
    run_manifesto_promise_ingestion
)


class TestManifestoPromiseIngestion(unittest.TestCase):
    """Validation test suite for sourced manifesto and promise ingestion."""

    @classmethod
    def setUpClass(cls):
        # Run canonical ingestion
        cls.metrics = run_manifesto_promise_ingestion()

    def setUp(self):
        self.db = SessionLocal()

    def tearDown(self):
        self.db.close()

    def test_database_record_counts(self):
        """Verify non-zero verified record counts matching raw/processed corpus."""
        promises_count = self.db.query(PoliticalPromise).filter(PoliticalPromise.is_test_fixture == False).count()
        manifestos_count = self.db.query(Manifesto).count()
        documents_count = self.db.query(ManifestoDocument).count()
        sources_count = self.db.query(ManifestoSource).count()
        categories_count = self.db.query(PromiseCategory).count()
        category_mappings_count = self.db.query(PromiseCategoryMapping).count()

        self.assertEqual(promises_count, 1065, "Total political promises must match source dataset count (1065)")
        self.assertGreaterEqual(manifestos_count, 19, "Must contain at least 19 manifesto records")
        self.assertGreaterEqual(documents_count, 20, "Must contain at least 20 manifesto documents")
        self.assertGreaterEqual(sources_count, 20, "Must contain at least 20 manifesto sources")
        self.assertGreaterEqual(categories_count, 17, "Must contain at least 17 promise categories")
        self.assertGreaterEqual(category_mappings_count, 1065, "Every promise must map to at least one category")

    def test_tamil_text_preservation(self):
        """Requirement 3: Preserve original promise text and language (Tamil script)."""
        tamil_promises = self.db.query(PoliticalPromise).filter(
            PoliticalPromise.language == "Tamil",
            PoliticalPromise.is_test_fixture == False
        ).all()

        self.assertGreater(len(tamil_promises), 300, "Should contain >300 Tamil promises from 2021/2026 manifestos")

        tamil_unicode_pattern = re.compile(r'[\u0B80-\u0BFF]')
        for p in tamil_promises[:20]:
            self.assertTrue(
                bool(tamil_unicode_pattern.search(p.original_text)),
                f"Promise {p.promise_id} marked as Tamil must contain native Tamil characters in original_text"
            )
            # Ensure text is not an empty paraphrase
            self.assertGreater(len(p.original_text.strip()), 5)

    def test_english_text_preservation(self):
        """Requirement 3: Preserve original promise text in English."""
        english_promises = self.db.query(PoliticalPromise).filter(
            PoliticalPromise.language == "English",
            PoliticalPromise.is_test_fixture == False
        ).all()

        self.assertGreater(len(english_promises), 600, "Should contain >600 English promises")
        for p in english_promises[:20]:
            self.assertGreater(len(p.original_text.strip()), 5)
            self.assertIsNotNone(p.normalized_text)

    def test_derived_content_labeling(self):
        """Requirement 3: Any translation, summary, category, or target must be labeled as derived."""
        promises = self.db.query(PoliticalPromise).filter(PoliticalPromise.is_test_fixture == False).limit(50).all()
        for p in promises:
            meta = p.metadata_json or {}
            self.assertIn(
                "derived_content",
                meta,
                f"Promise {p.promise_id} must have an explicit 'derived_content' dictionary"
            )
            derived = meta["derived_content"]
            self.assertIn("normalized_text", derived)
            self.assertIn("classification", derived)
            self.assertIn("derived_category", derived)
            self.assertIn("extracted_targets", derived)

    def test_epistemic_separation_and_non_causality(self):
        """Requirement 5 & 6: Distinguish promise from policy/budget/outcome; no causal inference."""
        promises = self.db.query(PoliticalPromise).filter(PoliticalPromise.is_test_fixture == False).limit(50).all()
        for p in promises:
            meta = p.metadata_json or {}
            self.assertIn(
                "epistemic_guardrails",
                meta,
                f"Promise {p.promise_id} must declare epistemic_guardrails"
            )
            guardrails = meta["epistemic_guardrails"]
            self.assertEqual(guardrails.get("record_type"), "STATED_ELECTION_PROMISE")
            self.assertFalse(
                guardrails.get("fulfillment_inferred_from_scheme"),
                "Promise must never infer fulfillment solely from scheme matching"
            )
            self.assertFalse(
                guardrails.get("fulfillment_inferred_from_budget"),
                "Promise must never infer fulfillment solely from budget allocation"
            )

    def test_scheme_links_non_causal_disclaimer(self):
        """Requirement 6: Scheme links must carry continuous similarity and non-causal disclaimer."""
        links = self.db.query(PromiseSchemeLink).all()
        self.assertGreater(len(links), 0, "Should have seeded promise-to-scheme matches")

        for link in links:
            self.assertGreaterEqual(link.similarity_score, 0.0)
            self.assertLessEqual(link.similarity_score, 1.0)
            self.assertIsNotNone(link.notes)
            self.assertIn(
                "NON-CAUSAL",
                link.notes,
                f"Scheme link {link.id} must explicitly note non-causal relationship"
            )

    def test_measurable_targets_tracking(self):
        """Requirement 4: Track measurable targets, deadlines, departments only when present."""
        # Find promises that have specific extracted numeric/monetary targets
        targeted_promises = []
        all_promises = self.db.query(PoliticalPromise).filter(PoliticalPromise.is_test_fixture == False).all()
        for p in all_promises:
            meta = p.metadata_json or {}
            targets = meta.get("derived_content", {}).get("extracted_targets", {})
            if targets:
                targeted_promises.append((p, targets))

        self.assertGreater(
            len(targeted_promises),
            0,
            "At least some promises must track extracted targets (e.g. monetary_target, numeric_target)"
        )
        for p, targets in targeted_promises[:10]:
            # Each key in targets must be a recognized dimension
            valid_keys = {"numeric_target", "monetary_target", "time_horizon", "target_population", "responsible_department", "geography"}
            for k in targets:
                self.assertIn(k, valid_keys, f"Extracted target key {k} is invalid")

    def test_review_status_flagging(self):
        """Requirement 8: Provide review status for uncertain OCR, low confidence, or duplicates."""
        ambiguous_promises = self.db.query(PoliticalPromise).filter(
            PoliticalPromise.is_ambiguous == True,
            PoliticalPromise.is_test_fixture == False
        ).all()

        self.assertGreater(len(ambiguous_promises), 0, "Must flag ambiguous or needs_review promises")

        for p in ambiguous_promises[:20]:
            meta = p.metadata_json or {}
            v_status = meta.get("validation_status")
            v_score = meta.get("validation_score", 1.0)
            is_flagged = (
                v_status in ["needs_review", "probable_duplicate"]
                or v_score < 0.85
                or p.classification == "ambiguous"
                or bool(meta.get("validation_flags"))
            )
            self.assertTrue(
                is_flagged,
                f"Promise {p.promise_id} marked is_ambiguous must have an underlying review flag"
            )

    def test_referential_integrity(self):
        """Requirement 9: Reuse existing schema and ensure foreign key lineage."""
        for p in self.db.query(PoliticalPromise).filter(PoliticalPromise.is_test_fixture == False).limit(30):
            # Check promise -> manifesto
            manifesto = p.manifesto
            self.assertIsNotNone(manifesto, f"Promise {p.promise_id} must have a valid manifesto")

            # Check manifesto -> document
            doc = manifesto.document
            self.assertIsNotNone(doc, f"Manifesto {manifesto.manifesto_id} must have a valid document")

            # Check manifesto -> source
            source = manifesto.source
            self.assertIsNotNone(source, f"Manifesto {manifesto.manifesto_id} must have a valid source")

        for m in self.db.query(PromiseCategoryMapping).limit(30):
            cat = self.db.query(PromiseCategory).filter(PromiseCategory.id == m.category_id).first()
            self.assertIsNotNone(cat, f"Mapping category_id {m.category_id} must exist in promise_categories")

    def test_idempotent_ingestion(self):
        """Verify re-running ingestion does not duplicate rows or corrupt database."""
        initial_count = self.db.query(PoliticalPromise).count()
        run_manifesto_promise_ingestion()
        new_count = self.db.query(PoliticalPromise).count()
        self.assertEqual(initial_count, new_count, "Idempotent run must not change total promise count")


if __name__ == "__main__":
    unittest.main()
