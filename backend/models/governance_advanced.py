"""
CIVICLENS TN — Advanced Governance & Production Architecture Models (Phase 11)

Provides:
1. Legislative Follow-Through & Ministerial Assurances
2. Government Order (G.O.) Lifecycle & Versioning (Supersessions, Amendments, Repeals)
3. Machine Learning Model Registry & Epistemic Drift Monitoring
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


class AssuranceStatus(str, enum.Enum):
    PENDING_DEPARTMENT_ACTION = "PENDING_DEPARTMENT_ACTION"
    IMPLEMENTATION_IN_PROGRESS = "IMPLEMENTATION_IN_PROGRESS"
    FULFILLED_AND_DROPPED = "FULFILLED_AND_DROPPED"
    PARTIALLY_IMPLEMENTED = "PARTIALLY_IMPLEMENTED"
    LAPSED_DUE_TO_DISSOLUTION = "LAPSED_DUE_TO_DISSOLUTION"


class GOStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    AMENDED = "AMENDED"
    SUPERSEDED = "SUPERSEDED"
    REPEALED = "REPEALED"
    INOPERATIVE = "INOPERATIVE"


class GOType(str, enum.Enum):
    GO_MS = "GO_MS"  # Manuscript (Policy)
    GO_RT = "GO_RT"  # Routine / Administrative
    GO_2D = "GO_2D"  # Directorate level
    GO_3D = "GO_3D"  # Minor sanctions


class ModelTaskType(str, enum.Enum):
    BUDGET_CLUSTERING = "BUDGET_CLUSTERING"
    ANOMALY_DETECTION = "ANOMALY_DETECTION"
    MEDIA_FRAMING_DECONSTRUCTION = "MEDIA_FRAMING_DECONSTRUCTION"
    PROMISE_BUDGET_MATCHER = "PROMISE_BUDGET_MATCHER"
    GRIEVANCE_DOMAIN_CLASSIFIER = "GRIEVANCE_DOMAIN_CLASSIFIER"


class MinisterialAssurance(Base):
    """
    Legislative Follow-Through:
    Tracks formal assurances given by Ministers on the floor of the Tamil Nadu Legislative Assembly (TNLA)
    under Rule 164 of the TNLA Rules, monitored by the Committee on Government Assurances.
    """
    __tablename__ = "legislative_ministerial_assurances"

    id = Column(Integer, primary_key=True, index=True)
    assurance_code = Column(String(64), unique=True, index=True, nullable=False)  # e.g. ASSUR-TNLA-16-2023-084
    assembly_number = Column(Integer, default=16)  # 16th TN Legislative Assembly
    session_number = Column(String(32), nullable=True)  # e.g. "Budget Session 2023"

    question_number = Column(String(64), nullable=True, index=True)  # Starred/Unstarred question ref
    mla_name = Column(String(255), nullable=False)  # Member asking the question
    constituency_name = Column(String(100), nullable=True)

    minister_name = Column(String(255), nullable=False)
    portfolio_department = Column(String(255), nullable=False, index=True)
    date_given = Column(Date, nullable=False)

    assurance_statement = Column(Text, nullable=False)
    assurance_statement_ta = Column(Text, nullable=True)

    status = Column(SqlEnum(AssuranceStatus), default=AssuranceStatus.PENDING_DEPARTMENT_ACTION, nullable=False, index=True)
    committee_scrutiny_date = Column(Date, nullable=True)
    committee_remarks = Column(Text, nullable=True)

    action_taken_summary = Column(Text, nullable=True)
    action_taken_order_ref = Column(String(128), nullable=True)  # G.O. or circular issued in fulfillment
    action_verified_date = Column(Date, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class GovernmentOrderLifecycle(Base):
    """
    Tracks the lifecycle, amendments, supersessions, and repeals of Government Orders (G.O.s).
    Guarantees that references point to active, valid administrative law.
    """
    __tablename__ = "government_order_lifecycles"

    id = Column(Integer, primary_key=True, index=True)
    go_number = Column(String(128), unique=True, index=True, nullable=False)  # e.g. "G.O. (Ms) No. 34"
    issuing_department = Column(String(255), nullable=False, index=True)
    go_type = Column(SqlEnum(GOType), default=GOType.GO_MS, nullable=False)

    issue_date = Column(Date, nullable=False)
    subject_summary = Column(Text, nullable=False)
    subject_summary_ta = Column(Text, nullable=True)

    status = Column(SqlEnum(GOStatus), default=GOStatus.ACTIVE, nullable=False, index=True)

    # Versioning & Lineage
    supersedes_go_number = Column(String(128), nullable=True)
    amended_by_go_number = Column(String(128), nullable=True)
    repealed_by_go_number = Column(String(128), nullable=True)

    full_gazette_url = Column(String(512), nullable=True)
    gazette_pdf_sha256 = Column(String(64), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class MLModelRegistry(Base):
    """
    Epistemic & Analytical Validity:
    Tracks machine learning models deployed across the platform (clustering, anomaly detection, NLP).
    Records dataset provenance, evaluation metrics, drift thresholds, and human override logs.
    """
    __tablename__ = "ml_model_registry"

    id = Column(Integer, primary_key=True, index=True)
    model_identifier = Column(String(100), unique=True, index=True, nullable=False)  # e.g. "ISOLATION_FOREST_BUDGET_v2.1"
    model_name = Column(String(255), nullable=False)
    task_type = Column(SqlEnum(ModelTaskType), nullable=False)

    model_version = Column(String(32), nullable=False)
    framework = Column(String(64), default="scikit-learn")

    training_dataset_sha256 = Column(String(64), nullable=False)
    hyperparameters_json = Column(JSON, nullable=True)

    primary_metric_name = Column(String(64), default="F1_SCORE")
    primary_metric_value = Column(Float, nullable=False)
    drift_threshold = Column(Float, default=0.05)  # Alert when performance or feature distribution drifts > 5%

    last_evaluated_date = Column(Date, nullable=False)
    is_active_in_production = Column(Boolean, default=True)

    human_override_count = Column(Integer, default=0)
    audit_notes = Column(Text, nullable=True)

    # Hardcoded Rule: No standalone algorithmic accusation
    automated_accusation_permitted = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
