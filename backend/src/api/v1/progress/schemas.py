"""
Progress Tracking API Schemas
Pydantic models for request/response validation
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ProgressResponse(BaseModel):
    """User progress for a specific specialty"""

    id: int
    user_id: int
    specialty: str
    total_mcqs_attempted: int = Field(ge=0, description="Total MCQs attempted in specialty")
    total_mcqs_correct: int = Field(ge=0, description="Total correct answers")
    unique_mcqs_attempted: int = Field(ge=0, description="Unique questions attempted")
    total_osces_practiced: int = Field(ge=0, description="Total OSCE stations practiced")
    average_osce_score: float = Field(ge=0.0, le=15.0, description="Average OSCE score (0-15)")
    current_streak_days: int = Field(ge=0, description="Current daily study streak")
    longest_streak_days: int = Field(ge=0, description="Longest study streak achieved")
    last_activity_date: Optional[datetime] = Field(None, description="Last activity timestamp")
    total_study_time_minutes: int = Field(ge=0, description="Total study time in specialty")
    weak_topics: Optional[List[str]] = Field(None, description="Topics needing improvement")
    mastery_percentage: float = Field(ge=0.0, le=100.0, description="Overall mastery level")
    success_rate: float = Field(ge=0.0, le=100.0, description="MCQ success rate percentage")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AllProgressResponse(BaseModel):
    """All progress records for a user across all specialties"""

    user_id: int
    progress_records: List[ProgressResponse]
    total_mcqs_attempted: int = Field(description="Total MCQs across all specialties")
    total_study_time_minutes: int = Field(description="Total study time across all specialties")
    overall_success_rate: float = Field(ge=0.0, le=100.0, description="Success rate across all specialties")
    active_specialties: int = Field(description="Number of specialties with activity")


class StreakResponse(BaseModel):
    """Study streak information"""

    user_id: int
    current_streak_days: int = Field(ge=0)
    longest_streak_days: int = Field(ge=0)
    last_activity_date: Optional[datetime]
    is_active_today: bool = Field(description="Whether user has studied today")


class WeakTopicsResponse(BaseModel):
    """Weak topics aggregated across all specialties"""

    user_id: int
    weak_topics: List[dict] = Field(
        description="List of weak topics with specialty context",
        example=[
            {"specialty": "Cardiology", "topics": ["hypertension", "arrhythmias"]},
            {"specialty": "Neurology", "topics": ["stroke", "seizures"]},
        ],
    )
    total_weak_topics: int


class UpdateProgressRequest(BaseModel):
    """Request to update progress after completing an activity"""

    specialty: str = Field(..., description="Medical specialty")
    activity_type: str = Field(..., description="Type of activity: 'mcq' or 'osce'")
    is_correct: Optional[bool] = Field(None, description="For MCQ: whether answer was correct")
    osce_score: Optional[float] = Field(None, ge=0.0, le=15.0, description="For OSCE: score out of 15")
    study_time_minutes: int = Field(ge=0, description="Time spent on this activity")
    weak_topics: Optional[List[str]] = Field(None, description="Topics identified as weak during activity")

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "specialty": "Cardiology",
                    "activity_type": "mcq",
                    "is_correct": True,
                    "study_time_minutes": 3,
                    "weak_topics": None,
                },
                {
                    "specialty": "Neurology",
                    "activity_type": "osce",
                    "osce_score": 12.5,
                    "study_time_minutes": 8,
                    "weak_topics": ["stroke assessment", "Glasgow Coma Scale"],
                },
            ]
        }
