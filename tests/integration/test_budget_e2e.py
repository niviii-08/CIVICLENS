import os
import pytest
import pandas as pd
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.base import Base
from backend.models.budget import BudgetRecord, BudgetStage, BudgetDepartment, BudgetScheme, BudgetSourceDocument
from backend.ingestion.budget_ingestor import BudgetIngestor
from backend.api.app import create_app

@pytest.fixture(scope="function")
def isolated_budget_env(tmp_path):
    """Provides a completely isolated test database for budget end-to-end testing."""
    db_path = tmp_path / "budget_e2e_isolated.db"
    db_url = f"sqlite:///{db_path}"
    test_engine = create_engine(db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=test_engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    
    with patch("backend.database.session.SessionLocal", TestSessionLocal), \
         patch("backend.api.budget.SessionLocal", TestSessionLocal), \
         patch("backend.api.ml.SessionLocal", TestSessionLocal):
        db = TestSessionLocal()
        app = create_app()
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield db, client
        db.close()
        test_engine.dispose()

@pytest.fixture
def e2e_db(isolated_budget_env):
    return isolated_budget_env[0]

@pytest.fixture
def e2e_client(isolated_budget_env):
    return isolated_budget_env[1]

def test_e2e_budget_pipeline(e2e_db, e2e_client, tmp_path):
    """
    Simulates the entire pipeline: 
    1. CSV file on disk.
    2. Manifest JSON.
    3. Ingestion into DB.
    4. Retrieving through APIs.
    5. ML clustering and traceability.
    """
    
    raw_data = pd.DataFrame([
        {"department_name": " Health ", "scheme_name": "Primary Care", "financial_year": "2023-2024", "budget_estimate": 100.5},
        {"department_name": "Health", "scheme_name": "Hospital Infra", "financial_year": "2023-2024", "budget_estimate": 500.0},
        {"department_name": "Health", "scheme_name": "Hospital Infra", "financial_year": "2023-2024", "budget_estimate": 500.0},
        {"department_name": "Health", "scheme_name": "Maternity", "financial_year": None, "budget_estimate": 200.0},
    ])
    
    csv_path = tmp_path / "test_data.csv"
    raw_data.to_csv(csv_path, index=False)
    
    import json
    manifest_data = {
        "datasets": [
            {
                "dataset_id": "E2E_DOC_01",
                "dataset_title": "E2E Test Budget Document",
                "collection_status": "verified",
                "file_format": "csv",
                "original_filename": "test_data.csv",
                "published_date": "2024-01-01",
                "financial_year": "2023-24"
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f)
        
    ingestor = BudgetIngestor(e2e_db, str(manifest_path), str(tmp_path))
    ingestor.ingest()
    
    docs = e2e_db.query(BudgetSourceDocument).all()
    assert len(docs) == 1
    
    records = e2e_db.query(BudgetRecord).all()
    
    assert len(records) == 3, f"Expected 3 records, got {len(records)}"
    
    res = e2e_client.get('/api/budget/departments')
    assert res.status_code == 200
    depts = res.get_json()['data']
    assert len(depts) == 1
    assert depts[0]['name'] == "Health"
    dept_id = depts[0]['id']
    
    res = e2e_client.get(f'/api/budget/schemes?department_id={dept_id}')
    schemes = res.get_json()['data']
    assert len(schemes) == 3
    
    records_debug = e2e_db.query(BudgetRecord).all()
    for r in records_debug:
        print(f"DEBUG: {r.scheme.name} - {r.budget_stage} - {r.amount}")
        
    res = e2e_client.get('/api/ml/budget/clustering?budget_stage=budget_estimate&algorithm=kmeans&k=2')
    if res.status_code != 200:
        print(res.get_json())
    assert res.status_code == 200
    ml_data = res.get_json()['data']
    
    assert ml_data["algorithm"] == "kmeans"
    assert len(ml_data["data_points"]) == 3
    
    pt1 = ml_data["data_points"][0]
    assert "source_documents" in pt1
    assert len(pt1["source_documents"]) > 0
    assert str(docs[0].id) in pt1["source_documents"]

def test_e2e_empty_database_handling(e2e_client):
    """
    Test how the system behaves when no data is ingested.
    """
    res = e2e_client.get('/api/ml/budget/clustering?budget_stage=budget_estimate&algorithm=kmeans&k=2')
    assert res.status_code == 400
    assert "Insufficient records" in res.get_json()['message']
    
    res = e2e_client.get('/api/budget/records')
    assert res.status_code == 200
    assert len(res.get_json()['data']['records']) == 0
    
def test_e2e_invalid_file_handling(e2e_db, tmp_path):
    """
    Test how the ingestor handles missing files and unsupported formats.
    """
    import json
    manifest_data = {
        "datasets": [
            {
                "dataset_id": "ERR_01",
                "collection_status": "verified",
                "file_format": "csv",
                "original_filename": "does_not_exist.csv"
            },
            {
                "dataset_id": "ERR_02",
                "collection_status": "verified",
                "file_format": "xml",
                "original_filename": "test.xml"
            }
        ]
    }
    manifest_path = tmp_path / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest_data, f)
        
    (tmp_path / "test.xml").write_text("<test></test>")
    
    ingestor = BudgetIngestor(e2e_db, str(manifest_path), str(tmp_path))
    ingestor.ingest()
    
    assert e2e_db.query(BudgetRecord).count() == 0
