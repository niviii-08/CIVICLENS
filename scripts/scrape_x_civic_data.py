"""
CLI Script for scraping and archiving public civic records and party statements from X (Twitter).

Usage:
    python scripts/scrape_x_civic_data.py --query "Tamil Nadu budget" --max 15
    python scripts/scrape_x_civic_data.py --party DMK
    python scripts/scrape_x_civic_data.py --party AIADMK
    python scripts/scrape_x_civic_data.py --archive
"""

import sys
import argparse
from pathlib import Path

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.acquisition.x_scraper import x_scraper, TN_POLITICAL_HANDLES, DEFAULT_CIVIC_QUERIES
from backend.core.logger import setup_logger

logger = setup_logger("civiclens.scripts.scrape_x")


def main():
    parser = argparse.ArgumentParser(description="CivicLens TN — X (Twitter) Civic Scraping Utility")
    parser.add_argument("--query", "-q", type=str, help="Search query string")
    parser.add_argument("--party", "-p", type=str, choices=list(TN_POLITICAL_HANDLES.keys()), help="Political party key")
    parser.add_argument("--max", "-m", type=int, default=10, help="Maximum number of results to fetch")
    parser.add_argument("--archive", "-a", action="store_true", help="Archive results to data/raw/x_scrapes with SHA-256")
    parser.add_argument("--all-parties", action="store_true", help="Scrape latest statements across all TN parties")

    args = parser.parse_args()

    print("=" * 65)
    print("   CIVICLENS TN — X (TWITTER) CIVIC DATA SCRAPING PIPELINE")
    print("=" * 65)

    if args.party:
        handles = TN_POLITICAL_HANDLES[args.party]
        print(f"\n[+] Scraping official handles for party: {args.party} -> {handles}")
        for handle in handles:
            print(f"\n--- Checking handle: @{handle} ---")
            res = x_scraper.get_user_statements(handle, max_results=args.max)
            print(f"Status: {res.get('status')} | Source: {res.get('source')}")
            if res.get("notice"):
                print(f"Notice: {res.get('notice')}")
            tweets = res.get("tweets", [])
            for t in tweets[:3]:
                print(f"  • [{t.get('created_at', 'N/A')}] {t.get('text', '')[:100]}...")

            if args.archive and tweets:
                saved_file = x_scraper.archive_tweets_with_provenance(res)
                print(f"  -> Archived to: {saved_file}")

    elif args.all_parties:
        print("\n[+] Scanning all registered political parties in Tamil Nadu...")
        for party_name, handles in TN_POLITICAL_HANDLES.items():
            print(f"\n[Party: {party_name}] Handles: {handles}")
            res = x_scraper.search_recent_tweets(f"{party_name} Tamil Nadu promise OR budget", max_results=args.max)
            print(f"Status: {res.get('status')} | Retrieved: {res.get('count')} records | Source: {res.get('source')}")
            if args.archive:
                saved = x_scraper.archive_tweets_with_provenance(res)
                print(f"  -> Provenance archive: {saved}")

    else:
        query = args.query or DEFAULT_CIVIC_QUERIES[0]
        print(f"\n[+] Searching civic discourse for query: '{query}'")
        res = x_scraper.search_recent_tweets(query, max_results=args.max)
        print(f"Status: {res.get('status')} | Source: {res.get('source')} | Count: {res.get('count')}")
        if res.get("notice"):
            print(f"API Notice: {res.get('notice')}")

        data = res.get("data", [])
        print(f"\nRetrieved Records ({len(data)}):")
        for idx, item in enumerate(data, 1):
            metrics = item.get("public_metrics", {})
            print(f"\n[{idx}] ID: {item.get('id')}")
            print(f"    Text: {item.get('text')}")
            print(f"    Metrics: Likes={metrics.get('like_count', 0)}, Retweets={metrics.get('retweet_count', 0)}")

        if args.archive or True:
            saved_file = x_scraper.archive_tweets_with_provenance(res)
            print(f"\n[✓] Cryptographic archive saved to: {saved_file}")

    print("\n" + "=" * 65)
    print("   CIVIC DATA SCRAPING COMPLETE")
    print("=" * 65)


if __name__ == "__main__":
    main()
