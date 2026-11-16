"""
CIVICLENS TN — Evidence Provenance, Bitemporal Lineage & Legal Safeguards (Phase 11.1 & 11.7)

Provides:
1. Granular Extraction Lineage (Page / Table / Row / Cell)
2. Bitemporal Document Preservation & SHA-256 Hash Verification
3. DPDPA 2023 & DPDP Rules 2025 Compliance Registry
4. Bharatiya Nyaya Sanhita (BNS) 2023 Sec 356 Defamation Safeguards (Right of Reply & Public Corrections)
"""
import enum
import re
from datetime import datetime, timezone, date
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Date, Float,
    ForeignKey, Enum as SqlEnum, Boolean, Index
)
from backend.database.base_class import Base


class LinkHealthStatus(str, enum.Enum):
    ONLINE_VERIFIED = "ONLINE_VERIFIED"
    CHANGED_CONTENT = "CHANGED_CONTENT"
    DEAD_LINK_404 = "DEAD_LINK_404"
    ARCHIVED_WAYBACK = "ARCHIVED_WAYBACK"


class DataSubjectRequestType(str, enum.Enum):
    ACCESS = "ACCESS"
    CORRECTION = "CORRECTION"
    ERASURE_PII = "ERASURE_PII"
    GRIEVANCE_DPDPA = "GRIEVANCE_DPDPA"


class DPDPAStatus(str, enum.Enum):
    RECEIVED = "RECEIVED"
    VERIFIED = "VERIFIED"
    ACTION_TAKEN_REDACTED = "ACTION_TAKEN_REDACTED"
    EXEMPTED_PUBLIC_RECORD = "EXEMPTED_PUBLIC_RECORD"


class RightOfReplyStatus(str, enum.Enum):
    NOTICE_DISPATCHED = "NOTICE_DISPATCHED"
    REPLY_RECEIVED = "REPLY_RECEIVED"
    WINDOW_EXPIRED_NO_REPLY = "WINDOW_EXPIRED_NO_REPLY"
    FORMALLY_WAIVED = "FORMALLY_WAIVED"


class GranularExtractionLineage(Base):
    """
    Sub-document extraction provenance linking every database number/fact
    to the exact PDF page, table index, row number, and column.
    """
    __tablename__ = "extraction_lineages"

    id = Column(Integer, primary_key=True, index=True)
    target_table = Column(String(64), nullable=False, index=True)
    target_record_id = Column(String(64), nullable=False, index=True)

    source_document_title = Column(String(255), nullable=False)
    source_url = Column(String(512), nullable=True)
    document_sha256 = Column(String(64), nullable=False, index=True)

    page_number = Column(Integer, nullable=True)
    table_index = Column(Integer, nullable=True)
    row_number = Column(Integer, nullable=True)
    column_name = Column(String(100), nullable=True)

    extracted_verbatim_text = Column(Text, nullable=False)
    extraction_method = Column(String(64), default="PDFPLUMBER_TABLE_EXTRACTION")

    # Bitemporal Data Fields
    valid_time_start = Column(DateTime, nullable=True)
    valid_time_end = Column(DateTime, nullable=True)
    transaction_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    link_health = Column(SqlEnum(LinkHealthStatus), default=LinkHealthStatus.ONLINE_VERIFIED)
    last_verified_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class DPDPAComplianceRequest(Base):
    """
    Tracks privacy compliance under Digital Personal Data Protection Act (DPDPA) 2023
    and DPDP Rules 2025.
    """
    __tablename__ = "dpdpa_compliance_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_reference = Column(String(64), unique=True, index=True, nullable=False)
    request_type = Column(SqlEnum(DataSubjectRequestType), nullable=False)

    data_principal_hash = Column(String(64), nullable=False)  # Pseudonymized requester identity
    affected_record_table = Column(String(64), nullable=False)
    affected_record_id = Column(String(64), nullable=False)

    received_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(SqlEnum(DPDPAStatus), default=DPDPAStatus.RECEIVED, nullable=False)

    resolution_notes = Column(Text, nullable=True)
    resolution_date = Column(DateTime, nullable=True)


class RightOfReplyRegistry(Base):
    """
    Legal safeguard under Bharatiya Nyaya Sanhita (BNS) 2023 Sec 356 (Defamation).
    Logs mandatory fair-opportunity notifications sent to public entities,
    officials, or contractors before publishing critical analysis findings.
    """
    __tablename__ = "right_of_reply_records"

    id = Column(Integer, primary_key=True, index=True)
    reply_case_ref = Column(String(64), unique=True, index=True, nullable=False)
    entity_name = Column(String(255), nullable=False, index=True)
    entity_designation_or_type = Column(String(100), nullable=False)

    matter_in_dispute = Column(Text, nullable=False)
    notice_dispatched_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    deadline_date = Column(Date, nullable=False)

    status = Column(SqlEnum(RightOfReplyStatus), default=RightOfReplyStatus.NOTICE_DISPATCHED, nullable=False)
    response_received_at = Column(DateTime, nullable=True)
    rebuttal_statement = Column(Text, nullable=True)
    rebuttal_doc_sha256 = Column(String(64), nullable=True)


class PublicCorrectionNotice(Base):
    """
    Public correction and retraction log ensuring transparent accountability of the platform itself.
    """
    __tablename__ = "public_corrections"

    id = Column(Integer, primary_key=True, index=True)
    notice_id = Column(String(64), unique=True, index=True, nullable=False)  # e.g. CORR-2024-001
    target_record_ref = Column(String(128), nullable=False, index=True)

    original_statement = Column(Text, nullable=False)
    corrected_statement = Column(Text, nullable=False)
    reason_for_correction = Column(Text, nullable=False)

    published_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    editor_signoff = Column(String(100), nullable=False)


# ==============================================================================
# Epistemic & Legal Guardrail Functions
# ==============================================================================

PROHIBITED_DEFAMATORY_TERMS = [
    r"\bcorrupt\b",
    r"\bcorruption\b",
    r"\bguilty\b",
    r"\bcriminal\b",
    r"\bfraudulent\b",
    r"\bscam\b",
    r"\bthief\b",
    r"\bbribe\b",
    r"\bembezzler\b",
]

def enforce_bns_defamation_guardrail(text: str, has_statutory_court_judgment: bool = False) -> None:
    """
    Hardcoded epistemic guardrail enforcing BNS 2023 Sec 356 compliance.
    Forbids automated models or system texts from assigning criminal/corrupt guilt
    to any person or entity without an explicit statutory or judicial conviction reference.
    """
    if has_statutory_court_judgment:
        return

    lower_text = text.lower()
    for pattern in PROHIBITED_DEFAMATORY_TERMS:
        if re.search(pattern, lower_text):
            raise ValueError(
                f"BNS 2023 Sec 356 Defamation Safeguard Breach: Disallowed term matching '{pattern}' "
                f"found in statement without formal statutory judicial decree citation. "
                f"CIVICLENS TN strictly presents objective administrative records, non-adjudicative discrepancies, "
                f"and verified evidence without asserting criminal guilt."
            )
