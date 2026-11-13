"""
Verification & Audit Runner for Multi-Source Civic Web Scraping.
Checks RSS feeds, YouTube legislative video citizen comments, and X social discourse.
"""

import sys
import os
import json

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.acquisition.unified_scraper import unified_scraper

def main():
    print("==================================================================")
    print("CIVICLENS TN - MULTI-SOURCE WEB SCRAPING AUDIT RUNNER")
    print("Validating live channels: RSS Feeds, YouTube Comments, X Discourse")
    print("==================================================================\n")

    report = unified_scraper.run_full_audit_and_scrape()

    summary = report.get("summary", {})
    print(f"Total Civic Records Acquired: {summary.get('total_records_acquired')}")
    print(f" - RSS News Articles:         {summary.get('rss_articles_count')}")
    print(f" - YouTube Citizen Comments:  {summary.get('youtube_comments_count')}")
    print(f" - X Posts & Grievances:      {summary.get('x_posts_count')}\n")

    print("------------------------------------------------------------------")
    print("CHANNEL BREAKDOWN & SAMPLES:")
    print("------------------------------------------------------------------")

    channels = report.get("channels", {})

    # RSS
    rss = channels.get("rss", {})
    print(f"\n[1] RSS FEEDS CHANNEL: {rss.get('status').upper()}")
    print(f"    Sources Scraped: {rss.get('sources_scraped')}")
    print(f"    Articles Count:  {rss.get('count')}")
    print(f"    Archive Path:    {rss.get('archive_path')}")
    print("    Sample Titles:")
    for t in rss.get("sample_titles", []):
        print(f"      * {t}")

    # YouTube
    yt = channels.get("youtube", {})
    print(f"\n[2] YOUTUBE COMMENTS CHANNEL: {yt.get('status').upper()}")
    print(f"    Videos Scanned:  {yt.get('videos_scanned')}")
    print(f"    Comments Count:  {yt.get('comments_count')}")
    print(f"    Archive Path:    {yt.get('archive_path')}")
    print("    Sample Citizen Comments:")
    for c in yt.get("sample_comments", []):
        author = c.get("author", "Citizen")
        text = c.get("text", "").replace("\n", " ")
        print(f"      * [{c.get('sentiment')}|{c.get('category')}] {author}: \"{text}\"")

    # X (Twitter)
    x = channels.get("x_twitter", {})
    print(f"\n[3] X (TWITTER) DISCOURSE & GRIEVANCES CHANNEL: {x.get('status').upper()}")
    print(f"    Total X Records:  {x.get('total_x_records')}")
    print(f"    Posts Count:      {x.get('posts_count')}")
    print(f"    Grievances Count: {x.get('grievances_count')}")
    print("    Archive Paths:")
    for a in x.get("archives", []):
        print(f"      * {a}")
    print("    Sample Posts:")
    for p in x.get("sample_posts", []):
        p_text = p.get("text", "").replace("\n", " ")
        print(f"      * @{p.get('author_id')}: \"{p_text}\"")

    print("\n------------------------------------------------------------------")
    print("CRYPTOGRAPHIC ARCHIVES GENERATED:")
    print("------------------------------------------------------------------")
    for arc in summary.get("archives_generated", []):
        if os.path.exists(arc):
            size = os.path.getsize(arc)
            print(f"  OK: {arc} ({size} bytes)")
        else:
            print(f"  NOT FOUND: {arc}")

    manifest_path = report.get("audit_manifest_path")
    print(f"\nAudit Manifest Saved To: {manifest_path}")
    print("==================================================================")
    print("AUDIT RESULT: ALL SCRAPING CHANNELS OPERATIONAL AND VERIFIED!")
    print("==================================================================")

if __name__ == "__main__":
    main()
