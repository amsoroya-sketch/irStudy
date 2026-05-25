/**
 * RecommendationsPanel Component Tests
 * PRD-MVP-002 Phase 6: Tests 17-18
 *
 * Coverage:
 * - Test 17: Display recommendations with priority badges
 * - Test 18: Handle empty state (no recommendations)
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import RecommendationsPanel from '../RecommendationsPanel';
import * as dashboardApi from '../../../api/dashboard';
import type { DashboardOverviewResponse } from '../../../types/dashboard';

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
  recent_activity: [],
  recommendations: [
    { module: 'MCQ', specialty: 'Psychiatry', reason: 'Low accuracy (55.8%) - needs improvement', priority: 'high' },
    { module: 'OSCE', specialty: 'Neurology', reason: 'Practice clinical examination skills', priority: 'medium' },
    { module: 'EMR', specialty: 'Cardiology', reason: 'Strengthen EMR documentation', priority: 'low' },
  ],
};

const mockEmptyData: DashboardOverviewResponse = {
  ...mockDashboardData,
  recommendations: [],
};

const createTestQueryClient = () =>
  new QueryClient({ defaultOptions: { queries: { retry: false } } });

const renderWithQueryClient = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>);
};

describe('RecommendationsPanel - PRD-MVP-002 Phase 6', () => {
  it('Test 17: should display recommendations with priority badges', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithQueryClient(<RecommendationsPanel />);

    // Verify title
    expect(screen.getByText(/recommendations/i)).toBeInTheDocument();

    // Verify all recommendations displayed
    expect(screen.getByText(/Psychiatry/i)).toBeInTheDocument();
    expect(screen.getByText(/Low accuracy.*needs improvement/i)).toBeInTheDocument();
    expect(screen.getByText(/Neurology/i)).toBeInTheDocument();
    expect(screen.getByText(/Practice clinical examination/i)).toBeInTheDocument();
    expect(screen.getByText(/Cardiology/i)).toBeInTheDocument();
    expect(screen.getByText(/Strengthen EMR documentation/i)).toBeInTheDocument();

    // Verify priority badges (exact text match for badge labels)
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('LOW')).toBeInTheDocument();
  });

  it('Test 18: should handle empty state (no recommendations)', () => {
    vi.mocked(dashboardApi.useDashboardOverview).mockReturnValue({
      data: mockEmptyData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as any);

    renderWithQueryClient(<RecommendationsPanel />);

    // Verify empty state message
    expect(screen.getByText(/no recommendations/i)).toBeInTheDocument();
  });
});
