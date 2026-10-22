"""
CIVICLENS TN — Dataset Freshness & Ingestion Health REST API
============================================================
Provides public and administrative endpoints exposing data freshness,
monitoring statuses, citizen-facing labels, and failure diagnostics.
"""

from flask import Blueprint, jsonify, request
from backend.api.responses import success_response, error_response
from backend.ops.freshness_manager import DatasetFreshnessManager

freshness_bp = Blueprint("freshness", __name__, url_prefix="/freshness")

# Shared singleton instance
_freshness_manager = DatasetFreshnessManager()


@freshness_bp.route("", methods=["GET"])
def get_freshness_overview():
    """
    Returns system-wide dataset freshness summary across all 22 verified sources.
    Includes citizen-facing data freshness labels, publication cadences, and health states.
    """
    summary = _freshness_manager.assess_all_sources()
    return success_response(
        data=summary,
        message="Dataset freshness and health overview retrieved successfully."
    )


@freshness_bp.route("/<source_id>", methods=["GET"])
def get_source_freshness(source_id: str):
    """
    Returns granular freshness report and provenance for a single verified source.
    """
    try:
        report = _freshness_manager.assess_source_freshness(source_id.strip().upper())
        return success_response(
            data=report.to_dict(),
            message=f"Freshness details for source '{source_id}' retrieved successfully."
        )
    except ValueError as e:
        return error_response(
            message=str(e),
            status_code=404
        )


@freshness_bp.route("/diagnostics", methods=["GET"])
def get_health_diagnostics():
    """
    Returns diagnostics for any degraded, failed, or stale datasets.
    Zero sensitive credentials or tokens exposed.
    """
    all_data = _freshness_manager.assess_all_sources()
    flagged = [
        s for s in all_data["sources"]
        if s["health_status"] in ("DEGRADED", "FAILED", "STALE") or s["last_error"] is not None
    ]
    return success_response(
        data={
            "flagged_sources_count": len(flagged),
            "flagged_sources": flagged
        },
        message="Ingestion health diagnostics retrieved."
    )
