# 🔄 Ralph Gap Analysis Loop - Usage Guide

**Status**: ✅ RUNNING in tmux session `ralph-gap`
**Current PRD**: PRD_GAP_001 (Infrastructure Deployment)
**Phase**: Phase 1 (P0 Critical Blockers)

---

## 📺 VIEW RALPH LOOP

### Attach to tmux session (interactive mode):
```bash
tmux attach -t ralph-gap
```

**Inside tmux**:
- The loop is PAUSED waiting for you to implement PRD_GAP_001
- It's showing you the implementation prompt
- Press ENTER when you complete the PRD

**To detach** (leave it running in background):
- Press: `Ctrl+B`, then `D`

### View without attaching (read-only):
```bash
# See recent output
tmux capture-pane -t ralph-gap -p | tail -50

# View logs
tail -f logs/ralph-gap-analysis-*.log
```

---

## 🚀 CURRENT STATE

Ralph loop is asking you to implement:

**PRD_GAP_001: Infrastructure Deployment**
- File: `gap-analysis-prds/phase1-p0-blockers/PRD_GAP_001_INFRASTRUCTURE_DEPLOYMENT.md`
- Effort: 6 hours
- Tasks:
  1. Deploy Vault server (1h)
  2. Deploy Redis server (1h)
  3. Remove .env.dev from git (2h)
  4. Fix security tests (2h)

---

## 🔧 HOW TO PROCEED

### Option 1: Implement PRD Manually, Then Resume Loop

```bash
# 1. Read the PRD
cat gap-analysis-prds/phase1-p0-blockers/PRD_GAP_001_INFRASTRUCTURE_DEPLOYMENT.md

# 2. Implement tasks (see PRD for detailed steps)
# Example:
vault server -dev -dev-root-token-id="dev-only-token" &
docker run -d --name irstudy-redis -p 6380:6379 redis:7
git rm --cached backend/.env.dev frontend/.env.dev
# ... etc

# 3. When complete, attach to Ralph loop
tmux attach -t ralph-gap

# 4. Press ENTER to indicate PRD is complete

# 5. Answer "yes" when asked if PRD is complete

# 6. Ralph will run quality gates and move to next PRD
```

### Option 2: Let Ralph Guide You Step-by-Step

```bash
# Attach to session
tmux attach -t ralph-gap

# Ralph shows you what to do
# Follow the prompt instructions
# Press ENTER when done
# Answer yes/no when prompted
```

### Option 3: Kill Loop and Work on PRDs Independently

```bash
# Kill the Ralph loop
tmux kill-session -t ralph-gap

# Work on PRDs manually
cat GAP_ANALYSIS_QUICK_START.md
# Follow Phase 1 checklist

# Restart Ralph later if needed
tmux new-session -d -s ralph-gap 'bash scripts/ralph-gap-analysis-loop.sh'
```

---

## 📊 CHECK PROGRESS

### View State File
```bash
cat .ralph-gap-analysis-state.json | jq '.'
```

**Current State**:
```json
{
  "phase": "phase1-p0-blockers",
  "current_prd": "PRD_GAP_001",
  "current_cycle": 18,
  "max_cycles": 30,
  "completed_prds": []
}
```

### View Logs
```bash
# Most recent log
ls -lt logs/ralph-gap-analysis-*.log | head -1

# Tail logs
tail -f logs/ralph-gap-analysis-20260313_114904.log
```

---

## ✅ QUALITY GATES

Ralph automatically runs quality gates after each PRD:

1. **Test pass rate**: `pytest --tb=short -q`
2. **Build errors**: `npm run build`
3. **Security violations**: `grep -rn "sk-ant-\|password="`
4. **Vault status**: `vault status`
5. **Redis status**: `redis-cli PING`

If any gate fails, Ralph will mark PRD as IN_PROGRESS and retry.

---

## 🔄 LOOP WORKFLOW

```
┌─────────────────────────────────────┐
│ Ralph Loop Cycle                    │
├─────────────────────────────────────┤
│ 1. Read next PRD from state file   │
│ 2. Display PRD prompt to user      │
│ 3. ⏸️  PAUSE - Wait for ENTER       │
│ 4. Ask: "Is PRD complete?"         │
│ 5. If yes → Run quality gates      │
│ 6. If gates pass → Mark complete   │
│ 7. Move to next PRD                │
│ 8. Sleep 5 seconds                 │
│ 9. Repeat                          │
└─────────────────────────────────────┘
```

---

## 🎯 NEXT STEPS

**Right Now**:
1. Ralph is waiting for you at PRD_GAP_001
2. Attach to session: `tmux attach -t ralph-gap`
3. See the implementation prompt
4. Read PRD file for detailed steps
5. Implement tasks
6. Press ENTER when done
7. Answer "yes" if complete

**Or**:
- Work on PRDs manually using `GAP_ANALYSIS_QUICK_START.md`
- Kill Ralph loop: `tmux kill-session -t ralph-gap`
- Resume later when needed

---

## 🆘 TROUBLESHOOTING

**Loop stuck?**
```bash
# Kill and restart
tmux kill-session -t ralph-gap
tmux new-session -d -s ralph-gap 'bash scripts/ralph-gap-analysis-loop.sh'
```

**Want to skip a PRD?**
```bash
# Attach to session
tmux attach -t ralph-gap
# Press ENTER
# Answer "no" when asked if complete
# Ralph will retry in next cycle
```

**Want to manually mark PRD complete?**
```bash
# Edit state file
vim .ralph-gap-analysis-state.json
# Add "PRD_GAP_001" to completed_prds array
# Change current_prd to "PRD_GAP_002"
```

---

## 📁 FILES REFERENCE

- **PRD Files**: `gap-analysis-prds/phase1-p0-blockers/PRD_GAP_*.md`
- **State File**: `.ralph-gap-analysis-state.json`
- **Logs**: `logs/ralph-gap-analysis-*.log`
- **Quick Start**: `GAP_ANALYSIS_QUICK_START.md`
- **Loop Script**: `scripts/ralph-gap-analysis-loop.sh`

---

**Ralph loop is READY and WAITING for you!** 🚀

Attach now: `tmux attach -t ralph-gap`
