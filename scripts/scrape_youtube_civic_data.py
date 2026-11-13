"""
CLI Utility for scraping and archiving Tamil Nadu legislative assembly proceedings,
political press briefings, and civic debates via YouTube Data API v3.

Usage:
    python scripts/scrape_youtube_civic_data.py --query "Tamil Nadu budget" --max 5
    python scripts/scrape_youtube_civic_data.py --party DMK --max 5
    python scripts/scrape_youtube_civic_data.py --party AIADMK --max 5
    python scripts/scrape_youtube_civic_data.py --assembly --archive
"""

import sys
import argparse
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.acquisition.youtube_scraper import (
    youtube_scraper,
    DEFAULT_YOUTUBE_QUERIES,
    TN_BROADCAST_OUTLETS
)
from backend.core.logger import setup_logger

logger = setup_logger("civiclens.scripts.scrape_youtube")


def main():
    parser = argparse.ArgumentParser(description="CivicLens TN — YouTube Civic Data Scraping Utility")
    parser.add_argument("--query", "-q", type=str, help="Search query string")
    parser.add_argument("--party", "-p", type=str, choices=["DMK", "AIADMK", "BJP", "INC", "NTK", "PMK"], help="Party name for debate search")
    parser.add_argument("--max", "-m", type=int, default=5, help="Maximum number of videos to fetch (up to 50)")
    parser.add_argument("--order", choices=["relevance", "date", "viewCount", "rating"], default="relevance", help="Sort order")
    parser.add_argument("--assembly", action="store_true", help="Search legislative assembly debates and budget speeches")
    parser.add_argument("--archive", "-a", action="store_true", help="Save cryptographic archive to data/raw/youtube_scrapes")

    args = parser.parse_args()

    print("=" * 68)
    print("   CIVICLENS TN — YOUTUBE CIVIC DATA ACQUISITION PIPELINE")
    print("=" * 68)

    if args.party:
        print(f"\n[+] Searching assembly speeches & debates for party: {args.party}")
        res = youtube_scraper.search_party_debates(party=args.party, max_results=args.max)
    elif args.assembly:
        print("\n[+] Searching official Tamil Nadu Legislative Assembly proceedings & budget speeches...")
        res = youtube_scraper.search_civic_videos(
            query="Tamil Nadu Legislative Assembly Budget session speech",
            max_results=args.max,
            order=args.order
        )
    else:
        query = args.query or DEFAULT_YOUTUBE_QUERIES[0]
        print(f"\n[+] Searching civic & governance videos for: '{query}' (order={args.order})")
        res = youtube_scraper.search_civic_videos(query=query, max_results=args.max, order=args.order)

    print(f"Status: {res.get('status')} | Source: {res.get('source')} | Videos Found: {res.get('count')}")
    if res.get("notice"):
        print(f"Notice: {res.get('notice')}")

    videos = res.get("videos", [])
    print(f"\nRetrieved Video Records ({len(videos)}):")
    for idx, vid in enumerate(videos, 1):
        stats = vid.get("statistics", {})
        print(f"\n[{idx}] {vid.get('title')}")
        print(f"    Channel: {vid.get('channel_title')} | Published: {vid.get('published_at')}")
        print(f"    URL: {vid.get('video_url')}")
        if stats:
            print(f"    Engagement: Views={stats.get('view_count', 0):,}, Likes={stats.get('like_count', 0):,}, Comments={stats.get('comment_count', 0):,}")

    if args.archive or True:
        saved_file = youtube_scraper.archive_videos_with_provenance(res)
        print(f"\n[✓] Cryptographic provenance archive saved to:\n    {saved_file}")

    print("\n" + "=" * 68)
    print("   YOUTUBE DATA ACQUISITION COMPLETE")
    print("=" * 68)


if __name__ == "__main__":
    main()
