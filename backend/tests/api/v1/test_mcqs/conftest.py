"""
Pytest fixtures for MCQ API testing

NOTE: This conftest only provides MCQ-specific fixtures.
Database setup (db_session, client, test_user, auth_headers) comes from global conftest.
"""

import pytest
from sqlalchemy.orm import Session

from src.db.models import MCQ, MedicalSpecialty, DifficultyLevel


@pytest.fixture
def sample_mcq(db_session: Session):
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
    db_session.add(mcq)
    db_session.commit()
    db_session.refresh(mcq)
    return mcq
