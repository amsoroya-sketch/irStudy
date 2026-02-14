"""
Direct SM-2 algorithm testing (no FastAPI dependencies)
"""

import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')

from src.services.sm2_algorithm import SM2Algorithm
from datetime import datetime, timedelta

def test_sm2_algorithm_quality_5_perfect():
    """Test SM-2 algorithm with quality 5 (perfect response)"""
    # First review, perfect response
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=5,
        current_ease_factor=2.5,
        current_interval=1,
        repetitions=0
    )

    assert interval == 1  # First review always 1 day
    assert reps == 1  # Incremented
    assert ease_factor > 2.5  # Should increase
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR  # Clamped to max
    print("✅ test_sm2_algorithm_quality_5_perfect PASSED")


def test_sm2_algorithm_quality_3_difficult():
    """Test SM-2 algorithm with quality 3 (correct but difficult)"""
    # Second review, correct but difficult
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=3,
        current_ease_factor=2.5,
        current_interval=1,
        repetitions=1
    )

    assert interval == 6  # Second review is 6 days
    assert reps == 2  # Incremented
    assert ease_factor < 2.5  # Should decrease for quality 3
    print("✅ test_sm2_algorithm_quality_3_difficult PASSED")


def test_sm2_algorithm_quality_0_blackout():
    """Test SM-2 algorithm with quality 0 (complete blackout)"""
    # Failed review - should reset
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=2.6,
        current_interval=6,
        repetitions=2
    )

    assert interval == 1  # Reset to 1 day
    assert reps == 0  # Reset to 0
    assert ease_factor >= SM2Algorithm.MIN_EASE_FACTOR  # Should not go below min
    assert ease_factor < 2.6  # Should decrease
    print("✅ test_sm2_algorithm_quality_0_blackout PASSED")


def test_sm2_algorithm_ease_factor_clamping():
    """Test that ease factor is clamped to 1.3-2.5 range"""
    # Very poor quality should clamp at MIN_EASE_FACTOR
    _, _, ease_factor, _ = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=1.4,
        current_interval=1,
        repetitions=0
    )
    assert ease_factor >= SM2Algorithm.MIN_EASE_FACTOR
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR

    # Perfect quality should clamp at MAX_EASE_FACTOR
    _, _, ease_factor, _ = SM2Algorithm.calculate_next_review(
        quality=5,
        current_ease_factor=2.4,
        current_interval=1,
        repetitions=0
    )
    assert ease_factor <= SM2Algorithm.MAX_EASE_FACTOR
    print("✅ test_sm2_algorithm_ease_factor_clamping PASSED")


def test_sm2_algorithm_third_review():
    """Test SM-2 algorithm for third+ review (interval = previous × EF)"""
    next_date, interval, ease_factor, reps = SM2Algorithm.calculate_next_review(
        quality=4,
        current_ease_factor=2.5,
        current_interval=6,
        repetitions=2
    )

    assert reps == 3  # Third review
    # Interval should be approximately 6 × ease_factor
    assert interval > 6  # Should be greater than previous interval
    assert interval <= 20  # Reasonable upper bound
    print("✅ test_sm2_algorithm_third_review PASSED")


def test_sm2_algorithm_validate_quality():
    """Test quality validation"""
    assert SM2Algorithm.validate_quality(0) is True
    assert SM2Algorithm.validate_quality(5) is True
    assert SM2Algorithm.validate_quality(3) is True
    assert SM2Algorithm.validate_quality(-1) is False
    assert SM2Algorithm.validate_quality(6) is False
    print("✅ test_sm2_algorithm_validate_quality PASSED")


def test_sm2_algorithm_quality_descriptions():
    """Test quality descriptions"""
    assert SM2Algorithm.get_quality_description(0) == "Complete blackout"
    assert SM2Algorithm.get_quality_description(5) == "Perfect response"
    assert SM2Algorithm.get_quality_description(3) == "Correct, but difficult"
    print("✅ test_sm2_algorithm_quality_descriptions PASSED")


if __name__ == "__main__":
    print("=" * 70)
    print("SM-2 ALGORITHM UNIT TESTS")
    print("=" * 70)

    try:
        test_sm2_algorithm_quality_5_perfect()
        test_sm2_algorithm_quality_3_difficult()
        test_sm2_algorithm_quality_0_blackout()
        test_sm2_algorithm_ease_factor_clamping()
        test_sm2_algorithm_third_review()
        test_sm2_algorithm_validate_quality()
        test_sm2_algorithm_quality_descriptions()

        print("\n" + "=" * 70)
        print("✅ ALL SM-2 ALGORITHM TESTS PASSED (7/7)")
        print("=" * 70)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)
