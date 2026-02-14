# Medical Image Integration & MCQ/OSCE System - Master Plan

**Created:** 2026-02-03
**Status:** Planning Complete, Ready for Implementation
**Estimated Duration:** 4 days (32 hours)

---

## Executive Summary

This plan integrates medical images from multiple sources (HEAL, MedPix, etc.) with the existing MCQ/OSCE database system, creates a unified image management pipeline, and establishes automated linking between visual content and educational materials.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 1: DATABASE FOUNDATION (Day 1)                            │
│                                                                  │
│  JSON Files ──> Seed Script ──> PostgreSQL ──> FastAPI ──> React│
│  (data/mcqs)    (01)            (mcqs/osces)   (02)       (03)  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 2: IMAGE PROCESSING (Day 2)                               │
│                                                                  │
│  Medical Images ──> Process ──> Enrich ──> Index                │
│  (HEAL/MedPix)      (04)        (05)       (07)                │
│                                                                  │
│  Output: Unified metadata + PostgreSQL tables                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ PHASE 3: DISTRIBUTION & LINKING (Days 3-4)                      │
│                                                                  │
│  Images ──> CDN ──> Link to MCQs/OSCEs ──> RAG Integration     │
│            (06)        (09)                  (08)                │
│                                                                  │
│  Output: CDN URLs, automated linking, multimodal RAG            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Task Dependencies

```
┌──────────┐
│   01     │  Database Seed Script (CRITICAL PATH)
└────┬─────┘
     │
     ├──> 02  API Verification (depends on 01)
     │
     └──> 03  Frontend Integration (depends on 02)

┌──────────┐
│   04     │  Image Metadata Processing (PARALLEL)
└────┬─────┘
     │
     ├──> 05  Citation Enrichment (depends on 04)
     │
     └──> 07  Database Indexing (depends on 05)
          │
          ├──> 06  CDN Upload (depends on 07)
          │
          ├──> 09  Image Linking (depends on 07)
          │
          └──> 08  RAG Integration (depends on 07, 09)
```

---

## Phase Breakdown

### Phase 1: Database Foundation (8 hours)

**Goal:** MCQs/OSCEs in PostgreSQL, API working, Frontend displaying

| Task | File | Duration | Priority |
|------|------|----------|----------|
| Database Seed | 01_database_seed_script.md | 4h | P0 |
| API Verification | 02_api_endpoint_verification.md | 2h | P0 |
| Frontend Integration | 03_frontend_integration.md | 2h | P0 |

**Success Criteria:**
- ✅ 1,000+ MCQs loaded in database
- ✅ 140+ OSCEs loaded in database
- ✅ API returns data for all endpoints
- ✅ Frontend displays MCQs/OSCEs correctly

---

### Phase 2: Image Processing (8 hours)

**Goal:** Medical images catalogued with metadata and citations

| Task | File | Duration | Priority |
|------|------|----------|----------|
| Metadata Processing | 04_image_metadata_processing.md | 3h | P1 |
| Citation Enrichment | 05_image_citation_enrichment.md | 2h | P1 |
| Database Indexing | 07_database_image_indexing.md | 3h | P1 |

**Success Criteria:**
- ✅ Unified metadata JSON created
- ✅ All images have source citations
- ✅ Images indexed in PostgreSQL
- ✅ Full-text search enabled

---

### Phase 3: Distribution & Linking (16 hours)

**Goal:** Images accessible via CDN, linked to content, RAG-enabled

| Task | File | Duration | Priority |
|------|------|----------|----------|
| CDN Upload | 06_cdn_upload_system.md | 4h | P1 |
| Image Linking | 09_image_content_linking.md | 8h | P0 |
| RAG Integration | 08_rag_integration.md | 4h | P2 |

**Success Criteria:**
- ✅ Images uploaded to Cloudflare R2
- ✅ 70%+ MCQs/OSCEs have images linked
- ✅ RAG returns images with text responses
- ✅ Image search by medical findings works

---

## Timeline

### Day 1 (8 hours)
```
09:00-10:00  Task 01: Seed script design & JSON parsing
10:00-12:00  Task 01: Database insertion logic
12:00-13:00  Lunch
13:00-14:00  Task 01: Testing & validation
14:00-16:00  Task 02: API endpoint verification
16:00-18:00  Task 03: Frontend integration testing
```

### Day 2 (8 hours)
```
09:00-12:00  Task 04: Image metadata processing (all sources)
12:00-13:00  Lunch
13:00-15:00  Task 05: Citation enrichment
15:00-18:00  Task 07: Database image indexing
```

### Day 3 (8 hours)
```
09:00-13:00  Task 06: CDN upload system (Cloudflare R2)
13:00-14:00  Lunch
14:00-18:00  Task 09: Automated image linking (Part 1)
```

### Day 4 (8 hours)
```
09:00-13:00  Task 09: Image linking verification & manual review
13:00-14:00  Lunch
14:00-18:00  Task 08: RAG integration & testing
```

---

## Data Sources

### Medical Images
- **HEAL:** Hematology, Dermatology, Cardiology (~1,200 images)
- **MedPix:** (Future) Comprehensive medical image database
- **NIH:** (Future) Chest X-rays, pathology
- **Z-Anatomy:** (Future) Anatomical images

### Educational Content
- **MCQs:** ~1,000 questions (data/mcqs/*.json)
- **OSCEs:** ~140 stations (data/osces/*.json)
- **RAG Chunks:** Qdrant vector database with medical text

---

## Technology Stack

### Backend
- **Database:** PostgreSQL 15+
- **ORM:** SQLAlchemy
- **API:** FastAPI
- **Image Processing:** Pillow, imageio
- **CDN:** Cloudflare R2
- **Vector DB:** Qdrant (for RAG)

### Frontend
- **Framework:** React 18+
- **API Client:** TanStack Query
- **Image Display:** LazyLoad, Lightbox

### Data Processing
- **Python:** 3.12+
- **Libraries:** pandas, json, pathlib
- **Matching:** FuzzyWuzzy (for topic matching)
- **Embeddings:** CLIP (for image RAG)

---

## Success Metrics

### Quantitative
- ✅ 100% of MCQs/OSCEs imported (1,000+ MCQs, 140+ OSCEs)
- ✅ 70%+ MCQs with relevant images linked
- ✅ 50%+ OSCEs with supporting images
- ✅ <2s image load time (via CDN)
- ✅ 95%+ image citation accuracy
- ✅ Multimodal RAG returns images in 80%+ queries

### Qualitative
- ✅ Images enhance learning (not distract)
- ✅ Citations meet Australian compliance
- ✅ Images display correctly on mobile/desktop
- ✅ Search finds relevant images by medical terms
- ✅ Manual verification confirms clinical accuracy

---

## Risk Mitigation

### Risk 1: Image-Content Mismatch
**Mitigation:**
- Automated matching for high-confidence (>80%) only
- Manual verification for all automated assignments
- Medical expert reviews final links

### Risk 2: Copyright/License Issues
**Mitigation:**
- Only use CC-BY-NC, Public Domain sources
- Proper attribution in all cases
- Legal review of HEAL license terms

### Risk 3: CDN Costs
**Mitigation:**
- Optimize image sizes (max 500KB)
- Use progressive JPEGs
- Monitor bandwidth usage
- Set cost alerts

### Risk 4: Database Performance
**Mitigation:**
- Index specialty, topic, tags columns
- Implement pagination (max 100 results)
- Use Redis caching for popular queries

### Risk 5: Missing Images for Some Specialties
**Mitigation:**
- Prioritize Cardiology, Hematology, Dermatology (have images)
- Download MedPix for Respiratory, Psychiatry (missing)
- Use placeholder images with "Image pending" note

---

## Rollback Procedures

### If Database Seed Fails
1. Drop all inserted MCQs/OSCEs
2. Restore from backup (if exists)
3. Fix JSON parsing errors
4. Re-run seed script

### If Image Linking Breaks
1. Clear all `image_url` fields
2. Clear all `supporting_documents` JSON
3. Reset `image_assignments` table
4. Restart matching process

### If CDN Upload Fails
1. Images remain in local storage
2. Use local file paths temporarily
3. Retry upload with exponential backoff
4. Contact Cloudflare support if persistent

---

## Testing Strategy

### Unit Tests
- Database seed functions
- JSON parsing logic
- Image metadata extraction
- Fuzzy matching algorithm

### Integration Tests
- API endpoints with real data
- Frontend displays MCQs with images
- CDN image retrieval
- RAG multimodal queries

### Manual Tests
- Medical expert reviews image assignments
- Clinical accuracy of image-content pairs
- Mobile/desktop responsiveness
- Accessibility (WCAG 2.2 AA)

---

## Deployment Checklist

### Pre-Deployment
- [ ] All tests passing (unit + integration)
- [ ] Database backup created
- [ ] CDN credentials configured
- [ ] Environment variables set

### Deployment Steps
1. [ ] Run database migrations
2. [ ] Run seed script (MCQs/OSCEs)
3. [ ] Process and index images
4. [ ] Upload images to CDN
5. [ ] Run image linking script
6. [ ] Integrate with RAG
7. [ ] Deploy frontend updates

### Post-Deployment
- [ ] Verify API health check
- [ ] Test random MCQ/OSCE display
- [ ] Check image CDN loading
- [ ] Monitor error logs (24 hours)
- [ ] Review analytics (image usage)

---

## Maintenance Plan

### Daily
- Monitor CDN bandwidth usage
- Check error logs for 404 images
- Verify database query performance

### Weekly
- Review new image assignments
- Update topic mapping table
- Check for broken CDN links

### Monthly
- Medical expert review of image quality
- Update image citations if sources change
- Optimize database indexes

---

## Future Enhancements

### Phase 4 (Future)
- **MedPix Integration:** Download 59,000+ images
- **Z-Anatomy:** 3D anatomical models
- **NIH Chest X-Ray:** 112,000+ chest radiographs
- **Video Support:** Procedural videos for OSCEs

### Phase 5 (Future)
- **AI Image Search:** CLIP-based semantic search
- **Image Annotations:** Highlight key findings
- **User-Generated Images:** Upload clinical photos
- **Mobile App:** Offline image access

---

## Team Responsibilities

### Developer (Primary)
- Implement all 9 tasks
- Write unit/integration tests
- Deploy to production
- Monitor performance

### Medical Expert (Reviewer)
- Verify image-content links
- Validate clinical accuracy
- Review citations
- Approve final assignments

### QA Tester
- Test all API endpoints
- Verify frontend display
- Check mobile responsiveness
- Accessibility testing

---

## Communication Plan

### Daily Standup
- Progress on current task
- Blockers/issues
- Plan for next task

### Weekly Review
- Completed tasks demonstration
- Metrics review
- Adjust timeline if needed

### Final Presentation
- Demo full system
- Show metrics achieved
- Discuss future roadmap

---

## Budget

### Development Time
- 32 hours × $75/hour = $2,400

### Infrastructure
- Cloudflare R2 Storage: ~$0.015/GB/month (~$5/month for 300GB)
- PostgreSQL: Existing (no additional cost)
- Qdrant: Existing (no additional cost)

### Total: ~$2,460 (one-time + $5/month ongoing)

---

## Success Declaration

Project considered successful when:
1. ✅ All 1,000+ MCQs and 140+ OSCEs in database
2. ✅ API endpoints returning data correctly
3. ✅ Frontend displaying MCQs/OSCEs with images
4. ✅ 70%+ images linked to relevant content
5. ✅ Images accessible via CDN (<2s load time)
6. ✅ RAG returns multimodal responses
7. ✅ Medical expert approves image assignments
8. ✅ Zero copyright/license violations
9. ✅ System passes accessibility audit
10. ✅ All tests passing (100%)

---

**Next Step:** Begin Task 01 - Database Seed Script
**File:** `01_database_seed_script.md`
