"""
Session Timer - 8-Minute Countdown with Warnings
Implements strict server-side timing for OSCE sessions
"""
import logging
import asyncio
from datetime import datetime, timezone
from typing import Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class SessionTimer:
    """
    8-minute session timer with 1-minute warning.
    
    Features:
    - Server-authoritative (client cannot manipulate)
    - Broadcasts timer_update every 1 second
    - Sends warning at 7:00 (1 minute remaining)
    - Auto-finalizes session at 8:00
    - Accurate to ±0.5 seconds
    """
    
    MAX_DURATION = 480  # 8 minutes in seconds
    WARNING_AT = 420    # 7 minutes (1-min warning)
    
    def __init__(self, attempt_id: str, websocket: WebSocket, session_manager):
        self.attempt_id = attempt_id
        self.websocket = websocket
        self.session_manager = session_manager
        self.started_at: Optional[datetime] = None
        self.elapsed_seconds = 0
        self.warning_sent = False
        self.expired = False
        self._task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the 8-minute countdown timer."""
        self.started_at = datetime.now(timezone.utc)
        logger.info(f"✅ Timer started for attempt {self.attempt_id}")
        
        try:
            while self.elapsed_seconds < self.MAX_DURATION:
                # Calculate elapsed time
                now = datetime.now(timezone.utc)
                self.elapsed_seconds = int((now - self.started_at).total_seconds())
                remaining_seconds = self.MAX_DURATION - self.elapsed_seconds
                
                # Broadcast timer update
                await self._broadcast_timer_update(self.elapsed_seconds, remaining_seconds)
                
                # Check for 1-minute warning
                if self.elapsed_seconds >= self.WARNING_AT and not self.warning_sent:
                    await self._send_warning()
                    self.warning_sent = True
                
                # Wait 1 second
                await asyncio.sleep(1)
            
            # Timer expired - finalize session
            await self._finalize_session()
        
        except asyncio.CancelledError:
            logger.info(f"Timer cancelled for attempt {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Timer error: {e}", exc_info=True)
    
    async def _broadcast_timer_update(self, elapsed: int, remaining: int):
        """
        Broadcast timer update to client.
        
        Sends every 1 second to keep client synchronized.
        """
        try:
            await self.websocket.send_json({
                "type": "timer_update",
                "elapsed_seconds": elapsed,
                "remaining_seconds": remaining
            })
        except Exception as e:
            logger.error(f"❌ Failed to broadcast timer update: {e}")
    
    async def _send_warning(self):
        """Send 1-minute warning at 7:00 elapsed."""
        try:
            await self.websocket.send_json({
                "type": "timer_warning",
                "message": "1 minute remaining",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Log warning to database
            await self.session_manager.log_warning_sent()
            
            logger.info(f"⚠️  1-minute warning sent for attempt {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to send warning: {e}")
    
    async def _finalize_session(self):
        """
        Finalize session at 8:00.
        
        Steps:
        1. Mark session as expired
        2. Stop accepting new messages
        3. Sync Redis → PostgreSQL (final)
        4. Trigger AI Examiner scoring
        5. Send session_ended message
        6. Clean up Redis
        """
        self.expired = True
        logger.info(f"⏱️  Session expired for attempt {self.attempt_id}")
        
        try:
            # Send session ended message
            await self.websocket.send_json({
                "type": "session_ended",
                "message": "Time's up! Your session is being scored.",
                "attempt_id": self.attempt_id,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            # Final sync to PostgreSQL
            await self.session_manager.finalize_session()
            
            # Trigger AI Examiner scoring (background task)
            asyncio.create_task(self._trigger_scoring())
            
            logger.info(f"✅ Session finalized for attempt {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to finalize session: {e}", exc_info=True)
    
    async def _trigger_scoring(self):
        """
        Trigger AI Examiner scoring (background task).
        
        Loads conversation history and persona, calls AI Examiner service,
        saves scores to database, and broadcasts results to client.
        """
        try:
            logger.info(f"🤖 Triggering AI Examiner for attempt {self.attempt_id}")
            
            # Get scoring result
            scoring_result = await self.session_manager.score_session()
            
            # Broadcast scoring result
            await self.websocket.send_json({
                "type": "scoring_complete",
                "total_score": scoring_result["total_score"],
                "max_score": 15,
                "pass_fail": scoring_result["pass_fail"],
                "breakdown": {
                    "communication": {
                        "score": scoring_result["communication_score"],
                        "max": 3,
                        "feedback": scoring_result["communication_feedback"]
                    },
                    "clinical_reasoning": {
                        "score": scoring_result["clinical_reasoning_score"],
                        "max": 4,
                        "feedback": scoring_result["clinical_reasoning_feedback"]
                    },
                    "information_gathering": {
                        "score": scoring_result["information_gathering_score"],
                        "max": 4,
                        "feedback": scoring_result["information_gathering_feedback"]
                    },
                    "management": {
                        "score": scoring_result["management_score"],
                        "max": 2,
                        "feedback": scoring_result["management_feedback"]
                    },
                    "professionalism": {
                        "score": scoring_result["professionalism_score"],
                        "max": 2,
                        "feedback": scoring_result["professionalism_feedback"]
                    }
                },
                "strengths": scoring_result.get("strengths", []),
                "areas_for_improvement": scoring_result.get("areas_for_improvement", []),
                "overall_feedback": scoring_result.get("overall_feedback", "")
            })
            
            logger.info(f"✅ Scoring complete for attempt {self.attempt_id}: {scoring_result['total_score']}/15 ({scoring_result['pass_fail']})")
        
        except Exception as e:
            logger.error(f"❌ Scoring failed: {e}", exc_info=True)
            await self.websocket.send_json({
                "type": "error",
                "message": "Failed to score session. Please contact support."
            })
    
    def is_expired(self) -> bool:
        """Check if timer has expired."""
        return self.expired
    
    def cancel(self):
        """Cancel the timer task."""
        if self._task and not self._task.done():
            self._task.cancel()
