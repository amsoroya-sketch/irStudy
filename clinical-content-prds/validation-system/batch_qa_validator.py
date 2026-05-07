#!/usr/bin/env python3
"""
Batch QA Validator - Validate personas batch by batch
Runs 13 quality gates on all 207 personas grouped by specialty
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
from qa_validator import PersonaQAValidator


class BatchQAValidator:
    """Validates personas in batches by specialty"""

    def __init__(self, persona_dir: str = "batch1_personas"):
        self.persona_dir = Path(persona_dir)
        self.validator = PersonaQAValidator()
        self.results = {
            "validation_started": datetime.now().isoformat(),
            "batches": {},
            "overall_stats": {
                "total_personas": 0,
                "total_passed": 0,
                "total_failed": 0,
                "deployment_ready": 0
            }
        }

    def get_specialty_batches(self) -> Dict[str, List[Path]]:
        """Group persona files by specialty"""
        batches = {
            "cardiology": [],
            "emergency": [],
            "general": [],
            "pediatrics": [],
            "respiratory": []
        }

        for filepath in sorted(self.persona_dir.glob("*_persona.json")):
            specialty = filepath.name.split("_")[0]
            if specialty in batches:
                batches[specialty].append(filepath)

        return batches

    def validate_batch(self, specialty: str, persona_files: List[Path]) -> Dict[str, Any]:
        """Validate all personas in a specialty batch"""
        print(f"\n{'='*80}")
        print(f"VALIDATING {specialty.upper()} BATCH ({len(persona_files)} personas)")
        print(f"{'='*80}\n")

        batch_results = {
            "specialty": specialty,
            "total_personas": len(persona_files),
            "passed": 0,
            "failed": 0,
            "deployment_ready": 0,
            "personas": [],
            "errors_summary": {},
            "validation_completed": None
        }

        for i, filepath in enumerate(persona_files, 1):
            try:
                # Load persona
                with open(filepath, 'r') as f:
                    persona = json.load(f)

                # Validate
                print(f"[{i}/{len(persona_files)}] Validating {filepath.name}...", end=" ")
                validation_result = self.validator.validate_single_persona(persona)

                # Determine pass/fail
                gates_passed = validation_result["gates_passed"]
                gates_failed = validation_result["gates_failed"]
                deployment_ready = gates_passed >= 12  # 12/13 gates minimum

                if deployment_ready:
                    batch_results["deployment_ready"] += 1
                    print(f"✅ PASS ({gates_passed}/13 gates)")
                else:
                    print(f"❌ FAIL ({gates_passed}/13 gates, {gates_failed} failed)")

                if gates_failed == 0:
                    batch_results["passed"] += 1
                else:
                    batch_results["failed"] += 1

                # Save QA report
                qa_report_path = filepath.parent / filepath.name.replace("_persona.json", "_persona_qa_report.json")
                with open(qa_report_path, 'w') as f:
                    json.dump(validation_result, f, indent=2)

                # Collect errors
                for error in validation_result.get("errors", []):
                    batch_results["errors_summary"][error] = batch_results["errors_summary"].get(error, 0) + 1

                # Store summary
                batch_results["personas"].append({
                    "id": persona.get("id"),
                    "file": filepath.name,
                    "gates_passed": gates_passed,
                    "gates_failed": gates_failed,
                    "deployment_ready": deployment_ready,
                    "errors": validation_result.get("errors", [])
                })

            except Exception as e:
                print(f"❌ ERROR: {e}")
                batch_results["failed"] += 1
                batch_results["personas"].append({
                    "file": filepath.name,
                    "error": str(e)
                })

        batch_results["validation_completed"] = datetime.now().isoformat()

        # Print batch summary
        print(f"\n{'='*80}")
        print(f"{specialty.upper()} BATCH SUMMARY")
        print(f"{'='*80}")
        print(f"Total Personas:      {batch_results['total_personas']}")
        print(f"Perfect (13/13):     {batch_results['passed']}")
        print(f"Deployment Ready:    {batch_results['deployment_ready']} ({batch_results['deployment_ready']*100//batch_results['total_personas']}%)")
        print(f"Failed:              {batch_results['failed']}")

        if batch_results["errors_summary"]:
            print(f"\nTop Errors:")
            for error, count in sorted(batch_results["errors_summary"].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"  - {error}: {count} occurrences")

        print(f"{'='*80}\n")

        return batch_results

    def validate_all_batches(self) -> Dict[str, Any]:
        """Validate all batches sequentially"""
        batches = self.get_specialty_batches()

        print(f"\n{'#'*80}")
        print(f"BATCH QA VALIDATION - 207 PERSONAS")
        print(f"{'#'*80}")
        print(f"Total batches: {len(batches)}")
        print(f"Total personas: {sum(len(files) for files in batches.values())}")
        print(f"{'#'*80}\n")

        for specialty, persona_files in batches.items():
            batch_result = self.validate_batch(specialty, persona_files)
            self.results["batches"][specialty] = batch_result

            # Update overall stats
            self.results["overall_stats"]["total_personas"] += batch_result["total_personas"]
            self.results["overall_stats"]["total_passed"] += batch_result["passed"]
            self.results["overall_stats"]["total_failed"] += batch_result["failed"]
            self.results["overall_stats"]["deployment_ready"] += batch_result["deployment_ready"]

        self.results["validation_completed"] = datetime.now().isoformat()

        # Print overall summary
        self._print_overall_summary()

        # Save results
        self._save_results()

        return self.results

    def _print_overall_summary(self):
        """Print overall validation summary"""
        stats = self.results["overall_stats"]

        print(f"\n{'#'*80}")
        print(f"OVERALL VALIDATION SUMMARY")
        print(f"{'#'*80}")
        print(f"Total Personas:          {stats['total_personas']}")
        print(f"Perfect (13/13 gates):   {stats['total_passed']} ({stats['total_passed']*100//stats['total_personas']}%)")
        print(f"Deployment Ready (≥12):  {stats['deployment_ready']} ({stats['deployment_ready']*100//stats['total_personas']}%)")
        print(f"Failed:                  {stats['total_failed']} ({stats['total_failed']*100//stats['total_personas']}%)")
        print(f"{'#'*80}\n")

        print(f"Batch Breakdown:")
        for specialty, batch in self.results["batches"].items():
            print(f"  {specialty.capitalize():20} {batch['deployment_ready']:3}/{batch['total_personas']:3} deployment ready ({batch['deployment_ready']*100//batch['total_personas']:3}%)")

        print(f"\n{'#'*80}\n")

    def _save_results(self):
        """Save validation results to JSON"""
        output_file = self.persona_dir / "batch_validation_results.json"
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"✅ Validation results saved to: {output_file}")

        # Save summary report
        summary_file = self.persona_dir / "batch_validation_summary.md"
        with open(summary_file, 'w') as f:
            f.write(f"# Batch QA Validation Summary\n\n")
            f.write(f"**Date**: {self.results['validation_started']}\n\n")
            f.write(f"## Overall Results\n\n")
            f.write(f"- **Total Personas**: {self.results['overall_stats']['total_personas']}\n")
            f.write(f"- **Perfect (13/13)**: {self.results['overall_stats']['total_passed']} ({self.results['overall_stats']['total_passed']*100//self.results['overall_stats']['total_personas']}%)\n")
            f.write(f"- **Deployment Ready**: {self.results['overall_stats']['deployment_ready']} ({self.results['overall_stats']['deployment_ready']*100//self.results['overall_stats']['total_personas']}%)\n")
            f.write(f"- **Failed**: {self.results['overall_stats']['total_failed']}\n\n")
            f.write(f"## Batch Results\n\n")
            f.write(f"| Specialty | Total | Perfect | Deployment Ready | Failed |\n")
            f.write(f"|-----------|-------|---------|------------------|--------|\n")
            for specialty, batch in self.results["batches"].items():
                f.write(f"| {specialty.capitalize()} | {batch['total_personas']} | {batch['passed']} | {batch['deployment_ready']} | {batch['failed']} |\n")

        print(f"✅ Summary report saved to: {summary_file}\n")


def main():
    """Main execution"""
    validator = BatchQAValidator()
    results = validator.validate_all_batches()

    # Exit with appropriate code
    if results["overall_stats"]["deployment_ready"] >= 200:  # 96.6% target
        print("✅ VALIDATION SUCCESS: ≥200 personas deployment ready")
        sys.exit(0)
    else:
        print(f"⚠️  WARNING: Only {results['overall_stats']['deployment_ready']}/207 personas deployment ready")
        sys.exit(1)


if __name__ == "__main__":
    main()
