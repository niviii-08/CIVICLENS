import json
import logging
from unittest.mock import patch, MagicMock
from flask import g
from sqlalchemy.exc import OperationalError

from backend.api.app import create_app
from backend.core.config import config
from backend.core.logger import (
    SensitiveDataRedactor,
    JsonFormatter,
    TextFormatter,
    redact_text,
    setup_logger
)


def test_health_liveness_endpoints(api_client):
    """Verifies that liveness probes return 200 OK without performing database queries."""
    for path in ("/health", "/health/live", "/api/health", "/api/health/live"):
        res = api_client.get(path)
        assert res.status_code == 200
        body = res.get_json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "healthy"
        assert "X-Request-ID" in res.headers


def test_health_readiness_healthy(api_client):
    """Verifies that readiness probe returns 200 and confirms database readiness."""
    for path in ("/health/ready", "/health/db", "/api/health/ready"):
        res = api_client.get(path)
        assert res.status_code == 200
        body = res.get_json()
        assert body["status"] == "success"
        assert body["data"]["status"] == "ready"
        assert body["data"]["database"] == "connected"


def test_health_readiness_failure_scrubbed(monkeypatch):
    """
    Verifies that when database connectivity fails:
    1. Returns HTTP 503 Service Unavailable.
    2. Does NOT leak internal file paths, credentials, or SQL tracebacks.
    """
    app = create_app()
    app.config['TESTING'] = True

    with patch("backend.api.app.SessionLocal") as mock_session_local:
        mock_db = MagicMock()
        mock_db.execute.side_effect = OperationalError(
            "SELECT 1", {}, Exception("sqlite3.OperationalError: unable to open database file at /var/data/private.db")
        )
        mock_session_local.return_value = mock_db

        with app.test_client() as client:
            res = client.get("/health/ready")
            assert res.status_code == 503
            body = res.get_json()
            assert body["status"] == "error"
            assert "database connection check failed" in body["message"]

            # Ensure sensitive internal paths are not exposed in production mode
            body_str = json.dumps(body)
            assert "/var/data/private.db" not in body_str
            assert "unable to open database file" not in body_str


def test_request_correlation_headers(api_client):
    """Verifies that X-Request-ID header is generated and custom IDs are respected."""
    # Automatic generation
    res1 = api_client.get("/health")
    req_id_1 = res1.headers.get("X-Request-ID")
    assert req_id_1 is not None
    assert req_id_1.startswith("req_")

    # Client-supplied valid X-Request-ID
    custom_id = "citizen-audit-trace-20261021"
    res2 = api_client.get("/health", headers={"X-Request-ID": custom_id})
    assert res2.headers.get("X-Request-ID") == custom_id

    # Malformed client-supplied X-Request-ID is replaced with a safe generated ID
    malformed_id = "bad id with spaces; DROP TABLE students; --"
    res3 = api_client.get("/health", headers={"X-Request-ID": malformed_id})
    req_id_3 = res3.headers.get("X-Request-ID")
    assert req_id_3 != malformed_id
    assert req_id_3.startswith("req_")


def test_error_response_contains_request_id():
    """Verifies that 500 error responses correlate to the X-Request-ID for safe troubleshooting."""
    app = create_app()
    app.config['TESTING'] = True

    @app.route("/test-crash")
    def test_crash():
        raise RuntimeError("Controlled crash for testing")

    with app.test_client() as client:
        custom_id = "trace-err-99887766"
        res = client.get("/test-crash", headers={"X-Request-ID": custom_id})
        assert res.status_code == 500
        assert res.headers.get("X-Request-ID") == custom_id
        body = res.get_json()
        assert body["status"] == "error"
        assert body["request_id"] == custom_id


def test_sensitive_data_redaction():
    """Verifies that SensitiveDataRedactor scrubs tokens, credentials, and citizen PII."""
    redactor = SensitiveDataRedactor()

    # 1. Bearer token
    rec1 = logging.LogRecord("test", logging.INFO, "test.py", 1, "User auth Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9", (), None)
    redactor.filter(rec1)
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in rec1.msg
    assert "Bearer ***REDACTED***" in rec1.msg

    # 2. Key-value secrets and API keys
    rec2 = logging.LogRecord("test", logging.INFO, "test.py", 1, 'Config: api_key="super-secret-key-12345", password=dbpass99', (), None)
    redactor.filter(rec2)
    assert "super-secret-key-12345" not in rec2.msg
    assert "dbpass99" not in rec2.msg

    # 3. HTTP Cookie and Authorization headers
    rec3 = logging.LogRecord("test", logging.INFO, "test.py", 1, "Headers: Cookie: session_token=abcd1234efgh; user=admin", (), None)
    redactor.filter(rec3)
    assert "session_token=abcd1234efgh" not in rec3.msg

    # 4. Database URI passwords
    rec4 = logging.LogRecord("test", logging.INFO, "test.py", 1, "Connecting to postgresql://civic_admin:p@ssword123@db.prod.internal:5432/civiclens", (), None)
    redactor.filter(rec4)
    assert "p@ssword123" not in rec4.msg
    assert "postgresql://civic_admin:***REDACTED***@db.prod.internal:5432/civiclens" in rec4.msg

    # 5. Citizen PII (Aadhaar number)
    rec5 = logging.LogRecord("test", logging.INFO, "test.py", 1, "Beneficiary Aadhaar: 9876 5432 1098 submitted application", (), None)
    redactor.filter(rec5)
    assert "9876 5432 1098" not in rec5.msg
    assert "[AADHAAR_REDACTED]" in rec5.msg

    # 6. Citizen PII (Mobile phone number)
    rec6 = logging.LogRecord("test", logging.INFO, "test.py", 1, "Grievance SMS sent to +91 9840123456", (), None)
    redactor.filter(rec6)
    assert "9840123456" not in rec6.msg
    assert "[PHONE_REDACTED]" in rec6.msg


def test_json_formatter_validity():
    """Verifies that JsonFormatter outputs valid, single-line JSON with required schema fields."""
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="civiclens.test",
        level=logging.WARNING,
        pathname="test.py",
        lineno=42,
        msg='Testing quote "escaping" and\nmultiline text',
        args=(),
        exc_info=None
    )
    setattr(record, "request_id", "req_test123456")
    setattr(record, "status_code", 400)
    setattr(record, "duration_ms", 15.6)

    formatted = formatter.format(record)
    assert "\n" not in formatted  # Single-line JSON

    parsed = json.loads(formatted)
    assert parsed["logger"] == "civiclens.test"
    assert parsed["level"] == "WARNING"
    assert 'Testing quote "escaping" and\nmultiline text' in parsed["message"]
    assert parsed["request_id"] == "req_test123456"
    assert parsed["status_code"] == 400
    assert parsed["duration_ms"] == 15.6
    assert "timestamp" in parsed
