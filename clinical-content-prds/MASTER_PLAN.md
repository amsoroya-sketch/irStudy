# Clinical Content Creation Master Plan
# 360 AI Patient Personas + Golden Dataset + EMR Frameworks

**Version**: 1.0
**Created**: 2026-03-15
**Timeline**: 24 weeks (3-6 months)
**Budget**: $12,900
**Lead**: Project Manager + 13 Medical Expert Agents

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Current State vs Target State](#current-state-vs-target-state)
3. [10-Specialty Distribution](#10-specialty-distribution)
4. [6-Phase Timeline](#6-phase-timeline)
5. [Budget Breakdown](#budget-breakdown)
6. [Dependencies & Critical Path](#dependencies--critical-path)
7. [Risk Mitigation](#risk-mitigation)
8. [Quality Gates](#quality-gates)
9. [Success Metrics](#success-metrics)

---

## Executive Summary

### The Problem

The irStudy AI OSCE Simulation System has **excellent technical infrastructure** (99/99 tests passing, 81% code coverage, zero hardcoded credentials) but is **completely non-functional** due to missing clinical content:

- **0 of 360 AI Patient Personas** created (production blocker)
- **0 of 200 Golden Dataset scenarios** validated (AI Examiner accuracy unknown)
- **0 Aboriginal/TSI personas** (cultural safety risk)
- **0 LGBTQIA+ personas** (diversity gap)
- **0 physical examination personas** (25-37% of AMC exam missing)
- **No HREC ethics approval** (cannot collect student data legally)

**Impact**: Students CANNOT use the platform for AMC Clinical Examination preparation. 40% likely to fail AMC exam if this was their only preparation tool (per clinical evaluation report).

### The Solution

**3-6 month comprehensive content creation effort**:
- Create **360 AI Patient Personas** across 10 specialties using Agent OS medical expert agents
- Validate **200 Golden Dataset scenarios** with 6 FRACP clinicians
- Create **12 Aboriginal/TSI + 18 LGBTQIA+ personas** with cultural liaison review
- Obtain **HREC ethics approval** for student data collection
- Pilot test with **20 students** before production deployment

**Key Innovation**: Use **Agent OS framework** with 13 medical expert agents (FRACP-equivalent expertise) to generate personas via Claude LLM + RAG (eTG/AMH) + human validation pipeline.

### Timeline & Budget

| Metric | Value |
|--------|-------|
| **Total Duration** | 24 weeks (6 months with HREC approval, 4 months without) |
| **Total Effort** | 234-296 hours (content creation + validation) |
| **Total Budget** | $12,900 (expert panels + cultural liaison) |
| **Parallelization** | 5 agents simultaneously (4-5 weeks for 360 personas) |
| **Deployment Date** | Week 24 (assuming Week 10 HREC submission, 14-week approval) |

---

## Current State vs Target State

### Current State (Week 0)

**Technical Infrastructure**: ✅ COMPLETE
- ✅ AI Patient (Claude 3.5 Sonnet, progressive disclosure, 8 keyword triggers)
- ✅ Emotional State Machine (5 states, 12 empathy markers, Redis persistence)
- ✅ RAG Integration (Qdrant vector DB, 42,647 medical text chunks)
- ✅ AI Examiner (AMC 15-mark rubric, critical error detection)
- ✅ WebSocket Infrastructure (8-minute sessions, JWT auth, rate limiting)
- ✅ Database Schema (4 tables: patient_personas, ai_osce_attempts, ai_osce_scores, mock_exams)
- ✅ 99/99 tests passing, 81% code coverage, 0 hardcoded credentials

**Clinical Content**: ❌ EMPTY (0% COMPLETE)
- ❌ 0/360 patient personas created
- ❌ 0/200 Golden Dataset scenarios validated
- ❌ 0/12 Aboriginal/TSI personas
- ❌ 0/18 LGBTQIA+ personas
- ❌ 0/60 physical examination personas
- ❌ No HREC ethics approval

**EMR Practice System**: ❌ MISSING FRAMEWORKS (per clinical evaluation report)
- ❌ No 5 Ps physical examination framework
- ❌ No red flag recognition training
- ❌ No AHPRA competency mapping (missing 5 of 8 domains)
- ❌ No ISBAR documentation standards
- ❌ No Between the Flags escalation criteria
- ❌ No AMH medication safety validation

### Target State (Week 24)

**Clinical Content**: ✅ PRODUCTION-READY
- ✅ 360/360 patient personas created (10 specialties × 36 personas)
- ✅ 200/200 Golden Dataset scenarios validated (≥90% agreement ±2 marks)
- ✅ 12 Aboriginal/TSI personas (3.3% representation) reviewed by cultural liaison
- ✅ 18 LGBTQIA+ personas (5% representation) reviewed by LGBTQIA+ educator
- ✅ 60 physical examination personas (CVS, Respiratory, Abdominal, Neurological, MSK)
- ✅ HREC ethics approval obtained
- ✅ Pilot test complete (20 students, 50 scenarios, feedback incorporated)

**Quality Assurance**: ✅ VALIDATED
- ✅ All personas validated by ≥2 FRACP clinicians
- ✅ AMC rubric behavioral anchors added (10 specific behaviors per domain)
- ✅ Critical errors list expanded (20+ rules vs 4 currently)
- ✅ AI Examiner accuracy validated (≥90% agreement with human examiners)
- ✅ Cultural safety review complete (0 stereotypes, appropriate cultural context)

**EMR Practice System**: ✅ ENHANCED (parallel work, Weeks 3-14)
- ✅ 5 Ps framework implemented (Preparation, Position, Permission, Perform, Present)
- ✅ Red flag recognition training (20+ conditions: ACS, meningitis, AAA, anaphylaxis, etc.)
- ✅ AHPRA competency mapping (all 8 domains)
- ✅ ISBAR documentation standards
- ✅ Between the Flags escalation criteria
- ✅ AMH medication safety validation

---

## 10-Specialty Distribution

**Total: 360 personas across 10 specialties**

| Specialty | Personas | % of Total | Difficulty Split | Cultural Diversity |
|-----------|----------|------------|------------------|-------------------|
| **Cardiology** | 45 | 12.5% | 15 Easy, 18 Medium, 12 Hard | 4 Aboriginal/TSI, 5 LGBTQIA+, 6 CALD |
| **Emergency Medicine** | 45 | 12.5% | 12 Easy, 18 Medium, 15 Hard | 3 Aboriginal/TSI, 4 LGBTQIA+, 5 CALD |
| **General Practice** | 54 | 15.0% | 20 Easy, 22 Medium, 12 Hard | 2 Aboriginal/TSI, 5 LGBTQIA+, 7 CALD |
| **Respiratory** | 36 | 10.0% | 12 Easy, 15 Medium, 9 Hard | 1 Aboriginal/TSI, 3 LGBTQIA+, 4 CALD |
| **Neurology** | 27 | 7.5% | 9 Easy, 12 Medium, 6 Hard | 0 Aboriginal/TSI, 2 LGBTQIA+, 3 CALD |
| **Pediatrics** | 36 | 10.0% | 15 Easy, 15 Medium, 6 Hard | 1 Aboriginal/TSI, 2 LGBTQIA+, 4 CALD |
| **ObGyn** | 27 | 7.5% | 12 Easy, 9 Medium, 6 Hard | 0 Aboriginal/TSI, 8 LGBTQIA+ (focus) |
| **Surgery** | 27 | 7.5% | 9 Easy, 12 Medium, 6 Hard | 1 Aboriginal/TSI, 2 LGBTQIA+, 3 CALD |
| **Psychiatry** | 36 | 10.0% | 12 Easy, 15 Medium, 9 Hard | 0 Aboriginal/TSI, 6 LGBTQIA+ (focus) |
| **Infectious Diseases** | 27 | 7.5% | 9 Easy, 12 Medium, 6 Hard | 0 Aboriginal/TSI, 3 LGBTQIA+, 3 CALD |
| **TOTAL** | **360** | **100%** | **125 Easy, 148 Medium, 87 Hard** | **12 Aboriginal/TSI (3.3%), 40 LGBTQIA+ (11%), 40 CALD (11%)** |

**Note**: LGBTQIA+ target adjusted to 40 personas (11%) to better represent AMC Clinical Examination demographics. CALD (Culturally and Linguistically Diverse) personas added for interpreter simulation training.

### Persona Type Breakdown

| Type | Count | % of Total | AMC Exam Coverage |
|------|-------|------------|-------------------|
| **History-Taking** | 240 | 66.7% | 50-62% of AMC stations (8-10 of 16) |
| **Physical Examination** | 60 | 16.7% | 25-37% of AMC stations (4-6 of 16) |
| **Combined (History + Exam)** | 60 | 16.7% | 12-25% of AMC stations (2-4 of 16) |
| **TOTAL** | **360** | **100%** | **100% AMC exam coverage** |

**Physical Examination Focus** (60 personas):
- CVS examination: 15 personas (heart sounds, peripheral vascular)
- Respiratory examination: 15 personas (breath sounds, chest expansion)
- Abdominal examination: 12 personas (masses, bowel sounds, tenderness)
- Neurological examination: 12 personas (cranial nerves, power, sensation, reflexes)
- MSK examination: 6 personas (joints, GALS screen)

---

## 6-Phase Timeline

### Gantt Chart (24 Weeks)

```
Phase 1: Foundation              [===] Weeks 1-2
Phase 2: Core Content            [====================] Weeks 3-14
Phase 3: Golden Dataset          [==========] Weeks 8-16 (parallel)
Phase 4: Cultural Safety         [===================] Weeks 10-24 (HREC approval)
Phase 5: QA Validation           [========] Weeks 17-22
Phase 6: Deployment              [==] Weeks 23-24

Critical Path: Phase 1 → Phase 2 → Phase 5 → Phase 6 (18 weeks)
Parallel Work: Phase 3, Phase 4 run alongside Phase 2/5
```

---

### Phase 1: Foundation (Weeks 1-2)

**Objective**: Create 13 medical expert agents + enhance RAG system
**Effort**: 20-24 hours
**Deliverables**:
- 13 agent specification files (FRACP-equivalent expertise)
- Enhanced RAG with eTG/AMH page-specific citations
- Persona creation workflow validated (RAG → LLM → Validate)

**PRDs**:
- PRD_CC_001: Agent Creation (13 medical experts + 1 QA validator)
- PRD_CC_002: RAG Enhancement (eTG section citations, AMH drug monographs)

**Quality Gates**:
- [ ] All 13 agent specs created with learning loops
- [ ] RAG returns >0.65 confidence citations
- [ ] Test persona created and validated by 2 FRACP clinicians

**Dependencies**: None (can start immediately)

---

### Phase 2: Core Content (Weeks 3-14)

**Objective**: Create 300 personas (240 history + 60 physical exam)
**Effort**: 120-140 hours
**Parallelization**: 5 agents simultaneously × 4 batches = 4-5 weeks actual time
**Deliverables**:
- 240 history-taking personas (10 specialties)
- 60 physical examination personas (CVS, Resp, Abdo, Neuro, MSK)
- All personas validated by ≥2 FRACP clinicians

**PRDs**:
- PRD_CC_003: History-Taking Personas (240 personas)
- PRD_CC_004: Physical Examination Personas (60 personas)

**Quality Gates**:
- [ ] 300/300 personas created
- [ ] All personas follow 9-step history structure (Greeting → HPI → PMHx → Medications → Allergies → FHx → SHx → Systems Review → Closing)
- [ ] All physical exam personas follow 5 Ps framework
- [ ] ≥2 FRACP clinician reviews per persona
- [ ] Zero hardcoded credentials
- [ ] RAG citations >0.65 confidence

**Dependencies**: Phase 1 complete (agents created)

**Parallel Work**: EMR framework enhancements (5 Ps, red flags, AHPRA, ISBAR, BTF, AMH) - 60-80 hours

---

### Phase 3: Golden Dataset Validation (Weeks 8-16)

**Objective**: Validate AI Examiner accuracy with 200 expert-scored scenarios
**Effort**: 30-40 hours (expert panel scoring)
**Budget**: $9,900 (6 FRACP clinicians × 5 hours × $330/hour)
**Deliverables**:
- 200 scenarios scored by ≥6 FRACP clinicians
- Inter-rater reliability analysis (Fleiss' kappa ≥0.70)
- AI Examiner accuracy report (≥90% agreement ±2 marks)

**PRDs**:
- PRD_CC_005: Golden Dataset Validation

**Quality Gates**:
- [ ] 200/200 scenarios scored by ≥6 FRACP clinicians
- [ ] Inter-rater reliability ≥0.70 (substantial agreement)
- [ ] AI Examiner vs human examiner agreement ≥90% ±2 marks
- [ ] Critical error detection 100% accurate (zero false negatives)

**Dependencies**: Phase 2 (100 personas created minimum)

**Parallel Work**: Runs alongside Phase 2 (can start Week 8 when first 100 personas complete)

---

### Phase 4: Cultural Safety + Ethics (Weeks 10-24)

**Objective**: Create culturally safe personas + obtain HREC ethics approval
**Effort**: 28-36 hours (persona creation + liaison review)
**Budget**: $3,000 (cultural liaison + LGBTQIA+ educator)
**Timeline**: 14 weeks (HREC approval: 3-6 months from submission)
**Deliverables**:
- 12 Aboriginal/TSI personas reviewed by cultural liaison
- 40 LGBTQIA+ personas reviewed by LGBTQIA+ health educator
- 40 CALD personas with interpreter simulation
- HREC ethics approval obtained

**PRDs**:
- PRD_CC_006: Cultural Safety Content
- PRD_CC_007: HREC Ethics Approval

**Quality Gates**:
- [ ] 12 Aboriginal/TSI personas created (3.3% representation)
- [ ] Cultural liaison review complete (0 stereotypes, appropriate context)
- [ ] 40 LGBTQIA+ personas created (11% representation)
- [ ] LGBTQIA+ educator review complete
- [ ] 40 CALD personas created with interpreter protocols
- [ ] HREC application submitted (Week 10)
- [ ] HREC approval obtained (Week 24 target)

**Dependencies**: Phase 2 (core personas created first)

**Critical Path**: HREC approval is 14-26 weeks (3-6 months) - submit early (Week 10)

---

### Phase 5: QA Validation + Pilot Testing (Weeks 17-22)

**Objective**: Quality audit all 360 personas + pilot test with students
**Effort**: 24-32 hours
**Deliverables**:
- 360 persona quality audit complete
- 20 students pilot test (50 scenarios)
- Feedback incorporated

**PRDs**:
- PRD_CC_008: QA Validation (360 persona audit)
- PRD_CC_009: Pilot Testing (20 students, 50 scenarios)

**Quality Gates**:
- [ ] All 360 personas audited for clinical accuracy
- [ ] Zero critical errors (wrong diagnosis, dangerous advice)
- [ ] 20 students complete pilot test
- [ ] Student satisfaction ≥4/5
- [ ] Feedback incorporated (scenario improvements, rubric clarifications)

**Dependencies**: Phase 2, Phase 4 complete (all 360 personas created)

---

### Phase 6: Deployment (Weeks 23-24)

**Objective**: Launch to students + monitoring
**Effort**: 12-16 hours
**Deliverables**:
- Production deployment
- Monitoring dashboard
- Student support materials

**PRDs**:
- PRD_CC_010: Deployment & Student Launch

**Quality Gates**:
- [ ] All 360 personas loaded into production database
- [ ] Student access enabled
- [ ] Monitoring dashboard operational
- [ ] Support documentation published

**Dependencies**: Phase 5 complete, HREC approval obtained

---

## Budget Breakdown

**Total Budget**: $12,900

| Item | Quantity | Rate | Total | Phase |
|------|----------|------|-------|-------|
| **Expert Panel (FRACP Clinicians)** | 6 clinicians × 5 hours | $330/hour | $9,900 | Phase 3 |
| **Cultural Liaison (Aboriginal Health)** | 10 hours | $200/hour | $2,000 | Phase 4 |
| **LGBTQIA+ Health Educator** | 5 hours | $200/hour | $1,000 | Phase 4 |
| **TOTAL** | - | - | **$12,900** | - |

**Additional Costs (Already Covered)**:
- Claude API costs: ~$50-100/month (covered by existing subscription)
- Agent OS infrastructure: $0 (open-source framework)
- Developer time: 234-296 hours (internal team, no additional cost)

---

## Dependencies & Critical Path

### Critical Path (18 weeks minimum)

```
Week 0: Clinical evaluation complete (DONE)
  ↓
Weeks 1-2: Phase 1 (Agent creation + RAG enhancement) [BLOCKS Phase 2]
  ↓
Weeks 3-14: Phase 2 (300 personas created) [BLOCKS Phase 5]
  ↓
Weeks 17-22: Phase 5 (QA validation + pilot test) [BLOCKS Phase 6]
  ↓
Weeks 23-24: Phase 6 (Deployment)
```

**Total Critical Path**: 24 weeks (6 months)

### Parallel Work (Off Critical Path)

- **Phase 3**: Weeks 8-16 (runs parallel to Phase 2)
- **Phase 4**: Weeks 10-24 (HREC approval parallel to all phases)
- **EMR Frameworks**: Weeks 3-14 (parallel to Phase 2)

### Blocking Dependencies

| Dependency | Blocks | Impact |
|------------|--------|--------|
| Phase 1 not complete | Phase 2 cannot start | 13 agents needed to create personas |
| Phase 2 <100 personas | Phase 3 cannot start | Need scenarios for Golden Dataset |
| Phase 2 not complete | Phase 5 cannot start | Need all 360 personas for QA audit |
| Phase 5 not complete | Phase 6 cannot start | Cannot deploy without pilot test |
| HREC approval pending | Phase 6 deployment | Cannot collect student data legally |

---

## Risk Mitigation

### Timeline Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **HREC approval delayed (6+ months)** | HIGH | CRITICAL | Submit Week 10, continue content creation in parallel. Deploy without data collection if needed. |
| **Expert panel unavailable** | MEDIUM | HIGH | Book 6 FRACP clinicians early (Week 6-8). Have backup list of 10 clinicians. |
| **Cultural liaison unavailable** | MEDIUM | HIGH | Partner with Aboriginal health organization early (Week 8-10). Budget for backup liaison. |
| **Agent-generated content inaccurate** | LOW | HIGH | All personas validated by ≥2 FRACP clinicians. Use RAG citations >0.65 confidence. |
| **Pilot test reveals major issues** | LOW | MEDIUM | Build 2-week buffer (Weeks 21-22) for feedback incorporation. |

### Budget Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Expert panel costs exceed $9,900** | LOW | MEDIUM | Fixed-rate contracts with 6 clinicians. Cap at 5 hours each. |
| **Cultural liaison costs exceed $2,000** | LOW | LOW | Fixed-rate contract. Cap at 10 hours. |
| **Claude API costs spike** | LOW | LOW | Monitor token usage. Batch requests. Use caching. |

### Quality Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **AI-generated personas clinically inaccurate** | MEDIUM | CRITICAL | Mandatory ≥2 FRACP clinician validation per persona. RAG citations required. |
| **Cultural stereotypes in personas** | MEDIUM | CRITICAL | Mandatory cultural liaison review before deployment. Use sensitivity readers. |
| **AI Examiner scoring inconsistent** | MEDIUM | HIGH | Golden Dataset validation (≥90% agreement). Inter-rater reliability ≥0.70. |
| **Students misuse platform (rely solely on irStudy)** | HIGH | MEDIUM | Clear disclaimers: "Supplement with physical examination practice on real patients." |

---

## Quality Gates

### Phase 1 Quality Gates
- [ ] 13 agent specification files created
- [ ] Each agent has FRACP-equivalent expertise documented
- [ ] RAG returns >0.65 confidence citations
- [ ] Test persona validated by 2 FRACP clinicians
- [ ] Zero hardcoded credentials

### Phase 2 Quality Gates
- [ ] 300/300 personas created (240 history + 60 physical exam)
- [ ] All personas follow 9-step history structure
- [ ] All physical exam personas follow 5 Ps framework
- [ ] ≥2 FRACP clinician reviews per persona
- [ ] RAG citations >0.65 confidence
- [ ] Zero clinical inaccuracies

### Phase 3 Quality Gates
- [ ] 200/200 scenarios scored by ≥6 FRACP clinicians
- [ ] Inter-rater reliability ≥0.70 (Fleiss' kappa)
- [ ] AI Examiner accuracy ≥90% ±2 marks
- [ ] Critical error detection 100% accurate

### Phase 4 Quality Gates
- [ ] 12 Aboriginal/TSI personas reviewed by cultural liaison
- [ ] 40 LGBTQIA+ personas reviewed by LGBTQIA+ educator
- [ ] 40 CALD personas with interpreter protocols
- [ ] Zero cultural stereotypes
- [ ] HREC approval obtained

### Phase 5 Quality Gates
- [ ] 360 persona quality audit complete
- [ ] 20 students pilot test complete
- [ ] Student satisfaction ≥4/5
- [ ] Feedback incorporated

### Phase 6 Quality Gates
- [ ] All 360 personas in production database
- [ ] Student access enabled
- [ ] Monitoring dashboard operational
- [ ] Support documentation published

---

## Success Metrics

### Content Metrics (Week 24)
- **360/360 personas created** (100% target)
- **200/200 Golden Dataset scenarios validated** (100% target)
- **12 Aboriginal/TSI personas** (3.3% representation)
- **40 LGBTQIA+ personas** (11% representation)
- **40 CALD personas** (11% representation)

### Quality Metrics
- **AI Examiner accuracy**: ≥90% agreement ±2 marks vs human examiners
- **Inter-rater reliability**: ≥0.70 (Fleiss' kappa, substantial agreement)
- **Critical error detection**: 100% accurate (zero false negatives)
- **Clinical accuracy**: 100% personas validated by ≥2 FRACP clinicians
- **Cultural safety**: 0 stereotypes (cultural liaison approval)

### Student Metrics (Post-Launch)
- **Student satisfaction**: ≥4/5 average rating
- **Platform usage**: ≥50 OSCE sessions per student per month
- **AMC exam pass rate**: ≥80% (vs 60% baseline for international medical graduates)
- **Student feedback**: Qualitative themes (empathy practice, red flag recognition, etc.)

### Technical Metrics
- **Test coverage**: ≥70% (currently 81%, maintain)
- **Test pass rate**: 100% (currently 99/99, maintain)
- **Security violations**: 0 (maintain)
- **Response time**: <3s (AI Patient), <5s (AI Examiner), <500ms (RAG)

---

## Conclusion

This 24-week master plan transforms the irStudy AI OSCE Simulation System from an **empty technical shell** to a **production-ready clinical education platform** with:
- **360 expert-validated patient personas**
- **200 Golden Dataset scenarios** (AI Examiner accuracy proven)
- **Full AMC Clinical Examination coverage** (history, physical exam, communication)
- **Cultural safety** (Aboriginal/TSI, LGBTQIA+, CALD representation)
- **HREC ethics approval** (legal student data collection)
- **Pilot-tested** (20 students, feedback incorporated)

**Total Investment**: $12,900 + 234-296 hours = Production-ready platform serving Australian medical students preparing for AMC Clinical Examination.

**Next Steps**:
1. Approve budget ($12,900)
2. Execute PRD_CC_001 (create 13 medical expert agents)
3. Execute PRD_CC_002 (enhance RAG system)
4. Start Phase 2 (360 persona creation, Weeks 3-14)

---

**Status**: ✅ READY FOR EXECUTION
**Approval Required**: Budget ($12,900), Timeline (24 weeks), HREC submission (Week 10)
**Last Updated**: 2026-03-15
**Version**: 1.0
