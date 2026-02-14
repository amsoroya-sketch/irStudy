# irStudy Medical Education Platform - Setup Index
**Complete Infrastructure & Development Guide**

> 📋 **Purpose:** This document serves as the master index for understanding how the irStudy platform was built, configured, and deployed. Use this as your starting point for development, debugging, or recreating the environment.

**Last Updated:** 2026-02-03
**Platform Version:** 1.0.0
**Status:** ✅ Fully Operational

---

## 📑 Table of Contents

1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [Service Details](#service-details)
4. [Setup History & Troubleshooting](#setup-history--troubleshooting)
5. [Development Workflow](#development-workflow)
6. [Security & Secrets](#security--secrets)
7. [API Documentation](#api-documentation)
8. [Maintenance & Operations](#maintenance--operations)
9. [Key Files Reference](#key-files-reference)

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose installed
- Linux/macOS system (tested on Linux 6.14.0-37-generic)
- Minimum 16GB RAM, 4 CPU cores recommended
- Ports available: 5433, 6380, 6333-6334, 7474, 7687, 8001, 8080, 9090, 3001

### Start All Services
```bash
cd /home/dev/Development/irStudy
docker compose up -d
```

### Verify Services Running
```bash
docker compose ps
# Should show 11 services (8 healthy, 3 Celery services in optional restart)
```

### Access Key Endpoints
- **Backend API:** http://localhost:8001/
- **API Docs:** http://localhost:8001/api/docs
- **Database Admin:** http://localhost:8080
- **Qdrant Dashboard:** http://localhost:6333/dashboard
- **Neo4j Browser:** http://localhost:7474
- **Grafana:** http://localhost:3001
- **Prometheus:** http://localhost:9090

### Stop All Services
```bash
docker compose down
```

---

## 🏗️ Architecture Overview

### Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                     FRONTEND (Future)                   │
│                React + TanStack Query                   │
│                    Port: 3000 (TBD)                     │
└─────────────────────┬───────────────────────────────────┘
                      │
                      │ HTTP/REST API
                      ▼
┌─────────────────────────────────────────────────────────┐
│                  BACKEND API LAYER                      │
│              FastAPI + Python 3.11                      │
│               Port: 8001 (localhost)                    │
│                                                         │
│  Endpoints:                                             │
│  - /api/v1/auth     - Authentication                    │
│  - /api/v1/users    - User management                   │
│  - /api/v1/mcqs     - MCQ CRUD + attempts               │
│  - /api/v1/osces    - OSCE scenarios                    │
│  - /api/v1/progress - Analytics                         │
└──────────┬──────────┬──────────┬───────────┬────────────┘
           │          │          │           │
           ▼          ▼          ▼           ▼
┌──────────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────┐
│  PostgreSQL  │ │  Redis  │ │  Qdrant  │ │    Neo4j     │
│   (Primary)  │ │ (Cache) │ │  (RAG)   │ │   (Graph)    │
│  Port: 5433  │ │  6380   │ │6333-6334 │ │ 7474, 7687   │
└──────────────┘ └─────────┘ └──────────┘ └──────────────┘

           Background Tasks              Monitoring
    ┌─────────────────────────┐  ┌────────────────────────┐
    │ Celery Worker + Beat    │  │ Prometheus + Grafana   │
    │ Flower (Monitoring)     │  │ Ports: 9090, 3001      │
    └─────────────────────────┘  └────────────────────────┘
```

### Service Roles

| Service | Purpose | Critical? | Port(s) |
|---------|---------|-----------|---------|
| **Backend** | REST API, business logic | ✅ Yes | 8001 |
| **PostgreSQL** | Primary data store (users, MCQs, OSCEs, progress) | ✅ Yes | 5433 |
| **Redis** | Session cache, Celery broker | ✅ Yes | 6380 |
| **Qdrant** | Vector DB for RAG (medical knowledge search) | ✅ Yes | 6333-6334 |
| **Neo4j** | Medical knowledge graph | 🟡 Optional | 7474, 7687 |
| **Prometheus** | Metrics collection | 🟡 Optional | 9090 |
| **Grafana** | Monitoring dashboards | 🟡 Optional | 3001 |
| **Adminer** | Database admin UI | 🟡 Optional | 8080 |
| **Celery Worker** | Background task execution | 🟡 Optional | - |
| **Celery Beat** | Task scheduler | 🟡 Optional | - |
| **Flower** | Celery monitoring UI | 🟡 Optional | 5556 |

---

## 🔧 Service Details

### 1. Backend API (FastAPI)

**Container:** `irstudy-backend`
**Image:** Custom build from `./backend/Dockerfile`
**Port:** 8001 (mapped from internal 8000)
**Working Directory:** `/app`

**Key Features:**
- JWT authentication with secure password hashing
- Australian medical context (AMC, AHPRA, eTG references)
- Pydantic validation for all inputs
- Prometheus metrics at `/metrics`
- Health check at `/health`
- Auto-generated API docs at `/api/docs`

**Environment Variables:**
- `DATABASE_URL` - Constructed from secrets
- `REDIS_URL` - Constructed from secrets
- `SECRET_KEY` - JWT signing key from `/run/secrets/jwt_secret`
- `PYTHONPATH=/app/src` - For proper imports

**Startup Sequence:**
1. Load credentials from Docker secrets
2. Run Alembic migrations (`alembic upgrade head`)
3. Start Uvicorn server on 0.0.0.0:8000

**Import Structure:**
All imports use absolute paths from `src.*`:
- `from src.api.v1 import ...`
- `from src.db.models import ...`
- `from src.auth.security import ...`
- `from src.schemas.user import ...`

### 2. PostgreSQL (Primary Database)

**Container:** `irstudy-postgres`
**Image:** `postgres:16-alpine`
**Port:** 5433 (external) → 5432 (internal)
**Database:** `irstudy_medical`

**Security Features:**
- Read-only root filesystem (except /tmp, /run)
- Capability-restricted (only essential caps)
- Password loaded from Docker secret
- Health check: `pg_isready`

**Connection String:**
```
postgresql://postgres:<password>@localhost:5433/irstudy_medical
```

**Tables (via Alembic migration 001):**
- `users` - User accounts with HIPAA-compliant security
- `mcqs` - Multiple choice questions
- `osces` - OSCE scenarios
- `mcq_attempts` - Student attempt history
- `user_progress` - Analytics and mastery tracking

### 3. Redis (Cache & Message Broker)

**Container:** `irstudy-redis`
**Image:** `redis:7-alpine`
**Port:** 6380 (external) → 6379 (internal)

**Configuration:**
- Password authentication enabled
- Max memory: 1GB with LRU eviction
- Persistence: RDB + AOF enabled
- Health check: `redis-cli ping`

**Use Cases:**
- Session storage
- Celery message broker (when enabled)
- API rate limiting cache
- Temporary data cache

### 4. Qdrant (Vector Database for RAG)

**Container:** `irstudy-qdrant`
**Image:** Custom `irstudy-qdrant:custom` (built from `./docker/qdrant/Dockerfile`)
**Ports:** 6333 (HTTP API), 6334 (gRPC)

**Custom Build Reason:**
Base Qdrant image lacks `curl` for health checks. Custom Dockerfile installs it.

**Features:**
- Vector similarity search for medical knowledge
- API key protected (`/run/secrets/qdrant_api_key`)
- Web dashboard at http://localhost:6333/dashboard
- Collections: `medical_knowledge`

**Data Location:**
- Docker volume: `qdrant_data`
- Local mirror: `./docker/qdrant_storage/`

### 5. Neo4j (Knowledge Graph)

**Container:** `irstudy-neo4j`
**Image:** `neo4j:5.16.0-community`
**Ports:** 7474 (HTTP), 7687 (Bolt)

**Authentication:**
- Format: `neo4j/<password>` (stored in `/run/secrets/neo4j_auth`)
- Loaded via command override (Neo4j doesn't support `_FILE` suffix)

**Plugins:**
- APOC (graph algorithms)
- Graph Data Science

**Use Cases:**
- Medical concept relationships
- Drug interaction graphs
- Disease progression pathways

### 6. Monitoring Stack

#### Prometheus
- **Port:** 9090
- **Config:** `./monitoring/prometheus.yml`
- **Targets:** Backend (`backend:8000/metrics`)

#### Grafana
- **Port:** 3001
- **Datasource:** Prometheus (auto-configured)
- **Admin Password:** `./secrets/grafana_password.txt`

---

## 🛠️ Setup History & Troubleshooting

### What Happened: System Restart Recovery

The platform was initially set up but the system was restarted mid-installation. This caused several issues that were systematically resolved.

### Issues Encountered & Solutions

#### 1. Port Conflicts with Other Projects
**Problem:** SkillBridge and Ideas projects were already using standard ports.

**Solution:**
- PostgreSQL: 5432 → **5433**
- Redis: 6379 → **6380**
- Flower: 5555 → **5556**
- Backend: 8000 → **8001**

#### 2. Database Connection Failed
**Problem:** Backend couldn't connect to Postgres
```
connection to server at "localhost" (::1), port 5432 failed
```

**Root Cause:** `backend/src/db/base.py` defaulted to `localhost` instead of Docker network name.

**Solution:**
```python
# Changed:
host = os.getenv("DATABASE_HOST", "localhost")
# To:
host = os.getenv("DATABASE_HOST", "postgres")

# And added priority check:
database_url = os.getenv("DATABASE_URL")
if database_url:
    return database_url
```

#### 3. Python Import Errors
**Problem:**
```
ModuleNotFoundError: No module named 'api'
```

**Root Cause:** Relative imports (`from api.v1`) without proper PYTHONPATH.

**Solution:**
- Added `PYTHONPATH=/app/src` to docker-compose
- Changed all imports to absolute: `from src.api.v1 import ...`
- Created `backend/fix_imports.sh` to batch fix all files

#### 4. Missing JWT Secret
**Problem:**
```
ValueError: JWT secret key not found
```

**Solution:**
- Generated secure secret: `openssl rand -hex 32`
- Saved to `./secrets/jwt_secret.txt`
- Added to docker-compose secrets
- Exported as `SECRET_KEY` env var

#### 5. Qdrant Health Check Failed
**Problem:** Base Qdrant image lacks `curl` for health checks.

**Solution:**
- Created custom Dockerfile: `./docker/qdrant/Dockerfile`
- Installed curl in build
- Updated docker-compose to use custom image

#### 6. Neo4j Authentication Failed
**Problem:** `NEO4J_AUTH_FILE` environment variable not supported.

**Solution:**
```yaml
command: >
  sh -c "
    export NEO4J_AUTH=$$(cat /run/secrets/neo4j_auth) &&
    exec /startup/docker-entrypoint.sh neo4j
  "
```

#### 7. Prometheus Configuration Missing
**Problem:** `monitoring/prometheus.yml` was created as a directory instead of file.

**Solution:**
- Removed directory: `sudo rm -rf monitoring/prometheus.yml`
- Created proper YAML file with scrape configs
- Created `./tasks/003/fix_monitoring.sh` automation script

### Detailed Troubleshooting Logs

All setup issues are documented in:
- **Initial Diagnosis:** `./tasks/003/SETUP_SUMMARY.md`
- **Final Status:** `./tasks/003/FINAL_STATUS.md`
- **Fix Script:** `./tasks/003/fix_monitoring.sh`

---

## 💻 Development Workflow

### Backend Development

#### 1. Add New API Endpoint

```bash
# 1. Create schema (if needed)
vim backend/src/schemas/your_model.py

# 2. Create/update database model
vim backend/src/db/models.py

# 3. Generate migration
docker exec irstudy-backend alembic revision --autogenerate -m "Add your_model table"

# 4. Apply migration
docker exec irstudy-backend alembic upgrade head

# 5. Create API route
vim backend/src/api/v1/your_endpoint.py

# 6. Register route
vim backend/src/api/v1/router.py

# 7. Test endpoint
curl -X POST http://localhost:8001/api/v1/your-endpoint \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```

#### 2. Run Database Migrations

```bash
# Create migration
docker exec irstudy-backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker exec irstudy-backend alembic upgrade head

# Rollback one version
docker exec irstudy-backend alembic downgrade -1

# View migration history
docker exec irstudy-backend alembic history
```

#### 3. Access Database Directly

```bash
# Via Adminer (GUI)
Open: http://localhost:8080
System: PostgreSQL
Server: postgres
Username: postgres
Password: <from secrets/db_password.txt>
Database: irstudy_medical

# Via psql (CLI)
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical

# Common queries
\dt                          # List tables
\d users                     # Describe users table
SELECT * FROM users LIMIT 5; # View data
```

#### 4. View Logs

```bash
# Backend logs
docker logs irstudy-backend -f

# All services
docker compose logs -f

# Specific service
docker logs irstudy-postgres --tail 50

# Filter logs
docker logs irstudy-backend 2>&1 | grep ERROR
```

#### 5. Restart Services

```bash
# Restart single service
docker compose restart backend

# Restart all
docker compose restart

# Full rebuild
docker compose down
docker compose build
docker compose up -d
```

### Frontend Development (Future)

The frontend is planned to use:
- **Framework:** React + TypeScript
- **State Management:** TanStack Query (Task 016 completed)
- **Routing:** React Router
- **UI:** Material-UI or Tailwind CSS
- **API Client:** Auto-generated from FastAPI OpenAPI spec

See: `frontend/src/` for initial structure.

---

## 🔐 Security & Secrets

### Secrets Directory Structure

```
secrets/
├── anthropic_api_key.txt    # Claude API key
├── db_password.txt          # PostgreSQL password
├── flower_auth.txt          # Flower UI basic auth (user:pass)
├── grafana_password.txt     # Grafana admin password
├── jwt_secret.txt           # JWT signing key (64 chars hex)
├── neo4j_auth.txt          # Neo4j auth (neo4j/<password>)
├── openai_api_key.txt      # OpenAI API key
├── qdrant_api_key.txt      # Qdrant API authentication
└── redis_password.txt       # Redis password
```

### How Secrets Are Used

All secrets are mounted to `/run/secrets/` inside containers:

```yaml
secrets:
  jwt_secret:
    file: ./secrets/jwt_secret.txt

services:
  backend:
    secrets:
      - jwt_secret
    command: >
      sh -c "
        export SECRET_KEY=$$(cat /run/secrets/jwt_secret) &&
        uvicorn ...
      "
```

### Generate New Secrets

```bash
# Database password (32 chars alphanumeric)
openssl rand -base64 24 > secrets/db_password.txt

# JWT secret (64 chars hex)
openssl rand -hex 32 > secrets/jwt_secret.txt

# API key (64 chars hex)
openssl rand -hex 32 > secrets/qdrant_api_key.txt

# Basic auth (format: user:password)
echo "admin:$(openssl rand -base64 16)" > secrets/flower_auth.txt
```

### Security Best Practices

✅ **DO:**
- Keep `secrets/` directory in `.gitignore`
- Use Docker secrets for all sensitive data
- Rotate secrets regularly
- Use strong passwords (12+ chars, mixed case, numbers, symbols)
- Restrict file permissions: `chmod 600 secrets/*`

❌ **DON'T:**
- Commit secrets to git
- Hardcode passwords in docker-compose.yml
- Share secrets via insecure channels
- Use default passwords in production

---

## 📚 API Documentation

### Authentication Flow

#### 1. Register New User
```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!@#",
    "full_name": "John Smith"
  }'
```

#### 2. Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "SecurePass123!@#"
  }'

# Response:
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### 3. Access Protected Endpoint
```bash
TOKEN="your_access_token_here"

curl -X GET http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

### Interactive API Documentation

- **Swagger UI:** http://localhost:8001/api/docs
- **ReDoc:** http://localhost:8001/api/redoc
- **OpenAPI JSON:** http://localhost:8001/api/openapi.json

Try the "Authorize" button in Swagger UI to test authenticated endpoints.

---

## 🔧 Maintenance & Operations

### Health Checks

```bash
# Backend health
curl http://localhost:8001/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2026-02-03T06:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Monitoring

#### Prometheus Metrics
- **URL:** http://localhost:9090
- **Targets:** http://localhost:9090/targets
- **Query Example:** `http_requests_total`

#### Grafana Dashboards
- **URL:** http://localhost:3001
- **Default Credentials:** admin / (see `secrets/grafana_password.txt`)
- **Datasource:** Prometheus (pre-configured)

### Backup & Restore

#### Database Backup
```bash
# Create backup
docker exec irstudy-postgres pg_dump -U postgres irstudy_medical > backup_$(date +%Y%m%d).sql

# Restore from backup
cat backup_20260203.sql | docker exec -i irstudy-postgres psql -U postgres -d irstudy_medical
```

#### Qdrant Backup
```bash
# Backup via API
curl -X POST http://localhost:6333/collections/medical_knowledge/snapshots \
  -H "api-key: $(cat secrets/qdrant_api_key.txt)"

# Download snapshot
curl http://localhost:6333/collections/medical_knowledge/snapshots/{snapshot_name} \
  -H "api-key: $(cat secrets/qdrant_api_key.txt)" \
  -o medical_knowledge_snapshot.zip
```

### Performance Tuning

#### PostgreSQL Connection Pool
Edit `backend/src/db/base.py`:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,        # Increase for more concurrent connections
    max_overflow=40,     # Maximum overflow connections
    pool_timeout=30      # Connection timeout (seconds)
)
```

#### Redis Memory Limit
Edit `docker-compose.yml`:
```yaml
command: >
  redis-server
  --maxmemory 2gb      # Increase from 1gb
  --maxmemory-policy allkeys-lru
```

---

## 📂 Key Files Reference

### Configuration Files

| File | Purpose | Critical? |
|------|---------|-----------|
| `docker-compose.yml` | Service orchestration | ✅ Yes |
| `backend/alembic.ini` | Database migration config | ✅ Yes |
| `backend/src/db/base.py` | Database connection setup | ✅ Yes |
| `backend/src/main.py` | FastAPI application entry | ✅ Yes |
| `monitoring/prometheus.yml` | Prometheus scrape config | 🟡 Optional |
| `.gitignore` | Git exclusions (includes secrets/) | ✅ Yes |

### Scripts

| Script | Purpose |
|--------|---------|
| `backend/fix_imports.sh` | Fix relative to absolute imports |
| `tasks/003/fix_monitoring.sh` | Setup monitoring stack |
| `tasks/003/prereq.sh` | Start Docker stack |

### Documentation

| Document | Content |
|----------|---------|
| `README.md` | Project overview |
| `PLATFORM_SETUP_INDEX.md` | This file - master index |
| `tasks/003/SETUP_SUMMARY.md` | Initial diagnosis |
| `tasks/003/FINAL_STATUS.md` | Resolution details |
| `NEXT_STEPS.md` | Development roadmap |
| `PROJECT_CONSTRAINTS.md` | Medical accuracy requirements |

### Code Structure

```
irStudy/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/v1/            # API routes
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── users.py       # User management
│   │   │   ├── mcqs.py        # MCQ endpoints
│   │   │   ├── osces.py       # OSCE endpoints
│   │   │   ├── progress.py    # Analytics
│   │   │   └── router.py      # Route aggregation
│   │   ├── auth/              # Authentication logic
│   │   │   ├── security.py    # JWT, password hashing
│   │   │   └── dependencies.py # Auth decorators
│   │   ├── db/                # Database layer
│   │   │   ├── base.py        # Connection & session
│   │   │   └── models.py      # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas
│   │   │   ├── user.py
│   │   │   ├── mcq.py
│   │   │   └── osce.py
│   │   └── main.py            # FastAPI app
│   ├── alembic/               # Database migrations
│   │   ├── versions/          # Migration files
│   │   └── env.py             # Migration environment
│   ├── Dockerfile             # Backend container build
│   ├── requirements.txt       # Python dependencies
│   └── alembic.ini            # Alembic configuration
│
├── frontend/                   # React frontend (future)
│   └── src/                   # Source code
│
├── data/                       # Medical knowledge data
│   ├── mcqs/                  # MCQ JSON files
│   ├── osces/                 # OSCE scenarios
│   ├── chunks.json            # RAG knowledge chunks
│   └── processed/             # Processed textbooks
│
├── docker/                     # Custom Docker builds
│   ├── qdrant/
│   │   └── Dockerfile         # Qdrant with curl
│   └── neo4j_import/          # Neo4j data imports
│
├── monitoring/                 # Monitoring configs
│   ├── prometheus.yml         # Prometheus scrape config
│   └── grafana/
│       ├── dashboards/
│       └── datasources/       # Grafana datasources
│
├── scripts/                    # Utility scripts
│   ├── chunk_medical_texts.py
│   ├── generate_embeddings.py
│   └── index_qdrant.py
│
├── secrets/                    # Sensitive credentials
│   ├── db_password.txt
│   ├── jwt_secret.txt
│   └── ... (all secret files)
│
├── tasks/                      # Task tracking
│   └── 003/                   # Setup task docs
│
├── docker-compose.yml          # Service orchestration
└── PLATFORM_SETUP_INDEX.md     # This file
```

---

## 🎯 Common Tasks Quick Reference

### Start Fresh Environment
```bash
docker compose down -v  # Remove volumes
rm -rf docker/qdrant_storage/*
docker compose up -d
```

### View Service Status
```bash
docker compose ps
docker compose logs backend --tail 50
```

### Test Backend API
```bash
# Health check
curl http://localhost:8001/health

# Root endpoint
curl http://localhost:8001/

# API docs
open http://localhost:8001/api/docs
```

### Access Database
```bash
# Via Adminer
open http://localhost:8080

# Via CLI
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical
```

### Update Backend Code
```bash
# Restart with reload
docker compose restart backend

# Force rebuild
docker compose build backend
docker compose up -d backend
```

### Add Database Migration
```bash
docker exec irstudy-backend alembic revision --autogenerate -m "your description"
docker exec irstudy-backend alembic upgrade head
```

---

## 🆘 Troubleshooting Guide

### Backend Won't Start

**Check logs:**
```bash
docker logs irstudy-backend --tail 100
```

**Common issues:**
1. Missing secret → Check `secrets/` directory
2. Port conflict → Change port in docker-compose.yml
3. Import error → Run `backend/fix_imports.sh`
4. Database connection → Verify postgres is healthy: `docker compose ps`

### Database Connection Error

```bash
# Verify postgres is running
docker compose ps postgres

# Check connection from backend
docker exec irstudy-backend ping -c 3 postgres

# View postgres logs
docker logs irstudy-postgres --tail 50

# Test connection manually
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1"
```

### Port Already in Use

```bash
# Find what's using port 8001
sudo lsof -i :8001

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Reset Everything

```bash
# Nuclear option - removes all data
docker compose down -v
sudo rm -rf docker/qdrant_storage/*
docker compose up -d
```

---

## 📞 Support & Resources

### Documentation
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Docker Compose:** https://docs.docker.com/compose
- **PostgreSQL:** https://www.postgresql.org/docs
- **Qdrant:** https://qdrant.tech/documentation
- **Neo4j:** https://neo4j.com/docs

### Project-Specific
- **API Docs:** http://localhost:8001/api/docs
- **Setup History:** `./tasks/003/`
- **Constraints:** `./PROJECT_CONSTRAINTS.md`
- **Medical Context:** All resources use Australian standards (AMC, AHPRA, eTG)

---

## ✅ Checklist: Fresh Setup

Use this checklist when setting up on a new machine:

- [ ] Clone repository
- [ ] Install Docker & Docker Compose
- [ ] Create `secrets/` directory with all required files:
  - [ ] `db_password.txt`
  - [ ] `redis_password.txt`
  - [ ] `jwt_secret.txt` (generate: `openssl rand -hex 32`)
  - [ ] `qdrant_api_key.txt`
  - [ ] `neo4j_auth.txt` (format: `neo4j/<password>`)
  - [ ] `openai_api_key.txt`
  - [ ] `anthropic_api_key.txt`
  - [ ] `grafana_password.txt`
  - [ ] `flower_auth.txt` (format: `user:password`)
- [ ] Run `docker compose up -d`
- [ ] Wait ~60 seconds for services to start
- [ ] Verify: `docker compose ps` (8 services healthy)
- [ ] Test backend: `curl http://localhost:8001/`
- [ ] Access API docs: http://localhost:8001/api/docs
- [ ] Create first user via `/api/v1/auth/register`

---

**🎉 Platform Ready for Development!**

This index should serve as your complete reference for understanding, maintaining, and developing the irStudy Medical Education Platform. For specific implementation details, refer to the linked documentation files.

**Last Updated:** 2026-02-03
**Maintained By:** Development Team
**Version:** 1.0.0
