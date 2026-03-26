# Evaluation Execution & Continuous Improvement Strategy

**irStudy Medical Content Evaluation System**
**Version:** 1.0
**Date:** 2026-03-25

---

## 🎯 Executive Summary

This document outlines the **3-phase execution strategy** for evaluating 2,963 knowledge items and the **continuous improvement feedback loop** to iteratively enhance content quality.

**Key Principles:**
1. **Automated Evaluation:** Expert agents review content autonomously
2. **Parallel Processing:** 50 items evaluated simultaneously (5 items × 10 agents)
3. **Quality Gates:** Zero-tolerance for critical violations (Australian standards, safety)
4. **Feedback Loop:** Evaluation insights → Content fixes → Re-evaluation → Deployment
5. **Transparency:** Real-time dashboard tracking progress, scores, issues

---

## 📐 Phase 1: Evaluation Orchestration (Week 3)

### 1.1 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    EVALUATION ORCHESTRATOR                       │
│                                                                  │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐             │
│  │ Queue Mgr  │──▶│ Agent Pool │──▶│ Aggregator │             │
│  └────────────┘   └────────────┘   └────────────┘             │
│         │                │                 │                    │
│         ▼                ▼                 ▼                    │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐             │
│  │  Registry  │   │  Reports   │   │  Dashboard │             │
│  └────────────┘   └────────────┘   └────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Evaluation Workflow

**Step 1: Queue Management**
```python
# Load pending items from registry
pending_items = load_registry()["knowledge_items"]
pending_queue = [item for item in pending_items if item["status"] == "pending"]

# Prioritize by:
# 1. Content type (OSCE scripts first - highest complexity)
# 2. Specialty coverage (complete cardiology before moving to respiratory)
# 3. Dependencies (personas before study cards - may reference same conditions)

prioritized_queue = prioritize_queue(pending_queue)
```

**Step 2: Batch Processing**
```python
BATCH_SIZE = 5  # Evaluate 5 items simultaneously
MAX_PARALLEL_AGENTS = 10  # Each item evaluated by 2-6 agents

for batch in chunked(prioritized_queue, BATCH_SIZE):
    # For each item in batch, delegate to assigned agents in parallel
    for item in batch:
        assigned_agents = item["assigned_agents"]  # e.g., ["medication-management-expert", "radiology-interpretation-expert"]

        # Launch all agents for this item in parallel
        evaluation_results = await asyncio.gather(*[
            evaluate_item_with_agent(item, agent)
            for agent in assigned_agents
        ])

        # Aggregate scores
        aggregated_score = aggregate_scores(evaluation_results)

        # Save evaluation report
        save_evaluation_report(item, evaluation_results, aggregated_score)
```

**Step 3: Agent Evaluation Execution**

Each agent receives:
```markdown
# Evaluation Task for [agent-name]

## Item to Evaluate
- **Type:** patient_persona
- **ID:** persona_cardiology_052_stemi_female_58_persona
- **Specialty:** cardiology
- **File:** clinical-content-prds/validation-system/batch1_personas/cardiology_052_stemi_female_58_persona.json

## Your Expertise
You are: medication-management-expert
Specialization: Australian drug names, PBS compliance, polypharmacy management

## Evaluation Criteria (focus on your domain)
1. **Australian Drug Names** (CRITICAL - zero tolerance)
   - ✅ "paracetamol" (NOT "acetaminophen")
   - ✅ "adrenaline" (NOT "epinephrine")
   - ✅ "salbutamol" (NOT "albuterol")

2. **PBS Compliance**
   - Are medications PBS-listed?
   - Appropriate authority requirements noted?

3. **Dosing Accuracy**
   - Correct doses for Australian practice?
   - Renal/hepatic adjustments considered?

4. **Drug Interactions**
   - Any dangerous interactions identified?

## Scoring Rubric
- **9.0-10.0:** Excellent - deployment ready
- **8.0-8.9:** Good - minor revisions (e.g., add PBS streamline code)
- **7.0-7.9:** Acceptable - moderate revisions (e.g., change dose from BID to TDS)
- **6.0-6.9:** Poor - major revisions (e.g., wrong drug class)
- **0.0-5.9:** Failing - REJECT (e.g., "acetaminophen" used instead of "paracetamol")

## Required Output Format
```json
{
  "agent_name": "medication-management-expert",
  "item_id": "persona_cardiology_052_stemi_female_58_persona",
  "evaluation_date": "2026-03-25T10:30:00Z",
  "overall_score": 8.5,
  "criteria_scores": {
    "australian_drug_names": 10.0,
    "pbs_compliance": 8.0,
    "dosing_accuracy": 9.0,
    "drug_interactions": 7.0
  },
  "violations": [
    {
      "severity": "warning",
      "category": "pbs_compliance",
      "issue": "Atorvastatin 40mg lacks PBS streamline code (recommend: 2362B)",
      "location": "medications[2].pbs_code",
      "suggested_fix": "Add 'pbs_code': '2362B'"
    }
  ],
  "suggestions": [
    "Consider adding renal dosing note for metformin (eGFR <30 contraindicated)"
  ],
  "strengths": [
    "All drug names use Australian terminology (paracetamol, not acetaminophen)",
    "Aspirin dose correct for STEMI (300mg loading, 100mg maintenance)"
  ],
  "pass_fail": "PASS",
  "requires_manual_review": false
}
```
```

### 1.3 Score Aggregation Engine

**Weighted Average Calculation:**
```python
def aggregate_scores(agent_evaluations: List[Dict]) -> Dict:
    """
    Aggregate scores from multiple expert agents.

    Weights:
    - Australian standards: 25%
    - Clinical accuracy: 30%
    - Educational alignment: 20%
    - RAG citation quality: 15%
    - Cultural safety: 10%
    """

    # Map agents to criteria
    agent_to_criteria = {
        "medication-management-expert": ["australian_standards", "clinical_accuracy"],
        "clinical-documentation-expert": ["australian_standards", "educational_alignment"],
        "radiology-interpretation-expert": ["clinical_accuracy"],
        "mental-health-crisis-expert": ["clinical_accuracy", "cultural_safety"],
        # ... (see full mapping in config)
    }

    # Calculate weighted scores per criterion
    criterion_scores = defaultdict(list)
    for eval_result in agent_evaluations:
        agent = eval_result["agent_name"]
        criteria = agent_to_criteria.get(agent, [])

        for criterion in criteria:
            if criterion in eval_result["criteria_scores"]:
                criterion_scores[criterion].append(
                    eval_result["criteria_scores"][criterion]
                )

    # Average scores per criterion
    criterion_averages = {
        criterion: np.mean(scores)
        for criterion, scores in criterion_scores.items()
    }

    # Apply weights
    weights = {
        "australian_standards": 0.25,
        "clinical_accuracy": 0.30,
        "educational_alignment": 0.20,
        "rag_citation_quality": 0.15,
        "cultural_safety": 0.10,
    }

    overall_score = sum(
        criterion_averages.get(criterion, 0.0) * weight
        for criterion, weight in weights.items()
    )

    return {
        "overall_score": round(overall_score, 2),
        "criterion_scores": criterion_averages,
        "agent_evaluations": agent_evaluations,
        "num_agents": len(agent_evaluations),
    }
```

**Zero-Tolerance Quality Gates:**
```python
def check_quality_gates(aggregated_result: Dict) -> Dict:
    """
    Enforce zero-tolerance gates (auto-reject if violated).
    """
    violations = []

    # Gate 1: Australian drug names (CRITICAL)
    for agent_eval in aggregated_result["agent_evaluations"]:
        if agent_eval["agent_name"] == "medication-management-expert":
            for violation in agent_eval.get("violations", []):
                if violation["category"] == "australian_drug_names":
                    violations.append({
                        "gate": "australian_drug_names",
                        "severity": "CRITICAL",
                        "action": "AUTO_REJECT",
                        "issue": violation["issue"],
                    })

    # Gate 2: RAG citation confidence <0.65 (ZERO TOLERANCE)
    for agent_eval in aggregated_result["agent_evaluations"]:
        if "rag_citation_quality" in agent_eval.get("criteria_scores", {}):
            if agent_eval["criteria_scores"]["rag_citation_quality"] < 6.5:
                violations.append({
                    "gate": "rag_citation_quality",
                    "severity": "CRITICAL",
                    "action": "AUTO_REJECT",
                    "issue": "RAG citations below 0.65 confidence threshold",
                })

    # Gate 3: Clinical safety (dangerous medications, wrong doses)
    # ... (similar logic)

    if violations:
        aggregated_result["overall_score"] = 0.0  # Force fail
        aggregated_result["quality_gate_violations"] = violations
        aggregated_result["status"] = "REJECTED"
    else:
        aggregated_result["status"] = "APPROVED" if aggregated_result["overall_score"] >= 8.0 else "NEEDS_REVISION"

    return aggregated_result
```

---

## 🔄 Phase 2: Continuous Improvement Feedback Loop (Weeks 4-6)

### 2.1 Improvement Cycle

```
┌──────────────────────────────────────────────────────────────┐
│                    IMPROVEMENT CYCLE                          │
│                                                               │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐              │
│  │ Evaluate │───▶│  Analyze │───▶│   Fix    │              │
│  └──────────┘    └──────────┘    └──────────┘              │
│       ▲                                  │                   │
│       │                                  ▼                   │
│  ┌──────────┐                     ┌──────────┐              │
│  │ Re-eval  │◀────────────────────│  Deploy  │              │
│  └──────────┘                     └──────────┘              │
└──────────────────────────────────────────────────────────────┘

Cycle Duration: 3-5 days per iteration
Iterations: 3-4 cycles over 2 weeks
```

### 2.2 Issue Analysis & Categorization

**Automated Issue Extraction:**
```python
def analyze_evaluation_results(registry: Dict) -> Dict:
    """
    Analyze all evaluation results to identify patterns.
    """

    # Load all evaluation reports
    reports = load_all_reports()

    # Categorize issues by:
    # 1. Frequency (how many items affected)
    # 2. Severity (critical/warning/suggestion)
    # 3. Category (australian_standards, clinical_accuracy, etc.)
    # 4. Fixability (auto-fixable vs manual review)

    issue_summary = {
        "total_items_evaluated": len(reports),
        "total_violations": 0,
        "by_severity": defaultdict(int),
        "by_category": defaultdict(int),
        "by_fixability": defaultdict(int),
        "top_issues": [],
    }

    all_violations = []
    for report in reports:
        for agent_eval in report["agent_evaluations"]:
            for violation in agent_eval.get("violations", []):
                all_violations.append(violation)
                issue_summary["total_violations"] += 1
                issue_summary["by_severity"][violation["severity"]] += 1
                issue_summary["by_category"][violation["category"]] += 1

    # Identify top issues by frequency
    violation_counts = Counter([v["issue"] for v in all_violations])
    issue_summary["top_issues"] = [
        {"issue": issue, "count": count, "percentage": count / len(reports) * 100}
        for issue, count in violation_counts.most_common(20)
    ]

    return issue_summary
```

**Example Output:**
```json
{
  "total_items_evaluated": 2963,
  "total_violations": 4521,
  "by_severity": {
    "critical": 234,
    "warning": 1876,
    "suggestion": 2411
  },
  "by_category": {
    "australian_drug_names": 234,
    "pbs_compliance": 567,
    "rag_citation_quality": 123,
    "clinical_accuracy": 89
  },
  "top_issues": [
    {
      "issue": "Missing PBS streamline code",
      "count": 567,
      "percentage": 19.1,
      "auto_fixable": true
    },
    {
      "issue": "Acetaminophen used instead of paracetamol",
      "count": 234,
      "percentage": 7.9,
      "auto_fixable": true
    },
    {
      "issue": "RAG citation confidence <0.65",
      "count": 123,
      "percentage": 4.2,
      "auto_fixable": false
    }
  ]
}
```

### 2.3 Auto-Fix Engine

**Automated Corrections for Common Issues:**

```python
class AutoFixEngine:
    """
    Automatically fix common violations that don't require human judgment.
    """

    def __init__(self):
        self.fix_rules = {
            "australian_drug_names": self.fix_drug_names,
            "pbs_codes": self.fix_pbs_codes,
            "citation_format": self.fix_citation_format,
        }

        # Australian drug name mappings
        self.drug_name_map = {
            "acetaminophen": "paracetamol",
            "epinephrine": "adrenaline",
            "albuterol": "salbutamol",
            "lidocaine": "lignocaine",
            # ... (100+ mappings)
        }

        # PBS code database
        self.pbs_codes = load_pbs_database()

    def fix_drug_names(self, item: Dict, violations: List[Dict]) -> Dict:
        """Auto-fix American drug names to Australian."""
        content = item["content"]

        for violation in violations:
            if violation["category"] == "australian_drug_names":
                # Extract American drug name from violation
                american_name = extract_drug_name(violation["issue"])
                australian_name = self.drug_name_map.get(american_name.lower())

                if australian_name:
                    # Replace in JSON content
                    content = replace_drug_name(content, american_name, australian_name)

                    log_fix({
                        "item_id": item["item_id"],
                        "fix_type": "australian_drug_name",
                        "old_value": american_name,
                        "new_value": australian_name,
                        "location": violation["location"],
                    })

        return content

    def fix_pbs_codes(self, item: Dict, violations: List[Dict]) -> Dict:
        """Auto-add missing PBS codes."""
        content = item["content"]

        for violation in violations:
            if "Missing PBS" in violation["issue"]:
                # Extract medication name
                med_name = extract_medication(violation["location"])

                # Lookup PBS code
                pbs_code = self.pbs_codes.lookup(med_name)

                if pbs_code:
                    # Add PBS code to JSON
                    content = add_pbs_code(content, violation["location"], pbs_code)

                    log_fix({
                        "item_id": item["item_id"],
                        "fix_type": "pbs_code_addition",
                        "medication": med_name,
                        "pbs_code": pbs_code,
                    })

        return content

    def apply_fixes(self, item: Dict, evaluation_report: Dict) -> Dict:
        """Apply all auto-fixes to an item."""
        all_violations = []
        for agent_eval in evaluation_report["agent_evaluations"]:
            all_violations.extend(agent_eval.get("violations", []))

        # Group violations by category
        violations_by_category = defaultdict(list)
        for v in all_violations:
            violations_by_category[v["category"]].append(v)

        # Apply fixes
        fixed_content = item["content"]
        fixes_applied = []

        for category, violations in violations_by_category.items():
            if category in self.fix_rules:
                fixed_content = self.fix_rules[category](item, violations)
                fixes_applied.append(category)

        return {
            "original_content": item["content"],
            "fixed_content": fixed_content,
            "fixes_applied": fixes_applied,
            "num_fixes": len(fixes_applied),
        }
```

### 2.4 Manual Review Queue

**Items Requiring Human Review:**

```python
def create_manual_review_queue(evaluation_reports: List[Dict]) -> List[Dict]:
    """
    Identify items that need manual review (can't be auto-fixed).
    """

    manual_review_queue = []

    for report in evaluation_reports:
        # Flag for manual review if:
        # 1. Overall score <7.0 (poor/failing)
        # 2. Any critical violation that can't be auto-fixed
        # 3. Conflicting agent opinions (one says 9.0, another says 4.0)
        # 4. RAG citation issues (hallucinations)

        requires_review = (
            report["overall_score"] < 7.0 or
            has_unfixable_critical_violations(report) or
            has_agent_disagreement(report) or
            has_rag_citation_issues(report)
        )

        if requires_review:
            manual_review_queue.append({
                "item_id": report["item_id"],
                "overall_score": report["overall_score"],
                "reason_for_review": get_review_reason(report),
                "priority": calculate_priority(report),
                "assigned_reviewer": "clinical-content-specialist",
            })

    # Sort by priority (critical violations first)
    manual_review_queue.sort(key=lambda x: x["priority"], reverse=True)

    return manual_review_queue
```

### 2.5 Re-Evaluation Trigger

**When to Re-Evaluate:**

```python
def should_reevaluate(item: Dict) -> bool:
    """
    Determine if item should be re-evaluated after fixes.
    """

    # Re-evaluate if:
    # 1. Auto-fixes applied
    # 2. Manual corrections made
    # 3. File hash changed (content updated)
    # 4. Original score <8.0 (needs improvement)

    return (
        item.get("fixes_applied", []) or
        item.get("manually_corrected", False) or
        item["current_hash"] != item["original_hash"] or
        item.get("last_evaluation_score", 0.0) < 8.0
    )

def reevaluation_workflow():
    """
    Re-evaluate fixed items to verify improvements.
    """

    # Load items with fixes
    fixed_items = load_fixed_items()

    # Filter items needing re-evaluation
    reevaluation_queue = [item for item in fixed_items if should_reevaluate(item)]

    print(f"📊 Re-evaluation Queue: {len(reevaluation_queue)} items")

    # Run evaluation again (same process as initial evaluation)
    for item in reevaluation_queue:
        new_evaluation = evaluate_item(item)

        # Compare scores
        improvement = new_evaluation["overall_score"] - item.get("last_evaluation_score", 0.0)

        log_improvement({
            "item_id": item["item_id"],
            "old_score": item.get("last_evaluation_score"),
            "new_score": new_evaluation["overall_score"],
            "improvement": improvement,
            "fixes_applied": item.get("fixes_applied", []),
        })

        # Update registry
        update_registry(item["item_id"], new_evaluation)
```

---

## 📊 Phase 3: Tracking Dashboard (Week 4)

### 3.1 Dashboard Components

**Real-Time Progress Tracking:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>irStudy Evaluation Dashboard</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        .metric-card {
            border: 2px solid #ccc;
            padding: 20px;
            margin: 10px;
            border-radius: 8px;
        }
        .critical { background-color: #ffcccc; }
        .warning { background-color: #fff4cc; }
        .success { background-color: #ccffcc; }
    </style>
</head>
<body>
    <h1>🏥 irStudy Medical Content Evaluation Dashboard</h1>

    <!-- Overall Progress -->
    <div class="metric-card">
        <h2>📊 Overall Progress</h2>
        <p><strong>Total Items:</strong> 3,170</p>
        <p><strong>Evaluated:</strong> <span id="evaluated">1,245</span> (39.3%)</p>
        <p><strong>Approved (≥8.0):</strong> <span id="approved">982</span> (78.9%)</p>
        <p><strong>Needs Revision:</strong> <span id="needs_revision">234</span> (18.8%)</p>
        <p><strong>Rejected:</strong> <span id="rejected">29</span> (2.3%)</p>

        <div id="progress-bar"></div>
    </div>

    <!-- Quality Gates -->
    <div class="metric-card critical">
        <h2>🚨 Critical Violations (Zero Tolerance)</h2>
        <p><strong>Australian Drug Name Errors:</strong> <span id="drug-errors">29</span></p>
        <p><strong>RAG Citation Issues:</strong> <span id="rag-errors">15</span></p>
        <p><strong>Clinical Safety Concerns:</strong> <span id="safety-errors">5</span></p>
    </div>

    <!-- Agent Performance -->
    <div class="metric-card">
        <h2>👥 Agent Performance</h2>
        <table>
            <tr>
                <th>Agent</th>
                <th>Items Evaluated</th>
                <th>Avg Score</th>
                <th>Critical Violations Found</th>
            </tr>
            <tr>
                <td>medication-management-expert</td>
                <td>1,245</td>
                <td>8.3</td>
                <td>29</td>
            </tr>
            <tr>
                <td>radiology-interpretation-expert</td>
                <td>1,102</td>
                <td>8.7</td>
                <td>3</td>
            </tr>
            <!-- ... -->
        </table>
    </div>

    <!-- Specialty Heatmap -->
    <div class="metric-card">
        <h2>🗺️ Specialty Quality Heatmap</h2>
        <div id="specialty-heatmap"></div>
    </div>

    <!-- Issue Trends -->
    <div class="metric-card">
        <h2>📈 Issue Resolution Trends</h2>
        <div id="issue-trends"></div>
    </div>

    <script>
        // Update dashboard every 30 seconds
        setInterval(updateDashboard, 30000);

        function updateDashboard() {
            fetch('/api/evaluation-stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('evaluated').textContent = data.evaluated;
                    document.getElementById('approved').textContent = data.approved;
                    // ... update all metrics
                });
        }
    </script>
</body>
</html>
```

### 3.2 Dashboard Metrics

**Key Performance Indicators (KPIs):**

1. **Evaluation Velocity**
   - Items evaluated per hour
   - Projected completion date
   - Bottleneck identification (which agents are slowest?)

2. **Quality Metrics**
   - Average score by content type
   - Average score by specialty
   - Distribution of scores (histogram)

3. **Issue Tracking**
   - Top 10 most frequent issues
   - Issue resolution rate (% fixed in each iteration)
   - Time to fix (from detection to resolution)

4. **Agent Insights**
   - Inter-agent agreement (do agents give similar scores?)
   - Agent strictness (which agents are most critical?)
   - Agent coverage (which specialties lack expert coverage?)

5. **Improvement Trends**
   - Score improvement after fixes (before vs after)
   - Auto-fix success rate (% of issues fixed automatically)
   - Manual review queue size (trending up or down?)

---

## 🛠️ Implementation Roadmap

### Week 3: Evaluation Orchestrator
- [x] Queue management system
- [x] Parallel agent delegation
- [x] Score aggregation engine
- [x] Evaluation report generator
- [x] Quality gate enforcement

### Week 4: Feedback Loop & Dashboard
- [ ] Issue analysis engine
- [ ] Auto-fix engine (drug names, PBS codes)
- [ ] Manual review queue
- [ ] Re-evaluation workflow
- [ ] Real-time dashboard (HTML + API)

### Week 5-6: Full Evaluation Run
- [ ] Evaluate all 2,963 pending items
- [ ] Apply auto-fixes (expect 60-70% auto-fixable)
- [ ] Manual review queue processing (expect 30-40% manual)
- [ ] Re-evaluate fixed items (aim for 95%+ approval rate)
- [ ] Generate master evaluation report

---

## 📏 Success Criteria

**Quantitative Targets:**
- ✅ **95%+ approval rate** (overall score ≥8.0) after iteration 2
- ✅ **Zero critical violations** (Australian drug names, RAG citations, safety)
- ✅ **<5% manual review queue** by Week 6
- ✅ **70%+ auto-fix rate** for common issues
- ✅ **<1 hour** average time-to-fix per item

**Qualitative Targets:**
- ✅ **Australian compliance** - 100% use of paracetamol, adrenaline, salbutamol
- ✅ **Clinical safety** - No dangerous medication errors or dosing mistakes
- ✅ **Educational alignment** - AMC Clinical Exam blueprint coverage verified
- ✅ **Cultural safety** - Aboriginal/TSI, LGBTQIA+, CALD representation reviewed

---

## 🔐 Quality Assurance

### Validation at Each Stage

**Stage 1: Agent Evaluation**
- Each agent validates against their domain expertise
- Output format validated (JSON schema)
- Score ranges validated (0.0-10.0)

**Stage 2: Score Aggregation**
- Weighted averages calculated correctly
- Quality gates enforced
- Outlier detection (flag if one agent scores 9.0, another 3.0)

**Stage 3: Auto-Fix**
- Fixes applied only to designated locations
- Original content backed up
- Fix log maintained for audit trail

**Stage 4: Re-Evaluation**
- Verify score improvement after fixes
- Ensure no regressions (new score ≥ old score)
- Flag items that don't improve after fixes

---

## 📝 Deliverables

### Code Deliverables
1. `evaluation-system/core/evaluation_orchestrator.py` (500+ lines)
2. `evaluation-system/core/score_aggregator.py` (200+ lines)
3. `evaluation-system/core/auto_fix_engine.py` (400+ lines)
4. `evaluation-system/core/issue_analyzer.py` (300+ lines)
5. `evaluation-system/dashboard/index.html` (dashboard UI)
6. `evaluation-system/dashboard/api.py` (Flask API for dashboard)

### Report Deliverables
1. **Per-Item Evaluation Reports** (2,963 JSON files)
2. **Iteration Summary Reports** (3-4 iterations)
3. **Master Evaluation Report** (final summary)
4. **Issue Resolution Log** (audit trail)
5. **Agent Performance Report** (inter-agent agreement analysis)

---

**Status:** Ready to implement Week 3 (Evaluation Orchestrator)
**Next Action:** Create `evaluation_orchestrator.py` with queue management and parallel agent delegation
