import json
import logging
import re
import sys
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from flask import has_app_context, g
from backend.core.config import config

# Comprehensive redaction patterns for credentials, tokens, and citizen PII
SENSITIVE_PATTERNS = [
    # Bearer tokens
    (re.compile(r'(?i)(bearer\s+)([a-zA-Z0-9_\-\.]{8,})'), r'\1***REDACTED***'),
    # Basic authentication credentials
    (re.compile(r'(?i)(basic\s+)([a-zA-Z0-9+/=]{8,})'), r'\1***REDACTED***'),
    # Key-value secret configurations and headers
    (
        re.compile(r'(?i)(["\']?(?:api[_-]?key|secret[_-]?key|secret|password|access_token|refresh_token|private_key|auth_token)["\']?\s*[:=]\s*["\']?)([^"\'\s,}{]+)'),
        r'\1***REDACTED***'
    ),
    # HTTP Authorization and Cookie headers
    (
        re.compile(r'(?i)((?:authorization|proxy-authorization|cookie|set-cookie)\s*:\s*)([^\r\n]+)'),
        r'\1***REDACTED***'
    ),
    # Database connection URIs with embedded passwords (e.g. postgresql://user:pass@host:5432/db)
    (
        re.compile(r'(?i)(://[^:\s/]+:)(.*)(@(?:[a-zA-Z0-9_\-\.]+)(?::\d+)?(?:/|$|\s))'),
        r'\1***REDACTED***\3'
    ),
    # Citizen Aadhaar numbers (12-digit Indian national identity numbers, e.g. 1234-5678-9012 or 1234 5678 9012)
    (
        re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        r'[AADHAAR_REDACTED]'
    ),
    # Citizen 10-digit mobile phone numbers starting with 6, 7, 8, or 9 (with optional country code +91)
    (
        re.compile(r'\b(?:\+?91[-\s]?)?[6-9]\d{9}\b'),
        r'[PHONE_REDACTED]'
    ),
]


def redact_text(text: str) -> str:
    """Utility function to scrub credentials and personal identifiers from any string."""
    if not isinstance(text, str):
        return text
    scrubbed = text
    for pattern, replacement in SENSITIVE_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed


class SensitiveDataRedactor(logging.Filter):
    """Logging filter that scrubs authentication tokens, secrets, and citizen PII from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = redact_text(record.msg)

        # Also scrub string arguments if parameterized logging was used (e.g. logger.info("%s", secret))
        if record.args:
            if isinstance(record.args, tuple):
                record.args = tuple(redact_text(a) if isinstance(a, str) else a for a in record.args)
            elif isinstance(record.args, dict):
                record.args = {k: (redact_text(v) if isinstance(v, str) else v) for k, v in record.args.items()}

        return True


class JsonFormatter(logging.Formatter):
    """
    Format log records as valid, single-line JSON objects for operational log aggregators
    (CloudWatch, Datadog, ELK, Grafana Loki).
    """

    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }

        # Automatically bind request correlation ID if available
        req_id = getattr(record, "request_id", None)
        if not req_id and has_app_context() and hasattr(g, "request_id"):
            req_id = g.request_id
        if req_id:
            log_obj["request_id"] = req_id

        # Bind HTTP operational telemetry if attached
        for field in ("method", "path", "status_code", "duration_ms"):
            val = getattr(record, field, None)
            if val is not None:
                log_obj[field] = val

        # Bind sanitized exception metadata
        if record.exc_info and record.exc_info[0]:
            log_obj["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": redact_text(str(record.exc_info[1])) if record.exc_info[1] else "",
            }
            # Only include full traceback in JSON when debug mode is explicitly active
            if config.DEBUG:
                log_obj["exception"]["traceback"] = redact_text(self.formatException(record.exc_info))

        return json.dumps(log_obj, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Human-readable formatter for local interactive debugging."""

    def format(self, record: logging.LogRecord) -> str:
        req_id = getattr(record, "request_id", None)
        if not req_id and has_app_context() and hasattr(g, "request_id"):
            req_id = g.request_id

        req_ctx = f" [req:{req_id}]" if req_id else ""
        asctime = self.formatTime(record, self.datefmt)
        msg = record.getMessage()

        base = f"{asctime} [{record.levelname}] {record.name}{req_ctx}: {msg}"
        if record.exc_info:
            base += "\n" + redact_text(self.formatException(record.exc_info))
        return base


def get_formatter() -> logging.Formatter:
    """Returns JSON formatter for production and text formatter for debug mode."""
    if config.DEBUG:
        return TextFormatter()
    return JsonFormatter()


def setup_logger(name: str) -> logging.Logger:
    """
    Centralized logger factory.
    Creates structured JSON logs in production and readable logs in debug mode.
    Attaches sensitive data redactor to prevent credential and PII leakage.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = logging.DEBUG if config.DEBUG else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(SensitiveDataRedactor())
    handler.setFormatter(get_formatter())
    logger.addHandler(handler)

    # Prevent duplicating logs if root logger also handles it
    logger.propagate = False

    return logger


def configure_logging(app=None):
    """Configures centralized logging for the application and optional Flask instance."""
    level = logging.DEBUG if config.DEBUG else logging.INFO
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Attach redactor and formatter to all root handlers
    formatter = get_formatter()
    redactor = SensitiveDataRedactor()

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.addFilter(redactor)
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setLevel(level)
            handler.addFilter(redactor)
            handler.setFormatter(formatter)

    if app:
        app.logger.setLevel(level)
        for handler in app.logger.handlers:
            handler.addFilter(redactor)
            handler.setFormatter(formatter)
