/**
 * AMCRubricVisualization component tests.
 *
 * Verifies: null render on empty scores; the h6 title; per-category score chips
 * ("{score}/{max}") with aria-labels; progressbars with aria-valuenow/min/max;
 * and the percentage thresholds (red <50%, orange 50-70%, green >=70%) via the
 * rendered percentage + aria-valuenow (colour is theme-driven). Plus a11y.
 */

import { describe, it, expect } from 'vitest';
import {
  renderWithProviders,
  screen,
} from '../../../../test/renderWithProviders';
import { expectNoA11yViolations } from '../../../../test/axe';
import { AMCRubricVisualization } from '../AMCRubricVisualization';
import type { AMCRubricScore } from '../../../../types/emr';

// One category per colour band: 1/3 = 33% (red), 2/3 = 67% (orange),
// 3/3 = 100% (green).
const SCORES: AMCRubricScore[] = [
  { category: 'history_taking', score: 1, max_score: 3, feedback: 'Thin HPI' },
  {
    category: 'clinical_reasoning',
    score: 2,
    max_score: 3,
    feedback: 'Reasonable DDx',
  },
  {
    category: 'patient_safety',
    score: 3,
    max_score: 3,
    feedback: 'No safety gaps',
  },
];

describe('AMCRubricVisualization', () => {
  it('renders nothing when there are no scores', () => {
    const { container } = renderWithProviders(
      <AMCRubricVisualization scores={[]} />
    );
    expect(
      screen.queryByRole('heading', { name: 'AMC Rubric Scores' })
    ).not.toBeInTheDocument();
    expect(container).toBeEmptyDOMElement();
  });

  it('renders the h6 title', () => {
    renderWithProviders(<AMCRubricVisualization scores={SCORES} />);
    expect(
      screen.getByRole('heading', { level: 6, name: 'AMC Rubric Scores' })
    ).toBeInTheDocument();
  });

  it('renders a labelled score chip per category', () => {
    renderWithProviders(<AMCRubricVisualization scores={SCORES} />);
    expect(
      screen.getByLabelText('History Taking score: 1 out of 3')
    ).toHaveTextContent('1/3');
    expect(
      screen.getByLabelText('Clinical Reasoning score: 2 out of 3')
    ).toHaveTextContent('2/3');
    expect(
      screen.getByLabelText('Patient Safety score: 3 out of 3')
    ).toHaveTextContent('3/3');
  });

  it('renders progressbars with aria-valuenow/min/max', () => {
    renderWithProviders(<AMCRubricVisualization scores={SCORES} />);
    const bar = screen.getByRole('progressbar', {
      name: 'Clinical Reasoning score progress bar',
    });
    expect(bar).toHaveAttribute('aria-valuenow', '2');
    expect(bar).toHaveAttribute('aria-valuemin', '0');
    expect(bar).toHaveAttribute('aria-valuemax', '3');
  });

  it('renders the percentage per threshold band (red / orange / green)', () => {
    renderWithProviders(<AMCRubricVisualization scores={SCORES} />);
    // 1/3 -> 33% (red band), 2/3 -> 67% (orange band), 3/3 -> 100% (green band)
    expect(screen.getByText('33%')).toBeInTheDocument();
    expect(screen.getByText('67%')).toBeInTheDocument();
    expect(screen.getByText('100%')).toBeInTheDocument();

    expect(
      screen.getByRole('progressbar', { name: 'History Taking score progress bar' })
    ).toHaveAttribute('aria-valuenow', '1');
    expect(
      screen.getByRole('progressbar', { name: 'Patient Safety score progress bar' })
    ).toHaveAttribute('aria-valuenow', '3');
  });

  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(
      <AMCRubricVisualization scores={SCORES} />
    );
    await expectNoA11yViolations(container);
  });
});
