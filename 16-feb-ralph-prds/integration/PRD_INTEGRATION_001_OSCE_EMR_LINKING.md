# PRD: OSCE-EMR Integration & Dual Scoring System

**PRD ID**: PRD_INTEGRATION_001_OSCE_EMR_LINKING
**Category**: Integration
**Priority**: P1-High (Enhances core learning workflow)
**Estimated Effort**: 9-12 hours
**Dependencies**: 
- PRD_BACKEND_002 (EMR Session API - MUST complete first)
- Existing OSCE system (`/api/v1/osces/*`)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** medical student practicing for the AMC Clinical Examination
**I want** to document clinical cases in the EMR system immediately after completing OSCE stations
**So that** I can develop both clinical examination skills (OSCE) AND professional documentation skills (EMR) in an integrated workflow that reflects real clinical practice

### Business Context

In real Australian hospital practice, clinicians must:
1. **Perform clinical examinations** (history-taking, physical exam, communication)
2. **Document encounters** in hospital EMR systems (Cerner PowerChart, Epic EHR)
3. **Be assessed** on BOTH clinical skills AND documentation quality

Currently, the SkillBridge system has **two separate practice modes**:
- **OSCE Practice**: Clinical examination skills (history-taking, physical exam) scored 0-15 marks (AMC format)
- **EMR Practice**: Documentation skills (SOAP notes, prescriptions) validated separately

**The Problem**: Students practice these skills in isolation, missing the critical connection between clinical assessment and documentation.

**The Solution**: OSCE-EMR Integration creates a unified workflow:

```
1. Student completes OSCE station (history-taking, physical exam)
   ↓
2. OSCE scored (0-15 marks on clinical skills)
   ↓
3. PROMPT: "Document this case in EMR?" (Optional)
   ↓
4. If YES: Launch EMR session with same patient data
   ↓
5. Student writes SOAP note, orders investigations, prescribes medications
   ↓
6. EMR submission validated (0-100 score on documentation quality)
   ↓
7. DUAL SCORE displayed:
   - Clinical Score: 12/15 (80%)
   - Documentation Score: 85/100 (85%)
   - Combined Score: 82% (weighted: 60% clinical + 40% documentation)
   ↓
8. Progress tracked: OSCE-EMR linked completions, dual score averages
```

### Success Metrics
- **Integration Adoption**: 70%+ of OSCE completions trigger EMR documentation
- **Combined Score Average**: ≥75% after 20 linked sessions
- **Clinical-Documentation Correlation**: Students with high OSCE scores (≥12/15) achieve ≥80% EMR scores
- **Time to Document**: Students complete EMR documentation in <10 minutes after OSCE
- **User Satisfaction**: 85%+ students report integrated workflow "very helpful" for exam preparation
- **Performance Target**: OSCE → EMR session creation <500ms

### Scope

**In Scope**:
1. **OSCE → EMR Linking**
   - Link `emr_sessions.osce_id` to `osces.id`
   - Automatically populate EMR patient from OSCE `patient_instructions`
   - Pass clinical scenario, vital signs, presenting complaint to EMR
   - Track which OSCEs require documentation (`requires_documentation` flag)

2. **Dual Scoring System**
   - OSCE clinical score (0-15, from existing rubric)
   - EMR documentation score (0-100, from validation API)
   - Combined score calculation: **60% clinical + 40% documentation**
   - Pass threshold: Combined score ≥75% (reflecting AMC pass standard ~60% + buffer)

3. **Workflow Integration**
   - POST `/api/v1/osces/{osce_id}/start-emr-session` endpoint
   - GET `/api/v1/osces/{osce_id}/results` enhanced with EMR scores
   - Frontend: "Document this case" button on OSCE results page
   - Frontend: Dual score breakdown visualization (clinical + EMR)

4. **Progress Tracking**
   - New user_progress fields:
     - `osce_emr_linked_completions` (count of linked sessions)
     - `osce_emr_avg_combined_score` (running average)
     - `osce_emr_specialty_scores` (JSONB: scores by specialty)
   - Dashboard analytics: "Clinical + Documentation Performance"

5. **Data Flow**
   - OSCE `patient_instructions` → MockPatient transformation
   - OSCE `rubric` → EMR validation criteria alignment
   - OSCE `specialty` → EMR session specialty matching

**Out of Scope** (Future Phases):
- Real-time concurrent documentation (student types while video plays)
- OSCE video recording with timestamp-linked documentation
- Multi-student collaborative OSCE-EMR sessions
- Automated MockPatient generation from OSCE data (handled by separate OSCE Converter PRD)
- EMR documentation embedded in OSCE timer (Phase 2 feature)

---

## A - ARCHITECTURE (How)

### Technical Approach

Extend existing OSCE API (`/backend/src/api/v1/osces.py`) with EMR integration endpoints. Use the existing EMR Session API (`PRD_BACKEND_002`) to create sessions linked to OSCE stations. Transform OSCE `patient_instructions` (text) into structured `MockPatient` data for EMR UI. Calculate dual scores by combining OSCE rubric scores (0-15) with EMR validation scores (0-100), weighted 60/40.

### System Design

#### Component Diagram
```
┌─────────────────────────────────────────────────────────────────────┐
│                     Frontend (React + MUI)                           │
│                                                                       │
│  ┌────────────────────┐         ┌────────────────────────────────┐  │
│  │  OSCEPracticePage  │────────►│  OSCEResultsPage (ENHANCED)    │  │
│  │  - Timer           │         │  - Clinical score (0-15)       │  │
│  │  - Instructions    │         │  - "Document this case" button │  │
│  │  - Self-scoring    │         │  - EMR session launcher        │  │
│  └────────────────────┘         └────────────┬───────────────────┘  │
│                                               │                       │
│                                               │ Click "Document"      │
│                                               ▼                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  EMRSessionFromOSCE (NEW COMPONENT)                          │   │
│  │  - Pre-populated patient from OSCE data                      │   │
│  │  - Shows OSCE context (clinical scenario, vitals)            │   │
│  │  - Epic/Cerner UI selection                                  │   │
│  │  - Submit returns to OSCE results with dual score            │   │
│  └──────────────────────┬───────────────────────────────────────┘   │
│                         │                                             │
│                         │ Submit EMR                                  │
│                         ▼                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  DualScoreCard (NEW COMPONENT)                               │   │
│  │  - Clinical score: 12/15 (80%)    [Green progress bar]      │   │
│  │  - EMR score: 85/100 (85%)        [Blue progress bar]       │   │
│  │  - Combined: 82% (60%×80% + 40%×85%) [Gold progress bar]    │   │
│  │  - Pass/Fail badge (≥75% = Pass)                             │   │
│  │  - Detailed feedback links                                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────────┘
                         │ HTTP/JSON (JWT Auth)
                         ▼
┌─────────────────────────────────────────────────────────────────────┐
│              FastAPI Backend (Port 8001)                             │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  /api/v1/osces/* (EXISTING - ENHANCED)                       │   │
│  │  - GET    /osces/{id}/results  [ENHANCED: add EMR scores]   │   │
│  │  - POST   /osces/{id}/start-emr-session  [NEW]              │   │
│  │  - GET    /osces/{id}/dual-score  [NEW]                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │  /api/v1/emr/sessions/* (FROM PRD_BACKEND_002)              │   │
│  │  - POST   /sessions/start  [USE with osce_id parameter]     │   │
│  │  - POST   /sessions/{id}/submit  [ENHANCED: update OSCE]    │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │     Integration Services (NEW)                               │   │
│  │  - OSCEToPatientTransformer: OSCE → MockPatient             │   │
│  │  - DualScoreCalculator: Weighted scoring (60/40)            │   │
│  │  - LinkedProgressTracker: Update user_progress              │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                         │                                             │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │     Database Models (ENHANCED)                               │   │
│  │  - emr_sessions.osce_id (FK to osces.id)  [EXISTING]       │   │
│  │  - osces.requires_documentation (BOOLEAN)  [NEW COLUMN]     │   │
│  │  - osces.documentation_weight (NUMERIC)  [NEW COLUMN]       │   │
│  │  - user_progress.osce_emr_* columns  [NEW COLUMNS]          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└────────────────────────┬──────────────────────────────────────────┘
                         │
┌────────────────────────▼──────────────────────────────────────────┐
│              PostgreSQL Database                                   │
│  - osces (enhanced with documentation flags)                       │
│  - emr_sessions (osce_id link)                                     │
│  - user_progress (OSCE-EMR metrics)                                │
└────────────────────────────────────────────────────────────────────┘
```

#### Data Flow: Complete Integration Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: OSCE Station Completion                                │
└─────────────────────────────────────────────────────────────────┘
1. Student completes OSCE (8-minute station)
   ↓
2. Student self-scores using AMC rubric (0-3 marks × 5 categories)
   ↓
3. POST /api/v1/osces/{osce_id}/complete-station
   {
     "scores": {"history_examination": 3, "clinical_reasoning": 2, ...},
     "time_taken_seconds": 480,
     "self_reflection": "Forgot to ask about family history..."
   }
   ↓
4. Backend: Calculate total_score = sum(scores) = 12/15
   Backend: Update OSCE attempt, user_progress
   Backend: Return {total_score: 12, passed: true, rubric: {...}}
   ↓
5. Frontend: Display OSCE results
   - Clinical Score: 12/15 (80%) ✓ Pass
   - Areas for improvement: clinical_reasoning (scored 2/3)
   - Rubric for self-review

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: EMR Documentation Trigger (NEW)                        │
└─────────────────────────────────────────────────────────────────┘
6. Frontend checks: Does OSCE require documentation?
   GET /api/v1/osces/{osce_id} → osce.requires_documentation = true
   ↓
7. Frontend displays: "Document this case in EMR?" button
   ↓
8. User clicks "Yes, document this case"
   ↓
9. Frontend: POST /api/v1/osces/{osce_id}/start-emr-session
   {
     "emr_system": "epic"  // User's preference
   }
   ↓
10. Backend: OSCEToPatientTransformer
    - Parse OSCE patient_instructions (text) → Extract demographics
    - Extract vital_signs from OSCE data
    - Extract presenting_complaint
    - Create/retrieve MockPatient record
    ↓
11. Backend: Create EMR session (using PRD_BACKEND_002 API)
    session = create_emr_session(
      user_id=current_user.id,
      patient_id=transformed_patient.id,
      emr_system="epic",
      osce_id=osce_id  // LINK TO OSCE
    )
    ↓
12. Backend: Return session + patient
    {
      "session_id": "uuid",
      "patient": {...full patient data...},
      "emr_system": "epic",
      "osce_context": {
        "osce_id": "osce-123",
        "clinical_scenario": "65M chest pain...",
        "station_title": "Acute Coronary Syndrome History",
        "specialty": "Cardiology"
      }
    }
    ↓
13. Frontend: Navigate to EMR UI (Epic or Cerner)
    - Display patient demographics
    - Show OSCE context banner: "Documenting OSCE: Acute Coronary Syndrome History"
    - Pre-populate patient vitals, medications, allergies
    - Student writes SOAP note

┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: EMR Submission & Dual Score (NEW)                      │
└─────────────────────────────────────────────────────────────────┘
14. Student completes SOAP note, prescriptions, pathology orders
    ↓
15. Student clicks "Submit for Validation"
    ↓
16. Frontend: POST /api/v1/emr/sessions/{session_id}/submit
    {
      "soap_note": {...},
      "prescriptions": [...],
      "pathology_orders": [...],
      "completion_time_seconds": 540
    }
    ↓
17. Backend: Standard EMR submission (PRD_BACKEND_002)
    - Mark session complete
    - Create emr_soap_notes record
    - Trigger validation (AI analysis)
    - Update user_progress.emr_* counters
    ↓
18. Backend: OSCE-EMR Linking (NEW)
    - Retrieve linked OSCE attempt (via session.osce_id)
    - Wait for validation completion (or poll)
    - Calculate dual score:
      
      osce_score_normalized = (osce_total_score / 15) × 100  // 12/15 → 80%
      emr_score = validation_result.overall_score           // 85/100
      
      combined_score = (osce_score_normalized × 0.6) + (emr_score × 0.4)
                     = (80 × 0.6) + (85 × 0.4)
                     = 48 + 34
                     = 82%
      
      passed = combined_score >= 75
    ↓
19. Backend: Update user_progress (NEW)
    progress.osce_emr_linked_completions += 1
    progress.osce_emr_avg_combined_score = running_average(82%)
    progress.osce_emr_specialty_scores["Cardiology"].append(82)
    ↓
20. Backend: Return dual score result
    {
      "osce_score": 80,          // Normalized to 0-100
      "emr_score": 85,
      "combined_score": 82,
      "passed": true,            // ≥75%
      "breakdown": {
        "clinical_weight": 60,
        "documentation_weight": 40,
        "clinical_contribution": 48,
        "documentation_contribution": 34
      },
      "feedback_summary": "Strong clinical assessment. EMR documentation excellent."
    }
    ↓
21. Frontend: Navigate back to OSCE results page
    Display DualScoreCard component:
    
    ┌──────────────────────────────────────────────┐
    │  OSCE + EMR Performance                      │
    ├──────────────────────────────────────────────┤
    │  Clinical Score (60% weight)                 │
    │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░  12/15 (80%)          │
    │                                              │
    │  Documentation Score (40% weight)            │
    │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░  85/100 (85%)         │
    │                                              │
    │  Combined Score                              │
    │  ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░  82% ✓ PASS           │
    │                                              │
    │  [View Clinical Feedback]  [View EMR Feedback]│
    └──────────────────────────────────────────────┘
```

### API Endpoints Specification

#### Endpoint 1: Start EMR Session from OSCE (NEW)
```python
POST /api/v1/osces/{osce_id}/start-emr-session
```

**Request Body**:
```python
class OSCEEMRStartRequest(BaseModel):
    emr_system: Literal["cerner", "epic"]
    # Note: patient_filter not needed - patient derived from OSCE
```

**Response** (200 OK):
```python
class OSCEEMRStartResponse(BaseModel):
    session_id: str
    patient: MockPatientResponse  # Transformed from OSCE data
    emr_system: str
    osce_context: OSCEContext
    started_at: datetime

class OSCEContext(BaseModel):
    osce_id: str
    station_title: str
    specialty: str
    clinical_scenario: str  # From patient_instructions
    time_limit_minutes: int  # For EMR documentation (e.g., 10 min)
```

**Business Logic**:
1. Validate OSCE exists and user has completed it (has OSCEAttempt record)
2. Check OSCE requires_documentation = true
3. Transform OSCE data → MockPatient:
   ```python
   def transform_osce_to_patient(osce: OSCE) -> MockPatient:
       # Parse patient_instructions (text) to extract:
       # - Demographics (age, gender from scenario text)
       # - Presenting complaint (from candidate_instructions)
       # - Vital signs (if mentioned in patient_instructions)
       # - Medical history (if mentioned)
       # Return structured MockPatient object
   ```
4. Create EMR session (call PRD_BACKEND_002 API internally):
   ```python
   session = create_emr_session(
       user_id=current_user.id,
       patient_id=patient.id,
       emr_system=request.emr_system,
       osce_id=osce_id  # CRITICAL: Link session to OSCE
   )
   ```
5. Return session + patient + OSCE context

**Error Responses**:
- 404 Not Found: OSCE doesn't exist
- 403 Forbidden: User hasn't completed this OSCE yet
- 400 Bad Request: OSCE doesn't require documentation (requires_documentation=false)
- 409 Conflict: User already has active EMR session for this OSCE

**Example Request/Response**:
```json
POST /api/v1/osces/42/start-emr-session
{
  "emr_system": "epic"
}

Response (200 OK):
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "patient": {
    "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
    "mrn": "MRN12345678",
    "full_name": "John Smith",
    "age": 65,
    "gender": "Male",
    "allergies": ["Penicillin"],
    "current_medications": [
      {"name": "Metformin", "dose": "1000mg", "frequency": "BD"}
    ],
    "vital_signs": {
      "BP": "152/88", "HR": 92, "RR": 20, "Temp": 37.1, "SpO2": 95
    },
    "presenting_complaint": "Central chest pain for 2 hours",
    "specialty": "Cardiology"
  },
  "emr_system": "epic",
  "osce_context": {
    "osce_id": "OSCE-CARD-001",
    "station_title": "Acute Coronary Syndrome - History Taking",
    "specialty": "Cardiology",
    "clinical_scenario": "65-year-old male presenting to ED with chest pain radiating to left arm...",
    "time_limit_minutes": 10
  },
  "started_at": "2026-02-16T14:30:00Z"
}
```

---

#### Endpoint 2: Get OSCE Results with EMR Scores (ENHANCED)
```python
GET /api/v1/osces/{osce_id}/results
```

**Query Parameters**:
```python
attempt_id: Optional[int] = None  # If not provided, get latest attempt
```

**Response** (200 OK - ENHANCED):
```python
class OSCEResultsResponse(BaseModel):
    # Existing OSCE fields
    osce_id: str
    station_title: str
    attempt_number: int
    clinical_score: int  # 0-15 (raw OSCE score)
    clinical_score_percentage: float  # Normalized to 0-100
    passed_clinical: bool  # clinical_score >= 9 (60%)
    scores: Dict[str, int]  # Category breakdown
    time_taken_seconds: int
    rubric: dict  # Full AMC rubric for review
    areas_for_improvement: List[str]
    
    # NEW: EMR Integration fields
    emr_session_id: Optional[str] = None
    emr_score: Optional[float] = None  # 0-100 (from validation)
    combined_score: Optional[float] = None  # Weighted average
    passed_combined: Optional[bool] = None  # combined >= 75%
    dual_score_breakdown: Optional[DualScoreBreakdown] = None
    emr_feedback_summary: Optional[str] = None

class DualScoreBreakdown(BaseModel):
    clinical_weight: float = 60.0  # %
    documentation_weight: float = 40.0  # %
    clinical_contribution: float  # clinical_score_percentage × 0.6
    documentation_contribution: float  # emr_score × 0.4
    total: float  # Sum of contributions
    pass_threshold: float = 75.0
```

**Business Logic**:
1. Get OSCE attempt (latest or by attempt_id)
2. If attempt has linked EMR session (via emr_sessions.osce_id):
   - Retrieve EMR session
   - Get validation results (emr_soap_notes.overall_validation_score)
   - Calculate dual score:
     ```python
     clinical_normalized = (attempt.total_score / 15) * 100
     emr_score = soap_note.overall_validation_score
     combined = (clinical_normalized * 0.6) + (emr_score * 0.4)
     ```
3. Return results with dual scoring if EMR session exists

**Example Response**:
```json
GET /api/v1/osces/42/results

{
  "osce_id": "OSCE-CARD-001",
  "station_title": "Acute Coronary Syndrome - History Taking",
  "attempt_number": 1,
  "clinical_score": 12,
  "clinical_score_percentage": 80.0,
  "passed_clinical": true,
  "scores": {
    "history_examination": 3,
    "clinical_reasoning": 2,
    "communication": 3,
    "patient_safety": 2,
    "professionalism": 2
  },
  "time_taken_seconds": 480,
  "areas_for_improvement": ["clinical_reasoning"],
  
  // NEW EMR fields
  "emr_session_id": "550e8400-e29b-41d4-a716-446655440000",
  "emr_score": 85.0,
  "combined_score": 82.0,
  "passed_combined": true,
  "dual_score_breakdown": {
    "clinical_weight": 60.0,
    "documentation_weight": 40.0,
    "clinical_contribution": 48.0,  // 80 × 0.6
    "documentation_contribution": 34.0,  // 85 × 0.4
    "total": 82.0,
    "pass_threshold": 75.0
  },
  "emr_feedback_summary": "Excellent SOAP note structure. Minor terminology issues corrected."
}
```

---

#### Endpoint 3: Get Dual Score Summary (NEW)
```python
GET /api/v1/osces/{osce_id}/dual-score
```

**Purpose**: Lightweight endpoint for dashboard analytics (doesn't return full rubric)

**Response** (200 OK):
```python
class DualScoreSummary(BaseModel):
    osce_id: str
    station_title: str
    attempts_count: int
    latest_attempt: DualScoreAttempt

class DualScoreAttempt(BaseModel):
    attempt_number: int
    clinical_score: float  # 0-100 (normalized)
    emr_score: Optional[float]
    combined_score: Optional[float]
    passed: bool
    completed_at: datetime
```

---

### Database Schema Changes

#### Table: `osces` (ALTER)
```sql
-- Add documentation requirement flags
ALTER TABLE osces 
ADD COLUMN IF NOT EXISTS requires_documentation BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS documentation_weight NUMERIC(3,2) DEFAULT 0.40;

-- Add index for filtering OSCEs that require documentation
CREATE INDEX IF NOT EXISTS idx_osces_requires_documentation 
ON osces(requires_documentation) WHERE requires_documentation = TRUE;

-- Update existing OSCEs (mark clinical-heavy OSCEs as requiring documentation)
UPDATE osces 
SET requires_documentation = TRUE
WHERE station_type IN ('history_taking', 'physical_examination', 'emergency_scenario');

COMMENT ON COLUMN osces.requires_documentation IS 
'Flag indicating if this OSCE station requires EMR documentation practice';

COMMENT ON COLUMN osces.documentation_weight IS 
'Weight of documentation score in combined scoring (default 0.40 = 40%)';
```

#### Table: `user_progress` (ALTER)
```sql
-- Add OSCE-EMR integration metrics
ALTER TABLE user_progress 
ADD COLUMN IF NOT EXISTS osce_emr_linked_completions INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS osce_emr_avg_combined_score NUMERIC(5,2),
ADD COLUMN IF NOT EXISTS osce_emr_specialty_scores JSONB DEFAULT '{}'::jsonb;

-- Add index for querying by linked completions
CREATE INDEX IF NOT EXISTS idx_user_progress_osce_emr_linked 
ON user_progress(osce_emr_linked_completions);

-- Add index for JSONB specialty scores
CREATE INDEX IF NOT EXISTS idx_user_progress_osce_emr_specialty_scores 
ON user_progress USING GIN (osce_emr_specialty_scores);

COMMENT ON COLUMN user_progress.osce_emr_linked_completions IS 
'Count of OSCE stations completed with EMR documentation';

COMMENT ON COLUMN user_progress.osce_emr_avg_combined_score IS 
'Running average of combined scores (clinical + documentation weighted)';

COMMENT ON COLUMN user_progress.osce_emr_specialty_scores IS 
'JSONB: {"Cardiology": [82, 85, 78], "Respiratory": [90, 88]} - combined scores by specialty';
```

#### Table: `emr_sessions` (NO CHANGES - Already has osce_id)
```sql
-- Existing column from PRD_BACKEND_001:
-- osce_id VARCHAR(100) REFERENCES osces(osce_id)  ✓ Already exists

-- Verify foreign key exists
SELECT 
    constraint_name, 
    constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'emr_sessions' AND constraint_type = 'FOREIGN KEY';

-- If missing, add:
ALTER TABLE emr_sessions 
ADD CONSTRAINT fk_emr_sessions_osce 
FOREIGN KEY (osce_id) REFERENCES osces(osce_id) ON DELETE SET NULL;
```

---

### Technology Stack
- **Backend**: Python 3.11 + FastAPI (existing)
- **Frontend**: React 18 + TypeScript + MUI (existing)
- **Database**: PostgreSQL 15 (existing)
- **ORM**: SQLAlchemy 2.0 (existing)
- **Validation**: Pydantic 2.5 (existing)
- **NEW Services**:
  - `OSCEToPatientTransformer`: Transform OSCE text → MockPatient
  - `DualScoreCalculator`: Weighted scoring logic
  - `LinkedProgressTracker`: Update user_progress metrics

### Integration Points

**Integrates with**:
- `/api/v1/osces/*` (Existing OSCE API)
- `/api/v1/emr/sessions/*` (PRD_BACKEND_002 EMR Session API)
- Database (osces, emr_sessions, user_progress tables)

**Consumed by**:
- Frontend: OSCEResultsPage, EMRSessionFromOSCE, DualScoreCard components
- Dashboard: Analytics showing OSCE-EMR performance correlation

**Depends on**:
- PRD_BACKEND_002 (EMR Session API MUST complete first)
- Existing OSCE completion workflow

### Security Considerations
- [x] JWT authentication on all new endpoints
- [x] Authorization: Users can only access their own OSCE attempts + EMR sessions
- [x] Validate OSCE completion before allowing EMR session creation
- [x] Prevent duplicate EMR sessions for same OSCE attempt
- [x] OSCE-EMR link integrity (foreign key constraints)
- [x] Audit trail: Track when OSCE → EMR linking occurred

### Performance Requirements
- **Start EMR from OSCE**: <500ms (patient transformation + session creation)
- **Get dual score results**: <300ms (includes score calculation)
- **OSCE data → MockPatient transformation**: <100ms (text parsing)
- **No impact on existing OSCE performance**: Dual scoring is additive, not blocking

---

## L - LOOP (Iterative Development)

### Phase 1: Backend Integration (40% of effort, 4-5 hours)
**Goal**: Implement OSCE-EMR linking API endpoints and database changes

**Tasks**:
1. Database migration (add requires_documentation, documentation_weight, user_progress columns) - 1 hour
2. Create OSCEToPatientTransformer service - 1.5 hours
3. Implement POST /osces/{id}/start-emr-session endpoint - 1 hour
4. Enhance GET /osces/{id}/results with EMR scores - 1 hour
5. Create DualScoreCalculator service - 30 min

**Validation Gate**:
- [ ] Database migration runs successfully (0 errors)
- [ ] OSCEToPatientTransformer converts OSCE text → MockPatient
- [ ] Start EMR endpoint returns session + OSCE context
- [ ] Results endpoint shows dual scores when EMR session exists
- [ ] Dual score calculation correct (60% clinical + 40% EMR)

---

### Phase 2: Frontend Integration (40% of effort, 3-4 hours)
**Goal**: Create UI components for dual scoring and OSCE-EMR workflow

**Tasks**:
1. Enhance OSCEResultsPage: Add "Document this case" button - 1 hour
2. Create EMRSessionFromOSCE component (redirect to Epic/Cerner) - 1 hour
3. Create DualScoreCard component (visual score breakdown) - 1.5 hours
4. Update Dashboard: Add OSCE-EMR analytics section - 30 min

**Validation Gate**:
- [ ] "Document this case" button appears only when requires_documentation=true
- [ ] Clicking button starts EMR session with correct patient
- [ ] DualScoreCard displays clinical + EMR + combined scores
- [ ] Visual design matches existing components (MUI theme)
- [ ] Mobile responsive (scores readable on small screens)

---

### Phase 3: Testing & Polish (20% of effort, 2-3 hours)
**Goal**: Integration testing and user experience refinement

**Tasks**:
1. Integration tests: OSCE → EMR → Dual Score workflow - 1 hour
2. Edge case handling (OSCE without EMR, EMR without OSCE) - 30 min
3. Progress tracking verification (user_progress updates) - 30 min
4. Performance testing (OSCE → EMR startup time <500ms) - 30 min
5. Documentation and examples - 30 min

**Validation Gate**:
- [ ] Integration test: Complete OSCE → Start EMR → Submit → See dual score
- [ ] Edge case: OSCE completion without EMR still works (backward compatible)
- [ ] user_progress.osce_emr_* fields update correctly
- [ ] Performance: Start EMR from OSCE <500ms (measured)
- [ ] Documentation complete (API examples, component usage)

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks (Backend)

**Task 1.1**: Database Migration
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **File**: `/backend/alembic/versions/20260216_1400_011_add_osce_emr_integration.py`
- **Code**:
  ```python
  """Add OSCE-EMR integration fields
  
  Revision ID: 011_osce_emr_integration
  Revises: 010
  Create Date: 2026-02-16 14:00:00
  """
  
  from alembic import op
  import sqlalchemy as sa
  from sqlalchemy.dialects import postgresql
  
  def upgrade():
      # Add OSCE documentation flags
      op.add_column('osces', 
          sa.Column('requires_documentation', sa.Boolean(), 
                    nullable=False, server_default='false')
      )
      op.add_column('osces', 
          sa.Column('documentation_weight', sa.Numeric(3, 2), 
                    nullable=False, server_default='0.40')
      )
      
      # Add user_progress OSCE-EMR metrics
      op.add_column('user_progress', 
          sa.Column('osce_emr_linked_completions', sa.Integer(), 
                    nullable=False, server_default='0')
      )
      op.add_column('user_progress', 
          sa.Column('osce_emr_avg_combined_score', sa.Numeric(5, 2), 
                    nullable=True)
      )
      op.add_column('user_progress', 
          sa.Column('osce_emr_specialty_scores', 
                    postgresql.JSONB(astext_type=sa.Text()), 
                    nullable=False, server_default='{}')
      )
      
      # Create indexes
      op.create_index('idx_osces_requires_documentation', 'osces', 
                     ['requires_documentation'], unique=False)
      op.create_index('idx_user_progress_osce_emr_linked', 'user_progress', 
                     ['osce_emr_linked_completions'], unique=False)
      op.create_index('idx_user_progress_osce_emr_specialty_scores', 
                     'user_progress', ['osce_emr_specialty_scores'], 
                     unique=False, postgresql_using='gin')
      
      # Mark existing OSCEs as requiring documentation
      op.execute("""
          UPDATE osces 
          SET requires_documentation = TRUE
          WHERE station_type IN ('history_taking', 'physical_examination', 
                                 'emergency_scenario')
      """)
  
  def downgrade():
      op.drop_index('idx_user_progress_osce_emr_specialty_scores')
      op.drop_index('idx_user_progress_osce_emr_linked')
      op.drop_index('idx_osces_requires_documentation')
      op.drop_column('user_progress', 'osce_emr_specialty_scores')
      op.drop_column('user_progress', 'osce_emr_avg_combined_score')
      op.drop_column('user_progress', 'osce_emr_linked_completions')
      op.drop_column('osces', 'documentation_weight')
      op.drop_column('osces', 'requires_documentation')
  ```
- **Acceptance Criteria**:
  - [ ] Migration runs without errors
  - [ ] Columns added to osces and user_progress tables
  - [ ] Indexes created successfully
  - [ ] Existing OSCEs marked with requires_documentation=true
  - [ ] Rollback (downgrade) works correctly

**Task 1.2**: Create OSCEToPatientTransformer Service
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **File**: `/backend/src/services/integration/osce_to_patient_transformer.py`
- **Code**:
  ```python
  """
  Transform OSCE patient_instructions (text) to structured MockPatient
  
  Handles:
  - Demographic extraction (age, gender from scenario text)
  - Vital signs parsing
  - Presenting complaint extraction
  - Medical history extraction (if present)
  """
  
  import re
  from typing import Dict, Any, Optional
  from src.db.models import OSCE, MockPatient
  from sqlalchemy.orm import Session
  
  class OSCEToPatientTransformer:
      """Transform OSCE data into MockPatient for EMR practice"""
      
      def __init__(self, db: Session):
          self.db = db
      
      def transform(self, osce: OSCE) -> MockPatient:
          """
          Main transformation method
          
          Args:
              osce: OSCE database object
          
          Returns:
              MockPatient object (either existing or newly created)
          """
          # Check if MockPatient already exists for this OSCE
          existing_patient = self.db.query(MockPatient).filter(
              MockPatient.osce_id == osce.osce_id
          ).first()
          
          if existing_patient:
              return existing_patient
          
          # Parse OSCE data to extract patient information
          patient_data = self._parse_osce_data(osce)
          
          # Create new MockPatient
          patient = MockPatient(
              osce_id=osce.osce_id,
              mrn=self._generate_mrn(),
              full_name=patient_data.get("name", "Simulated Patient"),
              age=patient_data.get("age"),
              gender=patient_data.get("gender"),
              allergies=patient_data.get("allergies", []),
              current_medications=patient_data.get("medications", []),
              vital_signs=patient_data.get("vital_signs", {}),
              presenting_complaint=patient_data.get("presenting_complaint", ""),
              clinical_scenario=osce.patient_instructions,
              specialty=osce.specialty,
              complexity_level=self._infer_complexity(osce)
          )
          
          self.db.add(patient)
          self.db.commit()
          self.db.refresh(patient)
          
          return patient
      
      def _parse_osce_data(self, osce: OSCE) -> Dict[str, Any]:
          """Parse OSCE patient_instructions text to extract structured data"""
          text = osce.patient_instructions + " " + osce.candidate_instructions
          
          return {
              "name": self._extract_name(text),
              "age": self._extract_age(text),
              "gender": self._extract_gender(text),
              "presenting_complaint": self._extract_presenting_complaint(osce),
              "allergies": self._extract_allergies(text),
              "medications": self._extract_medications(text),
              "vital_signs": self._extract_vital_signs(text)
          }
      
      def _extract_age(self, text: str) -> Optional[int]:
          """Extract age from text (e.g., '65-year-old', '58 years old')"""
          patterns = [
              r'(\d{1,3})-year-old',
              r'(\d{1,3}) years old',
              r'aged (\d{1,3})',
              r'age (\d{1,3})'
          ]
          for pattern in patterns:
              match = re.search(pattern, text, re.IGNORECASE)
              if match:
                  return int(match.group(1))
          return None
      
      def _extract_gender(self, text: str) -> Optional[str]:
          """Extract gender from text"""
          text_lower = text.lower()
          if 'male' in text_lower and 'female' not in text_lower:
              return 'Male'
          elif 'female' in text_lower:
              return 'Female'
          return None
      
      def _extract_presenting_complaint(self, osce: OSCE) -> str:
          """Extract chief complaint from candidate_instructions"""
          # Look for common patterns
          text = osce.candidate_instructions
          patterns = [
              r'presenting with (.+?)\.',
              r'chief complaint[:\s]+(.+?)\.',
              r'complaining of (.+?)\.'
          ]
          for pattern in patterns:
              match = re.search(pattern, text, re.IGNORECASE)
              if match:
                  return match.group(1).strip()
          
          # Fallback: Use first sentence
          sentences = text.split('.')
          return sentences[0].strip() if sentences else ""
      
      def _extract_allergies(self, text: str) -> list:
          """Extract allergies from text"""
          allergy_pattern = r'allerg(?:y|ies)[:\s]+(.+?)(?:\.|,|$)'
          match = re.search(allergy_pattern, text, re.IGNORECASE)
          if match:
              allergens = match.group(1).split(',')
              return [a.strip() for a in allergens]
          
          # Check for "NKDA"
          if 'nkda' in text.lower() or 'no known drug allergies' in text.lower():
              return ["NKDA"]
          
          return []
      
      def _extract_medications(self, text: str) -> list:
          """Extract current medications from text (basic extraction)"""
          # This is simplified - in production, use medical NLP
          medications = []
          med_pattern = r'(?:taking|on) (.+?)(?:for|,|\.|$)'
          matches = re.finditer(med_pattern, text, re.IGNORECASE)
          
          for match in matches:
              med_text = match.group(1).strip()
              # Parse dose if present
              dose_match = re.search(r'(\d+\s*(?:mg|mcg|g))', med_text)
              if dose_match:
                  medications.append({
                      "name": re.sub(r'\d+\s*(?:mg|mcg|g)', '', med_text).strip(),
                      "dose": dose_match.group(1),
                      "frequency": "daily"  # Default
                  })
          
          return medications
      
      def _extract_vital_signs(self, text: str) -> dict:
          """Extract vital signs from text"""
          vitals = {}
          
          # Blood pressure (e.g., "BP 152/88", "BP: 152/88 mmHg")
          bp_match = re.search(r'BP[:\s]+(\d{2,3})/(\d{2,3})', text, re.IGNORECASE)
          if bp_match:
              vitals["BP"] = f"{bp_match.group(1)}/{bp_match.group(2)}"
          
          # Heart rate (e.g., "HR 92", "pulse 92 bpm")
          hr_match = re.search(r'(?:HR|heart rate|pulse)[:\s]+(\d{2,3})', text, re.IGNORECASE)
          if hr_match:
              vitals["HR"] = int(hr_match.group(1))
          
          # Respiratory rate
          rr_match = re.search(r'(?:RR|respiratory rate)[:\s]+(\d{1,2})', text, re.IGNORECASE)
          if rr_match:
              vitals["RR"] = int(rr_match.group(1))
          
          # SpO2
          spo2_match = re.search(r'(?:SpO2|oxygen saturation)[:\s]+(\d{2,3})%?', text, re.IGNORECASE)
          if spo2_match:
              vitals["SpO2"] = int(spo2_match.group(1))
          
          # Temperature
          temp_match = re.search(r'(?:temp|temperature)[:\s]+([\d.]+)', text, re.IGNORECASE)
          if temp_match:
              vitals["Temp"] = float(temp_match.group(1))
          
          return vitals
      
      def _extract_name(self, text: str) -> str:
          """Extract patient name if present, otherwise generate"""
          # Look for "Mr/Mrs/Ms [Name]" pattern
          name_match = re.search(r'(?:Mr|Mrs|Ms|Dr)\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
          if name_match:
              return name_match.group(1)
          
          # Generate generic name based on gender
          gender = self._extract_gender(text)
          if gender == 'Male':
              return "John Smith"
          elif gender == 'Female':
              return "Jane Smith"
          return "Patient"
      
      def _generate_mrn(self) -> str:
          """Generate unique MRN for patient"""
          import random
          return f"MRN{random.randint(10000000, 99999999)}"
      
      def _infer_complexity(self, osce: OSCE) -> str:
          """Infer complexity from OSCE rubric total marks"""
          # OSCEs with detailed rubrics are typically more complex
          rubric_keys = len(osce.rubric.keys()) if isinstance(osce.rubric, dict) else 0
          
          if rubric_keys >= 5:
              return "Complex"
          elif rubric_keys >= 3:
              return "Moderate"
          return "Simple"
  ```
- **Acceptance Criteria**:
  - [ ] Transformer extracts age from text (e.g., "65-year-old" → 65)
  - [ ] Transformer extracts gender (male/female)
  - [ ] Transformer extracts vital signs (BP, HR, RR, SpO2, Temp)
  - [ ] Transformer extracts presenting complaint
  - [ ] Transformer extracts allergies (including NKDA)
  - [ ] Returns existing MockPatient if already created for OSCE
  - [ ] Unit tests: 10+ test cases (age extraction, vitals parsing, etc.)

**Task 1.3**: Implement POST /osces/{id}/start-emr-session
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **File**: `/backend/src/api/v1/osces.py` (add to existing file)
- **Code**:
  ```python
  @router.post("/{osce_id}/start-emr-session", response_model=OSCEEMRStartResponse)
  async def start_emr_session_from_osce(
      osce_id: int,
      request: OSCEEMRStartRequest,
      current_user: User = Depends(get_current_active_user),
      db: Session = Depends(get_db)
  ):
      """
      Start EMR documentation session from completed OSCE station.
      
      Workflow:
      1. Validate user has completed this OSCE
      2. Transform OSCE data → MockPatient
      3. Create EMR session (linked to osce_id)
      4. Return session + patient + OSCE context
      
      Requirements:
      - User must have completed OSCE (OSCEAttempt exists)
      - OSCE must require documentation (requires_documentation=true)
      - User cannot have existing active EMR session for this OSCE
      """
      # 1. Validate OSCE exists
      osce = db.query(OSCE).filter(OSCE.id == osce_id, OSCE.is_published == True).first()
      if not osce:
          raise HTTPException(status_code=404, detail="OSCE not found")
      
      # 2. Check requires_documentation
      if not osce.requires_documentation:
          raise HTTPException(
              status_code=400,
              detail="This OSCE station does not require EMR documentation"
          )
      
      # 3. Validate user has completed OSCE
      attempt = db.query(OSCEAttempt).filter(
          OSCEAttempt.user_id == current_user.id,
          OSCEAttempt.osce_id == osce_id
      ).order_by(OSCEAttempt.created_at.desc()).first()
      
      if not attempt:
          raise HTTPException(
              status_code=403,
              detail="You must complete the OSCE station before documenting it"
          )
      
      # 4. Check for existing active EMR session for this OSCE
      existing_session = db.query(EMRSession).filter(
          EMRSession.user_id == current_user.id,
          EMRSession.osce_id == osce.osce_id,
          EMRSession.is_active == True
      ).first()
      
      if existing_session:
          raise HTTPException(
              status_code=409,
              detail="You already have an active EMR session for this OSCE"
          )
      
      # 5. Transform OSCE → MockPatient
      from src.services.integration.osce_to_patient_transformer import OSCEToPatientTransformer
      
      transformer = OSCEToPatientTransformer(db)
      patient = transformer.transform(osce)
      
      # 6. Create EMR session (linked to OSCE)
      session = EMRSession(
          user_id=current_user.id,
          patient_scenario_id=patient.id,
          osce_id=osce.osce_id,  # CRITICAL LINK
          emr_system=request.emr_system,
          is_active=True,
          session_data={}
      )
      db.add(session)
      db.commit()
      db.refresh(session)
      
      # 7. Return session + patient + OSCE context
      return OSCEEMRStartResponse(
          session_id=str(session.id),
          patient=MockPatientResponse.from_orm(patient),
          emr_system=session.emr_system,
          osce_context=OSCEContext(
              osce_id=osce.osce_id,
              station_title=osce.station_title,
              specialty=osce.specialty,
              clinical_scenario=osce.patient_instructions,
              time_limit_minutes=10  # Recommended time for EMR documentation
          ),
          started_at=session.started_at
      )
  ```
- **Acceptance Criteria**:
  - [ ] Returns 404 if OSCE doesn't exist
  - [ ] Returns 400 if OSCE doesn't require documentation
  - [ ] Returns 403 if user hasn't completed OSCE
  - [ ] Returns 409 if user has active EMR session for this OSCE
  - [ ] Creates EMR session with osce_id link
  - [ ] Returns patient data transformed from OSCE
  - [ ] Performance: <500ms (measured)

**Task 1.4**: Enhance GET /osces/{id}/results
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **File**: `/backend/src/api/v1/osces.py` (enhance existing endpoint)
- **Code**:
  ```python
  @router.get("/{osce_id}/results", response_model=OSCEResultsResponse)
  async def get_osce_results(
      osce_id: int,
      attempt_id: Optional[int] = None,
      current_user: User = Depends(get_current_active_user),
      db: Session = Depends(get_db)
  ):
      """
      Get OSCE results with optional EMR dual scoring.
      
      ENHANCED: Now returns EMR scores if student documented this OSCE.
      """
      # Existing OSCE logic...
      osce = db.query(OSCE).filter(OSCE.id == osce_id).first()
      if not osce:
          raise HTTPException(status_code=404, detail="OSCE not found")
      
      # Get attempt (latest or specific)
      if attempt_id:
          attempt = db.query(OSCEAttempt).filter_by(id=attempt_id).first()
      else:
          attempt = db.query(OSCEAttempt).filter(
              OSCEAttempt.user_id == current_user.id,
              OSCEAttempt.osce_id == osce_id
          ).order_by(OSCEAttempt.created_at.desc()).first()
      
      if not attempt:
          raise HTTPException(status_code=404, detail="No OSCE attempt found")
      
      # Base response (existing fields)
      response_data = {
          "osce_id": osce.osce_id,
          "station_title": osce.station_title,
          "attempt_number": attempt.attempt_number,
          "clinical_score": attempt.total_score,
          "clinical_score_percentage": (attempt.total_score / 15) * 100,
          "passed_clinical": attempt.passed,
          "scores": attempt.scores,
          "time_taken_seconds": attempt.time_taken_seconds,
          "rubric": osce.rubric,
          "areas_for_improvement": attempt.areas_for_improvement
      }
      
      # NEW: Check if user documented this OSCE
      emr_session = db.query(EMRSession).filter(
          EMRSession.user_id == current_user.id,
          EMRSession.osce_id == osce.osce_id,
          EMRSession.is_active == False  # Only completed sessions
      ).first()
      
      if emr_session:
          # Get EMR validation results
          soap_note = db.query(EMRSOAPNote).filter_by(
              emr_session_id=emr_session.id
          ).first()
          
          if soap_note and soap_note.overall_validation_score:
              # Calculate dual score
              from src.services.integration.dual_score_calculator import DualScoreCalculator
              
              calculator = DualScoreCalculator()
              dual_score = calculator.calculate(
                  clinical_score=attempt.total_score,
                  emr_score=soap_note.overall_validation_score,
                  clinical_weight=osce.documentation_weight or 0.6,
                  documentation_weight=1 - (osce.documentation_weight or 0.6)
              )
              
              response_data.update({
                  "emr_session_id": str(emr_session.id),
                  "emr_score": soap_note.overall_validation_score,
                  "combined_score": dual_score.combined_score,
                  "passed_combined": dual_score.passed,
                  "dual_score_breakdown": dual_score.breakdown,
                  "emr_feedback_summary": soap_note.feedback_summary
              })
      
      return OSCEResultsResponse(**response_data)
  ```

**Task 1.5**: Create DualScoreCalculator Service
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **File**: `/backend/src/services/integration/dual_score_calculator.py`
- **Code**:
  ```python
  """Calculate dual scores (clinical + documentation weighted average)"""
  
  from pydantic import BaseModel
  
  class DualScoreBreakdown(BaseModel):
      clinical_weight: float  # 0-1 (e.g., 0.6 = 60%)
      documentation_weight: float  # 0-1 (e.g., 0.4 = 40%)
      clinical_contribution: float  # clinical_score × weight
      documentation_contribution: float  # emr_score × weight
      total: float  # Sum of contributions
      pass_threshold: float = 75.0
  
  class DualScoreResult(BaseModel):
      combined_score: float
      passed: bool
      breakdown: DualScoreBreakdown
  
  class DualScoreCalculator:
      """Calculate weighted combined scores from clinical + documentation"""
      
      def calculate(
          self,
          clinical_score: int,  # 0-15 (OSCE rubric score)
          emr_score: float,  # 0-100 (EMR validation score)
          clinical_weight: float = 0.6,
          documentation_weight: float = 0.4
      ) -> DualScoreResult:
          """
          Calculate combined score with weighted average.
          
          Args:
              clinical_score: OSCE rubric score (0-15)
              emr_score: EMR validation score (0-100)
              clinical_weight: Weight for clinical score (default 60%)
              documentation_weight: Weight for EMR score (default 40%)
          
          Returns:
              DualScoreResult with combined score and breakdown
          """
          # Normalize clinical score to 0-100
          clinical_normalized = (clinical_score / 15) * 100
          
          # Calculate weighted contributions
          clinical_contribution = clinical_normalized * clinical_weight
          documentation_contribution = emr_score * documentation_weight
          
          # Combined score
          combined = clinical_contribution + documentation_contribution
          
          # Pass threshold: 75% (reflecting AMC ~60% + buffer)
          passed = combined >= 75.0
          
          return DualScoreResult(
              combined_score=round(combined, 2),
              passed=passed,
              breakdown=DualScoreBreakdown(
                  clinical_weight=clinical_weight * 100,  # Convert to percentage
                  documentation_weight=documentation_weight * 100,
                  clinical_contribution=round(clinical_contribution, 2),
                  documentation_contribution=round(documentation_contribution, 2),
                  total=round(combined, 2),
                  pass_threshold=75.0
              )
          )
  ```

---

### Phase 2 Tasks (Frontend)

**Task 2.1**: Enhance OSCEResultsPage Component
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **File**: `/frontend/src/components/osce/OSCEResultsPage.tsx`
- **Code**:
  ```typescript
  // Add "Document this case" button after OSCE completion
  
  import { Button, Alert } from '@mui/material';
  import { useState } from 'react';
  import { useNavigate } from 'react-router-dom';
  import { api } from '@/api/client';
  
  export function OSCEResultsPage({ osceId, attemptData }: Props) {
    const navigate = useNavigate();
    const [startingEMR, setStartingEMR] = useState(false);
    
    // Check if OSCE requires documentation
    const requiresDocumentation = attemptData.osce?.requires_documentation;
    const hasDocumented = !!attemptData.emr_session_id;
    
    const handleStartEMRSession = async () => {
      setStartingEMR(true);
      try {
        const response = await api.post(`/osces/${osceId}/start-emr-session`, {
          emr_system: 'epic'  // Or user preference
        });
        
        // Navigate to EMR session
        navigate(`/emr/session/${response.data.session_id}`, {
          state: { osceContext: response.data.osce_context }
        });
      } catch (error) {
        console.error('Failed to start EMR session:', error);
        alert('Error starting EMR session');
      } finally {
        setStartingEMR(false);
      }
    };
    
    return (
      <div>
        {/* Existing OSCE results */}
        <ScoreCard 
          score={attemptData.clinical_score} 
          maxScore={15}
          passed={attemptData.passed_clinical}
        />
        
        {/* NEW: Document this case prompt */}
        {requiresDocumentation && !hasDocumented && (
          <Alert severity="info" sx={{ mt: 2 }}>
            Practice documenting this case in EMR
            <Button 
              variant="contained" 
              onClick={handleStartEMRSession}
              disabled={startingEMR}
              sx={{ ml: 2 }}
            >
              {startingEMR ? 'Starting...' : 'Document this case'}
            </Button>
          </Alert>
        )}
        
        {/* NEW: Dual score display */}
        {hasDocumented && attemptData.dual_score_breakdown && (
          <DualScoreCard 
            clinicalScore={attemptData.clinical_score_percentage}
            emrScore={attemptData.emr_score}
            combinedScore={attemptData.combined_score}
            breakdown={attemptData.dual_score_breakdown}
            passed={attemptData.passed_combined}
          />
        )}
      </div>
    );
  }
  ```

**Task 2.2**: Create EMRSessionFromOSCE Component
- **Effort**: 1 hour
- **File**: `/frontend/src/components/emr/EMRSessionFromOSCE.tsx`
- **Code**:
  ```typescript
  /**
   * EMR session component for OSCE-linked documentation practice
   * 
   * Shows:
   * - OSCE context banner (station title, specialty)
   * - Pre-populated patient from OSCE data
   * - Epic/Cerner UI (based on user selection)
   * - Timer (recommended 10 minutes)
   */
  
  import { Box, Paper, Typography, Chip } from '@mui/material';
  import { useLocation } from 'react-router-dom';
  import { EpicEHRInterface } from './EpicEHRInterface';
  import { CernerInterface } from './CernerInterface';
  
  export function EMRSessionFromOSCE() {
    const location = useLocation();
    const { osceContext, patient, emrSystem } = location.state || {};
    
    if (!osceContext) {
      return <div>Error: No OSCE context provided</div>;
    }
    
    return (
      <Box>
        {/* OSCE Context Banner */}
        <Paper sx={{ p: 2, mb: 2, bgcolor: 'info.light' }}>
          <Typography variant="h6">
            Documenting OSCE: {osceContext.station_title}
          </Typography>
          <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
            <Chip label={`Specialty: ${osceContext.specialty}`} size="small" />
            <Chip label="OSCE-Linked Practice" color="primary" size="small" />
            <Chip label={`Recommended time: ${osceContext.time_limit_minutes} min`} 
                  size="small" />
          </Box>
        </Paper>
        
        {/* EMR Interface (Epic or Cerner) */}
        {emrSystem === 'epic' ? (
          <EpicEHRInterface patient={patient} osceLinked={true} />
        ) : (
          <CernerInterface patient={patient} osceLinked={true} />
        )}
      </Box>
    );
  }
  ```

**Task 2.3**: Create DualScoreCard Component
- **Effort**: 1.5 hours
- **File**: `/frontend/src/components/osce/DualScoreCard.tsx`
- **Code**:
  ```typescript
  /**
   * Visual breakdown of dual scoring (clinical + documentation)
   * 
   * Shows:
   * - Clinical score (0-100, normalized from 0-15)
   * - EMR documentation score (0-100)
   * - Combined weighted score (60% clinical + 40% EMR)
   * - Pass/Fail badge
   * - Progress bars for each component
   */
  
  import { Card, CardContent, Typography, LinearProgress, Box, Chip } from '@mui/material';
  import { CheckCircle, Cancel } from '@mui/icons-material';
  
  interface DualScoreCardProps {
    clinicalScore: number;  // 0-100 (normalized)
    emrScore: number;  // 0-100
    combinedScore: number;  // Weighted average
    breakdown: {
      clinical_weight: number;
      documentation_weight: number;
      clinical_contribution: number;
      documentation_contribution: number;
    };
    passed: boolean;
  }
  
  export function DualScoreCard({
    clinicalScore,
    emrScore,
    combinedScore,
    breakdown,
    passed
  }: DualScoreCardProps) {
    return (
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
            <Typography variant="h6">
              OSCE + EMR Performance
            </Typography>
            <Chip 
              icon={passed ? <CheckCircle /> : <Cancel />}
              label={passed ? 'PASS' : 'FAIL'}
              color={passed ? 'success' : 'error'}
            />
          </Box>
          
          {/* Clinical Score */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Clinical Skills ({breakdown.clinical_weight}% weight)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LinearProgress 
                variant="determinate" 
                value={clinicalScore} 
                sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                color="primary"
              />
              <Typography variant="h6" sx={{ minWidth: 60 }}>
                {clinicalScore.toFixed(0)}%
              </Typography>
            </Box>
          </Box>
          
          {/* EMR Documentation Score */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
              Documentation Quality ({breakdown.documentation_weight}% weight)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LinearProgress 
                variant="determinate" 
                value={emrScore} 
                sx={{ flexGrow: 1, height: 10, borderRadius: 5 }}
                color="info"
              />
              <Typography variant="h6" sx={{ minWidth: 60 }}>
                {emrScore.toFixed(0)}%
              </Typography>
            </Box>
          </Box>
          
          {/* Combined Score */}
          <Box 
            sx={{ 
              mt: 3, 
              p: 2, 
              bgcolor: passed ? 'success.light' : 'error.light',
              borderRadius: 2 
            }}
          >
            <Typography variant="body2" color="text.secondary">
              Combined Score (Pass threshold: 75%)
            </Typography>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <LinearProgress 
                variant="determinate" 
                value={combinedScore} 
                sx={{ flexGrow: 1, height: 15, borderRadius: 5 }}
                color={passed ? 'success' : 'error'}
              />
              <Typography variant="h5" sx={{ minWidth: 70 }}>
                {combinedScore.toFixed(1)}%
              </Typography>
            </Box>
          </Box>
          
          {/* Breakdown Formula */}
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Calculation: ({clinicalScore}% × {breakdown.clinical_weight}%) + 
            ({emrScore}% × {breakdown.documentation_weight}%) = {combinedScore.toFixed(1)}%
          </Typography>
        </CardContent>
      </Card>
    );
  }
  ```

**Task 2.4**: Update Dashboard with OSCE-EMR Analytics
- **Effort**: 30 min
- **File**: `/frontend/src/components/dashboard/Dashboard.tsx`
- **Code**:
  ```typescript
  // Add OSCE-EMR performance section to dashboard
  
  import { Card, CardContent, Typography, Grid } from '@mui/material';
  import { useQuery } from '@tanstack/react-query';
  import { api } from '@/api/client';
  
  export function Dashboard() {
    const { data: progress } = useQuery({
      queryKey: ['user-progress'],
      queryFn: () => api.get('/user/progress').then(r => r.data)
    });
    
    return (
      <Grid container spacing={3}>
        {/* Existing dashboard cards... */}
        
        {/* NEW: OSCE-EMR Integration Stats */}
        {progress?.osce_emr_linked_completions > 0 && (
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Clinical + Documentation Performance
                </Typography>
                <Typography variant="h3" color="primary">
                  {progress.osce_emr_avg_combined_score.toFixed(1)}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Average combined score across {progress.osce_emr_linked_completions} 
                  OSCE-EMR sessions
                </Typography>
                
                {/* Specialty breakdown */}
                <Box sx={{ mt: 2 }}>
                  {Object.entries(progress.osce_emr_specialty_scores).map(([specialty, scores]) => (
                    <Typography key={specialty} variant="body2">
                      {specialty}: {(scores.reduce((a,b) => a+b, 0) / scores.length).toFixed(1)}%
                    </Typography>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        )}
      </Grid>
    );
  }
  ```

---

### Phase 3 Tasks (Testing & Polish)

**Task 3.1**: Integration Tests
- **Effort**: 1 hour
- **File**: `/backend/tests/test_integration/test_osce_emr_linking.py`
- **Code**:
  ```python
  """Integration tests for OSCE-EMR linking workflow"""
  
  import pytest
  from fastapi.testclient import TestClient
  
  def test_complete_osce_emr_workflow(client, auth_headers, test_user, db_session):
      """
      Test full workflow:
      1. Complete OSCE station
      2. Start EMR session from OSCE
      3. Submit EMR documentation
      4. Get dual score results
      """
      # 1. Create and complete OSCE
      osce_data = {
          "osce_id": "OSCE-TEST-001",
          "station_title": "Test Cardiology Station",
          "station_type": "history_taking",
          "patient_instructions": "65-year-old male with chest pain. BP 152/88, HR 92.",
          "candidate_instructions": "Take a history from this patient presenting with chest pain.",
          "rubric": {...},  # AMC format rubric
          "specialty": "Cardiology",
          "requires_documentation": True
      }
      
      create_response = client.post("/api/v1/osces/", json=osce_data, 
                                    headers=auth_headers)
      assert create_response.status_code == 201
      osce_id = create_response.json()["id"]
      
      # Complete OSCE
      complete_response = client.post(
          f"/api/v1/osces/{osce_id}/complete-station",
          json={
              "scores": {"history_examination": 3, "clinical_reasoning": 2, 
                        "communication": 3, "patient_safety": 2, 
                        "professionalism": 2},
              "time_taken_seconds": 480
          },
          headers=auth_headers
      )
      assert complete_response.status_code == 200
      assert complete_response.json()["total_score"] == 12
      
      # 2. Start EMR session from OSCE
      emr_start_response = client.post(
          f"/api/v1/osces/{osce_id}/start-emr-session",
          json={"emr_system": "epic"},
          headers=auth_headers
      )
      assert emr_start_response.status_code == 200
      session_id = emr_start_response.json()["session_id"]
      assert emr_start_response.json()["osce_context"]["osce_id"] == "OSCE-TEST-001"
      
      # Verify patient data extracted from OSCE
      patient = emr_start_response.json()["patient"]
      assert patient["age"] == 65
      assert patient["gender"] == "Male"
      assert patient["vital_signs"]["BP"] == "152/88"
      
      # 3. Submit EMR documentation
      submit_response = client.post(
          f"/api/v1/emr/sessions/{session_id}/submit",
          json={
              "soap_note": {
                  "subjective": "65-year-old male with chest pain x 2 hours...",
                  "objective": "BP 152/88, HR 92, RR 20...",
                  "assessment": "Likely ACS...",
                  "plan": "ECG, troponin, aspirin..."
              },
              "prescriptions": [
                  {"medication_name": "Aspirin", "dose": "300mg", 
                   "frequency": "stat", "route": "PO", "quantity": 1, 
                   "repeats": 0, "indication": "ACS"}
              ],
              "pathology_orders": [],
              "completion_time_seconds": 540
          },
          headers=auth_headers
      )
      assert submit_response.status_code == 200
      
      # 4. Get dual score results
      results_response = client.get(
          f"/api/v1/osces/{osce_id}/results",
          headers=auth_headers
      )
      assert results_response.status_code == 200
      results = results_response.json()
      
      assert results["clinical_score"] == 12
      assert results["clinical_score_percentage"] == 80.0
      assert results["emr_session_id"] == session_id
      assert results["emr_score"] is not None  # Validation completed
      assert results["combined_score"] is not None
      assert "dual_score_breakdown" in results
      
      # Verify combined score calculation
      breakdown = results["dual_score_breakdown"]
      expected_combined = (80 * 0.6) + (results["emr_score"] * 0.4)
      assert abs(results["combined_score"] - expected_combined) < 0.1
  
  
  def test_osce_without_documentation_requirement(client, auth_headers):
      """Test OSCE that doesn't require documentation"""
      # Create OSCE with requires_documentation=false
      osce_data = {
          "osce_id": "OSCE-TEST-002",
          "station_title": "Procedural Skills Station",
          "station_type": "procedural_skills",
          "requires_documentation": False,
          # ... other fields
      }
      
      create_response = client.post("/api/v1/osces/", json=osce_data, 
                                    headers=auth_headers)
      osce_id = create_response.json()["id"]
      
      # Complete OSCE
      client.post(f"/api/v1/osces/{osce_id}/complete-station", 
                  json={"scores": {...}}, headers=auth_headers)
      
      # Try to start EMR session (should fail)
      emr_start_response = client.post(
          f"/api/v1/osces/{osce_id}/start-emr-session",
          json={"emr_system": "epic"},
          headers=auth_headers
      )
      assert emr_start_response.status_code == 400
      assert "does not require EMR documentation" in emr_start_response.json()["detail"]
  
  
  def test_dual_score_calculation_accuracy(client, auth_headers):
      """Test dual score calculation with known values"""
      # Clinical score: 12/15 = 80%
      # EMR score: 85/100 = 85%
      # Expected combined: (80 × 0.6) + (85 × 0.4) = 48 + 34 = 82%
      
      from src.services.integration.dual_score_calculator import DualScoreCalculator
      
      calculator = DualScoreCalculator()
      result = calculator.calculate(
          clinical_score=12,
          emr_score=85.0,
          clinical_weight=0.6,
          documentation_weight=0.4
      )
      
      assert result.combined_score == 82.0
      assert result.passed == True  # 82 >= 75
      assert result.breakdown.clinical_contribution == 48.0
      assert result.breakdown.documentation_contribution == 34.0
  ```

**Task 3.2**: Edge Case Handling
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Tests**:
  ```python
  def test_user_hasnt_completed_osce(client, auth_headers):
      """User tries to start EMR without completing OSCE first"""
      response = client.post("/api/v1/osces/999/start-emr-session", 
                            json={"emr_system": "epic"}, headers=auth_headers)
      assert response.status_code == 403
      assert "must complete the OSCE" in response.json()["detail"]
  
  def test_duplicate_emr_session_prevention(client, auth_headers):
      """Prevent duplicate active EMR sessions for same OSCE"""
      # Start first session
      client.post("/api/v1/osces/1/start-emr-session", 
                  json={"emr_system": "epic"}, headers=auth_headers)
      
      # Try to start second session (should fail)
      response = client.post("/api/v1/osces/1/start-emr-session", 
                            json={"emr_system": "cerner"}, headers=auth_headers)
      assert response.status_code == 409
      assert "already have an active EMR session" in response.json()["detail"]
  ```

**Task 3.3**: Progress Tracking Verification
- **Effort**: 30 min
- **Test**:
  ```python
  def test_user_progress_updates(client, auth_headers, db_session, test_user):
      """Verify user_progress OSCE-EMR metrics update correctly"""
      # Complete OSCE + EMR workflow (using test from 3.1)
      # ... workflow code ...
      
      # Check user_progress updates
      from src.db.models import UserProgress
      progress = db_session.query(UserProgress).filter_by(
          user_id=test_user.id
      ).first()
      
      assert progress.osce_emr_linked_completions == 1
      assert progress.osce_emr_avg_combined_score is not None
      assert "Cardiology" in progress.osce_emr_specialty_scores
  ```

**Task 3.4**: Performance Testing
- **Effort**: 30 min
- **Test**:
  ```python
  import time
  
  def test_start_emr_from_osce_performance(client, auth_headers, db_session):
      """Verify OSCE → EMR session creation <500ms"""
      # Setup: Create and complete OSCE
      # ... setup code ...
      
      # Measure performance
      start_time = time.time()
      response = client.post(
          f"/api/v1/osces/{osce_id}/start-emr-session",
          json={"emr_system": "epic"},
          headers=auth_headers
      )
      elapsed_ms = (time.time() - start_time) * 1000
      
      assert response.status_code == 200
      assert elapsed_ms < 500, f"Start EMR took {elapsed_ms}ms (target: <500ms)"
  ```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] OSCE completion shows "Document this case" button if requires_documentation=true
- [ ] Clicking button creates EMR session with patient data from OSCE
- [ ] EMR session links to OSCE (emr_sessions.osce_id populated)
- [ ] OSCE patient_instructions transformed to MockPatient (age, gender, vitals extracted)
- [ ] EMR submission returns to OSCE results page
- [ ] Dual score calculated correctly: (clinical × 0.6) + (EMR × 0.4)
- [ ] Dual score displayed in DualScoreCard component
- [ ] user_progress.osce_emr_* fields update after linked completion
- [ ] Dashboard shows OSCE-EMR combined score analytics

#### Quality Requirements
- [ ] **Test Coverage**: ≥70% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero-tolerance)
- [ ] **Integration Test**: OSCE → EMR → Dual Score workflow passes
- [ ] **Code Quality**: No linting errors, follows project patterns

#### Performance Requirements
- [ ] **Start EMR from OSCE**: <500ms p95
- [ ] **Get dual score results**: <300ms p95
- [ ] **Patient transformation**: <100ms (text parsing)
- [ ] **No impact on existing OSCE performance**

#### Security Requirements
- [ ] **JWT Required**: All new endpoints require authentication
- [ ] **Authorization**: Users can only link their own OSCEs + EMR sessions
- [ ] **Validation**: User must complete OSCE before starting EMR
- [ ] **Duplicate Prevention**: Cannot create duplicate active EMR sessions for same OSCE
- [ ] **Foreign Key Integrity**: emr_sessions.osce_id references osces.osce_id

#### Australian Medical Compliance
- [ ] OSCE rubric aligns with AMC Clinical Examination format (15 marks)
- [ ] Dual scoring reflects AMC pass standard (~60% clinical + buffer)
- [ ] EMR documentation validated against Australian standards (from PRD_BACKEND_003)
- [ ] Combined workflow prepares students for real Australian hospital practice

---

### Testing Requirements

#### Unit Tests (≥70% coverage)
```python
# OSCEToPatientTransformer tests
def test_extract_age_from_text():
    """Test age extraction: '65-year-old' → 65"""
    transformer = OSCEToPatientTransformer(db)
    age = transformer._extract_age("65-year-old male presenting with...")
    assert age == 65

def test_extract_vital_signs():
    """Test vital signs parsing: 'BP 152/88, HR 92' → dict"""
    transformer = OSCEToPatientTransformer(db)
    vitals = transformer._extract_vital_signs("BP 152/88, HR 92, SpO2 95%")
    assert vitals["BP"] == "152/88"
    assert vitals["HR"] == 92
    assert vitals["SpO2"] == 95

# DualScoreCalculator tests
def test_dual_score_calculation():
    """Test weighted average: (80×0.6) + (85×0.4) = 82"""
    calculator = DualScoreCalculator()
    result = calculator.calculate(clinical_score=12, emr_score=85)
    assert result.combined_score == 82.0
    assert result.passed == True  # 82 >= 75

def test_dual_score_fail_threshold():
    """Test fail case: combined score <75%"""
    calculator = DualScoreCalculator()
    result = calculator.calculate(clinical_score=8, emr_score=70)
    # (8/15 × 100 × 0.6) + (70 × 0.4) = 32 + 28 = 60%
    assert result.combined_score < 75
    assert result.passed == False
```

#### Integration Tests (100% endpoint coverage)
```python
def test_api_start_emr_from_osce(client, auth_headers):
    """Test POST /osces/{id}/start-emr-session"""
    # Complete OSCE first
    # ... setup code ...
    
    response = client.post(
        f"/api/v1/osces/{osce_id}/start-emr-session",
        json={"emr_system": "epic"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["osce_context"]["osce_id"] == expected_osce_id
    assert data["patient"]["age"] == 65  # Extracted from OSCE

def test_api_get_results_with_dual_score(client, auth_headers):
    """Test GET /osces/{id}/results with EMR scores"""
    # Complete OSCE + EMR workflow
    # ... workflow code ...
    
    response = client.get(f"/api/v1/osces/{osce_id}/results", 
                         headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["clinical_score"] == 12
    assert data["emr_score"] is not None
    assert data["combined_score"] is not None
    assert "dual_score_breakdown" in data
```

#### E2E Test (Full Workflow - Playwright)
```typescript
test('Complete OSCE and document in EMR', async ({ page }) => {
  // 1. Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'student@test.com');
  await page.fill('[name="password"]', 'TestPassword123');
  await page.click('button[type="submit"]');
  
  // 2. Start OSCE practice
  await page.goto('/osces');
  await page.click('text=Acute Coronary Syndrome - History Taking');
  await page.click('button:has-text("Start Practice")');
  
  // 3. Complete OSCE (self-scoring)
  await page.waitForSelector('text=Time: 8:00');
  // ... simulate 8-minute station ...
  await page.click('button:has-text("Complete Station")');
  
  // Self-score using AMC rubric
  await page.selectOption('[name="history_examination"]', '3');
  await page.selectOption('[name="clinical_reasoning"]', '2');
  await page.selectOption('[name="communication"]', '3');
  await page.selectOption('[name="patient_safety"]', '2');
  await page.selectOption('[name="professionalism"]', '2');
  await page.click('button:has-text("Submit Scores")');
  
  // 4. See results with "Document this case" button
  await expect(page.locator('text=Clinical Score: 12/15 (80%)')).toBeVisible();
  await expect(page.locator('button:has-text("Document this case")')).toBeVisible();
  
  // 5. Start EMR documentation
  await page.click('button:has-text("Document this case")');
  
  // Verify redirected to EMR UI with OSCE context
  await expect(page.locator('text=Documenting OSCE: Acute Coronary Syndrome')).toBeVisible();
  await expect(page.locator('text=Specialty: Cardiology')).toBeVisible();
  
  // 6. Complete SOAP note
  await page.fill('[name="subjective"]', 
    '65-year-old male presenting with central chest pain radiating to left arm...');
  await page.fill('[name="objective"]', 
    'BP 152/88, HR 92, RR 20, SpO2 95%...');
  await page.fill('[name="assessment"]', 
    'Likely Acute Coronary Syndrome - STEMI...');
  await page.fill('[name="plan"]', 
    'Activate cath lab, aspirin 300mg stat, ticagrelor...');
  
  // 7. Submit for validation
  await page.click('button:has-text("Submit for Validation")');
  
  // 8. See dual score results
  await expect(page.locator('text=OSCE + EMR Performance')).toBeVisible();
  await expect(page.locator('text=Clinical Skills (60% weight)')).toBeVisible();
  await expect(page.locator('text=Documentation Quality (40% weight)')).toBeVisible();
  await expect(page.locator('text=Combined Score')).toBeVisible();
  await expect(page.locator('text=PASS')).toBeVisible();  // Assuming good performance
});
```

---

### Documentation Deliverables

#### 1. API Documentation
- **File**: `/docs/OSCE_EMR_INTEGRATION_API.md`
- **Sections**:
  - Overview of OSCE-EMR linking workflow
  - Endpoint reference (3 new/enhanced endpoints)
  - Request/response examples
  - Dual scoring formula explanation
  - Error handling guide

#### 2. User Guide
- **File**: `/docs/OSCE_EMR_USER_GUIDE.md`
- **Sections**:
  - "How to use OSCE-EMR integrated practice"
  - Step-by-step workflow with screenshots
  - Understanding dual scores
  - Tips for improving combined performance

#### 3. Developer Guide
- **File**: `/docs/OSCE_EMR_DEVELOPER_GUIDE.md`
- **Sections**:
  - Architecture overview
  - OSCEToPatientTransformer implementation
  - DualScoreCalculator algorithm
  - Adding new transformation rules
  - Testing OSCE-EMR integration

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All tests passing (100% pass rate)
- [ ] Database migration tested in staging
- [ ] PRD_BACKEND_002 (EMR Session API) deployed and working
- [ ] Frontend components reviewed (UI/UX approved)
- [ ] Performance benchmarks met (<500ms OSCE → EMR)

#### Deployment
- [ ] Run database migration (add requires_documentation, user_progress columns)
- [ ] Deploy backend (new endpoints + services)
- [ ] Deploy frontend (new components)
- [ ] Mark existing OSCEs with requires_documentation=true (history, exam stations)
- [ ] Smoke tests in staging

#### Post-Deployment
- [ ] Create sample OSCE with documentation requirement
- [ ] Test complete workflow: OSCE → EMR → Dual Score
- [ ] Verify user_progress updates
- [ ] Monitor dashboard analytics
- [ ] Gather user feedback on dual scoring

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ OSCE completion triggers "Document this case" button
2. ✅ EMR session created with patient data from OSCE
3. ✅ Dual score calculated and displayed (clinical + EMR)
4. ✅ user_progress tracks OSCE-EMR linked completions
5. ✅ Dashboard shows combined score analytics
6. ✅ All integration tests passing
7. ✅ Performance targets met (<500ms OSCE → EMR)
8. ✅ User feedback positive (≥85% report helpful)
9. ✅ Documentation complete
10. ✅ Adoption rate ≥70% (OSCEs with EMR documentation)

**Sign-off Required From**:
- [ ] PM Coordinator (overall quality + workflow logic)
- [ ] Backend Engineer (API implementation + dual scoring)
- [ ] Frontend Engineer (UI components + user experience)
- [ ] Security Expert (authorization + data integrity)
- [ ] Testing QA (integration tests + performance)
- [ ] Clinical Educator (AMC format compliance)

---

## 📎 Appendices

### Appendix A: Dual Score Calculation Examples

**Example 1: Strong Clinical, Good Documentation**
```
Clinical Score: 13/15 (87%)
EMR Score: 80/100 (80%)

Calculation:
clinical_contribution = 87 × 0.6 = 52.2
documentation_contribution = 80 × 0.4 = 32.0
combined_score = 52.2 + 32.0 = 84.2%

Result: ✓ PASS (84.2% ≥ 75%)
```

**Example 2: Weak Clinical, Strong Documentation**
```
Clinical Score: 9/15 (60%)
EMR Score: 95/100 (95%)

Calculation:
clinical_contribution = 60 × 0.6 = 36.0
documentation_contribution = 95 × 0.4 = 38.0
combined_score = 36.0 + 38.0 = 74.0%

Result: ✗ FAIL (74.0% < 75%)
Interpretation: Clinical skills need improvement despite excellent documentation
```

**Example 3: Borderline Pass**
```
Clinical Score: 11/15 (73%)
EMR Score: 78/100 (78%)

Calculation:
clinical_contribution = 73 × 0.6 = 43.8
documentation_contribution = 78 × 0.4 = 31.2
combined_score = 43.8 + 31.2 = 75.0%

Result: ✓ PASS (75.0% = 75% threshold)
```

---

### Appendix B: OSCE Patient Instructions Parsing Examples

**Input (OSCE patient_instructions)**:
```
You are a 65-year-old male presenting to the Emergency Department 
with central chest pain for 2 hours. You have a history of hypertension, 
type 2 diabetes, and you smoke 20 cigarettes per day. 

Your current medications are:
- Amlodipine 5mg daily
- Metformin 500mg twice daily
- Aspirin 100mg daily

You have an allergy to Penicillin (rash).

Your vital signs are: BP 152/88, HR 92, RR 20, SpO2 95%, Temp 36.8°C.
```

**Output (MockPatient)**:
```json
{
  "age": 65,
  "gender": "Male",
  "presenting_complaint": "Central chest pain for 2 hours",
  "allergies": ["Penicillin"],
  "current_medications": [
    {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"},
    {"name": "Metformin", "dose": "500mg", "frequency": "BD"},
    {"name": "Aspirin", "dose": "100mg", "frequency": "daily"}
  ],
  "vital_signs": {
    "BP": "152/88",
    "HR": 92,
    "RR": 20,
    "SpO2": 95,
    "Temp": 36.8
  },
  "medical_history": {
    "pmhx": ["Hypertension", "Type 2 Diabetes"],
    "social_history": "Smoker 20 cigarettes/day"
  }
}
```

---

### Appendix C: Related PRDs

- **Depends On**:
  - PRD_BACKEND_002 (EMR Session API) - CRITICAL DEPENDENCY
  - Existing OSCE system (`/api/v1/osces/*`)

- **Blocks**:
  - PRD_INTEGRATION_002 (OSCE Video Recording with EMR)
  - PRD_INTEGRATION_003 (Multi-Station OSCE Circuits with Cumulative EMR)

- **Related**:
  - PRD_BACKEND_001 (Database Migration - created emr_sessions.osce_id)
  - PRD_BACKEND_003 (Validation API - provides EMR scores)
  - PRD_FRONTEND_001 (Epic UI - consumed by OSCE-EMR workflow)
  - PRD_FRONTEND_002 (Cerner UI - consumed by OSCE-EMR workflow)

---

### Appendix D: Database Schema Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│ osces                                                            │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                          │
│ osce_id (UNIQUE)                 ← Referenced by emr_sessions   │
│ station_title                                                    │
│ patient_instructions             ← Transformed to MockPatient   │
│ rubric (JSONB)                   ← Used for clinical scoring    │
│ specialty                                                        │
│ requires_documentation (NEW)     ← Flag for EMR linking         │
│ documentation_weight (NEW)       ← Weight for dual scoring      │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:N
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ emr_sessions                                                     │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                          │
│ user_id (FK)                                                     │
│ patient_scenario_id (FK)         ← Generated from OSCE          │
│ osce_id (FK) [EXISTING]          ← Links to osces.osce_id       │
│ emr_system (cerner/epic)                                         │
│ is_active                                                        │
│ started_at                                                       │
│ completed_at                                                     │
└─────────────────────────────────────────────────────────────────┘
                                    │
                                    │ 1:1
                                    ▼
┌─────────────────────────────────────────────────────────────────┐
│ emr_soap_notes                                                   │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                          │
│ emr_session_id (FK)                                              │
│ overall_validation_score         ← Used for dual scoring        │
│ subjective, objective, assessment, plan                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ user_progress                                                    │
├─────────────────────────────────────────────────────────────────┤
│ id (PK)                                                          │
│ user_id (FK)                                                     │
│ osce_emr_linked_completions (NEW)    ← Count of linked sessions│
│ osce_emr_avg_combined_score (NEW)    ← Running average         │
│ osce_emr_specialty_scores (NEW JSONB) ← By specialty           │
└─────────────────────────────────────────────────────────────────┘
```

---

**Document Status**: Draft → Ready for Review
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending PM Review
**Version**: 1.0
**Estimated LOC**: ~800 backend, ~400 frontend (1200 total)
**Estimated Effort**: 9-12 hours (validated against similar PRD_BACKEND_002)
