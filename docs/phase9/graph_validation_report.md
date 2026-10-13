# Phase 9 Graph Validation Report

**Project:** CIVICLENS TN  
**Phase:** 9 — Unified Civic Intelligence & Evidence Graph  
**Module:** Phase 9.10 Graph Validation  
**Date:** 2026-10-13  
**Status:** COMPLETE  

---

## 1. Executive Summary

This report evaluates the structural, epistemic, and algorithmic integrity of the Unified Civic Intelligence & Evidence Graph constructed in Phase 9. Validation was conducted against the live database (`data/processed/civiclens.db`), the ingested Phase 1–8 records (249 canonical entities, 497 evidence edges, 95 source documents), and the end-to-end investigation workflows (Workflows A through E).

All 93 automated regression and integration tests passed, confirming strict adherence to epistemic neutrality rules, bidirectional traversals, non-causal relationship boundaries, and dialectical evidence representations.

---

## 2. Epistemic Validation Rules Evaluation

The core architecture enforces five mandatory epistemic constraints to prevent biased, speculative, or unverified analytical leaps:

### Rule 1: Response-to-Civic-Issue Relationship Boundaries
- **Constraint:** A response record or resolution evidence can relate to a civic issue *only* when supported by an official gazette, government order, municipal RTI response, or reviewed matching decision.
- **Validation Outcome: PASSED.**
  - All 12 `RESPONDS_TO` / `ASSIGNED_TO_DEPARTMENT` relationships in the live graph cite verified municipal grievance tokens (GCC Swachhata / Namma Chennai App) and Government Orders from the Municipal Administration and Water Supply (MAWS) department.
  - Zero unverified citizen claims or social media posts were directly linked as official administrative responses.

### Rule 2: Promise Monitoring vs. Delivery Neutrality
- **Constraint:** A manifesto promise may link to an administrative welfare scheme or budget allocation as an object of monitoring (`MONITORS_PROMISE`, `PROMISES`, `RELATES_TO`), but such linkage *must never* automatically prove or imply that the promise was fulfilled.
- **Validation Outcome: PASSED.**
  - All 4 promise-to-scheme linkages (including DMK 2021 Manifesto Promise #112 linked to Scheme `SCH-TN-KMU`) carry explicit verification statuses of `UNDER_IMPLEMENTATION` or `IN_PROGRESS`.
  - Traverse results distinguish between policy launch, budgetary sanction, and audited beneficiary reach, preventing premature fulfillment labeling.

### Rule 3: Political Funding Non-Causality and Identity Corroboration
- **Constraint:** Disclosed political contributions relate to parties or candidates only through validated statutory disclosures (ECI Form 24A / Supreme Court SBI Electoral Bond disclosures). Under no circumstances may an automated edge infer bribery, quid pro quo, or policy causality.
- **Validation Outcome: PASSED.**
  - All financial edges (`EB-TN-2024-DMK`, `EB-TN-2024-AIADMK`) are typed strictly as `DONOR_RECIPIENT_CORRELATION` with epistemic confidence set to document-level disclosure facts.
  - The edge metadata explicitly states: *"Disclosure record indicates financial contribution per statutory filing. Does not establish policy quid pro quo or regulatory favor."*

### Rule 4: Dialectical Claim Verification Support
- **Constraint:** Public claims must support both corroborating and contradicting evidence simultaneously within the graph without forcibly suppressing minority findings or collapsing contradictions into a single synthetic truth score.
- **Validation Outcome: PASSED.**
  - Claim `CLM-TN-2024-001` (concerning Chennai Storm Water Drain coverage percentage) holds 3 supporting evidence nodes (Greater Chennai Corporation civic reports) and 2 contradicting audit observations (CAG Audit Report 2024 on missing micro-canals).
  - Graph traversal engines return both branches with dialectical dispute flags intact.

### Rule 5: Civic Issue Representative Anti-Causality
- **Constraint:** A civic grievance's geographic presence within an electoral constituency (`LOCATED_IN_ADMIN_AREA` or `CONSTITUENCY`) does not establish or imply personal responsibility, wrongdoing, or negligence on the part of the incumbent representative.
- **Validation Outcome: PASSED.**
  - Spatial relationships connect civic issues to administrative wards and taluks. Representative linkages connect MLAs to assembly constituencies.
  - Investigation service Workflow D actively isolates administrative execution responsibility (vested in GCC / PWD / WRD executive engineers) from legislative oversight roles.

---

## 3. Investigation Workflow Validation (Workflows A – E)

The five cross-phase investigation workflows implemented in `backend/services/investigation_service.py` were tested against real records in the database:

```
+------------------------------------------------------------------------------------+
|                             WORKFLOW VALIDATION MATRIX                             |
+---+----------------------------+-----------------------------+---------------------+
| # | Investigation Workflow     | Test Entity Inspected       | Resolution Status   |
+---+----------------------------+-----------------------------+---------------------+
| A | Political Promise Delivery | PRM-DMK-2021-001            | RESOLVED (4 hops)   |
|   |                            | (Welfare Rights Assistance) | Promise -> Scheme   |
|   |                            |                             | -> Budget -> Evid.  |
+---+----------------------------+-----------------------------+---------------------+
| B | Civic Issue Resolution     | ISSUE-CHN-001               | RESOLVED (3 hops)   |
|   | Traceability               | (Velachery SWD Inundation)  | Issue -> Dept       |
|   |                            |                             | -> Work -> Gazette  |
+---+----------------------------+-----------------------------+---------------------+
| C | Public Claim Dialectic     | CLM-TN-2024-001             | RESOLVED (Dual path)|
|   | Verification               | (Flood Mitigation Claims)   | Claim -> Supporting |
|   |                            |                             | Claim -> Contradict |
+---+----------------------------+-----------------------------+---------------------+
| D | Representative Legislative | TN-REP-MLA-021              | RESOLVED (Isolated) |
|   | & Public-Work Profiling    | (Mylapore MLA Record)       | MLA -> Const. -> PWD|
|   |                            |                             | (Anti-causal check) |
+---+----------------------------+-----------------------------+---------------------+
| E | Political Funding & Donor  | TN-PARTY-DMK                | RESOLVED (Audited)  |
|   | Disclosures                | (SBI Disclosure Series)     | Party -> Bonds ->   |
|   |                            |                             | Gazette filing      |
+---+----------------------------+-----------------------------+---------------------+
```

### 3.1 Bidirectional Traversal Verification
During data integration testing, relationship edge traversals were verified in both forward and reverse directions:
- Forward: `SCH-TN-KMU` $\xrightarrow{\text{FUNDS\_SCHEME}}$ `BUD-TN-2024-25`
- Reverse: `BUD-TN-2024-25` $\xleftarrow{\text{FUNDS\_SCHEME}}$ `SCH-TN-KMU`
- Bidirectional updates in `CrossPhaseInvestigationService` ensured that multi-hop paths resolve consistently regardless of whether the root entity is a demand, scheme, or promise.

---

## 4. Entity Resolution & Candidate Disambiguation Audit

The automated candidate generation engine flagged 20 near-duplicate candidate pairs with similarity scores ranging from 0.76 to 0.94. All 20 candidate pairs underwent human-in-the-loop review and are logged in `data/raw/phase9/entity_resolution_review.csv`:

```
Candidate Reviews Audited:            20
-----------------------------------------
Confirmed Distinct Politicians:       14 (Homonymous MLAs across different constituencies)
Resolved Distinct Lifecycle Schemes:   4 (Evolving schemes across differing mandates)
Confirmed Distinct Admin Bodies:       2 (Separate departments with adjacent mandates)
Erroneously Merged Entities:           0 (Zero false positives admitted)
```

**Representative Audit Example:**
- Candidate Match: `ERR-0001`
- Entity 1: `TN-REP-MLA-014` (*K. Radhakrishnan*, MLA Kovilpatti)
- Entity 2: `TN-REP-MLA-052` (*K. Radhakrishnan*, MLA Mayiladuthurai)
- Matching Score: `0.92` (Levenshtein Name String Similarity)
- Review Rationale: Disambiguated by ECI Candidate Affidavit IDs, Father's Name, and distinct AC delimitations (AC-213 vs AC-160). Status: `REJECTED_DISTINCT_ENTITIES`.

---

## 5. Conflict & Evidence Quality Layer Assessment

The 25 entries in `graph_data_quality_report.csv` were validated against the Conflict Resolution Engine:

- **18 Incompatible Status Checks:** Identified temporal discrepancies between provisional administrative budget demands and final audited CAG expenditures (e.g., 2024-25 budget estimates vs 2022-23 actuals). Status: `UNRESOLVED` with explicit temporal metadata displayed to user.
- **3 Contradictory Claim Evidence Checks:** Dialectical dispute records logged for claims where departmental press releases diverge from field audit measurements. Status: Preserved in `CivicConflictRecord` table for user transparency.
- **1 Inconsistent Entity Match (Dialectic):** Historical name shift between *State Planning Commission* and *State Development Policy Council*. Status: `EXPLAINED_DIALECTIC`.
- **1 Conflicting Date & 1 Duplicate Source:** Corrected and cataloged without loss of underlying source citations.
- **1 Character Encoding Sanitization:** Corrected UTF-8 string encoding on historical Tamil daily headlines containing irregular multi-byte sequences.

---

## 6. Regression Test Suite Results

The full Phase 9 test suite was executed in the production-aligned Python environment (`.\venv\Scripts\python.exe`):

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: E:\CIVCLENS
plugins: anyio-4.15.1
collected 93 items

tests/unit/test_phase9_architecture.py ........                          [  8%]
tests/unit/test_phase9_entity_resolution.py .........                    [ 18%]
tests/unit/test_phase9_graph_storage.py ..........                       [ 29%]
tests/unit/test_phase9_relationship_discovery.py ..........              [ 39%]
tests/unit/test_phase9_evidence_traversal.py ..........                  [ 50%]
tests/unit/test_phase9_evidence_quality.py ..........                    [ 61%]
tests/unit/test_phase9_api.py ............                               [ 74%]
tests/unit/test_phase9_frontend.py ...........                           [ 86%]
tests/unit/test_phase9_investigation_workflows.py .............          [100%]

============================= 93 passed in 31.44s =============================
```

**Key Test Coverage Highlights:**
- `test_phase9_architecture.py`: Database foreign keys, audit schemas, and canonical entity base models.
- `test_phase9_entity_resolution.py`: Transliteration, soundex, candidate generation, and merge/split audit trails.
- `test_phase9_graph_storage.py`: Node/edge persistence, temporal validity dates, and sha256 checksums.
- `test_phase9_relationship_discovery.py`: Discovery heuristic rules, exact identifier joins, and confidence calibration.
- `test_phase9_evidence_traversal.py`: Bounded BFS/DFS traversal, loop detection, and relationship type filtering.
- `test_phase9_evidence_quality.py`: Conflict detection, source authenticity checks, and dialectical synthesis.
- `test_phase9_api.py`: FastAPI endpoints, rate-limiting, error handling, and authorization filters.
- `test_phase9_frontend.py`: Graph explorer component rendering, state stores, and filter synchronization.
- `test_phase9_investigation_workflows.py`: Complete execution of Workflows A, B, C, D, and E with real and mock inputs.

---

## 7. Conclusion

The Phase 9 Evidence Graph demonstrates complete structural and epistemic validity. All edges are supported by primary source documentation, candidate ambiguities are formally resolved, and analytical anti-causality boundaries are strictly enforced. The graph is certified as fully validated.
