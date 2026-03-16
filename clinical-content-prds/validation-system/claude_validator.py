#!/usr/bin/env python3
"""
Claude API Integration for FRACP Clinical Validators
Invokes FRACP-VALIDATOR-001 to 010 using Claude API
"""

import json
import os
from typing import Dict, Any
from anthropic import Anthropic


class ClaudeClinicalValidator:
    """
    Invokes FRACP clinical validator agents using Claude API
    """

    def __init__(self, api_key: str = None):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key (or use ANTHROPIC_API_KEY env var)
        """
        self.client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
        self.model = "claude-sonnet-4-20250514"  # Claude Sonnet 4.5

        # Load validator skills
        self.skills_dir = os.path.expanduser("~/.claude/skills/medical-experts")

    def load_validator_skill(self, validator_id: str) -> str:
        """
        Load FRACP validator skill from file

        Args:
            validator_id: e.g., "FRACP-VALIDATOR-001"

        Returns:
            Validator skill prompt
        """
        # Map validator ID to file
        validator_files = {
            "FRACP-VALIDATOR-001": "fracp-validator-cardiology.md",
            "FRACP-VALIDATOR-002": "clinical-validators-all-specialties.md",  # Emergency
            "FRACP-VALIDATOR-003": "clinical-validators-all-specialties.md",  # GP
            "FRACP-VALIDATOR-004": "clinical-validators-all-specialties.md",  # Pediatrics
            "FRACP-VALIDATOR-005": "clinical-validators-all-specialties.md",  # ObGyn
            "FRACP-VALIDATOR-006": "clinical-validators-all-specialties.md",  # Surgery
            "FRACP-VALIDATOR-007": "clinical-validators-all-specialties.md",  # Psychiatry
            "FRACP-VALIDATOR-008": "clinical-validators-all-specialties.md",  # Respiratory
            "FRACP-VALIDATOR-009": "clinical-validators-all-specialties.md",  # Neurology
            "FRACP-VALIDATOR-010": "clinical-validators-all-specialties.md",  # ID
        }

        filename = validator_files.get(validator_id)
        if not filename:
            raise ValueError(f"Unknown validator ID: {validator_id}")

        filepath = os.path.join(self.skills_dir, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Validator skill file not found: {filepath}")

        with open(filepath, 'r') as f:
            return f.read()

    def validate_persona_clinical(
        self,
        persona_json: Dict[str, Any],
        specialty: str
    ) -> Dict[str, Any]:
        """
        Validate persona using appropriate FRACP clinical validator

        Args:
            persona_json: Persona data
            specialty: Specialty (Cardiology, Emergency, etc.)

        Returns:
            Clinical validation report
        """
        # Map specialty to validator ID
        specialty_validators = {
            "Cardiology": "FRACP-VALIDATOR-001",
            "Emergency": "FRACP-VALIDATOR-002",
            "General Practice": "FRACP-VALIDATOR-003",
            "Pediatrics": "FRACP-VALIDATOR-004",
            "ObGyn": "FRACP-VALIDATOR-005",
            "Surgery": "FRACP-VALIDATOR-006",
            "Psychiatry": "FRACP-VALIDATOR-007",
            "Respiratory": "FRACP-VALIDATOR-008",
            "Neurology": "FRACP-VALIDATOR-009",
            "Infectious Diseases": "FRACP-VALIDATOR-010"
        }

        validator_id = specialty_validators.get(specialty)
        if not validator_id:
            raise ValueError(f"Unknown specialty: {specialty}")

        # Load validator skill
        validator_skill = self.load_validator_skill(validator_id)

        # Construct validation prompt
        prompt = f"""You are {validator_id}, a FRACP-equivalent clinical validator.

{validator_skill}

---

TASK: Validate the following patient persona for clinical accuracy.

PERSONA JSON:
```json
{json.dumps(persona_json, indent=2)}
```

---

INSTRUCTIONS:
1. Review the persona against all 8 clinical validation criteria
2. Score each criterion (diagnosis accuracy, management appropriateness, etc.)
3. Calculate overall clinical accuracy score (0-10)
4. Provide structured feedback (strengths, improvements, critical issues)
5. Return validation report in JSON format

OUTPUT FORMAT:
```json
{{
  "validator_id": "{validator_id}",
  "validator_specialty": "{specialty}",
  "persona_id": "<persona_id>",
  "validation_date": "<ISO 8601 datetime>",
  "overall_approval": true/false,
  "clinical_accuracy_score": 0.0-10.0,
  "validation_results": {{
    "1_diagnosis_accuracy": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "2_management_appropriateness": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "3_australian_context": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "4_difficulty_appropriateness": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "5_critical_errors_defined": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "6_rag_citations_quality": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "7_history_structure": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}},
    "8_red_flags_identified": {{"status": "PASS/FAIL", "score": 0-10, "comment": "..."}}
  }},
  "errors_found": [],
  "feedback": {{
    "strengths": [],
    "improvements": [],
    "critical_issues": []
  }},
  "recommendation": "APPROVED/REJECTED - ...",
  "requires_revision": true/false
}}
```

IMPORTANT: Return ONLY the JSON validation report, no other text.
"""

        # Call Claude API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.3,  # Low temperature for consistent validation
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Extract JSON from response
        response_text = response.content[0].text

        # Try to extract JSON (handle markdown code blocks if present)
        if "```json" in response_text:
            # Extract from markdown code block
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_str = response_text[json_start:json_end].strip()
        else:
            json_str = response_text.strip()

        try:
            validation_report = json.loads(json_str)
            return validation_report
        except json.JSONDecodeError as e:
            # Return error report if JSON parsing fails
            return {
                "validator_id": validator_id,
                "persona_id": persona_json.get("id", "unknown"),
                "overall_approval": False,
                "clinical_accuracy_score": 0,
                "errors_found": [f"Failed to parse validation response: {str(e)}"],
                "recommendation": "REJECTED - Validator error",
                "requires_revision": True,
                "raw_response": response_text
            }


def validate_persona_with_claude(persona_filepath: str, specialty: str) -> Dict[str, Any]:
    """
    Convenience function to validate persona file using Claude

    Args:
        persona_filepath: Path to persona JSON file
        specialty: Specialty (Cardiology, Emergency, etc.)

    Returns:
        Clinical validation report
    """
    validator = ClaudeClinicalValidator()

    with open(persona_filepath, 'r') as f:
        persona = json.load(f)

    return validator.validate_persona_clinical(persona, specialty)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3:
        print("Usage: python claude_validator.py <persona_json_file> <specialty>")
        print("Example: python claude_validator.py cardiology_001_stemi.json Cardiology")
        sys.exit(1)

    filepath = sys.argv[1]
    specialty = sys.argv[2]

    try:
        report = validate_persona_with_claude(filepath, specialty)

        # Print summary
        print("\n" + "="*60)
        print(f"FRACP CLINICAL VALIDATION REPORT - {specialty}")
        print("="*60)
        print(f"Validator: {report.get('validator_id')}")
        print(f"Persona ID: {report.get('persona_id')}")
        print(f"Clinical Accuracy Score: {report.get('clinical_accuracy_score')}/10")
        print(f"Approval: {report.get('overall_approval')}")
        print(f"Recommendation: {report.get('recommendation')}")

        if report.get('feedback'):
            feedback = report['feedback']

            if feedback.get('strengths'):
                print("\nSTRENGTHS:")
                for strength in feedback['strengths']:
                    print(f"  ✅ {strength}")

            if feedback.get('improvements'):
                print("\nIMPROVEMENTS:")
                for improvement in feedback['improvements']:
                    print(f"  💡 {improvement}")

            if feedback.get('critical_issues'):
                print("\nCRITICAL ISSUES:")
                for issue in feedback['critical_issues']:
                    print(f"  ❌ {issue}")

        # Write full report
        output_file = filepath.replace('.json', '_clinical_validation.json')
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nFull report written to: {output_file}")
        print("="*60)

        # Exit with error code if failed
        sys.exit(0 if report.get('overall_approval') else 1)

    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
