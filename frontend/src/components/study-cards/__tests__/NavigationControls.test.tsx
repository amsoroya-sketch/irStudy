/**
 * NavigationControls Component Tests
 * Based on PRD-P1-006 Phase 3 - Navigation Controls
 *
 * Tests 20-24: Navigation button behavior
 *
 * TDD PHASE: RED (Tests written FIRST, expected to FAIL)
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NavigationControls } from '../NavigationControls';

describe('NavigationControls', () => {
  it('Test 20: should show current card number and total count', () => {
    render(
      <NavigationControls
        currentIndex={0}
        totalCards={5}
        onNext={vi.fn()}
        onPrevious={vi.fn()}
      />
    );

    expect(screen.getByText('Card 1 of 5')).toBeInTheDocument();
  });

  it('Test 21: should disable Previous button on first card', () => {
    render(
      <NavigationControls
        currentIndex={0}
        totalCards={5}
        onNext={vi.fn()}
        onPrevious={vi.fn()}
      />
    );

    const prevButton = screen.getByRole('button', { name: /previous/i });
    expect(prevButton).toBeDisabled();
  });

  it('Test 22: should disable Next button on last card', () => {
    render(
      <NavigationControls
        currentIndex={4}
        totalCards={5}
        onNext={vi.fn()}
        onPrevious={vi.fn()}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).toBeDisabled();
  });

  it('Test 23: should call onNext when Next button is clicked', async () => {
    const onNext = vi.fn();
    const user = userEvent.setup();

    render(
      <NavigationControls
        currentIndex={0}
        totalCards={5}
        onNext={onNext}
        onPrevious={vi.fn()}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    expect(onNext).toHaveBeenCalledOnce();
  });

  it('Test 24: should call onPrevious when Previous button is clicked', async () => {
    const onPrevious = vi.fn();
    const user = userEvent.setup();

    render(
      <NavigationControls
        currentIndex={1}
        totalCards={5}
        onNext={vi.fn()}
        onPrevious={onPrevious}
      />
    );

    const prevButton = screen.getByRole('button', { name: /previous/i });
    await user.click(prevButton);

    expect(onPrevious).toHaveBeenCalledOnce();
  });
});
