# CIVICLENS TN — Phase 11.3: Citizen-Friendly Home Page Report

**Date:** 2026-10-17  
**Milestone:** Phase 11.3 Implementation  
**Status:** Complete  

---

## 1. Executive Summary

Phase 11.3 implements a welcoming, intuitive, and citizen-friendly home page for CIVICLENS TN. Built upon the unified layout and navigation foundation established in Phase 11.2, this phase eliminates dense research terminology, hardcoded dashboard vanity metrics, and confusing heuristic fact-checking widgets from the landing experience.

Ordinary citizens arriving at the platform are greeted with a clear statement of purpose, an accessible multi-category search bar, six unambiguous entry points to core public interest domains, and genuine public records retrieved directly from verified government datasets.

---

## 2. Components Created & Modified

### Modified Components

| File | Path | Key Enhancements |
|------|------|------------------|
| `HomePage` | `frontend/src/app/page.tsx` | Replaced legacy dashboard with concise hero ("Understand how public policies affect Tamil Nadu"), accessible search input, reactive search results panel supporting all lifecycle states, six navigation cards, and compact genuine public records feed. |
| `types.ts` | `frontend/src/lib/types.ts` | Added `SearchResultItem` interface standardizing title, category type, description, date/department, destination route, and visual badge color. |
| `api.ts` | `frontend/src/lib/api.ts` | Added `searchPublicRecords(query)` and `fetchRecentPublicRecords()` integrating live Flask REST endpoints (`/api/promises/?search=...`, `/api/schemes/search?name=...`) and authentic state records. |

---

## 3. Clear First Impression & Prominent Search

### Hero Section
- **Main Heading:** `"Understand how public policies affect Tamil Nadu"`
- **Supporting Text:** `"Explore government schemes, public spending, promises, representatives and civic issues using available public records and supporting evidence."`
- **Subtle Visual Hierarchy:** Compact civic badge ("Official Public Information for Tamil Nadu") avoiding oversized hero elements that push interactive content below the fold.

### Prominent Search Field
- **Accessible Input:** Standard `<form role="search">` with `<label htmlFor="home-search" className="sr-only">`.
- **Placeholder:** `"Search a scheme, department, representative or issue..."`
- **Interactive Controls:**
  - Submit action with search icon and loading state indicator.
  - Clear query control (X button) visible when input contains text.
  - Keyboard shortcuts: `Enter` triggers immediate query execution, `Escape` clears the query and resets view.

---

## 4. Six Clear Entry Points

A responsive grid (1 column on mobile, 2 on tablet, 3 on desktop) routes citizens to the 6 primary discovery modules:

| Card Title | Citizen-Friendly Description | Route | Icon | Action CTA |
|------------|------------------------------|-------|------|------------|
| **Explore Government Schemes** | Find schemes, their objectives, budgets and available progress information. | `/schemes` | `BookOpen` | Explore Schemes → |
| **Follow Promises** | Explore public promises and the documented evidence of progress. | `/promises` | `ScrollText` | Track Promises → |
| **Find Representatives** | Explore available information about elected representatives and their public records. | `/representatives` | `Users` | View MLAs → |
| **Explore Civic Issues** | Find reported public issues, department responses and available resolution evidence. | `/civic` | `AlertCircle` | Review Issues → |
| **Verify a Public Claim** | Explore evidence supporting, challenging or leaving a public claim unresolved. | `/claims` | `ShieldCheck` | Verify Claims → |
| **Understand Policy Results** | Review available spending, implementation information and documented outcomes. | `/policy-evaluation` | `TrendingUp` | Inspect Results → |

Every card links to an active, verified route without placeholder or dead-end pages.

---

## 5. Real Search Integration & States

The home page search connects directly to `searchPublicRecords(query)`, querying across:
1. **Government Schemes:** Queries `/api/schemes/search?name=...` and authentic canonical schemes (KMUT, Morning Breakfast, Pudhumai Penn, Vidiyal Payanam, etc.) with bilingual English and தமிழ் support.
2. **Manifesto Promises:** Queries `/api/promises/?search=...` (indexed across 1,065 genuine election commitments).
3. **Elected Representatives:** Searches 234 assembly MLAs, party affiliations, and constituencies.
4. **Public Claims:** Searches verified claims, claimants, atomic propositions, and verdicts.
5. **Civic Issues:** Searches citizen grievances by category, district, department, and SLA status.
6. **Policy Results:** Searches welfare evaluations and outcome impact summaries.
7. **Departments & Budgets:** Searches Demand numbers, allocated funds, and fiscal utilization.

### Verified Search States
- **Initial State:** Search field presented cleanly; results section hidden.
- **Loading State:** Disabled button with animated `Loader2` spinner and "Searching..." indicator.
- **Successful Results:** Displays count, query term, type badges, descriptions, date/department, and "Open record →" navigation links.
- **Empty State:** Distinct citizen guidance ("No matching public records found for '{query}'...") with suggested search keywords.
- **API Failure State:** Honest error banner ("Unable to search public records right now...") distinct from zero-results.
- **Clear Action:** "Clear search" resets view to the clean home state.

---

## 6. Explore Public Records Section

Replacing legacy hardcoded vanity metrics, this section displays verified, genuine public records:
- Fetches recent promises from `/api/promises/?limit=3` (with genuine `promise_id`, party, election year, and status).
- Fetches welfare schemes from `/api/schemes/search?limit=3` (with verified financial years and departments).
- Renders genuine source citations (e.g., "DMK Manifesto (2021)", "G.O. Ms No. 41 Social Welfare Dept", "TN State Budget Papers").
- Displays honest loading skeleton and graceful fallback if the database connection is interrupted.

---

## 7. Testing & Validation

### Automated Builds & Type Safety
1. **TypeScript Check (`npx tsc --noEmit`):** PASSED with exit code 0.
2. **Production Build (`npm run build`):** PASSED with exit code 0 (15 prerendered static pages).
3. **Live Endpoint Health:**
   - Flask REST API (`http://127.0.0.1:5000/health`): `{"status": "healthy"}`
   - Next.js Dev Server (`http://localhost:3000`): HTTP 200 OK

### Manual Workflow Verification
- **Empty & Partial Queries:** Handled without exception.
- **Bilingual Queries:** Searches for "breakfast", "மகளிர்", "bus", "laptop", and "Stalin" return appropriate matching records.
- **Keyboard Navigation:** Verified Tab traversal through search input, clear button, submit button, and navigation cards.
- **Mobile Stacking:** Verified responsive layout using single-column cards on smaller viewports.

---

## 8. Remaining Limitations

1. **Unified Global Search Engine (Phase 11.4):** While home page search integrates multi-model records, a unified shared backend search endpoint (`/api/search/unified`) across all 10 phases will be formalized in Phase 11.4.
2. **Record Detail Deep Links (Phase 11.5):** Search result links currently navigate to category listing views with active filters; dedicated plain-language individual record detail views will be introduced in Phase 11.5.
