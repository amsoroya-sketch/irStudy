import pytest
from src.security.redis_encryption import RedisEncryptionService
from cryptography.fernet import Fernet


def test_redis_encryption_roundtrip():
    """Test encrypt → decrypt returns original data"""
    key = Fernet.generate_key()
    service = RedisEncryptionService(encryption_key=key)

    original_data = {
        "session_state": "conversation",
        "emotional_state": "CAUTIOUSLY_OPEN",
        "pain_level": 8,
        "message_count": 12
    }

    encrypted = service.encrypt(original_data)
    decrypted = service.decrypt(encrypted)

    assert decrypted == original_data


def test_redis_encryption_handles_none():
    """Test decrypting None returns None (key not found)"""
    key = Fernet.generate_key()
    service = RedisEncryptionService(encryption_key=key)

    result = service.decrypt(None)
    assert result is None
