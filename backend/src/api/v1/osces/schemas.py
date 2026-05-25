"""
Pydantic schemas for OSCE API endpoints

AMC CLINICAL EXAM FORMAT:
- 16 stations × 8 minutes each
- 15-mark rubric per station (9/15 to pass)
- Australian medical context and terminology
"""

from pydantic import BaseModel, Field, field_validator
from typing import Any, Optional, List, Dict
from datetime import datetime

from src.db.models import OSCEType, MedicalSpecialty, DifficultyLevel


# Forbidden American terms (MUST be rejected)
FORBIDDEN_AMERICAN_TERMS = [
    "acetaminophen",  # Use paracetamol
    "albuterol",      # Use salbutamol
    "epinephrine",    # Use adrenaline
    "911",            # Use 000 (Australian emergency number)
    "emergency room", # Use emergency department
    "er ",            # Use ED
]

# Required Australian citation sources
REQUIRED_AUSTRALIAN_SOURCES = ["etg", "pbs", "amh", "ahpra", "therapeutic guidelines", "nsw health"]


class OSCEResponse(BaseModel):
    """Response model for OSCE station (candidate view)"""

    id: int = Field(..., description="Database ID")
    osce_id: str = Field(..., description="Unique station ID (e.g., OSCE-CARD-001)")
    station_title: str = Field(..., description="Station title")
    station_type: OSCEType = Field(..., description="Station type (history, exam, etc.)")
    patient_instructions: str = Field(..., description="Instructions for simulated patient")
    candidate_instructions: str = Field(..., description="Instructions for candidate")
    time_limit_minutes: int = Field(..., description="Time limit in minutes (default: 8)")
    specialty: MedicalSpecialty = Field(..., description="Medical specialty")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    tags: Optional[List[str]] = Field(None, description="Topic tags")
    learning_objectives: Optional[List[str]] = Field(None, description="Learning objectives")
    red_flags: Optional[List[str]] = Field(None, description="Red flag symptoms to identify")
    created_at: datetime = Field(..., description="Creation timestamp")

    @field_validator("candidate_instructions", "patient_instructions")
    @classmethod
    def validate_australian_terminology(cls, value):
        """Ensure no American terminology in instructions"""
        content_lower = value.lower()

        for forbidden_term in FORBIDDEN_AMERICAN_TERMS:
            if forbidden_term in content_lower:
                raise ValueError(
                    f"American term '{forbidden_term}' not allowed. "
                    f"Use Australian terminology."
                )

        return value

    model_config = {"from_attributes": True}


class OSCECompletion(BaseModel):
    """Request model for OSCE station completion"""

    user_id: Optional[int] = Field(None, description="User ID (for progress tracking)")
    score: Optional[int] = Field(None, description="Score achieved (0-15)", ge=0, le=15)
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on station", ge=0)
    feedback: Optional[Dict[str, Any]] = Field(None, description="Feedback by rubric category")
    notes: Optional[str] = Field(None, description="Additional notes or reflection")


class OSCECompletionResponse(BaseModel):
    """Response model after OSCE station completion"""

    score: int = Field(..., description="Score achieved (0-15)")
    max_score: int = Field(15, description="Maximum possible score")
    passed: bool = Field(..., description="Whether candidate passed (≥9/15)")
    feedback: Dict[str, Any] = Field(..., description="Detailed feedback by category")
    learning_objectives: Optional[List[str]] = Field(None, description="Learning objectives")
    pass_mark: int = Field(9, description="Pass mark (9/15 for AMC Clinical Exam)")


class OSCERubric(BaseModel):
    """Scoring rubric for OSCE station"""

    osce_id: str = Field(..., description="Station ID")
    station_title: str = Field(..., description="Station title")
    station_type: OSCEType = Field(..., description="Station type")
    rubric: Dict[str, Dict[str, Any]] = Field(..., description="Scoring rubric")
    examiner_instructions: Optional[str] = Field(None, description="Instructions for examiner")
    max_marks: int = Field(15, description="Maximum marks (AMC format)")
    pass_mark: int = Field(9, description="Pass mark (60%)")
    time_limit_minutes: int = Field(8, description="Time limit in minutes")

    @field_validator("rubric")
    @classmethod
    def validate_rubric_total(cls, value):
        """Ensure rubric categories sum to 15 marks"""
        total_marks = sum(
            category.get("max_marks", category.get("marks", 0))
            for category in value.values()
        )

        if total_marks != 15:
            raise ValueError(
                f"Rubric categories must sum to 15 marks (AMC Clinical Exam format). "
                f"Current total: {total_marks}"
            )

        return value
