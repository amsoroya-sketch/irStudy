# PRD-PHASE3-002: SM-2 Algorithm

**Priority**: P1 (Critical for production launch)
**Estimated Time**: 6-8h
**Assigned Agent**: flutter-desktop-expert
**Dependencies**:
- ✅ PRD-PHASE3-001 (Flashcard Interface)
- ✅ study_card_reviews table

**Blocks**: Spaced repetition features

---

## Executive Summary

Implement SM-2 spaced repetition algorithm for flashcard scheduling with quality-based review dates.

**Impact**: Critical for production readiness and user experience.

---

## Success Criteria

### Must Have (100% Required)
- [ ] SM-2 algorithm implementation (calculate next review date)
- [ ] Update study_card_reviews table on each rating
- [ ] Track daily streak (consecutive days reviewed)
- [ ] Calculate retention rate (cards remembered / cards reviewed)
- [ ] Statistics dashboard: cards due today, streak, retention

### Should Have (90% Priority)
- [ ] Performance optimizations
- [ ] Enhanced error handling
- [ ] Logging and monitoring

### Nice to Have (Optional)
- [ ] Advanced features
- [ ] Additional visualizations

---

## Technical Specification

### SM-2 Algorithm Implementation

```typescript
function calculateNextReview(quality: number, easeFactor: number, interval: number): { nextInterval: number, newEaseFactor: number } {
  // SM-2 algorithm by Piotr Wozniak
  const newEF = easeFactor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02));
  const clampedEF = Math.max(1.3, newEF);
  
  let nextInterval: number;
  if (quality < 3) {
    nextInterval = 1; // Reset to 1 day
  } else {
    if (interval === 0) {
      nextInterval = 1;
    } else if (interval === 1) {
      nextInterval = 6;
    } else {
      nextInterval = Math.round(interval * clampedEF);
    }
  }
  
  return { nextInterval, newEaseFactor: clampedEF };
}
```

---

## Agent OS Expert Constraints

### Agent: flutter-desktop-expert

**CRITICAL**: Read these constraints before starting:

1. **Existing Code Patterns** (MUST FOLLOW):
   - Follow project code style
   - Use existing components and utilities
   - TypeScript strict mode (no any types)

2. **Requirements** (MUST IMPLEMENT):
   - Core functionality as specified
   - Error handling and validation
   - Performance benchmarks met

3. **Accessibility Requirements** (MUST MEET):
   - WCAG 2.2 AA compliant
   - Keyboard navigation
   - Screen reader support

4. **Performance Requirements** (MUST ACHIEVE):
   - <500ms API response time
   - <100ms UI render time
   - No memory leaks

5. **Security Requirements** (MUST ENFORCE):
   - NO hardcoded credentials or API keys
   - Input validation and sanitization
   - Secure data storage

6. **Testing Requirements** (MUST VALIDATE):
   - Unit tests for all logic
   - Integration tests for APIs
   - Edge case coverage

---

## Validation Checklist (Complete Before Returning!)

Before marking this PRD complete, verify:

### Code Quality
- [ ] Run TypeScript/Python type checker → 0 errors
- [ ] Run linter → 0 errors
- [ ] Run build/compile → Succeeds

### Functionality
- [ ] Core features work as specified
- [ ] Error cases handled gracefully
- [ ] Integration points tested

### Accessibility
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] High contrast mode supported

### Performance
- [ ] Performance benchmarks met
- [ ] No memory leaks
- [ ] Smooth animations (60fps)

### Security
- [ ] Run security scan (grep for hardcoded secrets) → 0 violations
- [ ] Input validation tested
- [ ] Authentication/authorization working

---

## Test Commands

```bash
# Run tests
cd /home/dev/Development/irStudy/backend
python -m pytest tests/ -v

cd /home/dev/Development/irStudy/frontend
npm run test
npm run build

```

---

## Files to Create/Modify

### Created
- `new_file.py` (~200 lines)

### Modified
- `existing_file.py` (~50 lines modified)

---

## Acceptance Criteria

**This PRD is COMPLETE when:**

1. ✅ All tests pass (100%)
2. ✅ Core functionality implemented and working
3. ✅ Accessibility compliance (WCAG 2.2 AA)
4. ✅ Performance benchmarks met
5. ✅ Security scan passes
6. ✅ Documentation complete
7. ✅ Manual testing confirms user journeys work end-to-end

---

## Reference Verification

**RAG Requirements**: NONE (implementation-focused PRD)

**Citations Required**: NONE

**Clinical References**: N/A

---

## Dependencies & Integration Points

**Depends On** (must exist before this PRD):
- ✅ PRD-PHASE3-001 (Flashcard Interface)
- ✅ study_card_reviews table

**Blocks** (cannot start until this completes):
- Spaced repetition features

**Integration Points**:
- API endpoints
- Database tables
- Frontend components

---

## Best Practices Applied (From Week 1)

✅ **Agent OS**: Assigned to flutter-desktop-expert (specialist for this domain)
✅ **Explicit Constraints**: Provided existing patterns, requirements, examples
✅ **Validation Checklist**: Agent must self-validate before returning
✅ **Security Scan**: Grep for hardcoded secrets before marking complete
✅ **Comprehensive Testing**: Unit, integration, E2E, accessibility, performance
✅ **Reference Verification**: RAG citations where applicable

---

**Created**: 2026-03-17
**Assigned Agent**: flutter-desktop-expert
**Estimated Hours**: 6-8h
**Status**: Ready for Execution

**Next PRD**: PRD-PHASE4-001 (EMR Database Schema)






















































































































































































































































































