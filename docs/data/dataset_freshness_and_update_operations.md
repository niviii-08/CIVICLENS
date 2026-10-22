# Civic Dataset Freshness & Update Operations

**CIVICLENS TN Operations & Data Reliability Documentation**  
**Component:** Dataset Freshness Monitoring, Ingestion Diagnostics & Update Management  
**Source Registry Ref:** `docs/data/verified_source_registry.md` (`SRC-BUD-001` through `SRC-GOV-002`)  
**Core Modules:** `backend/ops/freshness_manager.py`, `backend/api/freshness.py`, `backend/ingestion/data_quality.py`  
**Test Suites:** `tests/unit/test_dataset_freshness_operations.py`, `tests/unit/test_data_quality_and_import_safety.py`

---

## 1. Executive Summary

Public governance datasets across Tamil Nadu do not adhere to uniform or daily publication cadences. State budget books and CAG audit reports are released once annually during legislative sessions; legislative transcripts are tabled on a sessional basis; statutory gazettes appear weekly; and election results update every five years.

The **CIVICLENS TN Freshness & Update Management Engine** enforces an operational model grounded in verified source realities:
1. **Cadence-Adjusted Freshness:** Freshness expectations reflect the official publisher's authentic release cycle. Datasets with annual or 5-year lifecycles are not erroneously categorized as stale.
2. **Diagnostic Detection:** Automated checks detect and categorize failed downloads, schema shifts, missing files, HTTP errors, partial imports, and unexpectedly empty datasets.
3. **Citizen-Facing Transparency Labels:** Informative data freshness labels are displayed to citizens only when underlying timestamps are verified; if unverified, the system explicitly reports verification pending.
4. **Secret Scrubbing:** Error logs and diagnostic payloads scrub passwords, database URLs, API keys, bearer tokens, and JWTs.
5. **Deployment-Ready Operational Framework:** Because automated background workers (e.g. Celery / APScheduler) are not actively running in the current environment, documented operational CLI commands, systemd timers, and GitHub Actions templates are provided without falsely claiming automated sync execution.

---

## 2. Master Verified Source Inventory: Update Methods & Cadences

The table below catalogs all 22 verified sources from `docs/data/verified_source_registry.md`, detailing their actual update method, publication cadence, freshness threshold, and legal terms:

| Source ID | Civic Entity / Scope | Official Publisher | Update Method | Expected Cadence | Freshness Threshold | Legal & Access Terms |
|:---|:---|:---|:---:|:---:|:---:|:---|
| **`SRC-BUD-001`** | Budget Demands for Grants (BE, RE, AE) | Finance Department, GoTN | `MANUAL` | `ANNUAL` | 400 Days | RTI Act 2005 / Public State Record |
| **`SRC-BUD-002`** | Departmental Policy Notes & Objectives | State Departments & TNLA | `MANUAL` | `ANNUAL` | 400 Days | Tabled Assembly Paper |
| **`SRC-LEG-001`** | TNLA Debate Transcripts & Questions | TNLA Secretariat / TNeGA | `MANUAL` | `SESSIONAL` | 120 Days | TNLA Rules of Procedure |
| **`SRC-LEG-002`** | NeVA Tamil Nadu Daily Bulletins | NeVA / MoPA / TNLA | `SCHEDULED` | `SESSIONAL` | 90 Days | Government Open e-Governance |
| **`SRC-WRK-001`** | MLACDS Scheme Guidelines & Sanctions | Rural Development GoTN | `MANUAL` | `ANNUAL` | 400 Days | Public Scheme Guidelines |
| **`SRC-WRK-002`** | MPLADS Work Sanctions & Disbursals | MoSPI, GoI | `SCHEDULED` | `MONTHLY` | 45 Days | Government Open Data |
| **`SRC-ELC-001`** | ECI General Election Results & Form 20 | Election Commission of India | `EVENT_DRIVEN` | `EVENT_DRIVEN` | 1,825 Days (5 Yr) | Statutory Election Data |
| **`SRC-ELC-002`** | CEO Tamil Nadu Polling Returns & Affidavits| CEO Tamil Nadu | `EVENT_DRIVEN` | `EVENT_DRIVEN` | 1,825 Days (5 Yr) | RP Act 1951 Public Affidavits |
| **`SRC-FND-001`** | Political Party Form 24A (>₹20k Donations) | Election Commission of India | `SCHEDULED` | `ANNUAL` | 400 Days | RP Act 1951 Section 29C |
| **`SRC-FND-002`** | ECI Transparency Portal (Balance Sheets) | Election Commission of India | `SCHEDULED` | `ANNUAL` | 400 Days | Statutory Party Disclosures |
| **`SRC-FND-003`** | MCA-21 Electoral Trust Annual Returns | Ministry of Corporate Affairs | `SCHEDULED` | `ANNUAL` | 400 Days | Companies Act 2013 |
| **`SRC-GRV-001`** | CM Helpline 1100 (Mudhalvarin Mugavari) | TNeGA / GoTN | `UNAVAILABLE` | `DAILY` | 7 Days | DPDPA 2023 Protected (Dept Feed Only) |
| **`SRC-GRV-002`** | GCC 1913 PGRS Municipal Complaints | Greater Chennai Corporation | `UNAVAILABLE` | `DAILY` | 7 Days | Municipal Public Records (Token Only) |
| **`SRC-SLA-001`** | Tamil Nadu Citizen's Charters & SLAs | P&AR Department, GoTN | `MANUAL` | `ANNUAL` | 730 Days (2 Yr) | Statutory Service Commitments |
| **`SRC-AUD-001`** | CAG State Finances Audit Reports | CAG of India (Article 151) | `MANUAL` | `ANNUAL` | 400 Days | Constitutional Audit Document |
| **`SRC-POL-001`** | TN State Planning Commission Evaluations | TN State Planning Commission| `MANUAL` | `ANNUAL` | 365 Days | Official Research Monograph |
| **`SRC-STA-001`** | DES Tamil Nadu Statistical Hand Book | DES, GoTN | `MANUAL` | `ANNUAL` | 400 Days | Official Statistical Publication |
| **`SRC-STA-002`** | Open Government Data (`tn.data.gov.in`) | NIC & TNeGA | `API_BASED` | `MONTHLY` | 60 Days | GODL (Open Data License) |
| **`SRC-GEO-001`** | Local Government Directory (LGD) Codes | Ministry of Panchayati Raj | `API_BASED` | `MONTHLY` | 60 Days | National Standard Directory |
| **`SRC-GEO-002`** | TNeGA Urban GIS Ward Boundaries | TNeGA / ULBs | `MANUAL` | `EVENT_DRIVEN` | 1,825 Days (5 Yr) | State Spatial Data Standard |
| **`SRC-GOV-001`** | Tamil Nadu Government Gazette | Stationeries & Printing GoTN| `SCHEDULED` | `WEEKLY` | 14 Days | Official State Statutory Gazette |
| **`SRC-GOV-002`** | Official Government Orders (G.O.) Portal | All Departments, GoTN | `SCHEDULED` | `DAILY` | 7 Days | Official Administrative Orders |

---

## 3. Monitoring & Failure Diagnostics Engine

When imports are executed, the `DatasetFreshnessManager` monitors and logs six explicit operational health issue types:

```
+---------------------------------------------------------------------------------------------------------+
|                                    Ingestion Health Diagnostics Matrix                                  |
+--------------------------+-----------------------+------------------------------------------------------+
| Issue Type               | Health Status Flag    | Operational Root Cause & Remediation                 |
+--------------------------+-----------------------+------------------------------------------------------+
| FAILED_DOWNLOAD          | FAILED                | Network drop, HTTP 5xx server error, or connection   |
|                          |                       | timeout. Retries scheduled with exponential backoff. |
+--------------------------+-----------------------+------------------------------------------------------+
| SCHEMA_CHANGE            | FAILED                | Publisher altered column names, table headers, or    |
|                          |                       | data structures. Requires transformation adjustment. |
+--------------------------+-----------------------+------------------------------------------------------+
| MISSING_EXPECTED_FILE    | FAILED                | Target document missing from repository or manifest. |
|                          |                       | Quarantine import and verify upstream availability.  |
+--------------------------+-----------------------+------------------------------------------------------+
| HTTP_ERROR               | DEGRADED              | HTTP 403 Forbidden / 429 Rate Limited. Backoff and   |
|                          |                       | inspect access authorization.                        |
+--------------------------+-----------------------+------------------------------------------------------+
| PARTIAL_IMPORT           | DEGRADED              | Ingestion halted mid-batch (e.g. processed 25 of 38  |
|                          |                       | records). Savepoint rolled back cleanly.             |
+--------------------------+-----------------------+------------------------------------------------------+
| EMPTY_DATASET            | FAILED                | File exists or endpoint returned HTTP 200, but       |
|                          |                       | payload contains 0 records when data was expected.   |
+--------------------------+-----------------------+------------------------------------------------------+
```

### Zero Credential Leakage in Diagnostics:
All error payloads and diagnostics pass through `SecretScrubber`, redacting database credentials (`postgresql://***:***@host:5432/db`), API keys, access tokens, and JWT strings before entering system logs or API responses.

---

## 4. Citizen-Facing Data Freshness Labels

To protect citizens from false certainty or misunderstanding publication lags, the system computes informative freshness labels:

```
                                Dataset Assessment
                                        │
                    ┌───────────────────┴───────────────────┐
            Timestamp Available?                    Timestamp Absent?
                    │                                       │
         ┌──────────┴──────────┐               "Timestamp Unavailable /
       Failed?              Healthy?              Ingestion Pending"
         │                     │
"Update Temporarily     ┌──────┴────────────────────────┐
   Interrupted"         │                               │
                     Annual?                         Weekly?
                        │                               │
             "Official Annual Release        "Current Statutory Gazette
                     (2024)"                          Edition"
```

### Label Specifications by Category:
- **Annual State Records (`SRC-BUD-001`, `SRC-BUD-002`, `SRC-AUD-001`):** `"Official Annual Release (2024)"`
- **Election Cycles (`SRC-ELC-001`, `SRC-ELC-002`):** `"Current 16th Legislative Assembly Election Cycle (2021-2026)"`
- **Legislative Sessional Records (`SRC-LEG-001`, `SRC-LEG-002`):** `"Current Legislative Session Proceeding"`
- **Weekly Gazettes (`SRC-GOV-001`):** `"Current Statutory Gazette Edition"`
- **Monthly Administrative Directories (`SRC-GEO-001`):** `"Current Administrative Directory Sync"`
- **Privacy-Restricted Portals (`SRC-GRV-001`, `SRC-GRV-002`):** `"Departmental Verification Feed Only (DPDPA Protected)"`
- **Pending / Stale Publication:** `"Awaiting State Publication (Current Verified Baseline: {year})"`

---

## 5. Recovery Procedures & Operational Workflows

### Scenario 1: Recovering from a Failed Download or HTTP Error
1. Inspect failure diagnostic via `GET /api/freshness/diagnostics`.
2. Confirm upstream portal accessibility: `curl -I https://tnbudget.tn.gov.in/`.
3. If rate-limited (HTTP 429), verify `DEFAULT_DOMAIN_DELAYS` in acquisition framework.
4. Re-run ingestion in dry-run mode: `python -m backend.ops.freshness_manager sync --source SRC-BUD-001 --dry-run`.
5. Once verified, execute non-dry-run import; `DatasetFreshnessManager` automatically transitions health status from `FAILED` to `HEALTHY`.

### Scenario 2: Handling Schema Changes in Annual Budget Books
1. If `SCHEMA_CHANGE` is flagged, retrieve diagnostic details: `diagnostic_details.missing_columns`.
2. Compare previous year's DDG column headers with current publication.
3. Update column mapping dictionary in `backend/ingestion/budget_transform.py`.
4. Run unit tests: `python -m pytest tests/test_budget_validation.py`.
5. Re-ingest the affected volume using savepoint-guaranteed staging.

### Scenario 3: Recovering from a Partial Import
1. Ingestion rollback savepoint automatically reverts partial database state.
2. Inspect log to identify terminating record index.
3. Fix underlying malformed field (e.g. invalid date or unescaped character).
4. Re-run batch; existing valid records will be recognized and skipped (`SKIPPED_IDENTICAL`), while remainder completes insertion.

---

## 6. Deployment-Ready Scheduling Infrastructure

> [!IMPORTANT]
> **Current Environment Status:** There is no active Celery, APScheduler, or recurring cron worker currently executing in the project environment. Automated sync records must never be fabricated.

To operationalize recurring updates in staging or production environments, deploy the following production configurations:

### Option A: Systemd Timer (Linux Production Deployment)

Create `/etc/systemd/system/civiclens-freshness.service`:
```ini
[Unit]
Description=CIVICLENS TN Dataset Freshness & Ingestion Audit
After=network.target

[Service]
Type=oneshot
User=civiclens
WorkingDirectory=/opt/civiclens
Environment="PYTHONPATH=/opt/civiclens"
ExecStart=/opt/civiclens/venv/bin/python -m backend.ops.freshness_manager audit --auto-sync
```

Create `/etc/systemd/system/civiclens-freshness.timer`:
```ini
[Unit]
Description=Run CIVICLENS TN Freshness Audit Weekly (Wednesdays 04:00 UTC)

[Timer]
OnCalendar=Wed *-*-* 04:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable and activate:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now civiclens-freshness.timer
```

### Option B: GitHub Actions Scheduled Health Audit Workflow

Create `.github/workflows/dataset_freshness_audit.yml`:
```yaml
name: Civic Dataset Freshness Audit

on:
  schedule:
    - cron: '0 4 * * 3'  # Every Wednesday at 04:00 UTC (matching Gazette releases)
  workflow_dispatch:

jobs:
  freshness-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.13'
      - name: Install Dependencies
        run: pip install -r requirements.txt
      - name: Execute Freshness Audit
        run: python -m pytest tests/unit/test_dataset_freshness_operations.py
```

---

## 7. Supported REST API Endpoints

The system exposes operational data freshness via the `freshness` blueprint:

```
+---------------------------------------------------------------------------------------------------------+
|                                        Freshness REST API Endpoints                                     |
+------------------------------+--------+-----------------------------------------------------------------+
| Endpoint                     | Method | Description                                                     |
+------------------------------+--------+-----------------------------------------------------------------+
| /api/freshness               | GET    | Overview summary across all 22 verified sources with health     |
|                              |        | status counts, total records, and citizen freshness labels.     |
+------------------------------+--------+-----------------------------------------------------------------+
| /api/freshness/<source_id>   | GET    | Granular source-level report including last import timestamp,   |
|                              |        | publication cadence, update method, and failure diagnostics.    |
+------------------------------+--------+-----------------------------------------------------------------+
| /api/freshness/diagnostics   | GET    | Filtered list of all currently flagged, degraded, or stale      |
|                              |        | sources with sanitized error messages.                          |
+------------------------------+--------+-----------------------------------------------------------------+
```

---

## 8. Actual Verification Results

Verification was executed via automated test suites without mock data fabrication:

```
tests/test_budget_validation.py (5 Tests):
  - test_valid_record .......................................... PASSED [  3%]
  - test_missing_required_fields ............................... PASSED [  7%]
  - test_malformed_financial_year .............................. PASSED [ 11%]
  - test_null_amounts_handling ................................. PASSED [ 15%]
  - test_duplicate_detection_within_batch ....................... PASSED [ 19%]

tests/unit/test_data_quality_and_import_safety.py (11 Tests):
  - test_schema_required_fields_and_zero_fabrication ........... PASSED [ 23%]
  - test_source_url_and_provenance_validation .................. PASSED [ 26%]
  - test_duplicate_detection_historical_versions_and_conflicts . PASSED [ 30%]
  - test_external_identifier_format_validation ................. PASSED [ 34%]
  - test_referential_integrity_across_entities ................. PASSED [ 38%]
  - test_consistency_validation_date_fy_currency_geography ..... PASSED [ 42%]
  - test_missing_vs_zero_preservation .......................... PASSED [ 46%]
  - test_unicode_and_tamil_preservation ........................ PASSED [ 50%]
  - test_repeatable_imports_and_silent_overwrite_prevention .... PASSED [ 53%]
  - test_secret_scrubber_credential_masking .................... PASSED [ 57%]
  - test_safe_import_runner_dry_run_and_summary ................ PASSED [ 61%]

tests/unit/test_dataset_freshness_operations.py (10 Tests):
  - test_verified_source_catalog_cadences_and_methods .......... PASSED [ 65%]
  - test_freshness_evaluation_healthy .......................... PASSED [ 69%]
  - test_freshness_evaluation_stale_detection .................. PASSED [ 73%]
  - test_event_driven_sources_not_falsely_stale ................ PASSED [ 76%]
  - test_failed_download_diagnostics ........................... PASSED [ 80%]
  - test_partial_import_and_schema_change_diagnostics .......... PASSED [ 84%]
  - test_recovery_from_failed_update ........................... PASSED [ 88%]
  - test_citizen_freshness_labels .............................. PASSED [ 92%]
  - test_system_wide_freshness_assessment ....................... PASSED [ 96%]
  - test_freshness_api_endpoints ............................... PASSED [100%]

============================= 26 passed in 2.36s ==============================
```

**Outcome:** 26 passed, 0 failures, 100% pass rate.
