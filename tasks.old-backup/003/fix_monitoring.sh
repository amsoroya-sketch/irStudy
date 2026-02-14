#!/bin/bash
# Fix monitoring directory and restart Docker stack
# This script fixes the prometheus.yml directory issue and restarts services

set -e

echo "🔧 Fixing monitoring configuration..."

# Remove the incorrect directory
echo "📁 Removing prometheus.yml directory..."
sudo rm -rf /home/dev/Development/irStudy/monitoring/prometheus.yml

# Create proper prometheus.yml file with sudo
echo "📝 Creating prometheus.yml configuration file..."
sudo tee /home/dev/Development/irStudy/monitoring/prometheus.yml > /dev/null << 'EOF'
# Prometheus Configuration for irStudy Medical Platform
# Security-hardened monitoring configuration

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'irstudy-medical'
    environment: 'production'

# Scrape configurations
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Backend FastAPI metrics
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/metrics'
    scrape_interval: 10s

  # Additional services can be added here as they become available
  # - job_name: 'postgres'
  #   static_configs:
  #     - targets: ['postgres-exporter:9187']

  # - job_name: 'redis'
  #   static_configs:
  #     - targets: ['redis-exporter:9121']
EOF

echo "✅ Prometheus configuration created"

# Create grafana directories if they don't exist
echo "📁 Creating Grafana directories..."
sudo mkdir -p /home/dev/Development/irStudy/monitoring/grafana/dashboards
sudo mkdir -p /home/dev/Development/irStudy/monitoring/grafana/datasources

# Create basic Grafana datasource configuration
echo "📝 Creating Grafana datasource configuration..."
sudo tee /home/dev/Development/irStudy/monitoring/grafana/datasources/prometheus.yml > /dev/null << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

echo "✅ Grafana configuration created"

# Fix ownership back to user
echo "🔐 Fixing file ownership..."
sudo chown -R dev:dev /home/dev/Development/irStudy/monitoring/

# Verify file is created correctly
if [ -f /home/dev/Development/irStudy/monitoring/prometheus.yml ]; then
    echo "✅ Verification: prometheus.yml is now a file"
else
    echo "❌ Error: prometheus.yml was not created properly"
    exit 1
fi

echo ""
echo "🐳 Starting Docker stack..."
cd /home/dev/Development/irStudy
docker compose up -d

echo ""
echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "🏥 Health Check Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check each service
services=("irstudy-postgres" "irstudy-redis" "irstudy-qdrant" "irstudy-neo4j" "irstudy-prometheus")
for service in "${services[@]}"; do
    if docker ps --format '{{.Names}}' | grep -q "^${service}$"; then
        status=$(docker inspect --format='{{.State.Status}}' ${service})
        if [ "$status" = "running" ]; then
            echo "✅ ${service}: Running"
        else
            echo "⚠️  ${service}: ${status}"
        fi
    else
        echo "❌ ${service}: Not found"
    fi
done

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Service URLs:"
echo "  • PostgreSQL:  localhost:5432"
echo "  • Redis:       localhost:6379"
echo "  • Qdrant:      http://localhost:6333"
echo "  • Neo4j:       http://localhost:7474"
echo "  • Prometheus:  http://localhost:9090"
echo "  • Grafana:     http://localhost:3001"
echo "  • Backend:     http://localhost:8000 (when ready)"
echo "  • Adminer:     http://localhost:8080"
echo ""
echo "✅ Setup complete! Run 'docker compose logs -f' to monitor startup."
