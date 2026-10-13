"""
Unit and Integration Tests for Phase 7.10 — Real Claim and Evidence Data Integration.

Verifies:
1. Integrity of preserved raw archive (SHA-256) and extracted datasets.
2. Ingestion of real official reference documents (Tier 1 statutory & official).
3. Ingestion of news articles as secondary evidence documents.
4. Registration of real political claims from legislative records, manifestos, and statements.
5. End-to-end trace: Claim -> NLP Atomic Decomposition -> Retrieval -> Relationship Analysis -> Verification Outcome.
6. Correct assignment of epistemic outcomes without political bias or personal character judgments.
7. Verification of REST API endpoints serving real integrated records.
8. Fallback and search behavior across integrated records in the dashboard registry.
"""

import os
import json
import pytest
from datetime import datetime, timezone
from backend.database.session import SessionLocal
from backend.models.claim import (
    Claim, AtomicClaim, EvidenceDocument, EvidencePassage,
    ClaimEvidenceRelationship, VerificationResult, VerificationOutcome,
    ClaimCategory, AttributionType, CandidateSourceType, SourceTier
)
from backend.services.claim_ingestion import ClaimIngestionService
from backend.nlp.claim_decomposition import MultilingualClaimPipeline
from backend.services.evidence_retrieval import EvidenceRetrievalEngine
from backend.services.evidence_relationship_analyzer import EvidenceRelationshipAnalyzer
from backend.services.claim_verification_engine import ClaimVerificationEngine
from backend.api.app import create_app


class TestPhase7RealDataIntegration:
    """Test suite verifying Phase 7.10 real dataset integration and validation."""

    @pytest.fixture(scope="class")
    def db_session(self):
        from scripts.import_phase7_real_data import run_real_ingestion
        db = SessionLocal()
        if db.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-001").count() == 0:
            db.close()
            run_real_ingestion()
            db = SessionLocal()
        yield db
        db.close()

    @pytest.fixture(scope="class")
    def api_client(self, db_session):
        app = create_app()
        app.config["TESTING"] = True
        return app.test_client()

    def test_1_raw_dataset_preservation_and_checksums(self):
        """Verify that real archive and extracted inventory exist with valid SHA-256."""
        raw_archive = "data/raw/phase7/dataset_7_and_8.zip"
        raw_inventory = "data/raw/phase7/raw_inventory.json"
        
        assert os.path.exists(raw_archive), "Raw archive data/raw/phase7/dataset_7_and_8.zip must exist."
        assert os.path.exists(raw_inventory), "Inventory data/raw/phase7/raw_inventory.json must exist."
        
        with open(raw_inventory, "r", encoding="utf-8") as f:
            inv = json.load(f)
        
        assert len(inv) > 0, "Inventory must contain extracted files."
        archive_entry = next((item for item in inv if item["filename"] == "dataset_7_and_8.zip"), None)
        assert archive_entry is not None
        assert archive_entry["sha256"] == "b87f17dbf825c8fdcf92b644f9f8d7e827c642507a13b41111c034d4e8b5f0e2"

    def test_2_official_evidence_documents_ingested(self, db_session):
        """Verify that 35 official reference documents are ingested with metadata and passages."""
        official_docs = db_session.query(EvidenceDocument).filter(
            EvidenceDocument.source_tier == SourceTier.TIER_1_STATUTORY
        ).all()
        assert len(official_docs) >= 35, f"Expected at least 35 official documents, found {len(official_docs)}"
        
        # Check specific key statutory references
        prs_doc = db_session.query(EvidenceDocument).filter(EvidenceDocument.document_id == "EVD-CL-D-0001").first()
        assert prs_doc is not None
        assert "PRS Legislative Research" in prs_doc.publisher
        assert "Tamil Nadu Budget Analysis 2026-27" in prs_doc.title
        assert len(prs_doc.passages) >= 1

        magalir_doc = db_session.query(EvidenceDocument).filter(EvidenceDocument.document_id == "EVD-CL-D-0015").first()
        assert magalir_doc is not None
        assert "Social Welfare Department" in magalir_doc.publisher

    def test_3_secondary_news_evidence_ingested(self, db_session):
        """Verify secondary news articles are ingested as TIER_4 evidence."""
        news_docs = db_session.query(EvidenceDocument).filter(
            EvidenceDocument.source_tier == SourceTier.TIER_4_SECONDARY_CIVIC
        ).all()
        assert len(news_docs) >= 212, f"Expected at least 212 news evidence docs, found {len(news_docs)}"

    def test_4_real_claims_registration(self, db_session):
        """Verify registration of real policy claims with verbatim Tamil/English preservation."""
        real_claims = db_session.query(Claim).filter(Claim.claim_id.like("CLM-REAL-TN-%")).all()
        assert len(real_claims) >= 8, f"Expected 8 real claims, found {len(real_claims)}"
        
        # Check Tamil preservation for Marie Wilson laptop claim
        c1 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-001").first()
        assert c1 is not None
        assert "5.32 இலட்சம்" in c1.original_text
        assert c1.speaker_name == "N. Marie Wilson"
        assert c1.party == "TVK"
        assert c1.language == "ta"

        # Check English claim for Global Investors Meet
        c5 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-005").first()
        assert c5 is not None
        assert "Global Investors Meet 2024" in c5.original_text
        assert c5.speaker_name == "M.K. Stalin"
        assert c5.party == "DMK"

    def test_5_atomic_decomposition_accuracy(self, db_session):
        """Verify atomic claims generated by MultilingualClaimPipeline retain quantitative units."""
        c1 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-001").first()
        assert len(c1.atomic_claims) >= 1
        atm1 = c1.atomic_claims[0]
        assert atm1.numeric_value == 5.32
        
        c3 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-003").first()
        assert len(c3.atomic_claims) >= 1
        atm3 = c3.atomic_claims[0]
        assert atm3.numeric_value == 1000.0
        assert atm3.unit == "INR"

    def test_6_evidence_retrieval_and_candidates(self, db_session):
        """Verify that retrieval candidates link claims to relevant documents."""
        c1 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-001").first()
        assert len(c1.retrieval_candidates) > 0
        top_cand = c1.retrieval_candidates[0]
        assert top_cand.retrieval_score > 0.4

    def test_7_evidence_relationships_and_conflicts_retained(self, db_session):
        """Verify multi-relationship analysis establishes and preserves contradictions."""
        c5 = db_session.query(Claim).filter(Claim.claim_id == "CLM-REAL-TN-005").first()
        rels = list(c5.evidence_relationships)
        assert len(rels) >= 1
        has_contradiction = any(r.relationship_type.value == "CONTRADICTS" for r in rels)
        assert has_contradiction, "Claim 5 must retain contradictory evidence relationships."

    def test_8_verification_engine_synthesis(self, db_session):
        """Verify that VerificationResult assigns valid outcomes without subjective moralizing."""
        results = db_session.query(VerificationResult).filter(
            VerificationResult.claim_id.like("CLM-REAL-TN-%")
        ).all()
        assert len(results) >= 8

        outcomes = {r.outcome.value for r in results}
        # Check that diverse epistemic outcomes are produced based on evidence
        assert "insufficient_evidence" in outcomes
        assert "contradicted_by_available_evidence" in outcomes or "missing_important_context" in outcomes

        for r in results:
            d = r.to_dict()
            assert d.get("epistemic_disclaimer") is not None
            assert "honesty" in d["epistemic_disclaimer"].lower() or "intent" in d["epistemic_disclaimer"].lower()

    def test_9_api_serving_real_claims(self, api_client):
        """Verify REST API exposes registered real claims and verification profiles."""
        res = api_client.get("/api/claims/search?q=Marie+Wilson")
        assert res.status_code == 200
        data = res.get_json()["data"]
        assert data["total"] >= 1
        assert any(c["speaker_name"] == "N. Marie Wilson" for c in data["claims"])

        # Check single claim verification profile
        ver_res = api_client.get("/api/claims/CLM-REAL-TN-001/verification")
        assert ver_res.status_code == 200
        ver_data = ver_res.get_json()["data"]
        assert ver_data["claim_id"] == "CLM-REAL-TN-001"
        assert ver_data["verification"]["outcome"] in [
            "insufficient_evidence", "supported_by_available_evidence", "pending_review"
        ]

    def test_10_dashboard_registry_integration(self):
        """Verify that dashboard registry helper seamlessly combines fixtures and real claims."""
        from frontend.pages.six_claim_verification_test_helper import (
            ALL_CLAIMS_REGISTRY, REAL_INTEGRATED_CLAIMS, FIXTURE_CLAIMS
        )
        assert len(REAL_INTEGRATED_CLAIMS) >= 8
        assert len(ALL_CLAIMS_REGISTRY) >= len(FIXTURE_CLAIMS) + len(REAL_INTEGRATED_CLAIMS)
        real_cids = {c["claim_id"] for c in REAL_INTEGRATED_CLAIMS}
        assert "CLM-REAL-TN-001" in real_cids
        assert "CLM-REAL-TN-005" in real_cids
