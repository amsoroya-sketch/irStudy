#!/bin/bash
# Stop Vault dev server

if docker ps | grep -q vault-dev; then
    echo "🛑 Stopping Vault dev server..."
    docker stop vault-dev
    echo "✅ Vault stopped"
else
    echo "ℹ️  Vault not running"
fi
