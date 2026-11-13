import pytest
from backend.services.source import SourceService
from backend.services.document import DocumentService
from backend.services.evidence import EvidenceService
from backend.services.model_prediction import ModelPredictionService
from backend.services.model_evaluation import ModelEvaluationService

def test_service_architecture_and_validation(db_session, sample_source, sample_document):
    """
    Test the service layer validations and repository delegation using fixtures.
    """
    with pytest.raises(ValueError, match="Source name is strictly required."):
        SourceService.create_source(db_session, obj_in={"type": "News"})
        
    source = SourceService.create_source(db_session, obj_in={"name": "The Hindu", "type": " news "})
    assert source.type == "News"
    
    with pytest.raises(ValueError, match="Both Document 'title' and 'content' are required."):
        DocumentService.create_document(db_session, obj_in={"title": "Empty Content"})
        
    doc = DocumentService.create_document(
        db_session, obj_in={"title": "Policy Document", "content": "Article body.", "source_id": sample_source.id}
    )
    assert doc.id is not None
    
    with pytest.raises(ValueError, match="Evidence content cannot be empty."):
        EvidenceService.create_evidence(db_session, document_id=sample_document.id, content="")
        
    evidence = EvidenceService.create_evidence(
        db_session, 
        document_id=sample_document.id, 
        content="Extracted claim.", 
        context="Surrounding words.",
        explanation="This claim indicates X.",
        result_type="TestAssessment",
        result_id="res_123"
    )
    assert evidence.explanation == "This claim indicates X."
    
    fetched_evidence = EvidenceService.get_evidence_for_result(db_session, "TestAssessment", "res_123")
    assert len(fetched_evidence) == 1
    
    with pytest.raises(ValueError, match="Missing required field for prediction: target_type"):
        ModelPredictionService.record_prediction(db_session, obj_in={"model_name": "classifier"}) 
        
    prediction = ModelPredictionService.record_prediction(db_session, obj_in={
        "model_name": "claim_classifier",
        "model_version": "v1.2",
        "target_type": "Claim",
        "target_id": "99",
        "prediction_data": {"confidence": 0.9, "class": "Actionable"},
        "evidence_id": evidence.id
    })
    assert prediction.model_version == "v1.2"
    
    with pytest.raises(ValueError, match="Evaluation score must be a number."):
        ModelEvaluationService.record_evaluation(db_session, obj_in={
            "model_name": "claim_classifier",
            "model_version": "v1",
            "evaluation_metric": "F1",
            "score": "not_a_number"
        })
        
    evaluation = ModelEvaluationService.record_evaluation(db_session, obj_in={
        "model_name": "claim_classifier",
        "model_version": "v1",
        "evaluation_metric": "F1",
        "score": "0.85"
    })
    assert evaluation.score == 0.85
