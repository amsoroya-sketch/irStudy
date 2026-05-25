#!/bin/bash
# Initialize Vault secrets for irStudy platform
# This script sets up ALL secrets required by both EMR and AI OSCE systems
# Updated to match test expectations in tests/test_vault.py

set -e

export VAULT_ADDR='http://localhost:8200'
export VAULT_TOKEN='dev-only-token-change-in-prod'

echo "========================================================================"
echo "🔑 INITIALIZING VAULT SECRETS FOR irStudy PLATFORM"
echo "========================================================================"

# Check if Vault is running
if ! curl -s "$VAULT_ADDR/v1/sys/health" > /dev/null 2>&1; then
    echo "❌ Vault not running at $VAULT_ADDR"
    echo "Run: bash scripts/start_vault_dev.sh"
    exit 1
fi

echo "✅ Vault is running at $VAULT_ADDR"

# Check if vault CLI is available
if ! command -v vault &> /dev/null; then
    echo "❌ vault CLI not available"
    echo "Install vault CLI from: https://www.vaultproject.io/downloads"
    exit 1
fi

# Enable KV v2 secrets engine
echo ""
echo "📦 Enabling KV v2 secrets engine..."
vault secrets enable -path=secret kv-v2 2>/dev/null || echo "ℹ️  Secret engine already enabled"
vault secrets enable -path=amc-simulation kv-v2 2>/dev/null || echo "ℹ️  AMC simulation engine already enabled"

# Generate Fernet encryption key (required for db_encryption_key)
echo ""
echo "🔐 Generating encryption key..."
FERNET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
echo "✅ Fernet key generated"

# =============================================================================
# PRIMARY PATHS (amc-simulation/*) - Used by config.py and tests
# =============================================================================

echo ""
echo "🗄️  Storing database configuration (amc-simulation/database)..."
vault kv put amc-simulation/database \
    postgres_user="${POSTGRES_USER:-postgres}" \
    postgres_password="${POSTGRES_PASSWORD:-dev-postgres-password-change-in-prod}" \
    postgres_host="${POSTGRES_HOST:-localhost}" \
    postgres_port="${POSTGRES_PORT:-5432}" \
    postgres_db="${POSTGRES_DB:-amc_simulation}" \
    redis_password="${REDIS_PASSWORD:-dev-redis-password-change-in-prod}" \
    redis_host="${REDIS_HOST:-localhost}" \
    redis_port="${REDIS_PORT:-6379}" \
    db_encryption_key="$FERNET_KEY" \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Database configuration stored at amc-simulation/database"
else
    echo "❌ Failed to store database configuration"
    exit 1
fi

echo ""
echo "🔐 Storing API keys (amc-simulation/api-keys)..."
vault kv put amc-simulation/api-keys \
    anthropic_api_key="${ANTHROPIC_API_KEY:-test-claude-api-key-dev}" \
    jwt_secret="${JWT_SECRET_KEY:-dev-jwt-secret-key-change-in-production-minimum-32-chars}" \
    jwt_algorithm="HS256" \
    jwt_expiration_hours=24 \
    > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ API keys stored at amc-simulation/api-keys"
else
    echo "❌ Failed to store API keys"
    exit 1
fi

# =============================================================================
# LEGACY PATHS (secret/irStudy/*) - For backward compatibility
# =============================================================================

echo ""
echo "🔄 Storing legacy paths for backward compatibility..."

# AI OSCE Claude API key (for content generation)
vault kv put secret/ai-osce/claude-api-key \
    value="${ANTHROPIC_API_KEY:-test-claude-api-key-dev}" \
    > /dev/null 2>&1 && echo "  ✓ AI OSCE Claude API key (secret/ai-osce/claude-api-key)"

# irStudy Claude API key (legacy path)
vault kv put secret/irStudy/claude \
    api_key="${ANTHROPIC_API_KEY:-test-claude-api-key-dev}" \
    > /dev/null 2>&1 && echo "  ✓ irStudy Claude API key (secret/irStudy/claude)"

# Database secrets (legacy)
vault kv put secret/irStudy/database \
    password="${POSTGRES_PASSWORD:-dev-postgres-password-change-in-prod}" \
    username="${POSTGRES_USER:-postgres}" \
    > /dev/null 2>&1 && echo "  ✓ Database secrets (secret/irStudy/database)"

# JWT secrets (legacy)
vault kv put secret/irStudy/jwt \
    secret_key="${JWT_SECRET_KEY:-dev-jwt-secret-key-change-in-production-minimum-32-chars}" \
    > /dev/null 2>&1 && echo "  ✓ JWT secrets (secret/irStudy/jwt)"

# Encryption keys (legacy)
vault kv put secret/irStudy/encryption \
    key="${ENCRYPTION_KEY:-dev-encryption-key-32-bytes-long!}" \
    > /dev/null 2>&1 && echo "  ✓ Encryption keys (secret/irStudy/encryption)"

# Redis secrets (legacy)
vault kv put secret/irStudy/redis \
    password="${REDIS_PASSWORD:-dev-redis-password-change-in-prod}" \
    > /dev/null 2>&1 && echo "  ✓ Redis secrets (secret/irStudy/redis)"

# =============================================================================
# CONFIGURE SECRET ROTATION POLICIES
# =============================================================================

echo ""
echo "🔄 Configuring secret rotation policies (max_versions=5)..."

# Database secrets rotation
vault kv metadata put -max-versions=5 amc-simulation/database 2>/dev/null && \
    echo "  ✓ Database rotation policy configured" || \
    echo "  ⚠️  Could not configure database rotation policy"

# API keys rotation
vault kv metadata put -max-versions=5 amc-simulation/api-keys 2>/dev/null && \
    echo "  ✓ API keys rotation policy configured" || \
    echo "  ⚠️  Could not configure API keys rotation policy"

# =============================================================================
# VERIFICATION
# =============================================================================

echo ""
echo "✅ Verifying secrets..."

# Verify primary paths (CRITICAL - tests depend on these)
if vault kv get amc-simulation/database > /dev/null 2>&1; then
    echo "  ✓ amc-simulation/database (PRIMARY - used by tests)"
else
    echo "  ❌ amc-simulation/database MISSING!"
    exit 1
fi

if vault kv get amc-simulation/api-keys > /dev/null 2>&1; then
    echo "  ✓ amc-simulation/api-keys (PRIMARY - used by tests)"
else
    echo "  ❌ amc-simulation/api-keys MISSING!"
    exit 1
fi

# Verify legacy paths
vault kv get secret/ai-osce/claude-api-key > /dev/null 2>&1 && echo "  ✓ AI OSCE Claude API key (legacy)"
vault kv get secret/irStudy/claude > /dev/null 2>&1 && echo "  ✓ irStudy Claude API key (legacy)"
vault kv get secret/irStudy/database > /dev/null 2>&1 && echo "  ✓ Database secrets (legacy)"
vault kv get secret/irStudy/jwt > /dev/null 2>&1 && echo "  ✓ JWT secrets (legacy)"
vault kv get secret/irStudy/encryption > /dev/null 2>&1 && echo "  ✓ Encryption keys (legacy)"
vault kv get secret/irStudy/redis > /dev/null 2>&1 && echo "  ✓ Redis secrets (legacy)"

# Show detailed verification of critical keys
echo ""
echo "📋 Detailed verification of amc-simulation/database keys..."
DATABASE_KEYS=$(vault kv get -format=json amc-simulation/database 2>/dev/null | jq -r '.data.data | keys[]' 2>/dev/null || echo "")

if [ -z "$DATABASE_KEYS" ]; then
    echo "  ❌ Could not read database keys"
    exit 1
fi

for key in postgres_user postgres_password postgres_host postgres_port postgres_db redis_password redis_host redis_port db_encryption_key; do
    if echo "$DATABASE_KEYS" | grep -q "^${key}$"; then
        echo "  ✓ $key"
    else
        echo "  ❌ $key MISSING!"
        exit 1
    fi
done

echo ""
echo "📋 Detailed verification of amc-simulation/api-keys keys..."
API_KEYS=$(vault kv get -format=json amc-simulation/api-keys 2>/dev/null | jq -r '.data.data | keys[]' 2>/dev/null || echo "")

if [ -z "$API_KEYS" ]; then
    echo "  ❌ Could not read API keys"
    exit 1
fi

for key in anthropic_api_key jwt_secret jwt_algorithm; do
    if echo "$API_KEYS" | grep -q "^${key}$"; then
        echo "  ✓ $key"
    else
        echo "  ❌ $key MISSING!"
        exit 1
    fi
done

echo ""
echo "========================================================================"
echo "✅ VAULT INITIALIZATION COMPLETE"
echo "========================================================================"
echo ""
echo "Environment variables set:"
echo "  VAULT_ADDR=$VAULT_ADDR"
echo "  VAULT_TOKEN=$VAULT_TOKEN"
echo ""
echo "Secrets stored at:"
echo "  PRIMARY PATHS (used by config.py and tests):"
echo "    - amc-simulation/database (9 keys)"
echo "    - amc-simulation/api-keys (4 keys)"
echo ""
echo "  LEGACY PATHS (backward compatibility):"
echo "    - secret/ai-osce/claude-api-key"
echo "    - secret/irStudy/claude"
echo "    - secret/irStudy/database"
echo "    - secret/irStudy/jwt"
echo "    - secret/irStudy/encryption"
echo "    - secret/irStudy/redis"
echo ""
echo "Next steps:"
echo "  1. Run vault tests: bash run_tests.sh tests/test_vault.py -v"
echo "  2. Run all tests: bash run_tests.sh"
echo ""
