/**
 * OSCESession page tests (Phase 3 — component/a11y layer, no backend).
 *
 * Route-param page (`/osce/session/:attemptId`). The session + persona fetches
 * are mocked and the heavy children (WebSocketChat, SessionTimer,
 * SessionControls, OSCEToEMRModal) are stubbed so the test stays focused on the
 * page shell: loading, load error, the rendered station header/patient card +
 * chat mount, the "Back to OSCE Practice" navigation, and a11y.
 *
 * Uses the Phase 0 foundations: renderWithProviders + expectNoA11yViolations.
 */

import { it, expect, vi, beforeEach, describe } from 'vitest';
import {
  renderWithProviders,
  screen,
  userEvent,
} from '../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../test/axe';
import type { OSCEAttempt } from '../../api/osce';
import type { PersonaDetail } from '../../api/personas';

// --- useNavigate spy (keep the real MemoryRouter/useParams) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- Auth (owner of the session, with a token so the chat mounts) ---
vi.mock('../../context/AuthContext', () => ({
  useAuth: () => ({ user: { id: 'user-1' }, token: 'test-token' }),
}));

// --- API layer ---
const getOSCESession = vi.fn();
vi.mock('../../api/osce', () => ({
  getOSCESession: (...a: unknown[]) => getOSCESession(...a),
  endOSCESession: vi.fn(),
  pauseOSCESession: vi.fn(),
  resumeOSCESession: vi.fn(),
  getOSCEScore: vi.fn(),
}));

const getPersonaDetail = vi.fn();
vi.mock('../../api/personas', () => ({
  getPersonaDetail: (...a: unknown[]) => getPersonaDetail(...a),
}));

// --- Heavy children stubbed to keep the test focused on the page shell ---
vi.mock('../../components/osce/WebSocketChat', () => ({
  WebSocketChat: () => <div data-testid="ws-chat">WebSocket Chat</div>,
}));
vi.mock('../../components/osce/SessionTimer', () => ({
  SessionTimer: () => <div data-testid="session-timer">Timer</div>,
}));
vi.mock('../../components/osce/SessionControls', () => ({
  SessionControls: () => <div data-testid="session-controls">Controls</div>,
}));
vi.mock('../../components/integration/OSCEToEMRModal', () => ({
  OSCEToEMRModal: () => null,
}));

import OSCESession from '../OSCESession';

const SESSION: OSCEAttempt = {
  attempt_id: '123e4567-e89b-12d3-a456-426614174000',
  user_id: 'user-1',
  persona_id: 'persona-1',
  started_at: '2026-09-01T10:00:00Z',
  completed_at: null,
  score: null,
  status: 'in_progress',
  transcript: [],
};

const PERSONA: PersonaDetail = {
  persona_id: 'persona-1',
  persona_code: 'cardiology_001',
  name: 'John Brown',
  age: 65,
  gender: 'male',
  specialty: 'Cardiology',
  chief_complaint: 'Central crushing chest pain',
  difficulty_level: 'advanced',
  estimated_pass_rate: 0.42,
  amc_blueprint_area: 'Cardiovascular',
  occupation: null,
  cultural_background: null,
  preferred_language: 'English',
  opening_statement: 'Doctor, I have chest pain.',
  symptoms: {},
  medical_history: {},
  emotional_profile: {},
  rag_query_hints: [],
  key_differentials: [],
  critical_actions: [],
  amc_competencies: [],
};

const renderPage = () =>
  renderWithProviders(<OSCESession />, {
    path: '/osce/session/:attemptId',
    route: '/osce/session/123e4567-e89b-12d3-a456-426614174000',
    authed: true,
  });

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getOSCESession.mockResolvedValue(SESSION);
  getPersonaDetail.mockResolvedValue(PERSONA);
});

describe('OSCESession', () => {
  it('shows the loading state while the session is fetching', () => {
    getOSCESession.mockReturnValue(new Promise(() => {})); // never resolves
    renderPage();
    expect(screen.getByLabelText('Loading session')).toBeInTheDocument();
    expect(screen.getByText(/Loading OSCE session/i)).toBeInTheDocument();
  });

  it('renders the station header, patient card and chat once loaded', async () => {
    renderPage();

    expect(
      await screen.findByRole('heading', { name: /OSCE Session: John Brown/i })
    ).toBeInTheDocument();
    // Patient info card + specialty chip.
    expect(screen.getByText('Central crushing chest pain')).toBeInTheDocument();
    expect(screen.getByText('Cardiovascular')).toBeInTheDocument();
    // Stubbed children mounted.
    expect(screen.getByTestId('ws-chat')).toBeInTheDocument();
    expect(screen.getByTestId('session-timer')).toBeInTheDocument();
    expect(screen.getByTestId('session-controls')).toBeInTheDocument();
  });

  it('navigates back to OSCE practice from the header button', async () => {
    const user = userEvent.setup();
    renderPage();
    await screen.findByRole('heading', { name: /OSCE Session: John Brown/i });

    await user.click(
      screen.getByRole('button', { name: /Back to OSCE Practice/i })
    );
    expect(navigateMock).toHaveBeenCalledWith('/osce-practice');
  });

  it('shows an error state when the session fails to load', async () => {
    getOSCESession.mockRejectedValue(new Error('network down'));
    renderPage();

    expect(
      await screen.findByText(/Failed to load OSCE session/i, undefined, {
        timeout: 5000,
      })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('button', { name: /Back to OSCE Practice/i })
    ).toBeInTheDocument();
  });

  it('has no accessibility violations on the loaded session', async () => {
    const { container } = renderPage();
    await screen.findByRole('heading', { name: /OSCE Session: John Brown/i });
    await expectNoA11yViolations(container);
  });
});
