"""
Unit Tests for Phase 11.4 & 11.5 — CAG Audit & RTI Intelligence
"""
import pytest
from datetime import date
from backend.models.cag_rti import (
    CAGReport, CAGAuditParagraph, RTIRequest, RTIResponse, TNICSecondAppeal,
    CAGReportType, PACScrutinyStatus, ATRStatus, RTIDecision, TNICOrderType
)
from backend.services.cag_rti_service import CAGAndRTIService


def test_cag_report_and_paragraph_ingestion(db_session):
    """Verify CAG state report ingestion and audit paragraph registration."""
    report = CAGAndRTIService.ingest_cag_report(
        db=db_session,
        report_code="TEST-CAG-TN-2024-01",
        financial_year="2022-23",
        report_type=CAGReportType.STATE_FINANCES_AUDIT,
        title="Audit Report on State Finances",
        tabled_in_assembly_date=date(2024, 3, 20),
    )
    assert report.id is not None
    assert report.is_tabled is True

    para = CAGAndRTIService.add_audit_paragraph(
        db=db_session,
        report_id=report.id,
        paragraph_ref="Para 2.1",
        department_name="Finance Department",
        heading="Unreconciled Treasury Differences",
        audit_observation="Audit noted ₹35.20 Cr in treasury balances remaining unreconciled.",
        financial_implication_cr=35.2,
    )
    assert para.id is not None
    assert para.atr_status == ATRStatus.PENDING_DEPARTMENT_REPLY


def test_cag_atr_status_update(db_session):
    """Verify departmental Action Taken Report (ATR) status progression."""
    report = CAGAndRTIService.ingest_cag_report(
        db=db_session,
        report_code="TEST-CAG-TN-2024-02",
        financial_year="2022-23",
        report_type=CAGReportType.ECONOMIC_SECTOR,
        title="Audit Report on Economic Sector",
    )
    para = CAGAndRTIService.add_audit_paragraph(
        db=db_session,
        report_id=report.id,
        paragraph_ref="Para 4.3",
        department_name="Highways Department",
        heading="Overpayment on Road Widening Contracts",
        audit_observation="Excess payment of ₹4.8 Cr due to calculation error in bitumen escalation.",
        financial_implication_cr=4.8,
    )

    updated = CAGAndRTIService.update_atr_status(
        db=db_session,
        paragraph_id=para.id,
        department_reply_summary="Department initiated recovery of ₹4.8 Cr from contractor running bills.",
        reply_received_date=date(2024, 8, 10),
        atr_status=ATRStatus.ACCEPTED_SATISFACTORY,
        pac_status=PACScrutinyStatus.EXAMINED_AND_DROPPED,
    )
    assert updated.atr_status == ATRStatus.ACCEPTED_SATISFACTORY
    assert updated.pac_status == PACScrutinyStatus.EXAMINED_AND_DROPPED


def test_rti_turnaround_and_sla_breach_detection(db_session):
    """Verify RTI turnaround days and automatic 30-day statutory SLA breach detection."""
    # Compliant RTI (<30 days)
    req1 = CAGAndRTIService.file_rti_request(
        db=db_session,
        registration_number="TEST-RTI-001",
        public_authority="Revenue Department",
        department_name="Revenue Department",
        filing_date=date(2024, 1, 1),
        subject_matter="Patta transfer pending applications in Madurai North Taluk",
    )
    resp1 = CAGAndRTIService.record_rti_response(
        db=db_session,
        request_id=req1.id,
        response_date=date(2024, 1, 20),
        decision=RTIDecision.FULL_DISCLOSURE,
    )
    assert resp1.turnaround_days == 19
    assert resp1.statutory_sla_breached is False

    # Breached RTI (>30 days)
    req2 = CAGAndRTIService.file_rti_request(
        db=db_session,
        registration_number="TEST-RTI-002",
        public_authority="GCC",
        department_name="Municipal Administration",
        filing_date=date(2024, 2, 1),
        subject_matter="Stormwater drain tender comparative statements",
    )
    resp2 = CAGAndRTIService.record_rti_response(
        db=db_session,
        request_id=req2.id,
        response_date=date(2024, 3, 15),
        decision=RTIDecision.PARTIAL_DISCLOSURE,
        exemptions_cited="Section 8(1)(d)",
    )
    assert resp2.turnaround_days == 43
    assert resp2.statutory_sla_breached is True
