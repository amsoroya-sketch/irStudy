# Vault Quick Reference Guide

**For irStudy Platform Development**  
**Date**: 2026-04-05

---

## Quick Start

### 1. Environment Variables (MUST SET)

```bash
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'
```

Add to `~/.bashrc` for persistence:
```bash
echo 'export VAULT_ADDR="http://localhost:8200"' >> ~/.bashrc
echo 'export VAULT_TOKEN="dev-only-token-change-in-prod"' >> ~/.bashrc
source ~/.bashrc
```

### 2. Check Vault Status

```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev vault status
```

Expected output:
```
Sealed          false    ✅ Ready for use
Initialized     true     ✅ Secrets loaded
```

---

## Reading Secrets

### Get All Secrets in a Path
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault kv get secret/database
```

### Get Specific Secret Field
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault kv get -field=jwt-secret secret/shared
```

### Get Secret as JSON
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault kv get -format=json secret/shared | jq -r '.data.data'
```

---

## Secret Paths Reference

### Database Secrets (secret/database/)
```bash
vault kv get secret/database
```
- `postgres-irstudy-password` - PostgreSQL password
- `postgres-connection-string` - Full connection URL
- `postgres-admin-password` - Admin password for migrations

### EMR Secrets (secret/emr/)
```bash
vault kv get secret/emr
```
- `claude-api-key` - Claude API key (shared with OSCE)
- `session-encryption-key` - AES-256-GCM key for EMR data
- `template-signing-key` - HMAC key for template integrity
- `fallback-validator-key` - Rule-based fallback key

### AI OSCE Secrets (secret/ai-osce/)
```bash
vault kv get secret/ai-osce
```
- `claude-api-key` - Claude API key (same as EMR)
- `kimi-api-key` - Kimi API fallback key
- `redis-password` - Redis authentication password
- `websocket-secret` - JWT signing for WebSocket
- `session-encryption-key` - AES-256-GCM for transcripts
- `scoring-salt` - Salt for scoring hash

### Shared Secrets (secret/shared/)
```bash
vault kv get secret/shared
```
- `jwt-secret` - JWT access token signing (256-bit)
- `jwt-refresh-secret` - JWT refresh token signing
- `https-tls-cert` - SSL certificate (placeholder)
- `https-tls-key` - SSL private key (placeholder)
- `api-rate-limit-secret` - HMAC for rate limit tokens

---

## Using Secrets in Python Code

### Read from Vault (Recommended)
```python
from src.core.vault import get_vault_secret

# Get entire secret path
claude_config = get_vault_secret("emr")
api_key = claude_config["claude-api-key"]

# Get specific field
jwt_secret = get_vault_secret("shared", "jwt-secret")
```

### Fallback to Environment Variables
If Vault is unavailable, secrets fall back to environment variables:
```python
import os

# These will be used if Vault is down
os.getenv("ANTHROPIC_API_KEY")      # Maps to secret/emr/claude-api-key
os.getenv("JWT_SECRET_KEY")         # Maps to secret/shared/jwt-secret
os.getenv("DATABASE_PASSWORD")      # Maps to secret/database/postgres-irstudy-password
```

---

## Common Commands

### List Policies
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault policy list
```

### Read Policy
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault policy read emr-backend
```

### Update Secret
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault kv put secret/emr \
    claude-api-key="sk-ant-api03-YOUR-NEW-KEY"
```

### List All Secret Paths
```bash
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" \
    amc-vault-dev vault kv list secret/
```

---

## Troubleshooting

### Error: "permission denied"
**Cause**: Token doesn't have policy attached  
**Solution**: Use root token for development (VAULT_TOKEN='dev-only-token-change-in-prod')

### Error: "connection refused"
**Cause**: VAULT_ADDR not set or Vault container not running  
**Solution**:
```bash
# Check container
docker ps | grep vault

# Set environment variables
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'
```

### Error: "Vault is sealed"
**Cause**: Vault server restarted  
**Solution**:
```bash
# Check status
docker exec -e VAULT_ADDR="$VAULT_ADDR" amc-vault-dev vault status

# Unseal (dev mode auto-unseals, just restart container)
docker restart amc-vault-dev
```

---

## Security Best Practices

### DO:
- ✅ Always use Vault for secrets in production
- ✅ Use separate policies for EMR and OSCE services
- ✅ Rotate JWT secrets monthly
- ✅ Use environment variables as fallback for development only

### DON'T:
- ❌ Never commit VAULT_TOKEN to git
- ❌ Never hardcode API keys in code
- ❌ Never use root token in production
- ❌ Never print secrets to logs

---

## Quick Test Commands

### Verify All Secrets Initialized
```bash
./scripts/init_vault_week1.sh
```

### Run Security Tests
```bash
cd backend
python3 -m pytest tests/test_security/ -v
```

### Check for Hardcoded Credentials
```bash
grep -r "sk-ant-api" backend/src/ --include="*.py" | grep -v "PLACEHOLDER"
# Expected output: (nothing)
```

---

## Files Reference

- **Vault Client**: `backend/src/core/vault.py`
- **Auth Module**: `backend/src/core/auth.py`
- **Encryption**: `backend/src/security/encryption.py`
- **Initialization Script**: `scripts/init_vault_week1.sh`
- **Security Tests**: `backend/tests/test_security/`

---

**Last Updated**: 2026-04-05  
**Vault Version**: 1.15.6  
**Mode**: Development (in-memory storage)

**For Production**: Migrate to Vault with persistent storage and TLS. See `docs/VAULT_INTEGRATION.md` Section 3 (Production Deployment).
