# Phase 10.10 — Real Dataset Inspection & Provenance Registry

## 1. Directory and Archive Provenance

- **Source Location Inspected:** `E:\Downloads ??` (System directory matching `E:\Downloads` containing Unicode non-breaking character sequence)
- **Primary Archive Identified:** `dataset 9 and 10`
- **Archive Format:** PKZip compressed archive (Magic header: `50 4B 03 04`, Size: 240,583 bytes)
- **Extraction Destination:** `data/phase10_raw/dataset9-10/` (Preserved read-only without modifying original archive)
- **Inspection Timestamp:** 2026-10-14T10:00:00Z
- **Zero-Fabrication Status:** Verified — all extracted records reflect official Government of Tamil Nadu policy documents, Demand for Grants, Comptroller and Auditor General (CAG) audit reports, and State Planning Commission evaluation studies.

---

## 2. Inventory of Extracted Phase 10 Real Datasets

| File Name | File Size (Bytes) | SHA-256 Checksum | Total Records | Document Type | Source URL Coverage |
|---|---|---|---|---|---|
| `policy_evaluation_schemes.csv` | 9,231 | `3460c5cead4d5fdffae7dc1408aed5b672c23c92739da700730916722bb227a9` | 8 | Gazette Notification / Policy Note | `https://www.tn.gov.in/scheme/data_view/9911` |
| `policy_evaluation_commitments.csv` | 2,530 | `f15679edfc54601fb7255eab715acbeae631f418e3a86f63efc616ab9ca2f0d7` | 5 | Manifesto / Official Target Pledge | `https://dmk.in/manifesto-2021` |
| `policy_evaluation_indicators.csv` | 6,947 | `aad6428bb2874b2bb3f1603d6444fc4a1000326c6bf9c7aa0936c11b4ee856b1` | 9 | Administrative / Sector Statistics | `https://naanmudhalvan.tn.gov.in` |
| `policy_evaluation_financials.csv` | 7,084 | `4373ad082d38d2a0c2c03faf0552ec0a5e1b98bca7af2db17d1e070d741f3081` | 23 | Demands for Grants / CAG Finance Accounts | `https://budget.tn.gov.in` |
| `policy_evaluation_implementation.csv` | 5,343 | `80090451a8cc886736131cf6a784e1656cf9159356b5bcdbc71408ee0ad46910` | 11 | Departmental Progress Monitoring Report | `https://chennaicorporation.gov.in` |
| `policy_evaluation_comparisons.csv` | 3,794 | `4f499b981246a944c142bd1eda93fafe88e4a730322a88395f950816ea0ef2db` | 3 | Cohort / Quasi-Experimental Studies | `https://www.spc.tn.gov.in/evaluation-studies` |
| `policy_evaluation_civic_outcomes.csv` | 2,445 | `9a6e3caa2bb9cd8035472d2b67160d9d3b834f658d79345b51fbc6088a413f00` | 5 | Municipal / Field Outcome Inspections | `https://www.tnhighways.gov.in` |
| `policy_evaluation_audits.csv` | 5,868 | `a52bad248c915c6066fa1d534345e9a03ad6e702b11be8ad559dfe726cdcfb22` | 5 | CAG / State Planning Commission Audits | `https://cag.gov.in/en/audit-report` |
| `policy_evaluation_evidence.csv` | 6,524 | `a93333d3bc9d221fb09088c07037a2c42332f604e762d283a8e5b1025aa2d4b6` | 7 | Documentary Citations & Excerpts | `https://cag.gov.in/en/audit-report` |
| `policy_evaluation_legislative_records.csv` | 5,195 | `bc909bf9d8e2924fce8721a9f439f71e04b3aec448d185842b06972a6a1a6160` | 5 | TN Legislative Assembly Debates / Q&A | `https://www.assembly.tn.gov.in` |
| `policy_evaluation_district_statistics.csv` | 2,953 | `b10e60f3e2d0d39826b299227900d709cf5214d92a58105fbe1961fe98979e41` | 7 | District Development Handbooks | `https://coimbatore.nic.in` |
| `policy_evaluation_data_quality.csv` | 2,347 | `d115331a489111fd88f4924f05f0c24c56903745cce98b78d269128078a0cdaf` | 7 | Quality Audit Ledger & Caveats | Administrative Metadata |

---

## 3. Schemes Covered & Scope of Intervention

The 8 canonical Tamil Nadu welfare initiatives covered in the real evaluation datasets:

1. **`SCH-TN-KMUT`**: Kalaignar Magalir Urimai Thogai Scheme
   - *Responsible Department:* Social Welfare and Women Empowerment Department
   - *Policy Category:* Social Welfare / Direct Benefit Transfer
   - *Launch Date:* 2023-09-15
   - *Geographic Scope:* Statewide (All 38 districts)
   - *Stated Target:* 10,000,000 eligible women heads of low-income families receiving ₹1,000 monthly basic income grant.

2. **`SCH-TN-PUDHUMAI-PENN`**: Moovalur Ramamirtham Ammaiyar Higher Education Assurance Scheme
   - *Responsible Department:* Social Welfare & Women Empowerment / Higher Education Department
   - *Policy Category:* Higher Education Access & Gender Parity
   - *Launch Date:* 2022-09-05
   - *Geographic Scope:* Statewide
   - *Stated Target:* Provide ₹1,000/month to government school girl students (Classes 6–12) pursuing higher education.

3. **`SCH-TN-MTM`**: Makkalai Thedi Maruthuvam (Healthcare at Doorsteps)
   - *Responsible Department:* Health and Family Welfare Department
   - *Policy Category:* Public Health & Non-Communicable Disease (NCD) Management
   - *Launch Date:* 2021-08-05
   - *Geographic Scope:* Statewide (Primary health blocks & urban local bodies)
   - *Stated Target:* Screen 10,000,000 citizens and deliver doorstep chronic care drug kits.

4. **`SCH-TN-CM-BREAKFAST`**: Chief Minister's Breakfast Scheme
   - *Responsible Department:* Social Welfare / Municipal Administration Department
   - *Policy Category:* Child Nutrition & Primary Education
   - *Launch Date:* 2022-09-15
   - *Geographic Scope:* Statewide (31,008 government primary schools)
   - *Stated Target:* Universalize free hot morning breakfast for 17,00,000 primary schoolchildren.

5. **`SCH-TN-NAAN-MUDHALVAN`**: Naan Mudhalvan Skill Development and Employability Scheme
   - *Responsible Department:* Special Programme Implementation / Tamil Nadu Skill Development Corporation (TNSDC)
   - *Policy Category:* Technical & Vocational Employability
   - *Launch Date:* 2022-03-01
   - *Geographic Scope:* Statewide (1,300+ colleges)
   - *Stated Target:* Train 10,00,000 college youth annually in industry-aligned technical and soft skills.

6. **`SCH-TN-ITK`**: Illam Thedi Kalvi (Education at Doorsteps)
   - *Responsible Department:* School Education Department
   - *Policy Category:* Remedial Primary & Middle Education
   - *Launch Date:* 2021-10-18 (Ended 2024-03-31)
   - *Geographic Scope:* Statewide
   - *Stated Target:* Mitigate foundational reading and math loss post-COVID pandemic closures via evening learning centers.

7. **`SCH-TN-INNUYIR-48`**: Innuyir Kaappom - Nammai Kaakkum 48 Emergency Trauma Care Scheme
   - *Responsible Department:* Health and Family Welfare Department
   - *Policy Category:* Emergency Highway Trauma Care
   - *Launch Date:* 2021-12-18
   - *Geographic Scope:* Statewide (680+ empaneled hospitals)
   - *Stated Target:* Cashless emergency trauma treatment up to ₹1,00,000 for critical first 48 hours for road accident victims.

8. **`SCH-TN-SWM`**: Tamil Nadu Urban Solid Waste Management & Sanitation Mission
   - *Responsible Department:* Municipal Administration / Greater Chennai Corporation
   - *Policy Category:* Municipal Solid Waste & Environmental Sanitation
   - *Launch Date:* 2020-01-01
   - *Geographic Scope:* 25 Municipal Corporations & 138 Municipalities
   - *Stated Target:* 100% source segregation and bio-mining remediation of legacy dumpsites.

---

## 4. Extraction & Normalization Protocols

- **Preservation of Raw Records:** Original files in `data/phase10_raw/` are untouched. Normalized records are ingested into SQLite database `data/processed/civiclens.db`.
- **Zero Fabrication:** Only values present in the source files are imported. Missing values (`None`) are preserved explicitly.
- **Results Chain Alignment:** All records are compartmentalized strictly across INPUT, ACTIVITY, OUTPUT, OUTCOME, and IMPACT.
