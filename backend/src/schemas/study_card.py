"""
Pydantic schemas for Study Card model

AUSTRALIAN MEDICAL CONTEXT:
- Validation ensures Australian drug names
- Citation format validation (eTG, AHPRA, AMH)
- Spaced repetition using SM-2 algorithm
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
# BASE SCHEMAS
# ============================================================================


class CitationSchema(BaseModel):
    """Schema for individual citation"""

    title: str
    author: str = "Unknown Author"
    year: str = "2020"
    page: Optional[int] = None
    content: str = ""
    rag_confidence: Optional[float] = None
    source_type: str = "textbook"


class StudyCardBase(BaseModel):
    """Base study card schema with common fields"""

    card_id: str = Field(..., pattern=r"^[A-Z]+-CARD-\d{4}$")
    specialty: MedicalSpecialty
    topic: str = Field(..., min_length=3, max_length=255)
    subtopic: Optional[str] = Field(None, max_length=255)
    question: str = Field(..., min_length=10, max_length=5000)
    answer: str = Field(..., min_length=10, max_length=5000)
    explanation: Optional[str] = Field(None, max_length=5000)
    citations: List[Dict] = Field(..., min_items=1, max_items=5)
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: Optional[List[str]] = []
    card_type: str = "concept"

    @validator("citations")
    def validate_citations(cls, v):
        """Validate citations reference Australian guidelines"""
        if not v or len(v) == 0:
            raise ValueError("At least one citation is required")

        # Check that citations have required fields
        for citation in v:
            if not isinstance(citation, dict):
                raise ValueError("Citations must be dictionary objects")
            if "title" not in citation:
                raise ValueError("Citation must have 'title' field")

        return v


# ============================================================================
# REQUEST SCHEMAS (Input)
# ============================================================================


class StudyCardCreate(StudyCardBase):
    """Schema for creating new study card"""

    pass


class StudyCardUpdate(BaseModel):
    """Schema for updating existing study card"""

    question: Optional[str] = Field(None, min_length=10, max_length=5000)
    answer: Optional[str] = Field(None, min_length=10, max_length=5000)
    explanation: Optional[str] = Field(None, max_length=5000)
    tags: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None

    # Spaced repetition fields (updated by review logic)
    next_review_date: Optional[datetime] = None
    interval_days: Optional[int] = Field(None, ge=1)
    ease_factor: Optional[float] = Field(None, ge=1.3, le=3.0)
    repetitions: Optional[int] = Field(None, ge=0)


# ============================================================================
# RESPONSE SCHEMAS (Output)
# ============================================================================


class StudyCardResponse(StudyCardBase):
    """Schema for study card API responses"""

    id: int
    user_id: Optional[int]
    next_review_date: datetime
    interval_days: int
    ease_factor: float
    repetitions: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StudyCardPublic(BaseModel):
    """Public study card (for practice - front only initially)"""

    id: int
    card_id: str
    specialty: MedicalSpecialty
    topic: str
    subtopic: Optional[str]
    question: str  # Front of card
    difficulty: DifficultyLevel
    tags: Optional[List[str]]
    card_type: str

    class Config:
        from_attributes = True


class StudyCardWithAnswer(StudyCardPublic):
    """Study card with answer revealed (after user attempts)"""

    answer: str
    explanation: Optional[str]
    citations: List[Dict]


# ============================================================================
# SPACED REPETITION SCHEMAS
# ============================================================================


class StudyCardReview(BaseModel):
    """Schema for submitting study card review"""

    card_id: int = Field(..., description="Study card ID to review")
    quality: int = Field(..., ge=0, le=5, description="Quality rating 0-5 (SM-2 algorithm)")
    time_taken_seconds: int = Field(..., ge=1, description="Time taken to review (seconds)")


class StudyCardReviewResponse(BaseModel):
    """Response after reviewing a study card"""

    card_id: int
    quality: int
    next_review_date: datetime
    interval_days: int
    ease_factor: float
    repetitions: int
    message: str
    quality_description: str

    class Config:
        from_attributes = True


class StudyCardsDueResponse(BaseModel):
    """Response for cards due for review"""

    total_due: int
    cards: List[StudyCardResponse]


# ============================================================================
# STATISTICS SCHEMAS
# ============================================================================


class StudyCardStatistics(BaseModel):
    """Study card statistics"""

    total_cards: int
    by_specialty: Dict[str, int]
    by_difficulty: Dict[str, int]
    cards_due_today: int
    cards_mastered: int  # repetitions >= 3
    average_ease_factor: float
    total_reviews: int
    reviews_today: int
    average_quality: float
    retention_rate: float  # Percentage of quality >= 3 reviews


# ============================================================================
# GENERATE FROM OSCE SCHEMAS (PRD-P1-005 Phase 4)
# ============================================================================


class GenerateCardsRequest(BaseModel):
    """Request to generate study cards from OSCE session (PRD-P1-005)"""

    session_id: str = Field(
        ...,
        description="OSCE session UUID",
        example="550e8400-e29b-41d4-a716-446655440000",
        min_length=36,
        max_length=36,
    )

    @validator("session_id")
    def validate_uuid_format(cls, v):
        """Validate session_id is proper UUID format"""
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        if not re.match(uuid_pattern, v.lower()):
            raise ValueError(f"Invalid UUID format: {v}")
        return v


class GeneratedStudyCardResponse(BaseModel):
    """Individual study card in generation response"""

    id: int
    user_id: int
    session_id: str
    card_id: str
    specialty: str
    topic: str
    subtopic: Optional[str]
    question: str
    answer: str
    explanation: Optional[str]
    citations: List[Dict]
    difficulty: str
    tags: List[str]
    card_type: str

    # SM-2 parameters
    ease_factor: float
    interval_days: int
    repetitions: int
    next_review_date: datetime

    # Timestamps
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GenerateCardsResponse(BaseModel):
    """Response after generating study cards from OSCE session"""

    cards: List[GeneratedStudyCardResponse]
    count: int = Field(..., description="Number of cards generated")
    session_id: str
    message: str = Field(
        default="Study cards generated successfully",
        description="Success message",
    )
