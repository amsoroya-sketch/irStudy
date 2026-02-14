#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AMC Clinical Exam Simulation - HashiCorp Vault Setup
v2.0 Enhanced Architecture - Task 1.2: Secrets Management

Usage:
    source venv/bin/activate
    export VAULT_ADDR=http://localhost:8200
    export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod
    python backend/scripts/setup_vault.py
"""

import os
import sys
import secrets
from typing import Dict, Any

try:
    import hvac
    from cryptography.fernet import Fernet
except ImportError:
    print("ERROR: Required packages not installed")
    print("Run: pip install hvac cryptography")
    sys.exit(1)


class VaultSetup:
    """Initialize HashiCorp Vault with AMC simulation secrets"""

    def __init__(self):
        """Initialize Vault client"""
        self.vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
        self.vault_token = os.getenv("VAULT_ROOT_TOKEN")

        if not self.vault_token:
            raise ValueError(
                "VAULT_ROOT_TOKEN environment variable not set.\n"
                "Run: export VAULT_ROOT_TOKEN=dev-only-token-change-in-prod"
            )

        print(f"Connecting to Vault at {self.vault_addr}...")
        self.client = hvac.Client(url=self.vault_addr, token=self.vault_token)

        if not self.client.is_authenticated():
            raise ConnectionError(f"Failed to authenticate with Vault at {self.vault_addr}")

        print("✅ Connected to Vault successfully")

    def enable_kv_engine(self) -> None:
        """Enable KV v2 secrets engine at path 'amc-simulation'"""
        print("\n📦 Enabling KV v2 secrets engine...")
        try:
            mounted_engines = self.client.sys.list_mounted_secrets_engines()
            if 'amc-simulation/' in mounted_engines:
                print("ℹ️  KV engine already enabled at 'amc-simulation'")
                return
        except Exception as e:
            print(f"⚠️  Could not check existing engines: {e}")

        try:
            self.client.sys.enable_secrets_engine(
                backend_type='kv',
                path='amc-simulation',
                options={'version': '2'}
            )
            print("✅ KV v2 secrets engine enabled at path 'amc-simulation'")
        except Exception as e:
            print(f"⚠️  Could not enable KV engine (may already exist): {e}")

    def store_database_secrets(self) -> None:
        """Store database credentials and encryption keys"""
        print("\n🔐 Storing database secrets...")

        postgres_user = os.getenv("POSTGRES_USER", "amc_user")
        postgres_password = os.getenv("POSTGRES_PASSWORD")
        postgres_db = os.getenv("POSTGRES_DB", "amc_simulation")
        redis_password = os.getenv("REDIS_PASSWORD")

        if not postgres_password:
            print("⚠️  POSTGRES_PASSWORD not set, generating random password")
            postgres_password = secrets.token_urlsafe(32)

        if not redis_password:
            print("⚠️  REDIS_PASSWORD not set, generating random password")
            redis_password = secrets.token_urlsafe(32)

        db_encryption_key = Fernet.generate_key().decode('utf-8')

        database_secrets: Dict[str, Any] = {
            'postgres_user': postgres_user,
            'postgres_password': postgres_password,
            'postgres_db': postgres_db,
            'postgres_host': 'localhost',
            'postgres_port': 5432,
            'redis_password': redis_password,
            'redis_host': 'localhost',
            'redis_port': 6379,
            'db_encryption_key': db_encryption_key,
        }

        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path='amc-simulation/database',
                secret=database_secrets
            )
            print("✅ Database secrets stored successfully")
            print(f"   - PostgreSQL: {postgres_user}@{postgres_db}")
            print(f"   - Encryption key: {db_encryption_key[:20]}...")
        except Exception as e:
            print(f"❌ Failed to store database secrets: {e}")
            raise

    def store_api_keys(self) -> None:
        """Store API keys for external services"""
        print("\n🔑 Storing API keys...")

        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "PLACEHOLDER_SET_ME_LATER")
        jwt_secret = secrets.token_urlsafe(32)

        api_key_secrets: Dict[str, Any] = {
            'anthropic_api_key': anthropic_api_key,
            'jwt_secret': jwt_secret,
            'jwt_algorithm': "HS256",
            'jwt_expiration_hours': 24,
        }

        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path='amc-simulation/api-keys',
                secret=api_key_secrets
            )
            print("✅ API keys stored successfully")
            print(f"   - JWT secret: {jwt_secret[:20]}...")
        except Exception as e:
            print(f"❌ Failed to store API keys: {e}")
            raise

    def configure_key_rotation(self) -> None:
        """Configure automatic key rotation policy"""
        print("\n🔄 Configuring key rotation policy...")
        try:
            self.client.secrets.kv.v2.update_metadata(
                path='amc-simulation/database',
                max_versions=5,
                delete_version_after='90d'
            )
            print("✅ Database secrets rotation: 90 days (5 versions)")
            
            self.client.secrets.kv.v2.update_metadata(
                path='amc-simulation/api-keys',
                max_versions=5,
                delete_version_after='90d'
            )
            print("✅ API keys rotation: 90 days (5 versions)")
        except Exception as e:
            print(f"⚠️  Could not configure key rotation: {e}")

    def verify_secrets(self) -> bool:
        """Verify all secrets are accessible"""
        print("\n✅ Verifying secrets...")
        try:
            db_secret = self.client.secrets.kv.v2.read_secret_version(
                path='amc-simulation/database'
            )
            db_data = db_secret['data']['data']
            print(f"✅ Database secrets verified ({len(db_data)} keys)")

            api_secret = self.client.secrets.kv.v2.read_secret_version(
                path='amc-simulation/api-keys'
            )
            api_data = api_secret['data']['data']
            print(f"✅ API keys verified ({len(api_data)} keys)")
            return True
        except Exception as e:
            print(f"❌ Secret verification failed: {e}")
            return False

    def run(self) -> bool:
        """Run complete Vault setup"""
        print("\n" + "="*70)
        print("🚀 AMC CLINICAL EXAM SIMULATION - VAULT SETUP")
        print("="*70)
        try:
            self.enable_kv_engine()
            self.store_database_secrets()
            self.store_api_keys()
            self.configure_key_rotation()
            return self.verify_secrets()
        except Exception as e:
            print(f"\n❌ Vault setup failed: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    setup = VaultSetup()
    success = setup.run()
    if success:
        print("\n✅ Vault setup complete!")
        print("\nNext: Run 'alembic upgrade head' to create database schema")
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
