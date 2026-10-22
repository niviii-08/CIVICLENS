# CIVICLENS TN — Phase 13.9: Cross-Module Civic Intelligence Integration

## 1. Executive Summary

Phase 13.9 establishes a unified, traceable cross-module civic intelligence experience across all **CIVICLENS TN** capabilities developed in Phases 13.1 through 13.8:
1. **Manifesto Promises & Policy Outcomes** (Phase 13.2)
2. **Schemes, Budgets & Reported Results** (Phase 13.3)
3. **Public Claim Verifications & Evidence Dossiers** (Phase 13.4)
4. **Evidence-Backed Civic Timelines** (Phase 13.5)
5. **District & Constituency Civic Insights** (Phase 13.6)
6. **Transparent Public Reports & Multi-Format Exports** (Phase 13.7)
7. **Saved Civic Tracking & Live Updates** (Phase 13.8)

Rather than keeping these civic analytical tools isolated in separate routes, Phase 13.9 weaves them into a coherent **360-degree Civic Intelligence Engine**. Citizens exploring any single record—whether a manifesto promise, government welfare scheme, legislative representative, fact-check claim, or municipal grievance—can seamlessly transition across chronological timelines, budget disbursements, evidence dossiers, geographic profiles, exportable public reports, and real-time saved tracking without encountering dead ends, disjoint tables, or unsupported causal assumptions.

---

## 2. Integrated Architecture & Service Orchestration

Phase 13.9 integrates existing domain services through a centralized orchestration layer in `backend/services/cross_phase_integration_service.py` (`CrossPhaseIntegrationService`), backed by unified REST API endpoints in `backend/api/integration.py`:

```
                                  ┌──────────────────────────────────────────────┐
                                  │      CrossPhaseIntegrationService            │
                                  │ (Phase 13.9 Cross-Module Intelligence Engine)│
                                  └──────────────────────┬───────────────────────┘
                                                         │
             ┌───────────────────┬───────────────────────┼───────────────────────┬───────────────────┐
             │                   │                       │                       │                   │
             ▼                   ▼                       ▼                       ▼                   ▼
    ┌─────────────────┐ ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐ ┌─────────────────┐
    │  CivicTimeline  │ │  SchemeBudget   │     │ ClaimAssessment │     │ LocalComparison │ │TransparentReport│
    │     Service     │ │  ImpactService  │     │     Service     │     │     Service     │ │     Service     │
    │  (Phase 13.5)   │ │  (Phase 13.3)   │     │  (Phase 13.4)   │     │  (Phase 13.6)   │ │  (Phase 13.7)   │
    └─────────────────┘ └─────────────────┘     └─────────────────┘     └─────────────────┘ └─────────────────┘
             │                                                                                       │
             └───────────────────────────────────┬───────────────────────────────────────────────────┘
                                                 │
                                                 ▼
                                  ┌─────────────────────────────┐
                                  │   SavedCivicTrackingService │
                                  │        (Phase 13.8)         │
                                  └─────────────────────────────┘
```

### 2.1. Canonical Identifiers & Deterministic Aliases
To prevent joining records by ambiguous colloquial names or silently creating duplicate entities, canonical identifiers are strictly resolved:
* **Government Schemes:** `SCH-SW-KMUT` (aliases: `KMUT`, `MAGALIR`, `SCH-TN-KMUT`, `1`), `SCH-EDU-BREAKFAST`, `SCH-HE-PUDHUMAI`, `SCH-MA-SINGARA`
* **Manifesto Promises:** `PRM-DMK-2021-001` (aliases: `14`, `PRM-14`, `PRM-001`), `PRM-DMK-2021-003`, `PRM-DMK-2021-112`
* **Policy Evaluations:** `POL-TN-KMUT` (aliases: `POL-2023-KMUT`, `POL-KMUT`), `POL-TN-BREAKFAST`, `POL-TN-PUDHUMAI`
* **Public Claims:** `CLM-TN-2024-001` (aliases: `CLM-2024-001`, `CLM-001`), `CLM-TN-001`
* **Civic Issues:** `CIV-2024-0891` (aliases: `CIV-0891`, `891`)
* **Representatives:** `REP-AC-139` (aliases: `REP-001`, `REP-MLA-042`, `STALIN`), `REP-AC-086` (`EPS`)
* **Administrative Geography:** `AC-139` (`KOLATHUR`), `AC-013`, `CHENNAI`, `COIMBATORE`

---

## 3. Supported Inter-Module Navigation Pathways

Citizens can navigate bidirectionally between records across seven primary dimensions:

| Originating Module | Target Civic Capability | Integration Mechanism | Provenance & Navigation Route |
| :--- | :--- | :--- | :--- |
| **Manifesto Promise** (`PRM-DMK-2021-001`) | **Welfare Scheme & Policy Evaluation** | `CONN_DIRECT` | G.O. Ms No. 41 & State Planning Commission Study (`POL-TN-KMUT`) |
| **Government Scheme** (`SCH-SW-KMUT`) | **Budget Disbursals & Treasury Audit** | `CONN_DIRECT` / `CONN_EVIDENCE` | Demands for Grants (Demand 41), Treasury Ledgers & CAG Reports |
| **Public Claim** (`CLM-TN-2024-001`) | **Fact-Check Dossier & Atomic Sources** | `CONN_EVIDENCE` | Direct Benefit Transfer (DBT) credit statements & Official Gazette |
| **Civic Grievance** (`CIV-2024-0891`) | **Local MLA & Remediation Funding** | `CONN_EVIDENCE` | Greater Chennai Corp Ward 64 Delimitation to `AC-139` & Singara Chennai 2.0 |
| **Geographic Comparison** (`CHENNAI` / `AC-139`) | **Administrative Profiles & Civic Issues** | `CONN_DIRECT` | ECI Delimitation Orders & Municipal SLA compliance logs |
| **Civic Timeline** (`/timelines`) | **Underlying Source Milestones** | Context-Preserving Links | Chronological milestones with `?origin=timeline&highlight=MS-001` |
| **Saved Items** (`/saved`) | **Live Detail & Status Updates** | Stateless Change Verification | Local-first tracking payload with direct link to current detail |

---

## 4. Explicit vs. Inferred Relationship Differentiation

CIVICLENS TN enforces strict epistemic standards to distinguish verified institutional linkages from candidate algorithmic hypotheses:

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       RELATIONSHIP CLASSIFICATION                                      │
├─────────────────────────┬─────────────────────────┬────────────────────────────────────────────────────┤
│ Connection Type         │ Epistemic Meaning       │ Governance & Safeguards                            │
├─────────────────────────┼─────────────────────────┼────────────────────────────────────────────────────┤
│ direct_identifier       │ Statutory / FK Match    │ 100% confidence. Backed by Government Orders (G.O.) │
│                         │                         │ or canonical database foreign keys.                │
├─────────────────────────┼─────────────────────────┼────────────────────────────────────────────────────┤
│ evidence_relationship   │ Documentary Citation    │ Documented in primary audits (CAG, PAC), official  │
│                         │                         │ gazettes, or treasury bank accounts.               │
├─────────────────────────┼─────────────────────────┼────────────────────────────────────────────────────┤
│ inferred_relationship   │ Algorithmic Hypothesis  │ Generated via NLP thematic similarity or clustering│
│                         │                         │ MUST display mandatory caveat; excluded when       │
│                         │                         │ include_inferred=false.                            │
└─────────────────────────┴─────────────────────────┴────────────────────────────────────────────────────┘
```

### Mandatory Inferred Caveat
Every inferred relationship payload automatically includes the standard epistemic warning:
> *"Automated Candidate: This connection was suggested by algorithmic analysis and has not been verified by a statutory government document or audit."*

---

## 5. Multi-Hop Discovery & Cycle-Safe Graph Traversal

To allow citizens to trace multi-step civic connections (e.g., *Civic Grievance &rarr; Ward Delimitation &rarr; Sitting MLA &rarr; Party Manifesto Commitment &rarr; Government Welfare Scheme*) without risking infinite loops or memory exhaustion, `CrossPhaseIntegrationService.get_multi_hop_path` implements a **cycle-safe Breadth-First Search (BFS)**:

1. **Cycle Prevention:**
   Maintains an explicit `visited: Set[Tuple[str, str]]` recording `(node_id, node_type)` pairs. If an intermediate entity has already been expanded, it is immediately skipped, preventing circular traversal loops (`A -> B -> A`).
2. **Bounded Depth:**
   The parameter `max_hops` is bounded between 1 and 5 (default: 3). If no path is discovered within the boundary, the service returns `found: False` without recursive exhaustion.
3. **Cumulative Confidence:**
   Computes the cumulative confidence score along the discovery path as the multiplicative product of all intermediate edge confidences ($C_{\text{path}} = \prod C_{\text{edge}}$).
4. **Non-Causal Caveat:**
   Every multi-hop discovery response is stamped with the platform guardrail:
   > *"Multi-hop civic relationship establishes documentary or administrative traceability. It does NOT assert unilateral causality, individual culpability, or sole attribution."*

---

## 6. The 7 Canonical Cross-Module Citizen Journeys

Phase 13.9 exposes the seven primary citizen navigation journeys through `GET /api/integration/journeys/phase13`:

1. **Journey 1: Promise Tracking & Policy Outcome Evidence** (`journey-p13-1-promise-to-outcome`)
   - *Route:* `/promises/PRM-DMK-2021-001`
   - *Path:* Promise #14 &rarr; Scheme `SCH-SW-KMUT` (G.O. Ms No. 41) &rarr; Planning Commission Evaluation `POL-TN-KMUT` &rarr; Timeline & Export Report.
2. **Journey 2: Scheme & Budget Impact Analysis** (`journey-p13-2-scheme-budget-impact`)
   - *Route:* `/schemes/SCH-SW-KMUT`
   - *Path:* Scheme allocations (₹7,000 Cr &rarr; ₹13,720 Cr) &rarr; Demand 41 &rarr; Treasury DBT credits &rarr; CAG Audit variance report.
3. **Journey 3: Public Claim Assessment & Evidence Dossier** (`journey-p13-3-claim-evidence-dossier`)
   - *Route:* `/claims/CLM-TN-2024-001`
   - *Path:* 1.15+ Crore beneficiary count claim &rarr; Atomic propositions &rarr; Treasury disbursal statements &rarr; Primary gazette dossier.
4. **Journey 4: Civic Issue & Administrative Accountability** (`journey-p13-4-civic-issue-resolution`)
   - *Route:* `/civic/CIV-2024-0891`
   - *Path:* Drinking water grievance (PII masked) &rarr; Ward 64 / AC-139 &rarr; Kolathur MLA (`REP-AC-139`) &rarr; Singara Chennai 2.0 work order (`SCH-MA-SINGARA`).
5. **Journey 5: Comparable Geographic Civic Insights** (`journey-p13-5-geographic-comparison`)
   - *Route:* `/explore/local`
   - *Path:* Chennai vs Coimbatore municipal delivery &rarr; Kolathur `AC-139` profile &rarr; MLACDS expenditure &rarr; District comparison export.
6. **Journey 6: Chronological Civic Timelines to Source Records** (`journey-p13-6-timeline-traceability`)
   - *Route:* `/timelines`
   - *Path:* Chronological progression &rarr; Announcement vs Enactment vs Platform Index dates &rarr; Milestone deep link (`?origin=timeline&highlight=MS-001`).
7. **Journey 7: Saved Civic Tracking & Live Updates** (`journey-p13-7-saved-tracking-updates`)
   - *Route:* `/saved`
   - *Path:* Local browser bookmarking &rarr; Stateless status inspection &rarr; Change alerts with official source links &rarr; Live record detail.

---

## 7. Privacy Protection & DPDPA 2023 Compliance

In accordance with the **Digital Personal Data Protection Act (DPDPA) 2023** and platform architectural guidelines:
* **PII Redaction:** Any citizen personal identifier appearing in civic grievances or citizen-submitted records is sanitized before being returned across cross-module intelligence endpoints.
  - Indian mobile numbers (10 digits starting with 6–9) &rarr; `[Phone Redacted]`
  - Aadhaar numbers (12 digits) &rarr; `[Aadhaar Redacted]`
  - Email addresses &rarr; `[Email Redacted]`
  - Complainant names &rarr; `[Citizen Name Redacted for Privacy]`
* **Local-First Tracking:** The saved items tracking engine requires zero user accounts, zero personal credentials, and zero telemetry tracking.
* **Empty State Safeguard:** When no verified relationships exist, the platform returns explicit empty states (`has_related_records: False`) and never hallucinates synthetic links.

---

## 8. Context-Preserving URL Routing

Navigation between modules preserves citizen research context through standardized query parameters:
* `build_contextual_url(base_route, record_id, origin, highlight, tab, extra_params)`:
  - Timeline to Record: `/promises/PRM-DMK-2021-001?origin=timeline&highlight=MS-KMUT-2021-PLEDGE`
  - Report to Record: `/claims/CLM-TN-2024-001?origin=public_report&report_id=RPT-CLM-001`
  - Saved Items to Record: `/schemes/SCH-SW-KMUT?origin=saved_tracking&tracked=true`
  - Local Profile to Civic Issue: `/civic/CIV-2024-0891?origin=local_comparison&geo=AC-139`

---

## 9. Verification & Automated Test Results

Phase 13.9 verification was executed across the full test suite and frontend type checks:

### 9.1. Unit and Integration Test Suite
* **Test File:** `tests/unit/test_cross_module_integration.py` (15 tests) & `tests/api/test_cross_phase_integration.py` (10 tests)
* **Command:** `pytest tests/api/test_cross_phase_integration.py tests/unit/test_cross_module_integration.py -v`
* **Result:** **25 passed in 2.74s** (100% passing)

### 9.2. Complete Phase 13 Regression Test Suite
* **Command:** `pytest tests/unit/test_scheme_budget_impact_analysis.py tests/unit/test_claim_assessment_transparency.py tests/unit/test_civic_timelines.py tests/unit/test_local_civic_comparisons.py tests/unit/test_transparent_reports.py tests/unit/test_saved_tracking.py tests/unit/test_cross_module_integration.py -v`
* **Result:** **114 passed in 17.67s** (100% passing)

### 9.3. Frontend TypeScript Integrity
* **Command:** `npm run typecheck --prefix frontend`
* **Result:** **Clean compile (`tsc --noEmit`), 0 errors**.

---

## 10. Summary of Phase 13.9 Deliverables

| Deliverable | File Path | Scope & Functionality |
| :--- | :--- | :--- |
| **Cross-Phase Integration Service** | [`backend/services/cross_phase_integration_service.py`](file:///backend/services/cross_phase_integration_service.py) | Added 360-degree Civic Intelligence Engine, cycle-safe multi-hop BFS, canonical Phase 13 journeys, and contextual URL builder. |
| **Cross-Phase API Blueprint** | [`backend/api/integration.py`](file:///backend/api/integration.py) | Added `/api/integration/cross-module/<type>/<id>`, `/api/integration/journeys/phase13`, and `/api/integration/path`. |
| **Frontend API Client** | [`frontend/src/lib/api.ts`](file:///frontend/src/lib/api.ts) | Added TypeScript interfaces and client functions for cross-module intelligence, Phase 13 journeys, and multi-hop paths. |
| **Integration Test Suite** | [`tests/unit/test_cross_module_integration.py`](file:///tests/unit/test_cross_module_integration.py) | 15 comprehensive unit & API integration tests covering all 12 Phase 13.9 requirements. |
| **Documentation Report** | [`docs/completion_sprint/13_9_cross_module_integration.md`](file:///docs/completion_sprint/13_9_cross_module_integration.md) | Exhaustive sprint report detailing architecture, journeys, epistemic guardrails, and test evidence. |
