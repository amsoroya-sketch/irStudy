"""
MCQ API endpoints for irStudy Medical Education Platform

AUSTRALIAN CONTEXT:
- Drug names: Australian only (paracetamol NOT acetaminophen)
- Citations: eTG, PBS, AMH, AHPRA only
- All content validated against Australian medical guidelines

ENDPOINTS:
- GET /mcqs/random - Get random MCQ by specialty/difficulty
- GET /mcqs/{id} - Get specific MCQ by ID
- POST /mcqs/{id}/submit - Submit answer and get explanation
- GET /mcqs/{id}/explanation - Get explanation with citations
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import Optional, List
import random

from src.db.base import get_db
from src.db.models import MCQ, MCQAttempt, MedicalSpecialty, DifficultyLevel
from src.api.v1.mcqs import schemas

router = APIRouter(prefix="/mcqs", tags=["MCQ Practice"])


@router.get("/random", response_model=schemas.MCQResponse)
async def get_random_mcq(
    specialty: Optional[MedicalSpecialty] = Query(None, description="Filter by medical specialty"),
    difficulty: Optional[DifficultyLevel] = Query(None, description="Filter by difficulty level"),
    db: Session = Depends(get_db)
):
    """
    Get a random MCQ question.

    **Australian Context:**
    - All questions use Australian drug names (paracetamol, salbutamol, adrenaline)
    - Citations reference Australian guidelines (eTG, PBS, AMH, AHPRA)

    **Query Parameters:**
    - specialty: Filter by specialty (cardiology, respiratory, etc.)
    - difficulty: Filter by difficulty (easy, medium, hard)
    """
    query = db.query(MCQ)

    if specialty:
        query = query.filter(MCQ.specialty == specialty)
    if difficulty:
        query = query.filter(MCQ.difficulty == difficulty)

    mcqs = query.all()

    if not mcqs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No MCQs found matching criteria"
        )

    selected_mcq = random.choice(mcqs)

    return schemas.MCQResponse.from_orm(selected_mcq)


@router.get("/{mcq_id}", response_model=schemas.MCQResponse)
async def get_mcq(
    mcq_id: str,
    db: Session = Depends(get_db)
):
    """
    Get specific MCQ by question_id.

    **Example:** GET /mcqs/MCQ-CARD-001
    """
    mcq = db.query(MCQ).filter(MCQ.question_id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    return schemas.MCQResponse.from_orm(mcq)


@router.post("/{mcq_id}/submit", response_model=schemas.MCQSubmitResponse)
async def submit_mcq_answer(
    mcq_id: str,
    submission: schemas.MCQSubmit,
    db: Session = Depends(get_db)
):
    """
    Submit answer to MCQ and receive feedback.

    **Returns:**
    - is_correct: Whether answer was correct
    - correct_answer: The correct option letter
    - explanation: Detailed explanation with clinical reasoning
    - citation: Australian guideline reference
    - learning_points: Key learning points (if available)
    """
    mcq = db.query(MCQ).filter(MCQ.question_id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    is_correct = submission.selected_answer.upper() == mcq.correct_answer

    # Record attempt (if user_id provided)
    if submission.user_id:
        attempt = MCQAttempt(
            user_id=submission.user_id,
            mcq_id=mcq.id,
            selected_answer=submission.selected_answer.upper(),
            is_correct=is_correct,
            time_taken_seconds=submission.time_spent_seconds
        )
        db.add(attempt)
        db.commit()

    return schemas.MCQSubmitResponse(
        is_correct=is_correct,
        correct_answer=mcq.correct_answer,
        explanation=mcq.explanation,
        citation=mcq.citation,
        learning_points=mcq.learning_points
    )


@router.get("/{mcq_id}/explanation", response_model=schemas.MCQExplanation)
async def get_mcq_explanation(
    mcq_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed explanation and citation for MCQ.

    **Australian Context:**
    - All citations reference Australian medical guidelines
    - Drug names use Australian terminology
    - Emergency protocols follow Australian standards
    """
    mcq = db.query(MCQ).filter(MCQ.question_id == mcq_id).first()

    if not mcq:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"MCQ with ID {mcq_id} not found"
        )

    return schemas.MCQExplanation(
        correct_answer=mcq.correct_answer,
        explanation=mcq.explanation,
        citation=mcq.citation,
        learning_points=mcq.learning_points,
        specialty=mcq.specialty,
        difficulty=mcq.difficulty
    )
