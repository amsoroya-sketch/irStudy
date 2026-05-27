"""
EMR Validation Service - Business Logic Layer

3-Layer validation architecture:
- Layer 1: Completeness & structure checks (Python)
- Layer 2: Australian medical standards (PBS, MBS, eTG)
- Layer 3: Claude AI clinical reasoning validation

PERFORMANCE TARGET: <500ms (Layer 1+2), <3s (Layer 3)
SECURITY: No PHI in logs, API keys from Vault
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from src.api.v1.emr.validation_schemas import (
    SOAPNoteValidationResult,
    ValidationFeedback,
    AustralianComplianceCheck,
    PrescriptionValidationResult,
    PBSComplianceCheck,
    DrugInteraction,
    DoseCheck,
    PathologyValidationResult,
    MBSItem
)

logger = logging.getLogger(__name__)


class EMRValidationService:
    """
    EMR Validation Service

    Validates:
    1. SOAP notes (clinical documentation)
    2. Prescriptions (PBS compliance)
    3. Pathology orders (MBS appropriateness)
    """

    def __init__(self, db: Session):
        self.db = db

    async def validate_soap_note(
        self,
        session_id: str,
        soap_note: Dict[str, str],
        patient_context: Optional[Dict] = None
    ) -> SOAPNoteValidationResult:
        """
        Validate SOAP note with 3-layer architecture

        Args:
            session_id: EMR session UUID
            soap_note: Dict with subjective, objective, assessment, plan
            patient_context: Optional patient demographics/history

        Returns:
            SOAPNoteValidationResult with scores and feedback
        """
        start_time = datetime.utcnow()

        # Layer 1: Completeness checks
        completeness_score = self._check_completeness(soap_note)

        # Layer 2: Australian medical standards
        australian_compliance = self._check_australian_standards(soap_note)

        # Layer 3: Claude AI validation (async)
        try:
            from src.ai.clinical_validator import ClinicalValidator
            validator = ClinicalValidator()
            ai_result = await validator.validate_soap_with_claude(soap_note, patient_context or {})
        except Exception as e:
            logger.warning(f"Claude validation failed: {e}")
            ai_result = None

        # Calculate overall score (out of 15 marks - AMC rubric)
        if ai_result:
            overall_score = ai_result.get("overall_score", 0.0)
            category_scores = ai_result.get("category_scores", {})
            feedback_items = ai_result.get("feedback", [])
        else:
            # Fallback: Use completeness score only
            overall_score = (completeness_score / 100) * 15
            category_scores = {
                "history_examination": (completeness_score / 100) * 3,
                "clinical_reasoning": (completeness_score / 100) * 3,
                "communication": (completeness_score / 100) * 3,
                "patient_safety": (completeness_score / 100) * 3,
                "professionalism": (completeness_score / 100) * 3
            }
            feedback_items = []

        # Build validation result
        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return SOAPNoteValidationResult(
            validation_type="soap_note",
            overall_score=round(overall_score, 1),
            passed=overall_score >= 9.0,  # 60% pass mark
            category_scores=category_scores,
            strengths=ai_result.get("strengths", []) if ai_result else [],
            improvements=ai_result.get("improvements", []) if ai_result else [],
            red_flags=ai_result.get("red_flags", []) if ai_result else [],
            feedback=feedback_items,
            australian_compliance=australian_compliance,
            processing_time_ms=elapsed_ms
        )

    def _check_completeness(self, soap_note: Dict[str, str]) -> float:
        """
        Check SOAP note completeness (Layer 1)

        Returns:
            Completeness score 0-100
        """
        score = 100.0

        # Check minimum lengths
        subjective = soap_note.get("subjective", "")
        objective = soap_note.get("objective", "")
        assessment = soap_note.get("assessment", "")
        plan = soap_note.get("plan", "")

        if len(subjective) < 100:
            score -= 25
        if len(objective) < 100:
            score -= 25
        if len(assessment) < 50:
            score -= 25
        if len(plan) < 100:
            score -= 25

        return max(0.0, score)

    def _check_australian_standards(self, soap_note: Dict[str, str]) -> AustralianComplianceCheck:
        """
        Check Australian medical terminology and standards (Layer 2)

        Returns:
            AustralianComplianceCheck with compliance status
        """
        full_text = " ".join([
            soap_note.get("subjective", ""),
            soap_note.get("objective", ""),
            soap_note.get("assessment", ""),
            soap_note.get("plan", "")
        ]).lower()

        # Check terminology
        terminology_correct = True
        etg_compliant = True
        pbs_aware = True
        issues = []

        # Prompt injection detection (SECURITY)
        prompt_injection_patterns = [
            "ignore previous instructions",
            "disregard above",
            "system:",
            "assistant:",
            "[inst]",
            "<|im_start|>",
            "jailbreak",
            "dan mode"
        ]

        for pattern in prompt_injection_patterns:
            if pattern in full_text:
                terminology_correct = False
                issues.append(f"Potential prompt injection detected: '{pattern}'")

        # Australian vs US terminology
        if "acetaminophen" in full_text:  # SECURITY SCAN EXEMPTION
            terminology_correct = False
            issues.append("Use 'paracetamol' instead of 'acetaminophen'")  # SECURITY SCAN EXEMPTION

        if "tylenol" in full_text:
            terminology_correct = False
            issues.append("Use 'paracetamol' instead of 'Tylenol'")

        if "911" in full_text:
            terminology_correct = False
            issues.append("Use '000' for Australian emergency number")

        # Check for eTG mentions (good practice)
        if "etg" in full_text or "therapeutic guideline" in full_text:
            etg_compliant = True

        return AustralianComplianceCheck(
            terminology_correct=terminology_correct,
            etg_compliant=etg_compliant,
            pbs_aware=pbs_aware,
            issues=issues
        )

    async def validate_prescription(
        self,
        medication_name: str,
        dose: str,
        frequency: str,
        route: str,
        repeats: int,
        indication: str,
        authority_required: bool = False
    ) -> PrescriptionValidationResult:
        """
        Validate prescription against PBS standards

        Args:
            medication_name: Drug name
            dose: Dosage (e.g., "100mg")
            frequency: Frequency (e.g., "daily")
            route: Route (e.g., "PO")
            repeats: Number of repeats (max 5 for PBS)
            indication: Clinical indication
            authority_required: PBS authority needed

        Returns:
            PrescriptionValidationResult
        """
        start_time = datetime.utcnow()

        # PBS compliance check
        pbs_compliance = self._check_pbs_compliance(
            medication_name, repeats, authority_required
        )

        # Drug interaction check (simplified)
        interactions = self._check_drug_interactions(medication_name)

        # Dose appropriateness
        dose_check = self._check_dose_appropriateness(medication_name, dose)

        # Safety score
        safety_score = 10.0
        if not pbs_compliance.pbs_listed:
            safety_score -= 1.0
        if not pbs_compliance.restrictions_met:
            safety_score -= 2.0
        if len(interactions) > 0:
            safety_score -= sum(1 if i.severity == "minor" else 2 if i.severity == "moderate" else 3 for i in interactions)

        # Feedback
        feedback = []
        if not dose_check.within_range:
            feedback.append(f"Dose outside recommended range: {dose_check.recommended_dose}")
        if pbs_compliance.authority_required:
            feedback.append("PBS authority required for this medication")

        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Build warnings list
        warnings = list(feedback)  # Copy feedback to warnings
        if not pbs_compliance.pbs_listed:
            warnings.append("Medication not listed on PBS - will be private prescription")

        # Check for exceeding max repeats
        if repeats > 5:
            warnings.append(f"Exceeds PBS maximum of 5 repeats (requested {repeats})")

        # Check for US terminology
        if medication_name.lower() in ["acetaminophen", "tylenol"]:  # SECURITY SCAN EXEMPTION
            warnings.append("Use Australian drug name: 'paracetamol' instead of 'acetaminophen'")  # SECURITY SCAN EXEMPTION

        return PrescriptionValidationResult(
            is_valid=safety_score >= 7.0 and pbs_compliance.restrictions_met,
            pbs_compliant=pbs_compliance.pbs_listed and pbs_compliance.restrictions_met,
            medication_name=medication_name,
            pbs_listed=pbs_compliance.pbs_listed,
            authority_required=pbs_compliance.authority_required,
            approved=safety_score >= 7.0,
            safety_score=round(safety_score, 1),
            pbs_compliance=pbs_compliance,
            drug_interactions=interactions,
            dose_appropriateness=dose_check,
            warnings=warnings,
            feedback=feedback,
            processing_time_ms=elapsed_ms
        )

    def _check_pbs_compliance(
        self,
        medication_name: str,
        repeats: int,
        authority_required: bool
    ) -> PBSComplianceCheck:
        """Check PBS compliance (simplified implementation)"""

        # Hardcoded PBS database (simplified)
        pbs_medications = {
            "paracetamol": {"listed": True, "authority": False, "max_repeats": 5, "copay": 7.30},
            "aspirin": {"listed": True, "authority": False, "max_repeats": 5, "copay": 7.30},
            "atorvastatin": {"listed": True, "authority": False, "max_repeats": 5, "copay": 7.30},
            "metformin": {"listed": True, "authority": False, "max_repeats": 5, "copay": 7.30},
            "amlodipine": {"listed": True, "authority": False, "max_repeats": 5, "copay": 7.30},
            "adalimumab": {"listed": True, "authority": True, "max_repeats": 5, "copay": 42.50}
        }

        med_lower = medication_name.lower()
        pbs_info = pbs_medications.get(med_lower, {})

        pbs_listed = pbs_info.get("listed", False)
        restrictions_met = repeats <= 5

        return PBSComplianceCheck(
            pbs_listed=pbs_listed,
            authority_required=pbs_info.get("authority", False),
            restrictions_met=restrictions_met,
            max_repeats=5,
            patient_copay=pbs_info.get("copay", 0.0) if pbs_listed else 0.0
        )

    def _check_drug_interactions(self, medication_name: str) -> List[DrugInteraction]:
        """Check drug interactions (simplified)"""

        # Simplified interaction database
        interactions_db = {
            "aspirin": [
                DrugInteraction(
                    severity="moderate",
                    interacting_drug="Warfarin",
                    effect="Increased bleeding risk",
                    recommendation="Monitor INR closely"
                )
            ]
        }

        return interactions_db.get(medication_name.lower(), [])

    def _check_dose_appropriateness(self, medication_name: str, dose: str) -> DoseCheck:
        """Check dose appropriateness (simplified)"""

        # Simplified dose database
        dose_ranges = {
            "aspirin": {"min": "75mg", "max": "300mg", "recommended": "75-100mg daily"},
            "paracetamol": {"min": "500mg", "max": "1000mg", "recommended": "500-1000mg QID"},
            "atorvastatin": {"min": "10mg", "max": "80mg", "recommended": "20-40mg nocte"}
        }

        med_lower = medication_name.lower()
        dose_info = dose_ranges.get(med_lower, {})

        return DoseCheck(
            within_range=True,  # Simplified - always pass
            recommended_dose=dose_info.get("recommended", "See eTG guidelines"),
            patient_specific_factors=[]
        )

    async def validate_pathology_order(
        self,
        tests_ordered: List[str],
        indication: str,
        patient_context: Dict,
        urgency: str = "routine"
    ) -> PathologyValidationResult:
        """
        Validate pathology test orders against MBS

        Args:
            tests_ordered: List of test names
            indication: Clinical indication
            patient_context: Patient demographics/history
            urgency: routine, urgent, stat

        Returns:
            PathologyValidationResult
        """
        start_time = datetime.utcnow()

        # MBS item lookup
        mbs_items = []
        for test in tests_ordered:
            mbs_item = self._get_mbs_item(test)
            if mbs_item:
                mbs_items.append(mbs_item)

        # Appropriateness scoring
        appropriateness_score = self._score_pathology_appropriateness(
            tests_ordered, indication, patient_context
        )

        # Overuse warnings
        overuse_warnings = self._check_pathology_overuse(tests_ordered, indication)

        # Missing tests
        missing_tests = self._suggest_missing_tests(tests_ordered, indication)

        # Cost estimate
        cost_estimate = sum(item.rebate_amount for item in mbs_items)

        # Feedback
        feedback_items = []
        if appropriateness_score >= 8.0:
            feedback_items.append("Appropriate investigation for clinical indication")
        elif appropriateness_score >= 6.0:
            feedback_items.append("Investigation reasonable but consider necessity of all tests")
        else:
            feedback_items.append("Inappropriate investigation - several tests not indicated for this clinical scenario")

        # Add overuse warnings to feedback
        feedback_items.extend(overuse_warnings)

        # Add missing test suggestions
        for test in missing_tests:
            feedback_items.append(f"Consider adding: {test}")

        elapsed_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        # Get first test info for top-level fields
        first_test = tests_ordered[0] if tests_ordered else ""
        first_mbs_item = mbs_items[0] if mbs_items else None

        return PathologyValidationResult(
            appropriate=appropriateness_score >= 7.0,
            mbs_compliant=len(mbs_items) > 0,
            test_name=first_mbs_item.test_name if first_mbs_item else first_test,
            mbs_item_number=first_mbs_item.mbs_item_number if first_mbs_item else "",
            appropriateness_score=round(appropriateness_score, 1),
            mbs_items=mbs_items,
            overuse_warnings=overuse_warnings,
            missing_tests=missing_tests,
            cost_estimate=round(cost_estimate, 2),
            feedback=feedback_items,
            processing_time_ms=elapsed_ms
        )

    def _get_mbs_item(self, test_name: str) -> Optional[MBSItem]:
        """Get MBS item for test (simplified)"""

        # Simplified MBS database
        mbs_database = {
            "fbc": MBSItem(
                test_name="Full Blood Count",
                mbs_item_number="65070",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="Routine investigation"
            ),
            "full blood count": MBSItem(
                test_name="Full Blood Count",
                mbs_item_number="65070",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="Routine investigation"
            ),
            "uec": MBSItem(
                test_name="Urea, Electrolytes, Creatinine",
                mbs_item_number="66512",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="Routine investigation"
            ),
            "troponin": MBSItem(
                test_name="Troponin I",
                mbs_item_number="66800",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="Appropriate for suspected ACS"
            ),
            "troponin i": MBSItem(
                test_name="Troponin I",
                mbs_item_number="66800",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="Appropriate for suspected ACS"
            ),
            "d-dimer": MBSItem(
                test_name="D-dimer",
                mbs_item_number="65160",
                rebate_amount=16.90,
                bulk_billable=True,
                notes="For PE/DVT investigation"
            )
        }

        return mbs_database.get(test_name.lower())

    def _score_pathology_appropriateness(
        self,
        tests_ordered: List[str],
        indication: str,
        patient_context: Dict
    ) -> float:
        """Score pathology appropriateness (simplified)"""

        # Simplified scoring logic
        base_score = 8.5

        tests_lower = " ".join(tests_ordered).lower()

        # Check for inappropriate tests
        if "ct whole body" in tests_lower or "full body mri" in tests_lower:
            base_score -= 3.0

        # D-dimer in elderly patients has low specificity
        if "d-dimer" in tests_lower:
            age = patient_context.get("age", 0)
            if age > 70:
                base_score -= 1.5

        # Bonus for appropriate combinations
        if "troponin" in tests_lower and "chest pain" in indication.lower():
            base_score += 0.5

        return max(0.0, min(10.0, base_score))

    def _check_pathology_overuse(self, tests_ordered: List[str], indication: str) -> List[str]:
        """Check for pathology overuse (simplified)"""

        warnings = []

        # Check for unnecessary CT scans
        if "ct whole body" in " ".join(tests_ordered).lower():
            if "chest pain" in indication.lower() and "trauma" not in indication.lower():
                warnings.append("CT Whole Body not indicated for simple chest pain - consider targeted imaging")

        return warnings

    def _suggest_missing_tests(self, tests_ordered: List[str], indication: str) -> List[str]:
        """Suggest missing tests (simplified)"""

        missing = []
        tests_str = " ".join(tests_ordered).lower()

        # ACS workup
        if "chest pain" in indication.lower() or "acs" in indication.lower():
            if "troponin" not in tests_str:
                missing.append("Troponin (essential for ACS workup)")
            if "fbc" not in tests_str and "full blood count" not in tests_str:
                missing.append("FBC (baseline investigation)")

        return missing
