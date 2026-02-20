"""
Conversation Encryption Service - GDPR Article 32 / SHARED_INFRASTRUCTURE_SPEC Compliance

Encrypts conversation_history JSONB before PostgreSQL storage.
Uses AES-256-GCM with key from Vault (secret/ai-osce/session-encryption-key).

CRITICAL: Fixes Issue #1 from Security Review (unencrypted conversations)
Upgraded from Fernet (AES-128-CBC) to AES-256-GCM per SHARED_INFRASTRUCTURE_SPEC.md
"""

import base64
import json
import os
import secrets
from typing import List, Dict, Any

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# AES-256-GCM constants
AES256_KEY_BYTES = 32   # 256-bit key
GCM_NONCE_BYTES = 12    # 96-bit nonce (GCM standard)


class ConversationEncryptionService:
    """
    Encrypt/decrypt OSCE conversations for PostgreSQL storage using AES-256-GCM.

    Usage:
        encryption_service = ConversationEncryptionService()
        encrypted = encryption_service.encrypt_conversation(messages)
        await db.execute(
            "UPDATE osce_attempts SET conversation_history = :encrypted",
            {"encrypted": encrypted}
        )

    Security:
        - Uses AES-256-GCM (authenticated encryption — confidentiality + integrity)
        - Random 96-bit nonce per encryption (prepended to ciphertext)
        - Key from Vault (secret/ai-osce/session-encryption-key)
        - Base64 encoding for PostgreSQL TEXT storage
    """

    def __init__(self, encryption_key: bytes = None):
        """
        Initialize encryption service with AES-256-GCM.

        Args:
            encryption_key: 32-byte (256-bit) key from Vault.
                            If None, reads from OSCE_ENCRYPTION_KEY env var.
        """
        if encryption_key is None:
            key_b64 = os.getenv('OSCE_ENCRYPTION_KEY')
            if not key_b64:
                raise ValueError(
                    "OSCE_ENCRYPTION_KEY not set. "
                    "Run: vault kv get -field=session-encryption-key secret/ai-osce"
                )
            encryption_key = base64.b64decode(key_b64)

        if len(encryption_key) != AES256_KEY_BYTES:
            raise ValueError(
                f"Encryption key must be {AES256_KEY_BYTES} bytes (AES-256). "
                f"Got {len(encryption_key)} bytes."
            )

        # AESGCM handles AES-256-GCM authenticated encryption
        self.aesgcm = AESGCM(encryption_key)

    def encrypt_conversation(self, conversation: List[Dict[str, Any]]) -> str:
        """
        Encrypt conversation before PostgreSQL INSERT/UPDATE using AES-256-GCM.

        Args:
            conversation: List of message dicts [
                {"timestamp": "...", "speaker": "patient", "message": "..."},
                ...
            ]

        Returns:
            Base64-encoded string: nonce (12 bytes) + ciphertext + GCM tag (16 bytes)
            Safe for PostgreSQL TEXT storage.

        Example:
            >>> messages = [{"speaker": "patient", "message": "I have chest pain"}]
            >>> encrypted = service.encrypt_conversation(messages)
            >>> encrypted.startswith("Z0")  # Base64 prefix will vary
            True
        """
        # Serialize to JSON bytes
        plaintext = json.dumps(conversation, ensure_ascii=False).encode('utf-8')

        # Generate random 96-bit nonce (unique per encryption)
        nonce = secrets.token_bytes(GCM_NONCE_BYTES)

        # AES-256-GCM encrypt (returns ciphertext + 16-byte authentication tag)
        ciphertext = self.aesgcm.encrypt(nonce, plaintext, associated_data=None)

        # Prepend nonce to ciphertext, then base64-encode for PostgreSQL
        return base64.b64encode(nonce + ciphertext).decode('ascii')

    def decrypt_conversation(self, encrypted_data: str) -> List[Dict[str, Any]]:
        """
        Decrypt conversation after PostgreSQL SELECT using AES-256-GCM.

        Args:
            encrypted_data: Base64-encoded string (nonce + ciphertext + tag)

        Returns:
            List of message dicts (original conversation structure)

        Raises:
            cryptography.exceptions.InvalidTag: If data tampered or wrong key
            ValueError: If data format is invalid

        Example:
            >>> encrypted = "Z0FBQUFBQm1..."  # from database
            >>> messages = service.decrypt_conversation(encrypted)
            >>> messages[0]['speaker']
            'patient'
        """
        raw = base64.b64decode(encrypted_data.encode('ascii'))

        if len(raw) < GCM_NONCE_BYTES + 16:
            raise ValueError("Encrypted data too short — possible corruption")

        # Split nonce and ciphertext+tag
        nonce = raw[:GCM_NONCE_BYTES]
        ciphertext = raw[GCM_NONCE_BYTES:]

        # AES-256-GCM decrypt (verifies authentication tag automatically)
        plaintext = self.aesgcm.decrypt(nonce, ciphertext, associated_data=None)

        return json.loads(plaintext.decode('utf-8'))


# Initialize global instance (used by FastAPI dependency injection)
# Only initialize if OSCE_ENCRYPTION_KEY is set (production/dev environment)
try:
    encryption_service = ConversationEncryptionService()
except (ValueError, Exception):
    # Key not set — likely test environment
    # Tests will create their own instances with test keys
    encryption_service = None
