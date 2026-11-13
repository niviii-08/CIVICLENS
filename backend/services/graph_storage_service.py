"""

Evidence graph storage and relationship validation service.

Manages graph nodes, edges, provenance metadata, and relationship constraints

in the unified civic evidence store.

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

    CivicEdgeAuditRecord,

    GraphEntityType,

    GraphRelationshipType,

    MatchingMethod,

    GraphProvenanceStatus,

    GraphReviewStatus,

    EdgeOperationType,

)

from backend.models.entity_registry import CanonicalEntity

logger = logging.getLogger("civiclens.phase9.graph_storage")

class GraphStorageError(Exception):

    """Base exception for evidence graph storage operations."""

    pass

class NodeNotFoundError(GraphStorageError):

    """Raised when a referenced source or target node does not exist."""

    pass

class InvalidEvidenceError(GraphStorageError):

    """Raised when an edge lacks mandatory documentary evidence or source citation."""

    pass

class EpistemicRuleViolationError(GraphStorageError):

    """Raised when an edge violates civic knowledge integrity constraints."""

    pass

class DuplicateEdgeError(GraphStorageError):

    """Raised when an identical active edge already exists in strict mode."""

    pass

class GraphStorageService:

    """

    Manages persistence, validation, querying, and auditable mutation of the

    Civic Evidence Graph.

    """

    @staticmethod

    def create_or_get_node(

        session: Session,

        node_id: str,

        entity_type: GraphEntityType | str,

        canonical_id: str,

        label: str,

        label_ta: Optional[str] = None,

        source_phase: str = "PHASE_1",

        canonical_entity_id: Optional[str] = None,

        attributes: Optional[Dict[str, Any]] = None,

        is_test_fixture: bool = False,

    ) -> CivicGraphNode:

        """

        Creates a new graph node or returns existing node by node_id or (entity_type, canonical_id).

        Links to CanonicalEntity if canonical_entity_id is provided.

        """

        if isinstance(entity_type, str):

            entity_type = GraphEntityType(entity_type)

        existing = session.query(CivicGraphNode).filter(CivicGraphNode.node_id == node_id).first()

        if existing:

            if canonical_entity_id and not existing.canonical_entity_id:

                existing.canonical_entity_id = canonical_entity_id

                session.flush()

            return existing

        existing_by_tuple = session.query(CivicGraphNode).filter(

            CivicGraphNode.entity_type == entity_type,

            CivicGraphNode.canonical_id == canonical_id,

        ).first()

        if existing_by_tuple:

            if canonical_entity_id and not existing_by_tuple.canonical_entity_id:

                existing_by_tuple.canonical_entity_id = canonical_entity_id

                session.flush()

            return existing_by_tuple

        if canonical_entity_id:

            canon = session.query(CanonicalEntity).filter(CanonicalEntity.entity_id == canonical_entity_id).first()

            if not canon:

                logger.warning(

                    f"Canonical entity {canonical_entity_id} not found in registry during node creation {node_id}"

                )

        node = CivicGraphNode(

            node_id=node_id,

            entity_type=entity_type,

            canonical_id=canonical_id,

            canonical_entity_id=canonical_entity_id,

            label=label,

            label_ta=label_ta,

            source_phase=source_phase,

            attributes_json=attributes or {},

            is_test_fixture=is_test_fixture,

        )

        session.add(node)

        session.flush()

        return node

    @staticmethod

    def get_node(session: Session, node_id: str) -> Optional[CivicGraphNode]:

        """Fetch node by node_id."""

        return session.query(CivicGraphNode).filter(CivicGraphNode.node_id == node_id).first()

    @staticmethod

    def link_node_to_canonical_entity(

        session: Session,

        node_id: str,

        canonical_entity_id: str,

    ) -> CivicGraphNode:

        """

        Explicitly establishes a link between a graph node and a canonical registry entity.

        """

        node = session.query(CivicGraphNode).filter(CivicGraphNode.node_id == node_id).first()

        if not node:

            raise NodeNotFoundError(f"Node '{node_id}' does not exist.")

        node.canonical_entity_id = canonical_entity_id

        session.flush()

        return node

    @staticmethod

    def validate_relationship(

        source_node: CivicGraphNode,

        target_node: CivicGraphNode,

        relationship_type: GraphRelationshipType,

        evidence_reference: Optional[str] = None,

        source_document_id: Optional[str] = None,

        matching_method: MatchingMethod = MatchingMethod.DIRECT_DOCUMENTARY,

        confidence_score: float = 1.0,

        review_status: GraphReviewStatus = GraphReviewStatus.PENDING_REVIEW,

        properties: Optional[Dict[str, Any]] = None,

        epistemic_notes: Optional[str] = None,

    ) -> None:

        """

        Enforces epistemic validation rules and referential integrity before edge creation:

        - Rejects self-loops without justification.

        - Requires evidence reference or source document citation.

        - Rule 1: A response relates to a civic issue only when supported by a source or reviewed matching decision.

        - Rule 2: A promise relates to a scheme without automatically proving the promise was fulfilled.

        - Rule 3: A funding disclosure relates to a party or donor only when identity match is supported.

        - Rule 4: A claim can have supporting and contradicting evidence simultaneously.

        - Rule 5: A civic issue's geographic association does not establish an individual representative's responsibility.

        """

        props = properties or {}

        if source_node.node_id == target_node.node_id:

            raise EpistemicRuleViolationError(

                f"Self-referential edge on '{source_node.node_id}' is not permitted in civic intelligence graph."

            )

        has_evidence = bool(evidence_reference and str(evidence_reference).strip())

        has_source_doc = bool(source_document_id and str(source_document_id).strip())

        if not (has_evidence or has_source_doc):

            raise InvalidEvidenceError(

                f"Edge from '{source_node.node_id}' to '{target_node.node_id}' lacks mandatory evidence "

                f"reference or source document citation. Pure unbacked edges are strictly prohibited."

            )

        src_type = source_node.entity_type

        tgt_type = target_node.entity_type

        is_response_src = src_type in (GraphEntityType.RESPONSE_RECORD, GraphEntityType.RESOLUTION_EVIDENCE)

        is_issue_tgt = tgt_type in (GraphEntityType.CIVIC_ISSUE, GraphEntityType.GRIEVANCE_RECORD)

        is_issue_src = src_type in (GraphEntityType.CIVIC_ISSUE, GraphEntityType.GRIEVANCE_RECORD)

        is_response_tgt = tgt_type in (GraphEntityType.RESPONSE_RECORD, GraphEntityType.RESOLUTION_EVIDENCE)

        if (is_response_src and is_issue_tgt) or (is_issue_src and is_response_tgt):

            is_reviewed = review_status == GraphReviewStatus.VERIFIED or matching_method == MatchingMethod.HUMAN_REVIEWED

            is_direct_doc = matching_method == MatchingMethod.DIRECT_DOCUMENTARY and has_source_doc

            if not (is_reviewed or is_direct_doc):

                raise EpistemicRuleViolationError(

                    f"A response ({source_node.node_id}) can relate to a civic issue ({target_node.node_id}) "

                    f"only when supported by an official source document or a verified human-reviewed matching decision. "

                    f"Automated candidate matches without documentary proof or review are rejected."

                )

        is_promise = src_type == GraphEntityType.POLITICAL_PROMISE

        is_scheme = tgt_type in (GraphEntityType.BUDGET_SCHEME, GraphEntityType.HISTORICAL_SCHEME)

        if is_promise and is_scheme:

            if relationship_type in (GraphRelationshipType.IMPLEMENTS, GraphRelationshipType.PROVIDES_EVIDENCE_FOR):

                has_fulfillment_proof = (

                    props.get("proof_of_fulfillment") is True

                    or bool(props.get("government_order_number"))

                    or bool(props.get("expenditure_verified"))

                )

                if not has_fulfillment_proof:

                    raise EpistemicRuleViolationError(

                        f"Political promise '{source_node.node_id}' can relate to scheme '{target_node.node_id}' "

                        f"via 'relates_to' or 'contextualizes', but cannot be asserted as '{relationship_type.value}' "

                        f"(fulfillment) without direct documentary proof of implementation (e.g., official Government Order, "

                        f"audited expenditure line item). A promise relating to a scheme does not prove fulfillment."

                    )

        is_funding_node = src_type in (

            GraphEntityType.CONTRIBUTION,

            GraphEntityType.FINANCIAL_DOCUMENT,

            GraphEntityType.ELECTION_EXPENDITURE,

            GraphEntityType.ELECTORAL_TRUST,

            GraphEntityType.DONOR,

        )

        is_recipient_party = tgt_type in (

            GraphEntityType.POLITICAL_PARTY,

            GraphEntityType.DONOR,

            GraphEntityType.POLITICAL_PERSON,

            GraphEntityType.REPRESENTATIVE,

        )

        if is_funding_node and is_recipient_party:

            if props.get("unsupported_match") is True:

                raise EpistemicRuleViolationError(

                    f"Funding disclosure link between '{source_node.node_id}' and '{target_node.node_id}' "

                    f"is explicitly flagged as unsupported match."

                )

            if matching_method == MatchingMethod.AUTOMATED_CANDIDATE:

                if confidence_score < 0.70 and review_status != GraphReviewStatus.VERIFIED:

                    raise EpistemicRuleViolationError(

                        f"Funding disclosure identity match between '{source_node.node_id}' and '{target_node.node_id}' "

                        f"has insufficient confidence ({confidence_score:.2f} < 0.70) without verified review status."

                    )

        is_issue = src_type in (GraphEntityType.CIVIC_ISSUE, GraphEntityType.GRIEVANCE_RECORD)

        is_representative = tgt_type == GraphEntityType.REPRESENTATIVE

        if is_issue and is_representative:

            if relationship_type == GraphRelationshipType.LOCATED_IN:

                raise EpistemicRuleViolationError(

                    f"A civic issue ({source_node.node_id}) cannot have relationship 'located_in' directly "

                    f"to an individual representative ({target_node.node_id}). Issues are located in "

                    f"constituencies or administrative areas; representatives represent areas."

                )

            if props.get("geographic_association_only") is True or props.get("attribution_basis") == "geographic_cooccurrence":

                raise EpistemicRuleViolationError(

                    f"A civic issue's geographic co-occurrence within a constituency does not establish "

                    f"individual representative '{target_node.node_id}'s responsibility. Personal attribution "

                    f"requires official assembly proceedings, grievance assignment, or reviewed documentary proof."

                )

    @classmethod

    def add_evidence_edge(

        cls,

        session: Session,

        source_node_id: str,

        target_node_id: str,

        relationship_type: GraphRelationshipType | str,

        evidence_reference: Optional[str] = None,

        source_document_id: Optional[str] = None,

        source_document_url: Optional[str] = None,

        source_document_hash: Optional[str] = None,

        matching_method: MatchingMethod | str = MatchingMethod.DIRECT_DOCUMENTARY,

        confidence_score: float = 1.0,

        review_status: GraphReviewStatus | str = GraphReviewStatus.PENDING_REVIEW,

        provenance_status: GraphProvenanceStatus | str = GraphProvenanceStatus.VALID,

        valid_from: Optional[str] = None,

        valid_to: Optional[str] = None,

        epistemic_notes: Optional[str] = None,

        properties: Optional[Dict[str, Any]] = None,

        is_test_fixture: bool = False,

        performed_by: str = "SYSTEM_INGEST",

    ) -> CivicEvidenceEdge:

        """

        Validates and persists a directed evidence edge.

        Idempotent: If an identical edge (source, target, rel_type, source_doc) already exists

        and is active, returns the existing edge without creating a duplicate.

        """

        if isinstance(relationship_type, str):

            relationship_type = GraphRelationshipType.from_string(relationship_type)

        if isinstance(matching_method, str):

            matching_method = MatchingMethod(matching_method)

        if isinstance(review_status, str):

            review_status = GraphReviewStatus(review_status)

        if isinstance(provenance_status, str):

            provenance_status = GraphProvenanceStatus(provenance_status)

        source_node = session.query(CivicGraphNode).filter(CivicGraphNode.node_id == source_node_id).first()

        if not source_node:

            raise NodeNotFoundError(f"Source graph node '{source_node_id}' does not exist.")

        target_node = session.query(CivicGraphNode).filter(CivicGraphNode.node_id == target_node_id).first()

        if not target_node:

            raise NodeNotFoundError(f"Target graph node '{target_node_id}' does not exist.")

        cls.validate_relationship(

            source_node=source_node,

            target_node=target_node,

            relationship_type=relationship_type,

            evidence_reference=evidence_reference,

            source_document_id=source_document_id,

            matching_method=matching_method,

            confidence_score=confidence_score,

            review_status=review_status,

            properties=properties,

            epistemic_notes=epistemic_notes,

        )

        existing_edge = session.query(CivicEvidenceEdge).filter(

            CivicEvidenceEdge.source_node_id == source_node_id,

            CivicEvidenceEdge.target_node_id == target_node_id,

            CivicEvidenceEdge.relationship_type == relationship_type,

            CivicEvidenceEdge.source_document_id == source_document_id,

        ).first()

        if existing_edge:

            if existing_edge.provenance_status == GraphProvenanceStatus.VALID:

                logger.info(

                    f"Repeatable import: active edge {existing_edge.edge_id} already exists. Returning existing edge."

                )

                return existing_edge

            elif existing_edge.provenance_status in (GraphProvenanceStatus.RETRACTED, GraphProvenanceStatus.SUPERSEDED):

                existing_edge.provenance_status = provenance_status

                existing_edge.evidence_reference = evidence_reference or existing_edge.evidence_reference

                existing_edge.matching_method = matching_method

                existing_edge.confidence_score = confidence_score

                existing_edge.valid_from = valid_from or existing_edge.valid_from

                existing_edge.valid_to = valid_to or existing_edge.valid_to

                session.flush()

                cls._record_edge_audit(

                    session=session,

                    edge_id=existing_edge.edge_id,

                    operation_type=EdgeOperationType.RESTORE if provenance_status == GraphProvenanceStatus.VALID else EdgeOperationType.UPDATE,

                    rationale="Edge re-imported and re-activated during repeatable ingestion.",

                    performed_by=performed_by,

                    new_state=existing_edge.to_dict(),

                )

                return existing_edge

        doc_part = (source_document_id or "NODOC").replace(":", "_").replace("/", "_")

        edge_id = f"EDGE:{relationship_type.value.upper()}:{source_node_id}:{target_node_id}:{doc_part}"

        if len(edge_id) > 115:

            edge_id = edge_id[:100] + "_" + uuid.uuid4().hex[:8]

        edge = CivicEvidenceEdge(

            edge_id=edge_id,

            source_node_id=source_node_id,

            target_node_id=target_node_id,

            relationship_type=relationship_type,

            evidence_reference=evidence_reference,

            source_document_id=source_document_id,

            source_document_url=source_document_url,

            source_document_hash=source_document_hash,

            matching_method=matching_method,

            confidence_score=confidence_score,

            review_status=review_status,

            provenance_status=provenance_status,

            valid_from=valid_from,

            valid_to=valid_to,

            epistemic_notes=epistemic_notes,

            properties_json=properties or {},

            is_test_fixture=is_test_fixture,

        )

        session.add(edge)

        session.flush()

        cls._record_edge_audit(

            session=session,

            edge_id=edge.edge_id,

            operation_type=EdgeOperationType.CREATE,

            rationale="Initial evidence edge insertion.",

            performed_by=performed_by,

            new_state=edge.to_dict(),

        )

        return edge

    @classmethod

    def retract_edge(

        cls,

        session: Session,

        edge_id: str,

        rationale: str,

        performed_by: str = "SYSTEM_AUDITOR",

    ) -> CivicEvidenceEdge:

        """

        Reversibly retracts an edge (soft-reversal).

        Does NOT delete the edge row from the database; retains provenance history.

        """

        edge = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id == edge_id).first()

        if not edge:

            raise GraphStorageError(f"Edge '{edge_id}' does not exist.")

        prev_state = edge.to_dict()

        edge.provenance_status = GraphProvenanceStatus.RETRACTED

        session.flush()

        cls._record_edge_audit(

            session=session,

            edge_id=edge.edge_id,

            operation_type=EdgeOperationType.RETRACT,

            rationale=rationale,

            performed_by=performed_by,

            prev_state=prev_state,

            new_state=edge.to_dict(),

        )

        return edge

    @classmethod

    def supersede_edge(

        cls,

        session: Session,

        old_edge_id: str,

        new_edge_id: str,

        rationale: str,

        performed_by: str = "SYSTEM_AUDITOR",

    ) -> CivicEvidenceEdge:

        """

        Reversibly supersedes an existing edge with a corrected/updated edge.

        """

        edge = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id == old_edge_id).first()

        if not edge:

            raise GraphStorageError(f"Edge '{old_edge_id}' does not exist.")

        prev_state = edge.to_dict()

        edge.provenance_status = GraphProvenanceStatus.SUPERSEDED

        if not edge.properties_json:

            edge.properties_json = {}

        edge.properties_json = {**edge.properties_json, "superseded_by": new_edge_id}

        session.flush()

        cls._record_edge_audit(

            session=session,

            edge_id=edge.edge_id,

            operation_type=EdgeOperationType.SUPERSEDE,

            rationale=f"Superseded by {new_edge_id}. Rationale: {rationale}",

            performed_by=performed_by,

            prev_state=prev_state,

            new_state=edge.to_dict(),

        )

        return edge

    @classmethod

    def restore_edge(

        cls,

        session: Session,

        edge_id: str,

        rationale: str,

        performed_by: str = "SYSTEM_AUDITOR",

    ) -> CivicEvidenceEdge:

        """

        Reverses a retraction, restoring the edge to VALID status.

        """

        edge = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id == edge_id).first()

        if not edge:

            raise GraphStorageError(f"Edge '{edge_id}' does not exist.")

        prev_state = edge.to_dict()

        edge.provenance_status = GraphProvenanceStatus.VALID

        session.flush()

        cls._record_edge_audit(

            session=session,

            edge_id=edge.edge_id,

            operation_type=EdgeOperationType.RESTORE,

            rationale=rationale,

            performed_by=performed_by,

            prev_state=prev_state,

            new_state=edge.to_dict(),

        )

        return edge

    @classmethod

    def correct_edge(

        cls,

        session: Session,

        edge_id: str,

        rationale: str,

        performed_by: str = "SYSTEM_AUDITOR",

        **updates: Any,

    ) -> CivicEvidenceEdge:

        """

        Reversibly modifies edge metadata (confidence, temporal validity, review_status, etc.)

        while logging the change in the immutable audit ledger.

        """

        edge = session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id == edge_id).first()

        if not edge:

            raise GraphStorageError(f"Edge '{edge_id}' does not exist.")

        prev_state = edge.to_dict()

        for key, val in updates.items():

            if hasattr(edge, key) and key not in ("edge_id", "source_node_id", "target_node_id"):

                setattr(edge, key, val)

        session.flush()

        cls._record_edge_audit(

            session=session,

            edge_id=edge.edge_id,

            operation_type=EdgeOperationType.CORRECT,

            rationale=rationale,

            performed_by=performed_by,

            prev_state=prev_state,

            new_state=edge.to_dict(),

        )

        return edge

    @staticmethod

    def get_edge(session: Session, edge_id: str) -> Optional[CivicEvidenceEdge]:

        """Fetch edge by edge_id."""

        return session.query(CivicEvidenceEdge).filter(CivicEvidenceEdge.edge_id == edge_id).first()

    @staticmethod

    def get_node_edges(

        session: Session,

        node_id: str,

        direction: str = "both",

        relationship_type: Optional[GraphRelationshipType | str] = None,

        active_only: bool = True,

    ) -> List[CivicEvidenceEdge]:

        """

        Retrieves edges connected to a node, with optional direction, relationship, and active filtering.

        """

        query = session.query(CivicEvidenceEdge)

        if direction == "outgoing":

            query = query.filter(CivicEvidenceEdge.source_node_id == node_id)

        elif direction == "incoming":

            query = query.filter(CivicEvidenceEdge.target_node_id == node_id)

        else:
            query = query.filter(

                or_(

                    CivicEvidenceEdge.source_node_id == node_id,

                    CivicEvidenceEdge.target_node_id == node_id,

                )

            )

        if relationship_type:

            if isinstance(relationship_type, str):

                relationship_type = GraphRelationshipType.from_string(relationship_type)

            query = query.filter(CivicEvidenceEdge.relationship_type == relationship_type)

        if active_only:

            query = query.filter(CivicEvidenceEdge.provenance_status == GraphProvenanceStatus.VALID)

        return query.all()

    @staticmethod

    def get_edge_audit_records(session: Session, edge_id: str) -> List[CivicEdgeAuditRecord]:

        """Fetch complete chronological audit history for an edge."""

        return (

            session.query(CivicEdgeAuditRecord)

            .filter(CivicEdgeAuditRecord.edge_id == edge_id)

            .order_by(CivicEdgeAuditRecord.timestamp.asc())

            .all()

        )

    @staticmethod

    def _record_edge_audit(

        session: Session,

        edge_id: str,

        operation_type: EdgeOperationType,

        rationale: str,

        performed_by: str,

        prev_state: Optional[Dict[str, Any]] = None,

        new_state: Optional[Dict[str, Any]] = None,

    ) -> CivicEdgeAuditRecord:

        """Internal helper to write immutable audit record."""

        audit_id = f"EDGE-AUDIT-{uuid.uuid4().hex[:12].upper()}"

        audit_record = CivicEdgeAuditRecord(

            audit_id=audit_id,

            operation_type=operation_type,

            edge_id=edge_id,

            rationale=rationale,

            performed_by=performed_by,

            previous_state_json=prev_state,

            new_state_json=new_state,

            timestamp=datetime.now(timezone.utc),

        )

        session.add(audit_record)

        session.flush()

        return audit_record

