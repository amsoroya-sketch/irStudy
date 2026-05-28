/**
 * UnifiedDashboardPage Integration Tests
 * PRD-MVP-002 Phase 7: Tests 17-18 (Integration Tests)
 *
 * Note: The PRD lists these as Tests 17-18, but they are integration tests
 * for the complete dashboard page, not component-level tests.
 *
 * Coverage:
 * - Test 17 (Integration): Load dashboard with all components
 * - Test 18 (Integration): Refetch data when user clicks refresh button
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import UnifiedDashboardPage from '../UnifiedDashboardPage';
import * as dashboardApi from '../../api/dashboard';
import type { DashboardOverviewResponse } from '../../types/dashboard';

// Mock dashboard API hook
vi.mock('../../api/dashboard');

// Mock Recharts
vi.mock('recharts', async () => {
  const actual = await vi.importActual('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children?: React.ReactNode }) => <div data-testid="responsive-container">{children}</div>,
    BarChart: ({ children }: { children?: React.ReactNode }) => <div data-testid="bar-chart">{children}</div>,
    Bar: () => <div data-testid="bar" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Cell: () => <div data-testid="cell" />,
  };
});

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Complete mock data
const mockDashboardData: DashboardOverviewResponse = {
  overall_progress: {
    total_sessions: 156,
    completion_percentage: 68.5,
    avg_score: 78.3,
    total_time_minutes: 4320,
    last_activity: '2026-05-24T14:30:00Z',
  },
  modules: {
    mcq: {
      total_attempts: 89,
      average_score: 75.2,
      last_activity: '2026-05-24T10:15:00Z',
      completion_rate: 65.0,
    },
    osce: {
      total_attempts: 34,
      average_score: 82.1,
      last_activity: '2026-05-23T16:45:00Z',
      completion_rate: 70.0,
    },
    emr: {
      total_sessions: 21,
      average_score: 79.5,
      last_activity: '2026-05-24T14:30:00Z',
      completion_rate: 75.0,
    },
    mock_exam: {
      total_exams: 12,
      average_score: 76.8,
      last_activity: '2026-05-22T11:00:00Z',
      completion_rate: 60.0,
    },
  },
  specialty_breakdown: [
    {
      specialty: 'Cardiology',
      attempts: 45,
      avg_score: 82.5,
      strength: 'good',
    },
  ],
  recent_activity: [
    {
      type: 'mcq',
      description: 'Completed MCQ quiz on Cardiology',
      score: 85,
      timestamp: '2026-05-24T14:30:00Z',
    },
  ],
  recommendations: [
    {
      module: 'MCQ',
      specialty: 'Psychiatry',
      reason: 'Low accuracy - needs improvement',
      priority: 'high',
    },
  ],
};

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </BrowserRouter>
  );
};

describe('UnifiedDashboardPage - PRD-MVP-002 Phase 7 Integration Tests', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  /**
   * Test 17 (Integration): Load dashboard with all components
   *
   * Requirements:
   * - Page title "Dashboard" visible
   * - OverallProgressCard loaded (shows total sessions)
   * - ModuleStatsGrid loaded (shows all 4 modules)
   * - SpecialtyBreakdownChart loaded (shows chart)
   * - RecentActivityFeed loaded (shows activity)
   * - RecommendationsPanel loaded (shows recommendations)
   *
   * Success Criteria:
   * - All 5 major sections visible
   * - Data from API displayed correctly
   */
  it('Test 17 (Integration): should load dashboard with all components', async () => {
    const mockRefetch = vi.fn();
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      isFetching: false,
      refetch: mockRefetch,
    } as any);

    renderWithProviders(<UnifiedDashboardPage />);

    // Verify page title
    expect(screen.getByText('Dashboard')).toBeInTheDocument();

    // Verify OverallProgressCard (shows total sessions)
    expect(screen.getByText('156')).toBeInTheDocument(); // Total sessions
    expect(screen.getByText(/total sessions/i)).toBeInTheDocument();

    // Verify ModuleStatsGrid (all 4 modules)
    expect(screen.getByText(/MCQ Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/^OSCE$/i)).toBeInTheDocument();
    expect(screen.getByText(/EMR Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/Mock Exam/i)).toBeInTheDocument();

    // Verify SpecialtyBreakdownChart
    expect(screen.getByText(/specialty breakdown/i)).toBeInTheDocument();

    // Verify RecentActivityFeed
    expect(screen.getByText(/recent activity/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed MCQ quiz on Cardiology/i)).toBeInTheDocument();

    // Verify RecommendationsPanel
    expect(screen.getByText(/recommendations/i)).toBeInTheDocument();
    expect(screen.getByText(/Low accuracy - needs improvement/i)).toBeInTheDocument();
  });

  /**
   * Test 18 (Integration): Refetch data when user clicks refresh button
   *
   * Requirements:
   * - Refresh button visible in header
   * - Clicking refresh button calls refetch()
   * - Button disabled while fetching
   *
   * Success Criteria:
   * - refetch() called on button click
   * - Button shows disabled state when isFetching=true
   */
  it('Test 18 (Integration): should refetch data when user clicks refresh button', async () => {
    const user = userEvent.setup();
    const mockRefetch = vi.fn();

    // Initial render (not fetching)
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      isFetching: false,
      refetch: mockRefetch,
    } as any);

    const { rerender } = renderWithProviders(<UnifiedDashboardPage />);

    // Find refresh button
    const refreshButton = screen.getByLabelText(/refresh dashboard/i);
    expect(refreshButton).toBeInTheDocument();
    expect(refreshButton).not.toBeDisabled();

    // Click refresh button
    await user.click(refreshButton);

    // Verify refetch was called
    expect(mockRefetch).toHaveBeenCalledTimes(1);

    // Simulate fetching state
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      isFetching: true, // Now fetching
      refetch: mockRefetch,
    } as any);

    const queryClient = createTestQueryClient();
    rerender(
      <BrowserRouter>
        <QueryClientProvider client={queryClient}>
          <UnifiedDashboardPage />
        </QueryClientProvider>
      </BrowserRouter>
    );

    // Verify button is disabled during fetch
    const refreshButtonDisabled = screen.getByLabelText(/refresh dashboard/i);
    expect(refreshButtonDisabled).toBeDisabled();
  });
});
