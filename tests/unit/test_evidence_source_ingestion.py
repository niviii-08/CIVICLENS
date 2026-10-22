"""
Unit Tests for Source and Evidence Ingestion Pipeline
=====================================================
Validates:
1. URL syntax, domain whitelisting, disabled registry entries, and robots.txt restrictions.
2. Missing provenance rejection (title, publisher, URL, document_type, source_tier).
3. Cryptographic deduplication and duplicate document detection via SHA-256 hashing.
4. Extraction failures and OCR uncertainty flagging (replacement chars, garbled text).
5. Source tier hierarchy: statutory/official vs secondary news vs unverified submissions.
6. Non-assumption principle: finding a source != claim truth.
7. Conflicting evidence preservation and epistemic verdict synthesis (supported, contradicted, mixed, misleading, unverifiable).
8. Zero fabrication of page numbers, citations, or quotations.
"""

import unittest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base_class import Base
from backend.models.claim import (
    EvidenceDocument,
    EvidencePassage,
    Claim,
    AtomicClaim,
    ClaimEvidenceRelationship,
    VerificationResult,
    SourceTier,
    EvidenceRelationshipType,
    VerificationOutcome,
    VerificationVerdict,
    ClaimCategory,
    ClaimStatus,
    AttributionType,
    CandidateSourceType
)
from backend.acquisition.claim_evidence_scraper import (
    DEFAULT_PERMITTED_SOURCES,
    SourceRegistryEntry
)
from backend.ingestion.verified_evidence_ingestor import (
    VerifiedEvidenceIngestor,
    CANONICAL_VERIFIED_DOCUMENTS
)


class TestEvidenceSourceIngestion(unittest.TestCase):

    def setUp(self):
        """Creates an isolated in-memory SQLite database for unit tests."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.db = Session()
        self.ingestor = VerifiedEvidenceIngestor(db_session=self.db)

    def tearDown(self):
        self.db.close()
        Base.metadata.drop_all(self.engine)

    def test_01_invalid_url_handling(self):
        """
        Verify validation rejects empty, malformed, non-whitelisted, and robots-restricted URLs.
        """
        # Empty URL
        res_empty = self.ingestor.validate_source_url("")
        self.assertFalse(res_empty["is_valid"])
        self.assertEqual(res_empty["error_code"], "MISSING_URL")

        # Invalid Scheme
        res_scheme = self.ingestor.validate_source_url("ftp://tn.gov.in/doc.pdf")
        self.assertFalse(res_scheme["is_valid"])
        self.assertEqual(res_scheme["error_code"], "INVALID_SCHEME")

        # Malformed Domain
        res_domain = self.ingestor.validate_source_url("https:///no-domain.pdf")
        self.assertFalse(res_domain["is_valid"])
        self.assertEqual(res_domain["error_code"], "INVALID_DOMAIN")

        # Non-Whitelisted Domain
        res_untrusted = self.ingestor.validate_source_url("https://unverified-political-blog.net/post/123")
        self.assertFalse(res_untrusted["is_valid"])
        self.assertEqual(res_untrusted["error_code"], "DOMAIN_NOT_WHITELISTED")

        # Robots.txt Denied Path
        res_robots = self.ingestor.validate_source_url("https://pib.gov.in/admin/secret.pdf")
        self.assertFalse(res_robots["is_valid"])
        self.assertEqual(res_robots["error_code"], "ROBOTS_DENIED")

        # Valid Whitelisted URL
        res_valid = self.ingestor.validate_source_url("https://tn.gov.in/documents/go_ms_34.pdf")
        self.assertTrue(res_valid["is_valid"])
        self.assertEqual(res_valid["domain"], "tn.gov.in")
        self.assertEqual(res_valid["source_tier"], SourceTier.TIER_1_STATUTORY)

    def test_02_missing_provenance_validation(self):
        """
        Verify that documents lacking required provenance fields are rejected with clear error codes.
        """
        # Missing Title
        doc_no_title = {
            "document_id": "TEST-NO-TITLE",
            "publisher": "Govt of TN",
            "source_url": "https://tn.gov.in/doc1.pdf",
            "document_type": "GOVERNMENT_ORDER",
            "source_tier": SourceTier.TIER_1_STATUTORY
        }
        res_title = self.ingestor.ingest_document(doc_no_title)
        self.assertEqual(res_title["status"], "REJECTED_MISSING_PROVENANCE")
        self.assertIn("title", res_title["missing_fields"])

        # Missing Publisher
        doc_no_pub = {
            "document_id": "TEST-NO-PUB",
            "title": "Scheme Order",
            "source_url": "https://tn.gov.in/doc2.pdf",
            "document_type": "GOVERNMENT_ORDER",
            "source_tier": SourceTier.TIER_1_STATUTORY
        }
        res_pub = self.ingestor.ingest_document(doc_no_pub)
        self.assertEqual(res_pub["status"], "REJECTED_MISSING_PROVENANCE")
        self.assertIn("publisher", res_pub["missing_fields"])

        # Missing URL
        doc_no_url = {
            "document_id": "TEST-NO-URL",
            "title": "Scheme Order",
            "publisher": "Govt of TN",
            "document_type": "GOVERNMENT_ORDER",
            "source_tier": SourceTier.TIER_1_STATUTORY
        }
        res_url = self.ingestor.ingest_document(doc_no_url)
        self.assertEqual(res_url["status"], "REJECTED_INVALID_URL")

    def test_03_cryptographic_deduplication(self):
        """
        Verify that ingesting duplicate documents is detected via SHA-256 hashing and avoided.
        """
        sample_doc = {
            "document_id": "DOC-SAMPLE-01",
            "title": "Tamil Nadu Sanitation Policy Note",
            "publisher": "Municipal Administration Department",
            "source_url": "https://tn.gov.in/sanitation_policy.pdf",
            "document_type": "POLICY_NOTE",
            "source_category": "OFFICIAL_GOVERNMENT",
            "source_tier": SourceTier.TIER_2_OFFICIAL_AGENCY,
            "publication_date": "2023-04-01T00:00:00Z",
            "passages": [
                {
                    "passage_id": "PASS-SAMP-1",
                    "page_number": 5,
                    "section_or_table": "Section 2",
                    "passage_text": "Sanitation infrastructure allocations reached Rs. 1,200 crore."
                }
            ]
        }

        # First ingestion
        res1 = self.ingestor.ingest_document(sample_doc)
        self.assertEqual(res1["status"], "SUCCESS")
        self.assertIn("file_hash", res1)

        # Ingest exact duplicate with same ID and content
        res2 = self.ingestor.ingest_document(sample_doc)
        self.assertEqual(res2["status"], "DUPLICATE_DOCUMENT")
        self.assertEqual(res2["document_id"], "DOC-SAMPLE-01")

        # Verify database only contains 1 document record
        count = self.db.query(EvidenceDocument).filter(EvidenceDocument.document_id == "DOC-SAMPLE-01").count()
        self.assertEqual(count, 1)

    def test_04_extraction_quality_and_ocr_uncertainty(self):
        """
        Verify that degraded, noisy, or machine-extracted text is flagged as uncertain
        and requires human review before being used in verification.
        """
        # Clean text
        clean_text = "The Government of Tamil Nadu sanctioned Rs. 698 crore for higher education scholarships."
        clean_eval = self.ingestor.evaluate_extraction_quality(clean_text)
        self.assertFalse(clean_eval["is_uncertain_extraction"])
        self.assertFalse(clean_eval["requires_human_review"])
        self.assertGreaterEqual(clean_eval["ocr_confidence"], 0.90)

        # Degraded OCR text with unicode replacement characters
        ocr_degraded_text = "The G\ufffdvernm\ufffdnt of T\ufffdmil Nadu s\ufffdnctioned Rs. 698 cr\ufffdr\ufffde."
        degraded_eval = self.ingestor.evaluate_extraction_quality(ocr_degraded_text)
        self.assertTrue(degraded_eval["is_uncertain_extraction"])
        self.assertTrue(degraded_eval["requires_human_review"])
        self.assertLess(degraded_eval["ocr_confidence"], 0.85)
        self.assertTrue(any("UNICODE_REPLACEMENT" in s for s in degraded_eval["degradation_signals"]))

        # Garbled token noise
        garbled_text = "Sch00l educ_4t1on d3p4rtment allo_c4t1on for primary cl4ss3s."
        garbled_eval = self.ingestor.evaluate_extraction_quality(garbled_text)
        self.assertTrue(garbled_eval["is_uncertain_extraction"])
        self.assertTrue(garbled_eval["requires_human_review"])

        # Empty text
        empty_eval = self.ingestor.evaluate_extraction_quality("")
        self.assertTrue(empty_eval["is_uncertain_extraction"])
        self.assertEqual(empty_eval["ocr_confidence"], 0.0)

    def test_05_source_tier_distinction(self):
        """
        Verify distinction between statutory/constitutional primary sources, secondary news,
        and unverified citizen submissions.
        """
        # Statutory Government Order
        doc_statutory = {
            "document_id": "DOC-TIER-1",
            "title": "Government Order Ms 101",
            "publisher": "Finance Department TN",
            "source_url": "https://tn.gov.in/go101.pdf",
            "document_type": "GOVERNMENT_ORDER",
            "source_tier": SourceTier.TIER_1_STATUTORY,
            "passages": [{"passage_text": "Sanction order text."}]
        }
        res_stat = self.ingestor.ingest_document(doc_statutory)
        self.assertEqual(res_stat["status"], "SUCCESS")

        doc_rec1 = self.db.query(EvidenceDocument).filter_by(document_id="DOC-TIER-1").first()
        self.assertTrue(doc_rec1.is_official)
        self.assertEqual(doc_rec1.source_tier, SourceTier.TIER_1_STATUTORY)

        # Secondary News Publication
        doc_news = {
            "document_id": "DOC-TIER-4",
            "title": "News Article on Scheme",
            "publisher": "The Hindu",
            "source_url": "https://thehindu.com/article123.html",
            "document_type": "NEWS_REPORT",
            "source_tier": SourceTier.TIER_4_SECONDARY_CIVIC,
            "passages": [{"passage_text": "News summary paragraph."}]
        }
        res_news = self.ingestor.ingest_document(doc_news)
        self.assertEqual(res_news["status"], "SUCCESS")

        doc_rec2 = self.db.query(EvidenceDocument).filter_by(document_id="DOC-TIER-4").first()
        self.assertFalse(doc_rec2.is_official)
        self.assertEqual(doc_rec2.source_tier, SourceTier.TIER_4_SECONDARY_CIVIC)

    def test_06_non_assumption_source_found_does_not_mean_claim_is_true(self):
        """
        Verify that merely indexing or finding a source document does NOT label a claim true.
        Verification evaluates whether the passage supports or contradicts the proposition.
        """
        # Ingest canonical primary sources
        self.ingestor.ingest_canonical_corpus()

        # Create a claim asserting a false expenditure figure
        claim = Claim(
            claim_id="CLM-TEST-NON-ASSUMPTION",
            original_text="Government allocated Rs. 50,000 crore for Pudhumai Penn scheme.",
            normalized_text="Government allocated Rs. 50000 crore for Pudhumai Penn scheme.",
            claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
            attribution_type=AttributionType.DIRECT_QUOTE,
            candidate_source_type=CandidateSourceType.PUBLIC_SPEECH,
            status=ClaimStatus.PENDING
        )
        self.db.add(claim)
        self.db.commit()

        # Link to Pudhumai Penn G.O. passage which specifies Rs. 698 crore (contradicting the 50,000 Cr claim)
        rel = self.ingestor.link_passage_to_claim(
            claim_id="CLM-TEST-NON-ASSUMPTION",
            passage_id="PASS-GO-34-P1",
            relationship_type=EvidenceRelationshipType.CONTRADICTS,
            contradicting_reference="G.O. Ms 34 specifies Rs. 698.00 crore financial sanction, directly contradicting Rs. 50,000 crore assertion."
        )

        # Verify outcome synthesis
        synthesis = self.ingestor.verify_claim("CLM-TEST-NON-ASSUMPTION")
        self.assertEqual(synthesis["outcome"], VerificationOutcome.CONTRADICTED_BY_AVAILABLE_EVIDENCE)
        self.assertIn("contradicted", synthesis["explanation"].lower())

    def test_07_conflicting_sources_preservation(self):
        """
        Verify that when a Department report and an Audit report conflict, both records
        are retained transparently and the claim is classified as DISPUTED_EVIDENCE (mixed).
        """
        # Ingest canonical sources including Department G.O. (Ms) 89 and CAG Audit Report 2 of 2025
        self.ingestor.ingest_canonical_corpus()

        # Create KMUT beneficiary claim
        claim = Claim(
            claim_id="CLM-KMUT-BENEFICIARIES",
            original_text="1.15 crore women heads of households receive Rs. 1,000 monthly under KMUT.",
            normalized_text="1.15 crore women heads receive Rs 1000 under KMUT",
            claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
            attribution_type=AttributionType.DIRECT_QUOTE,
            candidate_source_type=CandidateSourceType.OFFICIAL_STATEMENT,
            status=ClaimStatus.PENDING
        )
        self.db.add(claim)
        self.db.commit()

        # 1. Department G.O. / Policy Note passage supports the 1.15 crore rollout
        self.ingestor.link_passage_to_claim(
            claim_id="CLM-KMUT-BENEFICIARIES",
            passage_id="PASS-GO-89-P1",
            relationship_type=EvidenceRelationshipType.SUPPORTS,
            supporting_reference="G.O. Ms 89 sanctions monthly DBT of Rs. 1,000 for adult female heads."
        )

        # 2. CAG Audit report passage contradicts full eligibility (512,000 flagged for reverification)
        self.ingestor.link_passage_to_claim(
            claim_id="CLM-KMUT-BENEFICIARIES",
            passage_id="PASS-CAG-2025-P42",
            relationship_type=EvidenceRelationshipType.CONTRADICTS,
            contradicting_reference="CAG Performance Audit Report 2 of 2025 field audit flagged 512,000 accounts for reverification due to statutory ceiling exceedance."
        )

        # Verify outcome synthesis detects conflict
        synthesis = self.ingestor.verify_claim("CLM-KMUT-BENEFICIARIES")
        self.assertEqual(synthesis["outcome"], VerificationOutcome.DISPUTED_EVIDENCE)
        self.assertIn("Direct conflict between available authoritative sources", synthesis["explanation"])
        self.assertEqual(synthesis["source_diversity"]["total_relevant_passages"], 2)

    def test_08_page_and_section_provenance_preservation(self):
        """
        Verify that page numbers, sections, and table references are stored accurately
        without hallucination or fabrication.
        """
        self.ingestor.ingest_canonical_corpus()

        # Check CAG Audit passage
        cag_pass = self.db.query(EvidencePassage).filter_by(passage_id="PASS-CAG-2025-P42").first()
        self.assertIsNotNone(cag_pass)
        self.assertEqual(cag_pass.page_number, 42)
        self.assertEqual(cag_pass.section_or_table, "Table 3.4: KMUT Field Sample Scrutiny")
        self.assertIn("3.2% accounts", cag_pass.passage_text)

        # Check AISHE passage
        aishe_pass = self.db.query(EvidencePassage).filter_by(passage_id="PASS-AISHE-P18").first()
        self.assertIsNotNone(aishe_pass)
        self.assertEqual(aishe_pass.page_number, 18)
        self.assertEqual(aishe_pass.section_or_table, "Table 2.1: Gross Enrollment Ratio in Tamil Nadu")


if __name__ == "__main__":
    unittest.main()
