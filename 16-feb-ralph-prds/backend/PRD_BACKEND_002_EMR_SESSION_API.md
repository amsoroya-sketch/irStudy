# PRD: EMR Session Management API

**PRD ID**: PRD_BACKEND_002_EMR_SESSION_API
**Category**: Backend
**Priority**: P0-Critical (BLOCKS frontend development)
**Estimated Effort**: 10-14 hours
**Dependencies**: PRD_BACKEND_001 (Database Migration must complete first)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** medical student using the EMR Practice System
**I want** to start, save, and submit EMR practice sessions
**So that** I can practice Australian SOAP notes, prescriptions, and pathology orders with auto-save and progress tracking

### Business Context
The EMR Session API is the **backbone** of the EMR Practice System, managing:
1. **Session lifecycle**: Start → Auto-save drafts → Submit for validation → Complete
2. **Patient assignment**: Random patient by specialty/complexity OR specific OSCE-linked patient
3. **EMR system selection**: Cerner PowerChart OR Epic EHR (user preference)
4. **Draft persistence**: Auto-save every 30 seconds (prevent data loss)
5. **Session history**: Retrieve past sessions for review and learning
6. **Progress tracking**: Update user_progress metrics after each session

This API must be **production-ready** with:
- **Auto-save latency**: <200ms (user shouldn't notice)
- **Session retrieval**: <500ms (fast page load)
- **Concurrent sessions**: Support 100+ users simultaneously
- **Data integrity**: No lost drafts, all state changes transactional

### Success Metrics
- **API Response Time**: <200ms (p95) for all endpoints
- **Auto-save Success Rate**: 99.9%+ (no data loss)
- **Session Completion Rate**: >80% of started sessions completed
- **Concurrent Users**: 100+ simultaneous sessions without performance degradation
- **Test Coverage**: ≥70% (unit + integration tests)
- **Test Pass Rate**: 100% (zero-tolerance policy)

### Scope
**In Scope**:
- 6 API endpoints (start, update/auto-save, submit, get, list, delete)
- Session state management (active/completed)
- Patient assignment logic (random, specialty-filtered, OSCE-linked)
- EMR system preference (Cerner/Epic)
- Auto-save functionality (JSONB session_data)
- Session history retrieval
- Progress metrics updates (user_progress table)
- OSCE integration (link sessions to OSCE stations)

**Out of Scope** (Handled by other PRDs):
- SOAP note validation (PRD_BACKEND_003)
- Prescription validation (PRD_BACKEND_003)
- Pathology validation (PRD_BACKEND_003)
- Patient scenario generation (PRD_BACKEND_004 - OSCE conversion)
- Frontend components (PRD_FRONTEND_001, PRD_FRONTEND_002)

---

## A - ARCHITECTURE (How)

### Technical Approach
Build FastAPI REST endpoints following existing patterns from `/backend/src/api/v1/osces.py` and `/backend/src/api/v1/mcqs.py`. Use Pydantic schemas for request/response validation, SQLAlchemy for database operations, and JWT authentication for all endpoints.

**API Contract Standardization (Fix #6)**:
- Backend uses snake_case (Python convention)
- Frontend expects camelCase (JavaScript convention)
- Solution: Pydantic `alias` for automatic serialization
- All responses use camelCase field names
- Example: `session_id` → `sessionId`, `emr_system` → `emrSystem`
- Config: `populate_by_name = True` (accepts both formats)

### System Design

#### Component Diagram
```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (React + MUI)                     │
│  EpicSOAPEditor, CernerSOAPEditor, EMRDashboard             │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTP/JSON (JWT Auth)
                         │
┌────────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Port 8001)                     │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  /api/v1/emr/sessions/* (NEW - 6 endpoints)            │ │
│  │  - POST   /sessions/start                              │ │
│  │  - PUT    /sessions/{session_id}  (auto-save)          │ │
│  │  - POST   /sessions/{session_id}/submit                │ │
│  │  - GET    /sessions/{session_id}                       │ │
│  │  - GET    /sessions  (list with filters)               │ │
│  │  - DELETE /sessions/{session_id}                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     Business Logic (Services Layer)                    │ │
│  │  - SessionService: CRUD operations                     │ │
│  │  - PatientAssignmentService: Random/filtered selection │ │
│  │  - ProgressTrackingService: Update user_progress       │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │     Data Access Layer (SQLAlchemy ORM)                 │ │
│  │  - EMRSession model                                    │ │
│  │  - MockPatient model                                   │ │
│  │  - UserProgress model                                  │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│              PostgreSQL Database                             │
│  - emr_sessions                                              │
│  - mock_patients                                             │
│  - user_progress (EMR columns)                               │
└──────────────────────────────────────────────────────────────┘
```

#### Data Flow: Start Session
```
1. User clicks "Start EMR Practice" (Epic system, Cardiology specialty)
   ↓
2. Frontend: POST /api/v1/emr/sessions/start
   {
     "emr_system": "epic",
     "patient_filter": {"specialty": "Cardiology", "complexity": "Moderate"},
     "osce_id": null  // Optional: link to OSCE station
   }
   ↓
3. Backend: PatientAssignmentService.get_random_patient(specialty="Cardiology", complexity="Moderate")
   ↓
4. Backend: Create EMRSession record (user_id, patient_id, emr_system="epic", is_active=true)
   ↓
5. Backend: Update user_progress.emr_sessions_total += 1, emr_epic_sessions += 1
   ↓
6. Backend: Return session + patient data
   {
     "session_id": "uuid",
     "patient": {...},  // Full patient scenario
     "emr_system": "epic",
     "started_at": "2026-02-16T10:30:00Z"
   }
   ↓
7. Frontend: Render Epic UI with patient data, start timer
```

#### Data Flow: Auto-Save
```
1. User types in SOAP note Subjective section (every 30 seconds trigger auto-save)
   ↓
2. Frontend: PUT /api/v1/emr/sessions/{session_id}
   {
     "session_data": {
       "draft_subjective": "Patient presents with chest pain...",
       "draft_objective": "",
       "current_tab": "subjective",
       "last_edit_time": "2026-02-16T10:35:00Z",
       "word_count": 15
     }
   }
   ↓
3. Backend: Update emr_sessions.session_data = JSONB (merge with existing)
   ↓
4. Backend: Update emr_sessions.auto_saved_at = NOW()
   ↓
5. Backend: Return success (200 OK)
   ↓
6. Frontend: Show "Draft saved" indicator (briefly)
```

#### Data Flow: Submit Session
```
1. User clicks "Submit for Validation"
   ↓
2. Frontend: POST /api/v1/emr/sessions/{session_id}/submit
   {
     "soap_note": {
       "subjective": "Patient presents with...",
       "objective": "BP 152/88, HR 92, RR 20...",
       "assessment": "Likely ACS...",
       "plan": "ECG, troponin, aspirin..."
     },
     "prescriptions": [
       {"medication": "Aspirin", "dose": "300mg", "route": "PO", ...}
     ],
     "pathology_orders": [
       {"test": "Troponin", "urgency": "Urgent", ...}
     ]
   }
   ↓
3. Backend: Mark session is_active=false, completed_at=NOW()
   ↓
4. Backend: Create emr_soap_notes record (link to session_id)
   ↓
5. Backend: Create emr_prescriptions records
   ↓
6. Backend: Create emr_pathology_orders records
   ↓
7. Backend: Update user_progress:
   - emr_sessions_completed += 1
   - emr_soap_notes_completed += 1
   - emr_prescriptions_written += len(prescriptions)
   - emr_pathology_orders_placed += len(pathology_orders)
   - emr_specialty_stats[specialty] += 1
   ↓
8. Backend: Trigger validation (async) - PRD_BACKEND_003
   ↓
9. Backend: Return success + validation_queue_id
   {
     "session_id": "uuid",
     "completed": true,
     "validation_queued": true,
     "validation_id": "uuid"
   }
   ↓
10. Frontend: Navigate to validation results page (poll for completion)
```

### API Endpoints Specification

#### Endpoint 1: Start Session
```python
POST /api/v1/emr/sessions/start
```

**Request Body** (Pydantic schema):
```python
class SessionStartRequest(BaseModel):
    emr_system: Literal["cerner", "epic"]
    patient_filter: Optional[PatientFilter] = None  # specialty, complexity, osce_id
    osce_id: Optional[str] = None  # Link to OSCE station if applicable

class PatientFilter(BaseModel):
    specialty: Optional[str] = None  # "Cardiology", "Respiratory", etc.
    complexity: Optional[Literal["Simple", "Moderate", "Complex"]] = None
    exclude_completed: bool = True  # Don't repeat patients user has already done
```

**Response** (200 OK):
```python
class SessionStartResponse(BaseModel):
    session_id: str = Field(..., alias="sessionId")
    patient: MockPatientResponse  # Full patient scenario
    emr_system: str = Field(..., alias="emrSystem")
    started_at: datetime = Field(..., alias="startedAt")
    session_data: dict = Field(default_factory=dict, alias="sessionData")

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase

class MockPatientResponse(BaseModel):
    id: str
    mrn: str
    full_name: str = Field(..., alias="fullName")
    age: int
    gender: str
    allergies: List[str]
    current_medications: List[dict] = Field(..., alias="currentMedications")
    vital_signs: dict = Field(..., alias="vitalSigns")
    presenting_complaint: str = Field(..., alias="presentingComplaint")
    clinical_scenario: str = Field(..., alias="clinicalScenario")
    specialty: str
    complexity_level: str = Field(..., alias="complexityLevel")
    # ... (all patient fields except internal metadata)

    class Config:
        populate_by_name = True  # Accept both snake_case and camelCase
```

**Business Logic**:
1. Validate user authenticated (JWT)
2. Check user doesn't have >5 active sessions (limit concurrent sessions)
3. If osce_id provided: get patient linked to that OSCE
4. Else: Use PatientAssignmentService to get random patient matching filters
5. Create EMRSession record (user_id, patient_id, emr_system, is_active=true)
6. Update user_progress.emr_sessions_total += 1
7. Return session + patient data

**Error Responses**:
- 401 Unauthorized: Missing/invalid JWT
- 400 Bad Request: Invalid emr_system or filter values
- 429 Too Many Requests: User has >5 active sessions
- 404 Not Found: osce_id provided but OSCE doesn't exist
- 500 Internal Server Error: Database error

---

#### Endpoint 2: Update Session (Auto-Save)
```python
PUT /api/v1/emr/sessions/{session_id}
```

**Request Body**:
```python
class SessionUpdateRequest(BaseModel):
    session_data: dict  # JSONB: any draft data (flexible schema)
    # Example:
    # {
    #   "draft_subjective": "Patient presents with...",
    #   "draft_objective": "BP 145/90...",
    #   "current_tab": "objective",
    #   "typing_start_time": "2026-02-16T10:30:00Z",
    #   "word_count": 150,
    #   "last_edit_time": "2026-02-16T10:35:00Z"
    # }
```

**Response** (200 OK):
```python
class SessionUpdateResponse(BaseModel):
    session_id: str = Field(..., alias="sessionId")
    auto_saved_at: datetime = Field(..., alias="autoSavedAt")

    class Config:
        populate_by_name = True
    message: str = "Draft saved successfully"
```

**Business Logic**:
1. Validate user owns this session (user_id matches)
2. Validate session is still active (is_active=true)
3. Merge session_data (JSONB update, preserve existing keys)
4. Update auto_saved_at = NOW()
5. Return success

**Performance Target**: <200ms (critical for UX - user shouldn't notice delay)

**Error Responses**:
- 401 Unauthorized: User doesn't own session
- 404 Not Found: Session doesn't exist
- 409 Conflict: Session already completed (is_active=false)

---

#### Endpoint 3: Submit Session
```python
POST /api/v1/emr/sessions/{session_id}/submit
```

**Request Body**:
```python
class SessionSubmitRequest(BaseModel):
    soap_note: SOAPNoteSubmit
    prescriptions: List[PrescriptionSubmit] = []
    pathology_orders: List[PathologyOrderSubmit] = []
    completion_time_seconds: int  # Frontend tracks total time
    typing_wpm: Optional[int] = None  # Frontend calculates WPM

class SOAPNoteSubmit(BaseModel):
    subjective: str = Field(..., min_length=50)
    objective: str = Field(..., min_length=30)
    assessment: str = Field(..., min_length=30)
    plan: str = Field(..., min_length=30)
    note_type: str = "Progress Note"

class PrescriptionSubmit(BaseModel):
    medication_name: str
    dose: str
    frequency: str
    route: str
    quantity: int
    repeats: int = Field(..., ge=0, le=5)
    indication: str = Field(..., min_length=5)

class PathologyOrderSubmit(BaseModel):
    test_name: str
    urgency: Literal["Routine", "Urgent", "Emergency"]
    clinical_indication: str = Field(..., min_length=10)
    is_panel: bool = False
    panel_tests: List[str] = []
```

**Response** (200 OK):
```python
class SessionSubmitResponse(BaseModel):
    session_id: str
    completed_at: datetime
    soap_note_id: str
    prescription_ids: List[str]
    pathology_order_ids: List[str]
    validation_queued: bool = True
    validation_status: str = "pending"  # "pending" | "in_progress" | "completed"
```

**Business Logic** (CRITICAL - Multi-step transaction):
1. Validate user owns session
2. Validate session is active
3. **BEGIN TRANSACTION**
4. Mark session: is_active=false, completed_at=NOW()
5. Create emr_soap_notes record (session_id, user_id, patient_scenario_id, subjective, objective, assessment, plan, completion_time_seconds, typing_wpm)
6. Create emr_prescriptions records (loop through prescriptions)
7. Create emr_pathology_orders records (loop through pathology_orders)
8. Update user_progress:
   - emr_sessions_completed += 1
   - emr_soap_notes_completed += 1
   - emr_prescriptions_written += len(prescriptions)
   - emr_pathology_orders_placed += len(pathology_orders)
   - emr_specialty_stats[patient.specialty] += 1
9. **COMMIT TRANSACTION**
10. Queue validation (async task - PRD_BACKEND_003)
11. Return success with IDs

**Error Responses**:
- 401 Unauthorized
- 404 Not Found
- 409 Conflict: Session already submitted
- 422 Unprocessable Entity: Pydantic validation failed (e.g., subjective too short)

---

#### Endpoint 4: Get Session
```python
GET /api/v1/emr/sessions/{session_id}
```

**Query Parameters**: None

**Response** (200 OK):
```python
class SessionDetailResponse(BaseModel):
    session_id: str
    user_id: str
    patient: MockPatientResponse
    emr_system: str
    is_active: bool
    started_at: datetime
    completed_at: Optional[datetime]
    auto_saved_at: Optional[datetime]
    session_data: dict  # Draft data if session active

    # If completed:
    soap_note: Optional[SOAPNoteResponse] = None
    prescriptions: List[PrescriptionResponse] = []
    pathology_orders: List[PathologyOrderResponse] = []
    validation_results: Optional[ValidationSummary] = None
```

**Business Logic**:
1. Validate user owns session OR user is admin
2. Fetch session from database (join with mock_patients)
3. If completed: fetch soap_note, prescriptions, pathology_orders, validation_results
4. Return full session details

**Use Case**: Resume draft session OR review completed session

---

#### Endpoint 5: List Sessions
```python
GET /api/v1/emr/sessions
```

**Query Parameters**:
```python
class SessionListParams(BaseModel):
    is_active: Optional[bool] = None  # Filter active/completed
    emr_system: Optional[Literal["cerner", "epic"]] = None
    specialty: Optional[str] = None
    limit: int = Field(default=20, le=100)
    offset: int = 0
    sort_by: str = "created_at"  # "created_at" | "completed_at"
    sort_order: Literal["asc", "desc"] = "desc"
```

**Response** (200 OK):
```python
class SessionListResponse(BaseModel):
    sessions: List[SessionSummary]
    total_count: int
    limit: int
    offset: int

class SessionSummary(BaseModel):
    session_id: str
    patient_name: str
    patient_specialty: str
    emr_system: str
    is_active: bool
    started_at: datetime
    completed_at: Optional[datetime]
    validation_score: Optional[float] = None  # If completed
```

**Business Logic**:
1. Validate user authenticated
2. Query emr_sessions WHERE user_id = current_user
3. Apply filters (is_active, emr_system, specialty)
4. Apply pagination (limit, offset)
5. Apply sorting
6. Return paginated list

**Use Case**: Session history page, resume draft sessions

---

#### Endpoint 6: Delete Session
```python
DELETE /api/v1/emr/sessions/{session_id}
```

**Response** (204 No Content): Success, no body

**Business Logic**:
1. Validate user owns session
2. Check session is NOT completed (only allow deleting drafts)
3. DELETE from emr_sessions (CASCADE will delete related records)
4. Update user_progress.emr_sessions_total -= 1 (if counted)
5. Return 204 No Content

**Error Responses**:
- 401 Unauthorized
- 404 Not Found
- 409 Conflict: Cannot delete completed session (soft-delete instead)

---

### Technology Stack
- **Framework**: FastAPI 0.109+
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic 2.5+
- **Authentication**: JWT (existing implementation from `/api/v1/auth.py`)
- **Database**: PostgreSQL 15 (existing)
- **Testing**: pytest + pytest-asyncio + httpx

### Integration Points
- **Integrates with**:
  - `/api/v1/auth` (JWT authentication)
  - Database (emr_sessions, mock_patients, user_progress tables)
  - PRD_BACKEND_003 (validation API - async trigger after submit)
- **Consumed by**:
  - Frontend Epic UI (PRD_FRONTEND_001)
  - Frontend Cerner UI (PRD_FRONTEND_002)
  - Dashboard (PRD_FRONTEND_003)

### Security Considerations
- [x] JWT authentication on ALL endpoints
- [x] User authorization (users can only access their own sessions)
- [x] Pydantic input validation (prevent SQL injection, XSS)
- [x] Rate limiting: 100 requests/minute per user (prevent abuse)
- [x] Session limits: Max 5 active sessions per user (prevent resource exhaustion)
- [x] No sensitive data in session_data JSONB (no passwords, API keys)
- [x] Transaction safety (ACID compliance for submit operation)

### Performance Requirements
- **Auto-save (PUT /sessions/{id})**: <200ms p95
- **Start session (POST /sessions/start)**: <500ms p95
- **Submit session (POST /sessions/{id}/submit)**: <1000ms p95 (multi-step transaction)
- **Get session (GET /sessions/{id})**: <300ms p95
- **List sessions (GET /sessions)**: <500ms p95
- **Concurrent sessions**: 100+ users simultaneously without degradation
- **Database queries**: Use indexes from PRD_BACKEND_001 (all <50ms)

---

## L - LOOP (Iterative Development)

### Phase 1: Core API Endpoints (50% of effort, 5-7 hours)
**Goal**: Implement 6 RESTful endpoints with basic functionality

**Tasks**:
1. Create API router file - 30 min
2. Implement POST /sessions/start - 1.5 hours
3. Implement PUT /sessions/{id} (auto-save) - 1 hour
4. Implement POST /sessions/{id}/submit - 2 hours (most complex)
5. Implement GET /sessions/{id} - 45 min
6. Implement GET /sessions (list) - 1 hour
7. Implement DELETE /sessions/{id} - 30 min

**Validation Gate**:
- [ ] All 6 endpoints return 200/204 responses
- [ ] Pydantic schemas validate correctly
- [ ] JWT authentication working
- [ ] Basic smoke tests passing
- [ ] No compilation errors (`uvicorn src.main:app --reload`)

---

### Phase 2: Business Logic & Services (30% of effort, 3-4 hours)
**Goal**: Implement supporting services and database operations

**Tasks**:
1. Create SessionService class - 1 hour
2. Create PatientAssignmentService - 1 hour
3. Create ProgressTrackingService - 1 hour
4. Implement transaction handling (submit endpoint) - 1 hour

**Validation Gate**:
- [ ] SessionService CRUD operations functional
- [ ] PatientAssignmentService returns random patients with filters
- [ ] ProgressTrackingService updates user_progress correctly
- [ ] Submit transaction is atomic (rollback on error)
- [ ] Services unit tested (≥70% coverage)

---

### Phase 3: Testing & Documentation (20% of effort, 2-3 hours)
**Goal**: Production-ready quality and documentation

**Tasks**:
1. Write unit tests for services - 1 hour
2. Write integration tests for endpoints - 1 hour
3. Write OpenAPI documentation - 30 min
4. Performance testing (load test) - 30 min

**Validation Gate**:
- [ ] Unit tests ≥70% coverage
- [ ] Integration tests 100% pass rate
- [ ] All endpoints documented in Swagger/ReDoc
- [ ] Performance targets met (<200ms, <500ms)
- [ ] Load test: 100 concurrent users supported

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create API Router File
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: `/backend/src/api/v1/emr/sessions.py`
- **Dependencies**: None
- **Code**:
  ```python
  from fastapi import APIRouter, Depends, HTTPException, status
  from sqlalchemy.orm import Session
  from typing import List, Optional

  from src.db.session import get_db
  from src.api.dependencies import get_current_user
  from src.schemas.emr import (
      SessionStartRequest, SessionStartResponse,
      SessionUpdateRequest, SessionUpdateResponse,
      SessionSubmitRequest, SessionSubmitResponse,
      SessionDetailResponse, SessionListResponse
  )

  router = APIRouter(prefix="/emr/sessions", tags=["EMR Sessions"])

  # Endpoints will be added here
  ```
- **Acceptance Criteria**:
  - [ ] File created
  - [ ] Router registered in main.py
  - [ ] Imports work (no errors)

**Task 1.2**: Implement POST /sessions/start
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Dependencies**: Task 1.1
- **Code Skeleton**:
  ```python
  @router.post("/start", response_model=SessionStartResponse)
  async def start_session(
      request: SessionStartRequest,
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      # 1. Check user doesn't have >5 active sessions
      active_count = db.query(EMRSession).filter(
          EMRSession.user_id == current_user.id,
          EMRSession.is_active == True
      ).count()

      if active_count >= 5:
          raise HTTPException(
              status_code=status.HTTP_429_TOO_MANY_REQUESTS,
              detail="Maximum 5 concurrent sessions allowed"
          )

      # 2. Get patient (random or OSCE-linked)
      if request.osce_id:
          patient = get_patient_for_osce(db, request.osce_id)
      else:
          patient = get_random_patient(
              db,
              specialty=request.patient_filter.specialty,
              complexity=request.patient_filter.complexity,
              exclude_user_completed=current_user.id if request.patient_filter.exclude_completed else None
          )

      if not patient:
          raise HTTPException(
              status_code=status.HTTP_404_NOT_FOUND,
              detail="No available patients matching criteria"
          )

      # 3. Create session
      session = EMRSession(
          user_id=current_user.id,
          patient_scenario_id=patient.id,
          osce_id=request.osce_id,
          emr_system=request.emr_system,
          is_active=True,
          session_data={}
      )
      db.add(session)

      # 4. Update user progress
      progress = db.query(UserProgress).filter_by(user_id=current_user.id).first()
      progress.emr_sessions_total += 1
      if request.emr_system == "epic":
          progress.emr_epic_sessions += 1
      else:
          progress.emr_cerner_sessions += 1

      db.commit()
      db.refresh(session)

      # 5. Return response
      return SessionStartResponse(
          session_id=str(session.id),
          patient=MockPatientResponse.from_orm(patient),
          emr_system=session.emr_system,
          started_at=session.started_at,
          session_data=session.session_data
      )
  ```
- **Acceptance Criteria**:
  - [ ] Endpoint returns 200 with session + patient data
  - [ ] Validates max 5 active sessions (returns 429 if exceeded)
  - [ ] Handles missing patients (returns 404)
  - [ ] Updates user_progress correctly
  - [ ] Transaction is atomic

**Task 1.3**: Implement PUT /sessions/{id} (Auto-Save)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Dependencies**: Task 1.1
- **Code**:
  ```python
  @router.put("/{session_id}", response_model=SessionUpdateResponse)
  async def update_session(
      session_id: str,
      request: SessionUpdateRequest,
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      # 1. Get session
      session = db.query(EMRSession).filter_by(id=session_id).first()

      if not session:
          raise HTTPException(status_code=404, detail="Session not found")

      # 2. Validate ownership
      if session.user_id != current_user.id:
          raise HTTPException(status_code=401, detail="Not authorized")

      # 3. Validate session is active
      if not session.is_active:
          raise HTTPException(status_code=409, detail="Session already completed")

      # 4. Merge session_data (preserve existing keys)
      existing_data = session.session_data or {}
      existing_data.update(request.session_data)
      session.session_data = existing_data
      session.auto_saved_at = datetime.utcnow()

      db.commit()

      return SessionUpdateResponse(
          session_id=str(session.id),
          auto_saved_at=session.auto_saved_at,
          message="Draft saved successfully"
      )
  ```
- **Acceptance Criteria**:
  - [ ] Returns 200 on success
  - [ ] Merges session_data (doesn't overwrite)
  - [ ] Updates auto_saved_at timestamp
  - [ ] Returns 401 if user doesn't own session
  - [ ] Returns 409 if session already completed
  - [ ] **Performance**: <200ms (measured with time.time())

**Task 1.4**: Implement POST /sessions/{id}/submit
- **Effort**: 2 hours (most complex - multi-step transaction)
- **Owner**: Backend Engineer
- **Dependencies**: Task 1.1
- **Code Structure**:
  ```python
  @router.post("/{session_id}/submit", response_model=SessionSubmitResponse)
  async def submit_session(
      session_id: str,
      request: SessionSubmitRequest,
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      # 1. Validate session ownership and active status
      # 2. BEGIN TRANSACTION (SQLAlchemy automatic)
      # 3. Mark session complete
      # 4. Create emr_soap_notes record
      # 5. Create emr_prescriptions records (loop)
      # 6. Create emr_pathology_orders records (loop)
      # 7. Update user_progress (multiple fields)
      # 8. COMMIT TRANSACTION
      # 9. Queue validation (async - background task)
      # 10. Return success

      try:
          # Implementation details...
          db.commit()
      except Exception as e:
          db.rollback()
          raise HTTPException(status_code=500, detail=str(e))
  ```
- **Acceptance Criteria**:
  - [ ] All database operations in single transaction
  - [ ] Rollback on any error (no partial commits)
  - [ ] Creates SOAP note, prescriptions, pathology orders
  - [ ] Updates user_progress (6 fields minimum)
  - [ ] Returns all created IDs
  - [ ] **Performance**: <1000ms (acceptable for complex operation)

**Task 1.5**: Implement GET /sessions/{id}
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Code**:
  ```python
  @router.get("/{session_id}", response_model=SessionDetailResponse)
  async def get_session(
      session_id: str,
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      session = db.query(EMRSession).filter_by(id=session_id).first()

      if not session:
          raise HTTPException(status_code=404, detail="Session not found")

      if session.user_id != current_user.id:
          raise HTTPException(status_code=401, detail="Not authorized")

      # Join with patient
      patient = db.query(MockPatient).filter_by(id=session.patient_scenario_id).first()

      response_data = {
          "session_id": str(session.id),
          "user_id": str(session.user_id),
          "patient": MockPatientResponse.from_orm(patient),
          "emr_system": session.emr_system,
          "is_active": session.is_active,
          "started_at": session.started_at,
          "completed_at": session.completed_at,
          "auto_saved_at": session.auto_saved_at,
          "session_data": session.session_data
      }

      # If completed, fetch SOAP note, prescriptions, etc.
      if not session.is_active:
          soap_note = db.query(EMRSOAPNote).filter_by(emr_session_id=session.id).first()
          prescriptions = db.query(EMRPrescription).filter_by(emr_session_id=session.id).all()
          pathology_orders = db.query(EMRPathologyOrder).filter_by(emr_session_id=session.id).all()

          response_data.update({
              "soap_note": SOAPNoteResponse.from_orm(soap_note) if soap_note else None,
              "prescriptions": [PrescriptionResponse.from_orm(p) for p in prescriptions],
              "pathology_orders": [PathologyOrderResponse.from_orm(po) for po in pathology_orders]
          })

      return SessionDetailResponse(**response_data)
  ```

**Task 1.6**: Implement GET /sessions (List)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Code**:
  ```python
  @router.get("", response_model=SessionListResponse)
  async def list_sessions(
      is_active: Optional[bool] = None,
      emr_system: Optional[str] = None,
      specialty: Optional[str] = None,
      limit: int = 20,
      offset: int = 0,
      sort_by: str = "created_at",
      sort_order: str = "desc",
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      query = db.query(EMRSession).filter(EMRSession.user_id == current_user.id)

      # Apply filters
      if is_active is not None:
          query = query.filter(EMRSession.is_active == is_active)
      if emr_system:
          query = query.filter(EMRSession.emr_system == emr_system)
      if specialty:
          query = query.join(MockPatient).filter(MockPatient.specialty == specialty)

      # Count total
      total_count = query.count()

      # Apply sorting
      if sort_order == "desc":
          query = query.order_by(getattr(EMRSession, sort_by).desc())
      else:
          query = query.order_by(getattr(EMRSession, sort_by).asc())

      # Apply pagination
      sessions = query.limit(limit).offset(offset).all()

      # Build response
      session_summaries = []
      for session in sessions:
          patient = db.query(MockPatient).filter_by(id=session.patient_scenario_id).first()
          validation_score = None
          if not session.is_active:
              soap_note = db.query(EMRSOAPNote).filter_by(emr_session_id=session.id).first()
              validation_score = soap_note.overall_validation_score if soap_note else None

          session_summaries.append(SessionSummary(
              session_id=str(session.id),
              patient_name=patient.full_name if patient else "Unknown",
              patient_specialty=patient.specialty if patient else "Unknown",
              emr_system=session.emr_system,
              is_active=session.is_active,
              started_at=session.started_at,
              completed_at=session.completed_at,
              validation_score=validation_score
          ))

      return SessionListResponse(
          sessions=session_summaries,
          total_count=total_count,
          limit=limit,
          offset=offset
      )
  ```

**Task 1.7**: Implement DELETE /sessions/{id}
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Code**:
  ```python
  @router.delete("/{session_id}", status_code=204)
  async def delete_session(
      session_id: str,
      db: Session = Depends(get_db),
      current_user: User = Depends(get_current_user)
  ):
      session = db.query(EMRSession).filter_by(id=session_id).first()

      if not session:
          raise HTTPException(status_code=404, detail="Session not found")

      if session.user_id != current_user.id:
          raise HTTPException(status_code=401, detail="Not authorized")

      if not session.is_active:
          raise HTTPException(
              status_code=409,
              detail="Cannot delete completed session. Use soft-delete instead."
          )

      db.delete(session)  # CASCADE will delete related records
      db.commit()

      return Response(status_code=204)
  ```

---

### Phase 2 Tasks

**Task 2.1**: Create SessionService
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/session_service.py`
- **Methods**:
  - `create_session(user_id, patient_id, emr_system, osce_id)`
  - `update_session_data(session_id, session_data)`
  - `complete_session(session_id, soap_note, prescriptions, pathology_orders)`
  - `get_session(session_id)`
  - `list_sessions(user_id, filters, pagination)`
  - `delete_session(session_id)`

**Task 2.2**: Create PatientAssignmentService
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/patient_assignment_service.py`
- **Methods**:
  - `get_random_patient(specialty, complexity, exclude_user_completed)`
  - `get_patient_for_osce(osce_id)`
  - `get_available_specialties()`

**Task 2.3**: Create ProgressTrackingService
- **Effort**: 1 hour
- **File**: `/backend/src/services/emr/progress_tracking_service.py`
- **Methods**:
  - `increment_sessions_total(user_id)`
  - `increment_sessions_completed(user_id, specialty, emr_system)`
  - `update_soap_note_metrics(user_id, score, typing_wpm, completion_time)`
  - `calculate_improvement_percentage(user_id)`

**Task 2.4**: Implement Transaction Handling (Submit)
- **Effort**: 1 hour
- **Focus**: Ensure submit_session is fully atomic
- **Testing**:
  - Simulate database error mid-transaction → verify rollback
  - Verify no orphaned records if any step fails

---

### Phase 3 Tasks

**Task 3.1**: Write Unit Tests for Services
- **Effort**: 1 hour
- **File**: `/backend/tests/test_services/test_session_service.py`
- **Test Cases** (15+ tests):
  - `test_create_session_success()`
  - `test_create_session_max_active_limit()`
  - `test_update_session_data_merge()`
  - `test_complete_session_transaction()`
  - `test_complete_session_rollback_on_error()`
  - `test_get_session_not_found()`
  - `test_list_sessions_pagination()`
  - `test_delete_session_only_drafts()`

**Task 3.2**: Write Integration Tests for Endpoints
- **Effort**: 1 hour
- **File**: `/backend/tests/test_api/test_emr_sessions.py`
- **Test Cases** (20+ tests):
  - `test_start_session_success()`
  - `test_start_session_unauthorized()`
  - `test_start_session_max_active()`
  - `test_update_session_auto_save()`
  - `test_submit_session_complete_flow()`
  - `test_get_session_returns_patient()`
  - `test_list_sessions_filter_by_specialty()`
  - `test_delete_session_draft_only()`

**Task 3.3**: Write OpenAPI Documentation
- **Effort**: 30 min
- **Enhancement**: Add detailed descriptions to all endpoints
- **Code**:
  ```python
  @router.post("/start",
      response_model=SessionStartResponse,
      summary="Start New EMR Practice Session",
      description="""
      Start a new EMR practice session with a randomly assigned patient.

      **Workflow:**
      1. Select EMR system (Cerner PowerChart or Epic EHR)
      2. Optionally filter patients by specialty and complexity
      3. System assigns a random patient matching criteria
      4. Session created with timer started

      **Limits:**
      - Maximum 5 concurrent active sessions per user
      - Patients already completed by user excluded (if flag set)
      """,
      responses={
          200: {"description": "Session started successfully"},
          429: {"description": "Too many active sessions (max 5)"},
          404: {"description": "No available patients matching criteria"}
      }
  )
  async def start_session(...):
      ...
  ```

**Task 3.4**: Performance Testing
- **Effort**: 30 min
- **Tool**: Locust or Apache Bench
- **Test Scenarios**:
  1. 100 concurrent users starting sessions → Measure p95 latency
  2. 100 concurrent users auto-saving → Target <200ms
  3. 50 concurrent users submitting sessions → Target <1000ms
- **Acceptance**:
  - Start session: <500ms p95
  - Auto-save: <200ms p95
  - Submit: <1000ms p95
  - No database connection pool exhaustion

---

### Timeline

| Day | Phase | Tasks | Hours | Deliverable |
|-----|-------|-------|-------|-------------|
| Day 1 AM | Phase 1 | 1.1-1.3 | 3h | Start, auto-save endpoints |
| Day 1 PM | Phase 1 | 1.4 | 2h | Submit endpoint (complex) |
| Day 2 AM | Phase 1 | 1.5-1.7 | 2.5h | Get, list, delete endpoints |
| Day 2 PM | Phase 2 | 2.1-2.4 | 4h | Services + transaction safety |
| Day 3 AM | Phase 3 | 3.1-3.2 | 2h | Unit + integration tests |
| Day 3 PM | Phase 3 | 3.3-3.4 | 1h | Documentation + performance |

**Total**: 2.5-3 days, 10-14 hours effort

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] All 6 endpoints implemented and working
- [ ] POST /sessions/start returns session + patient data
- [ ] PUT /sessions/{id} auto-saves draft data (JSONB merge)
- [ ] POST /sessions/{id}/submit creates SOAP note, prescriptions, pathology orders
- [ ] GET /sessions/{id} returns full session details (with patient)
- [ ] GET /sessions returns paginated list with filters
- [ ] DELETE /sessions/{id} removes draft sessions only
- [ ] User can only access their own sessions (authorization)
- [ ] Max 5 active sessions enforced per user

#### Quality Requirements
- [ ] **Test Coverage**: ≥70% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero-tolerance)
- [ ] **Code Quality**: No linting errors, follows FastAPI patterns
- [ ] **Documentation**: All endpoints in Swagger/ReDoc

#### Performance Requirements
- [ ] **Auto-save**: <200ms p95
- [ ] **Start session**: <500ms p95
- [ ] **Submit session**: <1000ms p95
- [ ] **Get/List sessions**: <500ms p95
- [ ] **Load test**: 100 concurrent users supported

#### Security Requirements
- [ ] **JWT Required**: All endpoints require authentication
- [ ] **Authorization**: Users can only access own sessions
- [ ] **Input Validation**: Pydantic validates all requests
- [ ] **Rate Limiting**: 100 requests/minute per user
- [ ] **Transaction Safety**: Submit is atomic (rollback on error)
- [ ] **No SQL Injection**: All queries parameterized

#### Australian Medical Compliance
- [ ] Supports both Cerner and Epic systems
- [ ] Patient assignment by Australian specialties
- [ ] Progress tracking includes EMR-specific metrics
- [ ] Session data preserves Australian clinical workflow

---

### Testing Requirements

#### Unit Tests (≥70% coverage)
```python
# Test SessionService
def test_create_session_updates_progress():
    """Verify user_progress.emr_sessions_total increments"""
    service = SessionService(db)
    user = create_test_user()
    patient = create_test_patient()

    initial_count = user.progress.emr_sessions_total
    session = service.create_session(user.id, patient.id, "epic", None)

    assert user.progress.emr_sessions_total == initial_count + 1
    assert user.progress.emr_epic_sessions == 1

def test_submit_session_transaction_rollback():
    """Verify rollback on error during submit"""
    service = SessionService(db)
    session = create_test_session()

    # Simulate error mid-transaction
    with patch('db.commit', side_effect=Exception("DB error")):
        with pytest.raises(Exception):
            service.complete_session(session.id, soap_note_data, [], [])

    # Verify no partial commit
    soap_notes = db.query(EMRSOAPNote).filter_by(emr_session_id=session.id).all()
    assert len(soap_notes) == 0
    assert session.is_active == True  # Still active (not marked complete)
```

#### Integration Tests (100% endpoint coverage)
```python
def test_api_start_session_success(client, auth_headers):
    """Test POST /sessions/start happy path"""
    response = client.post("/api/v1/emr/sessions/start", json={
        "emr_system": "epic",
        "patient_filter": {"specialty": "Cardiology", "complexity": "Moderate"}
    }, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "patient" in data
    assert data["patient"]["specialty"] == "Cardiology"
    assert data["emr_system"] == "epic"

def test_api_auto_save_performance(client, auth_headers, test_session):
    """Test PUT /sessions/{id} latency <200ms"""
    import time

    start = time.time()
    response = client.put(f"/api/v1/emr/sessions/{test_session.id}", json={
        "session_data": {"draft_subjective": "Patient presents with..."}
    }, headers=auth_headers)
    elapsed = (time.time() - start) * 1000

    assert response.status_code == 200
    assert elapsed < 200, f"Auto-save took {elapsed}ms (target: <200ms)"
```

#### E2E Test (Full Workflow)
```python
def test_complete_emr_session_workflow(client, auth_headers):
    """Test: Start → Auto-save → Submit → Get → List"""

    # 1. Start session
    start_response = client.post("/api/v1/emr/sessions/start", json={
        "emr_system": "epic",
        "patient_filter": {"specialty": "Emergency Medicine"}
    }, headers=auth_headers)
    assert start_response.status_code == 200
    session_id = start_response.json()["session_id"]

    # 2. Auto-save draft
    auto_save_response = client.put(f"/api/v1/emr/sessions/{session_id}", json={
        "session_data": {"draft_subjective": "65M with chest pain x 2 hours..."}
    }, headers=auth_headers)
    assert auto_save_response.status_code == 200

    # 3. Submit session
    submit_response = client.post(f"/api/v1/emr/sessions/{session_id}/submit", json={
        "soap_note": {
            "subjective": "65-year-old male presenting with central chest pain...",
            "objective": "BP 152/88, HR 92, RR 20, Temp 37.1, SpO2 95%...",
            "assessment": "Likely Acute Coronary Syndrome (NSTEMI)...",
            "plan": "ECG, Troponin, Aspirin 300mg PO stat, Cardiology consult..."
        },
        "prescriptions": [
            {"medication_name": "Aspirin", "dose": "300mg", "frequency": "stat",
             "route": "PO", "quantity": 1, "repeats": 0, "indication": "ACS"}
        ],
        "pathology_orders": [
            {"test_name": "Troponin I", "urgency": "Urgent",
             "clinical_indication": "Suspected ACS"}
        ],
        "completion_time_seconds": 480,
        "typing_wpm": 45
    }, headers=auth_headers)
    assert submit_response.status_code == 200
    soap_note_id = submit_response.json()["soap_note_id"]

    # 4. Get completed session
    get_response = client.get(f"/api/v1/emr/sessions/{session_id}", headers=auth_headers)
    assert get_response.status_code == 200
    data = get_response.json()
    assert data["is_active"] == False
    assert data["soap_note"]["subjective"].startswith("65-year-old male")
    assert len(data["prescriptions"]) == 1
    assert len(data["pathology_orders"]) == 1

    # 5. List sessions (should include completed session)
    list_response = client.get("/api/v1/emr/sessions?is_active=false", headers=auth_headers)
    assert list_response.status_code == 200
    assert list_response.json()["total_count"] >= 1
```

---

### Documentation Deliverables

#### 1. API Documentation (`docs/EMR_SESSION_API.md`)
- Overview of session lifecycle
- Endpoint reference (6 endpoints)
- Request/response examples
- Error handling guide
- Performance characteristics

#### 2. OpenAPI Spec (Auto-generated)
- Access via `http://localhost:8001/docs` (Swagger UI)
- All endpoints with detailed descriptions
- Request/response schemas
- Example payloads

#### 3. Developer Guide (`docs/EMR_SESSION_DEVELOPMENT.md`)
- How to add new endpoints
- Service layer architecture
- Testing guidelines
- Performance optimization tips

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All tests passing (100% pass rate)
- [ ] Code reviewed and approved
- [ ] Database migration (PRD_BACKEND_001) completed
- [ ] Performance benchmarks met
- [ ] Security scan passes (Bandit 0 HIGH)

#### Deployment
- [ ] Merge to main branch
- [ ] Deploy backend (Docker/Railway)
- [ ] Run smoke tests in production
- [ ] Monitor logs for errors

#### Post-Deployment
- [ ] API response times within targets
- [ ] No error spikes in logs
- [ ] 100 concurrent user load test passes
- [ ] Frontend integration working

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ All 6 endpoints implemented and working
2. ✅ Unit tests ≥70% coverage, 100% pass rate
3. ✅ Integration tests cover all endpoints
4. ✅ Performance targets met (<200ms auto-save, <500ms start, <1000ms submit)
5. ✅ Load test: 100 concurrent users supported
6. ✅ Authorization working (users can only access own sessions)
7. ✅ Transaction safety verified (submit rollback on error)
8. ✅ OpenAPI documentation complete
9. ✅ Security scan passes (0 HIGH/CRITICAL)
10. ✅ Frontend successfully integrates (can start/save/submit sessions)

**Sign-off Required From**:
- [ ] Backend Engineer (implementation complete)
- [ ] PM Coordinator (requirements met)
- [ ] Security Expert (authentication + authorization verified)
- [ ] Testing QA (test coverage + pass rate validated)
- [ ] Frontend Engineer (API contract confirmed)

---

## 📎 Appendices

### Appendix A: Complete Request/Response Examples

**Start Session Request**:
```json
POST /api/v1/emr/sessions/start
{
  "emr_system": "epic",
  "patient_filter": {
    "specialty": "Cardiology",
    "complexity": "Moderate",
    "exclude_completed": true
  },
  "osce_id": null
}
```

**Start Session Response**:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "mrn": "12345678",
    "full_name": "William Thompson",
    "age": 65,
    "gender": "Male",
    "allergies": ["Penicillin"],
    "current_medications": [
      {"name": "Metformin", "dose": "1000mg", "frequency": "BD"}
    ],
    "vital_signs": {
      "BP": "152/88",
      "HR": 92,
      "RR": 20,
      "Temp": 37.1,
      "SpO2": 95
    },
    "presenting_complaint": "Chest pain and shortness of breath for 2 hours",
    "clinical_scenario": "65-year-old male presenting to ED with...",
    "specialty": "Cardiology",
    "complexity_level": "Moderate"
  },
  "emr_system": "epic",
  "started_at": "2026-02-16T10:30:00Z",
  "session_data": {}
}
```

**Auto-Save Request**:
```json
PUT /api/v1/emr/sessions/550e8400-e29b-41d4-a716-446655440000
{
  "session_data": {
    "draft_subjective": "Patient presents with central chest pain radiating to left arm. Pain started 2 hours ago...",
    "current_tab": "objective",
    "last_edit_time": "2026-02-16T10:35:00Z",
    "word_count": 145
  }
}
```

**Submit Request**:
```json
POST /api/v1/emr/sessions/550e8400-e29b-41d4-a716-446655440000/submit
{
  "soap_note": {
    "subjective": "65-year-old male presenting with central chest pain radiating to left arm. Pain described as 'tight, heavy feeling' 7/10 severity, started 2 hours ago. Associated shortness of breath and diaphoresis. Patient has history of Type 2 Diabetes, Hypertension, ex-smoker (30 pack-years, quit 2020). Family history of CAD (father died of MI at age 60). Denies nausea, vomiting. Pain not relieved by rest.",
    "objective": "BP 152/88, HR 92, RR 20, Temp 37.1°C, SpO2 95% on RA. Patient appears diaphoretic and uncomfortable. Cardiovascular: Regular rhythm, no murmurs. Respiratory: Clear breath sounds bilaterally. Abdomen: Soft, non-tender. ECG: Sinus rhythm, HR 92, T-wave inversion in V4-V6, no ST elevation. Troponin I: 0.45 ng/mL (elevated).",
    "assessment": "Likely Acute Coronary Syndrome (NSTEMI) based on:  \n- Typical cardiac chest pain radiating to left arm  \n- Risk factors: T2DM, HTN, ex-smoker, family history  \n- ECG changes: T-wave inversion in lateral leads  \n- Elevated Troponin I (0.45)  \n\nDifferential diagnoses: Unstable Angina, STEMI (less likely - no ST elevation), Aortic Dissection (less likely - no tearing pain), Pulmonary Embolism.",
    "plan": "1. Investigations:  \n- Serial troponins (at 0, 3, 6 hours)  \n- FBC, UEC, LFT, Lipid profile  \n- CXR (exclude other causes)  \n\n2. Medications:  \n- Aspirin 300mg PO stat (already administered)  \n- Ticagrelor 180mg PO stat  \n- Atorvastatin 80mg PO daily  \n- Morphine 2.5-5mg IV PRN for pain  \n- GTN spray PRN  \n\n3. Referrals:  \n- Urgent Cardiology consult  \n- Consider PCI if ongoing ischemia  \n\n4. Monitoring:  \n- Continuous ECG monitoring  \n- 4-hourly vital signs  \n- Nil by mouth until reviewed by cardiology  \n\n5. Safety netting:  \n- If chest pain worsens or new ST changes → activate cath lab  \n- Patient educated about ACS, medication compliance",
    "note_type": "Progress Note"
  },
  "prescriptions": [
    {
      "medication_name": "Aspirin",
      "dose": "300mg",
      "frequency": "stat",
      "route": "PO",
      "quantity": 1,
      "repeats": 0,
      "indication": "Acute Coronary Syndrome"
    },
    {
      "medication_name": "Ticagrelor",
      "dose": "90mg",
      "frequency": "BD",
      "route": "PO",
      "quantity": 60,
      "repeats": 2,
      "indication": "Acute Coronary Syndrome"
    }
  ],
  "pathology_orders": [
    {
      "test_name": "Troponin I (serial)",
      "urgency": "Urgent",
      "clinical_indication": "Suspected NSTEMI, serial troponins at 0, 3, 6 hours"
    },
    {
      "test_name": "FBC",
      "urgency": "Routine",
      "clinical_indication": "Baseline investigations for ACS admission",
      "is_panel": false
    }
  ],
  "completion_time_seconds": 480,
  "typing_wpm": 45
}
```

### Appendix B: Error Response Format
```json
{
  "detail": "Maximum 5 concurrent sessions allowed",
  "status_code": 429,
  "error_code": "EMR_MAX_SESSIONS",
  "timestamp": "2026-02-16T10:30:00Z"
}
```

### Appendix C: Related PRDs
- **Depends On**: PRD_BACKEND_001 (Database Migration)
- **Blocks**:
  - PRD_FRONTEND_001 (Epic UI - needs session API)
  - PRD_FRONTEND_002 (Cerner UI - needs session API)
  - PRD_FRONTEND_003 (Dashboard - needs session list API)
- **Related**:
  - PRD_BACKEND_003 (Validation API - triggered after submit)
  - PRD_BACKEND_004 (OSCE Converter - generates patient data)

---

**Document Status**: Draft
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending
**Version**: 1.0
