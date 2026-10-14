# CIVICLENS TN — Phase 7.11 Implementation Audit: Auditable Claim Verification & Evidence Explorer

**Audit Date:** 2026-10-14  
**Audit Scope:** Verification architecture, claim decomposition, evidence acquisition & retrieval, relationship analysis, verification engine, human review, REST APIs, and frontend dashboard across Phases 7.1–7.10.  
**Auditor:** CIVICLENS TN Core Intelligence Team  
**Standard:** Phase 7.11 Auditable Verification & Evidence Explorer Specification  

---

## 1. Executive Summary

Phase 7.1 through Phase 7.10 successfully established the foundational data models, multilingual NLP decomposition, hybrid retrieval engine, multi-signal evidence relationship analysis, human-in-the-loop review workflow, and integration with 8 real Tamil Nadu claims alongside 35 statutory Tier 1 documents and 212 news documents.

The objective of **Phase 7.11** is to make every verification outcome auditable, explainable, and traceable from:
$$\text{ORIGINAL POLITICAL CLAIM} \rightarrow \text{ATOMIC CLAIMS} \rightarrow \text{SUPPORTING EVIDENCE} \rightarrow \text{CONTRADICTING EVIDENCE} \rightarrow \text{CONTEXTUAL EVIDENCE} \rightarrow \text{VERIFICATION REASONING} \rightarrow \text{FINAL EVIDENCE ASSESSMENT} \rightarrow \text{ORIGINAL SOURCE DOCUMENTS}$$

This audit assesses the existing implementation against the 10 mandated display capabilities to determine what is already complete and what extensions are required in Phase 7.11.

---

## 2. Assessment of Mandated Display Capabilities

| # | Required Display Capability | Status | Existing Implementation | Gaps to Address in Phase 7.11 |
|---|-----------------------------|:------:|-------------------------|-------------------------------|
| **1** | **The original claim and attribution** | **Complete** | `Claim` model preserves exact verbatim `original_text`, `speaker_name`, `speaker_role`, `speaker_party`, `claim_date`, `claim_source_url`, `candidate_source_type`, and `attribution_type`. Exposed via `/api/claims/<id>` and Section 1 of Claim Detail. | None. Original wording is preserved without rewriting. Unknown fields remain `null`. |
| **2** | **Each atomic claim** | **Partial** | `AtomicClaim` decomposes statements into Subject-Predicate-Object frames, temporal scope, geographic scope, and quantitative constraints (`numeric_value`, `unit`, `denominator`). Stored in database and displayed in UI expanders. | UI currently lacks proposition-specific evidence filtering where selecting an atomic claim isolates only its associated supporting, contradicting, and contextual passages. |
| **3** | **Evidence supporting the claim** | **Partial** | `ClaimEvidenceRelationship` classifies and links supporting passages (`relationship_type == SUPPORTS` or `PARTIALLY_SUPPORTS`). Displayed in Section 3 and Tab 4. | Citation metadata needs full standardization (`evidence_id`, `page_number`, `section_or_table`, `passage_reference`, `relevance_score`, `analysis_method`, `verification_status`). Explicit empty state needed when no supporting evidence exists. |
| **4** | **Evidence contradicting the claim** | **Partial** | `ClaimEvidenceRelationship` classifies `relationship_type == CONTRADICTS` with `contradicting_text_reference`. Prominently displayed without suppression. | Metadata citation fields (`page_number`, `section_or_table`) must be exposed in serialization without inventing missing values. Explicit empty state needed when no contradicting evidence exists. |
| **5** | **Contextual or qualifying evidence** | **Partial** | Handled via `relationship_type == CONTEXTUALIZES` and outdatedness flags. Displayed in Section 5. | Need unified Evidence Comparison section with interactive multi-filtering across relationship type, publisher, publication date, language, source category, and review status. |
| **6** | **The relationship between each evidence item and the claim** | **Partial** | Multi-signal checks for entity, temporal, geographic, quantitative, and proposition alignment. Syndicated copy detection and cluster IDs recorded. | Drill-down inspector needed to allow users to click any evidence passage to view retrieval reason, score, extraction method, limitations, and cross-linked claims. |
| **7** | **The reasoning behind the assessment** | **Partial** | `ClaimVerificationEngine` synthesizes outcome and multi-part proposition breakdown. | Explanation text needs explicit 10-point structured breakdown (Claim, Proposition, Supporting Summary, Contradicting Summary, Context, Evidence Gaps, Source Limitations, Outcome Justification, Uncertainty, Methodology/Version). |
| **8** | **The original source document** | **Partial** | `EvidenceDocument` stores `title`, `publisher`, `source_url`, `file_hash_sha256`, and `access_status`. API provides `/api/claims/evidence/documents/<doc_id>`. | UI needs verified public URLs and local document availability checks without fabricating previews or broken links. |
| **9** | **The methodology and limitations** | **Complete** | Methodology version (`CIVICLENS_VERIFICATION_METHODOLOGY_V1`), model version, source diversity metrics, confidence, uncertainty indicators, and epistemic disclaimers are fully recorded. | None. Strict anti-defamation charter and absence-of-evidence notices are enforced. |
| **10** | **The verification and review history** | **Complete** | `VerificationHistory`, `ReviewRecord`, and `VerificationRun` track automated baselines alongside human reviewer determinations, review actions, and timestamps. | None. Preserved permanently to prevent stealth revisions. |

---

## 3. Classification Summary

- **Complete (3/10):**
  - Capability 1: Original claim and attribution
  - Capability 9: Methodology and limitations
  - Capability 10: Verification and review history
- **Partial (7/10):**
  - Capability 2: Atomic claim decomposition traceability and proposition-specific filtering
  - Capability 3: Supporting evidence panel citation completeness & explicit empty states
  - Capability 4: Contradicting evidence panel citation completeness & explicit empty states
  - Capability 5: Contextual evidence & unified multi-faceted comparison filtering
  - Capability 6: Evidence relationship inspection & drill-down capabilities
  - Capability 7: 10-point structured explainable reasoning
  - Capability 8: Direct source document provenance & local accessibility verification
- **Missing (0/10):** No foundational capability is missing; the infrastructure from Phases 7.1–7.10 covers all necessary entities.
- **Unverifiable (0/10):** All components are empirical and testable.

---

## 4. Implementation Plan for Phase 7.11

1. **Step 2 — Evidence-Centric Data Model Extension:**
   - Extend `ClaimEvidenceRelationship.to_dict()` and `EvidencePassage.to_dict()` in `backend/models/claim.py` to serialize: `evidence_id`, `document_id`, `source_url`, `source_title`, `publisher`, `publication_date`, `retrieval_date`, `language`, `page_number`, `section_or_table`, `passage_reference`, `evidence_relationship`, `relevance_score`, `analysis_method`, and `verification_status`.
   - Preserve `null`/`None` when citation fields are unavailable; strictly never fabricate page numbers or publication dates.

2. **Step 3 & 4 — Claim Decomposition Traceability & Grouped Panels:**
   - In `backend/api/claims.py`, enhance `/api/claims/<claim_id>/relationships` and provide `/api/claims/<claim_id>/evidence-explorer` with grouped breakdowns (`supporting`, `contradicting`, `contextual`, `other`) and proposition-specific mapping.
   - Expose explicit empty-state messaging when any evidence category is empty.
   - Expose syndicated copy annotations (`is_syndicated_copy`, `syndication_cluster_id`) so duplicate wire reports are never counted as independent corroboration.

3. **Step 5 — Explainable Verification Reasoning:**
   - In `backend/services/claim_verification_engine.py`, update `synthesize_claim_outcome` to generate a dedicated 10-point structured reasoning dictionary and formatted markdown:
     1. Claim being evaluated
     2. Specific proposition being checked
     3. Evidence supporting the proposition
     4. Evidence contradicting the proposition
     5. Relevant context and qualifications
     6. Important evidence gaps
     7. Source reliability and limitations relevant to the claim
     8. Reason the selected outcome follows from the available evidence
     9. Remaining uncertainty
     10. Methodology and model version

4. **Step 6 & 7 — Evidence Explorer UI & Drill-Down:**
   - In `frontend/pages/6_Claim_Verification.py` and `frontend/pages/six_claim_verification_test_helper.py`, restructure Tab 2 (Claim Detail) into the 6 designated sections:
     - Section 1: Original Claim (Verbatim wording & provenance)
     - Section 2: Atomic Claims (Proposition selector for proposition-specific evidence isolation)
     - Section 3: Evidence Comparison (Supporting, Contradicting, Contextual with multi-filters)
     - Section 4: Verification Reasoning (10-point structured card)
     - Section 5: Source Documents (Validated source links & file access)
     - Section 6: Verification History (Automated baseline vs. human review)
   - Add Evidence Drill-Down inspector expanders detailing retrieval justification, score, passage context, alignment dimensions, and cross-linked claims.

5. **Testing & Final Validation:**
   - Author `tests/unit/test_phase7_auditable_verification.py` verifying the 10-point structured reasoning schema, complete citation fields, proposition-specific filtering, and non-defamation rules.
   - Execute full regression test suite across all Phase 7 modules.
