# Priority Matrix
## Complete P0-P4 Classification Across All Work

**Last Updated:** January 17, 2026
**Purpose:** Definitive priority ordering for all tasks
**Review Frequency:** Weekly

---

## Priority Levels Defined

| Level | Name | Description | Timeline | Blocking Impact |
|-------|------|-------------|----------|-----------------|
| **P0** | Critical Blockers | Must complete before anything else | Immediate | Blocks 70%+ of work |
| **P1** | High Priority | Core MVP features, critical path | Week 1-14 | Blocks key features |
| **P2** | Medium Priority | Important enhancements | Week 15-22 | Blocks some features |
| **P3** | Low Priority | Polish, optimization | Week 19-24 | Blocks launch quality |
| **P4** | Future | Post-launch enhancements | Post-Week 24 | No blocking impact |

---

## P0: CRITICAL BLOCKERS (Must Do First)

### 1. Issue #6: Acquire Required Medical Textbooks
**Priority:** P0
**Time:** 3-7 days (delivery)
**Cost:** $645-$1,140
**Blocks:** Issues #1, #2, #3, #4, #5 + all MCQ generation
**Status:** ⚠️ NOT STARTED

**Why P0:**
- Blocks ALL content creation work
- Required for 100% clinical accuracy
- No workarounds (StatPearls is backup only)
- Blocks 5+ GitHub issues

**Action:** Order top 5 books immediately
**File:** [issue_06_textbook_acquisition.md](../07_GITHUB_ISSUES/issue_06_textbook_acquisition.md)

---

### 2. Phase 1: Foundation Infrastructure (Week 1-2)
**Priority:** P0
**Time:** 2 weeks
**Cost:** $0
**Blocks:** Backend development, RAG system
**Status:** 🟡 80% COMPLETE

**Components:**
- [ ] Download StatPearls (FREE backup) - 4 hours
- [ ] Process 10,000+ PDFs → Embeddings → Qdrant - 6 hours
- [ ] Implement Medical Knowledge MCP Server - 8 hours
- [ ] Implement PubMed MCP Server - 6 hours
- [ ] Deploy Agent Registry - 4 hours
- [ ] Setup Redis Message Queue - 2 hours
- [ ] Validate end-to-end pipeline - 2 hours

**Why P0:**
- Blocks Phase 2 (Backend)
- Blocks Phase 3 (RAG)
- Foundation for entire system

**File:** [phase1_foundation.md](../01_PHASE_EXECUTION/phase1_foundation.md)

---

### 3. Critical Architecture Decisions
**Priority:** P0
**Time:** 2-4 hours
**Cost:** $0
**Blocks:** All technical work
**Status:** 🟢 MOSTLY COMPLETE

**Decisions Required:**
- [x] Self-hosted vs API LLMs → Self-hosted (Ollama)
- [x] Local vs cloud development → Local dev, K8s prod
- [ ] Which core medicine textbook → Davidson's recommended
- [x] Frontend framework → Next.js 15
- [x] Backend framework → FastAPI
- [x] Database choices → PostgreSQL + Qdrant + Neo4j + Redis

**Why P0:**
- Affects all downstream work
- Expensive to change later
- Blocks technology selection

---

## P1: HIGH PRIORITY (Core Value - Week 1-14)

### 4. Phase 2: Backend Core (Week 3-6)
**Priority:** P1
**Time:** 4 weeks
**Dependencies:** Phase 1 complete
**Blocks:** Frontend development, user testing
**Status:** ⏳ NOT STARTED

**Deliverables:**
- Database models (User, Question, Quiz, Progress)
- Alembic migrations
- OAuth2 + JWT authentication
- 20+ API endpoints (auth, questions, quizzes, progress)
- Security hardening (Argon2, rate limiting, CORS)

**Why P1:**
- Critical path to MVP
- Blocks frontend development
- Core platform functionality

**File:** [phase2_backend.md](../01_PHASE_EXECUTION/phase2_backend.md)

---

### 5. Phase 3: RAG & Question Generation (Week 7-10)
**Priority:** P1
**Time:** 4 weeks
**Dependencies:** Phase 1 complete + Books acquired
**Blocks:** Automated content generation
**Status:** ⏳ NOT STARTED

**Deliverables:**
- RAG query engine (Qdrant + LLM)
- Reranking system (cross-encoder)
- MCQ generator pipeline
- OSCE scenario generator
- QA-001 validation agent
- First 500 validated questions

**Why P1:**
- Core product differentiator (AI generation)
- Required for scaling content creation
- Enables agent workflows

**File:** [phase3_rag_generation.md](../01_PHASE_EXECUTION/phase3_rag_generation.md)

---

### 6. Phase 4: Frontend MVP (Week 11-14)
**Priority:** P1
**Time:** 4 weeks
**Dependencies:** Phase 2 (Backend) complete
**Blocks:** User testing, beta launch
**Status:** ⏳ NOT STARTED

**Deliverables:**
- Next.js 15 app (TypeScript + Tailwind)
- Authentication UI (login/register)
- Dashboard interface
- Quiz taking interface
- Results page with explanations
- Progress tracking dashboard
- Responsive design (mobile-first)
- Lighthouse score 95+

**Why P1:**
- First user-facing interface
- Required for MVP launch
- Enables user testing

**File:** [phase4_frontend.md](../01_PHASE_EXECUTION/phase4_frontend.md)

---

### 7. Issue #3: Create 12 Additional Mock OSCE Stations
**Priority:** P1
**Time:** 15 hours
**Dependencies:** Books acquired (AMC Handbook, Talley)
**Cost:** Included in book budget
**Status:** ⏳ NOT STARTED

**Target:** 50 total comprehensive OSCE stations
**Current:** 15 stations
**Gap:** 35 stations needed

**Why P1:**
- High user demand
- Core ICRP/AMC prep value
- Differentiator from competitors

**File:** [issue_03_mock_osce_stations.md](../07_GITHUB_ISSUES/issue_03_mock_osce_stations.md)

---

### 8. Issue #1: Complete Diabetes/Endocrine Module
**Priority:** P1
**Time:** 4 hours
**Dependencies:** Books acquired (eTG, Murtagh, AMH)
**Status:** ⏳ NOT STARTED

**Components:**
- Diabetes diagnosis & classification
- Type 1 & 2 management algorithms
- Complications & screening
- Medication dosing (insulin, oral agents)
- HbA1c interpretation

**Why P1:**
- High-yield topic (appears in 90% of exams)
- Heavily tested in AMC/ICRP
- Quick win (only 4 hours)

**File:** [issue_01_diabetes_module.md](../07_GITHUB_ISSUES/issue_01_diabetes_module.md)

---

### 9. Content: 5,000+ MCQs Across All Specialties
**Priority:** P1
**Time:** Automated (after Phase 3)
**Dependencies:** Phase 3 complete + Books acquired
**Status:** ⏳ NOT STARTED

**Distribution by Specialty:**
- Cardiology: 500 questions
- Respiratory: 500 questions
- Gastroenterology: 500 questions
- Endocrinology: 400 questions
- Neurology: 400 questions
- Emergency Medicine: 500 questions
- Obstetrics: 400 questions
- Gynaecology: 400 questions
- Paediatrics: 500 questions
- Psychiatry: 400 questions
- General Practice: 500 questions

**Why P1:**
- Core product value
- Required for comprehensive prep
- Scales with automation

**File:** [p1_core_content.md](../02_CONTENT_PLANS/by_priority/p1_core_content.md)

---

## P2: MEDIUM PRIORITY (Important - Week 15-22)

### 10. Phase 5: Agent System Expansion (Week 15-18)
**Priority:** P2
**Time:** 4 weeks
**Dependencies:** Phase 3 complete
**Blocks:** Automated workflows
**Status:** 🟡 10% COMPLETE (base classes only)

**Deliverables:**
- Implement 46 expert agents
- Multi-agent workflows (generation, QA, deployment)
- Automated content generation (1,000 questions/day)
- Agent monitoring dashboards

**Why P2:**
- Enables automation at scale
- Improves content quality
- Reduces manual effort

**File:** [phase5_agents.md](../01_PHASE_EXECUTION/phase5_agents.md)

---

### 11. Issue #4: Master Differential Diagnosis Guide
**Priority:** P2
**Time:** 8 hours
**Dependencies:** Books acquired (all core books)
**Status:** ⏳ NOT STARTED

**Components:**
- Organized by presenting complaint
- Common to rare causes
- Red flags for each presentation
- Investigation algorithms
- Australian guideline references

**Why P2:**
- High user value (quick reference)
- Consolidates existing content
- Improves study efficiency

**File:** [issue_04_differential_diagnosis_guide.md](../07_GITHUB_ISSUES/issue_04_differential_diagnosis_guide.md)

---

### 12. Issue #5: Expanded Case Bank (50-100 Cases)
**Priority:** P2
**Time:** 20-40 hours
**Dependencies:** Books acquired (all core books)
**Status:** ⏳ NOT STARTED

**Current:** 15 cases
**Target:** 50 minimum, 100 ideal

**Case Components:**
- Patient presentation
- History & examination findings
- Investigation results
- Differential diagnosis
- Management plan
- Learning points
- References

**Why P2:**
- Builds clinical reasoning skills
- High educational value
- Time-intensive but impactful

**File:** [issue_05_case_bank_expansion.md](../07_GITHUB_ISSUES/issue_05_case_bank_expansion.md)

---

### 13. Issue #2: Physical Examination Modules (5 Systems)
**Priority:** P2
**Time:** 10 hours
**Dependencies:** Books acquired (Talley & O'Connor)
**Status:** ⏳ NOT STARTED

**Systems:**
1. ENT examination
2. Musculoskeletal examination
3. Per vaginum examination
4. Thyroid examination
5. Lymph node examination

**Why P2:**
- Completes physical exam coverage
- OSCE preparation value
- Fills content gaps

**File:** [issue_02_physical_exam_modules.md](../07_GITHUB_ISSUES/issue_02_physical_exam_modules.md)

---

## P3: LOW PRIORITY (Enhancement - Week 19-24)

### 14. Phase 6: Testing & Polish (Week 19-22)
**Priority:** P3
**Time:** 4 weeks
**Dependencies:** Phases 2-5 complete
**Blocks:** Production launch
**Status:** ⏳ NOT STARTED

**Components:**
- Comprehensive testing (unit, integration, E2E, load)
- Performance optimization (backend, frontend, database, LLM)
- Security hardening (OWASP, penetration testing)
- Accessibility compliance (WCAG 2.1 AA)
- UX polish

**Why P3:**
- Required for quality launch
- Not needed until MVP complete
- Can iterate post-launch

**File:** [phase6_testing_polish.md](../01_PHASE_EXECUTION/phase6_testing_polish.md)

---

### 15. Issue #7: Interactive Study Timeline Tracker
**Priority:** P3 (but QUICK WIN!)
**Time:** 8 hours
**Dependencies:** None
**Cost:** $0
**Status:** ⏳ NOT STARTED

**Features:**
- 3-month ICRP preparation timeline
- Progress tracking (localStorage)
- Mobile-responsive
- Works offline

**Why P3 (despite being quick win):**
- Nice-to-have, not critical path
- Can be done anytime
- No dependencies (good for momentum)

**Recommendation:** Do early as quick win despite P3 priority

**File:** [issue_07_study_timeline_tracker.md](../07_GITHUB_ISSUES/issue_07_study_timeline_tracker.md)

---

### 16. Advanced Features
**Priority:** P3
**Time:** Ongoing
**Dependencies:** MVP launch
**Status:** ⏳ NOT STARTED

**Features:**
- Spaced repetition algorithm (SM-2)
- Adaptive learning system
- Personalized study plans
- Weak area identification
- Study time optimization
- Peer comparison analytics

**Why P3:**
- Enhances user experience
- Not required for MVP
- Can iterate based on user feedback

**Files:** See [06_FEATURE_PLANS/enhanced/](../06_FEATURE_PLANS/enhanced/)

---

## P4: FUTURE (Post-Launch)

### 17. Phase 7: Production Deployment (Week 23-24)
**Priority:** P4
**Time:** 2 weeks
**Dependencies:** Phase 6 complete
**Status:** ⏳ NOT STARTED

**Components:**
- Kubernetes cluster setup
- CI/CD pipeline (GitHub Actions + ArgoCD)
- Monitoring (Prometheus + Grafana)
- Production database deployment
- SSL/TLS configuration
- Beta testing (20-50 users)
- Launch

**Why P4:**
- Only needed at very end
- Can launch earlier with simpler deployment
- Can iterate infrastructure post-launch

**File:** [phase7_deployment.md](../01_PHASE_EXECUTION/phase7_deployment.md)

---

### 18. Mobile Applications (iOS & Android)
**Priority:** P4
**Time:** 8-12 weeks
**Dependencies:** Web MVP launched
**Status:** ⏳ NOT STARTED

**Approach:** React Native or Flutter
**Features:** Offline mode, push notifications, sync

**Why P4:**
- Not required for MVP
- Web app works on mobile browsers
- Can assess demand first

**File:** [mobile_app_plan.md](../06_FEATURE_PLANS/future/mobile_app_plan.md)

---

### 19. Advanced Integrations
**Priority:** P4
**Time:** Ongoing
**Dependencies:** Platform mature
**Status:** ⏳ NOT STARTED

**Integrations:**
- Medical image analysis (radiology, dermatology)
- Video content integration
- Live tutoring/mentorship
- Community forums
- Study groups

**Why P4:**
- Enhances platform over time
- Can be added incrementally
- Assess user demand first

**Files:** See [06_FEATURE_PLANS/future/](../06_FEATURE_PLANS/future/)

---

## Summary by Priority

| Priority | Items | Estimated Time | Critical? |
|----------|-------|----------------|-----------|
| **P0** | 3 items | 2 weeks + $645 | ✅ YES - Blocks 70% of work |
| **P1** | 6 items | 12 weeks | ✅ YES - Core MVP |
| **P2** | 4 items | 8 weeks | ⚠️ Important but not blocking |
| **P3** | 3 items | 6 weeks | ℹ️ Enhancement & polish |
| **P4** | 3 items | Post-launch | ℹ️ Future improvements |

**Total to MVP (P0 + P1):** 14 weeks + $645-$1,140
**Total to Full Launch (P0-P3):** 24 weeks + $645-$1,140
**Post-Launch (P4):** Ongoing enhancements

---

## Execution Order Recommendation

```
IMMEDIATE (Week 0):
1. Issue #6: Order books ($645-$1,140)

WEEK 1-2 (Phase 1):
2. Phase 1: Foundation infrastructure
3. Issue #7: Study timeline (quick win)

WEEK 3-6 (Phase 2):
4. Phase 2: Backend core
5. Issue #1: Diabetes module (after books arrive)

WEEK 7-10 (Phase 3):
6. Phase 3: RAG & generation
7. Generate first 500 questions

WEEK 11-14 (Phase 4):
8. Phase 4: Frontend MVP
9. Issue #3: 12 mock OSCE stations

WEEK 15-18 (Phase 5):
10. Phase 5: Agent system
11. Issue #4: Differential diagnosis guide
12. Issue #5: Case bank expansion

WEEK 19-22 (Phase 6):
13. Phase 6: Testing & polish
14. Issue #2: Physical exam modules
15. Advanced features

WEEK 23-24 (Phase 7):
16. Phase 7: Production deployment
17. Beta testing
18. Launch

POST-LAUNCH:
19. Mobile apps
20. Advanced integrations
```

---

**Last Updated:** January 17, 2026
**Next Review:** January 24, 2026
**Maintained By:** Project Manager (PM-001)
