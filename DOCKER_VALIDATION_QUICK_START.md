# Docker Stack Validation - Task 003

**Status**: Ready for manual execution
**Created**: 2026-02-02

## Quick Validation Commands

### 1. Validate Configuration
```bash
cd /home/dev/Development/irStudy
docker-compose config
```

### 2. Start All Services
```bash
docker-compose up -d
sleep 30
docker-compose ps
```

### 3. Test Connectivity
```bash
# PostgreSQL
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT version();"

# Redis
docker exec irstudy-redis redis-cli PING

# Qdrant Vector DB
curl -s http://localhost:6333/

# Neo4j Graph DB
curl -s http://localhost:7474/

# Backend Health
curl -s http://localhost:8000/health | jq
```

### 4. Verify Security
```bash
# Secrets mounted
docker exec irstudy-backend ls -la /run/secrets/

# Non-root user
docker exec irstudy-backend whoami

# No hardcoded credentials
docker-compose logs 2>&1 | grep -iE "password|secret|key" | grep -v "PASSWORD_FILE"
```

## Success Criteria
- ✅ All 11 services show Up (healthy)
- ✅ Backend /health returns all connections OK
- ✅ No hardcoded credentials in logs
- ✅ Docker secrets properly mounted
- ✅ Services running as non-root user

## Services Expected
1. irstudy-postgres
2. irstudy-redis
3. irstudy-qdrant
4. irstudy-neo4j
5. irstudy-backend
6. irstudy-celery-worker
7. irstudy-celery-beat
8. irstudy-flower
9. irstudy-prometheus
10. irstudy-grafana
11. irstudy-adminer
