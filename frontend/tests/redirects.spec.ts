/**
 * E2E: routing redirects + auth guard (Phase E-1).
 *
 * Covers the two fallback routes and the protected-route guard:
 *   @route:/   authenticated visiting "/" -> /dashboard
 *   @route:/*  logged-out unknown / dead links -> /login
 *   plus: logged-out protected route (/mcqs) -> /login (ProtectedRoute guard)
 */

import { test, expect } from '@playwright/test';
import { routeTest } from './support/coverage';

// --- Authenticated (shared storageState) ---
routeTest('/', 'authenticated root redirects to the dashboard', async ({ page }) => {
  await page.goto('/');
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
  await expect(
    page.getByRole('heading', { name: 'Dashboard', level: 1 })
  ).toBeVisible();
});

// --- Logged-out: fallback catch-all + auth guard ---
test.describe('logged-out redirects', () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  routeTest('*', 'unknown paths and dead links redirect to login', async ({ page }) => {
    // Unknown path -> catch-all Navigate to /login.
    await page.goto('/this-route-does-not-exist-xyz');
    await page.waitForURL(/\/login/, { timeout: 15000 });
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();

    // A dead link (no route defined) -> same catch-all -> /login.
    await page.goto('/profile');
    await page.waitForURL(/\/login/, { timeout: 15000 });
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('protected route while logged-out redirects to login', async ({ page }) => {
    await page.goto('/mcqs');
    await page.waitForURL(/\/login/, { timeout: 15000 });
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });
});
