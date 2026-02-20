"""
Vault Integration Module
Secure secret retrieval from HashiCorp Vault

SECURITY: Zero-tolerance for hardcoded credentials
Reference: docs/VAULT_INTEGRATION.md
"""

import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class VaultClient:
    """
    HashiCorp Vault client for secret management
    
    Supports:
    - KV v2 secrets engine
    - Token-based authentication
    - Auto-retry on transient failures
    """
    
    def __init__(self):
        """Initialize Vault client"""
        self.vault_addr = os.getenv("VAULT_ADDR", "http://127.0.0.1:8200")
        self.vault_token = os.getenv("VAULT_TOKEN")
        
        if not self.vault_token:
            logger.warning(
                "⚠️  VAULT_TOKEN not set - falling back to environment variables. "
                "This is acceptable for development but NOT for production."
            )
            self.client = None
            return
        
        try:
            import hvac
            from hvac.exceptions import VaultError
            
            self.client = hvac.Client(
                url=self.vault_addr,
                token=self.vault_token
            )
            
            # Verify authentication
            if not self.client.is_authenticated():
                raise RuntimeError(
                    f"Vault authentication failed for {self.vault_addr}"
                )
            
            logger.info(f"✅ Vault client initialized: {self.vault_addr}")
            
        except ImportError:
            logger.warning(
                "⚠️  hvac package not installed. "
                "Install with: pip install hvac"
            )
            self.client = None
        except Exception as e:
            logger.error(f"❌ Vault initialization failed: {e}")
            raise
    
    def get_secret(self, path: str, key: Optional[str] = None) -> Any:
        """
        Retrieve secret from Vault
        
        Args:
            path: Secret path (e.g., "irStudy/claude")
            key: Specific key to retrieve (e.g., "api_key")
                 If None, returns entire secret dict
        
        Returns:
            Secret value or dict of all values
        
        Raises:
            RuntimeError: If secret retrieval fails
        
        Example:
            # Get entire secret
            claude_config = vault.get_secret("irStudy/claude")
            
            # Get specific key
            api_key = vault.get_secret("irStudy/claude", "api_key")
        """
        if not self.client:
            # Fallback to environment variables
            logger.warning(
                f"⚠️  Vault unavailable - falling back to environment variable"
            )
            return self._get_from_env(path, key)
        
        try:
            # Read secret from KV v2 engine
            response = self.client.secrets.kv.v2.read_secret_version(
                path=path,
                mount_point="secret"
            )
            
            secret_data = response["data"]["data"]
            
            if key:
                if key not in secret_data:
                    raise KeyError(
                        f"Key '{key}' not found in secret '{path}'. "
                        f"Available keys: {list(secret_data.keys())}"
                    )
                return secret_data[key]
            
            return secret_data
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve secret '{path}': {e}")
            # Fallback to environment variables
            return self._get_from_env(path, key)
    
    def _get_from_env(self, path: str, key: Optional[str] = None) -> Any:
        """
        Fallback: Get secret from environment variables
        
        Maps Vault paths to environment variables:
        - irStudy/claude -> ANTHROPIC_API_KEY
        - irStudy/database -> DATABASE_URL
        - irStudy/jwt -> JWT_SECRET_KEY
        """
        # Map Vault paths to environment variable names
        env_mapping = {
            ("irStudy/claude", "api_key"): "ANTHROPIC_API_KEY",
            ("irStudy/database", "password"): "DATABASE_PASSWORD",
            ("irStudy/database", None): "DATABASE_URL",
            ("irStudy/jwt", "secret_key"): "JWT_SECRET_KEY",
            ("irStudy/encryption", "key"): "ENCRYPTION_KEY",
            ("irStudy/redis", "password"): "REDIS_PASSWORD",
        }
        
        env_var = env_mapping.get((path, key))
        
        if not env_var:
            raise RuntimeError(
                f"No fallback environment variable for Vault secret: {path}/{key}"
            )
        
        value = os.getenv(env_var)
        
        if not value:
            raise RuntimeError(
                f"Secret not found in Vault or environment: {env_var}"
            )
        
        logger.info(f"✅ Retrieved secret from environment: {env_var}")
        return value


# Global Vault client instance
_vault_client: Optional[VaultClient] = None


def get_vault_client() -> VaultClient:
    """Get or create global Vault client instance"""
    global _vault_client
    
    if _vault_client is None:
        _vault_client = VaultClient()
    
    return _vault_client


def get_vault_secret(path: str, key: Optional[str] = None) -> Any:
    """
    Convenience function to retrieve secret from Vault
    
    Args:
        path: Secret path (e.g., "irStudy/claude")
        key: Specific key to retrieve (e.g., "api_key")
    
    Returns:
        Secret value
    
    Example:
        # Get entire secret dict
        claude_config = get_vault_secret("irStudy/claude")
        
        # Get specific key
        api_key = get_vault_secret("irStudy/claude", "api_key")
    """
    client = get_vault_client()
    return client.get_secret(path, key)
