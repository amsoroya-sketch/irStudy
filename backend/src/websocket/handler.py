"""
WebSocket Handler for AI OSCE Real-Time Sessions
Implements 8-minute conversational sessions with timer, emotional state tracking, and message routing
"""
import logging
import json
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.websocket.auth import authenticate_websocket, authorize_session_access
from src.websocket.session_manager import SessionManager
from src.websocket.timer import SessionTimer
from src.security.prompt_injection import PromptInjectionProtector
from src.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)


class OSCEWebSocketHandler:
    """
    WebSocket handler for 8-minute AI OSCE sessions.
    
    Manages:
    - JWT authentication
    - 8-minute timer with 1-min warning
    - Message routing to AI Patient service
    - Emotional state tracking
    - Redis caching + PostgreSQL sync
    - Rate limiting (max 3 concurrent per user)
    """
    
    def __init__(self, websocket: WebSocket, attempt_id: str, token: str, db: Session):
        self.websocket = websocket
        self.attempt_id = attempt_id
        self.token = token
        self.db = db
        self.user_id: Optional[str] = None
        self.session_manager: Optional[SessionManager] = None
        self.timer: Optional[SessionTimer] = None
        self.injection_protector = PromptInjectionProtector()
        self.redis_client = get_redis_client()
        self.is_connected = False
    
    async def handle(self):
        """
        Main WebSocket connection handler.
        
        Flow:
        1. Authenticate JWT token
        2. Authorize session access
        3. Check rate limits
        4. Accept WebSocket connection
        5. Initialize session (load from Redis/PostgreSQL)
        6. Start 8-minute timer
        7. Enter message loop (send/receive until 8:00)
        8. Finalize session and cleanup
        """
        try:
            # Step 1: Authenticate
            payload = await authenticate_websocket(self.websocket, self.token)
            if not payload:
                return  # WebSocket already closed by authenticate_websocket
            
            self.user_id = payload.get("user_id") or payload.get("sub")
            
            # Step 2: Authorize
            has_access = await authorize_session_access(self.user_id, self.attempt_id, self.db)
            if not has_access:
                await self.websocket.close(code=1008, reason="Unauthorized - not your session")
                return
            
            # Step 3: Check rate limits
            if not await self._check_rate_limit():
                await self.websocket.close(code=1008, reason="Rate limit exceeded - max 3 concurrent sessions")
                return
            
            # Step 4: Accept connection
            await self.websocket.accept()
            self.is_connected = True
            logger.info(f"✅ WebSocket connected: attempt_id={self.attempt_id}, user_id={self.user_id}")
            
            # Step 5: Initialize session
            self.session_manager = SessionManager(self.attempt_id, self.user_id, self.db, self.redis_client)
            await self.session_manager.load_session()
            
            # Step 6: Start timer
            self.timer = SessionTimer(self.attempt_id, self.websocket, self.session_manager)
            asyncio.create_task(self.timer.start())
            
            # Step 7: Send opening patient statement
            await self._send_opening_statement()
            
            # Step 8: Message loop
            await self._message_loop()
        
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: attempt_id={self.attempt_id}")
            await self._handle_disconnect(normal=True)
        
        except Exception as e:
            logger.error(f"❌ WebSocket error: {e}", exc_info=True)
            await self._handle_disconnect(normal=False)
    
    async def _check_rate_limit(self) -> bool:
        """
        Check if user has exceeded concurrent connection limit (max 3).
        
        Returns:
            True if within limit, False if exceeded
        """
        rate_limit_key = f"user:{self.user_id}:websocket_connections"
        
        try:
            # Get current count
            current_count = self.redis_client.get_osce(rate_limit_key) or 0
            current_count = int(current_count) if isinstance(current_count, str) else current_count
            
            if current_count >= 3:
                logger.warning(f"❌ Rate limit exceeded for user {self.user_id}: {current_count} concurrent connections")
                return False
            
            # Increment counter
            new_count = current_count + 1
            self.redis_client.set_osce(rate_limit_key, new_count, ttl=1800)
            
            logger.info(f"✅ Rate limit check passed: user {self.user_id} has {new_count}/3 connections")
            return True
        
        except Exception as e:
            logger.error(f"❌ Rate limit check failed: {e}")
            # Fail open (allow connection) to avoid false rejections
            return True
    
    async def _send_opening_statement(self):
        """Send initial patient message to start the conversation."""
        try:
            opening_statement = self.session_manager.get_opening_statement()
            emotional_state = self.session_manager.get_emotional_state()
            
            message = {
                "type": "patient_message",
                "speaker": "patient",
                "message": opening_statement,
                "emotional_state": emotional_state,
                "emotional_state_changed": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            await self.websocket.send_json(message)
            logger.info(f"✅ Sent opening statement for attempt {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to send opening statement: {e}")
    
    async def _message_loop(self):
        """
        Main message processing loop.
        Receives student messages and routes to AI Patient service.
        """
        while self.is_connected and not self.timer.is_expired():
            try:
                # Wait for student message
                data = await self.websocket.receive_text()
                message_data = json.loads(data)
                
                # Validate message
                if not self._validate_message(message_data):
                    await self._send_error("Invalid message format")
                    continue
                
                # Process student message
                await self._process_student_message(message_data)
            
            except WebSocketDisconnect:
                raise  # Re-raise to be caught by main handler
            
            except json.JSONDecodeError:
                await self._send_error("Invalid JSON")
            
            except Exception as e:
                logger.error(f"❌ Error in message loop: {e}", exc_info=True)
                await self._send_error("Internal server error")
    
    def _validate_message(self, message_data: Dict[str, Any]) -> bool:
        """
        Validate student message.
        
        Checks:
        - message_data has "type" and "message" fields
        - message is not empty
        - message length <5000 chars
        """
        if not isinstance(message_data, dict):
            return False
        
        if message_data.get("type") != "student_message":
            return False
        
        message = message_data.get("message", "").strip()
        
        if not message:
            return False
        
        if len(message) > 5000:
            return False

        # SECURITY: Check for prompt injection attempts
        is_valid, error_msg = self.injection_protector.validate_student_message(message)
        if not is_valid:
            logger.warning(
                f"🚨 Prompt injection attempt blocked: user={self.user_id}, "
                f"attempt_id={self.attempt_id}, error={error_msg}"
            )
            return False
        
        return True
    
    async def _process_student_message(self, message_data: Dict[str, Any]):
        """
        Process student message:
        1. Log to Redis
        2. Send "thinking..." indicator
        3. Queue to AI Patient service (background task)
        4. Receive AI response
        5. Broadcast response to WebSocket
        """
        student_message = message_data.get("message")
        
        # Log to session manager
        await self.session_manager.log_student_message(student_message)
        
        # Send thinking indicator
        await self.websocket.send_json({
            "type": "thinking",
            "message": "Patient is thinking..."
        })
        
        # Queue AI Patient response (background task)
        asyncio.create_task(self._generate_ai_response(student_message))
    
    async def _generate_ai_response(self, student_message: str):
        """
        Generate AI Patient response (background task).
        
        Steps:
        1. Load persona and emotional state
        2. Call AI Patient service
        3. Update emotional state
        4. Log response to Redis
        5. Broadcast to WebSocket
        """
        try:
            # Generate AI response
            response_data = await self.session_manager.generate_ai_patient_response(student_message)
            
            # Broadcast to WebSocket
            await self.websocket.send_json({
                "type": "patient_message",
                "speaker": "patient",
                "message": response_data["message"],
                "emotional_state": response_data["emotional_state"],
                "emotional_state_changed": response_data.get("emotional_state_changed", False),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
            
            logger.info(f"✅ AI Patient response sent for attempt {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Failed to generate AI response: {e}", exc_info=True)
            await self._send_error("Failed to generate patient response")
    
    async def _send_error(self, message: str):
        """Send error message to client."""
        try:
            await self.websocket.send_json({
                "type": "error",
                "message": message
            })
        except Exception as e:
            logger.error(f"❌ Failed to send error message: {e}")
    
    async def _handle_disconnect(self, normal: bool = True):
        """
        Handle WebSocket disconnection.
        
        Steps:
        1. Sync Redis → PostgreSQL (don't lose data)
        2. Decrement rate limit counter
        3. Cleanup (if session expired)
        """
        self.is_connected = False
        
        try:
            # Sync to PostgreSQL
            if self.session_manager:
                await self.session_manager.sync_to_postgres()
                logger.info(f"✅ Session synced to PostgreSQL on disconnect: {self.attempt_id}")
            
            # Decrement rate limit
            if self.user_id:
                rate_limit_key = f"user:{self.user_id}:websocket_connections"
                current = self.redis_client.get_osce(rate_limit_key) or 0
                current = int(current) if isinstance(current, str) else current
                new_count = max(0, current - 1)
                self.redis_client.set_osce(rate_limit_key, new_count, ttl=1800)
                logger.info(f"✅ Decremented rate limit: user {self.user_id} now has {new_count} connections")
            
            # Cleanup if session expired
            if self.timer and self.timer.is_expired():
                await self.session_manager.cleanup_redis()
                logger.info(f"✅ Redis cleaned up for expired session: {self.attempt_id}")
        
        except Exception as e:
            logger.error(f"❌ Error during disconnect cleanup: {e}", exc_info=True)
