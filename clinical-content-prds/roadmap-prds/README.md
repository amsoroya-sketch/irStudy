# Roadmap PRD System - Complete Guide

**Created**: 2026-03-16
**Status**: Ready for Ralph Loop Execution
**Total PRDs**: 3 (Week 1 Critical)

---

## 📁 Folder Structure

```
roadmap-prds/
├── README.md (this file)
├── week1-critical/           # P0 - Must complete this week
│   ├── PRD-WEEK1-001-FIX-QA-VALIDATOR.md
│   ├── PRD-WEEK1-002-DATABASE-INSERTION.md
│   └── PRD-WEEK1-003-FRONTEND-INTEGRATION.md
│
├── week2-important/          # P1 - Complete next week
│   └── (to be created)
│
├── month2-scaling/           # P2 - Future enhancements
│   └── (to be created)
│
└── logs/                     # Execution logs (auto-created)
    ├── PRD-WEEK1-001_20260316_184900.log
    ├── PRD-WEEK1-002_20260316_190000.log
    └── PRD-WEEK1-003_20260316_192000.log
```

---

## 🚀 Quick Start

### Option 1: Run Ralph Loop in Tmux (Recommended)

```bash
# Start tmux session
cd /home/dev/Development/irStudy
tmux new-session -s ralph-roadmap \
  './scripts/ralph-roadmap-loop.sh 2>&1 | tee clinical-content-prds/roadmap-prds/ralph-execution.log'

# Detach: Ctrl+B, then D
# Reattach: tmux attach -t ralph-roadmap
```

### Option 2: Run Directly

```bash
cd /home/dev/Development/irStudy
./scripts/ralph-roadmap-loop.sh
```

---

## 📋 PRD Details

### Week 1 - Critical (Must Complete)

#### PRD-WEEK1-001: Fix QA Validator
- **Time**: 30 minutes
- **What**: Fix schema mismatch (expected_diagnosis → diagnosis)
- **Why**: Blocks QA validation of all 207 personas
- **Output**: QA validator runs successfully on all personas

#### PRD-WEEK1-002: Database Insertion
- **Time**: 2 hours
- **What**: Load 207 personas into PostgreSQL
- **Why**: Frontend needs database access via API
- **Output**: All 207 personas in database, API endpoints working

#### PRD-WEEK1-003: Frontend Integration
- **Time**: 3 hours
- **What**: Update UI to show all 207 personas with filters
- **Why**: Users need to select personas for OSCE practice
- **Output**: Persona selector shows 207 options, filtering works

**Total Week 1**: 5.5 hours

---

## 🔄 Ralph Loop Workflow

The Ralph loop executes PRDs automatically:

```
1. Read PRD markdown file
   ↓
2. Parse requirements & implementation steps
   ↓
3. Execute using Claude CLI
   ↓
4. Run test commands
   ↓
5. Verify success criteria
   ↓
6. Mark as completed in state file
   ↓
7. Move to next PRD
```

**State Tracking**: `.ralph-roadmap-state.json`

Example state:
```json
{
  "started_at": "2026-03-16T18:49:00Z",
  "current_phase": "week1-critical",
  "completed_prds": [
    "PRD-WEEK1-001-FIX-QA-VALIDATOR"
  ],
  "failed_prds": [],
  "current_prd": "PRD-WEEK1-002-DATABASE-INSERTION",
  "completed_count": 1
}
```

---

## 📊 Monitoring Progress

### View Real-Time Progress

```bash
# Watch log file
tail -f clinical-content-prds/roadmap-prds/ralph-execution.log

# Attach to tmux
tmux attach -t ralph-roadmap

# Check state
cat .ralph-roadmap-state.json | jq '.'
```

### Check Completion Status

```bash
# Quick summary
python3 -c "
import json
with open('.ralph-roadmap-state.json') as f:
    state = json.load(f)
print(f\"Completed: {state['completed_count']}\")
print(f\"Current: {state.get('current_prd', 'None')}\")
print(f\"Failed: {len(state.get('failed_prds', []))}\")
"
```

---

## ✅ Success Criteria

### Week 1 Complete When:
- [ ] All 3 PRDs marked as completed
- [ ] QA validator runs on 207 personas
- [ ] Database has 207 personas
- [ ] Frontend shows persona selector
- [ ] End-to-end test passes

### Validation Commands

```bash
# Test 1: QA Validator
python3 -c "
from qa_validator import PersonaQAValidator
import json
validator = PersonaQAValidator()
with open('batch1_personas/cardiology_001_stemi_male_65_persona.json') as f:
    result = validator.validate_single_persona(json.load(f))
print('✅ QA Pass' if result['overall_pass'] else '❌ QA Fail')
"

# Test 2: Database
psql -U postgres -h localhost -p 5433 -d irstudy_medical -c \
  "SELECT COUNT(*) FROM patient_personas;"
# Expected: 207

# Test 3: Frontend API
curl http://localhost:8000/api/v1/personas?specialty=Cardiology | jq '. | length'
# Expected: 45
```

---

## 🐛 Troubleshooting

### Ralph Loop Stuck

```bash
# Kill tmux session
tmux kill-session -t ralph-roadmap

# Check state file
cat .ralph-roadmap-state.json | jq '.current_prd'

# Resume from current PRD
./scripts/ralph-roadmap-loop.sh
```

### PRD Fails

```bash
# Check logs
ls -lht clinical-content-prds/roadmap-prds/logs/ | head -5

# View latest log
tail -100 clinical-content-prds/roadmap-prds/logs/PRD-WEEK1-*.log
```

### Manual Execution

If Ralph loop fails, execute PRD manually:

```bash
# Read the PRD
cat clinical-content-prds/roadmap-prds/week1-critical/PRD-WEEK1-001-FIX-QA-VALIDATOR.md

# Follow implementation steps manually
# Run test commands
# Mark as complete in state file
```

---

## 📈 Adding New PRDs

### Create New PRD

```bash
# Week 2 example
cat > clinical-content-prds/roadmap-prds/week2-important/PRD-WEEK2-001-USER-TESTING.md <<'EOF'
# PRD-WEEK2-001: User Testing Setup

**Priority**: P1
**Time**: 2 hours

## Success Criteria
- [ ] 10 alpha testers recruited
- [ ] Feedback form created
- [ ] Analytics tracking enabled

## Implementation Steps
1. Create Google Form for feedback
2. Set up Mixpanel analytics
3. Send invites to testers
...
EOF
```

### Ralph Loop Auto-Discovery

The loop automatically finds new PRDs in:
- `week1-critical/PRD-*.md`
- `week2-important/PRD-*.md`
- `month2-scaling/PRD-*.md`

---

## 🎯 Next Steps After Week 1

1. ✅ Create Week 2 PRDs (user testing, citation enhancement)
2. ✅ Create Month 2 PRDs (knowledge base expansion, Batch 2-10)
3. ✅ Run Ralph loop for Week 2
4. ✅ Monitor user feedback
5. ✅ Iterate based on results

---

**Created**: 2026-03-16
**Last Updated**: 2026-03-16
**Version**: 1.0
**Status**: ✅ Ready for Execution
