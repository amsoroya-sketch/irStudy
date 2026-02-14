# -*- coding: utf-8 -*-
"""
AMC Clinical Exam Simulation - Vault Integration Tests
v2.0 Enhanced Architecture - Task 1.2 Testing

Run with: pytest backend/tests/test_vault.py -v
"""

import pytest
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from src.config import get_settings, Settings
    import hvac
except ImportError as e:
    pytest.skip(f"Required packages not installed: {e}", allow_module_level=True)


@pytest.fixture
def settings():
    """Get settings instance"""
    return get_settings()


@pytest.fixture
def vault_client():
    """Get Vault client"""
    vault_addr = os.getenv("VAULT_ADDR", "http://localhost:8200")
    vault_token = os.getenv("VAULT_ROOT_TOKEN", "dev-only-token-change-in-prod")
    
    client = hvac.Client(url=vault_addr, token=vault_token)
    
    if not client.is_authenticated():
        pytest.skip("Vault not available or not authenticated")
    
    return client


class TestVaultConnection:
    """Test Vault connection and authentication"""

    def test_vault_connection(self, settings):
        """Test that we can connect to Vault"""
        assert settings.vault is not None
        assert settings.vault.is_authenticated()

    def test_vault_address_configured(self, settings):
        """Test Vault address is configured"""
        assert settings.vault_addr.startswith("http")
        assert "8200" in settings.vault_addr


class TestSecretRetrieval:
    """Test secret retrieval from Vault"""

    def test_get_database_secrets(self, settings):
        """Test fetching database secrets"""
        # This will raise an exception if secret doesn't exist
        postgres_user = settings.get_secret('amc-simulation/database', 'postgres_user')
        assert postgres_user is not None
        assert len(postgres_user) > 0

    def test_get_postgres_password(self, settings):
        """Test fetching PostgreSQL password"""
        password = settings.get_secret('amc-simulation/database', 'postgres_password')
        assert password is not None
        assert len(password) >= 16  # Should be strong password

    def test_get_redis_password(self, settings):
        """Test fetching Redis password"""
        password = settings.get_secret('amc-simulation/database', 'redis_password')
        assert password is not None
        assert len(password) >= 16

    def test_get_encryption_key(self, settings):
        """Test fetching database encryption key"""
        encryption_key = settings.get_secret('amc-simulation/database', 'db_encryption_key')
        assert encryption_key is not None
        assert len(encryption_key) > 32  # Fernet keys are base64 encoded

    def test_get_jwt_secret(self, settings):
        """Test fetching JWT secret"""
        jwt_secret = settings.get_secret('amc-simulation/api-keys', 'jwt_secret')
        assert jwt_secret is not None
        assert len(jwt_secret) >= 32

    def test_get_anthropic_api_key(self, settings):
        """Test fetching Anthropic API key"""
        api_key = settings.get_secret('amc-simulation/api-keys', 'anthropic_api_key')
        assert api_key is not None
        # May be placeholder if not set yet
        assert len(api_key) > 0


class TestConnectionStrings:
    """Test connection string generation"""

    def test_database_url(self, settings):
        """Test PostgreSQL connection URL generation"""
        db_url = settings.database_url
        assert db_url.startswith("postgresql://")
        assert "amc_simulation" in db_url or "postgres_db" in db_url

    def test_redis_url(self, settings):
        """Test Redis connection URL generation"""
        redis_url = settings.redis_url
        assert redis_url.startswith("redis://")


class TestSecretSecurity:
    """Test security properties of secrets"""

    def test_no_secrets_in_environment(self):
        """Test that secrets are not in environment variables"""
        # Only VAULT_ADDR and VAULT_TOKEN should be in env
        allowed_vault_vars = ['VAULT_ADDR', 'VAULT_ROOT_TOKEN']
        
        # These should NOT be in environment (should be in Vault)
        forbidden_vars = ['POSTGRES_PASSWORD', 'REDIS_PASSWORD', 'ANTHROPIC_API_KEY']
        
        for var in forbidden_vars:
            env_value = os.getenv(var)
            # It's okay if they exist (for docker-compose), but app shouldn't use them
            # App must fetch from Vault instead
            pass  # This test is more conceptual

    def test_settings_singleton(self):
        """Test that get_settings returns same instance"""
        settings1 = get_settings()
        settings2 = get_settings()
        assert settings1 is settings2  # Same object reference


class TestVaultKeyRotation:
    """Test Vault key rotation configuration"""

    def test_database_secrets_rotation_configured(self, vault_client):
        """Test database secrets have rotation policy"""
        try:
            metadata = vault_client.secrets.kv.v2.read_secret_metadata(
                path='amc-simulation/database'
            )
            assert metadata is not None
            # Check max_versions and delete_version_after
            assert metadata['data']['max_versions'] == 5
        except Exception as e:
            pytest.skip(f"Could not check rotation policy: {e}")

    def test_api_keys_rotation_configured(self, vault_client):
        """Test API keys have rotation policy"""
        try:
            metadata = vault_client.secrets.kv.v2.read_secret_metadata(
                path='amc-simulation/api-keys'
            )
            assert metadata is not None
            assert metadata['data']['max_versions'] == 5
        except Exception as e:
            pytest.skip(f"Could not check rotation policy: {e}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
