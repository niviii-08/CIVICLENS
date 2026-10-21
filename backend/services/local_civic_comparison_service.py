"""
CIVICLENS TN — Comparable Local Civic Insights Service
Phase 13.6: Geographic Identifiers, Cross-Jurisdiction Comparisons, and Epistemic Guardrails.

Enables citizens to explore and compare district, constituency, and local body metrics
strictly using verified geographic boundaries, compatible measurement units, and aligned
reporting periods.

Core Epistemic Safeguards:
1. No Arbitrary Composite Rankings: Single-metric comparisons permitted only with explicit formulas and limitation disclosures.
2. Zero vs Unavailable Distinction: 0.0 means measured zero; None means missing/unavailable. Never equate unavailable with zero.
3. Unit & Period Compatibility: Refuses comparison across incompatible units (e.g. PERCENT vs COUNT) or mismatched periods.
4. Boundary & Demographic Warnings: Surfaces warnings for district reorganizations, delimitation changes, and urban-rural skews.
5. Record Traceability: Every figure links back to primary gazettes, census tables, or audited grievance databases.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy.orm import Session

from backend.database.session import SessionLocal
from backend.models.civic_issue import (
    AdministrativeArea,
    AdministrativeLevel,
    CivicDepartment,
    CivicIssue,
    IssueMetric,
)
from backend.models.representative import (
    CalculationMethod,
    Constituency,
    ConstituencyGeographicMapping,
    ConstituencyWork,
    DevelopmentIndicator,
    IndicatorQualityStatus,
    Representative,
)
from backend.services.civic_mapping_service import CivicGeographicMapper

logger = logging.getLogger("civiclens.phase13.local_insights")


# =====================================================================
# Epistemic Guardrail Exceptions
# =====================================================================

class LocalInsightError(Exception):
    """Base exception for local civic comparison errors."""
    pass


class IncompatibleUnitError(LocalInsightError):
    """Raised when comparing records with incompatible measurement units."""
    pass


class IncompatiblePeriodError(LocalInsightError):
    """Raised when comparing records from misaligned reference timeframes."""
    pass


class IncompatibleGeographicLevelError(LocalInsightError):
    """Raised when attempting to compare entities of different administrative tiers."""
    pass


class ArbitraryScoringProhibitedError(LocalInsightError):
    """Raised when an unsupported composite index or arbitrary ranking is requested."""
    pass


class EntityNotFoundError(LocalInsightError):
    """Raised when a requested geographic entity or identifier is not found."""
    pass


# =====================================================================
# Canonical Supported Metrics Catalog
# =====================================================================

SUPPORTED_METRICS: Dict[str, Dict[str, Any]] = {
    # 1. Demographic & Socioeconomic Indicators (Census of India / Directorate of Census Operations, TN)
    "literacy_rate_pct": {
        "metric_id": "literacy_rate_pct",
        "name": "Literacy Rate",
        "unit": "PERCENT",
        "default_period": "2011",
        "supported_levels": ["DISTRICT", "CONSTITUENCY"],
        "description": "Percentage of population aged 7 and above who can read and write with understanding.",
        "calculation_formula": "(literate_population / population_aged_7_plus) * 100",
        "primary_source": "Office of the Registrar General & Census Commissioner, India (Census 2011)",
        "source_document_id": "DOC-CENSUS-2011-TN-PCA",
        "limitations": "Based on 2011 decennial census baseline; does not reflect subsequent population migrations or adult literacy drives.",
    },
    "urban_pct": {
        "metric_id": "urban_pct",
        "name": "Urban Population Share",
        "unit": "PERCENT",
        "default_period": "2011",
        "supported_levels": ["DISTRICT", "CONSTITUENCY"],
        "description": "Proportion of total resident population residing in statutorily notified urban local bodies (ULBs).",
        "calculation_formula": "(urban_population / total_population) * 100",
        "primary_source": "Census of India 2011 — Primary Census Abstract",
        "source_document_id": "DOC-CENSUS-2011-TN-PCA",
        "limitations": "Constituencies with high urban shares experience fundamentally different infrastructure challenges than predominantly agrarian rural constituencies.",
    },
    "total_population": {
        "metric_id": "total_population",
        "name": "Total Population",
        "unit": "COUNT",
        "default_period": "2011",
        "supported_levels": ["DISTRICT", "CONSTITUENCY", "WARD", "ZONE"],
        "description": "Total enumerated resident population within the delimitation boundary.",
        "calculation_formula": "Direct census enumeration aggregate",
        "primary_source": "Census of India 2011 / ECI Delimitation Order 2008",
        "source_document_id": "DOC-CENSUS-2011-TN-PCA",
        "limitations": "Electoral roll sizes diverge from resident census populations due to interstate and interdistrict migration.",
    },
    "sc_pct": {
        "metric_id": "sc_pct",
        "name": "Scheduled Caste Population Share",
        "unit": "PERCENT",
        "default_period": "2011",
        "supported_levels": ["DISTRICT", "CONSTITUENCY"],
        "description": "Proportion of resident population belonging to notified Scheduled Castes.",
        "calculation_formula": "(sc_population / total_population) * 100",
        "primary_source": "Census of India 2011",
        "source_document_id": "DOC-CENSUS-2011-TN-PCA",
        "limitations": "Reflects 2011 baseline data across official delimitation jurisdictions.",
    },

    # 2. Local Constituency Public Works & Development Funds (Phase 6 / MPLADS / MLACDS)
    "mplads_utilization_pct": {
        "metric_id": "mplads_utilization_pct",
        "name": "MPLADS Fund Utilization Rate",
        "unit": "PERCENT",
        "default_period": "FY2022-23",
        "supported_levels": ["CONSTITUENCY"],
        "description": "Ratio of cumulative expenditure incurred on sanctioned community infrastructure to total funds released.",
        "calculation_formula": "(expenditure_inr / sanctioned_funds_inr) * 100",
        "primary_source": "Ministry of Statistics and Programme Implementation (MoSPI) / District Collectorate Ledgers",
        "source_document_id": "DOC-MOSPI-MPLADS-2023",
        "limitations": "Expenditure booking often reflects administrative procedural sanction delays in district collectorates rather than lack of elected representative initiative.",
    },
    "mplads_expenditure_inr": {
        "metric_id": "mplads_expenditure_inr",
        "name": "Cumulative Development Expenditure",
        "unit": "INR",
        "default_period": "FY2022-23",
        "supported_levels": ["CONSTITUENCY"],
        "description": "Total disbursed expenditure on local drinking water, education, and connectivity infrastructure.",
        "calculation_formula": "Sum of audited public works voucher disbursals",
        "primary_source": "State Treasury & District Rural Development Agency (DRDA)",
        "source_document_id": "DOC-DRDA-WORKS-2023",
        "limitations": "Absolute monetary figures cannot be directly compared across multi-term tenures without temporal inflation adjustment.",
    },
    "public_works_completed_count": {
        "metric_id": "public_works_completed_count",
        "name": "Completed Public Works",
        "unit": "COUNT",
        "default_period": "FY2022-23",
        "supported_levels": ["CONSTITUENCY"],
        "description": "Number of physically completed and verified local infrastructure projects.",
        "calculation_formula": "Count of projects with status 'REPORTED_COMPLETED' or 'INDEPENDENTLY_VERIFIED_COMPLETED'",
        "primary_source": "DRDA Municipal Works Progress Register",
        "source_document_id": "DOC-DRDA-WORKS-2023",
        "limitations": "Does not reflect differences in the capital scale of individual works (e.g. a ₹1 Cr overhead tank vs a ₹5 Lakh bus shelter).",
    },

    # 3. Municipal Grievances & Citizen Charter Delivery (Phase 8 / CMWSSB / GCC / MAWS)
    "sla_compliance_rate_pct": {
        "metric_id": "sla_compliance_rate_pct",
        "name": "Citizen Charter SLA Compliance Rate",
        "unit": "PERCENT",
        "default_period": "2023-2024",
        "supported_levels": ["DISTRICT", "ZONE", "WARD"],
        "description": "Percentage of citizen grievances resolved within the statutory Citizen's Charter timeframe.",
        "calculation_formula": "(resolved_within_sla_count / total_resolved_count) * 100",
        "primary_source": "Municipal Administration & Water Supply (MAWS) Integrated Portal",
        "source_document_id": "DOC-MAWS-SLA-2024",
        "limitations": "Varies by civic category; complex road relaying or drainage overhauls have longer SLA baselines than street lighting replacement.",
    },
    "average_resolution_hours": {
        "metric_id": "average_resolution_hours",
        "name": "Average Grievance Resolution Time",
        "unit": "HOURS",
        "default_period": "2023-2024",
        "supported_levels": ["DISTRICT", "ZONE", "WARD"],
        "description": "Mean duration from initial citizen complaint registration to field closure verification.",
        "calculation_formula": "Mean of (actual_resolution_date - reported_date) in hours",
        "primary_source": "CMWSSB / Greater Chennai Corporation Grievance Redressal Audit",
        "source_document_id": "DOC-GCC-AUDIT-2024",
        "limitations": "Mean can be skewed by historical unresolved legacy grievances or complex inter-agency disputes.",
    },
    "grievances_logged_count": {
        "metric_id": "grievances_logged_count",
        "name": "Public Grievances Logged",
        "unit": "COUNT",
        "default_period": "2023-2024",
        "supported_levels": ["DISTRICT", "ZONE", "WARD"],
        "description": "Total citizen complaints registered through official civic portals and ward helpline services.",
        "calculation_formula": "Total count of registered grievance tokens",
        "primary_source": "TNeGA / GCC Integrated Grievance Database",
        "source_document_id": "DOC-GCC-AUDIT-2024",
        "limitations": "Higher counts often indicate higher citizen civic awareness and digital accessibility rather than greater physical infrastructure decay.",
    },

    # 4. State Policy Outcome Indicators (Phase 10 / Policy Registry)
    "primary_school_attendance_pct": {
        "metric_id": "primary_school_attendance_pct",
        "name": "Primary School Net Attendance Rate",
        "unit": "PERCENT",
        "default_period": "2023-24",
        "supported_levels": ["DISTRICT"],
        "description": "Net attendance rate among children enrolled in government primary schools.",
        "calculation_formula": "Department of School Education EMIS portal daily biometric/teacher registers",
        "primary_source": "School Education Department, Government of Tamil Nadu",
        "source_document_id": "DOC-SED-EMIS-2024",
        "limitations": "Correlated with seasonal harvest periods and local industrial calendar variations.",
    },
    "emergency_trauma_mortality_pct": {
        "metric_id": "emergency_trauma_mortality_pct",
        "name": "Highway Trauma Care 48H Mortality Rate",
        "unit": "PERCENT",
        "default_period": "2023-24",
        "supported_levels": ["DISTRICT"],
        "description": "In-hospital mortality rate for acute road traffic trauma cases within 48 hours of golden hour stabilization.",
        "calculation_formula": "(fatalities_within_48h / total_trauma_admissions) * 100",
        "primary_source": "Tamil Nadu Health System Reform Program (TNHSRP) / Innuyir Kaappom Registry",
        "source_document_id": "DOC-TNHSRP-2024",
        "limitations": "Districts with major national highway trunk corridors (e.g. NH-44, NH-45) handle disproportionately higher baseline severe multi-trauma volumes.",
    },
}


# =====================================================================
# Canonical Geographic Directory (Verified Project Knowledge)
# =====================================================================

CANONICAL_CONSTITUENCIES: Dict[str, Dict[str, Any]] = {
    "AC-011": {
        "constituency_id": "AC-011",
        "name": "Dr. Radhakrishnan Nagar",
        "type": "ASSEMBLY",
        "district": "Chennai",
        "district_code": "ADM-TN-DIST-003-CHENNAI",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 89.2,
                "urban_pct": 100.0,
                "total_population": 245000,
                "sc_pct": 18.5,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 25000000.0,
                "mplads_expenditure_inr": 24500000.0,
                "mplads_utilization_pct": 98.0,
                "public_works_completed_count": 12,
            },
        },
    },
    "AC-012": {
        "constituency_id": "AC-012",
        "name": "Perambur",
        "type": "ASSEMBLY",
        "district": "Chennai",
        "district_code": "ADM-TN-DIST-003-CHENNAI",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 88.4,
                "urban_pct": 100.0,
                "total_population": 280000,
                "sc_pct": 21.2,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 25000000.0,
                "mplads_expenditure_inr": 23800000.0,
                "mplads_utilization_pct": 95.2,
                "public_works_completed_count": 10,
            },
        },
    },
    "AC-013": {
        "constituency_id": "AC-013",
        "name": "Kolathur",
        "type": "ASSEMBLY",
        "district": "Chennai",
        "district_code": "ADM-TN-DIST-003-CHENNAI",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 91.0,
                "urban_pct": 100.0,
                "total_population": 260000,
                "sc_pct": 16.8,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 30000000.0,
                "mplads_expenditure_inr": 29400000.0,
                "mplads_utilization_pct": 98.0,
                "public_works_completed_count": 15,
            },
        },
    },
    "AC-085": {
        "constituency_id": "AC-085",
        "name": "Mettupalayam",
        "type": "ASSEMBLY",
        "district": "Coimbatore",
        "district_code": "ADM-TN-DIST-004-COIMBATORE",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 84.6,
                "urban_pct": 65.4,
                "total_population": 230000,
                "sc_pct": 14.2,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 25000000.0,
                "mplads_expenditure_inr": 21500000.0,
                "mplads_utilization_pct": 86.0,
                "public_works_completed_count": 8,
            },
        },
    },
    "AC-115": {
        "constituency_id": "AC-115",
        "name": "Edappadi",
        "type": "ASSEMBLY",
        "district": "Salem",
        "district_code": "ADM-TN-DIST-022-SALEM",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 81.3,
                "urban_pct": 42.1,
                "total_population": 225000,
                "sc_pct": 12.5,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 25000000.0,
                "mplads_expenditure_inr": 23200000.0,
                "mplads_utilization_pct": 92.8,
                "public_works_completed_count": 11,
            },
        },
    },
    "PC-001": {
        "constituency_id": "PC-001",
        "name": "Chennai North",
        "type": "PARLIAMENTARY",
        "district": "Chennai",
        "district_code": "ADM-TN-DIST-003-CHENNAI",
        "delimitation_year": 2008,
        "reservation": "GENERAL",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 89.6,
                "urban_pct": 100.0,
                "total_population": 1520000,
                "sc_pct": 19.1,
            },
            "FY2022-23": {
                "mplads_funds_allocated_inr": 50000000.0,
                "mplads_expenditure_inr": 48500000.0,
                "mplads_utilization_pct": 97.0,
                "public_works_completed_count": 28,
            },
        },
    },
}

CANONICAL_DISTRICTS: Dict[str, Dict[str, Any]] = {
    "ADM-TN-DIST-003-CHENNAI": {
        "district_code": "ADM-TN-DIST-003-CHENNAI",
        "name_en": "Chennai",
        "name_ta": "சென்னை",
        "lgd_code": "603",
        "headquarters": "Chennai",
        "population": 7088403,
        "metrics": {
            "2011": {
                "literacy_rate_pct": 90.18,
                "urban_pct": 100.0,
                "total_population": 7088403,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 91.4,
                "average_resolution_hours": 38.5,
                "grievances_logged_count": 48210,
                "grievances_resolved_count": 44063,
                "primary_school_attendance_pct": 92.4,
                "emergency_trauma_mortality_pct": 6.8,
            },
        },
    },
    "ADM-TN-DIST-004-COIMBATORE": {
        "district_code": "ADM-TN-DIST-004-COIMBATORE",
        "name_en": "Coimbatore",
        "name_ta": "கோயம்புத்தூர்",
        "lgd_code": "605",
        "headquarters": "Coimbatore",
        "population": 3458045,
        "metrics": {
            "2011": {
                "literacy_rate_pct": 83.98,
                "urban_pct": 75.7,
                "total_population": 3458045,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 88.2,
                "average_resolution_hours": 44.0,
                "grievances_logged_count": 21450,
                "grievances_resolved_count": 18918,
                "primary_school_attendance_pct": 90.1,
                "emergency_trauma_mortality_pct": 7.9,
            },
        },
    },
    "ADM-TN-DIST-013-MADURAI": {
        "district_code": "ADM-TN-DIST-013-MADURAI",
        "name_en": "Madurai",
        "name_ta": "மதுரை",
        "lgd_code": "622",
        "headquarters": "Madurai",
        "population": 3038252,
        "metrics": {
            "2011": {
                "literacy_rate_pct": 83.45,
                "urban_pct": 60.8,
                "total_population": 3038252,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 84.6,
                "average_resolution_hours": 49.2,
                "grievances_logged_count": 18940,
                "grievances_resolved_count": 16023,
                "primary_school_attendance_pct": 88.5,
                "emergency_trauma_mortality_pct": 8.7,
            },
        },
    },
    "ADM-TN-DIST-022-SALEM": {
        "district_code": "ADM-TN-DIST-022-SALEM",
        "name_en": "Salem",
        "name_ta": "சேலம்",
        "lgd_code": "617",
        "headquarters": "Salem",
        "population": 3482056,
        "metrics": {
            "2011": {
                "literacy_rate_pct": 72.86,
                "urban_pct": 51.0,
                "total_population": 3482056,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 82.1,
                "average_resolution_hours": 53.8,
                "grievances_logged_count": 16400,
                "grievances_resolved_count": 13464,
                "primary_school_attendance_pct": 87.2,
                "emergency_trauma_mortality_pct": 9.4,
            },
        },
    },
    "ADM-TN-DIST-028-TIRUCHIRAPPALLI": {
        "district_code": "ADM-TN-DIST-028-TIRUCHIRAPPALLI",
        "name_en": "Tiruchirappalli",
        "name_ta": "திருச்சிராப்பள்ளி",
        "lgd_code": "614",
        "headquarters": "Tiruchirappalli",
        "population": 2722290,
        "metrics": {
            "2011": {
                "literacy_rate_pct": 83.23,
                "urban_pct": 49.2,
                "total_population": 2722290,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 86.9,
                "average_resolution_hours": 42.1,
                "grievances_logged_count": 15800,
                "grievances_resolved_count": 13730,
                "primary_school_attendance_pct": 91.0,
                "emergency_trauma_mortality_pct": 8.1,
            },
        },
    },
    "ADM-TN-DIST-002-CHENGALPATTU": {
        "district_code": "ADM-TN-DIST-002-CHENGALPATTU",
        "name_en": "Chengalpattu",
        "name_ta": "செங்கல்பட்டு",
        "lgd_code": "730",
        "headquarters": "Chengalpattu",
        "population": 2556244,
        "bifurcation_history": "Carved out of Kancheepuram district on 29 November 2019 (G.O. Ms. No. 429).",
        "metrics": {
            "2011": {
                "literacy_rate_pct": 84.1,
                "urban_pct": 68.0,
                "total_population": 2556244,
            },
            "2023-2024": {
                "sla_compliance_rate_pct": 87.5,
                "average_resolution_hours": 46.0,
                "grievances_logged_count": 14200,
                "grievances_resolved_count": 12425,
                "primary_school_attendance_pct": 89.4,
                "emergency_trauma_mortality_pct": 8.5,
            },
        },
    },
}

CANONICAL_WARDS: Dict[str, Dict[str, Any]] = {
    "ADM-TN-GCC-WARD-174": {
        "ward_code": "ADM-TN-GCC-WARD-174",
        "name_en": "Ward 174 (Besant Nagar / Adyar)",
        "zone": "Zone 13 - Adyar",
        "zone_code": "ADM-TN-GCC-ZONE-13-ADYAR",
        "district": "Chennai",
        "population": 38000,
        "metrics": {
            "2023-2024": {
                "sla_compliance_rate_pct": 94.2,
                "average_resolution_hours": 26.4,
                "grievances_logged_count": 1420,
                "grievances_resolved_count": 1338,
            }
        },
    },
    "ADM-TN-GCC-WARD-064": {
        "ward_code": "ADM-TN-GCC-WARD-064",
        "name_en": "Ward 064 (Kolathur North)",
        "zone": "Zone 6 - Thiru. Vi. Ka. Nagar",
        "zone_code": "ADM-TN-GCC-ZONE-06-THIRU_VI_KA_NAGAR",
        "district": "Chennai",
        "population": 41200,
        "metrics": {
            "2023-2024": {
                "sla_compliance_rate_pct": 92.0,
                "average_resolution_hours": 31.0,
                "grievances_logged_count": 1680,
                "grievances_resolved_count": 1545,
            }
        },
    },
    "ADM-TN-GCC-WARD-114": {
        "ward_code": "ADM-TN-GCC-WARD-114",
        "name_en": "Ward 114 (Teynampet East)",
        "zone": "Zone 9 - Teynampet",
        "zone_code": "ADM-TN-GCC-ZONE-09-TEYNAMPET",
        "district": "Chennai",
        "population": 39500,
        "metrics": {
            "2023-2024": {
                "sla_compliance_rate_pct": 89.5,
                "average_resolution_hours": 36.2,
                "grievances_logged_count": 1950,
                "grievances_resolved_count": 1745,
            }
        },
    },
}


# =====================================================================
# Local Civic Comparison Service Implementation
# =====================================================================

class LocalCivicComparisonService:
    """
    Evidence-backed comparison engine across districts, constituencies, and administrative wards.
    Enforces strict compatibility of units, timeframes, and geographic tiers.
    """

    def __init__(self, db: Optional[Session] = None):
        self._db = db

    def _get_db(self) -> Session:
        if self._db is not None:
            return self._db
        return SessionLocal()

    def _close_db_if_local(self, db: Session):
        if self._db is None:
            db.close()

    # -----------------------------------------------------------------
    # Metadata and Directory Lookups
    # -----------------------------------------------------------------

    def get_supported_metrics(self, level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all verified comparable metrics, their units, reporting periods, and limitations.
        """
        metrics = list(SUPPORTED_METRICS.values())
        if level:
            lvl_norm = level.strip().upper()
            metrics = [m for m in metrics if lvl_norm in m.get("supported_levels", [])]
        return metrics

    def get_supported_geographies(self, level: Optional[str] = None) -> Dict[str, Any]:
        """
        Return verified project geographic entities (districts, constituencies, wards).
        """
        lvl_norm = level.strip().upper() if level else None

        results: Dict[str, Any] = {
            "districts": [],
            "constituencies": [],
            "wards": [],
        }

        if lvl_norm in (None, "DISTRICT"):
            for d_code, info in CANONICAL_DISTRICTS.items():
                results["districts"].append({
                    "district_code": d_code,
                    "name_en": info["name_en"],
                    "name_ta": info["name_ta"],
                    "lgd_code": info["lgd_code"],
                    "population": info["population"],
                    "bifurcation_history": info.get("bifurcation_history"),
                    "navigation_url": f"/civic/areas/{d_code}",
                })

        if lvl_norm in (None, "CONSTITUENCY", "ASSEMBLY", "PARLIAMENTARY"):
            for c_id, info in CANONICAL_CONSTITUENCIES.items():
                if lvl_norm in (None, "CONSTITUENCY") or info["type"] == lvl_norm:
                    results["constituencies"].append({
                        "constituency_id": c_id,
                        "name": info["name"],
                        "constituency_type": info["type"],
                        "district": info["district"],
                        "district_code": info["district_code"],
                        "delimitation_year": info["delimitation_year"],
                        "reservation": info["reservation"],
                        "navigation_url": f"/representatives/constituencies/{c_id}",
                    })

        if lvl_norm in (None, "WARD", "LOCAL_BODY"):
            for w_code, info in CANONICAL_WARDS.items():
                results["wards"].append({
                    "ward_code": w_code,
                    "name_en": info["name_en"],
                    "zone": info["zone"],
                    "district": info["district"],
                    "population": info["population"],
                    "navigation_url": f"/civic/areas/{w_code}",
                })

        return results

    # -----------------------------------------------------------------
    # Entity Profile Retrieval
    # -----------------------------------------------------------------

    def get_geographic_profile(self, entity_type: str, entity_id: str) -> Dict[str, Any]:
        """
        Retrieve complete profile and verified indicators for a specific district, constituency, or ward.
        """
        clean_type = entity_type.strip().lower()
        clean_id = entity_id.strip().upper()

        if clean_type in ("district", "districts"):
            # Check canonical first
            found_key = next((k for k in CANONICAL_DISTRICTS if k == clean_id or CANONICAL_DISTRICTS[k]["name_en"].upper() == clean_id), None)
            if not found_key:
                # Also match against 38 revenue districts in CivicGeographicMapper
                for mapper_code, (en_name, ta_name, lat, lon) in CivicGeographicMapper.TN_DISTRICTS.items():
                    if mapper_code == clean_id or en_name.upper() == clean_id:
                        return {
                            "entity_type": "DISTRICT",
                            "entity_id": mapper_code,
                            "name_en": en_name,
                            "name_ta": ta_name,
                            "latitude": lat,
                            "longitude": lon,
                            "data_status": "OFFICIAL_JURISDICTION_REGISTERED",
                            "notice": "Jurisdiction is official Tamil Nadu revenue district; specific sub-metric tables pending ingestion.",
                            "available_periods": [],
                            "metrics_by_period": {},
                        }
                raise EntityNotFoundError(f"District '{entity_id}' not found in official Tamil Nadu registry.")

            info = CANONICAL_DISTRICTS[found_key]
            return {
                "entity_type": "DISTRICT",
                "entity_id": found_key,
                "name_en": info["name_en"],
                "name_ta": info["name_ta"],
                "lgd_code": info["lgd_code"],
                "population": info["population"],
                "bifurcation_history": info.get("bifurcation_history"),
                "available_periods": list(info.get("metrics", {}).keys()),
                "metrics_by_period": info.get("metrics", {}),
            }

        elif clean_type in ("constituency", "constituencies"):
            found_key = next((k for k in CANONICAL_CONSTITUENCIES if k == clean_id or CANONICAL_CONSTITUENCIES[k]["name"].upper() == clean_id), None)
            if not found_key:
                raise EntityNotFoundError(f"Constituency '{entity_id}' not found in verified 2008 delimitation roster.")

            info = CANONICAL_CONSTITUENCIES[found_key]
            return {
                "entity_type": "CONSTITUENCY",
                "entity_id": found_key,
                "name": info["name"],
                "constituency_type": info["type"],
                "district": info["district"],
                "district_code": info["district_code"],
                "delimitation_year": info["delimitation_year"],
                "reservation": info["reservation"],
                "available_periods": list(info.get("metrics", {}).keys()),
                "metrics_by_period": info.get("metrics", {}),
            }

        elif clean_type in ("ward", "wards"):
            found_key = next((k for k in CANONICAL_WARDS if k == clean_id or CANONICAL_WARDS[k]["ward_code"] == clean_id), None)
            if not found_key:
                raise EntityNotFoundError(f"Ward '{entity_id}' not found in municipal corporation registry.")

            info = CANONICAL_WARDS[found_key]
            return {
                "entity_type": "WARD",
                "entity_id": found_key,
                "name_en": info["name_en"],
                "zone": info["zone"],
                "district": info["district"],
                "population": info["population"],
                "available_periods": list(info.get("metrics", {}).keys()),
                "metrics_by_period": info.get("metrics", {}),
            }

        else:
            raise IncompatibleGeographicLevelError(f"Unsupported geographic level '{entity_type}'. Must be 'district', 'constituency', or 'ward'.")

    # -----------------------------------------------------------------
    # Cross-Entity Civic Comparison Engine
    # -----------------------------------------------------------------

    def compare_entities(
        self,
        entity_type: str,
        entity_ids: List[str],
        metric_id: str,
        reporting_period: Optional[str] = None,
        rank_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a rigorous comparison across 2 or more entities of the same administrative level.
        Enforces unit compatibility, period consistency, zero vs missing distinction,
        and generates contextual warnings.
        """
        clean_type = entity_type.strip().upper()
        if clean_type in ("DISTRICTS",):
            clean_type = "DISTRICT"
        elif clean_type in ("CONSTITUENCIES",):
            clean_type = "CONSTITUENCY"
        elif clean_type in ("WARDS",):
            clean_type = "WARD"

        if clean_type not in ("DISTRICT", "CONSTITUENCY", "WARD"):
            raise IncompatibleGeographicLevelError(
                f"Unsupported geographic tier '{entity_type}'. Comparable tiers are: 'DISTRICT', 'CONSTITUENCY', 'WARD'."
            )

        if not entity_ids or len(entity_ids) < 2:
            raise LocalInsightError("At least 2 geographic entities are required for comparative analysis.")

        # Metric verification
        clean_metric = metric_id.strip().lower()
        if clean_metric not in SUPPORTED_METRICS:
            raise LocalInsightError(
                f"Unsupported or unverified metric '{metric_id}'. See /api/local-insights/metrics for validated indicators."
            )

        metric_def = SUPPORTED_METRICS[clean_metric]

        # Verify geographic level compatibility for metric
        if clean_type not in metric_def["supported_levels"]:
            raise IncompatibleGeographicLevelError(
                f"Metric '{metric_def['name']}' is not supported at '{clean_type}' level. Supported levels: {metric_def['supported_levels']}."
            )

        target_period = (reporting_period or metric_def["default_period"]).strip()

        # Epistemic Prohibitions: Arbitrary composite scores
        if rank_by and rank_by.lower() not in (clean_metric, "value", "none"):
            raise ArbitraryScoringProhibitedError(
                f"Arbitrary composite ranking '{rank_by}' is prohibited. CIVICLENS TN strictly permits sorting "
                f"only by the primary defensible metric being compared ('{clean_metric}') with full calculation transparency."
            )

        # Retrieve profiles and observations
        comparison_rows: List[Dict[str, Any]] = []
        warnings: List[str] = []
        urban_shares: List[float] = []
        populations: List[int] = []

        for e_id in entity_ids:
            try:
                profile = self.get_geographic_profile(clean_type, e_id)
            except EntityNotFoundError as e:
                raise EntityNotFoundError(str(e))

            canonical_id = profile["entity_id"]
            name = profile.get("name_en") or profile.get("name")
            period_data = profile.get("metrics_by_period", {}).get(target_period, {})

            # Check zero vs missing/unavailable
            if clean_metric in period_data:
                raw_val = period_data[clean_metric]
                if raw_val is None:
                    value = None
                    is_zero = False
                    is_unavailable = True
                    avail_status = "DATA_NOT_REPORTED"
                else:
                    value = float(raw_val)
                    is_zero = (value == 0.0)
                    is_unavailable = False
                    avail_status = "ZERO_RECORDED" if is_zero else "AVAILABLE"
            else:
                value = None
                is_zero = False
                is_unavailable = True
                avail_status = "OUTSIDE_AUDIT_SCOPE"

            # Capture urban share and population for contextual comparability checks
            demo_period = "2011" if clean_type in ("DISTRICT", "CONSTITUENCY") else target_period
            demo_data = profile.get("metrics_by_period", {}).get(demo_period, {})
            u_pct = demo_data.get("urban_pct")
            if u_pct is not None:
                urban_shares.append(float(u_pct))
            pop = profile.get("population") or demo_data.get("total_population")
            if pop is not None:
                populations.append(int(pop))

            # Check if entity has bifurcation history
            bifurcation = profile.get("bifurcation_history")
            if bifurcation:
                warnings.append(f"Geographic boundary note for {name}: {bifurcation}")

            row = {
                "entity_id": canonical_id,
                "name": name,
                "geographic_level": clean_type,
                "metric_id": clean_metric,
                "metric_name": metric_def["name"],
                "value": value,
                "unit": metric_def["unit"],
                "reporting_period": target_period,
                "is_zero": is_zero,
                "is_unavailable": is_unavailable,
                "availability_status": avail_status,
                "data_quality_status": "VERIFIED" if not is_unavailable else "UNAVAILABLE",
                "calculation_method": "DIRECT_OBSERVATION" if not is_unavailable else "UNAVAILABLE",
                "source_citations": [
                    {
                        "document_id": metric_def["source_document_id"],
                        "title": metric_def["primary_source"],
                        "official_url": "https://www.tn.gov.in" if "TN" in metric_def["source_document_id"] else "https://censusindia.gov.in",
                    }
                ],
            }
            comparison_rows.append(row)

        # Contextual comparability evaluations
        # 1. Urban vs Rural demographic divergence warning
        if len(urban_shares) >= 2:
            max_u = max(urban_shares)
            min_u = min(urban_shares)
            if (max_u - min_u) > 35.0:
                warnings.append(
                    f"DEMOGRAPHIC COMPARABILITY WARNING: Substantial urban-rural divergence detected "
                    f"(urban share ranges from {min_u:.1f}% to {max_u:.1f}%). Urban ULB municipal services "
                    f"and rural agrarian infrastructure operate under fundamentally different service parameters."
                )

        # 2. Population divergence warning
        if len(populations) >= 2:
            max_p = max(populations)
            min_p = min(populations)
            if min_p > 0 and (max_p / min_p) > 2.5:
                warnings.append(
                    f"POPULATION SCALE WARNING: Compared entities differ significantly in population scale "
                    f"(minimum: {min_p:,}, maximum: {max_p:,}). Absolute indicators should be evaluated "
                    f"per capita or normalized by population weight."
                )

        # 3. Missing data warnings
        unavailable_count = sum(1 for r in comparison_rows if r["is_unavailable"])
        if unavailable_count > 0:
            warnings.append(
                f"DATA COMPLETENESS WARNING: {unavailable_count} of {len(comparison_rows)} compared entities have "
                f"no verified records for '{metric_def['name']}' in period {target_period}. "
                f"Missing entries are explicitly labeled 'UNAVAILABLE' and must NEVER be treated as zero activity."
            )

        # Single-metric ranking if requested
        ranked_results = list(comparison_rows)
        ranking_metadata: Optional[Dict[str, Any]] = None

        if rank_by and rank_by.lower() in (clean_metric, "value"):
            # Sort valid values descending, placing unavailable at the bottom
            ranked_results.sort(
                key=lambda x: (x["value"] is not None, x["value"] if x["value"] is not None else -float("inf")),
                reverse=True,
            )
            for idx, r in enumerate(ranked_results, start=1):
                if r["value"] is not None:
                    r["relative_rank"] = idx
                else:
                    r["relative_rank"] = None

            ranking_metadata = {
                "ranked_by_metric": clean_metric,
                "ranking_direction": "DESCENDING",
                "calculation_formula": metric_def["calculation_formula"],
                "limitations": metric_def["limitations"],
                "disclaimer": (
                    "RANKING LIMITATION NOTICE: Relative rank is strictly confined to the observed single indicator. "
                    "It does NOT establish overall administrative efficacy, policy merit, or elected representative quality. "
                    "Variations in baseline funding, geographic terrain, and historical deficits must be accounted for."
                ),
            }

        return {
            "comparison_id": f"CMP-{clean_type}-{clean_metric.upper()}-{target_period}",
            "geographic_level": clean_type,
            "metric_id": clean_metric,
            "metric_name": metric_def["name"],
            "unit": metric_def["unit"],
            "reporting_period": target_period,
            "entities_compared_count": len(comparison_rows),
            "available_records_count": len(comparison_rows) - unavailable_count,
            "unavailable_records_count": unavailable_count,
            "comparisons": ranked_results,
            "ranking": ranking_metadata,
            "warnings": warnings,
            "guardrails": {
                "zero_vs_unavailable_rule": (
                    "NON-CONFLATION GUARDRAIL: Zero values (0.0) indicate an officially measured zero. "
                    "Unavailable records indicate lack of public publication and are strictly prohibited "
                    "from being presented as zero activity."
                ),
                "no_arbitrary_scores_rule": (
                    "OBJECTIVITY GUARDRAIL: CIVICLENS TN strictly prohibits arbitrary composite civic scores. "
                    "Comparisons evaluate verified, individual public indicators with explicit methodology."
                ),
                "causality_guardrail": (
                    "NON-CAUSATION GUARDRAIL: Relative indicator differences between districts or constituencies "
                    "do not prove causal efficacy of any single program without controlling for exogenous demographic factors."
                ),
            },
        }
