# CIVICLENS TN — Phase 11.5: Plain-Language Record Pages Report

**Date:** 2026-10-19  
**Milestone:** Phase 11.5 Implementation  
**Status:** Completed  
**Commit Target:** `feat(ui): simplify civic record detail pages`

---

## 1. Executive Summary

Phase 11.5 transforms CIVICLENS TN individual record detail pages from dense technical or political research outputs into clear, accessible, plain-language civic dossiers. The platform balances high public accessibility for ordinary citizens with rigorous epistemic discipline, preserving primary source provenance, audit trails, and data caveats without overwhelming non-specialist users.

All detail pages share a unified, responsive information architecture implemented via `RecordDetailLayout.tsx` across six core civic record types:
1. **Government Schemes & Budgets** (`/schemes/[id]`)
2. **Manifesto Promises** (`/promises/[id]`)
3. **Elected Representatives / MLAs** (`/representatives/[id]`)
4. **Public Claims & Fact-Checks** (`/claims/[id]`)
5. **Civic Grievances & Municipal SLA Issues** (`/civic/[id]`)
6. **Policy Outcome Evaluations** (`/policy-evaluation/[id]`)

---

## 2. Shared Record Architecture & 5-Step Information Hierarchy

Every detail page adheres to a consistent 5-step citizen-first information hierarchy designed to avoid technical jargon up front while keeping complete analytical data accessible:

```
+-------------------------------------------------------------------------+
| STEP 1: What Is This Record About?                                      |
| - Plain English title + Tamil vernacular name                          |
| - High-level summary (what this policy or claim does in simple terms)   |
| - Primary status badge with human-readable explanation card             |
+-------------------------------------------------------------------------+
| STEP 2: Key Facts at a Glance                                           |
| - Responsible Ministry / Department / Body                              |
| - Target Beneficiaries & Eligibility                                    |
| - Geographic Scope (Statewide / District / Assembly Constituency)       |
| - Active Reporting Period / Financial Year                              |
+-------------------------------------------------------------------------+
| STEP 3: Documented Evidence & Financial Disclosures                     |
| - Budget Estimate (BE) vs. Revised Estimate (RE) vs. Actuals (AE)      |
| - Transparent utilization rates computed only with valid denominators   |
| - Proposition breakdown (Claims) / SLA resolution metrics (Civic)       |
| - MLACDS performance indicators without causal over-attribution (MLAs) |
+-------------------------------------------------------------------------+
| STEP 4: Primary Sources & Verifiable Evidence                           |
| - Issuing department, document date, provenance tier (Govt/Audit/Press) |
| - Direct links to primary PDFs or clear offline archive notices         |
+-------------------------------------------------------------------------+
| STEP 5: Progressive Disclosure & Connected Knowledge                    |
| - Accordions: "How was this assessed?", "Technical identifiers",        |
|   and "Epistemic limitations & caveats"                                 |
| - Connected related records with explicit causal/thematic relationships |
+-------------------------------------------------------------------------+
```

---

## 3. Epistemic Data Limitations & Epistemic Safeguards

To prevent misinformation and uphold civic neutrality, Phase 11.5 establishes strict data integrity principles across all record views:

1. **Budget Estimation Distinctions (BE vs. RE vs. AE):**
   - **Budget Estimate (BE):** Planned legislative appropriation announced at budget presentation.
   - **Revised Estimate (RE):** Mid-year recalibration based on actual revenue inflows and expenditure trends.
   - **Actual Expenditure (AE):** Certified final disbursement from Comptroller & Auditor General (CAG) audit accounts.
   - *Rule:* Missing estimates or expenditures are never defaulted or coerced to zero. Utilization rates (\(\frac{\text{AE}}{\text{RE}}\) or \(\frac{\text{AE}}{\text{BE}}\)) are computed only when the denominator is strictly positive and confirmed by official documentation.

2. **Non-Causal Attribution Discipline for Elected Representatives (MLAs):**
   - General constituency development outcomes (e.g. state highway construction, major industrial investments, district poverty reduction) are led by executive line departments and are **not** causally attributed to the local MLA without documented legislative sponsorship, zero-hour interventions, or documented assembly questions.
   - MLA scorecards strictly report verified inputs: Assembly attendance %, questions tabled, private member interventions, and MLACDS (MLA Constituency Development Scheme) expenditure audited by the District Collectorate.

3. **Citizen Privacy & PII Protection in Civic Grievances:**
   - Citizen phone numbers, email addresses, and specific residential door numbers are masked and redacted from municipal grievance records (`CIV-...`), exposing only ward numbers, zone designations, and department resolution timestamps.

4. **Atomic Proposition Breakdown for Fact-Checks:**
   - Public claims are decomposed into atomic testable statements (e.g., historical precedent vs. expenditure magnitude vs. program continuation), each evaluated against certified government orders or official gazettes rather than broad generalized labels.

---

## 4. Components & Pages Changed

| Component / Route | Changes Implemented |
|---|---|
| `frontend/src/lib/types.ts` | Added `SourceDocument`, `RelatedRecord`, `DetailedFinancials`, and `DetailedCivicRecord` interfaces supporting the 5-step hierarchy, financial distinctions, atomic propositions, civic SLA metrics, representative metrics, and progressive disclosure hooks. |
| `frontend/src/lib/api.ts` | Added `fetchSchemeDetail()`, `fetchPromiseDetail()`, `fetchRepresentativeDetail()`, `fetchClaimDetail()`, `fetchCivicIssueDetail()`, and `fetchPolicyEvaluationDetail()` with live backend endpoint fallback to canonical seeds. |
| `frontend/src/components/RecordDetailLayout.tsx` | Universal plain-language layout implementing the 5-step hierarchy, key facts, financial disclosures, evidence tables, progressive disclosure accordions, and related records with responsive loading, 404, and error states. |
| `frontend/src/app/schemes/[id]/page.tsx` | Dynamic route for government schemes with budget breakdowns, target demographic cards, and policy guidelines. |
| `frontend/src/app/promises/[id]/page.tsx` | Dynamic route for manifesto promises with delivery timelines, verifying government evidence, and implementation status. |
| `frontend/src/app/representatives/[id]/page.tsx` | Dynamic route for MLA profiles with assembly attendance, questions asked, MLACDS funds utilization, and attribution caveats. |
| `frontend/src/app/claims/[id]/page.tsx` | Dynamic route for public claims and fact-checking dossiers with atomic proposition verification and source tiers. |
| `frontend/src/app/civic/[id]/page.tsx` | Dynamic route for civic grievances with SLA resolution metrics, department response timeline, and citizen privacy redaction. |
| `frontend/src/app/policy-evaluation/[id]/page.tsx` | Dynamic route for policy outcome evaluations with synthetic counterfactual assessments, outcome indicators, and methodological notes. |
| Directory Pages (`frontend/src/app/*/page.tsx`) | Added direct navigation links ("View Record", "Open Citizen Record", "View MLA Scorecard", etc.) connecting search & directory lists to dynamic detail routes. |
| `backend/services/unified_search_service.py` | Updated canonical and database search routes to point directly to the new plain-language detail routes (`/schemes/{id}`, `/promises/{id}`, etc.). |

---

## 5. Verification & Test Outcomes

1. **Backend Unified Search Integration Tests (`tests/api/test_unified_search_api.py`):**
   - `test_unified_search_empty_query`: **PASSED**
   - `test_unified_search_single_char_query`: **PASSED**
   - `test_unified_search_valid_query`: **PASSED**
   - `test_unified_search_category_filter`: **PASSED**
   - `test_unified_search_invalid_category_fallback`: **PASSED**
   - `test_unified_search_pagination`: **PASSED**
   - `test_unified_search_categories_endpoint`: **PASSED**
   - *Outcome:* **7/7 passed in 4.44s** in standard sandbox mode.

2. **Frontend Dynamic Detail Routing & Type Safety:**
   - Dynamic parameter routes verified across all six record families.
   - Graceful recovery states verified for invalid or non-existent record identifiers (404 Not Found card with return-to-directory actions).
   - Keyboard accessible accordions (`aria-expanded`) and contrast-compliant badges.

---

## 6. Unresolved Items & Phase 11.6 Readiness

- **Ready for Phase 11.6:** Unified styling tokens, accessibility checks (WCAG 2.1 AA screen reader audit), and localization (full Tamil language text strings).
- **No breaking changes:** All Phase 1–11.4 endpoints, database models, and directory listings remain fully preserved and operational.
