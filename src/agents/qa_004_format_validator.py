#!/usr/bin/env python3
"""
QA-004: Format Validator Agent
Validates document structure, frequency indicators, and required sections
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask

import logging
logger = logging.getLogger(__name__)


@dataclass
class FormatIssue:
    file: str
    line: int
    issue: str
    severity: str


class FormatValidatorQA(BaseAgent):
    """QA-004: Format and Structure Validator"""

    REQUIRED_SECTIONS = [
        "AMC EXAM FREQUENCY INDICATOR",
        "Purpose",
        "Opening Statement",
        "Red flag",
        "IMG Common Mistakes"
    ]

    FREQUENCY_PATTERN = r'\[([⭐]{1,3})\s+(HIGH|MEDIUM|LOW)-YIELD\]'

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="QA-004",
            name="Format Validator QA Agent",
            role=AgentRole.QA_TESTING,
            experience_years=5,
            technologies=["Markdown validation", "Document structure", "Template compliance"],
            specializations=["Frequency indicators", "Section completeness", "Format consistency"],
            pros=["Fast validation", "Template enforcement", "Consistency checking"],
            cons=["Cannot validate content quality"],
            max_concurrent_tasks=10,
            quality_gate_required=False
        )
        super().__init__(metadata)

    def validate_file_format(self, file_path: Path) -> List[FormatIssue]:
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            # Check frequency indicator
            if not re.search(self.FREQUENCY_PATTERN, content):
                issues.append(FormatIssue(
                    file=str(file_path),
                    line=0,
                    issue="Missing frequency indicator [⭐⭐⭐ HIGH-YIELD] format",
                    severity="important"
                ))

            # Check required sections
            for section in self.REQUIRED_SECTIONS:
                if section.lower() not in content.lower():
                    issues.append(FormatIssue(
                        file=str(file_path),
                        line=0,
                        issue=f"Missing required section: {section}",
                        severity="important"
                    ))

        except Exception as e:
            logger.error(f"Error validating {file_path}: {e}")

        return issues

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        directory = Path(task.metadata.get('directory'))
        pattern = task.metadata.get('pattern', '*.md')

        all_issues = []
        files_scanned = 0

        for file_path in directory.glob(pattern):
            if file_path.name.startswith('.'):
                continue

            files_scanned += 1
            issues = self.validate_file_format(file_path)
            all_issues.extend(issues)

        return {
            'status': 'success',
            'files_scanned': files_scanned,
            'issues_found': len(all_issues),
            'issues': [{'file': i.file, 'line': i.line, 'issue': i.issue, 'severity': i.severity} for i in all_issues]
        }

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        errors = []
        if output.get('status') != 'success':
            errors.append("Task failed")
        return len(errors) == 0, errors
