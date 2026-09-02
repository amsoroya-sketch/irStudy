/**
 * renderWithProviders — shared UI-test render helper (Phase 0 foundations).
 *
 * Wraps any UI in the same provider stack the app uses:
 *   QueryClientProvider (retry: false) -> MUI ThemeProvider (app theme)
 *   -> MemoryRouter.
 *
 * Mirrors the ad-hoc `wrap`/`renderPage` helpers in
 * src/pages/emr/__tests__/* so specs can import a single, typed entry point.
 *
 * Usage:
 *   renderWithProviders(<MyPage />);                         // renders under router
 *   renderWithProviders(<MyPage />, { authed: true });       // seeds accessToken
 *   renderWithProviders(<EMRValidationPage />, {             // route-param pages
 *     path: '/emr/validation/:sessionId',
 *     route: '/emr/validation/sess-1',
 *   });
 */

import type { ReactElement, ReactNode } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@mui/material/styles';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { render, type RenderOptions, type RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import appTheme from '../theme/theme';

export interface RenderWithProvidersOptions {
  /** Single initial location for the router (used when `initialEntries` is omitted). */
  route?: string;
  /** When set, render `<Routes><Route path={path} element={ui} /></Routes>` for param pages. */
  path?: string;
  /** Explicit MemoryRouter history stack; overrides `route` when provided. */
  initialEntries?: string[];
  /** Seed a dummy JWT in localStorage before render (for auth-gated UI). */
  authed?: boolean;
  /** Provide a shared QueryClient; a fresh retry-disabled one is created otherwise. */
  queryClient?: QueryClient;
  /** Passthrough options for @testing-library/react `render`. */
  renderOptions?: Omit<RenderOptions, 'wrapper'>;
}

/** Fresh QueryClient with retries disabled so failed queries surface immediately in tests. */
export function createTestQueryClient(): QueryClient {
  return new QueryClient({ defaultOptions: { queries: { retry: false } } });
}

export function renderWithProviders(
  ui: ReactElement,
  {
    route = '/',
    path,
    initialEntries,
    authed = false,
    queryClient,
    renderOptions,
  }: RenderWithProvidersOptions = {}
): RenderResult & { queryClient: QueryClient } {
  if (authed) {
    localStorage.setItem('accessToken', 'test-token');
  }

  const client = queryClient ?? createTestQueryClient();
  const entries = initialEntries ?? [route];

  const Wrapper = ({ children }: { children: ReactNode }): ReactElement => (
    <QueryClientProvider client={client}>
      <ThemeProvider theme={appTheme}>
        <MemoryRouter initialEntries={entries}>
          {path ? (
            <Routes>
              <Route path={path} element={children} />
            </Routes>
          ) : (
            children
          )}
        </MemoryRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );

  const result = render(ui, { wrapper: Wrapper, ...renderOptions });
  return { ...result, queryClient: client };
}

// Re-export the RTL surface + userEvent so specs import from one place.
export * from '@testing-library/react';
export { userEvent };
export { appTheme };
