import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, JSON, Float, Date
from sqlalchemy.orm import relationship
from backend.database.base_class import Base

class ProcessingStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Source(Base):
    """
    Represents the origin of information (e.g., a specific news outlet, government portal, NGO).
    """
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    url = Column(String, nullable=True)
    type = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    data_sources = relationship("DataSource", back_populates="source")
    documents = relationship("Document", back_populates="source")

class DataSource(Base):
    """
    Represents a specific dataset or raw file obtained from a Source.
    """
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=True)
    name = Column(String, nullable=False)
    file_path = Column(String, nullable=True)
    format = Column(String, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    source = relationship("Source", back_populates="data_sources")
    evidences = relationship("Evidence", back_populates="data_source")

class Document(Base):
    """
    Represents a single unstructured or semi-structured item of text (e.g., a news article, policy document, speech).
    """
    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(Integer, ForeignKey("source.id"), nullable=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    published_date = Column(Date, nullable=True)
    status = Column(Enum(ProcessingStatus), default=ProcessingStatus.PENDING)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    source = relationship("Source", back_populates="documents")
    evidences = relationship("Evidence", back_populates="document")

class Evidence(Base):
    """
    The crucial link between raw data/documents and CivicLens assessments. 
    Represents an extracted claim or data point that provides proof for model insights.
    """
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=True)
    data_source_id = Column(Integer, ForeignKey("datasource.id"), nullable=True)

    content = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    context = Column(Text, nullable=True)

    explanation = Column(Text, nullable=True)
    supporting_values = Column(JSON, nullable=True)
    result_type = Column(String, nullable=True)
    result_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="evidences")
    data_source = relationship("DataSource", back_populates="evidences")
    model_predictions = relationship("ModelPrediction", back_populates="evidence")

class ModelPrediction(Base):
    """
    Tracks a specific prediction made by an ML model (e.g., categorizing a news article, evaluating a promise).
    """
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False, index=True)
    model_version = Column(String, nullable=False)

    target_type = Column(String, nullable=False)
    target_id = Column(String, nullable=False)

    prediction_data = Column(JSON, nullable=False)

    evidence_id = Column(Integer, ForeignKey("evidence.id"), nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    evidence = relationship("Evidence", back_populates="model_predictions")

class ModelEvaluation(Base):
    """
    Tracks evaluation metrics for different models over time to monitor degradation and improvement.
    """
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False, index=True)
    model_version = Column(String, nullable=False)

    evaluation_metric = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    dataset_reference = Column(String, nullable=True)

    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
