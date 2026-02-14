# Week 2 PM Quick Reference Guide

**Sprint**: Week 2 WebSocket Authentication  
**Duration**: 2026-02-07 to 2026-02-17 (10 days)  
**PM Role**: Coordinate specialist agents, enforce quality gates, validate deliverables

---

## Quick Start Commands

### Check Infrastructure Status
```bash
# Redis cluster status
redis-cli -p 7379 ping
redis-cli -p 7380 ping
redis-cli -p 7381 ping

# Vault status
curl http://localhost:8200/v1/sys/health

# PostgreSQL status
psql -h localhost -p 5433 -U iruser -d irdb -c "SELECT version();"
```

### Run Quality Gates
```bash
cd /home/dev/Development/irStudy

# Run all tests
pytest backend/tests/ -v

# Security scan
grep -r "redis://.*:.*@" backend/src/
grep -r "VAULT_.*=\s*\"" backend/src/

# Test coverage
pytest --cov=backend/src --cov-report=term

# Load test
python backend/tests/load_test_websocket.py
```

---

## Task Checklist

### Task 2.1: WebSocket Authenticator ⏳
**Agent**: security-compliance-expert  
**Status**: Not started  
**Estimated**: 6 hours

**Files to Create**:
- [ ] backend/src/websocket/__init__.py
- [ ] backend/src/websocket/authenticator.py
- [ ] backend/src/websocket/rate_limiter.py
- [ ] backend/src/websocket/connection_tracker.py
- [ ] backend/tests/test_websocket_auth.py

**Validation**:
- [ ] pytest backend/tests/test_websocket_auth.py -v (100% pass)
- [ ] Security scan (0 violations)
- [ ] Performance test (p95 <50ms)

### Task 2.2: Security Event Logging ⏳
**Agent**: security-compliance-expert  
**Status**: Not started  
**Estimated**: 4 hours  
**Dependencies**: Task 2.1 complete

**Files to Create**:
- [ ] backend/src/security/__init__.py
- [ ] backend/src/security/events.py
- [ ] backend/tests/test_security_events.py

**Validation**:
- [ ] pytest backend/tests/test_security_events.py -v (100% pass)
- [ ] Vault integration working
- [ ] Prometheus metrics exported

### Task 2.3: Load Testing ⏳
**Agent**: testing-qa-expert  
**Status**: Not started  
**Estimated**: 6 hours  
**Dependencies**: Tasks 2.1 and 2.2 complete

**Files to Create**:
- [ ] backend/tests/test_websocket_integration.py
- [ ] backend/tests/load_test_websocket.py
- [ ] WEEK2_LOAD_TEST_REPORT.md

**Validation**:
- [ ] Load test passes (100 concurrent connections)
- [ ] p95 latency <50ms
- [ ] Rate limiting working
- [ ] Test report generated

### Task 2.4: Documentation ⏳
**Agent**: security-compliance-expert  
**Status**: Not started  
**Estimated**: 2 hours  
**Dependencies**: All tasks complete

**Files to Create**:
- [ ] backend/docs/WEBSOCKET_SECURITY_RUNBOOK.md
- [ ] backend/docs/WEBSOCKET_API.md

**Validation**:
- [ ] Runbook complete with diagrams
- [ ] API docs complete with examples

---

## Validation Scripts

### Pre-Task Validation (Run BEFORE delegating)
```bash
#!/bin/bash
# Check infrastructure ready

echo "Checking Redis..."
redis-cli -p 7379 ping || echo "❌ Redis down"

echo "Checking Vault..."
curl -s http://localhost:8200/v1/sys/health | grep "initialized" || echo "❌ Vault down"

echo "Checking PostgreSQL..."
psql -h localhost -p 5433 -U iruser -d irdb -c "SELECT 1;" > /dev/null 2>&1 || echo "❌ PostgreSQL down"

echo "✅ Infrastructure ready"
```

### Post-Task Validation (Run AFTER agent completes)
```bash
#!/bin/bash
# Validate agent deliverables

echo "Running tests..."
pytest backend/tests/test_websocket_auth.py -v --tb=short

echo "Running security scan..."
violations=$(grep -r "redis://.*:.*@" backend/src/ | wc -l)
if [ "$violations" -eq 0 ]; then
    echo "✅ No hardcoded credentials"
else
    echo "❌ Found $violations hardcoded credentials"
    exit 1
fi

echo "Checking test coverage..."
pytest --cov=backend/src/websocket --cov-report=term --cov-fail-under=80

echo "✅ All validations passed"
```

---

## Common Issues & Solutions

### Issue: Agent returns code with hardcoded credentials
**Solution**:
1. Run security scan: `grep -r "redis://" backend/src/websocket/`
2. Document violations in WEEK2_ISSUES.md
3. Create fix task with specific violations listed
4. Delegate back to same agent with explicit examples

**Example Fix Task**:
```markdown
## Fix Task: Remove Hardcoded Credentials

**Violations Found**:
- backend/src/websocket/authenticator.py:45
  ```python
  redis_client = redis.from_url("redis://localhost:7379")  # ❌ WRONG
  ```

**Fix Required**:
```python
import os
redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:7379")
)
```

**Validation**: Run `grep -r "redis://" backend/src/websocket/` → expect 0 matches
```

### Issue: Tests fail with "Redis connection refused"
**Solution**:
1. Check Redis running: `redis-cli -p 7379 ping`
2. If down, start Docker: `docker-compose up -d redis`
3. Rerun tests

### Issue: Authentication latency >50ms (p95)
**Solution**:
1. Profile code to find bottlenecks
2. Common causes:
   - Multiple Redis round trips (use pipelining)
   - Synchronous operations in async code
   - Heavy JWT signature verification (cache results)
3. Delegate optimization task to agent with profiling data

### Issue: Load test fails (connection timeout)
**Solution**:
1. Check connection limits: `ulimit -n`
2. Increase if needed: `ulimit -n 4096`
3. Check Redis max connections: `redis-cli CONFIG GET maxclients`
4. Rerun load test

---

## Decision Gates

### Gate 1: Proceed to Task 2.2?
**Criteria** (ALL must pass):
- ✅ Task 2.1 tests pass (100%)
- ✅ Security scan clean (0 violations)
- ✅ Performance target met (p95 <50ms)
- ✅ Code review passed

**If ANY fail**: Fix before proceeding

### Gate 2: Proceed to Task 2.3?
**Criteria**:
- ✅ Task 2.2 tests pass (100%)
- ✅ Vault integration working
- ✅ Security events logged correctly

### Gate 3: Proceed to Task 2.4?
**Criteria**:
- ✅ Load test passes (100 connections)
- ✅ p95 latency <50ms
- ✅ Rate limiting working
- ✅ Test report generated

### Gate 4: Sprint Complete?
**Criteria**:
- ✅ All tasks complete
- ✅ All documentation complete
- ✅ All tests passing
- ✅ 0 security violations
- ✅ Performance targets met

---

## Agent Communication Templates

### Delegation Message Template
```markdown
@security-compliance-expert

I'm delegating Task 2.1 (WebSocket Authenticator) to you.

**Task Details**: See WEEK2_TASK_DELEGATION.md section "Task 2.1 Delegation"

**Critical Constraints**:
1. NO hardcoded credentials (read constraints/03-security-configuration.md)
2. Reuse existing JWT functions (backend/src/auth/security.py)
3. Target <50ms authentication latency (p95)

**Validation Required**:
Before returning, YOU must run:
- pytest backend/tests/test_websocket_auth.py -v (expect 100% pass)
- grep -r "redis://" backend/src/websocket/ (expect 0 matches)

**Deliverables**:
1. 4 code files (authenticator.py, rate_limiter.py, connection_tracker.py, test_websocket_auth.py)
2. pytest output (100% pass rate)
3. Security scan output (0 violations)

**Estimated Time**: 6 hours

Let me know if you have questions before starting.
```

### Validation Failure Message Template
```markdown
@security-compliance-expert

Task 2.1 validation FAILED. Issues found:

**Issue 1: Hardcoded Credentials**
- File: backend/src/websocket/authenticator.py
- Line 42: `redis_client = redis.from_url("redis://localhost:7379")`
- Fix: Use `os.getenv("REDIS_URL", "redis://localhost:7379")`

**Issue 2: Test Failure**
- Test: test_authentication_latency_target
- Error: p95 latency 67ms exceeds 50ms target
- Fix: Profile code and optimize (see WEEK2_OPTIMIZATION_SUGGESTIONS.md)

**Next Steps**:
1. Fix both issues
2. Rerun validation checklist
3. Return when all checks pass

Do NOT proceed to Task 2.2 until these are resolved.
```

### Approval Message Template
```markdown
@security-compliance-expert

Task 2.1 APPROVED ✅

**Validation Results**:
- Tests: 12/12 passed (100%)
- Security scan: 0 violations
- Performance: p95 latency 42ms (under 50ms target)
- Code review: Passed

**Next Steps**:
I'm now delegating Task 2.2 (Security Event Logging) to you.
See WEEK2_TASK_DELEGATION.md section "Task 2.2 Delegation".
```

---

## Metrics Dashboard

### Week 2 Sprint Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Test Pass Rate | 100% | TBD | ⏳ |
| Security Violations | 0 | TBD | ⏳ |
| Auth Latency (p95) | <50ms | TBD | ⏳ |
| Concurrent Connections | 100 | TBD | ⏳ |
| Test Coverage | >80% | TBD | ⏳ |
| Tasks Complete | 4/4 | 0/4 | ⏳ |

### Update After Each Task
```bash
# Update metrics
echo "Task 2.1 Complete" >> WEEK2_PROGRESS.md
echo "Test Pass Rate: 100%" >> WEEK2_PROGRESS.md
echo "Auth Latency (p95): 42ms" >> WEEK2_PROGRESS.md
```

---

## Sprint Timeline

```
Week 2 Sprint (10 days)
├─ Day 1-2 (Feb 7-8): Task 2.1 - WebSocketAuthenticator
│  └─ Security-compliance-expert
├─ Day 3-4 (Feb 9-10): Task 2.2 - Security Event Logging
│  └─ Security-compliance-expert
├─ Day 5-6 (Feb 11-12): Task 2.3 - Load Testing
│  └─ Testing-qa-expert
├─ Day 7-8 (Feb 13-14): Task 2.4 - Documentation
│  └─ Security-compliance-expert
├─ Day 9 (Feb 15): Integration & Validation
│  └─ PM final validation
└─ Day 10 (Feb 16): Sprint Review & Retrospective
   └─ Demo + lessons learned
```

---

## PM Daily Checklist

### Daily Standup (Morning)
- [ ] Check infrastructure status (Redis, Vault, PostgreSQL)
- [ ] Review previous day's progress
- [ ] Identify blockers
- [ ] Delegate next task (if previous complete)

### Daily Review (Evening)
- [ ] Review completed work
- [ ] Run quality gates
- [ ] Update sprint metrics
- [ ] Document any issues

### Weekly Review (Friday)
- [ ] Sprint progress report
- [ ] Update stakeholders
- [ ] Adjust timeline if needed

---

## Contact Information

**PM**: Project Manager Agent  
**Security Expert**: security-compliance-expert  
**Testing Expert**: testing-qa-expert  
**Documentation**: All agents

**Escalation Path**:
1. Agent self-validation fails → PM reviews
2. PM validation fails → Fix task delegated
3. Repeated failures → Architecture review meeting

---

**Status**: Ready to start  
**Next Action**: Delegate Task 2.1 to security-compliance-expert  
**Estimated Completion**: 2026-02-17
