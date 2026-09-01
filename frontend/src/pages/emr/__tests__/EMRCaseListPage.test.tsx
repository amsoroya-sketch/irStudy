/**
 * EMRCaseListPage tests (Phase 1b — "pick a case and practice")
 *
 * Verifies the case picker renders cases grouped by specialty with a difficulty
 * chip, and that selecting a case starts a session and navigates.
 */

import { it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import type { EMRCaseListResponse } from '../../../types/emr';

const navigateMock = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual<typeof import('react-router-dom')>(
    'react-router-dom'
  );
  return { ...actual, useNavigate: () => navigateMock };
});

const listEMRCases = vi.fn();
const startEMRSession = vi.fn();
vi.mock('../../../api/emr', () => ({
  listEMRCases: (...args: unknown[]) => listEMRCases(...args),
  startEMRSession: (...args: unknown[]) => startEMRSession(...args),
}));

import EMRCaseListPage from '../EMRCaseListPage';

const CASES: EMRCaseListResponse = {
  total: 2,
  cases: [
    {
      id: 'p-1',
      mrn: 'MRN001',
      name: 'John Smith',
      age: 54,
      gender: 'Male',
      presenting_complaint: 'Central chest pain',
      specialty: 'Cardiology',
      difficulty: 'hard',
    },
    {
      id: 'p-2',
      mrn: 'MRN002',
      name: 'Jane Doe',
      age: 30,
      gender: 'Female',
      presenting_complaint: 'Productive cough',
      specialty: 'Respiratory',
      difficulty: 'easy',
    },
  ],
};

const renderPage = () => {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={['/emr/cases']}>
        <EMRCaseListPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
};

beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
  listEMRCases.mockResolvedValue(CASES);
  startEMRSession.mockResolvedValue({ session_id: 'sess-99' });
});

it('renders cases grouped by specialty with difficulty chips', async () => {
  renderPage();
  await waitFor(() =>
    expect(screen.getByText('John Smith')).toBeInTheDocument()
  );
  expect(screen.getByText('Jane Doe')).toBeInTheDocument();
  // Specialty section headers (also appear as filter option — use heading role)
  expect(
    screen.getByRole('heading', { name: 'Cardiology' })
  ).toBeInTheDocument();
  expect(
    screen.getByRole('heading', { name: 'Respiratory' })
  ).toBeInTheDocument();
  // Difficulty chips
  expect(screen.getByText('hard')).toBeInTheDocument();
  expect(screen.getByText('easy')).toBeInTheDocument();
});

it('starts a session for the chosen case and navigates', async () => {
  const user = userEvent.setup();
  renderPage();
  await waitFor(() =>
    expect(screen.getByText('John Smith')).toBeInTheDocument()
  );

  await user.click(
    screen.getByLabelText(/Practise case: John Smith/i)
  );

  await waitFor(() =>
    expect(startEMRSession).toHaveBeenCalledWith({ patient_id: 'p-1' })
  );
  await waitFor(() =>
    expect(navigateMock).toHaveBeenCalledWith('/emr/select/sess-99')
  );
});

it('starts a random case with no patient_id', async () => {
  const user = userEvent.setup();
  renderPage();
  await waitFor(() =>
    expect(screen.getByText('John Smith')).toBeInTheDocument()
  );

  await user.click(screen.getByRole('button', { name: /random EMR case/i }));

  await waitFor(() =>
    expect(startEMRSession).toHaveBeenCalledWith(undefined)
  );
  await waitFor(() =>
    expect(navigateMock).toHaveBeenCalledWith('/emr/select/sess-99')
  );
});
