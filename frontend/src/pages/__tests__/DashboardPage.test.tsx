/**
 * Dashboard (RBAC landing page) tests (Phase 2 — component/a11y layer).
 *
 * Covers src/pages/Dashboard.tsx — the role-based landing with EMR metrics,
 * mock-exam promo and the RBAC quick-action module cards. Complements (does not
 * duplicate) UnifiedDashboardPage.test.tsx and the components/dashboard/* specs.
 *
 * Verifies: module cards render, navigation on card click, the permissions
 * loading state, the EMR error surface, and a11y on the loaded dashboard.
 *
 * The recharts-based EMR presentational children have their own specs, so they
 * are stubbed here to keep this page test focused and deterministic; the real
 * EMRMetricsGrid is kept so its error/loaded states are exercised.
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  waitFor,
  userEvent,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';

// --- useNavigate spy ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- Auth context (Dashboard reads user.id) ---
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 'u1', email: 'student@example.com' } }),
}));

// --- Permissions (mutable loading flag; all permissions granted) ---
let mockPermsLoading = false;
vi.mock('../../hooks/usePermissions', () => ({
  usePermissions: () => ({
    permissions: ['mcq.view', 'osce.view', 'progress.view.own'],
    role: 'student',
    userId: 1,
    isLoading: mockPermsLoading,
    error: null,
    hasPermission: () => true,
    hasAnyPermission: () => true,
    hasAllPermissions: () => true,
    isStudent: () => true,
    isEducator: () => false,
    isAdmin: () => false,
    canCreateContent: () => false,
    canGrade: () => false,
  }),
}));

// --- EMR dashboard data (mutable per test) ---
let mockEMRResult: {
  data: Record<string, unknown>;
  isLoading: boolean;
  isError: boolean;
  errors: Array<Error | null>;
};
vi.mock('../../hooks/useEMRDashboardData', () => ({
  useEMRDashboardData: () => mockEMRResult,
  default: () => mockEMRResult,
}));

// --- Conversion stats query ---
vi.mock('../../api/integration', () => ({
  getConversionStats: vi.fn().mockResolvedValue({
    total_conversions: 0,
    average_pre_fill_percentage: 0,
    last_conversion_at: null,
  }),
}));

// --- Stub the recharts-based EMR children (own specs cover them) ---
vi.mock('../../components/dashboard/RecentEMRSessionsList', () => ({
  RecentEMRSessionsList: () => null,
}));
vi.mock('../../components/dashboard/EMRSpecialtyChart', () => ({
  EMRSpecialtyChart: () => null,
}));
vi.mock('../../components/dashboard/EMRSystemUsagePie', () => ({
  EMRSystemUsagePie: () => null,
}));

import Dashboard from '../Dashboard';

const METRICS = {
  total_sessions: 12,
  completed_sessions: 9,
  in_progress_sessions: 3,
  avg_validation_score: 7.8,
  avg_typing_wpm: 42,
  improvement_percentage: 5.5,
  ahpra_compliance_rate: 88,
  total_time_spent_seconds: 7200,
  epic_sessions: 8,
  cerner_sessions: 4,
  specialty_stats: [{ specialty: 'Cardiology', session_count: 5, avg_score: 8.1 }],
};

const okResult = () => ({
  data: { metrics: METRICS, recentSessions: [], weeklyTrends: [], weakAreas: [] },
  isLoading: false,
  isError: false,
  errors: [null, null, null, null],
});

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  mockPermsLoading = false;
  mockEMRResult = okResult();
});

describe('Dashboard (RBAC landing page)', () => {
  it('renders the RBAC quick-action module cards and EMR/mock sections', async () => {
    renderWithProviders(<Dashboard />, { authed: true });

    // Section headings
    expect(
      screen.getByRole('heading', { name: /EMR Documentation Practice/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /AMC Mock Examination/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { name: /Quick Actions/i })
    ).toBeInTheDocument();

    // Module cards (permissions granted)
    expect(screen.getByRole('heading', { name: /MCQ Practice/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /OSCE Scenarios/i })).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /My Progress/i })).toBeInTheDocument();

    // Real EMRMetricsGrid renders a stat card from the mocked metrics
    expect(screen.getByText('Total Sessions')).toBeInTheDocument();
  });

  it('navigates when quick-action / section buttons are clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Dashboard />, { authed: true });

    await user.click(screen.getByRole('button', { name: /Browse MCQs/i }));
    expect(navigateMock).toHaveBeenCalledWith('/mcqs');

    await user.click(screen.getByRole('button', { name: /Start EMR Session/i }));
    expect(navigateMock).toHaveBeenCalledWith('/emr/cases');

    await user.click(screen.getByRole('button', { name: /Start Mock Exam/i }));
    expect(navigateMock).toHaveBeenCalledWith('/osce/mock-exam/start');
  });

  it('shows the loading state while permissions are resolving', () => {
    mockPermsLoading = true;
    renderWithProviders(<Dashboard />, { authed: true });
    expect(screen.getByText(/^Loading\.\.\.$/)).toBeInTheDocument();
  });

  it('surfaces an EMR error via the metrics grid when the EMR queries fail', async () => {
    mockEMRResult = {
      data: { metrics: undefined, recentSessions: [], weeklyTrends: [], weakAreas: [] },
      isLoading: false,
      isError: true,
      errors: [new Error('boom'), null, null, null],
    };
    renderWithProviders(<Dashboard />, { authed: true });
    await waitFor(() =>
      expect(screen.getByText(/Failed to load EMR metrics/i)).toBeInTheDocument()
    );
  });

  it('has no accessibility violations on the loaded dashboard', async () => {
    const { container } = renderWithProviders(<Dashboard />, { authed: true });
    await waitFor(() =>
      expect(screen.getByRole('heading', { name: /Quick Actions/i })).toBeInTheDocument()
    );
    await expectNoA11yViolations(container);
  });
});
