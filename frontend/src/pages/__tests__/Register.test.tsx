/**
 * Register page tests (Phase 3 — component/a11y layer, no backend).
 *
 * Renders the real <Register /> inside the real <AuthProvider> with a mocked
 * axiosInstance. Covers field rendering, client-side validation (password
 * complexity + confirm-password mismatch), submit -> POST /auth/register with
 * the success message, server-error surfacing, and a11y.
 *
 * Uses the Phase 0 foundations: renderWithProviders + expectNoA11yViolations.
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  waitFor,
  userEvent,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';

// --- useNavigate spy (keep the real MemoryRouter/Routes) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- axios transport used by AuthContext ---
const get = vi.fn();
const post = vi.fn();
vi.mock('../../utils/axiosInstance', () => ({
  default: {
    get: (...a: unknown[]) => get(...a),
    post: (...a: unknown[]) => post(...a),
  },
}));

import Register from '../Register';
import { AuthProvider } from '../../context/AuthContext';

const VALID = {
  fullName: 'Jane Doe',
  email: 'jane@example.com',
  password: 'Password123!',
};

const renderRegister = () =>
  renderWithProviders(
    <AuthProvider>
      <Register />
    </AuthProvider>,
    { route: '/register' }
  );

/** Fill in a valid form so the submit button becomes enabled. */
const fillValidForm = async (user: ReturnType<typeof userEvent.setup>) => {
  await user.type(screen.getByLabelText(/Full Name/i), VALID.fullName);
  await user.type(screen.getByLabelText(/Email Address/i), VALID.email);
  await user.type(screen.getByLabelText(/^Password/i), VALID.password);
  await user.type(screen.getByLabelText(/Confirm Password/i), VALID.password);
  await user.click(screen.getByRole('checkbox', { name: /accept the terms/i }));
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('Register', () => {
  it('renders all account fields and the terms checkbox', () => {
    renderRegister();
    expect(screen.getByLabelText(/Full Name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Confirm Password/i)).toBeInTheDocument();
    expect(
      screen.getByRole('checkbox', { name: /accept the terms/i })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Create Account/i })
    ).toBeInTheDocument();
  });

  it('flags a weak password that fails the complexity rules', async () => {
    const user = userEvent.setup();
    renderRegister();

    await user.type(screen.getByLabelText(/^Password/i), 'short');
    await user.tab();

    expect(
      await screen.findByText(/at least 12 characters/i)
    ).toBeInTheDocument();
  });

  it('flags mismatched confirm password on blur', async () => {
    const user = userEvent.setup();
    renderRegister();

    await user.type(screen.getByLabelText(/^Password/i), VALID.password);
    await user.type(screen.getByLabelText(/Confirm Password/i), 'Different123!');
    await user.tab();

    expect(
      await screen.findByText(/Passwords do not match/i)
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Create Account/i })
    ).toBeDisabled();
  });

  it('registers successfully and shows the success message', async () => {
    const user = userEvent.setup();
    post.mockResolvedValue({ data: {} });
    renderRegister();

    await fillValidForm(user);
    await user.click(screen.getByRole('button', { name: /Create Account/i }));

    await waitFor(() =>
      expect(post).toHaveBeenCalledWith(
        '/auth/register',
        expect.objectContaining({
          email: VALID.email,
          password: VALID.password,
          full_name: VALID.fullName,
        })
      )
    );
    expect(
      await screen.findByText(/Registration successful/i)
    ).toBeInTheDocument();
  });

  it('shows the server error message when registration fails', async () => {
    const user = userEvent.setup();
    post.mockRejectedValue({
      response: { data: { detail: 'Email already registered' } },
    });
    renderRegister();

    await fillValidForm(user);
    await user.click(screen.getByRole('button', { name: /Create Account/i }));

    expect(
      await screen.findByText(/Email already registered/i)
    ).toBeInTheDocument();
    expect(screen.queryByText(/Registration successful/i)).not.toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = renderRegister();
    await expectNoA11yViolations(container);
  });
});
