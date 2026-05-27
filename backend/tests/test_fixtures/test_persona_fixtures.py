"""
Test persona fixtures to verify they work correctly
"""

import pytest
from src.db.models import MockPatient


def test_sample_personas_fixture(db_session, sample_personas):
    """Test that sample_personas fixture loads ~20 personas"""
    # Query database for loaded personas
    patients = db_session.query(MockPatient).all()

    assert len(patients) >= 15, f"Expected at least 15 personas, got {len(patients)}"
    assert len(patients) <= 25, f"Expected at most 25 personas, got {len(patients)}"

    # Verify first patient has required fields
    first_patient = patients[0]
    assert first_patient.id is not None
    assert first_patient.mrn.startswith("MOCK-")
    assert first_patient.name is not None
    assert first_patient.age > 0
    assert first_patient.gender in ['Male', 'Female', 'Other', 'Unknown']
    assert first_patient.presenting_complaint is not None
    assert first_patient.specialty is not None
    assert first_patient.difficulty in ['easy', 'medium', 'hard']


@pytest.mark.slow
def test_all_personas_fixture(db_session, all_personas):
    """Test that all_personas fixture loads 207 personas (slow test)"""
    # Query database for loaded personas
    patients = db_session.query(MockPatient).all()

    assert len(patients) >= 200, f"Expected at least 200 personas, got {len(patients)}"
    assert len(patients) <= 210, f"Expected at most 210 personas, got {len(patients)}"

    # Verify specialties are diverse
    specialties = set(p.specialty for p in patients)
    assert len(specialties) >= 3, f"Expected at least 3 specialties, got {specialties}"

    # Verify MRNs are unique
    mrns = [p.mrn for p in patients]
    assert len(mrns) == len(set(mrns)), "MRNs should be unique"


def test_all_persona_data_session_scope(all_persona_data):
    """Test that all_persona_data fixture returns raw persona dictionaries"""
    assert len(all_persona_data) >= 200
    assert len(all_persona_data) <= 210

    # Verify persona structure
    first_persona = all_persona_data[0]
    assert 'id' in first_persona
    assert 'name' in first_persona
    assert 'age' in first_persona
    assert 'specialty' in first_persona
    assert 'chief_complaint' in first_persona
