"""

Public representative, constituency, election, and legislative performance models.

Defines SQLAlchemy ORM entities for elected representatives (MLAs/MPs),

electoral constituencies, election history, representative terms,

constituency public works, development indicators, and performance metrics.

"""

import enum

from datetime import datetime, timezone

from typing import List, Optional

from sqlalchemy import (

    Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, JSON

)

from sqlalchemy.orm import relationship

from backend.database.base_class import Base

class RepresentativeType(str, enum.Enum):

    MLA = "MLA"

    LOK_SABHA_MP = "LOK_SABHA_MP"

    RAJYA_SABHA_MP = "RAJYA_SABHA_MP"

class ConstituencyType(str, enum.Enum):

    ASSEMBLY = "ASSEMBLY"

    PARLIAMENTARY = "PARLIAMENTARY"

class ElectionType(str, enum.Enum):

    STATE_ASSEMBLY = "STATE_ASSEMBLY"

    LOK_SABHA = "LOK_SABHA"

    RAJYA_SABHA = "RAJYA_SABHA"

class Representative(Base):

    """

    Canonical elected representative entity (MLA, Lok Sabha MP, Rajya Sabha MP).

    Maintains official name, known aliases, primary/current affiliation, and links to terms.

    """

    __tablename__ = "representatives"

    representative_id = Column(String, primary_key=True, index=True)

    official_name = Column(String, nullable=False, index=True)

    aliases = Column(JSON, default=list)
    representative_type = Column(String, nullable=False, index=True)

    party_id = Column(String, ForeignKey("political_parties.party_id", ondelete="SET NULL"), nullable=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="SET NULL"), nullable=True, index=True)

    election_id = Column(String, ForeignKey("elections.election_id", ondelete="SET NULL"), nullable=True, index=True)

    term_start = Column(String, nullable=True)

    term_end = Column(String, nullable=True)
    source_document_ids = Column(JSON, default=list)

    person_id = Column(String, ForeignKey("political_persons.person_id", ondelete="SET NULL"), nullable=True, index=True)

    date_of_birth = Column(String, nullable=True)

    gender = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    party = relationship("PoliticalParty", foreign_keys=[party_id])

    constituency = relationship("Constituency", foreign_keys=[constituency_id], back_populates="representatives")

    election = relationship("Election", foreign_keys=[election_id])

    terms = relationship("RepresentativeTerm", back_populates="representative", cascade="all, delete-orphan")

    legislative_activities = relationship("LegislativeActivity", back_populates="representative", cascade="all, delete-orphan")

    constituency_works = relationship("ConstituencyWork", back_populates="representative")

class Constituency(Base):

    """

    State Assembly or Parliamentary electoral constituency in Tamil Nadu.

    Preserves historical validity periods and delimitation boundaries.

    """

    __tablename__ = "constituencies"

    constituency_id = Column(String, primary_key=True, index=True)

    official_name = Column(String, nullable=False, index=True)

    constituency_type = Column(String, nullable=False, index=True)
    district = Column(String, nullable=False, index=True)

    state = Column(String, default="Tamil Nadu")

    valid_from = Column(String, nullable=False, default="2008")
    valid_to = Column(String, nullable=True)
    source_document_ids = Column(JSON, default=list)

    reservation_status = Column(String, default="GENERAL")
    delimitation_year = Column(Integer, default=2008)

    predecessor_id = Column(String, nullable=True)

    successor_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representatives = relationship("Representative", foreign_keys="[Representative.constituency_id]", back_populates="constituency")

    terms = relationship("RepresentativeTerm", back_populates="constituency")

    boundary_history = relationship("ConstituencyBoundaryHistory", back_populates="constituency", cascade="all, delete-orphan")

    constituency_works = relationship("ConstituencyWork", back_populates="constituency", cascade="all, delete-orphan")

    development_indicators = relationship("DevelopmentIndicator", back_populates="constituency")

    geographic_mappings = relationship("ConstituencyGeographicMapping", back_populates="constituency", cascade="all, delete-orphan")

class Election(Base):

    """

    State Assembly or Parliamentary general/bye-election cycle.

    """

    __tablename__ = "elections"

    election_id = Column(String, primary_key=True, index=True)

    election_name = Column(String, nullable=False)

    election_type = Column(String, nullable=False, index=True)
    election_year = Column(Integer, nullable=False, index=True)

    poll_date = Column(String, nullable=True)

    counting_date = Column(String, nullable=True)

    total_turnout_pct = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    terms = relationship("RepresentativeTerm", back_populates="election")

class RepresentativeTerm(Base):

    """

    Granular tenure record tying a representative to a specific constituency, election,

    and party affiliation for that specific historical term.

    Guarantees historical party affiliation is never overwritten by current affiliation.

    """

    __tablename__ = "representative_terms"

    term_id = Column(String, primary_key=True, index=True)

    representative_id = Column(String, ForeignKey("representatives.representative_id", ondelete="CASCADE"), nullable=False, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="SET NULL"), nullable=True, index=True)

    election_id = Column(String, ForeignKey("elections.election_id", ondelete="SET NULL"), nullable=True, index=True)

    party_id = Column(String, ForeignKey("political_parties.party_id", ondelete="SET NULL"), nullable=True, index=True)

    term_number = Column(Integer, default=1)

    house_type = Column(String, nullable=False)
    term_start = Column(String, nullable=False)

    term_end = Column(String, nullable=True)

    is_active_term = Column(Boolean, default=False)

    source_document_ids = Column(JSON, default=list)

    votes_polled = Column(Integer, nullable=True)

    win_margin_votes = Column(Integer, nullable=True)

    win_margin_percent = Column(Float, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representative = relationship("Representative", back_populates="terms")

    constituency = relationship("Constituency", back_populates="terms")

    election = relationship("Election", back_populates="terms")

    party = relationship("PoliticalParty", foreign_keys=[party_id])

class ConstituencyBoundaryHistory(Base):

    """

    Tracks historical boundary, delimitation order, or naming changes for constituencies.

    """

    __tablename__ = "constituency_boundary_history"

    history_id = Column(String, primary_key=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="CASCADE"), nullable=False, index=True)

    historical_name = Column(String, nullable=False)

    delimitation_order = Column(String, nullable=False)
    valid_from = Column(String, nullable=False)

    valid_to = Column(String, nullable=True)

    change_summary = Column(Text, nullable=True)

    source_document_ids = Column(JSON, default=list)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    constituency = relationship("Constituency", back_populates="boundary_history")

class LegislativeActivityType(str, enum.Enum):

    QUESTION_STARRED = "QUESTION_STARRED"

    QUESTION_UNSTARRED = "QUESTION_UNSTARRED"

    DEBATE = "DEBATE"

    ATTENDANCE = "ATTENDANCE"

    COMMITTEE = "COMMITTEE"

    BILL = "BILL"

    CALL_ATTENTION = "CALL_ATTENTION"

    ZERO_HOUR = "ZERO_HOUR"

class DataQualityStatus(str, enum.Enum):

    VERIFIED = "VERIFIED"

    PARTIAL = "PARTIAL"

    UNAVAILABLE = "UNAVAILABLE"

    NOT_RECORDED = "NOT_RECORDED"

class LegislativeActivity(Base):

    """

    Granular record of representative parliamentary or assembly activity.

    Stores questions submitted, debates participated, attendance percentage,

    bills introduced, and committee participation with full source provenance.

    """

    __tablename__ = "legislative_activities"

    activity_id = Column(String, primary_key=True, index=True)

    representative_id = Column(String, ForeignKey("representatives.representative_id", ondelete="CASCADE"), nullable=False, index=True)

    legislative_body = Column(String, nullable=False, index=True)
    session = Column(String, nullable=False, index=True)
    activity_type = Column(String, nullable=False, index=True)
    activity_date = Column(String, nullable=True, index=True)

    count = Column(Integer, default=1)

    value = Column(Float, nullable=True)
    title_subject = Column(String, nullable=True)

    ministry_or_department = Column(String, nullable=True)

    source_document_id = Column(String, nullable=True, index=True)

    source_reference = Column(String, nullable=True)
    data_quality_status = Column(String, nullable=False, default="VERIFIED")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representative = relationship("Representative", back_populates="legislative_activities")

class WorkProjectStatus(str, enum.Enum):

    PROPOSED = "PROPOSED"

    SANCTIONED = "SANCTIONED"

    FUNDS_RELEASED = "FUNDS_RELEASED"

    WORK_IN_PROGRESS = "WORK_IN_PROGRESS"

    REPORTED_COMPLETED = "REPORTED_COMPLETED"

    INDEPENDENTLY_VERIFIED_COMPLETED = "INDEPENDENTLY_VERIFIED_COMPLETED"

    UNKNOWN = "UNKNOWN"

class AttributionType(str, enum.Enum):

    REPRESENTATIVE_SPONSORED = "REPRESENTATIVE_SPONSORED"
    EXECUTIVE_STATE_PROJECT = "EXECUTIVE_STATE_PROJECT"
    EXECUTIVE_CENTRAL_PROJECT = "EXECUTIVE_CENTRAL_PROJECT"
    UNKNOWN = "UNKNOWN"

class ConstituencyWork(Base):

    """

    Constituency-level development work, project, or infrastructure scheme.

    Explicitly tracks allocation vs sanctioned vs released vs reported expenditure,

    distinguishes representative-sponsored works from general executive projects,

    and supports independent verification auditing.

    """

    __tablename__ = "constituency_works"

    work_id = Column(String, primary_key=True, index=True)

    representative_id = Column(String, ForeignKey("representatives.representative_id", ondelete="SET NULL"), nullable=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="CASCADE"), nullable=False, index=True)

    scheme_id = Column(String, nullable=False, index=True)

    project_description = Column(Text, nullable=False)

    sanctioned_amount = Column(Float, nullable=False, default=0.0)

    released_amount = Column(Float, nullable=False, default=0.0)

    reported_expenditure = Column(Float, nullable=False, default=0.0)

    approval_date = Column(String, nullable=True)
    completion_date = Column(String, nullable=True)
    project_status = Column(String, nullable=False, index=True, default=WorkProjectStatus.PROPOSED)

    implementing_agency = Column(String, nullable=True)

    source_document_id = Column(String, nullable=True, index=True)

    source_reference = Column(String, nullable=True)

    attribution_type = Column(String, nullable=False, default=AttributionType.REPRESENTATIVE_SPONSORED)

    verification_source = Column(String, nullable=True)
    has_conflicting_status = Column(Boolean, default=False)

    data_quality_issues = Column(JSON, default=list)

    last_updated = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representative = relationship("Representative", back_populates="constituency_works")

    constituency = relationship("Constituency", back_populates="constituency_works")

class GeographicLevel(str, enum.Enum):

    CONSTITUENCY = "CONSTITUENCY"

    DISTRICT = "DISTRICT"

    STATE = "STATE"

    BLOCK_TALUK = "BLOCK_TALUK"

class CalculationMethod(str, enum.Enum):

    DIRECT_OBSERVATION = "DIRECT_OBSERVATION"

    AREA_WEIGHTED_INTERPOLATION = "AREA_WEIGHTED_INTERPOLATION"

    POPULATION_WEIGHTED_AGGREGATION = "POPULATION_WEIGHTED_AGGREGATION"

    OFFICIAL_PUBLICATION = "OFFICIAL_PUBLICATION"

class IndicatorQualityStatus(str, enum.Enum):

    VERIFIED = "VERIFIED"

    INTERPOLATED = "INTERPOLATED"

    PROVISIONAL = "PROVISIONAL"

    ESTIMATED = "ESTIMATED"

    INCONSISTENT_UNIT = "INCONSISTENT_UNIT"

    MISSING = "MISSING"

class DevelopmentIndicator(Base):

    """

    Socioeconomic, demographic, or departmental development indicator.

    Stores observations at constituency, district, or state levels with explicit

    calculation methodology and data quality tracking.

    """

    __tablename__ = "development_indicators"

    indicator_id = Column(String, primary_key=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="SET NULL"), nullable=True, index=True)

    geographic_unit_id = Column(String, nullable=False, index=True)
    indicator_name = Column(String, nullable=False, index=True)

    value = Column(Float, nullable=False)

    unit = Column(String, nullable=False)
    reference_period = Column(String, nullable=False, index=True)
    geographic_level = Column(String, nullable=False, index=True)

    source_document_id = Column(String, nullable=True, index=True)

    source_reference = Column(String, nullable=True)
    calculation_method = Column(String, nullable=False, default=CalculationMethod.OFFICIAL_PUBLICATION)

    data_quality_status = Column(String, nullable=False, default=IndicatorQualityStatus.VERIFIED)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    constituency = relationship("Constituency", back_populates="development_indicators")

class ConstituencyGeographicMapping(Base):

    """

    Spatial and administrative intersection mapping between an electoral constituency

    and standard administrative boundaries (districts, taluks).

    Provides defensible population and area weights for geographic interpolation.

    """

    __tablename__ = "constituency_geographic_mappings"

    mapping_id = Column(String, primary_key=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="CASCADE"), nullable=False, index=True)

    district_name = Column(String, nullable=False, index=True)

    taluk_names = Column(JSON, default=list)

    area_share_in_district = Column(Float, default=1.0)
    population_share_in_district = Column(Float, default=1.0)
    delimitation_year = Column(Integer, default=2008)

    mapping_methodology = Column(String, default="ECI_DELIMITATION_ORDER_2008")

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    constituency = relationship("Constituency", back_populates="geographic_mappings")

class PromiseEvidenceStage(str, enum.Enum):

    PROMISE_IDENTIFIED = "PROMISE_IDENTIFIED"

    RELEVANT_SCHEME_IDENTIFIED = "RELEVANT_SCHEME_IDENTIFIED"

    POLICY_ACTION_DOCUMENTED = "POLICY_ACTION_DOCUMENTED"

    PROJECT_WORK_RECORDED = "PROJECT_WORK_RECORDED"

    OUTCOME_INDICATOR_OBSERVED = "OUTCOME_INDICATOR_OBSERVED"

    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

class PromisePerformanceLink(Base):

    """

    Connects elected representatives and their party manifesto promises (Phase 3)

    with government schemes (Phase 2), statutory evidence, local constituency works,

    and socioeconomic development indicators.

    """

    __tablename__ = "promise_performance_links"

    link_id = Column(String, primary_key=True, index=True)

    representative_id = Column(String, ForeignKey("representatives.representative_id", ondelete="CASCADE"), nullable=False, index=True)

    promise_id = Column(String, ForeignKey("political_promises.promise_id", ondelete="CASCADE"), nullable=False, index=True)

    party_id = Column(String, ForeignKey("political_parties.party_id", ondelete="SET NULL"), nullable=True, index=True)

    election_id = Column(String, ForeignKey("elections.election_id", ondelete="SET NULL"), nullable=True, index=True)

    scheme_id = Column(String, nullable=True, index=True)

    evidence_id = Column(Integer, ForeignKey("evidence.id", ondelete="SET NULL"), nullable=True, index=True)

    work_id = Column(String, ForeignKey("constituency_works.work_id", ondelete="SET NULL"), nullable=True, index=True)

    indicator_id = Column(String, ForeignKey("development_indicators.indicator_id", ondelete="SET NULL"), nullable=True, index=True)

    evidence_stage = Column(String, nullable=False, index=True, default=PromiseEvidenceStage.PROMISE_IDENTIFIED)

    matching_method = Column(String, default="PARTY_MANIFESTO_DIRECT")

    match_confidence = Column(Float, default=1.0)

    has_conflicting_dates = Column(Boolean, default=False)

    evidence_summary = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representative = relationship("Representative", backref="promise_links")

    promise = relationship("PoliticalPromise", backref="representative_links")

    evidence = relationship("Evidence", foreign_keys=[evidence_id])

    constituency_work = relationship("ConstituencyWork", foreign_keys=[work_id])

    development_indicator = relationship("DevelopmentIndicator", foreign_keys=[indicator_id])

class PerformanceDimension(str, enum.Enum):

    LEGISLATIVE_ACTIVITY = "LEGISLATIVE_ACTIVITY"

    CONSTITUENCY_WORKS = "CONSTITUENCY_WORKS"

    FINANCIAL_EXECUTION = "FINANCIAL_EXECUTION"

    DEVELOPMENT_TRENDS = "DEVELOPMENT_TRENDS"

    PROMISE_EVIDENCE = "PROMISE_EVIDENCE"

    DATA_COMPLETENESS = "DATA_COMPLETENESS"

class PerformanceMetric(Base):

    """

    Transparent, auditable performance metric record for representatives and constituencies.

    Preserves raw indicators, normalized indicators (0-100), explicit weighting,

    data completeness indices, and methodological caveats.

    """

    __tablename__ = "performance_metrics"

    metric_id = Column(String, primary_key=True, index=True)

    representative_id = Column(String, ForeignKey("representatives.representative_id", ondelete="CASCADE"), nullable=True, index=True)

    constituency_id = Column(String, ForeignKey("constituencies.constituency_id", ondelete="CASCADE"), nullable=True, index=True)

    election_term_id = Column(String, nullable=True, index=True)
    reporting_period = Column(String, nullable=False, index=True)

    dimension = Column(String, nullable=False, index=True)
    metric_code = Column(String, nullable=False, index=True)

    raw_value = Column(Float, nullable=True)
    raw_unit = Column(String, nullable=True)
    normalized_score = Column(Float, nullable=True)
    percentile_rank = Column(Float, nullable=True)

    data_completeness_ratio = Column(Float, default=1.0)
    is_sufficient_data = Column(Boolean, default=True)

    normalization_method = Column(String, nullable=True)
    cohort_definition = Column(String, nullable=True)

    component_breakdown = Column(JSON, default=dict)
    sensitivity_analysis = Column(JSON, default=dict)
    methodological_caveats = Column(JSON, default=list)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    representative = relationship("Representative", backref="performance_metrics")

    constituency = relationship("Constituency", backref="performance_metrics")

class SourceDocumentRegistry(Base):

    """

    Canonical Source Document Registry for representative performance.

    Stores statutory and empirical documents with publisher, version, SHA-256 hash, and provenance.

    """

    __tablename__ = "phase6_source_documents"

    document_id = Column(String, primary_key=True, index=True)
    source_name = Column(String, nullable=False, index=True)

    source_type = Column(String, nullable=False, index=True)
    official_source_url = Column(String, nullable=True)

    original_filename = Column(String, nullable=True)

    document_title = Column(String, nullable=False)

    publisher = Column(String, nullable=False)
    publication_date = Column(String, nullable=True)

    retrieval_date = Column(String, nullable=True)

    document_version = Column(String, default="1.0")

    sha256_checksum = Column(String, nullable=True)

    file_format = Column(String, nullable=False, default="PDF")
    reporting_period = Column(String, nullable=True, index=True)

    geographic_coverage = Column(String, nullable=False, default="TAMIL_NADU")

    verification_status = Column(String, nullable=False, default="VERIFIED")
    storage_path = Column(String, nullable=True)

    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

class FactEvidenceLink(Base):

    """

    Step 3: Granular Fact Evidence Relationship.

    Links any canonical fact or record directly to its supporting source document,

    specific page, table/section identifier, exact excerpt, and extraction confidence.

    """

    __tablename__ = "phase6_fact_evidence_links"

    link_id = Column(String, primary_key=True, index=True)

    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)
    fact_description = Column(String, nullable=False)

    document_id = Column(String, ForeignKey("phase6_source_documents.document_id", ondelete="CASCADE"), nullable=False, index=True)

    page_number = Column(Integer, nullable=True)

    section_or_table = Column(String, nullable=True)
    source_row_id = Column(String, nullable=True)

    supporting_excerpt = Column(Text, nullable=True)
    extraction_method = Column(String, default="MANUAL_VERIFIED")
    verification_status = Column(String, default="VERIFIED")
    confidence_score = Column(Float, default=1.0)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source_document = relationship("SourceDocumentRegistry", backref="evidence_links")

class MetricLineage(Base):

    """

    Step 4: Reproducible Metric Lineage.

    Stores the exact formula, mathematical transformation, and input record IDs

    that produced any derived or aggregate performance metric.

    """

    __tablename__ = "phase6_metric_lineages"

    lineage_id = Column(String, primary_key=True, index=True)

    metric_id = Column(String, ForeignKey("performance_metrics.metric_id", ondelete="CASCADE"), nullable=False, index=True)

    metric_name = Column(String, nullable=False)

    metric_value = Column(Float, nullable=False)

    calculation_method = Column(String, nullable=False)
    formula_expression = Column(String, nullable=False)
    input_record_ids = Column(JSON, default=list)
    source_document_ids = Column(JSON, default=list)

    reporting_period = Column(String, nullable=False)

    geographic_level = Column(String, nullable=False)

    calculation_version = Column(String, default="1.0")

    data_quality_status = Column(String, default="VERIFIED")

    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    metric = relationship("PerformanceMetric", backref="lineages")

class ConflictResolutionStatus(str, enum.Enum):

    CONSISTENT = "CONSISTENT"

    CONFLICTING = "CONFLICTING"

    REQUIRES_REVIEW = "REQUIRES_REVIEW"

    NOT_COMPARABLE = "NOT_COMPARABLE"

    UNRESOLVED = "UNRESOLVED"

    RESOLVED = "RESOLVED"

class ConflictingEvidenceRecord(Base):

    """

    Step 5: Conflicting Evidence Registry.

    Preserves divergent reports across official or secondary sources without arbitrary suppression.

    """

    __tablename__ = "phase6_conflicting_evidence"

    conflict_id = Column(String, primary_key=True, index=True)

    entity_type = Column(String, nullable=False, index=True)
    entity_id = Column(String, nullable=False, index=True)

    conflict_topic = Column(String, nullable=False)

    source_a_document_id = Column(String, ForeignKey("phase6_source_documents.document_id", ondelete="SET NULL"), nullable=True)

    source_a_value = Column(String, nullable=False)
    source_a_period = Column(String, nullable=True)

    source_b_document_id = Column(String, ForeignKey("phase6_source_documents.document_id", ondelete="SET NULL"), nullable=True)

    source_b_value = Column(String, nullable=False)
    source_b_period = Column(String, nullable=True)

    discrepancy_magnitude = Column(String, nullable=True)
    review_status = Column(String, nullable=False, default=ConflictResolutionStatus.CONFLICTING)

    resolution_basis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    source_a = relationship("SourceDocumentRegistry", foreign_keys=[source_a_document_id])

    source_b = relationship("SourceDocumentRegistry", foreign_keys=[source_b_document_id])

class AuditTrailEvent(Base):

    """

    Step 8: Immutable Audit Trail Ledger.

    Tracks critical lifecycle processing events: ingestion, extraction, normalization,

    corrections, and verification updates.

    """

    __tablename__ = "phase6_audit_trail_events"

    event_id = Column(String, primary_key=True, index=True)

    event_type = Column(String, nullable=False, index=True)
    entity_type = Column(String, nullable=False, index=True)
    record_id = Column(String, nullable=False, index=True)

    previous_value = Column(JSON, nullable=True)

    new_value = Column(JSON, nullable=True)

    reason = Column(Text, nullable=True)

    source_reference = Column(String, nullable=True)

    actor_or_process = Column(String, nullable=False, default="SYSTEM_PIPELINE")

    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))

