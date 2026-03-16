"""
Test Critical Error Detection

Tests the 25+ critical error rules and auto-fail logic.
"""

import pytest
from unittest.mock import Mock
from typing import Dict, Any, List

# Import with try/except for TDD pattern
try:
    from src.ai.scoring.critical_errors import CriticalErrorDetector
    from src.ai.scoring.error_rules import get_all_rules, get_rule_by_id
except ImportError:
    CriticalErrorDetector = None
    get_all_rules = None
    get_rule_by_id = None


# Fixtures

@pytest.fixture
def detector():
    """Critical error detector instance."""
    if CriticalErrorDetector is None:
        pytest.skip("CriticalErrorDetector not implemented yet")
    return CriticalErrorDetector()


@pytest.fixture
def chest_pain_persona():
    """Patient with chest pain (STEMI scenario)."""
    return {
        "name": "Robert Chen",
        "age": 52,
        "chief_complaint": "Chest pain for 2 hours",
        "key_differentials": ["STEMI", "Unstable angina"],
        "critical_actions": ["ECG within 10 minutes", "Aspirin 300mg"]
    }


@pytest.fixture
def chest_pain_missed_ecg():
    """Transcript where student misses ECG for chest pain (CE001)."""
    return [
        {"role": "student", "message": "Hello, what brings you in today?"},
        {"role": "patient", "message": "I have terrible crushing chest pain for 2 hours."},
        {"role": "student", "message": "That sounds uncomfortable. When did it start?"},
        {"role": "patient", "message": "2 hours ago at work."},
        {"role": "student", "message": "Okay, take some paracetamol and rest at home."},
        {"role": "patient", "message": "That's it? It really hurts."}
    ]


@pytest.fixture
def chest_pain_with_ecg():
    """Transcript where student correctly orders ECG (no CE001)."""
    return [
        {"role": "student", "message": "Hello, what brings you in today?"},
        {"role": "patient", "message": "I have terrible crushing chest pain for 2 hours."},
        {"role": "student", "message": "That's very concerning. I'm ordering an ECG right now."},
        {"role": "patient", "message": "Thank you doctor."},
        {"role": "student", "message": "I'm also giving you aspirin 300mg immediately."}
    ]


@pytest.fixture
def anaphylaxis_transcript():
    """Transcript with anaphylaxis not treated (CE003)."""
    return [
        {"role": "student", "message": "What's wrong?"},
        {"role": "patient", "message": "I have a widespread rash and difficulty breathing after eating peanuts."},
        {"role": "student", "message": "Sounds like an allergy. Take an antihistamine."},
        {"role": "patient", "message": "My throat is closing up!"},
        {"role": "student", "message": "Try to stay calm."}
    ]


@pytest.fixture
def allergy_not_checked():
    """Transcript where student prescribes without checking allergies (CE008)."""
    return [
        {"role": "student", "message": "You have a bacterial infection."},
        {"role": "patient", "message": "Okay."},
        {"role": "student", "message": "I'm prescribing amoxicillin 500mg three times daily."},
        {"role": "patient", "message": "Alright."}
    ]


@pytest.fixture
def allergy_checked():
    """Transcript where student correctly checks allergies."""
    return [
        {"role": "student", "message": "You have a bacterial infection. Do you have any allergies?"},
        {"role": "patient", "message": "No allergies."},
        {"role": "student", "message": "Good. I'm prescribing amoxicillin 500mg three times daily."}
    ]


# Test Classes

class TestCriticalErrorDetector:
    """Test critical error detector initialization and basic functionality."""

    def test_detector_initializes(self, detector):
        """Test detector initializes with all rules."""
        assert detector is not None
        assert len(detector.rules) >= 25  # Should have 25+ rules

    def test_all_rules_loaded(self):
        """Test all 25+ rules are defined."""
        if get_all_rules is None:
            pytest.skip("get_all_rules not implemented yet")

        rules = get_all_rules()
        assert len(rules) >= 25

        # Check key rules exist
        rule_ids = [rule.rule_id for rule in rules]
        assert "CE001" in rule_ids  # Missed chest pain ECG
        assert "CE002" in rule_ids  # Missed stroke
        assert "CE003" in rule_ids  # Missed anaphylaxis
        assert "CE008" in rule_ids  # Allergy not checked
        assert "CE012" in rule_ids  # No CPR in cardiac arrest

    def test_rules_have_required_fields(self):
        """Test all rules have required fields."""
        if get_all_rules is None:
            pytest.skip("get_all_rules not implemented yet")

        rules = get_all_rules()
        for rule in rules:
            assert hasattr(rule, "rule_id")
            assert hasattr(rule, "name")
            assert hasattr(rule, "description")
            assert hasattr(rule, "category")
            assert rule.rule_id.startswith("CE")
            assert len(rule.name) > 0
            assert len(rule.description) > 0


class TestRedFlagDetection:
    """Test detection of missed red flag scenarios."""

    def test_detect_missed_chest_pain_ecg(self, detector, chest_pain_persona, chest_pain_missed_ecg):
        """Test CE001: Missed ECG for chest pain."""
        errors = detector.detect_errors(
            chest_pain_missed_ecg,
            chest_pain_persona
        )

        # Should detect CE001
        assert len(errors) > 0
        ce001_found = any(e["rule_id"] == "CE001" for e in errors)
        assert ce001_found, "CE001 (missed chest pain ECG) should be detected"

        # Check error structure
        ce001 = next(e for e in errors if e["rule_id"] == "CE001")
        assert "name" in ce001
        assert "description" in ce001
        assert "category" in ce001
        assert ce001["category"] == "acute_care"

    def test_no_error_when_ecg_ordered(self, detector, chest_pain_persona, chest_pain_with_ecg):
        """Test CE001 NOT detected when ECG ordered correctly."""
        errors = detector.detect_errors(
            chest_pain_with_ecg,
            chest_pain_persona
        )

        # Should NOT detect CE001
        ce001_found = any(e["rule_id"] == "CE001" for e in errors)
        assert not ce001_found, "CE001 should NOT be detected when ECG ordered"

    def test_detect_missed_anaphylaxis(self, detector, anaphylaxis_transcript):
        """Test CE003: Missed anaphylaxis treatment."""
        persona = {"chief_complaint": "Allergic reaction"}
        errors = detector.detect_errors(
            anaphylaxis_transcript,
            persona
        )

        # Should detect CE003
        ce003_found = any(e["rule_id"] == "CE003" for e in errors)
        assert ce003_found, "CE003 (missed anaphylaxis) should be detected"


class TestMedicationSafety:
    """Test medication safety critical errors."""

    def test_detect_allergy_not_checked(self, detector, allergy_not_checked):
        """Test CE008: Medication prescribed without checking allergies."""
        persona = {"chief_complaint": "Infection"}
        errors = detector.detect_errors(
            allergy_not_checked,
            persona
        )

        # Should detect CE008
        ce008_found = any(e["rule_id"] == "CE008" for e in errors)
        assert ce008_found, "CE008 (allergy not checked) should be detected"

    def test_no_error_when_allergy_checked(self, detector, allergy_checked):
        """Test CE008 NOT detected when allergies checked."""
        persona = {"chief_complaint": "Infection"}
        errors = detector.detect_errors(
            allergy_checked,
            persona
        )

        # Should NOT detect CE008
        ce008_found = any(e["rule_id"] == "CE008" for e in errors)
        assert not ce008_found, "CE008 should NOT be detected when allergies checked"


class TestAutoFailLogic:
    """Test auto-fail logic when critical errors detected."""

    def test_auto_fail_overrides_perfect_score(self, detector, chest_pain_persona, chest_pain_missed_ecg):
        """Test critical error causes auto-fail even with 15/15 score."""
        # Simulate perfect score
        scores = {
            "communication_score": 3,
            "clinical_reasoning_score": 4,
            "information_gathering_score": 4,
            "management_score": 2,
            "professionalism_score": 2,
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": []
        }

        # Detect errors
        errors = detector.detect_errors(
            chest_pain_missed_ecg,
            chest_pain_persona,
            scores
        )

        # Apply auto-fail
        updated_scores = detector.apply_auto_fail(scores, errors)

        # Should override to FAIL
        assert updated_scores["pass_fail"] == "FAIL"
        assert updated_scores["total_score"] == 15  # Score unchanged
        assert len(updated_scores["critical_errors"]) > 0

    def test_no_auto_fail_when_no_errors(self, detector, chest_pain_persona, chest_pain_with_ecg):
        """Test no auto-fail when no critical errors."""
        scores = {
            "communication_score": 3,
            "clinical_reasoning_score": 4,
            "information_gathering_score": 4,
            "management_score": 2,
            "professionalism_score": 2,
            "total_score": 15,
            "pass_fail": "PASS",
            "critical_errors": []
        }

        # Detect errors (should be none)
        errors = detector.detect_errors(
            chest_pain_with_ecg,
            chest_pain_persona,
            scores
        )

        # Apply auto-fail (should have no effect)
        updated_scores = detector.apply_auto_fail(scores, errors)

        # Should remain PASS
        assert updated_scores["pass_fail"] == "PASS"
        assert len(updated_scores["critical_errors"]) == 0


class TestRuleCategories:
    """Test rules cover all major categories."""

    def test_acute_care_rules_exist(self):
        """Test acute care / red flag rules exist."""
        if get_all_rules is None:
            pytest.skip("get_all_rules not implemented yet")

        rules = get_all_rules()
        acute_care_rules = [r for r in rules if r.category == "acute_care"]
        assert len(acute_care_rules) >= 5  # CE001-CE005

    def test_medication_safety_rules_exist(self):
        """Test medication safety rules exist."""
        if get_all_rules is None:
            pytest.skip("get_all_rules not implemented yet")

        rules = get_all_rules()
        med_safety_rules = [r for r in rules if r.category == "medication_safety"]
        assert len(med_safety_rules) >= 5  # CE006-CE010

    def test_professionalism_rules_exist(self):
        """Test professionalism / ethics rules exist."""
        if get_all_rules is None:
            pytest.skip("get_all_rules not implemented yet")

        rules = get_all_rules()
        professionalism_rules = [r for r in rules if r.category == "professionalism"]
        assert len(professionalism_rules) >= 4  # CE016-CE020, CE025


class TestEdgeCases:
    """Test edge cases and false positives."""

    def test_no_false_positives_on_good_session(self, detector, chest_pain_persona, chest_pain_with_ecg):
        """Test no false positives on correctly managed session."""
        errors = detector.detect_errors(
            chest_pain_with_ecg,
            chest_pain_persona
        )

        # Should have zero critical errors
        assert len(errors) == 0, f"False positive: {errors}"

    def test_empty_transcript_no_errors(self, detector):
        """Test empty transcript returns no errors."""
        errors = detector.detect_errors([], {"chief_complaint": "Test"})
        assert len(errors) == 0

    def test_has_critical_errors_helper(self, detector):
        """Test has_critical_errors helper method."""
        assert detector.has_critical_errors([]) == False
        assert detector.has_critical_errors([{"rule_id": "CE001"}]) == True
