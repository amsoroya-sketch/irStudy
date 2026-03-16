# Gap Analysis PRDs - Implementation Plan

**Created**: 2026-03-13
**Purpose**: Systematic resolution of 34 critical gaps identified in platform analysis
**Total Effort**: 100-120 hours across 4 phases

---

## FOLDER STRUCTURE

```
gap-analysis-prds/
├── README.md (this file)
├── RALPH_EXECUTION_PLAN.md (overall execution strategy)
├── phase1-p0-blockers/ (20-30 hours - CRITICAL)
│   ├── PRD_GAP_001_INFRASTRUCTURE_DEPLOYMENT.md (Vault + Redis - 6h)
│   ├── PRD_GAP_002_EMR_API_ENDPOINTS.md (6 REST endpoints - 8-12h)
│   ├── PRD_GAP_003_FRONTEND_BUILD_FIXES.md (19 TypeScript errors - 1h)
│   └── PRD_GAP_004_TEST_SUITE_FIXES.md (100% pass rate - 8h)
├── phase2-core-functionality/ (50-64 hours)
│   ├── PRD_GAP_005_AI_OSCE_FRONTEND.md (PRD_005 implementation - 20-24h)
│   ├── PRD_GAP_006_INTEGRATION_LAYER.md (OSCE-to-EMR + dashboard - 14-20h)
│   ├── PRD_GAP_007_WEBSOCKET_COMPLETION.md (PRD_003 remaining - 8h)
│   └── PRD_GAP_008_ERROR_BOUNDARIES_ACCESSIBILITY.md (WCAG 2.2 AA - 8-12h)
├── phase3-production-readiness/ (20-30 hours)
│   ├── PRD_GAP_009_CODE_COVERAGE.md (70% coverage - 20h)
│   ├── PRD_GAP_010_SECURITY_HARDENING.md (0 violations - 6h)
│   └── PRD_GAP_011_PERFORMANCE_VALIDATION.md (All targets met - 4h)
└── phase4-deployment/ (10 hours)
    └── PRD_GAP_012_PRODUCTION_DEPLOYMENT.md (Kubernetes, monitoring - 10h)
```

---

## QUICK START

### Option 1: Automated Ralph Loop (Recommended)
```bash
# Start Ralph loop in tmux session
cd /home/dev/Development/irStudy
tmux new-session -s ralph-gap "bash scripts/ralph-gap-analysis-loop.sh"

# Attach to session to monitor progress
tmux attach -t ralph-gap

# Detach: Ctrl+B, then D
```

### Option 2: Manual PRD Execution
```bash
# Read PRD file
cat gap-analysis-prds/phase1-p0-blockers/PRD_GAP_001_INFRASTRUCTURE_DEPLOYMENT.md

# Implement tasks manually
# Follow implementation tasks section in PRD
# Run tests after each task
# Verify acceptance criteria

# Mark complete when done
```

---

## PHASE 1: P0 CRITICAL BLOCKERS (Week 1)

**Goal**: Unblock all development and deployment

### PRD_GAP_001: Infrastructure Deployment (6 hours)
**Status**: ⏳ PENDING
**Blocks**: All further development

**Tasks**:
1. Deploy Vault server (development mode)
2. Deploy Redis server (Docker, 2.5 GB)
3. Remove .env.dev from git, rotate credentials
4. Fix 127 security tests (currently not executable)

**Acceptance Criteria**:
- [ ] Vault operational at `http://localhost:8200`
- [ ] Redis operational at `localhost:6380`
- [ ] 0 hardcoded credentials in git
- [ ] 127/127 security tests passing

### PRD_GAP_002: EMR API Endpoints (8-12 hours)
**Status**: ⏳ PENDING
**Requires**: PRD_GAP_001 complete

**Tasks**:
1. Create `/backend/src/api/v1/emr/` directory structure
2. Implement 6 REST API endpoints (sessions, dashboard)
3. Write 20+ integration tests
4. Register router in main.py

**Acceptance Criteria**:
- [ ] 6 EMR endpoints operational
- [ ] 20+ tests passing (100%)
- [ ] Frontend can access EMR system

### PRD_GAP_003: Frontend Build Fixes (1 hour)
**Status**: ⏳ PENDING
**Can run in parallel with GAP_001**

**Tasks**:
1. Fix import path in `useAutoSave.ts:40`
2. Install `lucide-react` and `@types/node`
3. Update Material-UI v7 Grid API
4. Remove 9 unused variables

**Acceptance Criteria**:
- [ ] `npm run build` succeeds with 0 errors
- [ ] Production bundle generated

### PRD_GAP_004: Test Suite Fixes (8 hours)
**Status**: ⏳ PENDING
**Requires**: PRD_GAP_001 complete

**Tasks**:
1. Fix WebSocket import errors (8 files)
2. Expose AI modules in `__init__.py`
3. Install PyJWT dependency
4. Remove 2 hardcoded Anthropic API keys

**Acceptance Criteria**:
- [ ] Test pass rate: 100% (440+ tests)
- [ ] 0 import errors
- [ ] 0 hardcoded credentials

**Phase 1 Complete When**:
- All 4 PRDs complete
- Vault + Redis operational
- Frontend builds
- 100% test pass rate
- EMR API functional

---

## PHASE 2: CORE FUNCTIONALITY (Week 2-3)

**Goal**: Complete AI OSCE frontend and integration layer

### PRD_GAP_005: AI OSCE Frontend (20-24 hours)
Implement PRD_005 (5 features):
- Persona browser with filters
- WebSocket chat interface
- 8-minute session timer
- Results display (AMC rubric)
- Transcript viewer

### PRD_GAP_006: Integration Layer (14-20 hours)
- OSCE-to-EMR converter API
- Unified progress dashboard
- Cross-system E2E tests

### PRD_GAP_007: WebSocket Completion (8 hours)
- Celery Beat periodic sync
- Load testing (100 concurrent sessions)
- Performance benchmarking

### PRD_GAP_008: Error Boundaries & Accessibility (8-12 hours)
- Apply error boundaries to all pages
- Run WCAG 2.2 AA tests (156 tests)
- Fix accessibility violations

---

## PHASE 3: PRODUCTION READINESS (Week 4)

**Goal**: Achieve 70% coverage, 0 security violations, all performance targets

### PRD_GAP_009: Code Coverage to 70% (20 hours)
- Add 110 unit tests
- Integration tests for all systems
- Measure frontend coverage

### PRD_GAP_010: Security Hardening (6 hours)
- Fix 20 security violations
- Implement audit logging (HIPAA requirement)
- Claude API rate limiting

### PRD_GAP_011: Performance Validation (4 hours)
- WebSocket latency benchmarks
- Database query profiling
- Load testing validation

---

## PHASE 4: DEPLOYMENT (Week 5)

**Goal**: Deploy to staging and production

### PRD_GAP_012: Production Deployment (10 hours)
- Kubernetes configuration
- Prometheus + Grafana monitoring
- Staging deployment
- Production deployment

---

## MONITORING PROGRESS

### Check Ralph Loop Status
```bash
# Attach to tmux session
tmux attach -t ralph-gap

# View logs
tail -f logs/ralph-gap-analysis-*.log

# Check state file
cat .ralph-gap-analysis-state.json | jq '.'
```

### Check Quality Gates
```bash
# Test pass rate
cd backend && pytest --tb=short -q

# Frontend build
cd frontend && npm run build

# Security violations
grep -rn "sk-ant-\|password\s*=\s*['\"]" backend/src/ frontend/src/

# Coverage
pytest --cov=backend/src --cov-report=term
```

### Phase Completion Checklist
See `RALPH_EXECUTION_PLAN.md` for detailed checklists

---

## SUCCESS METRICS

**Before (Current State)**:
- Test pass rate: 83.8%
- Code coverage: 35%
- Build errors: 19 TypeScript errors
- Security violations: 20
- EMR System: 20% complete
- AI OSCE System: 60% complete
- Integration: 0% complete

**After (Target State)**:
- Test pass rate: 100%
- Code coverage: ≥70%
- Build errors: 0
- Security violations: 0
- EMR System: 100% complete
- AI OSCE System: 100% complete
- Integration: 100% complete

---

## SUPPORT

**Questions**: Read RALPH_EXECUTION_PLAN.md
**Issues**: Check logs in `logs/ralph-gap-analysis-*.log`
**State**: View `.ralph-gap-analysis-state.json`

---

**Created by**: Comprehensive gap analysis (4 expert agents, 6 hours analysis)
**Validated**: 2026-03-13
**Version**: 1.0
