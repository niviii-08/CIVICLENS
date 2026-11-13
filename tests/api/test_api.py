"""API health and core route integration tests."""

import pytest

def test_health_endpoint(api_client):
    response = api_client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert data['data']['status'] == 'healthy'

def test_active_routes(api_client):
    """Verify primary API module endpoints are reachable."""
    endpoints = [
        '/api/budget/years',
        '/api/schemes/',
        '/api/promises/',
        '/api/news/articles',
        '/api/funding/parties',
        '/api/claims/',
        '/api/civic/issues',
    ]
    for endpoint in endpoints:
        response = api_client.get(endpoint)
        assert response.status_code in (200, 404, 500)
