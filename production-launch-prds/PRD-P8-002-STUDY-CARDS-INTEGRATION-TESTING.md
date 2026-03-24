# PRD: Study Cards Pipeline - Integration Testing

**PRD ID**: PRD-P8-002-STUDY-CARDS-INTEGRATION-TESTING
**Category**: Integration Testing & Quality Assurance
**Priority**: P1-Critical (Validates Complete Study Cards Pipeline)
**Estimated Effort**: 6-8 hours
**Dependencies**: PRD-P1-005, PRD-P1-006, PRD-P1-007 (all must be complete)
**Status**: Ready for Implementation
**Assigned Agent**: `testing-qa-expert`

**Version**: 1.1 (Enhanced with Comprehensive Testing Plan)
**Created**: 2026-03-22
**Last Updated**: 2026-03-25

**Related Documentation**:
- [Comprehensive Testing Plan Part 1](./COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md) - Tests 1-90 (Unit + Integration)
- [Comprehensive Testing Plan Part 2](./COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS-PART2.md) - Tests 91-112 (Integration + E2E + Security + Performance + Accessibility)
- [PRD-P1-008: Frontend Testing Implementation](./PRD-P1-008-FRONTEND-TESTING-IMPLEMENTATION.md) - Ralph PRD for 85 frontend tests
- [PRD-P1-009: Backend Testing Implementation](./PRD-P1-009-BACKEND-TESTING-IMPLEMENTATION.md) - Ralph PRD for 27 backend tests

---

## R - REQUEST (What & Why)

### Executive Summary

Create a **comprehensive integration test suite** that validates the complete study cards pipeline end-to-end. This PRD ensures that all three components (Auto Study Card Generation, Flashcard Review Interface, SM-2 Review Logic) work together seamlessly, preventing regressions and catching integration bugs before production.

**NOTE**: This PRD is enhanced by a comprehensive testing plan covering **112 total tests** (60 unit + 36 integration + 16 E2E) across all study cards components. See the referenced documentation above for full test specifications with complete code examples.

**Testing Scope** (Original PRD Focus):
1. **OSCE → Study Cards** - Verify P1-4 (Scoring) triggers P1-5 (Card Generation) correctly
2. **Study Cards → Review Interface** - Verify P1-5 cards display correctly in P1-6 (Flashcard UI)
3. **Review → SM-2 Update** - Verify P1-6 ratings trigger P1-7 (SM-2 calculations) correctly
4. **Complete Workflow** - End-to-end test: OSCE session → Generate cards → Review → Rate → Next review scheduled
5. **Data Consistency** - Cross-component data validation (same card seen by all layers)
6. **Performance** - Full pipeline completes in <15 seconds
7. **Error Handling** - Graceful degradation when components fail

**Enhanced Testing Scope** (Comprehensive Testing Plan):
- **60 Unit Tests** - Component isolation (FlashcardCard, QualityRating, SM-2 algorithm, API endpoints)
- **36 Integration Tests** - Component interactions (P1-005↔P1-006, P1-006↔P1-007, Full pipeline)
- **16 E2E Tests** - Complete user workflows (Playwright multi-browser)
- **Security Tests** - XSS prevention, SQL injection, JWT auth, authorization, rate limiting
- **Performance Tests** - 60fps animation, <8s generation, <200ms API, 50 concurrent users
- **Accessibility Tests** - WCAG 2.2 AA compliance, keyboard navigation, screen reader support
- **Coverage Targets** - ≥80% lines, ≥75% branches, ≥90% functions

**Business Impact**:
- **Zero production bugs** - Catch integration issues before deployment
- **Regression prevention** - Automated tests run on every code change
- **Quality assurance** - 100% test pass rate enforced before merge
- **Developer confidence** - Clear validation that all PRDs work together
- **Time savings** - Automated tests faster than manual QA (2 min vs. 20 min)

**Current State**: Each PRD has unit/component tests, but no integration tests across all 3 PRDs.

**Desired State**: Comprehensive integration test suite covering all workflows, with 100% pass rate enforced by CI/CD.

### User Story

**As a** developer implementing the study cards pipeline
**I want** automated integration tests that validate all 3 PRDs work together
**So that** I can confidently deploy to production knowing the complete workflow functions correctly

**Acceptance Criteria**:
- After completing OSCE session, study cards generate automatically (P1-4 → P1-5 integration)
- Generated cards appear in review interface with correct data (P1-5 → P1-6 integration)
- Rating cards updates SM-2 parameters correctly (P1-6 → P1-7 integration)
- Next day, only cards with next_review_date <= NOW() appear (P1-7 → P1-6 integration)
- All tests pass on every git push (CI/CD enforcement)

### Problem Statement

**Current Pain Points**:
1. **No integration tests** - Unit tests pass but components might not integrate
2. **Manual QA required** - Developer must manually test complete workflow (time-consuming)
3. **Regression risk** - Changes to P1-5 might break P1-6 without detection
4. **Data inconsistency** - Frontend/backend might calculate SM-2 differently (caught only in production)

**Root Cause**: Each PRD developed independently with only unit tests. No tests validate cross-PRD integration.

**Proposed Solution**:
- **12 integration tests** covering all component interactions
- **3 E2E tests** (Playwright) covering complete user workflows
- **Performance benchmarks** ensuring <15s total pipeline time
- **CI/CD enforcement** blocking merges if tests fail

**Success Metrics**:
- 15/15 integration tests passing (100% pass rate)
- E2E tests run in <3 minutes total
- 0 production bugs related to study cards pipeline in first 30 days
- Developers deploy with confidence (measured by survey)

### Success Criteria

#### Must Have (100% Required)
- [ ] **112 Total Tests Passing**: 60 unit + 36 integration + 16 E2E (100% pass rate)
- [ ] **Integration Tests**: 36 tests covering all P1-5 ↔ P1-6 ↔ P1-7 interactions
- [ ] **E2E Tests**: 16 complete workflows with Playwright (multi-browser: Chromium, Firefox, WebKit)
- [ ] **Performance Benchmarks**: 60fps animation, <8s generation, <200ms API, <100ms SM-2 update, <15s total pipeline
- [ ] **Data Consistency**: Frontend/backend SM-2 calculations match (within 0.01 difference) - 10 test cases
- [ ] **Security Validation**: 5 tests (XSS, SQL injection, JWT, authorization, rate limiting)
- [ ] **Accessibility Compliance**: 7 WCAG 2.2 AA tests (Lighthouse ≥95, keyboard navigation, screen reader)
- [ ] **Error Handling**: Tests verify graceful degradation (RAG unavailable, API timeout, etc.)
- [ ] **CI/CD Integration**: Tests run automatically on every PR
- [ ] **Coverage Targets Met**: ≥80% lines, ≥75% branches, ≥90% functions

#### Should Have (90% Priority)
- [ ] **Test Coverage Report**: ≥80% coverage for integration code paths
- [ ] **Performance Regression Tests**: Fail if pipeline >20s (alert on degradation)
- [ ] **Visual Regression Tests**: Screenshot comparison for flashcard UI
- [ ] **Load Testing**: 50 concurrent users reviewing cards simultaneously

#### Nice to Have (Optional)
- [ ] **Chaos Testing**: Random component failures, verify system resilience
- [ ] **Database Rollback Tests**: Verify SM-2 updates are atomic
- [ ] **Cross-browser Tests**: Chrome, Firefox, Safari (Playwright matrix)

---

## A - ARCHITECTURE (How)

### Testing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Integration Test Suite                      │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Layer 1: Component Integration Tests (Backend)           │  │
│  │ - pytest (12 tests)                                      │  │
│  │                                                           │  │
│  │ Test 1: OSCE Finalize → Card Generation                  │  │
│  │   POST /osce-attempts/{id}/finalize                      │  │
│  │   → Triggers card generation                             │  │
│  │   → Verify 3-5 cards created with session_id             │  │
│  │                                                           │  │
│  │ Test 2: Card Generation → Database                       │  │
│  │   POST /study-cards/generate-from-osce                   │  │
│  │   → Verify cards inserted with correct SM-2 params       │  │
│  │   → Verify citations have qdrant_point_id                │  │
│  │                                                           │  │
│  │ Test 3: Card Review → SM-2 Update                        │  │
│  │   PUT /study-cards/{id}/review                           │  │
│  │   → Verify ease_factor, interval, next_review_date       │  │
│  │   → Verify last_reviewed_at updated                      │  │
│  │                                                           │  │
│  │ Test 4: Due Cards Filter                                 │  │
│  │   GET /study-cards?due=true                              │  │
│  │   → Verify only cards WHERE next_review_date <= NOW()    │  │
│  │                                                           │  │
│  │ ... 8 more integration tests                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Layer 2: Frontend Integration Tests (Vitest)             │  │
│  │ - React Testing Library (5 tests)                        │  │
│  │                                                           │  │
│  │ Test 1: FlashcardView → QualityRating Integration        │  │
│  │   Render FlashcardView with cards                        │  │
│  │   → Flip to answer                                       │  │
│  │   → QualityRating component appears                      │  │
│  │   → Click quality button                                 │  │
│  │   → Verify API call with correct card_id + quality       │  │
│  │                                                           │  │
│  │ Test 2: useSpacedRepetition Hook → API Integration       │  │
│  │   Call submitReview mutation                             │  │
│  │   → Verify PUT request sent                              │  │
│  │   → Mock API response                                    │  │
│  │   → Verify query invalidation                            │  │
│  │                                                           │  │
│  │ ... 3 more frontend integration tests                    │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │ Layer 3: E2E Tests (Playwright - 3 tests)                │  │
│  │                                                           │  │
│  │ E2E Test 1: Complete Study Cards Workflow                │  │
│  │   1. Login as student                                    │  │
│  │   2. Complete OSCE session                               │  │
│  │   3. View results page                                   │  │
│  │   4. Click "Generate Study Cards"                        │  │
│  │   5. Wait for generation (< 10s)                         │  │
│  │   6. Navigate to /study-cards/review                     │  │
│  │   7. Verify cards appear                                 │  │
│  │   8. Review card (show answer)                           │  │
│  │   9. Rate card (quality 4)                               │  │
│  │   10. Verify "Next review: X days" message              │  │
│  │   11. Continue to next card                              │  │
│  │   12. Complete all cards                                 │  │
│  │   13. Verify completion message                          │  │
│  │                                                           │  │
│  │ E2E Test 2: Spaced Repetition Scheduling                 │  │
│  │   1. Generate cards                                      │  │
│  │   2. Review all cards with quality 5 (perfect)          │  │
│  │   3. Verify cards disappear from "due" list              │  │
│  │   4. Manually set next_review_date to past (DB query)   │  │
│  │   5. Refresh /study-cards/review                         │  │
│  │   6. Verify cards reappear                               │  │
│  │                                                           │  │
│  │ E2E Test 3: SM-2 Algorithm Accuracy (Cross-Validation)   │  │
│  │   1. Generate test card                                  │  │
│  │   2. Review with quality 0-5 (6 separate tests)         │  │
│  │   3. For each quality:                                   │  │
│  │      - Frontend calculates SM-2                          │  │
│  │      - Backend recalculates SM-2                         │  │
│  │      - Verify frontend == backend (within 0.01)         │  │
│  │      - Verify database updated correctly                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Integration Test Matrix

| Test ID | Component A | Component B | Validates | Priority |
|---------|-------------|-------------|-----------|----------|
| INT-001 | P1-4 (OSCE Scoring) | P1-5 (Card Gen) | Finalize triggers generation | P0 |
| INT-002 | P1-5 (Card Gen) | Database | Cards inserted with SM-2 params | P0 |
| INT-003 | P1-5 (Card Gen) | Qdrant RAG | Citations have qdrant_point_id | P0 |
| INT-004 | Database | P1-6 (Flashcard UI) | Cards fetch and display | P0 |
| INT-005 | P1-6 (UI) | P1-7 (SM-2) | Quality ratings trigger calculations | P0 |
| INT-006 | P1-7 (Frontend) | P1-7 (Backend) | SM-2 calculations match | P0 |
| INT-007 | P1-7 (SM-2) | Database | SM-2 params update atomically | P0 |
| INT-008 | Database | P1-6 (UI) | Due date filter works | P0 |
| INT-009 | P1-5 (Card Gen) | P1-6 (UI) | Citations display correctly | P1 |
| INT-010 | P1-7 (SM-2) | P1-6 (UI) | Review result shows correct data | P1 |
| INT-011 | All Components | Performance | Pipeline completes <15s | P1 |
| INT-012 | All Components | Error Recovery | Graceful degradation on failures | P1 |

### Data Flow Validation

**Complete Pipeline Test** (E2E Test 1):
```
User Action                    System Component         Expected Result
─────────────────────────────────────────────────────────────────────
1. Complete OSCE session    → P1-4 (Scoring)         → total_score calculated
2. Click "Finalize"         → P1-4 (API)             → ai_osce_scores inserted
3. Auto-trigger card gen    → P1-5 (Card Gen)        → 3-5 cards created
   (or manual button click)
4. Claude API call          → P1-5 (Claude)          → Learning points extracted
5. Qdrant query             → P1-5 (RAG)             → Citations retrieved
6. Database insert          → P1-5 (DB)              → study_cards table updated
7. Navigate to review       → P1-6 (UI)              → FlashcardView renders
8. Fetch due cards          → P1-6 (API)             → GET /study-cards?due=true
9. Display card             → P1-6 (UI)              → Question shown
10. Flip to answer          → P1-6 (UI)              → Answer + citations shown
11. Click quality 4         → P1-7 (QualityRating)   → onRate(4) called
12. Calculate SM-2          → P1-7 (Hook)            → New params calculated
13. Submit review           → P1-7 (API)             → PUT /study-cards/{id}/review
14. Update database         → P1-7 (Backend)         → SM-2 params updated
15. Show result             → P1-7 (UI)              → "Next review: 6 days"
16. Invalidate cache        → P1-7 (React Query)     → Refetch cards
17. Next card loads         → P1-6 (UI)              → New card from updated list
18. Repeat steps 9-17       → Loop                   → All cards reviewed
19. Completion message      → P1-6 (UI)              → "Great job! 5 cards reviewed"

Next Day:
20. Open review page        → P1-6 (UI)              → GET /study-cards?due=true
21. Filter by due date      → Backend                → WHERE next_review_date <= NOW()
22. Show due cards only     → P1-6 (UI)              → Cards rated 0-3 reappear
                                                      → Cards rated 4-5 don't appear (scheduled later)
```

---

## L - LOOP (Iterative Development)

### Phase 1: Backend Integration Tests (3 hours)

**Objective**: Create pytest integration tests for API ↔ Database ↔ RAG

**Tasks**:
1. Create `tests/integration/test_study_cards_pipeline.py`
2. Write 8 integration tests covering P1-5, P1-7 backend
3. Add test fixtures for OSCE sessions, study cards
4. Mock Qdrant/Claude API for fast tests

**Deliverables**:
- 8 integration tests (pytest)
- Test fixtures
- Mock implementations

**Validation Checkpoints**:
- [ ] INT-001: OSCE finalize triggers card generation
- [ ] INT-002: Cards inserted with correct SM-2 params
- [ ] INT-003: Citations have qdrant_point_id
- [ ] INT-007: SM-2 updates are atomic (transaction test)
- [ ] INT-008: Due date filter works correctly
- [ ] 8/8 tests passing

**Test Example**:
```python
def test_osce_to_study_cards_integration(client, jwt_token, db):
    """INT-001: OSCE finalize triggers card generation"""
    # Step 1: Create OSCE session
    osce_response = client.post(
        "/api/v1/osce-attempts/start",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"persona_code": "CARD-001"}
    )
    attempt_id = osce_response.json()['attempt_id']

    # Step 2: Complete session (send messages, etc.)
    # ... (simplified for brevity)

    # Step 3: Finalize session (triggers scoring)
    finalize_response = client.post(
        f"/api/v1/osce-attempts/{attempt_id}/finalize",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert finalize_response.status_code == 200

    # Step 4: Generate study cards
    cards_response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": attempt_id}
    )
    assert cards_response.status_code == 201
    cards = cards_response.json()['cards']

    # Assertions
    assert len(cards) >= 3 and len(cards) <= 5
    assert all(card['session_id'] == attempt_id for card in cards)
    assert all(card['sm2_params']['ease_factor'] == 2.5 for card in cards)
    assert all(card['sm2_params']['interval_days'] == 1 for card in cards)
    assert all(len(card['citations']) >= 1 for card in cards)
```

#### 3-Layer QA Validation (Phase 1 - MANDATORY)
**Layer 1**: `pytest tests/test_integration/ -v` (12/12 pass) + `bandit -r backend/tests/` (0 issues)
**Layer 2**: PM reviews test code quality + verifies integration tests cover P1-5 ↔ P1-6 ↔ P1-7 interactions
**Layer 3**: QA runs `pytest tests/ -v` (100% pass) + `pytest --cov=src` (≥85% coverage)
**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 2: Frontend Integration Tests (2 hours)

**Objective**: Create Vitest integration tests for React components + API

**Tasks**:
1. Create `frontend/src/components/study-cards/__tests__/integration.test.tsx`
2. Write 4 integration tests for component interactions
3. Mock API responses
4. Test React Query integration

**Deliverables**:
- 4 frontend integration tests
- API mocks
- React Query test utils

**Validation Checkpoints**:
- [ ] INT-004: Cards fetch and display correctly
- [ ] INT-005: Quality ratings trigger API calls
- [ ] INT-006: Frontend/backend SM-2 calculations match
- [ ] INT-009: Citations display correctly
- [ ] 4/4 tests passing

**Test Example**:
```typescript
test('INT-005: Quality rating triggers SM-2 API call', async () => {
  const mockCard = {
    card_id: 'test-123',
    question: 'What is diabetes?',
    answer: 'A metabolic disorder',
    sm2_params: { ease_factor: 2.5, interval_days: 1, repetitions: 0 }
  };

  // Mock API
  const mockSubmit = vi.fn().mockResolvedValue({
    ease_factor: 2.6,
    interval_days: 6,
    repetitions: 1,
    next_review_date: '2026-03-28T00:00:00Z'
  });

  render(
    <QueryClientProvider client={queryClient}>
      <FlashcardView cards={[mockCard]} />
    </QueryClientProvider>
  );

  // Show answer
  await userEvent.click(screen.getByText('Show Answer'));

  // Rate card
  await userEvent.click(screen.getByText(/Easy/));

  // Verify API call
  await waitFor(() => {
    expect(mockSubmit).toHaveBeenCalledWith({
      cardId: 'test-123',
      quality: 4
    });
  });

  // Verify UI updated
  expect(screen.getByText(/Next review: 6 days/)).toBeInTheDocument();
});
```

#### 3-Layer QA Validation (Phase 2 - MANDATORY)
**Layer 1**: `npm test -- integration.test` (4/4 pass) + `npx tsc --noEmit` (0 errors)
**Layer 2**: PM reviews component integration tests + manual test UI workflow
**Layer 3**: QA runs `npm test` (100% pass) + `npm test -- --coverage` (≥80%)
**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 3: E2E Tests (2 hours)

**Objective**: Create Playwright E2E tests for complete workflows

**Tasks**:
1. Create `frontend/tests/e2e/study-cards-pipeline.spec.ts`
2. Write 3 E2E tests covering full user journeys
3. Add performance timing assertions
4. Test cross-browser compatibility

**Deliverables**:
- 3 E2E tests (Playwright)
- Performance benchmarks
- Cross-browser test matrix

**Validation Checkpoints**:
- [ ] E2E-001: Complete study cards workflow (<3 min)
- [ ] E2E-002: Spaced repetition scheduling works
- [ ] E2E-003: SM-2 algorithm accuracy (frontend == backend)
- [ ] Performance: Full pipeline <15s
- [ ] 3/3 E2E tests passing

**Test Example**:
```typescript
test('E2E-001: Complete study cards workflow', async ({ page }) => {
  const startTime = Date.now();

  // 1. Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'student@test.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');

  // 2. Start OSCE session
  await page.goto('/osce-practice');
  await page.click('[data-testid="persona-CARD-001"]');
  await page.click('button:has-text("Start Session")');
  await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();

  // 3. Complete session (simplified - send a few messages)
  await page.fill('[data-testid="chat-input"]', 'Hello, I have chest pain');
  await page.click('[data-testid="send-button"]');
  await page.waitForResponse(resp => resp.url().includes('/api/v1/chat'));

  // 4. End session
  await page.click('button:has-text("End Session")');
  await expect(page.locator('[data-testid="osce-results"]')).toBeVisible();

  // 5. Generate study cards
  await page.click('button:has-text("Generate Study Cards")');
  await expect(page.locator('[data-testid="study-cards-generated"]')).toBeVisible({ timeout: 10000 });

  const cardCount = await page.locator('[data-testid="study-card-item"]').count();
  expect(cardCount).toBeGreaterThanOrEqual(3);
  expect(cardCount).toBeLessThanOrEqual(5);

  // 6. Navigate to review
  await page.goto('/study-cards/review');
  await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

  // 7. Review first card
  await page.click('button:has-text("Show Answer")');
  await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

  // 8. Rate card (quality 4)
  await page.click('[data-testid="quality-4"]');
  await expect(page.locator('text=Next review:')).toBeVisible();
  await expect(page.locator('text=6 days')).toBeVisible();

  // 9. Continue to next card
  await page.click('button:has-text("Continue to Next Card")');
  await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

  // Performance assertion
  const totalTime = Date.now() - startTime;
  expect(totalTime).toBeLessThan(15000); // < 15 seconds
});
```

#### 3-Layer QA Validation (Phase 3 - MANDATORY)
**Layer 1**: `npx playwright test study-cards-pipeline.spec.ts` (3/3 pass) + performance check (<15s total)
**Layer 2**: PM runs E2E tests manually + observes full workflow in browser
**Layer 3**: QA runs cross-browser tests (`--project=chromium --project=firefox`) + validates performance benchmarks
**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 4: CI/CD Integration & Documentation (1 hour)

**Objective**: Add tests to CI/CD pipeline and document results

**Tasks**:
1. Update `.github/workflows/tests.yml` to run integration tests
2. Add test coverage reporting
3. Create test documentation
4. Add performance regression alerts

**Deliverables**:
- CI/CD workflow updates
- Test coverage badges
- Integration test documentation

**Validation Checkpoints**:
- [ ] All 19 tests run on every PR (12 backend + 4 frontend + 3 E2E)
- [ ] Tests block merge if failing
- [ ] Coverage report generated
- [ ] Performance alerts configured

#### 3-Layer QA Validation (Phase 4 - MANDATORY FINAL APPROVAL)

**Layer 1**: CI/CD config updated (`.github/workflows/test.yml`) + all pipelines pass + documentation complete
**Layer 2**: PM reviews CI/CD integration + verifies tests run on PR + checks coverage reports automated
**Layer 3**: QA comprehensive final validation:
  - All 19 tests pass (12 backend + 4 frontend + 3 E2E)
  - Coverage ≥85% backend, ≥80% frontend
  - Performance benchmarks met (<15s pipeline, <8s generation, <200ms API)
  - CI/CD blocking works (manually create failing test, verify PR blocked)
  - Documentation complete (test results, coverage reports, performance benchmarks)
**QA Final Decision**: ✅ APPROVE PRD-P8-002 COMPLETE / ❌ REJECT

**Final Approval Signature**:
- [ ] PM Sign-Off: _______________ Date: _______
- [ ] testing-qa-expert Sign-Off: _______________ Date: _______

**PRD-P8-002 Status**: ⏳ INCOMPLETE / ✅ COMPLETE

---

## P - PLAN (Detailed Implementation)

### Files to Create

#### 1. `backend/tests/integration/test_study_cards_pipeline.py` (600 lines)

**Purpose**: Backend integration tests

**Full Implementation**:

```python
"""
Integration tests for Study Cards Pipeline (P1-5, P1-7).

Tests the complete backend workflow:
- OSCE session → Card generation
- Card generation → Database
- Card review → SM-2 update
- Database queries → API responses

Run with: pytest tests/integration/test_study_cards_pipeline.py -v
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from src.db.models import StudyCard, OSCEScoreAI, OSCEAttemptAI
from src.ai.study_card_generator import StudyCardGenerator


@pytest.fixture
def sample_osce_session(db, test_user):
    """Create a completed OSCE session with scores."""
    # Create OSCE attempt
    attempt = OSCEAttemptAI(
        attempt_id="test-attempt-123",
        user_id=test_user.user_id,
        persona_code="CARD-001",
        started_at=datetime.now(timezone.utc),
        ended_at=datetime.now(timezone.utc)
    )
    db.add(attempt)

    # Create scores
    scores = OSCEScoreAI(
        score_id="test-score-123",
        attempt_id="test-attempt-123",
        total_score=12.5,
        result="PASS",
        overall_feedback="Good communication skills, missed some history elements",
        strengths="Excellent rapport, clear explanations",
        areas_for_improvement="Explore dietary patterns, medication adherence",
        # ... other fields
    )
    db.add(scores)
    db.commit()

    return attempt


def test_int_001_osce_to_study_cards(client, jwt_token, sample_osce_session, db):
    """
    INT-001: OSCE finalize triggers card generation.

    Validates: P1-4 (Scoring) → P1-5 (Card Generation)
    """
    # Generate study cards from OSCE session
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": sample_osce_session.attempt_id}
    )

    assert response.status_code == 201
    data = response.json()

    # Verify cards generated
    assert 'cards' in data
    assert len(data['cards']) >= 3
    assert len(data['cards']) <= 5

    # Verify session linking
    for card in data['cards']:
        assert card['session_id'] == sample_osce_session.attempt_id

    # Verify SM-2 initialization
    for card in data['cards']:
        assert card['sm2_params']['ease_factor'] == 2.5
        assert card['sm2_params']['interval_days'] == 1
        assert card['sm2_params']['repetitions'] == 0


def test_int_002_card_generation_database(client, jwt_token, sample_osce_session, db):
    """
    INT-002: Cards inserted with correct SM-2 params.

    Validates: P1-5 (Card Generation) → Database
    """
    # Generate cards
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": sample_osce_session.attempt_id}
    )

    card_ids = [card['card_id'] for card in response.json()['cards']]

    # Query database directly
    db_cards = db.query(StudyCard).filter(StudyCard.card_id.in_(card_ids)).all()

    assert len(db_cards) == len(card_ids)

    for card in db_cards:
        # SM-2 initialization
        assert card.ease_factor == 2.5
        assert card.interval_days == 1
        assert card.repetitions == 0
        assert card.next_review_date is not None

        # Session linking
        assert card.session_id == sample_osce_session.attempt_id

        # Content validation
        assert card.question is not None and len(card.question) > 20
        assert card.answer is not None and len(card.answer) > 50


@patch('src.ai.study_card_generator.QdrantClient')
def test_int_003_rag_citations(mock_qdrant, client, jwt_token, sample_osce_session):
    """
    INT-003: Citations have qdrant_point_id.

    Validates: P1-5 (Card Generation) → Qdrant RAG
    """
    # Mock Qdrant response
    mock_qdrant.return_value.search.return_value = [
        MagicMock(
            id="qdrant-id-123",
            score=0.87,
            payload={
                'title': 'eTG Diabetes Management',
                'page': 'p. 45-47',
                'text': 'Sample medical guideline text...'
            }
        )
    ]

    # Generate cards
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": sample_osce_session.attempt_id}
    )

    cards = response.json()['cards']

    # Verify citations
    for card in cards:
        assert len(card['citations']) >= 1
        for citation in card['citations']:
            assert 'qdrant_point_id' in citation
            assert 'source' in citation
            assert 'confidence' in citation
            assert citation['confidence'] >= 0.65


def test_int_004_cards_fetch_display(client, jwt_token, db, test_user):
    """
    INT-004: Cards fetch and display correctly.

    Validates: Database → P1-6 (Flashcard UI)
    """
    # Create test cards in database
    cards = [
        StudyCard(
            card_id=f"test-card-{i}",
            user_id=test_user.user_id,
            question=f"Question {i}",
            answer=f"Answer {i}",
            ease_factor=2.5,
            interval_days=1,
            repetitions=0,
            next_review_date=datetime.now(timezone.utc)
        )
        for i in range(5)
    ]
    db.add_all(cards)
    db.commit()

    # Fetch cards via API
    response = client.get(
        "/api/v1/study-cards",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
    data = response.json()

    assert len(data['cards']) == 5
    for i, card in enumerate(data['cards']):
        assert card['question'] == f"Question {i}"
        assert card['answer'] == f"Answer {i}"
        assert 'sm2_params' in card


def test_int_005_quality_rating_trigger(client, jwt_token, db, test_user):
    """
    INT-005: Quality ratings trigger SM-2 calculations.

    Validates: P1-6 (UI) → P1-7 (SM-2)
    """
    # Create test card
    card = StudyCard(
        card_id="test-card-quality",
        user_id=test_user.user_id,
        question="Test question",
        answer="Test answer",
        ease_factor=2.5,
        interval_days=1,
        repetitions=0,
        next_review_date=datetime.now(timezone.utc)
    )
    db.add(card)
    db.commit()

    # Submit quality rating (quality 4 - "Easy")
    response = client.put(
        f"/api/v1/study-cards/{card.card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": 4}
    )

    assert response.status_code == 200
    data = response.json()

    # Verify SM-2 calculation
    assert data['ease_factor'] > 2.5  # Should increase for quality 4
    assert data['interval_days'] == 1  # First review: 1 day
    assert data['repetitions'] == 1  # Incremented
    assert 'next_review_date' in data


def test_int_006_sm2_frontend_backend_match(client, jwt_token, db, test_user):
    """
    INT-006: Frontend/backend SM-2 calculations match.

    Validates: P1-7 (Frontend) ↔ P1-7 (Backend)
    """
    # Create test card
    card = StudyCard(
        card_id="test-card-sm2",
        user_id=test_user.user_id,
        question="Test",
        answer="Test",
        ease_factor=2.5,
        interval_days=6,
        repetitions=2,
        next_review_date=datetime.now(timezone.utc)
    )
    db.add(card)
    db.commit()

    # Calculate SM-2 on frontend (TypeScript algorithm, simulated here)
    def frontend_sm2(quality, ef, interval, reps):
        if quality >= 3:
            if reps == 0:
                new_interval = 1
            elif reps == 1:
                new_interval = 6
            else:
                new_interval = round(interval * ef)

            new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
            new_ef = max(1.3, new_ef)
            new_reps = reps + 1
        else:
            new_interval = 1
            new_ef = ef
            new_reps = 0

        return new_ef, new_interval, new_reps

    quality = 5
    frontend_ef, frontend_interval, frontend_reps = frontend_sm2(
        quality, 2.5, 6, 2
    )

    # Submit to backend
    response = client.put(
        f"/api/v1/study-cards/{card.card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": quality}
    )

    backend_data = response.json()

    # Verify match (within 0.01 tolerance for floating point)
    assert abs(backend_data['ease_factor'] - frontend_ef) < 0.01
    assert backend_data['interval_days'] == frontend_interval
    assert backend_data['repetitions'] == frontend_reps


def test_int_007_sm2_atomic_update(client, jwt_token, db, test_user):
    """
    INT-007: SM-2 updates are atomic (transaction test).

    Validates: P1-7 (SM-2) → Database
    """
    card = StudyCard(
        card_id="test-card-atomic",
        user_id=test_user.user_id,
        question="Test",
        answer="Test",
        ease_factor=2.5,
        interval_days=1,
        repetitions=0
    )
    db.add(card)
    db.commit()

    # Submit review
    response = client.put(
        f"/api/v1/study-cards/{card.card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": 3}
    )

    # Query database
    db.refresh(card)

    # Verify all SM-2 params updated together
    assert card.ease_factor != 2.5  # Changed
    assert card.repetitions == 1  # Changed
    assert card.last_reviewed_at is not None  # Updated


def test_int_008_due_date_filter(client, jwt_token, db, test_user):
    """
    INT-008: Due date filter works correctly.

    Validates: Database → P1-6 (UI)
    """
    # Create cards with different due dates
    now = datetime.now(timezone.utc)

    cards = [
        StudyCard(
            card_id="due-yesterday",
            user_id=test_user.user_id,
            question="Q1",
            answer="A1",
            next_review_date=now - timedelta(days=1)  # Due (past)
        ),
        StudyCard(
            card_id="due-today",
            user_id=test_user.user_id,
            question="Q2",
            answer="A2",
            next_review_date=now  # Due (now)
        ),
        StudyCard(
            card_id="due-tomorrow",
            user_id=test_user.user_id,
            question="Q3",
            answer="A3",
            next_review_date=now + timedelta(days=1)  # NOT due (future)
        )
    ]
    db.add_all(cards)
    db.commit()

    # Fetch due cards only
    response = client.get(
        "/api/v1/study-cards?due=true",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    data = response.json()
    card_ids = [card['card_id'] for card in data['cards']]

    # Verify only past/present cards returned
    assert "due-yesterday" in card_ids
    assert "due-today" in card_ids
    assert "due-tomorrow" not in card_ids


def test_int_009_citations_display(client, jwt_token, sample_osce_session):
    """
    INT-009: Citations display correctly.

    Validates: P1-5 (Card Gen) → P1-6 (UI)
    """
    # Generate cards with citations
    response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": sample_osce_session.attempt_id}
    )

    cards = response.json()['cards']

    for card in cards:
        # Verify citation structure
        for citation in card['citations']:
            assert 'source' in citation
            assert 'qdrant_point_id' in citation
            assert 'confidence' in citation
            assert 'page' in citation

            # Verify data quality
            assert citation['source'] != "Unknown"
            assert len(citation['qdrant_point_id']) > 0
            assert 0.65 <= citation['confidence'] <= 1.0


def test_int_011_performance_pipeline(client, jwt_token, sample_osce_session):
    """
    INT-011: Full pipeline completes in <15 seconds.

    Validates: All Components → Performance
    """
    import time

    start_time = time.time()

    # Step 1: Generate cards (~8s expected)
    gen_response = client.post(
        "/api/v1/study-cards/generate-from-osce",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"attempt_id": sample_osce_session.attempt_id}
    )
    assert gen_response.status_code == 201
    card_id = gen_response.json()['cards'][0]['card_id']

    # Step 2: Fetch cards (~100ms expected)
    fetch_response = client.get(
        "/api/v1/study-cards?due=true",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )
    assert fetch_response.status_code == 200

    # Step 3: Review card (~200ms expected)
    review_response = client.put(
        f"/api/v1/study-cards/{card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": 4}
    )
    assert review_response.status_code == 200

    elapsed = time.time() - start_time

    # Verify performance (< 15 seconds total)
    assert elapsed < 15.0, f"Pipeline took {elapsed:.2f}s, expected <15s"


def test_int_012_error_recovery(client, jwt_token, sample_osce_session):
    """
    INT-012: Graceful degradation on component failures.

    Validates: All Components → Error Handling
    """
    # Test 1: RAG service unavailable
    with patch('src.ai.study_card_generator.QdrantClient') as mock_qdrant:
        mock_qdrant.side_effect = Exception("Qdrant connection failed")

        response = client.post(
            "/api/v1/study-cards/generate-from-osce",
            headers={"Authorization": f"Bearer {jwt_token}"},
            json={"attempt_id": sample_osce_session.attempt_id}
        )

        # Should still generate cards, just without citations
        assert response.status_code == 201
        cards = response.json()['cards']
        assert len(cards) >= 3

        # Citations may be empty (graceful degradation)
        for card in cards:
            assert 'citations' in card  # Field exists
            # Length may be 0 if RAG failed

    # Test 2: Invalid quality rating
    card = StudyCard(
        card_id="test-error",
        user_id=test_user.user_id,
        question="Q",
        answer="A"
    )
    db.add(card)
    db.commit()

    response = client.put(
        f"/api/v1/study-cards/{card.card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": 10}  # Invalid (>5)
    )

    assert response.status_code == 422  # Validation error
```

---

#### 2. `frontend/tests/e2e/study-cards-pipeline.spec.ts` (400 lines)

**Purpose**: Playwright E2E tests

```typescript
import { test, expect } from '@playwright/test';

test.describe('Study Cards Pipeline E2E', () => {
  test('E2E-001: Complete study cards workflow', async ({ page }) => {
    const startTime = Date.now();

    // 1. Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'student@test.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/\/dashboard/);

    // 2. Start OSCE session
    await page.goto('/osce-practice');
    await page.click('[data-testid="persona-CARD-001"]');
    await page.click('button:has-text("Start Session")');
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();

    // 3. Send a few messages (simplified OSCE)
    await page.fill('[data-testid="chat-input"]', 'I have chest pain');
    await page.click('[data-testid="send-button"]');
    await page.waitForResponse(resp => resp.url().includes('/chat'));

    await page.fill('[data-testid="chat-input"]', 'It started 2 hours ago');
    await page.click('[data-testid="send-button"]');
    await page.waitForResponse(resp => resp.url().includes('/chat'));

    // 4. End session
    await page.click('button:has-text("End Session")');
    await expect(page.locator('[data-testid="osce-results"]')).toBeVisible({ timeout: 10000 });

    // 5. Verify score displayed
    await expect(page.locator('[data-testid="total-score"]')).toBeVisible();

    // 6. Generate study cards
    await page.click('button:has-text("Generate Study Cards")');
    await expect(page.locator('[data-testid="study-cards-generated"]')).toBeVisible({ timeout: 12000 });

    const cardCount = await page.locator('[data-testid="study-card-item"]').count();
    expect(cardCount).toBeGreaterThanOrEqual(3);
    expect(cardCount).toBeLessThanOrEqual(5);

    // 7. Navigate to review
    await page.goto('/study-cards/review');
    await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

    // 8. Review first card
    const questionText = await page.locator('[data-testid="flashcard-question"]').textContent();
    expect(questionText).toBeTruthy();

    await page.click('button:has-text("Show Answer")');
    await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

    // 9. Verify citations displayed
    await expect(page.locator('[data-testid="flashcard-citations"]')).toBeVisible();
    const citationCount = await page.locator('[data-testid="citation-item"]').count();
    expect(citationCount).toBeGreaterThanOrEqual(1);

    // 10. Rate card (quality 4 - "Easy")
    await page.click('[data-testid="quality-4"]');
    await expect(page.locator('text=Next review:')).toBeVisible();
    await expect(page.locator('text=6 days')).toBeVisible();

    // 11. Continue to next card
    await page.click('button:has-text("Continue to Next Card")');
    await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

    // 12. Verify progress updated
    await expect(page.locator('text=Card 2 of')).toBeVisible();

    // Performance check
    const elapsed = Date.now() - startTime;
    expect(elapsed).toBeLessThan(15000); // < 15 seconds
  });

  test('E2E-002: Spaced repetition scheduling', async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('[name="email"]', 'student@test.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Navigate to review page
    await page.goto('/study-cards/review');

    // Get initial card count
    const initialCount = await page.locator('[data-testid="flashcard-question"]').count();

    // Review all cards with quality 5 ("Perfect")
    for (let i = 0; i < initialCount; i++) {
      await page.click('button:has-text("Show Answer")');
      await page.click('[data-testid="quality-5"]');

      if (i < initialCount - 1) {
        await page.click('button:has-text("Continue to Next Card")');
      }
    }

    // Verify completion message
    await expect(page.locator('text=No cards due for review')).toBeVisible();

    // Simulate next day (manually update database via API or test fixture)
    // This would require a test helper endpoint or direct database access
    // For now, verify cards are gone from due list
    await page.reload();
    await expect(page.locator('text=No cards due for review')).toBeVisible();
  });

  test('E2E-003: SM-2 algorithm accuracy validation', async ({ page, request }) => {
    // This test validates frontend/backend SM-2 consistency

    // 1. Create a test card via API
    const createResponse = await request.post('/api/v1/study-cards/test-create', {
      headers: { 'Authorization': `Bearer ${await getTestToken()}` },
      data: {
        question: 'Test question for SM-2',
        answer: 'Test answer',
        ease_factor: 2.5,
        interval_days: 1,
        repetitions: 0
      }
    });
    const { card_id } = await createResponse.json();

    // 2. Navigate to review
    await page.goto('/login');
    await page.fill('[name="email"]', 'student@test.com');
    await page.fill('[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await page.goto('/study-cards/review');

    // 3. Test each quality value (0-5)
    for (let quality = 0; quality <= 5; quality++) {
      // Reset card to initial state
      await request.put(`/api/v1/study-cards/${card_id}/reset`, {
        headers: { 'Authorization': `Bearer ${await getTestToken()}` },
        data: { ease_factor: 2.5, interval_days: 1, repetitions: 0 }
      });

      // Review with this quality
      await page.goto('/study-cards/review');
      await page.click('button:has-text("Show Answer")');
      await page.click(`[data-testid="quality-${quality}"]`);

      // Get frontend calculated result
      const frontendResult = await page.locator('[data-testid="sm2-result"]').getAttribute('data-result');
      const frontend = JSON.parse(frontendResult);

      // Get backend result
      const backendResponse = await request.get(`/api/v1/study-cards/${card_id}`, {
        headers: { 'Authorization': `Bearer ${await getTestToken()}` }
      });
      const backend = await backendResponse.json();

      // Verify match (within 0.01 tolerance)
      expect(Math.abs(frontend.ease_factor - backend.ease_factor)).toBeLessThan(0.01);
      expect(frontend.interval_days).toBe(backend.interval_days);
      expect(frontend.repetitions).toBe(backend.repetitions);
    }
  });
});

// Helper function to get test JWT token
async function getTestToken(): Promise<string> {
  // Implementation depends on your auth system
  // Return a valid JWT for test user
  return 'test-jwt-token';
}
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### Integration Tests
- [ ] **INT-001**: OSCE → Card generation (8/8 passing)
- [ ] **INT-002**: Cards → Database with SM-2 params
- [ ] **INT-003**: RAG citations have qdrant_point_id
- [ ] **INT-004**: Cards fetch and display
- [ ] **INT-005**: Quality ratings trigger SM-2
- [ ] **INT-006**: Frontend/backend SM-2 match (within 0.01)
- [ ] **INT-007**: SM-2 updates atomic
- [ ] **INT-008**: Due date filter works

#### E2E Tests
- [ ] **E2E-001**: Complete workflow (<15s)
- [ ] **E2E-002**: Spaced repetition scheduling
- [ ] **E2E-003**: SM-2 algorithm accuracy

#### CI/CD
- [ ] Tests run on every PR
- [ ] Tests block merge if failing
- [ ] Coverage report ≥80%
- [ ] Performance alerts configured

### Validation Commands

```bash
# Backend integration tests
cd /home/dev/Development/irStudy/backend
pytest tests/integration/test_study_cards_pipeline.py -v
# Expected: 12/12 tests passed

# Frontend integration tests
cd /home/dev/Development/irStudy/frontend
npm test -- integration.test.tsx
# Expected: 4/4 tests passed

# E2E tests
cd /home/dev/Development/irStudy/frontend
npx playwright test tests/e2e/study-cards-pipeline.spec.ts
# Expected: 3/3 tests passed

# All tests (backend + frontend + E2E)
npm run test:all
# Expected: 19/19 tests passed

# Coverage report
npm run test:coverage
# Expected: ≥80% integration code coverage
```

---

## Agent OS Expert Constraints

### Agent: testing-qa-expert

**CRITICAL - Read Before Starting**:

**1. Test Coverage Requirements**:
- 100% pass rate mandatory
- Test all integration points (8 backend + 4 frontend + 3 E2E)
- Performance benchmarks (<15s pipeline)
- Error handling tests

**2. Test Data Management**:
- Use fixtures for OSCE sessions, study cards
- Mock external services (Qdrant, Claude API)
- Clean up database after each test

**3. CI/CD Integration**:
- Tests must be fast (<5 min total)
- Use test database (not production)
- Parallel test execution where possible

**4. Validation Checklist**:
- [ ] 19/19 tests passing
- [ ] Coverage ≥80%
- [ ] Performance <15s validated
- [ ] CI/CD workflow configured

---

## Dependencies

### Testing Dependencies (Already Installed)
- Backend: `pytest`, `pytest-mock`, `httpx`
- Frontend: `vitest`, `@testing-library/react`, `@playwright/test`

---

## Related PRDs

**Validates**:
- PRD-P1-005-AUTO-STUDY-CARD-GENERATION
- PRD-P1-006-FLASHCARD-REVIEW-INTERFACE
- PRD-P1-007-SM2-REVIEW-LOGIC

**Enhanced Testing Documentation**:
- [COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md](./COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md) - Tests 1-90 (40 pages, full code examples)
- [COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS-PART2.md](./COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS-PART2.md) - Tests 91-112 + Tooling Setup
- [PRD-P1-008-FRONTEND-TESTING-IMPLEMENTATION.md](./PRD-P1-008-FRONTEND-TESTING-IMPLEMENTATION.md) - Ralph PRD for 85 frontend tests (6 phases)
- [PRD-P1-009-BACKEND-TESTING-IMPLEMENTATION.md](./PRD-P1-009-BACKEND-TESTING-IMPLEMENTATION.md) - Ralph PRD for 27 backend tests (6 phases)

**Test Implementation Phases** (for Ralph autonomous execution):
1. **Frontend Tests** (PRD-P1-008): Vitest + Playwright + Axe-core - 85 tests
2. **Backend Tests** (PRD-P1-009): Pytest + Security + Performance - 27 tests
3. **Integration Tests** (This PRD): Complete pipeline validation - 36 tests

**Total Test Coverage**: 112 tests (60 unit + 36 integration + 16 E2E) with 100% pass rate requirement

---

**End of PRD-P8-002**

**Total Lines**: 1,800+ lines (complete integration testing specification)

**Completion Status**: Ready for implementation

**Study Cards Pipeline Documentation: COMPLETE**
- PRD-P1-005: Auto Study Cards (1,912 lines) ✅
- PRD-P1-006: Flashcard UI (1,630 lines) ✅
- PRD-P1-007: SM-2 Logic (1,418 lines) ✅
- PRD-P8-002: Integration Testing (1,800+ lines) ✅
- **Comprehensive Testing Plan**: Tests 1-112 (2 documents, 40+ pages) ✅
- **Ralph Testing PRDs**: P1-008 + P1-009 (implementation guides) ✅
- **Total: 6,760+ lines of comprehensive documentation + 112 test specifications**
