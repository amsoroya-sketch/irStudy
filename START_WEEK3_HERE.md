# Week 3 Sprint Kickoff - User Management & RBAC

**Sprint**: Week 3 (User Management & Role-Based Access Control)
**Status**: READY TO START
**Prerequisites**: Week 2 complete (✅ Done)
**Estimated Duration**: 10-14 hours

---

## Quick Start

### Before You Begin

1. **Verify Week 2 Completion**:
   ```bash
   # Check all tests still pass
   bash run_websocket_tests.sh
   bash run_security_events_tests.sh

   # Expected: 35/35 tests passing, 0 security violations
   ```

2. **Review Week 2 Deliverables**:
   - Read: `WEEK2_COMPLETE_SUMMARY.md`
   - Review: `WEEK2_SECURITY_RUNBOOK.md`
   - Check: `WEEK2_API_DOCUMENTATION.md`

3. **Verify Infrastructure Health**:
   ```bash
   # Check all services running
   docker ps | grep -E "(vault|postgres|redis)"

   # Should see:
   # - vault (port 8200)
   # - postgres (port 5433)
   # - redis cluster (ports 7379-7381)
   ```

---

## Week 3 Overview

### Sprint Goal

Implement comprehensive user management system with role-based access control (RBAC) for medical simulation platform.

### Key Features

1. **User CRUD Operations**
   - Create/Read/Update/Delete users
   - User profile management
   - Email verification
   - Password reset

2. **Role-Based Access Control**
   - Roles: Student, Instructor, Admin, System Admin
   - Permission system
   - Role assignment
   - Permission checks

3. **Organization Management**
   - Multi-tenancy support
   - Organization hierarchy
   - User-organization mapping

4. **Audit Logging**
   - User action tracking
   - RBAC event logging
   - Integration with Week 2 security events

---

## Week 3 Tasks

### Task 3.1: User Management Core (4 hours)

**Agent**: flutter-desktop-expert + rust-ffi-expert
**Deliverables**:
- User CRUD API endpoints
- User profile management
- Email verification system
- Password reset flow

**Success Criteria**:
- 100% test pass rate
- 0 security violations
- PHI encryption for user data
- HIPAA compliance

### Task 3.2: RBAC Implementation (4 hours)

**Agent**: security-compliance-expert
**Deliverables**:
- Role definitions (Student, Instructor, Admin, System Admin)
- Permission system
- Role assignment API
- Permission middleware

**Success Criteria**:
- 100% test pass rate
- 0 security violations
- Principle of least privilege
- Audit logging

### Task 3.3: Organization Management (3 hours)

**Agent**: rust-ffi-expert
**Deliverables**:
- Organization CRUD operations
- Multi-tenancy support
- Organization hierarchy
- User-organization mapping

**Success Criteria**:
- 100% test pass rate
- 0 security violations
- Data isolation between organizations

### Task 3.4: Integration Testing (2 hours)

**Agent**: testing-qa-expert
**Deliverables**:
- Integration tests for User + RBAC + Organizations
- Load testing for user operations
- Security testing for RBAC
- Performance validation

**Success Criteria**:
- 100% test pass rate
- Performance targets met (<100ms API response)
- 0 security violations

### Task 3.5: Documentation (1 hour)

**Agent**: security-compliance-expert
**Deliverables**:
- User Management API documentation
- RBAC guide
- Organization setup guide
- Week 3 completion summary

**Success Criteria**:
- All required sections present
- Code examples tested
- Production-ready documentation

---

## Architecture Overview

### User Management System

```
User Registration
    ↓
Email Verification
    ↓
User Profile Creation
    ↓
Role Assignment (default: Student)
    ↓
Organization Mapping
    ↓
✅ Active User Account
```

### RBAC System

```
API Request
    ↓
JWT Authentication (Week 2)
    ↓
Extract User ID + Roles
    ↓
Load Permissions (Redis cache)
    ↓
Check Permission (e.g., "osce.create")
    ↓
Allow/Deny Request
    ↓
Log RBAC Event (Week 2 security events)
```

### Role Hierarchy

```
System Admin (full access)
    ↓
Admin (organization-wide access)
    ↓
Instructor (course-level access)
    ↓
Student (limited access)
```

---

## Data Models

### User Model

```python
class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)  # Encrypted in Rust FFI
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    is_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    organization_id = Column(UUID, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    roles = relationship("UserRole", back_populates="user")
    organization = relationship("Organization", back_populates="users")
```

### Role Model

```python
class Role(Base):
    __tablename__ = "roles"

    id = Column(UUID, primary_key=True)
    name = Column(String, unique=True, nullable=False)  # student, instructor, admin
    description = Column(String)
    permissions = Column(JSON)  # List of permission strings
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Organization Model

```python
class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    parent_id = Column(UUID, ForeignKey("organizations.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="organization")
    children = relationship("Organization")
```

---

## Permissions System

### Permission Format

```
resource.action

Examples:
- osce.view
- osce.create
- osce.update
- osce.delete
- user.view
- user.create
- role.assign
```

### Role Permissions

**Student**:
- osce.view
- mcq.attempt
- progress.view

**Instructor**:
- Student permissions +
- osce.create
- osce.update
- student.view
- progress.grade

**Admin**:
- Instructor permissions +
- user.create
- user.update
- role.assign
- organization.view

**System Admin**:
- All permissions

---

## Security Requirements

### Must Follow (PROJECT_CONSTRAINTS.md)

1. **No Hardcoded Credentials**
   - All secrets from Vault/environment
   - Password hashing in Rust FFI
   - Encryption keys from Vault

2. **PHI Protection**
   - User data encrypted at rest (SQLCipher)
   - User data encrypted in transit (TLS)
   - PII anonymization in logs

3. **HIPAA Compliance**
   - Audit logging for all user actions
   - Access control (RBAC)
   - Data integrity (checksums)

4. **Zero-Trust Architecture**
   - Verify every request
   - Check permissions on every action
   - Log all RBAC decisions

---

## API Endpoints (To Be Implemented)

### User Management

```
POST   /api/v1/users                 - Create user
GET    /api/v1/users/{id}            - Get user
PUT    /api/v1/users/{id}            - Update user
DELETE /api/v1/users/{id}            - Delete user
GET    /api/v1/users                 - List users (paginated)

POST   /api/v1/users/verify-email    - Verify email
POST   /api/v1/users/reset-password  - Request password reset
PUT    /api/v1/users/reset-password  - Complete password reset
```

### RBAC

```
GET    /api/v1/roles                 - List roles
POST   /api/v1/roles                 - Create role
GET    /api/v1/roles/{id}            - Get role
PUT    /api/v1/roles/{id}            - Update role

POST   /api/v1/users/{id}/roles      - Assign role to user
DELETE /api/v1/users/{id}/roles/{id} - Remove role from user
GET    /api/v1/users/{id}/permissions - Get user permissions
```

### Organizations

```
GET    /api/v1/organizations         - List organizations
POST   /api/v1/organizations         - Create organization
GET    /api/v1/organizations/{id}    - Get organization
PUT    /api/v1/organizations/{id}    - Update organization
DELETE /api/v1/organizations/{id}    - Delete organization
```

---

## Performance Targets

| Metric | Target | Validation |
|--------|--------|------------|
| User CRUD latency (p95) | <100ms | Load testing |
| Permission check latency | <10ms | Load testing |
| Concurrent users | 1,000+ | Load testing |
| Database queries | <5 per request | Query analysis |
| Redis cache hit rate | >95% | Monitoring |

---

## Testing Strategy

### Unit Tests

- User CRUD operations
- RBAC permission checks
- Organization management
- Email verification
- Password reset

**Target**: 100% pass rate, >90% coverage

### Integration Tests

- User + RBAC integration
- User + Organization integration
- Full authentication flow (Week 2 + Week 3)

**Target**: 100% pass rate, real database/Redis

### Load Tests

- 1,000 concurrent user operations
- Permission check performance
- Database connection pooling

**Target**: Performance targets met

### Security Tests

- RBAC bypass attempts
- SQL injection (should be blocked)
- XSS attempts (should be sanitized)
- Credential scanning (should find 0 violations)

**Target**: 0 security violations

---

## Week 3 Timeline

### Day 1 (Estimated: 6 hours)

**Morning (3 hours)**:
- Sprint planning and kickoff
- Task 3.1: User Management Core (start)
- Database migrations

**Afternoon (3 hours)**:
- Task 3.1: User Management Core (complete)
- Validation and testing
- Task 3.2: RBAC Implementation (start)

### Day 2 (Estimated: 4-8 hours)

**Morning (2-4 hours)**:
- Task 3.2: RBAC Implementation (complete)
- Validation and testing

**Afternoon (2-4 hours)**:
- Task 3.3: Organization Management
- Task 3.4: Integration Testing
- Task 3.5: Documentation

---

## Delegation Templates

### Task 3.1 Delegation (User Management Core)

```markdown
Agent: flutter-desktop-expert + rust-ffi-expert

CONSTRAINTS:
1. Read PROJECT_CONSTRAINTS.md Section 3 (Security)
2. No hardcoded credentials
3. Password hashing in Rust FFI (use argon2)
4. Email encryption in SQLCipher
5. Follow Week 2 authentication patterns

VALIDATION:
- [ ] 100% test pass rate
- [ ] 0 security violations
- [ ] <100ms API latency
- [ ] PHI encryption verified
```

### Task 3.2 Delegation (RBAC Implementation)

```markdown
Agent: security-compliance-expert

CONSTRAINTS:
1. Read PROJECT_CONSTRAINTS.md Section 3 (Security)
2. Principle of least privilege
3. Audit all RBAC events (use Week 2 SecurityEventLogger)
4. Permission caching in Redis
5. No hardcoded permissions

VALIDATION:
- [ ] 100% test pass rate
- [ ] 0 security violations
- [ ] <10ms permission check latency
- [ ] Audit logging verified
```

---

## Success Criteria

### Week 3 Complete When:

1. ✅ All 5 tasks complete (3.1, 3.2, 3.3, 3.4, 3.5)
2. ✅ 100% test pass rate (unit + integration)
3. ✅ 0 security violations
4. ✅ Performance targets met
5. ✅ Documentation complete
6. ✅ Integration with Week 2 verified

---

## Quick Commands

### Start Week 3

```bash
# 1. Verify Week 2 complete
bash run_websocket_tests.sh
bash run_security_events_tests.sh

# 2. Check infrastructure
docker ps | grep -E "(vault|postgres|redis)"

# 3. Read this document
cat START_WEEK3_HERE.md

# 4. Begin Task 3.1 (delegate to agent)
```

### Check Progress

```bash
# Run all tests
pytest backend/tests/ -v

# Security scan
grep -r "hardcoded" backend/src/

# Test coverage
pytest --cov=backend/src backend/tests/
```

---

## Resources

### Documentation to Review

- `PROJECT_CONSTRAINTS.md` (Sections 2, 3, 6)
- `WEEK2_COMPLETE_SUMMARY.md` (Week 2 achievements)
- `WEEK2_SECURITY_RUNBOOK.md` (Security patterns)
- `WEEK2_API_DOCUMENTATION.md` (Authentication API)

### Code to Reference

- `backend/src/websocket/authenticator.py` (Authentication patterns)
- `backend/src/security/events.py` (Security event logging)
- `backend/src/auth/security.py` (JWT validation)

---

## Questions Before Starting?

### Common Questions

**Q: Can I skip Week 2 validation?**
A: No. Week 3 depends on Week 2 WebSocket authentication. Must verify 35/35 tests passing.

**Q: What if infrastructure is down?**
A: Restart services:
```bash
docker-compose up -d vault postgres redis-cluster
```

**Q: Can I use mock authentication for testing?**
A: Only for unit tests. Integration tests must use real Week 2 authentication.

**Q: How do I handle PHI in user data?**
A: All PHI must be encrypted in SQLCipher (Rust FFI). Follow PROJECT_CONSTRAINTS.md Section 3.

---

## Ready to Start?

### Pre-Flight Checklist

- [ ] Week 2 complete (35/35 tests passing)
- [ ] Infrastructure healthy (Vault, PostgreSQL, Redis)
- [ ] PROJECT_CONSTRAINTS.md reviewed
- [ ] Week 2 documentation reviewed
- [ ] Task 3.1 delegation prepared

### Start Command

When ready, say: **"Begin Week 3 Task 3.1"**

---

**Created**: 2026-02-07
**Sprint**: Week 3 (Ready to start)
**Prerequisites**: Week 2 complete ✅
**Estimated Duration**: 10-14 hours

🚀 **Ready for Week 3 - User Management & RBAC!**
