/**
 * EpicSidebar component tests.
 *
 * Verifies the navigation landmark, the three sections, the active-item
 * aria-current marker, and the onSectionChange callback.
 *
 * Accessibility note: this component has a genuine, pre-existing WCAG failure
 * (axe rule "list" / serious) — MUI <ListItemButton> renders <div>s directly
 * inside the <ul>, so the list contains non-<li> children. Fixing it is out of
 * scope for this test-only task (product source must not be modified beyond the
 * one authorised fix), so instead of asserting zero violations we
 * characterise the KNOWN violation here so it is surfaced, not suppressed.
 * See the returned findings — this should be fixed in the source (wrap each
 * ListItemButton in a ListItem, or set component="li").
 */

import { describe, it, expect, vi } from 'vitest';
import { axe } from 'jest-axe';
import {
  renderWithProviders,
  screen,
  userEvent,
} from '../../../../test/renderWithProviders';
import { EpicSidebar } from '../EpicSidebar';

describe('EpicSidebar', () => {
  it('renders the labelled navigation landmark with three sections', () => {
    renderWithProviders(
      <EpicSidebar activeSection="chart" onSectionChange={vi.fn()} />
    );
    const nav = screen.getByRole('navigation', {
      name: 'EMR section navigation',
    });
    expect(nav).toBeInTheDocument();
    for (const label of ['Chart Review', 'Orders', 'Results']) {
      expect(
        screen.getByRole('button', { name: new RegExp(`^${label}:`) })
      ).toBeInTheDocument();
    }
  });

  it('marks the active section with aria-current="page"', () => {
    renderWithProviders(
      <EpicSidebar activeSection="orders" onSectionChange={vi.fn()} />
    );
    expect(
      screen.getByRole('button', { name: /^Orders:/ })
    ).toHaveAttribute('aria-current', 'page');
    expect(
      screen.getByRole('button', { name: /^Chart Review:/ })
    ).not.toHaveAttribute('aria-current');
  });

  it('fires onSectionChange with the section id when clicked', async () => {
    const user = userEvent.setup();
    const onSectionChange = vi.fn();
    renderWithProviders(
      <EpicSidebar activeSection="chart" onSectionChange={onSectionChange} />
    );
    await user.click(screen.getByRole('button', { name: /^Results:/ }));
    expect(onSectionChange).toHaveBeenCalledWith('results');
  });

  it('has no a11y violations (ListItemButton wrapped in ListItem <li>)', async () => {
    const { container } = renderWithProviders(
      <EpicSidebar activeSection="chart" onSectionChange={vi.fn()} />
    );
    const results = await axe(container);
    // Regression guard: the sidebar previously emitted the axe "list" rule
    // because <ListItemButton> rendered <div>s directly inside <ul>. Fixed by
    // wrapping each button in <ListItem> (a real <li>).
    expect(results.violations.map((v) => v.id)).not.toContain('list');
    expect(results.violations).toHaveLength(0);
  });
});
