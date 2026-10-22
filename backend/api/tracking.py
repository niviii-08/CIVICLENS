"""
CIVICLENS TN — Phase 13.8: Saved Civic Tracking and Updates REST API Blueprint.

Provides citizen-accessible endpoints for managing local-first civic tracking:
  - GET  /api/tracking/types
  - POST /api/tracking/validate
  - POST /api/tracking/check-updates
  - GET  /api/tracking/item/<record_type>/<record_id>

Privacy & Security Architecture:
  - Zero-Knowledge Storage: Citizens track items locally in their browser without mandatory accounts.
  - Stateless Verification: Checks reference validity against live registries.
  - Deterministic Change Detection: Emits update alerts ONLY when real database state changes.
  - Graceful Deletions: Surfaces explicit archival notices when records are retired.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List
from flask import Blueprint, request

from backend.api.responses import error_response, success_response
from backend.services.saved_tracking_service import SavedCivicTrackingService

logger = logging.getLogger("civiclens.phase13.api.tracking")

tracking_bp = Blueprint("tracking", __name__, url_prefix="/tracking")


@tracking_bp.route("/types", methods=["GET"])
def get_supported_types():
    """Retrieve supported civic record types, privacy model, and notification infrastructure status."""
    service = SavedCivicTrackingService()
    try:
        data = service.get_supported_tracking_types()
        return success_response(
            data=data,
            message="Tracking types and privacy capabilities retrieved successfully",
        )
    except Exception as exc:
        logger.error(f"Error retrieving tracking types: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving tracking capabilities: {exc}", status_code=500)


@tracking_bp.route("/validate", methods=["POST"])
def validate_record():
    """
    Validates a single saved record or small batch of records.
    Payload:
      - record_type: 'promise', 'scheme', 'representative', 'claim', 'civic'
      - record_id: Identifier of the record
      OR:
      - items: List of {record_type, record_id}
    """
    payload = request.get_json(silent=True) or {}
    service = SavedCivicTrackingService()

    if "items" in payload:
        items = payload.get("items") or []
        resolved_items = [
            service.validate_and_resolve_record(
                record_type=it.get("record_type", ""),
                record_id=it.get("record_id", ""),
            )
            for it in items
        ]
        return success_response(
            data={"results": resolved_items, "count": len(resolved_items)},
            message="Batch records validated successfully",
        )

    record_type = payload.get("record_type")
    record_id = payload.get("record_id")
    if not record_type or not record_id:
        return error_response("Both 'record_type' and 'record_id' are required", status_code=400)

    try:
        resolved = service.validate_and_resolve_record(record_type=record_type, record_id=record_id)
        return success_response(data=resolved, message="Record validated successfully")
    except Exception as exc:
        logger.error(f"Error validating record: {exc}", exc_info=True)
        return error_response(f"Internal error validating record: {exc}", status_code=500)


@tracking_bp.route("/check-updates", methods=["POST"])
def check_updates():
    """
    Client-side sync endpoint for checking genuine updates across a user's saved items.
    Accepts:
      {
        "items": [
          {
            "record_type": "promise",
            "record_id": "PRM-DMK-2021-001",
            "last_known_status": "ANNOUNCED",
            "saved_at": "2023-01-01T00:00:00Z"
          }
        ]
      }
    """
    payload = request.get_json(silent=True) or {}
    items = payload.get("items", [])
    service = SavedCivicTrackingService()

    try:
        sync_result = service.batch_check_updates(items)
        return success_response(data=sync_result, message="Updates evaluated successfully")
    except Exception as exc:
        logger.error(f"Error evaluating updates: {exc}", exc_info=True)
        return error_response(f"Internal error checking updates: {exc}", status_code=500)


@tracking_bp.route("/item/<string:record_type>/<string:record_id>", methods=["GET"])
def get_tracked_item(record_type: str, record_id: str):
    """
    Retrieves live tracking card and status for an individual civic record.
    Optional query params:
      - last_known_status: for instantaneous change check
      - saved_at: timestamp when citizen originally tracked the item
    """
    service = SavedCivicTrackingService()
    last_known_status = request.args.get("last_known_status")
    saved_at = request.args.get("saved_at")

    try:
        eval_result = service.check_record_update(
            record_type=record_type,
            record_id=record_id,
            last_known_status=last_known_status,
            saved_at=saved_at,
        )
        return success_response(data=eval_result, message="Item tracking data retrieved successfully")
    except Exception as exc:
        logger.error(f"Error retrieving item tracking data: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving tracking data: {exc}", status_code=500)
