import pytest
import pandas as pd
import numpy as np
from backend.models.budget import BudgetRecord, BudgetStage, BudgetDepartment, BudgetScheme
from backend.ml.budget_pca import BudgetPCAAnalysis

def _generate_mock_records(n: int) -> list:
    dept = BudgetDepartment(name="Test Dept")
    records = []
    for i in range(n):
        scheme = BudgetScheme(name=f"Scheme {i}", department=dept)
        amount = 100.0 * (i + 1)
        records.append(
            BudgetRecord(
                scheme=scheme, 
                financial_year="2023-24", 
                budget_stage=BudgetStage.budget_estimate, 
                amount=amount
            )
        )
    return records

def test_pca_insufficient_data():
    pca = BudgetPCAAnalysis()
    records = _generate_mock_records(1)
    with pytest.raises(ValueError, match="Insufficient data"):
        pca.fit_transform(records)

def test_pca_invalid_components():
    pca = BudgetPCAAnalysis(n_components=10)
    records = _generate_mock_records(10)
    with pytest.raises(ValueError, match="Cannot request 10 components"):
        pca.fit_transform(records)

def test_pca_transformation_and_variance():
    records = _generate_mock_records(10)
    pca = BudgetPCAAnalysis(n_components=2)
    
    df = pca.fit_transform(records)
    
    assert "PC1" in df.columns
    assert "PC2" in df.columns
    assert "department" in df.columns
    assert "scheme" in df.columns
    assert len(df) == 10
    
    assert df["scheme"].iloc[0] == "Scheme 0"
    
    variance_stats = pca.get_explained_variance()
    assert "explained_variance_ratio" in variance_stats
    assert "cumulative_explained_variance" in variance_stats
    assert len(variance_stats["explained_variance_ratio"]) == 2
    
    cum_var = variance_stats["cumulative_explained_variance"]
    assert cum_var[1] >= cum_var[0]
    assert variance_stats["total_variance_explained"] <= 1.0001

def test_pca_unfitted_variance():
    pca = BudgetPCAAnalysis()
    with pytest.raises(ValueError, match="Call fit_transform first"):
        pca.get_explained_variance()
