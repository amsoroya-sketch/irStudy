/**
 * StartEMRSessionPage tests.
 *
 * The page starts a session via axiosInstance.post('/emr/sessions/start', {})
 * and, on success, navigates to the saved-preference system or the system
 * selector. We mock axiosInstance and react-router's useNavigate.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return { ...actual, useNavigate: () => navigateMock };
});

const post = vi.fn();
vi.mock('../../../utils/axiosInstance', () => ({
  default: { post: (...a: unknown[]) => post(...a) },
}));

import {
  renderWithProviders,
  screen,
  waitFor,
  userEvent,
} from '../../../test/renderWithProviders';
import StartEMRSessionPage from '../StartEMRSessionPage';

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('StartEMRSessionPage', () => {
  it('renders the start button', () => {
    renderWithProviders(<StartEMRSessionPage />);
    expect(
      screen.getByRole('button', { name: /Start New EMR Session/i })
    ).toBeInTheDocument();
  });

  it('shows the pending state while starting', async () => {
    const user = userEvent.setup();
    post.mockReturnValue(new Promise(() => {}));
    renderWithProviders(<StartEMRSessionPage />);

    await user.click(
      screen.getByRole('button', { name: /Start New EMR Session/i })
    );
    expect(
      await screen.findByText('Starting your EMR session...')
    ).toBeInTheDocument();
  });

  it('shows an error alert when starting fails', async () => {
    const user = userEvent.setup();
    post.mockRejectedValue(new Error('server error'));
    renderWithProviders(<StartEMRSessionPage />);

    await user.click(
      screen.getByRole('button', { name: /Start New EMR Session/i })
    );
    expect(
      await screen.findByText(/Failed to start session/i)
    ).toBeInTheDocument();
  });

  it('navigates straight to the saved system preference', async () => {
    const user = userEvent.setup();
    localStorage.setItem('emr_system_preference', 'cerner');
    post.mockResolvedValue({ data: { session_id: 'sess-77' } });
    renderWithProviders(<StartEMRSessionPage />);

    await user.click(
      screen.getByRole('button', { name: /Start New EMR Session/i })
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/emr/cerner/sess-77')
    );
  });

  it('navigates to the system selector when no preference is saved', async () => {
    const user = userEvent.setup();
    post.mockResolvedValue({ data: { session_id: 'sess-77' } });
    renderWithProviders(<StartEMRSessionPage />);

    await user.click(
      screen.getByRole('button', { name: /Start New EMR Session/i })
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/emr/select/sess-77')
    );
  });
});
