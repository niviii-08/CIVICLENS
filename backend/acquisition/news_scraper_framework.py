import os
import re
import time
import json
import hashlib
import urllib.robotparser
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse, urljoin
import requests

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    feedparser = None
    HAS_FEEDPARSER = False

from backend.core.config import config
from backend.core.logger import setup_logger
from backend.acquisition.news_registry import SourceConfig, NewsSourceRegistry
from backend.acquisition.news_adapters import adapter_registry, BaseSourceAdapter

logger = setup_logger("civiclens.acquisition.news_scraper_framework")

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scratch", "cache", "http")

class RateLimiter:
    """Per-domain rate limiter enforcing polite crawl delays."""
    def __init__(self, default_delay: float = 1.0):
        self.default_delay = default_delay
        self.last_fetch: Dict[str, float] = {}

    def wait(self, domain: str, custom_delay: Optional[float] = None) -> float:
        delay = custom_delay if custom_delay is not None else self.default_delay
        now = time.time()
        elapsed_wait = 0.0
        if domain in self.last_fetch:
            elapsed = now - self.last_fetch[domain]
            if elapsed < delay:
                elapsed_wait = delay - elapsed
                time.sleep(elapsed_wait)
        self.last_fetch[domain] = time.time()
        return elapsed_wait

class RobotsChecker:
    """Validator for domain robots.txt directives using strict timeout to prevent hanging."""
    def __init__(self, user_agent: str):
        self.user_agent = user_agent
        self.parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def is_allowed(self, url: str) -> bool:
        parsed = urlparse(url)
        domain = parsed.netloc
        if not domain:
            return True

        if domain not in self.parsers:
            robots_url = f"{parsed.scheme}://{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            try:
                resp = requests.get(robots_url, timeout=3, headers={"User-Agent": self.user_agent})
                if resp.status_code == 200:
                    rp.parse(resp.text.splitlines())
                else:
                    rp.parse(["User-agent: *", "Allow: /"])
                self.parsers[domain] = rp
            except Exception as e:
                logger.warning(f"Unable to read robots.txt for {domain}: {e}. Permissive fallback enabled.")
                rp.parse(["User-agent: *", "Allow: /"])
                self.parsers[domain] = rp

        try:
            return self.parsers[domain].can_fetch(self.user_agent, url)
        except Exception:
            return True

class CacheManager:
    """Disk & memory cache manager storing HTTP responses with TTL and header validation."""
    def __init__(self, cache_dir: str = CACHE_DIR, ttl_seconds: int = 86400):
        self.cache_dir = cache_dir
        self.ttl_seconds = ttl_seconds
        self.memory_cache: Dict[str, Dict] = {}
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_key(self, url: str) -> str:
        return hashlib.sha256(url.encode('utf-8')).hexdigest()

    def get(self, url: str) -> Optional[str]:
        key = self._get_key(url)
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["timestamp"] < self.ttl_seconds:
                return entry["content"]

        file_path = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if time.time() - data["timestamp"] < self.ttl_seconds:
                        self.memory_cache[key] = data
                        return data["content"]
            except Exception as e:
                logger.warning(f"Cache read error for {url}: {e}")

        return None

    def set(self, url: str, content: str, headers: Optional[Dict] = None) -> None:
        key = self._get_key(url)
        data = {
            "url": url,
            "timestamp": time.time(),
            "content": content,
            "headers": headers or {}
        }
        self.memory_cache[key] = data
        file_path = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Cache write error for {url}: {e}")

class Fetcher:
    """HTTP client supporting retries, rate limiting, and caching."""
    def __init__(self, rate_limiter: RateLimiter, cache_manager: CacheManager,
                 robots_checker: RobotsChecker, max_retries: int = 1, backoff_factor: float = 1.0):
        self.rate_limiter = rate_limiter
        self.cache_manager = cache_manager
        self.robots_checker = robots_checker
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.session = requests.Session()

    def fetch(self, url: str, source_config: Optional[SourceConfig] = None, use_cache: bool = True, timeout: int = 5) -> Optional[str]:
        if use_cache:
            cached = self.cache_manager.get(url)
            if cached:
                logger.info(f"Cache hit for URL: {url}")
                return cached

        if not self.robots_checker.is_allowed(url):
            logger.warning(f"Access blocked by robots.txt policy: {url}")
            return None

        domain = urlparse(url).netloc
        delay = min(source_config.rate_limit, 1.0) if source_config else 1.0
        self.rate_limiter.wait(domain, custom_delay=delay)

        attempt = 0
        while attempt < self.max_retries:
            attempt += 1
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = self.session.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                content = response.text
                if use_cache and content:
                    self.cache_manager.set(url, content, dict(response.headers))
                return content
            except requests.RequestException as e:
                logger.warning(f"Fetch attempt {attempt}/{self.max_retries} failed for {url}: {e}")
                if attempt < self.max_retries:
                    time.sleep(1.0)

        logger.error(f"Failed to fetch URL: {url}")
        return None

class Deduplicator:
    """Deduplication manager tracking URLs and exact text hashes."""
    def __init__(self):
        self.seen_urls: Set[str] = set()
        self.seen_hashes: Set[str] = set()

    def is_duplicate_url(self, url: str) -> bool:
        canonical = re.sub(r'(\?|#).*$', '', url.strip().lower())
        if canonical in self.seen_urls:
            return True
        self.seen_urls.add(canonical)
        return False

    def is_duplicate_text(self, text_hash: str) -> bool:
        if text_hash in self.seen_hashes:
            return True
        self.seen_hashes.add(text_hash)
        return False

class ContentExtractor:
    """Extracts, cleans, and normalizes article text content."""
    @staticmethod
    def extract_clean_text(raw_paragraphs: List[str]) -> str:
        cleaned = []
        for p in raw_paragraphs:
            txt = re.sub(r'\s+', ' ', p).strip()
            if len(txt.split()) >= 4:
                cleaned.append(txt)
        return "\n\n".join(cleaned)

class MetadataExtractor:
    """Extracts metadata fields (headline, author, pubdate, canonical URL)."""
    @staticmethod
    def extract_metadata(parsed_dict: Dict, source_config: Optional[SourceConfig] = None) -> Dict[str, Any]:
        return {
            "title": parsed_dict.get("title", ""),
            "author": parsed_dict.get("author", "Staff Reporter"),
            "publication_date": parsed_dict.get("publication_date", datetime.now(timezone.utc)),
            "canonical_url": parsed_dict.get("canonical_url", parsed_dict.get("url", "")),
            "language": source_config.language if source_config else "ta"
        }

class ArticleParser:
    """Parser controller delegating parsing to registered source adapters."""
    def __init__(self):
        self.registry = adapter_registry

    def parse(self, html_content: str, url: str, source_config: Optional[SourceConfig] = None) -> Optional[Dict[str, Any]]:
        adapter_name = source_config.parser_type if source_config else "generic_adapter"
        adapter = self.registry.get_adapter(adapter_name)
        selectors = source_config.selectors if source_config else {}

        try:
            parsed = adapter.parse_article(html_content, url, selector_config=selectors)
            if not parsed or not parsed.get("article_text"):
                logger.warning(f"Primary adapter '{adapter_name}' yielded empty content. Falling back to generic adapter.")
                generic_adapter = self.registry.get_adapter("generic_adapter")
                parsed = generic_adapter.parse_article(html_content, url, selector_config=selectors)
            return parsed
        except Exception as e:
            logger.error(f"Parser error using adapter '{adapter_name}' on {url}: {e}")
            return None

class BaseScraper(ABC):
    """Abstract Base Class for News Scraper implementations."""
    @abstractmethod
    def crawl_source(self, source_id: str) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def scrape_article(self, url: str, source_id: str) -> Optional[Dict[str, Any]]:
        pass

class SourceScraper(BaseScraper):
    """
    Main driver orchestrating URL discovery, fetcher, cache, rate limiter,
    deduplicator, and pluggable source adapters for a target news source.
    """
    def __init__(self, registry: Optional[NewsSourceRegistry] = None, user_agent: Optional[str] = None):
        self.registry = registry or NewsSourceRegistry()
        self.user_agent = user_agent or "CIVICLENS-TN-NewsAnalyzer/2.0 (+https://civiclens.tn.gov.in/bot)"
        self.rate_limiter = RateLimiter()
        self.cache_manager = CacheManager()
        self.robots_checker = RobotsChecker(self.user_agent)
        self.fetcher = Fetcher(self.rate_limiter, self.cache_manager, self.robots_checker)
        self.deduplicator = Deduplicator()
        self.parser = ArticleParser()
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})

    def discover_urls_from_rss(self, source_config: SourceConfig) -> List[str]:
        """Discovers article URLs from configured RSS feeds using feedparser with strict timeout."""
        discovered = []
        for rss_url in source_config.rss_urls:
            logger.info(f"Polling RSS feed: {rss_url}")
            if HAS_FEEDPARSER:
                try:
                    resp = self.session.get(rss_url, timeout=4)
                    if resp.status_code == 200:
                        feed = feedparser.parse(resp.content)
                        for entry in feed.entries:
                            link = entry.get("link", "").strip()
                            if link and not self.deduplicator.is_duplicate_url(link):
                                discovered.append(link)
                except Exception as e:
                    logger.warning(f"Error fetching RSS {rss_url}: {e}")

            if not discovered:
                xml_content = self.fetcher.fetch(rss_url, source_config=source_config, use_cache=False, timeout=4)
                if xml_content:
                    links = re.findall(r'<link>(.*?)</link>', xml_content, re.I)
                    for link in links:
                        link = link.strip()
                        if link and not link.endswith('.xml') and link != rss_url:
                            if not self.deduplicator.is_duplicate_url(link):
                                discovered.append(link)
        return discovered

    def fetch_articles_from_rss(self, source_config: SourceConfig, max_items: int = 15) -> List[Dict[str, Any]]:
        """
        Extracts structured articles directly from RSS feeds (title, link, summary, date, author)
        with SHA-256 deduplication and fallback content.
        """
        articles = []
        for rss_url in source_config.rss_urls:
            logger.info(f"Extracting structured articles from RSS feed: {rss_url}")
            if HAS_FEEDPARSER:
                try:
                    resp = self.session.get(rss_url, timeout=4)
                    if resp.status_code == 200:
                        feed = feedparser.parse(resp.content)
                        for entry in feed.entries[:max_items]:
                            url = entry.get("link", "").strip()
                            title = entry.get("title", "").strip()
                            summary = entry.get("summary", "") or entry.get("description", "")
                            summary_clean = re.sub(r'<[^>]+>', '', summary).strip()

                            if not title or not url:
                                continue

                            text_hash = hashlib.sha256(f"{title}:{summary_clean}".encode("utf-8")).hexdigest()
                            if self.deduplicator.is_duplicate_text(text_hash):
                                continue

                            pub_date = datetime.now(timezone.utc)
                            if "published_parsed" in entry and entry.published_parsed:
                                try:
                                    pub_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                                except Exception:
                                    pass

                            articles.append({
                                "url": url,
                                "canonical_url": url,
                                "title": title,
                                "author": entry.get("author", "Staff Reporter"),
                                "publication_date": pub_date.isoformat(),
                                "article_text": summary_clean if len(summary_clean) > 30 else f"{title}\n\n{summary_clean}",
                                "word_count": len(summary_clean.split()),
                                "text_hash": text_hash,
                                "source_id": source_config.source_id,
                                "source_name": source_config.source_name,
                                "language": source_config.language,
                                "is_rss_direct": True
                            })
                except Exception as e:
                    logger.warning(f"Error parsing RSS {rss_url}: {e}")

        return articles

    def discover_urls_from_html(self, html_content: str, base_url: str, source_config: SourceConfig) -> List[str]:
        """Discovers article links from index/category HTML pages using regex and url patterns."""
        discovered = []
        raw_links = re.findall(r'href=["\']([^"\']+)["\']', html_content, re.I)
        for rel_link in raw_links:
            full_url = urljoin(base_url, rel_link)
            is_article = False
            if source_config.article_url_patterns:
                for pattern in source_config.article_url_patterns:
                    if re.search(pattern, full_url):
                        is_article = True
                        break
            else:
                is_article = True

            if is_article and not self.deduplicator.is_duplicate_url(full_url):
                discovered.append(full_url)
        return discovered

    def scrape_article(self, url: str, source_id: str, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        """Scrapes and parses a single news article URL."""
        source_config = self.registry.get_source(source_id)
        if not source_config:
            logger.error(f"Source configuration '{source_id}' not found.")
            return None

        if not source_config.enabled:
            logger.warning(f"Source '{source_id}' is disabled. Skipping scrape.")
            return None

        html_content = self.fetcher.fetch(url, source_config=source_config, use_cache=use_cache, timeout=4)
        if not html_content:
            return None

        parsed = self.parser.parse(html_content, url, source_config=source_config)
        if not parsed:
            return None

        if self.deduplicator.is_duplicate_text(parsed["text_hash"]):
            logger.info(f"Duplicate article content detected for URL: {url}. Skipping.")
            return None

        parsed["source_id"] = source_id
        parsed["source_name"] = source_config.source_name
        parsed["language"] = source_config.language
        return parsed

    def crawl_source(self, source_id: str, max_articles: int = 10) -> List[Dict[str, Any]]:
        """Crawls a source using RSS and homepage discovery, returning parsed articles."""
        source_config = self.registry.get_source(source_id)
        if not source_config or not source_config.enabled:
            return []

        logger.info(f"Initiating crawl for source: '{source_config.source_name}' ({source_id})")

        # 1. Attempt direct RSS structured extraction first
        if source_config.rss_urls:
            rss_articles = self.fetch_articles_from_rss(source_config, max_items=max_articles)
            if rss_articles:
                logger.info(f"Retrieved {len(rss_articles)} articles directly from RSS for {source_id}")
                return rss_articles

        # 2. If RSS is not present, only attempt lightweight HTML crawl if patterns exist
        if not source_config.rss_urls and source_config.article_url_patterns and source_config.official_url:
            home_html = self.fetcher.fetch(source_config.official_url, source_config=source_config, timeout=4)
            if home_html:
                html_urls = self.discover_urls_from_html(home_html, source_config.official_url, source_config)
                scraped_articles = []
                for url in html_urls[:max_articles]:
                    art = self.scrape_article(url, source_id=source_id)
                    if art:
                        scraped_articles.append(art)
                if scraped_articles:
                    logger.info(f"Crawl complete for {source_id}: {len(scraped_articles)} articles scraped.")
                    return scraped_articles

        return []

    def crawl_all_active_rss_sources(self, max_per_source: int = 10) -> Dict[str, Any]:
        """Crawls all registered sources that have RSS configured and archives with SHA-256."""
        all_sources = self.registry.get_all_sources(enabled_only=True)
        results = {}
        total_scraped = 0
        all_articles = []

        # Only crawl sources with RSS configured
        rss_sources = [s for s in all_sources if s.rss_urls]

        for src in rss_sources:
            arts = self.crawl_source(src.source_id, max_articles=max_per_source)
            if arts:
                results[src.source_id] = {
                    "source_name": src.source_name,
                    "count": len(arts)
                }
                all_articles.extend(arts)
                total_scraped += len(arts)

        output = {
            "status": "success",
            "sources_scraped": len(results),
            "total_articles": total_scraped,
            "source_breakdown": results,
            "articles": all_articles
        }

        # Archive to disk
        archive_path = self.archive_news_with_provenance(output)
        output["archive_path"] = archive_path
        return output

    def archive_news_with_provenance(
        self,
        result_data: Dict[str, Any],
        output_dir: Optional[str] = None
    ) -> str:
        """Saves scraped news articles to disk with cryptographic SHA-256 provenance hashing."""
        out_path = output_dir or os.path.join(config.DATA_DIR, "raw", "news_scrapes")
        os.makedirs(out_path, exist_ok=True)

        timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"rss_scrape_all_{timestamp_str}.json"
        full_filepath = os.path.join(out_path, filename)

        serialized = json.dumps(result_data, sort_keys=True, default=str)
        sha256_checksum = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        payload = {
            "metadata": {
                "acquisition_timestamp": datetime.now(timezone.utc).isoformat(),
                "sha256_checksum": sha256_checksum,
                "record_count": result_data.get("total_articles", len(result_data.get("articles", []))),
                "generator": "CivicLens TN SourceScraper v2.0"
            },
            "payload": result_data
        }

        with open(full_filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)

        logger.info(f"Archived {payload['metadata']['record_count']} news records to {full_filepath} [SHA256: {sha256_checksum[:12]}]")
        return full_filepath
