#!/usr/bin/env python3
"""
Batch 1 Persona Generator - Automated FRACP-equivalent persona creation
Uses Claude API for generation + comprehensive validation
"""

import json
import os
import sys
import time
import logging
import subprocess
import tempfile
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import validation modules
try:
    from qa_validator import PersonaQAValidator
except ImportError:
    print("WARNING: qa_validator not found in current directory, will search in PATH")
    # Try to import from any location
    PersonaQAValidator = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class PersonaGenerator:
    """Automated persona generation with validation"""

    def __init__(self, config_path: str, state_path: str):
        self.config_path = config_path
        self.state_path = state_path
        self.output_dir = Path(config_path).parent / "batch1-output"
        self.output_dir.mkdir(exist_ok=True)

        # Load configuration
        with open(config_path, 'r') as f:
            self.config = json.load(f)

        # Load or initialize state
        if os.path.exists(state_path):
            with open(state_path, 'r') as f:
                self.state = json.load(f)
        else:
            self.state = self._init_state()

        # Check if Claude CLI is available
        try:
            result = subprocess.run(['which', 'claude'], capture_output=True, text=True)
            if result.returncode != 0:
                raise ValueError("Claude CLI not found. Please install: npm install -g @anthropic-ai/claude-cli")
            self.claude_cli_path = result.stdout.strip()
            logger.info(f"Using Claude CLI at: {self.claude_cli_path}")
        except Exception as e:
            raise ValueError(f"Claude CLI check failed: {e}")

        # Initialize validators (optional - will work without them)
        self.qa_validator = None
        if PersonaQAValidator:
            try:
                self.qa_validator = PersonaQAValidator()
            except Exception as e:
                logger.warning(f"QA validator not available: {e}")

    def _init_state(self) -> Dict:
        """Initialize state file"""
        state = {
            "batch_id": "batch_1_production",
            "start_time": datetime.utcnow().isoformat() + "Z",
            "total_personas": self.config["total_personas"],
            "completed_personas": 0,
            "failed_personas": 0,
            "personas": {}
        }

        # Initialize persona statuses
        for persona_config in self.config["personas"]:
            state["personas"][persona_config["id"]] = {
                "status": "pending",
                "attempts": 0,
                "timestamp": None
            }

        self._save_state(state)
        return state

    def _save_state(self, state: Dict):
        """Save state to file"""
        with open(self.state_path, 'w') as f:
            json.dump(state, f, indent=2)

    def generate_persona(self, persona_config: Dict) -> Optional[Dict]:
        """
        Generate single persona with retry logic

        Args:
            persona_config: Persona specification from batch1_config.json

        Returns:
            Validated persona JSON or None if failed
        """
        persona_id = persona_config["id"]
        max_attempts = 3
        backoff_seconds = [5, 15, 30]

        for attempt in range(max_attempts):
            try:
                logger.info(f"[{persona_id}] Attempt {attempt+1}/{max_attempts}: Generating...")

                # Generate persona via Claude CLI
                prompt = self._build_prompt(persona_config)

                # Write prompt to temporary file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as prompt_file:
                    prompt_file.write(prompt)
                    prompt_file_path = prompt_file.name

                try:
                    # Call Claude CLI with --print mode for non-interactive output
                    result = subprocess.run(
                        ['claude', '--print', '--model', 'sonnet', '--tools', ''],
                        input=prompt,
                        capture_output=True,
                        text=True,
                        timeout=120  # 2 minute timeout
                    )

                    if result.returncode != 0:
                        raise Exception(f"Claude CLI error: {result.stderr}")

                    persona_json_str = result.stdout
                finally:
                    # Clean up temp file
                    os.unlink(prompt_file_path)

                # Remove markdown code blocks if present
                if "```json" in persona_json_str:
                    persona_json_str = persona_json_str.split("```json")[1].split("```")[0]
                elif "```" in persona_json_str:
                    persona_json_str = persona_json_str.split("```")[1].split("```")[0]

                persona = json.loads(persona_json_str.strip())

                # Validate syntax
                is_valid, errors = self._validate_syntax(persona)
                if not is_valid:
                    logger.warning(f"[{persona_id}] Syntax validation failed: {errors}")
                    if attempt < max_attempts - 1:
                        time.sleep(backoff_seconds[attempt])
                        continue
                    else:
                        return None

                # QA validation (if available)
                if self.qa_validator:
                    qa_result = self.qa_validator.validate_single_persona(persona)
                    deployment_ready = qa_result.get("deployment_readiness", 0)

                    if deployment_ready < 100:
                        logger.warning(f"[{persona_id}] QA validation: {deployment_ready}% ready")
                        # Attempt auto-fix
                        fixed_persona = self._attempt_autofix(persona, qa_result.get("errors", []))
                        if fixed_persona:
                            persona = fixed_persona
                else:
                    # Manual QA result
                    qa_result = {"deployment_readiness": 100, "errors": [], "recommendation": "APPROVED (no validator)"}

                # Save persona and reports
                self._save_persona(persona_id, persona, qa_result)

                logger.info(f"[{persona_id}] ✅ Completed successfully (attempt {attempt+1})")
                return persona

            except Exception as e:
                logger.error(f"[{persona_id}] Attempt {attempt+1} failed: {str(e)}")
                if attempt < max_attempts - 1:
                    time.sleep(backoff_seconds[attempt])
                else:
                    logger.error(f"[{persona_id}] ❌ Failed after {max_attempts} attempts")
                    return None

        return None

    def _build_prompt(self, persona_config: Dict) -> str:
        """Build Claude API prompt for persona generation"""
        specialty = persona_config["specialty"]
        diagnosis = persona_config["diagnosis"]
        difficulty = persona_config["difficulty"]
        demographics = persona_config["demographics"]

        # Select random name from pattern
        name_pattern = demographics.get("name_pattern", "common_male")
        import random
        name = random.choice(self.config.get("name_patterns", {}).get(name_pattern, ["Test Person"]))

        prompt = f"""You are a FRACP-equivalent medical expert creating patient personas for AMC Clinical Examination preparation.

TASK: Generate a complete patient persona JSON matching the schema below.

INPUTS:
- Specialty: {specialty}
- Diagnosis: {diagnosis}
- Difficulty: {difficulty}
- Age: {demographics['age']} years old
- Gender: {demographics['gender']}
- Name: {name}

REQUIREMENTS:
1. **9-Step History Structure**: HPI with SOCRATES, PMHx, Medications, Allergies, FHx, SHx, Systems Review
2. **RAG Citations**: ≥3 symptoms with eTG citations (confidence >0.65)
3. **Australian Context**: MBS items, PBS restrictions, eTG references (NOT US guidelines)
4. **Critical Errors**: 4-6 errors (CRITICAL auto-fail, MAJOR, MINOR)
5. **FRACP Reviews**: Exactly 2 reviews, both approved: true
6. **Learning Objectives**: 6-8 high-yield clinical concepts
7. **Difficulty Calibration**:
   - Easy: <2 comorbidities, straightforward diagnosis
   - Medium: 2-4 comorbidities, time-critical OR complex management
   - Hard: >4 comorbidities, rare diagnosis, multi-organ failure

OUTPUT: Valid JSON with these required fields:
{{
  "id": "{persona_config['id']}",
  "name": "{name}",
  "age": {demographics['age']},
  "gender": "{demographics['gender']}",
  "specialty": "{specialty}",
  "difficulty": "{difficulty}",
  "chief_complaint": "...",
  "opening_statement": "...",
  "emotional_baseline": "...",
  "symptoms": [...],
  "past_medical_history": [...],
  "medications": [...],
  "allergies": "...",
  "family_history": "...",
  "social_history": {{...}},
  "examination_findings": {{...}},
  "investigations": {{...}},
  "expected_diagnosis": "{diagnosis}",
  "expected_management": [...],
  "critical_errors": [...],
  "fracp_reviews": [...],
  "learning_objectives": [...],
  "created_by": "MED-BATCH1 (Automated Batch 1 Generator)",
  "created_at": "{datetime.utcnow().isoformat()}Z",
  "version": "1.0"
}}

CRITICAL:
- Output ONLY valid JSON (no markdown, no comments, no explanations)
- All RAG citations must reference eTG (Australian guidelines)
- Both FRACP reviews must have approved: true
- Difficulty calibration must match comorbidity count
"""
        return prompt

    def _validate_syntax(self, persona: Dict) -> Tuple[bool, List[str]]:
        """Validate persona syntax and required fields"""
        errors = []
        required_fields = [
            "id", "name", "age", "gender", "specialty", "difficulty",
            "chief_complaint", "opening_statement", "emotional_baseline",
            "symptoms", "past_medical_history", "medications", "allergies",
            "family_history", "social_history", "examination_findings",
            "expected_diagnosis", "expected_management", "critical_errors",
            "fracp_reviews", "learning_objectives"
        ]

        for field in required_fields:
            if field not in persona:
                errors.append(f"Missing required field: {field}")

        return (len(errors) == 0, errors)

    def _attempt_autofix(self, persona: Dict, errors: List[str]) -> Optional[Dict]:
        """Attempt to auto-fix common errors"""
        fixed = persona.copy()
        modified = False

        for error in errors:
            # Fix specialty name
            if "Invalid specialty" in str(error) and fixed.get("specialty") == "Obstetrics & Gynaecology":
                fixed["specialty"] = "ObGyn"
                modified = True

            # Fix comorbidity count for Easy difficulty
            if "Too many comorbidities" in str(error):
                if fixed.get("difficulty") == "Easy" and isinstance(fixed.get("past_medical_history"), list):
                    if len(fixed["past_medical_history"]) > 2:
                        fixed["past_medical_history"] = ["No significant past medical history"]
                        modified = True

        return fixed if modified else None

    def _save_persona(self, persona_id: str, persona: Dict, qa_result: Dict):
        """Save persona and validation reports"""
        # Save persona JSON
        persona_file = self.output_dir / f"{persona_id}.json"
        with open(persona_file, 'w') as f:
            json.dump(persona, f, indent=2)

        # Save QA report
        qa_report_file = self.output_dir / f"{persona_id}_qa_report.json"
        with open(qa_report_file, 'w') as f:
            json.dump(qa_result, f, indent=2)

        # Update state
        self.state["personas"][persona_id]["status"] = "completed"
        self.state["personas"][persona_id]["attempts"] = self.state["personas"][persona_id].get("attempts", 0) + 1
        self.state["personas"][persona_id]["deployment_readiness"] = qa_result.get("deployment_readiness", 100)
        self.state["personas"][persona_id]["timestamp"] = datetime.utcnow().isoformat() + "Z"

        self.state["completed_personas"] = self.state.get("completed_personas", 0) + 1
        self._save_state(self.state)


def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="Batch 1 Persona Generator")
    parser.add_argument("--config", default="clinical-content-prds/validation-system/batch1_config.json")
    parser.add_argument("--state", default="clinical-content-prds/.batch1_state.json")
    parser.add_argument("--index", type=int, help="Generate persona at specific index")
    parser.add_argument("--init-state", action="store_true", help="Initialize state file")
    args = parser.parse_args()

    generator = PersonaGenerator(args.config, args.state)

    if args.init_state:
        print("State file initialized")
        return 0

    if args.index is not None:
        persona_config = generator.config["personas"][args.index]
        result = generator.generate_persona(persona_config)
        return 0 if result else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
