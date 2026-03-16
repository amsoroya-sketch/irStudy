"""
FastAPI WebSocket Router
Exposes /ws/osce/{attempt_id} endpoint
"""
import logging
from fastapi import APIRouter, WebSocket, Query, Depends
from sqlalchemy.orm import Session

from src.websocket.handler import OSCEWebSocketHandler
from src.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/osce/{attempt_id}")
async def websocket_osce_session(
    websocket: WebSocket,
    attempt_id: str,
    token: str = Query(..., description="JWT authentication token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time AI OSCE sessions.
    
    **URL**: `wss://api.example.com/ws/osce/{attempt_id}?token=<jwt_token>`
    
    **Flow**:
    1. Authenticate JWT token
    2. Authorize user access to attempt
    3. Check rate limits (max 3 concurrent per user)
    4. Accept WebSocket connection
    5. Start 8-minute timer
    6. Send opening patient statement
    7. Enter message loop (student ↔ AI Patient)
    8. Send 1-minute warning at 7:00
    9. Auto-finalize at 8:00
    10. Trigger AI Examiner scoring
    11. Send scoring results
    12. Close connection
    
    **Authentication**:
    - JWT token required in query parameter
    - Token must contain valid user_id
    - User must own the attempt
    
    **Rate Limiting**:
    - Max 3 concurrent WebSocket connections per user
    - 4th connection rejected with code 1008
    
    **Timer**:
    - Server-authoritative 8-minute countdown
    - Updates broadcast every 1 second
    - 1-minute warning at 7:00
    - Auto-finalize at 8:00 (hard stop)
    
    **Message Types** (Client → Server):
    ```json
    {
      "type": "student_message",
      "message": "Can you tell me more about the pain?"
    }
    ```
    
    **Message Types** (Server → Client):
    ```json
    {
      "type": "patient_message",
      "speaker": "patient",
      "message": "It started about 2 hours ago...",
      "emotional_state": "ANXIOUS_GUARDED",
      "emotional_state_changed": false,
      "timestamp": "2026-03-12T10:05:23Z"
    }
    ```
    
    ```json
    {
      "type": "timer_update",
      "elapsed_seconds": 45,
      "remaining_seconds": 435
    }
    ```
    
    ```json
    {
      "type": "timer_warning",
      "message": "1 minute remaining",
      "timestamp": "2026-03-12T10:13:43Z"
    }
    ```
    
    ```json
    {
      "type": "session_ended",
      "message": "Time's up! Your session is being scored.",
      "attempt_id": "uuid-123",
      "timestamp": "2026-03-12T10:13:45Z"
    }
    ```
    
    ```json
    {
      "type": "scoring_complete",
      "total_score": 14,
      "max_score": 15,
      "pass_fail": "PASS",
      "breakdown": {...},
      "strengths": [...],
      "areas_for_improvement": [...],
      "overall_feedback": "..."
    }
    ```
    
    **Error Handling**:
    - Invalid token: Connection closed with code 1008
    - Unauthorized: Connection closed with code 1008
    - Rate limit exceeded: Connection closed with code 1008
    - Session not found: Connection closed with code 1008
    """
    handler = OSCEWebSocketHandler(websocket, attempt_id, token, db)
    await handler.handle()
