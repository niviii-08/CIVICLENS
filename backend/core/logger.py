import logging
import re
import sys
from backend.core.config import config

SENSITIVE_PATTERNS = [
    re.compile(r'(?i)(bearer\s+)([a-zA-Z0-9_\-\.]{8,})'),
    re.compile(r'(?i)(["\']?(?:api[_-]?key|secret[_-]?key|secret|password|access_token|refresh_token)["\']?\s*[:=]\s*["\']?)([^"\'\s,}{]+)'),
]

class SensitiveDataRedactor(logging.Filter):
    """Logging filter that scrubs authentication tokens and secrets from log messages."""
    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            msg = record.msg
            for pattern in SENSITIVE_PATTERNS:
                msg = pattern.sub(r'\1***REDACTED***', msg)
            record.msg = msg
        return True

def setup_logger(name: str) -> logging.Logger:
    """
    Centralized logger factory.
    Creates structured JSON logs in production and readable logs in debug mode.
    Attaches sensitive data redactor to prevent credential leakage in logs.
    """
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    level = logging.DEBUG if config.DEBUG else logging.INFO
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(SensitiveDataRedactor())

    if config.DEBUG:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '{"time": "%(asctime)s", "name": "%(name)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
