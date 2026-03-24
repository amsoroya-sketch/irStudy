import { describe, it, expect } from 'vitest';
import { renderHook } from '@testing-library/react';
import { useSM2Algorithm } from '../useSM2Algorithm';

describe('SM-2 Algorithm Calculations', () => {
  // Test 41: Quality 5 ("Perfect") increases ease_factor
  it('should increase ease_factor when quality=5 (Perfect)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 5);

    // EF' = EF + (0.1 - (5-q) * (0.08 + (5-q) * 0.02))
    // EF' = 2.5 + (0.1 - 0 * 0.08) = 2.5 + 0.1 = 2.6
    expect(newParams.ease_factor).toBeCloseTo(2.6, 2);
    expect(newParams.interval_days).toBe(6); // First repetition: 6 days
    expect(newParams.repetitions).toBe(1);
  });

  // Test 42: Quality 4 ("Easy") increases ease_factor slightly
  it('should increase ease_factor slightly when quality=4 (Easy)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 4);

    // EF' = 2.5 + (0.1 - 1 * (0.08 + 1 * 0.02)) = 2.5 + (0.1 - 0.1) = 2.5
    expect(newParams.ease_factor).toBeCloseTo(2.5, 2);
    expect(newParams.interval_days).toBe(6);
    expect(newParams.repetitions).toBe(1);
  });

  // Test 43: Quality 3 ("OK") decreases ease_factor
  it('should decrease ease_factor when quality=3 (OK)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const newParams = result.current.calculateNext(initialParams, 3);

    // EF' = 2.5 + (0.1 - 2 * (0.08 + 2 * 0.02)) = 2.5 + (0.1 - 0.24) = 2.36
    expect(newParams.ease_factor).toBeCloseTo(2.36, 2);
    expect(newParams.interval_days).toBe(6);
    expect(newParams.repetitions).toBe(1);
  });

  // Test 44: Quality 2 ("Hard") resets interval to 1 day
  it('should reset interval to 1 day when quality=2 (Hard)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 6,
      repetitions: 2,
    };

    const newParams = result.current.calculateNext(initialParams, 2);

    // quality < 3: Reset
    expect(newParams.interval_days).toBe(1);
    expect(newParams.repetitions).toBe(0);
    expect(newParams.ease_factor).toBe(2.5); // Unchanged for quality < 3
  });

  // Test 45: Quality 1 ("Wrong") resets repetitions to 0
  it('should reset repetitions to 0 when quality=1 (Wrong)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 6,
      repetitions: 2, // Was on 2nd repetition
    };

    const newParams = result.current.calculateNext(initialParams, 1);

    expect(newParams.ease_factor).toBe(2.5); // Unchanged
    expect(newParams.interval_days).toBe(1); // Reset to 1 day
    expect(newParams.repetitions).toBe(0); // Reset
  });

  // Test 46: Quality 0 ("Blackout") resets and keeps ease_factor unchanged
  it('should reset and keep ease_factor unchanged when quality=0 (Blackout)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 2.5,
      interval_days: 6,
      repetitions: 2,
    };

    const newParams = result.current.calculateNext(initialParams, 0);

    expect(newParams.ease_factor).toBe(2.5); // Unchanged for quality < 3
    expect(newParams.interval_days).toBe(1);
    expect(newParams.repetitions).toBe(0);
  });

  // Test 47: ease_factor floor is 1.3 (never goes below)
  it('should enforce ease_factor floor of 1.3 (never below)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const initialParams = {
      ease_factor: 1.4, // Close to floor
      interval_days: 1,
      repetitions: 0,
    };

    // Quality 3 would normally decrease, but floor is 1.3
    const newParams = result.current.calculateNext(initialParams, 3);

    expect(newParams.ease_factor).toBeGreaterThanOrEqual(1.3);
  });

  // Test 48: Interval progression (1 → 6 → exponential)
  it('should progress intervals correctly (1 → 6 → 15 → 38...)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    // First review (quality 4)
    let params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    params = result.current.calculateNext(params, 4);
    expect(params.interval_days).toBe(6); // First repetition
    expect(params.repetitions).toBe(1);

    // Second review (quality 4)
    params = result.current.calculateNext(params, 4);
    // I(2) = I(1) * EF = 6 * 2.5 = 15 (rounds to 15)
    expect(params.interval_days).toBeCloseTo(15, 0);
    expect(params.repetitions).toBe(2);

    // Third review (quality 4)
    params = result.current.calculateNext(params, 4);
    // I(3) = I(2) * EF = 15 * 2.5 = 37.5 (rounds to 38)
    expect(params.interval_days).toBeCloseTo(38, 0);
    expect(params.repetitions).toBe(3);
  });

  // Test 49: next_review_date calculation (adds interval_days to NOW)
  it('should calculate next_review_date correctly (NOW + interval_days)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const now = new Date();
    const newParams = result.current.calculateNext(params, 4);

    const expectedDate = new Date(now.getTime() + 6 * 24 * 60 * 60 * 1000); // +6 days

    expect(newParams.next_review_date).toBeInstanceOf(Date);
    expect(newParams.next_review_date.getTime()).toBeCloseTo(expectedDate.getTime(), -4); // Allow 10s tolerance
  });

  // Test 50: Handles invalid quality (out of range 0-5)
  it('should throw error for quality <0 or >5', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(params, -1)).toThrow(/quality must be between 0 and 5/i);
    expect(() => result.current.calculateNext(params, 6)).toThrow(/quality must be between 0 and 5/i);
  });

  // Test 51: Handles negative ease_factor (invalid state)
  it('should throw error for negative ease_factor', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: -1.0,
      interval_days: 1,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/ease_factor must be >= 1.3/i);
  });

  // Test 52: Handles zero interval_days (invalid state)
  it('should throw error for interval_days <= 0', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: 2.5,
      interval_days: 0,
      repetitions: 0,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/interval_days must be >= 1/i);
  });

  // Test 53: Handles negative repetitions (invalid state)
  it('should throw error for negative repetitions', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const invalidParams = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: -1,
    };

    expect(() => result.current.calculateNext(invalidParams, 4)).toThrow(/repetitions must be >= 0/i);
  });

  // Test 54: Interval cap (max 365 days for safety)
  it('should cap interval at 365 days (prevent year+ intervals)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    let params = {
      ease_factor: 3.0, // High EF
      interval_days: 200, // Already high
      repetitions: 5,
    };

    // Quality 5 would normally push interval to 600 days
    params = result.current.calculateNext(params, 5);

    expect(params.interval_days).toBeLessThanOrEqual(365);
  });

  // Test 55: Consistency test (same inputs = same outputs)
  it('should return identical results for identical inputs (deterministic)', () => {
    const { result } = renderHook(() => useSM2Algorithm());

    const params = {
      ease_factor: 2.5,
      interval_days: 1,
      repetitions: 0,
    };

    const result1 = result.current.calculateNext(params, 4);
    const result2 = result.current.calculateNext(params, 4);

    expect(result1.ease_factor).toBeCloseTo(result2.ease_factor, 10);
    expect(result1.interval_days).toBe(result2.interval_days);
    expect(result1.repetitions).toBe(result2.repetitions);
  });
});
