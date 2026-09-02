/**
 * Shared Playwright auth helper (Phase 0 E2E foundations).
 *
 * Factored out of tests/emr-validation.spec.ts so every E2E spec logs in the
 * same way. Credentials come from the environment (never hardcoded secrets);
 * defaults match the seeded dev/test student account.
 */

import type { Page } from '@playwright/test';

export const STUDENT_EMAIL = process.env.E2E_STUDENT_EMAIL || 'student@test.com';
export const STUDENT_PASSWORD = process.env.E2E_STUDENT_PASSWORD || 'Student123!@#';

/** Log in through the UI and wait for the post-login redirect to /dashboard. */
export async function login(
  page: Page,
  email: string = STUDENT_EMAIL,
  password: string = STUDENT_PASSWORD
): Promise<void> {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(email);
  await page.getByLabel(/password/i).fill(password);
  await page.getByRole('button', { name: /sign in|log in|login/i }).click();
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
}
