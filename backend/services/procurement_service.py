"""
CIVICLENS TN — Public Procurement & Works Intelligence Service (Phase 11.3)

Provides analytics and monitoring across the public infrastructure procurement pipeline:
Tender -> Bidding -> Contract Award -> Public Work -> Payment Tranches -> Physical Inspections.
"""
from datetime import datetime, timezone, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.procurement import (
    Tender, TenderBid, ContractAward, ProcurementPublicWork, ProcurementPayment,
    TenderStatus, MilestoneProgressStatus, InspectionStatus, TenderCategory
)


class ProcurementService:
    """Core domain service for public procurement and works intelligence."""

    @staticmethod
    def create_tender(
        db: Session,
        tender_id: str,
        issuing_department: str,
        procuring_entity: str,
        title: str,
        estimated_cost_cr: float,
        published_date: date,
        submission_deadline: date,
        district: Optional[str] = None,
        canonical_scheme_code: Optional[str] = None,
        title_ta: Optional[str] = None,
        category: TenderCategory = TenderCategory.CIVIL_WORKS,
        source_url: Optional[str] = None,
        tender_notice_sha256: Optional[str] = None,
    ) -> Tender:
        """Create and publish a tracked government tender."""
        tender = Tender(
            tender_id=tender_id,
            canonical_scheme_code=canonical_scheme_code,
            issuing_department=issuing_department,
            procuring_entity=procuring_entity,
            title=title,
            title_ta=title_ta,
            category=category,
            estimated_cost_cr=estimated_cost_cr,
            published_date=published_date,
            submission_deadline=submission_deadline,
            district=district,
            status=TenderStatus.PUBLISHED,
            source_url=source_url,
            tender_notice_sha256=tender_notice_sha256,
        )
        db.add(tender)
        db.commit()
        db.refresh(tender)
        return tender

    @staticmethod
    def record_bid(
        db: Session,
        tender_id: int,
        bidder_name: str,
        bid_amount_cr: float,
        technical_score: Optional[float] = None,
        is_technically_qualified: bool = True,
        is_l1_lowest: bool = False,
    ) -> TenderBid:
        """Record a contractor bid for an open tender."""
        bid = TenderBid(
            tender_id=tender_id,
            bidder_name=bidder_name,
            bid_amount_cr=bid_amount_cr,
            technical_score=technical_score,
            is_technically_qualified=is_technically_qualified,
            is_l1_lowest=is_l1_lowest,
        )
        db.add(bid)
        db.commit()
        db.refresh(bid)
        return bid

    @staticmethod
    def record_award(
        db: Session,
        tender_id: int,
        contract_reference: str,
        contractor_name: str,
        awarded_amount_cr: float,
        award_date: date,
        stipulated_duration_months: int = 12,
        contractor_pan_masked: Optional[str] = None,
        work_order_reference: Optional[str] = None,
    ) -> ContractAward:
        """Record formal contract award and update tender status."""
        tender = db.query(Tender).filter_by(id=tender_id).first()
        if not tender:
            raise ValueError(f"Tender {tender_id} not found.")

        variance_pct = round(((awarded_amount_cr - tender.estimated_cost_cr) / tender.estimated_cost_cr) * 100, 2)

        award = ContractAward(
            tender_id=tender.id,
            contract_reference=contract_reference,
            contractor_name=contractor_name,
            contractor_pan_masked=contractor_pan_masked,
            awarded_amount_cr=awarded_amount_cr,
            variance_from_estimate_pct=variance_pct,
            award_date=award_date,
            stipulated_duration_months=stipulated_duration_months,
            work_order_reference=work_order_reference,
        )
        tender.status = TenderStatus.AWARDED
        tender.award_date = award_date

        db.add(award)
        db.commit()
        db.refresh(award)
        return award

    @staticmethod
    def create_public_work(
        db: Session,
        work_id: str,
        title: str,
        district: str,
        sanctioned_budget_cr: float,
        target_completion_date: date,
        tender_id: Optional[int] = None,
        title_ta: Optional[str] = None,
        local_body: Optional[str] = None,
        constituency_name: Optional[str] = None,
    ) -> ProcurementPublicWork:
        """Create a tracked public work infrastructure project."""
        work = ProcurementPublicWork(
            work_id=work_id,
            tender_id=tender_id,
            title=title,
            title_ta=title_ta,
            district=district,
            local_body=local_body,
            constituency_name=constituency_name,
            sanctioned_budget_cr=sanctioned_budget_cr,
            target_completion_date=target_completion_date,
            milestone_status=MilestoneProgressStatus.NOT_STARTED,
        )
        db.add(work)
        db.commit()
        db.refresh(work)
        return work

    @staticmethod
    def record_payment(
        db: Session,
        work_id: int,
        tranche_number: int,
        amount_paid_cr: float,
        payment_date: date,
        treasury_voucher_number: str,
        milestone_verified: Optional[str] = None,
    ) -> ProcurementPayment:
        """Record public payment voucher and update cumulative spend."""
        work = db.query(ProcurementPublicWork).filter_by(id=work_id).first()
        if not work:
            raise ValueError(f"ProcurementPublicWork {work_id} not found.")

        payment = ProcurementPayment(
            work_id=work.id,
            tranche_number=tranche_number,
            amount_paid_cr=amount_paid_cr,
            payment_date=payment_date,
            treasury_voucher_number=treasury_voucher_number,
            milestone_verified=milestone_verified,
        )
        work.cumulative_expenditure_cr = round((work.cumulative_expenditure_cr or 0.0) + amount_paid_cr, 4)
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    @staticmethod
    def get_procurement_summary(db: Session, district: Optional[str] = None) -> Dict[str, Any]:
        """Aggregate statistical metrics of tenders and public works."""
        tender_q = db.query(Tender)
        work_q = db.query(ProcurementPublicWork)

        if district:
            tender_q = tender_q.filter(Tender.district == district)
            work_q = work_q.filter(ProcurementPublicWork.district == district)

        total_tenders = tender_q.count()
        total_awarded = tender_q.filter(Tender.status == TenderStatus.AWARDED).count()
        total_estimated_cr = db.query(func.sum(Tender.estimated_cost_cr)).scalar() or 0.0

        total_works = work_q.count()
        completed_works = work_q.filter(ProcurementPublicWork.milestone_status == MilestoneProgressStatus.PHYSICALLY_COMPLETED).count()
        total_spent_cr = db.query(func.sum(ProcurementPublicWork.cumulative_expenditure_cr)).scalar() or 0.0

        return {
            "total_tenders_tracked": total_tenders,
            "tenders_awarded": total_awarded,
            "total_tender_value_cr": round(total_estimated_cr, 2),
            "total_public_works_tracked": total_works,
            "physically_completed_works": completed_works,
            "cumulative_disbursed_cr": round(total_spent_cr, 2),
            "completion_rate_pct": round((completed_works / total_works * 100), 2) if total_works > 0 else 0.0,
        }
