"""
Unit Tests for Phase 11.3 — Procurement & Works Intelligence
"""
import pytest
from datetime import date
from backend.models.procurement import (
    Tender, TenderBid, ContractAward, ProcurementPublicWork, ProcurementPayment,
    TenderStatus, MilestoneProgressStatus, InspectionStatus, TenderCategory
)
from backend.services.procurement_service import ProcurementService


def test_tender_creation_and_bid_evaluation(db_session):
    """Verify tender publication and L1 lowest bid identification."""
    tender = ProcurementService.create_tender(
        db=db_session,
        tender_id="TEST-TENDER-2024-001",
        issuing_department="School Education Department",
        procuring_entity="Directorate of School Education",
        title="Procurement of Laboratory Equipment",
        estimated_cost_cr=10.0,
        published_date=date(2024, 1, 15),
        submission_deadline=date(2024, 2, 15),
        district="Salem",
        category=TenderCategory.GOODS,
    )
    assert tender.id is not None
    assert tender.status == TenderStatus.PUBLISHED

    # Record Bids
    b1 = ProcurementService.record_bid(
        db=db_session,
        tender_id=tender.id,
        bidder_name="Scientific Supplies Corp",
        bid_amount_cr=9.4,
        is_l1_lowest=True,
    )
    b2 = ProcurementService.record_bid(
        db=db_session,
        tender_id=tender.id,
        bidder_name="Southern Lab Equipments",
        bid_amount_cr=9.8,
        is_l1_lowest=False,
    )
    assert b1.is_l1_lowest is True
    assert len(tender.bids) == 2


def test_contract_award_and_variance_calculation(db_session):
    """Verify contract award calculates percentage variance against estimated tender cost."""
    tender = ProcurementService.create_tender(
        db=db_session,
        tender_id="TEST-TENDER-2024-002",
        issuing_department="Public Works Department",
        procuring_entity="PWD Buildings Wing",
        title="Construction of Additional Classrooms",
        estimated_cost_cr=5.0,
        published_date=date(2024, 3, 1),
        submission_deadline=date(2024, 3, 30),
    )
    award = ProcurementService.record_award(
        db=db_session,
        tender_id=tender.id,
        contract_reference="PWD/BW/2024/CA-12",
        contractor_name="Kovai Builders Pvt Ltd",
        awarded_amount_cr=4.75,
        award_date=date(2024, 4, 15),
    )
    assert award.awarded_amount_cr == 4.75
    assert award.variance_from_estimate_pct == -5.0  # (4.75 - 5.0) / 5.0 * 100 = -5.0%
    assert tender.status == TenderStatus.AWARDED


def test_public_work_tracking_and_payment_disbursement(db_session):
    """Verify public work tracking, tranche payments, and cumulative expenditure updates."""
    work = ProcurementService.create_public_work(
        db=db_session,
        work_id="TEST-WORK-2024-01",
        title="Salem Primary Health Center Renovation",
        district="Salem",
        sanctioned_budget_cr=2.5,
        target_completion_date=date(2024, 12, 31),
    )
    assert work.cumulative_expenditure_cr == 0.0

    # Pay Tranche 1
    p1 = ProcurementService.record_payment(
        db=db_session,
        work_id=work.id,
        tranche_number=1,
        amount_paid_cr=1.0,
        payment_date=date(2024, 6, 1),
        treasury_voucher_number="VOUCH-001",
        milestone_verified="Demolition and roofing complete",
    )
    assert work.cumulative_expenditure_cr == 1.0

    # Pay Tranche 2
    p2 = ProcurementService.record_payment(
        db=db_session,
        work_id=work.id,
        tranche_number=2,
        amount_paid_cr=0.8,
        payment_date=date(2024, 9, 1),
        treasury_voucher_number="VOUCH-002",
        milestone_verified="Electrical and plumbing complete",
    )
    assert work.cumulative_expenditure_cr == 1.8


def test_procurement_summary_metrics(db_session):
    """Verify procurement summary statistics aggregation."""
    summary = ProcurementService.get_procurement_summary(db_session)
    assert "total_tenders_tracked" in summary
    assert "total_public_works_tracked" in summary
    assert "completion_rate_pct" in summary
