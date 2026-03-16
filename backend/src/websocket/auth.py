"""
WebSocket JWT Authentication
Validates JWT tokens and authorizes WebSocket connections
"""
import logging
from typing import Optional, Dict, Any
from fastapi import WebSocket, status
from jose import jwt, JWTError
import os

logger = logging.getLogger(__name__)

# JWT Configuration (should match your auth system)
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


async def authenticate_websocket(websocket: WebSocket, token: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Authenticate WebSocket connection using JWT token.
    
    Args:
        websocket: FastAPI WebSocket connection
        token: JWT token from query parameter
    
    Returns:
        Decoded token payload if valid, None if invalid
    
    Side Effects:
        Closes WebSocket with appropriate code if authentication fails
    """
    if not token:
        logger.warning("WebSocket connection attempted without token")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token required")
        return None
    
    try:
        # Decode and validate JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract required claims
        user_id = payload.get("user_id") or payload.get("sub")
        
        if not user_id:
            logger.warning("JWT token missing user_id claim")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token claims")
            return None
        
        logger.info(f"✅ WebSocket authenticated for user_id={user_id}")
        return payload
    
    except JWTError as e:
        logger.error(f"❌ JWT validation failed: {e}")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        return None
    
    except Exception as e:
        logger.error(f"❌ Unexpected error during authentication: {e}")
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Authentication error")
        return None


async def authorize_session_access(
    user_id: str,
    attempt_id: str,
    db_session
) -> bool:
    """
    Verify user has access to the specified OSCE attempt.
    
    Args:
        user_id: Authenticated user ID
        attempt_id: OSCE attempt ID from WebSocket path
        db_session: SQLAlchemy database session
    
    Returns:
        True if user owns the attempt, False otherwise
    """
    from src.db.models import OSCEAttemptAI
    
    try:
        # Query attempt
        attempt = db_session.query(OSCEAttemptAI).filter(
            OSCEAttemptAI.attempt_id == attempt_id
        ).first()
        
        if not attempt:
            logger.warning(f"Attempt {attempt_id} not found")
            return False
        
        if attempt.user_id != user_id:
            logger.warning(f"User {user_id} attempted to access attempt {attempt_id} (owner: {attempt.user_id})")
            return False
        
        logger.info(f"✅ User {user_id} authorized for attempt {attempt_id}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error authorizing session access: {e}")
        return False
