"""
Pydantic schemas for EMR API request/response validation

AUSTRALIAN MEDICAL CONTEXT:
- All schemas enforce Australian terminology and standards
- Validation ensures compliance with PBS, MBS, eTG
"""

from pydantic import BaseModel, Field, UUID4
from typing import Optional, List, Literal, Any
from datetime import datetime


# ============================================================================
# REQUEST SCHEMAS
# ============================================================================


class StartSessionRequest(BaseModel):
    """Request schema for starting new EMR session"""

    specialty: Optional[str] = Field(
        None, description="Medical specialty filter for patient selection"
    )
    difficulty: Optional[str] = Field(
        None, description="Difficulty level filter for patient selection"
    )
    patient_id: Optional[UUID4] = Field(
        None, description="Specific patient ID (overrides specialty/difficulty filters)"
    )


class CreateSessionRequest(BaseModel):
    """Request schema for creating new EMR session"""

    mock_patient_id: UUID4 = Field(..., description="UUID of mock patient to practice with")
    emr_system: Literal["epic", "cerner"] = Field(
        default="epic", description="EMR system theme (epic or cerner)"
    )
    session_type: Literal["practice", "assessment"] = Field(
        default="practice", description="Session type (practice or assessment)"
    )


class UpdateSessionRequest(BaseModel):
    """Request schema for updating session (auto-save)"""

    soap_note: Optional[dict] = Field(None, description="SOAP note content for auto-save")
    elapsed_time_seconds: Optional[int] = Field(0, description="Elapsed time in seconds since session start")


class SOAPNoteSubmit(BaseModel):
    """SOAP note content for submission"""

    subjective: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Subjective: Patient's reported symptoms and history",
    )
    objective: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Objective: Physical examination findings and vital signs",
    )
    assessment: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Assessment: Differential diagnosis and clinical reasoning",
    )
    plan: str = Field(
        ...,
        min_length=1,
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

    final_soap_note: Optional[dict] = Field(None, description="Final SOAP note content")
    soap_note: Optional[dict] = Field(None, description="SOAP note content (alternative field name)")
    prescriptions: List[PrescriptionSubmit] = Field(default_factory=list)
    pathology_orders: List[PathologyOrderSubmit] = Field(default_factory=list)
    typing_metrics: Optional[dict] = Field(None, description="Typing metrics (WPM, accuracy, etc.)")
    
    def model_post_init(self, __context):
        """Ensure either final_soap_note or soap_note is provided"""
        if not self.final_soap_note and not self.soap_note:
            raise ValueError("Either final_soap_note or soap_note must be provided")
        # Use soap_note as final_soap_note if not provided
        if not self.final_soap_note and self.soap_note:
            self.final_soap_note = self.soap_note


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================


class MockPatientResponse(BaseModel):
    """Mock patient demographic and clinical information"""

    id: UUID4 = Field(..., description="Patient UUID")
    name: str = Field(..., description="Patient name")
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    presenting_complaint: str = Field(..., description="Chief complaint")
    specialty: str = Field(..., description="Medical specialty")
    vital_signs: Optional[dict] = Field(None, description="Vital signs")
    medical_history: Optional[Any] = Field(None, description="Medical history (list or dict)")

    class Config:
        populate_by_name = True
        from_attributes = True


class ValidationLayerResult(BaseModel):
    """Individual validation layer result"""

    passed: bool = Field(..., description="Whether this layer passed validation")
    score: Optional[float] = Field(None, description="Layer score (0-100)")
    feedback: Optional[str] = Field(None, description="Layer-specific feedback")
    errors: List[str] = Field(default_factory=list, description="Validation errors")


class ValidationResult(BaseModel):
    """3-layer validation result"""

    overall_score: float = Field(..., description="Overall score (0-15 AMC rubric)")
    pass_fail: Optional[bool] = Field(
        None,
        description=(
            "Authoritative PASS/FAIL decision (from decide_pass_fail). "
            "None when the AI layer was unavailable and the note was not graded."
        ),
    )
    category_scores: Optional[dict] = Field(None, description="Score breakdown by category")
    completeness: Optional[dict] = Field(
        None, description="Per-section (S/O/A/P) completeness percentage (0-100)"
    )
    captured: List[str] = Field(
        default_factory=list, description="Answer-key elements the student documented"
    )
    missing_elements: List[str] = Field(
        default_factory=list, description="Answer-key elements the student omitted"
    )
    strengths: List[str] = Field(default_factory=list, description="Identified strengths")
    improvements: List[str] = Field(default_factory=list, description="Areas for improvement")
    red_flags: List[str] = Field(default_factory=list, description="Critical safety issues")
    australian_compliance: Optional[dict] = Field(None, description="Australian medical compliance check")
    ai_unavailable: Optional[bool] = Field(
        None,
        description=(
            "True when the Claude AI assessment layer was temporarily unavailable "
            "(missing Vault key or API error). When True the submission is NOT graded "
            "and the student may re-submit to re-run the assessment."
        ),
    )
    layer_1_zod: ValidationLayerResult = Field(
        ..., description="Layer 1: Zod/Pydantic validation"
    )
    layer_2_python: ValidationLayerResult = Field(
        ..., description="Layer 2: Python business logic validation"
    )
    layer_3_ai: Optional[ValidationLayerResult] = Field(
        None, description="Layer 3: Claude AI clinical reasoning validation"
    )
    performance_summary: Optional[dict] = Field(None, description="Performance summary")
    next_steps: Optional[dict] = Field(None, description="Recommended next steps")


class SessionResponse(BaseModel):
    """EMR session response"""

    session_id: UUID4 = Field(..., description="Session UUID")
    validation_id: Optional[UUID4] = Field(None, description="Validation ID (same as session_id for compatibility)")
    patient: MockPatientResponse = Field(..., description="Patient information")
    specialty: str = Field(..., description="Medical specialty")
    difficulty: str = Field(..., description="Difficulty level")
    started_at: datetime = Field(..., description="Session start timestamp")
    submitted_at: Optional[datetime] = Field(None, description="Session submission timestamp")
    elapsed_time_seconds: int = Field(default=0, description="Elapsed time in seconds")
    status: Literal["in_progress", "graded"] = Field(..., description="Session status")
    auto_save_count: int = Field(default=0, description="Number of auto-saves performed")
    last_auto_save_at: Optional[datetime] = Field(None, description="Last auto-save timestamp")
    validation_score: Optional[float] = Field(None, description="Validation score (0-15)")
    total_amc_score: Optional[float] = Field(None, description="Total AMC score (alias for validation_score)")
    validation_results: Optional[ValidationResult] = Field(
        None, description="Validation results (if graded)"
    )
    soap_note: Optional[dict] = Field(None, description="SOAP note content")
    typing_metrics: Optional[dict] = Field(None, description="Typing metrics")
    performance_summary: Optional[dict] = Field(None, description="Performance summary")
    next_steps: Optional[dict] = Field(None, description="Recommended next steps")
    message: Optional[str] = Field(None, description="Response message")

    class Config:
        from_attributes = True


class SubmitSessionResponse(BaseModel):
    """Session submission response"""

    session_id: UUID4 = Field(..., description="Session UUID")
    submitted_at: datetime = Field(..., description="Submission timestamp")
    validation_result: ValidationResult = Field(..., description="Validation result")


# ============================================================================
# CASE CATALOG SCHEMAS (Phase 1a - "pick a case and practice" picker)
# ============================================================================


class EMRCaseListItem(BaseModel):
    """
    A single selectable EMR practice case for the picker.

    NOTE: Intentionally does NOT expose ``validation_criteria`` (the per-case
    answer key) — that must never leak to the client.
    """

    id: UUID4 = Field(..., description="Mock-patient UUID (use as patient_id to start a session)")
    mrn: str = Field(..., description="Medical record number (stable case identifier)")
    name: str = Field(..., description="Patient name")
    age: int = Field(..., description="Patient age")
    gender: str = Field(..., description="Patient gender")
    presenting_complaint: str = Field(..., description="Chief complaint")
    specialty: str = Field(..., description="Medical specialty")
    difficulty: str = Field(..., description="Difficulty level (easy, medium, hard)")

    class Config:
        from_attributes = True


class EMRCaseListResponse(BaseModel):
    """Response for the EMR case catalog."""

    total: int = Field(..., description="Total number of cases matching the filters")
    cases: List[EMRCaseListItem] = Field(..., description="Selectable practice cases")


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
