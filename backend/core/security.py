"""
CivicLens TN - Core Security and Access Control Module
Provides centralized authentication verification, role validation, API key verification,
and request security utilities without external heavy frameworks.
"""
import hmac
from typing import Optional, Set, Dict, Any
from flask import Request, has_request_context, request
from backend.core.config import config


def verify_api_key(req: Optional[Request] = None) -> bool:
    """
    Verifies the request provides a valid API key when REVIEWER_API_KEY is configured.
    If REVIEWER_API_KEY is empty (dev/testing default), passes without requiring a key.
    Supports 'X-API-Key' header and 'Authorization: Bearer <key>'.
    Uses hmac.compare_digest to prevent timing attacks.
    """
    expected_key = getattr(config, "REVIEWER_API_KEY", "")
    if not expected_key:
        return True

    if req is None:
        if not has_request_context():
            return True
        req = request

    provided_key = req.headers.get("X-API-Key")
    if not provided_key:
        auth_header = req.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            provided_key = auth_header[7:].strip()

    if not provided_key:
        return False

    return hmac.compare_digest(provided_key, expected_key)


def verify_reviewer_security(
    req: Request,
    payload: Optional[Dict[str, Any]] = None,
    allowed_roles: Optional[Set[str]] = None,
) -> Optional[str]:
    """
    Validates reviewer authorization role and API key.
    Returns error message string if unauthorized, or None if authorized.
    """
    payload = payload or {}
    role = req.headers.get("X-Reviewer-Role") or payload.get("reviewer_role")
    if not role:
        return "Access Denied: Missing required reviewer authorization role (X-Reviewer-Role header or reviewer_role payload)."

    role_clean = role.strip().upper()
    if allowed_roles and role_clean not in allowed_roles:
        return f"Access Denied: Role '{role}' is not authorized to perform review operations. Authorized roles: {sorted(list(allowed_roles))}"

    if not verify_api_key(req):
        return "Access Denied: Invalid or missing reviewer API key."

    return None
