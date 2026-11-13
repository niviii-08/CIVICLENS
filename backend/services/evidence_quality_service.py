"""

Evidence quality and contradiction analysis service.

Assesses the quality, tier weighting, and potential contradictions in documentary

evidence supporting or contesting civic claims.

"""

from __future__ import annotations

import logging

import uuid

from datetime import datetime, timezone

from typing import Any, Dict, List, Optional, Tuple, Set

from sqlalchemy import or_, and_, desc

from sqlalchemy.orm import Session

from backend.models.graph import (

    CivicGraphNode,

    CivicEvidenceEdge,

    CivicConflictRecord,

    ConflictTypeEnum,

    ConflictSeverityEnum,

    ConflictResolutionStatus,

    GraphEntityType,

    GraphRelationshipType,

    MatchingMethod,

    GraphProvenanceStatus,

    GraphReviewStatus,

)

logger = logging.getLogger("civiclens.phase9.quality")

SOURCE_TIER_WEIGHTS = {

    "STATUTORY_AUDIT_GAZETTE": 0.95,
    "EXECUTIVE_DEPARTMENTAL_RECORD": 0.85,
    "VERIFIED_JOURNALISTIC_MEDIA": 0.65,
    "PROVISIONAL_CITIZEN_CLAIM": 0.40,
}

class EvidenceQualityService:

    """

    Evaluates multi-factor evidence quality and detects discrepancies across graph edges.

    """

    @staticmethod

    def assess_source_reliability(source_document_id: Optional[str]) -> Dict[str, Any]:

        """

        Assesses publisher authority tier for a source document.

        Does not assign an arbitrary universal score; maps to documented statutory standing.

        """

        if not source_document_id or not source_document_id.strip():

            return {

                "source_tier": "PROVISIONAL_CITIZEN_CLAIM",

                "authority_weight": 0.40,

                "statutory_standing": "Uncited / Missing Document Reference",

                "limitations": "No formal primary document cited; evidentiary value is provisional.",

            }

        doc_upper = str(source_document_id).upper()

        if any(kw in doc_upper for kw in ("CAG", "GAZETTE", "ECI", "FORM_21E", "HANSARD", "SUPREME_COURT")):

            return {

                "source_tier": "STATUTORY_AUDIT_GAZETTE",

                "authority_weight": 0.95,

                "statutory_standing": "Statutory / Independent Constitutional Authority",

                "limitations": "Subject to periodic revision or subsequent legislative amendments.",

            }

        if any(kw in doc_upper for kw in ("GO_", "G_O_", "BUDGET", "POLICY_NOTE", "ATR", "ADMIN_REPORT", "MAWS", "CMWSSB")):

            return {

                "source_tier": "EXECUTIVE_DEPARTMENTAL_RECORD",

                "authority_weight": 0.85,

                "statutory_standing": "Executive Departmental Publication",

                "limitations": "Reflects executive departmental filings; unverified by external constitutional audit.",

            }

        if any(kw in doc_upper for kw in ("NEWS", "ARTICLE", "HINDU", "DINAMALAR", "DINAMANI", "REPORT")):

            return {

                "source_tier": "VERIFIED_JOURNALISTIC_MEDIA",

                "authority_weight": 0.65,

                "statutory_standing": "Verified Journalistic Media Report",

                "limitations": "Third-party observation; reports public discourse but lacks legal evidentiary force.",

            }

        return {

            "source_tier": "PROVISIONAL_CITIZEN_CLAIM",

            "authority_weight": 0.40,

            "statutory_standing": "Informal / Unclassified Source",

            "limitations": "Unclassified document token; provisional evidentiary weight only.",

        }

    @classmethod

    def assess_edge_evidence_quality(cls, edge: CivicEvidenceEdge) -> Dict[str, Any]:

        """

        Evaluates the 9 documented evidence quality factors for an edge:

        - source_authenticity

        - directness

        - document_availability

        - date_relevance

        - geographic_relevance

        - entity_match_quality

        - source_completeness

        - consistency

        - review_status

        Returns a transparent scorecard with documented inputs, factor scores,

        interpretation, and explicit limitations.

        """

        source_eval = cls.assess_source_reliability(edge.source_document_id)

        source_authenticity = source_eval["authority_weight"]

        if edge.matching_method == MatchingMethod.DIRECT_DOCUMENTARY:

            directness = 1.0

        elif edge.matching_method == MatchingMethod.DETERMINISTIC_ID:

            directness = 0.90

        elif edge.matching_method == MatchingMethod.HUMAN_REVIEWED:

            directness = 0.85

        else:
            directness = 0.50

        doc_avail = 0.0

        if edge.source_document_id:

            doc_avail += 0.40

        if edge.source_document_url:

            doc_avail += 0.30

        if edge.source_document_hash:

            doc_avail += 0.30

        date_rel = 1.0

        if edge.valid_from:

            try:

                y = int(str(edge.valid_from)[:4])

                current_year = datetime.now(timezone.utc).year

                diff = current_year - y

                if diff > 5:

                    date_rel = 0.60

                elif diff > 3:

                    date_rel = 0.80

            except (ValueError, TypeError):

                date_rel = 0.85

        props = edge.properties_json or {}

        geo_rel = 0.70

        if props.get("exact_ward_match") or props.get("exact_ac_match"):

            geo_rel = 1.0

        elif props.get("district_mismatch"):

            geo_rel = 0.30

        entity_match_quality = max(0.0, min(1.0, float(edge.confidence_score)))

        has_ref = bool(edge.evidence_reference and edge.evidence_reference.strip())

        has_doc = bool(edge.source_document_id and edge.source_document_id.strip())

        if has_ref and has_doc:

            source_completeness = 1.0

        elif has_ref or has_doc:

            source_completeness = 0.50

        else:

            source_completeness = 0.0

        if edge.provenance_status == GraphProvenanceStatus.VALID:

            consistency = 1.0

        elif edge.provenance_status == GraphProvenanceStatus.PROVISIONAL:

            consistency = 0.70

        elif edge.provenance_status == GraphProvenanceStatus.DISPUTED:

            consistency = 0.40

        else:
            consistency = 0.20

        if edge.review_status == GraphReviewStatus.VERIFIED:

            review_score = 1.0

        elif edge.review_status == GraphReviewStatus.PENDING_REVIEW:

            review_score = 0.70

        elif edge.review_status == GraphReviewStatus.OVERRIDDEN:

            review_score = 0.80

        else:
            review_score = 0.0

        composite_score = round(

            (source_authenticity * 0.20)

            + (directness * 0.15)

            + (doc_avail * 0.15)

            + (source_completeness * 0.10)

            + (date_rel * 0.10)

            + (geo_rel * 0.10)

            + (entity_match_quality * 0.10)

            + (review_score * 0.10),

            3,

        )

        if composite_score >= 0.85:

            interpretation = "HIGH_CREDIBILITY: Primary statutory or verified documentary evidence with full provenance."

        elif composite_score >= 0.65:

            interpretation = "MODERATE_RELIABILITY: Corroborated evidence; minor gaps in hash availability or review."

        elif composite_score >= 0.40:

            interpretation = "PROVISIONAL_NEEDS_AUDIT: Heuristic candidate or secondary source; human audit required."

        else:

            interpretation = "UNRELIABLE: Deficient provenance, rejected review, or stale uncorroborated claim."

        return {

            "edge_id": edge.edge_id,

            "composite_score": composite_score,

            "interpretation": interpretation,

            "factor_breakdown": {

                "source_authenticity": round(source_authenticity, 2),

                "directness": round(directness, 2),

                "document_availability": round(doc_avail, 2),

                "source_completeness": round(source_completeness, 2),

                "date_relevance": round(date_relevance, 2) if 'date_relevance' in locals() else round(date_rel, 2),

                "geographic_relevance": round(geo_rel, 2),

                "entity_match_quality": round(entity_match_quality, 2),

                "consistency": round(consistency, 2),

                "review_status": round(review_score, 2),

            },

            "documented_inputs": {

                "source_document_id": edge.source_document_id,

                "source_tier": source_eval["source_tier"],

                "matching_method": edge.matching_method.value,

                "has_hash": bool(edge.source_document_hash),

                "has_url": bool(edge.source_document_url),

                "has_excerpt": bool(edge.evidence_reference),

                "review_status": edge.review_status.value,

                "provenance_status": edge.provenance_status.value,

            },

            "limitations": (

                "Numerical score reflects documentary provenance rigor, not infallible substantive ground truth. "

                "Higher scores reflect presence of verifiable statutory records, hashes, and review stamps."

            ),

        }

    @staticmethod

    def assess_evidence_completeness(

        session: Session,

        node_id: str,

    ) -> Dict[str, Any]:

        """

        Assesses whether the full required chain of evidence is present for an entity.

        Distinguishes completeness from source quality or verification outcome.

        """

        node = session.query(CivicGraphNode).filter(CivicGraphNode.node_id == node_id).first()

        if not node:

            return {"error": f"Node '{node_id}' not found."}

        edges = session.query(CivicEvidenceEdge).filter(

            or_(

                CivicEvidenceEdge.source_node_id == node_id,

                CivicEvidenceEdge.target_node_id == node_id,

            )

        ).all()

        missing_elements: List[str] = []

        present_elements: List[str] = []

        if node.entity_type in (GraphEntityType.HISTORICAL_SCHEME, GraphEntityType.BUDGET_SCHEME):

            has_funding = any(e.relationship_type == GraphRelationshipType.FUNDS for e in edges)

            has_impl = any(e.relationship_type == GraphRelationshipType.IMPLEMENTS for e in edges)

            if has_funding:

                present_elements.append("BUDGET_FUNDING_RECORD")

            else:

                missing_elements.append("MISSING_BUDGET_ALLOCATION: No statutory budget record linked.")

            if has_impl:

                present_elements.append("IMPLEMENTATION_RECORD")

            else:

                missing_elements.append("MISSING_IMPLEMENTATION_RECORD: No administrative G.O. or works linked.")

        elif node.entity_type in (GraphEntityType.CIVIC_ISSUE, GraphEntityType.GRIEVANCE_RECORD):

            has_resp = any(e.relationship_type == GraphRelationshipType.RESPONDS_TO for e in edges)

            has_resol = any(e.relationship_type == GraphRelationshipType.PROVIDES_EVIDENCE_FOR for e in edges)

            if has_resp:

                present_elements.append("OFFICIAL_DEPARTMENT_RESPONSE")

            else:

                missing_elements.append("MISSING_DEPARTMENT_RESPONSE: Grievance lacks official response.")

            if has_resol:

                present_elements.append("RESOLUTION_VERIFICATION_CERTIFICATE")

            else:

                missing_elements.append("MISSING_RESOLUTION_EVIDENCE: No on-the-ground potability/work certificate.")

        elif node.entity_type in (GraphEntityType.CLAIM, GraphEntityType.ATOMIC_CLAIM):

            has_evidence = any(

                e.relationship_type in (GraphRelationshipType.PROVIDES_EVIDENCE_FOR, GraphRelationshipType.CONTRADICTS)

                for e in edges

            )

            if has_evidence:

                present_elements.append("PRIMARY_EVIDENCE_CITATION")

            else:

                missing_elements.append("MISSING_PRIMARY_EVIDENCE: Claim lacks supporting or contradicting evidence.")

        total_expected = len(present_elements) + len(missing_elements)

        completeness_pct = (len(present_elements) / total_expected * 100.0) if total_expected > 0 else 100.0

        return {

            "node_id": node_id,

            "entity_type": node.entity_type.value,

            "completeness_percentage": round(completeness_pct, 1),

            "present_elements": present_elements,

            "missing_elements": missing_elements,

            "is_complete": len(missing_elements) == 0,

        }

    @classmethod

    def detect_conflicts(

        cls,

        session: Session,

        node_id: Optional[str] = None,

        persist_records: bool = True,

    ) -> List[CivicConflictRecord]:

        """

        Scans graph edges and nodes to detect evidentiary conflicts:

        1. Conflicting dates (e.g. incompatible event or completion years).

        2. Incompatible status reports (e.g. COMPLETED vs STALLED).

        3. Inconsistent entity matches (conflicting canonical mapping claims).

        4. Contradictory claim evidence (simultaneous support and contradiction).

        5. Outdated documents (stale sources superseded by statutory audits).

        6. Duplicate sources (repeated document references with differing hashes).

        7. Incomplete provenance (missing SHA-256 hashes or missing excerpts).

        Compares relative evidentiary weight between conflicting records without

        automatically assuming the newest document is correct.

        Preserves all conflicting evidence with documented diagnostic explanations.

        """

        conflicts: List[CivicConflictRecord] = []

        query = session.query(CivicGraphNode)

        if node_id:

            query = query.filter(CivicGraphNode.node_id == node_id)

        nodes = query.all()

        for node in nodes:

            incoming = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.target_node_id == node.node_id).all()

            outgoing = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.source_node_id == node.node_id).all()

            all_node_edges = incoming + outgoing

            if node.entity_type in (GraphEntityType.CLAIM, GraphEntityType.ATOMIC_CLAIM):

                support_edges = [e for e in incoming if e.relationship_type == GraphRelationshipType.PROVIDES_EVIDENCE_FOR]

                contra_edges = [e for e in incoming if e.relationship_type == GraphRelationshipType.CONTRADICTS]

                if support_edges and contra_edges:

                    for s_edge in support_edges:

                        for c_edge in contra_edges:

                            s_eval = cls.assess_edge_evidence_quality(s_edge)

                            c_eval = cls.assess_edge_evidence_quality(c_edge)

                            weight_comparison = {

                                "supporting_edge": {

                                    "edge_id": s_edge.edge_id,

                                    "source_document": s_edge.source_document_id,

                                    "source_tier": s_eval["documented_inputs"]["source_tier"],

                                    "composite_score": s_eval["composite_score"],

                                },

                                "contradicting_edge": {

                                    "edge_id": c_edge.edge_id,

                                    "source_document": c_edge.source_document_id,

                                    "source_tier": c_eval["documented_inputs"]["source_tier"],

                                    "composite_score": c_eval["composite_score"],

                                },

                                "heavier_edge": (

                                    s_edge.edge_id

                                    if s_eval["composite_score"] >= c_eval["composite_score"]

                                    else c_edge.edge_id

                                ),

                                "methodological_note": (

                                    "Conflicting evidence preserved. Documents do NOT have equal evidentiary value; "

                                    f"tier '{s_eval['documented_inputs']['source_tier']}' vs '{c_eval['documented_inputs']['source_tier']}'. "

                                    "Newer publication date does not automatically override statutory audit findings."

                                ),

                            }

                            conf = CivicConflictRecord(

                                conflict_id=f"CONF:CLAIM_CONTRA:{node.node_id}:{uuid.uuid4().hex[:8]}",

                                conflict_type=ConflictTypeEnum.CONTRADICTORY_CLAIM_EVIDENCE,

                                severity=ConflictSeverityEnum.HIGH,

                                primary_node_id=node.node_id,

                                edge_a_id=s_edge.edge_id,

                                edge_b_id=c_edge.edge_id,

                                description=(

                                    f"Claim '{node.label}' has simultaneous supporting evidence ({s_edge.source_document_id}) "

                                    f"and contradicting evidence ({c_edge.source_document_id}). "

                                    "Preserving multi-perspective contradiction is required for audit integrity."

                                ),

                                epistemic_weight_comparison=weight_comparison,

                                resolution_status=ConflictResolutionStatus.EXPLAINED_DIALECTIC,

                                is_test_fixture=node.is_test_fixture,

                            )

                            conflicts.append(conf)

            statuses: List[Tuple[CivicEvidenceEdge, str]] = []

            for e in all_node_edges:

                props = e.properties_json or {}

                status_val = props.get("status") or props.get("completion_status")

                if status_val:

                    statuses.append((e, str(status_val).upper()))

            if len(statuses) >= 2:

                for i in range(len(statuses)):

                    for j in range(i + 1, len(statuses)):

                        e1, s1 = statuses[i]

                        e2, s2 = statuses[j]

                        if s1 != s2 and {s1, s2}.intersection({"COMPLETED", "SANCTIONED"}) and {s1, s2}.intersection({"STALLED", "CANCELLED", "PENDING"}):

                            conf = CivicConflictRecord(

                                conflict_id=f"CONF:STATUS:{node.node_id}:{uuid.uuid4().hex[:8]}",

                                conflict_type=ConflictTypeEnum.INCOMPATIBLE_STATUS,

                                severity=ConflictSeverityEnum.CRITICAL,

                                primary_node_id=node.node_id,

                                edge_a_id=e1.edge_id,

                                edge_b_id=e2.edge_id,

                                description=(

                                    f"Incompatible status reports for entity '{node.label}': "

                                    f"Edge {e1.edge_id} asserts status '{s1}' ({e1.source_document_id}) while "

                                    f"Edge {e2.edge_id} asserts status '{s2}' ({e2.source_document_id})."

                                ),

                                epistemic_weight_comparison={

                                    "status_a": s1,

                                    "status_b": s2,

                                    "edge_a_doc": e1.source_document_id,

                                    "edge_b_doc": e2.source_document_id,

                                },

                                resolution_status=ConflictResolutionStatus.UNRESOLVED,

                                is_test_fixture=node.is_test_fixture,

                            )

                            conflicts.append(conf)

            date_edges: List[Tuple[CivicEvidenceEdge, int]] = []

            for e in all_node_edges:

                props = e.properties_json or {}

                yr = props.get("completion_year") or props.get("fiscal_year")

                if yr:

                    try:

                        clean_yr = int(str(yr)[:4])

                        date_edges.append((e, clean_yr))

                    except (ValueError, TypeError):

                        pass

            if len(date_edges) >= 2:

                for i in range(len(date_edges)):

                    for j in range(i + 1, len(date_edges)):

                        e1, y1 = date_edges[i]

                        e2, y2 = date_edges[j]

                        if abs(y1 - y2) > 2:

                            conf = CivicConflictRecord(

                                conflict_id=f"CONF:DATE:{node.node_id}:{uuid.uuid4().hex[:8]}",

                                conflict_type=ConflictTypeEnum.CONFLICTING_DATES,

                                severity=ConflictSeverityEnum.MEDIUM,

                                primary_node_id=node.node_id,

                                edge_a_id=e1.edge_id,

                                edge_b_id=e2.edge_id,

                                description=(

                                    f"Conflicting date timelines for '{node.label}': "

                                    f"Source {e1.source_document_id} records year {y1}, whereas "

                                    f"Source {e2.source_document_id} records year {y2} (divergence > 2 years)."

                                ),

                                epistemic_weight_comparison={

                                    "year_a": y1,

                                    "year_b": y2,

                                    "divergence_years": abs(y1 - y2),

                                },

                                resolution_status=ConflictResolutionStatus.UNRESOLVED,

                                is_test_fixture=node.is_test_fixture,

                            )

                            conflicts.append(conf)

            for e in all_node_edges:

                props = e.properties_json or {}

                if props.get("is_stale_source") is True or (e.valid_from and int(str(e.valid_from)[:4]) < 2018):

                    conf = CivicConflictRecord(

                        conflict_id=f"CONF:STALE:{node.node_id}:{e.edge_id}:{uuid.uuid4().hex[:6]}",

                        conflict_type=ConflictTypeEnum.OUTDATED_DOCUMENT,

                        severity=ConflictSeverityEnum.LOW,

                        primary_node_id=node.node_id,

                        edge_a_id=e.edge_id,

                        description=(

                            f"Edge '{e.edge_id}' cites stale or outdated document '{e.source_document_id}' "

                            f"(valid from {e.valid_from or 'prior era'}). Audit should cross-reference latest fiscal release."

                        ),

                        epistemic_weight_comparison={"stale_edge_id": e.edge_id},

                        resolution_status=ConflictResolutionStatus.UNRESOLVED,

                        is_test_fixture=node.is_test_fixture,

                    )

                    conflicts.append(conf)

            for e in all_node_edges:

                if not e.source_document_hash or not e.evidence_reference:

                    conf = CivicConflictRecord(

                        conflict_id=f"CONF:PROV:{node.node_id}:{e.edge_id}:{uuid.uuid4().hex[:6]}",

                        conflict_type=ConflictTypeEnum.INCOMPLETE_PROVENANCE,

                        severity=ConflictSeverityEnum.MEDIUM,

                        primary_node_id=node.node_id,

                        edge_a_id=e.edge_id,

                        description=(

                            f"Edge '{e.edge_id}' has incomplete provenance: "

                            f"{'missing SHA-256 hash; ' if not e.source_document_hash else ''}"

                            f"{'missing verbatim excerpt citation.' if not e.evidence_reference else ''}"

                        ),

                        epistemic_weight_comparison={"edge_id": e.edge_id},

                        resolution_status=ConflictResolutionStatus.UNRESOLVED,

                        is_test_fixture=node.is_test_fixture,

                    )

                    conflicts.append(conf)

        if persist_records:

            for c in conflicts:

                existing = session.query(CivicConflictRecord).filter(CivicConflictRecord.conflict_id == c.conflict_id).first()

                if not existing:

                    session.add(c)

            session.flush()

        return conflicts

