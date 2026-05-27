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
from typing import Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.v1.auth import get_current_user
from src.db.base import get_db
from src.db.models import EMRSession, User
from src.schemas.integration import (
    ConversionRequest,
    ConversionResponse,
    ConversionError
)
from src.services.integration.osce_to_emr_converter import OSCEToEMRConverter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/integration", tags=["integration"])


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
      "redirectUrl": "/emr/session/660e8400-e29b-41d4-a716-446655440001",
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

        # Step 2: Create EMR session with pre-filled SOAP note
        emr_session = EMRSession(
            user_id=current_user.id,
            emr_system="epic",  # Default EMR system
            patient_data={},  # Will be populated from OSCE persona
            session_data={
                "soap_note": {
                    "subjective": conversion_result.soap_note_draft.subjective,
                    "objective": conversion_result.soap_note_draft.objective,
                    "assessment": conversion_result.soap_note_draft.assessment,
                    "plan": conversion_result.soap_note_draft.plan
                },
                "auto_filled": True,
                "conversion_source": "osce_transcript"
            },
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
        db.commit()
        db.refresh(emr_session)

        logger.info(
            f"EMR session created: {emr_session.id} "
            f"(pre-fill: {conversion_result.metadata.pre_fill_percentage:.1%})"
        )

        # Step 3: Build response
        response = ConversionResponse(
            emr_session_id=emr_session.id,
            pre_fill_percentage=conversion_result.metadata.pre_fill_percentage,
            extraction_confidence=conversion_result.metadata.extraction_confidence,
            redirect_url=f"/emr/session/{emr_session.id}",
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
