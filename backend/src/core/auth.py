"""
Authentication and JWT Token Management
Unified JWT format for EMR and AI OSCE systems

SECURITY STANDARDS:
- JWT tokens signed with HS256 algorithm
- 15-minute access token expiry
- 7-day refresh token expiry
- Issuer: "irstudy-platform"
- Audience: ["emr-api", "osce-api"]
- All claims validated before token generation

Reference: SHARED_INFRASTRUCTURE_SPEC.md Section 3 (JWT Authentication)
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import os
import logging

from jose import JWTError, jwt

logger = logging.getLogger(__name__)


# JWT Configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))
ISSUER = "irstudy-platform"
AUDIENCE = ["emr-api", "osce-api"]


def get_jwt_secret() -> str:
    """
    Get JWT secret from Vault or environment
    
    Security: Falls back to environment variable if Vault unavailable
    """
    try:
        from src.core.vault import get_vault_secret
        return get_vault_secret("shared", "jwt-secret")
    except Exception as e:
        logger.warning(f"Failed to retrieve JWT secret from Vault: {e}")
        
        # Fallback to environment variable
        secret_key = os.getenv("JWT_SECRET_KEY") or os.getenv("SECRET_KEY")
        if not secret_key:
            raise ValueError(
                "JWT secret key not found. "
                "Set JWT_SECRET_KEY env var or configure Vault"
            )
        
        # Validate secret key minimum length (security requirement)
        if len(secret_key) < 64:
            raise ValueError(
                f"JWT secret key too weak. "
                f"Must be ≥64 characters (32 bytes hex). "
                f"Current length: {len(secret_key)}. "
                f"Generate with: openssl rand -hex 32"
            )
        
        return secret_key


def create_access_token(
    user_id: str,
    email: str,
    role: str,
    user_progress_id: str,
    subscription_tier: str = "free",
    mock_exam_access: bool = False,
    emr_session_limit: int = 50,
    osce_session_limit: int = 30
) -> str:
    """
    Create unified JWT access token for EMR and AI OSCE systems
    
    Token Structure (aligned with SHARED_INFRASTRUCTURE_SPEC.md):
    {
      "user_id": "uuid",
      "email": "student@example.com",
      "role": "student",
      "user_progress_id": "uuid",
      "subscription_tier": "premium",
      "mock_exam_access": true,
      "emr_session_limit": 50,
      "osce_session_limit": 30,
      "iat": 1708041600,
      "exp": 1708042500,
      "iss": "irstudy-platform",
      "aud": ["emr-api", "osce-api"]
    }
    
    Args:
        user_id: User UUID
        email: User email
        role: User role (student, educator, admin)
        user_progress_id: User progress UUID
        subscription_tier: Subscription tier (free, premium, enterprise)
        mock_exam_access: Whether user has access to mock exams
        emr_session_limit: Maximum EMR sessions allowed
        osce_session_limit: Maximum OSCE sessions allowed
    
    Returns:
        Encoded JWT access token (15-minute expiry)
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "user_progress_id": user_progress_id,
        "subscription_tier": subscription_tier,
        "mock_exam_access": mock_exam_access,
        "emr_session_limit": emr_session_limit,
        "osce_session_limit": osce_session_limit,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": ISSUER,
        "aud": AUDIENCE
    }
    
    secret_key = get_jwt_secret()
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    
    logger.info(f"Created access token for user {user_id} (expires in {ACCESS_TOKEN_EXPIRE_MINUTES} min)")
    return encoded_jwt


def create_refresh_token(
    user_id: str,
    token_id: str
) -> str:
    """
    Create JWT refresh token (7-day expiry)
    
    Token Structure:
    {
      "user_id": "uuid",
      "token_id": "uuid",
      "iat": 1708041600,
      "exp": 1708646400,
      "iss": "irstudy-platform",
      "type": "refresh"
    }
    
    Args:
        user_id: User UUID
        token_id: Unique token ID for tracking
    
    Returns:
        Encoded JWT refresh token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    payload = {
        "user_id": user_id,
        "token_id": token_id,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "iss": ISSUER,
        "type": "refresh"
    }
    
    secret_key = get_jwt_secret()
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=ALGORITHM)
    
    logger.info(f"Created refresh token for user {user_id} (expires in {REFRESH_TOKEN_EXPIRE_DAYS} days)")
    return encoded_jwt


def verify_token(token: str, expected_type: str = "access") -> Optional[Dict[str, Any]]:
    """
    Verify and decode JWT token

    Args:
        token: Encoded JWT token
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        Token payload if valid, None otherwise

    Validation:
        - Signature verification
        - Expiration check
        - Issuer validation
        - Audience validation (access tokens only)
        - Type validation
    """
    try:
        secret_key = get_jwt_secret()

        # Decode and verify token
        # Note: python-jose expects audience as string, not list
        # We verify the audience list manually after decoding
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            # Skip audience verification in jwt.decode (python-jose doesn't support list)
            options={"verify_aud": False}
        )

        # Manual audience validation for access tokens
        if expected_type == "access":
            token_aud = payload.get("aud")
            # Check if token audience matches our expected audience list
            if token_aud != AUDIENCE:
                logger.warning(f"Audience mismatch: expected {AUDIENCE}, got {token_aud}")
                return None

        # Verify token type (for refresh tokens)
        if expected_type == "refresh":
            if payload.get("type") != "refresh":
                logger.warning("Token type mismatch: expected refresh, got access")
                return None

        return payload

    except JWTError as e:
        logger.warning(f"JWT verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def verify_access_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify access token and return payload
    
    Args:
        token: JWT access token
    
    Returns:
        Token payload if valid, None otherwise
    """
    return verify_token(token, expected_type="access")


def verify_refresh_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify refresh token and return payload
    
    Args:
        token: JWT refresh token
    
    Returns:
        Token payload if valid, None otherwise
    """
    return verify_token(token, expected_type="refresh")
