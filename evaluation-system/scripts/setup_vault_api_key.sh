#!/bin/bash
#
# Setup Vault API Key for Evaluation System
# Stores Claude API key securely in Vault for automated evaluations
#
# Usage:
#   ./setup_vault_api_key.sh YOUR_ANTHROPIC_API_KEY
#
# Prerequisites:
#   - Vault running (docker compose -f docker-compose.dev.yml up -d vault)
#   - VAULT_ADDR and VAULT_TOKEN set in environment

set -e

echo "======================================================================"
echo "Evaluation System - Vault API Key Setup"
echo "======================================================================"
echo ""

# Check if API key provided
if [ $# -eq 0 ]; then
    echo "❌ Error: No API key provided"
    echo ""
    echo "Usage:"
    echo "  $0 YOUR_ANTHROPIC_API_KEY"
    echo ""
    echo "To get an API key:"
    echo "  1. Visit https://console.anthropic.com/settings/keys"
    echo "  2. Create a new API key"
    echo "  3. Run this script with the key as argument"
    echo ""
    exit 1
fi

API_KEY="$1"

# Validate API key format (should start with sk-ant-)
if [[ ! "$API_KEY" =~ ^sk-ant- ]]; then
    echo "⚠️  Warning: API key doesn't match expected format (sk-ant-...)"
    echo "   Proceeding anyway..."
    echo ""
fi

# Set Vault environment
export VAULT_ADDR=${VAULT_ADDR:-http://127.0.0.1:8200}
export VAULT_TOKEN=${VAULT_TOKEN:-dev-only-token-change-in-prod}

echo "🔧 Configuration:"
echo "   Vault Address: $VAULT_ADDR"
echo "   Vault Token: ${VAULT_TOKEN:0:10}***"
echo ""

# Check Vault is running
echo "🔍 Checking Vault status..."
if ! vault status > /dev/null 2>&1; then
    echo "❌ Error: Vault is not running or not accessible"
    echo ""
    echo "Start Vault with:"
    echo "  docker compose -f docker-compose.dev.yml up -d vault"
    echo ""
    exit 1
fi

echo "✅ Vault is running (unsealed)"
echo ""

# Store API key
echo "💾 Storing Claude API key in Vault..."
vault kv put secret/ai-osce/claude-api-key value="$API_KEY" > /dev/null

echo "✅ API key stored successfully!"
echo ""

# Verify storage
echo "🔍 Verifying storage..."
STORED_KEY=$(vault kv get -field=value secret/ai-osce/claude-api-key 2>/dev/null)

if [ -n "$STORED_KEY" ]; then
    # Show only last 4 characters for security
    MASKED_KEY="${STORED_KEY: -4}"
    echo "✅ API key retrieved successfully (***$MASKED_KEY)"
    echo ""
else
    echo "❌ Error: Could not retrieve API key from Vault"
    exit 1
fi

echo "======================================================================"
echo "✅ Setup Complete!"
echo "======================================================================"
echo ""
echo "Next steps:"
echo ""
echo "1. Test integration with single item:"
echo "   venv/bin/python3 evaluation-system/scripts/test_single_item.py"
echo ""
echo "2. Test with 10 items:"
echo "   venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py --max-items 10"
echo ""
echo "3. Run full production evaluation (2,963 items, 6-8 hours):"
echo "   venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \\"
echo "     --output-dir evaluation-system/reports/production_iteration_1"
echo ""
echo "======================================================================"
echo ""

exit 0
