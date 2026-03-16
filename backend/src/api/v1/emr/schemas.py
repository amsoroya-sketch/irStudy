"""
Pydantic schemas for EMR API request/response validation

AUSTRALIAN MEDICAL CONTEXT:
- All schemas enforce Australian terminology and standards
- Validation ensures compliance with PBS, MBS, eTG
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Literal
from datetime import datetime


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class CreateSessionRequest(BaseModel):
    """Request schema for creating new EMR session"""

    mock_patient_id: UUID4 = Field(..., description="UUID of mock patient to practice with")
    emr_system: Literal["epic", "cerner"] = Field(
        default="epic", description="EMR system theme (epic or cerner)"
    )
    session_type: Literal["practice", "assessment"] = Field(
        default="practice", description="Session type (practice or assessment)"
    )


class SOAPNoteSubmit(BaseModel):
    """SOAP note content for submission"""

    subjective: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Subjective: Patient's reported symptoms and history",
    )
    objective: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Objective: Physical examination findings and vital signs",
    )
    assessment: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Assessment: Differential diagnosis and clinical reasoning",
    )
    plan: str = Field(
        ...,
        min_length=50,
        max_length=5000,
        description="Plan: Management plan and follow-up",
    )


class PrescriptionSubmit(BaseModel):
    """Prescription submission (PBS-compliant)"""

    medication: str = Field(..., description="Medication name (Australian approved name)")
    dose: str = Field(..., description="Dose (e.g., '500mg')")
    route: str = Field(..., description="Route of administration (e.g., 'PO', 'IV')")
    frequency: str = Field(..., description="Frequency (e.g., 'BD', 'TDS', 'stat')")


class PathologyOrderSubmit(BaseModel):
    """Pathology order submission (MBS-compliant)"""

    test_name: str = Field(..., description="Test name (e.g., 'Troponin I', 'FBC')")
    urgency: Literal["routine", "urgent", "stat"] = Field(
        default="routine", description="Urgency level"
    )
    clinical_notes: str = Field(..., description="Clinical indication for test")


class SubmitSessionRequest(BaseModel):
    """Complete session submission with SOAP note, prescriptions, and pathology"""

    soap_note: SOAPNoteSubmit
    prescriptions: List[PrescriptionSubmit] = Field(default_factory=list)
    pathology_orders: List[PathologyOrderSubmit] = Field(default_factory=list)


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class MockPatientResponse(BaseModel):
    """Mock patient demographic and clinical information"""

    id: UUID4 = Field(..., alias="patient_id", description="Patient UUID")
    name: str = Field(..., description="Patient name")
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    presenting_complaint: str = Field(..., description="Chief complaint")
    vital_signs: Optional[dict] = Field(None, description="Vital signs")
    medical_history: Optional[dict] = Field(None, description="Medical history")

    class Config:
        populate_by_name = True
        from_attributes = True


class ValidationLayerResult(BaseModel):
    """Individual validation layer result"""

    score: float = Field(..., description="Layer score (0-100)")
    feedback: Optional[str] = Field(None, description="Layer-specific feedback")
    errors: List[str] = Field(default_factory=list, description="Validation errors")


class ValidationResult(BaseModel):
    """3-layer validation result"""

    overall_score: float = Field(..., description="Overall score (0-100)")
    layer_1_rule_based: ValidationLayerResult = Field(
        ..., description="Layer 1: Rule-based validation"
    )
    layer_2_claude_ai: Optional[ValidationLayerResult] = Field(
        None, description="Layer 2: Claude AI validation (60% of time)"
    )
    layer_3_specialist: Optional[ValidationLayerResult] = Field(
        None, description="Layer 3: Specialist review (flagged cases only)"
    )
    pass_fail: Literal["PASS", "BORDERLINE", "FAIL"] = Field(..., description="Pass/fail status")
    time_taken_seconds: int = Field(..., description="Time taken to complete session")


class SessionResponse(BaseModel):
    """EMR session response"""

    session_id: UUID4 = Field(..., description="Session UUID")
    mock_patient: MockPatientResponse = Field(..., description="Patient information")
    emr_system: str = Field(..., description="EMR system theme")
    started_at: datetime = Field(..., description="Session start timestamp")
    submitted_at: Optional[datetime] = Field(None, description="Session submission timestamp")
    status: Literal["in_progress", "submitted", "validated"] = Field(
        ..., description="Session status"
    )
    soap_note: Optional[dict] = Field(None, description="SOAP note content (if submitted)")
    validation_result: Optional[ValidationResult] = Field(
        None, description="Validation result (if validated)"
    )

    class Config:
        from_attributes = True


class SubmitSessionResponse(BaseModel):
    """Session submission response"""

    session_id: UUID4 = Field(..., description="Session UUID")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    validation_result: ValidationResult = Field(..., description="Validation result")


# ============================================================================
# DASHBOARD SCHEMAS
# ============================================================================


class OverallProgressResponse(BaseModel):
    """Overall EMR progress statistics"""

    total_sessions: int = Field(..., description="Total sessions completed")
    sessions_passed: int = Field(..., description="Sessions passed (≥70 score)")
    sessions_failed: int = Field(..., description="Sessions failed (<60 score)")
    sessions_in_progress: int = Field(..., description="Sessions in progress")
    average_score: float = Field(..., description="Average score across all sessions")
    total_time_minutes: float = Field(..., description="Total study time in minutes")
    improvement_trend: float = Field(
        ..., description="Improvement trend (% change over last 10 sessions)"
    )
    current_streak: int = Field(..., description="Current streak of passing sessions")
    last_session_date: Optional[datetime] = Field(None, description="Last session date")


class RecommendedPracticeScenario(BaseModel):
    """Recommended practice scenario"""

    patient_id: UUID4 = Field(..., description="Mock patient UUID")
    scenario_name: str = Field(..., description="Scenario name")
    difficulty: str = Field(..., description="Difficulty level")


class SpecialtyDetailResponse(BaseModel):
    """Specialty-specific progress breakdown"""

    specialty: str = Field(..., description="Medical specialty")
    sessions_attempted: int = Field(..., description="Sessions attempted in specialty")
    sessions_passed: int = Field(..., description="Sessions passed in specialty")
    average_score: float = Field(..., description="Average score in specialty")
    weak_areas: List[str] = Field(default_factory=list, description="Weak areas identified")
    strong_areas: List[str] = Field(default_factory=list, description="Strong areas identified")
    recommended_practice: List[RecommendedPracticeScenario] = Field(
        default_factory=list, description="Recommended practice scenarios"
    )


class SessionHistoryItem(BaseModel):
    """Individual session history item"""

    session_id: UUID4 = Field(..., description="Session UUID")
    mock_patient_name: str = Field(..., description="Patient name")
    specialty: str = Field(..., description="Medical specialty")
    chief_complaint: str = Field(..., description="Chief complaint")
    submitted_at: Optional[datetime] = Field(None, description="Submission timestamp")
    score: Optional[float] = Field(None, description="Overall score")
    pass_fail: Optional[str] = Field(None, description="Pass/fail status")
    time_taken_minutes: Optional[float] = Field(None, description="Time taken in minutes")

    class Config:
        from_attributes = True


class PaginationInfo(BaseModel):
    """Pagination metadata"""

    limit: int = Field(..., description="Items per page")
    offset: int = Field(..., description="Offset from start")
    has_more: bool = Field(..., description="Whether more items available")


class SessionHistoryResponse(BaseModel):
    """Session history response with pagination"""

    total_count: int = Field(..., description="Total sessions matching filter")
    sessions: List[SessionHistoryItem] = Field(..., description="Session history items")
    pagination: PaginationInfo = Field(..., description="Pagination metadata")
