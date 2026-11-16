"""
CIVICLENS TN — Public Procurement & Works Intelligence Models (Phase 11.3)

Provides end-to-end tracing from budget appropriations to on-the-ground infrastructure:
Budget Scheme -> Tender -> Bidding -> Contract Award -> Contractor -> Public Work -> Payments -> Physical Milestone & Defects.
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


class TenderCategory(str, enum.Enum):
    CIVIL_WORKS = "CIVIL_WORKS"
    GOODS = "GOODS"
    CONSULTING_SERVICES = "CONSULTING_SERVICES"
    MAINTENANCE = "MAINTENANCE"


class ProcurementMethod(str, enum.Enum):
    OPEN_TENDER = "OPEN_TENDER"
    TWO_COVER_SYSTEM = "TWO_COVER_SYSTEM"
    LIMITED_TENDER = "LIMITED_TENDER"
    SINGLE_SOURCE_EMERGENCY = "SINGLE_SOURCE_EMERGENCY"


class TenderStatus(str, enum.Enum):
    PUBLISHED = "PUBLISHED"
    TECHNICAL_EVALUATION = "TECHNICAL_EVALUATION"
    FINANCIAL_EVALUATION = "FINANCIAL_EVALUATION"
    AWARDED = "AWARDED"
    RETENDERED = "RETENDERED"
    CANCELLED = "CANCELLED"


class WorkType(str, enum.Enum):
    CIVIL_WORKS = "CIVIL_WORKS"
    SCHOOL_BUILDING = "SCHOOL_BUILDING"
    PRIMARY_HEALTH_CENTER = "PRIMARY_HEALTH_CENTER"
    ROAD_PAVING = "ROAD_PAVING"
    DRINKING_WATER_SCHEME = "DRINKING_WATER_SCHEME"
    DRAINAGE_AND_SEWERAGE = "DRAINAGE_AND_SEWERAGE"
    CHECK_DAM_AND_CANAL = "CHECK_DAM_AND_CANAL"
    COMMUNITY_HALL = "COMMUNITY_HALL"


class MilestoneProgressStatus(str, enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    STALLED = "STALLED"
    PHYSICALLY_COMPLETED = "PHYSICALLY_COMPLETED"
    DEFECTS_IDENTIFIED = "DEFECTS_IDENTIFIED"
    COMMISSIONED = "COMMISSIONED"


class InspectionStatus(str, enum.Enum):
    PENDING_INSPECTION = "PENDING_INSPECTION"
    PASSED_CONFORMANT = "PASSED_CONFORMANT"
    DEFECTS_NOTICED = "DEFECTS_NOTICED"
    RE_INSPECTION_REQUIRED = "RE_INSPECTION_REQUIRED"


class Tender(Base):
    """
    Public tender notice published on TN Transparency in Tenders portal (tntenders.gov.in)
    or department portal.
    """
    __tablename__ = "procurement_tenders"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(String(64), unique=True, index=True, nullable=False)
    canonical_scheme_code = Column(String(64), nullable=True, index=True)

    issuing_department = Column(String(255), nullable=False, index=True)
    procuring_entity = Column(String(255), nullable=False)
    title = Column(Text, nullable=False)
    title_ta = Column(Text, nullable=True)

    category = Column(SqlEnum(TenderCategory), default=TenderCategory.CIVIL_WORKS, nullable=False)
    procurement_method = Column(SqlEnum(ProcurementMethod), default=ProcurementMethod.OPEN_TENDER, nullable=False)

    estimated_cost_cr = Column(Float, nullable=False)
    earnest_money_deposit_inr = Column(Float, nullable=True)

    published_date = Column(Date, nullable=False)
    submission_deadline = Column(Date, nullable=False)
    award_date = Column(Date, nullable=True)

    district = Column(String(100), nullable=True, index=True)
    status = Column(SqlEnum(TenderStatus), default=TenderStatus.PUBLISHED, nullable=False)

    source_url = Column(String(512), nullable=True)
    tender_notice_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    bids = relationship("TenderBid", back_populates="tender", cascade="all, delete-orphan")
    award = relationship("ContractAward", uselist=False, back_populates="tender")
    public_works = relationship("ProcurementPublicWork", back_populates="tender")


class TenderBid(Base):
    """
    Individual bid received for a published public tender.
    """
    __tablename__ = "procurement_tender_bids"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("procurement_tenders.id"), nullable=False, index=True)

    bidder_name = Column(String(255), nullable=False, index=True)
    bid_amount_cr = Column(Float, nullable=False)
    technical_score = Column(Float, nullable=True)
    is_technically_qualified = Column(Boolean, default=True)

    is_l1_lowest = Column(Boolean, default=False)
    disqualification_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    tender = relationship("Tender", back_populates="bids")


class ContractAward(Base):
    """
    Final contract award decision and work order issuance.
    """
    __tablename__ = "procurement_contract_awards"

    id = Column(Integer, primary_key=True, index=True)
    tender_id = Column(Integer, ForeignKey("procurement_tenders.id"), nullable=False, unique=True)

    contract_reference = Column(String(128), unique=True, index=True, nullable=False)
    contractor_name = Column(String(255), nullable=False, index=True)
    contractor_pan_masked = Column(String(32), nullable=True)

    awarded_amount_cr = Column(Float, nullable=False)
    variance_from_estimate_pct = Column(Float, nullable=True)  # + / - % over or under estimate

    award_date = Column(Date, nullable=False)
    stipulated_duration_months = Column(Integer, default=12)
    work_order_reference = Column(String(128), nullable=True)
    work_order_sha256 = Column(String(64), nullable=True)

    tender = relationship("Tender", back_populates="award")


class ProcurementPublicWork(Base):
    """
    The concrete physical public asset or infrastructure project being constructed or delivered.
    """
    __tablename__ = "procurement_public_works"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(String(64), unique=True, index=True, nullable=False)
    tender_id = Column(Integer, ForeignKey("procurement_tenders.id"), nullable=True, index=True)

    title = Column(String(255), nullable=False, index=True)
    title_ta = Column(String(255), nullable=True)
    work_type = Column(SqlEnum(WorkType), default=WorkType.CIVIL_WORKS, nullable=False, index=True)

    district = Column(String(100), nullable=False, index=True)
    taluk = Column(String(100), nullable=True)
    local_body = Column(String(150), nullable=True)  # e.g. GCC Zone 5, Salem Municipality
    ward_number = Column(String(32), nullable=True)
    constituency_name = Column(String(100), nullable=True, index=True)

    sanctioned_budget_cr = Column(Float, nullable=False)
    cumulative_expenditure_cr = Column(Float, default=0.0)

    physical_progress_pct = Column(Float, default=0.0)
    milestone_status = Column(SqlEnum(MilestoneProgressStatus), default=MilestoneProgressStatus.NOT_STARTED, nullable=False)

    scheduled_start_date = Column(Date, nullable=True)
    target_completion_date = Column(Date, nullable=False)
    actual_completion_date = Column(Date, nullable=True)

    # Physical Verification & Defect Liability
    inspection_status = Column(SqlEnum(InspectionStatus), default=InspectionStatus.PENDING_INSPECTION, nullable=False)
    defect_liability_months = Column(Integer, default=24)
    defect_liability_end_date = Column(Date, nullable=True)

    completion_certificate_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    tender = relationship("Tender", back_populates="public_works")
    payments = relationship("ProcurementPayment", back_populates="work", cascade="all, delete-orphan")


class ProcurementPayment(Base):
    """
    Financial payment tranche released against contractor bills and inspection vouchers.
    """
    __tablename__ = "procurement_payments"

    id = Column(Integer, primary_key=True, index=True)
    work_id = Column(Integer, ForeignKey("procurement_public_works.id"), nullable=False, index=True)

    tranche_number = Column(Integer, nullable=False)
    amount_paid_cr = Column(Float, nullable=False)
    payment_date = Column(Date, nullable=False)

    treasury_voucher_number = Column(String(128), nullable=False)
    milestone_verified = Column(String(255), nullable=True)
    quality_certification_verified = Column(Boolean, default=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    work = relationship("ProcurementPublicWork", back_populates="payments")
