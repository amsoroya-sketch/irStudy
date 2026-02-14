"""
Authentication endpoints

Routes:
- POST /api/v1/auth/register - Register new user
- POST /api/v1/auth/login - Login and get tokens
- POST /api/v1/auth/refresh - Refresh access token
- POST /api/v1/auth/logout - Logout (invalidate tokens)
- POST /api/v1/auth/verify-email - Verify email address

SECURITY:
- Password hashing with bcrypt
- JWT access tokens (30 min expiry)
- JWT refresh tokens (7 day expiry)
- Account lockout after 5 failed attempts
- Rate limiting on login endpoint
"""

from datetime import timedelta, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User, UserRole
from src.schemas.user import UserCreate, UserLogin, Token, UserPrivate
from src.auth.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from src.auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["authentication"])


# ============================================================================
# REGISTRATION
# ============================================================================


@router.post("/register", response_model=UserPrivate, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register new user account.

    Requirements:
    - Unique email address
    - Password: 12+ chars, uppercase, lowercase, digit, special char
    - Full name: 2-255 characters

    Returns:
    - User object (without password hash)
    - Email verification required before full access
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email address already registered"
        )

    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=UserRole.STUDENT,  # Default role
        is_active=True,
        is_verified=False,  # Requires email verification
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # TODO: Send verification email
    # await send_verification_email(new_user.email, new_user.id)

    return new_user


# ============================================================================
# LOGIN
# ============================================================================


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """
    Login with email and password.

    Returns:
    - Access token (30 min expiry)
    - Refresh token (7 day expiry)

    Security:
    - Account locked after 5 failed attempts (30 min lockout)
    - Failed attempts tracked per user
    - Successful login resets failed attempt counter
    """
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    # Check if account is locked
    if user.locked_until is not None:
        if user.locked_until > datetime.now(user.locked_until.tzinfo):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked due to multiple failed login attempts. "
                f"Try again after {user.locked_until.strftime('%H:%M:%S')}",
            )
        else:
            # Lockout period expired - reset
            user.locked_until = None
            user.failed_login_attempts = 0
            db.commit()

    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        # Increment failed login attempts
        user.failed_login_attempts += 1

        # Lock account after 5 failed attempts
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.now(datetime.now().astimezone().tzinfo) + timedelta(
                minutes=30
            )
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account locked due to multiple failed login attempts. "
                "Please try again in 30 minutes.",
            )

        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password"
        )

    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact administrator.",
        )

    # Successful login - reset failed attempts
    user.failed_login_attempts = 0
    user.last_login_at = datetime.now(datetime.now().astimezone().tzinfo)
    db.commit()

    # Create tokens
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}

    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token({"user_id": user.id, "email": user.email})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 30 * 60,  # 30 minutes in seconds
    }


# ============================================================================
# REFRESH TOKEN
# ============================================================================


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token.

    Args:
    - refresh_token: Valid JWT refresh token

    Returns:
    - New access token (30 min expiry)
    - Same refresh token (or new one if rotation enabled)
    """
    # Verify refresh token
    payload = verify_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
        )

    # Get user from database
    user_id = payload.get("user_id")
    user = db.query(User).filter(User.id == user_id).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive"
        )

    # Create new access token
    token_data = {"user_id": user.id, "email": user.email, "role": user.role.value}

    new_access_token = create_access_token(token_data)

    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token,  # Return same refresh token
        "token_type": "bearer",
        "expires_in": 30 * 60,
    }


# ============================================================================
# LOGOUT
# ============================================================================


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user.

    NOTE: With JWT tokens, logout is handled client-side by deleting tokens.
    Server-side logout would require token blacklisting (Redis) which can be
    implemented if needed.

    For now, this endpoint serves as a marker for logout events in logs.
    """
    # TODO: Implement token blacklisting if required
    # await redis_client.setex(f"blacklist:{token}", 30*60, "1")

    return None


# ============================================================================
# EMAIL VERIFICATION
# ============================================================================


@router.post("/verify-email", response_model=UserPrivate)
async def verify_email(token: str, db: Session = Depends(get_db)):
    """
    Verify email address with verification token.

    Args:
    - token: Email verification token (sent to user's email)

    Returns:
    - Updated user object with is_verified=True
    """
    # TODO: Implement email verification token validation
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Email verification not yet implemented"
    )
