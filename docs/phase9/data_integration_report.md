# Phase 9 Data Integration Report

**Project:** CIVICLENS TN  
**Phase:** 9 — Unified Civic Intelligence & Evidence Graph  
**Module:** Phase 9.10 Real Data Integration  
**Date:** 2026-10-13  
**Status:** COMPLETE  

---

## 1. Executive Summary

This report documents the real dataset integration and schema synchronization completed in Phase 9.10 for the **CIVICLENS TN** Unified Civic Intelligence & Evidence Graph. The objective was to integrate authentic cross-phase records spanning Phases 1 through 8 into the unified canonical entity registry and evidence graph architecture without fabricating records or relationships, without deleting or mutating original primary records, and preserving complete evidentiary provenance.

The input data archive was extracted from `dataset9-10/civiclens_phase9_datasets` (sourced from the designated system download directory) into `data/raw/phase9/`. The ingested records have been validated against the relational schema and populated into SQLite database storage (`data/processed/civiclens.db`), establishing a foundational cross-phase intelligence layer for civic analytics in Tamil Nadu.

---

## 2. Ingested Datasets and Schema Inventory

Six primary dataset files were audited, normalized, and integrated:

| Dataset File | Description | Record Count | Schema Model |
| :--- | :--- | :---: | :--- |
| `graph_entities.csv` | Cross-phase entity records across 17 entity types with bilingual naming (Tamil / English), temporal validity, and source provenance | 249 | `CanonicalEntity`, `CivicGraphNode`, `SourceIdentifierMapping` |
| `graph_relationships.csv` | Documentary, hierarchical, and reviewed cross-phase relationships | 497 | `CivicEvidenceEdge` |
| `graph_evidence.csv` | Evidentiary backing records containing source URLs, locators, SHA-256 content hashes, and dialectical roles | 497 | `CivicEvidenceEdge`, `CivicSourceDocument` |
| `graph_source_registry.csv` | Primary source registry linking statutory gazettes, policy papers, budgets, media registries, and election notifications | 95 | `CivicSourceDocument` |
| `entity_resolution_review.csv` | Human-in-the-loop candidate match audit log resolving near-duplicate and homonymous candidate pairs | 20 | `DuplicateCandidateReview` |
| `graph_data_quality_report.csv` | Comprehensive data quality check results, including severity, resolution status, and epistemic guardrails | 25 | `CivicConflictRecord` |

---

## 3. Entity Distribution and Cross-Phase Provenance

The 249 ingested canonical entities span all preceding project phases (Phases 1–8). Every entity retains its original `source_phase` and `source_record_id`, ensuring strict non-destructive traceability.

### 3.1 Entity Distribution by Source Phase

```
Phase 6 (Representatives & Constituencies):  109 entities (43.8%)
Phase 8 (Civic Issues & Public Works):        57 entities (22.9%)
Phase 4 (News Articles & Media Outlets):      51 entities (20.5%)
Phase 2 (Government Schemes & Policies):      11 entities ( 4.4%)
Phase 1 (Budget & Expenditure Records):        6 entities ( 2.4%)
Phase 3 (Promises & Manifestos):               5 entities ( 2.0%)
Phase 5 (Political Funding & Contributions):   5 entities ( 2.0%)
Phase 7 (Claims & Fact Verification):          5 entities ( 2.0%)
------------------------------------------------------------------
Total Ingested Entities:                     249 entities (100.0%)
```

### 3.2 Canonical Entity Classification

The raw entity records map to the normalized canonical schema categories:

| Entity Type | Ingested Count | Canonical Class Mapping | Typical Identifiers |
| :--- | :---: | :--- | :--- |
| `representative` | 69 | `REPRESENTATIVE` | `TN-REP-MLA-001` ... `TN-REP-MLA-069` |
| `political_event` | 31 | `ADMINISTRATIVE_AREA` / `PUBLIC_WORK` | `EVT-TN-2024-001` ... |
| `constituency` | 22 | `CONSTITUENCY` | `TN-AC-001` (Dr. Radhakrishnan Nagar) to `TN-AC-022` |
| `news_article` | 20 | `SOURCE_DOCUMENT` | `ART-TH-2024-001` to `ART-DT-2024-020` |
| `political_party` | 18 | `POLITICAL_PARTY` | `TN-PARTY-DMK`, `TN-PARTY-AIADMK`, `TN-PARTY-INC` |
| `commitment` | 16 | `PUBLIC_CLAIM` / `PUBLIC_WORK` | `CM-EXP-2024-001` ... |
| `civic_issue` | 12 | `CIVIC_ISSUE` | `ISSUE-CHN-001` (Velachery Inundation) ... |
| `public_work` | 12 | `PUBLIC_WORK` | `PW-CHN-SWD-001` ... |
| `department` | 10 | `GOVERNMENT_DEPARTMENT` | `DEPT-MAWS`, `DEPT-HFW`, `DEPT-WRD`, `DEPT-SED` |
| `scheme` | 8 | `SCHEME` | `SCH-TN-KMU` (Kalaignar Magalir Urimai Thittam) ... |
| `administrative_area` | 6 | `ADMINISTRATIVE_AREA` | `ADM-TN-CHN-ZONE-13` (Adyar Zone) ... |
| `budget` | 5 | `SCHEME` / `SOURCE_DOCUMENT` | `BUD-TN-2024-25` (TN Annual Budget 2024-25) |
| `promise` | 5 | `PUBLIC_CLAIM` | `PRM-DMK-2021-001` ... |
| `verified_claim` | 5 | `PUBLIC_CLAIM` | `CLM-TN-2024-001` ... |
| `municipal_statistic` | 5 | `PUBLIC_WORK` / `CIVIC_ISSUE` | `STAT-CHN-SWM-2024` ... |
| `political_funding_disclosure` | 3 | `POLITICAL_PARTY` / `SOURCE_DOCUMENT` | `EB-TN-2024-DMK`, `EB-TN-2024-AIADMK` |
| `contractor` | 2 | `PUBLIC_WORK` | `CTR-TN-INFRA-01`, `CTR-TN-INFRA-02` |

---

## 4. Relationship Discovery and Ingestion Metrics

A total of 497 documentary, hierarchical, and reviewed relationships connect entities across Phases 1–8. All 497 relationships are backed by a corresponding evidence record in `graph_evidence.csv`.

### 4.1 Relationship Breakdown by Type

1. **`GOVERNED_BY_COMMITMENT`** (135 edges): Links public works and operational service delivery to sanctioned policy commitments and scheme guidelines.
2. **`ADDRESSES_OR_RELATES_TO_WORK`** (100 edges): Associates citizen grievances and civic issues with public infrastructure works and municipal remediations without asserting personal representative culpability.
3. **`MEMBER_OF_PARTY`** (61 edges): Formal party affiliation of elected representatives based on official Tamil Nadu Legislative Assembly gazettes.
4. **`PARTICIPATED_IN_EVENT`** (58 edges): Legislative debates, assembly questions, and public inspections documented in official assembly records.
5. **`REPRESENTS_CONSTITUENCY`** (46 edges): Delimitation and gazette records linking MLAs to their respective Assembly Constituencies.
6. **`LOCATED_IN_ADMIN_AREA`** (34 edges): Spatial hierarchy associating constituencies, wards, and works to administrative zones and districts.
7. **`ASSIGNED_TO_DEPARTMENT`** (12 edges): Portfolios assigned to government departments under Tamil Nadu Government Business Rules.
8. **`HEADS_DEPARTMENT`** (9 edges): Ministerial leadership verified against Chief Secretariat gazette notifications.
9. **`JURISDICTION_OVER`** (7 edges): Departmental jurisdiction over designated administrative areas and municipal bodies.
10. **`ADMINISTERS_SCHEME`** (7 edges): Nodal department administering a flagship welfare scheme.
11. **`FUNDS_SCHEME`** (6 edges): Statutory budget demands and finance department allocations funding schemes.
12. **`EXECUTING_DEPARTMENT_FOR`** (5 edges): Executing agencies (e.g., GCC, WRD, TWAD Board) responsible for civil works.
13. **`EVALUATES_ENTITY`** (5 edges): Independent audit, CAG report, or policy evaluation assessing public programs.
14. **`PUBLISHED_BY_BODY`** (5 edges): Official documents, gazettes, and disclosures mapped to publishing authorities.
15. **`MONITORS_PROMISE`** (4 edges): Civic tracking links between election promises and ongoing implementation monitoring (strictly preserving non-fulfillment neutrality).
16. **`DONOR_RECIPIENT_CORRELATION`** (2 edges): Disclosed contributions mapped from Election Commission / SBI electoral trust records without asserting quid pro quo causation.
17. **`AWARDED_TO_CONTRACTOR`** (1 edge): Transparent tender execution disclosure from the Tamil Nadu Public Works Department tender portal.

### 4.2 Matching Methods Employed

The relationships were established strictly through auditable, deterministic criteria:

- **`EXACT_IDENTIFIER_JOIN`**: 257 edges (51.7%) — Primary keys, Election Commission candidate IDs, Assembly Constituency numbers, and scheme codes.
- **`TOPIC_DOMAIN_CO_OCCURRENCE`**: 100 edges (20.1%) — Verified domain alignments between municipal issue categories and civil works classifications.
- **`GAZETTE_OFFICIAL_RECORD`**: 78 edges (15.7%) — Government Orders (GOs), TN Legislative Assembly bulletins, and Tamil Nadu Government Gazettes.
- **`ADMINISTRATIVE_HIERARCHY`**: 53 edges (10.7%) — Revenue district, taluk, ward, and Local Government Directory (LGD) alignments.
- **`PHASE7_CLAIM_EVALUATION`**: 5 edges (1.0%) — Multi-source claim verification linking factual statements to evidence passages.
- **`MANUAL_EDITORIAL_REVIEW`**: 4 edges (0.8%) — Expert editorial review validating complex historical scheme transitions.

---

## 5. Source Registry and Verification Pipeline

The 95 primary source documents registered in `graph_source_registry.csv` were verified for cryptographic integrity and open accessibility:

- **Cryptographic Hashing:** 100% of documents have verified SHA-256 content hashes.
- **URL Verification:** 95/95 sources have validated statutory or open media endpoints (e.g., `assembly.tn.gov.in`, `tn.gov.in`, `budget.tn.gov.in`, `eci.gov.in`, `chennaicorporation.gov.in`).
- **Access Status:** 94 documents are public open-access records; 1 source is marked as a partially digitized paper gazette archive with full physical bibliographic citations preserved.

---

## 6. Entity Resolution and Human-in-the-Loop Reviews

To prevent erroneous conflation of homonymous or near-duplicate public figures and administrative bodies, 20 high-scoring candidate matches were audited in `entity_resolution_review.csv`:

- **Rejected Distinct Entities (14 pairs):** Homonymous politicians with identical names representing distinct assembly constituencies across different electoral cycles (e.g., separate candidates named `K. S. Radhakrishnan` or `M. Shanmugam`).
- **Resolved Distinct Lifecycle Entities (4 pairs):** Schemes that evolved across administrations with name changes (e.g., Amma Unavagam vs. Kalaignar Canteens) preserved as separate historical lifecycle entities linked via `SUPERSEDES` rather than merged.
- **Confirmed Separate (2 pairs):** Distinct government departments sharing common administrative domains (e.g., Municipal Administration and Water Supply Dept vs. Water Resources Dept).

No unverified automatic merges were permitted, maintaining 100% integrity across identity graphs.

---

## 7. Data Quality Audit Findings

A dedicated audit of 25 data quality checks (`graph_data_quality_report.csv`) confirmed:
- Zero unhandled referential integrity breaks across all 497 edges.
- Mitigation and UTF-8 sanitization applied to media titles with mixed byte sequences.
- Explicit non-causality annotations attached to funding correlation edges (`EB-TN-2024-DMK`, `EB-TN-2024-AIADMK`).
- Provisional sanction figures segregated from final audited CAG expenditures with clear audit-lag flags.

---

## 8. Conclusion

Phase 9.10 data integration was executed in accordance with all evidentiary, architectural, and epistemic principles of CIVICLENS TN. The real dataset successfully unifies Phases 1 through 8 into an evidence graph ready for cross-phase queries and public accountability investigations.
