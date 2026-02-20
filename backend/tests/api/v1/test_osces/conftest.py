"""
Pytest fixtures for OSCE API testing
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.base import Base, get_db
from src.db.models import OSCE, OSCEType, MedicalSpecialty, DifficultyLevel

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
def sample_osce(db: Session):
    """Create sample OSCE for testing"""
    osce = OSCE(
        osce_id="OSCE-CARD-001",
        station_title="Acute Chest Pain Assessment",
        station_type=OSCEType.HISTORY_TAKING,
        clinical_scenario="58-year-old male with 2 hours of central chest pain",
        patient_instructions="You are presenting with crushing central chest pain radiating to left arm",
        marking_rubric={"introduction": {"max_marks": 1}, "history_taking": {"max_marks": 5}},
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        time_limit_minutes=8,
        learning_objectives=["SOCRATES pain assessment", "Cardiovascular risk factors"]
    )
    db.add(osce)
    db.commit()
    db.refresh(osce)
    return osce
