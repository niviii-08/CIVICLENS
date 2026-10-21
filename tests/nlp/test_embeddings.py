import pytest
from unittest.mock import MagicMock
import numpy as np
from backend.nlp.embeddings import HistoricalSchemeEmbedder
from backend.database.session import SessionLocal
from backend.models.budget import HistoricalScheme, BudgetDepartment

def test_embedder():
    embedder = HistoricalSchemeEmbedder()
    assert embedder.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
    
    # Mock underlying model to ensure deterministic, offline execution in CI/air-gapped runners
    mock_model = MagicMock()
    mock_model.encode.return_value = np.zeros(384)
    embedder._model = mock_model
    
    vec = embedder.generate_embedding("Tamil Nadu maternity assistance")
    assert len(vec) == 384
    
    text_hash = embedder._compute_text_hash("Hello")
    assert text_hash == embedder._compute_text_hash("Hello")
    assert text_hash != embedder._compute_text_hash("Hello ")

    print("Embedding generation successful.")
    
if __name__ == "__main__":
    test_embedder()
