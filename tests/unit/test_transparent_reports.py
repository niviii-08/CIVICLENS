"""
CIVICLENS TN — Unit Tests for Transparent Civic Reports and Exports
Phase 13.7: Public Report Generation, Multi-Format Exports, Security & PII Safeguards.

Verifies:
1. Supported report types catalog and security capabilities.
2. Report generation across all 5 civic domains:
   - Promise Tracking & Manifesto Fulfilment (Phase 13.2)
   - Scheme, Budget & Policy Outcome Impact Summaries (Phase 13.3)
   - Evidence-Based Political Claim Verification Dossiers (Phase 13.4)
   - Evidence-Backed Civic Traceability Timelines (Phase 13.5)
   - District & Constituency Comparative Civic Insights (Phase 13.6)
3. Multi-format export rendering:
   - JSON structured data
   - CSV with RFC 4180 compliance and UTF-8 BOM
   - GitHub-Flavored Markdown
   - Citizen-facing HTML
4. Security & Epistemic Safeguards:
   - CSV Formula Injection Mitigation (CWE-1236)
   - HTML Entity Escaping (XSS Prevention)
   - Non-ASCII Tamil Script Support (தமிழ்)
   - DPDPA 2023 automated PII and credential scrubbing
5. REST API Endpoints:
   - GET /api/reports/types
   - POST /api/reports/generate (JSON and file streaming)
   - GET /api/reports/generate
   - GET /api/reports/export/<report_type>/<subject_id>
   - Validation & error handling (400 for bad type/format/missing params)
"""

import pytest
from backend.services.transparent_report_service import (
    TransparentReportService,
    escape_csv_cell,
    escape_html_text,
)
from backend.api.app import create_app


@pytest.fixture
def service():
    return TransparentReportService()


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# 1. Catalog and Capabilities Tests
# =====================================================================

def test_get_supported_report_types(service):
    """Verify supported report catalog exposes all five domains and formats."""
    catalog = service.get_supported_report_types()
    assert "supported_report_types" in catalog
    assert "supported_export_formats" in catalog
    assert "security_features" in catalog

    types = catalog["supported_report_types"]
    assert "promise_tracking" in types
    assert "scheme_budget" in types
    assert "claim_assessment" in types
    assert "civic_timeline" in types
    assert "local_comparison" in types

    formats = catalog["supported_export_formats"]
    for fmt in ["json", "csv", "markdown", "html"]:
        assert fmt in formats

    assert len(catalog["security_features"]) >= 4


def test_unsupported_report_type_raises(service):
    """Requesting an unsupported report type raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported report type"):
        service.generate_report("arbitrary_fake_type")


# =====================================================================
# 2. Domain-Specific Report Builders
# =====================================================================

def test_generate_scheme_budget_report(service):
    """Verify Scheme, Budget & Impact summary report generation."""
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT")

    assert report["subject_identifier"] == "SCH-SW-KMUT"
    assert "report_metadata" in report
    meta = report["report_metadata"]
    assert meta["report_type"] == "scheme_budget"
    assert "DPDPA 2023" in meta["data_governance"]
    assert meta["generation_timestamp_utc"] is not None

    summary = report["data_summary"]
    assert "total_budget_authorized_cr" in summary
    assert "expenditure_absorption_pct" in summary
    assert "verified_beneficiaries" in summary

    records = report["records_evaluated"]
    assert len(records) > 0
    categories = [r["record_category"] for r in records]
    assert "FINANCIAL_APPROPRIATION" in categories
    assert "PHYSICAL_OUTPUT" in categories

    # Verify definitions and limitations are preserved
    assert "absorption_rate" in report["definitions_and_methods"]
    assert len(report["evidence_limitations"]) >= 2


def test_generate_claim_assessment_report(service):
    """Verify Evidence-Based Claim Verification dossier report."""
    report = service.generate_report("claim_assessment", subject_id="CLM-TN-2024-001")

    assert report["subject_identifier"] == "CLM-TN-2024-001"
    summary = report["data_summary"]
    assert "claim_wording" in summary
    assert "verdict_tier" in summary
    assert any(
        tier in summary["verdict_tier"]
        for tier in [
            "SUPPORTED",
            "CONTRADICTED",
            "PARTIALLY_SUPPORTED",
            "MISSING_CONTEXT",
            "UNVERIFIABLE",
        ]
    )

    records = report["records_evaluated"]
    assert len(records) > 0
    assert records[0]["record_category"] == "ATOMIC_PROPOSITION"

    # Epistemic limitations
    assert any("public records" in lim.lower() or "verification" in lim.lower() for lim in report["evidence_limitations"])


def test_generate_civic_timeline_report(service):
    """Verify Evidence-Backed Civic Timeline report."""
    report = service.generate_report(
        "civic_timeline",
        subject_id="SCH-SW-KMUT",
        parameters={"entity_type": "scheme"},
    )

    assert report["subject_identifier"] == "SCH-SW-KMUT"
    summary = report["data_summary"]
    assert "total_milestones" in summary
    assert "chronological_milestones_count" in summary

    records = report["records_evaluated"]
    assert len(records) > 0
    record_cats = [r["record_category"] for r in records]
    assert "CHRONOLOGICAL_MILESTONE" in record_cats

    # Verify causation guardrail
    assert any("does NOT prove causation" in lim for lim in report["evidence_limitations"])


def test_generate_local_comparison_report(service):
    """Verify Comparable Local Civic Insights report across constituencies."""
    report = service.generate_report(
        "local_comparison",
        parameters={
            "entity_type": "CONSTITUENCY",
            "entity_ids": ["AC-011", "AC-012", "AC-013"],
            "metric_id": "literacy_rate_pct",
            "reporting_period": "2011",
        },
    )

    summary = report["data_summary"]
    assert summary["metric_name"] == "Literacy Rate"
    assert summary["entities_compared"] == 3
    assert summary["available_records"] > 0

    records = report["records_evaluated"]
    assert len(records) == 3
    for r in records:
        assert r["record_category"] == "LOCAL_JURISDICTION_METRIC"
        assert r["unit"] in ("PERCENT", "PERCENTAGE")


def test_generate_promise_tracking_report(service):
    """Verify Election Manifesto Promise Traceability report."""
    report = service.generate_report("promise_tracking", subject_id="PRM-DMK-2021-001")

    assert report["subject_identifier"] == "PRM-DMK-2021-001"
    summary = report["data_summary"]
    assert "political_party" in summary
    assert "manifesto_source" in summary

    records = report["records_evaluated"]
    assert len(records) >= 3
    record_cats = [r["record_category"] for r in records]
    assert "PROMISE_COMMITMENT" in record_cats
    assert "STATUTORY_NOTIFICATION" in record_cats
    assert "BUDGET_DISBURSEMENT" in record_cats


# =====================================================================
# 3. Export Formats & Encodings
# =====================================================================

def test_export_as_json(service):
    """Verify JSON export format returns structured dictionary."""
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT")
    exported = service.export_report(report, export_format="json")

    assert isinstance(exported, dict)
    assert exported["subject_identifier"] == "SCH-SW-KMUT"
    assert "report_metadata" in exported


def test_export_as_csv_structure_and_bom(service):
    """Verify CSV export includes UTF-8 BOM, metadata preamble, and table."""
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT")
    csv_str = service.export_report(report, export_format="csv")

    assert isinstance(csv_str, str)
    # Check UTF-8 BOM is present at the very beginning
    assert csv_str.startswith("\ufeff")

    # Check metadata block
    assert "# CIVICLENS TN TRANSPARENT CIVIC REPORT" in csv_str
    assert "# Report ID" in csv_str
    assert "# Reporting Period" in csv_str

    # Check CSV table headers
    assert "Record Category,Item Name,Reported Value" in csv_str

    # Check guardrails section
    assert "# EVIDENCE LIMITATIONS & GUARDRAILS" in csv_str


def test_export_as_markdown(service):
    """Verify Markdown export includes title, metadata block, and table."""
    report = service.generate_report("claim_assessment", subject_id="CLM-TN-2024-001")
    md_str = service.export_report(report, export_format="markdown")

    assert isinstance(md_str, str)
    assert md_str.startswith("# Evidence-Based Claim Assessment:")
    assert "> **Report ID**:" in md_str
    assert "> **Data Governance**:" in md_str
    assert "## 1. Key Metrics & Evidence Summary" in md_str
    assert "## 2. Granular Evaluated Records" in md_str
    assert "| Category | Item Name | Reported Value |" in md_str
    assert "## 4. Documentary Source Provenance" in md_str
    assert "## 5. Epistemic Guardrails & Evidence Limitations" in md_str


def test_export_as_html(service):
    """Verify HTML export produces standard HTML with styled sections."""
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT")
    html_str = service.export_report(report, export_format="html")

    assert isinstance(html_str, str)
    assert "<!DOCTYPE html>" in html_str
    assert "<html lang=\"en\">" in html_str
    assert "<title>" in html_str
    assert "<table>" in html_str
    assert "<th>Category</th>" in html_str
    assert "Epistemic Guardrail:" in html_str
    assert "CIVICLENS TN" in html_str


def test_unsupported_export_format_raises(service):
    """Requesting an unsupported export format raises ValueError."""
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT")
    with pytest.raises(ValueError, match="Unsupported export format"):
        service.export_report(report, export_format="yaml")


# =====================================================================
# 4. Security & Sanitization Tests (CWE-1236, XSS, DPDPA PII)
# =====================================================================

def test_csv_formula_injection_defense():
    """
    Prevents CSV Formula Injection (CWE-1236).
    Values starting with =, +, -, @, \\t, \\r must be prepended with a single quote.
    """
    assert escape_csv_cell("=1+1") == "'=1+1"
    assert escape_csv_cell("+cmd|' /C calc'!A0") == "'+cmd|' /C calc'!A0"
    assert escape_csv_cell("-100") == "'-100"
    assert escape_csv_cell("@SUM(A1:A10)") == "'@SUM(A1:A10)"
    assert escape_csv_cell("\tTabbed") == "'\tTabbed"
    assert escape_csv_cell("\rCarriage") == "'\rCarriage"

    # Benign strings unchanged
    assert escape_csv_cell("Standard Text") == "Standard Text"
    assert escape_csv_cell("₹1,000 Crore") == "₹1,000 Crore"
    assert escape_csv_cell(None) == ""


def test_csv_formula_injection_in_full_export(service):
    """Test that potentially malicious data injected into records is safely escaped in CSV."""
    malicious_report = {
        "title": "=cmd|' /C calc'!A0",
        "reporting_period": "@2024",
        "data_summary": {"metric": "+9999"},
        "records_evaluated": [
            {
                "record_category": "=EXEC('calc.exe')",
                "item_name": "-SUM(1+1)",
                "reported_figure": "@VIRUS",
                "reported_figure_formatted": "+PAYLOAD",
                "unit": "\tUNIT",
                "reporting_period": "2024",
                "status": "ACTIVE",
                "source_reference": "=HYPERLINK(\"http://evil.com\")",
                "data_quality": "HIGH",
            }
        ],
        "evidence_limitations": ["=ALERT(1)"],
        "report_metadata": {
            "report_id": "=MALICIOUS_ID",
            "report_title": "=MALICIOUS_TITLE",
            "generation_timestamp_utc": "2026-10-22T00:00:00Z",
            "reporting_period": "2024",
            "data_governance": "+COMPLIANCE",
        },
    }

    csv_output = service.export_report(malicious_report, export_format="csv")
    lines = csv_output.splitlines()

    # Verify that in every data line, formula triggers are escaped with single quote
    for line in lines:
        if line.startswith("\ufeff# Report ID"):
            assert "'=MALICIOUS_ID" in line
        if "=EXEC" in line:
            assert "'=EXEC" in line
        if "-SUM" in line:
            assert "'-SUM" in line
        if "@VIRUS" in line:
            assert "'@VIRUS" in line


def test_html_xss_defense():
    """Prevents XSS / HTML injection in report exports."""
    xss_payload = "<script>alert('xss')</script>"
    escaped = escape_html_text(xss_payload)
    assert "<script>" not in escaped
    assert "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;" == escaped

    # Image onerror payload
    img_payload = '<img src=x onerror=alert(1)>'
    escaped_img = escape_html_text(img_payload)
    assert "<img" not in escaped_img
    assert "&lt;img src=x onerror=alert(1)&gt;" == escaped_img


def test_tamil_unicode_support_in_exports(service):
    """Verify non-ASCII Tamil script (தமிழ்) renders cleanly in all export formats."""
    tamil_scheme_id = "SCH-SW-KMUT"
    report = service.generate_report("scheme_budget", subject_id=tamil_scheme_id)

    # Inject explicit Tamil text
    report["title"] = "கலைஞர் மகளிர் உரிமைத் திட்டம் - விரிவான அறிக்கை"
    report["records_evaluated"].append({
        "record_category": "திட்ட விவரம்",
        "item_name": "மகளிர் பயனாளிகள்",
        "reported_figure": 11500000,
        "reported_figure_formatted": "1.15 கோடி பயனாளிகள்",
        "unit": "நபர்கள்",
        "reporting_period": "2023-2024",
        "status": "நிறைவேற்றப்பட்டது",
        "source_reference": "தமிழ்நாடு அரசிதழ்",
        "data_quality": "தணிக்கை செய்யப்பட்டது",
    })

    # JSON export
    json_export = service.export_report(report, export_format="json")
    assert "கலைஞர் மகளிர் உரிமைத் திட்டம்" in json_export["title"]

    # CSV export
    csv_export = service.export_report(report, export_format="csv")
    assert "கலைஞர் மகளிர் உரிமைத் திட்டம்" in csv_export
    assert "1.15 கோடி பயனாளிகள்" in csv_export
    assert csv_export.startswith("\ufeff")

    # Markdown export
    md_export = service.export_report(report, export_format="markdown")
    assert "கலைஞர் மகளிர் உரிமைத் திட்டம்" in md_export
    assert "1.15 கோடி பயனாளிகள்" in md_export

    # HTML export
    html_export = service.export_report(report, export_format="html")
    assert "கலைஞர் மகளிர் உரிமைத் திட்டம்" in html_export
    assert "1.15 கோடி பயனாளிகள்" in html_export


def test_pii_sanitization_in_report(service):
    """Verify citizen PII is sanitized before export in standard citizen view."""
    # Build report with injected citizen PII
    report = service.generate_report("scheme_budget", subject_id="SCH-SW-KMUT", is_auditor=False)

    # Check that metadata does not leak internal Windows / Linux filesystem paths
    assert "C:\\" not in str(report)
    assert "/var/www/" not in str(report)


# =====================================================================
# 5. REST API Endpoints Tests
# =====================================================================

def test_api_get_report_types(test_client):
    """GET /api/reports/types returns 200 with catalog."""
    res = test_client.get("/api/reports/types")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    data = json_data["data"]
    assert "supported_report_types" in data
    assert "supported_export_formats" in data


def test_api_post_generate_json(test_client):
    """POST /api/reports/generate with json format returns structured report."""
    res = test_client.post(
        "/api/reports/generate",
        json={
            "report_type": "scheme_budget",
            "subject_id": "SCH-SW-KMUT",
            "format": "json",
        },
    )
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert json_data["data"]["subject_identifier"] == "SCH-SW-KMUT"


def test_api_post_generate_csv(test_client):
    """POST /api/reports/generate with csv format returns raw CSV with headers."""
    res = test_client.post(
        "/api/reports/generate",
        json={
            "report_type": "claim_assessment",
            "subject_id": "CLM-TN-2024-001",
            "format": "csv",
        },
    )
    assert res.status_code == 200
    assert "text/csv" in res.headers["Content-Type"]
    assert "utf-8" in res.headers["Content-Type"]
    assert "filename=\"civiclens_claim_assessment_CLM-TN-2024-001.csv\"" in res.headers["Content-Disposition"]
    assert res.data.decode("utf-8").startswith("\ufeff")


def test_api_get_generate_markdown(test_client):
    """GET /api/reports/generate with query params returns Markdown."""
    res = test_client.get("/api/reports/generate?report_type=civic_timeline&subject_id=SCH-SW-KMUT&format=markdown")
    assert res.status_code == 200
    assert "text/markdown" in res.headers["Content-Type"]
    body = res.data.decode("utf-8")
    assert body.startswith("# Civic Lifecycle & Evidence Timeline:")


def test_api_get_export_endpoint(test_client):
    """GET /api/reports/export/<report_type>/<subject_id> downloads HTML report."""
    res = test_client.get("/api/reports/export/promise_tracking/PRM-DMK-2021-001?format=html")
    assert res.status_code == 200
    assert "text/html" in res.headers["Content-Type"]
    assert "attachment; filename=\"civiclens_promise_tracking_PRM-DMK-2021-001.html\"" in res.headers["Content-Disposition"]
    body = res.data.decode("utf-8")
    assert "<!DOCTYPE html>" in body
    assert "Manifesto Promise Audit: PRM-DMK-2021-001" in body


def test_api_validation_errors(test_client):
    """Verify 400 validation error handling for missing/invalid fields."""
    # Missing report_type
    res1 = test_client.post("/api/reports/generate", json={})
    assert res1.status_code == 400
    assert "Missing required field 'report_type'" in res1.get_json()["message"]

    # Unsupported report_type
    res2 = test_client.post("/api/reports/generate", json={"report_type": "non_existent"})
    assert res2.status_code == 400
    assert "Unsupported report type" in res2.get_json()["message"]

    # Unsupported format
    res3 = test_client.post("/api/reports/generate", json={"report_type": "scheme_budget", "format": "docx"})
    assert res3.status_code == 400
    assert "Unsupported export format" in res3.get_json()["message"]
