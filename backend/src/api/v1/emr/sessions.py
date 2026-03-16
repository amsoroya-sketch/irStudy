"""
EMR Session Management Endpoints

ENDPOINTS:
- POST /sessions - Create new EMR practice session
- GET /sessions/{session_id} - Retrieve session details
- POST /sessions/{session_id}/submit - Submit SOAP note for validation

SECURITY:
- JWT authentication required
- User can only access their own sessions
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from src.db.base import get_db
from src.db.models import User
from src.auth.dependencies import get_current_user
from .schemas import (
    CreateSessionRequest,
    SessionResponse,
    SubmitSessionRequest,
    SubmitSessionResponse,
    MockPatientResponse,
    ValidationResult,
    ValidationLayerResult,
)
from .validation import validate_soap_note

# Import database models
# Note: These models exist based on migration 20260215_1200_008_add_emr_tables.py
# We need to check if they're defined in src/db/models.py
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from src.db.base import Base
import uuid


# Temporary model definitions (if not in models.py)
class MockPatient(Base):
    __tablename__ = "mock_patients"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mrn = Column(String(20))
    name = Column(String(100))
    age = Column(Integer)
    gender = Column(String(20))
    presenting_complaint = Column(Text)
    vital_signs = Column(JSON)
    medical_history = Column(JSON)
    specialty = Column(String(50))
    difficulty = Column(String(20))


class EMRSession(Base):
    __tablename__ = "emr_sessions"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.id"))
    patient_id = Column(PGUUID(as_uuid=True), ForeignKey("mock_patients.id"))
    specialty = Column(String(50))
    difficulty = Column(String(20))
    started_at = Column(DateTime, default=datetime.utcnow)
    submitted_at = Column(DateTime, nullable=True)
    elapsed_time_seconds = Column(Integer, nullable=True)
    validation_score = Column(Float, nullable=True)
    score_breakdown = Column(JSON, nullable=True)
    status = Column(String(20), default="in_progress")


class EMRSOAPNote(Base):
    __tablename__ = "emr_soap_notes"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("emr_sessions.id"))
    subjective = Column(Text)
    objective = Column(Text)
    assessment = Column(Text)
    plan = Column(Text)
    is_final_submission = Column(Boolean, default=False)


class EMRPrescription(Base):
    __tablename__ = "emr_prescriptions"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("emr_sessions.id"))
    medication_name = Column(String(200))
    dose = Column(String(50))
    frequency = Column(String(50))
    route = Column(String(20))


class EMRPathologyOrder(Base):
    __tablename__ = "emr_pathology_orders"
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(PGUUID(as_uuid=True), ForeignKey("emr_sessions.id"))
    test_name = Column(String(200))
    urgency = Column(String(20))
    indication = Column(Text)


router = APIRouter()


# ============================================================================
# ENDPOINT 1: CREATE SESSION
# ============================================================================


@router.post("/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create new EMR practice session

    FLOW:
    1. Validate mock patient exists
    2. Create session record
    3. Return session + patient information

    AUTHORIZATION:
    - User can create unlimited practice sessions
    """
    # Validate mock patient exists
    mock_patient = (
        db.query(MockPatient).filter(MockPatient.id == request.mock_patient_id).first()
    )

    if not mock_patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mock patient {request.mock_patient_id} not found",
        )

    # Create session
    emr_session = EMRSession(
        user_id=current_user.id,
        patient_id=request.mock_patient_id,
        specialty=mock_patient.specialty,
        difficulty=mock_patient.difficulty,
        status="in_progress",
    )

    db.add(emr_session)
    db.commit()
    db.refresh(emr_session)

    # Build response
    return SessionResponse(
        session_id=emr_session.id,
        mock_patient=MockPatientResponse(
            patient_id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        emr_system=request.emr_system,
        started_at=emr_session.started_at,
        submitted_at=None,
        status="in_progress",
        soap_note=None,
        validation_result=None,
    )


# ============================================================================
# ENDPOINT 2: GET SESSION
# ============================================================================


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve EMR session details

    AUTHORIZATION:
    - User can only access their own sessions
    """
    # Fetch session with authorization check
    emr_session = (
        db.query(EMRSession)
        .filter(EMRSession.id == session_id, EMRSession.user_id == current_user.id)
        .first()
    )

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )

    # Fetch related data
    mock_patient = (
        db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()
    )

    soap_note = (
        db.query(EMRSOAPNote)
        .filter(
            EMRSOAPNote.session_id == session_id, EMRSOAPNote.is_final_submission == True
        )
        .first()
    )

    # Build SOAP note dict
    soap_note_dict = None
    if soap_note:
        soap_note_dict = {
            "subjective": soap_note.subjective,
            "objective": soap_note.objective,
            "assessment": soap_note.assessment,
            "plan": soap_note.plan,
        }

    # Build validation result
    validation_result = None
    if emr_session.score_breakdown:
        validation_result = ValidationResult(
            overall_score=emr_session.validation_score or 0,
            layer_1_rule_based=ValidationLayerResult(
                score=emr_session.score_breakdown.get("layer_1_rule_based", {}).get(
                    "score", 0
                ),
                feedback=emr_session.score_breakdown.get("layer_1_rule_based", {}).get(
                    "feedback", ""
                ),
                errors=emr_session.score_breakdown.get("layer_1_rule_based", {}).get(
                    "errors", []
                ),
            ),
            layer_2_claude_ai=(
                ValidationLayerResult(
                    score=emr_session.score_breakdown.get("layer_2_claude_ai", {}).get(
                        "score", 0
                    ),
                    feedback=emr_session.score_breakdown.get("layer_2_claude_ai", {}).get(
                        "feedback", ""
                    ),
                    errors=[],
                )
                if emr_session.score_breakdown.get("layer_2_claude_ai")
                else None
            ),
            layer_3_specialist=None,
            pass_fail=emr_session.score_breakdown.get("pass_fail", "FAIL"),
            time_taken_seconds=emr_session.elapsed_time_seconds or 0,
        )

    return SessionResponse(
        session_id=emr_session.id,
        mock_patient=MockPatientResponse(
            patient_id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        emr_system="epic",  # Default (can be stored in session if needed)
        started_at=emr_session.started_at,
        submitted_at=emr_session.submitted_at,
        status=emr_session.status,
        soap_note=soap_note_dict,
        validation_result=validation_result,
    )


# ============================================================================
# ENDPOINT 3: SUBMIT SESSION
# ============================================================================


@router.post("/sessions/{session_id}/submit", response_model=SubmitSessionResponse)
async def submit_session(
    session_id: UUID,
    request: SubmitSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit SOAP note for validation

    FLOW:
    1. Validate session exists and belongs to user
    2. Check session not already submitted
    3. Save SOAP note, prescriptions, pathology orders
    4. Run 3-layer validation
    5. Update session with results
    6. Return validation result

    PERFORMANCE TARGET: <500ms (p95)
    """
    # Fetch session (authorization check)
    emr_session = (
        db.query(EMRSession)
        .filter(EMRSession.id == session_id, EMRSession.user_id == current_user.id)
        .first()
    )

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or access denied",
        )

    if emr_session.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session already submitted",
        )

    # Save SOAP note
    soap_note_record = EMRSOAPNote(
        session_id=session_id,
        subjective=request.soap_note.subjective,
        objective=request.soap_note.objective,
        assessment=request.soap_note.assessment,
        plan=request.soap_note.plan,
        is_final_submission=True,
    )
    db.add(soap_note_record)

    # Save prescriptions
    for prescription in request.prescriptions:
        prescription_record = EMRPrescription(
            session_id=session_id,
            medication_name=prescription.medication,
            dose=prescription.dose,
            frequency=prescription.frequency,
            route=prescription.route,
        )
        db.add(prescription_record)

    # Save pathology orders
    for pathology in request.pathology_orders:
        pathology_record = EMRPathologyOrder(
            session_id=session_id,
            test_name=pathology.test_name,
            urgency=pathology.urgency,
            indication=pathology.clinical_notes,
        )
        db.add(pathology_record)

    # Calculate elapsed time
    elapsed_time = int((datetime.utcnow() - emr_session.started_at).total_seconds())

    # Fetch patient context for validation
    mock_patient = (
        db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()
    )

    patient_context = {
        "presenting_complaint": mock_patient.presenting_complaint,
        "age": mock_patient.age,
        "gender": mock_patient.gender,
        "vital_signs": mock_patient.vital_signs,
        "medical_history": mock_patient.medical_history,
    }

    # Run 3-layer validation
    validation_result = await validate_soap_note(
        soap_note={
            "subjective": request.soap_note.subjective,
            "objective": request.soap_note.objective,
            "assessment": request.soap_note.assessment,
            "plan": request.soap_note.plan,
        },
        patient_context=patient_context,
        time_taken_seconds=elapsed_time,
    )

    # Update session
    emr_session.status = "validated"
    emr_session.submitted_at = datetime.utcnow()
    emr_session.elapsed_time_seconds = elapsed_time
    emr_session.validation_score = validation_result["overall_score"]
    emr_session.score_breakdown = validation_result

    db.commit()

    # Build response
    return SubmitSessionResponse(
        session_id=session_id,
        submitted_at=emr_session.submitted_at,
        validation_result=ValidationResult(
            overall_score=validation_result["overall_score"],
            layer_1_rule_based=ValidationLayerResult(
                score=validation_result["layer_1_rule_based"]["score"],
                feedback=validation_result["layer_1_rule_based"]["feedback"],
                errors=validation_result["layer_1_rule_based"]["errors"],
            ),
            layer_2_claude_ai=(
                ValidationLayerResult(
                    score=validation_result["layer_2_claude_ai"]["score"],
                    feedback=validation_result["layer_2_claude_ai"]["feedback"],
                    errors=[],
                )
                if validation_result["layer_2_claude_ai"]
                else None
            ),
            layer_3_specialist=None,
            pass_fail=validation_result["pass_fail"],
            time_taken_seconds=elapsed_time,
        ),
    )
