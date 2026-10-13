# CIVICLENS TN — Phase 8.10: Real Dataset Inspection Report

**Generated:** October 13, 2026  
**System:** CIVICLENS TN (Public Accountability & Civic Intelligence Platform)  
**Inspection Target Directory:** `E:\Downloads` (located on host as `\\?\E:\Downloads 🔃` / Drive `E:\`)  
**Primary Dataset Target:** `dataset 7 and 8`  

---

## 1. Directory Inspection & Host Filesystem Audit

### 1.1 Filesystem Path Resolution
- The requested target directory `E:\Downloads` was inspected on the system.
- On the host Windows file system, the volume `E:\` contains the user's primary downloads folder named `Downloads 🔃` (`E:\Downloads 🔃`).
- Direct inspection identified the primary dataset archive: `dataset 7 and 8` (stored as an uncompressed/raw zip container without file extension).

### 1.2 Identified Archive Details
| Field | Value |
|---|---|
| **Original Filename** | `dataset 7 and 8` |
| **Physical Location** | `E:\Downloads 🔃\dataset 7 and 8` |
| **File Format** | ZIP Archive (PK Header) |
| **Size** | 2,434,765 bytes (~2.32 MB) |
| **SHA-256 Checksum** | `b87f17dbf825c8fdcf92b644f9f8d7e827c642507a13b41111c034d4e8b5f0e2` |
| **Preserved Destination** | `data/raw/phase8/dataset_7_and_8.zip` |
| **Extraction Path** | `data/raw/phase8/extracted/` |

---

## 2. Inventory of Available Documents & Datasets

Inspection of the archive identified **101 key documents and data files** across Phase 7 and Phase 8. The relevant Phase 8 candidate datasets include:

### 2.1 Public Works, Official References & Scheme Records
- **File:** `dataset/civiclens_phase4_datasets/official_references.csv` / `dataset/datasets/official_references.csv`
- **Format:** CSV (15,847 bytes, 35 rows)
- **Issuing Authorities:** Government of Tamil Nadu Gazettes, Press Information Bureau (PIB), Election Commission of India (ECI), Department of Information and Public Relations (DIPR), PRS Legislative Research.
- **Coverage:** Metro Rail Phase 1 & 2 expansions (Poonamallee–Vadapalani), Multi-Modal Logistics Parks (Mappedu), AIIMS Madurai, Tiruchirappalli International Airport New Terminal, Vande Bharat Express corridors.
- **Classification:** `REAL_RECORDS` (Primary statutory references & official releases).

### 2.2 Legislative Budget Allocations & Authenticated Speech Records
- **File:** `dataset/existing_verified_texts.json`
- **Format:** JSON (24,673 bytes, 8 authenticated transcripts)
- **Coverage:** Tamil Nadu General Budget 2026–27 (`CL-A-0001`), Tamil Nadu Agriculture Budget 2026–27 (`CL-A-0015`), Kuruvai Package canal desilting, TN-SHORE coastal and mangrove restoration, TN-VETRI rural infrastructure modernisation, and Road Safety Policy civil engineering redesign.
- **Classification:** `REAL_RECORDS` (Authenticated legislative transcripts).

### 2.3 Curated Civic News & Infrastructure Defects
- **Files:** `dataset/civiclens_phase4_datasets/news_articles.csv` (576,474 bytes, 212 rows), `dataset/scraped_expansion_articles.json` (430,741 bytes, 109 rows), `dataset/new_articles_scraped.json` (114,453 bytes, 31 rows)
- **Publishers:** The Hindu, Dinamani, Daily Thanthi, Dinamalar, Puthiya Thalaimurai, Maalaimalar, News18 Tamil.
- **Coverage:** Real civic events across Chennai, Coimbatore, Madurai, Tiruchirappalli, and Salem concerning Metro Rail execution, road safety conditions, and drainage systems.
- **Classification:** `REAL_RECORDS` (Secondary journalistic records).

### 2.4 Municipal Solid Waste Aggregate Statistics
- **File:** `dataset/datasets/phase8_live_store.json` (`aggregate_stats`)
- **Reporting Body:** Directorate of Municipal Administration / Greater Chennai Corporation (GCC).
- **Coverage:** Annual solid waste management metrics (2020–2024 daily collection tonnage: 346,750 TPD in 2020 to 419,750 TPD in 2024).
- **Classification:** `REAL_RECORDS` (Aggregated municipal performance indicators).

---

## 3. Missing Inputs & Explicit Non-Fabrication Declarations

In strict compliance with Phase 8 epistemic guidelines:

1. **Unredacted Individual Citizen Grievance Database Dumps (Unavailable):**
   - Direct raw citizen petition databases (such as internal exports from Mudhalvarin Mugavari / CM Helpline 1100 or GCC 1913 ticketing backends) are confidential government records protected under Indian privacy laws and the Digital Personal Data Protection Act (DPDPA) 2023.
   - **Zero simulated or fabricated individual citizen grievances were invented.** Aggregate statistics remain preserved strictly as aggregate development benchmarks (`GrievanceAggregateStat`).

2. **Standalone Shapefiles / GeoJSON GIS Layers (Not in Archive):**
   - GIS boundary Shapefiles were not included in `dataset 7 and 8`. Spatial mappings rely on the standardized Local Government Directory (LGD) codes and Tamil Nadu administrative boundaries cataloged in `backend/models/civic_issue.py`.

3. **External Website Harvesting Restrictions:**
   - No unauthorized web scraping bypassing CAPTCHAs, authenticated sessions, or terms of service was performed.
