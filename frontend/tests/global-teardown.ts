/**
 * Playwright global teardown (Phase E-0 E2E foundations).
 *
 * Intentionally minimal: E2E database teardown is handled out-of-band by
 * dropping the `irstudy_e2e` database (ops step), so there is nothing to clean
 * up here. Kept as a valid hook for future needs.
 */

export default async function globalTeardown(): Promise<void> {
  console.log('[global-teardown] done (DB teardown handled out-of-band).');
}
