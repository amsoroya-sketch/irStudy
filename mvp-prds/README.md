# MVP PRDs - Complete Implementation Guide

**Created**: 2026-05-25
**Status**: ✅ READY FOR RALPH EXECUTION
**Standards**: T-RALPH V2.1
**Total Estimated Effort**: 15-20 hours

---

## Overview

This directory contains 3 comprehensive PRDs for achieving MVP launch readiness. All PRDs follow T-RALPH v2.1 standards with:
- Test-First Development (TDD workflow enforced)
- PROJECT_CONSTRAINTS.md integration
- Full test specifications embedded in PRDs
- Detailed validation checklists

---

## PRD Summary

### PRD-MVP-001: Dashboard Backend Validation

**File**: `PRD-MVP-001-DASHBOARD-BACKEND-VALIDATION.md`
**Agent**: testing-qa-expert
**Effort**: 3-4 hours
**Status**: Ready for execution

**Purpose**: Validate existing dashboard backend API and extract service layer for better testability.

**Deliverables**:
- 16 integration tests validated (existing)
- 8 new unit tests for service layer
- Service layer extracted (`src/services/dashboard_service.py`)
- Performance validated (<200ms response time)
- Coverage ≥85%

**Tests**:
- Total: 24 tests (16 integration + 8 unit)
- Coverage: ≥85% lines, ≥80% branches
- Performance: <200ms (p95)

**Dependencies**: None (backend already implemented)

---

### PRD-MVP-002: Dashboard Frontend UI

**File**: `PRD-MVP-002-DASHBOARD-FRONTEND-UI.md`
**Agent**: react-frontend-developer
**Effort**: 8-10 hours
**Status**: Ready for execution

**Purpose**: Build unified dashboard frontend UI displaying aggregated progress across all 4 modules.

**Deliverables**:
- Dashboard API hook (`useDashboardOverview`)
- 6 React components (DashboardPage, OverallProgressCard, ModuleStatsGrid, etc.)
- TypeScript types matching backend schema
- 18 unit/integration tests + 2 E2E tests
- Responsive design (mobile, tablet, desktop)
- WCAG 2.2 AA accessibility

**Tests**:
- Total: 20 tests (18 unit/integration + 2 E2E)
- Coverage: ≥85% lines, ≥80% branches
- Performance: <2s page load

**Dependencies**: PRD-MVP-001 must be complete (backend API validated)

---

### PRD-MVP-003: Content Population MVP

**File**: `PRD-MVP-003-CONTENT-POPULATION-MVP.md`
**Agent**: python-backend-developer
**Effort**: 4-6 hours
**Status**: Ready for execution

**Purpose**: Validate sufficient educational content exists for MVP launch and populate any gaps.

**Deliverables**:
- Content audit script (documents current state)
- Content validation script (8 tests)
- Import scripts for MCQs, OSCEs, EMR personas, Mock Exam templates
- Final content readiness report

**Tests**:
- Total: 12 tests (8 validation + 4 import)
- Content thresholds: ≥200 MCQs, ≥50 OSCEs, ≥100 EMR personas, ≥3 templates
- RAG citation coverage: ≥95%

**Dependencies**: None (uses existing data files)

---

## Execution Order

**Recommended sequence**:

```
[Week 1]
Option 1: Run all 3 PRDs in parallel (if agents available)
  ├── PRD-MVP-001 (testing-qa-expert) [3-4 hours]
  ├── PRD-MVP-002 (react-frontend-developer) [8-10 hours] ← AFTER MVP-001
  └── PRD-MVP-003 (python-backend-developer) [4-6 hours]

Option 2: Sequential execution
  Day 1: PRD-MVP-001 (Dashboard Backend Validation)
  Day 2: PRD-MVP-003 (Content Population)
  Day 3-4: PRD-MVP-002 (Dashboard Frontend UI)

[Week 2]
Integration testing, user onboarding, production deployment
```

---

## Ralph Execution Commands

### PRD-MVP-001: Dashboard Backend Validation

```bash
cd /home/dev/Development/irStudy

# Option 1: Ralph autonomous execution
ralph execute mvp-prds/PRD-MVP-001-DASHBOARD-BACKEND-VALIDATION.md

# Option 2: Manual execution (for testing)
cd backend
./scripts/validate_dashboard_tests.sh
./scripts/validate_dashboard_performance.sh
```

**Expected Outcome**:
- 24/24 tests passing (16 integration + 8 unit)
- Service layer extracted
- Performance <200ms validated
- Coverage ≥85%

---

### PRD-MVP-002: Dashboard Frontend UI

```bash
# Option 1: Ralph autonomous execution
ralph execute mvp-prds/PRD-MVP-002-DASHBOARD-FRONTEND-UI.md

# Option 2: Manual execution
cd frontend
npm test -- dashboard
npx playwright test dashboard.spec.ts
```

**Expected Outcome**:
- 20/20 tests passing (18 unit/integration + 2 E2E)
- Dashboard UI complete and functional
- Responsive design working
- WCAG 2.2 AA compliant

---

### PRD-MVP-003: Content Population MVP

```bash
# Option 1: Ralph autonomous execution
ralph execute mvp-prds/PRD-MVP-003-CONTENT-POPULATION-MVP.md

# Option 2: Manual execution
cd backend
./scripts/audit_mvp_content.sh
./scripts/validate_content_mvp.sh
./scripts/populate_mvp_content.sh
```

**Expected Outcome**:
- 12/12 tests passing (8 validation + 4 import)
- ≥200 MCQs, ≥50 OSCEs, ≥100 EMR personas, ≥3 templates
- 100% RAG citation coverage
- 0 placeholder content

---

## Success Criteria (MVP Launch)

**All 3 PRDs must be COMPLETE before MVP launch:**

### Backend (PRD-MVP-001)
- [x] 685/685 tests passing (100%)
- [x] Dashboard API validated
- [x] Service layer extracted
- [x] Performance <200ms

### Frontend (PRD-MVP-002)
- [ ] Dashboard UI implemented
- [ ] 20/20 tests passing
- [ ] Responsive design working
- [ ] WCAG 2.2 AA compliant

### Content (PRD-MVP-003)
- [ ] Content audit complete
- [ ] ≥200 MCQs (balanced across specialties)
- [ ] ≥50 OSCEs (balanced across specialties)
- [ ] ≥100 EMR personas (13-gate QA validated)
- [ ] ≥3 Mock Exam templates
- [ ] 100% RAG citations (no hallucinations)
- [ ] 0 placeholder content

---

## Quality Gates

**Before MVP Launch, ALL must pass:**

### Compilation
```bash
# Frontend
cd frontend && npx tsc --noEmit
# Expected: 0 errors

# Backend
cd backend && python -m py_compile src/**/*.py
# Expected: 0 errors
```

### Tests
```bash
# Frontend
cd frontend && npm test && npx playwright test
# Expected: All tests passing

# Backend
cd backend && ./run_tests.sh
# Expected: 685/685 passing (100%)
```

### Security
```bash
# No hardcoded credentials
grep -r "api_key\|sk-ant-\|password\s*=" frontend/src/ backend/src/
# Expected: 0 matches

# No hardcoded URLs
grep -r "localhost\|http://\|ws://" frontend/src/components/ frontend/src/api/
# Expected: 0 matches (use environment variables)
```

### Linting
```bash
# Frontend
cd frontend && npm run lint
# Expected: 0 errors, 0 warnings

# Backend
cd backend && ruff check src/
# Expected: All checks passed
```

### Performance
```bash
# Dashboard API
curl -w "@curl-format.txt" "http://localhost:8001/api/v1/dashboard/overview"
# Expected: time_total <0.200s

# Frontend page load
npx playwright test --grep="E2E-1: should load dashboard"
# Expected: Page loads <2s
```

---

## Troubleshooting

### PRD-MVP-001 Issues

**Issue**: Tests fail with database connection error
**Fix**: Ensure PostgreSQL running on port 5433
```bash
docker ps | grep postgres
docker start irstudy-postgres  # If not running
```

**Issue**: Vault tests fail
**Fix**: Ensure Vault running in dev mode
```bash
cd backend
./scripts/start_vault_dev.sh
./scripts/init_vault_secrets.sh
```

---

### PRD-MVP-002 Issues

**Issue**: API hook returns 401 Unauthorized
**Fix**: Ensure JWT token exists in localStorage
```typescript
localStorage.setItem('authToken', 'your-jwt-token');
```

**Issue**: Components don't render
**Fix**: Check Material-UI theme provider wraps app
```typescript
<ThemeProvider theme={theme}>
  <DashboardPage />
</ThemeProvider>
```

---

### PRD-MVP-003 Issues

**Issue**: Import script fails "File not found"
**Fix**: Ensure data files exist
```bash
ls -la data/osces/
ls -la data/emr/patient_personas/
```

**Issue**: Duplicate key violation during import
**Fix**: Clear database and re-import
```bash
psql -U postgres -d irstudy_medical -c "TRUNCATE osces CASCADE;"
python scripts/import_osces.py --source data/osces/ --validate
```

---

## Next Steps After MVP PRDs

**After all 3 PRDs complete, proceed to:**

1. **Integration Testing** (1-2 days)
   - End-to-end user flows
   - Cross-module navigation
   - Performance under load

2. **User Onboarding** (2-3 days)
   - Welcome tour implementation
   - Help documentation
   - Demo data for new users

3. **Production Deployment** (3-5 days)
   - CI/CD pipeline setup
   - Production Vault configuration
   - Monitoring and logging
   - SSL certificates
   - Domain configuration

4. **MVP Launch** 🚀
   - Soft launch to 10 beta users
   - Gather feedback
   - Iterate on pain points
   - Public launch

---

## Documentation Links

**PRD Standards**:
- `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/PRD_STANDARDS_V2_T-RALPH.md`
- `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/RALPH_GLOBAL_CONSTRAINTS.md`

**Project Constraints**:
- `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
- `/home/dev/Development/irStudy/CLAUDE.md`

**Implementation Docs**:
- `DASHBOARD_API_IMPLEMENTATION_COMPLETE.md` (backend implementation details)
- `DASHBOARD_QUICK_START.md` (quick reference guide)
- `MVP_ROADMAP_2026-05-25.md` (full MVP roadmap)

---

## Contact & Support

**Questions?**
- Check PRD-specific troubleshooting sections
- Review PROJECT_CONSTRAINTS.md for patterns
- Consult T-RALPH standards for PRD structure

**Issues?**
- Document issue with error messages
- Check quality gates output
- Review test failure logs

---

**Last Updated**: 2026-05-25
**Version**: 1.0
**Status**: ✅ READY FOR EXECUTION
**Total PRDs**: 3 (all T-RALPH v2.1 compliant)
