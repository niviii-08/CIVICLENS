# CIVICLENS TN — Phase 11.7: Simple Filters and Understandable Results

## 1. Executive Summary

Phase 11.7 simplifies filters, listing layouts, statistical displays, and status terminology throughout CIVICLENS TN without altering underlying data or epistemic assessment logic. Ordinary citizens can now discover and explore public information using familiar terminology (e.g. *Department*, *District*, *Sector*, *Delivery Status*) while advanced extraction metadata and database identifiers are de-emphasized.

---

## 2. Audit of Existing Filters Across Modules

| Module / Page | Previous Filter Deficiencies | Phase 11.7 Simplification |
| :--- | :--- | :--- |
| **Government Schemes** (`/schemes`) | Only raw beneficiary group buttons. Missing department and status filters. No "Clear filters" button or active filter chips. Exposed raw internal IDs (`#SCH-SW-KMUT`) before title. | Replaced with `SimpleFilterBar`. Added Department and Status filters with progressive disclosure. De-emphasized IDs in favor of vernacular title, citizen benefit box, and direct "View Details" action. |
| **Manifesto Promises** (`/promises`) | Fragmented party pills and disjoint dropdowns. Missing active filter pills and URL state persistence. Stalled / Broken statuses lacked explanatory plain mapping. | Unified under `SimpleFilterBar` with Party, Status, and Sector. Preserves query parameters in URL (`?party=...&status=...&category=...`). Standardized status labels with tooltips explaining administrative vs field status. |
| **Claims & Fact-Checks** (`/claims`) | Unexplained verdict jargon (`"Verified True"` vs `"Partially True"` vs `"Misleading"`). No claimant filtering or URL sync. | Added filter by Speaker/Claimant and plain-language verdict mappings: *Evidence verified*, *Partially supported*, *Conflicting information*, and *Contradicted by evidence*. |
| **Civic Grievances** (`/civic`) | **Zero filters available.** Table exposed raw database ticket IDs (`CIV-2024-0891`) as primary title. No search or district filtering. | Added full `SimpleFilterBar` supporting District, Line Department, and SLA Resolution Status (`Resolved within SLA` vs `SLA Breached`). Presented readable cards with citizen privacy redactions preserved. |
| **MLAs & Representatives** (`/representatives`) | Only simple name search. No Party filter, no Attendance or MLACDS Fund filters. | Added Party and Assembly Attendance filters (`≥80% High`, `60-79% Moderate`, `<60%`). Added clear fund execution bar (`₹ spent / ₹ allocated`). |
| **Budget & Spending** (`/budget`) | Only Department select. Average utilization calculated without checking if RE denominator is valid. Missing audit actuals could be confused with zero spending. | Added Fiscal Utilization Band filter. Explicit currency (`₹... Cr`) and reporting period (`FY 2023-24`). Guarded percentage calculations against zero denominators. Replaced missing actuals with `"Pending CAG audit"`. |
| **Policy Evaluations** (`/policy-evaluation`) | **Zero filters available.** Users could not filter by target sector or launch year. | Added Target Sector and Launch Year filters with progressive disclosure. Clear distinction between BE, RE, and AE. Non-causal epistemic disclaimers highlighted. |

---

## 3. Simplified Filter Component (`SimpleFilterBar.tsx`)

A standardized, accessible filter component ([`frontend/src/components/SimpleFilterBar.tsx`](file:///c:/Users/Neevetha%20N/Documents/CIVCLENS-All%20features/CIVCLENS-All%20features/CIVCLENS/frontend/src/components/SimpleFilterBar.tsx)) was created:

1. **Familiar Citizen Labels**:
   - `Department`, `District`, `Target Group`, `Sector`, `Status`, `Delivery Status`, `Assembly Attendance`.
2. **Progressive Disclosure ("More filters")**:
   - Primary filters remain visible immediately; secondary or advanced filters are collapsed behind a toggled "More filters" button with active count indicator.
3. **Active Filter Chips & Clear Action**:
   - Every active filter produces an interactive pill with a removal icon `(x)`.
   - A one-click `"Clear filters"` button resets all search and filter parameters.
4. **URL State Synchronization**:
   - Filter state is synchronized with `window.history.replaceState` (`?q=...&dept=...&status=...`), allowing citizens to bookmark and share filtered views without page reload.
5. **Dynamic Count Feedback**:
   - Displays real-time counts: `"Showing 4 of 6 welfare schemes"`.

---

## 4. Standardized Status Labels (`StatusBadge.tsx`)

The status badge component ([`frontend/src/components/StatusBadge.tsx`](file:///c:/Users/Neevetha%20N/Documents/CIVCLENS-All%20features/CIVCLENS-All%20features/CIVCLENS/frontend/src/components/StatusBadge.tsx)) was updated to map technical statuses into citizen-friendly language:

| Raw Technical Status | Standardized Plain-Language Display | Epistemic Display Meaning |
| :--- | :--- | :--- |
| `Verified True` | **Evidence verified** | Statutory orders, gazettes, and CAG audits confirm factual validity. |
| `Fulfilled` / `Resolved` / `Implemented` | **Reported complete** | Official departmental records declare the action completed. |
| `In-Progress` / `Ongoing` | **In progress** | Active field delivery is underway across departments. |
| `Partially True` / `Misleading` / `Conflict` | **Conflicting information** | Records reflect partial delivery or conflicting audit variances. |
| `Broken` / `False` / `SLA Breached` | **Contradicted by evidence** | Documented evidence contradicts stated deadlines or claims. |
| `Stalled` / `Delayed` / `Escalated` | **Delayed / Under review** | Implementation delayed pending administrative clearance or funds. |
| `Unsubstantiated` / `Review` / `Pending` | **Not enough information** | Available evidence is insufficient to make a definitive determination. |

> [!NOTE]
> The term **"Evidence verified"** is strictly reserved for records supported by verified statutory documents or CAG audits. Technical status values are preserved in mouse-over tooltips and technical detail views.

---

## 5. Financial & Statistical Display Enhancements

1. **Explicit Currency and Timing**:
   - All budget amounts explicitly state currency (`₹... Cr` or `₹... Lakh`).
   - Every financial summary indicates the reporting period (`FY 2023-24`).
2. **BE vs RE vs AE Clarity**:
   - *Budget Estimate (BE)*: Initial planned allocation.
   - *Revised Estimate (RE)*: Mid-year supplementary appropriation.
   - *Actual Expenditure (AE)*: Audited tax disbursements.
3. **Missing Value Integrity**:
   - Missing actual disbursements are labeled `"Pending CAG audit"` or `"Not published"` instead of displaying misleading `₹0 Cr`.
4. **Denominator Guardrails**:
   - Utilization percentages are calculated only when `Revised Estimate > 0`, avoiding `NaN` or infinite values.
5. **Non-Causal Principles**:
   - Legislative and policy cards state clearly that individual attendance or fund execution does not imply sole causation of macro-level welfare outcomes.

---

## 6. Verification & Test Results

1. **TypeScript Verification**:
   - `npx tsc -p frontend --noEmit`: Clean compilation across all 7 updated listing and detail pages with **0 errors**.
2. **Backend API Suite**:
   - `pytest tests/api/ -v`: **All 55 tests passed** across all modules.
3. **URL State & Interactive Behavior**:
   - Validated search query clearing, filter group changes, multi-select criteria, and URL search parameter updating.
