/**
 * OSCEPractice page tests (Phase 3 — component/a11y layer, no backend).
 *
 * Mocks the personas + OSCE API clients and verifies: the persona list renders
 * into the selector, loading / empty / error states, selecting a persona loads
 * and shows its detail, and Start Session creates a session then navigates to
 * /osce/session/:attemptId. a11y on the loaded page.
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
import type { PersonaListItem, PersonaDetail } from '../../api/personas';

// --- useNavigate spy (keep the real MemoryRouter/Routes) ---
const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual =
    await vi.importActual<typeof import('react-router-dom')>('react-router-dom');
  return { ...actual, useNavigate: () => navigateMock };
});

// --- API layer ---
const getPersonas = vi.fn();
const getPersonaDetail = vi.fn();
vi.mock('../../api/personas', () => ({
  getPersonas: (...a: unknown[]) => getPersonas(...a),
  getPersonaDetail: (...a: unknown[]) => getPersonaDetail(...a),
}));

const createOSCESession = vi.fn();
vi.mock('../../api/osce', () => ({
  createOSCESession: (...a: unknown[]) => createOSCESession(...a),
}));

import OSCEPractice from '../OSCEPractice';

const PERSONA_ID = '123e4567-e89b-12d3-a456-426614174000';

const PERSONAS: PersonaListItem[] = [
  {
    persona_id: PERSONA_ID,
    persona_code: 'cardiology_001_stemi_male_65',
    name: 'John Brown',
    age: 65,
    gender: 'male',
    specialty: 'Cardiology',
    chief_complaint: 'Central crushing chest pain',
    difficulty_level: 'advanced',
    estimated_pass_rate: 0.42,
    amc_blueprint_area: 'Cardiovascular',
  },
];

const DETAIL: PersonaDetail = {
  ...PERSONAS[0],
  occupation: 'Retired teacher',
  cultural_background: 'Anglo-Australian',
  preferred_language: 'English',
  opening_statement: 'Doctor, I have terrible chest pain.',
  symptoms: {},
  medical_history: {},
  emotional_profile: {},
  rag_query_hints: [],
  key_differentials: ['STEMI', 'Aortic dissection'],
  critical_actions: [],
  amc_competencies: ['Clinical assessment'],
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  getPersonas.mockResolvedValue(PERSONAS);
  getPersonaDetail.mockResolvedValue(DETAIL);
  createOSCESession.mockResolvedValue({ attempt_id: 'attempt-123' });
});

describe('OSCEPractice', () => {
  it('renders the page heading and loads the persona selector', async () => {
    renderWithProviders(<OSCEPractice />);

    expect(
      screen.getByRole('heading', { name: /OSCE Practice/i })
    ).toBeInTheDocument();
    await waitFor(() =>
      expect(screen.getByLabelText(/Select Patient \(1 available\)/i)).toBeInTheDocument()
    );
  });

  it('shows a loading spinner while personas are fetching', () => {
    getPersonas.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithProviders(<OSCEPractice />);
    expect(screen.getByLabelText('Loading patient personas')).toBeInTheDocument();
  });

  it('shows the empty state when no personas are returned', async () => {
    getPersonas.mockResolvedValue([]);
    renderWithProviders(<OSCEPractice />);
    expect(
      await screen.findByText(/No patient personas found/i)
    ).toBeInTheDocument();
  });

  it('shows an error alert when personas fail to load', async () => {
    getPersonas.mockRejectedValue(new Error('boom'));
    renderWithProviders(<OSCEPractice />);
    expect(
      await screen.findByText(/Failed to load patient personas/i)
    ).toBeInTheDocument();
  });

  it('loads the persona detail after selecting a patient and starts a session', async () => {
    const user = userEvent.setup();
    renderWithProviders(<OSCEPractice />);

    await waitFor(() =>
      expect(screen.getByLabelText(/Select Patient \(1 available\)/i)).toBeInTheDocument()
    );

    // Open the persona selector and choose the patient.
    await user.click(screen.getByLabelText(/Select Patient \(1 available\)/i));
    await user.click(
      await screen.findByRole('option', { name: /John Brown - Central crushing chest pain/i })
    );

    // Detail view renders from the mocked getPersonaDetail response.
    expect(
      await screen.findByRole('heading', { name: 'Patient Details' })
    ).toBeInTheDocument();
    expect(getPersonaDetail).toHaveBeenCalledWith(PERSONA_ID);
    expect(screen.getByText('Doctor, I have terrible chest pain.', { exact: false })).toBeInTheDocument();

    // Start Session -> create session -> navigate.
    await user.click(screen.getByRole('button', { name: /Start Session/i }));

    await waitFor(() =>
      expect(createOSCESession).toHaveBeenCalledWith(PERSONA_ID)
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/osce/session/attempt-123')
    );
  });

  it('has no accessibility violations once the personas have loaded', async () => {
    const { container } = renderWithProviders(<OSCEPractice />);
    await waitFor(() =>
      expect(screen.getByLabelText(/Select Patient \(1 available\)/i)).toBeInTheDocument()
    );
    await expectNoA11yViolations(container);
  });
});
