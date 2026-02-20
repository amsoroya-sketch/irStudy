# AI OSCE Simulation - RALPH PRDs

**Created**: 2026-02-16
**Status**: In Progress
**Total PRDs**: 8
**Estimated Timeline**: 13 weeks (Phases 1-9)

---

## Overview

This directory contains 8 RALPH (Request, Architecture, Loop, Plan, Handoff) PRDs for implementing the AI OSCE Simulation System as defined in `AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md`.

## PRD Structure

Each PRD follows the RALPH format:
- **R - REQUEST**: User story, business value, success metrics
- **A - ARCHITECTURE**: Technical design, API specs, database schema
- **L - LOOP**: 3-phase iterative plan (Foundation → Core → Polish)
- **P - PLAN**: Detailed task breakdown (1-2 hour chunks)
- **H - HANDOFF**: Acceptance criteria, testing, documentation

## PRD List & Dependencies

### Foundation Layer (Week 1-2)
1. **PRD_AI_OSCE_001_DATABASE_AND_APIS.md** (P0-Critical)
   - 4 tables: patient_personas, osce_attempts, osce_scores, mock_exams
   - User progress integration
   - CRUD APIs for personas
   - Session creation API
   - **Dependencies**: None
   - **Blocks**: All other PRDs

### AI Integration Layer (Week 2-4)
2. **PRD_AI_OSCE_002_AI_INTEGRATION.md** (P0-Critical)
   - AI Patient system prompts (emotional intelligence)
   - AI Examiner scoring prompts (AMC 15-mark rubric)
   - RAG integration with Qdrant
   - AI Router integration (Claude/Kimi)
   - **Dependencies**: PRD_001 (database schema)
   - **Blocks**: PRD_003, PRD_004

3. **PRD_AI_OSCE_003_WEBSOCKET_INFRASTRUCTURE.md** (P0-Critical)
   - Real-time conversation loop
   - 8-minute timer with warnings
   - Redis session management
   - Background sync to PostgreSQL
   - **Dependencies**: PRD_001, PRD_002
   - **Blocks**: PRD_005, PRD_006

### Scoring & Frontend Layer (Week 4-6)
4. **PRD_AI_OSCE_004_SCORING_SYSTEM.md** (P1-High)
   - AMC 15-mark rubric implementation
   - Critical error detection
   - Golden Dataset validation
   - Feedback generation
   - **Dependencies**: PRD_002 (AI Examiner), PRD_003 (session data)
   - **Blocks**: PRD_005

5. **PRD_AI_OSCE_005_FRONTEND_IMPLEMENTATION.md** (P1-High)
   - Persona browsing page
   - Chat interface with timer
   - Results display with score breakdown
   - Transcript viewer
   - **Dependencies**: PRD_001, PRD_003, PRD_004
   - **Blocks**: PRD_006

### Advanced Features (Week 7-8)
6. **PRD_AI_OSCE_006_MOCK_EXAM_MODE.md** (P2-Medium)
   - 16-station orchestration
   - Station progression logic
   - Overall scoring calculation
   - Comprehensive report generation
   - **Dependencies**: PRD_005 (frontend foundation)
   - **Blocks**: None

### Quality Assurance (Week 8)
7. **PRD_AI_OSCE_007_TESTING_VALIDATION.md** (P1-High)
   - Load testing (100 concurrent sessions)
   - Golden Dataset (200 scenarios)
   - AI vs human examiner comparison
   - Security testing
   - **Dependencies**: All above PRDs
   - **Blocks**: PRD_008

### Content Layer (Week 9-12)
8. **PRD_AI_OSCE_008_CONTENT_CREATION.md** (P2-Medium)
   - 360 patient personas (45 per specialty)
   - Expert clinician validation
   - Progressive disclosure scripts
   - Emotional profile tuning
   - **Dependencies**: PRD_007 (validation framework)
   - **Blocks**: Production launch

## Dependency Graph

```
PRD_001 (Database & APIs)
    ↓
    ├──→ PRD_002 (AI Integration)
    │        ↓
    │        ├──→ PRD_003 (WebSocket)
    │        │        ↓
    │        │        ├──→ PRD_005 (Frontend)
    │        │        │        ↓
    │        │        │        └──→ PRD_006 (Mock Exam)
    │        │        │
    │        │        └──→ PRD_004 (Scoring)
    │        │                 ↓
    │        │                 └──→ PRD_005
    │        │
    │        └──→ PRD_004 (Scoring)
    │
    └──→ PRD_007 (Testing) → PRD_008 (Content)
```

## Implementation Phases

### Phase 1: Foundation (Week 1)
- PRD_001: Database Migration
- Target: All tables created, indexes optimized

### Phase 2: AI Core (Week 2-3)
- PRD_002: AI Patient/Examiner integration
- Target: AI responds realistically to student messages

### Phase 3: Real-time Infrastructure (Week 3-4)
- PRD_003: WebSocket + Redis
- Target: 8-minute sessions with live conversation

### Phase 4: Scoring & UI (Week 4-6)
- PRD_004: AMC rubric scoring
- PRD_005: Frontend interface
- Target: Students can practice individual OSCEs end-to-end

### Phase 5: Mock Exams (Week 7)
- PRD_006: 16-station orchestration
- Target: Full mock exam mode functional

### Phase 6: Quality Assurance (Week 8)
- PRD_007: Load testing, Golden Dataset validation
- Target: 100 concurrent sessions, 96%+ AI accuracy

### Phase 7: Content Creation (Week 9-12)
- PRD_008: 360 personas across 8 specialties
- Target: Production-ready content library

### Phase 8: Production Launch (Week 13)
- Deploy to production
- Monitor first 100 sessions
- Iterate based on feedback

## Success Metrics

### Technical
- Latency: <3s AI response (p95)
- Uptime: 99.5%+
- Cost: <$0.30 per OSCE session
- Concurrent capacity: 100+ sessions

### User Experience
- Session completion: >90%
- Pass rate: 60-70% (AMC standard)
- User satisfaction: >4.0/5.0
- Mock exam adoption: 30%+ of users

### Clinical
- Scoring consistency: AI within ±2 marks of human examiner
- Emotional realism: >80% report "AI felt realistic"
- Clinical accuracy: 0 major errors (monthly audit)

## Key Documents

### Source Architecture
- `../AI_OSCE_SIMULATION_INTEGRATION_ARCHITECTURE.md` (main architecture, 2,128 lines)
- `../AI_OSCE_TECHNICAL_REVIEW_PART1.md` (database & API review)
- `../AI_OSCE_TECHNICAL_REVIEW_PART2.md` (WebSocket & AI review)
- `../AI_OSCE_SECURITY_REVIEW.md` (security requirements)
- `../AI_OSCE_CLINICAL_REVIEW_REPORT.md` (clinical accuracy)

### Project Constraints
- `../constraints/README.md` (modular constraint system)
- `../PROJECT_CONSTRAINTS.md` (legacy constraints)
- `../ZERO_ERROR_POLICY.md` (quality gates)
- `../SECURITY_REVIEW_PROTOCOL.md` (security checklist)

### Templates
- `RALPH_PRD_TEMPLATE.md` (PRD template)
- `../16-feb-ralph-prds/backend/PRD_BACKEND_001_EMR_DATABASE_MIGRATION.md` (example PRD)

## PRD Authors

- **PRD_001**: Backend Expert (database schema, migrations)
- **PRD_002**: AI/LLM Expert + RAG Expert (AI integration)
- **PRD_003**: Backend Expert + Real-time Systems Expert (WebSocket)
- **PRD_004**: ABA Clinical Expert + AI Expert (AMC rubric)
- **PRD_005**: Frontend Expert (React, Material-UI)
- **PRD_006**: Backend Expert + Frontend Expert (orchestration)
- **PRD_007**: Testing QA Expert (load testing, validation)
- **PRD_008**: ABA Clinical Expert + Content Strategy Expert (personas)

## Status Tracking

See `IMPLEMENTATION_STATUS.md` for current progress.

## Security Notes

**CRITICAL**: All PRDs must address:
1. No hardcoded credentials (use Vault/environment variables)
2. Conversation data encryption at rest (Fernet encryption)
3. PHI anonymization in logs (use PHIAnonymizer utility)
4. Prompt injection protection (sanitize student input)
5. Rate limiting on WebSocket connections
6. GDPR compliance (data retention, right to deletion)

## Quality Gates

All PRDs must pass:
- [ ] 0 errors, 0 warnings (flutter analyze for frontend, mypy for backend)
- [ ] 100% test pass rate
- [ ] ≥70% test coverage
- [ ] 0 security violations (bandit, safety scans)
- [ ] Performance targets met (<3s latency, <$0.30 cost)
- [ ] Australian medical compliance (AMC rubric, terminology)

---

**Last Updated**: 2026-02-16
**Version**: 1.0
**Coordinator**: PM (Project Manager)
