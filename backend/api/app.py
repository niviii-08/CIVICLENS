import os
import re
import time
import uuid
from flask import Flask, request, g, send_file
from flask_cors import CORS
from sqlalchemy import text
from backend.core.config import config
from backend.core.logger import configure_logging, setup_logger
from backend.database.session import SessionLocal
from backend.api.routes import api_bp
from backend.api.errors import error_bp
from backend.api.responses import success_response, error_response

logger = setup_logger("civiclens.access")

def create_app(validate_config: bool = True):
    """Application factory for configuring and starting the Flask backend."""
    if validate_config:
        config.validate()

    configure_logging()

    app = Flask(config.APP_NAME)
    app.secret_key = config.SECRET_KEY or "dev-fallback-secret-key-civiclens-tn"
    app.config['MAX_CONTENT_LENGTH'] = config.MAX_CONTENT_LENGTH

    # Restrict CORS to configured allowed origins
    CORS(
        app,
        resources={
            r"/api/*": {"origins": config.ALLOWED_ORIGINS},
            r"/health*": {"origins": "*"},
            r"/version": {"origins": "*"},
        },
        supports_credentials=True,
    )

    app.register_blueprint(error_bp)
    app.register_blueprint(api_bp)

    @app.before_request
    def start_timer_and_correlation():
        """Assign request start time and validate/generate request correlation ID."""
        g.start_time = time.time()
        incoming_id = request.headers.get("X-Request-ID", "").strip()
        # Accept valid alphanumeric / dash / underscore client IDs (length 8-64); generate fresh if absent or malformed
        if incoming_id and re.match(r'^[a-zA-Z0-9_\-]{8,64}$', incoming_id):
            g.request_id = incoming_id
        else:
            g.request_id = f"req_{uuid.uuid4().hex[:16]}"

    @app.after_request
    def log_and_correlate_request(response):
        """Inject OWASP security headers, correlation headers, and emit structured access log."""
        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if not config.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

        # Response correlation header
        req_id = getattr(g, 'request_id', 'unknown')
        response.headers['X-Request-ID'] = req_id

        # Operational telemetry and latency calculation
        duration_ms = round((time.time() - getattr(g, 'start_time', time.time())) * 1000, 2)
        status_code = response.status_code
        log_msg = f"{request.method} {request.path} -> {status_code} ({duration_ms}ms)"

        extra = {
            "request_id": req_id,
            "method": request.method,
            "path": request.path,
            "status_code": status_code,
            "duration_ms": duration_ms
        }

        # Keep health check polling at DEBUG level to avoid polluting production operational streams
        if request.path.startswith('/health'):
            logger.debug(log_msg, extra=extra)
        elif status_code >= 500:
            logger.error(log_msg, extra=extra)
        elif status_code >= 400:
            logger.warning(log_msg, extra=extra)
        else:
            logger.info(log_msg, extra=extra)

        return response

    @app.route('/health', methods=['GET'])
    @app.route('/health/live', methods=['GET'])
    def health_live():
        """
        Liveness probe: verifies the process is alive and accepting connections.
        Fast and non-blocking; does not query backing services to prevent cascading failures.
        """
        return success_response(
            data={"status": "healthy", "check": "liveness"},
            message="Application is running"
        )

    @app.route('/health/ready', methods=['GET'])
    @app.route('/health/db', methods=['GET'])
    def health_ready():
        """
        Readiness probe: validates required dependencies (database connectivity).
        Returns 200 OK when ready to serve traffic; 503 Service Unavailable when dependency fails.
        Never exposes connection strings, internal paths, or credentials publicly.
        """
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return success_response(
                data={"status": "ready", "database": "connected"},
                message="Service is ready to handle traffic"
            )
        except Exception as e:
            # Safe internal error logging; sanitized public response
            logger.error(f"Readiness check failed on database probe: {e}", exc_info=True)
            details = "Database connection failed" if config.DEBUG else None
            return error_response(
                message="Service unavailable: database connection check failed",
                error_details=details,
                status_code=503
            )
        finally:
            db.close()

    @app.route('/version', methods=['GET'])
    def get_version():
        return success_response(data={"version": "0.1.0"}, message="Version retrieved")

    @app.route('/launch', methods=['GET'])
    @app.route('/', methods=['GET'])
    def serve_launch():
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        index_path = os.path.join(root_dir, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        return success_response(data={"status": "healthy"}, message="CivicLens API Running")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
