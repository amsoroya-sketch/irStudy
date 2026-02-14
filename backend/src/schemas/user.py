"""
Pydantic schemas for User model

SECURITY:
- Password never returned in responses
- Email validation enforced
- Role-based serialization
"""

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User roles matching database enum"""

    STUDENT = "student"
    EDUCATOR = "educator"
    ADMIN = "admin"


# ============================================================================
# REQUEST SCHEMAS (Input)
# ============================================================================


class UserCreate(BaseModel):
    """Schema for user registration"""

    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)
    full_name: str = Field(..., min_length=2, max_length=255)

    @validator("password")
    def password_strength(cls, v):
        """
        Validate password meets HIPAA-compliant requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserLogin(BaseModel):
    """Schema for user login"""

    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for user profile update"""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    """Schema for password change"""

    current_password: str
    new_password: str = Field(..., min_length=12, max_length=128)

    @validator("new_password")
    def password_strength(cls, v):
        """Apply same password strength validation"""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain at least one special character")
        return v


# ============================================================================
# RESPONSE SCHEMAS (Output)
# ============================================================================


class UserBase(BaseModel):
    """Base user schema (excludes sensitive fields)"""

    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)


class UserPublic(UserBase):
    """Public user profile (minimal information)"""

    pass


class UserPrivate(UserBase):
    """Private user profile (includes additional fields for own profile)"""

    last_login_at: Optional[datetime]
    updated_at: datetime


class UserAdmin(UserPrivate):
    """Admin user view (includes all non-sensitive fields)"""

    failed_login_attempts: int
    locked_until: Optional[datetime]


# ============================================================================
# AUTHENTICATION SCHEMAS
# ============================================================================


class Token(BaseModel):
    """JWT token response"""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Seconds until expiration


class TokenData(BaseModel):
    """Data encoded in JWT token"""

    user_id: int
    email: str
    role: UserRole


# ============================================================================
# EMAIL VERIFICATION SCHEMAS (Task 3.1)
# ============================================================================


class EmailVerificationRequest(BaseModel):
    """Request to verify email with token"""

    token: str = Field(..., min_length=32, max_length=64)


class EmailVerificationResponse(BaseModel):
    """Response after email verification"""

    message: str
    email: str
    verified: bool


# ============================================================================
# PASSWORD RESET SCHEMAS (Task 3.1)
# ============================================================================


class PasswordResetRequest(BaseModel):
    """Request password reset for email"""

    email: EmailStr


class PasswordResetResponse(BaseModel):
    """Response after requesting password reset"""

    message: str


class PasswordResetConfirm(BaseModel):
    """Confirm password reset with token and new password"""

    token: str = Field(..., min_length=32, max_length=64)
    new_password: str = Field(..., min_length=8, max_length=100)

    @validator("new_password")
    def validate_password_strength(cls, v):
        """Strong password validation"""
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain number")
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v):
            raise ValueError("Password must contain special character")
        return v
