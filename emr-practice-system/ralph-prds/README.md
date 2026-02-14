# RALPH PRD Index - EMR Practice System

**Project**: EMR Practice System for ICRP Preparation
**Total Estimated Time**: ~60 hours
**Created**: 2026-02-03
**Status**: Ready for Implementation

---

## Overview

This directory contains Product Requirement Documents (PRDs) for RALPH agent implementation of the EMR Practice System. Each PRD is self-contained with complete code, validation checklists, and time estimates.

**Purpose**: Enable IMGs (International Medical Graduates) to practice EMR documentation in realistic Cerner PowerChart and Epic EHR environments with AI-powered feedback for ICRP preparation.

---

## Project Structure

```
ralph-prds/
├── README.md                           # This file
├── phase1/                             # Frontend Foundation (24 hours)
│   ├── TASK_1.1_PROJECT_SETUP.md      # 4 hours
│   ├── TASK_1.2_CERNER_COMPONENTS.md  # 16 hours
│   ├── TASK_1.3_EPIC_COMPONENTS.md    # 12 hours
│   ├── TASK_1.4_STATE_MANAGEMENT.md   # 4 hours
│   └── TASK_1.5_CUSTOM_HOOKS.md       # 4 hours
├── phase2/                             # Validation Layer (22 hours)
│   ├── TASK_2.1_ZOD_SCHEMAS.md        # 6 hours
│   ├── TASK_2.2_PYTHON_VALIDATORS.md  # 10 hours
│   └── TASK_2.3_AI_VALIDATION.md      # 6 hours
├── phase3/                             # Backend (20 hours)
│   └── TASK_3_BACKEND_IMPLEMENTATION.md
└── phase4/                             # Integration (10 hours)
    └── TASK_4_INTEGRATION_TESTING.md
```

---

## Phase 1: Frontend Foundation (24 hours)

### TASK 1.1: Project Setup (4 hours)
**File**: `phase1/TASK_1.1_PROJECT_SETUP.md`

**What**: Initialize React + TypeScript + Vite project with all dependencies

**Deliverables**:
- Vite project created
- All dependencies installed (React, Tailwind, Framer Motion, TanStack Query, Zustand, React Hook Form, Zod)
- Tailwind configured with Cerner/Epic themes
- Path aliases configured
- Folder structure created
- Dev server running on port 5174

**Status**: ✅ **COMPLETED** (Task 1.1 already executed in tmux session)

---

### TASK 1.2: Cerner Components (16 hours)
**File**: `phase1/TASK_1.2_CERNER_COMPONENTS.md`

**What**: Build Cerner PowerChart UI components

**Components**:
1. **CernerSidebar** (2 hours) - Navigation with session timer
2. **PatientBanner** (2 hours) - Patient demographics, allergies, alerts
3. **SOAPNoteEditor** (6 hours) - Full SOAP note editor with auto-save, React Hook Form + Zod validation

**Deliverables**:
- All 3 components with complete TypeScript code
- Full CSS styling (Cerner dark theme)
- Form validation working
- Auto-save every 30 seconds
- Test page demonstrating all components

---

### TASK 1.3: Epic Components (12 hours)
**File**: `phase1/TASK_1.3_EPIC_COMPONENTS.md`

**What**: Build Epic EHR UI components

**Components**:
1. **EpicSidebar** (3 hours) - Light theme navigation
2. **EpicPatientBanner** (3 hours) - Patient context bar
3. **EpicNoteEditor** (6 hours) - Epic-style note editor with tabs

**Deliverables**:
- All 3 components with complete TypeScript code
- Full CSS styling (Epic light theme, purple accents)
- Form validation
- Auto-save functionality
- Test page

---

### TASK 1.4: State Management (4 hours)
**File**: `phase1/TASK_1.4_STATE_MANAGEMENT.md`

**What**: Create Zustand stores for global state

**Stores**:
1. **Session Store** (1.5 hours) - Session data, timer, typing metrics
2. **Form Store** (1.5 hours) - SOAP notes, prescriptions, pathology orders, auto-save tracking
3. **Validation Store** (1 hour) - Validation results, errors, warnings

**Deliverables**:
- All 3 stores with TypeScript types
- Zustand devtools enabled
- Persistence configured (localStorage)
- Usage examples

---

### TASK 1.5: Custom Hooks (4 hours)
**File**: `phase1/TASK_1.5_CUSTOM_HOOKS.md`

**What**: Create reusable React hooks

**Hooks**:
1. **useAutoSave** (1 hour) - Auto-save with interval
2. **useTypingMetrics** (1 hour) - Track WPM, accuracy, keystrokes
3. **usePBSSearch** (1 hour) - Search PBS medications with debounce
4. **useValidation** (1 hour) - Trigger validation, get results

**Deliverables**:
- All 4 hooks with full implementation
- TypeScript types
- Usage examples

---

## Phase 2: Validation Layer (22 hours)

### TASK 2.1: Zod Schemas (6 hours)
**File**: `phase2/TASK_2.1_ZOD_SCHEMAS.md`

**What**: Client-side validation schemas (Layer 1, <50ms)

**Schemas**:
1. **SOAP Note Schema** (2 hours) - All SOAP sections, vital signs ranges
2. **Prescription Schema** (2 hours) - PBS compliance, dose format, authority requirements
3. **Pathology Schema** (1.5 hours) - MBS compliance, clinical indication
4. **Session Schema** (0.5 hours) - Session metadata

**Deliverables**:
- All schemas with Australian clinical standards
- Custom validation rules
- Helpful error messages
- Validation utilities

---

### TASK 2.2: Python Validators (10 hours)
**File**: `phase2/TASK_2.2_PYTHON_VALIDATORS.md`

**What**: Rule-based validation (Layer 2, <1s)

**Validators**:
1. **PBS Validator** (3 hours) - PBS codes, quantity/repeat limits, authority, restrictions, drug interactions
2. **MBS Validator** (3 hours) - MBS codes, frequency rules, clinical indication adequacy
3. **Documentation Validator** (2 hours) - SOAP completeness, OLDCARTS elements, safety-netting
4. **Validation API** (2 hours) - FastAPI endpoints

**Deliverables**:
- Complete Python validators
- Australian PBS/MBS compliance
- Validation API endpoints
- Mock PBS/MBS databases

---

### TASK 2.3: AI Validation (6 hours)
**File**: `phase2/TASK_2.3_AI_VALIDATION.md`

**What**: AI-powered validation (Layer 3, 3-5s)

**Components**:
1. **Claude AI Validator** (3 hours) - SOAP, prescription, pathology validation with educational feedback
2. **AI API Endpoints** (1.5 hours) - FastAPI integration
3. **Validation Pipeline** (1.5 hours) - Orchestrate all 3 layers

**Deliverables**:
- Anthropic Claude 3.5 Sonnet integration
- Educational feedback (strengths, areas for improvement, learning points)
- Australian clinical guidelines references
- Combined 3-layer validation pipeline

---

## Phase 3: Backend (20 hours)

### TASK 3: Backend Implementation (20 hours)
**File**: `phase3/TASK_3_BACKEND_IMPLEMENTATION.md`

**What**: Complete FastAPI backend

**Sub-tasks**:
1. **Backend Setup** (3 hours) - FastAPI, PostgreSQL, folder structure, config
2. **Database Models** (4 hours) - SQLAlchemy models for users, sessions, SOAP notes, prescriptions, pathology
3. **Authentication** (4 hours) - JWT, password hashing, login/register endpoints
4. **Core APIs** (6 hours) - Sessions, SOAP notes, prescriptions, pathology CRUD
5. **Docker** (1.5 hours) - Dockerfile, docker-compose with PostgreSQL
6. **Migrations** (1.5 hours) - Alembic setup

**Deliverables**:
- FastAPI backend on port 8001
- PostgreSQL database
- JWT authentication
- All CRUD endpoints
- Docker containerization
- Database migrations

---

## Phase 4: Integration (10 hours)

### TASK 4: Integration & Testing (10 hours)
**File**: `phase4/TASK_4_INTEGRATION_TESTING.md`

**What**: Connect frontend to backend, E2E testing

**Sub-tasks**:
1. **Frontend-Backend Integration** (4 hours) - Axios client, API hooks, authentication flow
2. **Complete User Flows** (3 hours) - Login → Dashboard → Session → Documentation → Validation → Complete
3. **E2E Testing** (3 hours) - Playwright tests for complete flows

**Deliverables**:
- Frontend connected to backend
- Full authentication flow
- Complete session workflow
- Auto-save working
- Validation integrated
- E2E tests passing
- Deployment-ready system

---

## Quick Start Guide

### For RALPH Agents

1. **Start with Phase 1, Task 1.1** (already completed)
2. **Read the PRD file** for your assigned task
3. **Follow the code examples** (copy-paste ready)
4. **Complete the validation checklist** before marking task done
5. **Run tests** to verify implementation
6. **Move to next task** sequentially

### For Project Managers

1. **Assign tasks** by phase to different agents or developers
2. **Track progress** using the validation checklists
3. **Review deliverables** against time estimates
4. **Integration point** after each phase completion

---

## Key Technologies

**Frontend**:
- React 18.2.0 + TypeScript 5.3.3
- Vite 5.0.10 (build tool)
- Tailwind CSS 3.4.1 (styling)
- Framer Motion 11.0.3 (animations)
- TanStack Query 5.17.15 (API state)
- Zustand 4.4.7 (global state)
- React Hook Form 7.49.3 + Zod 3.22.4 (validation)

**Backend**:
- FastAPI 0.109.0 + Python 3.11
- SQLAlchemy 2.0.25 (ORM)
- PostgreSQL 15 (database)
- Alembic 1.13.1 (migrations)
- Anthropic Claude 3.5 Sonnet (AI validation)

---

## Validation Standards

**Australian Compliance**:
- PBS (Pharmaceutical Benefits Scheme) rules
- MBS (Medicare Benefits Schedule) codes
- TGA (Therapeutic Goods Administration) guidelines
- Australian clinical guidelines (eTG, Therapeutic Guidelines)
- AHPRA standards for IMGs
- ICRP competency requirements

**3-Layer Validation**:
1. **Layer 1 (Client)**: Zod schemas, <50ms, instant feedback
2. **Layer 2 (Python)**: PBS/MBS validation, <1s, compliance checks
3. **Layer 3 (AI)**: Claude analysis, 3-5s, educational feedback

---

## Time Summary

| Phase | Description | Estimated Time |
|-------|-------------|----------------|
| Phase 1 | Frontend Foundation | 24 hours |
| Phase 2 | Validation Layer | 22 hours |
| Phase 3 | Backend | 20 hours |
| Phase 4 | Integration | 10 hours |
| **Total** | **Complete System** | **~60 hours** |

**Note**: Times are estimates for experienced developers. Adjust based on team skill level.

---

## Success Criteria

**Functional Requirements**:
- ✅ Users can practice EMR documentation in Cerner and Epic interfaces
- ✅ SOAP notes validated against Australian standards
- ✅ Prescriptions checked for PBS compliance
- ✅ Pathology orders validated for MBS compliance
- ✅ AI provides educational feedback for ICRP preparation
- ✅ Auto-save prevents data loss
- ✅ Session timer tracks practice duration
- ✅ Typing metrics tracked for skill assessment

**Non-Functional Requirements**:
- ✅ Layer 1 validation < 50ms
- ✅ Layer 2 validation < 1s
- ✅ Layer 3 validation 3-5s
- ✅ 100% type safety (TypeScript)
- ✅ Responsive design (mobile-friendly)
- ✅ Secure authentication (JWT)
- ✅ Database persistence
- ✅ Docker deployable

---

## Support

**Questions**: Refer to master PRDs in `/home/dev/Development/irStudy/emr-practice-system/design-specs/`

**Issues**: Check validation checklists in each PRD

**Testing**: Follow E2E test examples in Phase 4

---

**Last Updated**: 2026-02-03
**Version**: 1.0
**Status**: ✅ All PRDs Complete - Ready for RALPH Implementation
