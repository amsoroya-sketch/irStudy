# Evaluation System - Quick Start Guide

**For:** irStudy Medical Content Evaluation System
**Version:** 1.0
**Date:** 2026-03-25

---

## 🚀 How to Run the Evaluation System

### Prerequisites

```bash
# Python 3.9+ required
python3 --version

# Install dependencies
pip3 install anthropic pyyaml numpy pandas plotly flask

# Verify Claude API key configured
echo $ANTHROPIC_API_KEY
```

### Step 1: Verify Setup (Week 1-2 Complete)

```bash
cd /home/dev/Development/irStudy

# Verify expert agents exist
ls -lh .claude/agents/*.md
# Expected: 13 agent files (10,000+ lines total)

# Verify registry exists
ls -lh evaluation-system/data/knowledge_item_registry.json
# Expected: ~2.2 MB file with 3,170 items

# Verify agent assignments
python3 << 'EOF'
import json
with open('evaluation-system/data/knowledge_item_registry.json', 'r') as f:
    registry = json.load(f)
pending = [item for item in registry['knowledge_items'] if item['evaluation_status'] == 'pending']
print(f"✅ Pending items with agents assigned: {len([i for i in pending if i.get('assigned_agents')])}")
print(f"Total pending: {len(pending)}")
EOF
# Expected: ✅ Pending items with agents assigned: 2963
```

### Step 2: Run Evaluation (Week 3)

**Option A: Full Automated Run (Recommended)**

```bash
# Run evaluation orchestrator (evaluates all 2,963 items)
cd evaluation-system
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --batch-size 5 \
  --max-parallel-agents 10 \
  --output-dir reports/iteration_1

# Expected output:
# ================================================================================
# irStudy Evaluation Orchestrator
# ================================================================================
# Registry: 3,170 items (2,963 pending)
# Batch size: 5 items
# Max parallel agents: 10
#
# 🔄 Starting evaluation...
#   Batch 1/593: Processing items 1-5...
#   Batch 2/593: Processing items 6-10...
#   ...
#   [Progress: 25%] Evaluated 750/2,963 items (avg score: 7.4)
#   [Progress: 50%] Evaluated 1,500/2,963 items (avg score: 7.6)
#   [Progress: 75%] Evaluated 2,250/2,963 items (avg score: 7.8)
#   [Progress: 100%] Evaluated 2,963/2,963 items (avg score: 8.1)
#
# ✅ Evaluation complete!
# Reports saved to: evaluation-system/reports/iteration_1/
# Duration: 6.2 hours
```

**Option B: Test Run (Small Sample)**

```bash
# Evaluate 10 items only (for testing)
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --batch-size 2 \
  --max-items 10 \
  --output-dir reports/test_run

# Expected: Completes in ~5 minutes
```

**Option C: Specific Specialty Only**

```bash
# Evaluate cardiology items only
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --specialty cardiology \
  --output-dir reports/cardiology_only

# Expected: ~495 cardiology items evaluated
```

### Step 3: Analyze Results (Week 4)

```bash
# Generate issue analysis report
python3 core/issue_analyzer.py \
  --reports-dir reports/iteration_1 \
  --output reports/issue_analysis.json

# Expected output:
# ================================================================================
# Issue Analysis Report
# ================================================================================
# Total violations: 4,521
# By severity:
#   - critical: 234 (5.2%)
#   - warning: 1,876 (41.5%)
#   - suggestion: 2,411 (53.3%)
#
# Top 10 issues:
#   1. Missing PBS streamline code (567 items, 19.1%)
#   2. Acetaminophen used instead of paracetamol (234 items, 7.9%)
#   3. RAG citation confidence <0.65 (123 items, 4.2%)
#   ...
#
# Auto-fixable: 3,167 (70.0%)
# Manual review: 1,354 (30.0%)
```

### Step 4: Apply Auto-Fixes

```bash
# Run auto-fix engine
python3 core/auto_fix_engine.py \
  --reports-dir reports/iteration_1 \
  --registry-path data/knowledge_item_registry.json \
  --output-dir fixes/iteration_1 \
  --dry-run  # Remove --dry-run to apply fixes

# Expected output:
# ================================================================================
# Auto-Fix Engine
# ================================================================================
# Loading 2,963 evaluation reports...
# Analyzing fixable issues...
#
# Fixes to apply:
#   - australian_drug_names: 234 items (acetaminophen → paracetamol)
#   - pbs_codes: 567 items (add missing PBS codes)
#   - citation_format: 89 items (standardize RAG citations)
#
# Total fixes: 890 items (30.0% of evaluated items)
#
# [DRY RUN] No changes applied. Remove --dry-run to apply fixes.

# Apply fixes (remove --dry-run)
python3 core/auto_fix_engine.py \
  --reports-dir reports/iteration_1 \
  --registry-path data/knowledge_item_registry.json \
  --output-dir fixes/iteration_1

# ✅ Fixes applied to 890 items
# Backup created: fixes/iteration_1/backup/
```

### Step 5: Re-Evaluate Fixed Items

```bash
# Re-evaluate only items with fixes
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --only-fixed-items \
  --output-dir reports/iteration_2

# Expected: 890 items re-evaluated
# Avg score improvement: 7.2 → 8.6 (+1.4 points)
```

### Step 6: Manual Review Queue

```bash
# Generate manual review queue
python3 core/manual_review_queue.py \
  --reports-dir reports/iteration_2 \
  --output manual_review_queue.json

# Expected output:
# ================================================================================
# Manual Review Queue
# ================================================================================
# Items requiring manual review: 334
#
# By reason:
#   - Overall score <7.0: 67
#   - RAG citation issues (hallucinations): 123
#   - Clinical safety concerns: 34
#   - Agent disagreement (variance >2.0): 110
#
# Priority order (critical first):
#   1. persona_emergency_082_septic_male_82 (clinical safety)
#   2. mcq_psychiatry_045 (RAG hallucination)
#   ...

# Review items interactively
python3 core/manual_review_ui.py \
  --queue manual_review_queue.json

# Opens interactive CLI interface:
# ┌────────────────────────────────────────────────────────────┐
# │ Manual Review Queue (334 items)                            │
# │                                                             │
# │ [1/334] persona_emergency_082_septic_male_82               │
# │ Reason: Clinical safety - Dangerous medication combination│
# │ Score: 4.2/10.0                                            │
# │                                                             │
# │ Violation: Gentamicin + Vancomycin without renal monitoring│
# │                                                             │
# │ Actions:                                                    │
# │   [F]ix manually   [S]kip   [A]pprove anyway  [R]eject    │
# │                                                             │
# └────────────────────────────────────────────────────────────┘
```

### Step 7: Launch Dashboard (Real-Time Monitoring)

```bash
# Start dashboard server
cd evaluation-system/dashboard
python3 api.py

# Expected output:
# * Running on http://localhost:5000
# * Dashboard available at: http://localhost:5000/dashboard

# Open browser to http://localhost:5000/dashboard
# See real-time evaluation progress, scores, issues
```

---

## 📊 Monitoring Progress

### Check Evaluation Status

```bash
# Quick status check
python3 << 'EOF'
import json
with open('evaluation-system/data/knowledge_item_registry.json', 'r') as f:
    registry = json.load(f)

items = registry['knowledge_items']
total = len(items)
completed = len([i for i in items if i['evaluation_status'] == 'completed'])
pending = len([i for i in items if i['evaluation_status'] == 'pending'])

print(f"Total: {total}")
print(f"Completed: {completed} ({completed/total*100:.1f}%)")
print(f"Pending: {pending} ({pending/total*100:.1f}%)")

# Calculate approval rate
if completed > 0:
    approved = len([i for i in items if i.get('overall_score', 0) >= 8.0])
    print(f"Approved (≥8.0): {approved}/{completed} ({approved/completed*100:.1f}%)")
EOF
```

### Check Agent Performance

```bash
# Agent evaluation counts
python3 << 'EOF'
import json
from collections import Counter

with open('evaluation-system/data/knowledge_item_registry.json', 'r') as f:
    registry = json.load(f)

all_agents = []
for item in registry['knowledge_items']:
    all_agents.extend(item.get('assigned_agents', []))

agent_counts = Counter(all_agents)
print("Agent Workload:")
for agent, count in agent_counts.most_common():
    print(f"  {agent}: {count} items")
EOF
```

### Check Issue Trends

```bash
# Issue frequency over time
python3 core/issue_trends.py \
  --reports-dir reports/ \
  --output issue_trends.png

# Generates graph showing:
# - Issue count decreasing over iterations
# - Auto-fix success rate increasing
# - Approval rate trending up
```

---

## 🔄 Iterative Improvement Workflow

### Iteration 1: Initial Evaluation + Auto-Fix

```bash
# 1. Evaluate all items
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --output-dir reports/iteration_1

# 2. Analyze issues
python3 core/issue_analyzer.py \
  --reports-dir reports/iteration_1 \
  --output reports/iteration_1_analysis.json

# 3. Apply auto-fixes
python3 core/auto_fix_engine.py \
  --reports-dir reports/iteration_1 \
  --registry-path data/knowledge_item_registry.json \
  --output-dir fixes/iteration_1

# 4. Re-evaluate fixed items
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --only-fixed-items \
  --output-dir reports/iteration_1_reeval

# 5. Check improvement
python3 << 'EOF'
import json
with open('reports/iteration_1_analysis.json') as f:
    before = json.load(f)
with open('reports/iteration_1_reeval/summary.json') as f:
    after = json.load(f)

print(f"Score improvement: {before['avg_score']:.1f} → {after['avg_score']:.1f}")
print(f"Approval rate: {before['approval_rate']:.1f}% → {after['approval_rate']:.1f}%")
EOF
```

### Iteration 2: Manual Review + Targeted Fixes

```bash
# 1. Generate manual review queue (items that couldn't be auto-fixed)
python3 core/manual_review_queue.py \
  --reports-dir reports/iteration_1_reeval \
  --output manual_review_queue_iter2.json

# 2. Review items (human in the loop)
python3 core/manual_review_ui.py \
  --queue manual_review_queue_iter2.json

# 3. Re-evaluate manually corrected items
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --only-manually-corrected \
  --output-dir reports/iteration_2
```

### Iteration 3: Final Polish

```bash
# 1. Identify remaining low-scoring items
python3 << 'EOF'
import json
with open('evaluation-system/data/knowledge_item_registry.json', 'r') as f:
    registry = json.load(f)

low_scorers = [
    item for item in registry['knowledge_items']
    if item.get('overall_score', 10) < 8.0
]

print(f"Items still below 8.0: {len(low_scorers)}")
with open('low_scorers.json', 'w') as f:
    json.dump(low_scorers, f, indent=2)
EOF

# 2. Manual review of remaining items
# (target: <5% of total items)

# 3. Final evaluation run
python3 core/evaluation_orchestrator.py \
  --registry-path data/knowledge_item_registry.json \
  --only-below-threshold 8.0 \
  --output-dir reports/iteration_3
```

---

## 📈 Success Metrics

### After Each Iteration, Check:

```bash
python3 << 'EOF'
import json
with open('evaluation-system/data/knowledge_item_registry.json', 'r') as f:
    registry = json.load(f)

items = [i for i in registry['knowledge_items'] if i.get('overall_score')]

# Calculate metrics
scores = [i['overall_score'] for i in items]
avg_score = sum(scores) / len(scores)
approval_rate = len([s for s in scores if s >= 8.0]) / len(scores) * 100
excellent_rate = len([s for s in scores if s >= 9.0]) / len(scores) * 100

# Critical violations
critical_violations = sum(
    len(i.get('quality_gate_violations', []))
    for i in items
)

print("=" * 60)
print("SUCCESS METRICS")
print("=" * 60)
print(f"Average Score: {avg_score:.2f}/10.0")
print(f"Approval Rate (≥8.0): {approval_rate:.1f}%")
print(f"Excellent Rate (≥9.0): {excellent_rate:.1f}%")
print(f"Critical Violations: {critical_violations}")
print()
print("Targets:")
print(f"  ✅ Avg Score ≥8.5: {'PASS' if avg_score >= 8.5 else 'FAIL'}")
print(f"  ✅ Approval ≥95%: {'PASS' if approval_rate >= 95 else 'FAIL'}")
print(f"  ✅ Zero Critical: {'PASS' if critical_violations == 0 else 'FAIL'}")
EOF
```

---

## 🛠️ Troubleshooting

### Evaluation Runs Slowly

```bash
# Increase batch size (trade memory for speed)
python3 core/evaluation_orchestrator.py \
  --batch-size 10 \  # Default: 5
  --max-parallel-agents 15  # Default: 10
```

### Claude API Rate Limits

```bash
# Add delays between batches
python3 core/evaluation_orchestrator.py \
  --batch-delay 5  # Wait 5 seconds between batches
```

### Agent Errors

```bash
# Check agent delegation logs
tail -f evaluation-system/logs/agent_errors.log

# Re-run failed items only
python3 core/evaluation_orchestrator.py \
  --retry-failed-only
```

### Disk Space Issues

```bash
# Evaluation reports can be large (3,000+ JSON files)
# Check disk usage
du -sh evaluation-system/reports/

# Compress old iterations
tar -czf iteration_1.tar.gz evaluation-system/reports/iteration_1/
rm -rf evaluation-system/reports/iteration_1/
```

---

## 📝 Final Deliverables

After completing all iterations:

```bash
# Generate master evaluation report
python3 core/generate_master_report.py \
  --registry-path data/knowledge_item_registry.json \
  --output MASTER_EVALUATION_REPORT.md

# Expected: Comprehensive report with:
# - Summary statistics (3,170 items, 99% approved)
# - Score distribution by content type
# - Score distribution by specialty
# - Top issues identified and resolved
# - Agent performance analysis
# - Recommendations for future content
```

---

**Ready to Start?**

```bash
# Quick start command (evaluates first 10 items as test)
cd /home/dev/Development/irStudy
python3 evaluation-system/core/evaluation_orchestrator.py \
  --max-items 10 \
  --output-dir evaluation-system/reports/test

# Full production run (all 2,963 items)
python3 evaluation-system/core/evaluation_orchestrator.py \
  --output-dir evaluation-system/reports/production_run_1
```

**Next Steps:** Create `evaluation_orchestrator.py` (Week 3)
