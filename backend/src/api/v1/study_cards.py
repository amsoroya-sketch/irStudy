"""
Study Card endpoints with SM-2 spaced repetition

Routes:
- GET /api/v1/study-cards/due-cards - Get cards due for review today
- POST /api/v1/study-cards/review - Submit review and update SM-2 schedule
- GET /api/v1/study-cards/statistics - Get study card statistics
- POST /api/v1/study-cards/generate-from-osce - Generate cards from OSCE session (PRD-P1-005)

AUSTRALIAN MEDICAL CONTEXT:
- All study cards validated for Australian medical terminology
- Citations reference Australian guidelines (eTG, AMH, AHPRA, NSW Health)
- Content aligned with AMC Clinical Exam preparation

SM-2 ALGORITHM:
- Quality ratings: 0 (complete blackout) to 5 (perfect response)
- Ease factor range: 1.3 - 2.5
- Interval calculation: I(n) = I(n-1) × EF
- Failed reviews (quality < 3) reset to day 1
"""

from typing import List, Optional
from datetime import datetime, date
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User, StudyCard, StudyCardReview, MedicalSpecialty, DifficultyLevel
from src.schemas.study_card import (
    StudyCardResponse,
    StudyCardPublic,
    StudyCardWithAnswer,
    StudyCardReview as StudyCardReviewSchema,
    StudyCardReviewResponse,
    StudyCardsDueResponse,
    StudyCardStatistics,
    GenerateCardsRequest,
    GenerateCardsResponse,
    GeneratedStudyCardResponse,
)
from src.auth.dependencies import get_current_active_user
from src.services.sm2_algorithm import SM2Algorithm
from src.ai.study_card_generator import StudyCardGenerator
from src.ai.rag_service import RAGService


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/study-cards", tags=["study-cards"])


# ============================================================================
# GET DUE CARDS
# ============================================================================


@router.get("/due-cards", response_model=StudyCardsDueResponse)
async def get_due_cards(
    limit: int = Query(20, ge=1, le=100, description="Maximum cards to return"),
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by specialty"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get study cards due for review today.

    Query parameters:
    - limit: Maximum cards to return (1-100, default 20)
    - specialty: Filter by medical specialty
    - difficulty: Filter by difficulty level

    Returns:
    - List of study cards due for review
    - Total count of due cards
    - Ordered by next_review_date (oldest first)

    SM-2 Context:
    - Cards with next_review_date <= today
    - Prioritizes overdue cards (oldest first)
    - Includes cards never reviewed (repetitions = 0)

    Raises:
    - 401: User not authenticated
    """
    # Build query for cards due today
    today = datetime.utcnow()

    query = db.query(StudyCard).filter(
        StudyCard.is_active == True,
        StudyCard.next_review_date <= today,
        StudyCard.deleted_at.is_(None)
    )

    # Apply filters if provided
    if specialty:
        query = query.filter(StudyCard.specialty == specialty)

    if difficulty:
        query = query.filter(StudyCard.difficulty == difficulty)

    # Get total count before limiting
    total_due = query.count()

    # Get cards ordered by next_review_date (oldest first)
    cards = query.order_by(StudyCard.next_review_date.asc()).limit(limit).all()

    # Convert to response models
    card_responses = [
        StudyCardResponse(
            id=card.id,
            user_id=card.user_id,
            card_id=card.card_id,
            specialty=card.specialty,
            topic=card.topic,
            subtopic=card.subtopic,
            question=card.question,
            answer=card.answer,
            explanation=card.explanation,
            citations=card.citations,
            difficulty=card.difficulty,
            tags=card.tags or [],
            card_type=card.card_type,
            next_review_date=card.next_review_date,
            interval_days=card.interval_days,
            ease_factor=card.ease_factor,
            repetitions=card.repetitions,
            is_active=card.is_active,
            created_at=card.created_at,
            updated_at=card.updated_at,
        )
        for card in cards
    ]

    return StudyCardsDueResponse(
        total_due=total_due,
        cards=card_responses
    )


# ============================================================================
# SUBMIT REVIEW
# ============================================================================


@router.post("/review", response_model=StudyCardReviewResponse, status_code=status.HTTP_200_OK)
async def submit_review(
    review: StudyCardReviewSchema,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit study card review and update SM-2 schedule.

    Request body:
    - card_id: Study card ID to review
    - quality: Quality rating 0-5 (SM-2 algorithm)
      - 0: Complete blackout
      - 1: Incorrect, but familiar
      - 2: Incorrect, but almost correct
      - 3: Correct, but difficult
      - 4: Correct, after hesitation
      - 5: Perfect response
    - time_taken_seconds: Time taken to review (analytics)

    Returns:
    - Updated SM-2 parameters (next_review_date, interval, ease_factor, repetitions)
    - Quality description
    - Encouraging message

    SM-2 Algorithm:
    - Quality < 3: Reset to day 1, reset repetitions to 0
    - Quality >= 3: Advance to next interval
    - Ease factor updated based on quality
    - Ease factor clamped to 1.3-2.5 range

    Raises:
    - 404: Study card not found
    - 401: User not authenticated
    - 400: Invalid quality rating (must be 0-5)
    """
    # Get study card
    card = db.query(StudyCard).filter(
        StudyCard.id == review.card_id,
        StudyCard.is_active == True,
        StudyCard.deleted_at.is_(None)
    ).first()

    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study card {review.card_id} not found or inactive"
        )

    # Validate quality rating
    if not SM2Algorithm.validate_quality(review.quality):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quality must be 0-5, got {review.quality}"
        )

    # Calculate next review using SM-2 algorithm
    next_review_date, interval_days, ease_factor, repetitions = SM2Algorithm.calculate_next_review(
        quality=review.quality,
        current_ease_factor=card.ease_factor,
        current_interval=card.interval_days,
        repetitions=card.repetitions
    )

    # Update study card with new SM-2 parameters
    card.next_review_date = next_review_date
    card.interval_days = interval_days
    card.ease_factor = ease_factor
    card.repetitions = repetitions
    card.updated_at = datetime.utcnow()

    # Record review in history table
    review_record = StudyCardReview(
        user_id=current_user.id,
        card_id=card.id,
        quality=review.quality,
        time_taken_seconds=review.time_taken_seconds,
        ease_factor_after=ease_factor,
        interval_days_after=interval_days,
        repetitions_after=repetitions,
        next_review_date_after=next_review_date,
    )
    db.add(review_record)

    # Commit changes
    db.commit()
    db.refresh(card)

    # Generate response message
    quality_desc = SM2Algorithm.get_quality_description(review.quality)

    if review.quality < 3:
        message = f"Keep practicing! Card will be reviewed again tomorrow. {quality_desc}."
    elif review.quality == 3:
        message = f"Good work! Next review in {interval_days} day(s). {quality_desc}."
    elif review.quality == 4:
        message = f"Great job! Next review in {interval_days} day(s). {quality_desc}."
    else:  # quality == 5
        message = f"Perfect! Next review in {interval_days} day(s). {quality_desc}."

    return StudyCardReviewResponse(
        card_id=card.id,
        quality=review.quality,
        next_review_date=next_review_date,
        interval_days=interval_days,
        ease_factor=ease_factor,
        repetitions=repetitions,
        message=message,
        quality_description=quality_desc,
    )


# ============================================================================
# GENERATE FROM OSCE SESSION (PRD-P1-005 Phase 4)
# ============================================================================


@router.post(
    "/generate-from-osce",
    response_model=GenerateCardsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Generate study cards from OSCE session",
    description=(
        "Automatically generate 3-5 study cards from OSCE feedback using Claude AI "
        "with RAG-enhanced citations. Returns existing cards if already generated (idempotent). "
        "\n\n**AUTHENTICATION**: JWT required. "
        "\n**AUTHORIZATION**: User must own the OSCE session. "
        "\n**IDEMPOTENCY**: Returns 409 Conflict if cards already exist for session."
    ),
)
async def generate_cards_from_osce(
    request: GenerateCardsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> GenerateCardsResponse:
    """
    Generate study cards from OSCE session feedback (PRD-P1-005).

    **Request Body**:
    ```json
    {
        "session_id": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```

    **Response** (201 Created):
    ```json
    {
        "cards": [
            {
                "id": 123,
                "question": "What is SOCRATES framework?",
                "answer": "Pain assessment framework...",
                "citations": [...],
                "ease_factor": 2.5,
                "interval_days": 1,
                "repetitions": 0,
                "next_review_date": "2026-03-24T12:00:00Z"
            }
        ],
        "count": 3,
        "session_id": "550e8400-...",
        "message": "Study cards generated successfully"
    }
    ```

    **Errors**:
    - 401: Unauthorized (no JWT)
    - 403: Forbidden (user doesn't own session)
    - 404: Session not found
    - 409: Cards already exist for session
    - 422: Invalid UUID format
    - 500: Internal server error

    **Performance**:
    - Target: <8 seconds for 3 cards
    - Uses async Claude API calls
    - RAG citations with confidence ≥0.65

    **Security**:
    - API key from Vault (no hardcoded credentials)
    - User authorization validated
    - Input validation (UUID format)
    """
    try:
        # Step 1: Idempotency check - return existing cards if found
        existing_cards = (
            db.query(StudyCard)
            .filter(
                StudyCard.session_id == request.session_id,
                StudyCard.is_active == True,
                StudyCard.deleted_at.is_(None)
            )
            .all()
        )

        if existing_cards:
            # Cards already exist - return 409 Conflict
            logger.info(
                f"Study cards already exist for session {request.session_id} "
                f"(found {len(existing_cards)} cards)"
            )
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "message": f"Study cards already exist for session {request.session_id}",
                    "existing_count": len(existing_cards),
                    "session_id": request.session_id,
                },
            )

        # Step 2: Initialize dependencies
        logger.info(f"Generating study cards for session {request.session_id}, user {current_user.id}")

        rag_service = RAGService()
        generator = StudyCardGenerator(rag_service=rag_service)

        # Step 3: Generate cards (full pipeline)
        # This calls generate_cards_from_session which:
        # - Validates session ownership (raises ValueError if unauthorized)
        # - Extracts learning points from feedback
        # - Generates Q&A pairs with Claude API
        # - Enriches with RAG citations
        # - Creates StudyCard objects with SM-2 initialization
        # - Batch inserts to database
        cards = await generator.generate_cards_from_session(
            session_id=request.session_id,
            user_id=current_user.id,
            db=db,
        )

        # Step 4: Convert to response schema
        card_responses = [
            GeneratedStudyCardResponse(
                id=card.id,
                user_id=card.user_id,
                session_id=card.session_id,
                card_id=card.card_id,
                specialty=card.specialty,
                topic=card.topic,
                subtopic=card.subtopic,
                question=card.question,
                answer=card.answer,
                explanation=card.explanation,
                citations=card.citations,
                difficulty=card.difficulty,
                tags=card.tags or [],
                card_type=card.card_type,
                ease_factor=card.ease_factor,
                interval_days=card.interval_days,
                repetitions=card.repetitions,
                next_review_date=card.next_review_date,
                created_at=card.created_at,
                updated_at=card.updated_at,
            )
            for card in cards
        ]

        logger.info(f"Successfully generated {len(card_responses)} study cards for session {request.session_id}")

        return GenerateCardsResponse(
            cards=card_responses,
            count=len(card_responses),
            session_id=request.session_id,
            message=f"Generated {len(card_responses)} study cards successfully",
        )

    except HTTPException:
        # Re-raise HTTPExceptions (401, 403, 404, 409)
        raise

    except ValueError as e:
        # ValueError from study_card_generator (session not found, permission denied)
        error_msg = str(e).lower()
        logger.error(f"Validation error generating cards for session {request.session_id}: {e}")

        if "not found" in error_msg or "does not exist" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        elif "permission" in error_msg or "ownership" in error_msg or "does not own" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e),
            )

    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(
            f"Unexpected error generating cards for session {request.session_id}: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while generating study cards",
        )


# ============================================================================
# GET STATISTICS
# ============================================================================


@router.get("/statistics", response_model=StudyCardStatistics)
async def get_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get study card statistics for current user.

    Returns:
    - total_cards: Total active study cards
    - by_specialty: Breakdown by medical specialty
    - by_difficulty: Breakdown by difficulty level
    - cards_due_today: Cards due for review today
    - cards_mastered: Cards with repetitions >= 3
    - average_ease_factor: Average ease factor across all cards
    - total_reviews: Total review attempts
    - reviews_today: Reviews submitted today
    - average_quality: Average quality rating
    - retention_rate: Percentage of reviews with quality >= 3

    AUSTRALIAN CONTEXT:
    - Statistics help identify weak specialties for AMC Clinical Exam prep
    - Retention rate indicates readiness for examination
    - Cards mastered (repetitions >= 3) indicate strong knowledge

    Raises:
    - 401: User not authenticated
    """
    # Get all active cards
    total_cards = db.query(StudyCard).filter(
        StudyCard.is_active == True,
        StudyCard.deleted_at.is_(None)
    ).count()

    # Cards by specialty
    specialty_counts = db.query(
        StudyCard.specialty,
        func.count(StudyCard.id)
    ).filter(
        StudyCard.is_active == True,
        StudyCard.deleted_at.is_(None)
    ).group_by(StudyCard.specialty).all()

    by_specialty = {str(specialty): count for specialty, count in specialty_counts}

    # Cards by difficulty
    difficulty_counts = db.query(
        StudyCard.difficulty,
        func.count(StudyCard.id)
    ).filter(
        StudyCard.is_active == True,
        StudyCard.deleted_at.is_(None)
    ).group_by(StudyCard.difficulty).all()

    by_difficulty = {str(difficulty): count for difficulty, count in difficulty_counts}

    # Cards due today
    today = datetime.utcnow()
    cards_due_today = db.query(StudyCard).filter(
        StudyCard.is_active == True,
        StudyCard.next_review_date <= today,
        StudyCard.deleted_at.is_(None)
    ).count()

    # Cards mastered (repetitions >= 3)
    cards_mastered = db.query(StudyCard).filter(
        StudyCard.is_active == True,
        StudyCard.repetitions >= 3,
        StudyCard.deleted_at.is_(None)
    ).count()

    # Average ease factor
    avg_ease_factor_result = db.query(
        func.avg(StudyCard.ease_factor)
    ).filter(
        StudyCard.is_active == True,
        StudyCard.deleted_at.is_(None)
    ).scalar()

    average_ease_factor = float(avg_ease_factor_result) if avg_ease_factor_result else 2.5

    # Total reviews for current user
    total_reviews = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id
    ).count()

    # Reviews today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    reviews_today = db.query(StudyCardReview).filter(
        StudyCardReview.user_id == current_user.id,
        StudyCardReview.reviewed_at >= today_start
    ).count()

    # Average quality
    avg_quality_result = db.query(
        func.avg(StudyCardReview.quality)
    ).filter(
        StudyCardReview.user_id == current_user.id
    ).scalar()

    average_quality = float(avg_quality_result) if avg_quality_result else 0.0

    # Retention rate (percentage of quality >= 3)
    if total_reviews > 0:
        successful_reviews = db.query(StudyCardReview).filter(
            StudyCardReview.user_id == current_user.id,
            StudyCardReview.quality >= 3
        ).count()
        retention_rate = (successful_reviews / total_reviews) * 100
    else:
        retention_rate = 0.0

    return StudyCardStatistics(
        total_cards=total_cards,
        by_specialty=by_specialty,
        by_difficulty=by_difficulty,
        cards_due_today=cards_due_today,
        cards_mastered=cards_mastered,
        average_ease_factor=average_ease_factor,
        total_reviews=total_reviews,
        reviews_today=reviews_today,
        average_quality=average_quality,
        retention_rate=retention_rate,
    )
