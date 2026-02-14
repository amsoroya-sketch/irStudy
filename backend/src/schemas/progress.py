"""
Progress and analytics schemas

SCHEMAS:
- SpecialtyPerformance: Performance metrics for a single specialty
- WeakArea: Specialty identified as needing improvement
- DashboardResponse: Comprehensive dashboard with all metrics
- WeeklyTrend: Weekly progress trend data
- SpecialtyDetailResponse: Detailed performance for one specialty

PRIVACY:
- All data scoped to current_user (never exposes other users' data)
- No raw user IDs or sensitive information
- Percentages rounded to 2 decimal places
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ============================================================================
# SPECIALTY PERFORMANCE
# ============================================================================


class SpecialtyPerformance(BaseModel):
    """
    Performance metrics for a single specialty.

    FIELDS:
    - specialty: Medical specialty name
    - total_attempts: Total MCQ attempts in this specialty
    - correct_attempts: Number of correct answers
    - accuracy_rate: Success percentage (0-100, rounded to 2 decimals)
    - average_time_seconds: Average time per question (seconds)
    """

    specialty: str = Field(..., description="Medical specialty (e.g., cardiology)")
    total_attempts: int = Field(..., ge=0, description="Total MCQ attempts")
    correct_attempts: int = Field(..., ge=0, description="Number of correct answers")
    accuracy_rate: float = Field(..., ge=0, le=100, description="Success percentage")
    average_time_seconds: int = Field(..., ge=0, description="Average time per question (seconds)")

    class Config:
        json_schema_extra = {
            "example": {
                "specialty": "cardiology",
                "total_attempts": 45,
                "correct_attempts": 32,
                "accuracy_rate": 71.11,
                "average_time_seconds": 95
            }
        }


# ============================================================================
# WEAK AREA
# ============================================================================


class WeakArea(BaseModel):
    """
    Specialty identified as needing improvement.

    CRITERIA:
    - Accuracy below threshold (default 70%)
    - Minimum attempts threshold (default 5)

    FIELDS:
    - specialty: Medical specialty name
    - accuracy_rate: Success percentage
    - total_attempts: Total attempts in this specialty
    - recommended_study_cards: Number of study cards available for this specialty
    """

    specialty: str = Field(..., description="Medical specialty needing improvement")
    accuracy_rate: float = Field(..., ge=0, le=100, description="Success percentage")
    total_attempts: int = Field(..., ge=0, description="Total attempts")
    recommended_study_cards: int = Field(..., ge=0, description="Available study cards count")

    class Config:
        json_schema_extra = {
            "example": {
                "specialty": "neurology",
                "accuracy_rate": 58.33,
                "total_attempts": 12,
                "recommended_study_cards": 47
            }
        }


# ============================================================================
# WEEKLY TREND
# ============================================================================


class WeeklyTrend(BaseModel):
    """
    Weekly progress trend data.

    FIELDS:
    - week_start: Start date of the week (Monday)
    - mcq_attempts: MCQ attempts during this week
    - accuracy_rate: Success percentage for this week
    - study_cards_reviewed: Study cards reviewed during this week
    """

    week_start: datetime = Field(..., description="Start date of the week (Monday)")
    mcq_attempts: int = Field(..., ge=0, description="MCQ attempts this week")
    accuracy_rate: float = Field(..., ge=0, le=100, description="Success percentage this week")
    study_cards_reviewed: int = Field(..., ge=0, description="Study cards reviewed this week")

    class Config:
        json_schema_extra = {
            "example": {
                "week_start": "2026-02-10T00:00:00Z",
                "mcq_attempts": 28,
                "accuracy_rate": 75.00,
                "study_cards_reviewed": 15
            }
        }


# ============================================================================
# DASHBOARD RESPONSE
# ============================================================================


class DashboardResponse(BaseModel):
    """
    Comprehensive dashboard analytics.

    FEATURES:
    - MCQ performance metrics
    - OSCE completion tracking
    - Study Card statistics
    - Specialty breakdown
    - Weak areas identification

    FIELDS:
    - total_mcq_attempts: Total MCQ attempts (all specialties)
    - mcq_accuracy_rate: Overall MCQ success percentage
    - total_osce_completions: Total OSCE stations practiced
    - study_cards_reviewed: Total study cards reviewed
    - study_card_retention_rate: Study Card retention percentage (quality >= 3)
    - specialty_breakdown: Performance per specialty
    - weak_areas: Specialties below threshold
    """

    total_mcq_attempts: int = Field(..., ge=0, description="Total MCQ attempts")
    mcq_accuracy_rate: float = Field(..., ge=0, le=100, description="Overall MCQ accuracy")
    total_osce_completions: int = Field(..., ge=0, description="Total OSCE stations practiced")
    study_cards_reviewed: int = Field(..., ge=0, description="Total study cards reviewed")
    study_card_retention_rate: float = Field(..., ge=0, le=100, description="Study Card retention rate")
    specialty_breakdown: List[SpecialtyPerformance] = Field(..., description="Performance per specialty")
    weak_areas: List[WeakArea] = Field(..., description="Specialties needing improvement")

    class Config:
        json_schema_extra = {
            "example": {
                "total_mcq_attempts": 152,
                "mcq_accuracy_rate": 73.68,
                "total_osce_completions": 8,
                "study_cards_reviewed": 64,
                "study_card_retention_rate": 78.12,
                "specialty_breakdown": [
                    {
                        "specialty": "cardiology",
                        "total_attempts": 45,
                        "correct_attempts": 32,
                        "accuracy_rate": 71.11,
                        "average_time_seconds": 95
                    }
                ],
                "weak_areas": [
                    {
                        "specialty": "neurology",
                        "accuracy_rate": 58.33,
                        "total_attempts": 12,
                        "recommended_study_cards": 47
                    }
                ]
            }
        }


# ============================================================================
# SPECIALTY DETAIL RESPONSE
# ============================================================================


class SpecialtyDetailResponse(BaseModel):
    """
    Detailed performance for one specialty.

    FIELDS:
    - specialty: Medical specialty name
    - total_attempts: Total MCQ attempts
    - correct_attempts: Number of correct answers
    - accuracy_rate: Success percentage
    - average_time_seconds: Average time per question
    - osce_completions: OSCE stations practiced in this specialty
    - study_cards_available: Available study cards count
    - recent_attempts: Recent attempt count (last 7 days)
    """

    specialty: str = Field(..., description="Medical specialty")
    total_attempts: int = Field(..., ge=0, description="Total MCQ attempts")
    correct_attempts: int = Field(..., ge=0, description="Number of correct answers")
    accuracy_rate: float = Field(..., ge=0, le=100, description="Success percentage")
    average_time_seconds: int = Field(..., ge=0, description="Average time per question")
    osce_completions: int = Field(..., ge=0, description="OSCE stations practiced")
    study_cards_available: int = Field(..., ge=0, description="Available study cards count")
    recent_attempts: int = Field(..., ge=0, description="Attempts in last 7 days")

    class Config:
        json_schema_extra = {
            "example": {
                "specialty": "cardiology",
                "total_attempts": 45,
                "correct_attempts": 32,
                "accuracy_rate": 71.11,
                "average_time_seconds": 95,
                "osce_completions": 3,
                "study_cards_available": 82,
                "recent_attempts": 12
            }
        }


# ============================================================================
# WEEKLY TRENDS RESPONSE
# ============================================================================


class WeeklyTrendsResponse(BaseModel):
    """
    Weekly trends response.

    FIELDS:
    - weeks: Number of weeks in trend data
    - trends: List of weekly trend data (most recent first)
    """

    weeks: int = Field(..., ge=1, le=12, description="Number of weeks")
    trends: List[WeeklyTrend] = Field(..., description="Weekly trend data")

    class Config:
        json_schema_extra = {
            "example": {
                "weeks": 4,
                "trends": [
                    {
                        "week_start": "2026-02-10T00:00:00Z",
                        "mcq_attempts": 28,
                        "accuracy_rate": 75.00,
                        "study_cards_reviewed": 15
                    },
                    {
                        "week_start": "2026-02-03T00:00:00Z",
                        "mcq_attempts": 35,
                        "accuracy_rate": 71.43,
                        "study_cards_reviewed": 22
                    }
                ]
            }
        }


# ============================================================================
# WEAK AREAS RESPONSE
# ============================================================================


class WeakAreasResponse(BaseModel):
    """
    Weak areas response.

    FIELDS:
    - threshold: Accuracy threshold used (percentage)
    - min_attempts: Minimum attempts required for inclusion
    - weak_areas: List of weak specialties
    """

    threshold: float = Field(..., ge=0, le=100, description="Accuracy threshold")
    min_attempts: int = Field(..., ge=1, description="Minimum attempts threshold")
    weak_areas: List[WeakArea] = Field(..., description="Weak specialties")

    class Config:
        json_schema_extra = {
            "example": {
                "threshold": 70.0,
                "min_attempts": 5,
                "weak_areas": [
                    {
                        "specialty": "neurology",
                        "accuracy_rate": 58.33,
                        "total_attempts": 12,
                        "recommended_study_cards": 47
                    }
                ]
            }
        }
