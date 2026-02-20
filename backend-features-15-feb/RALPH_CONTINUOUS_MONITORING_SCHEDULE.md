# Ralph Continuous Monitoring Schedule

**Project**: irStudy Backend Features Implementation
**Loop Type**: Ralph Documentation Monitoring
**Created**: 2026-02-15
**Status**: ACTIVE

---

## Monitoring Overview

**Purpose**: Automated quality assurance for Phase 0 documentation and approval tracking

**Monitoring Frequency**:
- Automated checks: Every 30 minutes
- Manual reviews: Daily (9:00 AM local time)
- Approval tracking: Daily (5:00 PM local time)

**Duration**: Until Phase 1 implementation begins (estimated 5 business days)

---

## Automated Monitoring (Every 30 Minutes)

### 1. Documentation Quality Checks

**File Integrity**:
```bash
# Check all expected files exist
files=(
  "README.md"
  "HANDOVER_DOCUMENT.md"
  "IMPLEMENTATION_STATUS_REPORT.md"
  "APPROVAL_SUBMISSION_CHECKLIST.md"
  "ralph-documentation/README.md"
  "ralph-documentation/ADR-001-AMC-RUBRIC-DESIGN.md"
  "ralph-documentation/ADR-002-SECURITY-ARCHITECTURE.md"
  "ralph-documentation/ADR-003-DATABASE-PERFORMANCE-OPTIMIZATION.md"
  "phase0-week01-clinical-accuracy/DIVERSE_CLINICAL_SCENARIOS.md"
  "phase0-week01-clinical-accuracy/RAG_VALIDATION_SPECIFICATION.md"
  "phase0-week01-clinical-accuracy/GOLDEN_DATASET_SPECIFICATION.md"
  "phase0-week02-security-hardening/SECURITY_VERIFICATION_REPORT.md"
  "phase0-week02-security-hardening/SECURITY_AUDIT_REPORT.md"
  "phase0-week03-database-optimization/PERFORMANCE_BENCHMARKS.md"
  "phase0-week03-database-optimization/IMPLEMENTATION_SUMMARY.md"
)

for file in "${files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "⚠️ ALERT: Missing file: $file"
  fi
done
```

**Cross-Reference Validation**:
```bash
# Check for broken references (excluding known monitoring reports)
grep -r "AMC_15_MARK_RUBRIC_EXPANDED\.md" . \
  --exclude="RALPH_MONITORING_REPORT_2026-02-15.md" \
  --exclude=".response_analysis" \
  --exclude-dir=".git"

# Alert if any references found (should be 0 after fixes)
if [ $? -eq 0 ]; then
  echo "⚠️ ALERT: Found references to old AMC rubric file"
fi
```

**Markdown Syntax Validation**:
```bash
# Validate all markdown files have valid structure
for md_file in $(find . -name "*.md" -type f); do
  # Check for unclosed code blocks
  backticks=$(grep -c '^```' "$md_file")
  if [ $((backticks % 2)) -ne 0 ]; then
    echo "⚠️ ALERT: Unclosed code block in $md_file"
  fi

  # Check for broken markdown links
  grep -o '\[.*\](.*)' "$md_file" | grep -v '^#' | while read link; do
    target=$(echo "$link" | sed 's/.*(\(.*\))/\1/')
    if [[ $target == /* ]] && [ ! -f "$target" ]; then
      echo "⚠️ ALERT: Broken link in $md_file: $target"
    fi
  done
done
```

### 2. Security Monitoring

**Hardcoded Credentials Scan**:
```bash
# Scan for hardcoded credentials patterns
patterns=(
  '(password|secret|api_key|db_pass|dbKey|dbPath)\s*=\s*["\x27][^"\x27]+["\x27]'
  'ENCRYPTION_KEY\s*=\s*["\x27][^"\x27]+'
  'DATABASE_PASSWORD\s*=\s*["\x27][^"\x27]+'
  'JWT_SECRET\s*=\s*["\x27][^"\x27]+'
)

for pattern in "${patterns[@]}"; do
  matches=$(grep -rE "$pattern" ../backend/src --include="*.py" | grep -v "README.md")
  if [ -n "$matches" ]; then
    echo "🚨 CRITICAL ALERT: Hardcoded credentials detected!"
    echo "$matches"
  fi
done
```

**Security Test Status** (requires manual approval currently):
```bash
# Note: This requires bash command approval, so manual check for now
# TODO: Automate in CI/CD pipeline

# Manual check command (when approved):
# cd ../backend && python -m pytest tests/test_api/test_security/ --tb=line -q

# Expected output: 16 passed in ~X.XXs
# Alert if: Any failures detected
```

**Scan Report Freshness**:
```bash
# Check if security scan reports are up to date (within 24 hours)
bandit_report="phase0-week02-security-hardening/bandit_report.json"
safety_report="phase0-week02-security-hardening/safety_report.json"

if [ -f "$bandit_report" ]; then
  age=$(find "$bandit_report" -mtime +1)
  if [ -n "$age" ]; then
    echo "⚠️ ALERT: Bandit report older than 24 hours"
  fi
fi

if [ -f "$safety_report" ]; then
  age=$(find "$safety_report" -mtime +1)
  if [ -n "$age" ]; then
    echo "⚠️ ALERT: Safety report older than 24 hours"
  fi
fi
```

### 3. Database Performance Monitoring

**Query Performance Validation**:
```bash
# Verify database indexes still exist and are being used
# Note: Requires database connection

# Commands to run (when database available):
# psql -U postgres -d irstudy_dev -c "\d+ emr_sessions" | grep idx_emr_sessions_active
# psql -U postgres -d irstudy_dev -c "\d+ mcqs" | grep idx_mcqs_difficulty_specialty
# psql -U postgres -d irstudy_dev -c "\d+ study_cards" | grep idx_study_cards_due_optimized
# psql -U postgres -d irstudy_dev -c "\d+ user_progress" | grep idx_user_progress_specialty_updated
# psql -U postgres -d irstudy_dev -c "\d+ osces" | grep idx_osces_specialty_difficulty

# Alert if any index missing
```

**Migration File Integrity**:
```bash
# Verify migration files not modified
migration_file="phase0-week03-database-optimization/migration_add_indexes.sql"
alembic_file="../backend/alembic/versions/20260215_1453_009_add_critical_performance_indexes.py"

if [ ! -f "$migration_file" ]; then
  echo "🚨 CRITICAL ALERT: Migration SQL file missing!"
fi

if [ ! -f "$alembic_file" ]; then
  echo "🚨 CRITICAL ALERT: Alembic migration file missing!"
fi
```

### 4. ADR Status Tracking

**ADR File Monitoring**:
```bash
# Check ADR status fields for consistency
adr_files=(
  "ralph-documentation/ADR-001-AMC-RUBRIC-DESIGN.md"
  "ralph-documentation/ADR-002-SECURITY-ARCHITECTURE.md"
  "ralph-documentation/ADR-003-DATABASE-PERFORMANCE-OPTIMIZATION.md"
)

for adr in "${adr_files[@]}"; do
  status=$(grep "^\*\*Status\*\*:" "$adr" | head -1)
  echo "ADR: $adr - $status"

  # Alert if status changed unexpectedly
  if echo "$status" | grep -q "Deprecated\|Superseded"; then
    echo "⚠️ ALERT: ADR status changed to Deprecated/Superseded: $adr"
  fi
done
```

---

## Manual Monitoring (Daily at 9:00 AM)

### Daily Quality Review Checklist

**Documentation Health**:
- [ ] All 17 Phase 0 files present and accessible
- [ ] No new broken links introduced
- [ ] Code examples still syntactically correct
- [ ] Australian terminology maintained (no American terms)
- [ ] Citations complete and properly formatted

**Security Health**:
- [ ] Zero hardcoded credentials (automated scan passed)
- [ ] Security test pass rate 100% (if automated)
- [ ] No new HIGH/CRITICAL vulnerabilities
- [ ] Bandit/Safety reports current (within 24 hours)

**Database Health**:
- [ ] All 5 indexes present in database
- [ ] Query performance maintained (<0.1ms average)
- [ ] Migration files intact
- [ ] No database schema drift

**ADR Health**:
- [ ] All 3 ADRs have correct status
- [ ] Approval tracking up to date
- [ ] Related ADRs properly linked
- [ ] Version history current

### Daily Monitoring Report Template

```markdown
# Daily Ralph Monitoring Report - [DATE]

**Loop Iteration**: [Number]
**Status**: ✅ Healthy / ⚠️ Issues Detected / 🚨 Critical Issues

## Automated Checks Summary

**Documentation Quality**: [PASS/FAIL]
- Files present: [X/17]
- Broken links: [X found]
- Syntax errors: [X found]

**Security Status**: [PASS/FAIL]
- Hardcoded credentials: [X found]
- Security tests: [X/16 passing]
- Scan freshness: [Current/Stale]

**Database Status**: [PASS/FAIL]
- Indexes present: [X/5]
- Migration files: [Intact/Modified]

**ADR Status**: [PASS/FAIL]
- All ADRs valid: [Yes/No]
- Status consistency: [Pass/Fail]

## Issues Detected

[List any issues found, or "None" if healthy]

## Actions Taken

[List any fixes applied, or "None" if no issues]

## Approval Tracking

See separate approval tracking report.

---

**Next Check**: [Tomorrow's date] 9:00 AM
**Alert Level**: [Low/Medium/High]
```

---

## Approval Tracking (Daily at 5:00 PM)

### Approval Status Update Template

```markdown
# Approval Tracking Update - [DATE]

**Days Since Submission**: [X days]

## Clinical Advisor (5-day timeline)

**Status**: [Not Submitted/Pending/In Review/Approved/Feedback Requested]
**Expected Completion**: 2026-02-22
**Days Remaining**: [X days]

**Latest Activity**:
- [Date]: [Action/update]

**Next Action**:
- [What needs to happen next]

## Security Team (3-day timeline)

**Status**: [Not Submitted/Pending/In Review/Approved/Feedback Requested]
**Expected Completion**: 2026-02-20
**Days Remaining**: [X days]

**Latest Activity**:
- [Date]: [Action/update]

**Next Action**:
- [What needs to happen next]

## DBA (2-day timeline)

**Status**: [Not Submitted/Pending/In Review/Approved/Feedback Requested]
**Expected Completion**: 2026-02-19
**Days Remaining**: [X days]

**Latest Activity**:
- [Date]: [Action/update]

**Next Action**:
- [What needs to happen next]

## Overall Progress

**Approvals Received**: [X/3]
**Critical Path Status**: [On Track/At Risk/Delayed]
**Estimated Phase 1 Start**: [Date]

## Blockers

[List any blockers, or "None"]

## Risks

[List any approval risks, or "None"]

---

**Next Update**: [Tomorrow's date] 5:00 PM
**Alert Level**: [Green/Yellow/Red]
```

### Approval Follow-Up Actions

**If No Response After 2 Days**:
1. Send friendly follow-up email
2. Check spam folder
3. Verify correct contact email
4. Escalate to PM if needed

**If Feedback Requested**:
1. Acknowledge within 4 hours
2. Assess complexity (minor/moderate/major)
3. Assign to appropriate expert agent
4. Respond within committed timeline
5. Request re-review

**If Approval Received**:
1. Update ADR status immediately
2. Update IMPLEMENTATION_STATUS_REPORT.md
3. Update ralph-documentation/README.md
4. Notify team
5. Check if all 3 approvals complete → trigger Phase 1 prep

---

## Monitoring Scripts

### Script 1: Full Automated Check

**Location**: `scripts/ralph_monitor.sh`

```bash
#!/bin/bash

# Ralph Continuous Monitoring Script
# Runs every 30 minutes via cron

echo "=== Ralph Monitoring Check: $(date) ==="

# 1. File integrity check
echo "Checking file integrity..."
missing_files=0
expected_files=(
  "README.md"
  "HANDOVER_DOCUMENT.md"
  "IMPLEMENTATION_STATUS_REPORT.md"
  "ralph-documentation/ADR-001-AMC-RUBRIC-DESIGN.md"
  "ralph-documentation/ADR-002-SECURITY-ARCHITECTURE.md"
  "ralph-documentation/ADR-003-DATABASE-PERFORMANCE-OPTIMIZATION.md"
)

for file in "${expected_files[@]}"; do
  if [ ! -f "$file" ]; then
    echo "⚠️ Missing: $file"
    ((missing_files++))
  fi
done

if [ $missing_files -eq 0 ]; then
  echo "✅ All files present"
else
  echo "🚨 ALERT: $missing_files files missing!"
fi

# 2. Cross-reference check
echo "Checking cross-references..."
old_refs=$(grep -r "AMC_15_MARK_RUBRIC_EXPANDED\.md" . \
  --exclude="RALPH_MONITORING_REPORT_2026-02-15.md" \
  --exclude=".response_analysis" \
  --exclude-dir=".git" \
  2>/dev/null | wc -l)

if [ $old_refs -eq 0 ]; then
  echo "✅ No broken references"
else
  echo "⚠️ ALERT: $old_refs references to old AMC rubric file found"
fi

# 3. Security scan
echo "Scanning for hardcoded credentials..."
creds=$(grep -rE '(password|secret|api_key)\s*=\s*["'"'"'][^"'"'"']+["'"'"']' \
  ../backend/src --include="*.py" | grep -v "README.md" | wc -l)

if [ $creds -eq 0 ]; then
  echo "✅ No hardcoded credentials"
else
  echo "🚨 CRITICAL: $creds hardcoded credentials detected!"
fi

# 4. Summary
echo "=== Check Complete: $(date) ==="
echo ""
```

**Cron Schedule**:
```cron
# Ralph monitoring - every 30 minutes during business hours (9 AM - 6 PM)
*/30 9-18 * * 1-5 cd /home/dev/Development/irStudy/backend-features-15-feb && ./scripts/ralph_monitor.sh >> logs/ralph_monitor.log 2>&1
```

### Script 2: Daily Approval Tracker

**Location**: `scripts/daily_approval_check.sh`

```bash
#!/bin/bash

# Daily Approval Tracking Script
# Runs at 5:00 PM daily

echo "=== Daily Approval Check: $(date) ==="

# Check if approval tracking file exists
tracking_file="approval_tracking_status.txt"

if [ ! -f "$tracking_file" ]; then
  echo "Creating initial tracking file..."
  cat > "$tracking_file" <<EOF
Clinical Advisor: Not Submitted
Security Team: Not Submitted
DBA: Not Submitted
EOF
fi

# Display current status
echo "Current Approval Status:"
cat "$tracking_file"

# Check for updates (manual process for now)
echo ""
echo "Action Items:"
echo "1. Check email for approval responses"
echo "2. Update tracking file if status changed"
echo "3. Send follow-up if no response after 2 days"
echo "4. Update ADRs if approvals received"

echo "=== Check Complete: $(date) ==="
```

**Cron Schedule**:
```cron
# Daily approval check - 5:00 PM weekdays
0 17 * * 1-5 cd /home/dev/Development/irStudy/backend-features-15-feb && ./scripts/daily_approval_check.sh
```

---

## Alert Levels

### 🟢 Low (Informational)

**Triggers**:
- Documentation files older than 7 days (no changes expected)
- Approval response within expected timeline
- All quality gates passing

**Action**: Log only, no immediate action needed

### 🟡 Medium (Warning)

**Triggers**:
- Broken cross-references detected
- Markdown syntax errors
- Security scan reports stale (>24 hours)
- Approval response delayed 1 day past timeline

**Action**: Investigate within 4 hours, fix within 1 business day

### 🔴 High (Critical)

**Triggers**:
- Hardcoded credentials detected
- Critical documentation files missing
- Security test failures
- Database indexes missing
- Approval delayed 3+ days past timeline

**Action**: Immediate investigation and escalation to PM Coordinator

---

## Monitoring Metrics Dashboard

### Key Performance Indicators

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Documentation Completeness | 100% | [X%] | [✅/⚠️/🚨] |
| Security Test Pass Rate | 100% | [X%] | [✅/⚠️/🚨] |
| Hardcoded Credentials | 0 | [X] | [✅/⚠️/🚨] |
| Broken Links | 0 | [X] | [✅/⚠️/🚨] |
| Database Indexes Present | 5/5 | [X/5] | [✅/⚠️/🚨] |
| Approvals Received | 3/3 | [X/3] | [✅/⚠️/🚨] |

### Monitoring Health Score

**Calculation**:
```
Health Score = (
  Documentation Quality (30%) +
  Security Status (30%) +
  Database Performance (20%) +
  Approval Progress (20%)
) / 100
```

**Thresholds**:
- 90-100: Excellent (Green)
- 75-89: Good (Yellow)
- 60-74: Fair (Orange)
- <60: Poor (Red)

---

## Monitoring Duration

**Start Date**: 2026-02-15
**End Date**: When all 3 approvals received + Phase 1 begins
**Estimated Duration**: 5-7 business days

**Transition Plan**:
When all approvals received:
1. Final monitoring report generated
2. Monitoring frequency reduced to weekly (Phase 1 documentation)
3. Focus shifts to Phase 1 implementation tracking

---

## Success Criteria

**Monitoring Loop Successful** if:
- ✅ 100% documentation quality maintained (no broken links, syntax errors)
- ✅ 100% security test pass rate throughout monitoring period
- ✅ Zero hardcoded credentials detected
- ✅ All 3 approvals received within 7 business days
- ✅ All ADRs updated with approval status
- ✅ Phase 1 implementation ready to start

---

**Document Created**: 2026-02-15
**Status**: ✅ ACTIVE
**Next Review**: Daily at 9:00 AM

**Prepared By**: Ralph Documentation Loop (Claude AI Agent)
**Loop Type**: Continuous monitoring + approval tracking

---

**END OF MONITORING SCHEDULE**
