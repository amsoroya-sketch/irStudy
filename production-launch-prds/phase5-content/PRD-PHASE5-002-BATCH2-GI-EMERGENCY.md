# PRD-PHASE5-002: Batch2 GI Emergency

**Priority**: P1
**Estimated Time**: 8-12h
**Assigned Agent**: general-purpose
**Dependencies**:
- ✅ PRD-PHASE5-001
- ✅ QA validator

**Blocks**: Batch3-10 generation

---

## Executive Summary

Generate 30 personas from video scenarios with dual citations and QA validation.

**Impact**: Critical component for production launch.

---

## Success Criteria

### Must Have (100% Required)
- [ ] 30 personas generated
- [ ] Dual citations (eTG + video)
- [ ] QA validation passed (13 gates)
- [ ] Specialties: GI, Emergency

### Should Have (90% Priority)
- [ ] Optimizations
- [ ] Enhanced logging

### Nice to Have (Optional)
- [ ] Advanced features

---

## Technical Specification

Implementation details defined in constraints below.

---

## Agent OS Expert Constraints

### Agent: general-purpose

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
- `backend/data/batch2_personas.json` (~3000 lines)

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
- PRD-PHASE5-001
- QA validator

**Blocks**: Batch3-10 generation

---

## Best Practices Applied

✅ Agent OS: general-purpose
✅ Explicit constraints
✅ Validation checklist  
✅ Security scan
✅ Comprehensive testing

---

**Created**: 2026-03-17
**Agent**: general-purpose
**Hours**: 8-12h
**Status**: Ready for Execution

















































































































































































































































































































































