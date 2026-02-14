import pytest
from src.security.phi_anonymizer import PHIAnonymizer


def test_email_redaction():
    """Test email addresses are redacted"""
    message = "Contact me at john.smith@example.com or jane@test.org.au"
    anonymized = PHIAnonymizer.anonymize(message)

    assert "[EMAIL_REDACTED]" in anonymized
    assert "john.smith@example.com" not in anonymized
    assert "jane@test.org.au" not in anonymized


def test_phone_redaction_australian():
    """Test Australian phone numbers are redacted"""
    messages = [
        "Call 0412 345 678",  # Mobile
        "Phone: +61 2 9876 5432",  # Sydney landline
        "Contact 1300 123 456",  # 1300 number
        "Hotline 1800 987 654",  # 1800 number
    ]

    for message in messages:
        anonymized = PHIAnonymizer.anonymize(message)
        assert "[PHONE_REDACTED]" in anonymized, f"Failed for: {message}"


def test_medicare_redaction():
    """Test Medicare numbers are redacted"""
    message = "My Medicare number is 1234567890 1"
    anonymized = PHIAnonymizer.anonymize(message)

    assert "[MEDICARE_REDACTED]" in anonymized
    assert "1234567890" not in anonymized


def test_dob_redaction():
    """Test dates of birth are redacted"""
    messages = [
        "DOB: 15/03/1985",
        "Born on 03-07-1990",
        "Birthday 7/12/95",
    ]

    for message in messages:
        anonymized = PHIAnonymizer.anonymize(message)
        assert "[DOB_REDACTED]" in anonymized, f"Failed for: {message}"


def test_hash_identifier():
    """Test identifier hashing is consistent"""
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    hash1 = PHIAnonymizer.hash_identifier(user_id)
    hash2 = PHIAnonymizer.hash_identifier(user_id)

    # Same input = same hash (deterministic)
    assert hash1 == hash2
    assert len(hash1) == 12  # Truncated to 12 chars
    assert user_id not in hash1  # Original ID not visible


def test_multiple_phi_types():
    """Test multiple PHI types in one message"""
    message = "I'm John Smith, email john@example.com, phone 0412345678, DOB 15/03/1985"
    anonymized = PHIAnonymizer.anonymize(message)

    assert "[EMAIL_REDACTED]" in anonymized
    assert "[PHONE_REDACTED]" in anonymized
    assert "[DOB_REDACTED]" in anonymized
    assert "john@example.com" not in anonymized
    assert "0412345678" not in anonymized
