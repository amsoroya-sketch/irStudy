"""
Redis Encryption Service - Encrypt Session Data

Encrypts active OSCE session data before Redis storage.
Prevents memory dump attacks from exposing live conversations.

CRITICAL: Fixes Issue #4 from Security Review (Redis plaintext)
"""

from cryptography.fernet import Fernet
import json
import os
from typing import Any, Optional


class RedisEncryptionService:
    """
    Encrypt/decrypt data before Redis SET/GET operations.

    Wraps all Redis operations for OSCE session data:
    - osce:session:{attempt_id}:persona
    - osce:session:{attempt_id}:state
    - osce:session:{attempt_id}:messages
    - osce:session:{attempt_id}:actions

    Usage:
        redis_enc = RedisEncryptionService()
        encrypted_value = redis_enc.encrypt(session_data)
        await redis.set(f"osce:session:{attempt_id}:state", encrypted_value)

        encrypted = await redis.get(f"osce:session:{attempt_id}:state")
        session_data = redis_enc.decrypt(encrypted)
    """

    def __init__(self, encryption_key: bytes = None):
        """Initialize with same key as ConversationEncryptionService"""
        if encryption_key is None:
            key_b64 = os.getenv('OSCE_ENCRYPTION_KEY')
            if not key_b64:
                raise ValueError("OSCE_ENCRYPTION_KEY not set")
            encryption_key = key_b64.encode()

        self.cipher = Fernet(encryption_key)

    def encrypt(self, data: Any) -> str:
        """
        Encrypt Python object for Redis storage.

        Args:
            data: Any JSON-serializable Python object

        Returns:
            Encrypted string (UTF-8 compatible for Redis)
        """
        json_str = json.dumps(data, ensure_ascii=False)
        encrypted = self.cipher.encrypt(json_str.encode('utf-8'))
        return encrypted.decode('utf-8')  # Redis expects str, not bytes

    def decrypt(self, encrypted_data: Optional[str]) -> Any:
        """
        Decrypt Redis value back to Python object.

        Args:
            encrypted_data: Encrypted string from Redis

        Returns:
            Original Python object (dict, list, etc.)
        """
        if encrypted_data is None:
            return None

        decrypted = self.cipher.decrypt(encrypted_data.encode('utf-8'))
        return json.loads(decrypted.decode('utf-8'))


# Global instance
try:
    redis_encryption_service = RedisEncryptionService()
except ValueError:
    # Key not set - likely test environment
    redis_encryption_service = None
