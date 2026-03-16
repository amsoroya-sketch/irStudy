"""
OSCE Session endpoints for AI OSCE Simulation

Routes:
- POST /api/v1/osce-sessions - Create new OSCE session
- GET /api/v1/osce-sessions/{attempt_id} - Get session details
- GET /api/v1/osce-sessions/{attempt_id}/transcript - Get conversation history
- GET /api/v1/osce-sessions/{attempt_id}/score - Get AI Examiner score

SECURITY:
- JWT authentication required on all endpoints
- UUID validation for attempt_id and persona_id
- User authorization (can only view own sessions)
- No PHI leaks in error messages

AMC CLINICAL EXAM CONTEXT:
- 8-minute stations (480 seconds)
- 15-mark rubric (9/15 to pass)
- Real-time conversation tracking
- AI Examiner scoring after completion
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel

from src.db.base import get_db
from src.db.models import OSCEAttemptAI, OSCEScoreAI, PatientPersona, User
from src.auth.dependencies import get_current_active_user


router = APIRouter(prefix="/osce-sessions", tags=["ai-osce"])


class CreateOSCESessionRequest(BaseModel):
    """Request model for creating new OSCE session"""
    persona_id: str
    session_type: str = "individual"
    mock_exam_id: Optional[str] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_osce_session(
    request: CreateOSCESessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Create new AI OSCE practice session.

    Args:
    - persona_id: UUID of patient persona to practice with
    - session_type: 'individual' (default) or 'mock_exam'

    Returns:
    - attempt_id: UUID for this session
    - persona_code: Reference code (e.g., CARD-001-CHEST-PAIN)
    - opening_statement: What the AI Patient says first
    - time_limit_seconds: 480 (8 minutes)

    Next steps:
    - Frontend starts 8-minute timer
    - Student interacts with AI Patient via WebSocket (PRD_003)
    - Session auto-finalizes at 8:00

    Raises:
    - 404: Patient persona not found
    - 400: Invalid session type

    Example request:
    POST /api/v1/osce-sessions
    {
        "persona_id": "123e4567-e89b-12d3-a456-426614174000",
        "session_type": "individual"
    }

    Example response:
    {
        "attempt_id": "987fcdeb-51a2-43d7-8a9b-123456789abc",
        "persona_code": "CARD-001-CHEST-PAIN",
        "patient_name": "John Smith",
        "opening_statement": "Doctor, I've been having this terrible chest pain...",
        "time_limit_seconds": 480,
        "started_at": "2026-02-23T10:30:00+00:00"
    }
    """
    # Validate session type
    if request.session_type not in ["individual", "mock_exam"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session type. Must be 'individual' or 'mock_exam'"
        )

    # Verify persona exists
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == request.persona_id,
        PatientPersona.is_active == True
    ).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient persona not found"
        )

    # Create attempt record
    new_attempt = OSCEAttemptAI(
        attempt_id=str(uuid4()),
        user_id=str(current_user.id),
        persona_id=request.persona_id,
        session_type=request.session_type,
        started_at=datetime.now(timezone.utc),
        conversation_history=[],
        emotional_state_transitions=[],
        student_actions=[],
        was_completed=False,
        session_state='initialized',
    )

    db.add(new_attempt)
    db.commit()
    db.refresh(new_attempt)

    return {
        "attempt_id": new_attempt.attempt_id,
        "persona_code": persona.persona_code,
        "patient_name": persona.name,
        "opening_statement": persona.opening_statement,
        "time_limit_seconds": 480,
        "started_at": new_attempt.started_at.isoformat(),
    }


@router.get("/{attempt_id}")
async def get_osce_session(
    attempt_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get OSCE session details.

    Returns:
    - Session metadata (started_at, ended_at, duration)
    - Completion status
    - Persona details

    Args:
    - attempt_id: UUID of OSCE session

    Returns:
    - Session metadata and completion status

    Raises:
    - 404: OSCE session not found or unauthorized

    Example response:
    {
        "attempt_id": "987fcdeb-51a2-43d7-8a9b-123456789abc",
        "session_type": "individual",
        "started_at": "2026-02-23T10:30:00+00:00",
        "ended_at": "2026-02-23T10:38:00+00:00",
        "duration_seconds": 480,
        "was_completed": true,
        "persona": {
            "persona_code": "CARD-001-CHEST-PAIN",
            "name": "John Smith",
            "specialty": "cardiology"
        }
    }
    """
    attempt = db.query(OSCEAttemptAI).filter(
        OSCEAttemptAI.attempt_id == str(attempt_id),
        OSCEAttemptAI.user_id == str(current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE session not found"
        )

    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == attempt.persona_id
    ).first()

    return {
        "attempt_id": attempt.attempt_id,
        "session_type": attempt.session_type,
        "started_at": attempt.started_at.isoformat(),
        "ended_at": attempt.ended_at.isoformat() if attempt.ended_at else None,
        "duration_seconds": attempt.duration_seconds,
        "was_completed": attempt.was_completed,
        "persona": {
            "persona_code": persona.persona_code if persona else None,
            "name": persona.name if persona else None,
            "specialty": persona.specialty if persona else None,
        }
    }


@router.get("/{attempt_id}/transcript")
async def get_osce_transcript(
    attempt_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get full conversation transcript.

    Returns:
    - conversation_history: JSONB array of messages
    - emotional_state_transitions: How patient's emotional state evolved
    - student_actions: Non-verbal actions (e.g., "examined abdomen")

    Format:
    conversation_history: [
        {"role": "patient", "message": "I've had this terrible chest pain...", "timestamp": "..."},
        {"role": "student", "message": "Can you describe the pain?", "timestamp": "..."},
        ...
    ]

    Args:
    - attempt_id: UUID of OSCE session

    Returns:
    - Full conversation transcript and student actions

    Raises:
    - 404: OSCE session not found or unauthorized

    Example response:
    {
        "attempt_id": "987fcdeb-51a2-43d7-8a9b-123456789abc",
        "conversation_history": [
            {
                "role": "patient",
                "message": "I've had this terrible chest pain for 2 hours",
                "timestamp": "2026-02-23T10:30:15+00:00"
            },
            {
                "role": "student",
                "message": "Can you describe the pain?",
                "timestamp": "2026-02-23T10:30:45+00:00"
            }
        ],
        "emotional_state_transitions": [
            {"state": "anxious", "timestamp": "2026-02-23T10:30:00+00:00"},
            {"state": "calm", "timestamp": "2026-02-23T10:32:00+00:00"}
        ],
        "student_actions": [
            {"action": "examined chest", "timestamp": "2026-02-23T10:35:00+00:00"}
        ]
    }
    """
    attempt = db.query(OSCEAttemptAI).filter(
        OSCEAttemptAI.attempt_id == str(attempt_id),
        OSCEAttemptAI.user_id == str(current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE session not found"
        )

    return {
        "attempt_id": attempt.attempt_id,
        "conversation_history": attempt.conversation_history or [],
        "emotional_state_transitions": attempt.emotional_state_transitions or [],
        "student_actions": attempt.student_actions or [],
    }


@router.get("/{attempt_id}/score")
async def get_osce_score(
    attempt_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get AI Examiner score for completed OSCE.

    Returns:
    - AMC 15-mark rubric breakdown:
      - Communication (0-3)
      - Clinical Reasoning (0-4)
      - Information Gathering (0-4)
      - Management (0-2)
      - Professionalism (0-2)
    - total_score (calculated, max 15)
    - pass_fail ('PASS' if ≥9, else 'FAIL')
    - ai_examiner_feedback: Detailed written feedback
    - strengths: Array of strengths
    - areas_for_improvement: Array of weaknesses

    Raises:
    - 404: Session not found or score not available yet

    Args:
    - attempt_id: UUID of OSCE session

    Returns:
    - AI Examiner score with detailed rubric breakdown

    Example response:
    {
        "attempt_id": "987fcdeb-51a2-43d7-8a9b-123456789abc",
        "scores": {
            "communication": 2,
            "clinical_reasoning": 3,
            "information_gathering": 3,
            "management": 1,
            "professionalism": 2
        },
        "total_score": 11,
        "pass_fail": "PASS",
        "ai_examiner_feedback": "Good systematic approach to history taking...",
        "strengths": ["Clear communication", "Systematic history"],
        "areas_for_improvement": ["Safety netting", "Red flag identification"],
        "critical_errors": [],
        "scored_at": "2026-02-23T10:40:00+00:00",
        "scoring_model_version": "claude-3.5-sonnet-20250219"
    }
    """
    attempt = db.query(OSCEAttemptAI).filter(
        OSCEAttemptAI.attempt_id == str(attempt_id),
        OSCEAttemptAI.user_id == str(current_user.id)
    ).first()

    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE session not found"
        )

    score = db.query(OSCEScoreAI).filter(
        OSCEScoreAI.attempt_id == str(attempt_id)
    ).first()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Score not available yet. AI Examiner analysis pending."
        )

    # Calculate total (or use database GENERATED column if available)
    total_score = (
        (score.communication_score or 0) +
        (score.clinical_reasoning_score or 0) +
        (score.information_gathering_score or 0) +
        (score.management_score or 0) +
        (score.professionalism_score or 0)
    )

    return {
        "attempt_id": score.attempt_id,
        "scores": {
            "communication": score.communication_score,
            "clinical_reasoning": score.clinical_reasoning_score,
            "information_gathering": score.information_gathering_score,
            "management": score.management_score,
            "professionalism": score.professionalism_score,
        },
        "total_score": total_score,
        "pass_fail": "PASS" if total_score >= 9 else "FAIL",
        "ai_examiner_feedback": score.ai_examiner_feedback,
        "strengths": score.strengths or [],
        "areas_for_improvement": score.areas_for_improvement or [],
        "critical_errors": score.critical_errors or [],
        "scored_at": score.scored_at.isoformat(),
        "scoring_model_version": score.scoring_model_version,
    }
