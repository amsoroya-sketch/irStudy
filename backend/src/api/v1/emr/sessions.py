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

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from typing import List, Optional

from src.db.base import get_db
from src.db.models import (
    User,
    MockPatient,
    EMRSession,
    EMRSOAPNote,
    EMRPrescription,
    EMRPathologyOrder,
)
from src.auth.dependencies import get_current_user
from .schemas import (
    CreateSessionRequest,
    SessionResponse,
    SubmitSessionRequest,
    SubmitSessionResponse,
    MockPatientResponse,
    ValidationResult,
    ValidationLayerResult,
    SessionHistoryResponse,
    SessionHistoryItem,
    PaginationInfo,
)
from .validation import validate_soap_note


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
# ENDPOINT 2: LIST SESSIONS
# ============================================================================


@router.get("/sessions", response_model=SessionHistoryResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Number of sessions per page"),
    offset: int = Query(0, ge=0, description="Offset from start"),
    sort_by: str = Query("started_at", description="Field to sort by (started_at, submitted_at)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
):
    """
    List user's EMR sessions with pagination and sorting

    AUTHORIZATION:
    - User can only access their own sessions

    SORTING:
    - sort_by: started_at (default), submitted_at
    - sort_order: desc (newest first, default), asc (oldest first)

    SQL INJECTION PROTECTION:
    - Whitelist validation for sort_by parameter
    - Enum validation for sort_order parameter
    """
    # SQL injection protection: Whitelist valid sort fields
    valid_sort_fields = {"started_at", "submitted_at"}
    if sort_by not in valid_sort_fields:
        sort_by = "started_at"  # Fallback to default

    # SQL injection protection: Validate sort order
    if sort_order.lower() not in {"asc", "desc"}:
        sort_order = "desc"  # Fallback to default

    # Build base query
    query = (
        db.query(EMRSession, MockPatient)
        .join(MockPatient, EMRSession.patient_id == MockPatient.id)
        .filter(EMRSession.user_id == current_user.id)
    )

    # Get total count
    total_count = query.count()

    # Apply sorting
    sort_column = getattr(EMRSession, sort_by)
    if sort_order.lower() == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    # Apply pagination
    query = query.limit(limit).offset(offset)

    # Execute query
    results = query.all()

    # Build session history items
    sessions = []
    for emr_session, mock_patient in results:
        # Calculate time taken if session is submitted
        time_taken_minutes = None
        if emr_session.submitted_at and emr_session.started_at:
            time_delta = emr_session.submitted_at - emr_session.started_at
            time_taken_minutes = round(time_delta.total_seconds() / 60, 2)

        sessions.append(
            SessionHistoryItem(
                session_id=emr_session.id,
                mock_patient_name=mock_patient.name,
                specialty=emr_session.specialty,
                chief_complaint=mock_patient.presenting_complaint or "Not specified",
                submitted_at=emr_session.submitted_at,
                score=emr_session.validation_score,
                pass_fail="pass" if emr_session.validation_score and emr_session.validation_score >= 70 else "fail" if emr_session.validation_score else None,
                time_taken_minutes=time_taken_minutes,
            )
        )

    return SessionHistoryResponse(
        total_count=total_count,
        sessions=sessions,
        pagination=PaginationInfo(
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total_count,
        ),
    )


# ============================================================================
# ENDPOINT 3: GET SESSION
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
