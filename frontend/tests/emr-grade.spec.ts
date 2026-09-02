/**
 * E2E: EMR clinical documentation GRADING (Phase E-2, AI-driven).
 *
 * Route covered:
 *   @route:/emr/validation/:sessionId  → the AI-graded results page
 *
 * The grading pipeline runs REAL Claude (POST /emr/sessions/:id/submit is
 * synchronous, ~6-25s). We therefore assert an INVARIANT: the results page
 * reaches ONE terminal state — either
 *   (a) a PASS/FAIL chip with an overall score in 0..15, OR
 *   (b) the "AI assessment is temporarily unavailable" notice (+ "Return to
 *       documentation"), i.e. the AI layer was down and the attempt is ungraded.
 * We never assert a specific score / verdict from the model.
 *
 * IMPORTANT (real bug, see notes): the Epic/Cerner "Submit for review" button
 * posts `{ session_data: ... }`, but the backend `SubmitSessionRequest` requires
 * `final_soap_note` (or `soap_note`) at the top level → the UI submit 422s and
 * NEVER navigates to /emr/validation. To exercise the *validation page* against
 * a genuinely graded session we submit via the API (correct contract) and then
 * load the page the same way a working submit would. This seeds real backend
 * state; it does not fake any assertion.
 */

import { test, expect, type Page } from '@playwright/test';
import { routeTest } from './support/coverage';
import { apiLogin, seedEmrSession, submitEmrSession } from './support/seed';

// The submit endpoint runs Claude synchronously (~6-25s) and the dev backend
// serialises those calls, so run this file's grading journeys one at a time to
// avoid a parallel validation GET queuing behind an in-flight AI submit.
test.describe.configure({ mode: 'serial' });

/** A deliberately UNSAFE plan: nitrates in an inferior STEMI / RV-infarct. */
const UNSAFE_STEMI_NOTE = {
  subjective:
    'Central crushing chest pain for two hours radiating to the left arm, ' +
    'associated with nausea and diaphoresis, worse on exertion.',
  objective:
    'BP 88/60, HR 52, inferior ST elevation (II, III, aVF) on ECG with ' +
    'hypotension suggesting right-ventricular involvement. Chest clear.',
  assessment:
    'Acute inferior ST-elevation myocardial infarction with probable right ' +
    'ventricular infarction.',
  plan:
    'Give GTN (nitrates) sublingual now. Aspirin 300mg. Order troponin and ' +
    'repeat ECG.',
};

/** A safer, well-structured note (no nitrates in RV infarct). */
const SAFE_NOTE = {
  subjective:
    'Central chest pain 2 hours, radiating to left arm, with nausea and ' +
    'diaphoresis. No syncope. Risk factors: smoker, hypertension.',
  objective:
    'BP 138/86, HR 78, SpO2 97% RA. Inferior ST elevation on ECG. ' +
    'Cardiovascular and respiratory exam otherwise unremarkable.',
  assessment:
    'Acute inferior STEMI. Rule out right ventricular involvement before ' +
    'any preload-reducing therapy.',
  plan:
    'Aspirin 300mg, dual antiplatelet, urgent PCI referral, IV fluids if ' +
    'RV infarct, continuous cardiac monitoring, analgesia. Avoid nitrates ' +
    'until RV infarct excluded.',
};

/**
 * Poll the validation page until it settles on a terminal state, tolerant of
 * which one. Returns the outcome for optional annotation.
 */
async function awaitTerminalValidation(page: Page): Promise<'graded' | 'ai_unavailable'> {
  const passChip = page.getByText('PASS', { exact: true });
  const failChip = page.getByText('FAIL', { exact: true });
  const score = page.getByText(/\b\d+(?:\.\d+)?\s*\/\s*15\b/);
  const aiDown = page.getByText(/AI assessment is temporarily unavailable/i);

  // The status banner (if still grading) resolves within this window; the AI
  // submit itself is synchronous so a terminal state is normally immediate.
  let outcome: 'graded' | 'ai_unavailable' | null = null;
  await expect
    .poll(
      async () => {
        if (await aiDown.isVisible().catch(() => false)) {
          outcome = 'ai_unavailable';
          return true;
        }
        const graded =
          (await passChip.isVisible().catch(() => false)) ||
          (await failChip.isVisible().catch(() => false));
        if (graded && (await score.first().isVisible().catch(() => false))) {
          outcome = 'graded';
          return true;
        }
        return false;
      },
      { timeout: 120_000, intervals: [1000, 2000, 3000] }
    )
    .toBe(true);

  if (outcome === 'graded') {
    // Overall score must be a real number within the 0..15 AMC rubric.
    const scoreText = (await score.first().innerText()).trim();
    const value = parseFloat(scoreText.split('/')[0]);
    expect(Number.isFinite(value)).toBe(true);
    expect(value).toBeGreaterThanOrEqual(0);
    expect(value).toBeLessThanOrEqual(15);
  } else {
    // ai_unavailable is a genuine terminal state: the re-submit CTA must render
    // and NO PASS/FAIL verdict may be shown (never a fake 0/15 fail).
    await expect(
      page.getByRole('button', { name: /return to documentation/i })
    ).toBeVisible();
    await expect(page.getByText('PASS', { exact: true })).toHaveCount(0);
    await expect(page.getByText('FAIL', { exact: true })).toHaveCount(0);
  }
  return outcome!;
}

routeTest(
  '/emr/validation/:sessionId',
  'unsafe STEMI note is graded live and the results page reaches a terminal state',
  async ({ page, request }) => {
    test.setTimeout(180_000);
    const token = await apiLogin(request);
    const sessionId = await seedEmrSession(request, { token });

    // Submit the unsafe (nitrates-in-STEMI) documentation via the API contract
    // the backend actually accepts, then open the results page.
    await submitEmrSession(request, token, sessionId, UNSAFE_STEMI_NOTE);
    await page.goto(`/emr/validation/${sessionId}`);

    // Page shell is always present regardless of AI outcome.
    await expect(
      page.getByRole('heading', { name: /emr validation results/i })
    ).toBeVisible({ timeout: 60_000 });

    const outcome = await awaitTerminalValidation(page);
    if (outcome === 'ai_unavailable') {
      test.info().annotations.push({
        type: 'limitation',
        description:
          'live Claude EMR grading returned ai_unavailable — PASS/FAIL verdict + ' +
          'AMC rubric were not exercised (AI layer unavailable in this environment).',
      });
    }
  }
);

routeTest(
  '/emr/validation/:sessionId',
  'a safe well-structured note is graded live to a terminal state (PASS-or-graded, tolerant)',
  async ({ page, request }) => {
    test.setTimeout(180_000);
    const token = await apiLogin(request);
    const sessionId = await seedEmrSession(request, { token });

    await submitEmrSession(request, token, sessionId, SAFE_NOTE);
    await page.goto(`/emr/validation/${sessionId}`);

    await expect(
      page.getByRole('heading', { name: /emr validation results/i })
    ).toBeVisible({ timeout: 60_000 });

    const outcome = await awaitTerminalValidation(page);
    if (outcome === 'ai_unavailable') {
      test.info().annotations.push({
        type: 'limitation',
        description:
          'live Claude EMR grading returned ai_unavailable for the safe note — ' +
          'a positive PASS verdict was not exercised (AI layer unavailable).',
      });
    }
  }
);
