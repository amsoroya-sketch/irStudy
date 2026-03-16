#!/bin/bash
#
# Ralph Loop - PRD_004 Phases 3-6 Implementation
# Confidence Calculation, Feedback Generation, Golden Dataset, Integration
#

set -euo pipefail

PROJECT_ROOT="/home/dev/Development/irStudy"
STATE_FILE="$PROJECT_ROOT/.ralph-loop-state.json"
LOG_FILE="$PROJECT_ROOT/ralph-prd004-phase3-6.log"
BACKEND_DIR="$PROJECT_ROOT/backend"

cd "$PROJECT_ROOT"

echo "===================================================================="
echo "RALPH LOOP - PRD_004 Phases 3-6 (Confidence, Feedback, Dataset, Integration)"
echo "===================================================================="
echo "Started: $(date)"
echo ""

# Update state file - mark Phases 1-2 complete
jq '.prd_004_progress = {
    "phase_1": "COMPLETE (10/10 tests passing)",
    "phase_2": "COMPLETE (16/16 tests passing)",
    "phase_3": "IN_PROGRESS",
    "phase_4": "PENDING",
    "phase_5": "PENDING",
    "phase_6": "PENDING",
    "total_tests": 26,
    "started_phase_3_6": "'$(date -Iseconds)'"
}' "$STATE_FILE" > "$STATE_FILE.tmp" && mv "$STATE_FILE.tmp" "$STATE_FILE"

echo "State updated - Phases 3-6 now active"
echo ""

# PRD_004 Phases 3-6 Implementation Prompt
PROMPT=$(cat <<'ENDPROMPT'
You are implementing PRD_004 Phases 3-6 for the AI OSCE Scoring System.

**CONTEXT:**
- ✅ Phase 1 COMPLETE: Enhanced AI Examiner Rubric (10/10 tests passing)
- ✅ Phase 2 COMPLETE: Critical Error Detection - 25 rules (16/16 tests passing)
- ⏳ Phase 3: Confidence Calculation (NEXT)
- ⏳ Phase 4: Feedback Generation
- ⏳ Phase 5: Golden Dataset
- ⏳ Phase 6: Integration & Testing

**CRITICAL READING:**
1. Read: `/home/dev/Development/irStudy/ai-osce-ralph-prds/PRD_AI_OSCE_004_SCORING_SYSTEM.md` (full spec)
2. Check existing: `backend/src/ai/ai_examiner.py` (main scorer)
3. Check existing: `backend/src/ai/scoring/critical_errors.py` (Phase 2 - reference pattern)
4. Check existing: `backend/tests/test_ai/test_ai_examiner_rubric.py` (Phase 1 tests - reference pattern)
5. Check existing: `backend/tests/test_ai/test_critical_errors.py` (Phase 2 tests - reference pattern)

**OBJECTIVE:**
Implement remaining 4 phases (Confidence, Feedback, Golden Dataset, Integration) with comprehensive testing.

---

## Phase 3: Confidence Calculation (4 hours → ~1.5 hours with TDD)

**Objective**: Calculate scoring confidence (0.0-1.0) based on evidence quality.

**Formula**:
```python
confidence = (evidence_clarity × 0.5) + (score_consistency × 0.4) - (edge_case_penalty × 0.1)
```

**Implementation**:

1. **Create file**: `backend/src/ai/scoring/confidence.py`

```python
"""
Confidence Calculation for AI OSCE Scoring

Calculates scoring confidence (0.0-1.0) based on:
- Evidence clarity (transcript completeness)
- Score consistency (rubric alignment)
- Edge case detection (ambiguous situations)

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class ConfidenceCalculator:
    """
    Calculate confidence in AI scoring decisions.

    Low confidence (< 0.7) → human review recommended
    High confidence (≥ 0.9) → reliable automated scoring
    """

    def __init__(self):
        self.min_confidence = 0.0
        self.max_confidence = 1.0
        self.human_review_threshold = 0.7

    def calculate_confidence(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> float:
        """
        Calculate overall confidence (0.0-1.0).

        Args:
            transcript: Session conversation history
            scores: AI Examiner scores dict
            persona: Patient persona

        Returns:
            float: Confidence score (0.0-1.0)
        """
        # Component 1: Evidence clarity (0.0-1.0)
        evidence_clarity = self._calculate_evidence_clarity(transcript, persona)

        # Component 2: Score consistency (0.0-1.0)
        score_consistency = self._calculate_score_consistency(scores)

        # Component 3: Edge case penalty (0.0-1.0)
        edge_case_penalty = self._detect_edge_cases(transcript, scores, persona)

        # Weighted formula
        confidence = (
            evidence_clarity * 0.5 +
            score_consistency * 0.4 -
            edge_case_penalty * 0.1
        )

        # Clamp to [0.0, 1.0]
        confidence = max(self.min_confidence, min(self.max_confidence, confidence))

        logger.info(
            f"Confidence: {confidence:.2f} "
            f"(evidence={evidence_clarity:.2f}, consistency={score_consistency:.2f}, penalty={edge_case_penalty:.2f})"
        )

        return confidence

    def _calculate_evidence_clarity(
        self,
        transcript: List[Dict[str, str]],
        persona: Dict[str, Any]
    ) -> float:
        """
        Calculate evidence clarity (transcript completeness).

        Factors:
        - Transcript length (longer = more evidence)
        - Student message count (more questions = thorough)
        - Coverage of key domains (history, examination, management)
        """
        if not transcript:
            return 0.0

        total_messages = len(transcript)
        student_messages = [m for m in transcript if m.get("role") == "student"]
        student_count = len(student_messages)

        # Heuristic: Good session has 6-15 student messages
        if student_count < 3:
            length_score = 0.3
        elif student_count < 6:
            length_score = 0.6
        elif student_count <= 15:
            length_score = 1.0
        else:
            length_score = 0.9  # Very long sessions may be rambling

        # Check domain coverage (keywords in student messages)
        student_text = " ".join([m.get("message", "").lower() for m in student_messages])

        history_coverage = any(kw in student_text for kw in ["when", "how long", "history", "symptoms", "started"])
        exam_coverage = any(kw in student_text for kw in ["examine", "check", "vital signs", "look at", "listen"])
        management_coverage = any(kw in student_text for kw in ["treatment", "medication", "prescribe", "tests", "ecg", "blood", "referral"])

        domain_coverage = sum([history_coverage, exam_coverage, management_coverage]) / 3.0

        # Weighted combination
        clarity = (length_score * 0.6) + (domain_coverage * 0.4)

        return clarity

    def _calculate_score_consistency(self, scores: Dict[str, Any]) -> float:
        """
        Calculate score consistency (rubric alignment).

        Factors:
        - Total score matches sum of domains
        - Pass/fail determination aligns with total score
        - Feedback present for all domains
        """
        total_score = scores.get("total_score", 0)

        # Check score matches sum
        expected_total = (
            scores.get("communication_score", 0) +
            scores.get("clinical_reasoning_score", 0) +
            scores.get("information_gathering_score", 0) +
            scores.get("management_score", 0) +
            scores.get("professionalism_score", 0)
        )

        if total_score != expected_total:
            return 0.5  # Inconsistency detected

        # Check pass/fail logic
        pass_fail = scores.get("pass_fail", "")
        critical_errors = scores.get("critical_errors", [])

        if critical_errors and pass_fail != "FAIL":
            return 0.6  # Critical error should force FAIL

        if not critical_errors:
            if total_score >= 9 and pass_fail != "PASS":
                return 0.6
            elif total_score == 8 and pass_fail != "BORDERLINE":
                return 0.6
            elif total_score <= 7 and pass_fail != "FAIL":
                return 0.6

        # Check feedback presence
        feedback_fields = [
            "communication_feedback",
            "clinical_reasoning_feedback",
            "information_gathering_feedback",
            "management_feedback",
            "professionalism_feedback",
            "overall_feedback"
        ]

        feedback_present = sum([
            1 for field in feedback_fields
            if scores.get(field) and len(scores.get(field, "")) > 10
        ])

        feedback_score = feedback_present / len(feedback_fields)

        # All checks passed
        return 0.7 + (feedback_score * 0.3)  # 0.7-1.0 range

    def _detect_edge_cases(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> float:
        """
        Detect edge cases that reduce confidence.

        Edge cases:
        - Very short session (< 5 messages)
        - Borderline score (8/15)
        - Patient didn't disclose key information
        - Ambiguous clinical scenario
        """
        penalty = 0.0

        # Very short session
        if len(transcript) < 5:
            penalty += 0.3

        # Borderline score
        if scores.get("pass_fail") == "BORDERLINE":
            penalty += 0.2

        # Very low scores (< 5/15)
        if scores.get("total_score", 0) < 5:
            penalty += 0.2

        # Missing critical actions (if defined in persona)
        critical_actions = persona.get("critical_actions", [])
        if critical_actions:
            student_text = " ".join([
                m.get("message", "").lower()
                for m in transcript
                if m.get("role") == "student"
            ])

            actions_taken = sum([
                1 for action in critical_actions
                if any(keyword.lower() in student_text for keyword in action.split())
            ])

            if actions_taken < len(critical_actions) * 0.5:  # < 50% of critical actions
                penalty += 0.15

        return min(1.0, penalty)  # Cap at 1.0

    def needs_human_review(self, confidence: float) -> bool:
        """Check if confidence is low enough to warrant human review."""
        return confidence < self.human_review_threshold


def calculate_confidence(
    transcript: List[Dict[str, str]],
    scores: Dict[str, Any],
    persona: Dict[str, Any]
) -> float:
    """
    Convenience function for confidence calculation.

    Returns:
        float: Confidence score (0.0-1.0)
    """
    calculator = ConfidenceCalculator()
    return calculator.calculate_confidence(transcript, scores, persona)
```

2. **Create tests FIRST**: `backend/tests/test_ai/test_confidence.py`

```python
"""
Test Confidence Calculation

Tests confidence scoring (0.0-1.0) based on evidence, consistency, edge cases.
"""

import pytest
from typing import Dict, Any, List

try:
    from src.ai.scoring.confidence import ConfidenceCalculator, calculate_confidence
except ImportError:
    ConfidenceCalculator = None
    calculate_confidence = None


@pytest.fixture
def calculator():
    """Confidence calculator instance."""
    if ConfidenceCalculator is None:
        pytest.skip("ConfidenceCalculator not implemented yet")
    return ConfidenceCalculator()


@pytest.fixture
def high_quality_session():
    """High-quality transcript (should have high confidence)."""
    return [
        {"role": "student", "message": "Good morning. What brings you in today?"},
        {"role": "patient", "message": "I have chest pain."},
        {"role": "student", "message": "When did the pain start?"},
        {"role": "patient", "message": "2 hours ago."},
        {"role": "student", "message": "On a scale of 1-10, how severe?"},
        {"role": "patient", "message": "8 out of 10."},
        {"role": "student", "message": "I'm ordering an ECG and giving you aspirin immediately."},
        {"role": "patient", "message": "Thank you doctor."},
        {"role": "student", "message": "I'm also calling cardiology for urgent review."}
    ]


@pytest.fixture
def low_quality_session():
    """Low-quality transcript (should have low confidence)."""
    return [
        {"role": "student", "message": "Hi."},
        {"role": "patient", "message": "Chest pain."},
        {"role": "student", "message": "Rest."}
    ]


@pytest.fixture
def perfect_scores():
    """Perfect scores (15/15, PASS)."""
    return {
        "communication_score": 3,
        "clinical_reasoning_score": 4,
        "information_gathering_score": 4,
        "management_score": 2,
        "professionalism_score": 2,
        "total_score": 15,
        "pass_fail": "PASS",
        "critical_errors": [],
        "communication_feedback": "Excellent communication",
        "clinical_reasoning_feedback": "Outstanding reasoning",
        "information_gathering_feedback": "Comprehensive history",
        "management_feedback": "Appropriate management",
        "professionalism_feedback": "Professional demeanor",
        "overall_feedback": "Exemplary performance"
    }


@pytest.fixture
def borderline_scores():
    """Borderline scores (8/15, BORDERLINE)."""
    return {
        "communication_score": 2,
        "clinical_reasoning_score": 2,
        "information_gathering_score": 2,
        "management_score": 1,
        "professionalism_score": 1,
        "total_score": 8,
        "pass_fail": "BORDERLINE",
        "critical_errors": [],
        "communication_feedback": "Adequate",
        "clinical_reasoning_feedback": "Basic",
        "information_gathering_feedback": "Minimal",
        "management_feedback": "Acceptable",
        "professionalism_feedback": "Satisfactory",
        "overall_feedback": "Borderline performance"
    }


class TestConfidenceCalculator:
    """Test confidence calculator initialization and basic functionality."""

    def test_calculator_initializes(self, calculator):
        """Test calculator initializes correctly."""
        assert calculator is not None
        assert calculator.min_confidence == 0.0
        assert calculator.max_confidence == 1.0
        assert calculator.human_review_threshold == 0.7

    def test_high_confidence_on_quality_session(
        self,
        calculator,
        high_quality_session,
        perfect_scores
    ):
        """Test high confidence (≥0.9) on high-quality session."""
        persona = {"chief_complaint": "Chest pain"}

        confidence = calculator.calculate_confidence(
            high_quality_session,
            perfect_scores,
            persona
        )

        assert 0.9 <= confidence <= 1.0, f"Expected ≥0.9, got {confidence}"

    def test_low_confidence_on_poor_session(
        self,
        calculator,
        low_quality_session,
        borderline_scores
    ):
        """Test low confidence (<0.7) on poor-quality session."""
        persona = {"chief_complaint": "Chest pain"}

        confidence = calculator.calculate_confidence(
            low_quality_session,
            borderline_scores,
            persona
        )

        assert confidence < 0.7, f"Expected <0.7, got {confidence}"

    def test_confidence_always_in_range(self, calculator):
        """Test confidence always returns 0.0-1.0."""
        # Empty session edge case
        confidence = calculator.calculate_confidence(
            [],
            {"total_score": 0, "pass_fail": "FAIL", "critical_errors": []},
            {}
        )

        assert 0.0 <= confidence <= 1.0

    def test_borderline_score_reduces_confidence(
        self,
        calculator,
        high_quality_session,
        borderline_scores
    ):
        """Test borderline score (8/15) reduces confidence."""
        persona = {"chief_complaint": "Test"}

        confidence = calculator.calculate_confidence(
            high_quality_session,
            borderline_scores,
            persona
        )

        # Borderline adds 0.2 penalty
        assert confidence < 0.9, f"Borderline should reduce confidence, got {confidence}"

    def test_needs_human_review(self, calculator):
        """Test human review threshold (< 0.7)."""
        assert calculator.needs_human_review(0.6) == True
        assert calculator.needs_human_review(0.7) == False
        assert calculator.needs_human_review(0.9) == False

    def test_convenience_function(self, high_quality_session, perfect_scores):
        """Test convenience function calculate_confidence()."""
        if calculate_confidence is None:
            pytest.skip("calculate_confidence not implemented yet")

        persona = {"chief_complaint": "Test"}
        confidence = calculate_confidence(high_quality_session, perfect_scores, persona)

        assert 0.0 <= confidence <= 1.0
```

3. **Run tests (RED phase)**:
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
python -m pytest tests/test_ai/test_confidence.py -v --tb=short
```

Expected: Tests FAIL (not implemented yet)

4. **Implement code (GREEN phase)**: Create `confidence.py` with the implementation above

5. **Run tests (GREEN phase)**:
```bash
python -m pytest tests/test_ai/test_confidence.py -v --tb=short
```

Expected: 7/7 tests PASS

---

## Phase 4: Feedback Generation (4 hours → ~1.5 hours with TDD)

**Objective**: Generate structured feedback (strengths, improvements, narrative).

**Implementation**:

1. **Create file**: `backend/src/ai/scoring/feedback_generator.py`

```python
"""
Feedback Generator for AI OSCE Scoring

Generates structured feedback:
- Strengths (3-5 specific achievements)
- Areas for improvement (2-4 actionable gaps)
- Narrative (100-150 word constructive summary)

SECURITY: No hardcoded credentials
CONTEXT: AMC Clinical Examination
"""

import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class FeedbackGenerator:
    """
    Generate structured feedback for OSCE sessions.

    Feedback is evidence-based (references transcript) and constructive.
    """

    def generate_feedback(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any],
        persona: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate complete feedback package.

        Returns:
            Dict with:
            - strengths: List[str] (3-5 items)
            - areas_for_improvement: List[str] (2-4 items)
            - narrative: str (100-150 words)
        """
        strengths = self.generate_strengths(transcript, scores)
        improvements = self.generate_improvements(transcript, scores)
        narrative = self.generate_narrative(strengths, improvements, scores)

        return {
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "narrative": narrative
        }

    def generate_strengths(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any]
    ) -> List[str]:
        """
        Extract 3-5 specific strengths from high-scoring domains.

        Returns evidence-based strengths (references transcript).
        """
        strengths = []

        # Communication (0-3)
        if scores.get("communication_score", 0) >= 2:
            strengths.append("Demonstrated empathy and active listening skills")

        # Clinical Reasoning (0-4)
        if scores.get("clinical_reasoning_score", 0) >= 3:
            strengths.append("Strong clinical reasoning with appropriate differential diagnosis")

        # Information Gathering (0-4)
        if scores.get("information_gathering_score", 0) >= 3:
            strengths.append("Systematic and comprehensive history taking")

        # Management (0-2)
        if scores.get("management_score", 0) >= 2:
            strengths.append("Evidence-based management plan with appropriate investigations")

        # Professionalism (0-2)
        if scores.get("professionalism_score", 0) >= 2:
            strengths.append("Maintained professionalism and patient-centered approach")

        # Ensure 3-5 strengths
        if len(strengths) < 3:
            strengths.append("Completed the consultation within time constraints")

        return strengths[:5]  # Max 5

    def generate_improvements(
        self,
        transcript: List[Dict[str, str]],
        scores: Dict[str, Any]
    ) -> List[str]:
        """
        Identify 2-4 actionable gaps from low-scoring domains.

        Returns constructive, specific improvements.
        """
        improvements = []

        # Communication (0-3)
        if scores.get("communication_score", 0) < 2:
            improvements.append("Enhance empathy and active listening - use open-ended questions")

        # Clinical Reasoning (0-4)
        if scores.get("clinical_reasoning_score", 0) < 2:
            improvements.append("Develop broader differential diagnosis - consider red flags systematically")

        # Information Gathering (0-4)
        if scores.get("information_gathering_score", 0) < 2:
            improvements.append("Use structured history taking framework (e.g., SOCRATES for pain)")

        # Management (0-2)
        if scores.get("management_score", 0) < 1:
            improvements.append("Formulate evidence-based management plans - include investigations and treatment")

        # Professionalism (0-2)
        if scores.get("professionalism_score", 0) < 1:
            improvements.append("Maintain professional demeanor and patient-centered approach throughout")

        # Critical errors
        if scores.get("critical_errors"):
            improvements.insert(0, "Address critical safety errors - recognize and act on red flags immediately")

        # Ensure 2-4 improvements
        if not improvements:
            improvements.append("Continue developing clinical skills through practice")

        return improvements[:4]  # Max 4

    def generate_narrative(
        self,
        strengths: List[str],
        improvements: List[str],
        scores: Dict[str, Any]
    ) -> str:
        """
        Generate 100-150 word constructive narrative.

        Combines strengths and improvements in growth-oriented tone.
        """
        total_score = scores.get("total_score", 0)
        pass_fail = scores.get("pass_fail", "")

        # Opening
        if pass_fail == "PASS" and total_score >= 12:
            opening = "This was a strong performance demonstrating competence across multiple domains."
        elif pass_fail == "PASS":
            opening = "This session met the minimum standard with areas of competence."
        elif pass_fail == "BORDERLINE":
            opening = "This session showed some competence but requires improvement in key areas."
        else:
            opening = "This session requires significant development to meet clinical standards."

        # Strengths summary
        if strengths:
            strength_text = f" Notable strengths included {strengths[0].lower()}"
            if len(strengths) > 1:
                strength_text += f" and {strengths[1].lower()}"
            strength_text += "."
        else:
            strength_text = ""

        # Improvements summary
        if improvements:
            improve_text = f" To improve, focus on {improvements[0].lower()}"
            if len(improvements) > 1:
                improve_text += f" Additionally, {improvements[1].lower()}"
            improve_text += "."
        else:
            improve_text = ""

        # Closing
        closing = " With targeted practice, clinical competence will continue to develop."

        narrative = opening + strength_text + improve_text + closing

        return narrative


def generate_feedback(
    transcript: List[Dict[str, str]],
    scores: Dict[str, Any],
    persona: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Convenience function for feedback generation.

    Returns:
        Dict with strengths, areas_for_improvement, narrative
    """
    generator = FeedbackGenerator()
    return generator.generate_feedback(transcript, scores, persona)
```

2. **Create tests FIRST**: `backend/tests/test_ai/test_feedback.py`

(Create similar test structure as Phase 3, with 4+ tests covering:
- `test_generate_strengths_high_scores` (high scores → 3-5 strengths)
- `test_generate_improvements_low_scores` (low scores → 2-4 improvements)
- `test_generate_narrative_word_count` (100-150 words)
- `test_evidence_based_feedback` (references scores/transcript))

3. **TDD Cycle**: RED → GREEN → Refactor

---

## Phase 5: Golden Dataset (2 hours → ~1 hour with TDD)

**Objective**: Create 20 sample scenarios for validation (AI vs human ±2 marks, ≥90% accuracy).

**Implementation**:

1. **Create file**: `backend/data/golden_dataset_scoring.json`

Structure (20 scenarios covering):
- 5 perfect sessions (15/15, PASS)
- 8 passing sessions (9-14/15, PASS)
- 3 borderline sessions (8/15, BORDERLINE)
- 4 failing sessions (0-7/15, FAIL)
- Include critical error scenarios
- Multiple specialties (cardiology, neurology, pediatrics, obstetrics, psychiatry)

2. **Create tests**: `backend/tests/test_ai/test_golden_dataset.py`

Tests:
- `test_golden_dataset_exists` (file exists, 20 scenarios)
- `test_ai_vs_human_accuracy` (AI scores ± 2 marks of human scores, ≥90% accuracy)
- `test_pass_fail_agreement` (≥95% agreement on pass/fail)

---

## Phase 6: Integration & Testing (2 hours → ~1 hour with TDD)

**Objective**: Integrate scoring into session finalization via WebSocket.

**Implementation**:

1. **Update**: `backend/src/websocket/session_manager.py`

Add scoring trigger at session end:

```python
async def finalize_session(self, attempt_id: str):
    # Existing finalization logic...

    # NEW: Trigger AI scoring
    from src.ai.ai_examiner import AIExaminerService
    from src.ai.scoring.critical_errors import CriticalErrorDetector
    from src.ai.scoring.confidence import calculate_confidence

    examiner = AIExaminerService()
    detector = CriticalErrorDetector()

    # Get transcript and persona
    transcript = self._get_full_transcript(attempt_id)
    persona = self._get_persona(attempt_id)

    # Score session
    scores = examiner.score_session(persona, transcript)

    # Detect critical errors
    critical_errors = detector.detect_errors(transcript, persona, scores)

    # Apply auto-fail if critical errors
    scores = detector.apply_auto_fail(scores, critical_errors)

    # Calculate confidence
    confidence = calculate_confidence(transcript, scores, persona)

    # Save to database (OSCEScoreAI table)
    await self._save_score(attempt_id, scores, confidence)

    # Broadcast results via WebSocket
    await self._broadcast_results(scores, confidence)
```

2. **Create tests**: `backend/tests/test_ai/test_scoring_integration.py`

Tests:
- `test_end_to_end_scoring_flow` (session → scoring → results)
- `test_score_saved_to_database` (OSCEScoreAI table)
- `test_critical_error_overrides_score` (15/15 but CE → FAIL)
- `test_performance_target` (scoring <5s)

---

**VALIDATION CHECKLIST (CRITICAL - RUN BEFORE REPORTING COMPLETE):**

```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate

# 1. All Phase 3-6 tests pass
python -m pytest tests/test_ai/test_confidence.py -v
python -m pytest tests/test_ai/test_feedback.py -v
python -m pytest tests/test_ai/test_golden_dataset.py -v
python -m pytest tests/test_ai/test_scoring_integration.py -v

# 2. All PRD_004 tests pass (Phases 1-6)
python -m pytest tests/test_ai/test_ai_examiner_rubric.py tests/test_ai/test_critical_errors.py tests/test_ai/test_confidence.py tests/test_ai/test_feedback.py tests/test_ai/test_golden_dataset.py tests/test_ai/test_scoring_integration.py -v

# Expected: ~48+ tests passing (100%)

# 3. No regression in existing tests
python -m pytest tests/test_ai/test_ai_examiner.py -v

# Expected: 11/13 passing (2 pre-existing failures)

# 4. Code coverage ≥70%
python -m pytest tests/test_ai/test_*scoring*.py tests/test_ai/test_confidence.py tests/test_ai/test_feedback.py --cov=src/ai/scoring --cov-report=term

# Expected: ≥70% coverage

# 5. Security scan (zero violations)
grep -r "sk-ant-" src/ai/scoring/ && echo "❌ HARDCODED CREDENTIALS FOUND" || echo "✅ No hardcoded credentials"
grep -r "test-api-key" src/ai/scoring/ && echo "❌ HARDCODED TEST KEY FOUND" || echo "✅ No test keys in production code"

# Expected: ✅ Zero violations

# 6. Golden Dataset validation
python -m pytest tests/test_ai/test_golden_dataset.py::test_ai_vs_human_accuracy -v

# Expected: ≥90% accuracy (AI vs human ±2 marks)

echo "===================================================================="
echo "PRD_004 VALIDATION COMPLETE"
echo "===================================================================="
echo "Expected Results:"
echo "- Phase 3-6 tests: ~22+ tests passing (100%)"
echo "- Combined PRD_004 tests: ~48+ tests passing (100%)"
echo "- No regression: 11/13 existing tests still passing"
echo "- Coverage: ≥70%"
echo "- Security: 0 violations"
echo "- Golden Dataset: ≥90% accuracy"
echo "===================================================================="
```

**CONSTRAINTS:**

1. **TDD MANDATORY**: Write tests FIRST for each phase, confirm FAIL, then implement
2. **Zero hardcoded credentials**: Use Vault via `get_vault_secret()`
3. **Australian Medical Context**: AMC rubric, "paracetamol" not "acetaminophen", emergency 000
4. **Integration**: Update `session_manager.py` to trigger scoring at session end
5. **Performance**: Scoring must complete <5s (p95)

**RETURN FORMAT:**

Report when ALL phases complete with:
1. Summary of files created/modified (list all 10+ files)
2. Test results for each phase (must show 100% pass rate)
3. Combined test results (all PRD_004 tests)
4. Coverage report (must be ≥70%)
5. Security scan results (must be zero violations)
6. Golden Dataset accuracy (must be ≥90%)
7. Integration validation (session_manager.py updated, WebSocket working)
8. Performance metrics (scoring <5s)

BEGIN Phase 3: Confidence Calculation.
Write tests FIRST, confirm they FAIL, then implement.
ENDPROMPT
)

echo "$PROMPT" | claude -p --model claude-sonnet-4-5-20250929 | tee -a "$LOG_FILE"

echo ""
echo "===================================================================="
echo "Ralph PRD_004 Phases 3-6 - Complete"
echo "===================================================================="
echo "Log file: $LOG_FILE"
echo "Check results above"
echo ""
