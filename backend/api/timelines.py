"""
CIVICLENS TN — Phase 13.5: Evidence-Backed Civic Timelines REST API Blueprint.

Provides citizen-accessible endpoints for exploring chronological civic records:
  - GET /api/timelines/<entity_type>/<entity_id>
  - GET /api/timelines/journey/<journey_id>
  - GET /api/timelines

Strict Epistemic & Temporal Safeguards:
  1. Sequence is not causation: temporal order does not prove causal efficacy.
  2. Date semantics transparency: explicitly exposes event_date, publication_date, reporting_period, and indexed_at.
  3. No manufactured dates: undated items remain in unanchored_milestones.
  4. Traceability: links to source documents, gazettes, audit notes, and detail pages.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from flask import Blueprint, request

from backend.api.responses import error_response, success_response
from backend.services.civic_timeline_service import (
    CivicTimelineService,
    EPISTEMIC_SEQUENCE_NOT_CAUSATION,
    EPISTEMIC_DATE_SEMANTICS_NOTICE,
    EPISTEMIC_INFERRED_RELATIONSHIP_DISCLOSURE,
)

logger = logging.getLogger("civiclens.phase13.api.timelines")

timelines_bp = Blueprint("timelines", __name__, url_prefix="/timelines")


@timelines_bp.route("/<string:entity_type>/<string:entity_id>", methods=["GET"])
def get_entity_timeline(entity_type: str, entity_id: str):
    """
    Retrieve an evidence-backed chronological timeline for a specific civic record.

    Supported entity_types:
      - scheme (e.g., SCH-SW-KMUT, SCH-HE-PUDHUMAI-PENN)
      - promise (e.g., PRM-DMK-2021-001)
      - claim (e.g., CLM-TN-2024-001)
      - policy (e.g., POL-TN-KMUT)
      - civic_issue / civic (e.g., CIV-2024-0891)
      - journey (e.g., JOURNEY-1-SCHEME-TO-POLICY)
    """
    service = CivicTimelineService()
    try:
        timeline = service.get_timeline(entity_type=entity_type, entity_id=entity_id)
        if not timeline:
            return error_response(
                message=f"No timeline records found for {entity_type} '{entity_id}'.",
                status_code=404,
            )

        # Optional filter by date range if provided in query params
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        include_unanchored = request.args.get("include_unanchored", "true").lower() == "true"

        filtered_chronological = timeline.get("chronological_milestones", [])
        if start_date:
            filtered_chronological = [
                m for m in filtered_chronological
                if m.get("date_semantics", {}).get("primary_date", "") >= start_date
            ]
        if end_date:
            filtered_chronological = [
                m for m in filtered_chronological
                if m.get("date_semantics", {}).get("primary_date", "") <= end_date
            ]

        response_data = dict(timeline)
        response_data["chronological_milestones"] = filtered_chronological
        response_data["chronological_milestones_count"] = len(filtered_chronological)

        if not include_unanchored:
            response_data["unanchored_milestones"] = []
            response_data["unanchored_milestones_count"] = 0

        return success_response(
            data=response_data,
            message="Evidence-backed civic timeline retrieved successfully",
        )
    except ValueError as val_err:
        logger.warning(f"Validation or lookup error for timeline ({entity_type}/{entity_id}): {val_err}")
        return error_response(
            message=str(val_err),
            status_code=404,
        )
    except Exception as exc:
        logger.error(f"Unexpected error constructing timeline ({entity_type}/{entity_id}): {exc}", exc_info=True)
        return error_response(
            message=f"Internal error retrieving timeline for {entity_type} '{entity_id}'.",
            status_code=500,
        )


@timelines_bp.route("/journey/<string:journey_id>", methods=["GET"])
def get_journey_timeline(journey_id: str):
    """
    Retrieve an end-to-end civic journey timeline tracing a promise to statutory scheme,
    budget allocation, grievance tracking, and measured policy outcome.
    """
    return get_entity_timeline(entity_type="journey", entity_id=journey_id)


@timelines_bp.route("", methods=["GET"])
@timelines_bp.route("/", methods=["GET"])
def list_available_timelines():
    """
    List featured canonical timelines, supported entity types, and date semantics guidance.
    """
    featured = [
        {
            "timeline_id": "TL-SCHEME-SCH-SW-KMUT",
            "entity_type": "scheme",
            "entity_id": "SCH-SW-KMUT",
            "title": "Kalaignar Magalir Urimai Thittam (KMUT) — Lifecycle & Impact Timeline",
            "date_range": "2021-03-15 to 2024-03-15",
            "milestones_count": 8,
            "has_unanchored": True,
            "url": "/api/timelines/scheme/SCH-SW-KMUT",
        },
        {
            "timeline_id": "TL-PROMISE-PRM-DMK-2021-001",
            "entity_type": "promise",
            "entity_id": "PRM-DMK-2021-001",
            "title": "DMK 2021 Manifesto Promise #14 Traceability Timeline",
            "date_range": "2021-03-15 to 2024-03-15",
            "milestones_count": 8,
            "has_unanchored": True,
            "url": "/api/timelines/promise/PRM-DMK-2021-001",
        },
        {
            "timeline_id": "TL-CIVIC-CIV-2024-0891",
            "entity_type": "civic_issue",
            "entity_id": "CIV-2024-0891",
            "title": "Civic Grievance CIV-2024-0891 (CMWSSB Contamination Remediation)",
            "date_range": "2024-06-12 to 2024-06-25",
            "milestones_count": 4,
            "has_unanchored": False,
            "url": "/api/timelines/civic_issue/CIV-2024-0891",
        },
        {
            "timeline_id": "TL-CLAIM-CLM-TN-2024-001",
            "entity_type": "claim",
            "entity_id": "CLM-TN-2024-001",
            "title": "Public Claim Verification Timeline (1.15 Cr KMUT Beneficiaries)",
            "date_range": "2021-03-15 to 2024-03-15",
            "milestones_count": 8,
            "has_unanchored": True,
            "url": "/api/timelines/claim/CLM-TN-2024-001",
        },
        {
            "timeline_id": "TL-JOURNEY-JOURNEY-1-SCHEME-TO-POLICY",
            "entity_type": "journey",
            "entity_id": "JOURNEY-1-SCHEME-TO-POLICY",
            "title": "Citizen Journey: Manifesto Pledge -> Scheme -> Budget -> Outcome",
            "date_range": "2021-03-15 to 2024-03-15",
            "milestones_count": 8,
            "has_unanchored": True,
            "url": "/api/timelines/journey/JOURNEY-1-SCHEME-TO-POLICY",
        },
    ]

    return success_response(
        data={
            "featured_timelines": featured,
            "supported_entity_types": [
                "scheme",
                "promise",
                "claim",
                "policy",
                "civic_issue",
                "journey",
            ],
            "guardrails": {
                "causation_limitation": EPISTEMIC_SEQUENCE_NOT_CAUSATION,
                "date_semantics_notice": EPISTEMIC_DATE_SEMANTICS_NOTICE,
                "inferred_relationship_disclosure": EPISTEMIC_INFERRED_RELATIONSHIP_DISCLOSURE,
            },
        },
        message="Civic timeline index and guidelines retrieved successfully",
    )
