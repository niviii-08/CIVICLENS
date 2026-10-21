# CIVICLENS TN — Phase 13.6: District and Constituency Civic Insights Report

## Executive Summary
Phase 13.6 establishes an evidence-backed local civic comparison framework across Tamil Nadu's administrative tiers—encompassing its 38 revenue districts, 234 Assembly constituencies (ACs), 39 Parliamentary constituencies (PCs), and Greater Chennai Corporation (GCC) municipal wards. 

Comparative public governance analysis frequently suffers from systemic distortions: comparing urban municipal corporations with rural agricultural constituencies without demographic control, conflating missing audit records with zero performance, ranking jurisdictions using unscientific composite indices, and ignoring administrative boundary reorganizations (such as district bifurcations).

Phase 13.6 resolves these epistemic vulnerabilities by enforcing strict comparability invariants:
1. **Tier & Unit Homogeneity**: Comparisons are permitted strictly within identical administrative levels (`DISTRICT` with `DISTRICT`, `CONSTITUENCY` with `CONSTITUENCY`, `WARD` with `WARD`) and identical measurement units (`PERCENT`, `INR`, `COUNT`, `HOURS`).
2. **Zero vs Unavailable Segregation**: Officially measured zero values (`value=0.0`) are strictly segregated from missing or unindexed audit periods (`value=None`, `availability_status="OUTSIDE_AUDIT_SCOPE"`). Missing data is never converted into zero activity.
3. **Prohibition of Arbitrary Composite Scores**: CIVICLENS TN explicitly bans arbitrary composite "governance ratings" or subjective scorecards. Sorting is allowed only along a single verified public metric accompanied by its algebraic formula, limitations, and an explicit non-superiority disclaimer.
4. **Contextual Divergence Warnings**: When comparing jurisdictions with divergent urban-rural demographics (>35% urban share gap), population scales (>2.5x ratio), or historical bifurcations (e.g. Chengalpattu carved from Kancheepuram in 2019), transparent warnings are surfaced.
5. **Full Documentary Traceability**: Every metric points directly to primary source documents (Census of India 2011 Primary Census Abstracts, MoSPI MPLADS ledgers, MAWS Citizen's Charter audits, ECI Delimitation Orders, and School Education EMIS portals).

---

## 1. Geographic Jurisdictions & Verified Identifiers

### 1.1 Revenue Districts (38 Districts)
- **Standard Identifier Format**: `ADM-TN-DIST-{001..038}-{NAME}` (e.g. `ADM-TN-DIST-003-CHENNAI`, `ADM-TN-DIST-004-COIMBATORE`, `ADM-TN-DIST-013-MADURAI`, `ADM-TN-DIST-022-SALEM`).
- **Standard Metadata**: Local Government Directory (LGD) codes (e.g., Chennai: 603, Coimbatore: 605, Madurai: 622), bilingual Tamil/English nomenclature, headquarters, GPS centroid coordinates, and 2011 census population.
- **Historical Bifurcations Tracked**:
  - **Chengalpattu (`ADM-TN-DIST-002-CHENGALPATTU`)**: Bifurcated from Kancheepuram on 29 November 2019 (G.O. Ms. No. 429).
  - **Tenkasi (`ADM-TN-DIST-024-TENKASI`)**: Bifurcated from Tirunelveli on 22 November 2019 (G.O. Ms. No. 427).
  - **Kallakurichi (`ADM-TN-DIST-009-KALLAKURICHI`)**: Bifurcated from Viluppuram on 12 November 2019 (G.O. Ms. No. 425).
  - **Ranipet & Tirupathur (`ADM-TN-DIST-021-RANIPET`, `ADM-TN-DIST-030-TIRUPATHUR`)**: Trifurcated from Vellore on 28 November 2019 (G.O. Ms. No. 428).
  - **Mayiladuthurai (`ADM-TN-DIST-014-MAYILADUTHURAI`)**: Bifurcated from Nagapattinam on 28 December 2020 (G.O. Ms. No. 818).

### 1.2 Electoral Constituencies (Assembly & Parliamentary)
- **Delimitation Basis**: 2008 Delimitation Commission of India Order (`ECI_DELIMITATION_ORDER_2008`).
- **Assembly Constituencies (AC)**: `AC-011` (Dr. Radhakrishnan Nagar), `AC-012` (Perambur), `AC-013` (Kolathur), `AC-085` (Mettupalayam), `AC-115` (Edappadi), etc.
- **Parliamentary Constituencies (PC)**: `PC-001` (Chennai North), `PC-002` (Chennai Central), `PC-039` (Thoothukkudi), etc.
- **Attributes**: Delimitation year (2008), reservation category (GENERAL, SC, ST), parent revenue district, and urban/rural population composition.

### 1.3 Municipal Corporations & Local Body Wards
- **Greater Chennai Corporation (GCC)**: Zones 1–15 and 200 notified electoral wards (e.g. `ADM-TN-GCC-WARD-174` Besant Nagar/Adyar, `ADM-TN-GCC-WARD-064` Kolathur North, `ADM-TN-GCC-WARD-114` Teynampet East).
- **Service Standards**: Citizen's Charter statutory SLAs (MAWS/CMWSSB/GCC).

---

## 2. Supported Comparable Metrics Catalog

| Metric Identifier | Metric Name | Unit | Supported Levels | Default Reference Period | Calculation Formula | Primary Source |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `literacy_rate_pct` | Literacy Rate | `PERCENT` | `DISTRICT`, `CONSTITUENCY` | 2011 | `(literate_pop / pop_7_plus) * 100` | Census of India 2011 (PCA) |
| `urban_pct` | Urban Population Share | `PERCENT` | `DISTRICT`, `CONSTITUENCY` | 2011 | `(urban_pop / total_pop) * 100` | Census of India 2011 (PCA) |
| `total_population` | Enumerated Population | `COUNT` | `DISTRICT`, `CONSTITUENCY`, `WARD` | 2011 | Direct enumeration aggregate | Census of India 2011 |
| `sc_pct` | Scheduled Caste Share | `PERCENT` | `DISTRICT`, `CONSTITUENCY` | 2011 | `(sc_pop / total_pop) * 100` | Census of India 2011 |
| `mplads_utilization_pct` | Fund Utilization Rate | `PERCENT` | `CONSTITUENCY` | FY2022-23 | `(expenditure / sanctioned) * 100` | MoSPI / DRDA Ledgers |
| `mplads_expenditure_inr` | Development Expenditure | `INR` | `CONSTITUENCY` | FY2022-23 | Sum of audited disbursals | State Treasury Ledgers |
| `public_works_completed_count` | Completed Works | `COUNT` | `CONSTITUENCY` | FY2022-23 | Count of verified completed projects | DRDA Progress Register |
| `sla_compliance_rate_pct` | Charter SLA Compliance | `PERCENT` | `DISTRICT`, `ZONE`, `WARD` | 2023-2024 | `(within_sla / total_resolved) * 100` | MAWS Citizen Charter Portal |
| `average_resolution_hours` | Mean Resolution Time | `HOURS` | `DISTRICT`, `ZONE`, `WARD` | 2023-2024 | Mean duration (hours) to closure | CMWSSB / GCC Audit |
| `grievances_logged_count` | Complaints Logged | `COUNT` | `DISTRICT`, `ZONE`, `WARD` | 2023-2024 | Total grievance tokens registered | TNeGA Grievance Database |
| `primary_school_attendance_pct` | Primary Attendance | `PERCENT` | `DISTRICT` | 2023-24 | EMIS daily biometric average | School Education Dept |
| `emergency_trauma_mortality_pct` | Highway 48H Mortality | `PERCENT` | `DISTRICT` | 2023-24 | `(fatalities_48h / admissions) * 100` | TNHSRP Trauma Registry |

---

## 3. Epistemic & Methodological Guardrails

### 3.1 Strict Prohibition of Arbitrary Composite Scores
```
"OBJECTIVITY GUARDRAIL: CIVICLENS TN strictly prohibits arbitrary composite civic scores.
Comparisons evaluate verified, individual public indicators with explicit methodology."
```
Arbitrary composite indices (such as weighted combinations of streetlights, literacy, and fund utilization into an opaque "82/100" score) conceal trade-offs and introduce subjective bias. In Phase 13.6, any request to rank jurisdictions by an arbitrary composite metric raises `ArbitraryScoringProhibitedError` (HTTP 400).

### 3.2 Single-Metric Defensible Ranking Standard
When citizens request ranking along a verified metric (e.g. `rank_by="literacy_rate_pct"`):
1. Values are sorted in descending order, with unavailable records placed at the bottom.
2. The exact algebraic formula and primary documentation are attached.
3. Limitations of the indicator are prominently presented.
4. An explicit disclaimer is attached:
   > *"Relative rank is strictly confined to the observed single indicator. It does NOT establish overall administrative efficacy, policy merit, or elected representative quality. Variations in baseline funding, geographic terrain, and historical deficits must be accounted for."*

### 3.3 Zero vs Unavailable Non-Conflation Rule
```
"NON-CONFLATION GUARDRAIL: Zero values (0.0) indicate an officially measured zero.
Unavailable records indicate lack of public publication and are strictly prohibited
from being presented as zero activity."
```
If a district or constituency was not covered by an audit cycle, its value is rendered as `None` with `is_unavailable=True` and `availability_status="OUTSIDE_AUDIT_SCOPE"`. The system warns that missing entries must never be interpreted as zero public activity.

### 3.4 Contextual Demographic & Boundary Divergence Warnings
- **Urban-Rural Divergence**: Triggered when the difference in urban population share across compared entities exceeds 35 percentage points (e.g., Kolathur at 100% urban vs Edappadi at 42.1% urban).
- **Population Divergence**: Triggered when population scale varies by more than 2.5x.
- **Bifurcation Context**: Triggered whenever a newly formed district (e.g. Chengalpattu, Tenkasi, Kallakurichi) is evaluated against historical pre-2019 time periods.

---

## 4. Architectural Implementation Overview

### 4.1 Service Layer: `LocalCivicComparisonService`
Located at `backend/services/local_civic_comparison_service.py`:
- `get_supported_metrics(level)`: Returns verified metrics filtered by administrative level.
- `get_supported_geographies(level)`: Returns verified district, constituency, and ward rosters.
- `get_geographic_profile(entity_type, entity_id)`: Retrieves comprehensive profile, LGD code, population, and multi-period observations.
- `compare_entities(entity_type, entity_ids, metric_id, reporting_period, rank_by)`: Validates unit/period compatibility, executes comparisons, computes single-metric ranking, and compiles contextual warnings.

### 4.2 REST API Blueprint: `backend/api/local_insights.py`
Registered under `/api/local-insights` in `backend/api/routes.py`:

| Endpoint | Method | Description | Parameters |
| :--- | :--- | :--- | :--- |
| `/api/local-insights/geographies` | `GET` | List verified districts, constituencies, and wards. | `level` (optional) |
| `/api/local-insights/metrics` | `GET` | Catalog of verified comparable civic metrics. | `level` (optional) |
| `/api/local-insights/profile/<type>/<id>` | `GET` | Detailed geographic profile and available period data. | None |
| `/api/local-insights/compare` | `POST` | Execute comparison across 2+ entities. | JSON payload |
| `/api/local-insights/compare` | `GET` | Execute comparison via query parameters. | `entity_type`, `entities`, `metric_id`, `period`, `rank_by` |

---

## 5. Automated Verification & Test Coverage

A dedicated test suite of 19 automated tests is established in `tests/unit/test_local_civic_comparisons.py`:

| Test Case | Component Tested | Verifications Performed | Status |
| :--- | :--- | :--- | :--- |
| `test_get_supported_geographies` | Service Directory | Canonical districts, constituencies, and wards lookup | **PASS** |
| `test_get_supported_metrics_catalog` | Service Directory | Units, formulas, sources, and limitations present | **PASS** |
| `test_get_geographic_profile` | Profile Retrieval | Districts, constituencies, bifurcated entities, and 404 handling | **PASS** |
| `test_compare_constituencies_success` | Comparison Engine | Multi-constituency comparison on `literacy_rate_pct` (Census 2011) | **PASS** |
| `test_compare_districts_sla_compliance` | Comparison Engine | Multi-district comparison on `sla_compliance_rate_pct` (2023-2024) | **PASS** |
| `test_incompatible_geographic_levels_rejected` | Guardrail Engine | Cross-tier comparison rejection (`IncompatibleGeographicLevelError`) | **PASS** |
| `test_metric_unsupported_at_geographic_level` | Guardrail Engine | Rejects constituency-only metric evaluated at district level | **PASS** |
| `test_arbitrary_composite_scoring_prohibited` | Guardrail Engine | Rejects arbitrary composite scores (`ArbitraryScoringProhibitedError`) | **PASS** |
| `test_defensible_single_metric_ranking` | Ranking Engine | Descending sort, relative ranks, formula, and disclaimer | **PASS** |
| `test_zero_vs_unavailable_distinction` | Guardrail Engine | Preserves `None` and `is_unavailable=True`; never outputs 0.0 | **PASS** |
| `test_demographic_divergence_warning` | Warning Engine | Flags >35% urban-rural gap (Kolathur vs Edappadi) | **PASS** |
| `test_boundary_bifurcation_warning` | Warning Engine | Surfaces G.O. Ms. No. 429 note for Chengalpattu | **PASS** |
| `test_api_list_geographies` | REST API | `GET /api/local-insights/geographies` response schema | **PASS** |
| `test_api_list_metrics` | REST API | `GET /api/local-insights/metrics` catalog response | **PASS** |
| `test_api_get_profile_success` | REST API | `GET /api/local-insights/profile/constituency/AC-013` | **PASS** |
| `test_api_get_profile_not_found` | REST API | Returns HTTP 404 for unknown geographic code | **PASS** |
| `test_api_post_compare_success` | REST API | `POST /api/local-insights/compare` end-to-end payload | **PASS** |
| `test_api_get_compare_query_params` | REST API | `GET /api/local-insights/compare` URL query execution | **PASS** |
| `test_api_prohibit_arbitrary_ranking` | REST API | Returns HTTP 400 when arbitrary composite ranking requested | **PASS** |

**Total Suite Result**: **19 passed in 17.22s**.

---

## 6. Files Created & Modified in Phase 13.6

- `backend/services/local_civic_comparison_service.py`: Core comparison engine, metric catalog, compatibility validator, and ranking calculator.
- `backend/api/local_insights.py`: REST API router supporting directories, profiles, and comparisons.
- `backend/api/routes.py`: Registered `local_insights_bp` under `/api`.
- `tests/unit/test_local_civic_comparisons.py`: 19 unit and API integration tests.
- `docs/completion_sprint/13_6_local_civic_comparisons.md`: Architectural documentation and completion report.
