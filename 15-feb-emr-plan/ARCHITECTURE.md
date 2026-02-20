# Epic EHR Practice System - Integration Architecture

**Document Version**: 1.0
**Date**: 2026-02-15
**Status**: Approved - Ready for Implementation

---

## Executive Summary

This document defines the integration architecture for implementing a high-fidelity Epic EHR simulation within the irStudy medical education platform. The architecture prioritizes **unified user experience**, **full integration** with existing OSCE/MCQ/video content, and **Australian medical standards compliance**.

---

## 1. Architecture Decision: Unified Application Approach

### 1.1 Decision

**SELECTED: Option A - Full Integration into Main Application**

Migrate Epic EHR UI components from `/emr-frontend/` (Tailwind CSS) into `/frontend/` (Material-UI v7) for a unified, cohesive user experience.

### 1.2 Rationale

| Factor | Option A (Unified) | Option B (Separate) |
|--------|-------------------|---------------------|
| **User Experience** | ✅ Seamless navigation between MCQ/OSCE/EMR | ❌ Context switching between apps |
| **Authentication** | ✅ Single JWT session | ⚠️ Shared auth module needed |
| **Design Consistency** | ✅ Material-UI throughout | ❌ Tailwind vs MUI inconsistency |
| **Code Reusability** | ✅ Share components (StatCard, Timer, etc.) | ⚠️ Duplicate components |
| **Maintenance** | ✅ Single codebase, one build | ❌ Two repos, two builds |
| **Bundle Size** | ✅ Shared dependencies | ❌ Duplicate React/MUI bundles |
| **Integration** | ✅ Native (same state management) | ⚠️ API/iframe integration |
| **Development Speed** | ⚠️ Initial migration effort | ✅ Use existing EMR code |

**Verdict**: Option A provides superior long-term maintainability and user experience, despite initial migration effort (~2-3 days).

### 1.3 Migration Strategy

```
/emr-frontend/src/components/epic/
├── EpicSidebar.tsx (Tailwind + Framer Motion)
├── EpicPatientBanner.tsx (Tailwind)
└── EpicNoteEditor.tsx (Tailwind + Zustand)

              ↓ MIGRATE TO ↓

/frontend/src/components/emr/epic/
├── EpicSidebar.tsx (Material-UI + Emotion)
├── EpicPatientBanner.tsx (Material-UI)
└── EpicSOAPEditor.tsx (Material-UI + React Hook Form)
```

**Key Changes**:
- Tailwind classes → Material-UI `sx` prop / `styled` components
- Framer Motion → MUI transitions (Fade, Slide, Grow)
- Zustand → TanStack Query (align with existing MCQ/OSCE state management)
- Lucide React icons → Material-UI icons (consistency)

---

## 2. System Architecture Overview

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    irStudy Web Application                       │
│                     (React + Material-UI v7)                     │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard  │  MCQ Practice  │  OSCE Practice  │  EMR Practice  │
│             │                │                 │  (NEW)         │
└──────────────┬──────────────────────────────────────────────────┘
               │
               │ JWT Authentication (existing)
               │ Axios + TanStack Query
               │
┌──────────────▼──────────────────────────────────────────────────┐
│                  FastAPI Backend (Python 3.11+)                  │
├─────────────────────────────────────────────────────────────────┤
│  /api/v1/mcqs/  │  /api/v1/osces/  │  /api/v1/emr/ (NEW)       │
│                 │                  │                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         AI Validation Agents (NEW)                        │  │
│  │  - SOAPValidator (Claude Sonnet 4.5)                      │  │
│  │  - PrescriptionValidator (PBS compliance)                 │  │
│  │  - PathologyValidator (MBS compliance)                    │  │
│  └──────────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────────┐
│                     Data Layer                                   │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL (irstudy_medical)  │  Qdrant (RAG)  │  Redis Cache  │
│  - users, mcqs, osces          │  - 9,950 med   │  - Sessions   │
│  - emr_sessions (NEW)          │    chunks      │  - Rate       │
│  - emr_soap_notes (NEW)        │  - eTG, AMH    │    limiting   │
│  - emr_prescriptions (NEW)     │  - AHPRA       │               │
│  - mock_patients (NEW)         │                │               │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Hierarchy (Frontend)

```
App.tsx
├── AuthProvider (existing)
├── ThemeProvider (existing)
├── QueryClientProvider (existing, TanStack Query)
└── Router
    ├── /dashboard
    │   └── DashboardPage (extended with EMR metrics)
    ├── /mcq-practice
    │   └── MCQPracticePage (existing)
    ├── /osce-practice
    │   └── OSCEPracticePage (existing)
    └── /emr-practice (NEW)
        ├── EMRLandingPage (case selection)
        ├── EMRSessionPage (Epic EHR UI)
        │   ├── EpicSidebar (navigation)
        │   ├── EpicPatientBanner (demographics)
        │   └── EpicContentArea
        │       ├── EpicSOAPEditor (documentation)
        │       ├── EpicPrescriptionPanel (PBS search)
        │       ├── EpicPathologyPanel (MBS ordering)
        │       └── EpicValidationPanel (3-layer feedback)
        └── EMRHistoryPage (session history)
```

---

## 3. Backend Architecture

### 3.1 API Structure

```
/api/v1/emr/
├── sessions/
│   ├── POST   /start                  # Create new EMR session
│   ├── GET    /{session_id}           # Get session details
│   ├── PUT    /{session_id}           # Update session (auto-save)
│   ├── POST   /{session_id}/submit    # Submit for validation
│   └── DELETE /{session_id}           # Cancel session
├── patients/
│   ├── GET    /random                 # Random patient by specialty
│   ├── GET    /{patient_id}           # Get patient details
│   └── GET    /from-osce/{osce_id}    # Convert OSCE to EMR case
├── validation/
│   ├── POST   /soap-note              # Validate SOAP (Layer 2+3)
│   ├── POST   /prescription           # Validate Rx (PBS)
│   └── POST   /pathology              # Validate path order (MBS)
├── analytics/
│   ├── GET    /user/{user_id}/progress    # EMR metrics
│   ├── GET    /user/{user_id}/history     # Session list
│   └── GET    /user/{user_id}/trends      # Performance trends
└── reference/
    ├── GET    /pbs/medications        # PBS drug search
    ├── GET    /mbs/pathology          # MBS item search
    └── GET    /guidelines             # eTG quick reference
```

### 3.2 Database Schema Extensions

**New Tables** (6 total):

```sql
-- 1. EMR Sessions (practice sessions)
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id),
    patient_id UUID NOT NULL REFERENCES mock_patients(id),
    specialty VARCHAR(50) NOT NULL,  -- cardiology, respiratory, etc.
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP,
    elapsed_time_seconds INTEGER,
    validation_score FLOAT,  -- 0-15 (AMC rubric)
    status VARCHAR(20) NOT NULL,  -- in_progress, submitted, graded
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- 2. SOAP Notes (documentation drafts)
CREATE TABLE emr_soap_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id),
    subjective TEXT,  -- HPI, ROS
    objective TEXT,   -- Vitals, physical exam
    assessment TEXT,  -- Diagnosis, differential
    plan TEXT,        -- Management, follow-up
    soap_note_data JSON,  -- Full structured data
    word_count INTEGER,
    typing_wpm FLOAT,
    auto_saved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 3. Prescriptions (medication orders)
CREATE TABLE emr_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id),
    medication_name VARCHAR(200) NOT NULL,  -- Australian name
    dose VARCHAR(50),
    frequency VARCHAR(50),
    route VARCHAR(20),
    repeats INTEGER,
    indication TEXT,
    pbs_listed BOOLEAN,
    authority_required BOOLEAN,
    validation_errors JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Pathology Orders (lab requests)
CREATE TABLE emr_pathology_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id),
    test_name VARCHAR(200) NOT NULL,
    mbs_item_number VARCHAR(10),
    urgency VARCHAR(20),  -- routine, urgent, emergency
    indication TEXT,
    appropriate BOOLEAN,
    validation_feedback JSON,
    created_at TIMESTAMP DEFAULT NOW()
);

-- 5. Validation Results (AI feedback)
CREATE TABLE emr_validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id),
    validation_type VARCHAR(50),  -- soap_note, prescription, pathology
    layer_1_zod JSON,      -- Client-side validation errors
    layer_2_python JSON,   -- PBS/MBS compliance warnings
    layer_3_ai JSON,       -- Claude clinical reasoning insights
    overall_score FLOAT,   -- 0-15 (AMC format)
    strengths TEXT[],
    improvements TEXT[],
    red_flags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- 6. Mock Patients (simulated patient database)
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(20) UNIQUE NOT NULL,  -- Medical Record Number
    medicare_number VARCHAR(11),
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    aboriginal_tsi_status VARCHAR(50),
    demographics JSON,  -- Full patient data
    presenting_complaint TEXT,
    medical_history JSON,
    medications JSON,
    allergies JSON,
    vital_signs JSON,
    physical_exam_findings JSON,
    investigation_results JSON,  -- Labs, imaging
    source_osce_id INTEGER REFERENCES osces(id),
    specialty VARCHAR(50) NOT NULL,
    difficulty VARCHAR(20),  -- easy, medium, hard
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 7. Extend UserProgress (no new table, migration adds columns)
ALTER TABLE user_progress ADD COLUMN emr_sessions_completed INTEGER DEFAULT 0;
ALTER TABLE user_progress ADD COLUMN emr_soap_notes_written INTEGER DEFAULT 0;
ALTER TABLE user_progress ADD COLUMN emr_average_score FLOAT DEFAULT 0.0;
ALTER TABLE user_progress ADD COLUMN emr_total_time_minutes INTEGER DEFAULT 0;
```

**Indexes for Performance**:
```sql
CREATE INDEX idx_emr_sessions_user_id ON emr_sessions(user_id);
CREATE INDEX idx_emr_sessions_started_at ON emr_sessions(started_at);
CREATE INDEX idx_emr_sessions_specialty ON emr_sessions(specialty);
CREATE INDEX idx_mock_patients_specialty ON mock_patients(specialty);
CREATE INDEX idx_mock_patients_difficulty ON mock_patients(difficulty);
```

---

## 4. Integration Architecture

### 4.1 OSCE → EMR Case Conversion

**Pattern**:
```python
# backend/src/services/emr_case_converter.py

async def convert_osce_to_emr_case(osce: OSCE) -> MockPatient:
    """
    Convert an OSCE scenario into a complete EMR patient case.

    OSCE Structure:
    - patient_instructions: "You are John Smith, 58M, presenting with..."
    - candidate_instructions: "Take a focused history..."
    - rubric: AMC 15-mark criteria
    - specialty: cardiology
    - australian_guidelines: eTG references

    EMR Case Structure:
    - Full patient demographics (extracted + generated)
    - Realistic vital signs
    - Investigation results (labs, ECG, imaging)
    - Medication list
    - Allergies
    - Validation criteria (from rubric)
    """

    # 1. Extract patient data from patient_instructions
    patient_data = parse_patient_instructions(osce.patient_instructions)

    # 2. Generate realistic clinical data
    mock_patient = MockPatient(
        mrn=generate_mrn(),
        medicare_number=generate_medicare_number(),
        name=patient_data.get('name', generate_realistic_name()),
        age=patient_data.get('age'),
        gender=patient_data.get('gender'),
        demographics={
            'address': generate_australian_address(),
            'phone': generate_phone(),
            'emergency_contact': generate_contact(),
            'gp_details': generate_gp_details(),
        },
        presenting_complaint=extract_presenting_complaint(osce.patient_instructions),
        medical_history=extract_medical_history(osce.patient_instructions),
        medications=generate_realistic_medications(osce.specialty),
        allergies=patient_data.get('allergies', ['NKDA']),
        vital_signs=generate_vital_signs(osce.specialty),
        physical_exam_findings=generate_exam_findings(osce.specialty),
        investigation_results=generate_investigations(osce.specialty),
        source_osce_id=osce.id,
        specialty=osce.specialty,
        difficulty=osce.difficulty
    )

    return mock_patient
```

**Example Conversion**:

```
OSCE Input (OSCE-CARD-001):
┌────────────────────────────────────────────────────────┐
│ Patient Instructions:                                  │
│ You are John Smith, 58-year-old male, presenting to   │
│ ED with central chest pain for 2 hours. Pain 7/10,    │
│ crushing, radiating to left arm. Sweating, nauseous.  │
│ PMHx: Hypertension (on amlodipine 5mg), T2DM (on      │
│ metformin 500mg BD). Smoker 30 pack-years.            │
│ Allergies: Penicillin (rash)                          │
└────────────────────────────────────────────────────────┘

              ↓ CONVERT TO ↓

EMR Patient Case:
┌────────────────────────────────────────────────────────┐
│ MRN: 12345678  Medicare: 2912 34567 1                 │
│ Name: John Smith  Age: 58  Gender: Male               │
│ Address: 12 King St, Sydney NSW 2000                  │
│                                                        │
│ Presenting Complaint: Central chest pain (2h)         │
│                                                        │
│ Vital Signs:                                           │
│   HR 95 bpm, BP 155/92, RR 20, SpO2 96%, Temp 36.8°C │
│                                                        │
│ Medications:                                           │
│   - Amlodipine 5mg daily                              │
│   - Metformin 500mg BD                                │
│                                                        │
│ Allergies: Penicillin (rash)                          │
│                                                        │
│ Investigation Results:                                 │
│   ECG: ST elevation 2mm in leads II, III, aVF         │
│   Troponin I: 1.2 ng/mL (↑↑)                         │
│   FBC: Hb 145 g/L, WCC 9.2, Plt 250                   │
│   UEC: Na 138, K 4.2, Cr 85 µmol/L                   │
│   Random BSL: 8.2 mmol/L                              │
└────────────────────────────────────────────────────────┘
```

### 4.2 Authentication Integration

**Reuse Existing JWT System** (zero changes needed):

```typescript
// frontend/src/context/AuthContext.tsx (EXISTING)
export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(
    localStorage.getItem('accessToken')
  );

  // ... existing login/logout logic
};

// NEW EMR Component
const EMRSessionPage = () => {
  const { user, token } = useAuth();  // Reuse existing hook

  // All EMR API calls automatically include JWT
  const { data: session } = useQuery({
    queryKey: ['emr-session', sessionId],
    queryFn: async () => {
      // axiosInstance already has JWT interceptor
      const response = await axiosInstance.get(`/emr/sessions/${sessionId}`);
      return response.data;
    }
  });
};
```

**Authorization Rules**:
```python
# backend/src/api/v1/emr/sessions.py

@router.post("/start", response_model=EMRSessionResponse)
async def start_emr_session(
    patient_id: UUID,
    current_user: User = Depends(get_current_active_user),  # REUSE
    db: Session = Depends(get_db)
):
    # All users can practice EMR (students, educators, admins)
    # Educators can additionally review student sessions
    pass
```

### 4.3 State Management Integration

**Pattern**: TanStack Query (consistent with MCQ/OSCE)

```typescript
// frontend/src/hooks/emr/useEMRSession.ts

export const useEMRSession = (sessionId: string) => {
  return useQuery({
    queryKey: ['emr-session', sessionId],
    queryFn: async () => {
      const response = await axiosInstance.get(`/emr/sessions/${sessionId}`);
      return response.data;
    },
    staleTime: 0,  // Always fresh for real-time validation
    refetchInterval: 30000,  // Auto-refresh every 30s
  });
};

export const useAutoSaveSOAP = (sessionId: string) => {
  return useMutation({
    mutationFn: async (soapData: SOAPNoteData) => {
      const response = await axiosInstance.put(
        `/emr/sessions/${sessionId}`,
        { soap_note: soapData }
      );
      return response.data;
    },
    onSuccess: () => {
      // Invalidate session cache to trigger refetch
      queryClient.invalidateQueries(['emr-session', sessionId]);
    },
  });
};

export const useValidateSOAP = (sessionId: string) => {
  return useMutation({
    mutationFn: async (soapData: SOAPNoteData) => {
      const response = await axiosInstance.post(
        `/emr/validation/soap-note`,
        { session_id: sessionId, soap_note: soapData }
      );
      return response.data;
    },
    // Validation takes 3-5 seconds (Claude AI)
  });
};
```

### 4.4 Progress Tracking Integration

**Unified Dashboard** (extend existing):

```typescript
// frontend/src/components/dashboard/DashboardPage.tsx

const DashboardPage = () => {
  const { user } = useAuth();
  const { data: progress } = useQuery({
    queryKey: ['user-progress', user?.id],
    queryFn: async () => {
      const response = await axiosInstance.get(`/users/${user?.id}/progress`);
      return response.data;
    }
  });

  return (
    <Grid container spacing={3}>
      {/* EXISTING */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="MCQs Attempted"
          value={progress.total_mcqs_attempted}
          icon={<QuestionMarkIcon />}
        />
      </Grid>
      <Grid item xs={12} md={4}>
        <StatCard
          title="OSCEs Practiced"
          value={progress.total_osces_practiced}
          icon={<PersonIcon />}
        />
      </Grid>

      {/* NEW EMR METRICS */}
      <Grid item xs={12} md={4}>
        <StatCard
          title="SOAP Notes Written"
          value={progress.emr_soap_notes_written}
          icon={<DescriptionIcon />}
        />
      </Grid>

      {/* Unified specialty breakdown (MCQ + OSCE + EMR) */}
      <Grid item xs={12}>
        <SpecialtyBreakdown data={progress.by_specialty} />
      </Grid>
    </Grid>
  );
};
```

---

## 5. AI Integration Architecture

### 5.1 Three-Layer Validation System

```
┌─────────────────────────────────────────────────────────────┐
│                    User Types in Epic UI                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
         ┌─────────────▼─────────────┐
         │   Layer 1: Zod (Client)   │  <50ms
         │   - Type validation       │  RED inline errors
         │   - Character minimums    │  "HPI too short (30/50 chars)"
         │   - Required fields       │
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │ Layer 2: Python (Server)  │  <1 second
         │ - PBS compliance          │  YELLOW warnings
         │ - MBS appropriateness     │  "Max 5 repeats for this drug"
         │ - Australian terminology  │  "Use 'paracetamol' not 'acetaminophen'"
         └─────────────┬─────────────┘
                       │
         ┌─────────────▼─────────────┐
         │ Layer 3: Claude AI        │  3-5 seconds
         │ - Clinical reasoning      │  GREEN insights
         │ - AMC rubric scoring      │  "Excellent differential (3/3)"
         │ - Red flag detection      │  "Consider ACS, arrange ECG"
         │ - Safety netting          │
         └───────────────────────────┘
```

### 5.2 AI Validator Implementation

```python
# backend/agents/soap_validator.py

from anthropic import Anthropic
import json

class SOAPNoteValidator:
    """
    Layer 3 validator using Claude Sonnet 4.5 for clinical reasoning.

    Cost: ~$0.02 per validation (3-5 second latency)
    """

    def __init__(self):
        self.anthropic = Anthropic()  # Use Claude, NOT Ollama
        self.model = "claude-sonnet-4-5-20250929"

    async def validate(
        self,
        soap_note: dict,
        patient_case: dict,
        rubric_criteria: dict
    ) -> dict:
        """
        Validate SOAP note against AMC Clinical Exam standards.

        Returns:
        {
            "overall_score": 12.5,  # 0-15 (AMC format)
            "category_scores": {
                "history_examination": 3.0,
                "clinical_reasoning": 2.5,
                "communication": 3.0,
                "patient_safety": 2.0,
                "professionalism": 2.0
            },
            "strengths": [
                "Excellent SOCRATES pain assessment",
                "Appropriate differential diagnosis (ACS, PE, gastritis)",
                "Safety netting with red flag advice"
            ],
            "improvements": [
                "Consider asking about radiation to jaw/neck",
                "Add cardiovascular risk factors to assessment",
                "Specify exact troponin timing in plan"
            ],
            "red_flags": [
                "Patient has ACS - URGENT cardiology referral needed",
                "STEMI criteria met - activate cath lab"
            ],
            "australian_compliance": {
                "terminology": "✓ Correct (paracetamol not acetaminophen)",
                "emergency_number": "✓ Mentioned 000 for worsening symptoms",
                "etg_alignment": "✓ Follows eTG Cardiovascular guidelines"
            }
        }
        """

        prompt = f"""
You are an Australian BCBA-level medical educator assessing a medical student's SOAP note for the AMC Clinical Examination.

PATIENT CASE:
{json.dumps(patient_case, indent=2)}

STUDENT'S SOAP NOTE:
Subjective: {soap_note.get('subjective', '')}
Objective: {soap_note.get('objective', '')}
Assessment: {soap_note.get('assessment', '')}
Plan: {soap_note.get('plan', '')}

AMC RUBRIC (15 marks total):
{json.dumps(rubric_criteria, indent=2)}

ASSESSMENT CRITERIA:
1. Score using the 15-mark AMC rubric (0-3 per category)
2. Identify strengths (what the student did well)
3. Suggest 2-3 specific improvements
4. Flag any RED FLAGS (critical errors or patient safety issues)
5. Verify Australian medical standards compliance:
   - Correct Australian drug names (paracetamol not acetaminophen)
   - Emergency number 000 (not 911)
   - eTG guideline alignment
   - SI units (mmol/L not mg/dL)

Return ONLY valid JSON in this exact format:
{{
  "overall_score": <float 0-15>,
  "category_scores": {{
    "history_examination": <float 0-3>,
    "clinical_reasoning": <float 0-3>,
    "communication": <float 0-3>,
    "patient_safety": <float 0-3>,
    "professionalism": <float 0-3>
  }},
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "red_flags": ["...", "..."],
  "australian_compliance": {{
    "terminology": "✓/✗ ...",
    "emergency_number": "✓/✗ ...",
    "etg_alignment": "✓/✗ ..."
  }}
}}
"""

        message = self.anthropic.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.2,  # Low temperature for consistent grading
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text

        # Parse JSON response
        validation_result = json.loads(response_text)

        return validation_result
```

---

## 6. Technology Stack Summary

### 6.1 Frontend

```json
{
  "framework": "React 19.2.0",
  "language": "TypeScript 5.9.3",
  "ui_library": "Material-UI v7 (@mui/material ^7.3.7)",
  "styling": "Emotion (CSS-in-JS, MUI default)",
  "state_management": "TanStack Query v5",
  "routing": "React Router v7",
  "forms": "React Hook Form + Zod",
  "http_client": "Axios (with JWT interceptor)",
  "icons": "Material-UI icons (@mui/icons-material)",
  "animations": "MUI transitions (Fade, Slide, Grow)",
  "build_tool": "Vite 7.2.4"
}
```

### 6.2 Backend

```json
{
  "framework": "FastAPI 0.109.0 (async ASGI)",
  "language": "Python 3.11+",
  "orm": "SQLAlchemy (async support)",
  "database": "PostgreSQL 14 (irstudy_medical)",
  "cache": "Redis cluster (6 nodes)",
  "vector_db": "Qdrant (9,950 medical chunks)",
  "secrets": "HashiCorp Vault",
  "ai_provider": "Anthropic Claude Sonnet 4.5",
  "validation": "Pydantic v2",
  "authentication": "JWT (HS256)",
  "api_versioning": "/api/v1/",
  "rate_limiting": "SlowAPI + Prometheus metrics"
}
```

### 6.3 Testing

```json
{
  "e2e": "Playwright (Chromium)",
  "unit_frontend": "Vitest + React Testing Library",
  "unit_backend": "pytest + pytest-asyncio",
  "api_testing": "pytest + httpx",
  "coverage_target": "≥70%",
  "test_pass_rate": "100% (zero-error policy)"
}
```

---

## 7. Performance Targets

| Metric | Target | Monitoring |
|--------|--------|------------|
| **Layer 1 Zod Validation** | <50ms | Client-side performance.now() |
| **Layer 2 Python Validation** | <1 second | FastAPI middleware timing |
| **Layer 3 Claude AI Validation** | 3-5 seconds | Anthropic API latency logs |
| **Auto-save Latency** | <200ms | PUT /sessions/{id} timing |
| **Patient Case Load** | <500ms | GET /patients/{id} timing |
| **Session Start** | <1 second | POST /sessions/start timing |
| **Dashboard Load** | <2 seconds | React profiler |
| **Frontend Bundle Size** | <500 KB (gzipped) | Vite build analysis |

---

## 8. Security Architecture

### 8.1 Authentication Flow

```
1. User logs in → JWT issued (existing system)
2. JWT stored in localStorage (existing)
3. Axios interceptor adds JWT to all requests (existing)
4. Backend validates JWT on all /api/v1/emr/* endpoints (existing pattern)
5. User role checked for authorization (existing)
```

### 8.2 Data Privacy (HIPAA/GDPR Compliance)

- ✅ All mock patients are **simulated** (no real PHI)
- ✅ User data encrypted at rest (PostgreSQL TDE)
- ✅ Soft delete pattern (compliance with data retention)
- ✅ GDPR APIs already implemented (`/api/v1/gdpr/`)
- ✅ Vault-backed secrets (no hardcoded credentials)
- ⚠️ PHI anonymizer not yet implemented (Phase 0 Week 0.2 - 30% complete)

### 8.3 API Security

- ✅ Rate limiting (SlowAPI with Redis)
- ✅ CORS configuration (allow only frontend origin)
- ✅ Input validation (Pydantic schemas)
- ✅ SQL injection prevention (SQLAlchemy parameterized queries)
- ✅ XSS prevention (React escapes by default, MUI sanitizes)
- ✅ CSRF protection (SameSite cookies for session tokens)

---

## 9. Deployment Architecture

### 9.1 Development Environment

```
Docker Compose:
┌──────────────────────────────────────────────────────┐
│  frontend:5173 (Vite dev server)                     │
│  backend:8000 (FastAPI with hot reload)              │
│  postgresql:5433 (irstudy_medical database)          │
│  redis-cluster:7000-7005 (6 nodes)                   │
│  qdrant:6333 (vector database)                       │
│  vault:8200 (secrets management)                     │
└──────────────────────────────────────────────────────┘
```

### 9.2 Production Considerations (Future)

```
Frontend:
- Vite production build → Nginx static hosting
- CloudFront CDN for global delivery
- Brotli compression

Backend:
- Gunicorn + Uvicorn workers (async ASGI)
- Kubernetes deployment (auto-scaling)
- PostgreSQL read replicas for analytics queries

Monitoring:
- Prometheus metrics (API latency, error rates)
- Grafana dashboards
- Sentry error tracking
- Claude API usage monitoring (cost control)
```

---

## 10. Migration Checklist

### 10.1 Phase 1: Foundation (Week 1)

- [x] Architecture decision documented (this file)
- [ ] Create `/15-feb-emr-plan/` folder structure
- [ ] Write DATABASE_MIGRATION.md
- [ ] Write API_SPECIFICATION.md
- [ ] Write INTEGRATION_STRATEGY.md
- [ ] Create Alembic migration for 6 new tables
- [ ] Add indexes for performance
- [ ] Extend UserProgress model

### 10.2 Phase 2: Backend (Week 1-2)

- [ ] Implement `/api/v1/emr/sessions/` endpoints
- [ ] Implement `/api/v1/emr/patients/` endpoints
- [ ] Implement `/api/v1/emr/validation/` endpoints
- [ ] Build SOAPValidator agent (Claude integration)
- [ ] Build PrescriptionValidator agent (PBS)
- [ ] Build PathologyValidator agent (MBS)
- [ ] Create Pydantic schemas for EMR models
- [ ] Add unit tests (pytest, ≥70% coverage)

### 10.3 Phase 3: Frontend (Week 2-3)

- [ ] Migrate EpicSidebar.tsx to Material-UI
- [ ] Migrate EpicPatientBanner.tsx to Material-UI
- [ ] Create EpicSOAPEditor.tsx (React Hook Form + Zod)
- [ ] Create EpicPrescriptionPanel.tsx (PBS search)
- [ ] Create EpicPathologyPanel.tsx (MBS ordering)
- [ ] Create EpicValidationPanel.tsx (3-layer feedback)
- [ ] Implement auto-save (30-second interval)
- [ ] Implement typing metrics (WPM tracker)
- [ ] Create EMRLandingPage (case selection)
- [ ] Extend DashboardPage with EMR metrics

### 10.4 Phase 4: Integration (Week 3)

- [ ] Convert 50 OSCE scenarios to EMR patient cases
- [ ] Populate mock_patients table
- [ ] Link OSCE scenarios to EMR practice
- [ ] Link MCQ medications to PBS search
- [ ] Embed educational videos in EMR cases
- [ ] Unified progress tracking

### 10.5 Phase 5: Testing & Polish (Week 4)

- [ ] Playwright E2E tests (complete EMR workflow)
- [ ] Performance testing (validate targets met)
- [ ] Security audit (JWT, input validation)
- [ ] Australian standards compliance verification
- [ ] Documentation updates

---

## 11. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **EMR Cases Available** | 50+ (from 221 OSCEs) | Database count |
| **Validation Latency** | Layer 1: <50ms, Layer 2: <1s, Layer 3: 3-5s | API logs |
| **Test Pass Rate** | 100% | Playwright + pytest results |
| **Test Coverage** | ≥70% | Coverage reports |
| **Zero Hardcoded Credentials** | 0 violations | Security scan (grep) |
| **Australian Compliance** | 90%+ | AI validation accuracy vs. expert review |
| **User Session Completion** | 80%+ | Analytics (sessions submitted / started) |
| **Average SOAP Note Score** | 9/15+ (60% pass rate) | Database analytics |

---

## 12. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Tailwind → MUI migration takes >3 days** | High | Start with 1 component (EpicSidebar) to validate approach |
| **Claude API costs exceed budget** | Medium | Monitor usage, implement caching for common validations |
| **Database performance degrades** | Medium | Add indexes immediately, test with 1000+ sessions |
| **Design system inconsistencies** | Low | Use existing MUI components (StatCard pattern) |
| **Authentication integration issues** | Low | Reuse existing JWT system (no changes needed) |
| **OSCE → EMR conversion inaccurate** | Medium | Manual review of first 10 cases by medical expert |

---

## 13. Future Enhancements (Post-MVP)

1. **Real-Time Collaboration**
   - WebSocket integration (backend already has support)
   - Educator watches student in real-time
   - Live feedback during session

2. **Advanced Analytics**
   - Heatmaps (which SOAP sections take longest)
   - Predictive scoring (AI suggests score before submission)
   - Specialty-specific benchmarking

3. **Cerner PowerChart UI**
   - Second EMR system (dark blue theme)
   - Toggle between Epic and Cerner
   - Comparative training

4. **Mobile Support**
   - Responsive Material-UI design
   - Touch-optimized SOAP editor
   - PWA for offline practice

5. **Gamification**
   - Achievements (e.g., "100 SOAP Notes Written")
   - Leaderboards (anonymized)
   - Streaks (consecutive days practicing)

---

## Conclusion

This architecture provides a **solid foundation** for integrating high-fidelity Epic EHR simulation into the irStudy platform. Key advantages:

- ✅ **Unified UX**: Single Material-UI application
- ✅ **Reusable Infrastructure**: Leverage existing auth, API patterns, database
- ✅ **Australian Compliance**: Built-in eTG/AMH/AHPRA validation
- ✅ **Full Integration**: Seamless OSCE/MCQ/video cross-linking
- ✅ **Scalable**: Clear path to Cerner, mobile, real-time features

**Next Steps**: Proceed to DATABASE_MIGRATION.md for detailed schema design.

---

**Document Status**: ✅ APPROVED
**Last Updated**: 2026-02-15
**Review Date**: 2026-03-01 (post-MVP completion)
