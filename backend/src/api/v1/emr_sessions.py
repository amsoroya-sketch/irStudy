"""
EMR Session Management API

Routes:
- POST /api/v1/emr/sessions/start - Start new EMR practice session
- PUT /api/v1/emr/sessions/{session_id} - Auto-save session draft
- POST /api/v1/emr/sessions/{session_id}/submit - Submit for validation
- GET /api/v1/emr/sessions/{session_id} - Get session details
- GET /api/v1/emr/sessions - List sessions (with filters)
- DELETE /api/v1/emr/sessions/{session_id} - Delete draft session

AUSTRALIAN MEDICAL CONTEXT:
- Epic EHR and Cerner PowerChart simulation
- PBS-compliant prescriptions
- MBS pathology orders
- AHPRA standards compliance

PERFORMANCE TARGETS:
- Auto-save: <200ms p95
- Start session: <500ms p95
- Submit: <500ms p95 (optimized)
- Get/List: <300ms p95
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User
from src.auth.dependencies import get_current_active_user
from src.schemas.emr import (
    SessionStartRequest,
    SessionStartResponse,
    SessionUpdateRequest,
    SessionUpdateResponse,
    SessionSubmitRequest,
    SessionSubmitResponse,
    SessionDetailResponse,
    SessionListResponse,
    SessionSummary,
    MockPatientResponse,
    SOAPNoteResponse,
    PrescriptionResponse,
    PathologyOrderResponse,
)
from src.services.emr.session_service import SessionService
from src.services.emr.patient_service import PatientService
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emr/sessions", tags=["EMR Sessions"])


# ============================================================================
# START SESSION
# ============================================================================

@router.post("/start", response_model=SessionStartResponse,
             summary="Start New EMR Practice Session",
             description="""
Start a new EMR practice session with a randomly assigned patient.

**Workflow:**
1. Select EMR system (Cerner PowerChart or Epic EHR)
2. Optionally filter patients by specialty and complexity
3. System assigns a random patient matching criteria
4. Session created with timer started

**Limits:**
- Maximum 5 concurrent active sessions per user
- Patients already completed by user excluded (if flag set)
""",
             responses={
                 200: {"description": "Session started successfully"},
                 429: {"description": "Too many active sessions (max 5)"},
                 404: {"description": "No available patients matching criteria"}
             })
async def start_session(
    request: SessionStartRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start new EMR practice session.

    Performance: <500ms target
    """
    try:
        # Get patient (random or OSCE-linked)
        if request.osce_id:
            patient = PatientService.get_patient_for_osce(db, request.osce_id)
            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No patient found for OSCE {request.osce_id}"
                )
        else:
            # Get random patient with filters
            specialty = request.patient_filter.specialty if request.patient_filter else None
            complexity = request.patient_filter.complexity if request.patient_filter else None
            exclude_user = current_user.id if (request.patient_filter and request.patient_filter.exclude_completed) else None

            patient = PatientService.get_random_patient(
                db,
                specialty=specialty,
                complexity=complexity,
                exclude_user_completed=exclude_user
            )

            if not patient:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No available patients matching criteria"
                )

        # Create session
        session_result = SessionService.create_session(
            db,
            user_id=current_user.id,
            patient_id=patient["id"],
            emr_system=request.emr_system,
            osce_id=request.osce_id
        )

        # Build response
        return SessionStartResponse(
            session_id=session_result["session_id"],
            patient=MockPatientResponse(
                id=patient["id"],
                mrn=patient.get("mrn", ""),
                full_name=patient.get("name", ""),
                age=patient.get("age", 0),
                gender=patient.get("gender", ""),
                allergies=patient.get("allergies", []),
                current_medications=patient.get("medications", []),
                vital_signs=patient.get("vital_signs", {}),
                presenting_complaint=patient.get("presenting_complaint", ""),
                clinical_scenario=patient.get("clinical_scenario", ""),
                specialty=patient.get("specialty", ""),
                complexity_level=patient.get("complexity_level", patient.get("difficulty", "")),
                demographics=patient.get("demographics", {}),
                medical_history=patient.get("medical_history"),
                medications=patient.get("medications"),
                physical_exam_findings=patient.get("physical_exam_findings"),
                investigation_results=patient.get("investigation_results")
            ),
            emr_system=request.emr_system,
            started_at=session_result["started_at"],
            session_data={}
        )

    except ValueError as e:
        # Max sessions or patient not found
        if "Maximum" in str(e):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start session"
        )


# ============================================================================
# UPDATE SESSION (AUTO-SAVE)
# ============================================================================

@router.put("/{session_id}", response_model=SessionUpdateResponse,
            summary="Auto-Save Session Draft",
            description="""
Auto-save EMR session draft data.

**Triggered:** Every 30 seconds by frontend
**Performance:** <200ms target (user shouldn't notice delay)
**Data:** JSONB merge (preserves existing keys)
""",
            responses={
                200: {"description": "Draft saved successfully"},
                401: {"description": "User doesn't own this session"},
                404: {"description": "Session not found"},
                409: {"description": "Session already completed"}
            })
async def update_session(
    session_id: str,
    request: SessionUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Auto-save session draft data.

    Performance: <200ms target (critical for UX)
    """
    try:
        auto_saved_at = SessionService.update_session_data(
            db,
            session_id=session_id,
            user_id=current_user.id,
            session_data=request.session_data
        )

        return SessionUpdateResponse(
            session_id=session_id,
            auto_saved_at=auto_saved_at,
            message="Draft saved successfully"
        )

    except ValueError as e:
        error_msg = str(e)
        if "already submitted" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Error updating session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save draft"
        )


# ============================================================================
# SUBMIT SESSION
# ============================================================================

@router.post("/{session_id}/submit", response_model=SessionSubmitResponse,
             summary="Submit EMR Session for Validation",
             description="""
Submit completed EMR session for AI validation.

**Steps (atomic transaction):**
1. Mark session complete
2. Create SOAP note record
3. Create prescription records
4. Create pathology order records
5. Update user progress
6. Queue validation (async)

**Performance:** <500ms target (optimized)
**Validation:** 3-layer system (Rule-based → Python → Claude AI)
""",
             responses={
                 200: {"description": "Session submitted successfully"},
                 401: {"description": "Unauthorized"},
                 404: {"description": "Session not found"},
                 409: {"description": "Session already submitted"},
                 422: {"description": "Validation failed (e.g., subjective too short)"}
             })
async def submit_session(
    session_id: str,
    request: SessionSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submit EMR session (ACID transaction).

    Performance: <500ms target
    """
    try:
        result = SessionService.submit_session(
            db,
            session_id=session_id,
            user_id=current_user.id,
            submit_data=request
        )

        return SessionSubmitResponse(
            session_id=result["session_id"],
            completed_at=result["completed_at"],
            soap_note_id=result["soap_note_id"],
            prescription_ids=result["prescription_ids"],
            pathology_order_ids=result["pathology_order_ids"],
            validation_queued=True,
            validation_status="pending"
        )

    except ValueError as e:
        error_msg = str(e)
        if "already submitted" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_msg
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg
        )
    except Exception as e:
        logger.error(f"Error submitting session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit session"
        )


# ============================================================================
# GET SESSION
# ============================================================================

@router.get("/{session_id}", response_model=SessionDetailResponse,
            summary="Get Session Details",
            description="""
Get detailed EMR session information.

**Use cases:**
- Resume draft session
- Review completed session
- View validation feedback

**Performance:** <300ms target
""",
            responses={
                200: {"description": "Session details returned"},
                401: {"description": "Unauthorized"},
                404: {"description": "Session not found"}
            })
async def get_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get session details.

    Performance: <300ms target
    """
    try:
        session_data = SessionService.get_session(
            db,
            session_id=session_id,
            user_id=current_user.id
        )

        if not session_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )

        # Build patient response
        patient = MockPatientResponse(
            id=str(session_data["patient_id"]),
            mrn="",  # TODO: Join with mock_patients
            full_name=session_data.get("name", ""),
            age=session_data.get("age", 0),
            gender=session_data.get("gender", ""),
            allergies=[],
            current_medications=[],
            vital_signs={},
            presenting_complaint=session_data.get("presenting_complaint", ""),
            clinical_scenario="",
            specialty=session_data.get("patient_specialty", ""),
            complexity_level=session_data.get("patient_difficulty", ""),
            demographics={}
        )

        # Build response
        response = SessionDetailResponse(
            session_id=str(session_data["id"]),
            user_id=session_data["user_id"],
            patient=patient,
            emr_system="epic",  # TODO: Add to session table
            is_active=session_data["submitted_at"] is None,
            started_at=session_data["started_at"],
            completed_at=session_data.get("submitted_at"),
            auto_saved_at=session_data.get("submitted_at"),
            session_data=session_data.get("score_breakdown", {})
        )

        # Add SOAP note if completed
        if session_data.get("soap_note"):
            soap = session_data["soap_note"]
            response.soap_note = SOAPNoteResponse(
                id=str(soap["id"]),
                subjective=soap["subjective"],
                objective=soap["objective"],
                assessment=soap["assessment"],
                plan=soap["plan"],
                note_type=soap.get("note_type", "Progress Note"),
                typing_wpm=soap.get("typing_wpm"),
                completion_time_seconds=soap.get("completion_time_seconds"),
                overall_validation_score=soap.get("overall_validation_score"),
                ahpra_compliant=soap.get("ahpra_compliant", False)
            )

        # Add prescriptions if completed
        if session_data.get("prescriptions"):
            response.prescriptions = [
                PrescriptionResponse(
                    id=str(rx["id"]),
                    medication_name=rx["medication_name"],
                    dose=rx["dose"],
                    frequency=rx["frequency"],
                    route=rx["route"],
                    quantity=rx["quantity"],
                    repeats=rx["repeats"],
                    indication=rx["indication"],
                    validation_score=rx.get("validation_score")
                )
                for rx in session_data["prescriptions"]
            ]

        # Add pathology orders if completed
        if session_data.get("pathology_orders"):
            response.pathology_orders = [
                PathologyOrderResponse(
                    id=str(order["id"]),
                    test_name=order["test_name"],
                    urgency=order["urgency"],
                    clinical_indication=order["clinical_indication"],
                    validation_score=order.get("validation_score")
                )
                for order in session_data["pathology_orders"]
            ]

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch session"
        )


# ============================================================================
# LIST SESSIONS
# ============================================================================

@router.get("", response_model=SessionListResponse,
            summary="List EMR Sessions",
            description="""
List user's EMR sessions with pagination and filtering.

**Use cases:**
- Session history page
- Resume draft sessions
- Track progress

**Performance:** <500ms target
""",
            responses={
                200: {"description": "Sessions list returned"},
                401: {"description": "Unauthorized"}
            })
async def list_sessions(
    is_active: Optional[bool] = Query(None, description="Filter by completion status"),
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    limit: int = Query(20, le=100, description="Page size"),
    offset: int = Query(0, ge=0, description="Page offset"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List sessions with pagination.

    Performance: <500ms target
    """
    try:
        result = SessionService.list_sessions(
            db,
            user_id=current_user.id,
            is_active=is_active,
            specialty=specialty,
            limit=limit,
            offset=offset
        )

        # Convert to response format
        sessions = [
            SessionSummary(
                session_id=str(s["id"]),
                patient_name=s.get("patient_name", "Unknown"),
                patient_specialty=s.get("specialty", "Unknown"),
                emr_system="epic",  # TODO: Add to table
                is_active=s["submitted_at"] is None,
                started_at=s["started_at"],
                completed_at=s.get("submitted_at"),
                validation_score=s.get("validation_score")
            )
            for s in result["sessions"]
        ]

        return SessionListResponse(
            sessions=sessions,
            total_count=result["total_count"],
            limit=result["limit"],
            offset=result["offset"]
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


# ============================================================================
# DELETE SESSION
# ============================================================================

@router.delete("/{session_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               summary="Delete Draft Session",
               description="""
Delete draft EMR session (only if not submitted).

**Use cases:**
- Cancel practice session
- Clean up abandoned drafts

**Note:** Cannot delete completed sessions (soft-delete instead)
""",
               responses={
                   204: {"description": "Session deleted successfully"},
                   401: {"description": "Unauthorized"},
                   404: {"description": "Session not found"},
                   409: {"description": "Cannot delete completed session"}
               })
async def delete_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete draft session only.
    """
    try:
        SessionService.delete_session(
            db,
            session_id=session_id,
            user_id=current_user.id
        )

        return Response(status_code=status.HTTP_204_NO_CONTENT)

    except ValueError as e:
        error_msg = str(e)
        if "already submitted" in error_msg or "cannot be deleted" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot delete completed session"
            )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    except Exception as e:
        logger.error(f"Error deleting session {session_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )
