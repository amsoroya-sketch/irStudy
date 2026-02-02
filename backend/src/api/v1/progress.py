"""
User progress and analytics endpoints

Routes:
- GET /api/v1/progress/dashboard - Get dashboard analytics  
- GET /api/v1/progress/weak-areas - Identify weak topics
- GET /api/v1/progress/stats - Overall statistics
- GET /api/v1/progress/specialty/{specialty} - Specialty progress

FEATURES:
- Personalized analytics based on MCQ attempts
- Weak area identification (topics with <70% success rate)
- Study streak tracking
- Specialty-specific progress breakdown
- Australian medical context preserved
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from db.base import get_db
from db.models import (
    User,
    MCQ,
    MCQAttempt,
    UserProgress,
    MedicalSpecialty,
    DifficultyLevel
)
from auth.dependencies import get_current_active_user


router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/dashboard")
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard analytics for current user"""
    
    # Overall statistics
    total_attempts = db.query(func.count(MCQAttempt.id)).filter(
        MCQAttempt.user_id == current_user.id
    ).scalar() or 0

    total_correct = db.query(func.count(MCQAttempt.id)).filter(
        MCQAttempt.user_id == current_user.id,
        MCQAttempt.is_correct == True
    ).scalar() or 0

    overall_success_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0

    # By specialty
    specialty_stats = db.query(
        MCQ.specialty,
        func.count(MCQAttempt.id).label("attempts"),
        func.sum(case((MCQAttempt.is_correct == True, 1), else_=0)).label("correct"),
    ).join(
        MCQAttempt, MCQAttempt.mcq_id == MCQ.id
    ).filter(
        MCQAttempt.user_id == current_user.id
    ).group_by(MCQ.specialty).all()

    by_specialty = {
        str(specialty): {
            "attempts": attempts,
            "correct": int(correct),
            "success_rate": round((correct / attempts * 100) if attempts > 0 else 0.0, 2)
        }
        for specialty, attempts, correct in specialty_stats
    }

    return {
        "overall_stats": {
            "total_attempts": total_attempts,
            "total_correct": total_correct,
            "success_rate": round(overall_success_rate, 2)
        },
        "by_specialty": by_specialty
    }


@router.get("/weak-areas")
async def identify_weak_areas(
    min_attempts: int = 5,
    threshold_percentage: float = 70.0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Identify topics where user needs improvement"""
    
    specialty_performance = db.query(
        MCQ.specialty,
        func.count(MCQAttempt.id).label("attempts"),
        func.sum(case((MCQAttempt.is_correct == True, 1), else_=0)).label("correct"),
    ).join(
        MCQAttempt, MCQAttempt.mcq_id == MCQ.id
    ).filter(
        MCQAttempt.user_id == current_user.id
    ).group_by(MCQ.specialty).having(
        func.count(MCQAttempt.id) >= min_attempts
    ).all()

    weak_specialties = []
    for specialty, attempts, correct in specialty_performance:
        success_rate = (correct / attempts * 100) if attempts > 0 else 0.0
        if success_rate < threshold_percentage:
            weak_specialties.append({
                "specialty": str(specialty),
                "attempts": attempts,
                "correct": int(correct),
                "success_rate": round(success_rate, 2),
                "priority": "urgent" if success_rate < 50 else "important"
            })

    weak_specialties.sort(key=lambda x: x["success_rate"])

    return {
        "weak_specialties": weak_specialties,
        "criteria": {
            "min_attempts": min_attempts,
            "threshold_percentage": threshold_percentage
        }
    }


@router.get("/stats")
async def get_overall_statistics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive statistics across all activity"""
    
    # Total unique questions
    unique_questions = db.query(
        func.count(func.distinct(MCQAttempt.mcq_id))
    ).filter(
        MCQAttempt.user_id == current_user.id
    ).scalar() or 0

    # Total attempts
    total_attempts = db.query(
        func.count(MCQAttempt.id)
    ).filter(
        MCQAttempt.user_id == current_user.id
    ).scalar() or 0

    # Overall success rate
    total_correct = db.query(
        func.count(MCQAttempt.id)
    ).filter(
        MCQAttempt.user_id == current_user.id,
        MCQAttempt.is_correct == True
    ).scalar() or 0

    success_rate = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0

    return {
        "total_questions_attempted": unique_questions,
        "total_attempts": total_attempts,
        "success_rate": round(success_rate, 2),
        "amc_exam_readiness": {
            "estimated_readiness": "ready" if success_rate >= 70 else "needs_practice",
            "your_success_rate": round(success_rate, 2)
        }
    }
