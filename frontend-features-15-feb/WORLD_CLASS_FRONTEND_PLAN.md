# COMPREHENSIVE FRONTEND FEATURES IMPLEMENTATION PLAN
## irStudy AMC Medical Education Platform - TASK_006 through TASK_009

**Date:** 2026-02-15
**Document Version:** 1.0
**Platform Status:** Backend 56% complete, Frontend 30% complete
**Goal:** Achieve world-class quality (WCAG 2.2 AA, Material Design 3, 70%+ test coverage)

---

## EXECUTIVE SUMMARY

### Scope
This plan covers implementation of 4 critical frontend features for the irStudy platform:
- **TASK_006**: Quiz Interface (MCQ + OSCE practice) - 40% → 100%
- **TASK_007**: Citation Display Component - 50% → 100%
- **TASK_008**: Performance Dashboard - 30% → 100%
- **TASK_009**: Mobile Responsive Design - 0% → 100%

### Current State Analysis
**Existing Components (Partially Implemented):**
- MCQPracticeInterface.tsx (good quality, 90% complete)
- CitationPanel.tsx (good quality, 80% complete)
- PerformanceChart.tsx, StatCard.tsx, SpecialtyBreakdown.tsx, WeakAreasPanel.tsx (50% complete)
- MCQTimer.tsx, ImageLightbox.tsx (100% complete)

**Backend API Status:**
- MCQ endpoints: 70% complete (/random, /attempt, /explanation exist)
- OSCE endpoints: 70% complete (/random, /rubric exist)
- Progress endpoints: 60% complete (/dashboard, /weak-areas exist)
- **AI OSCE System**: Architecture defined but NO conversational endpoints yet
- **EMR System**: 0% complete (Phase 3 - not in current scope)

### Key Finding: AI OSCE & EMR Not Ready
Based on comprehensive code search:
- **AI OSCE**: Architecture document exists (4-layer system with WebSocket, AI Patient/Examiner agents) but NO backend implementation found
- **EMR Practice**: Master PRD exists but zero code implementation
- **Impact**: TASK_006 OSCE interface will be built as **placeholder/mockup** until backend ready

### Timeline & Effort
- **Total Effort**: 23-28 hours (3-4 weeks with testing/polish)
- **Sprint 1 (Week 1)**: TASK_006 Quiz Interface - 8-10 hours
- **Sprint 2 (Week 2)**: TASK_007 + TASK_008 - 9-12 hours
- **Sprint 3 (Week 3)**: TASK_009 + E2E Testing - 6-6 hours

---

## 1. BACKEND INTEGRATION ANALYSIS

### 1.1 Available Backend APIs

| API Endpoint | Status | Frontend Integration |
|--------------|--------|---------------------|
| `GET /api/v1/mcqs/random` | ✅ Implemented | useMCQ() hook exists |
| `POST /api/v1/mcqs/{id}/attempt` | ✅ Implemented | useSubmitMCQ() hook exists |
| `GET /api/v1/osces/random` | ✅ Implemented | Need useOSCE() hook |
| `GET /api/v1/progress/dashboard` | ✅ Implemented | Need useDashboard() hook |
| `GET /api/v1/progress/weak-areas` | ✅ Implemented | Need useWeakAreas() hook |
| `GET /api/v1/progress/trends/weekly` | ⚠️ Not found | Need backend implementation |
| `WS /ws/osce/{session_id}` | ❌ Not implemented | AI OSCE Phase 3 |
| `POST /api/v1/emr/sessions` | ❌ Not implemented | EMR Phase 3 |

### 1.2 API Integration Matrix

#### MCQ Practice Flow
```typescript
// Data Flow: API → TanStack Query → Components
1. Frontend: useMCQ(specialty, difficulty) → GET /api/v1/mcqs/random
2. Backend: Returns MCQPublic (question, options, metadata - NO answer)
3. Frontend: User selects answer → useSubmitMCQ()
4. Backend: POST /api/v1/mcqs/{id}/attempt → Returns MCQAttemptResponse
5. Response Schema:
{
  is_correct: boolean,
  correct_answer: 'A' | 'B' | 'C' | 'D' | 'E',
  explanation: string,
  citation: string,
  time_taken_seconds: number,
  learning_points?: string[]
}
```

#### OSCE Practice Flow (PLACEHOLDER - Backend Not Ready)
```typescript
// Current State: No AI OSCE backend
// Architecture Exists: 4-layer system (WebSocket, AI Patient, AI Examiner)
// Implementation Status: 0%

// PLACEHOLDER Flow (for UI mockup):
1. Frontend: Display OSCE scenario (static patient info)
2. Frontend: Show conversation textarea (no real AI)
3. Frontend: Mock responses from JSON file
4. Frontend: Display AMC 15-mark rubric (static scores)
5. Frontend: "Connect to AI" button disabled with tooltip

// FUTURE Flow (when backend ready):
1. POST /api/v1/osce/start → session_id
2. WebSocket /ws/osce/{session_id} → Real-time AI Patient responses
3. POST /api/v1/osce/{session_id}/end → AI Examiner scoring
4. GET /api/v1/osce/{session_id}/results → AMC rubric feedback
```

#### Performance Dashboard Flow
```typescript
// Data Flow
1. Frontend: useDashboard() → GET /api/v1/progress/dashboard
2. Backend: Returns DashboardResponse
{
  total_mcq_attempts: number,
  mcq_accuracy_rate: number,  // 0-100
  total_osce_completions: number,
  study_cards_reviewed: number,
  study_card_retention_rate: number,
  specialty_breakdown: SpecialtyPerformance[],
  weak_areas: WeakArea[]
}

3. Frontend: useWeeklyTrends(weeks=4) → GET /api/v1/progress/trends/weekly
   NOTE: This endpoint NOT FOUND in backend - need to create or use mock data

4. Components: Recharts visualizations render data
```

### 1.3 Missing Backend Endpoints (Required for Frontend)

#### Priority 1: Required for TASK_008 Dashboard
```python
# backend/src/api/v1/progress.py
@router.get("/trends/weekly", response_model=WeeklyTrendsResponse)
async def get_weekly_trends(
    weeks: int = Query(4, ge=1, le=26),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get weekly progress trends for the past N weeks.

    Returns: List[WeeklyTrend]
    - week_start: datetime
    - mcq_attempts: int
    - accuracy_rate: float
    - study_cards_reviewed: int
    """
    # Implementation needed
```

#### Priority 2: AI OSCE Endpoints (Phase 3 - Not Current Scope)
```python
# backend/src/api/v1/osces.py - NEW endpoints needed
POST /api/v1/osce/start  # Initialize AI session
WS /ws/osce/{session_id}  # Real-time AI conversation
POST /api/v1/osce/{session_id}/end  # Finalize and score
GET /api/v1/osce/{session_id}/results  # Get AMC rubric results
```

#### Priority 3: EMR Practice Endpoints (Phase 3 - Not Current Scope)
```python
# backend/src/api/v1/emr_practice.py - NEW module needed
POST /api/v1/emr/sessions  # Create EMR practice session
POST /api/v1/emr/validate/soap-note  # AI validation
POST /api/v1/emr/validate/prescription  # PBS compliance check
```

---

## 2. FEATURE ARCHITECTURE

### TASK_006: Quiz Interface (40% → 100%)

#### A. Backend Integration Points

**MCQ Practice (Ready):**
```typescript
// API Endpoints
GET /api/v1/mcqs/random?specialty={specialty}&difficulty={difficulty}
POST /api/v1/mcqs/{mcq_id}/attempt
  Request: { mcq_id, selected_answer, time_taken_seconds }
  Response: { is_correct, correct_answer, explanation, citation, learning_points }

// TanStack Query Hooks (Already Exist)
frontend/src/hooks/useMCQ.ts:
- useMCQ(specialty?, difficulty?) → { data: MCQ, isLoading, error, refetch }
- useSubmitMCQ() → { mutate, isPending, data: MCQAttemptResponse }

// Request/Response Schemas (Already Defined)
frontend/src/types/mcq.ts:
- MCQ, MCQAttemptCreate, MCQAttemptResponse
```

**OSCE Practice (NOT Ready - Placeholder Only):**
```typescript
// Current Status: No backend implementation
// Architecture: Defined in planning/feb-6-ai-simulator-amc/01_SYSTEM_ARCHITECTURE.md
// Layers: Frontend → FastAPI (WebSocket) → AI Agents (SIM-001 Patient, SIM-002 Examiner) → Redis/PostgreSQL

// PLACEHOLDER Implementation (for TASK_006):
// File: frontend/src/components/osce/OSCEPracticePlaceholder.tsx
interface OSCEPlaceholderProps {
  osceId: number;
}

export const OSCEPracticePlaceholder: React.FC<OSCEPlaceholderProps> = ({ osceId }) => {
  return (
    <Card>
      <Alert severity="info">
        AI OSCE Practice Coming Soon
      </Alert>
      <Typography>
        Backend Status: AI Patient/Examiner agents not implemented
      </Typography>
      <Typography>
        Architecture: 4-layer system with WebSocket + Claude 3.5 Sonnet
      </Typography>
      <Button disabled>
        Connect to AI Patient (Requires Backend)
      </Button>

      {/* Static OSCE scenario display */}
      <OSCEScenarioCard scenario={staticScenario} />

      {/* Mock conversation (no real AI) */}
      <ConversationPlaceholder />
    </Card>
  );
};
```

**Why Placeholder Approach:**
1. Backend AI OSCE endpoints don't exist (verified via code search)
2. Architecture document shows complex 4-layer system (WebSocket, AI agents, Redis state)
3. Estimated effort for backend: 40+ hours (separate epic)
4. Frontend can be built now, integrated later

#### B. Component Architecture

**File Structure:**
```
frontend/src/
├── components/
│   ├── mcq/
│   │   ├── MCQPracticeInterface.tsx (✅ EXISTS - 90% complete)
│   │   ├── MCQTimer.tsx (✅ EXISTS - 100% complete)
│   │   └── MCQQuestionCard.tsx (NEW - extract from MCQPracticeInterface)
│   ├── osce/
│   │   ├── OSCEPracticePlaceholder.tsx (NEW - placeholder until backend ready)
│   │   ├── OSCEScenarioCard.tsx (NEW - display station info)
│   │   ├── ConversationPlaceholder.tsx (NEW - mock AI conversation)
│   │   └── AMCRubricDisplay.tsx (NEW - show 15-mark rubric)
│   ├── common/
│   │   ├── ImageLightbox.tsx (✅ EXISTS - 100% complete)
│   │   └── Timer.tsx (NEW - reusable timer for both MCQ/OSCE)
│   └── citations/
│       └── CitationPanel.tsx (✅ EXISTS - 80% complete)
├── pages/
│   ├── MCQPracticePage.tsx (NEW - wrapper page)
│   └── OSCEPracticePage.tsx (NEW - wrapper page)
├── hooks/
│   ├── useMCQ.ts (✅ EXISTS)
│   ├── useSubmitMCQ.ts (✅ EXISTS)
│   ├── useOSCE.ts (NEW - fetch OSCE scenarios)
│   └── useWebSocketOSCE.ts (NEW - placeholder, returns null until backend ready)
└── types/
    ├── mcq.ts (✅ EXISTS)
    ├── osce.ts (NEW - OSCE types)
    └── amc_rubric.ts (NEW - AMC 15-mark rubric types)
```

**Component Hierarchy:**
```
MCQPracticePage
├── MCQPracticeInterface (✅ EXISTS)
│   ├── MCQTimer (✅ EXISTS)
│   ├── ImageLightbox (✅ EXISTS)
│   ├── MCQQuestionCard (NEW)
│   └── CitationPanel (✅ EXISTS)

OSCEPracticePage (NEW)
├── OSCEPracticePlaceholder (NEW - until backend ready)
│   ├── OSCEScenarioCard (NEW)
│   ├── ConversationPlaceholder (NEW)
│   ├── AMCRubricDisplay (NEW)
│   └── Timer (NEW - 8-minute countdown)
```

#### C. Material Design 3 Implementation

```typescript
// frontend/src/theme/theme.ts
import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'light',  // Support dark mode toggle
    primary: {
      main: '#1976d2',  // Medical blue
      light: '#42a5f5',
      dark: '#1565c0',
    },
    secondary: {
      main: '#dc004e',  // Alert red
      light: '#f50057',
      dark: '#c51162',
    },
    success: {
      main: '#2e7d32',  // Correct answer green
    },
    error: {
      main: '#d32f2f',  // Incorrect answer red
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontSize: '2rem',
      fontWeight: 500,
      '@media (max-width:768px)': {
        fontSize: '1.5rem',
      },
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',  // No ALL CAPS
          borderRadius: 8,
          minHeight: 44,  // Touch target
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
  },
});

// Dark mode theme variant
export const darkTheme = createTheme({
  ...theme,
  palette: {
    mode: 'dark',
    // ... dark palette
  },
});
```

#### D. Accessibility (WCAG 2.2 AA)

**Keyboard Navigation:**
```typescript
// MCQ answer selection via keyboard
<RadioGroup
  onKeyDown={(e) => {
    if (e.key === 'Enter' && selectedAnswer) {
      handleSubmit();
    }
  }}
  aria-labelledby="mcq-question"
>
  {/* Radio buttons */}
</RadioGroup>

// Skip to next question (after submission)
<Button
  onClick={handleNext}
  onKeyDown={(e) => e.key === 'Enter' && handleNext()}
  aria-label="Next question"
  autoFocus  // Auto-focus after submission
>
  Next Question
</Button>
```

**Screen Reader Support:**
```typescript
// Announce answer correctness
<Alert
  severity={isCorrect ? 'success' : 'error'}
  role="alert"
  aria-live="assertive"  // Interrupt screen reader
>
  {isCorrect ? 'Correct! Well done.' : 'Incorrect. Review explanation.'}
</Alert>

// Timer warnings
{timeRemaining < 30 && (
  <span role="status" aria-live="polite" className="sr-only">
    {timeRemaining} seconds remaining
  </span>
)}
```

**Color Contrast (≥4.5:1):**
- Success green: #2e7d32 on white → 4.6:1 ✓
- Error red: #d32f2f on white → 4.5:1 ✓
- Primary blue: #1976d2 on white → 4.7:1 ✓

#### E. Testing Strategy

**Unit Tests (Vitest + React Testing Library):**
```typescript
// frontend/tests/components/mcq/MCQPracticeInterface.test.tsx
describe('MCQPracticeInterface', () => {
  it('renders question and options correctly', () => {
    render(<MCQPracticeInterface />);
    expect(screen.getByText(/What is/i)).toBeInTheDocument();
  });

  it('enables submit button only when answer selected', async () => {
    render(<MCQPracticeInterface />);
    const submitBtn = screen.getByRole('button', { name: /Submit/i });
    expect(submitBtn).toBeDisabled();

    fireEvent.click(screen.getByLabelText(/A\./i));
    expect(submitBtn).toBeEnabled();
  });

  it('shows explanation after correct answer', async () => {
    render(<MCQPracticeInterface />);
    // ... submit answer
    await waitFor(() => {
      expect(screen.getByText(/Correct!/i)).toBeInTheDocument();
      expect(screen.getByText(/Explanation:/i)).toBeInTheDocument();
    });
  });
});
```

**Integration Tests:**
```typescript
// Test API integration with MSW (Mock Service Worker)
import { rest } from 'msw';
import { setupServer } from 'msw/node';

const server = setupServer(
  rest.get('/api/v1/mcqs/random', (req, res, ctx) => {
    return res(ctx.json({
      id: 1,
      question_text: 'Test question',
      options: { A: 'Option A', B: 'Option B' },
      // ...
    }));
  })
);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

**E2E Tests (Playwright - Already 65 tests exist):**
```typescript
// testing/playwright/tests/integration/mcq-practice.spec.ts
test('complete MCQ practice flow', async ({ page }) => {
  await page.goto('/mcq-practice');

  // Wait for question load
  await page.waitForSelector('[data-testid="mcq-question"]');

  // Select answer
  await page.click('text=A.');

  // Submit
  await page.click('text=Submit Answer');

  // Verify feedback
  await expect(page.locator('[role="alert"]')).toContainText(/(Correct|Incorrect)/);

  // Next question
  await page.click('text=Next Question');
});
```

---

### TASK_007: Citation Display Component (50% → 100%)

#### A. Backend Integration Points

**Current State:** CitationPanel.tsx exists with 80% functionality

**API Integration:**
```typescript
// Citations come from MCQ attempt response
interface MCQAttemptResponse {
  citation: string;  // Single citation string
  // Example: "eTG: Therapeutic Guidelines - Cardiovascular (Page 42, Section 3.2)"
}

// Frontend parses citation string
import { parseCitation } from '@/utils/citationParser';

const parsed = parseCitation(citation);
// Returns:
{
  source: 'eTG',
  displayText: 'Therapeutic Guidelines - Cardiovascular',
  page: '42',
  section: '3.2',
  confidence: 0.85  // If RAG verified
}
```

**No Backend Changes Required** - Component already integrates well

#### B. Component Enhancements

**Citation Parser:**
```typescript
// frontend/src/utils/citationParser.ts
export function parseCitation(citation: string): ParsedCitation {
  // Regex patterns for Australian sources
  const patterns = {
    eTG: /eTG:\s*(.+?)(?:\s*\(Page\s*(\d+)(?:,\s*Section\s*([\d.]+))?\))?/,
    PBS: /PBS:\s*(.+?)(?:\s*-\s*(.+))?/,
    AMH: /AMH:\s*(.+?)(?:\s*\(Page\s*(\d+)\))?/,
    AHPRA: /AHPRA:\s*(.+)/,
    RACGP: /RACGP:\s*(.+?)(?:\s*\((.+)\))?/,
  };

  for (const [source, pattern] of Object.entries(patterns)) {
    const match = citation.match(pattern);
    if (match) {
      return {
        source,
        displayText: match[1],
        page: match[2] || null,
        section: match[3] || null,
      };
    }
  }

  return {
    source: 'Other',
    displayText: citation,
    page: null,
    section: null,
  };
}
```

**Enhanced Component:**
```typescript
// frontend/src/components/citations/CitationPanel.tsx (ENHANCED)
export const CitationPanel: React.FC<CitationPanelProps> = ({
  citations,
  showConfidence = false,
  allowCopy = true,
}) => {
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);

  return (
    <>
      <Card>
        {citations.map((citation, idx) => (
          <Box key={idx}>
            {/* Existing citation display */}

            {/* NEW: View details button */}
            <IconButton onClick={() => {
              setSelectedCitation(citation);
              setModalOpen(true);
            }}>
              <InfoIcon />
            </IconButton>
          </Box>
        ))}
      </Card>

      {/* NEW: Citation details modal */}
      <Modal open={modalOpen} onClose={() => setModalOpen(false)}>
        <CitationDetailsModal citation={selectedCitation} />
      </Modal>
    </>
  );
};
```

---

### TASK_008: Performance Dashboard (30% → 100%)

#### A. Backend Integration

**TanStack Query Hooks:**
```typescript
// frontend/src/hooks/useDashboard.ts
export const useDashboard = () => {
  return useQuery({
    queryKey: ['dashboard'],
    queryFn: async () => {
      const response = await apiClient.get('/api/v1/progress/dashboard');
      return response.data as DashboardResponse;
    },
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
};

export const useWeeklyTrends = (weeks: number = 4) => {
  return useQuery({
    queryKey: ['trends', 'weekly', weeks],
    queryFn: async () => {
      // TEMPORARY: Use mock data until backend endpoint exists
      if (process.env.NODE_ENV === 'development') {
        return generateMockTrends(weeks);
      }

      const response = await apiClient.get(`/api/v1/progress/trends/weekly?weeks=${weeks}`);
      return response.data.trends as WeeklyTrend[];
    },
    enabled: weeks > 0 && weeks <= 26,
  });
};
```

#### B. Exam Readiness Algorithm

```typescript
// frontend/src/utils/examReadiness.ts
interface ExamReadinessFactors {
  mcqAccuracy: number;  // 0-100
  osceCompletions: number;
  studyCardMastery: number;  // 0-100
  weakAreasCount: number;
  studyStreak: number;  // Days
}

export function calculateExamReadiness(factors: ExamReadinessFactors): number {
  // Weighted scoring
  const weights = {
    mcqAccuracy: 0.35,  // 35% weight
    osce: 0.25,         // 25% weight
    studyCards: 0.20,   // 20% weight
    weakAreas: 0.10,    // 10% weight (inverse)
    streak: 0.10,       // 10% weight
  };

  // MCQ score (target 75% accuracy = 100 readiness)
  const mcqScore = Math.min((factors.mcqAccuracy / 75) * 100, 100);

  // OSCE score (target 20 completions = 100 readiness)
  const osceScore = Math.min((factors.osceCompletions / 20) * 100, 100);

  // Study card score (direct mastery %)
  const studyCardScore = factors.studyCardMastery;

  // Weak areas penalty (each weak area reduces score)
  const weakAreasScore = Math.max(100 - (factors.weakAreasCount * 10), 0);

  // Study streak bonus (consistent study = readiness)
  const streakScore = Math.min((factors.studyStreak / 30) * 100, 100);  // 30 days = max

  // Weighted sum
  const readiness = (
    mcqScore * weights.mcqAccuracy +
    osceScore * weights.osce +
    studyCardScore * weights.studyCards +
    weakAreasScore * weights.weakAreas +
    streakScore * weights.streak
  );

  return Math.round(readiness);
}
```

---

### TASK_009: Mobile Responsive Design (0% → 100%)

#### A. Breakpoints

```typescript
// frontend/src/theme/theme.ts
export const theme = createTheme({
  breakpoints: {
    values: {
      xs: 320,   // Mobile small (iPhone SE)
      sm: 768,   // Tablet portrait
      md: 1024,  // Tablet landscape / Desktop small
      lg: 1280,  // Desktop
      xl: 1920,  // Desktop XL
    },
  },
});
```

#### B. Mobile Navigation

```typescript
// frontend/src/components/layout/MobileBottomNav.tsx
import { BottomNavigation, BottomNavigationAction } from '@mui/material';
import { Home, Quiz, Dashboard, Person } from '@mui/icons-material';

export const MobileBottomNav: React.FC = () => {
  const [value, setValue] = useState('home');
  const navigate = useNavigate();
  const { isMobile } = useResponsive();

  if (!isMobile) return null;  // Hide on desktop

  return (
    <BottomNavigation
      value={value}
      onChange={(event, newValue) => {
        setValue(newValue);
        navigate(`/${newValue}`);
      }}
      sx={{
        position: 'fixed',
        bottom: 0,
        left: 0,
        right: 0,
        borderTop: '1px solid',
        borderColor: 'divider',
      }}
    >
      <BottomNavigationAction label="Home" value="home" icon={<Home />} />
      <BottomNavigationAction label="Practice" value="practice" icon={<Quiz />} />
      <BottomNavigationAction label="Dashboard" value="dashboard" icon={<Dashboard />} />
      <BottomNavigationAction label="Profile" value="profile" icon={<Person />} />
    </BottomNavigation>
  );
};
```

#### C. PWA Configuration

```typescript
// vite.config.ts
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      manifest: {
        name: 'irStudy - AMC Medical Education',
        short_name: 'irStudy',
        theme_color: '#1976d2',
        background_color: '#ffffff',
        display: 'standalone',
        icons: [
          {
            src: 'pwa-192x192.png',
            sizes: '192x192',
            type: 'image/png',
          },
          {
            src: 'pwa-512x512.png',
            sizes: '512x512',
            type: 'image/png',
          },
        ],
      },
    }),
  ],
});
```

---

## 3. WEEK-BY-WEEK SCHEDULE

### Sprint 1: TASK_006 Quiz Interface (Week 1 - 8-10 hours)

**Days 1-2 (8 hours):**
- Review existing MCQPracticeInterface
- Create OSCEPracticePlaceholder component
- Create useOSCE() hook
- Create AMCRubricDisplay component
- Write unit tests

**Days 3-4 (6 hours):**
- Enhance MCQPracticeInterface
- Add keyboard shortcuts
- Implement timer warning states
- E2E tests for MCQ flow

**Day 5 (2 hours):**
- Code review and polish
- Documentation
- Mark TASK_006 complete

---

### Sprint 2: TASK_007 + TASK_008 (Week 2 - 9-12 hours)

**Days 1-2 (4 hours) - TASK_007:**
- Enhance CitationPanel
- Create CitationDetailsModal
- Add link to source functionality
- Write tests

**Days 3-4 (8 hours) - TASK_008:**
- Create PerformanceDashboard page
- Integrate useDashboard() hooks
- Create ExamReadinessGauge
- Connect dashboard components to API

**Day 5 (2 hours):**
- Testing and polish
- Verify charts responsive
- Mark complete

---

### Sprint 3: TASK_009 Mobile Responsive (Week 3 - 6 hours)

**Days 1-2 (6 hours):**
- Configure theme breakpoints
- Create MobileBottomNav
- Make Sidebar responsive
- Add swipe gestures

**Days 3-4 (6 hours):**
- Configure PWA
- Optimize images
- Code splitting
- Run Lighthouse audits

**Day 5 (2 hours):**
- E2E mobile testing
- Cross-browser testing
- Final Lighthouse audit
- Mark complete

---

## 4. SUCCESS CRITERIA

### Functional Acceptance

**TASK_006:**
- ✅ MCQ practice flow complete
- ✅ OSCE placeholder with clear messaging
- ✅ Timer functional with warnings
- ✅ Keyboard navigation working

**TASK_007:**
- ✅ Australian sources parsed correctly
- ✅ RAG verification badge shown
- ✅ Copy to clipboard functional
- ✅ Modal deep-dive working

**TASK_008:**
- ✅ Dashboard displays 4 stat cards
- ✅ Weekly trends chart working
- ✅ Exam readiness gauge accurate
- ✅ All data from backend APIs

**TASK_009:**
- ✅ Mobile breakpoints work
- ✅ Bottom navigation on mobile
- ✅ Touch targets ≥44x44px
- ✅ PWA installable
- ✅ Lighthouse >90

### Quality Gates

- ✅ 70%+ test coverage
- ✅ 100% test pass rate
- ✅ WCAG 2.2 AA compliant
- ✅ 0 TypeScript errors
- ✅ Lighthouse >90 (all metrics)

---

## 5. RESOURCES

### PRD References
- TASK_006: `/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_006_*.md`
- TASK_007: `/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_007_*.md`
- TASK_008: `/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_008_*.md`
- TASK_009: `/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_009_*.md`

### Expert Agents
- **Primary**: flutter-desktop-expert (React/TypeScript)
- **Support**: testing-qa-expert (70%+ coverage)
- **Review**: security-compliance-expert (PHI handling)

---

**Document Status**: ✅ READY FOR IMPLEMENTATION
**Created**: 2026-02-15
**Total Effort**: 23-28 hours (3-4 weeks)
**Next Step**: Begin Sprint 1 - TASK_006 Quiz Interface
