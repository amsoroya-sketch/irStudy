# PRD: AI OSCE Mock Exam Mode - 16-Station Sequential Exam Orchestration

**PRD ID**: PRD_AI_OSCE_006_MOCK_EXAM_MODE
**Category**: Backend + Frontend
**Priority**: P1-High (Completes exam functionality)
**Estimated Effort**: 20-24 hours
**Dependencies**: PRD_AI_OSCE_001 (Database), PRD_AI_OSCE_002 (WebSocket), PRD_AI_OSCE_003 (AI Patient), PRD_AI_OSCE_004 (AI Examiner)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** medical student
**I want** to take a comprehensive 16-station mock exam that mirrors the AMC OSCE format
**So that** I can simulate the full exam experience, receive overall performance scoring, and identify systematic strengths/weaknesses across multiple clinical specialties

### Business Context
Mock exam mode is the final comprehensive assessment tool in the AI OSCE suite. Unlike individual practice (single station, unlimited time), mock exams enforce:

1. **Sequential Station Progression**: 16 stations, 8 minutes each, auto-advance with 5-sec breaks
2. **Fixed Duration**: ~150 minutes total (2 hours 40 minutes), no pausing or skipping
3. **Integrated Scoring**: Each station contributes to overall score (max 240, AMC pass = 198/240 = 82.5%)
4. **Balanced Persona Selection**: 2 personas per specialty × 8 specialties, auto-selected from intermediate/advanced difficulty
5. **Comprehensive Reporting**: Station-by-station breakdown + overall analysis + PDF export

This completes the AI OSCE feature roadmap and provides students with high-fidelity exam simulation for AMC Clinical Examination preparation.

**Business Value**:
- Eliminates exam anxiety through realistic full-exam practice
- Provides quantified pass/fail predictions before real exam
- Generates detailed comparative analysis (station performance vs. peers)
- Reduces human OSCE dependency ($0.04-0.07/student vs. $50-100 per session)
- Data-driven curriculum feedback (which specialties need more practice)

### Success Metrics
- **Exam Creation Speed**: <2 seconds to auto-select 16 personas and create exam
- **Station Auto-Advancement**: <3 seconds between station completion and next station load
- **Overall Score Calculation**: <1 second to aggregate 16 station scores
- **Report Generation**: <5 seconds for comprehensive HTML report, <10 seconds for PDF
- **Data Integrity**: Zero score loss, all 16 stations captured, no partial exams
- **User Experience**: 0 exam interruptions, seamless 150-minute experience
- **Pass Rate Accuracy**: AI mock exam pass/fail predicts real exam outcome with >85% accuracy

### Scope
**In Scope**:
- POST /api/v1/mock-exams (create exam with auto-selected personas)
- GET /api/v1/mock-exams/{exam_id} (retrieve exam progress)
- PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete (mark station complete)
- GET /api/v1/mock-exams/{exam_id}/results (overall exam results)
- Mock exam orchestration logic (station progression, auto-advance, scoring aggregation)
- Results dashboard (station-by-station table, overall score, pass/fail verdict)
- PDF report generation (professional exam report with charts)
- WebSocket events for real-time progress updates
- Database updates to mock_exams table (exam_state, total_score, overall_pass_fail)

**Out of Scope** (Future Iterations):
- Peer comparison analytics (leaderboards, percentile rankings)
- Adaptive station selection (difficulty increases based on performance)
- Time pressure analytics (time spent per question, decision speed metrics)
- Multi-user exam proctoring (classroom mode)
- Scheduling and automated reminders

---

## A - ARCHITECTURE (How)

### Technical Approach
Implement mock exam orchestration using transactional state machine (scheduled → in_progress → completed), WebSocket events for real-time progress, and background job for asynchronous report generation. Integrate with existing AI Patient/Examiner pipeline (PRD_003/004) and WebSocket layer (PRD_002).

**Key Design Decisions**:
1. **Auto-Persona Selection**: Deterministic SQL query (2 per specialty, balanced difficulty) vs. random (ensures consistent distributions)
2. **Station State Machine**: Explicit exam_state field prevents race conditions and accidental re-completion
3. **Real-Time Progress**: WebSocket events push station completion immediately (vs. polling)
4. **Score Aggregation**: SUM(station_scores) at exam completion (vs. running total that could be corrupted)
5. **Report Generation**: Async Celery task for PDFs (non-blocking, <10 sec user wait)
6. **Pass/Fail Threshold**: 198/240 (82.5%) follows official AMC guideline, with no critical errors override

### System Design

#### Component Diagram
```
┌──────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                            │
│  - Start mock exam button                                        │
│  - Station counter (Station N of 16)                             │
│  - 8-min timer (per station)                                     │
│  - Station results display (5-sec break, next station loading)   │
│  - Overall results dashboard (score, pass/fail, breakdown)       │
│  - PDF report viewer + download button                           │
└────────────────────┬─────────────────────────────────────────────┘
                     │ HTTPS REST API + WebSocket
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Python 3.11)                      │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Router: POST /api/v1/mock-exams                        │   │
│  │  - Auto-select 16 personas (2 per specialty)            │   │
│  │  - Create mock_exams record                             │   │
│  │  - Return exam_id, start_url, estimated_duration        │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Router: GET /api/v1/mock-exams/{exam_id}              │   │
│  │  - Get current_station, exam_state, timing              │   │
│  │  - For station N, load persona data                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Router: PUT /api/v1/mock-exams/{exam_id}/station/{n}/ │   │
│  │          complete                                        │   │
│  │  - Update osce_attempts with final scores               │   │
│  │  - Increment current_station                            │   │
│  │  - Check if exam_complete (station 16)                  │   │
│  │  - Emit WebSocket event                                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Router: GET /api/v1/mock-exams/{exam_id}/results      │   │
│  │  - Aggregate all 16 station scores                      │   │
│  │  - Calculate overall_pass_fail                          │   │
│  │  - Generate summary report                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  WebSocket: /ws/mock-exam/{exam_id}                     │   │
│  │  - Emit: station_complete event (score, next station)   │   │
│  │  - Emit: exam_complete event (overall results)          │   │
│  │  - Emit: error event (exam abandoned)                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Celery Background Job: generate_mock_exam_report()    │   │
│  │  - Generate PDF with charts, station analysis          │   │
│  │  - Store in object storage (S3)                         │   │
│  │  - Update mock_exams.report_url                         │   │
│  └─────────────────────────────────────────────────────────┘   │
└────────────────────┬─────────────────────────────────────────────┘
                     │ SQLAlchemy ORM + Celery
                     ↓
┌──────────────────────────────────────────────────────────────────┐
│                  POSTGRESQL 15 DATABASE                          │
│  - mock_exams (state machine: scheduled → in_progress → complete)│
│  - osce_attempts (16 records, one per station)                   │
│  - osce_scores (16 records, aggregated for overall score)        │
└──────────────────────────────────────────────────────────────────┘
```

#### Data Flow: Mock Exam Mode
```
1. EXAM CREATION
   Student → POST /api/v1/mock-exams
   Backend → SELECT 2 personas PER specialty (8 total specialties)
             WHERE difficulty IN ('intermediate', 'advanced')
             ORDER BY RANDOM() (deterministic seed)
   Backend → INSERT INTO mock_exams (user_id, stations_config)
   Backend → RETURN {exam_id, stations: 16, estimated_duration: "2h 40m"}

2. EXAM START
   Student → Click "Start Exam"
   Backend → UPDATE mock_exams SET exam_state = 'in_progress', actual_start = NOW()
   Frontend → Load Station 1 UI (timer: 8:00, patient intro)

3. STATION LOOP (Repeat 16 times)

   STATION N (8 minutes):
   ├─ Frontend → Load patient persona from mock_exams.stations_config[N-1]
   ├─ Frontend → Create WebSocket connection to /ws/osce/{attempt_id}
   ├─ Backend → Create osce_attempts record (user_id, persona_id, station_number=N)
   ├─ Student ↔ AI Patient (8-minute conversation via WebSocket)
   ├─ Timer expires → Auto-finalize osce_attempts
   ├─ Backend → Score session (Claude AI Examiner)
   ├─ Backend → INSERT INTO osce_scores (attempt_id, scores, feedback)
   └─ Backend → Emit WebSocket event:
      {
        "type": "station_complete",
        "station": N,
        "total_stations": 16,
        "score": 12,
        "pass_fail": "PASS",
        "next_station_starts_in": 5
      }

   5-SECOND BREAK:
   ├─ Frontend → Display station result card
   ├─ Frontend → Countdown timer (5, 4, 3, 2, 1)
   └─ Auto-load Station N+1

4. EXAM COMPLETION (After Station 16)
   Backend → Query all 16 osce_scores
             SUM(total_score) → overall_score (max 240)
             OVERALL_PASS_FAIL = IF (score >= 198 AND no_critical_errors) THEN 'PASS' ELSE 'FAIL'
   Backend → UPDATE mock_exams SET exam_state = 'completed',
                                   actual_end = NOW(),
                                   total_duration_minutes = (actual_end - actual_start)/60,
                                   total_score = 198,
                                   overall_pass_fail = 'PASS'
   Backend → Emit WebSocket event:
      {
        "type": "exam_complete",
        "total_score": 198,
        "max_score": 240,
        "percentage": 82.5,
        "pass_fail": "PASS",
        "estimated_ami_rank": "75th percentile"
      }
   Backend → Queue Celery task: generate_mock_exam_report(exam_id)

5. RESULTS DISPLAY
   Frontend → GET /api/v1/mock-exams/{exam_id}/results
   Backend → Return {
               total_score: 198,
               pass_fail: 'PASS',
               breakdown: [16 station objects with scores/feedback],
               strengths: ["Strong clinical reasoning", "Excellent communication"],
               weaknesses: ["Missed red flags in respiratory", "Incomplete history in psychiatry"],
               specialty_analysis: {cardiology: 25/30, respiratory: 20/30, ...}
             }
   Frontend → Display results dashboard
               - Overall score card (198/240, 82.5%, PASS)
               - Station-by-station table (station #, specialty, score, pass/fail)
               - Specialty breakdown (bar chart)
               - Strengths/weaknesses summary
               - Download PDF button

6. REPORT GENERATION (Background)
   Celery task → Load exam data + all station transcripts
   Celery task → Generate HTML with ReportLab (charts, station analysis)
   Celery task → Render to PDF
   Celery task → Upload to S3
   Celery task → UPDATE mock_exams SET report_url = 's3://...'
   Frontend → Display "Report Ready" badge, download link appears
```

### Database Schema Extensions

#### Table: mock_exams (Enhanced)
```sql
-- Updates to existing mock_exams table for exam orchestration

ALTER TABLE mock_exams ADD COLUMN (
    -- State Machine
    exam_state VARCHAR(20) DEFAULT 'scheduled' CHECK (
        exam_state IN ('scheduled', 'in_progress', 'paused', 'completed', 'abandoned')
    ),

    -- Timing (precise tracking)
    actual_start TIMESTAMP,  -- When student clicked "Start Exam"
    actual_end TIMESTAMP,    -- When Station 16 completed
    total_duration_minutes INTEGER,  -- = EXTRACT(EPOCH FROM (actual_end - actual_start)) / 60

    -- Progress Tracking
    current_station INTEGER DEFAULT 1 CHECK (current_station BETWEEN 1 AND 16),

    -- Overall Performance
    total_score INTEGER CHECK (total_score BETWEEN 0 AND 240),  -- Sum of 16 stations × 15 max each
    overall_pass_fail VARCHAR(10) CHECK (overall_pass_fail IN ('PASS', 'FAIL', 'INCOMPLETE')),

    -- Report Generation
    report_url VARCHAR(500),  -- S3 URL to PDF report
    report_generated_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance Index for filtering exams by state
CREATE INDEX idx_mock_exams_state ON mock_exams(user_id, exam_state)
WHERE exam_state IN ('scheduled', 'in_progress');
```

#### View: mock_exam_results
```sql
-- Aggregated view for results calculation
CREATE VIEW v_mock_exam_results AS
SELECT
    me.exam_id,
    me.user_id,
    me.exam_date,
    me.exam_state,
    me.actual_start,
    me.actual_end,
    me.total_duration_minutes,
    COUNT(oa.attempt_id) AS stations_completed,
    SUM(os.total_score) AS total_score,
    ROUND(SUM(os.total_score)::numeric / (COUNT(os.score_id) * 15) * 100, 1) AS percentage,
    CASE
        WHEN SUM(os.total_score) >= 198 AND COUNT(CASE WHEN os.critical_errors != '[]'::jsonb THEN 1 END) = 0
        THEN 'PASS'
        ELSE 'FAIL'
    END AS overall_pass_fail
FROM mock_exams me
LEFT JOIN osce_attempts oa ON me.exam_id = oa.mock_exam_id
LEFT JOIN osce_scores os ON oa.attempt_id = os.attempt_id
GROUP BY me.exam_id, me.user_id;
```

### API Endpoints Specification

#### Endpoint 1: Create Mock Exam (POST /api/v1/mock-exams)
**Purpose**: Initialize new 16-station mock exam with auto-selected balanced personas

```python
class CreateMockExamRequest(BaseModel):
    exam_date: date = Field(default=date.today())
    specialty_mix: str = Field("balanced", regex="^(balanced|random|custom)$")
    # Future: specialty_mix = "custom" with persona_ids provided

class CreateMockExamResponse(BaseModel):
    exam_id: str
    stations: int = 16
    estimated_duration: str  # "2 hours 40 minutes"
    start_url: str  # "/mock-exam/{exam_id}/station/1"
    stations_config: List[dict]  # 16 objects with station #, persona_id, specialty

@router.post("/api/v1/mock-exams", response_model=CreateMockExamResponse, status_code=201)
async def create_mock_exam(
    request: CreateMockExamRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create new mock exam with auto-selected personas.

    Auto-Selection Logic:
    - Group 360 personas by specialty (8 total)
    - Select 2 personas per specialty (intermediate or advanced difficulty)
    - Shuffle within each specialty for randomness
    - Build stations_config with 16 persona assignments

    Execution Time: <2 seconds
    """

    # Step 1: Validate no active exam in progress
    active_exam = db.query(MockExam).filter(
        MockExam.user_id == current_user.user_id,
        MockExam.exam_state.in_(['scheduled', 'in_progress'])
    ).first()

    if active_exam:
        raise HTTPException(
            status_code=409,
            detail=f"You have an active exam already (exam_id: {active_exam.exam_id})"
        )

    # Step 2: Auto-select 2 personas per specialty (8 specialties)
    specialties = [
        'cardiology', 'respiratory', 'gastroenterology', 'neurology',
        'emergency_medicine', 'psychiatry', 'rheumatology', 'endocrinology'
    ]

    stations_config = []
    station_num = 1

    for specialty in specialties:
        # Select 2 personas for this specialty (intermediate or advanced)
        personas = db.query(PatientPersona).filter(
            PatientPersona.specialty == specialty,
            PatientPersona.difficulty_level.in_(['intermediate', 'advanced']),
            PatientPersona.is_active == True
        ).order_by(func.random()).limit(2).all()

        if len(personas) < 2:
            raise HTTPException(
                status_code=500,
                detail=f"Insufficient personas for specialty: {specialty}"
            )

        for persona in personas:
            stations_config.append({
                'station': station_num,
                'persona_id': str(persona.persona_id),
                'specialty': specialty,
                'persona_code': persona.persona_code,
                'chief_complaint': persona.chief_complaint
            })
            station_num += 1

    # Step 3: Create mock_exams record
    mock_exam = MockExam(
        user_id=current_user.user_id,
        exam_date=request.exam_date,
        stations_config=stations_config,
        exam_state='scheduled',
        current_station=1
    )
    db.add(mock_exam)
    db.commit()
    db.refresh(mock_exam)

    return CreateMockExamResponse(
        exam_id=str(mock_exam.exam_id),
        stations=16,
        estimated_duration="2 hours 40 minutes",
        start_url=f"/mock-exam/{mock_exam.exam_id}/station/1",
        stations_config=mock_exam.stations_config
    )
```

**Request Example**:
```json
POST /api/v1/mock-exams
{
  "exam_date": "2026-02-16",
  "specialty_mix": "balanced"
}
```

**Response Example**:
```json
{
  "exam_id": "exam-uuid-1234",
  "stations": 16,
  "estimated_duration": "2 hours 40 minutes",
  "start_url": "/mock-exam/exam-uuid-1234/station/1",
  "stations_config": [
    {"station": 1, "persona_id": "card-uuid-1", "specialty": "cardiology", "chief_complaint": "Chest pain"},
    {"station": 2, "persona_id": "card-uuid-2", "specialty": "cardiology", "chief_complaint": "Palpitations"},
    ...
    {"station": 16, "persona_id": "endo-uuid-2", "specialty": "endocrinology", "chief_complaint": "Diabetes control"}
  ]
}
```

#### Endpoint 2: Get Mock Exam State (GET /api/v1/mock-exams/{exam_id})
**Purpose**: Retrieve current exam progress and station config

```python
class MockExamStateResponse(BaseModel):
    exam_id: str
    exam_state: str  # scheduled, in_progress, paused, completed, abandoned
    current_station: int  # 1-16
    stations_config: List[dict]
    actual_start: Optional[datetime]
    elapsed_time_minutes: Optional[int]
    total_score: Optional[int]
    overall_pass_fail: Optional[str]

@router.get("/api/v1/mock-exams/{exam_id}", response_model=MockExamStateResponse)
async def get_mock_exam_state(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current exam state and next station config."""

    exam = db.query(MockExam).filter(
        MockExam.exam_id == exam_id,
        MockExam.user_id == current_user.user_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    elapsed_time = None
    if exam.actual_start:
        elapsed_time = int((datetime.utcnow() - exam.actual_start).total_seconds() / 60)

    return MockExamStateResponse(
        exam_id=str(exam.exam_id),
        exam_state=exam.exam_state,
        current_station=exam.current_station,
        stations_config=exam.stations_config,
        actual_start=exam.actual_start,
        elapsed_time_minutes=elapsed_time,
        total_score=exam.total_score,
        overall_pass_fail=exam.overall_pass_fail
    )
```

#### Endpoint 3: Mark Station Complete (PUT /api/v1/mock-exams/{exam_id}/station/{station_number}/complete)
**Purpose**: Finalize station and progress to next station

```python
class MarkStationCompleteRequest(BaseModel):
    osce_attempt_id: str  # attempt_id returned from session creation

class StationCompleteResponse(BaseModel):
    station: int
    total_stations: int
    score: int
    pass_fail: str
    next_station_starts_in: int  # 5 seconds
    remaining_stations: List[int]

@router.put("/api/v1/mock-exams/{exam_id}/station/{station_number}/complete",
            response_model=StationCompleteResponse)
async def mark_station_complete(
    exam_id: str,
    station_number: int,
    request: MarkStationCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark station complete and progress to next.

    Logic:
    1. Validate exam ownership and state
    2. Validate station_number matches current_station
    3. Get osce_attempt and verify it's scored
    4. Increment current_station (if < 16)
    5. Check if exam_complete (station 16)
    6. Emit WebSocket event to all clients
    7. Return next station info
    """

    # Step 1: Get and validate exam
    exam = db.query(MockExam).filter(
        MockExam.exam_id == exam_id,
        MockExam.user_id == current_user.user_id,
        MockExam.exam_state == 'in_progress'
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found or not in progress")

    if exam.current_station != station_number:
        raise HTTPException(
            status_code=400,
            detail=f"Expected station {exam.current_station}, got {station_number}"
        )

    # Step 2: Get attempt and score
    attempt = db.query(OSCEAttempt).filter(
        OSCEAttempt.attempt_id == request.osce_attempt_id,
        OSCEAttempt.user_id == current_user.user_id,
        OSCEAttempt.station_number == station_number,
        OSCEAttempt.mock_exam_id == exam_id
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Attempt not found")

    score = db.query(OSCEScore).filter(
        OSCEScore.attempt_id == attempt.attempt_id
    ).first()

    if not score:
        raise HTTPException(status_code=400, detail="Station not yet scored")

    # Step 3: Progress exam
    is_final_station = (station_number == 16)

    if is_final_station:
        # Calculate overall exam score
        all_scores = db.query(OSCEScore).join(
            OSCEAttempt,
            OSCEScore.attempt_id == OSCEAttempt.attempt_id
        ).filter(
            OSCEAttempt.mock_exam_id == exam_id
        ).all()

        total_score = sum(s.total_score for s in all_scores)

        # Check for critical errors
        has_critical_errors = any(
            len(s.critical_errors) > 0 for s in all_scores
        )

        # Determine pass/fail
        overall_pass_fail = 'PASS' if (total_score >= 198 and not has_critical_errors) else 'FAIL'

        # Update exam
        exam.exam_state = 'completed'
        exam.actual_end = datetime.utcnow()
        exam.total_duration_minutes = int(
            (exam.actual_end - exam.actual_start).total_seconds() / 60
        )
        exam.total_score = total_score
        exam.overall_pass_fail = overall_pass_fail

        db.commit()

        # Queue report generation
        generate_mock_exam_report.delay(str(exam.exam_id))

        # Emit exam_complete event
        await broadcast_websocket_event(
            exam_id=str(exam.exam_id),
            event={
                'type': 'exam_complete',
                'total_score': total_score,
                'max_score': 240,
                'percentage': round(total_score / 240 * 100, 1),
                'pass_fail': overall_pass_fail,
                'timestamp': datetime.utcnow().isoformat()
            }
        )
    else:
        # Progress to next station
        exam.current_station += 1
        db.commit()

    # Emit station_complete event
    remaining = list(range(exam.current_station, 17))

    await broadcast_websocket_event(
        exam_id=str(exam.exam_id),
        event={
            'type': 'station_complete',
            'station': station_number,
            'total_stations': 16,
            'score': score.total_score,
            'pass_fail': score.pass_fail,
            'next_station': exam.current_station if not is_final_station else None,
            'next_station_starts_in': 5,
            'remaining_stations': remaining,
            'timestamp': datetime.utcnow().isoformat()
        }
    )

    return StationCompleteResponse(
        station=station_number,
        total_stations=16,
        score=score.total_score,
        pass_fail=score.pass_fail,
        next_station_starts_in=5,
        remaining_stations=remaining
    )
```

#### Endpoint 4: Get Exam Results (GET /api/v1/mock-exams/{exam_id}/results)
**Purpose**: Retrieve comprehensive exam results with station breakdown

```python
class StationResult(BaseModel):
    station: int
    specialty: str
    persona_code: str
    chief_complaint: str
    score: int
    max_score: int = 15
    pass_fail: str
    communication_score: int
    clinical_reasoning_score: int
    information_gathering_score: int
    management_score: int
    professionalism_score: int
    feedback: str
    critical_errors: List[dict]

class SpecialtyAnalysis(BaseModel):
    specialty: str
    stations: int
    total_score: int
    max_score: int
    percentage: float
    average_score: float

class MockExamResults(BaseModel):
    exam_id: str
    exam_date: date
    exam_state: str
    total_score: int
    max_score: int = 240
    percentage: float
    pass_fail: str
    actual_duration_minutes: int

    station_results: List[StationResult]
    specialty_breakdown: List[SpecialtyAnalysis]

    strengths: List[str]
    areas_for_improvement: List[str]

    overall_feedback: str

    report_url: Optional[str]
    report_generated_at: Optional[datetime]

@router.get("/api/v1/mock-exams/{exam_id}/results", response_model=MockExamResults)
async def get_mock_exam_results(
    exam_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive exam results with all 16 station scores and analysis.

    Only available for completed exams.
    """

    exam = db.query(MockExam).filter(
        MockExam.exam_id == exam_id,
        MockExam.user_id == current_user.user_id
    ).first()

    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    if exam.exam_state != 'completed':
        raise HTTPException(status_code=400, detail="Exam not yet completed")

    # Get all station results
    attempts = db.query(OSCEAttempt).filter(
        OSCEAttempt.mock_exam_id == exam_id
    ).order_by(OSCEAttempt.station_number).all()

    station_results = []
    strengths_set = set()
    weaknesses_set = set()
    specialty_scores = {}

    for attempt in attempts:
        score = db.query(OSCEScore).filter(
            OSCEScore.attempt_id == attempt.attempt_id
        ).first()

        persona = db.query(PatientPersona).filter(
            PatientPersona.persona_id == attempt.persona_id
        ).first()

        station_results.append(StationResult(
            station=attempt.station_number,
            specialty=persona.specialty,
            persona_code=persona.persona_code,
            chief_complaint=persona.chief_complaint,
            score=score.total_score,
            pass_fail=score.pass_fail,
            communication_score=score.communication_score,
            clinical_reasoning_score=score.clinical_reasoning_score,
            information_gathering_score=score.information_gathering_score,
            management_score=score.management_score,
            professionalism_score=score.professionalism_score,
            feedback=score.overall_feedback,
            critical_errors=score.critical_errors
        ))

        # Collect strengths and weaknesses
        if score.strengths:
            strengths_set.update(score.strengths)
        if score.areas_for_improvement:
            weaknesses_set.update(score.areas_for_improvement)

        # Build specialty breakdown
        if persona.specialty not in specialty_scores:
            specialty_scores[persona.specialty] = {'scores': [], 'stations': 0}
        specialty_scores[persona.specialty]['scores'].append(score.total_score)
        specialty_scores[persona.specialty]['stations'] += 1

    # Build specialty breakdown
    specialty_breakdown = []
    for specialty, data in specialty_scores.items():
        total = sum(data['scores'])
        max_score = data['stations'] * 15
        specialty_breakdown.append(SpecialtyAnalysis(
            specialty=specialty,
            stations=data['stations'],
            total_score=total,
            max_score=max_score,
            percentage=round(total / max_score * 100, 1),
            average_score=round(total / len(data['scores']), 1)
        ))

    return MockExamResults(
        exam_id=str(exam.exam_id),
        exam_date=exam.exam_date,
        exam_state=exam.exam_state,
        total_score=exam.total_score,
        percentage=round(exam.total_score / 240 * 100, 1),
        pass_fail=exam.overall_pass_fail,
        actual_duration_minutes=exam.total_duration_minutes,
        station_results=station_results,
        specialty_breakdown=specialty_breakdown,
        strengths=list(strengths_set)[:5],  # Top 5
        areas_for_improvement=list(weaknesses_set)[:5],
        overall_feedback=f"Strong performance across {len(specialty_breakdown)} specialties..." if exam.overall_pass_fail == 'PASS' else "Review weak areas before next attempt...",
        report_url=exam.report_url,
        report_generated_at=exam.report_generated_at
    )
```

### WebSocket Events

#### Event: station_complete
```json
{
  "type": "station_complete",
  "station": 5,
  "total_stations": 16,
  "score": 12,
  "pass_fail": "PASS",
  "next_station": 6,
  "next_station_starts_in": 5,
  "remaining_stations": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16],
  "timestamp": "2026-02-16T10:35:00Z"
}
```

#### Event: exam_complete
```json
{
  "type": "exam_complete",
  "total_score": 198,
  "max_score": 240,
  "percentage": 82.5,
  "pass_fail": "PASS",
  "estimated_amc_rank": "75th percentile",
  "timestamp": "2026-02-16T11:25:00Z"
}
```

---

## L - LOOP (Iterative Development)

### Phase 1: Database & API Foundation (35% of effort, 8-9 hours)
**Goal**: Implement mock exam orchestration endpoints and state machine

**Tasks**:
1. Enhance mock_exams table schema - 1 hour
2. Create persona auto-selection logic - 1.5 hours
3. Implement POST /api/v1/mock-exams - 1.5 hours
4. Implement GET /api/v1/mock-exams/{exam_id} - 45 min
5. Implement PUT /api/v1/mock-exams/{exam_id}/station/{n}/complete - 2 hours
6. Create v_mock_exam_results view - 1 hour
7. Implement GET /api/v1/mock-exams/{exam_id}/results - 1.5 hours

**Validation Gate**:
- [ ] All 4 endpoints functional with correct request/response models
- [ ] State machine transitions working (scheduled → in_progress → completed)
- [ ] Persona auto-selection creates balanced 16-station config in <2 sec
- [ ] Score aggregation correct (sum of 16 stations)
- [ ] Pass/fail logic correct (≥198/240 = PASS, no critical errors)
- [ ] Authorization checks prevent cross-user access

---

### Phase 2: Frontend & Real-Time (35% of effort, 8-9 hours)
**Goal**: Build mock exam UI with station progression and real-time WebSocket updates

**Tasks**:
1. Design MockExamStart component (exam overview, start button) - 1 hour
2. Implement station progression UI (Station N of 16, 8-min timer) - 1.5 hours
3. Implement 5-second break UI (countdown, next station loading) - 1 hour
4. Implement WebSocket integration for real-time station updates - 1.5 hours
5. Build results dashboard (overall score, station table, breakdown) - 2 hours
6. Implement PDF report viewer and download - 1 hour
7. Add exam state indicators (in progress, completed, abandoned) - 1 hour

**Validation Gate**:
- [ ] MockExamStart displays all 16 stations before exam begins
- [ ] Station progression auto-advances after 8-min timer or score received
- [ ] 5-second break countdown displays correctly
- [ ] Real-time WebSocket events update UI without page reload
- [ ] Results dashboard shows all 16 stations with scores
- [ ] Specialty breakdown chart renders correctly
- [ ] PDF report downloads successfully

---

### Phase 3: Reporting & Polish (30% of effort, 6-7 hours)
**Goal**: Generate professional PDF reports and comprehensive testing

**Tasks**:
1. Create Celery task for PDF report generation - 1.5 hours
2. Design PDF report layout (cover, scores, station breakdown, analysis) - 1.5 hours
3. Implement report generation with ReportLab/Weasyprint - 2 hours
4. Write unit tests for mock exam endpoints - 1.5 hours
5. Write integration tests for full exam flow - 1.5 hours
6. Performance testing (16-station orchestration, <3 sec station transitions) - 1 hour

**Validation Gate**:
- [ ] PDF report generates in <10 seconds
- [ ] Report includes all required sections (scores, breakdown, analysis, comparison)
- [ ] Report downloads from S3 successfully
- [ ] Test coverage ≥80%
- [ ] 100% test pass rate
- [ ] Performance targets met (station transitions <3 sec, score aggregation <1 sec)

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks (Database & API Foundation)

**Task 1.1**: Enhance mock_exams Table Schema
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Alembic migration with table enhancements
- **Acceptance Criteria**:
  - [ ] exam_state column added with CHECK constraint
  - [ ] actual_start, actual_end timestamps added
  - [ ] total_duration_minutes calculated field
  - [ ] current_station field (1-16)
  - [ ] total_score and overall_pass_fail fields
  - [ ] report_url and report_generated_at fields
  - [ ] Index on (user_id, exam_state)

**Task 1.2**: Persona Auto-Selection Logic
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Reusable function for balanced persona selection
- **Acceptance Criteria**:
  - [ ] Selects 2 personas per specialty (8 specialties = 16 total)
  - [ ] Filters by intermediate/advanced difficulty only
  - [ ] Execution time <2 seconds
  - [ ] Returns stations_config JSONB structure
  - [ ] Deterministic seed (reproducible if needed)

**Task 1.3**: Implement POST /api/v1/mock-exams
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Endpoint to create new mock exam
- **Acceptance Criteria**:
  - [ ] Creates MockExam record with scheduled state
  - [ ] Auto-selects 16 personas via Task 1.2
  - [ ] Returns exam_id, stations_config, start_url
  - [ ] Validates no active exam in progress
  - [ ] 201 Created status
  - [ ] <2 sec response time

**Task 1.4**: Implement GET /api/v1/mock-exams/{exam_id}
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Endpoint to get exam state and current station
- **Acceptance Criteria**:
  - [ ] Returns exam_state, current_station, stations_config
  - [ ] Calculates elapsed_time_minutes
  - [ ] Authorization check (user can only access own exams)
  - [ ] 404 if exam not found

**Task 1.5**: Implement PUT /api/v1/mock-exams/{exam_id}/station/{n}/complete
- **Effort**: 2 hours
- **Owner**: Backend Engineer
- **Deliverable**: Station completion and progression endpoint
- **Acceptance Criteria**:
  - [ ] Validates station_number matches current_station
  - [ ] Gets osce_attempt and verifies score exists
  - [ ] Increments current_station (if < 16)
  - [ ] Detects final station (16) and triggers exam completion
  - [ ] Calculates overall score (sum of 16 stations)
  - [ ] Determines pass/fail (≥198/240, no critical errors)
  - [ ] Emits WebSocket events (station_complete or exam_complete)
  - [ ] Queues PDF report generation for completed exams

**Task 1.6**: Create v_mock_exam_results View
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: SQL view for aggregated results
- **Acceptance Criteria**:
  - [ ] JOINs mock_exams, osce_attempts, osce_scores
  - [ ] Aggregates all 16 station scores
  - [ ] Calculates total_score, percentage, overall_pass_fail
  - [ ] Used by GET /results endpoint

**Task 1.7**: Implement GET /api/v1/mock-exams/{exam_id}/results
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Comprehensive results endpoint
- **Acceptance Criteria**:
  - [ ] Returns all 16 station results (station #, score, feedback, breakdown)
  - [ ] Includes specialty_breakdown (2 stations per specialty)
  - [ ] Extracts strengths and areas_for_improvement
  - [ ] Calculates overall_feedback
  - [ ] Returns report_url if available
  - [ ] 400 if exam not completed
  - [ ] <1 sec response time

---

### Phase 2 Tasks (Frontend & Real-Time)

**Task 2.1**: Design MockExamStart Component
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: React component showing exam overview
- **Acceptance Criteria**:
  - [ ] Displays "16-Station Mock Exam" header
  - [ ] Shows all 16 stations (station #, specialty, persona name)
  - [ ] Displays estimated duration: "2 hours 40 minutes"
  - [ ] Shows pass threshold: "198/240 (82.5%) required to pass"
  - [ ] "Start Exam" button calls POST /mock-exams
  - [ ] Confirmation modal: "You cannot pause or skip stations"

**Task 2.2**: Implement Station Progression UI
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: Station display with 8-minute timer
- **Acceptance Criteria**:
  - [ ] Displays "Station N of 16" indicator
  - [ ] Shows patient persona (name, age, opening statement)
  - [ ] 8-minute countdown timer (MM:SS format)
  - [ ] Timer turns red at 1-minute warning
  - [ ] Integrates with existing AI Patient chat UI (from PRD_002)
  - [ ] Auto-finalizes at 8:00 mark

**Task 2.3**: Implement 5-Second Break UI
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: Break screen between stations
- **Acceptance Criteria**:
  - [ ] Displays station result card (score, pass/fail, brief feedback)
  - [ ] "Next station in: 5, 4, 3, 2, 1..." countdown
  - [ ] Auto-advances to next station UI after 5 seconds
  - [ ] No manual action required

**Task 2.4**: Implement WebSocket Integration
- **Effort**: 1.5 hours
- **Owner**: Frontend Engineer
- **Deliverable**: Real-time event handling for exam progress
- **Acceptance Criteria**:
  - [ ] Connects to /ws/mock-exam/{exam_id}
  - [ ] Listens for station_complete events
  - [ ] Updates station result display in real-time
  - [ ] Listens for exam_complete events
  - [ ] Redirects to results page when exam finishes
  - [ ] Handles connection errors and reconnection

**Task 2.5**: Build Results Dashboard
- **Effort**: 2 hours
- **Owner**: Frontend Engineer
- **Deliverable**: Comprehensive results display
- **Acceptance Criteria**:
  - [ ] Overall score card (198/240, 82.5%, PASS badge)
  - [ ] Station-by-station table (16 rows)
  - [ ] Specialty breakdown (bar chart or grid)
  - [ ] Strengths section (top 5 strengths)
  - [ ] Areas for improvement section (top 5 weaknesses)
  - [ ] Overall feedback narrative
  - [ ] Responsive design (mobile + desktop)

**Task 2.6**: Implement PDF Report Viewer
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: PDF viewer and download UI
- **Acceptance Criteria**:
  - [ ] "Download Report" button
  - [ ] Displays "Report generating..." while Celery task runs
  - [ ] Shows "Report Ready" when report_url available
  - [ ] Opens PDF viewer in modal (pdf.js library)
  - [ ] Download button for PDF

**Task 2.7**: Add Exam State Indicators
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: Visual indicators for exam state
- **Acceptance Criteria**:
  - [ ] "In Progress" badge during exam (Station N of 16)
  - [ ] "Completed" badge after exam finishes
  - [ ] "Abandoned" state handled (exam paused/abandoned)
  - [ ] Progress bar showing stations completed

---

### Phase 3 Tasks (Reporting & Polish)

**Task 3.1**: Create Celery Task for PDF Generation
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: Async task to generate PDF reports
- **Acceptance Criteria**:
  - [ ] Task queued from PUT /station/{n}/complete when exam_state = 'completed'
  - [ ] Loads all exam data (16 station scores, transcripts, feedback)
  - [ ] Generates HTML layout with ReportLab/Weasyprint
  - [ ] Renders to PDF
  - [ ] Uploads to S3
  - [ ] Updates mock_exams.report_url
  - [ ] Sets report_generated_at timestamp
  - [ ] Execution time <10 seconds

**Task 3.2**: Design PDF Report Layout
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer + Designer
- **Deliverable**: Professional PDF template
- **Sections**:
  - [ ] Cover page (student name, exam date, overall score, pass/fail)
  - [ ] Executive summary (score breakdown, strengths, weaknesses)
  - [ ] Station-by-station analysis (16 pages, one per station)
  - [ ] Specialty breakdown (chart)
  - [ ] Comparison to pass threshold (visual gauge)
  - [ ] Recommendations for improvement

**Task 3.3**: Implement PDF Generation Logic
- **Effort**: 2 hours
- **Owner**: Backend Engineer
- **Deliverable**: Complete PDF generation pipeline
- **Acceptance Criteria**:
  - [ ] Uses ReportLab or Weasyprint for rendering
  - [ ] Generates charts (specialty breakdown bar chart)
  - [ ] Includes all station scores and feedback
  - [ ] Professional formatting (colors, fonts, spacing)
  - [ ] PDF file size <5 MB

**Task 3.4**: Write Unit Tests
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: Unit tests for mock exam logic
- **Test Cases**:
  - [ ] Test persona auto-selection (returns 16 balanced personas)
  - [ ] Test state machine transitions (scheduled → in_progress → completed)
  - [ ] Test score aggregation (sum of 16 stations)
  - [ ] Test pass/fail logic (≥198/240 = PASS)
  - [ ] Test critical error override (critical errors force FAIL)

**Task 3.5**: Write Integration Tests
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer / Testing QA
- **Deliverable**: End-to-end exam flow tests
- **Test Cases**:
  - [ ] Create exam → verify stations_config
  - [ ] Start exam → verify exam_state = 'in_progress'
  - [ ] Complete stations 1-15 → verify progression
  - [ ] Complete station 16 → verify exam_state = 'completed'
  - [ ] Get results → verify score aggregation correct
  - [ ] Unauthorized access → verify 403 error

**Task 3.6**: Performance Testing
- **Effort**: 1 hour
- **Owner**: Backend Engineer / DevOps
- **Deliverable**: Performance benchmarks
- **Tests**:
  - [ ] Exam creation <2 seconds
  - [ ] Station completion/progression <3 seconds
  - [ ] Score aggregation <1 second
  - [ ] Results retrieval <1 second
  - [ ] PDF generation <10 seconds
  - [ ] Handle 100 concurrent exams

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] POST /api/v1/mock-exams creates exam with auto-selected 16 balanced personas
- [ ] GET /api/v1/mock-exams/{exam_id} returns exam state and current station
- [ ] PUT /api/v1/mock-exams/{exam_id}/station/{n}/complete progresses exam
- [ ] GET /api/v1/mock-exams/{exam_id}/results returns all 16 station scores + aggregated results
- [ ] State machine working (scheduled → in_progress → completed)
- [ ] Score aggregation correct (sum of 16 stations, max 240)
- [ ] Pass/fail logic correct (≥198/240 without critical errors = PASS)
- [ ] WebSocket events emit correctly (station_complete, exam_complete)
- [ ] PDF report generation completes in <10 seconds
- [ ] Frontend displays all 16 stations before exam start
- [ ] Station progression UI works seamlessly (8-min timer, 5-sec break)
- [ ] Results dashboard shows all required data (scores, breakdown, analysis)

#### Quality Requirements
- [ ] **Test Coverage**: ≥80% (unit + integration)
- [ ] **Test Pass Rate**: 100%
- [ ] **Code Quality**: No linting errors, follows FastAPI best practices
- [ ] **Documentation**: API docs complete, PDF template documented
- [ ] **Migration Success**: Database enhancements run without errors
- [ ] **Performance**: All targets met (<2 sec exam creation, <3 sec station transitions)

#### Performance Requirements
- [ ] **Exam Creation**: <2 seconds
- [ ] **Persona Auto-Selection**: <2 seconds (16 personas selected and configured)
- [ ] **Station Progression**: <3 seconds
- [ ] **Score Aggregation**: <1 second
- [ ] **Results Retrieval**: <1 second
- [ ] **PDF Generation**: <10 seconds
- [ ] **API Response Times**: <500ms (p95)

#### Security Requirements
- [ ] **Authorization**: Users can only access their own exams (403 if unauthorized)
- [ ] **JWT Authentication**: All endpoints require valid token
- [ ] **Input Validation**: Pydantic schemas validate all inputs
- [ ] **GDPR Compliance**: ON DELETE CASCADE for user data

#### Australian Medical Compliance
- [ ] **Pass Threshold**: ≥198/240 (82.5%) follows AMC guideline
- [ ] **AMC Rubric**: Scoring uses 15-mark breakdown (Communication, Clinical Reasoning, etc.)
- [ ] **Critical Error Override**: Critical errors force FAIL regardless of score
- [ ] **Specialty Balance**: 2 stations per specialty × 8 specialties = 16 stations
- [ ] **Exam Format**: 8 min per station × 16 stations = 2h 40m total (matches real OSCE)

### Testing Requirements

#### Unit Tests (≥80% coverage)
```python
# Test persona auto-selection
def test_auto_select_16_personas_balanced():
    """Verify 2 personas per specialty, intermediate/advanced difficulty"""
    personas = auto_select_exam_personas()
    assert len(personas) == 16
    specialty_counts = Counter([p['specialty'] for p in personas])
    assert all(count == 2 for count in specialty_counts.values())

# Test score aggregation
def test_aggregate_16_station_scores():
    """Verify sum of 16 stations correct"""
    exam = create_exam()
    complete_all_stations(exam, scores=[12, 11, 13, 10, 12, 14, 11, 12, 13, 12, 11, 13, 12, 10, 12, 13])
    total = aggregate_scores(exam)
    assert total == 192  # Sum of all scores

# Test pass/fail logic
def test_pass_fail_logic():
    """Verify ≥198/240 without critical errors = PASS"""
    assert determine_pass_fail(score=198, critical_errors=[]) == 'PASS'
    assert determine_pass_fail(score=197, critical_errors=[]) == 'FAIL'
    assert determine_pass_fail(score=200, critical_errors=[{'error': 'missed_red_flag'}]) == 'FAIL'
```

#### Integration Tests (API Endpoints)
```python
# Test complete exam flow
async def test_complete_mock_exam_flow():
    """E2E: Create → Start → Complete 16 stations → View results"""
    # Create exam
    exam = create_mock_exam(user_id)
    assert exam.exam_state == 'scheduled'

    # Start exam
    start_exam(exam_id)
    assert exam.exam_state == 'in_progress'

    # Complete stations 1-16
    for station_num in range(1, 17):
        complete_station(exam_id, station_num)

    # Verify exam completed
    assert exam.exam_state == 'completed'
    assert exam.total_score >= 0 and exam.total_score <= 240

    # Get results
    results = get_mock_exam_results(exam_id)
    assert len(results.station_results) == 16
    assert results.overall_pass_fail in ['PASS', 'FAIL']
```

### Documentation Deliverables

#### 1. API Documentation
```markdown
# Mock Exam Mode API

## Endpoints

### POST /api/v1/mock-exams
Create 16-station mock exam with auto-selected personas.
- Request: {exam_date, specialty_mix}
- Response: {exam_id, stations: 16, estimated_duration, start_url, stations_config}
- Status: 201 Created

### GET /api/v1/mock-exams/{exam_id}
Get current exam state and next station config.
- Response: {exam_id, exam_state, current_station, stations_config, elapsed_time}
- Status: 200 OK

### PUT /api/v1/mock-exams/{exam_id}/station/{n}/complete
Mark station complete and progress to next.
- Request: {osce_attempt_id}
- Response: {station, score, pass_fail, next_station_starts_in: 5}
- Status: 200 OK

### GET /api/v1/mock-exams/{exam_id}/results
Get comprehensive exam results.
- Response: {total_score, pass_fail, station_results: [16], specialty_breakdown, report_url}
- Status: 200 OK
```

#### 2. PDF Report Template
- Cover page with score summary
- 16 station detail pages
- Specialty breakdown chart
- Strengths/weaknesses analysis
- Recommendations

#### 3. WebSocket Events Documentation
- station_complete event structure
- exam_complete event structure
- Error event handling

### Deployment Checklist

#### Pre-Deployment
- [ ] All 4 endpoints implemented and tested
- [ ] Frontend components complete
- [ ] PDF generation tested
- [ ] Test coverage ≥80%
- [ ] Performance targets validated
- [ ] Security review complete

#### Deployment (Development)
- [ ] Run database migration
- [ ] Verify table enhancements
- [ ] Deploy backend endpoints
- [ ] Deploy frontend components
- [ ] Test full exam flow (create → complete → results)
- [ ] Verify WebSocket events
- [ ] Verify PDF generation

#### Post-Deployment
- [ ] Monitor API response times
- [ ] Monitor exam completion rates
- [ ] Check PDF generation job queue
- [ ] Verify no exam interruptions
- [ ] Collect pass/fail rate statistics

---

## Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ POST /mock-exams creates exam with auto-selected 16 personas in <2 sec
2. ✅ All 4 API endpoints functional and tested
3. ✅ State machine working (scheduled → in_progress → completed)
4. ✅ Score aggregation correct (sum of 16 stations)
5. ✅ Pass/fail logic correct (≥198/240 = PASS)
6. ✅ Frontend displays all 16 stations before exam
7. ✅ Station progression seamless (8-min timer, 5-sec break)
8. ✅ Results dashboard complete (scores, breakdown, analysis)
9. ✅ PDF report generation working (<10 sec)
10. ✅ WebSocket events real-time
11. ✅ Test coverage ≥80%, 100% pass rate
12. ✅ Performance targets met
13. ✅ Authoriz checks prevent cross-user access
14. ✅ Documentation complete

**Sign-off Required From**:
- [ ] Backend Engineer (endpoints functional, tests passing)
- [ ] Frontend Engineer (UI complete, real-time working)
- [ ] PM Coordinator (requirements met, quality validated)
- [ ] Testing QA (test coverage ≥80%, 100% pass rate, performance benchmarks met)

---

## 📎 Appendices

### Appendix A: Mock Exam Flow Diagram
```
[Start] → POST /mock-exams → exam_state: 'scheduled'
            ↓
         16 personas auto-selected (2 per specialty)
            ↓
         Student views exam overview
            ↓
         Click "Start Exam"
            ↓
         PUT /start → exam_state: 'in_progress'
            ↓
         FOR station = 1 TO 16:
         ├─ Load Station UI (8-min timer, patient intro)
         ├─ Create osce_attempt
         ├─ 8-minute AI Patient conversation
         ├─ Auto-finalize at 8:00
         ├─ AI Examiner scores session
         ├─ PUT /station/{n}/complete
         ├─ Emit WebSocket: station_complete
         ├─ Display result card (score, feedback)
         ├─ 5-second break countdown
         └─ Auto-load next station
            ↓
         GET /results → Aggregated scores, specialty breakdown
            ↓
         Celery: generate_mock_exam_report()
            ↓
         Display results dashboard + PDF download
            ↓
         [Complete]
```

### Appendix B: Scoring Aggregation Example
```
Station  Specialty        Score  Pass/Fail
─────────────────────────────────────────
   1     Cardiology        13    PASS
   2     Cardiology        12    PASS
   3     Respiratory       11    PASS
   4     Respiratory       12    PASS
   5     Gastro            13    PASS
   6     Gastro            10    PASS
   7     Neurology         12    PASS
   8     Neurology         12    PASS
   9     Emergency         14    PASS
  10     Emergency         11    PASS
  11     Psychiatry        13    PASS
  12     Psychiatry        12    PASS
  13     Rheumatology      11    PASS
  14     Rheumatology      12    PASS
  15     Endocrinology     12    PASS
  16     Endocrinology     13    PASS
─────────────────────────────────────────
TOTAL:                    198    PASS ✅

Percentage: 198/240 = 82.5%
Pass Threshold: ≥198/240 (82.5%) = PASS
Result: PASS (no critical errors detected)
```

### Appendix C: Related PRDs
- **Depends On**: PRD_001 (Database), PRD_002 (WebSocket), PRD_003 (AI Patient), PRD_004 (AI Examiner)
- **Blocks**: None (completes exam functionality)
- **Related**: Frontend dashboard PRDs, reporting analytics

---

**Document Status**: Complete
**Created**: 2026-02-16
**Version**: 1.0
**Estimated Effort**: 20-24 hours
**File Size**: ~42 KB
