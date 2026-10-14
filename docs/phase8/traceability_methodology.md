# Phase 8.11 — Civic Issue Evidence Traceability & Resolution Audit Methodology

**System:** CIVICLENS TN  
**Phase:** 8.11 (Public Grievance & Civic Issue Intelligence)  
**Date:** 2026-10-14  
**Status:** Approved Statutory Methodology  

---

### 1. Conceptual Framework & Objectives

In public civic governance, a fundamental epistemic challenge is the gap between **administrative declarations** and **ground truth empirical outcomes**. Grievance management systems frequently record dockets as "closed" or "resolved" when an administrative acknowledgment is issued or an inter-departmental memo is forwarded, without verifying whether physical remediation occurred.

Phase 8.11 establishes an **end-to-end bidirectional evidence traceability and resolution audit trail** within CIVICLENS TN. Every civic issue can be inspected from its initial public petition through departmental routing and responses, to empirical physical evidence and role-governed human audits.

```
[1. ORIGINAL PUBLIC RECORD]
      │  (RECORD_ID_MATCH / INGESTION)
      ▼
[2. NORMALIZED CIVIC ISSUE]
      │  (TAXONOMY_CLASSIFICATION & JURISDICTION_ROUTING)
      ▼
[3. RESPONSIBLE DEPARTMENT / LOCAL AUTHORITY]
      │  (OFFICIAL_ACTION_TAKEN_REPORT / ATR_SUBMISSION)
      ▼
[4. OFFICIAL RESPONSE / ATR]
      │  (CLOSURE_DECLARATION)
      ▼
[5. REPORTED RESOLUTION (marked_resolved)]
      │  (EMPIRICAL_AUDIT / WORK_ORDER / SITE_INSPECTION)
      ▼
[6. RESOLUTION EVIDENCE]
      │  (INDEPENDENT_VERIFICATION & AUDITOR_SIGN_OFF)
      ▼
[7. VERIFICATION STATUS & AUDIT TRAIL]
```

---

### 2. Core Epistemic Invariants

1. **Reported Status $\neq$ Verified Outcome**:  
   A departmental classification of `marked_resolved` signifies solely that the reporting authority has declared the issue closed. It **never** establishes an independently verified empirical fix. CIVICLENS TN strictly separates administrative claims from verified outcomes.

2. **Bidirectional Navigation**:  
   Auditors and citizens must be able to navigate:
   - **Forward**: From petition $\to$ issue $\to$ department $\to$ ATR $\to$ closure claim $\to$ evidence $\to$ audit sign-off.
   - **Backward**: From an empirical artifact (e.g. completion certificate or field inspection photo) back to the response, department, normalized issue, and original citizen petition.

3. **Explicit Provenance on Every Hop**:  
   Every link in the chain records its source record, target record, relationship nature, matching method, confidence score (0.0–1.0), and timestamp.

4. **Transparent Data Gaps**:  
   Missing intermediate records are never hidden or silently dropped. The system explicitly renders structured gap indicators with reasons (e.g., *"No official Action-Taken Report filed in collected records"*, *"Zero empirical evidence documented"*).

5. **Contradictory Evidence Preservation**:  
   When independent evidence (e.g. citizen audit or investigative news report) contradicts an official ATR, the contradiction is highlighted as `resolution_evidence_conflicting` and routed to `DISPUTED`. It is never overwritten.

6. **DPDPA 2023 Compliance**:  
   In compliance with the Digital Personal Data Protection Act (DPDPA) 2023, zero Personal Identifiable Information (names, personal phone numbers, email addresses, exact residential door addresses) is exposed anywhere in the traceability chain or audit logs.

---

### 3. Origin Badge Classifications

Every node and hop in the traceability timeline is stamped with an origin badge:

| Badge Indicator | Technical Code | Definition | Legal / Audit Significance |
| :--- | :--- | :--- | :--- |
| 🏛️ **Official Government Record** | `OFFICIAL_GOVERNMENT_RECORD` | Originates directly from official government portals, ATRs, gazette notifications, municipal resolutions, or statutory work orders. | Primary evidentiary weight; reflects official executive action. |
| 🤖 **Automated System Inference** | `AUTOMATED_SYSTEM_INFERENCE` | Derived via deterministic rule engines, bilingual NLP classification, geospatial boundary matching, or multi-source corroboration algorithms. | System-generated hypothesis; transparently flagged with confidence and model version. |
| 👤 **Human Auditor Review** | `HUMAN_AUDITOR_REVIEW` | Authenticated assessment override or validation executed by an authorized civic auditor or ombudsperson. | Final evidentiary determination; carries full accountability with reviewer role and rationale. |

---

### 4. Canonical Evidence Assessment Taxonomy

CIVICLENS TN enforces a 7-state taxonomy for evidence assessment:

1. `resolution_evidence_available`: At least one empirical artifact (work order, completion certificate, site report) corroborates the declared resolution.
2. `resolution_evidence_incomplete`: Partial documentation exists (e.g., sanction order) but final completion or handover proof is absent.
3. `resolution_evidence_conflicting`: Independent ground reports, citizen audits, or field photographs contradict official closure claims.
4. `resolution_not_independently_verified`: Official closure is recorded, but no third-party or independent validation has occurred.
5. `independently_verified_resolved`: Both official documentation and corroborating empirical evidence or independent field audits confirm remediation.
6. `insufficient_evidence`: The docket lacks documentation to substantiate either resolution or ongoing failure.
7. `pending_review`: Awaiting assessment by an authorized civic auditor.

---

### 5. Mathematical Formulations for Traceability Metrics

All metrics are computed over validated records. Where denominators equal zero, rates default safely to $0.0$.

#### 1. Evidence Coverage Rate ($R_{EC}$)
Measures the proportion of administrative closures backed by empirical evidence artifacts:
$$\large R_{EC} = \frac{N_{\text{resolved with evidence}}}{N_{\text{marked resolved}}}$$
- **Numerator ($N_{\text{resolved with evidence}}$)**: Issues with status `RESOLVED` or `VERIFIED_RESOLVED` having $\ge 1$ linked `ResolutionEvidence`.
- **Denominator ($N_{\text{marked resolved}}$)**: Total issues with status `RESOLVED` or `VERIFIED_RESOLVED` or having an ATR with `reported_status == "marked_resolved"`.

#### 2. Independent Verification Rate ($R_{IV}$)
Measures the proportion of administrative closures that have undergone third-party or empirical verification:
$$\large R_{IV} = \frac{N_{\text{independently verified}}}{N_{\text{marked resolved}}}$$
- **Numerator ($N_{\text{independently verified}}$)**: Issues where `resolution_verification_status == "VERIFIED"` or `evidence_assessment == "independently_verified_resolved"`.
- **Denominator ($N_{\text{marked resolved}}$)**: Total marked-resolved issues.

#### 3. Department Response Rate ($R_{DR}$)
Measures administrative responsiveness across all filed grievances:
$$\large R_{DR} = \frac{N_{\text{with official response}}}{N_{\text{total issues}}}$$
- **Numerator ($N_{\text{with official response}}$)**: Issues having $\ge 1$ logged `ResponseRecord`.
- **Denominator ($N_{\text{total issues}}$)**: Total civic issues.

#### 4. Unverified Resolution Rate ($R_{UR}$)
Measures the proportion of administrative closures operating on trust without corroboration:
$$\large R_{UR} = \frac{N_{\text{marked resolved}} - N_{\text{independently verified}}}{N_{\text{marked resolved}}} = 1.0 - R_{IV}$$

#### 5. Conflicting Evidence Rate ($R_{CE}$)
Identifies the proportion of evidence-backed issues where ground reports contest closure:
$$\large R_{CE} = \frac{N_{\text{conflicting issues}}}{N_{\text{issues with evidence}}}$$
- **Numerator ($N_{\text{conflicting issues}}$)**: Issues with `evidence_assessment == "resolution_evidence_conflicting"`, `resolution_verification_status == "CONTRADICTED"`, or $\ge 1$ evidence having `contradicts_resolution == True`.
- **Denominator ($N_{\text{issues with evidence}}$)**: Total issues having $\ge 1$ linked `ResolutionEvidence`.

#### 6. Audit Trail Completeness Rate ($R_{ATC}$)
Measures structural integrity across all stages of the traceability chain:
$$\large R_{ATC} = \frac{N_{\text{complete audit trail}}}{N_{\text{total issues}}}$$
- **Numerator ($N_{\text{complete audit trail}}$)**: Issues having unbroken links across Stages 1–4 (Grievance + Department + Response) and verified or reviewed in Stage 7.
- **Denominator ($N_{\text{total issues}}$)**: Total civic issues.

---

### 6. Role-Governed Review Workflow

To prevent unauthorized tampering while enabling human oversight, reviews require explicit role authentication via HTTP header:
`X-Reviewer-Role: SENIOR_CIVIC_AUDITOR | DISTRICT_AUDITOR | CIVIC_OMBUDSPERSON | ADMIN`

#### Permitted Actions & State Transitions

| Review Action | Target Issue Status | Target Assessment | Audit Trail Event |
| :--- | :--- | :--- | :--- |
| `VERIFY_RESOLUTION` | `VERIFIED_RESOLVED` | `independently_verified_resolved` | `AUDITOR_REVIEW_ACTION` |
| `DISPUTE_RESOLUTION` | `DISPUTED` | `resolution_evidence_conflicting` | `AUDITOR_REVIEW_ACTION` |
| `REOPEN_ISSUE` | `OPEN` (repeat count +1) | `insufficient_evidence` | `AUDITOR_REVIEW_ACTION` |
| `REQUEST_EVIDENCE` | Unchanged | `resolution_evidence_incomplete` | `AUDITOR_REVIEW_ACTION` |
| `UPDATE_ASSESSMENT`| Unchanged | User specified (valid Enum) | `AUDITOR_REVIEW_ACTION` |

Every action creates an immutable `CivicReviewAudit` entry and appends an `IssueEvent` audit trail record. Rationale notes are automatically sanitized against PII.

---

### 7. Methodological Limitations & Usage Guardrails

1. **Reporting Disparities**: Complaint counts reflect smartphone access, municipal helpline awareness, and civic portal adoption, **not** the true per-capita incidence of civic problems.
2. **Non-Causality Guardrail**: An infrastructure deficiency occurring within an electoral constituency or administrative ward does not imply malfeasance or causation by the incumbent representative without explicit statutory evidence.
3. **Absence of Proof $\neq$ Proof of Absence**: The lack of documented completion certificates in the collected records indicates a **data collection gap**, not conclusive proof of non-performance.
