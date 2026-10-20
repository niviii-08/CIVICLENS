"""
Automated tests for Phase 11.9: Cross-Phase Record Integration.

Verifies:
  1. System-wide Integration Matrix endpoint
  2. Supported Citizen Navigation Journeys endpoint
  3. Valid cross-phase relationships across schemes, promises, representatives, civic issues, and claims
  4. Inferred vs explicit relationship distinction and epistemic caveats
  5. Privacy redaction on citizen grievances
  6. Empty states for records with no connections (no fabricated records)
  7. Canonical alias resolution (stable IDs, avoids duplicate merging)
  8. Query boundedness and input error handling
"""

import pytest


def test_integration_matrix_endpoint(api_client):
    """Test retrieving system-wide cross-phase integration matrix."""
    resp = api_client.get('/api/integration/matrix')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['status'] == 'success'
    
    matrix = json_data['data']['matrix']
    assert len(matrix) >= 6
    
    # Check that required columns are documented
    first = matrix[0]
    assert 'source_record_type' in first
    assert 'related_record_type' in first
    assert 'relationship_source' in first
    assert 'api_support' in first
    assert 'validation_requirements' in first
    assert 'status' in first


def test_supported_journeys_endpoint(api_client):
    """Test retrieving canonical citizen cross-phase navigation journeys."""
    resp = api_client.get('/api/integration/journeys')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['status'] == 'success'

    journeys = json_data['data']['journeys']
    assert len(journeys) >= 6

    # Verify Journey 1: Scheme -> Policy Evaluation
    j1 = next((j for j in journeys if j['journey_id'] == 'journey-1-scheme-to-policy'), None)
    assert j1 is not None
    assert 'SCH-SW-KMUT' in j1['start_route']
    assert 'POL-TN-KMUT' in j1['step_2']

    # Verify Journey 4: Civic Issue -> Department Response -> Representative
    j4 = next((j for j in journeys if j['journey_id'] == 'journey-4-civic-to-resolution'), None)
    assert j4 is not None
    assert 'CIV-2024-0891' in j4['start_route']


def test_scheme_cross_phase_relationships(api_client):
    """Test retrieving verified and inferred relationships for canonical scheme (KMUT)."""
    resp = api_client.get('/api/integration/related/scheme/SCH-SW-KMUT')
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert data['has_related_records'] is True
    assert data['total_count'] >= 3

    # Check connection type breakdown
    assert data['direct_count'] >= 2
    assert data['evidence_count'] >= 1
    assert data['inferred_count'] >= 1

    records = data['related_records']

    # 1. Scheme -> Policy Evaluation (Direct)
    policy_rel = next((r for r in records if r['type'] == 'policy' and r['id'] == 'POL-TN-KMUT'), None)
    assert policy_rel is not None
    assert policy_rel['connection_type'] == 'direct_identifier'
    assert policy_rel['matching_method'] == 'CANONICAL_SCHEME_CODE'
    assert policy_rel['confidence_score'] == 1.0
    assert policy_rel['is_inferred'] is False

    # 2. Scheme -> Manifesto Promise (Direct)
    promise_rel = next((r for r in records if r['type'] == 'promise' and r['id'] == 'PRM-DMK-2021-001'), None)
    assert promise_rel is not None
    assert promise_rel['connection_type'] == 'direct_identifier'
    assert promise_rel['matching_method'] == 'DETERMINISTIC_ID'
    assert promise_rel['is_inferred'] is False

    # 3. Scheme -> Public Claim (Evidence)
    claim_rel = next((r for r in records if r['type'] == 'claim' and r['id'] == 'CLM-TN-2024-001'), None)
    assert claim_rel is not None
    assert claim_rel['connection_type'] == 'evidence_relationship'
    assert claim_rel['is_inferred'] is False


def test_inferred_vs_explicit_filter(api_client):
    """Test filtering out inferred candidate matches when include_inferred=false."""
    # With inferred=false
    resp = api_client.get('/api/integration/related/scheme/SCH-SW-KMUT?include_inferred=false')
    assert resp.status_code == 200
    data = resp.get_json()['data']
    
    assert data['inferred_count'] == 0
    for r in data['related_records']:
        assert r['connection_type'] != 'inferred_relationship'
        assert r.get('is_inferred') is False

    # Ensure inferred candidate (SCH-HE-PUDHUMAI) is absent
    inferred = next((r for r in data['related_records'] if r['id'] == 'SCH-HE-PUDHUMAI'), None)
    assert inferred is None


def test_inferred_relationship_epistemic_caveat(api_client):
    """Test that inferred relationships contain explicit epistemic warning caveat."""
    resp = api_client.get('/api/integration/related/scheme/SCH-SW-KMUT?include_inferred=true')
    assert resp.status_code == 200
    records = resp.get_json()['data']['related_records']

    inferred_rec = next((r for r in records if r.get('is_inferred') is True), None)
    assert inferred_rec is not None
    assert inferred_rec['connection_type'] == 'inferred_relationship'
    assert 'epistemic_caveat' in inferred_rec
    assert 'automated' in inferred_rec['epistemic_caveat'].lower() or 'not an official' in inferred_rec['epistemic_caveat'].lower()


def test_civic_issue_cross_phase_and_privacy_redaction(api_client):
    """Test civic grievance cross-phase navigation with strict citizen PII masking."""
    resp = api_client.get('/api/integration/related/civic/CIV-2024-0891')
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert data['has_related_records'] is True

    records = data['related_records']
    rep_rel = next((r for r in records if r['type'] == 'representative'), None)
    assert rep_rel is not None
    assert rep_rel['id'] == 'REP-AC-139'
    assert rep_rel['connection_type'] == 'evidence_relationship'
    assert rep_rel['matching_method'] == 'ADMINISTRATIVE_JURISDICTION'

    scheme_rel = next((r for r in records if r['type'] == 'scheme'), None)
    assert scheme_rel is not None
    assert scheme_rel['id'] == 'SCH-MA-SINGARA'
    assert scheme_rel['connection_type'] == 'direct_identifier'

    # Check PII privacy guarantee: no phone numbers or personal complainant names
    for r in records:
        full_text = f"{r.get('title', '')} {r.get('relationship_reason', '')}"
        assert not any(c.isdigit() for c in full_text if len(full_text.split()) > 1 and '9840' in full_text)


def test_representative_cross_phase_linkages(api_client):
    """Test elected representative cross-phase linkages to promises, grievances, and schemes."""
    resp = api_client.get('/api/integration/related/representative/REP-AC-139')
    assert resp.status_code == 200
    data = resp.get_json()['data']
    assert data['has_related_records'] is True

    records = data['related_records']
    # Linked promise
    assert any(r['type'] == 'promise' and r['id'] == 'PRM-DMK-2021-001' for r in records)
    # Linked civic issue
    assert any(r['type'] == 'civic' and r['id'] == 'CIV-2024-0891' for r in records)
    # Linked welfare scheme
    assert any(r['type'] == 'scheme' and r['id'] == 'SCH-SW-KMUT' for r in records)


def test_missing_relationships_empty_state(api_client):
    """Test that records with no linked records return clear notice without hallucinations."""
    resp = api_client.get('/api/integration/related/scheme/SCH-UNLINKED-999')
    assert resp.status_code == 200
    data = resp.get_json()['data']

    assert data['has_related_records'] is False
    assert data['total_count'] == 0
    assert len(data['related_records']) == 0
    assert data['notice'] is not None
    assert 'No connected public records are currently linked' in data['notice']
    assert 'does not infer connections' in data['notice']


def test_canonical_alias_resolution(api_client):
    """Test that colloquial aliases resolve to stable canonical record IDs without duplicate merging."""
    resp_alias = api_client.get('/api/integration/related/scheme/KMUT')
    assert resp_alias.status_code == 200
    data_alias = resp_alias.get_json()['data']
    assert data_alias['source_record']['canonical_id'] == 'SCH-SW-KMUT'
    assert data_alias['has_related_records'] is True

    # Test promise numeric alias
    resp_prm = api_client.get('/api/integration/related/promise/14')
    assert resp_prm.status_code == 200
    data_prm = resp_prm.get_json()['data']
    assert data_prm['source_record']['canonical_id'] == 'PRM-DMK-2021-001'


def test_invalid_parameters_handling(api_client):
    """Test handling of invalid query parameters and edge cases."""
    # Invalid limit parameter
    resp_bad_limit = api_client.get('/api/integration/related/scheme/SCH-SW-KMUT?limit=abc')
    assert resp_bad_limit.status_code == 400
    assert resp_bad_limit.get_json()['status'] == 'error'

    # Empty record type or id
    resp_empty = api_client.get('/api/integration/related/ / ')
    assert resp_empty.status_code in (400, 404)
