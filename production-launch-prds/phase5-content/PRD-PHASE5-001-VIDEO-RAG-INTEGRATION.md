# PRD-PHASE5-001: Video RAG Integration

**Priority**: P1
**Estimated Time**: 8-10h
**Assigned Agent**: general-purpose
**Dependencies**:
- ✅ Qdrant running
- ✅ Video transcripts

**Blocks**: Batch2 generation

---

## Executive Summary

Index 31 video scenarios to Qdrant with 13,000+ chunks for semantic search.

**Impact**: Critical component for production launch.

---

## Success Criteria

### Must Have (100% Required)
- [ ] 31 videos indexed
- [ ] Collection: osce_video_scenarios
- [ ] 13,000+ chunks with metadata
- [ ] Semantic search working

### Should Have (90% Priority)
- [ ] Optimizations
- [ ] Enhanced logging

### Nice to Have (Optional)
- [ ] Advanced features

---

## Technical Specification

### Indexing:
- Extract transcripts with timestamps
- Chunk into 200-word segments
- Generate embeddings (Claude embeddings)
- Store in Qdrant with metadata:
  - video_id, timestamp, specialty, keywords

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
- `scripts/index_videos_to_qdrant.py` (~250 lines)

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
- Qdrant running
- Video transcripts

**Blocks**: Batch2 generation

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
**Hours**: 8-10h
**Status**: Ready for Execution












































































































































































































































































































































