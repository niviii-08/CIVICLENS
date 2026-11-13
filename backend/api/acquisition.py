"""
CIVICLENS TN - Civic Data Acquisition & Web Scraping REST API
=============================================================
Provides endpoints for monitoring, triggering, and inspecting multi-source web scraping:
- RSS news feeds & government releases
- YouTube legislative debates & citizen comments
- X (Twitter) political discourse & civic grievances
"""

from datetime import datetime, timezone
import os
import json
from flask import Blueprint, request, jsonify

from backend.core.config import config
from backend.core.logger import setup_logger
from backend.api.responses import success_response, error_response
from backend.acquisition.unified_scraper import unified_scraper
from backend.acquisition.news_registry import NewsSourceRegistry

logger = setup_logger("civiclens.api.acquisition")

acquisition_bp = Blueprint("acquisition", __name__, url_prefix="/acquisition")


@acquisition_bp.route("/status", methods=["GET"])
def get_acquisition_status():
    """
    Returns operating status of all civic acquisition channels:
    RSS feeds, YouTube Data API/scraper, and X API/scraper.
    """
    registry = NewsSourceRegistry()
    active_sources = registry.get_all_sources(enabled_only=True)
    rss_sources = [s for s in active_sources if s.rss_urls]

    raw_dir = os.path.join(config.DATA_DIR, "raw")
    news_scrapes_dir = os.path.join(raw_dir, "news_scrapes")
    yt_comments_dir = os.path.join(raw_dir, "youtube_comments")
    x_scrapes_dir = os.path.join(raw_dir, "x_scrapes")

    def count_files(directory):
        if not os.path.exists(directory):
            return 0
        return len([f for f in os.listdir(directory) if f.endswith(".json")])

    status_data = {
        "status": "operational",
        "channels": {
            "rss": {
                "status": "active",
                "registered_sources_count": len(active_sources),
                "rss_feeds_configured_count": len(rss_sources),
                "archives_count": count_files(news_scrapes_dir),
                "sample_sources": [s.source_name for s in rss_sources[:4]]
            },
            "youtube": {
                "status": "active",
                "has_api_key": bool(config.YOUTUBE_API_KEY),
                "features": ["video_metadata", "legislative_debates", "citizen_comments", "sentiment_tagging"],
                "archives_count": count_files(yt_comments_dir)
            },
            "x_twitter": {
                "status": "active",
                "has_bearer_token": bool(config.X_BEARER_TOKEN),
                "features": ["statement_monitoring", "civic_grievances", "hashtag_tracking", "sha256_provenance"],
                "archives_count": count_files(x_scrapes_dir)
            }
        },
        "storage": {
            "raw_dir": raw_dir,
            "has_raw_storage": os.path.exists(raw_dir)
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    return success_response(
        data=status_data,
        message="Acquisition channels operational status retrieved successfully."
    )


@acquisition_bp.route("/scrape", methods=["POST"])
def trigger_scrape():
    """
    Triggers web scraping on demand for a given channel or all channels.
    Request body (JSON):
      {
        "channel": "all" | "rss" | "youtube" | "x",
        "query": "optional query string",
        "max_results": 10
      }
    """
    body = request.get_json(silent=True) or {}
    channel = body.get("channel", "all").strip().lower()
    query = body.get("query", "").strip()
    max_results = min(int(body.get("max_results", 10)), 50)

    try:
        if channel == "rss":
            source_id = body.get("source_id")
            result = unified_scraper.scrape_rss(source_id=source_id, max_articles=max_results)
            return success_response(data=result, message="RSS web scraping completed successfully.")

        elif channel == "youtube":
            yt_query = query or "Tamil Nadu government welfare scheme"
            result = unified_scraper.scrape_youtube_comments(
                query=yt_query,
                max_videos=3,
                max_comments_per_video=max_results
            )
            return success_response(data=result, message="YouTube civic comments scraping completed.")

        elif channel == "x" or channel == "twitter":
            x_query = query or "Tamil Nadu budget"
            username = body.get("username")
            if username:
                result = unified_scraper.scrape_x_discourse(username=username, max_results=max_results)
            else:
                result = unified_scraper.scrape_x_discourse(query=x_query, max_results=max_results)
            return success_response(data=result, message="X civic discourse scraping completed.")

        elif channel == "all":
            result = unified_scraper.run_full_audit_and_scrape()
            return success_response(data=result, message="Full multi-source web scraping executed successfully.")

        else:
            return error_response(
                message=f"Invalid channel '{channel}'. Supported: 'all', 'rss', 'youtube', 'x'.",
                status_code=400
            )

    except Exception as e:
        logger.error(f"Error executing scrape for channel '{channel}': {e}", exc_info=True)
        return error_response(
            message=f"Scraping failed: {str(e)}",
            status_code=500
        )


@acquisition_bp.route("/rss", methods=["GET"])
def get_latest_rss():
    """Returns recently scraped RSS articles or runs a quick poll."""
    max_articles = min(int(request.args.get("limit", 15)), 50)
    source_id = request.args.get("source_id")

    res = unified_scraper.scrape_rss(source_id=source_id, max_articles=max_articles)
    return success_response(data=res, message="Latest RSS articles retrieved.")


@acquisition_bp.route("/youtube-comments", methods=["GET"])
def get_youtube_comments():
    """Returns citizen comments scraped from civic and legislative videos."""
    query = request.args.get("query", "Tamil Nadu legislative assembly welfare budget")
    max_comments = min(int(request.args.get("limit", 20)), 50)

    res = unified_scraper.scrape_youtube_comments(query=query, max_videos=2, max_comments_per_video=max_comments)
    return success_response(data=res, message="Civic YouTube comments retrieved.")


@acquisition_bp.route("/x-posts", methods=["GET"])
def get_x_posts():
    """Returns scraped X posts, statements, and citizen grievances."""
    query = request.args.get("query", "Tamil Nadu budget")
    username = request.args.get("username")
    limit = min(int(request.args.get("limit", 15)), 50)

    res = unified_scraper.scrape_x_discourse(query=query, username=username, max_results=limit)
    return success_response(data=res, message="X civic posts and discourse retrieved.")
