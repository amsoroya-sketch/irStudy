# Agent OS Regeneration Plan - Executive Summary

**Document**: `/home/dev/Development/irStudy/planning/jan-26-plan/AGENT_OS_REGENERATION_PLAN.md`
**Pages**: 1,465 lines
**Status**: READY FOR EXECUTION
**Created**: 2026-01-26

---

## Critical Sections Reference

### 1. Agent OS Routing Architecture (Lines 35-200)
- Specialty-to-agent mapping (MED-001, MED-002, MED-009)
- Agent capabilities matrix
- Task delegation pattern with proper imports

### 2. Fail-Fast Validation Pipeline (Lines 201-500)
- **3-Stage Validation**:
  - Stage 1: Pre-generation (RAG, LLM, Agent OS checks)
  - Stage 2: Incremental per-MCQ (8 validation steps)
  - Stage 3: Post-generation (QA-003, QA-001, substance check)
- Retry logic (max 2 retries, 3 total attempts)
- Validation scripts integration

### 3. Specialty-Specific Generation (Lines 501-800)
- **Priority 1: Respiratory (MED-002)** - Day 1-2
  - 5 topic areas: Asthma, COPD, Pneumonia, PE, Other
  - 6 tools: spirometry, CXR, Wells PE, CURB-65, etc.
  - Detailed prompt template with constraints
- **Priority 2: Cardiology (MED-001)** - Day 2-3
  - 5 topic areas: ACS, Heart Failure, Arrhythmias, HTN, Other
  - 6 tools: ECG, GRACE, TIMI, CHA2DS2-VASc, etc.
- **Priority 3: Psychiatry (MED-009)** - Day 3-4
  - 5 topic areas: Depression, Anxiety, Psychosis, Bipolar, Other
  - 24 tools: PHQ-9, GAD-7, MSE, BPRS, Y-BOCS, etc.

### 4. Quality Gates (Lines 801-1000)
- **Pre-generation**: `pre_generation_check.sh` (4 checks, blocking)
- **Incremental**: `validate_mcq_incremental()` (7 validation rules)
- **Post-generation**: `post_generation_check.sh` (4 validators, blocking)
- **Pre-commit hook**: Final gate (blocks placeholder content)

### 5. Success Metrics (Lines 1001-1100)
- **Quantitative**: 10 metrics (Agent OS usage, placeholders, citations, etc.)
- **Qualitative**: 5 metrics (clinical accuracy, difficulty, realism)
- **Performance**: 4 metrics (generation speed, retry rate, success rate)
- **Success Criteria**: Go/No-Go decision framework

### 6. Execution Timeline (Lines 1101-1250)
- **Day 1-2**: Respiratory (8-10 hours, 200 MCQs)
- **Day 2-3**: Cardiology (8-10 hours, 200 MCQs)
- **Day 3-4**: Psychiatry (8-10 hours, 200 MCQs)
- **Day 5**: Final validation & documentation (4-6 hours)
- **Total**: 3-5 days with quality gates

### 7. Rollback Plan (Lines 1251-1350)
- Failure criteria (>5% placeholders, <50% QA-003 approval)
- Rollback steps (stop, diagnose, fallback options)
- Partial success handling (commit good MCQs, fix issues, resume)

### 8. Monitoring & Logging (Lines 1351-1400)
- Real-time monitor script (10-second refresh)
- Log levels (INFO, WARNING, ERROR, CRITICAL)
- Log format with timestamps and agent IDs

### 9. Deliverables Checklist (Lines 1401-1450)
- 8 code artifacts (generation scripts, validation scripts)
- 4 data artifacts (600 MCQs in JSON)
- 7 validation reports (QA-003, Australian compliance)
- 5 documentation updates
- 5 git commits

---

## Key Innovations

1. **Agent OS Integration**: Route by specialty to medical experts (NOT generic client)
2. **Fail-Fast Philosophy**: Validate at 3 stages (pre, incremental, post)
3. **LLM-Powered Generation**: RAG citation CONTENT passed to LLM (NOT templates)
4. **Specialty Tools**: ECG, spirometry, MSE applied per specialty
5. **Zero-Error Policy**: 0 placeholders enforced at every gate

---

## Differences from Previous Approach

| Previous (75% Failure) | Agent OS (Target: 100% Success) |
|------------------------|----------------------------------|
| Generic OllamaClient | Specialty-routed agents (MED-001/002/009) |
| Template-based generation | LLM-powered with RAG content |
| Post-generation validation | Fail-fast at 3 stages |
| No specialty tools | ECG, spirometry, MSE applied |
| 2,208 placeholders detected | 0 placeholders enforced |

---

## Quick Start

```bash
# 1. Pre-generation check (MUST PASS before proceeding)
cd /home/dev/Development/irStudy
./scripts-jan-26/pre_generation_check.sh

# 2. Generate respiratory MCQs (Priority 1)
python3 scripts-jan-26/generate_respiratory_mcqs.py

# 3. Post-generation validation (MUST PASS before next specialty)
./scripts-jan-26/post_generation_check.sh respiratory

# 4. If PASS, proceed to cardiology
python3 scripts-jan-26/generate_cardiology_mcqs.py
./scripts-jan-26/post_generation_check.sh cardiology

# 5. If PASS, proceed to psychiatry
python3 scripts-jan-26/generate_psychiatry_mcqs.py
./scripts-jan-26/post_generation_check.sh psychiatry

# 6. Final validation and commit
git add data-jan-26/mcqs/
git commit -m "feat: Add 600 Agent OS MCQs (MED-001/002/009)"
```

---

## PM Next Actions

1. Review this plan with user
2. Get approval for fresh start approach
3. Delegate to specialist agents:
   - **testing-qa-expert**: Create validation scripts
   - **MED-002**: Generate respiratory MCQs
   - **MED-001**: Generate cardiology MCQs
   - **MED-009**: Generate psychiatry MCQs
4. Monitor progress with fail-fast gates
5. Validate deliverables against success metrics

---

**Human-in-the-Loop**: User approval required before execution.
**Risk Level**: LOW (fail-fast prevents large-scale failures)
**Estimated Duration**: 3-5 days (realistic with quality gates)
**Confidence**: HIGH (lessons learned from 2,208 MCQ failure applied)
