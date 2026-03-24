# PRD: Frontend Testing Implementation (P1-006 + P1-007 Tests)

**PRD ID**: PRD-P1-008-FRONTEND-TESTING-IMPLEMENTATION
**Category**: Frontend Testing (Vitest, Playwright, Accessibility)
**Priority**: P1-Critical (Validates Frontend Functionality)
**Estimated Effort**: 12-16 hours
**Dependencies**: PRD-P1-006, PRD-P1-007 (code must exist to test)
**Status**: Ready for Implementation
**Assigned Agents**: `react-frontend-developer`, `testing-qa-expert`

**Version**: 1.0
**Created**: 2026-03-24
**Last Updated**: 2026-03-24

---

## R - REQUEST (What & Why)

### Executive Summary

Implement **85 comprehensive frontend tests** covering Flashcard Review Interface (PRD-P1-006) and SM-2 Review Logic (PRD-P1-007) with Vitest unit tests, Playwright E2E tests, and accessibility validation (WCAG 2.2 AA). This PRD ensures zero-tolerance quality enforcement with 100% test pass rate and ≥80% coverage before production deployment.

**Test Breakdown**:
- **40 tests for PRD-P1-006** (Flashcard UI): 28 unit + 8 integration + 4 E2E
- **45 tests for PRD-P1-007** (SM-2 Logic): 32 unit + 10 integration + 3 E2E
- **Total**: 60 unit + 18 integration + 7 E2E = 85 tests

**Business Impact**:
- **Zero production bugs**: Catch UI regressions before deployment
- **Accessibility compliance**: WCAG 2.2 AA enforced (legal requirement)
- **Performance validation**: 60fps animation verified programmatically
- **SM-2 consistency**: TypeScript ↔ Python algorithm match within 0.01
- **Developer confidence**: Automated tests faster than manual QA (3 min vs. 30 min)

**Success Criteria**:
- ✅ 85/85 tests pass (100% pass rate)
- ✅ ≥80% line coverage, ≥75% branch coverage
- ✅ Lighthouse accessibility score ≥95
- ✅ 60fps flip animation (measured in E2E tests)
- ✅ CI/CD integration (tests run on every PR)

---

## A - ARCHITECTURE

### Testing Stack

**Unit Tests** (Vitest + Testing Library):
- **Framework**: Vitest 1.0+ (Vite-native, fast)
- **Component Testing**: @testing-library/react 14+
- **Mocking**: vi.fn(), MSW (Mock Service Worker)
- **Coverage**: V8 provider (built into Vitest)

**Integration Tests** (Vitest + MSW):
- **API Mocking**: MSW for realistic server responses
- **State Management**: Test with React Query
- **Async Testing**: waitFor, renderHook

**E2E Tests** (Playwright):
- **Framework**: Playwright 1.40+
- **Browsers**: Chromium, Firefox, WebKit, Mobile Chrome/Safari
- **Performance Measurement**: Chrome DevTools Protocol
- **Accessibility**: Axe-core + Playwright integration

**Accessibility Tests** (Axe-core + Playwright):
- **Tool**: @axe-core/playwright
- **Standards**: WCAG 2.0 A/AA, WCAG 2.1 AA, WCAG 2.2 AA
- **Coverage**: Keyboard nav, ARIA labels, color contrast, focus management

### File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── study-cards/
│   │       ├── __tests__/                          # Unit tests
│   │       │   ├── FlashcardReview.test.tsx        # 8 tests
│   │       │   ├── FlashcardCard.test.tsx          # 10 tests
│   │       │   ├── NavigationControls.test.tsx     # 5 tests
│   │       │   ├── CitationsList.test.tsx          # 3 tests
│   │       │   ├── LoadingStates.test.tsx          # 2 tests
│   │       │   ├── QualityRating.test.tsx          # 7 tests
│   │       │   ├── FlashcardReview.integration.test.tsx  # 4 tests
│   │       │   ├── Navigation.integration.test.tsx       # 4 tests
│   │       │   └── QualityRating.integration.test.tsx    # 5 tests
│   │       ├── FlashcardReview.tsx
│   │       ├── FlashcardCard.tsx
│   │       ├── NavigationControls.tsx
│   │       ├── CitationsList.tsx
│   │       ├── QualityRating.tsx
│   │       └── FlashcardSkeleton.tsx
│   └── hooks/
│       ├── __tests__/
│       │   ├── useSM2Algorithm.test.ts             # 15 tests
│       │   ├── SM2Consistency.test.ts              # 10 tests
│       │   └── useStudyCardReview.integration.test.ts # 5 tests
│       ├── useSM2Algorithm.ts
│       └── useStudyCardReview.ts
├── tests/
│   ├── e2e/
│   │   ├── flashcard-review.spec.ts                # 4 E2E tests
│   │   ├── sm2-review.spec.ts                      # 3 E2E tests
│   │   └── study-cards-full-pipeline.spec.ts       # (P8-002)
│   ├── accessibility/
│   │   └── flashcard-wcag.spec.ts                  # 7 accessibility tests
│   ├── performance/
│   │   └── flashcard-animation.spec.ts             # 1 performance test
│   └── setup.ts                                    # Global test setup
├── vitest.config.ts                                # Vitest configuration
├── playwright.config.ts                            # Playwright configuration
└── package.json                                    # Test scripts
```

---

## L - LOOP (Iterative Development Phases)

### Phase 1: Vitest Setup + FlashcardReview Unit Tests (3-4 hours)

**Deliverables**:
- Configure Vitest with coverage thresholds (80% line, 75% branch)
- Create test setup file with React Query wrapper, MSW handlers
- Implement `FlashcardReview.test.tsx` (8 tests):
  1. Display loading skeleton while fetching
  2. Display empty state when no cards due
  3. Display first card when data loads
  4. Progress indicator shows correct position
  5. Error state displays when API fails
  6. Retry button refetches data
  7. Handle 401 Unauthorized (redirect to login)
  8. Handle 403 Forbidden with message

**Validation**:
```bash
npm test -- FlashcardReview.test.tsx
# Expected: 8/8 tests PASSED
```

---

### Phase 2: FlashcardCard + Navigation Unit Tests (3-4 hours)

**Deliverables**:
- Implement `FlashcardCard.test.tsx` (10 tests):
  - Show question side initially (answer hidden)
  - "Show Answer" button exists and is accessible
  - Clicking "Show Answer" flips card
  - Spacebar keypress flips card
  - Flip animation uses CSS transform (performance)
  - Long question text wraps correctly
  - Long answer text wraps correctly
  - Citations display with qdrant_point_id
  - Card with no citations shows message
  - Unicode characters display correctly
- Implement `NavigationControls.test.tsx` (5 tests):
  - Previous button disabled on first card
  - Next button disabled on last card
  - Both buttons enabled on middle card
  - Clicking Previous calls callback
  - Arrow keys trigger navigation
- Implement `CitationsList.test.tsx` (3 tests):
  - Display all citations with formatting
  - Validate qdrant_point_id present
  - Sort citations by confidence descending
- Implement `LoadingStates.test.tsx` (2 tests):
  - Skeleton displays placeholders
  - Skeleton has accessible loading announcement

**Validation**:
```bash
npm test -- FlashcardCard.test.tsx NavigationControls.test.tsx CitationsList.test.tsx LoadingStates.test.tsx
# Expected: 20/20 tests PASSED
```

---

### Phase 3: SM-2 Algorithm Unit Tests + Consistency (4-5 hours)

**Deliverables**:
- Implement `useSM2Algorithm.test.ts` (15 tests):
  - Quality 5 ("Perfect") increases ease_factor
  - Quality 4 ("Easy") increases ease_factor slightly
  - Quality 3 ("OK") maintains ease_factor
  - Quality 2 ("Hard") decreases ease_factor
  - Quality 1 ("Wrong") resets repetitions to 0
  - Quality 0 ("Blackout") resets and decreases significantly
  - ease_factor floor is 1.3
  - Interval progression (1 → 6 → exponential)
  - next_review_date calculation correct
  - Handles invalid quality (<0 or >5)
  - Handles negative ease_factor
  - Handles zero interval_days
  - Handles negative repetitions
  - Interval cap (max 365 days)
  - Consistency test (same inputs = same outputs)
- Implement `SM2Consistency.test.ts` (10 tests):
  - Compare TypeScript vs. Python SM-2 results for 10 test cases
  - Verify match within 0.01 tolerance

**Validation**:
```bash
npm test -- useSM2Algorithm.test.ts SM2Consistency.test.ts
# Expected: 25/25 tests PASSED
```

---

### Phase 4: Quality Rating + Integration Tests (3-4 hours)

**Deliverables**:
- Implement `QualityRating.test.tsx` (7 tests):
  - Render 6 quality buttons (0-5)
  - Clicking rating button calls callback
  - Keyboard shortcuts (0-5 keys) trigger ratings
  - Disable buttons while submitting
  - Show loading indicator during submission
  - Display error message on failure
  - Color coding for quality levels
- Implement integration tests (13 tests):
  - `FlashcardReview.integration.test.tsx` (4): API fetching, JWT token, 401 handling, due date filtering
  - `Navigation.integration.test.tsx` (4): Clicking Next/Previous, arrow keys, flip state reset
  - `QualityRating.integration.test.tsx` (5): API submission, next review date display, JWT token, 401 handling, optimistic update

**Validation**:
```bash
npm test -- QualityRating.test.tsx
npm test -- *.integration.test.tsx
# Expected: 20/20 tests PASSED
```

---

### Phase 5: E2E Tests with Playwright (4-5 hours)

**Deliverables**:
- Configure Playwright (chromium, firefox, webkit, mobile)
- Implement `flashcard-review.spec.ts` (4 E2E tests):
  1. Complete flashcard review workflow
  2. Keyboard navigation without mouse
  3. Mobile responsiveness (touch gestures)
  4. Performance - 60fps flip animation
- Implement `sm2-review.spec.ts` (3 E2E tests):
  1. Complete review workflow with quality rating
  2. Keyboard shortcuts for quality ratings
  3. Statistics update after multiple reviews

**Validation**:
```bash
npx playwright test flashcard-review.spec.ts sm2-review.spec.ts
# Expected: 7/7 tests PASSED
```

---

### Phase 6: Accessibility Tests + Final QA (3-4 hours)

**Deliverables**:
- Implement `flashcard-wcag.spec.ts` (7 accessibility tests):
  1. Pass axe accessibility scan
  2. Support keyboard navigation
  3. Have proper ARIA labels
  4. Have sufficient color contrast
  5. Work with screen reader (announcements)
  6. Support high contrast mode
  7. Support zoom up to 200%
- Implement `flashcard-animation.spec.ts` (1 performance test):
  - Maintain 60fps during flip animation
- Run full test suite with coverage
- Fix any failing tests
- Generate coverage report

**Validation**:
```bash
npx playwright test accessibility/
npm test -- --coverage
# Expected: All tests PASSED, coverage ≥80%
```

---

## P - PLAN (Detailed Implementation)

### Phase 1: Vitest Setup + FlashcardReview Unit Tests

#### Step 1.1: Install Dependencies

```bash
cd frontend
npm install -D vitest @vitest/ui @testing-library/react @testing-library/user-event @testing-library/jest-dom jsdom
npm install -D msw
```

#### Step 1.2: Create Vitest Configuration

**File**: `frontend/vitest.config.ts`

```typescript
import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/tests/setup.ts'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html', 'lcov'],
      exclude: [
        'node_modules/',
        'src/tests/',
        '**/*.test.{ts,tsx}',
        '**/*.spec.{ts,tsx}',
        '**/types.ts',
      ],
      thresholds: {
        lines: 80,
        functions: 90,
        branches: 75,
        statements: 80,
      },
    },
    include: ['src/**/*.test.{ts,tsx}'],
    exclude: ['node_modules', 'dist', 'build'],
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
});
```

#### Step 1.3: Create Test Setup File

**File**: `frontend/src/tests/setup.ts`

```typescript
import '@testing-library/jest-dom';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

// Cleanup after each test
afterEach(() => {
  cleanup();
});

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock IntersectionObserver
global.IntersectionObserver = class IntersectionObserver {
  constructor() {}
  disconnect() {}
  observe() {}
  takeRecords() {
    return [];
  }
  unobserve() {}
};
```

#### Step 1.4: Implement FlashcardReview.test.tsx

**File**: `frontend/src/components/study-cards/__tests__/FlashcardReview.test.tsx`

(See COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md, tests 1-8 for full implementation)

---

### Phase 2-6: [Detailed implementation steps continue...]

(Full implementation steps for each phase provided in testing plan documents)

---

## H - HANDOFF (Acceptance Criteria & Testing)

### Acceptance Criteria

**MUST HAVE** (100% Required):
- [ ] **85/85 tests pass** (100% pass rate, zero tolerance for failures)
- [ ] **Coverage ≥80%** (lines), ≥75% (branches), ≥90% (functions)
- [ ] **Vitest configured** with thresholds enforced
- [ ] **Playwright configured** with multi-browser support
- [ ] **MSW configured** for API mocking in integration tests
- [ ] **Accessibility tests pass** (WCAG 2.2 AA, Lighthouse ≥95)
- [ ] **Performance validated** (60fps flip animation measured programmatically)
- [ ] **SM-2 consistency** (TypeScript ↔ Python within 0.01 tolerance)
- [ ] **CI/CD integration** (tests run on every PR, block merge if fail)
- [ ] **0 TypeScript errors** (`npx tsc --noEmit`)
- [ ] **0 Lint errors** (`npm run lint`)

**SHOULD HAVE** (90% Priority):
- [ ] **Test execution time** <3 minutes for full suite
- [ ] **Coverage report** generated as HTML (viewable locally)
- [ ] **Playwright UI mode** works for debugging E2E tests
- [ ] **Watch mode** works for Vitest (hot reload tests)

**NICE TO HAVE** (Optional):
- [ ] **Visual regression tests** (screenshot comparison for UI changes)
- [ ] **Performance regression alerts** (fail if animation drops below 54fps)
- [ ] **Test documentation** (README with common testing patterns)

---

### 3-Layer QA Validation (Phase 6 - MANDATORY FINAL APPROVAL)

#### Layer 1: Agent Self-Validation (`react-frontend-developer` + `testing-qa-expert`)

**Agent MUST run these commands and confirm 0 errors before returning:**

```bash
cd /home/dev/Development/irStudy/frontend

# 1. Run all tests
npm test
# Expected: ✅ 85/85 tests PASSED (100%)

# 2. Generate coverage report
npm test -- --coverage
# Expected: ✅ Coverage ≥80% (lines), ≥75% (branches), ≥90% (functions)

# 3. Run E2E tests
npx playwright test
# Expected: ✅ All E2E tests PASSED

# 4. Run accessibility tests
npx playwright test accessibility/
# Expected: ✅ All accessibility tests PASSED (0 WCAG violations)

# 5. TypeScript type check
npx tsc --noEmit
# Expected: ✅ 0 errors

# 6. Lint check
npm run lint
# Expected: ✅ 0 errors, 0 warnings

# 7. Build production bundle (smoke test)
npm run build
# Expected: ✅ Build succeeds

# 8. Run Lighthouse audit
npm run lighthouse
# Expected: ✅ Accessibility ≥95, Performance ≥90
```

**Agent Checklist** (mark before returning to PM):
- [ ] 85/85 tests PASSED (no flaky tests, deterministic)
- [ ] Coverage meets thresholds (80/75/90)
- [ ] E2E tests pass in all browsers (chromium, firefox, webkit)
- [ ] Accessibility audit passes (0 violations)
- [ ] TypeScript compiles (0 errors)
- [ ] Lint passes (0 errors)
- [ ] Build succeeds (no production warnings)
- [ ] Lighthouse accessibility ≥95

**BLOCKS Phase 6**: If ANY check fails, agent MUST fix immediately and re-run ALL validation commands.

---

#### Layer 2: PM Independent Verification

**PM runs SAME commands (don't trust agent report blindly):**

```bash
cd /home/dev/Development/irStudy/frontend

# 1. Verify tests pass (PM sees with own eyes)
npm test
# Expected: ✅ 85/85 PASSED

# 2. Verify coverage (check HTML report)
npm test -- --coverage
open coverage/index.html  # Visual inspection of coverage
# Expected: ✅ All files ≥80% coverage

# 3. Spot-check critical tests (manual run)
npm test -- FlashcardCard.test.tsx
npm test -- useSM2Algorithm.test.ts
npx playwright test flashcard-review.spec.ts --headed
# Expected: ✅ All pass, visually verify flip animation smooth
```

**PM Checklist**:
- [ ] Tests verified (PM ran npm test, saw 85/85 PASSED)
- [ ] Coverage verified (HTML report shows ≥80% lines)
- [ ] Critical tests spot-checked (FlashcardCard, SM-2 algorithm)
- [ ] E2E tests visually verified (flip animation smooth at 60fps)
- [ ] Code quality reviewed (test structure, naming conventions)
- [ ] No console errors during test runs
- [ ] No suspicious test patterns (setTimeout, hardcoded waits >1s)

**BLOCKS Phase 6**: If PM finds issues, delegate fix back to `testing-qa-expert` with specific error list.

---

#### Layer 3: testing-qa-expert Review

**QA expert runs comprehensive validation before approving phase:**

```bash
cd /home/dev/Development/irStudy/frontend

# 1. Full test suite (stress test)
npm test -- --run --reporter=verbose
# Expected: ✅ 100% pass rate (no flaky failures)

# 2. Coverage validation (deep dive)
npm test -- --coverage --reporter=verbose
# Check specific files:
# - FlashcardReview.tsx: ≥85%
# - FlashcardCard.tsx: ≥85%
# - useSM2Algorithm.ts: ≥90% (critical algorithm)
# - QualityRating.tsx: ≥80%

# 3. E2E cross-browser validation
npx playwright test --project=chromium --project=firefox --project=webkit
# Expected: ✅ All browsers pass

# 4. Accessibility deep scan
npx playwright test accessibility/ --reporter=html
# Review HTML report for violations
# Expected: ✅ 0 violations across all WCAG levels (A, AA, 2.1 AA, 2.2 AA)

# 5. Performance validation
npx playwright test performance/flashcard-animation.spec.ts
# Expected: ✅ avgFPS ≥54, maxFrameTime ≤33ms

# 6. Integration test validation (API mocking)
npm test -- *.integration.test.tsx
# Expected: ✅ All integration tests pass (API mocked correctly)

# 7. SM-2 consistency validation (critical)
npm test -- SM2Consistency.test.ts --reporter=verbose
# Expected: ✅ All 10 test cases match Python within 0.01 tolerance
```

**QA Checklist**:
- [ ] 100% test pass rate (no flaky tests, ran 3 times)
- [ ] Coverage ≥80% (verified in HTML report, all files above threshold)
- [ ] E2E tests pass in all browsers (chromium, firefox, webkit, mobile)
- [ ] Accessibility 0 violations (WCAG 2.2 AA enforced)
- [ ] Performance ≥60fps (flip animation measured programmatically)
- [ ] SM-2 consistency validated (TypeScript ↔ Python match)
- [ ] Integration tests use MSW correctly (no real API calls)
- [ ] Test code follows best practices (no hardcoded timeouts, proper async handling)

**QA Decision**: ✅ APPROVE Phase 6 / ❌ REJECT Phase 6

**BLOCKS Phase 6**: If QA rejects, ENTIRE Phase 6 blocked until all issues resolved and re-validated.

---

### Final Approval Signature

- [ ] PM Sign-Off: _______________ Date: _______
- [ ] testing-qa-expert Sign-Off: _______________ Date: _______

**PRD-P1-008 Status**: ⏳ INCOMPLETE (awaiting QA sign-off) / ✅ COMPLETE (all gates passed)

---

## Validation Commands (Quick Reference)

```bash
# All tests
npm test

# Coverage report
npm test -- --coverage

# Watch mode (development)
npm test -- --watch

# Specific test file
npm test -- FlashcardReview.test.tsx

# E2E tests
npx playwright test

# E2E with UI (debugging)
npx playwright test --ui

# E2E headed mode (visible browser)
npx playwright test --headed

# Accessibility tests
npx playwright test accessibility/

# Performance tests
npx playwright test performance/

# TypeScript check
npx tsc --noEmit

# Lint
npm run lint

# Build
npm run build

# Lighthouse audit
npm run lighthouse
```

---

## Dependencies

**Before testing can begin**:
- [ ] PRD-P1-006 implemented (FlashcardReview, FlashcardCard components exist)
- [ ] PRD-P1-007 implemented (useSM2Algorithm hook exists)
- [ ] Backend API available (P1-005 complete)
- [ ] Test fixtures created (mock data generator)

**External packages required**:
```json
{
  "devDependencies": {
    "vitest": "^1.0.0",
    "@vitest/ui": "^1.0.0",
    "@testing-library/react": "^14.0.0",
    "@testing-library/user-event": "^14.5.0",
    "@testing-library/jest-dom": "^6.1.0",
    "jsdom": "^23.0.0",
    "msw": "^2.0.0",
    "@playwright/test": "^1.40.0",
    "@axe-core/playwright": "^4.8.0",
    "playwright-lighthouse": "^4.0.0"
  }
}
```

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
