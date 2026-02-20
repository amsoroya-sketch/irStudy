# Ralph PRD Multi-Execution Plan

**Created**: 2026-02-16 17:50
**Status**: Ready for Launch
**Purpose**: Execute multiple PRD projects concurrently using separate tmux sessions

---

## 📊 Summary of All PRD Projects

### **Total PRD Documentation Created Today (Feb 16, 2026)**

| System | PRD Count | Size | Lines | Location |
|--------|-----------|------|-------|----------|
| **EMR Practice System** | 14 | 1,052 KB | 27,716 | `/16-feb-ralph-prds/` |
| **AI OSCE Simulation** | 8 | 476 KB | 11,459 | `/ai-osce-ralph-prds/` |
| **Phase 1 MVP Tasks** | 14 | 280 KB | ~7,000 | `/planning/phase1-mvp-implementation-feb7-2026/prds/` |
| **EMR Ralph Phases** | 4 phases | - | - | `/emr-practice-system/ralph-prds/` |
| **TOTAL** | **36+** | **1,808+ KB** | **46,175+ lines** | Multiple directories |

---

## 🎯 Executable Ralph Projects (3 Active)

### **Project 1: Main Phase 1 MVP** (P0-Critical)
- **Session Name**: `ralph-main`
- **Location**: `/home/dev/Development/irStudy/`
- **PROMPT.md**: ✅ Present
- **Status**: 🟢 READY TO EXECUTE
- **Description**: 14 MVP tasks (API Security, CRUD, Study Cards, Progress Tracking, etc.)
- **Estimated Time**: 68-96 hours total
- **Current Task**: TASK_001 - API Security Audit (6-8h)

**Tasks**:
1. TASK_001: API Security Audit (6-8h)
2. TASK_002: Question Management CRUD (6-8h)
3. TASK_003: Study Card System (4-5h)
4. TASK_004: User Progress Tracking (4-5h)
5. TASK_005: Spaced Repetition Engine (3-4h)
6. TASK_006: Quiz Interface Redesign (8-10h)
7. TASK_007: Citation Display Component (3-4h)
8. TASK_008: Performance Dashboard (6-8h)
9. TASK_009: Mobile Responsive Design (4-5h)
10. TASK_010: E2E Testing Suite (6-8h)
11. TASK_011: RAG Explanation Engine (5-6h)
12. TASK_012: Load Testing & Optimization (4-5h)
13. TASK_013: Deployment Pipeline (5-6h)
14. TASK_014: MVP Validation & Launch (4-5h)

---

### **Project 2: EMR PRD Refinement** (P1-High)
- **Session Name**: `ralph-emr`
- **Location**: `/home/dev/Development/irStudy/emr-practice-system/emr-ralph-project/`
- **PROMPT.md**: ✅ Present
- **Status**: 🟢 READY TO EXECUTE
- **Description**: Refine EMR PRDs for AMC Clinical Examination alignment
- **Current Task**: Read @fix_plan.md and execute first TODO

**Existing PRDs to Refine**:
- 00_MASTER_EMR_PRD.md (31KB)
- 01_CERNER_POWERCHART_UI_PRD.md (27KB)
- 02_EPIC_EHR_UI_PRD.md (37KB)
- 03_BACKEND_API_PRD.md (33KB)
- 04_TESTING_STRATEGY_PRD.md (33KB)

**Refinement Goals**:
- AMC Clinical Examination alignment (NOT ICRP)
- Australian medical context (eTG/AMH guidelines)
- World-class implementation documentation

---

### **Project 3: Backend Monitoring** (P2-Medium)
- **Session Name**: `ralph-backend`
- **Location**: `/home/dev/Development/irStudy/backend-features-15-feb/`
- **PROMPT.md**: ✅ Present
- **Status**: 🟡 COMPLETE (Monitoring only)
- **Description**: Phase 0 documentation and monitoring

**Completed Phases**:
- ✅ Phase 0.1: Clinical Accuracy (100%)
- ✅ Phase 0.2: Security Hardening (100%)
- ✅ Phase 0.3: Database Optimization (85%)

---

## 📁 PRD Documentation (Not Executable - Already Complete)

### **16-feb-ralph-prds/** - EMR System PRDs
**Status**: ✅ Documentation Complete (14 PRDs)
**Purpose**: Specifications for implementation (NOT Ralph tasks)

- Backend: 5 PRDs (Database, Session API, Validation API, OSCE Converter, Analytics API)
- Frontend: 4 PRDs (Epic UI, Cerner UI, Dashboard, Validation Display)
- Integration: 3 PRDs (OSCE-EMR Linking, Unified Progress, Smart Recommendations)
- Testing: 3 PRDs (E2E Tests, AI Validation Accuracy, Performance Benchmarks)

**These are RALPH-formatted specifications** to guide implementation, not tasks to execute in Ralph loop.

---

### **ai-osce-ralph-prds/** - AI OSCE System PRDs
**Status**: ✅ Documentation Complete (8 PRDs)
**Purpose**: Specifications for implementation (NOT Ralph tasks)

- Backend/Infrastructure: 4 PRDs
- Frontend: 1 PRD
- Testing/QA: 1 PRD
- Content Creation: 1 PRD
- Mock Exam Mode: 1 PRD

**These are RALPH-formatted specifications** to guide implementation, not tasks to execute in Ralph loop.

---

## 🚀 Execution Strategy

### **Option A: Sequential Execution (Safe)**
1. Launch `ralph-main` first
2. Wait for TASK_001-003 to complete
3. Launch `ralph-emr` in parallel
4. Monitor both sessions concurrently

### **Option B: Concurrent Execution (Fast)**
1. Launch all READY projects simultaneously
2. Monitor all sessions with unified dashboard
3. Each session runs independently in tmux

### **Option C: Selective Execution**
1. Choose specific project(s) to execute
2. Manual launch and monitoring

---

## 🛠️ Usage Instructions

### **1. Launch Projects**
```bash
cd /home/dev/Development/irStudy
./launch_all_ralph_prds.sh
```

**Interactive Menu**:
- `1` - Launch Main Project only
- `2` - Launch EMR PRD Refinement only
- `3` - Launch Backend Monitoring (skip if COMPLETE)
- `A` - Launch all READY projects concurrently
- `Q` - Quit without launching

### **2. Monitor All Sessions**
```bash
cd /home/dev/Development/irStudy
./monitor_all_ralph_sessions.sh
```

**Dashboard Shows**:
- Active sessions status
- Loop count and API usage
- Task progress (@fix_plan.md)
- Circuit breaker state
- Recent activity logs

### **3. Attach to Individual Session**
```bash
# Main project
tmux attach -t ralph-main

# EMR refinement
tmux attach -t ralph-emr

# Backend monitoring
tmux attach -t ralph-backend
```

**Within Session**:
- `Ctrl+B` then `D` - Detach (keeps running)
- `Ctrl+B` then `↑`/`↓` - Switch between panes
- `Ctrl+C` - Stop Ralph loop

### **4. Manage Sessions**
```bash
# List all sessions
tmux list-sessions

# Kill specific session
tmux kill-session -t ralph-main

# Kill all Ralph sessions
tmux kill-session -a -t ralph-
```

---

## 📋 Expected Outcomes

### **Main Project (ralph-main)**
- **Duration**: 68-96 hours (spread over 2-3 weeks)
- **Output**: 14 completed MVP tasks
- **Deliverables**:
  - API security hardened (0 HIGH/CRITICAL vulnerabilities)
  - Question management CRUD complete
  - Study card system implemented
  - Progress tracking operational
  - Spaced repetition engine working
  - Quiz interface redesigned
  - E2E testing suite passing
  - Production deployment pipeline ready

### **EMR Refinement (ralph-emr)**
- **Duration**: 20-30 hours
- **Output**: 5 refined PRD documents
- **Deliverables**:
  - AMC Clinical Examination alignment verified
  - Australian medical context embedded
  - Implementation-ready specifications
  - Architecture decision records (ADRs)

---

## ⚠️ Important Notes

### **PRD Documentation vs. Ralph Execution**
- **📄 PRDs in 16-feb-ralph-prds/ and ai-osce-ralph-prds/** are DOCUMENTATION (RALPH-formatted specifications)
- **🚀 PROMPT.md projects** are EXECUTABLE tasks for Ralph loop
- **Don't confuse**: PRD files describe WHAT to build, PROMPT.md tells Ralph HOW to build it

### **Rate Limits**
- Each session configured for 50 calls/hour (configurable)
- Total concurrent: 150 calls/hour maximum
- Monitor API usage to avoid limits

### **Session Continuity**
- Ralph sessions persist in tmux (detach-safe)
- Can attach/detach without interrupting execution
- Sessions survive terminal disconnection

### **Circuit Breaker**
- Automatic halt if stagnation detected
- Manual reset: `ralph --reset-circuit`
- Check status: `ralph --circuit-status`

---

## 📞 Quick Reference

| Task | Command |
|------|---------|
| Launch all projects | `./launch_all_ralph_prds.sh` |
| Monitor all sessions | `./monitor_all_ralph_sessions.sh` |
| Attach to main | `tmux attach -t ralph-main` |
| Attach to EMR | `tmux attach -t ralph-emr` |
| List sessions | `tmux list-sessions` |
| Kill session | `tmux kill-session -t <name>` |
| Detach from session | `Ctrl+B` then `D` |
| Switch panes | `Ctrl+B` then `↑`/`↓` |

---

## ✅ Pre-Launch Checklist

- [x] All PROMPT.md files validated
- [x] Ralph loop script tested
- [x] Tmux installed and available
- [x] Launch script created and executable
- [x] Monitor script created and executable
- [x] Documentation complete
- [ ] User approval to launch
- [ ] Select execution strategy (A, B, or C)
- [ ] Begin execution

---

**Ready to Execute**: All systems ready. Run `./launch_all_ralph_prds.sh` to begin.

**Estimated Total Time**: 88-126 hours across all projects (with concurrent execution: 2-3 weeks calendar time)

**Next Action**: User decision on execution strategy
