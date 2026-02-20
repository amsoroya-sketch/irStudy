# EMR Practice Simulation System - Master PRD

**Product:** Hospital EMR Practice System for AMC Clinical Examination Preparation
**Version:** 2.0
**Date:** 2026-02-15
**Owner:** Product Team
**Status:** Planning Phase

---

## Executive Summary

### Vision
Create a realistic hospital Electronic Medical Record (EMR) simulation system that allows medical students preparing for the AMC Clinical Examination (Australian Medical Council Clinical Examination) to practice clinical documentation, prescription writing, and pathology ordering in authentic Cerner PowerChart and Epic EHR interfaces, with AI-powered validation providing immediate feedback on Australian medical standards compliance and AHPRA clinical competency requirements.

### Problem Statement
Medical graduates preparing for the AMC Clinical Examination lack practical experience with hospital EMR systems used in Australian teaching hospitals, leading to:
- Slow documentation speed (20+ minutes for progress notes vs. 5-10 min target expected in clinical practice)
- Medication ordering errors (dosing, PBS compliance, drug interactions)
- Incomplete SOAP notes (missing critical elements required in Australian clinical documentation)
- Unfamiliarity with Australian medical terminology (paracetamol vs. acetaminophen, adrenaline vs. epinephrine)
- Poor typing skills in medical context (< 30 WPM)
- Lack of familiarity with AHPRA documentation standards and NSW Health EMR protocols

### Target Users
1. **Primary:** Medical students preparing for AMC Clinical Examination (Australian Medical Council Clinical Examination)
2. **Secondary:** International Medical Graduates (IMGs) preparing for clinical practice in Australian hospitals
3. **Tertiary:** Junior doctors upskilling in EMR documentation and AHPRA-compliant clinical records

### Success Metrics (World-Class Standards)
- **Speed:** Users complete SOAP notes in < 8 minutes after 20 sessions (vs. 20+ minutes initially)
- **AHPRA Compliance:** 95%+ compliance with AHPRA clinical documentation standards
- **Australian Standards:** 95%+ compliance with Australian medical terminology and NSW Health EMR protocols
- **Engagement:** 90%+ users practice at least 3 sessions per week
- **AI Validation Accuracy:** 90%+ accuracy vs. human clinical educator review (BCBA-level validation)
- **Clinical Accuracy:** 90%+ accuracy in diagnosis, prescription safety, and pathology appropriateness
- **Pass Rate Improvement:** Users show 40%+ improvement in documentation quality after 20 sessions
- **User Satisfaction:** 85%+ users rate the system as "very helpful" for AMC Clinical Examination preparation
- **Safety:** Zero critical medication errors (allergy violations, contraindications) after 10 practice sessions

---

## Australian Clinical Standards Compliance

### AHPRA Clinical Documentation Standards

This EMR Practice System is designed to meet AHPRA (Australian Health Practitioner Regulation Agency) clinical documentation standards, ensuring all users develop competency in:

1. **Accurate and Complete Documentation**
   - Patient identification details (full name, DOB, MRN, UR number)
   - Date and time of clinical encounter
   - Clinician identification and signature
   - Clear and legible documentation (typed entries)

2. **Clinical Content Requirements**
   - Comprehensive history taking (HPC, PMHx, medications, allergies, social/family history)
   - Systematic physical examination findings
   - Appropriate differential diagnoses
   - Evidence-based management plans
   - Safety netting and follow-up arrangements

3. **Professional Standards**
   - Respectful and non-judgmental language
   - Patient privacy and confidentiality
   - Informed consent documentation
   - Cultural safety (Aboriginal and Torres Strait Islander health context)

### NSW Health EMR Protocols

The system simulates NSW Health EMR protocols used in major teaching hospitals:

1. **Australian SOAP Note Format**
   - **S (Subjective):** Patient's complaint in their own words, HPI details, relevant history
   - **O (Objective):** Vital signs, physical examination findings, investigation results
   - **A (Assessment):** Primary diagnosis, differential diagnoses, problem list
   - **P (Plan):** Investigations, medications (PBS-compliant), referrals, follow-up, safety netting

2. **Medication Documentation**
   - Generic drug names (as per PBS)
   - Australian terminology (paracetamol, not acetaminophen)
   - Complete prescribing information (dose, route, frequency, duration)
   - Indication for each medication
   - PBS streamlined authority requirements noted

3. **Investigation Ordering**
   - MBS item numbers where applicable
   - Clear clinical indication
   - Urgency level (routine, urgent, emergency)
   - Relevant clinical information for pathologist/radiologist

### Australian Medical Terminology Compliance

The system enforces Australian medical terminology standards:

| **American Term** | **Australian Term** | **Validation** |
|-------------------|---------------------|----------------|
| Acetaminophen | Paracetamol | Required |
| Epinephrine | Adrenaline | Required |
| Albuterol | Salbutamol | Required |
| Norepinephrine | Noradrenaline | Required |
| Acetylsalicylic acid | Aspirin | Preferred |
| Primary care physician | GP (General Practitioner) | Required |
| Operating room | Operating theatre | Preferred |
| ER | ED (Emergency Department) | Required |

### PBS and MBS Integration

1. **PBS (Pharmaceutical Benefits Scheme)**
   - 4,000+ PBS-listed medications
   - Streamlined authority requirements flagged
   - Generic vs. brand name guidance
   - Dosing ranges and restrictions
   - Special patient groups (concession card holders, children, elderly)

2. **MBS (Medicare Benefits Schedule)**
   - Common pathology item numbers (FBC: 65070, UEC: 66512, LFT: 66524, etc.)
   - Imaging item numbers
   - Indication requirements
   - Bulk billing information

---

## Product Overview

### Core Features

#### 1. **Simulated EMR Environments**
- **Cerner PowerChart Simulation**
  - Dark sidebar with blue accents
  - 7 modules: Dashboard, Patient Chart, Progress Notes, Medications, Orders, Vitals, Alerts
  - Realistic UI/UX matching actual Cerner interface

- **Epic EHR Simulation**
  - Purple theme with icon-based navigation
  - Modules: Storyboard, Patient Summary, Note Writer, Med Manager, Order Entry, Flowsheet
  - Tab-based multi-document interface

#### 2. **Clinical Documentation Practice**
- **SOAP Note Editor**
  - Structured fields (Subjective, Objective, Assessment, Plan)
  - Minimum character validation (50+ chars per section)
  - Real-time typing metrics (WPM, accuracy)
  - Draft saving every 30 seconds

- **Prescription Writing**
  - PBS medication search (4,000+ drugs)
  - Dose calculators
  - Drug interaction warnings
  - Streamlined authority requirements
  - Quantity/repeats validation (max 5 repeats)

- **Pathology Ordering**
  - MBS item number lookup
  - Common test panels (FBC, UEC, LFT, etc.)
  - Indication requirements
  - Urgency selection (Routine/Urgent/Emergency)

#### 3. **Simulated Patient Scenarios**
- **200+ Patient Cases**
  - 10 medical specialties
  - Varied complexity (simple to complex)
  - Australian demographic data
  - Realistic clinical scenarios from Australian hospital settings and AMC Clinical Examination contexts

- **Patient Demographics**
  - Name, age, gender, MRN
  - Aboriginal/Torres Strait Islander status
  - Allergies (medication, food, environmental)
  - Current medications
  - Medical history
  - Vital signs
  - Presenting complaint

#### 4. **AI-Powered Validation**
- **SOAP Note Validation**
  - Structure completeness (all 4 sections present)
  - Clinical accuracy (diagnosis matches presentation)
  - Australian terminology usage
  - Red flag identification
  - Safety netting

- **Prescription Validation**
  - PBS compliance
  - Dose appropriateness (age, weight, renal/hepatic function)
  - Drug interactions
  - Allergy checking
  - Indication match

- **Pathology Validation**
  - MBS item appropriateness
  - Indication completeness
  - Over-investigation detection
  - Urgency appropriateness

#### 5. **Real-Time Feedback System**
- **Instant Validation**
  - Submit for review button
  - 2-3 second AI analysis
  - Detailed feedback panel

- **Feedback Components**
  - Overall score (0-100)
  - Criteria-based scoring (6-8 criteria)
  - Strengths (3-5 bullet points)
  - Areas for improvement (3-5 bullet points)
  - Specific suggestions (actionable)
  - Example corrections (show vs. tell)

#### 6. **Progress Tracking**
- **Session History**
  - All past sessions saved
  - Review previous work
  - Track improvement over time

- **Analytics Dashboard**
  - Sessions completed
  - Average documentation time
  - Validation scores trend
  - Weak areas identification
  - Specialty-specific performance

#### 7. **OSCE Station Integration**

The EMR Practice System integrates seamlessly with OSCE (Objective Structured Clinical Examination) stations to provide authentic clinical examination preparation for the AMC Clinical Examination.

**Integration Features:**

1. **EMR-Required OSCE Stations**
   - Students encounter OSCE stations that explicitly require EMR documentation
   - Example: "Complete a SOAP note in the hospital EMR system based on this patient encounter"
   - Simulates real clinical examination conditions where EMR proficiency is assessed

2. **Dual-Interface Display**
   - OSCE station instructions displayed in a banner (non-intrusive)
   - Full EMR interface (Cerner or Epic) below for documentation
   - Timer visible showing remaining time for station
   - Patient scenario details accessible throughout

3. **Real-Time EMR Documentation During OSCE**
   - Students practice documenting while managing time pressure
   - Realistic workflow: gather information → document in EMR → submit
   - Typing speed and accuracy tracked under examination conditions

4. **Integrated Scoring System**
   - **OSCE Score (60%):** Clinical examination skills, communication, examination technique
   - **EMR Documentation Score (40%):** SOAP note quality, Australian terminology, PBS/MBS compliance
   - **Combined Score:** Provides holistic assessment of clinical and documentation skills

5. **Technical Architecture**

```typescript
// components/osce/OSCEStationWithEMR.tsx
interface OSCEStation {
  id: string;
  title: string;
  instructions: string;
  duration_minutes: number;
  patient_scenario_id: string;
  emr_system: 'cerner' | 'epic';
  required_documentation: ('soap_note' | 'prescription' | 'pathology')[];
  scoring_weights: {
    osce_clinical_skills: number;  // 0.6
    emr_documentation: number;      // 0.4
  };
}

export const OSCEStationWithEMR: React.FC<{ station: OSCEStation }> = ({ station }) => {
  const [timeRemaining, setTimeRemaining] = useState(station.duration_minutes * 60);
  const [documentationStarted, setDocumentationStarted] = useState(false);

  return (
    <div className="osce-station-container">
      {/* OSCE Instructions Banner */}
      <div className="osce-banner bg-blue-900 text-white p-4">
        <div className="flex justify-between items-center">
          <div>
            <h2 className="text-xl font-bold">{station.title}</h2>
            <p className="text-sm">{station.instructions}</p>
          </div>
          <div className="text-right">
            <div className="text-3xl font-mono font-bold">
              {Math.floor(timeRemaining / 60)}:{(timeRemaining % 60).toString().padStart(2, '0')}
            </div>
            <div className="text-xs">Time Remaining</div>
          </div>
        </div>
      </div>

      {/* EMR Interface */}
      <div className="emr-interface">
        {station.emr_system === 'cerner' ? (
          <CernerSimulation
            patientScenarioId={station.patient_scenario_id}
            osceMode={true}
            onDocumentationStart={() => setDocumentationStarted(true)}
          />
        ) : (
          <EpicSimulation
            patientScenarioId={station.patient_scenario_id}
            osceMode={true}
            onDocumentationStart={() => setDocumentationStarted(true)}
          />
        )}
      </div>
    </div>
  );
};
```

6. **Database Schema: OSCE-EMR Integration**

```sql
-- Table: osce_emr_sessions
CREATE TABLE osce_emr_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES users(id),
  osce_station_id UUID NOT NULL,
  emr_session_id UUID NOT NULL REFERENCES emr_sessions(id),

  -- OSCE Details
  station_title VARCHAR(255) NOT NULL,
  duration_minutes INT NOT NULL,
  started_at TIMESTAMP NOT NULL DEFAULT NOW(),
  completed_at TIMESTAMP,

  -- Scoring
  osce_clinical_score DECIMAL(5,2),  -- 0-100 (manual scoring by examiner)
  emr_documentation_score DECIMAL(5,2),  -- 0-100 (AI validation)
  combined_score DECIMAL(5,2),  -- Weighted average

  -- Metadata
  documentation_time_seconds INT,
  typing_speed_wpm DECIMAL(5,2),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Table: osce_stations (predefined OSCE scenarios)
CREATE TABLE osce_stations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title VARCHAR(255) NOT NULL,
  instructions TEXT NOT NULL,
  duration_minutes INT NOT NULL DEFAULT 10,
  patient_scenario_id UUID NOT NULL REFERENCES patient_scenarios(id),
  emr_system VARCHAR(20) NOT NULL CHECK (emr_system IN ('cerner', 'epic')),
  required_documentation JSONB NOT NULL,  -- ['soap_note', 'prescription']
  scoring_weights JSONB NOT NULL,  -- {"osce_clinical_skills": 0.6, "emr_documentation": 0.4}

  -- AMC Clinical Examination Context
  specialty VARCHAR(100),
  difficulty_level VARCHAR(20) CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced')),

  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

7. **API Endpoints: OSCE Integration**

```python
# backend/api/routes/osce_integration.py
from fastapi import APIRouter, Depends
from typing import List

router = APIRouter()

@router.post("/osce/sessions/start")
async def start_osce_emr_session(
    osce_station_id: str,
    user_id: str = Depends(get_current_user)
) -> OSCEEMRSession:
    """
    Start a new OSCE station with EMR documentation requirement.
    Returns session ID, patient scenario, and timer settings.
    """
    pass

@router.post("/osce/sessions/{session_id}/submit")
async def submit_osce_emr_documentation(
    session_id: str,
    documentation: EMRDocumentation,
    user_id: str = Depends(get_current_user)
) -> OSCESubmissionResult:
    """
    Submit EMR documentation for OSCE station.
    Triggers AI validation and calculates EMR documentation score.
    """
    pass

@router.get("/osce/sessions/{session_id}/score")
async def get_osce_emr_score(
    session_id: str,
    user_id: str = Depends(get_current_user)
) -> OSCEScore:
    """
    Get combined OSCE + EMR score.
    Returns breakdown: clinical skills score, EMR documentation score, combined score.
    """
    pass

@router.get("/osce/stations")
async def list_osce_stations(
    specialty: Optional[str] = None,
    difficulty: Optional[str] = None
) -> List[OSCEStation]:
    """
    List available OSCE stations with EMR documentation requirements.
    Can filter by specialty and difficulty level.
    """
    pass
```

8. **Success Metrics: OSCE Integration**
   - **Station Completion Rate:** 95%+ of users complete EMR documentation within time limit
   - **Combined Score:** Average combined score (OSCE + EMR) of 75%+
   - **Documentation Quality:** 90%+ of OSCE EMR submissions meet AHPRA standards
   - **Time Management:** 85%+ of users complete documentation with ≥2 minutes remaining
   - **Realistic Preparation:** 90%+ of users report feeling "well-prepared" for AMC Clinical Examination EMR components

---

## Technical Architecture

### System Components

#### Frontend (React + TypeScript)
```
frontend/
├── src/
│   ├── components/
│   │   ├── cerner/
│   │   │   ├── CernerSidebar.tsx
│   │   │   ├── CernerHeader.tsx
│   │   │   ├── PatientBanner.tsx
│   │   │   ├── ProgressNoteEditor.tsx
│   │   │   ├── MedicationOrderEntry.tsx
│   │   │   └── PathologyOrderEntry.tsx
│   │   ├── epic/
│   │   │   ├── EpicSidebar.tsx
│   │   │   ├── EpicStoryboard.tsx
│   │   │   ├── NoteWriter.tsx
│   │   │   └── OrderEntry.tsx
│   │   ├── common/
│   │   │   ├── ValidationPanel.tsx
│   │   │   ├── FeedbackCard.tsx
│   │   │   ├── TypingMetrics.tsx
│   │   │   └── ProgressChart.tsx
│   │   └── shared/
│   │       ├── Button.tsx
│   │       ├── Modal.tsx
│   │       └── Loader.tsx
│   ├── pages/
│   │   ├── DashboardPage.tsx
│   │   ├── SessionPage.tsx
│   │   ├── AnalyticsPage.tsx
│   │   └── HistoryPage.tsx
│   ├── hooks/
│   │   ├── useEMRSession.ts
│   │   ├── useValidation.ts
│   │   └── useTypingMetrics.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── validation.ts
│   │   └── storage.ts
│   └── types/
│       ├── emr.types.ts
│       ├── patient.types.ts
│       └── validation.types.ts
```

#### Backend (FastAPI + Python)
```
backend/
├── agents/
│   ├── soap_validator.py
│   ├── prescription_validator.py
│   └── pathology_validator.py
├── api/
│   └── routes/
│       ├── patients.py
│       ├── sessions.py
│       ├── validation.py
│       └── analytics.py
├── models/
│   ├── database.py
│   ├── patient.py
│   ├── session.py
│   └── validation.py
├── services/
│   ├── pbs_service.py
│   ├── mbs_service.py
│   ├── claude_service.py
│   └── rag_service.py
└── utils/
    ├── validators.py
    └── helpers.py
```

### Data Flow

```
User Input → Frontend Component → API Call → Backend Validation
                                                    ↓
                                           Claude AI Analysis
                                                    ↓
                                           RAG Knowledge Lookup
                                                    ↓
                                           Validation Rules Engine
                                                    ↓
Feedback Display ← Frontend ← API Response ← Structured Feedback
```

---

## Integration with Main irStudy Platform

### Architecture Integration

#### Option 1: Standalone Module (Recommended)
```
irStudy/
├── frontend/                    # Main platform
├── backend/                     # Main platform
├── emr-practice-system/         # NEW: Separate module
│   ├── frontend/
│   └── backend/
└── shared/                      # Shared utilities
    ├── auth/
    ├── database/
    └── validation/
```

**Benefits:**
- Independent development/deployment
- Clear separation of concerns
- Can be deployed separately
- Easier testing

**Integration Points:**
1. **Shared Authentication:** Use main platform JWT tokens
2. **Shared Database:** User accounts, progress data
3. **Shared UI Components:** Design system, theme
4. **API Gateway:** Route /emr-practice/* to EMR module

#### Option 2: Integrated Module
```
irStudy/
├── frontend/
│   └── src/
│       ├── features/
│       │   ├── mcqs/
│       │   ├── osces/
│       │   └── emr-practice/    # NEW
│       └── ...
└── backend/
    └── src/
        └── api/
            └── v1/
                ├── mcqs.py
                ├── osces.py
                └── emr_practice.py  # NEW
```

**Benefits:**
- Single codebase
- Shared infrastructure
- Unified deployment
- Consistent UX

### Integration Implementation

#### 1. Authentication Integration
```typescript
// shared/auth/authContext.tsx
export const useAuth = () => {
  const token = localStorage.getItem('jwt_token');
  const user = parseJWT(token);

  return {
    token,
    user,
    isAuthenticated: !!token,
    login: (credentials) => { /* ... */ },
    logout: () => { /* ... */ }
  };
};

// emr-practice/frontend/src/App.tsx
import { useAuth } from '@/shared/auth/authContext';

function EMRApp() {
  const { isAuthenticated, user } = useAuth();

  if (!isAuthenticated) {
    return <Redirect to="/login" />;
  }

  return <EMRDashboard user={user} />;
}
```

#### 2. Database Integration
```python
# shared/database/base.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
Base = declarative_base()

# emr-practice/backend/models/session.py
from shared.database.base import Base

class EMRSession(Base):
    __tablename__ = "emr_sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))  # Links to main users table
    # ... other fields
```

#### 3. API Gateway Routing
```python
# main backend/src/main.py
from fastapi import FastAPI
from emr_practice.api import emr_router

app = FastAPI()

# Mount EMR practice routes
app.include_router(
    emr_router,
    prefix="/api/v1/emr-practice",
    tags=["emr-practice"]
)
```

#### 4. Navigation Integration
```typescript
// main frontend/src/components/Sidebar.tsx
const navItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/mcqs', label: 'MCQs' },
  { path: '/osces', label: 'OSCEs' },
  { path: '/emr-practice', label: 'EMR Practice', icon: <FileText /> },  // NEW
  { path: '/progress', label: 'Progress' },
];
```

---

## User Input Validation & Feedback System

### Validation Architecture

#### Layer 1: Client-Side Validation (Instant)
```typescript
// frontend/src/components/ProgressNoteEditor.tsx
const soapNoteSchema = z.object({
  subjective: z.string()
    .min(50, 'Subjective section must be at least 50 characters')
    .max(2000, 'Too long'),
  objective: z.string()
    .min(50, 'Objective section must be at least 50 characters')
    .max(2000, 'Too long'),
  assessment: z.string()
    .min(30, 'Assessment section must be at least 30 characters')
    .max(1000, 'Too long'),
  plan: z.string()
    .min(30, 'Plan section must be at least 30 characters')
    .max(1500, 'Too long'),
});

// Real-time validation as user types
const { errors } = useForm({ resolver: zodResolver(soapNoteSchema) });
```

**Feedback:** Immediate inline errors (red border, error message below field)

#### Layer 2: Rule-Based Validation (2-3 seconds)
```python
# backend/services/validation_rules.py
class SOAPNoteRules:
    """Fast rule-based validation before AI analysis"""

    def validate_structure(self, soap_note: SOAPNote) -> List[ValidationError]:
        errors = []

        # Check all sections present
        if not soap_note.subjective:
            errors.append(ValidationError("subjective", "Subjective section missing"))

        # Check minimum content
        if len(soap_note.subjective.split()) < 20:
            errors.append(ValidationError("subjective", "Too brief - needs more detail"))

        # Check for critical keywords in assessment
        if not any(word in soap_note.assessment.lower() for word in ['diagnosis', 'differential', 'problem']):
            errors.append(ValidationError("assessment", "Should include diagnosis or differential"))

        # Check plan has investigations/management
        if not any(word in soap_note.plan.lower() for word in ['investigation', 'medication', 'follow-up', 'refer']):
            errors.append(ValidationError("plan", "Plan should include investigations or management"))

        return errors

class PrescriptionRules:
    """PBS and medication safety rules"""

    def __init__(self):
        self.pbs_database = load_pbs_database()
        self.drug_interactions = load_interaction_database()

    def validate_prescription(self, rx: Prescription, patient: Patient) -> ValidationResult:
        errors = []
        warnings = []

        # PBS compliance
        if not self.check_pbs_listed(rx.medication):
            errors.append("Medication not PBS-listed")

        # Dose range check
        if not self.check_dose_range(rx.medication, rx.dose, patient.age, patient.weight):
            errors.append(f"Dose {rx.dose} outside recommended range")

        # Allergy check
        if self.check_allergy(rx.medication, patient.allergies):
            errors.append(f"CRITICAL: Patient allergic to {rx.medication}")

        # Drug interactions
        interactions = self.check_interactions(rx.medication, patient.current_medications)
        if interactions:
            warnings.extend(interactions)

        # Indication check
        if not rx.indication or len(rx.indication) < 5:
            errors.append("Indication required (PBS requirement)")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

**Feedback:** Immediate structured errors/warnings panel

#### Layer 3: AI-Powered Deep Validation (5-8 seconds)
```python
# backend/agents/soap_validator.py
from anthropic import Anthropic

class SOAPNoteValidator:
    """AI-powered clinical validation using Claude 3.5 Sonnet"""

    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.rag_service = RAGService()

    async def validate(self, soap_note: SOAPNote, patient: Patient) -> DetailedFeedback:
        # Get relevant medical knowledge from RAG
        context = await self.rag_service.get_relevant_context(
            query=patient.presenting_complaint,
            top_k=5
        )

        prompt = f"""You are an experienced Australian clinical educator reviewing a medical student's SOAP note for AMC Clinical Examination preparation.

PATIENT SCENARIO:
{patient.clinical_scenario}

Presenting Complaint: {patient.presenting_complaint}
Key History: {patient.history_summary}

STUDENT'S SOAP NOTE:
Subjective: {soap_note.subjective}
Objective: {soap_note.objective}
Assessment: {soap_note.assessment}
Plan: {soap_note.plan}

RELEVANT MEDICAL KNOWLEDGE:
{context}

Evaluate this SOAP note using Australian medical standards. Provide feedback in this JSON format:

{{
  "overall_score": <0-100>,
  "criteria_scores": [
    {{
      "criterion": "Completeness",
      "score": <0-10>,
      "feedback": "..."
    }},
    {{
      "criterion": "Clinical Accuracy",
      "score": <0-10>,
      "feedback": "..."
    }},
    {{
      "criterion": "Australian Terminology",
      "score": <0-10>,
      "feedback": "..."
    }},
    {{
      "criterion": "Safety & Red Flags",
      "score": <0-10>,
      "feedback": "..."
    }},
    {{
      "criterion": "Management Plan",
      "score": <0-10>,
      "feedback": "..."
    }}
  ],
  "strengths": ["...", "...", "..."],
  "improvements": ["...", "...", "..."],
  "specific_suggestions": [
    {{
      "issue": "...",
      "suggestion": "...",
      "example": "..."
    }}
  ],
  "australian_compliance": {{
    "terminology_correct": true/false,
    "pbs_mbs_mentioned": true/false,
    "safety_netting_present": true/false
  }},
  "overall_feedback": "2-3 sentences of constructive feedback"
}}

Be specific, constructive, and educational. Focus on AMC Clinical Examination readiness and AHPRA clinical competency standards."""

        response = await self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            temperature=0.2,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse AI response
        feedback = self._parse_json_response(response.content[0].text)

        # Store feedback in database
        await self._save_validation(soap_note.id, feedback)

        return feedback
```

**Feedback:** Comprehensive detailed analysis with actionable suggestions

---

## Validation Feedback UI

### Feedback Panel Design

```typescript
// components/common/ValidationPanel.tsx
interface ValidationPanelProps {
  validationResult: ValidationResult;
  onRevise: () => void;
  onAccept: () => void;
}

export const ValidationPanel: React.FC<ValidationPanelProps> = ({
  validationResult,
  onRevise,
  onAccept
}) => {
  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Overall Score */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-xl font-semibold">Overall Score</h3>
          <div className={`text-4xl font-bold ${getScoreColor(validationResult.overall_score)}`}>
            {validationResult.overall_score}/100
          </div>
        </div>
        <ProgressBar value={validationResult.overall_score} max={100} />
        <p className="text-sm text-gray-600 mt-2">{validationResult.overall_feedback}</p>
      </div>

      {/* Criteria Breakdown */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3">Criteria Scores</h4>
        {validationResult.criteria_scores.map((criterion, index) => (
          <div key={index} className="mb-4">
            <div className="flex items-center justify-between mb-1">
              <span className="font-medium">{criterion.criterion}</span>
              <span className={`font-bold ${getScoreColor(criterion.score * 10)}`}>
                {criterion.score}/10
              </span>
            </div>
            <ProgressBar value={criterion.score} max={10} />
            <p className="text-sm text-gray-600 mt-1">{criterion.feedback}</p>
          </div>
        ))}
      </div>

      {/* Strengths */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <CheckCircle className="text-green-600" />
          Strengths
        </h4>
        <ul className="space-y-2">
          {validationResult.strengths.map((strength, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-green-600 mt-1">✓</span>
              <span className="text-sm">{strength}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Areas for Improvement */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3 flex items-center gap-2">
          <AlertCircle className="text-orange-600" />
          Areas for Improvement
        </h4>
        <ul className="space-y-2">
          {validationResult.improvements.map((improvement, index) => (
            <li key={index} className="flex items-start gap-2">
              <span className="text-orange-600 mt-1">•</span>
              <span className="text-sm">{improvement}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Specific Suggestions */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3">Specific Suggestions</h4>
        {validationResult.specific_suggestions.map((suggestion, index) => (
          <div key={index} className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-3">
            <p className="font-medium text-blue-900 mb-1">{suggestion.issue}</p>
            <p className="text-sm text-blue-800 mb-2">{suggestion.suggestion}</p>
            {suggestion.example && (
              <div className="bg-white rounded p-2 text-sm font-mono">
                <span className="text-gray-500">Example:</span> {suggestion.example}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Australian Compliance Badges */}
      <div className="mb-6">
        <h4 className="font-semibold mb-3">Australian Standards</h4>
        <div className="flex flex-wrap gap-2">
          <ComplianceBadge
            label="Terminology"
            passed={validationResult.australian_compliance.terminology_correct}
          />
          <ComplianceBadge
            label="PBS/MBS"
            passed={validationResult.australian_compliance.pbs_mbs_mentioned}
          />
          <ComplianceBadge
            label="Safety Netting"
            passed={validationResult.australian_compliance.safety_netting_present}
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-3">
        <button
          onClick={onRevise}
          className="flex-1 btn-secondary"
        >
          Revise & Resubmit
        </button>
        <button
          onClick={onAccept}
          className="flex-1 btn-primary"
        >
          Accept & Continue
        </button>
      </div>
    </div>
  );
};
```

---

## Validation Rule Examples

### SOAP Note Validation Rules

#### Rule 1: Completeness Check
```python
def check_completeness(soap_note: SOAPNote) -> List[Issue]:
    issues = []

    # Subjective checks
    if len(soap_note.subjective.split()) < 30:
        issues.append(Issue(
            field="subjective",
            severity="error",
            message="Subjective section too brief",
            suggestion="Include: chief complaint, HPI details (onset, duration, severity, aggravating/relieving factors), relevant PMHx, medications, allergies"
        ))

    # Must mention key symptoms
    if not any(keyword in soap_note.subjective.lower() for keyword in ['pain', 'symptom', 'complaint', 'problem', 'concern']):
        issues.append(Issue(
            field="subjective",
            severity="warning",
            message="Patient's main symptom unclear",
            suggestion="Clearly state the presenting symptom in patient's words"
        ))

    # Objective checks
    vital_signs_keywords = ['bp', 'hr', 'rr', 'temp', 'spo2', 'blood pressure', 'heart rate']
    if not any(keyword in soap_note.objective.lower() for keyword in vital_signs_keywords):
        issues.append(Issue(
            field="objective",
            severity="error",
            message="Vital signs missing",
            suggestion="Always document: BP, HR, RR, Temp, SpO2 (even if normal)"
        ))

    # Assessment checks
    if not any(keyword in soap_note.assessment.lower() for keyword in ['diagnosis', 'differential', 'impression', 'likely']):
        issues.append(Issue(
            field="assessment",
            severity="error",
            message="No clear diagnosis stated",
            suggestion="State primary diagnosis and 2-3 differentials if uncertain"
        ))

    # Plan checks
    plan_components = ['investigation', 'medication', 'imaging', 'refer', 'follow-up', 'admit', 'discharge']
    if not any(keyword in soap_note.plan.lower() for keyword in plan_components):
        issues.append(Issue(
            field="plan",
            severity="error",
            message="Plan lacks specific actions",
            suggestion="Include: investigations to order, medications to prescribe, follow-up arrangements"
        ))

    return issues
```

#### Rule 2: Australian Terminology Check
```python
def check_australian_terminology(text: str) -> List[Issue]:
    issues = []

    # American vs. Australian terms
    american_terms = {
        'acetaminophen': 'paracetamol',
        'epinephrine': 'adrenaline',
        'albuterol': 'salbutamol',
        'primary care physician': 'GP',
        'operating room': 'operating theatre',
        'ER': 'ED',
        'program': 'programme'
    }

    for american, australian in american_terms.items():
        if american in text.lower():
            issues.append(Issue(
                field="terminology",
                severity="warning",
                message=f"American term '{american}' used",
                suggestion=f"Use Australian term: '{australian}'"
            ))

    # PBS/MBS mention check
    if any(word in text.lower() for word in ['medication', 'prescription', 'drug', 'tablet']):
        if 'pbs' not in text.lower():
            issues.append(Issue(
                field="plan",
                severity="info",
                message="Consider mentioning PBS",
                suggestion="For prescriptions, mention PBS compliance or streamlined authority"
            ))

    if any(word in text.lower() for word in ['blood test', 'imaging', 'xray', 'ultrasound']):
        if 'mbs' not in text.lower():
            issues.append(Issue(
                field="plan",
                severity="info",
                message="Consider mentioning MBS",
                suggestion="For investigations, can mention relevant MBS item numbers"
            ))

    return issues
```

#### Rule 3: Clinical Red Flags
```python
def check_red_flags(soap_note: SOAPNote, patient: Patient) -> List[Issue]:
    issues = []

    # Chest pain red flags
    if 'chest pain' in patient.presenting_complaint.lower():
        red_flags = ['cardiac', 'ecg', 'troponin', 'aspirin', 'nitrate']
        if not any(flag in soap_note.plan.lower() for flag in red_flags):
            issues.append(Issue(
                field="plan",
                severity="critical",
                message="Chest pain red flags not addressed",
                suggestion="For chest pain: ECG, troponin, consider ACS protocol"
            ))

    # Headache red flags
    if 'headache' in patient.presenting_complaint.lower():
        red_flags = ['thunderclap', 'worst ever', 'sudden', 'neurological', 'ct head']
        if any(flag in soap_note.subjective.lower() for flag in red_flags[:3]):
            if 'ct' not in soap_note.plan.lower() and 'imaging' not in soap_note.plan.lower():
                issues.append(Issue(
                    field="plan",
                    severity="critical",
                    message="Red flag headache - imaging not mentioned",
                    suggestion="Thunderclap/worst headache: urgent CT head to exclude SAH"
                ))

    # Sepsis screening
    sepsis_symptoms = ['fever', 'hypotension', 'tachycardia', 'confusion']
    if sum(1 for symptom in sepsis_symptoms if symptom in soap_note.subjective.lower()) >= 2:
        if 'sepsis' not in soap_note.assessment.lower():
            issues.append(Issue(
                field="assessment",
                severity="critical",
                message="Possible sepsis not considered",
                suggestion="Multiple SIRS criteria present - consider sepsis in differential"
            ))

    return issues
```

### Prescription Validation Rules

```python
class PrescriptionValidator:
    def __init__(self):
        self.pbs_db = load_pbs_database()
        self.bnf_db = load_bnf_database()
        self.interactions_db = load_interactions()

    def validate(self, rx: Prescription, patient: Patient) -> ValidationResult:
        errors = []
        warnings = []
        info = []

        # 1. PBS Check
        pbs_result = self.check_pbs_compliance(rx)
        if not pbs_result.is_listed:
            errors.append(f"{rx.medication} not PBS-listed - check spelling or use generic name")
        elif pbs_result.requires_authority:
            info.append(f"Streamlined authority required for {rx.medication}")

        # 2. Dose Check
        dose_result = self.check_dose_appropriateness(rx, patient)
        if dose_result.outside_range:
            errors.append(f"Dose {rx.dose} outside recommended range ({dose_result.min_dose}-{dose_result.max_dose})")

        # 3. Renal/Hepatic Adjustment
        if patient.has_renal_impairment():
            if rx.medication in self.bnf_db.renal_dose_adjust:
                warnings.append(f"{rx.medication} requires renal dose adjustment - check eGFR")

        # 4. Age Appropriateness
        if patient.age > 65:
            if rx.medication in ['anticholinergics', 'benzodiazepines', 'nsaids']:
                warnings.append(f"{rx.medication} in elderly - consider Beers Criteria")

        # 5. Pregnancy/Breastfeeding
        if patient.is_pregnant():
            if rx.medication in self.bnf_db.pregnancy_category_d_x:
                errors.append(f"{rx.medication} contraindicated in pregnancy (Category {self.bnf_db.get_pregnancy_cat(rx.medication)})")

        # 6. Allergy Check
        allergy_match = self.check_allergy(rx.medication, patient.allergies)
        if allergy_match:
            errors.append(f"CRITICAL: Patient has documented {allergy_match.allergen} allergy")

        # 7. Drug Interactions
        interactions = self.check_interactions(rx.medication, patient.current_medications)
        for interaction in interactions:
            if interaction.severity == 'major':
                errors.append(f"Major interaction with {interaction.drug_b}: {interaction.effect}")
            elif interaction.severity == 'moderate':
                warnings.append(f"Moderate interaction with {interaction.drug_b}: {interaction.effect}")

        # 8. Indication Check
        if not rx.indication or len(rx.indication) < 5:
            errors.append("Indication required (PBS requirement)")

        # 9. Quantity/Duration Check
        if rx.quantity > 100 and rx.medication not in self.pbs_db.high_quantity_approved:
            warnings.append(f"Quantity {rx.quantity} unusually high - verify")

        if rx.repeats > 5:
            errors.append("Maximum 5 repeats allowed")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            score=self._calculate_score(errors, warnings, info)
        )
```

---

## Next Steps

1. **Review PRD:** Project team reviews and approves
2. **Create detailed sub-PRDs:**
   - UI/UX Design PRD
   - Backend Architecture PRD
   - Validation Rules PRD
   - Integration PRD
3. **Stakeholder Review:** Clinical educators validate rules
4. **RALPH Agent Setup:** Configure agents for implementation
5. **Sprint Planning:** Break into 2-week sprints

---

**Document Status:** Draft v1.0
**Next Review:** 2026-02-05
**Approvers:** Product Manager, Clinical Lead, Tech Lead
