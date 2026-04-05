"""
Pydantic schemas for EMR Practice System API

SECURITY:
- All PHI fields properly validated
- No hardcoded credentials
- HIPAA-compliant field validation

AUSTRALIAN MEDICAL CONTEXT:
- PBS codes for medications
- MBS codes for pathology
- Australian terminology (paracetamol NOT acetaminophen)

API CONTRACT:
- Backend uses snake_case (Python convention)
- Frontend expects camelCase (JavaScript convention)
- Pydantic aliases handle automatic conversion
- populate_by_name = True (accepts both formats)
"""

from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator, ConfigDict
from uuid import UUID


# ============================================================================
# SESSION MANAGEMENT SCHEMAS
# ============================================================================

class PatientFilter(BaseModel):
    """Filter criteria for patient selection"""
    specialty: Optional[str] = None
    complexity: Optional[Literal["Simple", "Moderate", "Complex"]] = None
    exclude_completed: bool = True

    model_config = ConfigDict(populate_by_name=True)


class SessionStartRequest(BaseModel):
    """Request to start new EMR practice session"""
    emr_system: Literal["cerner", "epic"] = Field(..., alias="emrSystem")
    patient_filter: Optional[PatientFilter] = Field(None, alias="patientFilter")
    osce_id: Optional[str] = Field(None, alias="osceId")

    model_config = ConfigDict(populate_by_name=True)


class MockPatientResponse(BaseModel):
    """Patient scenario data (camelCase for frontend)"""
    id: str
    mrn: str
    full_name: str = Field(..., alias="fullName")
    age: int
    gender: str
    allergies: List[str]
    current_medications: List[Dict[str, Any]] = Field(..., alias="currentMedications")
    vital_signs: Dict[str, Any] = Field(..., alias="vitalSigns")
    presenting_complaint: str = Field(..., alias="presentingComplaint")
    clinical_scenario: str = Field(..., alias="clinicalScenario")
    specialty: str
    complexity_level: str = Field(..., alias="complexityLevel")
    demographics: Dict[str, Any]
    medical_history: Optional[Dict[str, Any]] = Field(None, alias="medicalHistory")
    medications: Optional[List[Dict[str, Any]]] = None
    physical_exam_findings: Optional[Dict[str, Any]] = Field(None, alias="physicalExamFindings")
    investigation_results: Optional[Dict[str, Any]] = Field(None, alias="investigationResults")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class SessionStartResponse(BaseModel):
    """Response after starting EMR session"""
    session_id: str = Field(..., alias="sessionId")
    patient: MockPatientResponse
    emr_system: str = Field(..., alias="emrSystem")
    started_at: datetime = Field(..., alias="startedAt")
    session_data: Dict[str, Any] = Field(default_factory=dict, alias="sessionData")

    model_config = ConfigDict(populate_by_name=True)


class SessionUpdateRequest(BaseModel):
    """Request to update session (auto-save)"""
    session_data: Dict[str, Any] = Field(..., alias="sessionData")

    model_config = ConfigDict(populate_by_name=True)


class SessionUpdateResponse(BaseModel):
    """Response after auto-save"""
    session_id: str = Field(..., alias="sessionId")
    auto_saved_at: datetime = Field(..., alias="autoSavedAt")
    message: str = "Draft saved successfully"

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# SUBMISSION SCHEMAS
# ============================================================================

class SOAPNoteSubmit(BaseModel):
    """SOAP note submission data"""
    subjective: str = Field(..., min_length=50)
    objective: str = Field(..., min_length=30)
    assessment: str = Field(..., min_length=30)
    plan: str = Field(..., min_length=30)
    note_type: str = Field(default="Progress Note", alias="noteType")

    model_config = ConfigDict(populate_by_name=True)

    @validator('subjective', 'objective', 'assessment', 'plan')
    def check_not_placeholder(cls, v):
        """Prevent placeholder content"""
        placeholders = ['lorem ipsum', 'placeholder', 'example text', 'sample']
        if any(p in v.lower() for p in placeholders):
            raise ValueError('Content contains placeholder text')
        return v


class PrescriptionSubmit(BaseModel):
    """PBS-compliant prescription submission"""
    medication_name: str = Field(..., alias="medicationName")
    dose: str
    frequency: str
    route: str
    quantity: int
    repeats: int = Field(..., ge=0, le=5)  # Max 5 repeats per PBS
    indication: str = Field(..., min_length=5)

    model_config = ConfigDict(populate_by_name=True)

    @validator('medication_name')
    def check_australian_terminology(cls, v):
        """Enforce Australian drug names"""
        american_drugs = {
            'acetaminophen': 'paracetamol',
            'albuterol': 'salbutamol',
            'epinephrine': 'adrenaline'
        }
        for american, australian in american_drugs.items():
            if american in v.lower():
                raise ValueError(f'Use Australian terminology: {australian} not {american}')
        return v


class PathologyOrderSubmit(BaseModel):
    """MBS-compliant pathology order submission"""
    test_name: str = Field(..., alias="testName")
    urgency: Literal["Routine", "Urgent", "Emergency"]
    clinical_indication: str = Field(..., min_length=10, alias="clinicalIndication")
    is_panel: bool = Field(default=False, alias="isPanel")
    panel_tests: List[str] = Field(default_factory=list, alias="panelTests")

    model_config = ConfigDict(populate_by_name=True)


class SessionSubmitRequest(BaseModel):
    """Complete session submission"""
    soap_note: SOAPNoteSubmit = Field(..., alias="soapNote")
    prescriptions: List[PrescriptionSubmit] = Field(default_factory=list)
    pathology_orders: List[PathologyOrderSubmit] = Field(default_factory=list, alias="pathologyOrders")
    completion_time_seconds: int = Field(..., alias="completionTimeSeconds")
    typing_wpm: Optional[int] = Field(None, alias="typingWpm")

    model_config = ConfigDict(populate_by_name=True)


class SessionSubmitResponse(BaseModel):
    """Response after session submission"""
    session_id: str = Field(..., alias="sessionId")
    completed_at: datetime = Field(..., alias="completedAt")
    soap_note_id: str = Field(..., alias="soapNoteId")
    prescription_ids: List[str] = Field(..., alias="prescriptionIds")
    pathology_order_ids: List[str] = Field(..., alias="pathologyOrderIds")
    validation_queued: bool = Field(default=True, alias="validationQueued")
    validation_status: str = Field(default="pending", alias="validationStatus")

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# RETRIEVAL SCHEMAS
# ============================================================================

class SOAPNoteResponse(BaseModel):
    """SOAP note response data"""
    id: str
    subjective: str
    objective: str
    assessment: str
    plan: str
    note_type: str = Field(..., alias="noteType")
    typing_wpm: Optional[int] = Field(None, alias="typingWpm")
    completion_time_seconds: Optional[int] = Field(None, alias="completionTimeSeconds")
    overall_validation_score: Optional[float] = Field(None, alias="overallValidationScore")
    ahpra_compliant: bool = Field(..., alias="ahpraCompliant")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PrescriptionResponse(BaseModel):
    """Prescription response data"""
    id: str
    medication_name: str = Field(..., alias="medicationName")
    dose: str
    frequency: str
    route: str
    quantity: int
    repeats: int
    indication: str
    validation_score: Optional[float] = Field(None, alias="validationScore")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class PathologyOrderResponse(BaseModel):
    """Pathology order response data"""
    id: str
    test_name: str = Field(..., alias="testName")
    urgency: str
    clinical_indication: str = Field(..., alias="clinicalIndication")
    validation_score: Optional[float] = Field(None, alias="validationScore")

    model_config = ConfigDict(populate_by_name=True, from_attributes=True)


class SessionDetailResponse(BaseModel):
    """Detailed session information"""
    session_id: str = Field(..., alias="sessionId")
    user_id: int = Field(..., alias="userId")
    patient: MockPatientResponse
    emr_system: str = Field(..., alias="emrSystem")
    is_active: bool = Field(..., alias="isActive")
    started_at: datetime = Field(..., alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    auto_saved_at: Optional[datetime] = Field(None, alias="autoSavedAt")
    session_data: Dict[str, Any] = Field(..., alias="sessionData")

    # Only if completed
    soap_note: Optional[SOAPNoteResponse] = Field(None, alias="soapNote")
    prescriptions: List[PrescriptionResponse] = Field(default_factory=list)
    pathology_orders: List[PathologyOrderResponse] = Field(default_factory=list, alias="pathologyOrders")

    model_config = ConfigDict(populate_by_name=True)


class SessionSummary(BaseModel):
    """Session summary for list view"""
    session_id: str = Field(..., alias="sessionId")
    patient_name: str = Field(..., alias="patientName")
    patient_specialty: str = Field(..., alias="patientSpecialty")
    emr_system: str = Field(..., alias="emrSystem")
    is_active: bool = Field(..., alias="isActive")
    started_at: datetime = Field(..., alias="startedAt")
    completed_at: Optional[datetime] = Field(None, alias="completedAt")
    validation_score: Optional[float] = Field(None, alias="validationScore")

    model_config = ConfigDict(populate_by_name=True)


class SessionListResponse(BaseModel):
    """Paginated session list"""
    sessions: List[SessionSummary]
    total_count: int = Field(..., alias="totalCount")
    limit: int
    offset: int

    model_config = ConfigDict(populate_by_name=True)


# ============================================================================
# VALIDATION SCHEMAS
# ============================================================================

class ValidationRequest(BaseModel):
    """Request for SOAP note validation"""
    soap_note_id: str = Field(..., alias="soapNoteId")
    validation_layer: Literal[1, 2, 3] = Field(..., alias="validationLayer")

    model_config = ConfigDict(populate_by_name=True)


class ValidationResponse(BaseModel):
    """Validation result"""
    validation_id: str = Field(..., alias="validationId")
    validation_layer: int = Field(..., alias="validationLayer")
    score: float
    passed: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    detailed_feedback: Optional[Dict[str, Any]] = Field(None, alias="detailedFeedback")
    australian_compliant: bool = Field(..., alias="australianCompliant")

    model_config = ConfigDict(populate_by_name=True)
