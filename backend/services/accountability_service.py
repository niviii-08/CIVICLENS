"""
CIVICLENS TN — Public Accountability Lifecycle Service (Phase 11.2)

Orchestrates the 6-stage accountability cycle:
1. Discovery & Case Formulation
2. Institutional Attribution
3. Official Response Recording
4. Corrective Action Follow-Through
5. Independent Outcome Verification
6. Immutable Public Accountability Dossier Generation
"""
import hashlib
import json
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from backend.models.accountability import (
    AccountabilityCase, InstitutionalAttribution, OfficialResponse,
    CorrectiveAction, OutcomeVerification, CaseStatus, CaseSeverity,
    CaseTriggerType, GroundOutcomeStatus, ResponseReceiptStatus
)
from backend.models.provenance import enforce_bns_defamation_guardrail


class AccountabilityService:
    """Core domain service for civic accountability lifecycle management."""

    @staticmethod
    def create_case(
        db: Session,
        case_id: str,
        title: str,
        description: str,
        governance_domain: str,
        trigger_type: CaseTriggerType,
        trigger_entity_id: str,
        title_ta: Optional[str] = None,
        district: Optional[str] = None,
        severity: CaseSeverity = CaseSeverity.MEDIUM,
        financial_implication_cr: Optional[float] = None,
        valid_from: Optional[datetime] = None,
    ) -> AccountabilityCase:
        """Create a new tracked public accountability case with bitemporal timestamps."""
        # Enforce legal defamation guardrail before logging
        enforce_bns_defamation_guardrail(description)

        now = datetime.now(timezone.utc)
        provenance_str = f"{case_id}|{title}|{governance_domain}|{trigger_entity_id}|{now.isoformat()}"
        evidence_hash = hashlib.sha256(provenance_str.encode("utf-8")).hexdigest()

        case = AccountabilityCase(
            case_id=case_id,
            title=title,
            title_ta=title_ta,
            description=description,
            governance_domain=governance_domain,
            district=district,
            trigger_type=trigger_type,
            trigger_entity_id=trigger_entity_id,
            status=CaseStatus.OPEN,
            severity=severity,
            financial_implication_cr=financial_implication_cr,
            evidence_provenance_hash=evidence_hash,
            valid_from=valid_from or now,
            transaction_time=now,
        )
        db.add(case)
        db.commit()
        db.refresh(case)
        return case

    @staticmethod
    def add_attribution(
        db: Session,
        case_id: int,
        department_name: str,
        directorate_or_agency: Optional[str] = None,
        jurisdiction_level: str = "STATE",
        district: Optional[str] = None,
        taluk: Optional[str] = None,
        designated_authority: Optional[str] = None,
        statutory_mandate_reference: Optional[str] = None,
        is_primary: bool = True,
    ) -> InstitutionalAttribution:
        """Map the institutional body formally responsible for the matter."""
        case = db.query(AccountabilityCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"AccountabilityCase with ID {case_id} not found.")

        attr = InstitutionalAttribution(
            case_id=case.id,
            department_name=department_name,
            directorate_or_agency=directorate_or_agency,
            jurisdiction_level=jurisdiction_level,
            district=district,
            taluk=taluk,
            designated_authority=designated_authority,
            statutory_mandate_reference=statutory_mandate_reference,
            is_primary=is_primary,
        )
        db.add(attr)
        db.commit()
        db.refresh(attr)
        return attr

    @staticmethod
    def record_official_response(
        db: Session,
        case_id: int,
        response_reference: str,
        channel: Any,
        response_date: date,
        response_summary: str,
        receipt_status: ResponseReceiptStatus = ResponseReceiptStatus.FORMAL_REPLY,
        responding_officer_designation: Optional[str] = None,
        admitted_discrepancy: Any = None,
        document_url: Optional[str] = None,
        document_sha256: Optional[str] = None,
    ) -> OfficialResponse:
        """Record official departmental/ministerial response to the accountability issue."""
        case = db.query(AccountabilityCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"AccountabilityCase with ID {case_id} not found.")

        resp = OfficialResponse(
            case_id=case.id,
            response_reference=response_reference,
            channel=channel,
            receipt_status=receipt_status,
            response_date=response_date,
            responding_officer_designation=responding_officer_designation,
            response_summary=response_summary,
            admitted_discrepancy=admitted_discrepancy,
            document_url=document_url,
            document_sha256=document_sha256,
        )
        db.add(resp)

        # Transition case status
        if case.status in (CaseStatus.OPEN, CaseStatus.UNDER_REVIEW):
            case.status = CaseStatus.RESPONSE_RECEIVED

        db.commit()
        db.refresh(resp)
        return resp

    @staticmethod
    def log_corrective_action(
        db: Session,
        case_id: int,
        action_type: Any,
        description: str,
        executing_agency: str,
        sanctioned_amount_cr: Optional[float] = None,
        target_completion_date: Optional[date] = None,
        resolution_order_ref: Optional[str] = None,
    ) -> CorrectiveAction:
        """Log concrete corrective action sanctioned by the authority."""
        case = db.query(AccountabilityCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"AccountabilityCase with ID {case_id} not found.")

        action = CorrectiveAction(
            case_id=case.id,
            action_type=action_type,
            description=description,
            executing_agency=executing_agency,
            sanctioned_amount_cr=sanctioned_amount_cr,
            target_completion_date=target_completion_date,
            resolution_order_ref=resolution_order_ref,
        )
        db.add(action)
        case.status = CaseStatus.CORRECTIVE_ACTION_PENDING
        db.commit()
        db.refresh(action)
        return action

    @staticmethod
    def verify_outcome(
        db: Session,
        case_id: int,
        verification_method: Any,
        verifying_entity: str,
        verification_date: date,
        ground_status: GroundOutcomeStatus,
        findings_summary: str,
        geo_latitude: Optional[float] = None,
        geo_longitude: Optional[float] = None,
        photo_evidence_sha256: Optional[str] = None,
    ) -> OutcomeVerification:
        """
        Record independent ground outcome verification.
        Crucial Rule: Cannot close case as CLOSED_VERIFIED without positive ground corroboration!
        """
        case = db.query(AccountabilityCase).filter_by(id=case_id).first()
        if not case:
            raise ValueError(f"AccountabilityCase with ID {case_id} not found.")

        ver = OutcomeVerification(
            case_id=case.id,
            verification_method=verification_method,
            verifying_entity=verifying_entity,
            verification_date=verification_date,
            ground_status=ground_status,
            findings_summary=findings_summary,
            geo_latitude=geo_latitude,
            geo_longitude=geo_longitude,
            photo_evidence_sha256=photo_evidence_sha256,
        )

        if ground_status == GroundOutcomeStatus.VERIFIED_RESOLVED:
            case.status = CaseStatus.CLOSED_VERIFIED
            case.valid_to = datetime.now(timezone.utc)
        elif ground_status == GroundOutcomeStatus.NOT_RESOLVED_FALSE_CLOSURE:
            case.status = CaseStatus.DISPUTED
            ver.is_statutory_closure_overridden = True
            ver.reopen_recommended = True
        else:
            case.status = CaseStatus.INDEPENDENTLY_VERIFIED

        db.add(ver)
        db.commit()
        db.refresh(ver)
        return ver

    @staticmethod
    def generate_accountability_dossier(db: Session, case_id: str) -> Dict[str, Any]:
        """Generate an auditable, citation-ready accountability dossier."""
        case = db.query(AccountabilityCase).filter_by(case_id=case_id).first()
        if not case:
            raise ValueError(f"Accountability case {case_id} not found.")

        dossier = {
            "dossier_type": "PUBLIC_ACCOUNTABILITY_CASE_DOSSIER",
            "case_id": case.case_id,
            "title": case.title,
            "title_ta": case.title_ta,
            "domain": case.governance_domain,
            "district": case.district,
            "status": case.status.value,
            "severity": case.severity.value,
            "trigger_type": case.trigger_type.value,
            "trigger_entity_id": case.trigger_entity_id,
            "financial_implication_cr": case.financial_implication_cr,
            "provenance_hash": case.evidence_provenance_hash,
            "bitemporal": {
                "valid_from": case.valid_from.isoformat() if case.valid_from else None,
                "valid_to": case.valid_to.isoformat() if case.valid_to else None,
                "transaction_time": case.transaction_time.isoformat() if case.transaction_time else None,
            },
            "institutional_attribution": [
                {
                    "department": a.department_name,
                    "agency": a.directorate_or_agency,
                    "level": a.jurisdiction_level,
                    "district": a.district,
                    "officer": a.designated_authority,
                    "statutory_mandate": a.statutory_mandate_reference,
                    "is_primary": a.is_primary,
                }
                for a in case.attributions
            ],
            "official_responses": [
                {
                    "reference": r.response_reference,
                    "channel": r.channel.value,
                    "receipt_status": r.receipt_status.value,
                    "date": r.response_date.isoformat(),
                    "summary": r.response_summary,
                    "document_url": r.document_url,
                    "sha256": r.document_sha256,
                }
                for r in case.responses
            ],
            "corrective_actions": [
                {
                    "action_type": c.action_type.value,
                    "description": c.description,
                    "executing_agency": c.executing_agency,
                    "status": c.status.value,
                    "sanctioned_amount_cr": c.sanctioned_amount_cr,
                    "target_date": c.target_completion_date.isoformat() if c.target_completion_date else None,
                }
                for c in case.corrective_actions
            ],
            "ground_verifications": [
                {
                    "method": v.verification_method.value,
                    "verifying_entity": v.verifying_entity,
                    "date": v.verification_date.isoformat(),
                    "ground_status": v.ground_status.value,
                    "findings": v.findings_summary,
                    "false_closure_overridden": v.is_statutory_closure_overridden,
                    "photo_sha256": v.photo_evidence_sha256,
                }
                for v in case.verifications
            ],
            "epistemic_disclaimer": (
                "NON-CAUSAL CIVIC OBSERVATION: This dossier aggregates official public records, "
                "statutory audit paragraphs, verified contractor work orders, and independent physical verifications. "
                "CIVICLENS TN presents documentary evidence without asserting subjective or criminal guilt."
            ),
        }
        return dossier
