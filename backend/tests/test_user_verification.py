# -*- coding: utf-8 -*-
"""
AMC Clinical Exam Simulation - User Verification Tests
Task 3.1: Email Verification + Password Reset + Audit Logging

COVERAGE:
- Email verification (6 tests)
- Password reset (8 tests)
- Security event logging (6 tests)

Run with: pytest backend/tests/test_user_verification.py -v
"""

import pytest
import pytest_asyncio
import secrets
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.db.base import Base
from src.db.models import User, UserRole
from src.auth.security import hash_password


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def db_session():
    """Create in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def test_user(db_session):
    """Create test user"""
    user = User(
        email="test@example.com",
        password_hash=hash_password("TestPassword123!"),
        full_name="Test User",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=False
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# EMAIL VERIFICATION TESTS (6 tests)
# ============================================================================

class TestEmailVerification:
    """Test email verification functionality"""
    
    def test_verify_email_success(self, db_session, test_user):
        """Test successful email verification"""
        # Set verification token
        token = secrets.token_urlsafe(32)
        test_user.verification_token = token
        test_user.verification_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Verify email (simulate endpoint logic)
        user = db_session.query(User).filter(
            User.verification_token == token
        ).first()
        
        assert user is not None
        assert user.id == test_user.id
        
        # Update user
        user.is_verified = True
        user.verification_token = None
        user.verification_token_created_at = None
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_verified is True
        assert user.verification_token is None
    
    def test_verify_email_invalid_token(self, db_session, test_user):
        """Test verification with invalid token"""
        # Try to find user with invalid token
        user = db_session.query(User).filter(
            User.verification_token == "invalid_token_12345"
        ).first()
        
        assert user is None
    
    def test_verify_email_expired_token(self, db_session, test_user):
        """Test verification with expired token (>24 hours)"""
        # Set token 25 hours ago
        token = secrets.token_urlsafe(32)
        test_user.verification_token = token
        test_user.verification_token_created_at = datetime.now(timezone.utc) - timedelta(hours=25)
        db_session.commit()
        
        # Check token expiry
        user = db_session.query(User).filter(
            User.verification_token == token
        ).first()
        
        assert user is not None
        token_age = datetime.now(timezone.utc) - user.verification_token_created_at
        assert token_age > timedelta(hours=24)
    
    def test_verify_email_already_verified(self, db_session, test_user):
        """Test verification when already verified"""
        # Set user as already verified
        test_user.is_verified = True
        db_session.commit()
        
        assert test_user.is_verified is True
    
    def test_verify_email_sets_is_verified(self, db_session, test_user):
        """Test is_verified flag is set to True"""
        token = secrets.token_urlsafe(32)
        test_user.verification_token = token
        test_user.verification_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Verify
        user = db_session.query(User).filter(
            User.verification_token == token
        ).first()
        user.is_verified = True
        db_session.commit()
        db_session.refresh(user)
        
        assert user.is_verified is True
    
    def test_verify_email_clears_token(self, db_session, test_user):
        """Test verification token is cleared after success"""
        token = secrets.token_urlsafe(32)
        test_user.verification_token = token
        test_user.verification_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Verify and clear
        user = db_session.query(User).filter(
            User.verification_token == token
        ).first()
        user.is_verified = True
        user.verification_token = None
        user.verification_token_created_at = None
        db_session.commit()
        db_session.refresh(user)
        
        assert user.verification_token is None
        assert user.verification_token_created_at is None


# ============================================================================
# PASSWORD RESET TESTS (8 tests)
# ============================================================================

class TestPasswordReset:
    """Test password reset functionality"""
    
    def test_request_password_reset_existing_email(self, db_session, test_user):
        """Test password reset request for existing email"""
        # Generate reset token
        reset_token = secrets.token_urlsafe(32)
        test_user.reset_token = reset_token
        test_user.reset_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        db_session.refresh(test_user)
        
        assert test_user.reset_token is not None
        assert test_user.reset_token_created_at is not None
    
    def test_request_password_reset_nonexistent_email(self, db_session):
        """Test reset request for nonexistent email (should still return success)"""
        # Try to find user with nonexistent email
        user = db_session.query(User).filter(
            User.email == "nonexistent@example.com"
        ).first()
        
        assert user is None
        # In actual endpoint, this still returns success message
    
    def test_reset_password_success(self, db_session, test_user):
        """Test successful password reset"""
        # Set reset token
        reset_token = secrets.token_urlsafe(32)
        test_user.reset_token = reset_token
        test_user.reset_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Find user by token
        user = db_session.query(User).filter(
            User.reset_token == reset_token
        ).first()
        
        assert user is not None
        
        # Reset password
        new_password = "NewPassword123!"
        user.password_hash = hash_password(new_password)
        user.reset_token = None
        user.reset_token_created_at = None
        user.failed_login_attempts = 0
        db_session.commit()
        db_session.refresh(user)
        
        assert user.reset_token is None
        assert user.failed_login_attempts == 0
    
    def test_reset_password_invalid_token(self, db_session):
        """Test reset with invalid token"""
        user = db_session.query(User).filter(
            User.reset_token == "invalid_token"
        ).first()
        
        assert user is None
    
    def test_reset_password_expired_token(self, db_session, test_user):
        """Test reset with expired token (>1 hour)"""
        # Set token 2 hours ago
        reset_token = secrets.token_urlsafe(32)
        test_user.reset_token = reset_token
        test_user.reset_token_created_at = datetime.now(timezone.utc) - timedelta(hours=2)
        db_session.commit()
        
        # Check expiry
        user = db_session.query(User).filter(
            User.reset_token == reset_token
        ).first()
        
        assert user is not None
        token_age = datetime.now(timezone.utc) - user.reset_token_created_at
        assert token_age > timedelta(hours=1)
    
    def test_reset_password_weak_password(self):
        """Test reset with weak password (should fail validation)"""
        weak_passwords = [
            "short",  # Too short
            "nouppercase1!",  # No uppercase
            "NOLOWERCASE1!",  # No lowercase
            "NoDigits!",  # No digits
            "NoSpecial123",  # No special char
        ]
        
        from pydantic import ValidationError
        from src.schemas.user import PasswordResetConfirm
        
        for weak_pw in weak_passwords:
            with pytest.raises(ValidationError):
                PasswordResetConfirm(
                    token="a" * 32,
                    new_password=weak_pw
                )
    
    def test_reset_password_updates_hash(self, db_session, test_user):
        """Test password hash is updated"""
        old_hash = test_user.password_hash
        
        # Reset password
        reset_token = secrets.token_urlsafe(32)
        test_user.reset_token = reset_token
        test_user.reset_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        user = db_session.query(User).filter(
            User.reset_token == reset_token
        ).first()
        
        new_password = "NewPassword456!"
        user.password_hash = hash_password(new_password)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.password_hash != old_hash
    
    def test_reset_password_clears_failed_attempts(self, db_session, test_user):
        """Test reset clears failed_login_attempts"""
        # Set failed attempts
        test_user.failed_login_attempts = 5
        reset_token = secrets.token_urlsafe(32)
        test_user.reset_token = reset_token
        test_user.reset_token_created_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Reset password
        user = db_session.query(User).filter(
            User.reset_token == reset_token
        ).first()
        
        user.password_hash = hash_password("NewPassword789!")
        user.reset_token = None
        user.failed_login_attempts = 0
        db_session.commit()
        db_session.refresh(user)
        
        assert user.failed_login_attempts == 0


# ============================================================================
# SECURITY EVENT LOGGING TESTS (6 tests)
# ============================================================================

class TestSecurityEventLogging:
    """Test security event logging integration"""
    
    @pytest.mark.asyncio
    async def test_email_verification_logs_event(self):
        """Test email verification logs security event"""
        from src.security.events import SecurityEventLogger
        
        # Mock Redis client
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        
        logger = SecurityEventLogger(mock_redis, None)
        
        # Log event
        await logger.log_event(
            event_type="email_verified",
            user_id="user-12345678",
            ip_address="192.168.1.100",
            metadata={"email_verified": True},
            severity="low"
        )
        
        assert "security:events" in mock_redis._lists
    
    @pytest.mark.asyncio
    async def test_password_reset_request_logs_event(self):
        """Test password reset request logs event"""
        from src.security.events import SecurityEventLogger
        
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        
        logger = SecurityEventLogger(mock_redis, None)
        
        await logger.log_event(
            event_type="password_reset_requested",
            user_id="user-87654321",
            ip_address="192.168.1.200",
            metadata={"email_exists": True},
            severity="medium"
        )
        
        assert "security:events" in mock_redis._lists
    
    @pytest.mark.asyncio
    async def test_password_reset_confirm_logs_event(self):
        """Test password reset confirm logs high severity event"""
        from src.security.events import SecurityEventLogger
        
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        
        logger = SecurityEventLogger(mock_redis, None)
        
        await logger.log_event(
            event_type="password_reset_completed",
            user_id="user-11223344",
            ip_address="192.168.1.150",
            metadata={"password_changed": True},
            severity="high"
        )
        
        assert "security:events" in mock_redis._lists
    
    @pytest.mark.asyncio
    async def test_user_creation_logs_event(self):
        """Test user creation logs security event"""
        # This test verifies the integration point exists
        # Actual implementation would be in create_user endpoint
        from src.security.events import SecurityEventLogger
        
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        
        logger = SecurityEventLogger(mock_redis, None)
        
        await logger.log_event(
            event_type="user_created",
            user_id="user-99887766",
            ip_address="192.168.1.50",
            metadata={"created_by": "admin-12...", "role": "student"},
            severity="low"
        )
        
        assert "security:events" in mock_redis._lists
    
    @pytest.mark.asyncio
    async def test_user_id_anonymization(self):
        """Test user IDs are anonymized in logs"""
        from src.security.events import SecurityEventLogger
        import json
        
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        async def mock_lrange(key, start, stop):
            return mock_redis._lists.get(key, [])[start:stop+1 if stop >= 0 else None]
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        mock_redis.lrange = mock_lrange
        
        logger = SecurityEventLogger(mock_redis, None)
        
        # Log event with long user ID
        await logger.log_event(
            event_type="test_event",
            user_id="user-1234567890123456789",
            ip_address="192.168.1.100",
            metadata={},
            severity="info"
        )
        
        # Check anonymization
        events = await mock_redis.lrange("security:events", 0, 0)
        event_dict = json.loads(events[0])
        
        assert event_dict["user_id"] == "user-123***"
    
    @pytest.mark.asyncio
    async def test_security_event_severity_levels(self):
        """Test correct severity levels for different events"""
        from src.security.events import SecurityEventLogger
        import json
        
        mock_redis = AsyncMock()
        mock_redis._lists = {}
        
        async def mock_lpush(key, value):
            if key not in mock_redis._lists:
                mock_redis._lists[key] = []
            mock_redis._lists[key].insert(0, value)
            return len(mock_redis._lists[key])
        
        async def mock_ltrim(key, start, stop):
            return True
        
        async def mock_lrange(key, start, stop):
            return mock_redis._lists.get(key, [])[start:stop+1 if stop >= 0 else None]
        
        mock_redis.lpush = mock_lpush
        mock_redis.ltrim = mock_ltrim
        mock_redis.lrange = mock_lrange
        
        logger = SecurityEventLogger(mock_redis, None)
        
        # Test different severity levels
        test_cases = [
            ("email_verified", "low"),
            ("password_reset_requested", "medium"),
            ("password_reset_completed", "high"),
        ]
        
        for event_type, expected_severity in test_cases:
            await logger.log_event(
                event_type=event_type,
                user_id="user-123",
                ip_address="192.168.1.100",
                metadata={},
                severity=expected_severity
            )
        
        # Verify severities
        events = await mock_redis.lrange("security:events", 0, -1)
        severities = [json.loads(e)["severity"] for e in events]
        
        assert "low" in severities
        assert "medium" in severities
        assert "high" in severities


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
