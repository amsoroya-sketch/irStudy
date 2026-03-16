"""
TDD Tests for Emotional State Machine
Phase 2: Emotional State System
"""
import pytest
from unittest.mock import Mock, patch

try:
    from src.ai.emotional_state import EmotionalStateMachine
except ImportError:
    EmotionalStateMachine = None

class TestEmotionalStateMachineInitialization:
    def test_state_machine_exists(self):
        if EmotionalStateMachine is None:
            pytest.fail("Not implemented yet (TDD RED)")
        assert EmotionalStateMachine is not None

    def test_initializes_with_baseline_state(self):
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        machine = EmotionalStateMachine()
        assert machine.current_state == "ANXIOUS_GUARDED"
        assert machine.empathy_points == 0


class TestEmpathyDetection:
    """Test suite for empathy marker detection"""

    @pytest.fixture
    def machine(self):
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        return EmotionalStateMachine()

    def test_detects_empathy_phrases(self, machine):
        """Test empathy markers detected in student messages"""
        empathy_phrases = [
            "I understand this must be very frightening",
            "That sounds really concerning",
            "I can imagine how worried you are",
            "This must be difficult for you"
        ]
        
        for phrase in empathy_phrases:
            initial_points = machine.empathy_points
            machine.process_student_message(phrase)
            assert machine.empathy_points > initial_points, f"Failed for: {phrase}"

    def test_detects_dismissive_phrases(self, machine):
        """Test dismissive markers detected (negative points)"""
        dismissive_phrases = [
            "Its probably nothing to worry about",
            "Youre overreacting",
            "That doesnt sound serious"
        ]
        
        for phrase in dismissive_phrases:
            initial_points = machine.empathy_points
            machine.process_student_message(phrase)
            assert machine.empathy_points < initial_points, f"Failed for: {phrase}"

    def test_neutral_message_no_change(self, machine):
        """Test neutral messages dont change empathy"""
        machine.empathy_points = 5
        machine.process_student_message("What medications are you taking?")
        assert machine.empathy_points == 5


class TestStateTransitions:
    """Test suite for state transitions"""

    @pytest.fixture
    def machine(self):
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        return EmotionalStateMachine()

    def test_anxious_to_cautiously_open(self, machine):
        """Test transition from ANXIOUS_GUARDED to CAUTIOUSLY_OPEN"""
        assert machine.current_state == "ANXIOUS_GUARDED"
        
        # Use fewer empathy-rich phrases to reach exactly 3 points
        machine.process_student_message("I understand")
        machine.process_student_message("That sounds concerning")
        machine.process_student_message("I appreciate")
        
        assert machine.current_state == "CAUTIOUSLY_OPEN"
        assert machine.empathy_points >= 3
        assert machine.empathy_points < 6  # Should not reach TRUSTING yet

    def test_cautiously_open_to_trusting(self, machine):
        """Test transition to TRUSTING state"""
        machine.current_state = "CAUTIOUSLY_OPEN"
        machine.empathy_points = 4  # Start closer to threshold
        
        # Need 2 more points to reach 6
        machine.process_student_message("I understand")
        machine.process_student_message("That feels difficult")
        
        assert machine.current_state == "TRUSTING"
        assert machine.empathy_points >= 6

    def test_defensive_on_dismissal(self, machine):
        """Test transition to DEFENSIVE on dismissive language"""
        machine.current_state = "CAUTIOUSLY_OPEN"
        machine.process_student_message("Its probably nothing to worry about")
        assert machine.current_state == "DEFENSIVE"

    def test_withdrawn_on_multiple_dismissals(self, machine):
        """Test transition to WITHDRAWN after repeated dismissals"""
        machine.current_state = "DEFENSIVE"
        machine.empathy_points = -2  # Start at threshold
        
        # Another dismissal → WITHDRAWN (empathy < -2)
        machine.process_student_message("Youre overreacting")
        assert machine.current_state == "WITHDRAWN"
        assert machine.empathy_points < -2


class TestRedisIntegration:
    """Test suite for Redis state persistence"""

    @pytest.fixture
    def mock_redis(self):
        with patch("src.ai.emotional_state.get_redis_client") as mock:
            redis_mock = Mock()
            mock.return_value = redis_mock
            yield redis_mock

    def test_saves_state_to_redis(self, mock_redis):
        """Test state saved to Redis with correct namespace"""
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        
        # Mock Redis returns None (no existing state)
        mock_redis.get_osce.return_value = None
        
        machine = EmotionalStateMachine(session_id="test-session-123")
        machine.process_student_message("I understand")
        
        mock_redis.set_osce.assert_called()
        call_args = mock_redis.set_osce.call_args
        
        assert "test-session-123" in str(call_args)
        assert "emotional_state" in str(call_args)

    def test_loads_state_from_redis(self, mock_redis):
        """Test state loaded from Redis on initialization"""
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        
        mock_redis.get_osce.return_value = {
            "current_state": "CAUTIOUSLY_OPEN",
            "empathy_points": 5
        }
        
        machine = EmotionalStateMachine(session_id="test-session-123")
        assert machine.current_state == "CAUTIOUSLY_OPEN"
        assert machine.empathy_points == 5


class TestTransitionHistory:
    """Test suite for state transition logging"""

    @pytest.fixture
    def machine(self):
        if EmotionalStateMachine is None:
            pytest.skip("Not implemented yet")
        return EmotionalStateMachine()

    def test_logs_state_transitions(self, machine):
        """Test state transitions are logged"""
        for _ in range(3):
            machine.process_student_message("I understand")
        
        assert len(machine.transition_history) > 0
        last_transition = machine.transition_history[-1]
        
        assert "from_state" in last_transition
        assert "to_state" in last_transition
        assert last_transition["to_state"] == "CAUTIOUSLY_OPEN"
