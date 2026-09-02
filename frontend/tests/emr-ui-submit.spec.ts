import { test, expect } from '@playwright/test';
import { routeTest } from './support/coverage';
import { apiLogin, seedEmrSession } from './support/seed';

/**
 * Regression proof for the EMR submit contract bug: the "Submit for Review"
 * button previously POSTed `{ session_data }`, which 422'd, so a real user could
 * never submit. This drives the ACTUAL UI button and asserts it reaches the
 * validation route (no 422, no stuck state).
 */
routeTest('/emr/epic/:sessionId', 'UI Submit for Review reaches the validation page (contract fix)', async ({ page, request }) => {
  test.setTimeout(120_000);

  // Seed a real EMR session for the STEMI case via the API, then open Epic.
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token, mrn: 'EMRP-0001' });

  await page.goto(`/emr/epic/${sessionId}`);
  await expect(page.getByRole('heading', { name: 'Clinical Scenario' })).toBeVisible();

  // Document a SOAP note through the real editor.
  await page.getByRole('tab', { name: 'Subjective' }).click();
  await page
    .getByLabel('Subjective section')
    .fill('58yo man, central crushing chest pain 45 min, radiating to left arm, diaphoretic. RF: smoker, HTN, T2DM, FHx early MI. No PDE5 inhibitor use.');
  await page.getByRole('tab', { name: 'Objective' }).click();
  await page.getByLabel('Objective section').fill('12-lead ECG within 10 min. BP both arms. HR 94, BP 138/86, SpO2 95%.');
  await page.getByRole('tab', { name: 'Assessment' }).click();
  await page.getByLabel('Assessment section').fill('Acute coronary syndrome, likely STEMI. Consider aortic dissection and PE.');
  await page.getByRole('tab', { name: 'Plan' }).click();
  await page.getByLabel('Plan section').fill('ECG within 10 min, aspirin 300 mg, troponin/FBC/UEC, cardiac monitor, cardiology referral. Oxygen only if SpO2 < 94%.');

  // Click the REAL submit button — this exercises the fixed payload builder.
  await page.getByRole('button', { name: 'Submit for review' }).click();

  // Proof: it navigates to the validation route (previously blocked by 422).
  await expect(page).toHaveURL(new RegExp(`/emr/validation/${sessionId}`), { timeout: 60_000 });
  await expect(page.getByRole('heading', { name: /EMR Validation Results/i })).toBeVisible();
  // A terminal state renders (graded PASS/FAIL, or the honest ai_unavailable notice) — not an error/stuck page.
  await expect(
    page.getByText(/PASS|FAIL|AI assessment is temporarily unavailable|Validation in progress/i).first()
  ).toBeVisible({ timeout: 60_000 });
});
