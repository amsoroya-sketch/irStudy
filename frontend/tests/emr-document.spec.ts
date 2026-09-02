/**
 * E2E: EMR clinical documentation journeys (Phase E-1).
 *
 * Runs authenticated against the live backend + seeded EMR cases. Exercises the
 * full "pick a case -> choose a system -> document" flow across BOTH Epic and
 * Cerner. Sessions for the direct-render tests are seeded via the API so they
 * don't depend on ambient navigation state. Does NOT submit (grading = E-2).
 *
 * Routes covered:
 *   @route:/emr/cases              case picker -> starts a session
 *   @route:/emr/start              quick-start -> system selector
 *   @route:/emr/select/:sessionId  pick Epic/Cerner
 *   @route:/emr/epic/:sessionId    document SOAP + prescription (Epic)
 *   @route:/emr/cerner/:sessionId  document SOAP + prescription (Cerner)
 */

import { expect, type Page } from '@playwright/test';
import { routeTest } from './support/coverage';
import { apiLogin, seedEmrSession } from './support/seed';

/** Document a SOAP section + add a prescription, then assert auto-save fired. */
async function documentAndAssertAutoSave(page: Page): Promise<void> {
  // Scenario brief must be visible before documenting.
  await expect(
    page.getByRole('heading', { name: 'Clinical Scenario' })
  ).toBeVisible();

  // Type into the Subjective SOAP section (the default active tab).
  const subjective = page.getByRole('textbox', { name: 'Subjective section' });
  await expect(subjective).toBeVisible();
  await subjective.fill(
    'HPI: Central chest pain, 2 hours, radiating to left arm. Nausea, diaphoresis.'
  );

  // Switch to Orders and add a prescription.
  await page.getByRole('button', { name: /^Orders:/ }).click();
  await page.getByRole('button', { name: /add new prescription/i }).click();

  await page.getByRole('combobox', { name: 'Medication' }).click();
  await page.getByRole('option', { name: 'Aspirin 100mg tablets' }).click();
  // Field labels carry a required asterisk, so match by role + regex.
  await page.getByRole('textbox', { name: /dose/i }).fill('300 mg');
  await page.getByRole('combobox', { name: 'Frequency' }).click();
  await page.getByRole('option', { name: 'Once daily' }).click();
  await page.getByRole('button', { name: 'Add', exact: true }).click();

  // Prescription lands in the list.
  await expect(page.getByText('Aspirin 100mg tablets')).toBeVisible();

  // Auto-save (5s debounce) fires -> the status indicator updates.
  await expect(
    page.getByText(/saving\.\.\.|all changes saved/i)
  ).toBeVisible({ timeout: 15000 });
}

routeTest('/emr/cases', 'pick a case and start a session', async ({ page }) => {
  await page.goto('/emr/cases');

  await expect(
    page.getByRole('heading', { name: /pick an emr case/i })
  ).toBeVisible();

  const firstCase = page.getByRole('button', { name: /^Practise case:/ }).first();
  await expect(firstCase).toBeVisible();
  await firstCase.click();

  // No saved system preference -> lands on the system selector.
  await page.waitForURL(/\/emr\/select\//, { timeout: 20000 });
  await expect(
    page.getByRole('heading', { name: /select emr system/i })
  ).toBeVisible();
});

routeTest('/emr/start', 'quick-start routes to the system selector', async ({ page }) => {
  await page.goto('/emr/start');

  await page.getByRole('button', { name: /start new emr session/i }).click();

  await page.waitForURL(/\/emr\/select\//, { timeout: 20000 });
  await expect(
    page.getByRole('heading', { name: /select emr system/i })
  ).toBeVisible();
});

routeTest('/emr/select/:sessionId', 'choose Epic from the system selector', async ({ page, request }) => {
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });

  await page.goto(`/emr/select/${sessionId}`);

  await expect(page.getByRole('heading', { level: 2, name: 'Epic' })).toBeVisible();
  await expect(page.getByRole('heading', { level: 2, name: 'Cerner' })).toBeVisible();

  await page.getByRole('heading', { level: 2, name: 'Epic' }).click();
  await page.waitForURL(new RegExp(`/emr/epic/${sessionId}`), { timeout: 15000 });
});

routeTest('/emr/epic/:sessionId', 'document a case in the Epic EMR', async ({ page, request }) => {
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });

  await page.goto(`/emr/epic/${sessionId}`);
  await expect(page.getByRole('heading', { name: 'Epic EMR' })).toBeVisible();
  await documentAndAssertAutoSave(page);
});

routeTest('/emr/cerner/:sessionId', 'document a case in the Cerner EMR', async ({ page, request }) => {
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });

  await page.goto(`/emr/cerner/${sessionId}`);
  await expect(page.getByRole('heading', { name: 'Cerner PowerChart' })).toBeVisible();
  await documentAndAssertAutoSave(page);
});
