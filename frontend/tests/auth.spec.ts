/**
 * E2E: authentication journeys (Phase E-1).
 *
 * Drives the real login/register UI against the live backend + seeded student.
 * Opts out of the shared storageState so every test starts logged-out.
 *
 * Routes covered:
 *   @route:/login     valid login -> /dashboard, invalid creds -> error
 *   @route:/register  client-side validation + successful submit path
 */

import { expect } from '@playwright/test';
import { routeTest } from './support/coverage';
import { STUDENT_EMAIL, STUDENT_PASSWORD } from './support/auth';

// These specs exercise the auth UI, so start from a clean, logged-out state.
import { test } from '@playwright/test';
test.use({ storageState: { cookies: [], origins: [] } });

routeTest('/login', 'valid credentials log in and land on the dashboard', async ({ page }) => {
  await page.goto('/login');

  await page.getByLabel(/email address/i).fill(STUDENT_EMAIL);
  await page.getByLabel(/^password/i).fill(STUDENT_PASSWORD);
  await page.getByRole('button', { name: /sign in/i }).click();

  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
  await expect(
    page.getByRole('heading', { name: 'Dashboard', level: 1 })
  ).toBeVisible();
});

routeTest('/login', 'invalid credentials surface an error and stay on /login', async ({ page }) => {
  await page.goto('/login');

  // Valid password FORMAT (passes client-side complexity so submit is enabled)
  // but wrong credentials -> the backend returns 401.
  await page.getByLabel(/email address/i).fill(STUDENT_EMAIL);
  await page.getByLabel(/^password/i).fill('WrongPass123!@#');
  await page.getByRole('button', { name: /sign in/i }).click();

  // Backend returns 401 "Incorrect email or password" -> surfaced in an Alert.
  await expect(page.getByText(/incorrect email or password/i)).toBeVisible();
  await expect(page).toHaveURL(/\/login/);
});

routeTest('/register', 'validates inputs then submits a new account', async ({ page }) => {
  await page.goto('/register');

  // Page renders the account fields.
  await expect(
    page.getByRole('heading', { name: /create account/i })
  ).toBeVisible();

  // Client-side validation: a weak password is flagged on blur.
  await page.getByLabel(/^password/i).fill('short');
  await page.getByLabel(/full name/i).click(); // blur the password field
  await expect(page.getByText(/at least 12 characters/i)).toBeVisible();

  // Fill a valid, unique account and submit the real registration path.
  const uniqueEmail = `e2e_${Date.now()}@test.com`;
  const strongPassword = 'TestPass123!@#';

  await page.getByLabel(/full name/i).fill('E2E Test Student');
  await page.getByLabel(/email address/i).fill(uniqueEmail);
  await page.getByLabel(/^password/i).fill(strongPassword);
  await page.getByLabel(/confirm password/i).fill(strongPassword);
  await page.getByRole('checkbox', { name: /accept the terms/i }).check();

  const submit = page.getByRole('button', { name: /create account/i });
  await expect(submit).toBeEnabled();
  await submit.click();

  await expect(page.getByText(/registration successful/i)).toBeVisible();
});
