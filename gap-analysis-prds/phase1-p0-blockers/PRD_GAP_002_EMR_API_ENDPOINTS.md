# PRD_GAP_002: EMR API Endpoints Implementation

**Priority**: P0 - CRITICAL BLOCKER
**Estimated Effort**: 8-12 hours
**Dependencies**: PRD_GAP_001 (Vault + Redis deployed)
**Owner**: rust-ffi-expert

---

## 1. REQUEST (What & Why)

### User Story
> As a medical student,
> I need REST API endpoints to practice EMR documentation,
> So that I can submit SOAP notes and view my progress dashboard.

### Business Context
- **Current State**: 6 EMR database tables exist, but 0/6 API endpoints implemented
- **Impact**: Frontend cannot access EMR system (40% of platform unusable)
- **Wasted Investment**: 18 critical EMR fixes from master plan cannot be validated
- **User Experience**: Dashboard shows placeholder data only

### Problem Statement
1. EMR database tables exist (`mock_patients`, `emr_sessions`, `emr_soap_notes`, etc.)
2. Migration applied successfully (`20260215_1200_008`)
3. **BUT**: `/backend/src/api/v1/emr/` directory does NOT exist
4. Frontend `/src/pages/PerformanceDashboard.tsx` calls non-existent endpoints
5. Students cannot practice EMR documentation

### Success Metrics
- [ ] 6 EMR API endpoints operational
- [ ] 20+ integration tests passing (100%)
- [ ] Performance: <500ms (p95) for submit endpoint
- [ ] Frontend can create sessions, submit SOAP notes, view dashboard
- [ ] EMR practice system unblocked (20% → 100% complete)

---

## 2. ARCHITECTURE (How)

### 2.1 API Endpoint Design

**Base Path**: `/api/v1/emr`

**Endpoints** (6 total):

#### Session Management (3 endpoints)

**1. Create EMR Session**
```http
POST /api/v1/emr/sessions
Authorization: Bearer <jwt-token>
Content-Type: application/json

Request:
{
  "mock_patient_id": "uuid",
  "emr_system": "epic" | "cerner",  // Theme selector
  "session_type": "practice" | "assessment"
}

Response (201 Created):
{
  "session_id": "uuid",
  "mock_patient": {
    "patient_id": "uuid",
    "name": "John Doe",
    "age": 45,
    "gender": "Male",
    "chief_complaint": "Chest pain",
    "vitals": {...},
    "medical_history": {...}
  },
  "started_at": "2026-03-13T10:00:00Z",
  "auto_save_enabled": true
}
```

**2. Get EMR Session**
```http
GET /api/v1/emr/sessions/{session_id}
Authorization: Bearer <jwt-token>

Response (200 OK):
{
  "session_id": "uuid",
  "mock_patient_id": "uuid",
  "emr_system": "epic",
  "started_at": "2026-03-13T10:00:00Z",
  "submitted_at": null,  // null if not submitted yet
  "soap_note": {
    "subjective": "...",
    "objective": "...",
    "assessment": "...",
    "plan": "..."
  },
  "validation_result": null,  // null until submitted
  "status": "in_progress" | "submitted" | "validated"
}
```

**3. Submit SOAP Note for Validation**
```http
POST /api/v1/emr/sessions/{session_id}/submit
Authorization: Bearer <jwt-token>
Content-Type: application/json

Request:
{
  "soap_note": {
    "subjective": "45yo M with 2-hour history of central chest pain...",
    "objective": "BP 145/90, HR 95, RR 18, Temp 37.2°C, SpO2 98%...",
    "assessment": "1. Acute coronary syndrome - rule out STEMI...",
    "plan": "1. Immediate: ECG, troponin, FBC, UEC, CXR..."
  },
  "prescriptions": [
    {
      "medication": "Aspirin",
      "dose": "300mg",
      "route": "PO",
      "frequency": "stat"
    }
  ],
  "pathology_orders": [
    {
      "test_name": "Troponin I",
      "urgency": "urgent",
      "clinical_notes": "?ACS"
    }
  ]
}

Response (200 OK):
{
  "session_id": "uuid",
  "submitted_at": "2026-03-13T10:15:00Z",
  "validation_result": {
    "overall_score": 85.5,  // 0-100
    "layer_1_rule_based": {
      "score": 90,
      "completeness": 95,
      "structure": 85,
      "errors": []
    },
    "layer_2_claude_ai": {
      "score": 82,
      "clinical_reasoning": 85,
      "safety": 90,
      "evidence_based": 80,
      "feedback": "Good differential diagnosis. Consider adding troponin timing..."
    },
    "layer_3_specialist": null,  // Only for flagged cases
    "pass_fail": "PASS",  // PASS (≥70), BORDERLINE (60-69), FAIL (<60)
    "time_taken_seconds": 900
  }
}
```

#### Dashboard Analytics (3 endpoints)

**4. Overall Progress**
```http
GET /api/v1/emr/dashboard/overall-progress
Authorization: Bearer <jwt-token>

Response (200 OK):
{
  "total_sessions": 67,
  "sessions_passed": 55,
  "sessions_failed": 8,
  "sessions_in_progress": 4,
  "average_score": 82.1,
  "total_time_minutes": 3420,
  "improvement_trend": +5.3,  // % improvement over last 10 sessions
  "current_streak": 7,  // Consecutive passing sessions
  "last_session_date": "2026-03-12T14:30:00Z"
}
```

**5. Specialty Breakdown**
```http
GET /api/v1/emr/dashboard/specialty-detail/{specialty}
Authorization: Bearer <jwt-token>

Parameters:
- specialty: "cardiology" | "respiratory" | "neurology" | "gastroenterology" |
             "endocrinology" | "musculoskeletal" | "psychiatry" | "general"

Response (200 OK):
{
  "specialty": "cardiology",
  "sessions_attempted": 12,
  "sessions_passed": 10,
  "average_score": 88.5,
  "weak_areas": [
    "ECG interpretation",
    "Antiplatelet therapy dosing"
  ],
  "strong_areas": [
    "History taking",
    "Differential diagnosis"
  ],
  "recommended_practice": [
    {
      "patient_id": "uuid",
      "scenario_name": "STEMI management",
      "difficulty": "intermediate"
    }
  ]
}
```

**6. Session History**
```http
GET /api/v1/emr/dashboard/session-history
Authorization: Bearer <jwt-token>

Query Parameters:
- limit: int (default 20, max 100)
- offset: int (default 0)
- specialty: string (optional filter)
- pass_fail: "PASS" | "FAIL" | "BORDERLINE" (optional filter)

Response (200 OK):
{
  "total_count": 67,
  "sessions": [
    {
      "session_id": "uuid",
      "mock_patient_name": "John Doe",
      "specialty": "cardiology",
      "chief_complaint": "Chest pain",
      "submitted_at": "2026-03-12T14:30:00Z",
      "score": 85.5,
      "pass_fail": "PASS",
      "time_taken_minutes": 15
    },
    // ... more sessions
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

### 2.2 Database Schema Integration

**Existing Tables** (already created):
- `mock_patients` - 500+ simulated patient records
- `emr_sessions` - Session tracking
- `emr_soap_notes` - SOAP documentation
- `emr_prescriptions` - PBS-compliant medications
- `emr_pathology_orders` - MBS pathology requests
- `emr_validation_results` - 3-layer validation feedback

**ORM Models** (`backend/src/db/models.py`):
```python
# Already exist - just reference them
from src.db.models import (
    EMRSession,
    EMRSOAPNote,
    EMRPrescription,
    EMRPathologyOrder,
    EMRValidationResult,
    MockPatient
)
```

### 2.3 Validation Service Integration

**Existing Service** (`backend/src/services/emr/validators/`):
- `fallback_validator.py` - Rule-based validation (Layer 1)
- Claude AI validator (Layer 2) - Integration needed
- Specialist review (Layer 3) - Manual process

**Integration**:
```python
from src.services.emr.validators.fallback_validator import FallbackValidator
from src.ai.claude_validator import ClaudeValidator  # To be created

async def validate_soap_note(soap_note: dict, patient_context: dict):
    # Layer 1: Rule-based (always runs)
    layer1_result = FallbackValidator().validate(soap_note, patient_context)

    # Layer 2: Claude AI (60% of time, 40% fallback)
    if random.random() < 0.6:
        try:
            layer2_result = await ClaudeValidator().validate(soap_note, patient_context)
        except Exception:
            layer2_result = None  # Fallback to Layer 1 only
    else:
        layer2_result = None

    # Combine scores
    overall_score = (layer1_result.score * 0.4 + (layer2_result.score if layer2_result else layer1_result.score) * 0.6)

    return {
        "overall_score": overall_score,
        "layer_1_rule_based": layer1_result,
        "layer_2_claude_ai": layer2_result,
        "layer_3_specialist": None,
        "pass_fail": "PASS" if overall_score >= 70 else ("BORDERLINE" if overall_score >= 60 else "FAIL")
    }
```

---

## 3. IMPLEMENTATION TASKS

### Task 1: Create API Directory Structure (30 minutes)

```bash
mkdir -p backend/src/api/v1/emr
touch backend/src/api/v1/emr/__init__.py
touch backend/src/api/v1/emr/router.py
touch backend/src/api/v1/emr/sessions.py
touch backend/src/api/v1/emr/dashboard.py
touch backend/src/api/v1/emr/schemas.py
```

### Task 2: Define Pydantic Schemas (2 hours)

**File**: `backend/src/api/v1/emr/schemas.py`

```python
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID

# Request Schemas
class CreateSessionRequest(BaseModel):
    mock_patient_id: UUID
    emr_system: Literal["epic", "cerner"] = "epic"
    session_type: Literal["practice", "assessment"] = "practice"

class SOAPNoteSubmit(BaseModel):
    subjective: str = Field(..., min_length=50, max_length=5000)
    objective: str = Field(..., min_length=50, max_length=5000)
    assessment: str = Field(..., min_length=50, max_length=5000)
    plan: str = Field(..., min_length=50, max_length=5000)

class PrescriptionSubmit(BaseModel):
    medication: str
    dose: str
    route: str
    frequency: str

class PathologyOrderSubmit(BaseModel):
    test_name: str
    urgency: Literal["routine", "urgent", "stat"]
    clinical_notes: str

class SubmitSessionRequest(BaseModel):
    soap_note: SOAPNoteSubmit
    prescriptions: List[PrescriptionSubmit] = []
    pathology_orders: List[PathologyOrderSubmit] = []

# Response Schemas
class MockPatientResponse(BaseModel):
    patient_id: UUID
    name: str
    age: int
    gender: str
    chief_complaint: str
    vitals: dict
    medical_history: dict

class SessionResponse(BaseModel):
    session_id: UUID
    mock_patient: MockPatientResponse
    emr_system: str
    started_at: datetime
    submitted_at: Optional[datetime] = None
    status: Literal["in_progress", "submitted", "validated"]
    soap_note: Optional[dict] = None
    validation_result: Optional[dict] = None

# ... (continue with all schemas)
```

### Task 3: Implement Session Endpoints (3 hours)

**File**: `backend/src/api/v1/emr/sessions.py`

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from src.db.base import get_db
from src.db.models import EMRSession, EMRSOAPNote, MockPatient, User
from src.core.auth import get_current_user
from src.services.emr.validators.fallback_validator import FallbackValidator
from .schemas import (
    CreateSessionRequest, SessionResponse, SubmitSessionRequest
)

router = APIRouter()

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create new EMR practice session"""

    # Validate mock patient exists
    mock_patient = db.query(MockPatient).filter(
        MockPatient.patient_id == request.mock_patient_id
    ).first()

    if not mock_patient:
        raise HTTPException(
            status_code=404,
            detail=f"Mock patient {request.mock_patient_id} not found"
        )

    # Create session
    session = EMRSession(
        user_id=current_user.user_id,
        mock_patient_id=request.mock_patient_id,
        emr_system=request.emr_system,
        session_type=request.session_type,
        status="in_progress"
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    # Return response
    return SessionResponse(
        session_id=session.session_id,
        mock_patient=MockPatientResponse(**mock_patient.__dict__),
        emr_system=session.emr_system,
        started_at=session.started_at,
        status=session.status
    )

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve EMR session details"""

    session = db.query(EMRSession).filter(
        EMRSession.session_id == session_id,
        EMRSession.user_id == current_user.user_id  # Authorization check
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch related data
    mock_patient = db.query(MockPatient).filter(
        MockPatient.patient_id == session.mock_patient_id
    ).first()

    soap_note = db.query(EMRSOAPNote).filter(
        EMRSOAPNote.session_id == session_id
    ).first()

    return SessionResponse(
        session_id=session.session_id,
        mock_patient=MockPatientResponse(**mock_patient.__dict__),
        emr_system=session.emr_system,
        started_at=session.started_at,
        submitted_at=session.submitted_at,
        status=session.status,
        soap_note=soap_note.__dict__ if soap_note else None,
        validation_result=session.validation_result
    )

@router.post("/sessions/{session_id}/submit")
async def submit_session(
    session_id: UUID,
    request: SubmitSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit SOAP note for validation"""

    # Fetch session (authorization check)
    session = db.query(EMRSession).filter(
        EMRSession.session_id == session_id,
        EMRSession.user_id == current_user.user_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.status != "in_progress":
        raise HTTPException(status_code=400, detail="Session already submitted")

    # Save SOAP note
    soap_note = EMRSOAPNote(
        session_id=session_id,
        subjective=request.soap_note.subjective,
        objective=request.soap_note.objective,
        assessment=request.soap_note.assessment,
        plan=request.soap_note.plan
    )
    db.add(soap_note)

    # Validate SOAP note
    mock_patient = db.query(MockPatient).get(session.mock_patient_id)
    validation_result = await validate_soap_note(
        soap_note=request.soap_note.dict(),
        patient_context=mock_patient.__dict__
    )

    # Update session
    session.status = "validated"
    session.submitted_at = datetime.utcnow()
    session.validation_result = validation_result

    db.commit()

    return validation_result

# Helper function (implement in service layer)
async def validate_soap_note(soap_note: dict, patient_context: dict):
    # TODO: Integrate with FallbackValidator and ClaudeValidator
    pass
```

### Task 4: Implement Dashboard Endpoints (2 hours)

**File**: `backend/src/api/v1/emr/dashboard.py`

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, List

from src.db.base import get_db
from src.db.models import EMRSession, User
from src.core.auth import get_current_user
from .schemas import (
    OverallProgressResponse,
    SpecialtyDetailResponse,
    SessionHistoryResponse
)

router = APIRouter()

@router.get("/dashboard/overall-progress", response_model=OverallProgressResponse)
async def get_overall_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall EMR progress statistics"""

    # Query all user sessions
    sessions = db.query(EMRSession).filter(
        EMRSession.user_id == current_user.user_id
    ).all()

    total_sessions = len(sessions)
    sessions_passed = sum(1 for s in sessions if s.validation_result and s.validation_result.get("pass_fail") == "PASS")
    sessions_failed = sum(1 for s in sessions if s.validation_result and s.validation_result.get("pass_fail") == "FAIL")
    sessions_in_progress = sum(1 for s in sessions if s.status == "in_progress")

    # Calculate average score
    scores = [s.validation_result.get("overall_score") for s in sessions if s.validation_result]
    average_score = sum(scores) / len(scores) if scores else 0

    # Calculate total time
    total_time_minutes = sum(
        (s.submitted_at - s.started_at).total_seconds() / 60
        for s in sessions if s.submitted_at
    )

    # Calculate improvement trend (last 10 sessions vs previous 10)
    recent_10 = sessions[-10:] if len(sessions) >= 10 else sessions
    previous_10 = sessions[-20:-10] if len(sessions) >= 20 else []

    recent_avg = sum(s.validation_result.get("overall_score", 0) for s in recent_10) / len(recent_10) if recent_10 else 0
    previous_avg = sum(s.validation_result.get("overall_score", 0) for s in previous_10) / len(previous_10) if previous_10 else recent_avg

    improvement_trend = recent_avg - previous_avg

    # Current streak
    current_streak = 0
    for session in reversed(sessions):
        if session.validation_result and session.validation_result.get("pass_fail") == "PASS":
            current_streak += 1
        else:
            break

    return OverallProgressResponse(
        total_sessions=total_sessions,
        sessions_passed=sessions_passed,
        sessions_failed=sessions_failed,
        sessions_in_progress=sessions_in_progress,
        average_score=average_score,
        total_time_minutes=total_time_minutes,
        improvement_trend=improvement_trend,
        current_streak=current_streak,
        last_session_date=sessions[-1].started_at if sessions else None
    )

# ... (continue with specialty-detail and session-history endpoints)
```

### Task 5: Register Router in Main (30 minutes)

**File**: `backend/src/api/v1/router.py`

```python
from fastapi import APIRouter
from .emr.router import router as emr_router  # NEW

api_router = APIRouter()

# Existing routers
api_router.include_router(patient_personas_router, prefix="/patient-personas", tags=["AI OSCE"])
api_router.include_router(osce_sessions_router, prefix="/osce-sessions", tags=["AI OSCE"])

# NEW: EMR router
api_router.include_router(emr_router, prefix="/emr", tags=["EMR Practice"])
```

**File**: `backend/src/api/v1/emr/router.py`

```python
from fastapi import APIRouter
from .sessions import router as sessions_router
from .dashboard import router as dashboard_router

router = APIRouter()

router.include_router(sessions_router, tags=["EMR Sessions"])
router.include_router(dashboard_router, tags=["EMR Dashboard"])
```

### Task 6: Write Integration Tests (3 hours)

**File**: `backend/tests/test_api/test_emr_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

def test_create_session(client: TestClient, auth_headers: dict, mock_patient_id: str):
    """Test POST /api/v1/emr/sessions"""
    response = client.post(
        "/api/v1/emr/sessions",
        json={
            "mock_patient_id": mock_patient_id,
            "emr_system": "epic",
            "session_type": "practice"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert "session_id" in data
    assert data["emr_system"] == "epic"
    assert data["status"] == "in_progress"

def test_get_session(client: TestClient, auth_headers: dict, session_id: str):
    """Test GET /api/v1/emr/sessions/{id}"""
    response = client.get(
        f"/api/v1/emr/sessions/{session_id}",
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id

def test_submit_session(client: TestClient, auth_headers: dict, session_id: str):
    """Test POST /api/v1/emr/sessions/{id}/submit"""
    response = client.post(
        f"/api/v1/emr/sessions/{session_id}/submit",
        json={
            "soap_note": {
                "subjective": "45yo M with 2-hour history of central chest pain, radiating to left arm...",
                "objective": "BP 145/90, HR 95, RR 18, Temp 37.2°C, SpO2 98%. Cardiovascular: S1 S2 normal...",
                "assessment": "1. Acute coronary syndrome - rule out STEMI. 2. Differential: Unstable angina...",
                "plan": "1. Immediate: 12-lead ECG, high-sensitivity troponin, FBC, UEC, CXR..."
            },
            "prescriptions": [
                {
                    "medication": "Aspirin",
                    "dose": "300mg",
                    "route": "PO",
                    "frequency": "stat"
                }
            ]
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert "validation_result" in data
    assert data["validation_result"]["overall_score"] > 0
    assert data["validation_result"]["pass_fail"] in ["PASS", "BORDERLINE", "FAIL"]

# ... (add 20+ more tests for all endpoints)
```

---

## 4. ACCEPTANCE CRITERIA

### Must Have (P0)
- [x] 6 EMR API endpoints operational
- [x] All endpoints require JWT authentication
- [x] User can only access their own sessions (authorization)
- [x] 20+ integration tests passing (100%)
- [x] Performance: Submit endpoint <500ms (p95)
- [x] Pydantic validation on all request/response models
- [x] Frontend PerformanceDashboard displays real data (not placeholder)

### Should Have (P1)
- [ ] Auto-save endpoint (PATCH /sessions/{id}/autosave)
- [ ] Session deletion endpoint (DELETE /sessions/{id})
- [ ] Export session to PDF

### Could Have (P2)
- [ ] Batch session creation (POST /sessions/batch)
- [ ] Advanced analytics (time-of-day performance, specialty correlations)

---

## 5. TESTING REQUIREMENTS

**Unit Tests**: 0 (all logic in service layer)
**Integration Tests**: 20+ tests
- Session creation (3 tests: valid, invalid patient, duplicate)
- Session retrieval (3 tests: valid, not found, unauthorized)
- Session submission (5 tests: valid, missing fields, already submitted, performance)
- Overall progress (3 tests: no sessions, some sessions, many sessions)
- Specialty detail (3 tests: valid specialty, invalid specialty, no data)
- Session history (3 tests: pagination, filtering, sorting)

**Total**: 20+ tests

---

## 6. PERFORMANCE TARGETS

| Endpoint | Target (p95) | Load |
|----------|--------------|------|
| POST /sessions | <200ms | 10 req/s |
| GET /sessions/{id} | <100ms | 50 req/s |
| POST /sessions/{id}/submit | <500ms | 5 req/s |
| GET /dashboard/overall-progress | <300ms | 20 req/s |
| GET /dashboard/session-history | <200ms | 20 req/s |

---

## 7. DEPENDENCIES

**Requires**:
- PRD_GAP_001 (Vault + Redis deployed)
- Database tables (already exist)
- JWT authentication (already implemented)

**Blocks**:
- Frontend EMR integration
- Dashboard testing
- EMR practice system validation

---

**END OF PRD_GAP_002**
