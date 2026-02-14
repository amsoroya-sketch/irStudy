# Ralph PRD Automation System

**Version:** 1.0
**Date:** 2026-02-07
**Status:** Ready for Execution

---

## Overview

This automation system runs all 14 Phase 1 MVP PRDs sequentially using Ralph in monitored tmux sessions. Each PRD is executed autonomously with real-time monitoring, logging, and progress tracking.

## Quick Start

### 1. Run All PRDs from Start

```bash
cd /home/dev/Development/irStudy
./run_ralph_prds.sh
```

This will:
- Initialize Ralph in the irStudy project
- Create tmux session with 3-pane monitoring layout
- Start TASK_001 (API Security Audit)
- Show live logs, status, and execution output

### 2. Attach to Running Session

```bash
tmux attach -t ralph-irstudy-mvp
```

**Tmux Controls:**
- `Ctrl+B, D` - Detach from session (Ralph keeps running)
- `Ctrl+B, ←/→/↑/↓` - Navigate between panes
- `Ctrl+B, [` - Enter scroll mode (use arrow keys, press `q` to exit)

### 3. Check Status

```bash
./run_ralph_prds.sh --status
```

Shows:
- Active tmux sessions
- Task progress from @fix_plan.md
- Latest log files
- Ralph status.json

### 4. Start from Specific Task

```bash
# Start from TASK_005 (skip first 4 tasks)
./run_ralph_prds.sh --task 5
```

---

## Tmux Session Layout

When you attach to the tmux session, you'll see:

```
┌─────────────────────────────────┬─────────────────────────────────┐
│                                 │                                 │
│  Pane 0: Ralph Execution        │  Pane 1: Live Logs              │
│  - Claude Code output           │  - tail -f logs/*.log           │
│  - Loop iterations              │  - Real-time log streaming      │
│  - Task progress                │                                 │
│                                 │                                 │
├─────────────────────────────────┴─────────────────────────────────┤
│                                                                   │
│  Pane 2: Status Monitoring                                        │
│  - watch -n 5 'cat status.json | jq .'                            │
│  - Updates every 5 seconds                                        │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## All Available Commands

### Execution Commands

```bash
# Run all 14 PRDs from start
./run_ralph_prds.sh

# Start from specific task (1-14)
./run_ralph_prds.sh --task 5

# Dry run (show execution plan without running)
./run_ralph_prds.sh --dry-run
```

### Monitoring Commands

```bash
# Attach to active session
./run_ralph_prds.sh --monitor-only
# OR
tmux attach -t ralph-irstudy-mvp

# Check status
./run_ralph_prds.sh --status

# View logs manually
tail -f ralph_logs/task_001_*.log
```

### Management Commands

```bash
# Stop all Ralph sessions
./run_ralph_prds.sh --stop

# Clean Ralph state files
./run_ralph_prds.sh --clean

# Show help
./run_ralph_prds.sh --help
```

---

## Workflow for All 14 Tasks

### Step-by-Step Process

1. **Start Task 1:**
   ```bash
   cd /home/dev/Development/irStudy
   ./run_ralph_prds.sh
   ```

2. **Monitor Progress:**
   - Attach to tmux: `tmux attach -t ralph-irstudy-mvp`
   - Watch Ralph execute the PRD
   - Look for completion signals:
     - `TASK_001: ✅ DONE` in @fix_plan.md
     - Git commit created
     - Ralph loop exits

3. **When Task 1 Completes:**
   - Detach from tmux: `Ctrl+B, D`
   - Verify completion: `./run_ralph_prds.sh --status`
   - Start Task 2: `./run_ralph_prds.sh --task 2`

4. **Repeat for Tasks 2-14:**
   ```bash
   # After each task completes
   ./run_ralph_prds.sh --task 3
   ./run_ralph_prds.sh --task 4
   # ... etc
   ```

### Automated Continuation (Optional)

Create a watch script to auto-advance:

```bash
#!/bin/bash
# auto_advance.sh

for task in {1..14}; do
    echo "Starting TASK_$(printf '%03d' $task)..."
    ./run_ralph_prds.sh --task $task

    # Wait for Ralph to exit
    while tmux has-session -t ralph-irstudy-mvp 2>/dev/null; do
        sleep 30
    done

    echo "TASK_$(printf '%03d' $task) complete. Moving to next..."
    sleep 10
done

echo "🎉 All 14 tasks complete!"
```

---

## Task Checklist

Track your progress through all 14 PRDs:

### Week 1: Backend Foundation (22-29 hours)
- [ ] **TASK_001:** API Security Audit (6-8h) - P0-Critical
- [ ] **TASK_002:** Question Management CRUD (6-8h) - P0-Critical
- [ ] **TASK_003:** Study Card System (4-5h) - P1-High
- [ ] **TASK_004:** User Progress Tracking (4-5h) - P1-High
- [ ] **TASK_005:** Spaced Repetition Engine (3-4h) - P1-High

### Week 2: Frontend Development (21-27 hours)
- [ ] **TASK_006:** Quiz Interface Redesign (8-10h) - P0-Critical
- [ ] **TASK_007:** Citation Display Component (3-4h) - P1-High
- [ ] **TASK_008:** Performance Dashboard (6-8h) - P1-High
- [ ] **TASK_009:** Mobile Responsive Design (4-5h) - P1-High

### Week 3: Integration & Launch (24-30 hours)
- [ ] **TASK_010:** E2E Testing Suite (6-8h) - P0-Critical
- [ ] **TASK_011:** RAG Explanation Engine (5-6h) - P1-High
- [ ] **TASK_012:** Load Testing & Optimization (4-5h) - P1-High
- [ ] **TASK_013:** Deployment Pipeline (5-6h) - P0-Critical
- [ ] **TASK_014:** MVP Validation & Launch (4-5h) - P0-Critical

---

## File Structure

```
/home/dev/Development/irStudy/
├── run_ralph_prds.sh              # Main automation script
├── RALPH_PRD_AUTOMATION.md        # This documentation
├── PROMPT.md                      # Current PRD (auto-updated)
├── @fix_plan.md                   # Task progress checklist
├── @AGENT.md                      # Build instructions
├── ralph_logs/                    # Execution logs
│   ├── task_001_20260207_*.log
│   ├── task_002_20260207_*.log
│   └── ...
├── logs/                          # Ralph internal logs
├── status.json                    # Ralph status
├── .ralph_session                 # Session tracking
└── planning/phase1-mvp-implementation-feb7-2026/
    └── prds/                      # All 14 PRD files
        ├── PRD_TASK_001_API_SECURITY_AUDIT.md
        ├── PRD_TASK_002_QUESTION_MANAGEMENT_CRUD.md
        └── ... (14 total)
```

---

## Completion Criteria for Each Task

Before moving to the next task, verify:

1. **@fix_plan.md Updated:**
   ```bash
   grep "TASK_001.*✅ DONE" @fix_plan.md
   ```

2. **Git Commit Created:**
   ```bash
   git log --oneline -1 | grep "TASK_001"
   ```

3. **Ralph Exit Status:**
   - Ralph loop exits cleanly
   - No errors in status.json
   - Circuit breaker state: CLOSED

4. **Deliverables Created:**
   - Check for files mentioned in PRD success criteria
   - Verify tests pass (if applicable)
   - Confirm validation checklist complete

---

## Troubleshooting

### Ralph Exits Prematurely

**Symptom:** Ralph exits after 1-2 loops without completing task

**Solutions:**
1. Check if PRD has question-based phrasing:
   ```bash
   grep -E "Would you|Should I|Please" PROMPT.md
   ```

2. Clean stale state:
   ```bash
   ./run_ralph_prds.sh --clean
   ralph --reset-session
   ```

3. Check exit signals:
   ```bash
   cat .exit_signals | jq .
   ```

### Tmux Session Not Found

**Symptom:** `./run_ralph_prds.sh --monitor-only` fails

**Solutions:**
1. Check active sessions:
   ```bash
   tmux list-sessions
   ```

2. Start a new task:
   ```bash
   ./run_ralph_prds.sh --task 1
   ```

### Circuit Breaker Opens

**Symptom:** Ralph stops with circuit breaker OPEN

**Solutions:**
1. Check circuit breaker status:
   ```bash
   ralph --circuit-status
   ```

2. Review recent errors:
   ```bash
   tail -50 ralph_logs/task_*.log
   ```

3. Reset circuit breaker:
   ```bash
   ralph --reset-circuit
   ralph --reset-session
   ```

4. Restart current task:
   ```bash
   ./run_ralph_prds.sh --task X  # Replace X with current task number
   ```

### Task Stalls (No Progress)

**Symptom:** Ralph runs but makes no progress for 30+ minutes

**Solutions:**
1. Attach to session and check:
   ```bash
   tmux attach -t ralph-irstudy-mvp
   ```

2. Check if waiting for prerequisite:
   ```bash
   ls tasks/*/prereq.sh
   ```

3. Increase timeout:
   ```bash
   ralph --timeout 30  # 30 minutes instead of 15
   ```

---

## Logs and Monitoring

### Log Files

**Ralph Execution Logs:**
- Location: `ralph_logs/task_NNN_YYYYMMDD_HHMMSS.log`
- Content: Full Ralph output, Claude responses, errors
- Retention: Keep all logs for post-mortem analysis

**Ralph Internal Logs:**
- Location: `logs/loop_*.log`
- Content: Internal Ralph loop state, circuit breaker events
- Automatically rotated

### Monitoring Files

**status.json:**
```json
{
  "status": "running",
  "current_task": "TASK_001",
  "loop_count": 5,
  "circuit_breaker": "CLOSED",
  "last_update": "2026-02-07T12:00:00Z"
}
```

**@fix_plan.md:**
- Real-time task progress
- Updated by Ralph after each task completion
- Checkboxes: `[ ]` (pending) → `[x]` (done)

---

## Performance Expectations

### Per-Task Execution Time

| Task | Estimated | Actual (TBD) | Notes |
|------|-----------|--------------|-------|
| TASK_001 | 6-8h | ___ | Security audit may need manual verification |
| TASK_002 | 6-8h | ___ | CRUD endpoints with Australian drug validation |
| TASK_003 | 4-5h | ___ | Study card system with SM-2 algorithm |
| TASK_004 | 4-5h | ___ | Progress tracking analytics |
| TASK_005 | 3-4h | ___ | Database optimization for SM-2 |
| TASK_006 | 8-10h | ___ | React quiz interface (longest frontend task) |
| TASK_007 | 3-4h | ___ | Citation display component |
| TASK_008 | 6-8h | ___ | Performance dashboard with Recharts |
| TASK_009 | 4-5h | ___ | Mobile responsive design + PWA |
| TASK_010 | 6-8h | ___ | Playwright E2E tests (20+ scenarios) |
| TASK_011 | 5-6h | ___ | Qdrant RAG integration |
| TASK_012 | 4-5h | ___ | Locust load testing (500 users) |
| TASK_013 | 5-6h | ___ | Railway + Vercel deployment |
| TASK_014 | 4-5h | ___ | Beta user onboarding + launch |

**Total:** 67-86 hours

---

## Success Metrics

### Overall Phase 1 Completion Criteria

- [ ] All 14 tasks marked complete in @fix_plan.md
- [ ] 14 git commits created (one per task)
- [ ] Backend: API endpoints functional (TASK_001-005)
- [ ] Frontend: All pages rendering (TASK_006-009)
- [ ] Integration: E2E tests passing (TASK_010)
- [ ] Performance: Load tests passing (TASK_012)
- [ ] Deployment: Production URLs live (TASK_013)
- [ ] Launch: 50 beta users onboarded (TASK_014)

### Quality Gates

**Week 1 Gate:**
- Backend API security: 0 HIGH/CRITICAL issues
- All unit tests passing
- Database migrations successful

**Week 2 Gate:**
- Frontend TypeScript: 0 errors
- All components rendering
- Mobile responsive (Lighthouse >90)

**Week 3 Gate (FINAL):**
- E2E tests: 100% pass rate
- Load test: 500 users, <2s page load
- Production deployment: successful
- 50 beta users: active

---

## Next Steps After Completion

Once all 14 PRDs are complete:

1. **Verify MVP Completeness:**
   ```bash
   ./run_ralph_prds.sh --status
   git log --oneline | grep "TASK_" | wc -l  # Should be 14
   ```

2. **Run Full Test Suite:**
   ```bash
   cd backend && pytest tests/ -v
   cd ../frontend && npm test
   npx playwright test
   ```

3. **Deploy to Production:**
   - Follow TASK_013 deployment checklist
   - Verify health checks: `/api/v1/health/readiness`
   - Monitor Sentry for errors

4. **Onboard Beta Users:**
   - Follow TASK_014 beta user onboarding script
   - Send welcome emails
   - Distribute feedback survey

5. **Monitor First 24 Hours:**
   - Sentry error dashboard
   - Prometheus metrics
   - User feedback survey responses

---

## Support and Issues

### Ralph System Issues

- **Documentation:** `~/.ralph/README.md`
- **GitHub:** https://github.com/anthropics/ralph-claude-code/issues
- **Reset all state:** `ralph --clean && ralph --reset-circuit && ralph --reset-session`

### irStudy PRD Issues

- **PRD Location:** `/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/`
- **Constraint Documentation:** `/home/dev/Development/irStudy/constraints/`
- **Project Constraints:** `/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md`

---

**Last Updated:** 2026-02-07
**Version:** 1.0
**Automation Script:** `run_ralph_prds.sh` (16KB)
**Total PRDs:** 14
**Estimated Time:** 67-86 hours
