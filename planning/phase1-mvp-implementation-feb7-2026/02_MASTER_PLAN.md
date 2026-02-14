# Phase 1 MVP Implementation - Master Plan
## irStudy Medical Education Platform

**Version:** 1.0
**Date:** 2026-02-07
**Duration:** 3 weeks (Feb 7-27, 2026)
**Status:** 🟡 Ready for Execution

---

## 📋 Executive Summary

### Mission Statement

Deliver a **production-ready medical education platform** for Australian Medical Council (AMC) exam preparation in 3 weeks, featuring 1,208 MCQs, 210 OSCEs, 140 Study Cards with SM-2 spaced repetition, and 3,168 medical images, all validated for Australian medical context.

### Strategic Objectives

1. **Security First:** Zero P0/P1 vulnerabilities, HIPAA-compliant architecture
2. **Australian Medical Context:** 100% validation (drug names, citations, guidelines)
3. **Performance:** API <200ms, page load <2s, 500 concurrent users supported
4. **Quality:** 100% test pass rate, >70% code coverage, Lighthouse score >90
5. **User Experience:** 50 beta users onboarded, >80% satisfaction

---

## 🎯 Success Criteria

**Phase 1 MVP is complete when ALL of the following are achieved:**

### Infrastructure ✅ (Already Complete)
- [x] PostgreSQL operational (port 5433, database: `irstudy_medical`)
- [x] Redis cluster operational (6 nodes)
- [x] Qdrant vector database operational (port 6333)
- [x] Vault secrets management (port 8200)
- [x] Database content: 1,208 MCQs, 210 OSCEs, 140 Study Cards
- [x] Image library: 3,168 medical images (50.3% of 6,300 target)

### Backend (Week 1) ⏳
- [ ] All 5 backend tasks completed (TASK_001-005)
- [ ] 100% test pass rate (pytest)
- [ ] Zero P0/P1 security vulnerabilities (Bandit + Safety)
- [ ] API response time <200ms (95th percentile)
- [ ] Australian drug name validation operational
- [ ] Citation verification (eTG, PBS, AMH, AHPRA)

### Frontend (Week 2) ⏳
- [ ] All 4 frontend tasks completed (TASK_006-009)
- [ ] Lighthouse score >90 (mobile + desktop)
- [ ] All 3,168 images loading correctly
- [ ] TypeScript type checking: 0 errors
- [ ] Mobile-responsive design (320px, 768px, 1024px breakpoints)
- [ ] PWA configuration complete

### Integration (Week 3) ⏳
- [ ] E2E test suite: 100% pass rate (20+ scenarios)
- [ ] Load testing: 500 concurrent users, <2s page load
- [ ] Production deployment successful (Railway + Vercel)
- [ ] 50 beta users onboarded and active
- [ ] Monitoring operational (Sentry + Prometheus)

### Final Validation ⏳
- [ ] Zero downtime in first week of production
- [ ] User satisfaction >80% (beta survey)
- [ ] Australian medical context: 100% validated
- [ ] All quality gates passed

---

## 📊 Project Overview

### Timeline

| Week | Focus | Tasks | Duration | Target Completion |
|------|-------|-------|----------|-------------------|
| **Week 1** | Backend Foundation | 5 tasks (TASK_001-005) | 22-29 hours | Feb 13, 2026 |
| **Week 2** | Frontend Core | 4 tasks (TASK_006-009) | 21-27 hours | Feb 20, 2026 |
| **Week 3** | Integration & Polish | 5 tasks (TASK_010-014) | 24-31 hours | Feb 27, 2026 |
| **TOTAL** | **14 tasks** | **14 tasks** | **67-87 hours** | **Feb 27, 2026** |

**Critical Path:** 43-55 hours (7-9 working days)
**Buffer:** 8 days (53% slack built into schedule)

---

### Resource Allocation

| Role | Tasks | Effort | Agent Type |
|------|-------|--------|------------|
| **Security Expert** | TASK_001 | 6-8 hours | security-compliance-expert + rust-ffi-expert |
| **Backend Developer** | TASK_002, 003, 004, 005, 011, 012 (partial) | 33-41 hours | general-purpose agent (Python/FastAPI) |
| **Frontend Developer** | TASK_006, 007, 008, 009 | 21-27 hours | flutter-desktop-expert (React/TypeScript) |
| **QA Engineer** | TASK_010, 012 (partial), 014 (partial) | 12-16 hours | testing-qa-expert |
| **DevOps Engineer** | TASK_013 | 5-6 hours | general-purpose agent (DevOps) |
| **Project Manager** | TASK_014 (partial), coordination | 6-8 hours | project-manager-coordinator |

**Recommended Team Size:** 2-3 agents working concurrently
**Parallelization Opportunities:** 18-23 hours time savings

---

### Budget Estimate

**Total Effort:** 67-87 hours
**Parallelization Savings:** -18-23 hours
**Actual Work Time:** 49-64 hours
**Hourly Rate:** $50/hour (estimated)
**Total Cost:** **$2,450 - $3,200**

---

## 🗺️ Week-by-Week Breakdown

### Week 1: Backend Foundation (Feb 7-13)

**Objective:** Secure, tested backend APIs for MCQs, OSCEs, Study Cards, and Progress Tracking

#### TASK_001: API Security Audit (Day 1-2)
- **Duration:** 6-8 hours
- **Owner:** security-compliance-expert + rust-ffi-expert
- **Deliverables:**
  - Security audit report (Bandit + Safety scans)
  - Zero P0/P1 vulnerabilities
  - OWASP Top 10 compliance verified
  - CI/CD security scan integration

#### TASK_002: Question Management CRUD (Day 3-4)
- **Duration:** 6-8 hours
- **Owner:** general-purpose agent (Python/FastAPI)
- **Deliverables:**
  - MCQ endpoints: GET /random, POST /submit-answer, GET /explanations
  - OSCE endpoints: GET /random, POST /complete-station
  - Australian drug name validation
  - 100% test coverage

#### TASK_003: Study Card System (Day 3-4, parallel with TASK_002)
- **Duration:** 4-5 hours
- **Owner:** general-purpose agent (Python/FastAPI)
- **Deliverables:**
  - Study Card endpoints: GET /due-cards, POST /review
  - SM-2 algorithm integration
  - Review history tracking

#### TASK_004: User Progress Tracking (Day 5)
- **Duration:** 4-5 hours
- **Owner:** general-purpose agent (Python/FastAPI)
- **Deliverables:**
  - Progress endpoints: GET /dashboard, GET /weak-areas
  - Specialty-based insights
  - Weekly/monthly trends

#### TASK_005: Spaced Repetition Engine (Day 5, parallel with TASK_004)
- **Duration:** 3-4 hours
- **Owner:** general-purpose agent (Python/FastAPI)
- **Deliverables:**
  - Optimized SM-2 algorithm
  - Daily review queue generation
  - Performance optimization (<100ms)

**Week 1 Quality Gate:**
- All backend APIs operational
- 100% test pass rate
- Zero security vulnerabilities
- API response time <200ms

---

### Week 2: Frontend Core (Feb 14-20)

**Objective:** Modern, mobile-responsive frontend interfaces for all user-facing features

#### TASK_006: Quiz Interface Redesign (Day 1-2)
- **Duration:** 8-10 hours
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Deliverables:**
  - React component: `<MCQPracticeInterface />`
  - Timer, image lightbox, answer submission
  - Material-UI v6 design system
  - TypeScript: 0 errors

#### TASK_007: Citation Display Component (Day 3)
- **Duration:** 3-4 hours
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Deliverables:**
  - React component: `<CitationPanel />`
  - Formatted eTG, PBS, AMH, AHPRA guidelines
  - RAG verification badge

#### TASK_008: Performance Dashboard (Day 4)
- **Duration:** 6-8 hours
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Deliverables:**
  - React page: `<DashboardPage />`
  - Performance charts (Recharts)
  - Specialty breakdown, weak area highlights

#### TASK_009: Mobile Responsive Design (Day 5)
- **Duration:** 4-5 hours
- **Owner:** flutter-desktop-expert (React/TypeScript)
- **Deliverables:**
  - Mobile breakpoints (320px, 768px, 1024px)
  - PWA configuration
  - Lighthouse score >90

**Week 2 Quality Gate:**
- All frontend interfaces complete
- Lighthouse score >90
- All images loading
- TypeScript: 0 errors
- Mobile-responsive verified

---

### Week 3: Integration & Polish (Feb 21-27)

**Objective:** Production-ready deployment with comprehensive testing and monitoring

#### TASK_010: E2E Testing Suite (Day 1-2)
- **Duration:** 6-8 hours
- **Owner:** testing-qa-expert
- **Deliverables:**
  - Playwright test suite (20+ scenarios)
  - Critical paths: MCQ practice, OSCE practice, Study Cards
  - CI/CD integration (GitHub Actions)

#### TASK_011: RAG Explanation Engine (Day 1-2, parallel with TASK_010)
- **Duration:** 5-6 hours
- **Owner:** general-purpose agent (Python/RAG)
- **Deliverables:**
  - RAG query service (Qdrant integration)
  - Enhanced MCQ explanations
  - Query latency <500ms

#### TASK_012: Load Testing & Optimization (Day 3)
- **Duration:** 4-5 hours
- **Owner:** testing-qa-expert + general-purpose agent
- **Deliverables:**
  - Locust test scenarios (50-500 users)
  - Performance benchmarks met
  - Redis caching, database optimization

#### TASK_013: Deployment Pipeline (Day 4)
- **Duration:** 5-6 hours
- **Owner:** general-purpose agent (DevOps)
- **Deliverables:**
  - GitHub Actions workflows (Test → Build → Deploy)
  - Railway deployment (backend)
  - Vercel deployment (frontend)
  - Health check endpoints

#### TASK_014: MVP Validation & Launch (Day 5)
- **Duration:** 4-5 hours
- **Owner:** project-manager-coordinator + testing-qa-expert
- **Deliverables:**
  - 50 beta users onboarded
  - UAT completion
  - Production monitoring (Sentry + Prometheus)
  - Beta feedback survey

**Week 3 Quality Gate (FINAL):**
- E2E tests: 100% pass rate
- Load test: 500 users, <2s page load
- Production deployment successful
- 50 beta users active
- Zero P0/P1 bugs

---

## 🏗️ Architecture Overview

### Tech Stack

**Frontend:**
- Framework: React 19.2 + TypeScript 5.3+
- Build Tool: Vite 5.0+
- UI Library: Material-UI v6 (Material Design 3)
- State Management: TanStack Query v5
- Routing: React Router v6
- Charts: Recharts v2
- Testing: Vitest + Playwright
- Deployment: Vercel

**Backend:**
- Framework: FastAPI + Python 3.11+
- Database: PostgreSQL 16 (SQLAlchemy ORM)
- Cache: Redis Cluster (6 nodes)
- Vector DB: Qdrant (RAG knowledge base)
- Secrets: HashiCorp Vault
- Task Queue: Celery (for async tasks)
- Testing: pytest + coverage
- Deployment: Railway

**Infrastructure:**
- Authentication: JWT (HS256)
- API Documentation: OpenAPI/Swagger
- Monitoring: Sentry (errors) + Prometheus (metrics)
- CI/CD: GitHub Actions
- Image CDN: Cloudflare or similar

---

### Database Schema

**Core Tables:**
- `users` - User accounts with bcrypt password hashing
- `mcqs` - Multiple choice questions (1,208 records)
- `osces` - OSCE scenarios (210 records)
- `study_cards` - Flashcards with SM-2 algorithm (140 records)
- `mcq_attempts` - User practice tracking
- `user_progress` - Performance analytics

**Key Fields:**
- Australian context validation: `australian_guidelines` (JSON)
- SM-2 spaced repetition: `next_review_date`, `interval_days`, `ease_factor`, `repetitions`
- Performance tracking: `correct_ratio`, `time_spent`, `specialty_performance`

---

### API Endpoints (Summary)

**Authentication:**
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - JWT token issuance
- `POST /api/v1/auth/refresh` - Refresh token rotation

**MCQs:**
- `GET /api/v1/mcqs/random` - Get random MCQ (filtered by specialty/difficulty)
- `POST /api/v1/mcqs/{id}/submit` - Submit answer, get feedback
- `GET /api/v1/mcqs/{id}/explanation` - Get detailed explanation with citations

**OSCEs:**
- `GET /api/v1/osces/random` - Get random OSCE scenario
- `POST /api/v1/osces/{id}/complete` - Submit completion, get rubric feedback

**Study Cards:**
- `GET /api/v1/cards/due` - Get cards due for review (SM-2 algorithm)
- `POST /api/v1/cards/{id}/review` - Submit review, update SM-2 schedule
- `GET /api/v1/cards/statistics` - Get review statistics

**Progress:**
- `GET /api/v1/progress/dashboard` - Get overall performance dashboard
- `GET /api/v1/progress/specialty/{name}` - Get specialty-specific insights
- `GET /api/v1/progress/weak-areas` - Identify weak areas for targeted study

---

## 🔒 Security Framework

### 6-Layer Security Architecture

**Layer 1: Network Security**
- HTTPS enforced (TLS 1.3)
- CORS with explicit allowed origins (no wildcard)
- CSP headers (Content Security Policy)
- Rate limiting: 20 req/min (anonymous), 60 req/min (authenticated)

**Layer 2: Authentication & Authorization**
- JWT tokens (HS256, 30 min expiration)
- Refresh token rotation (7 days)
- Account lockout: 5 failed attempts = 30 min lockout
- Password policy: ≥12 chars, uppercase, lowercase, digit, special

**Layer 3: Data Protection**
- Passwords: bcrypt hashing (cost factor 12)
- Sensitive data: AES-256-GCM encryption
- Database: PostgreSQL with row-level security
- Secrets: HashiCorp Vault (not environment variables in production)

**Layer 4: Input Validation**
- Pydantic schemas on ALL endpoints
- Australian drug name validation (reject American terms)
- SQL injection prevention (parameterized queries only)
- XSS prevention (HTML sanitization)

**Layer 5: Audit & Monitoring**
- Security event logging (failed logins, access denials)
- Log retention: 365 days
- Sentry error tracking
- Prometheus metrics (API response times, error rates)

**Layer 6: Compliance**
- OWASP Top 10 2021 compliance
- HIPAA-ready architecture (though current data is non-PHI educational content)
- Australian AHPRA standards validation
- Zero-tolerance for P0/P1 vulnerabilities

---

## 📊 Quality Assurance Framework

### Testing Strategy

**Unit Testing:**
- Backend: pytest with >70% coverage
- Frontend: Vitest with >70% coverage
- Target: 100% pass rate (zero tolerance for failing tests)

**Integration Testing:**
- API contract testing (OpenAPI spec validation)
- Database integration tests (PostgreSQL test database)
- Redis caching tests

**End-to-End Testing:**
- Playwright test suite (20+ scenarios)
- Critical user journeys: Registration → MCQ practice → Results
- Cross-browser testing (Chrome, Firefox, Safari)

**Performance Testing:**
- Load testing: Locust (50-500 concurrent users)
- API response time: <200ms (95th percentile)
- Page load time: <2s
- Database query optimization

**Security Testing:**
- Automated: Bandit + Safety scans
- Manual: OWASP Top 10 verification
- CI/CD integration: Fail build on HIGH/CRITICAL issues

---

### Quality Gates

**Gate 1: Week 1 Complete (Feb 13)**
- [ ] All 5 backend tasks completed
- [ ] 100% test pass rate
- [ ] Zero P0/P1 vulnerabilities
- [ ] API response time <200ms

**Gate 2: Week 2 Complete (Feb 20)**
- [ ] All 4 frontend tasks completed
- [ ] Lighthouse score >90
- [ ] TypeScript: 0 errors
- [ ] Mobile-responsive verified

**Gate 3: Week 3 Complete (Feb 27) - FINAL GATE**
- [ ] E2E tests: 100% pass
- [ ] Load test: 500 users OK
- [ ] Production deployment successful
- [ ] 50 beta users active

---

## 🚨 Risk Register (Top 5 Risks)

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **TASK_001 discovers major security flaws** | Medium (30%) | High | Allocate 2 expert agents, split into critical/nice-to-have fixes |
| **TASK_002 API contract changes mid-dev** | Low (15%) | High | Define OpenAPI spec upfront, freeze after Day 1 |
| **TASK_010 E2E tests reveal critical bugs** | Medium (40%) | Medium | Run smoke tests after TASK_006/008, don't wait for Week 3 |
| **Image linking not ready by Week 2** | Medium (35%) | Low | Proceed with placeholder images, integrate later |
| **Load testing reveals performance issues** | Medium (30%) | Medium | Redis caching + database optimization in TASK_012 |

**Escalation:** P0 risks → Immediate PM notification, P1 risks → Daily standup review

---

## 📈 Success Metrics (KPIs)

### Performance Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| API Response Time (95th %) | Unknown | <200ms | Prometheus |
| Page Load Time | Unknown | <2s | Lighthouse |
| Uptime (Week 1) | 0% | >99% | Uptime monitoring |
| Load Test Capacity | Unknown | 500 users | Locust |

### Quality Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Test Pass Rate | Unknown | 100% | CI/CD |
| Code Coverage | Unknown | >70% | pytest-cov |
| Security Vulnerabilities (P0/P1) | Unknown | 0 | Bandit + Safety |
| Lighthouse Score (Mobile) | Unknown | >90 | Lighthouse |

### User Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Beta Users Onboarded | 0 | 50 | Manual tracking |
| User Satisfaction | Unknown | >80% | Survey |
| Retention Rate (Week 1) | Unknown | >70% | Analytics |
| Support Tickets | 0 | <10 | GitHub Issues |

---

## 🤝 Stakeholder Communication

### Daily Standups (15 minutes)

**When:** Daily, 9:00 AM
**Who:** All agents + PM
**Format:**
1. What did you complete yesterday?
2. What are you working on today?
3. Any blockers?
4. Update [04_TASK_CHECKLIST.md](./04_TASK_CHECKLIST.md)

### Weekly Reviews (60 minutes)

**Week 1 Review (Feb 13, 5:00 PM):**
- Backend demo (all APIs operational)
- Security audit report review
- Quality Gate 1 validation
- Week 2 planning confirmation

**Week 2 Review (Feb 20, 5:00 PM):**
- Frontend demo (all interfaces functional)
- Performance testing results
- Quality Gate 2 validation
- Week 3 planning confirmation

**Week 3 Review (Feb 27, 5:00 PM):**
- Production deployment demo
- Beta user feedback review
- Final Quality Gate validation
- Phase 2 planning kickoff

---

## 📞 Support & Escalation

**For Technical Issues:**
- Review [02_MASTER_PLAN.md](./02_MASTER_PLAN.md) Architecture section
- Check `constraints/README.md` for project-specific patterns
- Search existing codebase for similar implementations

**For Task Clarification:**
- Read full `TASK_XXX.md` file
- Check [DEPENDENCIES_MAP.md](./DEPENDENCIES_MAP.md) for prerequisites
- Review [DELEGATION_GUIDE.md](./DELEGATION_GUIDE.md) for Agent OS templates

**For Blockers:**
- Flag in daily standup
- Update [RISK_REGISTER.md](./RISK_REGISTER.md)
- Escalate P0 issues to PM immediately

---

## 🎯 Next Actions

**Immediate (Today):**
1. Review this master plan (20 min)
2. Read [DEPENDENCIES_MAP.md](./DEPENDENCIES_MAP.md) (5 min)
3. Read [TASK_001_API_SECURITY_AUDIT.md](./TASK_001_API_SECURITY_AUDIT.md) (12 min)
4. Start TASK_001 execution (delegate to security-compliance-expert)

**Week 1 (Feb 7-13):**
1. Complete all 5 backend tasks
2. Pass Quality Gate 1
3. Prepare for frontend development (Week 2)

**Week 2 (Feb 14-20):**
1. Complete all 4 frontend tasks
2. Pass Quality Gate 2
3. Prepare for integration testing (Week 3)

**Week 3 (Feb 21-27):**
1. Complete all 5 integration tasks
2. Pass Final Quality Gate
3. Launch to 50 beta users

---

**Last Updated:** 2026-02-07
**Status:** 🟡 Ready for Execution
**Next Review:** 2026-02-13 (Week 1 Checkpoint)
**Maintained By:** Project Manager
