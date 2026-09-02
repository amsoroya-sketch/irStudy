/**
 * EMRSelectSystemPage tests.
 *
 * Choosing Epic or Cerner persists the preference to
 * localStorage['emr_system_preference'] and navigates to
 * /emr/{system}/{sessionId}.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return { ...actual, useNavigate: () => navigateMock };
});

import {
  renderWithProviders,
  screen,
  userEvent,
} from '../../../test/renderWithProviders';
import EMRSelectSystemPage from '../EMRSelectSystemPage';

const renderPage = () =>
  renderWithProviders(<EMRSelectSystemPage />, {
    path: '/emr/select/:sessionId',
    route: '/emr/select/sess-1',
  });

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('EMRSelectSystemPage', () => {
  it('selecting Epic saves the preference and navigates', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole('heading', { level: 2, name: 'Epic' }));

    expect(localStorage.getItem('emr_system_preference')).toBe('epic');
    expect(navigateMock).toHaveBeenCalledWith('/emr/epic/sess-1');
  });

  it('selecting Cerner saves the preference and navigates', async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(screen.getByRole('heading', { level: 2, name: 'Cerner' }));

    expect(localStorage.getItem('emr_system_preference')).toBe('cerner');
    expect(navigateMock).toHaveBeenCalledWith('/emr/cerner/sess-1');
  });
});
