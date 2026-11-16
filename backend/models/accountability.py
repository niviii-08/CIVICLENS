"""
CIVICLENS TN — Public Accountability Lifecycle Models (Phase 11.2)

Provides end-to-end governance accountability tracking:
1. Case Discovery & Formulation
2. Institutional Attribution
3. Official Response Tracking
4. Corrective Action Follow-Through
5. Independent Outcome Verification
6. Citation-Ready Accountability Dossier
"""
import enum
from datetime import datetime, timezone, date
from typing import Optional, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float,
    ForeignKey, Enum as SqlEnum, Boolean, JSON, Index
)
from sqlalchemy.orm import relationship
from backend.database.base_class import Base


class CaseTriggerType(str, enum.Enum):
    BUDGET_DISCREPANCY = "BUDGET_DISCREPANCY"
    PROMISE_BREACH = "PROMISE_BREACH"
    GRIEVANCE_SLA_BREACH = "GRIEVANCE_SLA_BREACH"
    CAG_AUDIT_FINDING = "CAG_AUDIT_FINDING"
    PROCUREMENT_DEFECT = "PROCUREMENT_DEFECT"
    CITIZEN_RTI_DISCLOSURE = "CITIZEN_RTI_DISCLOSURE"
    POLICY_OUTCOME_DEFICIT = "POLICY_OUTCOME_DEFICIT"


class CaseStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESPONSE_RECEIVED = "RESPONSE_RECEIVED"
    CORRECTIVE_ACTION_PENDING = "CORRECTIVE_ACTION_PENDING"
    INDEPENDENTLY_VERIFIED = "INDEPENDENTLY_VERIFIED"
    CLOSED_VERIFIED = "CLOSED_VERIFIED"
    DISPUTED = "DISPUTED"


class CaseSeverity(str, enum.Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ResponseChannel(str, enum.Enum):
    LEGISLATIVE_ASSEMBLY_REPLY = "LEGISLATIVE_ASSEMBLY_REPLY"
    GOVERNMENT_ORDER = "GOVERNMENT_ORDER"
    PRESS_RELEASE = "PRESS_RELEASE"
    DIRECT_OFFICIAL_LETTER = "DIRECT_OFFICIAL_LETTER"
    RTI_DISCLOSURE = "RTI_DISCLOSURE"
    PUBLIC_ACCOUNTS_COMMITTEE = "PUBLIC_ACCOUNTS_COMMITTEE"


class ResponseReceiptStatus(str, enum.Enum):
    FORMAL_REPLY = "FORMAL_REPLY"
    PRESS_RELEASE = "PRESS_RELEASE"
    PROCEDURAL_ACKNOWLEDGMENT = "PROCEDURAL_ACKNOWLEDGMENT"
    NO_RESPONSE_OVERDUE = "NO_RESPONSE_OVERDUE"


class DiscrepancyAdmittance(str, enum.Enum):
    FULL = "FULL"
    PARTIAL = "PARTIAL"
    DENIED = "DENIED"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"


class CorrectiveActionType(str, enum.Enum):
    REMEDIAL_PUBLIC_WORKS = "REMEDIAL_PUBLIC_WORKS"
    FUND_RECOVERY = "FUND_RECOVERY"
    RE_TENDERING = "RE_TENDERING"
    DISCIPLINARY_INQUIRY = "DISCIPLINARY_INQUIRY"
    POLICY_REVISION = "POLICY_REVISION"
    SLA_PROCESS_OVERHAUL = "SLA_PROCESS_OVERHAUL"


class ActionExecutionStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    SANCTIONED = "SANCTIONED"
    IN_PROGRESS = "IN_PROGRESS"
    EXECUTED = "EXECUTED"
    DELAYED = "DELAYED"
    ABANDONED = "ABANDONED"


class GroundVerificationMethod(str, enum.Enum):
    PHYSICAL_INSPECTION = "PHYSICAL_INSPECTION"
    THIRD_PARTY_AUDIT = "THIRD_PARTY_AUDIT"
    CITIZEN_PHOTO_GEO_REPORT = "CITIZEN_PHOTO_GEO_REPORT"
    RTI_CONFIRMATION = "RTI_CONFIRMATION"
    CAG_FOLLOW_UP = "CAG_FOLLOW_UP"


class GroundOutcomeStatus(str, enum.Enum):
    VERIFIED_RESOLVED = "VERIFIED_RESOLVED"
    PARTIALLY_RESOLVED = "PARTIALLY_RESOLVED"
    NOT_RESOLVED_FALSE_CLOSURE = "NOT_RESOLVED_FALSE_CLOSURE"
    INCONCLUSIVE = "INCONCLUSIVE"


class AccountabilityCase(Base):
    """
    Primary orchestrating entity for public accountability.
    Connects detected anomalies across budget, schemes, grievances, audits, and promises
    to real institutional attribution, official responses, and verified outcomes.
    """
    __tablename__ = "accountability_cases"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(String(64), unique=True, index=True, nullable=False)
    title = Column(String(255), nullable=False, index=True)
    title_ta = Column(String(255), nullable=True)
    description = Column(Text, nullable=False)

    governance_domain = Column(String(100), nullable=False, index=True)
    district = Column(String(100), nullable=True, index=True)

    trigger_type = Column(SqlEnum(CaseTriggerType), nullable=False, index=True)
    trigger_entity_id = Column(String(128), nullable=False, index=True)

    status = Column(SqlEnum(CaseStatus), default=CaseStatus.OPEN, nullable=False, index=True)
    severity = Column(SqlEnum(CaseSeverity), default=CaseSeverity.MEDIUM, nullable=False)

    financial_implication_cr = Column(Float, nullable=True)
    evidence_provenance_hash = Column(String(64), nullable=True)

    # Bitemporal Data Modeling:
    # valid_from / valid_to = when this governance discrepancy/fact existed in reality
    # transaction_time = when recorded into CIVICLENS database
    valid_from = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    valid_to = Column(DateTime, nullable=True)
    transaction_time = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relationships
    attributions = relationship("InstitutionalAttribution", back_populates="case", cascade="all, delete-orphan")
    responses = relationship("OfficialResponse", back_populates="case", cascade="all, delete-orphan")
    corrective_actions = relationship("CorrectiveAction", back_populates="case", cascade="all, delete-orphan")
    verifications = relationship("OutcomeVerification", back_populates="case", cascade="all, delete-orphan")


class InstitutionalAttribution(Base):
    """
    Maps specific public department, directorate, urban local body (GCC),
    collectorate, or administrative office with formal jurisdiction over an accountability case.
    """
    __tablename__ = "institutional_attributions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("accountability_cases.id"), nullable=False, index=True)

    department_name = Column(String(255), nullable=False, index=True)
    directorate_or_agency = Column(String(255), nullable=True)
    jurisdiction_level = Column(String(50), default="STATE", nullable=False)  # STATE, DISTRICT, TALUK, GCC, WARD
    district = Column(String(100), nullable=True)
    taluk = Column(String(100), nullable=True)
    designated_authority = Column(String(255), nullable=True)
    statutory_mandate_reference = Column(String(255), nullable=True)

    is_primary = Column(Boolean, default=True)
    attributed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("AccountabilityCase", back_populates="attributions")


class OfficialResponse(Base):
    """
    Tracks formal explanations, government replies, press releases, or G.O.s
    issued in response to a tracked governance discrepancy.
    """
    __tablename__ = "official_responses"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("accountability_cases.id"), nullable=False, index=True)

    response_reference = Column(String(128), nullable=False)
    channel = Column(SqlEnum(ResponseChannel), nullable=False)
    receipt_status = Column(SqlEnum(ResponseReceiptStatus), default=ResponseReceiptStatus.FORMAL_REPLY, nullable=False)

    response_date = Column(Date, nullable=False)
    responding_officer_designation = Column(String(255), nullable=True)
    response_summary = Column(Text, nullable=False)
    admitted_discrepancy = Column(SqlEnum(DiscrepancyAdmittance), default=DiscrepancyAdmittance.UNDER_INVESTIGATION)

    document_url = Column(String(512), nullable=True)
    document_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("AccountabilityCase", back_populates="responses")


class CorrectiveAction(Base):
    """
    Tracks concrete remedial commitments made by public authorities:
    re-tendering, infrastructure repairs, fund recoveries, or policy revisions.
    """
    __tablename__ = "corrective_actions"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("accountability_cases.id"), nullable=False, index=True)

    action_type = Column(SqlEnum(CorrectiveActionType), nullable=False)
    description = Column(Text, nullable=False)
    executing_agency = Column(String(255), nullable=False)

    sanctioned_amount_cr = Column(Float, nullable=True)
    target_completion_date = Column(Date, nullable=True)
    actual_completion_date = Column(Date, nullable=True)

    status = Column(SqlEnum(ActionExecutionStatus), default=ActionExecutionStatus.PROPOSED, nullable=False)
    resolution_order_ref = Column(String(128), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    case = relationship("AccountabilityCase", back_populates="corrective_actions")


class OutcomeVerification(Base):
    """
    Independent outcome verification to prevent bureaucratic "false closures".
    Requires physical inspection, photo evidence, citizen report, or RTI corroboration.
    """
    __tablename__ = "outcome_verifications"

    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("accountability_cases.id"), nullable=False, index=True)

    verification_method = Column(SqlEnum(GroundVerificationMethod), nullable=False)
    verifying_entity = Column(String(255), nullable=False)
    verification_date = Column(Date, nullable=False)

    ground_status = Column(SqlEnum(GroundOutcomeStatus), nullable=False)
    findings_summary = Column(Text, nullable=False)

    geo_latitude = Column(Float, nullable=True)
    geo_longitude = Column(Float, nullable=True)
    photo_evidence_sha256 = Column(String(64), nullable=True)

    is_statutory_closure_overridden = Column(Boolean, default=False)
    reopen_recommended = Column(Boolean, default=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    case = relationship("AccountabilityCase", back_populates="verifications")
