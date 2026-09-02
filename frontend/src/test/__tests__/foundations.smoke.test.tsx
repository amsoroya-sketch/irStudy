/**
 * Foundations smoke test (Phase 0).
 *
 * Proves the shared UI-test foundations wire up correctly:
 *  - renderWithProviders mounts UI under the provider stack (with and without a `path`)
 *  - the axe harness + `toHaveNoViolations` matcher are registered and pass on
 *    a trivially accessible fragment.
 *
 * This is infrastructure validation, not a product test.
 */

import { it, expect } from 'vitest';
import { renderWithProviders, screen } from '../renderWithProviders';
import { expectNoA11yViolations } from '../axe';

it('renders a plain element under the providers (no path)', () => {
  renderWithProviders(<h1>Foundations OK</h1>);
  expect(screen.getByRole('heading', { name: 'Foundations OK' })).toBeInTheDocument();
});

it('renders a route-param element via a `path` route', () => {
  renderWithProviders(<h1>Session View</h1>, {
    path: '/emr/validation/:sessionId',
    route: '/emr/validation/sess-1',
  });
  expect(screen.getByRole('heading', { name: 'Session View' })).toBeInTheDocument();
});

it('seeds a dummy token when authed is set', () => {
  localStorage.clear();
  renderWithProviders(<p>Authed</p>, { authed: true });
  expect(localStorage.getItem('accessToken')).toBe('test-token');
});

it('passes expectNoA11yViolations on an accessible fragment', async () => {
  const { container } = renderWithProviders(
    <main>
      <h1>Accessible Page</h1>
      <button type="button">Continue</button>
      <img src="/logo.png" alt="Study platform logo" />
    </main>
  );
  await expectNoA11yViolations(container);
});
