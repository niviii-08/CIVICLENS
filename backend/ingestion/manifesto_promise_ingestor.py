"""
CIVICLENS TN — Sourced Manifesto and Political Promise Ingestion Pipeline
========================================================================
Canonical ingestion module for political manifestos, party commitments,
and evidence linkages.

Enforces strict provenance, verbatim text and language preservation (Tamil/English),
derived content labelling, measurable target tracking, review status flagging,
and non-causal separation between stated promises, schemes, and budget allocations.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter
from datetime import datetime, timezone

from sqlalchemy.orm import Session
from backend.database.session import SessionLocal, engine
import backend.database.base as db_base
from backend.models.manifesto import ManifestoSource, ManifestoDocument, Manifesto
from backend.models.promise import (
    PoliticalPromise,
    PromiseCategory,
    PromiseCategoryMapping,
    PromiseSchemeLink,
    PromiseAssessment,
    PromiseStatus
)
from backend.models.budget import HistoricalScheme

logger = logging.getLogger("ManifestoPromiseIngestor")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ManifestoPromiseIngestor:
    """
    Ingests official manifestos, verbatim promises, and scheme cross-references
    with strict epistemic discipline and provenance tracking.
    """

    def __init__(
        self,
        db_session: Session,
        manifest_file: str = "data/raw/manifestos/manifest.json",
        validated_promises_file: str = "data/processed/promises/validated_promises.json",
        scheme_matches_file: str = "data/processed/promises/promise_scheme_matches.json",
        assessments_file: str = "data/processed/assessments/real_promise_assessments.json"
    ):
        self.db = db_session
        self.manifest_file = manifest_file
        self.validated_promises_file = validated_promises_file
        self.scheme_matches_file = scheme_matches_file
        self.assessments_file = assessments_file

    def ingest_all(self) -> Dict[str, Any]:
        """
        Executes full ingestion pipeline across sources, documents, manifestos,
        categories, promises, scheme matches, and status assessments.
        """
        logger.info("Starting CIVICLENS TN Manifesto & Promise Ingestion Pipeline...")

        db_base.Base.metadata.create_all(bind=engine)

        metrics = {
            "sources_processed": 0,
            "documents_processed": 0,
            "manifestos_processed": 0,
            "categories_processed": 0,
            "promises_discovered": 0,
            "promises_inserted": 0,
            "promises_updated": 0,
            "promises_rejected": 0,
            "promises_flagged_ambiguous": 0,
            "exact_duplicates": 0,
            "probable_duplicates": 0,
            "category_mappings_created": 0,
            "scheme_links_created": 0,
            "assessments_created": 0,
            "by_party": Counter(),
            "by_election": Counter(),
            "by_language": Counter(),
            "by_classification": Counter()
        }

        # Step 1: Ingest Sources, Documents, and Manifestos
        self._ingest_manifesto_catalog(metrics)

        # Step 2: Ingest Taxonomies & Promises
        self._ingest_promises_and_taxonomies(metrics)

        # Step 3: Ingest Scheme Links (with explicit non-causal disclaimer)
        self._ingest_scheme_links(metrics)

        # Step 4: Ingest Assessments
        self._ingest_assessments(metrics)

        logger.info("Manifesto & Promise Ingestion Pipeline completed successfully.")
        return metrics

    def _ingest_manifesto_catalog(self, metrics: Dict[str, Any]):
        """Ingests ManifestoSource, ManifestoDocument, and Manifesto entities."""
        if not os.path.exists(self.manifest_file):
            logger.warning(f"Manifest file {self.manifest_file} not found.")
            return

        with open(self.manifest_file, "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

        raw_files = manifest_data.get("files", [])
        logger.info(f"Loaded {len(raw_files)} raw manifesto files from {self.manifest_file}.")

        manifestos_map: Dict[str, Dict[str, Any]] = {}

        for rfile in raw_files:
            fid = rfile["file_id"]
            source_id = f"SRC-{fid}"
            doc_id = f"DOC-{fid}"

            # 1. ManifestoSource
            source_obj = self.db.query(ManifestoSource).filter(ManifestoSource.source_id == source_id).first()
            if not source_obj:
                source_obj = ManifestoSource(
                    source_id=source_id,
                    organization=rfile.get("party") or "Archive",
                    source_url=rfile.get("source_url"),
                    source_type="primary" if rfile.get("party") else "archive",
                    source_tier=1,
                    retrieval_method="local_dataset_registration",
                    retrieval_status="completed",
                    checksum=rfile.get("sha256"),
                    notes=rfile.get("document_title")
                )
                self.db.add(source_obj)
                self.db.flush()
                metrics["sources_processed"] += 1

            # 2. ManifestoDocument
            doc_obj = self.db.query(ManifestoDocument).filter(ManifestoDocument.document_id == doc_id).first()
            if not doc_obj:
                doc_obj = ManifestoDocument(
                    document_id=doc_id,
                    source_id=source_id,
                    original_filename=rfile.get("original_filename"),
                    file_format=rfile.get("file_type", "pdf").upper(),
                    file_size=rfile.get("size_bytes"),
                    storage_path=rfile.get("relative_path"),
                    checksum=rfile.get("sha256"),
                    page_count=1,
                    extraction_method="rule_based_pdf",
                    extraction_status="completed"
                )
                self.db.add(doc_obj)
                self.db.flush()
                metrics["documents_processed"] += 1

            # 3. Formulate Manifesto ID
            party_name = rfile.get("party") or "ARCHIVE"
            year_val = rfile.get("election_year") or 2026
            m_id = f"MF-{party_name}-{year_val}"

            if m_id not in manifestos_map:
                manifestos_map[m_id] = {
                    "manifesto_id": m_id,
                    "party": party_name,
                    "election": f"{year_val} Tamil Nadu Legislative Assembly Election",
                    "election_year": year_val,
                    "language": rfile.get("language") or "English",
                    "title": rfile.get("document_title") or f"{party_name} Manifesto {year_val}",
                    "source_id": source_id,
                    "document_id": doc_id
                }

        for m_id, m_info in manifestos_map.items():
            existing_m = self.db.query(Manifesto).filter(Manifesto.manifesto_id == m_id).first()
            if not existing_m:
                m_obj = Manifesto(
                    manifesto_id=m_info["manifesto_id"],
                    party=m_info["party"],
                    election=m_info["election"],
                    election_year=m_info["election_year"],
                    language=m_info["language"],
                    title=m_info["title"],
                    source_id=m_info["source_id"],
                    document_id=m_info["document_id"],
                    extraction_status="completed",
                    verification_status="verified"
                )
                self.db.add(m_obj)
                metrics["manifestos_processed"] += 1

        self.db.commit()
        logger.info(f"Manifesto catalog processed: {len(manifestos_map)} manifestos.")

    def _ingest_promises_and_taxonomies(self, metrics: Dict[str, Any]):
        """Ingests validated political promises, category mappings, and target tracking."""
        if not os.path.exists(self.validated_promises_file):
            logger.warning(f"Validated promises file {self.validated_promises_file} not found.")
            return

        with open(self.validated_promises_file, "r", encoding="utf-8") as f:
            validated_promises = json.load(f)

        metrics["promises_discovered"] = len(validated_promises)
        logger.info(f"Processing {len(validated_promises)} validated promises...")

        # Pre-seed categories
        unique_categories = set(p.get("category", "Uncategorized") for p in validated_promises)
        category_objs: Dict[str, PromiseCategory] = {}

        for cat_name in sorted(unique_categories):
            cat_obj = self.db.query(PromiseCategory).filter(PromiseCategory.category_code == cat_name).first()
            if not cat_obj:
                cat_obj = PromiseCategory(
                    category_code=cat_name,
                    name=cat_name,
                    description=f"{cat_name} policy commitments and welfare promises"
                )
                self.db.add(cat_obj)
                self.db.flush()
                metrics["categories_processed"] += 1
            category_objs[cat_name] = cat_obj

        self.db.commit()

        for p in validated_promises:
            pid = p.get("promise_id")
            orig_text = p.get("original_text", "").strip()
            v_status = p.get("validation_status", "valid")

            # Anti-fabrication check: reject empty text or invalid provenance
            if not orig_text or v_status == "invalid":
                metrics["promises_rejected"] += 1
                logger.warning(f"Rejecting unanchored or invalid promise: {pid}")
                continue

            if v_status == "duplicate":
                metrics["exact_duplicates"] += 1
            elif v_status == "probable_duplicate":
                metrics["probable_duplicates"] += 1

            manifesto_id = p.get("manifesto_id")
            cat_name = p.get("category", "Uncategorized")
            lang = p.get("language", "Unknown")
            classification = p.get("classification", "general_policy")
            confidence = float(p.get("confidence", 1.0))

            # Ensure parent manifesto exists
            manifesto_obj = self.db.query(Manifesto).filter(Manifesto.manifesto_id == manifesto_id).first()
            if not manifesto_obj:
                party_code = manifesto_id.split("-")[1] if len(manifesto_id.split("-")) >= 2 else "Party"
                year_val = int(manifesto_id.split("-")[2]) if len(manifesto_id.split("-")) >= 3 and manifesto_id.split("-")[2].isdigit() else 2026
                manifesto_obj = Manifesto(
                    manifesto_id=manifesto_id,
                    party=party_code,
                    election=f"{year_val} Tamil Nadu Legislative Assembly Election",
                    election_year=year_val,
                    language=lang,
                    title=f"{party_code} Manifesto {year_val}",
                    extraction_status="completed",
                    verification_status="verified"
                )
                self.db.add(manifesto_obj)
                self.db.flush()

            # Ambiguity & Review Status logic
            review_flags = list(p.get("validation_flags", []))
            if v_status in ["needs_review", "probable_duplicate"]:
                flag_name = f"validation_status_{v_status}"
                if flag_name not in review_flags:
                    review_flags.append(flag_name)
            if classification == "ambiguous":
                if "ambiguous_classification" not in review_flags:
                    review_flags.append("ambiguous_classification")

            is_ambiguous = (
                v_status in ["needs_review", "probable_duplicate"]
                or p.get("is_ambiguous", False)
                or classification == "ambiguous"
                or bool(review_flags)
            )
            if is_ambiguous:
                metrics["promises_flagged_ambiguous"] += 1

            # Extract structured targets if present
            raw_meta = p.get("metadata", {})
            structured_targets = {
                "numeric_target": raw_meta.get("numeric_target"),
                "monetary_target": raw_meta.get("monetary_target"),
                "time_horizon": raw_meta.get("time_horizon"),
                "target_population": raw_meta.get("target_population"),
                "responsible_department": raw_meta.get("department"),
                "geography": raw_meta.get("geography")
            }

            metadata_payload = {
                "category": cat_name,
                "validation_status": v_status,
                "validation_score": p.get("validation_score", 1.0),
                "validation_flags": review_flags,
                "derived_content": {
                    "normalized_text": p.get("normalized_text", orig_text),
                    "classification": classification,
                    "derived_category": cat_name,
                    "extracted_targets": {k: v for k, v in structured_targets.items() if v is not None}
                },
                "epistemic_guardrails": {
                    "record_type": "STATED_ELECTION_PROMISE",
                    "fulfillment_inferred_from_scheme": False,
                    "fulfillment_inferred_from_budget": False,
                    "disclaimer": "Stated election promises are commitments made by political parties. Implementation, budget allocation, and outcome verification require independent corroboration."
                }
            }

            metrics["by_party"][manifesto_obj.party] += 1
            metrics["by_election"][str(manifesto_obj.election_year)] += 1
            metrics["by_language"][lang] += 1
            metrics["by_classification"][classification] += 1

            existing_p = self.db.query(PoliticalPromise).filter(PoliticalPromise.promise_id == pid).first()
            if not existing_p:
                promise_obj = PoliticalPromise(
                    promise_id=pid,
                    manifesto_id=manifesto_id,
                    original_text=orig_text,  # Verbatim text in original language preserved
                    normalized_text=p.get("normalized_text", orig_text),
                    page_number=p.get("page_number"),
                    section=p.get("section"),
                    language=lang,
                    classification=classification,
                    extraction_method=p.get("extraction_method", "rule_based_v1"),
                    extraction_confidence=confidence,
                    is_ambiguous=is_ambiguous,
                    is_test_fixture=False,
                    metadata_json=metadata_payload
                )
                self.db.add(promise_obj)
                metrics["promises_inserted"] += 1

                # Category Mapping
                cat_obj = category_objs.get(cat_name)
                if cat_obj:
                    mapping_obj = PromiseCategoryMapping(
                        promise_id=pid,
                        category_id=cat_obj.id,
                        is_primary=True,
                        confidence=confidence
                    )
                    self.db.add(mapping_obj)
                    metrics["category_mappings_created"] += 1
            else:
                existing_p.original_text = orig_text
                existing_p.normalized_text = p.get("normalized_text", orig_text)
                existing_p.page_number = p.get("page_number")
                existing_p.section = p.get("section")
                existing_p.language = lang
                existing_p.classification = classification
                existing_p.extraction_confidence = confidence
                existing_p.is_ambiguous = is_ambiguous
                existing_p.metadata_json = metadata_payload
                metrics["promises_updated"] += 1

        self.db.commit()
        logger.info(f"Promises committed: {metrics['promises_inserted']} inserted, {metrics['promises_updated']} updated.")

    def _ingest_scheme_links(self, metrics: Dict[str, Any]):
        """Ingests semantic links between promises and historical schemes with non-causal disclaimer."""
        if not os.path.exists(self.scheme_matches_file):
            logger.info("Scheme matches file not present; skipping scheme link ingestion.")
            return

        with open(self.scheme_matches_file, "r", encoding="utf-8") as f:
            matches_data = json.load(f)

        logger.info(f"Ingesting {len(matches_data)} promise-to-scheme candidate matches...")
        for m in matches_data:
            pid = m.get("promise_id")
            s_name = m.get("scheme_name")
            sim_score = float(m.get("similarity_score", 0.0))

            scheme_obj = self.db.query(HistoricalScheme).filter(HistoricalScheme.scheme_name == s_name).first()
            if not scheme_obj:
                continue

            existing_link = self.db.query(PromiseSchemeLink).filter(
                PromiseSchemeLink.promise_id == pid,
                PromiseSchemeLink.historical_scheme_id == scheme_obj.id
            ).first()

            notes_text = (
                f"Confidence tier: {m.get('confidence_tier', 'Low')}. "
                "NON-CAUSAL LINK: Semantic similarity indicates topical relation only; "
                "does NOT imply promise fulfillment, budget sanction, or policy enactment."
            )

            if not existing_link:
                link_obj = PromiseSchemeLink(
                    promise_id=pid,
                    historical_scheme_id=scheme_obj.id,
                    similarity_score=sim_score,
                    confidence=sim_score,
                    matching_method=m.get("matching_method", "multilingual_hybrid_cosine_similarity"),
                    notes=notes_text
                )
                self.db.add(link_obj)
                metrics["scheme_links_created"] += 1
            else:
                existing_link.similarity_score = sim_score
                existing_link.confidence = sim_score
                existing_link.notes = notes_text

        self.db.commit()
        logger.info(f"Scheme links committed: {metrics['scheme_links_created']} records.")

    def _ingest_assessments(self, metrics: Dict[str, Any]):
        """Ingests promise implementation assessments."""
        if not os.path.exists(self.assessments_file):
            logger.info("Assessments file not present; skipping assessment ingestion.")
            return

        with open(self.assessments_file, "r", encoding="utf-8") as f:
            assessments_data = json.load(f)

        logger.info(f"Ingesting {len(assessments_data)} promise assessments...")
        for a in assessments_data:
            pid = a.get("promise_id")
            status_val = a.get("status", "unclear")

            existing_ass = self.db.query(PromiseAssessment).filter(PromiseAssessment.promise_id == pid).first()
            
            try:
                p_status = PromiseStatus(status_val)
            except ValueError:
                p_status = PromiseStatus.unclear

            if not existing_ass:
                ass_obj = PromiseAssessment(
                    promise_id=pid,
                    status=p_status,
                    confidence_score=float(a.get("confidence", 0.0)),
                    explanation=a.get("explanation", ""),
                    evidence_citations=a.get("evidence_ids", []),
                    source_tiers=a.get("source_tiers", []),
                    assessed_at=datetime.now(timezone.utc),
                    evaluation_method=a.get("methodology", "transparent_rule_based_evidence_assessment_v1")
                )
                self.db.add(ass_obj)
                metrics["assessments_created"] += 1
            else:
                existing_ass.status = p_status
                existing_ass.confidence_score = float(a.get("confidence", 0.0))
                existing_ass.explanation = a.get("explanation", "")
                existing_ass.evidence_citations = a.get("evidence_ids", [])
                existing_ass.source_tiers = a.get("source_tiers", [])

        self.db.commit()
        logger.info(f"Assessments committed: {metrics['assessments_created']} records.")


def run_manifesto_promise_ingestion() -> Dict[str, Any]:
    """Canonical entrypoint function for pipeline execution."""
    db = SessionLocal()
    try:
        ingestor = ManifestoPromiseIngestor(db_session=db)
        return ingestor.ingest_all()
    finally:
        db.close()


if __name__ == "__main__":
    metrics = run_manifesto_promise_ingestion()
    print("Ingestion Summary Metrics:")
    for k, v in metrics.items():
        if isinstance(v, Counter):
            print(f"  {k}: {dict(v)}")
        else:
            print(f"  {k}: {v}")
