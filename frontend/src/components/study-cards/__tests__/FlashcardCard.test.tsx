/**
 * FlashcardCard Component Tests
 * PRD-P1-006 Phase 2: Flashcard Card Component
 * Tests 9-18 from COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md
 *
 * TDD APPROACH (RED PHASE): These tests are written FIRST
 * Component implementation will be written to pass these tests (GREEN phase)
 *
 * PERFORMANCE TARGET: 60fps flip animation (<16.67ms per frame)
 */

import { describe, it, expect } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FlashcardCard } from '../FlashcardCard';
import { StudyCard } from '../../../types/study-cards';

describe('FlashcardCard - Flip Animation & Display', () => {
  const mockCard: StudyCard = {
    id: 1,
    card_id: 'CARD-550e8400-e29b-41d4-a716-446655440000-1',
    user_id: 42,
    session_id: '550e8400-e29b-41d4-a716-446655440000',
    question: 'What is the SOCRATES framework for pain assessment?',
    answer:
      'SOCRATES is a mnemonic for systematic pain assessment:\n\n- **S**ite: Where is the pain?\n- **O**nset: When did it start?\n- **C**haracter: What does it feel like?\n- **R**adiation: Does it spread anywhere?\n- **A**ssociations: Any other symptoms?\n- **T**ime course: Pattern over time?\n- **E**xacerbating/relieving factors: What makes it better/worse?\n- **S**everity: How bad is it (0-10)?',
    citations: [
      {
        source: "Talley & O'Connor Clinical Examination 9th Ed",
        qdrant_point_id: '550e8400-e29b-41d4-a716-446655440000',
        confidence: 0.85,
        page: 'p. 412',
      },
    ],
    sm2_params: {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    },
    next_review_date: '2026-03-26T00:00:00Z',
    last_reviewed_at: null,
    specialty: 'general_medicine',
    topic: 'Pain Assessment',
    subtopic: null,
    difficulty: 'easy',
    tags: ['SOCRATES', 'pain assessment', 'clinical skills'],
    card_type: 'history_taking',
    is_active: true,
    created_at: '2026-03-25T00:00:00Z',
    updated_at: '2026-03-25T00:00:00Z',
  };

  // Test 9: Shows question side initially (answer hidden)
  it('should display question side initially with answer hidden', () => {
    render(<FlashcardCard card={mockCard} />);

    expect(screen.getByText(/What is the SOCRATES framework/i)).toBeInTheDocument();
    expect(screen.queryByText(/SOCRATES is a mnemonic/i)).not.toBeInTheDocument();
    expect(screen.queryByTestId('citation-list')).not.toBeInTheDocument();
  });

  // Test 10: "Show Answer" button exists and is accessible
  it('should have accessible "Show Answer" button', () => {
    render(<FlashcardCard card={mockCard} />);

    const showAnswerBtn = screen.getByRole('button', { name: /show answer/i });
    expect(showAnswerBtn).toBeInTheDocument();
    expect(showAnswerBtn).toHaveAttribute('aria-label', 'Show answer');
    expect(showAnswerBtn).toHaveAttribute('aria-pressed', 'false');
  });

  // Test 11: Clicking "Show Answer" flips card (reveals answer)
  it('should flip card to show answer when "Show Answer" is clicked', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    const showAnswerBtn = screen.getByRole('button', { name: /show answer/i });
    await user.click(showAnswerBtn);

    // Wait for flip animation (0.6s)
    await waitFor(
      () => {
        expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeInTheDocument();
        expect(screen.getByTestId('citation-list')).toBeInTheDocument();
      },
      { timeout: 1000 }
    );

    // Verify question is hidden after flip
    expect(screen.queryByText(/What is the SOCRATES framework/i)).not.toBeInTheDocument();
  });

  // Test 12: Spacebar keypress flips card (keyboard shortcut)
  it('should flip card when spacebar is pressed', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    // Press spacebar
    await user.keyboard(' ');

    await waitFor(
      () => {
        expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeInTheDocument();
      },
      { timeout: 1000 }
    );
  });

  // Test 13: Flip animation uses CSS transform (60fps target)
  it('should use CSS transform for flip animation (performance)', () => {
    const { container } = render(<FlashcardCard card={mockCard} />);

    const cardElement = container.querySelector('[data-testid="flashcard-card-inner"]');
    expect(cardElement).toBeInTheDocument();

    // Verify CSS transform is used (GPU-accelerated)
    const computedStyle = window.getComputedStyle(cardElement as Element);
    expect(computedStyle.transition).toContain('transform');
    expect(computedStyle.transformStyle).toBe('preserve-3d');
  });

  // Test 14: Long question text wraps correctly (no overflow)
  it('should wrap long question text without horizontal scroll', () => {
    const longQuestion = 'A'.repeat(500); // 500 characters
    const cardWithLongQ: StudyCard = { ...mockCard, question: longQuestion };

    render(<FlashcardCard card={cardWithLongQ} />);

    const questionElement = screen.getByText(longQuestion);
    const computedStyle = window.getComputedStyle(questionElement);

    expect(computedStyle.overflowWrap).toBe('break-word');
  });

  // Test 15: Long answer text wraps correctly
  it('should wrap long answer text without horizontal scroll', async () => {
    const user = userEvent.setup();
    const longAnswer = 'B'.repeat(1000); // 1000 characters
    const cardWithLongA: StudyCard = { ...mockCard, answer: longAnswer };

    render(<FlashcardCard card={cardWithLongA} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      const answerElement = screen.getByText(longAnswer);
      const computedStyle = window.getComputedStyle(answerElement);

      expect(computedStyle.overflowWrap).toBe('break-word');
    });
  });

  // Test 16: Citations display correctly with qdrant_point_id
  it('should display citations with source, page, and confidence', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      expect(screen.getByText(/Talley & O'Connor/i)).toBeInTheDocument();
      expect(screen.getByText(/p\. 412/i)).toBeInTheDocument();
      expect(screen.getByText(/85%/i)).toBeInTheDocument();
    });
  });

  // Test 17: Card with no citations shows "No citations available"
  it('should display "No citations" message when citations array is empty', async () => {
    const user = userEvent.setup();
    const cardNoCitations: StudyCard = { ...mockCard, citations: [] };

    render(<FlashcardCard card={cardNoCitations} />);

    await user.click(screen.getByRole('button', { name: /show answer/i }));

    await waitFor(() => {
      expect(screen.getByText(/no citations available/i)).toBeInTheDocument();
    });
  });

  // Test 18: Card with special characters (unicode) displays correctly
  it('should display unicode characters correctly (Chinese, emoji, math symbols)', () => {
    const unicodeCard: StudyCard = {
      ...mockCard,
      question: '心脏检查 (Cardiac Examination) 🫀',
      answer: 'α-blocker contraindicated in acute MI ≤48h',
    };

    render(<FlashcardCard card={unicodeCard} />);

    expect(screen.getByText(/心脏检查/)).toBeInTheDocument();
    expect(screen.getByText(/🫀/)).toBeInTheDocument();
  });

  // Test 19 (PERFORMANCE): Flip animation completes within 700ms (60fps target)
  it('should complete flip animation within 700ms (60fps performance)', async () => {
    const user = userEvent.setup();
    render(<FlashcardCard card={mockCard} />);

    const startTime = performance.now();

    // Flip card
    await user.click(screen.getByRole('button', { name: /show answer/i }));

    // Wait for animation to complete
    await waitFor(
      () => {
        expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeInTheDocument();
      },
      { timeout: 1000 }
    );

    const endTime = performance.now();
    const duration = endTime - startTime;

    // Animation should complete within 700ms (600ms animation + 100ms buffer)
    expect(duration).toBeLessThan(700);

    // Verify element is visible after flip
    expect(screen.getByText(/SOCRATES is a mnemonic/i)).toBeVisible();
  });
});
