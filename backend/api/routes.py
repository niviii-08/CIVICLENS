from flask import Blueprint
from backend.api.responses import error_response, success_response
from backend.api.budget import budget_bp
from backend.api.ml import ml_bp
from backend.api.schemes import schemes_bp
from backend.api.promises import promises_bp
from backend.api.news import news_bp
from backend.api.funding import funding_bp
from backend.api.representatives import representatives_bp
from backend.api.claims import claims_bp
from backend.api.civic import civic_bp
from backend.api.entities import entities_bp
from backend.api.graph import graph_bp
from backend.api.policy_evaluation import policy_evaluation_bp
from backend.api.search import search_bp
from backend.api.evidence import evidence_bp
from backend.api.integration import integration_bp
from backend.api.timelines import timelines_bp
from backend.api.local_insights import local_insights_bp
from backend.api.reports import reports_bp
from backend.api.tracking import tracking_bp
from backend.api.freshness import freshness_bp

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/health', methods=['GET'])
@api_bp.route('/health/live', methods=['GET'])
def api_health_live():
    return success_response(data={"status": "healthy", "check": "liveness"}, message="Application is running")

@api_bp.route('/health/ready', methods=['GET'])
def api_health_ready():
    from backend.database.session import SessionLocal
    from sqlalchemy import text
    import logging
    logger = logging.getLogger("civiclens.api")
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return success_response(data={"status": "ready", "database": "connected"}, message="Service is ready to handle traffic")
    except Exception as e:
        logger.error(f"API readiness check failed: {e}", exc_info=True)
        return error_response(message="Service unavailable: database connection check failed", status_code=503)
    finally:
        db.close()

def not_implemented():
    return error_response(message="Module not implemented yet.", status_code=501)

api_bp.register_blueprint(budget_bp)
api_bp.register_blueprint(ml_bp)
api_bp.register_blueprint(schemes_bp)
api_bp.register_blueprint(promises_bp)
api_bp.register_blueprint(news_bp)
api_bp.register_blueprint(funding_bp)
api_bp.register_blueprint(representatives_bp)
api_bp.register_blueprint(claims_bp)
api_bp.register_blueprint(civic_bp)
api_bp.register_blueprint(entities_bp)
api_bp.register_blueprint(graph_bp)
api_bp.register_blueprint(policy_evaluation_bp)
api_bp.register_blueprint(search_bp)
api_bp.register_blueprint(evidence_bp, url_prefix='/evidence')
api_bp.register_blueprint(integration_bp)
api_bp.register_blueprint(timelines_bp)
api_bp.register_blueprint(local_insights_bp)
api_bp.register_blueprint(reports_bp)
api_bp.register_blueprint(tracking_bp)
api_bp.register_blueprint(freshness_bp)

namespaces = []

for ns in namespaces:
    ns_bp = Blueprint(ns, __name__, url_prefix=f'/{ns}')

    @ns_bp.route('/', defaults={'path': ''}, methods=['GET', 'POST', 'PUT', 'DELETE'])
    @ns_bp.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
    def handle_unimplemented(path):
        return not_implemented()

    api_bp.register_blueprint(ns_bp)
