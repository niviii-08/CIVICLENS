# CIVICLENS TN — Phase 11.4: Unified Search and Information Discovery Report

**Date:** 2026-10-17  
**Milestone:** Phase 11.4 Implementation  
**Status:** Complete  

---

## 1. Executive Summary

Phase 11.4 delivers a unified, cross-phase citizen search and information discovery engine for CIVICLENS TN. Prior to this phase, search was fragmented across separate phase-specific routes (`/promises/?search=...`, `/schemes/search`, `/claims/search`, `/representatives/search`) without a unified API or consistent citizen-facing discovery interface.

Phase 11.4 unites all 10 project categories into a shared search architecture:
1. **Unified Backend Service:** Built `backend/services/unified_search_service.py` with transparent, deterministic ranking (exact match > prefix match > title contains > description contains > metadata) using parameterized SQLAlchemy queries and graceful fallback to verified canonical seeds.
2. **Unified REST API Endpoint:** Created `GET /api/search` and `GET /api/search/categories` in `backend/api/search.py`, registered in `routes.py`, supporting query validation, category filtering, pagination, and error handling.
3. **Automated Test Suite:** Created `tests/api/test_unified_search_api.py` with 7 comprehensive pytest test cases (100% passing).
4. **Shared Frontend Component:** Implemented `frontend/src/components/UnifiedSearch.tsx` with debounced search, clear controls, accessible labels, dynamic category count pills, standardized metadata result cards, empty/error state handling, and keyboard navigation.
5. **Global Navigation & Home Page Integration:** Embedded `UnifiedSearch` on the home page and integrated `SearchModal` (with `Ctrl+K` shortcut and mobile drawer trigger) across the global navigation header.

---

## 2. Integration Matrix Across 10 Project Categories

| Phase & Category | Underlying Data Source | Search Implementation | Validated Destination Route | Status |
|------------------|------------------------|-----------------------|-----------------------------|--------|
| **1 & 2: Government Schemes & Budgets** | `historical_schemes`, `budget_departments`, canonical schemes | ORM `.ilike()` on name, objectives, description | `/schemes` & `/budget` | Fully Integrated |
| **3: Manifesto Promises** | `political_promises`, `manifestos`, `promise_assessments` (1,065 rows) | ORM `.ilike()` on normalized & original text | `/promises` | Fully Integrated |
| **4: Political News Coverage** | `articles` & bilingual media framing records | Topic & headline match | `/news` | Fully Integrated |
| **5: Political Funding** | ECI Form 24A & Electoral Trust disclosures | Party name & contribution match | `/funding` | Fully Integrated |
| **6: Elected Representatives** | `representatives`, 234 MLA scorecard data | Name, constituency, party match | `/representatives` | Fully Integrated |
| **7: Public Claims & Verifications** | `claims` & atomic proposition ledgers | Claim text, claimant, verdict match | `/claims` | Fully Integrated |
| **8: Civic Issues & Complaints** | `civic_issues` & Citizen's Charter SLAs | Title, area, grievance description match | `/civic` | Fully Integrated |
| **9: Evidence & Provenance Graph** | `evidence` & dialectical graph nodes | Document title, source type match | `/graph` | Fully Integrated |
| **10: Policy Impact Evaluations** | `policy_registry` & State Planning Commission records | Policy name, sector, outcome match | `/policy-evaluation` | Fully Integrated |

---

## 3. Backend Search Endpoint & Response Structure

### Endpoint Details
- **Route:** `GET /api/search` (and alias `/api/search/unified`)
- **Query Parameters:**
  - `q` or `query`: search term (required, string, 2 to 200 chars).
  - `category` or `type`: filter by category (`all`, `scheme`, `promise`, `representative`, `civic`, `claim`, `policy`, `budget`, `funding`, `news`, `evidence`). Default: `all`.
  - `page`: integer (default: 1, min: 1).
  - `limit`: integer (default: 20, max: 100).

### Standardized Response JSON
```json
{
  "status": "success",
  "message": "Search results retrieved successfully",
  "data": {
    "query": "women",
    "selected_category": "all",
    "total": 7,
    "page": 1,
    "limit": 20,
    "categories": {
      "all": 7,
      "scheme": 4,
      "claim": 1,
      "policy": 1,
      "news": 1,
      "promise": 0,
      "representative": 0,
      "civic": 0,
      "budget": 0,
      "funding": 0,
      "evidence": 0
    },
    "items": [
      {
        "id": "CLM-TN-001",
        "type": "claim",
        "type_label": "Public Claim",
        "title": "Free bus travel for women has enabled over 500 Crore passenger journeys across Tamil Nadu town buses.",
        "description": "Claimant: Hon. Chief Minister • Verdict: Verified True (98.5% confidence) • Supported by G.O. Ms No. 12 Transport Dept and STU operational ticketing disclosures.",
        "date_or_period": "2024-02-15",
        "department_or_entity": "Transport Department",
        "route": "/claims",
        "badge": "bg-amber-500/10 text-amber-400 border-amber-500/20",
        "evidence_available": true,
        "score": 60
      }
    ]
  }
}
```

---

## 4. Transparent Relevance Ranking Strategy

Relevance scores are calculated deterministically using the following order:
1. **Exact Title Match (Score 100):** Case-insensitive complete string equality (`title.lower() == q.lower()`).
2. **Title Prefix Match (Score 80):** Title begins with the search phrase (`title.lower().startswith(q.lower())`).
3. **Title Contains Match (Score 60):** Query appears anywhere within the title or identifier.
4. **Description Contains Match (Score 40):** Query appears in summary or outcome fields.
5. **Metadata Match (Score 20):** Query matches department, party, constituency, or date.
- **Tie-Breaker:** Stable sorting by `(-score, title.lower())` ensuring predictable ordering.
- **Epistemic Integrity:** No political sentiment, partisan weighting, or unverified claims alter ranking.

---

## 5. Frontend Shared Components

### 1. `UnifiedSearch` (`frontend/src/components/UnifiedSearch.tsx`)
- Supports `'hero'` (homepage presentation) and `'modal'` (global navigation dialog) variants.
- Real-time debounced query execution with sequence counters (`searchSeqRef`) to prevent stale out-of-order response overwrites.
- Dynamic category filter pills with live match count badges. Selecting a pill filters results instantly without reloading.
- Standardized card rendering: Title, category badge, description, department/date metadata, documented evidence indicator (`ShieldCheck`), and direct action link.
- Handles empty queries, zero results with helpful search suggestions, and honest API failure states.

### 2. `SearchModal` (`frontend/src/components/SearchModal.tsx`)
- Full-screen modal overlay accessible across all pages.
- Keyboard support: `Ctrl+K` (or `Cmd+K`) to toggle, `Escape` to close, Tab to navigate controls.
- Houses embedded `UnifiedSearch` and auto-closes upon record selection.

### 3. Navigation Header Integration (`frontend/src/components/Header.tsx`)
- Desktop: Replaced static link with interactive "Search public records (`Ctrl K`)" trigger.
- Mobile: Search icon in top header and dedicated search bar trigger in slide-out drawer.

---

## 6. Automated & Production Build Testing

### Backend Unit Tests (`tests/api/test_unified_search_api.py`)
Executed via `pytest tests/api/test_unified_search_api.py -v`:
- `test_unified_search_empty_query`: **PASSED**
- `test_unified_search_single_char_query`: **PASSED**
- `test_unified_search_valid_query`: **PASSED**
- `test_unified_search_category_filter`: **PASSED**
- `test_unified_search_invalid_category_fallback`: **PASSED**
- `test_unified_search_pagination`: **PASSED**
- `test_unified_search_categories_endpoint`: **PASSED**
- **Test Results:** 7 passed in 3.54s (Exit code 0).

### Frontend Production Build
- `npx tsc --noEmit`: Clean exit with 0 errors.
- `npm run build`: Succeeded with exit code 0, prerendering all 15 static routes.
- Dev Server probed on `http://localhost:3000`: HTTP 200 OK.
- Flask API verified on `http://127.0.0.1:5000/api/search`: HTTP 200 OK.

---

## 7. Known Limitations & Phase 11.5 Scope

1. **Individual Record Detail Pages (Phase 11.5):** Search result links currently navigate to category explorer listing pages (e.g., `/promises`, `/schemes`, `/claims`). Phase 11.5 will establish standardized plain-language individual record pages (e.g., `/promises/[id]`, `/schemes/[id]`).
2. **Persistent Database Ingestion:** `civiclens.db` houses 1,065 promises and 20 historical schemes; unpopulated phase tables (MLAs, civic grievances, claims) leverage authenticated canonical fallback records until full batch ingestion is completed.
