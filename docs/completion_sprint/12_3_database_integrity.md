# CIVICLENS TN — Phase 12.3: Database Reliability and Data Integrity Report

**Date:** 2026-10-21  
**Phase:** 12.3 — Database Reliability and Data Integrity  
**Component:** Database Engine Configuration, Concurrency, Transactions, Schema Migrations, Referential Integrity, and Hot Backups  
**Status:** Completed & Verified  

---

## 1. Executive Summary & Confirmed Database Technology

Phase 12.3 addresses verified database risks and reliability bottlenecks identified in the Phase 12.1 Production Readiness Audit (`docs/completion_sprint/12_1_production_readiness_audit.md`). 

### 1.1 Confirmed Database Technology Stack
- **Database Engine:** SQLite 3 (Database file: `data/processed/civiclens.db`) operating with **Write-Ahead Logging (WAL)** mode.
- **ORM Framework:** SQLAlchemy 2.0 with connection pooling configuration for PostgreSQL/MySQL support and SQLite multithreaded support (`check_same_thread=False`).
- **Migration Management:** Alembic (1.18.5) utilizing linear revision chains and idempotent schema reflection.
- **Schema Scale:** 120 relational tables, 119 registered ORM models spanning all civic intelligence phases (budget, schemes, manifestos, promises, representatives, claims, civic issues, graph relationships, and policy evaluations).

All improvements were implemented non-destructively: no civic data was deleted, fabricated, or rewritten, and no destructive table resets were performed.

---

## 2. Issues Found and Remediations Implemented

| Issue ID | Severity | Description | Root Cause | Remediated Status & Implementation Details |
| :--- | :--- | :--- | :--- | :--- |
| **DB-ISSUE-01** | **Critical** | Database lock contention under concurrent access (`OperationalError: database is locked`). | SQLite defaults to `DELETE` journal mode and a short 5-second lock timeout. Concurrent readers and writers collided. | **Remediated.** In [`backend/database/session.py`](file:///backend/database/session.py), added an engine connection event listener setting `PRAGMA journal_mode=WAL`, `PRAGMA busy_timeout=10000` (10s auto-retry), `PRAGMA synchronous=NORMAL`, and SQLAlchemy `connect_args["timeout"] = 30.0`. |
| **DB-ISSUE-02** | **Critical** | Missing referential integrity enforcement on foreign key constraints. | SQLite disables foreign key enforcement by default (`PRAGMA foreign_keys = OFF`). | **Remediated.** Enforced `PRAGMA foreign_keys = ON` on every database connection. New writes violating foreign keys are immediately aborted with `sqlite3.IntegrityError`. |
| **DB-ISSUE-03** | **High** | Multi-step write operations vulnerable to partial state updates upon unhandled errors. | Ingestion scripts and mutation endpoints executed separate `session.commit()` calls without atomic transaction boundaries. | **Remediated.** Implemented `transactional_session()` context manager in [`backend/database/session.py`](file:///backend/database/session.py). Multi-step writes automatically commit on clean exit or execute `session.rollback()` on exception. |
| **DB-ISSUE-04** | **High** | Incomplete ORM metadata registration in Alembic. | [`backend/database/base.py`](file:///backend/database/base.py) only imported models from Phases 1–4, leaving later phase models unrepresented in `Base.metadata`. | **Remediated.** Registered all 119 ORM models from all phases into [`backend/database/base.py`](file:///backend/database/base.py). Alembic and schema reflection now accurately recognize the entire schema graph. |
| **DB-ISSUE-05** | **Medium** | Alembic migration scripts failed when tables already existed. | Migrations lacked table-existence reflection guards, causing crashes during re-runs or parallel test setup. | **Remediated.** Updated [`alembic/versions/phase5_funding_schema.py`](file:///alembic/versions/phase5_funding_schema.py) and [`alembic/versions/phase10_policy_evaluation_schema.py`](file:///alembic/versions/phase10_policy_evaluation_schema.py) with `sa.inspect(conn).get_table_names()` guards. Authored [`alembic/versions/phase12_database_integrity.py`](file:///alembic/versions/phase12_database_integrity.py) to add missing indexes. |
| **DB-ISSUE-06** | **High** | Absence of verified hot database backup and restoration utility. | No automated backup utility existed; file copies during active WAL writes risked corrupting database snapshots. | **Remediated.** Developed [`scripts/backup_database.py`](file:///scripts/backup_database.py) using SQLite's online backup API (`sqlite3.Connection.backup()`), SHA-256 manifests, and automated `PRAGMA integrity_check` validation. |

---

## 3. Database Integrity & Non-Destructive Audit Findings

A non-destructive diagnostic audit was executed directly against `data/processed/civiclens.db` via [`scripts/check_database_integrity.py`](file:///scripts/check_database_integrity.py):

### 3.1 B-Tree File Integrity
- Command: `PRAGMA integrity_check;`
- **Result:** `ok` (Zero corrupt B-tree pages, zero leaf allocation errors).

### 3.2 Canonical Table Duplicate Checks
No duplicate primary entities were detected across core canonical tables:
- `historical_schemes (scheme_name)`: **0 duplicates** across 20 records.
- `political_parties (party_name)`: **0 duplicates** across 8 records.
- `policy_registry (policy_name)`: **0 duplicates** across 8 records.
- `budget_departments (name)`: **0 duplicates** across 9 records.
- `promise_categories (name)`: **0 duplicates** across 17 records.
- `political_claims (claim_id)`: **0 duplicates** across 9 records.

### 3.3 Foreign Key Integrity & Orphaned Records Analysis
- Command: `PRAGMA foreign_key_check;`
- **Result:** 4,437 orphaned references detected in legacy table `promise_assessment_history`.
- **Root Cause Analysis:** In early phases (Phases 3–4), 1,065 promise assessments and 2,130 category mappings were ingested and seeded with references to `political_promises(id)`. However, the parent `political_promises` table was left empty (promises were modeled as assessment snapshots rather than populated parent rows).
- **Integrity Guarantee:**
  - In accordance with the constraint *"Do not delete, rewrite, or fabricate civic data"*, existing historical rows were preserved intact without synthetic record fabrication.
  - With `PRAGMA foreign_keys = ON` now enforced on all active connections, all new insertions must satisfy parent constraints, preventing any future accumulation of orphan records.

---

## 4. Alembic Migration History & Linearity

Alembic migrations are verified in a single, strictly linear revision chain without branches or competing heads:

```mermaid
flowchart LR
    M1["3c1c20ede17a<br/>create_budget_schema"] --> M2["15485971f6ab<br/>add_historicalscheme"]
    M2 --> M3["7ccfdea60b7f<br/>create_historical_scheme_db"]
    M3 --> M4["phase5_funding_schema<br/>funding_transparency"]
    M4 --> M5["phase10_policy_evaluation_schema<br/>policy_evaluation"]
    M5 --> M6["phase12_database_integrity<br/>(head) indexes & alignment"]
```

### Verification Command & Output
```bash
python -m alembic current
```
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
phase12_database_integrity (head)
```

---

## 5. Verified Backup and Disaster Recovery

### 5.1 Online Hot-Backup Procedure
The backup script [`scripts/backup_database.py`](file:///scripts/backup_database.py) uses the SQLite Online Backup API (`sqlite3.Connection.backup()`), allowing consistent snapshots to be taken while web requests and ingestion jobs continue reading and writing concurrently:

```bash
python scripts/backup_database.py --source data/processed/civiclens.db --dest-dir data/backups
```

**Verified Output:**
```
[*] Starting backup from 'data/processed/civiclens.db' to 'data/backups/civiclens_backup_20261021_074738.db'...
[+] Database pages transferred successfully.
[+] Backup completed: civiclens_backup_20261021_074738.db (7,856,128 bytes)
[+] SHA-256 Checksum: e95dfaa8b2925d1cbc76b58a03b106390202db544fb927daececc7efcbb4fd1c
[*] Running PRAGMA integrity_check on backup...
[+] Backup verified: PRAGMA integrity_check returned 'ok'
```

### 5.2 Dry-Run Restore Verification
Restoration safety was verified using the `--dry-run` flag, which tests the integrity of the backup file before executing file replacement:

```bash
python scripts/backup_database.py --restore-from data/backups/civiclens_backup_20261021_074738.db --restore-to data/processed/civiclens.db --dry-run
```
**Output:**
```
[*] Verifying integrity of backup 'data/backups/civiclens_backup_20261021_074738.db' before restore...
[+] Dry run: Backup is intact and ready for restore.
```

---

## 6. Automated Test Verification

All database integrity behaviors are continuously verified by [`tests/unit/test_database_integrity.py`](file:///tests/unit/test_database_integrity.py):

| Test Case | Description | Result |
| :--- | :--- | :--- |
| `test_sqlite_pragmas_enforced` | Confirms `foreign_keys=1`, `journal_mode=WAL`, `busy_timeout>=10000` | **PASSED** |
| `test_transactional_session_commit` | Verifies clean transactions commit automatically | **PASSED** |
| `test_transactional_session_rollback` | Verifies unhandled exceptions trigger automatic rollback | **PASSED** |
| `test_foreign_key_referential_integrity_enforcement` | Confirms invalid parent foreign keys raise `IntegrityError` | **PASSED** |
| `test_no_duplicate_canonical_records` | Verifies schemes and departments have 0 duplicate identifiers | **PASSED** |
| `test_database_backup_and_checksum_verification` | Verifies hot backup creation, manifest generation, and SHA-256 | **PASSED** |
| `test_database_restore_dry_run_and_execution` | Verifies dry-run validation and byte-identical database restore | **PASSED** |

**Execution Result:**
```
pytest tests/unit/test_database_integrity.py -v
======================== 7 passed, 1 warning in 2.70s =========================
```

---

## 7. Unresolved Risks and Operational Guidance

1. **SQLite Concurrency Ceiling:**
   - SQLite in WAL mode safely supports hundreds of concurrent readers and sequential queued writers with 10s timeout.
   - For high-volume multi-instance horizontal scaling, the application should be pointed to a PostgreSQL database by setting `DATABASE_URL=postgresql://user:pass@host:5432/civiclens` (supported natively by the SQLAlchemy connection pooling configuration in `session.py`).
2. **Legacy Orphaned Records:**
   - 4,437 rows in `promise_assessment_history` reference unpopulated `political_promises` IDs from Phase 3/4. These records are preserved for provenance, and active FK enforcement prevents new orphans.
3. **Operator Cron Backup:**
   - Operators must schedule periodic execution of `python scripts/backup_database.py` via cron or systemd timer before taking production traffic.
