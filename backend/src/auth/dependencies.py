"""
FastAPI dependency injection for authentication

USAGE:
    @app.get("/protected")
    def protected_route(current_user: User = Depends(get_current_user)):
        return {"user": current_user.email}

    @app.get("/admin-only")
    def admin_route(current_user: User = Depends(require_admin)):
        return {"admin": current_user.email}
"""

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from src.db.base import get_db
from src.db.models import User, UserRole
from src.auth.security import verify_access_token


# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session

    Returns:
        Current user object

    Raises:
        HTTPException 401: Invalid or expired token
        HTTPException 404: User not found
        HTTPException 403: Account inactive or locked
    """
    # Normal authentication flow
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token from Authorization header
    token = credentials.credentials

    # Verify and decode token
    payload = verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user ID from payload
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Fetch user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Check if account is active
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    # Check if account is locked
    if user.locked_until is not None:
        from datetime import datetime

        if user.locked_until > datetime.now(user.locked_until.tzinfo):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is temporarily locked due to multiple failed login attempts",
            )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user (verified account).

    Args:
        current_user: Current user from token

    Returns:
        Current user if active and verified

    Raises:
        HTTPException 403: Account not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email address.",
        )

    return current_user


async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if admin

    Raises:
        HTTPException 403: Insufficient permissions
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin access required.",
        )

    return current_user


async def require_educator(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require educator or admin role.

    Args:
        current_user: Current authenticated user

    Returns:
        Current user if educator or admin

    Raises:
        HTTPException 403: Insufficient permissions
    """
    if current_user.role not in [UserRole.EDUCATOR, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Educator access required.",
        )

    return current_user


# ============================================================================
# RBAC PERMISSION DEPENDENCIES (Task 3.2)
# ============================================================================

from .permissions import Permission, has_permission
from ..security.events import SecurityEventLogger


def require_permission(permission: Permission):
    """
    Dependency factory to check if current user has required permission.

    Usage:
        @router.post("/mcqs")
        async def create_mcq(
            current_user: User = Depends(require_permission(Permission.MCQ_CREATE))
        ):
            ...

    Logs all permission checks to security events.

    Args:
        permission: Required permission

    Returns:
        Dependency function that checks permission
    """

    async def check_permission(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if user has the required permission"""
        if not has_permission(current_user.role, permission):
            # Log permission denied
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                event_logger = SecurityEventLogger(redis_url)
                await event_logger.log_event(
                    event_type="permission_denied",
                    user_id=str(current_user.id)[:8] + "...",
                    ip_address="system",
                    metadata={"permission": permission.value, "user_role": current_user.role.value},
                    severity="medium",
                )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission.value} required",
            )

        # Log permission granted
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            event_logger = SecurityEventLogger(redis_url)
            await event_logger.log_event(
                event_type="permission_granted",
                user_id=str(current_user.id)[:8] + "...",
                ip_address="system",
                metadata={"permission": permission.value, "user_role": current_user.role.value},
                severity="low",
            )

        return current_user

    return check_permission


def require_any_permission(*permissions: Permission):
    """
    Dependency factory to check if user has ANY of the required permissions.

    Usage:
        @router.get("/content")
        async def view_content(
            current_user: User = Depends(require_any_permission(
                Permission.MCQ_VIEW, Permission.OSCE_VIEW
            ))
        ):
            ...

    Args:
        *permissions: Required permissions (OR logic)

    Returns:
        Dependency function that checks permissions
    """

    async def check_permissions(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if user has any of the required permissions"""
        for perm in permissions:
            if has_permission(current_user.role, perm):
                # Log successful check
                redis_url = os.getenv("REDIS_URL")
                if redis_url:
                    event_logger = SecurityEventLogger(redis_url)
                    await event_logger.log_event(
                        event_type="permission_granted",
                        user_id=str(current_user.id)[:8] + "...",
                        ip_address="system",
                        metadata={
                            "permission": perm.value,
                            "user_role": current_user.role.value,
                            "check_type": "any_permission",
                        },
                        severity="low",
                    )
                return current_user

        # Log permission denied
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            event_logger = SecurityEventLogger(redis_url)
            await event_logger.log_event(
                event_type="permission_denied",
                user_id=str(current_user.id)[:8] + "...",
                ip_address="system",
                metadata={
                    "required_permissions": [p.value for p in permissions],
                    "user_role": current_user.role.value,
                    "check_type": "any_permission",
                },
                severity="medium",
            )

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"One of these permissions required: {[p.value for p in permissions]}",
        )

    return check_permissions


def require_all_permissions(*permissions: Permission):
    """
    Dependency factory to check if user has ALL of the required permissions.

    Usage:
        @router.post("/advanced-action")
        async def advanced_action(
            current_user: User = Depends(require_all_permissions(
                Permission.MCQ_UPDATE, Permission.OSCE_UPDATE
            ))
        ):
            ...

    Args:
        *permissions: Required permissions (AND logic)

    Returns:
        Dependency function that checks permissions
    """

    async def check_permissions(current_user: User = Depends(get_current_active_user)) -> User:
        """Check if user has all of the required permissions"""
        missing_permissions = []

        for perm in permissions:
            if not has_permission(current_user.role, perm):
                missing_permissions.append(perm)

        if missing_permissions:
            # Log permission denied
            redis_url = os.getenv("REDIS_URL")
            if redis_url:
                event_logger = SecurityEventLogger(redis_url)
                await event_logger.log_event(
                    event_type="permission_denied",
                    user_id=str(current_user.id)[:8] + "...",
                    ip_address="system",
                    metadata={
                        "required_permissions": [p.value for p in permissions],
                        "missing_permissions": [p.value for p in missing_permissions],
                        "user_role": current_user.role.value,
                        "check_type": "all_permissions",
                    },
                    severity="medium",
                )

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All these permissions required: {[p.value for p in permissions]}",
            )

        # Log permission granted
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            event_logger = SecurityEventLogger(redis_url)
            await event_logger.log_event(
                event_type="permission_granted",
                user_id=str(current_user.id)[:8] + "...",
                ip_address="system",
                metadata={
                    "permissions": [p.value for p in permissions],
                    "user_role": current_user.role.value,
                    "check_type": "all_permissions",
                },
                severity="low",
            )

        return current_user

    return check_permissions
