/**
 * E2E: spaced-repetition study cards (Phase E-1).
 *
 * Runs authenticated against the live backend (389 cards due for the seeded
 * student). Reveals an answer, rates it, and asserts the deck advances — or the
 * honest terminal/empty state if nothing is due.
 *
 * Route covered:
 *   @route:/study-cards
 */

import { expect } from '@playwright/test';
import { routeTest } from './support/coverage';

routeTest('/study-cards', 'reveal a due card, rate it, and advance', async ({ page }) => {
  await page.goto('/study-cards');

  const showAnswer = page.getByRole('button', { name: /show answer/i });
  const emptyState = page.getByText(/no cards due for review/i);

  // Either a card is due or we get the honest empty state.
  await expect(showAnswer.or(emptyState).first()).toBeVisible();

  if (await emptyState.isVisible().catch(() => false)) {
    // Terminal state is a valid outcome — nothing left to review.
    return;
  }

  // Progress starts at card 1.
  await expect(page.getByText(/card 1 of/i)).toBeVisible();

  await showAnswer.click();
  await expect(page.getByRole('heading', { name: 'Answer' })).toBeVisible();

  // Rate "Good" -> deck advances to the next card (or terminal state).
  await page.getByRole('button', { name: /good/i }).click();

  await expect(
    page.getByText(/card 2 of/i).or(page.getByText(/all cards reviewed/i))
  ).toBeVisible();
});
