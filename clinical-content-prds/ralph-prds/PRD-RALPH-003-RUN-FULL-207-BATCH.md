# PRD-RALPH-003: Execute Full 207-Persona Production Batch

**Created**: 2026-03-15
**Priority**: P0 (Critical)
**Status**: Pending (Blocked by PRD-RALPH-001, PRD-RALPH-002)
**Estimated Duration**: 5-6 hours

---

## Executive Summary

Execute production batch generation of all 207 FRACP-equivalent personas using the Ralph automation pipeline with comprehensive QA validation.

---

## Prerequisites

### P-001: PRD-RALPH-001 Complete
- ✅ 25 pilot personas completed and validated
- ✅ Ralph pipeline proven functional
- ✅ QA gates working (13 quality checks)

### P-002: PRD-RALPH-002 Complete
- ✅ batch1_full_config.json generated (207 personas)
- ✅ Distributions validated (specialty, difficulty)
- ✅ All diagnoses unique and clinically appropriate

---

## Business Requirements

### BR-001: Production-Ready Persona Library
- **Target**: 207 validated personas
- **Quality**: 100% deployment readiness (≥70% QA score)
- **Purpose**: Comprehensive AMC Clinical Exam prep

### BR-002: Timeline Constraint
- **Maximum Duration**: 8 hours (1 business day)
- **Expected Duration**: 5-6 hours
- **Rate**: ~35 personas/hour (85 sec/persona average)

### BR-003: Cost Constraint
- **Claude CLI Usage**: Free (using existing authentication)
- **Infrastructure**: $0 (local execution)
- **Target**: $0 total cost

---

## Functional Requirements

### FR-001: Batch Execution
**Command**:
```bash
cd /home/dev/Development/irStudy
tmux new-session -s ralph-batch1-full
./scripts/ralph-batch1-loop.sh
```

**Expected Behavior**:
- Initialize state file for 207 personas
- Generate personas sequentially (index 0-206)
- Save persona JSON + QA report for each
- Update state file after each completion
- Handle failures gracefully (retry 3x, continue batch)

### FR-002: Quality Gates (Per Persona)
**Layer 1: Syntax Validation** (<1 sec):
- Valid JSON format
- All 17 required fields present
- No missing data

**Layer 2: QA Validation** (~1 sec):
- 13 quality gates from qa_validator.py
- Deployment readiness ≥70%
- Auto-fix for common errors

**Total Time per Persona**: ~85 seconds (generation + validation + save)

### FR-003: Progress Monitoring
**Real-Time Tracking**:
- State file updates after each persona
- Completed count displayed: "Progress: X% (N/207)"
- Tmux session shows live generation logs

**Monitoring Commands**:
```bash
# Watch progress (separate terminal)
watch -n 60 'cat clinical-content-prds/.batch1_state.json | jq "{completed: .completed_personas, failed: .failed_personas, progress: (.completed_personas / .total_personas * 100 | floor)}"'

# Check output count
watch -n 300 'ls clinical-content-prds/validation-system/batch1-output/*.json | wc -l'
```

### FR-004: Resilience & Recovery
**Auto-Retry**:
- 3 attempts per persona (with 5s, 15s, 30s backoff)
- Auto-fix for common errors (specialty names, comorbidities)
- Continue batch if single persona fails (mark for manual review)

**Resume Capability**:
```bash
# If interrupted, resume from last completed
./scripts/ralph-batch1-loop.sh --resume
```

**State Persistence**:
- `.batch1_state.json` saved after each persona
- Tracks: completed, failed, pending statuses
- Zero data loss on interruption

---

## Non-Functional Requirements

### NFR-001: Performance
- **Target**: 85 seconds per persona (average)
- **Total Duration**: 5-6 hours for 207 personas
- **Rate Limiting**: 1 second delay between personas (Claude API safety)

### NFR-002: Reliability
- **Uptime**: Continuous execution (no manual intervention)
- **Failure Rate**: <5% (failures handled via retry)
- **Data Loss**: 0% (state file persistence)

### NFR-003: Observability
- **Logging**: Real-time progress in tmux
- **State File**: JSON-queryable progress tracker
- **Output Files**: Immediate visibility of completed personas

---

## Acceptance Criteria

### AC-001: All Personas Generated
- ✅ 207 persona JSON files in batch1-output/
- ✅ 207 QA report JSON files in batch1-output/
- ✅ Total files: 414

### AC-002: QA Validation Passed
- ✅ All personas have deployment_readiness ≥70%
- ✅ Distribution targets met:
  - Cardiology: 45
  - Emergency: 45
  - General Practice: 54
  - Pediatrics: 36
  - Respiratory: 27

### AC-003: State File Complete
- ✅ `completed_personas: 207`
- ✅ `failed_personas: 0` (or minimal <5%)
- ✅ All persona statuses: "completed"

### AC-004: File Integrity
- ✅ All persona files 8-25 KB (comprehensive data)
- ✅ All QA report files 1-2 KB (validation results)
- ✅ Valid JSON (no corruption)

---

## Implementation Steps

### Step 1: Pre-Execution Checks
```bash
# Verify full config exists
test -f clinical-content-prds/validation-system/batch1_full_config.json && echo "Config ready" || echo "ERROR: Config missing"

# Check config count
jq '.total_personas' clinical-content-prds/validation-system/batch1_full_config.json
# Expected: 207

# Ensure output directory clean
mv clinical-content-prds/validation-system/batch1-output clinical-content-prds/validation-system/batch1-pilot-archive
mkdir -p clinical-content-prds/validation-system/batch1-output

# Reset state file
rm -f clinical-content-prds/.batch1_state.json
```

### Step 2: Update Ralph Scripts
```bash
# Point to full config
sed -i 's/batch1_config.json/batch1_full_config.json/g' scripts/ralph-batch1-loop.sh

# Verify update
grep "batch1_full_config.json" scripts/ralph-batch1-loop.sh
# Expected: CONFIG_FILE line shows batch1_full_config.json
```

### Step 3: Launch Ralph Full Batch
```bash
# Create new tmux session
tmux new-session -d -s ralph-batch1-full -c /home/dev/Development/irStudy

# Set up environment
tmux send-keys -t ralph-batch1-full "source backend/venv/bin/activate" C-m
tmux send-keys -t ralph-batch1-full "clear" C-m

# Start Ralph loop
tmux send-keys -t ralph-batch1-full "./scripts/ralph-batch1-loop.sh" C-m

# Attach to monitor
tmux attach -t ralph-batch1-full
```

### Step 4: Monitor Execution (Detached)
```bash
# Detach from tmux: Ctrl+B, D

# Monitor in separate terminal
watch -n 60 'echo "=== Ralph Batch1 Full Progress ===" && cat clinical-content-prds/.batch1_state.json | jq "{batch_id, total: .total_personas, completed: .completed_personas, failed: .failed_personas, progress: (.completed_personas / .total_personas * 100 | floor)}"'
```

### Step 5: Completion Validation
```bash
# Check final counts
ls clinical-content-prds/validation-system/batch1-output/*.json | wc -l
# Expected: 414 (207 personas + 207 QA reports)

# Verify state file
cat clinical-content-prds/.batch1_state.json | jq '{completed: .completed_personas, failed: .failed_personas}'
# Expected: {"completed": 207, "failed": 0}

# Check QA pass rate
for file in clinical-content-prds/validation-system/batch1-output/*_qa_report.json; do
  jq '.deployment_readiness' "$file"
done | awk '{sum+=$1; count++} END {print "Average QA: " sum/count "%"}'
# Expected: >70%
```

---

## Risk Mitigation

### Risk 1: Long Execution Time
**Probability**: High
**Impact**: Low (expected behavior)
**Mitigation**:
- Run overnight (start 6 PM, complete by midnight)
- Tmux allows detached execution
- Resume capability if needed

### Risk 2: Claude CLI Rate Limiting
**Probability**: Medium
**Impact**: Medium
**Mitigation**:
- 1-second delay between requests (safe buffer)
- 3-attempt retry with exponential backoff
- If persistent, increase delay to 2 seconds

### Risk 3: Disk Space
**Probability**: Low
**Impact**: Medium
**Mitigation**:
- Pre-check: 5 GB free space available
- Estimated usage: ~3 MB for 207 personas
- Monitor: `df -h` during execution

### Risk 4: QA Validation Failures
**Probability**: Medium (5-10% of personas)
**Impact**: Low
**Mitigation**:
- Auto-fix for 80% of common errors
- Failed personas flagged for manual review
- Batch continues (doesn't block on single failure)

---

## Timeline

**Total Estimated Duration**: 5-6 hours

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Pre-execution checks | 10 min | 0:10 |
| Personas 1-50 | 1.2 hours | 1:22 |
| Personas 51-100 | 1.2 hours | 2:32 |
| Personas 101-150 | 1.2 hours | 3:52 |
| Personas 151-200 | 1.2 hours | 5:02 |
| Personas 201-207 | 10 min | 5:12 |
| Final validation | 15 min | 5:27 |

**Recommended Start Time**: 6:00 PM (complete by 11:30 PM)

---

## Deliverables

### D-001: Complete Persona Library
**Location**: `clinical-content-prds/validation-system/batch1-output/`
**Contents**:
- 207 persona JSON files (~8-25 KB each)
- 207 QA report JSON files (~1-2 KB each)
- **Total**: 414 files, ~2.5 MB

### D-002: Final State File
**Location**: `clinical-content-prds/.batch1_state.json`
**Contents**:
```json
{
  "batch_id": "batch_1_production",
  "total_personas": 207,
  "completed_personas": 207,
  "failed_personas": 0,
  "personas": { ... all 207 with "completed" status ... }
}
```

### D-003: Completion Report
**Generated by**: Ralph loop final output
**Contents**:
- Total completed: 207/207
- Total duration: ~5-6 hours
- Output directory path
- Timestamp of completion

---

## Post-Completion Actions

1. **Generate Aggregate Report**: Run validation_pipeline.py across all 207
2. **Review Failed Personas**: Manual review of any flagged personas
3. **Archive Outputs**: Compress batch1-output/ for long-term storage
4. **Proceed to Phase 3B**: PostgreSQL import and production deployment
5. **Update Documentation**: Mark Batch1 production complete

---

**Status**: ⏸️ PENDING
**Blocked By**: PRD-RALPH-001, PRD-RALPH-002
**Next Action**: Execute PRD-RALPH-001 and PRD-RALPH-002 first
**Owner**: Ralph Automation System
**Approver**: Clinical Content PRD Team
