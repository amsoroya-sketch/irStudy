# Comprehensive Testing Plan: Study Cards Pipeline

**Document ID**: TESTING-PLAN-STUDY-CARDS-001
**Version**: 1.0
**Created**: 2026-03-24
**Scope**: PRD-P1-006 (Flashcard UI), PRD-P1-007 (SM-2 Logic), PRD-P8-002 (Integration)
**Coverage Target**: 100+ test cases (exhaustive depth)
**Critical Focus**: SM-2 Algorithm, Security/Auth, Performance/Animation, Accessibility

---

## Table of Contents

1. [Test Inventory Summary](#1-test-inventory-summary)
2. [Field-Level Test Matrix](#2-field-level-test-matrix)
3. [PRD-P1-006: Flashcard Review Interface Tests](#3-prd-p1-006-flashcard-review-interface-tests)
4. [PRD-P1-007: SM-2 Review Logic Tests](#4-prd-p1-007-sm2-review-logic-tests)
5. [PRD-P8-002: Integration Testing](#5-prd-p8-002-integration-testing)
6. [Security & Penetration Tests](#6-security--penetration-tests)
7. [Performance Benchmarking](#7-performance-benchmarking)
8. [Accessibility Testing (WCAG 2.2 AA)](#8-accessibility-testing-wcag-22-aa)
9. [Tooling Setup & Configuration](#9-tooling-setup--configuration)
10. [Quality Gates & CI/CD](#10-quality-gates--cicd)

---

## 1. Test Inventory Summary

### Total Test Count: **112 tests**

| Category | Unit Tests | Integration Tests | E2E Tests | Total |
|----------|-----------|-------------------|-----------|-------|
| **PRD-P1-006 (Flashcard UI)** | 28 | 8 | 4 | **40** |
| **PRD-P1-007 (SM-2 Logic)** | 32 | 10 | 3 | **45** |
| **PRD-P8-002 (Integration)** | 0 | 15 | 7 | **22** |
| **Security & Auth** | 0 | 3 | 2 | **5** |
| **TOTAL** | **60** | **36** | **16** | **112** |

### Coverage Targets

- **Line Coverage**: ≥80% (enforced by CI/CD)
- **Branch Coverage**: ≥75%
- **Function Coverage**: ≥90%
- **Critical Path Coverage**: 100% (SM-2 algorithm, auth, card generation)

### Quality Benchmarks

- **Test Pass Rate**: 100% (zero tolerance for failures)
- **Build Time**: <5 minutes (parallel test execution)
- **E2E Test Runtime**: <3 minutes (Playwright parallel mode)
- **Performance**: 60fps animation, <200ms API, <15s pipeline
- **Accessibility**: Lighthouse score ≥95 (WCAG 2.2 AA)

---

## 2. Field-Level Test Matrix

**StudyCard Model Fields** (from `/backend/src/schemas/study_card.py` and database):

| Field | Display Test | Validation Test | Calculation Test | Edge Cases | Security Test | Test Count |
|-------|-------------|----------------|------------------|------------|---------------|------------|
| `id` (PK) | ✓ | ✓ | - | null, negative, duplicate | - | 3 |
| `user_id` | - | ✓ | - | null, invalid, mismatch | Auth check | 4 |
| `session_id` | ✓ | ✓ | - | null, invalid UUID, malformed | SQL injection | 5 |
| `card_id` | ✓ | ✓ | - | null, wrong pattern, duplicate | - | 3 |
| `specialty` | ✓ | ✓ | - | invalid enum, null | - | 3 |
| `topic` | ✓ | ✓ | - | empty, >255 chars, XSS | XSS test | 5 |
| `subtopic` | ✓ | ✓ | - | null (optional), >255 chars | - | 2 |
| `question` | ✓ | ✓ | - | <10 chars, >5000 chars, XSS, unicode | XSS test | 6 |
| `answer` | ✓ | ✓ | - | <10 chars, >5000 chars, XSS, unicode | XSS test | 6 |
| `explanation` | ✓ | ✓ | - | null (optional), >5000 chars | - | 2 |
| `citations` | ✓ | ✓ | - | empty [], >5 items, missing qdrant_point_id | - | 5 |
| `difficulty` | ✓ | ✓ | - | invalid enum, null | - | 3 |
| `tags` | ✓ | ✓ | - | empty [], >10 tags, special chars | - | 3 |
| `card_type` | ✓ | ✓ | - | invalid type, null | - | 2 |
| **SM-2 Parameters** | | | | | | |
| `ease_factor` | ✓ | ✓ | ✓ | <1.3 (floor), >3.0, negative, 0 | - | 6 |
| `interval_days` | ✓ | ✓ | ✓ | 0, negative, >365, 1→6→exponential | - | 7 |
| `repetitions` | ✓ | ✓ | ✓ | negative, very large (>100) | - | 3 |
| `next_review_date` | ✓ | ✓ | ✓ | past date, null, far future (2050) | - | 5 |
| **Timestamps** | | | | | | |
| `created_at` | ✓ | ✓ | - | null, future date | - | 2 |
| `updated_at` | ✓ | ✓ | - | null, before created_at | - | 2 |
| `is_active` | ✓ | ✓ | - | null, toggle state | - | 2 |
| **TOTAL** | | | | | | **79** |

**Additional Non-Field Tests**: 33 (UI interactions, animations, workflows, error handling)

**Grand Total**: 112 tests

---

## 3. PRD-P1-006: Flashcard Review Interface Tests

**Total**: 40 tests (28 unit + 8 integration + 4 E2E)

### 3.1 Component Unit Tests (28 tests)

#### 3.1.1 FlashcardReview Component (8 tests)

**File**: `frontend/src/components/study-cards/__tests__/FlashcardReview.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FlashcardReview } from '../FlashcardReview';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Test 1: Renders loading state initially
describe('FlashcardReview', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('should display loading skeleton while fetching cards', () => {
    render(<FlashcardReview />, { wrapper });

    // Verify skeleton is shown
    expect(screen.getByTestId('flashcard-skeleton')).toBeInTheDocument();
    expect(screen.queryByTestId('flashcard-card')).not.toBeInTheDocument();
  });

  // Test 2: Renders empty state when no cards due
  it('should display empty state when no cards are due for review', async () => {
    // Mock API to return empty array
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ cards: [], count: 0 }),
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/no cards due for review/i)).toBeInTheDocument();
      expect(screen.getByText(/check back tomorrow/i)).toBeInTheDocument();
    });
  });

  // Test 3: Renders first card when data loads
  it('should display first card when cards are fetched successfully', async () => {
    const mockCards = [
      {
        id: 1,
        question: 'What is the SOCRATES framework?',
        answer: 'Pain assessment framework...',
        citations: [
          {
            source: 'Talley & O\'Connor Clinical Examination 9th Ed',
            qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
            confidence: 0.85,
            page: 412,
          },
        ],
        ease_factor: 2.5,
        interval_days: 1,
        repetitions: 0,
        next_review_date: new Date().toISOString(),
      },
    ];

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ cards: mockCards, count: 1 }),
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      // Verify question side is shown (not answer initially)
      expect(screen.getByText('What is the SOCRATES framework?')).toBeInTheDocument();
      expect(screen.queryByText('Pain assessment framework')).not.toBeInTheDocument();

      // Verify "Show Answer" button exists
      expect(screen.getByRole('button', { name: /show answer/i })).toBeInTheDocument();
    });
  });

  // Test 4: Progress indicator shows correct position
  it('should display progress indicator with correct card position', async () => {
    const mockCards = [
      { id: 1, question: 'Q1', answer: 'A1', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
      { id: 2, question: 'Q2', answer: 'A2', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
      { id: 3, question: 'Q3', answer: 'A3', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
    ];

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({ cards: mockCards, count: 3 }),
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      // Verify progress shows "1 of 3"
      expect(screen.getByText(/card 1 of 3/i)).toBeInTheDocument();
    });
  });

  // Test 5: Error state displays when API fails
  it('should display error state when API call fails', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'));

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/failed to load cards/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });
  });

  // Test 6: Retry button refetches data
  it('should refetch cards when retry button is clicked', async () => {
    const fetchMock = vi.fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ cards: [{ id: 1, question: 'Q1', answer: 'A1', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() }], count: 1 }),
      });

    global.fetch = fetchMock;

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/failed to load cards/i)).toBeInTheDocument();
    });

    const retryButton = screen.getByRole('button', { name: /retry/i });
    await userEvent.click(retryButton);

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });
  });

  // Test 7: Handles unauthorized (401) error
  it('should redirect to login when 401 Unauthorized received', async () => {
    const mockNavigate = vi.fn();
    vi.mock('react-router-dom', () => ({
      useNavigate: () => mockNavigate,
    }));

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: async () => ({ detail: 'Unauthorized' }),
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  // Test 8: Handles forbidden (403) error with message
  it('should display permission error when 403 Forbidden received', async () => {
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: false,
      status: 403,
      json: async () => ({ detail: 'You do not own this session' }),
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/permission denied/i)).toBeInTheDocument();
      expect(screen.getByText(/you do not own this session/i)).toBeInTheDocument();
    });
  });
});
```

#### 3.1.2 FlashcardCard Component (10 tests)

**File**: `frontend/src/components/study-cards/__tests__/FlashcardCard.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FlashcardCard } from '../FlashcardCard';

describe('FlashcardCard - Flip Animation & Display', () => {
  const mockCard = {
    id: 1,
    question: 'What is the SOCRATES framework for pain assessment?',
    answer: 'SOCRATES is a mnemonic for systematic pain assessment: Site, Onset, Character, Radiation, Associations, Time course, Exacerbating/relieving factors, Severity.',
    citations: [
      {
        source: 'Talley & O\'Connor Clinical Examination 9th Ed',
        qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
        confidence: 0.85,
        page: 412,
      },
    ],
    ease_factor: 2.5,
    interval_days: 1,
    repetitions: 0,
    next_review_date: new Date().toISOString(),
  };

  // Test 9: Shows question side initially (answer hidden)
  it('should display question side initially with answer hidden', () => {
    render(<FlashcardCard card={mockCard} />);

    expect(screen.getByText(/What is the SOCRATES framework/i)).toBeInTheDocument();
    expect(screen.queryByText(/SOCRATES is a mnemonic/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId('citation-list')).not.toBeInTheDocument();
  });

  // Test 10: "Show Answer" button exists and is accessible
  it('should have accessible "Show Answer" button', () => {
    render(<FlashcardCard card={mockCard} />);

    const showAnswerBtn = screen.getByRole('button', { name: /show answer/i });
    expect(showAnswerBtn).toBeInTheDocument();
    expect(showAnswerBtn).toHaveAttribute('aria-label', 'Show answer');
    expect(showAnswerBtn).toHaveAttribute('aria-pressed', 'false');
  });

  // Test 11: Clicking "Show Answer" flips card (reveals answer)
  it('should flip card to show answer when "Show Answer" is clicked', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    const showAnswerBtn = screen.getByRole('button', { name: /show answer/i });
    await user.click(showAnswerBtn);

    // Wait for flip animation (0.6s)
    await waitFor(() => {
      expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeInTheDocument();
      expect(screen.getByTestId('citation-list')).toBeInTheDocument();
    }, { timeout: 1000 });

    // Verify question is hidden after flip
    expect(screen.queryByText(/What is the SOCRATES framework/i)).not.toBeInTheDocument();
  });

  // Test 12: Spacebar keypress flips card (keyboard shortcut)
  it('should flip card when spacebar is pressed', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    // Press spacebar
    await user.keyboard(' ');

    await waitFor(() => {
      expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeInTheDocument();
    }, { timeout: 1000 });
  });

  // Test 13: Flip animation uses CSS transform (60fps target)
  it('should use CSS transform for flip animation (performance)', () => {
    const { container } = render(<FlashcardCard card={mockCard} />);

    const cardElement = container.querySelector('[data-testid="flashcard-card-inner"]');
    expect(cardElement).toHaveStyle({
      transition: 'transform 0.6s',
      transformStyle: 'preserve-3d',
    });
  });

  // Test 14: Long question text wraps correctly (no overflow)
  it('should wrap long question text without horizontal scroll', () => {
    const longQuestion = 'A'.repeat(500); // 500 characters
    const cardWithLongQ = { ...mockCard, question: longQuestion };

    const { container } = render(<FlashcardCard card={cardWithLongQ} />);

    const questionElement = screen.getByText(longQuestion);
    const computedStyle = window.getComputedStyle(questionElement);

    expect(computedStyle.overflowWrap).toBe('break-word');
    expect(computedStyle.wordBreak).toMatch(/break-word|break-all/);
  });

  // Test 15: Long answer text wraps correctly
  it('should wrap long answer text without horizontal scroll', async () => {
    const user = userEvent.setup();
    const longAnswer = 'B'.repeat(1000); // 1000 characters
    const cardWithLongA = { ...mockCard, answer: longAnswer };

    render(<FlashcardCard card={cardWithLongA} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      const answerElement = screen.getByText(longAnswer);
      const computedStyle = window.getComputedStyle(answerElement);

      expect(computedStyle.overflowWrap).toBe('break-word');
    });
  });

  // Test 16: Citations display correctly with qdrant_point_id
  it('should display citations with source, page, and confidence', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      expect(screen.getByText(/Talley & O'Connor/i)).toBeInTheDocument();
      expect(screen.getByText(/p\. 412/i)).toBeInTheDocument();
      expect(screen.getByText(/85% confidence/i)).toBeInTheDocument();
    });
  });

  // Test 17: Card with no citations shows "No citations available"
  it('should display "No citations" message when citations array is empty', async () => {
    const user = userEvent.setup();
    const cardNoCitations = { ...mockCard, citations: [] };

    render(<FlashcardCard card={cardNoCitations} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      expect(screen.getByText(/no citations available/i)).toBeInTheDocument();
    });
  });

  // Test 18: Card with special characters (unicode) displays correctly
  it('should display unicode characters correctly (Chinese, emoji, math symbols)', () => {
    const unicodeCard = {
      ...mockCard,
      question: '心脏检查 (Cardiac Examination) 🫀',
      answer: 'α-blocker contraindicated in acute MI ≤48h',
    };

    render(<FlashcardCard card={unicodeCard} />);

    expect(screen.getByText(/心脏检查/)).toBeInTheDocument();
    expect(screen.getByText(/🫀/)).toBeInTheDocument();
  });
});
```

#### 3.1.3 Navigation Controls (5 tests)

**File**: `frontend/src/components/study-cards/__tests__/NavigationControls.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NavigationControls } from '../NavigationControls';

describe('NavigationControls - Previous/Next Buttons', () => {
  // Test 19: Previous button disabled on first card
  it('should disable "Previous" button when on first card', () => {
    render(
      <NavigationControls
        currentCardIndex={0}
        totalCards={5}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />
    );

    const prevButton = screen.getByRole('button', { name: /previous/i });
    expect(prevButton).toBeDisabled();
    expect(prevButton).toHaveAttribute('aria-disabled', 'true');
  });

  // Test 20: Next button disabled on last card
  it('should disable "Next" button when on last card', () => {
    render(
      <NavigationControls
        currentCardIndex={4}
        totalCards={5}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).toBeDisabled();
    expect(nextButton).toHaveAttribute('aria-disabled', 'true');
  });

  // Test 21: Both buttons enabled on middle card
  it('should enable both buttons when on middle card', () => {
    render(
      <NavigationControls
        currentCardIndex={2}
        totalCards={5}
        onPrevious={vi.fn()}
        onNext={vi.fn()}
      />
    );

    expect(screen.getByRole('button', { name: /previous/i })).not.toBeDisabled();
    expect(screen.getByRole('button', { name: /next/i })).not.toBeDisabled();
  });

  // Test 22: Clicking Previous calls onPrevious callback
  it('should call onPrevious when "Previous" button is clicked', async () => {
    const user = userEvent.setup();
    const onPreviousMock = vi.fn();

    render(
      <NavigationControls
        currentCardIndex={2}
        totalCards={5}
        onPrevious={onPreviousMock}
        onNext={vi.fn()}
      />
    );

    await user.click(screen.getByRole('button', { name: /previous/i }));
    expect(onPreviousMock).toHaveBeenCalledTimes(1);
  });

  // Test 23: Arrow keys trigger navigation (keyboard shortcuts)
  it('should navigate with arrow keys (left=previous, right=next)', async () => {
    const user = userEvent.setup();
    const onPreviousMock = vi.fn();
    const onNextMock = vi.fn();

    render(
      <NavigationControls
        currentCardIndex={2}
        totalCards={5}
        onPrevious={onPreviousMock}
        onNext={onNextMock}
      />
    );

    // Press left arrow
    await user.keyboard('{ArrowLeft}');
    expect(onPreviousMock).toHaveBeenCalledTimes(1);

    // Press right arrow
    await user.keyboard('{ArrowRight}');
    expect(onNextMock).toHaveBeenCalledTimes(1);
  });
});
```

#### 3.1.4 CitationsList Component (3 tests)

**File**: `frontend/src/components/study-cards/__tests__/CitationsList.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { CitationsList } from '../CitationsList';

describe('CitationsList - RAG Citation Display', () => {
  const mockCitations = [
    {
      source: 'Talley & O\'Connor Clinical Examination 9th Ed',
      qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
      confidence: 0.85,
      page: 412,
    },
    {
      source: 'eTG Complete (Australian Guidelines)',
      qdrant_point_id: '550e8400-e29b-41d4-a716-446655440001',
      confidence: 0.92,
      page: 156,
    },
  ];

  // Test 24: Displays all citations with correct formatting
  it('should display all citations with source, page, and confidence', () => {
    render(<CitationsList citations={mockCitations} />);

    expect(screen.getByText(/Talley & O'Connor/i)).toBeInTheDocument();
    expect(screen.getByText(/p\. 412/i)).toBeInTheDocument();
    expect(screen.getByText(/85%/i)).toBeInTheDocument();

    expect(screen.getByText(/eTG Complete/i)).toBeInTheDocument();
    expect(screen.getByText(/p\. 156/i)).toBeInTheDocument();
    expect(screen.getByText(/92%/i)).toBeInTheDocument();
  });

  // Test 25: Validates qdrant_point_id is present (critical for RAG)
  it('should only display citations with valid qdrant_point_id', () => {
    const invalidCitations = [
      ...mockCitations,
      {
        source: 'Invalid Source',
        qdrant_point_id: null, // Missing qdrant_point_id
        confidence: 0.75,
        page: 200,
      },
    ];

    render(<CitationsList citations={invalidCitations} />);

    // Verify invalid citation is NOT displayed
    expect(screen.queryByText(/Invalid Source/i)).not.toBeInTheDocument();

    // Verify valid citations ARE displayed
    expect(screen.getByText(/Talley & O'Connor/i)).toBeInTheDocument();
    expect(screen.getByText(/eTG Complete/i)).toBeInTheDocument();
  });

  // Test 26: Sorts citations by confidence (highest first)
  it('should sort citations by confidence descending (highest first)', () => {
    render(<CitationsList citations={mockCitations} />);

    const citationElements = screen.getAllByTestId('citation-item');

    // First citation should be eTG (92% confidence)
    expect(citationElements[0]).toHaveTextContent(/eTG Complete/i);
    expect(citationElements[0]).toHaveTextContent(/92%/i);

    // Second citation should be Talley (85% confidence)
    expect(citationElements[1]).toHaveTextContent(/Talley & O'Connor/i);
    expect(citationElements[1]).toHaveTextContent(/85%/i);
  });
});
```

#### 3.1.5 Loading States (2 tests)

**File**: `frontend/src/components/study-cards/__tests__/LoadingStates.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FlashcardSkeleton } from '../FlashcardSkeleton';

describe('Loading States - Skeleton UI', () => {
  // Test 27: Skeleton displays placeholder content
  it('should display skeleton placeholders while loading', () => {
    render(<FlashcardSkeleton />);

    expect(screen.getByTestId('flashcard-skeleton')).toBeInTheDocument();
    expect(screen.getByTestId('skeleton-question')).toBeInTheDocument();
    expect(screen.getByTestId('skeleton-button')).toBeInTheDocument();
  });

  // Test 28: Skeleton has accessible loading announcement
  it('should announce loading state to screen readers', () => {
    render(<FlashcardSkeleton />);

    const skeleton = screen.getByTestId('flashcard-skeleton');
    expect(skeleton).toHaveAttribute('aria-busy', 'true');
    expect(skeleton).toHaveAttribute('aria-label', 'Loading flashcards');
  });
});
```

---

### 3.2 Integration Tests (8 tests)

#### 3.2.1 FlashcardReview + API Integration (4 tests)

**File**: `frontend/src/components/study-cards/__tests__/FlashcardReview.integration.test.tsx`

```typescript
import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { FlashcardReview } from '../FlashcardReview';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Mock Service Worker (MSW) for API mocking
const server = setupServer(
  rest.get('/api/v1/study-cards', (req, res, ctx) => {
    return res(
      ctx.json({
        cards: [
          {
            id: 1,
            question: 'What is SOCRATES?',
            answer: 'Pain assessment framework',
            citations: [],
            ease_factor: 2.5,
            interval_days: 1,
            repetitions: 0,
            next_review_date: new Date().toISOString(),
          },
        ],
        count: 1,
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('FlashcardReview + API Integration', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  // Test 29: Fetches cards from API on mount
  it('should fetch cards from /api/v1/study-cards on component mount', async () => {
    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('What is SOCRATES?')).toBeInTheDocument();
    });
  });

  // Test 30: Includes JWT token in Authorization header
  it('should include JWT token in Authorization header', async () => {
    let authHeader: string | null = null;

    server.use(
      rest.get('/api/v1/study-cards', (req, res, ctx) => {
        authHeader = req.headers.get('Authorization');
        return res(ctx.json({ cards: [], count: 0 }));
      })
    );

    // Mock localStorage with JWT
    localStorage.setItem('access_token', 'fake-jwt-token');

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(authHeader).toBe('Bearer fake-jwt-token');
    });
  });

  // Test 31: Handles 401 Unauthorized and redirects to login
  it('should redirect to /login when 401 Unauthorized received', async () => {
    server.use(
      rest.get('/api/v1/study-cards', (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({ detail: 'Unauthorized' }));
      })
    );

    const mockNavigate = vi.fn();
    vi.mock('react-router-dom', () => ({
      useNavigate: () => mockNavigate,
    }));

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  // Test 32: Filters cards by due date (next_review_date <= NOW)
  it('should only display cards where next_review_date <= NOW', async () => {
    const now = new Date();
    const tomorrow = new Date(now.getTime() + 24 * 60 * 60 * 1000);

    server.use(
      rest.get('/api/v1/study-cards', (req, res, ctx) => {
        return res(
          ctx.json({
            cards: [
              { id: 1, question: 'Due today', next_review_date: now.toISOString(), answer: 'A1', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0 },
              { id: 2, question: 'Due tomorrow', next_review_date: tomorrow.toISOString(), answer: 'A2', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0 },
            ],
            count: 2,
          })
        );
      })
    );

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      // Only "Due today" card should be shown
      expect(screen.getByText('Due today')).toBeInTheDocument();
      expect(screen.queryByText('Due tomorrow')).not.toBeInTheDocument();
    });
  });
});
```

#### 3.2.2 Navigation + State Management (4 tests)

**File**: `frontend/src/components/study-cards/__tests__/Navigation.integration.test.tsx`

```typescript
import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FlashcardReview } from '../FlashcardReview';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('Navigation + State Management Integration', () => {
  const mockCards = [
    { id: 1, question: 'Q1', answer: 'A1', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
    { id: 2, question: 'Q2', answer: 'A2', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
    { id: 3, question: 'Q3', answer: 'A3', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
  ];

  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ cards: mockCards, count: 3 }),
    });
  });

  // Test 33: Clicking "Next" advances to next card
  it('should advance to next card when "Next" button is clicked', async () => {
    const user = userEvent.setup();
    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
      expect(screen.getByText(/card 1 of 3/i)).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText('Q2')).toBeInTheDocument();
      expect(screen.getByText(/card 2 of 3/i)).toBeInTheDocument();
    });
  });

  // Test 34: Clicking "Previous" goes back to previous card
  it('should go back to previous card when "Previous" button is clicked', async () => {
    const user = userEvent.setup();
    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
    });

    // Navigate to card 2
    await user.click(screen.getByRole('button', { name: /next/i }));

    await waitFor(() => {
      expect(screen.getByText('Q2')).toBeInTheDocument();
    });

    // Go back to card 1
    await user.click(screen.getByRole('button', { name: /previous/i }));

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
      expect(screen.getByText(/card 1 of 3/i)).toBeInTheDocument();
    });
  });

  // Test 35: Arrow keys navigate between cards
  it('should navigate with arrow keys (ArrowRight=next, ArrowLeft=previous)', async () => {
    const user = userEvent.setup();
    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
    });

    // Press ArrowRight to go to Q2
    await user.keyboard('{ArrowRight}');

    await waitFor(() => {
      expect(screen.getByText('Q2')).toBeInTheDocument();
    });

    // Press ArrowLeft to go back to Q1
    await user.keyboard('{ArrowLeft}');

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
    });
  });

  // Test 36: Flip state resets when navigating to new card
  it('should reset flip state (show question) when navigating to new card', async () => {
    const user = userEvent.setup();
    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText('Q1')).toBeInTheDocument();
    });

    // Flip card 1 to show answer
    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      expect(screen.getByText('A1')).toBeInTheDocument();
    });

    // Navigate to card 2
    await user.keyboard('{ArrowRight}');

    await waitFor(() => {
      // Card 2 should show question side (not flipped)
      expect(screen.getByText('Q2')).toBeInTheDocument();
      expect(screen.queryByText('A2')).not.toBeInTheDocument();
      expect(screen.getByRole('button', { name: /show answer/i })).toBeInTheDocument();
    });
  });
});
```

---

### 3.3 E2E Tests (4 tests)

**File**: `frontend/tests/e2e/flashcard-review.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('Flashcard Review E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  // Test 37: Complete flashcard review workflow
  test('should complete full flashcard review workflow', async ({ page }) => {
    // Navigate to study cards
    await page.goto('/study-cards/review');

    // Wait for cards to load
    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Verify question is shown
    await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

    // Click "Show Answer"
    await page.click('button:has-text("Show Answer")');

    // Wait for flip animation (0.6s)
    await page.waitForTimeout(700);

    // Verify answer is shown
    await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

    // Verify citations are shown
    await expect(page.locator('[data-testid="citation-list"]')).toBeVisible();

    // Navigate to next card
    await page.keyboard.press('ArrowRight');

    // Verify progress updated
    await expect(page.locator('text=/card 2 of/i')).toBeVisible();
  });

  // Test 38: Keyboard navigation without mouse
  test('should support full keyboard navigation (accessibility)', async ({ page }) => {
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Tab to "Show Answer" button
    await page.keyboard.press('Tab');
    await expect(page.locator('button:has-text("Show Answer")')).toBeFocused();

    // Press spacebar to flip
    await page.keyboard.press('Space');

    await page.waitForTimeout(700);

    // Verify answer is shown
    await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

    // Press ArrowRight to next card
    await page.keyboard.press('ArrowRight');

    // Verify new card shown
    await expect(page.locator('text=/card 2 of/i')).toBeVisible();
  });

  // Test 39: Mobile responsiveness (touch gestures)
  test('should work on mobile viewport with touch', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 }); // iPhone SE

    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Tap "Show Answer" button
    await page.locator('button:has-text("Show Answer")').tap();

    await page.waitForTimeout(700);

    // Verify answer is shown
    await expect(page.locator('[data-testid="flashcard-answer"]')).toBeVisible();

    // Swipe left to right (next card) - simulate touch swipe
    const card = page.locator('[data-testid="flashcard-card"]');
    const box = await card.boundingBox();
    if (box) {
      await page.touchscreen.tap(box.x + 50, box.y + box.height / 2);
      await page.touchscreen.swipe(
        { x: box.x + 50, y: box.y + box.height / 2 },
        { x: box.x + box.width - 50, y: box.y + box.height / 2 }
      );
    }

    // Verify next card shown
    await expect(page.locator('text=/card 2 of/i')).toBeVisible();
  });

  // Test 40: Performance - 60fps flip animation
  test('should maintain 60fps during flip animation', async ({ page }) => {
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Start performance measurement
    await page.evaluate(() => {
      (window as any).performanceData = [];
      let lastTime = performance.now();

      function measureFrame() {
        const now = performance.now();
        const delta = now - lastTime;
        (window as any).performanceData.push(delta);
        lastTime = now;

        if ((window as any).performanceData.length < 60) {
          requestAnimationFrame(measureFrame);
        }
      }

      requestAnimationFrame(measureFrame);
    });

    // Trigger flip animation
    await page.click('button:has-text("Show Answer")');

    // Wait for animation to complete
    await page.waitForTimeout(700);

    // Analyze frame times
    const performanceData = await page.evaluate(() => (window as any).performanceData);

    // Calculate FPS
    const avgFrameTime = performanceData.reduce((a: number, b: number) => a + b, 0) / performanceData.length;
    const avgFPS = 1000 / avgFrameTime;

    // Assert ≥60fps (allowing 10% margin: ≥54fps)
    expect(avgFPS).toBeGreaterThanOrEqual(54);

    // Verify no dropped frames (no frame took >33ms = <30fps)
    const maxFrameTime = Math.max(...performanceData);
    expect(maxFrameTime).toBeLessThanOrEqual(33);
  });
});
```

---

## 4. PRD-P1-007: SM-2 Review Logic Tests

**Total**: 45 tests (32 unit + 10 integration + 3 E2E)

### 4.1 SM-2 Algorithm Unit Tests (32 tests)

#### 4.1.1 SM-2 Calculation Core (15 tests)

**File**: `frontend/src/hooks/__tests__/useSM2Algorithm.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSM2Algorithm } from '../useSM2Algorithm';

describe('SM-2 Algorithm Calculations', () => {
  // Test 41: Quality 5 ("Perfect") increases ease_factor
  it('should increase ease_factor when quality=5 (Perfect)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 5);

    // EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    // EF' = 2.5 + (0.1 - 0 * 0.08) = 2.5 + 0.1 = 2.6
    expect(newParams.ease_factor).toBeCloseTo(2.6, 2);
    expect(newParams.interval_days).toBe(6); // First repetition: 6 days
    expect(newParams.repetitions).toBe(1);
  });

  // Test 42: Quality 4 ("Easy") increases ease_factor slightly
  it('should increase ease_factor slightly when quality=4 (Easy)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 4);

    // EF' = 2.5 + (0.1 - 1 * (0.08 + 1 * 0.02)) = 2.5 + (0.1 - 0.1) = 2.5
    expect(newParams.ease_factor).toBeCloseTo(2.5, 2);
    expect(newParams.interval_days).toBe(6);
    expect(newParams.repetitions).toBe(1);
  });

  // Test 43: Quality 3 ("OK") maintains ease_factor
  it('should maintain ease_factor when quality=3 (OK)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 3);

    // EF' = 2.5 + (0.1 - 2 * (0.08 + 2 * 0.02)) = 2.5 + (0.1 - 0.24) = 2.36
    expect(newParams.ease_factor).toBeCloseTo(2.36, 2);
    expect(newParams.interval_days).toBe(6);
    expect(newParams.repetitions).toBe(1);
  });

  // Test 44: Quality 2 ("Hard") decreases ease_factor
  it('should decrease ease_factor when quality=2 (Hard)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 2);

    // EF' = 2.5 + (0.1 - 3 * (0.08 + 3 * 0.02)) = 2.5 + (0.1 - 0.42) = 2.18
    expect(newParams.ease_factor).toBeCloseTo(2.18, 2);
    expect(newParams.interval_days).toBe(6);
    expect(newParams.repetitions).toBe(1);
  });

  // Test 45: Quality 1 ("Wrong") resets repetitions to 0
  it('should reset repetitions to 0 when quality=1 (Wrong)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 6,
      repetitions: 2, // Was on 2nd repetition
    };

    const newParams = result.current.calculateNext(initialParams, 1);

    // EF' = 2.5 + (0.1 - 4 * (0.08 + 4 * 0.02)) = 2.5 + (0.1 - 0.64) = 1.96
    expect(newParams.ease_factor).toBeCloseTo(1.96, 2);
    expect(newParams.interval_days).toBe(1); // Reset to 1 day
    expect(newParams.repetitions).toBe(0); // Reset
  });

  // Test 46: Quality 0 ("Blackout") resets and decreases ease_factor significantly
  it('should reset and decrease ease_factor significantly when quality=0 (Blackout)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 6,
      repetitions: 2,
    };

    const newParams = result.current.calculateNext(initialParams, 0);

    // EF' = 2.5 + (0.1 - 5 * (0.08 + 5 * 0.02)) = 2.5 + (0.1 - 0.9) = 1.7
    expect(newParams.ease_factor).toBeCloseTo(1.7, 2);
    expect(newParams.interval_days).toBe(1);
    expect(newParams.repetitions).toBe(0);
  });

  // Test 47: ease_factor floor is 1.3 (never goes below)
  it('should enforce ease_factor floor of 1.3 (never below)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 1.4, // Close to floor
      interval_days: 1,
      repetitions: 0,
    };

    // Quality 0 would normally decrease to 0.6, but floor is 1.3
    const newParams = result.current.calculateNext(initialParams, 0);

    expect(newParams.ease_factor).toBeGreaterThanOrEqual(1.3);
    expect(newParams.ease_factor).toBeCloseTo(1.3, 2);
  });

  // Test 48: Interval progression (1 → 6 → exponential)
  it('should progress intervals correctly (1 → 6 → 13 → 29...)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    // First review (quality 4)
    let params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    params = result.current.calculateNext(params, 4);
    expect(params.interval_days).toBe(6); // First repetition
    expect(params.repetitions).toBe(1);

    // Second review (quality 4)
    params = result.current.calculateNext(params, 4);
    // I(2) = I(1) * EF = 6 * 2.5 = 15 (rounds to 15)
    expect(params.interval_days).toBeCloseTo(15, 0);
    expect(params.repetitions).toBe(2);

    // Third review (quality 4)
    params = result.current.calculateNext(params, 4);
    // I(3) = I(2) * EF = 15 * 2.5 = 37.5 (rounds to 38)
    expect(params.interval_days).toBeCloseTo(38, 0);
    expect(params.repetitions).toBe(3);
  });

  // Test 49: next_review_date calculation (adds interval_days to NOW)
  it('should calculate next_review_date correctly (NOW + interval_days)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const now = new Date();
    const newParams = result.current.calculateNext(params, 4);

    const expectedDate = new Date(now.getTime() + 6 * 24 * 60 * 60 * 1000); // +6 days

    expect(newParams.next_review_date).toBeInstanceOf(Date);
    expect(newParams.next_review_date.getTime()).toBeCloseTo(expectedDate.getTime(), -4); // Allow 10s tolerance
  });

  // Test 50: Handles invalid quality (out of range 0-5)
  it('should throw error for quality <0 or >5', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(params, -1)).toThrow(/quality must be between 0 and 5/i);
    expect(() => result.current.calculateNext(params, 6)).toThrow(/quality must be between 0 and 5/i);
  });

  // Test 51: Handles negative ease_factor (invalid state)
  it('should throw error for negative ease_factor', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: -1.0,
      interval_days: 1,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/ease_factor must be >= 1.3/i);
  });

  // Test 52: Handles zero interval_days (invalid state)
  it('should throw error for interval_days <= 0', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: 2.5,
      interval_days: 0,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/interval_days must be >= 1/i);
  });

  // Test 53: Handles negative repetitions (invalid state)
  it('should throw error for negative repetitions', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: -1,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/repetitions must be >= 0/i);
  });

  // Test 54: Interval cap (max 365 days for safety)
  it('should cap interval at 365 days (prevent year+ intervals)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    let params = {
      ease_factor: 3.0, // High EF
      interval_days: 200, // Already high
      repetitions: 5,
    };

    // Quality 5 would normally push interval to 600 days
    params = result.current.calculateNext(params, 5);

    expect(params.interval_days).toBeLessThanOrEqual(365);
  });

  // Test 55: Consistency test (same inputs = same outputs)
  it('should return identical results for identical inputs (deterministic)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const result1 = result.current.calculateNext(params, 4);
    const result2 = result.current.calculateNext(params, 4);

    expect(result1.ease_factor).toBeCloseTo(result2.ease_factor, 10);
    expect(result1.interval_days).toBe(result2.interval_days);
    expect(result1.repetitions).toBe(result2.repetitions);
  });
});
```

#### 4.1.2 TypeScript ↔ Python Consistency Tests (10 tests)

**File**: `frontend/src/hooks/__tests__/SM2Consistency.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSM2Algorithm } from '../useSM2Algorithm';

describe('SM-2 TypeScript ↔ Python Consistency', () => {
  // Test 56-65: Compare TypeScript vs Python SM-2 results (10 test cases)

  const testCases = [
    {
      name: 'Initial card (q=5)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 5 },
      expected_python: { ease_factor: 2.6, interval_days: 6, repetitions: 1 },
    },
    {
      name: 'Initial card (q=4)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 4 },
      expected_python: { ease_factor: 2.5, interval_days: 6, repetitions: 1 },
    },
    {
      name: 'Initial card (q=3)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 3 },
      expected_python: { ease_factor: 2.36, interval_days: 6, repetitions: 1 },
    },
    {
      name: 'Initial card (q=2)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 2 },
      expected_python: { ease_factor: 2.18, interval_days: 6, repetitions: 1 },
    },
    {
      name: 'Initial card (q=1)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 1 },
      expected_python: { ease_factor: 1.96, interval_days: 1, repetitions: 0 },
    },
    {
      name: 'Initial card (q=0)',
      input: { ease_factor: 2.5, interval_days: 1, repetitions: 0, quality: 0 },
      expected_python: { ease_factor: 1.7, interval_days: 1, repetitions: 0 },
    },
    {
      name: 'Second repetition (q=5)',
      input: { ease_factor: 2.6, interval_days: 6, repetitions: 1, quality: 5 },
      expected_python: { ease_factor: 2.7, interval_days: 16, repetitions: 2 }, // 6 * 2.6 = 15.6 → 16
    },
    {
      name: 'Third repetition (q=4)',
      input: { ease_factor: 2.6, interval_days: 16, repetitions: 2, quality: 4 },
      expected_python: { ease_factor: 2.6, interval_days: 42, repetitions: 3 }, // 16 * 2.6 = 41.6 → 42
    },
    {
      name: 'ease_factor floor test (q=0)',
      input: { ease_factor: 1.5, interval_days: 1, repetitions: 0, quality: 0 },
      expected_python: { ease_factor: 1.3, interval_days: 1, repetitions: 0 }, // 1.5 - 0.8 = 0.7 → floor 1.3
    },
    {
      name: 'High repetition (q=5)',
      input: { ease_factor: 2.8, interval_days: 100, repetitions: 10, quality: 5 },
      expected_python: { ease_factor: 2.9, interval_days: 280, repetitions: 11 }, // 100 * 2.8 = 280
    },
  ];

  testCases.forEach((testCase, index) => {
    it(`Test ${index + 56}: ${testCase.name} - TypeScript matches Python within 0.01 tolerance`, () => {
      const { result } = renderHook(() => useSM2Algorithm());

      const { ease_factor, interval_days, repetitions, quality } = testCase.input;

      const tsResult = result.current.calculateNext(
        { ease_factor, interval_days, repetitions },
        quality
      );

      // Compare with Python expected values (tolerance: 0.01)
      expect(tsResult.ease_factor).toBeCloseTo(testCase.expected_python.ease_factor, 2);
      expect(tsResult.interval_days).toBeCloseTo(testCase.expected_python.interval_days, 0);
      expect(tsResult.repetitions).toBe(testCase.expected_python.repetitions);
    });
  });
});
```

#### 4.1.3 QualityRating Component (7 tests)

**File**: `frontend/src/components/study-cards/__tests__/QualityRating.test.tsx`

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QualityRating } from '../QualityRating';

describe('QualityRating Component', () => {
  // Test 66: Renders 6 quality buttons (0-5)
  it('should render 6 quality rating buttons (0-5)', () => {
    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />);

    expect(screen.getByRole('button', { name: /0.*blackout/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /1.*wrong/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /2.*hard/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /3.*ok/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /4.*easy/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /5.*perfect/i })).toBeInTheDocument();
  });

  // Test 67: Clicking rating button calls callback with quality value
  it('should call onRatingSubmit with quality value when button clicked', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn();

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />);

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    expect(onRatingSubmitMock).toHaveBeenCalledWith(1, 4); // cardId=1, quality=4
  });

  // Test 68: Keyboard shortcuts (0-5 keys) trigger ratings
  it('should support keyboard shortcuts (pressing 0-5 keys)', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn();

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />);

    await user.keyboard('4'); // Press "4" key

    expect(onRatingSubmitMock).toHaveBeenCalledWith(1, 4);
  });

  // Test 69: Disables buttons while submitting
  it('should disable all buttons while rating is being submitted', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn().mockReturnValue(new Promise(resolve => setTimeout(resolve, 1000)));

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />);

    const easyButton = screen.getByRole('button', { name: /4.*easy/i });
    await user.click(easyButton);

    // All buttons should be disabled during submission
    expect(screen.getByRole('button', { name: /0.*blackout/i })).toBeDisabled();
    expect(screen.getByRole('button', { name: /5.*perfect/i })).toBeDisabled();
  });

  // Test 70: Shows loading indicator during submission
  it('should show loading indicator while submitting rating', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn().mockReturnValue(new Promise(resolve => setTimeout(resolve, 1000)));

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />);

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    expect(screen.getByTestId('rating-loading-spinner')).toBeInTheDocument();
  });

  // Test 71: Displays error message on submission failure
  it('should display error message when rating submission fails', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn().mockRejectedValue(new Error('Network error'));

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />);

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    await waitFor(() => {
      expect(screen.getByText(/failed to submit rating/i)).toBeInTheDocument();
    });
  });

  // Test 72: Color coding for quality levels (accessibility)
  it('should use color coding for quality levels (green=good, red=bad)', () => {
    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />);

    const perfectButton = screen.getByRole('button', { name: /5.*perfect/i });
    const blackoutButton = screen.getByRole('button', { name: /0.*blackout/i });

    // Perfect button should have success color (green)
    expect(perfectButton).toHaveClass(/success|green/i);

    // Blackout button should have error color (red)
    expect(blackoutButton).toHaveClass(/error|red/i);
  });
});
```

---

### 4.2 Integration Tests (10 tests)

#### 4.2.1 QualityRating + API Integration (5 tests)

**File**: `frontend/src/components/study-cards/__tests__/QualityRating.integration.test.tsx`

```typescript
import { describe, it, expect, beforeAll, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { setupServer } from 'msw/node';
import { rest } from 'msw';
import { QualityRating } from '../QualityRating';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const server = setupServer(
  rest.put('/api/v1/study-cards/:cardId/review', (req, res, ctx) => {
    return res(
      ctx.json({
        card_id: 1,
        quality: 4,
        next_review_date: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString(),
        interval_days: 6,
        ease_factor: 2.5,
        repetitions: 1,
        message: 'Review recorded successfully',
        quality_description: 'Easy',
      })
    );
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

describe('QualityRating + API Integration', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  // Test 73: Submits rating to API with correct payload
  it('should send PUT /api/v1/study-cards/:cardId/review with quality', async () => {
    const user = userEvent.setup();
    let requestBody: any = null;

    server.use(
      rest.put('/api/v1/study-cards/:cardId/review', async (req, res, ctx) => {
        requestBody = await req.json();
        return res(ctx.json({ card_id: 1, quality: 4, next_review_date: new Date().toISOString(), interval_days: 6, ease_factor: 2.5, repetitions: 1, message: 'Success', quality_description: 'Easy' }));
      })
    );

    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />, { wrapper });

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    await waitFor(() => {
      expect(requestBody).toEqual({ quality: 4, time_taken_seconds: expect.any(Number) });
    });
  });

  // Test 74: Displays next review date after successful submission
  it('should display next review date after rating submitted', async () => {
    const user = userEvent.setup();

    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />, { wrapper });

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    await waitFor(() => {
      expect(screen.getByText(/next review: in 6 days/i)).toBeInTheDocument();
    });
  });

  // Test 75: Includes JWT token in Authorization header
  it('should include JWT token in API request', async () => {
    const user = userEvent.setup();
    let authHeader: string | null = null;

    server.use(
      rest.put('/api/v1/study-cards/:cardId/review', (req, res, ctx) => {
        authHeader = req.headers.get('Authorization');
        return res(ctx.json({ card_id: 1, quality: 4, next_review_date: new Date().toISOString(), interval_days: 6, ease_factor: 2.5, repetitions: 1, message: 'Success', quality_description: 'Easy' }));
      })
    );

    localStorage.setItem('access_token', 'fake-jwt-token');

    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />, { wrapper });

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    await waitFor(() => {
      expect(authHeader).toBe('Bearer fake-jwt-token');
    });
  });

  // Test 76: Handles 401 Unauthorized (expired JWT)
  it('should redirect to login when 401 Unauthorized received', async () => {
    const user = userEvent.setup();
    const mockNavigate = vi.fn();

    server.use(
      rest.put('/api/v1/study-cards/:cardId/review', (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({ detail: 'Token expired' }));
      })
    );

    vi.mock('react-router-dom', () => ({
      useNavigate: () => mockNavigate,
    }));

    render(<QualityRating cardId={1} onRatingSubmit={vi.fn()} />, { wrapper });

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  // Test 77: Optimistic UI update (shows next card immediately)
  it('should show next card optimistically while API call completes', async () => {
    const user = userEvent.setup();
    const onRatingSubmitMock = vi.fn().mockResolvedValue({ success: true });

    // Delay API response by 1 second
    server.use(
      rest.put('/api/v1/study-cards/:cardId/review', async (req, res, ctx) => {
        await new Promise(resolve => setTimeout(resolve, 1000));
        return res(ctx.json({ card_id: 1, quality: 4, next_review_date: new Date().toISOString(), interval_days: 6, ease_factor: 2.5, repetitions: 1, message: 'Success', quality_description: 'Easy' }));
      })
    );

    render(<QualityRating cardId={1} onRatingSubmit={onRatingSubmitMock} />, { wrapper });

    await user.click(screen.getByRole('button', { name: /4.*easy/i }));

    // Verify callback called immediately (optimistic update)
    expect(onRatingSubmitMock).toHaveBeenCalledTimes(1);

    // Wait for API to complete
    await waitFor(() => {
      expect(screen.queryByTestId('rating-loading-spinner')).not.toBeInTheDocument();
    }, { timeout: 1500 });
  });
});
```

#### 4.2.2 SM-2 + State Management (5 tests)

**File**: `frontend/src/hooks/__tests__/useStudyCardReview.integration.test.ts`

```typescript
import { describe, it, expect } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { useStudyCardReview } from '../useStudyCardReview';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

describe('SM-2 + State Management Integration', () => {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  beforeEach(() => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        cards: [
          { id: 1, question: 'Q1', answer: 'A1', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
          { id: 2, question: 'Q2', answer: 'A2', citations: [], ease_factor: 2.5, interval_days: 1, repetitions: 0, next_review_date: new Date().toISOString() },
        ],
        count: 2,
      }),
    });
  });

  // Test 78: submitRating updates card locally before API response
  it('should update card state optimistically before API response', async () => {
    const { result } = renderHook(() => useStudyCardReview(), { wrapper });

    await waitFor(() => {
      expect(result.current.cards).toHaveLength(2);
    });

    // Submit rating for card 1
    result.current.submitRating(1, 4);

    // Verify card 1 removed from deck immediately (optimistic update)
    await waitFor(() => {
      expect(result.current.cards).toHaveLength(1);
      expect(result.current.cards[0].id).toBe(2); // Only card 2 remains
    });
  });

  // Test 79: Rollback on API failure (reverts optimistic update)
  it('should rollback optimistic update if API call fails', async () => {
    const { result } = renderHook(() => useStudyCardReview(), { wrapper });

    await waitFor(() => {
      expect(result.current.cards).toHaveLength(2);
    });

    // Mock API failure
    global.fetch = vi.fn().mockRejectedValue(new Error('Network error'));

    // Submit rating
    result.current.submitRating(1, 4);

    // Verify optimistic removal
    await waitFor(() => {
      expect(result.current.cards).toHaveLength(1);
    });

    // Wait for rollback (API failure detected)
    await waitFor(() => {
      expect(result.current.cards).toHaveLength(2); // Rolled back
      expect(result.current.error).toMatch(/failed to submit rating/i);
    });
  });

  // Test 80: Multiple rapid ratings queue correctly (no race condition)
  it('should handle multiple rapid ratings without race conditions', async () => {
    const { result } = renderHook(() => useStudyCardReview(), { wrapper });

    await waitFor(() => {
      expect(result.current.cards).toHaveLength(2);
    });

    // Submit ratings for both cards rapidly
    result.current.submitRating(1, 4);
    result.current.submitRating(2, 5);

    // Verify both cards removed
    await waitFor(() => {
      expect(result.current.cards).toHaveLength(0);
    });

    // Verify API called twice (no lost requests)
    expect(global.fetch).toHaveBeenCalledTimes(3); // Initial fetch + 2 ratings
  });

  // Test 81: Due date filter updates after rating submission
  it('should update due date filter after rating (excludes future cards)', async () => {
    const { result } = renderHook(() => useStudyCardReview(), { wrapper });

    await waitFor(() => {
      expect(result.current.cards).toHaveLength(2);
    });

    // Mock API to return card with future next_review_date
    const futureDate = new Date(Date.now() + 10 * 24 * 60 * 60 * 1000); // +10 days

    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        card_id: 1,
        next_review_date: futureDate.toISOString(),
        interval_days: 10,
        ease_factor: 2.5,
        repetitions: 1,
        message: 'Success',
        quality_description: 'Easy',
      }),
    });

    // Submit rating
    result.current.submitRating(1, 4);

    // Verify card 1 removed (future review date)
    await waitFor(() => {
      expect(result.current.cards).toHaveLength(1);
      expect(result.current.cards[0].id).toBe(2);
    });
  });

  // Test 82: Statistics update after rating (total_reviews, avg_quality)
  it('should update statistics after rating submission', async () => {
    const { result } = renderHook(() => useStudyCardReview(), { wrapper });

    await waitFor(() => {
      expect(result.current.statistics.total_reviews).toBe(0);
    });

    // Submit rating
    result.current.submitRating(1, 4);

    // Verify statistics updated
    await waitFor(() => {
      expect(result.current.statistics.total_reviews).toBe(1);
      expect(result.current.statistics.average_quality).toBe(4);
    });
  });
});
```

---

### 4.3 E2E Tests (3 tests)

**File**: `frontend/tests/e2e/sm2-review.spec.ts`

```typescript
import { test, expect } from '@playwright/test';

test.describe('SM-2 Review E2E', () => {
  test.beforeEach(async ({ page }) => {
    // Login
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@test.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL('/dashboard');
  });

  // Test 83: Complete review workflow with SM-2 rating
  test('should complete full review workflow with quality rating', async ({ page }) => {
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Show answer
    await page.click('button:has-text("Show Answer")');
    await page.waitForTimeout(700); // Flip animation

    // Verify quality rating buttons appear
    await expect(page.locator('button:has-text("5 - Perfect")')).toBeVisible();

    // Click quality rating (4 - Easy)
    await page.click('button:has-text("4 - Easy")');

    // Verify next review date displayed
    await expect(page.locator('text=/next review: in \\d+ days/i')).toBeVisible({ timeout: 3000 });

    // Verify card advanced (or deck complete)
    await expect(page.locator('text=/card 2 of|review complete/i')).toBeVisible();
  });

  // Test 84: Keyboard shortcuts for quality rating (0-5 keys)
  test('should support keyboard shortcuts for quality ratings', async ({ page }) => {
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Show answer with spacebar
    await page.keyboard.press('Space');
    await page.waitForTimeout(700);

    // Rate with keyboard (press "4" key)
    await page.keyboard.press('4');

    // Verify rating submitted
    await expect(page.locator('text=/next review: in \\d+ days/i')).toBeVisible({ timeout: 3000 });
  });

  // Test 85: Statistics update after multiple reviews
  test('should update statistics after multiple card reviews', async ({ page }) => {
    await page.goto('/study-cards/review');

    await expect(page.locator('[data-testid="flashcard-card"]')).toBeVisible({ timeout: 5000 });

    // Review 3 cards
    for (let i = 0; i < 3; i++) {
      // Show answer
      await page.keyboard.press('Space');
      await page.waitForTimeout(700);

      // Rate as "Easy" (4)
      await page.keyboard.press('4');

      // Wait for next card or completion
      await page.waitForTimeout(1000);
    }

    // Navigate to statistics page
    await page.click('a:has-text("Statistics")');

    // Verify statistics updated
    await expect(page.locator('text=/total reviews: 3/i')).toBeVisible();
    await expect(page.locator('text=/average quality: 4\\.0/i')).toBeVisible();
    await expect(page.locator('text=/retention rate: 100%/i')).toBeVisible(); // All rated ≥3
  });
});
```

---

## 5. PRD-P8-002: Integration Testing

**Total**: 22 tests (0 unit + 15 integration + 7 E2E)

### 5.1 Cross-Component Integration Tests (15 tests)

#### 5.1.1 P1-005 → P1-006 Integration (5 tests)

**File**: `backend/tests/test_integration/test_study_cards_pipeline.py`

```python
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from src.main import app
from src.db.models import StudyCard, OSCEAttemptAI, User


@pytest.mark.asyncio
class TestP1005ToP1006Integration:
    """Test integration between Auto Study Card Generation (P1-005) and Flashcard Review Interface (P1-006)"""

    # Test 86: Cards generated by P1-005 are fetchable by P1-006 API
    async def test_generated_cards_fetchable_by_review_api(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that cards generated from OSCE session can be fetched for review"""
        # Step 1: Create OSCE session
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440000",
            user_id=test_user.user_id,
            persona_code="CARD-001",
            feedback_text="Excellent history taking. Used SOCRATES framework effectively.",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        # Step 2: Generate cards via P1-005 API
        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440000"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 201
        generated_data = generate_response.json()
        assert generated_data["count"] >= 3

        # Step 3: Fetch cards via P1-006 API
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert review_response.status_code == 200
        review_data = review_response.json()

        # Verify same cards returned
        assert review_data["count"] == generated_data["count"]
        assert len(review_data["cards"]) == generated_data["count"]

        # Verify card structure matches frontend expectations
        card = review_data["cards"][0]
        assert "id" in card
        assert "question" in card
        assert "answer" in card
        assert "citations" in card
        assert "ease_factor" in card
        assert "interval_days" in card
        assert "repetitions" in card
        assert "next_review_date" in card

    # Test 87: Citations generated by P1-005 display correctly in P1-006
    async def test_citations_from_generation_display_in_ui(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that RAG citations from P1-005 are properly formatted for P1-006 display"""
        # Generate cards (P1-005)
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440001",
            user_id=test_user.user_id,
            persona_code="CARD-002",
            feedback_text="Good pain assessment using SOCRATES.",
            score=80,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440001"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 201

        # Fetch for review (P1-006)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        card = review_response.json()["cards"][0]

        # Verify citations have required fields for frontend display
        assert len(card["citations"]) > 0
        citation = card["citations"][0]

        assert "source" in citation
        assert "qdrant_point_id" in citation  # Critical for RAG validation
        assert "confidence" in citation
        assert citation["confidence"] >= 0.65  # P1-005 validation threshold

        # Verify qdrant_point_id is valid UUID format
        import re
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        assert re.match(uuid_pattern, citation["qdrant_point_id"].lower())

    # Test 88: SM-2 parameters initialized correctly by P1-005 for P1-006 use
    async def test_sm2_parameters_initialized_for_first_review(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that SM-2 parameters are correctly initialized for first review in P1-006"""
        # Generate cards (P1-005)
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440002",
            user_id=test_user.user_id,
            persona_code="CARD-003",
            feedback_text="Test session",
            score=75,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440002"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 201

        # Fetch for review (P1-006)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        card = review_response.json()["cards"][0]

        # Verify SM-2 initialization (per PRD-P1-005 Phase 3)
        assert card["ease_factor"] == 2.5  # Default ease factor
        assert card["interval_days"] == 1  # First review tomorrow
        assert card["repetitions"] == 0    # No reviews yet
        assert "next_review_date" in card

        # Verify next_review_date is NOW (card available immediately for first review)
        next_review = datetime.fromisoformat(card["next_review_date"].replace('Z', '+00:00'))
        now = datetime.utcnow()
        delta = abs((next_review - now).total_seconds())
        assert delta < 60  # Within 60 seconds (allowing for test execution time)

    # Test 89: Content validation from P1-005 ensures P1-006 displays substantive content
    async def test_no_placeholder_content_in_review_interface(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that P1-005 content validation prevents placeholders in P1-006 display"""
        # Generate cards (P1-005 validates content)
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440003",
            user_id=test_user.user_id,
            persona_code="CARD-004",
            feedback_text="Comprehensive feedback with multiple learning points for testing.",
            score=90,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        generate_response = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440003"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert generate_response.status_code == 201

        # Fetch for review (P1-006)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        cards = review_response.json()["cards"]

        # Verify no placeholder patterns in any card
        forbidden_patterns = ["lorem ipsum", "[insert", "todo", "tbd", "...", "[placeholder"]

        for card in cards:
            question_lower = card["question"].lower()
            answer_lower = card["answer"].lower()

            for pattern in forbidden_patterns:
                assert pattern not in question_lower, f"Placeholder '{pattern}' found in question"
                assert pattern not in answer_lower, f"Placeholder '{pattern}' found in answer"

            # Verify minimum content length (substantive requirement)
            assert len(card["question"]) >= 10, "Question too short (<10 chars)"
            assert len(card["answer"]) >= 20, "Answer too short (<20 chars)"

    # Test 90: Idempotency - regenerating cards returns 409, P1-006 shows existing cards
    async def test_idempotency_prevents_duplicate_cards_in_review(
        self, async_client: AsyncClient, db: Session, test_user: User
    ):
        """Test that P1-005 idempotency prevents duplicate cards in P1-006 review queue"""
        osce_session = OSCEAttemptAI(
            attempt_id="550e8400-e29b-41d4-a716-446655440004",
            user_id=test_user.user_id,
            persona_code="CARD-005",
            feedback_text="Test session",
            score=85,
            created_at=datetime.utcnow(),
        )
        db.add(osce_session)
        db.commit()

        # First generation (P1-005)
        response1 = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440004"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response1.status_code == 201
        count_first = response1.json()["count"]

        # Second generation attempt (should fail with 409)
        response2 = await async_client.post(
            "/api/v1/study-cards/generate-from-osce",
            json={"session_id": "550e8400-e29b-41d4-a716-446655440004"},
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert response2.status_code == 409  # Conflict

        # Verify P1-006 still shows correct count (no duplicates)
        review_response = await async_client.get(
            "/api/v1/study-cards",
            headers={"Authorization": f"Bearer {test_user.access_token}"},
        )
        assert review_response.json()["count"] == count_first  # Same as first generation
```

---

Due to the 200,000 token limit, I'll continue the comprehensive testing plan in a separate document. Let me save this current progress and create a continuation:

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Create comprehensive testing plan document (100+ test cases)", "status": "completed", "activeForm": "Creating comprehensive testing plan document"}, {"content": "Continue testing plan (P1-006↔P1-007, P8-002 E2E, Security, Performance, Accessibility, Tooling)", "status": "in_progress", "activeForm": "Continuing testing plan with remaining sections"}, {"content": "Implement PRD-P1-006 (Flashcard Review Interface)", "status": "pending", "activeForm": "Implementing PRD-P1-006 (Flashcard Review Interface)"}, {"content": "Implement PRD-P1-007 (SM-2 Review Logic)", "status": "pending", "activeForm": "Implementing PRD-P1-007 (SM-2 Review Logic)"}, {"content": "Implement PRD-P8-002 (Integration Testing)", "status": "pending", "activeForm": "Implementing PRD-P8-002 (Integration Testing)"}]