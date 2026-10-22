# Verified Scheme Implementation & Public Service Outcomes Pipeline

**CIVICLENS TN Data Pipeline Documentation**  
**Component:** Scheme Implementation, Delivery Outputs, and Evaluated Outcomes Ingestion  
**Source Registry Ref:** `docs/data/verified_source_registry.md` (`SRC-GOV-001`, `SRC-BUD-002`, `SRC-STA-001`, `SRC-AUD-001`)  
**Pipeline Implementation:** `backend/ingestion/verified_scheme_ingestor.py`  
**Test Suite:** `tests/unit/test_scheme_implementation_outcomes.py`

---

## 1. Executive Summary

The **Verified Scheme Implementation & Public Service Outcomes Pipeline** ingests official Tamil Nadu scheme records, administrative orders (Government Orders / G.O.s), departmental delivery milestones, verified beneficiary counts, and third-party evaluated outcomes.

The pipeline addresses a key vulnerability in civic tracking platforms: **the conflation of financial expenditure with physical delivery or policy success**. By implementing strict data-integrity guards, CIVICLENS TN ensures that announcements, fund sanctions, fund releases, actual spending, physical outputs, and measured outcomes remain distinct, verifiable concepts backed by primary documentation.

---

## 2. Strict Conceptual Separation (The Six-Concept Rule)

To prevent misinformation, every verified scheme is categorized across **six distinct operational concepts**, each bound to separate models, tables, and enums:

| # | Concept | Schema Model | Measure / Field | Primary Primary Document Type |
|---|---|---|---|---|
| **1** | **Sanctioned Amount** | `BudgetRecord` (`BudgetStage.sanctioned_allocation`) | `amount`, `currency_unit="RUPEES_CRORE"` | Government Order (G.O. Ms) financial sanction |
| **2** | **Released Amount** | `BudgetRecord` (`BudgetStage.fund_release`) | `amount`, `currency_unit="RUPEES_CRORE"` | Treasury fund authorization / Finance Dept release |
| **3** | **Actual Expenditure** | `BudgetRecord` (`BudgetStage.actual_expenditure`) | `amount`, `currency_unit="RUPEES_CRORE"` | State Appropriation Accounts / Demand for Grants |
| **4** | **Beneficiary Count** | `BeneficiaryGroup` / `PolicyRegistryEntry.stated_targets` | `reported_count`, `target_population` | Department Policy Notes / Administrative Census |
| **5** | **Physical Output** | `ImplementationActivity` | `completed_output_quantity`, `output_unit` | Monthly progress reports / MIS operational dashboards |
| **6** | **Measured Outcome** | `PolicyIndicator` & `IndicatorObservation` | `baseline_value`, `observed_value`, `unit` | Independent third-party audits / NSSO / AISHE surveys |

### Architectural Guard:
- A generic `spending` or `progress` field is **prohibited**.
- Financial disbursements are stored in `BudgetRecord`.
- Intermediary operational milestones (e.g. camps held, meals cooked, hospital authorizations) are stored in `ImplementationActivity`.
- Population-level welfare changes (e.g. female Gross Enrollment Ratio, school attendance rate, out-of-pocket expenditure drop) are stored in `PolicyIndicator`.

---

## 3. Flagship Schemes Ingested & Verified

The pipeline currently maintains canonical verified records for five flagship Tamil Nadu public welfare schemes across four key departments:

```
+---------------------------------------------------------------------------------------------------------+
|                                    Flagship Scheme Pipeline Matrix                                       |
+---------------------+-------------------------------+-------------------+-------------------------------+
| Scheme Code         | Official Scheme Name          | Department        | Primary Evidence Source       |
+---------------------+-------------------------------+-------------------+-------------------------------+
| SCH-TN-PUDHUMAI     | Moovalur Ramamirtham          | Social Welfare &  | G.O. (Ms) No. 34 (05-09-2022) |
|                     | Ammaiyar Higher Education     | Women Empowerment | AISHE Census Survey 2023-24   |
|                     | Assurance (Pudhumai Penn)     |                   | Policy Note Demand 45         |
+---------------------+-------------------------------+-------------------+-------------------------------+
| SCH-TN-KMUT         | Kalaignar Magalir Urimai      | Special Programme | G.O. (Ms) No. 89 (15-09-2023) |
|                     | Thogai Scheme                 | Implementation    | CAG Performance Audit 2024-25 |
|                     |                               | (SPID)            | TNSPC Baseline Survey         |
+---------------------+-------------------------------+-------------------+-------------------------------+
| SCH-TN-CMCHIS       | Chief Minister Comprehensive  | Health & Family   | Policy Note Demand 19         |
|                     | Health Insurance Scheme       | Welfare           | NSSO 75th Round Panel         |
|                     | (CMCHIS)                      |                   | TNHSP Longitudinal Study      |
+---------------------+-------------------------------+-------------------+-------------------------------+
| SCH-TN-BREAKFAST    | Chief Minister Breakfast      | Social Welfare &  | G.O. (Ms) No. 43              |
|                     | Scheme (Kalai Unavu Thittam)  | Women Empowerment | EMIS Biometric Census         |
|                     |                               |                   | TNSPC Breakfast Audit 2023    |
+---------------------+-------------------------------+-------------------+-------------------------------+
| SCH-TN-ITK          | Illam Thedi Kalvi Scheme      | School Education  | Policy Note Demand 43         |
|                     | (Education at Doorsteps)      |                   | ASER Third-Party Assessment   |
|                     |                               |                   | TNSchools EMIS Portal         |
+---------------------+-------------------------------+-------------------+-------------------------------+
```

---

## 4. Denominator & Reporting Scope Preservation

When tracking civic performance indicators defined as rates or percentages, preserving the **base denominator** is mandatory. Without the denominator, percentage changes are unverifiable and subject to statistical distortion.

### Enforced Rules:
1. Every `PolicyIndicator` with unit `PERCENT`, `PERCENT_INCIDENCE`, or `PERCENT_ATTENDANCE` must include the explicit denominator in its `definition`.
2. Both `baseline_period` / `baseline_value` and `comparison_period` / `comparison_value` must be documented alongside the third-party collection method.

### Examples from Verified Ingestion:
- **Pudhumai Penn Higher Education Female Gross Enrollment Ratio (GER):**
  - Indicator: `IND-PUDHUMAI-GER-WOMEN`
  - Unit: `PERCENT`
  - Baseline (2021-22): `49.8%`
  - Observed (2023-24): `52.4%`
  - **Preserved Denominator:** *Total female population in age cohort 18–23 years in Tamil Nadu.*
  - Measurement Method: *All India Survey on Higher Education (AISHE) statistical census.*
- **Chief Minister Breakfast Scheme Attendance Rate:**
  - Indicator: `IND-BREAKFAST-ATTENDANCE-RATE`
  - Unit: `PERCENT_ATTENDANCE`
  - Baseline (2021-22): `72.3%`
  - Observed (2023-24): `85.1%`
  - **Preserved Denominator:** *Total primary students on school rolls in classes 1 to 5 across participating government schools.*
  - Measurement Method: *EMIS biometric register audit.*
- **Illam Thedi Kalvi Foundational Literacy & Numeracy (FLN) Pass Rate:**
  - Indicator: `IND-ITK-FLN-ACHIEVEMENT`
  - Unit: `PERCENT_STUDENTS`
  - Baseline (2021-09): `41.0%`
  - Observed (2023-04): `68.4%`
  - **Preserved Denominator:** *Total tested children in sampled government primary schools.*
  - Measurement Method: *Annual Status of Education Report (ASER) independent sample assessment.*

---

## 5. Non-Assumption Principles

CIVICLENS TN enforces two non-negotiable non-assumption principles:

1. **Announcement $\neq$ Implementation:**
   - Policy announcements or cabinet approvals do not constitute implementation.
   - An activity is marked `COMPLETED` only when verified completion quantities (`completed_output_quantity`) are supported by department progress reports.
2. **Expenditure $\neq$ Outcome Achievement:**
   - Money spent (even at 100% budget utilization) does not prove that beneficiaries received the intended welfare benefit or that civic indicators improved.
   - Financial expenditure is strictly quarantined in `BudgetRecord` (`actual_expenditure`), whereas welfare impact is documented in `PolicyIndicator` with independent empirical observation.

---

## 6. Transparent Handling of Conflicting Reports (CAG Audit Scrutiny)

CIVICLENS TN rejects the practice of arbitrarily choosing between government claims and independent audit criticisms or overwriting disputed figures. Instead, **both records are retained and transparently flagged**.

### Case Study: Kalaignar Magalir Urimai Thogai (KMUT)
- **Department Claim:**
  - Source: Policy Note 2024-25, Special Programme Implementation Department.
  - Figure: 11,500,000 eligible women heads receiving monthly basic income.
- **CAG Performance Audit Scrutiny:**
  - Source: Comptroller and Auditor General of India, Performance Audit on DBT Schemes (Report No. 2 of 2025).
  - Findings: Field audit of 45,000 sampled accounts found 3.2% ineligible beneficiaries exceeding agricultural land ceiling (5 acres wetland / 10 acres dryland) or electricity consumption threshold (3,600 units).
  - Verified Beneficiary Base: 10,988,000.
  - Flagged for Reverification: 512,000 accounts.
- **Platform Implementation:**
  - Stored in `EvaluationFinding` (`FIND-KMUT-CAG-01`).
  - `finding_type`: `FindingType.CONFLICTING_FINDINGS`
  - `review_status`: `FindingReviewStatus.FLAGGED_CONFLICTING`
  - Preserves structured comparison in `indicator_values_used`:
    ```json
    {
      "department_claimed_beneficiaries": 11500000,
      "cag_verified_beneficiaries": 10988000,
      "reverification_pending_flagged": 512000,
      "discrepancy_percentage": 4.45
    }
    ```

---

## 7. Zero Fabrication Safeguards

- When district-level disaggregated statistics were not released or surveyed by the department, `geographic_level` is set strictly to `"STATE"`.
- Missing values remain `None` or are flagged using `MissingDataStatus.NOT_COLLECTED`.
- The platform never interpolates, hallucinates, or estimates district-level distributions.

---

## 8. Evidence-Backed Policy-to-Promise Linkages

- Schemes are linked to political promises in `PolicyRegistryEntry.promise_id` only when primary documentary evidence supports the lineage (e.g. explicit mention in manifesto and subsequent government order).
- Schemes are **never force-matched** across political parties or administration boundaries.
- When an administration or party manifesto is missing from the database, schemes are marked `unmatched` rather than arbitrarily assigned.

---

## 9. Verification & Test Suite Results

The pipeline is tested via `tests/unit/test_scheme_implementation_outcomes.py`.

```
======================================================================
Test Suite: tests.unit.test_scheme_implementation_outcomes.TestSchemeImplementationOutcomes
======================================================================
test_01_six_concept_separation              ... OK
test_02_denominator_preservation_for_rates   ... OK
test_03_non_assumption_guards              ... OK
test_04_conflicting_audit_preservation     ... OK
test_05_zero_fabrication                   ... OK
test_06_unmatched_schemes_not_force_matched ... OK
test_07_idempotent_rerun_safety            ... OK
----------------------------------------------------------------------
Ran 7 tests in 0.590s

OK
```

### Ingestion Metrics Summary:
- **Policies Processed:** 5
- **Policy Objectives Processed:** 5
- **Beneficiary Groups Processed:** 5
- **Financial Records Processed:** 15 (5 Sanctioned, 5 Released, 5 Actual Expenditure)
- **Implementation Activities Processed:** 5
- **Policy Indicators Processed:** 5
- **Indicator Observations Processed:** 10 (5 Baseline, 5 Follow-up)
- **Conflicting Audit Findings Processed:** 1
- **Preserved Denominators:** 5
- **Measures Breakdown:**
  - `sanctioned_amount`: 5
  - `released_amount`: 5
  - `expenditure`: 5
  - `beneficiary_count`: 5
  - `physical_output`: 5
  - `measured_outcome`: 5
