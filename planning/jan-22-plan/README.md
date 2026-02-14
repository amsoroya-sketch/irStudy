# AMC Medical Education Expansion - Detailed Plans
**Created:** 2026-01-22
**Updated:** 2026-01-24
**Status:** 🟢 ACTIVE - Week 1 in progress

---

## 📋 Quick Navigation

### 🎯 Start Here
- **[PROJECT_STATUS_TRACKER.md](PROJECT_STATUS_TRACKER.md)** - Real-time project status dashboard
- **[EXPANSION_ROADMAP.md](EXPANSION_ROADMAP.md)** - Complete 14-20 week plan
- **[VERSION.md](VERSION.md)** - Version history and changelog

---

## 📅 Weekly Execution Plans

Detailed day-by-day execution plans for each week:

### Phase A: Foundation (Weeks 1-4)
- **[WEEK_01_EXECUTION.md](weekly/WEEK_01_EXECUTION.md)** - Psychiatry Agent + Initial Content ← 🟢 **CURRENT**
- **[WEEK_02_EXECUTION.md](weekly/WEEK_02_EXECUTION.md)** - Psychiatry Complete + QA Upgrade
- **Week 3-4:** Gastroenterology + Endocrinology agents (to be created)

### Phase B: Scaling (Weeks 5-10)
- **Week 5-6:** Neurology + Emergency Medicine agents
- **Week 7-8:** ObGyn + Paediatrics agents
- **Week 9-10:** General Practice + Marwan cases

### Phase C: Major Push (Weeks 11-16)
- **Week 11-12:** OSCE expansion + Marwan medicine cases
- **Week 13-14:** Red flags + final content
- **Week 15-16:** Picture integration + polish

### Phase D: Optional (Weeks 17-20)
- **Week 17-20:** Full Cochrane integration (60,000+ vectors)

---

## 🤖 Agent Expansion Plans

Detailed expansion plans for each medical expert agent:

### Current Agent (Week 1-2)
- **[MED_009_PSYCHIATRY_EXPANSION.md](agents/MED_009_PSYCHIATRY_EXPANSION.md)** - 115 → 850 LOC ← 🟢 **ACTIVE**
  - Mental State Examination framework
  - Risk assessment tools (suicide, violence)
  - Australian Mental Health Act compliance
  - Psychiatric medication side effects
  - ECT counseling framework

### Future Agents (Weeks 3-10)
- **MED-003:** Gastroenterology (Week 3-4)
- **MED-004:** Endocrinology (Week 3-4)
- **MED-005:** Neurology (Week 5-6)
- **MED-006:** Emergency Medicine (Week 5-6)
- **MED-007:** ObGyn (Week 7-8)
- **MED-008:** Paediatrics (Week 7-8)
- **MED-010:** General Practice (Week 9-10)

**Template:** All agents follow MED-009 expansion pattern (850 LOC, clinical tools, MCQ generation, OSCE generation)

---

## 🔬 Track-Specific Plans

Four parallel execution tracks running throughout the project:

### Track 1: Agent Expansion (Weeks 1-10)
- **[TRACK_01_AGENT_EXPANSION.md](tracks/TRACK_01_AGENT_EXPANSION.md)**
- Expand 8 medical expert agents
- 115 → 850 LOC each (6,800 total new code)
- Status: 🟡 0/8 complete (Week 1 in progress)

### Track 2: Content Generation (Weeks 1-20)
- Generate 5,000+ MCQs with RAG citations
- Create 164 OSCE modules
- Generate 150+ evidence summaries
- Status: 🟡 0/5,000 MCQs, 0/164 OSCE

### Track 3: Quality Assurance (Weeks 1-20)
- **[QA_003_UPGRADE_PLAN.md](QA_003_UPGRADE_PLAN.md)**
- RAG citation validation (automated)
- Confidence scoring system (3-tier)
- 100% automation (no human resources)
- Status: 🟡 Week 1 in progress (design + initial implementation)

### Track 4: Content Enhancement (Weeks 5-15)
- **[TRACK_04_CONTENT_ENHANCEMENT.md](tracks/TRACK_04_CONTENT_ENHANCEMENT.md)**
- Add citations to 46 existing OSCE modules
- Enhance 750 flashcards with citations
- Integrate 300+ pictures from source books
- Status: ⏳ Starts Week 5

---

## 📊 Progress Tracking

### Real-Time Status
See **[PROJECT_STATUS_TRACKER.md](PROJECT_STATUS_TRACKER.md)** for:
- Daily progress updates
- Weekly milestone tracking
- Phase completion status
- Quality metrics dashboard
- Risk alerts and blockers

### Key Metrics (Current)
| Metric | Target | Current | Progress |
|--------|--------|---------|----------|
| **Agents Expanded** | 8 | 0 | 0% |
| **MCQs Generated** | 5,000 | 0 | 0% |
| **OSCE Modules** | 164 | 0 | 0% |
| **OSCE Enhanced** | 46 | 0 | 0% |
| **Flashcards Enhanced** | 750 | 0 | 0% |
| **Pictures Integrated** | 300 | 0 | 0% |

---

## 🎯 Current Focus (Week 1)

### This Week's Goals
1. **MED-009 Psychiatry:** 50% complete (115 → 400 LOC)
   - Mental State Examination framework
   - Risk assessment tools
   - Mental Health Act compliance

2. **Content Generation:** 100 psychiatry MCQs + 5 OSCE modules
   - Depression, anxiety, psychosis, bipolar, suicide risk
   - RAG-verified citations for all content

3. **QA-003 Upgrade:** Design + initial implementation
   - RAG citation validator (50 LOC)
   - Confidence scoring system
   - Test on 20 sample MCQs

4. **OSCE Audit:** Catalog all 46 existing modules
   - Identify citation gaps
   - Prioritize enhancement order

### Daily Schedule (This Week)
- **Day 1 (Monday):** MSE framework + 20 depression MCQs
- **Day 2 (Tuesday):** Risk assessment + 20 anxiety/bipolar MCQs
- **Day 3 (Wednesday):** Mental Health Act + 25 psychosis MCQs
- **Day 4 (Thursday):** QA-003 implementation + 20 suicide risk MCQs
- **Day 5 (Friday):** OSCE modules + week review

---

## 📚 Documentation Structure

```
planning/jan-22-plan/
├── README.md (this file)
├── EXPANSION_ROADMAP.md (14-20 week master plan)
├── VERSION.md (version tracking)
├── QA_VALIDATION_PLAN.md (quality assurance)
├── PROJECT_STATUS_TRACKER.md (real-time dashboard)
├── QA_003_UPGRADE_PLAN.md (automated citation validation)
│
├── weekly/ (week-by-week execution)
│   ├── WEEK_01_EXECUTION.md ← 🟢 CURRENT
│   ├── WEEK_02_EXECUTION.md
│   └── ... (to be created)
│
├── agents/ (agent expansion plans)
│   ├── MED_009_PSYCHIATRY_EXPANSION.md ← 🟢 ACTIVE
│   └── ... (to be created)
│
└── tracks/ (parallel execution tracks)
    ├── TRACK_01_AGENT_EXPANSION.md
    ├── TRACK_04_CONTENT_ENHANCEMENT.md
    └── ... (Tracks 2 & 3 to be created)
```

---

## 🚀 How to Use These Plans

### For Project Management
1. **Start with:** [PROJECT_STATUS_TRACKER.md](PROJECT_STATUS_TRACKER.md) (dashboard)
2. **Check:** Current week execution plan for detailed tasks
3. **Update:** Progress daily in status tracker
4. **Review:** Weekly milestones every Friday

### For Agent Development
1. **Read:** Agent-specific expansion plan (e.g., MED_009_PSYCHIATRY_EXPANSION.md)
2. **Follow:** Component-by-component implementation guide
3. **Test:** Unit tests for each component
4. **Validate:** QA-003 automated validation

### For Content Generation
1. **Check:** Track 2 content targets by specialty
2. **Use:** RAG system for citation retrieval
3. **Generate:** MCQs with template structure
4. **Validate:** QA-003 automated approval (>90% target)

### For Quality Assurance
1. **Read:** [QA_003_UPGRADE_PLAN.md](QA_003_UPGRADE_PLAN.md)
2. **Implement:** RAG validation workflow
3. **Monitor:** Auto-approval rates and confidence scores
4. **Refine:** Thresholds based on Week 1-2 results

---

## 🎯 Success Criteria

### Phase A (End of Week 4)
- ✅ 4/10 agents complete
- ✅ 1,500 MCQs total
- ✅ 17 psychiatry OSCE modules
- ✅ 20 existing OSCE modules enhanced
- ✅ QA-003 operational (>90% auto-approval)

### Phase B (End of Week 10)
- ✅ ALL 10 agents complete (850 LOC each)
- ✅ 5,000 MCQs total
- ✅ 100 new OSCE modules
- ✅ ALL existing content enhanced (46 OSCE + 750 flashcards)

### Phase C (End of Week 16)
- ✅ 164 total OSCE modules
- ✅ 500+ pictures integrated
- ✅ All content deliverables complete

---

## ⚠️ Risk Management

### Current Risks (Week 1)
- **None** - All dependencies met

### Mitigation Strategies
1. **Agent Complexity:** Use MED-009 as template for all agents
2. **Timeline Compression:** Parallel agent development (Weeks 3-8)
3. **Citation Accuracy:** Three-tier QA validation (auto, LLM, reject)
4. **Picture Copyright:** Fair use for education + full attribution

---

## 🔗 Related Documents

### Project-Wide Planning
- **[../EXPANSION_ROADMAP.md](EXPANSION_ROADMAP.md)** - This folder's master plan
- **[../00_MASTER/INDEX.md](../00_MASTER/INDEX.md)** - Overall planning structure
- **[../README.md](../README.md)** - Planning system guide

### Technical Infrastructure
- **[../../docs/RAG_SYSTEM_INDEX.md](../../RAG_SYSTEM_INDEX.md)** - RAG architecture
- **[../../constraints/](../../constraints/)** - Project constraints and requirements

---

## 📞 Quick Support

### Find a Document
- **Current week tasks?** → weekly/WEEK_XX_EXECUTION.md
- **Agent expansion details?** → agents/MED_XXX_EXPANSION.md
- **Overall progress?** → PROJECT_STATUS_TRACKER.md
- **Quality standards?** → QA_003_UPGRADE_PLAN.md
- **Track progress?** → tracks/TRACK_XX.md

### Update Progress
1. Daily: Update PROJECT_STATUS_TRACKER.md
2. Weekly: Complete weekly execution plan checklist
3. Per agent: Update agent expansion plan status
4. Per track: Update track-specific metrics

---

## 📈 Version History

| Version | Date | Changes |
|---------|------|---------|
| **3.1.0** | 2026-01-24 | Detailed subdivision created (Week 1, agents, tracks, QA-003) |
| **3.0.0** | 2026-01-22 | Expansion roadmap created (14-20 week plan) |
| **2.0.0** | 2026-01-17 | Planning structure established |

See [VERSION.md](VERSION.md) for detailed changelog.

---

**Last Updated:** 2026-01-24
**Status:** 🟢 WEEK 1 DAY 1 IN PROGRESS
**Next Update:** Daily (PROJECT_STATUS_TRACKER.md)
**Next Milestone:** End of Week 1 (2026-01-31)
