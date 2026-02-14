# RALPH Agent Implementation Guide

**Version**: 1.0
**Date**: 2026-02-02
**Purpose**: Step-by-step guide for implementing EMR practice system using RALPH agents
**Total Estimate**: 100-125 hours

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Phase 1: Frontend Implementation](#phase-1-frontend-implementation)
3. [Phase 2: Validation Implementation](#phase-2-validation-implementation)
4. [Phase 3: Backend Implementation](#phase-3-backend-implementation)
5. [Phase 4: Integration & Testing](#phase-4-integration--testing)
6. [RALPH Agent Prompts](#ralph-agent-prompts)

---

## Prerequisites

### Before Starting

1. **Review All PRDs**: Read all documents in `/emr-practice-system/prd/`
2. **Setup Environment**: Node.js 20+, Python 3.11+, Docker
3. **API Keys**: Anthropic API key for AI validation
4. **Project Constraints**: Read `/constraints/README.md`

### Repository Structure

```
irStudy/
├── emr-practice-system/        # NEW: All PRDs here
│   ├── README.md               # Master index
│   ├── prd/                    # All PRD documents
│   ├── validation-rules/       # Validation specifications
│   └── ui-mockups/             # Styling specs
├── frontend/                    # Main frontend (existing)
├── backend/                     # Main backend (existing)
└── emr-frontend/               # NEW: EMR frontend (to create)
└── emr-backend/                # NEW: EMR backend (to create)
```

---

## Phase 1: Frontend Implementation

**Estimated Time**: 40-50 hours
**Agent**: flutter-desktop-expert (adapt for React) OR general-purpose

### Task 1.1: Project Setup (4 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Setup React + TypeScript + Vite project for EMR practice system frontend

**Context**:
You are setting up a NEW frontend module for the EMR practice system. This will be a separate React application that integrates with the main irStudy platform.

**Requirements**:
1. Create new directory: `/home/dev/Development/irStudy/emr-frontend`
2. Initialize Vite + React + TypeScript project
3. Install dependencies from Master PRD section 5.1:
   ```
   react@18.2.0
   typescript@5.3.3
   vite@5.0.10
   tailwindcss@3.4.1
   framer-motion@11.0.3
   lucide-react@0.309.0
   react-hook-form@7.49.3
   zod@3.22.4
   @tanstack/react-query@5.17.15
   zustand@4.4.7
   ```
4. Configure Tailwind CSS with custom theme
5. Create folder structure:
   ```
   src/
   ├── components/
   │   ├── cerner/
   │   └── epic/
   ├── pages/
   ├── hooks/
   ├── stores/
   ├── api/
   ├── schemas/
   └── utils/
   ```
6. Configure `vite.config.ts` with proxy to backend API (port 8001)
7. Create `.env.example` with required environment variables

**References**:
- Master PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md` (section 5)
- Styling Spec: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md`

**Validation**:
- [ ] `npm run dev` starts successfully
- [ ] Tailwind CSS classes work
- [ ] TypeScript compilation has 0 errors
- [ ] All dependencies installed correctly

**Deliverable**: Working Vite + React + TypeScript project with all dependencies installed
```

### Task 1.2: Implement Cerner UI Components (16 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement Cerner PowerChart UI components

**Context**:
Implement ALL Cerner PowerChart components as specified in the Cerner UI PRD. These components simulate the real Cerner EMR system used in Australian hospitals.

**Components to Implement** (in order):

1. **CernerSidebar** (2 hours)
   - Reference: Cerner PRD section 3.1
   - File: `src/components/cerner/CernerSidebar.tsx`
   - Copy TypeScript code from PRD verbatim
   - Copy CSS from Styling Spec section 3.1
   - Test: Renders 7 navigation items, highlights active item

2. **PatientBanner** (2 hours)
   - Reference: Cerner PRD section 3.2
   - File: `src/components/cerner/PatientBanner.tsx`
   - Include allergy alerts with severity colors
   - Test: Displays patient info, shows allergies prominently

3. **SOAPNoteEditor** (6 hours)
   - Reference: Cerner PRD section 3.3
   - File: `src/components/cerner/SOAPNoteEditor.tsx`
   - Implement all 4 sections (Subjective, Objective, Assessment, Plan)
   - Integrate React Hook Form + Zod validation
   - Add auto-save functionality (30 second debounce)
   - Test: All sections editable, validation works, auto-save triggers

4. **MedicationOrderEntry** (4 hours)
   - Reference: Cerner PRD section 3.4
   - File: `src/components/cerner/MedicationOrderEntry.tsx`
   - PBS medication search with debouncing
   - Dosage calculator
   - Test: Search works, form validates, PBS code validation

5. **PathologyOrderForm** (2 hours)
   - Reference: Cerner PRD section 3.5
   - File: `src/components/cerner/PathologyOrderForm.tsx`
   - MBS item number validation
   - Test: MBS validation, urgency selection works

**References**:
- Cerner UI PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/01_CERNER_POWERCHART_UI_PRD.md`
- Styling Spec: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md`
- Validation Rules: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md` (section 3)

**IMPORTANT**:
- Copy code from PRDs exactly as specified
- Use Australian medical terminology (paracetamol, not acetaminophen)
- Implement all CSS styling from Styling Spec
- Add proper TypeScript types
- Include accessibility (aria-labels, keyboard navigation)

**Validation**:
- [ ] All 5 components render without errors
- [ ] Styling matches mockups in PRD
- [ ] Forms have proper validation
- [ ] Auto-save works (test by changing data and waiting 30s)
- [ ] No TypeScript errors
- [ ] No console warnings

**Deliverable**: 5 fully functional Cerner UI components with styling and validation
```

### Task 1.3: Implement Epic UI Components (12 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement Epic EHR UI components

**Context**:
Implement ALL Epic EHR components as specified in the Epic UI PRD. These components use a purple theme and icon-based navigation.

**Components to Implement** (in order):

1. **EpicIconBar** (2 hours)
   - Reference: Epic PRD section 3.1
   - File: `src/components/epic/EpicIconBar.tsx`
   - Vertical icon navigation (left side)
   - Test: Icons render, active state works

2. **EpicPatientBanner** (2 hours)
   - Reference: Epic PRD section 3.2
   - File: `src/components/epic/EpicPatientBanner.tsx`
   - Different layout from Cerner (linear vs grid)
   - Test: Patient info displays correctly

3. **EpicWorkspacePanel** (4 hours)
   - Reference: Epic PRD section 3.3
   - File: `src/components/epic/EpicWorkspacePanel.tsx`
   - Resizable dual-panel layout
   - Tab bar for switching views
   - Test: Panels resize correctly, tabs work

4. **EpicNoteComposer** (2 hours)
   - Reference: Epic PRD section 3.4
   - File: `src/components/epic/EpicNoteComposer.tsx`
   - Template selector
   - Test: Templates switch correctly

5. **EpicMedicationPanel** (2 hours)
   - Reference: Epic PRD section 3.5
   - File: `src/components/epic/EpicMedicationPanel.tsx`
   - Similar to Cerner but with Epic styling
   - Test: PBS search works with Epic theme

**References**:
- Epic UI PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/02_EPIC_EHR_UI_PRD.md`
- Styling Spec: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md` (Epic theme)

**Validation**:
- [ ] All Epic components render
- [ ] Purple theme applied correctly
- [ ] Icon bar navigation works
- [ ] Panel resizing works smoothly
- [ ] No TypeScript errors

**Deliverable**: 5 Epic UI components with purple theme and icon navigation
```

### Task 1.4: Implement State Management (4 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement Zustand stores for state management

**Context**:
Create global state management using Zustand for EMR session data, SOAP notes, prescriptions, and validation results.

**Stores to Create**:

1. **EMRSessionStore** (1 hour)
   - Reference: Styling Spec section 7
   - File: `src/stores/emrSessionStore.ts`
   - State: sessionId, patient, emrType, metrics
   - Actions: setSession, setPatient, updateMetrics

2. **SOAPNoteStore** (1 hour)
   - File: `src/stores/soapNoteStore.ts`
   - State: currentNote (Subjective, Objective, Assessment, Plan)
   - Actions: updateSection, saveNote, resetNote

3. **ValidationStore** (1 hour)
   - File: `src/stores/validationStore.ts`
   - State: validationResult, isValidating, errors, warnings
   - Actions: startValidation, setResult, clearErrors

4. **PrescriptionStore** (1 hour)
   - File: `src/stores/prescriptionStore.ts`
   - State: prescriptions array
   - Actions: addPrescription, removePrescription, updatePrescription

**References**:
- Styling Spec: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md` (section 7)

**Validation**:
- [ ] All stores created with proper TypeScript types
- [ ] Actions update state correctly
- [ ] Stores persist across component re-renders
- [ ] No memory leaks (proper cleanup)

**Deliverable**: 4 Zustand stores with full TypeScript typing
```

### Task 1.5: Implement Custom Hooks (4 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement custom React hooks for common functionality

**Context**:
Create reusable hooks for auto-save, typing metrics, PBS search, and validation.

**Hooks to Create**:

1. **useAutoSave** (1 hour)
   - Reference: Styling Spec section 4.1
   - File: `src/hooks/useAutoSave.ts`
   - Debounce 30 seconds
   - Test: Saves after 30s, cancels on unmount

2. **useTypingMetrics** (1 hour)
   - Reference: Styling Spec section 4.2
   - File: `src/hooks/useTypingMetrics.ts`
   - Calculate WPM, keystroke count
   - Test: WPM calculation accurate

3. **usePBSSearch** (1 hour)
   - Reference: Styling Spec section 4.3
   - File: `src/hooks/usePBSSearch.ts`
   - Debounced search (300ms)
   - Test: Search triggers after 300ms pause

4. **useValidation** (1 hour)
   - File: `src/hooks/useValidation.ts`
   - Progressive validation (Layer 1 → 2 → 3)
   - Test: Layers execute in sequence

**References**:
- Styling Spec: `/home/dev/Development/irStudy/emr-practice-system/ui-mockups/STYLING_FUNCTIONALITY_SPEC.md` (section 4)

**Validation**:
- [ ] All hooks implemented
- [ ] Hooks tested with React Testing Library
- [ ] Proper cleanup on unmount
- [ ] TypeScript types correct

**Deliverable**: 4 custom hooks with tests
```

---

## Phase 2: Validation Implementation

**Estimated Time**: 20-25 hours
**Agent**: general-purpose

### Task 2.1: Client-Side Validation (Zod Schemas) (6 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement all Zod validation schemas

**Context**:
Create comprehensive client-side validation using Zod schemas for SOAP notes, prescriptions, and pathology orders. This is Layer 1 validation (instant feedback).

**Schemas to Create**:

1. **SOAP Note Schema** (3 hours)
   - Reference: Validation Rules section 3.1
   - File: `src/schemas/soapNoteSchema.ts`
   - Copy schema code from Validation Rules PRD exactly
   - Include all sections: Subjective, Objective, Assessment, Plan
   - Test: All validations work (min length, max length, regex patterns)

2. **Prescription Schema** (2 hours)
   - Reference: Validation Rules section 3.2
   - File: `src/schemas/prescriptionSchema.ts`
   - PBS code validation
   - Dosage validation
   - Test: PBS code format, quantity limits, repeats limits

3. **Pathology Order Schema** (1 hour)
   - Reference: Validation Rules section 3.3
   - File: `src/schemas/pathologyOrderSchema.ts`
   - MBS item number validation
   - Test: MBS format (5 digits)

**References**:
- Validation Rules: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md` (section 3)

**IMPORTANT**:
- Copy Zod schemas from PRD verbatim
- Add Australian terminology validation (reject "acetaminophen", accept "paracetamol")
- Include all regex patterns exactly as specified
- Add helpful error messages

**Validation**:
- [ ] All schemas validate correctly
- [ ] Error messages are clear
- [ ] Australian terminology enforced
- [ ] 100% of test cases pass (create tests for each validation rule)

**Deliverable**: 3 complete Zod schemas with tests
```

### Task 2.2: Rule-Based Validation (Python) (10 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement Python rule-based validators (Layer 2)

**Context**:
Create Python validators for PBS medication compliance, MBS pathology compliance, and clinical safety checks. These run on the backend and return results in <1 second.

**Validators to Create**:

1. **PBS Validator** (4 hours)
   - Reference: Validation Rules section 4.1
   - File: `backend/src/validation/pbs_validator.py`
   - Copy code from Validation Rules PRD
   - Mock PBS database with common medications
   - Test: Quantity limits, repeats limits, allergy checking, drug interactions

2. **MBS Validator** (2 hours)
   - Reference: Validation Rules section 4.2
   - File: `backend/src/validation/mbs_validator.py`
   - Copy code from Validation Rules PRD
   - Mock MBS database with common tests
   - Test: Item number validation, frequency limits, fasting requirements

3. **Clinical Safety Validator** (4 hours)
   - Reference: Validation Rules section 4.3
   - File: `backend/src/validation/clinical_safety_validator.py`
   - Red flag detection (chest pain, stroke, sepsis, etc.)
   - Vital signs validation
   - Test: All red flag patterns detected

**References**:
- Validation Rules: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md` (section 4)

**IMPORTANT**:
- Copy validation logic from PRD exactly
- Use mock databases (don't connect to real PBS/MBS APIs yet)
- Return ValidationError objects with severity, category, message, suggestion
- Ensure all validators complete in <1 second

**Validation**:
- [ ] All 3 validators implemented
- [ ] Unit tests for each validator (pytest)
- [ ] 50+ test cases for PBS validator
- [ ] 30+ test cases for MBS validator
- [ ] All red flags detected correctly
- [ ] Response time <1 second

**Deliverable**: 3 Python validators with comprehensive tests
```

### Task 2.3: AI Validation Service (Claude) (6 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement AI-powered validation using Claude 3.5 Sonnet (Layer 3)

**Context**:
Create AI validation service that provides deep clinical reasoning assessment and educational feedback. This is the final layer of validation.

**Service to Create**:

**AI Validator** (6 hours)
   - Reference: Validation Rules section 5
   - File: `backend/src/validation/ai_validator.py`
   - Copy AIValidator class from Validation Rules PRD
   - Implement SOAP note validation with scoring (0-100)
   - Implement prescription validation
   - Test: Returns valid JSON, scores are reasonable, feedback is educational

**System Prompts**:
- Copy system prompts from Validation Rules PRD (section 5.1)
- Include Australian medical educator persona
- Specify assessment criteria (clinical reasoning, documentation, compliance, safety)

**References**:
- Validation Rules: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md` (section 5)
- Backend API PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md` (AIValidationService)

**IMPORTANT**:
- Use Anthropic API with Claude 3.5 Sonnet
- Temperature: 0.3 (for consistent evaluation)
- Max tokens: 4000
- Parse JSON response
- Handle API errors gracefully (timeout, rate limiting)

**Validation**:
- [ ] AI validator returns valid JSON
- [ ] Overall scores between 0-100
- [ ] Educational feedback provided
- [ ] Strengths and improvements listed
- [ ] Response time 3-5 seconds (acceptable)
- [ ] API errors handled

**Deliverable**: AI validation service with Claude integration
```

---

## Phase 3: Backend Implementation

**Estimated Time**: 20-25 hours
**Agent**: general-purpose

### Task 3.1: Setup Backend Project (3 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Setup FastAPI backend project for EMR practice system

**Context**:
Create new FastAPI backend for EMR practice system with SQLAlchemy, Alembic, and all required dependencies.

**Requirements**:
1. Create directory: `/home/dev/Development/irStudy/emr-backend`
2. Create virtual environment: `python -m venv venv`
3. Install dependencies from Backend API PRD section 1
4. Create project structure as specified in Backend API PRD section 2
5. Setup FastAPI app with CORS middleware
6. Setup SQLAlchemy with async engine
7. Setup Alembic for migrations

**References**:
- Backend API PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md` (sections 1-2)

**Validation**:
- [ ] Virtual environment created
- [ ] All dependencies installed
- [ ] FastAPI app runs (`uvicorn src.main:app --reload`)
- [ ] /docs endpoint shows Swagger UI
- [ ] /health endpoint returns {"status": "healthy"}
- [ ] Database connection works

**Deliverable**: Working FastAPI project with all dependencies
```

### Task 3.2: Implement Core APIs (10 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement all core API endpoints

**Context**:
Implement authentication, session management, SOAP note CRUD, prescription management, pathology orders, validation endpoints, and progress tracking.

**Endpoints to Implement** (in order):

1. **Authentication API** (2 hours)
   - Reference: Backend API PRD section 3
   - File: `backend/src/api/v1/auth.py`
   - Endpoints: POST /login, POST /register, GET /me
   - JWT token generation
   - Test: Login works, token validates

2. **Session Management API** (2 hours)
   - Reference: Backend API PRD section 4.1
   - File: `backend/src/api/v1/sessions.py`
   - Endpoints: POST /sessions, GET /sessions/{id}, POST /sessions/{id}/complete
   - Test: Create session, get session, complete session

3. **SOAP Note API** (2 hours)
   - Reference: Backend API PRD section 4.2
   - File: `backend/src/api/v1/soap_notes.py`
   - Endpoints: POST /soap-notes, GET /soap-notes/{id}, PATCH /soap-notes/{id}
   - Test: CRUD operations work

4. **Prescription API** (2 hours)
   - Reference: Backend API PRD section 4.3
   - File: `backend/src/api/v1/prescriptions.py`
   - Endpoints: POST /prescriptions, GET /prescriptions/{id}
   - Test: Create prescription, get prescription

5. **Pathology API** (1 hour)
   - Reference: Backend API PRD section 4.4
   - File: `backend/src/api/v1/pathology.py`
   - Endpoints: POST /pathology, GET /pathology/{id}
   - Test: Create order, get order

6. **Validation API** (1 hour)
   - Reference: Backend API PRD section 4.5
   - File: `backend/src/api/v1/validation.py`
   - Endpoints: POST /validation/soap-note, POST /validation/prescription
   - Test: Validation returns results

**References**:
- Backend API PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md` (section 4)

**Validation**:
- [ ] All endpoints implemented
- [ ] OpenAPI docs show all endpoints
- [ ] Authentication works (JWT)
- [ ] All CRUD operations work
- [ ] Error handling works (422, 401, 404, 500)
- [ ] Response times meet SLAs

**Deliverable**: 6 API routers with all endpoints
```

### Task 3.3: Implement Database Models (4 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Implement all SQLAlchemy database models

**Context**:
Create database models for users, sessions, SOAP notes, prescriptions, pathology orders, and validation results.

**Models to Create**:

1. **User Model** (1 hour)
   - Reference: Backend API PRD section 5
   - File: `backend/src/models/user.py`
   - Fields: id, email, full_name, hashed_password, role, created_at
   - Test: Create user, query user

2. **EMR Session Model** (1 hour)
   - Reference: Backend API PRD section 5
   - File: `backend/src/models/session.py`
   - Fields: id, user_id, patient_id, emr_type, status, metrics, scores
   - Relationships: user, patient, soap_notes, prescriptions
   - Test: Create session, update status

3. **SOAP Note Model** (1 hour)
   - Reference: Backend API PRD section 5
   - File: `backend/src/models/soap_note.py`
   - Fields: id, session_id, subjective (JSON), objective (JSON), assessment (JSON), plan (JSON)
   - Test: Create note, update sections

4. **Prescription & Pathology Models** (1 hour)
   - Files: `backend/src/models/prescription.py`, `backend/src/models/pathology_order.py`
   - Similar structure to SOAP note
   - Test: Create, retrieve

**References**:
- Backend API PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md` (section 5)

**Validation**:
- [ ] All models created
- [ ] Alembic migrations generated
- [ ] Migrations run successfully
- [ ] Database tables created
- [ ] Relationships work (foreign keys)
- [ ] JSON fields serialize correctly

**Deliverable**: 5 database models with migrations
```

### Task 3.4: Integration & Testing (3 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Create integration tests for backend API

**Context**:
Test all API endpoints end-to-end with database integration.

**Tests to Create**:

1. **Authentication Tests** (1 hour)
   - Test login with valid credentials
   - Test login with invalid credentials
   - Test JWT token validation
   - Test token expiration

2. **Workflow Tests** (2 hours)
   - Test complete EMR session workflow
   - Test SOAP note creation → validation → completion
   - Test prescription creation → PBS validation
   - Test pathology order → MBS validation

**References**:
- Testing Strategy PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/04_TESTING_STRATEGY_PRD.md` (section 3)
- Backend API PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md` (section 4)

**Validation**:
- [ ] All integration tests pass
- [ ] 100% test pass rate
- [ ] Code coverage ≥70%
- [ ] No flaky tests

**Deliverable**: Integration test suite with ≥70% coverage
```

---

## Phase 4: Integration & Testing

**Estimated Time**: 10-12 hours

### Task 4.1: Connect Frontend to Backend (4 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Integrate frontend with backend API using TanStack Query

**Context**:
Connect React frontend to FastAPI backend using TanStack Query for API state management.

**API Client to Create**:

1. **API Client Setup** (1 hour)
   - File: `emr-frontend/src/api/client.ts`
   - Axios instance with JWT interceptor
   - Error handling
   - Test: Requests include Bearer token

2. **TanStack Query Hooks** (3 hours)
   - File: `emr-frontend/src/api/hooks/`
   - useCreateSession
   - useSOAPNote (get, create, update)
   - useValidation
   - Test: All hooks work, caching works, mutations work

**Validation**:
- [ ] Frontend calls backend successfully
- [ ] JWT authentication works
- [ ] TanStack Query caching works
- [ ] Error handling works (network errors, 401, 422)

**Deliverable**: Frontend-backend integration complete
```

### Task 4.2: E2E Testing (6 hours)

**RALPH Agent Prompt:**

```markdown
**Task**: Create end-to-end tests using Playwright

**Context**:
Test critical user workflows from login to session completion.

**Tests to Create**:

1. **Complete Cerner Session** (3 hours)
   - Login → Start Session → Write SOAP Note → Validate → Complete
   - Test all validation layers execute
   - Test final scores displayed

2. **Complete Epic Session** (2 hours)
   - Similar workflow with Epic UI
   - Test panel resizing works
   - Test navigation works

3. **Prescription Workflow** (1 hour)
   - Search PBS → Select Med → Fill Form → Validate
   - Test PBS validation errors displayed

**References**:
- Testing Strategy PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/04_TESTING_STRATEGY_PRD.md` (section 5)

**Validation**:
- [ ] All E2E tests pass
- [ ] Tests run in <5 minutes
- [ ] Screenshots captured on failure

**Deliverable**: E2E test suite covering critical workflows
```

---

## RALPH Agent Prompts

### Agent Delegation Best Practices

1. **Front-load Context**: Always reference specific PRD sections
2. **Explicit Constraints**: Specify what NOT to do (anti-patterns)
3. **Validation Checklist**: Agent must verify before returning
4. **Code Examples**: Provide exactly where to find code in PRDs

### Sequential Validation Pattern

```
Delegate Task 1 → Agent Works → Agent Self-Validates → PM Validates
    ↓ (if pass)
Delegate Task 2 → Agent Works → Agent Self-Validates → PM Validates
    ↓ (if pass)
Continue...
```

**DO NOT** batch delegate without validation between tasks.

---

## Progress Tracking

### Implementation Status

Update this table as you complete tasks:

| Phase | Task | Status | Hours | Completion Date |
|-------|------|--------|-------|-----------------|
| Phase 1 | 1.1 Project Setup | ⏳ Not Started | 4 | - |
| Phase 1 | 1.2 Cerner Components | ⏳ Not Started | 16 | - |
| Phase 1 | 1.3 Epic Components | ⏳ Not Started | 12 | - |
| Phase 1 | 1.4 State Management | ⏳ Not Started | 4 | - |
| Phase 1 | 1.5 Custom Hooks | ⏳ Not Started | 4 | - |
| Phase 2 | 2.1 Zod Schemas | ⏳ Not Started | 6 | - |
| Phase 2 | 2.2 Python Validators | ⏳ Not Started | 10 | - |
| Phase 2 | 2.3 AI Validation | ⏳ Not Started | 6 | - |
| Phase 3 | 3.1 Backend Setup | ⏳ Not Started | 3 | - |
| Phase 3 | 3.2 Core APIs | ⏳ Not Started | 10 | - |
| Phase 3 | 3.3 Database Models | ⏳ Not Started | 4 | - |
| Phase 3 | 3.4 Integration Tests | ⏳ Not Started | 3 | - |
| Phase 4 | 4.1 Frontend-Backend | ⏳ Not Started | 4 | - |
| Phase 4 | 4.2 E2E Testing | ⏳ Not Started | 6 | - |
| **TOTAL** | | 0% | **100-125** | - |

---

## Quality Gates

Before moving to next phase, ensure:

### Phase 1 Complete ✅
- [ ] All Cerner components render
- [ ] All Epic components render
- [ ] Styling matches PRD mockups
- [ ] State management works
- [ ] Custom hooks work
- [ ] `npm run dev` successful
- [ ] 0 TypeScript errors
- [ ] 0 console warnings

### Phase 2 Complete ✅
- [ ] All Zod schemas validate
- [ ] PBS validator passes 50+ test cases
- [ ] MBS validator passes 30+ test cases
- [ ] Clinical safety validator detects all red flags
- [ ] AI validator returns valid JSON
- [ ] All validators meet response time SLAs

### Phase 3 Complete ✅
- [ ] All API endpoints work
- [ ] Authentication & JWT work
- [ ] Database models created
- [ ] Migrations run successfully
- [ ] Integration tests pass (≥70% coverage)
- [ ] 100% test pass rate

### Phase 4 Complete ✅
- [ ] Frontend calls backend successfully
- [ ] E2E tests pass
- [ ] Complete user workflow works (login → session → validation → complete)
- [ ] No critical bugs

---

## Support & Resources

### Key Documents

1. **Starting Implementation?** → Read Master PRD first
2. **Building UI?** → Cerner PRD + Epic PRD + Styling Spec
3. **Implementing Validation?** → Validation Rules (all sections)
4. **Building API?** → Backend API PRD
5. **Writing Tests?** → Testing Strategy PRD

### External Resources

- **PBS Online**: https://pbs.gov.au
- **MBS Online**: https://mbsonline.gov.au
- **eTG**: https://tg.org.au
- **Anthropic API**: https://docs.anthropic.com

---

**Document Version**: 1.0
**Last Updated**: 2026-02-02
**Status**: ✅ Ready for RALPH Agents
**Estimated Total Time**: 100-125 hours

