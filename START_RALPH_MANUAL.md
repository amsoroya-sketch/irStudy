# Manual Ralph Startup Guide

**Fixed:** Ralph now uses `--no-continue` flag to prevent session continuity issues.

---

## 🚀 Quick Start

```bash
cd /home/dev/Development/irStudy

# Option 1: Use automation script (recommended)
./run_ralph_prds.sh

# Option 2: Manual tmux + Ralph
tmux new-session -s ralph-irstudy-mvp
ralph --no-continue --calls 50 --timeout 30
```

---

## ✅ What Was Fixed

**Issue:** Ralph was continuing from old session context (Login component fixes) instead of starting fresh with TASK_001 PRD.

**Fix Applied:** Added `--no-continue` flag to `run_ralph_prds.sh` (line 249)

**Before:**
```bash
ralph --monitor --calls 50 --timeout 30
```

**After:**
```bash
ralph --no-continue --calls 50 --timeout 30
```

This ensures each task starts with a clean slate.

---

## 📊 Current Status

- ✅ **PROMPT.md:** Updated with TASK_001 PRD (API Security Audit)
- ✅ **@fix_plan.md:** Updated with 14 Phase 1 MVP tasks
- ✅ **Ralph state:** Cleaned (exit signals, circuit breaker, session)
- ✅ **Script fixed:** `--no-continue` flag added
- 🎯 **Ready to start:** TASK_001

---

## 🎮 How to Start Ralph

### Using Automation Script (Easiest)

```bash
cd /home/dev/Development/irStudy
./run_ralph_prds.sh
```

This will:
1. ✅ Verify dependencies (tmux, ralph, PRDs)
2. ✅ Initialize Ralph files (@fix_plan.md, @AGENT.md)
3. ✅ Create 3-pane tmux session
4. ✅ Copy TASK_001 PRD to PROMPT.md
5. ✅ Start Ralph with `--no-continue` flag
6. ✅ Enable live monitoring

**Pane Layout:**
```
┌─────────────────────┬────────────────────┐
│ Ralph Execution     │ Live Logs          │
│ (Claude output)     │ (tail -f logs/)    │
├─────────────────────┴────────────────────┤
│ Status (watch status.json)              │
└─────────────────────────────────────────┘
```

**Controls:**
- `Ctrl+B, D` - Detach (Ralph keeps running)
- `Ctrl+B, ←/→/↑/↓` - Navigate panes
- `Ctrl+B, [` - Scroll mode

### Manual tmux Start (Advanced)

```bash
cd /home/dev/Development/irStudy

# 1. Create tmux session
tmux new-session -s ralph-manual -n task-001

# 2. Split panes
tmux split-window -h
tmux split-window -v -t 0

# 3. Pane 0: Ralph execution
tmux send-keys -t 0 "cd /home/dev/Development/irStudy" C-m
tmux send-keys -t 0 "ralph --no-continue --calls 50 --timeout 30" C-m

# 4. Pane 1: Logs
tmux send-keys -t 1 "cd /home/dev/Development/irStudy" C-m
tmux send-keys -t 1 "tail -f logs/*.log" C-m

# 5. Pane 2: Status
tmux send-keys -t 2 "cd /home/dev/Development/irStudy" C-m
tmux send-keys -t 2 "watch -n 5 'cat status.json | jq .'" C-m

# 6. Attach
tmux attach -t ralph-manual
```

---

## 🔍 Monitoring Commands

```bash
# Check status without attaching
./run_ralph_prds.sh --status

# View live logs
tail -f ralph_logs/task_001_*.log

# Check progress
grep "TASK_" @fix_plan.md

# Check circuit breaker
ralph --circuit-status

# List tmux sessions
tmux list-sessions

# Attach to running session
tmux attach -t ralph-irstudy-mvp
```

---

## 🎯 What Ralph Will Do

**TASK_001: API Security Audit (6-8 hours)**

1. Install Bandit + Safety security tools
2. Run security scans on backend code
3. Fix P0/P1 vulnerabilities:
   - Hardcoded credentials
   - Weak JWT secrets
   - Missing rate limiting
   - CORS misconfigurations
4. OWASP Top 10 verification
5. Harden JWT authentication
6. Integrate security scans into CI/CD
7. Generate security audit report

**Expected Output:**
- Security reports in `backend/security_reports/`
- Updated `.github/workflows/` with security scans
- Git commit: `feat(security): Complete TASK_001 API Security Audit...`
- @fix_plan.md updated: `TASK_001: ✅ DONE`

---

## ✅ Success Criteria

TASK_001 is complete when:

- [ ] Bandit scan: 0 HIGH/CRITICAL issues
- [ ] Safety check: 0 vulnerabilities
- [ ] JWT_SECRET_KEY: ≥32 characters
- [ ] OWASP Top 10: All verified
- [ ] GitHub Actions: Security workflow added
- [ ] Security report: Generated
- [ ] Git commit: Created
- [ ] @fix_plan.md: Marked ✅ DONE

---

## 🚨 If Ralph Exits Early Again

**Symptoms:**
- Ralph exits after 1-3 loops
- "Strong completion indicators" message
- Task not actually complete

**Fixes:**

1. **Reset everything:**
   ```bash
   ralph --clean
   ralph --reset-session
   ralph --reset-circuit
   ```

2. **Check session state:**
   ```bash
   cat .ralph_session
   # Should be empty or recent timestamp
   ```

3. **Verify PROMPT.md:**
   ```bash
   head -10 PROMPT.md
   # Should show TASK_001 PRD header
   ```

4. **Check for old session:**
   ```bash
   grep -i "login\|typescript" logs/claude_output_*.log | tail -5
   # Should NOT show old Login/TypeScript work
   ```

5. **Restart with forced fresh start:**
   ```bash
   rm -f .ralph_session .ralph_session_history
   ./run_ralph_prds.sh --task 1
   ```

---

## 📁 Key Files

```
/home/dev/Development/irStudy/
├── run_ralph_prds.sh              ✅ Fixed (--no-continue added)
├── PROMPT.md                      ✅ TASK_001 PRD
├── @fix_plan.md                   ✅ 14 MVP tasks
├── .ralph_session                 (empty/clean)
├── .exit_signals                  (reset)
└── ralph_logs/
    └── task_001_*.log             (will be created)
```

---

## 🎉 Ready to Start

Everything is fixed and ready. Choose your method:

**Easy:** `./run_ralph_prds.sh` (automated tmux setup)
**Manual:** Create tmux session yourself (full control)

Ralph will now start fresh on TASK_001 without any old session context! 🚀

---

**Last Updated:** 2026-02-08 07:56
**Fix Applied:** `--no-continue` flag added to prevent session continuity
**Status:** ✅ Ready for execution
