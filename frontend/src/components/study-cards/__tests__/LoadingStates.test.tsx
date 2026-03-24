/**
 * LoadingStates Component Tests
 * PRD-P1-006 Phase 4: Loading and Skeleton States
 *
 * Tests 28-29 from COMPREHENSIVE-TESTING-PLAN-STUDY-CARDS.md
 *
 * TDD Workflow: RED Phase
 * - Test 28: Display skeleton loader with card shape
 * - Test 29: Display multiple skeleton items when count prop is provided
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { FlashcardSkeleton } from '../LoadingStates';

describe('LoadingStates', () => {
  it('Test 28: should display skeleton loader with card shape', () => {
    render(<FlashcardSkeleton />);

    // Verify skeleton elements are visible
    const skeleton = screen.getByTestId('flashcard-skeleton');
    expect(skeleton).toBeInTheDocument();

    // Verify skeleton has proper dimensions (similar to real flashcard)
    expect(skeleton).toHaveStyle({ minHeight: '400px' });
  });

  it('Test 29: should display multiple skeleton items when count prop is provided', () => {
    render(<FlashcardSkeleton count={3} />);

    // Verify 3 skeleton items are rendered
    const skeletons = screen.getAllByTestId('flashcard-skeleton-item');
    expect(skeletons).toHaveLength(3);
  });
});
