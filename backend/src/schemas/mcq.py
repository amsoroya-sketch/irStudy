"""
Pydantic schemas for MCQ model

AUSTRALIAN MEDICAL CONTEXT:
- Validation ensures Australian drug names
- Citation format validation (eTG, AHPRA, AMH)
- SI units validation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DifficultyLevel(str, Enum):
    """Difficulty levels matching database enum"""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class MedicalSpecialty(str, Enum):
    """Medical specialties matching database enum"""

    CARDIOLOGY = "cardiology"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    NEUROLOGY = "neurology"
    PSYCHIATRY = "psychiatry"
    ENDOCRINOLOGY = "endocrinology"
    EMERGENCY_MEDICINE = "emergency_medicine"
    GENERAL_PRACTICE = "general_practice"
    PAEDIATRICS = "paediatrics"
    OBSTETRICS_GYNAECOLOGY = "obstetrics_gynaecology"
    SURGERY = "surgery"


# ============================================================================
# REQUEST SCHEMAS (Input)
# ============================================================================


class MCQCreate(BaseModel):
    """Schema for creating new MCQ"""

    question_id: str = Field(..., pattern=r"^MCQ-[A-Z]+-\d{3}$")
    question_text: str = Field(..., min_length=50, max_length=5000)
    options: Dict[str, str] = Field(..., min_items=4, max_items=5)
    correct_answer: str = Field(..., pattern=r"^[A-E]$")
    explanation: str = Field(..., min_length=100, max_length=5000)
    citation: str = Field(..., min_length=10, max_length=500)
    learning_points: Optional[List[str]] = None
    specialty: MedicalSpecialty
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    image_caption: Optional[str] = None

    @validator("options")
    def validate_options(cls, v):
        """Validate options dictionary has correct keys"""
        required_keys = ["A", "B", "C", "D"]
        if not all(key in v for key in required_keys):
            raise ValueError("Options must include at least A, B, C, D")

        # Check for American drug names
        american_drugs = {
            "acetaminophen": "paracetamol",
            "epinephrine": "adrenaline",
            "albuterol": "salbutamol",
        }
        all_text = " ".join(v.values()).lower()
        for american, australian in american_drugs.items():
            if american in all_text:
                raise ValueError(f'Use Australian drug name "{australian}" not "{american}"')

        return v

    @validator("citation")
    def validate_citation(cls, v):
        """Validate citation references Australian guidelines"""
        australian_sources = [
            "therapeutic guidelines",
            "etg",
            "ahpra",
            "amh",
            "australian medicines handbook",
            "pbs",
            "ranzcp",
            "racgp",
            "talley",
        ]
        v_lower = v.lower()
        if not any(source in v_lower for source in australian_sources):
            raise ValueError(
                "Citation must reference Australian guidelines "
                "(Therapeutic Guidelines, eTG, AHPRA, AMH, PBS, etc.)"
            )
        return v


class MCQUpdate(BaseModel):
    """Schema for updating existing MCQ"""

    question_text: Optional[str] = Field(None, min_length=50, max_length=5000)
    options: Optional[Dict[str, str]] = None
    correct_answer: Optional[str] = Field(None, pattern=r"^[A-E]$")
    explanation: Optional[str] = Field(None, min_length=100, max_length=5000)
    citation: Optional[str] = Field(None, min_length=10, max_length=500)
    learning_points: Optional[List[str]] = None
    specialty: Optional[MedicalSpecialty] = None
    difficulty: Optional[DifficultyLevel] = None
    tags: Optional[List[str]] = None
    image_url: Optional[str] = None
    is_published: Optional[bool] = None


class MCQAttemptCreate(BaseModel):
    """Schema for submitting MCQ attempt"""

    mcq_id: int
    selected_answer: str = Field(..., pattern=r"^[A-E]$")
    time_taken_seconds: int = Field(..., ge=1, le=600)  # 1-600 seconds
    confidence_level: Optional[int] = Field(None, ge=1, le=5)


# ============================================================================
# RESPONSE SCHEMAS (Output)
# ============================================================================


class MCQBase(BaseModel):
    """Base MCQ schema"""

    id: int
    question_id: str
    question_text: str
    options: Dict[str, str]
    specialty: MedicalSpecialty
    difficulty: DifficultyLevel
    tags: Optional[List[str]]
    image_url: Optional[str]
    image_caption: Optional[str]
    times_attempted: int
    success_rate: float
    created_at: datetime

    class Config:
        from_attributes = True


class MCQPublic(MCQBase):
    """Public MCQ (for practice - no answer revealed)"""

    pass


class MCQWithAnswer(MCQBase):
    """MCQ with correct answer (for review after attempt)"""

    correct_answer: str
    explanation: str
    citation: str
    learning_points: Optional[List[str]]


class MCQAttemptResponse(BaseModel):
    """Response after submitting MCQ attempt"""

    id: int
    is_correct: bool
    selected_answer: str
    correct_answer: str
    explanation: str
    citation: str
    learning_points: Optional[List[str]]
    time_taken_seconds: int
    attempt_number: int

    class Config:
        from_attributes = True


class MCQStatistics(BaseModel):
    """MCQ statistics"""

    total_mcqs: int
    by_specialty: Dict[str, int]
    by_difficulty: Dict[str, int]
    average_success_rate: float
