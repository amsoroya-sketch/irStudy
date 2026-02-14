# START WEEK 2 HERE - Your Action Plan

**Created**: 2026-02-07  
**Status**: READY TO START  
**Role**: You are the Project Manager coordinating Week 2 implementation

---

## What You Asked For

> "Start Week 2 implementation: Enhanced WebSocket Authentication for AMC Clinical Exam Simulation v2.0"

## What I Created

### 📋 Complete Sprint Plan (56KB)
**File**: `WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md`

This is the master plan containing:
- Sprint overview and zero-trust architecture
- Task 2.1: WebSocketAuthenticator (6 hours)
- Task 2.2: SecurityEventLogger (4 hours)
- Task 2.3: Load Testing (6 hours)
- Task 2.4: Documentation (2 hours)
- Complete code skeletons for all components
- Quality gates and validation checklists
- Risk mitigation strategies

**Use this**: As reference document for technical details

---

### 🎯 Task Delegation Guide (20KB)
**File**: `WEEK2_TASK_DELEGATION.md`

This contains ready-to-use delegation prompts:
- Task 2.1: Copy/paste prompt for security-compliance-expert
- Task 2.2: Copy/paste prompt for security-compliance-expert
- Task 2.3: Copy/paste prompt for testing-qa-expert
- Task 2.4: Copy/paste prompt for security-compliance-expert
- Post-delegation validation procedures
- Decision gate criteria (when to proceed vs. fix)

**Use this**: To delegate tasks to specialist agents

---

### ⚡ PM Quick Reference (10KB)
**File**: `WEEK2_PM_QUICK_REFERENCE.md`

Your daily operations guide:
- Quick start commands (check infrastructure)
- Task checklists with validation steps
- Common issues and solutions
- Agent communication templates
- Daily PM checklist
- Metrics dashboard

**Use this**: Every day for operational tasks

---

### 📊 Implementation Summary (14KB)
**File**: `WEEK2_IMPLEMENTATION_READY.md`

Executive summary of the sprint:
- What was created (all documents)
- Architecture overview
- Success metrics and targets
- Risk mitigation strategies
- Timeline and milestones

**Use this**: For high-level overview and stakeholder updates

---

## Your First Action (5 minutes)

### Step 1: Check Infrastructure
```bash
cd /home/dev/Development/irStudy

# Redis cluster (6 nodes)
redis-cli -p 7379 ping
redis-cli -p 7380 ping
redis-cli -p 7381 ping

# Vault
curl http://localhost:8200/v1/sys/health

# PostgreSQL
psql -h localhost -p 5433 -U iruser -d irdb -c "SELECT version();"
```

**Expected**: All services respond successfully

### Step 2: Delegate Task 2.1 (2 minutes)

**Agent**: security-compliance-expert  
**Estimated Time**: 6 hours  
**File**: `WEEK2_TASK_DELEGATION.md` (lines 30-250)

**Delegation Message**:
```markdown
@security-compliance-expert

I'm delegating Task 2.1 (WebSocket Authenticator Core) to you.

## Task Details
See /home/dev/Development/irStudy/WEEK2_TASK_DELEGATION.md section "Task 2.1 Delegation"

## Critical Constraints
1. NO hardcoded credentials (read constraints/03-security-configuration.md)
2. Reuse existing JWT functions (backend/src/auth/security.py)
3. Target <50ms authentication latency (p95)
4. All Redis operations async (redis.asyncio)

## Files to Create
- backend/src/websocket/__init__.py
- backend/src/websocket/authenticator.py
- backend/src/websocket/rate_limiter.py
- backend/src/websocket/connection_tracker.py
- backend/tests/test_websocket_auth.py

## Validation Required (Before Returning)
Run these commands:
```bash
# Run tests
pytest backend/tests/test_websocket_auth.py -v

# Security scan
grep -r "redis://.*:.*@" backend/src/websocket/

# Expected: 100% tests pass, 0 hardcoded credentials
```

## Code Patterns to Follow
- JWT validation: backend/src/auth/security.py
- Redis async: Use redis.asyncio library
- See WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md sections 2.1.2, 2.1.3, 2.1.4 for code skeletons

## Success Criteria
- ✅ 100% test pass rate
- ✅ 0 hardcoded credentials
- ✅ <50ms authentication latency (p95)
- ✅ Security events logged

Let me know if you have questions before starting.
```

**Copy this message and send to security-compliance-expert**

---

## Your Daily Routine (10 minutes/day)

### Morning Standup
1. Check infrastructure status (Redis, Vault, PostgreSQL)
2. Review agent progress from previous day
3. Identify any blockers
4. Delegate next task if previous complete

### Evening Review
1. Review completed work
2. Run quality gates (tests, security scan)
3. Update sprint metrics
4. Document any issues

**Use**: `WEEK2_PM_QUICK_REFERENCE.md` for daily checklists

---

## Quality Gates (When to Proceed)

### After Task 2.1 (WebSocket Authenticator)
Run validation:
```bash
cd /home/dev/Development/irStudy

# 1. Run tests
pytest backend/tests/test_websocket_auth.py -v

# 2. Security scan
grep -r "redis://" backend/src/websocket/

# 3. Performance test
pytest backend/tests/test_websocket_auth.py::test_authentication_latency_target -v
```

**Proceed to Task 2.2 if**:
- ✅ Tests: 100% pass rate
- ✅ Security: 0 violations
- ✅ Performance: p95 <50ms

**Fix before proceeding if**:
- ❌ Any tests fail
- ❌ Hardcoded credentials found
- ❌ Performance >50ms

---

## Sprint Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Test Pass Rate | 100% | `pytest backend/tests/ -v` |
| Security Violations | 0 | `grep -r "redis://" backend/src/` |
| Auth Latency (p95) | <50ms | Load test output |
| Concurrent Connections | 100 | Load test (10 users × 10 connections) |
| Test Coverage | >80% | `pytest --cov=backend/src/websocket` |
| Documentation | Complete | Runbook + API docs reviewed |

---

## Sprint Timeline (10 Days)

```
Feb 7-8:   Task 2.1 - WebSocketAuthenticator (security-compliance-expert)
Feb 9-10:  Task 2.2 - Security Event Logging (security-compliance-expert)
Feb 11-12: Task 2.3 - Load Testing (testing-qa-expert)
Feb 13-14: Task 2.4 - Documentation (security-compliance-expert)
Feb 15:    Integration & Final Validation (PM)
Feb 16:    Sprint Review & Retrospective (PM + team)
```

**Estimated Total Time**: 18 hours over 10 days (~2 hours/day)

---

## Key Improvements from Week 1

### What We Fixed
1. **Sequential validation** (not parallel batch)
   - Prevents systematic errors across multiple agents
   - Issues caught early, not after all work complete

2. **Explicit constraints in delegation prompts**
   - Agents know what NOT to do upfront
   - Example code patterns provided
   - Anti-patterns documented

3. **Self-validation checklists**
   - Agents verify their work before returning
   - PM validates only after agent self-check

4. **Decision gates between tasks**
   - Clear criteria for proceeding vs. fixing
   - No task starts until previous approved

**Result**: Prevents issues like 124 hardcoded credentials we had to fix in Week 1

---

## If Something Goes Wrong

### Issue: Agent returns code with violations
**Action**: 
1. Document violations in `WEEK2_ISSUES.md`
2. Use fix template from `WEEK2_PM_QUICK_REFERENCE.md`
3. Delegate fix task back to same agent
4. Do NOT proceed to next task until resolved

### Issue: Tests fail
**Action**:
1. Review test output for specific failures
2. Check infrastructure (Redis, Vault, PostgreSQL)
3. If infrastructure issue: Restart Docker services
4. If code issue: Delegate fix with specific error messages

### Issue: Performance target not met (>50ms)
**Action**:
1. Run profiling to identify bottlenecks
2. Common causes: Multiple Redis round trips, synchronous operations
3. Sprint plan includes optimization strategies (section 2.1)
4. Delegate optimization task with profiling data

**See**: `WEEK2_PM_QUICK_REFERENCE.md` section "Common Issues & Solutions"

---

## Documents Quick Reference

| Document | Size | Purpose | When to Use |
|----------|------|---------|-------------|
| `WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md` | 56KB | Master plan with technical details | Reference during implementation |
| `WEEK2_TASK_DELEGATION.md` | 20KB | Agent delegation prompts | When delegating tasks |
| `WEEK2_PM_QUICK_REFERENCE.md` | 10KB | Daily operations guide | Every day |
| `WEEK2_IMPLEMENTATION_READY.md` | 14KB | Executive summary | Stakeholder updates |
| `START_WEEK2_HERE.md` | This file | Quick start guide | Right now! |

---

## Zero-Trust WebSocket Architecture

### What We're Building
```
Client WebSocket Connection
    ↓
1. JWT Token Validation (signature, expiration, claims)
    ↓
2. Session Correlation (verify session exists in Redis)
    ↓
3. Token Fingerprinting (IP + User-Agent + screen resolution)
    ↓
4. Rate Limiting (Redis sliding window, max 10/min)
    ↓
5. Connection Tracking (max 3 concurrent per user)
    ↓
6. Security Event Logging (batched to Vault audit log)
    ↓
Authenticated WebSocket Connection Established ✅
```

### Security Features
- Multi-factor validation (6 steps)
- Zero-trust architecture (verify everything)
- Rate limiting (prevent abuse)
- Connection tracking (limit concurrent connections)
- Security event logging (SIEM integration)
- Performance optimized (<50ms latency)

---

## Week 1 Context (Already Complete)

✅ Vault running (http://localhost:8200, 13 secrets)  
✅ PostgreSQL encrypted schema (localhost:5433)  
✅ Redis Cluster (6 nodes, 7379-7384)  
✅ JWT authentication infrastructure (backend/src/auth/)  
✅ All 14 validation tests passed

**You can now build on this solid foundation.**

---

## Final Checklist Before Starting

- [ ] Read this document (START_WEEK2_HERE.md)
- [ ] Skim `WEEK2_IMPLEMENTATION_READY.md` (executive summary)
- [ ] Check infrastructure status (Redis, Vault, PostgreSQL)
- [ ] Open `WEEK2_TASK_DELEGATION.md` (ready to copy Task 2.1 prompt)
- [ ] Bookmark `WEEK2_PM_QUICK_REFERENCE.md` (daily reference)

**Once checked**: Delegate Task 2.1 to security-compliance-expert

---

## Expected Sprint Outcome

### By Feb 17 (Day 10), You Will Have:
1. ✅ Zero-trust WebSocket authentication system
2. ✅ 100% test pass rate (unit + integration + load)
3. ✅ 0 security violations (no hardcoded credentials)
4. ✅ <50ms authentication latency (p95)
5. ✅ 100 concurrent connections supported
6. ✅ Complete security documentation (runbook + API docs)
7. ✅ Load test report with performance metrics
8. ✅ Sprint retrospective with lessons learned

### Production-Ready Features:
- Multi-factor WebSocket authentication
- Rate limiting (10 connections/minute per user)
- Connection tracking (max 3 concurrent per user)
- Security event logging (Vault audit integration)
- Prometheus metrics export (monitoring ready)
- Comprehensive documentation (security runbook)

---

## Questions?

If you have questions during the sprint:
1. Check `WEEK2_PM_QUICK_REFERENCE.md` (common issues section)
2. Review `WEEK2_WEBSOCKET_AUTH_SPRINT_PLAN.md` (technical details)
3. Check project constraints (`constraints/03-security-configuration.md`)

---

## Ready to Start?

**Your next action**: Delegate Task 2.1 to security-compliance-expert

**Delegation prompt**: Copy from `WEEK2_TASK_DELEGATION.md` (lines 30-250)

**Estimated completion**: Task 2.1 in 6 hours, full sprint in 10 days

---

**Sprint Status**: READY TO START ✅  
**Next Action**: Delegate Task 2.1 NOW  
**Expected Completion**: 2026-02-17

Good luck with Week 2! 🚀

---

**Created by**: Project Manager Agent  
**Date**: 2026-02-07  
**Version**: 1.0
