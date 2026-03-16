# PRD-RALPH-001: Complete Batch1 Pilot (25 Personas)

**Created**: 2026-03-15
**Priority**: P0 (Critical)
**Status**: Ready for Execution
**Estimated Duration**: 10 minutes

---

## Executive Summary

Complete the remaining 5 personas from the Batch1 pilot run (20/25 completed). This validates the full Ralph pipeline before scaling to 207 personas.

---

## Current State

**Completed**: 20/25 personas
**Saved**: 40 files (20 personas + 20 QA reports)
**Location**: `clinical-content-prds/validation-system/batch1-output/`
**State File**: `.batch1_state.json` (tracks progress)

**Remaining Personas** (5):
1. `emergency_003_major_trauma_mvc_male_32` (Hard)
2. `emergency_005_acute_abdomen_perforation_male_55` (Medium)
3. `gp_002_t2dm_suboptimal_control_female_64` (Medium)
4. `respiratory_002_cap_severe_female_75` (Hard)
5. `respiratory_004_pe_subsegmental_female_38` (Medium)

---

## Requirements

### FR-001: Resume Ralph Loop
- ✅ Use existing state file (no reinitialization)
- ✅ Start from persona index 20
- ✅ Complete remaining 5 personas
- ✅ Maintain same validation gates (13 QA checks)

### FR-002: Validation Gates (Same as Before)
- Syntax validation (17 required fields)
- QA validation (13 quality gates, ≥70% deployment readiness)
- Auto-fix for common errors
- State file updates after each completion

### FR-003: Success Criteria
- All 25 personas generated ✅
- All 25 QA validated (≥70% deployment readiness) ✅
- 50 files in batch1-output/ (25 personas + 25 QA reports)
- State file shows: `"completed_personas": 25`

---

## Implementation Steps

### Step 1: Verify Current State
```bash
# Check completed count
cat clinical-content-prds/.batch1_state.json | jq '.completed_personas'
# Expected: 20

# Check pending count
cat clinical-content-prds/.batch1_state.json | jq '.personas | to_entries | map(select(.value.status == "pending")) | length'
# Expected: 5

# Check existing outputs
ls clinical-content-prds/validation-system/batch1-output/*.json | wc -l
# Expected: 40
```

### Step 2: Resume Ralph Loop
```bash
# Navigate to project
cd /home/dev/Development/irStudy

# Attach to existing tmux session
tmux attach -t ralph-batch1

# Resume from last completed persona
./scripts/ralph-batch1-loop.sh --resume
```

### Step 3: Monitor Progress
```bash
# Watch state file (in separate terminal)
watch -n 30 'cat clinical-content-prds/.batch1_state.json | jq "{completed: .completed_personas, total: .total_personas}"'

# Expected progression:
# 20 → 21 → 22 → 23 → 24 → 25
```

### Step 4: Validate Completion
```bash
# Check final count
ls clinical-content-prds/validation-system/batch1-output/*.json | wc -l
# Expected: 50 (25 personas + 25 QA reports)

# Check state file
cat clinical-content-prds/.batch1_state.json | jq '{completed: .completed_personas, failed: .failed_personas}'
# Expected: {"completed": 25, "failed": 0}

# Check all personas have ≥70% QA score
for file in clinical-content-prds/validation-system/batch1-output/*_qa_report.json; do
  jq '.deployment_readiness' "$file"
done | awk '{if ($1 < 70) print "FAIL: " FILENAME; else count++} END {print count " personas passed QA"}'
# Expected: 25 personas passed QA
```

---

## Acceptance Criteria

### AC-001: All 25 Personas Generated
- ✅ 25 persona JSON files exist
- ✅ All files 8-20 KB (comprehensive clinical data)
- ✅ No missing required fields

### AC-002: All QA Reports Pass
- ✅ 25 QA report files exist
- ✅ All reports show ≥70% deployment readiness
- ✅ No critical errors (auto-fail flags)

### AC-003: State File Accurate
- ✅ `completed_personas: 25`
- ✅ `failed_personas: 0`
- ✅ All persona statuses: `"completed"`

### AC-004: Ralph Loop Completed
- ✅ Ralph script exits successfully (exit code 0)
- ✅ Final message: "RALPH BATCH 1 PRODUCTION COMPLETE"
- ✅ Output directory path displayed

---

## Risk Mitigation

### Risk 1: Claude CLI Timeout
**Probability**: Low
**Impact**: Medium
**Mitigation**: 3-attempt retry with exponential backoff (5s, 15s, 30s)

### Risk 2: QA Validation Fails
**Probability**: Medium
**Impact**: Low
**Mitigation**: Auto-fix for common errors (specialty names, comorbidities)

### Risk 3: Network Interruption
**Probability**: Low
**Impact**: Low
**Mitigation**: State file persists progress, resume from last completed

---

## Dependencies

- ✅ Claude CLI authentication (already configured)
- ✅ batch1_config.json (25 personas - already exists)
- ✅ batch1_persona_generator.py (already implemented with CLI integration)
- ✅ qa_validator.py (13 quality gates - already available)
- ✅ ralph-batch1-loop.sh (resume capability - already implemented)
- ✅ tmux session 'ralph-batch1' (already running)

---

## Deliverables

### D-001: Completed Personas (25)
**Location**: `clinical-content-prds/validation-system/batch1-output/`
**Format**:
- `{persona_id}.json` (25 files)
- `{persona_id}_qa_report.json` (25 files)

### D-002: Final State File
**Location**: `clinical-content-prds/.batch1_state.json`
**Contents**:
```json
{
  "batch_id": "batch_1_pilot",
  "total_personas": 25,
  "completed_personas": 25,
  "failed_personas": 0,
  "personas": {
    "cardiology_001_...": {"status": "completed", ...},
    ... (all 25)
  }
}
```

### D-003: Completion Report
**Auto-generated**: Ralph loop final output
**Contents**:
- Total completed: 25/25
- Output directory path
- Timestamp of completion

---

## Timeline

**Total Estimated Duration**: 10 minutes

| Task | Duration | Dependencies |
|------|----------|--------------|
| Resume Ralph loop | 1 min | tmux session |
| Generate 5 personas | 7 min | Claude CLI |
| Final validation | 2 min | All personas complete |

**Expected Completion**: 2026-03-15 13:10 (10 min from now)

---

## Success Metrics

- ✅ **Completion Rate**: 100% (25/25 personas)
- ✅ **QA Pass Rate**: 100% (all ≥70% deployment readiness)
- ✅ **Failure Rate**: 0% (zero failed personas)
- ✅ **Time per Persona**: ~85 seconds (generation + validation)

---

## Post-Completion Actions

1. **Archive Pilot Batch**: Move batch1-output to batch1-pilot-archive/
2. **Validate Pipeline**: Confirm Ralph workflow ready for 207 personas
3. **Proceed to PRD-RALPH-002**: Generate full 207-persona config
4. **Update Documentation**: Mark pilot phase complete

---

**Status**: ✅ READY FOR EXECUTION
**Next PRD**: PRD-RALPH-002 (Generate Full 207 Config)
**Owner**: Ralph Automation System
**Approver**: Clinical Content PRD Team
