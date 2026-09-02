/**
 * EpicSOAPEditor component tests.
 *
 * Verifies the 4-tab SOAP interface: tab switching reveals the correct panel,
 * typing fires onChange(sectionId, value), the word-count chip updates, the
 * readonly flag disables inputs, and the editor is accessible.
 *
 * Selectors: tabs by role=tab under aria-label="SOAP note sections"; each
 * textarea by aria-label "{Label} section"; word count via the chip's
 * aria-label "Word count: N". Only the ACTIVE tab panel is mounted (the
 * component renders panel children only when value === index).
 */

import { describe, it, expect, vi } from 'vitest';
import { useState } from 'react';
import {
  renderWithProviders,
  screen,
  userEvent,
} from '../../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../../test/axe';
import { EpicSOAPEditor } from '../EpicSOAPEditor';
import type { SOAPNoteDraft } from '../../../../types/emr';

const emptyDraft: SOAPNoteDraft = {
  subjective: '',
  objective: '',
  assessment: '',
  plan: '',
  prescriptions: [],
  pathology_orders: [],
  imaging_orders: [],
};

/**
 * Controlled harness so typing actually updates the draft (the component is
 * fully controlled) — this lets the word-count chip recompute.
 */
function Harness({
  onChange,
  initial = emptyDraft,
  readonly = false,
}: {
  onChange: (field: keyof SOAPNoteDraft, value: string) => void;
  initial?: SOAPNoteDraft;
  readonly?: boolean;
}) {
  const [draft, setDraft] = useState<SOAPNoteDraft>(initial);
  return (
    <EpicSOAPEditor
      sessionId="sess-1"
      draft={draft}
      readonly={readonly}
      onChange={(field, value) => {
        onChange(field, value);
        setDraft((d) => ({ ...d, [field]: value }));
      }}
    />
  );
}

describe('EpicSOAPEditor', () => {
  it('renders four SOAP tabs under the labelled tablist', () => {
    renderWithProviders(<Harness onChange={vi.fn()} />);
    const tablist = screen.getByRole('tablist', { name: 'SOAP note sections' });
    expect(tablist).toBeInTheDocument();
    for (const label of ['Subjective', 'Objective', 'Assessment', 'Plan']) {
      expect(screen.getByRole('tab', { name: label })).toBeInTheDocument();
    }
  });

  it('shows only the Subjective textarea initially and reveals others on tab switch', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness onChange={vi.fn()} />);

    // Only the active panel is mounted.
    expect(
      screen.getByRole('textbox', { name: 'Subjective section' })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('textbox', { name: 'Objective section' })
    ).not.toBeInTheDocument();

    await user.click(screen.getByRole('tab', { name: 'Assessment' }));
    expect(
      screen.getByRole('textbox', { name: 'Assessment section' })
    ).toBeInTheDocument();
    expect(
      screen.queryByRole('textbox', { name: 'Subjective section' })
    ).not.toBeInTheDocument();
  });

  it('fires onChange(sectionId, value) as the user types', async () => {
    const user = userEvent.setup();
    const onChange = vi.fn();
    renderWithProviders(<Harness onChange={onChange} />);

    await user.type(
      screen.getByRole('textbox', { name: 'Subjective section' }),
      'Chest'
    );

    // Every keystroke targets the "subjective" section id.
    expect(onChange).toHaveBeenCalled();
    expect(onChange.mock.calls.every(([field]) => field === 'subjective')).toBe(
      true
    );
    // Last emitted value reflects the accumulated controlled input.
    expect(onChange.mock.calls.at(-1)?.[1]).toBe('Chest');
  });

  it('updates the word-count chip as text is entered', async () => {
    const user = userEvent.setup();
    renderWithProviders(<Harness onChange={vi.fn()} />);

    expect(screen.getByLabelText('Word count: 0')).toBeInTheDocument();

    await user.type(
      screen.getByRole('textbox', { name: 'Subjective section' }),
      'severe central chest pain'
    );

    expect(screen.getByLabelText('Word count: 4')).toBeInTheDocument();
  });

  it('disables the input when readonly', () => {
    renderWithProviders(
      <Harness
        onChange={vi.fn()}
        readonly
        initial={{ ...emptyDraft, subjective: 'Read only note' }}
      />
    );
    expect(
      screen.getByRole('textbox', { name: 'Subjective section' })
    ).toBeDisabled();
  });

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(<Harness onChange={vi.fn()} />);
    await expectNoA11yViolations(container);
  });
});
