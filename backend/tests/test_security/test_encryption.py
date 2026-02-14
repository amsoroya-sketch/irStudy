import pytest
from src.security.encryption import ConversationEncryptionService
from cryptography.fernet import Fernet


def test_conversation_encryption_roundtrip():
    """Test encrypt → decrypt returns original data"""
    # Setup
    key = Fernet.generate_key()
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
    assert len(encrypted) > 50  # Ciphertext + base64 overhead

    # Decrypt
    decrypted = service.decrypt_conversation(encrypted)

    # Verify roundtrip
    assert decrypted == original_conversation
    assert decrypted[0]['message'] == "I've been having chest pain for 2 hours"


def test_conversation_encryption_tamper_detection():
    """Test HMAC detects tampered ciphertext"""
    key = Fernet.generate_key()
    service = ConversationEncryptionService(encryption_key=key)

    conversation = [{"speaker": "patient", "message": "test"}]
    encrypted = service.encrypt_conversation(conversation)

    # Tamper with ciphertext (flip one bit)
    tampered = encrypted[:-10] + "AAAAAAAAAA"

    # Verify tamper detection
    with pytest.raises(Exception):  # InvalidToken or DecryptionError
        service.decrypt_conversation(tampered)


def test_conversation_encryption_different_keys():
    """Test decryption fails with wrong key"""
    key1 = Fernet.generate_key()
    key2 = Fernet.generate_key()

    service1 = ConversationEncryptionService(encryption_key=key1)
    service2 = ConversationEncryptionService(encryption_key=key2)

    conversation = [{"speaker": "patient", "message": "test"}]
    encrypted = service1.encrypt_conversation(conversation)

    # Verify wrong key fails
    with pytest.raises(Exception):
        service2.decrypt_conversation(encrypted)
