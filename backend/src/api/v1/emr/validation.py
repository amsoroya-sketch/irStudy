"""
EMR Validation Endpoints

POST /api/v1/emr/validation/soap-note - Validate SOAP note
POST /api/v1/emr/validation/prescription - Validate prescription (PBS)
POST /api/v1/emr/validation/pathology - Validate pathology order (MBS)

SECURITY:
- JWT authentication required
- Rate limiting: 10 requests/minute
- No PHI in error logs
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.auth.dependencies import get_current_active_user, get_current_user
from src.db.models import User
from src.api.v1.emr.validation_schemas import (
    SOAPNoteValidationRequest,
    SOAPNoteValidationResult,
    PrescriptionValidationRequest,
    PrescriptionValidationResult,
    PathologyOrderValidationRequest,
    PathologyValidationResult
)
from src.services.emr_validation_service import EMRValidationService
from src.db.models import EMRSession, MockPatient, EMRSOAPNote
from src.api.v1.emr.schemas import SessionResponse, MockPatientResponse, ValidationResult, ValidationLayerResult
from uuid import UUID

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/validation", tags=["EMR Validation"])


# ============================================================================
# POST /validation/soap-note - VALIDATE SOAP NOTE
# ============================================================================


@router.post("/soap-note", response_model=SOAPNoteValidationResult)
async def validate_soap_note(
    request: SOAPNoteValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate SOAP note documentation

    3-Layer Validation:
    1. Completeness & structure
    2. Australian medical standards (eTG, PBS, MBS)
    3. Claude AI clinical reasoning

    Args:
        request: SOAP note validation request
        current_user: Authenticated user
        db: Database session

    Returns:
        SOAPNoteValidationResult with scores and feedback

    Raises:
        401: Unauthorized (no JWT token)
        400: Bad Request (invalid session_id or missing fields)
        500: Internal Server Error (validation failed)
    """
    try:
        # Initialize validation service
        service = EMRValidationService(db)

        # Validate SOAP note
        result = await service.validate_soap_note(
            session_id=request.session_id,
            soap_note=request.soap_note,
            patient_context=request.patient_context
        )

        logger.info(
            f"SOAP validation completed: session={request.session_id[:8]}, "
            f"score={result.overall_score}/15, user={current_user.email}"
        )

        return result

    except ValueError as e:
        logger.error(f"SOAP validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"SOAP validation failed: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation service unavailable"
        )


# ============================================================================
# POST /validation/prescription - VALIDATE PRESCRIPTION (PBS)
# ============================================================================


@router.post("/prescription", response_model=PrescriptionValidationResult)
async def validate_prescription(
    request: PrescriptionValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate prescription against PBS standards

    Checks:
    - PBS listing and restrictions
    - Maximum repeats (5 for PBS)
    - Authority requirements
    - Drug interactions
    - Dose appropriateness
    - Australian terminology

    Args:
        request: Prescription validation request
        current_user: Authenticated user
        db: Database session

    Returns:
        PrescriptionValidationResult with safety score and PBS compliance

    Raises:
        401: Unauthorized
        400: Bad Request (invalid medication or dose)
        500: Internal Server Error
    """
    try:
        # Initialize validation service
        service = EMRValidationService(db)

        # Validate prescription
        result = await service.validate_prescription(
            medication_name=request.medication_name,
            dose=request.dose,
            frequency=request.frequency,
            route=request.route,
            repeats=request.repeats,
            indication=request.indication,
            authority_required=request.authority_required
        )

        logger.info(
            f"Prescription validation: med={request.medication_name}, "
            f"safety_score={result.safety_score}/10, user={current_user.email}"
        )

        return result

    except ValueError as e:
        logger.error(f"Prescription validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prescription validation failed: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation service unavailable"
        )


# ============================================================================
# POST /validation/pathology - VALIDATE PATHOLOGY ORDER (MBS)
# ============================================================================


@router.post("/pathology", response_model=PathologyValidationResult)
async def validate_pathology_order(
    request: PathologyOrderValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Validate pathology test orders against MBS

    Checks:
    - MBS item numbers and rebates
    - Clinical appropriateness
    - Overuse warnings
    - Missing essential tests
    - Cost estimate

    Args:
        request: Pathology order validation request
        current_user: Authenticated user
        db: Database session

    Returns:
        PathologyValidationResult with appropriateness score and MBS items

    Raises:
        401: Unauthorized
        400: Bad Request (invalid urgency or missing indication)
        500: Internal Server Error
    """
    try:
        # Initialize validation service
        service = EMRValidationService(db)

        # Validate pathology order
        result = await service.validate_pathology_order(
            tests_ordered=request.tests_ordered,
            indication=request.indication,
            patient_context=request.patient_context,
            urgency=request.urgency
        )

        logger.info(
            f"Pathology validation: tests={len(request.tests_ordered)}, "
            f"appropriateness={result.appropriateness_score}/10, "
            f"cost=${result.cost_estimate}, user={current_user.email}"
        )

        return result

    except ValueError as e:
        logger.error(f"Pathology validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Pathology validation failed: {type(e).__name__}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Validation service unavailable"
        )

# ============================================================================
# VALIDATION RETRIEVAL ENDPOINT (for backward compatibility)
# ============================================================================

@router.get("/{validation_id}", response_model=SessionResponse)
async def get_validation_results(
    validation_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve validation results by validation_id.
    
    For backward compatibility, validation_id is an alias for session_id.
    This endpoint returns the same data as GET /sessions/{session_id}.
    """
    # validation_id is the same as session_id
    emr_session = db.query(EMRSession).filter(
        EMRSession.id == validation_id,
        EMRSession.user_id == current_user.id
    ).first()

    if not emr_session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Validation results not found",
        )

    # Fetch patient
    mock_patient = db.query(MockPatient).filter(MockPatient.id == emr_session.patient_id).first()

    # Query SOAP note from separate table
    soap_note_record = db.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == emr_session.id,
        EMRSOAPNote.is_final_submission == True
    ).first()
    
    soap_note_dict = None
    if soap_note_record:
        soap_note_dict = {
            "subjective": soap_note_record.subjective,
            "objective": soap_note_record.objective,
            "assessment": soap_note_record.assessment,
            "plan": soap_note_record.plan
        }

    # Build validation results when the session has been graded, OR when a prior
    # submit hit an AI outage (score_breakdown carries ai_unavailable=True but the
    # session was deliberately left un-graded). In the outage case we surface the
    # ai_unavailable flag and a None pass_fail so the client never reads back a
    # fabricated PASS/FAIL for a session the AI never actually graded.
    validation_results = None
    breakdown = emr_session.score_breakdown or {}
    ai_unavailable = bool(breakdown.get("ai_unavailable"))
    if breakdown and (emr_session.status == "graded" or ai_unavailable):
        # pass_fail is the authoritative decision persisted at submit time. It is
        # None when the AI layer was unavailable; do NOT recompute it here.
        validation_results = ValidationResult(
            overall_score=breakdown.get("overall_score", 0.0),
            pass_fail=breakdown.get("pass_fail"),
            category_scores=breakdown.get("category_scores", {}),
            completeness=breakdown.get("completeness") or None,
            captured=breakdown.get("captured", []),
            missing_elements=breakdown.get("missing_elements", []),
            strengths=breakdown.get("strengths", []),
            improvements=breakdown.get("improvements", []),
            red_flags=breakdown.get("red_flags", []),
            australian_compliance=breakdown.get("australian_compliance", {}),
            ai_unavailable=True if ai_unavailable else None,
            layer_1_zod=ValidationLayerResult(**breakdown.get("layer_1_zod", {"passed": True, "errors": []})),
            layer_2_python=ValidationLayerResult(**breakdown.get("layer_2_python", {"passed": True, "errors": []})),
            layer_3_ai=ValidationLayerResult(**breakdown.get("layer_3_ai", {"passed": True, "errors": []})),
            performance_summary=breakdown.get("performance_summary", {}),
            next_steps=breakdown.get("next_steps", {}),
        )

    return SessionResponse(
        session_id=emr_session.id,
        validation_id=emr_session.id,
        patient=MockPatientResponse(
            id=mock_patient.id,
            name=mock_patient.name,
            age=mock_patient.age,
            gender=mock_patient.gender,
            presenting_complaint=mock_patient.presenting_complaint,
            specialty=mock_patient.specialty,
            vital_signs=mock_patient.vital_signs,
            medical_history=mock_patient.medical_history,
        ),
        specialty=emr_session.specialty,
        difficulty=emr_session.difficulty,
        started_at=emr_session.started_at,
        submitted_at=emr_session.submitted_at,
        elapsed_time_seconds=emr_session.elapsed_time_seconds or 0,
        status=emr_session.status,
        auto_save_count=emr_session.auto_save_count or 0,
        last_auto_save_at=emr_session.last_auto_save_at,
        validation_score=emr_session.validation_score,
        total_amc_score=emr_session.validation_score,
        validation_results=validation_results,
        soap_note=soap_note_dict,
        typing_metrics=emr_session.typing_metrics,
        performance_summary=emr_session.score_breakdown.get("performance_summary") if emr_session.score_breakdown else None,
        next_steps=emr_session.score_breakdown.get("next_steps") if emr_session.score_breakdown else None,
    )
