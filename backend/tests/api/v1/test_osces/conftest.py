"""
Pytest fixtures for OSCE API testing

NOTE: This conftest imports fixtures from the parent test suite:
- db_session: Database session from tests/conftest.py
- client: FastAPI test client from tests/conftest.py
- auth_headers: JWT authentication headers from tests/conftest.py
- test_user: Test user fixture from tests/conftest.py

These fixtures are automatically available to all tests in this directory.
"""

import pytest
from sqlalchemy.orm import Session

from src.db.models import OSCE, OSCEType, MedicalSpecialty, DifficultyLevel


# ============================================================================
# OSCE FIXTURES
# ============================================================================


@pytest.fixture
def sample_osce(db_session: Session):
    """
    Create sample OSCE for testing.

    Uses current schema with correct field names:
    - patient_instructions (not clinical_scenario)
    - candidate_instructions (required field)
    - rubric (not marking_rubric)
    - is_published=True (required for endpoint access)
    """
    osce = OSCE(
        osce_id="OSCE-CARD-001",
        station_title="Acute Chest Pain Assessment",
        station_type=OSCEType.HISTORY_TAKING,
        patient_instructions=(
            "You are a 58-year-old male presenting with crushing central chest pain "
            "radiating to your left arm. Started 2 hours ago while watching television. "
            "You appear anxious and sweaty."
        ),
        candidate_instructions=(
            "You are in the emergency department. "
            "A 58-year-old male presents with chest pain. "
            "Take a focused history using the SOCRATES framework. "
            "You have 8 minutes."
        ),
        examiner_instructions=(
            "Assess the candidate's ability to take a systematic cardiovascular history. "
            "Award marks for SOCRATES framework, red flag identification, and communication."
        ),
        rubric={
            "history_examination": {"max_marks": 3, "criteria": "Systematic SOCRATES assessment"},
            "clinical_reasoning": {"max_marks": 3, "criteria": "Identifies ACS as differential"},
            "communication": {"max_marks": 3, "criteria": "Clear, empathetic communication"},
            "safety": {"max_marks": 3, "criteria": "Identifies red flags and urgency"},
            "professionalism": {"max_marks": 3, "criteria": "Professional manner, patient comfort"}
        },
        specialty=MedicalSpecialty.CARDIOLOGY,
        difficulty=DifficultyLevel.MEDIUM,
        time_limit_minutes=8,
        learning_objectives=[
            "Apply SOCRATES framework for pain history",
            "Identify red flags for acute coronary syndrome",
            "Communicate effectively with anxious patient"
        ],
        tags=["chest pain", "history taking", "ACS", "emergency"],
        red_flags=[
            "Sudden onset severe chest pain",
            "Radiation to left arm/jaw",
            "Diaphoresis",
            "Cardiovascular risk factors"
        ],
        is_published=True  # Required for endpoint access
    )
    db_session.add(osce)
    db_session.commit()
    db_session.refresh(osce)
    return osce
