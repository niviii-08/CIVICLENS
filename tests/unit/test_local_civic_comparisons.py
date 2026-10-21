"""
CIVICLENS TN — Unit Tests for District & Constituency Civic Insights
Phase 13.6: Geographic Identifiers, Cross-Jurisdiction Comparisons, and Epistemic Guardrails.

Verifies:
1. Supported geographic directories lookup (Districts, Constituencies, Wards).
2. Metric catalog validation with units, reporting periods, and calculation formulas.
3. Geographic profile retrieval and bifurcation context.
4. Comparable cohort evaluations (Constituencies on literacy, Districts on SLA compliance).
5. Incompatible geographic level rejection.
6. Unsupported metric for geographic tier rejection.
7. Strict prohibition of arbitrary composite scores.
8. Single-metric defensible ranking with formula and limitations disclosure.
9. Strict non-conflation of zero (0.0) vs unavailable (None) records.
10. Contextual demographic divergence warning (urban vs rural skew).
11. Population scale divergence warning.
12. REST API endpoints (GET /geographies, /metrics, /profile, POST /compare, GET /compare).
"""

import pytest
from backend.services.local_civic_comparison_service import (
    LocalCivicComparisonService,
    LocalInsightError,
    IncompatibleUnitError,
    IncompatiblePeriodError,
    IncompatibleGeographicLevelError,
    ArbitraryScoringProhibitedError,
    EntityNotFoundError,
    SUPPORTED_METRICS,
)
from backend.api.app import create_app


@pytest.fixture
def service():
    return LocalCivicComparisonService()


@pytest.fixture
def test_client():
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# =====================================================================
# Service Layer Directory & Profile Tests
# =====================================================================

def test_get_supported_geographies(service):
    """Verify retrieval of verified districts, constituencies, and municipal wards."""
    geos = service.get_supported_geographies()

    assert "districts" in geos
    assert "constituencies" in geos
    assert "wards" in geos

    # Check key canonical districts exist
    district_codes = [d["district_code"] for d in geos["districts"]]
    assert "ADM-TN-DIST-003-CHENNAI" in district_codes
    assert "ADM-TN-DIST-004-COIMBATORE" in district_codes
    assert "ADM-TN-DIST-013-MADURAI" in district_codes
    assert "ADM-TN-DIST-022-SALEM" in district_codes
    assert "ADM-TN-DIST-002-CHENGALPATTU" in district_codes

    # Check key canonical constituencies exist
    constituency_ids = [c["constituency_id"] for c in geos["constituencies"]]
    assert "AC-011" in constituency_ids
    assert "AC-012" in constituency_ids
    assert "AC-013" in constituency_ids
    assert "AC-115" in constituency_ids
    assert "PC-001" in constituency_ids

    # Check level filter works
    only_districts = service.get_supported_geographies(level="DISTRICT")
    assert len(only_districts["districts"]) > 0
    assert len(only_districts["constituencies"]) == 0


def test_get_supported_metrics_catalog(service):
    """Verify supported metrics expose units, formulas, sources, and limitations."""
    metrics = service.get_supported_metrics()
    assert len(metrics) >= 8

    metric_ids = [m["metric_id"] for m in metrics]
    assert "literacy_rate_pct" in metric_ids
    assert "urban_pct" in metric_ids
    assert "mplads_utilization_pct" in metric_ids
    assert "sla_compliance_rate_pct" in metric_ids
    assert "emergency_trauma_mortality_pct" in metric_ids

    # Each metric must have non-empty unit, calculation formula, and limitations
    for m in metrics:
        assert "unit" in m and len(m["unit"]) > 0
        assert "calculation_formula" in m and len(m["calculation_formula"]) > 0
        assert "primary_source" in m and len(m["primary_source"]) > 0
        assert "limitations" in m and len(m["limitations"]) > 0

    # Test filtering by level
    constituency_metrics = service.get_supported_metrics(level="CONSTITUENCY")
    for cm in constituency_metrics:
        assert "CONSTITUENCY" in cm["supported_levels"]


def test_get_geographic_profile(service):
    """Verify geographic profile retrieval for district, constituency, and ward."""
    # 1. District
    d_prof = service.get_geographic_profile("district", "ADM-TN-DIST-003-CHENNAI")
    assert d_prof["entity_type"] == "DISTRICT"
    assert d_prof["name_en"] == "Chennai"
    assert d_prof["lgd_code"] == "603"
    assert "2011" in d_prof["available_periods"]
    assert "2023-2024" in d_prof["available_periods"]

    # 2. Bifurcated District has boundary history
    c_prof = service.get_geographic_profile("district", "ADM-TN-DIST-002-CHENGALPATTU")
    assert "bifurcation_history" in c_prof
    assert "Kancheepuram" in c_prof["bifurcation_history"]

    # 3. Constituency
    ac_prof = service.get_geographic_profile("constituency", "AC-013")
    assert ac_prof["entity_type"] == "CONSTITUENCY"
    assert ac_prof["name"] == "Kolathur"
    assert ac_prof["district"] == "Chennai"
    assert ac_prof["delimitation_year"] == 2008

    # 4. Unknown entity raises EntityNotFoundError
    with pytest.raises(EntityNotFoundError):
        service.get_geographic_profile("constituency", "AC-NONEXISTENT-999")


# =====================================================================
# Comparative Analysis & Epistemic Guardrail Tests
# =====================================================================

def test_compare_constituencies_success(service):
    """Verify valid comparison across 4 assembly constituencies on literacy_rate_pct."""
    result = service.compare_entities(
        entity_type="CONSTITUENCY",
        entity_ids=["AC-011", "AC-012", "AC-013", "AC-115"],
        metric_id="literacy_rate_pct",
        reporting_period="2011",
    )

    assert result["geographic_level"] == "CONSTITUENCY"
    assert result["metric_id"] == "literacy_rate_pct"
    assert result["unit"] == "PERCENT"
    assert result["reporting_period"] == "2011"
    assert result["entities_compared_count"] == 4
    assert result["available_records_count"] == 4
    assert result["unavailable_records_count"] == 0

    # Check rows
    for r in result["comparisons"]:
        assert r["value"] is not None
        assert r["unit"] == "PERCENT"
        assert r["is_zero"] is False
        assert r["is_unavailable"] is False
        assert len(r["source_citations"]) > 0


def test_compare_districts_sla_compliance(service):
    """Verify valid comparison across districts on municipal SLA delivery."""
    result = service.compare_entities(
        entity_type="DISTRICT",
        entity_ids=["ADM-TN-DIST-003-CHENNAI", "ADM-TN-DIST-004-COIMBATORE", "ADM-TN-DIST-013-MADURAI"],
        metric_id="sla_compliance_rate_pct",
        reporting_period="2023-2024",
    )

    assert result["geographic_level"] == "DISTRICT"
    assert result["entities_compared_count"] == 3
    assert result["unit"] == "PERCENT"


def test_incompatible_geographic_levels_rejected(service):
    """Verify that comparing across unsupported tiers raises IncompatibleGeographicLevelError."""
    with pytest.raises(IncompatibleGeographicLevelError):
        service.compare_entities(
            entity_type="COUNTRY",
            entity_ids=["IND", "USA"],
            metric_id="literacy_rate_pct",
        )


def test_metric_unsupported_at_geographic_level(service):
    """Verify error when applying constituency-specific metric at district level."""
    with pytest.raises(IncompatibleGeographicLevelError):
        service.compare_entities(
            entity_type="DISTRICT",
            entity_ids=["ADM-TN-DIST-003-CHENNAI", "ADM-TN-DIST-004-COIMBATORE"],
            metric_id="mplads_utilization_pct",  # Supported only for CONSTITUENCY
        )


def test_arbitrary_composite_scoring_prohibited(service):
    """Verify strict prohibition of arbitrary composite scores (e.g. 'civic_score')."""
    with pytest.raises(ArbitraryScoringProhibitedError):
        service.compare_entities(
            entity_type="CONSTITUENCY",
            entity_ids=["AC-011", "AC-013"],
            metric_id="literacy_rate_pct",
            rank_by="composite_civic_governance_score",  # Prohibited arbitrary ranking
        )


def test_defensible_single_metric_ranking(service):
    """Verify single-metric sorting with formula and limitation transparency."""
    result = service.compare_entities(
        entity_type="CONSTITUENCY",
        entity_ids=["AC-011", "AC-012", "AC-013", "AC-085", "AC-115"],
        metric_id="literacy_rate_pct",
        reporting_period="2011",
        rank_by="literacy_rate_pct",
    )

    assert result["ranking"] is not None
    assert result["ranking"]["ranked_by_metric"] == "literacy_rate_pct"
    assert result["ranking"]["ranking_direction"] == "DESCENDING"
    assert "calculation_formula" in result["ranking"]
    assert "limitations" in result["ranking"]
    assert "RANKING LIMITATION NOTICE" in result["ranking"]["disclaimer"]

    # Verify descending monotonicity
    values = [r["value"] for r in result["comparisons"]]
    assert values == sorted(values, reverse=True)

    # Check relative ranks
    assert result["comparisons"][0]["relative_rank"] == 1
    assert result["comparisons"][-1]["relative_rank"] == 5


def test_zero_vs_unavailable_distinction(service):
    """Verify unavailable records remain value=None with is_unavailable=True, never 0.0."""
    # Compare with a metric not recorded for wards (e.g. literacy_rate_pct is only at district/constituency)
    # Or query a period where data is absent
    result = service.compare_entities(
        entity_type="CONSTITUENCY",
        entity_ids=["AC-011", "AC-013"],
        metric_id="mplads_utilization_pct",
        reporting_period="2011",  # MPLADS not recorded in 2011 census period
    )

    assert result["unavailable_records_count"] == 2
    for r in result["comparisons"]:
        assert r["value"] is None
        assert r["is_unavailable"] is True
        assert r["is_zero"] is False
        assert r["availability_status"] == "OUTSIDE_AUDIT_SCOPE"
        assert r["data_quality_status"] == "UNAVAILABLE"


def test_demographic_divergence_warning(service):
    """Verify warning generated when comparing 100% urban Kolathur with 42.1% urban Edappadi."""
    result = service.compare_entities(
        entity_type="CONSTITUENCY",
        entity_ids=["AC-013", "AC-115"],
        metric_id="literacy_rate_pct",
        reporting_period="2011",
    )

    warnings = result["warnings"]
    assert any("DEMOGRAPHIC COMPARABILITY WARNING" in w for w in warnings)
    assert any("urban share ranges" in w for w in warnings)


def test_boundary_bifurcation_warning(service):
    """Verify district reorganization warning when Chengalpattu is compared."""
    result = service.compare_entities(
        entity_type="DISTRICT",
        entity_ids=["ADM-TN-DIST-003-CHENNAI", "ADM-TN-DIST-002-CHENGALPATTU"],
        metric_id="sla_compliance_rate_pct",
        reporting_period="2023-2024",
    )

    warnings = result["warnings"]
    assert any("Geographic boundary note for Chengalpattu" in w for w in warnings)
    assert any("Kancheepuram" in w for w in warnings)


# =====================================================================
# REST API Endpoints Tests
# =====================================================================

def test_api_list_geographies(test_client):
    """Verify GET /api/local-insights/geographies returns structured directory."""
    resp = test_client.get("/api/local-insights/geographies")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    assert "districts" in data["data"]
    assert "constituencies" in data["data"]
    assert len(data["data"]["districts"]) >= 5


def test_api_list_metrics(test_client):
    """Verify GET /api/local-insights/metrics returns verified metric catalog."""
    resp = test_client.get("/api/local-insights/metrics")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    assert "metrics" in data["data"]
    assert data["data"]["total_supported_metrics"] >= 8


def test_api_get_profile_success(test_client):
    """Verify GET /api/local-insights/profile/constituency/AC-013 returns profile."""
    resp = test_client.get("/api/local-insights/profile/constituency/AC-013")
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    payload = data["data"]
    assert payload["name"] == "Kolathur"
    assert payload["district"] == "Chennai"


def test_api_get_profile_not_found(test_client):
    """Verify unknown entity returns 404 with structured error."""
    resp = test_client.get("/api/local-insights/profile/constituency/UNKNOWN-999")
    assert resp.status_code == 404

    data = resp.get_json()
    assert data["status"] == "error"
    assert "not found" in data["message"]


def test_api_post_compare_success(test_client):
    """Verify POST /api/local-insights/compare generates valid comparison."""
    payload = {
        "entity_type": "CONSTITUENCY",
        "entity_ids": ["AC-011", "AC-012", "AC-013"],
        "metric_id": "literacy_rate_pct",
        "reporting_period": "2011",
        "rank_by": "literacy_rate_pct",
    }
    resp = test_client.post("/api/local-insights/compare", json=payload)
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    cmp_data = data["data"]
    assert cmp_data["entities_compared_count"] == 3
    assert cmp_data["ranking"] is not None


def test_api_get_compare_query_params(test_client):
    """Verify GET /api/local-insights/compare with query parameters."""
    url = "/api/local-insights/compare?entity_type=DISTRICT&entities=ADM-TN-DIST-003-CHENNAI,ADM-TN-DIST-004-COIMBATORE&metric=sla_compliance_rate_pct&period=2023-2024"
    resp = test_client.get(url)
    assert resp.status_code == 200

    data = resp.get_json()
    assert data["status"] == "success"
    assert data["data"]["entities_compared_count"] == 2


def test_api_prohibit_arbitrary_ranking(test_client):
    """Verify POST /api/local-insights/compare rejects arbitrary scores with 400."""
    payload = {
        "entity_type": "CONSTITUENCY",
        "entity_ids": ["AC-011", "AC-013"],
        "metric_id": "literacy_rate_pct",
        "rank_by": "arbitrary_composite_score",
    }
    resp = test_client.post("/api/local-insights/compare", json=payload)
    assert resp.status_code == 400

    data = resp.get_json()
    assert data["status"] == "error"
    assert "Arbitrary composite ranking" in data["message"]
