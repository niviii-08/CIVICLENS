"""
CIVICLENS TN — CAG Audit-Observation API Blueprint (Phase 11.4)
"""
from flask import Blueprint, request
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.cag_rti import CAGReport, CAGAuditParagraph, ATRStatus
from backend.services.cag_rti_service import CAGAndRTIService

cag_audit_bp = Blueprint("cag_audit", __name__, url_prefix="/cag-audit")


@cag_audit_bp.route("/reports", methods=["GET"])
def list_reports():
    """List CAG Audit Reports."""
    db = SessionLocal()
    try:
        reports = db.query(CAGReport).order_by(CAGReport.created_at.desc()).all()
        data = [
            {
                "id": r.id,
                "report_code": r.report_code,
                "financial_year": r.financial_year,
                "report_type": r.report_type.value,
                "title": r.title,
                "tabled_date": r.tabled_in_assembly_date.isoformat() if r.tabled_in_assembly_date else None,
                "is_tabled": r.is_tabled,
                "url": r.cag_portal_url,
                "paragraphs_count": len(r.paragraphs) if r.paragraphs else 0,
            }
            for r in reports
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} CAG reports")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@cag_audit_bp.route("/paragraphs", methods=["GET"])
def list_paragraphs():
    """List CAG audit paragraphs with departmental ATR statuses."""
    db = SessionLocal()
    try:
        dept = request.args.get("department")
        atr_status = request.args.get("atr_status")

        q = db.query(CAGAuditParagraph)
        if dept:
            q = q.filter(CAGAuditParagraph.department_name == dept)
        if atr_status:
            q = q.filter(CAGAuditParagraph.atr_status == atr_status)

        paras = q.order_by(CAGAuditParagraph.created_at.desc()).limit(100).all()
        data = [
            {
                "id": p.id,
                "paragraph_ref": p.paragraph_ref,
                "department": p.department_name,
                "scheme_code": p.scheme_code,
                "heading": p.heading,
                "observation": p.audit_observation,
                "financial_implication_cr": p.financial_implication_cr,
                "atr_status": p.atr_status.value,
                "pac_status": p.pac_status.value,
                "reply_summary": p.department_reply_summary,
                "pac_recommendations": p.pac_recommendations,
            }
            for p in paras
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} CAG audit paragraphs")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@cag_audit_bp.route("/summary", methods=["GET"])
def get_summary():
    """Get CAG audit follow-through metrics."""
    db = SessionLocal()
    try:
        summary = CAGAndRTIService.get_cag_audit_summary(db)
        return success_response(data=summary, message="CAG audit summary retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
