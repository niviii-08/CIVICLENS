"""
CivicLens TN - Real Phase 7 Data Ingestion and Verification Runner
Loads real official references and secondary news articles from data/raw/phase7/extracted/,
populates EvidenceDocument and EvidencePassage, ingests 8 real policy claims, executes
claim decomposition, candidate evidence retrieval, relationship analysis, and verification engine.
"""

import os
import sys
import csv
import hashlib
from datetime import datetime, timezone

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.session import SessionLocal, engine
from backend.database.base_class import Base
from backend.models.claim import (
    Claim, ClaimVersion, AtomicClaim, EvidenceDocument, EvidencePassage,
    ClaimEvidenceRelationship, ClaimRetrievalCandidate, VerificationResult,
    VerificationHistory, VerificationRun, ClaimCategory, AttributionType,
    CandidateSourceType, SourceTier, ClaimStatus, ReviewStatus,
    EvidenceRelationshipType, VerificationOutcome, VerificationVerdict
)
from backend.nlp.claim_decomposition import MultilingualClaimPipeline
from backend.services.evidence_retrieval import EvidenceRetrievalEngine
from backend.services.evidence_relationship_analyzer import EvidenceRelationshipAnalyzer
from backend.services.claim_verification_engine import ClaimVerificationEngine


def run_real_ingestion():
    # Ensure all tables exist in target SQLite DB
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        print("Ingesting official references...")
        off_path = "data/raw/phase7/extracted/datasets/official_references.csv"
        if os.path.exists(off_path):
            with open(off_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    ref_id = r["reference_id"]
                    doc_id = f"EVD-{ref_id}"
                    existing = db.query(EvidenceDocument).filter(EvidenceDocument.document_id == doc_id).first()
                    if not existing:
                        pub_dt = None
                        if r.get("publication_date"):
                            try:
                                pub_dt = datetime.strptime(r["publication_date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                            except Exception:
                                pub_dt = datetime.now(timezone.utc)
                        text_content = r.get("document_text_or_summary", "")
                        h = hashlib.sha256(text_content.encode("utf-8")).hexdigest()
                        doc = EvidenceDocument(
                            document_id=doc_id,
                            source_tier=SourceTier.TIER_1_STATUTORY,
                            source_name="Official Statutory Record",
                            publisher=r.get("issuing_authority", "Government of Tamil Nadu"),
                            document_type=r.get("reference_type", "statutory_record"),
                            source_category="OFFICIAL_REFERENCE",
                            title=r.get("title", "Statutory Reference"),
                            publication_date=pub_dt,
                            retrieval_date=datetime.now(timezone.utc),
                            source_url=r.get("url", ""),
                            file_path=off_path,
                            file_hash_sha256=h,
                            extraction_method="OFFICIAL_REGISTRY_IMPORT",
                            access_status="PUBLIC",
                            language="en",
                            is_official=True,
                            is_test_fixture=False
                        )
                        db.add(doc)
                        psg = EvidencePassage(
                            passage_id=f"PSG-{ref_id}-01",
                            document_id=doc_id,
                            passage_text=text_content,
                            section_or_table=r.get("reference_type", "Summary")
                        )
                        db.add(psg)
            db.commit()

        print("Ingesting news articles...")
        news_path = "data/raw/phase7/extracted/datasets/news_articles.csv"
        if os.path.exists(news_path):
            with open(news_path, "r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for r in reader:
                    art_id = r.get("article_id")
                    if not art_id:
                        continue
                    doc_id = f"EVD-{art_id}"
                    existing = db.query(EvidenceDocument).filter(EvidenceDocument.document_id == doc_id).first()
                    if not existing:
                        pub_dt = None
                        if r.get("published_date"):
                            try:
                                pub_dt = datetime.strptime(r["published_date"].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
                            except Exception:
                                pub_dt = datetime.now(timezone.utc)
                        art_text = r.get("article_text", "")
                        h = hashlib.sha256(f"{doc_id}:{art_text}".encode("utf-8")).hexdigest()
                        doc = EvidenceDocument(
                            document_id=doc_id,
                            source_tier=SourceTier.TIER_4_SECONDARY_CIVIC,
                            source_name=r.get("source", "News Media"),
                            publisher=r.get("source", "News Media"),
                            document_type="news_article",
                            source_category="NEWS_ARTICLE",
                            title=r.get("title", "News Report"),
                            publication_date=pub_dt,
                            retrieval_date=datetime.now(timezone.utc),
                            source_url=r.get("url", ""),
                            file_path=news_path,
                            file_hash_sha256=h,
                            extraction_method="SCRAPED_PARSED",
                            access_status="PUBLIC",
                            language="ta" if r.get("language") == "Tamil" else "en",
                            is_official=False,
                            is_test_fixture=False
                        )
                        db.add(doc)
                        psg_text = art_text[:1200]
                        psg = EvidencePassage(
                            passage_id=f"PSG-{art_id}-01",
                            document_id=doc_id,
                            passage_text=psg_text,
                            section_or_table=r.get("category", "News")
                        )
                        db.add(psg)
            db.commit()

        print("Registering real policy claims...")
        real_claims_data = [
            {
                "claim_id": "CLM-REAL-TN-001",
                "original_text": "5.32 இலட்சம் 11ஆம் வகுப்பு மாணாக்கர்களுக்கு மடிக்கணினி வழங்கப்படும்.",
                "language": "ta",
                "speaker_name": "N. Marie Wilson",
                "speaker_role": "Minister for Finance and Human Resources",
                "party": "TVK",
                "claim_date": datetime(2026, 8, 5, tzinfo=timezone.utc),
                "category": ClaimCategory.GOVERNMENT_SCHEMES,
                "source_type": CandidateSourceType.LEGISLATIVE_RECORD,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://www.nakkheeran.in/24-by-7-news/budget-2026-key-annou",
                "doc_id": "DOC-NEWS-CL-A-0001",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-002",
                "original_text": "2036-க்குள் 1.5 லட்சம் கோடி டாலர் பொருளாதாரத்தை எட்ட தமிழ்நாடு அரசு இலக்கு நிர்ணயித்துள்ளது.",
                "language": "ta",
                "speaker_name": "N. Marie Wilson",
                "speaker_role": "Minister for Finance and Human Resources",
                "party": "TVK",
                "claim_date": datetime(2026, 8, 5, tzinfo=timezone.utc),
                "category": ClaimCategory.EMPLOYMENT_ECONOMIC,
                "source_type": CandidateSourceType.LEGISLATIVE_RECORD,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://bernama.com/tam/news.php?id=2590665",
                "doc_id": "DOC-NEWS-CL-A-0003",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-003",
                "original_text": "Pudhumai Penn scheme disburses Rs 1000 monthly financial assistance to government school girl students pursuing higher education.",
                "language": "en",
                "speaker_name": "M.K. Stalin",
                "speaker_role": "Chief Minister of Tamil Nadu",
                "party": "DMK",
                "claim_date": datetime(2022, 9, 5, tzinfo=timezone.utc),
                "category": ClaimCategory.GOVERNMENT_SCHEMES,
                "source_type": CandidateSourceType.OFFICIAL_STATEMENT,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://www.tn.gov.in/scheme/data_view/9898",
                "doc_id": "DOC-GOVT-CL-D-0014",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-004",
                "original_text": "Kalaignar Magalir Urimai Thogai scheme provides Rs 1,000 monthly financial aid to over 1 crore eligible women heads of families.",
                "language": "en",
                "speaker_name": "M.K. Stalin",
                "speaker_role": "Chief Minister of Tamil Nadu",
                "party": "DMK",
                "claim_date": datetime(2023, 9, 15, tzinfo=timezone.utc),
                "category": ClaimCategory.GOVERNMENT_SCHEMES,
                "source_type": CandidateSourceType.OFFICIAL_STATEMENT,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://www.tn.gov.in/scheme/data_view/9899",
                "doc_id": "DOC-GOVT-CL-D-0015",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-005",
                "original_text": "Tamil Nadu Global Investors Meet 2024 attracted prospective investment commitments exceeding Rs. 6 lakh crore.",
                "language": "en",
                "speaker_name": "M.K. Stalin",
                "speaker_role": "Chief Minister of Tamil Nadu",
                "party": "DMK",
                "claim_date": datetime(2024, 1, 7, tzinfo=timezone.utc),
                "category": ClaimCategory.EMPLOYMENT_ECONOMIC,
                "source_type": CandidateSourceType.PRESS_RELEASE,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://www.dipr.tn.gov.in/",
                "doc_id": "DOC-DIPR-CL-D-0021",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-006",
                "original_text": "Makkalai Thedi Maruthuvam healthcare scheme has surpassed one crore doorstep healthcare service deliveries across Tamil Nadu.",
                "language": "en",
                "speaker_name": "Ma. Subramanian",
                "speaker_role": "Minister for Health and Family Welfare",
                "party": "DMK",
                "claim_date": datetime(2023, 1, 10, tzinfo=timezone.utc),
                "category": ClaimCategory.HEALTHCARE_EDUCATION,
                "source_type": CandidateSourceType.PRESS_RELEASE,
                "attr_type": AttributionType.DIRECT_QUOTE,
                "url": "https://www.tn.gov.in/scheme/data_view/9890",
                "doc_id": "DOC-GOVT-CL-D-0016",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-007",
                "original_text": "Committed expenditure comprising salaries, pensions, and interest payments consumed approximately 61 per cent of revenue receipts in Tamil Nadu revised budget 2026-27.",
                "language": "en",
                "speaker_name": "PRS Legislative Research",
                "speaker_role": "Independent Research Think-Tank",
                "party": "Independent",
                "claim_date": datetime(2026, 8, 28, tzinfo=timezone.utc),
                "category": ClaimCategory.BUDGET_EXPENDITURE,
                "source_type": CandidateSourceType.OFFICIAL_STATEMENT,
                "attr_type": AttributionType.JOURNALIST_DESCRIPTION,
                "url": "https://prsindia.org/budgets/states/tamil-nadu-budget-analysis-2026-27",
                "doc_id": "DOC-PRS-CL-D-0001",
                "geo": "Tamil Nadu"
            },
            {
                "claim_id": "CLM-REAL-TN-008",
                "original_text": "அனைத்து அரசுப் பள்ளிகளிலும் முழுமையாக நவீன ஸ்மார்ட் வகுப்பறைகள் அமைத்து முடிக்கப்பட்டுவிட்டன.",
                "language": "ta",
                "speaker_name": "Unverified Social Media Post",
                "speaker_role": "Citizen Submission",
                "party": "None",
                "claim_date": datetime(2026, 9, 1, tzinfo=timezone.utc),
                "category": ClaimCategory.HEALTHCARE_EDUCATION,
                "source_type": CandidateSourceType.MANUAL_SUBMISSION,
                "attr_type": AttributionType.USER_SUBMITTED,
                "url": "https://public-forum.tn.gov/claims/submission-8812",
                "doc_id": "DOC-CITIZEN-008",
                "geo": "Tamil Nadu"
            }
        ]

        for cd in real_claims_data:
            c = db.query(Claim).filter(Claim.claim_id == cd["claim_id"]).first()
            if not c:
                h = hashlib.sha256(cd["original_text"].encode("utf-8")).hexdigest()
                c = Claim(
                    claim_id=cd["claim_id"],
                    original_text=cd["original_text"],
                    normalized_text=cd["original_text"].strip(),
                    language=cd["language"],
                    speaker_name=cd["speaker_name"],
                    speaker_role=cd["speaker_role"],
                    speaker_party=cd["party"],
                    party=cd["party"],
                    claim_date=cd["claim_date"],
                    publication_date=cd["claim_date"],
                    claim_category=cd["category"],
                    candidate_source_type=cd["source_type"],
                    attribution_type=cd["attr_type"],
                    claim_source_url=cd["url"],
                    source_document_id=cd["doc_id"],
                    geographic_scope=cd["geo"],
                    extraction_method="MANUAL_CURATION" if "USER" not in cd["doc_id"] else "CITIZEN_SUBMISSION",
                    content_fingerprint=h,
                    status=ClaimStatus.UNDER_REVIEW,
                    review_status=ReviewStatus.PENDING_REVIEW,
                    is_test_fixture=False
                )
                db.add(c)
                db.flush()

                # Atomic claim decomposition
                nlp_pipeline = MultilingualClaimPipeline()
                decomp = nlp_pipeline.process_claim(claim_id=c.claim_id, original_text=c.original_text, persist_to_db=False)
                for at in decomp["atomic_claims"]:
                    acm = AtomicClaim(
                        atomic_claim_id=at["atomic_claim_id"],
                        claim_id=c.claim_id,
                        atomic_claim_text=at["atomic_claim_text"],
                        language=at["language"],
                        subject=at.get("subject", "Tamil Nadu"),
                        predicate=at.get("predicate", "asserts"),
                        action=at.get("action", "announces"),
                        object=at.get("object", at["atomic_claim_text"]),
                        numeric_value=at.get("numeric_value"),
                        unit=at.get("unit"),
                        claim_type=at.get("claim_type", "FACTUAL"),
                        decomposition_method="MULTILINGUAL_RULE_EXTRACTION",
                        confidence=at.get("confidence", 0.95),
                        is_verifiable=at.get("is_verifiable", True)
                    )
                    db.add(acm)

        db.commit()

        print("Executing evidence retrieval, relationships, and verification...")
        retrieval_engine = EvidenceRetrievalEngine(db)
        relationship_analyzer = EvidenceRelationshipAnalyzer(db)
        verification_engine = ClaimVerificationEngine(db)

        all_real_claims = db.query(Claim).filter(Claim.claim_id.like("CLM-REAL-TN-%")).all()
        for c in all_real_claims:
            for acm in c.atomic_claims:
                cands = retrieval_engine.retrieve_candidate_evidence(
                    claim_id=c.claim_id,
                    query_text=acm.atomic_claim_text,
                    atomic_claim_id=acm.atomic_claim_id,
                    language=c.language,
                    top_k=5,
                    persist_candidates=True
                )
            db.flush()

            # Analyze and persist relationships
            relationship_analyzer.analyze_and_persist_relationships(claim_id=c.claim_id)

            # Execute Claim Verification Synthesis
            ver_result = verification_engine.verify_claim(c.claim_id)
            c.status = ClaimStatus.VERIFIED

        db.commit()
        print("Real data ingestion and verification pipeline completed successfully.")
    except Exception as e:
        db.rollback()
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_real_ingestion()
