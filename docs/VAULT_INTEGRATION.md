# Vault Integration Guide

**Project**: irStudy Medical Education Platform
**Purpose**: Secure secret management using HashiCorp Vault
**Status**: MANDATORY for production deployment
**Last Updated**: 2026-02-16

---

## Overview

This guide documents how to integrate HashiCorp Vault for secure secret management in the irStudy platform. Vault provides a centralized, audited, and encrypted storage for sensitive data including API keys, database credentials, and encryption keys.

**Why Vault?**
- **Zero Hardcoded Secrets**: Eliminates credentials in code/config files
- **Audit Trail**: Tracks all secret access attempts
- **Dynamic Secrets**: Auto-generates short-lived database credentials
- **Encryption**: AES-256-GCM for data at rest
- **Access Control**: Fine-grained policies per service/user

---

## Setup

### 1. Install Vault CLI

**macOS**:
```bash
brew install vault
```

**Linux (Ubuntu/Debian)**:
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install vault
```

**Verify installation**:
```bash
vault --version
# Expected output: Vault v1.15.0 or higher
```

### 2. Start Vault Development Server

**DEVELOPMENT ONLY** (not for production):
```bash
vault server -dev
```

This will output:
```
Unseal Key: <key>
Root Token: <token>
Development mode should NOT be used in production!
```

**Set environment variables**:
```bash
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='<root-token-from-above>'
```

Add to `~/.bashrc` or `~/.zshrc` for persistence:
```bash
echo 'export VAULT_ADDR="http://127.0.0.1:8200"' >> ~/.bashrc
echo 'export VAULT_TOKEN="<your-token>"' >> ~/.bashrc
source ~/.bashrc
```

### 3. Production Deployment

For production, use Vault in **non-dev mode** with TLS:

```bash
# Create Vault configuration
cat > vault-config.hcl << EOF
storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address = "0.0.0.0:8200"
  tls_cert_file = "/opt/vault/tls/vault.crt"
  tls_key_file = "/opt/vault/tls/vault.key"
}

api_addr = "https://vault.irstudy.com:8200"
cluster_addr = "https://vault.irstudy.com:8201"
ui = true
EOF

# Initialize and unseal Vault
vault operator init
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>
```

---

## Secret Hierarchy

### Complete Key Structure (EMR + AI OSCE)

```
secret/
├── database/
│   ├── postgres-irstudy-password         # Shared by both systems
│   ├── postgres-connection-string        # postgresql://user:pass@host:5433/irstudy
│   └── postgres-admin-password           # For migrations, admin tasks
│
├── emr/
│   ├── claude-api-key                    # EMR SOAP validator (shared with AI OSCE)
│   ├── session-encryption-key            # AES-256-GCM key for EMR data at rest
│   ├── template-signing-key              # HMAC key for template integrity
│   └── fallback-validator-key            # Rule-based fallback when Claude down
│
├── ai-osce/
│   ├── claude-api-key                    # AI Patient/Examiner (same as emr/claude-api-key)
│   ├── kimi-api-key                      # Fallback for AI Patient (70% quality)
│   ├── redis-password                    # OSCE session storage authentication
│   ├── websocket-secret                  # JWT signing for WebSocket connections
│   ├── session-encryption-key            # AES-256-GCM for transcript encryption
│   └── scoring-salt                      # Salt for scoring hash verification
│
└── shared/
    ├── jwt-secret                        # Authentication token signing (256-bit)
    ├── jwt-refresh-secret                # Refresh token signing (256-bit, rotated monthly)
    ├── https-tls-cert                    # SSL certificate (Let's Encrypt or CA)
    ├── https-tls-key                     # SSL private key
    └── api-rate-limit-secret             # HMAC secret for rate limit tokens
```

### Initialize Secrets

```bash
#!/bin/bash
# scripts/vault-init-secrets.sh

# Enable KV secrets engine (version 2)
vault secrets enable -version=2 -path=secret kv

# Database secrets
vault kv put secret/database \
  postgres-irstudy-password="$(openssl rand -base64 32)" \
  postgres-connection-string="postgresql://irstudy:PASSWORD@localhost:5433/irstudy" \
  postgres-admin-password="$(openssl rand -base64 32)"

# EMR secrets
vault kv put secret/emr \
  claude-api-key="sk-ant-api03-YOUR-CLAUDE-KEY" \
  session-encryption-key="$(openssl rand -base64 32)" \
  template-signing-key="$(openssl rand -base64 32)" \
  fallback-validator-key="$(openssl rand -base64 32)"

# AI OSCE secrets
vault kv put secret/ai-osce \
  claude-api-key="sk-ant-api03-YOUR-CLAUDE-KEY" \
  kimi-api-key="YOUR-KIMI-API-KEY" \
  redis-password="$(openssl rand -base64 32)" \
  websocket-secret="$(openssl rand -base64 32)" \
  session-encryption-key="$(openssl rand -base64 32)" \
  scoring-salt="$(openssl rand -base64 16)"

# Shared secrets
vault kv put secret/shared \
  jwt-secret="$(openssl rand -base64 32)" \
  jwt-refresh-secret="$(openssl rand -base64 32)" \
  api-rate-limit-secret="$(openssl rand -base64 32)"

echo "✅ All secrets initialized"
```

### Read Secrets

```bash
# Read entire secret path
vault kv get secret/ai-osce

# Read specific field
vault kv get -field=redis-password secret/ai-osce

# JSON output
vault kv get -format=json secret/ai-osce | jq -r '.data.data.redis_password'
```

---

## Access Control Policies

### EMR Backend Service Policy

**File**: `policies/emr-backend.hcl`
```hcl
# Read access to EMR secrets
path "secret/data/emr/*" {
  capabilities = ["read"]
}

# Read access to database secrets
path "secret/data/database/*" {
  capabilities = ["read"]
}

# Read access to shared JWT secret
path "secret/data/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/data/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
```

Apply policy:
```bash
vault policy write emr-backend policies/emr-backend.hcl
```

### AI OSCE Backend Service Policy

**File**: `policies/osce-backend.hcl`
```hcl
# Read access to AI OSCE secrets
path "secret/data/ai-osce/*" {
  capabilities = ["read"]
}

# Read access to database secrets
path "secret/data/database/*" {
  capabilities = ["read"]
}

# Read access to shared JWT secret
path "secret/data/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/data/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
```

Apply policy:
```bash
vault policy write osce-backend policies/osce-backend.hcl
```

### Create Service Tokens

```bash
# Create token for EMR backend (renewable, TTL 72h)
vault token create -policy=emr-backend -ttl=72h -renewable=true

# Create token for OSCE backend (renewable, TTL 72h)
vault token create -policy=osce-backend -ttl=72h -renewable=true
```

---

## Backend Integration

### Python (FastAPI)

**File**: `backend/src/core/vault.py`
```python
import hvac
import os
from typing import Dict

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR', 'http://localhost:8200'),
            token=os.getenv('VAULT_TOKEN')
        )

        if not self.client.is_authenticated():
            raise Exception("Vault authentication failed")

    def get_secret(self, path: str) -> Dict[str, str]:
        """
        Read secret from Vault KV v2
        path: e.g., 'database', 'emr', 'ai-osce', 'shared/jwt-secret'
        """
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data']
        except Exception as e:
            raise Exception(f"Failed to read secret {path}: {str(e)}")

    def get_database_config(self) -> Dict[str, str]:
        """Get PostgreSQL connection details"""
        return self.get_secret('database')

    def get_emr_config(self) -> Dict[str, str]:
        """Get EMR system secrets"""
        return self.get_secret('emr')

    def get_osce_config(self) -> Dict[str, str]:
        """Get AI OSCE system secrets"""
        return self.get_secret('ai-osce')

    def get_jwt_secret(self) -> str:
        """Get JWT signing secret"""
        secrets = self.get_secret('shared')
        return secrets['jwt-secret']

# Initialize global Vault client
vault = VaultClient()

# Usage examples
db_config = vault.get_database_config()
DATABASE_URL = db_config['postgres-connection-string']

emr_config = vault.get_emr_config()
CLAUDE_API_KEY = emr_config['claude-api-key']

osce_config = vault.get_osce_config()
REDIS_PASSWORD = osce_config['redis-password']
WEBSOCKET_SECRET = osce_config['websocket-secret']
```

---

## Key Rotation

### Rotation Schedule

| Secret | Rotation Frequency | Impact |
|--------|-------------------|--------|
| Database passwords | 90 days | Requires coordinated downtime |
| JWT secrets | 30 days | Automatic, dual-key overlap |
| Claude API key | As needed | Immediate (if compromised) |
| Encryption keys | 180 days | Gradual migration (dual-key decrypt) |
| TLS certificates | 90 days | Automated via Let's Encrypt |

### JWT Secret Rotation Procedure

```bash
#!/bin/bash
# scripts/rotate-jwt-secret.sh

# Step 1: Generate new JWT secret
NEW_SECRET=$(openssl rand -base64 32)

# Step 2: Read current secret
CURRENT_SECRET=$(vault kv get -field=jwt-secret secret/shared)

# Step 3: Write new secret to 'jwt-secret-next'
vault kv patch secret/shared jwt-secret-next="$NEW_SECRET"

# Step 4: Update backend to use BOTH secrets for verification (dual-key period)
# Backend code should try current secret first, then fall back to next

# Step 5: Wait 24 hours (allow all tokens to expire or be refreshed)

# Step 6: Promote new secret to primary
vault kv patch secret/shared jwt-secret="$NEW_SECRET"
vault kv patch secret/shared jwt-secret-prev="$CURRENT_SECRET"

# Step 7: Wait another 24 hours

# Step 8: Remove old secret
vault kv patch secret/shared jwt-secret-prev=""

echo "✅ JWT secret rotation complete"
```

---

## Monitoring & Auditing

### Enable Audit Logging

```bash
vault audit enable file file_path=/var/log/vault/audit.log
```

### View Audit Log

```bash
# Recent secret access attempts
tail -f /var/log/vault/audit.log | jq '.request.path'

# Failed authentication attempts
grep '"error"' /var/log/vault/audit.log | jq '.'

# Specific secret access
grep 'secret/data/ai-osce' /var/log/vault/audit.log | jq '.'
```

### Metrics (Prometheus)

Vault exposes Prometheus metrics at `http://localhost:8200/v1/sys/metrics?format=prometheus`

Key metrics to monitor:
- `vault_core_unsealed` - Is Vault unsealed? (1 = yes, 0 = no)
- `vault_runtime_alloc_bytes` - Memory usage
- `vault_core_handle_request_count` - Request rate
- `vault_core_handle_request_duration_seconds` - Request latency

---

## Troubleshooting

### Issue: "permission denied" when reading secrets

**Cause**: Service token doesn't have policy attached

**Solution**:
```bash
# Check token policies
vault token lookup

# Attach policy to token
vault write auth/token/roles/emr-backend \
  allowed_policies=emr-backend \
  orphan=true \
  renewable=true \
  token_ttl=72h
```

### Issue: Vault is sealed

**Cause**: Vault server restarted

**Solution**:
```bash
# Check seal status
vault status

# Unseal (requires 3 of 5 unseal keys)
vault operator unseal <key-1>
vault operator unseal <key-2>
vault operator unseal <key-3>
```

### Issue: "connection refused" from backend

**Cause**: `VAULT_ADDR` or `VAULT_TOKEN` not set

**Solution**:
```bash
# Set environment variables
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='your-token-here'

# Verify connection
vault status
```

---

## Production Checklist

- [ ] Vault running in **non-dev mode** with TLS
- [ ] Audit logging enabled (`/var/log/vault/audit.log`)
- [ ] All secrets initialized (database, emr, ai-osce, shared)
- [ ] Service policies created (emr-backend, osce-backend)
- [ ] Service tokens generated and provided to backend services
- [ ] Unseal keys stored securely (separate from Vault server)
- [ ] Root token securely backed up and removed from server
- [ ] Monitoring configured (Prometheus metrics, alerts)
- [ ] Key rotation schedule documented and automated
- [ ] Disaster recovery procedure tested (restore from backup)

---

**Document Status**: ✅ Complete
**Last Updated**: 2026-02-16
**Version**: 2.0 (Added AI OSCE secrets)
**Owner**: Security Team + DevOps
