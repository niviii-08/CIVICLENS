"""
Integration Tests for Phase 11 — End-to-End REST API Verification
"""
import pytest
from backend.api.app import create_app
from backend.database.session import SessionLocal
from backend.models.accountability import AccountabilityCase
from scripts.ingest_phase11_accountability_data import seed_phase11_data


@pytest.fixture(scope="module")
def client():
    """Ensure Phase 11 seed data is present in database and return Flask test client."""
    seed_phase11_data()
    app = create_app(validate_config=False)
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_api_accountability_cases(client):
    """Verify GET /api/accountability/cases endpoint."""
    res = client.get("/api/accountability/cases")
    assert res.status_code == 200
    json_data = res.get_json()
    assert json_data["status"] == "success"
    assert len(json_data["data"]) >= 2

    # Verify single case dossier
    case_id = json_data["data"][0]["case_id"]
    res_single = client.get(f"/api/accountability/cases/{case_id}")
    assert res_single.status_code == 200
    single_data = res_single.get_json()["data"]
    assert single_data["dossier_type"] == "PUBLIC_ACCOUNTABILITY_CASE_DOSSIER"
    assert "epistemic_disclaimer" in single_data


def test_api_procurement(client):
    """Verify GET /api/procurement/tenders and /works endpoints."""
    res_tenders = client.get("/api/procurement/tenders")
    assert res_tenders.status_code == 200
    tenders = res_tenders.get_json()["data"]
    assert len(tenders) >= 1

    res_works = client.get("/api/procurement/works")
    assert res_works.status_code == 200
    works = res_works.get_json()["data"]
    assert len(works) >= 1

    res_sum = client.get("/api/procurement/summary")
    assert res_sum.status_code == 200
    assert "total_tenders_tracked" in res_sum.get_json()["data"]


def test_api_cag_audit(client):
    """Verify GET /api/cag-audit/reports and /paragraphs endpoints."""
    res_reports = client.get("/api/cag-audit/reports")
    assert res_reports.status_code == 200
    reports = res_reports.get_json()["data"]
    assert len(reports) >= 1

    res_paras = client.get("/api/cag-audit/paragraphs")
    assert res_paras.status_code == 200
    paras = res_paras.get_json()["data"]
    assert len(paras) >= 1


def test_api_rti(client):
    """Verify GET /api/rti/requests endpoint."""
    res = client.get("/api/rti/requests")
    assert res.status_code == 200
    requests = res.get_json()["data"]
    assert len(requests) >= 1


def test_api_provenance_and_graph_coverage(client):
    """Verify GET /api/provenance/right-of-reply and /graph/coverage endpoints."""
    res_ror = client.get("/api/provenance/right-of-reply")
    assert res_ror.status_code == 200

    res_cov = client.get("/api/provenance/graph/coverage")
    assert res_cov.status_code == 200
    cov = res_cov.get_json()["data"]
    assert cov["total_nodes"] > 0
    assert "connectivity_coverage_pct" in cov
