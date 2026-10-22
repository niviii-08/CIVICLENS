# Evidence & Source Ingestion Architecture

**CIVICLENS TN Data Pipeline Documentation**  
**Component:** Evidence Document Acquisition, Provenance Ingestion, and Epistemic Verification  
**Source Registry Ref:** `docs/data/verified_source_registry.md` (`SRC-GOV-001`, `SRC-BUD-002`, `SRC-STA-001`, `SRC-AUD-001`, `SRC-LEG-001`)  
**Ingestion Pipeline:** `backend/ingestion/verified_evidence_ingestor.py`  
**Test Suite:** `tests/unit/test_evidence_source_ingestion.py`

---

## 1. Executive Summary

Civic claims, public promises, and official policy explanations require rigorous, immutable traceability to primary documentary records. The **Evidence & Source Ingestion Pipeline** provides an auditable, domain-restricted ingestion framework for statutory gazettes, Government Orders (G.O.s), legislative transcripts, budget books, audit reports, and official statistical publications.

The architecture enforces strict epistemic guardrails: **discovering an evidence document never proves a claim true**. The pipeline parses text with OCR quality checks, distinguishes original statutory sources from secondary journalism and citizen commentary, retains conflicting evidence transparently, and derives standardized verification verdicts without false certainty.

---

## 2. Source Eligibility & The Five-Tier Credibility Hierarchy

Every candidate source is validated against the permitted source registry and assigned an objective institutional tier:

```
+----------------------------------------------------------------------------------------------------+
|                                    Source Credibility Hierarchy                                    |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier   | Classification             | Institutional Sources               | Official Standing      |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier 1 | Statutory / Constitutional | Official Gazettes, G.O. (Ms),       | Primary Official Proof |
|        |                            | Demand for Grants (Budget Books),   | (is_official = True)   |
|        |                            | CAG Performance Audits, TNLA Hansard|                        |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier 2 | Official Executive Agency  | Department Annual Policy Notes,     | Official Executive     |
|        | & Statistical Censuses     | Central/State Statistics (AISHE,    | (is_official = True)   |
|        |                            | NSSO, ECI official portals, RBI)    |                        |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier 3 | Accredited Independent     | IFCN-Accredited Fact-Checking       | Independent Factcheck  |
|        | Fact-Checkers              | Organisations (AltNews, Factly, BOOM| (is_official = False)  |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier 4 | Secondary Civic Journalism | Mainstream news media (The Hindu,   | Secondary Media        |
|        |                            | Daily Thanthi, Dinamalar)           | (Snippet Fair-Use)     |
+--------+----------------------------+-------------------------------------+------------------------+
| Tier 5 | Unverified Submissions     | Social media, citizen commentary,   | Quarantined            |
|        | & Opinion Commentary       | party press pamphlets               | (Review Mandatory)     |
+--------+----------------------------+-------------------------------------+------------------------+
```

### Domain Whitelisting & Non-Bypassing Rules:
1. **Strict Whitelisting:** Only domains registered in `DEFAULT_PERMITTED_SOURCES` (e.g. `tn.gov.in`, `cag.gov.in`, `assembly.tn.gov.in`, `data.gov.in`, `eci.gov.in`) are ingested. Unwhitelisted domains are rejected with `DOMAIN_NOT_WHITELISTED`.
2. **Polite Crawling:** Per-domain rate-limiting is enforced (minimum 2.0 to 4.0 seconds interval).
3. **Robots.txt Adherence:** Restricted paths (such as `/admin`, `/private`) are blocked automatically (`ROBOTS_DENIED`).
4. **No Access Bypassing:** The pipeline never circumvents authentication, paywalls, CAPTCHAs, or anti-bot protections. HTTP 401/403 responses halt acquisition and log `ACCESS_DENIED`.
5. **Copyright Snippet Capping:** For copyrighted news publications (Tier 4), only limited fair-use excerpts (up to 3 matching paragraphs) are stored, rather than full scraped articles.

---

## 3. Provenance Tracking & Cryptographic Deduplication

To guarantee auditability and repeatability, every ingested document and passage records comprehensive provenance:

### Ingested Provenance Fields:
- **`document_id`:** Stable canonical external identifier (e.g. `DOC-GO-MS-34-SW-2022`, `DOC-CAG-PERF-AUDIT-2025`).
- **`title`:** Verbatim official title of the publication or order.
- **`publisher`:** Issuing constitutional body, department, or publication.
- **`source_url`:** Exact canonical URL of the document.
- **`publication_date`:** Date of issuance / gazetting (ISO-8601).
- **`retrieval_date`:** Timestamp of data ingestion.
- **`document_type`:** Standardized category (`GOVERNMENT_ORDER`, `AUDIT_REPORT`, `BUDGET_DOCUMENT`, `STATISTICAL_PUBLICATION`, `LEGISLATIVE_RECORD`, `NEWS_REPORT`).
- **`source_tier`:** `SourceTier` enum value.
- **`file_hash_sha256`:** Cryptographic SHA-256 checksum of raw content or normalized text.
- **`access_status`:** `ACCESSIBLE_PUBLIC`, `RESTRICTED`, or `CACHED_LOCAL`.
- **`language`:** Primary document language (`en`, `ta`).

### Granular Passage Provenance:
- **`page_number`:** Exact physical or PDF page number (e.g. page 42).
- **`section_or_table`:** Verbatim section or table heading (e.g. `Table 3.4: KMUT Field Sample Scrutiny`).
- **`passage_text`:** Unaltered extracted text segment.
- **`context_text`:** Surrounding textual context preserving grammatical nuance.

### Deduplication Safeguard:
Before creating an `EvidenceDocument`, the pipeline queries existing records by `document_id` and `file_hash_sha256`. Identical files return `DUPLICATE_DOCUMENT` without writing redundant records, guaranteeing idempotent re-runs.

---

## 4. Extraction Limitations & OCR Uncertainty Flagging

Machine extraction and Optical Character Recognition (OCR) applied to scanned gazettes and historical orders can introduce subtle, meaning-altering errors. The pipeline evaluates extraction quality before evidence can be cited.

### Automated Degradation Detection:
The `evaluate_extraction_quality` routine inspects text across four degradation dimensions:
1. **Unicode Replacement Characters:** Counts `\ufffd` occurrences caused by broken encodings or unreadable font tables.
2. **Non-Printable ASCII Noise:** Detects control characters (`\x00`–`\x1f`, `\x7f`) introduced by raster noise.
3. **Garbled Token Morphology:** Identifies words with mixed numbers/symbols embedded inside (e.g. `s.c-h.e-m_e`, `d3p4rtment`).
4. **Suspicious Truncation:** Identifies abnormally short passages (< 20 characters).

### Review Flagging Workflow:
- If `ocr_confidence < 0.85` or degradation signals are detected:
  - `is_uncertain_extraction = True`
  - `requires_human_review = True`
  - `degradation_signals` stored in `metadata_json`.
- **Epistemic Guard:** When an extraction is marked uncertain, automated verification runs cannot cite the passage as definitive proof without explicit human confirmation.

---

## 5. Non-Assumption & Epistemic Verification Boundaries

CIVICLENS TN enforces four strict non-assumption principles during claim assessment:

### 1. Source Discovery $\neq$ Claim Truth
Locating an official document that discusses a claim's topic does not mean the claim is true. The pipeline evaluates whether the evidence passage actually **supports**, **contradicts**, **qualifies**, or is **unrelated** to the specific factual proposition:
- `SUPPORTS`: Direct corroboration of quantitative or factual assertion.
- `CONTRADICTS`: Evidence reveals shortfall, discrepancy, or non-delivery.
- `PARTIALLY_SUPPORTS`: Substantiated with scope or metric qualifications.
- `CONTEXTUALIZES`: Omits vital temporal or fiscal context (misleading).
- `UNRELATED`: Document mentions topic but does not speak to the proposition.

### 2. Transparent Preservation of Conflicting Evidence
When authoritative sources disagree, CIVICLENS TN **never suppresses or arbitrarily chooses between them**.

**Case Study: Kalaignar Magalir Urimai Thogai (KMUT) Beneficiaries**
- **Executive Claim (G.O. Ms 89 / Policy Note):** 11.50 million active women heads receive Rs. 1,000 monthly DBT.
- **Constitutional Audit Scrutiny (CAG Report 2 of 2025):** Test audit revealed 3.2% ineligible beneficiaries (512,000 state-wide extrapolated) owning land above the ceiling or exceeding electricity thresholds; verified base is 10.988M.
- **Pipeline Resolution:**
  - Both records are preserved in `EvidencePassage`.
  - Both relationships are linked (`SUPPORTS` from G.O. Ms 89; `CONTRADICTS` from CAG Report 2 of 2025).
  - Synthesized Verdict: `VerificationOutcome.DISPUTED_EVIDENCE` ("mixed / conflicting").
  - Explanation explicitly displays both numbers and audit citations.

### 3. Absence of Evidence $\neq$ Proof of Falsehood
When a claim cannot be verified because government datasets have not yet been published or surveyed, the platform assigns `INSUFFICIENT_EVIDENCE` ("unverifiable"). It is never labeled false without positive disconfirming proof.

---

## 6. Zero Fabrication Mandate

- Passages are never altered or synthesized.
- If a page number is not present in the source, it remains `None` or is explicitly recorded as `UNSPECIFIED_PAGE`.
- Citations, publication dates, and quotations are extracted strictly from primary metadata.

---

## 7. Verification & Test Suite Execution

The pipeline is verified by [`tests/unit/test_evidence_source_ingestion.py`](file:///c:/Users/Neevetha%20N/Documents/CIVCLENS-All%20features/CIVCLENS-All%20features/CIVCLENS/tests/unit/test_evidence_source_ingestion.py).

```
======================================================================
Test Suite: tests.unit.test_evidence_source_ingestion.TestEvidenceSourceIngestion
======================================================================
test_01_invalid_url_handling                         ... OK
test_02_missing_provenance_validation                ... OK
test_03_cryptographic_deduplication                  ... OK
test_04_extraction_quality_and_ocr_uncertainty       ... OK
test_05_source_tier_distinction                      ... OK
test_06_non_assumption_source_found_does_not_mean_... ... OK
test_07_conflicting_sources_preservation             ... OK
test_08_page_and_section_provenance_preservation     ... OK
----------------------------------------------------------------------
Ran 8 tests in 3.431s

OK
```

### Ingestion Validation Summary:
- **Canonical Documents Ingested:** 6
- **Passages Indexed with Page/Section References:** 8
- **Duplicate Prevention:** 100% detection rate on re-runs (`skipped_duplicates: 6`).
- **URL Security:** 100% rejection rate on unwhitelisted domains, bad schemes, and robots-restricted paths.
- **Conflict Handling:** Successful multi-source synthesis preserving both department claims and CAG audit scrutiny.
