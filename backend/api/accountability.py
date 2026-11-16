"""
CIVICLENS TN — Public Accountability API Blueprint (Phase 11.2)
"""
from datetime import datetime, date
from flask import Blueprint, request, jsonify
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.accountability import (
    AccountabilityCase, InstitutionalAttribution, OfficialResponse,
    CorrectiveAction, OutcomeVerification, CaseStatus, CaseSeverity,
    CaseTriggerType, GroundOutcomeStatus, ResponseChannel, ResponseReceiptStatus
)
from backend.services.accountability_service import AccountabilityService

accountability_bp = Blueprint("accountability", __name__, url_prefix="/accountability")


@accountability_bp.route("/cases", methods=["GET"])
def list_cases():
    """List public accountability cases with optional filters."""
    db = SessionLocal()
    try:
        domain = request.args.get("domain")
        district = request.args.get("district")
        status = request.args.get("status")
        severity = request.args.get("severity")

        q = db.query(AccountabilityCase)
        if domain:
            q = q.filter(AccountabilityCase.governance_domain == domain)
        if district:
            q = q.filter(AccountabilityCase.district == district)
        if status:
            q = q.filter(AccountabilityCase.status == status)
        if severity:
            q = q.filter(AccountabilityCase.severity == severity)

        cases = q.order_by(AccountabilityCase.created_at.desc()).limit(100).all()
        data = [
            {
                "id": c.id,
                "case_id": c.case_id,
                "title": c.title,
                "title_ta": c.title_ta,
                "domain": c.governance_domain,
                "district": c.district,
                "trigger_type": c.trigger_type.value,
                "trigger_entity_id": c.trigger_entity_id,
                "status": c.status.value,
                "severity": c.severity.value,
                "financial_implication_cr": c.financial_implication_cr,
                "provenance_hash": c.evidence_provenance_hash,
                "created_at": c.created_at.isoformat() if c.created_at else None,
            }
            for c in cases
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} accountability cases")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@accountability_bp.route("/cases/<case_id>", methods=["GET"])
def get_case(case_id):
    """Get single accountability case with full lifecycle details."""
    db = SessionLocal()
    try:
        case = db.query(AccountabilityCase).filter_by(case_id=case_id).first()
        if not case:
            return error_response(f"Case '{case_id}' not found", status_code=404)

        dossier = AccountabilityService.generate_accountability_dossier(db, case_id)
        return success_response(data=dossier, message="Case retrieved successfully")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@accountability_bp.route("/cases", methods=["POST"])
def create_case():
    """Create a new public accountability case."""
    db = SessionLocal()
    try:
        body = request.get_json() or {}
        case_id = body.get("case_id")
        title = body.get("title")
        description = body.get("description")
        domain = body.get("governance_domain")
        trigger_type = body.get("trigger_type", "BUDGET_DISCREPANCY")
        trigger_entity_id = body.get("trigger_entity_id")

        if not all([case_id, title, description, domain, trigger_entity_id]):
            return error_response("Missing mandatory fields", status_code=400)

        case = AccountabilityService.create_case(
            db=db,
            case_id=case_id,
            title=title,
            description=description,
            governance_domain=domain,
            trigger_type=CaseTriggerType(trigger_type),
            trigger_entity_id=trigger_entity_id,
            title_ta=body.get("title_ta"),
            district=body.get("district"),
            severity=CaseSeverity(body.get("severity", "MEDIUM")),
            financial_implication_cr=body.get("financial_implication_cr"),
        )
        return success_response(
            data={"case_id": case.case_id, "status": case.status.value},
            message="Accountability case created successfully",
            status_code=201
        )
    except ValueError as e:
        return error_response(str(e), status_code=422)
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@accountability_bp.route("/cases/<int:case_id>/attribution", methods=["POST"])
def add_attribution(case_id):
    """Add institutional attribution to a case."""
    db = SessionLocal()
    try:
        body = request.get_json() or {}
        attr = AccountabilityService.add_attribution(
            db=db,
            case_id=case_id,
            department_name=body.get("department_name"),
            directorate_or_agency=body.get("directorate_or_agency"),
            jurisdiction_level=body.get("jurisdiction_level", "STATE"),
            district=body.get("district"),
            taluk=body.get("taluk"),
            designated_authority=body.get("designated_authority"),
            statutory_mandate_reference=body.get("statutory_mandate_reference"),
        )
        return success_response(
            data={"id": attr.id, "department": attr.department_name},
            message="Institutional attribution recorded",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@accountability_bp.route("/cases/<int:case_id>/response", methods=["POST"])
def add_response(case_id):
    """Record official response from authority."""
    db = SessionLocal()
    try:
        body = request.get_json() or {}
        resp = AccountabilityService.record_official_response(
            db=db,
            case_id=case_id,
            response_reference=body.get("response_reference"),
            channel=ResponseChannel(body.get("channel", "GOVERNMENT_ORDER")),
            response_date=date.fromisoformat(body.get("response_date")),
            response_summary=body.get("response_summary"),
            receipt_status=ResponseReceiptStatus(body.get("receipt_status", "FORMAL_REPLY")),
            responding_officer_designation=body.get("responding_officer_designation"),
            document_url=body.get("document_url"),
            document_sha256=body.get("document_sha256"),
        )
        return success_response(
            data={"id": resp.id, "reference": resp.response_reference},
            message="Official response recorded",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@accountability_bp.route("/cases/<int:case_id>/verify", methods=["POST"])
def verify_outcome(case_id):
    """Record independent outcome verification."""
    db = SessionLocal()
    try:
        body = request.get_json() or {}
        ver = AccountabilityService.verify_outcome(
            db=db,
            case_id=case_id,
            verification_method=body.get("verification_method", "PHYSICAL_INSPECTION"),
            verifying_entity=body.get("verifying_entity"),
            verification_date=date.fromisoformat(body.get("verification_date")),
            ground_status=GroundOutcomeStatus(body.get("ground_status")),
            findings_summary=body.get("findings_summary"),
            geo_latitude=body.get("geo_latitude"),
            geo_longitude=body.get("geo_longitude"),
            photo_evidence_sha256=body.get("photo_evidence_sha256"),
        )
        return success_response(
            data={"id": ver.id, "ground_status": ver.ground_status.value},
            message="Independent verification recorded",
            status_code=201
        )
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
