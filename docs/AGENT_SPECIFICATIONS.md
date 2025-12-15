# Expert Agent Specifications
## Complete Catalog of 40+ Medical Education AI Agents

**Version:** 1.0.0
**Last Updated:** December 14, 2025
**Total Agents:** 46

---

## Table of Contents

1. [Project Management (1 agent)](#project-management)
2. [Software Development (12 agents)](#software-development)
3. [Data & AI Engineering (8 agents)](#data--ai-engineering)
4. [DevOps & Infrastructure (6 agents)](#devops--infrastructure)
5. [Quality Assurance (4 agents)](#quality-assurance)
6. [Medical Experts (15 agents)](#medical-experts)

---

## Project Management

### PM-001: Chief Project Manager & Architect

**Experience:** 10+ years in medical software, 5+ years as architect

**Technologies:**
- **Project Management:** Jira, Linear, Asana, GitHub Projects
- **Architecture:** C4 Model, UML, Event Storming, Domain-Driven Design
- **SDLC:** Agile/Scrum, Kanban, CI/CD
- **Documentation:** Confluence, Notion, ADR (Architecture Decision Records), RFC
- **Risk Management:** SWOT, FMEA, Dependency Analysis

**Responsibilities:**
1. Sprint Planning & Execution (2-week cycles)
2. Architecture Decision Making (ADR creation)
3. Agent Coordination & Task Delegation
4. Quality Gate Enforcement (80%+ test coverage, security scans)
5. Risk Management & Mitigation
6. SDLC Process Enforcement
7. Code Review Coordination
8. Documentation Standards
9. Stakeholder Communication
10. Technical Debt Management

**Quality Gates Enforced:**
- ✅ Code Review: At least 1 peer approval
- ✅ Unit Tests: 80%+ coverage
- ✅ Integration Tests: All critical paths tested
- ✅ Security Scan: No high/critical vulnerabilities
- ✅ Performance Test: Meets SLA targets (optional)
- ✅ Documentation: All public APIs documented

**Pros:**
- ✅ Ensures system consistency across all components
- ✅ Prevents technical debt through proactive architecture
- ✅ Coordinates complex multi-agent workflows
- ✅ Enforces quality standards (80%+ coverage, security scans)
- ✅ Long-term vision with short-term execution
- ✅ Risk identification and mitigation
- ✅ Balances process with agility

**Cons:**
- ❌ Can slow down rapid prototyping phases
- ❌ Documentation overhead in early stages
- ❌ May over-engineer simple features
- ❌ Requires balance between process and agility

**Integration Points:**
- **Coordinates:** All 45 other agents
- **Reports To:** User (product owner)
- **Artifacts:** Sprint plans, ADRs, risk registers, quality reports

---

## Software Development

### DEV-001: Senior Backend Architect (Python/FastAPI)

**Experience:** 10+ years Python, 5+ years FastAPI/async programming

**Technologies:**
- **Backend:** FastAPI 0.109+, Starlette, Pydantic 2.5+
- **Database:** SQLAlchemy 2.0 (async), Alembic migrations
- **Authentication:** OAuth2, JWT (python-jose), Argon2 hashing
- **API:** RESTful design, OpenAPI 3.1, WebSockets
- **Performance:** Async/await, connection pooling, caching strategies
- **Testing:** pytest, pytest-asyncio, TestClient
- **Monitoring:** Prometheus client, structlog

**Responsibilities:**
1. API Architecture & Design (RESTful, OpenAPI)
2. Database Schema Design (PostgreSQL + SQLAlchemy)
3. Authentication & Authorization (OAuth2 + JWT + RBAC)
4. Business Logic Implementation
5. Performance Optimization (async, caching, pooling)
6. API Documentation (auto-generated OpenAPI)
7. Error Handling & Logging
8. Security Best Practices (SQL injection, XSS prevention)
9. Integration Testing
10. Code Review for backend PRs

**Performance Targets:**
- 3,000+ requests/second (under load)
- <100ms average response time (95th percentile)
- <500ms database queries (95th percentile)

**Pros:**
- ✅ Async-first architecture (10-100x better than Django for I/O)
- ✅ Automatic OpenAPI documentation
- ✅ Type-safe with Pydantic models
- ✅ Lightweight and fast (3,000+ RPS)
- ✅ Built-in validation and serialization
- ✅ Excellent for microservices
- ✅ WebSocket support built-in

**Cons:**
- ❌ No built-in admin interface (vs Django admin)
- ❌ Smaller ecosystem than Django
- ❌ Requires understanding of async/await
- ❌ Less opinionated (more decisions needed)

**Integration Points:**
- **Works With:** DEV-004 (Database), DEV-005 (Auth), DEV-006 (API Integration)
- **Consumes:** AI-001 (RAG System), AI-002 (LLM Ops)
- **Artifacts:** API endpoints, business logic, database models

---

### DEV-002: Senior Frontend Architect (Next.js/React)

**Experience:** 10+ years JavaScript/TypeScript, 5+ years React, 3+ years Next.js

**Technologies:**
- **Framework:** Next.js 15 (App Router), React 19
- **Language:** TypeScript 5.3+
- **State Management:** TanStack Query (server state), Zustand (client state)
- **UI Components:** shadcn/ui, Radix UI primitives
- **Styling:** Tailwind CSS 3.4+, CSS Modules
- **Forms:** React Hook Form, Zod validation
- **Testing:** Vitest, Playwright (E2E), Testing Library
- **Build:** Turbopack, SWC compiler

**Responsibilities:**
1. Application Architecture (App Router, layouts, routing)
2. UI/UX Implementation (shadcn/ui components)
3. State Management (TanStack Query + Zustand)
4. Data Fetching Strategy (Server Components, streaming)
5. Performance Optimization (code splitting, lazy loading)
6. Accessibility (WCAG 2.1 AA compliance)
7. SEO Optimization (metadata, sitemaps)
8. Responsive Design (mobile-first)
9. Error Boundaries & Error Handling
10. Frontend Testing (unit, integration, E2E)

**Performance Targets:**
- <100ms Time to First Byte (TTFB)
- <1.5s Largest Contentful Paint (LCP)
- <100ms First Input Delay (FID)
- <0.1 Cumulative Layout Shift (CLS)
- Lighthouse Score: 95+ (all categories)

**Pros:**
- ✅ Server-Side Rendering for SEO
- ✅ React Server Components (zero JS for static content)
- ✅ TypeScript for type safety
- ✅ Excellent DX with Turbopack (700x faster than Webpack)
- ✅ Built-in API routes
- ✅ Image optimization automatic
- ✅ shadcn/ui = 10-100x smaller bundles than MUI

**Cons:**
- ❌ Learning curve for App Router
- ❌ Vercel-centric documentation
- ❌ React Server Components paradigm shift
- ❌ More boilerplate than Vue/Svelte

**Integration Points:**
- **Works With:** DEV-003 (UI/UX), DEV-006 (API), DEV-007 (WebSocket)
- **Consumes:** Backend APIs from DEV-001
- **Artifacts:** React components, pages, layouts, hooks

---

### DEV-003: UI/UX Specialist & Design System Engineer

**Experience:** 10+ years UI/UX design, 5+ years design systems

**Technologies:**
- **Design:** Figma, Adobe XD, Sketch
- **Components:** shadcn/ui, Radix UI, Headless UI
- **Styling:** Tailwind CSS, CSS-in-JS (Emotion)
- **Accessibility:** ARIA, axe-core, Lighthouse
- **Animation:** Framer Motion, CSS animations
- **Icons:** Lucide React, Heroicons
- **Prototyping:** Storybook, Chromatic

**Responsibilities:**
1. Design System Creation (component library)
2. UI Component Development (shadcn/ui customization)
3. Accessibility Implementation (WCAG 2.1 AA)
4. Responsive Design (mobile-first)
5. Animation & Microinteractions
6. Design Token Management (colors, spacing, typography)
7. Storybook Documentation
8. Visual Regression Testing
9. User Testing & Feedback
10. Design Handoff to Developers

**Design Principles:**
- **Medical-First:** Clean, professional, trust-building
- **Accessibility:** WCAG 2.1 AA minimum
- **Performance:** Minimal bundle size, lazy loading
- **Consistency:** Design tokens, component patterns
- **Responsive:** Mobile-first, 320px → 4K support

**Pros:**
- ✅ Creates consistent design language
- ✅ Reduces design → dev friction
- ✅ Accessibility baked in
- ✅ Reusable components across platform
- ✅ Design tokens for easy theming
- ✅ Visual regression testing prevents UI bugs

**Cons:**
- ❌ Initial setup time for design system
- ❌ Requires designer-developer collaboration
- ❌ Storybook maintenance overhead
- ❌ Can slow down rapid prototyping

**Integration Points:**
- **Works With:** DEV-002 (Frontend), QA-002 (E2E Testing)
- **Delivers:** Design system, component library, Storybook
- **Artifacts:** Figma designs, React components, design tokens

---

### DEV-004: Database Engineer (PostgreSQL/Qdrant/Neo4j)

**Experience:** 10+ years database design, 5+ years vector databases

**Technologies:**
- **Relational:** PostgreSQL 16+, SQLAlchemy 2.0 async
- **Vector:** Qdrant 1.7+ (self-hosted)
- **Graph:** Neo4j 5.16+ (community edition)
- **Caching:** Redis 7.2+
- **Migrations:** Alembic, Liquibase
- **Performance:** Query optimization, indexing, partitioning
- **Monitoring:** pg_stat_statements, EXPLAIN ANALYZE
- **Backup:** pg_dump, WAL archiving, point-in-time recovery

**Responsibilities:**
1. Database Schema Design (normalized, indexed)
2. Migration Management (Alembic scripts)
3. Query Optimization (EXPLAIN ANALYZE, indexes)
4. Vector Database Management (Qdrant collections)
5. Knowledge Graph Design (Neo4j, SNOMED CT)
6. Caching Strategy (Redis for hot data)
7. Backup & Recovery Planning
8. Performance Monitoring
9. Data Integrity (constraints, triggers)
10. Security (RLS, encryption at rest)

**Performance Targets:**
- <50ms simple queries (95th percentile)
- <500ms complex joins (95th percentile)
- <500ms vector search (Qdrant, k=10)
- <1s knowledge graph queries (Neo4j, 3-hop)

**Pros:**
- ✅ PostgreSQL = battle-tested, ACID compliant
- ✅ Qdrant = fastest open-source vector DB
- ✅ Neo4j = best graph DB for medical ontologies
- ✅ Redis = sub-millisecond caching
- ✅ SQLAlchemy 2.0 async = type-safe, performant
- ✅ Self-hosted = zero cloud costs

**Cons:**
- ❌ Three different database paradigms to manage
- ❌ Qdrant requires GPU for large datasets (optional)
- ❌ Neo4j community = single server (no clustering)
- ❌ Complex backup strategy for multi-DB setup

**Integration Points:**
- **Works With:** DEV-001 (Backend), AI-001 (RAG), AI-004 (ETL)
- **Manages:** PostgreSQL, Qdrant, Neo4j, Redis
- **Artifacts:** Schemas, migrations, indexes, backup scripts

---

### DEV-005: Authentication & Security Engineer

**Experience:** 10+ years application security, 5+ years OAuth/JWT

**Technologies:**
- **Authentication:** OAuth2, OpenID Connect, JWT (python-jose)
- **Password Hashing:** Argon2, bcrypt
- **Authorization:** RBAC, ABAC, permission systems
- **Security:** OWASP Top 10, SQL injection prevention, XSS protection
- **Encryption:** AES-256 (data at rest), TLS 1.3 (in transit)
- **MFA:** TOTP (Google Authenticator), WebAuthn (passkeys)
- **Compliance:** HIPAA 2025, GDPR, SOC 2
- **Security Scanning:** Bandit, Safety, OWASP Dependency-Check

**Responsibilities:**
1. Authentication System Design (OAuth2 + JWT)
2. Authorization & RBAC Implementation
3. Password Security (Argon2 hashing, strength validation)
4. Multi-Factor Authentication (TOTP, WebAuthn)
5. Session Management (JWT refresh tokens)
6. Security Best Practices Enforcement
7. HIPAA Compliance (2025 requirements)
8. Security Audits & Penetration Testing
9. Encryption Implementation (AES-256, TLS 1.3)
10. Security Training for Team

**Security Standards:**
- **OWASP Top 10:** All vulnerabilities mitigated
- **HIPAA 2025:** Annual audits, real-time PHI monitoring, biometric auth
- **Password Policy:** Min 12 chars, complexity rules, Argon2 hashing
- **MFA:** Required for admin accounts
- **Encryption:** AES-256 at rest, TLS 1.3 in transit
- **Session:** JWT with 15-min access token, 7-day refresh token

**Pros:**
- ✅ Prevents 99% of common vulnerabilities
- ✅ HIPAA 2025 compliant out-of-the-box
- ✅ OAuth2 = industry standard
- ✅ Argon2 = most secure password hashing (2024)
- ✅ WebAuthn = passwordless future
- ✅ Defense in depth (multiple layers)

**Cons:**
- ❌ Complex implementation (OAuth2 flows)
- ❌ MFA friction for users
- ❌ HIPAA compliance requires annual audits ($$$)
- ❌ Security vs. UX trade-offs

**Integration Points:**
- **Works With:** DEV-001 (Backend), DEV-002 (Frontend)
- **Protects:** All system components
- **Artifacts:** Auth system, RBAC, security policies, audit logs

---

### DEV-006: API Integration Specialist

**Experience:** 10+ years API design, 5+ years microservices

**Technologies:**
- **API Design:** RESTful, GraphQL, gRPC
- **Documentation:** OpenAPI 3.1, Swagger UI, Redoc
- **Testing:** Postman, Insomnia, pytest, httpx
- **Versioning:** URL versioning, header versioning
- **Rate Limiting:** Redis-based, token bucket algorithm
- **Monitoring:** Prometheus, Grafana, Sentry
- **External APIs:** PubMed API, SNOMED CT API, RxNorm API

**Responsibilities:**
1. API Design (RESTful best practices)
2. OpenAPI Specification (automatic docs)
3. API Versioning Strategy
4. Rate Limiting & Throttling
5. External API Integration (PubMed, SNOMED)
6. API Testing (unit, integration, contract)
7. Error Response Standardization
8. API Monitoring & Logging
9. API Gateway Configuration
10. Developer Documentation

**API Standards:**
- **REST:** Resources, HTTP methods, status codes
- **Versioning:** `/api/v1/`, `/api/v2/`
- **Error Format:** RFC 7807 (Problem Details)
- **Rate Limiting:** 100 req/min (free), 1000 req/min (premium)
- **Documentation:** Auto-generated OpenAPI, code examples
- **CORS:** Configured for frontend origins

**Pros:**
- ✅ RESTful = widely understood, tooling mature
- ✅ OpenAPI = automatic docs, client generation
- ✅ Versioning = backward compatibility
- ✅ Rate limiting = prevents abuse
- ✅ Monitoring = observability into API usage
- ✅ External integrations = rich medical data

**Cons:**
- ❌ REST can be chatty (multiple round-trips)
- ❌ Versioning adds complexity
- ❌ External API dependencies (uptime risk)
- ❌ Rate limits can frustrate power users

**Integration Points:**
- **Works With:** DEV-001 (Backend), DEV-002 (Frontend)
- **Integrates:** PubMed, SNOMED CT, RxNorm, other medical APIs
- **Artifacts:** API endpoints, OpenAPI specs, integration docs

---

### DEV-007: Real-time & WebSocket Engineer

**Experience:** 10+ years real-time systems, 5+ years WebSockets

**Technologies:**
- **WebSockets:** FastAPI WebSocket, Socket.IO
- **Real-time:** Server-Sent Events (SSE), Long Polling
- **Message Queue:** Redis Pub/Sub, RabbitMQ, Celery
- **Broadcasting:** Redis Streams, WebSocket rooms
- **State Management:** Connection pooling, session management
- **Testing:** pytest-asyncio, WebSocket test clients

**Responsibilities:**
1. WebSocket Implementation (real-time updates)
2. Live Session Management (AMC Clinical practice)
3. Progress Tracking (real-time quiz progress)
4. Notification System (alerts, achievements)
5. Collaborative Features (multi-user sessions)
6. Connection Management (reconnection, heartbeat)
7. Broadcasting (room-based, topic-based)
8. Performance Optimization (connection pooling)
9. Testing Real-time Features
10. Monitoring WebSocket Health

**Use Cases:**
- **Live Quizzes:** Real-time answer submission, leaderboards
- **OSCE Practice:** Live session with timer, scoring
- **Progress Tracking:** Real-time study stats, streaks
- **Notifications:** Achievement unlocks, reminders
- **Collaborative Study:** Multi-user study rooms

**Pros:**
- ✅ Real-time updates without polling
- ✅ Low latency (<100ms)
- ✅ Bidirectional communication
- ✅ FastAPI native WebSocket support
- ✅ Redis Pub/Sub for broadcasting
- ✅ Great for live features

**Cons:**
- ❌ Connection management complexity
- ❌ Scaling WebSockets requires sticky sessions
- ❌ Higher server resource usage
- ❌ Firewall/proxy issues

**Integration Points:**
- **Works With:** DEV-001 (Backend), DEV-002 (Frontend)
- **Uses:** Redis for Pub/Sub, Celery for tasks
- **Artifacts:** WebSocket endpoints, real-time features

---

### DEV-008: Mobile Developer (Flutter/React Native)

**Experience:** 10+ years mobile development, 5+ years cross-platform

**Technologies:**
- **Flutter:** Flutter 3.16+, Dart 3.2+
- **React Native:** RN 0.73+, Expo SDK 50+
- **State:** Riverpod (Flutter), Redux Toolkit (RN)
- **Local Storage:** SQLite, Hive, AsyncStorage
- **Offline:** Background sync, caching strategies
- **Testing:** Flutter test, Detox (RN)
- **Deployment:** App Store, Google Play, Fastlane

**Responsibilities:**
1. Mobile App Architecture
2. Offline-First Design (local database, sync)
3. Platform-Specific Features (notifications, biometrics)
4. Performance Optimization (60 FPS, battery)
5. App Store Submission
6. Mobile Testing (unit, widget, integration)
7. Push Notifications
8. In-App Purchases (subscriptions)
9. Analytics Integration
10. Mobile CI/CD

**Pros:**
- ✅ Cross-platform (iOS + Android from one codebase)
- ✅ Offline-first for on-the-go study
- ✅ Native performance
- ✅ Push notifications for study reminders
- ✅ Flutter = beautiful UI, fast development
- ✅ React Native = huge ecosystem

**Cons:**
- ❌ App store approval delays
- ❌ Platform-specific bugs
- ❌ Larger app size than native
- ❌ Separate codebase from web (if Flutter)

**Integration Points:**
- **Works With:** DEV-001 (Backend API), DEV-007 (WebSocket)
- **Delivers:** iOS app, Android app
- **Artifacts:** Mobile apps, app store listings

---

### DEV-009: Data Engineer (ETL/Pipelines)

**Experience:** 10+ years data engineering, 5+ years ETL/orchestration

**Technologies:**
- **ETL:** Dagster 1.5+, Airflow (alternative)
- **Data Processing:** Polars (5-10x faster than Pandas)
- **Data Quality:** Great Expectations, Pandera
- **Scheduling:** Dagster schedules, cron
- **Storage:** Parquet, CSV, JSON
- **Monitoring:** Dagster UI, Prometheus

**Responsibilities:**
1. ETL Pipeline Design (PDF → Embeddings → Qdrant)
2. Data Quality Checks (Great Expectations)
3. Incremental Updates (new textbooks added)
4. Pipeline Monitoring
5. Error Handling & Retries
6. Data Lineage Tracking
7. Performance Optimization
8. Data Validation
9. Pipeline Testing
10. Documentation

**ETL Pipelines:**
1. **Medical Textbook Pipeline:**
   - PDF Extraction → Chunking → Embeddings → Qdrant
   - Runs: On-demand (new books)
   - Duration: 4-6 hours for 20 books

2. **Knowledge Graph Pipeline:**
   - Medical entities → SNOMED mapping → Neo4j
   - Runs: Daily
   - Duration: 30-60 min

3. **Question Generation Pipeline:**
   - RAG retrieval → LLM generation → Quality check → PostgreSQL
   - Runs: On-demand
   - Duration: 5-10 sec per question

**Pros:**
- ✅ Dagster = asset-centric, great for ML
- ✅ Polars = 5-10x faster than Pandas
- ✅ Data quality checks prevent bad data
- ✅ Monitoring = visibility into pipelines
- ✅ Incremental updates = efficient
- ✅ Reproducible pipelines

**Cons:**
- ❌ Dagster learning curve
- ❌ Pipeline complexity for simple tasks
- ❌ Resource-intensive for large datasets
- ❌ Debugging distributed pipelines

**Integration Points:**
- **Works With:** AI-001 (RAG), AI-003 (Embeddings), DEV-004 (Database)
- **Produces:** Processed data, embeddings, knowledge graph
- **Artifacts:** Dagster pipelines, data quality checks

---

### DEV-010: Performance Engineer

**Experience:** 10+ years performance optimization, 5+ years profiling

**Technologies:**
- **Profiling:** py-spy, cProfile, memory_profiler
- **Load Testing:** k6, Locust, Apache Bench
- **Monitoring:** Prometheus, Grafana, Pyroscope
- **Caching:** Redis, in-memory LRU
- **Database:** Query optimization, connection pooling
- **Frontend:** Lighthouse, WebPageTest, Bundle analysis

**Responsibilities:**
1. Performance Profiling (CPU, memory, I/O)
2. Load Testing (k6 scenarios)
3. Bottleneck Identification
4. Optimization Implementation
5. Caching Strategy
6. Database Query Optimization
7. Frontend Performance (Lighthouse 95+)
8. Monitoring & Alerting
9. Performance Budgets
10. SLA Definition & Monitoring

**Performance Targets:**
- **Backend API:** 3,000+ RPS, <100ms p95
- **Database:** <50ms simple, <500ms complex
- **Vector Search:** <500ms (Qdrant, k=10)
- **LLM Generation:** 40-60 tokens/sec (7B), 5-10 (70B)
- **Frontend:** Lighthouse 95+, <1.5s LCP
- **MCQ Generation:** 5-10 sec per question
- **OSCE Scenario:** 15-30 sec per scenario

**Pros:**
- ✅ Ensures SLA compliance
- ✅ Identifies bottlenecks early
- ✅ Prevents performance regression
- ✅ Optimizes cloud costs (if scaling)
- ✅ Better user experience
- ✅ Data-driven optimization

**Cons:**
- ❌ Premature optimization risk
- ❌ Profiling overhead in production
- ❌ Can conflict with rapid development
- ❌ Diminishing returns at scale

**Integration Points:**
- **Works With:** All dev agents for optimization
- **Monitors:** All system components
- **Artifacts:** Performance reports, optimization PRs, monitoring dashboards

---

### DEV-011: Documentation Engineer

**Experience:** 10+ years technical writing, 5+ years developer docs

**Technologies:**
- **Docs:** MkDocs Material, Docusaurus, GitBook
- **API Docs:** OpenAPI/Swagger, Redoc
- **Code Docs:** Sphinx, JSDoc, TSDoc
- **Diagrams:** Mermaid, PlantUML, C4 Model
- **Versioning:** Git, semantic versioning
- **Search:** Algolia DocSearch, lunr.js

**Responsibilities:**
1. User Documentation (guides, tutorials)
2. API Documentation (OpenAPI specs)
3. Code Documentation (docstrings, comments)
4. Architecture Documentation (C4 diagrams, ADRs)
5. Onboarding Docs (new developers)
6. Changelog Maintenance
7. Video Tutorials (screencasts)
8. FAQ & Troubleshooting
9. Documentation Site Maintenance
10. Documentation Testing (broken links, outdated)

**Documentation Types:**
- **User Docs:** How to use platform, study guides
- **API Docs:** OpenAPI specs, code examples
- **Developer Docs:** Setup, architecture, contributing
- **Medical Content:** Question explanations, clinical guidelines
- **Internal Docs:** ADRs, RFCs, runbooks

**Pros:**
- ✅ Reduces support burden
- ✅ Improves developer onboarding
- ✅ API docs auto-generated (OpenAPI)
- ✅ Versioned with code (Git)
- ✅ Searchable documentation
- ✅ Better user experience

**Cons:**
- ❌ Documentation drift (outdated docs)
- ❌ Maintenance overhead
- ❌ Requires discipline to keep updated
- ❌ Time away from coding

**Integration Points:**
- **Works With:** All agents for documentation
- **Delivers:** Docs site, API specs, guides
- **Artifacts:** MkDocs site, OpenAPI specs, ADRs

---

### DEV-012: DevTools & CLI Engineer

**Experience:** 10+ years tooling, 5+ years CLI development

**Technologies:**
- **CLI:** Click, Typer, Rich (Python)
- **Build Tools:** Make, Just, Task
- **Dev Environment:** Docker Compose, Vagrant
- **Code Generation:** Cookiecutter, Yeoman
- **Linting/Formatting:** Ruff, Black, ESLint, Prettier
- **Git Hooks:** pre-commit, Husky

**Responsibilities:**
1. CLI Tool Development (`medical_ai.py`)
2. Developer Scripts (setup.sh, deploy.sh)
3. Code Generators (boilerplate, scaffolding)
4. Pre-commit Hooks (linting, formatting)
5. Build Automation (Makefiles, scripts)
6. Developer Environment Setup
7. Productivity Enhancements
8. Tool Documentation
9. Version Management
10. Debugging Tools

**Tools Created:**
- **medical_ai.py:** Main CLI (process, test, services, info)
- **setup.sh:** Automated setup script
- **dev.sh:** Development environment launcher
- **deploy.sh:** Deployment automation
- **Pre-commit hooks:** Ruff, Black, pytest, security scan

**Pros:**
- ✅ Automates repetitive tasks
- ✅ Consistent developer experience
- ✅ Faster onboarding
- ✅ Prevents common mistakes (pre-commit)
- ✅ Productivity multiplier
- ✅ Single command operations

**Cons:**
- ❌ Tool maintenance overhead
- ❌ Cross-platform compatibility (Windows)
- ❌ Learning curve for new tools
- ❌ Can become over-engineered

**Integration Points:**
- **Works With:** All agents for tooling needs
- **Delivers:** CLI tools, scripts, automation
- **Artifacts:** medical_ai.py, setup.sh, pre-commit config

---

## Data & AI Engineering

### AI-001: RAG System Architect

**Experience:** 10+ years ML/AI, 5+ years LLMs, 3+ years RAG systems

**Technologies:**
- **Embeddings:** PubMedBERT, BiomedBERT, sentence-transformers
- **Vector DB:** Qdrant 1.7+ (self-hosted)
- **Reranking:** Cohere Rerank, Cross-Encoder
- **Chunking:** Semantic chunking, sliding window
- **Retrieval:** Hybrid search (vector + keyword), MMR
- **Frameworks:** LangChain, LlamaIndex
- **Evaluation:** RAGAS, TruLens, human eval

**Responsibilities:**
1. RAG Architecture Design (retrieval + generation)
2. Embedding Model Selection (PubMedBERT)
3. Chunking Strategy (preserve medical context)
4. Retrieval Optimization (hybrid search, reranking)
5. Context Window Management (LLM limits)
6. Evaluation & Metrics (retrieval accuracy, answer quality)
7. Prompt Engineering
8. RAG Pipeline Implementation
9. Performance Tuning
10. Quality Assurance

**RAG Pipeline:**
```
User Query
    ↓
[Embed Query] (PubMedBERT)
    ↓
[Vector Search] (Qdrant, top-k=20)
    ↓
[Rerank] (Cross-Encoder, top-k=5)
    ↓
[Build Context] (5 chunks, ~2000 tokens)
    ↓
[LLM Generation] (Meditron 7B, temperature=0.3)
    ↓
[Post-processing] (citation extraction, formatting)
    ↓
Answer with Citations
```

**Performance Targets:**
- **Retrieval:** <500ms (vector search + reranking)
- **Generation:** 5-10 sec (answer with citations)
- **Accuracy:** 90%+ (human eval on medical questions)
- **Context Relevance:** 85%+ (RAGAS metric)

**Pros:**
- ✅ Grounds LLM in factual medical knowledge
- ✅ Reduces hallucinations by 90%+
- ✅ Citations for transparency
- ✅ PubMedBERT = medical-optimized
- ✅ Hybrid search = better retrieval than pure vector
- ✅ Self-hosted = zero API costs

**Cons:**
- ❌ Complex pipeline (many components)
- ❌ Retrieval quality critical (GIGO)
- ❌ Context window limits (LLM max tokens)
- ❌ Evaluation is hard (subjective medical quality)

**Integration Points:**
- **Works With:** AI-002 (LLM Ops), AI-003 (Embeddings), DEV-004 (Qdrant)
- **Consumes:** Medical textbook embeddings
- **Artifacts:** RAG pipeline, retrieval scripts, evaluation reports

---

### AI-002: LLM Operations Engineer

**Experience:** 10+ years ML ops, 5+ years LLMs, 3+ years production LLMs

**Technologies:**
- **LLM Serving:** vLLM (production), Ollama (development)
- **Local LLMs:** Meditron 7B, BioMistral 7B, Llama 3.1 70B, Mixtral 8x7B
- **Frameworks:** LangChain, LlamaIndex
- **Monitoring:** Prometheus, Grafana, LangSmith
- **GPU:** CUDA 12.0+, NVIDIA GPUs
- **Optimization:** Quantization (GGUF), Flash Attention 2
- **Testing:** Evals (medical accuracy), prompt testing

**Responsibilities:**
1. LLM Serving Infrastructure (vLLM for production)
2. Model Selection & Evaluation
3. Prompt Engineering & Templates
4. Inference Optimization (quantization, batching)
5. GPU Resource Management
6. Monitoring & Logging (LangSmith)
7. A/B Testing (different models, prompts)
8. Error Handling & Fallbacks
9. Cost Optimization (GPU utilization)
10. Model Updates & Versioning

**LLM Models:**
1. **Meditron 7B** (Yale, medical expert)
   - Use: Medical facts, clinical reasoning
   - Speed: 40-60 tokens/sec
   - Memory: 14 GB VRAM

2. **BioMistral 7B** (biomedical LLM)
   - Use: Biomedical literature, research
   - Speed: 40-60 tokens/sec
   - Memory: 14 GB VRAM

3. **Llama 3.1 70B** (Meta, best reasoning)
   - Use: Complex reasoning, question generation
   - Speed: 5-10 tokens/sec
   - Memory: 140 GB VRAM (quantized: 35 GB)

4. **Mixtral 8x7B** (Mistral AI)
   - Use: High-quality content generation
   - Speed: 30-50 tokens/sec
   - Memory: 28 GB VRAM

**Performance Targets:**
- **Throughput:** 40-60 tokens/sec (7B), 5-10 (70B)
- **Latency:** <100ms first token, <20ms/token after
- **GPU Utilization:** 80%+ (batching)
- **Availability:** 99.9% uptime

**Pros:**
- ✅ Zero API costs (local LLMs)
- ✅ Privacy (medical content stays local)
- ✅ vLLM = 10-20x faster than naive serving
- ✅ Medical-specific models (Meditron, BioMistral)
- ✅ Unlimited generation
- ✅ Full control over inference

**Cons:**
- ❌ GPU hardware cost ($2,000-$5,000)
- ❌ Electricity costs ($50-100/month)
- ❌ Model updates require redownload (10-140 GB)
- ❌ 7B models less capable than GPT-4

**Integration Points:**
- **Works With:** AI-001 (RAG), AI-003 (Multi-Agent)
- **Serves:** All agents requiring LLM inference
- **Artifacts:** vLLM server, Ollama setup, prompt templates

---

### AI-003: Multi-Agent System Architect

**Experience:** 10+ years distributed systems, 5+ years agent systems

**Technologies:**
- **Orchestration:** LangGraph, AutoGen, CrewAI
- **Communication:** Message queues (Redis, RabbitMQ)
- **State Management:** Shared state, agent memory
- **Planning:** ReAct, Plan-and-Execute, Reflection
- **Tools:** Function calling, tool use
- **Frameworks:** LangChain, Semantic Kernel

**Responsibilities:**
1. Multi-Agent Architecture Design
2. Agent Communication Protocols
3. Task Decomposition & Planning
4. Agent Orchestration (LangGraph workflows)
5. State Management & Memory
6. Tool Integration (functions, APIs)
7. Agent Coordination
8. Error Handling & Retries
9. Monitoring Agent Behavior
10. Performance Optimization

**Agent System:**
```
User Request
    ↓
[PM-001] Project Manager (coordinator)
    ↓
├─> [MED-001] Cardiology Expert → Generate MCQ
├─> [AI-001] RAG System → Retrieve context
├─> [QA-001] Medical Reviewer → Validate question
└─> [DEV-004] Database → Store question
    ↓
Aggregated Response
```

**Agent Patterns:**
1. **Sequential:** Agent A → Agent B → Agent C
2. **Parallel:** Agent A + Agent B + Agent C (simultaneously)
3. **Hierarchical:** PM delegates to specialists
4. **Collaborative:** Agents debate/vote on answer
5. **Reflective:** Agent critiques own output, retries

**Pros:**
- ✅ Breaks complex tasks into specialized subtasks
- ✅ Each agent focuses on expertise
- ✅ Parallel execution for speed
- ✅ Fault tolerance (retry failed agents)
- ✅ Scalable (add more agents)
- ✅ LangGraph = state management built-in

**Cons:**
- ❌ Complex orchestration logic
- ❌ Debugging distributed agent systems
- ❌ Agent communication overhead
- ❌ Coordination challenges

**Integration Points:**
- **Works With:** PM-001 (orchestrator), all 40+ agents
- **Uses:** LangGraph for workflows
- **Artifacts:** Agent workflows, communication protocols

---

### AI-004: ETL & Data Pipeline Engineer

**Experience:** 10+ years ETL, 5+ years big data, 3+ years ML pipelines

**Technologies:**
- **ETL:** Dagster 1.5+, Apache Airflow (alternative)
- **Data Processing:** Polars, DuckDB, Pandas
- **Validation:** Great Expectations, Pandera
- **Storage:** Parquet, Delta Lake, PostgreSQL
- **Scheduling:** Dagster schedules, cron
- **Monitoring:** Dagster UI, Prometheus

**Responsibilities:**
1. ETL Pipeline Design (PDF → Embeddings)
2. Data Quality Validation
3. Incremental Processing (new data)
4. Pipeline Orchestration (Dagster)
5. Error Handling & Recovery
6. Data Lineage Tracking
7. Performance Optimization
8. Testing Pipelines
9. Monitoring & Alerting
10. Documentation

**Key Pipelines:**
See DEV-009 for details (same agent, different categorization)

**Pros:**
- ✅ Dagster = asset-centric, great for ML
- ✅ Polars = 5-10x faster than Pandas
- ✅ Data quality = prevents bad data
- ✅ Incremental = efficient updates
- ✅ Monitoring = visibility
- ✅ Reproducible

**Cons:**
- ❌ Dagster learning curve
- ❌ Complex for simple tasks
- ❌ Resource-intensive
- ❌ Debugging distributed

**Integration Points:**
- **Works With:** AI-001 (RAG), DEV-004 (Database)
- **Produces:** Embeddings, knowledge graph
- **Artifacts:** Dagster pipelines, data quality checks

---

### AI-005: Medical NLP Specialist

**Experience:** 10+ years NLP, 5+ years medical NLP

**Technologies:**
- **Models:** BioBERT, PubMedBERT, ClinicalBERT, SciBERT
- **Libraries:** spaCy, Hugging Face Transformers, NLTK
- **Tasks:** NER (named entity recognition), relation extraction, text classification
- **Medical:** UMLS, SNOMED CT, ICD-10, MeSH
- **Frameworks:** PyTorch, TensorFlow

**Responsibilities:**
1. Medical Entity Extraction (diseases, drugs, procedures)
2. SNOMED CT Mapping
3. Clinical Text Classification
4. Medical Abbreviation Expansion
5. Negation Detection (patient does NOT have X)
6. Relation Extraction (drug-disease relationships)
7. Medical Concept Normalization
8. Custom NER Model Training
9. Evaluation & Metrics
10. Integration with Knowledge Graph

**Use Cases:**
- **Entity Extraction:** Extract diseases, drugs, symptoms from textbooks
- **SNOMED Mapping:** Map extracted entities to SNOMED CT codes
- **Question Tagging:** Automatically tag questions by specialty, topic
- **Abbreviation Expansion:** "MI" → "Myocardial Infarction"
- **Negation:** Detect "patient does NOT have diabetes"

**Pros:**
- ✅ Automates medical entity extraction
- ✅ PubMedBERT = medical-optimized
- ✅ SNOMED CT = standard medical ontology
- ✅ Enables knowledge graph construction
- ✅ Better search (entity-based)
- ✅ Question auto-tagging

**Cons:**
- ❌ Medical NER challenging (abbreviations, negation)
- ❌ SNOMED CT complex (350,000+ concepts)
- ❌ Domain adaptation required
- ❌ Evaluation needs medical experts

**Integration Points:**
- **Works With:** AI-001 (RAG), DEV-004 (Knowledge Graph)
- **Produces:** Extracted entities, SNOMED mappings
- **Artifacts:** NER models, entity databases

---

### AI-006: Computer Vision Engineer (Medical Imaging)

**Experience:** 10+ years computer vision, 5+ years medical imaging

**Technologies:**
- **Frameworks:** PyTorch, TensorFlow, OpenCV
- **Models:** ResNet, EfficientNet, Vision Transformers
- **Medical:** DICOM, NIfTI, medical image processing
- **OCR:** Tesseract, PaddleOCR, docTR
- **Visualization:** Matplotlib, Pillow, SimpleITK

**Responsibilities:**
1. Medical Image Processing (X-rays, CT, MRI)
2. OCR for Scanned Textbooks
3. Diagram Extraction (anatomy diagrams, flowcharts)
4. Image-Based Question Generation
5. Medical Image Classification
6. Figure Caption Extraction
7. Table Detection & Extraction
8. Image Preprocessing
9. Model Training & Evaluation
10. Integration with RAG System

**Use Cases:**
- **OCR:** Extract text from scanned medical textbooks
- **Diagram Extraction:** Extract anatomy diagrams for visual questions
- **Table Detection:** Detect and extract tables from PDFs
- **Image Questions:** Generate questions from medical images
- **Figure Captions:** Extract figure captions for context

**Pros:**
- ✅ Handles scanned textbooks (OCR)
- ✅ Enables visual questions (images)
- ✅ Extracts tables accurately
- ✅ Medical image understanding
- ✅ Vision-language models (Qwen2.5VL)
- ✅ Automated diagram extraction

**Cons:**
- ❌ OCR quality varies (scanned quality)
- ❌ Medical imaging requires domain knowledge
- ❌ Large models (ResNet, ViT)
- ❌ GPU-intensive training

**Integration Points:**
- **Works With:** AI-001 (RAG), AI-007 (Vision-Language)
- **Processes:** Medical images, scanned pages
- **Artifacts:** OCR models, image datasets

---

### AI-007: Vision-Language Model Engineer

**Experience:** 10+ years ML, 5+ years multimodal AI

**Technologies:**
- **Models:** Qwen2.5VL 7B, LLaVA 7B, BakLLaVA
- **Frameworks:** Hugging Face, LangChain
- **Inference:** vLLM, Ollama (multimodal support)
- **Image Processing:** PIL, OpenCV, torchvision

**Responsibilities:**
1. Vision-Language Model Selection (Qwen2.5VL)
2. Image-Based Question Generation
3. Medical Image Analysis with LLM
4. Diagram Understanding
5. Visual Reasoning
6. Prompt Engineering (image + text)
7. Model Evaluation
8. Integration with RAG
9. Performance Optimization
10. Use Case Development

**Vision-Language Pipeline:**
```
Medical Image (X-ray, CT, diagram)
    ↓
[Qwen2.5VL 7B] Vision-Language Model
    ↓
Image Understanding + LLM Reasoning
    ↓
Generated Question/Explanation
```

**Use Cases:**
- **Visual MCQs:** Generate questions from medical images
- **Diagram Analysis:** Analyze anatomy diagrams, flowcharts
- **Image Explanations:** Explain X-rays, CT scans
- **OSCE Scenarios:** Generate scenarios from clinical images
- **Visual Flashcards:** Image-based study cards

**Pros:**
- ✅ Understands images + text together
- ✅ Qwen2.5VL = open-source, powerful
- ✅ Enables visual questions (critical for AMC)
- ✅ Local inference (zero API costs)
- ✅ Medical image understanding
- ✅ Diagram analysis

**Cons:**
- ❌ Larger models (7B+ for good quality)
- ❌ Slower inference than text-only
- ❌ GPU memory (image + text)
- ❌ Hallucination risk (image misinterpretation)

**Integration Points:**
- **Works With:** AI-001 (RAG), AI-006 (Computer Vision)
- **Processes:** Medical images, diagrams
- **Artifacts:** Vision-language pipeline, visual question bank

---

### AI-008: MLOps & Model Management Engineer

**Experience:** 10+ years ML engineering, 5+ years MLOps

**Technologies:**
- **MLOps:** MLflow, DVC, Weights & Biases
- **Experiment Tracking:** MLflow, Comet.ml
- **Model Registry:** MLflow Model Registry
- **Versioning:** DVC (data), Git (code)
- **Deployment:** Docker, Kubernetes, vLLM
- **Monitoring:** Prometheus, Grafana, Evidently AI
- **Testing:** pytest, Great Expectations

**Responsibilities:**
1. Model Versioning & Registry (MLflow)
2. Experiment Tracking
3. Model Deployment (vLLM, Docker)
4. A/B Testing (model comparisons)
5. Model Monitoring (drift detection)
6. Performance Tracking
7. Reproducibility (DVC, MLflow)
8. Model Rollback
9. CI/CD for ML
10. Documentation

**MLOps Workflow:**
```
[Train Model] → [Track Experiments (MLflow)]
    ↓
[Register Model] → [MLflow Model Registry]
    ↓
[Deploy] → [vLLM + Docker]
    ↓
[Monitor] → [Prometheus + Evidently AI]
    ↓
[Drift Detected?] → [Retrain] → Loop
```

**Pros:**
- ✅ MLflow = open-source, comprehensive
- ✅ Experiment tracking = reproducibility
- ✅ Model registry = versioning
- ✅ Drift detection = quality maintenance
- ✅ A/B testing = data-driven model selection
- ✅ CI/CD for ML

**Cons:**
- ❌ MLOps complexity
- ❌ Infrastructure overhead
- ❌ Requires discipline
- ❌ Monitoring cost

**Integration Points:**
- **Works With:** All AI agents for model management
- **Manages:** All ML models (embeddings, LLMs, classifiers)
- **Artifacts:** MLflow registry, deployment configs

---

## DevOps & Infrastructure

### DEVOPS-001: Kubernetes & Cloud Architect

**Experience:** 10+ years infrastructure, 5+ years Kubernetes

**Technologies:**
- **Orchestration:** Kubernetes 1.28+, Helm, Kustomize
- **Cloud:** AWS, GCP, Azure (optional, prefer self-hosted)
- **Networking:** Istio, Linkerd, Nginx Ingress
- **Storage:** Persistent Volumes, StatefulSets
- **Scaling:** HPA (Horizontal Pod Autoscaler), VPA
- **Monitoring:** Prometheus Operator, Grafana

**Responsibilities:**
1. Kubernetes Cluster Design
2. Container Orchestration
3. Service Mesh (Istio for advanced scenarios)
4. Auto-Scaling (HPA based on CPU, memory, custom metrics)
5. Load Balancing
6. Storage Management
7. Disaster Recovery
8. Multi-Region Deployment (if scaling globally)
9. Cost Optimization
10. Security (RBAC, network policies)

**K8s Architecture:**
```
Ingress (Nginx)
    ↓
Services
├─> Backend (FastAPI) - Deployment (3 replicas)
├─> Frontend (Next.js) - Deployment (2 replicas)
├─> Qdrant - StatefulSet (persistent storage)
├─> PostgreSQL - StatefulSet
└─> Redis - Deployment
```

**Pros:**
- ✅ Auto-scaling (handle traffic spikes)
- ✅ High availability (replica sets)
- ✅ Rolling updates (zero downtime)
- ✅ Self-healing (restarts failed pods)
- ✅ Resource limits (prevent OOM)
- ✅ Production-grade orchestration

**Cons:**
- ❌ Complex for small deployments
- ❌ Steep learning curve
- ❌ Overkill for single-server setup
- ❌ Resource overhead (kubelet, etcd)

**Integration Points:**
- **Works With:** DEVOPS-002 (CI/CD), DEVOPS-003 (Monitoring)
- **Manages:** All containerized services
- **Artifacts:** Helm charts, K8s manifests, deployment configs

---

### DEVOPS-002: CI/CD Engineer

**Experience:** 10+ years automation, 5+ years CI/CD pipelines

**Technologies:**
- **CI/CD:** GitHub Actions, GitLab CI, CircleCI
- **GitOps:** ArgoCD, Flux
- **Containers:** Docker, Podman
- **Registries:** GitHub Container Registry, Docker Hub
- **Testing:** pytest, Playwright, k6
- **Security:** Trivy (container scanning), Bandit, Safety

**Responsibilities:**
1. CI/CD Pipeline Design
2. Automated Testing (unit, integration, E2E)
3. Docker Image Building
4. Container Registry Management
5. GitOps Deployment (ArgoCD)
6. Environment Management (dev, staging, prod)
7. Security Scanning (Trivy, Bandit)
8. Performance Testing (k6)
9. Rollback Strategies
10. Pipeline Monitoring

**CI/CD Pipeline:**
```
[Git Push]
    ↓
[GitHub Actions]
    ↓
├─> Lint (Ruff, ESLint)
├─> Type Check (mypy, TypeScript)
├─> Unit Tests (pytest, Vitest)
├─> Security Scan (Trivy, Bandit)
├─> Build Docker Image
├─> Integration Tests
└─> E2E Tests (Playwright)
    ↓
[Push to Registry]
    ↓
[ArgoCD Detects Change]
    ↓
[Deploy to K8s]
    ↓
[Health Checks]
    ↓
[Rollback if Failed]
```

**Quality Gates:**
- ✅ All tests pass (unit, integration, E2E)
- ✅ Test coverage ≥80%
- ✅ No high/critical security vulnerabilities
- ✅ Linting passes (Ruff, ESLint)
- ✅ Type checking passes (mypy, TypeScript)
- ✅ Build succeeds
- ✅ Health checks pass after deployment

**Pros:**
- ✅ Automated testing prevents regressions
- ✅ Fast feedback (minutes, not hours)
- ✅ GitOps = declarative, auditable
- ✅ Security scanning = early vulnerability detection
- ✅ Rollback = safety net
- ✅ Consistent deployments

**Cons:**
- ❌ Pipeline complexity
- ❌ Flaky tests can block deployments
- ❌ CI/CD costs (GitHub Actions minutes)
- ❌ Debugging pipeline failures

**Integration Points:**
- **Works With:** All dev agents for CI/CD
- **Deploys:** All services to K8s
- **Artifacts:** GitHub Actions workflows, ArgoCD apps

---

### DEVOPS-003: Monitoring & Observability Engineer

**Experience:** 10+ years monitoring, 5+ years observability

**Technologies:**
- **Metrics:** Prometheus, Grafana, VictoriaMetrics
- **Logging:** Grafana Loki, ELK Stack (Elasticsearch, Logstash, Kibana)
- **Tracing:** Jaeger, Tempo, OpenTelemetry
- **Alerting:** Alertmanager, PagerDuty, Opsgenie
- **APM:** Sentry, New Relic (optional)
- **Dashboards:** Grafana, Chronograf

**Responsibilities:**
1. Metrics Collection (Prometheus)
2. Log Aggregation (Loki)
3. Distributed Tracing (Jaeger)
4. Dashboard Creation (Grafana)
5. Alerting & On-Call (Alertmanager)
6. SLI/SLO Definition
7. Incident Response
8. Performance Monitoring
9. Cost Tracking
10. Observability Best Practices

**Monitoring Stack:**
```
[Application]
    ↓
Metrics → Prometheus → Grafana Dashboards
Logs → Loki → Grafana Explore
Traces → Jaeger → Distributed Tracing UI
    ↓
Alertmanager → PagerDuty/Email
```

**Key Metrics:**
- **Backend:** Request rate, latency (p50, p95, p99), error rate
- **Database:** Query latency, connection pool usage, slow queries
- **LLM:** Inference latency, throughput (tokens/sec), GPU utilization
- **Frontend:** Page load time, LCP, FID, CLS, JS errors
- **Infrastructure:** CPU, memory, disk, network

**SLOs (Service Level Objectives):**
- **Availability:** 99.9% uptime (43 min downtime/month)
- **Latency:** p95 < 100ms (API), p95 < 1.5s (page load)
- **Error Rate:** < 0.1% (1 error per 1000 requests)
- **Throughput:** 3,000+ RPS (backend)

**Pros:**
- ✅ Prometheus = industry standard, powerful
- ✅ Grafana = beautiful dashboards
- ✅ Loki = lightweight log aggregation
- ✅ Jaeger = distributed tracing
- ✅ Alerting = proactive issue detection
- ✅ Self-hosted = zero cost

**Cons:**
- ❌ Prometheus storage can grow large
- ❌ Alert fatigue (too many alerts)
- ❌ Dashboard maintenance
- ❌ Requires expertise to interpret metrics

**Integration Points:**
- **Works With:** All services for monitoring
- **Provides:** Dashboards, alerts, insights
- **Artifacts:** Grafana dashboards, Prometheus rules, alert configs

---

### DEVOPS-004: Security & Compliance Engineer

**Experience:** 10+ years security, 5+ years compliance (HIPAA, GDPR)

**Technologies:**
- **Security:** OWASP ZAP, Burp Suite, Nmap
- **Scanning:** Trivy (containers), Bandit (Python), npm audit (JS)
- **Secrets:** HashiCorp Vault, AWS Secrets Manager
- **Compliance:** HIPAA 2025, GDPR, SOC 2
- **Encryption:** AES-256, TLS 1.3, Let's Encrypt
- **Audit:** Auditd, logging, SIEM

**Responsibilities:**
1. Security Audits & Penetration Testing
2. Vulnerability Scanning (Trivy, Bandit, Safety)
3. Secrets Management (Vault)
4. HIPAA 2025 Compliance
5. Encryption Implementation (AES-256, TLS 1.3)
6. Security Policies & Procedures
7. Incident Response Planning
8. Access Control (RBAC, least privilege)
9. Audit Logging
10. Security Training

**Security Practices:**
- **OWASP Top 10:** All vulnerabilities mitigated
- **Secrets:** Never in code, use Vault
- **Encryption:** AES-256 at rest, TLS 1.3 in transit
- **Authentication:** OAuth2 + JWT + Argon2
- **MFA:** Required for admin accounts
- **RBAC:** Least privilege access
- **Audit Logs:** All sensitive operations logged
- **Scanning:** Daily vulnerability scans

**HIPAA 2025 Requirements:**
- ✅ Annual security audits
- ✅ Real-time PHI monitoring
- ✅ Biometric authentication (WebAuthn)
- ✅ Encryption at rest & in transit
- ✅ Audit logs (6+ years retention)
- ✅ Business Associate Agreements (BAAs)
- ✅ Breach notification (<72 hours)

**Pros:**
- ✅ Prevents security breaches
- ✅ HIPAA 2025 compliant
- ✅ Vault = secure secrets management
- ✅ Daily scans = early detection
- ✅ Audit logs = compliance + forensics
- ✅ Defense in depth

**Cons:**
- ❌ HIPAA compliance expensive (annual audits)
- ❌ Security friction vs. UX
- ❌ Vault complexity
- ❌ Compliance overhead

**Integration Points:**
- **Works With:** All agents for security review
- **Protects:** All system components
- **Artifacts:** Security policies, audit reports, vulnerability scans

---

### DEVOPS-005: Database Administrator (DBA)

**Experience:** 10+ years database administration, 5+ years PostgreSQL

**Technologies:**
- **RDBMS:** PostgreSQL 16+, pgAdmin
- **Replication:** Streaming replication, logical replication
- **Backup:** pg_dump, WAL archiving, pg_basebackup
- **Monitoring:** pg_stat_statements, pgBadger, Prometheus postgres_exporter
- **Tuning:** postgresql.conf, shared_buffers, work_mem
- **High Availability:** Patroni, repmgr, PgBouncer (connection pooling)

**Responsibilities:**
1. Database Performance Tuning
2. Query Optimization (EXPLAIN ANALYZE)
3. Index Management
4. Backup & Recovery
5. Replication Setup (primary-replica)
6. Connection Pooling (PgBouncer)
7. Monitoring & Alerting
8. Disk Space Management
9. Vacuum & Maintenance
10. Disaster Recovery Planning

**Performance Tuning:**
- **Indexes:** Proper indexes for all queries
- **Queries:** <50ms simple, <500ms complex (p95)
- **Connections:** PgBouncer for connection pooling
- **Vacuum:** Auto-vacuum configured
- **Shared Buffers:** 25% of RAM
- **Work Mem:** Tuned for query workload

**Backup Strategy:**
- **Daily:** Full backup (pg_dump)
- **Continuous:** WAL archiving (point-in-time recovery)
- **Retention:** 30 days
- **Testing:** Monthly restore drills

**Pros:**
- ✅ PostgreSQL = battle-tested, ACID
- ✅ Query optimization = fast responses
- ✅ Replication = high availability
- ✅ Backups = disaster recovery
- ✅ PgBouncer = handles 1000s of connections
- ✅ Self-hosted = zero cost

**Cons:**
- ❌ PostgreSQL tuning complex
- ❌ Backup storage costs
- ❌ Replication lag (async)
- ❌ Single point of failure (without HA)

**Integration Points:**
- **Works With:** DEV-004 (Database Engineer)
- **Manages:** PostgreSQL production instances
- **Artifacts:** Backup scripts, tuning configs, monitoring dashboards

---

### DEVOPS-006: Infrastructure as Code (IaC) Engineer

**Experience:** 10+ years infrastructure, 5+ years IaC (Terraform, Ansible)

**Technologies:**
- **IaC:** Terraform, Pulumi, OpenTofu
- **Config Management:** Ansible, Chef, Puppet
- **Cloud:** AWS, GCP, Azure (optional)
- **Versioning:** Git, Terraform Cloud
- **Testing:** Terratest, InSpec
- **Documentation:** Terraform docs, README

**Responsibilities:**
1. Infrastructure as Code (Terraform)
2. Configuration Management (Ansible)
3. Environment Provisioning (dev, staging, prod)
4. Infrastructure Versioning (Git)
5. State Management (Terraform state)
6. Drift Detection
7. Infrastructure Testing (Terratest)
8. Documentation
9. Cost Optimization
10. Disaster Recovery

**IaC Stack:**
```
Terraform (Infrastructure)
├─> AWS/GCP/Self-Hosted
│   ├─> VPC, Subnets, Security Groups
│   ├─> EC2/Compute Instances
│   ├─> Load Balancers
│   └─> Managed Databases (RDS, etc.)
    ↓
Ansible (Configuration)
├─> Install Docker
├─> Setup Kubernetes
├─> Configure Services
└─> Deploy Applications
```

**Pros:**
- ✅ Infrastructure versioned in Git
- ✅ Reproducible environments
- ✅ Terraform = declarative, idempotent
- ✅ Ansible = agentless, simple
- ✅ Drift detection = consistency
- ✅ Documentation as code

**Cons:**
- ❌ Terraform state management complexity
- ❌ Learning curve
- ❌ Terraform plan can be slow
- ❌ Debugging IaC issues

**Integration Points:**
- **Works With:** DEVOPS-001 (Kubernetes), DEVOPS-002 (CI/CD)
- **Provisions:** All infrastructure
- **Artifacts:** Terraform modules, Ansible playbooks

---

## Quality Assurance

### QA-001: Senior Medical QA Specialist

**Experience:** 10+ years QA, 5+ years medical domain

**Responsibilities:**
1. Medical Content Validation (clinical accuracy)
2. Question Quality Review (AMC standard)
3. Clinical Scenario Review (OSCE realism)
4. Medical Guideline Compliance (eTG, NSW protocols)
5. Expert Review Coordination (with real doctors)
6. Quality Metrics Tracking
7. Error Pattern Analysis
8. Content Improvement Recommendations
9. Peer Review Process
10. Documentation

**Quality Criteria:**
- **Clinical Accuracy:** 100% (verified by medical experts)
- **Guideline Compliance:** Australian standards (eTG, AMH)
- **Question Quality:** AMC exam format, difficulty calibration
- **Clarity:** Unambiguous stems, clear options
- **Distractors:** Plausible incorrect options
- **Explanations:** Evidence-based, cited

**Validation Process:**
```
[AI Generated Question]
    ↓
[QA-001 Review] (medical accuracy, format)
    ↓
[MED Expert Review] (specialist review)
    ↓
[User Testing] (med students, IMGs)
    ↓
[Feedback Loop] (improve prompt, retrain)
    ↓
[Approved Question Bank]
```

**Pros:**
- ✅ Ensures clinical accuracy
- ✅ Prevents medical misinformation
- ✅ AMC exam alignment
- ✅ Quality metrics = data-driven improvement
- ✅ Expert validation
- ✅ Continuous improvement

**Cons:**
- ❌ Requires medical expert time (expensive)
- ❌ Slow review process
- ❌ Subjective quality judgments
- ❌ Bottleneck for content generation

**Integration Points:**
- **Works With:** All MED agents, AI-001 (RAG)
- **Reviews:** All generated medical content
- **Artifacts:** Quality reports, approved question bank

---

### QA-002: Test Automation Engineer (E2E)

**Experience:** 10+ years test automation, 5+ years E2E testing

**Technologies:**
- **E2E:** Playwright, Cypress, Selenium
- **Visual:** Percy, Chromatic, BackstopJS
- **API:** pytest, Postman, Insomnia
- **Performance:** k6, Lighthouse CI
- **CI Integration:** GitHub Actions, CircleCI
- **Reporting:** Allure, Mochawesome

**Responsibilities:**
1. E2E Test Suite Development (Playwright)
2. Visual Regression Testing (Percy)
3. API Testing (pytest, httpx)
4. Performance Testing (k6, Lighthouse)
5. CI/CD Integration
6. Test Data Management
7. Flaky Test Fixing
8. Test Reporting
9. Test Coverage Analysis
10. Test Maintenance

**Test Types:**
- **E2E:** User flows (signup, login, take quiz, view results)
- **Visual:** Screenshot comparison (UI regression)
- **API:** All endpoints (CRUD, auth, search)
- **Performance:** Load testing (k6), page speed (Lighthouse)
- **Accessibility:** axe-core (WCAG 2.1 AA)

**E2E Test Examples:**
```typescript
// Playwright E2E test
test('User takes MCQ quiz and sees results', async ({ page }) => {
  await page.goto('/login');
  await page.fill('[name="email"]', 'test@example.com');
  await page.fill('[name="password"]', 'password123');
  await page.click('button[type="submit"]');

  await page.goto('/quiz/cardiology');
  await page.click('text=Start Quiz');

  // Answer 10 questions
  for (let i = 0; i < 10; i++) {
    await page.click('[data-testid="option-a"]');
    await page.click('text=Next');
  }

  await page.click('text=Submit Quiz');

  // Verify results page
  await expect(page.locator('text=Your Score')).toBeVisible();
  await expect(page.locator('[data-testid="score"]')).toHaveText(/\d+\/10/);
});
```

**Pros:**
- ✅ Playwright = fast, reliable, multi-browser
- ✅ Catches regressions before production
- ✅ Visual regression = prevents UI bugs
- ✅ API testing = backend validation
- ✅ CI integration = automated on every PR
- ✅ Test coverage metrics

**Cons:**
- ❌ Flaky tests (timing issues)
- ❌ Maintenance overhead (tests break with UI changes)
- ❌ Slow execution (E2E tests take minutes)
- ❌ Test data management complexity

**Integration Points:**
- **Works With:** DEV-002 (Frontend), DEV-001 (Backend), DEVOPS-002 (CI/CD)
- **Tests:** All user flows, APIs, UI
- **Artifacts:** Playwright tests, test reports, visual baselines

---

### QA-003: Performance & Load Testing Engineer

**Experience:** 10+ years performance testing, 5+ years load testing

**Technologies:**
- **Load Testing:** k6, Locust, JMeter, Gatling
- **Profiling:** py-spy, cProfile, memory_profiler
- **Monitoring:** Prometheus, Grafana, Pyroscope
- **APM:** New Relic, Datadog (optional)
- **Benchmarking:** Apache Bench, wrk, hey

**Responsibilities:**
1. Load Testing (k6 scenarios)
2. Stress Testing (breaking point)
3. Spike Testing (sudden traffic spike)
4. Soak Testing (sustained load)
5. Performance Profiling
6. Bottleneck Identification
7. SLA Validation
8. Performance Regression Testing
9. Capacity Planning
10. Reporting

**Load Testing Scenarios:**
```javascript
// k6 load test
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up to 100 users
    { duration: '5m', target: 100 },  // Stay at 100 for 5 min
    { duration: '2m', target: 200 },  // Ramp to 200
    { duration: '5m', target: 200 },  // Stay at 200 for 5 min
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<100'], // 95% of requests < 100ms
    http_req_failed: ['rate<0.01'],   // Error rate < 1%
  },
};

export default function () {
  let res = http.get('https://api.example.com/questions');
  check(res, {
    'status is 200': (r) => r.status === 200,
    'response time < 100ms': (r) => r.timings.duration < 100,
  });
  sleep(1);
}
```

**Performance Targets:**
- **Backend API:** 3,000+ RPS, p95 < 100ms
- **Database:** p95 < 50ms (simple), < 500ms (complex)
- **LLM:** 40-60 tokens/sec (7B), 5-10 (70B)
- **Frontend:** Lighthouse 95+, LCP < 1.5s
- **Concurrent Users:** 1,000+ simultaneous

**Pros:**
- ✅ k6 = modern, scriptable, accurate
- ✅ Validates SLA compliance
- ✅ Identifies bottlenecks before production
- ✅ Capacity planning data
- ✅ Performance regression prevention
- ✅ CI integration

**Cons:**
- ❌ Requires production-like environment
- ❌ Load testing can be expensive (resources)
- ❌ Results interpretation requires expertise
- ❌ False positives (network variance)

**Integration Points:**
- **Works With:** DEV-010 (Performance Engineer), DEVOPS-003 (Monitoring)
- **Tests:** All services under load
- **Artifacts:** k6 scripts, load test reports, performance baselines

---

### QA-004: Security Testing & Penetration Tester

**Experience:** 10+ years security testing, 5+ years penetration testing

**Technologies:**
- **Pentesting:** Burp Suite, OWASP ZAP, Metasploit
- **Scanning:** Nmap, Nessus, Nikto, Trivy
- **Fuzzing:** AFL, libFuzzer, Radamsa
- **SAST:** Bandit (Python), Semgrep, SonarQube
- **DAST:** OWASP ZAP, Burp Suite Scanner
- **Secrets:** TruffleHog, GitGuardian, git-secrets

**Responsibilities:**
1. Penetration Testing (OWASP Top 10)
2. Vulnerability Scanning (Trivy, Bandit)
3. Security Code Review
4. Secrets Detection (TruffleHog)
5. API Security Testing
6. Authentication/Authorization Testing
7. SQL Injection, XSS Testing
8. Reporting & Remediation
9. Security Training
10. Compliance Validation (HIPAA)

**Security Tests:**
- **OWASP Top 10:**
  1. Broken Access Control
  2. Cryptographic Failures
  3. Injection (SQL, NoSQL, OS)
  4. Insecure Design
  5. Security Misconfiguration
  6. Vulnerable Components
  7. Identification & Authentication Failures
  8. Software & Data Integrity Failures
  9. Security Logging & Monitoring Failures
  10. Server-Side Request Forgery (SSRF)

- **Medical-Specific:**
  - PHI data leakage
  - HIPAA compliance violations
  - Unauthorized access to medical records
  - Insecure medical image storage

**Penetration Testing Process:**
```
[Reconnaissance]
    ↓
[Scanning] (Nmap, Nessus)
    ↓
[Enumeration]
    ↓
[Exploitation] (OWASP ZAP, Burp Suite)
    ↓
[Reporting] (vulnerabilities, severity, remediation)
    ↓
[Remediation Verification]
```

**Pros:**
- ✅ Identifies real vulnerabilities
- ✅ OWASP Top 10 coverage
- ✅ Burp Suite = industry standard
- ✅ Secrets detection = prevents leaks
- ✅ Compliance validation (HIPAA)
- ✅ Security training for team

**Cons:**
- ❌ Time-consuming (manual testing)
- ❌ Requires security expertise
- ❌ False positives (scanners)
- ❌ Can disrupt services (pentesting)

**Integration Points:**
- **Works With:** DEVOPS-004 (Security Engineer), DEV-005 (Auth)
- **Tests:** All system components for vulnerabilities
- **Artifacts:** Pentest reports, vulnerability scans, remediation plans

---

## Medical Experts

### MED-001: Cardiology Expert

**Experience:** 10+ years cardiology, 5+ years medical education

**Specializations:**
- Acute Coronary Syndrome (ACS)
- Heart Failure
- Arrhythmias (AF, VT, SVT)
- Hypertension
- Valvular Heart Disease
- Cardiac Emergencies

**Responsibilities:**
1. Generate Cardiology MCQs (AMC format)
2. Review Cardiology Content (clinical accuracy)
3. Create OSCE Scenarios (chest pain, palpitations)
4. Validate Treatment Guidelines (eTG compliance)
5. Medical Literature Review (cardiology research)
6. Question Difficulty Calibration
7. Explanation Writing (evidence-based)
8. Peer Review (other cardiology content)
9. Guideline Updates (new eTG versions)
10. Student Question Answering

**Content Examples:**
- **MCQ:** 48-year-old male with chest pain, ECG shows ST elevation in V2-V4. What is the most appropriate immediate management?
- **OSCE:** Patient presents with acute shortness of breath, raised JVP, bilateral crepitations. Conduct cardiac examination.
- **Flashcard:** Acute heart failure management (LMNOP mnemonic)

**Pros:**
- ✅ Cardiology = high-yield for AMC/ICRP
- ✅ Expert validation = clinical accuracy
- ✅ Australian guidelines (eTG)
- ✅ Emergency scenarios = exam focus
- ✅ Evidence-based explanations

**Cons:**
- ❌ Requires real cardiologist time (expensive)
- ❌ Guideline updates (eTG changes)
- ❌ Specialist availability

**Integration Points:**
- **Works With:** AI-001 (RAG), QA-001 (Medical QA)
- **Produces:** Cardiology questions, scenarios, explanations
- **Artifacts:** Cardiology question bank, OSCE scenarios

---

### MED-002: Respiratory Medicine Expert

**Experience:** 10+ years respiratory medicine

**Specializations:**
- Asthma & COPD
- Pneumonia
- Pulmonary Embolism
- Tuberculosis
- Interstitial Lung Disease
- Respiratory Emergencies

**Responsibilities:**
Similar to MED-001, specialized for respiratory medicine.

**Content Examples:**
- **MCQ:** 65-year-old smoker with progressive dyspnea, spirometry shows FEV1/FVC <0.7. Diagnosis?
- **OSCE:** Assess respiratory function, perform peak flow measurement.

---

### MED-003: Gastroenterology & Hepatology Expert

**Experience:** 10+ years GI/hepatology

**Specializations:**
- Peptic Ulcer Disease
- IBD (Crohn's, Ulcerative Colitis)
- Cirrhosis & Liver Failure
- GI Bleeding
- Pancreatitis
- Hepatitis

---

### MED-004: Endocrinology & Diabetes Expert

**Experience:** 10+ years endocrinology

**Specializations:**
- Diabetes (Type 1, Type 2, Gestational)
- Thyroid Disorders
- Adrenal Disorders
- Metabolic Syndrome
- Diabetic Emergencies (DKA, HHS)

---

### MED-005: Neurology Expert

**Experience:** 10+ years neurology

**Specializations:**
- Stroke & TIA
- Seizures & Epilepsy
- Headache & Migraine
- Multiple Sclerosis
- Parkinson's Disease
- Neuromuscular Disorders

---

### MED-006: Psychiatry Expert

**Experience:** 10+ years psychiatry

**Specializations:**
- Depression & Anxiety
- Schizophrenia & Psychosis
- Bipolar Disorder
- Substance Use Disorders
- Suicide Risk Assessment
- Mental State Examination

---

### MED-007: Pediatrics Expert

**Experience:** 10+ years pediatrics

**Specializations:**
- Neonatal Care
- Pediatric Emergencies
- Childhood Infections
- Growth & Development
- Pediatric Asthma
- Immunizations

---

### MED-008: Obstetrics & Gynecology Expert

**Experience:** 10+ years O&G

**Specializations:**
- Antenatal Care
- Labor & Delivery
- Postpartum Care
- Gynecological Emergencies
- Contraception
- Menstrual Disorders

---

### MED-009: Surgery (General) Expert

**Experience:** 10+ years general surgery

**Specializations:**
- Acute Abdomen
- Appendicitis
- Hernias
- Bowel Obstruction
- Surgical Emergencies
- Post-op Complications

---

### MED-010: Orthopedics Expert

**Experience:** 10+ years orthopedics

**Specializations:**
- Fractures & Dislocations
- Trauma Management
- Arthritis
- Sports Injuries
- Musculoskeletal Examination

---

### MED-011: Emergency Medicine Expert

**Experience:** 10+ years emergency medicine

**Specializations:**
- Trauma (ATLS)
- Resuscitation (ALS, BLS)
- Toxicology
- Emergency Procedures
- Triage
- Critical Care

---

### MED-012: Infectious Diseases Expert

**Experience:** 10+ years infectious diseases

**Specializations:**
- Sepsis & Septic Shock
- Meningitis
- Pneumonia
- UTIs
- HIV/AIDS
- Tropical Diseases

---

### MED-013: Renal Medicine Expert

**Experience:** 10+ years nephrology

**Specializations:**
- Acute Kidney Injury
- Chronic Kidney Disease
- Electrolyte Disorders
- Dialysis
- Glomerulonephritis
- Renal Emergencies

---

### MED-014: Dermatology Expert

**Experience:** 10+ years dermatology

**Specializations:**
- Eczema & Psoriasis
- Skin Infections
- Skin Cancer
- Acne
- Dermatological Emergencies

---

### MED-015: General Practice Expert

**Experience:** 10+ years general practice

**Specializations:**
- Preventive Care
- Chronic Disease Management
- Screening Programs
- Mental Health in Primary Care
- Geriatrics
- Medicare/PBS (Australia)

**Integration Note:** This is the most important medical agent for ICRP/AMC as exams focus heavily on general practice scenarios.

---

## Agent Orchestration Workflows

### Example: Generate 100 Cardiology MCQs

```
[PM-001] Receives task: Generate 100 cardiology MCQs
    ↓
[PM-001] Breaks down into subtasks:
    ├─> [AI-001] RAG System: Retrieve cardiology content (20 chunks)
    ├─> [MED-001] Cardiology Expert: Generate 100 questions
    ├─> [QA-001] Medical QA: Validate clinical accuracy (all 100)
    ├─> [AI-002] LLM Ops: Run LLM generation (Llama 3.1 70B)
    └─> [DEV-004] Database: Store approved questions
    ↓
[PM-001] Aggregates results, generates report
    ↓
[User] Receives 100 validated cardiology MCQs
```

### Example: Deploy New Feature

```
[PM-001] Sprint Planning: New feature - Real-time quiz
    ↓
[PM-001] Delegates:
    ├─> [DEV-007] WebSocket Engineer: Implement real-time updates
    ├─> [DEV-001] Backend: API endpoints for quiz submission
    ├─> [DEV-002] Frontend: Real-time UI components
    ├─> [QA-002] E2E Testing: Test real-time flows
    └─> [DEVOPS-002] CI/CD: Deploy to staging
    ↓
[PM-001] Runs quality gates:
    ├─> Code review approval
    ├─> All tests pass (80%+ coverage)
    ├─> Security scan clean
    └─> Performance test (handles 1000 concurrent)
    ↓
[PM-001] Approves deployment to production
    ↓
[DEVOPS-002] ArgoCD deploys to K8s
```

---

## Summary

**Total Agents:** 46

- **Project Management:** 1 (PM-001)
- **Software Development:** 12 (DEV-001 to DEV-012)
- **Data & AI Engineering:** 8 (AI-001 to AI-008)
- **DevOps & Infrastructure:** 6 (DEVOPS-001 to DEVOPS-006)
- **Quality Assurance:** 4 (QA-001 to QA-004)
- **Medical Experts:** 15 (MED-001 to MED-015)

**Key Principles:**
1. **10+ Years Experience:** All agents have senior-level expertise
2. **Technology Choices:** Modern stack (FastAPI, Next.js, Polars, Qdrant, etc.)
3. **Pros & Cons:** Transparent about trade-offs
4. **Integration:** Clear integration points between agents
5. **Quality Gates:** PM-001 enforces 80%+ test coverage, security scans, code review
6. **Medical Accuracy:** QA-001 + MED experts validate all medical content
7. **Zero Cost:** Self-hosted infrastructure, local LLMs

**Next Steps:**
1. Implement remaining agents (MED-002 to MED-015, create Python classes)
2. Build LangGraph workflows for agent orchestration
3. Integrate agents with existing infrastructure
4. Start generating medical content with multi-agent system
5. Deploy to production with full CI/CD pipeline

---

**Last Updated:** December 14, 2025
**Version:** 1.0.0
**Status:** Complete Specifications Ready for Implementation
