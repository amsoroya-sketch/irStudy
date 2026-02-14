# Phase 1 MVP - Task Dependencies Map
**Visual Dependency Chart with Critical Path Analysis**

**Last Updated:** 2026-02-07

---

## 🗺️ Visual Dependency Chart (ASCII Gantt)

```
WEEK 1: Backend Foundation (Feb 7-13, 2026)
════════════════════════════════════════════════════════════════

Day 1-2          Day 3-4              Day 5
┌──────────┐     ┌──────────┐         ┌──────────┐
│ TASK_001 │────▶│ TASK_002 │────────▶│ TASK_006 │ (Frontend starts)
│ Security │     │ MCQ/OSCE │         │ Quiz UI  │
│ Audit    │     │   CRUD   │         └──────────┘
└──────────┘     └────┬─────┘
     │                │                ┌──────────┐
     │                └───────────────▶│ TASK_004 │
     │                                 │ Progress │
     │                ┌──────────┐     │ Tracking │
     └───────────────▶│ TASK_003 │────▶└──────────┘
                      │  Study   │
                      │  Cards   │     ┌──────────┐
                      └────┬─────┘     │ TASK_005 │
                           └──────────▶│   SM-2   │
                                       │  Engine  │
                                       └──────────┘

WEEK 2: Frontend Core (Feb 14-20, 2026)
════════════════════════════════════════════════════════════════

Day 1-2          Day 3          Day 4-5
┌──────────┐     ┌──────────┐  ┌──────────┐
│ TASK_006 │────▶│ TASK_007 │  │ TASK_008 │◀───[TASK_004]
│ Quiz UI  │     │Citations │  │Dashboard │
└──────────┘     └──────────┘  └────┬─────┘
                                     │
                                     ▼
                                ┌──────────┐
                                │ TASK_009 │
                                │  Mobile  │
                                └──────────┘

WEEK 3: Integration & Polish (Feb 21-27, 2026)
════════════════════════════════════════════════════════════════

Day 1-2          Day 3          Day 4          Day 5
┌──────────┐     ┌──────────┐  ┌──────────┐   ┌──────────┐
│ TASK_010 │────▶│ TASK_012 │─▶│ TASK_013 │──▶│ TASK_014 │
│  E2E     │     │   Load   │  │ Deploy   │   │  Launch  │
│  Tests   │     │  Testing │  │ Pipeline │   │          │
└────┬─────┘     └──────────┘  └──────────┘   └──────────┘
     │
[TASK_009]       [TASK_002]
     │           ┌──────────┐
     │           │ TASK_011 │
     │           │   RAG    │
     │           │ Explain  │
     │           └──────────┘
```

---

## 🔴 Critical Path Analysis

**Critical Path** (longest dependency chain, determines minimum project duration):

```
TASK_001 → TASK_002 → TASK_006 → TASK_009 → TASK_010 → TASK_012 → TASK_013 → TASK_014
```

**Total Critical Path Duration:** 6-8h + 6-8h + 8-10h + 4-5h + 6-8h + 4-5h + 5-6h + 4-5h = **43-55 hours**

**With 8-hour workdays:** 5.4-6.9 days minimum (rounded to **7 working days** with overhead)

**Slack built into 3-week schedule:** 15 working days total - 7 critical days = **8 days buffer** (53% slack)

---

## 📊 Dependency Matrix

| Task | Depends On | Blocks | Can Run in Parallel With |
|------|-----------|--------|--------------------------|
| **TASK_001** | None | All tasks | None (must complete first) |
| **TASK_002** | TASK_001 | TASK_004, TASK_006, TASK_011 | TASK_003 |
| **TASK_003** | TASK_001 | TASK_004, TASK_005 | TASK_002 |
| **TASK_004** | TASK_002, TASK_003 | TASK_008 | TASK_005, TASK_006, TASK_007 |
| **TASK_005** | TASK_003 | None | TASK_002, TASK_004, TASK_006 |
| **TASK_006** | TASK_002 | TASK_007, TASK_009 | TASK_003, TASK_004, TASK_005 |
| **TASK_007** | TASK_006 | None | TASK_008 |
| **TASK_008** | TASK_004 | TASK_009 | TASK_006, TASK_007 |
| **TASK_009** | TASK_006, TASK_008 | TASK_010 | TASK_011 |
| **TASK_010** | TASK_009 | TASK_012 | TASK_011 |
| **TASK_011** | TASK_002 | None | TASK_006-010 |
| **TASK_012** | TASK_010 | TASK_013 | None |
| **TASK_013** | TASK_012 | TASK_014 | None |
| **TASK_014** | TASK_013 | None | None (final task) |

---

## ⚡ Parallel Execution Opportunities

### Week 1: Backend Foundation

**After TASK_001 completes:**

**Parallel Track A:** TASK_002 (MCQ/OSCE CRUD) - 6-8 hours
**Parallel Track B:** TASK_003 (Study Cards) - 4-5 hours

**After TASK_002 & TASK_003 complete:**

**Parallel Track A:** TASK_004 (Progress Tracking) - 4-5 hours
**Parallel Track B:** TASK_005 (SM-2 Engine) - 3-4 hours

**Potential time savings:** 2-3 hours (if 2 agents work simultaneously)

---

### Week 2: Frontend Core

**After TASK_002 completes:**

**Parallel Track A (Frontend):** TASK_006 (Quiz UI) → TASK_007 (Citations) - 11-14 hours
**Parallel Track B (Backend):** TASK_004 (Progress) → TASK_008 (Dashboard) - 10-13 hours

**Potential time savings:** 10-13 hours (if 2 agents work simultaneously)

---

### Week 3: Integration & Polish

**After TASK_002 completes:**

**Parallel Track A (Critical Path):** TASK_010 → TASK_012 → TASK_013 → TASK_014
**Parallel Track B (Enhancement):** TASK_011 (RAG Explanation Engine) - 5-6 hours

**Potential time savings:** 5-6 hours

**Total Potential Time Savings:** 17-22 hours (31-40% reduction)

---

## 🚧 Blocking Dependencies (High Risk)

### TASK_001 Blocks Everything
**Risk:** If TASK_001 takes longer than 8 hours OR finds major security issues requiring extensive refactoring
**Impact:** All downstream tasks delayed
**Mitigation:**
- Allocate 2 expert agents (security-compliance-expert + rust-ffi-expert)
- Start TASK_001 on Day 1, 8:00 AM sharp
- If >5 P0/P1 vulnerabilities found, escalate to PM immediately
- Keep TASK_001 scope focused: audit + fix existing code, don't add new features

---

### TASK_002 Blocks All Frontend Work
**Risk:** If TASK_002 API endpoints incomplete or buggy, TASK_006-009 cannot proceed
**Impact:** Frontend development delayed, Week 2 at risk
**Mitigation:**
- Allocate senior backend developer (general-purpose agent)
- 100% test coverage requirement before marking complete
- API contract defined upfront (OpenAPI spec) so frontend can mock
- Frontend can start with mock data while TASK_002 in progress

---

### TASK_009 Blocks All Week 3 Integration
**Risk:** If mobile responsive design incomplete, E2E tests cannot verify mobile flows
**Impact:** Week 3 delayed, launch at risk
**Mitigation:**
- Prioritize critical flows first (MCQ practice, login, dashboard)
- Nice-to-have features can be deferred (Study Cards mobile gestures)
- Lighthouse score >80 acceptable if >90 difficult, can optimize later

---

## 🔄 Dependency Chains (Longest to Shortest)

### Chain 1 (Critical Path): 7 tasks, 43-55 hours
```
TASK_001 → TASK_002 → TASK_006 → TASK_009 → TASK_010 → TASK_012 → TASK_013 → TASK_014
```

### Chain 2: 6 tasks, 27-34 hours
```
TASK_001 → TASK_003 → TASK_004 → TASK_008 → TASK_009 → [joins Chain 1]
```

### Chain 3: 5 tasks, 22-27 hours
```
TASK_001 → TASK_003 → TASK_005 (terminates, no downstream blockers)
```

### Chain 4: 4 tasks, 20-26 hours
```
TASK_001 → TASK_002 → TASK_006 → TASK_007 (terminates)
```

### Chain 5: 3 tasks, 17-22 hours
```
TASK_001 → TASK_002 → TASK_011 (terminates, can run in parallel with Week 2-3 tasks)
```

---

## 📅 Recommended Execution Schedule

### Week 1 (Feb 7-13, 2026)

**Day 1-2 (Fri-Sat):**
- 08:00-16:00: TASK_001 (Security Audit) - security-compliance-expert + rust-ffi-expert

**Day 3 (Sun):**
- 08:00-16:00: TASK_002 (MCQ/OSCE CRUD) starts - general-purpose agent
- 08:00-13:00: TASK_003 (Study Cards) starts - general-purpose agent #2 (parallel)

**Day 4 (Mon):**
- Continue TASK_002 if needed
- 14:00-18:00: TASK_003 completion (if needed)

**Day 5 (Tue):**
- 08:00-13:00: TASK_004 (Progress Tracking) - general-purpose agent
- 08:00-12:00: TASK_005 (SM-2 Engine) - general-purpose agent #2 (parallel)

**Day 6-7 (Wed-Thu):** Buffer for Week 1 overruns

---

### Week 2 (Feb 14-20, 2026)

**Day 8-9 (Fri-Sat):**
- 08:00-18:00: TASK_006 (Quiz UI) - flutter-desktop-expert

**Day 10 (Sun):**
- 08:00-12:00: TASK_007 (Citations) - flutter-desktop-expert
- 12:00-18:00: TASK_008 (Dashboard) starts - flutter-desktop-expert

**Day 11 (Mon):**
- Continue TASK_008 (Dashboard)

**Day 12 (Tue):**
- 08:00-13:00: TASK_009 (Mobile Responsive) - flutter-desktop-expert

**Day 13-14 (Wed-Thu):** Buffer for Week 2 overruns

---

### Week 3 (Feb 21-27, 2026)

**Day 15-16 (Fri-Sat):**
- 08:00-16:00: TASK_010 (E2E Testing) - testing-qa-expert
- 08:00-14:00: TASK_011 (RAG Explanation) - general-purpose agent (parallel)

**Day 17 (Sun):**
- 08:00-13:00: TASK_012 (Load Testing) - testing-qa-expert + general-purpose agent

**Day 18 (Mon):**
- 08:00-14:00: TASK_013 (Deployment Pipeline) - general-purpose agent (DevOps)

**Day 19 (Tue):**
- 08:00-13:00: TASK_014 (MVP Launch) - project-manager-coordinator + testing-qa-expert

**Day 20-21 (Wed-Thu):** Final validation, beta user onboarding, monitoring setup

---

## 🎯 Optimization Strategy

### Minimize Critical Path Duration

**Strategy:** Allocate most senior/experienced agents to critical path tasks
- TASK_001: 2 expert agents (reduce from 8h to 6h)
- TASK_002: Senior backend developer (reduce from 8h to 6h)
- TASK_006: Senior frontend developer (reduce from 10h to 8h)
- TASK_012: Load testing expert (reduce from 5h to 4h)

**Potential savings:** 8 hours on critical path = **1 full workday earlier completion**

---

### Maximize Parallel Execution

**Strategy:** Run independent tasks simultaneously with multiple agents

**Week 1 Parallelization:**
- TASK_002 + TASK_003 (parallel) = save 4-5 hours
- TASK_004 + TASK_005 (parallel) = save 3-4 hours
- **Total saved: 7-9 hours**

**Week 2 Parallelization:**
- TASK_006/007 + TASK_008 (frontend team can split) = save 6-8 hours
- **Total saved: 6-8 hours**

**Week 3 Parallelization:**
- TASK_010 + TASK_011 (parallel) = save 5-6 hours
- **Total saved: 5-6 hours**

**Grand Total Time Savings:** 18-23 hours = **2-3 workdays**

---

## ⚠️ Risk Scenarios

### Scenario 1: TASK_001 Discovers Major Security Flaws
**Probability:** Medium (30%)
**Impact:** High (3-5 day delay)
**Mitigation:**
- Allocate extra 2 days buffer after TASK_001
- If >10 P0/P1 issues found, split into TASK_001A (critical fixes) and TASK_001B (nice-to-have fixes)
- Proceed with TASK_002 after TASK_001A only

---

### Scenario 2: TASK_002 API Contract Changes Mid-Development
**Probability:** Low (15%)
**Impact:** High (frontend rework, 2-3 day delay)
**Mitigation:**
- Define OpenAPI spec BEFORE starting TASK_002
- Frontend uses spec to generate TypeScript types
- API contract frozen after TASK_002 Day 1

---

### Scenario 3: TASK_010 E2E Tests Reveal Critical Bugs
**Probability:** Medium (40%)
**Impact:** Medium (1-2 day delay)
**Mitigation:**
- Run smoke tests after TASK_006 and TASK_008 (don't wait for TASK_010)
- Fix bugs incrementally during Week 2, not all in Week 3

---

## 🔗 External Dependencies (Outside This Plan)

**From OTHER Claude Session (Image Linking):**
- 3,168 medical images available
- Unified catalog needs regeneration (partial: 518 images, target: 3,168)
- Image matching algorithms pending (link images to MCQs/OSCEs)

**Impact on This Plan:**
- TASK_006 (Quiz UI) can display images IF OTHER session completes image linking
- If image linking not ready by Day 8 (start of Week 2), TASK_006 proceeds with placeholder images
- Image linking can be integrated later (non-blocking)

**Coordination Point:** Day 7 (Feb 13) - Check with OTHER session on image linking status

---

## 📊 Summary Statistics

**Total Tasks:** 14
**Total Estimated Effort:** 73-95 hours
**Critical Path Duration:** 43-55 hours
**Parallelization Savings:** 18-23 hours
**Optimized Duration:** 55-72 hours actual work time
**Calendar Days Available:** 21 days (3 weeks)
**Working Days (5 days/week):** 15 days
**Buffer Days:** 15 - 7 (critical path) = **8 days (53% slack)**

**Recommended Team Size:** 2-3 agents working concurrently
**Recommended Daily Hours:** 6-8 hours/agent
**Total Project Cost (at $50/hour):** $3,650 - $4,750

---

## 🎯 Quick Reference

**To start a new task:**
1. Check dependencies in this file: Are all prerequisite tasks ✅ Complete?
2. If yes, proceed with task
3. If no, wait OR start a parallel task

**To update this file:**
- Mark tasks complete when all quality gates passed
- Update "Blocks" column when downstream task starts
- Flag new risks in Risk Scenarios section

---

**Last Updated:** 2026-02-07
**Next Review:** 2026-02-13 (Week 1 Checkpoint)
**Maintained By:** Project Manager
