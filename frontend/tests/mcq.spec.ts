/**
 * E2E: MCQ practice journey (Phase E-1).
 *
 * Runs authenticated against the live backend (1675 seeded MCQs). Browses the
 * list, opens a REAL MCQ (id derived by clicking through the UI — never
 * hardcoded), answers it and asserts immediate feedback + explanation.
 *
 * Routes covered:
 *   @route:/mcqs               browse list
 *   @route:/mcqs/:id/attempt   attempt + feedback
 */

import { expect } from '@playwright/test';
import { routeTest } from './support/coverage';

routeTest('/mcqs', 'browse the seeded MCQ list', async ({ page }) => {
  await page.goto('/mcqs');

  await expect(
    page.getByRole('heading', { name: /mcq practice browser/i })
  ).toBeVisible();

  // At least one real MCQ card with an Attempt action renders.
  await expect(page.getByRole('button', { name: 'Attempt' }).first()).toBeVisible();
});

routeTest('/mcqs/:id/attempt', 'open a real MCQ, answer it and see feedback', async ({ page }) => {
  await page.goto('/mcqs');

  const firstAttempt = page.getByRole('button', { name: 'Attempt' }).first();
  await expect(firstAttempt).toBeVisible();
  await firstAttempt.click();

  // Real id is derived from the UI navigation, not hardcoded.
  await page.waitForURL(/\/mcqs\/\d+\/attempt/, { timeout: 15000 });

  // Question stem + answer options render.
  await expect(
    page.getByRole('heading', { name: /^MCQ #\d+/ })
  ).toBeVisible();
  const options = page.getByRole('radio');
  await expect(options.first()).toBeVisible();

  // Select the first option and submit.
  await options.first().check();
  await page.getByRole('button', { name: /submit answer/i }).click();

  // Immediate feedback (correct or incorrect) + the explanation panel.
  await expect(page.getByText(/correct!|incorrect\./i).first()).toBeVisible();
  await expect(page.getByText(/explanation:/i)).toBeVisible();
});
