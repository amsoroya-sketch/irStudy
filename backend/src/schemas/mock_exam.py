"""
Pydantic schemas for Mock Exam Mode (16-station OSCE exams)

AMC CLINICAL EXAM FORMAT:
- 16 stations × 8 minutes each = 128 minutes
- 2-minute breaks between stations
- Total duration: ~150 minutes (2.5 hours)
- Pass criteria: ≥198/240 (82.5%), no critical errors
- Balanced distribution: 2 personas per specialty × 8 specialties

SECURITY:
- All persona_id fields validated as UUIDs
- No PHI exposure in responses
- All timestamps in UTC with timezone
"""

from pydantic import BaseModel, Field, field_validator, UUID4
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid


# ============================================================================
# PERSONA INFO SCHEMA
# ============================================================================


class PersonaInfo(BaseModel):
    """Persona information for mock exam station"""

    persona_id: str = Field(..., description="UUID of patient persona")
    persona_code: str = Field(..., pattern=r"^[A-Z]+-\d{3}-.+$", description="Unique persona code")
    name: str = Field(..., min_length=2, max_length=100, description="Patient name")
    specialty: str = Field(..., min_length=3, max_length=50, description="Medical specialty")
    chief_complaint: str = Field(..., min_length=5, max_length=500, description="Presenting complaint")
    difficulty_level: Literal['foundation', 'intermediate', 'advanced'] = Field(
        ...,
        description="Difficulty level"
    )

    @field_validator('persona_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate persona_id is valid UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"persona_id must be a valid UUID, got: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "persona_id": "550e8400-e29b-41d4-a716-446655440000",
                "persona_code": "CARD-001-CHEST-PAIN",
                "name": "John Smith",
                "specialty": "Cardiology",
                "chief_complaint": "Chest pain for 2 hours",
                "difficulty_level": "intermediate"
            }
        }


# ============================================================================
# MOCK EXAM CREATION
# ============================================================================


class MockExamCreateRequest(BaseModel):
    """Request to create a new mock exam (optional customization)"""

    exam_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=200,
        description="Optional custom exam name"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "exam_name": "AMC Clinical Practice Exam #1"
            }
        }


class MockExamCreateResponse(BaseModel):
    """Response after creating mock exam"""

    exam_id: str = Field(..., description="UUID of created exam")
    stations_config: List[PersonaInfo] = Field(
        ...,
        min_length=16,
        max_length=16,
        description="16 personas for exam stations"
    )
    estimated_duration_minutes: int = Field(
        default=150,
        description="Estimated total duration (16×8min + 15×2min breaks)"
    )
    start_url: str = Field(..., description="URL to start exam")
    created_at: datetime = Field(..., description="Exam creation timestamp (UTC)")

    @field_validator('exam_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate exam_id is valid UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"exam_id must be a valid UUID, got: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "exam_id": "660e8400-e29b-41d4-a716-446655440001",
                "stations_config": [
                    {
                        "persona_id": "550e8400-e29b-41d4-a716-446655440000",
                        "persona_code": "CARD-001-CHEST-PAIN",
                        "name": "John Smith",
                        "specialty": "Cardiology",
                        "chief_complaint": "Chest pain for 2 hours",
                        "difficulty_level": "intermediate"
                    }
                ],
                "estimated_duration_minutes": 150,
                "start_url": "/api/v1/osce/session/660e8400-e29b-41d4-a716-446655440001/station/1",
                "created_at": "2026-04-05T10:00:00Z"
            }
        }


# ============================================================================
# MOCK EXAM STATUS
# ============================================================================


class MockExamStatusResponse(BaseModel):
    """Current exam status and progress"""

    exam_id: str = Field(..., description="UUID of exam")
    exam_state: Literal['IN_PROGRESS', 'COMPLETED', 'ABANDONED'] = Field(
        ...,
        description="Current exam state"
    )
    current_station_number: int = Field(
        ...,
        ge=1,
        le=16,
        description="Current station (1-16)"
    )
    stations_completed: int = Field(
        ...,
        ge=0,
        le=16,
        description="Number of stations completed"
    )
    total_score: int = Field(
        ...,
        ge=0,
        le=240,
        description="Running total score (max 240)"
    )
    max_possible_score: int = Field(default=240, description="Maximum possible score")
    time_elapsed_minutes: Optional[int] = Field(
        None,
        ge=0,
        description="Time elapsed since exam start"
    )
    started_at: Optional[datetime] = Field(None, description="Exam start time (UTC)")
    completed_at: Optional[datetime] = Field(None, description="Exam completion time (UTC)")
    exam_name: Optional[str] = Field(None, description="Custom exam name")

    @field_validator('exam_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate exam_id is valid UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"exam_id must be a valid UUID, got: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "exam_id": "660e8400-e29b-41d4-a716-446655440001",
                "exam_state": "IN_PROGRESS",
                "current_station_number": 5,
                "stations_completed": 4,
                "total_score": 48,
                "max_possible_score": 240,
                "time_elapsed_minutes": 42,
                "started_at": "2026-04-05T10:00:00Z",
                "completed_at": None,
                "exam_name": "AMC Clinical Practice Exam #1"
            }
        }


# ============================================================================
# STATION COMPLETION
# ============================================================================


class StationCompleteRequest(BaseModel):
    """Request to mark station as complete"""

    attempt_id: str = Field(..., description="UUID of OSCE attempt")
    station_score: int = Field(..., ge=0, le=15, description="Station score (0-15)")
    pass_fail: Literal['PASS', 'FAIL'] = Field(..., description="Station pass/fail status")

    @field_validator('attempt_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate attempt_id is valid UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"attempt_id must be a valid UUID, got: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "attempt_id": "770e8400-e29b-41d4-a716-446655440002",
                "station_score": 12,
                "pass_fail": "PASS"
            }
        }


class StationCompleteResponse(BaseModel):
    """Response after completing station"""

    next_station_number: Optional[int] = Field(
        None,
        ge=1,
        le=16,
        description="Next station number (null if exam complete)"
    )
    station_score: int = Field(..., ge=0, le=15, description="Score for completed station")
    overall_progress: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Overall exam progress (0.0-1.0)"
    )
    exam_complete: bool = Field(..., description="Whether exam is now complete")
    total_score: int = Field(..., ge=0, le=240, description="Running total score")

    class Config:
        json_schema_extra = {
            "example": {
                "next_station_number": 6,
                "station_score": 12,
                "overall_progress": 0.3125,
                "exam_complete": False,
                "total_score": 60
            }
        }


# ============================================================================
# EXAM RESULTS
# ============================================================================


class StationResult(BaseModel):
    """Individual station result"""

    station_number: int = Field(..., ge=1, le=16, description="Station number")
    persona_name: str = Field(..., description="Patient persona name")
    specialty: str = Field(..., description="Medical specialty")
    score: int = Field(..., ge=0, le=15, description="Station score (0-15)")
    pass_fail: Literal['PASS', 'FAIL'] = Field(..., description="Station outcome")
    duration_minutes: int = Field(default=8, description="Station duration")

    class Config:
        json_schema_extra = {
            "example": {
                "station_number": 1,
                "persona_name": "John Smith",
                "specialty": "Cardiology",
                "score": 12,
                "pass_fail": "PASS",
                "duration_minutes": 8
            }
        }


class SummaryStatistics(BaseModel):
    """Summary statistics for exam performance"""

    stations_passed: int = Field(..., ge=0, le=16, description="Number of stations passed")
    stations_failed: int = Field(..., ge=0, le=16, description="Number of stations failed")
    average_score_per_station: float = Field(
        ...,
        ge=0.0,
        le=15.0,
        description="Average score per station"
    )
    percentage: float = Field(..., ge=0.0, le=100.0, description="Overall percentage")
    performance_by_specialty: Dict[str, Dict[str, Any]] = Field(
        default_factory=dict,
        description="Performance breakdown by specialty"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "stations_passed": 14,
                "stations_failed": 2,
                "average_score_per_station": 12.375,
                "percentage": 82.5,
                "performance_by_specialty": {
                    "Cardiology": {
                        "stations": 2,
                        "average_score": 13.0,
                        "passed": 2
                    }
                }
            }
        }


class MockExamResultsResponse(BaseModel):
    """Comprehensive exam results"""

    exam_id: str = Field(..., description="UUID of exam")
    overall_score: int = Field(..., ge=0, le=240, description="Total score (0-240)")
    max_score: int = Field(default=240, description="Maximum possible score")
    percentage: float = Field(..., ge=0.0, le=100.0, description="Overall percentage")
    overall_pass_fail: Literal['PASS', 'FAIL'] = Field(..., description="Overall exam outcome")
    stations: List[StationResult] = Field(
        ...,
        min_length=16,
        max_length=16,
        description="Results for all 16 stations"
    )
    summary_statistics: SummaryStatistics = Field(..., description="Summary statistics")
    total_duration_minutes: int = Field(..., ge=0, description="Total exam duration")
    completed_at: datetime = Field(..., description="Exam completion time (UTC)")
    exam_name: Optional[str] = Field(None, description="Custom exam name")
    report_pdf_url: Optional[str] = Field(None, description="URL to PDF report (if generated)")

    @field_validator('exam_id')
    @classmethod
    def validate_uuid(cls, v: str) -> str:
        """Validate exam_id is valid UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"exam_id must be a valid UUID, got: {v}")

    class Config:
        json_schema_extra = {
            "example": {
                "exam_id": "660e8400-e29b-41d4-a716-446655440001",
                "overall_score": 198,
                "max_score": 240,
                "percentage": 82.5,
                "overall_pass_fail": "PASS",
                "stations": [],
                "summary_statistics": {
                    "stations_passed": 14,
                    "stations_failed": 2,
                    "average_score_per_station": 12.375,
                    "percentage": 82.5,
                    "performance_by_specialty": {}
                },
                "total_duration_minutes": 148,
                "completed_at": "2026-04-05T12:30:00Z",
                "exam_name": "AMC Clinical Practice Exam #1",
                "report_pdf_url": None
            }
        }
