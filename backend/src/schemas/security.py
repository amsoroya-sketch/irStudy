"""
Security Input Validation Schemas (PRD 2 - Step 7)

Prevents XSS, SQL injection via Enum validation and input sanitization.
Independent of database models to avoid import dependencies in tests.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum
import re
import html


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
