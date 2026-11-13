"""
CIVICLENS TN ?" Unified Civic Web Scraping & Multi-Source Acquisition Orchestrator.
===================================================================================
Coordinates polite, multi-channel public web scraping across:
1. RSS & Media Outlets (The Hindu, Dinamani, Dinamalar, Google News TN Syndication, PIB)
2. YouTube Civic Speech & Citizen Comments (Assembly Debates, Budget Sessions, Welfare Feedback)
3. X (Twitter) Discourse & Grievances (Political statements, Official Department Handles, GCC Grievances)

Enforces:
- SHA-256 cryptographic provenance hashing on every acquired record.
- Rate limiting, robots.txt compliance, and polite backoff.
- Multi-signal sentiment & civic categorization.
- Dual-mode operation (Live network fetching with structured grounded provenance fallback).
"""

import os
import json
import hashlib
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

from backend.core.config import config
from backend.core.logger import setup_logger
from backend.acquisition.news_scraper_framework import SourceScraper, NewsSourceRegistry
from backend.acquisition.youtube_scraper import YouTubeCivicScraper, youtube_scraper
from backend.acquisition.x_scraper import XCivicScraper, x_scraper

logger = setup_logger("civiclens.acquisition.unified_scraper")


class UnifiedCivicScraper:
    """
    Master acquisition orchestrator managing all civic web scrapers:
    RSS feeds, YouTube legislative video comments, and X social discourse.
    """

    def __init__(
        self,
        news_scraper_instance: Optional[SourceScraper] = None,
        youtube_scraper_instance: Optional[YouTubeCivicScraper] = None,
        x_scraper_instance: Optional[XCivicScraper] = None
    ):
        self.news_scraper = news_scraper_instance or SourceScraper()
        self.youtube_scraper = youtube_scraper_instance or youtube_scraper
        self.x_scraper = x_scraper_instance or x_scraper
        self.raw_data_dir = os.path.join(config.DATA_DIR, "raw")
        os.makedirs(self.raw_data_dir, exist_ok=True)

    def scrape_rss(
        self,
        source_id: Optional[str] = None,
        max_articles: int = 10
    ) -> Dict[str, Any]:
        """
        Scrapes news and government updates from registered RSS feeds.

        Args:
            source_id: Specific source ID (e.g. 'src_thehindu_en') or None for all active RSS sources.
            max_articles: Max articles to collect per source.

        Returns:
            Dictionary containing scraped articles, provenance metadata, and file archives.
        """
        logger.info(f"Initiating RSS scrape (source_id={source_id}, max={max_articles})")

        if source_id:
            articles = self.news_scraper.crawl_source(source_id=source_id, max_articles=max_articles)
            output = {
                "status": "success",
                "channel": "rss",
                "source_id": source_id,
                "count": len(articles),
                "articles": articles
            }
            archive_path = self.news_scraper.archive_news_with_provenance(output)
            output["archive_path"] = archive_path
            return output
        else:
            return self.news_scraper.crawl_all_active_rss_sources(max_per_source=max_articles)

    def scrape_youtube_comments(
        self,
        query: str = "Tamil Nadu government welfare scheme",
        max_videos: int = 3,
        max_comments_per_video: int = 20
    ) -> Dict[str, Any]:
        """
        Scrapes YouTube legislative debate/announcement videos and citizen comments.
        Extracts comment text (Tamil & English), engagement metrics, and civic sentiment tags.

        Args:
            query: Topic query for search (e.g. 'Tamil Nadu Assembly Budget session').
            max_videos: Number of videos to inspect.
            max_comments_per_video: Max comments to scrape per video.

        Returns:
            Dictionary containing videos, structured comments, sentiment tags, and provenance.
        """
        logger.info(f"Initiating YouTube comment scrape for query: '{query}'")
        return self.youtube_scraper.scrape_civic_comments(
            query=query,
            max_videos=max_videos,
            max_comments_per_video=max_comments_per_video
        )

    def scrape_x_discourse(
        self,
        query: str = "Tamil Nadu budget",
        username: Optional[str] = None,
        max_results: int = 15
    ) -> Dict[str, Any]:
        """
        Scrapes X (Twitter) public discourse, official statements, and citizen grievances.

        Args:
            query: Keyword or hashtag query.
            username: Specific handle without @ (e.g. 'CMOTamilnadu', 'chennaicorp').
            max_results: Max posts to retrieve.

        Returns:
            Dictionary with tweets, engagement metrics, and archive path.
        """
        logger.info(f"Initiating X discourse scrape (query='{query}', username='{username}')")
        if username:
            return self.x_scraper.get_user_statements(username=username, max_results=max_results)
        else:
            return self.x_scraper.search_recent_tweets(query=query, max_results=max_results)

    def scrape_x_civic_grievances(
        self,
        topic_or_hashtag: str = "#GCCgrievance",
        max_results: int = 15
    ) -> Dict[str, Any]:
        """
        Specialized scraper for public civic grievances and departmental SLA responses on X.
        """
        logger.info(f"Scraping X civic grievances for {topic_or_hashtag}")
        return self.x_scraper.scrape_civic_grievances(topic_or_hashtag=topic_or_hashtag, max_results=max_results)

    def run_full_audit_and_scrape(self) -> Dict[str, Any]:
        """
        Executes end-to-end multi-source web scraping across ALL supported channels:
        1. RSS feeds (Regional news + Google News TN syndication)
        2. YouTube videos & citizen comments (Legislative debate & welfare sentiment)
        3. X political statements & citizen grievances (#GCCgrievance, #TNEB, #TNGovt)

        Generates cryptographic SHA-256 archive files and an audit report.
        """
        timestamp_start = datetime.now(timezone.utc).isoformat()
        logger.info(f"Starting complete multi-source civic web scraping audit at {timestamp_start}")

        audit_results = {
            "orchestrator": "CivicLens TN UnifiedCivicScraper v2.0",
            "started_at": timestamp_start,
            "channels": {},
            "summary": {
                "total_records_acquired": 0,
                "rss_articles_count": 0,
                "youtube_comments_count": 0,
                "x_posts_count": 0,
                "archives_generated": []
            }
        }

        # 1. Scrape RSS feeds
        try:
            rss_res = self.scrape_rss(max_articles=10)
            articles_count = rss_res.get("total_articles", len(rss_res.get("articles", [])))
            archive_path = rss_res.get("archive_path", "")

            audit_results["channels"]["rss"] = {
                "status": "success",
                "count": articles_count,
                "sources_scraped": rss_res.get("sources_scraped", 1),
                "archive_path": archive_path,
                "sample_titles": [a.get("title") for a in rss_res.get("articles", [])[:3]]
            }
            audit_results["summary"]["rss_articles_count"] = articles_count
            audit_results["summary"]["total_records_acquired"] += articles_count
            if archive_path:
                audit_results["summary"]["archives_generated"].append(archive_path)
        except Exception as e:
            logger.error(f"RSS scraping error in unified audit: {e}")
            audit_results["channels"]["rss"] = {"status": "error", "error": str(e)}

        # 2. Scrape YouTube Videos & Comments
        try:
            yt_res = self.scrape_youtube_comments(
                query="Tamil Nadu legislative assembly welfare budget",
                max_videos=3,
                max_comments_per_video=15
            )
            comments_count = yt_res.get("total_comments", len(yt_res.get("comments", [])))
            archive_path = yt_res.get("archive_path", "")

            audit_results["channels"]["youtube"] = {
                "status": "success",
                "videos_scanned": yt_res.get("videos_scanned", 0),
                "comments_count": comments_count,
                "archive_path": archive_path,
                "sample_comments": [
                    {
                        "author": c.get("author"),
                        "text": c.get("text")[:80] + "..." if len(c.get("text", "")) > 80 else c.get("text"),
                        "sentiment": c.get("sentiment"),
                        "category": c.get("civic_category")
                    }
                    for c in yt_res.get("comments", [])[:3]
                ]
            }
            audit_results["summary"]["youtube_comments_count"] = comments_count
            audit_results["summary"]["total_records_acquired"] += comments_count
            if archive_path:
                audit_results["summary"]["archives_generated"].append(archive_path)
        except Exception as e:
            logger.error(f"YouTube scraping error in unified audit: {e}")
            audit_results["channels"]["youtube"] = {"status": "error", "error": str(e)}

        # 3. Scrape X Posts & Grievances
        try:
            x_search_res = self.scrape_x_discourse(query="Tamil Nadu budget OR மகளிர் உரிமை", max_results=10)
            x_grievances_res = self.scrape_x_civic_grievances(topic_or_hashtag="#GCCgrievance", max_results=10)

            x_posts = x_search_res.get("data", [])
            x_grievances = x_grievances_res.get("grievances", [])
            total_x = len(x_posts) + len(x_grievances)

            archives = []
            if x_search_res.get("archive_path"):
                archives.append(x_search_res.get("archive_path"))
            if x_grievances_res.get("archive_path"):
                archives.append(x_grievances_res.get("archive_path"))

            audit_results["channels"]["x_twitter"] = {
                "status": "success",
                "posts_count": len(x_posts),
                "grievances_count": len(x_grievances),
                "total_x_records": total_x,
                "archives": archives,
                "sample_posts": [
                    {
                        "id": p.get("id"),
                        "text": p.get("text")[:80] + "..." if len(p.get("text", "")) > 80 else p.get("text"),
                        "author_id": p.get("author_id")
                    }
                    for p in (x_posts + x_grievances)[:3]
                ]
            }
            audit_results["summary"]["x_posts_count"] = total_x
            audit_results["summary"]["total_records_acquired"] += total_x
            audit_results["summary"]["archives_generated"].extend(archives)
        except Exception as e:
            logger.error(f"X scraping error in unified audit: {e}")
            audit_results["channels"]["x_twitter"] = {"status": "error", "error": str(e)}

        timestamp_end = datetime.now(timezone.utc).isoformat()
        audit_results["completed_at"] = timestamp_end

        # Save overarching audit manifest
        audit_filename = f"unified_scrape_audit_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        audit_filepath = os.path.join(self.raw_data_dir, audit_filename)

        with open(audit_filepath, "w", encoding="utf-8") as f:
            json.dump(audit_results, f, indent=2, ensure_ascii=False)

        audit_results["audit_manifest_path"] = audit_filepath
        logger.info(f"Completed multi-source scrape audit. Total records: {audit_results['summary']['total_records_acquired']}")
        return audit_results


unified_scraper = UnifiedCivicScraper()
