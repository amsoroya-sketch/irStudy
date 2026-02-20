import os
import pytest
from src.security.encryption import ConversationEncryptionService


def test_conversation_encryption_roundtrip():
    """Test AES-256-GCM encrypt → decrypt returns original data"""
    # 32-byte (256-bit) random key for AES-256-GCM
    key = os.urandom(32)
    service = ConversationEncryptionService(encryption_key=key)

    original_conversation = [
        {
            "timestamp": "2026-02-09T10:05:23Z",
            "speaker": "patient",
            "message": "I've been having chest pain for 2 hours"
        },
        {
            "timestamp": "2026-02-09T10:05:45Z",
            "speaker": "student",
            "message": "Can you describe the pain?"
        }
    ]

    # Encrypt
    encrypted = service.encrypt_conversation(original_conversation)

    # Verify encrypted is base64 string
    assert isinstance(encrypted, str)
    assert len(encrypted) > 50  # nonce (12) + ciphertext + GCM tag (16) + base64 overhead

    # Decrypt
    decrypted = service.decrypt_conversation(encrypted)

    # Verify roundtrip
    assert decrypted == original_conversation
    assert decrypted[0]['message'] == "I've been having chest pain for 2 hours"


def test_conversation_encryption_tamper_detection():
    """Test AES-256-GCM authentication tag detects tampered ciphertext"""
    key = os.urandom(32)
    service = ConversationEncryptionService(encryption_key=key)

    conversation = [{"speaker": "patient", "message": "test"}]
    encrypted = service.encrypt_conversation(conversation)

    # Tamper with ciphertext (corrupt last 10 characters)
    tampered = encrypted[:-10] + "AAAAAAAAAA"

    # Verify tamper detection (GCM authentication tag will fail)
    with pytest.raises(Exception):  # InvalidTag or binascii.Error
        service.decrypt_conversation(tampered)


def test_conversation_encryption_different_keys():
    """Test AES-256-GCM decryption fails with wrong key"""
    key1 = os.urandom(32)
    key2 = os.urandom(32)

    service1 = ConversationEncryptionService(encryption_key=key1)
    service2 = ConversationEncryptionService(encryption_key=key2)

    conversation = [{"speaker": "patient", "message": "test"}]
    encrypted = service1.encrypt_conversation(conversation)

    # Verify wrong key fails (GCM authentication tag invalid)
    with pytest.raises(Exception):
        service2.decrypt_conversation(encrypted)
