# CIVICLENS TN — Phase 11.2: Shared Layout and Citizen-Friendly Navigation Report

**Date:** 2026-10-17  
**Milestone:** Phase 11.2 Implementation  
**Status:** Complete  

---

## 1. Executive Summary

Phase 11.2 establishes a unified, citizen-friendly application shell and navigation architecture for CIVICLENS TN. Prior to Phase 11.2, the platform functioned as an assortment of technical research modules with a dense fixed sidebar, developer jargon ("Policy Outcome & Impact Evaluation", "MCA-21 Cross-Validation", "Evidence Graph Multi-Hop Traversal"), and no consistent page header or breadcrumb structure.

Phase 11.2 addresses these findings from the Phase 11.1 citizen UX audit by:
1. Replacing the fixed desktop sidebar with a responsive top header and civic footer.
2. Restructuring navigation into 7 primary citizen-facing destinations plus a consolidated "Explore all features" secondary hub.
3. Establishing reusable `PageHeader` and `Breadcrumb` components across all 10 core routes.
4. Adding dedicated citizen discovery routes: `/schemes` (Government Schemes) and `/explore` (Advanced Features Hub).
5. Ensuring complete responsiveness, WCAG AA contrast, keyboard accessibility, and zero broken links.

---

## 2. Shared Components Created & Modified

### New Components

| Component | Path | Description |
|-----------|------|-------------|
| `Header` | `frontend/src/components/Header.tsx` | Sticky top navigation bar featuring CIVICLENS TN wordmark, subtitle, 7 citizen nav links, "Explore all features" dropdown, live backend health pill, search CTA button, and accessible mobile hamburger drawer. |
| `Footer` | `frontend/src/components/Footer.tsx` | Civic footer with structured links across Citizen Services, Civic Intelligence Lab, and Data Provenance, alongside official disclaimer and copyright. |
| `Breadcrumb` | `frontend/src/components/Breadcrumb.tsx` | Accessible breadcrumb navigation (`nav aria-label="Breadcrumb"`, `aria-current="page"`, Home icon, chevron delimiters). |
| `PageHeader` | `frontend/src/components/PageHeader.tsx` | Standardized page header component providing title, plain-language description, optional badge, breadcrumbs, and contextual action buttons. |

### Layout Updates

| File | Path | Description |
|------|------|-------------|
| `RootLayout` | `frontend/src/app/layout.tsx` | Replaced legacy two-column flex layout (sidebar + navbar) with a top-to-bottom vertical column (`Header` → constrained `<main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 md:py-8">` → `Footer`). |

### New Route Pages Created

| Route | Path | Description |
|-------|------|-------------|
| `/schemes` | `frontend/src/app/schemes/page.tsx` | Citizen-friendly welfare scheme explorer showcasing key Tamil Nadu welfare schemes (KMUT, Breakfast Scheme, Pudhumai Penn, Vidiyal Payanam, etc.) with beneficiary filters and bilingual search. |
| `/explore` | `frontend/src/app/explore/page.tsx` | Hub for secondary and specialized civic intelligence modules (Budget & Spending, Political Funding, News Coverage, Evidence Network). |

---

## 3. Navigation Mapping & Terminology Simplification

Citizen-facing terminology has been streamlined to eliminate research jargon while strictly preserving underlying data models and API endpoints:

| Citizen Destination | Route | Previous Technical Label | Placement |
|---------------------|-------|--------------------------|-----------|
| **Home** | `/` | Dashboard / Overview | Primary Nav |
| **Government Schemes** | `/schemes` | *New Citizen View* | Primary Nav |
| **Promises & Progress** | `/promises` | Manifesto Delivery Tracker | Primary Nav |
| **Representatives** | `/representatives` | Legislative Assembly Scorecard | Primary Nav |
| **Civic Issues** | `/civic` | Public Grievance Intelligence | Primary Nav |
| **Verify Claims** | `/claims` | Fact-Checking & Claims | Primary Nav |
| **Policy Results** | `/policy-evaluation` | Policy Outcome & Impact Evaluation | Primary Nav |
| **Budget & Spending** | `/budget` | Budget & Fiscal Transparency | Secondary ("Explore all") |
| **Political Funding** | `/funding` | Political Funding & Contributions | Secondary ("Explore all") |
| **News Coverage** | `/news` | Media Bias & Coverage Intelligence | Secondary ("Explore all") |
| **Explore Evidence** | `/graph` | Evidence Graph Explorer | Secondary ("Explore all") |

---

## 4. Pages Standardized with PageHeader & Breadcrumbs

All 10 major functional pages were refactored to use `PageHeader` and `Breadcrumb`:

1. `/promises` (`PromisesPage`): Added "Promises & Progress" title, plain-language description, manifesto delivery badge.
2. `/representatives` (`RepresentativesPage`): Standardized header with "Representatives (234 MLAs)" and constituency spending context.
3. `/civic` (`CivicPage`): Standardized header with "Civic Issues & Service Standards" and Citizen's Charter SLA context.
4. `/claims` (`ClaimsPage`): Standardized header with "Verify Claims" and fact-checking provenance context.
5. `/policy-evaluation` (`PolicyEvaluationPage`): Fixed stray JSX div and integrated `PageHeader` with "Policy Results" and "Export Audit Dossier" action.
6. `/budget` (`BudgetPage`): Integrated breadcrumbs linking through `/explore` to preserve hierarchical navigation context.
7. `/funding` (`FundingPage`): Integrated breadcrumbs through `/explore` for secondary feature discovery.
8. `/news` (`NewsPage`): Integrated breadcrumbs through `/explore`.
9. `/graph` (`GraphPage`): Renamed visual heading to "Explore Evidence" with breadcrumbs through `/explore`.
10. `/schemes` (`SchemesPage`): Fully native `PageHeader` and breadcrumb implementation.

---

## 5. Responsive Design & Accessibility

### Responsive Behavior
- **Desktop (≥ 1280px / `xl` breakpoint):** Horizontal navigation bar displaying all 7 primary citizen items, the "Explore all" dropdown with hover/click flyout, backend health status, and a quick-verify search button.
- **Tablet & Mobile (< 1280px):** Responsive header with compact brand mark and hamburger toggle. Expanding the hamburger reveals a slide-down mobile drawer containing:
  - All 7 primary navigation links with active highlight.
  - An expanded "Advanced Features" section with Budget, Funding, News, and Evidence links.
  - Search CTA and backend status indicators.
  - Automatic close-on-navigate behavior.

### Accessibility (WCAG 2.2 AA)
- Semantic HTML tags (`<header>`, `<nav>`, `<main>`, `<footer>`, `<button>`).
- ARIA landmarks and attributes: `aria-label="Global navigation"`, `aria-label="Breadcrumb"`, `aria-current="page"`, `aria-expanded` on dropdowns and mobile toggles.
- Color contrast compliant: Dark theme background `#06070a`, slate-900/950 card surfaces, slate-100 high-contrast primary text, slate-400 secondary text, and blue-600 interactive accents.
- Keyboard navigation: Full tab navigation support across header items, dropdown menu options, breadcrumb trails, and mobile drawer controls.

---

## 6. Build and Test Verification

### Next.js Production Build
Executed `npm run build` in `frontend/`:
- **Build Status:** SUCCESS (Exit code 0)
- **TypeScript & Lint Validation:** PASSED with zero errors (`npx tsc --noEmit` clean).
- **Prerendered Routes (15 total):**
  - `/` (Home)
  - `/_not-found`
  - `/budget`
  - `/civic`
  - `/claims`
  - `/explore` *(New)*
  - `/funding`
  - `/graph`
  - `/news`
  - `/policy-evaluation`
  - `/promises`
  - `/representatives`
  - `/schemes` *(New)*

### Test Infrastructure Audit
- Checked for frontend automated test suites: No Jest, Vitest, Cypress, or Playwright configurations exist in `frontend/package.json`.
- The repository relies on backend Python integration/unit test suites (`tests/`).
- Verified zero console errors or broken import paths during static generation.

---

## 7. Remaining Limitations & Next Phase Dependencies

1. **Home Page Redesign (Phase 11.3):** The current home page (`/`) still displays the legacy dashboard layout with hardcoded metrics and hero verify form. Phase 11.3 will implement the citizen-friendly home page with 6 entry cards and search integration.
2. **Unified Search (Phase 11.4):** Header search currently directs users to `/claims`. Phase 11.4 will unify discovery across schemes, promises, representatives, civic issues, and claims into a shared search engine.
3. **Database Population:** As documented in Phase 11.1, `civiclens.db` currently contains 16 populated tables (primarily Phase 3 promises and schemes); Phase 10 tables require ingestion for live policy evaluations.
