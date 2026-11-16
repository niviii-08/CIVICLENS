"""
CIVICLENS TN — RTI Intelligence API Blueprint (Phase 11.5)
"""
from flask import Blueprint, request
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.cag_rti import RTIRequest, RTIResponse, TNICSecondAppeal, RTIDecision
from backend.services.cag_rti_service import CAGAndRTIService

rti_bp = Blueprint("rti", __name__, url_prefix="/rti")


@rti_bp.route("/requests", methods=["GET"])
def list_requests():
    """List RTI applications and compliance SLA metrics."""
    db = SessionLocal()
    try:
        dept = request.args.get("department")
        status = request.args.get("status")

        q = db.query(RTIRequest)
        if dept:
            q = q.filter(RTIRequest.department_name == dept)
        if status:
            q = q.filter(RTIRequest.status == status)

        requests_list = q.order_by(RTIRequest.filing_date.desc()).limit(100).all()
        data = [
            {
                "id": r.id,
                "registration_number": r.registration_number,
                "public_authority": r.public_authority,
                "department": r.department_name,
                "filing_date": r.filing_date.isoformat(),
                "subject": r.subject_matter,
                "status": r.status.value,
                "response": {
                    "date": r.response.response_date.isoformat(),
                    "turnaround_days": r.response.turnaround_days,
                    "sla_breached": r.response.statutory_sla_breached,
                    "decision": r.response.decision.value,
                    "exemptions_cited": r.response.exemptions_cited,
                    "summary": r.response.disclosed_information_summary,
                } if r.response else None,
            }
            for r in requests_list
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} RTI requests")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@rti_bp.route("/appeals", methods=["GET"])
def list_appeals():
    """List TNIC second appeal decisions."""
    db = SessionLocal()
    try:
        appeals = db.query(TNICSecondAppeal).order_by(TNICSecondAppeal.hearing_date.desc()).all()
        data = [
            {
                "id": a.id,
                "case_number": a.appeal_case_number,
                "hearing_date": a.hearing_date.isoformat(),
                "commissioner": a.commissioner_name,
                "order_type": a.order_type.value,
                "penalty_inr": a.penalty_amount_inr,
                "summary": a.order_summary,
            }
            for a in appeals
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} TNIC appeals")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
