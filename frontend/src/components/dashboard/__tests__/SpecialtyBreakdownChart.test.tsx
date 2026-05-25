/**
 * SpecialtyBreakdownChart Component Tests
 * PRD-MVP-002 Phase 4: Tests 13-14
 *
 * TDD Workflow:
 * - RED: Tests fail (component not implemented)
 * - GREEN: Tests pass (component implemented)
 *
 * Coverage:
 * - Test 13: Render chart with specialty data
 * - Test 14: Handle empty state with message
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SpecialtyBreakdownChart from '../SpecialtyBreakdownChart';
import * as dashboardApi from '../../../api/dashboard';
import type { DashboardOverviewResponse } from '../../../types/dashboard';

// Mock dashboard API hook
vi.mock('../../../api/dashboard');

// Mock Recharts components (they don't render in JSDOM)
vi.mock('recharts', async () => {
  const actual = await vi.importActual('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: any) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children, data }: any) => (
      <div data-testid="bar-chart" data-chart-data={JSON.stringify(data)}>
        {children}
      </div>
    ),
    Bar: ({ dataKey }: any) => <div data-testid={`bar-${dataKey}`} />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    CartesianGrid: () => <div data-testid="cartesian-grid" />,
    Tooltip: () => <div data-testid="tooltip" />,
    Legend: () => <div data-testid="legend" />,
    Cell: ({ fill }: any) => <div data-testid="cell" data-fill={fill} />,
  };
});

// Test data with specialty breakdown
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
    {
      specialty: 'Respiratory',
      attempts: 38,
      avg_score: 75.2,
      strength: 'good',
    },
    {
      specialty: 'Psychiatry',
      attempts: 27,
      avg_score: 55.8,
      strength: 'weak',
    },
    {
      specialty: 'Neurology',
      attempts: 15,
      avg_score: 68.3,
      strength: 'average',
    },
  ],
  recent_activity: [],
  recommendations: [],
};

// Test data with empty specialty breakdown
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

// Helper to render with QueryClient
const renderWithQueryClient = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
};

describe('SpecialtyBreakdownChart - PRD-MVP-002 Phase 4', () => {
  /**
   * Test 13: Render chart with specialty data
   *
   * Requirements:
   * - Horizontal bar chart (BarChart component)
   * - X-axis: Average score (0-100)
   * - Y-axis: Specialty names
   * - Bars color-coded by performance (green >75, orange 60-75, red <60)
   * - Sorted by attempts (most active at top)
   *
   * Success Criteria:
   * - BarChart component rendered
   * - Chart data includes all 4 specialties
   * - Specialties sorted by attempts (Cardiology first with 45 attempts)
   *
   * Note: Recharts components don't render text in JSDOM, so we verify
   * chart data structure and legend instead of rendered axis labels.
   */
  it('Test 13: should render chart with specialty data', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    const { container } = renderWithQueryClient(<SpecialtyBreakdownChart />);

    // Verify chart container rendered
    expect(screen.getByTestId('bar-chart')).toBeInTheDocument();

    // Verify chart data is passed correctly (sorted by attempts)
    const chartElement = screen.getByTestId('bar-chart');
    const chartData = JSON.parse(chartElement.getAttribute('data-chart-data') || '[]');

    expect(chartData).toHaveLength(4);
    expect(chartData[0].specialty).toBe('Cardiology'); // Most attempts (45)
    expect(chartData[0].avg_score).toBe(82.5);
    expect(chartData[1].specialty).toBe('Respiratory'); // 38 attempts
    expect(chartData[2].specialty).toBe('Psychiatry'); // 27 attempts
    expect(chartData[3].specialty).toBe('Neurology'); // 15 attempts

    // Verify chart title
    expect(screen.getByText(/specialty breakdown/i)).toBeInTheDocument();

    // Verify legend (which does render in JSDOM)
    expect(screen.getByText(/excellent/i)).toBeInTheDocument();
    expect(screen.getByText(/average/i)).toBeInTheDocument();
    expect(screen.getByText(/needs improvement/i)).toBeInTheDocument();
  });

  /**
   * Test 14: Handle empty state with message
   *
   * Requirements:
   * - Show "No specialty data available" when specialty_breakdown is empty
   * - No chart rendered
   * - Informative message displayed
   *
   * Success Criteria:
   * - No BarChart component rendered
   * - Empty state message visible
   */
  it('Test 14: should handle empty state with message', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockEmptyData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithQueryClient(<SpecialtyBreakdownChart />);

    // Verify no chart rendered
    expect(screen.queryByTestId('bar-chart')).not.toBeInTheDocument();

    // Verify empty state message
    expect(
      screen.getByText(/no specialty data available/i)
    ).toBeInTheDocument();
  });
});
