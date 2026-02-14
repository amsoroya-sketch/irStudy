"""
Optimized Study Card endpoints for high-performance spaced repetition

Routes (Performance-Optimized):
- GET /api/v1/study-cards/queue/daily - Daily review queue (<100ms target)
- GET /api/v1/study-cards/queue/overdue-count - Fast count query (<50ms target)
- GET /api/v1/study-cards/schedule/prediction - Schedule prediction (<200ms target)
- POST /api/v1/study-cards/queue/batch-review - Batch SM-2 updates (<500ms for 10 cards)
- GET /api/v1/study-cards/analytics/struggling - Cards with low ease factor
- GET /api/v1/study-cards/analytics/mastered - Cards with high repetitions

PERFORMANCE FEATURES:
- Database-level filtering and aggregation
- Composite index utilization
- No Python loops (all SQL)
- Batch operations for efficiency
- Performance logging with warnings

AUSTRALIAN MEDICAL CONTEXT:
- All study cards validated for Australian medical terminology
- Citations reference Australian guidelines (eTG, AMH, AHPRA, NSW Health)
- Content aligned with AMC Clinical Exam preparation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import time
import logging

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.db.base import get_db
from src.db.models import User, StudyCard, MedicalSpecialty
from src.schemas.study_card import StudyCardResponse
from src.auth.dependencies import get_current_active_user
from src.services.review_queue_service import ReviewQueueService

logger = logging.getLogger(__name__)

# Performance threshold (log warning if exceeded)
PERFORMANCE_WARNING_MS = 100

router = APIRouter(prefix="/study-cards", tags=["study-cards-optimized"])


# ============================================================================
# REQUEST/RESPONSE SCHEMAS
# ============================================================================


class DailyQueueResponse(BaseModel):
    """Response for daily review queue"""
    total_due: int = Field(..., description="Total cards due for review")
    cards: List[StudyCardResponse] = Field(..., description="Cards due for review")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")
    has_more: bool = Field(..., description="Whether more cards are available")
    offset: int = Field(..., description="Current offset for pagination")


class OverdueCountResponse(BaseModel):
    """Response for overdue count"""
    overdue_count: int = Field(..., description="Number of cards overdue")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


class SchedulePredictionResponse(BaseModel):
    """Response for schedule prediction"""
    schedule: List[Dict[str, Any]] = Field(..., description="Daily review schedule")
    days_ahead: int = Field(..., description="Number of days predicted")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


class BatchReviewRequest(BaseModel):
    """Request for batch review submission"""
    reviews: List[Dict[str, Any]] = Field(
        ...,
        description="List of reviews with card_id, quality, and time_taken_seconds",
        min_items=1,
        max_items=50
    )


class BatchReviewResponse(BaseModel):
    """Response for batch review submission"""
    results: List[Dict[str, Any]] = Field(..., description="Updated SM-2 parameters for each card")
    cards_updated: int = Field(..., description="Number of cards updated")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


class AnalyticsCardsResponse(BaseModel):
    """Response for struggling/mastered cards"""
    cards: List[StudyCardResponse] = Field(..., description="Filtered study cards")
    count: int = Field(..., description="Number of cards returned")
    query_time_ms: float = Field(..., description="Query execution time in milliseconds")


# ============================================================================
# OPTIMIZED ENDPOINTS
# ============================================================================


@router.get("/queue/daily", response_model=DailyQueueResponse)
async def get_daily_queue(
    limit: int = Query(20, ge=1, le=100, description="Maximum cards to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by specialty"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get daily review queue with optimized query (<100ms target).

    PERFORMANCE OPTIMIZATIONS:
    - Uses composite index: (user_id, next_review_date)
    - Database-level filtering (no Python loops)
    - Orders by urgency (most overdue first)
    - Pagination prevents memory overload

    Query parameters:
    - limit: Maximum cards to return (1-100, default 20)
    - offset: Pagination offset (default 0)
    - specialty: Filter by medical specialty (optional)

    Returns:
    - total_due: Total cards due for review
    - cards: List of study cards due today
    - query_time_ms: Query execution time
    - has_more: Whether more cards are available
    - offset: Current pagination offset

    Performance Target: <100ms (P95)
    Expected: 8-15ms with proper indexes

    Example:
        GET /api/v1/study-cards/queue/daily?limit=20&offset=0&specialty=cardiology

    Raises:
    - 401: User not authenticated
    - 422: Invalid query parameters
    """
    start_time = time.time()

    try:
        # Get daily queue using optimized service
        cards, total_due = ReviewQueueService.get_daily_queue(
            db=db,
            user_id=current_user.id,
            limit=limit,
            specialty=specialty,
            offset=offset,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Log performance warning if threshold exceeded
        if query_time_ms > PERFORMANCE_WARNING_MS:
            logger.warning(
                f"Daily queue query exceeded {PERFORMANCE_WARNING_MS}ms threshold | "
                f"actual={query_time_ms:.2f}ms | user_id={current_user.id} | "
                f"total_due={total_due}"
            )

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

        # Check if more cards are available
        has_more = (offset + len(cards)) < total_due

        return DailyQueueResponse(
            total_due=total_due,
            cards=card_responses,
            query_time_ms=query_time_ms,
            has_more=has_more,
            offset=offset,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in daily queue endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching daily queue"
        )


@router.get("/queue/overdue-count", response_model=OverdueCountResponse)
async def get_overdue_count(
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by specialty"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get fast count of overdue cards (<50ms target).

    PERFORMANCE OPTIMIZATIONS:
    - Index-only query (no table scan)
    - Uses composite index: (user_id, next_review_date)
    - No ORDER BY (faster count)

    Query parameters:
    - specialty: Filter by medical specialty (optional)

    Returns:
    - overdue_count: Number of cards overdue
    - query_time_ms: Query execution time

    Performance Target: <50ms
    Expected: 3-8ms with proper indexes

    Example:
        GET /api/v1/study-cards/queue/overdue-count
        GET /api/v1/study-cards/queue/overdue-count?specialty=cardiology

    Raises:
    - 401: User not authenticated
    """
    start_time = time.time()

    try:
        # Get overdue count using optimized service
        overdue_count = ReviewQueueService.get_overdue_count(
            db=db,
            user_id=current_user.id,
            specialty=specialty,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Log performance warning if threshold exceeded
        if query_time_ms > 50:  # Lower threshold for count queries
            logger.warning(
                f"Overdue count query exceeded 50ms threshold | "
                f"actual={query_time_ms:.2f}ms | user_id={current_user.id}"
            )

        return OverdueCountResponse(
            overdue_count=overdue_count,
            query_time_ms=query_time_ms,
        )

    except Exception as e:
        logger.error(f"Error in overdue count endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching overdue count"
        )


@router.get("/schedule/prediction", response_model=SchedulePredictionResponse)
async def get_schedule_prediction(
    days_ahead: int = Query(7, ge=1, le=30, description="Number of days to predict"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Predict upcoming review schedule (<200ms target).

    PERFORMANCE OPTIMIZATIONS:
    - Database-level GROUP BY with date truncation
    - No Python aggregation loops
    - Uses composite index: (user_id, next_review_date)

    Query parameters:
    - days_ahead: Number of days to predict (1-30, default 7)

    Returns:
    - schedule: List of daily review counts
        [{"date": "2026-02-14", "count": 15}, ...]
    - days_ahead: Number of days predicted
    - query_time_ms: Query execution time

    Performance Target: <200ms
    Expected: 20-50ms with proper indexes

    Example:
        GET /api/v1/study-cards/schedule/prediction?days_ahead=7

    Raises:
    - 401: User not authenticated
    - 422: Invalid days_ahead parameter
    """
    start_time = time.time()

    try:
        # Get schedule prediction using optimized service
        schedule = ReviewQueueService.predict_upcoming_reviews(
            db=db,
            user_id=current_user.id,
            days_ahead=days_ahead,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Log performance warning if threshold exceeded
        if query_time_ms > 200:
            logger.warning(
                f"Schedule prediction query exceeded 200ms threshold | "
                f"actual={query_time_ms:.2f}ms | user_id={current_user.id} | "
                f"days_ahead={days_ahead}"
            )

        return SchedulePredictionResponse(
            schedule=schedule,
            days_ahead=days_ahead,
            query_time_ms=query_time_ms,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in schedule prediction endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching schedule prediction"
        )


@router.post("/queue/batch-review", response_model=BatchReviewResponse)
async def submit_batch_review(
    batch_request: BatchReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Submit batch review and update SM-2 schedules (<500ms for 10 cards).

    PERFORMANCE OPTIMIZATIONS:
    - Single database commit (atomic transaction)
    - Batch updates using bulk_update_mappings
    - Validates all cards before updating

    Request body:
    - reviews: List of reviews (1-50 cards max)
        [
            {"card_id": 1, "quality": 5, "time_taken_seconds": 30},
            {"card_id": 2, "quality": 3, "time_taken_seconds": 45},
            ...
        ]

    Returns:
    - results: Updated SM-2 parameters for each card
    - cards_updated: Number of cards updated
    - query_time_ms: Query execution time

    Performance Target: <500ms for 10 cards
    Expected: 50-150ms with proper indexes

    Example:
        POST /api/v1/study-cards/queue/batch-review
        {
            "reviews": [
                {"card_id": 1, "quality": 5, "time_taken_seconds": 30},
                {"card_id": 2, "quality": 3, "time_taken_seconds": 45}
            ]
        }

    Raises:
    - 401: User not authenticated
    - 404: One or more cards not found
    - 400: Invalid quality rating
    - 422: Invalid request format
    """
    start_time = time.time()

    try:
        # Batch update using optimized service
        results = ReviewQueueService.batch_update_sm2(
            db=db,
            user_id=current_user.id,
            reviews=batch_request.reviews,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

        # Log performance warning if threshold exceeded
        # Scale threshold by number of cards (50ms per card)
        threshold_ms = len(batch_request.reviews) * 50
        if query_time_ms > threshold_ms:
            logger.warning(
                f"Batch review query exceeded {threshold_ms}ms threshold | "
                f"actual={query_time_ms:.2f}ms | user_id={current_user.id} | "
                f"cards={len(batch_request.reviews)}"
            )

        return BatchReviewResponse(
            results=results,
            cards_updated=len(results),
            query_time_ms=query_time_ms,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in batch review endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error processing batch review"
        )


@router.get("/analytics/struggling", response_model=AnalyticsCardsResponse)
async def get_struggling_cards(
    ease_factor_threshold: float = Query(1.5, ge=1.3, le=2.5, description="Ease factor threshold"),
    limit: int = Query(20, ge=1, le=100, description="Maximum cards to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get cards with low ease factor (struggling cards).

    PERFORMANCE OPTIMIZATIONS:
    - Uses index: idx_study_cards_ease_factor
    - Orders by ease factor (lowest first)

    Query parameters:
    - ease_factor_threshold: Threshold for struggling (default 1.5)
    - limit: Maximum cards to return (1-100, default 20)

    Returns:
    - cards: List of struggling study cards
    - count: Number of cards returned
    - query_time_ms: Query execution time

    Performance Target: <100ms
    Expected: 10-25ms with proper indexes

    Example:
        GET /api/v1/study-cards/analytics/struggling?ease_factor_threshold=1.5&limit=20

    Raises:
    - 401: User not authenticated
    """
    start_time = time.time()

    try:
        # Get struggling cards using optimized service
        cards = ReviewQueueService.get_struggling_cards(
            db=db,
            user_id=current_user.id,
            ease_factor_threshold=ease_factor_threshold,
            limit=limit,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

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

        return AnalyticsCardsResponse(
            cards=card_responses,
            count=len(card_responses),
            query_time_ms=query_time_ms,
        )

    except Exception as e:
        logger.error(f"Error in struggling cards endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching struggling cards"
        )


@router.get("/analytics/mastered", response_model=AnalyticsCardsResponse)
async def get_mastered_cards(
    repetitions_threshold: int = Query(3, ge=1, le=100, description="Repetitions threshold"),
    limit: int = Query(20, ge=1, le=100, description="Maximum cards to return"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get cards with high repetition count (mastered cards).

    PERFORMANCE OPTIMIZATIONS:
    - Uses index: idx_study_cards_repetitions
    - Orders by repetitions (highest first)

    Query parameters:
    - repetitions_threshold: Threshold for mastery (default 3)
    - limit: Maximum cards to return (1-100, default 20)

    Returns:
    - cards: List of mastered study cards
    - count: Number of cards returned
    - query_time_ms: Query execution time

    Performance Target: <100ms
    Expected: 10-25ms with proper indexes

    Example:
        GET /api/v1/study-cards/analytics/mastered?repetitions_threshold=3&limit=20

    Raises:
    - 401: User not authenticated
    """
    start_time = time.time()

    try:
        # Get mastered cards using optimized service
        cards = ReviewQueueService.get_mastered_cards(
            db=db,
            user_id=current_user.id,
            repetitions_threshold=repetitions_threshold,
            limit=limit,
        )

        # Calculate query time
        query_time_ms = (time.time() - start_time) * 1000

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

        return AnalyticsCardsResponse(
            cards=card_responses,
            count=len(card_responses),
            query_time_ms=query_time_ms,
        )

    except Exception as e:
        logger.error(f"Error in mastered cards endpoint | error={str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching mastered cards"
        )
