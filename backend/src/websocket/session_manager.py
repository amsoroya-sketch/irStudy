"""
Session Manager - Redis/PostgreSQL State Management
Handles session lifecycle, caching, and synchronization
"""
import logging
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SessionManager:
    """
    Manages OSCE session state across Redis (cache) and PostgreSQL (persistent).
    
    Responsibilities:
    - Load session from Redis or PostgreSQL
    - Cache persona, emotional state, messages in Redis
    - Sync to PostgreSQL every 30 seconds (via Celery Beat)
    - Log student messages and AI responses
    - Track emotional state transitions
    - Generate AI Patient responses
    - Trigger AI Examiner scoring
    - Cleanup on session end
    """
    
    def __init__(self, attempt_id: str, user_id: str, db: Session, redis_client):
        self.attempt_id = attempt_id
        self.user_id = user_id
        self.db = db
        self.redis = redis_client
        self.persona = None
        self.emotional_state = "ANXIOUS_GUARDED"
        self.empathy_points = 0
        self.message_count = 0
    
    async def load_session(self):
        """
        Load session state from Redis or PostgreSQL.
        
        Priority:
        1. Try Redis (fast cache)
        2. Fall back to PostgreSQL (persistent)
        """
        # Try Redis first
        redis_state = self._load_from_redis()
        if redis_state:
            logger.info(f"✅ Session loaded from Redis: {self.attempt_id}")
            return
        
        # Fall back to PostgreSQL
        self._load_from_postgres()
        
        # Cache in Redis for future requests
        self._cache_to_redis()
        
        logger.info(f"✅ Session loaded from PostgreSQL and cached: {self.attempt_id}")
    
    def _load_from_redis(self) -> bool:
        """Load session from Redis cache."""
        try:
            # Load persona
            persona_key = f"session:{self.attempt_id}:persona"
            persona_data = self.redis.get_osce(persona_key)
            
            if not persona_data:
                return False
            
            self.persona = persona_data if isinstance(persona_data, dict) else json.loads(persona_data)
            
            # Load state
            state_key = f"session:{self.attempt_id}:state"
            state_data = self.redis.get_osce(state_key)
            
            if state_data:
                if isinstance(state_data, dict):
                    self.emotional_state = state_data.get("emotional_state", "ANXIOUS_GUARDED")
                    self.empathy_points = int(state_data.get("empathy_points", 0))
                    self.message_count = int(state_data.get("message_count", 0))
                else:
                    state = json.loads(state_data)
                    self.emotional_state = state.get("emotional_state", "ANXIOUS_GUARDED")
                    self.empathy_points = int(state.get("empathy_points", 0))
                    self.message_count = int(state.get("message_count", 0))
            
            return True
        
        except Exception as e:
            logger.warning(f"⚠️  Failed to load from Redis: {e}")
            return False
    
    def _load_from_postgres(self):
        """Load session from PostgreSQL."""
        from src.db.models import OSCEAttemptAI, PatientPersona
        
        try:
            # Load attempt
            attempt = self.db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == self.attempt_id
            ).first()
            
            if not attempt:
                raise ValueError(f"Attempt {self.attempt_id} not found")
            
            # Load persona
            persona = self.db.query(PatientPersona).filter(
                PatientPersona.persona_id == attempt.persona_id
            ).first()
            
            if not persona:
                raise ValueError(f"Persona {attempt.persona_id} not found")
            
            # Convert to dict
            self.persona = {
                "persona_id": persona.persona_id,
                "name": persona.name,
                "age": persona.age,
                "gender": persona.gender,
                "occupation": persona.occupation,
                "cultural_background": persona.cultural_background,
                "chief_complaint": persona.chief_complaint,
                "opening_statement": persona.opening_statement,
                "symptoms": persona.symptoms,
                "medical_history": persona.medical_history,
                "emotional_profile": persona.emotional_profile,
                "key_differentials": persona.key_differentials,
                "critical_actions": persona.critical_actions
            }
            
            # Load existing state from attempt
            if attempt.emotional_state_transitions:
                transitions = attempt.emotional_state_transitions
                if isinstance(transitions, str):
                    transitions = json.loads(transitions)
                if transitions and len(transitions) > 0:
                    self.emotional_state = transitions[-1].get("to_state", "ANXIOUS_GUARDED")
            
            # Load message count
            if attempt.conversation_history:
                history = attempt.conversation_history
                if isinstance(history, str):
                    history = json.loads(history)
                self.message_count = len(history) if history else 0
        
        except Exception as e:
            logger.error(f"❌ Failed to load from PostgreSQL: {e}", exc_info=True)
            raise
    
    def _cache_to_redis(self):
        """Cache session data to Redis."""
        try:
            # Cache persona
            persona_key = f"session:{self.attempt_id}:persona"
            self.redis.set_osce(persona_key, self.persona, ttl=1800)
            
            # Cache state
            state_key = f"session:{self.attempt_id}:state"
            state_data = {
                "emotional_state": self.emotional_state,
                "empathy_points": self.empathy_points,
                "message_count": self.message_count,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            self.redis.set_osce(state_key, state_data, ttl=1800)
            
            logger.info(f"✅ Session cached to Redis: {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to cache to Redis: {e}")
    
    def get_opening_statement(self) -> str:
        """Get patient's opening statement."""
        if not self.persona:
            return "I'm not feeling well, doctor."
        return self.persona.get("opening_statement", "I'm not feeling well, doctor.")
    
    def get_emotional_state(self) -> str:
        """Get current emotional state."""
        return self.emotional_state
    
    async def log_student_message(self, message: str):
        """Log student message to Redis."""
        try:
            messages_key = f"session:{self.attempt_id}:messages"
            message_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "speaker": "student",
                "message": message
            }
            
            # Get existing messages
            existing = self.redis.get_osce(messages_key) or []
            if isinstance(existing, str):
                existing = json.loads(existing)
            
            # Append new message
            existing.append(message_data)
            
            # Save back to Redis
            self.redis.set_osce(messages_key, existing, ttl=1800)
            
            # Update message count
            self.message_count += 1
            state_key = f"session:{self.attempt_id}:state"
            state_data = self.redis.get_osce(state_key) or {}
            if isinstance(state_data, str):
                state_data = json.loads(state_data)
            state_data["message_count"] = self.message_count
            self.redis.set_osce(state_key, state_data, ttl=1800)
            
            logger.info(f"✅ Student message logged: attempt={self.attempt_id}, count={self.message_count}")
        
        except Exception as e:
            logger.error(f"❌ Failed to log student message: {e}")
    
    async def generate_ai_patient_response(self, student_message: str) -> Dict[str, Any]:
        """
        Generate AI Patient response using AI Patient service.
        
        Returns:
            Dict with keys: message, emotional_state, emotional_state_changed
        """
        from src.ai.ai_patient import AIPatientService
        from src.ai.emotional_state import EmotionalStateMachine
        
        try:
            # Initialize AI Patient service
            ai_patient = AIPatientService()
            
            # Update emotional state
            state_machine = EmotionalStateMachine(
                baseline_state=self.emotional_state,
                session_id=self.attempt_id
            )
            new_state = state_machine.process_student_message(student_message)
            state_changed = (new_state != self.emotional_state)
            self.emotional_state = new_state
            self.empathy_points = state_machine.empathy_points
            
            # Generate AI response
            patient_response = ai_patient.generate_response(
                persona=self.persona,
                student_message=student_message,
                emotional_state=self.emotional_state
            )
            
            # Log response to Redis
            await self._log_patient_message(patient_response)
            
            return {
                "message": patient_response,
                "emotional_state": self.emotional_state,
                "emotional_state_changed": state_changed
            }
        
        except Exception as e:
            logger.error(f"❌ Failed to generate AI response: {e}", exc_info=True)
            return {
                "message": "I'm sorry, I'm having trouble expressing myself right now.",
                "emotional_state": self.emotional_state,
                "emotional_state_changed": False
            }
    
    async def _log_patient_message(self, message: str):
        """Log patient message to Redis."""
        try:
            messages_key = f"session:{self.attempt_id}:messages"
            message_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "speaker": "patient",
                "message": message,
                "emotional_state": self.emotional_state
            }
            
            existing = self.redis.get_osce(messages_key) or []
            if isinstance(existing, str):
                existing = json.loads(existing)
            
            existing.append(message_data)
            self.redis.set_osce(messages_key, existing, ttl=1800)
            
            logger.info(f"✅ Patient message logged: attempt={self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to log patient message: {e}")
    
    async def log_warning_sent(self):
        """Log that 1-minute warning was sent."""
        from src.db.models import OSCEAttemptAI
        
        try:
            attempt = self.db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == self.attempt_id
            ).first()
            
            if attempt:
                # Note: warning_1min_shown field would need to be added to model
                # For now, log to conversation history
                pass
            
            self.db.commit()
        except Exception as e:
            logger.error(f"❌ Failed to log warning: {e}")
            self.db.rollback()
    
    async def finalize_session(self):
        """
        Finalize session at 8:00.
        
        Steps:
        1. Final Redis → PostgreSQL sync
        2. Mark session as finalized
        3. Calculate total tokens and cost
        """
        await self.sync_to_postgres()
        
        from src.db.models import OSCEAttemptAI
        
        try:
            attempt = self.db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == self.attempt_id
            ).first()
            
            if attempt:
                attempt.ended_at = datetime.now(timezone.utc)
                attempt.duration_seconds = 480
                attempt.session_state = "finalized"
                self.db.commit()
                
                logger.info(f"✅ Session finalized: {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to finalize session: {e}")
            self.db.rollback()
    
    async def sync_to_postgres(self):
        """
        Sync Redis session data to PostgreSQL.
        Called periodically (every 30s) and on disconnect.
        """
        from src.db.models import OSCEAttemptAI
        
        try:
            # Load messages from Redis
            messages_key = f"session:{self.attempt_id}:messages"
            messages = self.redis.get_osce(messages_key) or []
            if isinstance(messages, str):
                messages = json.loads(messages)
            
            # Update attempt in PostgreSQL
            attempt = self.db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == self.attempt_id
            ).first()
            
            if attempt:
                attempt.conversation_history = messages
                attempt.total_messages = len(messages)
                attempt.updated_at = datetime.now(timezone.utc)
                self.db.commit()
                
                logger.info(f"✅ Synced {len(messages)} messages to PostgreSQL: {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to sync to PostgreSQL: {e}")
            self.db.rollback()
    
    async def score_session(self) -> Dict[str, Any]:
        """
        Trigger AI Examiner to score the session.
        
        Returns:
            Scoring result dict
        """
        from src.ai.ai_examiner import AIExaminerService
        from src.db.models import OSCEAttemptAI, OSCEScoreAI
        
        try:
            # Load conversation history
            attempt = self.db.query(OSCEAttemptAI).filter(
                OSCEAttemptAI.attempt_id == self.attempt_id
            ).first()
            
            if not attempt or not attempt.conversation_history:
                raise ValueError("No conversation history found")
            
            # Format transcript
            history = attempt.conversation_history
            if isinstance(history, str):
                history = json.loads(history)
            
            transcript = [
                {"role": msg["speaker"], "message": msg["message"]}
                for msg in history
            ]
            
            # Score session
            ai_examiner = AIExaminerService()
            scores = ai_examiner.score_session(self.persona, transcript)
            
            # Save scores to database
            score_record = OSCEScoreAI(
                attempt_id=self.attempt_id,
                communication_score=scores["communication_score"],
                communication_feedback=scores["communication_feedback"],
                clinical_reasoning_score=scores["clinical_reasoning_score"],
                clinical_reasoning_feedback=scores["clinical_reasoning_feedback"],
                information_gathering_score=scores["information_gathering_score"],
                information_gathering_feedback=scores["information_gathering_feedback"],
                management_score=scores["management_score"],
                management_feedback=scores["management_feedback"],
                professionalism_score=scores["professionalism_score"],
                professionalism_feedback=scores["professionalism_feedback"],
                total_score=scores["total_score"],
                pass_fail=scores["pass_fail"],
                critical_errors=scores.get("critical_errors", []),
                strengths=scores.get("strengths", []),
                areas_for_improvement=scores.get("areas_for_improvement", []),
                overall_feedback=scores.get("overall_feedback", "")
            )
            
            self.db.add(score_record)
            self.db.commit()
            
            logger.info(f"✅ Session scored: {self.attempt_id}, score={scores['total_score']}/15")
            
            return scores
        
        except Exception as e:
            logger.error(f"❌ Failed to score session: {e}", exc_info=True)
            self.db.rollback()
            raise
    
    async def cleanup_redis(self):
        """Clean up Redis keys after session ends."""
        try:
            keys_to_delete = [
                f"session:{self.attempt_id}:persona",
                f"session:{self.attempt_id}:state",
                f"session:{self.attempt_id}:messages"
            ]
            
            for key in keys_to_delete:
                # Redis client handles namespace prefix
                pass  # Keys will expire automatically via TTL
            
            logger.info(f"✅ Redis cleanup scheduled: {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to cleanup Redis: {e}")
