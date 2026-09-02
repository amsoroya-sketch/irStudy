/**
 * EpicPathologyPanel component tests.
 *
 * Covers: h3 heading + empty state, the required-field disable rule
 * (test_name && indication), adding an order via the onChange contract, the
 * urgency select, the rendered orders table, and accessibility.
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
import { EpicPathologyPanel } from '../EpicPathologyPanel';
import type { PathologyOrderDraft } from '../../../../types/emr';

function Harness({
  onChange,
  initial = [],
}: {
  onChange: (o: PathologyOrderDraft[]) => void;
  initial?: PathologyOrderDraft[];
}) {
  const [orders, setOrders] = useState<PathologyOrderDraft[]>(initial);
  return (
    <EpicPathologyPanel
      pathologyOrders={orders}
      onChange={(o) => {
        onChange(o);
        setOrders(o);
      }}
    />
  );
}

const EXISTING: PathologyOrderDraft = {
  test_name: 'Troponin',
  indication: 'Chest pain',
  urgency: 'urgent',
};

async function selectOption(
  user: ReturnType<typeof userEvent.setup>,
  comboName: string,
  optionName: string
) {
  await user.click(screen.getByRole('combobox', { name: comboName }));
  await user.click(screen.getByRole('option', { name: optionName }));
}

describe('EpicPathologyPanel', () => {
  it('renders the h3 heading and empty state', () => {
    renderWithProviders(<Harness onChange={vi.fn()} />);
    expect(
      screen.getByRole('heading', { level: 3, name: 'Pathology Orders' })
    ).toBeInTheDocument();
    expect(
      screen.getByText('No pathology orders added yet')
    ).toBeInTheDocument();
  });

  it('keeps save disabled until test name and indication are provided', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness onChange={vi.fn()} />);

    await user.click(
      screen.getByRole('button', { name: 'Add new pathology order' })
    );
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    await selectOption(user, 'Test Name', 'Full Blood Count (FBC)');
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeDisabled();

    await user.type(
      screen.getByRole('textbox', { name: 'Clinical Indication' }),
      'Anaemia screen'
    );
    expect(screen.getByRole('button', { name: /^Add$/ })).toBeEnabled();
  });

  it('adds a pathology order (urgency selectable) and lists it', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} />);

    await user.click(
      screen.getByRole('button', { name: 'Add new pathology order' })
    );
    await selectOption(user, 'Test Name', 'Full Blood Count (FBC)');
    await user.type(
      screen.getByRole('textbox', { name: 'Clinical Indication' }),
      'Anaemia screen'
    );
    await selectOption(user, 'Urgency', 'Urgent');
    await user.click(screen.getByRole('button', { name: /^Add$/ }));

    expect(onChange).toHaveBeenCalledWith([
      {
        test_name: 'Full Blood Count (FBC)',
        indication: 'Anaemia screen',
        urgency: 'urgent',
      },
    ]);

    const table = screen.getByRole('table', { name: 'Pathology orders list' });
    expect(within(table).getByText('Full Blood Count (FBC)')).toBeInTheDocument();
  });

  it('deletes a pathology order', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} initial={[EXISTING]} />);

    await user.click(
      screen.getByRole('button', { name: 'Delete pathology order 1' })
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
