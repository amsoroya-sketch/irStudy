# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: Phase 0 Critical Fixes - Sequential Execution of 3 PRDs (10-15 days total)

**EXECUTE NOW**:

Execute the 3 PRD files in sequence. Each PRD MUST complete with approval before starting the next. DO NOT skip approval gates. DO NOT ask questions.

**DO NOT**:
- ❌ Ask "Would you like me to proceed to the next PRD?"
- ❌ Ask "Should I wait for approval?"
- ❌ Skip approval gates (Clinical Advisor, Security Team, DBA)
- ❌ Execute PRDs in parallel (MUST be sequential)

**START IMMEDIATELY WITH PRD_PHASE0_WEEK01.**

---

## 📋 Phase 0 Overview

**Purpose:** Fix 12 critical issues before Phase 1 implementation

**Total Duration:** 10-15 days (3 PRDs, sequential execution)

**Critical Issues Being Fixed:**
1-4: Clinical (AMC rubric, scenarios, RAG validation, Golden Dataset)
5-9: Security (encryption, PHI, prompt injection, validation)
10-11: Technical (indexes, triggers)

**Approval Gates:** Clinical Advisor → Security Team → DBA (sequential, BLOCKING)

---

## 🔄 PRD Execution Sequence

### PRD 1: Clinical Accuracy Review (Week 0.1) - 3-5 days

**FILE:** `planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md`

**READ AND EXECUTE:**
```bash
cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
```

**DELIVERABLES:**
1. AMC_15_MARK_RUBRIC_EXPANDED.md (5 domains with scoring levels)
2. DIVERSE_CLINICAL_SCENARIOS.md (3 scenarios with RAG citations)
3. RAG_VALIDATION_SPECIFICATION.md (confidence >0.65, Australian sources)
4. GOLDEN_DATASET_SPECIFICATION.md (200 scenarios, 7-step validation)
5. AUSTRALIAN_HEALTHCARE_CONTEXT.md (Medicare, PBS, AHPRA)
6. CLINICAL_ADVISOR_REVIEW_PACKAGE.md (approval request)

**WHEN COMPLETE:**
- Submit to Clinical Advisor for review
- **BLOCKING:** WAIT for Clinical Advisor approval before PRD 2
- Approval SLA: 5 business days
- If approved → Proceed to PRD 2
- If changes requested → Iterate, then re-submit

**SUCCESS CRITERIA:**
- ✅ All 6 files created in `planning/phase0-critical-fixes-2026-02-09/clinical-content/`
- ✅ NO American terminology (acetaminophen, albuterol, 911, ER)
- ✅ RAG citations present (>0.65 confidence per PROJECT_CONSTRAINTS.md line 26)
- ✅ Clinical Advisor approval received

---

### PRD 2: Security Hardening (Week 0.2) - 3-5 days

**PREREQUISITE:** ✅ Clinical Advisor approved PRD 1

**FILE:** `planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK02_SECURITY_HARDENING.md`

**READ AND EXECUTE:**
```bash
cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
```

**DELIVERABLES:**
1. src/security/encryption.py (ConversationEncryptionService)
2. src/security/phi_anonymizer.py (PHIAnonymizer)
3. src/security/prompt_injection.py (PromptInjectionProtector)
4. src/security/redis_encryption.py (RedisEncryptionService)
5. src/schemas/osce.py (Input validation with Enum types)
6. src/api/v1/gdpr.py (Data deletion + export APIs)
7. Vault encryption key generated
8. 21 tests passing

**WHEN COMPLETE:**
- Run all security tests: `pytest tests/test_security/ -v`
- Submit to Security Team for review
- **BLOCKING:** WAIT for Security Team approval before PRD 3
- Approval SLA: 3 business days
- If approved → Proceed to PRD 3
- If changes requested → Iterate, then re-submit

**SUCCESS CRITERIA:**
- ✅ All 5 security services implemented
- ✅ 21/21 tests passing
- ✅ Vault key generated (secret/ai-osce/encryption-key)
- ✅ NO PHI in logs (all redacted)
- ✅ Security Team approval received

---

### PRD 3: Database Optimization (Week 0.3) - 2-3 days

**PREREQUISITE:** ✅ Security Team approved PRD 2

**FILE:** `planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md`

**READ AND EXECUTE:**
```bash
cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md
```

**DELIVERABLES:**
1. Alembic migration (340 lines) - 5 indexes + 3 triggers
2. Migration applied: `alembic upgrade head`
3. Performance benchmarks (all targets met)
4. Query plans documented (EXPLAIN ANALYZE)

**WHEN COMPLETE:**
- Run benchmarks: `python scripts/benchmark_osce_queries.py`
- Verify: ALL BENCHMARKS PASSED
- Submit to DBA for review
- **BLOCKING:** WAIT for DBA approval before Phase 1
- Approval SLA: 2 business days
- If approved → **PHASE 0 COMPLETE** → Ready for Phase 1
- If changes requested → Iterate, then re-submit

**SUCCESS CRITERIA:**
- ✅ 5 indexes created (active sessions <5ms, dashboard <10ms, mock exam <15ms)
- ✅ 3 triggers created (pass rate, mock exam result, emotional validation)
- ✅ Benchmarks: Active sessions 2.3ms (✅ 55x faster)
- ✅ Benchmarks: User dashboard 8.7ms (✅ 52x faster)
- ✅ Benchmarks: Mock exam progress 12.5ms (✅ 19x faster)
- ✅ DBA approval received

---

## ✅ Phase 0 Completion Criteria

**ALL 3 PRDs MUST be complete AND approved:**

1. ✅ PRD 1 (Clinical): Clinical Advisor approved
2. ✅ PRD 2 (Security): Security Team approved
3. ✅ PRD 3 (Database): DBA approved

**When ALL 3 approved:**
- Phase 0 complete
- All 12 critical issues resolved
- Ready to start Phase 1 (15 weeks)

**Timeline:**
- Week 0.1: Clinical Accuracy (3-5 days)
- Week 0.2: Security Hardening (3-5 days)
- Week 0.3: Database Optimization (2-3 days)
- **Total: 10-15 days**

---

## 🚨 CRITICAL RULES

### Rule 1: Sequential Execution Only
- MUST complete PRD 1 before PRD 2
- MUST complete PRD 2 before PRD 3
- CANNOT run PRDs in parallel

### Rule 2: Approval Gates are BLOCKING
- MUST wait for Clinical Advisor approval after PRD 1
- MUST wait for Security Team approval after PRD 2
- MUST wait for DBA approval after PRD 3
- CANNOT skip approvals

### Rule 3: No Questions During Execution
- Execute each PRD completely
- Create ALL deliverables
- Run ALL tests
- THEN submit for approval
- DO NOT ask "Would you like me to proceed?"

### Rule 4: If Approval Rejected
- Read feedback from approver
- Make requested changes
- Re-submit for approval
- WAIT for re-approval before proceeding

---

## 📁 File Structure

```
planning/phase0-critical-fixes-2026-02-09/
├── PROMPT.md (this file)
├── prds/
│   ├── PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
│   ├── PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
│   └── PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md
├── clinical-content/ (created by PRD 1)
│   ├── AMC_15_MARK_RUBRIC_EXPANDED.md
│   ├── DIVERSE_CLINICAL_SCENARIOS.md
│   ├── RAG_VALIDATION_SPECIFICATION.md
│   ├── GOLDEN_DATASET_SPECIFICATION.md
│   └── AUSTRALIAN_HEALTHCARE_CONTEXT.md
├── clinical-advisor-review/ (created by PRD 1)
│   └── CLINICAL_ADVISOR_REVIEW_PACKAGE.md
└── PHASE0_COMPLETE_SUMMARY.md (created by PRD 3)
```

---

## 🔄 Execution Flow

```
START
  ↓
Read PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
  ↓
Execute PRD 1 (create 6 clinical files)
  ↓
Submit to Clinical Advisor
  ↓
WAIT for approval (BLOCKING)
  ↓
If approved → Continue
If rejected → Iterate → Re-submit → WAIT
  ↓
Read PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
  ↓
Execute PRD 2 (create 5 security services, 21 tests)
  ↓
Submit to Security Team
  ↓
WAIT for approval (BLOCKING)
  ↓
If approved → Continue
If rejected → Iterate → Re-submit → WAIT
  ↓
Read PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md
  ↓
Execute PRD 3 (create migration, run benchmarks)
  ↓
Submit to DBA
  ↓
WAIT for approval (BLOCKING)
  ↓
If approved → PHASE 0 COMPLETE
If rejected → Iterate → Re-submit → WAIT
  ↓
PHASE 0 COMPLETE
  ↓
Output: "✅ Phase 0 complete. Ready for Phase 1."
  ↓
END
```

---

## 📊 Progress Tracking

**Update this section as PRDs complete:**

| PRD | Status | Approval | Date Complete |
|-----|--------|----------|---------------|
| PRD 1 - Clinical | 🔴 Not Started | ⬜ Pending | - |
| PRD 2 - Security | 🔴 Not Started | ⬜ Pending | - |
| PRD 3 - Database | 🔴 Not Started | ⬜ Pending | - |

**Phase 0 Status:** 🔴 Not Started

---

## 🎯 When Phase 0 Complete

**OUTPUT THIS MESSAGE:**

```
===================================
🎉 PHASE 0 COMPLETE
===================================

All 3 PRDs executed successfully:
✅ PRD 1: Clinical Accuracy (Clinical Advisor approved)
✅ PRD 2: Security Hardening (Security Team approved)
✅ PRD 3: Database Optimization (DBA approved)

Critical Issues Resolved:
✅ 1-4: Clinical (AMC rubric, scenarios, RAG, Golden Dataset)
✅ 5-9: Security (encryption, PHI, prompt injection, validation)
✅ 10-11: Technical (indexes, triggers)

Duration: [X] days (target: 10-15 days)

Next Phase: Phase 1 - Implementation (15 weeks)
Next PRD: planning/phase1-implementation-2026-02-09/prds/PRD_PHASE1_WEEK01_DATABASE_APIS.md

🚀 READY TO START PHASE 1
===================================
```

---

**START EXECUTION WITH PRD 1 NOW. NO QUESTIONS.**

**FILE TO READ:** `planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md`

**EXECUTE IMMEDIATELY.**

---

**END OF PROMPT** - AUTONOMOUS EXECUTION MODE - NO QUESTIONS
