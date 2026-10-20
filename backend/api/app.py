import os
from flask import Flask
from flask_cors import CORS
from sqlalchemy import text
from backend.core.config import config
from backend.database.session import SessionLocal
from backend.api.routes import api_bp
from backend.api.errors import error_bp
from backend.api.responses import success_response, error_response

def create_app(validate_config: bool = True):
    """Application factory for configuring and starting the Flask backend."""
    if validate_config:
        config.validate()

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

    @app.after_request
    def set_security_headers(response):
        """Inject OWASP defensive HTTP security headers into all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        if not config.DEBUG:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    @app.route('/health', methods=['GET'])
    def health_check():
        """General application health check."""
        return success_response(data={"status": "healthy"}, message="Application is running")

    @app.route('/health/db', methods=['GET'])
    def db_health_check():
        """Checks if the database is reachable."""
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
            return success_response(data={"db_status": "connected"}, message="Database is reachable")
        except Exception as e:
            error_details = str(e) if config.DEBUG else "Database service unavailable."
            return error_response(message="Database connection failed", error_details=error_details, status_code=503)
        finally:
            db.close()

    @app.route('/version', methods=['GET'])
    def get_version():
        return success_response(data={"version": "0.1.0"}, message="Version retrieved")

    @app.route('/launch', methods=['GET'])
    @app.route('/', methods=['GET'])
    def serve_launch():
        from flask import send_file
        import os
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        index_path = os.path.join(root_dir, 'index.html')
        if os.path.exists(index_path):
            return send_file(index_path)
        return success_response(data={"status": "healthy"}, message="CivicLens API Running")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.DEBUG)
