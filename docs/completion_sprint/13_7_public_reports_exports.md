# CIVICLENS TN — Phase 13.7: Transparent Civic Reports and Exports

## 1. Executive Summary
Phase 13.7 delivers a comprehensive, citizen-accessible public reporting and export architecture for **CIVICLENS TN**. Citizens, journalists, and civic researchers can generate, review, and export verifiable public accountability reports directly from existing CIVICLENS TN records without introduction of unvetted third-party dependencies.

The reporting engine spans five core civic intelligence domains:
1. **Election Manifesto Promise Tracking Dossiers** (`promise_tracking`)
2. **Scheme, Budget Allocation & Policy Outcome Summaries** (`scheme_budget`)
3. **Evidence-Based Public Claim Verification Dossiers** (`claim_assessment`)
4. **Evidence-Backed Civic Traceability Timelines** (`civic_timeline`)
5. **District & Constituency Comparative Civic Insights** (`local_comparison`)

Every report enforces strict epistemic standards, source provenance, calculation formulas, and robust data-security safeguards including **Digital Personal Data Protection Act (DPDPA 2023)** compliance, **CSV Formula Injection (CWE-1236)** mitigation, and **HTML Entity Sanitization (XSS Defense)**.

---

## 2. Multi-Format Export Architecture

The platform supports four export formats, preserving complete semantic structure, source attribution, and epistemic guardrails across each:

| Format | MIME Type | File Extension | Encoding & Standards | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **JSON** | `application/json; charset=utf-8` | `.json` | RFC 8259, UTF-8, 2-space indented | Automated API ingestion, open-data pipelines, civic tech integrations |
| **CSV** | `text/csv; charset=utf-8` | `.csv` | RFC 4180, UTF-8 BOM (`\ufeff`), Formula Escaping | Spreadsheet analysis in Microsoft Excel, LibreOffice Calc, Google Sheets |
| **Markdown** | `text/markdown; charset=utf-8` | `.md` | GitHub-Flavored Markdown (GFM) | Open-source archiving, citizen journalism, GitHub repository audits |
| **HTML** | `text/html; charset=utf-8` | `.html` | HTML5, Responsive semantic styling, Entity Escaping | Standalone printable citizen dossiers, shareable offline web pages |

---

## 3. Supported Civic Analysis Report Domains

### 3.1. Scheme, Budget & Policy Outcome Impact Analysis (`scheme_budget`)
* **Underlying Engine:** [`backend.services.scheme_budget_impact_service.SchemeBudgetImpactService`](file:///backend/services/scheme_budget_impact_service.py)
* **Evaluated Records:**
  - `FINANCIAL_APPROPRIATION`: Legislative Budget Estimates (BE) and in-year Revised Estimates (RE).
  - `FINANCIAL_EXPENDITURE`: Final treasury disbursements audited by the Comptroller and Auditor General (CAG).
  - `PHYSICAL_OUTPUT`: Administrative progress milestones and direct beneficiaries registered.
  - `POLICY_OUTCOME`: Longitudinal survey indicators with baseline and follow-up values.
* **Preserved Metrics:** Total budget authorized (₹ Cr), actual expenditure (₹ Cr), absorption rate (%), verified beneficiary counts.
* **Epistemic Guardrails:** Explicit disclosure that budget allocation does not constitute actual cash disbursement and observed outcome trends do not prove sole causal attribution.

### 3.2. Evidence-Based Public Claim Verification Dossiers (`claim_assessment`)
* **Underlying Engine:** [`backend.services.claim_assessment_service.ClaimAssessmentService`](file:///backend/services/claim_assessment_service.py)
* **Evaluated Records:**
  - Atomic proposition decomposition of public statements.
  - Verification classification against CIVICLENS TN's 5-tier taxonomy:
    1. `SUPPORTED_BY_AVAILABLE_EVIDENCE`
    2. `CONTRADICTED_BY_AVAILABLE_EVIDENCE`
    3. `PARTIALLY_SUPPORTED`
    4. `MISSING_IMPORTANT_CONTEXT`
    5. `UNVERIFIABLE_OR_INSUFFICIENT_EVIDENCE`
* **Preserved Metrics:** Speaker attribution, statement date, corroborating and contradicting evidence counts, confidence score.
* **Epistemic Guardrails:** Strict non-prejudice rule: the absence of public government records is never equated with proof of falsehood.

### 3.3. Evidence-Backed Civic Traceability Timelines (`civic_timeline`)
* **Underlying Engine:** [`backend.services.civic_timeline_service.CivicTimelineService`](file:///backend/services/civic_timeline_service.py)
* **Evaluated Records:**
  - `CHRONOLOGICAL_MILESTONE`: Deterministically sorted date-bearing civic events.
  - `UNANCHORED_MILESTONE`: Undated records preserved without manufactured timestamps.
* **Preserved Metrics:** Event date semantics, publication dates, connection basis (direct identifier vs documented evidence).
* **Epistemic Guardrails:** Sequence is not causation: temporal sequence does not prove causal attribution.

### 3.4. District & Constituency Comparative Civic Insights (`local_comparison`)
* **Underlying Engine:** [`backend.services.local_civic_comparison_service.LocalCivicComparisonService`](file:///backend/services/local_civic_comparison_service.py)
* **Evaluated Records:**
  - Comparative metrics across compatible administrative tiers (Districts, Assembly Constituencies, Municipal Wards).
* **Preserved Metrics:** Metric name, verified unit, reporting period, available vs unavailable records.
* **Epistemic Guardrails:** Strict prohibition of arbitrary composite scores; zero values (0.0) are never conflated with missing data (`None`).

### 3.5. Election Manifesto Promise Traceability (`promise_tracking`)
* **Underlying Engine:** [`backend.models.promise.PoliticalPromise`](file:///backend/models/promise.py) and statutory gazette registries.
* **Evaluated Records:**
  - `PROMISE_COMMITMENT`: Manifesto electoral pledge.
  - `STATUTORY_NOTIFICATION`: Executive Government Orders (G.O.s) establishing policy framework.
  - `BUDGET_DISBURSEMENT`: State treasury DBT ledgers and verified beneficiary counts.
* **Preserved Metrics:** Party attribution, manifesto source, statutory G.O. references, fulfilment status.
* **Epistemic Guardrails:** Absence of evidence is not proof of non-implementation; status reflects verified public records at time of export.

---

## 4. Security, Privacy & Integrity Guardrails

### 4.1. DPDPA 2023 Compliance & Automated PII Scrubbing
All reports pass through [`backend.services.civic_search_service.sanitize_payload`](file:///backend/services/civic_search_service.py):
* Redacts citizen names, phone numbers (`\b[6-9]\d{9}\b`), email addresses, and Aadhaar identifiers (`\b\d{4}\s?\d{4}\s?\d{4}\b`).
* Scrubs internal server directories (`C:\...`, `/var/www/...`) and database connection strings to prevent server information leakage.
* Enforces role-based disclosure (`is_auditor=False` by default for citizen and public queries).

### 4.2. CSV Formula Injection Mitigation (CWE-1236)
Implemented in [`escape_csv_cell`](file:///backend/services/transparent_report_service.py):
* Spreadsheet software (Excel, LibreOffice Calc) can execute malicious shell commands if a cell starts with `=`, `+`, `-`, `@`, `\t`, or `\r`.
* All string values are checked: if a cell starts with a formula trigger character, it is prepended with a single quote (`'`), neutralizing executable expressions and forcing interpretation strictly as plain text.

### 4.3. HTML Entity Escaping (Cross-Site Scripting Defense)
Implemented in [`escape_html_text`](file:///backend/services/transparent_report_service.py):
* Prevents stored or reflected XSS attacks in generated standalone HTML reports.
* Converts untrusted characters to safe HTML entities:
  - `<` &rarr; `&lt;`
  - `>` &rarr; `&gt;`
  - `&` &rarr; `&amp;`
  - `"` &rarr; `&quot;`
  - `'` &rarr; `&#x27;`

### 4.4. Tamil Script & Non-ASCII Character Support (தமிழ்)
* In CSV exports, the output starts with an explicit **UTF-8 Byte Order Mark (`\ufeff`)**.
* Ensures non-ASCII characters, such as Tamil scheme names (`கலைஞர் மகளிர் உரிமைத் திட்டம்`) and units (`கோடி பயனாளிகள்`), display correctly in Excel and Calc without character corruption or mojibake.

---

## 5. REST API Specifications

The blueprint is registered at `/api/reports` in [`backend/api/routes.py`](file:///backend/api/routes.py):

| Endpoint | HTTP Method | Query / Body Params | Response / Headers | Description |
| :--- | :--- | :--- | :--- | :--- |
| `/api/reports/types` | `GET` | None | `200 OK` (JSON catalog) | Returns supported report types, export formats, and security capabilities. |
| `/api/reports/generate` | `POST` | `{"report_type": "...", "subject_id": "...", "format": "...", "parameters": {...}}` | `200 OK` (JSON or file stream) | Generates and exports a civic intelligence report. |
| `/api/reports/generate` | `GET` | `?report_type=...&subject_id=...&format=...` | `200 OK` (JSON or file stream) | Query-string report generation for citizen link sharing. |
| `/api/reports/export/<report_type>/<subject_id>` | `GET` | `?format=json\|csv\|markdown\|html` | `200 OK` with `Content-Disposition: attachment; filename="..."` | Standalone file download endpoint with proper MIME headers. |

### Error Codes
* `400 Bad Request`: Missing `report_type`, unsupported report type, or unsupported export format.
* `404 Not Found`: Target subject identifier not found in civic registry.
* `500 Internal Server Error`: Unhandled system exception (logged with request correlation ID).

---

## 6. Verification and Test Results

### 6.1. Unit Test Suite (`tests/unit/test_transparent_reports.py`)
Executed with Python 3.13:
```
pytest tests/unit/test_transparent_reports.py -v
```
Results:
```
============================= 23 passed in 4.02s ==============================
- test_get_supported_report_types: PASSED
- test_unsupported_report_type_raises: PASSED
- test_generate_scheme_budget_report: PASSED
- test_generate_claim_assessment_report: PASSED
- test_generate_civic_timeline_report: PASSED
- test_generate_local_comparison_report: PASSED
- test_generate_promise_tracking_report: PASSED
- test_export_as_json: PASSED
- test_export_as_csv_structure_and_bom: PASSED
- test_export_as_markdown: PASSED
- test_export_as_html: PASSED
- test_unsupported_export_format_raises: PASSED
- test_csv_formula_injection_defense: PASSED
- test_csv_formula_injection_in_full_export: PASSED
- test_html_xss_defense: PASSED
- test_tamil_unicode_support_in_exports: PASSED
- test_pii_sanitization_in_report: PASSED
- test_api_get_report_types: PASSED
- test_api_post_generate_json: PASSED
- test_api_post_generate_csv: PASSED
- test_api_get_generate_markdown: PASSED
- test_api_get_export_endpoint: PASSED
- test_api_validation_errors: PASSED
```

### 6.2. Frontend Type Integrity Check
```
npm run typecheck --prefix frontend
```
Results:
```
> civiclens-frontend@1.0.0 typecheck
> tsc --noEmit
Exit code: 0 (No type errors)
```

---

## 7. Epistemic Limitations & Future Enhancements

1. **Static Export Timestamps:**
   Exported reports capture a point-in-time snapshot. When underlying government gazettes or CAG audits are updated, exported offline files do not automatically refresh. The report header embeds an explicit generation timestamp (`generation_timestamp_utc`) to preserve temporal provenance.
2. **Zero vs Unavailable Data:**
   In local comparisons, missing departmental reports are explicitly rendered as `UNAVAILABLE` rather than `0.0`. This prevents unwarranted negative inferences about public service delivery.
3. **Correlation vs Causation:**
   All exported scheme and budget reports explicitly include the epistemic disclaimer that observed longitudinal changes represent empirical associations and cannot be interpreted as proven causal impacts without counterfactual econometric evaluations.
