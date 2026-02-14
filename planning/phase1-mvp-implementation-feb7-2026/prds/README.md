# Phase 1 MVP - Ralph-Compatible PRDs
**Product Requirements Documents for Autonomous Execution**

**Version:** 1.0
**Date:** 2026-02-07
**Status:** 🟡 Ready for Ralph Execution
**Total PRDs:** 14 (0/14 complete)

---

## 📚 What Are These PRDs?

These PRD files are **Ralph-compatible** versions of the comprehensive task files in the parent directory. They are optimized for **autonomous AI agent execution** following the Ralph loop pattern.

### Key Differences from Regular Task Files:

✅ **Directive Language**: Uses "EXECUTE NOW" commands instead of questions
✅ **Exact Commands**: Copy-paste executable bash/Python/TypeScript code
✅ **No Questions**: Zero "Would you like..." phrasing to prevent premature exit
✅ **Clear Success Criteria**: Specific checkboxes for when to stop
✅ **Validation Commands**: Explicit verification with expected output

---

## 🗂️ PRD Index

### Week 1: Backend Foundation (5 PRDs, 22-29 hours)

| # | PRD File | Duration | Priority | Dependencies | Status |
|---|----------|----------|----------|--------------|--------|
| 001 | [API Security Audit](./PRD_TASK_001_API_SECURITY_AUDIT.md) | 6-8h | P0-Critical | None | 🟡 Not Started |
| 002 | [Question Management CRUD](./PRD_TASK_002_QUESTION_MANAGEMENT_CRUD.md) | 6-8h | P0-Critical | TASK_001 | 🟡 Not Started |
| 003 | [Study Card System](./PRD_TASK_003_STUDY_CARD_SYSTEM.md) | 4-5h | P1-High | TASK_001 | 🟡 Not Started |
| 004 | [User Progress Tracking](./PRD_TASK_004_USER_PROGRESS_TRACKING.md) | 4-5h | P1-High | TASK_002, TASK_003 | 🟡 Not Started |
| 005 | [Spaced Repetition Engine](./PRD_TASK_005_SPACED_REPETITION_ENGINE.md) | 3-4h | P1-High | TASK_003 | 🟡 Not Started |

### Week 2: Frontend Core (4 PRDs, 21-27 hours)

| # | PRD File | Duration | Priority | Dependencies | Status |
|---|----------|----------|----------|--------------|--------|
| 006 | [Quiz Interface Redesign](./PRD_TASK_006_QUIZ_INTERFACE_REDESIGN.md) | 8-10h | P0-Critical | TASK_002 | 🟡 Not Started |
| 007 | [Citation Display Component](./PRD_TASK_007_CITATION_DISPLAY_COMPONENT.md) | 3-4h | P1-High | TASK_006 | 🟡 Not Started |
| 008 | [Performance Dashboard](./PRD_TASK_008_PERFORMANCE_DASHBOARD.md) | 6-8h | P1-High | TASK_004 | 🟡 Not Started |
| 009 | [Mobile Responsive Design](./PRD_TASK_009_MOBILE_RESPONSIVE_DESIGN.md) | 4-5h | P1-High | TASK_006, TASK_008 | 🟡 Not Started |

### Week 3: Integration & Polish (5 PRDs, 24-31 hours)

| # | PRD File | Duration | Priority | Dependencies | Status |
|---|----------|----------|----------|--------------|--------|
| 010 | [E2E Testing Suite](./PRD_TASK_010_E2E_TESTING_SUITE.md) | 6-8h | P0-Critical | TASK_009 | 🟡 Not Started |
| 011 | [RAG Explanation Engine](./PRD_TASK_011_RAG_EXPLANATION_ENGINE.md) | 5-6h | P1-High | TASK_002 | 🟡 Not Started |
| 012 | [Load Testing & Optimization](./PRD_TASK_012_LOAD_TESTING_OPTIMIZATION.md) | 4-5h | P1-High | TASK_010 | 🟡 Not Started |
| 013 | [Deployment Pipeline](./PRD_TASK_013_DEPLOYMENT_PIPELINE.md) | 5-6h | P0-Critical | TASK_012 | 🟡 Not Started |
| 014 | [MVP Validation & Launch](./PRD_TASK_014_MVP_VALIDATION_LAUNCH.md) | 4-5h | P0-Critical | TASK_013 | 🟡 Not Started |

---

## 🔗 Critical Path

```
TASK_001 → TASK_002 → TASK_006 → TASK_009 → TASK_010 → TASK_012 → TASK_013 → TASK_014
```

**Duration:** 43-55 hours (7-9 working days)
**Buffer:** 8 days (53% slack in 3-week schedule)

---

## 🚀 How to Use with Ralph

### Initial Setup

```bash
# Navigate to irStudy project
cd /home/dev/Development/irStudy

# Ensure Ralph is installed
ralph --version  # Should show v0.9.9+

# Initialize Ralph session
ralph --clean  # Reset any stale state
```

### Execute a Specific PRD

```bash
# Update PROMPT.md to point to current PRD
echo "**CURRENT TASK**: Read /home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_001_API_SECURITY_AUDIT.md

**EXECUTE IMMEDIATELY**
" > PROMPT.md

# Start Ralph (with monitoring recommended)
ralph --monitor --calls 50
```

### Monitor Progress

```bash
# Check @fix_plan.md for task completion status
cat @fix_plan.md | grep "TASK_"

# Check quality gates
grep "Gate.*Status" planning/phase1-mvp-implementation-feb7-2026/04_TASK_CHECKLIST.md
```

---

## 📋 Ralph Execution Checklist

**Before Starting Each PRD:**

- [ ] All dependencies complete (check [DEPENDENCIES_MAP.md](../DEPENDENCIES_MAP.md))
- [ ] Previous task quality gates passed
- [ ] PROMPT.md updated to point to current PRD
- [ ] Ralph state clean (run `ralph --clean` if needed)
- [ ] Environment configured (database, Redis, Qdrant operational)

**During Execution:**

- [ ] Ralph monitoring active (`ralph-monitor` or `ralph --monitor`)
- [ ] Logs being written to `logs/` directory
- [ ] Circuit breaker not triggered (check `ralph --circuit-status`)

**After Completion:**

- [ ] All success criteria checkboxes ✅
- [ ] Quality gates passed (100% test pass rate)
- [ ] @fix_plan.md updated (TASK_NNN: ✅ DONE)
- [ ] Git commit created with conventional commit message
- [ ] Move to next PRD in sequence

---

## 🎯 Quality Gates

### Week 1 Gate (Target: Feb 13, 2026)
- [ ] All 5 backend PRDs complete (TASK_001-005)
- [ ] 100% test pass rate (pytest)
- [ ] Zero P0/P1 security vulnerabilities
- [ ] API response time <200ms (95th percentile)

### Week 2 Gate (Target: Feb 20, 2026)
- [ ] All 4 frontend PRDs complete (TASK_006-009)
- [ ] Lighthouse score >90 (mobile + desktop)
- [ ] TypeScript type checking: 0 errors
- [ ] All 3,168 images loading correctly

### Week 3 Gate - FINAL (Target: Feb 27, 2026)
- [ ] All 5 integration PRDs complete (TASK_010-014)
- [ ] E2E tests: 100% pass rate (20+ scenarios)
- [ ] Load test: 500 concurrent users, <2s page load
- [ ] Production deployment successful
- [ ] 50 beta users onboarded and active

---

## 📚 Additional Resources

**Project Documentation:**
- [00_README.md](../00_README.md) - Main entry point
- [02_MASTER_PLAN.md](../02_MASTER_PLAN.md) - Executive summary & 3-week timeline
- [03_QUICK_START.md](../03_QUICK_START.md) - Get started in 5 minutes
- [04_TASK_CHECKLIST.md](../04_TASK_CHECKLIST.md) - Daily progress tracker
- [DEPENDENCIES_MAP.md](../DEPENDENCIES_MAP.md) - Visual dependency chart

**Constraints & Standards:**
- [PROJECT_CONSTRAINTS.md](/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md) - Top 10 critical constraints
- [constraints/README.md](/home/dev/Development/irStudy/constraints/README.md) - Detailed constraint modules
- [constraints/13-ralph-execution.md](/home/dev/Development/irStudy/constraints/13-ralph-execution.md) - Ralph-specific rules

**Ralph Documentation:**
- [Ralph Global Config](~/.ralph/CLAUDE.md) - Agent OS best practices
- [Ralph CLAUDE.md](/home/dev/Development/ralph-claude-code/CLAUDE.md) - Ralph loop documentation

---

## 🆘 Troubleshooting

### Ralph Exits Prematurely

**Symptom:** Ralph completes loop but task not actually done
**Causes:**
- PROMPT.md uses "Would you like..." phrasing (triggers exit)
- Success criteria too vague (Ralph thinks it's done)
- Stale `.exit_signals` file from previous run

**Solutions:**
```bash
# 1. Clean Ralph state
ralph --clean

# 2. Verify PROMPT.md has directive language
grep -E "(Would you|Should I|Please)" PROMPT.md  # Should return empty

# 3. Check PRD has explicit "EXECUTE NOW" commands
grep "EXECUTE NOW" planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_*.md
```

### Tests Failing

**Symptom:** Quality gate blocked due to test failures
**Solutions:**
```bash
# Backend tests
cd backend
pytest -v tests/

# Frontend tests
cd frontend
npm test

# Check test pass rate
grep -A 5 "test pass rate" logs/latest.log
```

### Dependencies Not Met

**Symptom:** PRD references endpoints/components that don't exist
**Solutions:**
```bash
# Check dependency map
cat planning/phase1-mvp-implementation-feb7-2026/DEPENDENCIES_MAP.md

# Verify previous task complete
grep "TASK_00[1-9].*DONE" @fix_plan.md
```

---

## 📞 Quick Commands

```bash
# Start current PRD with Ralph
ralph --monitor --calls 50

# Check progress
cat @fix_plan.md | grep "✅"

# Reset Ralph state
ralph --clean

# Check quality gates
cat planning/phase1-mvp-implementation-feb7-2026/04_TASK_CHECKLIST.md | grep -A 10 "Quality Gate"

# Run all tests
cd backend && pytest -v && cd ../frontend && npm test

# Check security scans
cd backend && bandit -r src/ && safety check
```

---

**Last Updated:** 2026-02-07
**Next Update:** Daily (as PRDs are completed)
**Maintained By:** Project Manager + Claude Code + Ralph

**Progress:** 0/14 PRDs complete (0%)
**Target Completion:** Feb 27, 2026
**Status:** 🟡 Ready for Execution
