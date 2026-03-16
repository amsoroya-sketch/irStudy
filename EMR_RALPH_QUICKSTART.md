# EMR Ralph Loop - Quick Start Guide

**Created**: 2026-02-28
**Purpose**: Execute EMR Practice System implementation in parallel with AI OSCE

---

## 🎯 What This Does

The EMR Ralph Loop automates the implementation of **18 critical fixes** across **6 phases** (Week 2-4, 67.5-73.5 hours):

1. **Phase 1**: Critical Security (8h) - Database encryption, PHI anonymization, transactions
2. **Phase 2**: Reliability (5h) - Claude API fallback, health checks, DB constraints
3. **Phase 3**: Performance (4h) - Dashboard optimization, auto-save debounce
4. **Phase 4**: Security Hardening (3.5h) - Prompt injection, rate limiting, error boundaries
5. **Phase 5**: Testing (24h) - 56 WCAG tests, 35 OWASP tests, AI benchmark dataset
6. **Phase 6**: Integration (10h) - Dashboard API, theme switching, API standardization

**Final Deliverables**: 328 tests passing, <500ms submit, PHI encrypted, WCAG 2.2 AA compliant

---

## 🚀 Quick Start (3 Options)

### Option A: Autonomous Execution (Recommended)

```bash
cd /home/dev/Development/irStudy

# Execute the Ralph loop script
./scripts/ralph-emr-loop.sh

# The script will output a comprehensive prompt
# Copy the prompt and send to Claude Code in a separate session
```

### Option B: Direct Prompt Execution

```bash
# Read the prompt from the script
cat scripts/ralph-emr-loop.sh | grep -A 500 "RALPH_PROMPT="

# Copy the RALPH_PROMPT content and send directly to Claude Code
```

### Option C: Manual Phase-by-Phase

Execute each phase manually by reading the script and delegating to agents yourself.

---

## 📊 Monitoring Progress

### Real-time State Monitoring

```bash
# Watch EMR progress
watch -n 5 'cat .ralph-emr-state.json | jq .'

# Watch AI OSCE progress (parallel execution)
watch -n 5 'cat .ralph-loop-state.json | jq .'

# Watch unified state (both systems)
watch -n 5 'cat .ralph-unified-state.json | jq .'
```

### Check Logs

```bash
# EMR implementation log
tail -f ralph-emr.log

# AI OSCE implementation log
tail -f ralph-week2.log
```

### Tmux Sessions (if running in tmux)

```bash
# Attach to EMR session
tmux attach -t ralph-emr

# Attach to AI OSCE session
tmux attach -t ralph-week2
```

---

## ✅ Quality Gates (Run After Each Phase)

### After Phase 1 (Critical Security)

```bash
cd backend

# Type checking
python -m mypy src/security/ --strict

# Security tests
pytest tests/test_security/test_emr_security.py -v

# Credential scan
grep -r "sk-ant-\|secret.*=.*['\"]" src/security/ || echo "✅ No hardcoded credentials"

# Australian compliance
grep -ri "acetaminophen\|tylenol\|albuterol" src/ || echo "✅ Australian terminology only"
```

**Pass Criteria**: 10/10 tests, 0 hardcoded creds, 0 American terms, mypy passes

---

### After Phase 2 (Reliability)

```bash
cd backend

# Health check endpoint
pytest tests/test_api/test_health.py -v

# Claude API fallback
pytest tests/test_services/test_fallback_validator.py -v

# Database constraints
pytest tests/test_db/test_constraints.py -v
```

**Pass Criteria**: All tests passing, health endpoint responds, fallback works

---

### After Phase 3 (Performance)

```bash
cd frontend

# Dashboard performance test
npm run test:performance

# Auto-save test
npm run test:auto-save

cd ../backend

# Performance benchmarks
pytest tests/test_performance/ -v
```

**Pass Criteria**: Dashboard <1s, Auto-save <200ms, Submit <500ms

---

### After Phase 4 (Security Hardening)

```bash
cd backend

# Prompt injection tests
pytest tests/test_security/test_prompt_injection.py -v

# Rate limiting tests
pytest tests/test_middleware/test_rate_limiting.py -v

cd ../frontend

# Error boundary tests
npm run test:error-boundaries
```

**Pass Criteria**: Prompt injection blocked, rate limiting active, error boundaries working

---

### After Phase 5 (Testing)

```bash
cd backend

# All backend tests
pytest tests/ -v --cov=src --cov-report=term-missing

cd ../frontend

# Accessibility tests
npm run test:a11y

# Target: 56/56 WCAG tests passing
```

**Pass Criteria**: 328/328 tests passing (100%), 56 WCAG tests pass, 0 axe-core violations

---

### After Phase 6 (Integration) - FINAL

```bash
cd backend

# Full test suite
pytest tests/ -v --cov=src --cov-report=html

# Security audit
../scripts/security-audit.sh

# Performance benchmarks
pytest tests/test_performance/ -v

cd ../frontend

# Full frontend tests
npm test

# Accessibility tests
npm run test:a11y

# Type checking
npx tsc --noEmit
```

**Pass Criteria**:
- ✅ 328/328 tests passing (100%)
- ✅ Performance: <500ms submit, <1s dashboard, <200ms auto-save
- ✅ Security: 0 hardcoded creds, PHI encrypted, HTTPS enforced
- ✅ Accessibility: 56 WCAG 2.2 AA/AAA tests passing, 0 violations
- ✅ AI accuracy: ≥85% vs expert SOAP notes

---

## 🔗 Coordination with AI OSCE

EMR runs **in parallel** with AI OSCE. Coordinate on:

### 1. User Progress Migration

Both systems extend `user_progress` table. Create **combined migration**:

```python
# Combined Alembic migration
def upgrade():
    # EMR columns
    op.add_column('user_progress', sa.Column('emr_sessions_completed', sa.Integer(), server_default='0'))
    op.add_column('user_progress', sa.Column('avg_soap_score', sa.Float(), nullable=True))
    op.add_column('user_progress', sa.Column('last_emr_activity', sa.DateTime(), nullable=True))

    # AI OSCE columns
    op.add_column('user_progress', sa.Column('osce_attempts_count', sa.Integer(), server_default='0'))
    op.add_column('user_progress', sa.Column('avg_osce_score', sa.Float(), nullable=True))
    op.add_column('user_progress', sa.Column('last_osce_activity', sa.DateTime(), nullable=True))
    op.add_column('user_progress', sa.Column('mock_exams_completed', sa.Integer(), server_default='0'))
```

### 2. Claude API Rate Limits

Shared limit: **90 req/min total**

**Priority**: AI Patient > AI Examiner > EMR validator

**Monitoring**:
```bash
# Check API usage
grep "claude_api_call" ralph-emr.log ralph-week2.log | wc -l
```

**If rate limit hit**: Increase fallback usage (EMR rule-based validator, OSCE Kimi API)

### 3. Security Tests

Total: **35 tests** (15 EMR + 20 AI OSCE)

**DO NOT duplicate** - extend `backend/tests/test_security/test_security_comprehensive.py`

EMR adds:
- `test_emr_phi_encrypted_at_rest()`
- `test_emr_phi_anonymized_in_claude_api()`
- `test_emr_transaction_rollback()`
- ... (12 more EMR-specific tests)

AI OSCE adds:
- `test_osce_transcript_encrypted()`
- `test_websocket_jwt_auth()`
- `test_osce_prompt_injection_blocked()`
- ... (17 more OSCE-specific tests)

---

## 📁 File Structure

### EMR Implementation Files (29 files, 8,849 lines)

**Backend** (5 files, 1,170 lines):
- `backend/src/security/encryption.py` (220 lines)
- `backend/src/security/phi_anonymizer.py` (180 lines)
- `backend/src/services/emr/validators/fallback_validator.py` (180 lines)
- `backend/src/api/v1/health.py` (120 lines)
- `backend/tests/fixtures/gold_standard_soap_notes.json` (500 lines)

**Frontend** (4 files, 811 lines):
- `frontend/src/context/ThemeContext.tsx` (172 lines)
- `frontend/src/components/ErrorBoundary.tsx` (222 lines)
- `frontend/src/hooks/useEMRDashboardData.ts` (202 lines)
- `frontend/src/hooks/useAutoSave.ts` (215 lines)

**Security** (7 files, 2,122 lines):
- `scripts/security-audit.sh` (212 lines)
- `backend/src/core/vault.py` (189 lines) - ✅ Already exists from Week 1
- `backend/src/middleware/https_redirect.py` (136 lines) - ✅ Already exists
- `backend/tests/test_security/test_emr_security.py` (150 lines) - NEW
- ... (3 more documentation files)

**Testing** (4 files, 2,128 lines):
- `testing/playwright/tests/accessibility/a11y-epic-ui.spec.ts` (477 lines)
- `testing/playwright/tests/accessibility/a11y-cerner-ui.spec.ts` (372 lines)
- `backend/tests/security/test_penetration.py` (679 lines)
- `testing/MANUAL_ACCESSIBILITY_TESTING.md` (600 lines)

---

## 🎯 Success Criteria

### EMR Implementation Complete When:

- [ ] All 18 critical fixes implemented
- [ ] 29 implementation files created (8,849 lines)
- [ ] 328 tests passing (100% pass rate)
- [ ] Performance: <500ms submit, <1s dashboard, <200ms auto-save
- [ ] Security: 0 hardcoded credentials, PHI encrypted, HTTPS enforced
- [ ] Accessibility: 56 WCAG 2.2 AA/AAA tests passing, 0 axe-core violations
- [ ] AI accuracy: ≥85% vs 100 expert-graded SOAP notes
- [ ] Dashboard optimization: 2s → 500-700ms (70% faster)
- [ ] Auto-save efficiency: 60 API calls/min → 2-3 calls/min (95% reduction)

### Platform-Wide (EMR + AI OSCE) Complete When:

- [ ] 500+ tests passing across both systems
- [ ] Unified progress dashboard operational
- [ ] OSCE-to-EMR converter working (≥70% pre-fill)
- [ ] Monthly costs <$200
- [ ] 99.5%+ uptime
- [ ] WCAG 2.2 AA compliance across all UIs

---

## 📞 Troubleshooting

### Issue: Claude API rate limit exceeded

**Symptom**: `RateLimitError: 90 requests/minute exceeded`

**Solution**:
1. Check usage: `grep "claude_api_call" ralph-*.log | wc -l`
2. Increase fallback: EMR rule-based validator (60% → 70% usage)
3. Upgrade Claude tier: Tier 2 ($500/month, 200 req/min)

---

### Issue: user_progress migration conflict

**Symptom**: `Alembic error: column "emr_sessions_completed" already exists`

**Solution**:
1. Check existing columns: `psql -c "\d user_progress"`
2. Create combined migration (see "Coordination" section above)
3. Drop conflicting migration: `alembic downgrade -1`

---

### Issue: Tests failing after Phase 1

**Symptom**: `pytest tests/test_security/ -v` shows failures

**Solution**:
1. Check specific failure: `pytest tests/test_security/test_emr_security.py::test_phi_encrypted -v`
2. Review agent implementation
3. Re-delegate to rust-ffi-expert with specific error message
4. **DO NOT proceed to Phase 2 until Phase 1 passes**

---

### Issue: Hardcoded credentials detected

**Symptom**: `grep -r "sk-ant-" src/` returns matches

**Solution**:
1. Identify file: `grep -rn "sk-ant-" src/`
2. Replace with Vault call: `get_vault_secret("secret/emr/claude-api-key", "value")`
3. Re-run credential scan
4. **BLOCK deployment until 0 hardcoded credentials**

---

## 📚 Reference Documents

**Master Plans**:
- `COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md` - Overall platform strategy
- `COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md` - EMR-specific implementation details

**PRD Directory**:
- `16-feb-ralph-prds/` - 14 EMR PRDs (backend, frontend, integration, testing)

**State Files**:
- `.ralph-emr-state.json` - EMR-specific state
- `.ralph-loop-state.json` - AI OSCE state
- `.ralph-unified-state.json` - Combined platform state

**Logs**:
- `ralph-emr.log` - EMR implementation log
- `ralph-week2.log` - AI OSCE implementation log

**Scripts**:
- `scripts/ralph-emr-loop.sh` - This EMR Ralph loop
- `scripts/ralph-week2-loop.sh` - AI OSCE Ralph loop (parallel execution)
- `scripts/security-audit.sh` - Automated security scanning

---

## 🎬 Next Steps

1. **Execute Ralph Loop**:
   ```bash
   ./scripts/ralph-emr-loop.sh
   ```

2. **Copy the output prompt** and send to Claude Code

3. **Monitor progress**:
   ```bash
   watch -n 5 'cat .ralph-emr-state.json | jq .'
   ```

4. **Validate after each phase** using quality gates above

5. **Coordinate with AI OSCE** on user_progress migration, Claude API limits, security tests

6. **Final validation** after Phase 6 - all 328 tests passing

---

**Status**: ✅ Ready to Execute
**Created**: 2026-02-28
**Version**: 1.0
**Owner**: PM Coordinator

---

END OF EMR RALPH QUICKSTART GUIDE
