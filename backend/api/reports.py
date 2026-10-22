"""
CIVICLENS TN — Phase 13.7: Transparent Civic Reports and Exports REST API Blueprint.

Provides citizen-accessible endpoints for generating and exporting structured public accountability reports:
  - GET  /api/reports/types
  - POST /api/reports/generate
  - GET  /api/reports/generate
  - GET  /api/reports/export/<report_type>/<subject_id>

Supported Formats:
  - JSON (application/json)
  - CSV (text/csv; charset=utf-8) with RFC 4180 compliance & UTF-8 BOM
  - Markdown (text/markdown; charset=utf-8)
  - HTML (text/html; charset=utf-8)

Security Guardrails:
  - Automated DPDPA 2023 PII scrubbing
  - CSV formula injection protection (CWE-1236)
  - HTML entity escaping (XSS mitigation)
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from flask import Blueprint, Response, make_response, request

from backend.api.responses import error_response, success_response
from backend.services.transparent_report_service import TransparentReportService

logger = logging.getLogger("civiclens.phase13.api.reports")

reports_bp = Blueprint("reports", __name__, url_prefix="/reports")

MIME_TYPES = {
    "json": "application/json; charset=utf-8",
    "csv": "text/csv; charset=utf-8",
    "markdown": "text/markdown; charset=utf-8",
    "html": "text/html; charset=utf-8",
}

EXTENSIONS = {
    "json": "json",
    "csv": "csv",
    "markdown": "md",
    "html": "html",
}


def _format_download_response(
    content: Any,
    export_format: str,
    filename_base: str,
    as_attachment: bool = True,
) -> Response:
    """Formats file response with content-type and content-disposition headers."""
    fmt = export_format.lower().strip()
    mimetype = MIME_TYPES.get(fmt, "text/plain; charset=utf-8")
    ext = EXTENSIONS.get(fmt, "txt")
    filename = f"{filename_base}.{ext}"

    if fmt == "json":
        if isinstance(content, (dict, list)):
            body = json.dumps(content, ensure_ascii=False, indent=2)
        else:
            body = str(content)
    else:
        body = str(content)

    resp = make_response(body)
    resp.headers["Content-Type"] = mimetype
    disposition_type = "attachment" if as_attachment else "inline"
    resp.headers["Content-Disposition"] = f'{disposition_type}; filename="{filename}"'
    return resp


@reports_bp.route("/types", methods=["GET"])
def get_report_types():
    """Retrieve supported civic report types, formats, and security capabilities."""
    service = TransparentReportService()
    try:
        types_info = service.get_supported_report_types()
        return success_response(
            data=types_info,
            message="Report types catalog retrieved successfully",
        )
    except Exception as exc:
        logger.error(f"Error retrieving report types: {exc}", exc_info=True)
        return error_response(f"Internal error retrieving report types: {exc}", status_code=500)


@reports_bp.route("/generate", methods=["POST"])
def generate_report_post():
    """
    Generate or export a transparent civic report.
    JSON payload:
      - report_type (required): 'scheme_budget', 'claim_assessment', 'civic_timeline', 'local_comparison', 'promise_tracking'
      - subject_id (optional): entity/subject identifier
      - format (optional, default 'json'): 'json', 'csv', 'markdown', 'html'
      - parameters (optional): extra filter parameters
      - is_auditor (optional, default false): auditor permission flag
    """
    payload = request.get_json(silent=True) or {}
    report_type = payload.get("report_type")
    if not report_type:
        return error_response("Missing required field 'report_type'", status_code=400)

    subject_id = payload.get("subject_id")
    export_format = payload.get("format", "json").lower().strip()
    parameters = payload.get("parameters") or {}
    is_auditor = bool(payload.get("is_auditor", False))

    service = TransparentReportService()
    if report_type not in service.SUPPORTED_REPORT_TYPES:
        return error_response(
            f"Unsupported report type '{report_type}'. Supported: {list(service.SUPPORTED_REPORT_TYPES.keys())}",
            status_code=400,
        )
    if export_format not in service.SUPPORTED_FORMATS:
        return error_response(
            f"Unsupported export format '{export_format}'. Supported: {service.SUPPORTED_FORMATS}",
            status_code=400,
        )

    try:
        report_data = service.generate_report(
            report_type=report_type,
            subject_id=subject_id,
            parameters=parameters,
            is_auditor=is_auditor,
        )
        if export_format == "json":
            return success_response(data=report_data, message="Report generated successfully")

        # Non-JSON formats (csv, markdown, html)
        exported_str = service.export_report(report_data, export_format=export_format)
        filename_base = f"civiclens_{report_type}_{subject_id or 'tn'}"
        return _format_download_response(exported_str, export_format, filename_base, as_attachment=False)
    except ValueError as ve:
        logger.warning(f"Validation error generating report: {ve}")
        return error_response(str(ve), status_code=400)
    except Exception as exc:
        logger.error(f"Error generating report: {exc}", exc_info=True)
        return error_response(f"Internal error generating report: {exc}", status_code=500)


@reports_bp.route("/generate", methods=["GET"])
def generate_report_get():
    """
    Generate or export a transparent civic report via query parameters.
    Query parameters:
      - report_type (required)
      - subject_id (optional)
      - format (optional, default 'json')
      - is_auditor (optional, default false)
      - ...additional query parameters passed to report builder
    """
    report_type = request.args.get("report_type")
    if not report_type:
        return error_response("Missing required query parameter 'report_type'", status_code=400)

    subject_id = request.args.get("subject_id")
    export_format = request.args.get("format", "json").lower().strip()
    is_auditor = request.args.get("is_auditor", "false").lower() in ("true", "1")

    parameters = {
        k: v for k, v in request.args.items()
        if k not in ("report_type", "subject_id", "format", "is_auditor")
    }

    service = TransparentReportService()
    if report_type not in service.SUPPORTED_REPORT_TYPES:
        return error_response(
            f"Unsupported report type '{report_type}'. Supported: {list(service.SUPPORTED_REPORT_TYPES.keys())}",
            status_code=400,
        )
    if export_format not in service.SUPPORTED_FORMATS:
        return error_response(
            f"Unsupported export format '{export_format}'. Supported: {service.SUPPORTED_FORMATS}",
            status_code=400,
        )

    try:
        report_data = service.generate_report(
            report_type=report_type,
            subject_id=subject_id,
            parameters=parameters,
            is_auditor=is_auditor,
        )
        if export_format == "json":
            return success_response(data=report_data, message="Report generated successfully")

        exported_str = service.export_report(report_data, export_format=export_format)
        filename_base = f"civiclens_{report_type}_{subject_id or 'tn'}"
        return _format_download_response(exported_str, export_format, filename_base, as_attachment=False)
    except ValueError as ve:
        logger.warning(f"Validation error generating report: {ve}")
        return error_response(str(ve), status_code=400)
    except Exception as exc:
        logger.error(f"Error generating report: {exc}", exc_info=True)
        return error_response(f"Internal error generating report: {exc}", status_code=500)


@reports_bp.route("/export/<string:report_type>/<string:subject_id>", methods=["GET"])
def export_report_endpoint(report_type: str, subject_id: str):
    """
    Export / download a transparent civic report as a standalone file.
    Query parameters:
      - format (optional, default 'json'): 'json', 'csv', 'markdown', 'html'
      - is_auditor (optional, default false)
      - ...additional query parameters passed to report builder
    """
    export_format = request.args.get("format", "json").lower().strip()
    is_auditor = request.args.get("is_auditor", "false").lower() in ("true", "1")

    parameters = {
        k: v for k, v in request.args.items()
        if k not in ("format", "is_auditor")
    }

    service = TransparentReportService()
    if report_type not in service.SUPPORTED_REPORT_TYPES:
        return error_response(
            f"Unsupported report type '{report_type}'. Supported: {list(service.SUPPORTED_REPORT_TYPES.keys())}",
            status_code=400,
        )
    if export_format not in service.SUPPORTED_FORMATS:
        return error_response(
            f"Unsupported export format '{export_format}'. Supported: {service.SUPPORTED_FORMATS}",
            status_code=400,
        )

    try:
        report_data = service.generate_report(
            report_type=report_type,
            subject_id=subject_id,
            parameters=parameters,
            is_auditor=is_auditor,
        )
        exported = service.export_report(report_data, export_format=export_format)
        filename_base = f"civiclens_{report_type}_{subject_id}"
        return _format_download_response(exported, export_format, filename_base, as_attachment=True)
    except ValueError as ve:
        logger.warning(f"Validation error exporting report: {ve}")
        return error_response(str(ve), status_code=400)
    except Exception as exc:
        logger.error(f"Error exporting report: {exc}", exc_info=True)
        return error_response(f"Internal error exporting report: {exc}", status_code=500)
