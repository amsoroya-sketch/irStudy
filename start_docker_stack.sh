#\!/bin/bash
# Docker Stack Startup - Task 003
set -e
cd /home/dev/Development/irStudy
echo "Starting 11-service Docker stack..."
docker compose up -d
sleep 30
docker compose ps
echo "Testing connectivity..."
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1;"
docker exec irstudy-redis redis-cli ping
curl -s http://localhost:6333/ | head -3
echo "Stack ready"
