from flask import jsonify, g, has_app_context
from typing import Any, Dict, Tuple, Optional

def success_response(data: Any = None, message: str = "Success", status_code: int = 200) -> Tuple[Any, int]:
    """
    Standardize all successful API responses.
    """
    response: Dict[str, Any] = {"status": "success", "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code

def error_response(
    message: str,
    error_details: Any = None,
    status_code: int = 400,
    request_id: Optional[str] = None
) -> Tuple[Any, int]:
    """
    Standardize all error API responses.
    Automatically attaches request correlation ID for safe, privacy-preserving diagnostics.
    """
    response: Dict[str, Any] = {"status": "error", "message": message}
    if error_details:
        response["details"] = error_details

    req_id = request_id
    if not req_id and has_app_context() and hasattr(g, 'request_id'):
        req_id = g.request_id

    if req_id:
        response["request_id"] = req_id

    return jsonify(response), status_code
