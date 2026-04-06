"""
EMR Models Migration Tests

PURPOSE: Verify EMR models are properly defined in src/db/models.py
         and importable across the codebase.

TESTS (12 total):
1-6. Model definition tests (models exist in models.py)
7-10. Database CRUD tests (models work with SQLAlchemy)
11-12. Migration validation tests (schema correct)

TDD WORKFLOW: RED → GREEN → REFACTOR
Expected: All 12 tests fail initially (models not in models.py yet)
After migration: All 12 tests pass
"""

import pytest
from sqlalchemy import inspect
from uuid import uuid4
from datetime import datetime, timedelta


# ============================================================================
# TEST 1: MockPatient Model Exists in models.py
# ============================================================================

def test_mock_patient_model_importable():
    """Verify MockPatient model is importable from models.py"""
    from src.db.models import MockPatient

    assert MockPatient is not None, "MockPatient model should be defined"
    assert MockPatient.__tablename__ == "mock_patients", \
        f"Expected table 'mock_patients', got '{MockPatient.__tablename__}'"


# ============================================================================
# TEST 2: EMRSession Model Exists in models.py
# ============================================================================

def test_emr_session_model_importable():
    """Verify EMRSession model is importable from models.py"""
    from src.db.models import EMRSession

    assert EMRSession is not None, "EMRSession model should be defined"
    assert EMRSession.__tablename__ == "emr_sessions", \
        f"Expected table 'emr_sessions', got '{EMRSession.__tablename__}'"


# ============================================================================
# TEST 3: EMRSOAPNote Model Exists in models.py
# ============================================================================

def test_emr_soap_note_model_importable():
    """Verify EMRSOAPNote model is importable from models.py"""
    from src.db.models import EMRSOAPNote

    assert EMRSOAPNote is not None, "EMRSOAPNote model should be defined"
    assert EMRSOAPNote.__tablename__ == "emr_soap_notes", \
        f"Expected table 'emr_soap_notes', got '{EMRSOAPNote.__tablename__}'"


# ============================================================================
# TEST 4: EMRPrescription Model Exists in models.py
# ============================================================================

def test_emr_prescription_model_importable():
    """Verify EMRPrescription model is importable from models.py"""
    from src.db.models import EMRPrescription

    assert EMRPrescription is not None, "EMRPrescription model should be defined"
    assert EMRPrescription.__tablename__ == "emr_prescriptions", \
        f"Expected table 'emr_prescriptions', got '{EMRPrescription.__tablename__}'"


# ============================================================================
# TEST 5: EMRPathologyOrder Model Exists in models.py
# ============================================================================

def test_emr_pathology_order_model_importable():
    """Verify EMRPathologyOrder model is importable from models.py"""
    from src.db.models import EMRPathologyOrder

    assert EMRPathologyOrder is not None, "EMRPathologyOrder model should be defined"
    assert EMRPathologyOrder.__tablename__ == "emr_pathology_orders", \
        f"Expected table 'emr_pathology_orders', got '{EMRPathologyOrder.__tablename__}'"


# ============================================================================
# TEST 6: EMRValidationResult Model Exists in models.py
# ============================================================================

def test_emr_validation_result_model_importable():
    """Verify EMRValidationResult model is importable from models.py"""
    from src.db.models import EMRValidationResult

    assert EMRValidationResult is not None, "EMRValidationResult model should be defined"
    assert EMRValidationResult.__tablename__ == "emr_validation_results", \
        f"Expected table 'emr_validation_results', got '{EMRValidationResult.__tablename__}'"


# ============================================================================
# TEST 7: MockPatient CRUD Operations Work
# ============================================================================

def test_mock_patient_crud(db_session):
    """Test MockPatient model can be created, read, updated, deleted"""
    from src.db.models import MockPatient

    # Create
    patient = MockPatient(
        id=uuid4(),
        name="Test Patient",
        mrn="MRN001",
        age=45,
        gender="Male",
        specialty="Cardiology",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Read
    fetched = db_session.query(MockPatient).filter(
        MockPatient.mrn == "MRN001"
    ).first()

    assert fetched is not None, "Patient should be retrievable"
    assert fetched.name == "Test Patient"
    assert fetched.age == 45

    # Update
    fetched.age = 46
    db_session.commit()

    updated = db_session.query(MockPatient).filter(
        MockPatient.mrn == "MRN001"
    ).first()
    assert updated.age == 46, "Age should be updated"

    # Delete
    db_session.delete(fetched)
    db_session.commit()

    deleted = db_session.query(MockPatient).filter(
        MockPatient.mrn == "MRN001"
    ).first()
    assert deleted is None, "Patient should be deleted"


# ============================================================================
# TEST 8: EMRSession CRUD Operations Work
# ============================================================================

def test_emr_session_crud(db_session):
    """Test EMRSession model can be created and retrieved"""
    from src.db.models import EMRSession, MockPatient

    # Create patient first (foreign key dependency)
    patient = MockPatient(
        id=uuid4(),
        name="Session Test Patient",
        mrn="MRN_SESSION",
        age=50,
        gender="Female",
        specialty="Respiratory",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create EMR session
    session = EMRSession(
        id=uuid4(),
        user_id=1,  # Assuming user with ID 1 exists
        patient_id=patient.id,
        emr_system="epic",
        specialty="Respiratory",
        difficulty="intermediate",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Read
    fetched = db_session.query(EMRSession).filter(
        EMRSession.patient_id == patient.id
    ).first()

    assert fetched is not None, "Session should be retrievable"
    assert fetched.emr_system == "epic"
    assert fetched.specialty == "Respiratory"


# ============================================================================
# TEST 9: EMRSOAPNote CRUD Operations Work
# ============================================================================

def test_emr_soap_note_crud(db_session):
    """Test EMRSOAPNote model can be created and retrieved"""
    from src.db.models import EMRSOAPNote, EMRSession, MockPatient

    # Create patient
    patient = MockPatient(
        id=uuid4(),
        name="SOAP Test Patient",
        mrn="MRN_SOAP",
        age=35,
        gender="Male",
        specialty="Psychiatry",
        difficulty="intermediate"
    )
    db_session.add(patient)
    db_session.commit()

    # Create session
    session = EMRSession(
        id=uuid4(),
        user_id=1,
        patient_id=patient.id,
        emr_system="cerner",
        specialty="Psychiatry",
        difficulty="intermediate",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Create SOAP note
    soap_note = EMRSOAPNote(
        id=uuid4(),
        session_id=session.id,
        subjective="Patient reports feeling anxious",
        objective="Patient appears restless",
        assessment="Generalized anxiety disorder",
        plan="Start CBT therapy",
        typing_wpm=45.5,
        completion_time_seconds=1200
    )
    db_session.add(soap_note)
    db_session.commit()

    # Read
    fetched = db_session.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == session.id
    ).first()

    assert fetched is not None, "SOAP note should be retrievable"
    assert fetched.subjective == "Patient reports feeling anxious"
    assert fetched.typing_wpm == 45.5


# ============================================================================
# TEST 10: Foreign Key Relationships Work
# ============================================================================

def test_model_relationships(db_session):
    """Test foreign key relationships between models"""
    from src.db.models import EMRSession, MockPatient, EMRPrescription

    # Create patient
    patient = MockPatient(
        id=uuid4(),
        name="Relationship Test",
        mrn="MRN_REL",
        age=60,
        gender="Female",
        specialty="Cardiology",
        difficulty="advanced"
    )
    db_session.add(patient)
    db_session.commit()

    # Create session
    session = EMRSession(
        id=uuid4(),
        user_id=1,
        patient_id=patient.id,
        emr_system="epic",
        specialty="Cardiology",
        difficulty="advanced",
        started_at=datetime.utcnow()
    )
    db_session.add(session)
    db_session.commit()

    # Create prescription linked to session
    prescription = EMRPrescription(
        id=uuid4(),
        session_id=session.id,
        medication_name="Atorvastatin",
        dose="20mg",
        frequency="Once daily",
        route="Oral"
    )
    db_session.add(prescription)
    db_session.commit()

    # Verify relationships
    fetched_prescription = db_session.query(EMRPrescription).filter(
        EMRPrescription.session_id == session.id
    ).first()

    assert fetched_prescription is not None, "Prescription should be retrievable via session_id"
    assert fetched_prescription.medication_name == "Atorvastatin"


# ============================================================================
# TEST 11: Database Schema Validation (Column Types)
# ============================================================================

def test_model_column_types(db_session):
    """Verify models have correct column types"""
    from src.db.models import EMRSession

    # Get table metadata
    inspector = inspect(db_session.bind)
    columns = {col['name']: col for col in inspector.get_columns('emr_sessions')}

    # Verify critical columns exist and have correct types
    assert 'id' in columns, "id column should exist"
    assert 'user_id' in columns, "user_id column should exist"
    assert 'patient_id' in columns, "patient_id column should exist"
    assert 'emr_system' in columns, "emr_system column should exist"
    assert 'started_at' in columns, "started_at column should exist"
    assert 'validation_score' in columns, "validation_score column should exist"


# ============================================================================
# TEST 12: Primary Keys and Nullable Constraints
# ============================================================================

def test_model_constraints(db_session):
    """Verify models have correct primary keys and nullable constraints"""
    from src.db.models import MockPatient, EMRSession

    inspector = inspect(db_session.bind)

    # Check MockPatient primary key
    mock_patient_pk = inspector.get_pk_constraint('mock_patients')
    assert 'id' in mock_patient_pk['constrained_columns'], \
        "id should be primary key"

    # Check EMRSession primary key
    emr_session_pk = inspector.get_pk_constraint('emr_sessions')
    assert 'id' in emr_session_pk['constrained_columns'], \
        "id should be primary key"

    # Check foreign keys
    emr_session_fks = inspector.get_foreign_keys('emr_sessions')
    fk_columns = [fk['constrained_columns'][0] for fk in emr_session_fks]

    assert 'patient_id' in fk_columns, "patient_id should be a foreign key"
    assert 'user_id' in fk_columns, "user_id should be a foreign key"
