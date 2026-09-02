/**
 * E2E: HTML OSCE notes browser + viewer (Phase E-1).
 *
 * Runs authenticated against the live backend. Lists notes, opens one and
 * asserts the sandboxed iframe viewer dialog appears.
 *
 * Route covered:
 *   @route:/html-notes
 */

import { expect } from '@playwright/test';
import { routeTest } from './support/coverage';

routeTest('/html-notes', 'list notes and open the iframe viewer', async ({ page }) => {
  await page.goto('/html-notes');

  await expect(
    page.getByRole('heading', { name: 'HTML OSCE Notes', level: 1 })
  ).toBeVisible();

  // First real note card (title rendered as a level-2 heading inside the card).
  const firstNote = page.getByRole('heading', { level: 2 }).first();
  await expect(firstNote).toBeVisible();
  await firstNote.click();

  // Viewer dialog with the sandboxed iframe.
  const dialog = page.getByRole('dialog');
  await expect(dialog).toBeVisible();
  await expect(dialog.locator('iframe')).toBeVisible();
});
