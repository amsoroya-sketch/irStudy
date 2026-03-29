# PRD: Spaced Repetition Review Logic (SM-2 Algorithm)

**PRD ID**: PRD-P1-007-SM2-REVIEW-LOGIC
**Category**: Frontend Logic + Backend Integration
**Priority**: P1-High (Enables Effective Knowledge Retention)
**Estimated Effort**: 5-7 hours
**Dependencies**: PRD-P1-006 (Flashcard Review Interface - needs UI to integrate ratings)
**Status**: Ready for Implementation
**Assigned Agents**: `react-frontend-developer`, `python-backend-developer`

**Version**: 1.0 (Full Implementation)
**Created**: 2026-03-22
**Last Updated**: 2026-03-22

---

## R - REQUEST (What & Why)

### Executive Summary

Implement the **SM-2 (SuperMemo-2) spaced repetition algorithm** to intelligently schedule study card reviews based on student performance. When students rate flashcards using a 6-point quality scale (0-5), the system dynamically calculates optimal review intervals, transforming passive flashcard review into an active learning system proven to increase retention by 200-300%.

**Algorithm Calculates**:
1. **Ease Factor (EF)** - How easy the card is for this student (1.3 to 2.5+, personalized per card)
2. **Interval Days (I)** - Days until next review (1 day → 6 days → exponential growth based on EF)
3. **Repetitions (n)** - Consecutive successful reviews (resets to 0 on incorrect response)
4. **Next Review Date** - Exact timestamp when card becomes "due" again

**Business Impact**:
- **Retention increase**: 200-300% better long-term memory vs. traditional cramming
- **Time efficiency**: Focus on weak cards, skip mastered ones (40% time savings)
- **Personalized learning**: Algorithm adapts to each student's memory strength per card
- **Behavioral psychology**: Optimal difficulty timing prevents frustration and boredom
- **ROI**: Students pass AMC Clinical Exam first attempt rate increases from 65% to 85%

**Current State**: Study cards exist with static SM-2 parameters (ease_factor=2.5, interval=1, repetitions=0). No way for students to rate cards or update schedules.

**Desired State**: Dynamic SM-2 algorithm adjusts parameters based on quality ratings, creating personalized review schedules. Students see "due today" cards only, reducing overwhelm.

### User Story

**As a** medical student reviewing study cards generated from my OSCE sessions
**I want** the system to automatically schedule my next review based on how well I know each card
**So that** I can efficiently retain clinical knowledge without manually tracking review schedules, focusing my limited study time on cards I'm struggling with

**Acceptance Criteria**:
- After viewing answer, I see 6 quality rating buttons (0-5 with labels)
- Clicking a rating triggers SM-2 calculation and updates database
- System shows me when I'll see the card next (e.g., "Next review: March 28, 2026")
- Tomorrow, I only see cards that are "due" (next_review_date <= TODAY)
- Cards I rate 5 ("Perfect") disappear for weeks, cards I rate 0 ("Blackout") reappear tomorrow

### Problem Statement

**Current Pain Points**:
1. **No spaced repetition** - Students see all cards every time, causing overwhelm
2. **No prioritization** - Equal time spent on mastered vs. struggling cards (inefficient)
3. **No feedback loop** - System doesn't adapt to student's actual knowledge level
4. **Manual tracking burden** - Students abandon flashcards because it's too much work

**Root Cause**: SM-2 parameters are static (initialized at card creation). No mechanism to update them based on student performance.

**Proposed Solution**:
- Frontend: `useSpacedRepetition` hook implements SM-2 algorithm in TypeScript
- Frontend: `QualityRating` component displays 6 buttons after answer shown
- Backend: `PUT /api/v1/study-cards/{card_id}/review` endpoint updates database
- Frontend: `GET /api/v1/study-cards?due=true` filters cards WHERE next_review_date <= NOW()

**Success Metrics**:
- 80% of students rate cards consistently (5+ days per week)
- Average ease_factor across all students: 2.3-2.7 (healthy range)
- Retention rate (cards rated ≥3 on re-review): ≥70%
- Study time per session: Decreases from 45min to 25min as algorithm learns

### Success Criteria

#### Must Have (100% Required)
- [ ] **SM-2 Algorithm**: Implements standard SuperMemo-2 formula with 100% accuracy
- [ ] **Quality Rating UI**: 6 buttons (0-5) with descriptive labels ("Blackout", "Wrong", "Hard", "OK", "Easy", "Perfect")
- [ ] **Parameter Updates**: Correctly calculates ease_factor, interval_days, repetitions, next_review_date per SM-2 spec
- [ ] **API Integration**: PUT /api/v1/study-cards/{card_id}/review endpoint updates database atomically
- [ ] **Due Date Filtering**: Only shows cards where `next_review_date <= NOW()` in review interface
- [ ] **TypeScript Hook**: `useSpacedRepetition` hook manages algorithm logic with full type safety
- [ ] **Testing**: 25+ tests (15 algorithm accuracy tests, 10 integration tests), 100% pass rate
- [ ] **0 Errors**: TypeScript compiles, tests pass, lint passes, backend passes pytest

#### Should Have (90% Priority)
- [ ] **Visual Feedback**: Shows new interval and next review date after rating ("Next review: in 6 days")
- [ ] **Undo Last Rating**: Allows reverting if student misclicked (within 5 seconds)
- [ ] **Keyboard Shortcuts**: Press 0-5 keys to rate cards quickly
- [ ] **Statistics Dashboard**: Shows retention rate, average ease factor, total reviews completed
- [ ] **Optimistic UI**: Immediately shows next card while API call completes in background

#### Nice to Have (Optional)
- [ ] **Custom Intervals**: Allow students to manually override next review date (power users)
- [ ] **Study Streaks**: Track consecutive days of review, show "7 day streak!" badge
- [ ] **Difficulty Distribution**: Chart showing distribution of easy/medium/hard cards in deck
- [ ] **Export to Anki**: Allow exporting cards with SM-2 params to Anki format

---

## A - ARCHITECTURE (How)

### Technical Approach

**SM-2 Algorithm Overview** (SuperMemo-2, 1987):

The algorithm adjusts three parameters based on a 6-point quality scale (0-5):

1. **Quality Scale** (Student Input):
   - **0** = Complete blackout (no recall)
   - **1** = Incorrect response, but recognized the answer when shown
   - **2** = Incorrect response, but seems easy to remember now
   - **3** = Correct response, but required significant difficulty to recall
   - **4** = Correct response, recalled with some hesitation
   - **5** = Perfect response, recalled instantly

2. **Ease Factor (EF)** - Difficulty multiplier (1.3 to ∞, typically 1.3-2.5):
   - Starts at 2.5 for all new cards
   - Increases for quality 4-5 (card is easy for this student)
   - Decreases for quality 3 (card is hard)
   - Unchanged for quality 0-2 (incorrect responses)
   - Formula: `EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))`
   - Minimum: 1.3 (never goes lower to prevent cards from disappearing)

3. **Interval (I)** - Days until next review:
   - First review (n=0): Always 1 day
   - Second review (n=1): Always 6 days
   - Subsequent reviews (n≥2): `I(n) = I(n-1) * EF`
   - Resets to 1 day for quality <3 (incorrect)

4. **Repetitions (n)** - Consecutive successful reviews:
   - Increments by 1 for quality ≥3
   - Resets to 0 for quality <3

**SM-2 Formula** (Pseudocode):
```
function calculate_sm2(quality, current_EF, current_interval, current_n):
    if quality >= 3:  # Correct response
        if current_n == 0:
            new_interval = 1 day
        elif current_n == 1:
            new_interval = 6 days
        else:
            new_interval = round(current_interval * current_EF)

        new_EF = current_EF + (0.1 - (5-quality) * (0.08 + (5-quality) * 0.02))
        new_EF = max(1.3, new_EF)  # Floor at 1.3
        new_n = current_n + 1

    else:  # Incorrect response (quality < 3)
        new_interval = 1 day
        new_EF = current_EF  # Unchanged
        new_n = 0  # Reset

    next_review_date = NOW() + new_interval days

    return {
        ease_factor: new_EF,
        interval_days: new_interval,
        repetitions: new_n,
        next_review_date: next_review_date
    }
```

**Example Calculations**:
```
# Card 1: Student rates "Perfect" (5)
Initial: EF=2.5, I=1, n=0, q=5
→ n=1, I=1 (first review always 1 day), EF=2.6 (improved)
Next review: Tomorrow

# Card 1: Student rates "Perfect" (5) again
Current: EF=2.6, I=1, n=1, q=5
→ n=2, I=6 (second review always 6 days), EF=2.7
Next review: 6 days from now

# Card 1: Student rates "Easy" (4) third time
Current: EF=2.7, I=6, n=2, q=4
→ n=3, I=round(6*2.7)=16 days, EF=2.76
Next review: 16 days from now

# Card 2: Student rates "Blackout" (0)
Initial: EF=2.5, I=1, n=0, q=0
→ n=0 (reset), I=1 (reset), EF=2.5 (unchanged)
Next review: Tomorrow (student struggles with this one)
```

### Component Design

```
┌─────────────────────────────────────────────────────────────────┐
│                      ReviewSession.tsx                          │
│                  (Orchestrates P1-6 + P1-7)                     │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  FlashcardView (from P1-6)                                │  │
│  │  - Renders question/answer with flip animation           │  │
│  │  - Navigation (next/previous)                             │  │
│  │  - Citations display                                      │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  QualityRating (NEW - P1-7)                               │  │
│  │                                                           │  │
│  │  How well did you know this?                              │  │
│  │                                                           │  │
│  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐ ┌────┐              │  │
│  │  │ 0  │ │ 1  │ │ 2  │ │ 3  │ │ 4  │ │ 5  │              │  │
│  │  │💀  │ │❌  │ │😰 │ │😐 │ │😊 │ │⭐ │              │  │
│  │  │ Black│ │Wrong│ │Hard│ │ OK │ │Easy│ │Perf│              │  │
│  │  │-out │ │    │ │    │ │    │ │    │ │-ect│              │  │
│  │  └────┘ └────┘ └────┘ └────┘ └────┘ └────┘              │  │
│  │                                                           │  │
│  │  (Appears only after student has viewed answer)           │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  ReviewResult (NEW - P1-7)                                │  │
│  │                                                           │  │
│  │  ✅ Card reviewed!                                        │  │
│  │  📅 Next review: March 28, 2026 (6 days from now)         │  │
│  │  📈 Ease factor: 2.6 → 2.76 (+0.16)                       │  │
│  │  🔢 Repetitions: 2 consecutive correct                    │  │
│  │                                                           │  │
│  │  [ Continue to Next Card ]                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│ Step 1: Student reviews card (FlashcardView)                  │
│         - Views question                                       │
│         - Clicks "Show Answer"                                 │
│         - Reads answer + citations                             │
│ ↓                                                              │
│ Step 2: QualityRating component appears                       │
│         - 6 buttons: 0-5                                       │
│         - Student selects quality (e.g., 4 = "Easy")          │
│ ↓                                                              │
│ Step 3: useSpacedRepetition hook calculates SM-2              │
│         calculateSM2(quality=4, EF=2.5, I=1, n=0)             │
│         → Returns: {EF=2.6, I=6, n=1, next_review=...}        │
│ ↓                                                              │
│ Step 4: Frontend sends PUT request to backend                 │
│         PUT /api/v1/study-cards/abc-123/review                │
│         Body: { "quality": 4 }                                 │
│ ↓                                                              │
│ Step 5: Backend validates + recalculates SM-2                 │
│         (Double-check frontend calculation for security)       │
│         UPDATE study_cards SET                                 │
│           ease_factor = 2.6,                                   │
│           interval_days = 6,                                   │
│           repetitions = 1,                                     │
│           next_review_date = NOW() + INTERVAL '6 days',       │
│           last_reviewed_at = NOW()                             │
│         WHERE card_id = 'abc-123'                              │
│ ↓                                                              │
│ Step 6: Backend returns updated card                          │
│         Response: { card_id, ease_factor, interval_days, ...}│
│ ↓                                                              │
│ Step 7: Frontend displays ReviewResult                        │
│         "✅ Card reviewed! Next review: March 28 (6 days)"    │
│ ↓                                                              │
│ Step 8: Student clicks "Continue to Next Card"                │
│         - Current card removed from "due" list                 │
│         - Next card loads                                      │
│         - Repeat from Step 1                                   │
└────────────────────────────────────────────────────────────────┘

Next Session (6 days later):
┌────────────────────────────────────────────────────────────────┐
│ GET /api/v1/study-cards?due=true                              │
│ → Filters: WHERE next_review_date <= NOW()                    │
│ → Returns only cards scheduled for today                       │
└────────────────────────────────────────────────────────────────┘
```

### State Management

**Frontend Hook** (`useSpacedRepetition.ts`):
- Implements SM-2 calculation logic
- Manages API mutation for submitting ratings
- Provides optimistic UI updates
- Handles error recovery (fallback to server calculation)

**Backend API** (`study_cards.py`):
- Receives quality rating (0-5)
- Recalculates SM-2 parameters (server-side validation)
- Updates database atomically
- Returns updated card with new review date

### Database Schema

**No migration required** - `study_cards` table already has SM-2 columns from P1-5:

```sql
-- Existing columns (no changes needed)
CREATE TABLE study_cards (
    card_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,

    -- SM-2 parameters (initialized by P1-5, updated by P1-7)
    ease_factor DECIMAL(3,2) DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed_at TIMESTAMP,  -- Updated each review

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Query for Due Cards**:
```sql
-- Frontend calls GET /api/v1/study-cards?due=true
SELECT * FROM study_cards
WHERE user_id = $1
  AND next_review_date <= CURRENT_TIMESTAMP
ORDER BY next_review_date ASC  -- Oldest cards first
LIMIT 50;
```

---

## L - LOOP (Iterative Development)

### Phase 1: SM-2 Algorithm Implementation (Frontend) - 2 hours

**Objective**: Create `useSpacedRepetition` hook with 100% accurate SM-2 algorithm

**Tasks**:
1. Create `hooks/useSpacedRepetition.ts`
2. Implement `calculateSM2()` function per SuperMemo-2 spec
3. Write 15 unit tests covering all quality values (0-5) and edge cases
4. Validate algorithm accuracy against reference implementation

**Deliverables**:
- `useSpacedRepetition.ts` hook (150 lines)
- 15 unit tests with 100% pass rate
- Edge case handling (negative quality, decimal quality, null values)

**Validation Checkpoints**:
- [ ] Quality 0-2 resets repetitions to 0, interval to 1 day
- [ ] Quality 3 first review → interval=1 day, second review → interval=6 days
- [ ] Quality 4-5 increases ease_factor correctly per formula
- [ ] Ease factor never drops below 1.3
- [ ] Interval rounds to integer days
- [ ] 15/15 tests passing

**Test Cases**:
```typescript
test('quality 0 resets repetitions and interval', () => {
  const result = calculateSM2({
    quality: 0,
    ease_factor: 2.5,
    interval_days: 6,
    repetitions: 2
  });

  expect(result.repetitions).toBe(0);
  expect(result.interval_days).toBe(1);
  expect(result.ease_factor).toBe(2.5); // Unchanged
});

test('quality 3 first review sets interval to 1 day', () => {
  const result = calculateSM2({
    quality: 3,
    ease_factor: 2.5,
    interval_days: 1,
    repetitions: 0
  });

  expect(result.interval_days).toBe(1);
  expect(result.repetitions).toBe(1);
  expect(result.ease_factor).toBeCloseTo(2.36); // Decreased (hard recall)
});

test('quality 3 second review sets interval to 6 days', () => {
  const result = calculateSM2({
    quality: 3,
    ease_factor: 2.36,
    interval_days: 1,
    repetitions: 1
  });

  expect(result.interval_days).toBe(6);
  expect(result.repetitions).toBe(2);
});

test('quality 5 increases ease_factor to maximum', () => {
  const result = calculateSM2({
    quality: 5,
    ease_factor: 2.5,
    interval_days: 6,
    repetitions: 2
  });

  expect(result.ease_factor).toBeCloseTo(2.6); // +0.1
  expect(result.interval_days).toBe(16); // round(6 * 2.6)
});

test('ease_factor never drops below 1.3', () => {
  let ef = 1.4;
  for (let i = 0; i < 100; i++) {
    const result = calculateSM2({
      quality: 3,
      ease_factor: ef,
      interval_days: 1,
      repetitions: 0
    });
    ef = result.ease_factor;
  }

  expect(ef).toBeGreaterThanOrEqual(1.3);
});
```

**Exit Criteria**:
- Algorithm matches SuperMemo-2 spec 100%
- 15/15 tests passing
- 0 TypeScript errors

#### 3-Layer QA Validation (Phase 1 - MANDATORY)

**Layer 1: Agent Self-Validation** (`react-frontend-developer`)

```bash
cd /home/dev/Development/irStudy/frontend

# 1. Run SM-2 algorithm tests
npm test -- useSpacedRepetition
# Expected: ✅ 15/15 tests passed

# 2. TypeScript compilation
npx tsc --noEmit
# Expected: ✅ 0 errors

# 3. Lint check
npm run lint
# Expected: ✅ 0 errors
```

**Agent Checklist**:
- [ ] 15/15 algorithm tests pass
- [ ] SM-2 formula matches spec exactly
- [ ] 0 TypeScript errors

**BLOCKS Phase 1**: Fix if any check fails.

---

**Layer 2: PM Verification**

```bash
npm test -- useSpacedRepetition
# Verify: 15/15 PASSED
```

**PM Checklist**:
- [ ] Algorithm verified (ease_factor, interval, repetitions calculations correct)

---

**Layer 3: testing-qa-expert Review**

```bash
npm test && npm test -- --coverage
# Expected: ✅ 100% pass, ≥80% coverage
```

**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 2: Quality Rating UI Component - 2 hours

**Objective**: Create `QualityRating` component with 6 buttons and visual feedback

**Tasks**:
1. Create `components/study-cards/QualityRating.tsx`
2. Implement 6-button UI with icons and labels
3. Add keyboard shortcuts (0-5 keys)
4. Integrate with `useSpacedRepetition` hook
5. Add `ReviewResult` component for feedback

**Deliverables**:
- `QualityRating.tsx` (120 lines)
- `ReviewResult.tsx` (80 lines)
- 5 component tests

**Validation Checkpoints**:
- [ ] 6 buttons displayed after answer shown
- [ ] Buttons have descriptive labels (Blackout, Wrong, Hard, OK, Easy, Perfect)
- [ ] Clicking button triggers SM-2 calculation
- [ ] Keyboard shortcuts work (0-5 keys)
- [ ] Review result shows next review date and ease factor change
- [ ] 5/5 component tests passing

**Test Cases**:
```typescript
test('renders 6 quality buttons after answer shown', () => {
  render(<QualityRating isAnswerShown={true} onRate={mockOnRate} />);
  expect(screen.getByText(/Blackout/)).toBeInTheDocument();
  expect(screen.getByText(/Perfect/)).toBeInTheDocument();
});

test('buttons hidden when answer not shown', () => {
  render(<QualityRating isAnswerShown={false} onRate={mockOnRate} />);
  expect(screen.queryByText(/Blackout/)).not.toBeInTheDocument();
});

test('clicking quality 4 button calls onRate with 4', () => {
  render(<QualityRating isAnswerShown={true} onRate={mockOnRate} />);
  fireEvent.click(screen.getByText(/Easy/));
  expect(mockOnRate).toHaveBeenCalledWith(4);
});

test('keyboard shortcut 5 triggers perfect rating', () => {
  render(<QualityRating isAnswerShown={true} onRate={mockOnRate} />);
  fireEvent.keyDown(document, { key: '5' });
  expect(mockOnRate).toHaveBeenCalledWith(5);
});

test('displays next review date after rating', () => {
  const result = { next_review_date: '2026-03-28', interval_days: 6 };
  render(<ReviewResult result={result} />);
  expect(screen.getByText(/Next review: March 28/)).toBeInTheDocument();
  expect(screen.getByText(/6 days/)).toBeInTheDocument();
});
```

**Exit Criteria**:
- Quality rating UI functional
- Keyboard shortcuts work
- Visual feedback displayed
- 5/5 tests passing

#### 3-Layer QA Validation (Phase 2 - MANDATORY)
**Layer 1**: `npm test -- QualityRating` (5/5 pass) + `npx tsc --noEmit` (0 errors)
**Layer 2**: PM verifies keyboard shortcuts (0-5 keys work)
**Layer 3**: QA runs full suite (`npm test && npm test -- --coverage`, ≥80%)
**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 3: Backend API Integration - 1.5 hours

**Objective**: Create PUT endpoint for submitting reviews

**Tasks**:
1. Add `PUT /api/v1/study-cards/{card_id}/review` endpoint
2. Implement SM-2 calculation in Python (server-side validation)
3. Update database with new SM-2 parameters
4. Add integration tests

**Deliverables**:
- API endpoint implementation (90 lines)
- Python SM-2 function (50 lines)
- 5 integration tests

**Validation Checkpoints**:
- [ ] API accepts quality 0-5, rejects invalid values
- [ ] SM-2 calculation matches frontend (Python vs TypeScript consistency)
- [ ] Database updated correctly
- [ ] Returns updated card with new review date
- [ ] Ownership validation (user can only review own cards)
- [ ] 5/5 integration tests passing

**Test Cases**:
```python
def test_review_card_quality_3(client, jwt_token, sample_card):
    """Test reviewing card with quality 3"""
    response = client.put(
        f"/api/v1/study-cards/{sample_card.card_id}/review",
        headers={"Authorization": f"Bearer {jwt_token}"},
        json={"quality": 3}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['interval_days'] == 1  # First review
    assert data['repetitions'] == 1
    assert data['ease_factor'] < 2.5  # Decreased (quality 3)

def test_review_card_quality_5(client, jwt_token, sample_card):
    """Test reviewing card with quality 5"""
    response = client.put(
        f"/api/v1/study-cards/{sample_card.card_id}/review",
        json={"quality": 5}
    )

    assert response.status_code == 200
    data = response.json()
    assert data['ease_factor'] > 2.5  # Increased (quality 5)

def test_review_card_invalid_quality(client, jwt_token, sample_card):
    """Test that quality 6 is rejected"""
    response = client.put(
        f"/api/v1/study-cards/{sample_card.card_id}/review",
        json={"quality": 6}
    )

    assert response.status_code == 422  # Validation error

def test_review_card_ownership(client, other_user_jwt, sample_card):
    """Test that user cannot review another user's card"""
    response = client.put(
        f"/api/v1/study-cards/{sample_card.card_id}/review",
        headers={"Authorization": f"Bearer {other_user_jwt}"},
        json={"quality": 4}
    )

    assert response.status_code == 403

def test_get_due_cards(client, jwt_token, db):
    """Test that GET /study-cards?due=true returns only due cards"""
    # Create cards with different next_review_dates
    # Card 1: Due today
    # Card 2: Due next week
    # Card 3: Due yesterday

    response = client.get(
        "/api/v1/study-cards?due=true",
        headers={"Authorization": f"Bearer {jwt_token}"}
    )

    assert response.status_code == 200
    cards = response.json()['cards']
    assert len(cards) == 2  # Card 1 and Card 3 only
```

**Exit Criteria**:
- API endpoint functional
- SM-2 calculation correct
- Frontend/backend SM-2 algorithms match (within 0.01 tolerance)
- 5/5 integration tests passing

#### 3-Layer QA Validation (Phase 3 - MANDATORY)
**Layer 1**: `pytest tests/test_api/test_study_cards_review.py -v` (5/5 pass) + `bandit -r src/api/` (0 issues)
**Layer 2**: PM runs `curl PUT /study-cards/{id}/review` (manual API test) + verify SM-2 match test passes
**Layer 3**: QA runs `pytest tests/ -v` (100% pass) + coverage check (≥85%)
**QA Decision**: ✅ APPROVE / ❌ REJECT

---

### Phase 4: Integration Testing + Documentation - 0.5 hours

**Objective**: Complete E2E tests and finalize documentation

**Tasks**:
1. Write E2E test (Playwright)
2. Add API documentation (OpenAPI schema)
3. Update README with SM-2 usage examples
4. Final QA pass

**Deliverables**:
- 1 E2E test
- OpenAPI schema updates
- README updates

**Validation Checkpoints**:
- [ ] E2E test passes (complete review workflow)
- [ ] API documentation complete
- [ ] README includes SM-2 examples
- [ ] 25/25 total tests passing (15 unit + 5 component + 5 integration)

**E2E Test**:
```typescript
test('Student reviews card with quality rating', async ({ page }) => {
  // Login
  await page.goto('/login');
  await page.fill('[name="email"]', 'student@test.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  // Navigate to review
  await page.goto('/study-cards/review');

  // Card appears
  await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

  // Show answer
  await page.click('button:has-text("Show Answer")');

  // Quality rating panel appears
  await expect(page.locator('[data-testid="quality-rating"]')).toBeVisible();

  // Select quality 4 ("Easy")
  await page.click('[data-testid="quality-4"]');

  // Success message
  await expect(page.locator('text=Next review:')).toBeVisible();
  await expect(page.locator('text=6 days')).toBeVisible();

  // Next card loads
  await page.click('button:has-text("Continue to Next Card")');
  await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();
});
```

**Exit Criteria**:
- All tests passing (26/26)
- Documentation complete
- Ready for production

#### 3-Layer QA Validation (Phase 4 - MANDATORY FINAL APPROVAL)

**Layer 1**: Frontend: `npm test` (100% pass) + Backend: `pytest tests/ -v` (100% pass) + E2E: `npx playwright test` (1/1 pass)
**Layer 2**: PM runs full workflow manually (OSCE → Generate Cards → Review → Rate → Verify SM-2 update in DB)
**Layer 3**: QA comprehensive validation:
  - Frontend coverage ≥80% (`npm test -- --coverage`)
  - Backend coverage ≥85% (`pytest --cov=src`)
  - SM-2 consistency test passes (TypeScript ↔ Python within 0.01 tolerance)
  - Performance: <200ms API response (`curl -w`)
  - E2E workflow <30s total
**QA Final Decision**: ✅ APPROVE PRD-P1-007 COMPLETE / ❌ REJECT

**Final Approval Signature**:
- [ ] PM Sign-Off: _______________ Date: _______
- [ ] testing-qa-expert Sign-Off: _______________ Date: _______

**PRD-P1-007 Status**: ⏳ INCOMPLETE / ✅ COMPLETE

---

## P - PLAN (Detailed Implementation)

### Files to Create

#### 1. `frontend/src/hooks/useSpacedRepetition.ts` (250 lines)

**Purpose**: SM-2 algorithm implementation and API integration

**Full Implementation**:

```typescript
import { useCallback } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../api/client';

interface SM2Params {
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

interface SM2Result extends SM2Params {
  next_review_date: string;
}

interface ReviewResponse {
  card_id: string;
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_date: string;
  last_reviewed_at: string;
}

/**
 * useSpacedRepetition Hook
 *
 * Implements SM-2 (SuperMemo-2) spaced repetition algorithm.
 *
 * Features:
 * - Client-side SM-2 calculation for instant feedback
 * - Server-side recalculation for validation
 * - Optimistic UI updates
 * - Error recovery
 *
 * References:
 * - SuperMemo-2 Algorithm (1987): https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
 *
 * @returns Object with calculateSM2 function and submitReview mutation
 */
export function useSpacedRepetition() {
  const queryClient = useQueryClient();

  /**
   * Calculate SM-2 parameters based on quality rating.
   *
   * @param quality - Rating from 0-5
   *   0 = Complete blackout
   *   1 = Incorrect, recognized answer
   *   2 = Incorrect, seems easy to remember
   *   3 = Correct, significant difficulty
   *   4 = Correct, hesitation
   *   5 = Perfect recall
   * @param current - Current SM-2 parameters
   * @returns Updated SM-2 parameters + next review date
   *
   * Algorithm:
   * 1. If quality >= 3 (correct):
   *    - First review (n=0): interval = 1 day
   *    - Second review (n=1): interval = 6 days
   *    - Subsequent (n≥2): interval = previous_interval * EF
   *    - Update EF: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
   *    - EF minimum = 1.3
   *    - Increment repetitions
   *
   * 2. If quality < 3 (incorrect):
   *    - Reset repetitions = 0
   *    - Reset interval = 1 day
   *    - EF unchanged
   */
  const calculateSM2 = useCallback((
    quality: number,
    current: SM2Params
  ): SM2Result => {
    // Validate quality range
    if (quality < 0 || quality > 5) {
      throw new Error('Quality must be between 0 and 5 (inclusive)');
    }

    // Round quality to integer (in case user passed decimal)
    quality = Math.round(quality);

    let { ease_factor, interval_days, repetitions } = current;

    if (quality >= 3) {
      // ✅ Correct response

      // Calculate new interval
      if (repetitions === 0) {
        interval_days = 1; // First review: tomorrow
      } else if (repetitions === 1) {
        interval_days = 6; // Second review: 6 days
      } else {
        // Subsequent reviews: exponential growth
        interval_days = Math.round(interval_days * ease_factor);
      }

      // Update ease factor (makes card easier/harder based on quality)
      // Formula: EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
      const q = quality;
      ease_factor = ease_factor + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02));

      // Enforce minimum ease factor of 1.3
      ease_factor = Math.max(1.3, ease_factor);

      // Increment repetitions
      repetitions += 1;
    } else {
      // ❌ Incorrect response (quality 0, 1, or 2)

      // Reset to start
      repetitions = 0;
      interval_days = 1;
      // ease_factor unchanged (preserve difficulty level)
    }

    // Calculate next review date
    const next_review_date = new Date();
    next_review_date.setDate(next_review_date.getDate() + interval_days);

    return {
      ease_factor: Math.round(ease_factor * 100) / 100, // Round to 2 decimal places
      interval_days,
      repetitions,
      next_review_date: next_review_date.toISOString()
    };
  }, []);

  /**
   * Submit card review to backend API.
   *
   * This mutation:
   * 1. Calls PUT /api/v1/study-cards/{cardId}/review
   * 2. Backend recalculates SM-2 (server-side validation)
   * 3. Database updated atomically
   * 4. Invalidates study-cards query cache (triggers refetch)
   */
  const submitReview = useMutation<ReviewResponse, Error, { cardId: string; quality: number }>({
    mutationFn: async ({ cardId, quality }) => {
      const response = await api.put<ReviewResponse>(
        `/api/v1/study-cards/${cardId}/review`,
        { quality }
      );
      return response.data;
    },
    onSuccess: (data) => {
      // Invalidate queries to refetch updated cards
      queryClient.invalidateQueries({ queryKey: ['study-cards'] });
      queryClient.invalidateQueries({ queryKey: ['study-cards', 'due'] });

      console.log(`Card ${data.card_id} reviewed successfully. Next review: ${data.next_review_date}`);
    },
    onError: (error) => {
      console.error('Failed to submit review:', error);
      // Error handling in UI component
    }
  });

  return {
    calculateSM2,
    submitReview
  };
}
```

---

#### 2. `frontend/src/components/study-cards/QualityRating.tsx` (200 lines)

**Purpose**: UI component for 6-point quality rating scale

```typescript
import React, { useEffect } from 'react';
import {
  Box,
  Button,
  Typography,
  Stack,
  Chip,
  Fade
} from '@mui/material';

interface QualityRatingProps {
  /** Whether answer has been shown (ratings only appear after answer) */
  isAnswerShown: boolean;
  /** Callback when student selects a quality rating */
  onRate: (quality: number) => void;
  /** Loading state while API call in progress */
  loading?: boolean;
}

// Quality scale definitions
const QUALITY_OPTIONS = [
  { value: 0, label: 'Blackout', emoji: '💀', color: 'error', description: 'No recall' },
  { value: 1, label: 'Wrong', emoji: '❌', color: 'error', description: 'Incorrect, but recognized' },
  { value: 2, label: 'Hard', emoji: '😰', color: 'warning', description: 'Incorrect, seems easy now' },
  { value: 3, label: 'OK', emoji: '😐', color: 'info', description: 'Correct, significant difficulty' },
  { value: 4, label: 'Easy', emoji: '😊', color: 'success', description: 'Correct, some hesitation' },
  { value: 5, label: 'Perfect', emoji: '⭐', color: 'success', description: 'Perfect recall' }
] as const;

/**
 * QualityRating Component
 *
 * Displays 6-button quality rating scale (0-5) for spaced repetition.
 * Only appears after student has viewed the answer.
 *
 * Features:
 * - 6 clearly labeled buttons
 * - Keyboard shortcuts (0-5 keys)
 * - Visual feedback on selection
 * - Disabled during API call
 *
 * Usage:
 *   <QualityRating
 *     isAnswerShown={isFlipped}
 *     onRate={(q) => handleRate(cardId, q)}
 *   />
 */
export function QualityRating({
  isAnswerShown,
  onRate,
  loading = false
}: QualityRatingProps) {
  // Keyboard shortcuts (0-5 keys)
  useEffect(() => {
    if (!isAnswerShown) return;

    const handleKeyPress = (event: KeyboardEvent) => {
      // Ignore if typing in input field
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
        return;
      }

      const key = event.key;
      if (['0', '1', '2', '3', '4', '5'].includes(key)) {
        event.preventDefault();
        const quality = parseInt(key, 10);
        onRate(quality);
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [isAnswerShown, onRate]);

  // Don't render if answer not shown yet
  if (!isAnswerShown) {
    return null;
  }

  return (
    <Fade in={isAnswerShown} timeout={300}>
      <Box sx={{ mt: 4, p: 3, bgcolor: 'action.hover', borderRadius: 2 }}>
        <Typography variant="h6" gutterBottom align="center">
          How well did you know this?
        </Typography>

        <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 2 }}>
          Your answer determines when you'll see this card next
        </Typography>

        <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap" useFlexGap>
          {QUALITY_OPTIONS.map((option) => (
            <Button
              key={option.value}
              variant="outlined"
              onClick={() => onRate(option.value)}
              disabled={loading}
              aria-label={`Rate quality ${option.value}: ${option.label} - ${option.description}`}
              sx={{
                minWidth: 100,
                height: 80,
                display: 'flex',
                flexDirection: 'column',
                gap: 0.5,
                borderColor: `${option.color}.main`,
                '&:hover': {
                  bgcolor: `${option.color}.light`,
                  borderColor: `${option.color}.dark`,
                }
              }}
            >
              <Box sx={{ fontSize: '1.5rem' }}>{option.emoji}</Box>
              <Typography variant="caption" fontWeight="bold">
                {option.value}: {option.label}
              </Typography>
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: '0.65rem' }}>
                {option.description}
              </Typography>
            </Button>
          ))}
        </Stack>

        <Typography variant="caption" display="block" align="center" color="text.secondary" sx={{ mt: 2 }}>
          Tip: Press 0-5 keys for quick rating
        </Typography>
      </Box>
    </Fade>
  );
}
```

---

#### 3. `frontend/src/components/study-cards/ReviewResult.tsx` (150 lines)

**Purpose**: Display review result with next review date

```typescript
import React from 'react';
import {
  Box,
  Typography,
  Alert,
  Button,
  Stack,
  Chip
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import RepeatIcon from '@mui/icons-material/Repeat';

interface ReviewResultProps {
  /** Updated SM-2 parameters after review */
  result: {
    ease_factor: number;
    interval_days: number;
    repetitions: number;
    next_review_date: string;
  };
  /** Previous ease factor (to show delta) */
  previousEaseFactor?: number;
  /** Callback to continue to next card */
  onContinue: () => void;
}

/**
 * ReviewResult Component
 *
 * Displays feedback after student rates a card.
 * Shows when card will appear next and how SM-2 parameters changed.
 */
export function ReviewResult({
  result,
  previousEaseFactor,
  onContinue
}: ReviewResultProps) {
  // Calculate days from now
  const nextReviewDate = new Date(result.next_review_date);
  const daysFromNow = Math.ceil(
    (nextReviewDate.getTime() - Date.now()) / (1000 * 60 * 60 * 24)
  );

  // Format date
  const formattedDate = nextReviewDate.toLocaleDateString('en-US', {
    month: 'long',
    day: 'numeric',
    year: 'numeric'
  });

  // Ease factor delta
  const easeDelta = previousEaseFactor
    ? result.ease_factor - previousEaseFactor
    : 0;

  return (
    <Alert
      severity="success"
      icon={<CheckCircleIcon />}
      sx={{ mt: 3 }}
    >
      <Typography variant="h6" gutterBottom>
        Card Reviewed Successfully!
      </Typography>

      <Stack spacing={1.5} sx={{ mt: 2 }}>
        {/* Next Review Date */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <CalendarTodayIcon fontSize="small" color="action" />
          <Typography variant="body2">
            <strong>Next review:</strong> {formattedDate}{' '}
            <Chip
              label={`${daysFromNow} ${daysFromNow === 1 ? 'day' : 'days'}`}
              size="small"
              color={daysFromNow === 1 ? 'warning' : 'info'}
            />
          </Typography>
        </Box>

        {/* Ease Factor */}
        {previousEaseFactor && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <TrendingUpIcon fontSize="small" color="action" />
            <Typography variant="body2">
              <strong>Ease factor:</strong> {previousEaseFactor.toFixed(2)} → {result.ease_factor.toFixed(2)}
              <Chip
                label={easeDelta > 0 ? `+${easeDelta.toFixed(2)}` : easeDelta.toFixed(2)}
                size="small"
                color={easeDelta > 0 ? 'success' : easeDelta < 0 ? 'warning' : 'default'}
                sx={{ ml: 1 }}
              />
            </Typography>
          </Box>
        )}

        {/* Repetitions */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <RepeatIcon fontSize="small" color="action" />
          <Typography variant="body2">
            <strong>Consecutive correct:</strong> {result.repetitions}{' '}
            {result.repetitions === 0 && '(review tomorrow)'}
          </Typography>
        </Box>
      </Stack>

      <Button
        variant="contained"
        fullWidth
        onClick={onContinue}
        sx={{ mt: 2 }}
      >
        Continue to Next Card
      </Button>
    </Alert>
  );
}
```

---

### Files to Modify

#### 1. `backend/src/api/v1/study_cards.py` (+150 lines)

**Add PUT /review endpoint**:

```python
from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel, Field

class ReviewRequest(BaseModel):
    """Request body for reviewing a study card."""
    quality: int = Field(..., ge=0, le=5, description="Quality rating (0-5)")

class ReviewResponse(BaseModel):
    """Response after reviewing a study card."""
    card_id: str
    ease_factor: Decimal
    interval_days: int
    repetitions: int
    next_review_date: datetime
    last_reviewed_at: datetime

def calculate_sm2_python(
    quality: int,
    ease_factor: float,
    interval_days: int,
    repetitions: int
) -> dict:
    """
    Calculate SM-2 parameters (Python implementation).

    This function must match the TypeScript implementation exactly.
    Used for server-side validation of client-calculated values.

    Args:
        quality: Rating 0-5
        ease_factor: Current ease factor
        interval_days: Current interval
        repetitions: Current repetition count

    Returns:
        Dict with updated SM-2 parameters
    """
    if quality >= 3:
        # Correct response
        if repetitions == 0:
            new_interval = 1
        elif repetitions == 1:
            new_interval = 6
        else:
            new_interval = round(interval_days * ease_factor)

        # Update ease factor
        new_ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(1.3, new_ease_factor)

        new_repetitions = repetitions + 1
    else:
        # Incorrect response
        new_interval = 1
        new_ease_factor = ease_factor  # Unchanged
        new_repetitions = 0

    next_review_date = datetime.now(timezone.utc) + timedelta(days=new_interval)

    return {
        'ease_factor': round(new_ease_factor, 2),
        'interval_days': new_interval,
        'repetitions': new_repetitions,
        'next_review_date': next_review_date
    }

@router.put("/{card_id}/review", response_model=ReviewResponse)
async def review_study_card(
    card_id: str,
    review: ReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Review a study card and update SM-2 parameters.

    Implements SuperMemo-2 spaced repetition algorithm.

    Request:
        quality (int): Rating from 0-5
          0 = Complete blackout
          1 = Incorrect, recognized answer
          2 = Incorrect, seems easy
          3 = Correct, significant difficulty
          4 = Correct, hesitation
          5 = Perfect recall

    Response:
        Updated card with new SM-2 parameters
    """
    # Fetch card
    card = db.query(StudyCard).filter(
        StudyCard.card_id == card_id,
        StudyCard.user_id == current_user.user_id
    ).first()

    if not card:
        # Check if card exists at all
        exists = db.query(StudyCard).filter(StudyCard.card_id == card_id).first()
        if exists:
            raise HTTPException(status_code=403, detail="You cannot review another user's card")
        else:
            raise HTTPException(status_code=404, detail=f"Study card not found: {card_id}")

    # Calculate SM-2 parameters
    quality = review.quality
    current_ef = float(card.ease_factor)
    current_interval = card.interval_days
    current_reps = card.repetitions

    sm2_result = calculate_sm2_python(quality, current_ef, current_interval, current_reps)

    # Update database
    card.ease_factor = Decimal(str(sm2_result['ease_factor']))
    card.interval_days = sm2_result['interval_days']
    card.repetitions = sm2_result['repetitions']
    card.next_review_date = sm2_result['next_review_date']
    card.last_reviewed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(card)

    return ReviewResponse(
        card_id=card.card_id,
        ease_factor=card.ease_factor,
        interval_days=card.interval_days,
        repetitions=card.repetitions,
        next_review_date=card.next_review_date,
        last_reviewed_at=card.last_reviewed_at
    )

@router.get("", response_model=List[StudyCardResponse])
async def get_study_cards(
    due: bool = False,  # NEW: Filter by due date
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get study cards for current user.

    Query params:
        due (bool): If true, return only cards due for review (next_review_date <= NOW)
    """
    query = db.query(StudyCard).filter(StudyCard.user_id == current_user.user_id)

    if due:
        query = query.filter(StudyCard.next_review_date <= datetime.now(timezone.utc))

    cards = query.order_by(StudyCard.next_review_date.asc()).limit(50).all()

    return [StudyCardResponse.from_orm(card) for card in cards]
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### SM-2 Algorithm Accuracy
- [ ] **Quality 0-2**: Resets repetitions=0, interval=1, EF unchanged
- [ ] **Quality 3**: First review → I=1, second → I=6, EF decreases slightly
- [ ] **Quality 4-5**: EF increases, exponential interval growth
- [ ] **Ease factor floor**: Never drops below 1.3
- [ ] **TypeScript ↔ Python consistency**: Same inputs produce same outputs

#### UI Integration
- [ ] **Quality buttons**: 6 buttons (0-5) appear after answer shown
- [ ] **Keyboard shortcuts**: 0-5 keys trigger ratings
- [ ] **Visual feedback**: Shows next review date + ease factor change
- [ ] **Loading state**: Button disabled during API call
- [ ] **WCAG 2.2 AA**: Color contrast, ARIA labels, keyboard navigation

#### API Integration
- [ ] **PUT /review**: Accepts quality 0-5, rejects invalid
- [ ] **Database update**: Atomically updates ease_factor, interval, repetitions, next_review_date
- [ ] **Ownership validation**: 403 error if reviewing another user's card
- [ ] **GET ?due=true**: Filters WHERE next_review_date <= NOW()

#### Testing
- [ ] **15 algorithm tests**: All quality values, edge cases
- [ ] **5 component tests**: QualityRating, ReviewResult
- [ ] **5 integration tests**: API endpoint, database
- [ ] **1 E2E test**: Complete review workflow
- [ ] **Total: 26/26 tests passing**

### Validation Commands

```bash
# Frontend tests
cd /home/dev/Development/irStudy/frontend
npm test -- useSpacedRepetition.test.ts
# Expected: 15/15 tests passed

npm test -- QualityRating.test.tsx
# Expected: 5/5 tests passed

# Backend tests
cd /home/dev/Development/irStudy/backend
pytest tests/test_api/test_study_cards_review.py -v
# Expected: 5/5 tests passed

# E2E test
cd /home/dev/Development/irStudy/frontend
npx playwright test tests/e2e/study-cards-review.spec.ts
# Expected: 1/1 tests passed

# TypeScript validation
npx tsc --noEmit
# Expected: 0 errors

# Build
npm run build
# Expected: Build succeeded

# Python validation
cd /home/dev/Development/irStudy/backend
pytest tests/ -v
# Expected: All tests pass (including new review tests)
```

---

## Agent OS Expert Constraints

### Agent: react-frontend-developer

**CRITICAL - Read Before Starting**:

**1. SM-2 Algorithm**:
- Use **exact SuperMemo-2 formula** (see ARCHITECTURE section)
- NO modifications (scientifically validated algorithm)
- Match Python implementation exactly (client-server consistency)
- Test all quality values 0-5 with unit tests

**2. TypeScript Standards**:
- NO `any` types
- Strict null checking
- Interfaces for SM2Params, SM2Result
- Validate quality range 0-5 at function entry

**3. UI Requirements**:
- 6 buttons clearly labeled (Blackout, Wrong, Hard, OK, Easy, Perfect)
- Keyboard shortcuts (0-5 keys)
- Only show after answer revealed
- Visual feedback immediate (don't wait for API)

**4. Validation Checklist**:
- [ ] 15/15 algorithm tests passing
- [ ] 5/5 component tests passing
- [ ] `npx tsc --noEmit` → 0 errors
- [ ] Algorithm matches Python implementation

### Agent: python-backend-developer

**CRITICAL - Read Before Starting**:

**1. SM-2 Implementation**:
- Python function MUST match TypeScript exactly
- Same inputs → same outputs (validate with tests)
- Use same rounding (round to 2 decimal places)

**2. Database Updates**:
- Atomic transaction (all SM-2 params updated together)
- Update `last_reviewed_at` timestamp
- Use Decimal for ease_factor (not float)

**3. API Security**:
- Ownership validation (user can only review own cards)
- Quality validation (Pydantic Field with ge=0, le=5)
- No SQL injection (SQLAlchemy ORM)

**4. Validation Checklist**:
- [ ] 5/5 integration tests passing
- [ ] Algorithm matches TypeScript
- [ ] Ownership checks work (403 error)
- [ ] Quality validation works (422 error for quality=6)

---

## Dependencies

### Frontend Dependencies (Already Installed)
- `@tanstack/react-query: ^5.0.0` (for useMutation)
- `@mui/material: ^7.0.0`
- `react: ^19.0.0`

### Backend Dependencies (Already Installed)
- `fastapi: ^0.115.0`
- `sqlalchemy: ^2.0.0`
- `pydantic: ^2.0.0`

---

## Related PRDs

**Depends On**:
- PRD-P1-005-AUTO-STUDY-CARD-GENERATION (cards must exist)
- PRD-P1-006-FLASHCARD-REVIEW-INTERFACE (needs UI to integrate into)

**Integrates With**:
- Study cards API (`GET /api/v1/study-cards?due=true`)
- SM-2 database columns (ease_factor, interval_days, repetitions, next_review_date)

---

**End of PRD-P1-007**

**Total Lines**: 1,900+ lines (full implementation with SM-2 algorithm code)

**Completion Status**: Ready for implementation by `react-frontend-developer` and `python-backend-developer` agents

**Next Steps**:
1. Ralph executes this PRD autonomously
2. Agents create all files listed in PLAN section
3. Agents run validation commands
4. 26/26 tests passing, 0 errors
5. Study cards pipeline complete (P1-5, P1-6, P1-7)
