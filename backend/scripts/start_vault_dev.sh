#!/bin/bash
# Start Vault dev server for local testing

# Check if Vault is already running
if lsof -Pi :8200 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "✅ Vault already running on port 8200"
    exit 0
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Install Docker first."
    exit 1
fi

# Check if old container exists and remove it
if docker ps -a | grep -q vault-dev; then
    echo "🧹 Removing old Vault container..."
    docker rm -f vault-dev >/dev/null 2>&1
fi

# Start Vault dev server
echo "🚀 Starting Vault dev server..."
docker run --rm -d \
    --name vault-dev \
    --cap-add=IPC_LOCK \
    -p 8200:8200 \
    -e 'VAULT_DEV_ROOT_TOKEN_ID=dev-only-token-change-in-prod' \
    -e 'VAULT_DEV_LISTEN_ADDRESS=0.0.0.0:8200' \
    hashicorp/vault:latest

# Wait for Vault to be ready
echo "⏳ Waiting for Vault to start..."
for i in {1..30}; do
    if curl -s http://localhost:8200/v1/sys/health > /dev/null 2>&1; then
        echo "✅ Vault started successfully"
        echo "📍 Vault Address: http://localhost:8200"
        echo "🔑 Root Token: dev-only-token-change-in-prod"
        exit 0
    fi
    sleep 1
done

echo "❌ Vault failed to start within 30 seconds"
docker logs vault-dev
exit 1
