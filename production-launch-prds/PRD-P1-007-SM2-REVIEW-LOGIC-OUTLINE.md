# PRD OUTLINE: Spaced Repetition Review Logic (SM-2 Algorithm)

**PRD ID**: PRD-P1-007-SM2-REVIEW-LOGIC
**Category**: Frontend Logic + Backend Integration
**Priority**: P1-High (Enables Effective Knowledge Retention)
**Estimated Effort**: 5-7 hours
**Dependencies**: PRD-P1-006 (Flashcard Review Interface - needs UI to integrate ratings)
**Status**: Outline for Review
**Assigned Agents**: `react-frontend-developer`, `python-backend-developer`

**NOTE**: This is a condensed outline (360-400 lines). Full PRD will be 1,900+ lines with complete code implementations.

---

## R - REQUEST (What & Why)

### Executive Summary

Implement the **SM-2 spaced repetition algorithm** to intelligently schedule study card reviews based on student performance. When students rate flashcards (quality 0-5), the system calculates:

1. **Ease Factor** - How easy the card is (2.5 default, adjusted based on performance)
2. **Interval Days** - How many days until next review (1 day → 6 days → exponential growth)
3. **Repetitions** - Number of consecutive successful reviews
4. **Next Review Date** - Exact timestamp when card should be shown again

**Business Impact**:
- **Better retention** - Scientifically proven spaced repetition increases long-term memory by 200-300%
- **Efficient study** - Students review cards at optimal intervals (not too soon, not too late)
- **Personalized learning** - Algorithm adapts to each student's performance per card
- **Time savings** - Focus on weak areas, reduce review time for mastered cards

**Current State**: Study cards exist with static SM-2 parameters (ease_factor=2.5, interval=1, repetitions=0).

**Desired State**: Dynamic SM-2 algorithm adjusts parameters based on student quality ratings, scheduling next review dates.

### User Story

**As a** medical student reviewing study cards generated from my OSCE sessions
**I want** the system to automatically schedule my next review based on how well I know each card
**So that** I can efficiently retain clinical knowledge without manually tracking review schedules

### Success Criteria

#### Must Have (100% Required)
- [ ] **SM-2 Algorithm**: Implements standard SuperMemo-2 formula correctly
- [ ] **Quality Rating UI**: 6 buttons (0-5) for rating card difficulty after viewing answer
- [ ] **Parameter Updates**: Correctly calculates ease_factor, interval_days, repetitions, next_review_date
- [ ] **API Integration**: PUT /api/v1/study-cards/{card_id}/review endpoint updates database
- [ ] **Due Date Filtering**: Only shows cards where `next_review_date <= NOW()`
- [ ] **TypeScript Hook**: `useSpacedRepetition` hook manages algorithm logic
- [ ] **Testing**: 25+ tests (algorithm accuracy, edge cases, API integration)
- [ ] **0 Errors**: TypeScript compiles, tests pass 100%, lint passes

#### Should Have (90% Priority)
- [ ] **Visual Feedback**: Shows new interval and next review date after rating
- [ ] **Undo Last Rating**: Allows reverting if student misclicked
- [ ] **Statistics Dashboard**: Shows retention rate, average ease factor, total reviews

#### Nice to Have (Optional)
- [ ] **Custom Intervals**: Allow students to manually adjust review schedule
- [ ] **Study Streak**: Track consecutive days of review
- [ ] **Difficulty Distribution**: Chart showing easy/medium/hard cards

---

## A - ARCHITECTURE (How)

### Technical Approach

**SM-2 Algorithm Overview**:
```
Input: quality (0-5 integer)
  0 = Complete blackout
  1 = Incorrect, but recognized answer
  2 = Incorrect, but easy recall
  3 = Correct, but difficult recall
  4 = Correct, with hesitation
  5 = Perfect recall

Output: Updated SM-2 parameters
  ease_factor (EF): 1.3 minimum (quality ≥3 adjusts by formula)
  interval_days (I): Exponential growth (1 → 6 → I * EF)
  repetitions (n): Counter (increments for quality ≥3, resets to 0 for quality <3)
  next_review_date: NOW() + interval_days
```

**SM-2 Formula** (Standard SuperMemo-2):
```
IF quality >= 3 (correct response):
  IF repetitions == 0:
    interval = 1 day
  ELSE IF repetitions == 1:
    interval = 6 days
  ELSE:
    interval = previous_interval * ease_factor

  ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
  ease_factor = max(1.3, ease_factor)
  repetitions = repetitions + 1

ELSE (quality < 3 - incorrect response):
  repetitions = 0
  interval = 1 day
  ease_factor = unchanged

next_review_date = NOW() + interval (in days)
```

### Component Design

```
┌─────────────────────────────────────────────────────────────┐
│                   ReviewSession.tsx                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  FlashcardView (from P1-6)                            │  │
│  │  - Shows question/answer                              │  │
│  │  - Flip animation                                     │  │
│  │  - Navigation                                         │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Quality Rating Panel (NEW)                           │  │
│  │                                                       │  │
│  │  How well did you know this?                          │  │
│  │                                                       │  │
│  │  [0: Blackout] [1: Wrong] [2: Hard] [3: OK]           │  │
│  │  [4: Easy] [5: Perfect]                               │  │
│  │                                                       │  │
│  │  (Appears after student views answer)                 │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Next Review Info (NEW)                               │  │
│  │                                                       │  │
│  │  ✅ Card reviewed successfully!                       │  │
│  │  Next review: March 28, 2026 (6 days)                 │  │
│  │  Ease factor: 2.6                                     │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### State Management

**Frontend Hook** (`useSpacedRepetition.ts`):
```typescript
interface SM2Result {
  ease_factor: number;
  interval_days: number;
  repetitions: number;
  next_review_date: string; // ISO 8601
}

export function useSpacedRepetition() {
  const calculateSM2 = useCallback((
    quality: number, // 0-5
    current_ease_factor: number,
    current_interval_days: number,
    current_repetitions: number
  ): SM2Result => {
    // SM-2 algorithm implementation (80 lines)
  }, []);

  const submitReview = useMutation({
    mutationFn: async ({ cardId, quality }: { cardId: string; quality: number }) => {
      return api.put(`/api/v1/study-cards/${cardId}/review`, { quality });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['study-cards']);
    }
  });

  return { calculateSM2, submitReview };
}
```

**Backend API** (`backend/src/api/v1/study_cards.py`):
```python
@router.put("/{card_id}/review", response_model=StudyCardResponse)
async def review_study_card(
    card_id: str,
    review: ReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update SM-2 parameters based on student quality rating.

    Request Body:
    {
      "quality": 4  // 0-5 integer
    }

    Response:
    {
      "card_id": "...",
      "ease_factor": 2.6,
      "interval_days": 6,
      "repetitions": 2,
      "next_review_date": "2026-03-28T21:06:15Z",
      "last_reviewed_at": "2026-03-22T21:06:15Z"
    }
    """
    # Fetch card, validate ownership
    # Calculate SM-2 parameters
    # Update database
    # Return updated card
```

### Database Schema

**No migration required** - `study_cards` table already has SM-2 columns:
```sql
-- From PRD-P1-005 (Auto Study Cards)
CREATE TABLE study_cards (
    card_id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(user_id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    explanation TEXT,
    citations JSONB DEFAULT '[]'::JSONB,
    session_id UUID REFERENCES osce_attempts(attempt_id),

    -- SM-2 Parameters (already exist)
    ease_factor DECIMAL(3,2) DEFAULT 2.5,
    interval_days INTEGER DEFAULT 1,
    repetitions INTEGER DEFAULT 0,
    next_review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_reviewed_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Data Flow

```
1. Student opens review session
   ↓
2. Frontend fetches cards WHERE next_review_date <= NOW()
   GET /api/v1/study-cards?due=true
   ↓
3. Student views flashcard (P1-6 component)
   ↓
4. Student clicks "Show Answer"
   ↓
5. Quality rating panel appears (0-5 buttons)
   ↓
6. Student selects quality (e.g., 4 - "Easy")
   ↓
7. Frontend calculates new SM-2 parameters (useSpacedRepetition hook)
   quality=4, current_ease_factor=2.5, current_interval=1, repetitions=0
   → new_ease_factor=2.6, new_interval=6, new_repetitions=1
   ↓
8. Frontend sends review to backend
   PUT /api/v1/study-cards/{card_id}/review
   Body: { "quality": 4 }
   ↓
9. Backend validates + updates database
   UPDATE study_cards SET
     ease_factor = 2.6,
     interval_days = 6,
     repetitions = 1,
     next_review_date = NOW() + INTERVAL '6 days',
     last_reviewed_at = NOW()
   ↓
10. Frontend shows success message
    "✅ Next review: March 28, 2026 (6 days)"
```

---

## L - LOOP (Iterative Development)

### Phase 1: SM-2 Algorithm Implementation (2 hours)

**Deliverables**:
- `useSpacedRepetition.ts` hook with SM-2 calculation logic
- Unit tests for algorithm accuracy (15 tests covering all quality values)
- Edge case handling (minimum EF=1.3, negative quality, decimal quality)

**Validation**:
- [ ] Quality 0-2 resets repetitions to 0, interval to 1 day
- [ ] Quality 3 increases interval to 1 day (first review)
- [ ] Quality 3 increases interval to 6 days (second review)
- [ ] Quality 4-5 increases interval exponentially (I * EF)
- [ ] Ease factor never drops below 1.3
- [ ] 15/15 tests pass

### Phase 2: Quality Rating UI (2 hours)

**Deliverables**:
- `QualityRating.tsx` component with 6 buttons (0-5)
- Integration with FlashcardView (shows after answer revealed)
- Visual feedback (next review date, ease factor)
- Accessibility (ARIA labels, keyboard shortcuts 0-5)

**Validation**:
- [ ] Buttons appear only after "Show Answer" clicked
- [ ] Clicking quality button triggers SM-2 calculation
- [ ] Next review date displays correctly
- [ ] Keyboard shortcuts work (press 0-5 keys)
- [ ] WCAG 2.2 AA compliance (color contrast, ARIA labels)

### Phase 3: Backend Integration + Testing (1.5 hours)

**Deliverables**:
- API endpoint: PUT /api/v1/study-cards/{card_id}/review
- Database update logic
- Integration tests (API + database)
- E2E test (complete review flow)

**Validation**:
- [ ] API updates database correctly
- [ ] API returns updated SM-2 parameters
- [ ] API validates quality range (0-5 only)
- [ ] GET /api/v1/study-cards?due=true filters by next_review_date
- [ ] 10/10 integration tests pass

---

## P - PLAN (Detailed Implementation)

### Files to Create

**1. `frontend/src/hooks/useSpacedRepetition.ts` (250 lines)**
- Purpose: SM-2 algorithm implementation + API mutation
- Functions:
  - `calculateSM2(quality, ease_factor, interval, repetitions)` - Core algorithm
  - `submitReview(cardId, quality)` - API call
  - `getNextReviewDate(intervalDays)` - Date calculation
- Full implementation in expanded PRD

**2. `frontend/src/components/study-cards/QualityRating.tsx` (200 lines)**
- Purpose: 6-button quality rating panel
- Props: `onRate: (quality: number) => void`, `disabled: boolean`
- Material-UI components: Button, Stack, Typography, Chip
- Full implementation in expanded PRD

**3. `frontend/src/components/study-cards/ReviewSession.tsx` (300 lines)**
- Purpose: Orchestrates FlashcardView + QualityRating
- State: currentCard, isAnswerShown, reviewResult
- Integrates P1-6 FlashcardView component
- Full implementation in expanded PRD

**4. `backend/src/api/v1/study_cards.py` (+80 lines)**
- Purpose: Add PUT /review endpoint
- Existing file - modification only
- Full implementation in expanded PRD

**5. `backend/src/schemas/study_cards.py` (+20 lines)**
- Purpose: Add ReviewRequest, ReviewResponse schemas
- Existing file - modification only
- Full implementation in expanded PRD

**6. `frontend/src/components/study-cards/__tests__/useSpacedRepetition.test.ts` (350 lines)**
- Purpose: Test SM-2 algorithm accuracy
- 15+ unit tests covering all quality values
- Full implementation in expanded PRD

**7. `backend/tests/test_api/test_study_cards_review.py` (200 lines)**
- Purpose: Integration tests for review endpoint
- 10+ tests (valid review, invalid quality, ownership validation)
- Full implementation in expanded PRD

### Files to Modify

**1. `frontend/src/components/study-cards/FlashcardView.tsx` (+10 lines)**
- Add: `onAnswerShown` callback prop
- Modify: Call callback when "Show Answer" clicked
- Allows ReviewSession to show quality rating panel

**2. `frontend/src/api/studyCards.ts` (+15 lines)**
- Add: `reviewStudyCard(cardId, quality)` API function
- Uses existing axios instance

**3. `frontend/src/routes.tsx` (+1 line)**
- Add: /study-cards/review route for ReviewSession page

### Key Function Signatures (Full Code in Expanded PRD)

```typescript
// useSpacedRepetition.ts

interface SM2Params {
  ease_factor: number;
  interval_days: number;
  repetitions: number;
}

interface SM2Result extends SM2Params {
  next_review_date: string;
}

export function useSpacedRepetition() {
  /**
   * Calculate new SM-2 parameters based on quality rating.
   *
   * @param quality - Rating from 0-5 (0=blackout, 5=perfect)
   * @param current - Current SM-2 parameters
   * @returns Updated SM-2 parameters + next review date
   */
  const calculateSM2 = useCallback((
    quality: number,
    current: SM2Params
  ): SM2Result => {
    // Validate quality range
    if (quality < 0 || quality > 5) {
      throw new Error('Quality must be 0-5');
    }

    let { ease_factor, interval_days, repetitions } = current;

    if (quality >= 3) {
      // Correct response
      if (repetitions === 0) {
        interval_days = 1;
      } else if (repetitions === 1) {
        interval_days = 6;
      } else {
        interval_days = Math.round(interval_days * ease_factor);
      }

      // Update ease factor
      ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
      ease_factor = Math.max(1.3, ease_factor);

      repetitions += 1;
    } else {
      // Incorrect response
      repetitions = 0;
      interval_days = 1;
      // ease_factor unchanged
    }

    const next_review_date = new Date();
    next_review_date.setDate(next_review_date.getDate() + interval_days);

    return {
      ease_factor: Math.round(ease_factor * 100) / 100, // 2 decimal places
      interval_days,
      repetitions,
      next_review_date: next_review_date.toISOString()
    };
  }, []);

  const submitReview = useMutation({
    mutationFn: async ({ cardId, quality }: { cardId: string; quality: number }) => {
      return api.put<StudyCardResponse>(`/api/v1/study-cards/${cardId}/review`, { quality });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['study-cards']);
    }
  });

  return { calculateSM2, submitReview };
}
```

```python
# backend/src/api/v1/study_cards.py

class ReviewRequest(BaseModel):
    quality: int = Field(..., ge=0, le=5, description="Quality rating (0-5)")

class ReviewResponse(BaseModel):
    card_id: str
    ease_factor: Decimal
    interval_days: int
    repetitions: int
    next_review_date: datetime
    last_reviewed_at: datetime

@router.put("/{card_id}/review", response_model=ReviewResponse)
async def review_study_card(
    card_id: str,
    review: ReviewRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update SM-2 parameters based on student quality rating.

    Implements SuperMemo-2 algorithm for spaced repetition.
    """
    # Fetch card
    card = db.query(StudyCard).filter(
        StudyCard.card_id == card_id,
        StudyCard.user_id == current_user.user_id
    ).first()

    if not card:
        raise HTTPException(status_code=404, detail="Study card not found")

    # Calculate SM-2 parameters (Python implementation)
    quality = review.quality
    ease_factor = float(card.ease_factor)
    interval_days = card.interval_days
    repetitions = card.repetitions

    if quality >= 3:
        # Correct response
        if repetitions == 0:
            interval_days = 1
        elif repetitions == 1:
            interval_days = 6
        else:
            interval_days = round(interval_days * ease_factor)

        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        ease_factor = max(1.3, ease_factor)
        repetitions += 1
    else:
        # Incorrect response
        repetitions = 0
        interval_days = 1

    # Update database
    card.ease_factor = Decimal(str(round(ease_factor, 2)))
    card.interval_days = interval_days
    card.repetitions = repetitions
    card.next_review_date = datetime.now(timezone.utc) + timedelta(days=interval_days)
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
```

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria Checklist

#### SM-2 Algorithm Accuracy
- [ ] **Quality 0**: Resets repetitions=0, interval=1 day, EF unchanged
- [ ] **Quality 1**: Resets repetitions=0, interval=1 day, EF unchanged
- [ ] **Quality 2**: Resets repetitions=0, interval=1 day, EF unchanged
- [ ] **Quality 3**: First review → interval=1 day, second review → interval=6 days
- [ ] **Quality 4**: Increases EF, exponential interval growth
- [ ] **Quality 5**: Maximum EF increase, exponential interval growth
- [ ] **Ease Factor**: Never drops below 1.3
- [ ] **Date Calculation**: next_review_date = NOW() + interval_days (accurate)

#### UI Integration
- [ ] **Quality Rating Panel**: Appears after answer shown
- [ ] **6 Buttons**: 0-5 quality values, clear labels
- [ ] **Visual Feedback**: Shows next review date and ease factor after rating
- [ ] **Keyboard Shortcuts**: Press 0-5 keys to rate
- [ ] **Disabled State**: Cannot rate before answer shown
- [ ] **Loading State**: Shows spinner while submitting review

#### API Integration
- [ ] **PUT /api/v1/study-cards/{card_id}/review**: Accepts quality (0-5)
- [ ] **Database Update**: Correctly updates ease_factor, interval_days, repetitions, next_review_date
- [ ] **Ownership Validation**: Only card owner can review
- [ ] **Quality Validation**: Rejects quality <0 or >5
- [ ] **GET ?due=true**: Filters cards WHERE next_review_date <= NOW()

#### Code Quality
- [ ] **TypeScript**: 0 errors (`npx tsc --noEmit`)
- [ ] **Lint**: 0 errors (`npm run lint`)
- [ ] **Build**: Succeeds (`npm run build`)
- [ ] **Frontend Tests**: 15/15 passing (algorithm tests)
- [ ] **Backend Tests**: 10/10 passing (API tests)

### Testing Requirements Summary

**Frontend Unit Tests** (Full code in expanded PRD):
- `test('quality 0 resets repetitions and interval')`
- `test('quality 3 first review sets interval to 1 day')`
- `test('quality 3 second review sets interval to 6 days')`
- `test('quality 4 increases ease factor correctly')`
- `test('quality 5 increases ease factor to maximum')`
- `test('ease factor never drops below 1.3')`
- `test('interval grows exponentially for quality >= 3')`
- `test('next review date calculated correctly')`
- ... 7 more tests

**Backend Integration Tests**:
- `test_review_study_card_valid_quality_3()`
- `test_review_study_card_valid_quality_5()`
- `test_review_study_card_invalid_quality_6()`
- `test_review_study_card_ownership_validation()`
- `test_get_due_study_cards()`
- ... 5 more tests

**E2E Test** (Playwright):
```typescript
test('Student reviews flashcard with quality rating', async ({ page }) => {
  await page.goto('/study-cards/review');

  // Card appears
  await expect(page.locator('[data-testid="flashcard-question"]')).toBeVisible();

  // Show answer
  await page.click('button:has-text("Show Answer")');

  // Quality rating panel appears
  await expect(page.locator('[data-testid="quality-rating"]')).toBeVisible();

  // Select quality 4
  await page.click('[data-testid="quality-4"]');

  // Success message
  await expect(page.locator('text=Next review:')).toBeVisible();
});
```

### Validation Commands Summary

```bash
# TypeScript validation
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit
# Expected: 0 errors

# Frontend tests
npm test -- useSpacedRepetition.test.ts
# Expected: 15/15 tests passed

# Backend tests
cd /home/dev/Development/irStudy/backend
pytest tests/test_api/test_study_cards_review.py -v
# Expected: 10/10 tests passed

# Build test
cd /home/dev/Development/irStudy/frontend
npm run build
# Expected: Build succeeded

# Manual test: Review a card
# 1. Login as student
# 2. Navigate to /study-cards/review
# 3. View flashcard question
# 4. Click "Show Answer"
# 5. Select quality rating (0-5)
# 6. Verify next review date displayed
# 7. Check database: SELECT next_review_date FROM study_cards WHERE card_id = '...'
# Expected: next_review_date = NOW() + interval_days
```

---

## Agent OS Expert Constraints

### Agent: react-frontend-developer

**CRITICAL - Read Before Starting**:

**1. SM-2 Algorithm Implementation**:
- Use **exact SuperMemo-2 formula** (see ARCHITECTURE section)
- NO modifications to algorithm (it's scientifically validated)
- Edge cases:
  - Quality <0 or >5: throw error
  - Ease factor minimum: 1.3 (NEVER lower)
  - Interval rounding: Math.round() to integer days
  - Date calculation: Use native Date object, ISO 8601 format

**2. TypeScript Standards**:
- NO `any` types allowed
- Strict null checking
- Interface for SM2Params, SM2Result
- Validate quality range at function entry

**3. Integration with P1-6**:
- Reuse FlashcardView component (from PRD-P1-006)
- Add `onAnswerShown` callback prop to FlashcardView
- Quality rating panel appears ONLY after answer shown
- DO NOT modify FlashcardView's flip animation logic

**4. Accessibility Requirements (WCAG 2.2 AA)**:
- All 6 quality buttons have `aria-label`
- Keyboard shortcuts: 0-5 keys
- Focus management: Auto-focus quality rating panel after answer shown
- Screen reader: Announce next review date
- Color contrast: ≥4.5:1 for all text

**5. Validation Checklist (Complete Before Returning)**:
- [ ] `npx tsc --noEmit` → 0 errors
- [ ] `npm test -- useSpacedRepetition.test.ts` → 15/15 passed
- [ ] `npm run build` → Build succeeds
- [ ] Manual test: Review card, check database next_review_date is correct
- [ ] Keyboard shortcuts work (0-5 keys)

### Agent: python-backend-developer

**CRITICAL - Read Before Starting**:

**1. SM-2 Algorithm Consistency**:
- Backend algorithm MUST match frontend exactly (see ARCHITECTURE section)
- Use same formula, same rounding, same edge cases
- Test frontend + backend produce identical results for same inputs

**2. Database Schema**:
- NO migration required (columns already exist)
- Update these fields:
  - ease_factor (DECIMAL 3,2)
  - interval_days (INTEGER)
  - repetitions (INTEGER)
  - next_review_date (TIMESTAMP)
  - last_reviewed_at (TIMESTAMP)

**3. Security Requirements**:
- Ownership validation: current_user.user_id == card.user_id
- Quality validation: 0 <= quality <= 5 (Pydantic Field constraint)
- NO SQL injection (use SQLAlchemy ORM)
- Rate limiting: 100 reviews per minute per user (prevent abuse)

**4. API Specification**:
- Endpoint: PUT /api/v1/study-cards/{card_id}/review
- Request: `{ "quality": 4 }`
- Response: Updated SM-2 parameters + timestamps
- Error codes:
  - 404: Card not found
  - 422: Invalid quality value
  - 429: Rate limit exceeded

**5. Validation Checklist (Complete Before Returning)**:
- [ ] `pytest tests/test_api/test_study_cards_review.py -v` → 10/10 passed
- [ ] Manual test: Call API, verify database updated
- [ ] Security test: Cannot review another user's card (403 error)
- [ ] Edge case test: Quality=6 returns 422 error

---

## Dependencies

### NPM Packages (Already Installed)
- `@mui/material: ^7.0.0`
- `@tanstack/react-query: ^5.0.0` (for useMutation)
- `react: ^19.0.0`
- `react-dom: ^19.0.0`

### Python Packages (Already Installed)
- `fastapi: ^0.115.0`
- `sqlalchemy: ^2.0.0`
- `pydantic: ^2.0.0`

### Internal Dependencies
- PRD-P1-006 (Flashcard Review Interface) - MUST complete first
- PRD-P1-005 (Auto Study Cards) - Provides SM-2 column schema

---

## Related PRDs

**Depends On**:
- PRD-P1-006-FLASHCARD-REVIEW-INTERFACE (needs UI component to integrate quality ratings)
- PRD-P1-005-AUTO-STUDY-CARD-GENERATION (needs SM-2 columns in database)

**Blocks**:
- PRD-P8-002-INTEGRATION-TESTING (needs complete study cards pipeline)

**Integrates With**:
- Study cards API (`/api/v1/study-cards`)
- Flashcard review interface (Material-UI components)

---

**End of PRD-P1-007 OUTLINE**

**Total Lines**: 395 lines (outline format)
**Full PRD Expansion**: Will be 1,900+ lines with complete code implementations

**Next Steps**:
1. User reviews this outline (along with P1-5 and P1-6 outlines)
2. User provides feedback/approval
3. Expand to full PRD with maximum code detail
4. Create PRD-P8-002 outline (Integration Testing)

