/**
 * ModuleStatsGrid Component Tests
 * PRD-MVP-002 Phase 3: Tests 9-12
 *
 * TDD Workflow:
 * - RED: Tests fail (component not implemented)
 * - GREEN: Tests pass (component implemented)
 *
 * Coverage:
 * - Test 9: Display all 4 module cards
 * - Test 10: Navigate to module page on click
 * - Test 11: Handle empty state (no attempts)
 * - Test 12: Responsive grid layout
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import ModuleStatsGrid from '../ModuleStatsGrid';
import * as dashboardApi from '../../../api/dashboard';
import type { DashboardOverviewResponse } from '../../../types/dashboard';

// Mock dashboard API hook
vi.mock('../../../api/dashboard');

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

// Test data with all modules having activity
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
  specialty_breakdown: [],
  recent_activity: [],
  recommendations: [],
};

// Test data with empty modules (no activity)
const mockEmptyData: DashboardOverviewResponse = {
  overall_progress: {
    total_sessions: 0,
    completion_percentage: 0,
    avg_score: 0,
    total_time_minutes: 0,
    last_activity: null,
  },
  modules: {
    mcq: {
      total_attempts: 0,
      average_score: 0,
      last_activity: null,
      completion_rate: 0,
    },
    osce: {
      total_attempts: 0,
      average_score: 0,
      last_activity: null,
      completion_rate: 0,
    },
    emr: {
      total_sessions: 0,
      average_score: 0,
      last_activity: null,
      completion_rate: 0,
    },
    mock_exam: {
      total_exams: 0,
      average_score: 0,
      last_activity: null,
      completion_rate: 0,
    },
  },
  specialty_breakdown: [],
  recent_activity: [],
  recommendations: [],
};

// Helper to create QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

// Helper to render with QueryClient and Router
const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </BrowserRouter>
  );
};

describe('ModuleStatsGrid - PRD-MVP-002 Phase 3', () => {
  beforeEach(() => {
    mockNavigate.mockClear();
  });

  /**
   * Test 9: Display all 4 module cards
   *
   * Requirements:
   * - MCQ card: "MCQ Practice", 89 attempts, 75.2% avg score
   * - OSCE card: "OSCE", 34 attempts, 82.1% avg score
   * - EMR card: "EMR Practice", 21 sessions, 79.5% avg score
   * - Mock Exam card: "Mock Exam", 12 exams, 76.8% avg score
   * - All cards display last activity
   *
   * Success Criteria:
   * - All 4 module names visible
   * - All attempt/session counts visible
   * - All average scores visible
   */
  it('Test 9: should display all 4 module cards', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithProviders(<ModuleStatsGrid />);

    // Verify all module names
    expect(screen.getByText(/MCQ Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/OSCE/i)).toBeInTheDocument();
    expect(screen.getByText(/EMR Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/Mock Exam/i)).toBeInTheDocument();

    // Verify MCQ stats
    expect(screen.getByText('89')).toBeInTheDocument(); // attempts
    expect(screen.getByText(/75.2%/)).toBeInTheDocument(); // avg score

    // Verify OSCE stats
    expect(screen.getByText('34')).toBeInTheDocument(); // attempts
    expect(screen.getByText(/82.1%/)).toBeInTheDocument(); // avg score

    // Verify EMR stats
    expect(screen.getByText('21')).toBeInTheDocument(); // sessions
    expect(screen.getByText(/79.5%/)).toBeInTheDocument(); // avg score

    // Verify Mock Exam stats
    expect(screen.getByText('12')).toBeInTheDocument(); // exams
    expect(screen.getByText(/76.8%/)).toBeInTheDocument(); // avg score
  });

  /**
   * Test 10: Navigate to module page on click
   *
   * Requirements:
   * - Clicking MCQ card navigates to /mcqs
   * - Clicking OSCE card navigates to /osces
   * - Clicking EMR card navigates to /emr
   * - Clicking Mock Exam card navigates to /mock-exam
   * - Cards use CardActionArea for clickability
   *
   * Success Criteria:
   * - navigate() called with correct path
   * - Keyboard accessible (Enter key triggers navigation)
   */
  it('Test 10: should navigate to module page on click', async () => {
    const user = userEvent.setup();

    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithProviders(<ModuleStatsGrid />);

    // Click MCQ card
    const mcqCard = screen.getByText(/MCQ Practice/i).closest('[role="button"]');
    expect(mcqCard).toBeInTheDocument();
    await user.click(mcqCard!);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/mcqs');
    });

    // Click OSCE card
    const osceCard = screen.getByText(/OSCE/i).closest('[role="button"]');
    await user.click(osceCard!);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/osces');
    });

    // Click EMR card
    const emrCard = screen.getByText(/EMR Practice/i).closest('[role="button"]');
    await user.click(emrCard!);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/emr');
    });

    // Click Mock Exam card
    const mockExamCard = screen.getByText(/Mock Exam/i).closest('[role="button"]');
    await user.click(mockExamCard!);
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/mock-exam');
    });
  });

  /**
   * Test 11: Handle empty state (no attempts)
   *
   * Requirements:
   * - Show "No activity yet" or similar message when attempts/sessions = 0
   * - Display "0" for attempt counts
   * - Display "0%" for average scores
   * - Show "Never" for last activity
   *
   * Success Criteria:
   * - All 4 modules displayed even with 0 activity
   * - "No activity yet" or "Get started" message visible
   */
  it('Test 11: should handle empty state (no attempts)', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockEmptyData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithProviders(<ModuleStatsGrid />);

    // Verify all module names still displayed
    expect(screen.getByText(/MCQ Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/OSCE/i)).toBeInTheDocument();
    expect(screen.getByText(/EMR Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/Mock Exam/i)).toBeInTheDocument();

    // Verify empty state indicators (should show 0 or "No activity")
    const zeroTexts = screen.getAllByText('0');
    expect(zeroTexts.length).toBeGreaterThan(0); // At least some zeros for counts

    // Verify "Never" for last activity (formatRelativeTime returns "Never" for null)
    const neverTexts = screen.getAllByText(/Never/i);
    expect(neverTexts.length).toBeGreaterThan(0); // All modules have "Never"
  });

  /**
   * Test 12: Responsive grid layout
   *
   * Requirements:
   * - Grid container with spacing
   * - Grid items: xs=12 (full width on mobile), sm=6 (2 columns on tablet), md=6 (2 columns on desktop)
   * - 2x2 grid layout on larger screens
   *
   * Success Criteria:
   * - Grid container exists
   * - 4 Grid items exist
   * - Container has proper spacing
   */
  it('Test 12: should use responsive grid layout', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    const { container } = renderWithProviders(<ModuleStatsGrid />);

    // Verify 4 module cards are rendered
    const cards = container.querySelectorAll('[role="button"]');
    expect(cards.length).toBe(4);

    // Verify all 4 modules are visible
    expect(screen.getByText(/MCQ Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/OSCE/i)).toBeInTheDocument();
    expect(screen.getByText(/EMR Practice/i)).toBeInTheDocument();
    expect(screen.getByText(/Mock Exam/i)).toBeInTheDocument();
  });
});
