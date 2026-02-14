"""
Conversation Encryption Service - GDPR Article 32 Compliance

Encrypts conversation_history JSONB before PostgreSQL storage.
Uses Fernet (AES-128-CBC) with key from Vault.

CRITICAL: Fixes Issue #1 from Security Review (unencrypted conversations)
"""

from cryptography.fernet import Fernet
import base64
import json
import os
from typing import List, Dict, Any


class ConversationEncryptionService:
    """
    Encrypt/decrypt OSCE conversations for PostgreSQL storage.

    Usage:
        encryption_service = ConversationEncryptionService()
        encrypted = encryption_service.encrypt_conversation(messages)
        await db.execute(
            "UPDATE osce_attempts SET conversation_history = :encrypted",
            {"encrypted": encrypted}
        )

    Security:
        - Uses Fernet (AES-128-CBC + HMAC for integrity)
        - Key from Vault (secret/ai-osce/encryption-key)
        - Base64 encoding for PostgreSQL TEXT storage
    """

    def __init__(self, encryption_key: bytes = None):
        """
        Initialize encryption service.

        Args:
            encryption_key: 32-byte Fernet key from Vault
                            If None, reads from OSCE_ENCRYPTION_KEY env var
        """
        if encryption_key is None:
            # Read from environment (Vault-backed in production)
            key_b64 = os.getenv('OSCE_ENCRYPTION_KEY')
            if not key_b64:
                raise ValueError(
                    "OSCE_ENCRYPTION_KEY not set. "
                    "Run: vault kv get -field=value secret/ai-osce/encryption-key"
                )
            encryption_key = key_b64.encode()

        self.cipher = Fernet(encryption_key)

    def encrypt_conversation(self, conversation: List[Dict[str, Any]]) -> str:
        """
        Encrypt conversation before PostgreSQL INSERT/UPDATE.

        Args:
            conversation: List of message dicts [
                {"timestamp": "...", "speaker": "patient", "message": "..."},
                ...
            ]

        Returns:
            Base64-encoded encrypted string (safe for PostgreSQL TEXT)

        Example:
            >>> messages = [{"speaker": "patient", "message": "I have chest pain"}]
            >>> encrypted = service.encrypt_conversation(messages)
            >>> len(encrypted)
            188  # Base64 encoded ciphertext
        """
        # Serialize to JSON
        json_str = json.dumps(conversation, ensure_ascii=False)

        # Encrypt (Fernet adds timestamp + HMAC automatically)
        encrypted = self.cipher.encrypt(json_str.encode('utf-8'))

        # Base64 encode for PostgreSQL TEXT storage
        return base64.b64encode(encrypted).decode('ascii')

    def decrypt_conversation(self, encrypted_data: str) -> List[Dict[str, Any]]:
        """
        Decrypt conversation after PostgreSQL SELECT.

        Args:
            encrypted_data: Base64-encoded ciphertext from database

        Returns:
            List of message dicts (original conversation structure)

        Raises:
            cryptography.fernet.InvalidToken: If data tampered or wrong key

        Example:
            >>> encrypted = "Z0FBQUFBQm1..." # from database
            >>> messages = service.decrypt_conversation(encrypted)
            >>> messages[0]['speaker']
            'patient'
        """
        # Decode from base64
        encrypted = base64.b64decode(encrypted_data.encode('ascii'))

        # Decrypt (Fernet verifies HMAC, checks timestamp automatically)
        decrypted = self.cipher.decrypt(encrypted)

        # Parse JSON
        return json.loads(decrypted.decode('utf-8'))


# Initialize global instance (used by FastAPI dependency injection)
# Only initialize if OSCE_ENCRYPTION_KEY is set (production/dev environment)
try:
    encryption_service = ConversationEncryptionService()
except ValueError:
    # Key not set - likely test environment
    # Tests will create their own instances with test keys
    encryption_service = None
