# CIVICLENS TN — Phase 12.3: Database Reliability and Data Integrity Report

**Date:** 2026-10-20  
**Phase:** 12.3 — Database Reliability and Data Integrity  
**Scope:** SQLite PRAGMA enforcement, connection pooling & resilience, transactional session boundary management, Alembic migration alignment & idempotency, foreign key integrity, duplicate prevention, and verified hot-backup utilities.

---

## 1. Executive Summary

Phase 12.3 strengthened CIVICLENS TN's data persistence and integrity posture without modifying existing civic data or changing the technology stack. Key improvements include:
1. **SQLite PRAGMA & Connection Hardening**: Enforced `PRAGMA foreign_keys = ON`, `PRAGMA journal_mode = WAL`, `PRAGMA busy_timeout = 10000`, and `PRAGMA synchronous = NORMAL` on every connection via SQLAlchemy event listeners, with a 30-second SQLite connect timeout and connection pooling settings for PostgreSQL/external RDBMS.
2. **Transactional Session Scoping**: Implemented `transactional_session()` in `backend/database/session.py` to ensure multi-step writes are atomically committed on clean execution or rolled back upon exception.
3. **Comprehensive Metadata Alignment**: Registered all 119 ORM models spanning Phases 1–11 in `backend/database/base.py`, ensuring Alembic and metadata reflection accurately capture the complete schema graph.
4. **Idempotent Alembic Migrations**: Guarded table creation in `alembic/versions/phase5_funding_schema.py` and `alembic/versions/phase10_policy_evaluation_schema.py` using table-existence inspection, and authored `alembic/versions/phase12_database_integrity.py` to reconcile missing tables and add indexes across core civic entities.
5. **Verified Online Backup & Restore Utility**: Developed `scripts/backup_database.py` utilizing SQLite's hot online backup API (`sqlite3.Connection.backup()`), SHA-256 manifest verification, and automated `PRAGMA integrity_check` validation.
6. **Data Integrity Test Suite**: Created `tests/unit/test_database_integrity.py` verifying PRAGMA enforcement, transactional rollback, foreign key integrity violation catching, zero duplicate canonical entities, and hot backup validity (6/6 passing).

---

## 2. Verified Issues and Implemented Remediations

### 2.1 Connection Pragmas and Concurrency Locks
- **Issue**: SQLite by default operates in `DELETE` journal mode with `foreign_keys = OFF` and a default 5-second lock timeout. Concurrent operations from background collectors and frontend requests were vulnerable to `OperationalError: database is locked`.
- **Remediation**: Added an `@event.listens_for(engine, "connect")` listener in `backend/database/session.py`:
  - `PRAGMA foreign_keys = ON`: Prevents orphan child records across budget, promise, representative, and policy tables.
  - `PRAGMA journal_mode = WAL`: Allows concurrent readers and writers without blocking.
  - `PRAGMA busy_timeout = 10000`: Automatically retries busy locks for up to 10 seconds before raising an error.
  - `PRAGMA synchronous = NORMAL`: Maximizes write throughput safely within WAL mode.

### 2.2 Multi-Step Write Scoping
- **Issue**: Multi-step write operations in ingestion pipelines and services were vulnerable to partial state updates if unhandled exceptions occurred between commits.
- **Remediation**: Introduced `transactional_session()` context manager in `backend/database/session.py`. Usage patterns automatically guarantee `session.commit()` on clean exit and `session.rollback()` on exception.

### 2.3 Alembic Schema & Model Metadata Registration
- **Issue**: `backend/database/base.py` only imported a subset of models, leaving later phase models (Phase 5 funding, Phase 6 representatives, Phase 7 claims, Phase 8 civic issues, Phase 9 graph, Phase 10 policy evaluation, Phase 11 search/evidence) disconnected from `Base.metadata`.
- **Remediation**: Exported and imported all models in `backend/database/base.py`. Upgraded existing migration scripts (`phase5_funding_schema.py`, `phase10_policy_evaluation_schema.py`) with reflection checks (`sa.inspect(conn).get_table_names()`) to prevent failure when tables already exist. Authored `alembic/versions/phase12_database_integrity.py` and applied it to `data/processed/civiclens.db` (`alembic current` is at head).

### 2.4 Verified Backup and Restore
- **Issue**: No automated hot-backup script existed with integrity checking and SHA-256 verification.
- **Remediation**: Created `scripts/backup_database.py`:
  - Uses SQLite Online Backup API (`sqlite3.Connection.backup()`) to create atomic, non-blocking snapshots without locking reader threads.
  - Runs `PRAGMA integrity_check;` on the backup file.
  - Computes SHA-256 hashes and saves a metadata manifest JSON with row counts, file size, timestamp, and checksum.
  - Supports `--verify-restore` mode to test restoring to an ephemeral database.

---

## 3. Test Verification Results

- `pytest tests/unit/test_database_integrity.py -v`:
  - `test_sqlite_pragmas_enabled`: PASSED (foreign_keys=1, journal_mode=WAL, busy_timeout=10000)
  - `test_transactional_session_commits_on_success`: PASSED
  - `test_transactional_session_rollbacks_on_error`: PASSED
  - `test_foreign_key_integrity_enforcement`: PASSED (IntegrityError raised on missing parent key)
  - `test_no_duplicate_canonical_entities_in_seed_db`: PASSED
  - `test_database_backup_and_integrity_check`: PASSED
- `pytest tests/api/ -v`: 65/65 tests PASSED.

---

## 4. Conclusion
The database infrastructure is verified, robust, and aligned with Phase 12.3 requirements. All database operations now maintain strict referential integrity, concurrency resilience, and verified backup capabilities.
