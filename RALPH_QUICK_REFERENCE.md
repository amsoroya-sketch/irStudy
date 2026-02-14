# Ralph PRD Automation - Quick Reference Card

**TL;DR:** Run Ralph on all 14 PRDs sequentially in tmux with monitoring.

---

## 🚀 Quick Start (3 Commands)

```bash
cd /home/dev/Development/irStudy
./run_ralph_prds.sh                    # Start TASK_001
tmux attach -t ralph-irstudy-mvp      # Monitor progress
```

**Detach:** `Ctrl+B, D` (Ralph keeps running)

---

## 📋 All Commands

| Command | Purpose |
|---------|---------|
| `./run_ralph_prds.sh` | Run all 14 PRDs from start |
| `./run_ralph_prds.sh --task 5` | Start from TASK_005 |
| `./run_ralph_prds.sh --status` | Check progress |
| `./run_ralph_prds.sh --monitor-only` | Attach to running session |
| `./run_ralph_prds.sh --stop` | Stop all Ralph sessions |
| `./run_ralph_prds.sh --clean` | Reset Ralph state |
| `./run_ralph_prds.sh --dry-run` | Show execution plan |

---

## 🎯 Workflow for All 14 Tasks

```bash
# 1. Start Task 1
./run_ralph_prds.sh

# 2. Monitor
tmux attach -t ralph-irstudy-mvp
# Detach: Ctrl+B, D

# 3. When task completes, check status
./run_ralph_prds.sh --status

# 4. Start next task
./run_ralph_prds.sh --task 2

# 5. Repeat for tasks 2-14
./run_ralph_prds.sh --task 3
./run_ralph_prds.sh --task 4
# ... etc
```

---

## 📊 Tmux Layout

```
┌─────────────────────┬───────────────────────┐
│ Ralph Execution     │ Live Logs             │
│ (Claude output)     │ (tail -f logs/*.log)  │
├─────────────────────┴───────────────────────┤
│ Status Monitoring (status.json)             │
└─────────────────────────────────────────────┘
```

**Navigate:** `Ctrl+B, ←/→/↑/↓`
**Scroll:** `Ctrl+B, [` (arrow keys, `q` to exit)

---

## ✅ Task Completion Checklist

Before moving to next task:

1. **@fix_plan.md:** `TASK_XXX: ✅ DONE`
2. **Git commit:** Created with "feat(module): TASK_XXX..."
3. **Ralph exit:** Clean exit, no errors
4. **Deliverables:** Files created per PRD success criteria

---

## 🔧 Troubleshooting

### Ralph Exits Early
```bash
./run_ralph_prds.sh --clean
ralph --reset-session
ralph --reset-circuit
```

### Circuit Breaker Open
```bash
ralph --circuit-status
ralph --reset-circuit
./run_ralph_prds.sh --task X  # Restart current task
```

### No Tmux Session
```bash
tmux list-sessions
./run_ralph_prds.sh --task 1  # Start new session
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `PROMPT.md` | Current PRD (auto-updated) |
| `@fix_plan.md` | Task progress checklist |
| `ralph_logs/task_*.log` | Execution logs |
| `status.json` | Ralph current status |

---

## 📈 Progress Tracking

### Week 1: Backend (5 tasks, 22-29h)
- [ ] TASK_001: API Security Audit (6-8h)
- [ ] TASK_002: Question Management CRUD (6-8h)
- [ ] TASK_003: Study Card System (4-5h)
- [ ] TASK_004: User Progress Tracking (4-5h)
- [ ] TASK_005: Spaced Repetition Engine (3-4h)

### Week 2: Frontend (4 tasks, 21-27h)
- [ ] TASK_006: Quiz Interface Redesign (8-10h)
- [ ] TASK_007: Citation Display Component (3-4h)
- [ ] TASK_008: Performance Dashboard (6-8h)
- [ ] TASK_009: Mobile Responsive Design (4-5h)

### Week 3: Integration (5 tasks, 24-30h)
- [ ] TASK_010: E2E Testing Suite (6-8h)
- [ ] TASK_011: RAG Explanation Engine (5-6h)
- [ ] TASK_012: Load Testing & Optimization (4-5h)
- [ ] TASK_013: Deployment Pipeline (5-6h)
- [ ] TASK_014: MVP Validation & Launch (4-5h)

---

## 🎉 When Complete

```bash
# Verify all 14 tasks done
git log --oneline | grep "TASK_" | wc -l  # Should be 14

# Check @fix_plan.md
grep "✅ DONE" @fix_plan.md | wc -l  # Should be 14

# Deploy to production (TASK_013)
# Onboard beta users (TASK_014)
```

---

**Full Documentation:** `RALPH_PRD_AUTOMATION.md`
**Script Location:** `/home/dev/Development/irStudy/run_ralph_prds.sh`
**PRD Directory:** `planning/phase1-mvp-implementation-feb7-2026/prds/`
