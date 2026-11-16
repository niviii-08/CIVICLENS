"""
Unit Tests for Phase 11.2 — Public Accountability Lifecycle Engine
"""
import pytest
from datetime import datetime, timezone, date, timedelta
from backend.models.accountability import (
    AccountabilityCase, InstitutionalAttribution, OfficialResponse,
    CorrectiveAction, OutcomeVerification, CaseStatus, CaseSeverity,
    CaseTriggerType, GroundOutcomeStatus, ResponseChannel, ResponseReceiptStatus,
    CorrectiveActionType, ActionExecutionStatus, GroundVerificationMethod, DiscrepancyAdmittance
)
from backend.services.accountability_service import AccountabilityService
from backend.models.provenance import enforce_bns_defamation_guardrail


def test_case_creation_with_bitemporal_fields(db_session):
    """Verify accountability cases create with valid_from and transaction_time bitemporal fields."""
    case = AccountabilityService.create_case(
        db=db_session,
        case_id="TEST-CASE-2024-001",
        title="Test Water Drainage Discrepancy",
        description="Observed mismatch between allocated desilting funds and physical drain cross-section.",
        governance_domain="Water Resources",
        trigger_type=CaseTriggerType.BUDGET_DISCREPANCY,
        trigger_entity_id="SCH-TN-WRD-01",
        severity=CaseSeverity.HIGH,
        financial_implication_cr=12.5,
    )
    assert case.id is not None
    assert case.status == CaseStatus.OPEN
    assert case.valid_from is not None
    assert case.transaction_time is not None
    assert case.evidence_provenance_hash is not None


def test_bns_defamation_guardrail_prevents_criminal_labeling():
    """Verify BNS 2023 Sec 356 guardrail forbids unverified corrupt/criminal accusation terms."""
    with pytest.raises(ValueError) as excinfo:
        enforce_bns_defamation_guardrail("The official is corrupt and ran a massive scam.")
    assert "BNS 2023 Sec 356 Defamation Safeguard Breach" in str(excinfo.value)

    # Compliant statement does not raise
    enforce_bns_defamation_guardrail(
        "Administrative records indicate a discrepancy between budget allocation and utilization vouchers."
    )


def test_institutional_attribution(db_session):
    """Verify formal institutional mapping to government department and authority."""
    case = AccountabilityService.create_case(
        db=db_session,
        case_id="TEST-CASE-ATTR-01",
        title="School Building Structural Delay",
        description="Physical construction overdue by 12 months.",
        governance_domain="School Education",
        trigger_type=CaseTriggerType.PROCUREMENT_DEFECT,
        trigger_entity_id="WORK-SED-01",
    )
    attr = AccountabilityService.add_attribution(
        db=db_session,
        case_id=case.id,
        department_name="School Education Department",
        directorate_or_agency="Directorate of School Education",
        jurisdiction_level="DISTRICT",
        district="Madurai",
        designated_authority="Chief Educational Officer",
        statutory_mandate_reference="Right to Education Act 2009 Standards",
    )
    assert attr.id is not None
    assert attr.department_name == "School Education Department"
    assert attr.district == "Madurai"
    assert len(case.attributions) == 1


def test_official_response_state_transition(db_session):
    """Verify recording an official response transitions case status to RESPONSE_RECEIVED."""
    case = AccountabilityService.create_case(
        db=db_session,
        case_id="TEST-CASE-RESP-01",
        title="Primary Health Center Staffing",
        description="Doctor vacancy unfulfilled for 6 months.",
        governance_domain="Health",
        trigger_type=CaseTriggerType.POLICY_OUTCOME_DEFICIT,
        trigger_entity_id="PHC-TN-01",
    )
    resp = AccountabilityService.record_official_response(
        db=db_session,
        case_id=case.id,
        response_reference="HFW/2024/REPLY-01",
        channel=ResponseChannel.LEGISLATIVE_ASSEMBLY_REPLY,
        response_date=date(2024, 7, 12),
        response_summary="Minister assured recruitment through Medical Services Recruitment Board (MRB).",
        receipt_status=ResponseReceiptStatus.FORMAL_REPLY,
        admitted_discrepancy=DiscrepancyAdmittance.PARTIAL,
    )
    assert resp.id is not None
    assert case.status == CaseStatus.RESPONSE_RECEIVED


def test_independent_outcome_verification_prevents_false_closure(db_session):
    """Verify a case cannot be CLOSED_VERIFIED if ground verification finds the issue unresolved."""
    case = AccountabilityService.create_case(
        db=db_session,
        case_id="TEST-CASE-VER-01",
        title="Rural Road Paving Project",
        description="Grievance filed reporting incomplete paving.",
        governance_domain="Rural Development",
        trigger_type=CaseTriggerType.GRIEVANCE_SLA_BREACH,
        trigger_entity_id="GRIEV-TN-RD-01",
    )

    # Authority logs corrective action
    AccountabilityService.log_corrective_action(
        db=db_session,
        case_id=case.id,
        action_type=CorrectiveActionType.REMEDIAL_PUBLIC_WORKS,
        description="Contractor directed to complete final bituminous layer.",
        executing_agency="Rural Development Agency",
    )
    assert case.status == CaseStatus.CORRECTIVE_ACTION_PENDING

    # Ground inspection reports FALSE CLOSURE
    ver = AccountabilityService.verify_outcome(
        db=db_session,
        case_id=case.id,
        verification_method=GroundVerificationMethod.PHYSICAL_INSPECTION,
        verifying_entity="Independent Civic Audit Panel",
        verification_date=date(2024, 9, 20),
        ground_status=GroundOutcomeStatus.NOT_RESOLVED_FALSE_CLOSURE,
        findings_summary="Physical spot inspection confirmed road remains gravel; top layer not laid.",
    )
    assert ver.is_statutory_closure_overridden is True
    assert ver.reopen_recommended is True
    assert case.status == CaseStatus.DISPUTED  # Prevented false closure!


def test_dossier_export(db_session):
    """Verify comprehensive, citation-ready accountability dossier export."""
    case = AccountabilityService.create_case(
        db=db_session,
        case_id="TEST-CASE-DOSSIER-01",
        title="Nutrition Kitchen Audit",
        description="Audit of meal kitchen delivery.",
        governance_domain="Social Welfare",
        trigger_type=CaseTriggerType.POLICY_OUTCOME_DEFICIT,
        trigger_entity_id="SCH-TN-MEAL-01",
        financial_implication_cr=5.2,
    )
    AccountabilityService.add_attribution(
        db=db_session,
        case_id=case.id,
        department_name="Social Welfare Department",
    )
    dossier = AccountabilityService.generate_accountability_dossier(db_session, case.case_id)
    assert dossier["dossier_type"] == "PUBLIC_ACCOUNTABILITY_CASE_DOSSIER"
    assert dossier["case_id"] == "TEST-CASE-DOSSIER-01"
    assert dossier["financial_implication_cr"] == 5.2
    assert len(dossier["institutional_attribution"]) == 1
    assert "NON-CAUSAL CIVIC OBSERVATION" in dossier["epistemic_disclaimer"]
