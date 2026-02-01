"""
Pydantic schemas for OSCE model

AMC CLINICAL EXAM CONTEXT:
- 15-mark rubric validation (5 categories × 3 marks)
- 8-minute station duration
- Australian medical standards enforcement
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum

from schemas.mcq import MedicalSpecialty  # Reuse specialty enum


class OSCEType(str, Enum):
    """OSCE station types"""
    HISTORY_TAKING = "history_taking"
    PHYSICAL_EXAMINATION = "physical_examination"
    COUNSELING = "counseling"
    EMERGENCY_MANAGEMENT = "emergency_management"
    PROCEDURAL_SKILLS = "procedural_skills"
    COMMUNICATION = "communication"
    INTERPRETATION = "interpretation"  # ECG, X-ray, blood results
    BREAKING_BAD_NEWS = "breaking_bad_news"
    CONSENT = "consent"


# ============================================================================
# REQUEST SCHEMAS (Input)
# ============================================================================

class OSCECreate(BaseModel):
    """Schema for creating new OSCE"""
    osce_id: str = Field(..., pattern=r'^OSCE-[A-Z]+-\d{3}$')
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

    @validator('rubric')
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
            raise ValueError('Rubric must be a dictionary')

        required_categories = [
            'history_examination',
            'clinical_reasoning',
            'communication',
            'safety',
            'professionalism'
        ]

        # Check all required categories present
        for category in required_categories:
            if category not in v:
                raise ValueError(f'Rubric missing required category: {category}')

        # Validate each category
        total_marks = 0
        for category_name, category_data in v.items():
            if not isinstance(category_data, dict):
                raise ValueError(f'Category {category_name} must be a dictionary')

            # Check marks field
            if 'marks' not in category_data:
                raise ValueError(f'Category {category_name} missing "marks" field')

            marks = category_data['marks']
            if not isinstance(marks, int) or marks < 0 or marks > 3:
                raise ValueError(f'Category {category_name} marks must be 0-3')

            total_marks += marks

            # Check criteria field
            if 'criteria' not in category_data:
                raise ValueError(f'Category {category_name} missing "criteria" field')

            # Check mark descriptors (0, 1, 2, 3)
            for mark_level in ['0', '1', '2', '3']:
                if mark_level not in category_data:
                    raise ValueError(
                        f'Category {category_name} missing descriptor for mark level {mark_level}'
                    )

        # Total must be 15 marks
        if total_marks != 15:
            raise ValueError(f'Rubric must total 15 marks (AMC format), got {total_marks} marks')

        return v

    @validator('australian_guidelines')
    def validate_australian_guidelines(cls, v):
        """Validate Australian guideline references"""
        if v is None:
            return v

        australian_sources = [
            'therapeutic guidelines',
            'etg',
            'ahpra',
            'amh',
            'pbs',
            'ranzcp',
            'racgp',
            'talley',
            'murtagh',
            'amc'
        ]

        all_text = ' '.join(str(val) for val in v.values()).lower()
        if not any(source in all_text for source in australian_sources):
            raise ValueError(
                'Guidelines must reference Australian sources '
                '(eTG, AHPRA, AMH, PBS, RANZCP, RACGP, etc.)'
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


class OSCEWithRubric(OSCEPublic):
    """OSCE with complete rubric (for review after practice)"""
    examiner_instructions: Optional[str]
    rubric: Dict[str, Any]
    australian_guidelines: Optional[Dict[str, str]]
