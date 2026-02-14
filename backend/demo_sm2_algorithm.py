#!/usr/bin/env python3
"""
SM-2 Algorithm Demonstration

Shows how the SuperMemo-2 algorithm schedules study card reviews
based on quality ratings (0-5).
"""

import sys
sys.path.insert(0, '/home/dev/Development/irStudy/backend')

from src.services.sm2_algorithm import SM2Algorithm
from datetime import datetime, timedelta

def print_header(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def print_review(review_num, quality, ease_factor, interval, repetitions, next_date):
    print(f"\n📝 Review {review_num}:")
    print(f"   Quality Rating: {quality} - {SM2Algorithm.get_quality_description(quality)}")
    print(f"   Ease Factor: {ease_factor:.2f}")
    print(f"   Interval: {interval} day(s)")
    print(f"   Repetitions: {repetitions}")
    print(f"   Next Review: {next_date.strftime('%Y-%m-%d')}")

def demo_perfect_reviews():
    """Demonstrate card progression with perfect reviews (quality 5)"""
    print_header("SCENARIO 1: Perfect Reviews (Quality 5)")
    print("Student perfectly recalls card every time")

    # Initial state
    ease_factor = 2.5
    interval = 1
    repetitions = 0
    current_date = datetime.utcnow()

    print(f"\n📌 Starting State:")
    print(f"   Ease Factor: {ease_factor}")
    print(f"   Interval: {interval} day(s)")
    print(f"   Repetitions: {repetitions}")

    # Simulate 5 perfect reviews
    for i in range(1, 6):
        next_date, interval, ease_factor, repetitions = SM2Algorithm.calculate_next_review(
            quality=5,
            current_ease_factor=ease_factor,
            current_interval=interval,
            repetitions=repetitions
        )
        current_date += timedelta(days=interval)
        print_review(i, 5, ease_factor, interval, repetitions, current_date)

def demo_mixed_reviews():
    """Demonstrate card progression with mixed quality reviews"""
    print_header("SCENARIO 2: Mixed Quality Reviews")
    print("Student has varying recall quality")

    # Initial state
    ease_factor = 2.5
    interval = 1
    repetitions = 0
    current_date = datetime.utcnow()

    print(f"\n📌 Starting State:")
    print(f"   Ease Factor: {ease_factor}")
    print(f"   Interval: {interval} day(s)")
    print(f"   Repetitions: {repetitions}")

    # Review sequence: 4 (good), 3 (difficult), 5 (perfect), 4 (good), 2 (failed)
    qualities = [4, 3, 5, 4, 2]

    for i, quality in enumerate(qualities, 1):
        next_date, interval, ease_factor, repetitions = SM2Algorithm.calculate_next_review(
            quality=quality,
            current_ease_factor=ease_factor,
            current_interval=interval,
            repetitions=repetitions
        )
        current_date += timedelta(days=interval)
        print_review(i, quality, ease_factor, interval, repetitions, current_date)

        if quality < 3:
            print("   ⚠️  Card RESET - Quality < 3")

def demo_failed_review():
    """Demonstrate what happens when a student fails a review"""
    print_header("SCENARIO 3: Failed Review (Quality 0)")
    print("Student has complete blackout - card gets reset")

    # Simulate card that was at rep 3 with long interval
    ease_factor = 2.4
    interval = 15  # Was scheduled for 15 days
    repetitions = 3
    current_date = datetime.utcnow()

    print(f"\n📌 Before Failure:")
    print(f"   Ease Factor: {ease_factor}")
    print(f"   Interval: {interval} day(s)")
    print(f"   Repetitions: {repetitions}")
    print(f"   Status: Well-mastered card")

    # Failed review
    next_date, interval, ease_factor, repetitions = SM2Algorithm.calculate_next_review(
        quality=0,
        current_ease_factor=ease_factor,
        current_interval=interval,
        repetitions=repetitions
    )

    print(f"\n❌ After Failure (Quality 0):")
    print(f"   Ease Factor: {ease_factor:.2f} (decreased)")
    print(f"   Interval: {interval} day(s) (RESET to 1)")
    print(f"   Repetitions: {repetitions} (RESET to 0)")
    print(f"   Status: Starting over")
    print(f"\n   💡 The card will be shown again tomorrow")

def demo_quality_scale():
    """Demonstrate the quality rating scale"""
    print_header("SM-2 QUALITY RATING SCALE")

    for quality in range(6):
        desc = SM2Algorithm.get_quality_description(quality)
        if quality < 3:
            result = "❌ FAIL - Card resets to day 1"
        else:
            result = "✅ PASS - Card advances"
        print(f"\n{quality}: {desc}")
        print(f"    → {result}")

def main():
    print("\n" + "=" * 70)
    print("SM-2 SPACED REPETITION ALGORITHM DEMONSTRATION")
    print("irStudy Medical Education Platform")
    print("=" * 70)

    # Run demonstrations
    demo_quality_scale()
    demo_perfect_reviews()
    demo_mixed_reviews()
    demo_failed_review()

    # Summary
    print_header("KEY POINTS")
    print("""
✅ Quality ≥ 3: Card advances to next interval
❌ Quality < 3: Card resets to day 1 (interval = 1, repetitions = 0)

📈 Interval Schedule:
   - Repetition 1: 1 day
   - Repetition 2: 6 days
   - Repetition 3+: previous_interval × ease_factor

🎯 Ease Factor:
   - Range: 1.3 - 2.5
   - Increases with perfect reviews
   - Decreases with difficult reviews
   - Clamped to valid range

📚 Perfect for AMC Clinical Exam preparation!
""")

if __name__ == "__main__":
    main()
