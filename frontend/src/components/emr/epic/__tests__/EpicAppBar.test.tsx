/**
 * EpicAppBar component tests.
 *
 * Verifies the banner landmark + h1, the patient context region, the auto-save
 * status chip (role=status) driven by the autoSaveStatus prop, the Save/Submit
 * action callbacks, the Submitting state, the exit control, and accessibility.
 */

import type React from 'react';
import { describe, it, expect, vi } from 'vitest';
import {
  renderWithProviders,
  screen,
  within,
  userEvent,
} from '../../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../../test/axe';
import { EpicAppBar } from '../EpicAppBar';
import type { AutoSaveStatus, MockPatient } from '../../../../types/emr';

const patient: MockPatient = {
  id: 'p-1',
  name: 'John Smith',
  age: 54,
  gender: 'Male',
  mrn: 'MRN001',
  presenting_complaint: 'Central chest pain',
  specialty: 'Cardiology',
};

function setup(
  overrides: Partial<React.ComponentProps<typeof EpicAppBar>> = {}
) {
  const props = {
    patient,
    onSave: vi.fn(),
    onSubmit: vi.fn(),
    onExit: vi.fn(),
    autoSaveStatus: 'idle' as AutoSaveStatus,
    ...overrides,
  };
  return { props, ...renderWithProviders(<EpicAppBar {...props} />) };
}

describe('EpicAppBar', () => {
  it('renders the banner landmark, the Epic EMR h1, and the patient region', () => {
    setup();
    expect(screen.getByRole('banner')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 1, name: 'Epic EMR' })
    ).toBeInTheDocument();
    const region = screen.getByRole('region', { name: 'Current patient' });
    expect(within(region).getByText('John Smith')).toBeInTheDocument();
  });

  it.each<[AutoSaveStatus, string]>([
    ['idle', 'Not saved'],
    ['saving', 'Saving...'],
    ['saved', 'All changes saved'],
    ['error', 'Save failed'],
  ])('shows the "%s" auto-save status as "%s"', (status, label) => {
    setup({ autoSaveStatus: status });
    expect(screen.getByRole('status')).toHaveTextContent(label);
  });

  it('fires onSave when Save Draft is clicked', async () => {
    const user = userEvent.setup();
    const { props } = setup();
    await user.click(screen.getByRole('button', { name: 'Save draft' }));
    expect(props.onSave).toHaveBeenCalledTimes(1);
  });

  it('fires onSubmit when Submit for Review is clicked', async () => {
    const user = userEvent.setup();
    const { props } = setup();
    await user.click(screen.getByRole('button', { name: 'Submit for review' }));
    expect(props.onSubmit).toHaveBeenCalledTimes(1);
  });

  it('reflects the submitting state (label + disabled actions)', () => {
    const { props } = setup({ isSubmitting: true });
    const submit = screen.getByRole('button', { name: 'Submit for review' });
    expect(submit).toHaveTextContent('Submitting...');
    expect(submit).toBeDisabled();
    expect(screen.getByRole('button', { name: 'Save draft' })).toBeDisabled();
    expect(props.onSubmit).not.toHaveBeenCalled();
  });

  it('fires onExit from the exit control', async () => {
    const user = userEvent.setup();
    const { props } = setup();
    await user.click(screen.getByRole('button', { name: 'Exit session' }));
    expect(props.onExit).toHaveBeenCalledTimes(1);
  });

  it('has no accessibility violations', async () => {
    const { container } = setup();
    await expectNoA11yViolations(container);
  });
});
