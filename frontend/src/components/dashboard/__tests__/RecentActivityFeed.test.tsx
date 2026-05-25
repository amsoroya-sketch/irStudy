/**
 * RecentActivityFeed Component Tests
 * PRD-MVP-002 Phase 5: Tests 15-16
 *
 * Coverage:
 * - Test 15: Display recent activities sorted by time
 * - Test 16: Handle empty state (no recent activity)
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecentActivityFeed from '../RecentActivityFeed';
import * as dashboardApi from '../../../api/dashboard';
import type { DashboardOverviewResponse } from '../../../types/dashboard';

// Mock dashboard API hook
vi.mock('../../../api/dashboard');

const mockDashboardData: DashboardOverviewResponse = {
  overall_progress: {
    total_sessions: 156,
    completion_percentage: 68.5,
    avg_score: 78.3,
    total_time_minutes: 4320,
    last_activity: '2026-05-24T14:30:00Z',
  },
  modules: {
    mcq: { total_attempts: 89, average_score: 75.2, last_activity: '2026-05-24T10:15:00Z', completion_rate: 65.0 },
    osce: { total_attempts: 34, average_score: 82.1, last_activity: '2026-05-23T16:45:00Z', completion_rate: 70.0 },
    emr: { total_sessions: 21, average_score: 79.5, last_activity: '2026-05-24T14:30:00Z', completion_rate: 75.0 },
    mock_exam: { total_exams: 12, average_score: 76.8, last_activity: '2026-05-22T11:00:00Z', completion_rate: 60.0 },
  },
  specialty_breakdown: [],
  recent_activity: [
    { type: 'mcq', description: 'Completed MCQ quiz on Cardiology', score: 85, timestamp: '2026-05-24T14:30:00Z' },
    { type: 'osce', description: 'Completed OSCE session', score: 78, timestamp: '2026-05-24T12:00:00Z' },
    { type: 'emr', description: 'Completed EMR patient case', score: 92, timestamp: '2026-05-23T16:45:00Z' },
    { type: 'mcq', description: 'Completed MCQ quiz on Respiratory', score: 72, timestamp: '2026-05-23T10:00:00Z' },
  ],
  recommendations: [],
};

const mockEmptyData: DashboardOverviewResponse = {
  ...mockDashboardData,
  recent_activity: [],
};

const createTestQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const renderWithQueryClient = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe('RecentActivityFeed - PRD-MVP-002 Phase 5', () => {
  it('Test 15: should display recent activities sorted by time', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithQueryClient(<RecentActivityFeed />);

    // Verify title
    expect(screen.getByText(/recent activity/i)).toBeInTheDocument();

    // Verify all activities displayed
    expect(screen.getByText(/Completed MCQ quiz on Cardiology/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed OSCE session/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed EMR patient case/i)).toBeInTheDocument();
    expect(screen.getByText(/Completed MCQ quiz on Respiratory/i)).toBeInTheDocument();

    // Verify scores displayed
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('78%')).toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
    expect(screen.getByText('72%')).toBeInTheDocument();
  });

  it('Test 16: should handle empty state (no recent activity)', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockEmptyData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithQueryClient(<RecentActivityFeed />);

    // Verify empty state message
    expect(screen.getByText(/no recent activity/i)).toBeInTheDocument();
  });
});
