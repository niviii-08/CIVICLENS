"""
Unit tests for CIVICLENS TN — Verified Civic Reference Data Ingestion.

Validates:
1. Administrative geography hierarchy (State -> 38 Districts -> 21 Corporations -> 15 GCC Zones).
2. Strict separation of geography types (Parliamentary vs Assembly vs Revenue Districts vs ULBs).
3. Exact constituency counts (39 PCs + 234 ACs = 273 total constituencies).
4. Preservation of historical officeholder terms, vote counts, and win margins (2016 vs 2021).
5. Explicit review flagging for boundary reassignments and reorganizations.
6. Referential integrity and absence of orphaned records.
7. Disambiguation and alias resolution across representative identifiers.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.database.base_class import Base
from backend.models.representative import (
    Representative,
    Constituency,
    Election,
    RepresentativeTerm,
    ConstituencyBoundaryHistory,
    ConstituencyGeographicMapping,
    RepresentativeType,
    ConstituencyType,
    ElectionType
)
from backend.models.civic_issue import (
    AdministrativeArea,
    AdministrativeLevel
)
from backend.models.news import PoliticalParty
from backend.ingestion.civic_reference_ingestor import CivicReferenceIngestor
from backend.services.representative_registry import RepresentativeRegistryService


@pytest.fixture(scope="module")
def memory_db():
    """Provides an isolated in-memory SQLite database session with full reference data."""
    test_engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=test_engine)
    TestSession = sessionmaker(bind=test_engine)
    session = TestSession()

    ingestor = CivicReferenceIngestor(db=session)
    ingestor.ingest_all()

    yield session
    session.close()


def test_1_administrative_geography_hierarchy(memory_db: Session):
    """Verifies State -> District -> Corporation -> Ward hierarchy and LGD codes."""
    # State
    state = memory_db.query(AdministrativeArea).filter(AdministrativeArea.area_code == "ADM-TN-STATE").first()
    assert state is not None
    assert state.name_en == "Tamil Nadu"
    assert state.name_ta == "தமிழ்நாடு"
    assert state.administrative_level == AdministrativeLevel.STATE
    assert state.lgd_code == "33"
    assert state.parent_id is None

    # 38 Revenue Districts
    districts = memory_db.query(AdministrativeArea).filter(
        AdministrativeArea.administrative_level == AdministrativeLevel.DISTRICT
    ).all()
    assert len(districts) == 38
    for dist in districts:
        assert dist.parent_id == state.id
        assert dist.lgd_code is not None and len(dist.lgd_code) > 0
        assert dist.name_en is not None
        assert dist.name_ta is not None

    # Specific District Checks
    chennai = next(d for d in districts if d.area_code == "ADM-TN-DIST-003-CHENNAI")
    assert chennai.name_en == "Chennai"
    assert chennai.lgd_code == "577"

    coimbatore = next(d for d in districts if d.area_code == "ADM-TN-DIST-004-COIMBATORE")
    assert coimbatore.name_en == "Coimbatore"
    assert coimbatore.lgd_code == "578"

    # 21 Municipal Corporations
    corps = memory_db.query(AdministrativeArea).filter(
        AdministrativeArea.administrative_level == AdministrativeLevel.MUNICIPAL_CORPORATION
    ).all()
    assert len(corps) == 21
    gcc = next(c for c in corps if c.area_code == "ADM-TN-CORP-CHENNAI")
    assert gcc.parent_id == chennai.id
    assert gcc.lgd_code == "251663"

    # 15 GCC Zones
    zones = memory_db.query(AdministrativeArea).filter(
        AdministrativeArea.administrative_level == AdministrativeLevel.WARD
    ).all()
    assert len(zones) == 15
    for z in zones:
        assert z.parent_id == gcc.id


def test_2_strict_constituency_type_separation(memory_db: Session):
    """Verifies strict separation between 39 Parliamentary and 234 Assembly constituencies."""
    pcs = memory_db.query(Constituency).filter(Constituency.constituency_type == ConstituencyType.PARLIAMENTARY).all()
    assert len(pcs) == 39

    acs = memory_db.query(Constituency).filter(Constituency.constituency_type == ConstituencyType.ASSEMBLY).all()
    assert len(acs) == 234

    # Total constituencies must be exactly 273
    total = memory_db.query(Constituency).count()
    assert total == 273

    # Check reservation breakdown for Assembly: 188 Gen, 44 SC, 2 ST
    sc_acs = [a for a in acs if a.reservation_status == "SC"]
    st_acs = [a for a in acs if a.reservation_status == "ST"]
    gen_acs = [a for a in acs if a.reservation_status == "GENERAL"]

    assert len(sc_acs) == 44
    assert len(st_acs) == 2  # Yercaud (AC-083) and Senthamangalam (AC-093)
    assert len(gen_acs) == 188
    assert len(sc_acs) + len(st_acs) + len(gen_acs) == 234


def test_3_historical_officeholder_and_term_preservation(memory_db: Session):
    """Verifies historical vs active officeholder terms, vote counts, and margins."""
    stalin = memory_db.query(Representative).filter(Representative.representative_id == "REP-MLA-013").first()
    assert stalin is not None
    assert stalin.official_name == "M. K. Stalin"
    assert "REP-TN-011" in stalin.aliases

    terms = memory_db.query(RepresentativeTerm).filter(
        RepresentativeTerm.representative_id == "REP-MLA-013"
    ).order_by(RepresentativeTerm.term_start).all()
    assert len(terms) == 2

    # 15th Assembly (2016-2021) - Historical Term
    t15 = terms[0]
    assert t15.election_id == "TNLA-2016"
    assert t15.is_active_term is False
    assert t15.term_end == "2021-05-03"
    assert t15.votes_polled == 91303
    assert t15.win_margin_votes == 2981
    assert t15.party_id == "PARTY-DMK"

    # 16th Assembly (2021-Present) - Active Term
    t16 = terms[1]
    assert t16.election_id == "TNLA-2021"
    assert t16.is_active_term is True
    assert t16.term_end is None
    assert t16.votes_polled == 105522
    assert t16.win_margin_votes == 70384
    assert t16.party_id == "PARTY-DMK"

    # EPS (Edappadi)
    eps = memory_db.query(Representative).filter(Representative.representative_id == "REP-MLA-086").first()
    assert eps is not None
    assert "REP-TN-016" in eps.aliases
    eps_terms = memory_db.query(RepresentativeTerm).filter(
        RepresentativeTerm.representative_id == "REP-MLA-086"
    ).all()
    assert len(eps_terms) == 2
    active_eps = next(t for t in eps_terms if t.is_active_term)
    assert active_eps.votes_polled == 163823
    assert active_eps.win_margin_votes == 93802
    assert active_eps.party_id == "PARTY-AIADMK"


def test_4_boundary_reorganization_and_flagged_reviews(memory_db: Session):
    """Verifies that boundary reorganizations are recorded and flagged for review."""
    history = memory_db.query(ConstituencyBoundaryHistory).all()
    assert len(history) >= 8

    tambaram_hist = next(h for h in history if h.constituency_id == "AC-031")
    assert "FLAGGED_FOR_REVIEW" in tambaram_hist.change_summary
    assert "Chengalpattu" in tambaram_hist.change_summary
    assert "Kancheepuram" in tambaram_hist.change_summary

    arakkonam_hist = next(h for h in history if h.constituency_id == "AC-038")
    assert "FLAGGED_FOR_REVIEW" in arakkonam_hist.change_summary
    assert "Ranipet" in arakkonam_hist.change_summary


def test_5_constituency_geographic_mappings(memory_db: Session):
    """Verifies all 234 ACs have geographic mappings to standard revenue districts."""
    mappings = memory_db.query(ConstituencyGeographicMapping).all()
    assert len(mappings) == 234

    kolathur_map = next(m for m in mappings if m.constituency_id == "AC-013")
    assert kolathur_map.district_name == "Chennai"
    assert kolathur_map.delimitation_year == 2008


def test_6_referential_integrity_validation(memory_db: Session):
    """Runs the built-in integrity validator to ensure zero orphan keys or broken links."""
    ingestor = CivicReferenceIngestor(db=memory_db)
    validation = ingestor.validate_integrity()

    assert validation["is_valid"] is True
    assert len(validation["errors"]) == 0
    assert validation["counts"]["assembly_constituencies"] == 234
    assert validation["counts"]["parliamentary_constituencies"] == 39
    assert validation["counts"]["districts"] == 38
    assert validation["counts"]["corporations"] == 21
    assert validation["counts"]["total_elections"] == 4
    assert validation["counts"]["total_terms"] >= 14


def test_7_representative_disambiguation_with_registry_service(memory_db: Session):
    """Verifies RepresentativeRegistryService resolves representatives by name, alias, and context."""
    service = RepresentativeRegistryService(db=memory_db)

    # Resolution by exact name with constituency context
    rep = service.resolve_representative(
        query_name="M. K. Stalin",
        constituency_id="AC-013"
    )
    assert rep.representative_id == "REP-MLA-013"

    # Resolution by Tamil alias
    rep_ta = service.resolve_representative(
        query_name="மு.க. ஸ்டாலின்",
        constituency_id="AC-013"
    )
    assert rep_ta.representative_id == "REP-MLA-013"

    # Resolution of EPS
    rep_eps = service.resolve_representative(
        query_name="Edappadi K. Palaniswami",
        constituency_id="AC-086"
    )
    assert rep_eps.representative_id == "REP-MLA-086"
