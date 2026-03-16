#!/usr/bin/env python3
"""
Complete Persona Validation Pipeline
Integrates: Persona Creation → Clinical Validation (Claude) → QA Validation → Database Storage
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, Tuple

from qa_validator import PersonaQAValidator
from claude_validator import ClaudeClinicalValidator


class ValidationPipeline:
    """
    End-to-end validation pipeline for patient personas
    """

    def __init__(self, output_dir: str = "./validation-output"):
        """
        Initialize pipeline

        Args:
            output_dir: Directory for validation reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        self.qa_validator = PersonaQAValidator()
        self.clinical_validator = ClaudeClinicalValidator()

    def run_pipeline(
        self,
        persona_json: Dict[str, Any],
        specialty: str,
        save_reports: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete validation pipeline

        Args:
            persona_json: Persona data
            specialty: Specialty (for clinical validation)
            save_reports: Whether to save reports to files

        Returns:
            Pipeline summary with all validation results
        """
        persona_id = persona_json.get("id", "unknown")

        print(f"\n{'='*70}")
        print(f"VALIDATION PIPELINE: {persona_id}")
        print(f"{'='*70}\n")

        # Step 1: Clinical Validation (FRACP-VALIDATOR-###)
        print(f"[STEP 1/3] Clinical Validation ({specialty})...")
        try:
            clinical_report = self.clinical_validator.validate_persona_clinical(
                persona_json, specialty
            )
            clinical_approved = clinical_report.get("overall_approval", False)
            clinical_score = clinical_report.get("clinical_accuracy_score", 0)

            print(f"  ✓ Clinical Validation Complete")
            print(f"    Score: {clinical_score}/10")
            print(f"    Status: {'✅ APPROVED' if clinical_approved else '❌ REJECTED'}")

        except Exception as e:
            print(f"  ❌ Clinical Validation Failed: {str(e)}")
            clinical_report = {
                "overall_approval": False,
                "clinical_accuracy_score": 0,
                "errors_found": [str(e)],
                "recommendation": "REJECTED - Validation error"
            }
            clinical_approved = False
            clinical_score = 0

        # Step 2: Technical QA Validation (QA-001)
        print(f"\n[STEP 2/3] Technical QA Validation (13 quality gates)...")
        try:
            qa_report = self.qa_validator.validate_single_persona(persona_json)
            qa_approved = qa_report["recommendation"] == "APPROVED FOR DEPLOYMENT"

            print(f"  ✓ QA Validation Complete")
            print(f"    Gates Passed: {qa_report['gates_passed']}/{qa_report['total_quality_gates']}")
            print(f"    Deployment Readiness: {qa_report['deployment_readiness']}%")
            print(f"    Status: {'✅ APPROVED' if qa_approved else '❌ REJECTED'}")

        except Exception as e:
            print(f"  ❌ QA Validation Failed: {str(e)}")
            qa_report = {
                "gates_passed": 0,
                "gates_failed": 13,
                "deployment_readiness": 0,
                "errors": [str(e)],
                "recommendation": "REJECTED - Validation error"
            }
            qa_approved = False

        # Step 3: Deployment Decision
        print(f"\n[STEP 3/3] Deployment Decision...")

        deployment_approved = clinical_approved and qa_approved

        if deployment_approved:
            print(f"  ✅ APPROVED FOR DEPLOYMENT")
            deployment_status = "approved"
        else:
            print(f"  ❌ REJECTED - Requires Revision")
            deployment_status = "rejected"

            # Print reasons
            if not clinical_approved:
                print(f"    Reason: Clinical validation failed (score {clinical_score}/10)")
            if not qa_approved:
                print(f"    Reason: QA validation failed ({qa_report['gates_failed']} gates failed)")

        # Save reports if requested
        if save_reports:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save clinical validation report
            clinical_report_file = os.path.join(
                self.output_dir,
                f"{persona_id}_clinical_validation_{timestamp}.json"
            )
            with open(clinical_report_file, 'w') as f:
                json.dump(clinical_report, f, indent=2)

            # Save QA validation report
            qa_report_file = os.path.join(
                self.output_dir,
                f"{persona_id}_qa_validation_{timestamp}.json"
            )
            with open(qa_report_file, 'w') as f:
                json.dump(qa_report, f, indent=2)

            print(f"\n  📄 Reports saved:")
            print(f"     {clinical_report_file}")
            print(f"     {qa_report_file}")

        # Create pipeline summary
        summary = {
            "persona_id": persona_id,
            "specialty": specialty,
            "validation_date": datetime.now().isoformat(),

            "clinical_validation": {
                "approved": clinical_approved,
                "score": clinical_score,
                "recommendation": clinical_report.get("recommendation")
            },

            "qa_validation": {
                "approved": qa_approved,
                "gates_passed": qa_report.get("gates_passed", 0),
                "gates_failed": qa_report.get("gates_failed", 0),
                "deployment_readiness": qa_report.get("deployment_readiness", 0)
            },

            "deployment": {
                "approved": deployment_approved,
                "status": deployment_status
            },

            "full_reports": {
                "clinical": clinical_report,
                "qa": qa_report
            }
        }

        print(f"\n{'='*70}")
        print(f"PIPELINE SUMMARY")
        print(f"{'='*70}")
        print(f"Clinical Validation: {'✅ PASS' if clinical_approved else '❌ FAIL'} ({clinical_score}/10)")
        print(f"QA Validation: {'✅ PASS' if qa_approved else '❌ FAIL'} ({qa_report.get('gates_passed', 0)}/13 gates)")
        print(f"Deployment Status: {'✅ APPROVED' if deployment_approved else '❌ REJECTED'}")
        print(f"{'='*70}\n")

        return summary


def main():
    """
    CLI entry point
    """
    if len(sys.argv) < 3:
        print("Usage: python validation_pipeline.py <persona_json_file> <specialty>")
        print("Example: python validation_pipeline.py cardiology_001_stemi.json Cardiology")
        sys.exit(1)

    persona_file = sys.argv[1]
    specialty = sys.argv[2]

    # Load persona
    try:
        with open(persona_file, 'r') as f:
            persona = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: File not found: {persona_file}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in file: {persona_file}")
        sys.exit(1)

    # Run pipeline
    pipeline = ValidationPipeline()
    summary = pipeline.run_pipeline(persona, specialty)

    # Save summary
    summary_file = persona_file.replace('.json', '_pipeline_summary.json')
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"Pipeline summary saved to: {summary_file}")

    # Exit with appropriate code
    sys.exit(0 if summary["deployment"]["approved"] else 1)


if __name__ == "__main__":
    main()
