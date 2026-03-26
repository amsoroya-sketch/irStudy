#!/usr/bin/env python3
"""
Results Analysis Script
Generates comprehensive HTML report from evaluation results.

Features:
- Score distribution charts
- Approval rate by specialty
- Top violations analysis
- Agent performance metrics
- Improvement trajectory
- Manual review queue generation

Usage:
    python3 analyze_results.py \
        --input evaluation-system/reports/production_iteration_1/summary.json \
        --output evaluation-system/reports/analysis_iteration_1.html
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict, Counter
from datetime import datetime


def load_evaluation_summary(summary_path: Path) -> Dict[str, Any]:
    """Load evaluation summary JSON."""
    with open(summary_path) as f:
        return json.load(f)


def load_all_evaluations(evaluations_dir: Path) -> List[Dict[str, Any]]:
    """Load all individual evaluation reports."""
    evaluations = []

    for eval_file in evaluations_dir.glob("*.json"):
        with open(eval_file) as f:
            evaluations.append(json.load(f))

    return evaluations


def analyze_score_distribution(evaluations: List[Dict]) -> Dict[str, Any]:
    """Analyze score distribution."""
    scores = [e.get("overall_score", 0) for e in evaluations]

    # Score bins: 0-5, 5-7, 7-8.5, 8.5-9.5, 9.5-10
    bins = {
        "0-5 (Poor)": 0,
        "5-7 (Below Average)": 0,
        "7-8.5 (Average)": 0,
        "8.5-9.5 (Good)": 0,
        "9.5-10 (Excellent)": 0,
    }

    for score in scores:
        if score < 5:
            bins["0-5 (Poor)"] += 1
        elif score < 7:
            bins["5-7 (Below Average)"] += 1
        elif score < 8.5:
            bins["7-8.5 (Average)"] += 1
        elif score < 9.5:
            bins["8.5-9.5 (Good)"] += 1
        else:
            bins["9.5-10 (Excellent)"] += 1

    return {
        "bins": bins,
        "avg_score": sum(scores) / len(scores) if scores else 0,
        "min_score": min(scores) if scores else 0,
        "max_score": max(scores) if scores else 0,
        "total_items": len(scores)
    }


def analyze_violations(evaluations: List[Dict]) -> Dict[str, Any]:
    """Analyze violation patterns."""
    all_violations = []
    critical_violations = []

    for evaluation in evaluations:
        violations = evaluation.get("violations", [])

        for violation in violations:
            violation_type = violation.get("type", "Unknown")
            severity = violation.get("severity", "medium")

            all_violations.append(violation_type)

            if severity == "critical":
                critical_violations.append(violation_type)

    # Count violations
    violation_counts = Counter(all_violations)
    critical_counts = Counter(critical_violations)

    return {
        "total_violations": len(all_violations),
        "unique_violation_types": len(violation_counts),
        "top_10_violations": violation_counts.most_common(10),
        "critical_violations": len(critical_violations),
        "top_critical_violations": critical_counts.most_common(5)
    }


def analyze_by_specialty(evaluations: List[Dict]) -> Dict[str, Any]:
    """Analyze scores by medical specialty."""
    specialty_scores = defaultdict(list)

    for evaluation in evaluations:
        specialty = evaluation.get("specialty", "Unknown")
        score = evaluation.get("overall_score", 0)
        specialty_scores[specialty].append(score)

    specialty_stats = {}

    for specialty, scores in specialty_scores.items():
        specialty_stats[specialty] = {
            "count": len(scores),
            "avg_score": sum(scores) / len(scores),
            "min_score": min(scores),
            "max_score": max(scores),
            "approval_rate": sum(1 for s in scores if s >= 8.5) / len(scores) * 100
        }

    return specialty_stats


def analyze_agent_performance(evaluations: List[Dict]) -> Dict[str, Any]:
    """Analyze individual agent performance."""
    agent_scores = defaultdict(list)

    for evaluation in evaluations:
        # Check if evaluation has agent breakdown
        agent_evaluations = evaluation.get("agent_evaluations", [])

        for agent_eval in agent_evaluations:
            agent_name = agent_eval.get("agent_name", "Unknown")
            score = agent_eval.get("overall_score", 0)
            agent_scores[agent_name].append(score)

    agent_stats = {}

    for agent_name, scores in agent_scores.items():
        agent_stats[agent_name] = {
            "evaluations_count": len(scores),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "max_score": max(scores) if scores else 0,
        }

    return agent_stats


def generate_manual_review_queue(evaluations: List[Dict], threshold: float = 8.5) -> List[Dict]:
    """Generate list of items requiring manual review."""
    review_queue = []

    for evaluation in evaluations:
        score = evaluation.get("overall_score", 0)
        item_id = evaluation.get("item_id", "Unknown")
        violations = evaluation.get("violations", [])

        # Add to review queue if:
        # 1. Score below threshold
        # 2. Has critical violations
        # 3. Requires manual review flag set

        needs_review = (
            score < threshold or
            any(v.get("severity") == "critical" for v in violations) or
            evaluation.get("requires_manual_review", False)
        )

        if needs_review:
            review_queue.append({
                "item_id": item_id,
                "item_type": evaluation.get("item_type", "Unknown"),
                "specialty": evaluation.get("specialty", "Unknown"),
                "score": score,
                "violations_count": len(violations),
                "critical_violations": sum(1 for v in violations if v.get("severity") == "critical"),
                "file_path": evaluation.get("file_path", ""),
            })

    # Sort by score (lowest first)
    review_queue.sort(key=lambda x: x["score"])

    return review_queue


def generate_html_report(
    summary: Dict[str, Any],
    score_dist: Dict[str, Any],
    violations: Dict[str, Any],
    specialty_stats: Dict[str, Any],
    agent_performance: Dict[str, Any],
    review_queue: List[Dict]
) -> str:
    """Generate HTML report."""

    html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Evaluation Results Analysis</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            max-width: 1200px;
            margin: 40px auto;
            padding: 0 20px;
            background: #f5f5f5;
        }}

        h1, h2, h3 {{
            color: #333;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}

        .header h1 {{
            margin: 0;
            color: white;
        }}

        .header p {{
            margin: 10px 0 0 0;
            opacity: 0.9;
        }}

        .section {{
            background: white;
            padding: 30px;
            margin-bottom: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .metric {{
            display: inline-block;
            margin: 10px 20px 10px 0;
        }}

        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}

        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}

        .score-good {{ color: #10b981; }}
        .score-average {{ color: #f59e0b; }}
        .score-poor {{ color: #ef4444; }}

        table {{
            width: 100%;
            border-collapse: collapse;
        }}

        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}

        th {{
            background: #f9fafb;
            font-weight: 600;
            color: #374151;
        }}

        tr:hover {{
            background: #f9fafb;
        }}

        .progress-bar {{
            width: 100%;
            height: 30px;
            background: #e5e7eb;
            border-radius: 5px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981 0%, #059669 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
        }}

        .chart-bar {{
            display: flex;
            align-items: center;
            margin: 10px 0;
        }}

        .chart-label {{
            width: 150px;
            font-size: 14px;
            color: #374151;
        }}

        .chart-bar-fill {{
            height: 25px;
            background: #667eea;
            border-radius: 3px;
            margin-left: 10px;
            position: relative;
        }}

        .chart-value {{
            position: absolute;
            right: 10px;
            color: white;
            font-size: 12px;
            line-height: 25px;
            font-weight: bold;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}

        .badge-critical {{ background: #fee2e2; color: #991b1b; }}
        .badge-warning {{ background: #fef3c7; color: #92400e; }}
        .badge-info {{ background: #dbeafe; color: #1e40af; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Evaluation Results Analysis</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>

    <div class="section">
        <h2>📈 Overall Statistics</h2>

        <div class="metric">
            <div class="metric-label">Total Items</div>
            <div class="metric-value">{score_dist['total_items']}</div>
        </div>

        <div class="metric">
            <div class="metric-label">Average Score</div>
            <div class="metric-value {'score-good' if score_dist['avg_score'] >= 8.5 else 'score-average' if score_dist['avg_score'] >= 7 else 'score-poor'}">{score_dist['avg_score']:.1f}/10.0</div>
        </div>

        <div class="metric">
            <div class="metric-label">Approval Rate</div>
            <div class="metric-value">{summary.get('statistics', {}).get('approval_rate', 0):.1f}%</div>
        </div>

        <div class="metric">
            <div class="metric-label">Critical Violations</div>
            <div class="metric-value score-poor">{violations['critical_violations']}</div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" style="width: {summary.get('statistics', {}).get('approval_rate', 0)}%">
                {summary.get('statistics', {}).get('approval_rate', 0):.1f}% Approved
            </div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Score Distribution</h2>

        {''.join([
            f'''<div class="chart-bar">
                <div class="chart-label">{label}</div>
                <div class="chart-bar-fill" style="width: {(count / score_dist['total_items'] * 300) if score_dist['total_items'] > 0 else 0}px">
                    <span class="chart-value">{count}</span>
                </div>
            </div>'''
            for label, count in score_dist['bins'].items()
        ])}
    </div>

    <div class="section">
        <h2>⚠️ Top Violations</h2>

        <table>
            <thead>
                <tr>
                    <th>Violation Type</th>
                    <th>Count</th>
                    <th>Severity</th>
                </tr>
            </thead>
            <tbody>
                {''.join([
                    f'''<tr>
                        <td>{vtype}</td>
                        <td>{count}</td>
                        <td><span class="badge badge-{'critical' if vtype in [v[0] for v in violations['top_critical_violations']] else 'warning'}">
                            {'CRITICAL' if vtype in [v[0] for v in violations['top_critical_violations']] else 'Warning'}
                        </span></td>
                    </tr>'''
                    for vtype, count in violations['top_10_violations']
                ])}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>🏥 Performance by Specialty</h2>

        <table>
            <thead>
                <tr>
                    <th>Specialty</th>
                    <th>Items</th>
                    <th>Avg Score</th>
                    <th>Approval Rate</th>
                </tr>
            </thead>
            <tbody>
                {''.join([
                    f'''<tr>
                        <td>{specialty}</td>
                        <td>{stats['count']}</td>
                        <td class="{'score-good' if stats['avg_score'] >= 8.5 else 'score-average' if stats['avg_score'] >= 7 else 'score-poor'}">{stats['avg_score']:.1f}/10.0</td>
                        <td>{stats['approval_rate']:.1f}%</td>
                    </tr>'''
                    for specialty, stats in sorted(specialty_stats.items(), key=lambda x: x[1]['avg_score'], reverse=True)
                ])}
            </tbody>
        </table>
    </div>

    <div class="section">
        <h2>📋 Manual Review Queue ({len(review_queue)} items)</h2>

        <p>Items requiring manual review (score &lt; 8.5 or critical violations):</p>

        <table>
            <thead>
                <tr>
                    <th>Item ID</th>
                    <th>Type</th>
                    <th>Specialty</th>
                    <th>Score</th>
                    <th>Violations</th>
                </tr>
            </thead>
            <tbody>
                {''.join([
                    f'''<tr>
                        <td>{item['item_id']}</td>
                        <td>{item['item_type']}</td>
                        <td>{item['specialty']}</td>
                        <td class="{'score-good' if item['score'] >= 8.5 else 'score-average' if item['score'] >= 7 else 'score-poor'}">{item['score']:.1f}/10.0</td>
                        <td>{item['violations_count']} <span class="badge badge-critical">{item['critical_violations']} critical</span></td>
                    </tr>'''
                    for item in review_queue[:50]  # Show first 50
                ])}
            </tbody>
        </table>

        {f'<p><em>Showing first 50 of {len(review_queue)} items. Full list saved to review_queue.json</em></p>' if len(review_queue) > 50 else ''}
    </div>

    <div class="section">
        <h2>🎯 Next Steps</h2>

        <ol>
            <li><strong>Auto-Fix Engine</strong>: Run automated fixes on {len(review_queue)} flagged items
                <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;">venv/bin/python3 evaluation-system/core/auto_fix_engine.py \\
  --input evaluation-system/reports/production_iteration_1 \\
  --output evaluation-system/reports/auto_fixed_batch_1</pre>
            </li>

            <li><strong>Re-Evaluation</strong>: Re-evaluate fixed items (Iteration 2)
                <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;">venv/bin/python3 evaluation-system/core/evaluation_orchestrator.py \\
  --output-dir evaluation-system/reports/production_iteration_2</pre>
            </li>

            <li><strong>Manual Review</strong>: Review items that couldn't be auto-fixed (30%)
                <pre style="background: #f3f4f6; padding: 15px; border-radius: 5px; overflow-x: auto;">venv/bin/python3 evaluation-system/scripts/review_dashboard.py --port 5000</pre>
            </li>
        </ol>
    </div>
</body>
</html>
"""

    return html


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Analyze evaluation results")
    parser.add_argument(
        "--input",
        required=True,
        help="Path to summary.json file"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output HTML file path"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=8.5,
        help="Score threshold for manual review queue (default: 8.5)"
    )

    args = parser.parse_args()

    summary_path = Path(args.input)
    output_path = Path(args.output)

    if not summary_path.exists():
        print(f"❌ Summary file not found: {summary_path}")
        return 1

    print("=" * 80)
    print("RESULTS ANALYSIS - Medical Content Evaluation System")
    print("=" * 80)
    print()

    # Load summary
    print("Loading evaluation summary...")
    summary = load_evaluation_summary(summary_path)

    # Load all evaluations
    evaluations_dir = summary_path.parent / "evaluations"

    if evaluations_dir.exists():
        print(f"Loading {summary.get('statistics', {}).get('evaluated', 0)} evaluation reports...")
        evaluations = load_all_evaluations(evaluations_dir)
    else:
        print("⚠️  Evaluations directory not found. Using summary only.")
        evaluations = []

    # Analyze
    print("Analyzing score distribution...")
    score_dist = analyze_score_distribution(evaluations) if evaluations else {}

    print("Analyzing violations...")
    violations = analyze_violations(evaluations) if evaluations else {}

    print("Analyzing by specialty...")
    specialty_stats = analyze_by_specialty(evaluations) if evaluations else {}

    print("Analyzing agent performance...")
    agent_performance = analyze_agent_performance(evaluations) if evaluations else {}

    print(f"Generating manual review queue (threshold: {args.threshold})...")
    review_queue = generate_manual_review_queue(evaluations, args.threshold) if evaluations else []

    # Save review queue
    if review_queue:
        review_queue_path = output_path.parent / "manual_review_queue.json"
        with open(review_queue_path, 'w') as f:
            json.dump(review_queue, f, indent=2)
        print(f"✅ Manual review queue saved: {review_queue_path}")

    # Generate HTML
    print("Generating HTML report...")
    html = generate_html_report(
        summary,
        score_dist,
        violations,
        specialty_stats,
        agent_performance,
        review_queue
    )

    # Save HTML
    with open(output_path, 'w') as f:
        f.write(html)

    print(f"✅ HTML report generated: {output_path}")
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    if evaluations:
        print(f"Total items: {score_dist.get('total_items', 0)}")
        print(f"Average score: {score_dist.get('avg_score', 0):.1f}/10.0")
        print(f"Approval rate: {summary.get('statistics', {}).get('approval_rate', 0):.1f}%")
        print(f"Manual review queue: {len(review_queue)} items")
        print()

    print(f"Open report: {output_path}")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
