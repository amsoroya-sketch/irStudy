/**
 * MCQBrowser page tests (Phase 2 — component/a11y layer, no backend).
 *
 * Verifies the MCQ list renders from the mocked API, filter/search behaviour,
 * loading / empty / error states, navigation to the attempt route, and that the
 * loaded list has no accessibility violations.
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
import type { MCQListResponse } from '../../types/mcq';

// --- useNavigate spy (only override navigate; keep the rest of react-router) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- API layer ---
const getMCQs = vi.fn();
vi.mock('../../api/mcqs', () => ({
  getMCQs: (...args: unknown[]) => getMCQs(...args),
}));

// --- Permissions (grant everything so RBAC-guarded actions render) ---
vi.mock('../../hooks/usePermissions', () => ({
  usePermissions: () => ({
    permissions: ['mcq.view', 'mcq.attempt', 'mcq.create', 'mcq.update'],
    role: 'student',
    userId: 1,
    isLoading: false,
    error: null,
    hasPermission: () => true,
    hasAnyPermission: () => true,
    hasAllPermissions: () => true,
    isStudent: () => true,
    isEducator: () => false,
    isAdmin: () => false,
    canCreateContent: () => true,
    canGrade: () => false,
  }),
}));

import MCQBrowser from '../MCQBrowser';

const MCQS: MCQListResponse = {
  items: [
    {
      id: 1,
      question: 'A 54-year-old man presents with central crushing chest pain.',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      option_e: '',
      correct_answer: 'A',
      explanation: '',
      category: 'Cardiology',
      difficulty: 'hard',
      tags: ['ACS', 'ECG'],
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
    {
      id: 2,
      question: 'A 4-year-old with fever, rash and irritability.',
      option_a: '',
      option_b: '',
      option_c: '',
      option_d: '',
      option_e: '',
      correct_answer: 'B',
      explanation: '',
      category: 'Paediatrics',
      difficulty: 'easy',
      tags: ['fever'],
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    },
  ],
  total: 2,
  skip: 0,
  limit: 20,
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getMCQs.mockResolvedValue(MCQS);
});

describe('MCQBrowser', () => {
  it('renders the MCQ list from the mocked API', async () => {
    renderWithProviders(<MCQBrowser />);

    await waitFor(() =>
      expect(
        screen.getByText(/central crushing chest pain/i)
      ).toBeInTheDocument()
    );
    expect(screen.getByText(/fever, rash and irritability/i)).toBeInTheDocument();
    // Difficulty + category chips from the data
    expect(screen.getByText('hard')).toBeInTheDocument();
    expect(screen.getByText('Cardiology')).toBeInTheDocument();
  });

  it('shows a loading spinner while MCQs are fetching', () => {
    getMCQs.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithProviders(<MCQBrowser />);
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows the empty state when no MCQs are returned', async () => {
    getMCQs.mockResolvedValue({ items: [], total: 0, skip: 0, limit: 20 });
    renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/No MCQs found/i)).toBeInTheDocument()
    );
  });

  it('shows an error alert when the fetch fails', async () => {
    getMCQs.mockRejectedValue(new Error('boom'));
    renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/Failed to load MCQs/i)).toBeInTheDocument()
    );
  });

  it('refetches with the search query as the user types', async () => {
    const user = userEvent.setup();
    renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/central crushing chest pain/i)).toBeInTheDocument()
    );

    await user.type(screen.getByLabelText('Search'), 'chest');

    await waitFor(() =>
      expect(getMCQs).toHaveBeenCalledWith(
        expect.objectContaining({ search: 'chest' })
      )
    );
  });

  it('refetches with the chosen difficulty filter', async () => {
    const user = userEvent.setup();
    renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/central crushing chest pain/i)).toBeInTheDocument()
    );

    await user.click(screen.getByRole('combobox', { name: 'Difficulty' }));
    await user.click(screen.getByRole('option', { name: 'Hard' }));

    await waitFor(() =>
      expect(getMCQs).toHaveBeenCalledWith(
        expect.objectContaining({ difficulty: 'hard' })
      )
    );
  });

  it('navigates to the attempt route when an MCQ Attempt button is clicked', async () => {
    const user = userEvent.setup();
    renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/central crushing chest pain/i)).toBeInTheDocument()
    );

    await user.click(screen.getAllByRole('button', { name: 'Attempt' })[0]);

    expect(navigateMock).toHaveBeenCalledWith('/mcqs/1/attempt');
  });

  it('has no accessibility violations once the list has loaded', async () => {
    const { container } = renderWithProviders(<MCQBrowser />);
    await waitFor(() =>
      expect(screen.getByText(/central crushing chest pain/i)).toBeInTheDocument()
    );
    await expectNoA11yViolations(container);
  });
});
