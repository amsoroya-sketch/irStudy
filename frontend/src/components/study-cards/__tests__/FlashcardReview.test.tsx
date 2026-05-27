/**
 * FlashcardReview Component Tests
 * PRD-P1-006 Phase 1: Flashcard Review Interface
 * Tests 1-8 from COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md
 *
 * TDD APPROACH: These tests are written FIRST (RED phase)
 * Component implementation will be written to pass these tests (GREEN phase)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { FlashcardReview } from '../FlashcardReview';
import { StudyCard } from '../../../types/study-cards';
import * as api from '../../../api/studyCards';

// Mock the API module
vi.mock('../../../api/studyCards');

// Mock useNavigate from react-router-dom
const mockNavigate = vi.fn();
vi.mock('react-router-dom', () => ({
  useNavigate: () => mockNavigate,
}));

describe('FlashcardReview Component', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Create fresh QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false, // Disable retries for testing
          gcTime: 0, // Disable cache for testing
        },
      },
    });

    // Reset mocks
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Cleanup query client
    queryClient.clear();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  // Test 1: Display loading skeleton while fetching cards
  it('should display loading skeleton while fetching cards', () => {
    // Mock API to return a pending promise (loading state)
    vi.mocked(api.getStudyCards).mockImplementation(
      () => new Promise(() => {}) // Never resolves (loading forever)
    );

    render(<FlashcardReview />, { wrapper });

    // Verify skeleton is shown
    expect(screen.getByTestId('flashcard-skeleton')).toBeInTheDocument();
    expect(screen.queryByTestId('flashcard-card')).not.toBeInTheDocument();
  });

  // Test 2: Display empty state when no cards are due for review
  it('should display empty state when no cards are due for review', async () => {
    // Mock API to return empty array
    vi.mocked(api.getStudyCards).mockResolvedValueOnce({
      cards: [],
      total_due: 0,
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/no cards due for review/i)).toBeInTheDocument();
      expect(screen.getByText(/check back tomorrow/i)).toBeInTheDocument();
    });

    // Verify skeleton is gone
    expect(screen.queryByTestId('flashcard-skeleton')).not.toBeInTheDocument();
  });

  // Test 3: Display first card when cards are fetched successfully
  it('should display first card when cards are fetched successfully', async () => {
    const mockCards: StudyCard[] = [
      {
        id: 1,
        card_id: 'CARD-550e8400-e29b-41d4-a716-446655440000-1',
        user_id: 42,
        session_id: '550e8400-e29b-41d4-a716-446655440000',
        question: 'What is the SOCRATES framework for pain assessment?',
        answer:
          'SOCRATES is a mnemonic for pain assessment:\n\n- **S**ite: Where is the pain?\n- **O**nset: When did it start?\n- **C**haracter: What does it feel like?\n- **R**adiation: Does it spread anywhere?\n- **A**ssociations: Any other symptoms?\n- **T**ime course: Pattern over time?\n- **E**xacerbating/relieving factors: What makes it better/worse?\n- **S**everity: How bad is it (0-10)?',
        citations: [
          {
            source: "Talley & O'Connor Clinical Examination 9th Ed",
            qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
            confidence: 0.85,
            page: '412',
          },
        ],
        sm2_params: {
          ease_factor: 2.5,
          interval_days: 1,
          repetitions: 0,
        },
        next_review_date: new Date().toISOString(),
        last_reviewed_at: null,
        specialty: 'general_medicine',
        topic: 'Pain Assessment',
        subtopic: 'History Taking',
        difficulty: 'easy',
        tags: ['SOCRATES', 'pain', 'history-taking'],
        card_type: 'history_taking',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    vi.mocked(api.getStudyCards).mockResolvedValueOnce({
      cards: mockCards,
      total_due: 1,
    });

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      // Verify question is shown (not answer initially - flashcard should start with question side)
      expect(screen.getByText('What is the SOCRATES framework for pain assessment?')).toBeInTheDocument();

      // Verify "Show Answer" button exists (answer should be hidden initially)
      expect(screen.getByRole('button', { name: /show answer/i })).toBeInTheDocument();
    });

    // Verify skeleton is gone
    expect(screen.queryByTestId('flashcard-skeleton')).not.toBeInTheDocument();

    // Verify card is present
    expect(screen.getByTestId('flashcard-card')).toBeInTheDocument();
  });

  // Test 4: Handle API error with error message
  it('should display error state when API call fails', async () => {
    // Mock API to reject with network error
    const error = new Error('Network error');
    vi.mocked(api.getStudyCards).mockRejectedValueOnce(error);

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/failed to load cards/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
    });

    // Verify skeleton is gone
    expect(screen.queryByTestId('flashcard-skeleton')).not.toBeInTheDocument();
  });

  // Test 5: Show 401 error and redirect to login
  it('should redirect to login when 401 Unauthorized received', async () => {
    // Mock API to reject with 401 error
    const error = {
      response: {
        status: 401,
        data: { detail: 'Unauthorized' },
      },
    };

    vi.mocked(api.getStudyCards).mockRejectedValueOnce(error);

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      // Verify navigate was called with /login
      expect(mockNavigate).toHaveBeenCalledWith('/login');
    });
  });

  // Test 6: Show 403 error with access denied message
  it('should display permission error when 403 Forbidden received', async () => {
    // Mock API to reject with 403 error
    const error = {
      response: {
        status: 403,
        data: { detail: 'You do not own this session' },
      },
    };

    vi.mocked(api.getStudyCards).mockRejectedValueOnce(error);

    render(<FlashcardReview />, { wrapper });

    await waitFor(() => {
      expect(screen.getByText(/permission denied/i)).toBeInTheDocument();
      expect(screen.getByText(/you do not own this session/i)).toBeInTheDocument();
    });
  });

  // Test 7: Refetch cards when user navigates back to page
  it('should refetch cards when retry button is clicked', async () => {
    const user = userEvent.setup();

    // Mock API to fail first, then succeed
    const mockCards: StudyCard[] = [
      {
        id: 1,
        card_id: 'CARD-550e8400-e29b-41d4-a716-446655440000-1',
        user_id: 42,
        session_id: '550e8400-e29b-41d4-a716-446655440000',
        question: 'Test Question',
        answer: 'Test Answer',
        citations: [],
        sm2_params: {
          ease_factor: 2.5,
          interval_days: 1,
          repetitions: 0,
        },
        next_review_date: new Date().toISOString(),
        last_reviewed_at: null,
        specialty: 'general_medicine',
        topic: 'Test',
        subtopic: null,
        difficulty: 'easy',
        tags: [],
        card_type: 'history_taking',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    vi.mocked(api.getStudyCards)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({
        cards: mockCards,
        total_due: 1,
      });

    render(<FlashcardReview />, { wrapper });

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/failed to load cards/i)).toBeInTheDocument();
    });

    // Click retry button
    const retryButton = screen.getByRole('button', { name: /retry/i });
    await user.click(retryButton);

    // Wait for cards to load
    await waitFor(() => {
      expect(screen.getByText('Test Question')).toBeInTheDocument();
    });

    // Verify API was called twice
    expect(api.getStudyCards).toHaveBeenCalledTimes(2);
  });

  // Test 8: Invalidate cache when card reviewed
  it('should invalidate cache when card is reviewed', async () => {
    const user = userEvent.setup();

    const mockCards: StudyCard[] = [
      {
        id: 1,
        card_id: 'CARD-550e8400-e29b-41d4-a716-446655440000-1',
        user_id: 42,
        session_id: '550e8400-e29b-41d4-a716-446655440000',
        question: 'Test Question',
        answer: 'Test Answer',
        citations: [],
        sm2_params: {
          ease_factor: 2.5,
          interval_days: 1,
          repetitions: 0,
        },
        next_review_date: new Date().toISOString(),
        last_reviewed_at: null,
        specialty: 'general_medicine',
        topic: 'Test',
        subtopic: null,
        difficulty: 'easy',
        tags: [],
        card_type: 'history_taking',
        is_active: true,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      },
    ];

    // Mock initial fetch
    vi.mocked(api.getStudyCards).mockResolvedValue({
      cards: mockCards,
      total_due: 1,
    });

    // Mock review API
    vi.mocked(api.reviewCard).mockResolvedValueOnce({
      card_id: 1,
      quality: 3,
      interval_days: 6,
      ease_factor: 2.6,
      repetitions: 1,
      next_review_date: new Date(Date.now() + 6 * 24 * 60 * 60 * 1000).toISOString(),
      message: 'Good work! Next review in 6 day(s). Correct, but difficult.',
      quality_description: 'Correct, but difficult',
    });

    render(<FlashcardReview />, { wrapper });

    // Wait for card to load
    await waitFor(() => {
      expect(screen.getByText('Test Question')).toBeInTheDocument();
    });

    // Show answer
    const showAnswerButton = screen.getByRole('button', { name: /show answer/i });
    await user.click(showAnswerButton);

    // Wait for answer to appear
    await waitFor(() => {
      expect(screen.getByText('Test Answer')).toBeInTheDocument();
    });

    // Click "Good" button to review card
    const goodButton = screen.getByRole('button', { name: /good/i });
    await user.click(goodButton);

    // Verify review API was called
    await waitFor(() => {
      expect(api.reviewCard).toHaveBeenCalledWith(1, 3);
    });

    // Verify cards were refetched (cache invalidated)
    // getStudyCards should be called at least twice: initial fetch + refetch after review
    await waitFor(() => {
      expect(api.getStudyCards).toHaveBeenCalledTimes(2);
    });
  });
});
