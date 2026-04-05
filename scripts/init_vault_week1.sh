#!/bin/bash
# Week 1 Shared Infrastructure - Vault Initialization Script
# Initializes Vault with all secrets for EMR + AI OSCE systems
#
# Reference: SHARED_INFRASTRUCTURE_SPEC.md Section 1 (Vault)
# Reference: VAULT_INTEGRATION.md Section "Initialize Secrets"

set -e  # Exit on error

echo "========================================================================"
echo "WEEK 1 SHARED INFRASTRUCTURE - VAULT INITIALIZATION"
echo "========================================================================"
echo

# Environment variables
export VAULT_ADDR="${VAULT_ADDR:-http://localhost:8200}"
export VAULT_TOKEN="${VAULT_TOKEN:-dev-only-token-change-in-prod}"

# Check Vault is accessible
echo "1. Checking Vault connection..."
if ! docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev vault status > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to Vault at $VAULT_ADDR"
    echo "   Ensure Vault container is running: docker ps | grep vault"
    exit 1
fi
echo "✅ Vault is accessible"
echo

# Enable KV v2 secrets engine
echo "2. Enabling KV v2 secrets engine..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault secrets enable -version=2 -path=secret kv 2>/dev/null || echo "   (already enabled)"
echo "✅ KV v2 secrets engine enabled at path 'secret/'"
echo

# Initialize database secrets
echo "3. Initializing database secrets..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv put secret/database \
    postgres-irstudy-password="$(openssl rand -base64 32)" \
    postgres-connection-string="postgresql://irstudy:CHANGEME@localhost:5433/irstudy" \
    postgres-admin-password="$(openssl rand -base64 32)"
echo "✅ Database secrets initialized (secret/database/)"
echo

# Initialize EMR secrets
echo "4. Initializing EMR secrets..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv put secret/emr \
    claude-api-key="${ANTHROPIC_API_KEY:-PLACEHOLDER_SET_ME_LATER}" \
    session-encryption-key="$(openssl rand -base64 32)" \
    template-signing-key="$(openssl rand -base64 32)" \
    fallback-validator-key="$(openssl rand -base64 32)"
echo "✅ EMR secrets initialized (secret/emr/)"
echo

# Initialize AI OSCE secrets
echo "5. Initializing AI OSCE secrets..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv put secret/ai-osce \
    claude-api-key="${ANTHROPIC_API_KEY:-PLACEHOLDER_SET_ME_LATER}" \
    kimi-api-key="${KIMI_API_KEY:-PLACEHOLDER_SET_ME_LATER}" \
    redis-password="$(openssl rand -base64 32)" \
    websocket-secret="$(openssl rand -base64 32)" \
    session-encryption-key="$(openssl rand -base64 32)" \
    scoring-salt="$(openssl rand -base64 16)"
echo "✅ AI OSCE secrets initialized (secret/ai-osce/)"
echo

# Initialize shared secrets
echo "6. Initializing shared secrets..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv put secret/shared \
    jwt-secret="$(openssl rand -base64 32)" \
    jwt-refresh-secret="$(openssl rand -base64 32)" \
    https-tls-cert="PLACEHOLDER_TLS_CERT" \
    https-tls-key="PLACEHOLDER_TLS_KEY" \
    api-rate-limit-secret="$(openssl rand -base64 32)"
echo "✅ Shared secrets initialized (secret/shared/)"
echo

# Create EMR backend policy
echo "7. Creating EMR backend access policy..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev sh -c '
cat > /tmp/emr-backend.hcl << POLICY
# EMR Backend Service Policy
path "secret/data/emr/*" {
  capabilities = ["read"]
}

path "secret/data/database/*" {
  capabilities = ["read"]
}

path "secret/data/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/data/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
POLICY

vault policy write emr-backend /tmp/emr-backend.hcl
'
echo "✅ EMR backend policy created"
echo

# Create AI OSCE backend policy
echo "8. Creating AI OSCE backend access policy..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev sh -c '
cat > /tmp/osce-backend.hcl << POLICY
# AI OSCE Backend Service Policy
path "secret/data/ai-osce/*" {
  capabilities = ["read"]
}

path "secret/data/database/*" {
  capabilities = ["read"]
}

path "secret/data/shared/jwt-secret" {
  capabilities = ["read"]
}

path "secret/data/shared/api-rate-limit-secret" {
  capabilities = ["read"]
}
POLICY

vault policy write osce-backend /tmp/osce-backend.hcl
'
echo "✅ AI OSCE backend policy created"
echo

# Verify all secrets are readable
echo "9. Verifying secrets..."
docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/database > /dev/null && echo "✅ secret/database/ readable"

docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/emr > /dev/null && echo "✅ secret/emr/ readable"

docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/ai-osce > /dev/null && echo "✅ secret/ai-osce/ readable"

docker exec -e VAULT_ADDR="$VAULT_ADDR" -e VAULT_TOKEN="$VAULT_TOKEN" amc-vault-dev \
    vault kv get secret/shared > /dev/null && echo "✅ secret/shared/ readable"

echo
echo "========================================================================"
echo "✅ VAULT INITIALIZATION COMPLETE"
echo "========================================================================"
echo
echo "Next steps:"
echo "1. Export environment variables:"
echo "   export VAULT_ADDR='http://localhost:8200'"
echo "   export VAULT_TOKEN='dev-only-token-change-in-prod'"
echo "2. Run security tests: pytest backend/tests/test_security/ -v"
echo "3. Run credential scan: grep -r 'password.*=' backend/src/"
echo
