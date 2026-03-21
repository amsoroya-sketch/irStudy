# PRD-PHASE6-001: 16-Station Mock Exam Orchestration

**Priority**: P0
**Estimated Time**: 12-16h
**Assigned Agent**: rust-ffi-expert
**Dependencies**:
- ✅ All scoring logic
- ✅ PRD-PHASE2-001
- ✅ Session timer

**Blocks**: Mock exam feature

---

## Executive Summary

Orchestrate 16 OSCE stations with 8-minute sessions, 2-minute breaks, and final report generation (240 marks total).

**Impact**: Essential for production readiness.

---

## Success Criteria

### Must Have (100% Required)
- [ ] 16 stations × 8 minutes
- [ ] 2-minute breaks between stations
- [ ] Session persistence across breaks
- [ ] Final report (240 marks)
- [ ] PDF export with AMC formatting
- [ ] Progress tracking

### Should Have (90% Priority)
- [ ] Enhancements

### Nice to Have (Optional)
- [ ] Future features

---

## Technical Specification

### Orchestration Flow:
1. Select 16 personas (or use predefined exam)
2. Start Station 1 (8 min timer)
3. Auto-transition to 2-min break
4. Repeat for stations 2-16
5. Generate final report:
   - Total score /240
   - Per-station breakdown
   - Strengths/weaknesses summary
   - Pass/Fail (threshold: 144/240 = 60%)

---

## Agent OS Expert Constraints

### Agent: rust-ffi-expert

**CRITICAL**: Read constraints before starting:

1. **Existing Patterns** (MUST FOLLOW):
   - Follow project conventions

2. **Requirements** (MUST IMPLEMENT):
   - Implement features

3. **Accessibility** (MUST MEET):
   - WCAG 2.2 AA compliant
   - Keyboard navigation
   - Screen reader support

4. **Performance** (MUST ACHIEVE):
   - <500ms latency

5. **Security** (MUST ENFORCE):
   - NO hardcoded credentials
   - Input validation
   - Secure storage

6. **Testing** (MUST VALIDATE):
   - Unit tests
   - Integration tests

---

## Validation Checklist

### Code Quality
- [ ] Type check → 0 errors
- [ ] Lint → 0 errors
- [ ] Build succeeds

### Functionality
- [ ] Features work

### Accessibility
- [ ] Keyboard nav
- [ ] Screen reader

### Performance
- [ ] Benchmarks met
- [ ] No leaks

### Security
- [ ] Security scan passes
- [ ] No secrets

---

## Test Commands

```bash
# Run tests\npytest tests/ -v
```

---

## Files to Create/Modify

### Created
- `backend/src/api/v1/mock_exams.py` (~400 lines)
- `backend/src/orchestration/exam_orchestrator.py` (~300 lines)

### Modified
- `mod.py` (~50 lines)

---

## Acceptance Criteria

1. ✅ Tests pass
2. ✅ Functionality works
3. ✅ Accessibility compliant
4. ✅ Performance met
5. ✅ Security passes
6. ✅ Documentation complete

---

## Reference Verification

**RAG**: NONE
**Citations**: N/A

---

## Dependencies & Integration

**Depends On**:
- All scoring logic
- PRD-PHASE2-001
- Session timer

**Blocks**: Mock exam feature

---

## Best Practices Applied

✅ Agent OS: rust-ffi-expert
✅ Constraints provided
✅ Validation required
✅ Security scan
✅ Testing comprehensive

---

**Created**: 2026-03-17
**Agent**: rust-ffi-expert
**Hours**: 12-16h
**Status**: Ready







































































































































































































































































































































