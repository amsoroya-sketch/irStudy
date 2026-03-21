# PRD-PHASE8-002: Auto Study Cards

**Priority**: P1
**Estimated Time**: 8-12h
**Assigned Agent**: general-purpose
**Dependencies**:
- ✅ PRD-PHASE2-003
- ✅ Study cards API

**Blocks**: Study card automation

---

## Executive Summary

Auto-generate 3-5 study cards after each OSCE session from AI Examiner feedback.

**Impact**: Essential for production readiness.

---

## Success Criteria

### Must Have (100% Required)
- [ ] Auto-generate 3-5 cards per session
- [ ] Extract from feedback
- [ ] Link to original session
- [ ] RAG citations required
- [ ] Preview before saving
- [ ] Manual edit option

### Should Have (90% Priority)
- [ ] Enhancements

### Nice to Have (Optional)
- [ ] Future features

---

## Technical Specification

### Generation Logic:
1. Parse feedback (strengths, improvements, suggestions)
2. Identify key learning points (2-3 from improvements, 1-2 from suggestions)
3. Format as Q&A:
   - Front: Question about concept
   - Back: Answer with citation
4. Link card.session_id to ai_osce_attempts.id
5. Set initial SM-2 params (easeFactor: 2.5, interval: 0)

---

## Agent OS Expert Constraints

### Agent: general-purpose

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
- `backend/src/ai/study_card_generator.py` (~300 lines)

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
- PRD-PHASE2-003
- Study cards API

**Blocks**: Study card automation

---

## Best Practices Applied

✅ Agent OS: general-purpose
✅ Constraints provided
✅ Validation required
✅ Security scan
✅ Testing comprehensive

---

**Created**: 2026-03-17
**Agent**: general-purpose
**Hours**: 8-12h
**Status**: Ready












































































































































































































































































































































