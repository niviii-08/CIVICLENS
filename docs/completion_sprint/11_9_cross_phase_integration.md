# CIVICLENS TN — Phase 11.9: Cross-Phase Record Integration

## 1. Executive Summary

Phase 11.9 connects relevant civic records across all 10 modules of CIVICLENS TN while preserving the platform's strict evidentiary discipline and epistemic integrity. Ordinary citizens can now seamlessly navigate between welfare schemes, election manifesto promises, representative performance, civic grievances, public claims, and policy outcome evaluations without confronting dead ends, disjoint tables, or unverified assertions.

Prior to Phase 11.9, individual phases maintained isolated cross-phase junctions or bespoke database schemas without a unified citizen discovery pathway. Phase 11.9 establishes a centralized **Cross-Phase Integration Service** (`CrossPhaseIntegrationService`), a public REST API (`/api/integration/related/...`, `/api/integration/matrix`, `/api/integration/journeys`), enhanced frontend record detail displays with clear connection type classifications, citizen privacy redactions, and empty state protections.

---

## 2. Cross-Phase Integration Audit Matrix

The audit below summarizes all verified inter-module relationships across Phases 1–10:

| Source Record Type | Related Record Type | Relationship Source | API / Database Support | Validation Requirements | Implementation Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Government Scheme** (Phase 2) | **Policy Evaluation** (Phase 10) | Canonical Scheme Code (`canonical_scheme_code`) & DB Foreign Key | `GET /api/policy-evaluation/policies?scheme_id=...` & `GET /api/integration/related/scheme/<id>` | Exact code match or validated alias; non-causal attribution disclaimer enforced. | **IMPLEMENTED & VERIFIED** |
| **Government Scheme** (Phase 2) | **Manifesto Promise** (Phase 3) | Junction Table (`PromiseSchemeLink`) & Statutory Order Citations | `GET /api/promises/<promise_id>/scheme-matches` | Deterministic ID link or similarity score $\ge 0.85$ with candidate caveat. | **IMPLEMENTED & VERIFIED** |
| **Manifesto Promise** (Phase 3) | **Representative** (Phase 6) | Junction Table (`PromisePerformanceLink`) & Party Sponsorship | `GET /api/representatives/<rep_id>/promises` | Electoral term synchronization; macro-outcomes not attributed solely to individual representative. | **IMPLEMENTED & VERIFIED** |
| **Public Claim** (Phase 7) | **Government Scheme** (Phase 2) | Junction Table (`ClaimCrossPhaseLink`) & Statutory Evidence Citations | `GET /api/claims/<claim_id>/cross-phase` | Atomic proposition decomposition; source tier $\ge \text{TIER\_2}$. | **IMPLEMENTED & VERIFIED** |
| **Civic Issue** (Phase 8) | **Representative** (Phase 6) | Delimitation & Administrative Boundary Mapping (Ward $\to$ AC) | `GET /api/civic/issues/<issue_id>/cross-phase` | Strict citizen PII redaction; spatial co-occurrence does not imply individual culpability. | **IMPLEMENTED & VERIFIED** |
| **Civic Issue** (Phase 8) | **Government Scheme** (Phase 2) | Departmental Work Order & Remediation Funding (`CivicCrossPhaseLink`) | `GET /api/civic/issues/<issue_id>/cross-phase` | Confirmed public work voucher or municipal budget line. | **IMPLEMENTED & VERIFIED** |
| **Evidence Node** (Phase 9) | **All Entities** (Phases 1–10) | Evidence Graph Edge (`CivicEvidenceEdge`) & Candidate Proposals | `GET /api/graph/nodes/<node_id>/connected-entities` | Confidence score $\ge 0.8$ for verified edges; automated proposals flagged as inferred. | **IMPLEMENTED & VERIFIED** |

---

## 3. Canonical Identifiers & Alias Resolution

To prevent joining records solely by ambiguous display names and to prevent silent merging of duplicate-looking entities, canonical identifiers are strictly enforced:

1. **Deterministic Canonical Identifiers**:
   - Schemes: `SCH-SW-KMUT`, `SCH-EDU-BREAKFAST`, `SCH-HE-PUDHUMAI`, `SCH-MA-SINGARA`
   - Promises: `PRM-DMK-2021-001`, `PRM-DMK-2021-003`, `PRM-DMK-2021-112`
   - Policy Evaluations: `POL-TN-KMUT`, `POL-TN-BREAKFAST`, `POL-TN-PUDHUMAI`
   - Claims: `CLM-TN-2024-001`, `CLM-TN-001`, `CLM-TN-002`
   - Civic Issues: `CIV-2024-0891`
   - Representatives: `REP-AC-139` (Kolathur), `REP-AC-086` (Edappadi)

2. **Explicit Alias Mapping (`RECORD_ALIASES`)**:
   Colloquial citizen queries and legacy IDs are resolved deterministically without database duplication:
   - `KMUT` / `MAGALIR` / `1` $\longrightarrow$ `SCH-SW-KMUT`
   - `14` / `PRM-14` $\longrightarrow$ `PRM-DMK-2021-001`
   - `POL-2023-KMUT` $\longrightarrow$ `POL-TN-KMUT`
   - `CLM-2024-001` $\longrightarrow$ `CLM-TN-2024-001`
   - `REP-001` / `REP-MLA-042` $\longrightarrow$ `REP-AC-139`

---

## 4. Supported Citizen Navigation Journeys

The platform supports 6 canonical cross-phase journeys:

1. **Government Scheme $\longrightarrow$ Policy Evaluation $\longrightarrow$ Published Outcome Evidence**:
   - *Example*: Citizen opens Kalaignar Magalir Urimai Thittam ([`/schemes/SCH-SW-KMUT`](file:///schemes/SCH-SW-KMUT)), navigates to the State Planning Commission evaluation ([`/policy-evaluation/POL-TN-KMUT`](file:///policy-evaluation/POL-TN-KMUT)), and reviews verified beneficiary discretionary spending data.
2. **Manifesto Promise $\longrightarrow$ Documented Implementation Activity $\longrightarrow$ Sources**:
   - *Example*: Citizen checks DMK 2021 Manifesto Promise #14 ([`/promises/PRM-DMK-2021-001`](file:///promises/PRM-DMK-2021-001)) and follows the verified link to G.O. Ms No. 41 and the operational welfare scheme.
3. **Public Claim $\longrightarrow$ Verification Assessment $\longrightarrow$ Original Source Documents**:
   - *Example*: Citizen views claim fact-check on 1.15+ Crore beneficiary count ([`/claims/CLM-TN-2024-001`](file:///claims/CLM-TN-2024-001)), inspects verified treasury disbursals, and reads the primary gazette.
4. **Civic Issue $\longrightarrow$ Department Response $\longrightarrow$ Available Resolution Evidence**:
   - *Example*: Citizen inspects drinking water grievance in Kolathur ([`/civic/CIV-2024-0891`](file:///civic/CIV-2024-0891)), reviews CMWSSB pipeline replacement within statutory SLA, and explores links to Singara Chennai 2.0 remediation funding.
5. **Representative $\longrightarrow$ Relevant Public Records $\longrightarrow$ Source Documents**:
   - *Example*: Citizen inspects Kolathur MLA profile ([`/representatives/REP-AC-139`](file:///representatives/REP-AC-139)), reviews local constituency works and party manifesto commitments.
6. **Political Funding / News Coverage $\longrightarrow$ Relevant Public Records**:
   - *Example*: Citizen reviews electoral VAT reduction pledges ([`/promises/PRM-DMK-2021-003`](file:///promises/PRM-DMK-2021-003)) and follows documentary links to CAG audit variances.

---

## 5. Explaining Relationships & Epistemic Boundaries

Every related record is classified into one of three distinct connection types:

| Connection Type | Plain-Language Label | Visual Badge | Epistemic Meaning & Governance |
| :--- | :--- | :--- | :--- |
| **`direct_identifier`** | Directly Linked by Identifier | Blue pill (`Link2` icon) | Factually established linkage via database foreign key, statutory scheme code, or gazette order. 100% confidence. |
| **`evidence_relationship`** | Documented Evidence Link | Emerald pill (`ShieldCheck` icon) | Connected through an explicit primary source citation or verified knowledge graph edge. |
| **`inferred_relationship`** | Automated / Inferred Match | Amber pill (`AlertTriangle` icon) | Algorithmic suggestion (e.g. NLP thematic similarity). **Must not be presented as established fact.** Displays mandatory caveat: *"Suggested by automated analysis; not an official government linkage."* |

---

## 6. Privacy Protection & Empty State Safeguards

1. **Citizen PII Masking**:
   - Complainant personal details in civic grievance records are scrubbed before exposure in related-record payloads.
   - Phone numbers, Aadhaar numbers, and email addresses are redacted to `[Phone Redacted]`, `[Aadhaar Redacted]`, and `[Citizen Name Redacted for Privacy]`.
2. **Missing Relationship Handling**:
   - When a record has no verified connections, the API returns `total_count: 0` and `related_records: []`.
   - The frontend renders `CivicStateNotice` with `state="no_records_available"`, explaining:
     > *"No connected public records are currently linked to this record in the verified knowledge base. CivicLens TN maintains strict evidence integrity and does not infer connections without verified statutory or audit linkage."*
   - Dummy records are **never** fabricated to populate the UI.
3. **Query Boundedness**:
   - All relational database queries are bounded by `limit <= 50`, preventing expensive unbounded scans or memory exhaustion.

---

## 7. Verification & Test Results

1. **Cross-Phase Integration Test Suite**:
   - Ran `pytest tests/api/test_cross_phase_integration.py -v`.
   - **Result**: **10 passed in 2.26s** (100% passing).
2. **Complete API Regression Test Suite**:
   - Ran `pytest tests/api/ -v`.
   - **Result**: **All 65 API tests passed** with zero regressions.
3. **Frontend TypeScript Compilation**:
   - Ran `npx tsc -p frontend --noEmit`.
   - **Result**: Passed with **0 errors**.
