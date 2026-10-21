"""

Civic issue intelligence and grievance tracking REST API router.

Provides endpoints for searching civic issues, viewing department performance,

tracking resolution evidence, and monitoring recurring complaint hotspots.

"""

from __future__ import annotations

import logging

import uuid

from datetime import datetime, timezone

from collections import defaultdict
from typing import Any, Dict, List, Optional

from flask import Blueprint, request

from sqlalchemy import desc, func, or_

from sqlalchemy.orm import Session

from backend.api.responses import error_response, success_response

from backend.database.session import SessionLocal

from backend.models.civic_issue import (

    AdministrativeArea,

    CivicCrossPhaseLink,

    CivicDepartment,

    CivicIssue,

    CivicIssueSeverity,

    CivicIssueStatus,

    DataQualityIssue,

    GrievanceRecord,

    IssueCategory,

    IssueCategoryEnum,

    IssueEvent,

    IssueMetric,

    PublicWork,

    ResolutionEvidence,

    ResponseRecord,

    ServiceStandard,

    SourceDocument,

    CivicReviewAudit,

    EvidenceAssessmentEnum,

    ResolutionVerificationStatus,

    sanitize_pii,

)

from backend.services.civic_analytics_service import CivicAnalyticsEngine

logger = logging.getLogger(__name__)

civic_bp = Blueprint("civic", __name__, url_prefix="/civic")

def resolve_civic_cross_phase_entities(db: Session, links: List[CivicCrossPhaseLink]) -> List[Dict[str, Any]]:

    """

    Resolves linked entities from Phases 1-7 via stable identifiers

    without copying datasets across databases.

    """

    resolved_links: List[Dict[str, Any]] = []

    for link in links:

        link_dict = link.to_dict()

        entity_payload: Optional[Dict[str, Any]] = None

        try:

            if link.target_phase == "PHASE_1_2_BUDGET_SCHEME" or link.entity_type in {"HISTORICAL_SCHEME", "BUDGET_SCHEME"}:

                if link.entity_type == "HISTORICAL_SCHEME":

                    from backend.models.budget import HistoricalScheme

                    scheme_id = int(link.entity_id) if str(link.entity_id).isdigit() else link.entity_id

                    hs = db.query(HistoricalScheme).filter(HistoricalScheme.id == scheme_id).first()

                    if hs:

                        entity_payload = {

                            "id": hs.id,

                            "scheme_name": hs.scheme_name,

                            "financial_year": hs.financial_year,

                            "department": hs.department.name if hs.department else None,

                            "objectives": hs.objectives,

                        }

                elif link.entity_type == "BUDGET_SCHEME":

                    from backend.models.budget import BudgetScheme

                    scheme_id = int(link.entity_id) if str(link.entity_id).isdigit() else link.entity_id

                    bs = db.query(BudgetScheme).filter(BudgetScheme.id == scheme_id).first()

                    if bs:

                        entity_payload = {

                            "id": bs.id,

                            "name": bs.name,

                            "department_id": bs.department_id,

                        }

            elif link.target_phase == "PHASE_3_PROMISE" or link.entity_type == "POLITICAL_PROMISE":

                from backend.models.promise import PoliticalPromise

                p = db.query(PoliticalPromise).filter(PoliticalPromise.promise_id == link.entity_id).first()

                if p:

                    entity_payload = {

                        "promise_id": p.promise_id,

                        "original_text": p.original_text,

                        "classification": p.classification,

                        "manifesto_id": p.manifesto_id,

                    }

            elif link.target_phase == "PHASE_4_NEWS" or link.entity_type in {"NEWS_ARTICLE", "ARTICLE"}:

                from backend.models.news import Article

                art = db.query(Article).filter(Article.article_id == link.entity_id).first()

                if art:

                    entity_payload = {

                        "article_id": art.article_id,

                        "title": art.title,

                        "url": art.url,

                        "source_name": art.source.source_name if art.source else None,

                        "publication_date": art.publication_date.isoformat() if art.publication_date else None,

                    }

            elif link.target_phase == "PHASE_5_FUNDING" or link.entity_type == "FINANCIAL_DOCUMENT":

                from backend.models.funding import FinancialDocument

                fd = db.query(FinancialDocument).filter(FinancialDocument.document_id == link.entity_id).first()

                if fd:

                    entity_payload = {

                        "document_id": fd.document_id,

                        "financial_year": fd.financial_year,

                        "filing_type": fd.filing_type,

                        "source_url": fd.source_url,

                    }

            elif link.target_phase in {"PHASE_6_REPRESENTATIVE", "PHASE_6_CONSTITUENCY"} or link.entity_type in {"REPRESENTATIVE", "CONSTITUENCY"}:

                if link.entity_type == "REPRESENTATIVE":

                    from backend.models.representative import Representative

                    rep = db.query(Representative).filter(Representative.representative_id == link.entity_id).first()

                    if rep:

                        entity_payload = {

                            "representative_id": rep.representative_id,

                            "official_name": rep.official_name,

                            "representative_type": rep.representative_type,

                            "party_id": rep.party_id,

                            "constituency_id": rep.constituency_id,

                        }

                elif link.entity_type == "CONSTITUENCY":

                    from backend.models.representative import Constituency

                    con = db.query(Constituency).filter(Constituency.constituency_id == link.entity_id).first()

                    if con:

                        entity_payload = {

                            "constituency_id": con.constituency_id,

                            "official_name": getattr(con, "official_name", None) or getattr(con, "name", None),

                            "constituency_type": con.constituency_type.value if hasattr(con.constituency_type, "value") else str(con.constituency_type),

                            "district": getattr(con, "district", None),

                        }

            elif link.target_phase == "PHASE_7_CLAIM" or link.entity_type == "CLAIM":

                from backend.models.claim import Claim

                cl = db.query(Claim).filter(Claim.claim_id == link.entity_id).first()

                if cl:

                    claim_cat = getattr(cl, "claim_category", None) or getattr(cl, "category", None)

                    entity_payload = {

                        "claim_id": cl.claim_id,

                        "canonical_text": getattr(cl, "original_text", None) or getattr(cl, "canonical_text", ""),

                        "category": claim_cat.value if hasattr(claim_cat, "value") else str(claim_cat),

                        "status": cl.status.value if hasattr(cl.status, "value") else str(cl.status),

                    }

        except Exception as e:

            logger.warning(f"Could not resolve cross-phase link {link.entity_type}:{link.entity_id}: {e}")

            entity_payload = None

        link_dict["resolved_entity"] = entity_payload

        resolved_links.append(link_dict)

    return resolved_links

@civic_bp.route("/issues", methods=["GET"])

def search_civic_issues():

    """

    Searches and filters civic issues across categories, areas, departments,

    statuses, and date intervals with pagination.

    """

    db: Session = SessionLocal()

    try:

        query = db.query(CivicIssue)

        q_text = request.args.get("q")

        if q_text and q_text.strip():

            term = f"%{q_text.strip()}%"

            query = query.filter(

                or_(

                    CivicIssue.title.ilike(term),

                    CivicIssue.description.ilike(term),

                    CivicIssue.title_ta.ilike(term),

                    CivicIssue.issue_code.ilike(term),

                )

            )

        category_param = request.args.get("category")

        if category_param:

            cat_obj = db.query(IssueCategory).filter(

                or_(

                    IssueCategory.code == category_param.lower(),

                    IssueCategory.name_en.ilike(category_param),

                )

            ).first()

            if cat_obj:

                query = query.filter(CivicIssue.category_id == cat_obj.id)

        area_param = request.args.get("area_id")

        if area_param:

            area_obj = db.query(AdministrativeArea).filter(

                or_(

                    AdministrativeArea.area_code == area_param,

                    AdministrativeArea.name_en.ilike(area_param),

                    AdministrativeArea.id == int(area_param) if area_param.isdigit() else False,

                )

            ).first()

            if area_obj:

                query = query.filter(CivicIssue.administrative_area_id == area_obj.id)

        dept_param = request.args.get("department_id")

        if dept_param:

            dept_obj = db.query(CivicDepartment).filter(

                or_(

                    CivicDepartment.code == dept_param,

                    CivicDepartment.name_en.ilike(dept_param),

                    CivicDepartment.id == int(dept_param) if dept_param.isdigit() else False,

                )

            ).first()

            if dept_obj:

                query = query.filter(CivicIssue.department_id == dept_obj.id)

        status_param = request.args.get("status")

        if status_param:

            try:

                status_enum = CivicIssueStatus(status_param.upper())

                query = query.filter(CivicIssue.status == status_enum)

            except ValueError:

                pass

        severity_param = request.args.get("severity")

        if severity_param:

            try:

                severity_enum = CivicIssueSeverity(severity_param.upper())

                query = query.filter(CivicIssue.severity == severity_enum)

            except ValueError:

                pass

        is_recurring = request.args.get("is_recurring")

        if is_recurring is not None:

            if is_recurring.lower() in {"true", "1"}:

                query = query.filter(CivicIssue.repeat_count > 1)

            elif is_recurring.lower() in {"false", "0"}:

                query = query.filter(CivicIssue.repeat_count <= 1)

        start_date = request.args.get("start_date")

        if start_date:

            try:

                s_dt = datetime.fromisoformat(start_date.replace("Z", "+00:00"))

                query = query.filter(CivicIssue.reported_date >= s_dt)

            except Exception:

                pass

        end_date = request.args.get("end_date")

        if end_date:

            try:

                e_dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))

                query = query.filter(CivicIssue.reported_date <= e_dt)

            except Exception:

                pass

        total_count = query.count()

        page = max(1, request.args.get("page", 1, type=int))

        per_page = min(100, max(1, request.args.get("per_page", 20, type=int)))

        offset = (page - 1) * per_page

        issues = query.order_by(desc(CivicIssue.reported_date)).offset(offset).limit(per_page).all()

        results = [issue.to_dict() for issue in issues]

        total_pages = (total_count + per_page - 1) // per_page if total_count > 0 else 1

        return success_response(

            data={

                "issues": results,

                "pagination": {

                    "page": page,

                    "per_page": per_page,

                    "total": total_count,

                    "total_pages": total_pages,

                },

            },

            message="Civic issues retrieved successfully.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>", methods=["GET"])

def get_civic_issue_details(issue_id: str):

    """

    Retrieves full details of a specific civic issue, including category,

    department, administrative area, SLA standards, public works, metrics,

    and cross-phase links.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        data = issue.to_dict()

        data["category"] = issue.category.to_dict() if issue.category else None

        data["department"] = issue.department.to_dict() if issue.department else None

        data["administrative_area"] = issue.administrative_area.to_dict() if issue.administrative_area else None

        sla = None

        if issue.department_id and issue.category_id:

            std = (

                db.query(ServiceStandard)

                .filter(

                    ServiceStandard.department_id == issue.department_id,

                    ServiceStandard.category_id == issue.category_id,

                )

                .first()

            )

            if std:

                sla = std.to_dict()

        data["service_standard"] = sla

        data["responses_count"] = len(issue.responses) if issue.responses else 0

        data["grievance_records_count"] = len(issue.grievance_records) if issue.grievance_records else 0

        data["public_works_count"] = len(issue.public_works) if issue.public_works else 0

        data["public_works"] = [pw.to_dict() for pw in issue.public_works] if issue.public_works else []

        data["quality_issues"] = [qi.to_dict() for qi in issue.quality_issues] if issue.quality_issues else []

        cross_links = resolve_civic_cross_phase_entities(db, issue.cross_phase_links or [])

        data["cross_phase_links"] = cross_links

        return success_response(data=data, message="Civic issue details retrieved.")

    finally:

        db.close()

@civic_bp.route("/categories", methods=["GET"])

def get_issue_categories():

    """

    Returns all canonical civic issue categories with descriptions,

    default department routing, priority weights, and active issue counts.

    """

    db: Session = SessionLocal()

    try:

        categories = db.query(IssueCategory).order_by(IssueCategory.name_en).all()

        # Batch query counts and service standards to resolve N+1 bottleneck
        counts_by_cat = dict(
            db.query(CivicIssue.category_id, func.count(CivicIssue.id))
            .group_by(CivicIssue.category_id)
            .all()
        )

        all_standards = db.query(ServiceStandard).all()
        standards_by_cat = defaultdict(list)
        for s in all_standards:
            standards_by_cat[s.category_id].append(s.to_dict())

        results = []
        for cat in categories:
            cat_dict = cat.to_dict()
            cat_dict["active_issues_count"] = counts_by_cat.get(cat.id, 0)
            cat_dict["service_standards"] = standards_by_cat.get(cat.id, [])
            results.append(cat_dict)

        return success_response(data={"categories": results}, message="Civic issue categories retrieved.")

    finally:

        db.close()

@civic_bp.route("/areas", methods=["GET"])

def get_administrative_areas():

    """

    Returns administrative jurisdictions in Tamil Nadu with population context,

    LGD codes, and active issue counts.

    """

    db: Session = SessionLocal()

    try:

        query = db.query(AdministrativeArea)

        level = request.args.get("level")

        if level:

            query = query.filter(AdministrativeArea.administrative_level == level.upper())

        parent_id = request.args.get("parent_id")

        if parent_id and parent_id.isdigit():

            query = query.filter(AdministrativeArea.parent_id == int(parent_id))

        q_name = request.args.get("q")

        if q_name and q_name.strip():

            term = f"%{q_name.strip()}%"

            query = query.filter(

                or_(

                    AdministrativeArea.name_en.ilike(term),

                    AdministrativeArea.name_ta.ilike(term),

                    AdministrativeArea.area_code.ilike(term),

                )

            )

        areas = query.order_by(AdministrativeArea.name_en).all()

        # Batch query issue counts across all administrative areas to resolve N+1 bottleneck
        counts_by_area = dict(
            db.query(CivicIssue.administrative_area_id, func.count(CivicIssue.id))
            .group_by(CivicIssue.administrative_area_id)
            .all()
        )

        results = []
        for area in areas:
            area_dict = area.to_dict()
            area_dict["active_issues_count"] = counts_by_area.get(area.id, 0)
            results.append(area_dict)

        return success_response(data={"areas": results}, message="Administrative areas retrieved.")

    finally:

        db.close()

@civic_bp.route("/departments", methods=["GET"])

def get_civic_departments():

    """

    Returns departments and local body directorates with assigned issue counts

    and contact details.

    """

    db: Session = SessionLocal()

    try:

        departments = db.query(CivicDepartment).order_by(CivicDepartment.name_en).all()

        # Batch query assigned issues across all departments to resolve N+1 bottleneck
        counts_by_dept = dict(
            db.query(CivicIssue.department_id, func.count(CivicIssue.id))
            .group_by(CivicIssue.department_id)
            .all()
        )

        results = []
        for dept in departments:
            dept_dict = dept.to_dict()
            dept_dict["total_assigned_issues"] = counts_by_dept.get(dept.id, 0)
            results.append(dept_dict)

        return success_response(data={"departments": results}, message="Civic departments retrieved.")

    finally:

        db.close()

@civic_bp.route("/departments/<dept_id>/summary", methods=["GET"])

def get_department_performance_summary(dept_id: str):

    """

    Returns a detailed performance summary for a specific department:

    total dockets, open, under review, marked resolved, verified resolved,

    SLA compliance rate, and statutory turnaround limits.

    """

    db: Session = SessionLocal()

    try:

        dept = None

        if dept_id.isdigit():

            dept = db.query(CivicDepartment).filter(CivicDepartment.id == int(dept_id)).first()

        if not dept:

            dept = db.query(CivicDepartment).filter(CivicDepartment.code == dept_id).first()

        if not dept:

            return error_response(message=f"Department '{dept_id}' not found.", status_code=404)

        issues = db.query(CivicIssue).filter(CivicIssue.department_id == dept.id).all()

        total_issues = len(issues)

        open_count = sum(1 for i in issues if i.status == CivicIssueStatus.OPEN)

        under_review_count = sum(1 for i in issues if i.status == CivicIssueStatus.IN_PROGRESS)

        marked_resolved_count = sum(1 for i in issues if i.status == CivicIssueStatus.RESOLVED)

        disputed_count = sum(1 for i in issues if i.status == CivicIssueStatus.DISPUTED)

        resolved_issues = [i for i in issues if i.actual_resolution_date and i.reported_date]

        resolution_days = [(i.actual_resolution_date - i.reported_date).total_seconds() / 86400.0 for i in resolved_issues]

        avg_res_days = round(sum(resolution_days) / len(resolution_days), 2) if resolution_days else None

        responses = db.query(ResponseRecord).filter(ResponseRecord.department_id == dept.id).all()

        total_resp = len(responses)

        breached_resp = sum(1 for r in responses if r.is_sla_breached)

        sla_compliance_rate = round(((total_resp - breached_resp) / total_resp) * 100, 2) if total_resp > 0 else 100.0

        summary = {

            "department": dept.to_dict(),

            "total_assigned_issues": total_issues,

            "status_breakdown": {

                "open": open_count,

                "under_review": under_review_count,

                "marked_resolved": marked_resolved_count,

                "disputed": disputed_count,

            },

            "average_resolution_days": avg_res_days,

            "sla_compliance_percentage": sla_compliance_rate,

            "total_responses_logged": total_resp,

            "sla_breaches_count": breached_resp,

            "service_standards": [s.to_dict() for s in dept.service_standards],

        }

        return success_response(data=summary, message=f"Department summary for '{dept.name_en}' retrieved.")

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/responses", methods=["GET"])

def get_issue_response_history(issue_id: str):

    """

    Returns the complete chronological response history, action-taken reports,

    and state transitions for a specific issue.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        responses = (

            db.query(ResponseRecord)

            .filter(ResponseRecord.civic_issue_id == issue.id)

            .order_by(ResponseRecord.action_taken_date.asc())

            .all()

        )

        events = (

            db.query(IssueEvent)

            .filter(IssueEvent.civic_issue_id == issue.id)

            .order_by(IssueEvent.event_timestamp.asc())

            .all()

        )

        return success_response(

            data={

                "issue_id": issue.id,

                "issue_code": issue.issue_code,

                "responses": [r.to_dict() for r in responses],

                "events": [e.to_dict() for e in events],

            },

            message="Response history retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/evidence", methods=["GET"])

def get_issue_resolution_evidence(issue_id: str):

    """

    Returns empirical evidence artifacts supporting or refuting resolution claims

    (e.g., work orders, completion certificates, site verification).

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        response_ids = [r.id for r in issue.responses] if issue.responses else []

        evidences = []

        if response_ids:

            evidences = db.query(ResolutionEvidence).filter(ResolutionEvidence.response_id.in_(response_ids)).all()

        return success_response(

            data={

                "issue_id": issue.id,

                "issue_code": issue.issue_code,

                "resolution_verification_status": issue.resolution_verification_status.value,

                "evidence_count": len(evidences),

                "evidences": [e.to_dict() for e in evidences],

            },

            message="Resolution evidence retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/clusters", methods=["GET"])

def get_recurring_clusters():

    """

    Identifies and returns recurring issue hotspots aggregated by administrative

    area and category.

    """

    db: Session = SessionLocal()

    try:

        engine = CivicAnalyticsEngine(default_source="VALIDATED_CIVIC_RECORDS")

        issues = db.query(CivicIssue).order_by(CivicIssue.id.desc()).limit(5000).all()

        clusters_metric = engine.calculate_recurring_clusters(issues, period="ALL_TIME")

        return success_response(

            data={

                "recurring_records_count": clusters_metric.distribution.get("recurring_records_count", 0),

                "recurrence_rate_pct": clusters_metric.distribution.get("recurrence_rate_pct", 0.0),

                "hotspot_clusters_count": clusters_metric.distribution.get("hotspot_clusters_count", 0),

                "top_hotspots": clusters_metric.distribution.get("top_hotspots", {}),

                "caveats": clusters_metric.caveats,

            },

            message="Recurring issue clusters retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/analytics/trends", methods=["GET"])

def get_civic_trend_analytics():

    """

    Executes the CivicAnalyticsEngine across validated records, providing

    time-series aggregations, category counts, turnaround times, and guarded

    statistical anomaly detection.

    """

    db: Session = SessionLocal()

    try:

        period = request.args.get("period", "ALL_TIME")

        data_source = request.args.get("data_source", "VALIDATED_CIVIC_RECORDS")

        areas = db.query(AdministrativeArea).all()

        pop_map = {a.area_code: a.population for a in areas if a.population}

        issues = db.query(CivicIssue).order_by(CivicIssue.id.desc()).limit(5000).all()

        engine = CivicAnalyticsEngine(default_source=data_source)

        report = engine.generate_comprehensive_report(

            records=issues,

            period=period,

            data_source=data_source,

            population_map=pop_map,

        )

        metrics_dict = {k: v.__dict__ for k, v in report.metrics.items()}

        anomaly_dict = report.anomaly_detection.__dict__ if report.anomaly_detection else None

        return success_response(

            data={

                "reporting_period": report.reporting_period,

                "data_source": report.data_source,

                "total_records": report.total_records,

                "metrics": metrics_dict,

                "anomaly_detection": anomaly_dict,

                "general_disclaimer": report.general_disclaimer,

            },

            message="Civic trend analytics computed successfully.",

        )

    finally:

        db.close()

@civic_bp.route("/source-documents", methods=["GET"])

def get_source_documents():

    """

    Returns official gazettes, government orders, and portal report documents

    with SHA256 checksums and source tiers.

    """

    db: Session = SessionLocal()

    try:

        docs = db.query(SourceDocument).order_by(desc(SourceDocument.published_date)).all()

        return success_response(

            data={"source_documents": [d.to_dict() for d in docs]},

            message="Source documents retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/source-documents", methods=["GET"])

def get_issue_source_documents(issue_id: str):

    """

    Returns source documents directly connected to a specific civic issue,

    its underlying petitions, or official responses.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        doc_ids = set()

        for g in issue.grievance_records:

            if g.source_document_id:

                doc_ids.add(g.source_document_id)

        for r in issue.responses:

            if getattr(r, "source_document_id", None):

                doc_ids.add(r.source_document_id)

        docs = []

        if doc_ids:

            docs = db.query(SourceDocument).filter(SourceDocument.id.in_(doc_ids)).all()

        return success_response(

            data={"source_documents": [d.to_dict() for d in docs]},

            message="Issue source documents retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/cross-phase-link", methods=["POST"])

def create_cross_phase_link(issue_id: str):

    """

    Explicitly registers a cross-phase relationship connecting a CivicIssue

    to an entity from Phases 1-7.

    STRICT ANTI-CAUSALITY GUARD:

    Rejects superficial links created solely because records share a geographic area.

    Every relationship requires a documented matching method and provenance summary.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        payload = request.get_json(silent=True) or {}

        target_phase = payload.get("target_phase")

        entity_type = payload.get("entity_type")

        entity_id = payload.get("entity_id")

        relationship_nature = payload.get("relationship_nature")

        matching_method = payload.get("matching_method")

        provenance_summary = payload.get("provenance_summary")

        confidence = float(payload.get("confidence", 1.0))

        extra_metadata = payload.get("extra_metadata", {})

        if not all([target_phase, entity_type, entity_id, relationship_nature, matching_method, provenance_summary]):

            return error_response(

                message="Missing required fields: target_phase, entity_type, entity_id, relationship_nature, matching_method, provenance_summary.",

                status_code=400,

            )

        forbidden_methods = {"same_area", "same_district", "geographic_proximity_only", "co_located_only"}

        if matching_method.strip().lower() in forbidden_methods:

            return error_response(

                message=(

                    "Invalid cross-phase relationship: Cannot create cross-phase links merely because "

                    "records share a geographic area without explicit empirical connection (e.g. tender reference, "

                    "scheme sanction, constituency attribution, or news citation)."

                ),

                status_code=400,

            )

        link_id = f"CPL-{uuid.uuid4().hex[:12].upper()}"

        link = CivicCrossPhaseLink(

            link_id=link_id,

            civic_issue_id=issue.id,

            target_phase=target_phase,

            entity_type=entity_type,

            entity_id=str(entity_id),

            relationship_nature=relationship_nature,

            matching_method=matching_method,

            confidence=confidence,

            provenance_summary=provenance_summary,

            extra_metadata=extra_metadata,

            is_test_fixture=bool(payload.get("is_test_fixture", False)),

        )

        db.add(link)

        db.commit()

        db.refresh(link)

        return success_response(

            data=link.to_dict(),

            message="Cross-phase relationship established with explicit provenance.",

            status_code=201,

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/cross-phase", methods=["GET"])

def get_issue_cross_phase_links(issue_id: str):

    """

    Returns all documented cross-phase relationships for an issue,

    with resolved entity payloads from Phases 1-7.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        links = db.query(CivicCrossPhaseLink).filter(CivicCrossPhaseLink.civic_issue_id == issue.id).all()

        resolved_links = resolve_civic_cross_phase_entities(db, links)

        return success_response(

            data={

                "issue_id": issue.id,

                "issue_code": issue.issue_code,

                "cross_phase_links_count": len(resolved_links),

                "cross_phase_links": resolved_links,

            },

            message="Cross-phase relationships retrieved.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/timeline", methods=["GET"])

def get_civic_issue_timeline(issue_id: str):

    """

    Returns the complete 7-stage evidence traceability chain for a civic issue:

    Stage 1: ORIGINAL_PUBLIC_RECORD

    Stage 2: NORMALIZED_CIVIC_ISSUE

    Stage 3: RESPONSIBLE_DEPARTMENT

    Stage 4: OFFICIAL_RESPONSE_ATR

    Stage 5: REPORTED_RESOLUTION

    Stage 6: RESOLUTION_EVIDENCE

    Stage 7: VERIFICATION_STATUS_AND_AUDIT

    Distinguishes:

    - OFFICIAL_GOVERNMENT_RECORD

    - AUTOMATED_SYSTEM_INFERENCE

    - HUMAN_AUDITOR_REVIEW

    Explicitly flags gaps, missing links, and contradictory evidence.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        grievance = db.query(GrievanceRecord).filter(GrievanceRecord.civic_issue_id == issue.id).first()

        department = issue.department

        area = issue.administrative_area

        responses = (

            db.query(ResponseRecord)

            .filter(ResponseRecord.civic_issue_id == issue.id)

            .order_by(ResponseRecord.action_taken_date.asc())

            .all()

        )

        works = db.query(PublicWork).filter(PublicWork.civic_issue_id == issue.id).all()

        audits = (

            db.query(CivicReviewAudit)

            .filter(CivicReviewAudit.civic_issue_id == issue.id)

            .order_by(CivicReviewAudit.created_at.asc())

            .all()

        )

        all_evidences = []

        for r in responses:

            for e in r.evidences:

                all_evidences.append(e)

        contradicting_evidences = [

            e for e in all_evidences

            if e.contradicts_resolution or (hasattr(e, "evidence_type") and e.evidence_type.value in ["NEWS_REPORT", "CITIZEN_AUDIT"] and not e.is_verified)

        ]

        chain = []

        gaps_count = 0

        if grievance:

            src_doc = grievance.source_document

            chain.append({

                "stage_index": 1,

                "stage_name": "ORIGINAL_PUBLIC_RECORD",

                "record_type": "GrievanceRecord",

                "record_id": grievance.grievance_id,

                "origin_badge": "OFFICIAL_GOVERNMENT_RECORD",

                "title": f"Grievance Petition [{grievance.source_id}]",

                "description": sanitize_pii(grievance.description_or_permitted_summary),

                "timestamp": grievance.submission_date.isoformat() if grievance.submission_date else None,

                "matching_method": "SOURCE_PORTAL_INGESTION",

                "confidence": 1.0,

                "is_gap": False,

                "gap_reason": None,

                "source_reference": grievance.source_record_reference,

                "source_document": src_doc.to_dict() if src_doc else None,

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 1,

                "stage_name": "ORIGINAL_PUBLIC_RECORD",

                "record_type": None,

                "record_id": None,

                "origin_badge": "NOT_AVAILABLE",

                "title": "Original Grievance Record Missing",

                "description": "Not available in collected public records or direct gazette entries.",

                "timestamp": None,

                "matching_method": None,

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "Original public grievance petition not found in the ingested archives.",

            })

        chain.append({

            "stage_index": 2,

            "stage_name": "NORMALIZED_CIVIC_ISSUE",

            "record_type": "CivicIssue",

            "record_id": issue.issue_code,

            "origin_badge": "AUTOMATED_SYSTEM_INFERENCE",

            "title": f"Civic Issue: {issue.category.name_en if issue.category else 'Uncategorized'}",

            "description": sanitize_pii(issue.description),

            "timestamp": issue.reported_date.isoformat() if issue.reported_date else None,

            "matching_method": grievance.classification_method if grievance else "RULE_BASED",

            "confidence": grievance.classification_confidence if grievance else 1.0,

            "is_gap": False,

            "gap_reason": None,

            "severity": issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity),

            "status": issue.status.value if hasattr(issue.status, "value") else str(issue.status),

        })

        if department:

            chain.append({

                "stage_index": 3,

                "stage_name": "RESPONSIBLE_DEPARTMENT",

                "record_type": "CivicDepartment",

                "record_id": department.code,

                "origin_badge": "OFFICIAL_GOVERNMENT_RECORD",

                "title": f"Routing: {department.name_en}",

                "description": f"Competent Authority: {department.name_ta} ({department.code}). Jurisdiction Area: {area.name_en if area else 'Statewide'}.",

                "timestamp": issue.reported_date.isoformat() if issue.reported_date else None,

                "matching_method": "JURISDICTION_DIRECTORY_ROUTING",

                "confidence": 1.0,

                "is_gap": False,

                "gap_reason": None,

                "administrative_area": area.to_dict() if area else None,

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 3,

                "stage_name": "RESPONSIBLE_DEPARTMENT",

                "record_type": None,

                "record_id": None,

                "origin_badge": "UNRESOLVED_JURISDICTION",

                "title": "Unresolved Department Responsibility",

                "description": "Responsibility is shared or not explicitly assigned in collected records.",

                "timestamp": None,

                "matching_method": None,

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "No government department officially mapped to this issue docket.",

            })

        if responses:

            latest_resp = responses[-1]

            chain.append({

                "stage_index": 4,

                "stage_name": "OFFICIAL_RESPONSE_ATR",

                "record_type": "ResponseRecord",

                "record_id": latest_resp.response_code,

                "origin_badge": "OFFICIAL_GOVERNMENT_RECORD",

                "title": f"Official Action Taken Report [{latest_resp.action_type.value if hasattr(latest_resp.action_type, 'value') else str(latest_resp.action_type)}]",

                "description": sanitize_pii(latest_resp.response_summary or latest_resp.official_remark),

                "timestamp": latest_resp.action_taken_date.isoformat() if latest_resp.action_taken_date else None,

                "matching_method": "DEPARTMENT_ATR_SUBMISSION",

                "confidence": 1.0,

                "is_gap": False,

                "gap_reason": None,

                "total_responses_count": len(responses),

                "reported_status": latest_resp.reported_status,

                "is_sla_breached": latest_resp.is_sla_breached,

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 4,

                "stage_name": "OFFICIAL_RESPONSE_ATR",

                "record_type": None,

                "record_id": None,

                "origin_badge": "NO_OFFICIAL_RESPONSE",

                "title": "No Official ATR Filed",

                "description": "No departmental Action-Taken Report or official reply found in collected records.",

                "timestamp": None,

                "matching_method": None,

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "Department has not filed an Action-Taken Report or official acknowledgment.",

            })

        is_marked_resolved = (

            issue.status in [CivicIssueStatus.RESOLVED, CivicIssueStatus.VERIFIED_RESOLVED]

            or any(r.reported_status == "marked_resolved" for r in responses)

            or issue.actual_resolution_date is not None

        )

        if is_marked_resolved:

            res_date = issue.actual_resolution_date or (responses[-1].action_taken_date if responses else None)

            chain.append({

                "stage_index": 5,

                "stage_name": "REPORTED_RESOLUTION",

                "record_type": "StatusDeclaration",

                "record_id": f"RESOLVED-{issue.issue_code}",

                "origin_badge": "OFFICIAL_GOVERNMENT_RECORD",

                "title": "Reported Resolution Declared",

                "description": (

                    "Department records mark this issue as resolved. "

                    "Note: 'marked_resolved' represents an official closure claim, "

                    "not an independently verified empirical outcome."

                ),

                "timestamp": res_date.isoformat() if res_date else None,

                "matching_method": "OFFICIAL_CLOSURE_ENTRY",

                "confidence": 1.0,

                "is_gap": False,

                "gap_reason": None,

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 5,

                "stage_name": "REPORTED_RESOLUTION",

                "record_type": None,

                "record_id": None,

                "origin_badge": "UNRESOLVED_OR_PENDING",

                "title": "Not Marked Resolved",

                "description": f"Issue status is currently '{issue.status.value if hasattr(issue.status, 'value') else str(issue.status)}'.",

                "timestamp": None,

                "matching_method": None,

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "Responsible authority has not declared resolution.",

            })

        if all_evidences:

            chain.append({

                "stage_index": 6,

                "stage_name": "RESOLUTION_EVIDENCE",

                "record_type": "ResolutionEvidence",

                "record_id": [e.id for e in all_evidences],

                "origin_badge": "OFFICIAL_GOVERNMENT_RECORD" if all(e.evidence_type.value in ["WORK_ORDER", "COMPLETION_CERTIFICATE", "FIELD_INSPECTION_REPORT"] for e in all_evidences) else "INDEPENDENT_EVIDENCE",

                "title": f"Empirical Resolution Evidence ({len(all_evidences)} Artifacts)",

                "description": "; ".join(f"[{e.evidence_type.value}] {e.title}" for e in all_evidences[:3]),

                "timestamp": all_evidences[-1].created_at.isoformat() if all_evidences[-1].created_at else None,

                "matching_method": all_evidences[0].matching_method if hasattr(all_evidences[0], "matching_method") else "RECORD_ID_MATCH",

                "confidence": float(all_evidences[0].confidence) if hasattr(all_evidences[0], "confidence") else 1.0,

                "is_gap": False,

                "gap_reason": None,

                "evidences": [e.to_dict() for e in all_evidences],

                "public_works": [w.to_dict() for w in works],

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 6,

                "stage_name": "RESOLUTION_EVIDENCE",

                "record_type": None,

                "record_id": None,

                "origin_badge": "NO_EMPIRICAL_EVIDENCE",

                "title": "No Empirical Evidence Documented",

                "description": "No completion certificates, field inspection reports, or work orders logged to corroborate resolution.",

                "timestamp": None,

                "matching_method": None,

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "Zero empirical artifacts available to substantiate closure claims.",

            })

        ver_status = issue.resolution_verification_status.value if hasattr(issue.resolution_verification_status, "value") else str(issue.resolution_verification_status)

        assessment_val = issue.evidence_assessment.value if hasattr(issue.evidence_assessment, "value") else (str(issue.evidence_assessment) if issue.evidence_assessment else "pending_review")

        if audits:

            latest_audit = audits[-1]

            chain.append({

                "stage_index": 7,

                "stage_name": "VERIFICATION_STATUS_AND_AUDIT",

                "record_type": "CivicReviewAudit",

                "record_id": latest_audit.id,

                "origin_badge": "HUMAN_AUDITOR_REVIEW",

                "title": f"Human Review Audit: {latest_audit.action}",

                "description": f"Auditor ({latest_audit.reviewer_role}): {latest_audit.reason}",

                "timestamp": latest_audit.created_at.isoformat() if latest_audit.created_at else None,

                "matching_method": "ROLE_GOVERNED_HUMAN_AUDIT",

                "confidence": 1.0,

                "is_gap": False,

                "gap_reason": None,

                "verification_status": ver_status,

                "evidence_assessment": assessment_val,

                "audit_history": [a.to_dict() for a in audits],

            })

        elif ver_status == "VERIFIED":

            chain.append({

                "stage_index": 7,

                "stage_name": "VERIFICATION_STATUS_AND_AUDIT",

                "record_type": "SystemVerificationState",

                "record_id": None,

                "origin_badge": "AUTOMATED_SYSTEM_INFERENCE",

                "title": "Independently Verified by Corroborating Evidence",

                "description": "Corroborated by high-confidence empirical artifacts (work completion certificates, inspection records).",

                "timestamp": None,

                "matching_method": "MULTI_SOURCE_CORROBORATION",

                "confidence": 0.95,

                "is_gap": False,

                "gap_reason": None,

                "verification_status": ver_status,

                "evidence_assessment": assessment_val,

                "audit_history": [],

            })

        else:

            gaps_count += 1

            chain.append({

                "stage_index": 7,

                "stage_name": "VERIFICATION_STATUS_AND_AUDIT",

                "record_type": "SystemVerificationState",

                "record_id": None,

                "origin_badge": "PENDING_REVIEW",

                "title": f"Verification Status: {ver_status}",

                "description": "Pending human audit review or corroborating evidence verification.",

                "timestamp": None,

                "matching_method": "PENDING_ASSESSMENT",

                "confidence": 0.0,

                "is_gap": True,

                "gap_reason": "Not independently verified; pending auditor review or additional evidence.",

                "verification_status": ver_status,

                "evidence_assessment": assessment_val,

                "audit_history": [],

            })

        completeness_score = round((7.0 - gaps_count) / 7.0, 2)

        payload = {

            "issue_id": issue.id,

            "issue_code": issue.issue_code,

            "issue_title": issue.title,

            "reported_date": issue.reported_date.isoformat() if issue.reported_date else None,

            "current_status": issue.status.value if hasattr(issue.status, "value") else str(issue.status),

            "verification_status": ver_status,

            "evidence_assessment": assessment_val,

            "completeness_score": completeness_score,

            "gaps_count": gaps_count,

            "contradictions_detected": [e.to_dict() for e in contradicting_evidences],

            "chain": chain,

            "backward_navigation": {

                "has_resolution_evidence": len(all_evidences) > 0,

                "evidence_to_response_map": [{"evidence_id": e.id, "response_id": e.response_id} for e in all_evidences],

                "response_to_issue_map": [{"response_id": r.id, "issue_id": issue.id} for r in responses],

                "issue_to_grievance_map": [{"grievance_id": g.grievance_id, "source_doc_id": g.source_document_id} for g in issue.grievance_records],

            },

        }

        return success_response(data=payload, message="Traceability timeline generated successfully.")

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/provenance", methods=["GET"])

def get_civic_issue_provenance(issue_id: str):

    """

    Returns the complete node-edge provenance graph for a civic issue.

    """

    db: Session = SessionLocal()

    try:

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        nodes = []

        edges = []

        issue_node_id = f"ISSUE-{issue.id}"

        nodes.append({

            "id": issue_node_id,

            "type": "CivicIssue",

            "label": issue.issue_code,

            "data": issue.to_dict(),

        })

        for g in issue.grievance_records:

            g_node_id = f"GRIEVANCE-{g.id}"

            nodes.append({

                "id": g_node_id,

                "type": "GrievanceRecord",

                "label": g.grievance_id,

                "data": g.to_dict(),

            })

            edges.append({

                "source": g_node_id,

                "target": issue_node_id,

                "relationship": "NORMALIZED_INTO",

                "matching_method": g.classification_method or "RULE_BASED",

                "confidence": g.classification_confidence or 1.0,

            })

            if g.source_document:

                doc_node_id = f"DOC-{g.source_document.id}"

                if not any(n["id"] == doc_node_id for n in nodes):

                    nodes.append({

                        "id": doc_node_id,

                        "type": "SourceDocument",

                        "label": g.source_document.document_code,

                        "data": g.source_document.to_dict(),

                    })

                edges.append({

                    "source": doc_node_id,

                    "target": g_node_id,

                    "relationship": "EXTRACTED_FROM",

                    "matching_method": "DOCUMENT_PARSING",

                    "confidence": 1.0,

                })

        if issue.department:

            dept_node_id = f"DEPT-{issue.department.id}"

            nodes.append({

                "id": dept_node_id,

                "type": "CivicDepartment",

                "label": issue.department.code,

                "data": issue.department.to_dict(),

            })

            edges.append({

                "source": issue_node_id,

                "target": dept_node_id,

                "relationship": "ASSIGNED_TO_DEPARTMENT",

                "matching_method": "JURISDICTION_ROUTING",

                "confidence": 1.0,

            })

        if issue.administrative_area:

            area_node_id = f"AREA-{issue.administrative_area.id}"

            nodes.append({

                "id": area_node_id,

                "type": "AdministrativeArea",

                "label": issue.administrative_area.area_code,

                "data": issue.administrative_area.to_dict(),

            })

            edges.append({

                "source": issue_node_id,

                "target": area_node_id,

                "relationship": "LOCATED_IN",

                "matching_method": "GEOGRAPHIC_BOUNDARY_MAPPING",

                "confidence": 1.0,

            })

        for r in issue.responses:

            r_node_id = f"RESP-{r.id}"

            nodes.append({

                "id": r_node_id,

                "type": "ResponseRecord",

                "label": r.response_code,

                "data": r.to_dict(),

            })

            edges.append({

                "source": r_node_id,

                "target": issue_node_id,

                "relationship": "OFFICIAL_ATR_FOR",

                "matching_method": "PORTAL_RESPONSE_LOGGING",

                "confidence": 1.0,

            })

            for e in r.evidences:

                e_node_id = f"EVID-{e.id}"

                nodes.append({

                    "id": e_node_id,

                    "type": "ResolutionEvidence",

                    "label": f"EVID-{e.id}: {e.evidence_type.value}",

                    "data": e.to_dict(),

                })

                edges.append({

                    "source": e_node_id,

                    "target": r_node_id,

                    "relationship": "CORROBORATES_RESPONSE",

                    "matching_method": e.matching_method or "RECORD_ID_MATCH",

                    "confidence": e.confidence or 1.0,

                })

        for w in issue.public_works:

            w_node_id = f"WORK-{w.id}"

            nodes.append({

                "id": w_node_id,

                "type": "PublicWork",

                "label": w.work_code,

                "data": w.to_dict(),

            })

            edges.append({

                "source": w_node_id,

                "target": issue_node_id,

                "relationship": "REMEDIATION_WORK_CONTRACT",

                "matching_method": "TENDER_REFERENCE_MATCH",

                "confidence": 1.0,

            })

        for a in issue.review_audits:

            a_node_id = f"AUDIT-{a.id}"

            nodes.append({

                "id": a_node_id,

                "type": "CivicReviewAudit",

                "label": f"AUDIT-{a.id}: {a.action}",

                "data": a.to_dict(),

            })

            edges.append({

                "source": a_node_id,

                "target": issue_node_id,

                "relationship": "HUMAN_AUDIT_ACTION",

                "matching_method": "ROLE_GOVERNED_REVIEW",

                "confidence": 1.0,

            })

        for c in issue.cross_phase_links:

            c_node_id = f"CPL-{c.link_id}"

            nodes.append({

                "id": c_node_id,

                "type": "CivicCrossPhaseLink",

                "label": c.relationship_nature,

                "data": c.to_dict(),

            })

            edges.append({

                "source": issue_node_id,

                "target": c_node_id,

                "relationship": "CROSS_PHASE_CONNECTION",

                "matching_method": c.matching_method,

                "confidence": c.confidence,

            })

        return success_response(

            data={

                "issue_id": issue.id,

                "issue_code": issue.issue_code,

                "node_count": len(nodes),

                "edge_count": len(edges),

                "nodes": nodes,

                "edges": edges,

            },

            message="Provenance graph generated.",

        )

    finally:

        db.close()

@civic_bp.route("/issues/<issue_id>/review", methods=["POST"])

def submit_civic_issue_review(issue_id: str):

    """

    Submits a role-governed review audit action for a civic issue.

    Enforces Step 4 & 7 verification governance.

    Header Required: X-Reviewer-Role: SENIOR_CIVIC_AUDITOR | DISTRICT_AUDITOR | CIVIC_OMBUDSPERSON | ADMIN

    """

    db: Session = SessionLocal()

    try:

        reviewer_role = request.headers.get("X-Reviewer-Role", "").strip()

        allowed_roles = {"SENIOR_CIVIC_AUDITOR", "DISTRICT_AUDITOR", "CIVIC_OMBUDSPERSON", "ADMIN"}

        if not reviewer_role or reviewer_role not in allowed_roles:

            return error_response(

                message=f"Forbidden: Reviewer role '{reviewer_role}' not authorized to perform resolution audits. Required role: SENIOR_CIVIC_AUDITOR, DISTRICT_AUDITOR, CIVIC_OMBUDSPERSON, or ADMIN.",

                status_code=403,

            )

        from backend.core.security import verify_api_key

        if not verify_api_key(request):

            return error_response(

                message="Forbidden: Invalid or missing reviewer API key.",

                status_code=403,

            )

        issue = None

        if issue_id.isdigit():

            issue = db.query(CivicIssue).filter(CivicIssue.id == int(issue_id)).first()

        if not issue:

            issue = db.query(CivicIssue).filter(CivicIssue.issue_code == issue_id).first()

        if not issue:

            return error_response(message=f"Civic issue '{issue_id}' not found.", status_code=404)

        payload = request.get_json(silent=True) or {}

        action = payload.get("action", "").strip().upper()

        reason = payload.get("reason", "").strip()

        new_assessment = payload.get("new_assessment")

        evidence_ids = payload.get("evidence_ids", [])

        reviewer_id = payload.get("reviewer_id") or f"AUDITOR-{uuid.uuid4().hex[:6].upper()}"

        allowed_actions = {

            "VERIFY_RESOLUTION",

            "REOPEN_ISSUE",

            "DISPUTE_RESOLUTION",

            "REQUEST_EVIDENCE",

            "UPDATE_ASSESSMENT",

        }

        if action not in allowed_actions:

            return error_response(

                message=f"Invalid review action '{action}'. Must be one of: {', '.join(sorted(allowed_actions))}.",

                status_code=400,

            )

        if not reason or len(reason) < 5:

            return error_response(

                message="Review reason is required and must contain at least 5 characters documenting audit findings.",

                status_code=400,

            )

        previous_status = issue.status.value if hasattr(issue.status, "value") else str(issue.status)

        previous_assessment = (

            issue.evidence_assessment.value

            if hasattr(issue.evidence_assessment, "value")

            else (str(issue.evidence_assessment) if issue.evidence_assessment else "pending_review")

        )

        target_assessment = new_assessment

        if action == "VERIFY_RESOLUTION":

            issue.resolution_verification_status = ResolutionVerificationStatus.VERIFIED

            issue.evidence_assessment = EvidenceAssessmentEnum.INDEPENDENTLY_VERIFIED_RESOLVED

            issue.status = CivicIssueStatus.VERIFIED_RESOLVED

            target_assessment = EvidenceAssessmentEnum.INDEPENDENTLY_VERIFIED_RESOLVED.value

        elif action == "DISPUTE_RESOLUTION":

            issue.resolution_verification_status = ResolutionVerificationStatus.CONTRADICTED

            issue.evidence_assessment = EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_CONFLICTING

            issue.status = CivicIssueStatus.DISPUTED

            target_assessment = EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_CONFLICTING.value

        elif action == "REOPEN_ISSUE":

            issue.status = CivicIssueStatus.OPEN

            issue.resolution_verification_status = ResolutionVerificationStatus.PENDING_VERIFICATION

            issue.evidence_assessment = EvidenceAssessmentEnum.INSUFFICIENT_EVIDENCE

            issue.repeat_count = (issue.repeat_count or 1) + 1

            target_assessment = EvidenceAssessmentEnum.INSUFFICIENT_EVIDENCE.value

        elif action == "REQUEST_EVIDENCE":

            issue.evidence_assessment = EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_INCOMPLETE

            target_assessment = EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_INCOMPLETE.value

        elif action == "UPDATE_ASSESSMENT":

            if new_assessment:

                try:

                    enum_val = EvidenceAssessmentEnum(new_assessment)

                    issue.evidence_assessment = enum_val

                    target_assessment = enum_val.value

                except ValueError:

                    return error_response(

                        message=f"Invalid assessment '{new_assessment}'. Valid options: {[e.value for e in EvidenceAssessmentEnum]}",

                        status_code=400,

                    )

        clean_reason = sanitize_pii(reason)

        audit_entry = CivicReviewAudit(

            civic_issue_id=issue.id,

            reviewer_id=reviewer_id,

            reviewer_role=reviewer_role,

            previous_status=previous_status,

            new_status=issue.status.value if hasattr(issue.status, "value") else str(issue.status),

            previous_assessment=previous_assessment,

            new_assessment=target_assessment or previous_assessment,

            action=action,

            reason=clean_reason,

            evidence_ids=evidence_ids,

            is_test_fixture=bool(payload.get("is_test_fixture", issue.is_test_fixture)),

        )

        db.add(audit_entry)

        event = IssueEvent(

            civic_issue_id=issue.id,

            event_type="AUDITOR_REVIEW_ACTION",

            actor_type=reviewer_role,

            notes=f"Action: {action}. Assessment: {target_assessment}. Rationale: {clean_reason}",

        )

        db.add(event)

        db.commit()

        db.refresh(audit_entry)

        db.refresh(issue)

        return success_response(

            data={

                "audit": audit_entry.to_dict(),

                "issue": issue.to_dict(),

            },

            message=f"Review audit action '{action}' recorded by {reviewer_role}.",

            status_code=201,

        )

    finally:

        db.close()

@civic_bp.route("/traceability/metrics", methods=["GET"])

def get_traceability_metrics():

    """

    Computes canonical Phase 8.11 evidence traceability and resolution indicators:

    1. Evidence Coverage Rate: (Resolved issues with evidence / Total marked_resolved issues)

    2. Independent Verification Rate: (Independently verified / Total marked_resolved issues)

    3. Department Response Rate: (Issues with official ATR / Total issues)

    4. Unverified Resolution Rate: (Marked resolved without verification / Total marked_resolved issues)

    5. Conflicting Evidence Rate: (Issues with contradicting evidence / Issues with evidence)

    6. Audit Trail Completeness Rate: (Issues with complete provenance / Total issues)

    Safeguards:

    - Zero issues handled cleanly (returns 0.0 without division by zero).

    - Explicit distinction between reported status and verified outcome.

    """

    db: Session = SessionLocal()

    try:

        district = request.args.get("district")

        department_code = request.args.get("department")

        query = db.query(CivicIssue)

        if district:

            query = query.join(AdministrativeArea).filter(

                or_(

                    AdministrativeArea.name_en.ilike(f"%{district}%"),

                    AdministrativeArea.area_code.ilike(f"%{district}%"),

                )

            )

        if department_code:

            query = query.join(CivicDepartment).filter(CivicDepartment.code == department_code)

        all_issues = query.all()

        total_issues = len(all_issues)

        if total_issues == 0:

            return success_response(

                data={

                    "total_issues": 0,

                    "marked_resolved_count": 0,

                    "evidence_coverage_rate": 0.0,

                    "evidence_coverage_percentage": 0.0,

                    "independent_verification_rate": 0.0,

                    "independent_verification_percentage": 0.0,

                    "department_response_rate": 0.0,

                    "department_response_percentage": 0.0,

                    "unverified_resolution_rate": 0.0,

                    "unverified_resolution_percentage": 0.0,

                    "conflicting_evidence_rate": 0.0,

                    "conflicting_evidence_percentage": 0.0,

                    "audit_trail_completeness_rate": 0.0,

                    "audit_trail_completeness_percentage": 0.0,

                    "definitions": {

                        "evidence_coverage_rate": "Proportion of marked-resolved issues backed by at least one empirical resolution evidence artifact.",

                        "independent_verification_rate": "Proportion of marked-resolved issues independently verified by field audit or corroborating proof.",

                        "department_response_rate": "Proportion of civic issues having an official departmental Action-Taken Report or acknowledgment.",

                        "unverified_resolution_rate": "Proportion of marked-resolved issues lacking independent corroboration.",

                        "conflicting_evidence_rate": "Proportion of evidence-backed issues where independent findings contradict the official closure claim.",

                        "audit_trail_completeness_rate": "Proportion of issues with unbroken bidirectional audit logs from public petition to resolution audit.",

                    },

                    "methodological_caveats": [

                        "Data sample contains zero matching issues for the specified filter criteria.",

                        "Complaint volume does not equal true civic problem prevalence.",

                    ],

                },

                message="Traceability metrics computed (empty sample).",

            )

        resolved_issues = [

            i for i in all_issues

            if i.status in [CivicIssueStatus.RESOLVED, CivicIssueStatus.VERIFIED_RESOLVED]

            or i.actual_resolution_date is not None

            or any(r.reported_status == "marked_resolved" for r in i.responses)

        ]

        total_resolved = len(resolved_issues)

        issues_with_evidence = [i for i in all_issues if any(len(r.evidences) > 0 for r in i.responses)]

        resolved_with_evidence = [i for i in resolved_issues if any(len(r.evidences) > 0 for r in i.responses)]

        verified_issues = [

            i for i in resolved_issues

            if i.resolution_verification_status == ResolutionVerificationStatus.VERIFIED

            or i.evidence_assessment == EvidenceAssessmentEnum.INDEPENDENTLY_VERIFIED_RESOLVED

            or any(a.action == "VERIFY_RESOLUTION" for a in i.review_audits)

        ]

        issues_with_response = [i for i in all_issues if len(i.responses) > 0]

        conflicting_issues = [

            i for i in issues_with_evidence

            if i.resolution_verification_status == ResolutionVerificationStatus.CONTRADICTED

            or i.evidence_assessment == EvidenceAssessmentEnum.RESOLUTION_EVIDENCE_CONFLICTING

            or any(any(e.contradicts_resolution for e in r.evidences) for r in i.responses)

        ]

        complete_audit_issues = [

            i for i in all_issues

            if len(i.grievance_records) > 0

            and i.department_id is not None

            and len(i.responses) > 0

            and (len(i.review_audits) > 0 or i.resolution_verification_status == ResolutionVerificationStatus.VERIFIED)

        ]

        ev_cov_rate = round(len(resolved_with_evidence) / total_resolved, 4) if total_resolved > 0 else 0.0

        ind_ver_rate = round(len(verified_issues) / total_resolved, 4) if total_resolved > 0 else 0.0

        dept_resp_rate = round(len(issues_with_response) / total_issues, 4) if total_issues > 0 else 0.0

        unver_res_rate = round((total_resolved - len(verified_issues)) / total_resolved, 4) if total_resolved > 0 else 0.0

        conflict_rate = round(len(conflicting_issues) / len(issues_with_evidence), 4) if len(issues_with_evidence) > 0 else 0.0

        comp_rate = round(len(complete_audit_issues) / total_issues, 4) if total_issues > 0 else 0.0

        metrics_payload = {

            "sample_size": total_issues,

            "total_issues": total_issues,

            "total_marked_resolved": total_resolved,

            "total_with_evidence": len(issues_with_evidence),

            "evidence_coverage_rate": ev_cov_rate,

            "evidence_coverage_percentage": round(ev_cov_rate * 100, 2),

            "independent_verification_rate": ind_ver_rate,

            "independent_verification_percentage": round(ind_ver_rate * 100, 2),

            "department_response_rate": dept_resp_rate,

            "department_response_percentage": round(dept_resp_rate * 100, 2),

            "unverified_resolution_rate": unver_res_rate,

            "unverified_resolution_percentage": round(unver_res_rate * 100, 2),

            "conflicting_evidence_rate": conflict_rate,

            "conflicting_evidence_percentage": round(conflict_rate * 100, 2),

            "audit_trail_completeness_rate": comp_rate,

            "audit_trail_completeness_percentage": round(comp_rate * 100, 2),

            "counts": {

                "resolved_with_evidence_count": len(resolved_with_evidence),

                "independently_verified_count": len(verified_issues),

                "with_official_response_count": len(issues_with_response),

                "unverified_resolved_count": max(0, total_resolved - len(verified_issues)),

                "conflicting_evidence_count": len(conflicting_issues),

                "complete_audit_trail_count": len(complete_audit_issues),

            },

            "definitions": {

                "evidence_coverage_rate": "Proportion of marked-resolved issues backed by at least one empirical resolution evidence artifact.",

                "independent_verification_rate": "Proportion of marked-resolved issues independently verified by field audit or corroborating proof.",

                "department_response_rate": "Proportion of civic issues having an official departmental Action-Taken Report or acknowledgment.",

                "unverified_resolution_rate": "Proportion of marked-resolved issues lacking independent corroboration.",

                "conflicting_evidence_rate": "Proportion of evidence-backed issues where independent findings contradict the official closure claim.",

                "audit_trail_completeness_rate": "Proportion of issues with unbroken bidirectional audit logs from public petition to resolution audit.",

            },

            "methodological_caveats": [

                "Complaint counts reflect portal access, digital literacy, and administrative reporting practices, not ground truth issue frequency.",

                "A department status of 'marked_resolved' represents an administrative claim and must not be conflated with independently verified resolution.",

                "Absence of evidence does not constitute evidence of non-resolution, but indicates missing verification data.",

            ],

        }

        return success_response(data=metrics_payload, message="Traceability metrics computed successfully.")

    finally:

        db.close()

