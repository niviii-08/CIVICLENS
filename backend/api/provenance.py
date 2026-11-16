"""
CIVICLENS TN — Provenance, Safeguards & Evidence Graph API Blueprint (Phase 11.1, 11.7, 11.9)
"""
from flask import Blueprint, request
from backend.database.session import SessionLocal
from backend.api.responses import success_response, error_response
from backend.models.provenance import (
    GranularExtractionLineage, RightOfReplyRegistry, PublicCorrectionNotice,
    DPDPAComplianceRequest
)
from backend.services.evidence_graph_expansion_service import EvidenceGraphExpansionService

provenance_bp = Blueprint("provenance", __name__, url_prefix="/provenance")


@provenance_bp.route("/lineage/<target_table>/<target_id>", methods=["GET"])
def get_lineage(target_table, target_id):
    """Retrieve granular document extraction lineage for a specific record."""
    db = SessionLocal()
    try:
        lineages = db.query(GranularExtractionLineage).filter_by(
            target_table=target_table, target_record_id=str(target_id)
        ).all()
        data = [
            {
                "id": l.id,
                "source_title": l.source_document_title,
                "source_url": l.source_url,
                "sha256": l.document_sha256,
                "page": l.page_number,
                "table_index": l.table_index,
                "row_number": l.row_number,
                "column": l.column_name,
                "verbatim": l.extracted_verbatim_text,
                "link_health": l.link_health.value,
                "transaction_time": l.transaction_time.isoformat(),
            }
            for l in lineages
        ]
        return success_response(data=data, message="Extraction lineage retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@provenance_bp.route("/right-of-reply", methods=["GET"])
def list_right_of_reply():
    """List Right of Reply notices and rebuttal records under BNS 2023 Sec 356."""
    db = SessionLocal()
    try:
        records = db.query(RightOfReplyRegistry).order_by(RightOfReplyRegistry.notice_dispatched_at.desc()).all()
        data = [
            {
                "id": r.id,
                "case_ref": r.reply_case_ref,
                "entity": r.entity_name,
                "designation": r.entity_designation_or_type,
                "matter": r.matter_in_dispute,
                "dispatched_at": r.notice_dispatched_at.isoformat(),
                "deadline": r.deadline_date.isoformat(),
                "status": r.status.value,
                "rebuttal": r.rebuttal_statement,
            }
            for r in records
        ]
        return success_response(data=data, message="Right of reply records retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@provenance_bp.route("/corrections", methods=["GET"])
def list_corrections():
    """List public correction and retraction notices."""
    db = SessionLocal()
    try:
        corrections = db.query(PublicCorrectionNotice).order_by(PublicCorrectionNotice.published_at.desc()).all()
        data = [
            {
                "id": c.id,
                "notice_id": c.notice_id,
                "record_ref": c.target_record_ref,
                "original": c.original_statement,
                "corrected": c.corrected_statement,
                "reason": c.reason_for_correction,
                "published_at": c.published_at.isoformat(),
                "editor": c.editor_signoff,
            }
            for c in corrections
        ]
        return success_response(data=data, message="Public corrections retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@provenance_bp.route("/graph/expand", methods=["POST"])
def expand_graph():
    """Trigger Phase 11 graph expansion."""
    db = SessionLocal()
    try:
        res = EvidenceGraphExpansionService.expand_graph_with_phase11_entities(db)
        return success_response(data=res, message="Graph expanded with Phase 11 entities")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()


@provenance_bp.route("/graph/coverage", methods=["GET"])
def get_graph_coverage():
    """Get statewide evidence graph coverage metrics."""
    db = SessionLocal()
    try:
        metrics = EvidenceGraphExpansionService.get_graph_coverage_metrics(db)
        return success_response(data=metrics, message="Graph coverage metrics retrieved")
    except Exception as e:
        return error_response(str(e), status_code=500)
    finally:
        db.close()
