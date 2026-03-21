# PRD-PHASE4-003: AHPRA Compliance

**Priority**: P0
**Estimated Time**: 10-12h
**Assigned Agent**: security-compliance-expert
**Dependencies**:
- ✅ AHPRA Code of Conduct
- ✅ EMR UI

**Blocks**: Production launch

---

## Executive Summary

Enforce 10 AHPRA standards with validation rules and alert system for violations.

**Impact**: Critical component for production launch.

---

## Success Criteria

### Must Have (100% Required)
- [ ] 10 AHPRA standards enforced
- [ ] Validation with RAG citations
- [ ] Alert system for violations
- [ ] Audit log for compliance

### Should Have (90% Priority)
- [ ] Optimizations
- [ ] Enhanced logging

### Nice to Have (Optional)
- [ ] Advanced features

---

## Technical Specification

### 10 Standards:
1. Informed consent documented
2. Patient identification verified
3. Adverse events reported
4. Medication reconciliation
5. Allergies checked before prescribing
6. Clinical reasoning documented
7. Handover documentation
8. Privacy and confidentiality
9. Professional boundaries
10. Continuous quality improvement

---

## Agent OS Expert Constraints

### Agent: security-compliance-expert

**CRITICAL**: Read these constraints before starting:

1. **Existing Code Patterns** (MUST FOLLOW):
   - Follow project conventions

2. **Requirements** (MUST IMPLEMENT):
   - Implement core features

3. **Accessibility** (MUST MEET):
   - WCAG 2.2 AA compliant
   - Keyboard navigation
   - Screen reader support

4. **Performance** (MUST ACHIEVE):
   - <500ms response time

5. **Security** (MUST ENFORCE):
   - NO hardcoded credentials
   - Input validation
   - Secure data storage

6. **Testing** (MUST VALIDATE):
   - Unit tests
   - Integration tests

---

## Validation Checklist

Before marking complete:

### Code Quality
- [ ] Type checker → 0 errors
- [ ] Linter → 0 errors
- [ ] Build succeeds

### Functionality
- [ ] Features work
- [ ] Error handling

### Accessibility
- [ ] Keyboard nav works
- [ ] Screen reader tested

### Performance
- [ ] Benchmarks met
- [ ] No memory leaks

### Security
- [ ] Security scan passes
- [ ] No hardcoded secrets

---

## Test Commands

```bash
# Run tests\ncd backend && python -m pytest tests/ -v
```

---

## Files to Create/Modify

### Created
- `backend/src/compliance/ahpra_validator.py` (~350 lines)

### Modified  
- `existing.py` (~50 lines)

---

## Acceptance Criteria

1. ✅ All tests pass
2. ✅ Core functionality works
3. ✅ Accessibility compliant
4. ✅ Performance met
5. ✅ Security scan passes
6. ✅ Documentation complete

---

## Reference Verification

**RAG Requirements**: NONE
**Citations**: N/A

---

## Dependencies & Integration

**Depends On**:
- AHPRA Code of Conduct
- EMR UI

**Blocks**: Production launch

---

## Best Practices Applied

✅ Agent OS: security-compliance-expert
✅ Explicit constraints
✅ Validation checklist  
✅ Security scan
✅ Comprehensive testing

---

**Created**: 2026-03-17
**Agent**: security-compliance-expert
**Hours**: 10-12h
**Status**: Ready for Execution







































































































































































































































































































































