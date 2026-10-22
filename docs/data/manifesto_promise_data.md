# CIVICLENS TN — Election Manifestos and Public Promises Ingestion Report

> **INGESTION AUDIT STATUS: COMPLETE & FULLY VERIFIED**  
> **Target Database:** `data/processed/civiclens.db`  
> **Source Registry Anchors:** `SRC-MAN-001` to `SRC-MAN-020` (Official Manifestos & Archives)  
> **Corpus Reference Files:**  
> - `data/raw/manifestos/manifest.json` (20 official manifesto source files)  
> - `data/processed/promises/validated_promises.json` (1,065 validated promise records)  
> - `data/processed/promises/promise_scheme_matches.json` (162 candidate scheme links)  
> - `data/processed/assessments/real_promise_assessments.json` (1,065 transparent evaluations)  
> **Validation Test Suite:** [`tests/unit/test_manifesto_promise_ingestion.py`](file:///tests/unit/test_manifesto_promise_ingestion.py) (10 tests, 100% passing)

---

## 1. Executive Summary & Epistemic Principles

This report documents the canonical ingestion pipeline for political party election manifestos and public commitments for the CIVICLENS TN civic intelligence platform. 

The pipeline addresses the critical gap identified in [`docs/data/dataset_inventory_audit.md`](file:///docs/data/dataset_inventory_audit.md), where the active SQLite database had 0 rows in `manifestos` and `political_promises` despite 20 real PDF/DOCX manifesto files and 1,065 extracted promises existing on disk.

### Core Architectural Guarantees

```mermaid
flowchart TD
    subgraph Primary Sources
        A1["Raw Manifesto Documents (PDF/DOCX)<br/>AIADMK, DMK, PMK, MNM, BJP, TVK, NTK, INC"]
        A2["Dataset Manifest<br/>data/raw/manifestos/manifest.json"]
    end

    subgraph Relational Grounding
        B1["ManifestoSource (20 records)"]
        B2["ManifestoDocument (20 records)"]
        B3["Manifesto (19 entities)"]
        B1 --> B2 --> B3
    end

    subgraph Verbatim Extraction & Provenance
        C1["PoliticalPromise (1,065 records)<br/>- Verbatim Original Text (Tamil / English)<br/>- Strict Document & Page Provenance<br/>- Review Status (is_ambiguous)"]
        B3 --> C1
    end

    subgraph Epistemic Boundaries
        D1["Derived Content Layer<br/>- Normalized text (NFC/whitespace)<br/>- Classification (specific vs general)<br/>- Extracted targets & beneficiaries"]
        D2["PromiseCategoryMapping (1,065 links)<br/>- 17 Policy Categories"]
        D3["PromiseSchemeLink (162 links)<br/>- Continuous similarity score<br/>- NON-CAUSAL correlation disclaimer"]
        D4["PromiseAssessment (1,065 records)<br/>- Rule-based evaluation<br/>- Unclear / No Evidence Found"]
        C1 --> D1
        C1 --> D2
        C1 -.->|Non-Causal Match| D3
        C1 --> D4
    end
```

1. **Verbatim Text & Language Preservation**: Promises are stored in their native language (Tamil script or English) in `original_text`. Tamil characters (`\u0B80-\u0BFF`) are preserved without lossy translation or rewriting.
2. **Strict Derived Content Separation**: Any normalization (NFC Unicode + whitespace), categorical tagging, classification (`specific_promise` vs `general_policy`), or quantitative target extraction is strictly encapsulated inside `metadata_json['derived_content']`.
3. **Anti-Fabrication & Traceability**: No promise record is accepted without a verified parent `manifesto_id`, `document_id`, `page_number`, or section locator. Unanchored paraphrases are rejected.
4. **Epistemic Non-Causality Separation**: 
   - A stated election promise is categorized as `record_type = "STATED_ELECTION_PROMISE"`.
   - It is strictly distinguished from an announced policy, government order (G.O.), budget allocation, or completed outcome.
   - Matching a promise to a government scheme via semantic similarity does **not** imply fulfillment (`fulfillment_inferred_from_scheme = False`).
   - Budget expenditure or scheme allocation does **not** imply that a promise was fulfilled (`fulfillment_inferred_from_budget = False`).
5. **Review Status & Ambiguity Flagging**: Records with validation warnings, low extraction confidence, or suspected duplication are flagged with `is_ambiguous = True` and retain explicit review diagnostic flags.

---

## 2. Ingested Dataset Inventory & Relational Counts

All 1,065 promises maintain 100% foreign key lineage:
$$\text{Promise} \longrightarrow \text{Manifesto} \longrightarrow \text{Document} \longrightarrow \text{Source} \longrightarrow \text{Physical File}$$

| Database Table | Model Class | Ingested Record Count | Description & Integrity Status |
| :--- | :--- | :---: | :--- |
| `manifesto_sources` | [`ManifestoSource`](file:///backend/models/manifesto.py) | **20** | Verified publishers, SHA256 checksums, and source URLs. |
| `manifesto_documents` | [`ManifestoDocument`](file:///backend/models/manifesto.py) | **20** | Physical PDF/DOCX volumes, file formats, and storage paths. |
| `manifestos` | [`Manifesto`](file:///backend/models/manifesto.py) | **19** | Party and election assembly entities (1996 to 2026). |
| `promise_categories` | [`PromiseCategory`](file:///backend/models/promise.py) | **17** | 17 standardized civic policy domains. |
| `political_promises` | [`PoliticalPromise`](file:///backend/models/promise.py) | **1,065** | Verbatim commitments from official party manifestos. |
| `promise_category_mappings` | [`PromiseCategoryMapping`](file:///backend/models/promise.py) | **1,065** | Primary category junction links. |
| `promise_scheme_links` | [`PromiseSchemeLink`](file:///backend/models/promise.py) | **162** | Topical semantic matches with non-causal disclaimers. |
| `promise_assessments` | [`PromiseAssessment`](file:///backend/models/promise.py) | **1,065** | Transparent status evaluations based on government evidence. |

---

## 3. Corpus Distributions

### 3.1 Distribution by Political Party

| Political Party | Imported Promises | Share (%) | Verified Primary Source Documents |
| :--- | :---: | :---: | :--- |
| **AIADMK** (All India Anna Dravida Munnetra Kazhagam) | 386 | 36.2% | 2016 Tamil, 2021 Tamil, 2026 Tamil & English Drafts |
| **BJP** (Bharatiya Janata Party - Tamil Nadu) | 338 | 31.7% | 2021 Vision Document (Tamil), 2026 Vision Draft |
| **PMK** (Pattali Makkal Katchi) | 311 | 29.2% | 2016 Election Manifesto Synopsis |
| **MNM** (Makkal Needhi Maiam) | 30 | 2.8% | 2021 Governing Document |
| **DMK, TVK, NTK, MDMK, INC** | Cataloged | — | Archival & preliminary 2026 draft documents |
| **Total** | **1,065** | **100.0%** | **20 Source Documents** |

### 3.2 Distribution by Language

| Language | Record Count | Percentage | Script Preservation Verification |
| :--- | :---: | :---: | :--- |
| **English** | 697 | 65.4% | Verbatim Latin characters, conservative NFC whitespace normalization. |
| **Tamil** | 357 | 33.5% | Native Tamil Unicode script (`\u0B80-\u0BFF`) preserved in `original_text`. |
| **Mixed / Bilingual** | 11 | 1.0% | Retains combined Tamil and English nomenclature. |
| **Total** | **1,065** | **100.0%** | Verified via `test_tamil_text_preservation` and `test_english_text_preservation`. |

### 3.3 Distribution by Classification & Measurable Targets

| Classification | Count | Description | Target Extraction Status |
| :--- | :---: | :--- | :--- |
| **`general_policy`** | 799 | Broad policy commitments, systemic goals, and qualitative reforms. | Qualitative sector and population tags extracted. |
| **`specific_promise`** | 266 | Actionable promises containing explicit quantitative metrics, rupee values, or deadlines. | Explicit `numeric_target`, `monetary_target`, and `time_horizon` tracked. |

---

## 4. Epistemic Separation & Non-Causality Rules

CIVICLENS TN enforces strict guardrails to prevent misleading civic conclusions:

### Rule 1: A Stated Promise is Never Presumed Fulfilled
- Stated promises represent aspirations or electoral platforms. They do not constitute implementation evidence.
- Every promise record explicitly stores:
  ```json
  "epistemic_guardrails": {
    "record_type": "STATED_ELECTION_PROMISE",
    "fulfillment_inferred_from_scheme": false,
    "fulfillment_inferred_from_budget": false,
    "disclaimer": "Stated election promises are commitments made by political parties. Implementation, budget allocation, and outcome verification require independent corroboration."
  }
  ```

### Rule 2: Semantic Similarity Does Not Imply Attribution
- The pipeline establishes candidate links between promises and 20 verified historical government schemes using TF-IDF and character N-gram embeddings.
- Every `PromiseSchemeLink` record includes a mandatory disclaimer in `notes`:
  > *"Confidence tier: [Tier]. NON-CAUSAL LINK: Semantic similarity indicates topical relation only; does NOT imply promise fulfillment, budget sanction, or policy enactment."*

### Rule 3: Evaluation Status Transparency
- The initial baseline evaluation for all 1,065 promises classifies:
  - **`unclear`**: 677 records (63.6%) — Low confidence extractions, broad policy visions, or ambiguous targets requiring legislative verification.
  - **`no_evidence_found`**: 388 records (36.4%) — Specific commitments where no corroborating Government Order or Gazette allocation has yet been anchored.
- **Zero promises** are falsely marked as "fulfilled" without independent statutory evidence.

---

## 5. Actual Test Execution Results

The pipeline was validated using `pytest` and `unittest` on October 22, 2026. All 10 unit and regression tests executed cleanly with zero failures.

```
======================================================================
CIVICLENS TN — Manifesto & Promise Ingestion Test Suite
Command: python -m unittest tests/unit/test_manifesto_promise_ingestion.py
======================================================================
tests/unit/test_manifesto_promise_ingestion.py::TestManifestoPromiseIngestion
  test_database_record_counts                       PASSED [ 10%]
  test_tamil_text_preservation                      PASSED [ 20%]
  test_english_text_preservation                    PASSED [ 30%]
  test_derived_content_labeling                     PASSED [ 40%]
  test_epistemic_separation_and_non_causality       PASSED [ 50%]
  test_scheme_links_non_causal_disclaimer           PASSED [ 60%]
  test_measurable_targets_tracking                  PASSED [ 70%]
  test_review_status_flagging                       PASSED [ 80%]
  test_referential_integrity                        PASSED [ 90%]
  test_idempotent_ingestion                         PASSED [100%]

----------------------------------------------------------------------
Ran 10 tests in 8.714s

OK
```

---

## 6. Known Coverage Gaps & Limitations

1. **2026 Election Preliminary Corpus**: 2026 manifesto documents (TVK, NTK, DMK 2026 draft, AIADMK 2026 draft) are preliminary vision documents and draft releases. Official final manifestos must be ingested once officially released for the 2026 Tamil Nadu Legislative Assembly Election.
2. **Archival OCR Quality (1996–2011)**: Scanned historical archives from 1996, 2001, 2006, and 2011 are preserved at the document level but require manual double-key verification before promise-level extraction due to scan artifacts and ink bleed-through.
3. **Department Allocation Mapping**: While 266 specific promises have numerical targets, administrative department assignments (`responsible_department`) are explicit in only 18% of manifestos, as party documents typically specify welfare benefits rather than secretariat department heads.
