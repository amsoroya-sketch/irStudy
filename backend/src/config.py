# -*- coding: utf-8 -*-
"""
AMC Clinical Exam Simulation - Configuration Management
v2.0 Enhanced Architecture - Vault-backed Settings

Security: All secrets fetched from HashiCorp Vault (not environment variables)
Per PROJECT_CONSTRAINTS.md constraint 3
"""

import os
from functools import lru_cache
from typing import Optional

try:
    import hvac
    from pydantic_settings import BaseSettings
except ImportError:
    print("ERROR: Install required packages: pip install hvac pydantic-settings")
    raise


class Settings(BaseSettings):
    """
    Application settings with Vault integration
    
    Only VAULT_ADDR and VAULT_TOKEN come from environment.
    All other secrets are fetched from Vault at runtime.
    """

    # Vault connection (only secrets in environment)
    vault_addr: str = "http://localhost:8200"
    vault_token: str = ""
    
    # Application settings
    environment: str = "development"
    debug: bool = True
    
    # Cached Vault client
    _vault_client: Optional[hvac.Client] = None

    class Config:
        env_file = ".env.dev"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    @property
    def vault(self) -> hvac.Client:
        """Lazy-loaded Vault client"""
        if self._vault_client is None:
            if not self.vault_token:
                # Try to get from environment
                self.vault_token = os.getenv("VAULT_ROOT_TOKEN", "")
            
            if not self.vault_token:
                raise ValueError(
                    "Vault token not configured. Set VAULT_ROOT_TOKEN environment variable."
                )
            
            self._vault_client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token
            )
            
            if not self._vault_client.is_authenticated():
                raise ConnectionError(f"Failed to authenticate with Vault at {self.vault_addr}")
        
        return self._vault_client

    def get_secret(self, path: str, key: str) -> str:
        """
        Fetch secret from Vault
        
        Args:
            path: Vault path (e.g., 'amc-simulation/database')
            key: Secret key (e.g., 'postgres_password')
            
        Returns:
            Secret value as string
        """
        try:
            secret = self.vault.secrets.kv.v2.read_secret_version(path=path)
            return secret['data']['data'][key]
        except Exception as e:
            raise ValueError(f"Failed to fetch secret {key} from {path}: {e}")

    # Database connection properties
    @property
    def database_url(self) -> str:
        """PostgreSQL connection string"""
        user = self.get_secret('amc-simulation/database', 'postgres_user')
        password = self.get_secret('amc-simulation/database', 'postgres_password')
        host = self.get_secret('amc-simulation/database', 'postgres_host')
        port = self.get_secret('amc-simulation/database', 'postgres_port')
        db = self.get_secret('amc-simulation/database', 'postgres_db')
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"

    @property
    def redis_url(self) -> str:
        """Redis connection string"""
        password = self.get_secret('amc-simulation/database', 'redis_password')
        host = self.get_secret('amc-simulation/database', 'redis_host')
        port = self.get_secret('amc-simulation/database', 'redis_port')
        return f"redis://:{password}@{host}:{port}/0"

    @property
    def db_encryption_key(self) -> str:
        """Fernet encryption key for database field-level encryption"""
        return self.get_secret('amc-simulation/database', 'db_encryption_key')

    # API keys
    @property
    def anthropic_api_key(self) -> str:
        """Anthropic Claude API key"""
        return self.get_secret('amc-simulation/api-keys', 'anthropic_api_key')

    @property
    def jwt_secret(self) -> str:
        """JWT signing secret"""
        return self.get_secret('amc-simulation/api-keys', 'jwt_secret')

    @property
    def jwt_algorithm(self) -> str:
        """JWT algorithm"""
        return self.get_secret('amc-simulation/api-keys', 'jwt_algorithm')


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    
    Uses lru_cache to ensure single instance (singleton pattern)
    """
    return Settings()
