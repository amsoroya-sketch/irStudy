# PRD-MVP-002: Dashboard Frontend UI (Unified Progress View)

**PRD ID**: PRD-MVP-002
**Status**: Ready for Implementation
**Created**: 2026-05-25
**Standards**: T-RALPH V2.1
**Estimated Effort**: 8-10 hours
**Agent**: react-frontend-developer

---

## T - TESTS (Test Specification - Write These FIRST)

### Test Inventory
- **Total Tests**: 18
- **Unit Tests**: 12 (Component + API integration)
- **Integration Tests**: 4 (Data fetching + rendering)
- **E2E Tests**: 2 (Full user flow with Playwright)

### TDD Workflow (MANDATORY)

1. **RED Phase**: Write all tests FIRST → Confirm they FAIL
2. **GREEN Phase**: Implement components → Confirm tests PASS
3. **REFACTOR Phase**: Improve code → Maintain 100% pass rate

**Agent Constraint**: DO NOT implement ANY component before tests are written and confirmed failing.

---

### Phase 1 Tests: Dashboard API Hook (4 Tests)

#### Test 1: Fetch Dashboard Data Successfully

**Purpose**: Verify API hook fetches dashboard data from backend
**RED Phase Expected**: Hook not found error
**GREEN Phase Expected**: Test passes when hook implemented

```typescript
// FILE: frontend/src/api/__tests__/dashboard.test.ts

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useDashboardOverview } from '../dashboard';
import axios from 'axios';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Dashboard API Hook', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('Test 1: should fetch dashboard data successfully', async () => {
    // Arrange
    const mockDashboardData = {
      overall_progress: {
        total_sessions: 127,
        completion_percentage: 68.5,
        avg_score: 76.2,
        total_time_minutes: 2340,
        last_activity: '2026-05-25T14:30:00Z'
      },
      modules: {
        mcq: { total_attempts: 45, average_score: 78.5, last_activity: '2026-05-25T14:30:00Z', completion_rate: 71.1 },
        osce: { total_attempts: 32, average_score: 74.8, last_activity: '2026-05-24T16:20:00Z', completion_rate: 65.6 },
        emr: { total_sessions: 28, average_score: 72.3, last_activity: '2026-05-25T10:15:00Z', completion_rate: 60.7 },
        mock_exam: { total_exams: 22, average_score: 80.1, last_activity: '2026-05-23T09:45:00Z', completion_rate: 81.8 }
      },
      specialty_breakdown: [
        { specialty: 'cardiology', attempts: 15, avg_score: 82.3 },
        { specialty: 'respiratory', attempts: 12, avg_score: 75.1 }
      ],
      recent_activity: [
        { module: 'mcq', activity: 'Completed MCQ on Chest Pain', score: 85, timestamp: '2026-05-25T14:30:00Z' }
      ],
      recommendations: [
        'Focus on psychiatry - 15% below average'
      ]
    };

    mockedAxios.get.mockResolvedValueOnce({ data: mockDashboardData });

    // Act
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert
    await waitFor(() => {
      expect(result.current.isSuccess).toBe(true);
    });

    expect(result.current.data).toEqual(mockDashboardData);
    expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/dashboard/overview', {
      headers: { Authorization: 'Bearer mock-token' }
    });
  });

  it('Test 2: should handle API error gracefully', async () => {
    // Arrange
    mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

    // Act
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert
    await waitFor(() => {
      expect(result.current.isError).toBe(true);
    });

    expect(result.current.error).toBeDefined();
    expect(result.current.data).toBeUndefined();
  });

  it('Test 3: should show loading state while fetching', () => {
    // Arrange
    mockedAxios.get.mockImplementationOnce(() => new Promise(() => {})); // Pending promise

    // Act
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    // Assert
    expect(result.current.isLoading).toBe(true);
    expect(result.current.data).toBeUndefined();
  });

  it('Test 4: should refetch data when invalidated', async () => {
    // Arrange
    const mockData1 = { overall_progress: { total_sessions: 100 }, modules: {}, specialty_breakdown: [], recent_activity: [], recommendations: [] };
    const mockData2 = { overall_progress: { total_sessions: 105 }, modules: {}, specialty_breakdown: [], recent_activity: [], recommendations: [] };

    mockedAxios.get
      .mockResolvedValueOnce({ data: mockData1 })
      .mockResolvedValueOnce({ data: mockData2 });

    // Act
    const { result } = renderHook(() => useDashboardOverview(), { wrapper });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));
    expect(result.current.data?.overall_progress.total_sessions).toBe(100);

    // Refetch
    result.current.refetch();

    await waitFor(() => expect(result.current.data?.overall_progress.total_sessions).toBe(105));

    // Assert
    expect(mockedAxios.get).toHaveBeenCalledTimes(2);
  });
});
```

---

### Phase 2 Tests: OverallProgressCard Component (4 Tests)

#### Test 5: Display Overall Progress Metrics

**Purpose**: Verify OverallProgressCard displays total sessions, completion %, avg score
**RED Phase Expected**: Component not found error
**GREEN Phase Expected**: Test passes when component implemented

```typescript
// FILE: frontend/src/components/dashboard/__tests__/OverallProgressCard.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { OverallProgressCard } from '../OverallProgressCard';

describe('OverallProgressCard', () => {
  it('Test 5: should display overall progress metrics', () => {
    // Arrange
    const mockProgress = {
      total_sessions: 127,
      completion_percentage: 68.5,
      avg_score: 76.2,
      total_time_minutes: 2340,
      last_activity: '2026-05-25T14:30:00Z'
    };

    // Act
    render(<OverallProgressCard progress={mockProgress} />);

    // Assert
    expect(screen.getByText('127')).toBeInTheDocument(); // Total sessions
    expect(screen.getByText(/68\.5%/)).toBeInTheDocument(); // Completion percentage
    expect(screen.getByText(/76\.2/)).toBeInTheDocument(); // Average score
    expect(screen.getByText(/2,340/)).toBeInTheDocument(); // Total time (formatted)
  });

  it('Test 6: should display loading skeleton when data is undefined', () => {
    // Act
    render(<OverallProgressCard progress={undefined} isLoading={true} />);

    // Assert
    expect(screen.getByTestId('overall-progress-skeleton')).toBeInTheDocument();
    expect(screen.queryByText(/Total Sessions/)).not.toBeInTheDocument();
  });

  it('Test 7: should display zero state when no sessions exist', () => {
    // Arrange
    const mockProgress = {
      total_sessions: 0,
      completion_percentage: 0,
      avg_score: 0,
      total_time_minutes: 0,
      last_activity: null
    };

    // Act
    render(<OverallProgressCard progress={mockProgress} />);

    // Assert
    expect(screen.getByText('0')).toBeInTheDocument(); // Total sessions
    expect(screen.getByText(/0%/)).toBeInTheDocument(); // Completion percentage
    expect(screen.getByText(/No activity yet/)).toBeInTheDocument();
  });

  it('Test 8: should format last activity as relative time', () => {
    // Arrange
    const now = new Date();
    const twoHoursAgo = new Date(now.getTime() - 2 * 60 * 60 * 1000);

    const mockProgress = {
      total_sessions: 10,
      completion_percentage: 50,
      avg_score: 75,
      total_time_minutes: 120,
      last_activity: twoHoursAgo.toISOString()
    };

    // Act
    render(<OverallProgressCard progress={mockProgress} />);

    // Assert
    expect(screen.getByText(/2 hours ago/)).toBeInTheDocument();
  });
});
```

---

### Phase 3 Tests: ModuleStatsGrid Component (4 Tests)

#### Test 9: Display Module Statistics Grid

```typescript
// FILE: frontend/src/components/dashboard/__tests__/ModuleStatsGrid.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ModuleStatsGrid } from '../ModuleStatsGrid';

describe('ModuleStatsGrid', () => {
  it('Test 9: should display all 4 module cards', () => {
    // Arrange
    const mockModules = {
      mcq: { total_attempts: 45, average_score: 78.5, last_activity: '2026-05-25T14:30:00Z', completion_rate: 71.1 },
      osce: { total_attempts: 32, average_score: 74.8, last_activity: '2026-05-24T16:20:00Z', completion_rate: 65.6 },
      emr: { total_sessions: 28, average_score: 72.3, last_activity: '2026-05-25T10:15:00Z', completion_rate: 60.7 },
      mock_exam: { total_exams: 22, average_score: 80.1, last_activity: '2026-05-23T09:45:00Z', completion_rate: 81.8 }
    };

    // Act
    render(<ModuleStatsGrid modules={mockModules} />);

    // Assert
    expect(screen.getByText('MCQ Practice')).toBeInTheDocument();
    expect(screen.getByText('OSCE Simulation')).toBeInTheDocument();
    expect(screen.getByText('EMR Practice')).toBeInTheDocument();
    expect(screen.getByText('Mock Exam')).toBeInTheDocument();

    // Verify stats displayed
    expect(screen.getByText('45')).toBeInTheDocument(); // MCQ attempts
    expect(screen.getByText('78.5')).toBeInTheDocument(); // MCQ avg score
  });

  it('Test 10: should highlight best performing module', () => {
    // Arrange
    const mockModules = {
      mcq: { total_attempts: 45, average_score: 78.5, completion_rate: 71.1 },
      osce: { total_attempts: 32, average_score: 74.8, completion_rate: 65.6 },
      emr: { total_sessions: 28, average_score: 72.3, completion_rate: 60.7 },
      mock_exam: { total_exams: 22, average_score: 85.1, completion_rate: 81.8 } // Highest score
    };

    // Act
    render(<ModuleStatsGrid modules={mockModules} />);

    // Assert
    const mockExamCard = screen.getByTestId('module-card-mock_exam');
    expect(mockExamCard).toHaveClass('border-green-500'); // Highlighted
  });

  it('Test 11: should show warning icon for low completion rate', () => {
    // Arrange
    const mockModules = {
      mcq: { total_attempts: 5, average_score: 60.0, completion_rate: 40.0 }, // Low completion
      osce: { total_attempts: 0, average_score: 0, completion_rate: 0 },
      emr: { total_sessions: 0, average_score: 0, completion_rate: 0 },
      mock_exam: { total_exams: 0, average_score: 0, completion_rate: 0 }
    };

    // Act
    render(<ModuleStatsGrid modules={mockModules} />);

    // Assert
    expect(screen.getByTestId('warning-icon-mcq')).toBeInTheDocument();
  });

  it('Test 12: should display empty state when no module activity', () => {
    // Arrange
    const mockModules = {
      mcq: { total_attempts: 0, average_score: 0, completion_rate: 0 },
      osce: { total_attempts: 0, average_score: 0, completion_rate: 0 },
      emr: { total_sessions: 0, average_score: 0, completion_rate: 0 },
      mock_exam: { total_exams: 0, average_score: 0, completion_rate: 0 }
    };

    // Act
    render(<ModuleStatsGrid modules={mockModules} />);

    // Assert
    expect(screen.getByText(/No activity yet/)).toBeInTheDocument();
    expect(screen.getByText(/Start practicing/)).toBeInTheDocument();
  });
});
```

---

### Phase 4 Tests: SpecialtyBreakdownChart Component (2 Tests)

#### Test 13: Display Specialty Breakdown Chart

```typescript
// FILE: frontend/src/components/dashboard/__tests__/SpecialtyBreakdownChart.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SpecialtyBreakdownChart } from '../SpecialtyBreakdownChart';

describe('SpecialtyBreakdownChart', () => {
  it('Test 13: should render bar chart with specialty data', () => {
    // Arrange
    const mockBreakdown = [
      { specialty: 'cardiology', attempts: 15, avg_score: 82.3 },
      { specialty: 'respiratory', attempts: 12, avg_score: 75.1 },
      { specialty: 'psychiatry', attempts: 10, avg_score: 68.5 }
    ];

    // Act
    render(<SpecialtyBreakdownChart breakdown={mockBreakdown} />);

    // Assert
    expect(screen.getByText('Cardiology')).toBeInTheDocument();
    expect(screen.getByText('Respiratory')).toBeInTheDocument();
    expect(screen.getByText('Psychiatry')).toBeInTheDocument();

    // Verify chart rendered (Recharts)
    expect(screen.getByRole('img', { name: /specialty breakdown chart/i })).toBeInTheDocument();
  });

  it('Test 14: should sort specialties by attempts (descending)', () => {
    // Arrange
    const mockBreakdown = [
      { specialty: 'psychiatry', attempts: 10, avg_score: 68.5 },
      { specialty: 'cardiology', attempts: 15, avg_score: 82.3 }, // Most attempts
      { specialty: 'respiratory', attempts: 12, avg_score: 75.1 }
    ];

    // Act
    render(<SpecialtyBreakdownChart breakdown={mockBreakdown} />);

    // Assert
    const specialtyLabels = screen.getAllByTestId(/^specialty-label-/);
    expect(specialtyLabels[0]).toHaveTextContent('Cardiology'); // First (15 attempts)
    expect(specialtyLabels[1]).toHaveTextContent('Respiratory'); // Second (12 attempts)
    expect(specialtyLabels[2]).toHaveTextContent('Psychiatry'); // Third (10 attempts)
  });
});
```

---

### Phase 5 Tests: RecentActivityFeed Component (2 Tests)

#### Test 15: Display Recent Activity Timeline

```typescript
// FILE: frontend/src/components/dashboard/__tests__/RecentActivityFeed.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RecentActivityFeed } from '../RecentActivityFeed';

describe('RecentActivityFeed', () => {
  it('Test 15: should display recent activity timeline', () => {
    // Arrange
    const mockActivities = [
      { module: 'mcq', activity: 'Completed MCQ on Chest Pain', score: 85, timestamp: '2026-05-25T14:30:00Z' },
      { module: 'osce', activity: 'Started OSCE for Respiratory Exam', score: null, timestamp: '2026-05-25T10:15:00Z' },
      { module: 'emr', activity: 'Submitted EMR for Cardiology Case', score: 78, timestamp: '2026-05-24T16:20:00Z' }
    ];

    // Act
    render(<RecentActivityFeed activities={mockActivities} />);

    // Assert
    expect(screen.getByText(/Completed MCQ on Chest Pain/)).toBeInTheDocument();
    expect(screen.getByText(/Started OSCE for Respiratory Exam/)).toBeInTheDocument();
    expect(screen.getByText(/Submitted EMR for Cardiology Case/)).toBeInTheDocument();

    // Verify scores displayed
    expect(screen.getByText('85')).toBeInTheDocument();
    expect(screen.getByText('78')).toBeInTheDocument();
  });

  it('Test 16: should limit to 10 most recent activities', () => {
    // Arrange
    const mockActivities = Array.from({ length: 15 }, (_, i) => ({
      module: 'mcq',
      activity: `Activity ${i + 1}`,
      score: 80,
      timestamp: new Date(Date.now() - i * 1000 * 60 * 60).toISOString() // 1 hour intervals
    }));

    // Act
    render(<RecentActivityFeed activities={mockActivities} />);

    // Assert
    const activityItems = screen.getAllByTestId(/^activity-item-/);
    expect(activityItems).toHaveLength(10); // Only 10 displayed
  });
});
```

---

### Phase 6 Tests: RecommendationsPanel Component (2 Tests)

#### Test 17: Display Personalized Recommendations

```typescript
// FILE: frontend/src/components/dashboard/__tests__/RecommendationsPanel.test.tsx

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { RecommendationsPanel } from '../RecommendationsPanel';

describe('RecommendationsPanel', () => {
  it('Test 17: should display personalized recommendations', () => {
    // Arrange
    const mockRecommendations = [
      'Focus on psychiatry - 15 points below average',
      'Try OSCE mode - unused for 5 days',
      'Complete 3 more sessions to reach weekly goal'
    ];

    // Act
    render(<RecommendationsPanel recommendations={mockRecommendations} />);

    // Assert
    expect(screen.getByText(/Focus on psychiatry/)).toBeInTheDocument();
    expect(screen.getByText(/Try OSCE mode/)).toBeInTheDocument();
    expect(screen.getByText(/Complete 3 more sessions/)).toBeInTheDocument();
  });

  it('Test 18: should display empty state when no recommendations', () => {
    // Arrange
    const mockRecommendations: string[] = [];

    // Act
    render(<RecommendationsPanel recommendations={mockRecommendations} />);

    // Assert
    expect(screen.getByText(/Great work!/)).toBeInTheDocument();
    expect(screen.getByText(/No recommendations at this time/)).toBeInTheDocument();
  });
});
```

---

### Phase 7 Tests: E2E Dashboard Flow (2 Tests)

#### Test E2E-1: Complete Dashboard Load Flow

```typescript
// FILE: frontend/e2e/dashboard.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Dashboard E2E Flow', () => {
  test('E2E-1: should load dashboard and display all sections', async ({ page }) => {
    // Arrange: Login first
    await page.goto('/login');
    await page.fill('input[name="email"]', 'student@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.click('button[type="submit"]');

    // Act: Navigate to dashboard
    await page.waitForURL('/dashboard');

    // Assert: All sections visible
    await expect(page.locator('h2:has-text("Overall Progress")')).toBeVisible();
    await expect(page.locator('h2:has-text("Module Performance")')).toBeVisible();
    await expect(page.locator('h2:has-text("Specialty Breakdown")')).toBeVisible();
    await expect(page.locator('h2:has-text("Recent Activity")')).toBeVisible();
    await expect(page.locator('h2:has-text("Recommendations")')).toBeVisible();

    // Verify data loaded (no skeleton loaders)
    await expect(page.locator('[data-testid="overall-progress-skeleton"]')).not.toBeVisible();

    // Verify metrics displayed
    await expect(page.locator('text=/Total Sessions/')).toBeVisible();
    await expect(page.locator('text=/Completion Rate/')).toBeVisible();
  });

  test('E2E-2: should navigate to module from dashboard', async ({ page }) => {
    // Arrange: Load dashboard
    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Act: Click on MCQ module card
    await page.click('[data-testid="module-card-mcq"]');

    // Assert: Navigated to MCQ practice page
    await page.waitForURL('/mcq');
    await expect(page.locator('h1:has-text("MCQ Practice")')).toBeVisible();
  });
});
```

---

### Test Execution Commands

```bash
# Phase 1: Dashboard API hook tests (4 tests)
cd /home/dev/Development/irStudy/frontend
npm test -- dashboard.test.ts
# Expected: 4/4 passing

# Phase 2: OverallProgressCard tests (4 tests)
npm test -- OverallProgressCard.test.tsx
# Expected: 4/4 passing

# Phase 3: ModuleStatsGrid tests (4 tests)
npm test -- ModuleStatsGrid.test.tsx
# Expected: 4/4 passing

# Phase 4: SpecialtyBreakdownChart tests (2 tests)
npm test -- SpecialtyBreakdownChart.test.tsx
# Expected: 2/2 passing

# Phase 5: RecentActivityFeed tests (2 tests)
npm test -- RecentActivityFeed.test.tsx
# Expected: 2/2 passing

# Phase 6: RecommendationsPanel tests (2 tests)
npm test -- RecommendationsPanel.test.tsx
# Expected: 2/2 passing

# All unit/integration tests
npm test -- dashboard
# Expected: 18/18 passing

# E2E tests
npx playwright test dashboard.spec.ts
# Expected: 2/2 passing

# Coverage report
npm test -- dashboard --coverage
# Expected: ≥85% coverage
```

---

### Test Coverage Targets

**Per Phase**:
- Phase 1: 4 tests (API hook)
- Phase 2: 4 tests (OverallProgressCard)
- Phase 3: 4 tests (ModuleStatsGrid)
- Phase 4: 2 tests (SpecialtyBreakdownChart)
- Phase 5: 2 tests (RecentActivityFeed)
- Phase 6: 2 tests (RecommendationsPanel)
- Phase 7: 2 tests (E2E flow)

**Total**: 18 tests + 2 E2E (20 total, 100% must pass)

**Coverage Thresholds**:
- Lines: ≥85%
- Branches: ≥80%
- Functions: ≥90%
- Statements: ≥85%

---

## R - REQUEST (User Story & Business Context)

### Executive Summary

Build the unified dashboard frontend UI that displays aggregated progress across all 4 modules (MCQ, OSCE, EMR, Mock Exam). This is the **primary entry point** for MVP users and must:

1. **Fetch** data from `/api/v1/dashboard/overview` (validated by PRD-MVP-001)
2. **Display** 5 sections: Overall Progress, Module Stats, Specialty Breakdown, Recent Activity, Recommendations
3. **Navigate** to specific modules when user clicks module cards
4. **Load** in <2 seconds (including API call)
5. **Work** on mobile, tablet, desktop (responsive Material Design 3)

**Why This Matters**: The dashboard is the first thing users see after login. It must create immediate value by showing progress and guiding next actions.

### Problem Statement

**Current State**:
- Backend API validated and ready (`GET /api/v1/dashboard/overview`)
- No frontend UI exists to consume the API
- Users cannot see their aggregated progress across modules
- No central navigation point for MVP

**Gap**:
- Cannot launch MVP without dashboard UI
- Users have no way to track overall performance
- Module navigation requires manually typing URLs

**Risk**:
- Poor first impression if dashboard is slow or confusing
- Users abandon platform if they can't see progress immediately
- MVP launch delayed without this critical component

### Success Criteria

**Functional**:
- ✅ Dashboard fetches and displays all 5 sections from API
- ✅ Overall progress shows total sessions, completion %, avg score, last activity
- ✅ Module stats grid shows 4 cards (MCQ, OSCE, EMR, Mock Exam) with navigation
- ✅ Specialty breakdown chart visualizes performance by specialty
- ✅ Recent activity feed shows last 10 actions
- ✅ Recommendations panel shows personalized suggestions
- ✅ Clicking module card navigates to that module's practice page

**Performance**:
- ✅ Page loads in <2 seconds (including API call <200ms)
- ✅ Responsive design works on mobile (375px), tablet (768px), desktop (1280px)
- ✅ Loading skeletons display while fetching data
- ✅ Smooth animations (no janky scrolling)

**Quality**:
- ✅ 18/18 unit/integration tests passing
- ✅ 2/2 E2E tests passing
- ✅ Code coverage ≥85%
- ✅ 0 TypeScript errors
- ✅ 0 linting errors
- ✅ WCAG 2.2 AA accessibility (keyboard nav, screen reader support)

**UX**:
- ✅ Error states handled gracefully (API failure shows retry button)
- ✅ Empty states shown when no data (encouraging CTA to start practicing)
- ✅ Visual hierarchy clear (most important metrics stand out)
- ✅ Color coding intuitive (green = good, yellow = needs work, red = low score)

---

## A - ARCHITECTURE (Technical Approach)

### Component Hierarchy

```
Dashboard Page (Container)
├── OverallProgressCard (displays total sessions, completion %, avg score, time)
├── ModuleStatsGrid (4 cards: MCQ, OSCE, EMR, Mock Exam)
│   ├── ModuleCard (MCQ)
│   ├── ModuleCard (OSCE)
│   ├── ModuleCard (EMR)
│   └── ModuleCard (Mock Exam)
├── SpecialtyBreakdownChart (Recharts bar chart)
├── RecentActivityFeed (timeline of last 10 actions)
└── RecommendationsPanel (personalized suggestions)
```

### Data Flow

```
[User loads /dashboard]
    ↓
[DashboardPage calls useDashboardOverview()]
    ↓
[API hook: GET /api/v1/dashboard/overview with JWT]
    ↓
[Backend returns DashboardResponse (validated by PRD-MVP-001)]
    ↓
[React Query caches response]
    ↓
[DashboardPage passes data to child components as props]
    ↓
[Child components render with Material-UI components]
    ↓
[User clicks ModuleCard]
    ↓
[Navigate to /mcq, /osce, /emr, or /mock-exam]
```

### Technology Stack

**Frontend**:
- React 18 (functional components + hooks)
- TypeScript 5.3
- Material-UI v5 (Material Design 3)
- React Query (data fetching + caching)
- Recharts (specialty breakdown chart)
- React Router v6 (navigation)
- date-fns (date formatting)

**Testing**:
- Vitest (unit/integration tests)
- React Testing Library (component testing)
- Playwright (E2E tests)

**Build**:
- Vite (bundler)
- TypeScript compiler (type checking)
- ESLint (linting)

### File Structure

```
frontend/src/
├── api/
│   ├── dashboard.ts (useDashboardOverview hook)
│   └── __tests__/
│       └── dashboard.test.ts (4 tests)
├── components/dashboard/
│   ├── DashboardPage.tsx (container)
│   ├── OverallProgressCard.tsx
│   ├── ModuleStatsGrid.tsx
│   ├── ModuleCard.tsx
│   ├── SpecialtyBreakdownChart.tsx
│   ├── RecentActivityFeed.tsx
│   ├── RecommendationsPanel.tsx
│   └── __tests__/
│       ├── OverallProgressCard.test.tsx (4 tests)
│       ├── ModuleStatsGrid.test.tsx (4 tests)
│       ├── SpecialtyBreakdownChart.test.tsx (2 tests)
│       ├── RecentActivityFeed.test.tsx (2 tests)
│       └── RecommendationsPanel.test.tsx (2 tests)
├── types/
│   └── dashboard.ts (TypeScript interfaces)
└── e2e/
    └── dashboard.spec.ts (2 E2E tests)
```

### API Response Type (from PRD-MVP-001)

```typescript
// FILE: frontend/src/types/dashboard.ts

export interface OverallProgress {
  total_sessions: number;
  completion_percentage: number;
  avg_score: number;
  total_time_minutes: number;
  last_activity: string | null;
}

export interface ModuleStats {
  total_attempts?: number;
  total_sessions?: number;
  total_exams?: number;
  average_score: number;
  last_activity: string | null;
  completion_rate: number;
}

export interface SpecialtyBreakdown {
  specialty: string;
  attempts: number;
  avg_score: number;
}

export interface RecentActivity {
  module: 'mcq' | 'osce' | 'emr' | 'mock_exam';
  activity: string;
  score: number | null;
  timestamp: string;
}

export interface DashboardResponse {
  overall_progress: OverallProgress;
  modules: {
    mcq: ModuleStats;
    osce: ModuleStats;
    emr: ModuleStats;
    mock_exam: ModuleStats;
  };
  specialty_breakdown: SpecialtyBreakdown[];
  recent_activity: RecentActivity[];
  recommendations: string[];
}
```

---

## L - LOOP (Iterative Development with TDD)

### Agent Constraints (ALL PHASES)

**CRITICAL - Read These Files FIRST**:
1. **PROJECT_CONSTRAINTS.md**: `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`
   - Section 2: Technology Stack (React, Material-UI, TypeScript)
   - Section 3: Security Requirements (JWT auth, no hardcoded API URLs)
   - Section 4: Testing Requirements (TDD workflow, ≥85% coverage)
   - Section 6: Quality Gates (TypeScript, ESLint, tests)

2. **T Section**: Read all tests for your phase FIRST

3. **Existing Code**: Review similar components before creating new ones
   - Pattern: `src/components/mcq/MCQPracticeInterface.tsx` (API hooks pattern)
   - Pattern: `src/components/study-cards/FlashcardReview.tsx` (loading states)

**Validation Checklist** (Complete before returning):
- [ ] Read PROJECT_CONSTRAINTS.md sections 2, 3, 4, 6
- [ ] Followed existing patterns: MCQPracticeInterface.tsx (React Query), FlashcardReview.tsx (Material-UI)
- [ ] Ran quality gate commands from constraints section 6
- [ ] No hardcoded API URLs: `grep -r "localhost\|http://\|ws://" src/components/dashboard/` → 0 results
- [ ] TypeScript: `npx tsc --noEmit` → 0 errors
- [ ] Tests: `npm test -- dashboard` → 18/18 passing
- [ ] Linting: `npm run lint` → 0 errors

---

### Phase 1: API Hook & TypeScript Types (1.5 hours)

**TDD Workflow (MANDATORY)**:

1. **RED Phase (30 min)**:
   - Agent reads T section Tests 1-4
   - Agent creates `src/types/dashboard.ts` (TypeScript interfaces)
   - Agent creates `src/api/__tests__/dashboard.test.ts` with Tests 1-4
   - Agent runs: `npm test -- dashboard.test.ts`
   - **Confirms**: 4/4 tests FAIL (hook doesn't exist)
   - **Blocker**: If tests pass → Investigate (hook may already exist)

2. **GREEN Phase (40 min)**:
   - Agent creates `src/api/dashboard.ts` (useDashboardOverview hook)
   - Agent implements React Query hook calling `/api/v1/dashboard/overview`
   - Agent runs: `npm test -- dashboard.test.ts`
   - **Confirms**: 4/4 tests PASS
   - **Blocker**: If any test fails → Fix implementation

3. **VALIDATION Phase (20 min)**:
   - Agent runs: `npx tsc --noEmit` → 0 errors
   - Agent verifies: No hardcoded API URLs (use environment variable)
   - Agent tests: Manual API call to verify endpoint works
   - **Confirms**: Hook works with real backend (if available)

**Deliverables**:
- [ ] `src/types/dashboard.ts` (90 lines, 5 interfaces)
- [ ] `src/api/dashboard.ts` (45 lines, 1 hook)
- [ ] `src/api/__tests__/dashboard.test.ts` (150 lines, 4 tests)

**3-Layer QA Validation**:
- **Layer 0 (TDD)**: Tests written FIRST and confirmed failing
- **Layer 1 (Agent)**: `npm test -- dashboard.test.ts` → 4/4 passing
- **Layer 2 (Agent)**: `npx tsc --noEmit` → 0 errors
- **Layer 3 (Human)**: Review TypeScript types match backend schema

---

(Phases 2-7 follow similar TDD workflow structure - implementation details in P section)

---

## P - PLAN (Detailed Implementation)

### Phase 1: API Hook & Types (1.5 hours)

**File 1: TypeScript Types**

```typescript
// FILE: frontend/src/types/dashboard.ts

/**
 * Dashboard API response types
 *
 * Matches backend schema from PRD-MVP-001 (src/api/v1/dashboard.py)
 * Author: react-frontend-developer
 * Date: 2026-05-25
 */

export interface OverallProgress {
  total_sessions: number;
  completion_percentage: number;
  avg_score: number;
  total_time_minutes: number;
  last_activity: string | null;
}

export interface ModuleStats {
  total_attempts?: number;     // MCQ, OSCE
  total_sessions?: number;     // EMR
  total_exams?: number;        // Mock Exam
  average_score: number;
  last_activity: string | null;
  completion_rate: number;
}

export interface SpecialtyBreakdown {
  specialty: string;
  attempts: number;
  avg_score: number;
}

export interface RecentActivity {
  module: 'mcq' | 'osce' | 'emr' | 'mock_exam';
  activity: string;
  score: number | null;
  timestamp: string;
}

export interface DashboardResponse {
  overall_progress: OverallProgress;
  modules: {
    mcq: ModuleStats;
    osce: ModuleStats;
    emr: ModuleStats;
    mock_exam: ModuleStats;
  };
  specialty_breakdown: SpecialtyBreakdown[];
  recent_activity: RecentActivity[];
  recommendations: string[];
}

// Validation: Ensure types exported
// grep -c "export interface" src/types/dashboard.ts
// Expected: 5
```

**File 2: API Hook**

```typescript
// FILE: frontend/src/api/dashboard.ts

/**
 * Dashboard API hook using React Query
 *
 * Fetches aggregated dashboard data from backend API
 * Implements caching, error handling, loading states
 *
 * Author: react-frontend-developer
 * Date: 2026-05-25
 */

import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { DashboardResponse } from '../types/dashboard';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

/**
 * Fetch dashboard overview data
 *
 * @returns React Query result with dashboard data
 *
 * @example
 * const { data, isLoading, error } = useDashboardOverview();
 *
 * if (isLoading) return <Skeleton />;
 * if (error) return <ErrorMessage />;
 * return <Dashboard data={data} />;
 */
export function useDashboardOverview() {
  return useQuery<DashboardResponse>({
    queryKey: ['dashboard', 'overview'],
    queryFn: async () => {
      // Get JWT token from localStorage (or auth context)
      const token = localStorage.getItem('authToken');

      if (!token) {
        throw new Error('No authentication token found');
      }

      const response = await axios.get<DashboardResponse>(
        `${API_BASE_URL}/api/v1/dashboard/overview`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes (dashboard data doesn't change frequently)
    cacheTime: 10 * 60 * 1000, // 10 minutes
    refetchOnWindowFocus: false, // Don't refetch when user returns to tab
  });
}

// Validation: Ensure hook exports
// grep -c "export function useDashboardOverview" src/api/dashboard.ts
// Expected: 1
```

**File 3: API Hook Tests** (from T section - Tests 1-4)

*Full implementation of Tests 1-4 as specified in T section*

---

### Phase 2-6: Component Implementation

*(Full implementation continues with each component following the same TDD pattern as shown in Phase 1)*

---

## H - HANDOFF (Delivery & Validation)

### Test Results Summary (MANDATORY)

**Test Execution Evidence**:
```bash
cd /home/dev/Development/irStudy/frontend

# Unit/Integration Tests
npm test -- dashboard

# Expected Output:
✓ src/api/__tests__/dashboard.test.ts (4 tests)
  ✓ Test 1: should fetch dashboard data successfully
  ✓ Test 2: should handle API error gracefully
  ✓ Test 3: should show loading state while fetching
  ✓ Test 4: should refetch data when invalidated

✓ src/components/dashboard/__tests__/OverallProgressCard.test.tsx (4 tests)
  ✓ Test 5: should display overall progress metrics
  ✓ Test 6: should display loading skeleton when data is undefined
  ✓ Test 7: should display zero state when no sessions exist
  ✓ Test 8: should format last activity as relative time

✓ src/components/dashboard/__tests__/ModuleStatsGrid.test.tsx (4 tests)
  ... (Tests 9-12)

✓ src/components/dashboard/__tests__/SpecialtyBreakdownChart.test.tsx (2 tests)
  ... (Tests 13-14)

✓ src/components/dashboard/__tests__/RecentActivityFeed.test.tsx (2 tests)
  ... (Tests 15-16)

✓ src/components/dashboard/__tests__/RecommendationsPanel.test.tsx (2 tests)
  ... (Tests 17-18)

Test Files: 6 passed (6)
Tests: 18 passed (18)
Duration: 4.23s

# E2E Tests
npx playwright test dashboard.spec.ts

# Expected Output:
Running 2 tests using 1 worker

  ✓ E2E-1: should load dashboard and display all sections (3.2s)
  ✓ E2E-2: should navigate to module from dashboard (1.8s)

2 passed (5.0s)
```

**TDD Compliance Verification**:
- [x] All 18 unit/integration tests written BEFORE implementation (RED phase)
- [x] All 18 tests confirmed FAILING before implementation
- [x] All 18 tests confirmed PASSING after implementation (GREEN phase)
- [x] All 18 tests STILL PASSING after refactoring
- [x] 2/2 E2E tests passing
- [ ] 0 tests skipped or marked as "TODO"

**Code Coverage**:
```bash
npm test -- dashboard --coverage

# Expected Output:
File                                           | % Stmts | % Branch | % Funcs | % Lines
-----------------------------------------------|---------|----------|---------|--------
src/api/dashboard.ts                           |   100   |   100    |   100   |   100
src/components/dashboard/DashboardPage.tsx     |   92.3  |   87.5   |   100   |   92.3
src/components/dashboard/OverallProgressCard.tsx|   95.8  |   90.0   |   100   |   95.8
src/components/dashboard/ModuleStatsGrid.tsx   |   93.2  |   88.9   |   100   |   93.2
src/components/dashboard/SpecialtyBreakdownChart.tsx|   100   |   100    |   100   |   100
src/components/dashboard/RecentActivityFeed.tsx|   100   |   100    |   100   |   100
src/components/dashboard/RecommendationsPanel.tsx|   100   |   100    |   100   |   100
-----------------------------------------------|---------|----------|---------|--------
TOTAL                                          |   94.5  |   89.3   |   100   |   94.5

✅ Coverage thresholds MET (≥85% lines, ≥80% branches, ≥90% functions)
```

---

### Acceptance Criteria

**Functionality**:
- [x] Dashboard fetches data from backend API successfully
- [x] All 5 sections render correctly
- [x] Module navigation works (clicking card → navigates)
- [x] Loading states show skeletons
- [x] Error states show retry button
- [x] Empty states show encouraging CTAs

**TDD Process**:
- [x] Tests written FIRST for all 7 phases
- [x] RED-GREEN-REFACTOR workflow followed
- [x] Test pass rate: 20/20 (18 unit + 2 E2E) (100%)

**Code Quality**:
- [x] TypeScript: 0 errors (`npx tsc --noEmit`)
- [x] ESLint: 0 errors (`npm run lint`)
- [x] No `any` types (strict mode)
- [x] Coverage: ≥85% lines, ≥80% branches, ≥90% functions

**Performance**:
- [x] Page loads in <2 seconds
- [x] API call <200ms (validated by PRD-MVP-001)
- [x] Responsive on mobile, tablet, desktop
- [x] Smooth animations (60fps)

**Accessibility**:
- [x] WCAG 2.2 AA compliant
- [x] Keyboard navigation works
- [x] Screen reader support (ARIA labels)
- [x] Color contrast ≥4.5:1

---

### Deliverables

**Code Files**:
- [x] `src/types/dashboard.ts` (90 lines)
- [x] `src/api/dashboard.ts` (45 lines)
- [x] `src/components/dashboard/DashboardPage.tsx` (180 lines)
- [x] `src/components/dashboard/OverallProgressCard.tsx` (120 lines)
- [x] `src/components/dashboard/ModuleStatsGrid.tsx` (200 lines)
- [x] `src/components/dashboard/ModuleCard.tsx` (85 lines)
- [x] `src/components/dashboard/SpecialtyBreakdownChart.tsx` (95 lines)
- [x] `src/components/dashboard/RecentActivityFeed.tsx` (110 lines)
- [x] `src/components/dashboard/RecommendationsPanel.tsx` (75 lines)

**Test Files**:
- [x] `src/api/__tests__/dashboard.test.ts` (150 lines, 4 tests)
- [x] `src/components/dashboard/__tests__/OverallProgressCard.test.tsx` (180 lines, 4 tests)
- [x] `src/components/dashboard/__tests__/ModuleStatsGrid.test.tsx` (200 lines, 4 tests)
- [x] `src/components/dashboard/__tests__/SpecialtyBreakdownChart.test.tsx` (90 lines, 2 tests)
- [x] `src/components/dashboard/__tests__/RecentActivityFeed.test.tsx` (95 lines, 2 tests)
- [x] `src/components/dashboard/__tests__/RecommendationsPanel.test.tsx` (80 lines, 2 tests)
- [x] `e2e/dashboard.spec.ts` (65 lines, 2 tests)

**Documentation**:
- [x] Component README with usage examples
- [x] Storybook stories for each component
- [x] API documentation (JSDoc comments)

---

### Quality Gates Checklist

**TypeScript**:
```bash
npx tsc --noEmit
# Expected: No errors
```

**Tests**:
```bash
npm test -- dashboard
# Expected: 18/18 passing

npx playwright test dashboard.spec.ts
# Expected: 2/2 passing
```

**Linting**:
```bash
npm run lint
# Expected: 0 errors, 0 warnings
```

**Security**:
```bash
grep -r "localhost\|http://\|api_key" src/components/dashboard/ src/api/dashboard.ts
# Expected: 0 matches (use environment variables)
```

**Accessibility**:
```bash
npx playwright test dashboard.spec.ts --project=a11y
# Expected: 0 violations (axe-core)
```

---

### Next Steps

**Immediate**:
1. Run PRD-MVP-002 (this PRD) via Ralph
2. Validate all 20 tests passing (18 unit + 2 E2E)
3. Manual QA: Test on mobile, tablet, desktop
4. Mark PRD-MVP-002 as COMPLETE

**Following PRDs**:
1. **PRD-MVP-003**: Content Population MVP (import MCQs, OSCEs, EMR patients)
2. **PRD-MVP-004**: User Onboarding (welcome tour, help docs)
3. **PRD-MVP-005**: Production Deployment (CI/CD, monitoring)

**Integration**:
- Dashboard is now primary entry point after login
- Update router to redirect `/` → `/dashboard` after auth
- Add dashboard link to navigation menu

---

**Status**: ✅ READY FOR RALPH EXECUTION
**Estimated Completion**: 8-10 hours
**Blockers**: PRD-MVP-001 must be complete first (backend API validated)
**Risk Level**: MEDIUM (frontend complexity, multiple components)
