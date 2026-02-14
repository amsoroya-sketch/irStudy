# Session Handover - AI OSCE Simulation Design
**Date:** 2026-02-09
**Session Type:** Architecture Design & Planning
**Status:** Design Complete, Ready for Implementation

---

## What We Accomplished

### Primary Deliverable
Created comprehensive integration architecture document for AI Patient/Examiner OSCE simulation system:
- **File:** `AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md`
- **Size:** ~40,000 words
- **Scope:** Complete technical specification from database schema to WebSocket protocols

### Key Decisions Made (User Confirmed)

1. **Data Architecture:**
   - Create NEW separate AI patient persona library (not reuse existing 140 OSCEs)
   - NEW dedicated tables: `patient_personas`, `osce_attempts`, `osce_scores`, `mock_exams`
   - EXTEND existing `user_progress` table with AI OSCE tracking columns

2. **Storage Strategy:**
   - **Dual storage:** Redis (active sessions) + PostgreSQL (permanent archive)
   - Background sync every 30 seconds during sessions
   - TTL: 30 minutes for Redis session data

3. **Exam Modes:**
   - **Individual Practice:** Single 8-minute OSCE, immediate feedback
   - **Mock Exam Mode:** 16 sequential stations, 2.5 hours, comprehensive scoring

4. **Technology Stack:**
   - **AI:** Claude 3.5 Sonnet (single LLM, dual personas: Patient + Examiner)
   - **RAG:** Existing Qdrant vector DB (42,647 medical chunks)
   - **Communication:** WebSocket real-time (existing infrastructure)
   - **Cost Target:** <$0.30 per OSCE session (achieved: $0.0445 with prompt caching)

---

## What's in the Architecture Document

### 1. Database Schema (Comprehensive)
- `patient_personas`: 360 rich AI profiles with emotional intelligence
- `osce_attempts`: Session tracking with conversation history
- `osce_scores`: AMC 15-mark rubric breakdown
- `mock_exams`: 16-station orchestration
- Integration: Extended `user_progress` with AI OSCE counters

### 2. Complete Data Flows
- **Individual Practice Flow:** 6 phases from persona selection → results display
- **Mock Exam Flow:** 16-station sequential progression
- Both flows documented with step-by-step WebSocket message examples

### 3. API Specifications
- 12 new endpoints documented with request/response examples
- WebSocket protocol defined (client ↔ server messages)
- Authentication: Inherits existing RBAC system

### 4. Redis Session Management
- Key structure defined (`osce:session:{attempt_id}:*`)
- Background sync job specification
- Session cleanup logic

### 5. Integration Points
- **Authentication:** Existing JWT + RBAC (4 new permissions)
- **Progress Tracking:** Extends user_progress table
- **RAG System:** Uses existing Qdrant infrastructure
- **AI Router:** Uses existing dual-provider system (Claude/Kimi)

### 6. Performance & Cost Analysis
- Latency target: <3s per AI response (95th percentile)
- Concurrent capacity: 100 simultaneous sessions
- Cost: $0.0445 per OSCE ($1,335/month at 1000 OSCEs/day)

### 7. Implementation Roadmap
- 9 phases over 13 weeks
- Phase 1: Database & APIs (Week 1)
- Phase 2-4: AI integration, WebSocket, scoring
- Phase 5-6: Frontend implementation
- Phase 7-9: Testing, content creation, launch

### 8. Appendices
- Sample patient persona JSON (CARD-001-CHEST-PAIN: Robert Chen)
- Sample conversation transcript with AI Examiner scoring report

---

## Technical Context

### Existing Infrastructure (Already Running)
```
PostgreSQL: port 5433 (amc-postgres-dev) - HEALTHY
Redis Cluster: 6 nodes, ports 7379-7384 - HEALTHY
Vault: port 8200 (unsealed) - HEALTHY
Backend API: 90% complete (30 endpoints)
WebSocket auth: 100% complete (zero-trust security)
RBAC: 100% complete (24 permissions, 3 roles)
Frontend: 30% complete (MCQ interface done)
Content: 940 questions, 3,168 images, 42,647 RAG chunks
```

### What This New System Adds
- **AI Patient:** Realistic patient simulation with emotional states
- **AI Examiner:** Automated AMC 15-mark rubric scoring
- **8-minute OSCE sessions:** Individual practice mode
- **16-station mock exams:** Full exam simulation
- **WebSocket real-time chat:** Student ↔ AI Patient conversation

### Integration Strategy
- **Reuse:** Auth, RBAC, WebSocket, RAG, AI Router (all existing)
- **New:** Database tables, AI prompts, scoring logic, session orchestration
- **Extend:** user_progress table with AI OSCE tracking

---

## User's Original Vision

**From User's Request:**
> "AI based amc clinical exam system, using AI for patient, examiner and student"

**Clarifications:**
- Student = Human user (taking the exam)
- AI Patient = Simulated patient with realistic emotions/symptoms
- AI Examiner = Automated scoring using AMC rubric
- Purpose: AMC Clinical Exam practice (NOT development tools)

**User Explicitly Rejected:**
- Agent OS approach (that's for coding, not medical simulation)
- Reusing existing OSCE content (want separate persona library)

---

## Next Steps for Implementation

### Immediate Actions (Week 1)
1. **Database Setup:**
   ```bash
   # Create Alembic migration
   cd backend
   alembic revision --autogenerate -m "add_ai_osce_tables"
   alembic upgrade head
   ```

2. **Seed Sample Data:**
   - Create 5 sample patient personas (one per specialty for testing)
   - Validate database schema with sample OSCE attempt

3. **API Scaffolding:**
   - Create FastAPI routers: `backend/src/api/v1/patient_personas.py`
   - Create FastAPI routers: `backend/src/api/v1/osce_sessions.py`
   - Create Pydantic schemas: `backend/src/schemas/persona.py`, `osce.py`

### Week 2-3 Priorities
- AI prompt engineering (Patient system prompts with emotional states)
- WebSocket conversation loop implementation
- Redis session management
- Background sync job (Celery task)

### Phase 1 Success Criteria
- [ ] Database tables created and tested
- [ ] Can create patient persona via API
- [ ] Can start OSCE session and get WebSocket URL
- [ ] Sample conversation works end-to-end (student → AI Patient → response)
- [ ] Session data saved to PostgreSQL

---

## Key Files to Review

### Architecture & Planning
- `AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md` (THIS SESSION - main deliverable)
- `COMPREHENSIVE_PLATFORM_PLAN.md` (overall product roadmap)
- `WHATS_NEXT.md` (project status summary)

### Existing Infrastructure
- `backend/src/websocket/` (WebSocket auth, rate limiting, connection tracking)
- `backend/src/ai_router/` (Dual AI provider: Claude/Kimi)
- `backend/src/auth/` (JWT, RBAC, permissions)
- `docker-compose.yml` (PostgreSQL, Redis, Vault services)

### Constraints & Standards
- `PROJECT_CONSTRAINTS.md` (development requirements)
- `CLAUDE.md` (project-specific and global instructions)

---

## Questions to Confirm in Next Session

Before starting implementation, confirm:

1. **Content Strategy:**
   - Who will create the 360 patient personas? (Clinical experts?)
   - Timeline for persona validation and approval?

2. **Pricing Model:**
   - Is AI OSCE practice included in all tiers, or premium feature?
   - Mock exam access: paid feature or available to all?

3. **Clinical Validation:**
   - Who will validate the Golden Dataset (200 scenarios)?
   - How often to recalibrate AI Examiner scoring?

4. **Launch Timeline:**
   - Target launch date for Phase 1 (basic individual practice)?
   - Beta testing with real students before full launch?

---

## Technical Debt & Risks

### Known Challenges
1. **Cost Management:** Claude API costs could exceed budget at scale
   - Mitigation: Circuit breaker to free Kimi, daily budget alerts
2. **Scoring Consistency:** AI Examiner must match human examiners
   - Mitigation: Golden Dataset validation, quarterly recalibration
3. **Medical Accuracy:** AI Patient must not give incorrect information
   - Mitigation: RAG integration, expert validation, monthly audits

### Dependencies
- Existing infrastructure must remain stable (PostgreSQL, Redis, WebSocket)
- Claude 3.5 Sonnet API availability (fallback to Kimi if needed)
- Clinical expert availability for persona validation

---

## Current Project Status

### Infrastructure: 80% Complete
- Backend API, database, auth, WebSocket, RBAC all operational
- RAG system indexed and working (42,647 chunks)
- Docker services healthy

### AI System: 10% → 15% (after this session)
- **Before:** No AI OSCE design
- **After:** Complete architecture designed, ready for implementation
- **Remaining:** Actual coding, testing, content creation

### Content: Complete for MCQs/Study Cards
- 940 questions with images
- RAG indexed
- AI OSCE content: 0% (need to create 360 personas)

---

## Command to Start Next Session

```bash
# Review the architecture document
cat AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md

# Check infrastructure status
docker ps
docker compose logs -f amc-postgres-dev  # Verify database healthy

# Start backend development environment
cd backend
source venv/bin/activate
alembic current  # Check current migration state

# Ready to create first migration for AI OSCE tables
alembic revision --autogenerate -m "add_ai_osce_tables"
```

---

## Summary for Next Developer/Session

**In one sentence:** We designed a complete AI OSCE simulation system where students practice 8-minute clinical exams with AI-powered patients that have realistic emotions, scored automatically by an AI examiner using the AMC 15-mark rubric, integrated with existing infrastructure via new database tables and WebSocket real-time communication.

**What's ready:** Complete technical specification (database, APIs, data flows, cost analysis, roadmap)

**What's needed:** Implementation starting with Phase 1 (database tables + basic APIs)

**Estimated effort:** 13 weeks for full implementation (Phases 1-9)

**Next milestone:** Week 1 - Create database tables and test with sample persona

---

## Contact & Escalation

**If blocked on:**
- Clinical validation: Escalate to clinical advisor
- Infrastructure issues: Check `docker compose logs`
- Cost concerns: Review `AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md` Section 7.3
- Technical decisions: Reference architecture document Section 1-6

**For questions about design rationale:**
- Why dual storage (Redis + PostgreSQL)? See Section 3.1, Section 5
- Why Claude 3.5 Sonnet? See conversation summary in this file
- Why new tables vs reusing existing? User decision confirmed via AskUserQuestion

---

**Session Status:** COMPLETE ✓
**Next Action:** Begin Phase 1 implementation (database tables)
**Ready to Handover:** YES

---

**END OF HANDOVER**
