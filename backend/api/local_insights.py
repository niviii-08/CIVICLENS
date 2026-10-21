"""
CIVICLENS TN — Phase 13.6: District & Constituency Civic Insights REST API Blueprint.

Provides citizen-accessible endpoints for exploring comparable local civic data:
  - GET /api/local-insights/geographies
  - GET /api/local-insights/metrics
  - GET /api/local-insights/profile/<entity_type>/<entity_id>
  - POST /api/local-insights/compare
  - GET /api/local-insights/compare

Strict Epistemic & Methodological Guardrails:
  1. No arbitrary composite rankings: only single-metric sorting with explicit formulas and limitation disclosures.
  2. Zero vs missing non-conflation: unavailable data is never reported as zero activity.
  3. Strict unit and period compatibility: mismatched units or periods are rejected.
  4. Demographic & boundary disclosures: urban-rural skews and district bifurcations are actively surfaced.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from flask import Blueprint, request

from backend.api.responses import error_response, success_response
from backend.services.local_civic_comparison_service import (
    LocalCivicComparisonService,
    LocalInsightError,
    IncompatibleUnitError,
    IncompatiblePeriodError,
    IncompatibleGeographicLevelError,
    ArbitraryScoringProhibitedError,
    EntityNotFoundError,
)

logger = logging.getLogger("civiclens.phase13.api.local_insights")

local_insights_bp = Blueprint("local_insights", __name__, url_prefix="/local-insights")


@local_insights_bp.route("/geographies", methods=["GET"])
def list_supported_geographies():
    """
    List verified project geographic entities (districts, constituencies, wards).
    Query parameter:
      - level: optional ('DISTRICT', 'CONSTITUENCY', 'WARD')
    """
    level = request.args.get("level")
    service = LocalCivicComparisonService()
    try:
        data = service.get_supported_geographies(level=level)
        return success_response(
            data=data,
            message="Verified project geographies retrieved successfully",
        )
    except Exception as exc:
        logger.error(f"Error retrieving geographies: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving geographies: {exc}", status_code=500)


@local_insights_bp.route("/metrics", methods=["GET"])
def list_supported_metrics():
    """
    List verified comparable metrics, measurement units, reporting periods, and calculation formulas.
    Query parameter:
      - level: optional ('DISTRICT', 'CONSTITUENCY', 'WARD')
    """
    level = request.args.get("level")
    service = LocalCivicComparisonService()
    try:
        metrics = service.get_supported_metrics(level=level)
        return success_response(
            data={"metrics": metrics, "total_supported_metrics": len(metrics)},
            message="Supported comparable civic metrics retrieved successfully",
        )
    except Exception as exc:
        logger.error(f"Error retrieving metrics: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving metrics: {exc}", status_code=500)


@local_insights_bp.route("/profile/<string:entity_type>/<string:entity_id>", methods=["GET"])
def get_geographic_profile(entity_type: str, entity_id: str):
    """
    Retrieve profile, demographic context, and available verified indicators for a local entity.
    """
    service = LocalCivicComparisonService()
    try:
        profile = service.get_geographic_profile(entity_type=entity_type, entity_id=entity_id)
        return success_response(
            data=profile,
            message=f"Geographic profile for {entity_type} '{entity_id}' retrieved successfully",
        )
    except EntityNotFoundError as enf:
        logger.warning(f"Entity not found: {enf}")
        return error_response(str(enf), status_code=404)
    except IncompatibleGeographicLevelError as ige:
        logger.warning(f"Invalid level: {ige}")
        return error_response(str(ige), status_code=400)
    except Exception as exc:
        logger.error(f"Unexpected error retrieving profile: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving profile: {exc}", status_code=500)


@local_insights_bp.route("/compare", methods=["POST", "GET"])
def compare_local_civic_entities():
    """
    Compare 2 or more districts, constituencies, or wards on a verified metric.

    POST JSON payload:
      - entity_type: 'DISTRICT', 'CONSTITUENCY', or 'WARD'
      - entity_ids: list of entity IDs/codes (min 2)
      - metric_id: identifier of verified metric
      - reporting_period: optional reference timeframe
      - rank_by: optional single metric to sort by

    GET query parameters:
      - entity_type: 'DISTRICT', 'CONSTITUENCY', or 'WARD'
      - entities: comma-separated list of IDs
      - metric_id: identifier of verified metric
      - reporting_period: optional reference timeframe
      - rank_by: optional single metric to sort by
    """
    if request.method == "POST":
        payload = request.get_json() or {}
        entity_type = payload.get("entity_type")
        entity_ids = payload.get("entity_ids", [])
        metric_id = payload.get("metric_id")
        reporting_period = payload.get("reporting_period")
        rank_by = payload.get("rank_by")
    else:
        entity_type = request.args.get("entity_type")
        entities_str = request.args.get("entities", "")
        entity_ids = [e.strip() for e in entities_str.split(",") if e.strip()]
        metric_id = request.args.get("metric_id") or request.args.get("metric")
        reporting_period = request.args.get("reporting_period") or request.args.get("period")
        rank_by = request.args.get("rank_by")

    if not entity_type:
        return error_response("Missing required parameter 'entity_type' (e.g. 'DISTRICT', 'CONSTITUENCY', 'WARD').", status_code=400)
    if not entity_ids or len(entity_ids) < 2:
        return error_response("At least 2 entity identifiers are required for comparison.", status_code=400)
    if not metric_id:
        return error_response("Missing required parameter 'metric_id' (e.g. 'literacy_rate_pct', 'mplads_utilization_pct').", status_code=400)

    service = LocalCivicComparisonService()
    try:
        comparison_result = service.compare_entities(
            entity_type=entity_type,
            entity_ids=entity_ids,
            metric_id=metric_id,
            reporting_period=reporting_period,
            rank_by=rank_by,
        )
        return success_response(
            data=comparison_result,
            message="Local civic comparison generated successfully",
        )
    except EntityNotFoundError as enf:
        logger.warning(f"Comparison entity not found: {enf}")
        return error_response(str(enf), status_code=404)
    except ArbitraryScoringProhibitedError as asp:
        logger.warning(f"Arbitrary ranking prohibited: {asp}")
        return error_response(str(asp), status_code=400)
    except (IncompatibleGeographicLevelError, IncompatibleUnitError, IncompatiblePeriodError, LocalInsightError) as lie:
        logger.warning(f"Comparison compatibility error: {lie}")
        return error_response(str(lie), status_code=400)
    except Exception as exc:
        logger.error(f"Unexpected error in compare_local_civic_entities: {exc}", exc_info=True)
        return error_response(f"Internal error executing local comparison: {exc}", status_code=500)
