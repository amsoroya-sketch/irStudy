"""
Pydantic schemas for MCQ API endpoints

AUSTRALIAN CONTEXT VALIDATION:
- All drug names validated against Australian terminology
- Citations must reference eTG, PBS, AMH, or AHPRA
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.db.models import MedicalSpecialty, DifficultyLevel


# Forbidden American drug names (MUST be rejected)
FORBIDDEN_DRUG_NAMES = [
    "acetaminophen",  # Use paracetamol
    "albuterol",      # Use salbutamol
    "epinephrine",    # Use adrenaline
    "tylenol",        # Use paracetamol
    "ventolin",       # Brand name - use salbutamol
]

# Required Australian citation sources
REQUIRED_CITATION_SOURCES = ["etg", "pbs", "amh", "ahpra", "therapeutic guidelines"]


class MCQResponse(BaseModel):
    """Response model for MCQ question (without answer)"""

    question_id: str = Field(..., description="Unique question ID (e.g., MCQ-CARD-001)")
    question_text: str = Field(..., description="Clinical vignette")
    options: Dict[str, str] = Field(..., description="Answer options (A-E)")
    specialty: MedicalSpecialty = Field(..., description="Medical specialty")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    tags: Optional[List[str]] = Field(None, description="Topic tags")
    image_url: Optional[str] = Field(None, description="Clinical image URL")

    @field_validator("question_text", mode="before")
    def validate_australian_drug_names(cls, value):
        """Ensure no American drug names in question content"""
        content = str(value).lower()

        for forbidden_drug in FORBIDDEN_DRUG_NAMES:
            if forbidden_drug in content:
                raise ValueError(
                    f"American drug name '{forbidden_drug}' not allowed. "
                    f"Use Australian terminology."
                )

        return value

    model_config = {"from_attributes": True}


class MCQSubmit(BaseModel):
    """Request model for submitting MCQ answer"""

    selected_answer: str = Field(..., description="Selected option (A-E)", pattern="^[A-Ea-e]$")
    user_id: Optional[int] = Field(None, description="User ID (for progress tracking)")
    time_spent_seconds: Optional[int] = Field(None, description="Time spent on question", ge=0)

    @field_validator("selected_answer")
    def uppercase_answer(cls, value):
        """Convert answer to uppercase"""
        return value.upper()


class MCQSubmitResponse(BaseModel):
    """Response model after submitting MCQ answer"""

    is_correct: bool = Field(..., description="Whether answer was correct")
    correct_answer: str = Field(..., description="Correct option letter")
    explanation: str = Field(..., description="Detailed explanation with clinical reasoning")
    citation: str = Field(..., description="Australian guideline reference")
    learning_points: Optional[List[str]] = Field(None, description="Key learning points")

    @field_validator("citation", mode="after")
    def validate_australian_citation(cls, value):
        """Ensure citation references Australian sources"""
        citation_lower = value.lower()

        has_australian_source = any(
            source in citation_lower for source in REQUIRED_CITATION_SOURCES
        )

        if not has_australian_source:
            raise ValueError(
                "Citation must reference Australian medical guidelines "
                "(eTG, PBS, AMH, AHPRA, or Therapeutic Guidelines)"
            )

        return value


class MCQExplanation(BaseModel):
    """Detailed explanation model for MCQ"""

    correct_answer: str = Field(..., description="Correct option letter")
    explanation: str = Field(..., description="Detailed clinical explanation")
    citation: str = Field(..., description="Australian guideline reference")
    learning_points: Optional[List[str]] = Field(None, description="Key learning points")
    specialty: MedicalSpecialty = Field(..., description="Medical specialty")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")

    @field_validator("citation", mode="after")
    def validate_australian_citation(cls, value):
        """Ensure citation references Australian sources"""
        citation_lower = value.lower()

        has_australian_source = any(
            source in citation_lower for source in REQUIRED_CITATION_SOURCES
        )

        if not has_australian_source:
            raise ValueError(
                "Citation must reference Australian medical guidelines "
                "(eTG, PBS, AMH, AHPRA, or Therapeutic Guidelines)"
            )

        return value
