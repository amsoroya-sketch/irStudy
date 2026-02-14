# Phase 1 MVP - Quick Start Guide
**Get Started in 5 Minutes**

**Last Updated:** 2026-02-07

---

## 🚀 First 5 Minutes

### 1. What is Phase 1 MVP? (30 seconds)

**Goal:** Deliver production-ready medical education platform for AMC exam prep

**Timeline:** 3 weeks (Feb 7-27, 2026)

**Deliverables:**
- 1,208 MCQs + 210 OSCEs + 140 Study Cards
- 3,168 medical images linked to questions
- Progress tracking with analytics
- JWT authentication + HIPAA security

---

### 2. Your First Action (60 seconds)

**If you are a:**

**Project Manager:**
→ Read [02_MASTER_PLAN.md](./02_MASTER_PLAN.md) Executive Summary (10 min)

**Backend Developer:**
→ Read [TASK_001_API_SECURITY_AUDIT.md](./TASK_001_API_SECURITY_AUDIT.md) (12 min)

**Frontend Developer:**
→ Read [TASK_006_QUIZ_INTERFACE_REDESIGN.md](./TASK_006_QUIZ_INTERFACE_REDESIGN.md) (12 min)

**QA/DevOps:**
→ Read [TASK_010_E2E_TESTING_SUITE.md](./TASK_010_E2E_TESTING_SUITE.md) (12 min)

---

### 3. Verify Infrastructure (2 minutes)

**Check services are running:**

```bash
cd /home/dev/Development/irStudy

# Verify all services operational
docker ps
# Expected: postgres (5433), redis (6 nodes), qdrant (6333), vault (8200)

# Verify database content
docker exec -it amc-postgres-dev psql -U amc_user -d irstudy_medical -c "SELECT COUNT(*) FROM mcqs;"
# Expected: 1208

docker exec -it amc-postgres-dev psql -U amc_user -d irstudy_medical -c "SELECT COUNT(*) FROM osces;"
# Expected: 210

docker exec -it amc-postgres-dev psql -U amc_user -d irstudy_medical -c "SELECT COUNT(*) FROM study_cards;"
# Expected: 140

# Verify images
find data/medical_images -type f -name "*.jpg" | wc -l
# Expected: ~3168
```

**If any service is down:**
→ Read [INFRASTRUCTURE_SETUP_COMPLETE_2026-02-07.md](../../INFRASTRUCTURE_SETUP_COMPLETE_2026-02-07.md)

---

### 4. Read Project Constraints (2 minutes)

**MANDATORY before any coding:**

```bash
# Read project constraints FIRST
cat constraints/README.md
```

**Key Constraints:**
- ❌ NEVER use American drug names (acetaminophen → paracetamol)
- ✅ ALWAYS validate Australian medical context
- ✅ ALWAYS run tests before committing (100% pass rate)
- ❌ NEVER hardcode credentials
- ✅ ALWAYS use Agent OS delegation templates

---

## 📋 Week-by-Week Workflow

### Week 1: Backend Foundation (Feb 7-13)

**Tasks:** TASK_001 through TASK_005

**Daily Workflow:**

**Day 1-2:** API Security Audit (TASK_001)
```bash
# 1. Read task file
cat planning/phase1-mvp-implementation-feb7-2026/TASK_001_API_SECURITY_AUDIT.md

# 2. Run security scan
cd backend
bandit -r src/ -f json -o security_report.json
safety check

# 3. Fix vulnerabilities
# (Follow TASK_001 checklist)

# 4. Verify zero P0/P1 issues
cat security_report.json | jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")'
# Expected: empty (zero results)
```

**Day 3-4:** Question Management CRUD (TASK_002)
```bash
# 1. Implement MCQ/OSCE APIs
# (Use delegation template from DELEGATION_GUIDE.md)

# 2. Run tests
VAULT_ADDR=http://localhost:8200 VAULT_ROOT_TOKEN=dev-only-token-change-in-prod \
REDIS_URL=redis://localhost:7379 \
pytest backend/tests/test_mcqs.py backend/tests/test_osces.py -v

# 3. Verify 100% pass rate
```

**Day 5:** Study Card System (TASK_003) + Progress Tracking (TASK_004)

**Week 1 Completion Checklist:**
- [ ] All 5 tasks completed
- [ ] 100% test pass rate
- [ ] Zero P0/P1 security vulnerabilities
- [ ] API response time <200ms

---

### Week 2: Frontend Core (Feb 14-20)

**Tasks:** TASK_006 through TASK_009

**Daily Workflow:**

**Day 1-2:** Quiz Interface (TASK_006)
```bash
# 1. Create React components
cd frontend
npm run dev  # Start development server

# 2. Test manually
# → Navigate to http://localhost:5173/practice
# → Select MCQ practice
# → Verify timer, image display, answer submission

# 3. Run type checking
npm run type-check
# Expected: 0 errors
```

**Day 3:** Citation Display (TASK_007)

**Day 4:** Performance Dashboard (TASK_008)

**Day 5:** Mobile Responsive (TASK_009)

**Week 2 Completion Checklist:**
- [ ] All 4 tasks completed
- [ ] Lighthouse score >90 (mobile)
- [ ] All images loading correctly
- [ ] Dashboard charts rendering

---

### Week 3: Integration & Polish (Feb 21-27)

**Tasks:** TASK_010 through TASK_014

**Daily Workflow:**

**Day 1-2:** E2E Testing (TASK_010)
```bash
# 1. Run Playwright tests
cd frontend
npx playwright test

# 2. Verify critical paths pass
npx playwright test --grep "MCQ practice flow"
npx playwright test --grep "Study card review"

# Expected: 100% pass rate
```

**Day 3:** RAG Explanation Engine (TASK_011)

**Day 4:** Load Testing (TASK_012)
```bash
# Run load test
cd backend
locust -f tests/load_test.py --host http://localhost:8000

# Web UI: http://localhost:8089
# Test: 500 concurrent users
# Target: <2s page load, <200ms API response
```

**Day 5:** Deployment Pipeline (TASK_013) + MVP Launch (TASK_014)

**Week 3 Completion Checklist:**
- [ ] E2E tests passing (100%)
- [ ] Load test: 500 users, <2s page load
- [ ] Production deployment successful
- [ ] 50 beta users onboarded

---

## 🎯 Common Workflows

### Starting a New Task

```bash
# 1. Read task file completely
cat planning/phase1-mvp-implementation-feb7-2026/TASK_XXX_TASK_NAME.md

# 2. Check dependencies completed
cat planning/phase1-mvp-implementation-feb7-2026/DEPENDENCIES_MAP.md

# 3. Copy Agent OS delegation template
cat planning/phase1-mvp-implementation-feb7-2026/DELEGATION_GUIDE.md | grep -A 50 "TASK_XXX"

# 4. Read PROJECT_CONSTRAINTS.md FIRST
cat constraints/README.md

# 5. Search for similar existing code
grep -r "similar_pattern" backend/src/

# 6. Execute task (use expert agent)

# 7. Validate before returning
pytest backend/tests/  # For backend tasks
npm run type-check      # For frontend tasks
```

---

### Updating Progress

```bash
# Daily standup: Update task checklist
vim planning/phase1-mvp-implementation-feb7-2026/04_TASK_CHECKLIST.md

# Mark task as complete
# Change: - [ ] TASK_XXX
# To:     - [x] TASK_XXX ✅ (2026-02-XX)
```

---

### Running Full Test Suite

```bash
# Backend tests
cd backend
VAULT_ADDR=http://localhost:8200 VAULT_ROOT_TOKEN=dev-only-token-change-in-prod \
REDIS_URL=redis://localhost:7379 \
pytest --cov=src --cov-report=html

# Expected: 100% pass rate, >70% coverage

# Frontend tests
cd frontend
npm run test
npm run type-check

# E2E tests
cd frontend
npx playwright test

# Security scan
cd backend
bandit -r src/
safety check
```

---

### Checking Quality Gates

```bash
# Week 1 Gate
cat planning/phase1-mvp-implementation-feb7-2026/QUALITY_GATES.md

# Verify:
# - All backend APIs operational
# - Zero P0/P1 security vulnerabilities
# - 100% test pass rate
# - API response <200ms
```

---

## 🚨 Troubleshooting

### Database Connection Issues

```bash
# Verify PostgreSQL running
docker ps | grep postgres

# Test connection
docker exec -it amc-postgres-dev psql -U amc_user -d irstudy_medical -c "SELECT 1;"

# If fails, check credentials
cat backend/.env | grep DATABASE
```

---

### Redis Connection Issues

```bash
# Verify Redis cluster running
docker ps | grep redis

# Test connection
docker exec -it redis-node-1 redis-cli -c PING
# Expected: PONG

# Check cluster status
docker exec -it redis-node-1 redis-cli -c CLUSTER INFO
```

---

### Frontend Build Errors

```bash
# Clear cache
cd frontend
rm -rf node_modules package-lock.json
npm install

# Run type checking
npm run type-check

# Check for TypeScript errors
npm run build
```

---

### Tests Failing

```bash
# Backend: Check database migrations
cd backend
alembic current
alembic upgrade head

# Backend: Check test database
pytest backend/tests/test_mcqs.py -v -s

# Frontend: Check imports
cd frontend
npm run type-check
```

---

## 📚 Essential Reading by Role

### Project Manager (60 min total)

**Must Read:**
1. [02_MASTER_PLAN.md](./02_MASTER_PLAN.md) - Full plan (20 min)
2. [DELEGATION_GUIDE.md](./DELEGATION_GUIDE.md) - Agent OS templates (20 min)
3. [RISK_REGISTER.md](./RISK_REGISTER.md) - Risk matrix (10 min)
4. [04_TASK_CHECKLIST.md](./04_TASK_CHECKLIST.md) - Progress tracker (5 min)

**Daily Check:**
- Task completion status (04_TASK_CHECKLIST.md)
- Active risks (RISK_REGISTER.md)

---

### Backend Developer (90 min total)

**Must Read:**
1. This file (5 min)
2. [constraints/README.md](../../constraints/README.md) - Project constraints (15 min)
3. Your assigned TASK files (60 min total)
4. [QUALITY_GATES.md](./QUALITY_GATES.md) - Validation criteria (10 min)

**Before Each Task:**
- Read TASK_XXX.md completely
- Search for existing code patterns
- Copy Agent OS delegation template

---

### Frontend Developer (90 min total)

**Must Read:**
1. This file (5 min)
2. [constraints/README.md](../../constraints/README.md) - Project constraints (15 min)
3. Your assigned TASK files (60 min total)
4. [QUALITY_GATES.md](./QUALITY_GATES.md) - Validation criteria (10 min)

**Before Each Task:**
- Review Material-UI v6 patterns
- Check image library status
- Verify API endpoints available

---

### QA/DevOps (75 min total)

**Must Read:**
1. This file (5 min)
2. [QUALITY_GATES.md](./QUALITY_GATES.md) - Complete validation framework (15 min)
3. Your assigned TASK files (45 min total)
4. [SUCCESS_METRICS.md](./SUCCESS_METRICS.md) - Target KPIs (10 min)

**Daily:**
- Run full test suite
- Check quality gates
- Monitor performance metrics

---

## ⚡ Critical Paths

### Path 1: Backend Foundation → Frontend Core

```
TASK_001 (Security Audit)
    ↓
TASK_002 (MCQ/OSCE CRUD) ────┐
    ↓                        │
TASK_003 (Study Cards) ──────┤
    ↓                        │
TASK_004 (Progress Track) ───┤
    ↓                        ↓
TASK_005 (SM-2 Engine)   TASK_006 (Quiz UI)
                             ↓
                         TASK_007 (Citations)
                             ↓
                         TASK_008 (Dashboard)
                             ↓
                         TASK_009 (Mobile)
```

**CRITICAL:** TASK_001 and TASK_002 block all frontend work

---

### Path 2: Testing & Deployment

```
TASK_009 (Mobile Responsive)
    ↓
TASK_010 (E2E Testing)
    ↓
TASK_012 (Load Testing)
    ↓
TASK_013 (Deployment Pipeline)
    ↓
TASK_014 (MVP Launch)
```

**CRITICAL:** TASK_013 deployment blocks TASK_014 launch

---

## 🎯 Success Checklist

**Phase 1 MVP Complete When:**

- [x] Infrastructure operational (Database: ✅, Redis: ✅, Images: ✅)
- [ ] Week 1: All backend APIs functional (5/5 tasks)
- [ ] Week 2: All frontend interfaces complete (4/4 tasks)
- [ ] Week 3: Testing + deployment operational (5/5 tasks)
- [ ] 100% test pass rate (backend + frontend + E2E)
- [ ] Zero P0/P1 security vulnerabilities
- [ ] Load test: 500 users, <2s page load
- [ ] 50 beta users onboarded
- [ ] Production deployment successful

---

## 📞 Quick Links

**Full Documentation:**
- [00_README.md](./00_README.md) - Main entry point
- [01_INDEX.md](./01_INDEX.md) - Complete file index
- [02_MASTER_PLAN.md](./02_MASTER_PLAN.md) - Executive summary

**Infrastructure:**
- [INFRASTRUCTURE_SETUP_COMPLETE_2026-02-07.md](../../INFRASTRUCTURE_SETUP_COMPLETE_2026-02-07.md)
- [CRITICAL_FINDINGS_2026-02-07.md](../../CRITICAL_FINDINGS_2026-02-07.md)

**Planning Package:**
- [PLANNING_PACKAGE_INDEX.md](../../PLANNING_PACKAGE_INDEX.md)
- [COMPREHENSIVE_PLATFORM_PLAN_EXTENDED_SECURITY.md](../../COMPREHENSIVE_PLATFORM_PLAN_EXTENDED_SECURITY.md)

---

## 🚀 Ready to Start?

**Your next action:**

1. ✅ You've read this Quick Start guide (5 min)
2. → Read [04_TASK_CHECKLIST.md](./04_TASK_CHECKLIST.md) (2 min)
3. → Read your first assigned TASK_XXX.md file (12 min)
4. → Copy Agent OS delegation template from [DELEGATION_GUIDE.md](./DELEGATION_GUIDE.md)
5. → Execute with expert agents

**Questions?** Everything you need is in this folder. Start with [00_README.md](./00_README.md).

---

**Last Updated:** 2026-02-07
**Est. Read Time:** 5 minutes
**Status:** ✅ Complete
