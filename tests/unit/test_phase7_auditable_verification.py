"""
Unit Tests for Phase 7.11 — Auditable Claim Verification & Evidence Explorer.

Verifies:
1. Complete citation metadata serialization (evidence_id, page_number, section_or_table, etc.).
2. No fabrication of missing citations (unknown fields remain None, not fabricated numbers).
3. 10-point explainable reasoning matrix generation & non-defamatory wording constraints.
4. Contradictory evidence visibility guarantee (prominent display, no suppression).
5. Syndication identification & wire copy clustering (discounting duplicate wire copy).
6. Proposition decomposition traceability & proposition-specific evidence mapping.
7. APIClient method get_claim_evidence_explorer.
8. Epistemic charter constraints (strictly no politician truthfulness scores or party rankings).
9. Disputed evidence handling (impartial multi-baseline synthesis).
10. Full 8-step auditable verification trajectory contract.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base_class import Base
from backend.models.claim import (
    Claim,
    AtomicClaim,
    EvidenceDocument,
    EvidencePassage,
    ClaimEvidenceRelationship,
    VerificationResult,
    EvidenceRelationshipType,
    VerificationOutcome,
    ClaimCategory,
    SourceTier,
    ClaimStatus,
    ReviewStatus
)
from backend.services.claim_verification_engine import ClaimVerificationEngine
from frontend.services.api import APIClient
from frontend.pages.six_claim_verification_test_helper import (
    FIXTURE_CLAIMS,
    normalize_evidence_relationship,
    ensure_structured_reasoning,
    build_evidence_explorer_dossier
)


@pytest.fixture
def memory_db():
    """In-memory SQLite DB for testing verification engine and models."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


class TestPhase7AuditableVerification:
    """Comprehensive test suite for Phase 7.11 Auditable Claim Verification."""

    def test_1_complete_citation_metadata_serialization(self):
        """Test that ClaimEvidenceRelationship and EvidencePassage serialize all citation fields."""
        doc = EvidenceDocument(
            document_id="EVD-DOC-TEST-01",
            source_name="Department of Economics and Statistics, TN",
            source_url="https://tn.gov.in/des/report2024.pdf",
            title="Statistical Handbook of Tamil Nadu 2024",
            publisher="Department of Economics and Statistics, TN",
            document_type="STATISTICAL_REPORT",
            publication_date=datetime(2024, 1, 15, tzinfo=timezone.utc),
            retrieval_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            source_tier=SourceTier.TIER_1_STATUTORY,
            language="en"
        )

        passage = EvidencePassage(
            passage_id="PAS-001",
            document_id="EVD-DOC-TEST-01",
            passage_text="Real GSDP growth rate for Tamil Nadu in FY 2023-24 stood at 8.24%.",
            page_number=42,
            section_or_table="Table 3.1: GSDP Growth",
            document=doc
        )

        passage_dict = passage.to_dict()
        assert passage_dict["passage_id"] == "PAS-001"
        assert passage_dict["page_number"] == 42
        assert passage_dict["section_or_table"] == "Table 3.1: GSDP Growth"
        assert passage_dict["source_title"] == "Statistical Handbook of Tamil Nadu 2024"
        assert passage_dict["source_url"] == "https://tn.gov.in/des/report2024.pdf"

        rel = ClaimEvidenceRelationship(
            relationship_id="REL-TEST-001",
            claim_id="CLM-001",
            atomic_claim_id="ATM-001",
            evidence_document_id="EVD-DOC-TEST-01",
            passage_id="PAS-001",
            relationship_type=EvidenceRelationshipType.SUPPORTS,
            relevance_score=0.95,
            confidence_score=0.91,
            supporting_text_reference="Real GSDP growth rate for Tamil Nadu in FY 2023-24 stood at 8.24%.",
            analysis_method="SEMANTIC_SIMILARITY_AND_NUMERICAL_CROSSCHECK",
            human_review_status=ReviewStatus.ACCEPTED,
            document=doc,
            passage=passage
        )

        rel_dict = rel.to_dict()
        assert rel_dict["evidence_id"] == "REL-TEST-001"
        assert rel_dict["document_id"] == "EVD-DOC-TEST-01"
        assert rel_dict["source_title"] == "Statistical Handbook of Tamil Nadu 2024"
        assert rel_dict["publisher"] == "Department of Economics and Statistics, TN"
        assert "2024-01-15" in rel_dict["publication_date"]
        assert rel_dict["source_tier"] == "TIER_1_STATUTORY"
        assert rel_dict["page_number"] == 42
        assert rel_dict["section_or_table"] == "Table 3.1: GSDP Growth"
        assert rel_dict["evidence_relationship"] == "supports"
        assert rel_dict["verification_status"] == "ACCEPTED"
        assert rel_dict["analysis_method"] == "SEMANTIC_SIMILARITY_AND_NUMERICAL_CROSSCHECK"

    def test_2_unknown_citations_not_fabricated(self):
        """Verify that unknown page numbers and metadata are preserved as None, never fabricated."""
        doc = EvidenceDocument(
            document_id="EVD-DOC-WEB-02",
            source_name="DIPR Tamil Nadu",
            source_url="https://tn.gov.in/press/pr.html",
            title="Press Release",
            publisher="DIPR Tamil Nadu",
            document_type="PRESS_RELEASE"
        )
        # Passage without page number or table
        passage = EvidencePassage(
            passage_id="PAS-002",
            document_id="EVD-DOC-WEB-02",
            passage_text="Web announcement excerpt.",
            page_number=None,
            section_or_table=None,
            document=doc
        )
        p_dict = passage.to_dict()
        assert p_dict["page_number"] is None
        assert p_dict["section_or_table"] is None

        rel = ClaimEvidenceRelationship(
            relationship_id="REL-002",
            claim_id="CLM-002",
            evidence_document_id="EVD-DOC-WEB-02",
            passage_id="PAS-002",
            relationship_type=EvidenceRelationshipType.SUPPORTS,
            document=doc,
            passage=passage
        )
        r_dict = rel.to_dict()
        assert r_dict["page_number"] is None
        assert r_dict["section_or_table"] is None
        assert r_dict["publication_date"] is None

    def test_3_ten_point_structured_reasoning_schema(self, memory_db):
        """Test that ClaimVerificationEngine and VerificationResult generate the 10-point reasoning breakdown."""
        # Setup claim and evidence in DB
        claim = Claim(
            claim_id="CLM-REASON-01",
            original_text="Tamil Nadu GSDP growth rate reached 8.2% in FY 2023-24.",
            normalized_text="tamil nadu gsdp growth rate reached 8.2 in fy 2023-24",
            claim_category=ClaimCategory.EMPLOYMENT_ECONOMIC,
            language="en",
            status=ClaimStatus.PENDING
        )
        atm = AtomicClaim(
            atomic_claim_id="ATM-REASON-01",
            claim_id="CLM-REASON-01",
            atomic_claim_text="Tamil Nadu GSDP growth rate reached 8.2%.",
            subject="Tamil Nadu GSDP",
            predicate="reached",
            object="8.2%"
        )
        doc = EvidenceDocument(
            document_id="DOC-REASON-01",
            source_name="DES TN",
            source_tier=SourceTier.TIER_1_STATUTORY,
            title="DES Advanced Estimates 2024",
            publisher="DES TN",
            document_type="STATISTICAL_REPORT",
            publication_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            file_hash_sha256="hash-reason-01",
            is_official=True
        )
        passage = EvidencePassage(
            passage_id="PAS-REASON-01",
            document_id="DOC-REASON-01",
            passage_text="Table 1: Real GSDP growth for 2023-24 (AE) is 8.24%."
        )
        rel = ClaimEvidenceRelationship(
            relationship_id="REL-REASON-01",
            claim_id="CLM-REASON-01",
            atomic_claim_id="ATM-REASON-01",
            evidence_document_id="DOC-REASON-01",
            passage_id="PAS-REASON-01",
            relationship_type=EvidenceRelationshipType.SUPPORTS,
            relevance_score=0.92,
            document=doc,
            passage=passage
        )

        memory_db.add_all([claim, atm, doc, passage, rel])
        memory_db.commit()

        engine = ClaimVerificationEngine(memory_db)
        synthesis = engine.synthesize_claim_outcome(claim, [rel])

        assert "structured_reasoning" in synthesis
        sr = synthesis["structured_reasoning"]
        assert len(sr) == 10
        assert "claim_evaluated" in sr
        assert "specific_propositions" in sr
        assert "supporting_evidence_summary" in sr
        assert "contradicting_evidence_summary" in sr
        assert "context_and_qualifications" in sr
        assert "evidence_gaps" in sr
        assert "source_reliability_and_limitations" in sr
        assert "outcome_justification" in sr
        assert "remaining_uncertainty" in sr
        assert "methodology_and_model" in sr

        # Verify epistemic wording is non-defamatory
        assert "absence of proof" in sr["remaining_uncertainty"].lower() or "proof of falsehood" in sr["remaining_uncertainty"].lower()

        # Also verify helper ensure_structured_reasoning
        helper_sr = ensure_structured_reasoning(FIXTURE_CLAIMS[0])
        assert len(helper_sr) == 10
        assert "claim_evaluated" in helper_sr

    def test_4_contradictory_evidence_visibility_guarantee(self):
        """Verify that contradicting evidence is prominently structured and not hidden or suppressed."""
        dossier = build_evidence_explorer_dossier(FIXTURE_CLAIMS[1])  # CLM_02: School enrollment contradicted
        assert dossier["claim_id"] == "TEST_FIXTURE_CLM_02"

        ev_comp = dossier["evidence_comparison"]
        assert len(ev_comp["contradicting"]) >= 1
        assert len(ev_comp["supporting"]) == 0

        # Verify empty state message for supporting evidence is explicit and neutral
        assert ev_comp["empty_states"]["supporting"] is not None
        assert "absence of evidence" in ev_comp["empty_states"]["supporting"].lower()

        # Contradicting item has full citation
        contra_item = ev_comp["contradicting"][0]
        assert contra_item["evidence_relationship"] == "contradicts"
        assert contra_item["publisher"] is not None
        assert contra_item["passage_reference"] is not None

    def test_5_syndicated_wire_copy_identification(self):
        """Verify that syndicated wire copies are identified and do not artificially inflate source diversity."""
        claim_with_syndication = {
            "claim_id": "CLM-SYND-01",
            "original_text": "Scheme investment reached Rs 1000 crore.",
            "relationships": [
                {
                    "relationship_id": "REL-PRIMARY",
                    "evidence_document_id": "EVD-PTI-01",
                    "source_title": "PTI Wire Dispatch",
                    "publisher": "Press Trust of India",
                    "relationship_type": "supports",
                    "passage_reference": "Investment of 1000 crore announced.",
                    "is_syndicated_copy": False,
                    "syndication_cluster_id": "CLUSTER-PTI-01"
                },
                {
                    "relationship_id": "REL-SYND-A",
                    "evidence_document_id": "EVD-REP-01",
                    "source_title": "Daily News Article Copy",
                    "publisher": "Republisher A",
                    "relationship_type": "supports",
                    "passage_reference": "Investment of 1000 crore announced.",
                    "is_syndicated_copy": True,
                    "syndication_cluster_id": "CLUSTER-PTI-01",
                    "primary_source_publisher": "Press Trust of India"
                }
            ],
            "verification": {
                "outcome": "supported_by_available_evidence",
                "explanation": "Supported by news report.",
                "source_diversity": 1
            }
        }

        dossier = build_evidence_explorer_dossier(claim_with_syndication)
        ev_comp = dossier["evidence_comparison"]
        assert "CLUSTER-PTI-01" in ev_comp["syndicated_clusters"]
        # Find the syndicated item
        synd_items = [r for r in ev_comp["supporting"] if r.get("is_syndicated_copy")]
        assert len(synd_items) == 1
        assert synd_items[0]["primary_source_publisher"] == "Press Trust of India"

    def test_6_proposition_decomposition_traceability(self):
        """Test that atomic propositions map supporting and contradicting evidence independently."""
        claim_multi = FIXTURE_CLAIMS[0]  # GSDP claim
        dossier = build_evidence_explorer_dossier(claim_multi)

        atomic_list = dossier["atomic_claims"]
        assert len(atomic_list) >= 1
        prop = atomic_list[0]
        assert "atomic_claim" in prop
        assert "resolution_status" in prop
        assert prop["resolution_status"] in ["SUPPORTED", "CONTRADICTED", "DISPUTED", "CONTEXTUALIZED", "UNRESOLVED"]
        assert len(prop["supporting_evidence"]) >= 1

    def test_7_api_client_evidence_explorer_method(self):
        """Test APIClient.get_claim_evidence_explorer wrapper."""
        client = APIClient(base_url="http://localhost:8000")

        with patch("requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.ok = True
            mock_resp.json.return_value = {
                "status": "success",
                "data": {
                    "claim_id": "TEST_FIXTURE_CLM_01",
                    "original_claim": {"claim_id": "TEST_FIXTURE_CLM_01"},
                    "atomic_claims": [],
                    "evidence_comparison": {"supporting": [], "contradicting": [], "contextual": []},
                    "verification_reasoning": {"outcome": "supported_by_available_evidence"},
                    "source_documents": [],
                    "verification_history": []
                }
            }
            mock_get.return_value = mock_resp

            ok, dossier = client.get_claim_evidence_explorer("TEST_FIXTURE_CLM_01")
            assert ok is True
            assert dossier["claim_id"] == "TEST_FIXTURE_CLM_01"
            assert "evidence_comparison" in dossier
            assert "verification_reasoning" in dossier

    def test_8_no_politician_truthfulness_scoring_charter(self):
        """Charter Guarantee: strictly verify absence of politician honesty scores or party leaderboards."""
        for claim in FIXTURE_CLAIMS:
            dossier = build_evidence_explorer_dossier(claim)
            dossier_str = str(dossier).lower()

            # Ensure banned concepts are completely absent
            assert "truthfulness score" not in dossier_str
            assert "honesty score" not in dossier_str
            assert "politician rank" not in dossier_str
            assert "party ranking" not in dossier_str
            assert "leaderboard" not in dossier_str

    def test_9_disputed_evidence_handling(self):
        """Verify that disputed evidence (different metric baselines) presents both sides impartially."""
        claim_disputed = next(c for c in FIXTURE_CLAIMS if c["claim_id"] == "TEST_FIXTURE_CLM_06")
        dossier = build_evidence_explorer_dossier(claim_disputed)

        ev_comp = dossier["evidence_comparison"]
        # Must have both supporting and contradicting evidence
        assert len(ev_comp["supporting"]) >= 1
        assert len(ev_comp["contradicting"]) >= 1

        v_reason = dossier["verification_reasoning"]
        assert v_reason["outcome"] == "disputed_evidence"
        # Reasoning must explain the dual denominator baseline
        assert "per-capita" in v_reason["explanation"].lower() or "budget" in v_reason["explanation"].lower()

    def test_10_full_trajectory_dossier_contract(self):
        """Validate the full 8-step auditable verification trajectory contract."""
        dossier = build_evidence_explorer_dossier(FIXTURE_CLAIMS[0])

        # 1. Original Political Claim
        assert dossier["original_claim"]["original_text"] is not None
        # 2. Atomic Claims
        assert len(dossier["atomic_claims"]) > 0
        # 3. Supporting Evidence
        assert "supporting" in dossier["evidence_comparison"]
        # 4. Contradicting Evidence
        assert "contradicting" in dossier["evidence_comparison"]
        # 5. Contextual Evidence
        assert "contextual" in dossier["evidence_comparison"]
        # 6. Verification Reasoning
        assert "structured_reasoning" in dossier["verification_reasoning"]
        # 7. Final Evidence Assessment
        assert "outcome" in dossier["verification_reasoning"]
        # 8. Original Source Documents
        assert len(dossier["source_documents"]) > 0
        for doc in dossier["source_documents"]:
            assert "document_id" in doc
            assert "source_tier" in doc
            assert "file_hash_sha256" in doc
