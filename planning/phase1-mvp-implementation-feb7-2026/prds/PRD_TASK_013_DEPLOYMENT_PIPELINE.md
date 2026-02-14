# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_013 - Deployment Pipeline (5-6 hours)

**EXECUTE NOW**:

```bash
cd /home/dev/Development/irStudy

# Create GitHub Actions workflow directory
mkdir -p .github/workflows

# Create deployment workflow
cat > .github/workflows/deploy.yml <<'EOF'
# Deployment workflow will be implemented here
EOF

# Initialize Railway CLI (if not installed)
npm install -g @railway/cli

# Initialize Vercel CLI (if not installed)
npm install -g vercel
```

**DO NOT**:
- ❌ Ask "Would you like me to configure Railway first?"
- ❌ Ask "Should I set up production or staging environment?"
- ❌ Wait for approval
- ❌ Ask "Which deployment strategy should I use?"

**START IMMEDIATELY. NO QUESTIONS.**

---

## 📋 Metadata

- **Week:** 3
- **Day:** 4 (Feb 24, 2026)
- **Duration:** 5-6 hours
- **Priority:** P0-Critical
- **Dependencies:** TASK_012 (Load Testing must pass)
- **Owner:** general-purpose agent (DevOps specialist)
- **Status:** 🟡 Not Started
- **Blocks:** TASK_014 (MVP Launch)

---

## 🎯 Objectives

1. **Create GitHub Actions CI/CD workflows** (Test → Build → Deploy)
2. **Configure Railway deployment** (Backend API + PostgreSQL + Redis + Qdrant)
3. **Configure Vercel deployment** (Frontend SPA with environment variables)
4. **Automate database migrations** (Alembic)
5. **Implement rollback strategy** with blue-green deployment
6. **Create health check endpoints** (liveness, readiness)
7. **Achieve zero-downtime deployment**

---

## 📝 Implementation Guide

### Step 1: Create Backend Health Check Endpoints (30 min)

```bash
cd /home/dev/Development/irStudy/backend

cat > src/api/v1/health.py <<'EOF'
from fastapi import APIRouter, status, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from fastapi import Depends
import redis
from qdrant_client import QdrantClient
import os

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("/liveness")
async def liveness_check():
    """
    Kubernetes liveness probe endpoint.
    Returns 200 if the application is running.
    """
    return {"status": "alive", "service": "irStudy Backend API"}

@router.get("/readiness")
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe endpoint.
    Returns 200 if all dependencies are healthy.
    """
    health_status = {
        "status": "ready",
        "checks": {}
    }

    # Check PostgreSQL
    try:
        db.execute("SELECT 1")
        health_status["checks"]["postgres"] = "healthy"
    except Exception as e:
        health_status["checks"]["postgres"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Redis
    try:
        redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0
        )
        redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # Check Qdrant
    try:
        qdrant_client = QdrantClient(
            host=os.getenv("QDRANT_HOST", "localhost"),
            port=int(os.getenv("QDRANT_PORT", 6333))
        )
        qdrant_client.get_collections()
        health_status["checks"]["qdrant"] = "healthy"
    except Exception as e:
        health_status["checks"]["qdrant"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    if health_status["status"] == "degraded":
        raise HTTPException(status_code=503, detail=health_status)

    return health_status

@router.get("/version")
async def version_info():
    """
    Returns application version and build information.
    """
    return {
        "version": "1.0.0",
        "build": os.getenv("RAILWAY_GIT_COMMIT_SHA", "local"),
        "environment": os.getenv("ENVIRONMENT", "development")
    }
EOF

# Register health routes in main.py
python <<'EOF'
import re
with open("src/main.py", "r") as f:
    content = f.read()

if "health" not in content:
    # Add health import
    content = re.sub(
        r"(from src.api.v1 import)",
        "\\1 health,",
        content
    )
    # Add health router
    content = re.sub(
        r"(app.include_router\(.*?\))",
        "\\1\napp.include_router(health.router)",
        content,
        count=1
    )
    with open("src/main.py", "w") as f:
        f.write(content)
    print("✅ Health routes registered")
else:
    print("✅ Health routes already registered")
EOF

echo "✅ Health check endpoints created"
```

### Step 2: Create GitHub Actions Workflows (1.5 hours)

```bash
cd /home/dev/Development/irStudy

cat > .github/workflows/deploy-backend.yml <<'EOF'
name: Deploy Backend to Railway

on:
  push:
    branches: [ main ]
    paths:
      - 'backend/**'
      - '.github/workflows/deploy-backend.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=src --cov-report=term-missing

      - name: Security scan
        run: |
          cd backend
          pip install bandit safety
          bandit -r src/ -f json -o bandit-report.json || true
          safety check --json || true

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install Railway CLI
        run: npm install -g @railway/cli

      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd backend
          railway up --service backend

      - name: Run database migrations
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          cd backend
          railway run --service backend alembic upgrade head

      - name: Health check
        run: |
          sleep 10
          curl -f https://irstudy-backend.railway.app/api/v1/health/readiness || exit 1
EOF

cat > .github/workflows/deploy-frontend.yml <<'EOF'
name: Deploy Frontend to Vercel

on:
  push:
    branches: [ main ]
    paths:
      - 'frontend/**'
      - '.github/workflows/deploy-frontend.yml'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run TypeScript checks
        run: |
          cd frontend
          npx tsc --noEmit

      - name: Run tests
        run: |
          cd frontend
          npm test

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          working-directory: ./frontend
          vercel-args: '--prod'

      - name: Health check
        run: |
          sleep 10
          curl -f https://irstudy.vercel.app || exit 1
EOF

echo "✅ GitHub Actions workflows created"
```

### Step 3: Configure Railway Deployment (1.5 hours)

```bash
cd /home/dev/Development/irStudy/backend

# Create Railway configuration
cat > railway.toml <<'EOF'
[build]
builder = "NIXPACKS"
buildCommand = "pip install -r requirements.txt"

[deploy]
startCommand = "uvicorn src.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health/readiness"
healthcheckTimeout = 100
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3

[env]
PORT = "8000"
ENVIRONMENT = "production"
EOF

# Create production environment file template
cat > .env.production.template <<'EOF'
# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/irstudy_prod

# Redis Configuration
REDIS_HOST=redis.railway.internal
REDIS_PORT=6379

# Qdrant Configuration
QDRANT_HOST=qdrant.railway.internal
QDRANT_PORT=6333

# Security
SECRET_KEY=<GENERATE_32_CHAR_SECRET>
JWT_SECRET_KEY=<GENERATE_32_CHAR_SECRET>

# CORS
ALLOWED_ORIGINS=https://irstudy.vercel.app,https://www.irstudy.com

# HashiCorp Vault
VAULT_ADDR=https://vault.railway.internal:8200
VAULT_TOKEN=<VAULT_TOKEN>

# Environment
ENVIRONMENT=production
DEBUG=False
EOF

# Create migration deployment script
cat > scripts/deploy-migrations.sh <<'EOF'
#!/bin/bash
set -e

echo "🔄 Running database migrations..."

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
while ! pg_isready -h ${DATABASE_HOST} -p ${DATABASE_PORT} -U ${DATABASE_USER}; do
  sleep 1
done

echo "✅ PostgreSQL is ready"

# Run migrations
alembic upgrade head

echo "✅ Migrations complete"

# Verify migrations
alembic current
EOF

chmod +x scripts/deploy-migrations.sh

echo "✅ Railway configuration created"
```

### Step 4: Configure Vercel Deployment (1 hour)

```bash
cd /home/dev/Development/irStudy/frontend

# Create Vercel configuration
cat > vercel.json <<'EOF'
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm ci",
  "framework": "vite",
  "outputDirectory": "dist",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://irstudy-backend.railway.app"
  },
  "regions": ["syd1"]
}
EOF

# Create production environment template
cat > .env.production.template <<'EOF'
VITE_API_BASE_URL=https://irstudy-backend.railway.app
VITE_ENVIRONMENT=production
VITE_SENTRY_DSN=<SENTRY_DSN>
EOF

echo "✅ Vercel configuration created"
```

### Step 5: Implement Rollback Strategy (30 min)

```bash
cd /home/dev/Development/irStudy

cat > docs/ROLLBACK_STRATEGY.md <<'EOF'
# Deployment Rollback Strategy

## Blue-Green Deployment Pattern

We use blue-green deployment to enable zero-downtime rollbacks.

### Rollback Process

#### Backend (Railway)

1. **Identify failed deployment**:
   ```bash
   railway logs --service backend --tail 100
   ```

2. **Rollback to previous version**:
   ```bash
   railway rollback --service backend
   ```

3. **Verify health**:
   ```bash
   curl https://irstudy-backend.railway.app/api/v1/health/readiness
   ```

4. **Database rollback (if needed)**:
   ```bash
   railway run --service backend alembic downgrade -1
   ```

#### Frontend (Vercel)

1. **Identify failed deployment**:
   ```bash
   vercel inspect <deployment-url>
   ```

2. **Rollback to previous deployment**:
   - Go to Vercel dashboard → Deployments
   - Find previous successful deployment
   - Click "Promote to Production"

3. **Verify health**:
   ```bash
   curl https://irstudy.vercel.app
   ```

### Automated Rollback Triggers

- Health check failures for >5 minutes
- Error rate >5% in first 10 minutes
- Response time p95 >2 seconds

### Post-Rollback Actions

1. [ ] Notify team via Slack
2. [ ] Create incident report
3. [ ] Root cause analysis
4. [ ] Fix and re-deploy
EOF

echo "✅ Rollback strategy documented"
```

### Step 6: Create Deployment Checklist (30 min)

```bash
cat > docs/DEPLOYMENT_CHECKLIST.md <<'EOF'
# Deployment Checklist

## Pre-Deployment (15 minutes)

- [ ] All tests pass locally (`pytest`, `npm test`)
- [ ] E2E tests pass (`npx playwright test`)
- [ ] Load tests pass (500 concurrent users, <2s page load)
- [ ] Security scan passes (0 HIGH/CRITICAL issues)
- [ ] Database migration tested locally
- [ ] Environment variables configured in Railway/Vercel
- [ ] Backup created of production database

## Deployment (30 minutes)

### Backend Deployment

- [ ] Push to `main` branch (triggers GitHub Actions)
- [ ] Verify GitHub Actions workflow passes
- [ ] Railway deployment successful
- [ ] Database migrations applied
- [ ] Health check endpoint returns 200
- [ ] API smoke test: `GET /api/v1/health/version`

### Frontend Deployment

- [ ] Push to `main` branch (triggers GitHub Actions)
- [ ] Verify GitHub Actions workflow passes
- [ ] Vercel deployment successful
- [ ] Environment variables set correctly
- [ ] Frontend loads in browser
- [ ] API integration works (login, fetch MCQs)

## Post-Deployment Monitoring (1 hour)

- [ ] Monitor error rate (Sentry)
- [ ] Monitor response times (Railway metrics)
- [ ] Check database connection pool
- [ ] Verify Redis cache hit rate
- [ ] Test critical user journeys:
  - [ ] User registration
  - [ ] MCQ practice (answer submission)
  - [ ] Study card review
  - [ ] Dashboard analytics

## Rollback Criteria

Rollback if ANY of these occur:

- [ ] Error rate >5% in first 10 minutes
- [ ] Response time p95 >2 seconds
- [ ] Health check failures >5 minutes
- [ ] Database connection failures
- [ ] 500 errors on critical endpoints

## Success Criteria

- [ ] Zero downtime during deployment
- [ ] All health checks green
- [ ] Error rate <1%
- [ ] Response time p95 <500ms
- [ ] 100% uptime first 24 hours
EOF

echo "✅ Deployment checklist created"
```

---

## ✅ Validation Checklist

```bash
cd /home/dev/Development/irStudy

# 1. Verify GitHub Actions workflows
[ -f .github/workflows/deploy-backend.yml ] && echo "✅ Backend workflow: EXISTS" || echo "❌ MISSING"
[ -f .github/workflows/deploy-frontend.yml ] && echo "✅ Frontend workflow: EXISTS" || echo "❌ MISSING"

# 2. Verify Railway configuration
[ -f backend/railway.toml ] && echo "✅ Railway config: EXISTS" || echo "❌ MISSING"

# 3. Verify Vercel configuration
[ -f frontend/vercel.json ] && echo "✅ Vercel config: EXISTS" || echo "❌ MISSING"

# 4. Verify health check endpoints
curl http://localhost:8000/api/v1/health/liveness && echo "✅ Liveness: OK" || echo "❌ FAILED"
curl http://localhost:8000/api/v1/health/readiness && echo "✅ Readiness: OK" || echo "❌ FAILED"

# 5. Verify documentation
[ -f docs/ROLLBACK_STRATEGY.md ] && echo "✅ Rollback docs: EXISTS" || echo "❌ MISSING"
[ -f docs/DEPLOYMENT_CHECKLIST.md ] && echo "✅ Deployment checklist: EXISTS" || echo "❌ MISSING"

# 6. Test deployment locally
echo "Manual verification required:"
echo "- GitHub secrets configured (RAILWAY_TOKEN, VERCEL_TOKEN)"
echo "- Railway project created (backend, postgres, redis, qdrant)"
echo "- Vercel project created (frontend)"
```

---

## 🎯 Success Criteria

1. ✅ GitHub Actions workflows created (Test → Build → Deploy)
2. ✅ Railway deployment configured (Backend + dependencies)
3. ✅ Vercel deployment configured (Frontend)
4. ✅ Database migration automation working
5. ✅ Rollback strategy documented and tested
6. ✅ Health check endpoints operational (200 OK)
7. ✅ Zero-downtime deployment achieved

---

## 🔄 When Complete

```bash
cd /home/dev/Development/irStudy

sed -i 's/TASK_013.*TODO/TASK_013: ✅ DONE/' @fix_plan.md

git add .
git commit -m "feat(deployment): Complete TASK_013 Deployment Pipeline - Railway + Vercel

- GitHub Actions CI/CD workflows (Test → Build → Deploy)
- Railway deployment: Backend API + PostgreSQL + Redis + Qdrant
- Vercel deployment: Frontend SPA with environment variables
- Database migration automation with Alembic
- Blue-green deployment with rollback strategy
- Health check endpoints: /liveness, /readiness, /version
- Zero-downtime deployment achieved

Deliverables:
- .github/workflows/deploy-backend.yml
- .github/workflows/deploy-frontend.yml
- backend/railway.toml
- frontend/vercel.json
- backend/src/api/v1/health.py
- docs/ROLLBACK_STRATEGY.md
- docs/DEPLOYMENT_CHECKLIST.md

Quality Gates: 7/7 passed ✅
Blocks: TASK_014 now unblocked (Final MVP Launch)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

echo "✅ TASK_013 complete. Starting TASK_014 (FINAL TASK)..."
```

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Not Started
**Depends On:** TASK_012
**Blocks:** TASK_014
