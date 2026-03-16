"""
Test Golden Dataset Validation

Tests AI vs human scoring accuracy (±2 marks, ≥90% accuracy).
"""

import pytest
import json
from pathlib import Path
from typing import Dict, Any

# Fixtures

@pytest.fixture
def golden_dataset():
    """Load golden dataset."""
    dataset_path = Path(__file__).parent.parent.parent / "data" / "golden_dataset_scoring.json"

    if not dataset_path.exists():
        pytest.skip("Golden dataset not found")

    with open(dataset_path) as f:
        return json.load(f)


# Test Classes

class TestGoldenDatasetStructure:
    """Test golden dataset file structure and completeness."""

    def test_dataset_exists(self, golden_dataset):
        """Test golden dataset file exists and loads."""
        assert golden_dataset is not None
        assert "scenarios" in golden_dataset
        assert "validation_criteria" in golden_dataset

    def test_dataset_has_20_scenarios(self, golden_dataset):
        """Test dataset has exactly 20 scenarios."""
        scenarios = golden_dataset["scenarios"]
        assert len(scenarios) == 20, f"Expected 20 scenarios, got {len(scenarios)}"

    def test_scenario_distribution(self, golden_dataset):
        """Test correct distribution (5 perfect, 8 passing, 3 borderline, 4 failing)."""
        scenarios = golden_dataset["scenarios"]

        perfect = [s for s in scenarios if s["category"] == "perfect"]
        passing = [s for s in scenarios if s["category"] == "passing"]
        borderline = [s for s in scenarios if s["category"] == "borderline"]
        failing = [s for s in scenarios if s["category"] == "failing"]

        assert len(perfect) == 5, f"Expected 5 perfect, got {len(perfect)}"
        assert len(passing) == 8, f"Expected 8 passing, got {len(passing)}"
        assert len(borderline) == 3, f"Expected 3 borderline, got {len(borderline)}"
        assert len(failing) == 4, f"Expected 4 failing, got {len(failing)}"

    def test_all_scenarios_have_required_fields(self, golden_dataset):
        """Test all scenarios have required fields."""
        scenarios = golden_dataset["scenarios"]

        for scenario in scenarios:
            # Metadata
            assert "scenario_id" in scenario
            assert "category" in scenario
            assert "specialty" in scenario
            assert "chief_complaint" in scenario

            # Expert scores
            assert "expert_scores" in scenario
            scores = scenario["expert_scores"]

            # All 5 domain scores
            assert "communication_score" in scores
            assert "clinical_reasoning_score" in scores
            assert "information_gathering_score" in scores
            assert "management_score" in scores
            assert "professionalism_score" in scores
            assert "total_score" in scores
            assert "pass_fail" in scores

    def test_scores_in_valid_ranges(self, golden_dataset):
        """Test all scores within valid ranges (0-3, 0-4, 0-2, 0-15)."""
        scenarios = golden_dataset["scenarios"]

        for scenario in scenarios:
            scores = scenario["expert_scores"]

            # Check ranges
            assert 0 <= scores["communication_score"] <= 3
            assert 0 <= scores["clinical_reasoning_score"] <= 4
            assert 0 <= scores["information_gathering_score"] <= 4
            assert 0 <= scores["management_score"] <= 2
            assert 0 <= scores["professionalism_score"] <= 2
            assert 0 <= scores["total_score"] <= 15

            # Check total = sum
            expected_total = (
                scores["communication_score"] +
                scores["clinical_reasoning_score"] +
                scores["information_gathering_score"] +
                scores["management_score"] +
                scores["professionalism_score"]
            )
            assert scores["total_score"] == expected_total

    def test_pass_fail_logic(self, golden_dataset):
        """Test pass/fail determination is correct."""
        scenarios = golden_dataset["scenarios"]

        for scenario in scenarios:
            scores = scenario["expert_scores"]
            total = scores["total_score"]
            pass_fail = scores["pass_fail"]

            # PASS: ≥9
            # BORDERLINE: 8
            # FAIL: ≤7
            if total >= 9:
                assert pass_fail == "PASS", f"{scenario['scenario_id']}: {total}/15 should be PASS"
            elif total == 8:
                assert pass_fail == "BORDERLINE", f"{scenario['scenario_id']}: 8/15 should be BORDERLINE"
            else:
                assert pass_fail == "FAIL", f"{scenario['scenario_id']}: {total}/15 should be FAIL"


class TestSpecialtyCoverage:
    """Test dataset covers multiple specialties."""

    def test_multiple_specialties(self, golden_dataset):
        """Test dataset covers 5+ clinical specialties."""
        scenarios = golden_dataset["scenarios"]
        specialties = set(s["specialty"] for s in scenarios)

        assert len(specialties) >= 5, f"Expected 5+ specialties, got {len(specialties)}: {specialties}"

    def test_specialty_distribution(self, golden_dataset):
        """Test no single specialty dominates (max 40% of scenarios)."""
        scenarios = golden_dataset["scenarios"]
        specialty_counts = {}

        for scenario in scenarios:
            specialty = scenario["specialty"]
            specialty_counts[specialty] = specialty_counts.get(specialty, 0) + 1

        max_count = max(specialty_counts.values())
        max_percentage = (max_count / len(scenarios)) * 100

        assert max_percentage <= 40, f"One specialty has {max_percentage:.0f}% of scenarios (max 40%)"


class TestValidationCriteria:
    """Test validation criteria are documented."""

    def test_validation_criteria_exists(self, golden_dataset):
        """Test validation criteria section exists."""
        assert "validation_criteria" in golden_dataset

        criteria = golden_dataset["validation_criteria"]
        assert "ai_vs_human_variance" in criteria
        assert "pass_fail_agreement" in criteria
        assert "total_scenarios" in criteria

    def test_variance_requirement(self, golden_dataset):
        """Test variance requirement is documented (≤2 marks)."""
        criteria = golden_dataset["validation_criteria"]
        assert "≤2" in criteria["ai_vs_human_variance"]

    def test_accuracy_requirement(self, golden_dataset):
        """Test accuracy requirement is documented (≥90%)."""
        criteria = golden_dataset["validation_criteria"]
        agreement = criteria["pass_fail_agreement"]
        assert "90" in agreement or "95" in agreement


class TestPerfectScenarios:
    """Test perfect scenarios (15/15) are realistic."""

    def test_perfect_scenarios_have_max_score(self, golden_dataset):
        """Test all perfect scenarios have 15/15."""
        scenarios = golden_dataset["scenarios"]
        perfect = [s for s in scenarios if s["category"] == "perfect"]

        for scenario in perfect:
            assert scenario["expert_scores"]["total_score"] == 15
            assert scenario["expert_scores"]["pass_fail"] == "PASS"

    def test_perfect_scenarios_have_context(self, golden_dataset):
        """Test perfect scenarios have clinical context."""
        scenarios = golden_dataset["scenarios"]
        perfect = [s for s in scenarios if s["category"] == "perfect"]

        for scenario in perfect:
            assert "notes" in scenario
            assert len(scenario["notes"]) > 20  # Substantive notes


class TestFailingScenarios:
    """Test failing scenarios (≤7/15) are realistic."""

    def test_failing_scenarios_have_low_scores(self, golden_dataset):
        """Test all failing scenarios have ≤7/15."""
        scenarios = golden_dataset["scenarios"]
        failing = [s for s in scenarios if s["category"] == "failing"]

        for scenario in failing:
            assert scenario["expert_scores"]["total_score"] <= 7
            assert scenario["expert_scores"]["pass_fail"] == "FAIL"

    def test_failing_scenarios_have_reasons(self, golden_dataset):
        """Test failing scenarios document failure reasons."""
        scenarios = golden_dataset["scenarios"]
        failing = [s for s in scenarios if s["category"] == "failing"]

        for scenario in failing:
            assert "notes" in scenario
            notes_lower = scenario["notes"].lower()
            # Should mention critical issue
            assert any(kw in notes_lower for kw in ["missed", "critical", "failure", "not recognized", "no"])
