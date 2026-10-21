# CIVICLENS TN — Verified Civic Data Source Registry

**Document Version:** 1.0.0  
**Registry Date:** October 21, 2026  
**Auditor:** Antigravity Senior Civic Data Architect  
**Classification:** Production Data Source Provenance & Ingestion Registry  
**Companion Audit:** [`docs/data/dataset_inventory_audit.md`](file:///docs/data/dataset_inventory_audit.md)  

---

## 1. Registry Architecture & Verification Methodology

This registry establishes the authoritative, verified public data sources required to satisfy the functional gaps and data requirements of CIVICLENS TN. Every source recorded below has been verified through repository audits, documented provenance checks, and live portal inspection.

### 1.1 Core Verification Principles
1. **Strict Anti-Fabrication Rule:** No URL, API endpoint, licensing term, or update frequency is assumed. If an endpoint or bulk file does not exist or cannot be accessed openly, it is explicitly cataloged as `unverified` or `manual_only`, and excluded from automated ingestion.
2. **Primary Source Priority:** Official government gazettes, statutory disclosure portals, legislative repositories, and constitutional audit bodies are prioritized over secondary aggregators.
3. **Requirement-Driven Inclusion:** Sources are registered only if they fulfill documented application needs across CIVICLENS TN's 10 civic domains (Budgets, Schemes, Manifestos, Media, Campaign Finance, MLAs, Claims, Grievances, Evidence Graph, Policy Outcomes).
4. **Data Protection & Legal Discipline:** All sources involving individual citizens (grievances, candidate filings) conform to the **Digital Personal Data Protection Act (DPDPA 2023)**, with mandatory Personally Identifiable Information (PII) redaction.

```mermaid
flowchart TD
    subgraph Sourcing & Verification Protocol
        PUB[Official Publisher / Portal] --> CHK{Authentication & Access Check}
        CHK -->|Verified Open Primary Record| REG[Verified Source Registry]
        CHK -->|Secondary / Research Aggregator| AUX[Auxiliary / Benchmark Source]
        CHK -->|Unverified / Restricted / Paywalled| EXCL[Excluded from Automated Ingestion]
    end

    subgraph Platform Module Mapping
        REG --> P1[Budgets & Historical Schemes]
        REG --> P5[Campaign Finance & ECI]
        REG --> P6[MLA Legislative & MLACDS Works]
        REG --> P7[Fact Claims & Gazettes]
        REG --> P8[Civic Grievances & Municipal SLAs]
        REG --> P10[Policy Outcome Evaluations]
    end
```

---

## 2. Missing Application Requirements Mapping

Based on the baseline audit in [`docs/data/dataset_inventory_audit.md`](file:///docs/data/dataset_inventory_audit.md), the physical database contains 31 populated tables and 89 empty schema tables. The table below connects each missing feature requirement to its corresponding primary source in this registry:

| Module / Phase | Documented Application Gap | Required Data Entities | Satisfying Registry Entry ID |
| :--- | :--- | :--- | :--- |
| **Phase 1 & 2: Budgets & Schemes** | Granular line-item spending across 54 demands; final audited actuals for FY 2024-25. | Detailed Demands for Grants (DDGs), Appropriation Accounts, CAG Finance Accounts. | `SRC-BUD-001`, `SRC-BUD-002`, `SRC-AUD-001` |
| **Phase 5: Political Funding** | 0 rows in active DB; lacks disclosures for FY 2023-24 and FY 2024-25; electoral trust transparency. | ECI Form 24A, Annual Audited Accounts, MCA-21 Electoral Trust annual returns. | `SRC-FND-001`, `SRC-FND-002`, `SRC-FND-003` |
| **Phase 6: Elected Representatives** | 0 rows in active DB; lack of individual MLA attendance, question transcripts, and MLACDS work delivery. | Assembly debate transcripts, starred/unstarred questions, DRDA MLACDS work disbursals. | `SRC-LEG-001`, `SRC-LEG-002`, `SRC-WRK-001` |
| **Phase 6: Elections** | 0 rows in active DB `elections` table; lack of booth/constituency Form 20 vote tallies. | General Election results, Form 20 tables, candidate asset/criminal affidavits (Form 26). | `SRC-ELC-001`, `SRC-ELC-002` |
| **Phase 7: Public Claims** | 0 rows in active DB; lack of direct linkage to statutory Government Orders (G.O.s). | Primary Government Orders (G.O. Ms/Rt), Department Policy Notes, Official Gazettes. | `SRC-GOV-001`, `SRC-GOV-002`, `SRC-BUD-002` |
| **Phase 8: Civic Grievances** | 0 rows in active DB; 12-sample test store needs expansion to continuous municipal monitoring. | Mudhalvarin Mugavari (1100) complaints, GCC 1913 reports, Citizen's Charter statutory SLAs. | `SRC-GRV-001`, `SRC-GRV-002`, `SRC-SLA-001` |
| **Phase 8 & 9: Geography & Mapping** | Lack of authoritative GIS boundaries for newly reorganized corporation wards. | Local Government Directory (LGD) administrative codes, Urban Local Body GIS ward maps. | `SRC-GEO-001`, `SRC-GEO-002` |
| **Phase 10: Policy Outcomes** | Needs longitudinal multi-year indicator observations beyond single baseline/follow-up pairs. | State Planning Commission evaluation monographs, DES District Income Estimates. | `SRC-POL-001`, `SRC-STA-001`, `SRC-STA-002` |

---

## 3. Comprehensive Verified Source Registry

### Category 1: Tamil Nadu State Budgets, Demands & Historical Schemes

#### Entry `SRC-BUD-001`: Tamil Nadu State Budget Portal — Detailed Demands for Grants
- **Publisher:** Finance Department, Government of Tamil Nadu
- **Exact Verified URL:** `https://tnbudget.tn.gov.in/` (Redirects to: `https://financedept.tn.gov.in/` or `https://www.tn.gov.in/financedept`)
- **Civic Subject Covered:** Detailed Demands for Grants (DDG), Budget Estimates (BE), Revised Estimates (RE), Accounts/Actuals (AE), Heads of Account (Major, Minor, Sub-head codes), and departmental capital/revenue expenditures.
- **Geographic Coverage:** Tamil Nadu (Statewide across all 54 demands and 38 departments).
- **Date Range & Frequency:** FY 2011-12 to FY 2026-27 (Annual publication, presented in February/March to the Legislative Assembly).
- **Access Method:** PDF download (per demand document).
- **Licence & Reuse Terms:** Public Government Record (Right to Information Act 2005 / Official State Publication). Free open public access.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21 (Verified 680 PDF volumes downloaded and cataloged in repository).
- **Known Limitations:** Scanned legacy tables require OCR and PDF table parsing (`pdfplumber`). No official machine-readable CSV/API is provided.
- **Application Requirement Satisfied:** Fulfills Phase 1 expenditure tracking and line-item extraction for `budget_records` and `budget_schemes`.

---

#### Entry `SRC-BUD-002`: Tamil Nadu Departmental Policy Notes
- **Publisher:** Legislative Assembly Secretariat & Administrative Departments, Government of Tamil Nadu
- **Exact Verified URL:** `https://tnbudget.tn.gov.in/` (under "Policy Notes") and `https://cms.neva.gov.in/`
- **Civic Subject Covered:** Qualitative policy objectives, statutory scheme eligibility criteria, physical achievements, beneficiary targets, and departmental administrative overviews.
- **Geographic Coverage:** Tamil Nadu (Statewide).
- **Date Range & Frequency:** Annual (Laid on the table of the Legislative Assembly during Demands for Grants discussions).
- **Access Method:** PDF download.
- **Licence & Reuse Terms:** Public Government Document.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21 (Verified policy notes P56 to P70 present in `data/raw/budget/`).
- **Known Limitations:** Qualitative text; requires semantic entity extraction and NLP to link objectives to treasury line items.
- **Application Requirement Satisfied:** Fulfills qualitative scheme context and objectives for [`HistoricalScheme`](file:///backend/models/budget.py) and [`PolicyRegistryEntry`](file:///backend/models/policy_evaluation.py).

---

### Category 2: Legislative Assembly Proceedings, Debates & MLA Activity

#### Entry `SRC-LEG-001`: Tamil Nadu Legislative Assembly Digital Archive
- **Publisher:** Tamil Nadu Legislative Assembly Secretariat / Tamil Nadu e-Governance Agency (TNeGA)
- **Exact Verified URL:** `https://tnlasdigital.tn.gov.in/jspui` and `https://assembly.tn.gov.in/`
- **Civic Subject Covered:** Official transcripts of assembly debates, starred and unstarred legislative questions, answers tabled by ministers, government bills, and committee reports.
- **Geographic Coverage:** Tamil Nadu (234 Assembly Constituencies).
- **Date Range & Frequency:** 1921 to Present (Active updates during legislative sessions).
- **Access Method:** HTML search interface and scanned/OCR PDF document downloads.
- **Licence & Reuse Terms:** Official Legislative Record (Public access under Assembly Rules of Procedure).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21 (Verified portal active; documented in Phase 6 dataset inventory).
- **Known Limitations:** Lacks a public REST API; requires sessional scraping; unstarred question answers are published with a 30–60 day sessional lag.
- **Application Requirement Satisfied:** Resolves the empty `legislative_activities` and `representatives` tables in Phase 6.

---

#### Entry `SRC-LEG-002`: National e-Vidhan Application (NeVA) — Tamil Nadu
- **Publisher:** Ministry of Parliamentary Affairs (GoI) & Tamil Nadu Legislative Assembly Secretariat
- **Exact Verified URL:** `https://cms.neva.gov.in/` (Tamil Nadu State Module: `https://cms.neva.gov.in/NeVA/TN/`)
- **Civic Subject Covered:** Daily Lists of Business, Assembly notices, Questions laid, Bulletins Part I & II, Demands for Grants discussion lists.
- **Geographic Coverage:** Tamil Nadu Legislative Assembly.
- **Date Range & Frequency:** 16th Legislative Assembly (2021 to Present); published daily during sittings.
- **Access Method:** Web portal / PDF downloads.
- **Licence & Reuse Terms:** Official e-Governance Portal (Free public access).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Daily notices are published by date; bulk export is not provided.
- **Application Requirement Satisfied:** Enables tracking of official assembly notices and real-time legislative member participation.

---

### Category 3: Representative Local Infrastructure & Constituency Works (MLACDS & MPLADS)

#### Entry `SRC-WRK-001`: Tamil Nadu Rural Development — MLACDS State Scheme Guidelines & Disbursals
- **Publisher:** Rural Development and Panchayat Raj Department, Government of Tamil Nadu
- **Exact Verified URL:** `https://tnrd.tn.gov.in/` (Navigate: *State Schemes > MLA Constituency Development Scheme*)
- **Civic Subject Covered:** Annual fund allocations (₹3.00 Cr/constituency), statutory guidelines, permissible and non-permissible works, mandatory 22% SC/ST earmarks, and district-level administrative sanction orders.
- **Geographic Coverage:** All 234 Assembly Constituencies in Tamil Nadu.
- **Date Range & Frequency:** Updated annually via Government Orders (G.O. Ms).
- **Access Method:** PDF guidelines, administrative circulars, and periodic status reports.
- **Licence & Reuse Terms:** Official Government Scheme Records.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Granular work-level contractor/tender disbursals reside with District Collectors / DRDA accounts rather than a single unified open database.
- **Application Requirement Satisfied:** Populates `constituency_works` and resolves MLACDS tracking in `backend/services/constituency_works.py`.

---

#### Entry `SRC-WRK-002`: Ministry of Statistics & Programme Implementation — MPLADS Portal
- **Publisher:** Ministry of Statistics and Programme Implementation (MoSPI), Government of India
- **Exact Verified URL:** `https://mplads.gov.in/`
- **Civic Subject Covered:** Member of Parliament Local Area Development Scheme (MPLADS) work-level recommendations, sanctions, expenditures, and asset completion registers for Tamil Nadu's 39 Lok Sabha and 18 Rajya Sabha MPs.
- **Geographic Coverage:** Tamil Nadu (39 Parliamentary Constituencies).
- **Date Range & Frequency:** 16th, 17th, and 18th Lok Sabha (Continuous live data).
- **Access Method:** Web portal, HTML tables, downloadable work lists.
- **Licence & Reuse Terms:** Government Open Data / Ministry Public Portal.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Portal structure changed during recent portal modernization; requires parsing work-level tables.
- **Application Requirement Satisfied:** Enables comparative representative infrastructure benchmarking.

---

### Category 4: Elections, Candidates & Constituency Electoral Data

#### Entry `SRC-ELC-001`: Election Commission of India (ECI) Results Portal
- **Publisher:** Election Commission of India (ECI)
- **Exact Verified URL:** `https://results.eci.gov.in/` (Historical and General Elections: `https://eci.gov.in/statistical-report/statistical-reports/`)
- **Civic Subject Covered:** Assembly and Parliamentary election results, constituency-wise candidate votes, margins of victory, NOTA counts, voter turnout percentages, and Form-20 booth-level statistics.
- **Geographic Coverage:** Tamil Nadu (234 Assembly Constituencies, 39 Parliamentary Constituencies).
- **Date Range & Frequency:** 1967 to 2024 (Updated post-election cycle).
- **Access Method:** HTML constituency pages, downloadable PDF Statistical Reports, and Form 20 tables.
- **Licence & Reuse Terms:** Official Statutory Election Data (Election Commission of India).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Bulk CSV downloads for Form 20 are published state-by-state on Chief Electoral Officer portals rather than in a single national API.
- **Application Requirement Satisfied:** Fulfills the currently empty `elections` and `constituencies` tables.

---

#### Entry `SRC-ELC-002`: Chief Electoral Officer (CEO) Tamil Nadu Portal
- **Publisher:** Office of the Chief Electoral Officer, Tamil Nadu
- **Exact Verified URL:** `https://www.elections.tn.gov.in/`
- **Civic Subject Covered:** Detailed Narrative Reports (e.g. TNLA 2016 Narrative Report - 528 pages, TNLA 2021 Compendium), Form 20 final result sheets by polling station, electoral rolls summary, and candidate affidavits (Form 26).
- **Geographic Coverage:** Tamil Nadu (Statewide, District-wise, AC-wise).
- **Date Range & Frequency:** 2011, 2016, 2021 Assembly and 2019, 2024 Parliamentary elections.
- **Access Method:** PDF downloads, HTML archives.
- **Licence & Reuse Terms:** Official Public Records under Representation of the People Act, 1951.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Domain occasionally rate-limits automated web scrapers.
- **Application Requirement Satisfied:** Candidate biographical facts, legal declarations, and election metadata.

---

### Category 5: Political Funding, Party Accounts & Campaign Finance

#### Entry `SRC-FND-001`: ECI Integrated Election Expenditure Monitoring System (IEMS) / Political Parties Portal
- **Publisher:** Election Commission of India
- **Exact Verified URL:** `https://iems.eci.gov.in` and `https://eci.gov.in/candidate-political-party/political-party/`
- **Civic Subject Covered:** Contribution Reports (Form 24A detailing individual and corporate donations >₹20,000), Annual Audited Accounts (balance sheets, income/expenditure statements), and Election Expenditure Statements.
- **Geographic Coverage:** State parties registered in Tamil Nadu (DMK, AIADMK, PMK, MDMK, NTK, DMDK) and recognized national parties.
- **Date Range & Frequency:** FY 2015-16 to FY 2024-25 (Annual filings mandated by statutory deadlines).
- **Access Method:** PDF downloads of scanned statutory filings.
- **Licence & Reuse Terms:** Statutory Public Disclosures under Section 29C of Representation of the People Act, 1951.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Small cash donations below ₹20,000 are not individualized; documents are scanned PDFs requiring OCR.
- **Application Requirement Satisfied:** Solves Phase 5 database population for `contributions`, `party_financial_statements`, and `donors`.

---

#### Entry `SRC-FND-002`: ECI Political Finance Transparency Portal
- **Publisher:** Election Commission of India
- **Exact Verified URL:** `https://transparency.eci.gov.in/`
- **Civic Subject Covered:** Searchable digital disclosures for political party contribution reports, annual accounts, and election expenses.
- **Geographic Coverage:** India & Tamil Nadu.
- **Date Range & Frequency:** FY 2021-22 onwards.
- **Access Method:** Web search and downloadable PDF reports.
- **Licence & Reuse Terms:** Public Statutory Records.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Newly deployed system; historical archives prior to 2021 remain on the legacy ECI portal.
- **Application Requirement Satisfied:** Provides modern digital filings for ongoing campaign finance cross-validation.

---

#### Entry `SRC-FND-003`: Ministry of Corporate Affairs — MCA-21 Electoral Trust Filings
- **Publisher:** Ministry of Corporate Affairs (MCA), Government of India
- **Exact Verified URL:** `https://www.mca.gov.in/` (Company Search / Annual Returns under Electoral Trusts Scheme, 2013)
- **Civic Subject Covered:** Annual contribution and disbursement reports of registered Electoral Trusts (e.g. Prudent Electoral Trust, Samaj Electoral Trust), linking corporate donors to party beneficiaries.
- **Geographic Coverage:** Corporate donors and political beneficiaries in Tamil Nadu and India.
- **Date Range & Frequency:** Annual filings (Financial years 2013-14 to 2024-25).
- **Access Method:** PDF filings via MCA-21 company registry.
- **Licence & Reuse Terms:** Statutory corporate disclosure under the Companies Act, 2013.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Corporate filings require CIN (Corporate Identity Number) lookup.
- **Application Requirement Satisfied:** Populates `electoral_trusts` in `backend/models/funding.py`.

---

### Category 6: Citizen Grievances, Service Standards & Administrative SLAs

#### Entry `SRC-GRV-001`: Mudhalvarin Mugavari (CM Helpline 1100)
- **Publisher:** Special Officer, Mudhalvarin Mugavari Department & Tamil Nadu e-Governance Agency (TNeGA)
- **Exact Verified URL:** `https://cmhelpline.tnega.org/`
- **Civic Subject Covered:** Integrated public grievance redressal covering 14 civic and departmental domains (revenue, roads, drinking water, electricity, welfare pensions, civil supplies).
- **Geographic Coverage:** Tamil Nadu (All 38 Districts).
- **Date Range & Frequency:** 2021 to Present (Continuous operational grievance lifecycle).
- **Access Method:** Web portal, 1100 helpline, citizen dashboard. (Bulk public access requires anonymized departmental export).
- **Licence & Reuse Terms:** Public Governance System. Under DPDPA 2023, individual citizen complaints cannot be ingested without strict PII redaction.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Direct database access requires institutional memorandum or open data feed; individual petition tracking requires citizen OTP.
- **Application Requirement Satisfied:** Supplies ground-truth civic issue taxonomies and resolution time benchmarks for `civic_issues` and `grievance_records`.

---

#### Entry `SRC-GRV-002`: Greater Chennai Corporation (GCC) 1913 Public Grievance Redressal System (PGRS)
- **Publisher:** Greater Chennai Corporation (GCC)
- **Exact Verified URL:** `https://chennaicorporation.gov.in/` (Dedicated Portal: `https://gccservices.in/pgr/pgr.php`)
- **Civic Subject Covered:** Urban municipal grievances: solid waste management, stormwater drain blocks, road potholes, street lights, vector control, and public health complaints.
- **Geographic Coverage:** Greater Chennai Corporation (15 Zones, 200 Municipal Wards).
- **Date Range & Frequency:** Daily live complaints (24x7 control room via 1913).
- **Access Method:** Web portal, Namma Chennai Mobile App, daily status trackers.
- **Licence & Reuse Terms:** Municipal Public Records (Subject to citizen privacy safeguards).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** API endpoints are internal; public status is queried by grievance token.
- **Application Requirement Satisfied:** Powers ward-level hotspot clustering in [`civic_analytics_service.py`](file:///backend/services/civic_analytics_service.py).

---

#### Entry `SRC-SLA-001`: Tamil Nadu Citizen's Charters
- **Publisher:** Personnel and Administrative Reforms Department, Government of Tamil Nadu
- **Exact Verified URL:** `https://ar.tn.gov.in/` and `https://www.tn.gov.in/charters/`
- **Civic Subject Covered:** Statutory service turnaround times, service level agreements (SLAs), designated appellate officers, and fee schedules across state departments (e.g. CMWSSB, TANGEDCO, Revenue, Transport).
- **Geographic Coverage:** Tamil Nadu (Statewide).
- **Date Range & Frequency:** Published departmental charters (Periodic statutory updates).
- **Access Method:** Downloadable PDF Charters.
- **Licence & Reuse Terms:** Statutory Public Commitments.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Published as departmental booklets; requires extracting SLA matrices into structured tables.
- **Application Requirement Satisfied:** Directly populates `service_standards` and defines SLA breach alerting thresholds in [`backend/api/civic.py`](file:///backend/api/civic.py).

---

### Category 7: Official Audit, State Finances & Actual Expenditure Reconciliation

#### Entry `SRC-AUD-001`: Comptroller & Auditor General (CAG) of India — State Finances Audit Reports
- **Publisher:** Comptroller and Auditor General of India (`cag.gov.in`) & Principal Accountant General (Audit), Tamil Nadu
- **Exact Verified URL:** `https://cag.gov.in/en/audit-report` (Tamil Nadu State Reports)
- **Civic Subject Covered:** Independent constitutional audit of state finances, Chapter 2 (Budgetary Management), audited Actual Expenditures (AE) vs Revised Estimates (RE), Direct Benefit Transfer (DBT) scheme evaluations, and compliance audits.
- **Geographic Coverage:** Tamil Nadu (Statewide).
- **Date Range & Frequency:** Annual Reports tabled in the Legislative Assembly (e.g. Report No. 2 of 2025 tabled October 17, 2025).
- **Access Method:** Complete PDF Reports and audit chapters.
- **Licence & Reuse Terms:** Constitutional Audit Document (Article 151 of the Constitution of India). Free public access.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21 (Verified Report No. 2 of 2025 for FY 2023-24).
- **Known Limitations:** Tabled with a 1-year audit reconciliation lag.
- **Application Requirement Satisfied:** Converts RE allocations into verified Actual Expenditures (AE) for Phase 1 and Phase 10 budget execution services.

---

### Category 8: Policy Outcome Evaluation, Baseline Indicators & Research Monographs

#### Entry `SRC-POL-001`: Tamil Nadu State Planning Commission (TNSPC) Evaluation Studies
- **Publisher:** Tamil Nadu State Planning Commission (TNSPC), Government of Tamil Nadu
- **Exact Verified URL:** `https://spc.tn.gov.in/`
- **Civic Subject Covered:** Empirical policy evaluation studies, household surveys, baseline-vs-endline evaluations of welfare schemes (*Illam Thedi Kalvi*, *Chief Minister's Breakfast Scheme*, *Pudhumai Penn*, *Kalaignar Magalir Urimai Thogai*), and Sustainable Development Goal (SDG) indicator monitoring.
- **Geographic Coverage:** Tamil Nadu (Statewide and district sample cohorts).
- **Date Range & Frequency:** Published research monographs (2021 to 2026).
- **Access Method:** Downloadable Research PDFs and Policy Papers.
- **Licence & Reuse Terms:** Official Government Research & Policy Evaluation.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21 (Matched against Phase 10 evaluation studies in DB).
- **Known Limitations:** Observational and descriptive cohort studies; non-causal guardrails must be maintained.
- **Application Requirement Satisfied:** Populates `evaluation_studies`, `policy_indicators`, and `indicator_observations` in [`backend/models/policy_evaluation.py`](file:///backend/models/policy_evaluation.py).

---

### Category 9: State Macro Statistics, District Income & Demographics

#### Entry `SRC-STA-001`: Department of Economics and Statistics (DES) Tamil Nadu — Statistical Publications
- **Publisher:** Department of Economics and Statistics (DES), Government of Tamil Nadu
- **Exact Verified URL:** `https://des.tn.gov.in/`
- **Civic Subject Covered:** Statistical Hand Book of Tamil Nadu, District Income Estimates (NDDP at current and constant prices, base year 2011-12), Estimates of State Domestic Product (GSDP), Season and Crop Reports, and Tamil Nadu at a Glance.
- **Geographic Coverage:** Tamil Nadu (Statewide and all 38 Districts).
- **Date Range & Frequency:** Annual publications (Series spanning 2011-12 to 2024-25).
- **Access Method:** PDF publications and HTML tabular data.
- **Licence & Reuse Terms:** Official Statistical Publications (DES GoTN).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** District income figures for recent years are categorized as "provisional" pending final economic census reconciliation.
- **Application Requirement Satisfied:** Powers district-level normalization in `development_indicators` and `policy_evaluation_district_statistics.csv`.

---

#### Entry `SRC-STA-002`: Tamil Nadu Open Government Data Portal (`tn.data.gov.in`)
- **Publisher:** National Informatics Centre (NIC) & Tamil Nadu e-Governance Agency (TNeGA)
- **Exact Verified URL:** `https://tn.data.gov.in/`
- **Civic Subject Covered:** Machine-readable public catalogs across education (UDISE school stats), health infrastructure, vehicle registrations, agricultural land use, and public transport operations.
- **Geographic Coverage:** Tamil Nadu.
- **Date Range & Frequency:** Periodic departmental uploads.
- **Access Method:** Machine-readable CSV, JSON, XML, and XLS downloads; metadata APIs.
- **Licence & Reuse Terms:** **Government Open Data License - India (GODL)**. Permitted for commercial and non-commercial reuse with attribution.
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Departmental catalog update intervals vary; granular scheme-by-scheme budget ledgers are rarely provided in bulk.
- **Application Requirement Satisfied:** Supplies machine-readable demographic and institutional baseline metrics.

---

### Category 10: Geographic Administrative Boundaries & Spatial Hierarchies

#### Entry `SRC-GEO-001`: Ministry of Panchayati Raj — Local Government Directory (LGD)
- **Publisher:** Ministry of Panchayati Raj, Government of India
- **Exact Verified URL:** `https://lgdirectory.gov.in/`
- **Civic Subject Covered:** Authoritative standard location codes (LGD Codes) for all administrative tiers in Tamil Nadu: 38 Districts, 310+ Taluks, 388 Development Blocks, 12,525 Village Panchayats, 21 Municipal Corporations, 138 Municipalities, 490 Town Panchayats, and mapped urban/rural wards.
- **Geographic Coverage:** Tamil Nadu (100% administrative hierarchy).
- **Date Range & Frequency:** Continuous statutory updates reflecting government reorganization notifications.
- **Access Method:** Direct Excel, CSV, and PDF directory downloads.
- **Licence & Reuse Terms:** Central Government e-Governance Standard (Open public access).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Provides alphanumeric codes and parent-child hierarchy; does not host GIS polygon shapefiles.
- **Application Requirement Satisfied:** Fulfills `administrative_areas` and standardizes geographic entity resolution in [`civic_mapping_service.py`](file:///backend/services/civic_mapping_service.py).

---

#### Entry `SRC-GEO-002`: Survey of India / Tamil Nadu Urban Local Body Boundary Portal
- **Publisher:** Survey of India & Directorate of Town and Country Planning (DTCP), Tamil Nadu
- **Exact Verified URL:** `https://surveyofindia.gov.in/` and OpenCity Tamil Nadu Geodata Archive (`https://opencity.in/`)
- **Civic Subject Covered:** GIS spatial vector boundaries (GeoJSON / ESRI Shapefile) for Assembly Constituencies (Delimitation 2008), Corporation Wards, and Revenue Taluks.
- **Geographic Coverage:** Tamil Nadu (Statewide and major urban corporations).
- **Date Range & Frequency:** Delimitation 2008 boundaries (Updated post-urban local body expansions).
- **Access Method:** Downloadable GeoJSON / SHP files.
- **Licence & Reuse Terms:** National Geospatial Policy 2022 / Creative Commons Attribution for OpenCity derivatives.
- **Source Classification:** **Primary / Curated Secondary GIS**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** Newly expanded peri-urban corporation wards (Tambaram, Avadi) lack unified single-file open shapefiles.
- **Application Requirement Satisfied:** Enables spatial polygon intersection for constituency-to-ward grievance mapping.

---

### Category 11: Government Orders (G.O.s) & Statutory Gazettes

#### Entry `SRC-GOV-001`: Tamil Nadu Government Orders (G.O.) Search Portal
- **Publisher:** Tamil Nadu e-Governance Agency (TNeGA) & Information Technology Department
- **Exact Verified URL:** `https://www.tn.gov.in/gorders` (and departmental archives via `cms.tn.gov.in`)
- **Civic Subject Covered:** Statutory Government Orders (G.O. Ms, G.O. Rt) sanctioning welfare schemes, administrative guidelines, fund sanctions, and public appointments across all government departments.
- **Geographic Coverage:** Tamil Nadu.
- **Date Range & Frequency:** 2000 to Present (Updated daily as orders are notified).
- **Access Method:** Web search by Department, G.O. number, and year; downloadable PDF orders.
- **Licence & Reuse Terms:** Official Government Orders (Public records).
- **Source Classification:** **Primary Source**
- **Verification Date:** 2026-10-21.
- **Known Limitations:** No automated bulk REST API; requires targeted query retrieval by G.O. identifier.
- **Application Requirement Satisfied:** Serves as the ultimate evidentiary anchor for political claim verification (Phase 7) and promise fulfillment (Phase 3).

---

## 4. Auxiliary & Curated Secondary Sources

The following sources provide valuable secondary research, academic benchmarking, or media synthesis. They are strictly classified as **Secondary Sources** and are used only to cross-check primary records:

| Source ID | Publisher & Source Name | Exact Verified URL | Civic Scope | Source Type | Recommended Use in CIVICLENS |
| :--- | :--- | :--- | :--- | :---: | :--- |
| **SRC-AUX-001** | **PRS Legislative Research — Tamil Nadu State Budget & Assembly Track** | `https://prsindia.org/budgets/states/tamil-nadu` | State budget summaries, macro fiscal trends, and legislative performance briefs. | **Secondary Research** | Used to cross-check macro fiscal ratios (GSDP deficit percentages) and assembly question trends. |
| **SRC-AUX-002** | **Trivedi Centre for Political Data (TCPD) — LokDhaba & Incumbency Archive** | `https://lokdhaba.ashoka.edu.in/` | Candidate-level historical election statistics for Tamil Nadu assembly elections (1962–2021). | **Academic Dataset** | Provides standardized historical politician identifiers for candidate disambiguation. |
| **SRC-AUX-003** | **Association for Democratic Reforms (ADR) / National Election Watch** | `https://adrindia.org/` and `https://myneta.info/` | Candidate asset affidavits, criminal case disclosures, and political party financial analysis. | **Secondary Aggregator** | Benchmarking party funding analysis; primary citations must remain ECI Form 24A and Form 26. |
| **SRC-AUX-004** | **Regional Media Houses (The Hindu, Dinamalar, Daily Thanthi, DT Next)** | Cataloged in [`config/news_sources.json`](file:///config/news_sources.json) (44 publishers) | Bilingual regional news coverage, political statements, and ground reporting. | **Media Source** | Used solely within the Phase 4 Framing & Bias Indicator Engine. Excluded from factual budget or legislative ground truth. |

---

## 5. Unverified & Excluded Sources (Automated Ingestion Prohibited)

In compliance with the project's epistemic discipline, the following data sources are **explicitly excluded from automated ingestion**:

1. **Unauthenticated Social Media Scrapers (X / YouTube):**
   - *Reason:* Scraping endpoints without authenticated enterprise API keys (`X_BEARER_TOKEN`, `YOUTUBE_API_KEY`) violates platform Terms of Service and generates non-deterministic, rate-limited results.
   - *Status:* **Excluded from automated production pipeline.** Test harnesses must continue using cryptographically hashed offline fixtures in `data/raw/x_scrapes/`.
2. **Proprietary Paywalled Data Compilers (e.g. Indiastat):**
   - *Reason:* Third-party paywalled portals restrict automated redistribution, and their underlying primary sources (DES, ECI, MoSPI) can be acquired directly.
   - *Status:* **Excluded.**
3. **Internal Departmental Call Center Databases:**
   - *Reason:* Unredacted call logs contain citizen phone numbers, Aadhaar numbers, and residential addresses protected under DPDPA 2023.
   - *Status:* **Excluded from public ingestion**; only officially published, anonymized statistical summaries from TNeGA may be imported.
4. **Third-Party Politician "Ranking" or "Integrity Score" Websites:**
   - *Reason:* Subjective scoring violates the non-partisan epistemic guardrails documented in [`docs/DATA_SOURCES_AND_LIMITATIONS.md`](file:///docs/DATA_SOURCES_AND_LIMITATIONS.md).
   - *Status:* **Strictly Prohibited.**

---

## 6. Sourcing & Ingestion Feasibility Matrix

| Registry ID | Primary Source Name | Ingestion Method | File Format | Technical Feasibility & Required Tooling | Priority Level |
| :--- | :--- | :--- | :---: | :--- | :---: |
| `SRC-FND-001` | ECI Political Funding (Batch B02) | Local CSV Import | CSV | **Immediate (No network needed).** Fix relative path in [`scripts/import_phase5_real_data.py`](file:///scripts/import_phase5_real_data.py). | **P0 (Sprint Ready)** |
| `SRC-GRV-001` | Live Grievance Store | JSON Loader | JSON | **Immediate (No network needed).** Seed `civic_issues` from existing `data/raw/phase8/.../phase8_live_store.json`. | **P0 (Sprint Ready)** |
| `SRC-GEO-001` | Local Government Directory (LGD) | Bulk File Download | Excel / CSV | **High.** Download statewide directory for Tamil Nadu; populate `administrative_areas`. | **P1 (High)** |
| `SRC-SLA-001` | Tamil Nadu Citizen's Charters | Structured Extraction | PDF | **High.** Extract statutory SLA tables across 14 municipal departments into `service_standards`. | **P1 (High)** |
| `SRC-LEG-001` | TNLA Digital Debates & Questions | Web Crawler / OCR | PDF / HTML | **Medium.** Target unstarred question sessions; parse tabular MLA activity metrics into SQLite. | **P2 (Medium)** |
| `SRC-AUD-001` | CAG State Finances Audit Reports | PDF Table Parsing | PDF | **Medium.** Ingest Chapter 2 tables from Report No. 2 of 2025 to update AE expenditures. | **P2 (Medium)** |
| `SRC-WRK-001` | MLACDS Work Disbursals | PDF Extraction | PDF | **Medium.** Parse DRDA sanction orders for priority constituencies (Kolathur, Edappadi, Chepauk). | **P2 (Medium)** |

---

## 7. Actionable Roadmap for Data Ingestion

To transition CIVICLENS TN from curated fallbacks to full statewide production coverage without introducing unverified data or breaking existing tests:

```mermaid
flowchart LR
    S1[Step 1: Local Data Activation] --> S2[Step 2: Standards & Geography]
    S2 --> S3[Step 3: Legislative & Works Ingestion]
    S3 --> S4[Step 4: Continuous Audit & Evaluation]

    subgraph Step 1
        S1A[Update import_phase5 path to batch_b02]
        S1B[Seed claims from real_claims_integrated.json]
        S1C[Seed civic issues from phase8_live_store.json]
    end

    subgraph Step 2
        S2A[Import LGD Tamil Nadu codebook]
        S2B[Populate 14-domain Citizen's Charter SLAs]
    end

    subgraph Step 3
        S3A[Ingest TNLA assembly questions for 234 ACs]
        S3B[Ingest MLACDS DRDA disbursal logs]
    end

    subgraph Step 4
        S4A[Ingest CAG 2023-24 Finance Accounts]
        S4B[Ingest TNSPC 2024 Policy Monographs]
    end
```

1. **Step 1: Activate Existing In-Repository Data (Immediate / Offline):**
   - Correct the hardcoded absolute path in [`scripts/import_phase5_real_data.py`](file:///scripts/import_phase5_real_data.py) to target `data/raw/political_funding/batch_b02`.
   - Ingest `data/raw/phase7/real_claims_integrated.json` and `data/raw/phase8/extracted/dataset/datasets/phase8_live_store.json` into SQLite to populate the 8 funding, 15 claim, and 15 civic issue tables.
2. **Step 2: Seed Geographic Standards & Statutory SLAs (Short-Term):**
   - Import the official LGD Tamil Nadu directory (`SRC-GEO-001`) into `administrative_areas` to establish canonical district, taluk, block, and ward codes.
   - Transcribe statutory Citizen's Charter turnaround SLAs (`SRC-SLA-001`) into `service_standards` across all 14 civic categories.
3. **Step 3: Ingest Legislative & Local Public Works Records (Mid-Term):**
   - Ingest starred/unstarred legislative questions from the Assembly Digital Archive (`SRC-LEG-001`) to activate legislative profiles across all 234 MLAs.
   - Aggregate MLACDS sanction and expenditure registers (`SRC-WRK-001`) from District Collectorates to populate `constituency_works`.
4. **Step 4: Reconcile Audited Actuals & Outcome Longitudinal Panels (Ongoing):**
   - Update `budget_records` with CAG Audited Actuals (`SRC-AUD-001`) for FY 2023-24 once finalized.
   - Expand `indicator_observations` in Phase 10 using newly published TNSPC evaluation monographs (`SRC-POL-001`) to transition 2-point static snapshots into multi-year longitudinal impact curves.
