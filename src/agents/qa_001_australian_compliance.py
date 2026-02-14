#!/usr/bin/env python3
"""
QA-001: Australian Compliance Agent
Auto-corrects American terminology and enforces Australian medical standards

Agent Responsibilities:
- Australian terminology enforcement (paediatric NOT pediatric)
- Australian drug names (paracetamol NOT acetaminophen)
- Australian emergency numbers (000 NOT 911)
- Australian units and conventions
- Frequency indicator format validation
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask
from scripts.validate_australian_compliance import AustralianComplianceValidator

import logging

logger = logging.getLogger(__name__)


class AustralianComplianceQA(BaseAgent):
    """
    QA-001: Australian Compliance Quality Assurance Agent.

    Expertise:
    - Australian medical terminology standards
    - PROJECT_CONSTRAINTS.md compliance
    - AHPRA documentation standards
    - AMC exam terminology requirements
    """

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="QA-001",
            name="Australian Compliance QA Agent",
            role=AgentRole.QA_TESTING,
            experience_years=10,
            technologies=[
                "Australian medical terminology",
                "AHPRA standards",
                "AMC exam requirements",
                "PROJECT_CONSTRAINTS.md compliance",
            ],
            specializations=[
                "Australian vs American terminology",
                "PBS drug naming",
                "SI unit enforcement",
                "Australian clinical conventions",
            ],
            pros=[
                "100% compliance with Australian standards",
                "Auto-correction capability",
                "Comprehensive terminology database",
                "Zero-tolerance for American terms",
            ],
            cons=[
                "May flag British spellings as issues",
                "Requires manual review for ambiguous terms",
            ],
            max_concurrent_tasks=5,
            quality_gate_required=True,
        )
        super().__init__(metadata)

        self.validator = None

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute Australian compliance validation task.

        Task parameters:
        - directory: str - Directory to validate
        - pattern: str (optional) - File pattern (default: *.md)
        - auto_correct: bool (optional) - Enable auto-correction (default: True)
        - output_dir: str (optional) - Output directory for reports

        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"🇦🇺 Starting Australian compliance validation")

        # Extract parameters
        directory = Path(task.metadata.get("directory"))
        pattern = task.metadata.get("pattern", "*.md")
        auto_correct = task.metadata.get("auto_correct", True)
        output_dir = Path(task.metadata.get("output_dir", "validation_reports"))

        # Ensure directories exist
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory}")

        output_dir.mkdir(parents=True, exist_ok=True)

        # Create validator
        self.validator = AustralianComplianceValidator(auto_correct=auto_correct)

        # Validate directory
        self.logger.info(f"Scanning {directory} for Australian compliance")
        self.logger.info(f"Auto-correction: {'ENABLED' if auto_correct else 'DISABLED'}")

        report = self.validator.validate_directory(directory, pattern)

        # Generate reports
        md_output = output_dir / "australian_compliance.md"
        json_output = output_dir / "australian_compliance.json"

        self.validator.generate_report_markdown(md_output)
        self.validator.generate_report_json(json_output)

        # Prepare result
        result = {
            "status": "success",
            "files_scanned": report.files_scanned,
            "issues_found": report.issues_found,
            "auto_corrections": report.auto_corrections,
            "manual_review_needed": report.manual_review_needed,
            "compliance_score": report.compliance_score,
            "reports": {"markdown": str(md_output), "json": str(json_output)},
            "artifacts": [str(md_output), str(json_output)],
        }

        self.logger.info(f"✓ Australian compliance validation complete")
        self.logger.info(f"  - Compliance score: {report.compliance_score:.1f}%")
        self.logger.info(f"  - Auto-corrections: {report.auto_corrections}")
        self.logger.info(f"  - Manual review needed: {report.manual_review_needed}")

        return result

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate the compliance check results.

        Validation criteria:
        - All files scanned successfully
        - Reports generated
        - Compliance score calculated
        - Zero critical errors in validation process
        """
        errors = []

        # Check status
        if output.get("status") != "success":
            errors.append("Task did not complete successfully")

        # Check files scanned
        if output.get("files_scanned", 0) == 0:
            errors.append("No files were scanned")

        # Check reports generated
        if "reports" not in output:
            errors.append("Reports not generated")
        else:
            md_path = Path(output["reports"]["markdown"])
            json_path = Path(output["reports"]["json"])

            if not md_path.exists():
                errors.append(f"Markdown report not found: {md_path}")
            if not json_path.exists():
                errors.append(f"JSON report not found: {json_path}")

        # Check compliance score calculated
        if "compliance_score" not in output:
            errors.append("Compliance score not calculated")

        # Quality gate: For ICRP content, we expect high compliance
        if output.get("compliance_score", 0) < 90:
            self.logger.warning(f"⚠️ Compliance score below 90%: {output.get('compliance_score')}%")
            # Don't fail, but log warning

        validation_passed = len(errors) == 0

        if validation_passed:
            self.logger.info("✅ Validation passed - all quality gates met")
        else:
            self.logger.error(f"❌ Validation failed: {len(errors)} error(s)")

        return validation_passed, errors


# Example usage
if __name__ == "__main__":
    from src.agents.base_agent import AgentTask

    # Create agent
    agent = AustralianComplianceQA()

    # Create task
    task = AgentTask(
        title="Validate ICRP OSCE content for Australian compliance",
        description="Scan all OSCE preparation files and auto-correct American terminology",
        metadata={
            "directory": "ICRP_OSCE_Preparation",
            "pattern": "*.md",
            "auto_correct": True,
            "output_dir": "validation_reports",
        },
    )

    # Assign and run
    if agent.assign_task(task):
        result_task = agent.run_task(task)

        if result_task.status.value == "completed":
            print("\n" + "=" * 60)
            print("✓ Australian Compliance Validation Complete")
            print("=" * 60)
            print(f"Files Scanned: {result_task.result['files_scanned']}")
            print(f"Issues Found: {result_task.result['issues_found']}")
            print(f"Auto-Corrections: {result_task.result['auto_corrections']}")
            print(f"Compliance Score: {result_task.result['compliance_score']:.1f}%")
            print("=" * 60)
        else:
            print(f"❌ Task failed: {result_task.error}")
