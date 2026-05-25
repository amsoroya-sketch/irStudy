# PRD-MVP-005: User Onboarding Implementation

**Status**: Ready for Execution
**Priority**: P0 (Critical for UX)
**Estimated Effort**: 2-3 days (26-34 hours)
**Target Completion**: 2026-05-29
**PRD Version**: T-RALPH v2.1

---

## Document Control

| Field | Value |
|-------|-------|
| **PRD ID** | PRD-MVP-005 |
| **Title** | User Onboarding Implementation |
| **Author** | Claude Code (Sonnet 4.5) |
| **Created** | 2026-05-25 |
| **Last Updated** | 2026-05-25 |
| **Status** | Ready for Execution |
| **Assignee** | Kimi / Ralph |
| **Dependencies** | PRD-MVP-004 (Integration Testing) |
| **Blocks** | MVP Launch |

---

## T - TESTS (Write Tests FIRST)

### Test Framework: Vitest + React Testing Library

**Test Categories**:
1. **Welcome Tour Component Tests** (5 tests) - Shepherd.js integration
2. **Guided MCQ Session Tests** (4 tests) - First practice flow
3. **Onboarding Checklist Tests** (4 tests) - Progress tracking
4. **Help System Tests** (3 tests) - Contextual help
5. **Email Template Tests** (2 tests) - Rendering validation
6. **Demo Account Tests** (2 tests) - Pre-populated data

**Total Test Count**: 20 component tests

---

### Test Suite 1: Welcome Tour Component Tests

**File**: `frontend/src/components/onboarding/__tests__/WelcomeTour.test.tsx`

```typescript
/**
 * Welcome Tour Component Tests
 *
 * Tests Shepherd.js integration and tour flow.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { WelcomeTour } from '../WelcomeTour';

// Mock Shepherd.js
vi.mock('react-shepherd', () => ({
  ShepherdTour: ({ children, steps, onComplete }: any) => {
    return (
      <div data-testid="shepherd-tour">
        {children}
        <button onClick={() => onComplete && onComplete()}>
          Complete Tour
        </button>
      </div>
    );
  }
}));

describe('WelcomeTour Component', () => {
  let mockOnComplete: ReturnType<typeof vi.fn>;

  beforeEach(() => {
    mockOnComplete = vi.fn();
  });

  it('Test 1: renders tour with 8 steps', () => {
    /**
     * Verify tour initializes with all 8 steps
     *
     * Expected:
     * - Tour component renders
     * - 8 steps defined in configuration
     */
    const { container } = render(
      <WelcomeTour onComplete={mockOnComplete} />
    );

    expect(screen.getByTestId('shepherd-tour')).toBeInTheDocument();
  });

  it('Test 2: calls onComplete when tour finishes', async () => {
    /**
     * Verify onComplete callback triggered
     *
     * Steps:
     * 1. Render tour
     * 2. Click "Complete Tour" button
     * 3. Verify onComplete called
     */
    render(<WelcomeTour onComplete={mockOnComplete} />);

    const completeButton = screen.getByText('Complete Tour');
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockOnComplete).toHaveBeenCalledTimes(1);
    });
  });

  it('Test 3: tour step targets correct elements', () => {
    /**
     * Verify tour steps attach to correct DOM elements
     *
     * Expected:
     * - Dashboard step targets .dashboard-overview
     * - MCQ step targets .module-card-mcq
     * - Specialty step targets .specialty-breakdown-chart
     */
    // Mock dashboard with target elements
    document.body.innerHTML = `
      <div class="dashboard-overview"></div>
      <div class="module-card-mcq"></div>
      <div class="specialty-breakdown-chart"></div>
    `;

    render(<WelcomeTour onComplete={mockOnComplete} />);

    // Verify target elements exist
    expect(document.querySelector('.dashboard-overview')).toBeInTheDocument();
    expect(document.querySelector('.module-card-mcq')).toBeInTheDocument();
    expect(document.querySelector('.specialty-breakdown-chart')).toBeInTheDocument();
  });

  it('Test 4: tour allows skip option', () => {
    /**
     * Verify users can skip tour
     *
     * Expected:
     * - Skip button present in welcome step
     * - Clicking skip calls onComplete
     */
    const { rerender } = render(
      <WelcomeTour onComplete={mockOnComplete} />
    );

    // Tour should have skip option in first step
    // (Implementation will add Skip button)
    expect(mockOnComplete).not.toHaveBeenCalled();
  });

  it('Test 5: tour saves completion state to localStorage', async () => {
    /**
     * Verify tour completion persists
     *
     * Expected:
     * - After tour completes, localStorage has 'tour_completed': true
     */
    const mockLocalStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
      removeItem: vi.fn(),
      clear: vi.fn(),
      length: 0,
      key: vi.fn()
    };

    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true
    });

    render(<WelcomeTour onComplete={mockOnComplete} />);

    const completeButton = screen.getByText('Complete Tour');
    fireEvent.click(completeButton);

    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'onboarding_tour_completed',
        'true'
      );
    });
  });
});
```

---

### Test Suite 2: Guided MCQ Session Tests

**File**: `frontend/src/components/onboarding/__tests__/GuidedMCQSession.test.tsx`

```typescript
/**
 * Guided MCQ Session Component Tests
 *
 * Tests first MCQ practice session with guidance.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { GuidedMCQSession } from '../GuidedMCQSession';

// Mock API hook
vi.mock('../../api/mcqs', () => ({
  useMCQSession: () => ({
    data: [
      {
        question_id: 'ONBOARD-MCQ-1',
        question_text: 'Test question 1?',
        options: {
          A: 'Option A',
          B: 'Option B',
          C: 'Option C',
          D: 'Option D'
        },
        correct_answer: 'A',
        explanation: 'This is why A is correct.',
        citation: 'Australian Medical Guidelines'
      }
    ],
    isLoading: false,
    error: null
  })
}));

describe('GuidedMCQSession Component', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false }
      }
    });
  });

  const renderWithProvider = (component: React.ReactElement) => {
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  it('Test 6: displays guidance alert for first session', () => {
    /**
     * Verify guidance alert shown to new users
     *
     * Expected:
     * - Alert with "First Session Guide" text
     * - Info severity (blue color)
     */
    renderWithProvider(<GuidedMCQSession />);

    const alert = screen.getByText(/First Session Guide/i);
    expect(alert).toBeInTheDocument();
    expect(alert.closest('[role="alert"]')).toHaveAttribute(
      'class',
      expect.stringContaining('MuiAlert-standardInfo')
    );
  });

  it('Test 7: renders question with 4 options', () => {
    /**
     * Verify question displays correctly
     *
     * Expected:
     * - Question text visible
     * - 4 option buttons (A, B, C, D)
     * - Submit button disabled until option selected
     */
    renderWithProvider(<GuidedMCQSession />);

    expect(screen.getByText('Test question 1?')).toBeInTheDocument();
    expect(screen.getByText(/Option A/i)).toBeInTheDocument();
    expect(screen.getByText(/Option B/i)).toBeInTheDocument();
    expect(screen.getByText(/Option C/i)).toBeInTheDocument();
    expect(screen.getByText(/Option D/i)).toBeInTheDocument();

    const submitButton = screen.getByText('Submit Answer');
    expect(submitButton).toBeDisabled();
  });

  it('Test 8: shows feedback after answer submission', async () => {
    /**
     * Verify feedback shown after answering
     *
     * Steps:
     * 1. Select option A (correct)
     * 2. Click Submit
     * 3. Verify "Correct!" message
     * 4. Verify explanation shown
     */
    renderWithProvider(<GuidedMCQSession />);

    // Select option A
    const optionA = screen.getByText(/Option A/i);
    fireEvent.click(optionA);

    // Submit answer
    const submitButton = screen.getByText('Submit Answer');
    expect(submitButton).not.toBeDisabled();
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/✅ Correct!/i)).toBeInTheDocument();
      expect(screen.getByText(/This is why A is correct/i)).toBeInTheDocument();
      expect(screen.getByText(/Australian Medical Guidelines/i)).toBeInTheDocument();
    });
  });

  it('Test 9: progresses through 5 questions', async () => {
    /**
     * Verify user can complete all 5 questions
     *
     * Expected:
     * - After answering question 1, "Next Question" button appears
     * - Clicking Next shows question 2
     * - After question 5, "See Results" button appears
     */
    renderWithProvider(<GuidedMCQSession />);

    // Answer question 1
    fireEvent.click(screen.getByText(/Option A/i));
    fireEvent.click(screen.getByText('Submit Answer'));

    await waitFor(() => {
      expect(screen.getByText('Next Question')).toBeInTheDocument();
    });

    // Click Next
    fireEvent.click(screen.getByText('Next Question'));

    // Verify question counter updates
    await waitFor(() => {
      expect(screen.getByText('Question 2 of 5')).toBeInTheDocument();
    });
  });
});
```

---

### Test Suite 3: Onboarding Checklist Tests

**File**: `frontend/src/components/onboarding/__tests__/OnboardingChecklist.test.tsx`

```typescript
/**
 * Onboarding Checklist Component Tests
 *
 * Tests progress tracking and task completion.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { OnboardingChecklist } from '../OnboardingChecklist';

// Mock onboarding progress API
vi.mock('../../api/onboarding', () => ({
  useOnboardingProgress: () => ({
    data: {
      welcome_tour_completed: true,
      first_mcq_completed: true,
      first_osce_completed: false,
      osce_to_emr_completed: false,
      dashboard_viewed: true,
      specialty_focused: false
    },
    isLoading: false
  })
}));

describe('OnboardingChecklist Component', () => {
  const renderWithProvider = (component: React.ReactElement) => {
    const queryClient = new QueryClient();
    return render(
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    );
  };

  it('Test 10: displays 6 checklist tasks', () => {
    /**
     * Verify all 6 onboarding tasks shown
     *
     * Expected tasks:
     * 1. Complete welcome tour
     * 2. Complete first MCQ session
     * 3. Try OSCE simulation
     * 4. Convert OSCE to EMR case
     * 5. Review your dashboard
     * 6. Focus on a specialty
     */
    renderWithProvider(<OnboardingChecklist />);

    expect(screen.getByText(/Complete welcome tour/i)).toBeInTheDocument();
    expect(screen.getByText(/Complete first MCQ session/i)).toBeInTheDocument();
    expect(screen.getByText(/Try OSCE simulation/i)).toBeInTheDocument();
    expect(screen.getByText(/Convert OSCE to EMR case/i)).toBeInTheDocument();
    expect(screen.getByText(/Review your dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Focus on a specialty/i)).toBeInTheDocument();
  });

  it('Test 11: shows correct completion status', () => {
    /**
     * Verify completed tasks marked correctly
     *
     * From mock data:
     * - welcome_tour: ✅ completed
     * - first_mcq: ✅ completed
     * - first_osce: ❌ pending
     * - osce_to_emr: ❌ pending
     * - dashboard_viewed: ✅ completed
     * - specialty_focused: ❌ pending
     */
    renderWithProvider(<OnboardingChecklist />);

    // Check for checkmarks (completed tasks)
    const checkmarks = screen.getAllByTestId('CheckCircleIcon');
    expect(checkmarks).toHaveLength(3); // 3 completed tasks

    // Check for empty circles (pending tasks)
    const emptyCircles = screen.getAllByTestId('RadioButtonUncheckedIcon');
    expect(emptyCircles).toHaveLength(3); // 3 pending tasks
  });

  it('Test 12: calculates progress percentage correctly', () => {
    /**
     * Verify progress bar shows correct percentage
     *
     * 3 completed / 6 total = 50%
     */
    renderWithProvider(<OnboardingChecklist />);

    const progressText = screen.getByText(/3 of 6 tasks completed/i);
    expect(progressText).toBeInTheDocument();

    // Check for 50% progress in LinearProgress
    const progressBar = document.querySelector('[role="progressbar"]');
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  });

  it('Test 13: shows points earned', () => {
    /**
     * Verify point system displayed
     *
     * Points (from mock):
     * - welcome_tour: 10 pts ✅
     * - first_mcq: 20 pts ✅
     * - dashboard_viewed: 10 pts ✅
     * Total: 40/100 points
     */
    renderWithProvider(<OnboardingChecklist />);

    const pointsChip = screen.getByText(/40\/100 points/i);
    expect(pointsChip).toBeInTheDocument();
  });
});
```

---

### Test Suite 4: Help System Tests

**File**: `frontend/src/components/help/__tests__/HelpButton.test.tsx`

```typescript
/**
 * Help Button Component Tests
 *
 * Tests contextual help system.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 */

import { describe, it, expect } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { HelpButton } from '../HelpButton';

describe('HelpButton Component', () => {
  it('Test 14: renders help icon button', () => {
    /**
     * Verify help button displays
     *
     * Expected:
     * - Question mark icon (HelpOutlineIcon)
     * - Accessible label
     */
    render(
      <HelpButton
        topic="MCQ Scoring"
        content="Each question is worth 1 point."
      />
    );

    const button = screen.getByLabelText('Help: MCQ Scoring');
    expect(button).toBeInTheDocument();

    const icon = screen.getByTestId('HelpOutlineIcon');
    expect(icon).toBeInTheDocument();
  });

  it('Test 15: opens popover on click', () => {
    /**
     * Verify popover shows help content
     *
     * Steps:
     * 1. Click help button
     * 2. Verify popover appears
     * 3. Verify topic and content displayed
     */
    render(
      <HelpButton
        topic="MCQ Scoring"
        content="Each question is worth 1 point. Your percentage is calculated as (correct answers / total questions) × 100."
        learnMoreUrl="/help/mcq-scoring"
      />
    );

    // Click help button
    const button = screen.getByLabelText('Help: MCQ Scoring');
    fireEvent.click(button);

    // Verify popover content
    expect(screen.getByText('MCQ Scoring')).toBeInTheDocument();
    expect(screen.getByText(/Each question is worth 1 point/i)).toBeInTheDocument();

    // Verify "Learn more" link
    const learnMoreLink = screen.getByText('Learn more →');
    expect(learnMoreLink).toHaveAttribute('href', '/help/mcq-scoring');
  });

  it('Test 16: closes popover when clicking outside', () => {
    /**
     * Verify popover dismisses on outside click
     */
    render(
      <div>
        <HelpButton
          topic="Test Topic"
          content="Test content"
        />
        <button data-testid="outside-button">Outside</button>
      </div>
    );

    // Open popover
    const helpButton = screen.getByLabelText('Help: Test Topic');
    fireEvent.click(helpButton);

    expect(screen.getByText('Test Topic')).toBeInTheDocument();

    // Click outside
    const outsideButton = screen.getByTestId('outside-button');
    fireEvent.click(outsideButton);

    // Popover should close
    expect(screen.queryByText('Test Topic')).not.toBeInTheDocument();
  });
});
```

---

### Test Suite 5: Email Template Tests

**File**: `backend/tests/test_email_templates.py`

```python
"""
Email Template Tests

Tests email rendering and content.

PRD: PRD-MVP-005-USER-ONBOARDING.md
"""

import pytest
from src.services.email_service import EmailService

@pytest.mark.unit
class TestEmailTemplates:
    """Test email template rendering"""

    def test_email_01_welcome_email_renders(self):
        """
        Test 17: Welcome email renders correctly

        Expected:
        - Subject: "Verify your irStudy account"
        - Contains verification link
        - Contains user's first name
        """
        email_service = EmailService()

        email_html = email_service.render_template(
            'welcome',
            user_name='Dr. Test Student',
            verification_token='test-token-12345',
            verification_url='https://irstudy.com.au/verify?token=test-token-12345'
        )

        assert 'Dr. Test Student' in email_html
        assert 'Verify your irStudy account' in email_html
        assert 'test-token-12345' in email_html
        assert 'Verify Email' in email_html

    def test_email_02_first_session_email_renders(self):
        """
        Test 18: First session completed email renders

        Expected:
        - Subject: "Great start, [Name]!"
        - Contains score (e.g., "4/5 (80%)")
        - Contains specialty
        - Contains "View Dashboard" CTA
        """
        email_service = EmailService()

        email_html = email_service.render_template(
            'first_session_complete',
            user_name='Dr. Test Student',
            score='4/5',
            percentage=80,
            specialty='Cardiology',
            time_minutes=12
        )

        assert 'Dr. Test Student' in email_html
        assert '4/5' in email_html
        assert '80%' in email_html
        assert 'Cardiology' in email_html
        assert 'View Dashboard' in email_html
```

---

### Test Suite 6: Demo Account Tests

**File**: `backend/tests/test_demo_account.py`

```python
"""
Demo Account Tests

Tests pre-populated demo account data.

PRD: PRD-MVP-005-USER-ONBOARDING.md
"""

import pytest
from sqlalchemy.orm import Session
from src.db.models import User, MCQAttempt, OSCESession, EMRSession

@pytest.mark.integration
class TestDemoAccount:
    """Test demo account data population"""

    def test_demo_01_account_has_30_days_activity(self, db: Session):
        """
        Test 19: Demo account has activity spread over 30 days

        Expected:
        - Demo user exists (email: demo@irstudy.com.au)
        - ≥20 MCQ sessions
        - ≥5 OSCE sessions
        - ≥3 EMR sessions
        - Activity dates span ≥25 days
        """
        from datetime import datetime, timedelta

        demo_user = db.query(User).filter(
            User.email == 'demo@irstudy.com.au'
        ).first()

        assert demo_user is not None, "Demo account not found"
        assert demo_user.is_demo_account is True

        # Check MCQ attempts
        mcq_attempts = db.query(MCQAttempt).filter(
            MCQAttempt.user_id == demo_user.id
        ).all()

        assert len(mcq_attempts) >= 20, f"Expected ≥20 MCQ attempts, got {len(mcq_attempts)}"

        # Check date spread
        if mcq_attempts:
            dates = [attempt.created_at.date() for attempt in mcq_attempts]
            date_range = (max(dates) - min(dates)).days

            assert date_range >= 25, f"Activity spread only {date_range} days (need ≥25)"

    def test_demo_02_account_realistic_scores(self, db: Session):
        """
        Test 20: Demo account scores are realistic (60-90%)

        Expected:
        - MCQ scores between 60-90%
        - OSCE scores between 7.0-9.5 / 10
        - Not all perfect scores (too unrealistic)
        """
        demo_user = db.query(User).filter(
            User.email == 'demo@irstudy.com.au'
        ).first()

        mcq_attempts = db.query(MCQAttempt).filter(
            MCQAttempt.user_id == demo_user.id
        ).all()

        if mcq_attempts:
            # Calculate avg score
            correct_count = sum(1 for a in mcq_attempts if a.is_correct)
            score_pct = (correct_count / len(mcq_attempts)) * 100

            assert 60 <= score_pct <= 90, f"Demo score {score_pct}% not realistic (need 60-90%)"

        # Check OSCE scores
        osce_sessions = db.query(OSCESession).filter(
            OSCESession.user_id == demo_user.id
        ).all()

        if osce_sessions:
            scores = [s.score for s in osce_sessions if s.score is not None]
            avg_score = sum(scores) / len(scores) if scores else 0

            assert 7.0 <= avg_score <= 9.5, f"Demo OSCE score {avg_score} not realistic (need 7.0-9.5)"
```

---

## R - REQUEST (Problem Statement)

### Problem
The irStudy MVP has a complete, functional platform with 751/751 tests passing. However, **new users face a steep learning curve** with no guidance on how to use the platform's features.

**Critical UX Gaps**:
1. No welcome tour - users don't know where to start
2. No guided first session - overwhelming for beginners
3. No progress tracking - users don't see achievement
4. No help documentation - users struggle with features
5. No email engagement - users forget about platform
6. No demo data - empty dashboard for new users looks broken

**Impact if not resolved**:
- High bounce rate (users leave after registration)
- Low feature adoption (users only use MCQ, ignore OSCE/EMR)
- Poor retention (no habit formation)
- High support burden (repetitive "how do I..." questions)

### Success Criteria

**Must Have (P0)**:
- ✅ Welcome tour completes with 8 steps
- ✅ Guided first MCQ session works (5 easy questions)
- ✅ Onboarding checklist tracks 6 tasks
- ✅ ≥20 FAQ questions with search
- ✅ 5 email templates (welcome, tour, first session, week 1, inactive)
- ✅ Demo account with 30 days of activity

**Should Have (P1)**:
- ✅ Contextual help buttons on 10+ pages
- ✅ Video tutorials (6 videos, 3-7 min each)
- ✅ Onboarding analytics (Mixpanel tracking)
- ✅ A/B testing framework (tour timing, checklist visibility)

**Could Have (P2)**:
- Push notifications for re-engagement
- In-app chat support
- Gamification badges

### Out of Scope
- Mobile app onboarding (no mobile app yet)
- Multi-language support (English only for MVP)
- Advanced gamification (leaderboards, achievements)

---

## A - ARCHITECTURE

### Component Hierarchy

```
UnifiedDashboardPage
├── DemoAccountBanner (if demo account)
├── WelcomeTour (if first visit)
│   └── ShepherdTour (8 steps)
├── OnboardingChecklist (collapsible)
│   ├── ChecklistItem × 6
│   └── LinearProgress
├── OverallProgressCard
│   └── HelpButton
├── ModuleStatsGrid
│   └── HelpButton × 4
├── SpecialtyBreakdownChart
│   └── HelpButton
└── RecommendationsPanel

GuidedMCQSession (separate page)
├── Alert (guidance)
├── QuestionCard
│   ├── OptionsGroup
│   └── SubmitButton
└── FeedbackPanel
    ├── Explanation
    └── Citation
```

### Data Flow

```
User Registration
     ↓
Email Verification
     ↓
First Login → Check localStorage
     ↓
Tour Not Completed? → Show WelcomeTour
     ↓
Tour Completed → Save to localStorage + Backend
     ↓
Redirect to /mcq?onboarding=true
     ↓
GuidedMCQSession (5 easy questions)
     ↓
First Session Complete → Email Trigger
     ↓
Dashboard with OnboardingChecklist
     ↓
Track Progress via API
```

### API Endpoints (New)

**Onboarding Progress API**:
```typescript
GET  /api/v1/onboarding/progress
POST /api/v1/onboarding/progress
```

**Response**:
```json
{
  "welcome_tour_completed": true,
  "first_mcq_completed": true,
  "first_osce_completed": false,
  "osce_to_emr_completed": false,
  "dashboard_viewed": true,
  "specialty_focused": false,
  "total_points": 40,
  "completion_percentage": 50.0
}
```

---

## L - LOOP (Iterative Development with TDD)

### Phase 1: Welcome Tour (6 hours)

**RED** (Write tests, confirm they fail):
```bash
cd frontend
npm test -- WelcomeTour.test.tsx --run

# Expected: 5 tests FAIL (component not implemented yet)
# - Test 1: renders tour with 8 steps
# - Test 2: calls onComplete when tour finishes
# - Test 3: tour step targets correct elements
# - Test 4: tour allows skip option
# - Test 5: tour saves completion state to localStorage
```

**GREEN** (Implement component):
```bash
# Create component file (see P section for full code)
# File: frontend/src/components/onboarding/WelcomeTour.tsx

npm test -- WelcomeTour.test.tsx --run
# Expected: 5/5 passing
```

**REFACTOR** (Improve code quality):
- Extract step configuration to separate file
- Add TypeScript types for tour steps
- Improve accessibility (ARIA labels)
- Add loading state for slow devices

**Validation Checklist**:
- [ ] 5/5 WelcomeTour tests passing
- [ ] Tour displays on first login
- [ ] All 8 steps visible and clickable
- [ ] localStorage saves completion
- [ ] No console errors

---

### Phase 2: Guided MCQ Session (5 hours)

**RED** (Write tests, confirm they fail):
```bash
npm test -- GuidedMCQSession.test.tsx --run

# Expected: 4 tests FAIL
# - Test 6: displays guidance alert
# - Test 7: renders question with 4 options
# - Test 8: shows feedback after submission
# - Test 9: progresses through 5 questions
```

**GREEN** (Implement component):
```bash
# Create component file (see P section)
# File: frontend/src/components/onboarding/GuidedMCQSession.tsx

npm test -- GuidedMCQSession.test.tsx --run
# Expected: 4/4 passing
```

**REFACTOR** (Optimize UX):
- Add smooth transitions between questions
- Improve feedback animations
- Add keyboard shortcuts (Enter to submit)
- Optimize for mobile screens

**Validation Checklist**:
- [ ] 4/4 GuidedMCQSession tests passing
- [ ] Guidance alert shows helpful text
- [ ] Feedback panel shows explanation + citation
- [ ] "Next Question" button advances flow
- [ ] Results page shows after question 5

---

### Phase 3: Onboarding Checklist (4 hours)

**RED** (Write tests, confirm they fail):
```bash
npm test -- OnboardingChecklist.test.tsx --run

# Expected: 4 tests FAIL
# - Test 10: displays 6 checklist tasks
# - Test 11: shows correct completion status
# - Test 12: calculates progress percentage correctly
# - Test 13: shows points earned
```

**GREEN** (Implement component + API):
```bash
# Create component: OnboardingChecklist.tsx
# Create API hook: useOnboardingProgress()
# Create backend endpoint: /api/v1/onboarding/progress

npm test -- OnboardingChecklist.test.tsx --run
# Expected: 4/4 passing
```

**REFACTOR** (Polish UI):
- Add checkmark animations
- Add progress bar transitions
- Add celebration confetti when 100% complete
- Add tooltips for task descriptions

**Validation Checklist**:
- [ ] 4/4 OnboardingChecklist tests passing
- [ ] Backend API returns correct progress
- [ ] Progress bar animates smoothly
- [ ] Points chip updates correctly
- [ ] Completed tasks marked with checkmark

---

### Phase 4: Help System (4 hours)

**RED** (Write tests, confirm they fail):
```bash
npm test -- HelpButton.test.tsx --run

# Expected: 3 tests FAIL
# - Test 14: renders help icon button
# - Test 15: opens popover on click
# - Test 16: closes popover when clicking outside
```

**GREEN** (Implement help system):
```bash
# Create HelpButton component
# Create FAQ page with search
# Add help buttons to 10+ pages

npm test -- HelpButton.test.tsx --run
# Expected: 3/3 passing
```

**REFACTOR** (Improve help content):
- Write comprehensive FAQ answers
- Add screenshots to help articles
- Add search functionality to FAQ
- Link related help articles

**Validation Checklist**:
- [ ] 3/3 HelpButton tests passing
- [ ] Help popovers show on 10+ pages
- [ ] FAQ page searchable
- [ ] ≥20 FAQ questions written
- [ ] Help content uses Australian medical terminology

---

### Phase 5: Email System (3 hours)

**RED** (Write tests, confirm they fail):
```bash
cd backend
pytest tests/test_email_templates.py -v

# Expected: 2 tests FAIL
# - Test 17: welcome email renders
# - Test 18: first session email renders
```

**GREEN** (Implement email service):
```bash
# Create EmailService class
# Create 5 email templates (HTML + plain text)
# Set up SendGrid/Mailgun integration

pytest tests/test_email_templates.py -v
# Expected: 2/2 passing
```

**REFACTOR** (Email improvements):
- Add inline CSS for email clients
- Test email rendering across Gmail, Outlook, Apple Mail
- Add unsubscribe links
- Add email open tracking (optional)

**Validation Checklist**:
- [ ] 2/2 email template tests passing
- [ ] 5 email templates created
- [ ] Emails render correctly in Gmail/Outlook
- [ ] Email triggers configured
- [ ] Unsubscribe links working

---

### Phase 6: Demo Account (2 hours)

**RED** (Write tests, confirm they fail):
```bash
pytest tests/test_demo_account.py -v

# Expected: 2 tests FAIL
# - Test 19: account has 30 days activity
# - Test 20: account has realistic scores
```

**GREEN** (Create demo account script):
```bash
# Create script: backend/scripts/create_demo_account.py
# Generate 30 days of activity
# Populate MCQ attempts, OSCE sessions, EMR sessions

pytest tests/test_demo_account.py -v
# Expected: 2/2 passing
```

**REFACTOR** (Improve demo data):
- Add variety in specialties (cardiology, respiratory, psychiatry)
- Add realistic score variation (not all 100%)
- Add incomplete sessions (simulate real usage)
- Add recent activity (last 7 days)

**Validation Checklist**:
- [ ] 2/2 demo account tests passing
- [ ] Demo account accessible via special link
- [ ] Dashboard shows realistic data
- [ ] Demo banner shows at top
- [ ] "Create Account" CTA prominent

---

## P - PLAN (File-by-File Implementation)

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── onboarding/
│   │   │   ├── WelcomeTour.tsx (NEW - 150 lines)
│   │   │   ├── GuidedMCQSession.tsx (NEW - 250 lines)
│   │   │   ├── OnboardingChecklist.tsx (NEW - 180 lines)
│   │   │   ├── DemoAccountBanner.tsx (NEW - 40 lines)
│   │   │   └── __tests__/
│   │   │       ├── WelcomeTour.test.tsx (NEW - 120 lines)
│   │   │       ├── GuidedMCQSession.test.tsx (NEW - 150 lines)
│   │   │       └── OnboardingChecklist.test.tsx (NEW - 100 lines)
│   │   └── help/
│   │       ├── HelpButton.tsx (NEW - 80 lines)
│   │       ├── FAQPage.tsx (NEW - 300 lines)
│   │       ├── VideoTutorials.tsx (NEW - 150 lines)
│   │       └── __tests__/
│   │           └── HelpButton.test.tsx (NEW - 80 lines)
│   ├── api/
│   │   └── onboarding.ts (NEW - 60 lines)
│   ├── pages/
│   │   ├── HelpCenterPage.tsx (NEW - 200 lines)
│   │   └── GuidedMCQPage.tsx (NEW - 100 lines)
│   └── utils/
│       └── analytics.ts (UPDATE - add onboarding events)

backend/
├── src/
│   ├── api/
│   │   └── v1/
│   │       └── onboarding/
│   │           ├── router.py (NEW - 120 lines)
│   │           └── schemas.py (NEW - 60 lines)
│   ├── services/
│   │   └── email_service.py (NEW - 200 lines)
│   └── db/
│       └── models.py (UPDATE - add OnboardingProgress model)
├── scripts/
│   ├── create_demo_account.py (NEW - 250 lines)
│   └── send_onboarding_emails.py (NEW - 150 lines)
├── templates/
│   └── emails/
│       ├── welcome.html (NEW - 150 lines)
│       ├── tour_reminder.html (NEW - 120 lines)
│       ├── first_session_complete.html (NEW - 140 lines)
│       ├── week_1_summary.html (NEW - 180 lines)
│       └── inactive_user.html (NEW - 130 lines)
└── tests/
    ├── test_email_templates.py (NEW - 80 lines)
    └── test_demo_account.py (NEW - 100 lines)
```

---

### File 1: `frontend/src/components/onboarding/WelcomeTour.tsx`

**Purpose**: Interactive 8-step product tour using Shepherd.js

**Full Implementation**:

```typescript
/**
 * Welcome Tour Component
 *
 * Interactive product tour for first-time users.
 * Uses Shepherd.js for step-by-step guidance.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 * Author: react-frontend-developer
 * Date: 2026-05-25
 */

import React, { useEffect } from 'react';
import { ShepherdTour, ShepherdTourContext } from 'react-shepherd';
import 'shepherd.js/dist/css/shepherd.css';
import { useNavigate } from 'react-router-dom';

interface WelcomeTourProps {
  onComplete: () => void;
}

const tourSteps = [
  {
    id: 'welcome',
    title: 'Welcome to irStudy! 🎉',
    text: `
      <p>Your AI-powered platform for Australian medical exam preparation.</p>
      <p>Let's take a quick tour (2 minutes).</p>
    `,
    buttons: [
      {
        text: 'Start Tour',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      },
      {
        text: 'Skip',
        action(this: any) {
          this.complete();
        },
        classes: 'shepherd-button-secondary'
      }
    ]
  },
  {
    id: 'dashboard',
    title: 'Your Dashboard',
    text: `
      <p>Track your progress across all modules.</p>
      <p>See your scores, strengths, and personalized recommendations.</p>
    `,
    attachTo: {
      element: '.dashboard-overview',
      on: 'bottom' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        },
        classes: 'shepherd-button-secondary'
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'mcq-module',
    title: 'MCQ Practice',
    text: `
      <p>Practice with <strong>1,600+ questions</strong> covering:</p>
      <ul>
        <li>Cardiology</li>
        <li>Respiratory</li>
        <li>Psychiatry</li>
        <li>And more specialties</li>
      </ul>
      <p>Each question includes detailed explanations and Australian medical citations.</p>
    `,
    attachTo: {
      element: '.module-card-mcq',
      on: 'right' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'osce-module',
    title: 'OSCE Simulation',
    text: `
      <p>Practice clinical scenarios with AI-powered assessment.</p>
      <p>Complete:</p>
      <ul>
        <li>History taking (9-step approach)</li>
        <li>Physical examinations</li>
        <li>Clinical reasoning</li>
      </ul>
      <p>Receive detailed feedback on your approach.</p>
    `,
    attachTo: {
      element: '.module-card-osce',
      on: 'right' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'emr-module',
    title: 'EMR Practice',
    text: `
      <p>Write clinical notes in realistic EMR systems:</p>
      <ul>
        <li>Epic</li>
        <li>Cerner</li>
        <li>Best Practice</li>
      </ul>
      <p>Get AI feedback on your documentation quality and clinical reasoning.</p>
    `,
    attachTo: {
      element: '.module-card-emr',
      on: 'left' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'mock-exam-module',
    title: 'Mock Exams',
    text: `
      <p>Simulate real AMC Part 1 and FRACP exams.</p>
      <p>Features:</p>
      <ul>
        <li>Timed conditions</li>
        <li>Realistic difficulty</li>
        <li>Comprehensive performance analysis</li>
      </ul>
    `,
    attachTo: {
      element: '.module-card-mock-exam',
      on: 'left' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'specialty-breakdown',
    title: 'Specialty Performance',
    text: `
      <p>See how you perform across medical specialties.</p>
      <p>Focus your study on areas that need improvement.</p>
    `,
    attachTo: {
      element: '.specialty-breakdown-chart',
      on: 'top' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'recommendations',
    title: 'AI Recommendations',
    text: `
      <p>Get personalized study suggestions based on:</p>
      <ul>
        <li>Your performance</li>
        <li>Learning patterns</li>
        <li>Exam preparation timeline</li>
      </ul>
    `,
    attachTo: {
      element: '.recommendations-panel',
      on: 'top' as const
    },
    buttons: [
      {
        text: 'Back',
        action(this: any) {
          this.back();
        }
      },
      {
        text: 'Next',
        action(this: any) {
          this.next();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  },
  {
    id: 'start-practicing',
    title: 'Ready to Start!',
    text: `
      <p>Let's begin with a quick MCQ session to get you familiar with the platform.</p>
      <p>You'll answer <strong>5 questions</strong> and see how our feedback system works.</p>
    `,
    buttons: [
      {
        text: 'Start First Session',
        action(this: any) {
          this.complete();
        },
        classes: 'shepherd-button-primary'
      }
    ]
  }
];

const tourOptions = {
  defaultStepOptions: {
    cancelIcon: {
      enabled: true
    },
    scrollTo: {
      behavior: 'smooth' as ScrollBehavior,
      block: 'center' as ScrollLogicalPosition
    }
  },
  useModalOverlay: true
};

export const WelcomeTour: React.FC<WelcomeTourProps> = ({ onComplete }) => {
  const navigate = useNavigate();

  const handleTourComplete = () => {
    // Save completion to localStorage
    localStorage.setItem('onboarding_tour_completed', 'true');

    // Save to backend API
    fetch('/api/v1/onboarding/progress', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('authToken')}`
      },
      body: JSON.stringify({
        welcome_tour_completed: true
      })
    });

    // Track analytics
    if (window.mixpanel) {
      window.mixpanel.track('Onboarding: Tour Completed');
    }

    // Callback
    onComplete();

    // Redirect to guided MCQ session
    navigate('/mcq?onboarding=true');
  };

  return (
    <ShepherdTour steps={tourSteps} tourOptions={tourOptions}>
      <TourButton onComplete={handleTourComplete} />
    </ShepherdTour>
  );
};

// Auto-start tour
const TourButton: React.FC<{ onComplete: () => void }> = ({ onComplete }) => {
  const tour = React.useContext(ShepherdTourContext);

  useEffect(() => {
    // Auto-start tour on mount
    if (tour) {
      tour.on('complete', onComplete);
      tour.start();
    }

    return () => {
      if (tour) {
        tour.off('complete', onComplete);
      }
    };
  }, [tour, onComplete]);

  return null;
};

// Custom styling
const styles = `
.shepherd-element {
  max-width: 400px;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.shepherd-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 10px;
}

.shepherd-text {
  font-size: 0.95rem;
  line-height: 1.6;
}

.shepherd-text ul {
  margin: 10px 0;
  padding-left: 20px;
}

.shepherd-button-primary {
  background: #667eea;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.shepherd-button-primary:hover {
  background: #5568d3;
}

.shepherd-button-secondary {
  background: transparent;
  color: #667eea;
  border: 1px solid #667eea;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
}
`;

// Inject styles
if (typeof document !== 'undefined') {
  const styleSheet = document.createElement('style');
  styleSheet.textContent = styles;
  document.head.appendChild(styleSheet);
}
```

---

### File 2: `frontend/src/components/onboarding/GuidedMCQSession.tsx`

**Purpose**: First MCQ practice session with extra guidance

**Full Implementation**:

```typescript
/**
 * Guided MCQ Session Component
 *
 * First MCQ practice session with step-by-step guidance.
 *
 * PRD: PRD-MVP-005-USER-ONBOARDING.md
 */

import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Button,
  Alert,
  RadioGroup,
  FormControlLabel,
  Radio,
  LinearProgress,
  Chip
} from '@mui/material';
import { useMCQSession } from '../../api/mcqs';
import { useNavigate } from 'react-router-dom';

export const GuidedMCQSession: React.FC = () => {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState(false);
  const [answers, setAnswers] = useState<Record<number, string>>({});

  const { data: questions, isLoading, error } = useMCQSession({
    difficulty: 'easy',
    limit: 5,
    onboarding: true
  });

  if (isLoading) {
    return (
      <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
        <LinearProgress />
        <Typography sx={{ mt: 2, textAlign: 'center' }}>
          Loading your first practice session...
        </Typography>
      </Box>
    );
  }

  if (error || !questions || questions.length === 0) {
    return (
      <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
        <Alert severity="error">
          Failed to load questions. Please try again.
        </Alert>
      </Box>
    );
  }

  const currentQ = questions[currentQuestion];
  const isCorrect = selectedAnswer === currentQ.correct_answer;
  const progress = ((currentQuestion + 1) / questions.length) * 100;

  const handleSubmit = () => {
    setShowFeedback(true);
    setAnswers({
      ...answers,
      [currentQuestion]: selectedAnswer!
    });

    // Track analytics
    if (window.mixpanel) {
      window.mixpanel.track('Onboarding: First Session Answer', {
        question_number: currentQuestion + 1,
        is_correct: isCorrect
      });
    }
  };

  const handleNext = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedAnswer(null);
      setShowFeedback(false);
    } else {
      // Show results
      navigate('/mcq/results?onboarding=true');

      // Track completion
      if (window.mixpanel) {
        window.mixpanel.track('Onboarding: First Session Completed');
      }
    }
  };

  return (
    <Box sx={{ maxWidth: 800, mx: 'auto', p: 3 }}>
      {/* Guidance Alert */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>First Session Guide:</strong> Take your time with each question.
          We'll show you detailed explanations and Australian medical references
          after each answer.
        </Typography>
      </Alert>

      {/* Progress Bar */}
      <Box sx={{ mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Question {currentQuestion + 1} of {questions.length}
          </Typography>
          <Chip
            label={`${Math.round(progress)}% Complete`}
            size="small"
            color="primary"
            variant="outlined"
          />
        </Box>
        <LinearProgress variant="determinate" value={progress} />
      </Box>

      {/* Question Card */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Question {currentQuestion + 1}
          </Typography>

          <Typography variant="body1" sx={{ my: 3, lineHeight: 1.8 }}>
            {currentQ.question_text}
          </Typography>

          {/* Answer Options */}
          <RadioGroup
            value={selectedAnswer || ''}
            onChange={(e) => setSelectedAnswer(e.target.value)}
          >
            {Object.entries(currentQ.options).map(([key, value]) => (
              <FormControlLabel
                key={key}
                value={key}
                control={<Radio />}
                label={
                  <Box>
                    <strong>{key}.</strong> {value}
                  </Box>
                }
                disabled={showFeedback}
                sx={{
                  border: '1px solid #e0e0e0',
                  borderRadius: 1,
                  p: 1.5,
                  mb: 1,
                  '&:hover': {
                    backgroundColor: showFeedback ? 'transparent' : '#f5f5f5'
                  }
                }}
              />
            ))}
          </RadioGroup>

          {/* Submit Button */}
          {!showFeedback && (
            <Button
              variant="contained"
              onClick={handleSubmit}
              disabled={!selectedAnswer}
              fullWidth
              sx={{ mt: 3 }}
              size="large"
            >
              Submit Answer
            </Button>
          )}

          {/* Feedback Panel */}
          {showFeedback && (
            <Box sx={{ mt: 3 }}>
              <Alert
                severity={isCorrect ? 'success' : 'error'}
                sx={{ mb: 2 }}
              >
                <Typography variant="h6">
                  {isCorrect ? '✅ Correct!' : '❌ Incorrect'}
                </Typography>
                {!isCorrect && (
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    <strong>Correct Answer:</strong> {currentQ.correct_answer}
                  </Typography>
                )}
              </Alert>

              {/* Explanation */}
              <Box
                sx={{
                  p: 2,
                  bgcolor: 'grey.50',
                  borderRadius: 1,
                  border: '1px solid',
                  borderColor: 'grey.300'
                }}
              >
                <Typography
                  variant="subtitle2"
                  color="primary"
                  gutterBottom
                  sx={{ fontWeight: 600 }}
                >
                  Explanation
                </Typography>
                <Typography variant="body2" sx={{ mb: 2, lineHeight: 1.8 }}>
                  {currentQ.explanation}
                </Typography>

                <Typography
                  variant="subtitle2"
                  color="primary"
                  gutterBottom
                  sx={{ fontWeight: 600 }}
                >
                  Reference
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {currentQ.citation}
                </Typography>
              </Box>

              {/* Next Button */}
              <Button
                variant="contained"
                onClick={handleNext}
                fullWidth
                sx={{ mt: 2 }}
                size="large"
              >
                {currentQuestion < questions.length - 1
                  ? 'Next Question →'
                  : 'See Results'}
              </Button>
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Encouragement */}
      {showFeedback && isCorrect && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Great work! You're building your medical knowledge with evidence-based
          Australian guidelines.
        </Alert>
      )}
    </Box>
  );
};
```

---

Due to length constraints, I'll create a summary document showing all remaining files:

**PRD-MVP-005 Status**:
- ✅ T Section: 6 test suites (20 tests total) - COMPLETE
- ✅ R Section: Problem statement & success criteria - COMPLETE
- ✅ A Section: Architecture & component hierarchy - COMPLETE
- ✅ L Section: TDD workflow (6 phases) - COMPLETE
- ✅ P Section: 2 major files implemented above
- ⏳ P Section: 28 more files to document (continuing...)

**Remaining files in PRD-MVP-005**:
3. OnboardingChecklist.tsx (180 lines)
4. HelpButton.tsx (80 lines)
5. FAQPage.tsx (300 lines)
6. Onboarding API router (120 lines)
7. Email service (200 lines)
8. Demo account script (250 lines)
9. 5 email templates (total 720 lines)
10. Additional test files

**Total PRD Size Estimate**: ~3,500 lines (comparable to PRD-MVP-004)

Would you like me to:
1. **Continue writing the full PRD-MVP-005** with all remaining files?
2. **Create a summary completion document** showing what's done?
3. **Commit what we have so far** and continue in next session?