# Epic EHR Practice System - Database Migration Plan

**Document Version**: 1.0
**Date**: 2026-02-15
**Status**: Ready for Implementation

---

## Executive Summary

This document specifies the database schema extensions required for the Epic EHR Practice System. The migration adds **6 new tables** and **extends 1 existing table** (user_progress) to support EMR session management, documentation tracking, and AI validation.

**Migration Strategy**: Alembic migration with zero downtime (additive changes only).

---

## 1. Current Database State

### 1.1 Existing Schema (Relevant Tables)

```sql
-- irstudy_medical database (PostgreSQL 14, port 5433)

-- Users (authentication & roles)
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role VARCHAR(20) NOT NULL,  -- student, educator, admin
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    failed_login_attempts INTEGER DEFAULT 0,
    account_locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- OSCEs (221 scenarios, source for EMR patient cases)
CREATE TABLE osces (
    id SERIAL PRIMARY KEY,
    station_title VARCHAR(200) NOT NULL,
    patient_instructions TEXT NOT NULL,  -- Simulated patient scenario
    candidate_instructions TEXT NOT NULL,
    specialty VARCHAR(50) NOT NULL,  -- cardiology, respiratory, etc.
    difficulty VARCHAR(20),  -- easy, medium, hard
    time_limit_minutes INTEGER DEFAULT 8,
    rubric JSON NOT NULL,  -- AMC 15-mark criteria
    learning_objectives JSON,
    video_resources JSON,  -- Educational videos
    australian_guidelines JSON,  -- eTG, NSW Health references
    tags JSON,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- User Progress (tracks MCQ/OSCE performance, needs EMR extension)
CREATE TABLE user_progress (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id),
    total_mcqs_attempted INTEGER DEFAULT 0,
    total_osces_practiced INTEGER DEFAULT 0,
    correct_mcqs INTEGER DEFAULT 0,

    -- Specialty-specific tracking (10 medical specialties)
    cardiology_mcqs INTEGER DEFAULT 0,
    respiratory_mcqs INTEGER DEFAULT 0,
    gastroenterology_mcqs INTEGER DEFAULT 0,
    neurology_mcqs INTEGER DEFAULT 0,
    endocrinology_mcqs INTEGER DEFAULT 0,
    rheumatology_mcqs INTEGER DEFAULT 0,
    haematology_mcqs INTEGER DEFAULT 0,
    renal_mcqs INTEGER DEFAULT 0,
    infectious_diseases_mcqs INTEGER DEFAULT 0,
    emergency_medicine_mcqs INTEGER DEFAULT 0,

    cardiology_osces INTEGER DEFAULT 0,
    respiratory_osces INTEGER DEFAULT 0,
    -- ... (similar for other specialties)

    total_study_time_minutes INTEGER DEFAULT 0,
    last_study_date DATE,
    current_streak_days INTEGER DEFAULT 0,
    longest_streak_days INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Enums (existing)
CREATE TYPE user_role AS ENUM ('student', 'educator', 'admin');
CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard');
CREATE TYPE medical_specialty AS ENUM (
    'cardiology', 'respiratory', 'gastroenterology', 'neurology',
    'endocrinology', 'rheumatology', 'haematology', 'renal',
    'infectious_diseases', 'emergency_medicine'
);
```

### 1.2 Existing Indexes

```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_osces_specialty ON osces(specialty);
CREATE INDEX idx_osces_difficulty ON osces(difficulty);
CREATE INDEX idx_user_progress_user_id ON user_progress(user_id);
```

---

## 2. New Schema Requirements

### 2.1 Overview of New Tables

| Table | Purpose | Row Estimate (1 year) |
|-------|---------|------------------------|
| `mock_patients` | Simulated patient database (from OSCEs) | 500+ cases |
| `emr_sessions` | EMR practice sessions | 50,000+ sessions (100 users × 500 sessions) |
| `emr_soap_notes` | SOAP note documentation drafts | 50,000+ notes (1 per session) |
| `emr_prescriptions` | Medication orders | 100,000+ prescriptions (~2 per session) |
| `emr_pathology_orders` | Lab test requests | 75,000+ orders (~1.5 per session) |
| `emr_validation_results` | AI validation feedback | 150,000+ results (~3 per session: SOAP, Rx, Path) |

**Total New Storage**: ~5-10 GB (1 year, 100 active users)

---

## 3. Detailed Table Specifications

### 3.1 Table: `mock_patients`

**Purpose**: Simulated patient database converted from OSCE scenarios.

```sql
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mrn VARCHAR(20) UNIQUE NOT NULL,  -- Medical Record Number (e.g., "MRN12345678")
    medicare_number VARCHAR(11),  -- Format: "2912 34567 1" (10 digits + 1 check digit)

    -- Demographics
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 100),
    gender VARCHAR(20) NOT NULL,  -- male, female, non-binary, prefer-not-to-say
    aboriginal_tsi_status VARCHAR(50),  -- Aboriginal, Torres Strait Islander, Both, Neither, Prefer not to say

    demographics JSON NOT NULL,
    -- {
    --   "address": "12 King St, Sydney NSW 2000",
    --   "phone": "0412 345 678",
    --   "email": "patient@example.com",
    --   "emergency_contact": {
    --     "name": "Jane Smith",
    --     "relationship": "Wife",
    --     "phone": "0423 456 789"
    --   },
    --   "gp_details": {
    --     "name": "Dr. John Doe",
    --     "clinic": "Sydney Medical Centre",
    --     "phone": "(02) 9876 5432"
    --   },
    --   "preferred_language": "English",
    --   "interpreter_required": false
    -- }

    -- Clinical Information
    presenting_complaint TEXT NOT NULL,  -- Chief complaint (e.g., "Central chest pain")

    medical_history JSON,
    -- {
    --   "pmhx": ["Hypertension (diagnosed 2018)", "Type 2 Diabetes (2020)"],
    --   "pshx": ["Appendectomy (2010)"],
    --   "fhx": ["Father - MI age 55", "Mother - Breast cancer"],
    --   "shx": {
    --     "smoking": "30 pack-years, quit 2023",
    --     "alcohol": "10 standard drinks/week",
    --     "occupation": "Accountant",
    --     "living_situation": "Lives with spouse"
    --   }
    -- }

    medications JSON,
    -- [
    --   {
    --     "name": "Amlodipine",
    --     "dose": "5mg",
    --     "frequency": "daily",
    --     "route": "PO",
    --     "indication": "Hypertension"
    --   },
    --   {
    --     "name": "Metformin",
    --     "dose": "500mg",
    --     "frequency": "BD",
    --     "route": "PO",
    --     "indication": "Type 2 Diabetes"
    --   }
    -- ]

    allergies JSON,
    -- [
    --   {
    --     "allergen": "Penicillin",
    --     "reaction": "Rash",
    --     "severity": "mild"
    --   }
    -- ]
    -- Or: ["NKDA"] if no known drug allergies

    vital_signs JSON,
    -- {
    --   "hr": 95,  -- beats per minute
    --   "bp_systolic": 155,
    --   "bp_diastolic": 92,
    --   "rr": 20,  -- breaths per minute
    --   "spo2": 96,  -- %
    --   "temp": 36.8,  -- °C
    --   "weight": 85,  -- kg
    --   "height": 175,  -- cm
    --   "bmi": 27.8,
    --   "gcs": 15,
    --   "pain_score": 7  -- 0-10
    -- }

    physical_exam_findings JSON,
    -- {
    --   "general": "Alert, distressed, sweating",
    --   "cardiovascular": "Regular rhythm, no murmurs, normal S1/S2",
    --   "respiratory": "Equal air entry, no crackles/wheeze",
    --   "abdominal": "Soft, non-tender, bowel sounds present",
    --   "neurological": "Cranial nerves intact, normal power/sensation",
    --   "skin": "No rashes or lesions"
    -- }

    investigation_results JSON,
    -- {
    --   "ecg": {
    --     "findings": "ST elevation 2mm in leads II, III, aVF",
    --     "interpretation": "Inferior STEMI"
    --   },
    --   "labs": {
    --     "troponin_i": {"value": 1.2, "unit": "ng/mL", "reference": "<0.04", "flag": "HIGH"},
    --     "fbc": {
    --       "hb": {"value": 145, "unit": "g/L", "reference": "130-180"},
    --       "wcc": {"value": 9.2, "unit": "x10^9/L", "reference": "4-11"},
    --       "platelets": {"value": 250, "unit": "x10^9/L", "reference": "150-400"}
    --     },
    --     "uec": {
    --       "sodium": {"value": 138, "unit": "mmol/L", "reference": "135-145"},
    --       "potassium": {"value": 4.2, "unit": "mmol/L", "reference": "3.5-5.0"},
    --       "creatinine": {"value": 85, "unit": "µmol/L", "reference": "60-110"}
    --     },
    --     "bsl": {"value": 8.2, "unit": "mmol/L", "reference": "4-7", "flag": "MILDLY HIGH"}
    --   },
    --   "imaging": {
    --     "cxr": "Normal cardiac silhouette, clear lung fields"
    --   }
    -- }

    -- Source and Classification
    source_osce_id INTEGER REFERENCES osces(id),  -- NULL if manually created
    specialty VARCHAR(50) NOT NULL,  -- Medical specialty
    difficulty VARCHAR(20) NOT NULL,  -- easy, medium, hard

    -- Validation Criteria (from OSCE rubric)
    validation_criteria JSON,
    -- {
    --   "expected_diagnosis": ["Acute Coronary Syndrome", "STEMI"],
    --   "key_history_points": [
    --     "SOCRATES pain assessment",
    --     "Cardiovascular risk factors",
    --     "Red flags (radiation, diaphoresis, nausea)"
    --   ],
    --   "expected_investigations": ["ECG", "Troponin", "FBC", "UEC"],
    --   "expected_management": [
    --     "Call 000 / Cardiology consult",
    --     "Aspirin 300mg STAT",
    --     "Clopidogrel 300mg STAT",
    --     "Morphine for pain",
    --     "Oxygen if SpO2 <94%",
    --     "Arrange urgent angiography"
    --   ],
    --   "red_flags": [
    --     "STEMI criteria - activate cath lab",
    --     "High troponin - ACS confirmed"
    --   ]
    -- }

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP  -- Soft delete for compliance
);

-- Indexes for performance
CREATE INDEX idx_mock_patients_specialty ON mock_patients(specialty);
CREATE INDEX idx_mock_patients_difficulty ON mock_patients(difficulty);
CREATE INDEX idx_mock_patients_source_osce ON mock_patients(source_osce_id);
CREATE INDEX idx_mock_patients_mrn ON mock_patients(mrn);

-- Comments
COMMENT ON TABLE mock_patients IS 'Simulated patient database for EMR practice (converted from OSCE scenarios)';
COMMENT ON COLUMN mock_patients.medicare_number IS 'Australian Medicare number (10 digits + check digit)';
COMMENT ON COLUMN mock_patients.aboriginal_tsi_status IS 'Mandatory field per NSW Health EMR standards';
```

---

### 3.2 Table: `emr_sessions`

**Purpose**: Tracks individual EMR practice sessions.

```sql
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_id UUID NOT NULL REFERENCES mock_patients(id) ON DELETE CASCADE,

    -- Session Metadata
    specialty VARCHAR(50) NOT NULL,  -- Inherited from patient
    difficulty VARCHAR(20) NOT NULL,  -- Inherited from patient
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    submitted_at TIMESTAMP,  -- NULL if in progress
    elapsed_time_seconds INTEGER,  -- Total time spent in session

    -- Scoring (AMC 15-mark rubric)
    validation_score FLOAT CHECK (validation_score >= 0 AND validation_score <= 15),
    -- Breakdown:
    -- - History/Examination: 0-3
    -- - Clinical Reasoning: 0-3
    -- - Communication: 0-3
    -- - Patient Safety: 0-3
    -- - Professionalism: 0-3
    -- Pass mark: 9/15 (60%)

    score_breakdown JSON,
    -- {
    --   "history_examination": 2.5,
    --   "clinical_reasoning": 3.0,
    --   "communication": 2.0,
    --   "patient_safety": 2.5,
    --   "professionalism": 2.5,
    --   "total": 12.5
    -- }

    -- Session Status
    status VARCHAR(20) NOT NULL DEFAULT 'in_progress',
    -- Options: in_progress, submitted, graded, cancelled

    -- Performance Metrics
    typing_metrics JSON,
    -- {
    --   "total_words": 450,
    --   "average_wpm": 35,
    --   "total_typing_time_seconds": 770,
    --   "backspace_count": 42,
    --   "accuracy": 0.92
    -- }

    auto_save_count INTEGER DEFAULT 0,
    last_auto_save_at TIMESTAMP,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    deleted_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_emr_sessions_user_id ON emr_sessions(user_id);
CREATE INDEX idx_emr_sessions_patient_id ON emr_sessions(patient_id);
CREATE INDEX idx_emr_sessions_started_at ON emr_sessions(started_at DESC);  -- For recent sessions query
CREATE INDEX idx_emr_sessions_specialty ON emr_sessions(specialty);
CREATE INDEX idx_emr_sessions_status ON emr_sessions(status);
CREATE INDEX idx_emr_sessions_user_specialty ON emr_sessions(user_id, specialty);  -- Composite for analytics

-- Comments
COMMENT ON TABLE emr_sessions IS 'EMR practice sessions (Epic EHR simulation)';
COMMENT ON COLUMN emr_sessions.validation_score IS 'Overall score 0-15 (AMC rubric), pass mark 9/15';
COMMENT ON COLUMN emr_sessions.status IS 'in_progress, submitted, graded, cancelled';
```

---

### 3.3 Table: `emr_soap_notes`

**Purpose**: Stores SOAP note documentation drafts and final submissions.

```sql
CREATE TABLE emr_soap_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,

    -- SOAP Note Content
    subjective TEXT,  -- History of Presenting Illness (HPI), Review of Systems (ROS)
    objective TEXT,   -- Vital signs, physical examination findings
    assessment TEXT,  -- Diagnosis, differential diagnosis
    plan TEXT,        -- Management plan, investigations, follow-up

    -- Structured Data (for validation)
    soap_note_data JSON,
    -- {
    --   "subjective": {
    --     "hpi": "58M with 2-hour history of central crushing chest pain 7/10...",
    --     "ros": {
    --       "cardiovascular": "Pain radiates to left arm, associated with sweating and nausea",
    --       "respiratory": "No dyspnea at rest",
    --       "gastrointestinal": "Denies vomiting, no epigastric pain"
    --     },
    --     "pmhx": ["Hypertension", "Type 2 Diabetes"],
    --     "medications": ["Amlodipine 5mg daily", "Metformin 500mg BD"],
    --     "allergies": ["Penicillin (rash)"],
    --     "fhx": "Father had MI age 55",
    --     "shx": "30 pack-year smoking history, quit 2023"
    --   },
    --   "objective": {
    --     "vitals": {
    --       "hr": 95, "bp": "155/92", "rr": 20, "spo2": 96, "temp": 36.8, "pain": 7
    --     },
    --     "general": "Alert, distressed, diaphoretic",
    --     "cardiovascular": "Regular rhythm, no murmurs",
    --     "respiratory": "Clear lung fields bilaterally",
    --     "abdominal": "Soft, non-tender"
    --   },
    --   "assessment": {
    --     "primary_diagnosis": "Acute Coronary Syndrome - Inferior STEMI",
    --     "differential": ["STEMI", "NSTEMI", "Unstable angina", "PE", "Aortic dissection"],
    --     "severity": "High risk - STEMI criteria met"
    --   },
    --   "plan": {
    --     "immediate": [
    --       "Call 000 / Activate cath lab",
    --       "Aspirin 300mg STAT PO",
    --       "Clopidogrel 300mg STAT PO",
    --       "Morphine 2.5mg IV for pain",
    --       "Oxygen if SpO2 <94%"
    --     ],
    --     "investigations": ["Serial ECG", "Repeat troponin in 3h", "CXR"],
    --     "referrals": ["URGENT Cardiology consult"],
    --     "follow_up": "Admit to CCU, arrange urgent angiography"
    --   }
    -- }

    -- Metrics
    word_count INTEGER,  -- Total words in SOAP note
    character_count INTEGER,  -- Total characters (for minimum validations)
    typing_wpm FLOAT,  -- Words per minute (average typing speed)

    -- Auto-save Tracking
    is_final_submission BOOLEAN DEFAULT FALSE,  -- TRUE when session submitted
    auto_saved_at TIMESTAMP,
    version INTEGER DEFAULT 1,  -- Increment on each auto-save

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_emr_soap_notes_session_id ON emr_soap_notes(session_id);
CREATE INDEX idx_emr_soap_notes_final ON emr_soap_notes(is_final_submission);

-- Comments
COMMENT ON TABLE emr_soap_notes IS 'SOAP note documentation for EMR sessions';
COMMENT ON COLUMN emr_soap_notes.soap_note_data IS 'Structured JSON for AI validation';
COMMENT ON COLUMN emr_soap_notes.version IS 'Increments on auto-save (v1, v2, v3...)';
```

---

### 3.4 Table: `emr_prescriptions`

**Purpose**: Stores medication orders within EMR sessions.

```sql
CREATE TABLE emr_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,

    -- Prescription Details (Australian Format)
    medication_name VARCHAR(200) NOT NULL,  -- MUST use Australian names (paracetamol not acetaminophen)
    dose VARCHAR(50) NOT NULL,  -- e.g., "5mg", "500mg", "1 tablet"
    frequency VARCHAR(50) NOT NULL,  -- daily, BD, TDS, QID, PRN, weekly, etc.
    route VARCHAR(20) NOT NULL,  -- PO, IV, IM, SC, PR, topical, inhaled, etc.
    repeats INTEGER NOT NULL CHECK (repeats >= 0 AND repeats <= 5),  -- Max 5 repeats (PBS rule)
    indication TEXT,  -- Clinical indication for prescription

    -- PBS (Pharmaceutical Benefits Scheme) Validation
    pbs_listed BOOLEAN,  -- TRUE if drug is on PBS
    pbs_item_code VARCHAR(10),  -- PBS item number (if applicable)
    authority_required BOOLEAN,  -- TRUE if requires PBS authority approval

    -- Validation Results
    validation_errors JSON,
    -- [
    --   {
    --     "type": "error",
    --     "field": "dose",
    --     "message": "Dose exceeds maximum (max 10mg daily)"
    --   },
    --   {
    --     "type": "warning",
    --     "field": "repeats",
    --     "message": "Max 5 repeats for Schedule 4 drugs"
    --   }
    -- ]

    is_valid BOOLEAN DEFAULT NULL,  -- NULL = not validated, TRUE/FALSE = validated

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_emr_prescriptions_session_id ON emr_prescriptions(session_id);
CREATE INDEX idx_emr_prescriptions_medication ON emr_prescriptions(medication_name);

-- Comments
COMMENT ON TABLE emr_prescriptions IS 'Medication orders in EMR sessions (PBS compliant)';
COMMENT ON COLUMN emr_prescriptions.medication_name IS 'MUST use Australian terminology (paracetamol not acetaminophen)';
COMMENT ON COLUMN emr_prescriptions.repeats IS 'Max 5 repeats per PBS rules';
COMMENT ON COLUMN emr_prescriptions.authority_required IS 'Some PBS drugs require authority approval';
```

---

### 3.5 Table: `emr_pathology_orders`

**Purpose**: Stores laboratory test requests within EMR sessions.

```sql
CREATE TABLE emr_pathology_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,

    -- Pathology Test Details
    test_name VARCHAR(200) NOT NULL,  -- e.g., "Full Blood Count", "Troponin I", "Lipid Panel"
    test_category VARCHAR(50),  -- Haematology, Biochemistry, Microbiology, Immunology, etc.
    mbs_item_number VARCHAR(10),  -- Medicare Benefits Schedule item number (e.g., "66512" for FBC)

    -- Clinical Context
    urgency VARCHAR(20) NOT NULL DEFAULT 'routine',  -- routine, urgent, emergency
    -- routine: 24-48h, urgent: 4-6h, emergency: <1h

    indication TEXT,  -- Clinical indication for test

    -- Validation
    appropriate BOOLEAN DEFAULT NULL,  -- NULL = not validated, TRUE/FALSE = AI assessment
    validation_feedback JSON,
    -- {
    --   "appropriateness": "appropriate",  -- appropriate, inappropriate, questionable
    --   "reasoning": "Troponin indicated for suspected ACS (chest pain + ECG changes)",
    --   "etg_alignment": "Follows eTG Cardiovascular guidelines",
    --   "cost_effectiveness": "High-value test for this presentation",
    --   "alternatives": [],
    --   "red_flags": ["Serial troponins required (0h, 3h) for ACS rule-out"]
    -- }

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_emr_pathology_orders_session_id ON emr_pathology_orders(session_id);
CREATE INDEX idx_emr_pathology_orders_urgency ON emr_pathology_orders(urgency);
CREATE INDEX idx_emr_pathology_orders_test_name ON emr_pathology_orders(test_name);

-- Comments
COMMENT ON TABLE emr_pathology_orders IS 'Laboratory test requests in EMR sessions (MBS compliant)';
COMMENT ON COLUMN emr_pathology_orders.mbs_item_number IS 'Medicare Benefits Schedule item number';
COMMENT ON COLUMN emr_pathology_orders.urgency IS 'routine (24-48h), urgent (4-6h), emergency (<1h)';
```

---

### 3.6 Table: `emr_validation_results`

**Purpose**: Stores AI validation feedback from 3-layer validation system.

```sql
CREATE TABLE emr_validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,

    -- Validation Type
    validation_type VARCHAR(50) NOT NULL,  -- soap_note, prescription, pathology

    -- Layer 1: Zod (Client-side TypeScript validation)
    layer_1_zod JSON,
    -- {
    --   "passed": false,
    --   "errors": [
    --     {
    --       "field": "subjective",
    --       "message": "HPI too short (30/50 characters minimum)",
    --       "severity": "error"
    --     }
    --   ],
    --   "latency_ms": 25
    -- }

    -- Layer 2: Python (Server-side PBS/MBS compliance)
    layer_2_python JSON,
    -- {
    --   "passed": true,
    --   "warnings": [
    --     {
    --       "field": "prescriptions[0].repeats",
    --       "message": "Max 5 repeats for Schedule 4 drugs (you entered 3 - OK)",
    --       "severity": "warning"
    --     }
    --   ],
    --   "pbs_compliance": "compliant",
    --   "mbs_compliance": "compliant",
    --   "australian_terminology": "correct",
    --   "latency_ms": 850
    -- }

    -- Layer 3: Claude AI (Clinical reasoning validation)
    layer_3_ai JSON,
    -- {
    --   "overall_score": 12.5,  -- 0-15 (AMC rubric)
    --   "category_scores": {
    --     "history_examination": 3.0,
    --     "clinical_reasoning": 2.5,
    --     "communication": 3.0,
    --     "patient_safety": 2.0,
    --     "professionalism": 2.0
    --   },
    --   "strengths": [
    --     "Excellent SOCRATES pain assessment",
    --     "Appropriate differential diagnosis (ACS, PE, gastritis)",
    --     "Safety netting with red flag advice"
    --   ],
    --   "improvements": [
    --     "Consider asking about radiation to jaw/neck",
    --     "Add cardiovascular risk factors to assessment"
    --   ],
    --   "red_flags": [
    --     "STEMI criteria met - URGENT cardiology referral needed",
    --     "Patient requires immediate cath lab activation"
    --   ],
    --   "australian_compliance": {
    --     "terminology": "✓ Correct (paracetamol not acetaminophen)",
    --     "emergency_number": "✓ Mentioned 000 for worsening symptoms",
    --     "etg_alignment": "✓ Follows eTG Cardiovascular guidelines"
    --   },
    --   "latency_ms": 3420,
    --   "model": "claude-sonnet-4-5-20250929",
    --   "tokens_used": 1850
    -- }

    -- Overall Validation Summary
    overall_score FLOAT CHECK (overall_score >= 0 AND overall_score <= 15),
    passed BOOLEAN,  -- TRUE if score >= 9/15 (60% pass mark)

    -- Extracted Feedback (for UI display)
    strengths TEXT[],  -- Array of strength points
    improvements TEXT[],  -- Array of improvement suggestions
    red_flags TEXT[],  -- Array of critical safety issues

    -- Metadata
    validated_at TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_emr_validation_results_session_id ON emr_validation_results(session_id);
CREATE INDEX idx_emr_validation_results_type ON emr_validation_results(validation_type);
CREATE INDEX idx_emr_validation_results_validated_at ON emr_validation_results(validated_at DESC);

-- Comments
COMMENT ON TABLE emr_validation_results IS '3-layer validation results (Zod, Python, Claude AI)';
COMMENT ON COLUMN emr_validation_results.layer_1_zod IS 'Client-side validation (<50ms)';
COMMENT ON COLUMN emr_validation_results.layer_2_python IS 'Server-side PBS/MBS compliance (<1s)';
COMMENT ON COLUMN emr_validation_results.layer_3_ai IS 'Claude AI clinical reasoning (3-5s)';
```

---

### 3.7 Extend Existing Table: `user_progress`

**Purpose**: Add EMR metrics to existing progress tracking.

```sql
-- Migration: Add new columns to user_progress table

ALTER TABLE user_progress
ADD COLUMN emr_sessions_completed INTEGER DEFAULT 0,
ADD COLUMN emr_soap_notes_written INTEGER DEFAULT 0,
ADD COLUMN emr_average_score FLOAT DEFAULT 0.0 CHECK (emr_average_score >= 0 AND emr_average_score <= 15),
ADD COLUMN emr_total_time_minutes INTEGER DEFAULT 0,

-- Specialty-specific EMR tracking (10 medical specialties)
ADD COLUMN emr_cardiology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_respiratory_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_gastroenterology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_neurology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_endocrinology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_rheumatology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_haematology_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_renal_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_infectious_diseases_sessions INTEGER DEFAULT 0,
ADD COLUMN emr_emergency_medicine_sessions INTEGER DEFAULT 0,

-- EMR Performance Metrics
ADD COLUMN emr_pass_rate FLOAT DEFAULT 0.0 CHECK (emr_pass_rate >= 0 AND emr_pass_rate <= 1),
-- Pass rate = (sessions with score ≥9/15) / total_sessions

ADD COLUMN emr_highest_score FLOAT DEFAULT 0.0 CHECK (emr_highest_score >= 0 AND emr_highest_score <= 15),
ADD COLUMN emr_last_session_date DATE;

-- Comments
COMMENT ON COLUMN user_progress.emr_sessions_completed IS 'Total EMR sessions submitted (not in-progress)';
COMMENT ON COLUMN user_progress.emr_soap_notes_written IS 'Total SOAP notes written (final submissions)';
COMMENT ON COLUMN user_progress.emr_average_score IS 'Average validation score (0-15, AMC rubric)';
COMMENT ON COLUMN user_progress.emr_pass_rate IS 'Percentage of sessions passing (score ≥9/15)';
```

---

## 4. Alembic Migration Script

### 4.1 Migration File: `2026_02_15_emr_tables.py`

```python
"""Add EMR practice system tables

Revision ID: emr_001
Revises: previous_revision_id
Create Date: 2026-02-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'emr_001'
down_revision = 'previous_revision_id'  # Replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    """Create EMR tables and extend user_progress."""

    # 1. Create mock_patients table
    op.create_table(
        'mock_patients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('mrn', sa.String(20), unique=True, nullable=False),
        sa.Column('medicare_number', sa.String(11), nullable=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('gender', sa.String(20), nullable=False),
        sa.Column('aboriginal_tsi_status', sa.String(50), nullable=True),
        sa.Column('demographics', postgresql.JSON, nullable=False),
        sa.Column('presenting_complaint', sa.Text, nullable=False),
        sa.Column('medical_history', postgresql.JSON, nullable=True),
        sa.Column('medications', postgresql.JSON, nullable=True),
        sa.Column('allergies', postgresql.JSON, nullable=True),
        sa.Column('vital_signs', postgresql.JSON, nullable=True),
        sa.Column('physical_exam_findings', postgresql.JSON, nullable=True),
        sa.Column('investigation_results', postgresql.JSON, nullable=True),
        sa.Column('source_osce_id', sa.Integer, sa.ForeignKey('osces.id'), nullable=True),
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('validation_criteria', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint('age >= 18 AND age <= 100', name='check_age_range')
    )

    # Indexes for mock_patients
    op.create_index('idx_mock_patients_specialty', 'mock_patients', ['specialty'])
    op.create_index('idx_mock_patients_difficulty', 'mock_patients', ['difficulty'])
    op.create_index('idx_mock_patients_source_osce', 'mock_patients', ['source_osce_id'])
    op.create_index('idx_mock_patients_mrn', 'mock_patients', ['mrn'])

    # 2. Create emr_sessions table
    op.create_table(
        'emr_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('patient_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('mock_patients.id', ondelete='CASCADE'), nullable=False),
        sa.Column('specialty', sa.String(50), nullable=False),
        sa.Column('difficulty', sa.String(20), nullable=False),
        sa.Column('started_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('NOW()')),
        sa.Column('submitted_at', sa.TIMESTAMP, nullable=True),
        sa.Column('elapsed_time_seconds', sa.Integer, nullable=True),
        sa.Column('validation_score', sa.Float, nullable=True),
        sa.Column('score_breakdown', postgresql.JSON, nullable=True),
        sa.Column('status', sa.String(20), nullable=False, server_default='in_progress'),
        sa.Column('typing_metrics', postgresql.JSON, nullable=True),
        sa.Column('auto_save_count', sa.Integer, default=0),
        sa.Column('last_auto_save_at', sa.TIMESTAMP, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.CheckConstraint('validation_score >= 0 AND validation_score <= 15', name='check_validation_score')
    )

    # Indexes for emr_sessions
    op.create_index('idx_emr_sessions_user_id', 'emr_sessions', ['user_id'])
    op.create_index('idx_emr_sessions_patient_id', 'emr_sessions', ['patient_id'])
    op.create_index('idx_emr_sessions_started_at', 'emr_sessions', [sa.text('started_at DESC')])
    op.create_index('idx_emr_sessions_specialty', 'emr_sessions', ['specialty'])
    op.create_index('idx_emr_sessions_status', 'emr_sessions', ['status'])
    op.create_index('idx_emr_sessions_user_specialty', 'emr_sessions', ['user_id', 'specialty'])

    # 3. Create emr_soap_notes table
    op.create_table(
        'emr_soap_notes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subjective', sa.Text, nullable=True),
        sa.Column('objective', sa.Text, nullable=True),
        sa.Column('assessment', sa.Text, nullable=True),
        sa.Column('plan', sa.Text, nullable=True),
        sa.Column('soap_note_data', postgresql.JSON, nullable=True),
        sa.Column('word_count', sa.Integer, nullable=True),
        sa.Column('character_count', sa.Integer, nullable=True),
        sa.Column('typing_wpm', sa.Float, nullable=True),
        sa.Column('is_final_submission', sa.Boolean, default=False),
        sa.Column('auto_saved_at', sa.TIMESTAMP, nullable=True),
        sa.Column('version', sa.Integer, default=1),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )

    # Indexes for emr_soap_notes
    op.create_index('idx_emr_soap_notes_session_id', 'emr_soap_notes', ['session_id'])
    op.create_index('idx_emr_soap_notes_final', 'emr_soap_notes', ['is_final_submission'])

    # 4. Create emr_prescriptions table
    op.create_table(
        'emr_prescriptions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('medication_name', sa.String(200), nullable=False),
        sa.Column('dose', sa.String(50), nullable=False),
        sa.Column('frequency', sa.String(50), nullable=False),
        sa.Column('route', sa.String(20), nullable=False),
        sa.Column('repeats', sa.Integer, nullable=False),
        sa.Column('indication', sa.Text, nullable=True),
        sa.Column('pbs_listed', sa.Boolean, nullable=True),
        sa.Column('pbs_item_code', sa.String(10), nullable=True),
        sa.Column('authority_required', sa.Boolean, nullable=True),
        sa.Column('validation_errors', postgresql.JSON, nullable=True),
        sa.Column('is_valid', sa.Boolean, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.CheckConstraint('repeats >= 0 AND repeats <= 5', name='check_repeats_range')
    )

    # Indexes for emr_prescriptions
    op.create_index('idx_emr_prescriptions_session_id', 'emr_prescriptions', ['session_id'])
    op.create_index('idx_emr_prescriptions_medication', 'emr_prescriptions', ['medication_name'])

    # 5. Create emr_pathology_orders table
    op.create_table(
        'emr_pathology_orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('test_name', sa.String(200), nullable=False),
        sa.Column('test_category', sa.String(50), nullable=True),
        sa.Column('mbs_item_number', sa.String(10), nullable=True),
        sa.Column('urgency', sa.String(20), nullable=False, server_default='routine'),
        sa.Column('indication', sa.Text, nullable=True),
        sa.Column('appropriate', sa.Boolean, nullable=True),
        sa.Column('validation_feedback', postgresql.JSON, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.text('NOW()'))
    )

    # Indexes for emr_pathology_orders
    op.create_index('idx_emr_pathology_orders_session_id', 'emr_pathology_orders', ['session_id'])
    op.create_index('idx_emr_pathology_orders_urgency', 'emr_pathology_orders', ['urgency'])
    op.create_index('idx_emr_pathology_orders_test_name', 'emr_pathology_orders', ['test_name'])

    # 6. Create emr_validation_results table
    op.create_table(
        'emr_validation_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('emr_sessions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('validation_type', sa.String(50), nullable=False),
        sa.Column('layer_1_zod', postgresql.JSON, nullable=True),
        sa.Column('layer_2_python', postgresql.JSON, nullable=True),
        sa.Column('layer_3_ai', postgresql.JSON, nullable=True),
        sa.Column('overall_score', sa.Float, nullable=True),
        sa.Column('passed', sa.Boolean, nullable=True),
        sa.Column('strengths', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('improvements', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('red_flags', postgresql.ARRAY(sa.Text), nullable=True),
        sa.Column('validated_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.text('NOW()')),
        sa.CheckConstraint('overall_score >= 0 AND overall_score <= 15', name='check_overall_score')
    )

    # Indexes for emr_validation_results
    op.create_index('idx_emr_validation_results_session_id', 'emr_validation_results', ['session_id'])
    op.create_index('idx_emr_validation_results_type', 'emr_validation_results', ['validation_type'])
    op.create_index('idx_emr_validation_results_validated_at', 'emr_validation_results', [sa.text('validated_at DESC')])

    # 7. Extend user_progress table
    op.add_column('user_progress', sa.Column('emr_sessions_completed', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_soap_notes_written', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_average_score', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_total_time_minutes', sa.Integer, server_default='0'))

    # Specialty-specific EMR columns
    op.add_column('user_progress', sa.Column('emr_cardiology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_respiratory_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_gastroenterology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_neurology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_endocrinology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_rheumatology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_haematology_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_renal_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_infectious_diseases_sessions', sa.Integer, server_default='0'))
    op.add_column('user_progress', sa.Column('emr_emergency_medicine_sessions', sa.Integer, server_default='0'))

    # Performance metrics
    op.add_column('user_progress', sa.Column('emr_pass_rate', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_highest_score', sa.Float, server_default='0.0'))
    op.add_column('user_progress', sa.Column('emr_last_session_date', sa.Date, nullable=True))


def downgrade():
    """Remove EMR tables and user_progress extensions."""

    # Drop tables in reverse order (due to foreign keys)
    op.drop_table('emr_validation_results')
    op.drop_table('emr_pathology_orders')
    op.drop_table('emr_prescriptions')
    op.drop_table('emr_soap_notes')
    op.drop_table('emr_sessions')
    op.drop_table('mock_patients')

    # Remove user_progress columns
    op.drop_column('user_progress', 'emr_last_session_date')
    op.drop_column('user_progress', 'emr_highest_score')
    op.drop_column('user_progress', 'emr_pass_rate')

    op.drop_column('user_progress', 'emr_emergency_medicine_sessions')
    op.drop_column('user_progress', 'emr_infectious_diseases_sessions')
    op.drop_column('user_progress', 'emr_renal_sessions')
    op.drop_column('user_progress', 'emr_haematology_sessions')
    op.drop_column('user_progress', 'emr_rheumatology_sessions')
    op.drop_column('user_progress', 'emr_endocrinology_sessions')
    op.drop_column('user_progress', 'emr_neurology_sessions')
    op.drop_column('user_progress', 'emr_gastroenterology_sessions')
    op.drop_column('user_progress', 'emr_respiratory_sessions')
    op.drop_column('user_progress', 'emr_cardiology_sessions')

    op.drop_column('user_progress', 'emr_total_time_minutes')
    op.drop_column('user_progress', 'emr_average_score')
    op.drop_column('user_progress', 'emr_soap_notes_written')
    op.drop_column('user_progress', 'emr_sessions_completed')
```

---

## 5. Data Population Strategy

### 5.1 Initial Data: Convert Existing OSCEs

**Script**: `backend/scripts/populate_mock_patients.py`

```python
"""
Convert existing 221 OSCE scenarios into mock_patients entries.

Priority:
1. Cardiology (20 OSCEs → 20 patients)
2. Respiratory (20 OSCEs → 20 patients)
3. Emergency Medicine (10 OSCEs → 10 patients)
Total: 50 patients (MVP)

Full conversion: 221 patients (all specialties)
"""

async def convert_osces_to_mock_patients():
    # Fetch all OSCEs from database
    osces = await db.query(OSCE).all()

    for osce in osces:
        # Parse patient_instructions to extract demographics
        patient_data = parse_patient_instructions(osce.patient_instructions)

        # Generate realistic clinical data
        mock_patient = MockPatient(
            mrn=generate_mrn(),
            medicare_number=generate_medicare_number(),
            # ... (see ARCHITECTURE.md Section 4.1 for full conversion logic)
        )

        await db.add(mock_patient)

    await db.commit()
```

**Execution**:
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
python scripts/populate_mock_patients.py
```

**Expected Result**:
- 50 mock_patients entries (MVP)
- Linked to source_osce_id
- Realistic vital signs, investigation results, medications

---

## 6. Performance Considerations

### 6.1 Index Strategy

**Query Patterns**:
1. **Get recent sessions for user**:
   ```sql
   SELECT * FROM emr_sessions
   WHERE user_id = ? AND deleted_at IS NULL
   ORDER BY started_at DESC
   LIMIT 20;
   ```
   → **Index**: `idx_emr_sessions_user_id`, `idx_emr_sessions_started_at`

2. **Get user's cardiology sessions**:
   ```sql
   SELECT * FROM emr_sessions
   WHERE user_id = ? AND specialty = 'cardiology'
   ORDER BY started_at DESC;
   ```
   → **Index**: `idx_emr_sessions_user_specialty` (composite)

3. **Get random patient by specialty**:
   ```sql
   SELECT * FROM mock_patients
   WHERE specialty = ? AND difficulty = ? AND deleted_at IS NULL
   ORDER BY RANDOM()
   LIMIT 1;
   ```
   → **Index**: `idx_mock_patients_specialty`, `idx_mock_patients_difficulty`

### 6.2 Estimated Storage

**1 Year Projection** (100 active users):

| Table | Rows | Avg Row Size | Total Size |
|-------|------|--------------|------------|
| mock_patients | 500 | 10 KB (JSON heavy) | 5 MB |
| emr_sessions | 50,000 | 2 KB | 100 MB |
| emr_soap_notes | 50,000 | 5 KB (text + JSON) | 250 MB |
| emr_prescriptions | 100,000 | 1 KB | 100 MB |
| emr_pathology_orders | 75,000 | 1 KB | 75 MB |
| emr_validation_results | 150,000 | 3 KB (AI feedback) | 450 MB |
| **Total** | | | **~1 GB** |

**Scaling**: 1,000 users × 10 years = ~100 GB (manageable with PostgreSQL partitioning if needed)

### 6.3 Query Optimization

**Materialized Views** (future enhancement):

```sql
-- Pre-aggregate user EMR statistics
CREATE MATERIALIZED VIEW user_emr_stats AS
SELECT
    user_id,
    COUNT(*) AS total_sessions,
    AVG(validation_score) AS avg_score,
    SUM(CASE WHEN validation_score >= 9 THEN 1 ELSE 0 END)::FLOAT / COUNT(*) AS pass_rate,
    MAX(validation_score) AS highest_score,
    SUM(elapsed_time_seconds) / 60 AS total_time_minutes
FROM emr_sessions
WHERE status = 'graded' AND deleted_at IS NULL
GROUP BY user_id;

-- Refresh daily
REFRESH MATERIALIZED VIEW user_emr_stats;
```

---

## 7. Migration Execution Plan

### 7.1 Pre-Migration Checklist

- [ ] Backup `irstudy_medical` database
- [ ] Test migration on development database
- [ ] Verify all foreign key constraints
- [ ] Check Alembic revision history
- [ ] Notify users of brief downtime (if production)

### 7.2 Execution Steps

```bash
# 1. Navigate to backend directory
cd /home/dev/Development/irStudy/backend

# 2. Activate virtual environment
source venv/bin/activate

# 3. Generate migration (if not already created)
alembic revision --autogenerate -m "Add EMR practice system tables"

# 4. Review generated migration file
cat alembic/versions/emr_001_*.py

# 5. Apply migration
alembic upgrade head

# 6. Verify tables created
psql -h localhost -p 5433 -d irstudy_medical -U postgres -c "\dt emr_*"
psql -h localhost -p 5433 -d irstudy_medical -U postgres -c "\dt mock_patients"

# 7. Verify user_progress columns added
psql -h localhost -p 5433 -d irstudy_medical -U postgres -c "\d user_progress"

# 8. Populate initial data (50 patients from OSCEs)
python scripts/populate_mock_patients.py

# 9. Verify data
psql -h localhost -p 5433 -d irstudy_medical -U postgres -c "SELECT COUNT(*) FROM mock_patients;"
```

### 7.3 Rollback Plan

```bash
# If migration fails, rollback
alembic downgrade -1

# Restore from backup (if needed)
psql -h localhost -p 5433 -d irstudy_medical -U postgres < backup_2026_02_15.sql
```

---

## 8. Testing Strategy

### 8.1 Unit Tests (pytest)

```python
# tests/test_emr_models.py

def test_mock_patient_creation():
    """Test mock patient model creation and validation."""
    patient = MockPatient(
        mrn="MRN12345678",
        name="John Smith",
        age=58,
        gender="male",
        demographics={"address": "12 King St, Sydney NSW 2000"},
        presenting_complaint="Central chest pain",
        specialty="cardiology",
        difficulty="medium"
    )
    assert patient.mrn == "MRN12345678"
    assert patient.age == 58

def test_emr_session_scoring():
    """Test AMC rubric scoring (0-15, pass mark 9/15)."""
    session = EMRSession(
        user_id=1,
        patient_id=uuid4(),
        specialty="cardiology",
        difficulty="medium",
        validation_score=12.5
    )
    assert session.validation_score >= 9  # Pass
    assert session.validation_score <= 15

def test_prescription_pbs_compliance():
    """Test PBS repeats validation (max 5)."""
    prescription = EMRPrescription(
        session_id=uuid4(),
        medication_name="Amlodipine",
        dose="5mg",
        frequency="daily",
        route="PO",
        repeats=3  # Valid (max 5)
    )
    assert prescription.repeats <= 5
```

### 8.2 Integration Tests

```python
# tests/test_emr_api.py

async def test_start_emr_session(client, auth_headers):
    """Test POST /api/v1/emr/sessions/start."""
    response = await client.post(
        "/api/v1/emr/sessions/start",
        json={"patient_id": str(patient_id), "specialty": "cardiology"},
        headers=auth_headers
    )
    assert response.status_code == 201
    assert response.json()["status"] == "in_progress"

async def test_auto_save_soap_note(client, auth_headers, session_id):
    """Test PUT /api/v1/emr/sessions/{id} (auto-save)."""
    response = await client.put(
        f"/api/v1/emr/sessions/{session_id}",
        json={
            "soap_note": {
                "subjective": "58M with 2h central chest pain...",
                "objective": "HR 95, BP 155/92...",
                "assessment": "ACS - Inferior STEMI",
                "plan": "Call 000, aspirin 300mg STAT..."
            }
        },
        headers=auth_headers
    )
    assert response.status_code == 200
    assert response.json()["auto_save_count"] == 1
```

---

## 9. Success Criteria

- [x] Migration script created (`2026_02_15_emr_tables.py`)
- [ ] Migration runs successfully (`alembic upgrade head`)
- [ ] 6 new tables created (mock_patients, emr_sessions, etc.)
- [ ] user_progress table extended with 17 new columns
- [ ] All indexes created successfully
- [ ] 50 mock_patients populated from OSCEs
- [ ] Zero downtime (development environment)
- [ ] All foreign key constraints validated
- [ ] pytest unit tests pass (100%)
- [ ] Database size < 10 MB (initial state)

---

## Conclusion

This migration adds a **robust, scalable database schema** for the Epic EHR Practice System. Key highlights:

- ✅ **6 new tables** optimized for EMR workflows
- ✅ **17 new columns** in user_progress for unified tracking
- ✅ **Comprehensive indexes** for query performance
- ✅ **Australian compliance** (Medicare numbers, PBS/MBS, Aboriginal/TSI status)
- ✅ **AMC rubric alignment** (15-mark scoring system)
- ✅ **Soft delete pattern** (GDPR/data retention compliance)
- ✅ **JSON flexibility** (medications, investigations, validation feedback)

**Next Steps**: Proceed to API_SPECIFICATION.md for backend endpoint design.

---

**Document Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2026-02-15
**Review Date**: Post-migration (verify table creation)
