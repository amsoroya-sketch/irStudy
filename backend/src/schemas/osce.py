"""
Pydantic schemas for OSCE model

AMC CLINICAL EXAM CONTEXT:
- 15-mark rubric validation (5 categories × 3 marks)
- 8-minute station duration
- Australian medical standards enforcement
"""

from pydantic import BaseModel, Field, validator, field_validator, HttpUrl
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
import re
import html

from src.schemas.mcq import MedicalSpecialty  # Reuse specialty enum
from src.db.models import (
    OSCEType,
)  # Import database enum (6 values: history_taking, physical_examination, counselling, communication, diagnosis_management, emergency_scenario)


# ============================================================================
# VIDEO RESOURCE SCHEMAS
# ============================================================================


class VideoResource(BaseModel):
    """Individual video resource for OSCE demonstration"""

    title: str = Field(..., min_length=5, max_length=200, description="Video title")
    url: str = Field(..., description="Video URL (must be HTTPS)")
    source: str = Field(..., min_length=3, max_length=100, description="Source institution")
    duration_minutes: Optional[int] = Field(None, ge=1, le=60, description="Video duration in minutes")
    focus: str = Field(..., min_length=10, max_length=500, description="What the video demonstrates")
    why_recommended: str = Field(..., min_length=10, max_length=500, description="Why this video is recommended")
    australian_relevance: Optional[str] = Field(None, max_length=500, description="Australian AMC relevance notes")

    @field_validator('url')
    @classmethod
    def validate_https(cls, v: str) -> str:
        """Ensure all video URLs are HTTPS (security)"""
        if not v.startswith('https://'):
            raise ValueError("Video URLs must use HTTPS")
        return v

    @field_validator('source')
    @classmethod
    def validate_trusted_source(cls, v: str) -> str:
        """Validate video is from trusted medical education source"""
        trusted_sources = [
            'stanford medicine',
            'geeky medics',
            'oxford medical education',
            'university of calgary',
            'racp',
            'racs',
            'monash',
            'melbourne',
            'unsw',
            'sydney'
        ]
        if not any(source in v.lower() for source in trusted_sources):
            raise ValueError(
                f"Video source must be from trusted medical education institution. "
                f"Got: {v}. Expected one of: {', '.join(trusted_sources)}"
            )
        return v


class VideoResources(BaseModel):
    """Collection of video resources for an OSCE"""

    essential_videos: List[VideoResource] = Field(
        default_factory=list,
        description="Essential videos to watch first (max 4)",
        max_length=4
    )
    supplementary_videos: List[VideoResource] = Field(
        default_factory=list,
        description="Optional supplementary videos (max 3)",
        max_length=3
    )


# ============================================================================
# REQUEST SCHEMAS (Input)
# ============================================================================


class OSCECreate(BaseModel):
    """Schema for creating new OSCE"""

    osce_id: str = Field(..., pattern=r"^OSCE-[A-Z]+-\d{3}$")
    station_title: str = Field(..., min_length=10, max_length=255)
    station_type: OSCEType
    patient_instructions: str = Field(..., min_length=100, max_length=5000)
    candidate_instructions: str = Field(..., min_length=100, max_length=5000)
    examiner_instructions: Optional[str] = Field(None, max_length=5000)
    rubric: Dict[str, Any] = Field(..., description="15-mark AMC format rubric")
    specialty: MedicalSpecialty
    time_limit_minutes: int = Field(default=8, ge=5, le=15)
    learning_objectives: Optional[List[str]] = None
    red_flags: Optional[List[str]] = None
    australian_guidelines: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    video_resources: Optional[VideoResources] = Field(None, description="Video demonstration resources")

    @validator("rubric")
    def validate_rubric(cls, v):
        """
        Validate rubric is 15-mark AMC format.

        Expected structure:
        {
            "history_examination": {"marks": 3, "criteria": "...", "0": "...", "1": "...", "2": "...", "3": "..."},
            "clinical_reasoning": {"marks": 3, ...},
            "communication": {"marks": 3, ...},
            "safety": {"marks": 3, ...},
            "professionalism": {"marks": 3, ...}
        }
        """
        if not isinstance(v, dict):
            raise ValueError("Rubric must be a dictionary")

        required_categories = [
            "history_examination",
            "clinical_reasoning",
            "communication",
            "safety",
            "professionalism",
        ]

        # Check all required categories present
        for category in required_categories:
            if category not in v:
                raise ValueError(f"Rubric missing required category: {category}")

        # Validate each category
        total_marks = 0
        for category_name, category_data in v.items():
            if not isinstance(category_data, dict):
                raise ValueError(f"Category {category_name} must be a dictionary")

            # Check marks field
            if "marks" not in category_data:
                raise ValueError(f'Category {category_name} missing "marks" field')

            marks = category_data["marks"]
            if not isinstance(marks, int) or marks < 0 or marks > 3:
                raise ValueError(f"Category {category_name} marks must be 0-3")

            total_marks += marks

            # Check criteria field
            if "criteria" not in category_data:
                raise ValueError(f'Category {category_name} missing "criteria" field')

            # Check mark descriptors (0, 1, 2, 3)
            for mark_level in ["0", "1", "2", "3"]:
                if mark_level not in category_data:
                    raise ValueError(
                        f"Category {category_name} missing descriptor for mark level {mark_level}"
                    )

        # Total must be 15 marks
        if total_marks != 15:
            raise ValueError(f"Rubric must total 15 marks (AMC format), got {total_marks} marks")

        return v

    @validator("australian_guidelines")
    def validate_australian_guidelines(cls, v):
        """Validate Australian guideline references"""
        if v is None:
            return v

        australian_sources = [
            "therapeutic guidelines",
            "etg",
            "ahpra",
            "amh",
            "pbs",
            "ranzcp",
            "racgp",
            "talley",
            "murtagh",
            "amc",
        ]

        all_text = " ".join(str(val) for val in v.values()).lower()
        if not any(source in all_text for source in australian_sources):
            raise ValueError(
                "Guidelines must reference Australian sources "
                "(eTG, AHPRA, AMH, PBS, RANZCP, RACGP, etc.)"
            )

        return v


class OSCEUpdate(BaseModel):
    """Schema for updating existing OSCE"""

    station_title: Optional[str] = Field(None, min_length=10, max_length=255)
    station_type: Optional[OSCEType] = None
    patient_instructions: Optional[str] = Field(None, min_length=100, max_length=5000)
    candidate_instructions: Optional[str] = Field(None, min_length=100, max_length=5000)
    examiner_instructions: Optional[str] = Field(None, max_length=5000)
    rubric: Optional[Dict[str, Any]] = None
    specialty: Optional[MedicalSpecialty] = None
    time_limit_minutes: Optional[int] = Field(None, ge=5, le=15)
    learning_objectives: Optional[List[str]] = None
    red_flags: Optional[List[str]] = None
    australian_guidelines: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    video_resources: Optional[VideoResources] = None
    is_published: Optional[bool] = None


# ============================================================================
# RESPONSE SCHEMAS (Output)
# ============================================================================


class OSCEBase(BaseModel):
    """Base OSCE schema"""

    id: int
    osce_id: str
    station_title: str
    station_type: OSCEType
    specialty: MedicalSpecialty
    time_limit_minutes: int
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


class OSCEPublic(OSCEBase):
    """Public OSCE (without rubric for practice)"""

    patient_instructions: str
    candidate_instructions: str
    learning_objectives: Optional[List[str]]
    red_flags: Optional[List[str]]
    video_resources: Optional[VideoResources]


class OSCEWithRubric(OSCEPublic):
    """OSCE with complete rubric (for review after practice)"""

    examiner_instructions: Optional[str]
    rubric: Dict[str, Any]
    australian_guidelines: Optional[Dict[str, str]]


# ============================================================================
# OSCE ATTEMPT SCHEMAS
# ============================================================================


class OSCEAttemptCreate(BaseModel):
    """Schema for submitting OSCE station completion"""

    osce_id: int
    scores: Dict[str, int] = Field(..., description="Category scores (5 categories, 0-3 marks each)")
    time_taken_seconds: int = Field(..., ge=1, le=900)  # 1-900 seconds (15 minutes max)
    self_reflection: Optional[str] = Field(None, max_length=2000)

    @validator("scores")
    def validate_scores(cls, v):
        """Validate scores follow AMC 15-mark format"""
        required_categories = [
            "history_examination",
            "clinical_reasoning",
            "communication",
            "safety",
            "professionalism",
        ]

        # Check all required categories present
        for category in required_categories:
            if category not in v:
                raise ValueError(f"Missing required category: {category}")

        # Validate each score is 0-3
        for category, score in v.items():
            if not isinstance(score, int) or score < 0 or score > 3:
                raise ValueError(f"Score for {category} must be 0-3, got {score}")

        return v


class OSCEAttemptResponse(BaseModel):
    """Response after submitting OSCE attempt"""

    id: int
    total_score: int
    passed: bool
    scores: Dict[str, int]
    time_taken_seconds: int
    attempt_number: int
    areas_for_improvement: Optional[List[str]]
    rubric: Dict[str, Any]  # Include rubric for comparison
    examiner_instructions: Optional[str]

    class Config:
        from_attributes = True


# ============================================================================
# SECURITY INPUT VALIDATION SCHEMAS (Added for PRD 2 - Security Hardening)
# ============================================================================


class SpecialtyEnum(str, Enum):
    """AMC specialties - prevents SQL injection via specialty parameter"""
    CARDIOLOGY = "cardiology"
    RESPIRATORY = "respiratory"
    GASTROENTEROLOGY = "gastroenterology"
    NEUROLOGY = "neurology"
    ENDOCRINOLOGY = "endocrinology"
    PSYCHIATRY = "psychiatry"
    SURGERY = "surgery"
    OBGYN = "obgyn"
    PAEDIATRICS = "paediatrics"


class DifficultyEnum(str, Enum):
    """Difficulty levels - prevents injection"""
    FOUNDATION = "foundation"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class SessionTypeEnum(str, Enum):
    """Session types - prevents injection"""
    INDIVIDUAL = "individual"
    MOCK_EXAM = "mock_exam"


class OSCESessionCreate(BaseModel):
    """Request schema for creating OSCE session - WITH INPUT VALIDATION"""
    persona_id: str = Field(
        ...,
        pattern=r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        description="UUID of patient persona (validates UUID format, prevents SQL injection)"
    )
    session_type: SessionTypeEnum = Field(
        ...,
        description="Session type (Enum prevents injection)"
    )

    @field_validator('persona_id')
    @classmethod
    def validate_persona_id(cls, v: str) -> str:
        """Extra validation: UUID format only"""
        # Pydantic pattern already validates, this is defense in depth
        if not re.match(r'^[0-9a-f-]+$', v):
            raise ValueError("Invalid persona_id format")
        return v


class StudentMessage(BaseModel):
    """Student message via WebSocket - WITH XSS PROTECTION"""
    message: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Student's message (max 1000 chars, XSS sanitized)"
    )

    @field_validator('message')
    @classmethod
    def sanitize_message(cls, v: str) -> str:
        """
        Sanitize message to prevent XSS if displayed in web UI.

        Note: This is defense in depth. Frontend should also sanitize.
        """
        # HTML escape to prevent XSS
        sanitized = html.escape(v)

        # Remove any script tags (shouldn't exist after escape, but paranoid)
        sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.DOTALL | re.IGNORECASE)

        return sanitized
