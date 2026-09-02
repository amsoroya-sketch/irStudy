/**
 * Playwright global setup (Phase E-0 E2E foundations).
 *
 * Logs the seeded student in ONCE via the backend API and persists a
 * `storageState` (localStorage: accessToken/refreshToken/user under the Vite
 * origin) so protected-route specs load straight into the app without driving
 * the login UI. Auth specs opt out with `test.use({ storageState: ... })`.
 *
 * Seeding the DB/user is an ops step (dropping/creating `irstudy_e2e`), NOT done
 * here — if login fails we throw a clear, actionable error. No hardcoded
 * secrets: everything comes from env with dev/test defaults.
 */

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { request } from '@playwright/test';

const __dirname = dirname(fileURLToPath(import.meta.url));

const STUDENT_EMAIL = process.env.E2E_STUDENT_EMAIL || 'student@test.com';
const STUDENT_PASSWORD = process.env.E2E_STUDENT_PASSWORD || 'Student123!@#';
const API_BASE_URL = process.env.VITE_API_URL || 'http://localhost:8001/api/v1';
const APP_ORIGIN = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:5173';

const AUTH_FILE = resolve(__dirname, '.auth/user.json');

/** Backend origin (health endpoint lives at `<origin>/health`, outside /api/v1). */
function backendOrigin(): string {
  return new URL(API_BASE_URL).origin;
}

/** Poll the backend health endpoint until it is up (or time out). */
async function waitForBackend(timeoutMs = 30_000): Promise<void> {
  const ctx = await request.newContext();
  const healthUrl = `${backendOrigin()}/health`;
  const deadline = Date.now() + timeoutMs;
  let lastError = 'unknown error';
  try {
    while (Date.now() < deadline) {
      try {
        const res = await ctx.get(healthUrl, { timeout: 5_000 });
        if (res.ok()) return;
        lastError = `HTTP ${res.status()}`;
      } catch (err) {
        lastError = err instanceof Error ? err.message : String(err);
      }
      await new Promise((r) => setTimeout(r, 1_000));
    }
  } finally {
    await ctx.dispose();
  }
  throw new Error(
    `Backend not reachable at ${healthUrl} after ${timeoutMs}ms (${lastError}).\n` +
      'Start the backend and seed the E2E student before running E2E tests.'
  );
}

export default async function globalSetup(): Promise<void> {
  await waitForBackend();

  // NOTE: build absolute URLs from API_BASE_URL rather than relying on the
  // request-context baseURL join. Playwright resolves a leading-slash path
  // against the ORIGIN of baseURL (dropping the `/api/v1` prefix), which 404s.
  const ctx = await request.newContext();
  try {
    const loginRes = await ctx.post(`${API_BASE_URL}/auth/login`, {
      data: { email: STUDENT_EMAIL, password: STUDENT_PASSWORD },
    });

    if (!loginRes.ok()) {
      const body = await loginRes.text().catch(() => '');
      throw new Error(
        `E2E login failed: ${loginRes.status()} ${loginRes.statusText()} — ${body}\n` +
          `The E2E student (${STUDENT_EMAIL}) must exist. Start the backend and seed\n` +
          'the user/DB (ops step: create `irstudy_e2e` + seed student) before running.'
      );
    }

    const { access_token, refresh_token } = (await loginRes.json()) as {
      access_token: string;
      refresh_token: string;
    };

    const meRes = await ctx.get(`${API_BASE_URL}/users/me`, {
      headers: { Authorization: `Bearer ${access_token}` },
    });
    if (!meRes.ok()) {
      const body = await meRes.text().catch(() => '');
      throw new Error(
        `E2E setup: /users/me failed: ${meRes.status()} ${meRes.statusText()} — ${body}`
      );
    }
    const user = await meRes.json();

    const storageState = {
      cookies: [],
      origins: [
        {
          origin: APP_ORIGIN,
          localStorage: [
            { name: 'accessToken', value: access_token },
            { name: 'refreshToken', value: refresh_token },
            { name: 'user', value: JSON.stringify(user) },
          ],
        },
      ],
    };

    mkdirSync(dirname(AUTH_FILE), { recursive: true });
    writeFileSync(AUTH_FILE, JSON.stringify(storageState, null, 2), 'utf8');
    console.log(`[global-setup] wrote auth storageState -> ${AUTH_FILE}`);
  } finally {
    await ctx.dispose();
  }
}
