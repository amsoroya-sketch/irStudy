/**
 * EpicPrescriptionPanel component tests.
 *
 * Covers: add/edit/delete via the onChange contract, the required-field disable
 * rule on the save button (medication && dose && frequency), the empty state,
 * accessibility, and a regression guard that the stray "SECURITY SCAN
 * EXEMPTION" developer comment is no longer leaked into the visible Alert.
 *
 * MUI fields are queried by role: select triggers are role=combobox (named by
 * their label), text inputs are role=textbox (named by their label).
 */

import { describe, it, expect, vi } from 'vitest';
import { useState } from 'react';
import {
  renderWithProviders,
  screen,
  within,
  userEvent,
} from '../../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../../test/axe';
import { EpicPrescriptionPanel } from '../EpicPrescriptionPanel';
import type { PrescriptionDraft } from '../../../../types/emr';

/** Controlled harness so an added/edited/deleted row is reflected in the list. */
function Harness({
  onChange,
  initial = [],
}: {
  onChange: (p: PrescriptionDraft[]) => void;
  initial?: PrescriptionDraft[];
}) {
  const [rx, setRx] = useState<PrescriptionDraft[]>(initial);
  return (
    <EpicPrescriptionPanel
      prescriptions={rx}
      onChange={(p) => {
        onChange(p);
        setRx(p);
      }}
    />
  );
}

const EXISTING: PrescriptionDraft = {
  medication: 'Amoxicillin 500mg capsules',
  dose: '1 capsule',
  frequency: 'Three times daily',
  route: 'Oral',
  duration: '5 days',
  indication: 'Chest infection',
};

async function selectOption(
  user: ReturnType<typeof userEvent.setup>,
  comboName: string,
  optionName: string
) {
  await user.click(screen.getByRole('combobox', { name: comboName }));
  await user.click(screen.getByRole('option', { name: optionName }));
}

describe('EpicPrescriptionPanel', () => {
  it('renders the h3 heading and empty state', () => {
    renderWithProviders(<Harness onChange={vi.fn()} />);
    expect(
      screen.getByRole('heading', { level: 3, name: 'Prescriptions' })
    ).toBeInTheDocument();
    expect(screen.getByText('No prescriptions added yet')).toBeInTheDocument();
    expect(
      screen.queryByRole('table', { name: 'Prescriptions list' })
    ).not.toBeInTheDocument();
  });

  it('does NOT leak the SECURITY SCAN EXEMPTION developer comment', () => {
    renderWithProviders(<Harness onChange={vi.fn()} />);
    expect(screen.queryByText(/SECURITY SCAN EXEMPTION/i)).not.toBeInTheDocument();
    // The real Alert content is still present.
    expect(
      screen.getByText(/Use Australian PBS medication names/i)
    ).toBeInTheDocument();
  });

  it('toggles the add form and keeps the save button disabled until required fields are set', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness onChange={vi.fn()} />);

    await user.click(screen.getByRole('button', { name: 'Add new prescription' }));

    const save = screen.getByRole('button', { name: /^Add$/ });
    expect(save).toBeDisabled();

    // Medication only -> still disabled.
    await selectOption(user, 'Medication', 'Paracetamol 500mg tablets');
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    // + Dose -> still disabled (frequency missing).
    await user.type(screen.getByRole('textbox', { name: 'Dose' }), '1-2 tablets');
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    // + Frequency -> now enabled.
    await selectOption(user, 'Frequency', 'Every 6 hours');
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeEnabled();
  });

  it('adds a prescription and renders it in the list', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} />);

    await user.click(screen.getByRole('button', { name: 'Add new prescription' }));
    await selectOption(user, 'Medication', 'Paracetamol 500mg tablets');
    await user.type(screen.getByRole('textbox', { name: 'Dose' }), '1-2 tablets');
    await selectOption(user, 'Frequency', 'Every 6 hours');
    await user.click(screen.getByRole('button', { name: /^Add$/ }));

    expect(onChange).toHaveBeenCalledWith([
      {
        medication: 'Paracetamol 500mg tablets',
        dose: '1-2 tablets',
        frequency: 'Every 6 hours',
        route: 'Oral',
        duration: '',
        indication: '',
      },
    ]);

    const table = screen.getByRole('table', { name: 'Prescriptions list' });
    expect(
      within(table).getByText('Paracetamol 500mg tablets')
    ).toBeInTheDocument();
  });

  it('edits an existing prescription', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} initial={[EXISTING]} />);

    await user.click(screen.getByRole('button', { name: 'Edit prescription 1' }));

    const dose = screen.getByRole('textbox', { name: 'Dose' });
    await user.clear(dose);
    await user.type(dose, '2 capsules');
    await user.click(screen.getByRole('button', { name: /^Update$/ }));

    expect(onChange).toHaveBeenCalledWith([
      { ...EXISTING, dose: '2 capsules' },
    ]);
  });

  it('deletes a prescription', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} initial={[EXISTING]} />);

    await user.click(
      screen.getByRole('button', { name: 'Delete prescription 1' })
    );

    expect(onChange).toHaveBeenCalledWith([]);
    expect(screen.getByText('No prescriptions added yet')).toBeInTheDocument();
  });

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <Harness onChange={vi.fn()} initial={[EXISTING]} />
    );
    await expectNoA11yViolations(container);
  });
});
