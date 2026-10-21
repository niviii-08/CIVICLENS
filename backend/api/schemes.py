from collections import defaultdict
from contextlib import contextmanager
from flask import Blueprint, request
from sqlalchemy.orm import Session

from backend.database.session import get_db
from backend.models.budget import (
    HistoricalScheme,
    BudgetDepartment,
    SchemeCategory,
    SchemeSourceRelationship,
    BudgetSourceDocument,
)
from backend.api.responses import success_response, error_response
from backend.services.scheme_budget_impact_service import (
    SchemeBudgetImpactService,
    IncompatibleMetricComparisonError,
)

schemes_bp = Blueprint('schemes', __name__, url_prefix='/schemes')


@contextmanager
def _get_db_session():
    """
    Safely resolves get_db() generator or session instance and guarantees closure.
    Supports both default session generation and test-injected fixtures.
    """
    res = get_db()
    if hasattr(res, "__iter__") or hasattr(res, "__next__"):
        gen = iter(res)
        db = next(gen)
        try:
            yield db
        finally:
            try:
                next(gen)
            except StopIteration:
                pass
    else:
        db = res
        try:
            yield db
        finally:
            if hasattr(db, "close"):
                db.close()


@schemes_bp.route('/search', methods=['GET'])
def search_schemes():
    name = request.args.get('name', type=str)
    description = request.args.get('description', type=str)
    year = request.args.get('year', type=str)
    department_id = request.args.get('department_id', type=int)
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)

    if page < 1:
        return error_response("Page must be >= 1", status_code=400)
    if limit < 1 or limit > 100:
        return error_response("Limit must be between 1 and 100", status_code=400)

    try:
        with _get_db_session() as db:
            query = db.query(HistoricalScheme)

            if name:
                query = query.filter(HistoricalScheme.scheme_name.ilike(f"%{name}%"))
            if description:
                query = query.filter(HistoricalScheme.description.ilike(f"%{description}%"))
            if year:
                if len(year) != 7 or "-" not in year:
                    return error_response("Invalid year format. Expected YYYY-YY.", status_code=400)
                query = query.filter(HistoricalScheme.financial_year == year)
            if department_id:
                query = query.filter(HistoricalScheme.department_id == department_id)
            if category_id:
                query = query.filter(HistoricalScheme.category_id == category_id)

            total_count = query.count()
            schemes = query.offset((page - 1) * limit).limit(limit).all()

            data = []
            for s in schemes:
                data.append({
                    "id": s.id,
                    "scheme_name": s.scheme_name,
                    "financial_year": s.financial_year,
                    "department_id": s.department_id,
                    "category_id": s.category_id,
                    "description": s.description,
                    "objectives": s.objectives,
                    "target_beneficiaries": s.target_beneficiaries,
                    "is_uncertain_match": bool(s.is_uncertain_match),
                    "match_confidence": s.match_confidence
                })

            return success_response({
                "items": data,
                "page": page,
                "limit": limit,
                "total": total_count
            })
    except Exception as e:
        return error_response(f"Database error: {str(e)}", status_code=500)


@schemes_bp.route('/<int:scheme_id>', methods=['GET'])
def get_scheme(scheme_id: int):
    with _get_db_session() as db:
        scheme = db.query(HistoricalScheme).filter(HistoricalScheme.id == scheme_id).first()
        if not scheme:
            return error_response("Scheme not found", status_code=404)

        return success_response({
            "id": scheme.id,
            "scheme_name": scheme.scheme_name,
            "financial_year": scheme.financial_year,
            "department_id": scheme.department_id,
            "category_id": scheme.category_id,
            "description": scheme.description,
            "objectives": scheme.objectives,
            "target_beneficiaries": scheme.target_beneficiaries,
            "is_uncertain_match": bool(scheme.is_uncertain_match)
        })


@schemes_bp.route('/<scheme_id>/impact-analysis', methods=['GET'])
def get_scheme_impact_analysis(scheme_id: str):
    """
    Phase 13.3 Scheme and Budget Impact Analysis Endpoint.
    Returns multi-year financial inputs (BE, RE, AE), verified beneficiaries,
    reported outputs, measured outcomes, and epistemic guardrails.
    """
    with _get_db_session() as db:
        try:
            service = SchemeBudgetImpactService(db)
            result = service.analyze_scheme_impact(scheme_id)
            return success_response(result)
        except ValueError as ve:
            return error_response(str(ve), status_code=404)
        except Exception as e:
            return error_response(f"Failed to analyze scheme impact: {str(e)}", status_code=500)


@schemes_bp.route('/<int:scheme_id>/history', methods=['GET'])
def get_scheme_history(scheme_id: int):
    with _get_db_session() as db:
        scheme = db.query(HistoricalScheme).filter(HistoricalScheme.id == scheme_id).first()
        if not scheme:
            return error_response("Scheme not found", status_code=404)

        if not scheme.budget_scheme_id:
            history = [scheme]
        else:
            history = (
                db.query(HistoricalScheme)
                .filter(HistoricalScheme.budget_scheme_id == scheme.budget_scheme_id)
                .order_by(HistoricalScheme.financial_year.desc())
                .all()
            )

        data = [{
            "id": h.id,
            "financial_year": h.financial_year,
            "scheme_name": h.scheme_name,
            "description": h.description,
            "objectives": h.objectives,
            "is_uncertain_match": bool(h.is_uncertain_match)
        } for h in history]

        return success_response(data)


@schemes_bp.route('/<int:scheme_id>/sources', methods=['GET'])
def get_scheme_sources(scheme_id: int):
    with _get_db_session() as db:
        scheme = db.query(HistoricalScheme).filter(HistoricalScheme.id == scheme_id).first()
        if not scheme:
            return error_response("Scheme not found", status_code=404)

        # Bulk join relationships and source documents in a single SQL query
        rel_docs = (
            db.query(SchemeSourceRelationship, BudgetSourceDocument)
            .outerjoin(BudgetSourceDocument, SchemeSourceRelationship.source_document_id == BudgetSourceDocument.id)
            .filter(SchemeSourceRelationship.historical_scheme_id == scheme_id)
            .all()
        )

        data = []
        for rel, doc in rel_docs:
            data.append({
                "relationship_id": rel.id,
                "source_document_id": rel.source_document_id,
                "document_title": doc.title if doc else None,
                "manifest_dataset_id": doc.manifest_dataset_id if doc else None,
                "source_page_number": rel.source_page_number,
                "extracted_text_snippet": rel.extracted_text[:200] if rel.extracted_text else None
            })

        return success_response(data)


@schemes_bp.route('/categories', methods=['GET'])
def get_scheme_categories():
    with _get_db_session() as db:
        categories = db.query(SchemeCategory).all()
        data = [{"id": c.id, "name": c.name, "description": c.description} for c in categories]
        return success_response(data)


@schemes_bp.route('/<int:scheme_id>/similar', methods=['GET'])
def get_similar_schemes(scheme_id: int):
    top_k = request.args.get('top_k', 5, type=int)
    threshold = request.args.get('threshold', 0.3, type=float)
    page = request.args.get('page', 1, type=int)
    department_id = request.args.get('department_id', type=int)
    year = request.args.get('year', type=str)
    category_id = request.args.get('category_id', type=int)

    if page < 1:
        return error_response("Page must be >= 1", status_code=400)
    if top_k < 1 or top_k > 100:
        return error_response("top_k must be between 1 and 100", status_code=400)

    try:
        with _get_db_session() as db:
            from backend.nlp.similarity import SemanticSchemeSearcher
            searcher = SemanticSchemeSearcher(db)
            results = searcher.search_by_scheme_id(
                scheme_id, top_k=top_k, threshold=threshold, page=page,
                department_id=department_id, year=year, category_id=category_id
            )
            return success_response(results)
    except ValueError as ve:
        return error_response(str(ve), status_code=404)
    except Exception as e:
        return error_response(f"Similarity search failed: {str(e)}", status_code=500)


@schemes_bp.route('/semantic_search', methods=['GET'])
def semantic_text_search():
    query = request.args.get('query', type=str)
    if not query:
        return error_response("Query parameter is required.", status_code=400)

    top_k = request.args.get('top_k', 5, type=int)
    threshold = request.args.get('threshold', 0.3, type=float)
    page = request.args.get('page', 1, type=int)
    department_id = request.args.get('department_id', type=int)
    year = request.args.get('year', type=str)
    category_id = request.args.get('category_id', type=int)

    if page < 1:
        return error_response("Page must be >= 1", status_code=400)
    if top_k < 1 or top_k > 100:
        return error_response("top_k must be between 1 and 100", status_code=400)

    try:
        with _get_db_session() as db:
            from backend.nlp.similarity import SemanticSchemeSearcher
            searcher = SemanticSchemeSearcher(db)
            results = searcher.search_by_text(
                query, top_k=top_k, threshold=threshold, page=page,
                department_id=department_id, year=year, category_id=category_id
            )
            return success_response(results)
    except Exception as e:
        return error_response(f"Semantic search failed: {str(e)}", status_code=500)


@schemes_bp.route('/compare-impact', methods=['GET'])
def compare_schemes_impact_endpoint():
    ids_param = request.args.get('ids')
    fy = request.args.get('financial_year') or request.args.get('fy')
    if not ids_param:
        return error_response("Query parameter 'ids' is required (comma-separated).", status_code=400)

    ids = [i.strip() for i in ids_param.split(',') if i.strip()]
    if len(ids) < 2:
        return error_response("At least two scheme IDs or codes are required for comparison.", status_code=400)

    with _get_db_session() as db:
        try:
            service = SchemeBudgetImpactService(db)
            result = service.compare_schemes_impact(ids, financial_year=fy)
            return success_response(result)
        except IncompatibleMetricComparisonError as ie:
            return error_response(str(ie), status_code=400)
        except Exception as e:
            return error_response(f"Impact comparison failed: {str(e)}", status_code=500)


@schemes_bp.route('/compare', methods=['GET'])
def compare_schemes():
    ids_param = request.args.get('ids')
    if not ids_param:
        return error_response("Query parameter 'ids' is required (comma-separated).", status_code=400)

    # Support mode=impact delegate
    mode = request.args.get('mode') or request.args.get('type')
    if mode == 'impact':
        return compare_schemes_impact_endpoint()

    try:
        scheme_ids = [int(i.strip()) for i in ids_param.split(',') if i.strip().isdigit()]
    except ValueError:
        return error_response("Invalid IDs format.", status_code=400)

    if len(scheme_ids) < 2:
        return error_response("At least two scheme IDs are required for comparison.", status_code=400)

    try:
        with _get_db_session() as db:
            schemes = db.query(HistoricalScheme).filter(HistoricalScheme.id.in_(scheme_ids)).all()
            if not schemes:
                return error_response("No schemes found for provided IDs.", status_code=404)

            from backend.nlp.similarity import cosine_similarity

            # Bulk load all source documents for all schemes in one joined query (eliminates N+1)
            rel_docs = (
                db.query(SchemeSourceRelationship, BudgetSourceDocument)
                .outerjoin(BudgetSourceDocument, SchemeSourceRelationship.source_document_id == BudgetSourceDocument.id)
                .filter(SchemeSourceRelationship.historical_scheme_id.in_(scheme_ids))
                .all()
            )
            sources_by_scheme = defaultdict(list)
            for rel, doc in rel_docs:
                if doc:
                    sources_by_scheme[rel.historical_scheme_id].append({
                        "title": doc.title,
                        "page": rel.source_page_number
                    })

            results = []
            for s in schemes:
                dept_name = s.department.name if s.department else "Unknown"
                sources = sources_by_scheme.get(s.id, [])
                vec = s.embedding.get("vector") if (s.embedding and isinstance(s.embedding, dict)) else []

                results.append({
                    "id": s.id,
                    "scheme_name": s.scheme_name,
                    "financial_year": s.financial_year,
                    "department": dept_name,
                    "description": s.description,
                    "objectives": s.objectives,
                    "target_beneficiaries": s.target_beneficiaries,
                    "sources": sources,
                    "vector": vec
                })

            similarity_matrix = {}
            for i, s1 in enumerate(results):
                similarity_matrix[s1["id"]] = {}
                for j, s2 in enumerate(results):
                    if i == j:
                        similarity_matrix[s1["id"]][s2["id"]] = 1.0
                    else:
                        if s1["vector"] and s2["vector"]:
                            score = cosine_similarity(s1["vector"], s2["vector"])
                            similarity_matrix[s1["id"]][s2["id"]] = round(score, 4)
                        else:
                            similarity_matrix[s1["id"]][s2["id"]] = 0.0

            for r in results:
                del r["vector"]

            return success_response({
                "schemes": results,
                "similarity_matrix": similarity_matrix
            })
    except Exception as e:
        return error_response(f"Comparison failed: {str(e)}", status_code=500)


@schemes_bp.route('/themes', methods=['GET'])
def analyze_scheme_themes():
    n_clusters = request.args.get('n_clusters', 5, type=int)
    department_id = request.args.get('department_id', type=int)

    if n_clusters < 2 or n_clusters > 20:
        return error_response("n_clusters must be between 2 and 20", status_code=400)

    try:
        with _get_db_session() as db:
            from backend.ml.theme_analysis import ThemeAnalyzer
            analyzer = ThemeAnalyzer(db)
            results = analyzer.analyze_themes(n_clusters=n_clusters, department_id=department_id)
            return success_response(results)
    except ValueError as ve:
        return error_response(str(ve), status_code=400)
    except Exception as e:
        return error_response(f"Theme analysis failed: {str(e)}", status_code=500)
