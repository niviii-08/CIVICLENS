# Phase 10.9 — Policy Evaluation Explorer & Report Generation Frontend Documentation

## 1. Overview & Architectural Role

The **Policy Evaluation Explorer** (`frontend/pages/10_Policy_Evaluation_Explorer.py`) is the citizen- and researcher-facing user interface for Phase 10 of **CIVICLENS TN**. It translates complex statutory budget accounts, departmental performance reports, empirical indicator observations, and audit scrutiny into an accessible, interactive, and epistemically guarded exploration experience.

The frontend operates in tight alignment with the **Unified Civic Intelligence and Evidence Graph** (Phase 9) and canonical Phase 1–8 entities.

---

## 2. Core Functional Views

The interface is structured into ten tabbed functional panels:

### 1. Policy Evaluation Explorer
- **Search & Filter:** Multi-criteria filtering by policy name, canonical scheme code, responsible department, and evaluation lifecycle status (`ACTIVE`, `EVALUATED`, `INCONCLUSIVE`).
- **Metadata Cards:** Displays canonical identifiers, geographic jurisdiction (`STATEWIDE`, `DISTRICT`), and operational launch dates.
- **Cross-Phase Canonical Anchors:** Displays links to Phase 1 Budget Schemes, Phase 3 Manifesto Promises, Phase 7 Verified Claims, and Phase 9 Evidence Graph nodes (`NODE:POLICY:<id>`).

### 2. Policy Detail and Objectives
- **Verbatim Source Text:** Preserves the exact statutory or executive wording of policy objectives from Government Orders (G.O.s) to ensure zero administrative drift or interpretation distortion.
- **Ambiguity Review Status:** Explicitly labels objectives as `VERIFIED_CLEAR` or flags ambiguous objectives for human review.
- **Beneficiary Groups & Eligibility Rules:** Detailed criteria for eligible demographics (e.g. government school alumnae, income thresholds, household electricity limits).

### 3. Budget Execution View
- **Multi-Year Analysis:** Analyzes Budget Estimate (BE) vs. Revised Estimate (RE) vs. Actual Audited Expenditure.
- **Absorption Metrics:** Computes Revised Allocation Absorption Rate (RAAR) and Surrender of Funds Ratio (SFR).
- **Epistemic Spending Guardrail:** Displays prominent alerts warning that underspending alone does not prove policy failure (e.g. procurement phasing or unit-cost savings) and 100% absorption does not prove public benefit.

### 4. Implementation Output View
- **Operational Deliverables:** Compares planned physical targets vs. completed physical deliverables across `ImplementationActivity` records.
- **Completion Ratios:** Computes Output Quantity Completion Ratios (OQCR) grouped by physical units (students, camps, health kits, bio-mining acres) so incompatible units are never aggregated together.
- **Tier Clarification:** Explicitly labels physical deliverables as belonging strictly to the OUTPUT tier, distinguishing them from citizen OUTCOMES.

### 5. Indicator and Baseline Comparison
- **Five-Tier Results Chain Classification:** Classifies all indicators across INPUT, ACTIVITY, OUTPUT, OUTCOME, and IMPACT.
- **Strict Missing-Data Handling:** Missing baseline or comparison observations are preserved as `None` / `Unreported` and are **never** treated as zero.
- **Collection Methodology & Formulas:** Exposes exact administrative or survey data sources (e.g. AISHE, NFHS, State Health MIS).

### 6. Outcome Trend View
- **Before-and-After Comparisons:** Compares baseline vs. follow-up values with absolute change and mathematically valid percentage change.
- **Zero-Baseline Safeguard:** Mathematically undefined percentage changes on zero baselines are flagged and suppressed to prevent division-by-zero distortion.
- **Non-Causal Epistemic Label:** Every comparison is explicitly labeled as `DESCRIPTIVE_ASSOCIATION_OR_OBSERVED_CHANGE`. Correlation is never presented as proven causal impact without a counterfactual evaluation design.

### 7. Evidence and Findings Panel
- **12 Mandatory Attributes:** Exposes evaluation ID, policy ID, question, finding statement, evidence references, indicator metrics, calculation method, supporting evidence, contradicting evidence, limitations, review status, and timestamp.
- **Dialectical Presentation:** Supporting documentary evidence is displayed side-by-side with contradicting or contextual audit observations (e.g., CAG performance audit findings).

### 8. Source Document Explorer
- **Full Traceability:** Every metric links directly to primary sources including Tamil Nadu Government Gazettes, CAG Audit Reports, AISHE statistical releases, and State Planning Commission evaluation studies.
- **Phase 9 Evidence Graph Integration:** Displays connected graph edges, relationship types (`implements`, `evaluates`, `measures`), matching methods (`DETERMINISTIC_ID`, `DIRECT_DOCUMENTARY`), and confidence scores.

### 9. Limitations and Data Quality View
- **Methodological Caveats:** Catalogs selection biases, absence of control groups, external confounding factors, and reporting lags.
- **Data Quality Audit Logs:** Tracks unresolved anomalies from `policy_evaluation_data_quality.csv` (e.g., CAG finance account reconciliation lags).

### 10. Evaluation Report & Export
- **Auditable Generation:** Generates comprehensive evaluation dossiers compiling objectives, stated targets, metric definitions, methodology, limitations, and source references.
- **Multi-Format Export:** One-click downloads available in:
  - **Markdown (`.md`)**: Complete human-readable report.
  - **JSON (`.json`)**: Machine-readable structured schema.
  - **CSV (`.csv`)**: Tabular quantitative target and indicator data.

---

## 3. Resilience, Fallback & Error Handling

- **API-First Architecture:** Calls backend REST endpoints via `api_client` (`/api/policy-evaluation/...`).
- **Zero-Downtime Database Fallback:** If the REST API server is offline or unreachable, the frontend seamlessly queries `civiclens.db` via SQLAlchemy `SessionLocal()`, ensuring uninterrupted analysis.
- **Empty States:** When a policy lacks specific financial or physical deliverables, informative advisory notices are displayed instead of blank screens or broken widgets.

---

## 4. Methodological Prohibitions

1. **No Political Success Scores:** The application deliberately refrains from producing a single composite "policy score" or percentage, as political scoring lacks defensible empirical validity and invites subjective bias.
2. **Zero Target Invention:** No targets are invented by analysts; missing targets are explicitly labelled as `NO_PUBLISHED_TARGET`.
3. **No Uncorroborated Causal Claims:** Observable indicator increases are never attributed solely to a policy without rigorous counterfactual identification.
