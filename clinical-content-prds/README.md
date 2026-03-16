# Clinical Content PRDs - 360 AI Patient Personas + Golden Dataset

**Created**: 2026-03-15
**Purpose**: Comprehensive roadmap for creating 360 AI Patient Personas across 10 medical specialties
**Timeline**: 3-6 months (24 weeks)
**Budget**: $12,900
**Scope**: All three priorities in parallel (360 personas + Golden Dataset + EMR frameworks)

---

## Executive Summary

This folder contains **10 PRDs** structured across **6 phases** to create production-ready clinical content for the irStudy AI OSCE Simulation System. Currently, the platform has **0 of 360 personas** created, representing a complete blocker for student deployment.

### Critical Statistics

- **Current State**: 0/360 personas (0%), 0/200 Golden Dataset scenarios (0%)
- **Target State**: 360/360 personas (100%), 200/200 Golden Dataset scenarios (100%)
- **Estimated Effort**: 234-296 hours total
- **Timeline**: 24 weeks (3-6 months with HREC approval)
- **Budget Required**: $12,900 (expert panels + cultural liaison)

### What's Inside

| Phase | PRDs | Focus | Timeline | Effort |
|-------|------|-------|----------|--------|
| **Phase 1** | PRD_CC_001, PRD_CC_002 | Foundation (Agent creation, RAG enhancement) | Weeks 1-2 | 20-24h |
| **Phase 2** | PRD_CC_003, PRD_CC_004 | Core Content (300 personas: History + Physical Exam) | Weeks 3-14 | 120-140h |
| **Phase 3** | PRD_CC_005 | Golden Dataset Validation (200 scenarios) | Weeks 8-16 | 30-40h |
| **Phase 4** | PRD_CC_006, PRD_CC_007 | Cultural Safety + HREC Ethics Approval | Weeks 10-24 | 28-36h |
| **Phase 5** | PRD_CC_008, PRD_CC_009 | QA Validation + Pilot Testing | Weeks 17-22 | 24-32h |
| **Phase 6** | PRD_CC_010 | Deployment + Student Launch | Weeks 23-24 | 12-16h |

---

## Quick Start

### For Project Managers

**To start Phase 1**:
```bash
# Execute Ralph loop for automated multi-agent execution
bash scripts/ralph-clinical-content-loop.sh

# Or manually read PRDs:
cat clinical-content-prds/phase1-foundation/PRD_CC_001_AGENT_CREATION.md
cat clinical-content-prds/phase1-foundation/PRD_CC_002_RAG_ENHANCEMENT.md
```

### For Developers

**Read these files first**:
1. `MASTER_PLAN.md` - Overall 24-week roadmap
2. `RALPH_EXECUTION_PLAN.md` - Parallel execution strategy
3. `agents/README.md` - 13 medical expert agent specifications
4. `phase1-foundation/PRD_CC_001_AGENT_CREATION.md` - Start here

### For Clinical Educators

**Key deliverables you'll validate**:
- 360 patient personas (10 specialties × 36 personas each)
- 200 Golden Dataset scenarios (AI Examiner validation)
- 12 Aboriginal/TSI personas (cultural safety review)
- AMC rubric behavioral anchors (scoring consistency)

---

## Folder Structure

```
clinical-content-prds/
├── README.md (this file)
├── MASTER_PLAN.md (24-week roadmap, budget breakdown, dependencies)
├── RALPH_EXECUTION_PLAN.md (parallel execution, state tracking)
│
├── phase1-foundation/
│   ├── PRD_CC_001_AGENT_CREATION.md (Create 13 medical expert agents)
│   └── PRD_CC_002_RAG_ENHANCEMENT.md (Enhance RAG with eTG citations)
│
├── phase2-core-content/
│   ├── PRD_CC_003_HISTORY_PERSONAS.md (240 history-taking personas)
│   └── PRD_CC_004_PHYSICAL_EXAM_PERSONAS.md (60 physical exam personas)
│
├── phase3-validation/
│   └── PRD_CC_005_GOLDEN_DATASET.md (200 expert-validated scenarios)
│
├── phase4-cultural-safety/
│   ├── PRD_CC_006_CULTURAL_SAFETY.md (12 Aboriginal/TSI + 18 LGBTQIA+ personas)
│   └── PRD_CC_007_ETHICS_HREC.md (Ethics approval for data collection)
│
├── phase5-qa/
│   ├── PRD_CC_008_QA_VALIDATION.md (360 persona quality audit)
│   └── PRD_CC_009_PILOT_TESTING.md (20 students, 50 scenarios)
│
├── phase6-deployment/
│   └── PRD_CC_010_DEPLOYMENT.md (Student launch + monitoring)
│
└── agents/ (13 medical expert agent specifications)
    ├── README.md
    ├── MED-001-cardiology-expert.md
    ├── MED-002-emergency-expert.md
    ├── MED-003-gp-expert.md
    ├── MED-004-pediatrics-expert.md
    ├── MED-005-obgyn-expert.md
    ├── MED-006-surgery-expert.md
    ├── MED-007-psychiatry-expert.md
    ├── MED-008-respiratory-expert.md
    ├── MED-009-neurology-expert.md
    ├── MED-010-infectious-diseases-expert.md
    ├── MED-011-cultural-safety-expert.md
    ├── MED-012-physical-exam-expert.md
    └── QA-001-medical-qa-validator.md
```

---

## Key Achievements

### Foundation Complete (Week 0)
- ✅ Clinical evaluation report (19 critical gaps identified)
- ✅ Technical infrastructure ready (AI Patient, Emotional State, RAG, WebSocket)
- ✅ 99/99 tests passing (100% pass rate)
- ✅ 0 hardcoded credentials
- ✅ AMC 15-mark rubric structure validated

### What's Needed
- ❌ 0 of 360 patient personas created (production blocker)
- ❌ 0 of 200 Golden Dataset scenarios validated
- ❌ 0 Aboriginal/TSI personas (cultural safety risk)
- ❌ 0 LGBTQIA+ personas (diversity gap)
- ❌ 0 physical examination personas (25-37% of AMC exam missing)
- ❌ No HREC ethics approval (cannot collect student data)

---

## Success Criteria

### By Week 24 (End of Phase 6)
- ✅ 360/360 patient personas created and validated
- ✅ 200/200 Golden Dataset scenarios scored by ≥6 FRACP clinicians
- ✅ ≥90% agreement ±2 marks (AI Examiner vs human examiners)
- ✅ 12 Aboriginal/TSI personas reviewed by cultural liaison
- ✅ 18 LGBTQIA+ personas reviewed by LGBTQIA+ health educator
- ✅ HREC ethics approval obtained
- ✅ Pilot test complete (20 students, 50 scenarios)
- ✅ Student deployment ready

---

## Risk Mitigation

### Timeline Risks
- **HREC approval delay** (3-6 months): Submit application Week 10, continue content creation in parallel
- **Expert panel availability**: Book 6 FRACP clinicians early (Week 8)
- **Cultural liaison unavailable**: Partner with Aboriginal health organization (Week 10)

### Budget Risks
- **Expert panel costs**: $9,900 budgeted (6 clinicians × 5 hours × $330/hour)
- **Cultural liaison**: $2,000 budgeted (10 hours × $200/hour)
- **LGBTQIA+ review**: $1,000 budgeted (5 hours × $200/hour)
- **Total**: $12,900 (approved)

### Quality Risks
- **AI-generated content accuracy**: All personas validated by ≥2 FRACP clinicians
- **Cultural stereotypes**: Mandatory cultural liaison review before deployment
- **AI Examiner scoring consistency**: Golden Dataset validation (≥90% agreement)

---

## Parallel Execution Strategy

**Ralph loop runs 5 agents simultaneously across 4 batches**:
- **Batch 1**: Cardiology, Emergency, GP, Respiratory, Neurology agents
- **Batch 2**: Pediatrics, ObGyn, Surgery, Psychiatry, Infectious Diseases agents
- **Batch 3**: Cultural Safety, Physical Exam agents
- **Batch 4**: QA Validator (reviews all personas)

**Result**: 24-30 personas per batch (72-90 personas per week) = 4-5 weeks for 360 personas

---

## Next Steps

1. **Read MASTER_PLAN.md** - Understand full 24-week roadmap
2. **Read RALPH_EXECUTION_PLAN.md** - Learn parallel execution strategy
3. **Execute PRD_CC_001** - Create 13 medical expert agents
4. **Execute PRD_CC_002** - Enhance RAG with eTG/AMH citations
5. **Start Phase 2** - Begin 360 persona creation (Weeks 3-14)

---

**Status**: ✅ READY FOR EXECUTION
**Last Updated**: 2026-03-15
**Version**: 1.0
