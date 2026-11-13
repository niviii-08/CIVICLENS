"""
Phase 5 Financial Document Cross-Validation Test Fixtures.

Contains explicitly labelled mock statutory documents, contribution lists,
audited financial statements, electoral trust reports, and election expenditure reports
for testing all cross-validation scenarios and human review workflows.
"""

from typing import List
from backend.schemas.funding import ContributionSchema, FinancialStatementSchema, ElectionExpenditureSchema


MOCK_CROSSVAL_FORM24A_FY21: List[ContributionSchema] = [
    ContributionSchema(
        contribution_id="CONT_CV_001",
        party_id="PARTY_TN_DMK",
        donor_name_as_reported="Mega Corp Infrastructure Pvt Ltd",
        donor_name_normalized="MEGA CORP INFRASTRUCTURE PVT LTD",
        amount=10000000.0,
        financial_year="FY2021-22",
        contribution_type="EFT",
        document_id="DOC_FORM24A_DMK_FY21"
    ),
    ContributionSchema(
        contribution_id="CONT_CV_002",
        party_id="PARTY_TN_DMK",
        donor_name_as_reported="Prudent Electoral Trust",
        donor_name_normalized="PRUDENT ELECTORAL TRUST",
        amount=50000000.0,
        financial_year="FY2021-22",
        contribution_type="ElectoralTrust",
        document_id="DOC_FORM24A_DMK_FY21"
    ),
    ContributionSchema(
        contribution_id="CONT_CV_003",
        party_id="PARTY_TN_DMK",
        donor_name_as_reported="Dr. K. Swaminathan",
        donor_name_normalized="DR. K. SWAMINATHAN",
        amount=100000.0,
        financial_year="FY2021-22",
        contribution_type="Cheque",
        document_id="DOC_FORM24A_DMK_FY21"
    ),
    ContributionSchema(
        contribution_id="CONT_CV_004",
        party_id="PARTY_TN_DMK",
        donor_name_as_reported="Small Retailer Store",
        donor_name_normalized="SMALL RETAILER STORE",
        amount=30000.0,
        financial_year="FY2021-22",
        contribution_type="Cheque",
        document_id="DOC_FORM24A_DMK_FY21"
    )
]

MOCK_CROSSVAL_AUDIT_MATCHED_FY21 = FinancialStatementSchema(
    statement_id="STMT_MATCHED_FY21",
    party_id="PARTY_TN_DMK",
    financial_year="FY2021-22",
    total_income_reported=300000000.0,
    total_expenditure_reported=220000000.0,
    net_surplus_deficit=80000000.0,
    income_categories={
        "donations_above_20k": 60130000.0,
        "electoral_bond_income": 150000000.0,
        "other_income": 89870000.0
    },
    expenditure_categories={
        "publicity_and_media": 120000000.0,
        "star_campaigner_travel": 50000000.0,
        "salaries_and_admin": 30000000.0,
        "candidate_assistance": 20000000.0
    },
    document_id="DOC_AUDIT_DMK_FY21"
)

MOCK_CROSSVAL_AUDIT_MISMATCH_FY21 = FinancialStatementSchema(
    statement_id="STMT_MISMATCH_FY21",
    party_id="PARTY_TN_DMK",
    financial_year="FY2021-22",
    total_income_reported=300000000.0,
    total_expenditure_reported=220000000.0,
    net_surplus_deficit=80000000.0,
    income_categories={
        "donations_above_20k": 70000000.0,
        "electoral_bond_income": 140000000.0,
        "other_income": 90000000.0
    },
    expenditure_categories={
        "publicity_and_media": 120000000.0,
        "salaries_and_admin": 100000000.0
    },
    document_id="DOC_AUDIT_DMK_FY21_ALT"
)

MOCK_CROSSVAL_AUDIT_IMPOSSIBLE_INCOME_FY21 = FinancialStatementSchema(
    statement_id="STMT_IMPOSSIBLE_FY21",
    party_id="PARTY_TN_DMK",
    financial_year="FY2021-22",
    total_income_reported=40000000.0,
    total_expenditure_reported=35000000.0,
    net_surplus_deficit=5000000.0,
    income_categories={
        "donations_above_20k": 40000000.0
    },
    document_id="DOC_AUDIT_DMK_FY21_BAD"
)

MOCK_CROSSVAL_ELECTION_EXP_TN2021 = ElectionExpenditureSchema(
    expenditure_id="EXP_TN2021_DMK",
    party_id="PARTY_TN_DMK",
    election="TN Legislative Assembly 2021",
    reporting_period="FY2021-22",
    expenditure_categories={
        "publicity_and_media": 120000000.0,
        "star_campaigner_travel": 50000000.0,
        "candidate_assistance": 20000000.0
    },
    reported_totals=190000000.0,
    document_id="DOC_EXP_TN2021_DMK"
)

MOCK_CROSSVAL_ELECTION_EXP_EXCESS = ElectionExpenditureSchema(
    expenditure_id="EXP_TN2021_EXCESS",
    party_id="PARTY_TN_DMK",
    election="TN Legislative Assembly 2021",
    reporting_period="FY2021-22",
    expenditure_categories={
        "publicity_and_media": 250000000.0
    },
    reported_totals=250000000.0,
    document_id="DOC_EXP_TN2021_EXCESS"
)

TRUST_DISBURSEMENT_AMOUNT_MATCHED = 50000000.0
TRUST_DISBURSEMENT_AMOUNT_MISMATCHED = 65000000.0
