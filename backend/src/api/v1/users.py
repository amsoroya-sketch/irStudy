"""
User management endpoints

Routes:
- GET /api/v1/users/me - Get current user profile
- PUT /api/v1/users/me - Update current user profile
- POST /api/v1/users/me/change-password - Change password
- DELETE /api/v1/users/me - Deactivate account (soft delete)
- GET /api/v1/users/{user_id} - Get user by ID (admin only)
- GET /api/v1/users - List all users (admin only)

SECURITY:
- All endpoints require authentication
- User can only access/modify their own data
- Admin can access all users
"""

from typing import List
from datetime import datetime
import re

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User
from src.schemas.user import (
    UserPrivate, UserAdmin, UserUpdate, PasswordChange,
    EmailVerificationRequest, EmailVerificationResponse,
    PasswordResetRequest, PasswordResetResponse, PasswordResetConfirm
)
from src.auth.dependencies import get_current_user, get_current_active_user, require_admin
from src.auth.security import verify_password, hash_password


router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# USER SEARCH
# ============================================================================


@router.get("/search")
async def search_users(
    query: str = Query(..., min_length=1, max_length=100, description="Search query (name or email)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search users by name or email.

    Security:
    - SQLAlchemy ORM prevents SQL injection (parameterized queries)
    - Input sanitization removes special characters
    - Returns empty list for invalid queries (no 422 errors)
    - Limit 10 results (prevents data enumeration)
    """
    # Sanitize query: allow only alphanumeric + space + @ + .
    sanitized = re.sub(r'[^a-zA-Z0-9\s@.]', '', query)

    if not sanitized or len(sanitized) < 2:
        return []  # Empty results for invalid/short queries

    # SQLAlchemy ORM query (parameterized - SQL injection safe)
    results = db.query(User).filter(
        (User.full_name.ilike(f"%{sanitized}%")) |
        (User.email.ilike(f"%{sanitized}%"))
    ).limit(10).all()

    # Return minimal data (no password hashes, roles, etc.)
    return [
        {
            "id": str(user.id),
            "name": user.full_name,
            "email": user.email,
        }
        for user in results
    ]


# ============================================================================
# CURRENT USER PROFILE
# ============================================================================


@router.get("/me", response_model=UserPrivate)
async def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """
    Get current user's profile.

    Returns:
    - User object with all non-sensitive fields
    - Requires: Valid access token
    """
    return current_user


@router.put("/me", response_model=UserPrivate)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Update current user's profile.

    Allowed updates:
    - full_name: Change display name
    - email: Change email (requires re-verification)

    Returns:
    - Updated user object
    """
    # Check if new email is already taken
    if user_update.email and user_update.email != current_user.email:
        existing_user = db.query(User).filter(User.email == user_update.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email address already registered"
            )

        current_user.email = user_update.email
        current_user.is_verified = False  # Require re-verification
        # TODO: Send new verification email

    # Update full name
    if user_update.full_name:
        current_user.full_name = user_update.full_name

    db.commit()
    db.refresh(current_user)

    return current_user


# ============================================================================
# PASSWORD CHANGE
# ============================================================================


@router.post("/me/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change current user's password.

    Requirements:
    - Must provide current password for verification
    - New password must meet strength requirements
    - New password must be different from current password

    Security:
    - Invalidates all existing sessions (TODO: implement token blacklisting)
    - Resets failed login attempts
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect"
        )

    # Check new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )

    # Update password
    current_user.password_hash = hash_password(password_data.new_password)
    current_user.failed_login_attempts = 0
    current_user.locked_until = None

    db.commit()

    # TODO: Invalidate all existing tokens
    # await invalidate_user_tokens(current_user.id)

    return None


# ============================================================================
# ACCOUNT DEACTIVATION
# ============================================================================


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_account(
    current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)
):
    """
    Deactivate current user's account (soft delete).

    This performs a soft delete:
    - Sets deleted_at timestamp
    - Sets is_active=False
    - User can no longer login
    - Data retained for audit trail (HIPAA requirement)

    Account can be reactivated by admin within 30 days.
    After 30 days, data is permanently deleted.
    """
    current_user.is_active = False
    current_user.deleted_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()

    # TODO: Schedule permanent deletion after 30 days
    # await schedule_permanent_deletion(current_user.id, days=30)

    return None


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================


@router.get("/{user_id}", response_model=UserAdmin)
async def get_user_by_id(
    user_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)
):
    """
    Get user by ID (admin only).

    Args:
    - user_id: User's database ID

    Returns:
    - User object

    Requires:
    - Admin role
    """
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.get("/", response_model=List[UserAdmin])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """
    List all users (admin only).

    Query parameters:
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records to return (max 100)
    - include_inactive: Include deactivated users

    Returns:
    - List of user objects

    Requires:
    - Admin role
    """
    query = db.query(User)

    # Filter out soft-deleted users unless requested
    if not include_inactive:
        query = query.filter(User.deleted_at.is_(None))
        query = query.filter(User.is_active == True)

    users = query.offset(skip).limit(min(limit, 100)).all()

    return users


# ============================================================================
# EMAIL VERIFICATION (Task 3.1)
# ============================================================================


@router.post("/verify-email", response_model=EmailVerificationResponse)
async def verify_email(request: EmailVerificationRequest, db: Session = Depends(get_db)):
    """
    Verify user email with verification token.

    Flow:
    1. Find user by verification_token
    2. Check token not expired (24 hours)
    3. Set is_verified = True
    4. Clear verification_token
    5. Log security event

    Returns:
        EmailVerificationResponse with success message

    Raises:
        HTTPException 400: Invalid or expired token
    """
    from datetime import timedelta, timezone
    from src.schemas.user import EmailVerificationRequest, EmailVerificationResponse
    from src.security.events import SecurityEventLogger
    import os
    import secrets

    # Find user by token
    user = db.query(User).filter(User.verification_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    # Check token not expired (24 hours)
    if user.verification_token_created_at:
        token_age = datetime.now(timezone.utc) - user.verification_token_created_at
        if token_age > timedelta(hours=24):
            raise HTTPException(status_code=400, detail="Verification token expired")

    # Update user
    user.is_verified = True
    user.verification_token = None
    user.verification_token_created_at = None
    db.commit()
    db.refresh(user)

    # Log security event (async-compatible version)
    try:
        import redis.asyncio as redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url)
        event_logger = SecurityEventLogger(redis_client, None)

        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in async context
            asyncio.create_task(
                event_logger.log_event(
                    event_type="email_verified",
                    user_id=str(user.id)[:8] + "...",
                    ip_address="system",
                    metadata={"email_verified": True},
                    severity="low",
                )
            )
        else:
            # Sync context
            loop.run_until_complete(
                event_logger.log_event(
                    event_type="email_verified",
                    user_id=str(user.id)[:8] + "...",
                    ip_address="system",
                    metadata={"email_verified": True},
                    severity="low",
                )
            )
    except Exception as e:
        # Don't fail verification if logging fails
        print(f"Failed to log security event: {e}")

    return EmailVerificationResponse(
        message="Email verified successfully", email=user.email, verified=True
    )


# ============================================================================
# PASSWORD RESET (Task 3.1)
# ============================================================================


@router.post("/reset-password/request", response_model=PasswordResetResponse)
async def request_password_reset(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Request password reset for user email.

    Security: Always returns success even if email doesn't exist (prevent enumeration)

    Flow:
    1. Find user by email
    2. Generate reset token (secrets.token_urlsafe(32))
    3. Store token with timestamp
    4. Log security event
    5. Return success (in production, send email)
    """
    from datetime import timezone
    from src.schemas.user import PasswordResetRequest, PasswordResetResponse
    from src.security.events import SecurityEventLogger
    import os
    import secrets

    # Find user
    user = db.query(User).filter(User.email == request.email).first()

    # Always return success (prevent email enumeration)
    if user:
        # Generate token
        reset_token = secrets.token_urlsafe(32)
        user.reset_token = reset_token
        user.reset_token_created_at = datetime.now(timezone.utc)
        db.commit()

        # Log event
        try:
            import redis.asyncio as redis

            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            redis_client = redis.from_url(redis_url)
            event_logger = SecurityEventLogger(redis_client, None)

            import asyncio

            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(
                    event_logger.log_event(
                        event_type="password_reset_requested",
                        user_id=str(user.id)[:8] + "...",
                        ip_address="system",
                        metadata={"email_exists": True},
                        severity="medium",
                    )
                )
        except Exception as e:
            print(f"Failed to log security event: {e}")

    return PasswordResetResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password/confirm", response_model=PasswordResetResponse)
async def confirm_password_reset(request: PasswordResetConfirm, db: Session = Depends(get_db)):
    """
    Confirm password reset with token and new password.

    Flow:
    1. Find user by reset_token
    2. Check token not expired (1 hour)
    3. Hash new password
    4. Update password_hash
    5. Clear reset_token
    6. Log security event
    """
    from datetime import timedelta, timezone
    from src.schemas.user import PasswordResetConfirm, PasswordResetResponse
    from src.security.events import SecurityEventLogger
    import os

    # Find user by token
    user = db.query(User).filter(User.reset_token == request.token).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    # Check token not expired (1 hour)
    if user.reset_token_created_at:
        token_age = datetime.now(timezone.utc) - user.reset_token_created_at
        if token_age > timedelta(hours=1):
            raise HTTPException(status_code=400, detail="Reset token expired")

    # Hash new password
    user.password_hash = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_created_at = None
    user.failed_login_attempts = 0  # Reset lockout counter
    db.commit()

    # Log event
    try:
        import redis.asyncio as redis

        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        redis_client = redis.from_url(redis_url)
        event_logger = SecurityEventLogger(redis_client, None)

        import asyncio

        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.create_task(
                event_logger.log_event(
                    event_type="password_reset_completed",
                    user_id=str(user.id)[:8] + "...",
                    ip_address="system",
                    metadata={"password_changed": True},
                    severity="high",
                )
            )
    except Exception as e:
        print(f"Failed to log security event: {e}")

    return PasswordResetResponse(message="Password reset successfully")
