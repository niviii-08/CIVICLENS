"""
CIVICLENS TN — Public Procurement & Works API Blueprint (Phase 11.3)
"""
from datetime import date
from flask import Blueprint, request
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.procurement import (
    Tender, TenderBid, ContractAward, ProcurementPublicWork, ProcurementPayment,
    TenderStatus, MilestoneProgressStatus, TenderCategory
)
from backend.services.procurement_service import ProcurementService

procurement_bp = Blueprint("procurement", __name__, url_prefix="/procurement")


@procurement_bp.route("/tenders", methods=["GET"])
def list_tenders():
    """List tenders with optional filtering."""
    db = SessionLocal()
    try:
        dept = request.args.get("department")
        district = request.args.get("district")
        status = request.args.get("status")

        q = db.query(Tender)
        if dept:
            q = q.filter(Tender.issuing_department == dept)
        if district:
            q = q.filter(Tender.district == district)
        if status:
            q = q.filter(Tender.status == status)

        tenders = q.order_by(Tender.published_date.desc()).limit(100).all()
        data = [
            {
                "id": t.id,
                "tender_id": t.tender_id,
                "department": t.issuing_department,
                "title": t.title,
                "title_ta": t.title_ta,
                "category": t.category.value,
                "estimated_cost_cr": t.estimated_cost_cr,
                "published_date": t.published_date.isoformat(),
                "deadline": t.submission_deadline.isoformat(),
                "district": t.district,
                "status": t.status.value,
                "source_url": t.source_url,
                "bids_count": len(t.bids) if t.bids else 0,
                "is_awarded": t.award is not None,
            }
            for t in tenders
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} tenders")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@procurement_bp.route("/tenders/<tender_id>", methods=["GET"])
def get_tender(tender_id):
    """Get single tender details with bids and award."""
    db = SessionLocal()
    try:
        t = db.query(Tender).filter_by(tender_id=tender_id).first()
        if not t:
            return error_response(f"Tender '{tender_id}' not found", status_code=404)

        data = {
            "tender_id": t.tender_id,
            "department": t.issuing_department,
            "procuring_entity": t.procuring_entity,
            "title": t.title,
            "title_ta": t.title_ta,
            "category": t.category.value,
            "estimated_cost_cr": t.estimated_cost_cr,
            "published_date": t.published_date.isoformat(),
            "deadline": t.submission_deadline.isoformat(),
            "status": t.status.value,
            "district": t.district,
            "bids": [
                {
                    "bidder": b.bidder_name,
                    "amount_cr": b.bid_amount_cr,
                    "is_l1": b.is_l1_lowest,
                    "qualified": b.is_technically_qualified,
                }
                for b in t.bids
            ],
            "award": {
                "contract_ref": t.award.contract_reference,
                "contractor": t.award.contractor_name,
                "awarded_cr": t.award.awarded_amount_cr,
                "variance_pct": t.award.variance_from_estimate_pct,
                "award_date": t.award.award_date.isoformat(),
            } if t.award else None,
        }
        return success_response(data=data, message="Tender retrieved successfully")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@procurement_bp.route("/works", methods=["GET"])
def list_works():
    """List public works infrastructure projects."""
    db = SessionLocal()
    try:
        district = request.args.get("district")
        status = request.args.get("status")

        q = db.query(ProcurementPublicWork)
        if district:
            q = q.filter(ProcurementPublicWork.district == district)
        if status:
            q = q.filter(ProcurementPublicWork.milestone_status == status)

        works = q.order_by(ProcurementPublicWork.created_at.desc()).limit(100).all()
        data = [
            {
                "id": w.id,
                "work_id": w.work_id,
                "title": w.title,
                "title_ta": w.title_ta,
                "district": w.district,
                "local_body": w.local_body,
                "budget_cr": w.sanctioned_budget_cr,
                "spent_cr": w.cumulative_expenditure_cr,
                "progress_pct": w.physical_progress_pct,
                "status": w.milestone_status.value,
                "inspection_status": w.inspection_status.value,
                "target_date": w.target_completion_date.isoformat(),
                "actual_date": w.actual_completion_date.isoformat() if w.actual_completion_date else None,
            }
            for w in works
        ]
        return success_response(data=data, message=f"Retrieved {len(data)} public works")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@procurement_bp.route("/summary", methods=["GET"])
def get_summary():
    """Get procurement summary statistics."""
    db = SessionLocal()
    try:
        district = request.args.get("district")
        summary = ProcurementService.get_procurement_summary(db, district=district)
        return success_response(data=summary, message="Procurement summary retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
