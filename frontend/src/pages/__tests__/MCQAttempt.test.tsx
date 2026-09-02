/**
 * MCQAttempt page tests (Phase 2 — component/a11y layer, no backend).
 *
 * Route-param page (`/mcqs/:id/attempt`). Verifies question stem + options
 * render, selecting an option, submit → correct/incorrect feedback with the
 * explanation and citation, loading + error states, and a11y on the loaded
 * question.
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

// --- useNavigate spy (keep the real useParams / Routes) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- API layer ---
const getMCQById = vi.fn();
const submitMCQAttempt = vi.fn();
vi.mock('../../api/mcqs', () => ({
  getMCQById: (...args: unknown[]) => getMCQById(...args),
  submitMCQAttempt: (...args: unknown[]) => submitMCQAttempt(...args),
}));

// --- Permissions (grant MCQ_ATTEMPT so the PermissionGuard renders children) ---
vi.mock('../../hooks/usePermissions', () => ({
  usePermissions: () => ({
    permissions: ['mcq.attempt'],
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
    canCreateContent: () => false,
    canGrade: () => false,
  }),
}));

import MCQAttempt from '../MCQAttempt';

const MCQ = {
  id: 42,
  question_text:
    'A 65-year-old man presents with crushing central chest pain radiating to the left arm.',
  options: {
    A: 'Aspirin 300mg orally',
    B: 'Paracetamol 1g orally',
    C: 'Salbutamol nebuliser',
    D: 'Reassurance and discharge',
  },
  specialty: 'cardiology',
  difficulty: 'hard',
  tags: ['ACS'],
  citation: 'eTG Cardiovascular: Acute coronary syndromes',
};

const renderPage = () =>
  renderWithProviders(<MCQAttempt />, {
    path: '/mcqs/:id/attempt',
    route: '/mcqs/abc/attempt',
    authed: true,
  });

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getMCQById.mockResolvedValue(MCQ);
});

describe('MCQAttempt', () => {
  it('shows a loading spinner while the MCQ is fetching', () => {
    getMCQById.mockReturnValue(new Promise(() => {})); // never resolves
    renderPage();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('renders the question stem and all answer options', async () => {
    renderPage();
    await waitFor(() =>
      expect(
        screen.getByText(/crushing central chest pain/i)
      ).toBeInTheDocument()
    );
    expect(screen.getByRole('radio', { name: /Aspirin 300mg/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /Paracetamol 1g/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /Salbutamol/i })).toBeInTheDocument();
    expect(screen.getByRole('radio', { name: /Reassurance/i })).toBeInTheDocument();
  });

  it('submits the selected answer and shows correct feedback + explanation + citation', async () => {
    const user = userEvent.setup();
    submitMCQAttempt.mockResolvedValue({
      is_correct: true,
      correct_answer: 'A',
      explanation:
        'Aspirin 300mg is first-line antiplatelet therapy in suspected ACS.',
    });
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole('radio', { name: /Aspirin 300mg/i })).toBeInTheDocument()
    );

    await user.click(screen.getByRole('radio', { name: /Aspirin 300mg/i }));
    await user.click(screen.getByRole('button', { name: /Submit Answer/i }));

    expect(submitMCQAttempt).toHaveBeenCalledTimes(1);
    await waitFor(() => expect(screen.getByText(/Correct!/i)).toBeInTheDocument());
    expect(
      screen.getByText(/first-line antiplatelet therapy/i)
    ).toBeInTheDocument();
    // Citation from the MCQ is displayed alongside the explanation
    expect(screen.getByText(/eTG Cardiovascular/i)).toBeInTheDocument();
  });

  it('shows incorrect feedback with the correct answer when the answer is wrong', async () => {
    const user = userEvent.setup();
    submitMCQAttempt.mockResolvedValue({
      is_correct: false,
      correct_answer: 'A',
      explanation: 'Paracetamol does not treat acute coronary syndrome.',
    });
    renderPage();
    await waitFor(() =>
      expect(screen.getByRole('radio', { name: /Paracetamol 1g/i })).toBeInTheDocument()
    );

    await user.click(screen.getByRole('radio', { name: /Paracetamol 1g/i }));
    await user.click(screen.getByRole('button', { name: /Submit Answer/i }));

    await waitFor(() => expect(screen.getByText(/Incorrect\./i)).toBeInTheDocument());
    expect(screen.getByText(/Correct answer:/i)).toBeInTheDocument();
  });

  it('shows an error state when the MCQ fails to load', async () => {
    getMCQById.mockRejectedValue(new Error('boom'));
    renderPage();
    await waitFor(() =>
      expect(screen.getByText(/Failed to load MCQ/i)).toBeInTheDocument()
    );
    expect(
      screen.getByRole('button', { name: /Back to Browser/i })
    ).toBeInTheDocument();
  });

  it('has no accessibility violations on the loaded question', async () => {
    const { container } = renderPage();
    await waitFor(() =>
      expect(screen.getByRole('radio', { name: /Aspirin 300mg/i })).toBeInTheDocument()
    );
    await expectNoA11yViolations(container);
  });
});
