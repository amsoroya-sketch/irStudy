/**
 * StudyCards page tests (Phase 3 — component/a11y layer, no backend).
 *
 * The `/study-cards` route renders <FlashcardReview />. This spec exercises it
 * through the Phase 0 renderWithProviders harness (adding router + a11y cover
 * on top of the component-level suite in
 * src/components/study-cards/__tests__/FlashcardReview.test.tsx): loading /
 * empty states, a card rendering, the show-answer + rating interaction, and
 * a11y on the loaded card.
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
import type { StudyCard } from '../../types/study-cards';

// --- useNavigate spy (keep the real MemoryRouter) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- API layer (useStudyCards -> getStudyCards; rating -> reviewCard) ---
const getStudyCards = vi.fn();
const reviewCard = vi.fn();
vi.mock('../../api/studyCards', () => ({
  getStudyCards: (...a: unknown[]) => getStudyCards(...a),
  reviewCard: (...a: unknown[]) => reviewCard(...a),
}));

import { FlashcardReview } from '../../components/study-cards/FlashcardReview';

const CARD: StudyCard = {
  id: 1,
  card_id: 'CARD-550e8400-e29b-41d4-a716-446655440000-1',
  user_id: 42,
  session_id: '550e8400-e29b-41d4-a716-446655440000',
  question: 'What is the SOCRATES framework for pain assessment?',
  answer: 'Site, Onset, Character, Radiation, Associations, Time, Exacerbating, Severity.',
  citations: [
    {
      source: "Talley & O'Connor Clinical Examination 9th Ed",
      qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
      confidence: 0.85,
      page: '412',
    },
  ],
  sm2_params: { ease_factor: 2.5, interval_days: 1, repetitions: 0 },
  next_review_date: new Date().toISOString(),
  last_reviewed_at: null,
  specialty: 'general_medicine',
  topic: 'Pain Assessment',
  subtopic: 'History Taking',
  difficulty: 'easy',
  tags: ['SOCRATES'],
  card_type: 'history_taking',
  is_active: true,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getStudyCards.mockResolvedValue({ cards: [CARD], total_due: 1 });
});

describe('StudyCards (FlashcardReview page)', () => {
  it('shows the loading skeleton while cards are fetching', () => {
    getStudyCards.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithProviders(<FlashcardReview />, { route: '/study-cards', authed: true });
    expect(screen.getByTestId('flashcard-skeleton')).toBeInTheDocument();
  });

  it('shows the empty state when no cards are due', async () => {
    getStudyCards.mockResolvedValue({ cards: [], total_due: 0 });
    renderWithProviders(<FlashcardReview />, { route: '/study-cards', authed: true });
    expect(
      await screen.findByText(/No Cards Due for Review/i)
    ).toBeInTheDocument();
  });

  it('renders the first card question and hides the answer initially', async () => {
    renderWithProviders(<FlashcardReview />, { route: '/study-cards', authed: true });
    expect(await screen.findByText(CARD.question)).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /show answer/i })
    ).toBeInTheDocument();
    expect(screen.queryByText(CARD.answer)).not.toBeInTheDocument();
  });

  it('reveals the answer and submits a rating via reviewCard', async () => {
    const user = userEvent.setup();
    reviewCard.mockResolvedValue({
      card_id: 1,
      quality: 3,
      interval_days: 6,
      ease_factor: 2.6,
      repetitions: 1,
      next_review_date: new Date().toISOString(),
      message: 'Good work!',
      quality_description: 'Correct',
    });
    renderWithProviders(<FlashcardReview />, { route: '/study-cards', authed: true });

    await user.click(await screen.findByRole('button', { name: /show answer/i }));
    expect(await screen.findByText(CARD.answer)).toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: /good/i }));
    await waitFor(() => expect(reviewCard).toHaveBeenCalledWith(1, 3));
  });

  it('has no accessibility violations on the loaded card', async () => {
    const { container } = renderWithProviders(<FlashcardReview />, {
      route: '/study-cards',
      authed: true,
    });
    await screen.findByText(CARD.question);
    await expectNoA11yViolations(container);
  });
});
