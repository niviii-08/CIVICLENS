import pytest
import pandas as pd
import numpy as np
from backend.models.budget import BudgetRecord, BudgetStage, BudgetDepartment, BudgetScheme
from backend.ml.budget_features import BudgetFeatureEngineering

def test_budget_features_extraction():
    dept = BudgetDepartment(name="Health")
    scheme_a = BudgetScheme(name="Scheme A", department=dept)
    scheme_b = BudgetScheme(name="Scheme B", department=dept)
    
    records = [
        BudgetRecord(scheme=scheme_a, financial_year="2023-24", budget_stage=BudgetStage.budget_estimate, amount=1000.0),
        BudgetRecord(scheme=scheme_b, financial_year="2023-24", budget_stage=BudgetStage.budget_estimate, amount=3000.0),
        
        BudgetRecord(scheme=scheme_a, financial_year="2024-25", budget_stage=BudgetStage.budget_estimate, amount=1200.0),
        BudgetRecord(scheme=scheme_a, financial_year="2024-25", budget_stage=BudgetStage.actual_expenditure, amount=1000.0),
        
        BudgetRecord(scheme=scheme_b, financial_year="2024-25", budget_stage=BudgetStage.budget_estimate, amount=None)
    ]
    
    extractor = BudgetFeatureEngineering()
    extractor.fit(records)
    
    X, y_ids = extractor.transform(records)
    
    assert not X.empty
    assert len(X) == 3
    
    assert list(X.columns) == ["be_amount", "allocation_share", "yoy_change_be", "actual_vs_be_diff"]
    
    idx_23_a = y_ids[(y_ids["scheme"] == "Scheme A") & (y_ids["financial_year"] == "2023-24")].index[0]
    idx_23_b = y_ids[(y_ids["scheme"] == "Scheme B") & (y_ids["financial_year"] == "2023-24")].index[0]
    
    raw_df = extractor._create_raw_matrix(records)
    features, ids = extractor._engineer_features(raw_df)
    
    f_23_a = features.loc[idx_23_a]
    f_23_b = features.loc[idx_23_b]
    
    assert f_23_a["be_amount"] == 1000.0
    assert f_23_b["be_amount"] == 3000.0
    assert f_23_a["allocation_share"] == 0.25
    assert f_23_b["allocation_share"] == 0.75
    
    assert pd.isna(f_23_a["yoy_change_be"])
    assert pd.isna(f_23_b["yoy_change_be"])
    
    idx_24_a = y_ids[(y_ids["scheme"] == "Scheme A") & (y_ids["financial_year"] == "2024-25")].index[0]
    f_24_a = features.loc[idx_24_a]
    
    assert f_24_a["be_amount"] == 1200.0
    assert f_24_a["allocation_share"] == 1.0
    
    assert f_24_a["yoy_change_be"] == 0.2
    np.testing.assert_almost_equal(f_24_a["actual_vs_be_diff"], -0.16666, decimal=4)

def test_no_data_leakage():
    dept = BudgetDepartment(name="Test")
    scheme = BudgetScheme(name="Scheme C", department=dept)
    
    train = [BudgetRecord(scheme=scheme, financial_year="2023-24", budget_stage=BudgetStage.budget_estimate, amount=100.0)]
    test = [BudgetRecord(scheme=scheme, financial_year="2024-25", budget_stage=BudgetStage.budget_estimate, amount=500.0)]
    
    ext = BudgetFeatureEngineering().fit(train)
    
    assert ext.means_["be_amount"] == 100.0
    
    X_test, _ = ext.transform(test)
    
    assert X_test.iloc[0]["be_amount"] == 400.0 
