# Phase 0: Critical Fixes - Planning Package

**Status**: 🟡 Ready for Execution
**Duration**: 10-15 days (3 PRDs, sequential)
**Created**: 2026-02-09
**Last Updated**: 2026-02-09

---

## 📋 Overview

Phase 0 addresses **12 critical issues** identified in expert reviews before Phase 1 implementation begins. These fixes are essential for:

- **Clinical Accuracy** (Issues 1-4): AMC rubric compliance, diverse scenarios, RAG validation, Golden Dataset
- **Security Hardening** (Issues 5-9): Encryption, PHI anonymization, prompt injection protection, GDPR compliance
- **Database Optimization** (Issues 10-11): Performance indexes, automated triggers

**Why Phase 0 is Required:**
- Expert reviews scored system at 4.1/10 (Clinical) and 6.0/10 (Security)
- 12 critical gaps must be resolved before building Phase 1 features
- Approval gates ensure quality before progression

---

## 🚀 Quick Start

### For Ralph Autonomous Execution:

```bash
# Navigate to project root
cd /home/dev/Development/irStudy

# Execute Phase 0 with Ralph
# Point Ralph to the PROMPT.md file
ralph execute planning/phase0-critical-fixes-2026-02-09/PROMPT.md
```

Ralph will:
1. Execute PRD 1 (Clinical Accuracy)
2. Wait for Clinical Advisor approval (BLOCKING)
3. Execute PRD 2 (Security Hardening)
4. Wait for Security Team approval (BLOCKING)
5. Execute PRD 3 (Database Optimization)
6. Wait for DBA approval (BLOCKING)
7. Mark Phase 0 complete

### For Manual Execution:

```bash
# Read each PRD sequentially
cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
# Follow implementation steps
# Submit for Clinical Advisor approval
# WAIT for approval before proceeding

cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
# Follow implementation steps
# Submit for Security Team approval
# WAIT for approval before proceeding

cat planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md
# Follow implementation steps
# Submit for DBA approval
# WAIT for approval before Phase 1
```

---

## 📁 Directory Structure

```
planning/phase0-critical-fixes-2026-02-09/
├── README.md                    # This file - overview and quick start
├── INDEX.md                     # Detailed file catalog and dependencies
├── PROMPT.md                    # Master Ralph execution file
│
├── prds/                        # Product Requirement Documents
│   ├── PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
│   ├── PRD_PHASE0_WEEK02_SECURITY_HARDENING.md
│   └── PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md
│
├── clinical-content/            # Created by PRD 1 (Week 0.1)
│   ├── AMC_15_MARK_RUBRIC_EXPANDED.md
│   ├── DIVERSE_CLINICAL_SCENARIOS.md
│   ├── RAG_VALIDATION_SPECIFICATION.md
│   ├── GOLDEN_DATASET_SPECIFICATION.md
│   └── AUSTRALIAN_HEALTHCARE_CONTEXT.md
│
├── clinical-advisor-review/     # Created by PRD 1 (Week 0.1)
│   └── CLINICAL_ADVISOR_REVIEW_PACKAGE.md
│
└── PHASE0_COMPLETE_SUMMARY.md   # Created by PRD 3 (Week 0.3)
```

---

## 🔄 Execution Workflow

```
┌─────────────────────────────────────────────────┐
│  START PHASE 0                                  │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  PRD 1: Clinical Accuracy Review (3-5 days)     │
│  - Create 6 clinical content files              │
│  - AMC rubric, scenarios, RAG spec, Golden DS   │
│  - Australian healthcare context                │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  ⏸️  APPROVAL GATE 1: Clinical Advisor          │
│  - Review all clinical content                  │
│  - SLA: 5 business days                         │
│  - BLOCKING: Must approve before PRD 2          │
└─────────────────┬───────────────────────────────┘
                  │ ✅ Approved
                  ▼
┌─────────────────────────────────────────────────┐
│  PRD 2: Security Hardening (3-5 days)           │
│  - Implement 5 security services                │
│  - Encryption, PHI anonymization, prompt guard  │
│  - GDPR APIs, 21 tests                          │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  ⏸️  APPROVAL GATE 2: Security Team             │
│  - Review security implementation               │
│  - SLA: 3 business days                         │
│  - BLOCKING: Must approve before PRD 3          │
└─────────────────┬───────────────────────────────┘
                  │ ✅ Approved
                  ▼
┌─────────────────────────────────────────────────┐
│  PRD 3: Database Optimization (2-3 days)        │
│  - Create migration with 5 indexes + 3 triggers │
│  - Achieve 55x performance improvement          │
│  - Run benchmarks, document results             │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  ⏸️  APPROVAL GATE 3: DBA                       │
│  - Review database changes                      │
│  - SLA: 2 business days                         │
│  - BLOCKING: Must approve before Phase 1        │
└─────────────────┬───────────────────────────────┘
                  │ ✅ Approved
                  ▼
┌─────────────────────────────────────────────────┐
│  ✅ PHASE 0 COMPLETE - READY FOR PHASE 1        │
└─────────────────────────────────────────────────┘
```

---

## 📊 PRD Summary

### PRD 1: Clinical Accuracy Review (Week 0.1)

**File**: `prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md`

**Duration**: 3-5 days
**Deliverables**: 6 clinical content files
**Approval Gate**: Clinical Advisor (5 business days SLA)

**Fixes Issues**:
1. AMC 15-mark rubric expansion (5 domains with detailed scoring)
2. Diverse clinical scenarios (Aboriginal, CALD, Obstetric contexts)
3. RAG validation specification (>0.65 confidence, Australian sources)
4. Golden Dataset specification (200 scenarios, 7-step validation)

**Success Criteria**:
- ✅ All 6 files created in `clinical-content/`
- ✅ NO American terminology (acetaminophen → paracetamol)
- ✅ RAG citations present (>0.65 confidence per PROJECT_CONSTRAINTS.md line 26)
- ✅ Clinical Advisor approval received

**Key Commands**:
```bash
# Read source material
cat planning/ai-osce-v2-comprehensive-plan-2026-02-09/expert-reviews/AI_OSCE_CLINICAL_REVIEW_REPORT.md

# Verify no American terminology
grep -iE "(acetaminophen|albuterol|epinephrine|911|ER|mom)" clinical-content/*.md
# Should return 0 results

# Verify RAG citations present
grep -c "SOURCE:" clinical-content/DIVERSE_CLINICAL_SCENARIOS.md
# Should return 9+ (3 scenarios × 3 citations minimum)
```

---

### PRD 2: Security Hardening (Week 0.2)

**File**: `prds/PRD_PHASE0_WEEK02_SECURITY_HARDENING.md`

**Duration**: 3-5 days
**Deliverables**: 5 security services + GDPR APIs + 21 tests
**Approval Gate**: Security Team (3 business days SLA)

**Fixes Issues**:
5. Conversation encryption (Fernet AES-128-CBC)
6. PHI anonymization in logs (email, phone, Medicare redaction)
7. Prompt injection protection (3 severity levels)
8. Redis encryption for session data
9. Input validation with Enum types

**Success Criteria**:
- ✅ All 5 security services implemented (`src/security/*.py`)
- ✅ 21/21 tests passing (`pytest tests/test_security/ -v`)
- ✅ Vault key generated (`secret/ai-osce/encryption-key`)
- ✅ NO PHI in logs (all redacted)
- ✅ Security Team approval received

**Key Commands**:
```bash
# Generate encryption key
vault write secret/ai-osce/encryption-key value=$(openssl rand -base64 32)

# Run all security tests
VAULT_ADDR=http://localhost:8200 VAULT_ROOT_TOKEN=dev-only-token-change-in-prod \
pytest tests/test_security/ -v --cov=src/security --cov-report=term-missing

# Verify no PHI in logs
grep -iE "(test@example\.com|\+61[0-9]{9}|\d{10}\s?\d)" logs/*.log
# Should return 0 results (all PHI should be redacted)
```

---

### PRD 3: Database Optimization (Week 0.3)

**File**: `prds/PRD_PHASE0_WEEK03_DATABASE_OPTIMIZATION.md`

**Duration**: 2-3 days
**Deliverables**: Alembic migration (5 indexes + 3 triggers)
**Approval Gate**: DBA (2 business days SLA)

**Fixes Issues**:
10. Performance indexes (55x faster queries)
11. Automated triggers (pass rate calculation, validation)

**Success Criteria**:
- ✅ 5 indexes created (active sessions, user dashboard, mock exam, tags, date range)
- ✅ 3 triggers created (pass rate, mock exam result, emotional validation)
- ✅ Benchmarks: Active sessions <5ms (target: 2.3ms, 55x improvement)
- ✅ Benchmarks: User dashboard <10ms (target: 8.7ms, 52x improvement)
- ✅ Benchmarks: Mock exam progress <15ms (target: 12.5ms, 19x improvement)
- ✅ DBA approval received

**Key Commands**:
```bash
# Apply migration
alembic upgrade head

# Run benchmarks
python scripts/benchmark_osce_queries.py

# Expected output:
# Active Sessions Query: 2.3ms (p95: 2.8ms) ✅ PASS (<5ms target)
# User Dashboard Query: 8.7ms (p95: 9.2ms) ✅ PASS (<10ms target)
# Mock Exam Progress Query: 12.5ms (p95: 13.8ms) ✅ PASS (<15ms target)
# ALL BENCHMARKS PASSED ✅
```

---

## ✅ Completion Criteria

Phase 0 is **COMPLETE** when:

1. ✅ PRD 1 executed AND Clinical Advisor approved
2. ✅ PRD 2 executed AND Security Team approved
3. ✅ PRD 3 executed AND DBA approved

**Output Message:**
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

## 🚨 Critical Rules

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
- Ralph uses directive language only (no "Would you like...")

### Rule 4: If Approval Rejected
- Read feedback from approver
- Make requested changes
- Re-submit for approval
- WAIT for re-approval before proceeding

---

## 📚 Related Documentation

**Source Materials** (read these PRDs were created from):
- `planning/ai-osce-v2-comprehensive-plan-2026-02-09/AI_OSCE_V2_ARCHITECTURE_PLAN.md` - Original architecture (40,000 tokens)
- `planning/ai-osce-v2-comprehensive-plan-2026-02-09/expert-reviews/AI_OSCE_CLINICAL_REVIEW_REPORT.md` - Clinical expert review
- `planning/ai-osce-v2-comprehensive-plan-2026-02-09/expert-reviews/AI_OSCE_SECURITY_REVIEW.md` - Security expert review
- `planning/ai-osce-v2-comprehensive-plan-2026-02-09/expert-reviews/AI_OSCE_TECHNICAL_REVIEW_PART2.md` - Database optimization review

**Project Constraints**:
- `PROJECT_CONSTRAINTS.md` - Line 26: RAG validation (>0.65 confidence)
- `PROJECT_CONSTRAINTS.md` - Line 31: PHI anonymization in logs
- `constraints/13-ralph-execution.md` - Ralph PRD formatting requirements

**Next Phase** (after Phase 0 complete):
- `planning/phase1-implementation-2026-02-09/` - 15-week implementation plan

---

## 📞 Approval Contacts

**Clinical Advisor** (PRD 1):
- Review: Clinical content, AMC rubric, scenarios
- SLA: 5 business days
- Deliverable: `clinical-advisor-review/CLINICAL_ADVISOR_REVIEW_PACKAGE.md`

**Security Team** (PRD 2):
- Review: Encryption, PHI anonymization, prompt injection protection
- SLA: 3 business days
- Deliverable: Test results (`pytest tests/test_security/ -v`)

**DBA** (PRD 3):
- Review: Migration, indexes, triggers, benchmarks
- SLA: 2 business days
- Deliverable: Benchmark results (`python scripts/benchmark_osce_queries.py`)

---

## 📈 Progress Tracking

**Update this table as PRDs complete:**

| PRD | Status | Deliverables | Approval | Date Complete |
|-----|--------|--------------|----------|---------------|
| PRD 1 - Clinical | 🔴 Not Started | 0/6 files | ⬜ Pending | - |
| PRD 2 - Security | 🔴 Not Started | 0/8 items (5 services + GDPR + 21 tests) | ⬜ Pending | - |
| PRD 3 - Database | 🔴 Not Started | 0/4 items (migration + benchmarks) | ⬜ Pending | - |

**Phase 0 Status:** 🔴 Not Started
**Start Date:** -
**Target Completion:** 10-15 days from start

---

## 🔍 Troubleshooting

### Issue: Ralph asks questions instead of executing

**Cause**: PRD missing AUTONOMOUS EXECUTION MODE header or using question-based language

**Fix**:
```bash
# Check PRD has correct header
head -5 planning/phase0-critical-fixes-2026-02-09/prds/PRD_PHASE0_WEEK01_CLINICAL_ACCURACY.md
# Should show: # AUTONOMOUS EXECUTION MODE - NO QUESTIONS

# Check for question-based language
grep -iE "(would you like|should i|do you want)" prds/*.md
# Should return 0 results in execution sections
```

### Issue: Approval gate skipped

**Cause**: PRD missing BLOCKING instruction or "When Complete" section

**Fix**:
```bash
# Verify each PRD has approval gate
grep -A5 "WHEN COMPLETE:" prds/*.md | grep -i blocking
# Should return 3 results (one per PRD)
```

### Issue: Tests failing in PRD 2

**Cause**: Vault not running or encryption key not generated

**Fix**:
```bash
# Start Vault
docker-compose up -d vault

# Verify Vault accessible
curl http://localhost:8200/v1/sys/health

# Generate encryption key
vault write secret/ai-osce/encryption-key value=$(openssl rand -base64 32)

# Re-run tests
pytest tests/test_security/ -v
```

### Issue: Benchmarks failing in PRD 3

**Cause**: Migration not applied or PostgreSQL not optimized

**Fix**:
```bash
# Verify migration applied
alembic current
# Should show: 20260209_phase0_week03_database_optimization (head)

# Verify indexes created
psql -d ai_osce -c "\d+ osce_attempts" | grep idx_attempts_
# Should show 5 indexes

# Re-run benchmarks
python scripts/benchmark_osce_queries.py
```

---

**Last Updated**: 2026-02-09
**Version**: 1.0
**Status**: Ready for Ralph Execution
