#!/bin/bash
# Vault Secret Initialization Script
# Initializes complete key hierarchy for irStudy platform (EMR + AI OSCE)
# Based on: SHARED_INFRASTRUCTURE_SPEC.md and docs/VAULT_INTEGRATION.md

set -e

# Vault connection
export VAULT_ADDR='http://127.0.0.1:8200'
export VAULT_TOKEN='dev-only-token'

echo "🔐 Initializing Vault secrets for irStudy platform..."

# Enable KV secrets engine v2
echo "📦 Enabling KV secrets engine v2..."
vault secrets enable -version=2 -path=secret kv 2>/dev/null || echo "KV engine already enabled"

# Database secrets
echo "💾 Initializing database secrets..."
vault kv put secret/database \
  postgres-irstudy-password="$(openssl rand -base64 32)" \
  postgres-connection-string="postgresql://irstudy:REPLACE_PASSWORD@localhost:5433/irstudy" \
  postgres-admin-password="$(openssl rand -base64 32)"

# EMR secrets
echo "🏥 Initializing EMR system secrets..."
vault kv put secret/emr \
  claude-api-key="REPLACE-WITH-REAL-CLAUDE-KEY" \
  session-encryption-key="$(openssl rand -base64 32)" \
  template-signing-key="$(openssl rand -base64 32)" \
  fallback-validator-key="$(openssl rand -base64 32)"

# AI OSCE secrets
echo "🤖 Initializing AI OSCE system secrets..."
vault kv put secret/ai-osce \
  claude-api-key="REPLACE-WITH-REAL-CLAUDE-KEY" \
  kimi-api-key="REPLACE-WITH-REAL-KIMI-KEY" \
  redis-password="$(openssl rand -base64 32)" \
  websocket-secret="$(openssl rand -base64 32)" \
  session-encryption-key="$(openssl rand -base64 32)" \
  scoring-salt="$(openssl rand -base64 16)"

# Shared secrets
echo "🔑 Initializing shared secrets..."
vault kv put secret/shared \
  jwt-secret="$(openssl rand -base64 32)" \
  jwt-refresh-secret="$(openssl rand -base64 32)" \
  api-rate-limit-secret="$(openssl rand -base64 32)"

echo ""
echo "✅ All secrets initialized successfully!"
echo ""
echo "📋 Secret paths created:"
vault kv list secret/
echo ""
echo "⚠️  IMPORTANT: Replace placeholder API keys with real values:"
echo "  - secret/emr/claude-api-key"
echo "  - secret/ai-osce/claude-api-key"
echo "  - secret/ai-osce/kimi-api-key"
echo ""
