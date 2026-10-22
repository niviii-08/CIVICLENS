"""
CIVICLENS TN — Budget and Public Finance Transformation Utilities
================================================================
Explicit currency conversions, accounting category comparability checks,
reconciliation validators, and non-causal financial assertions.
"""

import re
from enum import Enum
from typing import Optional, Dict, Any, Tuple, List


class CurrencyUnit(str, Enum):
    """Standardized currency units used in Tamil Nadu budget publications."""
    RUPEES_CRORE = "RUPEES_CRORE"
    RUPEES_LAKH = "RUPEES_LAKH"
    RUPEES_THOUSAND = "RUPEES_THOUSAND"
    RUPEES_ABSOLUTE = "RUPEES_ABSOLUTE"


# Exact conversion factors to Absolute Rupees (INR)
# 1 Crore = 10,000,000 INR
# 1 Lakh = 100,000 INR
# 1 Thousand = 1,000 INR
# 1 Absolute = 1 INR
_UNIT_TO_INR_FACTORS: Dict[str, float] = {
    "RUPEES_CRORE": 10_000_000.0,
    "INR_CRORE": 10_000_000.0,
    "CRORE": 10_000_000.0,
    "CRORES": 10_000_000.0,
    "CR": 10_000_000.0,

    "RUPEES_LAKH": 100_000.0,
    "INR_LAKH": 100_000.0,
    "LAKH": 100_000.0,
    "LAKHS": 100_000.0,
    "L": 100_000.0,

    "RUPEES_THOUSAND": 1_000.0,
    "INR_THOUSAND": 1_000.0,
    "THOUSAND": 1_000.0,
    "THOUSANDS": 1_000.0,
    "K": 1_000.0,

    "RUPEES_ABSOLUTE": 1.0,
    "INR_ABSOLUTE": 1.0,
    "INR": 1.0,
    "RUPEES": 1.0,
    "RS": 1.0
}


def normalize_unit_string(unit: str) -> str:
    """Normalizes raw unit string into standardized CurrencyUnit representation."""
    if not unit:
        return CurrencyUnit.RUPEES_ABSOLUTE.value
    cleaned = unit.strip().upper().replace(" ", "_").replace(".", "")
    if cleaned in ["RUPEES_CRORE", "INR_CRORE", "CRORE", "CRORES", "CR"]:
        return CurrencyUnit.RUPEES_CRORE.value
    elif cleaned in ["RUPEES_LAKH", "INR_LAKH", "LAKH", "LAKHS", "L"]:
        return CurrencyUnit.RUPEES_LAKH.value
    elif cleaned in ["RUPEES_THOUSAND", "INR_THOUSAND", "THOUSAND", "THOUSANDS", "K"]:
        return CurrencyUnit.RUPEES_THOUSAND.value
    elif cleaned in ["RUPEES_ABSOLUTE", "INR_ABSOLUTE", "INR", "RUPEES", "RS"]:
        return CurrencyUnit.RUPEES_ABSOLUTE.value
    else:
        raise ValueError(f"Unsupported or unrecognized currency unit: '{unit}'")


def convert_currency(
    amount: Optional[float],
    from_unit: str,
    to_unit: str,
    decimal_places: int = 4
) -> Optional[float]:
    """
    Explicit bidirectional conversion between currency units.
    
    CRITICAL RULE:
    - Never coerces None to 0.0 (preserves missing/unrecorded values).
    - Uses exact mathematical multipliers.
    - Validates source and target units strictly.
    """
    if amount is None:
        return None

    norm_from = normalize_unit_string(from_unit)
    norm_to = normalize_unit_string(to_unit)

    if norm_from == norm_to:
        return round(float(amount), decimal_places)

    factor_from = _UNIT_TO_INR_FACTORS[norm_from]
    factor_to = _UNIT_TO_INR_FACTORS[norm_to]

    # Convert to base INR, then to target unit
    amount_in_inr = float(amount) * factor_from
    converted_amount = amount_in_inr / factor_to

    return round(converted_amount, decimal_places)


def validate_financial_year(fy_string: str) -> bool:
    """
    Validates standard Indian financial year format (e.g., '2023-24' or '2026-27').
    Rejects malformed strings like '2023', '2023/2024', or non-consecutive years.
    """
    if not fy_string or not isinstance(fy_string, str):
        return False

    pattern = r"^(\d{4})-(\d{2})$"
    match = re.match(pattern, fy_string.strip())
    if not match:
        return False

    start_year = int(match.group(1))
    end_year_suffix = int(match.group(2))

    # Consecutive year validation: 2023 -> 24 (23 + 1 == 24), 1999 -> 00 ((99 + 1) % 100 == 0)
    expected_suffix = (start_year + 1) % 100
    return end_year_suffix == expected_suffix


def validate_comparability(
    stage_a: str,
    stage_b: str,
    category_a: Optional[str] = None,
    category_b: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validates whether two financial measures can be directly compared.
    
    Guards against:
    - Comparing identical stages without qualification.
    - Comparing Capital Outlay to Revenue Expenditure.
    - Comparing unaudited BE directly to audited AE without stage variance qualification.
    """
    if stage_a == stage_b:
        return False, "Cannot compare identical budget stages."

    if category_a and category_b:
        norm_cat_a = category_a.strip().upper()
        norm_cat_b = category_b.strip().upper()
        if "CAPITAL" in norm_cat_a and "REVENUE" in norm_cat_b:
            return False, "Incompatible accounting categories: cannot compare Capital Outlay directly to Revenue Expenditure."
        if "REVENUE" in norm_cat_a and "CAPITAL" in norm_cat_b:
            return False, "Incompatible accounting categories: cannot compare Revenue Expenditure directly to Capital Outlay."

    return True, None


def reconcile_subhead_totals(
    subhead_amounts: List[Optional[float]],
    reported_total: Optional[float],
    unit: str = "RUPEES_CRORE",
    tolerance: float = 0.05
) -> Dict[str, Any]:
    """
    Reconciles scheme sub-head line items against a reported demand total.
    
    Preserves missing values:
    - If reported_total is None or all subheads are None, reconciliation is skipped.
    - Only sums present non-None amounts.
    - Evaluates whether reported total matches sum within rounding tolerance.
    """
    if reported_total is None:
        return {
            "reconciliation_status": "SKIPPED_MISSING_REPORTED_TOTAL",
            "variance": None,
            "is_balanced": None
        }

    valid_subheads = [a for a in subhead_amounts if a is not None]
    if not valid_subheads:
        return {
            "reconciliation_status": "SKIPPED_NO_SUBHEAD_DATA",
            "variance": None,
            "is_balanced": None
        }

    computed_sum = sum(valid_subheads)
    variance = round(computed_sum - float(reported_total), 4)
    is_balanced = abs(variance) <= tolerance

    return {
        "reconciliation_status": "RECONCILED" if is_balanced else "DISCREPANCY_DETECTED",
        "computed_sum": round(computed_sum, 4),
        "reported_total": float(reported_total),
        "variance": variance,
        "is_balanced": is_balanced,
        "unit": unit,
        "subhead_count_present": len(valid_subheads),
        "subhead_count_missing": len(subhead_amounts) - len(valid_subheads)
    }
