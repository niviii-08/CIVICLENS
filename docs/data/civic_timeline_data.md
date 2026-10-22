# Historical Event & Civic Timeline Architecture

**CIVICLENS TN Data Pipeline Documentation**  
**Component:** Civic Timeline Reconciliation, Multi-Date Semantics, and Lifecycle Milestones  
**Source Registry Ref:** `docs/data/verified_source_registry.md` (`SRC-GOV-001`, `SRC-BUD-001`, `SRC-BUD-002`, `SRC-STA-001`, `SRC-AUD-001`)  
**Ingestion & Core Services:** `backend/services/civic_timeline_service.py`, `backend/ingestion/civic_timeline_ingestor.py`  
**Test Suites:** `tests/unit/test_civic_timelines.py`, `tests/unit/test_civic_timeline_records.py`

---

## 1. Executive Summary

Public governance initiatives across Tamil Nadu progress through complex, multi-year lifecycles—spanning electoral manifesto pledges, legislative budget speeches, statutory Government Orders (G.O.s), treasury fund releases, field execution, longitudinal outcome surveys, and constitutional audits.

The **CIVICLENS TN Civic Timeline Engine** establishes an auditable, source-backed temporal tracking framework. It reconstructs these lifecycles while enforcing strict epistemic guardrails:
1. **Sequence Is Not Causation:** Temporal precedence between an announcement and a social metric change never constitutes proof of policy causation.
2. **Non-Inference Rule:** An announcement or budget sanction never proves execution, and a news report's publication date is never inferred as an empirical project completion date.
3. **Multi-Source Deduplication:** Corroborating reports of the same civic event are merged into a unified milestone that retains provenance from all sources.
4. **Superseded Orders & Revisions:** Revised government orders and amendments are preserved transparently rather than overwriting historical records.
5. **Zero Manufactured Events:** Milestones lacking reliable calendar dates remain isolated in `unanchored_milestones` without synthetic timestamps.

---

## 2. The Eight Standard Lifecycle Event Statuses

Every civic milestone ingested or extracted is classified into one of eight standardized lifecycle statuses:

| Lifecycle Status | Associated Event Types | Institutional Governance Meaning | Statutory Proof Required |
|:---|:---|:---|:---|
| **`PROPOSED`** | `PROMISE_ANNOUNCEMENT`, `POLICY_PROPOSAL` | Electoral pledge, manifesto commitment, or preliminary reform draft. | Official Party Manifesto or Whitepaper |
| **`ANNOUNCED`** | `CABINET_ANNOUNCEMENT`, `POLICY_ANNOUNCEMENT`, `CLAIM_STATEMENT` | Formal legislative speech, ministerial address, or cabinet resolution. | TNLA Budget Speech / Official DIPR Release |
| **`APPROVED`** | `STATUTORY_NOTIFICATION`, `POLICY_ENACTMENT`, `GOVERNMENT_ORDER` | Administrative sanction, statutory rule notification, or legal order. | Tamil Nadu Government Gazette / G.O. (Ms) |
| **`FUNDED`** | `BUDGET_ALLOCATION`, `BUDGET_REVISION`, `FUND_RELEASE` | Legislative appropriation, revised demand for grant, or treasury release. | Detailed Demands for Grants / Budget Books |
| **`STARTED`** | `IMPLEMENTATION_STARTED`, `IMPLEMENTATION_MILESTONE`, `GRIEVANCE_FILED` | Operational enrollment launch, portal opening, or field execution start. | Department Circular / Official Launch Launch Order |
| **`COMPLETED`** | `ACTION_TAKEN`, `DELIVERY_COMPLETED`, `WORK_COMPLETED` | Verified direct service delivery completion, infrastructure handover. | Department Policy Note / Utilization Certificate |
| **`AUDITED`** | `CLAIM_VERIFICATION`, `AUDIT_SCRUTINY`, `HUMAN_AUDITOR_REVIEW` | Independent review, constitutional audit scrutiny, or fact verification. | CAG Audit Report (Art 151) / PAC Proceedings |
| **`OUTCOME_REPORTED`**| `OUTCOME_EVALUATION` | Longitudinal demographic census, welfare survey, or institutional evaluation. | AISHE / NSSO / State Planning Commission Report |

---

## 3. The Six Distinct Date Dimensions

To prevent the conflation of media coverage dates with operational delivery dates, every milestone strictly maintains six distinct date dimensions under `date_semantics`:

```
+---------------------------------------------------------------------------------------------------------+
|                                      Six-Dimensional Date Semantics                                     |
+-------------------+----------------------------+--------------------------------------------------------+
| Date Dimension    | ISO Format / Example       | Epistemic Governance Definition                        |
+-------------------+----------------------------+--------------------------------------------------------+
| event_date        | 2022-09-05T10:30:00Z       | The substantive moment when the real-world action took  |
|                   |                            | place (e.g. CM launch ceremony, DBT transfer run).     |
+-------------------+----------------------------+--------------------------------------------------------+
| announcement_date | 2022-03-18T11:00:00Z       | The date when the initiative was first formally        |
|                   |                            | announced in an election manifesto or budget speech.   |
+-------------------+----------------------------+--------------------------------------------------------+
| publication_date  | 2022-09-05T12:00:00Z       | The official gazette release, press release issue,     |
|                   |                            | or secondary journalistic article publication date.    |
+-------------------+----------------------------+--------------------------------------------------------+
| effective_date    | 2022-09-05T00:00:00Z       | The statutory or administrative date from which rules  |
|                   |                            | or financial entitlements take legal effect.           |
+-------------------+----------------------------+--------------------------------------------------------+
| reporting_period  | "2022-2023", "2023-2024"   | The financial year, census period, or survey cohort    |
|                   |                            | covering the record.                                   |
+-------------------+----------------------------+--------------------------------------------------------+
| retrieval_date    | 2026-10-14T00:00:00Z       | The exact timestamp when the record was ingested and   |
|                   |                            | indexed by the CIVICLENS TN platform.                  |
+-------------------+----------------------------+--------------------------------------------------------+
```

### Strict Non-Conflation Rules:
- **`primary_date`** serves strictly as the chronological anchor for linear rendering (`YYYY-MM-DD`).
- **No News-to-Completion Inference:** If an article published on 2024-04-15 reports on bridge construction, `publication_date` is `2024-04-15`, but `event_date` must reflect the empirical completion certificate date, not the article release date.
- **Divergence Surfacing:** When `event_date` and `publication_date` diverge, the system flags a warning to document administrative publishing latency.

---

## 4. Superseded Orders, Amendments & Conflicting Dates

Government policy frequently evolves through amending orders. Deleting older records or overwriting them with current orders corrupts the historical civic record.

### Handling Superseded Records:
When an administrative order (e.g. `G.O. (Ms) No. 22`) is replaced or revised by a later order (e.g. `G.O. (Ms) No. 34`):
1. **The earlier milestone remains** in the timeline to preserve historical truth.
2. The earlier milestone sets:
   - `date_semantics.is_superseded = True`
   - `date_semantics.superseded_by = "G.O. (Ms) No. 34, SW&WE Dept dated 2022-09-05"`
   - `date_semantics.has_date_conflict = True`
   - `date_semantics.conflict_explanation = "Preliminary draft guidelines issued in G.O. 22 were subsequently superseded by comprehensive regulations in G.O. 34."`
3. The UI and API render superseded milestones with distinct visual indicators, preventing citizens from assuming expired guidelines remain active.

---

## 5. Multi-Source Deduplication & Citation Aggregation

The same milestone is frequently published by official gazettes, press releases (DIPR), and news reports. Multiple records describing the identical substantive event must not clutter the civic timeline.

### Deduplication Logic:
The pipeline deduplicates milestones based on the compound key:
$$\text{DedupKey} = \text{CanonicalEntityID} + \text{EventType} + \text{DateKey (YYYY-MM-DD)}$$

```
Source 1: G.O. (Ms) No. 34 (Tier 1 Statutory) ───┐
                                                  ├──► Merged Canonical Milestone
Source 2: DIPR Press Release (Tier 1 Official) ───┤    (Aggregated source_citations)
                                                  │
Source 3: The Hindu News Article (Tier 4 Media) ─┘
```

- **Provenance Preservation:** All distinct document citations are aggregated into the canonical milestone's `source_citations` array.
- **Granular Tie-Breaking:** If two different event types occur on the same day (e.g. `STATUTORY_NOTIFICATION` and `IMPLEMENTATION_MILESTONE`), both records are retained in chronological precedence sequence defined by `EVENT_TYPE_PRECEDENCE`.

---

## 6. Zero Manufactured Events & Epistemic Guardrails

A timeline must never manufacture timestamps or insert synthetic dates to produce an artificially seamless progression.

1. **Unanchored Milestones Isolation:**
   - Any milestone lacking a verifiable, authoritative calendar date is assigned `primary_date: None` and placed in `unanchored_milestones`.
   - Examples include thematic convergence proposals, ongoing inter-departmental working drafts, or high-level program visions.
2. **Epistemic Notices & Guardrails:**
   Every generated timeline response embeds immutable epistemological guardrails:
   - `causation_limitation`: *"Temporal proximity in civic timelines does not establish causal efficacy. Intervening policy shifts, demographic trends, and macroeconomic variables must be independently evaluated."*
   - `date_semantics_notice`: *"Primary dates represent chronological anchors. Substantive implementation dates, statutory effective dates, and publication dates may diverge."*
   - `inferred_relationship_disclosure`: *"Connections established via machine inference are labeled with confidence scores and require human verification."*

---

## 7. Canonical Coverage Matrix

| Entity Code | Entity Name / Scope | Chronological Milestones | Unanchored Records | Date Coverage Span | Lifecycle Stages Corroborated |
|:---|:---|:---:|:---:|:---:|:---|
| **`SCH-TN-PUDHUMAI`** | Pudhumai Penn Higher Education Assurance Scheme | 9 | 1 | 2021-03-15 to 2025-02-15 | All 8 (`PROPOSED`, `ANNOUNCED`, `APPROVED` [including Superseded G.O. 22], `STARTED`, `FUNDED`, `COMPLETED`, `OUTCOME_REPORTED`, `AUDITED`) |
| **`SCH-SW-KMUT`** | Kalaignar Magalir Urimai Thittam (KMUT) | 7 | 1 | 2021-03-15 to 2025-01-20 | `PROPOSED`, `FUNDED` (BE), `STARTED`, `FUNDED` (RE), `OUTCOME_REPORTED`, `AUDITED` |
| **`CIV-2024-0891`** | Kolathur Ward 64 Water Contamination Grievance | 3 | 0 | 2024-06-12 to 2024-06-18 | `STARTED` (Filed), `STARTED` (Inspected), `COMPLETED` (ATR Rectified) |

---

## 8. Verification & Test Suite Summary

The timeline engine and date-semantics rules are verified by 25 unit tests across two suites:

```
tests/unit/test_civic_timelines.py (16 Tests):
  - test_canonical_scheme_timeline_ordering .................... PASSED
  - test_date_semantics_separation ............................. PASSED
  - test_unanchored_milestones_no_synthetic_dates .............. PASSED
  - test_identical_dates_tie_breaking .......................... PASSED
  - test_date_conflict_detection_and_surfacing ................. PASSED
  - test_connection_basis_and_inference_disclosure ............. PASSED
  - test_epistemic_non_causation_guardrails ..................... PASSED
  - test_civic_issue_timeline_lifecycle ........................ PASSED
  - test_database_backed_scheme_milestones ..................... PASSED
  - test_api_list_available_timelines .......................... PASSED
  - test_api_get_scheme_timeline_success ....................... PASSED
  - test_api_get_civic_issue_timeline_success .................. PASSED
  - test_api_get_journey_timeline_success ...................... PASSED
  - test_api_filter_date_range ................................. PASSED
  - test_api_exclude_unanchored ................................ PASSED
  - test_api_not_found_entity .................................. PASSED

tests/unit/test_civic_timeline_records.py (9 Tests):
  - test_eight_lifecycle_statuses_presence ..................... PASSED
  - test_six_distinct_date_dimensions .......................... PASSED
  - test_non_inference_announcement_not_completion ............. PASSED
  - test_superseded_orders_transparent_handling ................ PASSED
  - test_multi_source_deduplication_and_citation_merging ....... PASSED
  - test_same_date_distinct_event_types_not_collapsed .......... PASSED
  - test_zero_manufactured_events_unanchored_isolation ......... PASSED
  - test_source_citations_integrity ............................ PASSED
  - test_civic_timeline_ingestor_run_summary ................... PASSED
```

**Total:** 25 passed in ~11s, zero failures.
