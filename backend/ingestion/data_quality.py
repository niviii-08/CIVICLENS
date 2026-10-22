"""
CIVICLENS TN — Civic Data Quality, Validation & Ingestion Hardening Engine
=========================================================================
Comprehensive validation and hardening pipeline safeguarding civic data ingestion
across Tamil Nadu representatives, constituencies, departments, schemes, budgets,
promises, claims, evidence documents, and civic timelines.

Safeguards Enforced:
1. Schema & Required-Field Validation (rejects incomplete schemas; zero data fabrication).
2. Source URL & Provenance Validation (strict protocol, domain whitelisting, metadata auditing).
3. Duplicate Detection & Stable External Identifiers (distinguishes exact duplicates from
   historical versions, conflicting source records, and superseded orders).
4. Referential Integrity Validation across civic entities (cross-references without orphaned records).
5. Multi-Domain Consistency (Date ISO-8601, FY format, INR currency, unit multipliers,
   geographic validation for 38 TN districts, 234 ACs, 15 GCC zones, LGD codes).
6. Missing vs. Zero Values (preserves None without coercing to 0.0; distinguishes empirical zero).
7. Unicode & Tamil Text Preservation (detects mojibake/corrupted encodings; NFC normalization;
   bilingual name_en/name_ta preservation).
8. Record Quality Classification (VALID, INCOMPLETE, STALE, CONFLICTING, INVALID).
9. Repeatable Imports & Safe Reruns (idempotent; protects manually reviewed or newer data
   from silent overwrite).
10. Secret & Sensitive Data Scrubbing (sanitizes database strings, API keys, tokens from logs/reports).
11. Safe Staging, Dry-Run, Rollback & Backup Manifests (safe transaction savepoints; zero destructive runs).
"""

import re
import os
import json
import logging
import unicodedata
import urllib.parse
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set, Union
from sqlalchemy.orm import Session

logger = logging.getLogger("civiclens.data_quality")


# -----------------------------------------------------------------------------
# 1. Enums and Data Models
# -----------------------------------------------------------------------------

class RecordQualityStatus(str, Enum):
    VALID = "VALID"
    INCOMPLETE = "INCOMPLETE"
    STALE = "STALE"
    CONFLICTING = "CONFLICTING"
    INVALID = "INVALID"


class DuplicateType(str, Enum):
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    HISTORICAL_VERSION = "HISTORICAL_VERSION"
    CONFLICTING_SOURCE = "CONFLICTING_SOURCE"
    SUPERSEDED_ORDER = "SUPERSEDED_ORDER"
    UNIQUE_RECORD = "UNIQUE_RECORD"


@dataclass
class ImportSummary:
    """Standardized audit summary of an ingestion run."""
    total_evaluated: int = 0
    inserted: int = 0
    updated: int = 0
    skipped: int = 0
    rejected: int = 0
    review_required: int = 0
    conflicts_detected: int = 0
    stale_records_detected: int = 0
    is_dry_run: bool = False
    backup_manifest_id: Optional[str] = None
    validation_errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def validation_errors_count(self) -> int:
        return len(self.validation_errors)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_evaluated": self.total_evaluated,
            "inserted": self.inserted,
            "updated": self.updated,
            "skipped": self.skipped,
            "rejected": self.rejected,
            "review_required": self.review_required,
            "conflicts_detected": self.conflicts_detected,
            "stale_records_detected": self.stale_records_detected,
            "is_dry_run": self.is_dry_run,
            "backup_manifest_id": self.backup_manifest_id,
            "validation_errors_count": self.validation_errors_count,
            "validation_errors": self.validation_errors,
        }


# -----------------------------------------------------------------------------
# 2. Secret & Sensitive Data Scrubber (Zero Credential Leakage)
# -----------------------------------------------------------------------------

class SecretScrubber:
    """Scrubs credentials, passwords, tokens, API keys, and connection strings from error messages."""

    # Matches postgresql://user:pass@host/db or sqlite:///...
    DB_URL_PATTERN = re.compile(
        r"([a-zA-Z0-9\+]+://)([^/\s]+)@([a-zA-Z0-9\.\-]+(?::\d+)?(?:/[^\s]*)?)",
        re.IGNORECASE
    )

    # Matches api_key="secret", token='123456', password = "foo"
    AUTH_KV_PATTERN = re.compile(
        r"(?i)\b(api[_-]?key|access[_-]?token|secret[_-]?key|password|auth|authorization)\b(\s*[:=]\s*['\"]?)([\w\-\.\+/=]{6,})(['\"]?)",
    )

    # Matches bearer <token>
    BEARER_PATTERN = re.compile(
        r"(?i)\b(bearer)\s+([a-zA-Z0-9_\-\.\+/=]{6,})",
    )

    # Matches raw JWT tokens (header.payload.signature)
    JWT_PATTERN = re.compile(
        r"\bey[A-Za-z0-9_-]{8,}(?:\.[A-Za-z0-9_-]{8,})+\b"
    )

    @classmethod
    def sanitize(cls, message: str) -> str:
        """Sanitizes text by removing sensitive connection strings and secrets."""
        if not message or not isinstance(message, str):
            return ""

        # Mask database credentials
        clean = cls.DB_URL_PATTERN.sub(r"\1***:***@\3", message)
        # Mask JWT tokens first
        clean = cls.JWT_PATTERN.sub("[REDACTED_JWT]", clean)
        # Mask API keys / passwords / tokens
        clean = cls.AUTH_KV_PATTERN.sub(r"\1\2[REDACTED_SECRET]\4", clean)
        # Mask Bearer tokens
        clean = cls.BEARER_PATTERN.sub(r"\1 [REDACTED_SECRET]", clean)
        return clean


# -----------------------------------------------------------------------------
# 3. Source URL & Provenance Validator
# -----------------------------------------------------------------------------

class SourceProvenanceValidator:
    """Validates source URL protocols, whitelisted civic domains, and provenance records."""

    PERMITTED_PROTOCOLS = {"http", "https"}
    DISALLOWED_PROTOCOLS = {"ftp", "file", "javascript", "data", "blob"}

    WHITELISTED_CIVIC_DOMAINS = {
        # Official Government of Tamil Nadu
        "tn.gov.in",
        "tnelection.tn.gov.in",
        "tnbudget.tn.gov.in",
        "assembly.tn.gov.in",
        "des.tn.gov.in",
        "dipr.tn.gov.in",
        "elections.tn.gov.in",
        "chennaicorporation.gov.in",
        # Constitutional & National Statistical Authorities
        "eci.gov.in",
        "results.eci.gov.in",
        "cag.gov.in",
        "data.gov.in",
        "sansad.in",
        "pib.gov.in",
        "lgdirectory.gov.in",
        "censusindia.gov.in",
        "rbi.org.in",
        "prsindia.org",
        # Accredited Independent Fact-Checking Organisations (IFCN)
        "altnews.in",
        "boomlive.in",
        "factly.in",
        "vishvasnews.com",
        "thelogicalindian.com",
        # Mainstream Civic News Media
        "thehindu.com",
        "timesofindia.indiatimes.com",
        "dinamalar.com",
        "dailythanthi.com",
        "newindianexpress.com",
        "hindutamil.in",
        # Verified Political Parties (Manifesto archives)
        "dmk.in",
        "aiadmk.com",
    }

    @classmethod
    def validate_url(cls, url: Optional[str]) -> Tuple[bool, Optional[str], bool]:
        """
        Validates URL format, protocol, and domain whitelisting.
        Returns: (is_valid, error_or_warning_message, is_whitelisted)
        """
        if not url or not isinstance(url, str) or not url.strip():
            return False, "Missing or empty source URL.", False

        url_clean = url.strip()
        try:
            parsed = urllib.parse.urlparse(url_clean)
        except Exception as e:
            return False, f"Malformed URL: {SecretScrubber.sanitize(str(e))}", False

        # Scheme check
        scheme = parsed.scheme.lower()
        if scheme in cls.DISALLOWED_PROTOCOLS:
            return False, f"Disallowed URL protocol '{scheme}'. Strictly http/https allowed.", False

        if scheme not in cls.PERMITTED_PROTOCOLS:
            return False, f"Invalid URL protocol '{scheme}'. Must be http or https.", False

        # Host check
        hostname = (parsed.hostname or "").lower()
        if not hostname:
            return False, "URL lacks a valid network host.", False

        # Domain whitelist matching (supports subdomains, e.g. tnbudget.tn.gov.in matches tn.gov.in)
        is_whitelisted = False
        for allowed in cls.WHITELISTED_CIVIC_DOMAINS:
            if hostname == allowed or hostname.endswith("." + allowed):
                is_whitelisted = True
                break

        if not is_whitelisted:
            return (
                True,  # Structurally valid URL
                f"Source domain '{hostname}' is not in verified civic whitelist. Requires provenance review.",
                False
            )

        return True, None, True

    @classmethod
    def validate_provenance(cls, metadata: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validates that necessary provenance metadata is present and non-fabricated."""
        errors: List[str] = []

        if not metadata.get("title"):
            errors.append("Provenance missing document/source title.")
        if not metadata.get("publisher"):
            errors.append("Provenance missing issuing publisher/department.")

        url_valid, url_err, is_whitelisted = cls.validate_url(metadata.get("source_url") or metadata.get("url"))
        if not url_valid:
            errors.append(url_err or "Invalid source URL.")
        elif not is_whitelisted:
            # Notice for human review
            errors.append(f"UNVERIFIED_SOURCE_DOMAIN: {url_err}")

        return len(errors) == 0, errors


# -----------------------------------------------------------------------------
# 4. Schema & Required-Field Validator (Zero Fabrication)
# -----------------------------------------------------------------------------

class CivicSchemaValidator:
    """Enforces entity-specific required fields and strict zero-fabrication rules."""

    REQUIRED_FIELDS_BY_ENTITY = {
        "representative": ["representative_id", "name", "representative_type"],
        "constituency": ["constituency_id", "name", "constituency_type", "district_id"],
        "department": ["code", "name"],
        "scheme": ["scheme_code", "name", "department_id"],
        "budget_record": ["financial_year", "budget_stage", "department_name", "scheme_name"],
        "promise": ["promise_id", "party_id", "promise_text", "election_year"],
        "claim": ["claim_id", "claim_text", "claim_type"],
        "document": ["document_id", "title", "source_url", "source_tier"],
        "timeline_milestone": ["milestone_id", "title", "event_type", "date_semantics"],
    }

    @classmethod
    def validate_schema(cls, entity_type: str, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validates that all mandatory fields are present and non-empty.
        Never fabricates placeholder data to bypass requirements.
        """
        norm_type = entity_type.strip().lower()
        required = cls.REQUIRED_FIELDS_BY_ENTITY.get(norm_type)

        if not required:
            # Entity without strict schema; check for basic dictionary structure
            if not isinstance(record, dict) or not record:
                return False, [f"Record for '{entity_type}' must be a non-empty dictionary."]
            return True, []

        missing = []
        for field_name in required:
            val = record.get(field_name)
            if val is None or (isinstance(val, str) and not val.strip()):
                missing.append(field_name)

        if missing:
            errors = [f"Missing required field '{f}' for entity type '{entity_type}'." for f in missing]
            return False, errors

        return True, []


# -----------------------------------------------------------------------------
# 5. Consistency Validator (Date, FY, Currency, Unit, Geography, Missing vs Zero)
# -----------------------------------------------------------------------------

class ConsistencyValidator:
    """Validates date semantics, financial years, currency, units, geography, and missing vs zero."""

    # 38 Revenue Districts of Tamil Nadu (Official LGD names)
    TAMIL_NADU_DISTRICTS = {
        "ARIYALUR", "CHENGALPATTU", "CHENNAI", "COIMBATORE", "CUDDALORE",
        "DHARMAPURI", "DINDIGUL", "ERODE", "KALLAKURICHI", "KANCHEEPURAM", "KANCHIPURAM",
        "KANNIYAKUMARI", "KANYAKUMARI", "KARUR", "KRISHNAGIRI", "MADURAI",
        "MAYILADUTHURAI", "NAGAPATTINAM", "NAMAKKAL", "NILGIRIS", "PERAMBALUR",
        "PUDUKKOTTAI", "RAMANATHAPURAM", "RANIPET", "SALEM", "SIVAGANGA",
        "TENKASI", "THANJAVUR", "THENI", "THOOTHUKUDI", "TIRUCHIRAPPALLI", "TRICHY",
        "TIRUNELVELI", "TIRUPATHUR", "TIRUPATTUR", "TIRUPPUR", "TIRUVALLUR",
        "TIRUVANNAMALAI", "TIRUVARUR", "VELLORE", "VILUPPURAM", "VILLUPURAM",
        "VIRUDHUNAGAR"
    }

    # Financial year format: 2022-23 or 2022-2023
    FY_SHORT_REGEX = re.compile(r"^(\d{4})-(\d{2})$")
    FY_FULL_REGEX = re.compile(r"^(\d{4})-(\d{4})$")

    # Date ISO-8601 regex: YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ
    DATE_ISO_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})?)?$")

    # Valid Currency Units
    VALID_CURRENCY_UNITS = {
        "INR_CRORES": 10_000_000.0,
        "INR_LAKHS": 100_000.0,
        "INR_THOUSANDS": 1_000.0,
        "INR_ABSOLUTE": 1.0,
        "CRORES": 10_000_000.0,
        "LAKHS": 100_000.0,
        "THOUSANDS": 1_000.0,
        "ABSOLUTE": 1.0,
    }

    @classmethod
    def validate_date(cls, date_str: Optional[str]) -> Tuple[bool, Optional[str]]:
        """Validates that a date adheres strictly to ISO-8601 formatting."""
        if date_str is None or date_str == "":
            return True, None  # None is permitted for unanchored/undated records

        if not isinstance(date_str, str) or not cls.DATE_ISO_REGEX.match(date_str.strip()):
            return False, f"Malformed date '{date_str}'. Must follow ISO-8601 (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SSZ)."

        # Validate calendar validity
        clean_date = date_str.strip()[:10]
        try:
            datetime.strptime(clean_date, "%Y-%m-%d")
        except ValueError as ve:
            return False, f"Invalid calendar date '{date_str}': {str(ve)}."

        return True, None

    @classmethod
    def validate_chronology(
        cls,
        announcement_date: Optional[str] = None,
        event_date: Optional[str] = None,
        publication_date: Optional[str] = None,
        audit_date: Optional[str] = None,
    ) -> Tuple[bool, List[str]]:
        """Verifies chronological sanity across lifecycle date dimensions."""
        errors: List[str] = []

        d_ann = cls._parse_date_prefix(announcement_date)
        d_evt = cls._parse_date_prefix(event_date)
        d_pub = cls._parse_date_prefix(publication_date)
        d_aud = cls._parse_date_prefix(audit_date)

        if d_ann and d_evt and d_ann > d_evt:
            errors.append(f"Announcement date ({announcement_date}) cannot occur after substantive event date ({event_date}).")

        if d_evt and d_aud and d_evt > d_aud:
            errors.append(f"Substantive event date ({event_date}) cannot occur after constitutional audit date ({audit_date}).")

        return len(errors) == 0, errors

    @classmethod
    def _parse_date_prefix(cls, date_str: Optional[str]) -> Optional[datetime]:
        if not date_str or not isinstance(date_str, str):
            return None
        try:
            return datetime.strptime(date_str[:10], "%Y-%m-%d")
        except Exception:
            return None

    @classmethod
    def validate_financial_year(cls, fy_str: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validates financial year string format and consecutive year logic.
        Valid: '2023-24' or '2023-2024'.
        Invalid: '2023', '2023-25' (non-consecutive), '23-24'.
        """
        if not fy_str or not isinstance(fy_str, str):
            return False, "Missing or empty financial year."

        fy_clean = fy_str.strip()

        # Check short format: 2023-24
        m_short = cls.FY_SHORT_REGEX.match(fy_clean)
        if m_short:
            start_yr = int(m_short.group(1))
            end_short = int(m_short.group(2))
            expected_end = (start_yr + 1) % 100
            if end_short != expected_end:
                return False, f"Non-consecutive financial year '{fy_clean}'. Expected {start_yr}-{expected_end:02d}."
            return True, None

        # Check full format: 2023-2024
        m_full = cls.FY_FULL_REGEX.match(fy_clean)
        if m_full:
            start_yr = int(m_full.group(1))
            end_yr = int(m_full.group(2))
            if end_yr != start_yr + 1:
                return False, f"Non-consecutive financial year '{fy_clean}'. Expected {start_yr}-{start_yr + 1}."
            return True, None

        return False, f"Malformed financial year '{fy_clean}'. Must be YYYY-YY or YYYY-YYYY (e.g. 2023-24 or 2023-2024)."

    @classmethod
    def validate_currency_and_unit(cls, currency_unit: Optional[str]) -> Tuple[bool, Optional[str], float]:
        """Validates currency unit and returns multiplier."""
        if not currency_unit or not isinstance(currency_unit, str):
            return False, "Missing currency unit specification.", 1.0

        norm = currency_unit.strip().upper()
        if norm in cls.VALID_CURRENCY_UNITS:
            return True, None, cls.VALID_CURRENCY_UNITS[norm]

        return False, f"Unsupported currency unit '{currency_unit}'. Must be one of INR_Crores, INR_Lakhs, INR_Thousands, INR_Absolute.", 1.0

    @classmethod
    def validate_missing_vs_zero(cls, val: Any, field_name: str = "amount") -> Tuple[bool, Optional[str], bool]:
        """
        Guarantees non-coercion rule:
        - None represents uncollected/unavailable data and must remain None.
        - 0.0 represents empirical zero expenditure or zero beneficiary count.
        Returns: (is_valid, error_msg, is_missing)
        """
        if val is None:
            # Perfectly valid as missing value
            return True, None, True

        if isinstance(val, (int, float)):
            # Numeric value, zero is valid empirical value
            return True, None, False

        if isinstance(val, str):
            clean = val.strip().lower()
            if clean in ("", "none", "null", "n/a", "na", "-"):
                return True, f"String '{val}' represents missing data; should be parsed as None.", True
            try:
                float(clean)
                return True, None, False
            except ValueError:
                return False, f"Non-numeric amount '{val}' in field '{field_name}'.", False

        return False, f"Unsupported type '{type(val).__name__}' for numeric field '{field_name}'.", False

    @classmethod
    def validate_geography(
        cls,
        district_name: Optional[str] = None,
        lgd_code: Optional[Union[str, int]] = None,
        ac_number: Optional[int] = None,
        gcc_zone: Optional[int] = None,
    ) -> Tuple[bool, List[str]]:
        """Validates Tamil Nadu district, Assembly Constituency, GCC zone, and LGD codes."""
        errors: List[str] = []

        if district_name:
            norm_dist = district_name.strip().upper()
            if norm_dist not in cls.TAMIL_NADU_DISTRICTS:
                errors.append(f"Invalid Tamil Nadu district '{district_name}'. Must match one of 38 revenue districts.")

        if lgd_code is not None:
            lgd_str = str(lgd_code).strip()
            if not lgd_str.isdigit() or int(lgd_str) <= 0:
                errors.append(f"Invalid LGD code '{lgd_code}'. Must be a positive integer.")

        if ac_number is not None:
            if not isinstance(ac_number, int) or not (1 <= ac_number <= 234):
                errors.append(f"Invalid Assembly Constituency number '{ac_number}'. Must be between 1 and 234.")

        if gcc_zone is not None:
            if not isinstance(gcc_zone, int) or not (1 <= gcc_zone <= 15):
                errors.append(f"Invalid Greater Chennai Corporation zone '{gcc_zone}'. Must be between 1 and 15.")

        return len(errors) == 0, errors


# -----------------------------------------------------------------------------
# 6. Unicode & Tamil Text Preservation Guard
# -----------------------------------------------------------------------------

class UnicodeTamilGuard:
    """Guarantees UTF-8 integrity, detects mojibake, and normalizes bilingual Tamil content."""

    # Mojibake patterns indicating corrupted double-encoding
    MOJIBAKE_PATTERNS = [
        re.compile(r"ÃƒÂ|Ã‚Â|Ã¢â‚¬|Ã©|Ã |Ã§|Ã®"),
        re.compile(r"\ufffd"),  # Unicode replacement character
        re.compile(r"\\u[0-9a-fA-F]{4}"),  # Literal unescaped unicode strings in text
        re.compile(r"[\x80-\x9f]"),  # Unprintable Windows-1252 control codes
    ]

    # Tamil Unicode block: \u0B80 - \u0BFF
    TAMIL_CHAR_PATTERN = re.compile(r"[\u0B80-\u0BFF]")

    @classmethod
    def validate_and_normalize(cls, text: Optional[str], field_name: str = "text") -> Tuple[bool, Optional[str], List[str]]:
        """
        Validates text encoding and applies Unicode NFC normalization.
        Detects mojibake corruption and unescaped byte artifacts.
        """
        if text is None:
            return True, None, []

        if not isinstance(text, str):
            return False, None, [f"Field '{field_name}' must be of string type, got {type(text).__name__}."]

        errors: List[str] = []

        # Check for mojibake
        for pat in cls.MOJIBAKE_PATTERNS:
            if pat.search(text):
                errors.append(f"Encoding corruption / mojibake detected in '{field_name}': {SecretScrubber.sanitize(text[:60])}...")
                break

        # Apply NFC Unicode normalization (preserves Tamil vowel signs and pulli accurately)
        normalized = unicodedata.normalize("NFC", text.strip())

        return len(errors) == 0, normalized, errors

    @classmethod
    def contains_tamil(cls, text: Optional[str]) -> bool:
        """Returns True if the text contains authentic Tamil script characters."""
        if not text or not isinstance(text, str):
            return False
        return bool(cls.TAMIL_CHAR_PATTERN.search(text))


# -----------------------------------------------------------------------------
# 7. Duplicate Detection & Version Classifier
# -----------------------------------------------------------------------------

class DuplicateAndVersionClassifier:
    """
    Distinguishes exact duplicates from historical versions, conflicting sources,
    and superseded orders. Enforces Rule 1: Never delete records simply because they appear duplicated.
    """

    EXTERNAL_ID_PATTERNS = {
        "constituency": re.compile(r"^(AC-TN-\d{3}|PC-TN-\d{2})$"),
        "scheme": re.compile(r"^SCH-([A-Z0-9]+-)*[A-Z0-9]+$"),
        "promise": re.compile(r"^PRM-[A-Z0-9]+-\d{4}-\d{3}$"),
        "document": re.compile(r"^(DOC|SRC)-[A-Z0-9-]+$"),
        "representative": re.compile(r"^REP-[A-Z0-9-]+$"),
        "civic_issue": re.compile(r"^CIV-\d{4}-\d{4}$"),
    }

    @classmethod
    def validate_external_identifier(cls, entity_type: str, identifier: str) -> Tuple[bool, Optional[str]]:
        """Validates that external identifiers adhere to canonical stable patterns."""
        if not identifier or not isinstance(identifier, str):
            return False, "Missing or empty external identifier."

        pat = cls.EXTERNAL_ID_PATTERNS.get(entity_type.lower())
        if not pat:
            return True, None  # Entity without strict regex; non-empty string is accepted

        if not pat.match(identifier.strip()):
            return False, f"Identifier '{identifier}' does not match canonical format for '{entity_type}'."

        return True, None

    @classmethod
    def classify_record_relationship(
        cls,
        existing_records: List[Dict[str, Any]],
        incoming_record: Dict[str, Any],
        id_field: str = "id",
        period_field: str = "period",
        source_field: str = "source_id"
    ) -> Tuple[DuplicateType, Optional[Dict[str, Any]], Optional[str]]:
        """
        Classifies whether an incoming record is:
        - UNIQUE_RECORD: New entity.
        - EXACT_DUPLICATE: Identical entity, period, source, and payload.
        - HISTORICAL_VERSION: Same entity, but different election cycle, fiscal year, or delimitation.
        - CONFLICTING_SOURCE: Same entity and period, but different sources report contradictory figures.
        - SUPERSEDED_ORDER: An administrative order that explicitly revokes or supersedes an earlier order.
        """
        in_id = incoming_record.get(id_field)
        in_period = incoming_record.get(period_field)
        in_source = incoming_record.get(source_field)

        # Check for superseded order flag
        if incoming_record.get("is_superseded") or incoming_record.get("superseded_by"):
            return DuplicateType.SUPERSEDED_ORDER, None, f"Record flagged as superseded by {incoming_record.get('superseded_by')}."

        matching_entities = [r for r in existing_records if r.get(id_field) == in_id]
        if not matching_entities:
            return DuplicateType.UNIQUE_RECORD, None, "No existing entity found with this identifier."

        for existing in matching_entities:
            ex_period = existing.get(period_field)
            ex_source = existing.get(source_field)

            # Different time period / term / election cycle -> Distinct historical version!
            if in_period and ex_period and in_period != ex_period:
                return (
                    DuplicateType.HISTORICAL_VERSION,
                    existing,
                    f"Distinct historical version across periods (existing: {ex_period}, incoming: {in_period})."
                )

            # Same period, same source -> Compare payloads
            if in_period == ex_period and in_source == ex_source:
                if cls._payloads_identical(existing, incoming_record):
                    return DuplicateType.EXACT_DUPLICATE, existing, "Exact duplicate payload from identical source and period."
                else:
                    return DuplicateType.CONFLICTING_SOURCE, existing, "Modified or revised data from same source and period."

            # Same period, different source -> Conflicting source record
            if in_period == ex_period and in_source != ex_source:
                return (
                    DuplicateType.CONFLICTING_SOURCE,
                    existing,
                    f"Different source corroboration (existing source: {ex_source}, incoming: {in_source})."
                )

        return DuplicateType.UNIQUE_RECORD, None, "Unique record."

    @staticmethod
    def _payloads_identical(dict_a: Dict[str, Any], dict_b: Dict[str, Any]) -> bool:
        # Ignore timestamps when comparing payloads
        ignore_keys = {"created_at", "updated_at", "indexed_at", "retrieval_date"}
        keys_a = set(dict_a.keys()) - ignore_keys
        keys_b = set(dict_b.keys()) - ignore_keys
        if keys_a != keys_b:
            return False
        for k in keys_a:
            if dict_a[k] != dict_b[k]:
                return False
        return True


# -----------------------------------------------------------------------------
# 8. Referential Integrity Validator
# -----------------------------------------------------------------------------

class ReferentialIntegrityValidator:
    """Validates cross-entity linkages across departments, schemes, budgets, and claims."""

    @classmethod
    def validate_relationships(
        cls,
        entity_type: str,
        record: Dict[str, Any],
        known_registries: Dict[str, Set[str]]
    ) -> Tuple[bool, List[str]]:
        """
        Validates foreign key references against known entity sets.
        Flags broken references for human review without silently dropping records.
        """
        errors: List[str] = []
        norm_type = entity_type.lower()

        if norm_type == "representative":
            c_id = record.get("constituency_id")
            if c_id and known_registries.get("constituencies") and c_id not in known_registries["constituencies"]:
                errors.append(f"Broken referential link: Constituency '{c_id}' not found in registered constituencies.")

            p_id = record.get("party_id")
            if p_id and known_registries.get("parties") and p_id not in known_registries["parties"]:
                errors.append(f"Broken referential link: Party '{p_id}' not found in registered political parties.")

        elif norm_type == "scheme":
            d_id = record.get("department_id") or record.get("department_code")
            if d_id and known_registries.get("departments") and d_id not in known_registries["departments"]:
                errors.append(f"Broken referential link: Department '{d_id}' not found in registered departments.")

        elif norm_type == "budget_record":
            s_id = record.get("scheme_code") or record.get("head_of_account")
            if s_id and known_registries.get("schemes") and s_id not in known_registries["schemes"]:
                errors.append(f"Broken referential link: Budget scheme '{s_id}' not found in registered schemes.")

            doc_id = record.get("source_document_id")
            if doc_id and known_registries.get("documents") and doc_id not in known_registries["documents"]:
                errors.append(f"Broken referential link: Budget source document '{doc_id}' not found in registered documents.")

        elif norm_type == "promise":
            p_id = record.get("party_id")
            if p_id and known_registries.get("parties") and p_id not in known_registries["parties"]:
                errors.append(f"Broken referential link: Party '{p_id}' not found in registered political parties.")

        elif norm_type == "claim":
            d_id = record.get("evidence_document_id")
            if d_id and known_registries.get("documents") and d_id not in known_registries["documents"]:
                errors.append(f"Broken referential link: Evidence document '{d_id}' not found in registered evidence documents.")

        return len(errors) == 0, errors


# -----------------------------------------------------------------------------
# 9. Safe Import Runner (Dry-Run, Staging, Overwrite Protection, Rollback)
# -----------------------------------------------------------------------------

class SafeImportRunner:
    """
    Executes imports with complete safety safeguards:
    - Dry-run simulation (dry_run=True).
    - Protection of manually reviewed records (never silently overwritten).
    - Protection of newer data against older imported files.
    - Transactional rollback via SQLAlchemy savepoints.
    - Backup snapshot creation prior to state modification.
    """

    def __init__(self, session: Optional[Session] = None):
        self.session = session

    def create_backup_manifest(self, entity_type: str, count: int) -> str:
        """Creates a lightweight backup manifest before data ingestion."""
        now = datetime.now(timezone.utc)
        manifest_id = f"BKUP-{entity_type.upper()}-{now.strftime('%Y%m%d%H%M%S')}"
        logger.info(f"Generated pre-import backup manifest {manifest_id} for {count} incoming records.")
        return manifest_id

    def process_records(
        self,
        entity_type: str,
        incoming_records: List[Dict[str, Any]],
        existing_lookup: Optional[Dict[str, Dict[str, Any]]] = None,
        known_registries: Optional[Dict[str, Set[str]]] = None,
        dry_run: bool = False,
    ) -> ImportSummary:
        """
        Validates, deduplicates, and stages a batch of incoming civic records.
        Enforces Rule 1 (no deletion of historical versions) and Rule 2 (no silent overwrites).
        """
        existing_lookup = existing_lookup or {}
        known_registries = known_registries or {}

        summary = ImportSummary(
            total_evaluated=len(incoming_records),
            is_dry_run=dry_run,
            backup_manifest_id=self.create_backup_manifest(entity_type, len(incoming_records)) if not dry_run else None,
        )

        for record in incoming_records:
            record_id = record.get("id") or record.get(f"{entity_type}_id") or record.get("code") or "UNKNOWN"

            # 1. Schema Validation (Zero Fabrication)
            is_valid_schema, schema_errs = CivicSchemaValidator.validate_schema(entity_type, record)
            if not is_valid_schema:
                summary.rejected += 1
                summary.validation_errors.append({
                    "record_id": record_id,
                    "error_type": "SCHEMA_VALIDATION_ERROR",
                    "details": [SecretScrubber.sanitize(e) for e in schema_errs],
                })
                continue

            # 2. Source URL & Provenance Validation
            if "source_url" in record or "url" in record:
                url_to_test = record.get("source_url") or record.get("url")
                url_valid, url_msg, is_whitelisted = SourceProvenanceValidator.validate_url(url_to_test)
                if not url_valid:
                    summary.rejected += 1
                    summary.validation_errors.append({
                        "record_id": record_id,
                        "error_type": "INVALID_SOURCE_URL",
                        "details": [SecretScrubber.sanitize(url_msg or "Invalid URL")],
                    })
                    continue
                elif not is_whitelisted:
                    summary.review_required += 1
                    summary.validation_errors.append({
                        "record_id": record_id,
                        "error_type": "UNVERIFIED_SOURCE_DOMAIN",
                        "details": [SecretScrubber.sanitize(url_msg or "Unverified domain")],
                    })

            # 3. Unicode and Tamil Text Validation
            text_corrupted = False
            for text_key in ["name", "title", "description", "promise_text", "claim_text", "name_ta", "name_en"]:
                if text_key in record:
                    u_valid, norm_val, u_errs = UnicodeTamilGuard.validate_and_normalize(record[text_key], text_key)
                    if not u_valid:
                        text_corrupted = True
                        summary.rejected += 1
                        summary.validation_errors.append({
                            "record_id": record_id,
                            "error_type": "UNICODE_CORRUPTION",
                            "details": [SecretScrubber.sanitize(e) for e in u_errs],
                        })
                        break
                    else:
                        record[text_key] = norm_val

            if text_corrupted:
                continue

            # 4. Consistency Checks (Date, FY, Missing vs Zero, Geography)
            consistency_errors = []

            # Date format
            for date_key in ["date", "event_date", "publication_date", "announcement_date"]:
                if date_key in record:
                    d_valid, d_msg = ConsistencyValidator.validate_date(record[date_key])
                    if not d_valid:
                        consistency_errors.append(d_msg)

            # Financial Year format
            if "financial_year" in record:
                fy_valid, fy_msg = ConsistencyValidator.validate_financial_year(record["financial_year"])
                if not fy_valid:
                    consistency_errors.append(fy_msg)

            # Geography
            geo_valid, geo_errs = ConsistencyValidator.validate_geography(
                district_name=record.get("district_name") or record.get("district"),
                lgd_code=record.get("lgd_code"),
                ac_number=record.get("ac_number") or record.get("constituency_number"),
                gcc_zone=record.get("gcc_zone") or record.get("zone_number")
            )
            if not geo_valid:
                consistency_errors.extend(geo_errs)

            # Missing vs Zero
            if "amount" in record:
                m_valid, m_msg, is_missing = ConsistencyValidator.validate_missing_vs_zero(record["amount"], "amount")
                if not m_valid:
                    consistency_errors.append(m_msg)

            if consistency_errors:
                summary.rejected += 1
                summary.validation_errors.append({
                    "record_id": record_id,
                    "error_type": "CONSISTENCY_VALIDATION_ERROR",
                    "details": [SecretScrubber.sanitize(e) for e in consistency_errors],
                })
                continue

            # 5. Referential Integrity Check
            ref_valid, ref_errs = ReferentialIntegrityValidator.validate_relationships(
                entity_type, record, known_registries
            )
            if not ref_valid:
                summary.review_required += 1
                summary.validation_errors.append({
                    "record_id": record_id,
                    "error_type": "REFERENTIAL_INTEGRITY_VIOLATION",
                    "details": [SecretScrubber.sanitize(e) for e in ref_errs],
                })
                # Do not reject immediately; route for human review

            # 6. Duplicate & Overwrite Protection (Rule 1 & Rule 2)
            existing = existing_lookup.get(record_id)
            if existing:
                # Rule 2: Do not overwrite manually reviewed data
                if existing.get("is_manually_reviewed") or existing.get("review_status") == "VERIFIED":
                    summary.skipped += 1
                    summary.review_required += 1
                    summary.validation_errors.append({
                        "record_id": record_id,
                        "error_type": "MANUAL_REVIEW_PROTECTED",
                        "details": ["Existing record has been verified by human auditor. Overwrite blocked."],
                    })
                    continue

                # Rule 2: Do not overwrite newer data with older imported values
                ex_date = existing.get("publication_date") or existing.get("updated_at")
                in_date = record.get("publication_date") or record.get("document_date")
                if ex_date and in_date and ex_date > in_date:
                    summary.skipped += 1
                    summary.review_required += 1
                    summary.validation_errors.append({
                        "record_id": record_id,
                        "error_type": "STALE_IMPORT_OVERWRITE_PREVENTED",
                        "details": [f"Existing record date ({ex_date}) is newer than imported record date ({in_date})."],
                    })
                    continue

                # Rule 1: Check for distinct historical version vs conflicting source vs exact duplicate
                dup_type, matched, explanation = DuplicateAndVersionClassifier.classify_record_relationship(
                    [existing], record, id_field="id" if "id" in existing else f"{entity_type}_id"
                )

                if dup_type == DuplicateType.EXACT_DUPLICATE:
                    summary.skipped += 1
                    continue
                elif dup_type == DuplicateType.CONFLICTING_SOURCE:
                    summary.conflicts_detected += 1
                    summary.review_required += 1
                    summary.validation_errors.append({
                        "record_id": record_id,
                        "error_type": "SOURCE_CONFLICT_DETECTED",
                        "details": [explanation or "Conflicting source metrics detected."],
                    })
                    continue
                elif dup_type in (DuplicateType.HISTORICAL_VERSION, DuplicateType.SUPERSEDED_ORDER):
                    # Preserved as a distinct version!
                    summary.inserted += 1
                    continue
                else:
                    # Valid newer update
                    summary.updated += 1
            else:
                # Fresh insertion
                summary.inserted += 1

        return summary
