# EMR Practice System - Database Integration

**Version**: 1.0
**Date**: 2026-02-03
**Purpose**: Link EMR practice system with existing irStudy database (MCQs, OSCEs)

---

## Integration Overview

The EMR practice system will **share the same database** as the main irStudy platform, adding new tables while linking to existing user accounts and progress tracking.

### Architecture Decision

```
Main irStudy Database
├── Existing Tables
│   ├── users (SHARED)
│   ├── mcqs
│   ├── osces
│   ├── user_progress (SHARED)
│   └── study_sessions
└── NEW EMR Tables
    ├── emr_sessions (links to users)
    ├── emr_soap_notes
    ├── emr_prescriptions
    ├── emr_pathology_orders
    ├── emr_validation_results
    └── emr_scenarios (links to osces)
```

---

## Shared Tables

### 1. Users Table (Existing - SHARED)

The EMR system uses the **same user accounts** as MCQs/OSCEs:

```sql
-- Existing users table (already exists)
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP
);
```

**EMR Integration**:
- Same JWT authentication
- User logs in once, accesses MCQs, OSCEs, AND EMR practice
- Single user profile across all features

### 2. User Progress Table (Existing - EXTENDED)

Extend existing progress table to include EMR metrics:

```sql
-- Existing user_progress table
CREATE TABLE user_progress (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),

    -- Existing MCQ/OSCE metrics
    mcqs_completed INTEGER DEFAULT 0,
    mcqs_correct INTEGER DEFAULT 0,
    osces_completed INTEGER DEFAULT 0,
    osce_average_score FLOAT,

    -- NEW: EMR practice metrics
    emr_sessions_completed INTEGER DEFAULT 0,
    emr_soap_notes_written INTEGER DEFAULT 0,
    emr_prescriptions_written INTEGER DEFAULT 0,
    emr_average_score FLOAT,
    emr_total_time_minutes INTEGER DEFAULT 0,

    last_updated TIMESTAMP DEFAULT NOW()
);
```

**Benefits**:
- Unified progress dashboard (MCQs + OSCEs + EMR in one view)
- Track improvement across all study modalities
- Compare performance (e.g., "weak in cardiology MCQs AND EMR prescriptions")

---

## EMR-Specific Tables

### 1. EMR Sessions Table

```sql
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) NOT NULL,

    -- Link to OSCE scenarios (optional)
    linked_osce_id UUID REFERENCES osces(id),

    -- Mock patient data
    patient_id UUID REFERENCES mock_patients(id) NOT NULL,

    -- Session details
    emr_type VARCHAR(50) NOT NULL, -- 'cerner' or 'epic'
    status VARCHAR(50) DEFAULT 'active', -- 'active', 'completed', 'expired'

    -- Timestamps
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,

    -- Performance metrics
    time_elapsed_seconds INTEGER DEFAULT 0,
    words_typed INTEGER DEFAULT 0,
    wpm INTEGER DEFAULT 0,
    auto_saves_count INTEGER DEFAULT 0,

    -- Scores (after validation)
    overall_score INTEGER,
    clinical_reasoning_score INTEGER,
    documentation_score INTEGER,
    compliance_score INTEGER,
    safety_score INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_emr_sessions_user ON emr_sessions(user_id);
CREATE INDEX idx_emr_sessions_osce ON emr_sessions(linked_osce_id);
```

### 2. EMR SOAP Notes Table

```sql
CREATE TABLE emr_soap_notes (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES emr_sessions(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES mock_patients(id),

    -- SOAP sections (stored as JSONB for flexibility)
    subjective JSONB NOT NULL,
    objective JSONB NOT NULL,
    assessment JSONB NOT NULL,
    plan JSONB NOT NULL,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP DEFAULT NOW(),
    auto_save_enabled BOOLEAN DEFAULT TRUE,

    -- Validation
    validation_result_id UUID REFERENCES emr_validation_results(id)
);

CREATE INDEX idx_soap_notes_session ON emr_soap_notes(session_id);
```

### 3. EMR Prescriptions Table

```sql
CREATE TABLE emr_prescriptions (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES emr_sessions(id) ON DELETE CASCADE,
    patient_id UUID REFERENCES mock_patients(id),

    -- Prescription details (array of medications)
    medications JSONB NOT NULL,
    prescriber_number VARCHAR(50) NOT NULL,

    -- Validation
    validation_result_id UUID REFERENCES emr_validation_results(id),

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_prescriptions_session ON emr_prescriptions(session_id);
```

### 4. EMR Validation Results Table

```sql
CREATE TABLE emr_validation_results (
    id UUID PRIMARY KEY,
    session_id UUID REFERENCES emr_sessions(id),
    content_type VARCHAR(50) NOT NULL, -- 'soap_note', 'prescription', 'pathology'
    content_id UUID NOT NULL,

    -- Validation results (JSONB for flexibility)
    validation_data JSONB NOT NULL,

    -- Scores
    overall_score INTEGER,
    layer1_status VARCHAR(50),
    layer2_status VARCHAR(50),
    layer3_status VARCHAR(50),

    -- Performance
    total_duration_ms INTEGER,

    validated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_validation_session ON emr_validation_results(session_id);
```

### 5. Mock Patients Table

```sql
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL,
    sex VARCHAR(10) NOT NULL,
    mrn VARCHAR(50) UNIQUE NOT NULL, -- Medical Record Number

    -- Medical history
    allergies JSONB DEFAULT '[]',
    current_medications JSONB DEFAULT '[]',
    past_medical_history JSONB DEFAULT '[]',
    active_problems JSONB DEFAULT '[]',

    -- Demographics
    location VARCHAR(255),

    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6. EMR Scenarios Table (Links to OSCEs)

```sql
CREATE TABLE emr_scenarios (
    id UUID PRIMARY KEY,

    -- Link to existing OSCE
    osce_id UUID REFERENCES osces(id),

    -- Scenario details
    title VARCHAR(255) NOT NULL,
    description TEXT,
    patient_id UUID REFERENCES mock_patients(id),

    -- Expected content (for auto-grading)
    expected_diagnosis VARCHAR(255),
    expected_differentials JSONB,
    expected_investigations JSONB,
    expected_management JSONB,

    -- Difficulty
    difficulty VARCHAR(50), -- 'beginner', 'intermediate', 'advanced'

    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_scenarios_osce ON emr_scenarios(osce_id);
```

---

## Integration Points

### 1. User Authentication (Shared JWT)

```python
# backend/src/services/auth_service.py

# SAME authentication service used by MCQs, OSCEs, and EMR
class AuthService:
    @staticmethod
    def create_access_token(user_id: UUID) -> str:
        """
        Creates JWT token valid for ALL irStudy features
        (MCQs, OSCEs, EMR practice)
        """
        return jwt.encode({
            "sub": str(user_id),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }, settings.SECRET_KEY)
```

**Flow**:
```
User Login → JWT Token → Valid for:
    ├── MCQs (/api/v1/mcqs)
    ├── OSCEs (/api/v1/osces)
    └── EMR (/api/v1/emr-sessions)
```

### 2. Unified Progress Dashboard

```python
# backend/src/api/v1/progress.py

@router.get("/api/v1/progress/user")
async def get_user_progress(current_user: User = Depends(get_current_user)):
    """
    Returns unified progress across MCQs, OSCEs, AND EMR
    """

    progress = await db.execute(
        select(UserProgress).where(UserProgress.user_id == current_user.id)
    )

    return {
        "mcq_stats": {
            "completed": progress.mcqs_completed,
            "accuracy": progress.mcqs_correct / progress.mcqs_completed if progress.mcqs_completed > 0 else 0
        },
        "osce_stats": {
            "completed": progress.osces_completed,
            "average_score": progress.osce_average_score
        },
        "emr_stats": {  # NEW
            "sessions_completed": progress.emr_sessions_completed,
            "soap_notes_written": progress.emr_soap_notes_written,
            "average_score": progress.emr_average_score,
            "time_spent_minutes": progress.emr_total_time_minutes
        }
    }
```

### 3. OSCE → EMR Practice Integration

**Scenario**: After completing an OSCE, student can practice writing SOAP note for the same case in EMR

```python
# backend/src/api/v1/emr_sessions.py

@router.post("/api/v1/emr-sessions/from-osce/{osce_id}")
async def create_emr_session_from_osce(
    osce_id: UUID,
    emr_type: str,  # 'cerner' or 'epic'
    current_user: User = Depends(get_current_user)
):
    """
    Create EMR practice session based on completed OSCE
    """

    # Get OSCE details
    osce = await db.get(OSCE, osce_id)

    # Find or create EMR scenario linked to this OSCE
    scenario = await db.execute(
        select(EMRScenario).where(EMRScenario.osce_id == osce_id)
    )

    if not scenario:
        # Create scenario from OSCE data
        scenario = EMRScenario(
            osce_id=osce_id,
            title=osce.title,
            description=osce.scenario_description,
            patient_id=...,  # Create mock patient from OSCE
            expected_diagnosis=osce.expected_findings
        )

    # Create EMR session
    emr_session = EMRSession(
        user_id=current_user.id,
        linked_osce_id=osce_id,  # LINK TO OSCE
        patient_id=scenario.patient_id,
        emr_type=emr_type,
        expires_at=datetime.utcnow() + timedelta(minutes=15)
    )

    await db.commit()

    return {
        "session_id": emr_session.id,
        "osce_title": osce.title,
        "patient": {...},
        "scenario": {...}
    }
```

**User Flow**:
```
1. Student completes OSCE: "45F with chest pain"
2. UI shows: "Practice documenting this case in EMR? [Yes]"
3. Click Yes → Opens Cerner/Epic with same patient
4. Student writes SOAP note for same case
5. Validation compares against OSCE expected findings
```

### 4. Topic-Based Practice

Link EMR practice to MCQ topics:

```python
# Student weak in "Cardiology" MCQs
# System suggests: "Practice cardiology SOAP notes in EMR"

@router.get("/api/v1/emr-sessions/suggested")
async def get_suggested_emr_practice(current_user: User = Depends(get_current_user)):
    """
    Suggest EMR scenarios based on weak MCQ/OSCE topics
    """

    # Analyze user's MCQ performance
    weak_topics = await analyze_mcq_performance(current_user.id)
    # Example: ["cardiology", "respiratory"]

    # Get EMR scenarios in weak topics
    scenarios = await db.execute(
        select(EMRScenario)
        .join(OSCE)
        .where(OSCE.topic.in_(weak_topics))
        .limit(5)
    )

    return {
        "weak_topics": weak_topics,
        "suggested_scenarios": scenarios,
        "message": "Practice these EMR cases to improve in weak areas"
    }
```

---

## Database Migration Strategy

### Step 1: Extend Existing Tables

```sql
-- Alembic migration: Add EMR columns to user_progress
ALTER TABLE user_progress
ADD COLUMN emr_sessions_completed INTEGER DEFAULT 0,
ADD COLUMN emr_soap_notes_written INTEGER DEFAULT 0,
ADD COLUMN emr_prescriptions_written INTEGER DEFAULT 0,
ADD COLUMN emr_average_score FLOAT,
ADD COLUMN emr_total_time_minutes INTEGER DEFAULT 0;
```

### Step 2: Create New EMR Tables

```bash
# Generate Alembic migration
cd backend
alembic revision --autogenerate -m "add_emr_tables"

# Migration will create:
# - emr_sessions
# - emr_soap_notes
# - emr_prescriptions
# - emr_pathology_orders
# - emr_validation_results
# - mock_patients
# - emr_scenarios

alembic upgrade head
```

### Step 3: Seed Mock Patients

```python
# backend/scripts/seed_mock_patients.py

mock_patients = [
    {
        "name": "Sarah Johnson",
        "age": 45,
        "sex": "F",
        "mrn": "12345678",
        "allergies": [
            {"allergen": "Penicillin", "reaction": "Anaphylaxis", "severity": "severe"}
        ],
        "current_medications": [
            {"name": "Metformin", "dose": "500mg", "frequency": "BD"}
        ],
        "active_problems": ["Type 2 Diabetes", "Hypertension"]
    },
    # ... 20+ more mock patients
]

for patient_data in mock_patients:
    patient = MockPatient(**patient_data)
    db.add(patient)

db.commit()
```

---

## API Integration

### Unified Backend Routes

```python
# backend/src/main.py

app = FastAPI(title="irStudy Complete Platform")

# Existing routes
app.include_router(mcqs.router, prefix="/api/v1/mcqs", tags=["MCQs"])
app.include_router(osces.router, prefix="/api/v1/osces", tags=["OSCEs"])
app.include_router(progress.router, prefix="/api/v1/progress", tags=["Progress"])

# NEW: EMR routes
app.include_router(emr_sessions.router, prefix="/api/v1/emr-sessions", tags=["EMR Sessions"])
app.include_router(emr_soap_notes.router, prefix="/api/v1/emr/soap-notes", tags=["EMR SOAP Notes"])
app.include_router(emr_prescriptions.router, prefix="/api/v1/emr/prescriptions", tags=["EMR Prescriptions"])
app.include_router(emr_validation.router, prefix="/api/v1/emr/validation", tags=["EMR Validation"])
```

### Frontend Integration

```typescript
// frontend/src/pages/Dashboard.tsx

export const Dashboard: React.FC = () => {
  const { data: progress } = useUserProgress();

  return (
    <div className="dashboard">
      {/* MCQ Stats */}
      <StatCard
        title="MCQs"
        completed={progress.mcq_stats.completed}
        accuracy={progress.mcq_stats.accuracy}
      />

      {/* OSCE Stats */}
      <StatCard
        title="OSCEs"
        completed={progress.osce_stats.completed}
        score={progress.osce_stats.average_score}
      />

      {/* NEW: EMR Stats */}
      <StatCard
        title="EMR Practice"
        completed={progress.emr_stats.sessions_completed}
        score={progress.emr_stats.average_score}
        timeSpent={progress.emr_stats.time_spent_minutes}
      />

      {/* Suggested Practice */}
      <SuggestedPractice
        weakTopics={progress.weak_topics}
        suggestedOSCEs={...}
        suggestedEMRScenarios={...}  // NEW
      />
    </div>
  );
};
```

---

## Benefits of Integrated Approach

### 1. Single User Account
- ✅ One login for MCQs, OSCEs, and EMR
- ✅ Unified user profile
- ✅ Single JWT authentication

### 2. Comprehensive Progress Tracking
- ✅ See all study activities in one dashboard
- ✅ Identify weak topics across all modalities
- ✅ Track improvement over time

### 3. Cross-Feature Learning
- ✅ OSCE → EMR practice (same patient case)
- ✅ Weak MCQ topics → Suggested EMR scenarios
- ✅ EMR performance → Personalized MCQ recommendations

### 4. Simplified Deployment
- ✅ Single database (PostgreSQL)
- ✅ Single backend API
- ✅ Shared authentication
- ✅ Easier to maintain

---

## Implementation Checklist

### Database Integration
- [ ] Extend `user_progress` table with EMR columns
- [ ] Create new EMR tables (sessions, soap_notes, prescriptions, etc.)
- [ ] Create `mock_patients` table
- [ ] Create `emr_scenarios` table with OSCE links
- [ ] Add foreign key relationships
- [ ] Create database indexes

### Backend Integration
- [ ] Add EMR routes to main FastAPI app
- [ ] Reuse existing auth service (JWT)
- [ ] Extend progress API to include EMR stats
- [ ] Create OSCE → EMR session endpoint
- [ ] Create suggested practice endpoint

### Frontend Integration
- [ ] Add EMR stats to dashboard
- [ ] Create "Practice in EMR" button on OSCE completion
- [ ] Show suggested EMR scenarios based on weak topics
- [ ] Unified navigation (MCQs | OSCEs | EMR Practice)

---

## Example: Complete User Flow

```
1. User logs in → JWT token valid for all features

2. Dashboard shows:
   - MCQs: 45/100 completed (67% accuracy)
   - OSCEs: 12/50 completed (78 average score)
   - EMR Practice: 5 sessions (82 average score)
   - Weak Topic: Cardiology

3. User clicks "Suggested Practice"
   → Shows:
     - Cardiology MCQs (20 questions)
     - Cardiology OSCEs (3 scenarios)
     - Cardiology EMR practice (2 SOAP note scenarios) ← NEW

4. User completes OSCE: "45F with chest pain"
   → Score: 85/100
   → UI shows: "Practice documenting this case in EMR? [Yes]"

5. User clicks Yes
   → Opens Cerner PowerChart
   → Same patient: "Sarah Johnson, 45F, chest pain"
   → User writes SOAP note
   → Validation compares against OSCE expected findings

6. After EMR session:
   → Overall EMR score: 87/100
   → Clinical reasoning: 26/30
   → Documentation: 22/25
   → PBS compliance: 19/20
   → Progress updated in database

7. Dashboard now shows:
   - EMR Practice: 6 sessions (83 average score) ← Updated
```

---

**Document Version**: 1.0
**Last Updated**: 2026-02-03
**Status**: ✅ Database Integration Designed
**Integration Type**: Unified database with shared users and cross-feature linking

