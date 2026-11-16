"""
CIVICLENS TN — CAG Audit-Observation & RTI Intelligence Models (Phase 11.4 & 11.5)

Provides formal oversight tracking:
1. Comptroller & Auditor General (CAG) State Reports
2. Audit Paragraphs, Departmental Explanations, PAC/COPU Scrutiny & Action Taken Reports (ATRs)
3. Right to Information (RTI) Applications, Decisions, Exemptions Cited, and TNIC Second Appeals
"""
import enum
from datetime import datetime, timezone, date
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float,
    ForeignKey, Enum as SqlEnum, Boolean, Index
)
from sqlalchemy.orm import relationship
from backend.database.base_class import Base


class CAGReportType(str, enum.Enum):
    STATE_FINANCES_AUDIT = "STATE_FINANCES_AUDIT"
    APPROPRIATION_ACCOUNTS = "APPROPRIATION_ACCOUNTS"
    GENERAL_AND_SOCIAL_SECTOR = "GENERAL_AND_SOCIAL_SECTOR"
    ECONOMIC_SECTOR = "ECONOMIC_SECTOR"
    REVENUE_SECTOR = "REVENUE_SECTOR"
    PUBLIC_SECTOR_UNDERTAKINGS = "PUBLIC_SECTOR_UNDERTAKINGS"
    LOCAL_BODIES = "LOCAL_BODIES"


class PACScrutinyStatus(str, enum.Enum):
    PENDING_TABLING = "PENDING_TABLING"
    TABLED_AWAITING_EXAMINATION = "TABLED_AWAITING_EXAMINATION"
    UNDER_PAC_EXAMINATION = "UNDER_PAC_EXAMINATION"
    RECOMMENDATIONS_ISSUED = "RECOMMENDATIONS_ISSUED"
    EXAMINED_AND_DROPPED = "EXAMINED_AND_DROPPED"


class ATRStatus(str, enum.Enum):
    PENDING_DEPARTMENT_REPLY = "PENDING_DEPARTMENT_REPLY"
    REPLY_SUBMITTED_AWAITING_REVIEW = "REPLY_SUBMITTED_AWAITING_REVIEW"
    ACCEPTED_SATISFACTORY = "ACCEPTED_SATISFACTORY"
    INADEQUATE_EXPLANATION = "INADEQUATE_EXPLANATION"
    DROPPED_BY_COMMITTEE = "DROPPED_BY_COMMITTEE"


class RTIDecision(str, enum.Enum):
    FULL_DISCLOSURE = "FULL_DISCLOSURE"
    PARTIAL_DISCLOSURE = "PARTIAL_DISCLOSURE"
    REJECTED_EXEMPT = "REJECTED_EXEMPT"
    TRANSFERRED_SEC_6_3 = "TRANSFERRED_SEC_6_3"
    DEEMED_REFUSAL = "DEEMED_REFUSAL"
    PENDING_WITHIN_30_DAYS = "PENDING_WITHIN_30_DAYS"


class TNICOrderType(str, enum.Enum):
    DISCLOSURE_ORDERED = "DISCLOSURE_ORDERED"
    COMPENSATION_AWARDED = "COMPENSATION_AWARDED"
    PENALTY_IMPOSED_SEC_20 = "PENALTY_IMPOSED_SEC_20"
    DEPARTMENTAL_ENQUIRY_ORDERED = "DEPARTMENTAL_ENQUIRY_ORDERED"
    APPEAL_DISMISSED = "APPEAL_DISMISSED"


class CAGReport(Base):
    """
    State Audit Reports prepared by Comptroller and Auditor General of India
    for the State of Tamil Nadu, submitted to the Governor and tabled in the Legislative Assembly.
    """
    __tablename__ = "cag_audit_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_code = Column(String(64), unique=True, index=True, nullable=False)  # e.g. CAG-TN-2023-REPORT-03
    financial_year = Column(String(16), nullable=False, index=True)  # e.g. "2022-23"
    report_type = Column(SqlEnum(CAGReportType), nullable=False)
    title = Column(Text, nullable=False)

    tabled_in_assembly_date = Column(Date, nullable=True)
    is_tabled = Column(Boolean, default=False)

    cag_portal_url = Column(String(512), nullable=True)
    report_pdf_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    paragraphs = relationship("CAGAuditParagraph", back_populates="report", cascade="all, delete-orphan")


class CAGAuditParagraph(Base):
    """
    Individual audit observation or paragraph within a CAG Audit Report.
    """
    __tablename__ = "cag_audit_paragraphs"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("cag_audit_reports.id"), nullable=False, index=True)

    paragraph_ref = Column(String(32), nullable=False, index=True)  # e.g. "Paragraph 3.2"
    department_name = Column(String(255), nullable=False, index=True)
    scheme_code = Column(String(64), nullable=True, index=True)

    heading = Column(Text, nullable=False)
    audit_observation = Column(Text, nullable=False)
    financial_implication_cr = Column(Float, nullable=True)  # In ₹ Crore

    department_reply_summary = Column(Text, nullable=True)
    reply_received_date = Column(Date, nullable=True)

    pac_status = Column(SqlEnum(PACScrutinyStatus), default=PACScrutinyStatus.TABLED_AWAITING_EXAMINATION, nullable=False)
    pac_recommendations = Column(Text, nullable=True)

    atr_status = Column(SqlEnum(ATRStatus), default=ATRStatus.PENDING_DEPARTMENT_REPLY, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    report = relationship("CAGReport", back_populates="paragraphs")


class RTIRequest(Base):
    """
    Right to Information application filed under the RTI Act 2005
    with a Tamil Nadu Government Department or Public Authority.
    """
    __tablename__ = "rti_requests"

    id = Column(Integer, primary_key=True, index=True)
    registration_number = Column(String(64), unique=True, index=True, nullable=False)  # e.g. RTI/GOTN/SCH/2024/00412
    public_authority = Column(String(255), nullable=False, index=True)
    department_name = Column(String(255), nullable=False, index=True)

    filing_date = Column(Date, nullable=False)
    subject_matter = Column(Text, nullable=False)

    fee_paid_inr = Column(Float, default=10.0)
    pio_designation = Column(String(255), nullable=True)

    status = Column(SqlEnum(RTIDecision), default=RTIDecision.PENDING_WITHIN_30_DAYS, nullable=False)
    associated_case_id = Column(String(64), nullable=True, index=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    response = relationship("RTIResponse", uselist=False, back_populates="request")
    second_appeals = relationship("TNICSecondAppeal", back_populates="request")


class RTIResponse(Base):
    """
    Official decision and disclosure provided by Public Information Officer (PIO).
    """
    __tablename__ = "rti_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("rti_requests.id"), nullable=False, unique=True)

    response_date = Column(Date, nullable=False)
    turnaround_days = Column(Integer, nullable=False)
    statutory_sla_breached = Column(Boolean, default=False)  # Exceeded 30 days statutory window

    decision = Column(SqlEnum(RTIDecision), nullable=False)
    exemptions_cited = Column(String(128), nullable=True)  # e.g. "Section 8(1)(j), Section 8(1)(d)"

    disclosed_information_summary = Column(Text, nullable=True)
    disclosed_document_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    request = relationship("RTIRequest", back_populates="response")


class TNICSecondAppeal(Base):
    """
    Second Appeal order issued by the Tamil Nadu Information Commission (TNIC).
    """
    __tablename__ = "rti_tnic_appeals"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("rti_requests.id"), nullable=False, index=True)

    appeal_case_number = Column(String(64), unique=True, index=True, nullable=False)  # e.g. SA 4122/SCIC/2024
    commissioner_name = Column(String(255), nullable=True)

    hearing_date = Column(Date, nullable=False)
    order_type = Column(SqlEnum(TNICOrderType), nullable=False)
    order_summary = Column(Text, nullable=False)

    penalty_amount_inr = Column(Float, default=0.0)
    compliance_deadline = Column(Date, nullable=True)
    order_pdf_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    request = relationship("RTIRequest", back_populates="second_appeals")
