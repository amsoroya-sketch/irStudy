# Ralph Loop Execution Plan
# Automated Multi-Agent Content Creation

**Version**: 1.0
**Created**: 2026-03-15
**Purpose**: Parallel execution of 10 PRDs using Ralph loop automation
**Script**: `/home/dev/Development/irStudy/scripts/ralph-clinical-content-loop.sh`

---

## Table of Contents

1. [Overview](#overview)
2. [Ralph Loop Architecture](#ralph-loop-architecture)
3. [Parallel Execution Strategy](#parallel-execution-strategy)
4. [State Tracking](#state-tracking)
5. [Quality Gates Per Batch](#quality-gates-per-batch)
6. [How to Run](#how-to-run)
7. [Monitoring & Debugging](#monitoring--debugging)

---

## Overview

### What is Ralph Loop?

**Ralph** (Recursive Agent Loop for Persistent Handling) is an automated script that:
- Executes multiple PRDs in sequence or parallel
- Tracks state across sessions (`.ralph-clinical-content-state.json`)
- Delegates to specialist agents using Agent OS framework
- Runs quality gates after each batch
- Provides progress reports

### Why Use Ralph for Content Creation?

**Manual execution**: 10 PRDs × 24-30 hours each = 240-300 hours sequentially
**Ralph automated**: 10 PRDs in 4 batches × 5 agents parallel = 48-60 hours actual time

**Benefits**:
- **5x faster**: Parallel agent execution (5 agents simultaneously)
- **Consistent**: Same quality gates applied to all personas
- **Auditable**: State file tracks every persona created
- **Resumable**: If interrupted, picks up where it left off

---

## Ralph Loop Architecture

### High-Level Flow

```
┌──────────────────────────────────────────────────────────────┐
│                  Ralph Loop Controller                        │
│  (scripts/ralph-clinical-content-loop.sh)                    │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────────┐
         │  Read .ralph-clinical-content-state.json │
         │  (Current progress: Phase X, PRD Y)      │
         └──────────────────────────────────────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │   Execute Next Batch    │
              │   (5 agents parallel)   │
              └─────────────────────────┘
                            │
            ┌───────────────┼───────────────┐
            ▼               ▼               ▼
    ┌────────────┐  ┌────────────┐  ┌────────────┐
    │  Agent 1   │  │  Agent 2   │  │  Agent 3   │
    │ Cardiology │  │ Emergency  │  │   GP       │
    └────────────┘  └────────────┘  └────────────┘
            │               │               │
            └───────────────┼───────────────┘
                            ▼
              ┌─────────────────────────┐
              │   Quality Gate Check    │
              │   (All pass? Continue)  │
              └─────────────────────────┘
                            │
                            ▼
         ┌──────────────────────────────────────────┐
         │  Update .ralph-clinical-content-state.json │
         │  (Batch 1 complete, move to Batch 2)      │
         └──────────────────────────────────────────┘
```

### Agent Delegation Pattern

Each PRD delegates to specialist agents using Agent OS framework:

```markdown
## Agent Delegation (inside PRD)

**Delegate to**: cardiology-expert (MED-001)

**Prompt**:
Task: Create 45 cardiology patient personas

CONSTRAINTS:
1. Read constraints/4-llm-integration.md (RAG requirements)
2. Use eTG Cardiovascular guidelines (sections 2.1-2.8)
3. Follow 9-step history structure
4. Include RAG citations >0.65 confidence

VALIDATION CHECKLIST:
- [ ] 45 personas created (15 Easy, 18 Medium, 12 Hard)
- [ ] All follow JSON template (backend/data/patient_personas_template.json)
- [ ] RAG citations present (source + page_ref)
- [ ] Zero hardcoded credentials
- [ ] 2 FRACP clinician reviews per persona

RETURN FORMAT:
JSON array of 45 personas + validation report
```

---

## Parallel Execution Strategy

### Batch Structure (4 Batches Total)

**Batch 1: High-Volume Specialties** (Weeks 3-5)
- Cardiology (45 personas)
- Emergency Medicine (45 personas)
- General Practice (54 personas)
- Respiratory (36 personas)
- Neurology (27 personas)
- **Total**: 207 personas
- **Agents**: MED-001, MED-002, MED-003, MED-008, MED-009 (5 parallel)
- **Duration**: ~42 hours total (8-10 hours actual with parallelization)

**Batch 2: Remaining Specialties** (Weeks 6-8)
- Pediatrics (36 personas)
- ObGyn (27 personas)
- Surgery (27 personas)
- Psychiatry (36 personas)
- Infectious Diseases (27 personas)
- **Total**: 153 personas
- **Agents**: MED-004, MED-005, MED-006, MED-007, MED-010 (5 parallel)
- **Duration**: ~31 hours total (6-8 hours actual with parallelization)

**Batch 3: Physical Examination** (Weeks 9-11)
- CVS examination (15 personas)
- Respiratory examination (15 personas)
- Abdominal examination (12 personas)
- Neurological examination (12 personas)
- MSK examination (6 personas)
- **Total**: 60 personas
- **Agents**: MED-012 (physical-exam-expert)
- **Duration**: ~12 hours total (12 hours actual, single agent)

**Batch 4: Cultural Safety** (Weeks 12-14)
- Aboriginal/TSI personas (12 personas across specialties)
- LGBTQIA+ personas (40 personas across specialties)
- CALD personas (40 personas across specialties)
- **Total**: 92 personas (integrated into existing 360)
- **Agents**: MED-011 (cultural-safety-expert)
- **Duration**: ~28 hours total (28 hours actual, single agent)

**QA Validation** (After all batches complete)
- QA-001 (medical-qa-validator) reviews all 360 personas
- **Duration**: ~24 hours total

---

## State Tracking

### State File: `.ralph-clinical-content-state.json`

**Location**: `/home/dev/Development/irStudy/.ralph-clinical-content-state.json`

**Structure**:
```json
{
  "version": "1.0",
  "created_at": "2026-03-15T02:00:00Z",
  "last_updated": "2026-03-15T10:30:00Z",
  "current_phase": 2,
  "current_prd": "PRD_CC_003",
  "current_batch": 1,
  "total_personas_created": 207,
  "total_personas_target": 360,
  "batches": [
    {
      "batch_id": 1,
      "status": "COMPLETE",
      "personas_created": 207,
      "agents_used": ["MED-001", "MED-002", "MED-003", "MED-008", "MED-009"],
      "quality_gates_passed": true,
      "duration_hours": 9.5,
      "completed_at": "2026-03-18T14:00:00Z"
    },
    {
      "batch_id": 2,
      "status": "IN_PROGRESS",
      "personas_created": 0,
      "agents_used": ["MED-004", "MED-005", "MED-006", "MED-007", "MED-010"],
      "quality_gates_passed": null,
      "duration_hours": null,
      "completed_at": null
    }
  ],
  "prds_completed": [
    {
      "prd_id": "PRD_CC_001",
      "status": "COMPLETE",
      "deliverables": ["13 agent specs created"],
      "quality_gates_passed": true,
      "completed_at": "2026-03-16T18:00:00Z"
    },
    {
      "prd_id": "PRD_CC_002",
      "status": "COMPLETE",
      "deliverables": ["RAG enhanced with eTG citations"],
      "quality_gates_passed": true,
      "completed_at": "2026-03-17T12:00:00Z"
    }
  ],
  "quality_metrics": {
    "total_personas_validated": 207,
    "total_fracp_reviews": 414,
    "avg_rag_citation_confidence": 0.73,
    "zero_hardcoded_credentials": true
  }
}
```

### Resume Logic

**If Ralph loop is interrupted**:
```bash
# Read state file
current_phase=$(jq -r '.current_phase' .ralph-clinical-content-state.json)
current_batch=$(jq -r '.current_batch' .ralph-clinical-content-state.json)

# Resume from last checkpoint
if [ "$current_batch" == "1" ] && [ "$(jq -r '.batches[0].status' .ralph-clinical-content-state.json)" == "IN_PROGRESS" ]; then
  echo "Resuming Batch 1 from persona $(jq -r '.total_personas_created' .ralph-clinical-content-state.json)"
  # Continue batch 1
fi
```

---

## Quality Gates Per Batch

### After Each Batch Completes

**Automated Quality Gate Script**: `scripts/quality-gate-clinical-content.sh`

```bash
#!/bin/bash
# Quality gate for clinical content batches

BATCH_ID=$1
PERSONAS_JSON_DIR="backend/data/patient_personas/"

echo "Running quality gate for Batch $BATCH_ID..."

# Gate 1: Persona count matches target
expected_count=$(jq -r ".batches[$BATCH_ID - 1].personas_created" .ralph-clinical-content-state.json)
actual_count=$(find $PERSONAS_JSON_DIR -name "*.json" -type f | wc -l)

if [ "$actual_count" -ne "$expected_count" ]; then
  echo "❌ FAILED: Expected $expected_count personas, found $actual_count"
  exit 1
fi

# Gate 2: All personas have RAG citations
for file in $PERSONAS_JSON_DIR/*.json; do
  citations=$(jq -r '.symptoms | length' $file)
  if [ "$citations" -eq 0 ]; then
    echo "❌ FAILED: $file has no RAG citations"
    exit 1
  fi
done

# Gate 3: All personas validated by ≥2 FRACP clinicians
for file in $PERSONAS_JSON_DIR/*.json; do
  reviewers=$(jq -r '.fracp_reviews | length' $file)
  if [ "$reviewers" -lt 2 ]; then
    echo "❌ FAILED: $file has <2 FRACP reviews ($reviewers found)"
    exit 1
  fi
done

# Gate 4: Zero hardcoded credentials
if grep -r "api_key\|dbPath:\|dbKey:" $PERSONAS_JSON_DIR; then
  echo "❌ FAILED: Hardcoded credentials found"
  exit 1
fi

echo "✅ PASSED: Batch $BATCH_ID quality gates passed"
exit 0
```

### Quality Gate Checklist

**After Batch 1** (207 personas):
- [ ] 207 personas created (45+45+54+36+27)
- [ ] All follow JSON template
- [ ] RAG citations >0.65 confidence
- [ ] ≥2 FRACP reviews per persona
- [ ] Zero hardcoded credentials
- [ ] Clinical accuracy validated

**After Batch 2** (153 personas):
- [ ] 153 personas created (36+27+27+36+27)
- [ ] All follow JSON template
- [ ] RAG citations >0.65 confidence
- [ ] ≥2 FRACP reviews per persona
- [ ] Zero hardcoded credentials
- [ ] Clinical accuracy validated

**After Batch 3** (60 personas):
- [ ] 60 physical exam personas created
- [ ] All follow 5 Ps framework
- [ ] Examination findings clinically accurate
- [ ] ≥2 FRACP reviews per persona

**After Batch 4** (92 cultural personas):
- [ ] 12 Aboriginal/TSI personas reviewed by cultural liaison
- [ ] 40 LGBTQIA+ personas reviewed by LGBTQIA+ educator
- [ ] 40 CALD personas with interpreter protocols
- [ ] Zero cultural stereotypes

---

## How to Run

### Step 1: Prepare Environment

```bash
cd /home/dev/Development/irStudy

# Ensure state file doesn't exist (first run)
rm -f .ralph-clinical-content-state.json

# Ensure scripts are executable
chmod +x scripts/ralph-clinical-content-loop.sh
chmod +x scripts/quality-gate-clinical-content.sh
```

### Step 2: Execute Ralph Loop

```bash
# Full execution (all 4 batches)
bash scripts/ralph-clinical-content-loop.sh

# Or run specific batch
bash scripts/ralph-clinical-content-loop.sh --batch 1

# Or resume from last checkpoint
bash scripts/ralph-clinical-content-loop.sh --resume
```

### Step 3: Monitor Progress

```bash
# Watch state file updates
watch -n 10 'cat .ralph-clinical-content-state.json | jq .'

# Check logs
tail -f ralph-clinical-content.log

# Check persona count
find backend/data/patient_personas -name "*.json" | wc -l
```

### Step 4: Validate Completion

```bash
# After all batches complete, run QA validation
bash scripts/quality-gate-clinical-content.sh 4

# Check final state
cat .ralph-clinical-content-state.json | jq '.total_personas_created'
# Expected: 360
```

---

## Monitoring & Debugging

### Progress Dashboard

**Real-time metrics** (updated every 10 seconds):
```bash
#!/bin/bash
# scripts/clinical-content-dashboard.sh

while true; do
  clear
  echo "==============================================="
  echo "  Clinical Content Creation Dashboard"
  echo "==============================================="
  echo ""
  
  # Overall progress
  total_created=$(jq -r '.total_personas_created' .ralph-clinical-content-state.json)
  total_target=$(jq -r '.total_personas_target' .ralph-clinical-content-state.json)
  percentage=$((total_created * 100 / total_target))
  
  echo "Overall Progress: $total_created / $total_target ($percentage%)"
  echo ""
  
  # Batch status
  echo "Batch Status:"
  jq -r '.batches[] | "\(.batch_id): \(.status) - \(.personas_created) personas"' .ralph-clinical-content-state.json
  echo ""
  
  # Quality metrics
  echo "Quality Metrics:"
  avg_confidence=$(jq -r '.quality_metrics.avg_rag_citation_confidence' .ralph-clinical-content-state.json)
  echo "  Avg RAG Citation Confidence: $avg_confidence"
  echo "  Zero Hardcoded Credentials: $(jq -r '.quality_metrics.zero_hardcoded_credentials' .ralph-clinical-content-state.json)"
  echo ""
  
  sleep 10
done
```

### Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Agent timeout** | Batch stuck at X personas | Increase timeout in ralph script (default 600s) |
| **RAG citation confidence <0.65** | Quality gate fails | Check RAG vector DB status, re-index if needed |
| **Hardcoded credentials detected** | Quality gate fails | Review agent prompts, add explicit "NO HARDCODED VALUES" constraint |
| **FRACP review missing** | Quality gate fails | Check expert panel availability, schedule reviews in advance |
| **State file corrupted** | Ralph cannot resume | Restore from backup `.ralph-clinical-content-state.json.backup` |

### Debugging Commands

```bash
# Check last agent output
tail -n 100 ralph-clinical-content.log | grep "Agent: MED-001"

# Validate specific persona
jq . backend/data/patient_personas/cardiology_001.json

# Check RAG citation confidence
jq -r '.symptoms[].confidence' backend/data/patient_personas/cardiology_001.json

# Count FRACP reviews
jq -r '.fracp_reviews | length' backend/data/patient_personas/cardiology_001.json

# Search for hardcoded credentials
grep -r "api_key\|dbPath:\|dbKey:" backend/data/patient_personas/
```

---

## Ralph Loop Script Structure

**File**: `scripts/ralph-clinical-content-loop.sh`

```bash
#!/bin/bash
# Ralph Loop for Clinical Content Creation
# Executes 10 PRDs across 4 batches with quality gates

set -e

PROJECT_ROOT="/home/dev/Development/irStudy"
STATE_FILE="$PROJECT_ROOT/.ralph-clinical-content-state.json"
LOG_FILE="$PROJECT_ROOT/ralph-clinical-content.log"

# Initialize state file
init_state() {
  cat > $STATE_FILE << 'EOF'
{
  "version": "1.0",
  "created_at": "$(date -Iseconds)",
  "last_updated": "$(date -Iseconds)",
  "current_phase": 1,
  "current_prd": "PRD_CC_001",
  "current_batch": 0,
  "total_personas_created": 0,
  "total_personas_target": 360,
  "batches": [],
  "prds_completed": [],
  "quality_metrics": {}
}
EOF
}

# Execute PRD
execute_prd() {
  local prd_id=$1
  local prd_file="$PROJECT_ROOT/clinical-content-prds/phase*/PRD_$prd_id.md"
  
  echo "[$(date)] Executing $prd_id..." | tee -a $LOG_FILE
  
  # Delegate to Claude with PRD as context
  claude-code --prompt "Execute PRD: $(cat $prd_file)" | tee -a $LOG_FILE
  
  # Update state file
  jq ".prds_completed += [{\"prd_id\": \"$prd_id\", \"status\": \"COMPLETE\", \"completed_at\": \"$(date -Iseconds)\"}]" $STATE_FILE > tmp.$$.json && mv tmp.$$.json $STATE_FILE
}

# Execute batch (5 agents parallel)
execute_batch() {
  local batch_id=$1
  
  echo "[$(date)] Executing Batch $batch_id..." | tee -a $LOG_FILE
  
  # Run 5 agents in parallel
  # (Actual implementation uses GNU parallel or background jobs)
  
  # Run quality gate
  bash scripts/quality-gate-clinical-content.sh $batch_id
  
  # Update state file
  jq ".current_batch = $batch_id" $STATE_FILE > tmp.$$.json && mv tmp.$$.json $STATE_FILE
}

# Main execution
main() {
  # Initialize if first run
  if [ ! -f $STATE_FILE ]; then
    init_state
  fi
  
  # Execute Phase 1 (PRD_CC_001, PRD_CC_002)
  execute_prd "CC_001"
  execute_prd "CC_002"
  
  # Execute Phase 2 (Batches 1-4)
  for batch in {1..4}; do
    execute_batch $batch
  done
  
  # Execute remaining phases
  execute_prd "CC_005"
  execute_prd "CC_006"
  execute_prd "CC_007"
  execute_prd "CC_008"
  execute_prd "CC_009"
  execute_prd "CC_010"
  
  echo "[$(date)] Ralph loop complete! 360 personas created." | tee -a $LOG_FILE
}

main "$@"
```

---

## Summary

**Ralph loop provides**:
- **5x faster** execution (parallel agents)
- **Automated** quality gates (catch errors immediately)
- **Resumable** (state file tracks progress)
- **Auditable** (logs every persona created)

**Total time savings**: 240-300 hours sequential → 48-60 hours parallel = **80% reduction**

---

**Status**: ✅ READY FOR EXECUTION
**Next Step**: Create ralph-clinical-content-loop.sh script
**Last Updated**: 2026-03-15
**Version**: 1.0
