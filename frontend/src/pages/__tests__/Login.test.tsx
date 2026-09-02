/**
 * Login page tests (Phase 3 — component/a11y layer, no backend).
 *
 * Renders the real <Login /> inside the real <AuthProvider> and mocks the
 * axiosInstance transport so the genuine auth flow is exercised: form fields
 * (by label), client-side validation, submit -> POST /auth/login + GET
 * /users/me, token persisted to localStorage, and navigation to /dashboard.
 * Invalid-credentials error surfacing and a11y are also covered.
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

// --- useNavigate spy (keep the real MemoryRouter/Routes from renderWithProviders) ---
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

import Login from '../Login';
import { AuthProvider } from '../../context/AuthContext';

const VALID_EMAIL = 'student@example.com';
const VALID_PASSWORD = 'Password123!';

const renderLogin = () =>
  renderWithProviders(
    <AuthProvider>
      <Login />
    </AuthProvider>,
    { route: '/login' }
  );

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});

describe('Login', () => {
  it('renders the email and password fields by label', () => {
    renderLogin();
    expect(screen.getByLabelText(/Email Address/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/^Password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeInTheDocument();
  });

  it('logs in successfully: stores the token and navigates to /dashboard', async () => {
    const user = userEvent.setup();
    post.mockResolvedValue({
      data: { access_token: 'jwt-access-token', refresh_token: 'jwt-refresh-token' },
    });
    get.mockResolvedValue({
      data: { id: 1, email: VALID_EMAIL, full_name: 'Test Student' },
    });

    renderLogin();

    await user.type(screen.getByLabelText(/Email Address/i), VALID_EMAIL);
    await user.type(screen.getByLabelText(/^Password/i), VALID_PASSWORD);
    await user.click(screen.getByRole('button', { name: /Sign In/i }));

    await waitFor(() =>
      expect(post).toHaveBeenCalledWith('/auth/login', {
        email: VALID_EMAIL,
        password: VALID_PASSWORD,
      })
    );
    await waitFor(() =>
      expect(localStorage.getItem('accessToken')).toBe('jwt-access-token')
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/dashboard')
    );
  });

  it('shows the server error message when credentials are invalid', async () => {
    const user = userEvent.setup();
    post.mockRejectedValue({
      response: { data: { detail: 'Invalid email or password' } },
    });

    renderLogin();

    await user.type(screen.getByLabelText(/Email Address/i), VALID_EMAIL);
    await user.type(screen.getByLabelText(/^Password/i), VALID_PASSWORD);
    await user.click(screen.getByRole('button', { name: /Sign In/i }));

    expect(
      await screen.findByText(/Invalid email or password/i)
    ).toBeInTheDocument();
    expect(navigateMock).not.toHaveBeenCalledWith('/dashboard');
    expect(localStorage.getItem('accessToken')).toBeNull();
  });

  it('validates a required email on blur', async () => {
    const user = userEvent.setup();
    renderLogin();

    const email = screen.getByLabelText(/Email Address/i);
    await user.click(email);
    await user.tab(); // blur without typing

    expect(await screen.findByText(/Email is required/i)).toBeInTheDocument();
  });

  it('validates an invalid email format on blur', async () => {
    const user = userEvent.setup();
    renderLogin();

    const email = screen.getByLabelText(/Email Address/i);
    await user.type(email, 'not-an-email');
    await user.tab();

    expect(await screen.findByText(/Invalid email address/i)).toBeInTheDocument();
    // Submit stays disabled while the form is invalid.
    expect(screen.getByRole('button', { name: /Sign In/i })).toBeDisabled();
  });

  it('has no accessibility violations', async () => {
    const { container } = renderLogin();
    await expectNoA11yViolations(container);
  });
});
