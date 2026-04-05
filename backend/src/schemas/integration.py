"""
Pydantic schemas for OSCE-to-EMR Integration

CROSS-SYSTEM INTEGRATION:
- Links AI OSCE system with EMR Practice system
- Enables automatic SOAP note pre-filling from OSCE transcripts
- Tracks pedagogical learning transfer metrics

AUSTRALIAN MEDICAL CONTEXT:
- Ensures Australian terminology in converted SOAP notes
- Validates PBS/MBS compliance
- Enforces eTG/AMH guideline adherence
"""

from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import UUID


# ============================================================================
# CONVERSION REQUEST/RESPONSE SCHEMAS
# ============================================================================

class ConversionRequest(BaseModel):
    """Request to convert OSCE attempt to EMR session"""

    osce_attempt_id: UUID = Field(
        ...,
        alias="osceAttemptId",
        description="UUID of completed OSCE attempt to convert"
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator('osce_attempt_id')
    @classmethod
    def validate_uuid_format(cls, v: UUID) -> UUID:
        """Ensure valid UUID format"""
        if not v:
            raise ValueError("osce_attempt_id is required")
        return v


class ConversionMetadata(BaseModel):
    """Metadata about OSCE-to-EMR conversion process"""

    pre_fill_percentage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Percentage of SOAP note fields auto-filled (0.0-1.0)"
    )
    extraction_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Claude API confidence score for extracted data"
    )
    tokens_used: int = Field(
        ...,
        ge=0,
        description="Total Claude API tokens used for conversion"
    )
    api_response_time_ms: int = Field(
        ...,
        ge=0,
        description="Claude API response time in milliseconds"
    )
    conversion_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When conversion was performed"
    )
    missing_elements: List[str] = Field(
        default_factory=list,
        description="List of SOAP elements not extractable from transcript"
    )
    australian_terminology_compliance: bool = Field(
        default=True,
        description="Whether extracted content uses Australian medical terms"
    )

    model_config = ConfigDict(populate_by_name=True)


class SOAPNoteDraft(BaseModel):
    """Auto-generated SOAP note draft from OSCE transcript"""

    subjective: str = Field(
        ...,
        min_length=100,
        max_length=5000,
        description="History from patient (HPI, PMHx, medications, allergies, social history)"
    )
    objective: str = Field(
        ...,
        min_length=50,
        max_length=3000,
        description="Physical examination findings and vital signs"
    )
    assessment: str = Field(
        ...,
        min_length=50,
        max_length=2000,
        description="Differential diagnoses and most likely diagnosis"
    )
    plan: str = Field(
        ...,
        min_length=50,
        max_length=3000,
        description="Investigations, treatment plan, and follow-up"
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator('subjective', 'objective', 'assessment', 'plan')
    @classmethod
    def validate_no_placeholder_text(cls, v: str) -> str:
        """Ensure no placeholder content like [TO BE FILLED] or TODO"""
        forbidden_patterns = [
            'TODO',
            '[TO BE FILLED]',
            '[PLACEHOLDER]',
            'XXXX',
            'N/A - not mentioned',
            'Information not available'
        ]
        for pattern in forbidden_patterns:
            if pattern.lower() in v.lower():
                raise ValueError(f"SOAP note contains placeholder text: {pattern}")
        return v

    @field_validator('plan')
    @classmethod
    def validate_australian_terminology(cls, v: str) -> str:
        """Ensure Australian medical terminology in treatment plan"""
        # Check for common US terms that should be Australian
        us_terms = {
            'acetaminophen': 'paracetamol',
            'albuterol': 'salbutamol',
            '911': '000',
            'ER': 'ED',
            'emergency room': 'emergency department'
        }

        for us_term, au_term in us_terms.items():
            if us_term.lower() in v.lower():
                raise ValueError(
                    f"Use Australian terminology: '{au_term}' instead of '{us_term}'"
                )
        return v


class ConversionResult(BaseModel):
    """Result of OSCE-to-EMR conversion"""

    soap_note_draft: SOAPNoteDraft = Field(
        ...,
        alias="soapNoteDraft",
        description="Auto-generated SOAP note content"
    )
    metadata: ConversionMetadata = Field(
        ...,
        description="Conversion process metadata"
    )

    model_config = ConfigDict(populate_by_name=True)


class ConversionResponse(BaseModel):
    """Response after successful OSCE-to-EMR conversion"""

    emr_session_id: UUID = Field(
        ...,
        alias="emrSessionId",
        description="UUID of created EMR session with pre-filled SOAP note"
    )
    pre_fill_percentage: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        alias="preFillPercentage",
        description="Percentage of SOAP note auto-filled"
    )
    extraction_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        alias="extractionConfidence",
        description="Confidence score for extracted data"
    )
    redirect_url: str = Field(
        ...,
        alias="redirectUrl",
        description="Frontend URL to navigate to EMR session"
    )
    message: str = Field(
        default="OSCE successfully converted to EMR session",
        description="Success message"
    )

    model_config = ConfigDict(populate_by_name=True)


class ConversionError(BaseModel):
    """Error response for failed conversion"""

    error_code: str = Field(
        ...,
        alias="errorCode",
        description="Machine-readable error code"
    )
    error_message: str = Field(
        ...,
        alias="errorMessage",
        description="Human-readable error message"
    )
    osce_attempt_id: UUID = Field(
        ...,
        alias="osceAttemptId",
        description="OSCE attempt ID that failed conversion"
    )
    fallback_action: Optional[str] = Field(
        None,
        alias="fallbackAction",
        description="Suggested fallback action for user"
    )

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# INTERNAL CONVERSION SCHEMAS (Backend-only)
# ============================================================================

class OSCETranscriptExtract(BaseModel):
    """Extracted clinical data from OSCE transcript (internal use)"""

    chief_complaint: str = Field(..., description="Patient's main complaint")
    hpi: str = Field(..., description="History of Presenting Illness")
    associated_symptoms: List[str] = Field(default_factory=list)
    past_medical_history: List[str] = Field(default_factory=list)
    medications: List[str] = Field(default_factory=list)
    allergies: List[str] = Field(default_factory=list)
    social_history: Dict[str, Any] = Field(default_factory=dict)
    family_history: List[str] = Field(default_factory=list)
    vital_signs: Optional[Dict[str, Any]] = None
    physical_exam_findings: Optional[Dict[str, Any]] = None
    provisional_diagnosis: Optional[str] = None
    differential_diagnoses: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)


class ClaudeExtractionResponse(BaseModel):
    """Response from Claude API NLP extraction (internal use)"""

    subjective: str = Field(..., min_length=100)
    objective: str = Field(..., min_length=50)
    assessment: str = Field(..., min_length=50)
    plan: str = Field(..., min_length=50)
    extraction_confidence: float = Field(..., ge=0.0, le=1.0)
    missing_elements: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)
