# irStudy Project-Specific Constraints

## Project Overview

**Context**: irStudy platform has **two integrated systems** (EMR Practice + AI OSCE Simulation) sharing infrastructure.

**CRITICAL**: When working on irStudy, agents MUST coordinate across systems to prevent conflicts.

---

## Cross-System Implementation Workflow

### 🔗 Required Reading Before Any Task

1. **Master Plan** (overall platform view):
   - Read: `/home/dev/Development/irStudy/COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md`

2. **Shared Infrastructure Spec** (if exists):
   - Read: `/home/dev/Development/irStudy/SHARED_INFRASTRUCTURE_SPEC.md`
   - Contains: Vault keys, Redis namespaces, JWT format, security standards

3. **System-Specific Docs**:
   - EMR: `/home/dev/Development/irStudy/COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md`
   - AI OSCE: `/home/dev/Development/irStudy/ai-osce-ralph-prds/IMPLEMENTATION_STATUS.md`

### 📋 Sequential Implementation Protocol

**Step 1: Shared Infrastructure FIRST** (BLOCKS everything else)
```
PM reads COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md
  ↓
Identify shared infrastructure tasks (Vault, Redis, security tests)
  ↓
Delegate to security-compliance-expert (Vault + HTTPS + JWT)
  ↓
Validate: 0 hardcoded credentials, 35 security tests pass
  ↓
Delegate to rust-ffi-expert (Redis architecture)
  ↓
Validate: Redis operational, namespaces configured (emr:* vs osce:*)
  ↓
CHECKPOINT: Shared infrastructure COMPLETE → Proceed to system-specific work
```

**Step 2: System-Specific Implementation** (can run in parallel)
```
EMR Implementation (rust-ffi-expert, flutter-desktop-expert)
  ↓ (parallel)
AI OSCE Implementation (rust-ffi-expert, aba-clinical-expert, flutter-desktop-expert)
  ↓
CHECKPOINT: Both systems reference SHARED_INFRASTRUCTURE_SPEC.md
CHECKPOINT: No duplicate Vault keys, no Redis namespace collisions
  ↓
Validate each system independently before integration
```

**Step 3: Integration Layer** (requires both systems complete)
```
Delegate to rust-ffi-expert: OSCE-to-EMR converter
  ↓
Delegate to flutter-desktop-expert: Unified progress dashboard
  ↓
Delegate to testing-qa-expert: Cross-system E2E tests
  ↓
CHECKPOINT: 12 integration tests pass (100%)
  ↓
Final validation: All 500+ tests pass across platform
```

### ⚠️ Anti-Patterns to Avoid

**❌ DON'T**: Delegate EMR and AI OSCE tasks simultaneously without shared infrastructure
**✅ DO**: Complete Week 1 (shared infrastructure) before delegating system-specific tasks

**❌ DON'T**: Let agents create separate Vault setups, Redis configs, or security tests
**✅ DO**: Reference SHARED_INFRASTRUCTURE_SPEC.md in all agent prompts

**❌ DON'T**: Assume both systems can use different JWT formats or security headers
**✅ DO**: Enforce unified standards (9 security headers, same JWT claims)

**❌ DON'T**: Allow `user_progress` table extensions without coordination
**✅ DO**: Combined Alembic migration adding EMR + OSCE columns together

### 🎯 Delegation Template for Cross-System Work

```markdown
Agent Task: [Specific task for EMR or AI OSCE]

CROSS-SYSTEM CONSTRAINTS:
1. **MUST READ FIRST**:
   - COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md (understand integration)
   - SHARED_INFRASTRUCTURE_SPEC.md (reuse existing patterns)

2. **Shared Infrastructure** (DO NOT recreate):
   - Vault: Use existing key hierarchy (see VAULT_INTEGRATION.md)
   - Redis: Use assigned namespace (emr:* OR osce:*)
   - JWT: Use unified token format (see SHARED_INFRASTRUCTURE_SPEC.md)
   - Security: Extend existing test suite (backend/tests/test_security/)

3. **Validation Checklist**:
   - [ ] No duplicate infrastructure (Vault, Redis, security tests)
   - [ ] Namespace conflicts checked (Redis keys, database tables)
   - [ ] Security standards aligned (same encryption, HTTPS headers)
   - [ ] Cross-references added (link to integration PRDs if applicable)

4. **Integration Points**:
   - If extending `user_progress`: Coordinate with other system's migration
   - If using Claude API: Check shared rate limit (90 req/min total)
   - If creating dashboard: Consider unified view (EMR + OSCE metrics)

EXAMPLE (correct coordination):
[Provide specific example from SHARED_INFRASTRUCTURE_SPEC.md]
```

### 📊 Quality Gates for Cross-System Work

Before marking work COMPLETE:
- [ ] No duplicate infrastructure created (Vault, Redis, security)
- [ ] Shared components referenced, not recreated
- [ ] Integration tests added if systems interact
- [ ] Documentation cross-references updated
- [ ] Master plan STATUS updated (week completed, deliverables checked off)

---

## Technology Stack

### Frontend
- Flutter Desktop (Material Design 3)
- Riverpod 2.6+ for state management
- WCAG 2.2 AA accessibility compliance

### Backend
- FastAPI (Python)
- PostgreSQL with SQLAlchemy
- Redis for caching
- Rust FFI for performance-critical operations

### Security
- HashiCorp Vault for secrets management
- SQLCipher for database encryption
- JWT authentication
- 9 required security headers (HTTPS, CSP, HSTS, etc.)

### Testing Requirements
- 100% test pass rate (mandatory)
- ≥70% code coverage
- Unit tests (pytest/jest)
- Integration tests
- E2E tests (Playwright)

---

## irStudy-Specific Code Patterns

### Flutter Provider Pattern (MUST FOLLOW)

```dart
// CORRECT: Use databaseConfigProvider for all FFI calls
final dbConfig = ref.read(databaseConfigProvider);
await ffi.method(
  userId: dbConfig.userId,
  dbPath: dbConfig.dbPath,
  dbKey: dbConfig.dbKey,
);

// WRONG: Never hardcode credentials
await ffi.method(
  userId: 'mock-user-id',  // ❌ VIOLATION
  dbPath: '/path/to/db',   // ❌ VIOLATION
  dbKey: 'hardcoded-key',  // ❌ VIOLATION
);
```

### Redis Namespace Convention

```python
# EMR system uses emr:* prefix
redis_client.set("emr:patient:123", data)

# OSCE system uses osce:* prefix
redis_client.set("osce:session:456", data)
```

### RAG Content Requirements

All medical content MUST:
- Include `qdrant_point_id` (UUID) for traceability
- Cite Australian medical sources (≥60% of content)
- Link to source documents (no hallucinations)
- Pass reference verification checks

**Example**:
```json
{
  "red_flags": [
    {
      "flag": "Sudden-onset severe headache",
      "citation": {
        "source": "Talley & O'Connor Clinical Examination 9th Ed",
        "qdrant_point_id": "550e8400-e29b-41d4-a716-446655440000",
        "page": "p. 412"
      }
    }
  ]
}
```

---

## Project-Specific Validation Commands

```bash
# Frontend validation (from /home/dev/Development/irStudy/frontend)
cd /home/dev/Development/irStudy/frontend
npx tsc --noEmit  # Expected: 0 errors
npm run lint      # Expected: 0 errors
npm test          # Expected: 100% pass rate

# Backend validation (from /home/dev/Development/irStudy/backend)
cd /home/dev/Development/irStudy/backend
pytest --cov      # Expected: ≥70% coverage, 100% pass rate
python -m pylint src/  # Expected: score ≥9.0/10

# Security validation
grep -r "hardcoded\|localhost\|ws://" /home/dev/Development/irStudy/frontend/src/
# Expected: 0 matches

# Performance validation
curl -w "@curl-format.txt" "http://localhost:8001/api/v1/patient-personas"
# Expected: <200ms (p95)

# Flutter desktop build
cd /home/dev/Development/irStudy/frontend
flutter analyze   # Expected: 0 issues
flutter build linux  # Expected: successful build
```

---

**Last Updated:** 2026-03-29
**Version:** 1.0
**Project:** irStudy Platform (EMR + AI OSCE)
