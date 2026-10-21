"""
Phase 12.3: Database Reliability and Data Integrity Automated Tests
Validates:
- SQLite PRAGMAs (foreign_keys=ON, journal_mode=WAL, busy_timeout)
- Transactional session context manager commit/rollback behavior
- Referential integrity enforcement under active foreign keys
- Prevention of duplicate records in core entities
- Backup creation and integrity verification
"""
import os
import tempfile
import pytest
from sqlalchemy.exc import IntegrityError
from backend.database.session import SessionLocal, transactional_session, engine
from backend.models.common import Source
from backend.models.budget import BudgetRecord, HistoricalScheme, BudgetDepartment
from scripts.backup_database import backup_database, calculate_sha256


def test_sqlite_pragmas_enforced():
    """Verifies SQLite connection pragmas for foreign keys, WAL mode, and busy timeout."""
    with engine.connect() as conn:
        fk = conn.exec_driver_sql("PRAGMA foreign_keys;").scalar()
        jm = conn.exec_driver_sql("PRAGMA journal_mode;").scalar()
        bt = conn.exec_driver_sql("PRAGMA busy_timeout;").scalar()

        assert fk == 1, "PRAGMA foreign_keys must be enabled (1)"
        assert str(jm).lower() == "wal", "PRAGMA journal_mode must be 'wal'"
        assert bt >= 5000, f"PRAGMA busy_timeout must be at least 5000ms, got {bt}"


def test_transactional_session_commit():
    """Verifies that transactional_session automatically commits on clean completion."""
    src_name = f"TEST_SOURCE_COMMIT_{os.getpid()}"
    with transactional_session() as session:
        src = Source(name=src_name, type="Test")
        session.add(src)

    # Verify committed
    verify_session = SessionLocal()
    try:
        found = verify_session.query(Source).filter_by(name=src_name).first()
        assert found is not None
        assert found.type == "Test"
        # Cleanup
        verify_session.delete(found)
        verify_session.commit()
    finally:
        verify_session.close()


def test_transactional_session_rollback():
    """Verifies that transactional_session automatically rolls back upon an uncaught exception."""
    src_name = f"TEST_SOURCE_ROLLBACK_{os.getpid()}"

    with pytest.raises(RuntimeError):
        with transactional_session() as session:
            src = Source(name=src_name, type="Test")
            session.add(src)
            raise RuntimeError("Simulated failure inside transaction")

    # Verify NOT committed
    verify_session = SessionLocal()
    try:
        found = verify_session.query(Source).filter_by(name=src_name).first()
        assert found is None, "Failed transaction changes must be rolled back"
    finally:
        verify_session.close()


def test_foreign_key_referential_integrity_enforcement():
    """Verifies that inserting a child record with an invalid foreign key raises IntegrityError."""
    session = SessionLocal()
    try:
        # Invalid scheme_id that does not exist in budget_schemes
        invalid_record = BudgetRecord(
            scheme_id=99999999,
            financial_year="2023-24",
            amount=5000.0,
            budget_stage="actual"
        )
        session.add(invalid_record)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
    finally:
        session.close()


def test_no_duplicate_canonical_records():
    """Verifies that core entities have zero duplicate primary identifiers."""
    session = SessionLocal()
    try:
        from sqlalchemy import func
        # Check historical schemes
        dup_schemes = session.query(
            HistoricalScheme.scheme_name, func.count(HistoricalScheme.id)
        ).group_by(HistoricalScheme.scheme_name).having(func.count(HistoricalScheme.id) > 1).all()
        assert len(dup_schemes) == 0, f"Found duplicate schemes: {dup_schemes}"

        # Check departments
        dup_depts = session.query(
            BudgetDepartment.name, func.count(BudgetDepartment.id)
        ).group_by(BudgetDepartment.name).having(func.count(BudgetDepartment.id) > 1).all()
        assert len(dup_depts) == 0, f"Found duplicate departments: {dup_depts}"
    finally:
        session.close()


def test_database_backup_and_checksum_verification():
    """Verifies the online backup utility creates a valid SQLite backup with matching SHA-256."""
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_file = backup_database(
            source_path="data/processed/civiclens.db",
            backup_dir=tmpdir,
            verify=True
        )

        assert os.path.exists(backup_file)
        assert os.path.getsize(backup_file) > 0

        manifest_file = backup_file + ".manifest"
        assert os.path.exists(manifest_file)

        checksum = calculate_sha256(backup_file)
        assert len(checksum) == 64


def test_database_restore_dry_run_and_execution():
    """Verifies that restore_database validates backup integrity and restores safely."""
    from scripts.backup_database import restore_database
    with tempfile.TemporaryDirectory() as tmpdir:
        backup_file = backup_database(
            source_path="data/processed/civiclens.db",
            backup_dir=tmpdir,
            verify=True
        )
        target_restore = os.path.join(tmpdir, "restored_civiclens.db")

        # Test dry-run
        dry_run_success = restore_database(backup_file, target_restore, dry_run=True)
        assert dry_run_success is True
        assert not os.path.exists(target_restore)

        # Test actual restore
        restore_success = restore_database(backup_file, target_restore, dry_run=False)
        assert restore_success is True
        assert os.path.exists(target_restore)
        assert os.path.getsize(target_restore) == os.path.getsize(backup_file)

