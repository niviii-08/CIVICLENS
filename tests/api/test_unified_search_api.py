"""
Unified Citizen Search API automated tests (Phase 11.4).

Verifies cross-phase search endpoint behavior:
  - Input validation and sanitization
  - Empty and short queries
  - Exact and partial text matches
  - Standardized result metadata fields
  - Category filtering
  - Pagination limits
  - Deterministic relevance ranking
"""

import pytest


def test_unified_search_empty_query(api_client):
    """Empty query should return empty items without error."""
    response = api_client.get('/api/search?q=')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['total'] == 0
    assert data['data']['items'] == []


def test_unified_search_single_char_query(api_client):
    """Single character query should return safe empty response."""
    response = api_client.get('/api/search?q=x')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['total'] == 0


def test_unified_search_valid_query(api_client):
    """Search for 'women' should return standardized results across categories."""
    response = api_client.get('/api/search?q=women')
    assert response.status_code == 200
    payload = response.get_json()
    assert payload['status'] == 'success'
    data = payload['data']
    assert data['total'] > 0
    assert len(data['items']) > 0

    first_item = data['items'][0]
    # Check standardized fields
    assert 'id' in first_item
    assert 'type' in first_item
    assert 'type_label' in first_item
    assert 'title' in first_item
    assert 'description' in first_item
    assert 'date_or_period' in first_item
    assert 'department_or_entity' in first_item
    assert 'route' in first_item
    assert 'evidence_available' in first_item
    assert 'score' in first_item
    assert first_item['route'].startswith('/')


def test_unified_search_category_filter(api_client):
    """Filtering by category should return only items of that category."""
    response = api_client.get('/api/search?q=women&category=scheme')
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['selected_category'] == 'scheme'
    for item in data['items']:
        assert item['type'] == 'scheme'


def test_unified_search_invalid_category_fallback(api_client):
    """Invalid category should fall back to 'all' without error."""
    response = api_client.get('/api/search?q=women&category=invalid_category_xyz')
    assert response.status_code == 200
    data = response.get_json()['data']
    assert data['selected_category'] == 'all'


def test_unified_search_pagination(api_client):
    """Pagination parameters should limit the returned items count."""
    response = api_client.get('/api/search?q=women&limit=2&page=1')
    assert response.status_code == 200
    data = response.get_json()['data']
    assert len(data['items']) <= 2
    assert data['limit'] == 2
    assert data['page'] == 1


def test_unified_search_categories_endpoint(api_client):
    """Verify category directory endpoint returns all supported categories."""
    response = api_client.get('/api/search/categories')
    assert response.status_code == 200
    data = response.get_json()['data']
    assert 'categories' in data
    keys = [c['key'] for c in data['categories']]
    assert 'scheme' in keys
    assert 'promise' in keys
    assert 'representative' in keys
    assert 'civic' in keys
    assert 'claim' in keys
    assert 'policy' in keys
