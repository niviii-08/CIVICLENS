"""
CIVICLENS TN — Advanced Governance Service (Phase 11)
"""
from datetime import date, datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from backend.models.governance_advanced import (
    MinisterialAssurance, GovernmentOrderLifecycle, MLModelRegistry,
    AssuranceStatus, GOStatus, GOType, ModelTaskType
)


class GovernanceAdvancedService:
    """Service orchestrating legislative assurances, G.O. lifecycles, and model registry."""

    @staticmethod
    def record_assurance(
        db: Session,
        assurance_code: str,
        mla_name: str,
        minister_name: str,
        portfolio_department: str,
        date_given: date,
        assurance_statement: str,
        question_number: Optional[str] = None,
        constituency_name: Optional[str] = None,
        assurance_statement_ta: Optional[str] = None,
    ) -> MinisterialAssurance:
        """Log a formal ministerial assurance given on the Tamil Nadu Legislative Assembly floor."""
        assur = MinisterialAssurance(
            assurance_code=assurance_code,
            question_number=question_number,
            mla_name=mla_name,
            constituency_name=constituency_name,
            minister_name=minister_name,
            portfolio_department=portfolio_department,
            date_given=date_given,
            assurance_statement=assurance_statement,
            assurance_statement_ta=assurance_statement_ta,
            status=AssuranceStatus.PENDING_DEPARTMENT_ACTION,
        )
        db.add(assur)
        db.commit()
        db.refresh(assur)
        return assur

    @staticmethod
    def register_government_order(
        db: Session,
        go_number: str,
        issuing_department: str,
        issue_date: date,
        subject_summary: str,
        go_type: GOType = GOType.GO_MS,
        supersedes_go_number: Optional[str] = None,
        full_gazette_url: Optional[str] = None,
        gazette_pdf_sha256: Optional[str] = None,
    ) -> GovernmentOrderLifecycle:
        """Register a Government Order and update any superseded G.O.'s status."""
        # If this G.O. supersedes an older G.O., mark the older one SUPERSEDED
        if supersedes_go_number:
            old_go = db.query(GovernmentOrderLifecycle).filter_by(go_number=supersedes_go_number).first()
            if old_go:
                old_go.status = GOStatus.SUPERSEDED

        go = GovernmentOrderLifecycle(
            go_number=go_number,
            issuing_department=issuing_department,
            go_type=go_type,
            issue_date=issue_date,
            subject_summary=subject_summary,
            status=GOStatus.ACTIVE,
            supersedes_go_number=supersedes_go_number,
            full_gazette_url=full_gazette_url,
            gazette_pdf_sha256=gazette_pdf_sha256,
        )
        db.add(go)
        db.commit()
        db.refresh(go)
        return go

    @staticmethod
    def register_ml_model(
        db: Session,
        model_identifier: str,
        model_name: str,
        task_type: ModelTaskType,
        model_version: str,
        training_dataset_sha256: str,
        primary_metric_name: str,
        primary_metric_value: float,
        drift_threshold: float = 0.05,
    ) -> MLModelRegistry:
        """Register a validated machine learning model with mandatory epistemic guardrails."""
        entry = MLModelRegistry(
            model_identifier=model_identifier,
            model_name=model_name,
            task_type=task_type,
            model_version=model_version,
            training_dataset_sha256=training_dataset_sha256,
            primary_metric_name=primary_metric_name,
            primary_metric_value=primary_metric_value,
            drift_threshold=drift_threshold,
            last_evaluated_date=date.today(),
            is_active_in_production=True,
            automated_accusation_permitted=False,  # Non-negotiable guardrail
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
