"""
Emotional State Machine for AI Patient
Tracks emotional progression based on student communication

5 States:
- ANXIOUS_GUARDED (initial)
- CAUTIOUSLY_OPEN
- TRUSTING
- DEFENSIVE
- WITHDRAWN

Transitions triggered by empathy points from NLP analysis
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

from src.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class EmotionalStateMachine:
    """
    Emotional state machine for AI Patient.
    
    Tracks empathy from student messages and transitions between
    emotional states based on thresholds.
    """
    
    # Valid states
    STATES = [
        "ANXIOUS_GUARDED",
        "CAUTIOUSLY_OPEN",
        "TRUSTING",
        "DEFENSIVE",
        "WITHDRAWN"
    ]
    
    # Empathy thresholds for state transitions
    EMPATHY_THRESHOLDS = {
        "ANXIOUS_GUARDED": 3,  # Need 3 points to advance
        "CAUTIOUSLY_OPEN": 6,  # Need 6 total points to advance
    }
    
    # Empathy marker keywords
    EMPATHY_PHRASES = [
        "understand", "frightening", "concerning", "worried",
        "difficult", "hard", "imagine", "must be",
        "sounds", "feel", "appreciate", "thank you"
    ]
    
    # Dismissive marker keywords (negative empathy)
    DISMISSIVE_PHRASES = [
        "probably nothing", "overreacting", "not serious",
        "dont worry", "doesnt sound", "fine", "no big deal"
    ]
    
    def __init__(
        self,
        baseline_state: str = "ANXIOUS_GUARDED",
        session_id: Optional[str] = None
    ):
        """
        Initialize emotional state machine.
        
        Args:
            baseline_state: Initial emotional state
            session_id: OSCE session ID (for Redis persistence)
        """
        self.current_state = baseline_state
        self.empathy_points = 0
        self.session_id = session_id
        self.transition_history: List[Dict[str, Any]] = []
        
        # Load existing state from Redis if session_id provided
        if session_id:
            self._load_from_redis()
    
    def process_student_message(self, message: str) -> str:
        """
        Process student message, detect empathy, update state.
        
        Args:
            message: Students message text
        
        Returns:
            New emotional state
        """
        message_lower = message.lower()
        
        # 1. Detect empathy markers
        empathy_delta = self._detect_empathy(message_lower)
        self.empathy_points += empathy_delta
        
        # 2. Check for state transitions
        previous_state = self.current_state
        self._update_state()
        
        # 3. Log transition if state changed
        if previous_state != self.current_state:
            self._log_transition(previous_state, self.current_state)
            logger.info(
                f"Emotional state transition: {previous_state} → {self.current_state} "
                f"(empathy: {self.empathy_points})"
            )
        
        # 4. Save to Redis if session active
        if self.session_id:
            self._save_to_redis()
        
        return self.current_state
    
    def _detect_empathy(self, message: str) -> int:
        """
        Detect empathy markers in message.
        
        Args:
            message: Student message (lowercase)
        
        Returns:
            Empathy points change (positive or negative)
        """
        empathy_count = 0
        dismissive_count = 0
        
        # Check for empathy phrases
        for phrase in self.EMPATHY_PHRASES:
            if phrase in message:
                empathy_count += 1
        
        # Check for dismissive phrases
        for phrase in self.DISMISSIVE_PHRASES:
            if phrase in message:
                dismissive_count += 1
        
        # Calculate net empathy change
        return empathy_count - dismissive_count
    
    def _update_state(self):
        """Update emotional state based on empathy points."""
        # Transition rules
        if self.current_state == "ANXIOUS_GUARDED":
            if self.empathy_points >= self.EMPATHY_THRESHOLDS["ANXIOUS_GUARDED"]:
                self.current_state = "CAUTIOUSLY_OPEN"
            elif self.empathy_points < 0:
                self.current_state = "WITHDRAWN"
        
        elif self.current_state == "CAUTIOUSLY_OPEN":
            if self.empathy_points >= self.EMPATHY_THRESHOLDS["CAUTIOUSLY_OPEN"]:
                self.current_state = "TRUSTING"
            elif self.empathy_points < 0:
                self.current_state = "DEFENSIVE"
        
        elif self.current_state == "TRUSTING":
            if self.empathy_points < 0:
                self.current_state = "WITHDRAWN"
        
        elif self.current_state == "DEFENSIVE":
            if self.empathy_points < -2:
                self.current_state = "WITHDRAWN"
            elif self.empathy_points >= 3:
                # Recovery possible with strong empathy
                self.current_state = "CAUTIOUSLY_OPEN"
        
        elif self.current_state == "WITHDRAWN":
            # Very difficult to recover
            if self.empathy_points >= 5:
                self.current_state = "CAUTIOUSLY_OPEN"
    
    def _log_transition(self, from_state: str, to_state: str):
        """Log state transition to history."""
        self.transition_history.append({
            "from_state": from_state,
            "to_state": to_state,
            "empathy_points": self.empathy_points,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    def _save_to_redis(self):
        """Save current state to Redis (OSCE namespace)."""
        try:
            redis_client = get_redis_client()
            
            state_data = {
                "current_state": self.current_state,
                "empathy_points": self.empathy_points,
                "transition_history": self.transition_history
            }
            
            # Key: osce:session:{session_id}:emotional_state
            key = f"session:{self.session_id}:emotional_state"
            redis_client.set_osce(key, state_data, ttl=1800)  # 30 min TTL
            
        except Exception as e:
            logger.error(f"Failed to save emotional state to Redis: {e}")
    
    def _load_from_redis(self):
        """Load existing state from Redis."""
        try:
            redis_client = get_redis_client()
            
            key = f"session:{self.session_id}:emotional_state"
            state_data = redis_client.get_osce(key)
            
            if state_data:
                self.current_state = state_data.get("current_state", self.current_state)
                self.empathy_points = state_data.get("empathy_points", 0)
                self.transition_history = state_data.get("transition_history", [])
                logger.info(f"Loaded emotional state from Redis: {self.current_state}")
        
        except Exception as e:
            logger.warning(f"Failed to load emotional state from Redis: {e}")
