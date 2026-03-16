# PRD_GAP_001: Infrastructure Deployment (Vault + Redis)

**Priority**: P0 - CRITICAL BLOCKER
**Estimated Effort**: 6 hours
**Dependencies**: None (Week 1 foundation)
**Owner**: security-compliance-expert + backend-infrastructure

---

## 1. REQUEST (What & Why)

### User Story
> As a platform developer,
> I need Vault and Redis servers deployed and operational,
> So that applications can store secrets securely and WebSocket sessions can function.

### Business Context
- **Current State**: Vault and Redis client code complete (~400 lines) but servers NOT deployed
- **Impact**: Week 1 (Shared Infrastructure) INCOMPLETE - blocks ALL further development per master plan
- **Risk**: Applications using `.env` fallback with hardcoded credentials (SECURITY VIOLATION)

### Problem Statement
1. Vault server not running → applications read secrets from `.env.dev` (tracked in git)
2. Redis server not running → WebSocket sessions fail, rate limiting disabled, no caching
3. `.env.dev` contains hardcoded credentials → security audit FAILS
4. 127 security tests not executable → cannot validate HIPAA compliance

### Success Metrics
- [ ] Vault operational at `http://localhost:8200`
- [ ] Redis operational at `localhost:6380`
- [ ] Zero hardcoded credentials in git (`.env.dev` removed)
- [ ] 127 security tests passing (100%)
- [ ] Applications using Vault (not `.env` fallback)

---

## 2. ARCHITECTURE (How)

### 2.1 Vault Deployment

**Development Mode** (for testing):
```bash
vault server -dev \
  -dev-root-token-id="dev-only-token-change-in-prod" \
  -dev-listen-address="0.0.0.0:8200"
```

**Production Mode** (for staging/production):
```bash
vault server -config=/etc/vault/config.hcl
```

**Configuration File** (`/etc/vault/config.hcl`):
```hcl
storage "file" {
  path = "/opt/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 1  # Enable TLS in production
}

api_addr = "http://127.0.0.1:8200"
ui = true
```

**Secret Hierarchy** (from `SHARED_INFRASTRUCTURE_SPEC.md`):
```
secret/
├── database/
│   ├── postgres-irstudy-password
│   └── postgres-connection-string
├── emr/
│   ├── claude-api-key
│   ├── session-encryption-key
│   └── template-signing-key
├── ai-osce/
│   ├── claude-api-key
│   ├── kimi-api-key
│   ├── redis-password
│   ├── websocket-secret
│   └── session-encryption-key
└── shared/
    ├── jwt-secret
    ├── https-tls-cert
    └── https-tls-key
```

**Setup Script** (already exists):
- File: `/home/dev/Development/irStudy/backend/scripts/setup_vault.py`
- Action: Run after Vault server starts
- Creates all secret paths and policies

### 2.2 Redis Deployment

**Docker Deployment** (recommended for development):
```bash
docker run -d \
  --name irstudy-redis \
  -p 6380:6379 \
  -v /opt/redis/data:/data \
  redis:7 \
  --requirepass "$(vault kv get -field=password secret/ai-osce/redis-password)" \
  --maxmemory 2.5gb \
  --maxmemory-policy allkeys-lru \
  --save 60 1000 \
  --appendonly yes
```

**Configuration** (`redis.conf`):
```conf
# Memory
maxmemory 2560mb  # 2.5 GB (512 MB EMR + 2 GB OSCE)
maxmemory-policy allkeys-lru

# Persistence
save 60 1000
save 300 100
save 900 1
appendonly yes
appendfsync everysec

# Security
requirepass <from-vault>
bind 0.0.0.0
protected-mode yes

# Namespaces (enforced in application code)
# emr:* - 512 MB allocation
# osce:* - 2 GB allocation
```

**Health Check**:
```bash
redis-cli -p 6380 -a <password> PING
# Expected: PONG
```

### 2.3 Remove .env.dev from Git

**Actions**:
```bash
# 1. Remove from git (keep local copy)
git rm --cached backend/.env.dev
git rm --cached frontend/.env.dev

# 2. Add to .gitignore
echo "*.env" >> .gitignore
echo ".env.*" >> .gitignore
echo "!.env.example" >> .gitignore

# 3. Commit changes
git add .gitignore
git commit -m "security: remove .env files with hardcoded credentials

- Removed backend/.env.dev and frontend/.env.dev from git
- Added *.env to .gitignore (except .env.example)
- All applications now use Vault for secrets
- Fixes security violation: hardcoded PostgreSQL, Redis, Claude API credentials"

# 4. Rotate exposed credentials
# - PostgreSQL password
# - Redis password
# - Claude API key (if exposed)
# - JWT secret
```

**Create Template**:
```bash
# backend/.env.example
VAULT_ADDR=http://localhost:8200
VAULT_TOKEN=dev-only-token-change-in-prod
DATABASE_URL=postgresql://postgres:<FROM_VAULT>@localhost:5433/irstudy_medical
REDIS_URL=redis://:<FROM_VAULT>@localhost:6380
ENVIRONMENT=development
```

### 2.4 Update Applications to Use Vault

**Verification Checklist**:
- [ ] `backend/src/main.py` initializes Vault client on startup
- [ ] `backend/src/core/vault.py` successfully connects
- [ ] All API keys fetched from Vault (no `.env` fallback used)
- [ ] Redis password from Vault
- [ ] PostgreSQL password from Vault
- [ ] JWT secret from Vault

**Test**:
```bash
# Stop Vault server temporarily
vault server -dev &  # Start first
python -c "from backend.src.core.vault import get_vault_secret; print(get_vault_secret('secret/database/postgres-irstudy-password'))"
# Should print password (not None)
```

---

## 3. IMPLEMENTATION TASKS

### Task 1: Deploy Vault (1 hour)

**Steps**:
1. Install Vault:
   ```bash
   wget https://releases.hashicorp.com/vault/1.15.0/vault_1.15.0_linux_amd64.zip
   unzip vault_1.15.0_linux_amd64.zip
   sudo mv vault /usr/local/bin/
   vault --version
   ```

2. Start development server:
   ```bash
   vault server -dev -dev-root-token-id="dev-only-token-change-in-prod" &
   export VAULT_ADDR='http://localhost:8200'
   export VAULT_TOKEN='dev-only-token-change-in-prod'
   ```

3. Run setup script:
   ```bash
   cd /home/dev/Development/irStudy/backend
   python scripts/setup_vault.py
   ```

4. Verify secrets:
   ```bash
   vault kv list secret/
   vault kv get secret/database/postgres-irstudy-password
   ```

**Success Criteria**:
- [ ] Vault UI accessible at http://localhost:8200
- [ ] All secret paths created (15+ secrets)
- [ ] Setup script completes with 0 errors

### Task 2: Deploy Redis (1 hour)

**Steps**:
1. Pull Redis image:
   ```bash
   docker pull redis:7
   ```

2. Generate Redis password and store in Vault:
   ```bash
   REDIS_PWD=$(openssl rand -base64 32)
   vault kv put secret/ai-osce/redis-password password="$REDIS_PWD"
   ```

3. Start Redis container:
   ```bash
   docker run -d \
     --name irstudy-redis \
     -p 6380:6379 \
     -v /opt/redis/data:/data \
     redis:7 \
     --requirepass "$REDIS_PWD" \
     --maxmemory 2.5gb \
     --maxmemory-policy allkeys-lru \
     --save 60 1000 \
     --appendonly yes
   ```

4. Test connection:
   ```bash
   redis-cli -p 6380 -a "$REDIS_PWD" PING
   redis-cli -p 6380 -a "$REDIS_PWD" INFO memory
   ```

**Success Criteria**:
- [ ] Redis responds to PING with PONG
- [ ] Memory limit set to 2.5 GB
- [ ] AOF persistence enabled
- [ ] Password authentication working

### Task 3: Remove .env.dev from Git (2 hours)

**Steps**:
1. Backup current .env files:
   ```bash
   cp backend/.env.dev backend/.env.dev.backup
   cp frontend/.env.dev frontend/.env.dev.backup
   ```

2. Remove from git:
   ```bash
   git rm --cached backend/.env.dev frontend/.env.dev
   ```

3. Update .gitignore:
   ```bash
   echo "*.env" >> .gitignore
   echo ".env.*" >> .gitignore
   echo "!.env.example" >> .gitignore
   git add .gitignore
   ```

4. Create .env.example templates:
   ```bash
   # backend/.env.example content (see section 2.3)
   ```

5. Rotate credentials:
   - Generate new PostgreSQL password
   - Generate new Redis password
   - Rotate JWT secret
   - Update Vault with new values

6. Commit:
   ```bash
   git commit -m "security: remove .env files with hardcoded credentials"
   ```

**Success Criteria**:
- [ ] `.env.dev` not in git (`git ls-files | grep .env` returns only .env.example)
- [ ] All credentials rotated
- [ ] Applications still work (using Vault)

### Task 4: Fix Security Tests (2 hours)

**Issue**: 127 security tests not executable (pytest collection fails)

**Root Cause**: Missing database fixtures or environment variables

**Steps**:
1. Run pytest with verbose collection:
   ```bash
   cd /home/dev/Development/irStudy/backend
   pytest tests/test_security/ --collect-only -v 2>&1 | tee collection.log
   ```

2. Identify import errors:
   ```bash
   grep "ERROR\|ImportError" collection.log
   ```

3. Fix missing fixtures:
   - Check if `tests/test_security/conftest.py` exists
   - Add fixtures: `client`, `db_session`, `auth_headers`, `vault_client`

4. Run tests:
   ```bash
   pytest tests/test_security/test_security_comprehensive.py -v --tb=short
   ```

5. Target: 127/127 tests passing

**Success Criteria**:
- [ ] All 127 security tests executable
- [ ] 100% pass rate
- [ ] 0 hardcoded credentials detected
- [ ] HTTPS headers validated
- [ ] JWT validation tests passing

---

## 4. TESTING REQUIREMENTS

### Unit Tests
- [ ] Vault client connection test (5 tests)
- [ ] Redis client connection test (5 tests)
- [ ] Secret retrieval test (10 tests)
- [ ] Namespace isolation test (5 tests)

### Integration Tests
- [ ] Application startup with Vault (3 tests)
- [ ] Application startup with Redis (3 tests)
- [ ] Fallback behavior when Vault unavailable (2 tests)

### Security Tests
- [ ] 127 existing security tests (100% pass rate)
- [ ] No hardcoded credentials scan (1 test)
- [ ] Vault token rotation test (1 test)
- [ ] Redis authentication test (1 test)

**Total New Tests**: 36 tests

---

## 5. ACCEPTANCE CRITERIA

### Must Have (P0)
- [x] Vault server deployed and accessible
- [x] Redis server deployed and accessible
- [x] `.env.dev` removed from git
- [x] All credentials rotated
- [x] 127 security tests passing (100%)
- [x] Applications using Vault (0% fallback to `.env`)
- [x] WebSocket sessions working (Redis dependency met)

### Should Have (P1)
- [ ] Vault production mode documented
- [ ] Redis backup strategy documented
- [ ] Credential rotation automation (weekly JWT, monthly DB)

### Could Have (P2)
- [ ] Vault HA deployment guide
- [ ] Redis cluster configuration
- [ ] Monitoring dashboard (Grafana)

---

## 6. RISKS & MITIGATIONS

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Vault deployment fails | Low | HIGH | Use Docker image if binary fails |
| Redis memory exhaustion | Medium | HIGH | Configure maxmemory-policy, monitor usage |
| Credential rotation breaks apps | Medium | MEDIUM | Test in staging first, have rollback plan |
| Security tests still fail | Medium | HIGH | Fix fixtures incrementally, isolate failures |

---

## 7. DEPENDENCIES

**Blocks**:
- All Week 2-4 development (EMR, AI OSCE, Integration)
- WebSocket session creation
- Security audit completion
- Production deployment

**Blocked By**:
- None (Week 1 foundation task)

---

## 8. ROLLOUT PLAN

### Phase 1: Development Environment (Day 1)
1. Deploy Vault development mode
2. Deploy Redis Docker container
3. Run setup scripts
4. Verify connectivity

### Phase 2: Security Hardening (Day 2)
1. Remove .env.dev from git
2. Rotate all credentials
3. Run security tests
4. Verify 100% pass rate

### Phase 3: Documentation (Day 2)
1. Update README with setup instructions
2. Document Vault secret hierarchy
3. Document Redis namespace strategy
4. Create runbook for credential rotation

---

## 9. SUCCESS METRICS

**Before (Current State)**:
- Vault: Not deployed (code exists, server not running)
- Redis: Not deployed (code exists, server not running)
- Security violations: 20 (2 hardcoded API keys in .env.dev)
- Security tests: 0/127 executable (import errors)

**After (Target State)**:
- Vault: Operational, 15+ secrets stored
- Redis: Operational, 2.5 GB allocated
- Security violations: 0
- Security tests: 127/127 passing (100%)
- Applications: 100% using Vault (0% .env fallback)

---

## 10. DOCUMENTATION UPDATES

**Files to Update**:
1. `README.md` - Add Vault and Redis setup instructions
2. `docs/DEPLOYMENT.md` - Document infrastructure dependencies
3. `SHARED_INFRASTRUCTURE_SPEC.md` - Mark Week 1 as complete
4. `.env.example` - Create template for developers

---

**END OF PRD_GAP_001**
