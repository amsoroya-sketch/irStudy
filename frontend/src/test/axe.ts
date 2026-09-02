/**
 * Accessibility harness for component tests.
 *
 * Runs axe-core over a rendered container and asserts zero WCAG violations.
 * The `toHaveNoViolations` matcher is registered globally in src/test/setup.ts.
 *
 * Usage:
 *   const { container } = renderWithProviders(<MyComponent />);
 *   await expectNoA11yViolations(container);
 */

import { expect } from 'vitest';
import { axe } from 'jest-axe';

// Teach Vitest's expect about the jest-axe matcher (registered in setup.ts).
declare module 'vitest' {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  interface Assertion<T = any> {
    toHaveNoViolations(): T;
  }
  interface AsymmetricMatchersContaining {
    toHaveNoViolations(): void;
  }
}

/** Assert the given container has no detectable accessibility violations. */
export async function expectNoA11yViolations(container: HTMLElement): Promise<void> {
  const results = await axe(container);
  expect(results).toHaveNoViolations();
}
