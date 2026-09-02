/**
 * EpicImagingPanel component tests.
 *
 * Parallels EpicPathologyPanel: h3 heading + empty state, the required-field
 * disable rule (imaging_type && indication), adding an order via the onChange
 * contract, the urgency select, the orders table, and accessibility.
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
import { EpicImagingPanel } from '../EpicImagingPanel';
import type { ImagingOrderDraft } from '../../../../types/emr';

function Harness({
  onChange,
  initial = [],
}: {
  onChange: (o: ImagingOrderDraft[]) => void;
  initial?: ImagingOrderDraft[];
}) {
  const [orders, setOrders] = useState<ImagingOrderDraft[]>(initial);
  return (
    <EpicImagingPanel
      imagingOrders={orders}
      onChange={(o) => {
        onChange(o);
        setOrders(o);
      }}
    />
  );
}

const EXISTING: ImagingOrderDraft = {
  imaging_type: 'CT Pulmonary Angiogram (CTPA)',
  indication: 'Exclude PE',
  urgency: 'stat',
};

async function selectOption(
  user: ReturnType<typeof userEvent.setup>,
  comboName: string,
  optionName: string
) {
  await user.click(screen.getByRole('combobox', { name: comboName }));
  await user.click(screen.getByRole('option', { name: optionName }));
}

describe('EpicImagingPanel', () => {
  it('renders the h3 heading and empty state', () => {
    renderWithProviders(<Harness onChange={vi.fn()} />);
    expect(
      screen.getByRole('heading', { level: 3, name: 'Imaging Orders' })
    ).toBeInTheDocument();
    expect(
      screen.getByText('No imaging orders added yet')
    ).toBeInTheDocument();
  });

  it('keeps save disabled until imaging study and indication are provided', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness onChange={vi.fn()} />);

    await user.click(
      screen.getByRole('button', { name: 'Add new imaging order' })
    );
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    await selectOption(user, 'Imaging Study', 'Chest X-ray');
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    await user.type(
      screen.getByRole('textbox', { name: 'Clinical Indication' }),
      'Suspected pneumonia'
    );
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeEnabled();
  });

  it('adds an imaging order and lists it', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} />);

    await user.click(
      screen.getByRole('button', { name: 'Add new imaging order' })
    );
    await selectOption(user, 'Imaging Study', 'Chest X-ray');
    await user.type(
      screen.getByRole('textbox', { name: 'Clinical Indication' }),
      'Suspected pneumonia'
    );
    await user.click(screen.getByRole('button', { name: /^Add$/ }));

    expect(onChange).toHaveBeenCalledWith([
      {
        imaging_type: 'Chest X-ray',
        indication: 'Suspected pneumonia',
        urgency: 'routine',
      },
    ]);

    const table = screen.getByRole('table', { name: 'Imaging orders list' });
    expect(within(table).getByText('Chest X-ray')).toBeInTheDocument();
  });

  it('deletes an imaging order', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} initial={[EXISTING]} />);

    await user.click(
      screen.getByRole('button', { name: 'Delete imaging order 1' })
    );
    expect(onChange).toHaveBeenCalledWith([]);
  });

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <Harness onChange={vi.fn()} initial={[EXISTING]} />
    );
    await expectNoA11yViolations(container);
  });
});
