# irStudy Development Plan - Week 1 Tasks

**Project**: HIPAA-Compliant Medical Education Platform
**Timeline**: 8 Weeks (Currently: Week 1 of 8)
**Updated**: 2026-02-01
**Status**: IN PROGRESS

---

## 📊 Overall Progress

- **Week 1 Goal**: Security Foundation & Infrastructure (40 hours total)
- **Target Date**: 2026-02-08 (7 days from now)
- **Team Size**: 4 developers working in parallel

**Completion**: 25% (10/40 tasks complete)

---

## 🎯 Week 1 Milestones

- [ ] Docker stack running (11 services healthy)
- [ ] Security score: 10/10 (cybersecurity framework applied)
- [ ] HIPAA compliance: 95%+
- [ ] Agent OS integrated (skills registry functional)
- [ ] API endpoints return 200 OK (even if mock data)
- [ ] Zero hardcoded credentials (all via Docker secrets)

---

## 🚨 CRITICAL PATH (P0 - Must Complete First)

### Security Foundation (Developer 1 - 10 hours)

#### Task 001: Apply Cybersecurity Framework ⏱️ 30 min
**Priority**: P0 (CRITICAL - blocks all other work)
**Status**: TODO
**Owner**: Developer 1 (DevOps/Security Lead)

**Description**:
Install and configure the cybersecurity framework from `/home/dev/Development/cyberSecurity/` to achieve 95% HIPAA compliance in 30 minutes.

**Steps**:
```bash
cd /home/dev/Development/cyberSecurity
./INSTALL_ALL_SECURITY_TOOLS.sh
./SETUP_PROJECT_HOOKS.sh irStudy
cd /home/dev/Development/irStudy
pre-commit run --all-files
```

**Acceptance Criteria**:
- [ ] 40+ security tools installed successfully
- [ ] Pre-commit hooks active in `.git/hooks/`
- [ ] First scan completed with 0 critical issues
- [ ] HIPAA compliance score: 95%+

**Validation**:
```bash
ls -la .git/hooks/pre-commit
pre-commit run --all-files | grep "Passed"
```

---

#### Task 002: Create Secrets Directory ⏱️ 15 min
**Priority**: P0 (CRITICAL - blocks Docker stack)
**Status**: ✅ DONE
**Owner**: Developer 1
**Dependencies**: None

**Description**:
Create secure secrets directory with proper permissions and generate all required secret files for Docker stack.

**Steps**:
```bash
cd /home/dev/Development/irStudy
mkdir -p secrets && chmod 700 secrets
echo "$(pwgen -s 32 1)" > secrets/db_password.txt
echo "$(pwgen -s 32 1)" > secrets/redis_password.txt
echo "$(pwgen -s 64 1)" > secrets/qdrant_api_key.txt
echo "neo4j/$(pwgen -s 32 1)" > secrets/neo4j_auth.txt
echo "sk-your-openai-key" > secrets/openai_api_key.txt
echo "sk-ant-your-anthropic-key" > secrets/anthropic_api_key.txt
echo "admin:$(pwgen -s 24 1)" > secrets/flower_auth.txt
echo "$(pwgen -s 24 1)" > secrets/grafana_password.txt
chmod 600 secrets/*.txt
```

**Acceptance Criteria**:
- [ ] 8 secret files created
- [ ] File permissions: 600 (read/write owner only)
- [ ] Directory permissions: 700
- [ ] secrets/ in .gitignore
- [ ] `git status` shows secrets/ as ignored

---

#### Task 003: Test Docker Stack ⏱️ 1 hour
**Priority**: P0 (CRITICAL)
**Status**: TODO
**Owner**: Developer 1
**Dependencies**: Task 002 (secrets)

**Description**:
Validate that all 11 Docker services start successfully with the security-hardened docker-compose.yml.

**Steps**:
```bash
cd /home/dev/Development/irStudy
docker-compose config  # Validate syntax
docker-compose up -d   # Start services
sleep 30               # Wait for initialization
docker-compose ps      # Check status
```

**Acceptance Criteria**:
- [ ] All 11 services show "Up (healthy)" status
- [ ] PostgreSQL accessible: `docker exec irstudy-postgres psql -U postgres -d irstudy_medical -c "SELECT 1;"`
- [ ] Redis accessible: `docker exec irstudy-redis redis-cli -a "$(cat secrets/redis_password.txt)" ping`
- [ ] Qdrant accessible: `curl http://localhost:6333/`
- [ ] Neo4j accessible: `curl http://localhost:7474/`
- [ ] No errors in logs: `docker-compose logs --tail=50`

---

#### Task 004: Copy arQ Production Dockerfile ⏱️ 1 hour
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 1
**Dependencies**: None

**Description**:
Copy production-grade Dockerfile from arQ project and adapt for irStudy backend.

**Steps**:
```bash
cp ~/Development/arQ/backend/Dockerfile ~/Development/irStudy/backend/Dockerfile
cd ~/Development/irStudy/backend
# Adapt: Update Python version, dependencies, health check endpoint
docker build -t irstudy-backend:test .
```

**Acceptance Criteria**:
- [ ] Dockerfile copied from arQ
- [ ] Multi-stage build preserved (base → deps → builder → runner)
- [ ] Non-root user configured (uid: 1001)
- [ ] Health check endpoint updated
- [ ] Test build succeeds: image size <500MB
- [ ] No hardcoded credentials in Dockerfile

---

#### Task 005: Create .env.template ⏱️ 1 hour
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 1
**Dependencies**: None

**Description**:
Create .env.template with all configuration variables for irStudy platform.

**Acceptance Criteria**:
- [ ] .env.template created with all variables
- [ ] JWT_SECRET placeholder (__GENERATE_ME__)
- [ ] Database connection strings templated
- [ ] API keys templated (no real values)
- [ ] .env.template committed to Git
- [ ] .env in .gitignore
- [ ] .env created locally with real values

**Template Variables**:
- DATABASE_URL, REDIS_URL, QDRANT_URL, NEO4J_URL
- JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
- OPENAI_API_KEY, ANTHROPIC_API_KEY
- OLLAMA_URL, RAG_ENABLED
- LOG_LEVEL, DEBUG

---

#### Task 006: Copy Security Workflows ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 1
**Dependencies**: Task 001 (security framework)

**Description**:
Copy GitHub Actions security workflows from ideas-aggregator project.

**Steps**:
```bash
mkdir -p ~/Development/irStudy/.github/workflows
cp ~/Development/ideas-aggregator/.github/workflows/security.yml \
   ~/Development/irStudy/.github/workflows/
# Adapt for irStudy (update paths, add Python/FastAPI-specific checks)
```

**Acceptance Criteria**:
- [ ] Security workflow copied
- [ ] Workflow adapted for Python/FastAPI
- [ ] Triggers: push to main, PR to main
- [ ] Jobs: Trivy scan, Semgrep, Bandit, GitLeaks
- [ ] Slack/email notifications configured
- [ ] Workflow tested with dummy commit

---

#### Task 007: Create Security Documentation ⏱️ 1 hour
**Priority**: P2 (Medium)
**Status**: TODO
**Owner**: Developer 1
**Dependencies**: Tasks 001-006

**Description**:
Document security procedures for team.

**Deliverables**:
- [ ] docs/SECURITY_RUNBOOK.md (incident response)
- [ ] docs/SECRETS_ROTATION.md (password rotation guide)
- [ ] docs/HIPAA_COMPLIANCE.md (compliance checklist)

---

## 💻 Backend Setup (Developer 2 - 10 hours)

#### Task 008: Setup FastAPI Project Structure ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 2 (Backend Lead)
**Dependencies**: Task 003 (Docker stack)

**Description**:
Copy FastAPI application structure from ideas-aggregator project (969 lines).

**Steps**:
```bash
mkdir -p ~/Development/irStudy/backend/src
cp -r ~/Development/ideas-aggregator/backend/main.py \
      ~/Development/irStudy/backend/src/
cp -r ~/Development/ideas-aggregator/backend/routers \
      ~/Development/irStudy/backend/src/
cp -r ~/Development/ideas-aggregator/backend/schemas \
      ~/Development/irStudy/backend/src/
```

**Acceptance Criteria**:
- [ ] FastAPI app structure copied
- [ ] main.py adapted for irStudy (rename routes, schemas)
- [ ] OpenAPI docs accessible at /docs
- [ ] Health check endpoint: GET /api/health returns 200 OK
- [ ] CORS middleware configured
- [ ] Environment variables loaded from .env

---

#### Task 009: Implement JWT Authentication ⏱️ 3 hours
**Priority**: P0 (CRITICAL)
**Status**: ✅ DONE
**Owner**: Developer 2
**Dependencies**: Task 008 (FastAPI structure)

**Description**:
Copy JWT authentication module from arQ project (entire directory).

**Steps**:
```bash
cp -r ~/Development/arQ/backend/src/modules/auth \
      ~/Development/irStudy/backend/src/modules/
# Adapt: Update database models, user schema, password hashing
```

**Acceptance Criteria**:
- [ ] Auth module copied from arQ
- [ ] Routes: POST /api/auth/register, POST /api/auth/login, POST /api/auth/refresh
- [ ] JWT token generation/validation working
- [ ] Password hashing with bcrypt
- [ ] Token expiry: 15 min access, 7 days refresh
- [ ] Integration tests: 100% pass rate

---

#### Task 010: Create Database Schema ⏱️ 3 hours
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 2
**Dependencies**: Task 003 (Docker stack)

**Description**:
Design and implement PostgreSQL database schema for irStudy.

**Tables Required**:
- users (id, email, password_hash, role, created_at, updated_at)
- mcqs (id, question, options, correct_answer, explanation, citations, topic, difficulty)
- osces (id, scenario, examination_steps, diagnosis, management, citations)
- user_progress (id, user_id, mcq_id, answered_correctly, attempts, last_attempt_at)
- study_plans (id, user_id, target_exam, plan_data, created_at)
- audit_logs (id, user_id, action, resource, timestamp, ip_address)

**Acceptance Criteria**:
- [ ] Alembic migrations setup
- [ ] Initial migration: `alembic revision --autogenerate -m "initial schema"`
- [ ] Migration applied: `alembic upgrade head`
- [ ] All tables created in PostgreSQL
- [ ] Indexes on foreign keys and frequently queried fields
- [ ] Constraints: NOT NULL, UNIQUE, FOREIGN KEY

---

#### Task 011: Scaffold API Endpoints ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 2
**Dependencies**: Tasks 009 (auth), 010 (database)

**Description**:
Create API endpoint stubs that return mock data (implement later).

**Endpoints**:
- GET /api/mcqs - List MCQs (paginated)
- GET /api/mcqs/{id} - Get single MCQ
- POST /api/mcqs/{id}/answer - Submit answer
- GET /api/osces - List OSCEs
- GET /api/osces/{id} - Get single OSCE
- GET /api/users/me - Get current user
- GET /api/users/me/progress - Get user progress
- POST /api/study-plans - Generate study plan

**Acceptance Criteria**:
- [ ] All endpoints return 200 OK with mock data
- [ ] OpenAPI schema generated automatically
- [ ] Authentication required for protected endpoints
- [ ] Input validation with Pydantic
- [ ] Error handling: 400, 401, 403, 404, 500

---

## 🎨 Frontend Setup (Developer 3 - 10 hours)

#### Task 012: Setup React + TypeScript Project ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 3 (Frontend Lead)
**Dependencies**: None

**Description**:
Initialize React 18+ project with TypeScript, Vite, and Material-UI.

**Steps**:
```bash
cd ~/Development/irStudy
npm create vite@latest frontend -- --template react-ts
cd frontend
npm install @mui/material @emotion/react @emotion/styled
npm install axios react-router-dom @tanstack/react-query
```

**Acceptance Criteria**:
- [ ] React 18+ with TypeScript
- [ ] Vite build tool configured
- [ ] Material-UI v5 installed
- [ ] React Router v6 setup
- [ ] TanStack Query (React Query) for API calls
- [ ] ESLint + Prettier configured
- [ ] Dev server running: `npm run dev`

---

#### Task 013: Copy MCQ Components from respiratory-mcq-app ⏱️ 3 hours
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 3
**Dependencies**: Task 012 (React setup)

**Description**:
Copy production-tested MCQ interface components.

**Steps**:
```bash
cp -r ~/Development/irStudy/respiratory-mcq-app/src/components/MCQ* \
      ~/Development/irStudy/frontend/src/components/
# Adapt: Update API endpoints, styling for Material-UI
```

**Acceptance Criteria**:
- [ ] MCQViewer component copied and adapted
- [ ] Answer selection UI working
- [ ] Explanation display (shown after answer)
- [ ] Citation links functional
- [ ] Progress tracking (X of Y questions answered)
- [ ] Keyboard shortcuts (1-5 for options, Enter to submit)

---

#### Task 014: Create Dashboard Wireframe ⏱️ 2 hours
**Priority**: P2 (Medium)
**Status**: TODO
**Owner**: Developer 3
**Dependencies**: Task 012 (React setup)

**Description**:
Design and implement basic dashboard layout.

**Sections**:
- Header: Logo, user menu, logout
- Sidebar: Navigation (MCQs, OSCEs, Study Plan, Progress)
- Main: Content area (changes based on route)
- Footer: Copyright, links

**Acceptance Criteria**:
- [ ] Responsive layout (mobile, tablet, desktop)
- [ ] Material-UI AppBar + Drawer
- [ ] React Router navigation working
- [ ] Dark mode toggle (Material-UI theme)
- [ ] Loading states (skeleton screens)

---

#### Task 015: Implement Authentication UI ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 3
**Dependencies**: Tasks 012 (React), 009 (backend auth)

**Description**:
Create login, registration, and password reset forms.

**Acceptance Criteria**:
- [ ] Login form: email, password, submit
- [ ] Register form: email, password, confirm password
- [ ] Form validation (client-side)
- [ ] Error messages displayed
- [ ] JWT token stored in localStorage
- [ ] Protected routes (redirect to /login if not authenticated)
- [ ] Axios interceptor for auth headers

---

#### Task 016: API Client Setup ⏱️ 1 hour
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 3
**Dependencies**: Task 012 (React setup)

**Description**:
Create centralized API client with TanStack Query.

**Acceptance Criteria**:
- [ ] Axios instance configured (base URL from .env)
- [ ] TanStack Query setup with error handling
- [ ] Custom hooks: useMCQs(), useOSCEs(), useAuth()
- [ ] Automatic retry on network errors
- [ ] Loading states handled globally
- [ ] Type-safe API responses (TypeScript interfaces)

---

## 🤖 AI/Agent OS (Developer 4 - 10 hours)

#### Task 017: Create skills-registry.json ⏱️ 2 hours
**Priority**: P1 (High)
**Status**: ✅ DONE
**Owner**: Developer 4 (AI/ML + Tauri Lead)
**Dependencies**: None

**Description**:
Define 30+ skills for Agent OS integration.

**Skills Categories**:
- Content Generation: mcq-generator, osce-generator, explanation-generator
- Quality Assurance: citation-validator, clinical-accuracy-checker, australian-standards-validator
- Study Tools: spaced-repetition-scheduler, adaptive-difficulty-adjuster, performance-analyzer
- RAG System: semantic-search, citation-retriever, knowledge-graph-query

**Acceptance Criteria**:
- [x] skills-registry.json created in project root
- [x] At least 30 skills defined (30/30 complete)
- [x] Each skill has: id, name, description, category, parameters, usage, claude_command
- [x] Valid JSON format (validated with `jq`)
- [x] Skills organized by category

---

#### Task 018: Add BaseAgent Skill Methods ⏱️ 3 hours
**Priority**: P1 (High)
**Status**: TODO
**Owner**: Developer 4
**Dependencies**: Task 017 (skills registry)

**Description**:
Extend BaseAgent class with 6 new skill methods.

**Methods**:
1. generate_mcq(topic, difficulty, count)
2. validate_citation(citation, source)
3. analyze_performance(user_id, time_period)
4. create_study_plan(user_id, target_exam, weeks)
5. query_knowledge_graph(query, max_depth)
6. semantic_search(query, collection, top_k)

**Acceptance Criteria**:
- [ ] BaseAgent class extended with 6 methods
- [ ] Each method has docstring, type hints, error handling
- [ ] Methods integrate with skills-registry.json
- [ ] Unit tests: 100% pass rate
- [ ] Integration with RAG system (Qdrant)

---

#### Task 019: Optimize RAG System ⏱️ 3 hours
**Priority**: P2 (Medium)
**Status**: TODO
**Owner**: Developer 4
**Dependencies**: Task 003 (Docker stack with Qdrant)

**Description**:
Optimize Qdrant vector database for 42,647 medical knowledge chunks.

**Optimizations**:
- Index optimization (HNSW parameters)
- Query performance tuning
- Caching strategy (Redis)
- Batch retrieval for study plans

**Acceptance Criteria**:
- [ ] Qdrant collection created: "medical_knowledge"
- [ ] 42,647 vectors indexed
- [ ] Query latency: <200ms for top-10 results
- [ ] Relevance testing: precision@10 > 0.8
- [ ] Redis caching for frequent queries
- [ ] Monitoring: query count, latency, cache hit rate

---

#### Task 020: Design Tauri App Architecture ⏱️ 2 hours
**Priority**: P2 (Medium)
**Status**: TODO
**Owner**: Developer 4
**Dependencies**: None

**Description**:
Design architecture for Tauri desktop app (implementation starts Week 2).

**Deliverables**:
- [ ] docs/TAURI_ARCHITECTURE.md (technical design)
- [ ] Tech stack decisions (Tauri 1.5+, Rust, React/Vue, SQLite)
- [ ] Offline sync protocol design (conflict resolution)
- [ ] Security requirements (exam lockdown features)
- [ ] Bundle size target: 3-5MB

---

## 📝 Week 1 Completion Checklist

### Infrastructure (Developer 1)
- [ ] Task 001: Cybersecurity framework applied ✅ 30 min
- [ ] Task 002: Secrets directory created ✅ 15 min
- [ ] Task 003: Docker stack tested ✅ 1 hour
- [ ] Task 004: arQ Dockerfile copied ✅ 1 hour
- [ ] Task 005: .env.template created ✅ 1 hour
- [ ] Task 006: Security workflows copied ✅ 2 hours
- [ ] Task 007: Security documentation ✅ 1 hour

### Backend (Developer 2)
- [ ] Task 008: FastAPI structure setup ✅ 2 hours
- [ ] Task 009: JWT authentication ✅ 3 hours
- [ ] Task 010: Database schema ✅ 3 hours
- [ ] Task 011: API endpoints scaffolded ✅ 2 hours

### Frontend (Developer 3)
- [ ] Task 012: React + TypeScript setup ✅ 2 hours
- [ ] Task 013: MCQ components copied ✅ 3 hours
- [ ] Task 014: Dashboard wireframe ✅ 2 hours
- [ ] Task 015: Authentication UI ✅ 2 hours
- [ ] Task 016: API client setup ✅ 1 hour

### AI/Agent OS (Developer 4)
- [ ] Task 017: skills-registry.json ✅ 2 hours
- [ ] Task 018: BaseAgent methods ✅ 3 hours
- [ ] Task 019: RAG optimization ✅ 3 hours
- [ ] Task 020: Tauri architecture ✅ 2 hours

---

## 🎯 Week 1 Success Criteria

Week 1 is DONE when ALL of the following are true:

### Technical Milestones
- [ ] All 20 tasks marked complete (✅)
- [ ] Docker stack: 11 services running healthy
- [ ] Security: HIPAA 95%+, 0 critical vulnerabilities
- [ ] Backend: API endpoints return 200 OK
- [ ] Frontend: Dashboard accessible, login working
- [ ] AI/Agent OS: skills-registry.json functional, RAG queries <200ms

### Quality Gates
- [ ] Tests: 80%+ coverage, 100% pass rate
- [ ] Security scans: All pass (Trivy, Semgrep, Bandit, GitLeaks)
- [ ] Linting: No errors (ESLint, Shellcheck, black, isort)
- [ ] Performance: <2s page load, <200ms API response

### Documentation
- [ ] All tasks documented in this file
- [ ] Security runbook created
- [ ] API documentation auto-generated (OpenAPI/Swagger)
- [ ] Team demo prepared (Friday Week 1)

---

## 📞 Task Assignment

| Developer | Role | Tasks | Hours |
|-----------|------|-------|-------|
| Developer 1 | DevOps/Security | 001-007 | 10 hours |
| Developer 2 | Backend Lead | 008-011 | 10 hours |
| Developer 3 | Frontend Lead | 012-016 | 10 hours |
| Developer 4 | AI/ML + Tauri | 017-020 | 10 hours |

**Total**: 40 hours (Week 1)

---

## 🆘 Blockers & Risks

### Current Blockers
- None (Week 1 just starting)

### Identified Risks
1. **Cybersecurity framework installation fails** → Mitigate: Manual installation per tool
2. **Docker services won't start** → Mitigate: Check secrets/, ports, memory limits
3. **API keys not available** → Mitigate: Use placeholders for Week 1, get real keys later

---

**Next Update**: End of Day 1 (2026-02-02)
**Weekly Review**: Friday 2026-02-08
