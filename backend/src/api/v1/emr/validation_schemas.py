"""
EMR Validation API Schemas

Pydantic V2 schemas for 3-layer validation endpoints:
1. SOAP Note Validation
2. Prescription Validation
3. Pathology Order Validation

All schemas use Australian medical standards (eTG, PBS, MBS)
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import List, Dict, Optional
from datetime import datetime


# ============================================================================
# SOAP NOTE VALIDATION
# ============================================================================

class SOAPNoteValidationRequest(BaseModel):
    """Request to validate SOAP note documentation"""

    session_id: str = Field(..., description="EMR session UUID")
    soap_note: Dict[str, str] = Field(
        ...,
        description="SOAP note with subjective, objective, assessment, plan"
    )
    patient_context: Optional[Dict] = Field(
        default=None,
        description="Patient demographics, history, presenting complaint"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "soap_note": {
                    "subjective": "55yo M with sudden onset central chest pain...",
                    "objective": "BP 145/90, HR 98 irregular, bibasal creps...",
                    "assessment": "Acute Coronary Syndrome - Inferior STEMI",
                    "plan": "Aspirin 300mg stat, morphine 5mg IV, oxygen 15L..."
                },
                "patient_context": {
                    "age": 55,
                    "sex": "M",
                    "presenting_complaint": "Chest pain",
                    "specialty": "cardiology"
                }
            }
        }
    )


class ValidationFeedback(BaseModel):
    """Feedback for one AMC rubric category"""

    category: str = Field(..., description="AMC category name")
    score: float = Field(..., ge=0, le=3, description="Score out of 3 marks")
    strengths: List[str] = Field(default_factory=list)
    improvements: List[str] = Field(default_factory=list)
    citations: List[str] = Field(
        default_factory=list,
        description="eTG guideline references"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "category": "clinical_reasoning",
                "score": 2.5,
                "strengths": [
                    "Appropriate differential diagnosis",
                    "Correct STEMI identification"
                ],
                "improvements": [
                    "Could specify troponin timing",
                    "Missing PCI vs thrombolysis decision criteria"
                ],
                "citations": [
                    "eTG Cardiovascular - Acute Coronary Syndromes"
                ]
            }
        }
    )


class AustralianComplianceCheck(BaseModel):
    """Validation of Australian medical standards"""

    terminology_correct: bool = Field(
        ...,
        description="Uses Australian terminology (paracetamol not acetaminophen)"  # SECURITY SCAN EXEMPTION
    )
    etg_compliant: bool = Field(
        ...,
        description="Follows eTG Therapeutic Guidelines"
    )
    pbs_aware: bool = Field(
        ...,
        description="Considers PBS restrictions where applicable"
    )
    issues: List[str] = Field(
        default_factory=list,
        description="Australian compliance issues found"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "terminology_correct": True,
                "etg_compliant": True,
                "pbs_aware": True,
                "issues": []
            }
        }
    )


class SOAPNoteValidationResult(BaseModel):
    """Result of SOAP note validation"""

    validation_type: str = Field(default="soap_note", description="Validation type")
    overall_score: float = Field(..., ge=0, le=15, description="Total AMC score")
    passed: bool = Field(..., description="Score >= 9/15 (60%)")
    category_scores: Dict[str, float] = Field(
        ...,
        description="5 AMC categories with scores"
    )
    strengths: List[str] = Field(default_factory=list, description="Positive feedback")
    improvements: List[str] = Field(default_factory=list, description="Areas to improve")
    red_flags: List[str] = Field(default_factory=list, description="Safety concerns")
    feedback: List[ValidationFeedback] = Field(default_factory=list)
    australian_compliance: AustralianComplianceCheck
    processing_time_ms: int = Field(default=0, description="Validation latency")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_score": 12.5,
                "passed": True,
                "category_scores": {
                    "history_examination": 2.5,
                    "clinical_reasoning": 2.5,
                    "communication": 2.5,
                    "safety": 3.0,
                    "professionalism": 2.0
                },
                "feedback": [
                    {
                        "category": "safety",
                        "score": 3.0,
                        "strengths": ["Immediate recognition of STEMI"],
                        "improvements": [],
                        "citations": ["eTG Cardiovascular"]
                    }
                ],
                "australian_compliance": {
                    "terminology_correct": True,
                    "etg_compliant": True,
                    "pbs_aware": True,
                    "issues": []
                },
                "processing_time_ms": 450
            }
        }
    )


# ============================================================================
# PRESCRIPTION VALIDATION
# ============================================================================

class PrescriptionValidationRequest(BaseModel):
    """Request to validate prescription"""

    medication_name: str = Field(..., description="Medication name")
    dose: str = Field(..., description="Dose (e.g., 100mg)")
    frequency: str = Field(..., description="Frequency (e.g., daily)")
    route: str = Field(..., description="Route (e.g., PO)")
    repeats: int = Field(default=0, description="Number of PBS repeats (max 5)")
    indication: str = Field(..., description="Clinical indication")
    authority_required: bool = Field(default=False, description="PBS authority required")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "medication_name": "Aspirin",
                "dose": "100mg",
                "frequency": "daily",
                "route": "PO",
                "repeats": 5,
                "indication": "Secondary prevention post-STEMI",
                "authority_required": False
            }
        }
    )


class PBSComplianceCheck(BaseModel):
    """PBS (Pharmaceutical Benefits Scheme) compliance"""

    pbs_listed: bool = Field(..., description="Drug on PBS schedule")
    authority_required: bool = Field(
        default=False,
        description="Requires authority approval"
    )
    restrictions_met: bool = Field(
        default=True,
        description="PBS restrictions satisfied"
    )
    max_repeats: int = Field(default=5, description="Maximum PBS repeats allowed")
    patient_copay: Optional[float] = Field(
        default=None,
        description="Australian PBS patient copay amount"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "pbs_listed": True,
                "authority_required": False,
                "restrictions_met": True,
                "max_repeats": 5,
                "patient_copay": 7.30
            }
        }
    )


class DrugInteraction(BaseModel):
    """Drug interaction warning"""

    severity: str = Field(..., description="minor, moderate, severe")
    interacting_drug: str
    effect: str = Field(..., description="Clinical effect of interaction")
    recommendation: str = Field(..., description="What to do about it")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        if v not in ["minor", "moderate", "severe"]:
            raise ValueError("Severity must be minor, moderate, or severe")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "severity": "moderate",
                "interacting_drug": "Atorvastatin",
                "effect": "Increased bleeding risk when combined with aspirin",
                "recommendation": "Monitor for bleeding, consider gastroprotection"
            }
        }
    )


class DoseCheck(BaseModel):
    """Dose appropriateness validation"""

    within_range: bool = Field(..., description="Dose in therapeutic range")
    recommended_dose: str = Field(..., description="eTG recommended dose")
    patient_specific_factors: List[str] = Field(
        default_factory=list,
        description="Age, renal function, weight considerations"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "within_range": True,
                "recommended_dose": "75-100mg daily",
                "patient_specific_factors": [
                    "Standard adult dose appropriate",
                    "No renal adjustment needed"
                ]
            }
        }
    )


class PrescriptionValidationResult(BaseModel):
    """Result of prescription validation"""

    is_valid: bool = Field(..., description="Prescription is valid")
    pbs_compliant: bool = Field(..., description="Meets PBS requirements")
    medication_name: str = Field(..., description="Medication name")
    pbs_listed: bool = Field(default=True, description="Listed on PBS")
    authority_required: bool = Field(default=False, description="PBS authority needed")
    approved: bool = Field(..., description="Safe to prescribe")
    safety_score: float = Field(..., ge=0, le=10, description="Safety assessment")
    pbs_compliance: PBSComplianceCheck
    drug_interactions: List[DrugInteraction] = Field(default_factory=list)
    dose_appropriateness: DoseCheck
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    feedback: List[str] = Field(default_factory=list)
    processing_time_ms: int = Field(default=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "approved": True,
                "safety_score": 8.5,
                "pbs_compliance": {
                    "pbs_listed": True,
                    "authority_required": False,
                    "restrictions_met": True,
                    "max_repeats": 5,
                    "patient_copay": 7.30
                },
                "drug_interactions": [],
                "dose_appropriateness": {
                    "within_range": True,
                    "recommended_dose": "75-100mg daily",
                    "patient_specific_factors": []
                },
                "feedback": [
                    "Appropriate for secondary prevention",
                    "Consider gastroprotection if concurrent NSAID use"
                ],
                "processing_time_ms": 250
            }
        }
    )


# ============================================================================
# PATHOLOGY ORDER VALIDATION
# ============================================================================

class PathologyOrderValidationRequest(BaseModel):
    """Request to validate pathology test orders"""

    tests_ordered: List[str] = Field(..., description="Test names (e.g., FBC, UEC)")
    indication: str = Field(..., description="Clinical reason for testing")
    patient_context: Dict = Field(..., description="Patient demographics, history")
    urgency: str = Field(default="routine", description="routine, urgent, stat")

    @field_validator("urgency")
    @classmethod
    def validate_urgency(cls, v: str) -> str:
        if v not in ["routine", "urgent", "stat"]:
            raise ValueError("Urgency must be routine, urgent, or stat")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tests_ordered": ["FBC", "UEC", "Troponin", "D-dimer"],
                "indication": "Chest pain, ?ACS, ?PE",
                "patient_context": {
                    "age": 65,
                    "presenting_complaint": "Chest pain and dyspnoea",
                    "risk_factors": ["Smoking", "Hypertension", "Immobility"]
                },
                "urgency": "urgent"
            }
        }
    )


class MBSItem(BaseModel):
    """Medicare Benefits Schedule item"""

    test_name: str
    mbs_item_number: str = Field(..., description="MBS item code")
    rebate_amount: float = Field(..., description="Medicare rebate (AUD)")
    bulk_billable: bool = Field(default=True)
    notes: str = Field(default="", description="MBS restrictions/notes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "test_name": "Troponin",
                "mbs_item_number": "66512",
                "rebate_amount": 16.90,
                "bulk_billable": True,
                "notes": "Appropriate for suspected ACS"
            }
        }
    )


class PathologyValidationResult(BaseModel):
    """Result of pathology order validation"""

    appropriate: bool = Field(..., description="Investigation is appropriate")
    mbs_compliant: bool = Field(..., description="MBS compliant")
    test_name: str = Field(default="", description="Test name")
    mbs_item_number: str = Field(default="", description="MBS item number")
    appropriateness_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Clinical appropriateness"
    )
    mbs_items: List[MBSItem] = Field(default_factory=list)
    overuse_warnings: List[str] = Field(
        default_factory=list,
        description="Tests that may not be needed"
    )
    missing_tests: List[str] = Field(
        default_factory=list,
        description="Recommended additional tests"
    )
    cost_estimate: float = Field(default=0.0, description="Total MBS rebate (AUD)")
    feedback: List[str] = Field(default_factory=list, description="Feedback items")
    processing_time_ms: int = Field(default=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "appropriateness_score": 8.5,
                "mbs_items": [
                    {
                        "test_name": "Troponin",
                        "mbs_item_number": "66512",
                        "rebate_amount": 16.90,
                        "bulk_billable": True,
                        "notes": "Appropriate for ACS workup"
                    }
                ],
                "overuse_warnings": [
                    "D-dimer has low specificity in elderly patients"
                ],
                "missing_tests": [
                    "ECG (not a pathology test but essential for ACS)"
                ],
                "cost_estimate": 67.60,
                "feedback": "Appropriate investigation for chest pain with ACS/PE differential",
                "processing_time_ms": 180
            }
        }
    )
