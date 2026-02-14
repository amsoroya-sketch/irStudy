"""
Tests for security input validation schemas

Validates XSS/SQL injection protection (Step 7 of PRD 2)
"""

import pytest
from pydantic import ValidationError
from src.schemas.security import (
    OSCESessionCreate,
    StudentMessage,
    SpecialtyEnum,
    DifficultyEnum,
    SessionTypeEnum,
)


def test_osce_session_create_valid():
    """Test valid OSCE session creation"""
    data = {
        "persona_id": "550e8400-e29b-41d4-a716-446655440000",
        "session_type": "individual"
    }

    session = OSCESessionCreate(**data)
    assert session.persona_id == "550e8400-e29b-41d4-a716-446655440000"
    assert session.session_type == SessionTypeEnum.INDIVIDUAL


def test_osce_session_create_invalid_uuid():
    """Test invalid UUID rejected"""
    data = {
        "persona_id": "not-a-uuid",
        "session_type": "individual"
    }

    with pytest.raises(ValidationError) as exc_info:
        OSCESessionCreate(**data)

    # Verify it's a validation error for persona_id
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("persona_id",) for error in errors)


def test_osce_session_create_invalid_session_type():
    """Test invalid session_type rejected (SQL injection attempt)"""
    data = {
        "persona_id": "550e8400-e29b-41d4-a716-446655440000",
        "session_type": "'; DROP TABLE osce_attempts; --"
    }

    with pytest.raises(ValidationError) as exc_info:
        OSCESessionCreate(**data)

    # Verify it's a validation error for session_type
    errors = exc_info.value.errors()
    assert any(error["loc"] == ("session_type",) for error in errors)


def test_student_message_xss_sanitization():
    """Test XSS attempt is sanitized"""
    data = {
        "message": "Can you help <script>alert('XSS')</script> me?"
    }

    message = StudentMessage(**data)

    # HTML entities escaped - <script> becomes &lt;script&gt;
    assert "<script>" not in message.message
    assert "&lt;script&gt;" in message.message or "alert" not in message.message


def test_student_message_too_long():
    """Test message length limit enforced"""
    data = {
        "message": "A" * 1001  # Over 1000 char limit
    }

    with pytest.raises(ValidationError) as exc_info:
        StudentMessage(**data)

    # Verify it's a validation error for message length
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("message",) and "at most 1000 characters" in str(error)
        for error in errors
    )


def test_specialty_enum_valid_values():
    """Test SpecialtyEnum accepts valid specialties"""
    assert SpecialtyEnum.CARDIOLOGY.value == "cardiology"
    assert SpecialtyEnum.PSYCHIATRY.value == "psychiatry"
    assert SpecialtyEnum.SURGERY.value == "surgery"


def test_specialty_enum_rejects_invalid():
    """Test SpecialtyEnum rejects invalid values"""
    with pytest.raises(ValueError):
        SpecialtyEnum("hacking'; DROP TABLE users; --")


def test_difficulty_enum_valid_values():
    """Test DifficultyEnum accepts valid difficulties"""
    assert DifficultyEnum.FOUNDATION.value == "foundation"
    assert DifficultyEnum.INTERMEDIATE.value == "intermediate"
    assert DifficultyEnum.ADVANCED.value == "advanced"


def test_session_type_enum_valid_values():
    """Test SessionTypeEnum accepts valid session types"""
    assert SessionTypeEnum.INDIVIDUAL.value == "individual"
    assert SessionTypeEnum.MOCK_EXAM.value == "mock_exam"
