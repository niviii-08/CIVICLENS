"""
CIVICLENS TN — Advanced Governance & Oversight API Blueprint (Phase 11)
"""
from flask import Blueprint, request
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.governance_advanced import (
    MinisterialAssurance, GovernmentOrderLifecycle, MLModelRegistry,
    AssuranceStatus, GOStatus
)
from backend.services.governance_advanced_service import GovernanceAdvancedService

governance_advanced_bp = Blueprint("governance_advanced", __name__, url_prefix="/governance")


@governance_advanced_bp.route("/assurances", methods=["GET"])
def list_assurances():
    """List TNLA ministerial assurances with committee scrutiny statuses."""
    db = SessionLocal()
    try:
        dept = request.args.get("department")
        status = request.args.get("status")

        q = db.query(MinisterialAssurance)
        if dept:
            q = q.filter(MinisterialAssurance.portfolio_department == dept)
        if status:
            q = q.filter(MinisterialAssurance.status == status)

        assurances = q.order_by(MinisterialAssurance.date_given.desc()).limit(100).all()
        data = [
            {
                "id": a.id,
                "code": a.assurance_code,
                "mla": a.mla_name,
                "constituency": a.constituency_name,
                "minister": a.minister_name,
                "department": a.portfolio_department,
                "date_given": a.date_given.isoformat(),
                "statement": a.assurance_statement,
                "statement_ta": a.assurance_statement_ta,
                "status": a.status.value,
                "action_taken": a.action_taken_summary,
            }
            for a in assurances
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} ministerial assurances")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@governance_advanced_bp.route("/orders", methods=["GET"])
def list_orders():
    """List Government Orders (G.O.s) with versioning and status."""
    db = SessionLocal()
    try:
        dept = request.args.get("department")
        status = request.args.get("status")

        q = db.query(GovernmentOrderLifecycle)
        if dept:
            q = q.filter(GovernmentOrderLifecycle.issuing_department == dept)
        if status:
            q = q.filter(GovernmentOrderLifecycle.status == status)

        orders = q.order_by(GovernmentOrderLifecycle.issue_date.desc()).limit(100).all()
        data = [
            {
                "id": o.id,
                "go_number": o.go_number,
                "department": o.issuing_department,
                "type": o.go_type.value,
                "issue_date": o.issue_date.isoformat(),
                "subject": o.subject_summary,
                "status": o.status.value,
                "supersedes": o.supersedes_go_number,
                "gazette_url": o.full_gazette_url,
                "sha256": o.gazette_pdf_sha256,
            }
            for o in orders
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} government orders")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@governance_advanced_bp.route("/models", methods=["GET"])
def list_models():
    """List ML models in the Model Registry with drift thresholds and guardrails."""
    db = SessionLocal()
    try:
        models = db.query(MLModelRegistry).all()
        data = [
            {
                "id": m.id,
                "identifier": m.model_identifier,
                "name": m.model_name,
                "task": m.task_type.value,
                "version": m.model_version,
                "metric_name": m.primary_metric_name,
                "metric_value": m.primary_metric_value,
                "drift_threshold": m.drift_threshold,
                "is_active": m.is_active_in_production,
                "automated_accusation_permitted": m.automated_accusation_permitted,
            }
            for m in models
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} ML models")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
