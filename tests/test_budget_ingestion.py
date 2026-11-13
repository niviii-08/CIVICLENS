import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.database.base_class import Base
from backend.models.budget import BudgetRecord, BudgetStage
from backend.ingestion.budget_ingestor import BudgetIngestor
import backend.models.budget

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_ingestion_pipeline_with_csv_fixture(db_session):
    manifest_path = os.path.join("tests", "fixtures", "data", "raw", "budget", "test_manifest.json")
    raw_dir = os.path.join("tests", "fixtures", "data", "raw", "budget")
    
    ingestor = BudgetIngestor(db_session, manifest_path, raw_dir)
    ingestor.ingest()
    
    records = db_session.query(BudgetRecord).all()
    
    assert len(records) > 0
    assert records[0].source_document.manifest_dataset_id == "TEST_BUDGET_01"
    assert records[0].financial_year == "2024-25"
    assert records[0].scheme.department.name == "School Education"
    assert records[0].currency_unit == "INR_Thousands"
