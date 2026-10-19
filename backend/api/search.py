"""
Unified Search API Blueprint for CIVICLENS TN.

Provides GET /api/search for cross-phase citizen information discovery.
"""

import logging
from flask import Blueprint, request
from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.services.unified_search_service import search_unified, CATEGORY_CONFIG

logger = logging.getLogger("civiclens.api.search")

search_bp = Blueprint("search", __name__, url_prefix="/search")


def get_db():
    return SessionLocal()


@search_bp.route("", methods=["GET"], strict_slashes=False)
@search_bp.route("/", methods=["GET"], strict_slashes=False)
@search_bp.route("/unified", methods=["GET"], strict_slashes=False)
def unified_search():
    """
    Unified search across all 10 CIVICLENS TN phases:
      - schemes, promises, representatives, civic issues, claims,
        policy results, budgets, funding, news, and evidence records.

    Query parameters:
      - q or query: search term (required, string)
      - category or type: filter by record type (optional, default: "all")
      - page: page number (optional, default: 1)
      - limit: items per page (optional, default: 20, max: 100)
    """
    q = request.args.get("q") or request.args.get("query") or ""
    category = request.args.get("category") or request.args.get("type") or "all"
    
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 20))
    except ValueError:
        return error_response(message="Invalid page or limit parameter", status_code=400)

    if page < 1:
        page = 1
    if limit < 1:
        limit = 20
    if limit > 100:
        limit = 100

    db: Session = get_db()
    try:
        result = search_unified(
            db=db,
            query=q,
            category=category,
            page=page,
            limit=limit
        )
        return success_response(data=result, message="Search results retrieved successfully")
    except Exception as e:
        logger.error(f"Unified search error for query '{q}': {e}", exc_info=True)
        return error_response(
            message="Search service temporarily encountered an internal error",
            error_details=str(e),
            status_code=500
        )
    finally:
        db.close()


@search_bp.route("/categories", methods=["GET"])
def list_search_categories():
    """
    Returns available categories, display labels, and route mappings.
    """
    return success_response(
        data={
            "categories": [
                {
                    "key": key,
                    "label": cfg["label"],
                    "route": cfg["route"],
                    "badge": cfg["badge"]
                }
                for key, cfg in CATEGORY_CONFIG.items()
            ]
        },
        message="Search categories retrieved"
    )
