"""
SM-2 Spaced Repetition Algorithm Service

Implements the SuperMemo-2 (SM-2) algorithm for optimal study card scheduling.

ALGORITHM:
- Initial ease factor: 2.5
- Ease factor range: 1.3 - 2.5
- Quality ratings: 0 (complete blackout) to 5 (perfect response)
- Interval calculation: I(n) = I(n-1) × EF

QUALITY RATINGS:
- 0: Complete blackout
- 1: Incorrect, but familiar
- 2: Incorrect, but almost correct
- 3: Correct, but difficult
- 4: Correct, after hesitation
- 5: Perfect response

REPETITION SCHEDULE:
- Repetition 1: 1 day
- Repetition 2: 6 days
- Repetition 3+: previous_interval × ease_factor
- Quality < 3: Reset to day 1, reset repetitions

REFERENCES:
- Original SM-2 algorithm: https://www.supermemo.com/en/archives1990-2015/english/ol/sm2
- Australian medical education best practices
"""

from datetime import datetime, timedelta
from typing import Tuple


class SM2Algorithm:
    """
    SuperMemo-2 algorithm for spaced repetition.

    CONSTRAINTS:
    - Ease factor must be between 1.3 and 2.5
    - Quality ratings must be 0-5
    - Intervals increase with successful reviews
    - Failed reviews (quality < 3) reset progress
    """

    MIN_EASE_FACTOR = 1.3
    MAX_EASE_FACTOR = 2.5
    DEFAULT_EASE_FACTOR = 2.5

    @staticmethod
    def calculate_next_review(
        quality: int,
        current_ease_factor: float,
        current_interval: int,
        repetitions: int
    ) -> Tuple[datetime, int, float, int]:
        """
        Calculate next review date and updated SM-2 parameters.

        Args:
            quality: Quality rating 0-5 (0=complete blackout, 5=perfect recall)
            current_ease_factor: Current ease factor (1.3-2.5)
            current_interval: Current interval in days
            repetitions: Number of successful reviews

        Returns:
            Tuple of (next_review_date, interval_days, ease_factor, repetitions)

        Examples:
            # First review, quality 5 (perfect)
            >>> SM2Algorithm.calculate_next_review(5, 2.5, 1, 0)
            (datetime(...), 1, 2.6, 1)

            # Second review, quality 4 (good)
            >>> SM2Algorithm.calculate_next_review(4, 2.6, 1, 1)
            (datetime(...), 6, 2.5, 2)

            # Failed review, quality 2 (reset)
            >>> SM2Algorithm.calculate_next_review(2, 2.5, 6, 2)
            (datetime(...), 1, 2.18, 0)
        """
        # Validate inputs
        if not 0 <= quality <= 5:
            raise ValueError(f"Quality must be 0-5, got {quality}")
        if not SM2Algorithm.MIN_EASE_FACTOR <= current_ease_factor <= 3.0:
            raise ValueError(f"Ease factor must be {SM2Algorithm.MIN_EASE_FACTOR}-3.0, got {current_ease_factor}")
        if current_interval < 1:
            raise ValueError(f"Interval must be >= 1, got {current_interval}")
        if repetitions < 0:
            raise ValueError(f"Repetitions must be >= 0, got {repetitions}")

        # Calculate new ease factor
        # Formula: EF' = EF + (0.1 - (5-q) × (0.08 + (5-q) × 0.02))
        new_ease_factor = current_ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

        # Clamp ease factor to valid range (1.3 - 2.5)
        new_ease_factor = max(SM2Algorithm.MIN_EASE_FACTOR, min(SM2Algorithm.MAX_EASE_FACTOR, new_ease_factor))

        # Determine interval and repetitions based on quality
        if quality < 3:
            # Failed review - reset to beginning
            new_interval = 1
            new_repetitions = 0
        else:
            # Successful review - advance
            new_repetitions = repetitions + 1

            if new_repetitions == 1:
                # First successful review
                new_interval = 1
            elif new_repetitions == 2:
                # Second successful review
                new_interval = 6
            else:
                # Third+ successful review
                # Interval = previous_interval × ease_factor
                new_interval = round(current_interval * new_ease_factor)
                # Ensure minimum interval of 1 day
                new_interval = max(1, new_interval)

        # Calculate next review date
        next_review_date = datetime.utcnow() + timedelta(days=new_interval)

        return next_review_date, new_interval, new_ease_factor, new_repetitions

    @staticmethod
    def validate_quality(quality: int) -> bool:
        """
        Validate quality rating is in valid range.

        Args:
            quality: Quality rating to validate

        Returns:
            True if valid, False otherwise
        """
        return 0 <= quality <= 5

    @staticmethod
    def validate_ease_factor(ease_factor: float) -> bool:
        """
        Validate ease factor is in valid range.

        Args:
            ease_factor: Ease factor to validate

        Returns:
            True if valid, False otherwise
        """
        return SM2Algorithm.MIN_EASE_FACTOR <= ease_factor <= 3.0

    @staticmethod
    def get_quality_description(quality: int) -> str:
        """
        Get human-readable description of quality rating.

        Args:
            quality: Quality rating 0-5

        Returns:
            Description string

        Examples:
            >>> SM2Algorithm.get_quality_description(5)
            'Perfect response'
            >>> SM2Algorithm.get_quality_description(0)
            'Complete blackout'
        """
        descriptions = {
            0: "Complete blackout",
            1: "Incorrect, but familiar",
            2: "Incorrect, but almost correct",
            3: "Correct, but difficult",
            4: "Correct, after hesitation",
            5: "Perfect response"
        }
        return descriptions.get(quality, "Unknown quality")
