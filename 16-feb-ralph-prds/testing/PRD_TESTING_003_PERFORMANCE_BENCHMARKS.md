# PRD: Performance Benchmarking and Load Testing

**PRD ID**: PRD_TESTING_003_PERFORMANCE_BENCHMARKS
**Category**: Testing - Performance & Load Testing
**Priority**: P0-Critical (BLOCKS production deployment)
**Estimated Effort**: 16-20 hours
**Dependencies**: 
- PRD_BACKEND_002 (EMR Session API - auto-save performance)
- PRD_BACKEND_003 (EMR Validation API - Claude API latency)
- PRD_FRONTEND_003 (EMR Dashboard - chart render performance)
- PRD_INTEGRATION_002 (Unified Progress Tracking - cache performance)

**Status**: Ready for Implementation (FINAL PRD - 14 of 14)

---

## R - REQUEST (What & Why)

### User Story
**As a** DevOps engineer responsible for production deployment
**I want** automated performance benchmarking and load testing for the EMR Practice System
**So that** we can guarantee <200ms auto-save, <1s dashboard load, and 100+ concurrent users under production load without performance degradation

### Business Context

The EMR Practice System has **strict performance requirements** across 13 PRDs:

#### Performance Targets Extracted from All PRDs

| Category | Endpoint/Operation | Target Latency (p95) | Current Status | Blocking PRD |
|----------|-------------------|----------------------|----------------|--------------|
| **API - Session Management** | POST /emr/sessions/start | <500ms | TBD (baseline) | PRD_BACKEND_002 |
| **API - Auto-Save** | PUT /emr/sessions/{id} | <200ms | TBD | PRD_BACKEND_002 |
| **API - Submit Session** | POST /emr/sessions/{id}/submit | <1s (no validation) | TBD | PRD_BACKEND_002 |
| **API - Validation Layer 1** | Zod client-side validation | <50ms | TBD | PRD_BACKEND_003 |
| **API - Validation Layer 2** | Python rule-based validation | <1s | TBD | PRD_BACKEND_003 |
| **API - Validation Layer 3** | Claude API + RAG context | 3-5s | TBD | PRD_BACKEND_003 |
| **API - Dashboard Data** | GET /progress/dashboard/emr | <200ms (cached) | TBD | PRD_INTEGRATION_002 |
| **API - Weekly Trends** | GET /progress/weekly-trends/unified | <150ms (cached) | TBD | PRD_INTEGRATION_002 |
| **Frontend - Dashboard Load** | Initial page load (all widgets) | <1s | TBD | PRD_FRONTEND_003 |
| **Frontend - Chart Render** | Recharts ResponsiveContainer | <500ms | TBD | PRD_FRONTEND_003 |
| **Database - Complex Queries** | Specialty breakdown aggregation | <2s | TBD | PRD_INTEGRATION_002 |
| **Cache - Hit Rate** | Redis cache effectiveness | ≥95% | TBD | PRD_INTEGRATION_002 |
| **Cache - Response Time** | Cached API response | <100ms | TBD | PRD_INTEGRATION_002 |
| **Concurrent Load** | 100+ simultaneous users | No degradation | TBD | All Backend PRDs |
| **Throughput** | Session auto-save throughput | 1000 sessions/hour | TBD | PRD_BACKEND_002 |

**Problem**: Without automated performance testing, we cannot:
- **Guarantee SLAs**: No proof that <200ms auto-save works under load
- **Prevent regressions**: Code changes might break performance
- **Optimize bottlenecks**: No data on where slowdowns occur
- **Scale confidently**: Unknown breaking point (200 users? 500 users?)
- **Deploy safely**: Production issues discovered by real students = bad UX

**Solution**: Comprehensive performance benchmarking suite:
1. **API Load Testing** (Locust 2.20+): Simulate 50/100/200 concurrent users
2. **Database Query Profiling** (pgBench + EXPLAIN ANALYZE): Find slow queries
3. **Frontend Performance** (Lighthouse CI): Enforce Performance Score ≥90
4. **Claude API Caching Tests**: Validate ≥40% cache hit rate (cost savings)
5. **Regression Detection** (GitHub Actions): Block PRs that degrade performance

### Success Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **API Response Time (p95)** | All endpoints meet targets from table above | Locust load testing with 100 concurrent users |
| **Database Query Time (p95)** | Complex analytics queries <2s | pgBench + PostgreSQL EXPLAIN ANALYZE |
| **Frontend Performance Score** | Lighthouse Performance ≥90 | Lighthouse CI in GitHub Actions |
| **Cache Hit Rate** | ≥95% for dashboard APIs | Redis INFO stats during load test |
| **Claude API Cache Hit Rate** | ≥40% for repeated SOAP validations | Custom validator test with 100 similar submissions |
| **Concurrent User Capacity** | 100+ users without performance degradation (<10% latency increase) | Locust stress testing (0→200 users) |
| **Throughput** | 1000+ auto-save requests/hour sustained | Locust sustained load (5-10 min test) |
| **Performance Regression Detection** | 0 performance regressions merged to main | GitHub Actions workflow blocks PRs with >20% latency increase |

### Scope

**In Scope**:
- **API Performance Benchmarking**:
  - Locust load testing scenarios (Normal: 50 users, Peak: 100 users, Stress: 200 users, Spike: 0→200 in 30s)
  - All 15 API endpoints from PRD_BACKEND_002, PRD_BACKEND_003, PRD_INTEGRATION_002
  - Real-world user flows (start session → auto-save loop → submit → validate)
  - Performance report generation (HTML + JSON)

- **Database Query Profiling**:
  - pgBench baseline for read/write operations
  - EXPLAIN ANALYZE for complex queries (dashboard analytics, specialty breakdown, learning velocity)
  - Index effectiveness validation (ensure Index Scan, not Seq Scan)
  - Query optimization recommendations

- **Frontend Performance Testing**:
  - Lighthouse CI for dashboard pages (/, /dashboard, /emr/practice)
  - Performance budgets (FCP <1.5s, TTI <3s, CLS <0.1)
  - JavaScript bundle size monitoring (<300 KB)
  - Recharts render performance tests

- **Claude API Caching Validation**:
  - Cache hit rate measurement (100 similar SOAP notes submitted)
  - Cost savings calculation (cache hits reduce API calls)
  - Cache key collision detection (ensure unique validations aren't cached)
  - Redis memory usage monitoring

- **CI/CD Integration**:
  - GitHub Actions workflow for performance testing
  - Performance regression detection (compare against baseline)
  - Automated alerts for performance degradation
  - Performance dashboard (Grafana JSON template - optional)

**Out of Scope** (Future Iterations):
- Real-time production monitoring (Datadog, New Relic, Sentry)
- Auto-scaling configuration (Kubernetes HPA, AWS Auto Scaling)
- Global CDN performance testing (CloudFront, Cloudflare)
- Mobile device performance testing (iOS Safari, Chrome Android)
- Network throttling tests (3G/4G simulation)

---

## A - ARCHITECTURE (How)

### Technical Approach

Build a **multi-layer performance testing stack** following industry best practices:

1. **API Layer** (Locust 2.20+): Python-based load testing framework
   - **Why Locust**: Python ecosystem (matches backend), web UI for monitoring, distributed testing support
   - **Alternative rejected**: Apache JMeter (Java overhead, complex GUI), k6 (Golang, less Python integration)

2. **Database Layer** (pgBench + PostgreSQL tools): Native PostgreSQL performance testing
   - **Why pgBench**: Ships with PostgreSQL, industry standard for database benchmarking
   - **Supplemented with**: EXPLAIN ANALYZE (query plans), pg_stat_statements (query stats)

3. **Frontend Layer** (Lighthouse CI 0.13+): Automated web performance auditing
   - **Why Lighthouse**: Google-backed standard, CI integration, comprehensive metrics
   - **Alternative rejected**: WebPageTest (less automation), custom Puppeteer (reinventing wheel)

4. **Monitoring Layer** (Redis INFO, PostgreSQL stats): Native database metrics
   - **Why Native Tools**: No external dependencies, production-ready, real-time data
   - **Optional**: Grafana dashboards for visualization (not required for MVP)

### System Design

#### Performance Testing Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                      GitHub Actions CI/CD Pipeline                        │
│                                                                           │
│  Trigger: Pull Request + Daily Cron (2 AM UTC)                            │
└─────────────────────────────────┬─────────────────────────────────────────┘
                                  │
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                     Performance Test Orchestrator                         │
│                                                                           │
│  ┌─────────────────┐  ┌──────────────────┐  ┌──────────────────────┐   │
│  │ 1. Setup        │  │ 2. Baseline      │  │ 3. Run Tests         │   │
│  │ - Start services│  │ - Measure current│  │ - Locust (API)       │   │
│  │ - Seed test DB  │  │   performance    │  │ - pgBench (DB)       │   │
│  │ - Warm caches   │  │ - Save baseline  │  │ - Lighthouse (FE)    │   │
│  └─────────────────┘  └──────────────────┘  └──────────────────────┘   │
│                                                      │                    │
│  ┌─────────────────┐  ┌──────────────────┐         │                    │
│  │ 4. Analyze      │  │ 5. Report        │         │                    │
│  │ - Compare vs    │  │ - HTML report    │◄────────┘                    │
│  │   baseline      │  │ - JSON metrics   │                              │
│  │ - Detect        │  │ - GitHub comment │                              │
│  │   regressions   │  │   (if PR)        │                              │
│  └─────────────────┘  └──────────────────┘                              │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
          ┌───────────────────────┼───────────────────────┐
          ▼                       ▼                       ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────────┐
│  Locust          │  │  pgBench         │  │  Lighthouse CI       │
│  Load Testing    │  │  DB Profiling    │  │  Frontend Perf       │
│                  │  │                  │  │                      │
│ Target:          │  │ Target:          │  │ Target:              │
│ - API endpoints  │  │ - Complex queries│  │ - Dashboard pages    │
│                  │  │                  │  │                      │
│ Users:           │  │ Metrics:         │  │ Budgets:             │
│ - 50 (normal)    │  │ - TPS            │  │ - FCP <1.5s          │
│ - 100 (peak)     │  │ - Query latency  │  │ - TTI <3s            │
│ - 200 (stress)   │  │ - Index usage    │  │ - JS <300KB          │
│                  │  │                  │  │ - Performance ≥90    │
│ Output:          │  │ Output:          │  │                      │
│ - HTML report    │  │ - Query plans    │  │ Output:              │
│ - stats.json     │  │ - Slow queries   │  │ - JSON report        │
└──────────────────┘  └──────────────────┘  └──────────────────────┘
          │                       │                       │
          └───────────────────────┼───────────────────────┘
                                  ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                        Performance Report Dashboard                       │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  PERFORMANCE TEST RESULTS - PR #123                              │    │
│  │                                                                  │    │
│  │  ✅ PASSED - All performance targets met                         │    │
│  │                                                                  │    │
│  │  API Endpoints (Locust - 100 concurrent users):                 │    │
│  │    ✅ POST /emr/sessions/start          178ms (target: <500ms)   │    │
│  │    ✅ PUT /emr/sessions/{id}            142ms (target: <200ms)   │    │
│  │    ⚠️  POST /emr/validation/soap        4.2s  (target: 3-5s)     │    │
│  │    ✅ GET /progress/dashboard/emr       87ms  (target: <200ms)   │    │
│  │                                                                  │    │
│  │  Database Queries (pgBench):                                     │    │
│  │    ✅ Specialty breakdown aggregation   1.8s  (target: <2s)      │    │
│  │    ✅ Weekly trends calculation         1.2s  (target: <2s)      │    │
│  │    ✅ All queries use Index Scan (no Seq Scan)                   │    │
│  │                                                                  │    │
│  │  Frontend Performance (Lighthouse CI):                           │    │
│  │    ✅ Performance Score                 92    (target: ≥90)      │    │
│  │    ✅ First Contentful Paint            1.2s  (target: <1.5s)    │    │
│  │    ✅ Time to Interactive               2.7s  (target: <3s)      │    │
│  │    ✅ JavaScript Bundle Size            287KB (target: <300KB)   │    │
│  │                                                                  │    │
│  │  Cache Performance:                                              │    │
│  │    ✅ Redis Cache Hit Rate              96.2% (target: ≥95%)     │    │
│  │    ✅ Claude API Cache Hit Rate         42.5% (target: ≥40%)     │    │
│  │                                                                  │    │
│  │  Load Testing:                                                   │    │
│  │    ✅ 100 concurrent users              Passed (no degradation)  │    │
│  │    ✅ Throughput (auto-save)            1247 requests/hour       │    │
│  │                                                                  │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└───────────────────────────────────────────────────────────────────────────┘
```

#### Component Diagram: Locust Load Testing

```
┌───────────────────────────────────────────────────────────────────────────┐
│                         Locust Load Testing System                        │
└───────────────────────────────────────────────────────────────────────────┘

ARCHITECTURE:
  │
  ├─► LOCUST MASTER (Orchestrator)
  │   - Web UI (http://localhost:8089)
  │   - User configuration (50/100/200 users)
  │   - Results aggregation
  │   - Report generation
  │
  ├─► LOCUST WORKERS (Simulated Users)
  │   - User behavior: EMRUser class
  │   - Tasks weighted by frequency:
  │     * @task(10): autosave_session (most common)
  │     * @task(5):  start_new_session
  │     * @task(1):  submit_session_with_validation
  │   - Authentication: JWT token per user
  │   - Think time: between(1, 3) seconds
  │
  ├─► TARGET SYSTEM (Backend API)
  │   - FastAPI app (http://localhost:8001)
  │   - PostgreSQL database (localhost:5432)
  │   - Redis cache (localhost:6379)
  │
  └─► MONITORING
      - Response time percentiles (p50, p95, p99)
      - Request rate (RPS)
      - Failure rate (errors/total)
      - Resource usage (CPU, RAM, DB connections)

USER FLOW SIMULATION:
  1. User starts (on_start):
     - Login: POST /api/v1/auth/login → Get JWT token
     - Save token for subsequent requests

  2. Task loop (weighted randomization):
     - 10/16 chance: Auto-save session (PUT /emr/sessions/{id})
     - 5/16 chance:  Start new session (POST /emr/sessions/start)
     - 1/16 chance:  Submit session (POST /emr/sessions/{id}/submit)

  3. Wait time: Random 1-3 seconds between tasks (realistic typing pace)

  4. Response validation:
     - Mark as success if latency < target
     - Mark as failure if latency > target OR HTTP 500

LOAD TEST SCENARIOS:
  ┌────────────────────────────────────────────────────────────────┐
  │ Scenario 1: Normal Load (50 concurrent users)                  │
  │ - Duration: 5 minutes                                          │
  │ - Spawn rate: 5 users/second (0→50 in 10 seconds)             │
  │ - Expected: All endpoints meet latency targets                │
  │ - Purpose: Baseline performance measurement                   │
  └────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────┐
  │ Scenario 2: Peak Load (100 concurrent users)                   │
  │ - Duration: 10 minutes                                         │
  │ - Spawn rate: 10 users/second (0→100 in 10 seconds)           │
  │ - Expected: All endpoints still meet targets                  │
  │ - Purpose: Validate production capacity                       │
  │ - Success Criteria: <10% latency increase vs Scenario 1       │
  └────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────┐
  │ Scenario 3: Stress Test (200 concurrent users)                 │
  │ - Duration: 5 minutes                                          │
  │ - Spawn rate: 20 users/second (0→200 in 10 seconds)           │
  │ - Expected: Find breaking point (when latency >20% increase)  │
  │ - Purpose: Determine system limits                            │
  │ - Acceptance: System degrades gracefully (no 500 errors)      │
  └────────────────────────────────────────────────────────────────┘

  ┌────────────────────────────────────────────────────────────────┐
  │ Scenario 4: Spike Test (0→200→50→200 users)                    │
  │ - Duration: 10 minutes                                         │
  │ - Pattern:                                                     │
  │   * 0-30s:   0→200 users (rapid spike)                         │
  │   * 30s-5m:  200 users sustained                               │
  │   * 5m-6m:   200→50 users (scale down)                         │
  │   * 6m-7m:   50 users sustained                                │
  │   * 7m-8m:   50→200 users (second spike)                       │
  │   * 8m-10m:  200 users sustained                               │
  │ - Expected: System handles rapid scaling                       │
  │ - Purpose: Test auto-scaling triggers (if deployed to cloud)  │
  └────────────────────────────────────────────────────────────────┘
```

#### Data Flow: API Performance Test

```
1. GitHub Actions triggers performance test workflow
   ↓
2. Start services (docker-compose up -d):
   - PostgreSQL (port 5432)
   - Redis (port 6379)
   - Backend API (port 8001)
   ↓
3. Seed test database:
   - Create 100 test users (load_test_user_001@test.com ... load_test_user_100@test.com)
   - Create 500 mock patients (diverse specialties, complexities)
   - Create 200 pre-existing sessions (to test GET /sessions list endpoint)
   ↓
4. Warm caches (pre-populate Redis):
   - Call dashboard endpoints for each test user
   - Ensures cache hit rate test starts with populated cache
   ↓
5. Run Locust load test (Scenario 2: Peak Load - 100 users):
   - Command: locust -f tests/performance/test_api_benchmarks.py \
                     --users 100 --spawn-rate 10 --run-time 10m \
                     --headless --html performance_report.html \
                     --json performance_stats.json
   ↓
6. Locust spawns 100 EMRUser instances:
   - Each user:
     a. Logs in (POST /auth/login) → Gets JWT token
     b. Starts session (POST /emr/sessions/start)
     c. Enters auto-save loop (10x PUT /emr/sessions/{id} with 30s intervals)
     d. Submits session (POST /emr/sessions/{id}/submit)
     e. Triggers validation (POST /emr/validation/soap)
   ↓
7. Locust collects metrics:
   - Request count (total, success, failure)
   - Response times (min, median, p95, p99, max)
   - Request rate (RPS)
   - Failure rate (errors/total)
   ↓
8. Performance analyzer compares results vs baseline:
   - Load baseline.json (from last successful main branch build)
   - Compare each endpoint:
     * Current p95 vs Baseline p95
     * If current > baseline * 1.20 → REGRESSION DETECTED
   ↓
9. Generate performance report:
   - HTML report (visual charts, tables)
   - JSON stats (machine-readable for CI/CD)
   - GitHub PR comment (if triggered by PR):
     ```
     ## 🚀 Performance Test Results

     ✅ PASSED - All endpoints within performance targets

     ### API Latency (p95 - 100 concurrent users)
     | Endpoint | Current | Target | Status |
     |----------|---------|--------|--------|
     | POST /emr/sessions/start | 178ms | <500ms | ✅ PASS |
     | PUT /emr/sessions/{id} | 142ms | <200ms | ✅ PASS |
     | POST /emr/validation/soap | 4.2s | 3-5s | ✅ PASS |

     ### Regression Check
     ✅ No performance regressions detected (vs baseline from main@a1b2c3d)

     [View Full Report](https://github.com/actions/runs/123456/artifacts/performance_report.html)
     ```
   ↓
10. CI/CD decision:
    - If PASSED: Allow PR merge
    - If REGRESSION DETECTED: Block PR merge, require fixes
    - If CRITICAL FAILURE (500 errors): Block PR merge, alert team
```

#### Database Query Performance Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                    Database Performance Testing System                     │
└───────────────────────────────────────────────────────────────────────────┘

LAYERS:
  │
  ├─► QUERY PROFILING (EXPLAIN ANALYZE)
  │   - Purpose: Understand query execution plans
  │   - Validates: Indexes are used (Index Scan vs Seq Scan)
  │   - Detects: Missing indexes, inefficient joins
  │
  ├─► LOAD TESTING (pgBench)
  │   - Purpose: Measure database throughput (TPS)
  │   - Tests: Read-heavy, write-heavy, mixed workloads
  │   - Baselines: Simple SELECT, complex JOIN, UPDATE, INSERT
  │
  └─► SLOW QUERY LOG ANALYSIS (pg_stat_statements)
      - Purpose: Identify real-world slow queries
      - Metrics: Avg time, total time, calls, I/O time
      - Threshold: Flag queries >500ms

QUERY TEST CASES:

  ┌─────────────────────────────────────────────────────────────────┐
  │ Test 1: Dashboard Analytics Query (Complex Aggregation)        │
  │                                                                 │
  │ SQL:                                                            │
  │   SELECT                                                        │
  │     u.id,                                                       │
  │     COUNT(DISTINCT ms.id) FILTER (                             │
  │       WHERE ms.submitted_at >= NOW() - INTERVAL '7 days'       │
  │     ) as mcq_last_7d,                                          │
  │     COUNT(DISTINCT os.id) FILTER (                             │
  │       WHERE os.submitted_at >= NOW() - INTERVAL '7 days'       │
  │     ) as osce_last_7d,                                         │
  │     COUNT(DISTINCT es.id) FILTER (                             │
  │       WHERE es.submitted_at >= NOW() - INTERVAL '7 days'       │
  │     ) as emr_last_7d,                                          │
  │     AVG(ev.total_amc_score) as avg_emr_score                   │
  │   FROM users u                                                  │
  │   LEFT JOIN mcq_sessions ms ON u.id = ms.user_id               │
  │   LEFT JOIN osce_sessions os ON u.id = os.user_id              │
  │   LEFT JOIN emr_sessions es ON u.id = es.user_id               │
  │   LEFT JOIN emr_validations ev ON es.id = ev.session_id        │
  │   WHERE u.id = $1                                               │
  │   GROUP BY u.id;                                                │
  │                                                                 │
  │ Target: <2s                                                     │
  │ Test Scale: 10,000 users, 50,000 sessions                      │
  │ Expected Plan: Index Scan on users_pkey, Index Scan on         │
  │                session indexes (no Seq Scan)                   │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ Test 2: Specialty Breakdown Query (GROUP BY Aggregation)       │
  │                                                                 │
  │ SQL:                                                            │
  │   SELECT                                                        │
  │     mp.specialty,                                               │
  │     COUNT(es.id) as session_count,                             │
  │     AVG(ev.total_amc_score) as avg_score                       │
  │   FROM emr_sessions es                                          │
  │   JOIN mock_patients mp ON es.patient_id = mp.id               │
  │   LEFT JOIN emr_validations ev ON es.id = ev.session_id        │
  │   WHERE es.user_id = $1                                         │
  │     AND es.submitted_at >= NOW() - INTERVAL '30 days'          │
  │   GROUP BY mp.specialty                                         │
  │   ORDER BY session_count DESC;                                  │
  │                                                                 │
  │ Target: <1s                                                     │
  │ Test Scale: User with 200 EMR sessions across 15 specialties   │
  │ Expected Plan: Index Scan on emr_sessions.user_id,             │
  │                Nested Loop Join with mock_patients             │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ Test 3: Learning Velocity Calculation (Window Functions)       │
  │                                                                 │
  │ SQL:                                                            │
  │   WITH weekly_scores AS (                                       │
  │     SELECT                                                      │
  │       DATE_TRUNC('week', es.submitted_at) as week_start,       │
  │       AVG(ev.total_amc_score) as avg_score,                    │
  │       COUNT(es.id) as session_count                            │
  │     FROM emr_sessions es                                        │
  │     JOIN emr_validations ev ON es.id = ev.session_id           │
  │     WHERE es.user_id = $1                                       │
  │       AND es.submitted_at >= NOW() - INTERVAL '12 weeks'       │
  │     GROUP BY week_start                                         │
  │   )                                                             │
  │   SELECT                                                        │
  │     week_start,                                                 │
  │     avg_score,                                                  │
  │     session_count,                                              │
  │     avg_score - LAG(avg_score) OVER (                          │
  │       ORDER BY week_start                                       │
  │     ) as week_improvement                                       │
  │   FROM weekly_scores                                            │
  │   ORDER BY week_start DESC;                                     │
  │                                                                 │
  │ Target: <1.5s                                                   │
  │ Test Scale: 12 weeks of data, 300 EMR sessions                 │
  │ Expected Plan: Index Scan on emr_sessions.user_id +            │
  │                submitted_at, WindowAgg for LAG function        │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ Test 4: Auto-Save UPDATE (Single Row Update)                   │
  │                                                                 │
  │ SQL:                                                            │
  │   UPDATE emr_sessions                                           │
  │   SET                                                           │
  │     session_data = JSONB_SET(                                   │
  │       session_data,                                             │
  │       '{draft_subjective}',                                     │
  │       '"Patient presents with chest pain..."'                  │
  │     ),                                                          │
  │     auto_saved_at = NOW(),                                      │
  │     updated_at = NOW()                                          │
  │   WHERE id = $1;                                                │
  │                                                                 │
  │ Target: <50ms (critical for <200ms API response)               │
  │ Test Scale: 1,000,000 sessions in table (test with large data) │
  │ Expected Plan: Index Scan on emr_sessions_pkey (primary key)   │
  └─────────────────────────────────────────────────────────────────┘

PGBENCH CONFIGURATION:
  # Custom pgBench script for EMR-specific workload

  # File: tests/performance/pgbench_emr_workload.sql
  \set user_id random(1, 10000)
  \set session_id random(1, 50000)
  \set patient_id random(1, 500)

  BEGIN;

  -- Simulate auto-save (70% of operations)
  \if :random_int < 70
    UPDATE emr_sessions
    SET session_data = '{"draft_subjective": "Updated text"}',
        auto_saved_at = NOW()
    WHERE id = :session_id;
  \endif

  -- Simulate session start (20% of operations)
  \if :random_int >= 70 AND :random_int < 90
    INSERT INTO emr_sessions (user_id, patient_id, emr_system, is_active)
    VALUES (:user_id, :patient_id, 'epic', true);
  \endif

  -- Simulate dashboard query (10% of operations)
  \if :random_int >= 90
    SELECT COUNT(*) FROM emr_sessions WHERE user_id = :user_id;
  \endif

  COMMIT;

  # Run: pgbench -c 50 -j 4 -T 60 -f pgbench_emr_workload.sql -r emr_test_db
  # -c 50: 50 concurrent clients
  # -j 4: 4 worker threads
  # -T 60: Run for 60 seconds
  # -r: Report latencies per statement

  # Expected Output:
  #   transaction type: tests/performance/pgbench_emr_workload.sql
  #   scaling factor: 1
  #   query mode: simple
  #   number of clients: 50
  #   number of threads: 4
  #   duration: 60 s
  #   number of transactions actually processed: 120000
  #   latency average = 25.000 ms  (target: <50ms)
  #   tps = 2000.000000 (including connections establishing)
```

#### Frontend Performance Testing Architecture

```
┌───────────────────────────────────────────────────────────────────────────┐
│                   Lighthouse CI Performance Testing                       │
└───────────────────────────────────────────────────────────────────────────┘

WORKFLOW:
  1. Build frontend (npm run build)
  2. Serve production build (npm run preview on port 5173)
  3. Run Lighthouse CI on key pages:
     - /                      (Landing page)
     - /dashboard             (Main dashboard with charts)
     - /emr/practice          (EMR practice interface)
     - /mcq/practice          (MCQ practice interface)
  4. Compare metrics against budgets
  5. Generate report (JSON + HTML)

LIGHTHOUSE BUDGETS:

  ┌─────────────────────────────────────────────────────────────────┐
  │ Performance Metrics Budget                                      │
  │                                                                 │
  │ ✅ Performance Score:          ≥90 (0-100 scale)                │
  │ ✅ First Contentful Paint:     <1.5s                            │
  │ ✅ Speed Index:                 <2.5s                            │
  │ ✅ Largest Contentful Paint:   <2.5s                            │
  │ ✅ Time to Interactive:        <3.0s                            │
  │ ✅ Total Blocking Time:        <300ms                           │
  │ ✅ Cumulative Layout Shift:    <0.1                             │
  └─────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────┐
  │ Resource Size Budget                                            │
  │                                                                 │
  │ ✅ Total JavaScript:           <300 KB (gzipped)                │
  │ ✅ Main bundle (vendors~main): <200 KB (React, MUI, Recharts)  │
  │ ✅ Route chunk (dashboard):    <50 KB                           │
  │ ✅ Total CSS:                  <50 KB (MUI styles)              │
  │ ✅ Total Images:               <100 KB (optimized PNGs/SVGs)    │
  │ ✅ Total Fonts:                <100 KB (Roboto woff2)           │
  └─────────────────────────────────────────────────────────────────┘

LIGHTHOUSE CI CONFIGURATION:

  # File: .github/workflows/lighthouse-ci.yml
  name: Lighthouse CI
  on:
    pull_request:
      paths:
        - 'frontend/**'
        - '.github/workflows/lighthouse-ci.yml'
    schedule:
      - cron: '0 2 * * *'  # Daily at 2 AM UTC

  jobs:
    lighthouse:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        - uses: actions/setup-node@v4
          with:
            node-version: '20'
            cache: 'npm'
            cache-dependency-path: frontend/package-lock.json

        - name: Install dependencies
          working-directory: frontend
          run: npm ci

        - name: Build frontend
          working-directory: frontend
          run: npm run build

        - name: Serve production build
          working-directory: frontend
          run: npm run preview &
          # Wait for server to start
          shell: bash
          timeout-minutes: 2

        - name: Wait for server
          run: |
            npx wait-on http://localhost:5173 --timeout 60000

        - name: Run Lighthouse CI
          uses: treosh/lighthouse-ci-action@v11
          with:
            urls: |
              http://localhost:5173
              http://localhost:5173/dashboard
              http://localhost:5173/emr/practice
            budgetPath: ./frontend/lighthouse-budget.json
            temporaryPublicStorage: true
            uploadArtifacts: true
            runs: 3  # Run 3 times, take median

        - name: Comment PR with results
          if: github.event_name == 'pull_request'
          uses: actions/github-script@v7
          with:
            script: |
              const fs = require('fs');
              const results = JSON.parse(
                fs.readFileSync('.lighthouseci/manifest.json', 'utf8')
              );
              // Parse results and post comment (implementation omitted for brevity)

  # File: frontend/lighthouse-budget.json
  [
    {
      "path": "/*",
      "resourceSizes": [
        {
          "resourceType": "script",
          "budget": 300
        },
        {
          "resourceType": "stylesheet",
          "budget": 50
        },
        {
          "resourceType": "image",
          "budget": 100
        },
        {
          "resourceType": "font",
          "budget": 100
        },
        {
          "resourceType": "document",
          "budget": 30
        },
        {
          "resourceType": "total",
          "budget": 600
        }
      ],
      "timings": [
        {
          "metric": "first-contentful-paint",
          "budget": 1500
        },
        {
          "metric": "interactive",
          "budget": 3000
        },
        {
          "metric": "speed-index",
          "budget": 2500
        },
        {
          "metric": "largest-contentful-paint",
          "budget": 2500
        },
        {
          "metric": "cumulative-layout-shift",
          "budget": 0.1
        },
        {
          "metric": "total-blocking-time",
          "budget": 300
        }
      ]
    }
  ]

RECHARTS RENDER PERFORMANCE TEST:

  # File: frontend/src/components/dashboard/__tests__/PerformanceChart.perf.test.tsx

  import { render } from '@testing-library/react';
  import { performance } from 'perf_hooks';
  import PerformanceChart from '../PerformanceChart';

  describe('PerformanceChart Render Performance', () => {
    it('renders large dataset in <500ms', () => {
      // Generate 4 weeks of data (28 data points)
      const largeDataset = Array.from({ length: 28 }, (_, i) => ({
        week_start: `2026-W${i + 1}`,
        mcq_accuracy: Math.random() * 100,
        osce_avg_score: Math.random() * 15,
        emr_avg_score: Math.random() * 15,
      }));

      const startTime = performance.now();

      render(
        <PerformanceChart
          data={largeDataset}
          loading={false}
        />
      );

      const endTime = performance.now();
      const renderTime = endTime - startTime;

      expect(renderTime).toBeLessThan(500);  // <500ms target
    });

    it('re-renders on data change in <200ms', () => {
      const { rerender } = render(
        <PerformanceChart data={initialData} loading={false} />
      );

      const startTime = performance.now();

      rerender(
        <PerformanceChart data={updatedData} loading={false} />
      );

      const endTime = performance.now();
      const rerenderTime = endTime - startTime;

      expect(rerenderTime).toBeLessThan(200);  // <200ms target
    });
  });
```

#### Claude API Caching Performance Test

```
┌───────────────────────────────────────────────────────────────────────────┐
│                 Claude API Cache Effectiveness Testing                    │
└───────────────────────────────────────────────────────────────────────────┘

PURPOSE:
  - Validate Redis caching reduces Claude API calls (cost savings)
  - Measure cache hit rate (target: ≥40% for repeated validations)
  - Ensure cache keys prevent collisions (unique validations aren't cached)

TEST SCENARIO:
  100 students submit SOAP notes for the same patient scenario
  (simulates classroom setting where all students practice same case)

EXPECTED BEHAVIOR:
  - First submission:  CACHE MISS → Claude API call → Store in Redis
  - Submissions 2-100: CACHE HIT → Retrieve from Redis (no API call)
  - Cache hit rate:    ≥40% (99/100 = 99% in ideal case, but allow variance)

CACHE KEY STRATEGY:
  Key: "emr:validation:soap:{hash(soap_content + patient_id)}"
  TTL: 3600 seconds (1 hour)

  Why hash soap_content?
  - Identical SOAP notes → Same cache key → Cache hit
  - Different SOAP notes → Different cache key → Cache miss
  - Patient context matters (same SOAP for different patients = different validation)

IMPLEMENTATION:

  # File: backend/tests/performance/test_claude_api_caching.py

  import pytest
  import hashlib
  from backend.src.services.validation_service import EMRValidationService

  @pytest.mark.asyncio
  async def test_claude_api_cache_hit_rate():
      """
      Test Redis caching reduces Claude API calls.
      Target: ≥40% cache hit rate for repeated validations.
      """
      service = EMRValidationService()

      # Scenario: Same patient, 100 similar SOAP notes
      patient_scenario = {
          "id": "patient-001",
          "name": "John Smith",
          "age": 55,
          "chief_complaint": "Chest pain",
          "history": "2-hour history of central chest pain...",
      }

      # Generate 100 similar SOAP notes (slight variations)
      soap_notes = [
          {
              "subjective": f"Patient presents with chest pain for 2 hours. Pain described as crushing, radiating to left arm. {i}",
              "objective": "BP 152/88, HR 92, RR 20, SpO2 98% RA. S1S2+0, chest clear.",
              "assessment": "Likely acute coronary syndrome.",
              "plan": "ECG, troponin, aspirin 300mg PO stat, GTN sublingual.",
          }
          for i in range(100)
      ]

      cache_hits = 0
      cache_misses = 0
      api_call_count = 0

      for i, soap_note in enumerate(soap_notes):
          # Validate SOAP note
          result = await service.validate_soap_note(
              soap_note=soap_note,
              patient=patient_scenario,
          )

          # Check if cache was used
          if result.metadata.get("cache_hit"):
              cache_hits += 1
          else:
              cache_misses += 1
              api_call_count += 1

      # Calculate cache hit rate
      cache_hit_rate = cache_hits / (cache_hits + cache_misses)

      # Assertions
      assert cache_hit_rate >= 0.40, f"Cache hit rate {cache_hit_rate:.2%} < 40% target"
      assert api_call_count < 100, f"Expected <100 API calls, got {api_call_count}"

      # Log results
      print(f"""
      Cache Performance Test Results:
      --------------------------------
      Total validations:  100
      Cache hits:         {cache_hits} ({cache_hit_rate:.1%})
      Cache misses:       {cache_misses}
      Claude API calls:   {api_call_count}
      Cost savings:       {(1 - api_call_count/100):.1%} reduction

      Expected cost (no cache):  ~$0.30 (100 calls × $3/1M tokens × ~1000 tokens/call)
      Actual cost (with cache):  ~${api_call_count * 0.003:.2f}
      Cost saved:                ~${(100 - api_call_count) * 0.003:.2f}
      """)

  @pytest.mark.asyncio
  async def test_cache_key_uniqueness():
      """
      Test cache keys prevent collisions (different SOAP notes = different keys).
      """
      service = EMRValidationService()

      patient = {"id": "patient-001", "chief_complaint": "Chest pain"}

      soap_note_1 = {
          "subjective": "Patient presents with chest pain.",
          "objective": "BP 152/88.",
          "assessment": "ACS likely.",
          "plan": "ECG, troponin.",
      }

      soap_note_2 = {
          "subjective": "Patient presents with headache.",  # Different
          "objective": "BP 152/88.",
          "assessment": "Migraine likely.",
          "plan": "Paracetamol 1g PO.",
      }

      # Validate both SOAP notes
      result_1 = await service.validate_soap_note(soap_note_1, patient)
      result_2 = await service.validate_soap_note(soap_note_2, patient)

      # Both should be cache misses (different content)
      assert result_1.metadata.get("cache_hit") is False
      assert result_2.metadata.get("cache_hit") is False

      # Validate soap_note_1 again → should be cache hit
      result_1_repeat = await service.validate_soap_note(soap_note_1, patient)
      assert result_1_repeat.metadata.get("cache_hit") is True

  @pytest.mark.asyncio
  async def test_cache_invalidation_on_patient_change():
      """
      Test cache keys include patient context (same SOAP, different patient = cache miss).
      """
      service = EMRValidationService()

      soap_note = {
          "subjective": "Patient presents with chest pain.",
          "objective": "BP 152/88.",
          "assessment": "ACS likely.",
          "plan": "ECG, troponin.",
      }

      patient_1 = {"id": "patient-001", "age": 55, "chief_complaint": "Chest pain"}
      patient_2 = {"id": "patient-002", "age": 30, "chief_complaint": "Chest pain"}

      # Validate for patient_1
      result_1 = await service.validate_soap_note(soap_note, patient_1)
      assert result_1.metadata.get("cache_hit") is False

      # Validate for patient_2 (same SOAP, different patient)
      result_2 = await service.validate_soap_note(soap_note, patient_2)
      assert result_2.metadata.get("cache_hit") is False  # Different patient → cache miss

      # Validate for patient_1 again → cache hit
      result_1_repeat = await service.validate_soap_note(soap_note, patient_1)
      assert result_1_repeat.metadata.get("cache_hit") is True

REDIS MONITORING:

  # Monitor cache performance in real-time
  $ redis-cli INFO stats

  # Output (example):
  #   total_commands_processed:120000
  #   keyspace_hits:95000
  #   keyspace_misses:5000
  #   keyspace_hit_rate: 95% ✅ (95000 / (95000 + 5000))

  # Monitor cache memory usage
  $ redis-cli INFO memory

  # Output (example):
  #   used_memory_human:50.2M
  #   maxmemory_human:512M
  #   used_memory_percentage:9.8%  ✅ (plenty of headroom)
```

### Technology Stack

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Load Testing** | Locust | 2.20+ | API endpoint performance testing |
| **Database Profiling** | pgBench | (PostgreSQL 15) | Database throughput testing |
| **Database Analysis** | EXPLAIN ANALYZE | (PostgreSQL 15) | Query plan analysis |
| **Frontend Testing** | Lighthouse CI | 0.13+ | Web performance auditing |
| **Frontend Profiling** | React DevTools Profiler | (React 19.2) | Component render performance |
| **Monitoring** | Redis INFO | (Redis 7.2) | Cache hit rate monitoring |
| **Monitoring** | pg_stat_statements | (PostgreSQL 15) | Slow query detection |
| **CI/CD** | GitHub Actions | - | Automated performance regression detection |
| **Reporting** | HTML/JSON | - | Performance test reports |

### Integration Points

- **Integrates with**:
  - All backend APIs (PRD_BACKEND_002, PRD_BACKEND_003, PRD_INTEGRATION_002)
  - All frontend pages (PRD_FRONTEND_001, PRD_FRONTEND_002, PRD_FRONTEND_003)
  - PostgreSQL database (schema from PRD_BACKEND_001)
  - Redis cache (PRD_INTEGRATION_002)
  - GitHub Actions CI/CD pipeline

- **Consumed by**:
  - DevOps engineers (performance reports)
  - Developers (regression detection blocking PRs)
  - PM (production readiness validation)

- **Depends on**:
  - Test database seeding (100 users, 500 patients, 200 sessions)
  - Backend services running (FastAPI on port 8001)
  - Frontend build (npm run build → dist/)

### Security Considerations

- **Test Data Isolation**: Use separate test database (emr_test_db), never run load tests on production
- **API Rate Limiting**: Disable rate limiting for load tests (or use high limits)
- **Secrets Management**: Test users use dummy credentials (load_test_user_XXX@test.com / password123)
- **No PII in Reports**: Performance reports contain metrics only, no patient data
- **GitHub Actions Secrets**: Store API keys (Claude API) in GitHub Secrets, not in code

### Performance Requirements

| Requirement | Target | Measurement |
|-------------|--------|-------------|
| **API Response Time (p95)** | See table in "Business Context" section | Locust load testing |
| **Database Query Time (p95)** | <2s for complex queries | EXPLAIN ANALYZE |
| **Frontend Performance Score** | ≥90 | Lighthouse CI |
| **Cache Hit Rate** | ≥95% (Redis), ≥40% (Claude API) | Redis INFO, custom tests |
| **Concurrent Load** | 100+ users without degradation | Locust stress testing |
| **Throughput** | 1000+ auto-save requests/hour | Locust sustained load |
| **Regression Tolerance** | <20% latency increase vs baseline | GitHub Actions workflow |

---

## L - LOOP (Iterative Development)

### Phase 1: Foundation (30% of effort - 5 hours)

**Goal**: Set up performance testing infrastructure and establish baselines

**Tasks**:
1. **Install performance testing tools** - 30 min
   - Locust: `pip install locust==2.20.0`
   - pgBench: Already included with PostgreSQL 15
   - Lighthouse CI: `npm install -g @lhci/cli@0.13.0`
   - Create requirements.txt for performance tests

2. **Create test database seeding script** - 1 hour
   - Script: `tests/performance/seed_test_data.py`
   - Create 100 test users (load_test_user_001@test.com ... load_test_user_100@test.com)
   - Create 500 mock patients (diverse specialties, complexities)
   - Create 200 pre-existing EMR sessions (for GET /sessions list endpoint)
   - Create 50 completed sessions with validations (for dashboard analytics)

3. **Create baseline measurement script** - 1 hour
   - Script: `tests/performance/measure_baseline.py`
   - Run single-user tests for all endpoints
   - Save results to `baselines/baseline.json`:
     ```json
     {
       "commit": "a1b2c3d",
       "date": "2026-02-16",
       "endpoints": [
         {
           "name": "POST /emr/sessions/start",
           "p50": 120,
           "p95": 178,
           "p99": 245,
           "success_rate": 1.0
         },
         ...
       ]
     }
     ```

4. **Write basic Locust test file** - 1.5 hours
   - File: `tests/performance/test_api_benchmarks.py`
   - EMRUser class with on_start (login)
   - 3 tasks: autosave_session, start_new_session, submit_session
   - Response validation (mark failure if latency > target)

5. **Run smoke test** - 30 min
   - Start backend: `cd backend && uvicorn src.main:app --reload`
   - Run Locust: `locust -f tests/performance/test_api_benchmarks.py --users 5 --spawn-rate 1 --run-time 1m --headless`
   - Verify: All endpoints return 200, no 500 errors

**Validation Gate**:
- [ ] Locust installed and runs successfully
- [ ] Test database seeded (100 users, 500 patients, 200 sessions)
- [ ] Baseline measurements saved to baseline.json
- [ ] Smoke test passes (5 users, 1 minute, 100% success rate)
- [ ] No errors in setup (Docker containers running, database accessible)

---

### Phase 2: Core Functionality (50% of effort - 8 hours)

**Goal**: Implement all performance tests and database profiling

**Tasks**:
1. **Implement full Locust test suite** - 2 hours
   - Add all 15 API endpoints:
     * Session endpoints: start, update, submit, get, list, delete
     * Validation endpoints: validate_soap, validate_prescription, validate_pathology
     * Progress endpoints: dashboard, weekly_trends, weak_areas, specialty_breakdown
   - Weighted task distribution:
     * @task(10): autosave (most common)
     * @task(5): start session
     * @task(3): get dashboard data
     * @task(1): submit session
   - Add response validation (catch_response context)

2. **Create 4 load test scenarios** - 1.5 hours
   - Scenario 1: Normal load (50 users, 5 min)
   - Scenario 2: Peak load (100 users, 10 min)
   - Scenario 3: Stress test (200 users, 5 min)
   - Scenario 4: Spike test (0→200→50→200, 10 min)
   - Script: `tests/performance/run_load_tests.sh` (runs all 4 scenarios)

3. **Implement database query profiling** - 2 hours
   - Create SQL files for each test query:
     * `tests/performance/queries/dashboard_analytics.sql`
     * `tests/performance/queries/specialty_breakdown.sql`
     * `tests/performance/queries/learning_velocity.sql`
     * `tests/performance/queries/autosave_update.sql`
   - Each file includes:
     * EXPLAIN ANALYZE query
     * Expected plan (Index Scan vs Seq Scan)
     * Performance target (<1s, <2s, etc.)
   - Script: `tests/performance/run_query_profiling.sh`

4. **Create pgBench custom workload** - 1 hour
   - File: `tests/performance/pgbench_emr_workload.sql`
   - 70% auto-save UPDATEs
   - 20% session start INSERTs
   - 10% dashboard SELECTs
   - Run: `pgbench -c 50 -j 4 -T 60 -f pgbench_emr_workload.sql -r emr_test_db`

5. **Implement Claude API caching tests** - 1.5 hours
   - File: `backend/tests/performance/test_claude_api_caching.py`
   - Test 1: Cache hit rate (100 similar SOAP notes)
   - Test 2: Cache key uniqueness (different SOAP notes = different keys)
   - Test 3: Cache invalidation (different patient = cache miss)
   - Test 4: Redis memory usage (ensure <100 MB for 1000 cached validations)

**Validation Gate**:
- [ ] All 4 Locust scenarios run successfully
- [ ] Load test report generated (HTML + JSON)
- [ ] Database query profiling complete (all queries use Index Scan)
- [ ] pgBench workload achieves >1000 TPS
- [ ] Claude API cache hit rate ≥40%
- [ ] No critical failures (500 errors, database deadlocks)

---

### Phase 3: Polish & CI/CD Integration (20% of effort - 3 hours)

**Goal**: Automate performance testing in CI/CD and create performance dashboard

**Tasks**:
1. **Create Lighthouse CI configuration** - 1 hour
   - File: `.github/workflows/lighthouse-ci.yml`
   - Test 4 pages: /, /dashboard, /emr/practice, /mcq/practice
   - File: `frontend/lighthouse-budget.json` (performance budgets)
   - Run Lighthouse 3 times, take median
   - Post results as PR comment

2. **Create GitHub Actions performance workflow** - 1.5 hours
   - File: `.github/workflows/performance-tests.yml`
   - Trigger: Pull request (on backend/frontend changes) + daily cron
   - Steps:
     1. Start services (docker-compose up -d)
     2. Seed test database
     3. Warm caches
     4. Run Locust (Scenario 2: Peak Load - 100 users)
     5. Run database profiling
     6. Run Lighthouse CI
     7. Compare vs baseline
     8. Post PR comment with results
     9. Block PR if regression detected (exit code 1)

3. **Create performance regression detection script** - 30 min
   - Script: `tests/performance/detect_regressions.py`
   - Load current results (Locust JSON)
   - Load baseline (baselines/baseline.json)
   - Compare each endpoint:
     * If current p95 > baseline p95 * 1.20 → REGRESSION
   - Output: JSON report + exit code (0 = pass, 1 = regression)

4. **Write performance testing documentation** - 30 min
   - File: `docs/PERFORMANCE_TESTING.md`
   - How to run performance tests locally
   - How to interpret results
   - How to update baselines
   - Troubleshooting guide (common issues)

**Validation Gate**:
- [ ] Lighthouse CI workflow runs successfully
- [ ] GitHub Actions performance workflow triggers on PR
- [ ] Performance regression detected correctly (test with intentionally slow code)
- [ ] PR comment posted with results
- [ ] Documentation complete and accurate
- [ ] All tests passing (100% pass rate)

---

## P - PLAN (Detailed Implementation)

### Task Breakdown (1-2 hour chunks)

#### Phase 1 Tasks (Foundation)

**Task 1.1: Install Performance Testing Tools**
- **Effort**: 30 min
- **Owner**: DevOps Engineer / QA Engineer
- **Deliverable**: requirements.txt, installed tools
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] Locust 2.20.0 installed (`pip install locust==2.20.0`)
  - [ ] Lighthouse CLI 0.13.0 installed (`npm install -g @lhci/cli@0.13.0`)
  - [ ] requirements.txt created:
    ```
    locust==2.20.0
    pytest==7.4.3
    pytest-asyncio==0.21.1
    psycopg2-binary==2.9.9
    redis==5.0.1
    ```
  - [ ] All tools run successfully (`locust --version`, `lhci --version`)

**Task 1.2: Create Test Database Seeding Script**
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `tests/performance/seed_test_data.py`
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] Script creates 100 test users (load_test_user_001@test.com ... load_test_user_100@test.com)
  - [ ] Password: "password123" (hashed with bcrypt)
  - [ ] Script creates 500 mock patients (all specialties: Cardiology, Respiratory, etc.)
  - [ ] Script creates 200 pre-existing EMR sessions (50 completed, 150 active)
  - [ ] Script creates 50 EMR validations (linked to completed sessions)
  - [ ] Script is idempotent (can run multiple times without errors)
  - [ ] Run time: <60 seconds

**Implementation**:
```python
# File: tests/performance/seed_test_data.py

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from backend.src.db.models import User, MockPatient, EMRSession, EMRValidation
from backend.src.core.security import get_password_hash
import random
from datetime import datetime, timedelta

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/emr_test_db"

async def seed_test_data():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("Seeding test database...")

        # 1. Create 100 test users
        print("Creating 100 test users...")
        users = []
        for i in range(1, 101):
            user = User(
                email=f"load_test_user_{i:03d}@test.com",
                hashed_password=get_password_hash("password123"),
                full_name=f"Test User {i}",
                role="student",
                institution="Test University",
            )
            users.append(user)
        session.add_all(users)
        await session.commit()
        print(f"✅ Created {len(users)} test users")

        # 2. Create 500 mock patients
        print("Creating 500 mock patients...")
        specialties = ["Cardiology", "Respiratory", "Neurology", "Gastroenterology", "Endocrinology", "Rheumatology", "Nephrology", "Haematology"]
        complexities = ["Simple", "Moderate", "Complex"]
        patients = []
        for i in range(1, 501):
            patient = MockPatient(
                name=f"Test Patient {i}",
                age=random.randint(18, 85),
                gender=random.choice(["Male", "Female"]),
                chief_complaint=random.choice(["Chest pain", "Shortness of breath", "Headache", "Abdominal pain"]),
                specialty=random.choice(specialties),
                complexity=random.choice(complexities),
                scenario={"history": f"Patient {i} scenario..."},
            )
            patients.append(patient)
        session.add_all(patients)
        await session.commit()
        print(f"✅ Created {len(patients)} mock patients")

        # 3. Create 200 EMR sessions (50 completed, 150 active)
        print("Creating 200 EMR sessions...")
        sessions = []
        for i in range(1, 201):
            user = random.choice(users)
            patient = random.choice(patients)
            is_completed = i <= 50  # First 50 are completed
            session_obj = EMRSession(
                user_id=user.id,
                patient_id=patient.id,
                emr_system=random.choice(["epic", "cerner"]),
                is_active=not is_completed,
                started_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                submitted_at=datetime.utcnow() - timedelta(days=random.randint(0, 15)) if is_completed else None,
                completed_at=datetime.utcnow() - timedelta(days=random.randint(0, 15)) if is_completed else None,
                session_data={"draft_subjective": "Test draft..."} if not is_completed else {},
            )
            sessions.append(session_obj)
        session.add_all(sessions)
        await session.commit()
        print(f"✅ Created {len(sessions)} EMR sessions")

        # 4. Create 50 EMR validations (for completed sessions)
        print("Creating 50 EMR validations...")
        validations = []
        completed_sessions = [s for s in sessions if s.completed_at is not None]
        for sess in completed_sessions:
            validation = EMRValidation(
                session_id=sess.id,
                total_amc_score=random.randint(8, 15),
                pass_status=True,
                feedback_json={"communication_score": 3, "clinical_reasoning_score": 3},
                validated_at=datetime.utcnow(),
            )
            validations.append(validation)
        session.add_all(validations)
        await session.commit()
        print(f"✅ Created {len(validations)} EMR validations")

        print("✅ Test data seeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_test_data())
```

**Task 1.3: Create Baseline Measurement Script**
- **Effort**: 1 hour
- **Owner**: DevOps Engineer
- **Deliverable**: `tests/performance/measure_baseline.py`, `baselines/baseline.json`
- **Dependencies**: Task 1.2
- **Acceptance Criteria**:
  - [ ] Script runs single-user tests for all endpoints
  - [ ] Collects p50, p95, p99, success_rate for each endpoint
  - [ ] Saves results to `baselines/baseline.json` with commit SHA and date
  - [ ] Baseline file is human-readable and git-trackable
  - [ ] Run time: <5 minutes

**Task 1.4: Write Basic Locust Test File**
- **Effort**: 1.5 hours
- **Owner**: QA Engineer / Backend Engineer
- **Deliverable**: `tests/performance/test_api_benchmarks.py`
- **Dependencies**: Task 1.3
- **Acceptance Criteria**:
  - [ ] EMRUser class with on_start (login to get JWT token)
  - [ ] 3 tasks implemented: autosave_session, start_new_session, submit_session
  - [ ] Tasks weighted correctly (@task(10), @task(5), @task(1))
  - [ ] Response validation (mark failure if latency > target)
  - [ ] Think time: between(1, 3) seconds
  - [ ] All endpoints use JWT authentication

**Implementation**:
```python
# File: tests/performance/test_api_benchmarks.py

from locust import HttpUser, task, between
import random

class EMRUser(HttpUser):
    wait_time = between(1, 3)  # 1-3 seconds between tasks (realistic typing pace)
    host = "http://localhost:8001"

    def on_start(self):
        """Login and get JWT token"""
        # Login with one of 100 test users
        user_id = random.randint(1, 100)
        response = self.client.post("/api/v1/auth/login", json={
            "email": f"load_test_user_{user_id:03d}@test.com",
            "password": "password123"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
            self.session_id = None  # Will be set when session starts
        else:
            raise Exception(f"Login failed: {response.text}")

    @task(10)  # 10x weight (most common operation)
    def autosave_session(self):
        """Test auto-save performance (target: <200ms at p95)"""
        if not self.session_id:
            self.start_new_session()  # Create session if doesn't exist
            return

        with self.client.put(
            f"/api/v1/emr/sessions/{self.session_id}",
            json={
                "session_data": {
                    "draft_subjective": f"Patient presents with chest pain... (updated {random.randint(1, 1000)})",
                    "draft_objective": "BP 152/88, HR 92...",
                    "current_tab": "subjective",
                }
            },
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                latency_ms = response.elapsed.total_seconds() * 1000
                if latency_ms > 200:
                    response.failure(f"Auto-save took {latency_ms:.0f}ms (>200ms target)")
                else:
                    response.success()
            else:
                response.failure(f"Auto-save failed: {response.status_code}")

    @task(5)  # 5x weight
    def start_new_session(self):
        """Test session start (target: <500ms)"""
        with self.client.post(
            "/api/v1/emr/sessions/start",
            json={
                "emr_system": random.choice(["epic", "cerner"]),
                "patient_filter": {"specialty": "Cardiology", "complexity": "Moderate"},
            },
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                latency_ms = response.elapsed.total_seconds() * 1000
                self.session_id = response.json()["session_id"]  # Save for auto-save
                if latency_ms > 500:
                    response.failure(f"Session start took {latency_ms:.0f}ms (>500ms target)")
                else:
                    response.success()
            else:
                response.failure(f"Session start failed: {response.status_code}")

    @task(1)  # 1x weight (least common)
    def submit_session_with_validation(self):
        """Test full validation pipeline (target: <5s including Claude API)"""
        if not self.session_id:
            return  # Skip if no session

        with self.client.post(
            f"/api/v1/emr/sessions/{self.session_id}/submit",
            json={
                "soap_note": {
                    "subjective": "Patient presents with chest pain for 2 hours. Pain described as crushing, radiating to left arm.",
                    "objective": "BP 152/88, HR 92, RR 20, SpO2 98% RA. S1S2+0, chest clear.",
                    "assessment": "Likely acute coronary syndrome.",
                    "plan": "ECG, troponin, aspirin 300mg PO stat, GTN sublingual.",
                },
                "prescriptions": [
                    {"medication": "Aspirin", "dose": "300mg", "route": "PO", "frequency": "stat"}
                ],
                "pathology_orders": [
                    {"test": "Troponin", "urgency": "Urgent", "indication": "Rule out MI"}
                ]
            },
            headers=self.headers,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                latency_ms = response.elapsed.total_seconds() * 1000
                if latency_ms > 5000:
                    response.failure(f"Submit+validation took {latency_ms:.0f}ms (>5000ms target)")
                else:
                    response.success()
                self.session_id = None  # Reset session
            else:
                response.failure(f"Submit failed: {response.status_code}")
```

**Task 1.5: Run Smoke Test**
- **Effort**: 30 min
- **Owner**: QA Engineer
- **Deliverable**: Smoke test results (5 users, 1 minute)
- **Dependencies**: Task 1.4
- **Acceptance Criteria**:
  - [ ] Backend services running (FastAPI on port 8001)
  - [ ] Locust runs: `locust -f tests/performance/test_api_benchmarks.py --users 5 --spawn-rate 1 --run-time 1m --headless`
  - [ ] All requests return 200 (100% success rate)
  - [ ] No 500 errors in backend logs
  - [ ] No database connection errors

---

#### Phase 2 Tasks (Core Functionality)

**Task 2.1: Implement Full Locust Test Suite**
- **Effort**: 2 hours
- **Owner**: QA Engineer
- **Deliverable**: Complete `test_api_benchmarks.py` with all 15 endpoints
- **Dependencies**: Phase 1 complete
- **Acceptance Criteria**:
  - [ ] All session endpoints tested: start, update, submit, get, list, delete
  - [ ] All validation endpoints tested: validate_soap, validate_prescription, validate_pathology
  - [ ] All progress endpoints tested: dashboard, weekly_trends, weak_areas, specialty_breakdown
  - [ ] Weighted task distribution reflects real usage patterns
  - [ ] All endpoints have response validation (catch_response)

**Task 2.2: Create 4 Load Test Scenarios**
- **Effort**: 1.5 hours
- **Owner**: DevOps Engineer
- **Deliverable**: `tests/performance/run_load_tests.sh`
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Scenario 1: Normal load (50 users, 5 min) - runs successfully
  - [ ] Scenario 2: Peak load (100 users, 10 min) - runs successfully
  - [ ] Scenario 3: Stress test (200 users, 5 min) - runs successfully
  - [ ] Scenario 4: Spike test (custom user shape) - runs successfully
  - [ ] Script generates HTML + JSON reports for each scenario
  - [ ] Results saved to `performance_results/` directory

**Implementation**:
```bash
#!/bin/bash
# File: tests/performance/run_load_tests.sh

set -e

echo "🚀 Running EMR Performance Load Tests"
echo "======================================"

# Create results directory
mkdir -p performance_results

# Scenario 1: Normal Load (50 users)
echo ""
echo "📊 Scenario 1: Normal Load (50 concurrent users)"
locust -f tests/performance/test_api_benchmarks.py \
  --users 50 --spawn-rate 5 --run-time 5m \
  --headless \
  --html performance_results/scenario1_normal_load.html \
  --json performance_results/scenario1_normal_load.json

# Scenario 2: Peak Load (100 users)
echo ""
echo "📊 Scenario 2: Peak Load (100 concurrent users)"
locust -f tests/performance/test_api_benchmarks.py \
  --users 100 --spawn-rate 10 --run-time 10m \
  --headless \
  --html performance_results/scenario2_peak_load.html \
  --json performance_results/scenario2_peak_load.json

# Scenario 3: Stress Test (200 users)
echo ""
echo "📊 Scenario 3: Stress Test (200 concurrent users)"
locust -f tests/performance/test_api_benchmarks.py \
  --users 200 --spawn-rate 20 --run-time 5m \
  --headless \
  --html performance_results/scenario3_stress_test.html \
  --json performance_results/scenario3_stress_test.json

echo ""
echo "✅ All load test scenarios complete!"
echo "📈 Reports saved to performance_results/"
```

**Task 2.3: Implement Database Query Profiling**
- **Effort**: 2 hours
- **Owner**: Backend Engineer
- **Deliverable**: SQL files + profiling script
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] 4 SQL files created (dashboard_analytics, specialty_breakdown, learning_velocity, autosave_update)
  - [ ] Each query includes EXPLAIN ANALYZE output
  - [ ] All queries use Index Scan (no Seq Scan on large tables)
  - [ ] Profiling script runs all queries and generates report
  - [ ] Report flags queries slower than target (<1s, <2s, etc.)

**Task 2.4: Create pgBench Custom Workload**
- **Effort**: 1 hour
- **Owner**: Backend Engineer
- **Deliverable**: `tests/performance/pgbench_emr_workload.sql`
- **Dependencies**: Task 2.3
- **Acceptance Criteria**:
  - [ ] Custom workload file with 70% UPDATEs, 20% INSERTs, 10% SELECTs
  - [ ] pgBench runs: `pgbench -c 50 -j 4 -T 60 -f pgbench_emr_workload.sql -r emr_test_db`
  - [ ] Achieves >1000 TPS (transactions per second)
  - [ ] Latency average <50ms
  - [ ] No database errors (deadlocks, constraint violations)

**Task 2.5: Implement Claude API Caching Tests**
- **Effort**: 1.5 hours
- **Owner**: Backend Engineer
- **Deliverable**: `backend/tests/performance/test_claude_api_caching.py`
- **Dependencies**: Task 2.1
- **Acceptance Criteria**:
  - [ ] Test 1: Cache hit rate (100 similar SOAP notes) - ≥40% hit rate
  - [ ] Test 2: Cache key uniqueness (different SOAP notes = different keys) - passes
  - [ ] Test 3: Cache invalidation (different patient = cache miss) - passes
  - [ ] Test 4: Redis memory usage (<100 MB for 1000 cached validations) - passes
  - [ ] All tests passing (pytest)

---

#### Phase 3 Tasks (Polish & CI/CD)

**Task 3.1: Create Lighthouse CI Configuration**
- **Effort**: 1 hour
- **Owner**: Frontend Engineer
- **Deliverable**: `.github/workflows/lighthouse-ci.yml`, `frontend/lighthouse-budget.json`
- **Dependencies**: Phase 2 complete
- **Acceptance Criteria**:
  - [ ] Workflow triggers on PR (frontend/** changes)
  - [ ] Tests 4 pages: /, /dashboard, /emr/practice, /mcq/practice
  - [ ] Performance budgets defined (FCP <1.5s, TTI <3s, JS <300KB)
  - [ ] Runs 3 times per page, takes median
  - [ ] Posts results as PR comment
  - [ ] Blocks PR if Performance Score <90

**Task 3.2: Create GitHub Actions Performance Workflow**
- **Effort**: 1.5 hours
- **Owner**: DevOps Engineer
- **Deliverable**: `.github/workflows/performance-tests.yml`
- **Dependencies**: Task 3.1
- **Acceptance Criteria**:
  - [ ] Workflow triggers on PR (backend/** or frontend/** changes) + daily cron
  - [ ] Starts services (docker-compose up -d)
  - [ ] Seeds test database
  - [ ] Runs Locust (Scenario 2: Peak Load)
  - [ ] Runs database profiling
  - [ ] Compares vs baseline
  - [ ] Posts PR comment with results
  - [ ] Blocks PR if regression detected (exit code 1)

**Implementation**:
```yaml
# File: .github/workflows/performance-tests.yml

name: Performance Tests

on:
  pull_request:
    paths:
      - 'backend/**'
      - 'frontend/**'
      - 'tests/performance/**'
      - '.github/workflows/performance-tests.yml'
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC

jobs:
  performance:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: emr_test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

      redis:
        image: redis:7.2
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install backend dependencies
        working-directory: backend
        run: |
          pip install -r requirements.txt
          pip install -r ../tests/performance/requirements.txt

      - name: Run database migrations
        working-directory: backend
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/emr_test_db
        run: alembic upgrade head

      - name: Seed test database
        working-directory: tests/performance
        env:
          DATABASE_URL: postgresql+asyncpg://postgres:postgres@localhost:5432/emr_test_db
        run: python seed_test_data.py

      - name: Start backend API
        working-directory: backend
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/emr_test_db
          REDIS_URL: redis://localhost:6379
        run: |
          uvicorn src.main:app --host 0.0.0.0 --port 8001 &
          sleep 10  # Wait for server to start

      - name: Warm caches
        working-directory: tests/performance
        run: python warm_caches.py

      - name: Run Locust load test (Scenario 2: Peak Load)
        working-directory: tests/performance
        run: |
          locust -f test_api_benchmarks.py \
            --users 100 --spawn-rate 10 --run-time 10m \
            --headless \
            --html performance_report.html \
            --json performance_stats.json

      - name: Run database query profiling
        working-directory: tests/performance
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/emr_test_db
        run: ./run_query_profiling.sh

      - name: Detect performance regressions
        id: regression
        working-directory: tests/performance
        run: |
          python detect_regressions.py \
            --current performance_stats.json \
            --baseline ../../baselines/baseline.json \
            --output regression_report.json

      - name: Upload performance reports
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: performance-reports
          path: |
            tests/performance/performance_report.html
            tests/performance/performance_stats.json
            tests/performance/regression_report.json

      - name: Comment PR with results
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('tests/performance/regression_report.json', 'utf8')
            );

            const passed = report.regressions.length === 0;
            const emoji = passed ? '✅' : '❌';
            const status = passed ? 'PASSED' : 'REGRESSION DETECTED';

            let comment = `## ${emoji} Performance Test Results\n\n`;
            comment += `**Status**: ${status}\n\n`;
            comment += `### API Latency (p95 - 100 concurrent users)\n\n`;
            comment += `| Endpoint | Current | Target | Status |\n`;
            comment += `|----------|---------|--------|--------|\n`;

            for (const endpoint of report.endpoints) {
              const statusEmoji = endpoint.passed ? '✅' : '⚠️';
              comment += `| ${endpoint.name} | ${endpoint.current_p95}ms | <${endpoint.target}ms | ${statusEmoji} |\n`;
            }

            if (report.regressions.length > 0) {
              comment += `\n### ⚠️ Performance Regressions Detected\n\n`;
              for (const regression of report.regressions) {
                comment += `- **${regression.endpoint}**: ${regression.current_p95}ms (was ${regression.baseline_p95}ms) - ${regression.increase_pct}% increase\n`;
              }
            }

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });

      - name: Fail workflow if regression detected
        if: steps.regression.outputs.regressions == 'true'
        run: exit 1
```

**Task 3.3: Create Performance Regression Detection Script**
- **Effort**: 30 min
- **Owner**: DevOps Engineer
- **Deliverable**: `tests/performance/detect_regressions.py`
- **Dependencies**: Task 3.2
- **Acceptance Criteria**:
  - [ ] Loads current Locust results (JSON)
  - [ ] Loads baseline results (baselines/baseline.json)
  - [ ] Compares each endpoint: if current p95 > baseline p95 * 1.20 → REGRESSION
  - [ ] Outputs JSON report with regressions array
  - [ ] Exit code 0 if no regressions, exit code 1 if regressions found

**Task 3.4: Write Performance Testing Documentation**
- **Effort**: 30 min
- **Owner**: QA Engineer / DevOps Engineer
- **Deliverable**: `docs/PERFORMANCE_TESTING.md`
- **Dependencies**: Task 3.3
- **Acceptance Criteria**:
  - [ ] How to run performance tests locally (step-by-step)
  - [ ] How to interpret results (what p50/p95/p99 mean)
  - [ ] How to update baselines (when to update, how to commit)
  - [ ] Troubleshooting guide (common errors: database connection, timeout, 500 errors)
  - [ ] Documentation is clear and concise (<2000 words)

---

### Dependency Graph

```
Task 1.1 (Install Tools)
    ↓
Task 1.2 (Seed Database) ←─────────┐
    ↓                               │
Task 1.3 (Baseline Measurement)    │
    ↓                               │
Task 1.4 (Basic Locust Test)       │
    ↓                               │
Task 1.5 (Smoke Test)              │
    ↓                               │
────────────────────────────────────┼─── PHASE 1 GATE
    ↓                               │
Task 2.1 (Full Locust Suite)       │
    ↓                               │
Task 2.2 (Load Test Scenarios) ────┤
    ↓                               │
Task 2.3 (Database Profiling)      │
    ↓                               │
Task 2.4 (pgBench Workload)        │
    ↓                               │
Task 2.5 (Caching Tests)           │
    ↓                               │
────────────────────────────────────┼─── PHASE 2 GATE
    ↓                               │
Task 3.1 (Lighthouse CI) ──────────┤
    ↓                               │
Task 3.2 (GitHub Actions Workflow)─┤
    ↓                               │
Task 3.3 (Regression Detection)    │
    ↓                               │
Task 3.4 (Documentation)           │
    ↓                               │
────────────────────────────────────┘
    ↓
COMPLETE (PRD 14 of 14 - 100%)
```

---

### Resource Allocation

| Role | Effort (hours) | Tasks |
|------|----------------|-------|
| **DevOps Engineer** | 6 hours | 1.1, 1.3, 2.2, 3.2, 3.3 |
| **QA Engineer** | 5 hours | 1.4, 1.5, 2.1, 3.4 |
| **Backend Engineer** | 5 hours | 1.2, 2.3, 2.4, 2.5 |
| **Frontend Engineer** | 2 hours | 3.1 |
| **PM Coordinator** | 2 hours | Validation gates, final review |
| **Total** | 20 hours | 14 tasks across 3 phases |

---

### Timeline

| Day | Phase | Tasks | Deliverable |
|-----|-------|-------|-------------|
| **Day 1** | Phase 1 | 1.1, 1.2, 1.3 | Tools installed, test DB seeded, baseline measured |
| **Day 2** | Phase 1 | 1.4, 1.5 | Basic Locust test working, smoke test passes |
| **Day 3** | Phase 2 | 2.1, 2.2 | Full Locust suite + 4 load scenarios |
| **Day 4** | Phase 2 | 2.3, 2.4, 2.5 | Database profiling + pgBench + caching tests |
| **Day 5** | Phase 3 | 3.1, 3.2, 3.3, 3.4 | CI/CD integrated, documentation complete |

**Total Duration**: 5 days (1 sprint)

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements

- [ ] **Locust Load Testing**:
  - [ ] All 15 API endpoints tested (session, validation, progress)
  - [ ] 4 load test scenarios run successfully (Normal, Peak, Stress, Spike)
  - [ ] HTML + JSON reports generated for each scenario
  - [ ] All endpoints meet latency targets (see table in "Business Context")

- [ ] **Database Query Profiling**:
  - [ ] 4 complex queries profiled (dashboard analytics, specialty breakdown, learning velocity, auto-save)
  - [ ] All queries use Index Scan (no Seq Scan on large tables)
  - [ ] All queries meet latency targets (<1s, <2s, etc.)
  - [ ] pgBench workload achieves >1000 TPS

- [ ] **Frontend Performance Testing**:
  - [ ] Lighthouse CI tests 4 pages (/, /dashboard, /emr/practice, /mcq/practice)
  - [ ] All pages achieve Performance Score ≥90
  - [ ] All pages meet performance budgets (FCP <1.5s, TTI <3s, JS <300KB)
  - [ ] Recharts render performance <500ms

- [ ] **Claude API Caching**:
  - [ ] Cache hit rate ≥40% for repeated validations
  - [ ] Cache key uniqueness validated (different SOAP = different key)
  - [ ] Cache invalidation works (different patient = cache miss)
  - [ ] Redis memory usage <100 MB for 1000 cached validations

- [ ] **CI/CD Integration**:
  - [ ] GitHub Actions workflow triggers on PR (backend/frontend changes)
  - [ ] Workflow runs all performance tests (Locust, database profiling, Lighthouse)
  - [ ] Workflow compares vs baseline, detects regressions
  - [ ] Workflow posts PR comment with results
  - [ ] Workflow blocks PR merge if regression detected (exit code 1)

#### Quality Requirements

- [ ] **Test Coverage**: All performance tests passing (100% pass rate)
- [ ] **Test Data**: Test database seeded (100 users, 500 patients, 200 sessions)
- [ ] **Baselines**: Baseline measurements saved (baselines/baseline.json)
- [ ] **Documentation**: Performance testing documentation complete (docs/PERFORMANCE_TESTING.md)

#### Performance Requirements (ALL MUST MEET TARGETS)

**API Performance (Locust - 100 concurrent users)**:
- [ ] POST /emr/sessions/start: <500ms (p95)
- [ ] PUT /emr/sessions/{id} (auto-save): <200ms (p95)
- [ ] POST /emr/sessions/{id}/submit: <1s (p95, no validation)
- [ ] POST /emr/validation/soap (Layer 3 Claude): 3-5s (p95)
- [ ] GET /progress/dashboard/emr (cached): <200ms (p95)
- [ ] GET /progress/weekly-trends/unified (cached): <150ms (p95)

**Database Performance (pgBench + EXPLAIN ANALYZE)**:
- [ ] Dashboard analytics query: <2s
- [ ] Specialty breakdown query: <1s
- [ ] Learning velocity query: <1.5s
- [ ] Auto-save UPDATE: <50ms
- [ ] All queries use Index Scan (no Seq Scan)

**Frontend Performance (Lighthouse CI)**:
- [ ] Performance Score: ≥90 (all pages)
- [ ] First Contentful Paint: <1.5s (all pages)
- [ ] Time to Interactive: <3s (all pages)
- [ ] JavaScript Bundle Size: <300 KB
- [ ] Cumulative Layout Shift: <0.1

**Cache Performance**:
- [ ] Redis Cache Hit Rate: ≥95% (dashboard APIs)
- [ ] Claude API Cache Hit Rate: ≥40% (repeated validations)
- [ ] Cached API response time: <100ms

**Load Testing**:
- [ ] 100 concurrent users: No performance degradation (<10% latency increase vs 50 users)
- [ ] Throughput (auto-save): ≥1000 requests/hour sustained
- [ ] Error rate: <1% (500 errors/total requests)

#### Security Requirements

- [ ] **Test Data Isolation**: Test database separate from production (emr_test_db)
- [ ] **No PII in Reports**: Performance reports contain metrics only, no patient names/data
- [ ] **Dummy Credentials**: Test users use non-production passwords (password123)
- [ ] **Secrets Management**: Claude API key stored in GitHub Secrets, not in code

#### Regression Detection

- [ ] **Baseline Comparison**: All endpoints compared vs baseline.json
- [ ] **Regression Threshold**: Alert if current p95 > baseline p95 * 1.20 (20% increase)
- [ ] **PR Blocking**: Workflow exits with code 1 if regression detected
- [ ] **False Positive Handling**: Baseline can be updated after manual review

---

### Testing Requirements

#### Performance Tests (100% automated)

**Load Testing (Locust)**:
```python
# All scenarios must pass

# Scenario 1: Normal Load
assert all_endpoints_meet_targets(50_users, 5_min)
assert error_rate < 0.01  # <1% errors

# Scenario 2: Peak Load
assert all_endpoints_meet_targets(100_users, 10_min)
assert error_rate < 0.01

# Scenario 3: Stress Test
assert system_degrades_gracefully(200_users, 5_min)
assert no_500_errors()

# Scenario 4: Spike Test
assert handles_rapid_scaling(0_to_200_in_30s)
```

**Database Profiling (EXPLAIN ANALYZE)**:
```sql
-- All queries must use Index Scan

EXPLAIN ANALYZE <query>;
-- Expected: "Index Scan using <index_name>"
-- NOT: "Seq Scan on <table_name>"

-- Latency targets
assert dashboard_analytics_query < 2000ms
assert specialty_breakdown_query < 1000ms
assert learning_velocity_query < 1500ms
assert autosave_update_query < 50ms
```

**Frontend Performance (Lighthouse CI)**:
```bash
# All pages must meet budgets

lhci autorun \
  --assert.assertions.performance=0.90 \
  --assert.assertions.first-contentful-paint=1500 \
  --assert.assertions.interactive=3000
```

**Caching (pytest)**:
```python
# Cache hit rate tests

@pytest.mark.asyncio
async def test_redis_cache_hit_rate():
    hit_rate = await measure_cache_performance(100_users, 5_min)
    assert hit_rate >= 0.95

@pytest.mark.asyncio
async def test_claude_api_cache_hit_rate():
    hit_rate = await measure_claude_cache(100_soap_notes)
    assert hit_rate >= 0.40
```

#### Minimum Test Cases

- [x] **Locust Load Tests**: 4 scenarios (Normal, Peak, Stress, Spike)
- [x] **Database Profiling**: 4 queries (dashboard, specialty, velocity, auto-save)
- [x] **pgBench Workload**: Mixed workload (70% UPDATE, 20% INSERT, 10% SELECT)
- [x] **Lighthouse CI**: 4 pages (/, /dashboard, /emr/practice, /mcq/practice)
- [x] **Caching Tests**: 4 tests (Redis hit rate, Claude hit rate, uniqueness, invalidation)

---

### Documentation Deliverables

#### Code Documentation

- [ ] **Performance Test Scripts**: All Python/SQL files documented with docstrings
  - `tests/performance/test_api_benchmarks.py` (Locust tests)
  - `tests/performance/seed_test_data.py` (Database seeding)
  - `tests/performance/detect_regressions.py` (Regression detection)
  - `tests/performance/run_query_profiling.sh` (Database profiling)

- [ ] **Inline Comments**: Complex logic explained (e.g., cache key hashing, weighted tasks)

- [ ] **README Updates**: `tests/performance/README.md` with:
  - How to run performance tests locally
  - How to interpret results
  - How to update baselines

#### Architecture Documentation

- [ ] **Performance Testing Architecture**: This PRD serves as ADR (Architecture Decision Record)
  - Why Locust (Python ecosystem, web UI, distributed testing)
  - Why pgBench (native PostgreSQL, industry standard)
  - Why Lighthouse CI (Google-backed, CI integration)

- [ ] **Performance Metrics Glossary**: `docs/PERFORMANCE_METRICS.md`
  - p50 (median): 50% of requests faster than this
  - p95 (95th percentile): 95% of requests faster than this
  - p99 (99th percentile): 99% of requests faster than this
  - TPS (transactions per second): Database throughput
  - RPS (requests per second): API throughput

- [ ] **Baseline Management Guide**: `docs/BASELINE_MANAGEMENT.md`
  - When to update baselines (after intentional optimizations)
  - How to commit baselines (git commit baselines/baseline.json)
  - How to review baseline changes (manual review required)

#### User Documentation

- [ ] **Performance Testing Guide**: `docs/PERFORMANCE_TESTING.md`
  - How to run performance tests locally (step-by-step)
  - How to interpret results (understanding reports)
  - Troubleshooting guide (common errors and solutions)

- [ ] **CI/CD Integration Guide**: `docs/CI_CD_PERFORMANCE.md`
  - How GitHub Actions workflow works
  - How to fix performance regressions
  - How to request baseline updates

---

### Deployment Checklist

#### Pre-Deployment

- [ ] All performance tests passing (100% pass rate)
- [ ] All endpoints meet latency targets (see table in "Business Context")
- [ ] Database queries optimized (all use Index Scan)
- [ ] Frontend meets Lighthouse budgets (Performance Score ≥90)
- [ ] Cache hit rates meet targets (Redis ≥95%, Claude ≥40%)
- [ ] Baselines measured and saved (baselines/baseline.json)

#### Deployment

- [ ] GitHub Actions workflow created (`.github/workflows/performance-tests.yml`)
- [ ] Lighthouse CI workflow created (`.github/workflows/lighthouse-ci.yml`)
- [ ] Test database seeding script ready (`tests/performance/seed_test_data.py`)
- [ ] Performance budgets configured (`frontend/lighthouse-budget.json`)

#### Post-Deployment

- [ ] Workflow triggers on PR (verified)
- [ ] Workflow posts PR comment with results (verified)
- [ ] Workflow blocks PR merge if regression detected (verified)
- [ ] Daily cron job runs successfully (verified after 24 hours)
- [ ] Performance dashboard accessible (Grafana - optional)

---

### Success Validation

**This PRD is considered COMPLETE when**:

1. ✅ **All Acceptance Criteria Met** (100%)
   - All functional requirements implemented
   - All quality requirements satisfied
   - All performance targets met
   - All security checks passed

2. ✅ **All Tests Passing** (100% pass rate)
   - Locust load tests: 4 scenarios passing
   - Database profiling: All queries optimized
   - Lighthouse CI: All pages meet budgets
   - Caching tests: Hit rates meet targets

3. ✅ **CI/CD Integration Complete**
   - GitHub Actions workflow running
   - PR blocking on regression working
   - Performance reports generated

4. ✅ **Documentation Complete**
   - Performance testing guide written
   - Troubleshooting guide written
   - Architecture decisions documented

5. ✅ **Production Readiness Validated**
   - 100 concurrent users supported without degradation
   - All endpoints meet latency targets under load
   - No critical bottlenecks identified

6. ✅ **FINAL MILESTONE**: PRD 14 of 14 Complete (100% of EMR Project)
   - This is the FINAL PRD in the 14-PRD sequence
   - All backend PRDs complete (4/4)
   - All frontend PRDs complete (4/4)
   - All integration PRDs complete (2/2)
   - All testing PRDs complete (3/3)

**Sign-off Required From**:
- [ ] DevOps Engineer (CI/CD integration verified)
- [ ] QA Engineer (all performance tests passing)
- [ ] Backend Engineer (database queries optimized)
- [ ] Frontend Engineer (Lighthouse budgets met)
- [ ] PM Coordinator (production readiness confirmed)

---

## 📎 Appendices

### Appendix A: Performance Test Report Example

```
========================================
PERFORMANCE TEST REPORT
========================================
Date: 2026-02-16 10:30:00 UTC
Test: Scenario 2 - Peak Load (100 concurrent users)
Duration: 10 minutes
Backend: http://localhost:8001
========================================

API ENDPOINT PERFORMANCE (p95 latency):
----------------------------------------
POST /api/v1/emr/sessions/start
  - Requests: 2,500
  - Success Rate: 100%
  - p50: 120ms
  - p95: 178ms ✅ (target: <500ms)
  - p99: 245ms

PUT /api/v1/emr/sessions/{id}
  - Requests: 10,000
  - Success Rate: 100%
  - p50: 95ms
  - p95: 142ms ✅ (target: <200ms)
  - p99: 189ms

POST /api/v1/emr/sessions/{id}/submit
  - Requests: 1,000
  - Success Rate: 100%
  - p50: 650ms
  - p95: 875ms ✅ (target: <1s)
  - p99: 1,120ms

POST /api/v1/emr/validation/soap
  - Requests: 500
  - Success Rate: 100%
  - p50: 3,800ms
  - p95: 4,200ms ✅ (target: 3-5s)
  - p99: 4,850ms

GET /api/v1/progress/dashboard/emr
  - Requests: 3,000
  - Success Rate: 100%
  - p50: 65ms
  - p95: 87ms ✅ (target: <200ms)
  - p99: 112ms

========================================
DATABASE PERFORMANCE:
----------------------------------------
Dashboard Analytics Query: 1,780ms ✅ (target: <2s)
Specialty Breakdown Query: 920ms ✅ (target: <1s)
Learning Velocity Query: 1,350ms ✅ (target: <1.5s)
Auto-Save UPDATE: 42ms ✅ (target: <50ms)

All queries use Index Scan ✅

pgBench Workload:
  - TPS: 1,247 ✅ (target: >1000)
  - Latency Avg: 40.2ms ✅ (target: <50ms)

========================================
CACHE PERFORMANCE:
----------------------------------------
Redis Cache Hit Rate: 96.2% ✅ (target: ≥95%)
  - Hits: 28,850
  - Misses: 1,150
  - Total: 30,000

Claude API Cache Hit Rate: 42.5% ✅ (target: ≥40%)
  - Hits: 42
  - Misses: 58
  - Total: 100
  - Cost Savings: 42% reduction (~$0.13 saved)

========================================
OVERALL RESULT: ✅ ALL TARGETS MET
========================================
```

### Appendix B: Regression Report Example

```json
{
  "date": "2026-02-16T10:30:00Z",
  "commit": "b2c3d4e",
  "baseline_commit": "a1b2c3d",
  "overall_status": "REGRESSION_DETECTED",
  "regressions": [
    {
      "endpoint": "POST /api/v1/emr/sessions/start",
      "current_p95": 245,
      "baseline_p95": 178,
      "increase_pct": 37.6,
      "threshold_pct": 20,
      "severity": "HIGH"
    }
  ],
  "endpoints": [
    {
      "name": "POST /api/v1/emr/sessions/start",
      "current_p95": 245,
      "baseline_p95": 178,
      "target": 500,
      "passed": false,
      "regression": true
    },
    {
      "name": "PUT /api/v1/emr/sessions/{id}",
      "current_p95": 142,
      "baseline_p95": 138,
      "target": 200,
      "passed": true,
      "regression": false
    }
  ]
}
```

### Appendix C: Lighthouse Budget Configuration

```json
{
  "path": "/*",
  "resourceSizes": [
    {
      "resourceType": "script",
      "budget": 300
    },
    {
      "resourceType": "stylesheet",
      "budget": 50
    },
    {
      "resourceType": "image",
      "budget": 100
    },
    {
      "resourceType": "font",
      "budget": 100
    },
    {
      "resourceType": "document",
      "budget": 30
    },
    {
      "resourceType": "total",
      "budget": 600
    }
  ],
  "timings": [
    {
      "metric": "first-contentful-paint",
      "budget": 1500
    },
    {
      "metric": "interactive",
      "budget": 3000
    },
    {
      "metric": "speed-index",
      "budget": 2500
    },
    {
      "metric": "largest-contentful-paint",
      "budget": 2500
    },
    {
      "metric": "cumulative-layout-shift",
      "budget": 0.1
    },
    {
      "metric": "total-blocking-time",
      "budget": 300
    }
  ]
}
```

### Appendix D: Related PRDs

**Depends On**:
- **PRD_BACKEND_001**: EMR Database Migration (database schema, indexes)
- **PRD_BACKEND_002**: EMR Session Management API (auto-save endpoints)
- **PRD_BACKEND_003**: EMR Validation API (Claude API caching)
- **PRD_FRONTEND_003**: EMR Dashboard Integration (chart render performance)
- **PRD_INTEGRATION_002**: Unified Progress Tracking (Redis cache hit rate)

**Blocks**:
- **Production Deployment**: Cannot deploy without performance validation
- **Scalability Planning**: Performance data needed for capacity planning

**Related**:
- **PRD_TESTING_001**: Unit + Integration Testing (functional correctness)
- **PRD_TESTING_002**: E2E Testing (user workflows)

---

**Document Status**: Ready for Implementation (FINAL PRD - 14 of 14)

**Created**: 2026-02-16
**Last Updated**: 2026-02-16
**Approved By**: PM Coordinator
**Version**: 1.0

---

## 🎉 FINAL PRD COMPLETE - 100% PROJECT COVERAGE

**PRD Completion Status**:
- ✅ Backend PRDs: 4/4 (100%)
  - PRD_BACKEND_001: EMR Database Migration
  - PRD_BACKEND_002: EMR Session Management API
  - PRD_BACKEND_003: EMR Validation API
  - PRD_BACKEND_004: OSCE-EMR Converter

- ✅ Frontend PRDs: 4/4 (100%)
  - PRD_FRONTEND_001: Epic EHR UI Migration
  - PRD_FRONTEND_002: Cerner PowerChart UI Components
  - PRD_FRONTEND_003: EMR Dashboard Integration
  - PRD_FRONTEND_004: EMR Validation Display

- ✅ Integration PRDs: 2/2 (100%)
  - PRD_INTEGRATION_001: OSCE-EMR Video Linking
  - PRD_INTEGRATION_002: Unified Progress Tracking

- ✅ Testing PRDs: 3/3 (100%)
  - PRD_TESTING_001: Unit + Integration Tests
  - PRD_TESTING_002: E2E Testing (Playwright)
  - **PRD_TESTING_003: Performance Benchmarking (THIS PRD - FINAL)**

**Total PRDs: 14/14 (100%)**

**Next Steps**:
1. Review all 14 PRDs with PM Coordinator
2. Prioritize implementation order (P0 → P1 → P2 → P3)
3. Assign PRDs to expert agents (Backend, Frontend, DevOps, QA)
4. Begin implementation with PRD_BACKEND_001 (Database Migration)
5. Deploy to production after all acceptance criteria met

**Production Readiness**:
- With this PRD complete, the EMR Practice System has **complete performance validation coverage**
- All performance targets defined, measured, and enforced
- CI/CD integration ensures no performance regressions
- Production deployment blocked until all performance tests pass

🚀 **Ready to build a world-class EMR practice system for Australian medical students!**

