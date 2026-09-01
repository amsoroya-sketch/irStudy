"""
OSCE-to-EMR Conversion API Endpoint

POST /api/v1/integration/osce-to-emr
- Converts completed OSCE attempt to pre-filled EMR session
- Requires user authentication
- Returns EMR session ID and redirect URL

PERFORMANCE TARGET: <500ms (p95)
SECURITY: User can only convert their own OSCEs
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.db.base import get_db
from src.db.models import (
    EMRSession,
    EMRSOAPNote,
    MockPatient,
    OSCEAttemptAI,
    User,
)
from src.schemas.integration import (
    ConversionRequest,
    ConversionResponse,
    ConversionError
)
from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integration", tags=["integration"])

# AI-OSCE persona difficulty (foundation/intermediate/advanced) → EMR practice
# difficulty (easy/medium/hard, as validated by the EMR sessions endpoints).
_PERSONA_DIFFICULTY_MAP = {
    "foundation": "easy",
    "intermediate": "medium",
    "advanced": "hard",
    "easy": "easy",
    "medium": "medium",
    "hard": "hard",
}


def _map_persona_difficulty(value: Optional[str]) -> str:
    """Map an OSCE persona difficulty to an EMR practice difficulty.

    Defaults to ``"medium"`` when the persona difficulty is missing/unknown.
    """
    if not value:
        return "medium"
    return _PERSONA_DIFFICULTY_MAP.get(str(value).lower(), "medium")


@router.post(
    "/osce-to-emr",
    response_model=ConversionResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "OSCE successfully converted to EMR session"},
        400: {"model": ConversionError, "description": "Invalid OSCE type (cannot convert communication OSCEs)"},
        403: {"model": ConversionError, "description": "User not authorized to convert this OSCE"},
        404: {"model": ConversionError, "description": "OSCE attempt not found"},
        500: {"model": ConversionError, "description": "Conversion failed"},
    }
)
async def convert_osce_to_emr(
    request: ConversionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ConversionResponse:
    """
    Convert OSCE attempt to pre-filled EMR session

    **Workflow:**
    1. Validate user owns OSCE attempt
    2. Extract clinical data from OSCE transcript using Claude API
    3. Map extracted data to SOAP note template
    4. Create EMR session with pre-filled SOAP note
    5. Return EMR session ID and redirect URL

    **Requirements:**
    - OSCE must be completed (exam_state = 'COMPLETED')
    - OSCE type must be clinical history-taking (not communication/counselling)
    - User must own the OSCE attempt

    **Request:**
    ```json
    {
      "osceAttemptId": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```

    **Response:**
    ```json
    {
      "emrSessionId": "660e8400-e29b-41d4-a716-446655440001",
      "preFillPercentage": 0.78,
      "extractionConfidence": 0.85,
      "redirectUrl": "/emr/select/660e8400-e29b-41d4-a716-446655440001",
      "message": "OSCE successfully converted to EMR session"
    }
    ```

    **Error Codes:**
    - `OSCE_NOT_FOUND`: OSCE attempt does not exist
    - `UNAUTHORIZED`: User does not own OSCE attempt
    - `INVALID_OSCE_TYPE`: OSCE type cannot be converted (e.g., communication station)
    - `CONVERSION_FAILED`: Claude API error or technical failure
    """
    try:
        logger.info(
            f"OSCE-to-EMR conversion requested: "
            f"OSCE={request.osce_attempt_id}, User={current_user.id}"
        )

        # Initialize converter with database session
        converter = OSCEToEMRConverter(db_session=db)

        # Step 1: Convert OSCE to SOAP note (validates ownership internally)
        conversion_result = await converter.convert(
            osce_attempt_id=request.osce_attempt_id,
            user_id=current_user.id
        )

        # Step 2: Materialise a MockPatient from the OSCE persona.
        # emr_sessions.patient_id → mock_patients.id is NOT NULL (migration 008),
        # and mock_patients has its own NOT-NULL columns, so we must persist a
        # real patient row rather than stuffing data into un-migrated JSON blobs.
        osce_attempt = (
            db.query(OSCEAttemptAI)
            .filter(OSCEAttemptAI.attempt_id == str(request.osce_attempt_id))
            .first()
        )
        persona = osce_attempt.persona if osce_attempt else None

        if persona is not None:
            patient_name = persona.name
            patient_age = persona.age
            patient_gender = persona.gender
            specialty = persona.specialty
            presenting_complaint = persona.chief_complaint
            difficulty = _map_persona_difficulty(
                getattr(persona, "difficulty_level", None)
            )
            demographics = {
                "occupation": persona.occupation,
                "cultural_background": persona.cultural_background,
                "preferred_language": persona.preferred_language,
                "persona_code": persona.persona_code,
                "source": "osce_persona",
                "source_osce_attempt_id": str(request.osce_attempt_id),
            }
        else:
            # Persona demographics unavailable — use clearly-labelled placeholders
            # and safe defaults that satisfy migration-008 NOT NULL/CHECK rules.
            patient_name = "OSCE Patient (persona unavailable)"
            patient_age = 40  # within mock_patients CHECK (18..100)
            patient_gender = "unknown"
            specialty = "general_practice"
            presenting_complaint = (
                "Converted from OSCE attempt (patient details unavailable)"
            )
            difficulty = "medium"
            demographics = {
                "source": "osce_conversion",
                "source_osce_attempt_id": str(request.osce_attempt_id),
            }

        mock_patient = MockPatient(
            # mrn is varchar(20) & UNIQUE — a random 15-char suffix keeps it short
            # and collision-free even if the same OSCE is converted twice.
            mrn=f"OSCE-{uuid4().hex[:15]}",
            name=patient_name,
            age=patient_age,
            gender=patient_gender,
            demographics=demographics,
            presenting_complaint=presenting_complaint,
            specialty=specialty,
            difficulty=difficulty,
        )
        db.add(mock_patient)
        db.flush()  # assign mock_patient.id

        # Step 3: Create EMR session referencing the mock patient
        emr_session = EMRSession(
            user_id=current_user.id,
            patient_id=mock_patient.id,
            emr_system="epic",  # Default EMR system
            specialty=specialty,
            difficulty=difficulty,
            status="in_progress",
            source_osce_attempt_id=str(request.osce_attempt_id),
            conversion_metadata={
                "pre_fill_percentage": conversion_result.metadata.pre_fill_percentage,
                "extraction_confidence": conversion_result.metadata.extraction_confidence,
                "tokens_used": conversion_result.metadata.tokens_used,
                "api_response_time_ms": conversion_result.metadata.api_response_time_ms,
                "conversion_timestamp": conversion_result.metadata.conversion_timestamp.isoformat(),
                "missing_elements": conversion_result.metadata.missing_elements,
                "australian_terminology_compliance": conversion_result.metadata.australian_terminology_compliance
            }
        )
        db.add(emr_session)
        db.flush()  # assign emr_session.id

        # Step 4: Persist the pre-filled SOAP note as an editable DRAFT so the
        # Epic/Cerner editor loads it via the normal GET session → soap_note path
        # (mirrors the auto-save draft creation in api/v1/emr/sessions.py).
        draft = conversion_result.soap_note_draft
        soap_note = EMRSOAPNote(
            session_id=emr_session.id,
            subjective=draft.subjective,
            objective=draft.objective,
            assessment=draft.assessment,
            plan=draft.plan,
            is_final_submission=False,
        )
        db.add(soap_note)

        db.commit()
        db.refresh(emr_session)

        logger.info(
            f"EMR session created: {emr_session.id} "
            f"(patient={mock_patient.id}, "
            f"pre-fill: {conversion_result.metadata.pre_fill_percentage:.1%})"
        )

        # Step 5: Build response
        response = ConversionResponse(
            emr_session_id=emr_session.id,
            pre_fill_percentage=conversion_result.metadata.pre_fill_percentage,
            extraction_confidence=conversion_result.metadata.extraction_confidence,
            redirect_url=f"/emr/select/{emr_session.id}",
            message=(
                f"OSCE successfully converted to EMR session "
                f"({conversion_result.metadata.pre_fill_percentage:.0%} pre-filled)"
            )
        )

        return response

    except ValueError as e:
        # User authorization or validation errors
        error_msg = str(e)

        if "not found" in error_msg.lower():
            logger.warning(f"OSCE not found: {request.osce_attempt_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error_code": "OSCE_NOT_FOUND",
                    "error_message": error_msg,
                    "osce_attempt_id": str(request.osce_attempt_id),
                    "fallback_action": "Verify OSCE attempt ID is correct"
                }
            )

        elif "not authorized" in error_msg.lower() or "ownership" in error_msg.lower():
            logger.warning(f"Unauthorized OSCE conversion attempt: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error_code": "UNAUTHORIZED",
                    "error_message": error_msg,
                    "osce_attempt_id": str(request.osce_attempt_id),
                    "fallback_action": "You can only convert your own OSCE attempts"
                }
            )

        elif "cannot be converted" in error_msg.lower():
            logger.warning(f"Invalid OSCE type for conversion: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "INVALID_OSCE_TYPE",
                    "error_message": error_msg,
                    "osce_attempt_id": str(request.osce_attempt_id),
                    "fallback_action": "Only clinical history-taking OSCEs can be converted to SOAP notes. Consider creating a reflection log instead."
                }
            )

        else:
            # Generic validation error
            logger.error(f"OSCE conversion validation failed: {error_msg}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error_code": "VALIDATION_ERROR",
                    "error_message": error_msg,
                    "osce_attempt_id": str(request.osce_attempt_id)
                }
            )

    except Exception as e:
        # Unexpected errors (Claude API, database, etc.)
        logger.error(f"OSCE-to-EMR conversion failed: {e}", exc_info=True)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error_code": "CONVERSION_FAILED",
                "error_message": f"Conversion failed: {str(e)}",
                "osce_attempt_id": str(request.osce_attempt_id),
                "fallback_action": "Please try again. If the problem persists, contact support."
            }
        )


@router.get(
    "/conversion-stats",
    response_model=Dict[str, Any],
    tags=["integration"]
)
async def get_conversion_statistics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get OSCE-to-EMR conversion statistics for current user

    **Returns:**
    - Total conversions
    - Average pre-fill percentage
    - Average extraction confidence
    - Total tokens used
    - Pedagogical metrics (learning transfer)

    **Response:**
    ```json
    {
      "total_conversions": 12,
      "average_pre_fill_percentage": 0.78,
      "average_extraction_confidence": 0.84,
      "total_tokens_used": 18450,
      "conversion_success_rate": 0.92,
      "most_common_missing_elements": ["Vital signs", "Allergies"]
    }
    ```
    """
    from sqlalchemy import func

    # Query all EMR sessions with OSCE source for current user
    conversions = db.query(EMRSession).filter(
        EMRSession.user_id == current_user.user_id,
        EMRSession.source_osce_attempt_id.isnot(None)
    ).all()

    if not conversions:
        return {
            "total_conversions": 0,
            "message": "No OSCE-to-EMR conversions yet. Try converting your completed OSCEs!"
        }

    # Calculate statistics
    total = len(conversions)

    pre_fill_pcts = [
        c.conversion_metadata.get('pre_fill_percentage', 0.0)
        for c in conversions
        if c.conversion_metadata
    ]

    confidence_scores = [
        c.conversion_metadata.get('extraction_confidence', 0.0)
        for c in conversions
        if c.conversion_metadata
    ]

    tokens = [
        c.conversion_metadata.get('tokens_used', 0)
        for c in conversions
        if c.conversion_metadata
    ]

    # Aggregate missing elements
    missing_elements = []
    for c in conversions:
        if c.conversion_metadata:
            missing_elements.extend(
                c.conversion_metadata.get('missing_elements', [])
            )

    # Count most common missing elements
    from collections import Counter
    missing_counter = Counter(missing_elements)
    most_common_missing = [
        {"element": elem, "count": count}
        for elem, count in missing_counter.most_common(5)
    ]

    stats = {
        "total_conversions": total,
        "average_pre_fill_percentage": sum(pre_fill_pcts) / len(pre_fill_pcts) if pre_fill_pcts else 0.0,
        "average_extraction_confidence": sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0,
        "total_tokens_used": sum(tokens),
        "conversion_success_rate": len([p for p in pre_fill_pcts if p >= 0.70]) / total if total > 0 else 0.0,
        "most_common_missing_elements": most_common_missing
    }

    logger.info(f"Conversion stats retrieved for user {current_user.user_id}: {stats}")

    return stats
