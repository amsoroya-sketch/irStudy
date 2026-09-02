/**
 * Route-coverage tagging helper (Phase E-0 E2E foundations).
 *
 * Every journey spec declares which app route it exercises via `routeTest`.
 * The route is embedded in the Playwright test title as `@route:<path>` (a
 * grep-able tag) so the post-run gate (tests/verify-route-coverage.mjs) can
 * prove every route in ROUTES has at least one PASSING tagged test.
 *
 * Usage:
 *   import { routeTest } from './support/coverage';
 *   routeTest('/dashboard', 'dashboard renders KPIs', async ({ page }) => { ... });
 */

import { test } from '@playwright/test';

/** Matches `@route:<path>` tags in a test title. Global for repeated exec. */
export const ROUTE_TAG_RE = /@route:(\S+)/g;

/** Build the canonical tag for a route path. */
export function tagFor(path: string): string {
  return `@route:${path}`;
}

/** Routes recorded via routeTest during collection (best-effort, in-process). */
const recorded = new Set<string>();

/** Snapshot of routes tagged so far (order-independent). */
export function recordedRoutes(): string[] {
  return [...recorded];
}

/**
 * Declare a Playwright test that covers `routePath`.
 *
 * Appends the `@route:<routePath>` tag to the title and records the route so
 * the coverage gate can cross-check it against the canonical ROUTES list.
 */
export function routeTest(
  routePath: string,
  title: string,
  fn: Parameters<typeof test>[1]
): void {
  recorded.add(routePath);
  test(`${title} ${tagFor(routePath)}`, fn);
}
