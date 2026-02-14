# irStudy Build & Run Instructions

**Project**: HIPAA-Compliant Medical Education Platform
**Last Updated**: 2026-02-01
**Environment**: Development (Week 1 of 8)

---

## 🏗️ Project Structure

```
irStudy/
├── backend/              # FastAPI application
│   ├── src/
│   │   ├── main.py      # App entry point
│   │   ├── modules/     # Auth, MCQ, OSCE modules
│   │   ├── routers/     # API endpoints
│   │   └── schemas/     # Pydantic models
│   ├── tests/           # PyTest test suite
│   ├── Dockerfile       # Production container image
│   └── requirements.txt # Python dependencies
├── frontend/            # React + TypeScript UI
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── pages/       # Route pages
│   │   └── services/    # API client
│   ├── public/          # Static assets
│   └── package.json     # Node dependencies
├── docker/              # Docker configurations
│   └── postgres/        # Database init scripts
├── secrets/             # Docker secrets (chmod 600)
│   ├── db_password.txt
│   ├── redis_password.txt
│   ├── qdrant_api_key.txt
│   ├── neo4j_auth.txt
│   ├── openai_api_key.txt
│   ├── anthropic_api_key.txt
│   ├── flower_auth.txt
│   └── grafana_password.txt
├── planning/            # 8-week implementation plan
├── data/                # Medical content (MCQs, OSCEs)
├── scripts/             # Utility scripts
├── docs/                # Documentation
├── .env                 # Environment variables (not in Git)
├── .env.template        # Environment template (in Git)
├── docker-compose.yml   # 11-service Docker stack
├── skills-registry.json # Agent OS skill definitions
├── PROMPT.md            # Ralph development instructions
├── @fix_plan.md         # Prioritized task list (this drives development)
└── @AGENT.md            # This file (build/run instructions)
```

---

## 🚀 Quick Start (First Time Setup)

### Prerequisites
- Docker 20.10+ with Docker Compose
- Node.js 18+ with npm
- Python 3.11+
- Git
- pwgen (for secret generation)

### Initial Setup (30 minutes)

```bash
# 1. Clone repository (if not already)
cd /home/dev/Development/irStudy

# 2. Install cybersecurity framework (30 min)
cd /home/dev/Development/cyberSecurity
./INSTALL_ALL_SECURITY_TOOLS.sh
./SETUP_PROJECT_HOOKS.sh irStudy

# 3. Create secrets directory (5 min)
cd /home/dev/Development/irStudy
mkdir -p secrets && chmod 700 secrets
echo "$(pwgen -s 32 1)" > secrets/db_password.txt
echo "$(pwgen -s 32 1)" > secrets/redis_password.txt
echo "$(pwgen -s 64 1)" > secrets/qdrant_api_key.txt
echo "neo4j/$(pwgen -s 32 1)" > secrets/neo4j_auth.txt
echo "sk-placeholder" > secrets/openai_api_key.txt
echo "sk-ant-placeholder" > secrets/anthropic_api_key.txt
echo "admin:$(pwgen -s 24 1)" > secrets/flower_auth.txt
echo "$(pwgen -s 24 1)" > secrets/grafana_password.txt
chmod 600 secrets/*.txt

# 4. Create .env file (2 min)
cp .env.template .env
JWT_SECRET=$(openssl rand -hex 32)
sed -i "s/__GENERATE_ME__/$JWT_SECRET/" .env

# 5. Start Docker stack (2 min)
docker-compose up -d

# 6. Wait for services to be healthy (30 seconds)
sleep 30
docker-compose ps
```

**Expected Output:**
```
NAME                STATUS
irstudy-postgres    Up (healthy)
irstudy-redis       Up (healthy)
irstudy-qdrant      Up (healthy)
irstudy-neo4j       Up (healthy)
irstudy-backend     Up (healthy)
irstudy-frontend    Up
irstudy-celery      Up
irstudy-flower      Up
irstudy-prometheus  Up
irstudy-grafana     Up
irstudy-nginx       Up
```

---

## 🐳 Docker Stack Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
# All services
docker-compose logs --tail=100 -f

# Specific service
docker-compose logs --tail=100 -f backend
docker-compose logs --tail=100 -f postgres
```

### Restart Service
```bash
docker-compose restart backend
```

### Check Service Health
```bash
docker-compose ps
curl http://localhost:8000/api/health  # Backend
curl http://localhost:3000             # Frontend
curl http://localhost:6333/            # Qdrant
```

### Rebuild Service
```bash
docker-compose up -d --build backend
```

---

## 💻 Backend Development

### Install Dependencies
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run Backend Locally (without Docker)
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Run Tests
```bash
cd backend
source venv/bin/activate
pytest -v tests/
pytest --cov=src --cov-report=html tests/
```

### Database Migrations
```bash
cd backend
source venv/bin/activate

# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
cd backend

# Linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/

# Type checking
mypy src/

# Security scanning
bandit -r src/
semgrep --config auto src/
```

---

## 🎨 Frontend Development

### Install Dependencies
```bash
cd frontend
npm install
```

### Run Frontend Locally
```bash
cd frontend
npm run dev
# Access at: http://localhost:5173
```

### Build for Production
```bash
cd frontend
npm run build
npm run preview  # Test production build
```

### Run Tests
```bash
cd frontend
npm test
npm run test:coverage
```

### Code Quality
```bash
cd frontend

# Linting
npm run lint
npm run lint:fix

# Type checking
npm run type-check

# Formatting
npm run format
```

---

## 🔒 Security Scanning

### Pre-commit Hooks (Automatic)
```bash
# Runs automatically on git commit
git commit -m "message"

# Manual run
pre-commit run --all-files
```

### Manual Security Scans
```bash
# Container vulnerabilities
trivy image irstudy-backend:latest

# Code vulnerabilities
semgrep --config auto backend/src/
bandit -r backend/src/

# Secrets scanning
gitleaks detect --no-git

# Dependency vulnerabilities
pip-audit
npm audit
```

---

## 🧪 Testing

### Run All Tests
```bash
# Backend tests
cd backend && pytest -v

# Frontend tests
cd frontend && npm test

# End-to-end tests (Playwright)
cd tests/e2e && npx playwright test
```

### Coverage Reports
```bash
# Backend coverage
cd backend
pytest --cov=src --cov-report=html tests/
open htmlcov/index.html

# Frontend coverage
cd frontend
npm run test:coverage
open coverage/lcov-report/index.html
```

### Integration Tests
```bash
# Requires Docker stack running
docker-compose up -d
cd backend
pytest tests/integration/ -v
```

---

## 📊 Monitoring & Debugging

### Access Monitoring Tools

| Service | URL | Credentials |
|---------|-----|-------------|
| Backend API Docs | http://localhost:8000/docs | None (public) |
| Frontend App | http://localhost:3000 | Login required |
| Flower (Celery) | http://localhost:5555 | In `secrets/flower_auth.txt` |
| Grafana | http://localhost:3001 | admin / `secrets/grafana_password.txt` |
| Prometheus | http://localhost:9090 | None |
| Neo4j Browser | http://localhost:7474 | In `secrets/neo4j_auth.txt` |
| Qdrant Dashboard | http://localhost:6333/dashboard | None |

### Database Access
```bash
# PostgreSQL
docker exec -it irstudy-postgres psql -U postgres -d irstudy_medical

# Redis
docker exec -it irstudy-redis redis-cli -a "$(cat secrets/redis_password.txt)"

# Neo4j Cypher Shell
docker exec -it irstudy-neo4j cypher-shell -u neo4j -p "$(cat secrets/neo4j_auth.txt | cut -d'/' -f2)"
```

### Debug Mode
```bash
# Backend debug logs
export LOG_LEVEL=DEBUG
docker-compose restart backend

# Frontend debug mode
cd frontend
VITE_DEBUG=true npm run dev
```

---

## 🤖 Agent OS Integration

### Skills Registry
```bash
# View available skills
cat skills-registry.json | jq '.skills[] | {id, name, description}'

# Validate skills registry
cat skills-registry.json | jq empty  # No output = valid JSON
```

### Test Agent Skills
```python
# backend/src/agents/base_agent.py
from src.agents.base_agent import BaseAgent

agent = BaseAgent()
mcq = agent.generate_mcq(topic="cardiology", difficulty="medium", count=1)
print(mcq)
```

---

## 📦 Data Management

### Load Medical Content
```bash
# MCQs (18,000+)
cd scripts
python load_mcqs.py --source data/mcqs/ --collection respiratory

# OSCEs (3,000+)
python load_osces.py --source data/osces/

# RAG Vectors (42,647)
python load_vectors.py --source data/rag_vectors/ --collection medical_knowledge
```

### Backup Data
```bash
# PostgreSQL backup
docker exec irstudy-postgres pg_dump -U postgres irstudy_medical > backup_$(date +%Y%m%d).sql

# Qdrant backup
curl -X POST http://localhost:6333/collections/medical_knowledge/snapshots
```

---

## 🚀 Deployment (Future - Week 6)

### Production Build
```bash
# Backend
cd backend
docker build -t irstudy-backend:v1.0 .

# Frontend
cd frontend
npm run build
```

### Environment Variables
```bash
# Production .env
export ENV=production
export DEBUG=false
export LOG_LEVEL=INFO
export DATABASE_URL=postgresql://...
# ... (see .env.template for full list)
```

---

## 🆘 Troubleshooting

### Docker Service Won't Start
```bash
# Check logs
docker-compose logs <service>

# Common issues:
# - Port conflict: Change port in docker-compose.yml
# - Secret not found: Verify secrets/ directory
# - Memory limit: Increase in docker-compose.yml (mem_limit)
```

### Database Connection Failed
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Check connection string in .env
cat .env | grep DATABASE_URL

# Test connection
docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1;"
```

### API Returns 500 Error
```bash
# Check backend logs
docker-compose logs backend --tail=100

# Common issues:
# - Missing environment variable
# - Database migration not applied
# - Invalid JWT secret
```

### Pre-commit Hook Fails
```bash
# Review errors
pre-commit run --all-files

# Fix issues, then retry
# Common: GitLeaks false positives (add to .gitleaks.toml)
```

---

## 📖 Additional Resources

- **Master Plan**: `planning/final-implementation-plan-2026-02-01/00_MASTER_PLAN.md`
- **Week 1 Tasks**: `planning/final-implementation-plan-2026-02-01/01_WEEK1_SECURITY_FOUNDATION.md`
- **Project Constraints**: `PROJECT_CONSTRAINTS.md`
- **Security Runbook**: `docs/SECURITY_RUNBOOK.md` (create in Task 007)
- **API Documentation**: http://localhost:8000/docs (when backend running)

---

## 🔄 Development Cycle (For Ralph Autonomous Loop)

### Typical Workflow

1. **Read @fix_plan.md** - Check next task
2. **Implement** - Write code following TDD (tests first)
3. **Test** - Run tests, ensure 100% pass rate
4. **Scan** - Run security scans (pre-commit hooks)
5. **Commit** - Atomic commit with conventional message
6. **Update** - Mark task complete in @fix_plan.md
7. **Repeat** - Move to next task

### Quality Gates (Must Pass)
- ✅ Tests: 80%+ coverage, 100% pass rate
- ✅ Security: 0 critical vulnerabilities
- ✅ Linting: 0 errors
- ✅ Build: Docker images build successfully
- ✅ Performance: API <200ms, Page load <2s

---

**Remember**: This is a HIPAA-compliant medical platform. Security and accuracy are paramount. Never skip security scans or tests.

**Last Updated**: 2026-02-01
**Next Review**: End of Week 1 (2026-02-08)
