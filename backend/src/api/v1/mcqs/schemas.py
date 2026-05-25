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

    id: int = Field(..., description="Database ID")
    question_id: str = Field(..., description="Unique question ID (e.g., MCQ-CARD-001)")
    question_text: str = Field(..., description="Clinical vignette")
    options: Dict[str, str] = Field(..., description="Answer options (A-E)")
    specialty: MedicalSpecialty = Field(..., description="Medical specialty")
    difficulty: DifficultyLevel = Field(..., description="Difficulty level")
    tags: Optional[List[str]] = Field(None, description="Topic tags")
    image_url: Optional[str] = Field(None, description="Clinical image URL")
    image_caption: Optional[str] = Field(None, description="Image description")
    times_attempted: int = Field(default=0, description="Number of attempts")
    success_rate: float = Field(default=0.0, description="Success rate (0-1)")
    created_at: datetime = Field(..., description="Creation timestamp")

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

    mcq_id: int = Field(..., description="MCQ ID being attempted")
    selected_answer: str = Field(..., description="Selected option (A-E)", pattern="^[A-Ea-e]$")
    time_taken_seconds: Optional[int] = Field(None, description="Time spent on question", ge=0)
    confidence_level: Optional[int] = Field(None, description="Confidence level (1-5)", ge=1, le=5)

    @field_validator("selected_answer")
    def uppercase_answer(cls, value):
        """Convert answer to uppercase"""
        return value.upper()


class MCQSubmitResponse(BaseModel):
    """Response model after submitting MCQ answer"""

    is_correct: bool = Field(..., description="Whether answer was correct")
    selected_answer: str = Field(..., description="User's selected answer")
    correct_answer: str = Field(..., description="Correct option letter")
    explanation: str = Field(..., description="Detailed explanation with clinical reasoning")
    citation: str = Field(..., description="Australian guideline reference")
    learning_points: Optional[List[str]] = Field(None, description="Key learning points")
    attempt_number: int = Field(..., description="Attempt number for this MCQ")

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


class MCQStatistics(BaseModel):
    """Platform-wide MCQ statistics"""

    total_mcqs: int = Field(..., description="Total number of published MCQs")
    by_specialty: Dict[str, int] = Field(..., description="MCQ count by specialty")
    by_difficulty: Dict[str, int] = Field(..., description="MCQ count by difficulty")
    average_success_rate: float = Field(..., description="Average success rate across all MCQs")
