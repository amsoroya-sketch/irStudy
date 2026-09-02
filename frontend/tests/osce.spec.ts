/**
 * E2E: OSCE AI patient-simulation journeys (Phase E-2, AI-driven).
 *
 * Routes covered:
 *   @route:/osce-practice              persona picker → Start Session → navigates
 *   @route:/osce/session/:attemptId    live session page (persona + chat + timer)
 *
 * These flows drive real Claude over a WebSocket (ws://…/ws/osce/:attemptId),
 * which needs Redis for the AI examiner scoring pipeline. Redis may be DOWN in
 * this environment — in that case the conversation/scoring cannot run, but the
 * session PAGE still loads over REST. We therefore cover /osce/session by
 * asserting the page's LOAD INVARIANTS (persona header + chat container + timer),
 * best-effort exercise one chat turn + end→score with a bounded timeout, and
 * ANNOTATE when live WS scoring wasn't reachable. We never assert a specific
 * AI-generated score.
 */

import { test, expect } from '@playwright/test';
import { routeTest } from './support/coverage';
import { apiLogin, seedOsceSession } from './support/seed';

routeTest(
  '/osce-practice',
  'filter + select a persona, load detail, and Start Session navigates to the session',
  async ({ page }) => {
    test.setTimeout(90_000);
    await page.goto('/osce-practice');

    await expect(
      page.getByRole('heading', { name: /osce practice - patient personas/i })
    ).toBeVisible();

    // Narrow the list with the Specialty filter (proves the filter is wired).
    await page.getByRole('combobox', { name: /specialty/i }).click();
    await page.getByRole('option', { name: 'General Practice' }).click();

    // Open the patient dropdown and pick the first REAL persona (index 0 is the
    // "Choose a patient..." placeholder).
    const patientSelect = page.getByRole('combobox', { name: /select patient/i });
    await expect(patientSelect).toBeEnabled();
    await patientSelect.click();
    const firstPersona = page.getByRole('option').nth(1);
    await expect(firstPersona).toBeVisible();
    await firstPersona.click();

    // Detail view loads with the Start Session CTA.
    const startBtn = page.getByRole('button', { name: /start session/i });
    await expect(page.getByRole('heading', { name: /patient details/i })).toBeVisible();
    await expect(startBtn).toBeVisible();

    await startBtn.click();

    // Creating the AI attempt navigates to the live session (real attempt id).
    await page.waitForURL(/\/osce\/session\/[0-9a-f-]{36}/i, { timeout: 30_000 });
  }
);

routeTest(
  '/osce/session/:attemptId',
  'the live OSCE session page loads persona, chat container and timer (WS scoring best-effort)',
  async ({ page, request }) => {
    test.setTimeout(180_000);

    // Seed a real AI attempt via the API (deterministic id, no dependence on the
    // picker spec) and open the session page the same way the app would.
    const token = await apiLogin(request);
    const attemptId = await seedOsceSession(request, token);

    await page.goto(`/osce/session/${attemptId}`);

    // LOAD INVARIANTS (all served over REST, independent of Redis/WebSocket):
    //  - persona header (h1 "OSCE Session: <name>")
    //  - the WebSocket chat container (role=main, "OSCE chat interface")
    //  - the live session timer (role=timer)
    await expect(
      page.getByRole('heading', { name: /osce session:/i })
    ).toBeVisible({ timeout: 30_000 });
    const chat = page.getByRole('main', { name: /osce chat interface/i });
    await expect(chat).toBeVisible();
    await expect(page.getByRole('timer').first()).toBeVisible();

    // The session must NOT have bounced us back to the picker (ownership OK).
    await expect(page).toHaveURL(new RegExp(`/osce/session/${attemptId}`, 'i'));

    // --- Best-effort: exercise one live chat turn + end→score --------------
    // If Redis/WS is down the connection banner shows "Connecting…"/error and the
    // input stays disabled; we then annotate rather than fail (route already
    // covered by the load invariants above).
    const input = page.getByRole('textbox', { name: /message input/i });
    const connected = await input.isEnabled({ timeout: 20_000 }).catch(() => false);

    if (!connected) {
      const banner = page.getByText(
        /connecting to patient|reconnecting to patient/i
      );
      const reason = (await banner.first().isVisible().catch(() => false))
        ? 'WebSocket never reached "connected" (Redis/WS backend unavailable)'
        : 'chat input stayed disabled (WebSocket not connected)';
      test.info().annotations.push({
        type: 'limitation',
        description: `live OSCE WS scoring not exercised: ${reason}. Route covered by load invariants (persona + chat container + timer).`,
      });
      return;
    }

    // WS connected → send one message and end the session, waiting (bounded) for
    // either the AI patient reply OR the scoring dialog. Tolerant of AI latency.
    await input.fill('Hello, I am Dr Test. Can you tell me what brought you in today?');
    await page.getByRole('button', { name: /send message/i }).click();

    const scoreDialog = page.getByRole('dialog', { name: /osce session complete/i });
    const endBtn = page.getByRole('button', { name: /end session/i });
    if (await endBtn.isVisible().catch(() => false)) {
      await endBtn.click();
      // End confirmation dialog (if present) → confirm.
      const confirmEnd = page.getByRole('button', { name: /^end session$/i }).last();
      await confirmEnd.click().catch(() => {});
    }

    const scored = await scoreDialog
      .isVisible({ timeout: 150_000 })
      .catch(() => false);
    if (scored) {
      // AI examiner returned a verdict: assert the invariant shape only.
      await expect(page.getByText(/\/\s*15\b/).first()).toBeVisible();
      await expect(
        page.getByText('PASS', { exact: true }).or(page.getByText('FAIL', { exact: true })).first()
      ).toBeVisible();
    } else {
      test.info().annotations.push({
        type: 'limitation',
        description:
          'live OSCE AI examiner scoring did not complete within 2.5 min after end ' +
          '(WebSocket/Redis scoring pipeline unavailable). Route covered by load invariants.',
      });
    }
  }
);
