# Ralph PRD Pipeline - Medical Persona Generation

**Created**: 2026-03-15
**Status**: Active Execution
**Purpose**: Automated generation of 207 FRACP-equivalent medical personas

---

## 🎯 Quick Start

```bash
# Execute entire PRD pipeline (automated)
cd /home/dev/Development/irStudy
./scripts/ralph-execute-prds.sh
```

This will execute all three PRDs sequentially:
1. **PRD-RALPH-001**: Complete 25-persona pilot batch
2. **PRD-RALPH-002**: Generate full 207-persona config
3. **PRD-RALPH-003**: Execute full 207-persona production batch

---

## 📋 PRD Documents

### PRD-RALPH-001: Complete Batch1 Pilot
**File**: `PRD-RALPH-001-COMPLETE-BATCH1-PILOT.md`
**Status**: ⏳ **IN PROGRESS** (20/25 complete)
**Duration**: 10 minutes
**Purpose**: Validate Ralph pipeline with 25 pilot personas

**Key Deliverables**:
- 25 persona JSON files
- 25 QA validation reports
- State file with 100% completion rate

**Current Progress**:
- ✅ 20 personas completed and QA-validated
- ⏳ 5 personas in progress (currently generating)
- 📊 All completed personas passed QA (≥70% deployment readiness)

---

### PRD-RALPH-002: Generate Full 207 Config
**File**: `PRD-RALPH-002-GENERATE-FULL-207-CONFIG.md`
**Status**: ⏸️ **PENDING** (blocked by PRD-RALPH-001)
**Duration**: 30 minutes
**Purpose**: Create comprehensive config with all 207 persona specifications

**Key Deliverables**:
- `batch1_full_config.json` with 207 unique persona specs
- Specialty distribution: Cardiology (45), Emergency (45), GP (54), Pediatrics (36), Respiratory (27)
- Difficulty distribution: Easy (62), Medium (124), Hard (21)

**Approach**:
- Automated generation using Python script
- Based on PRD-003 specifications
- Validates distribution targets automatically

---

### PRD-RALPH-003: Run Full 207 Batch
**File**: `PRD-RALPH-003-RUN-FULL-207-BATCH.md`
**Status**: ⏸️ **PENDING** (blocked by PRD-RALPH-001, PRD-RALPH-002)
**Duration**: 5-6 hours
**Purpose**: Generate all 207 production personas

**Key Deliverables**:
- 207 persona JSON files (~2.5 MB total)
- 207 QA validation reports
- Complete state file tracking all progress

**Execution Plan**:
- Run overnight (recommended start: 6 PM)
- Continuous monitoring via tmux
- Auto-resume capability if interrupted
- Expected completion: 5-6 hours

---

## 🔄 Current Status (Live)

**Pilot Batch** (PRD-RALPH-001):
```
Status: IN PROGRESS
Completed: 20/25 personas (80%)
Pending: 5 personas
Current: respiratory_003_asthma_acute_severe_male_42 (Attempt 2/3)
```

**Ralph Loop**:
- ✅ Running in tmux session 'ralph-batch1'
- ✅ Claude CLI integration working
- ✅ QA validation active (13 quality gates)
- ⏳ Auto-retry handling timeout (120s → retry with backoff)

**Output Directory**:
```
Location: clinical-content-prds/validation-system/batch1-output/
Files: 40 (20 personas + 20 QA reports)
Expected: 50 when pilot complete
```

---

## 📊 Quality Metrics

### Pilot Batch Results (20/25 complete)

**QA Validation**:
- ✅ 100% pass rate (all ≥70% deployment readiness)
- ✅ Average QA score: 72.5%
- ✅ Zero security violations
- ✅ All Australian format compliant

**Generation Performance**:
- Average time per persona: 85 seconds
- Retry rate: ~5% (handled automatically)
- Claude CLI timeout: 120 seconds (auto-retry on timeout)

**File Integrity**:
- Persona files: 8-23 KB (comprehensive clinical data)
- QA reports: 1.1-1.5 KB (validation results)
- All JSON valid (no corruption)

---

## 🛠️ Tools & Scripts

### Execution Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **ralph-execute-prds.sh** | Master execution pipeline | `./scripts/ralph-execute-prds.sh` |
| **ralph-batch1-loop.sh** | Core generation loop | `./scripts/ralph-batch1-loop.sh [--resume]` |
| **start-ralph-batch1-tmux.sh** | Tmux session launcher | `./scripts/start-ralph-batch1-tmux.sh` |

### Monitoring Commands

```bash
# Check current progress
cat clinical-content-prds/.batch1_state.json | jq '{completed: .completed_personas, total: .total_personas}'

# Monitor in real-time
watch -n 30 'cat clinical-content-prds/.batch1_state.json | jq "{completed: .completed_personas, pending: (.personas | to_entries | map(select(.value.status == \"pending\")) | length)}"'

# Attach to Ralph tmux session
tmux attach -t ralph-batch1

# Count generated files
ls clinical-content-prds/validation-system/batch1-output/*.json | wc -l
```

---

## 🎯 Success Criteria

### PRD-RALPH-001 (Pilot)
- [x] 20/25 personas complete
- [ ] 25/25 personas complete ⏳ IN PROGRESS
- [ ] All QA validated ≥70%
- [ ] State file: completed_personas = 25

### PRD-RALPH-002 (Config)
- [ ] batch1_full_config.json created
- [ ] 207 persona specifications
- [ ] Distribution targets met
- [ ] All IDs unique

### PRD-RALPH-003 (Production)
- [ ] 207 personas generated
- [ ] 100% QA validation pass
- [ ] State file: completed_personas = 207
- [ ] 414 output files (207 + 207 QA reports)

---

## 📁 File Structure

```
clinical-content-prds/
├── ralph-prds/
│   ├── README.md (this file)
│   ├── PRD-RALPH-001-COMPLETE-BATCH1-PILOT.md
│   ├── PRD-RALPH-002-GENERATE-FULL-207-CONFIG.md
│   └── PRD-RALPH-003-RUN-FULL-207-BATCH.md
├── validation-system/
│   ├── batch1_config.json (25 personas - pilot)
│   ├── batch1_full_config.json (207 personas - to be generated)
│   ├── batch1_persona_generator.py (core engine with Claude CLI)
│   ├── qa_validator.py (13 quality gates)
│   ├── claude_validator.py (FRACP clinical review)
│   └── batch1-output/ (generated personas + QA reports)
├── .batch1_state.json (progress tracker)
└── RALPH_BATCH1_QUICKSTART.md (user guide)
```

---

## 🔧 Troubleshooting

### Issue: Claude CLI Timeout
**Symptom**: `Command timed out after 120 seconds`
**Cause**: Large prompt or API slowness
**Solution**: Auto-retry with 3 attempts (already handled)

### Issue: QA Validation Fails
**Symptom**: Persona marked failed, deployment_readiness <70%
**Cause**: Missing fields or format errors
**Solution**: Auto-fix for common errors, manual review for persistent failures

### Issue: Ralph Loop Stops
**Symptom**: Tmux session exits
**Cause**: Unexpected error or interruption
**Solution**: Resume with `./scripts/ralph-batch1-loop.sh --resume`

---

## 📈 Timeline

| PRD | Duration | Status |
|-----|----------|--------|
| **PRD-RALPH-001** | 10 min | ⏳ IN PROGRESS (80% complete) |
| **PRD-RALPH-002** | 30 min | ⏸️ PENDING |
| **PRD-RALPH-003** | 5-6 hours | ⏸️ PENDING |
| **Total** | ~6 hours | Expected completion: 2026-03-15 19:00 (if run now) |

---

## 🎉 Next Steps

1. ✅ Wait for PRD-RALPH-001 to complete (5 more personas)
2. ⏭️ Auto-execute PRD-RALPH-002 (generate full config)
3. 🚀 Launch PRD-RALPH-003 (full 207-persona batch)
4. 📊 Generate completion report
5. 🗄️ Import to PostgreSQL (Phase 3B)

---

**Last Updated**: 2026-03-15 18:50
**Current Phase**: PRD-RALPH-001 (80% complete)
**Next Milestone**: Pilot batch completion (expected: 19:00)
