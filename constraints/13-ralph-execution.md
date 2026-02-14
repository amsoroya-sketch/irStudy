# Constraint 13: Ralph Execution Requirements
**Autonomous AI Development Loop Standards**

**Version:** 1.0
**Date:** 2026-02-07
**Status:** MANDATORY
**Applies To:** All PROMPT.md files, PRD files, and Ralph-driven development

---

## 📋 Overview

This constraint defines requirements for writing effective prompts and PRDs that enable successful autonomous execution with Ralph (the AI development loop system). Failure to follow these guidelines results in premature loop exits, wasted API calls, and incomplete tasks.

**Problem Solved:** Ralph interprets questions like "Would you like me to proceed?" as completion signals and exits prematurely. This constraint prevents that.

---

## 🚨 Critical Rules

### Rule 1: AUTONOMOUS EXECUTION MODE Header

**REQUIRED**: Every PROMPT.md and PRD file MUST start with:

```markdown
# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: [Specific task description with duration]

**EXECUTE NOW**:
[Exact bash/Python/TypeScript commands here]

**DO NOT**:
- ❌ Ask "Would you like me to proceed?"
- ❌ Ask "Should I start with X?"
- ❌ Wait for approval
- ❌ Ask clarifying questions

**START IMMEDIATELY. NO QUESTIONS.**
```

**Why:** This header sets clear expectations that the AI should execute immediately without asking for permission.

---

### Rule 2: Directive Language Only

❌ **NEVER use these phrases:**
- "Would you like me to..."
- "Should I..."
- "Could you..."
- "Please let me know if..."
- "May I proceed with..."
- "Do you want me to..."

✅ **ALWAYS use directive language:**
- "EXECUTE NOW:"
- "RUN these commands:"
- "CREATE these files:"
- "UPDATE @fix_plan.md to mark complete"
- "COMMIT with message: [exact message]"

**Example:**

```markdown
❌ WRONG:
"Would you like me to run the security scan now?"

✅ CORRECT:
"EXECUTE NOW:
```bash
cd /home/dev/Development/irStudy/backend
bandit -r src/ -f json -o security_reports/bandit_report.json
```"
```

---

### Rule 3: Exact Commands (No Placeholders)

**REQUIRED**: All bash/Python/TypeScript commands must be copy-paste executable with NO placeholders.

❌ **WRONG (has placeholders):**
```bash
# Set up the database
docker-compose up -d
# Configure the environment variables
```

✅ **CORRECT (exact commands):**
```bash
cd /home/dev/Development/irStudy
docker-compose -f docker-compose.yml up -d postgres redis qdrant vault
cp .env.example .env
echo "DATABASE_URL=postgresql://amc_user:$(openssl rand -hex 16)@localhost:5433/irstudy_medical" >> .env
```

---

### Rule 4: Current Task Clearly Specified

**REQUIRED**: The PROMPT.md file MUST specify the exact current task at the top.

❌ **WRONG (too vague):**
```markdown
**CURRENT TASK**: Execute all Week 1 tasks
```

✅ **CORRECT (specific task):**
```markdown
**CURRENT TASK**: TASK_001 - API Security Audit (6-8 hours)

Run Bandit and Safety scans on backend codebase, fix all P0/P1 vulnerabilities, integrate security scanning into GitHub Actions CI/CD pipeline.

**COMPLETE WHEN**:
- Bandit scan: 0 HIGH/CRITICAL issues
- Safety scan: 0 CRITICAL vulnerabilities
- GitHub Actions workflow: `.github/workflows/security-scan.yml` operational
- Security audit report: Generated at `backend/docs/security_audit_report_2026-02-07.md`
```

---

### Rule 5: Success Criteria with Verification Commands

**REQUIRED**: Every task MUST have measurable success criteria with explicit verification commands.

❌ **WRONG (no verification):**
```markdown
✅ Security scan complete
✅ All tests pass
```

✅ **CORRECT (with verification commands):**
```markdown
✅ Security scan complete:
```bash
bandit -r src/ -f json -o bandit_final.json
CRITICAL=$(cat bandit_final.json | jq '.results[] | select(.issue_severity == "HIGH" or .issue_severity == "CRITICAL")' | wc -l)
[ "$CRITICAL" -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL ($CRITICAL issues)"
```

✅ All tests pass:
```bash
pytest -v tests/
# Expected: 100% pass rate, 0 failures
```
```

---

### Rule 6: What to Do WHEN COMPLETE

**REQUIRED**: Every PRD/PROMPT.md MUST specify what to do after task completion.

✅ **CORRECT format:**
```markdown
## When Complete

```bash
# 1. Update @fix_plan.md
sed -i 's/TASK_001.*TODO/TASK_001: ✅ DONE/' @fix_plan.md

# 2. Commit changes
git add .
git commit -m "security: Complete TASK_001 API security audit - 0 P0/P1 vulnerabilities

- Bandit scan: 0 HIGH/CRITICAL issues
- Safety scan: 0 CRITICAL vulnerabilities
- OWASP Top 10 compliance verified

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. Move to next task
echo "✅ TASK_001 complete. Starting TASK_002..."
# Read PRD_TASK_002_QUESTION_MANAGEMENT_CRUD.md
```
```

---

## 📝 PROMPT.md Template (Ralph-Compatible)

**File:** `PROMPT.md` (project root)

```markdown
# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_001 - API Security Audit (6-8 hours)

**EXECUTE NOW**:

Read and execute the following PRD:
`/home/dev/Development/irStudy/planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_001_API_SECURITY_AUDIT.md`

Follow ALL instructions in the PRD exactly as written. DO NOT ask questions.

**DO NOT**:
- ❌ Ask "Would you like me to proceed?"
- ❌ Ask "Should I run the security scan now?"
- ❌ Wait for approval before executing commands
- ❌ Skip steps or ask for clarification

**WHEN COMPLETE**:
1. Update @fix_plan.md: Change "TASK_001: TODO" → "TASK_001: ✅ DONE"
2. Commit with message: "security: Complete TASK_001 - API security audit"
3. Output: "✅ TASK_001 complete. Ready for TASK_002."

**START IMMEDIATELY.**
```

---

## 📋 PRD Structure Requirements

Every PRD file MUST include these sections:

### 1. AUTONOMOUS EXECUTION MODE Header
```markdown
# AUTONOMOUS EXECUTION MODE - NO QUESTIONS

**CURRENT TASK**: TASK_NNN - [Title] ([Duration])

**EXECUTE NOW**:
[Exact commands]

**DO NOT ASK QUESTIONS**
```

### 2. Metadata Block
```markdown
**Metadata:**
- **Week:** 1
- **Day:** 1-2 (Feb 7-8, 2026)
- **Duration:** 6-8 hours
- **Priority:** P0-Critical
- **Dependencies:** None (or list specific tasks)
- **Owner:** security-compliance-expert + rust-ffi-expert
- **Status:** 🟡 Not Started
```

### 3. Objectives (4-6 measurable goals)
```markdown
## 🎯 Objectives

1. **Comprehensive security audit** of all backend API endpoints
2. **Identify and fix** all P0/P1 vulnerabilities (target: zero)
3. **Implement automated security scanning** in CI/CD pipeline
```

### 4. Constraints (READ FIRST)
```markdown
## 🚨 Constraints (READ FIRST)

**From `/home/dev/Development/irStudy/constraints/README.md`:**

❌ **NEVER:**
- Hardcode database credentials
- Skip HTTPS/TLS for API endpoints

✅ **ALWAYS:**
- Use environment variables for secrets
- Implement rate limiting on ALL endpoints
```

### 5. Implementation Guide (Step-by-Step)
```markdown
## 📋 Implementation Guide

### Step 1: Setup (30 min)
```bash
cd /home/dev/Development/irStudy/backend
pip install bandit safety
```

### Step 2: Run Scans (1 hour)
```bash
bandit -r src/ -f json -o security_reports/bandit_report.json
```
```

### 6. Validation Checklist
```markdown
## ✅ Validation Checklist

Run these commands to verify:

```bash
# Verify Bandit passes
CRITICAL=$(cat bandit_final.json | jq '.results[] | select(.issue_severity == "HIGH")' | wc -l)
[ "$CRITICAL" -eq 0 ] && echo "✅ PASS" || echo "❌ FAIL"
```
```

### 7. Success Criteria (Exit Conditions)
```markdown
## 🎯 Success Criteria

**This task is DONE when ALL of these are true:**

1. ✅ Bandit scan: 0 HIGH/CRITICAL issues
2. ✅ Safety scan: 0 CRITICAL vulnerabilities
3. ✅ GitHub Actions workflow operational
```

### 8. When Complete
```markdown
## 🔄 When Complete

```bash
# 1. Update @fix_plan.md
sed -i 's/TASK_NNN.*TODO/TASK_NNN: ✅ DONE/' @fix_plan.md

# 2. Commit
git commit -m "feat(scope): description"

# 3. Next task
echo "✅ TASK_NNN complete. Starting TASK_[NNN+1]..."
```
```

---

## 🔍 Quality Checks Before Running Ralph

**Run these checks on PROMPT.md and PRD files:**

```bash
# Check 1: No question phrases
grep -E "(Would you|Should I|Could you|Please|May I)" PROMPT.md
# Expected: Empty output (no matches)

# Check 2: Has AUTONOMOUS EXECUTION MODE header
grep -q "AUTONOMOUS EXECUTION MODE" PROMPT.md && echo "✅ Header present" || echo "❌ Missing header"

# Check 3: Has exact commands (not just descriptions)
grep -q "```bash" planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_*.md && echo "✅ Commands present" || echo "❌ No commands"

# Check 4: Has success criteria
grep -q "Success Criteria" planning/phase1-mvp-implementation-feb7-2026/prds/PRD_TASK_*.md && echo "✅ Criteria present" || echo "❌ Missing criteria"
```

---

## ⚠️ Common Mistakes & Fixes

### Mistake 1: Too Polite Language

❌ **WRONG:**
"Please run the following commands when you're ready:"

✅ **CORRECT:**
"EXECUTE NOW:"

### Mistake 2: Vague Success Criteria

❌ **WRONG:**
"✅ Task complete when security is improved"

✅ **CORRECT:**
"✅ Task complete when Bandit reports 0 HIGH/CRITICAL issues (verified with command: `bandit -r src/`)"

### Mistake 3: No Verification Commands

❌ **WRONG:**
"✅ All tests should pass"

✅ **CORRECT:**
```markdown
✅ All tests pass:
```bash
pytest -v tests/
# Expected output: 100% pass rate, 0 failures, exit code 0
```
```

### Mistake 4: Multiple Choice Questions

❌ **WRONG:**
"Should I use approach A or approach B?"

✅ **CORRECT:**
"EXECUTE using approach A (rationale: faster, fewer dependencies)"

---

## 📚 References

**Ralph Documentation:**
- [Ralph CLAUDE.md](/home/dev/Development/ralph-claude-code/CLAUDE.md) - Full Ralph loop documentation
- [Ralph Global Config](~/.ralph/CLAUDE.md) - Agent OS best practices
- [Prerequisite System](/home/dev/Development/ralph-claude-code/docs/PREREQUISITE_SYSTEM.md) - Manual intervention workflows

**Project-Specific:**
- [PROJECT_CONSTRAINTS.md](/home/dev/Development/irStudy/PROJECT_CONSTRAINTS.md) - Top 10 critical constraints
- [constraints/README.md](/home/dev/Development/irStudy/constraints/README.md) - All constraint modules

**Troubleshooting:**
- [Stale State Premature Exit](/home/dev/Development/ralph-claude-code/docs/troubleshooting/2026-02-01-stale-state-premature-exit.md)
- [Writing Effective Prompts](/home/dev/Development/ralph-claude-code/docs/WRITING_EFFECTIVE_PROMPTS.md)

---

## ✅ Compliance Checklist

**Before starting Ralph loop, verify:**

- [ ] PROMPT.md has "AUTONOMOUS EXECUTION MODE" header
- [ ] PROMPT.md has "EXECUTE NOW" section with exact commands
- [ ] PROMPT.md has "DO NOT" section listing forbidden questions
- [ ] PROMPT.md specifies current task clearly at top
- [ ] All PRD files have exact bash/Python/TypeScript commands
- [ ] All PRD files have verification commands with expected output
- [ ] All PRD files have "When Complete" section
- [ ] No "Would you like..." phrasing in any file
- [ ] Success criteria are specific and measurable
- [ ] @fix_plan.md exists and tracks task completion

---

**Last Updated:** 2026-02-07
**Version:** 1.0
**Status:** MANDATORY
**Enforcement:** All Ralph-driven development MUST follow these rules

**Violation Impact:** Premature loop exits, wasted API calls, incomplete tasks, failed quality gates

**Responsible Owner:** Project Manager + AI Agent Coordinator
