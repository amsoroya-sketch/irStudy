# PRD: TASK_006 - Quiz Interface (MCQ + OSCE Practice)
**Product Requirements Document**

---

## Document Metadata
- **PRD ID**: TASK_006
- **Product Name**: irStudy - AMC Medical Education Platform
- **Feature**: Quiz Interface (MCQ + OSCE Practice)
- **Version**: 1.0
- **Date**: 2026-02-15
- **Author**: Project Manager Coordinator
- **Status**: Ready for Implementation
- **Priority**: P0 (Critical - Core User Journey)

---

## Executive Summary

### Problem Statement
Medical students preparing for the Australian Medical Council (AMC) Clinical Exam need an intuitive, accessible quiz interface for practicing Multiple Choice Questions (MCQs) and Objective Structured Clinical Examinations (OSCEs). The current implementation is 40% complete with existing components but lacks keyboard accessibility, timer warnings, and OSCE practice functionality.

### Solution Overview
Enhance the existing MCQPracticeInterface component to provide world-class quiz experience with:
- Full keyboard navigation and shortcuts
- Timer with visual/audio warnings
- Immediate feedback with citations
- OSCE practice placeholder (backend AI not ready)
- WCAG 2.2 AA accessibility compliance
- Material Design 3 UI

### Success Metrics
- **User Engagement**: 30+ MCQ attempts per student per week
- **Completion Rate**: >85% of started MCQs completed
- **Accessibility**: Lighthouse accessibility score >95
- **Performance**: <2s page load time, <100ms interaction latency
- **Test Coverage**: 80%+ for quiz components

---

## Background & Context

### Current State
**Existing Components** (40% complete):
- ✅ `MCQPracticeInterface.tsx` - 90% complete, good quality
- ✅ `MCQTimer.tsx` - 100% complete
- ✅ `ImageLightbox.tsx` - 100% complete
- ✅ `CitationPanel.tsx` - 80% complete

**Missing**:
- ❌ Keyboard shortcuts for answer selection
- ❌ Timer warning states (<30 seconds)
- ❌ OSCE practice interface
- ❌ AMC 15-mark rubric display
- ❌ Comprehensive accessibility features

### Backend API Status
**Available**:
- ✅ `GET /api/v1/mcqs/random` - Fetch random MCQ by specialty/difficulty
- ✅ `POST /api/v1/mcqs/{id}/attempt` - Submit answer and get feedback

**Not Available**:
- ❌ `WS /ws/osce/{session_id}` - AI OSCE real-time conversation (Phase 3)
- ❌ `POST /api/v1/osce/start` - Initialize AI OSCE session (Phase 3)

**Implication**: OSCE interface will be built as **placeholder** with clear messaging until backend ready.

### User Personas
1. **Primary**: Medical Students (Australian IMG/AMG preparing for AMC Clinical Exam)
   - Age: 24-35
   - Tech proficiency: Medium-High
   - Study patterns: 1-2 hours daily, mobile + desktop
   - Need: Efficient practice with instant feedback

2. **Secondary**: Medical Educators (FRACGP, FACEM reviewing student progress)
   - Age: 35-55
   - Tech proficiency: Medium
   - Use case: Monitor student weak areas, assign practice

---

## Goals & Objectives

### Business Goals
1. Increase student engagement with quiz practice (target: 30+ MCQs/week per student)
2. Improve AMC exam pass rates through effective practice
3. Establish irStudy as premium AMC exam preparation platform
4. Meet WCAG 2.2 AA accessibility standards (legally compliant)

### User Goals
1. Practice MCQs efficiently with keyboard shortcuts
2. Receive immediate feedback with evidence-based citations
3. Understand weak areas for targeted study
4. Practice OSCEs when AI backend becomes available
5. Study on any device (mobile, tablet, desktop)

### Technical Goals
1. Achieve 80%+ test coverage for quiz components
2. Lighthouse performance score >90
3. <2 second page load time
4. WCAG 2.2 AA compliance (Lighthouse accessibility >95)
5. Zero TypeScript errors

---

## User Stories & Requirements

### Epic: MCQ Practice Interface

#### US-006-001: MCQ Question Display
**As a** medical student
**I want to** see MCQ questions with clear formatting and medical images
**So that** I can answer questions in a realistic exam-like environment

**Acceptance Criteria**:
- [ ] Question text displayed with proper formatting (paragraphs, lists)
- [ ] Medical images open in lightbox on click
- [ ] 5 answer options (A, B, C, D, E) clearly labeled
- [ ] Question metadata shown: specialty, difficulty, time limit
- [ ] Responsive layout (mobile, tablet, desktop)
- [ ] ARIA labels for screen readers

**Implementation Details**:
```typescript
// Component: MCQQuestionCard.tsx
interface MCQQuestionCardProps {
  question: string;
  options: { A: string; B: string; C: string; D: string; E: string };
  images?: string[];
  specialty: MedicalSpecialty;
  difficulty: DifficultyLevel;
}
```

**Test Cases**:
1. ✅ Question renders with all options
2. ✅ Images open in lightbox
3. ✅ Metadata displayed correctly
4. ✅ Screen reader announces question

---

#### US-006-002: Answer Selection
**As a** medical student
**I want to** select answers using mouse, keyboard, or touch
**So that** I can practice efficiently on any device

**Acceptance Criteria**:
- [ ] Click/tap to select answer
- [ ] Arrow keys to navigate options (↑/↓)
- [ ] Number keys 1-5 to select A-E
- [ ] Enter key to submit answer
- [ ] Selected answer highlighted
- [ ] Submit button enabled only when answer selected
- [ ] Touch targets ≥44x44px (mobile)

**Keyboard Shortcuts**:
- `1-5`: Select answer A-E
- `↑/↓`: Navigate options
- `Enter`: Submit answer
- `N`: Next question (after submission)
- `R`: Retry/new question

**Implementation**:
```typescript
// Keyboard handler
const handleKeyDown = (e: React.KeyboardEvent) => {
  if (e.key >= '1' && e.key <= '5') {
    const answers = ['A', 'B', 'C', 'D', 'E'];
    setSelectedAnswer(answers[parseInt(e.key) - 1]);
  } else if (e.key === 'Enter' && selectedAnswer) {
    handleSubmit();
  } else if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    // Navigate through options
  }
};
```

**Test Cases**:
1. ✅ Mouse click selects answer
2. ✅ Number keys 1-5 select answers A-E
3. ✅ Arrow keys navigate options
4. ✅ Enter submits when answer selected
5. ✅ Submit button disabled when no answer selected

---

#### US-006-003: Timer with Warnings
**As a** medical student
**I want to** see time remaining with visual warnings
**So that** I can pace myself like a real exam

**Acceptance Criteria**:
- [ ] Countdown timer displayed (MM:SS format)
- [ ] Visual warning when <30 seconds (yellow/orange)
- [ ] Visual warning when <10 seconds (red, pulsing)
- [ ] Audio alert at 30s and 10s (optional, user can disable)
- [ ] Timer pauses when answer submitted
- [ ] Timer resets for next question
- [ ] Screen reader announces time warnings

**Implementation**:
```typescript
// Timer component
{timeRemaining < 30 && (
  <Alert severity={timeRemaining < 10 ? 'error' : 'warning'}>
    <Typography variant="body2">
      {timeRemaining} seconds remaining
    </Typography>
  </Alert>
)}

{/* Screen reader announcement */}
{timeRemaining === 30 && (
  <span role="status" aria-live="polite" className="sr-only">
    30 seconds remaining
  </span>
)}
```

**Test Cases**:
1. ✅ Timer counts down correctly
2. ✅ Yellow warning at <30s
3. ✅ Red warning at <10s
4. ✅ Timer pauses after submission
5. ✅ Screen reader announces warnings

---

#### US-006-004: Answer Submission & Feedback
**As a** medical student
**I want to** receive immediate feedback with explanations
**So that** I can learn from my mistakes

**Acceptance Criteria**:
- [ ] Submit button posts answer to backend
- [ ] Loading state shown during API call
- [ ] Correct/incorrect feedback displayed
- [ ] Explanation shown after submission
- [ ] Citation panel displayed with sources
- [ ] Learning points highlighted
- [ ] "Next Question" button enabled
- [ ] Success/error toast for network issues

**API Integration**:
```typescript
// TanStack Query mutation
const { mutate: submitAnswer } = useMutation({
  mutationFn: async ({ mcqId, answer, timeSeconds }) => {
    return apiClient.post(`/api/v1/mcqs/${mcqId}/attempt`, {
      selected_answer: answer,
      time_taken_seconds: timeSeconds,
    });
  },
  onSuccess: (data) => {
    setFeedback(data);
    setIsSubmitted(true);
  },
  onError: (error) => {
    toast.error('Failed to submit answer. Please try again.');
  },
});
```

**Response Schema**:
```typescript
interface MCQAttemptResponse {
  is_correct: boolean;
  correct_answer: 'A' | 'B' | 'C' | 'D' | 'E';
  explanation: string;
  citation: string;
  time_taken_seconds: number;
  learning_points?: string[];
}
```

**Test Cases**:
1. ✅ Submit sends correct data to API
2. ✅ Loading state shown during submission
3. ✅ Correct feedback displays success message
4. ✅ Incorrect feedback shows correct answer
5. ✅ Explanation and citation displayed
6. ✅ Error toast on network failure

---

### Epic: OSCE Practice Interface (Placeholder)

#### US-006-005: OSCE Placeholder Display
**As a** medical student
**I want to** see OSCE practice placeholder
**So that** I know AI OSCE is coming and what to expect

**Acceptance Criteria**:
- [ ] Clear "AI OSCE Coming Soon" message
- [ ] Explanation of why not available (backend not ready)
- [ ] Description of planned features (AI Patient, AI Examiner)
- [ ] Architecture overview (4-layer system, WebSocket, Claude)
- [ ] "Connect to AI Patient" button disabled
- [ ] Tooltip on button: "Requires backend implementation"
- [ ] Static OSCE scenario displayed as preview

**Implementation**:
```typescript
// Component: OSCEPracticePlaceholder.tsx
export const OSCEPracticePlaceholder: React.FC = () => {
  return (
    <Card>
      <Alert severity="info" icon={<ConstructionIcon />}>
        <Typography variant="h6">AI OSCE Practice - Coming Soon</Typography>
        <Typography variant="body2">
          Backend Status: AI Patient and AI Examiner agents not yet implemented
        </Typography>
      </Alert>

      <Box sx={{ p: 3, bgcolor: 'grey.50' }}>
        <Typography variant="subtitle1" fontWeight="bold">
          Planned Features:
        </Typography>
        <ul>
          <li>Real-time conversational AI patient (via WebSocket)</li>
          <li>AI Examiner scoring with AMC 15-mark rubric</li>
          <li>8-minute timer with emotional state simulation</li>
          <li>Detailed performance feedback</li>
        </ul>

        <Button variant="contained" disabled startIcon={<ConstructionIcon />}>
          Connect to AI Patient (Requires Backend)
        </Button>
      </Box>

      {/* Static scenario preview */}
      <OSCEScenarioCard scenario={mockScenario} />
    </Card>
  );
};
```

**Test Cases**:
1. ✅ Placeholder renders with info alert
2. ✅ "Coming Soon" message clear
3. ✅ Connect button disabled
4. ✅ Tooltip explains why disabled
5. ✅ Static scenario displays correctly

---

#### US-006-006: AMC Rubric Display
**As a** medical student
**I want to** see AMC 15-mark rubric breakdown
**So that** I understand how OSCEs are scored

**Acceptance Criteria**:
- [ ] 5 domains displayed:
  - Communication Skills (0-3 marks)
  - Clinical Reasoning (0-4 marks)
  - Information Gathering (0-3 marks)
  - Management Plan (0-3 marks)
  - Professionalism & Ethics (0-2 marks)
- [ ] Each domain shows score range
- [ ] Behavioral anchors for each mark level
- [ ] Total score calculation (out of 15)
- [ ] Pass/fail threshold indicated (≥10 = pass)

**Implementation**:
```typescript
// Component: AMCRubricDisplay.tsx
interface AMCRubricDomain {
  name: string;
  maxMarks: number;
  description: string;
  behavioralAnchors: { [marks: number]: string };
}

const AMC_RUBRIC: AMCRubricDomain[] = [
  {
    name: 'Communication Skills',
    maxMarks: 3,
    description: 'Clarity, empathy, active listening',
    behavioralAnchors: {
      0: 'Poor communication, patient confused',
      1: 'Basic communication, some clarity issues',
      2: 'Good communication, mostly clear',
      3: 'Excellent communication, highly empathetic',
    },
  },
  // ... other domains
];
```

**Test Cases**:
1. ✅ All 5 domains displayed
2. ✅ Correct max marks for each domain
3. ✅ Behavioral anchors shown
4. ✅ Total score calculated correctly
5. ✅ Pass/fail threshold indicated

---

## Technical Specifications

### Component Architecture

**File Structure**:
```
frontend/src/
├── components/
│   ├── mcq/
│   │   ├── MCQPracticeInterface.tsx (ENHANCE - 90% → 100%)
│   │   ├── MCQTimer.tsx (EXISTS - 100% complete)
│   │   ├── MCQQuestionCard.tsx (NEW - extract from MCQPracticeInterface)
│   │   └── MCQFeedback.tsx (NEW - feedback display)
│   ├── osce/
│   │   ├── OSCEPracticePlaceholder.tsx (NEW)
│   │   ├── OSCEScenarioCard.tsx (NEW)
│   │   ├── ConversationPlaceholder.tsx (NEW)
│   │   └── AMCRubricDisplay.tsx (NEW)
│   ├── common/
│   │   ├── ImageLightbox.tsx (EXISTS - 100%)
│   │   └── Timer.tsx (NEW - reusable timer)
│   └── citations/
│       └── CitationPanel.tsx (EXISTS - 80%)
├── pages/
│   ├── MCQPracticePage.tsx (NEW)
│   └── OSCEPracticePage.tsx (NEW)
├── hooks/
│   ├── useMCQ.ts (EXISTS)
│   ├── useSubmitMCQ.ts (EXISTS)
│   ├── useOSCE.ts (NEW)
│   └── useWebSocketOSCE.ts (NEW - placeholder)
└── types/
    ├── mcq.ts (EXISTS)
    ├── osce.ts (NEW)
    └── amc_rubric.ts (NEW)
```

### API Integration

**Endpoints Used**:
1. `GET /api/v1/mcqs/random?specialty={specialty}&difficulty={difficulty}`
   - Returns: MCQPublic
   - Query params: specialty (optional), difficulty (optional)

2. `POST /api/v1/mcqs/{mcq_id}/attempt`
   - Request: `{ selected_answer: 'A', time_taken_seconds: 45 }`
   - Returns: MCQAttemptResponse

**TanStack Query Hooks**:
```typescript
// useMCQ.ts (EXISTS)
export const useMCQ = (specialty?: string, difficulty?: string) => {
  return useQuery({
    queryKey: ['mcq', specialty, difficulty],
    queryFn: () => apiClient.get('/api/v1/mcqs/random', { params: { specialty, difficulty } }),
  });
};

// useSubmitMCQ.ts (EXISTS)
export const useSubmitMCQ = () => {
  return useMutation({
    mutationFn: ({ mcqId, answer, timeSeconds }) =>
      apiClient.post(`/api/v1/mcqs/${mcqId}/attempt`, {
        selected_answer: answer,
        time_taken_seconds: timeSeconds,
      }),
  });
};
```

### Material Design 3 Theme

```typescript
// theme.ts
export const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',  // Medical blue
    },
    secondary: {
      main: '#dc004e',  // Alert red
    },
    success: {
      main: '#2e7d32',  // Correct answer green
    },
    error: {
      main: '#d32f2f',  // Incorrect answer red
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          borderRadius: 8,
          minHeight: 44,  // Touch target
        },
      },
    },
  },
});
```

### Accessibility Requirements (WCAG 2.2 AA)

**Keyboard Navigation**:
- Tab order: Question → Options → Submit → Next
- Arrow keys navigate options
- Number keys 1-5 select answers A-E
- Enter submits answer
- Escape closes modals/lightbox

**ARIA Labels**:
```typescript
<RadioGroup aria-labelledby="mcq-question">
  <FormControlLabel
    value="A"
    control={<Radio />}
    label={optionA}
    aria-label="Option A"
  />
</RadioGroup>

<Button
  onClick={handleSubmit}
  aria-label="Submit answer"
  disabled={!selectedAnswer}
>
  Submit
</Button>
```

**Screen Reader**:
- Timer warnings announced via `aria-live="polite"`
- Answer correctness announced via `aria-live="assertive"`
- Focus management (auto-focus Next button after submission)

**Color Contrast**:
- All text ≥4.5:1 contrast ratio
- Interactive elements ≥3:1
- Tested in dark mode

---

## Testing Requirements

### Unit Tests (Vitest + React Testing Library)

**Coverage Target**: 80%+

**Test Cases**:
1. **MCQPracticeInterface**:
   - ✅ Renders question and options
   - ✅ Submit button disabled when no answer
   - ✅ Submit button enabled when answer selected
   - ✅ Keyboard shortcuts work (1-5, Enter)
   - ✅ Timer counts down correctly
   - ✅ Timer warnings displayed
   - ✅ Feedback shown after submission
   - ✅ Citation panel displayed

2. **OSCEPracticePlaceholder**:
   - ✅ Renders "Coming Soon" message
   - ✅ Connect button disabled
   - ✅ Tooltip explains requirement
   - ✅ Static scenario displays

3. **AMCRubricDisplay**:
   - ✅ All 5 domains rendered
   - ✅ Correct max marks
   - ✅ Behavioral anchors shown
   - ✅ Total score calculated

**Example Test**:
```typescript
describe('MCQPracticeInterface', () => {
  it('enables submit button when answer selected', () => {
    render(<MCQPracticeInterface />);

    const submitBtn = screen.getByRole('button', { name: /submit/i });
    expect(submitBtn).toBeDisabled();

    fireEvent.click(screen.getByLabelText('Option A'));
    expect(submitBtn).toBeEnabled();
  });

  it('shows correct feedback after submission', async () => {
    render(<MCQPracticeInterface />);

    fireEvent.click(screen.getByLabelText('Option A'));
    fireEvent.click(screen.getByRole('button', { name: /submit/i }));

    await waitFor(() => {
      expect(screen.getByText(/correct/i)).toBeInTheDocument();
    });
  });
});
```

### Integration Tests (MSW - Mock Service Worker)

**Test API Integration**:
```typescript
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/v1/mcqs/random', (req, res, ctx) => {
    return res(ctx.json(mockMCQ));
  }),
  rest.post('/api/v1/mcqs/:id/attempt', (req, res, ctx) => {
    return res(ctx.json(mockAttemptResponse));
  })
);

test('fetches MCQ and submits answer', async () => {
  render(<MCQPracticePage />);

  await waitFor(() => {
    expect(screen.getByText(mockMCQ.question_text)).toBeInTheDocument();
  });

  fireEvent.click(screen.getByLabelText('Option A'));
  fireEvent.click(screen.getByText('Submit'));

  await waitFor(() => {
    expect(screen.getByText(/feedback/i)).toBeInTheDocument();
  });
});
```

### E2E Tests (Playwright)

**Test Scenarios**:
1. Complete MCQ flow (load → answer → submit → review → next)
2. Keyboard navigation (Tab, Arrow keys, Enter)
3. Timer warnings (visual + screen reader)
4. OSCE placeholder displays correctly
5. Mobile responsive (touch targets, swipe)

**Example E2E Test**:
```typescript
// testing/playwright/tests/integration/mcq-practice.spec.ts
test('complete MCQ practice flow', async ({ page }) => {
  await page.goto('/practice/mcq');

  // Wait for question
  await page.waitForSelector('[data-testid="mcq-question"]');

  // Select answer with keyboard
  await page.keyboard.press('1');  // Select option A

  // Submit with Enter
  await page.keyboard.press('Enter');

  // Verify feedback
  await expect(page.locator('[role="alert"]')).toContainText(/(Correct|Incorrect)/);

  // Next question
  await page.keyboard.press('n');

  // Verify new question loaded
  await expect(page.locator('[data-testid="mcq-question"]')).not.toHaveText('');
});
```

### Accessibility Tests

**Tools**:
- axe-core (automated)
- Lighthouse (automated)
- Manual screen reader testing (NVDA, JAWS)

**Test Cases**:
1. ✅ Keyboard navigation works
2. ✅ Screen reader announces all content
3. ✅ Color contrast ≥4.5:1
4. ✅ Focus visible on all elements
5. ✅ ARIA labels correct
6. ✅ Touch targets ≥44x44px

**Lighthouse Targets**:
- Performance: >90
- Accessibility: >95
- Best Practices: >90
- SEO: >90

---

## Success Criteria

### Functional Requirements
- ✅ MCQ practice flow complete (load → answer → submit → review → next)
- ✅ OSCE placeholder displayed with clear messaging
- ✅ Timer functional with warnings (<30s yellow, <10s red)
- ✅ Image lightbox working for medical images
- ✅ Answer feedback immediate (correct/incorrect + explanation)
- ✅ Citation panel integrated
- ✅ Keyboard navigation functional (Tab, Arrow keys, 1-5, Enter)
- ✅ AMC 15-mark rubric displayed

### Quality Requirements
- ✅ Test coverage ≥80% (unit + integration)
- ✅ E2E test coverage for critical paths
- ✅ 100% test pass rate (zero-tolerance)
- ✅ WCAG 2.2 AA compliant (Lighthouse accessibility >95)
- ✅ 0 TypeScript errors
- ✅ Performance: <2s page load, <100ms interactions

### User Metrics
- ✅ 30+ MCQ attempts per student per week
- ✅ >85% completion rate (started → finished)
- ✅ <5% error rate (network failures, crashes)
- ✅ User satisfaction >4.5/5 (post-feature survey)

---

## Implementation Timeline

### Sprint 1 - Week 1 (8-10 hours)

**Days 1-2 (8 hours)**:
- Review existing MCQPracticeInterface.tsx
- Create OSCEPracticePlaceholder.tsx
- Create AMCRubricDisplay.tsx
- Create useOSCE.ts hook
- Write unit tests for new components

**Days 3-4 (6 hours)**:
- Enhance MCQPracticeInterface (keyboard shortcuts)
- Implement timer warning states
- Add accessibility features (ARIA labels, keyboard nav)
- Write E2E tests

**Day 5 (2 hours)**:
- Code review and polish
- Documentation (component READMEs)
- Mark TASK_006 complete

---

## Risks & Mitigations

### Risk 1: AI OSCE Backend Delay
**Probability**: High
**Impact**: Medium
**Mitigation**: Build placeholder now, integrate when backend ready. Clear user communication about status.

### Risk 2: Keyboard Shortcuts Conflict
**Probability**: Medium
**Impact**: Low
**Mitigation**: Test across browsers (Chrome, Safari, Firefox). Document shortcuts clearly.

### Risk 3: Timer Performance on Mobile
**Probability**: Low
**Impact**: Low
**Mitigation**: Use requestAnimationFrame for smooth countdown. Test on real devices.

---

## Dependencies

**Upstream**:
- Backend API: `GET /api/v1/mcqs/random` (✅ Available)
- Backend API: `POST /api/v1/mcqs/{id}/attempt` (✅ Available)

**Downstream**:
- TASK_007: Citation Display (depends on CitationPanel integration)
- TASK_009: Mobile Responsive (depends on component structure)

**External**:
- Material-UI v6 (already installed)
- TanStack Query v5 (already installed)
- Recharts (for future dashboard integration)

---

## Open Questions

1. **Audio alerts for timer**: Should we add audio alerts at 30s/10s? (Accessibility vs. distraction)
   - **Decision**: Add as optional feature (user can disable in settings)

2. **MCQ review mode**: Should users be able to review previously answered MCQs?
   - **Decision**: Phase 2 feature - not in TASK_006 scope

3. **OSCE conversation interface**: What UI pattern for AI conversation when backend ready?
   - **Decision**: Chat-like interface (defer to Phase 3 implementation)

---

## Approvals

**Required Approvals**:
- [ ] Product Manager: Functional requirements
- [ ] UX Designer: Material Design 3 compliance
- [ ] Accessibility Expert: WCAG 2.2 AA compliance
- [ ] Security Team: No PHI exposure in frontend
- [ ] QA Lead: Test coverage ≥80%

**Approval Date**: Pending implementation

---

## Appendix

### A. AMC 15-Mark Rubric Reference

| Domain | Marks | Description |
|--------|-------|-------------|
| Communication | 0-3 | Clarity, empathy, active listening, patient-centered |
| Clinical Reasoning | 0-4 | Differential diagnosis, systematic approach, evidence-based |
| Information Gathering | 0-3 | History taking, physical exam, appropriate investigations |
| Management Plan | 0-3 | Evidence-based, safety considerations, follow-up |
| Professionalism | 0-2 | Ethics, consent, cultural safety, confidentiality |
| **Total** | **15** | Pass ≥10, Fail <10, Excellent 14-15 |

### B. Keyboard Shortcuts Reference

| Key | Action |
|-----|--------|
| `1-5` | Select answer A-E |
| `↑/↓` | Navigate options |
| `Enter` | Submit answer |
| `N` | Next question (after submission) |
| `R` | Retry/new question |
| `Tab` | Navigate interactive elements |
| `Escape` | Close lightbox/modal |

### C. Related Documents

- Backend API Documentation: `http://localhost:8001/docs`
- Frontend Implementation Plan: `/frontend-features-15-feb/WORLD_CLASS_FRONTEND_PLAN.md`
- Accessibility Guidelines: `/frontend-features-15-feb/testing/accessibility-checklist.md`
- Original PRD: `/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_006_*.md`

---

**Document Status**: ✅ Ready for Implementation
**Last Updated**: 2026-02-15
**Next Review**: After Sprint 1 completion
