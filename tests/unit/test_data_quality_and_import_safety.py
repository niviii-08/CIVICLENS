"""
CIVICLENS TN — Unit Tests for Data Quality, Validation & Ingestion Hardening
===========================================================================
All test cases utilize explicitly labeled SYNTHETIC test fixtures (is_test_fixture=True).
No synthetic fixtures are stored in or mistaken for real civic production records.

Verifies:
1. Schema & required-field validation (zero data fabrication).
2. Source URL protocol and domain whitelisting.
3. Duplicate detection distinguishing exact duplicates, historical versions,
   conflicting source records, and superseded orders (Rule 1).
4. Stable external identifier validation.
5. Referential integrity validation across civic entities.
6. Multi-domain consistency (Date ISO-8601, FY consecutive years, currency multipliers, TN geography).
7. Non-coercion of missing vs. zero values.
8. Unicode & Tamil text preservation; mojibake corruption detection.
9. Protection against silent overwrites of manually reviewed or newer data (Rule 2).
10. Secret scrubbing ensuring zero credential leakage in error reporting.
11. Safe import runner with dry-run simulation and structured audit summary.
"""

import pytest
from datetime import datetime, timezone
from backend.ingestion.data_quality import (
    RecordQualityStatus,
    DuplicateType,
    ImportSummary,
    SecretScrubber,
    SourceProvenanceValidator,
    CivicSchemaValidator,
    ConsistencyValidator,
    UnicodeTamilGuard,
    DuplicateAndVersionClassifier,
    ReferentialIntegrityValidator,
    SafeImportRunner,
)


# -----------------------------------------------------------------------------
# Synthetic Test Fixtures (Clearly marked as synthetic test data)
# -----------------------------------------------------------------------------

@pytest.fixture
def synthetic_representative_fixture():
    return {
        "representative_id": "SYNTHETIC-TEST-REP-001",
        "name": "Dr. Synthetic Test MLA",
        "representative_type": "MLA",
        "constituency_id": "AC-TN-044",
        "party_id": "PARTY-DMK",
        "is_test_fixture": True,
    }


@pytest.fixture
def synthetic_scheme_fixture():
    return {
        "scheme_code": "SYNTHETIC-TEST-SCH-001",
        "name": "Synthetic Test Welfare Scheme",
        "department_id": "DEPT-SW",
        "financial_year": "2023-24",
        "is_test_fixture": True,
    }


# -----------------------------------------------------------------------------
# Test Cases
# -----------------------------------------------------------------------------

def test_schema_required_fields_and_zero_fabrication(synthetic_representative_fixture):
    """Verify schema validator enforces required fields and rejects incomplete records without fabricating data."""
    # Valid synthetic record
    is_valid, errs = CivicSchemaValidator.validate_schema("representative", synthetic_representative_fixture)
    assert is_valid is True
    assert len(errs) == 0

    # Incomplete record missing required field 'name'
    incomplete_record = {
        "representative_id": "SYNTHETIC-TEST-REP-002",
        "representative_type": "MLA",
        "is_test_fixture": True,
    }
    is_valid_inc, errs_inc = CivicSchemaValidator.validate_schema("representative", incomplete_record)
    assert is_valid_inc is False
    assert any("Missing required field 'name'" in e for e in errs_inc)


def test_source_url_and_provenance_validation():
    """Verify source URL protocols, whitelisted civic domains, and rejection of disallowed schemes."""
    # 1. Whitelisted government URLs
    valid, msg, whitelisted = SourceProvenanceValidator.validate_url("https://www.tn.gov.in/budget/statement.pdf")
    assert valid is True
    assert msg is None
    assert whitelisted is True

    valid_cag, msg_cag, whitelisted_cag = SourceProvenanceValidator.validate_url("https://cag.gov.in/reports/tn2024.pdf")
    assert valid_cag is True
    assert whitelisted_cag is True

    # 2. Disallowed protocols
    inv_proto, msg_proto, _ = SourceProvenanceValidator.validate_url("javascript:alert('malicious')")
    assert inv_proto is False
    assert "Disallowed URL protocol 'javascript'" in msg_proto

    inv_file, msg_file, _ = SourceProvenanceValidator.validate_url("file:///etc/passwd")
    assert inv_file is False
    assert "Disallowed URL protocol 'file'" in msg_file

    # 3. Non-whitelisted domain (structurally valid, flagged for human review)
    valid_ext, msg_ext, whitelisted_ext = SourceProvenanceValidator.validate_url("https://unverified-civic-blog.org/claim")
    assert valid_ext is True
    assert whitelisted_ext is False
    assert "not in verified civic whitelist" in msg_ext


def test_duplicate_detection_historical_versions_and_conflicts():
    """Verify Rule 1: Do not delete records simply because they appear duplicated."""
    existing_records = [
        {
            "id": "SYNTHETIC-TEST-REP-001",
            "name": "Synthetic Candidate A",
            "period": "TNLA-2016",
            "source_id": "SRC-ECI-2016",
            "votes_polled": 85000,
            "is_test_fixture": True,
        }
    ]

    # Case A: Historical Version (Same candidate elected in subsequent term TNLA-2021)
    incoming_historical = {
        "id": "SYNTHETIC-TEST-REP-001",
        "name": "Synthetic Candidate A",
        "period": "TNLA-2021",
        "source_id": "SRC-ECI-2021",
        "votes_polled": 92000,
        "is_test_fixture": True,
    }
    dup_type, matched, expl = DuplicateAndVersionClassifier.classify_record_relationship(
        existing_records, incoming_historical, id_field="id", period_field="period", source_field="source_id"
    )
    assert dup_type == DuplicateType.HISTORICAL_VERSION
    assert "Distinct historical version across periods" in expl

    # Case B: Conflicting Source (CAG audit vs Department report on same fiscal year)
    existing_budget = [
        {
            "id": "SYNTHETIC-SCH-EXP-001",
            "period": "2023-24",
            "source_id": "SRC-DEPT-POLICY-NOTE",
            "expenditure_crores": 1500.0,
            "is_test_fixture": True,
        }
    ]
    incoming_cag_audit = {
        "id": "SYNTHETIC-SCH-EXP-001",
        "period": "2023-24",
        "source_id": "SRC-CAG-AUDIT-REPORT",
        "expenditure_crores": 1420.5,
        "is_test_fixture": True,
    }
    dup_type_conf, _, expl_conf = DuplicateAndVersionClassifier.classify_record_relationship(
        existing_budget, incoming_cag_audit, id_field="id", period_field="period", source_field="source_id"
    )
    assert dup_type_conf == DuplicateType.CONFLICTING_SOURCE
    assert "Different source corroboration" in expl_conf

    # Case C: Exact Duplicate (identical payload, same period and source)
    incoming_exact = dict(existing_budget[0])
    dup_type_exact, _, _ = DuplicateAndVersionClassifier.classify_record_relationship(
        existing_budget, incoming_exact, id_field="id", period_field="period", source_field="source_id"
    )
    assert dup_type_exact == DuplicateType.EXACT_DUPLICATE


def test_external_identifier_format_validation():
    """Verify stable external identifiers adhere to canonical formatting patterns."""
    # Valid canonical IDs
    assert DuplicateAndVersionClassifier.validate_external_identifier("constituency", "AC-TN-044")[0] is True
    assert DuplicateAndVersionClassifier.validate_external_identifier("constituency", "PC-TN-02")[0] is True
    assert DuplicateAndVersionClassifier.validate_external_identifier("scheme", "SCH-TN-PUDHUMAI")[0] is True
    assert DuplicateAndVersionClassifier.validate_external_identifier("promise", "PRM-DMK-2021-001")[0] is True
    assert DuplicateAndVersionClassifier.validate_external_identifier("document", "DOC-GO-MS-34-SW-2022")[0] is True

    # Malformed IDs
    is_valid, err = DuplicateAndVersionClassifier.validate_external_identifier("constituency", "INVALID-CONST-XYZ")
    assert is_valid is False
    assert "does not match canonical format" in err


def test_referential_integrity_across_entities():
    """Verify referential integrity checks flag broken entity linkages for review."""
    known_registries = {
        "departments": {"DEPT-SW", "DEPT-HE", "DEPT-HLTH"},
        "constituencies": {"AC-TN-001", "AC-TN-044", "AC-TN-234"},
        "parties": {"PARTY-DMK", "PARTY-AIADMK", "PARTY-INC"},
    }

    # Case 1: Valid references
    valid_record = {
        "representative_id": "SYNTHETIC-REP-001",
        "name": "Valid Synthetic MLA",
        "constituency_id": "AC-TN-044",
        "party_id": "PARTY-DMK",
    }
    is_valid, errs = ReferentialIntegrityValidator.validate_relationships(
        "representative", valid_record, known_registries
    )
    assert is_valid is True
    assert len(errs) == 0

    # Case 2: Broken constituency link
    broken_record = {
        "representative_id": "SYNTHETIC-REP-002",
        "name": "Orphaned Synthetic MLA",
        "constituency_id": "AC-TN-999",  # Non-existent
        "party_id": "PARTY-DMK",
    }
    is_valid_brk, errs_brk = ReferentialIntegrityValidator.validate_relationships(
        "representative", broken_record, known_registries
    )
    assert is_valid_brk is False
    assert any("Constituency 'AC-TN-999' not found" in e for e in errs_brk)


def test_consistency_validation_date_fy_currency_geography():
    """Verify consistency rules across date formats, financial years, units, and Tamil Nadu geography."""
    # 1. Date format
    assert ConsistencyValidator.validate_date("2023-09-15")[0] is True
    assert ConsistencyValidator.validate_date("2023-09-15T10:30:00Z")[0] is True
    assert ConsistencyValidator.validate_date("15/09/2023")[0] is False  # Non-ISO
    assert ConsistencyValidator.validate_date("2023-02-31")[0] is False  # Invalid calendar date

    # 2. Chronology sanity
    chron_valid, chron_errs = ConsistencyValidator.validate_chronology(
        announcement_date="2023-05-01",
        event_date="2022-01-01",  # Impossible: announced after event
    )
    assert chron_valid is False
    assert any("Announcement date" in e for e in chron_errs)

    # 3. Financial Year validation
    assert ConsistencyValidator.validate_financial_year("2023-24")[0] is True
    assert ConsistencyValidator.validate_financial_year("2023-2024")[0] is True
    assert ConsistencyValidator.validate_financial_year("2023-25")[0] is False  # Non-consecutive
    assert ConsistencyValidator.validate_financial_year("2023")[0] is False     # Missing span

    # 4. Currency and Unit Multipliers
    u_valid, _, mult = ConsistencyValidator.validate_currency_and_unit("INR_Crores")
    assert u_valid is True
    assert mult == 10_000_000.0

    # 5. Tamil Nadu Geography (38 revenue districts, 234 ACs, 15 GCC zones)
    geo_valid, geo_errs = ConsistencyValidator.validate_geography(
        district_name="Chennai",
        lgd_code=577,
        ac_number=44,
        gcc_zone=5
    )
    assert geo_valid is True
    assert len(geo_errs) == 0

    # Invalid geography
    geo_inv, geo_inv_errs = ConsistencyValidator.validate_geography(
        district_name="Atlantis",
        ac_number=300,  # Exceeds 234
        gcc_zone=20     # Exceeds 15
    )
    assert geo_inv is False
    assert len(geo_inv_errs) == 3


def test_missing_vs_zero_preservation():
    """Verify non-coercion rule: None is preserved as missing; 0.0 is recognized as empirical zero."""
    # None represents missing/uncollected
    val, err, is_missing = ConsistencyValidator.validate_missing_vs_zero(None)
    assert val is True
    assert is_missing is True

    # 0.0 represents real empirical zero
    val_zero, err_zero, is_missing_zero = ConsistencyValidator.validate_missing_vs_zero(0.0)
    assert val_zero is True
    assert is_missing_zero is False

    # String '-' represents uncollected data
    val_dash, _, is_missing_dash = ConsistencyValidator.validate_missing_vs_zero("-")
    assert is_missing_dash is True


def test_unicode_and_tamil_preservation():
    """Verify Unicode NFC normalization, authentic Tamil text preservation, and mojibake detection."""
    # Authentic bilingual Tamil text
    tamil_text = "கலைஞர் மகளிர் உரிமைத் திட்டம் (Kalaignar Magalir Urimai Thittam)"
    is_valid, normalized, errs = UnicodeTamilGuard.validate_and_normalize(tamil_text, "scheme_name")
    assert is_valid is True
    assert UnicodeTamilGuard.contains_tamil(normalized) is True
    assert "கலைஞர்" in normalized

    # Mojibake corruption
    mojibake = "Tamil Nadu Â Government ÃƒÂ Announcement"
    is_valid_moji, _, errs_moji = UnicodeTamilGuard.validate_and_normalize(mojibake, "corrupted_text")
    assert is_valid_moji is False
    assert any("Encoding corruption" in e for e in errs_moji)


def test_repeatable_imports_and_silent_overwrite_prevention():
    """Verify Rule 2: Do not silently overwrite newer or manually reviewed data."""
    runner = SafeImportRunner()

    # Pre-existing database record verified by human auditor
    existing_lookup = {
        "SYNTHETIC-REP-001": {
            "id": "SYNTHETIC-REP-001",
            "name": "Auditor Verified Representative",
            "is_manually_reviewed": True,
            "review_status": "VERIFIED",
            "publication_date": "2024-01-01",
            "is_test_fixture": True,
        }
    }

    incoming_batch = [
        {
            "id": "SYNTHETIC-REP-001",
            "representative_id": "SYNTHETIC-REP-001",
            "name": "Overwriting Automated Candidate Name",
            "representative_type": "MLA",
            "publication_date": "2023-01-01",  # Older date
            "is_test_fixture": True,
        }
    ]

    summary = runner.process_records(
        entity_type="representative",
        incoming_records=incoming_batch,
        existing_lookup=existing_lookup,
        dry_run=True,
    )

    # Must protect manually reviewed record from silent overwrite
    assert summary.inserted == 0
    assert summary.updated == 0
    assert summary.skipped == 1
    assert summary.review_required >= 1
    assert any("Existing record has been verified by human auditor" in e["details"][0] for e in summary.validation_errors)


def test_secret_scrubber_credential_masking():
    """Verify SecretScrubber sanitizes database strings, credentials, and API tokens from logs."""
    raw_error = (
        "Failed to connect to database at postgresql://civic_admin:p@ssw0rd123!@db.internal:5432/civiclens_db "
        "with api_key='secret-token-abcdef123456' and bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjgNryP4J_wV"
    )
    clean_error = SecretScrubber.sanitize(raw_error)

    # Passwords and secrets must be redacted
    assert "p@ssw0rd123!" not in clean_error
    assert "secret-token-abcdef123456" not in clean_error
    assert "postgresql://***:***@db.internal:5432/civiclens_db" in clean_error
    assert "[REDACTED_SECRET]" in clean_error
    assert "[REDACTED_JWT]" in clean_error


def test_safe_import_runner_dry_run_and_summary():
    """Verify safe import runner generates structured audit metrics without persisting state during dry-run."""
    runner = SafeImportRunner()

    test_records = [
        # Valid new record
        {
            "scheme_code": "SYNTHETIC-SCH-001",
            "name": "New Valid Scheme",
            "department_id": "DEPT-SW",
            "financial_year": "2023-24",
            "is_test_fixture": True,
        },
        # Invalid record (missing required name)
        {
            "scheme_code": "SYNTHETIC-SCH-002",
            "department_id": "DEPT-SW",
            "is_test_fixture": True,
        },
        # Record with unverified domain
        {
            "scheme_code": "SYNTHETIC-SCH-003",
            "name": "Scheme With Unverified Source",
            "department_id": "DEPT-SW",
            "source_url": "https://random-unverified-blog.in/scheme.html",
            "is_test_fixture": True,
        }
    ]

    summary = runner.process_records(
        entity_type="scheme",
        incoming_records=test_records,
        existing_lookup={},
        dry_run=True,
    )

    assert summary.is_dry_run is True
    assert summary.total_evaluated == 3
    assert summary.inserted == 2
    assert summary.rejected == 1
    assert summary.review_required >= 1  # Unverified domain flagged
    assert summary.validation_errors_count >= 1
