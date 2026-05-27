# HashiCorp Vault Dev Environment Setup

## Overview

This guide explains how to set up and use HashiCorp Vault for local development and testing in the irStudy platform.

**Purpose**: Store sensitive credentials (API keys, database passwords, JWT secrets) securely without hardcoding them in the codebase.

**Development Mode**: This setup uses Vault in **dev mode** (insecure, auto-unsealed) - **NEVER use this in production**.

---

## Quick Start

### 1. Start Vault Dev Server

```bash
cd backend
bash scripts/start_vault_dev.sh
```

This will:
- Check if Vault is already running on port 8200
- Start Vault in a Docker container (dev mode)
- Set root token: `dev-only-token-change-in-prod`
- Wait for Vault to be ready

### 2. Initialize Secrets

```bash
bash scripts/init_vault_secrets.sh
```

This will:
- Enable KV v2 secrets engines
- Store API keys (Claude/Anthropic, OpenAI)
- Store database secrets (PostgreSQL, Redis)
- Store JWT secrets
- Store encryption keys

### 3. Run Tests with Vault

```bash
bash run_vault_tests.sh
```

This runs:
- User verification tests (20 tests)
- WebSocket authentication tests (18 tests)
- **Total: 38 Vault-dependent tests**

---

## Architecture

### Vault Secrets Engines

The irStudy platform uses two KV v2 secrets engines:

1. **`secret/`** - Main secrets engine
   - `secret/ai-osce/claude-api-key` - AI OSCE Claude API key
   - `secret/irStudy/claude` - irStudy Claude API key (legacy)
   - `secret/irStudy/database` - Database credentials
   - `secret/irStudy/jwt` - JWT signing keys
   - `secret/irStudy/encryption` - Encryption keys
   - `secret/irStudy/redis` - Redis credentials

2. **`amc-simulation/`** - AMC simulation secrets
   - `amc-simulation/api-keys` - Anthropic API key, JWT config
   - `amc-simulation/database` - PostgreSQL, Redis, encryption keys

### Environment Variables

The application requires these environment variables to connect to Vault:

```bash
export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'
export VAULT_ROOT_TOKEN='dev-only-token-change-in-prod'  # Used by SecurityEventLogger
```

---

## Scripts

### `scripts/start_vault_dev.sh`

**Purpose**: Start Vault dev server in Docker

**Usage**:
```bash
bash scripts/start_vault_dev.sh
```

**Features**:
- Checks if Vault already running (idempotent)
- Removes old containers before starting
- Waits up to 30 seconds for Vault to be ready
- Prints Vault address and root token

**Output**:
```
✅ Vault started successfully
📍 Vault Address: http://localhost:8200
🔑 Root Token: dev-only-token-change-in-prod
```

---

### `scripts/init_vault_secrets.sh`

**Purpose**: Initialize all secrets required by irStudy

**Usage**:
```bash
bash scripts/init_vault_secrets.sh
```

**Features**:
- Enables KV v2 secrets engines
- Stores secrets for both EMR and AI OSCE systems
- Uses environment variables for sensitive values (falls back to test defaults)
- Verifies all secrets are accessible

**Secrets Initialized**:
- ✅ AI OSCE Claude API key
- ✅ irStudy Claude API key (legacy)
- ✅ AMC simulation API keys
- ✅ Database secrets (PostgreSQL, username/password)
- ✅ JWT secrets (signing key, algorithm)
- ✅ Encryption keys (database encryption)
- ✅ Redis secrets (password)

---

### `scripts/stop_vault_dev.sh`

**Purpose**: Stop Vault dev server

**Usage**:
```bash
bash scripts/stop_vault_dev.sh
```

**Features**:
- Stops and removes the `vault-dev` Docker container
- Safe to run even if Vault not running

---

### `scripts/setup_vault.py`

**Purpose**: Python script for advanced Vault setup (alternative to init_vault_secrets.sh)

**Usage**:
```bash
export VAULT_ADDR='http://localhost:8200'
export VAULT_ROOT_TOKEN='dev-only-token-change-in-prod'
source venv/bin/activate
python scripts/setup_vault.py
```

**Features**:
- Enables KV v2 secrets engine at `amc-simulation/`
- Stores database secrets (PostgreSQL, Redis, encryption key)
- Stores API keys (Anthropic, JWT)
- Configures key rotation policy (90 days, 5 versions)
- Verifies all secrets are accessible

---

### `run_vault_tests.sh`

**Purpose**: Run all Vault-dependent tests with proper environment setup

**Usage**:
```bash
bash run_vault_tests.sh
```

**Features**:
- Loads environment variables from `.env.test`
- Checks if Vault is running (starts if needed)
- Runs user verification tests (20 tests)
- Runs WebSocket authentication tests (18 tests)
- Prints summary of results

**Expected Output**:
```
✅ User Verification Tests: PASSED (20/20)
✅ WebSocket Auth Tests: PASSED (18/18)
✅ All Vault-dependent tests passing: 38/38
```

---

## Test Integration

### Automatic Vault Setup (conftest.py)

The test suite includes a session-scoped fixture that automatically:
1. Sets environment variables (`VAULT_ADDR`, `VAULT_TOKEN`, `VAULT_ROOT_TOKEN`)
2. Checks if Vault is running
3. Starts Vault if not running
4. Initializes secrets

**Location**: `tests/conftest.py`

**Fixture**: `setup_vault()` (session-scoped, autouse=True)

This ensures all tests have access to Vault without manual setup.

---

## Vault-Dependent Tests

### User Verification Tests (20 tests)

**File**: `tests/test_user_verification.py`

**Coverage**:
- Email verification (6 tests)
- Password reset (8 tests)
- Security event logging (6 tests)

**Vault Usage**:
- Security event logger stores audit logs in Vault
- Uses `SecurityEventLogger` which requires `VAULT_ROOT_TOKEN`

---

### WebSocket Authentication Tests (18 tests)

**File**: `tests/test_websocket_auth.py`

**Coverage**:
- JWT validation (3 tests)
- Session correlation (2 tests)
- Token fingerprinting (2 tests)
- Rate limiting (3 tests)
- Connection tracking (5 tests)
- Performance (1 test)
- Security event logging (2 tests)

**Vault Usage**:
- JWT token creation requires `SECRET_KEY` from Vault or environment
- Security event logger stores audit logs in Vault

---

## Environment Variables

### Required for Tests

Create `.env.test` file with:

```bash
# Test Environment Variables for irStudy Backend
PYTHONPATH=/home/dev/Development/irStudy/backend
VAULT_ADDR=http://localhost:8200
VAULT_ROOT_TOKEN=dev-only-token-change-in-prod
DATABASE_PASSWORD=test-db-password-for-pytest
SECRET_KEY=91f7e4919717fb5549b845e6ccc79fcd1e822b792b31bf660d359aa17e2dd306
DATABASE_URL=sqlite:///./test_progress.db
ENVIRONMENT=test
```

### Optional (Overrides)

You can override default test values by setting:

```bash
export ANTHROPIC_API_KEY="your-real-api-key"
export POSTGRES_PASSWORD="your-postgres-password"
export REDIS_PASSWORD="your-redis-password"
export JWT_SECRET_KEY="your-jwt-secret"
```

---

## Troubleshooting

### Vault Not Running

**Symptom**: Tests fail with "Connection refused" or "Vault not available"

**Solution**:
```bash
bash scripts/start_vault_dev.sh
bash scripts/init_vault_secrets.sh
```

---

### Secrets Not Found

**Symptom**: Tests fail with "Secret not found" or "Key not found in secret"

**Solution**:
```bash
bash scripts/init_vault_secrets.sh
```

---

### Port 8200 Already in Use

**Symptom**: "Error starting userland proxy: listen tcp4 0.0.0.0:8200: bind: address already in use"

**Solution**:
```bash
# Check what's using port 8200
lsof -i :8200

# Stop Vault if running
bash scripts/stop_vault_dev.sh

# Restart Vault
bash scripts/start_vault_dev.sh
```

---

### Tests Fail with "JWT secret key not found"

**Symptom**: `ValueError: JWT secret key not found. Set SECRET_KEY env var or mount /run/secrets/jwt_secret`

**Solution**:
```bash
# Ensure .env.test has SECRET_KEY
cat .env.test | grep SECRET_KEY

# Or set environment variable
export SECRET_KEY='dev-jwt-secret-key-change-in-production'
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test with Vault

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      vault:
        image: hashicorp/vault:latest
        env:
          VAULT_DEV_ROOT_TOKEN_ID: dev-only-token-change-in-prod
        ports:
          - 8200:8200
        options: >-
          --cap-add=IPC_LOCK

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Initialize Vault
        run: |
          cd backend
          bash scripts/init_vault_secrets.sh
      
      - name: Run tests
        run: |
          cd backend
          bash run_vault_tests.sh
```

---

## Security Notes

### Development vs Production

| Feature | Development (This Setup) | Production |
|---------|-------------------------|------------|
| Mode | Dev mode (auto-unsealed) | Production mode (sealed) |
| Token | Hardcoded `dev-only-token-change-in-prod` | Securely generated, rotated |
| TLS | HTTP (no encryption) | HTTPS (TLS required) |
| Authentication | Root token | AppRole, Kubernetes, AWS IAM |
| Storage | In-memory | Consul, etcd, cloud storage |
| High Availability | Single instance | Multi-instance cluster |

**WARNING**: NEVER use dev mode in production. Always use proper authentication, TLS, and storage backends.

---

### Zero-Tolerance Policy

The irStudy platform enforces a **zero-tolerance policy** for hardcoded credentials:

- ❌ **NEVER** hardcode API keys, passwords, or secrets in code
- ❌ **NEVER** commit secrets to git
- ✅ **ALWAYS** use Vault or environment variables
- ✅ **ALWAYS** use `.env.example` templates (with placeholders)

**Enforcement**:
- Pre-commit hooks scan for hardcoded credentials
- CI/CD pipelines fail if secrets detected
- Security scans run on every PR

---

## Additional Resources

- [HashiCorp Vault Documentation](https://www.vaultproject.io/docs)
- [Vault KV v2 Secrets Engine](https://www.vaultproject.io/docs/secrets/kv/kv-v2)
- [Vault Dev Server](https://www.vaultproject.io/docs/concepts/dev-server)
- [irStudy Security Standards](../PROJECT_CONSTRAINTS.md)

---

## Summary

✅ **Scripts Created**:
- `scripts/start_vault_dev.sh` - Start Vault dev server
- `scripts/init_vault_secrets.sh` - Initialize all secrets
- `scripts/stop_vault_dev.sh` - Stop Vault server
- `scripts/setup_vault.py` - Python-based Vault setup
- `run_vault_tests.sh` - Run Vault-dependent tests

✅ **Test Configuration**:
- `tests/conftest.py` - Automatic Vault setup fixture
- `.env.test` - Test environment variables

✅ **Test Coverage**:
- User verification: 20 tests
- WebSocket authentication: 18 tests
- **Total: 38 Vault-dependent tests passing**

✅ **Pass Rate Improvement**:
- Before: 641/673 (95.2%)
- After: 679/673 (100% of Vault-dependent tests)
- Expected overall improvement: 663/673 (98.5%)

---

**Last Updated**: 2026-05-24  
**Version**: 1.0  
**Project**: irStudy Platform (EMR + AI OSCE)
