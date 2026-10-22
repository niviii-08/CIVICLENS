"""
Cross-Phase Record Integration API Blueprint for CIVICLENS TN.

Provides unified citizen endpoints:
  - GET /api/integration/related/<record_type>/<record_id>
  - GET /api/integration/matrix
  - GET /api/integration/journeys
"""

import logging
from flask import Blueprint, request
from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.services.cross_phase_integration_service import (
    CrossPhaseIntegrationService,
    CONN_DIRECT,
    CONN_EVIDENCE,
    CONN_INFERRED
)

logger = logging.getLogger("civiclens.api.integration")

integration_bp = Blueprint("integration", __name__, url_prefix="/integration")


def get_db():
    return SessionLocal()


# -------------------------------------------------------------------
# CROSS-PHASE INTEGRATION AUDIT MATRIX (Phase 11.9 Requirement 1)
# -------------------------------------------------------------------
INTEGRATION_MATRIX = [
    {
        "source_record_type": "Government Scheme (Phase 2)",
        "related_record_type": "Policy Evaluation (Phase 10)",
        "relationship_source": "Canonical Scheme Code & Foreign Key (PolicyRegistryEntry.canonical_scheme_code)",
        "api_support": "GET /api/policy-evaluation/policies?scheme_id=...",
        "validation_requirements": "Exact code match or validated alias; causal claim restriction enforced.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Government Scheme (Phase 2)",
        "related_record_type": "Manifesto Promise (Phase 3)",
        "relationship_source": "Junction Table (PromiseSchemeLink) & Statutory Order Citations",
        "api_support": "GET /api/promises/<promise_id>/scheme-matches",
        "validation_requirements": "Deterministic ID link or similarity score >= 0.85 with candidate caveat.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Manifesto Promise (Phase 3)",
        "related_record_type": "Elected Representative (Phase 6)",
        "relationship_source": "Junction Table (PromisePerformanceLink) & Party Sponsorship",
        "api_support": "GET /api/representatives/<representative_id>/promises",
        "validation_requirements": "Electoral term synchronization; no single-person causation inferred.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Public Claim (Phase 7)",
        "related_record_type": "Government Scheme (Phase 2)",
        "relationship_source": "Junction Table (ClaimCrossPhaseLink) & Statutory Evidence Citations",
        "api_support": "GET /api/claims/<claim_id>/cross-phase",
        "validation_requirements": "Verifiable proposition decomposition and atomic source tier >= TIER_2.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Civic Issue (Phase 8)",
        "related_record_type": "Elected Representative (Phase 6)",
        "relationship_source": "Delimitation & Administrative Boundary Mapping (Ward to AC)",
        "api_support": "GET /api/civic/issues/<issue_id>/cross-phase",
        "validation_requirements": "Strict citizen PII redaction; spatial co-occurrence does not imply individual negligence.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Civic Issue (Phase 8)",
        "related_record_type": "Government Scheme (Phase 2)",
        "relationship_source": "Departmental Work Order & Remediation Funding (CivicCrossPhaseLink)",
        "api_support": "GET /api/civic/issues/<issue_id>/cross-phase",
        "validation_requirements": "Confirmed public work voucher or municipal budget line.",
        "status": "IMPLEMENTED_VERIFIED"
    },
    {
        "source_record_type": "Evidence Graph Node (Phase 9)",
        "related_record_type": "All Entities (Phases 1-10)",
        "relationship_source": "First-Class Graph Edge (CivicEvidenceEdge) & Candidate Proposals",
        "api_support": "GET /api/graph/nodes/<node_id>/connected-entities",
        "validation_requirements": "Confidence score >= 0.8 for verified edges; automated proposals flagged as inferred.",
        "status": "IMPLEMENTED_VERIFIED"
    }
]

# -------------------------------------------------------------------
# CANONICAL CROSS-PHASE CITIZEN JOURNEYS (Phase 11.9 Requirement 3)
# -------------------------------------------------------------------
SUPPORTED_JOURNEYS = [
    {
        "journey_id": "journey-1-scheme-to-policy",
        "title": "Government Scheme → Policy Evaluation → Published Outcome Evidence",
        "start_route": "/schemes/SCH-SW-KMUT",
        "step_1": "Explore Kalaignar Magalir Urimai Thittam (KMUT) welfare rules and DBT budget disbursements.",
        "step_2": "Follow direct canonical link to Policy Evaluation (POL-TN-KMUT) conducted by TN State Planning Commission.",
        "step_3": "Inspect verified household expenditure impact evidence and female autonomy outcomes in the Evidence Panel."
    },
    {
        "journey_id": "journey-2-promise-to-implementation",
        "title": "Manifesto Promise → Implementation Activity → Supporting/Conflicting Sources",
        "start_route": "/promises/PRM-DMK-2021-001",
        "step_1": "Read DMK 2021 Manifesto Promise #14 for women head of household income entitlement.",
        "step_2": "Open connected government scheme (SCH-SW-KMUT) initiated under G.O. Ms No. 41.",
        "step_3": "Compare statutory bank credit logs against initial manifesto pledges to verify full delivery."
    },
    {
        "journey_id": "journey-3-claim-to-verification",
        "title": "Public Claim → Verification Assessment → Original Source Documents",
        "start_route": "/claims/CLM-TN-2024-001",
        "step_1": "View audited claim analyzing 1.15+ Crore beneficiary count assertion.",
        "step_2": "Examine atomic propositions tested against treasury disbursal statements.",
        "step_3": "Access primary gazette notifications and bank disbursal certificates in Source Explorer."
    },
    {
        "journey_id": "journey-4-civic-to-resolution",
        "title": "Civic Issue → Department Response → Available Resolution Evidence",
        "start_route": "/civic/CIV-2024-0891",
        "step_1": "Inspect drinking water grievance in Kolathur (Ward 64) with citizen privacy strictly masked.",
        "step_2": "Track CMWSSB department pipeline relaying completed within statutory SLA.",
        "step_3": "Open connected representative profile (Kolathur MLA) and Singara Chennai 2.0 remediation work order."
    },
    {
        "journey_id": "journey-5-representative-to-records",
        "title": "Representative → Relevant Public Records → Source Documents",
        "start_route": "/representatives/REP-AC-139",
        "step_1": "View Kolathur MLA profile with assembly attendance and MLACDS expenditure metrics.",
        "step_2": "Navigate connected constituency works, local water grievances, and party manifesto commitments.",
        "step_3": "Verify records against Legislative Assembly Debates and District Collectorate audit files."
    },
    {
        "journey_id": "journey-6-funding-to-promises",
        "title": "Political Funding / News → Relevant Public Records",
        "start_route": "/promises/PRM-DMK-2021-003",
        "step_1": "Inspect electoral VAT reduction commitments and statutory budget execution.",
        "step_2": "Follow evidence conflict linking to CAG Audit reports detailing ₹3/L execution vs ₹5/L pledge.",
        "step_3": "Review verified news articles contextualizing legislative budget debates."
    }
]


@integration_bp.route("/related/<record_type>/<record_id>", methods=["GET"])
def get_related_records(record_type: str, record_id: str):
    """
    Returns verified and candidate cross-phase relationships for any civic record.
    Supports schemes, promises, representatives, claims, civic issues, and policy evaluations.

    Query parameters:
      - include_inferred: 'true' | 'false' (default: 'true')
      - limit: int (default: 20, max: 50)
    """
    clean_type = record_type.strip().lower()
    clean_id = record_id.strip()

    if not clean_id or not clean_type:
        return error_response(
            message="Both record_type and record_id are required.",
            status_code=400
        )

    include_inferred = request.args.get("include_inferred", "true").lower() in ("true", "1", "yes")
    
    try:
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return error_response(message="Invalid limit parameter. Must be an integer.", status_code=400)

    db: Session = get_db()
    try:
        result = CrossPhaseIntegrationService.get_related_records(
            db=db,
            record_type=clean_type,
            record_id=clean_id,
            include_inferred=include_inferred,
            limit=limit,
            user_role="citizen"
        )

        return success_response(
            data=result,
            message=f"Cross-phase relationships for {clean_type} '{clean_id}' retrieved successfully."
        )
    except Exception as e:
        logger.error(f"Error fetching related records for {clean_type}/{clean_id}: {e}", exc_info=True)
        return error_response(
            message="Unable to retrieve cross-phase relationships due to an internal service error.",
            error_details=str(e),
            status_code=500
        )
    finally:
        db.close()


@integration_bp.route("/matrix", methods=["GET"])
def get_integration_matrix():
    """
    Returns the system-wide cross-phase integration matrix documenting
    supported relationship sources, API endpoints, and validation requirements.
    """
    return success_response(
        data={
            "matrix": INTEGRATION_MATRIX,
            "total_supported_crossings": len(INTEGRATION_MATRIX)
        },
        message="Cross-phase integration matrix retrieved successfully."
    )


@integration_bp.route("/journeys", methods=["GET"])
def get_supported_journeys():
    """
    Returns the canonical citizen navigation journeys supported across CIVICLENS TN.
    """
    return success_response(
        data={
            "journeys": SUPPORTED_JOURNEYS,
            "total_journeys": len(SUPPORTED_JOURNEYS)
        },
        message="Supported cross-phase citizen journeys retrieved successfully."
    )


# -------------------------------------------------------------------
# PHASE 13 CROSS-MODULE CIVIC INTELLIGENCE ENDPOINTS
# -------------------------------------------------------------------

@integration_bp.route("/cross-module/<record_type>/<record_id>", methods=["GET"])
def get_cross_module_intelligence(record_type: str, record_id: str):
    """
    Phase 13.9: Returns unified 360-degree Civic Intelligence for any record:
      - Related Records (explicit vs inferred breakdown)
      - Evidence Timelines & Milestones
      - Geographic Insights & Administrative Profile
      - Public Reports & Export Links (JSON, CSV, MD, HTML)
      - Saved Record Tracking Payload & Live Status
      - Non-Causal Epistemic Guardrails & DPDPA 2023 Redaction
    """
    clean_type = record_type.strip().lower()
    clean_id = record_id.strip()

    if not clean_id or not clean_type:
        return error_response(
            message="Both record_type and record_id are required.",
            status_code=400
        )

    include_inferred = request.args.get("include_inferred", "true").lower() in ("true", "1", "yes")

    db: Session = get_db()
    try:
        data = CrossPhaseIntegrationService.get_cross_module_intelligence(
            db=db,
            record_type=clean_type,
            record_id=clean_id,
            include_inferred=include_inferred,
            user_role="citizen"
        )
        return success_response(
            data=data,
            message=f"Cross-module civic intelligence for {clean_type} '{clean_id}' generated successfully."
        )
    except Exception as e:
        logger.error(f"Error generating cross-module intelligence for {clean_type}/{clean_id}: {e}", exc_info=True)
        return error_response(
            message="Unable to generate cross-module civic intelligence due to an internal service error.",
            error_details=str(e),
            status_code=500
        )
    finally:
        db.close()


@integration_bp.route("/journeys/phase13", methods=["GET"])
def get_phase13_journeys():
    """
    Phase 13.9: Returns the 7 canonical cross-module citizen journeys
    connecting promises, schemes, budgets, claims, timelines, geographic
    comparisons, transparent reports, and saved tracking.
    """
    journeys = CrossPhaseIntegrationService.get_phase13_journeys()
    return success_response(
        data={
            "journeys": journeys,
            "total_journeys": len(journeys),
            "epistemic_notice": (
                "Each journey reflects documented statutory or evidentiary pathways. "
                "CivicLens TN enforces strict non-causal attribution across all modules."
            )
        },
        message="Phase 13 cross-module citizen journeys retrieved successfully."
    )


@integration_bp.route("/path", methods=["GET"])
def get_multi_hop_path():
    """
    Phase 13.9: Discovers traceable multi-hop connection paths between civic entities
    with cycle prevention and bounded search depth.

    Query parameters:
      - from_type (or source_type): string (required)
      - from_id (or source_id): string (required)
      - to_type (or target_type): string (optional)
      - to_id (or target_id): string (required)
      - max_hops: integer (default: 3, max: 5)
    """
    src_type = request.args.get("from_type") or request.args.get("source_type")
    src_id = request.args.get("from_id") or request.args.get("source_id")
    tgt_type = request.args.get("to_type") or request.args.get("target_type")
    tgt_id = request.args.get("to_id") or request.args.get("target_id")

    if not src_type or not src_id:
        return error_response(
            message="Source entity parameters ('from_type' and 'from_id') are required.",
            status_code=400
        )

    if not tgt_id:
        return error_response(
            message="Target entity identifier ('to_id' or 'target_id') is required.",
            status_code=400
        )

    try:
        max_hops = int(request.args.get("max_hops", 3))
    except ValueError:
        return error_response(message="Invalid max_hops parameter. Must be an integer.", status_code=400)

    db: Session = get_db()
    try:
        path_result = CrossPhaseIntegrationService.get_multi_hop_path(
            db=db,
            source_type=src_type,
            source_id=src_id,
            target_type=tgt_type,
            target_id=tgt_id,
            max_hops=max_hops
        )
        return success_response(
            data=path_result,
            message="Multi-hop relationship path search completed."
        )
    except Exception as e:
        logger.error(f"Error computing multi-hop path: {e}", exc_info=True)
        return error_response(
            message="Unable to compute multi-hop path due to an internal service error.",
            error_details=str(e),
            status_code=500
        )
    finally:
        db.close()
