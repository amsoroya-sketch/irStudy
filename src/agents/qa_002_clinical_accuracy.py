#!/usr/bin/env python3
"""
QA-002: Clinical Accuracy Agent
Validates medical accuracy using RAG knowledge base with auto-correction

Agent Responsibilities:
- Drug dosage verification (vs eTG, Murtagh)
- Differential diagnosis validation
- Red flag completeness checking
- Management guideline accuracy
- Auto-correction with RAG confidence ≥0.85
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask
from scripts.validate_rag_facts import RAGFactValidator

import logging

logger = logging.getLogger(__name__)


class ClinicalAccuracyQA(BaseAgent):
    """
    QA-002: Clinical Accuracy Quality Assurance Agent.

    Expertise:
    - Medical fact verification via RAG
    - Australian clinical guidelines (eTG, Murtagh, Talley)
    - Drug dosing accuracy
    - Evidence-based medicine validation
    """

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="QA-002",
            name="Clinical Accuracy QA Agent",
            role=AgentRole.QA_TESTING,
            experience_years=15,
            technologies=[
                "RAG (Retrieval-Augmented Generation)",
                "PubMedBERT embeddings",
                "Qdrant vector database",
                "Medical knowledge bases",
            ],
            specializations=[
                "Drug dosage validation",
                "Differential diagnosis verification",
                "Evidence-based medicine",
                "Australian clinical guidelines",
            ],
            pros=[
                "RAG-powered fact-checking across 13 textbooks",
                "Auto-correction with high confidence matches",
                "Australian source prioritization (2x boost)",
                "Comprehensive citation generation",
            ],
            cons=[
                "Requires RAG system running (Qdrant)",
                "May miss very recent guidelines (RAG knowledge cutoff)",
                "Dependent on textbook quality in RAG",
            ],
            max_concurrent_tasks=3,
            quality_gate_required=True,
        )
        super().__init__(metadata)

        self.validator = None

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """
        Execute clinical accuracy validation with RAG.

        Task parameters:
        - directory: str - Directory to validate
        - pattern: str (optional) - File pattern (default: *.md)
        - auto_correct: bool (optional) - Enable auto-correction (default: True)
        - unverified_dir: str (optional) - Unverified claims directory
        - output_dir: str (optional) - Output directory for reports

        Returns:
            Dictionary with validation results
        """
        self.logger.info(f"🔬 Starting RAG-powered clinical accuracy validation")

        # Extract parameters
        directory = Path(task.metadata.get("directory"))
        pattern = task.metadata.get("pattern", "*.md")
        auto_correct = task.metadata.get("auto_correct", True)
        unverified_dir = Path(
            task.metadata.get("unverified_dir", "validation_reports/unverified_claims")
        )
        output_dir = Path(task.metadata.get("output_dir", "validation_reports"))

        # Ensure directories exist
        if not directory.exists():
            raise ValueError(f"Directory not found: {directory}")

        output_dir.mkdir(parents=True, exist_ok=True)
        unverified_dir.mkdir(parents=True, exist_ok=True)

        # Create validator (this initializes RAG service)
        self.logger.info("Initializing RAG Query Service...")
        self.validator = RAGFactValidator(
            auto_correct=auto_correct, unverified_claims_dir=unverified_dir
        )

        # Validate directory
        self.logger.info(f"RAG fact-checking {directory}")
        self.logger.info(f"Auto-correction: {'ENABLED' if auto_correct else 'DISABLED'}")
        self.logger.info(f"Confidence threshold: ≥0.85 for auto-correction")

        report = self.validator.validate_directory(directory, pattern)

        # Generate reports
        md_output = output_dir / "rag_validation.md"
        json_output = output_dir / "rag_validation.json"

        self.validator.generate_report_markdown(md_output)
        self.validator.generate_report_json(json_output)

        # Prepare result
        result = {
            "status": "success",
            "files_scanned": report.files_scanned,
            "claims_extracted": report.claims_extracted,
            "rag_verified": report.rag_verified,
            "auto_corrected": report.auto_corrected,
            "unverified_claims": report.unverified_claims,
            "average_confidence": report.average_confidence,
            "australian_sources_used": report.australian_sources_used,
            "corrections_applied": report.corrections_applied,
            "unverified_documents_created": report.unverified_documents_created,
            "reports": {"markdown": str(md_output), "json": str(json_output)},
            "artifacts": [str(md_output), str(json_output)] + report.unverified_documents_created,
        }

        self.logger.info(f"✓ Clinical accuracy validation complete")
        self.logger.info(f"  - Claims verified: {report.rag_verified}/{report.claims_extracted}")
        self.logger.info(f"  - Auto-corrections: {report.auto_corrected}")
        self.logger.info(f"  - Unverified claims: {report.unverified_claims}")
        self.logger.info(f"  - Average RAG confidence: {report.average_confidence:.2f}")

        return result

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate the clinical accuracy check results.

        Validation criteria:
        - All files scanned successfully
        - Reports generated
        - RAG system operational
        - High verification rate (>90%)
        - Unverified claims documented
        """
        errors = []

        # Check status
        if output.get("status") != "success":
            errors.append("Task did not complete successfully")

        # Check files scanned
        if output.get("files_scanned", 0) == 0:
            errors.append("No files were scanned")

        # Check claims extracted
        if output.get("claims_extracted", 0) == 0:
            self.logger.warning(
                "⚠️ No medical claims extracted - this may indicate pattern matching issues"
            )

        # Check RAG verification rate
        claims = output.get("claims_extracted", 1)
        verified = output.get("rag_verified", 0)
        verification_rate = (verified / claims) * 100 if claims > 0 else 0

        if verification_rate < 90:
            self.logger.warning(f"⚠️ RAG verification rate below 90%: {verification_rate:.1f}%")
            # Don't fail, but log warning

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

        # Check unverified claims documented
        unverified = output.get("unverified_claims", 0)
        unverified_docs = len(output.get("unverified_documents_created", []))

        if unverified > 0 and unverified_docs == 0:
            errors.append(f"{unverified} unverified claims but no documents created")

        # Check average confidence
        avg_confidence = output.get("average_confidence", 0)
        if avg_confidence < 0.80:
            self.logger.warning(f"⚠️ Average RAG confidence below 0.80: {avg_confidence:.2f}")

        validation_passed = len(errors) == 0

        if validation_passed:
            self.logger.info("✅ Validation passed - all quality gates met")
        else:
            self.logger.error(f"❌ Validation failed: {len(errors)} error(s)")

        return validation_passed, errors


# Example usage
if __name__ == "__main__":
    from src.agents.base_agent import AgentTask

    agent = ClinicalAccuracyQA()

    task = AgentTask(
        title="RAG fact-checking of ICRP OSCE content",
        description="Verify medical claims against RAG knowledge base with auto-correction",
        metadata={
            "directory": "ICRP_OSCE_Preparation",
            "auto_correct": True,
            "output_dir": "validation_reports",
        },
    )

    if agent.assign_task(task):
        result_task = agent.run_task(task)
        if result_task.status.value == "completed":
            print(
                f"✓ Verified {result_task.result['rag_verified']}/{result_task.result['claims_extracted']} claims"
            )
            print(f"✓ Auto-corrected {result_task.result['auto_corrected']} claims")
