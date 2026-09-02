/**
 * E2E: VISUAL regression baselines (Phase E-3).
 *
 * One `toHaveScreenshot` per stable app page, captured in a representative,
 * SETTLED state across BOTH viewport projects (desktop 1280×800, mobile 390×844
 * — see playwright.config.ts). Baselines land under
 * `tests/__screenshots__/visual.spec.ts/<arg>-<projectName>.png` (committed).
 *
 * The route-coverage gate (tests/verify-route-coverage.mjs) is already satisfied
 * by the journey specs, so these are plain `test(...)` (not `routeTest`). They
 * add PIXEL coverage on top of the behavioural coverage.
 *
 * STABILITY (avoid flaky baselines):
 *   - `animations: 'disabled'` on every shot; toHaveScreenshot also waits for two
 *     consecutive identical frames before comparing.
 *   - Volatile UI is masked (dates/timestamps, broken MCQ images, AI scores).
 *   - Data pages rely on the seeded `irstudy_e2e` fixtures (stable ordering).
 *   - The AI-graded EMR validation page reuses a SINGLE persisted, pre-graded
 *     session per project (cached in tests/.fixtures) so the persisted result is
 *     byte-identical across the update run and the two verify re-runs.
 *
 * KNOWN RESPONSIVE BUG (do NOT baseline the broken state): at 390px the Epic and
 * Cerner EMR editors and the MCQ attempt page have a sidebar/bottom-nav overlap.
 * Those three are captured DESKTOP-ONLY and annotated as skipped on mobile.
 */

import { test, expect, type Page, type Locator } from '@playwright/test';
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { apiLogin, seedEmrSession, submitEmrSession } from './support/seed';

const __dirname = dirname(fileURLToPath(import.meta.url));

/** A fixed, seeded MCQ id (exists in irstudy_e2e) → a deterministic attempt view. */
const FIXED_MCQ_ID = 686;

/** Reason attached to the mobile skips of the confirmed responsive-bug pages. */
const RESPONSIVE_BUG =
  'Tracked responsive bug: at 390px the sidebar/bottom-nav overlaps the content ' +
  '(Epic/Cerner EMR editors + MCQ attempt). Not baselining the broken mobile layout.';

/** Take a full-page, animation-free screenshot with optional masks. */
async function shoot(
  page: Page,
  name: string,
  opts: { mask?: Locator[]; fullPage?: boolean } = {}
): Promise<void> {
  await expect(page).toHaveScreenshot(`${name}.png`, {
    animations: 'disabled',
    fullPage: opts.fullPage ?? true,
    mask: opts.mask ?? [],
  });
}

// ---------------------------------------------------------------------------
// Public (logged-out) pages — opt out of the shared storageState.
// ---------------------------------------------------------------------------
test.describe('public pages', () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test('login', async ({ page }) => {
    await page.goto('/login');
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
    await shoot(page, 'login');
  });

  test('register', async ({ page }) => {
    await page.goto('/register');
    await expect(page.getByRole('heading', { name: /create account/i })).toBeVisible();
    await shoot(page, 'register');
  });
});

// ---------------------------------------------------------------------------
// Authenticated pages (shared storageState from global-setup).
// ---------------------------------------------------------------------------
test('dashboard', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page.getByRole('heading', { name: 'Dashboard', level: 1 })).toBeVisible();
  // Wait for the live sections to hydrate (skeletons -> data) before shooting.
  await expect(
    page.getByRole('heading', { name: 'HTML OSCE Notes', level: 2 })
  ).toBeVisible();
  await expect(page.getByText('Total Sessions')).toBeVisible();
  await expect(page.getByText(/failed to load/i)).toHaveCount(0);
  await page.waitForLoadState('networkidle');

  // The /dashboard aggregates (Overall Progress %, Total Sessions/Avg Score/Total
  // Time, per-module counts, Specialty Breakdown, Recent Activity, personalised
  // Recommendations) are LIVE cumulative stats for the seeded student. The EMR
  // seed helpers used by the other visual/journey specs — and each re-run —
  // mutate them, so they are not byte-stable. We therefore:
  //   1) capture the dashboard VIEWPORT-ONLY (fixed image size, so the variable-
  //      height Recommendations panel at the bottom can't change the dimensions);
  //   2) mask the live-data sections (`main > div` children: Overall Progress,
  //      Module Stats, the chart+activity Grid, Recommendations) while keeping the
  //      stable header + "HTML OSCE Notes" promo card as the pixel baseline.
  const main = page.locator('main > div');
  await shoot(page, 'dashboard', {
    fullPage: false,
    mask: [main.nth(1), main.nth(2), main.nth(4), main.nth(5)],
  });
});

test('performance', async ({ page }) => {
  await page.goto('/performance');
  await expect(
    page.getByRole('heading', { name: /performance dashboard/i })
  ).toBeVisible();
  await expect(
    page.getByRole('heading', { name: /amc exam readiness/i })
  ).toBeVisible();
  await expect(page.getByText(/failed to load dashboard data/i)).toHaveCount(0);
  // Recharts uses react-smooth (rAF/JS) entry animation that `animations:'disabled'`
  // cannot freeze and that never fully settles for pixel comparison, so mask the
  // chart surfaces. The rest of the page (headings, stat cards, readiness gauge,
  // panel text) is still baselined from the stable seeded analytics.
  await shoot(page, 'performance', {
    mask: [page.locator('.recharts-responsive-container')],
  });
});

test('mcqs browser', async ({ page }) => {
  await page.goto('/mcqs');
  await expect(
    page.getByRole('heading', { name: /mcq practice browser/i })
  ).toBeVisible();
  await expect(page.getByRole('button', { name: 'Attempt' }).first()).toBeVisible();
  await shoot(page, 'mcqs');
});

test('mcq attempt (initial question)', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name === 'mobile', RESPONSIVE_BUG);
  await page.goto(`/mcqs/${FIXED_MCQ_ID}/attempt`);
  await expect(page.getByRole('heading', { name: `MCQ #${FIXED_MCQ_ID}` })).toBeVisible();
  await expect(page.getByRole('radio').first()).toBeVisible();
  // The seeded stem image path 404s in dev; mask it so its (broken) box never
  // introduces layout noise.
  await shoot(page, 'mcq-attempt', {
    mask: [page.locator('img[alt="MCQ illustration"]')],
  });
});

test('study cards', async ({ page }) => {
  await page.goto('/study-cards');
  const showAnswer = page.getByRole('button', { name: /show answer/i });
  const empty = page.getByText(/no cards due for review/i);
  await expect(showAnswer.or(empty).first()).toBeVisible();
  await shoot(page, 'study-cards');
});

test('html notes', async ({ page }) => {
  await page.goto('/html-notes');
  await expect(
    page.getByRole('heading', { name: 'HTML OSCE Notes', level: 1 })
  ).toBeVisible();
  await expect(page.getByRole('heading', { level: 2 }).first()).toBeVisible();
  await shoot(page, 'html-notes');
});

test('emr case list', async ({ page }) => {
  await page.goto('/emr/cases');
  await expect(
    page.getByRole('heading', { name: /pick an emr case/i })
  ).toBeVisible();
  await expect(
    page.getByRole('button', { name: /^Practise case:/ }).first()
  ).toBeVisible();
  await shoot(page, 'emr-cases');
});

test('emr epic editor (light theme)', async ({ page, request }, testInfo) => {
  test.skip(testInfo.project.name === 'mobile', RESPONSIVE_BUG);
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });
  await page.goto(`/emr/epic/${sessionId}`);
  await expect(page.getByRole('heading', { name: 'Epic EMR' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Clinical Scenario' })).toBeVisible();
  // Fresh session → auto-save idle, empty SOAP editor: a deterministic shell.
  await shoot(page, 'emr-epic');
});

test('emr cerner editor (dark theme)', async ({ page, request }, testInfo) => {
  test.skip(testInfo.project.name === 'mobile', RESPONSIVE_BUG);
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });
  await page.goto(`/emr/cerner/${sessionId}`);
  await expect(page.getByRole('heading', { name: 'Cerner PowerChart' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Clinical Scenario' })).toBeVisible();
  await shoot(page, 'emr-cerner');
});

test('osce practice picker', async ({ page }) => {
  await page.goto('/osce-practice');
  await expect(
    page.getByRole('heading', { name: /osce practice - patient personas/i })
  ).toBeVisible();
  // Wait for the persona list to finish loading: the "Select Patient" control
  // starts at "(0 available)" and, once the query resolves, becomes enabled and
  // shows a non-zero count. Shooting early captures the "0 available" state and
  // the later count change shifts the whole page.
  await expect(
    page.getByRole('combobox', { name: /select patient/i })
  ).toBeEnabled();
  await expect(
    page.getByText(/select patient \([1-9]\d* available\)/i).first()
  ).toBeVisible();
  await page.waitForLoadState('networkidle');
  await shoot(page, 'osce-practice');
});

test('mock exam start', async ({ page }) => {
  await page.goto('/osce/mock-exam/start');
  await expect(
    page.getByRole('heading', { name: /amc clinical examination mock exam/i })
  ).toBeVisible();
  await expect(page.getByRole('button', { name: /start mock exam/i })).toBeVisible();
  await shoot(page, 'mock-exam-start');
});

// ---------------------------------------------------------------------------
// EMR validation (AI-graded) — reuse ONE persisted, pre-graded session per
// project so the persisted terminal state is byte-identical across re-runs.
// ---------------------------------------------------------------------------
const FIXTURE_DIR = resolve(__dirname, '.fixtures');

/** A safe, well-structured STEMI note → a genuine graded submission. */
const VALIDATION_NOTE = {
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
 * Return a stable, already-graded EMR session id for `projectName`.
 *
 * First call (baseline update) seeds + submits via the API contract the backend
 * accepts and caches the id on disk. Subsequent runs (the verify re-runs) reuse
 * the SAME persisted session, so GET /emr/validation just re-reads the stored
 * grading → identical pixels. The `.fixtures` dir is a generated artifact.
 */
async function persistedGradedSessionId(
  request: Parameters<typeof apiLogin>[0],
  projectName: string
): Promise<string> {
  mkdirSync(FIXTURE_DIR, { recursive: true });
  const fp = resolve(FIXTURE_DIR, `validation-session-${projectName}.json`);
  if (existsSync(fp)) {
    try {
      const cached = JSON.parse(readFileSync(fp, 'utf8')) as { sessionId?: string };
      if (cached.sessionId) return cached.sessionId;
    } catch {
      /* fall through and re-seed */
    }
  }
  const token = await apiLogin(request);
  const sessionId = await seedEmrSession(request, { token });
  await submitEmrSession(request, token, sessionId, VALIDATION_NOTE);
  writeFileSync(fp, JSON.stringify({ sessionId }), 'utf8');
  return sessionId;
}

test('emr validation results (terminal state)', async ({ page, request }, testInfo) => {
  test.setTimeout(180_000);
  const sessionId = await persistedGradedSessionId(request, testInfo.project.name);

  await page.goto(`/emr/validation/${sessionId}`);
  // The page shell is always present.
  await expect(
    page.getByRole('heading', { name: /emr validation results/i })
  ).toBeVisible({ timeout: 60_000 });

  // Wait for a TERMINAL state: either a graded score, or the honest
  // "AI assessment temporarily unavailable" notice.
  const score = page.getByText(/\b\d+(?:\.\d+)?\s*\/\s*15\b/);
  const aiDown = page.getByText(/AI assessment is temporarily unavailable/i);
  await expect(score.first().or(aiDown)).toBeVisible({ timeout: 120_000 });

  // Mask the numeric verdict as insurance (persisted → already stable).
  await shoot(page, 'emr-validation', {
    mask: [
      page.getByText('PASS', { exact: true }),
      page.getByText('FAIL', { exact: true }),
      score,
    ],
  });
});
