"""
CIVICLENS TN — CAG Audit-Observation & RTI Oversight Service (Phase 11.4 & 11.5)

Provides analytics for:
1. Comptroller & Auditor General (CAG) Audit Findings & Action Taken Reports (ATRs)
2. Right to Information (RTI) Transparency, Turnaround Times & TNIC Appeals
"""
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.cag_rti import (
    CAGReport, CAGAuditParagraph, RTIRequest, RTIResponse, TNICSecondAppeal,
    CAGReportType, PACScrutinyStatus, ATRStatus, RTIDecision, TNICOrderType
)


class CAGAndRTIService:
    """Core domain service for CAG audit observations and RTI intelligence."""

    @staticmethod
    def ingest_cag_report(
        db: Session,
        report_code: str,
        financial_year: str,
        report_type: CAGReportType,
        title: str,
        tabled_in_assembly_date: Optional[date] = None,
        cag_portal_url: Optional[str] = None,
        report_pdf_sha256: Optional[str] = None,
    ) -> CAGReport:
        """Ingest or register a formal CAG State Audit Report."""
        report = CAGReport(
            report_code=report_code,
            financial_year=financial_year,
            report_type=report_type,
            title=title,
            tabled_in_assembly_date=tabled_in_assembly_date,
            is_tabled=tabled_in_assembly_date is not None,
            cag_portal_url=cag_portal_url,
            report_pdf_sha256=report_pdf_sha256,
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def add_audit_paragraph(
        db: Session,
        report_id: int,
        paragraph_ref: str,
        department_name: str,
        heading: str,
        audit_observation: str,
        financial_implication_cr: Optional[float] = None,
        scheme_code: Optional[str] = None,
    ) -> CAGAuditParagraph:
        """Add a specific audit observation paragraph to a CAG report."""
        para = CAGAuditParagraph(
            report_id=report_id,
            paragraph_ref=paragraph_ref,
            department_name=department_name,
            scheme_code=scheme_code,
            heading=heading,
            audit_observation=audit_observation,
            financial_implication_cr=financial_implication_cr,
            pac_status=PACScrutinyStatus.TABLED_AWAITING_EXAMINATION,
            atr_status=ATRStatus.PENDING_DEPARTMENT_REPLY,
        )
        db.add(para)
        db.commit()
        db.refresh(para)
        return para

    @staticmethod
    def update_atr_status(
        db: Session,
        paragraph_id: int,
        department_reply_summary: str,
        reply_received_date: date,
        atr_status: ATRStatus,
        pac_status: Optional[PACScrutinyStatus] = None,
        pac_recommendations: Optional[str] = None,
    ) -> CAGAuditParagraph:
        """Update departmental Action Taken Report (ATR) status."""
        para = db.query(CAGAuditParagraph).filter_by(id=paragraph_id).first()
        if not para:
            raise ValueError(f"CAG Audit Paragraph {paragraph_id} not found.")

        para.department_reply_summary = department_reply_summary
        para.reply_received_date = reply_received_date
        para.atr_status = atr_status
        if pac_status:
            para.pac_status = pac_status
        if pac_recommendations:
            para.pac_recommendations = pac_recommendations

        db.commit()
        db.refresh(para)
        return para

    @staticmethod
    def file_rti_request(
        db: Session,
        registration_number: str,
        public_authority: str,
        department_name: str,
        filing_date: date,
        subject_matter: str,
        pio_designation: Optional[str] = None,
        associated_case_id: Optional[str] = None,
    ) -> RTIRequest:
        """Log a filed RTI application."""
        req = RTIRequest(
            registration_number=registration_number,
            public_authority=public_authority,
            department_name=department_name,
            filing_date=filing_date,
            subject_matter=subject_matter,
            pio_designation=pio_designation,
            associated_case_id=associated_case_id,
            status=RTIDecision.PENDING_WITHIN_30_DAYS,
        )
        db.add(req)
        db.commit()
        db.refresh(req)
        return req

    @staticmethod
    def record_rti_response(
        db: Session,
        request_id: int,
        response_date: date,
        decision: RTIDecision,
        disclosed_summary: Optional[str] = None,
        exemptions_cited: Optional[str] = None,
        disclosed_document_sha256: Optional[str] = None,
    ) -> RTIResponse:
        """Record PIO RTI disposal and evaluate statutory 30-day SLA compliance."""
        req = db.query(RTIRequest).filter_by(id=request_id).first()
        if not req:
            raise ValueError(f"RTI Request {request_id} not found.")

        turnaround = (response_date - req.filing_date).days
        breached = turnaround > 30

        resp = RTIResponse(
            request_id=req.id,
            response_date=response_date,
            turnaround_days=turnaround,
            statutory_sla_breached=breached,
            decision=decision,
            exemptions_cited=exemptions_cited,
            disclosed_information_summary=disclosed_summary,
            disclosed_document_sha256=disclosed_document_sha256,
        )
        req.status = decision
        db.add(resp)
        db.commit()
        db.refresh(resp)
        return resp

    @staticmethod
    def get_cag_audit_summary(db: Session) -> Dict[str, Any]:
        """Aggregate statistical metrics for CAG audit follow-through."""
        total_paras = db.query(CAGAuditParagraph).count()
        pending_paras = db.query(CAGAuditParagraph).filter(
            CAGAuditParagraph.atr_status == ATRStatus.PENDING_DEPARTMENT_REPLY
        ).count()
        total_implication = db.query(func.sum(CAGAuditParagraph.financial_implication_cr)).scalar() or 0.0

        return {
            "total_audit_paragraphs_tracked": total_paras,
            "paragraphs_pending_reply": pending_paras,
            "total_monetary_implication_cr": round(total_implication, 2),
            "response_compliance_rate_pct": round(
                ((total_paras - pending_paras) / total_paras * 100), 2
            ) if total_paras > 0 else 0.0,
        }
