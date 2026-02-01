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

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from db.base import get_db
from db.models import User
from schemas.user import UserResponse, UserUpdate, PasswordChange
from auth.dependencies import get_current_user, get_current_active_user, require_admin
from auth.security import verify_password, hash_password


router = APIRouter(prefix="/users", tags=["users"])


# ============================================================================
# CURRENT USER PROFILE
# ============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile.

    Returns:
    - User object with all non-sensitive fields
    - Requires: Valid access token
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
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
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
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
    db: Session = Depends(get_db)
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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Check new password is different
    if password_data.current_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password"
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
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
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

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    include_inactive: bool = False,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
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
