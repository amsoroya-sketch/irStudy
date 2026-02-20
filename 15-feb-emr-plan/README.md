# Epic EHR Practice System - Implementation Plan

**Project**: irStudy Medical Education Platform - EMR Practice Module
**Date**: 2026-02-15
**Status**: Planning Complete ✅ - Ready for Implementation
**Estimated Timeline**: 4 weeks (1 PM + specialist agents)

---

## 📋 Executive Summary

This folder contains comprehensive planning documents for implementing a **high-fidelity Epic EHR simulation** within the irStudy platform, enabling medical students to practice clinical documentation for the Australian AMC Clinical Examination.

**Current Completion**: ~0% (EMR components exist separately but not integrated)
**Target**: Production-ready Epic EHR Practice System with full OSCE/MCQ/video integration

---

## 📁 Planning Documents

### 1. **ARCHITECTURE.md** (44KB)
**Purpose**: Integration architecture and technology stack decisions

**Key Decisions**:
- ✅ **Unified Application** (Material-UI v7, not separate Tailwind app)
- ✅ **Full Integration** with existing OSCE/MCQ/video content
- ✅ **Claude Sonnet 4.5** for AI validation (NOT Ollama per constraints)
- ✅ **3-Layer Validation**: Zod (<50ms) → Python (<1s) → Claude AI (3-5s)
- ✅ **Reuse Existing JWT Auth** and FastAPI patterns

**Read This First**: Foundation for all other documents

---

### 2. **DATABASE_MIGRATION.md** (57KB)
**Purpose**: Complete database schema extension specification

**Contents**:
- **6 New Tables**:
  - `mock_patients` (500+ simulated patients from OSCEs)
  - `emr_sessions` (practice session tracking)
  - `emr_soap_notes` (SOAP documentation drafts)
  - `emr_prescriptions` (PBS-compliant medication orders)
  - `emr_pathology_orders` (MBS pathology requests)
  - `emr_validation_results` (3-layer AI feedback storage)
- **17 New Columns** in `user_progress` (EMR metrics)
- **Complete Alembic migration script** ready to execute
- **Performance indexes** for all query patterns
- **Australian compliance**: Medicare numbers, Aboriginal/TSI status

**Implementation Ready**: Copy migration script and run `alembic upgrade head`

---

### 3. **API_SPECIFICATION.md** (69KB)
**Purpose**: Complete RESTful API design for EMR backend

**Contents**:
- **19 Endpoints** across 5 groups:
  - Sessions: Start, update (auto-save), submit, get, list, delete
  - Patients: Random, specific, from-OSCE, list
  - Validation: SOAP note, prescription, pathology
  - Analytics: Progress, history, trends
  - Reference: PBS medications, MBS pathology, eTG guidelines
- **Pydantic Schemas** for all request/response models
- **3-Layer Validation** implementation details
- **Error Handling** with standard error response format
- **Rate Limiting**: 20 req/min for Claude AI (cost control)
- **Testing Strategy** with pytest examples

**Implementation Pattern**: Follow existing OSCE API (`backend/src/api/v1/osces.py`)

---

### 4. **INTEGRATION_STRATEGY.md** (82KB)
**Purpose**: OSCE → EMR conversion logic and cross-platform integration

**Contents**:
- **OSCE → EMR Conversion Algorithm**:
  - Parse unstructured `patient_instructions` text (NLP)
  - Extract: name, age, gender, presenting complaint, PMHx, medications
  - Generate: MRN, Medicare number, Australian address, GP details
  - Generate: Realistic vital signs based on specialty
  - Generate: Investigation results (labs, ECG, imaging)
  - Map OSCE rubric → EMR validation_criteria
- **Complete Python Implementation**:
  - `OSCEToEMRConverter` class (700+ lines)
  - `AustralianNameGenerator` (realistic names)
  - `AustralianAddressGenerator` (Sydney suburbs)
  - Batch conversion script ready to run
- **MCQ Integration**: Link medications to PBS validation
- **Video Integration**: Embed educational videos in EMR cases
- **Unified Progress Tracking**: Single dashboard for MCQ + OSCE + EMR
- **Smart Recommendations**: AI-powered learning pathway generation

**MVP Plan**: Convert 50 priority patients (cardiology, respiratory, emergency medicine) in Week 2

---

## 🎯 Implementation Roadmap

### Week 1: Foundation & Backend (Phase 1)

**Database**:
- [ ] Run Alembic migration (6 tables + 17 columns)
- [ ] Verify tables created successfully
- [ ] Add performance indexes
- [ ] Backup database

**Backend API**:
- [ ] Create `/backend/src/api/v1/emr/` directory structure
- [ ] Implement session management endpoints (start, update, submit, get)
- [ ] Implement patient endpoints (random, specific, from-OSCE)
- [ ] Create Pydantic schemas (`/backend/src/schemas/emr.py`)
- [ ] Build AI validators:
  - `agents/soap_validator.py` (Claude Sonnet 4.5 integration)
  - `agents/prescription_validator.py` (PBS compliance)
  - `agents/pathology_validator.py` (MBS validation)
- [ ] Write pytest unit tests (≥70% coverage target)

**Deliverable**: Working EMR API with 3-layer validation

---

### Week 2: Content & Conversion (Phase 2)

**OSCE → EMR Conversion**:
- [ ] Create `backend/scripts/osce_emr_converter.py`
- [ ] Create `backend/scripts/convert_osce_to_emr.py` (batch script)
- [ ] Test conversion on 5 sample OSCEs (manual verification)
- [ ] Convert 50 priority patients:
  - 20 cardiology cases
  - 15 respiratory cases
  - 15 emergency medicine cases
- [ ] Medical expert review (verify 10 random cases for accuracy)
- [ ] Populate `mock_patients` table

**Australian Reference Data**:
- [ ] Load PBS medication database (4,000+ drugs)
- [ ] Load MBS pathology item numbers
- [ ] Create Australian drug name mapping CSV

**Deliverable**: 50 realistic EMR patient cases ready for practice

---

### Week 3: Frontend & UI (Phase 3)

**Epic UI Migration** (Tailwind → Material-UI v7):
- [ ] Create `/frontend/src/components/emr/` directory
- [ ] Migrate `EpicSidebar.tsx`:
  - Tailwind classes → MUI `sx` prop
  - Framer Motion → MUI Fade/Slide transitions
  - Purple theme preserved
- [ ] Migrate `EpicPatientBanner.tsx` (demographics display)
- [ ] Create `EpicSOAPEditor.tsx`:
  - React Hook Form + Zod validation (Layer 1)
  - Auto-save every 30 seconds (PUT /sessions/{id})
  - Word count, typing WPM tracker
  - Character minimums (Subjective: 50, Objective: 30, etc.)
- [ ] Create `EpicPrescriptionPanel.tsx`:
  - PBS medication search autocomplete
  - Australian drug name validation
  - Max 5 repeats enforcement
- [ ] Create `EpicPathologyPanel.tsx`:
  - MBS item search
  - Urgency selection (routine/urgent/emergency)
- [ ] Create `EpicValidationPanel.tsx`:
  - 3-layer feedback display (red errors, yellow warnings, green insights)
  - Strengths/improvements/red flags
  - AMC rubric score breakdown

**Dashboard Integration**:
- [ ] Extend `/frontend/src/components/dashboard/DashboardPage.tsx`
- [ ] Add EMR metrics StatCards
- [ ] Create `UnifiedSpecialtyChart.tsx` (MCQ + OSCE + EMR grouped bars)
- [ ] Create `SmartRecommendations.tsx` (learning pathway suggestions)

**Deliverable**: Complete Epic EHR UI integrated into main app

---

### Week 4: Testing & Polish (Phase 4)

**3-Layer Validation Testing**:
- [ ] Test Zod validation (client-side <50ms)
- [ ] Test PBS/MBS Python validation (<1s)
- [ ] Test Claude AI validation (3-5s latency)
- [ ] Verify AMC 15-mark rubric scoring accuracy

**E2E Testing** (Playwright):
- [ ] Test complete EMR workflow:
  1. User logs in
  2. Starts EMR session (cardiology case)
  3. Types SOAP note (auto-save triggers)
  4. Adds prescription (PBS validation)
  5. Orders pathology (MBS validation)
  6. Submits session (3-layer validation)
  7. Views validation feedback
  8. Sees updated progress on dashboard
- [ ] Test all 10 specialties (1 case each)
- [ ] Test pass/fail scenarios (score ≥9/15 vs <9/15)

**Performance Testing**:
- [ ] Verify auto-save latency <200ms
- [ ] Verify Claude AI validation 3-5 seconds
- [ ] Verify patient case load <500ms
- [ ] Verify dashboard load <2 seconds
- [ ] Load test: 100 concurrent users

**Security Audit**:
- [ ] Verify JWT on all EMR endpoints
- [ ] Verify no hardcoded credentials (grep scan)
- [ ] Verify Pydantic validation on all inputs
- [ ] Verify rate limiting (Claude API: 20 req/min)

**Documentation**:
- [ ] Update API documentation (Swagger/ReDoc)
- [ ] Create user guide for EMR practice
- [ ] Document validation rules and scoring

**Deliverable**: Production-ready EMR system with 100% test pass rate

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│              irStudy Web Application                         │
│              (React 19.2 + Material-UI v7)                   │
├─────────────────────────────────────────────────────────────┤
│  Dashboard  │  MCQ  │  OSCE  │  EMR Practice (NEW)         │
└──────────────┬──────────────────────────────────────────────┘
               │ JWT Auth (existing)
               │ TanStack Query (existing)
┌──────────────▼──────────────────────────────────────────────┐
│           FastAPI Backend (Python 3.11+)                     │
├─────────────────────────────────────────────────────────────┤
│  /api/v1/mcqs/  │  /api/v1/osces/  │  /api/v1/emr/ (NEW)   │
│                 │                  │                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       AI Validators (Claude Sonnet 4.5)              │  │
│  │  - SOAPValidator (clinical reasoning)                │  │
│  │  - PrescriptionValidator (PBS compliance)            │  │
│  │  - PathologyValidator (MBS appropriateness)          │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────────┐
│                    Data Layer                                │
├─────────────────────────────────────────────────────────────┤
│  PostgreSQL 14          │  Qdrant Vector DB  │  Redis Cache │
│  - users, mcqs, osces   │  - 9,950 med chunks│  - Sessions  │
│  - mock_patients (NEW)  │  - eTG, AMH, AHPRA │  - Rate      │
│  - emr_sessions (NEW)   │                    │    limiting  │
│  - emr_soap_notes (NEW) │                    │              │
│  - 3 more tables (NEW)  │                    │              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Features

### 1. High-Fidelity Epic EHR UI
- Purple theme with icon-based navigation (Material-UI)
- Patient banner with demographics (MRN, Medicare, age, allergies)
- SOAP note editor with real-time validation
- PBS medication search with autocomplete
- MBS pathology ordering panel
- Session timer and typing metrics (WPM tracker)

### 2. 3-Layer Validation System
```
Layer 1: Zod (Client-side TypeScript)       <50ms    🔴 Red errors
         - Character minimums
         - Required fields
         - Format validation

Layer 2: Python (Server-side)               <1s      🟡 Yellow warnings
         - PBS compliance (max 5 repeats)
         - MBS appropriateness
         - Australian terminology

Layer 3: Claude AI (Clinical Reasoning)     3-5s     🟢 Green insights
         - AMC 15-mark rubric scoring
         - Strengths/improvements
         - Red flag detection
         - eTG guideline alignment
```

### 3. Australian Medical Standards Compliance
- ✅ PBS medication database (4,000+ drugs)
- ✅ MBS pathology item numbers
- ✅ Australian drug names (paracetamol not acetaminophen)
- ✅ Medicare numbers (10 digits + check digit)
- ✅ Aboriginal/Torres Strait Islander status (mandatory field)
- ✅ Emergency number 000 (not 911)
- ✅ SI units (mmol/L, µmol/L, g/L, °C)
- ✅ eTG/AMH/AHPRA guideline alignment

### 4. Full Integration
- **OSCE → EMR**: 221 OSCE scenarios converted to 500+ EMR patient cases
- **MCQ → EMR**: Medication content validates EMR prescriptions
- **Videos → EMR**: Educational videos embedded in patient cases
- **Unified Dashboard**: Single progress view for MCQ + OSCE + EMR

### 5. Smart Learning Pathways
- AI-powered recommendations based on performance
- Cross-reference learning (failed EMR → related MCQs/OSCEs/videos)
- Specialty-specific weak area identification

---

## 📊 Success Metrics

| Metric | Target | Current | Gap |
|--------|--------|---------|-----|
| **EMR Cases Available** | 50+ (MVP) | 0 | 50 needed |
| **Database Tables** | 6 new tables | 0 | Migration ready |
| **API Endpoints** | 19 endpoints | 0 | Spec complete |
| **UI Components** | 7 Epic components (MUI) | 0 (Tailwind exists) | Migration needed |
| **AI Validators** | 3 validators | 0 | Implementation needed |
| **Test Coverage** | ≥70% | 0% | TDD approach |
| **Test Pass Rate** | 100% | N/A | Zero-error policy |
| **Validation Latency** | Zod <50ms, Python <1s, AI 3-5s | N/A | Performance targets set |
| **Australian Compliance** | 90%+ | N/A | Validation rules defined |

---

## 🚀 Quick Start (Post-Planning)

### Prerequisites
- Planning documents reviewed ✅
- Constraints read (`/constraints/README.md`)
- Agent OS framework ready
- Claude API key configured (NOT Anthropic key per constraints)

### Phase 1: Database Migration (Day 1)
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# Backup database
pg_dump -h localhost -p 5433 -U postgres irstudy_medical > backup_2026_02_15.sql

# Run migration
alembic upgrade head

# Verify
psql -h localhost -p 5433 -U postgres irstudy_medical -c "\dt emr_*"
psql -h localhost -p 5433 -U postgres irstudy_medical -c "\d user_progress"
```

### Phase 2: OSCE Conversion (Day 2-3)
```bash
# Convert 50 priority patients
python scripts/convert_osce_to_emr.py \
  --priority-specialties cardiology,respiratory,emergency_medicine \
  --limit 50

# Verify
psql -h localhost -p 5433 -U postgres irstudy_medical -c "SELECT COUNT(*) FROM mock_patients;"
```

### Phase 3: Backend API (Day 4-7)
```bash
# Create API structure
mkdir -p backend/src/api/v1/emr
mkdir -p backend/agents

# Implement endpoints (follow API_SPECIFICATION.md)
# Run tests
pytest backend/tests/test_emr_api.py -v --cov=backend/src/api/v1/emr
```

### Phase 4: Frontend (Day 8-14)
```bash
cd /home/dev/Development/irStudy/frontend

# Create component structure
mkdir -p src/components/emr/epic

# Implement components (follow ARCHITECTURE.md migration strategy)
# Run tests
npm test
```

### Phase 5: E2E Testing (Day 15-21)
```bash
cd /home/dev/Development/irStudy/testing/playwright

# Run EMR workflow tests
BASE_URL=http://localhost:5173 npx playwright test tests/integration/emr/ --headed
```

---

## 🔗 Integration Points

### Existing Systems to Leverage
1. **Authentication**: `AuthContext.tsx` (JWT already working)
2. **API Client**: `axiosInstance.ts` (JWT interceptor configured)
3. **State Management**: TanStack Query (consistent pattern)
4. **Database**: PostgreSQL `irstudy_medical` (just add tables)
5. **RAG System**: Qdrant with 9,950 medical chunks (reuse for validation)
6. **Progress Tracking**: `UserProgress` model (extend with EMR columns)
7. **Dashboard**: `DashboardPage.tsx` (add EMR metrics)

### New Systems to Build
1. **EMR Backend API**: `/api/v1/emr/*` (19 endpoints)
2. **AI Validators**: 3 Claude Sonnet 4.5 agents
3. **Epic UI Components**: 7 Material-UI components
4. **OSCE Converter**: NLP parser + data generator
5. **PBS/MBS Databases**: Reference data loaders
6. **Validation Engine**: 3-layer system orchestrator

---

## ⚠️ Critical Constraints

### From PROJECT_CONSTRAINTS.md
1. **LLM Usage** (constraints/4-llm-integration.md):
   - ✅ **MUST use Claude API** (claude-sonnet-4-5-20250929) for:
     - SOAP note validation
     - Clinical reasoning assessment
     - Complex medical content generation
   - ❌ **NEVER use Ollama** for medical validation (not accurate enough)
   - ✅ **Can use Ollama** for: keyword extraction, simple yes/no validation

2. **Security** (zero-tolerance policy):
   - ❌ **NEVER hardcode credentials** (124 violations fixed previously - NEVER AGAIN)
   - ✅ **ALWAYS use Vault** for secrets (database passwords, API keys)
   - ✅ **ALWAYS validate inputs** (Pydantic schemas on all endpoints)
   - ✅ **ALWAYS use JWT auth** on all EMR endpoints

3. **Testing** (100% pass rate policy):
   - ✅ **MUST pass all tests** before marking task complete
   - ✅ **Target ≥70% coverage** (pytest, Playwright)
   - ✅ **Zero compilation errors** (flutter analyze, npm run type-check)

4. **Australian Medical Context**:
   - ✅ **ALWAYS use Australian terminology** (paracetamol not acetaminophen)
   - ✅ **ALWAYS reference eTG/AMH/AHPRA** guidelines
   - ✅ **ALWAYS use SI units** (mmol/L not mg/dL)
   - ✅ **Emergency number: 000** (not 911)

---

## 📞 Next Steps

### Immediate Actions (Week 1)
1. **PM Coordination**:
   - Review all 4 planning documents (ARCHITECTURE, DATABASE, API, INTEGRATION)
   - Validate approach with user
   - Confirm 4-week timeline acceptable

2. **Agent Delegation** (following Agent OS workflow):
   - **Database Expert**: Implement Alembic migration
   - **Backend Expert**: Build EMR API endpoints + AI validators
   - **Content Expert**: Run OSCE → EMR conversion (50 patients)
   - **Frontend Expert**: Migrate Epic UI to Material-UI
   - **Testing Expert**: Write E2E tests for EMR workflow
   - **Security Expert**: Audit for credential leaks, validate JWT usage

3. **Validation Gates** (after each phase):
   - ✅ Phase 1: Database migration successful, 6 tables created
   - ✅ Phase 2: 50 patients populated, medical expert verified
   - ✅ Phase 3: API endpoints working, pytest 100% pass
   - ✅ Phase 4: Epic UI functional, Material-UI migration complete
   - ✅ Phase 5: E2E tests passing, performance targets met

---

## 📚 Additional Resources

### Documents in This Folder
- `ARCHITECTURE.md` - System design and integration decisions
- `DATABASE_MIGRATION.md` - Schema extensions and Alembic migration
- `API_SPECIFICATION.md` - RESTful API endpoints and Pydantic schemas
- `INTEGRATION_STRATEGY.md` - OSCE conversion and cross-platform linking
- `README.md` - This file (implementation overview)

### External References
- AMC Clinical Examination: https://www.amc.org.au/
- eTG (Therapeutic Guidelines): https://etg.tg.org.au/
- PBS (Pharmaceutical Benefits Scheme): https://www.pbs.gov.au/
- MBS (Medicare Benefits Schedule): https://www.mbsonline.gov.au/
- NSW Health EMR Standards: https://www.health.nsw.gov.au/

### Project Files
- Project Constraints: `/constraints/README.md`
- Global Claude Instructions: `~/.claude/CLAUDE.md`
- Project Claude Instructions: `/CLAUDE.md`
- Existing OSCE API: `/backend/src/api/v1/osces.py`
- Existing MCQ API: `/backend/src/api/v1/mcqs.py`
- Existing Dashboard: `/frontend/src/components/dashboard/DashboardPage.tsx`

---

## ✅ Planning Checklist

- [x] Architecture decisions documented
- [x] Database schema designed (6 tables + 17 columns)
- [x] API specification complete (19 endpoints)
- [x] Integration strategy defined (OSCE → EMR conversion)
- [x] 4-week implementation timeline created
- [x] Success metrics defined
- [x] Testing strategy outlined
- [x] Security considerations addressed
- [x] Australian compliance verified
- [x] Agent delegation plan created
- [ ] **User approval obtained** ← Next step
- [ ] Begin implementation (database migration first)

---

**Status**: 📋 PLANNING COMPLETE - READY FOR USER APPROVAL
**Last Updated**: 2026-02-15
**Next Action**: Present to user for approval, then begin implementation
