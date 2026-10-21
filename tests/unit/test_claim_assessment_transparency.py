"""
CIVICLENS TN — Unit Tests for Evidence-Based Claim Assessment
Phase 13.4: Transparent Citizen Dossiers, 5-Tier Taxonomy, Provenance, and Epistemic Guardrails.

Verifies:
1. Canonical supported claim assessment (Kalaignar Magalir Urimai Thittam DBT).
2. Contradicted claim assessment with empirical CAG audit citations.
3. Mixed / Partially supported multi-part proposition breakdown.
4. Missing important context / misleading scope assessment.
5. Insufficient evidence and the non-prejudice rule (absence != falsehood).
6. Source conflict detection and divergent evidence surfacing.
7. Outdated baseline detection and temporal integrity warnings.
8. Separation of original claim wording/speaker from platform assessment.
9. Political neutrality guardrail (party affiliation never implies truth/falsehood).
10. REST API endpoint GET /api/claims/<claim_id>/assessment end-to-end.
"""

import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.base_class import Base
from backend.models.claim import (
    Claim,
    AtomicClaim,
    EvidenceDocument,
    EvidencePassage,
    ClaimEvidenceRelationship,
    VerificationResult,
    VerificationRun,
    VerificationOutcome,
    VerificationVerdict,
    EvidenceRelationshipType,
    SourceTier,
    ClaimCategory,
    CandidateSourceType,
    AttributionType,
)
from backend.services.claim_assessment_service import (
    ClaimAssessmentService,
    EPISTEMIC_POLITICAL_NEUTRALITY,
    EPISTEMIC_NON_PREJUDICE_ABSENCE,
)
from backend.api.app import create_app


@pytest.fixture
def assessment_db():
    """Isolated in-memory SQLite database session populated with multi-tier claim scenarios."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Documents
    doc_gazette = EvidenceDocument(
        document_id="EDOC-STATUTORY-GAZETTE-01",
        source_tier=SourceTier.TIER_1_STATUTORY,
        source_name="Tamil Nadu Government Gazette No. 41",
        publisher="Department of Social Welfare, GoTN",
        document_type="GOVERNMENT_ORDER",
        source_category="OFFICIAL_GOVERNMENT",
        title="Operational Rules for Women Basic Income Grant",
        publication_date=datetime(2023, 8, 1, tzinfo=timezone.utc),
        source_url="https://cms.tn.gov.in/gazette/go41.pdf",
        file_hash_sha256="hash-gazette-01-mock",
        is_official=True,
    )
    pass_gazette = EvidencePassage(
        passage_id="PASS-GAZETTE-01",
        document_id="EDOC-STATUTORY-GAZETTE-01",
        passage_text="Government Order confirms sanction of monthly grant of Rs 1,000 for verified women heads of families.",
        page_number=4,
    )

    doc_cag = EvidenceDocument(
        document_id="EDOC-CAG-AUDIT-2024",
        source_tier=SourceTier.TIER_1_STATUTORY,
        source_name="Comptroller and Auditor General Audit Report 2024",
        publisher="Comptroller and Auditor General of India",
        document_type="CAG_AUDIT",
        source_category="OFFICIAL_GOVERNMENT",
        title="Audit on State Expenditure Performance",
        publication_date=datetime(2024, 4, 15, tzinfo=timezone.utc),
        source_url="https://cag.gov.in/tn/audit2024.pdf",
        file_hash_sha256="hash-cag-01-mock",
        is_official=True,
    )
    pass_cag = EvidencePassage(
        passage_id="PASS-CAG-01",
        document_id="EDOC-CAG-AUDIT-2024",
        passage_text="Audit inspection confirmed that reported road construction reached only 42 km against the claimed 250 km.",
        page_number=18,
    )

    doc_old = EvidenceDocument(
        document_id="EDOC-HISTORICAL-2016",
        source_tier=SourceTier.TIER_1_STATUTORY,
        source_name="State Planning Commission Baseline 2016",
        publisher="State Planning Commission, TN",
        document_type="POLICY_BRIEF",
        source_category="OFFICIAL_GOVERNMENT",
        title="Infrastructure Baseline Report 2016",
        publication_date=datetime(2016, 5, 10, tzinfo=timezone.utc),
        source_url="https://spc.tn.gov.in/baseline2016.pdf",
        file_hash_sha256="hash-old-01-mock",
        is_official=True,
    )
    pass_old = EvidencePassage(
        passage_id="PASS-OLD-01",
        document_id="EDOC-HISTORICAL-2016",
        passage_text="Under 2016 norms, eligibility threshold was capped at Rs 1.2 Lakh household income.",
        page_number=12,
    )

    session.add_all([doc_gazette, pass_gazette, doc_cag, pass_cag, doc_old, pass_old])
    session.commit()

    # Scenario 1: Supported Claim
    claim_supp = Claim(
        claim_id="CLM-TEST-SUPP",
        original_text="Government established Rs 1,000 monthly entitlement for eligible women.",
        normalized_text="government established rs 1000 monthly entitlement for eligible women",
        claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
        speaker_name="State Spokesperson",
        speaker_role="Official",
        speaker_party="Ruling Party",
        attribution_type=AttributionType.DIRECT_QUOTE,
        claim_date=datetime(2023, 9, 15, tzinfo=timezone.utc),
    )
    rel_supp = ClaimEvidenceRelationship(
        relationship_id="REL-TEST-SUPP-1",
        claim_id=claim_supp.claim_id,
        evidence_document_id=doc_gazette.document_id,
        passage_id=pass_gazette.passage_id,
        relationship_type=EvidenceRelationshipType.SUPPORTS,
        supporting_text_reference="sanction of monthly grant of Rs 1,000",
        confidence_score=0.95,
        relevance_score=0.95,
    )
    res_supp = VerificationResult(
        result_id="VRES-TEST-SUPP",
        claim_id=claim_supp.claim_id,
        outcome=VerificationOutcome.SUPPORTED_BY_AVAILABLE_EVIDENCE,
        verdict=VerificationVerdict.SUPPORTED,
        confidence=0.95,
        explanation="Corroborated by Official Government Order.",
        is_current=True,
        verification_timestamp=datetime(2023, 9, 16, tzinfo=timezone.utc),
    )
    session.add_all([claim_supp, rel_supp, res_supp])

    # Scenario 2: Contradicted Claim
    claim_contra = Claim(
        claim_id="CLM-TEST-CONTRA",
        original_text="Over 250 kilometers of arterial highway were completed in the district this fiscal year.",
        normalized_text="over 250 kilometers of arterial highway were completed in the district this fiscal year",
        claim_category=ClaimCategory.PUBLIC_INFRASTRUCTURE,
        speaker_name="Opposition Leader",
        speaker_role="Member of Legislative Assembly",
        speaker_party="Opposition Party",
        attribution_type=AttributionType.DIRECT_QUOTE,
        claim_date=datetime(2024, 5, 1, tzinfo=timezone.utc),
    )
    rel_contra = ClaimEvidenceRelationship(
        relationship_id="REL-TEST-CONTRA-1",
        claim_id=claim_contra.claim_id,
        evidence_document_id=doc_cag.document_id,
        passage_id=pass_cag.passage_id,
        relationship_type=EvidenceRelationshipType.CONTRADICTS,
        contradicting_text_reference="reached only 42 km against the claimed 250 km",
        confidence_score=0.92,
        relevance_score=0.92,
    )
    res_contra = VerificationResult(
        result_id="VRES-TEST-CONTRA",
        claim_id=claim_contra.claim_id,
        outcome=VerificationOutcome.CONTRADICTED_BY_AVAILABLE_EVIDENCE,
        verdict=VerificationVerdict.CONTRADICTED,
        confidence=0.92,
        explanation="Contradicted by empirical CAG audit findings.",
        is_current=True,
        verification_timestamp=datetime(2024, 5, 2, tzinfo=timezone.utc),
    )
    session.add_all([claim_contra, rel_contra, res_contra])

    # Scenario 3: Mixed / Partially Supported Claim with Atomic Claims
    claim_mixed = Claim(
        claim_id="CLM-TEST-MIXED",
        original_text="The welfare scheme granted Rs 1,000 monthly and completed 250 km highway.",
        normalized_text="the welfare scheme granted rs 1000 monthly and completed 250 km highway",
        claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
        speaker_name="Cabinet Minister",
        speaker_role="Minister",
        speaker_party="Ruling Party",
        attribution_type=AttributionType.DIRECT_QUOTE,
        claim_date=datetime(2024, 6, 1, tzinfo=timezone.utc),
    )
    ac_mixed_1 = AtomicClaim(
        atomic_claim_id="AC-MIXED-1",
        claim_id=claim_mixed.claim_id,
        atomic_claim_text="Welfare scheme granted Rs 1,000 monthly.",
        subject="Welfare scheme",
        predicate="granted Rs 1,000 monthly",
        verifiability_status="VERIFIABLE",
    )
    ac_mixed_2 = AtomicClaim(
        atomic_claim_id="AC-MIXED-2",
        claim_id=claim_mixed.claim_id,
        atomic_claim_text="Completed 250 km highway.",
        subject="Highway construction",
        predicate="completed 250 km",
        verifiability_status="VERIFIABLE",
    )
    rel_mix_1 = ClaimEvidenceRelationship(
        relationship_id="REL-TEST-MIX-1",
        claim_id=claim_mixed.claim_id,
        atomic_claim_id=ac_mixed_1.atomic_claim_id,
        evidence_document_id=doc_gazette.document_id,
        passage_id=pass_gazette.passage_id,
        relationship_type=EvidenceRelationshipType.SUPPORTS,
        confidence_score=0.90,
    )
    rel_mix_2 = ClaimEvidenceRelationship(
        relationship_id="REL-TEST-MIX-2",
        claim_id=claim_mixed.claim_id,
        atomic_claim_id=ac_mixed_2.atomic_claim_id,
        evidence_document_id=doc_cag.document_id,
        passage_id=pass_cag.passage_id,
        relationship_type=EvidenceRelationshipType.CONTRADICTS,
        confidence_score=0.90,
    )
    res_mixed = VerificationResult(
        result_id="VRES-TEST-MIXED",
        claim_id=claim_mixed.claim_id,
        outcome=VerificationOutcome.PARTIALLY_SUPPORTED,
        verdict=VerificationVerdict.PARTIALLY_SUPPORTED,
        confidence=0.78,
        explanation="Sub-claim 1 is supported by Government Order, but sub-claim 2 is refuted by CAG audit.",
        is_current=True,
        verification_timestamp=datetime(2024, 6, 2, tzinfo=timezone.utc),
    )
    session.add_all([claim_mixed, ac_mixed_1, ac_mixed_2, rel_mix_1, rel_mix_2, res_mixed])

    # Scenario 4: Missing Important Context / Misleading Scope
    claim_ctx = Claim(
        claim_id="CLM-TEST-CONTEXT",
        original_text="Eligibility for the grant remains restricted to families earning below Rs 1.2 Lakh.",
        normalized_text="eligibility for the grant remains restricted to families earning below rs 1 2 lakh",
        claim_category=ClaimCategory.GOVERNMENT_SCHEMES,
        speaker_name="Independent Commentator",
        speaker_role="Journalist",
        speaker_party="Independent",
        attribution_type=AttributionType.JOURNALIST_DESCRIPTION,
        claim_date=datetime(2024, 7, 1, tzinfo=timezone.utc),
    )
    rel_ctx = ClaimEvidenceRelationship(
        relationship_id="REL-TEST-CTX-1",
        claim_id=claim_ctx.claim_id,
        evidence_document_id=doc_old.document_id,
        passage_id=pass_old.passage_id,
        relationship_type=EvidenceRelationshipType.CONTEXTUALIZES,
        is_outdated=True,
        confidence_score=0.85,
    )
    res_ctx = VerificationResult(
        result_id="VRES-TEST-CONTEXT",
        claim_id=claim_ctx.claim_id,
        outcome=VerificationOutcome.MISSING_IMPORTANT_CONTEXT,
        verdict=VerificationVerdict.MISLEADING_CONTEXT,
        confidence=0.82,
        explanation="Omission of updated 2023 eligibility threshold revisions.",
        is_current=True,
        verification_timestamp=datetime(2024, 7, 2, tzinfo=timezone.utc),
    )
    session.add_all([claim_ctx, rel_ctx, res_ctx])

    # Scenario 5: Insufficient Evidence / Unverifiable
    claim_unverif = Claim(
        claim_id="CLM-TEST-UNVERIF",
        original_text="Secret administrative decisions were taken to alter future pension allocations.",
        normalized_text="secret administrative decisions were taken to alter future pension allocations",
        claim_category=ClaimCategory.OTHER_PUBLIC_INTEREST,
        speaker_name="Anonymous Source",
        speaker_role="Citizen",
        speaker_party="Unaffiliated",
        attribution_type=AttributionType.USER_SUBMITTED,
        claim_date=datetime(2024, 8, 1, tzinfo=timezone.utc),
    )
    res_unverif = VerificationResult(
        result_id="VRES-TEST-UNVERIF",
        claim_id=claim_unverif.claim_id,
        outcome=VerificationOutcome.UNVERIFIABLE,
        verdict=VerificationVerdict.UNVERIFIABLE_INSUFFICIENT_EVIDENCE,
        confidence=0.30,
        explanation="No corroborating state gazette or legislative filing exists.",
        is_current=True,
        verification_timestamp=datetime(2024, 8, 2, tzinfo=timezone.utc),
    )
    session.add_all([claim_unverif, res_unverif])

    session.commit()
    yield session
    session.close()


@pytest.fixture
def api_client():
    """Flask test client."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# --- 1. Canonical Ground-Truth Supported Claim ---
def test_canonical_supported_claim_dossier():
    service = ClaimAssessmentService()
    dossier = service.get_claim_assessment_dossier("CLM-TN-2024-001")

    assert dossier["claim_id"] == "CLM-TN-2024-001"
    assert "original_claim" in dossier
    assert "evidentiary_assessment" in dossier

    # Verify separation
    orig = dossier["original_claim"]
    assert "Kalaignar Magalir Urimai Thittam" in orig["original_text"]
    assert orig["speaker"]["name"] == "M.K. Stalin"
    assert orig["speaker"]["party_affiliation"] == "DMK"

    # Verify assessment classification
    assess = dossier["evidentiary_assessment"]
    assert assess["tier_category"] == "SUPPORTED_BY_AVAILABLE_EVIDENCE"
    assert assess["citizen_label"] == "Supported by Available Evidence"
    assert assess["confidence_score"] >= 0.90
    assert not assess["source_conflict_detected"]

    # Verify documentary citations
    evidence = dossier["evidence_breakdown"]
    assert len(evidence["supporting_evidence"]) >= 1
    top_supp = evidence["supporting_evidence"][0]
    assert top_supp["document"]["source_tier"] == "TIER_1_STATUTORY"
    assert top_supp["document"]["official_url"] is not None


# --- 2. Contradicted Claim Assessment ---
def test_contradicted_claim_assessment(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-CONTRA")

    assess = dossier["evidentiary_assessment"]
    assert assess["tier_category"] == "CONTRADICTED_BY_AVAILABLE_EVIDENCE"
    assert assess["citizen_label"] == "Contradicted by Available Evidence"
    assert assess["verdict_tag"] == "CONTRADICTED"

    evidence = dossier["evidence_breakdown"]
    assert len(evidence["contradicting_evidence"]) == 1
    contra = evidence["contradicting_evidence"][0]
    assert "reached only 42 km" in contra["extracted_passage_text"]
    assert contra["document"]["title"] == "Audit on State Expenditure Performance"


# --- 3. Mixed / Partially Supported Claim with Propositions ---
def test_mixed_partially_supported_claim(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-MIXED")

    assess = dossier["evidentiary_assessment"]
    assert assess["tier_category"] == "PARTIALLY_SUPPORTED"
    assert assess["citizen_label"] == "Mixed / Partially Supported"

    props = dossier["proposition_breakdown"]["propositions"]
    assert len(props) == 2
    p1 = next(p for p in props if p["atomic_id"] == "AC-MIXED-1")
    p2 = next(p for p in props if p["atomic_id"] == "AC-MIXED-2")

    assert p1["resolution_status"] == "SUPPORTED"
    assert p2["resolution_status"] == "CONTRADICTED"


# --- 4. Missing Important Context Assessment ---
def test_missing_important_context_claim(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-CONTEXT")

    assess = dossier["evidentiary_assessment"]
    assert assess["tier_category"] == "MISSING_IMPORTANT_CONTEXT"
    assert assess["citizen_label"] == "Missing Important Context"

    evidence = dossier["evidence_breakdown"]
    assert len(evidence["contextual_evidence"]) == 1
    ctx = evidence["contextual_evidence"][0]
    assert ctx["is_outdated"] is True


# --- 5. Insufficient Evidence and Non-Prejudice Principle ---
def test_insufficient_evidence_non_prejudice_rule(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-UNVERIF")

    assess = dossier["evidentiary_assessment"]
    assert assess["tier_category"] == "INSUFFICIENT_EVIDENCE"
    assert assess["citizen_label"] == "Unverifiable / Insufficient Evidence"

    # CRITICAL: Absence of evidence MUST NOT be treated as proof of falsehood
    assert assess["verdict_tag"] != "CONTRADICTED"
    assert "Absence of evidence is not proof of falsehood" in assess["plain_language_summary"]
    assert "NON-PREJUDICE GUARDRAIL" in assess["non_prejudice_principle"]


# --- 6. Direct Source Conflict Detection ---
def test_source_conflict_detection(assessment_db):
    # Add conflicting document to CLM-TEST-SUPP
    doc_opp = EvidenceDocument(
        document_id="EDOC-OPPOSITION-MEMO",
        source_tier=SourceTier.TIER_2_OFFICIAL_AGENCY,
        source_name="Legislative Minority Memorandum",
        document_type="OFFICIAL_REPORT",
        title="Field Assessment Review",
        file_hash_sha256="hash-opp-memo-99",
    )
    pass_opp = EvidencePassage(
        passage_id="PASS-OPP-99",
        document_id="EDOC-OPPOSITION-MEMO",
        passage_text="Field surveys indicate only 60 percent received the credited amount in rural districts.",
    )
    rel_contra = ClaimEvidenceRelationship(
        relationship_id="REL-CONFLICT-99",
        claim_id="CLM-TEST-SUPP",
        evidence_document_id=doc_opp.document_id,
        passage_id=pass_opp.passage_id,
        relationship_type=EvidenceRelationshipType.CONTRADICTS,
    )
    assessment_db.add_all([doc_opp, pass_opp, rel_contra])
    assessment_db.commit()

    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-SUPP")

    assess = dossier["evidentiary_assessment"]
    assert assess["source_conflict_detected"] is True
    assert any("Direct source conflict" in r for r in assess["uncertainty_reasons"])


# --- 7. Strict Separation of Original Claim from Assessment ---
def test_strict_separation_of_claim_from_assessment(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)
    dossier = service.get_claim_assessment_dossier("CLM-TEST-SUPP")

    # Original claim contains speaker and statement words
    orig = dossier["original_claim"]
    assert orig["speaker"]["name"] == "State Spokesperson"
    assert orig["speaker"]["party_affiliation"] == "Ruling Party"
    assert "Rs 1,000 monthly" in orig["original_text"]

    # Assessment contains platform verdict, reasons, and guardrails
    assess = dossier["evidentiary_assessment"]
    assert "State Spokesperson" not in assess["technical_explanation"]
    assert assess["epistemic_guardrail"] == EPISTEMIC_POLITICAL_NEUTRALITY
    assert assess["non_prejudice_principle"] == EPISTEMIC_NON_PREJUDICE_ABSENCE


# --- 8. Political Neutrality Guardrail ---
def test_political_neutrality_guardrail(assessment_db):
    service = ClaimAssessmentService(db=assessment_db)

    dossier_ruling = service.get_claim_assessment_dossier("CLM-TEST-SUPP")
    dossier_opp = service.get_claim_assessment_dossier("CLM-TEST-CONTRA")

    assert "POLITICAL NEUTRALITY GUARDRAIL" in dossier_ruling["evidentiary_assessment"]["epistemic_guardrail"]
    assert "POLITICAL NEUTRALITY GUARDRAIL" in dossier_opp["evidentiary_assessment"]["epistemic_guardrail"]

    # Both assess solely on documentary evidence
    assert dossier_ruling["evidentiary_assessment"]["tier_category"] == "SUPPORTED_BY_AVAILABLE_EVIDENCE"
    assert dossier_opp["evidentiary_assessment"]["tier_category"] == "CONTRADICTED_BY_AVAILABLE_EVIDENCE"


# --- 9. REST API GET /api/claims/<claim_id>/assessment ---
def test_api_get_claim_assessment_endpoint(api_client):
    response = api_client.get("/api/claims/CLM-TN-2024-001/assessment")
    assert response.status_code == 200
    res_data = response.get_json()

    assert res_data["status"] == "success"
    data = res_data["data"]
    assert data["claim_id"] == "CLM-TN-2024-001"
    assert data["evidentiary_assessment"]["tier_category"] == "SUPPORTED_BY_AVAILABLE_EVIDENCE"
    assert len(data["evidence_breakdown"]["supporting_evidence"]) >= 1


# --- 10. REST API 404 for Unknown Claim ---
def test_api_get_claim_assessment_not_found(api_client):
    response = api_client.get("/api/claims/CLM-TOTALLY-UNKNOWN-99999/assessment")
    assert response.status_code == 404
    res_data = response.get_json()
    assert res_data["status"] == "error"
    assert "not found in the verified public database" in res_data["message"]
