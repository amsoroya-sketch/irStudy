/**
 * EpicEMRPage tests.
 *
 * The page loads a session via axiosInstance.get(/emr/sessions/:id), submits via
 * axiosInstance.post(/emr/sessions/:id/submit) and navigates to the validation
 * page on success. We mock axiosInstance (get/post/put — put is used by the
 * useAutoSave hook) and react-router's useNavigate.
 *
 * Covers: loading spinner, load error, no-patient warning, sidebar section
 * switching (Chart -> ScenarioBrief + SOAP; Orders -> the 3 order panels;
 * Results -> honest empty state), submit -> navigate, and a11y of the loaded
 * chart working area (the sidebar has a known, separate "list" violation, so
 * a11y is scoped to the main content column).
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';

const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return { ...actual, useNavigate: () => navigateMock };
});

const get = vi.fn();
const post = vi.fn();
const put = vi.fn();
vi.mock('../../../utils/axiosInstance', () => ({
  default: {
    get: (...a: unknown[]) => get(...a),
    post: (...a: unknown[]) => post(...a),
    put: (...a: unknown[]) => put(...a),
  },
}));

import {
  renderWithProviders,
  screen,
  within,
  waitFor,
  userEvent,
} from '../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../test/axe';
import EpicEMRPage from '../EpicEMRPage';
import type { EMRSession } from '../../../types/emr';

const SESSION: EMRSession = {
  session_id: 'sess-1',
  patient: {
    id: 'p-1',
    name: 'John Smith',
    age: 54,
    gender: 'Male',
    mrn: 'MRN001',
    presenting_complaint: 'Central chest pain radiating to the left arm',
    specialty: 'Cardiology',
    difficulty: 'hard',
    allergies: ['Penicillin'],
    vital_signs: { bp: '150/95', hr: 96, rr: 20, temp: 37, spo2: 96 },
    validation_criteria: {
      task: 'Document your assessment and initial management for this patient.',
    },
  },
  specialty: 'Cardiology',
  difficulty: 'hard',
  started_at: '2026-09-01T10:00:00Z',
  elapsed_time_seconds: 0,
  status: 'in_progress',
  auto_save_count: 0,
};

const renderPage = () =>
  renderWithProviders(<EpicEMRPage />, {
    path: '/emr/epic/:sessionId',
    route: '/emr/epic/sess-1',
    authed: true,
  });

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  post.mockResolvedValue({ data: {} });
  put.mockResolvedValue({ data: {} });
});

describe('EpicEMRPage', () => {
  it('shows a loading spinner while the session loads', () => {
    get.mockReturnValue(new Promise(() => {}));
    renderPage();
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('shows an error alert when the session fails to load', async () => {
    get.mockRejectedValue(new Error('network down'));
    renderPage();
    expect(
      await screen.findByText(/Failed to load EMR session/i)
    ).toBeInTheDocument();
  });

  it('warns when the session has no patient data', async () => {
    get.mockResolvedValue({ data: { session_id: 'sess-1' } });
    renderPage();
    expect(
      await screen.findByText('Loading patient data...')
    ).toBeInTheDocument();
  });

  it('renders the Chart view with the scenario brief and SOAP editor', async () => {
    get.mockResolvedValue({ data: SESSION });
    renderPage();

    expect(
      await screen.findByRole('heading', { name: 'Clinical Scenario' })
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Central chest pain radiating to the left arm/)
    ).toBeInTheDocument();
    expect(
      screen.getByRole('tablist', { name: 'SOAP note sections' })
    ).toBeInTheDocument();
  });

  it('switches to the Orders view and shows the three order panels', async () => {
    const user = userEvent.setup();
    get.mockResolvedValue({ data: SESSION });
    renderPage();
    await screen.findByRole('heading', { name: 'Clinical Scenario' });

    await user.click(screen.getByRole('button', { name: /^Orders:/ }));

    expect(
      screen.getByRole('heading', { level: 3, name: 'Prescriptions' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: 'Pathology Orders' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 3, name: 'Imaging Orders' })
    ).toBeInTheDocument();
  });

  it('switches to the Results view and shows the honest empty state', async () => {
    const user = userEvent.setup();
    get.mockResolvedValue({ data: SESSION });
    renderPage();
    await screen.findByRole('heading', { name: 'Clinical Scenario' });

    await user.click(screen.getByRole('button', { name: /^Results:/ }));

    expect(
      screen.getByText(/No investigation results are available/i)
    ).toBeInTheDocument();
  });

  it('submits the session and navigates to the validation page', async () => {
    const user = userEvent.setup();
    get.mockResolvedValue({ data: SESSION });
    renderPage();
    await screen.findByRole('heading', { name: 'Clinical Scenario' });

    await user.click(screen.getByRole('button', { name: 'Submit for review' }));

    await waitFor(() =>
      expect(post).toHaveBeenCalledWith(
        '/emr/sessions/sess-1/submit',
        expect.objectContaining({ session_data: expect.any(Object) })
      )
    );
    await waitFor(() =>
      expect(navigateMock).toHaveBeenCalledWith('/emr/validation/sess-1')
    );
  });

  it('has no accessibility violations in the loaded chart working area', async () => {
    get.mockResolvedValue({ data: SESSION });
    renderPage();
    await screen.findByRole('heading', { name: 'Clinical Scenario' });

    // Scope to the main content column (excludes the sidebar, which has a
    // separate, documented "list" violation tracked in EpicSidebar.test.tsx).
    const contentColumn = screen.getByRole('banner').parentElement as HTMLElement;
    expect(contentColumn).not.toBeNull();
    // Sanity-check the scope really is the working area (banner + SOAP editor).
    expect(
      within(contentColumn).getByRole('tablist', { name: 'SOAP note sections' })
    ).toBeInTheDocument();
    await expectNoA11yViolations(contentColumn);
  });
});
