#!/usr/bin/env node
/**
 * verify-route-coverage.mjs — post-run E2E coverage gate (Phase E-0).
 *
 * Proves every canonical app route has at least one PASSING journey test.
 *
 *   1. Canonical routes: parsed from src/routes.config.tsx (the ROUTES array).
 *   2. Covered routes:   `@route:<path>` tags collected from PASSED tests in
 *                        the Playwright JSON report (playwright-report/results.json).
 *   3. Any route with zero passing tagged tests -> printed + non-zero exit.
 *
 * Runs after `playwright test` (see package.json `test:e2e`). If no report
 * exists yet (e.g. run standalone before any E2E run) it prints a notice and
 * exits 0 rather than crashing.
 */

import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, resolve } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROUTES_CONFIG = resolve(__dirname, '../src/routes.config.tsx');
const REPORT_PATH = resolve(__dirname, '../playwright-report/results.json');

const ROUTE_TAG_RE = /@route:(\S+)/g;

/** Extract the canonical route paths from the ROUTES array declaration. */
function canonicalRoutes() {
  if (!existsSync(ROUTES_CONFIG)) {
    console.error(`✖ Cannot find routes config at ${ROUTES_CONFIG}`);
    process.exit(2);
  }
  const src = readFileSync(ROUTES_CONFIG, 'utf8');
  // Match `path: '<x>'` / `path: "<x>"` entries (the interface uses `path: string;`
  // without quotes, so it is not matched — only real ROUTES entries are).
  const re = /path:\s*['"]([^'"]+)['"]/g;
  const paths = [];
  let m;
  while ((m = re.exec(src)) !== null) {
    paths.push(m[1]);
  }
  return [...new Set(paths)];
}

/** Recursively collect every spec from the Playwright JSON suite tree. */
function collectSpecs(suite, out) {
  for (const spec of suite.specs ?? []) out.push(spec);
  for (const child of suite.suites ?? []) collectSpecs(child, out);
}

/** A spec passed if it reports ok and has at least one passing result. */
function specPassed(spec) {
  if (spec.ok !== true) return false;
  return (spec.tests ?? []).some((t) =>
    (t.results ?? []).some((r) => r.status === 'passed')
  );
}

/** Map of route path -> Set of spec titles that pass and tag it. */
function coveredRoutes(report) {
  const specs = [];
  for (const suite of report.suites ?? []) collectSpecs(suite, specs);

  const covered = new Map();
  for (const spec of specs) {
    if (!specPassed(spec)) continue;
    const title = spec.title ?? '';
    let m;
    ROUTE_TAG_RE.lastIndex = 0;
    while ((m = ROUTE_TAG_RE.exec(title)) !== null) {
      const route = m[1];
      if (!covered.has(route)) covered.set(route, new Set());
      covered.get(route).add(spec.file ? `${spec.file} › ${title}` : title);
    }
  }
  return covered;
}

function main() {
  const routes = canonicalRoutes();

  if (!existsSync(REPORT_PATH)) {
    console.log('ℹ no report yet — expected at ' + REPORT_PATH);
    console.log('  Run `playwright test` first (or `npm run test:e2e`).');
    console.log(`  Canonical routes to cover: ${routes.length}`);
    process.exit(0);
  }

  let report;
  try {
    const raw = readFileSync(REPORT_PATH, 'utf8').trim();
    if (!raw) {
      console.log('ℹ report is empty — no E2E results to verify yet.');
      process.exit(0);
    }
    report = JSON.parse(raw);
  } catch (err) {
    console.error(`✖ Could not parse ${REPORT_PATH}: ${err.message}`);
    process.exit(2);
  }

  const covered = coveredRoutes(report);

  // Print the coverage table.
  const pad = Math.max(...routes.map((r) => r.length), 'route'.length);
  console.log('\nRoute coverage (passing @route-tagged tests):\n');
  console.log(`  ${'route'.padEnd(pad)}  covered  spec`);
  console.log(`  ${'-'.repeat(pad)}  -------  ----`);

  const uncovered = [];
  for (const route of routes) {
    const hits = covered.get(route);
    const ok = hits && hits.size > 0;
    if (!ok) uncovered.push(route);
    const spec = ok ? [...hits][0] : '—';
    console.log(`  ${route.padEnd(pad)}  ${ok ? '  ✔  ' : '  ✖  '}    ${spec}`);
  }

  console.log(
    `\n${routes.length - uncovered.length}/${routes.length} routes covered.`
  );

  if (uncovered.length > 0) {
    console.error(
      `\n✖ ${uncovered.length} route(s) with NO passing tagged test:\n` +
        uncovered.map((r) => `    - ${r}`).join('\n')
    );
    process.exit(1);
  }

  console.log('✔ All routes covered by at least one passing test.');
  process.exit(0);
}

main();
