"""
Unit Tests for Phase 11 Advanced Governance & Production Architecture
"""
import pytest
from datetime import date
from backend.models.governance_advanced import (
    MinisterialAssurance, GovernmentOrderLifecycle, MLModelRegistry,
    AssuranceStatus, GOStatus, GOType, ModelTaskType
)
from backend.services.governance_advanced_service import GovernanceAdvancedService
from backend.core.storage import DocumentStorage


def test_ministerial_assurance_tracking(db_session):
    """Verify TNLA ministerial floor assurance recording and status."""
    assur = GovernanceAdvancedService.record_assurance(
        db=db_session,
        assurance_code="TEST-ASSUR-2024-001",
        mla_name="Thiru M. Appavu",
        minister_name="Minister for Water Resources",
        portfolio_department="Water Resources Department",
        date_given=date(2024, 4, 1),
        assurance_statement="Tamirabarani river basin desilting will be taken up before monsoon.",
        constituency_name="Radhapuram",
    )
    assert assur.id is not None
    assert assur.status == AssuranceStatus.PENDING_DEPARTMENT_ACTION
    assert assur.mla_name == "Thiru M. Appavu"


def test_government_order_lifecycle_and_supersession(db_session):
    """Verify G.O. registration and automatic supersession of prior G.O."""
    go1 = GovernanceAdvancedService.register_government_order(
        db=db_session,
        go_number="G.O. (Ms) No. 101",
        issuing_department="School Education Department",
        issue_date=date(2022, 5, 10),
        subject_summary="Initial guidelines for smart classroom deployment.",
    )
    assert go1.status == GOStatus.ACTIVE

    # New G.O. supersedes G.O. 101
    go2 = GovernanceAdvancedService.register_government_order(
        db=db_session,
        go_number="G.O. (Ms) No. 102",
        issuing_department="School Education Department",
        issue_date=date(2024, 2, 14),
        subject_summary="Revised guidelines superseding G.O. (Ms) No. 101.",
        supersedes_go_number="G.O. (Ms) No. 101",
    )
    assert go2.status == GOStatus.ACTIVE
    assert go1.status == GOStatus.SUPERSEDED  # Automatically transitioned!


def test_ml_model_registry_and_accusation_guardrail(db_session):
    """Verify ML model registry enforces automated_accusation_permitted=False."""
    model = GovernanceAdvancedService.register_ml_model(
        db=db_session,
        model_identifier="TEST_ML_MODEL_v1.0",
        model_name="Grievance Domain Classifier",
        task_type=ModelTaskType.GRIEVANCE_DOMAIN_CLASSIFIER,
        model_version="1.0.0",
        training_dataset_sha256="sample_hash_12345",
        primary_metric_name="MACRO_F1",
        primary_metric_value=0.915,
    )
    assert model.id is not None
    assert model.primary_metric_value == 0.915
    assert model.automated_accusation_permitted is False  # Guardrail verified


def test_document_storage_vault(tmp_path):
    """Verify content-addressable document storage and SHA-256 integrity verification."""
    vault = DocumentStorage(base_storage_dir=str(tmp_path))
    content = b"Official Tamil Nadu Government Gazette Sample Text"
    sha, path = vault.save_document(content, "gazette.pdf")

    assert len(sha) == 64
    retrieved = vault.retrieve_document(sha)
    assert retrieved == content
