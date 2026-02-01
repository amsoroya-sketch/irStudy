"""
Password hashing and JWT token management

SECURITY:
- Passwords hashed with bcrypt (work factor 12)
- JWT tokens signed with HS256 algorithm
- Secret key loaded from environment/Docker secret
- Tokens include expiration, user ID, role
- Refresh tokens for extended sessions
"""

from datetime import datetime, timedelta
from typing import Optional
import os

from jose import JWTError, jwt
from passlib.context import CryptContext


# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# JWT configuration
def get_secret_key() -> str:
    """
    Get JWT secret key from environment or Docker secret.

    SECURITY: Secret key must be strong (32+ bytes hex)
    Generate with: openssl rand -hex 32
    """
    # Try Docker secret first
    secret_path = "/run/secrets/jwt_secret"
    if os.path.exists(secret_path):
        with open(secret_path, 'r') as f:
            return f.read().strip()

    # Fallback to environment variable
    secret_key = os.getenv("SECRET_KEY")
    if not secret_key:
        raise ValueError(
            "JWT secret key not found. "
            "Set SECRET_KEY env var or mount /run/secrets/jwt_secret"
        )

    return secret_key


SECRET_KEY = get_secret_key()
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


# ============================================================================
# PASSWORD HASHING
# ============================================================================

def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against hash.

    Args:
        plain_password: Plain text password from user input
        hashed_password: Stored bcrypt hash

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ============================================================================
# JWT TOKEN GENERATION
# ============================================================================

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create JWT access token.

    Args:
        data: Payload data (user_id, email, role)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token (longer expiration).

    Args:
        data: Payload data (user_id, email)

    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# ============================================================================
# JWT TOKEN VERIFICATION
# ============================================================================

def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify JWT token.

    Args:
        token: Encoded JWT token

    Returns:
        Token payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[dict]:
    """
    Verify access token and return payload.

    Args:
        token: JWT access token

    Returns:
        Token payload if valid access token, None otherwise
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # Verify token type
    if payload.get("type") != "access":
        return None

    # Verify expiration (jose already checks this, but double-check)
    exp = payload.get("exp")
    if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
        return None

    return payload


def verify_refresh_token(token: str) -> Optional[dict]:
    """
    Verify refresh token and return payload.

    Args:
        token: JWT refresh token

    Returns:
        Token payload if valid refresh token, None otherwise
    """
    payload = decode_token(token)

    if payload is None:
        return None

    # Verify token type
    if payload.get("type") != "refresh":
        return None

    # Verify expiration
    exp = payload.get("exp")
    if exp is None or datetime.fromtimestamp(exp) < datetime.utcnow():
        return None

    return payload
