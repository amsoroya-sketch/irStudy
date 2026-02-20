/**
 * examReadiness Utility Tests
 * Tests for weighted AMC exam readiness algorithm
 */

import { describe, it, expect } from 'vitest';
import {
  calculateExamReadiness,
  getExamReadinessRecommendation,
  type ExamReadinessFactors,
} from './examReadiness';

// ── Base factors fixtures ────────────────────────────────────────────────────
const perfectFactors: ExamReadinessFactors = {
  mcqAccuracyRate: 75,
  osceCompletions: 20,
  studyCardRetentionRate: 100,
  weakAreaCount: 0,
  studyStreakDays: 30,
};

// All-zero with 10 weak areas so weak-areas bucket is also 0
const trueZeroFactors: ExamReadinessFactors = {
  mcqAccuracyRate: 0,
  osceCompletions: 0,
  studyCardRetentionRate: 0,
  weakAreaCount: 10, // 10+ weak areas → 0 contribution from that bucket
  studyStreakDays: 0,
};

// All metrics zero, no weak areas (weak bucket = 10)
const zeroMetricsNoWeak: ExamReadinessFactors = {
  mcqAccuracyRate: 0,
  osceCompletions: 0,
  studyCardRetentionRate: 0,
  weakAreaCount: 0,
  studyStreakDays: 0,
};

describe('calculateExamReadiness', () => {
  // ── Score bounds ────────────────────────────────────────────────────────────
  it('returns 100 for perfect factors', () => {
    const result = calculateExamReadiness(perfectFactors);
    expect(result.score).toBe(100);
  });

  it('returns 0 when all metrics are zero and 10+ weak areas', () => {
    const result = calculateExamReadiness(trueZeroFactors);
    expect(result.score).toBe(0);
  });

  it('weak-areas bucket contributes 10 when weakAreaCount is 0', () => {
    const result = calculateExamReadiness(zeroMetricsNoWeak);
    expect(result.score).toBe(10);
  });

  it('score is always between 0 and 100', () => {
    const extremeFactors: ExamReadinessFactors = {
      mcqAccuracyRate: 200,
      osceCompletions: 999,
      studyCardRetentionRate: 200,
      weakAreaCount: 0,
      studyStreakDays: 999,
    };
    const result = calculateExamReadiness(extremeFactors);
    expect(result.score).toBeGreaterThanOrEqual(0);
    expect(result.score).toBeLessThanOrEqual(100);
  });

  // ── Grade assignment ────────────────────────────────────────────────────────
  it('grades excellent for score >= 80', () => {
    const result = calculateExamReadiness(perfectFactors);
    expect(result.grade).toBe('excellent');
  });

  it('grades good for score 60-79', () => {
    const factors: ExamReadinessFactors = {
      mcqAccuracyRate: 75,
      osceCompletions: 10,
      studyCardRetentionRate: 80,
      weakAreaCount: 0,
      studyStreakDays: 0,
    };
    const result = calculateExamReadiness(factors);
    expect(result.score).toBeGreaterThanOrEqual(60);
    expect(result.score).toBeLessThan(80);
    expect(result.grade).toBe('good');
  });

  it('grades needs_work for score < 60', () => {
    const result = calculateExamReadiness(trueZeroFactors);
    expect(result.grade).toBe('needs_work');
  });

  // ── Individual factor weights ────────────────────────────────────────────────
  // Use trueZeroFactors as base (all contributions = 0) then add one factor
  it('MCQ accuracy contributes 35 points at target (75%)', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      mcqAccuracyRate: 75,
    });
    expect(result.score).toBe(35);
  });

  it('OSCE completions contributes 25 points at target (20 sessions)', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      osceCompletions: 20,
    });
    expect(result.score).toBe(25);
  });

  it('study card mastery contributes 20 points at 100%', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      studyCardRetentionRate: 100,
    });
    expect(result.score).toBe(20);
  });

  it('no weak areas contributes 10 points (full bucket)', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      weakAreaCount: 0,
    });
    expect(result.score).toBe(10);
  });

  it('each weak area reduces weak-areas bucket by 10%', () => {
    const noWeak = calculateExamReadiness({ ...trueZeroFactors, weakAreaCount: 0 });
    const oneWeak = calculateExamReadiness({ ...trueZeroFactors, weakAreaCount: 1 });
    // noWeak=10, oneWeak=(90/100)*10=9 → diff=1
    expect(noWeak.score - oneWeak.score).toBe(1);
  });

  it('10 or more weak areas zeroes weak-areas contribution', () => {
    const result = calculateExamReadiness(trueZeroFactors); // weakAreaCount=10
    expect(result.score).toBe(0);
  });

  it('streak contributes 10 points at 30 days (on top of weak-areas 10)', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      weakAreaCount: 0,       // weak contribution = 10
      studyStreakDays: 30,    // streak contribution = 10
    });
    expect(result.score).toBe(20);
  });

  it('streak defaults to 0 when not provided', () => {
    const factorsNoStreak: ExamReadinessFactors = {
      mcqAccuracyRate: 75,
      osceCompletions: 20,
      studyCardRetentionRate: 100,
      weakAreaCount: 0,
      // no studyStreakDays
    };
    const result = calculateExamReadiness(factorsNoStreak);
    // Without streak (10 points): 35 + 25 + 20 + 10 + 0 = 90
    expect(result.score).toBe(90);
  });

  // ── Factor breakdown array ──────────────────────────────────────────────────
  it('returns 5 factor breakdown items', () => {
    const result = calculateExamReadiness(perfectFactors);
    expect(result.factors).toHaveLength(5);
  });

  it('factor labels are correct', () => {
    const result = calculateExamReadiness(perfectFactors);
    const labels = result.factors.map((f) => f.label);
    expect(labels).toContain('MCQ Accuracy');
    expect(labels).toContain('OSCE Completions');
    expect(labels).toContain('Study Card Mastery');
    expect(labels).toContain('Weak Areas');
    expect(labels).toContain('Study Streak');
  });

  it('MCQ factor has correct actual value', () => {
    const result = calculateExamReadiness({ ...trueZeroFactors, mcqAccuracyRate: 60 });
    const mcqFactor = result.factors.find((f) => f.label === 'MCQ Accuracy');
    expect(mcqFactor?.actual).toBe(60);
    expect(mcqFactor?.target).toBe(75);
    expect(mcqFactor?.unit).toBe('%');
  });

  // ── Recommendation ─────────────────────────────────────────────────────────
  it('includes a non-empty recommendation string', () => {
    const result = calculateExamReadiness(perfectFactors);
    expect(typeof result.recommendation).toBe('string');
    expect(result.recommendation.length).toBeGreaterThan(10);
  });

  // ── Proportional scoring ────────────────────────────────────────────────────
  it('MCQ accuracy at half target gives half MCQ contribution', () => {
    const result = calculateExamReadiness({
      ...trueZeroFactors,
      weakAreaCount: 0,
      mcqAccuracyRate: 37.5, // half of 75
    });
    // MCQ = 0.5 * 35 = ~18, weak = 10 → total = 28
    expect(result.score).toBe(28);
  });
});

describe('getExamReadinessRecommendation', () => {
  it('returns excellent message for score >= 80', () => {
    const msg = getExamReadinessRecommendation(85, perfectFactors);
    expect(msg).toMatch(/[Ee]xcellent/);
    expect(msg).toMatch(/AMC/);
  });

  it('mentions MCQ accuracy when score 60-79 and accuracy below target', () => {
    const factors: ExamReadinessFactors = {
      mcqAccuracyRate: 50,
      osceCompletions: 20,
      studyCardRetentionRate: 80,
      weakAreaCount: 0,
      studyStreakDays: 15,
    };
    const msg = getExamReadinessRecommendation(65, factors);
    expect(msg).toMatch(/MCQ/i);
    expect(msg).toMatch(/50/);
  });

  it('mentions OSCE when score 60-79 and OSCE completions low', () => {
    const factors: ExamReadinessFactors = {
      mcqAccuracyRate: 80,
      osceCompletions: 5,
      studyCardRetentionRate: 90,
      weakAreaCount: 0,
      studyStreakDays: 10,
    };
    const msg = getExamReadinessRecommendation(65, factors);
    expect(msg).toMatch(/OSCE/i);
    expect(msg).toMatch(/5\/20/);
  });

  it('mentions weak areas when score 60-79 and weak areas exist', () => {
    const factors: ExamReadinessFactors = {
      mcqAccuracyRate: 80,
      osceCompletions: 20,
      studyCardRetentionRate: 80,
      weakAreaCount: 3,
      studyStreakDays: 10,
    };
    const msg = getExamReadinessRecommendation(65, factors);
    expect(msg).toMatch(/weak area/i);
    expect(msg).toMatch(/3/);
  });

  it('returns needs-work message for score < 60', () => {
    const msg = getExamReadinessRecommendation(40, trueZeroFactors);
    expect(msg).toMatch(/[Mm]ore practice/);
  });

  it('mentions OSCE priority when score < 60 and very few completions', () => {
    const factors: ExamReadinessFactors = {
      mcqAccuracyRate: 60,
      osceCompletions: 2,
      studyCardRetentionRate: 50,
      weakAreaCount: 1,
      studyStreakDays: 0,
    };
    const msg = getExamReadinessRecommendation(45, factors);
    expect(msg).toMatch(/OSCE/i);
  });
});
