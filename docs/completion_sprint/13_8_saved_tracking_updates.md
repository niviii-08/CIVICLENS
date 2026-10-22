# CIVICLENS TN — Phase 13.8: Saved Civic Tracking and Updates

## 1. Executive Summary
Phase 13.8 introduces a **local-first, privacy-preserving citizen civic tracking and live update engine** for **CIVICLENS TN**. Citizens can track manifesto promises, government welfare schemes, elected representatives (MLAs), claim verification dossiers, and civic grievances without creating accounts, providing email addresses, or undergoing invasive surveillance.

The system combines browser-based client-side persistence (`localStorage`) with a stateless backend change-detection engine that surfaces verified state transitions, new budget allocations, and Government Order publications while strictly preventing manufactured notifications.

---

## 2. Tracking Architecture & Persistence Model

### 2.1. Local-First Client Storage
* **Identity Architecture:** There are no mandatory user account tables in CIVICLENS TN. In accordance with Phase 13.8 instructions, the platform avoids inventing an unnecessary authentication/password database.
* **Storage Medium:** Browser `localStorage` under the key `civiclens_saved_records`.
* **Payload Structure:**
  ```json
  [
    {
      "record_type": "promise",
      "record_id": "PRM-DMK-2021-001",
      "title": "₹1,000 monthly basic rights grant for eligible women heads of families.",
      "detail_url": "/promises/PRM-DMK-2021-001",
      "last_known_status": "ANNOUNCED",
      "saved_at": "2023-01-01T00:00:00.000Z"
    }
  ]
  ```
* **Zero PII & Secrets:** No citizen names, phone numbers, passwords, session tokens, or sensitive credentials are ever written to browser storage.

### 2.2. Cross-User Privacy & Data Isolation
* Because saved items reside solely within each citizen's browser device, **cross-user data leakage is architecturally impossible**.
* The backend API operates in a stateless verification mode: it receives a batch of identifiers from the requesting browser, checks their live database state, and responds immediately without persisting user query histories.

---

## 3. Change Detection & Epistemic Guardrails

### 3.1. Deterministic Change Detection Rules
To prevent notification fatigue and maintain institutional credibility, notifications are never generated merely because a page was loaded or reloaded:
1. **Status Transition Detection:**
   - If `last_known_status` differs from the current database status (e.g. `ANNOUNCED` &rarr; `PARTIALLY_FULFILLED`), the system emits a structured update event:
     - `change_type`: `STATUS_TRANSITION`
     - `change_date`: Last verified database update timestamp.
     - `change_source`: "Official Gazettes and State Verification Ledger".
     - `change_description`: "Status updated from 'ANNOUNCED' to 'PARTIALLY_FULFILLED'."
2. **New Evidence & Disbursement Publication:**
   - Evaluates whether the record's verified audit timestamp is newer than the citizen's `saved_at` timestamp.
   - Emits `METRIC_OR_EVIDENCE_UPDATE` only when newly verified evidence documents or budget accounts are ingested.
3. **Retired / Archived Records:**
   - If a saved record is de-registered or purged from the public registry, `is_valid` returns `False`, accompanied by a clear notice (`RECORD_DELETED_OR_ARCHIVED`) and a one-click cleanup prompt (`can_remove: True`).

### 3.2. Outbound Delivery Safeguards
* **Notification Delivery Mechanism Status:**
  - Outbound email (SMTP), SMS gateways, and native mobile push servers are **intentionally not configured** in the project repository.
  - In strict compliance with Instruction 8 and Constraints ("Only implement email, push, or other outbound notifications if a real delivery mechanism is already configured... Do not add an authentication provider or notification vendor without justified requirements"), all notifications remain **in-app only**.
  - Citizens can toggle update highlighting on or off via the in-app preference switch (`civiclens_tracking_preferences`).

---

## 4. Supported Civic Record Domains

| Domain | Entity Class | Primary Identifiers | Statuses Tracked | Detail Route |
| :--- | :--- | :--- | :--- | :--- |
| **Promises** | `PoliticalPromise` | `promise_id` | `ANNOUNCED`, `POLICY_ACTION`, `PARTIALLY_FULFILLED`, `IMPLEMENTED` | `/promises/[id]` |
| **Schemes** | `HistoricalScheme`, `PolicyRegistryEntry` | `canonical_scheme_code`, `id` | `ACTIVE_DISBURSEMENT`, `OPERATIONAL`, `UNDER_EVALUATION` | `/schemes/[id]` |
| **MLAs** | `Representative` | `representative_id`, `id` | `INCUMBENT_MLA`, `TERM_CONCLUDED` | `/representatives/[id]` |
| **Claims** | `Claim`, `VerificationResult` | `claim_id` | `SUPPORTED`, `CONTRADICTED`, `PARTIALLY_SUPPORTED`, `MISSING_CONTEXT` | `/claims/[id]` |
| **Civic Grievances** | `CivicIssue` | `issue_code`, `id` | `LOGGED`, `IN_PROGRESS`, `SLA_BREACHED`, `RESOLVED` | `/civic/[id]` |

---

## 5. Software Components Delivered

### 5.1. Backend Service & API
* [`backend/services/saved_tracking_service.py`](file:///backend/services/saved_tracking_service.py):
  - `SavedCivicTrackingService` class with `validate_and_resolve_record`, `check_record_update`, and `batch_check_updates`.
  - Automated deduplication for duplicate tracking requests.
* [`backend/api/tracking.py`](file:///backend/api/tracking.py):
  - Blueprint `tracking_bp` mounted at `/api/tracking`.
  - Exposes `GET /types`, `POST /validate`, `POST /check-updates`, and `GET /item/<type>/<id>`.
* [`backend/api/routes.py`](file:///backend/api/routes.py):
  - Registered `tracking_bp` in central API gateway.

### 5.2. Frontend Tracker & Navigation
* [`frontend/src/lib/useSavedCivicItems.ts`](file:///frontend/src/lib/useSavedCivicItems.ts):
  - Custom React hook for client-side storage, duplicate prevention, removal, batch updates, and preference toggling.
* [`frontend/src/app/saved/page.tsx`](file:///frontend/src/app/saved/page.tsx):
  - Comprehensive citizen tracking dashboard with category filters, live change alerts, empty state guidance, and one-click removal.
* [`frontend/src/components/Sidebar.tsx`](file:///frontend/src/components/Sidebar.tsx):
  - Added "Tracked & Saved" navigation item with bookmark icon and "Local" badge.

---

## 6. Verification and Validation Results

### 6.1. Automated Unit Test Suite (`tests/unit/test_saved_tracking.py`)
Executed with Python 3.13:
```powershell
pytest tests/unit/test_saved_tracking.py -v
```
Results:
```
============================= 21 passed in 1.47s ==============================
- test_get_supported_tracking_types: PASSED
- test_validate_existing_promise: PASSED
- test_validate_existing_scheme: PASSED
- test_validate_existing_representative: PASSED
- test_validate_existing_claim: PASSED
- test_validate_existing_civic_issue: PASSED
- test_validate_nonexistent_record: PASSED
- test_validate_unsupported_type: PASSED
- test_change_detection_status_transition: PASSED
- test_change_detection_no_change_when_reloaded: PASSED
- test_change_detection_for_archived_record: PASSED
- test_batch_check_updates_empty_state: PASSED
- test_batch_check_updates_deduplication: PASSED
- test_batch_check_updates_mixed: PASSED
- test_cross_user_isolation_and_privacy_controls: PASSED
- test_api_get_tracking_types: PASSED
- test_api_post_validate_single: PASSED
- test_api_post_validate_batch: PASSED
- test_api_post_check_updates: PASSED
- test_api_get_tracked_item: PASSED
- test_api_validation_errors: PASSED
```

### 6.2. Frontend Type Integrity Check
```powershell
npm run typecheck --prefix frontend
```
Results:
```
> civiclens-frontend@1.0.0 typecheck
> tsc --noEmit
Exit code: 0 (No type errors)
```

---

## 7. Infrastructure Blockers & Future Capabilities
1. **Outbound Push & Email Notifications:**
   - Blocked by lack of SMTP or WebPush service configuration in the current application architecture.
   - Mitigated via live in-app badge notifications and automatic client-side update synchronization.
2. **Cross-Device Cloud Synchronization:**
   - Cloud sync across devices would require authenticated citizen profiles, which is deliberately avoided to protect citizen privacy and anonymity under DPDPA 2023.
   - Future enhancement could support encrypted, client-side export/import of tracking JSON configuration without server account requirements.
