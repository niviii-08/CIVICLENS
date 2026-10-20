"""
Phase 12.2 Security Hardening Verification Tests
Tests for:
- FINDING-SEC-01: Anonymous default role remediation on claims review.
- FINDING-SEC-02: Reviewer API key verification against header spoofing.
- FINDING-SEC-03: CORS origin restrictions.
- FINDING-SEC-04: Debug mode safety & stack trace protection.
- FINDING-SEC-05: Startup configuration validation in production.
- FINDING-SEC-06: Defensive HTTP security headers.
- Sensitive credential redacting in logs and representations.
"""

import logging
import pytest
from backend.api.app import create_app
from backend.core.config import Config, config
from backend.core.logger import SensitiveDataRedactor
from backend.core.security import verify_api_key, verify_reviewer_security
from backend.models.claim import Claim, ClaimCategory


def test_sec_01_claim_review_anonymous_rejected(api_client):
    """
    Verifies that POST /api/claims/<id>/review rejects requests without reviewer role
    rather than defaulting to 'DOMAIN_EXPERT' (Remediating FINDING-SEC-01).
    """
    res = api_client.post(
        "/api/claims/CLM-SEC-TEST-01/review",
        json={"reviewer_id": "ANON_USER", "action": "accept_assessment"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert "Access Denied" in data["message"]
    assert "Missing required reviewer authorization role" in data["message"]


def test_sec_01_claim_review_unauthorized_role_rejected(api_client):
    """
    Verifies that unauthorized roles (e.g. PUBLIC_USER) are strictly denied with 403.
    """
    res = api_client.post(
        "/api/claims/CLM-SEC-TEST-01/review",
        headers={"X-Reviewer-Role": "PUBLIC_USER"},
        json={"reviewer_id": "GUEST", "action": "accept_assessment"}
    )
    assert res.status_code == 403
    data = res.get_json()
    assert "Access Denied" in data["message"]
    assert "not authorized" in data["message"]


def test_sec_02_api_key_verification_enforcement(monkeypatch):
    """
    Verifies that when REVIEWER_API_KEY is configured, requests without valid
    X-API-Key or Bearer token are denied (Remediating FINDING-SEC-02).
    """
    monkeypatch.setattr(config, "REVIEWER_API_KEY", "super-secret-reviewer-token-12345")

    app = create_app(validate_config=False)
    app.config["TESTING"] = True

    with app.test_client() as client:
        # 1. Privileged role supplied, but NO API key -> 403
        res_no_key = client.post(
            "/api/claims/CLM-SEC-TEST-02/review",
            headers={"X-Reviewer-Role": "ADMIN"},
            json={"reviewer_id": "ADMIN-01", "action": "accept_assessment"}
        )
        assert res_no_key.status_code == 403
        assert "Invalid or missing reviewer API key" in res_no_key.get_json()["message"]

        # 2. Privileged role supplied with WRONG API key -> 403
        res_bad_key = client.post(
            "/api/claims/CLM-SEC-TEST-02/review",
            headers={
                "X-Reviewer-Role": "ADMIN",
                "X-API-Key": "wrong-token-value"
            },
            json={"reviewer_id": "ADMIN-01", "action": "accept_assessment"}
        )
        assert res_bad_key.status_code == 403
        assert "Invalid or missing reviewer API key" in res_bad_key.get_json()["message"]

        # 3. Privileged role supplied with VALID Bearer token -> passes security check
        # (It will proceed past security check to claim lookup; returning 404 because claim doesn't exist, not 403)
        res_valid_key = client.post(
            "/api/claims/CLM-SEC-TEST-02/review",
            headers={
                "X-Reviewer-Role": "ADMIN",
                "Authorization": "Bearer super-secret-reviewer-token-12345"
            },
            json={"reviewer_id": "ADMIN-01", "action": "accept_assessment"}
        )
        # Should NOT be 403 (security check passed)
        assert res_valid_key.status_code != 403


def test_sec_03_cors_origin_restriction(monkeypatch):
    """
    Verifies that CORS origins are restricted to configured values rather than wildcard '*'
    (Remediating FINDING-SEC-03).
    """
    monkeypatch.setattr(config, "ALLOWED_ORIGINS", ["http://localhost:3000", "https://civiclens.tn.gov.in"])

    app = create_app(validate_config=False)
    app.config["TESTING"] = True

    with app.test_client() as client:
        # Request from allowed origin
        res_allowed = client.get(
            "/api/health",
            headers={"Origin": "https://civiclens.tn.gov.in"}
        )
        assert res_allowed.headers.get("Access-Control-Allow-Origin") == "https://civiclens.tn.gov.in"

        # Request from untrusted malicious origin
        res_disallowed = client.get(
            "/api/health",
            headers={"Origin": "https://malicious-attacker-domain.com"}
        )
        assert res_disallowed.headers.get("Access-Control-Allow-Origin") != "https://malicious-attacker-domain.com"


def test_sec_04_debug_default_and_error_scrubbing(monkeypatch):
    """
    Verifies that DEBUG defaults to False and production 500 errors omit stack traces
    (Remediating FINDING-SEC-04).
    """
    cfg = Config()
    assert cfg.DEBUG is False, "DEBUG must default to False when environment variable is unset"

    monkeypatch.setattr(config, "DEBUG", False)
    app = create_app(validate_config=False)
    app.config["TESTING"] = True

    @app.route("/api/test-crash")
    def trigger_crash():
        raise RuntimeError("Internal private system failure details C:\\secret\\path")

    with app.test_client() as client:
        res = client.get("/api/test-crash")
        assert res.status_code == 500
        data = res.get_json()
        assert data["message"] == "An unexpected server error occurred."
        assert data.get("details") is None, "Stack trace details must be None in production"


def test_sec_05_startup_config_validation():
    """
    Verifies that startup configuration validation raises clear, safe errors when
    critical production settings are missing or insecure (Remediating FINDING-SEC-05).
    """
    cfg = Config()
    cfg.ENV = "production"
    cfg.SECRET_KEY = ""
    cfg.REVIEWER_API_KEY = ""
    cfg.DEBUG = True

    with pytest.raises(ValueError) as excinfo:
        cfg.validate()

    err_text = str(excinfo.value)
    assert "SECRET_KEY must be configured" in err_text
    assert "DEBUG mode must not be enabled when ENV=production" in err_text
    assert "REVIEWER_API_KEY must be configured" in err_text
    # Ensure no secret strings are leaked in error
    assert "change-me" not in err_text


def test_sec_06_http_security_headers(api_client):
    """
    Verifies that backend responses inject standard OWASP defense-in-depth headers
    (Remediating FINDING-SEC-06).
    """
    res = api_client.get("/health")
    assert res.status_code == 200
    assert res.headers.get("X-Content-Type-Options") == "nosniff"
    assert res.headers.get("X-Frame-Options") == "DENY"
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"
    assert res.headers.get("Referrer-Policy") == "strict-origin-when-cross-origin"


def test_ops_02_max_content_length(api_client):
    """
    Verifies that MAX_CONTENT_LENGTH is configured on Flask app (Remediating FINDING-OPS-02).
    """
    assert api_client.application.config.get("MAX_CONTENT_LENGTH") == 16 * 1024 * 1024


def test_secret_redaction_in_repr_and_logs():
    """
    Verifies that Config.__repr__ and logger redaction filter mask sensitive keys.
    """
    cfg = Config()
    cfg.SECRET_KEY = "my-super-secret-key"
    cfg.REVIEWER_API_KEY = "my-reviewer-key"
    cfg_repr = repr(cfg)

    assert "my-super-secret-key" not in cfg_repr
    assert "my-reviewer-key" not in cfg_repr
    assert "***REDACTED***" in cfg_repr

    # Test logger filter
    redactor = SensitiveDataRedactor()
    record = logging.LogRecord(
        name="test", level=logging.INFO, pathname="test.py", lineno=1,
        msg="Authenticated user with Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 and api_key=supersecret123",
        args=(), exc_info=None
    )
    redactor.filter(record)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in record.msg
    assert "supersecret123" not in record.msg
    assert "***REDACTED***" in record.msg
