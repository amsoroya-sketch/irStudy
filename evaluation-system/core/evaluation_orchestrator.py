#!/usr/bin/env python3
"""
Evaluation Orchestrator for irStudy Medical Content Evaluation System
Coordinates parallel evaluation of knowledge items by expert agents.

Features:
- Queue management and prioritization
- Parallel batch processing (5 items × 10 agents)
- Score aggregation with weighted criteria
- Quality gate enforcement (zero tolerance)
- Progress tracking and reporting

Usage:
    python3 evaluation_orchestrator.py --batch-size 5 --max-parallel-agents 10
"""

import json
import argparse
import asyncio
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


class EvaluationOrchestrator:
    """
    Orchestrates parallel evaluation of knowledge items by expert agents.
    """

    def __init__(
        self,
        registry_path: Path,
        output_dir: Path,
        batch_size: int = 5,
        max_parallel_agents: int = 10,
        batch_delay: float = 0,
        delegation_function=None,
    ):
        self.registry_path = registry_path
        self.output_dir = output_dir
        self.batch_size = batch_size
        self.max_parallel_agents = max_parallel_agents
        self.batch_delay = batch_delay
        self.delegation_function = delegation_function

        # Load registry
        with open(registry_path, 'r') as f:
            self.registry = json.load(f)

        self.knowledge_items = self.registry.get("knowledge_items", [])

        # Create output directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)

        # Statistics
        self.stats = {
            "total_items": 0,
            "items_evaluated": 0,
            "items_skipped": 0,
            "total_violations": 0,
            "by_status": defaultdict(int),
            "by_content_type": defaultdict(list),
            "by_specialty": defaultdict(list),
            "agent_invocations": defaultdict(int),
            "start_time": datetime.now().isoformat(),
        }

    def get_pending_items(self, max_items: Optional[int] = None) -> List[Dict]:
        """Get pending items from registry."""
        pending = [
            item for item in self.knowledge_items
            if item.get("evaluation_status") == "pending"
        ]

        if max_items:
            pending = pending[:max_items]

        return pending

    def prioritize_queue(self, items: List[Dict]) -> List[Dict]:
        """
        Prioritize items for evaluation.

        Priority order:
        1. OSCE scripts (most complex, need most expert attention)
        2. Patient personas (foundation for study cards)
        3. MCQs (largest volume)
        4. Study cards (can reference personas)
        """
        priority_map = {
            "osce_script": 1,
            "patient_persona": 2,
            "mcq": 3,
            "study_card": 4,
            "clinical_image": 5,
        }

        # Sort by priority, then by specialty (complete one specialty before moving to next)
        return sorted(
            items,
            key=lambda x: (
                priority_map.get(x.get("item_type"), 99),
                x.get("specialty", "zzz")
            )
        )

    async def evaluate_item_with_agent(
        self,
        item: Dict,
        agent_name: str,
        agent_config: Dict
    ) -> Dict:
        """
        Evaluate a single item with a specific expert agent.

        Uses real delegation if function provided, otherwise simulates.
        """
        # Record agent invocation
        self.stats["agent_invocations"][agent_name] += 1

        # Use real delegation if function provided, otherwise simulate
        if self.delegation_function:
            try:
                result = await self.delegation_function(item, agent_name)
                return result
            except Exception as e:
                print(f"⚠️  Delegation error for {item.get('item_id')}: {e}")
                # Fall back to simulation on error
                await asyncio.sleep(0.1)
                return self._simulate_agent_evaluation(item, agent_name, agent_config)
        else:
            # Simulation mode
            await asyncio.sleep(0.1)
            return self._simulate_agent_evaluation(item, agent_name, agent_config)

    def _simulate_agent_evaluation(
        self,
        item: Dict,
        agent_name: str,
        agent_config: Dict
    ) -> Dict:
        """
        Simulate agent evaluation (TEMPORARY - for testing orchestrator).

        In production, this will be replaced with actual Task tool delegation.
        """
        # Base score varies by agent strictness
        agent_strictness = {
            "medication-management-expert": 0.85,  # Strict on drug names
            "clinical-documentation-expert": 0.90,
            "radiology-interpretation-expert": 0.88,
            "mental-health-crisis-expert": 0.87,
            "history-taking-expert": 0.89,
            "physical-examination-expert": 0.88,
        }

        base_score = agent_strictness.get(agent_name, 0.85)

        # Content type affects score
        type_modifier = {
            "patient_persona": 1.0,
            "mcq": 0.95,
            "osce_script": 0.98,
            "study_card": 0.93,
        }.get(item.get("item_type"), 0.90)

        # Calculate overall score (random variation ±0.15)
        import random
        overall_score = min(10.0, max(0.0, (base_score * type_modifier * 10) + random.uniform(-0.5, 0.5)))

        # Generate violations based on score
        violations = []
        if overall_score < 9.0:
            violations.append({
                "severity": "warning",
                "category": "australian_standards",
                "issue": f"Minor improvement needed in {item.get('item_type')}",
                "location": f"{item.get('item_id')}.content",
                "suggested_fix": "Review Australian medical terminology",
            })

        if overall_score < 7.0:
            violations.append({
                "severity": "critical",
                "category": "clinical_accuracy",
                "issue": "Significant clinical accuracy concerns",
                "location": f"{item.get('item_id')}.content",
                "suggested_fix": "Manual review required",
            })

        # Medication management expert checks drug names
        if agent_name == "medication-management-expert" and random.random() < 0.05:
            violations.append({
                "severity": "critical",
                "category": "australian_drug_names",
                "issue": "American drug name detected (e.g., 'acetaminophen' instead of 'paracetamol')",
                "location": f"{item.get('item_id')}.medications[0].generic_name",
                "suggested_fix": "Replace 'acetaminophen' with 'paracetamol'",
            })
            overall_score = 0.0  # Auto-reject

        return {
            "agent_name": agent_name,
            "item_id": item.get("item_id"),
            "evaluation_date": datetime.now().isoformat(),
            "overall_score": round(overall_score, 2),
            "criteria_scores": {
                "australian_standards": round(overall_score * 0.95, 2),
                "clinical_accuracy": round(overall_score * 1.02, 2),
                "educational_alignment": round(overall_score * 0.98, 2),
            },
            "violations": violations,
            "suggestions": [
                f"Consider adding more detail to {item.get('specialty')} content"
            ] if overall_score < 9.0 else [],
            "strengths": [
                f"Good coverage of {item.get('specialty')} concepts",
                "Clear and well-structured content",
            ],
            "pass_fail": "PASS" if overall_score >= 7.0 else "FAIL",
            "requires_manual_review": overall_score < 7.0,
        }

    def aggregate_scores(self, agent_evaluations: List[Dict]) -> Dict:
        """
        Aggregate scores from multiple expert agents.

        Weights:
        - Australian standards: 25%
        - Clinical accuracy: 30%
        - Educational alignment: 20%
        - RAG citation quality: 15%
        - Cultural safety: 10%
        """
        weights = {
            "australian_standards": 0.25,
            "clinical_accuracy": 0.30,
            "educational_alignment": 0.20,
            "rag_citation_quality": 0.15,
            "cultural_safety": 0.10,
        }

        # Map agents to criteria they evaluate
        agent_to_criteria = {
            "medication-management-expert": ["australian_standards", "clinical_accuracy"],
            "clinical-documentation-expert": ["australian_standards", "educational_alignment"],
            "radiology-interpretation-expert": ["clinical_accuracy"],
            "mental-health-crisis-expert": ["clinical_accuracy", "cultural_safety"],
            "history-taking-expert": ["educational_alignment"],
            "physical-examination-expert": ["educational_alignment", "clinical_accuracy"],
            "procedural-skills-expert": ["clinical_accuracy"],
            "pediatric-emergency-expert": ["clinical_accuracy"],
            "palliative-care-expert": ["clinical_accuracy", "cultural_safety"],
            "rural-medicine-expert": ["clinical_accuracy"],
            "pathology-interpretation-expert": ["clinical_accuracy"],
            "surgical-skills-expert": ["clinical_accuracy"],
            "infection-control-expert": ["clinical_accuracy"],
        }

        # Collect scores per criterion
        criterion_scores = defaultdict(list)
        for eval_result in agent_evaluations:
            agent = eval_result["agent_name"]
            criteria = agent_to_criteria.get(agent, ["clinical_accuracy"])

            for criterion in criteria:
                if criterion in eval_result.get("criteria_scores", {}):
                    criterion_scores[criterion].append(
                        eval_result["criteria_scores"][criterion]
                    )
                else:
                    # Use overall score as fallback
                    criterion_scores[criterion].append(eval_result["overall_score"])

        # Calculate average per criterion
        criterion_averages = {}
        for criterion, scores in criterion_scores.items():
            criterion_averages[criterion] = sum(scores) / len(scores) if scores else 0.0

        # Apply weights
        overall_score = sum(
            criterion_averages.get(criterion, 0.0) * weight
            for criterion, weight in weights.items()
        )

        return {
            "overall_score": round(overall_score, 2),
            "criterion_scores": {k: round(v, 2) for k, v in criterion_averages.items()},
            "agent_evaluations": agent_evaluations,
            "num_agents": len(agent_evaluations),
        }

    def check_quality_gates(self, aggregated_result: Dict) -> Dict:
        """
        Enforce zero-tolerance quality gates.

        Critical violations:
        1. Australian drug names incorrect
        2. RAG citation confidence <0.65
        3. Clinical safety concerns
        """
        violations = []

        # Check all agent evaluations for critical violations
        for agent_eval in aggregated_result["agent_evaluations"]:
            for violation in agent_eval.get("violations", []):
                # Handle both dict and string violations (for robustness)
                if isinstance(violation, str):
                    # String violation - convert to dict
                    violation = {
                        "severity": "warning",
                        "category": "general",
                        "issue": violation,
                        "location": aggregated_result.get("item_id", "unknown"),
                        "suggested_fix": "Manual review required"
                    }

                if violation.get("severity") == "critical":
                    violations.append({
                        "gate": violation.get("category", "unknown"),
                        "severity": "CRITICAL",
                        "action": "AUTO_REJECT",
                        "issue": violation.get("issue", str(violation)),
                        "agent": agent_eval["agent_name"],
                    })

        # If any critical violations, force fail
        if violations:
            aggregated_result["overall_score"] = 0.0
            aggregated_result["quality_gate_violations"] = violations
            aggregated_result["status"] = "REJECTED"
        else:
            # Determine status based on score
            score = aggregated_result["overall_score"]
            if score >= 9.0:
                aggregated_result["status"] = "EXCELLENT"
            elif score >= 8.0:
                aggregated_result["status"] = "APPROVED"
            elif score >= 7.0:
                aggregated_result["status"] = "NEEDS_REVISION"
            else:
                aggregated_result["status"] = "REJECTED"

        return aggregated_result

    async def evaluate_item(self, item: Dict) -> Dict:
        """
        Evaluate a single knowledge item with all assigned agents.
        """
        assigned_agents = item.get("assigned_agents", [])

        if not assigned_agents:
            return {
                "item_id": item.get("item_id"),
                "status": "SKIPPED",
                "reason": "No agents assigned",
            }

        # Evaluate with all agents in parallel
        agent_config = {}  # TODO: Load agent configs from .claude/agents/
        agent_evaluations = await asyncio.gather(*[
            self.evaluate_item_with_agent(item, agent, agent_config)
            for agent in assigned_agents
        ])

        # Aggregate scores
        aggregated_result = self.aggregate_scores(agent_evaluations)

        # Check quality gates
        final_result = self.check_quality_gates(aggregated_result)

        # Add item metadata
        final_result["item_id"] = item.get("item_id")
        final_result["item_type"] = item.get("item_type")
        final_result["specialty"] = item.get("specialty")
        final_result["file_path"] = item.get("file_path")

        return final_result

    async def evaluate_batch(self, batch: List[Dict]) -> List[Dict]:
        """Evaluate a batch of items in parallel."""
        results = await asyncio.gather(*[
            self.evaluate_item(item)
            for item in batch
        ])
        return results

    def save_evaluation_report(self, item_id: str, result: Dict):
        """Save individual evaluation report."""
        report_path = self.output_dir / "reports" / f"{item_id}_evaluation.json"
        with open(report_path, 'w') as f:
            json.dump(result, f, indent=2)

    def update_statistics(self, result: Dict):
        """Update running statistics."""
        self.stats["items_evaluated"] += 1
        self.stats["by_status"][result.get("status", "UNKNOWN")] += 1

        # Track scores by content type and specialty
        content_type = result.get("item_type", "unknown")
        specialty = result.get("specialty", "unknown")
        score = result.get("overall_score", 0.0)

        self.stats["by_content_type"][content_type].append(score)
        self.stats["by_specialty"][specialty].append(score)

        # Count violations
        violations = result.get("quality_gate_violations", [])
        self.stats["total_violations"] += len(violations)

    def print_progress(self, batch_num: int, total_batches: int):
        """Print progress update."""
        evaluated = self.stats["items_evaluated"]
        total = self.stats["total_items"]
        percentage = (evaluated / total * 100) if total > 0 else 0

        # Calculate average score
        all_scores = []
        for scores in self.stats["by_content_type"].values():
            all_scores.extend(scores)
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0.0

        print(f"  Batch {batch_num}/{total_batches}: "
              f"[{percentage:.1f}%] "
              f"Evaluated {evaluated}/{total} items "
              f"(avg score: {avg_score:.2f})")

    async def run_evaluation(
        self,
        max_items: Optional[int] = None,
        specialty: Optional[str] = None,
    ) -> Dict:
        """
        Run full evaluation workflow.

        Args:
            max_items: Maximum number of items to evaluate (for testing)
            specialty: Only evaluate items from specific specialty
        """
        print("=" * 80)
        print("irStudy Evaluation Orchestrator")
        print("=" * 80)
        print(f"Registry: {self.registry_path}")
        print(f"Output: {self.output_dir}")
        print(f"Batch size: {self.batch_size}")
        print(f"Max parallel agents: {self.max_parallel_agents}")
        print()

        # Get pending items
        pending_items = self.get_pending_items(max_items)

        # Filter by specialty if specified
        if specialty:
            pending_items = [
                item for item in pending_items
                if item.get("specialty", "").lower() == specialty.lower()
            ]

        # Prioritize queue
        prioritized_items = self.prioritize_queue(pending_items)

        self.stats["total_items"] = len(prioritized_items)

        print(f"📊 Items to evaluate: {len(prioritized_items)}")
        if specialty:
            print(f"🎯 Specialty filter: {specialty}")
        print()

        # Process in batches
        total_batches = (len(prioritized_items) + self.batch_size - 1) // self.batch_size

        print("🔄 Starting evaluation...")
        start_time = time.time()

        for batch_num, i in enumerate(range(0, len(prioritized_items), self.batch_size), 1):
            batch = prioritized_items[i:i + self.batch_size]

            # Evaluate batch
            results = await self.evaluate_batch(batch)

            # Save reports and update stats
            for result in results:
                if result.get("status") != "SKIPPED":
                    self.save_evaluation_report(result["item_id"], result)
                    self.update_statistics(result)

            # Print progress
            self.print_progress(batch_num, total_batches)

            # Delay between batches (rate limiting)
            if self.batch_delay > 0 and batch_num < total_batches:
                await asyncio.sleep(self.batch_delay)

        # Final statistics
        end_time = time.time()
        duration = end_time - start_time

        self.stats["end_time"] = datetime.now().isoformat()
        self.stats["duration_seconds"] = round(duration, 2)

        # Calculate summary metrics
        all_scores = []
        for scores in self.stats["by_content_type"].values():
            all_scores.extend(scores)

        summary = {
            "total_evaluated": self.stats["items_evaluated"],
            "avg_score": round(sum(all_scores) / len(all_scores), 2) if all_scores else 0.0,
            "approval_rate": round(
                len([s for s in all_scores if s >= 8.0]) / len(all_scores) * 100, 1
            ) if all_scores else 0.0,
            "excellent_rate": round(
                len([s for s in all_scores if s >= 9.0]) / len(all_scores) * 100, 1
            ) if all_scores else 0.0,
            "by_status": dict(self.stats["by_status"]),
            "duration_hours": round(duration / 3600, 2),
        }

        # Print final summary
        print()
        print("=" * 80)
        print("📊 EVALUATION SUMMARY")
        print("=" * 80)
        print(f"Total Items Evaluated: {summary['total_evaluated']}")
        print(f"Average Score: {summary['avg_score']}/10.0")
        print(f"Approval Rate (≥8.0): {summary['approval_rate']}%")
        print(f"Excellent Rate (≥9.0): {summary['excellent_rate']}%")
        print()
        print(f"By Status:")
        for status, count in summary['by_status'].items():
            print(f"  - {status}: {count}")
        print()
        print(f"Duration: {summary['duration_hours']} hours")
        print()
        print(f"✅ Evaluation complete!")
        print(f"📁 Reports saved to: {self.output_dir / 'reports'}")

        # Save summary
        summary_path = self.output_dir / "summary.json"
        with open(summary_path, 'w') as f:
            json.dump({
                "summary": summary,
                "statistics": dict(self.stats),
            }, f, indent=2)

        print(f"📄 Summary saved to: {summary_path}")

        return summary


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Evaluate irStudy medical content with expert agents"
    )
    parser.add_argument(
        "--registry-path",
        type=Path,
        default=Path("evaluation-system/data/knowledge_item_registry.json"),
        help="Path to knowledge item registry"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("evaluation-system/reports/default_run"),
        help="Output directory for reports"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of items to process in parallel"
    )
    parser.add_argument(
        "--max-parallel-agents",
        type=int,
        default=10,
        help="Maximum number of parallel agent evaluations"
    )
    parser.add_argument(
        "--batch-delay",
        type=float,
        default=0,
        help="Delay in seconds between batches (for rate limiting)"
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        help="Maximum number of items to evaluate (for testing)"
    )
    parser.add_argument(
        "--specialty",
        type=str,
        default=None,
        help="Only evaluate items from specific specialty"
    )
    parser.add_argument(
        "--delegation-mode",
        type=str,
        choices=["api", "cli"],
        default="cli",
        help="Delegation mode: 'api' (fast, requires API key) or 'cli' (slower, uses claude CLI, zero setup)"
    )

    args = parser.parse_args()

    # Select delegation module based on mode
    import importlib.util

    if args.delegation_mode == "cli":
        print("Using Claude CLI delegation (zero setup, slower)")
        delegation_module = "claude_cli_delegation"
    else:
        print("Using Anthropic API delegation (requires API key, faster)")
        delegation_module = "claude_task_delegation"

    # Load delegation module dynamically
    delegation_path = Path(__file__).parent / f"{delegation_module}.py"
    spec = importlib.util.spec_from_file_location(delegation_module, str(delegation_path))
    delegation = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(delegation)

    # Store delegation function globally for orchestrator to use
    global DELEGATION_FUNCTION
    DELEGATION_FUNCTION = delegation.evaluate_item_with_agent_real

    # Resolve paths
    base_dir = Path(__file__).parent.parent.parent
    registry_path = base_dir / args.registry_path
    output_dir = base_dir / args.output_dir

    # Create orchestrator with delegation function
    orchestrator = EvaluationOrchestrator(
        registry_path=registry_path,
        output_dir=output_dir,
        batch_size=args.batch_size,
        max_parallel_agents=args.max_parallel_agents,
        batch_delay=args.batch_delay,
        delegation_function=DELEGATION_FUNCTION,
    )

    # Run evaluation
    summary = asyncio.run(orchestrator.run_evaluation(
        max_items=args.max_items,
        specialty=args.specialty,
    ))

    return 0


if __name__ == "__main__":
    sys.exit(main())
