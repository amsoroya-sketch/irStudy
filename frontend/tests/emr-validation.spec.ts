/**
 * E2E: EMR scenario brief + validation results (PRD-EMR-PRACTICE-003)
 *
 * Seeds a challenging cardiology case, documents a deliberately unsafe plan
 * (nitrates in a STEMI / RV-infarct picture), submits, and asserts the results
 * page renders a FAIL. Runs against the seeded stack (dev server + backend).
 */

import { test, expect } from '@playwright/test';

const STUDENT_EMAIL = process.env.E2E_STUDENT_EMAIL || 'student@test.com';
const STUDENT_PASSWORD = process.env.E2E_STUDENT_PASSWORD || 'Student123!@#';

async function login(page: import('@playwright/test').Page) {
  await page.goto('/login');
  await page.getByLabel(/email/i).fill(STUDENT_EMAIL);
  await page.getByLabel(/password/i).fill(STUDENT_PASSWORD);
  await page.getByRole('button', { name: /sign in|log in|login/i }).click();
  await page.waitForURL(/\/dashboard/, { timeout: 15000 });
}

test('E2E: nitrates-in-STEMI submission -> results page shows FAIL', async ({ page }) => {
  await login(page);

  // Start a new EMR session
  await page.goto('/emr/start');
  await page.getByRole('button', { name: /start new emr session/i }).click();

  // Choose Epic if the system-select screen appears
  const epicHeading = page.getByRole('heading', { name: /epic/i });
  if (await epicHeading.isVisible().catch(() => false)) {
    await epicHeading.click();
  }

  // Scenario brief + task must be visible before documenting
  await expect(page.getByText(/your task/i)).toBeVisible();

  // Document a deliberately failing plan (gives nitrates)
  const planTab = page.getByRole('tab', { name: /plan/i });
  if (await planTab.isVisible().catch(() => false)) {
    await planTab.click();
  }
  await page
    .getByRole('textbox')
    .first()
    .fill('Give GTN nitrates. Aspirin. Troponin.');

  await page.getByRole('button', { name: /submit for review|submit/i }).click();

  // Results page
  await expect(page).toHaveURL(/\/emr\/validation\//, { timeout: 20000 });
  await expect(page.getByText(/fail/i)).toBeVisible();
});
