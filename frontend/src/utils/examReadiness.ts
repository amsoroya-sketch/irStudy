/**
 * Exam Readiness Algorithm
 * Calculates AMC Clinical Exam readiness score from study metrics
 *
 * Weighted formula:
 *   35% MCQ Accuracy     (target: 75%)
 *   25% OSCE Completions (target: 20)
 *   20% Study Card Mastery
 *   10% Weak Areas Penalty (each weak area -10%)
 *   10% Study Streak Bonus (target: 30 days)
 */

export interface ExamReadinessFactors {
  mcqAccuracyRate: number;       // 0–100
  osceCompletions: number;       // count
  studyCardRetentionRate: number; // 0–100
  weakAreaCount: number;         // count
  studyStreakDays?: number;       // days (optional, defaults to 0)
}

export interface ExamReadinessResult {
  score: number;          // 0–100 rounded to nearest integer
  grade: 'excellent' | 'good' | 'needs_work';
  recommendation: string;
  factors: ExamReadinessFactorBreakdown[];
}

export interface ExamReadinessFactorBreakdown {
  label: string;
  contribution: number;   // points contributed to total (0–100 weight)
  actual: number;
  target: number;
  unit: string;
}

// Targets
const MCQ_TARGET_ACCURACY = 75;    // %
const OSCE_TARGET_COMPLETIONS = 20;
const STREAK_TARGET_DAYS = 30;

/**
 * Calculate weighted exam readiness score (0–100).
 */
export function calculateExamReadiness(factors: ExamReadinessFactors): ExamReadinessResult {
  const {
    mcqAccuracyRate,
    osceCompletions,
    studyCardRetentionRate,
    weakAreaCount,
    studyStreakDays = 0,
  } = factors;

  // ── Factor 1: MCQ Accuracy (35%) ─────────────────────────────────────────
  const mcqRatio = Math.min(mcqAccuracyRate / MCQ_TARGET_ACCURACY, 1);
  const mcqContribution = mcqRatio * 35;

  // ── Factor 2: OSCE Completions (25%) ─────────────────────────────────────
  const osceRatio = Math.min(osceCompletions / OSCE_TARGET_COMPLETIONS, 1);
  const osceContribution = osceRatio * 25;

  // ── Factor 3: Study Card Mastery (20%) ───────────────────────────────────
  const cardContribution = (studyCardRetentionRate / 100) * 20;

  // ── Factor 4: Weak Areas Penalty (10%) ───────────────────────────────────
  // Each weak area reduces the 10-point bucket by 10%; capped at 0
  const weakPenalty = Math.min(weakAreaCount * 10, 100);
  const weakContribution = ((100 - weakPenalty) / 100) * 10;

  // ── Factor 5: Study Streak Bonus (10%) ───────────────────────────────────
  const streakRatio = Math.min(studyStreakDays / STREAK_TARGET_DAYS, 1);
  const streakContribution = streakRatio * 10;

  // ── Total ─────────────────────────────────────────────────────────────────
  const rawScore =
    mcqContribution +
    osceContribution +
    cardContribution +
    weakContribution +
    streakContribution;

  const score = Math.round(Math.min(Math.max(rawScore, 0), 100));

  const grade: ExamReadinessResult['grade'] =
    score >= 80 ? 'excellent' : score >= 60 ? 'good' : 'needs_work';

  return {
    score,
    grade,
    recommendation: getExamReadinessRecommendation(score, factors),
    factors: [
      {
        label: 'MCQ Accuracy',
        contribution: Math.round(mcqContribution),
        actual: Math.round(mcqAccuracyRate * 10) / 10,
        target: MCQ_TARGET_ACCURACY,
        unit: '%',
      },
      {
        label: 'OSCE Completions',
        contribution: Math.round(osceContribution),
        actual: osceCompletions,
        target: OSCE_TARGET_COMPLETIONS,
        unit: ' sessions',
      },
      {
        label: 'Study Card Mastery',
        contribution: Math.round(cardContribution),
        actual: Math.round(studyCardRetentionRate * 10) / 10,
        target: 100,
        unit: '%',
      },
      {
        label: 'Weak Areas',
        contribution: Math.round(weakContribution),
        actual: weakAreaCount,
        target: 0,
        unit: ' areas',
      },
      {
        label: 'Study Streak',
        contribution: Math.round(streakContribution),
        actual: studyStreakDays,
        target: STREAK_TARGET_DAYS,
        unit: ' days',
      },
    ],
  };
}

/**
 * Generate a human-readable recommendation based on score and factors.
 */
export function getExamReadinessRecommendation(
  score: number,
  factors: ExamReadinessFactors
): string {
  const { mcqAccuracyRate, osceCompletions, weakAreaCount } = factors;

  if (score >= 80) {
    return 'Excellent! You are well-prepared for the AMC Clinical Exam. Maintain your study streak and review any remaining weak areas.';
  }

  if (score >= 60) {
    // Identify the weakest factor
    if (mcqAccuracyRate < MCQ_TARGET_ACCURACY) {
      return `Good progress! Focus on improving MCQ accuracy (currently ${mcqAccuracyRate.toFixed(1)}%, target ${MCQ_TARGET_ACCURACY}%) by reviewing weak areas and practicing more questions.`;
    }
    if (osceCompletions < OSCE_TARGET_COMPLETIONS) {
      return `Good progress! Complete more OSCE practice sessions (currently ${osceCompletions}/${OSCE_TARGET_COMPLETIONS}) to build clinical examination confidence.`;
    }
    if (weakAreaCount > 0) {
      return `Good progress! Address your ${weakAreaCount} weak area${weakAreaCount > 1 ? 's' : ''} to boost your readiness score significantly.`;
    }
    return 'Good progress! Focus on your weak areas and maintain a daily study streak to reach exam readiness.';
  }

  // Below 60
  if (mcqAccuracyRate < 50) {
    return 'More practice needed. Start with high-yield MCQs in your weakest specialties and aim for at least 75% accuracy before attempting practice exams.';
  }
  if (osceCompletions < 5) {
    return 'More practice needed. Prioritise OSCE clinical scenarios to build systematic examination skills required for the AMC Clinical Exam.';
  }
  return 'More practice needed. Build a consistent daily study schedule covering both MCQ practice and OSCE scenarios across all 11 AMC specialties.';
}
