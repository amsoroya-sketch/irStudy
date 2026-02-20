/**
 * ExamReadinessGauge Component Tests
 * Tests for the circular exam readiness gauge component
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import ExamReadinessGauge from './ExamReadinessGauge';
import type { ExamReadinessFactors } from '../../utils/examReadiness';

// ── Fixtures ──────────────────────────────────────────────────────────────────
const excellentFactors: ExamReadinessFactors = {
  mcqAccuracyRate: 75,
  osceCompletions: 20,
  studyCardRetentionRate: 100,
  weakAreaCount: 0,
  studyStreakDays: 30,
};

const goodFactors: ExamReadinessFactors = {
  mcqAccuracyRate: 60,
  osceCompletions: 10,
  studyCardRetentionRate: 70,
  weakAreaCount: 1,
  studyStreakDays: 10,
};

const needsWorkFactors: ExamReadinessFactors = {
  mcqAccuracyRate: 30,
  osceCompletions: 2,
  studyCardRetentionRate: 20,
  weakAreaCount: 10, // 10+ weak areas → 0 contribution from weak-areas bucket
  studyStreakDays: 0,
};

// Helper: get score from the gauge (uses "Ready" sibling text)
function getScoreFromGauge(): number {
  const readyText = screen.getByText('Ready');
  const scoreText = readyText.previousSibling?.textContent ?? '0%';
  return parseInt(scoreText);
}

describe('ExamReadinessGauge', () => {
  // ── Rendering ─────────────────────────────────────────────────────────────
  it('renders the component heading', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByText('AMC Exam Readiness')).toBeInTheDocument();
  });

  it('renders "Score Breakdown" section', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByText('Score Breakdown')).toBeInTheDocument();
  });

  it('has accessible region landmark', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByRole('region', { name: /Exam Readiness Gauge/i })).toBeInTheDocument();
  });

  it('renders "Ready" label inside gauge', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByText('Ready')).toBeInTheDocument();
  });

  // ── Score display ─────────────────────────────────────────────────────────
  it('displays 100% for perfect factors', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(getScoreFromGauge()).toBe(100);
  });

  it('displays score in 60-79 range for good factors', () => {
    render(<ExamReadinessGauge factors={goodFactors} />);
    const score = getScoreFromGauge();
    expect(score).toBeGreaterThanOrEqual(60);
    expect(score).toBeLessThan(80);
  });

  it('displays score below 60 for needs-work factors', () => {
    render(<ExamReadinessGauge factors={needsWorkFactors} />);
    const score = getScoreFromGauge();
    expect(score).toBeLessThan(60);
  });

  // ── Grade chip ────────────────────────────────────────────────────────────
  it('shows "Excellent" chip for top score', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByText('Excellent')).toBeInTheDocument();
  });

  it('shows "Good Progress" chip for mid score', () => {
    render(<ExamReadinessGauge factors={goodFactors} />);
    expect(screen.getByText('Good Progress')).toBeInTheDocument();
  });

  it('shows "Needs Work" chip for low score', () => {
    render(<ExamReadinessGauge factors={needsWorkFactors} />);
    expect(screen.getByText('Needs Work')).toBeInTheDocument();
  });

  // ── Factor breakdown labels ───────────────────────────────────────────────
  it('renders all 5 factor labels', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByText('MCQ Accuracy')).toBeInTheDocument();
    expect(screen.getByText('OSCE Completions')).toBeInTheDocument();
    expect(screen.getByText('Study Card Mastery')).toBeInTheDocument();
    expect(screen.getByText('Weak Areas')).toBeInTheDocument();
    expect(screen.getByText('Study Streak')).toBeInTheDocument();
  });

  it('shows actual MCQ accuracy in factor breakdown', () => {
    render(<ExamReadinessGauge factors={{ ...excellentFactors, mcqAccuracyRate: 65 }} />);
    expect(screen.getByText(/65/)).toBeInTheDocument();
  });

  it('shows actual weak areas count in factor breakdown', () => {
    render(<ExamReadinessGauge factors={{ ...excellentFactors, weakAreaCount: 3 }} />);
    expect(screen.getByText(/3 areas/)).toBeInTheDocument();
  });

  // ── Recommendation ────────────────────────────────────────────────────────
  it('displays a recommendation message', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    const statusEl = screen.getByRole('status');
    expect(statusEl.textContent?.length).toBeGreaterThan(10);
  });

  it('recommendation mentions AMC for excellent grade', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    const statusEl = screen.getByRole('status');
    expect(statusEl.textContent).toMatch(/AMC/);
  });

  // ── Accessibility ─────────────────────────────────────────────────────────
  it('info icon has accessible label', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByLabelText('Readiness score information')).toBeInTheDocument();
  });

  it('grade chip has accessible label', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByLabelText('Readiness grade: Excellent')).toBeInTheDocument();
  });

  it('progress bars have accessible labels', () => {
    render(<ExamReadinessGauge factors={excellentFactors} />);
    expect(screen.getByLabelText('MCQ Accuracy progress')).toBeInTheDocument();
    expect(screen.getByLabelText('OSCE Completions progress')).toBeInTheDocument();
    expect(screen.getByLabelText('Study Card Mastery progress')).toBeInTheDocument();
    expect(screen.getByLabelText('Weak Areas progress')).toBeInTheDocument();
    expect(screen.getByLabelText('Study Streak progress')).toBeInTheDocument();
  });

  // ── Edge cases ────────────────────────────────────────────────────────────
  it('renders without studyStreakDays prop (defaults to 0)', () => {
    const factorsNoStreak: ExamReadinessFactors = {
      mcqAccuracyRate: 75,
      osceCompletions: 20,
      studyCardRetentionRate: 100,
      weakAreaCount: 0,
    };
    expect(() => render(<ExamReadinessGauge factors={factorsNoStreak} />)).not.toThrow();
    expect(screen.getByText('Ready')).toBeInTheDocument();
  });

  it('handles all-zero factors without crashing', () => {
    const zeros: ExamReadinessFactors = {
      mcqAccuracyRate: 0,
      osceCompletions: 0,
      studyCardRetentionRate: 0,
      weakAreaCount: 10,
      studyStreakDays: 0,
    };
    expect(() => render(<ExamReadinessGauge factors={zeros} />)).not.toThrow();
    expect(screen.getByText('Needs Work')).toBeInTheDocument();
  });
});
