#!/usr/bin/env python3
"""
Encrypted Secret Manager for Medical Resources Download System

Provides secure storage and retrieval of API keys and credentials using
symmetric encryption with Fernet (AES-128 in CBC mode).

Security Features:
- Encrypted storage (Fernet symmetric encryption)
- File permissions (0600 - owner read/write only)
- Environment-based fallback
- Audit logging of secret access

Usage:
    from scripts.lib.secret_manager import SecretManager

    secrets = SecretManager()

    # First time: Set secrets
    secrets.set_secret('NCBI_API_KEY', 'your_api_key_here')

    # Retrieve secrets
    api_key = secrets.get_secret('NCBI_API_KEY')
"""

import json
import os
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)


class SecretManager:
    """Encrypted local secret storage using Fernet symmetric encryption"""

    def __init__(self, secrets_dir: Optional[Path] = None):
        """
        Initialize SecretManager

        Args:
            secrets_dir: Directory to store encrypted secrets
                        Defaults to ~/.medical_resources/
        """
        if secrets_dir is None:
            secrets_dir = Path.home() / '.medical_resources'

        self.secrets_dir = Path(secrets_dir)
        self.key_file = self.secrets_dir / 'encryption.key'
        self.secrets_file = self.secrets_dir / 'secrets.enc'

        # Create directory if doesn't exist
        self.secrets_dir.mkdir(parents=True, exist_ok=True)

        # Secure permissions (owner read/write only)
        try:
            self.secrets_dir.chmod(0o700)
        except Exception as e:
            logger.warning(f"Could not set directory permissions: {e}")

        # Initialize encryption
        self._initialize_encryption()

    def _initialize_encryption(self):
        """Initialize or load encryption key"""
        if not self.key_file.exists():
            # Generate new encryption key
            key = Fernet.generate_key()
            self.key_file.write_bytes(key)

            # Secure file permissions (owner read/write only)
            try:
                self.key_file.chmod(0o600)
            except Exception as e:
                logger.warning(f"Could not set key file permissions: {e}")

            logger.info(f"Generated new encryption key at {self.key_file}")

        # Load encryption key
        key = self.key_file.read_bytes()
        self.cipher = Fernet(key)

        # Initialize empty secrets file if doesn't exist
        if not self.secrets_file.exists():
            self._save_secrets({})

    def _load_secrets(self) -> dict:
        """Load and decrypt secrets from storage"""
        if not self.secrets_file.exists():
            return {}

        try:
            encrypted_data = self.secrets_file.read_bytes()
            decrypted_data = self.cipher.decrypt(encrypted_data)
            secrets = json.loads(decrypted_data.decode('utf-8'))
            return secrets
        except Exception as e:
            logger.error(f"Failed to decrypt secrets: {e}")
            raise ValueError(f"Secret decryption failed. Encryption key may be corrupted.")

    def _save_secrets(self, secrets: dict):
        """Encrypt and save secrets to storage"""
        try:
            json_data = json.dumps(secrets, indent=2)
            encrypted_data = self.cipher.encrypt(json_data.encode('utf-8'))
            self.secrets_file.write_bytes(encrypted_data)

            # Secure file permissions
            try:
                self.secrets_file.chmod(0o600)
            except Exception as e:
                logger.warning(f"Could not set secrets file permissions: {e}")

        except Exception as e:
            logger.error(f"Failed to encrypt secrets: {e}")
            raise

    def set_secret(self, name: str, value: str):
        """
        Store encrypted secret

        Args:
            name: Secret identifier (e.g., 'NCBI_API_KEY')
            value: Secret value to encrypt
        """
        secrets = self._load_secrets()
        secrets[name] = value
        self._save_secrets(secrets)
        logger.info(f"Secret '{name}' stored successfully")

    def get_secret(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """
        Retrieve decrypted secret with environment variable fallback

        Args:
            name: Secret identifier
            default: Default value if secret not found

        Returns:
            Decrypted secret value or default
        """
        # Try encrypted storage first
        secrets = self._load_secrets()
        if name in secrets:
            logger.debug(f"Retrieved secret '{name}' from encrypted storage")
            return secrets[name]

        # Fallback to environment variable (for backward compatibility)
        env_value = os.getenv(name)
        if env_value:
            logger.warning(
                f"Secret '{name}' retrieved from environment variable. "
                f"Consider migrating to encrypted storage with set_secret()"
            )
            return env_value

        # Return default if provided
        if default is not None:
            logger.debug(f"Secret '{name}' not found, using default")
            return default

        # Not found anywhere
        logger.error(f"Secret '{name}' not found in encrypted storage or environment")
        return None

    def delete_secret(self, name: str):
        """
        Delete a secret from encrypted storage

        Args:
            name: Secret identifier
        """
        secrets = self._load_secrets()
        if name in secrets:
            del secrets[name]
            self._save_secrets(secrets)
            logger.info(f"Secret '{name}' deleted successfully")
        else:
            logger.warning(f"Secret '{name}' not found, nothing to delete")

    def list_secrets(self) -> list:
        """
        List all stored secret names (not values)

        Returns:
            List of secret identifiers
        """
        secrets = self._load_secrets()
        return list(secrets.keys())

    def rotate_encryption_key(self):
        """
        Rotate encryption key and re-encrypt all secrets

        WARNING: This operation is sensitive. Ensure you have a backup.
        """
        # Load current secrets
        current_secrets = self._load_secrets()

        # Generate new key
        new_key = Fernet.generate_key()

        # Backup old key
        backup_key_file = self.key_file.with_suffix('.key.backup')
        self.key_file.rename(backup_key_file)

        # Save new key
        self.key_file.write_bytes(new_key)
        self.key_file.chmod(0o600)

        # Re-initialize with new key
        self.cipher = Fernet(new_key)

        # Re-encrypt secrets
        self._save_secrets(current_secrets)

        logger.info(f"Encryption key rotated successfully. Backup key: {backup_key_file}")


def migrate_from_env_file(env_file: Path, secret_manager: SecretManager):
    """
    Migrate secrets from .env file to encrypted storage

    Args:
        env_file: Path to .env file
        secret_manager: SecretManager instance
    """
    if not env_file.exists():
        logger.warning(f".env file not found: {env_file}")
        return

    migrated_count = 0

    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()

            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue

            # Parse export statements (export VAR=value) or simple assignments (VAR=value)
            if line.startswith('export '):
                line = line[7:]  # Remove 'export '

            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")  # Remove quotes

                # Migrate to encrypted storage
                secret_manager.set_secret(key, value)
                migrated_count += 1
                logger.info(f"Migrated '{key}' to encrypted storage")

    logger.info(f"Migration complete: {migrated_count} secrets migrated from {env_file}")
    logger.warning(
        f"\nNEXT STEPS:\n"
        f"1. Verify secrets work: python3 -c \"from scripts.lib.secret_manager import SecretManager; s = SecretManager(); print(s.list_secrets())\"\n"
        f"2. Remove {env_file} or add it to .gitignore\n"
        f"3. Update scripts to use SecretManager instead of os.getenv()"
    )


if __name__ == '__main__':
    # Example usage and migration script
    import argparse

    parser = argparse.ArgumentParser(description='Manage encrypted secrets')
    parser.add_argument('command', choices=['set', 'get', 'delete', 'list', 'migrate'],
                       help='Command to execute')
    parser.add_argument('--name', help='Secret name')
    parser.add_argument('--value', help='Secret value (for set command)')
    parser.add_argument('--env-file', help='Path to .env file (for migrate command)')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    secrets = SecretManager()

    if args.command == 'set':
        if not args.name or not args.value:
            print("Error: --name and --value required for 'set' command")
            exit(1)
        secrets.set_secret(args.name, args.value)
        print(f"✓ Secret '{args.name}' stored successfully")

    elif args.command == 'get':
        if not args.name:
            print("Error: --name required for 'get' command")
            exit(1)
        value = secrets.get_secret(args.name)
        if value:
            print(f"{args.name} = {value}")
        else:
            print(f"Secret '{args.name}' not found")
            exit(1)

    elif args.command == 'delete':
        if not args.name:
            print("Error: --name required for 'delete' command")
            exit(1)
        secrets.delete_secret(args.name)
        print(f"✓ Secret '{args.name}' deleted")

    elif args.command == 'list':
        secret_names = secrets.list_secrets()
        if secret_names:
            print("Stored secrets:")
            for name in secret_names:
                print(f"  - {name}")
        else:
            print("No secrets stored yet")

    elif args.command == 'migrate':
        if not args.env_file:
            # Default to project .env file
            project_root = Path(__file__).parent.parent.parent
            env_file = project_root / '.env'
        else:
            env_file = Path(args.env_file)

        print(f"Migrating secrets from {env_file}...")
        migrate_from_env_file(env_file, secrets)
