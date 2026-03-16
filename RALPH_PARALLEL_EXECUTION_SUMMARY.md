# Ralph Parallel Execution - EMR + AI OSCE Implementation

**Created**: 2026-02-28
**Status**: ✅ Ready to Execute
**Execution Mode**: Parallel (Both systems run simultaneously)

---

## 🎯 Overview

Ralph Loop automation has been configured to execute **TWO systems in parallel**:

1. **EMR Practice System** (Week 2-4, 67.5-73.5 hours)
2. **AI OSCE Simulation** (Week 3-8, 192-236 hours)

Both systems share:
- ✅ Week 1 infrastructure (Vault, Redis, HTTPS, JWT)
- ✅ Security test suite (35 total: 15 EMR + 20 OSCE)
- ✅ Claude API rate limit (90 req/min total)
- ✅ PostgreSQL database (user_progress table extended by both)

---

## 📊 Current Status

### System-by-System Breakdown

| System | Status | Current Phase | Next Action | Script |
|--------|--------|---------------|-------------|--------|
| **AI OSCE** | 🟢 PRD_001 Complete | Week 2: AI Integration | Start PRD_002 (AI Patient) | `ralph-week2-loop.sh` |
| **EMR** | 🟡 Ready to Start | Week 2: Critical Security | Start Phase 1 (8 hours) | `ralph-emr-loop.sh` |
| **Week 1 Infrastructure** | ✅ Complete | Shared Foundation | Monitoring | Week 1 deliverables |

### Progress Tracking

**AI OSCE**:
- ✅ PRD_001: Database & APIs (31/31 tests passing, 100%)
- 🔄 PRD_002: AI Integration (ready to start)
- ⏸️ PRD_003-005: Queued

**EMR**:
- 🔄 Phase 1: Critical Security (ready to start)
- ⏸️ Phase 2-6: Queued

**Shared Infrastructure** (Week 1):
- ✅ Vault operational
- ✅ Redis operational (namespaces: emr:*, osce:*)
- ✅ HTTPS enforced with 9 security headers
- ✅ JWT authentication configured
- ✅ Security test foundation (15 tests)

---

## 🚀 Execution Options

### Option A: Execute Both Systems in Parallel (Recommended)

**Terminal 1 - AI OSCE**:
```bash
cd /home/dev/Development/irStudy
./scripts/ralph-continue-prds.sh
# Copy the prompt and send to Claude Code in session 1
```

**Terminal 2 - EMR**:
```bash
cd /home/dev/Development/irStudy
./scripts/ralph-emr-loop.sh
# Copy the prompt and send to Claude Code in session 2
```

**Terminal 3 - Monitoring**:
```bash
# Watch unified state
watch -n 5 'cat .ralph-unified-state.json | jq .'

# Or watch individual systems
watch -n 5 'echo "=== AI OSCE ===" && cat .ralph-loop-state.json | jq .current_phase,.current_prd,.prd_001_completion && echo "=== EMR ===" && cat .ralph-emr-state.json | jq .current_phase,.current_task 2>/dev/null'
```

---

### Option B: Execute Sequentially (AI OSCE first, then EMR)

**Week 2-5: AI OSCE**:
```bash
./scripts/ralph-continue-prds.sh
# Complete PRD_002-005
```

**Week 6-8: EMR** (after AI OSCE complete):
```bash
./scripts/ralph-emr-loop.sh
# Execute Phase 1-6
```

---

### Option C: Manual Delegation (No Ralph automation)

Read the prompts from the scripts and manually delegate to agents:
- EMR: Read `scripts/ralph-emr-loop.sh` and delegate phases yourself
- AI OSCE: Read `scripts/ralph-continue-prds.sh` and delegate PRDs yourself

---

## 📁 File Structure Created

### Ralph Loop Scripts (5 scripts)

```
scripts/
├── ralph-emr-loop.sh          ✅ NEW - EMR implementation (15 KB)
├── ralph-week2-loop.sh        ✅ Existing - AI OSCE PRD_002-005 (3.3 KB)
├── ralph-continue-prds.sh     ✅ Existing - AI OSCE continuation (5.8 KB)
├── ralph-loop.sh              ✅ Existing - Generic RALPH framework (14 KB)
└── ralph-executor.sh          ✅ Existing - RALPH executor (9.9 KB)
```

### State Files (4 files)

```
.ralph-unified-state.json      ✅ NEW - Unified tracking (6.8 KB)
.ralph-emr-state.json          🔜 Created on first EMR execution
.ralph-loop-state.json         ✅ Existing - AI OSCE state (2.5 KB)
.ralph-status.json             ✅ Existing - Legacy status (951 B)
```

### Documentation (3 guides)

```
EMR_RALPH_QUICKSTART.md                  ✅ NEW - EMR quick start (12 KB)
RALPH_PARALLEL_EXECUTION_SUMMARY.md      ✅ NEW - This file
COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md  ✅ Existing - Master plan
```

---

## 🔗 Coordination Points (Critical!)

### 1. User Progress Table Migration

**Problem**: Both systems extend `user_progress` table

**EMR adds**:
- `emr_sessions_completed` (integer)
- `avg_soap_score` (float)
- `last_emr_activity` (datetime)

**AI OSCE adds**:
- `osce_attempts_count` (integer)
- `avg_osce_score` (float)
- `last_osce_activity` (datetime)
- `mock_exams_completed` (integer)

**Solution**: Create **combined Alembic migration** (one migration adding ALL 7 columns)

```bash
# Create combined migration
cd backend
alembic revision -m "add_emr_and_osce_user_progress_columns"

# Edit migration file to include all 7 columns from both systems
# See EMR_RALPH_QUICKSTART.md for example code
```

**When**: Before either system adds columns individually (coordinate timing!)

---

### 2. Claude API Rate Limits

**Shared Limit**: 90 req/min total (EMR + AI OSCE combined)

**Priority Queue**:
1. AI Patient (OSCE) - highest priority (real-time user interaction)
2. AI Examiner (OSCE) - medium priority (end of session)
3. EMR SOAP validator - lowest priority (background validation)

**Fallbacks**:
- EMR: Rule-based validator (70% accuracy, no API calls)
- AI OSCE: Kimi API (70% quality, separate rate limit)

**Monitoring**:
```bash
# Count Claude API calls in logs
grep "claude_api_call" ralph-emr.log ralph-week2.log | wc -l

# Alert if >90/min sustained
watch -n 60 'grep "claude_api_call" ralph-*.log | tail -90 | wc -l'
```

**If rate limit exceeded**: Increase fallback usage from 60% → 80%

---

### 3. Security Tests (Don't Duplicate!)

**Total Target**: 35 security tests (not 35 + 35!)

**EMR contributes**: 15 tests
- PHI encryption at rest
- PHI anonymization in Claude API
- Transaction handling
- HTTPS enforcement
- Prompt injection (EMR validator)
- Rate limiting
- ... (9 more EMR-specific)

**AI OSCE contributes**: 20 tests
- OSCE transcript encryption
- WebSocket JWT authentication
- WebSocket rate limiting
- Redis session encryption
- Prompt injection (AI Patient/Examiner)
- Session hijacking prevention
- ... (14 more OSCE-specific)

**Location**: `backend/tests/test_security/test_security_comprehensive.py`

**Coordination**: EMR adds to lines 1-200, AI OSCE adds to lines 201-400

---

## 📊 Monitoring Commands

### Unified State (Both Systems)

```bash
# Watch combined progress
watch -n 5 'cat .ralph-unified-state.json | jq .'

# Check system statuses
cat .ralph-unified-state.json | jq '.systems.emr.status, .systems.ai_osce.status'

# View coordination points
cat .ralph-unified-state.json | jq '.coordination_points'
```

---

### EMR-Specific Monitoring

```bash
# EMR state
cat .ralph-emr-state.json | jq .  # (created on first execution)

# EMR current phase
cat .ralph-emr-state.json | jq '.current_phase, .current_task'

# EMR quality gates
cat .ralph-emr-state.json | jq '.quality_gates'

# EMR logs
tail -f ralph-emr.log
```

---

### AI OSCE-Specific Monitoring

```bash
# AI OSCE state
cat .ralph-loop-state.json | jq .

# AI OSCE current PRD
cat .ralph-loop-state.json | jq '.current_prd, .current_task'

# AI OSCE completion status
cat .ralph-loop-state.json | jq '.prd_001_completion'

# AI OSCE logs
tail -f ralph-week2.log
```

---

### Performance Monitoring

```bash
# Test pass rates
cd backend
pytest tests/ -q --tb=no | tail -3

# API performance
cd backend
pytest tests/test_performance/ -v

# Frontend performance
cd frontend
npm run test:performance
```

---

## ✅ Success Criteria

### EMR Complete When:
- [ ] 328 tests passing (100% pass rate)
- [ ] Performance: <500ms submit, <1s dashboard, <200ms auto-save
- [ ] Security: 0 hardcoded credentials, PHI encrypted
- [ ] Accessibility: 56 WCAG 2.2 AA/AAA tests passing
- [ ] AI accuracy: ≥85% vs expert SOAP notes
- [ ] 18 critical fixes implemented
- [ ] 29 files created (8,849 lines)

### AI OSCE Complete When:
- [ ] PRD_002-005 implemented
- [ ] 360 patient personas validated by ≥2 clinicians
- [ ] AI Patient emotional intelligence working (6 states)
- [ ] AI Examiner scoring ±2 marks vs human (96%+ accuracy)
- [ ] Performance: <3s AI response, <500ms API, <100ms DB
- [ ] WebSocket sessions operational (8-min sessions)
- [ ] Mock exam mode functional (16 stations)
- [ ] ≥70% test coverage, 100% pass rate

### Platform-Wide Complete When:
- [ ] 500+ tests passing (EMR + AI OSCE combined)
- [ ] Unified progress dashboard operational
- [ ] OSCE-to-EMR converter working (≥70% pre-fill)
- [ ] Monthly costs <$200
- [ ] 99.5%+ uptime
- [ ] WCAG 2.2 AA compliance across all UIs
- [ ] Combined migration applied (user_progress extended)
- [ ] Security tests: 35/35 passing (15 EMR + 20 OSCE)

---

## 🎬 Recommended Execution Plan

### Day 1 (Today)

**Morning**:
1. ✅ Review this summary
2. ✅ Review `EMR_RALPH_QUICKSTART.md`
3. ✅ Execute: `./scripts/ralph-emr-loop.sh` (copy prompt for EMR)
4. ✅ Execute: `./scripts/ralph-continue-prds.sh` (copy prompt for AI OSCE)

**Afternoon**:
5. Send EMR prompt to Claude Code (Session 1)
6. Send AI OSCE prompt to Claude Code (Session 2)
7. Monitor both: `watch -n 5 'cat .ralph-unified-state.json | jq .'`

---

### Week 2 (EMR Phase 1-2 + AI OSCE PRD_002)

**EMR** (13 hours):
- Phase 1: Critical Security (8h) - Database encryption, PHI anonymization, transactions
- Phase 2: Reliability (5h) - Claude API fallback, health checks, DB constraints

**AI OSCE** (20-24 hours):
- PRD_002 Phase 1-5: AI Patient, Emotional State, RAG, AI Examiner, Integration Testing

**Coordination**:
- Create combined user_progress migration
- Monitor Claude API rate limits (90 req/min shared)
- Coordinate security tests (don't duplicate)

---

### Week 3 (EMR Phase 3-4 + AI OSCE PRD_003)

**EMR** (7.5 hours):
- Phase 3: Performance (4h) - Dashboard optimization, auto-save debounce
- Phase 4: Security Hardening (3.5h) - Prompt injection, rate limiting, error boundaries

**AI OSCE** (18-20 hours):
- PRD_003: WebSocket Infrastructure (8-min sessions, Redis sync, JWT auth)

---

### Week 4 (EMR Phase 5-6 + AI OSCE PRD_004)

**EMR** (34 hours):
- Phase 5: Testing (24h) - 56 WCAG tests, 35 OWASP tests (coordinate with OSCE), AI benchmark
- Phase 6: Integration (10h) - Dashboard API, theme switching, API contract standardization

**AI OSCE** (24-28 hours):
- PRD_004: Scoring System (AMC 15-mark rubric, golden dataset, critical errors)

---

### Week 5-8 (AI OSCE PRD_005 + Integration)

**EMR**: ✅ Complete, monitoring

**AI OSCE** (20-24 hours):
- PRD_005: Frontend Implementation (React UI, WebSocket chat, results display)

**Integration** (36-48 hours):
- OSCE-to-EMR converter
- Unified progress dashboard
- Cross-system E2E tests

---

## 📞 Support & Troubleshooting

### Common Issues

**Issue 1: Claude API rate limit exceeded**
- Check: `grep "RateLimitError" ralph-*.log`
- Fix: Increase fallback usage (EMR rule-based validator, OSCE Kimi API)

**Issue 2: user_progress migration conflict**
- Check: `psql -c "\d user_progress"`
- Fix: Create combined migration (see coordination section)

**Issue 3: Security tests duplicated**
- Check: `grep -c "def test_" backend/tests/test_security/test_security_comprehensive.py`
- Fix: Should be ~35 tests total, not 70+

**Issue 4: Tests failing after phase completion**
- Check: `pytest tests/ -q --tb=short`
- Fix: Re-delegate to agent with specific error message, **DO NOT proceed to next phase**

---

### Contact & Documentation

**Quick Start Guides**:
- EMR: `EMR_RALPH_QUICKSTART.md` (this directory)
- AI OSCE: `WEEK2_STATUS_SUMMARY.md` (already exists)
- Platform: `COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md`

**State Files**:
- Unified: `.ralph-unified-state.json` (both systems)
- EMR: `.ralph-emr-state.json` (EMR only)
- AI OSCE: `.ralph-loop-state.json` (AI OSCE only)

**Scripts**:
- EMR: `scripts/ralph-emr-loop.sh`
- AI OSCE: `scripts/ralph-continue-prds.sh`
- Security: `scripts/security-audit.sh`

**PRD Directories**:
- EMR: `16-feb-ralph-prds/` (14 PRDs)
- AI OSCE: `ai-osce-ralph-prds/` (8 PRDs)

---

## 🎯 Next Steps

1. **Review documentation** (this file + EMR_RALPH_QUICKSTART.md)

2. **Execute Ralph loops** (both systems in parallel):
   ```bash
   # Terminal 1 - EMR
   ./scripts/ralph-emr-loop.sh

   # Terminal 2 - AI OSCE
   ./scripts/ralph-continue-prds.sh
   ```

3. **Copy prompts** from script outputs and send to Claude Code

4. **Monitor progress**:
   ```bash
   watch -n 5 'cat .ralph-unified-state.json | jq .'
   ```

5. **Validate after each phase/PRD** using quality gates

6. **Coordinate** on user_progress migration, Claude API limits, security tests

7. **Final validation** when both systems complete

---

**Status**: ✅ Ready to Execute
**Created**: 2026-02-28
**Version**: 1.0
**Owner**: PM Coordinator
**Timeline**: Week 2-8 (6-7 weeks with parallel execution)
**Total Effort**: 259.5-309.5 hours (across both systems)

---

END OF RALPH PARALLEL EXECUTION SUMMARY
