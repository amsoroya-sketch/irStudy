# Epic EHR Practice System - API Specification

**Document Version**: 1.0
**Date**: 2026-02-15
**Status**: Ready for Implementation

---

## Executive Summary

This document specifies the complete RESTful API for the Epic EHR Practice System, following existing irStudy API patterns (FastAPI + Pydantic validation + JWT authentication). All endpoints are prefixed with `/api/v1/emr/` and follow OpenAPI 3.0 standards.

---

## 1. API Overview

### 1.1 Base URL

```
Development: http://localhost:8000/api/v1/emr
Production: https://irstudy.com.au/api/v1/emr
```

### 1.2 Authentication

**All EMR endpoints require JWT authentication** (reuse existing pattern):

```http
Authorization: Bearer <JWT_TOKEN>
```

**Roles**:
- `student`: Can practice EMR, view own sessions
- `educator`: Can review student sessions, provide feedback
- `admin`: Full access to all EMR data

### 1.3 API Versioning

- Version: `v1` (initial release)
- Breaking changes: Increment to `v2` with deprecation notice
- Non-breaking additions: Add to `v1` without version bump

### 1.4 Rate Limiting

```
Anonymous: 10 requests/minute
Authenticated: 100 requests/minute
Claude AI validation: 20 requests/minute (to control costs)
```

---

## 2. Endpoint Groups

### 2.1 Sessions Management

```
POST   /api/v1/emr/sessions/start           # Create new EMR session
GET    /api/v1/emr/sessions/{session_id}    # Get session details
PUT    /api/v1/emr/sessions/{session_id}    # Update session (auto-save)
POST   /api/v1/emr/sessions/{session_id}/submit  # Submit for validation
DELETE /api/v1/emr/sessions/{session_id}    # Cancel/delete session
GET    /api/v1/emr/sessions                 # List user's sessions (paginated)
```

### 2.2 Patient Cases

```
GET    /api/v1/emr/patients/random          # Get random patient case
GET    /api/v1/emr/patients/{patient_id}    # Get specific patient
GET    /api/v1/emr/patients/from-osce/{osce_id}  # Convert OSCE to EMR case
GET    /api/v1/emr/patients                 # List all available patients
```

### 2.3 Validation

```
POST   /api/v1/emr/validation/soap-note     # Validate SOAP note (Layer 2+3)
POST   /api/v1/emr/validation/prescription  # Validate prescription (PBS)
POST   /api/v1/emr/validation/pathology     # Validate pathology order (MBS)
```

### 2.4 Analytics & Progress

```
GET    /api/v1/emr/analytics/progress       # User's EMR progress metrics
GET    /api/v1/emr/analytics/history        # Session history (paginated)
GET    /api/v1/emr/analytics/trends         # Performance trends over time
GET    /api/v1/emr/analytics/leaderboard    # Anonymized leaderboard (optional)
```

### 2.5 Reference Data

```
GET    /api/v1/emr/reference/pbs/medications     # PBS drug search
GET    /api/v1/emr/reference/mbs/pathology       # MBS pathology search
GET    /api/v1/emr/reference/guidelines          # eTG quick reference
GET    /api/v1/emr/reference/specialties         # Available specialties
```

---

## 3. Detailed Endpoint Specifications

### 3.1 Sessions - Start New Session

**Endpoint**: `POST /api/v1/emr/sessions/start`

**Description**: Create a new EMR practice session with a randomly selected patient or specific patient.

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",  // Optional: specific patient
  "specialty": "cardiology",  // Optional: filter by specialty
  "difficulty": "medium"      // Optional: easy, medium, hard
}
```

**Pydantic Schema**:
```python
from pydantic import BaseModel, UUID4, Field
from typing import Optional

class EMRSessionStartRequest(BaseModel):
    patient_id: Optional[UUID4] = None
    specialty: Optional[str] = Field(None, pattern="^(cardiology|respiratory|gastroenterology|neurology|endocrinology|rheumatology|haematology|renal|infectious_diseases|emergency_medicine)$")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")

    class Config:
        json_schema_extra = {
            "example": {
                "specialty": "cardiology",
                "difficulty": "medium"
            }
        }
```

**Response** (201 Created):
```json
{
  "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
  "patient": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "mrn": "MRN12345678",
    "name": "John Smith",
    "age": 58,
    "gender": "male",
    "demographics": {
      "address": "12 King St, Sydney NSW 2000",
      "phone": "0412 345 678",
      "gp_details": {
        "name": "Dr. Jane Doe",
        "clinic": "Sydney Medical Centre"
      }
    },
    "presenting_complaint": "Central chest pain",
    "vital_signs": {
      "hr": 95,
      "bp_systolic": 155,
      "bp_diastolic": 92,
      "rr": 20,
      "spo2": 96,
      "temp": 36.8,
      "pain_score": 7
    },
    "allergies": [
      {"allergen": "Penicillin", "reaction": "Rash", "severity": "mild"}
    ]
  },
  "specialty": "cardiology",
  "difficulty": "medium",
  "started_at": "2026-02-15T10:30:00Z",
  "status": "in_progress",
  "elapsed_time_seconds": 0,
  "auto_save_count": 0
}
```

**Pydantic Response Schema**:
```python
from datetime import datetime

class PatientResponse(BaseModel):
    id: UUID4
    mrn: str
    name: str
    age: int
    gender: str
    demographics: dict
    presenting_complaint: str
    vital_signs: dict
    allergies: list

class EMRSessionStartResponse(BaseModel):
    session_id: UUID4
    patient: PatientResponse
    specialty: str
    difficulty: str
    started_at: datetime
    status: str
    elapsed_time_seconds: int
    auto_save_count: int
```

**Errors**:
- `400 Bad Request`: Invalid specialty/difficulty
- `404 Not Found`: No patients available matching criteria
- `401 Unauthorized`: Missing/invalid JWT token
- `429 Too Many Requests`: Rate limit exceeded

**Implementation Pattern** (following existing OSCE pattern):
```python
# backend/src/api/v1/emr/sessions.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.database import get_db
from src.db.models import User, MockPatient, EMRSession
from src.api.dependencies import get_current_active_user
from src.schemas.emr import EMRSessionStartRequest, EMRSessionStartResponse

router = APIRouter(prefix="/sessions", tags=["EMR Sessions"])

@router.post("/start", response_model=EMRSessionStartResponse, status_code=201)
async def start_emr_session(
    request: EMRSessionStartRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Start a new EMR practice session.

    - Selects random patient (or specific patient_id if provided)
    - Creates EMRSession record
    - Returns patient details and session metadata
    """

    # 1. Select patient (random or specific)
    if request.patient_id:
        patient = db.query(MockPatient).filter(
            MockPatient.id == request.patient_id,
            MockPatient.deleted_at.is_(None)
        ).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
    else:
        # Random patient with optional filters
        query = db.query(MockPatient).filter(MockPatient.deleted_at.is_(None))
        if request.specialty:
            query = query.filter(MockPatient.specialty == request.specialty)
        if request.difficulty:
            query = query.filter(MockPatient.difficulty == request.difficulty)

        patient = query.order_by(func.random()).first()
        if not patient:
            raise HTTPException(status_code=404, detail="No patients available matching criteria")

    # 2. Create EMR session
    session = EMRSession(
        user_id=current_user.id,
        patient_id=patient.id,
        specialty=patient.specialty,
        difficulty=patient.difficulty,
        status="in_progress"
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # 3. Return response
    return EMRSessionStartResponse(
        session_id=session.id,
        patient=patient,
        specialty=session.specialty,
        difficulty=session.difficulty,
        started_at=session.started_at,
        status=session.status,
        elapsed_time_seconds=0,
        auto_save_count=0
    )
```

---

### 3.2 Sessions - Get Session Details

**Endpoint**: `GET /api/v1/emr/sessions/{session_id}`

**Description**: Retrieve complete session details including SOAP note, prescriptions, pathology orders, and validation results.

**Authentication**: Required (JWT)

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Response** (200 OK):
```json
{
  "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
  "user_id": 123,
  "patient": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "mrn": "MRN12345678",
    "name": "John Smith",
    "age": 58,
    "presenting_complaint": "Central chest pain",
    "medical_history": {
      "pmhx": ["Hypertension", "Type 2 Diabetes"],
      "medications": [
        {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"}
      ],
      "allergies": [{"allergen": "Penicillin", "reaction": "Rash"}]
    },
    "vital_signs": {"hr": 95, "bp_systolic": 155, "bp_diastolic": 92},
    "investigation_results": {
      "ecg": {"findings": "ST elevation 2mm in leads II, III, aVF"},
      "labs": {
        "troponin_i": {"value": 1.2, "unit": "ng/mL", "flag": "HIGH"}
      }
    }
  },
  "soap_note": {
    "subjective": "58M with 2-hour history of central crushing chest pain 7/10...",
    "objective": "Alert, distressed, diaphoretic. HR 95, BP 155/92...",
    "assessment": "Acute Coronary Syndrome - Inferior STEMI",
    "plan": "Call 000, Aspirin 300mg STAT, Clopidogrel 300mg STAT...",
    "word_count": 450,
    "typing_wpm": 35,
    "version": 3,
    "auto_saved_at": "2026-02-15T10:45:00Z"
  },
  "prescriptions": [
    {
      "id": "abc123",
      "medication_name": "Aspirin",
      "dose": "300mg",
      "frequency": "STAT then 100mg daily",
      "route": "PO",
      "repeats": 5,
      "indication": "Acute Coronary Syndrome",
      "pbs_listed": true,
      "is_valid": true
    }
  ],
  "pathology_orders": [
    {
      "id": "def456",
      "test_name": "Troponin I",
      "mbs_item_number": "66800",
      "urgency": "emergency",
      "indication": "Suspected STEMI",
      "appropriate": true
    }
  ],
  "validation_results": [
    {
      "validation_type": "soap_note",
      "overall_score": 12.5,
      "passed": true,
      "strengths": ["Excellent SOCRATES assessment", "Appropriate differential"],
      "improvements": ["Consider radiation to jaw/neck"],
      "red_flags": ["STEMI criteria - urgent cardiology referral"]
    }
  ],
  "specialty": "cardiology",
  "difficulty": "medium",
  "started_at": "2026-02-15T10:30:00Z",
  "submitted_at": "2026-02-15T11:00:00Z",
  "elapsed_time_seconds": 1800,
  "validation_score": 12.5,
  "status": "graded",
  "typing_metrics": {
    "total_words": 450,
    "average_wpm": 35,
    "accuracy": 0.92
  }
}
```

**Errors**:
- `404 Not Found`: Session not found
- `403 Forbidden`: User doesn't own this session (students can only view own sessions)
- `401 Unauthorized`: Missing/invalid JWT token

**Authorization Rules**:
```python
# Students: Can only view their own sessions
if current_user.role == "student" and session.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Not authorized to view this session")

# Educators/Admins: Can view any session
```

---

### 3.3 Sessions - Update Session (Auto-Save)

**Endpoint**: `PUT /api/v1/emr/sessions/{session_id}`

**Description**: Auto-save SOAP note draft, prescriptions, pathology orders. Called every 30 seconds by frontend.

**Authentication**: Required (JWT)

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Request Body**:
```json
{
  "soap_note": {
    "subjective": "58M with 2-hour history of central crushing chest pain 7/10, radiating to left arm. Associated with sweating and nausea. Pain started at rest...",
    "objective": "Alert, distressed, diaphoretic. HR 95 bpm, BP 155/92 mmHg, RR 20, SpO2 96%, Temp 36.8°C, Pain score 7/10. CVS: Regular rhythm, no murmurs...",
    "assessment": "Acute Coronary Syndrome - likely Inferior STEMI based on ECG findings (ST elevation II, III, aVF) and elevated troponin.",
    "plan": "IMMEDIATE: Call 000 / Activate cath lab. Aspirin 300mg STAT PO, Clopidogrel 300mg STAT PO, Morphine 2.5mg IV for pain relief..."
  },
  "prescriptions": [
    {
      "medication_name": "Aspirin",
      "dose": "300mg",
      "frequency": "STAT then 100mg daily",
      "route": "PO",
      "repeats": 5,
      "indication": "Acute Coronary Syndrome"
    }
  ],
  "pathology_orders": [
    {
      "test_name": "Troponin I",
      "urgency": "emergency",
      "indication": "Suspected STEMI - serial troponins at 0h, 3h"
    }
  ],
  "elapsed_time_seconds": 900  // 15 minutes elapsed
}
```

**Response** (200 OK):
```json
{
  "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
  "status": "in_progress",
  "auto_save_count": 1,
  "last_auto_save_at": "2026-02-15T10:45:00Z",
  "soap_note_version": 2,
  "message": "Session auto-saved successfully"
}
```

**Implementation**:
```python
@router.put("/{session_id}", response_model=EMRSessionUpdateResponse)
async def update_emr_session(
    session_id: UUID,
    request: EMRSessionUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Auto-save session data (called every 30 seconds)."""

    # 1. Get session (verify ownership)
    session = db.query(EMRSession).filter(
        EMRSession.id == session_id,
        EMRSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Cannot update submitted session")

    # 2. Update/create SOAP note
    soap_note = db.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == session_id
    ).first()

    if soap_note:
        # Update existing
        soap_note.subjective = request.soap_note.get("subjective")
        soap_note.objective = request.soap_note.get("objective")
        soap_note.assessment = request.soap_note.get("assessment")
        soap_note.plan = request.soap_note.get("plan")
        soap_note.version += 1
        soap_note.auto_saved_at = datetime.utcnow()
    else:
        # Create new
        soap_note = EMRSOAPNote(
            session_id=session_id,
            **request.soap_note,
            version=1,
            auto_saved_at=datetime.utcnow()
        )
        db.add(soap_note)

    # 3. Update session metadata
    session.elapsed_time_seconds = request.elapsed_time_seconds
    session.auto_save_count += 1
    session.last_auto_save_at = datetime.utcnow()
    session.updated_at = datetime.utcnow()

    db.commit()

    return EMRSessionUpdateResponse(
        session_id=session.id,
        status=session.status,
        auto_save_count=session.auto_save_count,
        last_auto_save_at=session.last_auto_save_at,
        soap_note_version=soap_note.version,
        message="Session auto-saved successfully"
    )
```

**Errors**:
- `404 Not Found`: Session not found
- `400 Bad Request`: Cannot update submitted session
- `403 Forbidden`: Not authorized (wrong user)

---

### 3.4 Sessions - Submit for Validation

**Endpoint**: `POST /api/v1/emr/sessions/{session_id}/submit`

**Description**: Submit session for final validation. Triggers 3-layer validation (Zod already done client-side, now Python + Claude AI). **This is a long-running operation (3-5 seconds).**

**Authentication**: Required (JWT)

**Path Parameters**:
- `session_id` (UUID): Session identifier

**Request Body**:
```json
{
  "final_soap_note": {
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
  },
  "typing_metrics": {
    "total_words": 450,
    "average_wpm": 35,
    "total_typing_time_seconds": 770,
    "backspace_count": 42,
    "accuracy": 0.92
  }
}
```

**Response** (200 OK) - **3-5 second latency**:
```json
{
  "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
  "status": "graded",
  "submitted_at": "2026-02-15T11:00:00Z",
  "validation_results": {
    "overall_score": 12.5,
    "passed": true,
    "category_scores": {
      "history_examination": 3.0,
      "clinical_reasoning": 2.5,
      "communication": 3.0,
      "patient_safety": 2.0,
      "professionalism": 2.0
    },
    "layer_1_zod": {
      "passed": true,
      "errors": [],
      "latency_ms": 25
    },
    "layer_2_python": {
      "passed": true,
      "warnings": [
        {
          "field": "prescriptions[0].repeats",
          "message": "Max 5 repeats for Schedule 4 drugs (you entered 5 - OK)"
        }
      ],
      "pbs_compliance": "compliant",
      "mbs_compliance": "compliant",
      "australian_terminology": "correct",
      "latency_ms": 850
    },
    "layer_3_ai": {
      "overall_score": 12.5,
      "category_scores": {
        "history_examination": 3.0,
        "clinical_reasoning": 2.5,
        "communication": 3.0,
        "patient_safety": 2.0,
        "professionalism": 2.0
      },
      "strengths": [
        "Excellent SOCRATES pain assessment with all components",
        "Appropriate differential diagnosis (ACS, PE, gastritis)",
        "Safety netting with clear red flag advice",
        "Correct use of Australian drug names (aspirin not ASA)"
      ],
      "improvements": [
        "Consider asking about radiation to jaw/neck (common in ACS)",
        "Add cardiovascular risk factors to assessment (age, diabetes, smoking)",
        "Specify exact troponin timing in plan (0h and 3h for serial monitoring)"
      ],
      "red_flags": [
        "STEMI criteria met (ST elevation >1mm in 2 contiguous leads) - URGENT cardiology referral needed",
        "Patient requires immediate cath lab activation within 90 minutes"
      ],
      "australian_compliance": {
        "terminology": "✓ Correct (paracetamol not acetaminophen, adrenaline not epinephrine)",
        "emergency_number": "✓ Mentioned 000 for worsening symptoms",
        "etg_alignment": "✓ Follows eTG Cardiovascular guidelines for ACS management"
      },
      "latency_ms": 3420,
      "model": "claude-sonnet-4-5-20250929",
      "tokens_used": 1850
    },
    "strengths": [
      "Excellent SOCRATES pain assessment",
      "Appropriate differential diagnosis",
      "Safety netting with red flags"
    ],
    "improvements": [
      "Consider radiation to jaw/neck",
      "Add cardiovascular risk factors"
    ],
    "red_flags": [
      "STEMI criteria - urgent cardiology referral"
    ]
  },
  "performance_summary": {
    "time_taken_minutes": 30,
    "words_written": 450,
    "average_wpm": 35,
    "score_vs_average": "+2.1",  // 2.1 points above user's average
    "percentile": 75  // Top 25% of users
  },
  "next_steps": {
    "message": "Great work! You passed with 12.5/15 (83%). Practice more cardiology cases to improve clinical reasoning.",
    "recommended_actions": [
      "Review eTG Cardiovascular guidelines for ACS",
      "Practice 2 more cardiology OSCE stations",
      "Watch video: 'ECG interpretation for STEMI'"
    ],
    "related_content": {
      "osce_ids": [12, 34, 56],  // Related OSCE scenarios
      "mcq_ids": [789, 790, 791],  // Related MCQs
      "video_urls": ["https://..."]
    }
  }
}
```

**Implementation** (with async Claude AI call):
```python
from src.agents.soap_validator import SOAPNoteValidator

@router.post("/{session_id}/submit", response_model=EMRSessionSubmitResponse)
async def submit_emr_session(
    session_id: UUID,
    request: EMRSessionSubmitRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Submit EMR session for final validation.

    Triggers 3-layer validation:
    - Layer 1: Zod (already done client-side)
    - Layer 2: Python PBS/MBS compliance (~1 second)
    - Layer 3: Claude AI clinical reasoning (~3-5 seconds)
    """

    # 1. Get session
    session = db.query(EMRSession).filter(
        EMRSession.id == session_id,
        EMRSession.user_id == current_user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status == "graded":
        raise HTTPException(status_code=400, detail="Session already submitted")

    # 2. Get patient and validation criteria
    patient = db.query(MockPatient).filter(MockPatient.id == session.patient_id).first()

    # 3. Layer 2: Python validation (PBS/MBS compliance)
    layer_2_result = await validate_pbs_mbs_compliance(
        soap_note=request.final_soap_note,
        prescriptions=request.prescriptions,
        pathology_orders=request.pathology_orders
    )

    # 4. Layer 3: Claude AI validation
    soap_validator = SOAPNoteValidator()
    layer_3_result = await soap_validator.validate(
        soap_note=request.final_soap_note,
        patient_case=patient.to_dict(),
        rubric_criteria=patient.validation_criteria
    )

    # 5. Save validation results
    validation_result = EMRValidationResult(
        session_id=session_id,
        validation_type="soap_note",
        layer_1_zod={"passed": True, "errors": []},  // Assume client validated
        layer_2_python=layer_2_result,
        layer_3_ai=layer_3_result,
        overall_score=layer_3_result["overall_score"],
        passed=layer_3_result["overall_score"] >= 9.0,  // 60% pass mark
        strengths=layer_3_result["strengths"],
        improvements=layer_3_result["improvements"],
        red_flags=layer_3_result["red_flags"]
    )
    db.add(validation_result)

    # 6. Update session status
    session.status = "graded"
    session.submitted_at = datetime.utcnow()
    session.validation_score = layer_3_result["overall_score"]
    session.score_breakdown = layer_3_result["category_scores"]
    session.typing_metrics = request.typing_metrics

    # 7. Update user progress
    await update_user_emr_progress(current_user.id, session, db)

    db.commit()

    # 8. Return comprehensive response
    return EMRSessionSubmitResponse(
        session_id=session.id,
        status=session.status,
        submitted_at=session.submitted_at,
        validation_results=validation_result,
        performance_summary=calculate_performance_summary(session, current_user),
        next_steps=generate_next_steps(session, validation_result, patient)
    )
```

**Errors**:
- `404 Not Found`: Session not found
- `400 Bad Request`: Session already submitted, or missing required data
- `500 Internal Server Error`: Claude API error (retry once)

---

### 3.5 Patients - Get Random Patient

**Endpoint**: `GET /api/v1/emr/patients/random`

**Description**: Get a random patient case for EMR practice (alternative to starting session directly).

**Authentication**: Required (JWT)

**Query Parameters**:
- `specialty` (optional): Filter by medical specialty
- `difficulty` (optional): easy, medium, hard

**Example Request**:
```
GET /api/v1/emr/patients/random?specialty=cardiology&difficulty=medium
```

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "mrn": "MRN12345678",
  "name": "John Smith",
  "age": 58,
  "gender": "male",
  "demographics": {
    "address": "12 King St, Sydney NSW 2000",
    "phone": "0412 345 678"
  },
  "presenting_complaint": "Central chest pain",
  "medical_history": {
    "pmhx": ["Hypertension", "Type 2 Diabetes"],
    "medications": [
      {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"}
    ]
  },
  "vital_signs": {
    "hr": 95,
    "bp_systolic": 155,
    "bp_diastolic": 92,
    "temp": 36.8
  },
  "specialty": "cardiology",
  "difficulty": "medium"
}
```

**Errors**:
- `404 Not Found`: No patients matching criteria

---

### 3.6 Validation - Validate SOAP Note

**Endpoint**: `POST /api/v1/emr/validation/soap-note`

**Description**: Standalone SOAP note validation (can be called during session for real-time feedback, or after submission).

**Authentication**: Required (JWT)

**Request Body**:
```json
{
  "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
  "soap_note": {
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
  }
}
```

**Response** (200 OK) - **3-5 second latency**:
```json
{
  "validation_type": "soap_note",
  "overall_score": 12.5,
  "passed": true,
  "category_scores": {
    "history_examination": 3.0,
    "clinical_reasoning": 2.5,
    "communication": 3.0,
    "patient_safety": 2.0,
    "professionalism": 2.0
  },
  "strengths": ["Excellent SOCRATES assessment"],
  "improvements": ["Consider radiation to jaw/neck"],
  "red_flags": ["STEMI criteria - urgent referral"],
  "australian_compliance": {
    "terminology": "✓ Correct",
    "emergency_number": "✓ Mentioned 000",
    "etg_alignment": "✓ Follows eTG guidelines"
  },
  "latency_ms": 3420
}
```

**Rate Limiting**: 20 requests/minute (to control Claude API costs)

---

### 3.7 Reference - PBS Medication Search

**Endpoint**: `GET /api/v1/emr/reference/pbs/medications`

**Description**: Search PBS medication database (4,000+ drugs) with autocomplete support.

**Authentication**: Required (JWT)

**Query Parameters**:
- `q` (required): Search query (min 2 characters)
- `limit` (optional): Max results (default 10, max 50)

**Example Request**:
```
GET /api/v1/emr/reference/pbs/medications?q=amlod&limit=5
```

**Response** (200 OK):
```json
{
  "query": "amlod",
  "results": [
    {
      "medication_name": "Amlodipine",
      "pbs_item_code": "1234A",
      "strength": "5mg",
      "form": "tablet",
      "pbs_listed": true,
      "authority_required": false,
      "max_quantity": 30,
      "max_repeats": 5,
      "restriction": "Hypertension, angina",
      "brand_names": ["Norvasc", "Amlodipine Sandoz"],
      "australian_approved": true
    },
    {
      "medication_name": "Amlodipine",
      "strength": "10mg",
      "form": "tablet",
      "pbs_listed": true,
      "authority_required": false
    }
  ],
  "total": 2
}
```

**Implementation**:
```python
@router.get("/reference/pbs/medications")
async def search_pbs_medications(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Search PBS medication database with autocomplete."""

    # Search in PBS database (loaded from CSV/JSON)
    results = db.query(PBSMedication).filter(
        PBSMedication.medication_name.ilike(f"%{q}%")
    ).limit(limit).all()

    return {
        "query": q,
        "results": [med.to_dict() for med in results],
        "total": len(results)
    }
```

---

### 3.8 Analytics - User Progress

**Endpoint**: `GET /api/v1/emr/analytics/progress`

**Description**: Get user's EMR progress metrics (extends existing user_progress data).

**Authentication**: Required (JWT)

**Query Parameters**:
- `user_id` (optional): Get another user's progress (educators/admins only)

**Response** (200 OK):
```json
{
  "user_id": 123,
  "emr_sessions_completed": 25,
  "emr_soap_notes_written": 25,
  "emr_average_score": 11.2,
  "emr_pass_rate": 0.84,
  "emr_highest_score": 14.0,
  "emr_total_time_minutes": 750,
  "emr_last_session_date": "2026-02-15",
  "by_specialty": {
    "cardiology": {
      "sessions": 8,
      "average_score": 12.1,
      "pass_rate": 0.875
    },
    "respiratory": {
      "sessions": 5,
      "average_score": 10.8,
      "pass_rate": 0.80
    }
  },
  "recent_trend": {
    "last_7_days": {
      "sessions": 5,
      "average_score": 12.0,
      "improvement": "+0.8"  // vs. overall average
    },
    "last_30_days": {
      "sessions": 18,
      "average_score": 11.5,
      "improvement": "+0.3"
    }
  },
  "unified_progress": {
    "total_mcqs_attempted": 450,
    "total_osces_practiced": 32,
    "total_emr_sessions": 25,
    "overall_engagement_score": 85  // Composite metric
  }
}
```

---

### 3.9 Analytics - Session History

**Endpoint**: `GET /api/v1/emr/analytics/history`

**Description**: Paginated list of user's EMR sessions with filtering.

**Authentication**: Required (JWT)

**Query Parameters**:
- `user_id` (optional): Get another user's history (educators/admins only)
- `specialty` (optional): Filter by specialty
- `status` (optional): in_progress, submitted, graded
- `page` (default 1)
- `per_page` (default 20, max 100)

**Response** (200 OK):
```json
{
  "sessions": [
    {
      "session_id": "7a3f8d2e-1b4c-4e9a-8d7f-3e2a1b4c5d6e",
      "patient_name": "John Smith",
      "specialty": "cardiology",
      "difficulty": "medium",
      "started_at": "2026-02-15T10:30:00Z",
      "submitted_at": "2026-02-15T11:00:00Z",
      "validation_score": 12.5,
      "passed": true,
      "status": "graded"
    },
    {
      "session_id": "8b4g9e3f-2c5d-5f0b-9e8g-4f3b2c6d7e8f",
      "patient_name": "Sarah Johnson",
      "specialty": "respiratory",
      "difficulty": "hard",
      "started_at": "2026-02-14T14:00:00Z",
      "submitted_at": null,
      "validation_score": null,
      "passed": null,
      "status": "in_progress"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 25,
    "total_pages": 2
  }
}
```

---

## 4. Error Response Format

### 4.1 Standard Error Response

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "SOAP note subjective section too short (minimum 50 characters)",
    "details": {
      "field": "soap_note.subjective",
      "current_length": 30,
      "minimum_length": 50
    },
    "timestamp": "2026-02-15T10:45:00Z",
    "request_id": "req_abc123"
  }
}
```

### 4.2 Error Codes

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Request validation failed (Pydantic) |
| 400 | `INVALID_SESSION_STATUS` | Cannot perform action on session in this status |
| 401 | `UNAUTHORIZED` | Missing or invalid JWT token |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 429 | `RATE_LIMIT_EXCEEDED` | Too many requests |
| 500 | `INTERNAL_ERROR` | Server error |
| 503 | `CLAUDE_API_ERROR` | Claude AI service unavailable (retry) |

---

## 5. Pydantic Schemas Summary

### 5.1 Request Schemas

```python
# backend/src/schemas/emr.py

from pydantic import BaseModel, UUID4, Field, validator
from typing import Optional, List, Dict
from datetime import datetime

class EMRSessionStartRequest(BaseModel):
    patient_id: Optional[UUID4] = None
    specialty: Optional[str] = Field(None, pattern="^(cardiology|respiratory|...)$")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard)$")

class SOAPNoteData(BaseModel):
    subjective: str = Field(..., min_length=50, description="HPI minimum 50 chars")
    objective: str = Field(..., min_length=30, description="Vitals + exam minimum 30 chars")
    assessment: str = Field(..., min_length=20, description="Diagnosis minimum 20 chars")
    plan: str = Field(..., min_length=30, description="Management minimum 30 chars")

class PrescriptionData(BaseModel):
    medication_name: str = Field(..., min_length=2)
    dose: str = Field(..., pattern=r"^\d+(\.\d+)?\s*(mg|g|mcg|mL|units)$")
    frequency: str = Field(..., pattern=r"^(daily|BD|TDS|QID|PRN|weekly|STAT)$")
    route: str = Field(..., pattern=r"^(PO|IV|IM|SC|PR|topical|inhaled)$")
    repeats: int = Field(..., ge=0, le=5, description="Max 5 repeats (PBS)")
    indication: str

class PathologyOrderData(BaseModel):
    test_name: str = Field(..., min_length=2)
    urgency: str = Field(..., pattern=r"^(routine|urgent|emergency)$")
    indication: str

class EMRSessionUpdateRequest(BaseModel):
    soap_note: Optional[SOAPNoteData]
    prescriptions: Optional[List[PrescriptionData]]
    pathology_orders: Optional[List[PathologyOrderData]]
    elapsed_time_seconds: int = Field(..., ge=0)

class TypingMetrics(BaseModel):
    total_words: int
    average_wpm: float
    total_typing_time_seconds: int
    backspace_count: int
    accuracy: float = Field(..., ge=0, le=1)

class EMRSessionSubmitRequest(BaseModel):
    final_soap_note: SOAPNoteData
    prescriptions: Optional[List[PrescriptionData]]
    pathology_orders: Optional[List[PathologyOrderData]]
    typing_metrics: TypingMetrics
```

### 5.2 Response Schemas

```python
class PatientResponse(BaseModel):
    id: UUID4
    mrn: str
    name: str
    age: int
    gender: str
    demographics: dict
    presenting_complaint: str
    vital_signs: dict
    allergies: list
    specialty: str
    difficulty: str

class EMRSessionStartResponse(BaseModel):
    session_id: UUID4
    patient: PatientResponse
    specialty: str
    difficulty: str
    started_at: datetime
    status: str
    elapsed_time_seconds: int
    auto_save_count: int

class ValidationResultResponse(BaseModel):
    overall_score: float = Field(..., ge=0, le=15)
    passed: bool
    category_scores: Dict[str, float]
    strengths: List[str]
    improvements: List[str]
    red_flags: List[str]
    layer_1_zod: dict
    layer_2_python: dict
    layer_3_ai: dict

class EMRSessionSubmitResponse(BaseModel):
    session_id: UUID4
    status: str
    submitted_at: datetime
    validation_results: ValidationResultResponse
    performance_summary: dict
    next_steps: dict
```

---

## 6. Performance & Caching

### 6.1 Caching Strategy

```python
# Redis caching for expensive queries

# Cache patient data (1 hour)
@cache(expire=3600)
async def get_patient(patient_id: UUID):
    return db.query(MockPatient).filter(MockPatient.id == patient_id).first()

# Cache PBS medication search (24 hours)
@cache(expire=86400)
async def search_pbs_medications(query: str, limit: int):
    return db.query(PBSMedication).filter(...).all()

# No caching for session data (real-time updates needed)
```

### 6.2 Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Standard endpoints: 100 req/min
@app.post("/api/v1/emr/sessions/start")
@limiter.limit("100/minute")
async def start_session(...):
    pass

# Claude AI validation: 20 req/min (cost control)
@app.post("/api/v1/emr/validation/soap-note")
@limiter.limit("20/minute")
async def validate_soap(...):
    pass
```

---

## 7. Testing Strategy

### 7.1 Unit Tests (pytest)

```python
# tests/test_emr_api.py

async def test_start_session_success(client, auth_headers):
    """Test successful session start."""
    response = await client.post(
        "/api/v1/emr/sessions/start",
        json={"specialty": "cardiology", "difficulty": "medium"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["patient"]["specialty"] == "cardiology"

async def test_start_session_no_patients(client, auth_headers, empty_db):
    """Test session start with no patients available."""
    response = await client.post(
        "/api/v1/emr/sessions/start",
        json={"specialty": "cardiology"},
        headers=auth_headers
    )
    assert response.status_code == 404
    assert "No patients available" in response.json()["error"]["message"]

async def test_submit_session_validation(client, auth_headers, mock_session):
    """Test session submission with full validation."""
    response = await client.post(
        f"/api/v1/emr/sessions/{mock_session.id}/submit",
        json={
            "final_soap_note": {
                "subjective": "58M with 2-hour central chest pain...",
                "objective": "HR 95, BP 155/92...",
                "assessment": "ACS - STEMI",
                "plan": "Call 000, aspirin 300mg STAT..."
            },
            "typing_metrics": {
                "total_words": 450,
                "average_wpm": 35,
                "total_typing_time_seconds": 770,
                "backspace_count": 42,
                "accuracy": 0.92
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "graded"
    assert data["validation_results"]["overall_score"] >= 0
    assert data["validation_results"]["overall_score"] <= 15
```

### 7.2 Integration Tests

```python
async def test_full_emr_workflow(client, auth_headers):
    """Test complete EMR workflow: start → update → submit."""

    # 1. Start session
    start_response = await client.post(
        "/api/v1/emr/sessions/start",
        json={"specialty": "cardiology"},
        headers=auth_headers
    )
    session_id = start_response.json()["session_id"]

    # 2. Auto-save (simulate 30 seconds)
    await asyncio.sleep(0.1)  # Simulate delay
    update_response = await client.put(
        f"/api/v1/emr/sessions/{session_id}",
        json={
            "soap_note": {"subjective": "Test HPI...", "objective": "Test exam..."},
            "elapsed_time_seconds": 30
        },
        headers=auth_headers
    )
    assert update_response.json()["auto_save_count"] == 1

    # 3. Submit
    submit_response = await client.post(
        f"/api/v1/emr/sessions/{session_id}/submit",
        json={...},
        headers=auth_headers
    )
    assert submit_response.json()["status"] == "graded"
```

---

## 8. API Documentation (OpenAPI/Swagger)

### 8.1 Auto-Generated Docs

FastAPI automatically generates OpenAPI docs:

```
Development: http://localhost:8000/docs (Swagger UI)
Development: http://localhost:8000/redoc (ReDoc)
```

### 8.2 Custom Tags

```python
from fastapi import FastAPI

app = FastAPI(
    title="irStudy EMR Practice API",
    description="Epic EHR simulation for Australian AMC Clinical Exam preparation",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "EMR Sessions",
            "description": "Create and manage EMR practice sessions"
        },
        {
            "name": "Patients",
            "description": "Simulated patient cases"
        },
        {
            "name": "Validation",
            "description": "3-layer SOAP note validation (Zod, Python, Claude AI)"
        },
        {
            "name": "Analytics",
            "description": "Progress tracking and performance metrics"
        },
        {
            "name": "Reference",
            "description": "PBS/MBS/eTG reference data"
        }
    ]
)
```

---

## 9. Migration from Existing Patterns

### 9.1 Reuse Existing OSCE API Pattern

```python
# EXISTING: backend/src/api/v1/osces.py (reference)
@router.post("/{osce_id}/complete-station")
async def complete_osce_station(
    osce_id: int,
    attempt_data: OSCEAttemptCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 1. Validate input
    # 2. Calculate scores
    # 3. Create attempt record
    # 4. Update OSCE statistics
    # 5. Update user progress
    # 6. Return feedback

# NEW: backend/src/api/v1/emr/sessions.py (follow same pattern)
@router.post("/{session_id}/submit")
async def submit_emr_session(
    session_id: UUID,
    submission_data: EMRSubmissionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # 1. Validate input (Pydantic)
    # 2. Run 3-layer validation (Python + Claude)
    # 3. Create validation_result record
    # 4. Update session status
    # 5. Update user_progress (EMR columns)
    # 6. Return comprehensive feedback
```

### 9.2 Authentication Dependency

```python
# REUSE: backend/src/api/dependencies.py (no changes)
from src.api.dependencies import get_current_active_user

# All EMR endpoints use this dependency
@router.post("/sessions/start")
async def start_session(
    current_user: User = Depends(get_current_active_user)  # ← Reuse
):
    pass
```

---

## 10. Success Criteria

- [ ] All 19 endpoints implemented (`/sessions/*`, `/patients/*`, `/validation/*`, `/analytics/*`, `/reference/*`)
- [ ] Pydantic schemas for all request/response models
- [ ] 3-layer validation system working (Zod client-side already done, Python + Claude AI)
- [ ] Auto-save every 30 seconds tested
- [ ] Session submission returns validation in 3-5 seconds
- [ ] PBS medication search returns results <500ms
- [ ] User progress updates correctly after each session
- [ ] Pytest unit tests pass (100%)
- [ ] OpenAPI docs auto-generated and accurate
- [ ] Rate limiting enforced (Claude API: 20 req/min)

---

## Conclusion

This API specification provides a **complete, production-ready design** for the Epic EHR Practice System backend. Key highlights:

- ✅ **19 RESTful endpoints** following FastAPI best practices
- ✅ **Pydantic validation** on all inputs (Australian compliance built-in)
- ✅ **3-layer validation** (Zod → Python → Claude AI)
- ✅ **Reuses existing patterns** (OSCE API, JWT auth, user progress tracking)
- ✅ **Performance optimized** (caching, rate limiting, indexes)
- ✅ **Comprehensive testing** (unit tests, integration tests)
- ✅ **Auto-generated OpenAPI docs** (Swagger UI, ReDoc)

**Next Steps**: Proceed to INTEGRATION_STRATEGY.md for OSCE → EMR patient case conversion logic.

---

**Document Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2026-02-15
**Review Date**: Post-implementation (API testing phase)
