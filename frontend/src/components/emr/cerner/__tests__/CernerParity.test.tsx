/**
 * Cerner parity smoke test.
 *
 * The Cerner editor/order panels are theme-agnostic re-exports of the Epic
 * components — assert referential identity so the Epic tests transitively cover
 * Cerner. The chrome components (AppBar / Sidebar / PatientBanner) are distinct
 * and carry Cerner branding — assert their identifying titles/labels render.
 */

import { describe, it, expect, vi } from 'vitest';
import {
  renderWithProviders,
  screen,
} from '../../../../test/renderWithProviders';
import {
  CernerSOAPEditor,
  CernerPrescriptionPanel,
  CernerPathologyPanel,
  CernerImagingPanel,
  CernerAppBar,
  CernerSidebar,
  CernerPatientBanner,
} from '../index';
import { EpicSOAPEditor } from '../../epic/EpicSOAPEditor';
import { EpicPrescriptionPanel } from '../../epic/EpicPrescriptionPanel';
import { EpicPathologyPanel } from '../../epic/EpicPathologyPanel';
import { EpicImagingPanel } from '../../epic/EpicImagingPanel';
import type { MockPatient } from '../../../../types/emr';

const patient: MockPatient = {
  id: 'p-1',
  name: 'John Smith',
  age: 54,
  gender: 'Male',
  mrn: 'MRN001',
  presenting_complaint: 'Central chest pain',
  specialty: 'Cardiology',
};

describe('Cerner parity', () => {
  it('re-exports the Epic editor/order panels (referential identity)', () => {
    expect(CernerSOAPEditor).toBe(EpicSOAPEditor);
    expect(CernerPrescriptionPanel).toBe(EpicPrescriptionPanel);
    expect(CernerPathologyPanel).toBe(EpicPathologyPanel);
    expect(CernerImagingPanel).toBe(EpicImagingPanel);
  });

  it('renders the Cerner PowerChart app bar title', () => {
    renderWithProviders(
      <CernerAppBar
        patient={patient}
        onSave={vi.fn()}
        onSubmit={vi.fn()}
        onExit={vi.fn()}
        autoSaveStatus="idle"
      />
    );
    expect(
      screen.getByRole('heading', { level: 1, name: 'Cerner PowerChart' })
    ).toBeInTheDocument();
  });

  it('renders the Cerner PowerChart navigation landmark', () => {
    renderWithProviders(
      <CernerSidebar activeSection="chart" onSectionChange={vi.fn()} />
    );
    expect(
      screen.getByRole('navigation', { name: 'PowerChart section navigation' })
    ).toBeInTheDocument();
  });

  it('renders the Cerner patient banner', () => {
    renderWithProviders(<CernerPatientBanner patient={patient} />);
    expect(
      screen.getByRole('region', { name: 'Patient information banner' })
    ).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 2, name: 'John Smith' })
    ).toBeInTheDocument();
  });
});
