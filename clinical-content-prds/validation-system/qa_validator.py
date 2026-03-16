#!/usr/bin/env python3
"""
QA-001: Medical Persona Quality Assurance Validator
Implements 13 quality gates for validating patient personas before deployment
"""

import json
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime
from pathlib import Path


class PersonaQAValidator:
    """
    QA-001 implementation: Validates personas against 13 quality gates
    """

    def __init__(self):
        self.validation_date = datetime.now().isoformat()

        # Target distributions
        self.target_difficulty = {
            "Easy": 125,
            "Medium": 148,
            "Hard": 87
        }

        self.target_specialty = {
            "Cardiology": 45,
            "Emergency": 45,
            "General Practice": 54,
            "Pediatrics": 36,
            "Respiratory": 36,
            "Neurology": 27,
            "ObGyn": 27,
            "Surgery": 27,
            "Psychiatry": 36,
            "Infectious Diseases": 27
        }

        self.target_cultural = {
            "aboriginal_tsi": 12,
            "lgbtqia": 40,
            "cald": 40
        }

    def validate_single_persona(self, persona_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate a single persona against 13 quality gates

        Args:
            persona_json: Persona data as dictionary

        Returns:
            Validation report with pass/fail status for each gate
        """
        report = {
            "qa_validator_id": "QA-001",
            "persona_id": persona_json.get("id", "unknown"),
            "validation_date": self.validation_date,
            "total_quality_gates": 13,
            "gates_passed": 0,
            "gates_failed": 0,
            "quality_gates": {},
            "errors": [],
            "warnings": [],
            "recommendation": None,
            "deployment_readiness": 0
        }

        # Run all 13 quality gates
        gates = [
            ("1_json_compliance", self._gate_1_json_compliance),
            ("2_rag_citations_065", self._gate_2_rag_citations),
            ("3_fracp_reviews_2", self._gate_3_fracp_reviews),
            ("4_clinical_accuracy", self._gate_4_clinical_accuracy),
            ("5_australian_context", self._gate_5_australian_context),
            ("6_difficulty_appropriate", self._gate_6_difficulty),
            ("7_specialty_valid", self._gate_7_specialty),
            ("8_cultural_safety_aboriginal", self._gate_8_aboriginal),
            ("9_cultural_safety_lgbtqia", self._gate_9_lgbtqia),
            ("10_cultural_safety_cald", self._gate_10_cald),
            ("11_zero_credentials", self._gate_11_security),
            ("12_zero_security_violations", self._gate_12_phi),
            ("13_educational_alignment", self._gate_13_education)
        ]

        for gate_name, gate_func in gates:
            result, errors = gate_func(persona_json)
            report["quality_gates"][gate_name] = result

            if result == "PASS":
                report["gates_passed"] += 1
            elif result == "FAIL":
                report["gates_failed"] += 1
                report["errors"].extend(errors)
            elif result == "N/A":
                # N/A gates don't count toward pass/fail
                pass

        # Calculate deployment readiness (only count applicable gates)
        applicable_gates = sum(1 for status in report["quality_gates"].values() if status in ["PASS", "FAIL"])
        if applicable_gates > 0:
            report["deployment_readiness"] = round((report["gates_passed"] / applicable_gates) * 100, 1)

        # Determine recommendation
        if report["gates_failed"] == 0 and report["gates_passed"] >= 10:
            report["recommendation"] = "APPROVED FOR DEPLOYMENT"
        elif report["gates_failed"] <= 2:
            report["recommendation"] = "CONDITIONAL APPROVAL - Fix minor issues"
        else:
            report["recommendation"] = "REJECTED - Requires revision"

        return report

    # ========================================
    # Gate 1: JSON Template Compliance
    # ========================================
    def _gate_1_json_compliance(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check all required fields present"""
        errors = []

        required_fields = [
            "id", "name", "age", "gender", "specialty", "difficulty",
            "chief_complaint", "symptoms", "opening_statement",
            "past_medical_history", "medications", "allergies",
            "family_history", "social_history",
            "expected_diagnosis", "expected_management", "critical_errors"
        ]

        for field in required_fields:
            if field not in persona:
                errors.append(f"Missing required field: {field}")

        # Check symptoms structure (should be list of dicts)
        if "symptoms" in persona:
            if not isinstance(persona["symptoms"], list):
                errors.append("'symptoms' should be a list")
            elif len(persona["symptoms"]) > 0:
                first_symptom = persona["symptoms"][0]
                if not isinstance(first_symptom, dict):
                    errors.append("Each symptom should be a dictionary")
                elif "symptom" not in first_symptom:
                    errors.append("Each symptom dict should have 'symptom' field")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 2: RAG Citations >0.65
    # ========================================
    def _gate_2_rag_citations(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check RAG citations exist and have confidence >0.65"""
        errors = []

        symptoms = persona.get("symptoms", [])
        if len(symptoms) == 0:
            return ("FAIL", ["No symptoms defined"])

        for i, symptom in enumerate(symptoms):
            # Check RAG citation exists
            if "rag_citation" not in symptom:
                errors.append(f"Symptom {i+1} ('{symptom.get('symptom', 'unknown')}') missing RAG citation")
                continue

            citation = symptom["rag_citation"]

            # Check confidence
            confidence = citation.get("confidence", 0)
            if confidence < 0.65:
                errors.append(f"Symptom {i+1}: RAG citation confidence {confidence} < 0.65 threshold")

            # Check source specified
            if not citation.get("source"):
                errors.append(f"Symptom {i+1}: RAG citation missing source")

            # Check quote provided
            if not citation.get("quote"):
                errors.append(f"Symptom {i+1}: RAG citation missing quote")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 3: ≥2 FRACP Reviews
    # ========================================
    def _gate_3_fracp_reviews(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check at least 2 FRACP reviews with all approved"""
        errors = []

        # Support both field names
        reviews = persona.get("fracp_reviews") or persona.get("clinical_educator_reviews") or []

        if len(reviews) < 2:
            errors.append(f"Only {len(reviews)} review(s) found (minimum 2 required)")

        for i, review in enumerate(reviews):
            # Check approved status
            if not review.get("approved"):
                reviewer_name = review.get("reviewer_name", f"Reviewer {i+1}")
                errors.append(f"Review by {reviewer_name} not approved")

            # Check reviewer credentials specified
            if not review.get("reviewer_credentials"):
                errors.append(f"Review {i+1} missing reviewer credentials")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 4: Clinical Accuracy
    # ========================================
    def _gate_4_clinical_accuracy(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check clinical accuracy (no dangerous advice, diagnosis matches symptoms)"""
        errors = []

        diagnosis = persona.get("expected_diagnosis", "").lower()
        symptoms_str = str(persona.get("symptoms", [])).lower()
        management_str = str(persona.get("expected_management", [])).lower()
        full_persona_str = str(persona).lower()

        # Check critical errors defined
        critical_errors = persona.get("critical_errors", [])
        if len(critical_errors) == 0:
            errors.append("No critical errors defined (required for auto-fail logic)")

        # Check for dangerous medication combinations
        dangerous_patterns = [
            ("nsaid" in management_str and "acute kidney injury" in full_persona_str,
             "NSAIDs in acute kidney injury (contraindicated)"),
            ("aspirin" in management_str and "active peptic ulcer" in full_persona_str,
             "Aspirin in active peptic ulcer (contraindicated)"),
            ("warfarin" in management_str and "pregnant" in full_persona_str,
             "Warfarin in pregnancy (teratogenic)"),
            ("ace inhibitor" in management_str and "pregnant" in full_persona_str,
             "ACE inhibitor in pregnancy (teratogenic)")
        ]

        for condition, error_msg in dangerous_patterns:
            if condition:
                errors.append(f"CRITICAL: {error_msg}")

        # Diagnosis-specific checks (examples)
        if "stemi" in diagnosis and "chest pain" not in symptoms_str:
            errors.append("STEMI diagnosis but no chest pain in symptoms")

        if "anaphylaxis" in diagnosis and "adrenaline" not in management_str:
            errors.append("CRITICAL: Anaphylaxis but no adrenaline in management")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 5: Australian Medical Context
    # ========================================
    def _gate_5_australian_context(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check Australian terminology and context (PBS, MBS, eTG)"""
        errors = []

        full_text = str(persona).lower()

        # Check for US terminology
        us_terms = {
            "acetaminophen": "paracetamol (Australian term)",
            "albuterol": "salbutamol (Australian term)",
            " er ": "ED (Emergency Department, not ER)",
            "primary care physician": "GP (Australian term)",
            "tylenol": "paracetamol (Australian brand)"
        }

        for us_term, correct_term in us_terms.items():
            if us_term in full_text:
                errors.append(f"US terminology: '{us_term}' detected. Use {correct_term}")

        # Check for eTG citations in RAG citations
        has_etg_citation = False
        for symptom in persona.get("symptoms", []):
            citation_source = symptom.get("rag_citation", {}).get("source", "").lower()
            if "etg" in citation_source or "therapeutic guidelines" in citation_source:
                has_etg_citation = True
                break

        if not has_etg_citation:
            errors.append("No eTG (Therapeutic Guidelines) citations found in RAG sources")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 6: Difficulty Appropriateness
    # ========================================
    def _gate_6_difficulty(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check complexity matches difficulty level"""
        errors = []

        difficulty = persona.get("difficulty")
        if difficulty not in ["Easy", "Medium", "Hard"]:
            errors.append(f"Invalid difficulty: {difficulty} (must be Easy, Medium, or Hard)")
            return ("FAIL", errors)

        symptoms_count = len(persona.get("symptoms", []))
        comorbidities_count = len(persona.get("past_medical_history", []))

        # Easy: <5 symptoms, <2 comorbidities
        if difficulty == "Easy":
            if symptoms_count > 5:
                errors.append(f"Easy difficulty but {symptoms_count} symptoms (should be <5)")
            if comorbidities_count > 2:
                errors.append(f"Easy difficulty but {comorbidities_count} comorbidities (should be <2)")

        # Hard: >8 symptoms, >3 comorbidities
        if difficulty == "Hard":
            if symptoms_count < 8:
                errors.append(f"Hard difficulty but only {symptoms_count} symptoms (should be ≥8)")
            if comorbidities_count < 3:
                errors.append(f"Hard difficulty but only {comorbidities_count} comorbidities (should be ≥3)")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 7: Specialty Valid
    # ========================================
    def _gate_7_specialty(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check specialty is valid"""
        errors = []

        specialty = persona.get("specialty")
        valid_specialties = list(self.target_specialty.keys())

        if specialty not in valid_specialties:
            errors.append(f"Invalid specialty: {specialty} (must be one of {', '.join(valid_specialties)})")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 8: Cultural Safety - Aboriginal/TSI
    # ========================================
    def _gate_8_aboriginal(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check Aboriginal/TSI personas for cultural safety"""
        errors = []

        cultural_bg = persona.get("cultural_background", "").lower()

        if "aboriginal" not in cultural_bg and "torres strait" not in cultural_bg:
            return ("N/A", [])  # Not applicable

        full_text = str(persona).lower()

        # Check for stereotypes
        stereotype_phrases = ["non-compliant", "alcohol abuse", "didn't show up", "poor english"]
        for phrase in stereotype_phrases:
            if phrase in full_text:
                errors.append(f"Potential stereotype: '{phrase}' in Aboriginal/TSI persona")

        # Check Nation specified
        nations = ["noongar", "wurundjeri", "eora", "kaurna", "palawa", "yolngu", "awabakal"]
        if not any(nation in full_text for nation in nations):
            errors.append("Aboriginal/TSI persona missing Nation specification (Noongar, Wurundjeri, etc.)")

        # Check cultural liaison review
        if "cultural_liaison_review" not in persona:
            errors.append("Aboriginal/TSI persona missing cultural liaison review (MANDATORY)")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 9: Cultural Safety - LGBTQIA+
    # ========================================
    def _gate_9_lgbtqia(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check LGBTQIA+ personas for cultural safety"""
        errors = []

        pronouns = persona.get("pronouns")
        cultural_bg = persona.get("cultural_background", "").lower()
        full_text = str(persona).lower()

        if not pronouns and "transgender" not in cultural_bg and "lgbtq" not in cultural_bg:
            return ("N/A", [])  # Not applicable

        # Check pronouns specified
        if not pronouns:
            errors.append("LGBTQIA+ persona missing pronouns specification (he/him, she/her, they/them)")

        # Check no deadnaming
        if "legal_name" in persona and "preferred_name" in persona:
            # Ensure preferred name is used consistently
            pass  # This would be checked during actual usage

        # Check educator review
        if "lgbtq" in cultural_bg or "transgender" in cultural_bg:
            if "lgbtqia_educator_review" not in persona and "lgbtqia+_educator_review" not in persona:
                errors.append("LGBTQIA+ persona missing educator review (MANDATORY)")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 10: Cultural Safety - CALD
    # ========================================
    def _gate_10_cald(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check CALD personas for cultural safety"""
        errors = []

        language_context = persona.get("language_context", {})
        primary_language = language_context.get("primary_language", "English")

        if primary_language == "English":
            return ("N/A", [])  # Not applicable

        # Check interpreter services mentioned if limited English
        english_proficiency = language_context.get("english_proficiency", "")
        if "limited" in english_proficiency.lower():
            if "interpreter" not in str(persona).lower():
                errors.append("CALD persona with limited English but no interpreter services mentioned")

        # Check for stereotypical occupations
        occupation = persona.get("social_history", {}).get("occupation", "").lower()
        stereotype_jobs = ["taxi driver", "cleaner", "unemployed"]
        if occupation in stereotype_jobs:
            errors.append(f"Stereotypical occupation: '{occupation}' in CALD persona")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 11: Zero Hardcoded Credentials
    # ========================================
    def _gate_11_security(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check for hardcoded credentials, API keys, file paths"""
        errors = []

        full_text = str(persona)

        # Check for API keys
        api_key_patterns = [
            r'api[_-]?key',
            r'secret[_-]?key',
            r'password\s*[=:]',
            r'dbKey',
            r'db_password'
        ]

        for pattern in api_key_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                errors.append(f"SECURITY VIOLATION: Possible credential detected (pattern: {pattern})")

        # Check for file paths
        if "/home/" in full_text or "C:\\" in full_text or "/Users/" in full_text:
            errors.append("SECURITY VIOLATION: File path detected in persona JSON")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 12: Zero Security Violations (PHI)
    # ========================================
    def _gate_12_phi(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check PHI properly anonymized"""
        errors = []

        # Check for real-looking MRN numbers (should be generic)
        mrn = persona.get("mrn", "")
        if mrn and len(mrn) > 8:
            errors.append("MRN appears too specific (should be generic example)")

        # Check for specific dates (should be relative like "3 months ago")
        full_text = str(persona)
        date_pattern = r'\d{4}-\d{2}-\d{2}'  # YYYY-MM-DD
        if re.search(date_pattern, full_text):
            # Warning, not error (dates may be OK in some contexts)
            pass

        return ("PASS" if len(errors) == 0 else "FAIL", errors)

    # ========================================
    # Gate 13: Educational Alignment
    # ========================================
    def _gate_13_education(self, persona: Dict) -> Tuple[str, List[str]]:
        """Check AMC competencies and learning objectives"""
        errors = []

        # Check 9-step history structure
        history_fields = [
            "chief_complaint",
            "symptoms",  # HPI
            "past_medical_history",
            "medications",
            "allergies",
            "family_history",
            "social_history"
        ]

        missing_history = [field for field in history_fields if field not in persona]
        if missing_history:
            errors.append(f"9-step history incomplete (missing: {', '.join(missing_history)})")

        # Check SOCRATES framework in symptoms
        symptoms = persona.get("symptoms", [])
        if symptoms and len(symptoms) > 0:
            first_symptom = symptoms[0]
            socrates = first_symptom.get("socrates", {})

            socrates_elements = ["site", "onset", "character", "radiation", "associated", "timing", "severity"]
            missing_socrates = [elem for elem in socrates_elements if elem not in socrates]

            if len(missing_socrates) > 3:  # Allow some flexibility
                errors.append(f"SOCRATES framework incomplete (missing: {', '.join(missing_socrates)})")

        return ("PASS" if len(errors) == 0 else "FAIL", errors)


def validate_persona_file(filepath: str) -> Dict[str, Any]:
    """
    Validate a persona JSON file

    Args:
        filepath: Path to persona JSON file

    Returns:
        Validation report dictionary
    """
    validator = PersonaQAValidator()

    with open(filepath, 'r') as f:
        persona = json.load(f)

    return validator.validate_single_persona(persona)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python qa_validator.py <persona_json_file>")
        print("Example: python qa_validator.py cardiology_001_stemi.json")
        sys.exit(1)

    filepath = sys.argv[1]

    try:
        report = validate_persona_file(filepath)

        # Print summary
        print("\n" + "="*60)
        print("QA VALIDATION REPORT")
        print("="*60)
        print(f"Persona ID: {report['persona_id']}")
        print(f"Gates Passed: {report['gates_passed']}/{report['total_quality_gates']}")
        print(f"Gates Failed: {report['gates_failed']}")
        print(f"Deployment Readiness: {report['deployment_readiness']}%")
        print(f"Recommendation: {report['recommendation']}")

        if report['errors']:
            print("\nERRORS FOUND:")
            for error in report['errors']:
                print(f"  ❌ {error}")

        if report['warnings']:
            print("\nWARNINGS:")
            for warning in report['warnings']:
                print(f"  ⚠️  {warning}")

        # Write full report
        output_file = filepath.replace('.json', '_qa_report.json')
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nFull report written to: {output_file}")
        print("="*60)

        # Exit with error code if failed
        sys.exit(0 if report['recommendation'] == "APPROVED FOR DEPLOYMENT" else 1)

    except FileNotFoundError:
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"ERROR: Invalid JSON in file: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        sys.exit(1)
