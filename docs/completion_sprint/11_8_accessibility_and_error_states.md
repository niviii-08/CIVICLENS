# CIVICLENS TN — Phase 11.8: Accessibility, Error Handling and Empty States

## 1. Executive Summary

Phase 11.8 enhances the reliability, resilience, and WCAG 2.2 AA accessibility of CIVICLENS TN across all primary citizen workflows without altering existing business logic, evidence chains, or backend data models. 

Prior to this phase, network errors could occasionally be misinterpreted by citizens as "no records found", keyboard navigation lacked visible focus rings on interactive elements, non-semantic `div` tags were used for interactive controls, and empty states lacked guidance. Phase 11.8 standardizes **9 distinct civic states** through a unified, accessible component (`CivicStateNotice.tsx`), ensures visible keyboard focus indicators across all navigation and search elements, enforces rigorous path/credential sanitization on technical diagnostics, and adds debounced retry actions that preserve the user's active filter state.

---

## 2. Primary Workflow Accessibility & Semantic Audit

An audit across all primary citizen workflows identified accessibility and interaction barriers, which were resolved as follows:

| Workflow / Component | Prior Barrier / Deficiency | Phase 11.8 Resolution | WCAG 2.2 AA Criterion |
| :--- | :--- | :--- | :--- |
| **Global Navigation** ([`Navbar.tsx`](file:///frontend/src/components/Navbar.tsx), [`Header.tsx`](file:///frontend/src/components/Header.tsx)) | Mobile navigation toggles and dropdown triggers used non-semantic `div onClick` handlers without keyboard focusability, `tabIndex`, or accessible labels. | Replaced with semantic `<button type="button">`, explicit `aria-label="Toggle navigation menu"`, and high-contrast focus rings (`focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none`). | **2.1.1 Keyboard**, **4.1.2 Name, Role, Value** |
| **Unified Search** ([`UnifiedSearch.tsx`](file:///frontend/src/components/UnifiedSearch.tsx)) | Backend 500 errors or network failures rendered a generic "No matching records found" message, misleading citizens into believing no government records existed. Search result links had generic text. | Integrated `CivicStateNotice` with distinct `failed_api_request` alert (`role="alert"`, `aria-live="assertive"`) and debounced retry button. Every result item includes an explicit `aria-label="View public record: [Title] in [Domain]"`. | **3.3.1 Error Identification**, **4.1.3 Status Messages** |
| **Domain Listings** (`/schemes`, `/promises`, `/claims`, `/civic`, `/representatives`, `/budget`, `/policy-evaluation`) | Inconsistent loading spinners without screen-reader announcements; blank or cryptic empty screens when filters yielded zero matches; missing keyboard-accessible reset actions. | Standardized on `CivicStateNotice`: polite `loading` state (`role="status"`, `aria-live="polite"`), plain-language `no_matching_results` with direct "Clear all filters" CTA, and preservation of user search terms. | **1.3.1 Info and Relationships**, **3.3.2 Labels or Instructions** |
| **Record Detail Pages** ([`RecordDetailLayout.tsx`](file:///frontend/src/components/RecordDetailLayout.tsx)) | API connection failures showed raw error messages or crashed silently. Technical backtraces and Windows/Linux file paths were exposed. | Replaced with `CivicStateNotice` supporting automatic sanitization of paths (`C:\...`, `/var/...`), an active retry trigger, and clean fallback to previous catalog view. | **3.3.3 Error Suggestion**, **1.4.3 Contrast (Minimum)** |
| **Evidence Panel** ([`EvidencePanel.tsx`](file:///frontend/src/components/EvidencePanel.tsx)) | Collapsible accordions lacked `aria-expanded` attributes; missing focus indicators on document link cards. | Added `aria-expanded` to citation accordions, visible focus rings to source verification buttons, and descriptive aria-labels for primary statutory source links. | **4.1.2 Name, Role, Value**, **2.4.7 Focus Visible** |
| **Home Page** ([`page.tsx`](file:///frontend/src/app/page.tsx)) | Recent record links relied purely on colored badges for domain identification; links lacked unique accessible labels. | Added explicit `aria-label="View public record details for [Title]"` to all card links, ensuring screen-reader users understand destination context without relying on visual badges. | **2.4.4 Link Purpose (In Context)**, **1.4.1 Use of Color** |

---

## 3. The 9 Standardized Civic States (`CivicStateNotice.tsx`)

A single, reusable state notice component ([`frontend/src/components/CivicStateNotice.tsx`](file:///frontend/src/components/CivicStateNotice.tsx)) was built to standardize all empty, waiting, and error conditions across CIVICLENS TN:

| State Code | Purpose & Civic Context | Screen Reader Announcement | User Action / Recovery |
| :--- | :--- | :--- | :--- |
| **`loading`** | Asynchronous data fetching from departmental databases or indexers. | `role="status"`<br>`aria-live="polite"` | Displays animated pulse indicator and polite progress announcement without blocking interaction. |
| **`no_matching_results`** | Active search query or filter combination matched 0 published records. | `role="status"`<br>`aria-live="polite"` | Displays active filter suggestions and provides a `"Clear all filters"` button. |
| **`no_records_available`** | A valid category or district genuinely has no published official records yet. | `role="status"` | Informs citizen that records are pending publication by the nodal department. |
| **`incomplete_record`** | Record exists but official gazette notifications or audit disclosures are incomplete. | `role="status"` | Explains that certain fields await administrative disclosure without implying a software defect. |
| **`missing_source_document`** | Statutory document or gazette notification is temporarily unavailable or archived offline. | `role="status"` | Explains offline archival status and provides guidance on inspecting physical gazettes or filing an RTI. |
| **`conflicting_evidence`** | Multiple official sources (e.g. departmental release vs CAG audit) present conflicting figures. | `role="status"` | Presents non-judgmental guidance explaining that conflicting public records are under epistemic review. |
| **`insufficient_evidence`** | Statement or claim cannot be verified due to lack of primary statutory documentation. | `role="status"` | Outlines evidentiary standards and why CIVICLENS cannot render an unverified determination. |
| **`failed_api_request`** | Network failure, server timeout, or HTTP 5xx error occurred. | `role="alert"`<br>`aria-live="assertive"` | Informs user of temporary service unavailability; provides debounced `"Retry request"` button; preserves filter state; optionally displays sanitized technical details. |
| **`unavailable_restricted`** | Record is subject to statutory embargo, court order, or privacy protection laws. | `role="status"` | Plain statement citing legal disclosure restrictions without disclosing sensitive material. |

---

## 4. Error Recovery & Technical Hygiene Rules

1. **No Conflation of Errors with "No Results"**:
   - Network dropouts, 500 internal errors, and JSON parse exceptions are strictly routed to `failed_api_request`.
   - The message `"No matching records found"` is **never** shown when the true underlying cause was an unsuccessful network or backend request.

2. **Loop Prevention & Retry Debouncing**:
   - The `onRetry` handler inside `CivicStateNotice` is guarded by an `isRetrying` state.
   - During active re-fetches, the button displays a spinner with text `"Retrying..."` and disables click events, preventing denial-of-service spamming against backend endpoints.

3. **User State Preservation**:
   - Filter dropdowns, search terms, and URL parameters are preserved across error states. When a citizen clicks `"Retry request"`, the query executes using their original criteria rather than resetting to defaults.

4. **Sanitized Diagnostics (Zero Exposure of Paths or Credentials)**:
   - All error strings and technical diagnostics pass through `sanitizeErrorDetails()`:
     - Windows drive paths (e.g. `C:\Users\...`) and POSIX paths (e.g. `/var/log/...`, `/etc/...`) are redacted to `[redacted-system-path]`.
     - Authentication tokens, bearer headers, and database connection strings are stripped.
   - Diagnostics are hidden inside a closed `<details>` accordion labeled `"Show technical diagnostic info (for administrators)"`.

---

## 5. Verification & Validation

1. **TypeScript Static Analysis**:
   - Ran `npx tsc -p frontend --noEmit`.
   - **Result**: Passed with **0 errors** across all modified frontend components and pages.

2. **Backend API Test Suite**:
   - Ran `pytest tests/api/ -v`.
   - **Result**: **All 55 API test cases passed**, verifying that no backend routes or schemas were regressed.

3. **Accessibility & Keyboard Navigation**:
   - Verified that all interactive controls have visible focus rings (`focus-visible:ring-2 focus-visible:ring-emerald-500 focus-visible:outline-none`).
   - Verified that screen reader status alerts distinguish between non-urgent result filtering (`aria-live="polite"`) and critical server errors (`role="alert" aria-live="assertive"`).
   - Replaced all non-semantic `div onClick` navigation elements with `<button type="button">`.
