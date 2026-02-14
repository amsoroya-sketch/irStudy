/**
 * Performance Dashboard Page Tests
 * Tests for dashboard analytics and visualization components
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import PerformanceDashboard from '../../src/pages/PerformanceDashboard';
import * as dashboardHooks from '../../src/hooks/useDashboard';
import type { DashboardData, WeeklyTrendsResponse } from '../../src/types/dashboard';

// Mock dashboard hooks
vi.mock('../../src/hooks/useDashboard', () => ({
  useDashboard: vi.fn(),
  useWeeklyTrends: vi.fn(),
}));

// Mock dashboard data
const mockDashboardData: DashboardData = {
  total_mcq_attempts: 152,
  mcq_accuracy_rate: 73.68,
  total_osce_completions: 8,
  study_cards_reviewed: 64,
  study_card_retention_rate: 78.12,
  specialty_breakdown: [
    {
      specialty: 'cardiology',
      total_attempts: 45,
      correct_attempts: 32,
      accuracy_rate: 71.11,
      average_time_seconds: 95,
    },
    {
      specialty: 'respiratory',
      total_attempts: 38,
      correct_attempts: 30,
      accuracy_rate: 78.95,
      average_time_seconds: 88,
    },
    {
      specialty: 'neurology',
      total_attempts: 12,
      correct_attempts: 7,
      accuracy_rate: 58.33,
      average_time_seconds: 105,
    },
  ],
  weak_areas: [
    {
      specialty: 'neurology',
      accuracy_rate: 58.33,
      total_attempts: 12,
      recommended_study_cards: 47,
    },
  ],
};

// Mock weekly trends data
const mockTrendsData: WeeklyTrendsResponse = {
  weeks: 8,
  trends: [
    {
      week_start: '2026-02-10T00:00:00Z',
      mcq_attempts: 28,
      accuracy_rate: 75.0,
      study_cards_reviewed: 15,
    },
    {
      week_start: '2026-02-03T00:00:00Z',
      mcq_attempts: 35,
      accuracy_rate: 71.43,
      study_cards_reviewed: 22,
    },
    {
      week_start: '2026-01-27T00:00:00Z',
      mcq_attempts: 42,
      accuracy_rate: 69.05,
      study_cards_reviewed: 18,
    },
  ],
};

// Create test QueryClient
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

// Wrapper component
const renderWithQueryClient = (component: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(<QueryClientProvider client={queryClient}>{component}</QueryClientProvider>);
};

describe('PerformanceDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders dashboard title', async () => {
    // Mock successful data loading
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: mockTrendsData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check for dashboard title
    expect(screen.getByText('Performance Dashboard')).toBeInTheDocument();
  });

  it('displays stat cards with correct values', async () => {
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: mockTrendsData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check MCQ stat card
    expect(screen.getByText('MCQ Attempts')).toBeInTheDocument();
    expect(screen.getByText('152')).toBeInTheDocument();
    expect(screen.getByText('73.7% accuracy')).toBeInTheDocument();

    // Check OSCE stat card
    expect(screen.getByText('OSCE Completions')).toBeInTheDocument();
    expect(screen.getByText('8')).toBeInTheDocument();

    // Check Study Cards stat card
    expect(screen.getByText('Study Cards')).toBeInTheDocument();
    expect(screen.getByText('64')).toBeInTheDocument();

    // Check Weak Areas stat card
    expect(screen.getByText('Weak Areas')).toBeInTheDocument();
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('shows loading state initially', async () => {
    // Mock loading state
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check for loading indicator
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders charts after data loads', async () => {
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: mockTrendsData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check for chart titles
    expect(screen.getByText('Weekly Performance Trends')).toBeInTheDocument();
    expect(screen.getByText('Performance by Specialty')).toBeInTheDocument();
  });

  it('displays weak areas panel', async () => {
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: mockTrendsData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check weak areas panel
    expect(screen.getByText('Areas for Improvement')).toBeInTheDocument();
    expect(screen.getByText('Neurology')).toBeInTheDocument();
  });

  it('shows error state on API failure', async () => {
    // Mock error state
    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: new Error('Network error'),
      isError: true,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: undefined,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check error message
    await waitFor(() => {
      expect(screen.getByText(/failed to load dashboard data/i)).toBeInTheDocument();
    });
  });

  it('shows success message when no weak areas', async () => {
    const dataWithNoWeakAreas: DashboardData = {
      ...mockDashboardData,
      weak_areas: [],
    };

    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: dataWithNoWeakAreas,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: mockTrendsData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check for success message in weak areas panel
    expect(screen.getByText(/great work/i)).toBeInTheDocument();
    expect(screen.getByText(/no weak areas identified/i)).toBeInTheDocument();
  });

  it('displays info message when no trends available', async () => {
    const trendsWithNoData: WeeklyTrendsResponse = {
      weeks: 8,
      trends: [],
    };

    vi.mocked(dashboardHooks.useDashboard).mockReturnValue({
      data: mockDashboardData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useDashboard>);

    vi.mocked(dashboardHooks.useWeeklyTrends).mockReturnValue({
      data: trendsWithNoData,
      isLoading: false,
      error: null,
      isError: false,
      refetch: vi.fn(),
    } as ReturnType<typeof dashboardHooks.useWeeklyTrends>);

    renderWithQueryClient(<PerformanceDashboard />);

    // Check for info message about trends
    expect(screen.getByText(/no trend data available yet/i)).toBeInTheDocument();
  });
});
