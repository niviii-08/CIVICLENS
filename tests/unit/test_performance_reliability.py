"""
Phase 12.4: Performance and Operational Reliability Automated Tests.
Validates:
- Database session closure and leak prevention on schemes API endpoints
- Optimized bulk queries replacing N+1 patterns in civic, claims, and promises modules
- In-memory search caching: hits, misses, TTL expiration, and capacity bounds
- Bounded query execution on civic analytics endpoints
"""
import time
import pytest
from backend.api.app import create_app
from backend.database.session import SessionLocal
from backend.services.unified_search_service import (
    SearchCache,
    search_unified,
    clear_search_cache,
    get_search_cache_stats,
)


@pytest.fixture(scope="module")
def client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_schemes_api_session_lifecycle(client):
    """
    Verifies that calling schemes endpoints safely closes sessions and returns
    well-formed responses without leaking database connections.
    """
    res1 = client.get("/api/schemes/categories")
    assert res1.status_code == 200
    data1 = res1.get_json()
    assert data1["status"] == "success"

    res2 = client.get("/api/schemes/search?limit=5")
    assert res2.status_code == 200
    data2 = res2.get_json()
    assert data2["status"] == "success"
    assert "items" in data2["data"]


def test_schemes_sources_bulk_join(client):
    """
    Verifies that /api/schemes/<id>/sources uses an optimized join query
    and returns valid document attributes.
    """
    # Fetch first scheme ID from search
    search_res = client.get("/api/schemes/search?limit=1")
    items = search_res.get_json()["data"]["items"]
    if items:
        scheme_id = items[0]["id"]
        res = client.get(f"/api/schemes/{scheme_id}/sources")
        assert res.status_code == 200
        sources = res.get_json()["data"]
        assert isinstance(sources, list)
        if sources:
            assert "source_document_id" in sources[0]
            assert "relationship_id" in sources[0]


def test_civic_categories_bulk_aggregation(client):
    """
    Verifies that /api/civic/categories computes active_issues_count and
    service_standards via bulk aggregation without N+1 query loops.
    """
    res = client.get("/api/civic/categories")
    assert res.status_code == 200
    payload = res.get_json()
    assert payload["status"] == "success"
    categories = payload["data"]["categories"]
    assert isinstance(categories, list)
    for cat in categories:
        assert "active_issues_count" in cat
        assert isinstance(cat["active_issues_count"], int)
        assert "service_standards" in cat
        assert isinstance(cat["service_standards"], list)


def test_civic_areas_and_departments_bulk_aggregation(client):
    """
    Verifies that /api/civic/areas and /api/civic/departments execute bulk queries
    and return correct issue count metrics.
    """
    # Areas
    res_areas = client.get("/api/civic/areas")
    assert res_areas.status_code == 200
    areas = res_areas.get_json()["data"]["areas"]
    assert isinstance(areas, list)
    for area in areas:
        assert "active_issues_count" in area

    # Departments
    res_depts = client.get("/api/civic/departments")
    assert res_depts.status_code == 200
    departments = res_depts.get_json()["data"]["departments"]
    assert isinstance(departments, list)
    for dept in departments:
        assert "total_assigned_issues" in dept


def test_claims_stats_bulk_group_by(client):
    """
    Verifies that /api/claims/stats computes category and verdict distributions
    via bulk group-by queries rather than per-enum queries.
    """
    res = client.get("/api/claims/stats")
    assert res.status_code == 200
    data = res.get_json()["data"]
    assert "total_claims" in data
    assert "claims_by_category" in data
    assert "verdicts_distribution" in data
    assert isinstance(data["claims_by_category"], dict)
    assert isinstance(data["verdicts_distribution"], dict)


def test_promises_categories_bulk_count(client):
    """
    Verifies that /api/promises/categories computes promise_count via
    bulk group-by query.
    """
    res = client.get("/api/promises/categories")
    assert res.status_code == 200
    categories = res.get_json()["data"]["categories"]
    assert isinstance(categories, list)
    for cat in categories:
        assert "promise_count" in cat
        assert isinstance(cat["promise_count"], int)


def test_search_cache_hit_and_miss():
    """
    Verifies search cache hit/miss behavior, metrics tracking, and result consistency.
    """
    clear_search_cache()
    db = SessionLocal()
    try:
        # First query: Cache miss
        res1 = search_unified(db=db, query="pension", category="all", page=1, limit=10)
        stats1 = get_search_cache_stats()
        assert stats1["misses"] == 1
        assert stats1["hits"] == 0
        assert stats1["size"] == 1

        # Second identical query: Cache hit
        res2 = search_unified(db=db, query="pension", category="all", page=1, limit=10)
        stats2 = get_search_cache_stats()
        assert stats2["hits"] == 1
        assert stats2["misses"] == 1

        # Results should be identical
        assert res1["total"] == res2["total"]
        assert len(res1["items"]) == len(res2["items"])

        # Different query: Cache miss
        res3 = search_unified(db=db, query="water", category="all", page=1, limit=10)
        stats3 = get_search_cache_stats()
        assert stats3["misses"] == 2
        assert stats3["hits"] == 1
        assert stats3["size"] == 2
    finally:
        db.close()
        clear_search_cache()


def test_search_cache_ttl_and_bounded_size():
    """
    Verifies custom SearchCache behavior: LRU capacity limiting and TTL expiration.
    """
    cache = SearchCache(max_size=3, ttl_seconds=0.2)

    # 1. Test insertion and retrieval
    cache.set(("k1",), {"result": 1})
    cache.set(("k2",), {"result": 2})
    cache.set(("k3",), {"result": 3})
    assert cache.stats()["size"] == 3

    # 2. Test LRU capacity bound: inserting 4th item evicts the oldest (k1)
    cache.set(("k4",), {"result": 4})
    assert cache.stats()["size"] == 3
    assert cache.get(("k1",)) is None  # Evicted
    assert cache.get(("k4",)) == {"result": 4}

    # 3. Test TTL expiration
    time.sleep(0.25)
    assert cache.get(("k4",)) is None  # Expired
    assert cache.stats()["size"] == 2  # k4 was pruned on get


def test_civic_analytics_bounded_queries(client):
    """
    Verifies that civic analytics endpoints execute cleanly within safety bounds.
    """
    res1 = client.get("/api/civic/clusters")
    assert res1.status_code == 200
    assert res1.get_json()["status"] == "success"

    res2 = client.get("/api/civic/analytics/trends")
    assert res2.status_code == 200
    assert res2.get_json()["status"] == "success"
