#!/bin/bash
#
# Ralph Loop - EMR Practice System Implementation
# Runs in parallel with AI OSCE Week 2 implementation
# Executes 14 EMR PRDs across 6 phases (Week 2-4)
#
# Reference: COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md
# Timeline: 67.5-73.5 hours across 3 weeks
#

set -euo pipefail

PROJECT_ROOT="/home/dev/Development/irStudy"
STATE_FILE="$PROJECT_ROOT/.ralph-emr-state.json"
LOG_FILE="$PROJECT_ROOT/ralph-emr.log"
TMUX_SESSION="ralph-emr"

cd "$PROJECT_ROOT"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "==================================================================="
echo "RALPH LOOP - EMR Practice System Implementation"
echo "==================================================================="
echo "Started: $(date)"
echo ""

# Initialize EMR state file
init_emr_state() {
    cat > "$STATE_FILE" << 'EOF'
{
  "session_start": "",
  "current_phase": "Week 2: EMR Critical Security",
  "current_cycle": 0,
  "max_cycles": 14,
  "prd_queue": [
    "16-feb-ralph-prds/backend/PRD_BACKEND_001_DATABASE_MIGRATION.md",
    "16-feb-ralph-prds/backend/PRD_BACKEND_002_SESSION_MANAGEMENT_API.md",
    "16-feb-ralph-prds/backend/PRD_BACKEND_003_VALIDATION_API.md",
    "16-feb-ralph-prds/backend/PRD_BACKEND_004_TEMPLATE_LIBRARY_API.md",
    "16-feb-ralph-prds/backend/PRD_BACKEND_005_DASHBOARD_ANALYTICS_API.md",
    "16-feb-ralph-prds/frontend/PRD_FRONTEND_001_EPIC_EMR_UI.md",
    "16-feb-ralph-prds/frontend/PRD_FRONTEND_002_CERNER_EMR_UI.md",
    "16-feb-ralph-prds/frontend/PRD_FRONTEND_003_DASHBOARD.md"
  ],
  "completed_prds": [],
  "current_prd": null,
  "current_task": "Start Phase 1: Critical Security (8 hours)",
  "ralph_stages": {
    "request": "pending",
    "architecture": "pending",
    "loop": "pending",
    "plan": "pending",
    "handoff": "pending"
  },
  "implementation_phases": {
    "phase_1_critical_security": {
      "status": "ready",
      "effort_hours": 8,
      "fixes": ["#2 Database encryption", "#5 PHI anonymization", "#1 Transaction handling"],
      "agent": "rust-ffi-expert"
    },
    "phase_2_reliability": {
      "status": "pending",
      "effort_hours": 5,
      "fixes": ["#3 Claude API fallback", "#9 Health checks", "#8 DB constraints"],
      "agent": "rust-ffi-expert"
    },
    "phase_3_performance": {
      "status": "pending",
      "effort_hours": 4,
      "fixes": ["Frontend #3 Dashboard parallel requests", "Frontend #4 Auto-save debounce"],
      "agent": "flutter-desktop-expert"
    },
    "phase_4_security_hardening": {
      "status": "pending",
      "effort_hours": 3.5,
      "fixes": ["#6 Prompt injection", "#7 Rate limiting", "Frontend #5 Error boundaries"],
      "agent": "rust-ffi-expert + flutter-desktop-expert"
    },
    "phase_5_testing": {
      "status": "pending",
      "effort_hours": 24,
      "fixes": ["#11 AI benchmark dataset", "56 WCAG tests", "35 OWASP tests"],
      "agent": "testing-qa-expert"
    },
    "phase_6_integration": {
      "status": "pending",
      "effort_hours": 10,
      "fixes": ["PRD_BACKEND_005", "Frontend #2 Theme switching", "Frontend #6 API contract"],
      "agent": "rust-ffi-expert + flutter-desktop-expert"
    }
  },
  "quality_gates": {
    "vault_operational": true,
    "redis_operational": true,
    "security_tests_pass": false,
    "zero_hardcoded_creds": false,
    "phi_encrypted": false,
    "https_enforced": true,
    "performance_targets_met": false,
    "accessibility_tests_pass": false,
    "total_tests_passing": 0,
    "total_tests_expected": 328
  },
  "artifacts": {
    "backend_files_created": [],
    "frontend_files_created": [],
    "test_files_created": [],
    "migrations_applied": []
  },
  "next_actions": [
    "1. START Phase 1: Critical Security (8 hours)",
    "2. Implement database encryption (Fix #2)",
    "3. Implement PHI anonymization (Fix #5)",
    "4. Implement transaction handling (Fix #1)",
    "5. Validate: 0 hardcoded credentials, PHI encrypted"
  ]
}
EOF
    # Update session start timestamp
    jq ".session_start = \"$(date -Iseconds)\"" "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
    echo -e "${GREEN}✅ EMR Ralph state initialized${NC}"
}

# Check if state file exists, if not initialize
if [ ! -f "$STATE_FILE" ]; then
    echo "Initializing EMR Ralph state..."
    init_emr_state
fi

# Read current state
CURRENT_PRD=$(jq -r '.current_prd // "None"' "$STATE_FILE")
CURRENT_TASK=$(jq -r '.current_task' "$STATE_FILE")
CURRENT_PHASE=$(jq -r '.current_phase' "$STATE_FILE")

echo "Current Phase: $CURRENT_PHASE"
echo "Current Task: $CURRENT_TASK"
echo "Current PRD: $CURRENT_PRD"
echo ""

# Main implementation prompt
RALPH_PROMPT=$(cat <<'ENDPROMPT'
You are the project-manager-coordinator for the irStudy EMR Practice System implementation.

## CONTEXT

**Project**: EMR Practice System (SOAP note documentation training)
**Timeline**: Week 2-4 (3 weeks, 67.5-73.5 hours)
**Status**: Week 1 (Shared Infrastructure) COMPLETE ✅

**Shared Infrastructure Available**:
- ✅ HashiCorp Vault operational (backend/src/core/vault.py)
- ✅ Redis deployed (backend/src/core/redis_client.py) - namespace: emr:*
- ✅ HTTPS enforced with 9 security headers
- ✅ JWT authentication configured
- ✅ Security test suite foundation (15 tests, need expansion to 35)

**Reference Documents**:
- Master Plan: COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md
- EMR Summary: COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md
- PRD Directory: 16-feb-ralph-prds/ (14 EMR PRDs)
- Constraints: constraints/README.md

## CRITICAL: PARALLEL EXECUTION

This EMR implementation runs IN PARALLEL with AI OSCE Week 2 (PRD_002-005).

**Coordination Required**:
1. Both systems share Vault and Redis (different namespaces)
2. Both extend user_progress table (combined migration needed)
3. Both use Claude API (shared rate limit: 90 req/min total)
4. Both contribute to 35 total security tests (15 EMR + 20 OSCE)

**DO NOT**:
- Recreate Vault setup (already exists from Week 1)
- Recreate Redis (already deployed, use emr:* namespace)
- Recreate security tests (extend existing backend/tests/test_security/)

## IMPLEMENTATION PLAN: 6 PHASES (SEQUENTIAL)

### PHASE 1: Critical Security (Week 2, 8 hours) - START HERE

**Fixes to Implement**:
1. **Fix #2: Database Encryption** (3 hours)
   - File: backend/src/security/encryption.py
   - PHI encrypted at rest with AES-256-GCM
   - Encryption key from Vault: secret/emr/session-encryption-key
   - Reference: COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md lines 34-50

2. **Fix #5: PHI Anonymization** (3 hours)
   - File: backend/src/security/phi_anonymizer.py
   - Anonymize patient names, MRNs, dates before Claude API calls
   - Reference: EMR summary lines 34-50

3. **Fix #1: Transaction Handling** (2 hours)
   - File: backend/src/api/v1/sessions.py (update submit endpoint)
   - ACID-compliant submit endpoint
   - PostgreSQL transactions for emr_sessions + emr_soap_notes

**Delegation Instructions**:

Delegate to **rust-ffi-expert** with this prompt:

```
TASK: Implement EMR Phase 1 - Critical Security (3 fixes, 8 hours)

CONTEXT:
- Project: irStudy EMR Practice System
- Phase: Week 2, Phase 1 of 6
- Reference: COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md

CRITICAL CONSTRAINTS:
1. **MUST READ FIRST**:
   - COMPREHENSIVE_PLATFORM_IMPLEMENTATION_MASTER.md (understand shared infrastructure)
   - COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md (lines 34-50 for security fixes)
   - constraints/README.md (project-specific requirements)

2. **Shared Infrastructure** (DO NOT recreate):
   - Vault: Use existing backend/src/core/vault.py
   - Redis: Use existing backend/src/core/redis_client.py (namespace: emr:*)
   - Security tests: Extend backend/tests/test_security/test_security_comprehensive.py

3. **Zero Hardcoded Credentials**:
   - Encryption key: get_vault_secret("secret/emr/session-encryption-key", "value")
   - Database password: Already in Vault from Week 1
   - NO hardcoded keys anywhere

4. **Australian Medical Compliance**:
   - Terminology: paracetamol (NOT acetaminophen), salbutamol (NOT albuterol)
   - Date format: DD/MM/YYYY
   - Reference: constraints/README.md

FILES TO CREATE:

1. **backend/src/security/encryption.py** (220 lines)
   - Class: PHIEncryption
   - Method: encrypt_phi(data: str) -> str (AES-256-GCM)
   - Method: decrypt_phi(encrypted: str) -> str
   - Vault integration for key retrieval
   - Pattern: Similar to existing backend/src/core/vault.py

2. **backend/src/security/phi_anonymizer.py** (180 lines)
   - Class: PHIAnonymizer
   - Method: anonymize_for_claude(soap_note: str) -> str
   - Redact: Names, MRNs, DOBs, addresses
   - Keep: Clinical information (symptoms, diagnoses)

3. **backend/src/api/v1/sessions.py** (UPDATE existing file)
   - Update submit_emr_session endpoint
   - Add PostgreSQL transaction wrapper
   - Pattern:
     ```python
     async with db.begin():  # Transaction start
         # Insert emr_session
         # Insert emr_soap_note
         # Trigger validation
         # Commit or rollback
     ```

4. **backend/tests/test_security/test_emr_security.py** (150 lines, NEW)
   - Test: test_phi_encrypted_at_rest()
   - Test: test_phi_anonymized_in_claude_api()
   - Test: test_transaction_rollback_on_error()
   - Test: test_no_hardcoded_encryption_keys()
   - 10 security tests total

VALIDATION CHECKLIST (Before returning):

- [ ] All 4 files created/updated
- [ ] PHI encryption working (test with sample SOAP note)
- [ ] PHI anonymization removes names/MRNs (test output)
- [ ] Transaction handling prevents data corruption
- [ ] 10 security tests written and PASSING
- [ ] 0 hardcoded credentials: grep -r "secret/emr" backend/src/security/ = only Vault calls
- [ ] 0 American terminology: grep -ri "acetaminophen" backend/src/ = empty
- [ ] mypy type checking passes: python -m mypy backend/src/security/ --strict

EXPECTED OUTPUT:

Return a summary with:
1. Files created/updated (paths + line counts)
2. Test results (10/10 passing)
3. Validation checklist status (all ✅)
4. Any issues encountered and resolutions

BEGIN IMMEDIATELY. Report back when Phase 1 complete.
```

**After rust-ffi-expert completes Phase 1**:

Run these validation commands:

```bash
cd /home/dev/Development/irStudy/backend

# 1. Type checking
python -m mypy src/security/ --strict

# 2. Security tests
pytest tests/test_security/test_emr_security.py -v

# 3. Credential scan
grep -r "sk-ant-\|secret.*=.*['\"]" backend/src/security/ || echo "✅ No hardcoded credentials"

# 4. Australian compliance check
grep -ri "acetaminophen\|tylenol\|albuterol" backend/src/ || echo "✅ Australian terminology only"
```

**Pass Criteria**:
- [ ] 10/10 security tests passing
- [ ] 0 hardcoded credentials
- [ ] 0 American medical terms
- [ ] mypy passes with --strict

If all pass → Proceed to Phase 2.
If any fail → Re-delegate fix to rust-ffi-expert with specific errors.

---

### PHASE 2: Reliability (Week 2, 5 hours)

**After Phase 1 validated**, implement:
- Fix #3: Claude API fallback (3 hours)
- Fix #9: Health checks (1 hour)
- Fix #8: Database constraints (1 hour)

Delegate to rust-ffi-expert following same pattern.

---

### PHASE 3: Performance (Week 3, 4 hours)

**After Phase 2 validated**, implement:
- Frontend Fix #3: Dashboard parallel requests (2 hours)
- Frontend Fix #4: Auto-save debounce (2 hours)

Delegate to flutter-desktop-expert.

---

### PHASE 4: Security Hardening (Week 3, 3.5 hours)

**After Phase 3 validated**, implement:
- Fix #6: Prompt injection prevention (1.5 hours)
- Fix #7: Rate limiting (1 hour)
- Frontend Fix #5: Error boundaries (1 hour)

Delegate to rust-ffi-expert + flutter-desktop-expert.

---

### PHASE 5: Testing (Week 4, 24 hours)

**After Phase 4 validated**, implement:
- Fix #11: AI benchmark dataset (3 hours)
- 56 WCAG 2.2 AA/AAA tests (12 hours)
- 35 OWASP penetration tests (9 hours - 15 EMR + 20 OSCE, coordinate with AI OSCE team)

Delegate to testing-qa-expert.

---

### PHASE 6: Integration (Week 4, 10 hours)

**After Phase 5 validated**, implement:
- PRD_BACKEND_005: Dashboard Analytics API (5 hours)
- Frontend Fix #2: Theme switching (3 hours)
- Frontend Fix #6: API contract standardization (2 hours)

Delegate to rust-ffi-expert + flutter-desktop-expert.

---

## QUALITY GATES (RUN AFTER ALL 6 PHASES)

```bash
cd /home/dev/Development/irStudy/backend

# 1. All tests pass
pytest tests/ -v --cov=src --cov-report=term-missing
# Target: 328/328 tests passing (237 existing + 91 new)

# 2. Performance benchmarks
pytest tests/test_performance/ -v
# Targets: <500ms submit, <1s dashboard, <200ms auto-save

# 3. Security audit
./scripts/security-audit.sh
# Target: 0 HIGH/CRITICAL findings

# 4. Accessibility tests
cd ../frontend
npm run test:a11y
# Target: 56/56 WCAG tests passing, 0 axe-core violations
```

**Final Deliverables**:
- [ ] 18 critical fixes implemented
- [ ] 29 implementation files created (8,849 lines)
- [ ] 328 tests passing (100% pass rate)
- [ ] Performance: <500ms submit, <1s dashboard, <200ms auto-save
- [ ] Security: 0 hardcoded credentials, PHI encrypted, HTTPS enforced
- [ ] Accessibility: 56 WCAG tests passing, 0 violations
- [ ] AI validation: ≥85% accuracy vs expert SOAP notes

## CRITICAL REMINDERS

1. **Sequential Validation**: Complete Phase 1 → Validate → Phase 2 → Validate → etc.
2. **No Fire-and-Forget**: Don't delegate all 6 phases at once. Wait for each completion.
3. **Front-Load Context**: Every agent delegation MUST reference COMPREHENSIVE_EMR_IMPLEMENTATION_SUMMARY.md
4. **Institutional Memory**: Update .ralph-emr-state.json after each phase completion
5. **Coordinate with AI OSCE**: Security tests (35 total), user_progress migration, Claude API rate limits

## START IMMEDIATELY

Begin with Phase 1: Critical Security (8 hours).

Delegate to rust-ffi-expert with full context and validation checklist.

Report progress after Phase 1 validation complete.
ENDPROMPT
)

echo "==================================================================="
echo "Sending comprehensive EMR implementation plan to Claude..."
echo "==================================================================="
echo ""

# Send to Claude
echo "$RALPH_PROMPT" | tee -a "$LOG_FILE"

echo ""
echo "==================================================================="
echo "Ralph EMR Loop - Instructions Prepared"
echo "==================================================================="
echo "Next: Execute this script OR copy the prompt above to Claude"
echo ""
echo "State file: $STATE_FILE"
echo "Log file: $LOG_FILE"
echo ""
echo "To execute autonomously:"
echo "  claude -p < scripts/ralph-emr-loop.sh"
echo ""
echo "To monitor state:"
echo "  watch -n 5 'cat $STATE_FILE | jq .'"
echo ""
