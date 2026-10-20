"""
Automated tests for Phase 11.6: Evidence and Source Explorer.
Verifies:
  - Canonical & dynamic evidence dossiers across all record types
  - Distinction of supporting, conflicting, and contextual evidence
  - 5 epistemic uncertainty states
  - Epistemic rules disclaimer
  - Safe document metadata endpoint (no internal file paths or credentials exposed)
  - Safe viewer redirect / offline citizen assistance
"""

import pytest


def test_scheme_evidence_dossier(api_client):
    """Test retrieving evidence dossier for canonical welfare scheme (KMUT)."""
    resp = api_client.get('/api/evidence/records/scheme/SCH-SW-KMUT')
    assert resp.status_code == 200
    json_data = resp.get_json()
    assert json_data['status'] == 'success'
    dossier = json_data['data']['dossier']
    assert dossier['record_id'] == 'SCH-SW-KMUT'
    assert dossier['record_type'] == 'scheme'
    assert dossier['evidence_state'] == 'EVIDENCE_AVAILABLE'
    assert '1.16 Crore' in dossier['statement_explained']
    assert len(dossier['supporting_evidence']) >= 2
    assert len(dossier['contextual_evidence']) >= 1

    # Check statutory tier and integrity checksum
    first_doc = dossier['supporting_evidence'][0]
    assert first_doc['source_tier'] == 'TIER_1_STATUTORY'
    assert first_doc['is_official'] is True
    assert first_doc['relationship_type'] == 'supports'
    assert 'checksum' in first_doc
    assert first_doc['available'] is True

    # Check epistemic principles
    assert 'epistemic_principles' in dossier
    assert 'evidence_strength_rule' in dossier['epistemic_principles']
    assert 'absence_rule' in dossier['epistemic_principles']


def test_promise_conflicting_evidence_dossier(api_client):
    """Test retrieving evidence dossier with conflicting evidence (Petrol VAT promise)."""
    resp = api_client.get('/api/evidence/records/promise/PRM-DMK-2021-003')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['record_id'] == 'PRM-DMK-2021-003'
    assert data['evidence_state'] == 'EVIDENCE_CONFLICTS'
    assert len(data['supporting_evidence']) >= 1
    assert len(data['conflicting_evidence']) >= 1

    conflict = data['conflicting_evidence'][0]
    assert conflict['relationship_type'] == 'contradicts'
    assert 'Comptroller' in conflict['issuing_org'] or 'CAG' in conflict['issuing_org'] or 'CAG' in conflict['title']
    assert conflict['source_tier'] == 'TIER_1_STATUTORY'


def test_claim_conflicting_evidence_dossier(api_client):
    """Test retrieving evidence dossier for public claim fact-check."""
    resp = api_client.get('/api/evidence/records/claim/CLM-TN-2024-001')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['evidence_state'] == 'EVIDENCE_CONFLICTS'
    assert len(data['supporting_evidence']) >= 1
    assert len(data['conflicting_evidence']) >= 1


def test_representative_evidence_dossier(api_client):
    """Test retrieving evidence dossier for elected MLA representative."""
    resp = api_client.get('/api/evidence/records/representative/REP-MLA-042')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['evidence_state'] == 'EVIDENCE_AVAILABLE'
    assert len(data['supporting_evidence']) >= 2


def test_civic_issue_evidence_dossier(api_client):
    """Test retrieving evidence dossier for civic grievance resolution."""
    resp = api_client.get('/api/evidence/records/civic/CIV-2024-0891')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['record_id'] == 'CIV-2024-0891'
    assert data['evidence_state'] == 'EVIDENCE_AVAILABLE'
    assert len(data['supporting_evidence']) >= 1
    # Check that privacy redactions are preserved
    assert 'citizen' in data['plain_summary'].lower() or 'privacy' in str(data).lower()


def test_policy_evaluation_evidence_dossier(api_client):
    """Test retrieving evidence dossier for policy outcome evaluation."""
    resp = api_client.get('/api/evidence/records/policy/POL-TN-KMUT-2023')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['evidence_state'] == 'EVIDENCE_AVAILABLE'
    assert len(data['supporting_evidence']) >= 1


def test_fallback_unregistered_record(api_client):
    """Test safe dynamic synthesis for unknown record IDs without crashing."""
    resp = api_client.get('/api/evidence/records/scheme/SCH-NEW-999')
    assert resp.status_code == 200
    data = resp.get_json()['data']['dossier']
    assert data['record_id'] == 'SCH-NEW-999'
    assert data['evidence_state'] in [
        'EVIDENCE_AVAILABLE',
        'INSUFFICIENT_EVIDENCE',
        'ASSESSMENT_NOT_PERFORMED'
    ]
    assert 'plain_summary' in data


def test_document_metadata_sanitization(api_client):
    """Verify document metadata endpoint strictly hides internal file paths and credentials."""
    resp = api_client.get('/api/evidence/documents/DOC-TN-2023-GO29')
    assert resp.status_code == 200
    doc = resp.get_json()['data']
    assert doc['id'] == 'DOC-TN-2023-GO29'
    assert doc['source_tier'] == 'TIER_1_STATUTORY'
    assert doc['is_official'] is True

    # Critical security assertion: no internal filesystem paths or tokens
    doc_str = str(doc)
    assert 'C:\\' not in doc_str
    assert '/var/' not in doc_str
    assert 'password' not in doc_str.lower()
    assert 'secret' not in doc_str.lower()


def test_offline_document_safe_guidance(api_client):
    """Verify offline / physical document returns safe citizen guidance."""
    resp = api_client.get('/api/evidence/documents/DOC-SLBC-MINUTES-2023')
    assert resp.status_code == 200
    doc = resp.get_json()['data']
    assert doc['available'] is False
    assert 'offline_reason' in doc
    assert 'safe_alternative' in doc
    assert 'SLBC' in doc['safe_alternative']


def test_document_viewer_safe_redirect_and_offline_notice(api_client):
    """Test safe document redirection to verified external URL and offline guidance."""
    # 1. Online document redirects safely
    resp_online = api_client.get('/api/evidence/documents/DOC-GO-MS-58-2023/view')
    assert resp_online.status_code == 302
    assert 'https://cms.tn.gov.in' in resp_online.headers['Location']

    # 2. Offline document returns structured explanation without exposing paths
    resp_offline = api_client.get('/api/evidence/documents/DOC-SLBC-MINUTES-2023/view')
    assert resp_offline.status_code == 200
    offline_data = resp_offline.get_json()
    assert offline_data.get('status') == 'info' or 'Archive' in str(offline_data)
    assert 'offline_access_instructions' in offline_data or 'safe_alternative' in offline_data
    assert 'C:\\' not in str(offline_data)
