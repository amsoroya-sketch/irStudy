# PRD QA Validation Addendum - Study Cards Pipeline

**Document ID**: PRD-QA-ADDENDUM-STUDY-CARDS
**Applies To**: PRD-P1-005, PRD-P1-006, PRD-P1-007, PRD-P8-002
**Priority**: P0-Critical (MUST be followed)
**Status**: Mandatory Quality Gate
**Created**: 2026-03-24

---

## Purpose

This addendum adds **mandatory QA validation gates** to all Study Cards Pipeline PRDs. These gates ensure:
1. **Expert agents** are used correctly (no general-purpose agents)
2. **QA validation** happens BEFORE work is accepted (not after)
3. **testing-qa-expert** reviews all code before completion
4. **PM validation checkpoints** enforce quality at every phase

**Rationale**: Based on CLAUDE.md Agent OS workflow requirements - prevent systematic mistakes by validating early and often.

---

## Mandatory Agent Delegation Workflow

**ALL PRDs MUST follow this workflow:**

```
┌─────────────────────────────────────────────────────────────────┐
│ Phase Start: PM Reads PRD + Constraints                        │
│ ↓                                                               │
│ Step 1: PM Delegates to Expert Agent                           │
│   - Specify: Agent type (react-frontend-developer, etc.)       │
│   - Include: Explicit constraints from CLAUDE.md               │
│   - Provide: Validation checklist agent must complete          │
│   - Set: Success criteria (0 errors, specific targets)         │
│ ↓                                                               │
│ Step 2: Agent Self-Validates Work                              │
│   - Run: All validation commands (tsc, pytest, lint)           │
│   - Check: Validation checklist (mark each item ✓)             │
│   - Confirm: 0 compilation errors, 0 test failures             │
│   - Report: Results back to PM                                 │
│ ↓                                                               │
│ Step 3: PM Validation Checkpoint (BLOCKS next phase)           │
│   - Review: Agent's validation report                          │
│   - Run: Independent validation (don't trust blindly)          │
│   - Check: Code quality, test coverage, performance            │
│   - Decision: PASS → next phase, FAIL → delegate fix           │
│ ↓                                                               │
│ Step 4: testing-qa-expert Review (MANDATORY before complete)   │
│   - Run: Full test suite (unit + integration + E2E)            │
│   - Check: Test coverage ≥80%                                  │
│   - Validate: Performance benchmarks met                       │
│   - Security: Scan for hardcoded credentials, SQL injection    │
│   - Decision: PASS → mark phase complete, FAIL → delegate fix  │
│ ↓                                                               │
│ Phase Complete: PM marks phase as DONE                         │
└─────────────────────────────────────────────────────────────────┘

CRITICAL: If ANY step fails → DO NOT proceed to next phase
```

---

## QA Validation Gates (Added to Each PRD)

### PRD-P1-005: Auto Study Card Generation

**LOOP Section - Add QA Gates**:

#### Phase 1: Database Migration + Core Generator (4 hours)
**Agent**: `python-backend-developer`

**Deliverables**:
- Alembic migration + StudyCardGenerator class

**❌ OLD: Phase complete when code written**
**✅ NEW: Phase complete when QA validated**

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Agent MUST run these commands before returning:
cd /home/dev/Development/irStudy/backend

# 1. Run migration
alembic upgrade head
# Expected: ✓ Migration successful

# 2. Run tests
pytest tests/test_ai/test_study_card_generator.py -v
# Expected: ✓ 5/5 tests passed

# 3. Check for hardcoded credentials
grep -r "sk-ant-\|ANTHROPIC_API_KEY.*=" src/ai/study_card_generator.py
# Expected: ✓ 0 matches (using Vault)

# 4. Verify Australian terminology
grep -i "acetaminophen\|mg/dL\|911" src/ai/study_card_generator.py
# Expected: ✓ 0 matches (using Australian standards)
```

**QA Gate 2 (PM Validation)**:
```bash
# PM independently verifies:
pytest tests/test_ai/test_study_card_generator.py --cov=src.ai.study_card_generator --cov-report=term
# Expected: ✓ Coverage ≥85%

# PM checks code quality:
pylint src/ai/study_card_generator.py
# Expected: ✓ Score ≥8.0/10
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA expert runs comprehensive checks:

# 1. Full test suite
pytest tests/ -v
# Expected: ✓ 100% pass rate

# 2. Security scan
bandit -r src/ai/study_card_generator.py
# Expected: ✓ 0 high/medium severity issues

# 3. Performance test (mock Claude/Qdrant for speed)
pytest tests/test_ai/test_study_card_generator.py --durations=10
# Expected: ✓ All tests <1s

# 4. Integration smoke test
python -c "from src.ai.study_card_generator import StudyCardGenerator; assert StudyCardGenerator"
# Expected: ✓ No import errors
```

**ONLY proceed to Phase 2 if ALL 3 QA gates pass**

---

#### Phase 2: RAG Integration (3 hours)
**Agent**: `python-backend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Qdrant integration tests
pytest tests/test_ai/test_study_card_generator.py::test_query_rag_citations -v
# Expected: ✓ Test passed

# Citation validation
pytest tests/test_ai/test_study_card_generator.py::test_validate_citations -v
# Expected: ✓ Filters confidence <0.65

# Mock Qdrant unavailable
pytest tests/test_ai/test_study_card_generator.py::test_rag_failure_graceful -v
# Expected: ✓ Graceful degradation (no crash)
```

**QA Gate 2 (PM Validation)**:
```bash
# PM verifies RAG quality
pytest tests/test_ai/ -k "rag" -v
# Expected: ✓ All RAG tests pass

# PM checks citation structure
python scripts/test_qdrant_integration.py
# Expected: ✓ All citations have qdrant_point_id
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA verifies RAG integration
pytest tests/test_ai/ --cov=src.ai.study_card_generator --cov-report=html
# Expected: ✓ RAG code paths covered

# QA checks error handling
pytest tests/test_ai/test_study_card_generator.py -k "error" -v
# Expected: ✓ All error scenarios handled
```

---

#### Phase 3: Q&A Generation + API Endpoint (3 hours)
**Agents**: `python-backend-developer` + `security-compliance-expert`

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Backend developer tests
pytest tests/test_api/test_study_card_auto_generation.py -v
# Expected: ✓ 5/5 integration tests passed

# Security expert scans
grep -r "sk-ant-\|hardcoded\|password.*=" src/api/v1/study_cards.py
# Expected: ✓ 0 matches
```

**QA Gate 2 (PM Validation)**:
```bash
# PM tests API endpoint
curl -X POST http://localhost:8001/api/v1/study-cards/generate-from-osce \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"attempt_id": "test-123"}'
# Expected: ✓ 201 Created, 3-5 cards returned

# PM tests idempotency
# (Call endpoint twice, verify same card IDs)
# Expected: ✓ Same cards returned, no duplicates
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs full integration suite
pytest tests/test_api/test_study_card_auto_generation.py --verbose --tb=short
# Expected: ✓ 5/5 tests passed

# QA tests security
pytest tests/test_api/test_study_card_auto_generation.py::test_unauthorized -v
# Expected: ✓ 403 error for other user's session

# QA validates Australian terminology
pytest tests/test_content/test_australian_standards.py -k "study_cards" -v
# Expected: ✓ All cards use Australian terms
```

---

#### Phase 4: Final QA + Documentation (2 hours)
**Agent**: `testing-qa-expert` (MANDATORY FINAL GATE)

**Comprehensive QA Checklist**:
```bash
# ✓ 1. All unit tests passing
pytest tests/test_ai/test_study_card_generator.py -v
# Expected: 12/12 tests passed

# ✓ 2. All integration tests passing
pytest tests/test_api/test_study_card_auto_generation.py -v
# Expected: 5/5 tests passed

# ✓ 3. Test coverage ≥85%
pytest tests/ --cov=src.ai.study_card_generator --cov=src.api.v1.study_cards --cov-report=term
# Expected: Coverage ≥85%

# ✓ 4. Performance benchmark
time curl -X POST http://localhost:8001/api/v1/study-cards/generate-from-osce \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"attempt_id": "test-123"}'
# Expected: <8 seconds

# ✓ 5. Security scan (zero tolerance)
bandit -r src/api/v1/study_cards.py src/ai/study_card_generator.py
# Expected: 0 high/medium issues

grep -r "sk-ant-\|ANTHROPIC_API_KEY.*=\|password.*=\|hardcoded" src/
# Expected: 0 matches

# ✓ 6. Database migration rollback test
alembic downgrade -1
alembic upgrade head
# Expected: Both succeed without errors

# ✓ 7. Australian medical standards validation
pytest tests/test_content/test_australian_standards.py -v
# Expected: All tests pass (paracetamol, eTG, SI units)

# ✓ 8. RAG citation quality
python scripts/validate_rag_citations.py
# Expected: All citations confidence ≥0.65, NO "Unknown" titles

# ✓ 9. Idempotency test
python scripts/test_idempotency.py
# Expected: Same card IDs returned on repeat calls

# ✓ 10. Error handling test
pytest tests/test_api/test_study_card_auto_generation.py::test_generate_from_osce_no_score_error -v
pytest tests/test_api/test_study_card_auto_generation.py::test_generate_from_osce_unauthorized -v
# Expected: Both pass (400 and 403 errors correctly handled)
```

**ONLY mark PRD-P1-005 COMPLETE if all 10 checks pass**

---

### PRD-P1-006: Flashcard Review Interface

**LOOP Section - Add QA Gates**:

#### Phase 1: Basic Component Structure (2 hours)
**Agent**: `react-frontend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/frontend

# TypeScript compilation
npx tsc --noEmit
# Expected: ✓ 0 errors

# Basic component tests
npm test -- FlashcardView.test.tsx
# Expected: ✓ 5/5 basic tests passed

# Lint
npm run lint
# Expected: ✓ 0 errors
```

**QA Gate 2 (PM Validation)**:
```bash
# PM verifies component renders
npm run dev
# Navigate to /study-cards/review
# Expected: ✓ Component loads without errors

# PM checks TypeScript interfaces
grep -A 10 "interface FlashcardViewProps" src/components/study-cards/FlashcardView.tsx
# Expected: ✓ All props properly typed
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs test suite
npm test -- FlashcardView.test.tsx --coverage
# Expected: ✓ Coverage ≥80%

# QA checks accessibility basics
npm test -- FlashcardView.test.tsx -t "accessibility"
# Expected: ✓ Basic a11y tests pass
```

---

#### Phase 2: Flip Animation (2 hours)
**Agent**: `react-frontend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Animation tests
npm test -- FlashcardCard.test.tsx
# Expected: ✓ 8/8 animation tests passed

# Performance check (Chrome DevTools)
npm run dev
# Open DevTools > Performance
# Record flip animation 5 times
# Expected: ✓ 60fps maintained (no red bars)
```

**QA Gate 2 (PM Validation)**:
```bash
# PM verifies animation smoothness
npm run dev
# Navigate to /study-cards/review, flip card
# Expected: ✓ Smooth 0.6s flip, no janky motion

# PM checks CSS implementation
grep "transform.*rotateY" src/components/study-cards/FlashcardCard.tsx
# Expected: ✓ GPU-accelerated transform used
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs performance tests
npm test -- FlashcardCard.test.tsx -t "performance"
# Expected: ✓ Flip completes in 0.6s ± 0.05s

# QA checks for layout shift
npm run lighthouse -- --url=http://localhost:5173/study-cards/review
# Expected: ✓ CLS (Cumulative Layout Shift) = 0
```

---

#### Phase 3: Accessibility + Citations (1.5 hours)
**Agent**: `react-frontend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Accessibility tests
npm test -- FlashcardView.test.tsx -t "accessibility"
# Expected: ✓ 7/7 accessibility tests passed

# Keyboard navigation test
npm test -- FlashcardView.test.tsx -t "keyboard"
# Expected: ✓ Spacebar, arrows work
```

**QA Gate 2 (PM Validation)**:
```bash
# PM tests with axe-core
npm test -- FlashcardView.test.tsx -t "passes axe-core"
# Expected: ✓ 0 accessibility violations

# PM checks ARIA labels
grep -r "aria-label" src/components/study-cards/
# Expected: ✓ All buttons have labels
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs full accessibility audit
npm run lighthouse -- --only-categories=accessibility
# Expected: ✓ Score ≥95

# QA tests screen reader (manual)
# Use VoiceOver/NVDA to navigate flashcards
# Expected: ✓ All actions announced correctly

# QA tests color contrast
npm test -- FlashcardView.test.tsx -t "color contrast"
# Expected: ✓ All text ≥4.5:1 contrast ratio

# QA tests keyboard-only navigation
# Navigate entire interface without mouse
# Expected: ✓ All features accessible via keyboard
```

---

#### Phase 4: Final QA (0.5 hours)
**Agent**: `testing-qa-expert`

**Comprehensive QA Checklist**:
```bash
# ✓ 1. All component tests passing
npm test -- FlashcardView.test.tsx FlashcardCard.test.tsx FlashcardCitations.test.tsx
# Expected: 20/20 tests passed

# ✓ 2. TypeScript compilation
npx tsc --noEmit
# Expected: 0 errors

# ✓ 3. Build success
npm run build
# Expected: Build completes successfully

# ✓ 4. Lint
npm run lint
# Expected: 0 errors

# ✓ 5. Lighthouse audit
npm run lighthouse -- --url=http://localhost:5173/study-cards/review
# Expected: Accessibility ≥95, Performance ≥90

# ✓ 6. Visual regression test (optional but recommended)
npm run test:visual
# Expected: No unexpected visual changes

# ✓ 7. Cross-browser test (Playwright)
npx playwright test tests/e2e/flashcard-view.spec.ts --project=chromium --project=firefox
# Expected: Tests pass in both browsers

# ✓ 8. Mobile responsive test
npx playwright test tests/e2e/flashcard-view.spec.ts --project=mobile-chrome
# Expected: Touch gestures work, UI fits screen
```

**ONLY mark PRD-P1-006 COMPLETE if all 8 checks pass**

---

### PRD-P1-007: SM-2 Review Logic

**LOOP Section - Add QA Gates**:

#### Phase 1: SM-2 Algorithm Implementation (2 hours)
**Agent**: `react-frontend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/frontend

# Algorithm accuracy tests
npm test -- useSpacedRepetition.test.ts
# Expected: ✓ 15/15 tests passed (all quality values 0-5)

# Edge case tests
npm test -- useSpacedRepetition.test.ts -t "edge"
# Expected: ✓ Handles negative quality, decimal, null
```

**QA Gate 2 (PM Validation)**:
```bash
# PM verifies algorithm matches SuperMemo-2 spec
# Compare with reference implementation
python scripts/validate_sm2_algorithm.py
# Expected: ✓ Frontend matches reference within 0.01
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs algorithm validation suite
npm test -- useSpacedRepetition.test.ts --verbose
# Expected: ✓ 15/15 tests passed

# QA verifies ease factor floor
npm test -- useSpacedRepetition.test.ts -t "ease factor never drops below 1.3"
# Expected: ✓ Test passes after 100 iterations
```

---

#### Phase 2: Quality Rating UI (2 hours)
**Agent**: `react-frontend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
# Component tests
npm test -- QualityRating.test.tsx
# Expected: ✓ 5/5 tests passed

# Keyboard shortcuts test
npm test -- QualityRating.test.tsx -t "keyboard"
# Expected: ✓ 0-5 keys work
```

**QA Gate 2 (PM Validation)**:
```bash
# PM tests UI manually
npm run dev
# Navigate to review, flip card, check quality buttons
# Expected: ✓ 6 buttons appear, labeled correctly
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA verifies accessibility
npm test -- QualityRating.test.tsx -t "accessibility"
# Expected: ✓ All buttons have ARIA labels

# QA tests visual design
npm run storybook
# Navigate to QualityRating story
# Expected: ✓ Buttons clearly distinguishable, good UX
```

---

#### Phase 3: Backend API Integration (1.5 hours)
**Agent**: `python-backend-developer`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/backend

# API integration tests
pytest tests/test_api/test_study_cards_review.py -v
# Expected: ✓ 5/5 tests passed

# Algorithm consistency test
python scripts/test_sm2_consistency.py
# Expected: ✓ Frontend == Backend (within 0.01)
```

**QA Gate 2 (PM Validation)**:
```bash
# PM tests API endpoint
curl -X PUT http://localhost:8001/api/v1/study-cards/test-123/review \
  -H "Authorization: Bearer $TEST_TOKEN" \
  -d '{"quality": 4}'
# Expected: ✓ 200 OK, SM-2 params updated

# PM verifies database update
psql -d irstudy_medical -c "SELECT ease_factor, interval_days, repetitions FROM study_cards WHERE card_id = 'test-123';"
# Expected: ✓ Values updated correctly
```

**QA Gate 3 (testing-qa-expert Review)**:
```bash
# QA runs full test suite
pytest tests/test_api/test_study_cards_review.py --verbose --tb=short
# Expected: ✓ 5/5 tests passed

# QA tests ownership validation
pytest tests/test_api/test_study_cards_review.py::test_review_card_ownership -v
# Expected: ✓ 403 error for other user's card

# QA validates quality range
pytest tests/test_api/test_study_cards_review.py::test_review_card_invalid_quality -v
# Expected: ✓ 422 error for quality=6
```

---

#### Phase 4: Final QA (0.5 hours)
**Agent**: `testing-qa-expert`

**Comprehensive QA Checklist**:
```bash
# ✓ 1. Frontend algorithm tests
npm test -- useSpacedRepetition.test.ts
# Expected: 15/15 tests passed

# ✓ 2. Frontend component tests
npm test -- QualityRating.test.tsx ReviewResult.test.tsx
# Expected: 10/10 tests passed

# ✓ 3. Backend integration tests
pytest tests/test_api/test_study_cards_review.py -v
# Expected: 5/5 tests passed

# ✓ 4. E2E test
npx playwright test tests/e2e/sm2-review.spec.ts
# Expected: 1/1 test passed

# ✓ 5. Frontend/Backend consistency validation
python scripts/test_sm2_consistency.py
# Expected: ✓ All quality values (0-5) produce same results

# ✓ 6. TypeScript compilation
npx tsc --noEmit
# Expected: 0 errors

# ✓ 7. Python tests
pytest tests/test_api/test_study_cards_review.py -v
# Expected: 5/5 tests passed

# ✓ 8. Build success (frontend)
npm run build
# Expected: Build succeeds

# ✓ 9. Database update atomicity test
python scripts/test_sm2_transaction.py
# Expected: ✓ All SM-2 params updated atomically

# ✓ 10. Due date filter test
pytest tests/test_api/test_study_cards.py::test_get_due_cards -v
# Expected: ✓ Only cards WHERE next_review_date <= NOW()
```

**ONLY mark PRD-P1-007 COMPLETE if all 10 checks pass**

---

### PRD-P8-002: Integration Testing

**LOOP Section - Add QA Gates**:

#### Phase 1: Backend Integration Tests (3 hours)
**Agent**: `testing-qa-expert`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/backend

# Run all integration tests
pytest tests/integration/test_study_cards_pipeline.py -v
# Expected: ✓ 12/12 tests passed

# Verify coverage
pytest tests/integration/test_study_cards_pipeline.py --cov=src --cov-report=term
# Expected: ✓ Integration code paths covered
```

**QA Gate 2 (PM Validation)**:
```bash
# PM reviews test quality
cat tests/integration/test_study_cards_pipeline.py
# Expected: ✓ Tests cover all integration points

# PM runs tests independently
pytest tests/integration/test_study_cards_pipeline.py -v --tb=short
# Expected: ✓ 12/12 tests passed
```

**QA Gate 3 (security-compliance-expert Review)**:
```bash
# Security review of tests
grep -r "password\|secret\|api_key" tests/integration/test_study_cards_pipeline.py
# Expected: ✓ No hardcoded credentials in tests

# Verify test fixtures use Vault
grep "get_vault_secret\|mock" tests/integration/
# Expected: ✓ All secrets mocked or from Vault
```

---

#### Phase 2: Frontend Integration Tests (2 hours)
**Agent**: `testing-qa-expert`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/frontend

# Run frontend integration tests
npm test -- integration.test.tsx
# Expected: ✓ 4/4 tests passed
```

**QA Gate 2 (PM Validation)**:
```bash
# PM verifies test coverage
npm test -- integration.test.tsx --coverage
# Expected: ✓ Integration code ≥80% covered
```

---

#### Phase 3: E2E Tests (2 hours)
**Agent**: `testing-qa-expert`

**QA Gate 1 (Agent Self-Validation)**:
```bash
cd /home/dev/Development/irStudy/frontend

# Run E2E tests
npx playwright test tests/e2e/study-cards-pipeline.spec.ts
# Expected: ✓ 3/3 tests passed

# Performance validation
npx playwright test tests/e2e/study-cards-pipeline.spec.ts -t "E2E-001"
# Expected: ✓ Complete workflow <15s
```

**QA Gate 2 (PM Validation)**:
```bash
# PM reviews E2E test quality
cat tests/e2e/study-cards-pipeline.spec.ts
# Expected: ✓ Tests cover complete user workflows

# PM runs E2E tests
npx playwright test tests/e2e/study-cards-pipeline.spec.ts --headed
# Expected: ✓ All tests pass, UI looks correct
```

**QA Gate 3 (testing-qa-expert Final Review)**:
```bash
# QA runs ALL tests across entire pipeline

# Backend tests
cd /home/dev/Development/irStudy/backend
pytest tests/ -v
# Expected: ✓ 100% pass rate

# Frontend tests
cd /home/dev/Development/irStudy/frontend
npm test
# Expected: ✓ 100% pass rate

# E2E tests
npx playwright test
# Expected: ✓ 100% pass rate

# Performance validation
npx playwright test tests/e2e/study-cards-pipeline.spec.ts -t "performance"
# Expected: ✓ Full pipeline <15s
```

**ONLY mark PRD-P8-002 COMPLETE if ALL tests pass**

---

## Summary: Mandatory QA Gates Per PRD

| PRD | Total QA Gates | Agent Self-Validation | PM Validation | testing-qa-expert Review | Final Approval |
|-----|----------------|----------------------|---------------|--------------------------|----------------|
| P1-005 | 12 gates | Phase 1-3 (3 gates) | Phase 1-3 (3 gates) | Phase 1-4 (4 gates) | PM + QA |
| P1-006 | 12 gates | Phase 1-3 (3 gates) | Phase 1-3 (3 gates) | Phase 1-4 (4 gates) | PM + QA |
| P1-007 | 12 gates | Phase 1-3 (3 gates) | Phase 1-3 (3 gates) | Phase 1-4 (4 gates) | PM + QA |
| P8-002 | 9 gates | Phase 1-3 (3 gates) | Phase 1-3 (3 gates) | Phase 3 (3 gates) | PM + QA |
| **Total** | **45 QA gates** | **12 gates** | **12 gates** | **15 gates** | **4 PRDs** |

---

## Enforcement Rules

### Rule 1: Zero-Tolerance for Test Failures
- **1 test failure = BLOCK entire PRD**
- No exceptions, no "we'll fix it later"
- Fix immediately, re-validate, then proceed

### Rule 2: Sequential Validation (No Skipping)
```
Agent Self-Validation → PM Validation → QA Expert Review
         ↓                    ↓                  ↓
      MUST PASS           MUST PASS          MUST PASS
         ↓                    ↓                  ↓
    If FAIL → Fix      If FAIL → Fix      If FAIL → Fix
```

### Rule 3: No Code Acceptance Without QA
- **testing-qa-expert MUST review** before marking phase complete
- PM cannot accept code without QA sign-off
- Exception: Only for documentation-only changes

### Rule 4: Performance Benchmarks Enforced
- PRD-P1-005: <8s card generation
- PRD-P1-006: 60fps flip animation
- PRD-P1-007: <200ms API response
- PRD-P8-002: <15s full pipeline
- **Fail if ANY benchmark missed**

### Rule 5: Security Zero-Tolerance
```bash
# These commands MUST return 0 matches:
grep -r "sk-ant-\|ANTHROPIC_API_KEY.*=\|password.*=\|hardcoded" src/
grep -r "acetaminophen\|mg/dL\|911" src/  # Australian standards
```

---

## PM Checklist Before Marking PRD Complete

```
PRD: _______________

Phase 1:
[ ] Agent self-validated (ran all commands, 0 errors)
[ ] PM validated independently (ran commands, verified results)
[ ] testing-qa-expert reviewed (all tests passed)
[ ] Phase 1 COMPLETE ✓

Phase 2:
[ ] Agent self-validated
[ ] PM validated independently
[ ] testing-qa-expert reviewed
[ ] Phase 2 COMPLETE ✓

Phase 3:
[ ] Agent self-validated
[ ] PM validated independently
[ ] testing-qa-expert reviewed
[ ] Phase 3 COMPLETE ✓

Phase 4 (Final QA):
[ ] testing-qa-expert comprehensive checklist (10/10 items passed)
[ ] All unit tests passing (100% pass rate)
[ ] All integration tests passing (100% pass rate)
[ ] E2E tests passing (100% pass rate)
[ ] Test coverage ≥80%
[ ] Performance benchmarks met
[ ] Security scan clean (0 violations)
[ ] Australian medical standards validated
[ ] Documentation complete

FINAL APPROVAL:
[ ] PM sign-off: _______________
[ ] QA sign-off: _______________
[ ] PRD marked COMPLETE ✓
```

---

## Addendum Compliance

**This addendum is MANDATORY for Study Cards Pipeline PRDs.**

By following these QA gates, we ensure:
- ✅ Expert agents used correctly (no general-purpose shortcuts)
- ✅ QA happens BEFORE acceptance (not after deployment)
- ✅ 100% test pass rate enforced (zero tolerance for failures)
- ✅ Performance benchmarks met (not "best effort")
- ✅ Security validated (no credentials leak to production)
- ✅ Australian medical standards enforced (paracetamol, eTG, SI units)

**Violation of these QA gates = PRD rejected, must restart phase**

---

**Document Status**: ✅ ACTIVE - Apply to all Study Cards Pipeline PRDs immediately

**Last Updated**: 2026-03-24
**Version**: 1.0
**Approved By**: PM (Project Manager)
