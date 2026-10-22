"""
CIVICLENS TN — Unit Tests for Source-Backed Civic Timeline Records
=================================================================
Verifies:
1. Eight standard lifecycle statuses (PROPOSED, ANNOUNCED, APPROVED, FUNDED,
   STARTED, COMPLETED, AUDITED, OUTCOME_REPORTED).
2. Six distinct date dimensions (event_date, announcement_date, publication_date,
   effective_date, reporting_period, retrieval_date).
3. Non-inference rules (announcement != completion; publication date != completion date).
4. Transparent handling of superseded records and conflicting dates.
5. Multi-source deduplication preserving citations across distinct documents.
6. Zero manufactured events (undated records strictly isolated to unanchored_milestones).
7. Citation integrity (official URL, source tier, page number, section/table reference).
8. End-to-end ingestion and schema validation via CivicTimelineIngestor.
"""

import pytest
from datetime import datetime, timezone
from backend.services.civic_timeline_service import (
    CivicTimelineService,
    EventLifecycleStatus,
    EVENT_TYPE_TO_LIFECYCLE_STATUS,
    EVENT_TYPE_PRECEDENCE,
)
from backend.ingestion.civic_timeline_ingestor import (
    CivicTimelineIngestor,
    CANONICAL_SCHEME_TIMELINES,
    run_timeline_ingestion,
)


def test_eight_lifecycle_statuses_presence():
    """Verify all 8 lifecycle statuses are present in the canonical timeline."""
    service = CivicTimelineService()
    timeline = service.get_timeline("scheme", "SCH-TN-PUDHUMAI")

    chronological = timeline["chronological_milestones"]
    statuses_present = {m["event_status"] for m in chronological}

    expected_statuses = {
        EventLifecycleStatus.PROPOSED,
        EventLifecycleStatus.ANNOUNCED,
        EventLifecycleStatus.APPROVED,
        EventLifecycleStatus.FUNDED,
        EventLifecycleStatus.STARTED,
        EventLifecycleStatus.COMPLETED,
        EventLifecycleStatus.AUDITED,
        EventLifecycleStatus.OUTCOME_REPORTED,
    }

    assert expected_statuses.issubset(statuses_present), (
        f"Missing lifecycle statuses: {expected_statuses - statuses_present}"
    )


def test_six_distinct_date_dimensions():
    """Verify all 6 date dimensions are maintained and distinct across date semantics."""
    service = CivicTimelineService()
    timeline = service.get_timeline("scheme", "SCH-TN-PUDHUMAI")

    for milestone in timeline["chronological_milestones"]:
        ds = milestone["date_semantics"]
        # Required date keys
        assert "event_date" in ds
        assert "announcement_date" in ds
        assert "publication_date" in ds
        assert "effective_date" in ds
        assert "reporting_period" in ds
        assert "retrieval_date" in ds
        assert "primary_date" in ds

    # Test milestone with divergent publication vs event vs effective dates
    approved_ms = next(
        m for m in timeline["chronological_milestones"] if m["milestone_id"] == "MS-PUDHUMAI-APPROVED"
    )
    ds = approved_ms["date_semantics"]
    assert ds["event_date"] == "2022-09-05T00:00:00Z"
    assert ds["announcement_date"] == "2022-03-18T11:00:00Z"
    assert ds["effective_date"] == "2022-09-05T00:00:00Z"
    assert ds["reporting_period"] == "2022-2023"


def test_non_inference_announcement_not_completion():
    """Verify validation forbids assuming an announcement proves completion or inferring completion date."""
    ingestor = CivicTimelineIngestor()

    # Case 1: Announcement classified as COMPLETED
    invalid_announcement = {
        "milestone_id": "MS-INVALID-1",
        "title": "Unimplemented Announcement Marked Completed",
        "event_type": "PROMISE_ANNOUNCEMENT",
        "event_status": EventLifecycleStatus.COMPLETED,
        "date_semantics": {
            "primary_date": "2021-03-15",
            "event_date": "2021-03-15T00:00:00Z",
        },
    }
    val_res = ingestor.validate_milestone_dates(invalid_announcement)
    assert not val_res["is_valid"]
    assert any("cannot be classified as COMPLETED" in err for err in val_res["errors"])

    # Case 2: Completion inferred from news publication date
    inferred_completion = {
        "milestone_id": "MS-INVALID-2",
        "title": "Completion inferred from newspaper publication",
        "event_type": "ACTION_TAKEN",
        "event_status": EventLifecycleStatus.COMPLETED,
        "date_semantics": {
            "primary_date": "2023-01-01",
            "event_date": "2023-01-01T00:00:00Z",
            "inferred_completion_from_publication": True,
        },
    }
    val_res2 = ingestor.validate_milestone_dates(inferred_completion)
    assert not val_res2["is_valid"]
    assert any("Cannot infer completion date" in err for err in val_res2["errors"])

    # Case 3: Completed status without empirical date
    undated_completed = {
        "milestone_id": "MS-INVALID-3",
        "title": "Undated completion claim",
        "event_type": "ACTION_TAKEN",
        "event_status": EventLifecycleStatus.COMPLETED,
        "date_semantics": {
            "primary_date": None,
            "event_date": None,
        },
    }
    val_res3 = ingestor.validate_milestone_dates(undated_completed)
    assert not val_res3["is_valid"]
    assert any("cannot lack an empirical event_date" in err for err in val_res3["errors"])


def test_superseded_orders_transparent_handling():
    """Verify superseded government orders are recorded with is_superseded=True and superseded_by."""
    service = CivicTimelineService()
    timeline = service.get_timeline("scheme", "SCH-TN-PUDHUMAI")

    superseded_ms = next(
        (m for m in timeline["chronological_milestones"] if m["date_semantics"].get("is_superseded")),
        None,
    )

    assert superseded_ms is not None, "Timeline must retain superseded government orders transparently"
    ds = superseded_ms["date_semantics"]
    assert ds["is_superseded"] is True
    assert ds["superseded_by"] is not None
    assert "G.O. (Ms) No. 34" in ds["superseded_by"]
    assert ds["has_date_conflict"] is True
    assert ds["conflict_explanation"] is not None


def test_multi_source_deduplication_and_citation_merging():
    """Verify multi-source reports of the same event are merged with all citations retained."""
    milestones_with_duplicates = [
        {
            "milestone_id": "MS-GO-100",
            "event_type": "GOVERNMENT_ORDER",
            "date_semantics": {
                "primary_date": "2023-05-15",
                "event_date": "2023-05-15T00:00:00Z",
                "is_superseded": False,
            },
            "entity_reference": {"canonical_identifier": "SCH-TEST"},
            "source_citations": [
                {
                    "document_id": "DOC-GO-100",
                    "title": "G.O. (Ms) No. 100",
                    "source_tier": "TIER_1_STATUTORY",
                    "official_url": "https://tn.gov.in/go100.pdf",
                    "page_number": 1,
                }
            ],
        },
        {
            "milestone_id": "MS-NEWS-REPORT-100",
            "event_type": "GOVERNMENT_ORDER",
            "date_semantics": {
                "primary_date": "2023-05-15",
                "event_date": "2023-05-15T00:00:00Z",
                "has_date_conflict": True,
                "conflict_explanation": "Media noted earlier draft effective date.",
            },
            "entity_reference": {"canonical_identifier": "SCH-TEST"},
            "source_citations": [
                {
                    "document_id": "DOC-NEWS-DAILY-100",
                    "title": "Daily News Coverage on G.O. 100",
                    "source_tier": "TIER_4_SECONDARY_CIVIC",
                    "official_url": "https://newspaper.com/go100",
                    "page_number": 5,
                }
            ],
        },
    ]

    deduped = CivicTimelineService.deduplicate_milestones(milestones_with_duplicates)
    assert len(deduped) == 1, "Duplicate event across multiple sources must be collapsed into 1 milestone"

    merged = deduped[0]
    citations = merged["source_citations"]
    assert len(citations) == 2, "Merged milestone must aggregate citations from all sources"
    doc_ids = {c["document_id"] for c in citations}
    assert "DOC-GO-100" in doc_ids
    assert "DOC-NEWS-DAILY-100" in doc_ids
    assert merged["date_semantics"]["has_date_conflict"] is True
    assert "Media noted" in merged["date_semantics"]["conflict_explanation"]


def test_same_date_distinct_event_types_not_collapsed():
    """Verify distinct financial/operational event types occurring on the same date are not erroneously merged."""
    milestones = [
        {
            "milestone_id": "MS-STATUTORY-GO",
            "event_type": "STATUTORY_NOTIFICATION",
            "date_semantics": {"primary_date": "2022-09-05"},
            "entity_reference": {"canonical_identifier": "SCH-TEST"},
            "source_citations": [{"document_id": "DOC-1"}],
        },
        {
            "milestone_id": "MS-OPS-LAUNCH",
            "event_type": "IMPLEMENTATION_MILESTONE",
            "date_semantics": {"primary_date": "2022-09-05"},
            "entity_reference": {"canonical_identifier": "SCH-TEST"},
            "source_citations": [{"document_id": "DOC-2"}],
        },
    ]

    deduped = CivicTimelineService.deduplicate_milestones(milestones)
    assert len(deduped) == 2, "Different event types on the same date must remain distinct"


def test_zero_manufactured_events_unanchored_isolation():
    """Verify undated milestones remain in unanchored_milestones without synthetic timestamps."""
    service = CivicTimelineService()
    timeline = service.get_timeline("scheme", "SCH-TN-PUDHUMAI")

    unanchored = timeline["unanchored_milestones"]
    assert len(unanchored) >= 1

    for um in unanchored:
        ds = um["date_semantics"]
        assert ds["primary_date"] is None or ds["primary_date"].upper() in ("UNKNOWN", "NONE", "")
        assert ds["event_date"] is None
        assert ds["date_precision"] == "UNKNOWN"
        assert "Unanchored" in um["significance"] or "thematic" in um.get("title", "").lower() or "convergence" in um.get("title", "").lower()


def test_source_citations_integrity():
    """Verify that official source URLs, tiers, page numbers, and section references are preserved."""
    service = CivicTimelineService()
    timeline = service.get_timeline("scheme", "SCH-TN-PUDHUMAI")

    for m in timeline["chronological_milestones"]:
        citations = m.get("source_citations", [])
        assert len(citations) >= 1, f"Milestone {m['milestone_id']} must have at least one citation"
        for c in citations:
            assert c["official_url"].startswith("http"), f"Citation in {m['milestone_id']} missing official URL"
            assert "source_tier" in c, f"Citation in {m['milestone_id']} missing source tier"
            assert c["page_number"] is not None, f"Citation in {m['milestone_id']} missing page number"


def test_civic_timeline_ingestor_run_summary():
    """Verify CivicTimelineIngestor CLI entrypoint generates a correct summary."""
    summary = run_timeline_ingestion()
    assert "SCH-TN-PUDHUMAI" in summary
    pudh_summary = summary["SCH-TN-PUDHUMAI"]
    assert pudh_summary["chronological_milestones"] >= 8
    assert pudh_summary["unanchored_milestones"] >= 1
    assert pudh_summary["earliest"] == "2021-03-15"
    assert pudh_summary["latest"] >= "2025-01-01"
