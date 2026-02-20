# PRD_AI_OSCE_008_CONTENT_CREATION

**PRD ID**: PRD_AI_OSCE_008_CONTENT_CREATION
**Category**: Content Creation
**Priority**: P1-High
**Estimated Effort**: 80-100 hours
**Dependencies**: PRD_AI_OSCE_001 (Database), PRD_AI_OSCE_002 (AI Integration)
**Status**: Not Started

---

## R - REQUEST (What & Why)

### User Story
**As a** medical educator and content creator
**I want** 360 diverse, clinically accurate patient personas with emotional intelligence
**So that** AMC Clinical Exam students have unlimited, realistic OSCE practice scenarios covering all specialties, difficulty levels, and cultural contexts

### Business Context

The AI OSCE simulation system requires a comprehensive library of patient personas to be effective as an exam preparation tool. Currently, the platform has 140+ static OSCE scenarios for reference/study, but the new AI simulation system needs interactive, emotionally intelligent personas that:

1. **Respond dynamically** to student communication style (not scripted)
2. **Progressively disclose symptoms** based on natural conversation flow
3. **Exhibit emotional state changes** (anxious → trusting, or withdrawn if mishandled)
4. **Align with AMC Clinical Examination blueprint** across 8 core specialties
5. **Represent Australian clinical context** (eTG guidelines, AMH medications, cultural diversity)

**Target**: 360 patient personas (45 per specialty × 8 specialties)

**Why this matters**:
- AMC Clinical Exam has 16 stations covering diverse presentations
- Students need exposure to foundation, intermediate, and advanced cases
- Cultural competency is tested (Aboriginal/TSI, CALD patients)
- Emotional intelligence is critical (patient rapport, empathy, trust-building)
- Unlimited practice is only possible with large, diverse persona library

### Success Metrics

- **Metric 1: Clinical Accuracy** - 100% of personas validated by ≥2 expert clinicians (FRACP, FACRRM, or equivalent)
- **Metric 2: Cultural Representation** - 3.3% Aboriginal/Torres Strait Islander personas (12 of 360), balanced CALD representation
- **Metric 3: Difficulty Distribution** - 120 foundation, 180 intermediate, 60 advanced personas (33%/50%/17% split)
- **Metric 4: RAG Integration** - 100% of personas linked to eTG/AMH/AMC Handbook references
- **Metric 5: Emotional Intelligence** - All personas have 6-state emotional state machine with clear triggers
- **Metric 6: Progressive Disclosure** - Each persona has 8-12 question scenarios with natural symptom revelation flow

### Scope

**In Scope**:
- 360 patient personas across 8 specialties (Cardiology, Respiratory, Gastroenterology, Neurology, Endocrinology, Psychiatry, Musculoskeletal, Emergency Medicine)
- Each persona includes:
  - Demographics (age, gender, cultural background, occupation)
  - Chief complaint and opening statement
  - Progressive disclosure script (8-12 question scenarios)
  - Emotional profile with 6-state machine (ANXIOUS_GUARDED → CAUTIOUSLY_OPEN → TRUSTING → FULLY_COOPERATIVE / WITHDRAWN / UPSET)
  - RAG query hints (eTG chapters, AMH drug references, AMC Handbook sections)
  - Expected management and red flags
  - AMC rubric hints (what good students should demonstrate)
- Cultural diversity requirements (Aboriginal/TSI 3.3%, CALD representation)
- Expert validation workflow (≥2 clinicians per persona)
- Content versioning system (evidence-based updates)

**Out of Scope** (Future Iterations):
- Pediatric personas (AMC Clinical Exam is adults only)
- Non-Australian medical contexts (US, UK, European guidelines)
- Procedural skill stations (suturing, catheterization - these aren't conversational)
- Advanced specialty exams (e.g., FRACP Part 2 Written - this is AMC level)
- Automated persona generation via LLM (Phase 1 is manual curation with expert oversight)

---

## A - ARCHITECTURE (How)

### Technical Approach

**Content Creation Pipeline**:
```
Template Design → Manual Drafting → Expert Review → RAG Validation → Database Import → QA Testing → Publish
```

**Quality Assurance Workflow**:
1. **Template Creation** (1 persona): Establish gold standard with all required fields
2. **Batch Drafting** (Specialty-based): Create 45 personas per specialty using template
3. **Clinical Review** (Per Persona): ≥2 expert clinicians validate accuracy
4. **Cultural Audit** (Per Batch): Ensure 3.3% Aboriginal/TSI, balanced CALD representation
5. **RAG Integration Check** (Automated): Verify all personas link to eTG/AMH references
6. **Emotional State Testing** (Sample): Test 10 personas for state machine transitions
7. **Database Import** (Migration): Insert validated personas into `patient_personas` table
8. **End-to-End QA** (Live Testing): Students interact with 20 sample personas, feedback collected

### System Design

#### Content Structure

```
360 Patient Personas
├── Cardiology (45)
│   ├── Foundation (15)
│   │   ├── Stable angina
│   │   ├── Hypertension review
│   │   ├── Palpitations (benign)
│   │   └── ...
│   ├── Intermediate (22)
│   │   ├── Acute coronary syndrome
│   │   ├── Heart failure exacerbation
│   │   ├── Atrial fibrillation
│   │   └── ...
│   └── Advanced (8)
│       ├── Atypical MI presentation (diabetic)
│       ├── Aortic dissection
│       └── ...
├── Respiratory (45)
│   ├── Foundation (15)
│   ├── Intermediate (22)
│   └── Advanced (8)
├── [6 more specialties following same structure]
└── Emergency Medicine (45)
    ├── Foundation (15)
    ├── Intermediate (22)
    └── Advanced (8)
```

#### Persona Template (JSON Structure)

```json
{
  "persona_code": "CARD-001-CHEST-PAIN",
  "name": "David Nguyen",
  "age": 58,
  "gender": "Male",
  "occupation": "Construction site manager",
  "cultural_background": "Vietnamese Australian",
  "preferred_language": "English (Vietnamese spoken at home)",

  "specialty": "Cardiology",
  "difficulty_level": "intermediate",
  "chief_complaint": "Chest pain",
  "opening_statement": "I've been having this terrible chest pain for the past 2 hours. It's really scary.",

  "progressive_disclosure": {
    "immediate": [
      "Chest pain started 2 hours ago",
      "Pain radiates to left arm"
    ],
    "when_asked_onset": "Started after climbing stairs at work site",
    "when_asked_character": "Crushing pressure, feels like elephant on chest",
    "when_asked_severity": "8 out of 10, worst pain I've ever had",
    "when_asked_duration": "Constant for 2 hours, not getting better",
    "when_asked_relieving_factors": "Tried resting, didn't help. Took some paracetamol at home, no change",
    "when_asked_aggravating_factors": "Moving around makes it slightly worse",
    "when_asked_associated_symptoms": "Feeling sweaty, bit nauseated, short of breath",
    "when_asked_previous_episodes": "Had some chest tightness 6 months ago but ignored it",
    "when_asked_medical_history": "Type 2 diabetes for 10 years, high cholesterol",
    "when_asked_medications": "Metformin 1000mg twice daily, atorvastatin 40mg at night",
    "when_asked_family_history": "Father died of heart attack at 55",
    "when_asked_social_history": "Smoke 10 cigarettes a day for 20 years, drink 2-3 beers on weekends"
  },

  "emotional_profile": {
    "baseline_state": "ANXIOUS_GUARDED",
    "pain_level": 8,
    "anxiety_level": 7,
    "trust_threshold": 3,
    "empathy_responses": {
      "student_shows_concern": "CAUTIOUSLY_OPEN",
      "student_rushes_questions": "WITHDRAWN",
      "student_explains_clearly": "TRUSTING",
      "student_dismissive": "UPSET"
    },
    "state_transitions": [
      {
        "from": "ANXIOUS_GUARDED",
        "to": "CAUTIOUSLY_OPEN",
        "trigger": "Student shows empathy, asks open questions like 'That must be frightening'"
      },
      {
        "from": "CAUTIOUSLY_OPEN",
        "to": "TRUSTING",
        "trigger": "Student addresses pain, explains examination plan clearly"
      },
      {
        "from": "TRUSTING",
        "to": "FULLY_COOPERATIVE",
        "trigger": "Student demonstrates clinical competence, involves patient in decision-making"
      },
      {
        "from": "ANXIOUS_GUARDED",
        "to": "WITHDRAWN",
        "trigger": "Student interrupts frequently, uses medical jargon without explanation"
      },
      {
        "from": "WITHDRAWN",
        "to": "UPSET",
        "trigger": "Student dismisses concerns, appears rushed or distracted"
      }
    ]
  },

  "rag_query_hints": [
    "acute coronary syndrome",
    "STEMI management",
    "eTG cardiovascular chapter 3",
    "AMH aspirin contraindications",
    "AMC handbook cardiovascular emergencies"
  ],

  "key_differentials": [
    "STEMI (most likely)",
    "Unstable angina",
    "Pulmonary embolism",
    "Aortic dissection",
    "Gastroesophageal reflux (unlikely given severity)"
  ],

  "critical_actions": [
    "ECG within 10 minutes",
    "Aspirin 300mg stat (chewed)",
    "GTN spray sublingual",
    "IV access, bloods (troponin, FBC, UEC)",
    "Call cardiology/activate cath lab",
    "Oxygen if SpO2 <94%",
    "Morphine 2.5-5mg IV for pain"
  ],

  "red_flags": [
    "Crushing chest pain >20 minutes",
    "Radiation to left arm",
    "Sweating, nausea, shortness of breath",
    "Diabetes (silent MI risk)",
    "Strong family history of MI",
    "Current smoker"
  ],

  "expected_management": {
    "communication": [
      "Acknowledge severity and patient's fear",
      "Explain this is a medical emergency",
      "Reassure that help is available",
      "Explain each step clearly (ECG, blood tests, etc.)",
      "Involve patient in consent for treatment"
    ],
    "clinical_reasoning": [
      "Recognize ACS pattern (chest pain + radiation + sweating)",
      "Identify risk factors (diabetes, smoking, family history)",
      "Prioritize urgent ECG and troponin",
      "Consider differential diagnoses but act on most likely (ACS)"
    ],
    "information_gathering": [
      "SOCRATES pain assessment",
      "Cardiac risk factors (diabetes, hypertension, smoking, family history)",
      "Medication history (especially anticoagulants, diabetes meds)",
      "Social history (smoking, alcohol)"
    ],
    "management": [
      "Immediate: ECG, aspirin 300mg, GTN spray",
      "Short-term: IV access, bloods, cardiology consult",
      "Long-term discussion: Explain likely admission, possible angiography"
    ],
    "professionalism": [
      "Work efficiently but calmly (don't panic patient)",
      "Maintain eye contact and empathetic tone",
      "Explain medical terms (e.g., 'ECG is a heart tracing')",
      "Respect cultural background (offer interpreter if needed)"
    ]
  },

  "amc_blueprint_area": "Cardiovascular - Acute Coronary Syndromes",
  "amc_competencies": [
    "Clinical reasoning in emergency presentations",
    "Communication with anxious patients",
    "Management of acute cardiac chest pain",
    "Risk assessment and urgent referral"
  ],

  "estimated_pass_rate": 67.5,
  "version": 1,
  "is_active": true
}
```

### Data Flow

```
Expert Clinician (Manual Drafting)
    ↓
JSON Persona File (Template-based)
    ↓
Clinical Review (≥2 experts validate)
    ↓
Cultural Diversity Audit (3.3% Aboriginal/TSI check)
    ↓
RAG Validation (Link to eTG/AMH references)
    ↓
PostgreSQL Import (`patient_personas` table)
    ↓
QA Testing (Students interact, feedback collected)
    ↓
Production Deployment (Available for all students)
```

### Database Schema (from PRD_001)

```sql
CREATE TABLE patient_personas (
    persona_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    persona_code VARCHAR(20) UNIQUE NOT NULL,

    name VARCHAR(100) NOT NULL,
    age INT NOT NULL CHECK (age BETWEEN 18 AND 95),
    gender VARCHAR(20) NOT NULL,
    occupation VARCHAR(100),
    cultural_background VARCHAR(100),
    preferred_language VARCHAR(50) DEFAULT 'English',

    specialty VARCHAR(50) NOT NULL,
    chief_complaint TEXT NOT NULL,
    opening_statement TEXT NOT NULL,

    symptoms JSONB NOT NULL,
    medical_history JSONB NOT NULL,
    emotional_profile JSONB NOT NULL,

    rag_query_hints TEXT[],
    key_differentials TEXT[],
    critical_actions TEXT[],

    difficulty_level VARCHAR(20) NOT NULL CHECK (difficulty_level IN ('foundation', 'intermediate', 'advanced')),
    estimated_pass_rate DECIMAL(3,1),

    amc_blueprint_area VARCHAR(100),
    amc_competencies TEXT[],

    created_by UUID REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT NOW(),
    validated_by UUID REFERENCES users(user_id),
    validated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1
);
```

### Technology Stack

- **Content Format**: JSON files (one per persona, 360 total)
- **Version Control**: Git repository for persona library
- **Validation Tools**: Python scripts (Pydantic schemas for JSON validation)
- **Database Import**: Alembic migration + Python import script
- **Expert Review Platform**: Google Sheets or Airtable (collaborative review)
- **Cultural Audit**: Python script to validate 3.3% Aboriginal/TSI representation
- **RAG Validation**: Python script to verify eTG/AMH references exist in Qdrant vector DB

### Integration Points

- **Integrates with**: PRD_001 Database (`patient_personas` table), PRD_002 AI Integration (RAG system)
- **Consumed by**: PRD_005 Frontend (persona browser), PRD_003 WebSocket (OSCE sessions)
- **Depends on**: Expert clinicians (FRACP, FACRRM), cultural advisors (Aboriginal/TSI health)

### Security Considerations

- [ ] No PHI (Protected Health Information) - all personas are fictional
- [ ] Expert validator identities stored securely (`validated_by` references `users` table)
- [ ] Version control for content updates (audit trail of changes)
- [ ] Cultural sensitivity review (Aboriginal/TSI personas reviewed by Indigenous health experts)
- [ ] No hardcoded credentials in import scripts (use Vault for database access)

### Performance Requirements

- **Import Speed**: 360 personas imported in <5 minutes (PostgreSQL bulk insert)
- **Search Performance**: Persona filtering by specialty/difficulty <100ms (indexed queries)
- **RAG Validation**: All 360 personas validated against Qdrant in <10 minutes

---

## L - LOOP (Iterative Development)

### Phase 1: Foundation Personas (40% of effort, 2 weeks)

**Goal**: Create 120 foundation-level personas (15 per specialty × 8 specialties)

**Tasks**:
1. **Task 1.1**: Design persona template (JSON schema) - 2 hours
2. **Task 1.2**: Create gold standard persona (Cardiology foundation, expert-reviewed) - 3 hours
3. **Task 1.3**: Draft Cardiology foundation personas (15 total) - 8 hours
4. **Task 1.4**: Draft Respiratory foundation personas (15 total) - 8 hours
5. **Task 1.5**: Draft Gastroenterology foundation personas (15 total) - 8 hours
6. **Task 1.6**: Draft Neurology foundation personas (15 total) - 8 hours
7. **Task 1.7**: Draft Endocrinology foundation personas (15 total) - 8 hours
8. **Task 1.8**: Draft Psychiatry foundation personas (15 total) - 8 hours
9. **Task 1.9**: Draft Musculoskeletal foundation personas (15 total) - 8 hours
10. **Task 1.10**: Draft Emergency Medicine foundation personas (15 total) - 8 hours
11. **Task 1.11**: Expert clinical review (≥2 reviewers per persona, 120 personas) - 16 hours
12. **Task 1.12**: Cultural diversity audit (ensure 3.3% Aboriginal/TSI in foundation set) - 2 hours

**Total Phase 1 Effort**: 87 hours

**Validation Gate**:
- [ ] 120 foundation personas created (15 per specialty)
- [ ] 100% expert validated (≥2 clinicians per persona)
- [ ] Cultural diversity: 4 Aboriginal/TSI personas in foundation set (3.3% of 120)
- [ ] All personas have complete progressive disclosure (8-12 questions)
- [ ] All personas have 6-state emotional state machine
- [ ] All personas linked to eTG/AMH references (RAG query hints present)
- [ ] JSON schema validation passes (Pydantic)

---

### Phase 2: Intermediate Personas (50% of effort, 3 weeks)

**Goal**: Create 180 intermediate-level personas (22 per specialty × 8 specialties)

**Tasks**:
1. **Task 2.1**: Draft Cardiology intermediate personas (22 total) - 12 hours
2. **Task 2.2**: Draft Respiratory intermediate personas (22 total) - 12 hours
3. **Task 2.3**: Draft Gastroenterology intermediate personas (22 total) - 12 hours
4. **Task 2.4**: Draft Neurology intermediate personas (22 total) - 12 hours
5. **Task 2.5**: Draft Endocrinology intermediate personas (22 total) - 12 hours
6. **Task 2.6**: Draft Psychiatry intermediate personas (22 total) - 12 hours
7. **Task 2.7**: Draft Musculoskeletal intermediate personas (22 total) - 12 hours
8. **Task 2.8**: Draft Emergency Medicine intermediate personas (22 total) - 12 hours
9. **Task 2.9**: Expert clinical review (≥2 reviewers per persona, 180 personas) - 24 hours
10. **Task 2.10**: Cultural diversity audit (ensure 3.3% Aboriginal/TSI in intermediate set) - 2 hours

**Total Phase 2 Effort**: 122 hours

**Validation Gate**:
- [ ] 180 intermediate personas created (22 per specialty)
- [ ] 100% expert validated (≥2 clinicians per persona)
- [ ] Cultural diversity: 6 Aboriginal/TSI personas in intermediate set (3.3% of 180)
- [ ] All personas have complex progressive disclosure (multiple DDx paths)
- [ ] Emotional state machines tested (10 sample personas validated for state transitions)
- [ ] RAG integration validated (all eTG/AMH references exist in Qdrant)

---

### Phase 3: Advanced Personas (10% of effort, 1 week)

**Goal**: Create 60 advanced-level personas (8 per specialty × 8 specialties)

**Tasks**:
1. **Task 3.1**: Draft Cardiology advanced personas (8 total) - 5 hours
2. **Task 3.2**: Draft Respiratory advanced personas (8 total) - 5 hours
3. **Task 3.3**: Draft Gastroenterology advanced personas (8 total) - 5 hours
4. **Task 3.4**: Draft Neurology advanced personas (8 total) - 5 hours
5. **Task 3.5**: Draft Endocrinology advanced personas (8 total) - 5 hours
6. **Task 3.6**: Draft Psychiatry advanced personas (8 total) - 5 hours
7. **Task 3.7**: Draft Musculoskeletal advanced personas (8 total) - 5 hours
8. **Task 3.8**: Draft Emergency Medicine advanced personas (8 total) - 5 hours
9. **Task 3.9**: Expert clinical review (≥2 reviewers per persona, 60 personas) - 8 hours
10. **Task 3.10**: Cultural diversity audit (ensure 3.3% Aboriginal/TSI in advanced set) - 1 hour
11. **Task 3.11**: Final cultural diversity validation (12 Aboriginal/TSI personas total across all 360) - 2 hours
12. **Task 3.12**: Database import (all 360 personas to PostgreSQL) - 3 hours
13. **Task 3.13**: End-to-end QA testing (students interact with 20 sample personas) - 8 hours

**Total Phase 3 Effort**: 57 hours

**Validation Gate**:
- [ ] 60 advanced personas created (8 per specialty)
- [ ] 100% expert validated (≥2 clinicians per persona)
- [ ] Cultural diversity: 2 Aboriginal/TSI personas in advanced set (3.3% of 60)
- [ ] Total cultural diversity: 12 Aboriginal/TSI personas across all 360 (3.3%)
- [ ] All 360 personas imported to `patient_personas` table
- [ ] Database constraints pass (specialty, difficulty_level, age ranges)
- [ ] E2E testing: 20 sample personas tested with students, feedback collected
- [ ] Performance benchmarks met (persona search <100ms, import <5 min)

---

## P - PLAN (Detailed Implementation)

### Task Breakdown (1-2 hour chunks)

#### Phase 1 Tasks (Foundation Personas)

**Task 1.1: Design Persona Template (JSON Schema)**
- **Effort**: 2 hours
- **Owner**: Content Lead + Backend Engineer
- **Deliverable**: `persona_template.json` with Pydantic validation schema
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] JSON schema includes all required fields (demographics, progressive disclosure, emotional profile, RAG hints)
  - [ ] Pydantic validator enforces data types (age 18-95, difficulty in ['foundation', 'intermediate', 'advanced'])
  - [ ] Example persona passes validation (gold standard for future personas)

**Task 1.2: Create Gold Standard Persona (Cardiology Foundation)**
- **Effort**: 3 hours
- **Owner**: Expert Cardiologist + Content Lead
- **Deliverable**: `CARD-001-CHEST-PAIN.json` (fully validated)
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] All template fields completed (opening statement, 8-12 progressive disclosure questions)
  - [ ] Emotional state machine defined (6 states with clear triggers)
  - [ ] RAG query hints link to eTG Cardiovascular Chapter, AMH aspirin entry
  - [ ] Reviewed by ≥2 expert clinicians (FRACP or equivalent)
  - [ ] Australian medical terminology used (paracetamol, GTN spray, 000 emergency)

**Task 1.3: Draft Cardiology Foundation Personas (15 total)**
- **Effort**: 8 hours
- **Owner**: Content Team (Cardiologist oversight)
- **Deliverable**: 15 JSON files (`CARD-001` to `CARD-015`)
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] 15 distinct presentations (stable angina, palpitations, hypertension, syncope, etc.)
  - [ ] Difficulty level: Foundation (straightforward presentations, AMC Part 1 knowledge sufficient)
  - [ ] 1-2 Aboriginal/TSI personas (cultural background specified)
  - [ ] All personas pass Pydantic validation

**Task 1.4-1.10: Draft Remaining Specialties Foundation Personas**
- **Effort**: 8 hours each (7 specialties × 8 hours = 56 hours total)
- **Owner**: Content Team (Specialist oversight per specialty)
- **Deliverable**: 105 JSON files (15 per specialty × 7 specialties)
- **Dependencies**: Task 1.3 (follow same template)
- **Acceptance Criteria**:
  - [ ] Each specialty has 15 foundation personas
  - [ ] Cultural diversity: 2-3 Aboriginal/TSI personas across all foundation sets
  - [ ] All personas validated by Pydantic schema

**Task 1.11: Expert Clinical Review (120 Foundation Personas)**
- **Effort**: 16 hours (120 personas ÷ 7.5 personas/hour)
- **Owner**: Panel of ≥2 Expert Clinicians per Persona
- **Deliverable**: Review spreadsheet with approval signatures
- **Dependencies**: Tasks 1.3-1.10
- **Acceptance Criteria**:
  - [ ] Every persona reviewed by ≥2 clinicians (FRACP, FACRRM, or equivalent)
  - [ ] Clinical accuracy validated (symptoms, red flags, expected management align with eTG)
  - [ ] Progressive disclosure flow tested (does symptom revelation feel natural?)
  - [ ] Any errors corrected and re-reviewed

**Task 1.12: Cultural Diversity Audit (Foundation Set)**
- **Effort**: 2 hours
- **Owner**: Cultural Advisor + Content Lead
- **Deliverable**: Cultural diversity report (breakdown by cultural background)
- **Dependencies**: Task 1.11
- **Acceptance Criteria**:
  - [ ] 3.3% Aboriginal/Torres Strait Islander representation (4 of 120 foundation personas)
  - [ ] Balanced CALD representation (Vietnamese, Chinese, Indian, Middle Eastern, etc.)
  - [ ] Aboriginal/TSI personas reviewed by Indigenous health expert
  - [ ] Cultural sensitivity validated (no stereotypes, respectful presentations)

---

#### Phase 2 Tasks (Intermediate Personas)

**Task 2.1-2.8: Draft Intermediate Personas (22 per specialty × 8 specialties)**
- **Effort**: 12 hours each (8 specialties × 12 hours = 96 hours total)
- **Owner**: Content Team (Specialist oversight per specialty)
- **Deliverable**: 176 JSON files (22 per specialty × 8 specialties)
- **Dependencies**: Phase 1 complete (foundation template validated)
- **Acceptance Criteria**:
  - [ ] Each specialty has 22 intermediate personas
  - [ ] Difficulty level: Intermediate (requires clinical reasoning, AMC Clinical Exam level)
  - [ ] More complex progressive disclosure (multiple differential diagnoses, red herrings)
  - [ ] Emotional state machines more nuanced (cultural sensitivity tests)
  - [ ] 4-5 Aboriginal/TSI personas across all intermediate sets (3.3% of 180)

**Task 2.9: Expert Clinical Review (180 Intermediate Personas)**
- **Effort**: 24 hours (180 personas ÷ 7.5 personas/hour)
- **Owner**: Panel of ≥2 Expert Clinicians per Persona
- **Deliverable**: Review spreadsheet with approval signatures
- **Dependencies**: Tasks 2.1-2.8
- **Acceptance Criteria**:
  - [ ] Every persona reviewed by ≥2 clinicians
  - [ ] Intermediate-level complexity validated (not too easy, not too advanced)
  - [ ] Emotional state transitions tested (10 sample personas)
  - [ ] RAG query hints validated (all eTG/AMH references exist in Qdrant)

**Task 2.10: Cultural Diversity Audit (Intermediate Set)**
- **Effort**: 2 hours
- **Owner**: Cultural Advisor + Content Lead
- **Deliverable**: Cultural diversity report (intermediate set)
- **Dependencies**: Task 2.9
- **Acceptance Criteria**:
  - [ ] 3.3% Aboriginal/TSI representation (6 of 180 intermediate personas)
  - [ ] Cumulative: 10 Aboriginal/TSI personas across foundation + intermediate (300 total)
  - [ ] Aboriginal/TSI personas reviewed by Indigenous health expert

---

#### Phase 3 Tasks (Advanced Personas + Final Validation)

**Task 3.1-3.8: Draft Advanced Personas (8 per specialty × 8 specialties)**
- **Effort**: 5 hours each (8 specialties × 5 hours = 40 hours total)
- **Owner**: Content Team (Senior Specialist oversight)
- **Deliverable**: 64 JSON files (8 per specialty × 8 specialties)
- **Dependencies**: Phase 2 complete
- **Acceptance Criteria**:
  - [ ] Each specialty has 8 advanced personas
  - [ ] Difficulty level: Advanced (atypical presentations, complex comorbidities)
  - [ ] Examples: Diabetic with silent MI, elderly patient with delirium masking stroke
  - [ ] 1-2 Aboriginal/TSI personas across all advanced sets (3.3% of 60)

**Task 3.9: Expert Clinical Review (60 Advanced Personas)**
- **Effort**: 8 hours (60 personas ÷ 7.5 personas/hour)
- **Owner**: Panel of ≥2 Expert Clinicians per Persona
- **Deliverable**: Review spreadsheet with approval signatures
- **Dependencies**: Tasks 3.1-3.8
- **Acceptance Criteria**:
  - [ ] Every persona reviewed by ≥2 clinicians
  - [ ] Advanced-level complexity validated (suitable for high-performing students)
  - [ ] No unrealistic edge cases (must be plausible AMC Clinical Exam scenarios)

**Task 3.10: Cultural Diversity Audit (Advanced Set)**
- **Effort**: 1 hour
- **Owner**: Cultural Advisor + Content Lead
- **Deliverable**: Cultural diversity report (advanced set)
- **Dependencies**: Task 3.9
- **Acceptance Criteria**:
  - [ ] 3.3% Aboriginal/TSI representation (2 of 60 advanced personas)

**Task 3.11: Final Cultural Diversity Validation (All 360 Personas)**
- **Effort**: 2 hours
- **Owner**: Cultural Advisor + Content Lead
- **Deliverable**: Final cultural diversity audit report
- **Dependencies**: Task 3.10
- **Acceptance Criteria**:
  - [ ] Total: 12 Aboriginal/Torres Strait Islander personas (3.3% of 360)
  - [ ] Balanced across specialties (not all in one specialty)
  - [ ] Balanced CALD representation (Vietnamese, Chinese, Indian, Middle Eastern, Pacific Islander, etc.)
  - [ ] All Aboriginal/TSI personas reviewed by Indigenous health expert
  - [ ] No cultural stereotypes or insensitive presentations

**Task 3.12: Database Import (All 360 Personas)**
- **Effort**: 3 hours
- **Owner**: Backend Engineer
- **Deliverable**: All personas imported to `patient_personas` table
- **Dependencies**: Task 3.11
- **Acceptance Criteria**:
  - [ ] Python import script reads 360 JSON files
  - [ ] Pydantic validation passes for all personas
  - [ ] Bulk insert to PostgreSQL (one transaction)
  - [ ] All database constraints satisfied (specialty, difficulty_level, age ranges)
  - [ ] Import completes in <5 minutes
  - [ ] Indexes created (`specialty`, `difficulty_level`, `is_active`)

**Task 3.13: End-to-End QA Testing (20 Sample Personas)**
- **Effort**: 8 hours
- **Owner**: QA Team + Student Volunteers
- **Deliverable**: QA report with student feedback
- **Dependencies**: Task 3.12
- **Acceptance Criteria**:
  - [ ] 20 personas tested live (students interact with AI Patient)
  - [ ] Emotional state transitions validated (do personas respond naturally?)
  - [ ] Progressive disclosure flow tested (symptoms revealed appropriately)
  - [ ] RAG integration tested (AI Patient references eTG/AMH correctly)
  - [ ] Student feedback collected (realism score ≥4/5)
  - [ ] Any issues documented and personas updated

---

### Dependency Graph

```
Task 1.1 (Template Design)
    ↓
Task 1.2 (Gold Standard Persona)
    ↓
Tasks 1.3-1.10 (Foundation Personas - Parallel)
    ↓
Task 1.11 (Expert Review - Foundation)
    ↓
Task 1.12 (Cultural Audit - Foundation)
    ↓
PHASE 1 VALIDATION GATE
    ↓
Tasks 2.1-2.8 (Intermediate Personas - Parallel)
    ↓
Task 2.9 (Expert Review - Intermediate)
    ↓
Task 2.10 (Cultural Audit - Intermediate)
    ↓
PHASE 2 VALIDATION GATE
    ↓
Tasks 3.1-3.8 (Advanced Personas - Parallel)
    ↓
Task 3.9 (Expert Review - Advanced)
    ↓
Task 3.10 (Cultural Audit - Advanced)
    ↓
Task 3.11 (Final Cultural Diversity Validation)
    ↓
Task 3.12 (Database Import)
    ↓
Task 3.13 (E2E QA Testing)
    ↓
PHASE 3 VALIDATION GATE
    ↓
PRODUCTION RELEASE
```

---

### Resource Allocation

| Role | Effort (hours) | Tasks |
|------|----------------|-------|
| Content Lead | 20 hours | Template design, coordination, QA |
| Expert Clinicians (Panel of 10+) | 48 hours | Clinical review (360 personas × 2 reviewers) |
| Content Team (Medical Writers) | 150 hours | Drafting 360 personas |
| Cultural Advisor | 7 hours | Cultural diversity audits |
| Indigenous Health Expert | 5 hours | Aboriginal/TSI persona review |
| Backend Engineer | 5 hours | Database import script, Pydantic schemas |
| QA Team | 8 hours | End-to-end testing |
| **TOTAL** | **243 hours** | **(Revised estimate: 80-100 hours assumes parallel work and streamlined review)** |

---

### Timeline (6 Weeks)

| Week | Phase | Tasks | Deliverable |
|------|-------|-------|-------------|
| Week 1 | Phase 1 | Template + Gold Standard + Cardiology/Respiratory foundation | 30 foundation personas |
| Week 2 | Phase 1 | Remaining 6 specialties foundation + Expert review | 120 foundation personas validated |
| Week 3 | Phase 2 | Cardiology/Respiratory/Gastro/Neuro intermediate | 88 intermediate personas |
| Week 4 | Phase 2 | Endo/Psych/MSK/EM intermediate + Expert review | 180 intermediate personas validated |
| Week 5 | Phase 3 | All 8 specialties advanced + Expert review | 60 advanced personas validated |
| Week 6 | Phase 3 | Final cultural audit + Database import + QA testing | 360 personas live in production |

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] 360 patient personas created (45 per specialty × 8 specialties)
- [ ] Difficulty distribution: 120 foundation (33%), 180 intermediate (50%), 60 advanced (17%)
- [ ] All personas have complete progressive disclosure (8-12 question scenarios)
- [ ] All personas have 6-state emotional state machine (ANXIOUS_GUARDED → CAUTIOUSLY_OPEN → TRUSTING → FULLY_COOPERATIVE / WITHDRAWN / UPSET)
- [ ] All personas linked to RAG system (eTG/AMH/AMC Handbook query hints)
- [ ] All personas have expected management and red flags defined
- [ ] All personas align with AMC Clinical Examination blueprint

#### Quality Requirements
- [ ] **Expert Validation**: 100% of personas reviewed by ≥2 clinicians (FRACP, FACRRM, or equivalent)
- [ ] **Clinical Accuracy**: All symptoms, differentials, and management align with eTG/AMH guidelines
- [ ] **Cultural Diversity**: 3.3% Aboriginal/Torres Strait Islander representation (12 of 360 personas)
- [ ] **CALD Representation**: Balanced cultural backgrounds (Vietnamese, Chinese, Indian, Middle Eastern, Pacific Islander, etc.)
- [ ] **Cultural Sensitivity**: All Aboriginal/TSI personas reviewed by Indigenous health expert
- [ ] **JSON Validation**: 100% of personas pass Pydantic schema validation
- [ ] **Database Import**: All 360 personas successfully imported to `patient_personas` table

#### Performance Requirements
- [ ] **Import Speed**: All 360 personas imported in <5 minutes (PostgreSQL bulk insert)
- [ ] **Search Performance**: Persona filtering by specialty/difficulty <100ms (indexed queries)
- [ ] **RAG Validation**: All eTG/AMH references exist in Qdrant vector DB (<10 minutes validation)

#### Security Requirements
- [ ] **No PHI**: All personas are fictional (no real patient data)
- [ ] **Expert Privacy**: Validator identities stored securely (`validated_by` references `users` table)
- [ ] **Version Control**: All JSON files tracked in Git (audit trail of changes)
- [ ] **No Hardcoded Credentials**: Import scripts use Vault for database access

#### Australian Medical Compliance
- [ ] **Terminology**: Australian drug names (paracetamol not acetaminophen, salbutamol not albuterol, adrenaline not epinephrine)
- [ ] **Guidelines**: All management aligned with eTG (Therapeutic Guidelines) and AMH (Australian Medicines Handbook)
- [ ] **Standards**: Meets AHPRA clinical documentation standards
- [ ] **Units**: SI units only (mmol/L, g/L, °C - not mg/dL, °F)
- [ ] **Emergency**: 000 (not 911)
- [ ] **AMC Alignment**: All personas suitable for AMC Clinical Examination practice (not ICRP)

---

### Testing Requirements

#### Unit Tests (Pydantic Validation)

```python
# Example test structure
def test_persona_json_schema_validation():
    """Test all 360 personas pass Pydantic schema"""
    persona_files = glob.glob("personas/*.json")
    assert len(persona_files) == 360

    for file in persona_files:
        persona = PersonaSchema.parse_file(file)
        assert persona.age >= 18 and persona.age <= 95
        assert persona.difficulty_level in ['foundation', 'intermediate', 'advanced']
        assert len(persona.progressive_disclosure) >= 8
        assert len(persona.emotional_profile.state_transitions) == 6

def test_cultural_diversity_representation():
    """Test 3.3% Aboriginal/TSI representation"""
    personas = load_all_personas()
    aboriginal_tsi = [p for p in personas if 'Aboriginal' in p.cultural_background or 'Torres Strait' in p.cultural_background]
    assert len(aboriginal_tsi) == 12  # 3.3% of 360

def test_difficulty_distribution():
    """Test 33%/50%/17% difficulty split"""
    personas = load_all_personas()
    foundation = [p for p in personas if p.difficulty_level == 'foundation']
    intermediate = [p for p in personas if p.difficulty_level == 'intermediate']
    advanced = [p for p in personas if p.difficulty_level == 'advanced']

    assert len(foundation) == 120
    assert len(intermediate) == 180
    assert len(advanced) == 60
```

**Minimum Test Cases**:
- [ ] JSON schema validation (all 360 personas pass Pydantic)
- [ ] Cultural diversity (12 Aboriginal/TSI personas)
- [ ] Difficulty distribution (120/180/60 split)
- [ ] Specialty distribution (45 per specialty × 8 specialties)
- [ ] Progressive disclosure completeness (8-12 questions per persona)
- [ ] Emotional state machine structure (6 states, clear triggers)

#### Integration Tests

- [ ] **Database Import**: Import all 360 personas to PostgreSQL, verify constraints
- [ ] **RAG Integration**: Verify all eTG/AMH query hints exist in Qdrant vector DB
- [ ] **Persona Search API**: Filter by specialty/difficulty, verify <100ms response time
- [ ] **Version Control**: Verify all JSON files tracked in Git, commit history visible

#### E2E Tests (Student Interaction)

- [ ] **Test Scenario 1**: Student selects foundation cardiology persona, completes 8-minute session, receives AI Patient responses
- [ ] **Test Scenario 2**: Student shows empathy, emotional state transitions from ANXIOUS_GUARDED → CAUTIOUSLY_OPEN → TRUSTING
- [ ] **Test Scenario 3**: Student rushes questions, emotional state transitions to WITHDRAWN
- [ ] **Test Scenario 4**: Student asks about family history, progressive disclosure reveals "Father died of MI age 55"
- [ ] **Test Scenario 5**: Mock exam mode (16 sequential stations), verify persona auto-selection across all 8 specialties

---

### Documentation Deliverables

#### Code Documentation
- [ ] **Pydantic Schema**: `persona_schema.py` with docstrings explaining all fields
- [ ] **Import Script**: `import_personas.py` with usage instructions
- [ ] **Validation Scripts**: `validate_cultural_diversity.py`, `validate_rag_references.py`
- [ ] **README**: Setup instructions for persona library repository

#### Architecture Documentation
- [ ] **Persona Catalog**: Master spreadsheet listing all 360 personas (specialty, difficulty, cultural background, expert reviewers)
- [ ] **Cultural Diversity Report**: Breakdown of Aboriginal/TSI and CALD representation
- [ ] **RAG Reference Index**: Mapping of personas to eTG/AMH/AMC Handbook sections
- [ ] **Expert Reviewer List**: Panel of clinicians who validated personas (with credentials)

#### User Documentation
- [ ] **Content Creation Guide**: How to draft new personas (template usage, quality standards)
- [ ] **Review Guidelines**: How expert clinicians should validate personas (clinical accuracy checklist)
- [ ] **Cultural Sensitivity Guidelines**: How to create respectful Aboriginal/TSI and CALD personas
- [ ] **Versioning Guide**: How to update personas when eTG/AMH guidelines change

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All 360 personas pass Pydantic validation (100% pass rate)
- [ ] Cultural diversity validated (12 Aboriginal/TSI personas, balanced CALD)
- [ ] Expert review complete (≥2 clinicians per persona, approval signatures)
- [ ] RAG references validated (all eTG/AMH references exist in Qdrant)
- [ ] Database import tested in staging (360 personas imported successfully)

#### Deployment
- [ ] Database migration executed (if `patient_personas` table schema updated)
- [ ] Import script executed (360 personas inserted to production PostgreSQL)
- [ ] Indexes created (`specialty`, `difficulty_level`, `is_active`)
- [ ] Smoke test: Frontend persona browser shows all 360 personas
- [ ] Smoke test: Select random persona, start OSCE session, verify AI Patient responds

#### Post-Deployment
- [ ] Production smoke tests pass (persona search <100ms, AI Patient responses within 3 seconds)
- [ ] Monitoring dashboards show healthy metrics (no database errors, no missing personas)
- [ ] Student feedback collected (first 50 students rate persona realism ≥4/5)
- [ ] Performance metrics within targets (search <100ms, RAG query <500ms)
- [ ] Stakeholders notified (medical educators, AMC Clinical Exam coordinators)

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ All acceptance criteria met (100%)
2. ✅ 360 personas created, expert-validated, and imported to database
3. ✅ Cultural diversity validated (12 Aboriginal/TSI personas, balanced CALD)
4. ✅ RAG integration validated (all eTG/AMH references exist in Qdrant)
5. ✅ E2E testing complete (20 sample personas tested with students, feedback ≥4/5)
6. ✅ Documentation complete (persona catalog, cultural diversity report, RAG index)
7. ✅ Production deployment successful (all personas available to students)

**Sign-off Required From**:
- [ ] PM Coordinator (overall quality, project timeline met)
- [ ] Content Lead (360 personas complete, quality standards met)
- [ ] Expert Clinical Panel (≥2 clinicians per persona approved)
- [ ] Cultural Advisor (3.3% Aboriginal/TSI representation, cultural sensitivity validated)
- [ ] Indigenous Health Expert (Aboriginal/TSI personas respectfully presented)
- [ ] Backend Engineer (database import successful, performance benchmarks met)
- [ ] QA Team (E2E testing complete, student feedback positive)

---

## 📎 Appendices

### Appendix A: Example Persona (Cardiology Foundation)

**File**: `CARD-001-CHEST-PAIN.json`

```json
{
  "persona_code": "CARD-001-CHEST-PAIN",
  "name": "David Nguyen",
  "age": 58,
  "gender": "Male",
  "occupation": "Construction site manager",
  "cultural_background": "Vietnamese Australian",
  "preferred_language": "English (Vietnamese spoken at home)",

  "specialty": "Cardiology",
  "difficulty_level": "intermediate",
  "chief_complaint": "Chest pain",
  "opening_statement": "I've been having this terrible chest pain for the past 2 hours. It's really scary.",

  "progressive_disclosure": {
    "immediate": ["Chest pain started 2 hours ago", "Pain radiates to left arm"],
    "when_asked_onset": "Started after climbing stairs at work site",
    "when_asked_character": "Crushing pressure, feels like elephant on chest",
    "when_asked_severity": "8 out of 10, worst pain I've ever had",
    "when_asked_duration": "Constant for 2 hours, not getting better",
    "when_asked_relieving_factors": "Tried resting, didn't help. Took some paracetamol at home, no change",
    "when_asked_aggravating_factors": "Moving around makes it slightly worse",
    "when_asked_associated_symptoms": "Feeling sweaty, bit nauseated, short of breath",
    "when_asked_previous_episodes": "Had some chest tightness 6 months ago but ignored it",
    "when_asked_medical_history": "Type 2 diabetes for 10 years, high cholesterol",
    "when_asked_medications": "Metformin 1000mg twice daily, atorvastatin 40mg at night",
    "when_asked_family_history": "Father died of heart attack at 55",
    "when_asked_social_history": "Smoke 10 cigarettes a day for 20 years, drink 2-3 beers on weekends"
  },

  "emotional_profile": {
    "baseline_state": "ANXIOUS_GUARDED",
    "pain_level": 8,
    "anxiety_level": 7,
    "trust_threshold": 3,
    "state_transitions": [
      {"from": "ANXIOUS_GUARDED", "to": "CAUTIOUSLY_OPEN", "trigger": "Student shows empathy"},
      {"from": "CAUTIOUSLY_OPEN", "to": "TRUSTING", "trigger": "Student explains plan clearly"},
      {"from": "TRUSTING", "to": "FULLY_COOPERATIVE", "trigger": "Student demonstrates competence"},
      {"from": "ANXIOUS_GUARDED", "to": "WITHDRAWN", "trigger": "Student interrupts frequently"},
      {"from": "WITHDRAWN", "to": "UPSET", "trigger": "Student dismisses concerns"}
    ]
  },

  "rag_query_hints": ["acute coronary syndrome", "STEMI management", "eTG cardiovascular chapter 3"],
  "key_differentials": ["STEMI", "Unstable angina", "Pulmonary embolism"],
  "critical_actions": ["ECG within 10 minutes", "Aspirin 300mg stat", "Call cardiology"],

  "amc_blueprint_area": "Cardiovascular - Acute Coronary Syndromes",
  "amc_competencies": ["Clinical reasoning", "Emergency management"],

  "estimated_pass_rate": 67.5,
  "version": 1,
  "is_active": true
}
```

### Appendix B: Specialty Breakdown (360 Personas)

| Specialty | Foundation | Intermediate | Advanced | Total |
|-----------|------------|--------------|----------|-------|
| Cardiology | 15 | 22 | 8 | 45 |
| Respiratory | 15 | 22 | 8 | 45 |
| Gastroenterology | 15 | 22 | 8 | 45 |
| Neurology | 15 | 22 | 8 | 45 |
| Endocrinology | 15 | 22 | 8 | 45 |
| Psychiatry | 15 | 22 | 8 | 45 |
| Musculoskeletal | 15 | 22 | 8 | 45 |
| Emergency Medicine | 15 | 22 | 8 | 45 |
| **TOTAL** | **120** | **180** | **60** | **360** |

### Appendix C: Cultural Diversity Targets

| Cultural Background | Target % | Target Count (of 360) |
|---------------------|----------|-----------------------|
| Aboriginal/Torres Strait Islander | 3.3% | 12 |
| Vietnamese Australian | ~5% | 18 |
| Chinese Australian | ~5% | 18 |
| Indian Australian | ~5% | 18 |
| Middle Eastern (Lebanese, Iraqi, etc.) | ~4% | 14 |
| Pacific Islander (Samoan, Tongan, etc.) | ~3% | 11 |
| European (Italian, Greek, etc.) | ~10% | 36 |
| Anglo-Australian | ~65% | 233 |
| **TOTAL** | **100%** | **360** |

### Appendix D: Expert Review Panel (Example)

| Clinician | Credentials | Specialties Reviewed | Personas Validated |
|-----------|-------------|----------------------|--------------------|
| Dr. Sarah Chen | FRACP (Cardiology) | Cardiology | 45 |
| Dr. James O'Connor | FRACP (Respiratory) | Respiratory | 45 |
| Dr. Priya Patel | FRACP (Gastro) | Gastroenterology | 45 |
| Dr. Michael Wong | FRACP (Neurology) | Neurology | 45 |
| Dr. Emily Thompson | FRACP (Endocrinology) | Endocrinology | 45 |
| Dr. David Kim | FRANZCP (Psychiatry) | Psychiatry | 45 |
| Dr. Rebecca Taylor | FACEM (Emergency) | Emergency Medicine | 45 |
| Dr. Tom Williams | FACRRM (Rheumatology) | Musculoskeletal | 45 |
| Dr. Aunty Mary Johnson | Aboriginal Health Expert | Aboriginal/TSI personas | 12 |
| Dr. Hassan Al-Masri | CALD Health Advisor | CALD personas | 50 |

### Appendix E: Related PRDs

- **Depends On**:
  - PRD_AI_OSCE_001 (Database & APIs) - `patient_personas` table must exist
  - PRD_AI_OSCE_002 (AI Integration) - RAG system must be operational for query hint validation
- **Blocks**:
  - PRD_AI_OSCE_005 (Frontend Implementation) - Persona browser needs personas to display
  - PRD_AI_OSCE_006 (Mock Exam Mode) - Mock exams need 360 personas for auto-selection
- **Related**:
  - PRD_AI_OSCE_004 (Scoring System) - Personas define expected management for scoring validation
  - PRD_AI_OSCE_007 (Testing & Validation) - Personas used for E2E testing

---

**Document Status**: Draft → Ready for Review
**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: PM Coordinator (pending)
**Version**: 1.0
