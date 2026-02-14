# Dependency Map
## What Blocks What - Complete Dependency Chains

**Last Updated:** January 17, 2026
**Purpose:** Visualize dependencies to avoid blocked work
**Review Frequency:** Weekly

---

## Critical Path (Sequential Dependencies)

```
CRITICAL PATH TO MVP (14 weeks):

Week 0: 💰 Acquire Books ($645-$1,140)
   ↓ BLOCKS: All content creation
   ↓
Week 1-2: 🏗️ Phase 1: Foundation
   ├─ Download StatPearls (backup)
   ├─ Process PDFs → Embeddings → Qdrant
   ├─ MCP servers (Medical Knowledge + PubMed)
   └─ Agent infrastructure (registry + queue)
   ↓ BLOCKS: Phase 2 (Backend)
   ↓
Week 3-6: ⚙️ Phase 2: Backend Core
   ├─ Database models (User, Question, Quiz)
   ├─ OAuth2 + JWT authentication
   ├─ API endpoints (20+)
   └─ Security hardening
   ↓ BLOCKS: Phase 4 (Frontend)
   ↓ ENABLES: Phase 3 (can run in parallel)
   ↓
Week 7-10: 🤖 Phase 3: RAG & Question Generation
   ├─ RAG query engine
   ├─ MCQ generator
   ├─ OSCE scenario generator
   ├─ QA-001 validation agent
   └─ First 500 questions
   ↓ BLOCKS: Automated content scaling
   ↓ ENABLES: Agent system (Phase 5)
   ↓
Week 11-14: 🎨 Phase 4: Frontend MVP
   ├─ Next.js app setup
   ├─ Quiz interface
   ├─ Progress tracking
   └─ Responsive design
   ↓ BLOCKS: User testing
   ↓ ENABLES: MVP launch
   ↓
Week 15-18: 🤖 Phase 5: Agent System (optional for MVP)
Week 19-22: ✅ Phase 6: Testing & Polish
Week 23-24: 🚀 Phase 7: Deployment
```

**MVP Launch Point:** End of Week 14 (Phase 1-4 complete)
**Full Launch:** End of Week 24 (All phases complete)

---

## Dependency Categories

### 🔴 P0 Blockers (Must Complete First)

**1. Book Acquisition** (Week 0)
```
Issue #6: Acquire Books
   ↓ BLOCKS (cannot start without):
   ├─ Issue #1: Diabetes module
   ├─ Issue #2: Physical exam modules
   ├─ Issue #3: Mock OSCE stations
   ├─ Issue #4: Differential diagnosis guide
   ├─ Issue #5: Case bank expansion
   ├─ All MCQ generation (requires textbook content)
   ├─ All OSCE generation (requires clinical scenarios)
   └─ All clinical cases (requires case material)

WORKAROUND: Use StatPearls (FREE) as temporary content source
RISK: Quality lower without textbooks (85% vs 95%)
DECISION: Start with StatPearls, validate system, then invest in books
```

**2. Phase 1: Foundation** (Week 1-2)
```
Phase 1: Foundation Infrastructure
   ↓ BLOCKS:
   ├─ Phase 2: Backend (needs Qdrant populated)
   ├─ Phase 3: RAG system (needs embeddings)
   ├─ Issue #11: Verify Ollama (needs LLM setup)
   └─ Issue #12: Medical Knowledge MCP (needs Qdrant)

CAN RUN IN PARALLEL with:
   ├─ Issue #7: Study timeline (no dependencies)
   ├─ Issue #9: Enhance CLAUDE.md (no dependencies)
   └─ Planning documentation
```

**3. Phase 2: Backend Core** (Week 3-6)
```
Phase 2: Backend API
   ↓ BLOCKS:
   ├─ Phase 4: Frontend (needs API endpoints)
   ├─ User testing (needs auth system)
   └─ Beta launch (needs database)

CAN RUN IN PARALLEL with:
   └─ Phase 3: RAG & Generation (independent)
```

---

### 🟠 P1 High Priority (Critical Path)

**4. Phase 3: RAG & Question Generation** (Week 7-10)
```
Phase 3: RAG System
   ↓ BLOCKS:
   ├─ Phase 5: Agent system (needs RAG foundation)
   ├─ Automated content generation at scale
   └─ 5,000+ question bank

DEPENDENCY:
   ├─ Phase 1 complete (Qdrant populated)
   └─ Books acquired (for quality content)

CAN RUN IN PARALLEL with:
   └─ Phase 2: Backend (independent systems)
```

**5. Phase 4: Frontend MVP** (Week 11-14)
```
Phase 4: Frontend
   ↓ BLOCKS:
   ├─ User testing
   ├─ MVP launch
   └─ Beta testing program

DEPENDENCY:
   ├─ Phase 2 complete (needs API endpoints)
   └─ Phase 3 complete (needs question content)

CAN RUN IN PARALLEL with:
   └─ Phase 5: Agent system (if Phase 3 done)
```

---

### 🟡 P2 Medium Priority (Important but not blocking MVP)

**6. Phase 5: Agent System** (Week 15-18)
```
Phase 5: 46 Expert Agents
   ↓ ENABLES (but not required for MVP):
   ├─ Automated content generation (1,000 questions/day)
   ├─ Multi-agent workflows
   └─ Continuous content improvement

DEPENDENCY:
   └─ Phase 3 complete (needs RAG system)

CAN RUN IN PARALLEL with:
   ├─ Phase 4: Frontend (independent)
   └─ Content creation (manual)
```

**7. GitHub Issues (Content Creation)**
```
Issue #1: Diabetes Module (4 hours)
   DEPENDENCY: Books acquired
   CAN RUN: Any time after books arrive

Issue #2: Physical Exam Modules (10 hours)
   DEPENDENCY: Books acquired (Talley & O'Connor)
   CAN RUN: Any time after books arrive

Issue #3: 12 Mock OSCE Stations (15 hours)
   DEPENDENCY: Books acquired (AMC Handbook, Talley)
   CAN RUN: Any time after books arrive

Issue #4: Differential Diagnosis Guide (8 hours)
   DEPENDENCY: Books acquired (all core books)
   CAN RUN: Any time after books arrive
   RECOMMENDED: After Phase 3 (can use RAG)

Issue #5: Case Bank Expansion (20-40 hours)
   DEPENDENCY: Books acquired (all core books)
   CAN RUN: Any time after books arrive
   RECOMMENDED: After Phase 3 (can use RAG)

Issue #7: Study Timeline (8 hours)
   DEPENDENCY: None! ✅
   CAN RUN: Immediately (quick win)

Issues #8-14: Infrastructure/Technical
   DEPENDENCY: Phase 1 complete
   CAN RUN: Week 2+ (after infrastructure setup)
```

---

### 🟢 P3 Low Priority (Enhancement)

**8. Phase 6: Testing & Polish** (Week 19-22)
```
Phase 6: Testing & Polish
   ↓ BLOCKS:
   └─ Production launch (Phase 7)

DEPENDENCY:
   ├─ Phase 2 complete (backend to test)
   ├─ Phase 3 complete (RAG to test)
   ├─ Phase 4 complete (frontend to test)
   └─ Phase 5 complete (agents to test)

NOTE: Can do incremental testing throughout (recommended)
```

**9. Phase 7: Production Deployment** (Week 23-24)
```
Phase 7: Deployment
   ↓ ENABLES:
   └─ Public launch

DEPENDENCY:
   └─ Phase 6 complete (all testing passed)
```

---

## Parallel Work Streams

### Stream A: Content Development (After Books Acquired)
```
START: Week 0 (book acquisition)
DURATION: Ongoing (8-12 weeks)

Week 1-2:
├─ Issue #7: Study timeline (8h) ✅ No dependencies
└─ Issue #1: Diabetes module (4h) - requires books

Week 3-4:
├─ Issue #2: Physical exam modules (10h)
└─ Issue #3: Start mock OSCE stations (8/15h)

Week 5-6:
├─ Issue #3: Complete mock OSCE stations (7/15h)
└─ Issue #4: Differential diagnosis guide (8h)

Week 7-10:
├─ Phase 3: 500 questions generated (RAG)
└─ Issue #5: Case bank expansion (20-40h)

TOTAL EFFORT: ~77 hours manual + automated generation
BLOCKERS: Only book acquisition
ENABLES: Complete content library for MVP
```

---

### Stream B: Infrastructure Development (Technical)
```
START: Week 1 (after Phase 1 foundation)
DURATION: 14 weeks

Week 1-2: Phase 1 Foundation
Week 3-6: Phase 2 Backend
Week 7-10: Phase 3 RAG & Generation (parallel with backend)
Week 11-14: Phase 4 Frontend

TOTAL: 14 weeks to MVP
BLOCKERS: Sequential (Phase 1 → 2 → 4, Phase 3 parallel)
ENABLES: Working application
```

---

### Stream C: Agent System (Optional for MVP)
```
START: Week 15 (after Phase 3 complete)
DURATION: 4 weeks

Week 15-16: First 10 agents
Week 17-18: Next 10 agents + workflows

TOTAL: 4 weeks
BLOCKERS: Phase 3 complete (needs RAG)
ENABLES: Automated scaling (not required for MVP)
```

---

### Stream D: Quality & Testing (Continuous)
```
START: Week 1 (continuous throughout)
DURATION: Ongoing

Week 1-2: Infrastructure testing
Week 3-6: Backend testing (incremental)
Week 7-10: RAG testing, content validation
Week 11-14: Frontend testing, E2E tests
Week 19-22: Comprehensive testing phase

TOTAL: Continuous + 4 weeks focused
BLOCKERS: Each component must exist to test
ENABLES: Quality assurance throughout
```

---

## Dependency Resolution Strategies

### Strategy 1: Parallel Development
**Maximize parallel work to reduce timeline:**

**Weeks 1-2:**
- Phase 1 foundation (required)
- Issue #7 study timeline (parallel, no dependencies)
- Planning documentation (parallel)

**Weeks 3-10:**
- Phase 2 backend (Weeks 3-6)
- Phase 3 RAG (Weeks 7-10)
- Content creation Issues #1-5 (parallel, after books arrive)

**Weeks 11-18:**
- Phase 4 frontend (Weeks 11-14)
- Phase 5 agents (Weeks 15-18, after Phase 3)

**Result:** 18 weeks instead of 24 weeks to MVP with agents

---

### Strategy 2: Quick Wins First
**Build momentum with low-dependency tasks:**

**Quick Win List (No blockers or minimal dependencies):**
1. Issue #7: Study timeline (0h dependency, 8h work)
2. Phase 1: Foundation (0h dependency, 40h work)
3. Issue #9: Enhance CLAUDE.md (0h dependency, 2h work)
4. Planning documentation (0h dependency, 20h work)

**Benefit:** Show progress immediately while waiting for books

---

### Strategy 3: Critical Path Focus
**Focus on items that unblock the most work:**

**Priority Order:**
1. **Books** → Unblocks 5 GitHub issues + all content
2. **Phase 1** → Unblocks Phase 2 & 3
3. **Phase 2** → Unblocks Phase 4 (frontend)
4. **Phase 3** → Unblocks automated generation
5. **Phase 4** → Unblocks MVP launch

**Result:** Fastest path to working MVP

---

## Risk Areas (Single Points of Failure)

### Risk 1: Book Acquisition Delays
**Impact:** Blocks 5 GitHub issues + content quality
**Probability:** Medium (depends on budget/delivery)
**Mitigation:**
- Order immediately
- Use StatPearls as backup
- Institutional access (eTG, AMH) saves $540

**If Blocked:**
- Proceed with StatPearls content
- Lower quality expectations (85% vs 95%)
- Re-generate with textbooks later

---

### Risk 2: Phase 1 Foundation Issues
**Impact:** Blocks all subsequent phases
**Probability:** Low (straightforward setup)
**Mitigation:**
- Test incrementally (don't wait until end)
- Use existing Docker infrastructure
- Validate with small samples first

**If Blocked:**
- Focus on Phase 1 completion
- All other work depends on this
- Get help if needed (documentation exists)

---

### Risk 3: RAG System Quality Issues
**Impact:** Blocks automated generation quality
**Probability:** Medium (LLM quality varies)
**Mitigation:**
- Start with best models (Llama 3.1 70B)
- Use conservative prompts
- Manual review sample (10%)
- Iterate based on feedback

**If Blocked:**
- Fall back to manual content creation
- Use API-based LLMs (GPT-4, Claude)
- Increase manual review percentage

---

### Risk 4: Backend/Frontend Integration Issues
**Impact:** Delays MVP launch
**Probability:** Low (standard tech stack)
**Mitigation:**
- Use well-documented frameworks (FastAPI, Next.js)
- Test integration early
- Have API contract defined upfront

**If Blocked:**
- Simplify MVP scope
- Launch with basic features
- Iterate post-launch

---

## Decision Points

### Decision 1: Books or StatPearls? (Week 0)
**Dependency Check:**
- Can proceed with StatPearls? ✅ Yes
- Quality impact? ⚠️ Moderate (85% vs 95%)

**Decision:** Start StatPearls, validate system, invest in books if quality proven

---

### Decision 2: Sequential or Parallel Phases? (Week 3)
**Dependency Check:**
- Phase 2 and 3 independent? ✅ Yes
- Resources available? ✅ Yes (solo dev can manage)

**Decision:** Run Phase 2 (Backend) and Phase 3 (RAG) in parallel to save 4 weeks

---

### Decision 3: MVP or Full System? (Week 14)
**Dependency Check:**
- Phases 1-4 complete? ✅ Check
- Content sufficient? ✅ 500+ questions

**Decision:** Launch MVP at Week 14, iterate with agent system (Phase 5) later

---

### Decision 4: Manual or Automated Content? (Week 7)
**Dependency Check:**
- RAG system working? ✅ Check
- Quality acceptable? ⚠️ Test first

**Decision:** Generate 100 test questions, manual review, then scale if quality good

---

## Summary: What Blocks What

| Item | Blocks | Blocked By | Can Start |
|------|--------|------------|-----------|
| **Books** | Issues #1-5, All content | Nothing | Week 0 |
| **Phase 1** | Phase 2, Phase 3 | Nothing | Week 1 |
| **Phase 2** | Phase 4 | Phase 1 | Week 3 |
| **Phase 3** | Phase 5, Automation | Phase 1, Books | Week 7 |
| **Phase 4** | MVP launch | Phase 2, Phase 3 | Week 11 |
| **Phase 5** | Scaling | Phase 3 | Week 15 |
| **Phase 6** | Production | Phase 2-5 | Week 19 |
| **Phase 7** | Public launch | Phase 6 | Week 23 |
| **Issue #7** | Nothing | Nothing | Week 1 ✅ |
| **Issues #1-5** | Nothing | Books | When books arrive |
| **Issues #8-14** | Nothing | Phase 1 | Week 2+ |

---

**Last Updated:** January 17, 2026
**Next Review:** Weekly during execution
**Maintained By:** PM-001 (Project Manager)
