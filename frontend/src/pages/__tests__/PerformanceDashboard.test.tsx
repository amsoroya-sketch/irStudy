/**
 * PerformanceDashboard page tests (Phase 2 — component/a11y layer, no backend).
 *
 * Mocks the dashboard analytics hooks and asserts the page renders its stat
 * cards / charts / panels with data, plus loading, no-data (empty), the inner
 * "no trend / no specialty" info alerts, and error states. a11y on the loaded
 * dashboard.
 *
 * Recharts' ResponsiveContainer is given a fixed size so the real chart
 * components render under jsdom (ResizeObserver is polyfilled in test/setup.ts).
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  waitFor,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';
import type { DashboardData, WeeklyTrendsResponse } from '../../types/dashboard';

// --- Dashboard analytics hooks ---
const useDashboard = vi.fn();
const useWeeklyTrends = vi.fn();
vi.mock('../../hooks/useDashboard', () => ({
  useDashboard: () => useDashboard(),
  useWeeklyTrends: (weeks: number) => useWeeklyTrends(weeks),
}));

// --- Recharts: keep real charts but give ResponsiveContainer a size ---
vi.mock('recharts', async () => {
  const actual = await vi.importActual<typeof import('recharts')>('recharts');
  return {
    ...actual,
    ResponsiveContainer: ({ children }: { children?: React.ReactNode }) => (
      <div style={{ width: 800, height: 400 }}>{children}</div>
    ),
  };
});

import PerformanceDashboard from '../PerformanceDashboard';

const DASHBOARD: DashboardData = {
  total_mcq_attempts: 120,
  mcq_accuracy_rate: 76.5,
  total_osce_completions: 8,
  study_cards_reviewed: 45,
  study_card_retention_rate: 82.0,
  specialty_breakdown: [
    {
      specialty: 'Cardiology',
      total_attempts: 40,
      correct_attempts: 32,
      accuracy_rate: 80,
      average_time_seconds: 45,
    },
  ],
  weak_areas: [
    {
      specialty: 'Psychiatry',
      accuracy_rate: 55,
      total_attempts: 10,
      recommended_study_cards: 6,
    },
  ],
};

const TRENDS: WeeklyTrendsResponse = {
  weeks: 8,
  trends: [
    {
      week_start: '2026-08-01T00:00:00Z',
      mcq_attempts: 20,
      accuracy_rate: 75,
      study_cards_reviewed: 10,
    },
  ],
};

const setDashboard = (v: Partial<ReturnType<typeof useDashboard>>) =>
  useDashboard.mockReturnValue({ data: undefined, isLoading: false, error: null, ...v });
const setTrends = (v: Partial<ReturnType<typeof useWeeklyTrends>>) =>
  useWeeklyTrends.mockReturnValue({ data: undefined, isLoading: false, error: null, ...v });

beforeEach(() => {
  vi.clearAllMocks();
  setDashboard({ data: DASHBOARD });
  setTrends({ data: TRENDS });
});

describe('PerformanceDashboard', () => {
  it('renders stat cards, charts and panels with data', () => {
    renderWithProviders(<PerformanceDashboard />);

    expect(
      screen.getByRole('heading', { name: /Performance Dashboard/i })
    ).toBeInTheDocument();
    // Stat cards
    expect(screen.getByText('MCQ Attempts')).toBeInTheDocument();
    expect(screen.getByText('120')).toBeInTheDocument();
    // "OSCE Completions" is both a StatCard title and an ExamReadiness factor label
    expect(screen.getAllByText('OSCE Completions').length).toBeGreaterThan(0);
    // Panels / charts (real components render from the mocked data)
    expect(
      screen.getByRole('heading', { name: /AMC Exam Readiness/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /Areas for Improvement/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /Weekly Performance Trends/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /Performance by Specialty/i })
    ).toBeInTheDocument();
  });

  it('shows the loading spinner while data is fetching', () => {
    setDashboard({ data: undefined, isLoading: true });
    setTrends({ data: undefined, isLoading: true });
    renderWithProviders(<PerformanceDashboard />);
    expect(screen.getByLabelText('Loading dashboard data')).toBeInTheDocument();
  });

  it('shows the no-data notice when the dashboard payload is empty', () => {
    setDashboard({ data: undefined });
    setTrends({ data: undefined });
    renderWithProviders(<PerformanceDashboard />);
    expect(screen.getByText(/No dashboard data available/i)).toBeInTheDocument();
  });

  it('shows inner empty-state alerts when trends and specialty data are empty', () => {
    setDashboard({ data: { ...DASHBOARD, specialty_breakdown: [] } });
    setTrends({ data: { weeks: 8, trends: [] } });
    renderWithProviders(<PerformanceDashboard />);
    expect(screen.getByText(/No trend data available yet/i)).toBeInTheDocument();
    expect(screen.getByText(/No specialty data available yet/i)).toBeInTheDocument();
  });

  it('shows an error alert when a query fails', () => {
    setDashboard({ data: undefined, error: new Error('network down') });
    renderWithProviders(<PerformanceDashboard />);
    expect(screen.getByText(/Failed to load dashboard data/i)).toBeInTheDocument();
  });

  it('has no accessibility violations on the loaded dashboard', async () => {
    const { container } = renderWithProviders(<PerformanceDashboard />);
    await waitFor(() =>
      expect(
        screen.getByRole('heading', { name: /Performance Dashboard/i })
      ).toBeInTheDocument()
    );
    await expectNoA11yViolations(container);
  });
});
