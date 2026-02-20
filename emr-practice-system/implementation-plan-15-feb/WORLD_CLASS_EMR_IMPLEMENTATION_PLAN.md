# World-Class EMR Practice System Implementation Plan

**Date**: 2026-02-15
**Project**: irStudy - EMR Practice System for AMC Clinical Examination Preparation
**Timeline**: 12 weeks (March 1 - May 23, 2026)
**Quality Bar**: World-class production system
**Scope**: Both Cerner PowerChart & Epic EHR with full OSCE integration

---

## Executive Summary

### Vision Update
Create a **world-class** hospital Electronic Medical Record (EMR) simulation system for medical students preparing for **AMC Clinical Examination** and Australian hospital practice. The system will provide authentic Cerner PowerChart and Epic EHR experiences with AI-powered validation, complete Australian SOAP note support, and seamless OSCE station integration.

### User Requirements (from Feb 15, 2026)
- **EMR Systems**: Both Cerner PowerChart and Epic EHR developed simultaneously
- **Learning Goals**: UI familiarity + Clinical workflows + OSCE integration (comprehensive)
- **Documentation Formats**: Australian SOAP notes, Progress notes, Discharge summaries, Procedure notes (all formats)
- **Timeline**: 12+ weeks for world-class quality
- **Target**: AMC Clinical Examination preparation (NOT ICRP - per project constraints)

### Success Metrics (World-Class Standards)
- **Speed**: Users complete Australian SOAP notes in <8 minutes (expert level)
- **Accuracy**: 95%+ compliance with AHPRA and NSW Health EMR standards
- **Engagement**: 90%+ users practice at least 5 sessions per week
- **Validation**: AI feedback accuracy 90%+ vs. human clinical educator review
- **Pass Rate**: Users show 50%+ improvement in documentation quality after 30 sessions
- **OSCE Integration**: 100% of OSCE stations support EMR documentation
- **System Reliability**: 99.9% uptime, <200ms p95 response time

---

## Current State Analysis

### ✅ What Exists (Planning Phase)
1. **Master PRD** (`00_MASTER_EMR_PRD.md`) - 31KB, comprehensive vision
2. **Cerner PowerChart UI PRD** (`01_CERNER_POWERCHART_UI_PRD.md`) - 27KB, detailed UI specs
3. **Epic EHR UI PRD** (`02_EPIC_EHR_UI_PRD.md`) - 37KB, detailed UI specs
4. **Backend API PRD** (`03_BACKEND_API_PRD.md`) - 33KB, API specifications
5. **Testing Strategy PRD** (`04_TESTING_STRATEGY_PRD.md`) - 33KB, test approach

### ❌ What's Missing (0% Implementation)
1. **No code written** - All PRDs are planning documents only
2. **No database schema** - EMR-specific tables not created
3. **No frontend components** - Neither Cerner nor Epic UI built
4. **No backend endpoints** - API not implemented
5. **No test suite** - No tests written
6. **No OSCE integration** - Not connected to existing OSCE system
7. **No Australian content** - PRDs mention ICRP (should be AMC Clinical Exam)

### Critical Updates Required
1. **Replace ICRP references with AMC Clinical Examination** throughout all PRDs
2. **Add Australian-specific requirements**:
   - AHPRA compliance for clinical documentation
   - NSW Health EMR standards
   - Australian SOAP note format (per constraints)
   - PBS (Pharmaceutical Benefits Scheme) integration
   - MBS (Medicare Benefits Schedule) for pathology
3. **OSCE Integration Design** - How EMR connects to existing OSCE stations
4. **AI Validation with Australian Clinical Guidelines** - Reference Australian sources

---

## Implementation Phases (12 Weeks)

### Phase 1: Foundation & Database (Weeks 1-2)
**Duration**: 2 weeks (March 1-14)
**Goal**: Set up infrastructure, database schema, authentication

#### Week 1: Database Schema & Models
**Deliverables**:
- [ ] EMR-specific database tables created
- [ ] Alembic migrations for EMR schema
- [ ] SQLAlchemy models for all entities
- [ ] Seed data for 50 patient scenarios (Australian demographics)

**Database Tables**:
```sql
-- EMR Session Management
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,
    emr_system VARCHAR(20) NOT NULL CHECK (emr_system IN ('cerner', 'epic')),
    patient_scenario_id UUID REFERENCES patient_scenarios(id),
    osce_id VARCHAR(50) REFERENCES osces(osce_id),  -- Link to OSCE station
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    session_data JSONB,  -- Stores draft notes, current state
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Patient Scenarios (200+ scenarios for practice)
CREATE TABLE patient_scenarios (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(10) UNIQUE NOT NULL,  -- Medical Record Number
    full_name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    indigenous_status VARCHAR(50),  -- Aboriginal/Torres Strait Islander
    allergies TEXT[],  -- Array of allergies
    current_medications JSONB,
    medical_history JSONB,
    vital_signs JSONB,
    presenting_complaint TEXT NOT NULL,
    specialty VARCHAR(50) NOT NULL,  -- Cardiology, Respiratory, etc.
    complexity_level VARCHAR(20) NOT NULL,  -- Simple, Moderate, Complex
    clinical_scenario TEXT NOT NULL,  -- Full case description
    expected_diagnosis VARCHAR(200),
    australian_guidelines_url TEXT,  -- Link to relevant Australian guidelines
    created_at TIMESTAMP DEFAULT NOW()
);

-- SOAP Notes (Australian Format)
CREATE TABLE soap_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID REFERENCES emr_sessions(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    patient_scenario_id UUID REFERENCES patient_scenarios(id) NOT NULL,

    -- SOAP Sections (Australian format per constraints)
    subjective TEXT NOT NULL,  -- Min 50 chars
    objective TEXT NOT NULL,   -- Min 50 chars
    assessment TEXT NOT NULL,  -- Min 50 chars
    plan TEXT NOT NULL,        -- Min 50 chars

    -- Metadata
    note_type VARCHAR(50) NOT NULL,  -- Progress, Admission, Discharge
    typing_wpm INTEGER,  -- Words per minute
    completion_time_seconds INTEGER,  -- Time to complete
    draft_saves INTEGER DEFAULT 0,

    -- Validation Results
    validation_score DECIMAL(5,2),  -- 0-100
    validation_feedback JSONB,
    ahpra_compliant BOOLEAN,
    clinical_accuracy_score DECIMAL(5,2),

    -- Timestamps
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Prescriptions (PBS Integration)
CREATE TABLE prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID REFERENCES emr_sessions(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    patient_scenario_id UUID REFERENCES patient_scenarios(id) NOT NULL,

    -- Prescription Details
    medication_name VARCHAR(200) NOT NULL,
    pbs_code VARCHAR(20),  -- PBS item number
    dose VARCHAR(100) NOT NULL,
    frequency VARCHAR(100) NOT NULL,
    route VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    repeats INTEGER NOT NULL CHECK (repeats <= 5),
    indication TEXT NOT NULL,

    -- Safety Checks
    drug_interactions_checked BOOLEAN DEFAULT FALSE,
    dose_appropriate BOOLEAN,
    pbs_compliant BOOLEAN,

    -- Validation Results
    validation_score DECIMAL(5,2),
    validation_feedback JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Pathology Orders (MBS Integration)
CREATE TABLE pathology_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID REFERENCES emr_sessions(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    patient_scenario_id UUID REFERENCES patient_scenarios(id) NOT NULL,

    -- Order Details
    test_name VARCHAR(200) NOT NULL,
    mbs_item_number VARCHAR(20),  -- Medicare Benefits Schedule
    urgency VARCHAR(20) NOT NULL CHECK (urgency IN ('Routine', 'Urgent', 'Emergency')),
    clinical_indication TEXT NOT NULL,

    -- Panel or Individual Test
    is_panel BOOLEAN DEFAULT FALSE,
    panel_tests JSONB,  -- If panel, list of individual tests

    -- Validation
    indication_appropriate BOOLEAN,
    mbs_compliant BOOLEAN,
    validation_score DECIMAL(5,2),
    validation_feedback JSONB,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Progress Tracking (EMR-specific)
CREATE TABLE emr_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) NOT NULL,

    -- Typing Metrics
    avg_typing_wpm INTEGER,
    avg_completion_time_seconds INTEGER,
    total_notes_completed INTEGER DEFAULT 0,
    total_prescriptions_written INTEGER DEFAULT 0,
    total_pathology_orders INTEGER DEFAULT 0,

    -- Quality Metrics
    avg_soap_note_score DECIMAL(5,2),
    avg_prescription_score DECIMAL(5,2),
    ahpra_compliance_rate DECIMAL(5,2),

    -- Practice Stats
    total_practice_sessions INTEGER DEFAULT 0,
    total_practice_time_minutes INTEGER DEFAULT 0,
    cerner_sessions INTEGER DEFAULT 0,
    epic_sessions INTEGER DEFAULT 0,

    -- Improvement Tracking
    first_soap_score DECIMAL(5,2),
    latest_soap_score DECIMAL(5,2),
    improvement_percentage DECIMAL(5,2),

    -- Specialty Breakdown
    specialty_stats JSONB,  -- {cardiology: 10, respiratory: 5, ...}

    updated_at TIMESTAMP DEFAULT NOW()
);

-- OSCE EMR Integration (Link to existing OSCE system)
CREATE TABLE osce_emr_integration (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    osce_id VARCHAR(50) REFERENCES osces(osce_id) NOT NULL,

    -- EMR Configuration for OSCE Station
    requires_emr BOOLEAN DEFAULT FALSE,
    emr_system VARCHAR(20) CHECK (emr_system IN ('cerner', 'epic', 'either')),
    patient_scenario_id UUID REFERENCES patient_scenarios(id),

    -- Required Documentation
    requires_soap_note BOOLEAN DEFAULT FALSE,
    requires_prescription BOOLEAN DEFAULT FALSE,
    requires_pathology BOOLEAN DEFAULT FALSE,
    requires_procedure_note BOOLEAN DEFAULT FALSE,

    -- Time Limits
    documentation_time_limit_minutes INTEGER,

    -- Scoring
    documentation_weight_percentage INTEGER,  -- % of total OSCE score

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for Performance
CREATE INDEX idx_emr_sessions_user_id ON emr_sessions(user_id);
CREATE INDEX idx_emr_sessions_osce_id ON emr_sessions(osce_id);
CREATE INDEX idx_soap_notes_user_id ON soap_notes(user_id);
CREATE INDEX idx_soap_notes_session_id ON soap_notes(emr_session_id);
CREATE INDEX idx_prescriptions_user_id ON prescriptions(user_id);
CREATE INDEX idx_pathology_orders_user_id ON pathology_orders(user_id);
CREATE INDEX idx_patient_scenarios_specialty ON patient_scenarios(specialty);
CREATE INDEX idx_patient_scenarios_complexity ON patient_scenarios(complexity_level);
```

**Backend Models** (`backend/src/db/models/emr.py`):
```python
from sqlalchemy import Column, String, Integer, Boolean, DECIMAL, TIMESTAMP, Text, ARRAY, CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from ..base import Base

class EMRSession(Base):
    __tablename__ = "emr_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    emr_system = Column(String(20), CheckConstraint("emr_system IN ('cerner', 'epic')"), nullable=False)
    patient_scenario_id = Column(UUID(as_uuid=True), ForeignKey("patient_scenarios.id"))
    osce_id = Column(String(50), ForeignKey("osces.osce_id"))
    started_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    completed_at = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    session_data = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="emr_sessions")
    patient_scenario = relationship("PatientScenario", back_populates="emr_sessions")
    osce = relationship("OSCE", back_populates="emr_sessions")
    soap_notes = relationship("SOAPNote", back_populates="emr_session")
    prescriptions = relationship("Prescription", back_populates="emr_session")
    pathology_orders = relationship("PathologyOrder", back_populates="emr_session")

class PatientScenario(Base):
    __tablename__ = "patient_scenarios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mrn = Column(String(10), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    indigenous_status = Column(String(50))
    allergies = Column(ARRAY(Text))
    current_medications = Column(JSONB)
    medical_history = Column(JSONB)
    vital_signs = Column(JSONB)
    presenting_complaint = Column(Text, nullable=False)
    specialty = Column(String(50), nullable=False)
    complexity_level = Column(String(20), nullable=False)
    clinical_scenario = Column(Text, nullable=False)
    expected_diagnosis = Column(String(200))
    australian_guidelines_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    # Relationships
    emr_sessions = relationship("EMRSession", back_populates="patient_scenario")
    soap_notes = relationship("SOAPNote", back_populates="patient_scenario")
    prescriptions = relationship("Prescription", back_populates="patient_scenario")
    pathology_orders = relationship("PathologyOrder", back_populates="patient_scenario")

# Additional models: SOAPNote, Prescription, PathologyOrder, EMRProgress, OSCEEMRIntegration
# (Similar structure - full code in implementation)
```

#### Week 2: Authentication & API Foundation
**Deliverables**:
- [ ] EMR-specific API endpoints (sessions, patients)
- [ ] Authentication integration (reuse existing auth system)
- [ ] CORS configuration for frontend
- [ ] OpenAPI documentation setup
- [ ] Basic health check endpoints

**API Endpoints** (`backend/src/api/v1/emr_sessions.py`):
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import uuid

from ...db.base import get_db
from ...db.models.emr import EMRSession, PatientScenario
from ...schemas.emr import EMRSessionCreate, EMRSessionResponse, PatientScenarioResponse
from ...api.dependencies import get_current_user

router = APIRouter(prefix="/emr", tags=["EMR Practice System"])

@router.post("/sessions", response_model=EMRSessionResponse, status_code=status.HTTP_201_CREATED)
async def start_emr_session(
    session_data: EMRSessionCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new EMR practice session.

    - **emr_system**: Either 'cerner' or 'epic'
    - **patient_scenario_id**: Optional patient to load (random if not provided)
    - **osce_id**: Optional OSCE station link
    """
    # Implementation
    pass

@router.get("/sessions/{session_id}", response_model=EMRSessionResponse)
async def get_emr_session(
    session_id: uuid.UUID,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get EMR session details including current state and drafts."""
    pass

@router.get("/patients", response_model=List[PatientScenarioResponse])
async def list_patient_scenarios(
    specialty: str = None,
    complexity: str = None,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    List available patient scenarios for practice.

    - **specialty**: Filter by specialty (cardiology, respiratory, etc.)
    - **complexity**: Filter by complexity (simple, moderate, complex)
    """
    pass

@router.get("/patients/{patient_id}", response_model=PatientScenarioResponse)
async def get_patient_scenario(
    patient_id: uuid.UUID,
    db: Session = Depends(get_db)
):
    """Get full patient scenario details for EMR practice."""
    pass
```

**Success Criteria**:
- [ ] All database tables created successfully
- [ ] Alembic migrations run without errors
- [ ] Seed data loads 50 patient scenarios
- [ ] API endpoints return 200 OK with proper authentication
- [ ] OpenAPI docs accessible at `/docs`

---

### Phase 2: Cerner PowerChart UI (Weeks 3-5)
**Duration**: 3 weeks (March 15 - April 4)
**Goal**: Build complete Cerner PowerChart simulation UI

#### Week 3: Cerner Layout & Navigation
**Components to Build**:
- [ ] `CernerLayout.tsx` - Main layout with dark sidebar
- [ ] `CernerSidebar.tsx` - 7 navigation modules
- [ ] `CernerHeader.tsx` - Patient banner, search, user menu
- [ ] `CernerPatientBanner.tsx` - Patient demographics display
- [ ] `CernerDashboard.tsx` - Landing page with stats

**Visual Requirements** (from PRD):
```tsx
// frontend/src/components/emr/cerner/CernerLayout.tsx
import { useState } from 'react';
import { Box, Drawer, AppBar, Toolbar, Typography } from '@mui/material';
import { CernerSidebar } from './CernerSidebar';
import { CernerHeader } from './CernerHeader';
import { CernerPatientBanner } from './CernerPatientBanner';

const CERNER_THEME = {
  primary: '#2c3e50',      // Dark blue-grey
  primaryDark: '#1a252f',  // Darker sidebar
  accent: '#3498db',       // Blue accent
  success: '#27ae60',
  warning: '#f39c12',
  error: '#e74c3c',
  textPrimary: '#ecf0f1',
  textSecondary: '#bdc3c7',
};

export const CernerLayout = ({ children }: { children: React.ReactNode }) => {
  const [currentModule, setCurrentModule] = useState('dashboard');
  const [currentPatient, setCurrentPatient] = useState(null);

  return (
    <Box sx={{ display: 'flex', height: '100vh', bgcolor: '#1a252f' }}>
      {/* Left Sidebar - 240px */}
      <CernerSidebar
        currentModule={currentModule}
        onModuleChange={setCurrentModule}
      />

      {/* Main Content Area */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Top Header */}
        <CernerHeader currentPatient={currentPatient} />

        {/* Patient Banner (if patient selected) */}
        {currentPatient && (
          <CernerPatientBanner patient={currentPatient} />
        )}

        {/* Content Area */}
        <Box sx={{ flexGrow: 1, overflow: 'auto', p: 3 }}>
          {children}
        </Box>
      </Box>
    </Box>
  );
};
```

#### Week 4: Cerner SOAP Note Editor
**Components to Build**:
- [ ] `CernerProgressNotes.tsx` - Progress notes module
- [ ] `SOAPNoteEditor.tsx` - 4-section editor (Subjective, Objective, Assessment, Plan)
- [ ] `TypingMetrics.tsx` - Real-time WPM display
- [ ] `DraftSaver.tsx` - Auto-save every 30 seconds
- [ ] `ValidationPanel.tsx` - AI feedback display

**Australian SOAP Note Format** (per constraints):
```tsx
// frontend/src/components/emr/cerner/SOAPNoteEditor.tsx
import { useState, useEffect } from 'react';
import { Box, TextField, Typography, LinearProgress, Alert } from '@mui/material';
import { useDebounce } from '../../../hooks/useDebounce';
import { calculateWPM } from '../../../utils/typingMetrics';

interface SOAPNoteEditorProps {
  sessionId: string;
  patientScenario: PatientScenario;
  onSave: (note: SOAPNote) => Promise<void>;
}

export const SOAPNoteEditor = ({ sessionId, patientScenario, onSave }: SOAPNoteEditorProps) => {
  const [subjective, setSubjective] = useState('');
  const [objective, setObjective] = useState('');
  const [assessment, setAssessment] = useState('');
  const [plan, setPlan] = useState('');
  const [typingWPM, setTypingWPM] = useState(0);
  const [startTime, setStartTime] = useState(Date.now());
  const [validationErrors, setValidationErrors] = useState<string[]>([]);

  // Auto-save draft every 30 seconds
  const debouncedNote = useDebounce({ subjective, objective, assessment, plan }, 30000);

  useEffect(() => {
    if (debouncedNote) {
      saveDraft(debouncedNote);
    }
  }, [debouncedNote]);

  // Calculate WPM in real-time
  useEffect(() => {
    const totalText = subjective + objective + assessment + plan;
    const timeElapsedMinutes = (Date.now() - startTime) / 60000;
    const wordCount = totalText.split(/\s+/).filter(w => w.length > 0).length;
    setTypingWPM(Math.round(wordCount / timeElapsedMinutes));
  }, [subjective, objective, assessment, plan, startTime]);

  // Validate minimum character requirements (Australian SOAP format)
  const validateSection = (text: string, sectionName: string) => {
    if (text.length < 50) {
      return `${sectionName} must be at least 50 characters (currently ${text.length})`;
    }
    return null;
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Typing Metrics Display */}
      <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ color: CERNER_THEME.textPrimary }}>
          Progress Note - Australian SOAP Format
        </Typography>
        <Typography variant="body2" sx={{ color: CERNER_THEME.textSecondary }}>
          Typing Speed: {typingWPM} WPM | Target: 30+ WPM
        </Typography>
      </Box>

      {/* Patient Context */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <strong>Patient:</strong> {patientScenario.full_name} ({patientScenario.age}yo {patientScenario.gender})<br />
        <strong>Presenting Complaint:</strong> {patientScenario.presenting_complaint}
      </Alert>

      {/* Subjective Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ color: CERNER_THEME.accent, mb: 1 }}>
          Subjective (S) - Patient's History
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={4}
          value={subjective}
          onChange={(e) => setSubjective(e.target.value)}
          placeholder="Patient reports... History of presenting complaint, relevant past medical history, medications, allergies..."
          error={subjective.length > 0 && subjective.length < 50}
          helperText={`${subjective.length} / 50 characters minimum`}
          sx={{
            bgcolor: '#2c3e50',
            '& .MuiInputBase-input': { color: CERNER_THEME.textPrimary },
          }}
        />
      </Box>

      {/* Objective Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ color: CERNER_THEME.accent, mb: 1 }}>
          Objective (O) - Clinical Findings
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={4}
          value={objective}
          onChange={(e) => setObjective(e.target.value)}
          placeholder="Vital signs, physical examination findings, relevant investigation results..."
          error={objective.length > 0 && objective.length < 50}
          helperText={`${objective.length} / 50 characters minimum`}
          sx={{
            bgcolor: '#2c3e50',
            '& .MuiInputBase-input': { color: CERNER_THEME.textPrimary },
          }}
        />
      </Box>

      {/* Assessment Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ color: CERNER_THEME.accent, mb: 1 }}>
          Assessment (A) - Clinical Impression
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={3}
          value={assessment}
          onChange={(e) => setAssessment(e.target.value)}
          placeholder="Diagnosis or differential diagnoses, clinical reasoning..."
          error={assessment.length > 0 && assessment.length < 50}
          helperText={`${assessment.length} / 50 characters minimum`}
          sx={{
            bgcolor: '#2c3e50',
            '& .MuiInputBase-input': { color: CERNER_THEME.textPrimary },
          }}
        />
      </Box>

      {/* Plan Section */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ color: CERNER_THEME.accent, mb: 1 }}>
          Plan (P) - Management Plan
        </Typography>
        <TextField
          fullWidth
          multiline
          rows={4}
          value={plan}
          onChange={(e) => setPlan(e.target.value)}
          placeholder="Investigations, treatment plan, follow-up, patient education, safety netting..."
          error={plan.length > 0 && plan.length < 50}
          helperText={`${plan.length} / 50 characters minimum`}
          sx={{
            bgcolor: '#2c3e50',
            '& .MuiInputBase-input': { color: CERNER_THEME.textPrimary },
          }}
        />
      </Box>

      {/* Validation Errors */}
      {validationErrors.length > 0 && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          <ul style={{ margin: 0, paddingLeft: 20 }}>
            {validationErrors.map((err, idx) => (
              <li key={idx}>{err}</li>
            ))}
          </ul>
        </Alert>
      )}
    </Box>
  );
};
```

#### Week 5: Cerner Medications & Orders
**Components to Build**:
- [ ] `CernerMedications.tsx` - Prescription writing module
- [ ] `PBSMedicationSearch.tsx` - Search 4,000+ PBS medications
- [ ] `DoseCalculator.tsx` - Dose calculation widget
- [ ] `DrugInteractionChecker.tsx` - Interaction warnings
- [ ] `CernerPathology.tsx` - Pathology order entry
- [ ] `MBSTestSearch.tsx` - MBS test lookup

**Success Criteria**:
- [ ] Complete Cerner UI matches visual design from PRD
- [ ] SOAP note editor saves drafts every 30 seconds
- [ ] WPM calculation accurate
- [ ] PBS medication search functional
- [ ] All components responsive (desktop 1920x1080, tablet 1024x768)
- [ ] 80%+ test coverage for Cerner components

---

### Phase 3: Epic EHR UI (Weeks 6-8)
**Duration**: 3 weeks (April 5 - April 25)
**Goal**: Build complete Epic EHR simulation UI (parallel structure to Cerner)

#### Week 6: Epic Layout & Navigation
**Components to Build**:
- [ ] `EpicLayout.tsx` - Purple theme layout with icon bar
- [ ] `EpicIconBar.tsx` - Left icon navigation
- [ ] `EpicWorkspace.tsx` - Multi-panel workspace
- [ ] `EpicHeader.tsx` - Patient context bar
- [ ] `EpicStoryboard.tsx` - Landing dashboard

**Visual Requirements**:
```tsx
// frontend/src/components/emr/epic/EpicLayout.tsx
const EPIC_THEME = {
  primary: '#8b5cf6',       // Epic purple
  primaryDark: '#7c3aed',   // Darker purple
  primaryLight: '#a78bfa',  // Lighter purple
  bgWhite: '#ffffff',
  bgLight: '#f9fafb',
  bgGrey: '#f3f4f6',
  iconBar: '#1f2937',
  textPrimary: '#111827',
  textSecondary: '#6b7280',
};

export const EpicLayout = ({ children }: { children: React.ReactNode }) => {
  const [currentActivity, setCurrentActivity] = useState('storyboard');
  const [workspace Panels, setWorkspacePanels] = useState(['patient-summary']);

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      {/* Left Icon Bar - 64px */}
      <EpicIconBar
        currentActivity={currentActivity}
        onActivityChange={setCurrentActivity}
      />

      {/* Workspace Area */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', bgcolor: EPIC_THEME.bgWhite }}>
        <EpicHeader />
        <EpicWorkspace panels={workspacePanels}>
          {children}
        </EpicWorkspace>
      </Box>
    </Box>
  );
};
```

#### Week 7: Epic Note Writer
**Components to Build**:
- [ ] `EpicNoteWriter.tsx` - Note composition interface
- [ ] `EpicSOAPEditor.tsx` - SOAP editor (purple theme)
- [ ] `EpicTemplates.tsx` - Note templates
- [ ] `EpicSmartPhrases.tsx` - Quick text insertion

#### Week 8: Epic Med Manager & Order Entry
**Components to Build**:
- [ ] `EpicMedManager.tsx` - Medication management
- [ ] `EpicOrderEntry.tsx` - Pathology/imaging orders
- [ ] `EpicFlowsheet.tsx` - Vital signs display

**Success Criteria**:
- [ ] Complete Epic UI matches visual design from PRD
- [ ] Purple theme consistent across all components
- [ ] Icon navigation functional
- [ ] Multi-panel workspace supports drag-and-drop
- [ ] All Epic components at feature parity with Cerner
- [ ] 80%+ test coverage for Epic components

---

### Phase 4: AI Validation Service (Weeks 9-10)
**Duration**: 2 weeks (April 26 - May 9)
**Goal**: Build AI-powered validation for SOAP notes, prescriptions, pathology orders

#### Week 9: SOAP Note Validation
**Backend Service** (`backend/src/services/emr_validation.py`):
```python
from anthropic import Anthropic
from typing import Dict, List
import re

class SOAPNoteValidator:
    """
    AI-powered SOAP note validation using Claude.
    Checks compliance with AHPRA standards and Australian clinical guidelines.
    """

    def __init__(self, anthropic_client: Anthropic):
        self.client = anthropic_client
        self.australian_guidelines = self._load_australian_guidelines()

    async def validate_soap_note(
        self,
        soap_note: Dict[str, str],
        patient_scenario: Dict[str, any],
    ) -> Dict[str, any]:
        """
        Validate SOAP note against Australian standards.

        Returns:
            {
                "overall_score": 85.5,
                "ahpra_compliant": True,
                "clinical_accuracy": 90.0,
                "feedback": {
                    "subjective": ["Good history taking", "Consider asking about..."],
                    "objective": ["Complete vital signs", "Missing cardiovascular exam"],
                    "assessment": ["Diagnosis appropriate", "Consider differential: ..."],
                    "plan": ["Good safety netting", "Add follow-up timeframe"]
                },
                "red_flags_identified": True,
                "red_flags": ["Chest pain mentioned - needs urgent assessment"],
                "australian_terminology": 95.0,  # % compliance
                "terminology_issues": ["Use 'paracetamol' not 'acetaminophen'"]
            }
        """

        prompt = f"""You are an Australian clinical educator assessing a medical student's SOAP note for AMC Clinical Examination standards and AHPRA compliance.

**Patient Scenario:**
{patient_scenario['clinical_scenario']}

**Expected Diagnosis:**
{patient_scenario['expected_diagnosis']}

**Australian Guidelines:**
{patient_scenario.get('australian_guidelines_url', 'N/A')}

**Student's SOAP Note:**

**Subjective (S):**
{soap_note['subjective']}

**Objective (O):**
{soap_note['objective']}

**Assessment (A):**
{soap_note['assessment']}

**Plan (P):**
{soap_note['plan']}

---

**Evaluation Criteria:**

1. **Structure Completeness**: All 4 SOAP sections present with ≥50 characters each
2. **Clinical Accuracy**: Diagnosis matches patient presentation, appropriate management
3. **Australian Terminology**: Uses Australian medical terms (paracetamol not acetaminophen, etc.)
4. **Red Flags**: Identifies and addresses serious symptoms requiring urgent action
5. **Safety Netting**: Includes clear follow-up plan and patient advice
6. **AHPRA Compliance**: Professional, ethical, patient-centered documentation

**Please provide:**
- Overall score (0-100)
- Section-specific feedback (2-3 points per section)
- Red flags identified (if any)
- Australian terminology compliance (%)
- AHPRA compliance (yes/no with reasons)
- Clinical accuracy score (0-100)

Return response in JSON format.
"""

        response = await self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse Claude's response into structured validation result
        validation_result = self._parse_validation_response(response.content[0].text)

        return validation_result

    def _parse_validation_response(self, claude_response: str) -> Dict[str, any]:
        """Parse Claude's JSON response into validation result."""
        # Implementation: Extract JSON from response, validate structure
        pass

    def _load_australian_guidelines(self) -> Dict[str, str]:
        """Load Australian clinical guidelines from Qdrant RAG system."""
        # Implementation: Query Qdrant for relevant Australian guidelines
        pass
```

**API Endpoint** (`backend/src/api/v1/emr_validation.py`):
```python
@router.post("/validate/soap-note", response_model=SOAPNoteValidationResponse)
async def validate_soap_note(
    soap_note: SOAPNoteValidationRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
    validator: SOAPNoteValidator = Depends(get_soap_validator)
):
    """
    Validate SOAP note against Australian clinical standards.

    Returns AI-powered feedback with:
    - Overall score (0-100)
    - Section-specific feedback
    - AHPRA compliance check
    - Clinical accuracy assessment
    - Australian terminology compliance
    """
    # Get patient scenario
    patient = db.query(PatientScenario).filter_by(id=soap_note.patient_scenario_id).first()

    # Run AI validation
    validation_result = await validator.validate_soap_note(
        soap_note=soap_note.dict(),
        patient_scenario=patient.dict()
    )

    # Save validation result to database
    # ...

    return validation_result
```

#### Week 10: Prescription & Pathology Validation
**Services to Build**:
- [ ] `PrescriptionValidator` - PBS compliance, dose checking, drug interactions
- [ ] `PathologyValidator` - MBS compliance, indication appropriateness
- [ ] RAG integration with Australian drug database (PBS) and test database (MBS)

**Success Criteria**:
- [ ] SOAP note validation accuracy 90%+ vs. human educator
- [ ] Validation response time <3 seconds
- [ ] Australian terminology detection 95%+ accurate
- [ ] PBS/MBS compliance checks functional
- [ ] All validation services have 80%+ test coverage

---

### Phase 5: OSCE Integration (Week 11)
**Duration**: 1 week (May 10-16)
**Goal**: Integrate EMR system with existing OSCE stations

#### OSCE Integration Architecture
```typescript
// frontend/src/pages/OSCEStationWithEMR.tsx
import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { CernerLayout } from '../components/emr/cerner/CernerLayout';
import { EpicLayout } from '../components/emr/epic/EpicLayout';
import { OSCETimer } from '../components/osce/OSCETimer';
import { OSCEInstructions } from '../components/osce/OSCEInstructions';

export const OSCEStationWithEMR = () => {
  const { osceId } = useParams();
  const [osceData, setOsceData] = useState(null);
  const [emrSession, setEMRSession] = useState(null);
  const [timeRemaining, setTimeRemaining] = useState(0);

  useEffect(() => {
    // Fetch OSCE station data
    fetchOSCEData(osceId).then((data) => {
      setOsceData(data);

      // Check if OSCE requires EMR documentation
      if (data.osce_emr_integration?.requires_emr) {
        // Start EMR session automatically
        startEMRSession({
          emr_system: data.osce_emr_integration.emr_system,
          patient_scenario_id: data.osce_emr_integration.patient_scenario_id,
          osce_id: osceId,
        }).then(setEMRSession);

        // Set documentation time limit
        setTimeRemaining(data.osce_emr_integration.documentation_time_limit_minutes * 60);
      }
    });
  }, [osceId]);

  if (!osceData) return <div>Loading OSCE station...</div>;

  const EMRComponent = osceData.osce_emr_integration.emr_system === 'cerner' ? CernerLayout : EpicLayout;

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh' }}>
      {/* OSCE Instructions Banner */}
      <OSCEInstructions
        stationTitle={osceData.station_title}
        instructions={osceData.instructions}
        requiredDocumentation={osceData.osce_emr_integration}
      />

      {/* Timer */}
      <OSCETimer
        initialTime={timeRemaining}
        onTimeUp={() => alert('Time is up! Submitting documentation...')}
      />

      {/* EMR Interface */}
      <EMRComponent>
        {/* EMR content based on required documentation */}
        {osceData.osce_emr_integration.requires_soap_note && <SOAPNoteEditor sessionId={emrSession.id} />}
        {osceData.osce_emr_integration.requires_prescription && <PrescriptionWriter sessionId={emrSession.id} />}
        {osceData.osce_emr_integration.requires_pathology && <PathologyOrderEntry sessionId={emrSession.id} />}
      </EMRComponent>
    </Box>
  );
};
```

**Backend Integration**:
- [ ] Update OSCE schema to include `osce_emr_integration` table
- [ ] API endpoint to link OSCEs with patient scenarios
- [ ] Scoring algorithm: Combine OSCE performance + EMR documentation quality

**Success Criteria**:
- [ ] OSCE stations can require EMR documentation (configurable)
- [ ] EMR session auto-starts when student begins OSCE
- [ ] Documentation timer enforces time limits
- [ ] OSCE score incorporates EMR documentation quality (weighted)
- [ ] Existing 65 OSCE video tests still pass (no regressions)

---

### Phase 6: Testing, Documentation, Polish (Week 12)
**Duration**: 1 week (May 17-23)
**Goal**: Comprehensive testing, documentation, deployment readiness

#### Testing Deliverables
- [ ] **Frontend Tests**: 200+ component tests (80%+ coverage)
  - Cerner components: 80 tests
  - Epic components: 80 tests
  - Shared EMR components: 40 tests
- [ ] **Backend Tests**: 150+ API tests (80%+ coverage)
  - EMR session management: 30 tests
  - SOAP note CRUD: 25 tests
  - Prescription CRUD: 25 tests
  - Pathology CRUD: 20 tests
  - AI validation: 30 tests
  - OSCE integration: 20 tests
- [ ] **Integration Tests**: 50+ Playwright E2E tests
  - Complete Cerner workflow: 15 tests
  - Complete Epic workflow: 15 tests
  - OSCE + EMR integration: 10 tests
  - Validation feedback: 10 tests
- [ ] **Performance Tests**: Load testing for 1,000 concurrent users

#### Documentation Deliverables
- [ ] **API Documentation**: OpenAPI/Swagger complete
- [ ] **User Guide**: How to use EMR practice system (students)
- [ ] **Educator Guide**: How to configure OSCE + EMR integration
- [ ] **Architecture Documentation**: System design, database schema, AI validation approach
- [ ] **Deployment Guide**: Production deployment checklist

#### Polish Deliverables
- [ ] **Accessibility**: WCAG 2.2 AA compliance (keyboard navigation, screen reader support)
- [ ] **Responsive Design**: Works on desktop (1920x1080), tablet (1024x768), mobile (375x667)
- [ ] **Error Handling**: User-friendly error messages, retry logic
- [ ] **Performance**: <200ms p95 response time, <3s page load

**Success Criteria**:
- [ ] 100% test pass rate (zero flaky tests)
- [ ] 80%+ test coverage (frontend + backend)
- [ ] All documentation complete and reviewed
- [ ] Accessibility audit passing (Lighthouse score 90+)
- [ ] Performance benchmarks met (p95 <200ms)

---

## Technology Stack

### Frontend
```json
{
  "react": "^18.2.0",
  "@mui/material": "^5.15.0",
  "@mui/icons-material": "^5.15.0",
  "react-router-dom": "^6.20.0",
  "axios": "^1.6.0",
  "react-query": "^3.39.3",
  "typescript": "^5.3.3",
  "vite": "^5.0.10",

  // Testing
  "@testing-library/react": "^14.1.2",
  "vitest": "^1.1.0",
  "playwright": "^1.48.0"
}
```

### Backend
```python
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
alembic==1.13.1
psycopg2-binary==2.9.9

# Authentication (reuse existing)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# AI Validation
anthropic==0.18.1

# Database
redis==5.0.1

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
```

---

## Resource Allocation

### Development Team (Recommended)
- **Frontend Lead**: Cerner + Epic UI (1 developer, 8 weeks)
- **Backend Lead**: API + Database (1 developer, 6 weeks)
- **AI/ML Engineer**: Validation service (1 developer, 2 weeks)
- **QA Engineer**: Testing (1 tester, 3 weeks)
- **Clinical Consultant**: Australian guidelines validation (part-time)

### Infrastructure
- **Hosting**: AWS or Azure (Australian region for data residency)
- **Database**: PostgreSQL 16 (managed service)
- **Caching**: Redis 7
- **AI**: Anthropic Claude API (existing account)
- **Monitoring**: Prometheus + Grafana

### Budget Estimate (World-Class Quality)
- **Development**: 12 weeks × 3 developers = 36 dev-weeks
- **QA**: 3 weeks × 1 tester = 3 test-weeks
- **Infrastructure**: $500/month (development) → $2,000/month (production for 10k users)
- **Claude API**: ~$1,000/month for validation (estimate 10k validations/month)

---

## Success Metrics (World-Class Standards)

### Launch Criteria (May 23, 2026)
- [ ] Both Cerner and Epic UIs complete and tested
- [ ] 200+ patient scenarios loaded
- [ ] AI validation accuracy ≥90% vs. human educators
- [ ] 100% test pass rate with ≥80% coverage
- [ ] OSCE integration functional for all 4 OSCE types
- [ ] Performance: <200ms p95, 99.9% uptime
- [ ] Documentation: 100% complete (API docs, user guides, architecture)
- [ ] Security: HIPAA-compliant audit logs, PHI encryption
- [ ] Accessibility: WCAG 2.2 AA compliant

### 6-Month Post-Launch Metrics
- **Adoption**: 80%+ of AMC Clinical Exam students use EMR practice at least weekly
- **Improvement**: Users show 50%+ faster SOAP note completion after 30 sessions
- **Quality**: 95%+ AHPRA compliance rate in student documentation
- **Satisfaction**: Net Promoter Score (NPS) ≥70
- **OSCE Performance**: Students using EMR practice score 20%+ higher on OSCE documentation stations

---

## Risk Mitigation

### Technical Risks
1. **AI Validation Accuracy**: Mitigate with human-in-the-loop review for first 1,000 validations
2. **Performance at Scale**: Load testing for 10k concurrent users before launch
3. **Browser Compatibility**: Test on Chrome, Firefox, Safari, Edge
4. **Database Performance**: Index optimization, query profiling

### Clinical Risks
1. **Incorrect Medical Advice**: Disclaimer that system is for practice only, not real patient care
2. **Australian Guidelines Accuracy**: Clinical consultant review all patient scenarios
3. **AHPRA Compliance**: Legal review of documentation standards

### Schedule Risks
1. **12-week timeline aggressive**: Build MVP first (Cerner + basic validation), Epic later if needed
2. **AI validation complexity**: Fallback to rule-based validation if AI accuracy <80%

---

## Next Steps

### Immediate Actions (Week 1 - Starting March 1)
1. **Update PRD files** to replace ICRP with AMC Clinical Examination
2. **Create database schema** (Alembic migrations)
3. **Set up frontend project** structure (emr/ folder with cerner/ and epic/ subfolders)
4. **Implement authentication integration** (reuse existing auth system)
5. **Create first 10 patient scenarios** with Australian guidelines links

### Developer Onboarding
1. Read this implementation plan
2. Review existing PRD files (00-04 in `/prd` folder)
3. Set up local development environment (PostgreSQL, Redis, frontend, backend)
4. Run existing test suite to ensure no regressions
5. Start with Phase 1 Week 1 tasks (database schema)

---

## Appendix

### Australian Medical Resources
- **AMC Clinical Examination**: https://www.amc.org.au/assessment/clinical-examination/
- **AHPRA Standards**: https://www.ahpra.gov.au/
- **PBS (Pharmaceutical Benefits Scheme)**: https://www.pbs.gov.au/
- **MBS (Medicare Benefits Schedule)**: http://www.mbsonline.gov.au/
- **NSW Health EMR Standards**: https://www.health.nsw.gov.au/

### Related Documents
- **Backend Features Plan**: `/home/dev/Development/irStudy/backend-features-15-feb/WORLD_CLASS_BACKEND_PLAN.md`
- **Backend Handover**: `/home/dev/Development/irStudy/backend-features-15-feb/HANDOVER.md`
- **Test Plan**: `/home/dev/Development/irStudy/testing/playwright/COMPREHENSIVE_TEST_IMPLEMENTATION_PLAN.md`
- **PRD Files**: `/home/dev/Development/irStudy/emr-practice-system/prd/`

---

**END OF IMPLEMENTATION PLAN**

**Status**: Ready for development (0% → 100% in 12 weeks)
**Next Review**: March 1, 2026 (start of Week 1)
**Contact**: Project Manager (use AskUserQuestion for clarifications)
