/**
 * useSM2Algorithm Hook
 *
 * Implements the SuperMemo-2 (SM-2) spaced repetition algorithm.
 * Used for calculating optimal review intervals for study cards.
 *
 * @see https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
 *
 * Quality Scale:
 * - 0: Complete blackout (no recall)
 * - 1: Incorrect, but recognized answer when shown
 * - 2: Incorrect, but seems easy to remember now
 * - 3: Correct, but required significant difficulty to recall
 * - 4: Correct, recalled with some hesitation
 * - 5: Perfect response, recalled instantly
 */

/**
 * Input parameters for SM-2 calculation
 */
export interface SM2Input {
  /** Current ease factor (difficulty multiplier, ≥1.3) */
  ease_factor: number;
  /** Current interval in days (≥1) */
  interval_days: number;
  /** Current consecutive successful repetitions (≥0) */
  repetitions: number;
}

/**
 * Output parameters from SM-2 calculation
 */
export interface SM2Output {
  /** Updated ease factor */
  ease_factor: number;
  /** Updated interval in days */
  interval_days: number;
  /** Updated repetitions count */
  repetitions: number;
  /** Calculated next review date */
  next_review_date: Date;
}

/**
 * SuperMemo-2 algorithm constants
 */
const SM2_CONSTANTS = {
  /** Minimum allowed ease factor */
  MIN_EASE_FACTOR: 1.3,
  /** Default ease factor for new cards */
  DEFAULT_EASE_FACTOR: 2.5,
  /** First review interval (days) */
  FIRST_INTERVAL: 1,
  /** Second review interval (days) */
  SECOND_INTERVAL: 6,
  /** Maximum interval to prevent year+ reviews (days) */
  MAX_INTERVAL: 365,
  /** Minimum quality for correct response */
  CORRECT_THRESHOLD: 3,
} as const;

/**
 * Custom hook for SM-2 spaced repetition algorithm
 */
export const useSM2Algorithm = () => {
  /**
   * Calculate next review parameters using SM-2 algorithm
   *
   * @param input - Current SM-2 parameters
   * @param quality - Quality rating (0-5)
   * @returns Updated SM-2 parameters with next review date
   * @throws Error if input validation fails
   */
  const calculateNext = (input: SM2Input, quality: number): SM2Output => {
    // Validate inputs
    validateInputs(input, quality);

    const { ease_factor, interval_days, repetitions } = input;

    let new_ease_factor = ease_factor;
    let new_interval = interval_days;
    let new_repetitions = repetitions;

    if (quality >= SM2_CONSTANTS.CORRECT_THRESHOLD) {
      // Correct response (quality 3, 4, 5)

      // Increment repetitions first
      new_repetitions = repetitions + 1;

      // Calculate new interval based on NEW repetition count
      if (new_repetitions === 1) {
        // First successful review: always 6 days
        new_interval = SM2_CONSTANTS.SECOND_INTERVAL;
      } else {
        // Subsequent reviews (n ≥ 2): exponential growth
        // I(n) = round(I(n-1) * EF)
        new_interval = Math.round(interval_days * ease_factor);
      }

      // Calculate new ease factor
      // EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
      const q_diff = 5 - quality;
      new_ease_factor = ease_factor + (0.1 - q_diff * (0.08 + q_diff * 0.02));

      // Enforce minimum ease factor
      new_ease_factor = Math.max(SM2_CONSTANTS.MIN_EASE_FACTOR, new_ease_factor);
    } else {
      // Incorrect response (quality 0, 1, 2)

      // Reset interval to 1 day
      new_interval = SM2_CONSTANTS.FIRST_INTERVAL;

      // Reset repetitions to 0
      new_repetitions = 0;

      // Ease factor remains unchanged for incorrect responses
      new_ease_factor = ease_factor;
    }

    // Cap interval at maximum to prevent year+ reviews
    new_interval = Math.min(new_interval, SM2_CONSTANTS.MAX_INTERVAL);

    // Calculate next review date
    const next_review_date = new Date();
    next_review_date.setDate(next_review_date.getDate() + new_interval);

    return {
      ease_factor: new_ease_factor,
      interval_days: new_interval,
      repetitions: new_repetitions,
      next_review_date,
    };
  };

  return { calculateNext };
};

/**
 * Validate SM-2 input parameters
 *
 * @param input - SM-2 input parameters
 * @param quality - Quality rating
 * @throws Error if validation fails
 */
function validateInputs(input: SM2Input, quality: number): void {
  // Validate quality range (0-5)
  if (quality < 0 || quality > 5) {
    throw new Error('Quality must be between 0 and 5');
  }

  // Validate ease factor
  if (input.ease_factor < SM2_CONSTANTS.MIN_EASE_FACTOR) {
    throw new Error(`Ease_factor must be >= ${SM2_CONSTANTS.MIN_EASE_FACTOR}`);
  }

  // Validate interval
  if (input.interval_days < 1) {
    throw new Error('Interval_days must be >= 1');
  }

  // Validate repetitions
  if (input.repetitions < 0) {
    throw new Error('Repetitions must be >= 0');
  }
}
