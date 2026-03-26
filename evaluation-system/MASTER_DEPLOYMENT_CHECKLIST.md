# Master Deployment Checklist - irStudy Evaluation System

**Version:** 1.0
**Date:** 2026-03-25
**Status:** Pre-Production - Ready for Final Integration

---

## 📋 Pre-Deployment Verification

### Infrastructure Checklist ✅

- [x] **Expert Agents (13 total)**
  ```bash
  ls -1 .claude/agents/*.md | wc -l
  # Expected: 13+
  ```
  - [x] clinical-documentation-expert.md
  - [x] history-taking-expert.md
  - [x] physical-examination-expert.md
  - [x] procedural-skills-expert.md
  - [x] radiology-interpretation-expert.md
  - [x] medication-management-expert.md
  - [x] mental-health-crisis-expert.md
  - [x] pediatric-emergency-expert.md
  - [x] palliative-care-expert.md
  - [x] rural-medicine-expert.md
  - [x] pathology-interpretation-expert.md
  - [x] surgical-skills-expert.md
  - [x] infection-control-expert.md

- [x] **Knowledge Registry**
  ```bash
  python3 -c "import json; r=json.load(open('evaluation-system/data/knowledge_item_registry.json')); print(f'Items: {len(r[\"knowledge_items\"])}')"
  # Expected: Items: 3170
  ```
  - [x] 3,170 items catalogued
  - [x] 207 completed (with QA reports)
  - [x] 2,963 pending evaluation
  - [x] 10,679 agent assignments

- [x] **Evaluation Orchestrator**
  ```bash
  python3 evaluation-system/core/evaluation_orchestrator.py --max-items 1 --output-dir /tmp/test
  # Expected: 1 report generated, no errors
  ```
  - [x] Queue management functional
  - [x] Batch processing working (5 items parallel)
  - [x] Score aggregation correct
  - [x] Quality gates enforcing
  - [x] JSON reports generating

- [x] **Evaluation Prompts (13 templates)**
  ```bash
  ls -1 evaluation-system/config/evaluation_prompts/*.md | wc -l
  # Expected: 13
  ```
  - [x] medication_management_prompt.md (7.3 KB)
  - [x] clinical_documentation_prompt.md (7.8 KB)
  - [x] radiology_interpretation_prompt.md (2.4 KB)
  - [x] mental_health_crisis_prompt.md (2.9 KB)
  - [x] history-taking-expert_prompt.md (2.8 KB)
  - [x] physical-examination-expert_prompt.md (2.9 KB)
  - [x] pediatric-emergency-expert_prompt.md (2.9 KB)
  - [x] palliative-care-expert_prompt.md (2.9 KB)
  - [x] rural-medicine-expert_prompt.md (2.8 KB)
  - [x] pathology-interpretation-expert_prompt.md (2.9 KB)
  - [x] surgical-skills-expert_prompt.md (2.8 KB)
  - [x] infection-control-expert_prompt.md (2.9 KB)
  - [x] procedural-skills-expert_prompt.md (2.8 KB)

- [x] **Task Delegation Wrapper**
  ```bash
  python3 -c "import evaluation_system.core.claude_task_delegation as d; print('✅ Import successful')" 2>/dev/null || echo "⚠ Module path needs setup"
  ```
  - [x] load_item_content() implemented
  - [x] populate_prompt_template() implemented
  - [x] extract_json_from_response() implemented
  - [x] delegate_to_agent() implemented (simulation mode)
  - [ ] **TODO: Connect to real agents**

---

## 🔧 Integration Steps (Critical Path)

### Step 1: Real Agent Integration ⏳

**File:** `evaluation-system/core/claude_task_delegation.py`
**Line:** ~220-280 (in `delegate_to_agent()` function)

**Current State:**
```python
# TEMPORARY: Return simulated response
simulated_response = {
    "agent_name": subagent_type,
    "overall_score": round(random.uniform(7.0, 9.5), 2),
    ...
}
return simulated_response
```

**Required Change (Choose ONE option):**

#### Option A: Anthropic API Direct ⭐ RECOMMENDED
```python
import anthropic

client = anthropic.Anthropic()  # Uses ANTHROPIC_API_KEY env var

# Load agent expertise
agent_path = Path(f".claude/agents/{subagent_type}.md")
with open(agent_path) as f:
    agent_md = f.read()

# Extract content after YAML frontmatter
agent_lines = agent_md.split('\n')
in_fm = False
content_lines = []
for line in agent_lines:
    if line.strip() == '---':
        in_fm = not in_fm
        continue
    if not in_fm:
        content_lines.append(line)

agent_system = '\n'.join(content_lines)

# Call Claude API
response = client.messages.create(
    model="claude-sonnet-4-5-20250929",
    max_tokens=4096,
    system=f"{agent_system}\n\nYou are performing an evaluation task.",
    messages=[{"role": "user", "content": prompt}],
    timeout=timeout
)

result_text = response.content[0].text
return extract_json_from_response(result_text)
```

**Test:**
```bash
# Set API key
export ANTHROPIC_API_KEY="your-api-key-here"

# Test single evaluation
python3 << 'EOF'
import asyncio
import sys
sys.path.insert(0, '.')

# Import with direct path
import importlib.util
spec = importlib.util.spec_from_file_location("delegation", "evaluation-system/core/claude_task_delegation.py")
delegation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(delegation)

async def test():
    item = {
        "item_id": "test_001",
        "item_type": "mcq",
        "specialty": "cardiology",
        "file_path": "data/mcqs/week1_all_100_unique_mcqs.json",
        "array_index": 0
    }

    result = await delegation.evaluate_item_with_agent_real(
        item=item,
        agent_name="medication-management-expert"
    )

    print(f"✅ Score: {result['overall_score']}/10.0")
    print(f"✅ Status: {result['pass_fail']}")

asyncio.run(test())
EOF
```

**Expected Output:**
```
✅ Score: 8.5/10.0
✅ Status: PASS
```

#### Option B: Subprocess (Alternative)
```python
import subprocess
import tempfile

with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
    f.write(prompt)
    prompt_file = f.name

result = subprocess.run(
    ['claude', '--model', 'sonnet', '--file', prompt_file],
    capture_output=True,
    text=True,
    timeout=timeout
)

os.unlink(prompt_file)
return extract_json_from_response(result.stdout)
```

### Step 2: Update Orchestrator ⏳

**File:** `evaluation-system/core/evaluation_orchestrator.py`
**Line:** ~100 (in `evaluate_item_with_agent()`)

**Current:**
```python
return self._simulate_agent_evaluation(item, agent_name, agent_config)
```

**Change to:**
```python
# Import at top of file
from .claude_task_delegation import evaluate_item_with_agent_real

# In evaluate_item_with_agent():
return await evaluate_item_with_agent_real(item, agent_name)
```

**Test:**
```bash
python3 evaluation-system/core/evaluation_orchestrator.py \
  --max-items 5 \
  --output-dir evaluation-system/reports/real_agent_test_5

# Expected: 5 items evaluated with real agents
# Check reports for realistic scores (not simulation random)
```

### Step 3: Verify JSON Parsing ✅

**Test different response formats:**

```python
# Test 1: Pure JSON
response_1 = '{"agent_name": "test", "overall_score": 8.5}'

# Test 2: Markdown block
response_2 = '''
Here is my evaluation:

```json
{
  "agent_name": "medication-management-expert",
  "overall_score": 8.5,
  "pass_fail": "PASS"
}
```
'''

# Test 3: JSON with text
response_3 = 'The evaluation shows {"agent_name": "test", "score": 9.0}'

# All should parse successfully
from evaluation_system.core.claude_task_delegation import extract_json_from_response
for i, resp in enumerate([response_1, response_2, response_3], 1):
    result = extract_json_from_response(resp)
    print(f"✅ Test {i} parsed: {result}")
```

---

## 🚀 Production Deployment

### Phase 1: Small-Scale Test (1 hour)

```bash
# Test with 10 items
python3 evaluation-system/core/evaluation_orchestrator.py \
  --max-items 10 \
  --batch-size 2 \
  --output-dir evaluation-system/reports/prod_test_10

# Verify:
# - All 10 reports generated
# - Avg score 7.0-9.0 (realistic range)
# - No crashes or JSON parsing errors
# - Violations detected (if any)
```

**Success Criteria:**
- [ ] 10/10 items evaluated successfully
- [ ] 0 JSON parsing errors
- [ ] 0 orchestrator crashes
- [ ] Avg score in realistic range (7.0-9.0)
- [ ] Quality gates trigger appropriately

### Phase 2: Medium-Scale Test (3-4 hours)

```bash
# Test with 100 items
python3 evaluation-system/core/evaluation_orchestrator.py \
  --max-items 100 \
  --batch-size 5 \
  --batch-delay 1 \
  --output-dir evaluation-system/reports/prod_test_100

# Monitor progress, check for issues
```

**Success Criteria:**
- [ ] 100/100 items evaluated successfully
- [ ] <5% error rate
- [ ] Avg score stable across batches
- [ ] No memory leaks (check with `top` or `htop`)

### Phase 3: Full Production Run (6-8 hours)

```bash
# Evaluate all 2,963 pending items
python3 evaluation-system/core/evaluation_orchestrator.py \
  --batch-size 5 \
  --max-parallel-agents 10 \
  --batch-delay 2 \
  --output-dir evaluation-system/reports/production_iteration_1

# Monitor in separate terminal:
watch -n 30 'tail -20 evaluation-system/reports/production_iteration_1/summary.json'
```

**Success Criteria:**
- [ ] 2,963 items evaluated (100% completion)
- [ ] Avg score 7.0-8.0 (iteration 1 baseline)
- [ ] Approval rate 60-75%
- [ ] Critical violations identified (~5-10%)
- [ ] Reports saved for all items

---

## 📊 Post-Evaluation Analysis

### Generate Issue Report

```bash
python3 << 'EOF'
import json
from collections import Counter, defaultdict

# Load all evaluation reports
import glob
reports = []
for report_file in glob.glob('evaluation-system/reports/production_iteration_1/reports/*_evaluation.json'):
    with open(report_file) as f:
        reports.append(json.load(f))

# Analyze
total = len(reports)
scores = [r['overall_score'] for r in reports]
avg_score = sum(scores) / len(scores)
approval_rate = len([s for s in scores if s >= 8.0]) / total * 100

# Violations
all_violations = []
for r in reports:
    for agent_eval in r.get('agent_evaluations', []):
        all_violations.extend(agent_eval.get('violations', []))

violation_counts = Counter(v['issue'] for v in all_violations)

print("=" * 80)
print("ITERATION 1 ANALYSIS")
print("=" * 80)
print(f"Items Evaluated: {total}")
print(f"Avg Score: {avg_score:.2f}/10.0")
print(f"Approval Rate: {approval_rate:.1f}%")
print(f"\nTotal Violations: {len(all_violations)}")
print(f"\nTop 10 Issues:")
for issue, count in violation_counts.most_common(10):
    pct = count / total * 100
    print(f"  {count:4d} ({pct:5.1f}%) - {issue}")

# Save analysis
with open('evaluation-system/reports/production_iteration_1/analysis.json', 'w') as f:
    json.dump({
        'total_items': total,
        'avg_score': avg_score,
        'approval_rate': approval_rate,
        'total_violations': len(all_violations),
        'top_issues': dict(violation_counts.most_common(20))
    }, f, indent=2)

print(f"\n✅ Analysis saved to: production_iteration_1/analysis.json")
EOF
```

---

## 🔄 Iterative Improvement

### Iteration 2: Auto-Fix (Week 4)

**Build Auto-Fix Engine:**

```bash
# File to create: evaluation-system/core/auto_fix_engine.py
# Features:
# 1. Fix Australian drug names (acetaminophen → paracetamol)
# 2. Add missing PBS codes
# 3. Standardize RAG citation format
# 4. Fix dosing units (mg/dL → mmol/L)

# Run auto-fix:
python3 evaluation-system/core/auto_fix_engine.py \
  --reports-dir evaluation-system/reports/production_iteration_1 \
  --output-dir evaluation-system/fixes/iteration_1

# Expected: 70% of issues auto-fixed
```

### Iteration 3: Manual Review (Week 5)

**Manual Review Queue:**

```bash
# Generate review queue
python3 evaluation-system/core/manual_review_queue.py \
  --reports-dir evaluation-system/reports/production_iteration_1 \
  --threshold 7.0 \
  --output manual_review_queue.json

# Expected: ~30% of items (890 items) need manual review
```

### Iteration 4: Re-Evaluation (Week 5-6)

```bash
# Re-evaluate fixed items
python3 evaluation-system/core/evaluation_orchestrator.py \
  --only-fixed-items \
  --output-dir evaluation-system/reports/production_iteration_2

# Expected: Avg score 8.5-9.0, 90-95% approval
```

---

## ✅ Quality Gates

### Before Production Deployment

- [ ] **Code Review**
  - [ ] Task delegation integration reviewed
  - [ ] Error handling verified
  - [ ] Timeout logic tested
  - [ ] JSON parsing robust

- [ ] **Testing**
  - [ ] 10-item test: 100% success
  - [ ] 100-item test: <5% errors
  - [ ] Full run: <2% errors

- [ ] **Performance**
  - [ ] Batch processing: 5 items in <5 minutes
  - [ ] Memory usage: Stable (no leaks)
  - [ ] API rate limits: Respected (batch-delay set)

- [ ] **Quality**
  - [ ] Avg score 7.0-8.0 (iteration 1)
  - [ ] Quality gates triggering correctly
  - [ ] Violations categorized properly

### Before Final Deployment (99% Target)

- [ ] **Iteration 3 Complete**
  - [ ] Avg score ≥9.0
  - [ ] Approval rate ≥95% (target 99%)
  - [ ] Zero critical violations
  - [ ] All manual reviews complete

- [ ] **Documentation**
  - [ ] Master evaluation report generated
  - [ ] Issue resolution log complete
  - [ ] Agent performance analysis done

---

## 📝 Command Reference

### Quick Test Commands

```bash
# Test delegation wrapper
python3 evaluation-system/scripts/quick_test_delegation.sh

# Test orchestrator (10 items)
python3 evaluation-system/core/evaluation_orchestrator.py --max-items 10

# Check registry status
python3 << 'EOF'
import json
r = json.load(open('evaluation-system/data/knowledge_item_registry.json'))
print(f"Total: {len(r['knowledge_items'])}")
print(f"Pending: {len([i for i in r['knowledge_items'] if i['evaluation_status']=='pending'])}")
EOF
```

### Production Commands

```bash
# Full evaluation run
python3 evaluation-system/core/evaluation_orchestrator.py \
  --output-dir evaluation-system/reports/production_iteration_1

# Specific specialty only
python3 evaluation-system/core/evaluation_orchestrator.py \
  --specialty cardiology \
  --output-dir evaluation-system/reports/cardiology_only

# With rate limiting
python3 evaluation-system/core/evaluation_orchestrator.py \
  --batch-delay 5 \
  --output-dir evaluation-system/reports/with_delays
```

---

## 🎯 Success Metrics

### Iteration 1 Targets
- Items evaluated: 2,963 (100%)
- Avg score: 7.0-8.0
- Approval rate: 60-75%
- Critical violations: <10%
- Duration: 6-8 hours

### Final Targets (Iteration 3-4)
- Avg score: ≥9.0
- Approval rate: ≥95% (stretch: 99%)
- Critical violations: 0
- Auto-fix success: ≥70%
- Manual review: <5% of items

---

## 🚨 Troubleshooting

### Common Issues

**Issue 1: JSON Parsing Fails**
```bash
# Check agent response format
cat evaluation-system/reports/test/reports/item_001_evaluation.json | head -50

# Verify extract_json_from_response handles format
python3 -c "from evaluation_system.core.claude_task_delegation import extract_json_from_response; print(extract_json_from_response('```json\n{\"test\": 1}\n```'))"
```

**Issue 2: API Rate Limits**
```bash
# Increase batch delay
python3 evaluation_orchestrator.py --batch-delay 10  # 10 seconds between batches
```

**Issue 3: Memory Issues**
```bash
# Reduce batch size
python3 evaluation_orchestrator.py --batch-size 2  # 2 items at a time
```

---

**Status:** READY FOR PRODUCTION DEPLOYMENT
**Blockers:** 1 (real agent integration)
**ETA to Production:** 2-3 hours (integration) + 6-8 hours (full run) = **8-11 hours total**
