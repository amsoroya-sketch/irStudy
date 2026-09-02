/**
 * E2E: dashboard + performance analytics (Phase E-1).
 *
 * Runs authenticated (shared storageState) against the live backend. Asserts the
 * pages load their real data (headings / cards / charts) with no error alert.
 *
 * Routes covered:
 *   @route:/dashboard    unified overview renders
 *   @route:/performance  analytics dashboard renders
 */

import { expect } from '@playwright/test';
import { routeTest } from './support/coverage';

routeTest('/dashboard', 'unified dashboard loads with its key sections', async ({ page }) => {
  await page.goto('/dashboard');

  await expect(
    page.getByRole('heading', { name: 'Dashboard', level: 1 })
  ).toBeVisible();
  // Header controls + a known section render from live data.
  await expect(page.getByLabel(/refresh dashboard/i)).toBeVisible();
  await expect(
    page.getByRole('heading', { name: 'HTML OSCE Notes', level: 2 })
  ).toBeVisible();

  // No load failure surfaced.
  await expect(page.getByText(/failed to load/i)).toHaveCount(0);
});

routeTest('/performance', 'performance dashboard renders stat cards and charts', async ({ page }) => {
  await page.goto('/performance');

  await expect(
    page.getByRole('heading', { name: /performance dashboard/i })
  ).toBeVisible();
  // A stat card from the live analytics payload ("MCQ Attempts" also appears as
  // a chart legend, so scope to the first — the StatCard title).
  await expect(page.getByText('MCQ Attempts').first()).toBeVisible();
  // A rendered panel heading.
  await expect(
    page.getByRole('heading', { name: /amc exam readiness/i })
  ).toBeVisible();

  await expect(
    page.getByText(/failed to load dashboard data/i)
  ).toHaveCount(0);
});
