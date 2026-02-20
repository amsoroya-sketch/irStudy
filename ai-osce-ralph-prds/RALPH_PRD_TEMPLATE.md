# RALPH PRD Template

**PRD ID**: PRD_[CATEGORY]_[NUMBER]_[SHORT_NAME]
**Category**: [Backend | Frontend | Integration | Testing]
**Priority**: [P0-Critical | P1-High | P2-Medium | P3-Low]
**Estimated Effort**: [X-Y hours]
**Dependencies**: [List of PRD IDs that must complete first]
**Status**: [Not Started | In Progress | Under Review | Complete]

---

## R - REQUEST (What & Why)

### User Story
**As a** [user type]
**I want** [capability]
**So that** [business value]

### Business Context
[Explain why this feature is needed, what problem it solves, and how it fits into the larger product vision]

### Success Metrics
- **Metric 1**: [Quantifiable target, e.g., "API response time <200ms"]
- **Metric 2**: [User-facing outcome, e.g., "95% user satisfaction"]
- **Metric 3**: [Quality gate, e.g., "100% test pass rate"]

### Scope
**In Scope**:
- [Feature/capability 1]
- [Feature/capability 2]
- [Feature/capability 3]

**Out of Scope** (Future Iterations):
- [Deferred feature 1]
- [Deferred feature 2]

---

## A - ARCHITECTURE (How)

### Technical Approach
[High-level description of the technical solution]

### System Design

#### Component Diagram
```
[Visual representation of components and their relationships]
```

#### Data Flow
```
User Input → [Component A] → [Component B] → [Storage/API] → Response
```

#### Database Schema Changes (if applicable)
```sql
-- New tables, columns, indexes, triggers
CREATE TABLE example (
    id UUID PRIMARY KEY,
    ...
);
```

#### API Endpoints (if applicable)
```
POST   /api/v1/resource       - Create resource
GET    /api/v1/resource/:id   - Get resource
PUT    /api/v1/resource/:id   - Update resource
DELETE /api/v1/resource/:id   - Delete resource
```

### Technology Stack
- **Language/Framework**: [e.g., Python 3.11 + FastAPI]
- **Database**: [e.g., PostgreSQL 15]
- **Libraries**: [e.g., SQLAlchemy, Pydantic, pytest]
- **Tools**: [e.g., Alembic, Docker]

### Integration Points
- **Integrates with**: [Existing systems, APIs, services]
- **Consumed by**: [Frontend components, other services]
- **Depends on**: [External services, databases]

### Security Considerations
- [ ] Input validation (Pydantic schemas)
- [ ] Authentication (JWT required)
- [ ] Authorization (role-based access)
- [ ] Encryption (data at rest/in transit)
- [ ] No hardcoded credentials
- [ ] Secrets managed via Vault

### Performance Requirements
- **API Response Time**: [<200ms p95]
- **Database Query Time**: [<50ms]
- **Concurrent Users**: [100+ supported]
- **Throughput**: [X requests/second]

---

## L - LOOP (Iterative Development)

### Phase 1: Foundation (XX% of effort)
**Goal**: [Establish core infrastructure/skeleton]

**Tasks**:
1. [Task 1: Setup/scaffolding] - [X hours]
2. [Task 2: Database schema] - [Y hours]
3. [Task 3: Basic models] - [Z hours]

**Validation Gate**:
- [ ] Database migrations run successfully
- [ ] Models created and tested
- [ ] No compilation errors
- [ ] Basic smoke tests passing

---

### Phase 2: Core Functionality (XX% of effort)
**Goal**: [Implement main features]

**Tasks**:
1. [Task 4: API endpoint implementation] - [X hours]
2. [Task 5: Business logic] - [Y hours]
3. [Task 6: Validation rules] - [Z hours]
4. [Task 7: Integration with existing systems] - [W hours]

**Validation Gate**:
- [ ] All API endpoints working
- [ ] Unit tests ≥70% coverage
- [ ] Integration tests passing
- [ ] Manual testing successful
- [ ] Security scan (0 HIGH/CRITICAL)

---

### Phase 3: Polish & Optimization (XX% of effort)
**Goal**: [Production-ready quality]

**Tasks**:
1. [Task 8: Performance optimization] - [X hours]
2. [Task 9: Error handling and edge cases] - [Y hours]
3. [Task 10: Documentation] - [Z hours]
4. [Task 11: E2E testing] - [W hours]

**Validation Gate**:
- [ ] Performance benchmarks met
- [ ] 100% test pass rate
- [ ] Edge cases handled
- [ ] Documentation complete
- [ ] Production deployment successful

---

## P - PLAN (Detailed Implementation)

### Task Breakdown (1-2 hour chunks)

#### Phase 1 Tasks
**Task 1.1**: [Specific action]
- **Effort**: [30-60 min]
- **Owner**: [Agent type or developer]
- **Deliverable**: [File created, code written, test passing]
- **Dependencies**: None
- **Acceptance Criteria**:
  - [ ] [Specific testable outcome 1]
  - [ ] [Specific testable outcome 2]

**Task 1.2**: [Next specific action]
- **Effort**: [1-2 hours]
- **Owner**: [Agent type]
- **Deliverable**: [Concrete output]
- **Dependencies**: Task 1.1
- **Acceptance Criteria**:
  - [ ] [Outcome 1]
  - [ ] [Outcome 2]

[Continue for all tasks in Phase 1, then Phase 2, then Phase 3]

---

### Dependency Graph
```
Task 1.1 (Foundation)
    ↓
Task 1.2 (Schema)
    ↓
Task 2.1 (API) ←─┐
    ↓            │
Task 2.2 (Logic) │
    ↓            │
Task 2.3 (Tests)─┘
    ↓
Task 3.1 (Optimization)
    ↓
Task 3.2 (Documentation)
    ↓
COMPLETE
```

---

### Resource Allocation

| Role | Effort (hours) | Tasks |
|------|----------------|-------|
| Backend Engineer | [X hours] | [1.1, 1.2, 2.1, 2.2] |
| Security Expert | [Y hours] | [Security review, audit] |
| Testing QA | [Z hours] | [2.3, 3.1, E2E tests] |
| PM Coordinator | [W hours] | [Review, validation gates] |

---

### Timeline (Example)

| Day | Phase | Tasks | Deliverable |
|-----|-------|-------|-------------|
| Day 1 | Phase 1 | 1.1, 1.2 | Database schema created |
| Day 2 | Phase 1 | 1.3 | Models implemented |
| Day 3 | Phase 2 | 2.1, 2.2 | API endpoints working |
| Day 4 | Phase 2 | 2.3 | Tests passing |
| Day 5 | Phase 3 | 3.1, 3.2 | Production-ready |

---

## H - HANDOFF (Delivery & Validation)

### Acceptance Criteria (MUST ALL PASS)

#### Functional Requirements
- [ ] [Feature 1 works as specified]
- [ ] [Feature 2 works as specified]
- [ ] [Integration with system X successful]
- [ ] [Edge case Y handled correctly]

#### Quality Requirements
- [ ] **Test Coverage**: ≥70% (unit + integration)
- [ ] **Test Pass Rate**: 100% (zero tolerance)
- [ ] **Code Quality**: No linting errors, follows style guide
- [ ] **Documentation**: All endpoints/functions documented

#### Performance Requirements
- [ ] **API Response Time**: <200ms (p95)
- [ ] **Database Queries**: <50ms
- [ ] **Load Testing**: 100+ concurrent users supported

#### Security Requirements
- [ ] **No Hardcoded Credentials**: Grep scan passes
- [ ] **Input Validation**: All inputs validated (Pydantic)
- [ ] **Authentication**: JWT on all endpoints
- [ ] **Security Scan**: Bandit/Safety 0 HIGH/CRITICAL

#### Australian Medical Compliance (if applicable)
- [ ] **Terminology**: Australian drug names (paracetamol, salbutamol)
- [ ] **Guidelines**: References eTG/AMH/AHPRA
- [ ] **Standards**: Meets AHPRA documentation requirements
- [ ] **Units**: SI units only (mmol/L, g/L, °C)

---

### Testing Requirements

#### Unit Tests (≥70% coverage target)
```python
# Example test structure
def test_feature_happy_path():
    """Test normal operation"""
    # Arrange
    # Act
    # Assert

def test_feature_edge_case_1():
    """Test edge case handling"""
    # ...

def test_feature_error_handling():
    """Test error conditions"""
    # ...
```

**Minimum Test Cases**:
- [ ] Happy path (normal operation)
- [ ] Edge cases (boundary conditions)
- [ ] Error handling (invalid inputs, exceptions)
- [ ] Integration (interaction with other components)

#### Integration Tests
- [ ] [Test scenario 1: E.g., "Create session → Save note → Submit → Validate"]
- [ ] [Test scenario 2: E.g., "API authentication flow"]
- [ ] [Test scenario 3: E.g., "Database transaction rollback"]

#### E2E Tests (Playwright)
- [ ] [User flow 1: E.g., "Login → Start EMR session → Complete SOAP note"]
- [ ] [User flow 2: E.g., "Submit for validation → View feedback"]

---

### Documentation Deliverables

#### Code Documentation
- [ ] **API Documentation**: OpenAPI/Swagger spec updated
- [ ] **Function Docstrings**: All public functions documented
- [ ] **Inline Comments**: Complex logic explained
- [ ] **README Updates**: Setup/usage instructions

#### Architecture Documentation
- [ ] **Architecture Decision Record (ADR)**: Why this approach chosen
- [ ] **Database Schema Diagram**: ER diagram if schema changes
- [ ] **API Flow Diagram**: Request/response flow
- [ ] **Integration Diagram**: How this fits into larger system

#### User Documentation (if user-facing)
- [ ] **User Guide**: How to use the feature
- [ ] **Screenshots/Videos**: Visual demonstration
- [ ] **Troubleshooting Guide**: Common issues and solutions

---

### Deployment Checklist

#### Pre-Deployment
- [ ] All tests passing (100% pass rate)
- [ ] Security audit complete (0 HIGH/CRITICAL)
- [ ] Performance benchmarks met
- [ ] Database migration tested in staging
- [ ] Rollback plan documented

#### Deployment
- [ ] Database migration executed (if applicable)
- [ ] Environment variables configured (Vault)
- [ ] Service deployed to staging
- [ ] Smoke tests in staging pass
- [ ] Deploy to production

#### Post-Deployment
- [ ] Production smoke tests pass
- [ ] Monitoring dashboards show healthy metrics
- [ ] No error spikes in logs
- [ ] Performance metrics within targets
- [ ] Stakeholders notified

---

### Success Validation

**This PRD is considered COMPLETE when**:
1. ✅ All acceptance criteria met (100%)
2. ✅ All tests passing (100% pass rate)
3. ✅ Code reviewed and approved
4. ✅ Security scan passes (0 HIGH/CRITICAL)
5. ✅ Documentation complete
6. ✅ Production deployment successful
7. ✅ Success metrics trending positive

**Sign-off Required From**:
- [ ] PM Coordinator (overall quality)
- [ ] Security Expert (security approval)
- [ ] Testing QA (test coverage and pass rate)
- [ ] Lead Engineer (code review)

---

## 📎 Appendices

### Appendix A: API Request/Response Examples
```json
// Example request
POST /api/v1/resource
{
  "field1": "value1",
  "field2": "value2"
}

// Example response
{
  "id": "uuid",
  "field1": "value1",
  "created_at": "2026-02-16T00:00:00Z"
}
```

### Appendix B: Database Schema (Detailed)
```sql
-- Full table definition with constraints, indexes, triggers
```

### Appendix C: Error Codes
| Code | Message | Description | User Action |
|------|---------|-------------|-------------|
| E001 | Invalid input | Field X missing | Provide field X |
| E002 | Unauthorized | JWT expired | Re-authenticate |

### Appendix D: Related PRDs
- **Depends On**: [PRD_XXX_YYY] - [Brief description]
- **Blocks**: [PRD_AAA_BBB] - [Brief description]
- **Related**: [PRD_CCC_DDD] - [Brief description]

---

**Document Status**: [Draft | Under Review | Approved | In Progress | Complete]
**Created**: YYYY-MM-DD
**Last Updated**: YYYY-MM-DD
**Approved By**: [Name/Role]
**Version**: 1.0
