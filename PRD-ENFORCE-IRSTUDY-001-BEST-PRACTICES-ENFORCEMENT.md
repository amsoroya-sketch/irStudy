# PRD-ENFORCE-IRSTUDY-001: irStudy Best Practices Enforcement

**Project**: irStudy (Medical EMR + AI OSCE Platform)
**Priority**: P1 - HIGH (Complex dual-system architecture, stale development)
**Created**: 2026-07-01
**Standards**: T-RALPH V2.2 + Ponytail Integration (Ultra Mode)
**Estimated Duration**: 16-24 hours
**Status**: ✅ READY FOR RALPH EXECUTION

---

## 0 - DISCOVERY (Code Reuse Analysis)

**Purpose**: Identify existing implementations before creating new code

**Ponytail Principle**: Every line of code that doesn't need to exist saves tokens, time, and errors.

---

### 0.1 Discovery Commands

**CRITICAL - Read These Files FIRST**:
1. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
   - Section 2: Cross-System Implementation Workflow (EMR + AI OSCE)
   - Section 15: Medical Content Quality Gates (CRITICAL)
2. **.claude/CLAUDE.md**: `/home/dev/Development/irStudy/.claude/CLAUDE.md`
   - Already exists! (244 lines)
   - Review and enhance
3. **PONYTAIL_INTEGRATION.md**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/PONYTAIL_INTEGRATION.md`
4. **RALPH_GLOBAL_CONSTRAINTS.md**: `/home/dev/Development/ralph-dashboard/docs/specifications/prd-standards/RALPH_GLOBAL_CONSTRAINTS.md`

**Run these commands to audit the codebase:**

```bash
# Check existing .claude/CLAUDE.md structure
wc -l /home/dev/Development/irStudy/.claude/CLAUDE.md
# Result: 244 lines EXISTS (needs Ponytail section)

# Check PROJECT_CONSTRAINTS.md completeness
grep -c "^##" /home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md
# Result: 48 sections (needs Ponytail section)

# Check for existing pre-commit hooks
ls -la /home/dev/Development/irStudy/.git/hooks/pre-commit
# Result: Standard git hook (needs custom implementation)

# Check for existing CI/CD workflows
ls -la /home/dev/Development/irStudy/.github/workflows/
# Result: 2 workflows exist (security-scan.yml, security.yml)

# Check quality gate commands in constraints
grep -c "pytest\|pylint\|npx tsc" /home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md
# Result: 1 match (needs expansion to 5+ gates)

# Check existing PRDs
find /home/dev/Development/irStudy -name "PRD-*.md" -maxdepth 1
# Result: 1 PRD file (PRD-EMR-SESSIONS-API.md)

# Check last commit date
cd /home/dev/Development/irStudy && git log -1 --format="%cd" --date=short
# Result: 2026-05-28 (34 days ago - STALE)
```

---

### 0.2 Discovery Results

| Component/Feature | Exists? | Location | Lines | Action |
|-------------------|---------|----------|-------|--------|
| .claude/CLAUDE.md | ✅ YES | `.claude/CLAUDE.md` | 244 | UPDATE (add Ponytail) |
| PROJECT_CONSTRAINTS.md | ✅ YES | `PROJECT_CONSTRAINTS.md` | 799 | UPDATE (add Ponytail + expand quality gates) |
| GitHub Actions workflows | ✅ YES | `.github/workflows/` | 2 files | ENHANCE (add more workflows) |
| Pre-commit hook | ❌ NO | `.git/hooks/pre-commit` (standard) | - | CREATE |
| Quality gate scripts | ❌ NO | `scripts/` | - | CREATE |
| Ponytail section in constraints | ❌ NO | Not found | - | CREATE |
| Medical content validation | ✅ YES | Section 15 of constraints | - | REFERENCE |
| Ralph validation script | ❌ NO | `scripts/` | - | CREATE |

**Reuse Percentage**: 4/8 components exist (50% reuse opportunity)

---

### 0.3 Gap Analysis

**What EXISTS and can be REUSED:**
- ✅ .claude/CLAUDE.md: 244 lines (cross-system workflow documented) - UPDATE
- ✅ PROJECT_CONSTRAINTS.md: 799 lines (48 sections, medical quality gates) - UPDATE
- ✅ GitHub Actions: 2 workflows (security-scan.yml, security.yml) - ENHANCE
- ✅ Medical Content Quality Gates: Section 15 (13-gate QA, FRACP validation) - REFERENCE

**What NEEDS TO BE CREATED:**
- ❌ Ponytail section in PROJECT_CONSTRAINTS.md (~200 lines)
- ❌ Expanded quality gates section (~150 lines)
- ❌ Pre-commit hook for Python + TypeScript (~180 lines)
- ❌ Quality gate scripts (backend + frontend) (~300 lines)
- ❌ Ralph validation script (~150 lines)
- ❌ Additional CI/CD workflows (test-execution.yml, python-quality-gates.yml) (~200 lines)
- ❌ Ponytail section in .claude/CLAUDE.md (~100 lines)

**Net New Code**: ~1,280 lines
**Time Estimate**: 16-24 hours (dual-system complexity + needs restart from stale state)

---

### 0.4 Retroactive TDD Strategy

**For EXISTING code (4 components):**
1. **.claude/CLAUDE.md**: Add Ponytail section, validate structure
2. **PROJECT_CONSTRAINTS.md**: Add Ponytail + expand quality gates, validate with grep
3. **GitHub Actions workflows**: Enhance existing, test locally
4. **Medical Content Quality Gates**: Reference only (no changes)

**For NEW code (4 scripts + 2 workflows):**
1. **RED Phase**: Write validation tests → Expect tests to FAIL
2. **GREEN Phase**: Implement scripts/workflows → Expect tests to PASS
3. **REFACTOR Phase**: Improve → Maintain 100% pass rate

---

## T - TESTS

### Phase 1: Update .claude/CLAUDE.md with Ponytail (2 hours)

**Goal**: Add Ponytail section to existing .claude/CLAUDE.md

**TDD Workflow**: Retroactive TDD (file exists, adding new section)

**Test Code**:
```bash
# tests/validation/claude-md-ponytail-validation.sh
#!/bin/bash

echo "Testing .claude/CLAUDE.md Ponytail integration..."

# Test 1: File exists (should already pass)
test_file_exists() {
  if [ -f ".claude/CLAUDE.md" ]; then
    echo "✅ Test 1 PASS: .claude/CLAUDE.md exists"
    return 0
  else
    echo "❌ Test 1 FAIL: .claude/CLAUDE.md missing"
    return 1
  fi
}

# Test 2: Contains Ponytail section
test_ponytail_section() {
  if grep -q "## Ponytail Integration\|## Code Reuse Strategy" .claude/CLAUDE.md; then
    echo "✅ Test 2 PASS: Ponytail section present"
    return 0
  else
    echo "❌ Test 2 FAIL: Ponytail section missing"
    return 1
  fi
}

# Test 3: Contains Discovery commands
test_discovery_commands() {
  if grep -q "find.*name.*pattern\|grep -r" .claude/CLAUDE.md; then
    echo "✅ Test 3 PASS: Discovery commands documented"
    return 0
  else
    echo "❌ Test 3 FAIL: Discovery commands missing"
    return 1
  fi
}

# Test 4: Contains medical-specific patterns (irStudy-specific)
test_medical_patterns() {
  if grep -q "medical\|MCQ\|FRACP\|RAG" .claude/CLAUDE.md; then
    echo "✅ Test 4 PASS: Medical patterns documented"
    return 0
  else
    echo "❌ Test 4 FAIL: Medical patterns missing"
    return 1
  fi
}

# Run tests
test_file_exists && \
test_ponytail_section && \
test_discovery_commands && \
test_medical_patterns

if [ $? -eq 0 ]; then
  echo "🎉 All .claude/CLAUDE.md Ponytail tests PASSED (4/4)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (before update):
```bash
bash tests/validation/claude-md-ponytail-validation.sh
# Expected: 1/4 tests passing (file exists, but no Ponytail section)
```

**Validation** (after update):
```bash
bash tests/validation/claude-md-ponytail-validation.sh
# Expected: 4/4 tests passing ✅
```

---

### Phase 2: Update PROJECT_CONSTRAINTS.md with Ponytail + Quality Gates (3 hours)

**Goal**: Add Ponytail section and expand quality gates from 1 to 5+ commands

**TDD Workflow**: Retroactive TDD (file exists, adding/expanding sections)

**Test Code**:
```bash
# tests/validation/constraints-ponytail-validation.sh
#!/bin/bash

echo "Testing PROJECT_CONSTRAINTS.md Ponytail + Quality Gates..."

# Test 1: File exists (should already pass)
test_file_exists() {
  if [ -f "PROJECT_CONSTRAINTS.md" ]; then
    echo "✅ Test 1 PASS: PROJECT_CONSTRAINTS.md exists"
    return 0
  else
    echo "❌ Test 1 FAIL: PROJECT_CONSTRAINTS.md missing"
    return 1
  fi
}

# Test 2: Contains Ponytail section
test_ponytail_section() {
  if grep -q "## Ponytail\|## Code Reuse Strategy" PROJECT_CONSTRAINTS.md; then
    echo "✅ Test 2 PASS: Ponytail section present"
    return 0
  else
    echo "❌ Test 2 FAIL: Ponytail section missing"
    return 1
  fi
}

# Test 3: Contains 5+ quality gate commands
test_quality_gates() {
  gate_count=$(grep -c "pytest\|pylint\|npx tsc\|npm test\|npm run lint\|grep -r.*api_key" PROJECT_CONSTRAINTS.md)
  if [ "$gate_count" -ge 5 ]; then
    echo "✅ Test 3 PASS: $gate_count quality gate commands (≥5)"
    return 0
  else
    echo "❌ Test 3 FAIL: Only $gate_count quality gate commands (<5)"
    return 1
  fi
}

# Test 4: Contains backend quality gates (Python)
test_backend_gates() {
  if grep -q "pytest.*--cov" PROJECT_CONSTRAINTS.md && \
     grep -q "pylint" PROJECT_CONSTRAINTS.md; then
    echo "✅ Test 4 PASS: Backend (Python) quality gates present"
    return 0
  else
    echo "❌ Test 4 FAIL: Backend quality gates incomplete"
    return 1
  fi
}

# Test 5: Contains frontend quality gates (TypeScript)
test_frontend_gates() {
  if grep -q "npx tsc --noEmit" PROJECT_CONSTRAINTS.md && \
     grep -q "npm.*lint" PROJECT_CONSTRAINTS.md; then
    echo "✅ Test 5 PASS: Frontend (TypeScript) quality gates present"
    return 0
  else
    echo "❌ Test 5 FAIL: Frontend quality gates incomplete"
    return 1
  fi
}

# Test 6: Contains security scan commands
test_security_gates() {
  if grep -q "grep -r.*hardcoded\|grep -r.*api_key" PROJECT_CONSTRAINTS.md; then
    echo "✅ Test 6 PASS: Security scan commands present"
    return 0
  else
    echo "❌ Test 6 FAIL: Security scan commands missing"
    return 1
  fi
}

# Run tests
test_file_exists && \
test_ponytail_section && \
test_quality_gates && \
test_backend_gates && \
test_frontend_gates && \
test_security_gates

if [ $? -eq 0 ]; then
  echo "🎉 All PROJECT_CONSTRAINTS.md tests PASSED (6/6)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (before update):
```bash
bash tests/validation/constraints-ponytail-validation.sh
# Expected: 1/6 tests passing (file exists only)
```

**Validation** (after update):
```bash
bash tests/validation/constraints-ponytail-validation.sh
# Expected: 6/6 tests passing ✅
```

---

### Phase 3: Pre-Commit Hook (Python + TypeScript) (4 hours)

**Goal**: Create pre-commit hook for dual-language project

**TDD Workflow**: Standard TDD (custom hook doesn't exist)

**Test Code**:
```bash
# tests/validation/precommit-validation.sh
#!/bin/bash

echo "Testing git pre-commit hook for irStudy..."

# Test 1: Pre-commit hook exists and executable
test_hook_exists() {
  if [ -f ".git/hooks/pre-commit" ] && [ -x ".git/hooks/pre-commit" ]; then
    echo "✅ Test 1 PASS: pre-commit hook exists and is executable"
    return 0
  else
    echo "❌ Test 1 FAIL: pre-commit hook missing or not executable"
    return 1
  fi
}

# Test 2: Hook runs Python quality gates
test_python_gates() {
  if grep -q "pytest" .git/hooks/pre-commit && \
     grep -q "pylint" .git/hooks/pre-commit; then
    echo "✅ Test 2 PASS: Python quality gates present"
    return 0
  else
    echo "❌ Test 2 FAIL: Python quality gates missing"
    return 1
  fi
}

# Test 3: Hook runs TypeScript quality gates
test_typescript_gates() {
  if grep -q "npx tsc --noEmit" .git/hooks/pre-commit && \
     grep -q "npm.*lint" .git/hooks/pre-commit; then
    echo "✅ Test 3 PASS: TypeScript quality gates present"
    return 0
  else
    echo "❌ Test 3 FAIL: TypeScript quality gates missing"
    return 1
  fi
}

# Test 4: Hook scans for hardcoded secrets
test_security_scan() {
  if grep -q "grep.*api_key\|grep.*hardcoded" .git/hooks/pre-commit; then
    echo "✅ Test 4 PASS: Security scan present"
    return 0
  else
    echo "❌ Test 4 FAIL: Security scan missing"
    return 1
  fi
}

# Test 5: Hook validates medical content (irStudy-specific)
test_medical_validation() {
  if grep -q "validate_mcq_content\|placeholder" .git/hooks/pre-commit; then
    echo "✅ Test 5 PASS: Medical content validation present"
    return 0
  else
    echo "❌ Test 5 FAIL: Medical content validation missing"
    return 1
  fi
}

# Test 6: Hook exits on failure
test_exit_on_failure() {
  if grep -q "exit 1" .git/hooks/pre-commit; then
    echo "✅ Test 6 PASS: Hook exits on failures"
    return 0
  else
    echo "❌ Test 6 FAIL: Hook doesn't exit on failures"
    return 1
  fi
}

# Run tests
test_hook_exists && \
test_python_gates && \
test_typescript_gates && \
test_security_scan && \
test_medical_validation && \
test_exit_on_failure

if [ $? -eq 0 ]; then
  echo "🎉 All pre-commit hook tests PASSED (6/6)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (RED Phase):
```bash
bash tests/validation/precommit-validation.sh
# Expected: 0/6 tests passing ❌
```

**Validation** (GREEN Phase):
```bash
bash tests/validation/precommit-validation.sh
# Expected: 6/6 tests passing ✅
```

---

### Phase 4: CI/CD Enhancement (3 hours)

**Goal**: Add test-execution.yml and python-quality-gates.yml workflows

**TDD Workflow**: Standard TDD (workflows don't exist)

**Test Code**:
```bash
# tests/validation/cicd-validation.sh
#!/bin/bash

echo "Testing CI/CD workflows for irStudy..."

# Test 1: Workflows directory exists
test_workflows_dir() {
  if [ -d ".github/workflows" ]; then
    echo "✅ Test 1 PASS: .github/workflows directory exists"
    return 0
  else
    echo "❌ Test 1 FAIL: .github/workflows directory missing"
    return 1
  fi
}

# Test 2: Existing security workflows present (should already pass)
test_existing_workflows() {
  if [ -f ".github/workflows/security-scan.yml" ] && \
     [ -f ".github/workflows/security.yml" ]; then
    echo "✅ Test 2 PASS: Existing security workflows present"
    return 0
  else
    echo "❌ Test 2 FAIL: Existing workflows missing"
    return 1
  fi
}

# Test 3: New test-execution workflow exists
test_test_workflow() {
  if [ -f ".github/workflows/test-execution.yml" ]; then
    echo "✅ Test 3 PASS: test-execution.yml exists"
    return 0
  else
    echo "❌ Test 3 FAIL: test-execution.yml missing"
    return 1
  fi
}

# Test 4: New python-quality-gates workflow exists
test_python_workflow() {
  if [ -f ".github/workflows/python-quality-gates.yml" ]; then
    echo "✅ Test 4 PASS: python-quality-gates.yml exists"
    return 0
  else
    echo "❌ Test 4 FAIL: python-quality-gates.yml missing"
    return 1
  fi
}

# Test 5: Test workflow runs pytest
test_pytest_execution() {
  if grep -q "pytest --cov" .github/workflows/test-execution.yml; then
    echo "✅ Test 5 PASS: Test workflow runs pytest with coverage"
    return 0
  else
    echo "❌ Test 5 FAIL: pytest not configured in test workflow"
    return 1
  fi
}

# Test 6: Python workflow runs pylint
test_pylint_execution() {
  if grep -q "pylint" .github/workflows/python-quality-gates.yml; then
    echo "✅ Test 6 PASS: Python workflow runs pylint"
    return 0
  else
    echo "❌ Test 6 FAIL: pylint not configured"
    return 1
  fi
}

# Run tests
test_workflows_dir && \
test_existing_workflows && \
test_test_workflow && \
test_python_workflow && \
test_pytest_execution && \
test_pylint_execution

if [ $? -eq 0 ]; then
  echo "🎉 All CI/CD tests PASSED (6/6)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (RED Phase):
```bash
bash tests/validation/cicd-validation.sh
# Expected: 2/6 tests passing (existing workflows only)
```

**Validation** (GREEN Phase):
```bash
bash tests/validation/cicd-validation.sh
# Expected: 6/6 tests passing ✅
```

---

### Phase 5: Ralph Validation Script (2 hours)

**Goal**: Create irStudy-specific validation script (medical content validation)

**TDD Workflow**: Standard TDD (script doesn't exist)

**Test Code**:
```bash
# tests/validation/ralph-validation-test.sh
#!/bin/bash

echo "Testing Ralph validation script for irStudy..."

# Test 1: Validation script exists
test_script_exists() {
  if [ -f "scripts/validate-project-ready.sh" ] && [ -x "scripts/validate-project-ready.sh" ]; then
    echo "✅ Test 1 PASS: validate-project-ready.sh exists and is executable"
    return 0
  else
    echo "❌ Test 1 FAIL: validate-project-ready.sh missing or not executable"
    return 1
  fi
}

# Test 2: Script checks PROJECT_CONSTRAINTS.md
test_constraints_check() {
  if grep -q "PROJECT_CONSTRAINTS.md" scripts/validate-project-ready.sh; then
    echo "✅ Test 2 PASS: Script checks PROJECT_CONSTRAINTS.md"
    return 0
  else
    echo "❌ Test 2 FAIL: Script doesn't check PROJECT_CONSTRAINTS.md"
    return 1
  fi
}

# Test 3: Script checks medical content validation (irStudy-specific)
test_medical_validation() {
  if grep -q "validate_mcq_content\|Section 15\|medical.*quality" scripts/validate-project-ready.sh; then
    echo "✅ Test 3 PASS: Script validates medical content requirements"
    return 0
  else
    echo "❌ Test 3 FAIL: Medical content validation missing"
    return 1
  fi
}

# Test 4: Script validates cross-system workflow (EMR + AI OSCE)
test_cross_system() {
  if grep -q "EMR\|OSCE\|cross-system\|dual-system" scripts/validate-project-ready.sh; then
    echo "✅ Test 4 PASS: Script validates cross-system workflow"
    return 0
  else
    echo "❌ Test 4 FAIL: Cross-system validation missing"
    return 1
  fi
}

# Test 5: Script checks both backend and frontend quality gates
test_dual_stack() {
  if grep -q "pytest" scripts/validate-project-ready.sh && \
     grep -q "npx tsc\|npm test" scripts/validate-project-ready.sh; then
    echo "✅ Test 5 PASS: Script validates both Python and TypeScript"
    return 0
  else
    echo "❌ Test 5 FAIL: Dual-stack validation incomplete"
    return 1
  fi
}

# Run tests
test_script_exists && \
test_constraints_check && \
test_medical_validation && \
test_cross_system && \
test_dual_stack

if [ $? -eq 0 ]; then
  echo "🎉 All Ralph validation tests PASSED (5/5)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (RED Phase):
```bash
bash tests/validation/ralph-validation-test.sh
# Expected: 0/5 tests passing ❌
```

**Validation** (GREEN Phase):
```bash
bash tests/validation/ralph-validation-test.sh
# Expected: 5/5 tests passing ✅
```

---

### Phase 6: Update PRD-EMR-SESSIONS-API.md with Ponytail (2 hours)

**Goal**: Update existing PRD with Section 0 (Discovery) and Ponytail Ultra directives

**TDD Workflow**: Retroactive TDD (PRD exists, adding Section 0)

**Test Code**:
```bash
# tests/validation/prd-ponytail-validation.sh
#!/bin/bash

echo "Testing PRD-EMR-SESSIONS-API.md Ponytail compliance..."

PRD_FILE="PRD-EMR-SESSIONS-API.md"

# Test 1: PRD exists
test_prd_exists() {
  if [ -f "$PRD_FILE" ]; then
    echo "✅ Test 1 PASS: $PRD_FILE exists"
    return 0
  else
    echo "❌ Test 1 FAIL: $PRD_FILE missing"
    return 1
  fi
}

# Test 2: PRD has Section 0 (Discovery)
test_section_0() {
  if grep -q "^## 0 - DISCOVERY" "$PRD_FILE"; then
    echo "✅ Test 2 PASS: Section 0 (Discovery) present"
    return 0
  else
    echo "❌ Test 2 FAIL: Section 0 (Discovery) missing"
    return 1
  fi
}

# Test 3: PRD contains Ponytail Principle
test_ponytail_principle() {
  if grep -q "Ponytail Principle" "$PRD_FILE"; then
    echo "✅ Test 3 PASS: Ponytail Principle stated"
    return 0
  else
    echo "❌ Test 3 FAIL: Ponytail Principle missing"
    return 1
  fi
}

# Test 4: PRD has discovery commands
test_discovery_commands() {
  if grep -q "```bash" "$PRD_FILE" && \
     grep -q "find.*name\|grep -r" "$PRD_FILE"; then
    echo "✅ Test 4 PASS: Discovery commands present"
    return 0
  else
    echo "❌ Test 4 FAIL: Discovery commands missing"
    return 1
  fi
}

# Test 5: PRD has reuse percentage
test_reuse_percentage() {
  if grep -q "Reuse Percentage\|reuse opportunity" "$PRD_FILE"; then
    echo "✅ Test 5 PASS: Reuse percentage calculated"
    return 0
  else
    echo "❌ Test 5 FAIL: Reuse percentage missing"
    return 1
  fi
}

# Run tests
test_prd_exists && \
test_section_0 && \
test_ponytail_principle && \
test_discovery_commands && \
test_reuse_percentage

if [ $? -eq 0 ]; then
  echo "🎉 All PRD Ponytail tests PASSED (5/5)"
  exit 0
else
  echo "❌ Some tests FAILED"
  exit 1
fi
```

**Validation** (before update):
```bash
bash tests/validation/prd-ponytail-validation.sh
# Expected: 1/5 tests passing (PRD exists only)
```

**Validation** (after update):
```bash
bash tests/validation/prd-ponytail-validation.sh
# Expected: 5/5 tests passing ✅
```

---

### Test Summary

**Total Tests**: 28 tests across 6 phases
- Phase 1: 4 tests (.claude/CLAUDE.md Ponytail)
- Phase 2: 6 tests (PROJECT_CONSTRAINTS.md)
- Phase 3: 6 tests (Pre-commit hook)
- Phase 4: 6 tests (CI/CD workflows)
- Phase 5: 5 tests (Ralph validation)
- Phase 6: 5 tests (PRD update)

**Expected Pass Rate**: 100% (28/28 tests passing after implementation)

---

## R - REQUEST

### Business Context

irStudy is a **dual-system medical platform** (EMR + AI OSCE) with critical medical content quality requirements. The project is currently **stale** (34 days since last commit) and needs:
1. Restart from stale state
2. Best practices enforcement (Ponytail integration)
3. Enhanced quality gates (1 → 5+ commands)
4. Medical content validation enforcement

**Current State (CRITICAL GAPS)**:
- ✅ Has .claude/CLAUDE.md (244 lines) - GOOD
- ✅ Has PROJECT_CONSTRAINTS.md (799 lines) - GOOD
- ❌ No Ponytail integration (missing code reuse strategy)
- ❌ Only 1 quality gate command (needs 5+ for dual-stack)
- ❌ No pre-commit hook (manual enforcement only)
- ⚠️ Only 1 PRD file (low coverage for dual-system project)
- 🚨 **STALE**: 34 days since last commit

**Impact**:
- Medical content quality may degrade (no automated validation)
- Dual-system coordination issues (EMR + AI OSCE conflicts)
- Low PRD coverage (1 PRD for 2 complex systems)
- No automated code reuse checking

### User Story

**As a** medical platform development team
**I want** comprehensive best practices enforcement with medical content validation
**So that** both EMR and AI OSCE systems maintain high quality and comply with medical standards

**Acceptance Criteria**:
1. ✅ .claude/CLAUDE.md updated with Ponytail section
2. ✅ PROJECT_CONSTRAINTS.md has Ponytail section + 5+ quality gates
3. ✅ Pre-commit hook validates Python + TypeScript + medical content
4. ✅ CI/CD workflows enhanced (4 total workflows)
5. ✅ Ralph validation script includes medical content checks
6. ✅ PRD-EMR-SESSIONS-API.md updated with Section 0 (Discovery)
7. ✅ 100% test pass rate (28/28 validation tests)
8. ✅ Development restarted (new commits after enforcement)

---

## A - ARCHITECTURE

### System Components

```
irStudy/
├── .claude/
│   └── CLAUDE.md                           ← UPDATE: Add Ponytail section
├── .github/
│   └── workflows/                          ← ENHANCE: Add 2 new workflows
│       ├── security-scan.yml               (existing)
│       ├── security.yml                    (existing)
│       ├── test-execution.yml              (NEW)
│       └── python-quality-gates.yml        (NEW)
├── .git/
│   └── hooks/
│       └── pre-commit                      ← CREATE: Dual-language + medical validation
├── scripts/
│   ├── validate-project-ready.sh           ← CREATE: irStudy-specific validation
│   └── quality-gates.sh                    ← CREATE: Backend + frontend gates
├── tests/
│   └── validation/                         ← CREATE: 6 validation scripts
│       ├── claude-md-ponytail-validation.sh
│       ├── constraints-ponytail-validation.sh
│       ├── precommit-validation.sh
│       ├── cicd-validation.sh
│       ├── ralph-validation-test.sh
│       └── prd-ponytail-validation.sh
├── backend/                                ← REFERENCE: Python/FastAPI (114 files)
├── frontend/                               ← REFERENCE: TypeScript/React (141 files)
├── PROJECT_CONSTRAINTS.md                  ← UPDATE: Add Ponytail + expand quality gates
└── PRD-EMR-SESSIONS-API.md                 ← UPDATE: Add Section 0 (Discovery)
```

### Technology Stack

**Existing** (from PROJECT_CONSTRAINTS.md):
- Backend: Python/FastAPI, PostgreSQL, Redis, Rust FFI
- Frontend: TypeScript/React (Vite), Node.js
- Testing: Playwright (E2E), Pytest (backend), Jest/Vitest (frontend)

**Medical-Specific**:
- RAG System: Qdrant vector DB, embedding models
- Content Generation: Claude API (not local LLMs - prevents 64.8% placeholders)
- Validation: 13-gate QA + FRACP clinical validation (≥8.0/10 score)

### Integration Points

**1. Dual-System Coordination (EMR + AI OSCE)**
- Shared infrastructure FIRST (Vault, Redis, security tests)
- Sequential implementation (prevent namespace collisions)
- Cross-system E2E tests (final validation)

**2. Medical Content Quality Gates (Section 15 - CRITICAL)**
- Zero-tolerance placeholder detection (15 regex patterns)
- RAG citation requirements (≥3 citations per MCQ, >0.70 confidence)
- Claude API mandatory (not local LLMs)
- FRACP clinical validation (≥8.0/10 score)

**3. Ponytail Integration**
- All new PRDs must include Section 0 (Discovery)
- Retroactive TDD for existing code
- Standard TDD for new code only

---

## L - LOOP

### Loop Execution Strategy

**CRITICAL**: This PRD implements a 6-phase sequential development workflow with TDD enforcement.

**Phase Execution Order:**
1. Phase 1: Update .claude/CLAUDE.md with Ponytail (2 hours)
2. Phase 2: Update PROJECT_CONSTRAINTS.md with Ponytail + Quality Gates (3 hours)
3. Phase 3: Pre-Commit Hook (Python + TypeScript + Medical) (4 hours)
4. Phase 4: CI/CD Enhancement (3 hours)
5. Phase 5: Ralph Validation Script (2 hours)
6. Phase 6: Update PRD-EMR-SESSIONS-API.md with Ponytail (2 hours)

**Sequential Execution Requirements:**
- Each phase MUST complete with 100% test pass rate before next phase
- No parallel execution (each phase builds on previous)
- If tests fail: FIX immediately, do NOT proceed

**Phase Dependency Chain:**
```
Phase 1 (.claude/CLAUDE.md Ponytail)
    ↓ (provides: Ponytail patterns for PROJECT_CONSTRAINTS.md)
Phase 2 (PROJECT_CONSTRAINTS.md update)
    ↓ (provides: Quality gate commands for pre-commit hook)
Phase 3 (Pre-Commit Hook)
    ↓ (provides: Local enforcement pattern for CI/CD)
Phase 4 (CI/CD Enhancement)
    ↓ (provides: Automated workflows referenced in Ralph validation)
Phase 5 (Ralph Validation Script)
    ↓ (provides: Validation logic used in PRD update)
Phase 6 (Update PRD-EMR-SESSIONS-API.md)
    ↓
COMPLETE (28/28 tests passing, all quality gates functional)
```

**Blocking Conditions:**
- Python errors (pytest failures, pylint <9.0/10) → STOP
- TypeScript errors (compilation, linting) → STOP
- Medical content validation failures → STOP
- Security violations (hardcoded secrets) → STOP

**Recovery Protocol:**
If blocked:
1. Review error message carefully
2. Check PROJECT_CONSTRAINTS.md Section 15 (Medical Quality Gates)
3. Check .claude/CLAUDE.md for dual-system patterns
4. Fix issue
5. Re-run tests → Must pass before proceeding

---

(Implementation details for each phase would follow the same pattern as PRD-ENFORCE-RALPH-001, adapted for irStudy's dual-language stack and medical content requirements)

---

## P - PLAN

### Execution Summary

**Total Duration**: 16-24 hours
- Phase 1: Update .claude/CLAUDE.md (2 hours)
- Phase 2: Update PROJECT_CONSTRAINTS.md (3 hours)
- Phase 3: Pre-Commit Hook (4 hours) - Complex due to dual-language + medical validation
- Phase 4: CI/CD Enhancement (3 hours)
- Phase 5: Ralph Validation Script (2 hours)
- Phase 6: Update PRD (2 hours)

**Complexity Factors**:
- Dual-language stack (Python + TypeScript) - 4 extra hours
- Medical content validation - 2 extra hours
- Cross-system coordination (EMR + OSCE) - 2 extra hours
- Stale state restart - 2 extra hours

**Deliverables**:
1. ✅ Updated .claude/CLAUDE.md (+100 lines Ponytail section)
2. ✅ Updated PROJECT_CONSTRAINTS.md (+350 lines: Ponytail + quality gates)
3. ✅ Pre-commit hook (Python + TypeScript + Medical) (~180 lines)
4. ✅ 2 new CI/CD workflows (~200 lines)
5. ✅ Ralph validation script (~150 lines)
6. ✅ Updated PRD-EMR-SESSIONS-API.md (Section 0 added)
7. ✅ 6 validation test scripts (28 tests total)

---

## H - HANDOFF

### Completion Criteria

**All phases complete when:**
- [ ] .claude/CLAUDE.md has Ponytail section (4/4 tests passing)
- [ ] PROJECT_CONSTRAINTS.md has Ponytail + 5+ quality gates (6/6 tests passing)
- [ ] Pre-commit hook validates Python + TypeScript + Medical (6/6 tests passing)
- [ ] 4 CI/CD workflows functional (6/6 tests passing)
- [ ] Ralph validation script with medical checks (5/5 tests passing)
- [ ] PRD-EMR-SESSIONS-API.md has Section 0 (5/5 tests passing)
- [ ] All 28 validation tests passing (100% pass rate)
- [ ] Development restarted (new commits after enforcement)

### Ponytail Compliance

**Code Reuse Statistics**:
- Components reused: 4/8 (50%)
  - ✅ .claude/CLAUDE.md (244 lines - enhanced)
  - ✅ PROJECT_CONSTRAINTS.md (799 lines - enhanced)
  - ✅ GitHub Actions workflows (2 existing - enhanced)
  - ✅ Medical Content Quality Gates (Section 15 - referenced)
- Components created: 4/8 (50%)
  - ❌ Pre-commit hook (~180 lines)
  - ❌ Quality gate scripts (~300 lines)
  - ❌ Ralph validation script (~150 lines)
  - ❌ Validation test scripts (~400 lines)

**Total New Code**: ~1,030 lines
**Total Enhanced Code**: ~1,143 lines (existing files updated)
**Reuse Ratio**: 52.6% enhanced existing, 47.4% new infrastructure

### Next Steps

**After this PRD completes:**
1. Create more PRDs for dual-system implementation (currently only 1 PRD)
2. Apply enforcement to skillbridge-desktop-app (PRD-ENFORCE-SKILLBRIDGE-001)
3. Apply enforcement to moneySmart-v2 (PRD-ENFORCE-MONEYSMART-001)
4. Restart active development (address 34-day staleness)

---

**END OF PRD-ENFORCE-IRSTUDY-001**

**Status**: ✅ READY FOR RALPH EXECUTION
**Ponytail Mode**: Ultra (Aggressive code reuse)
**Estimated Completion**: 16-24 hours
**Dependencies**: PRD-ENFORCE-RALPH-001 (foundation documentation)
