"""
Unit tests for multi-source civic web scraping:
RSS feeds, YouTube citizen comments, and X (Twitter) discourse and grievances.
"""

import os
import json
import pytest
from backend.acquisition.unified_scraper import UnifiedCivicScraper, unified_scraper
from backend.acquisition.youtube_scraper import YouTubeCivicScraper
from backend.acquisition.x_scraper import XCivicScraper
from backend.acquisition.news_scraper_framework import SourceScraper
from backend.api.app import create_app


class TestMultiSourceWebScraping:
    """Tests the multi-source scraping architecture across RSS, YouTube, and X."""

    def test_rss_extraction_and_provenance(self):
        scraper = SourceScraper()
        sources = scraper.registry.get_all_sources(enabled_only=True)
        rss_sources = [s for s in sources if s.rss_urls]
        assert len(rss_sources) >= 1

        target_source = rss_sources[0]
        articles = scraper.fetch_articles_from_rss(target_source, max_items=5)
        # Even if network is blocked or allowed, returns a valid list
        assert isinstance(articles, list)
        if articles:
            first = articles[0]
            assert "title" in first
            assert "url" in first
            assert "text_hash" in first
            assert len(first["text_hash"]) == 64  # Valid SHA-256

    def test_youtube_comment_scraping_and_sentiment(self):
        yt = YouTubeCivicScraper()
        res = yt.get_video_comments(video_id="yt_test_vid_01", max_results=5)
        assert res["status"] in ("success", "partial_offline")
        assert "comments" in res
        assert len(res["comments"]) > 0

        first_c = res["comments"][0]
        assert "text" in first_c
        assert "sentiment" in first_c
        assert first_c["sentiment"] in ("POSITIVE", "NEUTRAL", "CRITICAL")
        assert "civic_category" in first_c
        assert "sha256_hash" in first_c
        assert len(first_c["sha256_hash"]) == 64

    def test_x_discourse_and_grievance_scraping(self):
        x = XCivicScraper()
        res = x.search_recent_tweets(query="Tamil Nadu budget", max_results=5)
        assert res["status"] in ("success", "partial_offline")
        assert "data" in res
        assert len(res["data"]) > 0

        first_tw = res["data"][0]
        assert "text" in first_tw
        assert "sha256_hash" in first_tw

        # Test grievances
        g_res = x.scrape_civic_grievances(topic_or_hashtag="#GCCgrievance", max_results=5)
        assert g_res["status"] == "success"
        assert "grievances" in g_res
        assert len(g_res["grievances"]) > 0
        assert "issue_type" in g_res["grievances"][0]
        assert "archive_path" in g_res
        assert os.path.exists(g_res["archive_path"])

    def test_unified_scraper_full_audit(self):
        u = UnifiedCivicScraper()
        audit = u.run_full_audit_and_scrape()

        assert audit["summary"]["total_records_acquired"] > 0
        assert audit["summary"]["rss_articles_count"] >= 0
        assert audit["summary"]["youtube_comments_count"] > 0
        assert audit["summary"]["x_posts_count"] > 0
        assert "channels" in audit
        assert "rss" in audit["channels"]
        assert "youtube" in audit["channels"]
        assert "x_twitter" in audit["channels"]
        assert os.path.exists(audit["audit_manifest_path"])

    def test_acquisition_api_endpoints(self):
        app = create_app(validate_config=False)
        client = app.test_client()

        # Status
        resp = client.get("/api/acquisition/status")
        assert resp.status_code == 200
        json_data = resp.get_json()
        assert json_data["status"] == "success"
        assert json_data["data"]["status"] == "operational"
        assert "rss" in json_data["data"]["channels"]
        assert "youtube" in json_data["data"]["channels"]
        assert "x_twitter" in json_data["data"]["channels"]

        # YouTube Comments
        resp_yt = client.get("/api/acquisition/youtube-comments?limit=3")
        assert resp_yt.status_code == 200
        assert len(resp_yt.get_json()["data"]["comments"]) > 0

        # X Posts
        resp_x = client.get("/api/acquisition/x-posts?limit=3")
        assert resp_x.status_code == 200
        assert len(resp_x.get_json()["data"]["data"]) > 0
