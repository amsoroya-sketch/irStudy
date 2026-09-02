import { defineConfig, devices } from '@playwright/test';

/**
 * Playwright config for frontend E2E tests (Phase E-0 foundations).
 *
 * Only picks up *.spec.ts under tests/ so it never collides with the Vitest
 * component tests (*.test.tsx). Runs against the seeded dev stack; the base URL
 * is configurable via PLAYWRIGHT_BASE_URL (defaults to the Vite dev server).
 *
 * globalSetup logs the seeded student in once and writes tests/.auth/user.json,
 * which every spec reuses via `use.storageState`. Auth specs override with
 * `test.use({ storageState: { cookies: [], origins: [] } })`.
 */
export default defineConfig({
  testDir: './tests',
  testMatch: '**/*.spec.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  // The dev backend serialises requests behind in-flight Claude calls, so on
  // high-core hosts Playwright's default (cores/2) worker count starves the REST
  // journey specs into timeouts. Cap workers (override with PW_WORKERS).
  workers: process.env.PW_WORKERS ? Number(process.env.PW_WORKERS) : 4,
  // Live-AI journeys can be slow; give generous per-test / assertion budgets.
  timeout: 60 * 1000,
  expect: { timeout: 15 * 1000 },
  reporter: [
    ['list'],
    ['html', { open: 'never' }],
    ['json', { outputFile: 'playwright-report/results.json' }],
  ],
  globalSetup: './tests/global-setup.ts',
  globalTeardown: './tests/global-teardown.ts',
  // Visual regression baselines: one per file + arg + project.
  snapshotPathTemplate: 'tests/__screenshots__/{testFilePath}/{arg}-{projectName}.png',
  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    // Reuse the logged-in student state written by global-setup. Auth specs
    // opt out per-file with test.use({ storageState: { cookies: [], origins: [] } }).
    storageState: 'tests/.auth/user.json',
  },
  projects: [
    {
      name: 'desktop',
      use: { ...devices['Desktop Chrome'], viewport: { width: 1280, height: 800 } },
    },
    {
      name: 'mobile',
      // Mobile viewport on chromium (Pixel-like); keep engine to chromium only.
      use: { ...devices['Desktop Chrome'], viewport: { width: 390, height: 844 } },
    },
  ],
  // Boot the Vite dev server for E2E runs. Locally we reuse an already-running
  // server (fast inner loop); in CI we always start a fresh one.
  webServer: {
    command: 'npm run dev',
    url: process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
