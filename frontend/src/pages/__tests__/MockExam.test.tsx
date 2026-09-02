/**
 * Mock Exam page tests (Phase 3 — component/a11y layer, no backend).
 *
 * Covers the two self-contained mock-exam pages:
 *  - MockExamStart: renders the exam brief, confirm dialog -> createMockExam ->
 *    navigate to station 1, and the create-error alert.
 *  - MockExamResults: route-param page; loading / error, the pass banner +
 *    station table from a mocked result, and a "return to dashboard" nav.
 * a11y on both loaded pages.
 *
 * Uses the Phase 0 foundations: renderWithProviders + expectNoA11yViolations.
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  waitFor,
  userEvent,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';
import type { MockExamResultsResponse } from '../../api/mockExams';

// --- useNavigate spy (keep the real MemoryRouter/useParams) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- API layer ---
const createMockExam = vi.fn();
const getMockExamResults = vi.fn();
vi.mock('../../api/mockExams', () => ({
  createMockExam: (...a: unknown[]) => createMockExam(...a),
  getMockExamResults: (...a: unknown[]) => getMockExamResults(...a),
}));

import MockExamStart from '../osce/MockExamStart';
import MockExamResults from '../osce/MockExamResults';

const RESULTS: MockExamResultsResponse = {
  overall_score: 210,
  percentage: 87.5,
  overall_pass_fail: 'PASS',
  stations: [
    {
      station_number: 1,
      specialty: 'Cardiology',
      persona_name: 'John Brown',
      score: 13,
      pass_fail: 'PASS',
      attempt_id: 'a-1',
    },
    {
      station_number: 2,
      specialty: 'Respiratory',
      persona_name: 'Mary White',
      score: 7,
      pass_fail: 'FAIL',
      attempt_id: 'a-2',
    },
  ],
  summary_statistics: {
    stations_passed: 14,
    stations_failed: 2,
    average_score_per_station: 13.1,
    performance_by_specialty: [
      {
        specialty: 'Cardiology',
        total_score: 26,
        max_score: 30,
        percentage: 86.7,
        stations_passed: 2,
        total_stations: 2,
      },
    ],
  },
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('MockExamStart', () => {
  it('renders the exam brief and format details', () => {
    renderWithProviders(<MockExamStart />);
    expect(
      screen.getByRole('heading', { name: /AMC Clinical Examination Mock Exam/i })
    ).toBeInTheDocument();
    expect(screen.getByText('16 Stations')).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Start mock exam/i })
    ).toBeInTheDocument();
  });

  it('confirms and creates an exam, then navigates to station 1', async () => {
    const user = userEvent.setup();
    createMockExam.mockResolvedValue({ exam_id: 'exam-9' });
    renderWithProviders(<MockExamStart />);

    await user.click(screen.getByRole('button', { name: /Start mock exam/i }));
    // Confirmation dialog appears.
    expect(
      await screen.findByRole('heading', { name: /Ready to Begin\?/i })
    ).toBeInTheDocument();
    await user.click(screen.getByRole('button', { name: /Confirm and start exam/i }));

    await waitFor(() => expect(createMockExam).toHaveBeenCalledTimes(1));
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/osce/mock-exam/exam-9/station/1')
    );
  });

  it('shows an error alert when exam creation fails', async () => {
    const user = userEvent.setup();
    createMockExam.mockRejectedValue(new Error('boom'));
    renderWithProviders(<MockExamStart />);

    await user.click(screen.getByRole('button', { name: /Start mock exam/i }));
    await user.click(
      await screen.findByRole('button', { name: /Confirm and start exam/i })
    );

    expect(
      await screen.findByText(/Failed to create mock exam/i)
    ).toBeInTheDocument();
  });

  it('has no accessibility violations on the start page', async () => {
    const { container } = renderWithProviders(<MockExamStart />);
    await expectNoA11yViolations(container);
  });
});

const renderResults = () =>
  renderWithProviders(<MockExamResults />, {
    path: '/osce/mock-exam/:examId/results',
    route: '/osce/mock-exam/exam-9/results',
    authed: true,
  });

describe('MockExamResults', () => {
  it('shows the loading state while results are fetching', () => {
    getMockExamResults.mockReturnValue(new Promise(() => {})); // never resolves
    renderResults();
    expect(screen.getByText(/Loading results/i)).toBeInTheDocument();
  });

  it('shows an error state when results fail to load', async () => {
    getMockExamResults.mockRejectedValue(new Error('boom'));
    renderResults();
    expect(
      await screen.findByText(/Failed to load exam results/i)
    ).toBeInTheDocument();
  });

  it('renders the pass banner, summary and station breakdown', async () => {
    getMockExamResults.mockResolvedValue(RESULTS);
    renderResults();

    expect(
      await screen.findByRole('heading', { name: /Congratulations! You Passed/i })
    ).toBeInTheDocument();
    expect(screen.getByText(/Overall Score: 210\/240/i)).toBeInTheDocument();
    // Station table content.
    expect(
      screen.getByRole('table', { name: /Mock exam station results/i })
    ).toBeInTheDocument();
    expect(screen.getByText('John Brown')).toBeInTheDocument();
    expect(screen.getByText('Mary White')).toBeInTheDocument();
  });

  it('returns to the dashboard from the action buttons', async () => {
    const user = userEvent.setup();
    getMockExamResults.mockResolvedValue(RESULTS);
    renderResults();
    await screen.findByRole('heading', { name: /Congratulations! You Passed/i });

    await user.click(
      screen.getByRole('button', { name: /Return to Dashboard/i })
    );
    expect(navigateMock).toHaveBeenCalledWith('/dashboard');
  });

  it('has no accessibility violations on the loaded results', async () => {
    getMockExamResults.mockResolvedValue(RESULTS);
    const { container } = renderResults();
    await screen.findByRole('heading', { name: /Congratulations! You Passed/i });
    await expectNoA11yViolations(container);
  });
});
