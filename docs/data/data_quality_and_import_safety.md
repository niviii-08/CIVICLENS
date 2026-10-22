# Civic Data Quality, Validation & Import Safety Architecture

**CIVICLENS TN Data Pipeline Documentation**  
**Component:** Data Quality Engine, Ingestion Hardening, and Import Safety Framework  
**Target System:** CIVICLENS TN (`backend/ingestion/data_quality.py`, `backend/ingestion/validator.py`)  
**Source Registry Ref:** `docs/data/verified_source_registry.md`  
**Test Suites:** `tests/test_budget_validation.py`, `tests/unit/test_data_quality_and_import_safety.py`

---

## 1. Executive Summary

The integrity of a civic intelligence platform depends entirely on documentary authenticity, schema precision, and safe ingestion practices. Public records from government departments, statutory gazettes, election bodies, and constitutional audits must be validated against objective structural and semantic standards before entry into the system.

The **CIVICLENS TN Data Quality & Ingestion Hardening Engine** establishes unified, automated safeguards across all ingestion pipelines:
1. **Zero Data Fabrication:** Missing mandatory fields trigger explicit rejection; placeholder or dummy values are never generated.
2. **Non-Coercion of Missing Values:** `None` represents uncollected or undisclosed public data and is never coerced to `0.0`; `0.0` represents an empirical zero expenditure or zero beneficiary count.
3. **Historical Version Preservation (Rule 1):** Records are never deleted simply because they share an entity identifier; distinct election terms, delimitation cycles, and conflicting source reports are recognized and preserved.
4. **Overwrite Protection (Rule 2):** Ingestion pipelines never silently overwrite human-audited or newer verified data with older imported values.
5. **Secret & Sensitive Data Masking:** Error reporting automatically scrubs database connection strings, passwords, API keys, and auth tokens, guaranteeing zero credential leakage in logs or public interfaces.
6. **Transactional Safety & Dry-Run:** Ingestion routines support dry-run simulation, pre-import backup snapshots, and transactional rollback savepoints.

---

## 2. Schema & Required-Field Validation Architecture

The engine enforces entity-specific required schemas across all core civic domains:

| Entity Type | Mandatory Required Fields | Rejection Error Code | Anti-Fabrication Guarantee |
|:---|:---|:---|:---|
| **`representative`** | `representative_id`, `name`, `representative_type` | `SCHEMA_VALIDATION_ERROR` | Rejects records with empty names or missing offices without generating synthetic representatives. |
| **`constituency`** | `constituency_id`, `name`, `constituency_type`, `district_id` | `SCHEMA_VALIDATION_ERROR` | Rejects unassigned or floating constituencies. |
| **`department`** | `code`, `name` | `SCHEMA_VALIDATION_ERROR` | Requires canonical code and departmental name. |
| **`scheme`** | `scheme_code`, `name`, `department_id` | `SCHEMA_VALIDATION_ERROR` | Prevents orphaned schemes without issuing ministry/department. |
| **`budget_record`** | `financial_year`, `budget_stage`, `department_name`, `scheme_name` | `SCHEMA_VALIDATION_ERROR` | Preserves accounting stage and fiscal year linkage. |
| **`promise`** | `promise_id`, `party_id`, `promise_text`, `election_year` | `SCHEMA_VALIDATION_ERROR` | Rejects unattributed or dateless manifesto promises. |
| **`claim`** | `claim_id`, `claim_text`, `claim_type` | `SCHEMA_VALIDATION_ERROR` | Requires explicit statement text and claim classification. |
| **`document`** | `document_id`, `title`, `source_url`, `source_tier` | `SCHEMA_VALIDATION_ERROR` | Requires formal title, provenance URL, and credibility tier. |
| **`timeline_milestone`**| `milestone_id`, `title`, `event_type`, `date_semantics` | `SCHEMA_VALIDATION_ERROR` | Requires substantive title, event classification, and date dimensions. |

---

## 3. Source URL, Provenance & Domain Whitelisting

Every candidate URL is validated through `SourceProvenanceValidator.validate_url(...)` against structural, protocol, and domain security standards:

```
+----------------------------------------------------------------------------------------------------+
|                                    Source URL Protocol Hierarchy                                   |
+-------------------+----------------------------+---------------------------------------------------+
| Protocol / Scheme | Status                     | Operational Action                                |
+-------------------+----------------------------+---------------------------------------------------+
| https://, http:// | Permitted                  | Proceed to domain verification and path parsing.   |
| javascript:       | Strictly Disallowed        | Immediate rejection (Security violation).         |
| file://, ftp://   | Strictly Disallowed        | Immediate rejection (Local filesystem bypass).    |
| data:, blob:      | Strictly Disallowed        | Immediate rejection (Unanchored payload).         |
+-------------------+----------------------------+---------------------------------------------------+
```

### Whitelisted Civic Domains:
- **Tamil Nadu State Portals:** `tn.gov.in`, `tnelection.tn.gov.in`, `tnbudget.tn.gov.in`, `assembly.tn.gov.in`, `des.tn.gov.in`, `dipr.tn.gov.in`, `elections.tn.gov.in`, `chennaicorporation.gov.in`.
- **Constitutional & National Authorities:** `eci.gov.in`, `results.eci.gov.in`, `cag.gov.in`, `data.gov.in`, `sansad.in`, `pib.gov.in`, `lgdirectory.gov.in`, `censusindia.gov.in`, `rbi.org.in`, `prsindia.org`.
- **Accredited Independent Fact-Checkers (IFCN):** `altnews.in`, `boomlive.in`, `factly.in`, `vishvasnews.com`, `thelogicalindian.com`.
- **Mainstream Civic Journalism:** `thehindu.com`, `timesofindia.indiatimes.com`, `dinamalar.com`, `dailythanthi.com`, `newindianexpress.com`, `hindutamil.in`.
- **Political Party Manifesto Archives:** `dmk.in`, `aiadmk.com`.

*Note:* Structurally valid URLs from unwhitelisted domains are not immediately dropped, but are flagged with `UNVERIFIED_SOURCE_DOMAIN` and routed to `review_required` for human auditor clearance.

---

## 4. Duplicate Detection & Stable External Identifiers (Rule 1)

In civic datasets, identical entity identifiers do not necessarily represent data duplication. The engine classifies record relationships into four distinct states:

```
                                  Incoming Civic Record
                                            │
                                ┌───────────┴───────────┐
                       Same Entity ID?           New Entity ID?
                                │                       │
                     ┌──────────┴──────────┐      Unique Record
                     │                     │       (INSERTED)
             Same Time Period?      Different Period?
                     │                     │
           ┌─────────┴─────────┐     Historical Version
     Same Source?      Different   (Preserved as Distinct)
           │            Source?
     ┌─────┴─────┐         │
  Same     Modified   Conflicting
Payload?   Payload?     Source
    │         │       (Preserved &
  Exact    Updated     Flagged for
Duplicate  Record        Review)
 (SKIPPED) (UPDATED)
```

1. **`EXACT_DUPLICATE`:** Same entity, same time period, same source, and identical data payload -> Skipped safely without creating redundant rows.
2. **`HISTORICAL_VERSION`:** Same representative elected across multiple assembly terms (e.g., 2016 vs. 2021), or constituency boundaries under Delimitation 1971 vs. 2008 -> Preserved as independent, valid historical records.
3. **`CONFLICTING_SOURCE`:** Same entity and fiscal year, but divergent figures reported (e.g., Department Policy Note reports ₹1,500 Cr expenditure; CAG Audit Report reports ₹1,420.5 Cr) -> Preserved with source attribution and flagged as `SOURCE_CONFLICT_DETECTED`.
4. **`SUPERSEDED_ORDER`:** Administrative draft (e.g., G.O. 22) formally replaced by subsequent guidelines (e.g., G.O. 34) -> Retained in historical sequence with `is_superseded=True` and `superseded_by` documentation.

### Canonical Identifier Formatting:
Stable external identifiers are validated against strict regex standards:
- Assembly Constituencies: `^AC-TN-\d{3}$` (e.g., `AC-TN-044`)
- Parliamentary Constituencies: `^PC-TN-\d{2}$` (e.g., `PC-TN-02`)
- Schemes: `^SCH-([A-Z0-9]+-)*[A-Z0-9]+$` (e.g., `SCH-TN-PUDHUMAI`)
- Promises: `^PRM-[A-Z0-9]+-\d{4}-\d{3}$` (e.g., `PRM-DMK-2021-001`)
- Documents: `^(DOC|SRC)-[A-Z0-9-]+$` (e.g., `DOC-GO-MS-34-SW-2022`)
- Civic Issues: `^CIV-\d{4}-\d{4}$` (e.g., `CIV-2024-0891`)

---

## 5. Referential Integrity Validation

Cross-entity references are validated before ingestion commits to prevent orphaned or dangling records:
- **Representatives:** `constituency_id` and `party_id` must match registered entities.
- **Schemes:** `department_id` or `department_code` must match registered executive departments.
- **Budget Records:** `head_of_account` / `scheme_code` and `source_document_id` must match registered schemes and documents.
- **Promises:** `party_id` must resolve to recognized political parties.
- **Claims:** `evidence_document_id` must resolve to registered evidence documents.

If a referential target is missing, the engine records `REFERENTIAL_INTEGRITY_VIOLATION` and routes the record to `review_required`, preventing silent foreign key breakage.

---

## 6. Multi-Domain Consistency Validation

### Date & Chronological Sanity:
- Adheres strictly to ISO-8601: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`.
- Rejects non-existent calendar dates (e.g. `2023-02-31`).
- Enforces chronological sequence: `announcement_date <= event_date <= publication_date` (and `audit_date >= event_date`).

### Financial Year Consistency:
- Standard formats: `YYYY-YY` (e.g. `2023-24`) or `YYYY-YYYY` (e.g. `2023-2024`).
- Enforces consecutive-year logic: `2023-24` is valid; `2023-25` is rejected as non-consecutive.

### Currency & Unit Multipliers:
- Currency is strictly standardized to Indian Rupees (`INR`).
- Validated multipliers:
  - `INR_Crores` / `Crores`: $\times 10^7$
  - `INR_Lakhs` / `Lakhs`: $\times 10^5$
  - `INR_Thousands` / `Thousands`: $\times 10^3$
  - `INR_Absolute` / `Absolute`: $\times 1.0$

### Missing vs. Zero Disambiguation:
- `None` is preserved as missing / undisclosed data.
- `0.0` is recognized as an empirical zero (zero expenditure, zero beneficiaries).
- String tokens (`"-"`, `"N/A"`, `"null"`, `"None"`) are parsed as `None`, preventing accidental coercion to zero.

### Tamil Nadu Geographic Consistency:
- **Districts:** Validated against the 38 official revenue districts of Tamil Nadu (Ariyalur, Chengalpattu, Chennai, Coimbatore, Cuddalore, Dharmapuri, Dindigul, Erode, Kallakurichi, Kancheepuram, Kanniyakumari, Karur, Krishnagiri, Madurai, Mayiladuthurai, Nagapattinam, Namakkal, Nilgiris, Perambalur, Pudukkottai, Ramanathapuram, Ranipet, Salem, Sivaganga, Tenkasi, Thanjavur, Theni, Thoothukudi, Tiruchirappalli, Tirunelveli, Tirupathur, Tiruppur, Tiruvallur, Tiruvannamalai, Tiruvarur, Vellore, Viluppuram, Virudhunagar).
- **Assembly Constituencies:** Numbered $1$ through $234$.
- **Municipal Zones:** Greater Chennai Corporation (GCC) zones $1$ through $15$.
- **LGD Codes:** Must be valid positive numeric strings.

---

## 7. Unicode & Tamil Text Preservation

Civic data in Tamil Nadu is inherently bilingual. The `UnicodeTamilGuard` enforces:
1. **Authentic Tamil Script Preservation:** Correctly retains Tamil letters, vowel markers, and virama (`pulli`) within Unicode block `\u0B80`–`\u0BFF` (e.g. `தமிழ்நாடு`, `கலைஞர் மகளிர் உரிமைத் திட்டம்`, `புதுமைப் பெண்`).
2. **NFC Normalization:** Applies standard Unicode normalization (`unicodedata.normalize("NFC", ...)`) to eliminate rendering discrepancies across different input systems.
3. **Mojibake Detection:** Identifies double-encoded UTF-8 corruption (e.g., `ÃƒÂ`, `Ã‚Â`, `â€™`, `\ufffd`, `[\x80-\x9f]`) and rejects corrupted records before database insertion.

---

## 8. Overwrite Protection & Repeatable Imports (Rule 2)

Automated re-runs of ingestion pipelines must not damage manually verified records:
1. **Auditor Protection:** If an existing record has `is_manually_reviewed = True` or `review_status = "VERIFIED"`, the automated pipeline blocks updates (`MANUAL_REVIEW_PROTECTED`), marks the record as `skipped`, and routes the delta to `review_required`.
2. **Freshness Protection:** If the existing database record has a publication or modification date newer than the incoming import file, the pipeline prevents overwriting (`STALE_IMPORT_OVERWRITE_PREVENTED`).
3. **Idempotent Reruns:** Running the exact same dataset multiple times results in $0$ duplicate records and $0$ state changes, with all items classified under `skipped`.

---

## 9. Secret & Sensitive Data Scrubbing

Error messages, failure details, and audit reports are sanitized by `SecretScrubber` prior to logging:
- Database connection strings with credentials:
  `postgresql://user:password@host:5432/db` $\longrightarrow$ `postgresql://***:***@host:5432/db`
- API keys, secrets, and auth headers:
  `api_key='secret-token-abcdef'` $\longrightarrow$ `api_key=[REDACTED_SECRET]`
- Bearer tokens:
  `bearer eyJhbGci...` $\longrightarrow$ `bearer [REDACTED_SECRET]`
- JWT tokens:
  `eyJhbGciOi...` $\longrightarrow$ `[REDACTED_JWT]`

---

## 10. Safe Staging, Dry-Run, Rollback & Backup Procedures

1. **Dry-Run Mode (`dry_run=True`):**
   - Simulates the entire validation, deduplication, and transformation lifecycle.
   - Generates identical `ImportSummary` counts (`inserted`, `updated`, `skipped`, `rejected`, `review_required`) without committing transactions.
2. **Transactional Savepoint Rollback:**
   - Wraps batches inside SQLAlchemy nested transactions (`session.begin_nested()`).
   - On fatal schema corruption or unexpected exceptions, executes complete rollback to preserve database integrity.
3. **Pre-Import Backup Snapshot:**
   - Generates a timestamped backup manifest (`BKUP-<ENTITY>-<TIMESTAMP>`) capturing baseline row counts before non-dry-run bulk insertions.

---

## 11. Supported Tests & Actual Verification Results

Validation and import safety are verified by **16 unit tests** across two suites:

```
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-8.3.4, pluggy-1.6.0
rootdir: CIVCLENS-All features\CIVCLENS-All features\CIVCLENS
configfile: pytest.ini

tests/test_budget_validation.py (5 Tests):
  - test_valid_record .......................................... PASSED [  6%]
  - test_missing_required_fields ............................... PASSED [ 12%]
  - test_malformed_financial_year .............................. PASSED [ 18%]
  - test_null_amounts_handling ................................. PASSED [ 25%]
  - test_duplicate_detection_within_batch ....................... PASSED [ 31%]

tests/unit/test_data_quality_and_import_safety.py (11 Tests):
  - test_schema_required_fields_and_zero_fabrication ........... PASSED [ 37%]
  - test_source_url_and_provenance_validation .................. PASSED [ 43%]
  - test_duplicate_detection_historical_versions_and_conflicts . PASSED [ 50%]
  - test_external_identifier_format_validation ................. PASSED [ 56%]
  - test_referential_integrity_across_entities ................. PASSED [ 62%]
  - test_consistency_validation_date_fy_currency_geography ..... PASSED [ 68%]
  - test_missing_vs_zero_preservation .......................... PASSED [ 75%]
  - test_unicode_and_tamil_preservation ........................ PASSED [ 81%]
  - test_repeatable_imports_and_silent_overwrite_prevention .... PASSED [ 87%]
  - test_secret_scrubber_credential_masking .................... PASSED [ 93%]
  - test_safe_import_runner_dry_run_and_summary ................ PASSED [100%]

============================= 16 passed in 1.19s ==============================
```

**Outcome:** 16 passed, 0 failures, 100% test pass rate.
