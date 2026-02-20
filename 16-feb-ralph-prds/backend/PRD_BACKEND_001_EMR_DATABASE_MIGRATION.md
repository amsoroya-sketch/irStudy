# PRD: EMR Database Migration

**PRD ID**: PRD_BACKEND_001_EMR_DATABASE_MIGRATION
**Category**: Backend
**Priority**: P0-Critical (BLOCKS all other EMR work)
**Estimated Effort**: 8-12 hours
**Dependencies**: None (foundation task)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** backend developer
**I want** a complete EMR database schema with all necessary tables, indexes, and relationships
**So that** the EMR Practice System can store patient scenarios, SOAP notes, prescriptions, pathology orders, and session data for AMC Clinical Examination preparation

### Business Context
The EMR Practice System requires dedicated database infrastructure to support:
1. **500+ simulated patient scenarios** (converted from existing 221 OSCEs)
2. **EMR session tracking** (practice sessions for both Cerner and Epic)
3. **Australian SOAP notes** (AHPRA-compliant clinical documentation)
4. **PBS prescriptions** (Australian medication orders with validation)
5. **MBS pathology orders** (Australian investigation requests)
6. **AI validation results** (3-layer feedback storage)
7. **Progress tracking** (EMR-specific metrics separate from MCQ/OSCE)
8. **OSCE integration** (link EMR practice to OSCE stations)

This database migration is the **foundation** for all EMR functionality and must be completed before any other EMR work can begin.

### Success Metrics
- **Migration Speed**: Complete in <5 minutes (no table locks)
- **Data Integrity**: 0 data loss, all foreign keys validated
- **Query Performance**: All core queries <50ms after indexing
- **Schema Accuracy**: 100% match to specification (6 tables + 17 columns)
- **Rollback Safety**: Rollback script tested and functional

### Scope
**In Scope**:
- 6 new EMR-specific tables (emr_sessions, mock_patients, emr_soap_notes, emr_prescriptions, emr_pathology_orders, emr_validation_results)
- 17 new columns in existing `user_progress` table (EMR metrics)
- Performance indexes for all common query patterns
- Australian-specific fields (Medicare numbers, Aboriginal/TSI status, PBS/MBS codes)
- OSCE integration foreign keys
- Alembic migration script (forward + rollback)

**Out of Scope** (Future Iterations):
- Data population (50 patient scenarios) - Separate PRD_BACKEND_004
- Database triggers - Handled in Phase 0.3
- Materialized views for analytics - Future optimization
- Cerner-specific tables (only Epic + Cerner flag in emr_sessions)

---

## A - ARCHITECTURE (How)

### Technical Approach
Create Alembic migration script to extend PostgreSQL database with EMR-specific schema while preserving existing tables and data. Use `CREATE INDEX CONCURRENTLY` to avoid table locks during index creation (production-safe).

### System Design

#### Database ER Diagram
```
┌─────────────┐         ┌──────────────────┐         ┌─────────────────┐
│   users     │◄────────│  emr_sessions    │────────►│ mock_patients   │
│             │         │                  │         │                 │
│ - id (PK)   │         │ - id (PK)        │         │ - id (PK)       │
│ - email     │         │ - user_id (FK)   │         │ - mrn           │
│ - role      │         │ - patient_id(FK) │         │ - full_name     │
└─────────────┘         │ - osce_id (FK)   │         │ - age, gender   │
                        │ - emr_system     │         │ - allergies     │
                        │ - is_active      │         │ - medications   │
                        │ - session_data   │         │ - specialty     │
                        └────────┬─────────┘         └─────────────────┘
                                 │
                   ┌─────────────┼─────────────┬──────────────────┐
                   │             │             │                  │
         ┌─────────▼────────┐ ┌─▼──────────────┐ ┌──────────────▼─────────┐
         │ emr_soap_notes   │ │emr_prescriptions│ │emr_pathology_orders    │
         │                  │ │                 │ │                        │
         │ - id (PK)        │ │ - id (PK)       │ │ - id (PK)              │
         │ - session_id(FK) │ │ - session_id(FK)│ │ - session_id (FK)      │
         │ - subjective     │ │ - medication    │ │ - test_name            │
         │ - objective      │ │ - pbs_code      │ │ - mbs_item_number      │
         │ - assessment     │ │ - dose, route   │ │ - urgency              │
         │ - plan           │ │ - repeats ≤5    │ │ - indication           │
         │ - validation_    │ │ - indication    │ │ - validation_feedback  │
         │   feedback       │ │ - validation_   │ └────────────────────────┘
         │ - ahpra_         │ │   feedback      │
         │   compliant      │ └─────────────────┘
         └──────────────────┘
                   │
         ┌─────────▼──────────────┐
         │emr_validation_results  │
         │                        │
         │ - id (PK)              │
         │ - session_id (FK)      │
         │ - validation_type      │ ← (soap_note | prescription | pathology)
         │ - layer (1|2|3)        │ ← (Zod | Python | Claude AI)
         │ - score (0-100)        │
         │ - feedback_json        │
         │ - australian_compliant │
         └────────────────────────┘
```

#### Existing Table Extension
```
┌─────────────────┐
│ user_progress   │ ← EXTEND with 17 new EMR columns
│                 │
│ (existing cols) │
│ - mcq_attempted │
│ - osce_completed│
│                 │
│ (NEW EMR cols)  │
│ - emr_sessions_total        │
│ - emr_soap_notes_completed  │
│ - emr_avg_typing_wpm        │
│ - emr_avg_completion_time   │
│ - emr_avg_validation_score  │
│ - emr_ahpra_compliance_rate │
│ - emr_cerner_sessions       │
│ - emr_epic_sessions         │
│ - emr_prescriptions_written │
│ - emr_pathology_orders      │
│ - emr_first_soap_score      │
│ - emr_latest_soap_score     │
│ - emr_improvement_pct       │
│ - emr_specialty_cardiology  │
│ - emr_specialty_respiratory │
│ - emr_specialty_emergency   │
│ - emr_specialty_other       │
└─────────────────┘
```

### Database Schema Details

#### Table 1: emr_sessions
```sql
CREATE TABLE emr_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_scenario_id UUID REFERENCES mock_patients(id) ON DELETE SET NULL,
    osce_id VARCHAR(50) REFERENCES osces(osce_id) ON DELETE SET NULL,

    -- Session Configuration
    emr_system VARCHAR(20) NOT NULL CHECK (emr_system IN ('cerner', 'epic')),
    session_type VARCHAR(50) DEFAULT 'practice' CHECK (session_type IN ('practice', 'osce', 'assessment')),

    -- Session State
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    auto_saved_at TIMESTAMP,

    -- Session Data (JSONB for flexibility)
    session_data JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "current_tab": "soap_note",
    --   "draft_subjective": "Patient presents with...",
    --   "typing_start_time": "2026-02-16T10:30:00Z",
    --   "word_count": 145
    -- }

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- Constraints
    CONSTRAINT valid_completion CHECK (
        (is_active = FALSE AND completed_at IS NOT NULL) OR
        (is_active = TRUE AND completed_at IS NULL)
    )
);

-- Indexes for performance
CREATE INDEX idx_emr_sessions_user_id ON emr_sessions(user_id);
CREATE INDEX idx_emr_sessions_active ON emr_sessions(user_id, is_active) WHERE is_active = TRUE;
CREATE INDEX idx_emr_sessions_osce ON emr_sessions(osce_id) WHERE osce_id IS NOT NULL;
CREATE INDEX idx_emr_sessions_created ON emr_sessions(user_id, created_at DESC);
```

#### Table 2: mock_patients
```sql
CREATE TABLE mock_patients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Demographics (Australian format)
    mrn VARCHAR(10) UNIQUE NOT NULL, -- Medical Record Number (8 digits)
    medicare_number VARCHAR(11), -- 10 digits + 1 check digit (e.g., 2428 341 221 7)
    full_name VARCHAR(100) NOT NULL,
    preferred_name VARCHAR(100),
    date_of_birth DATE NOT NULL,
    age INTEGER GENERATED ALWAYS AS (EXTRACT(YEAR FROM AGE(date_of_birth))) STORED,
    gender VARCHAR(20) NOT NULL CHECK (gender IN ('Male', 'Female', 'Other', 'Prefer not to say')),

    -- Australian-specific fields
    indigenous_status VARCHAR(100) DEFAULT 'Neither Aboriginal nor Torres Strait Islander',
    -- Options: 'Aboriginal', 'Torres Strait Islander', 'Both', 'Neither Aboriginal nor Torres Strait Islander'
    country_of_birth VARCHAR(100) DEFAULT 'Australia',
    primary_language VARCHAR(50) DEFAULT 'English',
    interpreter_required BOOLEAN DEFAULT FALSE,

    -- Contact Information
    address_line1 VARCHAR(200),
    suburb VARCHAR(100),
    state VARCHAR(3) CHECK (state IN ('NSW', 'VIC', 'QLD', 'SA', 'WA', 'TAS', 'NT', 'ACT')),
    postcode VARCHAR(4),
    phone VARCHAR(20),
    emergency_contact VARCHAR(200),
    gp_name VARCHAR(100),
    gp_phone VARCHAR(20),

    -- Clinical Information
    allergies TEXT[], -- Array: ['Penicillin', 'Peanuts']
    current_medications JSONB DEFAULT '[]'::jsonb,
    -- Example: [{"name": "Paracetamol", "dose": "500mg", "frequency": "PRN"}]

    medical_history JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "past_illnesses": ["Hypertension", "Type 2 Diabetes"],
    --   "surgeries": ["Appendectomy 2015"],
    --   "family_history": "Father with CAD"
    -- }

    social_history JSONB DEFAULT '{}'::jsonb,
    -- Example: {"smoking": "never", "alcohol": "occasional", "occupation": "teacher"}

    -- Vital Signs (Current)
    vital_signs JSONB DEFAULT '{}'::jsonb,
    -- Example: {"BP": "145/90", "HR": 88, "RR": 16, "Temp": 37.2, "SpO2": 98}

    -- Clinical Scenario
    presenting_complaint TEXT NOT NULL,
    clinical_scenario TEXT NOT NULL, -- Full case description
    specialty VARCHAR(50) NOT NULL,
    -- Options: Cardiology, Respiratory, Emergency Medicine, Gastroenterology,
    --          Neurology, Endocrinology, Psychiatry, Obstetrics, Paediatrics, General Practice

    complexity_level VARCHAR(20) NOT NULL CHECK (complexity_level IN ('Simple', 'Moderate', 'Complex')),
    expected_diagnosis VARCHAR(200),
    differential_diagnoses TEXT[],

    -- Investigation Results (if pre-populated)
    investigation_results JSONB DEFAULT '{}'::jsonb,
    -- Example: {
    --   "ECG": "Sinus rhythm, HR 88, normal axis",
    --   "FBC": {"Hb": 145, "WCC": 7.2, "Platelets": 250},
    --   "Troponin": 0.02
    -- }

    -- Australian Guidelines
    australian_guidelines_url TEXT,
    etg_reference TEXT, -- eTG (Therapeutic Guidelines) section
    amh_reference TEXT, -- AMH (Australian Medicines Handbook) section

    -- Source Information
    created_from VARCHAR(50) DEFAULT 'manual', -- 'manual' | 'osce_conversion' | 'ai_generated'
    source_osce_id VARCHAR(50), -- If converted from OSCE

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_mock_patients_specialty ON mock_patients(specialty) WHERE is_active = TRUE;
CREATE INDEX idx_mock_patients_complexity ON mock_patients(complexity_level) WHERE is_active = TRUE;
CREATE INDEX idx_mock_patients_source_osce ON mock_patients(source_osce_id) WHERE source_osce_id IS NOT NULL;
CREATE INDEX idx_mock_patients_mrn ON mock_patients(mrn);
```

#### Table 3: emr_soap_notes
```sql
CREATE TABLE emr_soap_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_scenario_id UUID NOT NULL REFERENCES mock_patients(id) ON DELETE CASCADE,

    -- SOAP Sections (Australian format per constraints)
    subjective TEXT NOT NULL CHECK (LENGTH(subjective) >= 50),
    objective TEXT NOT NULL CHECK (LENGTH(objective) >= 30),
    assessment TEXT NOT NULL CHECK (LENGTH(assessment) >= 30),
    plan TEXT NOT NULL CHECK (LENGTH(plan) >= 30),

    -- Note Type
    note_type VARCHAR(50) NOT NULL DEFAULT 'Progress Note',
    -- Options: 'Progress Note', 'Admission Note', 'Discharge Summary', 'Procedure Note', 'Consult Note'

    -- Typing Metrics
    typing_wpm INTEGER, -- Words per minute
    completion_time_seconds INTEGER, -- Time from start to submit
    draft_saves INTEGER DEFAULT 0, -- Number of auto-saves
    character_count INTEGER GENERATED ALWAYS AS (
        LENGTH(subjective) + LENGTH(objective) + LENGTH(assessment) + LENGTH(plan)
    ) STORED,

    -- Validation Results (3-layer system)
    validation_layer1_errors JSONB DEFAULT '[]'::jsonb, -- Zod (client-side)
    validation_layer2_warnings JSONB DEFAULT '[]'::jsonb, -- Python (server-side)
    validation_layer3_feedback JSONB, -- Claude AI (clinical reasoning)

    overall_validation_score DECIMAL(5,2), -- 0-100

    -- Australian Compliance
    ahpra_compliant BOOLEAN DEFAULT FALSE,
    australian_terminology_correct BOOLEAN DEFAULT FALSE,
    pbs_mbs_mentioned BOOLEAN DEFAULT FALSE,
    safety_netting_present BOOLEAN DEFAULT FALSE,

    -- AMC Rubric Scores (if OSCE context)
    communication_score INTEGER CHECK (communication_score BETWEEN 0 AND 3),
    clinical_reasoning_score INTEGER CHECK (clinical_reasoning_score BETWEEN 0 AND 4),
    information_gathering_score INTEGER CHECK (information_gathering_score BETWEEN 0 AND 3),
    management_score INTEGER CHECK (management_score BETWEEN 0 AND 3),
    professionalism_score INTEGER CHECK (professionalism_score BETWEEN 0 AND 2),
    total_amc_score INTEGER GENERATED ALWAYS AS (
        COALESCE(communication_score, 0) +
        COALESCE(clinical_reasoning_score, 0) +
        COALESCE(information_gathering_score, 0) +
        COALESCE(management_score, 0) +
        COALESCE(professionalism_score, 0)
    ) STORED,
    pass_status BOOLEAN GENERATED ALWAYS AS (
        COALESCE(communication_score, 0) +
        COALESCE(clinical_reasoning_score, 0) +
        COALESCE(information_gathering_score, 0) +
        COALESCE(management_score, 0) +
        COALESCE(professionalism_score, 0) >= 9
    ) STORED, -- Pass = ≥9/15

    -- Timestamps
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    validated_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_soap_notes_user ON emr_soap_notes(user_id, created_at DESC);
CREATE INDEX idx_soap_notes_session ON emr_soap_notes(emr_session_id);
CREATE INDEX idx_soap_notes_patient ON emr_soap_notes(patient_scenario_id);
CREATE INDEX idx_soap_notes_pass ON emr_soap_notes(user_id, pass_status);
```

#### Table 4: emr_prescriptions
```sql
CREATE TABLE emr_prescriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_scenario_id UUID NOT NULL REFERENCES mock_patients(id) ON DELETE CASCADE,

    -- Prescription Details (Australian PBS format)
    medication_name VARCHAR(200) NOT NULL,
    medication_generic_name VARCHAR(200), -- Generic name (PBS requirement)
    pbs_code VARCHAR(20), -- PBS item number (e.g., 1215K)

    -- Dosing
    dose VARCHAR(100) NOT NULL, -- e.g., "500mg"
    frequency VARCHAR(100) NOT NULL, -- e.g., "BD" (twice daily)
    route VARCHAR(50) NOT NULL, -- e.g., "PO" (oral)
    duration VARCHAR(100), -- e.g., "7 days"
    quantity INTEGER NOT NULL, -- Number of tablets/units
    repeats INTEGER NOT NULL DEFAULT 0 CHECK (repeats <= 5), -- Max 5 repeats (PBS)

    -- Indication (PBS requirement)
    indication TEXT NOT NULL CHECK (LENGTH(indication) >= 5),

    -- Safety Checks
    drug_interactions_checked BOOLEAN DEFAULT FALSE,
    allergy_checked BOOLEAN DEFAULT FALSE,
    dose_appropriate BOOLEAN,
    renal_adjustment_considered BOOLEAN DEFAULT FALSE,

    -- PBS Compliance
    pbs_listed BOOLEAN,
    pbs_compliant BOOLEAN,
    streamlined_authority_required BOOLEAN DEFAULT FALSE,

    -- Validation Results
    validation_score DECIMAL(5,2), -- 0-100
    validation_errors JSONB DEFAULT '[]'::jsonb,
    validation_warnings JSONB DEFAULT '[]'::jsonb,
    validation_feedback JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_prescriptions_user ON emr_prescriptions(user_id, created_at DESC);
CREATE INDEX idx_prescriptions_session ON emr_prescriptions(emr_session_id);
CREATE INDEX idx_prescriptions_medication ON emr_prescriptions(medication_generic_name);
```

#### Table 5: emr_pathology_orders
```sql
CREATE TABLE emr_pathology_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    patient_scenario_id UUID NOT NULL REFERENCES mock_patients(id) ON DELETE CASCADE,

    -- Order Details (Australian MBS format)
    test_name VARCHAR(200) NOT NULL,
    mbs_item_number VARCHAR(20), -- Medicare Benefits Schedule (e.g., 65070 for FBC)

    -- Order Type
    is_panel BOOLEAN DEFAULT FALSE,
    panel_tests JSONB DEFAULT '[]'::jsonb,
    -- Example for panel: ["FBC", "UEC", "LFT"]

    -- Urgency
    urgency VARCHAR(20) NOT NULL CHECK (urgency IN ('Routine', 'Urgent', 'Emergency')),

    -- Indication (MBS requirement)
    clinical_indication TEXT NOT NULL CHECK (LENGTH(clinical_indication) >= 10),

    -- Validation
    indication_appropriate BOOLEAN,
    mbs_compliant BOOLEAN,
    over_investigation_detected BOOLEAN DEFAULT FALSE,
    urgency_appropriate BOOLEAN,

    validation_score DECIMAL(5,2), -- 0-100
    validation_feedback JSONB,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_pathology_user ON emr_pathology_orders(user_id, created_at DESC);
CREATE INDEX idx_pathology_session ON emr_pathology_orders(emr_session_id);
CREATE INDEX idx_pathology_test ON emr_pathology_orders(test_name);
```

#### Table 6: emr_validation_results
```sql
CREATE TABLE emr_validation_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    emr_session_id UUID NOT NULL REFERENCES emr_sessions(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- What was validated
    validation_type VARCHAR(50) NOT NULL CHECK (validation_type IN ('soap_note', 'prescription', 'pathology')),
    validated_entity_id UUID NOT NULL, -- FK to emr_soap_notes.id, emr_prescriptions.id, or emr_pathology_orders.id

    -- Which validation layer (3-layer system)
    validation_layer INTEGER NOT NULL CHECK (validation_layer IN (1, 2, 3)),
    -- Layer 1: Zod (client-side TypeScript), Layer 2: Python (server-side), Layer 3: Claude AI

    -- Results
    score DECIMAL(5,2), -- 0-100
    passed BOOLEAN DEFAULT FALSE,

    -- Feedback Details
    errors JSONB DEFAULT '[]'::jsonb, -- Red errors (blocking)
    warnings JSONB DEFAULT '[]'::jsonb, -- Yellow warnings (non-blocking)
    insights JSONB DEFAULT '[]'::jsonb, -- Green insights (educational)

    detailed_feedback JSONB, -- Full Claude AI response for Layer 3

    -- Australian Compliance Flags
    australian_terminology_compliant BOOLEAN,
    etg_amh_referenced BOOLEAN,
    ahpra_standards_met BOOLEAN,

    -- Performance Metrics
    validation_latency_ms INTEGER, -- Time taken to validate (for monitoring)

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_validation_user ON emr_validation_results(user_id, created_at DESC);
CREATE INDEX idx_validation_session ON emr_validation_results(emr_session_id);
CREATE INDEX idx_validation_type_layer ON emr_validation_results(validation_type, validation_layer);
CREATE INDEX idx_validation_entity ON emr_validation_results(validated_entity_id);
```

#### Extend Existing Table: user_progress
```sql
-- Add 17 new EMR-specific columns to existing user_progress table
ALTER TABLE user_progress
    -- Session Metrics
    ADD COLUMN emr_sessions_total INTEGER DEFAULT 0,
    ADD COLUMN emr_sessions_completed INTEGER DEFAULT 0,
    ADD COLUMN emr_sessions_active INTEGER DEFAULT 0,

    -- Documentation Metrics
    ADD COLUMN emr_soap_notes_completed INTEGER DEFAULT 0,
    ADD COLUMN emr_prescriptions_written INTEGER DEFAULT 0,
    ADD COLUMN emr_pathology_orders_placed INTEGER DEFAULT 0,

    -- Quality Metrics
    ADD COLUMN emr_avg_validation_score DECIMAL(5,2),
    ADD COLUMN emr_avg_typing_wpm INTEGER,
    ADD COLUMN emr_avg_completion_time_seconds INTEGER,
    ADD COLUMN emr_ahpra_compliance_rate DECIMAL(5,2),

    -- EMR System Usage
    ADD COLUMN emr_cerner_sessions INTEGER DEFAULT 0,
    ADD COLUMN emr_epic_sessions INTEGER DEFAULT 0,

    -- Improvement Tracking
    ADD COLUMN emr_first_soap_score DECIMAL(5,2),
    ADD COLUMN emr_latest_soap_score DECIMAL(5,2),
    ADD COLUMN emr_improvement_percentage DECIMAL(5,2),

    -- Specialty Breakdown (simplified - detailed in JSONB if needed)
    ADD COLUMN emr_specialty_stats JSONB DEFAULT '{}'::jsonb;
    -- Example: {"cardiology": 10, "respiratory": 5, "emergency_medicine": 3}

-- Index for EMR progress queries
CREATE INDEX idx_user_progress_emr ON user_progress(user_id, emr_sessions_completed DESC);
```

### Technology Stack
- **Database**: PostgreSQL 15 (existing instance at localhost:5433)
- **Migration Tool**: Alembic 1.13+
- **ORM**: SQLAlchemy 2.0+
- **Python**: 3.11+
- **Validation**: Check constraints, foreign keys, generated columns

### Integration Points
- **Integrates with**: Existing `users` table, existing `osces` table
- **Consumed by**: EMR API endpoints (PRD_BACKEND_002, PRD_BACKEND_003)
- **Depends on**: Existing database infrastructure

### Security Considerations
- [x] No hardcoded credentials (database password from Vault/env)
- [x] Foreign key constraints prevent orphaned records
- [x] ON DELETE CASCADE for user data (GDPR compliance)
- [x] ON DELETE SET NULL for reference data (patient scenarios)
- [x] Check constraints for data integrity (e.g., repeats ≤ 5)
- [x] Generated columns for derived data (age, total scores)
- [x] JSONB for flexible but structured data
- [x] Indexes for query performance (all <50ms target)

### Performance Requirements
- **Migration Time**: <5 minutes (CONCURRENTLY for no locks)
- **Query Performance**:
  - Active sessions: <50ms
  - Patient lookup: <50ms
  - SOAP note retrieval: <100ms
  - Progress metrics: <100ms
- **Concurrent Users**: 100+ supported
- **Storage**: ~500 patient scenarios = ~50MB initial data

---

## L - LOOP (Iterative Development)

### Phase 1: Alembic Migration Script (40% of effort, 4-5 hours)
**Goal**: Create production-ready migration script

**Tasks**:
1. Create Alembic revision file - 30 min
2. Write CREATE TABLE statements for 6 tables - 2 hours
3. Write ALTER TABLE for user_progress (17 columns) - 30 min
4. Write CREATE INDEX CONCURRENTLY statements - 1 hour
5. Write rollback/downgrade script - 1 hour

**Validation Gate**:
- [ ] Alembic revision file created (`alembic/versions/20260216_XXXX_add_emr_schema.py`)
- [ ] All 6 tables defined with correct columns, types, constraints
- [ ] 17 columns added to user_progress
- [ ] All indexes created with CONCURRENTLY flag
- [ ] Downgrade script written and tested
- [ ] No syntax errors (`python -m py_compile`)

---

### Phase 2: Execute Migration & Verify (35% of effort, 3-4 hours)
**Goal**: Apply migration to development database and validate

**Tasks**:
1. Backup development database - 15 min
2. Run `alembic upgrade head` - 5 min
3. Verify all tables created - 30 min
4. Verify all indexes created - 30 min
5. Test EXPLAIN ANALYZE on queries - 1 hour
6. Insert test data (5 mock patients) - 1 hour
7. Test all foreign key relationships - 30 min

**Validation Gate**:
- [ ] Migration executes successfully (no errors)
- [ ] All 6 tables exist (`\dt emr_*` in psql)
- [ ] user_progress has 17 new columns (`\d user_progress`)
- [ ] All indexes created (`\di emr_*`)
- [ ] Query performance <50ms (EXPLAIN ANALYZE)
- [ ] Foreign keys validated (test inserts)
- [ ] Test data inserted successfully

---

### Phase 3: Documentation & Rollback Testing (25% of effort, 2-3 hours)
**Goal**: Document schema and ensure rollback safety

**Tasks**:
1. Generate ER diagram - 30 min
2. Document each table in README - 1 hour
3. Test rollback script (`alembic downgrade -1`) - 30 min
4. Write query examples for common patterns - 1 hour

**Validation Gate**:
- [ ] ER diagram created and saved
- [ ] Table documentation complete (columns, constraints, purpose)
- [ ] Rollback tested (downgrade + upgrade works)
- [ ] Query examples documented
- [ ] Migration guide written for production deployment

---

## P - PLAN (Detailed Implementation)

### Phase 1 Tasks

**Task 1.1**: Create Alembic Revision
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: `alembic/versions/20260216_XXXX_add_emr_schema.py`
- **Dependencies**: None
- **Command**:
  ```bash
  cd /home/dev/Development/irStudy/backend
  source venv/bin/activate
  alembic revision -m "add_emr_schema_6_tables_and_user_progress_extension"
  ```
- **Acceptance Criteria**:
  - [ ] Revision file created
  - [ ] File has upgrade() and downgrade() functions
  - [ ] Revision ID generated

**Task 1.2**: Write CREATE TABLE for emr_sessions
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete emr_sessions table definition
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] All columns defined (id, user_id, patient_scenario_id, osce_id, emr_system, etc.)
  - [ ] Foreign keys to users, mock_patients, osces
  - [ ] CHECK constraint for emr_system IN ('cerner', 'epic')
  - [ ] CHECK constraint for valid completion state
  - [ ] Timestamps (created_at, updated_at)

**Task 1.3**: Write CREATE TABLE for mock_patients
- **Effort**: 1 hour (largest table, many columns)
- **Owner**: Backend Engineer
- **Deliverable**: Complete mock_patients table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Demographics (mrn, medicare_number, full_name, date_of_birth, age GENERATED, gender)
  - [ ] Australian fields (indigenous_status, country_of_birth, interpreter_required)
  - [ ] Address fields (address_line1, suburb, state CHECK constraint, postcode)
  - [ ] Clinical data (allergies ARRAY, current_medications JSONB, medical_history JSONB)
  - [ ] Vital signs JSONB
  - [ ] Scenario details (presenting_complaint, clinical_scenario, specialty, complexity)
  - [ ] Australian guidelines (etg_reference, amh_reference)
  - [ ] Source tracking (created_from, source_osce_id)

**Task 1.4**: Write CREATE TABLE for emr_soap_notes
- **Effort**: 45 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete emr_soap_notes table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] SOAP sections (subjective, objective, assessment, plan) with LENGTH CHECK
  - [ ] Foreign keys to emr_sessions, users, mock_patients
  - [ ] Typing metrics (typing_wpm, completion_time_seconds, draft_saves)
  - [ ] Validation results (3 layers: JSONB for each)
  - [ ] Australian compliance flags (ahpra_compliant, australian_terminology_correct, etc.)
  - [ ] AMC rubric scores (5 domains) with GENERATED ALWAYS total_amc_score
  - [ ] GENERATED ALWAYS pass_status (≥9/15)

**Task 1.5**: Write CREATE TABLE for emr_prescriptions
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete emr_prescriptions table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Medication details (name, generic_name, pbs_code)
  - [ ] Dosing (dose, frequency, route, duration, quantity, repeats)
  - [ ] CHECK constraint repeats ≤ 5
  - [ ] Indication with LENGTH CHECK ≥ 5
  - [ ] Safety flags (drug_interactions_checked, allergy_checked, dose_appropriate)
  - [ ] PBS flags (pbs_listed, pbs_compliant, streamlined_authority_required)
  - [ ] Validation results JSONB

**Task 1.6**: Write CREATE TABLE for emr_pathology_orders
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete emr_pathology_orders table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Test details (test_name, mbs_item_number)
  - [ ] Panel support (is_panel BOOLEAN, panel_tests JSONB)
  - [ ] Urgency with CHECK constraint IN ('Routine', 'Urgent', 'Emergency')
  - [ ] Indication with LENGTH CHECK ≥ 10
  - [ ] Validation flags (indication_appropriate, mbs_compliant, over_investigation_detected)

**Task 1.7**: Write CREATE TABLE for emr_validation_results
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: Complete emr_validation_results table
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Validation metadata (validation_type, validated_entity_id, validation_layer)
  - [ ] CHECK constraint validation_type IN ('soap_note', 'prescription', 'pathology')
  - [ ] CHECK constraint validation_layer IN (1, 2, 3)
  - [ ] Results (score, passed, errors JSONB, warnings JSONB, insights JSONB)
  - [ ] Australian compliance flags
  - [ ] Performance tracking (validation_latency_ms)

**Task 1.8**: Write ALTER TABLE user_progress
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Deliverable**: 17 new columns added
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Session metrics (emr_sessions_total, emr_sessions_completed, emr_sessions_active)
  - [ ] Documentation metrics (emr_soap_notes_completed, emr_prescriptions_written, emr_pathology_orders_placed)
  - [ ] Quality metrics (emr_avg_validation_score, emr_avg_typing_wpm, emr_avg_completion_time_seconds, emr_ahpra_compliance_rate)
  - [ ] EMR system usage (emr_cerner_sessions, emr_epic_sessions)
  - [ ] Improvement tracking (emr_first_soap_score, emr_latest_soap_score, emr_improvement_percentage)
  - [ ] Specialty stats JSONB

**Task 1.9**: Write CREATE INDEX statements
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: 15+ indexes created
- **Dependencies**: Tasks 1.2-1.8
- **Acceptance Criteria**:
  - [ ] All indexes use CREATE INDEX CONCURRENTLY (production-safe)
  - [ ] emr_sessions: idx_user_id, idx_active, idx_osce, idx_created
  - [ ] mock_patients: idx_specialty, idx_complexity, idx_source_osce, idx_mrn
  - [ ] emr_soap_notes: idx_user, idx_session, idx_patient, idx_pass
  - [ ] emr_prescriptions: idx_user, idx_session, idx_medication
  - [ ] emr_pathology_orders: idx_user, idx_session, idx_test
  - [ ] emr_validation_results: idx_user, idx_session, idx_type_layer, idx_entity
  - [ ] user_progress: idx_user_progress_emr

**Task 1.10**: Write Rollback/Downgrade Script
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: Complete downgrade() function
- **Dependencies**: Tasks 1.2-1.9
- **Acceptance Criteria**:
  - [ ] DROP INDEX IF EXISTS for all indexes (reverse order)
  - [ ] ALTER TABLE user_progress DROP COLUMN for all 17 columns
  - [ ] DROP TABLE IF EXISTS for all 6 tables (reverse dependency order)
  - [ ] Downgrade tested in separate branch

---

### Phase 2 Tasks

**Task 2.1**: Backup Development Database
- **Effort**: 15 min
- **Owner**: Backend Engineer
- **Command**:
  ```bash
  pg_dump -h localhost -p 5433 -U postgres irstudy_medical > backups/backup_pre_emr_migration_2026_02_16.sql
  ```
- **Acceptance Criteria**:
  - [ ] Backup file created (size >10MB)
  - [ ] Backup verified (can restore if needed)

**Task 2.2**: Run Migration (Upgrade)
- **Effort**: 5 min
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.1, All Phase 1 tasks
- **Command**:
  ```bash
  cd /home/dev/Development/irStudy/backend
  source venv/bin/activate
  alembic upgrade head
  ```
- **Acceptance Criteria**:
  - [ ] Migration executes with 0 errors
  - [ ] Success message displayed
  - [ ] alembic_version table updated

**Task 2.3**: Verify Tables Created
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.2
- **Commands**:
  ```bash
  psql -h localhost -p 5433 -U postgres irstudy_medical
  \dt emr_*
  \d emr_sessions
  \d mock_patients
  \d emr_soap_notes
  \d emr_prescriptions
  \d emr_pathology_orders
  \d emr_validation_results
  \d user_progress  # Check new columns
  ```
- **Acceptance Criteria**:
  - [ ] 6 EMR tables exist
  - [ ] user_progress has 17 new EMR columns
  - [ ] All columns have correct types
  - [ ] All constraints present (CHECK, FOREIGN KEY, UNIQUE)

**Task 2.4**: Verify Indexes Created
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.2
- **Commands**:
  ```bash
  psql -h localhost -p 5433 -U postgres irstudy_medical
  \di emr_*
  \di user_progress_emr
  ```
- **Acceptance Criteria**:
  - [ ] 15+ indexes created
  - [ ] All indexes show CONCURRENTLY in creation log
  - [ ] No duplicate indexes

**Task 2.5**: Performance Testing (EXPLAIN ANALYZE)
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.4
- **Test Queries**:
  ```sql
  -- Query 1: Get active EMR sessions for user
  EXPLAIN ANALYZE
  SELECT * FROM emr_sessions
  WHERE user_id = '...' AND is_active = TRUE;
  -- Target: Index Scan, <50ms

  -- Query 2: Get patient scenarios by specialty
  EXPLAIN ANALYZE
  SELECT * FROM mock_patients
  WHERE specialty = 'Cardiology' AND is_active = TRUE
  LIMIT 10;
  -- Target: Index Scan, <50ms

  -- Query 3: Get SOAP notes for user (recent first)
  EXPLAIN ANALYZE
  SELECT * FROM emr_soap_notes
  WHERE user_id = '...'
  ORDER BY created_at DESC
  LIMIT 20;
  -- Target: Index Scan, <100ms

  -- Query 4: Get user EMR progress
  EXPLAIN ANALYZE
  SELECT emr_sessions_total, emr_avg_validation_score, emr_improvement_percentage
  FROM user_progress
  WHERE user_id = '...';
  -- Target: Index Scan, <10ms
  ```
- **Acceptance Criteria**:
  - [ ] All queries use Index Scan (not Seq Scan)
  - [ ] All queries <100ms
  - [ ] Critical queries (user sessions, progress) <50ms

**Task 2.6**: Insert Test Data
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.3
- **Deliverable**: 5 test patient scenarios
- **Script**:
  ```python
  # scripts/insert_test_emr_data.py
  from backend.src.db.models.emr import MockPatient
  from backend.src.db.session import SessionLocal

  # Insert 5 diverse test patients:
  # 1. Cardiology: 65M with chest pain
  # 2. Respiratory: 45F with asthma exacerbation
  # 3. Emergency: 30M with trauma
  # 4. Aboriginal patient: 55F with diabetes
  # 5. CALD patient: 60M with interpreter needs
  ```
- **Acceptance Criteria**:
  - [ ] 5 mock patients inserted
  - [ ] All required fields populated
  - [ ] Australian data (Medicare numbers, addresses, indigenous status)
  - [ ] Foreign keys validated (no orphaned records)

**Task 2.7**: Test Foreign Key Relationships
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Dependencies**: Task 2.6
- **Test Cases**:
  ```sql
  -- Test 1: Create EMR session linked to test patient
  INSERT INTO emr_sessions (user_id, patient_scenario_id, emr_system)
  VALUES ('existing_user_id', 'test_patient_1_id', 'epic');

  -- Test 2: Try to insert SOAP note without session (should fail)
  INSERT INTO emr_soap_notes (emr_session_id, user_id, patient_scenario_id, subjective, objective, assessment, plan)
  VALUES ('non_existent_session_id', ...);  -- Expect FK violation error

  -- Test 3: Delete test user, verify CASCADE
  DELETE FROM users WHERE id = 'test_user_id';
  -- Expect: emr_sessions, emr_soap_notes deleted (ON DELETE CASCADE)
  -- Expect: mock_patients remain (ON DELETE SET NULL)
  ```
- **Acceptance Criteria**:
  - [ ] Valid foreign keys allow inserts
  - [ ] Invalid foreign keys raise errors
  - [ ] ON DELETE CASCADE works for user data
  - [ ] ON DELETE SET NULL works for reference data

---

### Phase 3 Tasks

**Task 3.1**: Generate ER Diagram
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Tool**: dbdiagram.io or SchemaSpy
- **Deliverable**: `docs/emr_database_schema.png`
- **Acceptance Criteria**:
  - [ ] All 6 EMR tables shown
  - [ ] Relationships (FK) visualized
  - [ ] Key columns labeled
  - [ ] Diagram saved and committed

**Task 3.2**: Document Schema in README
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/EMR_DATABASE_SCHEMA.md`
- **Contents**:
  - Overview of EMR database architecture
  - Description of each table (purpose, key columns, relationships)
  - Index explanations (why each index exists)
  - Query examples for common operations
  - Australian compliance notes
- **Acceptance Criteria**:
  - [ ] All 6 tables documented
  - [ ] Purpose and usage clear
  - [ ] Query examples tested

**Task 3.3**: Test Rollback Script
- **Effort**: 30 min
- **Owner**: Backend Engineer
- **Dependencies**: All Phase 2 tasks
- **Test Procedure**:
  ```bash
  # Create test branch for rollback testing
  git checkout -b test-emr-rollback

  # Downgrade migration
  alembic downgrade -1

  # Verify all EMR tables dropped
  psql -h localhost -p 5433 -U postgres irstudy_medical -c "\dt emr_*"  # Should return empty

  # Verify user_progress columns removed
  psql -h localhost -p 5433 -U postgres irstudy_medical -c "\d user_progress"  # No emr_* columns

  # Re-upgrade to verify idempotency
  alembic upgrade head

  # Verify tables recreated
  psql -h localhost -p 5433 -U postgres irstudy_medical -c "\dt emr_*"  # 6 tables
  ```
- **Acceptance Criteria**:
  - [ ] Downgrade removes all EMR schema (tables, columns, indexes)
  - [ ] Existing data unaffected (users, mcqs, osces)
  - [ ] Re-upgrade works (idempotent)
  - [ ] Rollback script documented in migration guide

**Task 3.4**: Write Query Examples
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `backend/docs/EMR_QUERY_EXAMPLES.md`
- **Query Categories**:
  1. Session Management (start, list, get active)
  2. Patient Retrieval (by specialty, complexity, random)
  3. SOAP Note CRUD (create, retrieve, update)
  4. Progress Tracking (user stats, improvement trends)
  5. Validation Results (get feedback, filter by layer)
- **Acceptance Criteria**:
  - [ ] 15+ query examples
  - [ ] All queries tested and working
  - [ ] Performance metrics documented
  - [ ] Examples use parameterized queries (SQL injection safe)

---

### Timeline (Example)

| Day | Phase | Tasks | Hours | Deliverable |
|-----|-------|-------|-------|-------------|
| Day 1 AM | Phase 1 | 1.1-1.5 | 4h | First 5 tables defined |
| Day 1 PM | Phase 1 | 1.6-1.10 | 4h | Last table, indexes, rollback script |
| Day 2 AM | Phase 2 | 2.1-2.4 | 2h | Migration executed, verified |
| Day 2 PM | Phase 2 | 2.5-2.7 | 3h | Performance tested, test data |
| Day 3 AM | Phase 3 | 3.1-3.2 | 2h | Documentation |
| Day 3 PM | Phase 3 | 3.3-3.4 | 2h | Rollback tested, query examples |

**Total**: 2-3 days, 8-12 hours effort

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] 6 EMR tables created (emr_sessions, mock_patients, emr_soap_notes, emr_prescriptions, emr_pathology_orders, emr_validation_results)
- [ ] 17 EMR columns added to user_progress
- [ ] All foreign key relationships functional
- [ ] All CHECK constraints enforced
- [ ] Generated columns calculate correctly (age, total_amc_score, pass_status, character_count)
- [ ] JSONB columns accept valid JSON
- [ ] ARRAY columns accept arrays (allergies, differential_diagnoses)

#### Quality Requirements
- [ ] **Migration Success**: Alembic upgrade executes with 0 errors
- [ ] **Rollback Safety**: Alembic downgrade works without data loss
- [ ] **Code Quality**: Python syntax valid (no compilation errors)
- [ ] **Documentation**: Schema documented in README

#### Performance Requirements
- [ ] **Migration Time**: <5 minutes total
- [ ] **Query Performance**: All test queries <50-100ms (per target)
- [ ] **Index Usage**: All queries use Index Scan (verified with EXPLAIN ANALYZE)
- [ ] **No Table Locks**: All indexes created with CONCURRENTLY

#### Security Requirements
- [ ] **No Hardcoded Credentials**: Database password from environment variable
- [ ] **Foreign Key Constraints**: All relationships enforced
- [ ] **Data Integrity**: CHECK constraints prevent invalid data (e.g., repeats >5, negative ages)
- [ ] **GDPR Compliance**: ON DELETE CASCADE for user data

#### Australian Medical Compliance
- [ ] **Medicare Numbers**: 11-character field (10 digits + check digit)
- [ ] **Indigenous Status**: Proper options (Aboriginal, Torres Strait Islander, Both, Neither)
- [ ] **PBS Codes**: Field for PBS item numbers
- [ ] **MBS Codes**: Field for MBS item numbers
- [ ] **Australian States**: CHECK constraint for valid state codes (NSW, VIC, QLD, SA, WA, TAS, NT, ACT)
- [ ] **Australian Terminology**: Fields named appropriately (paracetamol, not acetaminophen)

---

### Testing Requirements

#### Migration Testing
```bash
# Test 1: Fresh migration
alembic upgrade head
# Expected: SUCCESS, 0 errors

# Test 2: Verify table count
psql -h localhost -p 5433 -U postgres irstudy_medical -c "
SELECT COUNT(*) FROM information_schema.tables
WHERE table_schema = 'public' AND table_name LIKE 'emr_%';
"
# Expected: 6 tables

# Test 3: Verify indexes
psql -h localhost -p 5433 -U postgres irstudy_medical -c "
SELECT COUNT(*) FROM pg_indexes
WHERE schemaname = 'public' AND indexname LIKE 'idx_emr_%';
"
# Expected: 15+ indexes

# Test 4: Rollback
alembic downgrade -1
psql -h localhost -p 5433 -U postgres irstudy_medical -c "\dt emr_*"
# Expected: 0 tables

# Test 5: Re-upgrade (idempotency)
alembic upgrade head
# Expected: SUCCESS
```

#### Data Integrity Testing
```python
# Test Case 1: Insert valid mock patient
def test_insert_valid_patient():
    patient = MockPatient(
        mrn='12345678',
        medicare_number='2428 341 221 7',
        full_name='John Smith',
        date_of_birth=date(1960, 5, 15),
        gender='Male',
        indigenous_status='Neither Aboriginal nor Torres Strait Islander',
        specialty='Cardiology',
        complexity_level='Moderate',
        presenting_complaint='Chest pain',
        clinical_scenario='65-year-old male presenting with...'
    )
    db.add(patient)
    db.commit()
    assert patient.age == 65  # Generated column
    assert patient.id is not None

# Test Case 2: Test CHECK constraint (repeats ≤ 5)
def test_prescription_repeats_constraint():
    with pytest.raises(IntegrityError):
        prescription = EMRPrescription(
            medication_name='Paracetamol',
            dose='500mg',
            frequency='QID',
            route='PO',
            quantity=100,
            repeats=6,  # INVALID: >5
            indication='Pain relief'
        )
        db.add(prescription)
        db.commit()

# Test Case 3: Test foreign key cascade
def test_user_delete_cascade():
    # Create user, session, SOAP note
    user = User(email='test@example.com')
    session = EMRSession(user_id=user.id, emr_system='epic')
    soap_note = EMRSOAPNote(
        emr_session_id=session.id,
        user_id=user.id,
        subjective='...',
        objective='...',
        assessment='...',
        plan='...'
    )
    db.add_all([user, session, soap_note])
    db.commit()

    # Delete user
    db.delete(user)
    db.commit()

    # Verify cascade
    assert db.query(EMRSession).filter_by(user_id=user.id).count() == 0
    assert db.query(EMRSOAPNote).filter_by(user_id=user.id).count() == 0
```

#### Performance Testing
```python
# Performance Test 1: Active sessions query
def test_active_sessions_performance():
    import time
    start = time.time()

    sessions = db.query(EMRSession).filter(
        EMRSession.user_id == user_id,
        EMRSession.is_active == True
    ).all()

    elapsed = (time.time() - start) * 1000  # Convert to ms
    assert elapsed < 50, f"Query took {elapsed}ms (target: <50ms)"

# Performance Test 2: Patient specialty lookup
def test_patient_specialty_performance():
    import time
    start = time.time()

    patients = db.query(MockPatient).filter(
        MockPatient.specialty == 'Cardiology',
        MockPatient.is_active == True
    ).limit(10).all()

    elapsed = (time.time() - start) * 1000
    assert elapsed < 50, f"Query took {elapsed}ms (target: <50ms)"
```

---

### Documentation Deliverables

#### 1. Migration Guide (`docs/EMR_DATABASE_MIGRATION_GUIDE.md`)
```markdown
# EMR Database Migration Guide

## Overview
This guide documents the EMR database schema migration (Revision: 20260216_XXXX).

## Pre-Migration Checklist
- [ ] Backup database: `pg_dump -h localhost -p 5433 ... > backup.sql`
- [ ] Review migration script: `alembic/versions/20260216_XXXX_add_emr_schema.py`
- [ ] Verify Alembic version: `alembic current`

## Migration Steps
1. Backup: `pg_dump ...`
2. Upgrade: `alembic upgrade head`
3. Verify: Run verification queries
4. Test: Insert test data

## Rollback Steps
If issues arise:
1. Downgrade: `alembic downgrade -1`
2. Restore backup: `psql ... < backup.sql`

## Post-Migration Verification
- Run test queries (see QUERY_EXAMPLES.md)
- Verify performance (<50ms targets)
- Check foreign keys functional

## Production Deployment
- Schedule during low-traffic window
- Monitor migration progress
- Have rollback script ready
- Test in staging first
```

#### 2. Schema Documentation (`docs/EMR_DATABASE_SCHEMA.md`)
- Table descriptions (purpose, columns, constraints)
- Relationship diagrams
- Index explanations
- Australian compliance notes

#### 3. Query Examples (`docs/EMR_QUERY_EXAMPLES.md`)
- 15+ common query patterns
- Performance benchmarks
- Best practices

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All acceptance criteria met
- [ ] Migration tested in development
- [ ] Rollback script tested
- [ ] Documentation complete
- [ ] Backup strategy confirmed

#### Deployment (Development)
- [ ] Backup database
- [ ] Run `alembic upgrade head`
- [ ] Verify tables created (6 EMR tables)
- [ ] Verify indexes created (15+)
- [ ] Run smoke tests
- [ ] Check logs for errors

#### Post-Deployment
- [ ] Performance metrics within targets (<50ms)
- [ ] Test data inserted successfully
- [ ] Foreign keys functional
- [ ] Documentation updated in repository

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ 6 EMR tables created and verified
2. ✅ 17 columns added to user_progress
3. ✅ All indexes created with CONCURRENTLY
4. ✅ Migration executes in <5 minutes
5. ✅ All queries <50-100ms (performance targets)
6. ✅ Rollback script tested and functional
7. ✅ Documentation complete (3 docs)
8. ✅ Test data inserted (5 mock patients)
9. ✅ Foreign keys validated
10. ✅ Zero data loss or integrity violations

**Sign-off Required From**:
- [ ] Backend Engineer (implementation complete)
- [ ] PM Coordinator (requirements met)
- [ ] Security Expert (no hardcoded credentials, FK constraints OK)
- [ ] DBA (migration safe for production, performance validated)

---

## 📎 Appendices

### Appendix A: Sample Data (Mock Patient)
```json
{
  "mrn": "12345678",
  "medicare_number": "2428 341 221 7",
  "full_name": "William (Billy) Thompson",
  "preferred_name": "Billy",
  "date_of_birth": "1960-03-15",
  "gender": "Male",
  "indigenous_status": "Aboriginal",
  "country_of_birth": "Australia",
  "primary_language": "English",
  "interpreter_required": false,
  "address_line1": "123 George Street",
  "suburb": "Redfern",
  "state": "NSW",
  "postcode": "2016",
  "phone": "0412 345 678",
  "emergency_contact": "Sister - Mary Thompson - 0423 456 789",
  "gp_name": "Dr. Sarah Chen",
  "gp_phone": "02 9555 1234",
  "allergies": ["Penicillin", "Shellfish"],
  "current_medications": [
    {"name": "Metformin", "dose": "1000mg", "frequency": "BD", "indication": "Type 2 Diabetes"},
    {"name": "Ramipril", "dose": "10mg", "frequency": "Daily", "indication": "Hypertension"}
  ],
  "medical_history": {
    "past_illnesses": ["Type 2 Diabetes (2015)", "Hypertension (2012)", "COPD (2018)"],
    "surgeries": ["None"],
    "family_history": "Father died of MI at age 60, Mother has Type 2 Diabetes"
  },
  "social_history": {
    "smoking": "Ex-smoker (quit 2020, 30 pack-years)",
    "alcohol": "Occasional (2-3 standard drinks/week)",
    "occupation": "Retired tradesman",
    "living_situation": "Lives alone, family nearby"
  },
  "vital_signs": {
    "BP": "152/88",
    "HR": 92,
    "RR": 20,
    "Temp": 37.1,
    "SpO2": 95,
    "Weight": 98,
    "Height": 175,
    "BMI": 32
  },
  "presenting_complaint": "Chest pain and shortness of breath for 2 hours",
  "clinical_scenario": "65-year-old Aboriginal male presenting to ED with 2-hour history of central chest pain radiating to left arm. Pain described as 'tight, heavy feeling' 7/10 severity. Associated shortness of breath and diaphoresis. Risk factors: T2DM, HTN, ex-smoker, family history of CAD. Denies nausea, vomiting. Pain not relieved by rest.",
  "specialty": "Emergency Medicine",
  "complexity_level": "Complex",
  "expected_diagnosis": "Acute Coronary Syndrome (NSTEMI)",
  "differential_diagnoses": ["NSTEMI", "Unstable Angina", "STEMI", "Aortic Dissection", "PE"],
  "investigation_results": {
    "ECG": "Sinus rhythm, HR 92, T-wave inversion in V4-V6, no ST elevation",
    "Troponin_I": 0.45,
    "FBC": {"Hb": 138, "WCC": 9.2, "Platelets": 245},
    "UEC": {"Na": 139, "K": 4.2, "Cr": 95, "eGFR": 68},
    "CXR": "No acute cardiopulmonary pathology"
  },
  "etg_reference": "eTG - Cardiovascular - Acute Coronary Syndromes",
  "amh_reference": "AMH - Cardiovascular - Antiplatelet therapy",
  "created_from": "manual",
  "source_osce_id": null
}
```

### Appendix B: Alembic Migration Skeleton
```python
"""add_emr_schema_6_tables_and_user_progress_extension

Revision ID: 20260216_XXXX
Revises: [previous_revision]
Create Date: 2026-02-16 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

# revision identifiers, used by Alembic.
revision = '20260216_XXXX'
down_revision = '[previous_revision]'
branch_labels = None
depends_on = None

def upgrade():
    # Table 1: emr_sessions
    op.create_table(
        'emr_sessions',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        # ... (full schema from Task 1.2)
    )

    # Table 2: mock_patients
    # ... (full schema from Task 1.3)

    # Tables 3-6: emr_soap_notes, emr_prescriptions, emr_pathology_orders, emr_validation_results
    # ... (full schemas from Tasks 1.4-1.7)

    # Extend user_progress
    # ... (17 columns from Task 1.8)

    # Indexes (CONCURRENTLY)
    # ... (all indexes from Task 1.9)

def downgrade():
    # Drop indexes first
    # Drop tables in reverse dependency order
    # Remove columns from user_progress
    pass
```

### Appendix C: Error Codes
| Code | Message | Description | Resolution |
|------|---------|-------------|------------|
| E_MIG_001 | Table already exists | EMR table exists from previous migration | Run `alembic downgrade -1` first |
| E_MIG_002 | Foreign key violation | Invalid user_id or osce_id | Verify referenced records exist |
| E_MIG_003 | CHECK constraint failed | Invalid value (e.g., repeats >5) | Fix data before migration |
| E_MIG_004 | Index creation timeout | CONCURRENTLY took >5 min | Retry during low-traffic period |

### Appendix D: Related PRDs
- **Blocks**:
  - PRD_BACKEND_002_EMR_SESSION_API (needs tables)
  - PRD_BACKEND_003_EMR_VALIDATION_API (needs tables)
  - PRD_BACKEND_004_OSCE_EMR_CONVERTER (needs mock_patients table)
  - All frontend PRDs (need backend data layer)
- **Depends On**: None (foundation task)
- **Related**:
  - Phase 0.3 Database Optimization (indexes and triggers pattern)

---

**Document Status**: Draft
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: Pending
**Version**: 1.0
