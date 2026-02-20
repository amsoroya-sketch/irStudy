"""
Pytest fixtures for MCQ API testing
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.base import Base, get_db
from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel

SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables once when module loads
Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def db():
    """Create fresh database session for each test"""
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """FastAPI test client with db dependency override"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_mcq(db: Session):
    """Create sample MCQ for testing"""
    mcq = MCQ(
        question_id="MCQ-CARD-001",
        question_text="A 58-year-old male presents with central crushing chest pain for 2 hours. ECG shows ST elevation in leads II, III, aVF. What is the most appropriate immediate management?",
        options={
            "A": "Aspirin 300mg and arrange outpatient cardiology review",
            "B": "Aspirin 300mg, clopidogrel 300mg, activate cath lab for primary PCI",
            "C": "Observation with serial troponins and beta-blocker",
            "D": "Thrombolysis with tenecteplase",
            "E": "High-flow oxygen and GTN infusion"
        },
        correct_answer="B",
        explanation="This patient has an inferior STEMI (ST elevation in II, III, aVF). The gold standard treatment in Australia is primary PCI within 90 minutes. Dual antiplatelet therapy (aspirin + P2Y12 inhibitor) should be given immediately unless contraindicated.",
        citation="eTG Cardiovascular - Acute Coronary Syndromes. Primary PCI is preferred over thrombolysis when available within 90 minutes for STEMI.",
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        learning_points=["STEMI diagnosis criteria", "Primary PCI vs thrombolysis", "Dual antiplatelet therapy"]
    )
    db.add(mcq)
    db.commit()
    db.refresh(mcq)
    return mcq
