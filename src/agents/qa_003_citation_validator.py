#!/usr/bin/env python3
"""
QA-003: Citation Validator Agent
Ensures all medical claims have proper citations from acceptable sources
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask
from scripts.validate_citations import CitationValidator

import logging

logger = logging.getLogger(__name__)


class CitationValidatorQA(BaseAgent):
    """QA-003: Citation Quality Assurance Agent"""

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="QA-003",
            name="Citation Validator QA Agent",
            role=AgentRole.QA_TESTING,
            experience_years=8,
            technologies=[
                "Citation analysis",
                "Medical literature standards",
                "eTG/AMC compliance",
            ],
            specializations=[
                "Citation format validation",
                "Source verification",
                "Evidence hierarchy",
            ],
            pros=["100% citation coverage enforcement", "Australian source prioritization"],
            cons=["Cannot verify citation accuracy, only presence"],
            max_concurrent_tasks=5,
            quality_gate_required=True,
        )
        super().__init__(metadata)
        self.validator = None

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        directory = Path(task.metadata.get("directory"))
        pattern = task.metadata.get("pattern", "*.md")
        strict_mode = task.metadata.get("strict_mode", True)
        output_dir = Path(task.metadata.get("output_dir", "validation_reports"))

        output_dir.mkdir(parents=True, exist_ok=True)

        self.validator = CitationValidator(strict_mode=strict_mode)
        report = self.validator.validate_directory(directory, pattern)

        md_output = output_dir / "citations.md"
        json_output = output_dir / "citations.json"

        self.validator.generate_report_markdown(md_output)
        self.validator.generate_report_json(json_output)

        return {
            "status": "success",
            "files_scanned": report.files_scanned,
            "claims_found": report.claims_found,
            "cited_claims": report.cited_claims,
            "uncited_claims": report.uncited_claims,
            "citation_coverage": report.citation_coverage,
            "reports": {"markdown": str(md_output), "json": str(json_output)},
            "artifacts": [str(md_output), str(json_output)],
        }

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        errors = []
        if output.get("status") != "success":
            errors.append("Task failed")
        if output.get("citation_coverage", 0) < 95:
            self.logger.warning(
                f"⚠️ Citation coverage below 95%: {output.get('citation_coverage')}%"
            )
        return len(errors) == 0, errors
