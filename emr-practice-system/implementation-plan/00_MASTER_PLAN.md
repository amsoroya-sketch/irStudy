# EMR Practice System - Master Implementation Plan

**Version**: 1.0
**Date**: 2026-02-04
**Status**: Ready for Execution
**Current Progress**: 10-15% Complete (Planning + Basic Skeleton)

---

## Executive Summary

This master plan breaks down the remaining 85-90% of EMR implementation into **19 detailed tasks** across **5 phases**. Each task has clear deliverables, acceptance criteria, and Agent OS delegation prompts.

### Total Effort Estimate
- **Phase 1 (Frontend):** 35-40 hours
- **Phase 2 (Validation):** 20-25 hours
- **Phase 3 (Backend):** 18-22 hours
- **Phase 4 (Integration):** 10-12 hours
- **Phase 5 (Polish):** 5-8 hours
- **TOTAL:** 88-107 hours

### Current Status (10-15% Complete)
✅ **Already Built:**
- Complete PRD documentation (9 documents, ~5,500 lines)
- Basic React + TypeScript frontend skeleton
- Basic Cerner/Epic component stubs
- Backend infrastructure (FastAPI, JWT auth, user management)
- One AI validator (12k lines)

❌ **Still Needed (85-90%):**
- Complete UI components (medication ordering, pathology ordering)
- Three-layer validation system (Zod + Python + AI)
- EMR-specific backend APIs (sessions, SOAP notes, prescriptions)
- Frontend-backend integration
- E2E testing
- Performance optimization & deployment

---

## Phase Overview

### Phase 1: Frontend Completion (35-40 hours)
**Goal**: Build all UI components, state management, hooks, styling

| Task | Hours | Status | Dependencies |
|------|-------|--------|--------------|
| [TASK 1.1](phase1-frontend/TASK_1.1_Complete_Cerner_Components.md) | 12 | ⏳ Not Started | None |
| [TASK 1.2](phase1-frontend/TASK_1.2_Complete_Epic_Components.md) | 8 | ⏳ Not Started | TASK 1.1 |
| [TASK 1.3](phase1-frontend/TASK_1.3_State_Management.md) | 4 | ⏳ Not Started | TASK 1.1, 1.2 |
| [TASK 1.4](phase1-frontend/TASK_1.4_Custom_Hooks.md) | 4 | ⏳ Not Started | TASK 1.3 |
| [TASK 1.5](phase1-frontend/TASK_1.5_Styling_Animations.md) | 6 | ⏳ Not Started | TASK 1.1, 1.2 |

**Phase Completion Criteria:**
- [ ] All 10+ components built (Cerner + Epic)
- [ ] 4 Zustand stores functional
- [ ] 4 custom hooks implemented
- [ ] Complete styling applied (dark + purple themes)
- [ ] 0 TypeScript errors
- [ ] ≥80% test coverage on hooks

---

### Phase 2: Validation Implementation (20-25 hours)
**Goal**: Build three-layer progressive validation system

| Task | Hours | Status | Dependencies |
|------|-------|--------|--------------|
| [TASK 2.1](phase2-validation/TASK_2.1_Zod_Schemas.md) | 6 | ⏳ Not Started | TASK 1.3 |
| [TASK 2.2](phase2-validation/TASK_2.2_PBS_MBS_Validators.md) | 10 | ⏳ Not Started | None |
| [TASK 2.3](phase2-validation/TASK_2.3_AI_Validation.md) | 6 | ⏳ Not Started | TASK 2.2 |
| [TASK 2.4](phase2-validation/TASK_2.4_Unified_Validation_API.md) | 2 | ⏳ Not Started | TASK 2.1, 2.2, 2.3 |

**Phase Completion Criteria:**
- [ ] Layer 1 (Zod): <50ms validation, inline errors
- [ ] Layer 2 (Python): <1s validation, PBS/MBS compliance, clinical safety
- [ ] Layer 3 (AI): 3-5s validation, educational feedback
- [ ] Unified API endpoint functional
- [ ] 100+ test cases pass (Zod), ≥70% coverage (Python)

---

### Phase 3: Backend Completion (18-22 hours)
**Goal**: Build EMR-specific APIs and database models

| Task | Hours | Status | Dependencies |
|------|-------|--------|--------------|
| [TASK 3.1](phase3-backend/TASK_3.1_Database_Models.md) | 4 | ⏳ Not Started | None |
| [TASK 3.2](phase3-backend/TASK_3.2_EMR_Session_APIs.md) | 6 | ⏳ Not Started | TASK 3.1 |
| [TASK 3.3](phase3-backend/TASK_3.3_Prescription_Pathology_APIs.md) | 4 | ⏳ Not Started | TASK 3.1 |
| [TASK 3.4](phase3-backend/TASK_3.4_Progress_Analytics_API.md) | 4 | ⏳ Not Started | TASK 3.2 |
| [TASK 3.5](phase3-backend/TASK_3.5_Backend_Testing.md) | 2 | ⏳ Not Started | TASK 3.2, 3.3, 3.4 |

**Phase Completion Criteria:**
- [ ] 5 new database models (EMRSession, SOAPNote, Prescription, PathologyOrder, MockPatient)
- [ ] 15+ API endpoints implemented
- [ ] OpenAPI docs updated
- [ ] ≥70% test coverage
- [ ] 100% test pass rate
- [ ] Response times meet SLAs (<400ms)

---

### Phase 4: Integration & E2E Testing (10-12 hours)
**Goal**: Connect frontend to backend, implement E2E tests

| Task | Hours | Status | Dependencies |
|------|-------|--------|--------------|
| [TASK 4.1](phase4-integration/TASK_4.1_Frontend_Backend_Integration.md) | 4 | ⏳ Not Started | TASK 1.4, 3.2, 3.3 |
| [TASK 4.2](phase4-integration/TASK_4.2_E2E_Testing.md) | 6 | ⏳ Not Started | TASK 4.1 |

**Phase Completion Criteria:**
- [ ] TanStack Query API hooks functional
- [ ] JWT authentication working
- [ ] Auto-save operational (30s debounce)
- [ ] E2E tests pass (Cerner session, Epic session, prescription workflow)
- [ ] Tests run in <5 minutes

---

### Phase 5: Polish & Deployment (5-8 hours)
**Goal**: Optimize performance, audit security, prepare deployment

| Task | Hours | Status | Dependencies |
|------|-------|--------|--------------|
| [TASK 5.1](phase5-polish/TASK_5.1_Performance_Optimization.md) | 3 | ⏳ Not Started | TASK 4.1 |
| [TASK 5.2](phase5-polish/TASK_5.2_Security_Audit.md) | 2 | ⏳ Not Started | TASK 4.1 |
| [TASK 5.3](phase5-polish/TASK_5.3_Docker_Deployment.md) | 3 | ⏳ Not Started | TASK 5.1, 5.2 |

**Phase Completion Criteria:**
- [ ] Bundle size <500KB gzipped
- [ ] Lighthouse Performance ≥90
- [ ] No security vulnerabilities (SQL injection, XSS)
- [ ] Docker images build successfully
- [ ] Deployment documentation complete

---

## Critical Path

**Sequential execution recommended:**

1. **Frontend Core** (TASK 1.1 → 1.3 → 1.4)
   - Build Cerner components first
   - Add state management
   - Implement hooks (especially auto-save, validation)

2. **Validation Pipeline** (TASK 2.2 → 2.3 → 2.4)
   - PBS/MBS validators (backend)
   - AI validation integration
   - Unified API endpoint

3. **Backend Infrastructure** (TASK 3.1 → 3.2 → 3.3)
   - Database models
   - Session + SOAP note APIs
   - Prescription + pathology APIs

4. **Integration** (TASK 4.1 → 4.2)
   - Connect frontend to backend
   - E2E tests to validate full workflows

5. **Polish** (TASK 5.1 → 5.2 → 5.3)
   - Performance optimization
   - Security audit
   - Deployment

**Parallel opportunities:**
- TASK 1.2 (Epic) can run parallel to TASK 2.2 (PBS/MBS validators)
- TASK 3.3 (Prescriptions API) can run parallel to TASK 1.5 (Styling)

---

## Agent OS Integration

### Expert Agents to Use

Per `/home/dev/.claude/CLAUDE.md` requirements:

| Phase | Agent Type | Tasks |
|-------|-----------|-------|
| Phase 1 | `flutter-desktop-expert` (adapt for React) | TASK 1.1-1.5 |
| Phase 2 | `rust-ffi-expert` (adapt for Python validation) | TASK 2.1-2.4 |
| Phase 3 | `rust-ffi-expert` (backend APIs) | TASK 3.1-3.5 |
| Phase 4 | `testing-qa-expert` | TASK 4.1-4.2 |
| Phase 5 | `security-compliance-expert` | TASK 5.1-5.3 |

**Alternative**: Use `general-purpose` agent with explicit constraints from PROJECT_CONSTRAINTS.md

### Delegation Workflow (CRITICAL)

**Before delegating ANY task:**

1. ✅ **Front-load context**: Agent must read `/home/dev/Development/irStudy/constraints/README.md` first
2. ✅ **Provide examples**: Reference existing code patterns in delegation prompt
3. ✅ **Explicit constraints**: Include what TO do and what NOT to do
4. ✅ **Validation checklist**: Agent must self-validate before returning
5. ✅ **Incremental validation**: PM validates after each task, don't batch

**Example delegation prompt template:**
```
Agent Task: [Task Name from MD file]

CONSTRAINTS:
1. Read /home/dev/Development/irStudy/constraints/README.md FIRST
2. Search for existing patterns: [specific files to reference]
3. Security: [specific security requirements]
4. Performance: [specific performance targets]
5. Validation checklist:
   - [ ] 0 compilation errors
   - [ ] ≥70% test coverage
   - [ ] 100% test pass rate
   - [ ] [task-specific criteria]

DELIVERABLES: [from task MD file]
ACCEPTANCE CRITERIA: [from task MD file]

Search for existing code at: [specific paths]
Follow patterns from: [specific example files]
```

---

## Quality Gates

### After Each Task

**Run these checks before marking task complete:**

1. **Compilation**:
   - Frontend: `cd /home/dev/Development/irStudy/emr-frontend && npm run type-check`
   - Backend: `cd /home/dev/Development/irStudy/backend && python -m mypy src/`

2. **Tests**:
   - Frontend: `npm run test` (100% pass rate)
   - Backend: `pytest --cov=src tests/ --cov-report=term-missing` (≥70% coverage, 100% pass)

3. **Linting**:
   - Frontend: `npm run lint`
   - Backend: `ruff check src/`

4. **Manual Smoke Test**: Complete one workflow end-to-end

### After Each Phase

**Additional checks:**

1. **Security Scan**: Run `safety check` (Python) or `npm audit` (Node)
2. **Performance**: Measure API response times, frontend bundle size
3. **Documentation**: Update README with new features
4. **Integration**: Test with previous phases

---

## Success Metrics

### MVP Definition (Must Have)

✅ **Minimum Viable Product (40-50 hours):**
- [ ] Cerner UI functional with SOAP note editor
- [ ] All 3 validation layers working
- [ ] PBS prescription validation
- [ ] Session management (start, save, complete)
- [ ] Educational AI feedback
- [ ] Basic E2E tests pass

### Production Ready (100-125 hours)

✅ **All MVP + Additional:**
- [ ] Epic UI complete
- [ ] Pathology ordering functional
- [ ] Progress tracking analytics
- [ ] Full E2E test suite
- [ ] Performance optimized (Lighthouse ≥90)
- [ ] Security audit passed
- [ ] Docker deployment ready
- [ ] WCAG 2.1 AA accessibility

---

## Risk Mitigation

### High Risk Areas

| Risk | Mitigation |
|------|------------|
| **AI Validation Cost** | Implement caching, skip Layer 3 if Layer 2 has critical errors, use test API keys during development |
| **PBS/MBS Data Accuracy** | Start with mock databases (20+ medications, 15+ tests), plan for real API integration later |
| **Performance (Layer 3)** | Set timeout at 10s, implement loading states, allow users to skip AI validation |
| **Frontend-Backend Auth** | Use existing JWT from main irStudy platform, reuse auth logic |
| **E2E Test Flakiness** | Use Playwright wait strategies, implement retry logic, clean test data |

### Blocked Task Resolution

If a task is blocked:
1. Document blocker in task MD file
2. Skip to parallel task if available
3. Create workaround (mock data, stub implementation)
4. Continue with warning flag
5. Return to blocked task when unblocked

---

## Progress Tracking

### Update This Table After Each Task

| Task ID | Status | Start Date | End Date | Actual Hours | Notes |
|---------|--------|------------|----------|--------------|-------|
| TASK 1.1 | ⏳ Not Started | - | - | - | - |
| TASK 1.2 | ⏳ Not Started | - | - | - | - |
| TASK 1.3 | ⏳ Not Started | - | - | - | - |
| TASK 1.4 | ⏳ Not Started | - | - | - | - |
| TASK 1.5 | ⏳ Not Started | - | - | - | - |
| TASK 2.1 | ⏳ Not Started | - | - | - | - |
| TASK 2.2 | ⏳ Not Started | - | - | - | - |
| TASK 2.3 | ⏳ Not Started | - | - | - | - |
| TASK 2.4 | ⏳ Not Started | - | - | - | - |
| TASK 3.1 | ⏳ Not Started | - | - | - | - |
| TASK 3.2 | ⏳ Not Started | - | - | - | - |
| TASK 3.3 | ⏳ Not Started | - | - | - | - |
| TASK 3.4 | ⏳ Not Started | - | - | - | - |
| TASK 3.5 | ⏳ Not Started | - | - | - | - |
| TASK 4.1 | ⏳ Not Started | - | - | - | - |
| TASK 4.2 | ⏳ Not Started | - | - | - | - |
| TASK 5.1 | ⏳ Not Started | - | - | - | - |
| TASK 5.2 | ⏳ Not Started | - | - | - | - |
| TASK 5.3 | ⏳ Not Started | - | - | - | - |

**Legend:**
- ⏳ Not Started
- 🔄 In Progress
- ✅ Complete
- ⚠️ Blocked
- ❌ Failed (requires rework)

---

## Next Steps

### To Start Implementation:

1. **Read this master plan completely**
2. **Review constraints**: `/home/dev/Development/irStudy/constraints/README.md`
3. **Start with TASK 1.1**: [Complete Cerner Components](phase1-frontend/TASK_1.1_Complete_Cerner_Components.md)
4. **Use Agent OS workflow**: Delegate → Agent validates → PM validates → Next task
5. **Update progress table** after each task completion

### Recommended Sequence:

**Week 1 (40 hours):**
- Complete Phase 1 (Frontend): TASK 1.1 → 1.5

**Week 2 (25 hours):**
- Complete Phase 2 (Validation): TASK 2.1 → 2.4

**Week 3 (22 hours):**
- Complete Phase 3 (Backend): TASK 3.1 → 3.5

**Week 4 (20 hours):**
- Complete Phase 4 + 5 (Integration + Polish): TASK 4.1 → 5.3

**Total: ~4 weeks for production-ready system**

---

## External Resources

### PRD Documentation
- Master PRD: `/home/dev/Development/irStudy/emr-practice-system/prd/00_MASTER_EMR_PRD.md`
- Cerner UI: `/home/dev/Development/irStudy/emr-practice-system/prd/01_CERNER_POWERCHART_UI_PRD.md`
- Epic UI: `/home/dev/Development/irStudy/emr-practice-system/prd/02_EPIC_EHR_UI_PRD.md`
- Backend API: `/home/dev/Development/irStudy/emr-practice-system/prd/03_BACKEND_API_PRD.md`
- Validation Rules: `/home/dev/Development/irStudy/emr-practice-system/validation-rules/VALIDATION_RULES_COMPREHENSIVE.md`
- Testing Strategy: `/home/dev/Development/irStudy/emr-practice-system/prd/04_TESTING_STRATEGY_PRD.md`

### Australian Medical Resources
- PBS: https://pbs.gov.au
- MBS: https://mbsonline.gov.au
- eTG: https://tg.org.au
- AMH: https://amh.net.au

### Technical Documentation
- FastAPI: https://fastapi.tiangolo.com
- React: https://react.dev
- TanStack Query: https://tanstack.com/query/latest
- Zod: https://zod.dev
- Anthropic: https://docs.anthropic.com

---

**Master Plan Version**: 1.0
**Last Updated**: 2026-02-04
**Next Review**: After Phase 1 completion
**Status**: ✅ Ready for Execution

Start with [TASK 1.1: Complete Cerner Components](phase1-frontend/TASK_1.1_Complete_Cerner_Components.md) →
