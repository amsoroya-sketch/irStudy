/**
 * EpicPatientBanner component tests.
 *
 * Verifies the patient region landmark + h2 name, the allergy alert (present vs
 * NKDA), the aria-labelled vital-sign chips, and accessibility.
 */

import { describe, it, expect } from 'vitest';
import {
  renderWithProviders,
  screen,
} from '../../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../../test/axe';
import { EpicPatientBanner } from '../EpicPatientBanner';
import type { MockPatient } from '../../../../types/emr';

const base: MockPatient = {
  id: 'p-1',
  name: 'Jane Doe',
  age: 30,
  gender: 'Female',
  mrn: 'MRN002',
  presenting_complaint: 'Productive cough',
  specialty: 'Respiratory',
};

const withAllergiesAndVitals: MockPatient = {
  ...base,
  allergies: ['Penicillin', 'Sulfur drugs'],
  vital_signs: { bp: '120/80', hr: 88, rr: 18, temp: 37.2, spo2: 97 },
};

describe('EpicPatientBanner', () => {
  it('renders the patient region landmark with the name as an h2', () => {
    renderWithProviders(<EpicPatientBanner patient={base} />);
    expect(
      screen.getByRole('region', { name: 'Patient information banner' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 2, name: 'Jane Doe' })
    ).toBeInTheDocument();
  });

  it('shows an allergy alert when allergies are present', () => {
    renderWithProviders(<EpicPatientBanner patient={withAllergiesAndVitals} />);
    const alert = screen.getByRole('alert');
    expect(alert).toHaveTextContent(/Penicillin/);
    expect(alert).toHaveTextContent(/Sulfur drugs/);
    expect(screen.queryByText(/NKDA/)).not.toBeInTheDocument();
  });

  it('shows NKDA when there are no allergies', () => {
    renderWithProviders(<EpicPatientBanner patient={base} />);
    expect(
      screen.getByText('NKDA (No Known Drug Allergies)')
    ).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });

  it('renders aria-labelled vital-sign chips', () => {
    renderWithProviders(<EpicPatientBanner patient={withAllergiesAndVitals} />);
    expect(screen.getByLabelText('Blood pressure: 120/80')).toBeInTheDocument();
    expect(
      screen.getByLabelText('Heart rate: 88 beats per minute')
    ).toBeInTheDocument();
    expect(
      screen.getByLabelText('Oxygen saturation: 97 percent')
    ).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <EpicPatientBanner patient={withAllergiesAndVitals} />
    );
    await expectNoA11yViolations(container);
  });
});
