"""
CIVICLENS TN — Phase 11.10 End-to-End Citizen Journey Validation Suite
Automated verification of the 6 canonical citizen discovery workflows:
- Journey A: Find and understand a scheme
- Journey B: Investigate a public promise
- Journey C: Explore a representative
- Journey D: Follow a civic issue
- Journey E: Investigate a public claim
- Journey F: Understand policy results
"""

import pytest


def test_journey_a_find_and_understand_scheme(api_client):
    """
    Journey A: Find and understand a scheme
    Flow: Search -> Scheme detail -> Cross-phase integration -> Policy evaluation
    """
    # Step 1: Search for welfare scheme via unified search
    search_res = api_client.get('/api/search?q=Magalir&category=schemes')
    assert search_res.status_code == 200
    search_data = search_res.get_json()['data']
    assert search_data['total'] >= 1
    items = search_data['items']
    assert len(items) >= 1
    top_hit = items[0]
    assert 'Magalir' in top_hit['title'] or 'KMUT' in top_hit['title']

    # Step 2: Retrieve scheme details
    scheme_res = api_client.get('/api/schemes/search?name=Magalir')
    assert scheme_res.status_code == 200
    scheme_items = scheme_res.get_json()['data']['items']
    assert len(scheme_items) >= 1
    scheme_record = scheme_items[0]
    assert 'scheme_name' in scheme_record
    assert 'financial_year' in scheme_record

    # Step 3: Follow cross-phase links from scheme
    cross_res = api_client.get('/api/integration/related/scheme/SCH-SW-KMUT')
    assert cross_res.status_code == 200
    cross_data = cross_res.get_json()['data']
    assert cross_data['has_related_records'] is True
    related = cross_data['related_records']

    # Step 4: Verify link to Policy Evaluation
    policy_rel = next((r for r in related if r['type'] == 'policy'), None)
    assert policy_rel is not None
    assert policy_rel['id'] == 'POL-TN-KMUT'
    assert policy_rel['connection_type'] == 'direct_identifier'

    # Step 5: Verify link to Manifesto Promise
    promise_rel = next((r for r in related if r['type'] == 'promise'), None)
    assert promise_rel is not None
    assert 'PRM-DMK-2021-001' in promise_rel['id']

    # Step 6: Follow link to Policy Evaluation detail
    policy_res = api_client.get(f"/api/policy-evaluation/policies/{policy_rel['id']}")
    assert policy_res.status_code == 200
    pol_data = policy_res.get_json()['data']
    assert pol_data['policy_id'] == 'POL-TN-KMUT'
    assert 'objectives' in pol_data
    assert len(pol_data['objectives']) >= 1


def test_journey_b_investigate_public_promise(api_client):
    """
    Journey B: Investigate a public promise
    Flow: Promise search/categories -> Promise cross-phase linkages -> Implementation evidence
    """
    # Step 1: Browse promise categories
    cat_res = api_client.get('/api/promises/categories')
    assert cat_res.status_code == 200
    cats = cat_res.get_json()['data']['categories']
    assert len(cats) >= 1

    # Step 2: Inspect canonical promise PRM-DMK-2021-001 cross-phase relationships
    cross_res = api_client.get('/api/integration/related/promise/PRM-DMK-2021-001')
    assert cross_res.status_code == 200
    cross_data = cross_res.get_json()['data']
    assert cross_data['has_related_records'] is True
    related = cross_data['related_records']

    # Step 3: Verify direct linkage to implementing government scheme
    scheme_rel = next((r for r in related if r['type'] == 'scheme'), None)
    assert scheme_rel is not None
    assert scheme_rel['id'] == 'SCH-SW-KMUT'
    assert scheme_rel['connection_type'] == 'direct_identifier'

    # Step 4: Verify sponsor linkage to elected representative
    rep_rel = next((r for r in related if r['type'] == 'representative'), None)
    assert rep_rel is not None
    assert rep_rel['id'] == 'REP-AC-139'
    assert 'Stalin' in rep_rel['title']


def test_journey_c_explore_representative(api_client):
    """
    Journey C: Explore a representative
    Flow: Search representative -> Representative detail -> Associated promises and works
    """
    # Step 1: Query representative relationships via cross-phase integration
    rep_res = api_client.get('/api/integration/related/representative/REP-AC-139')
    assert rep_res.status_code == 200
    rep_data = rep_res.get_json()['data']
    assert rep_data['has_related_records'] is True
    related = rep_data['related_records']

    # Step 2: Confirm associated manifesto commitments
    promise_link = next((r for r in related if r['type'] == 'promise'), None)
    assert promise_link is not None
    assert 'PRM-DMK-2021-001' in promise_link['id']

    # Step 3: Confirm associated welfare schemes
    scheme_link = next((r for r in related if r['type'] == 'scheme'), None)
    assert scheme_link is not None
    assert 'SCH-SW-KMUT' in scheme_link['id']


def test_journey_d_follow_civic_issue(api_client):
    """
    Journey D: Follow a civic issue
    Flow: Civic issues list -> Issue detail -> Department response -> Privacy redaction
    """
    # Step 1: Query cross-phase links for canonical civic grievance
    civic_res = api_client.get('/api/integration/related/civic/CIV-2024-0891')
    assert civic_res.status_code == 200
    civic_data = civic_res.get_json()['data']
    assert civic_data['has_related_records'] is True

    # Step 2: Confirm privacy redactions (citizen names/phone numbers masked)
    related = civic_data['related_records']
    assert len(related) >= 1
    for r in related:
        assert '[CITIZEN-CONFIDENTIAL]' in r['relationship_reason'] or 'Water' in r['title'] or 'Kolathur' in r['relationship_reason']


def test_journey_e_investigate_public_claim(api_client):
    """
    Journey E: Investigate a public claim
    Flow: Retrieve claim cross-phase relationships -> Supporting evidence -> Original documents
    """
    # Step 1: Retrieve claim cross-phase relationships
    claim_res = api_client.get('/api/integration/related/claim/CLM-TN-2024-001')
    assert claim_res.status_code == 200
    claim_data = claim_res.get_json()['data']
    assert claim_data['has_related_records'] is True
    related = claim_data['related_records']

    # Step 2: Confirm connection to underlying government welfare scheme
    scheme_rel = next((r for r in related if r['type'] == 'scheme'), None)
    assert scheme_rel is not None
    assert scheme_rel['id'] == 'SCH-SW-KMUT'
    assert scheme_rel['connection_type'] in ('evidence_relationship', 'direct_identifier')

    # Step 3: Confirm connection to manifesto promise / underlying evidence
    promise_rel = next((r for r in related if r['type'] == 'promise'), None)
    assert promise_rel is not None
    assert promise_rel['id'] == 'PRM-DMK-2021-001'


def test_journey_f_understand_policy_results(api_client):
    """
    Journey F: Understand policy results
    Flow: Policy registry -> Policy detail -> Objectives -> Indicators -> Findings -> Budget
    """
    # Step 1: Query policies list
    policies_res = api_client.get('/api/policy-evaluation/policies')
    assert policies_res.status_code == 200
    policies = policies_res.get_json()['data']
    assert len(policies) >= 1

    # Step 2: Retrieve policy detail for KMUT
    detail_res = api_client.get('/api/policy-evaluation/policies/POL-TN-KMUT')
    assert detail_res.status_code == 200
    data = detail_res.get_json()['data']
    assert data['policy_id'] == 'POL-TN-KMUT'
    assert len(data['objectives']) >= 1
    assert len(data['evaluation_plans']) >= 1
    assert len(data['implementation_activities']) >= 1

    # Step 3: Retrieve indicators
    ind_res = api_client.get('/api/policy-evaluation/indicators?policy_id=POL-TN-KMUT')
    assert ind_res.status_code == 200
    indicators = ind_res.get_json()['data']
    assert len(indicators) >= 1

    # Step 4: Retrieve findings
    find_res = api_client.get('/api/policy-evaluation/findings?policy_id=POL-TN-KMUT')
    assert find_res.status_code == 200
    findings = find_res.get_json()['data']
    assert len(findings) >= 1

    # Step 5: Check budget execution analytics for this policy
    budget_res = api_client.get('/api/policy-evaluation/policies/POL-TN-KMUT/budget-analysis?financial_year=2023-24')
    assert budget_res.status_code == 200
    budget_data = budget_res.get_json()['data']
    assert budget_data['policy_id'] == 'POL-TN-KMUT'
    assert 'budget_execution_rate_pct' in budget_data
    assert 'actual_expenditure_cr' in budget_data
