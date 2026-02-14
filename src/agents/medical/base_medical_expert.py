#!/usr/bin/env python3
"""
Base Medical Expert Agent
Common functionality for all medical specialist agents (MED-001 to MED-010)
"""

from abc import abstractmethod
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent, AgentTask, AgentRole
import re


class BaseMedicalExpert(BaseAgent):
    """
    Base class for all medical expert agents.

    Provides common functionality:
    - Australian terminology validation
    - Citation format validation
    - Drug name validation (Australian vs American)
    - Unit validation (SI units)
    - MCQ/OSCE generation templates
    - RAG integration patterns
    """

    # Australian medical terminology mappings
    AUSTRALIAN_TERMS = {
        'pediatric': 'paediatric',
        'anesthesia': 'anaesthesia',
        'esophagus': 'oesophagus',
        'hemoglobin': 'haemoglobin',
        'anemia': 'anaemia',
        'color': 'colour',
        'estrogen': 'oestrogen',
        'ER': 'Emergency Department',
        'PCP': 'GP',
        'primary care physician': 'general practitioner',
        'attending': 'specialist',
        'consult': 'referral',
    }

    # American drug names → Australian equivalents
    AUSTRALIAN_DRUG_NAMES = {
        'acetaminophen': 'paracetamol',
        'tylenol': 'panadol',
        'epinephrine': 'adrenaline',
        'albuterol': 'salbutamol',
        'furosemide': 'frusemide',  # Australian spelling preference
    }

    # Required medical units
    VALID_UNITS = [
        'mg', 'mcg', 'g', 'kg', 'mL', 'L',
        'mmol/L', 'mg/dL', 'IU', 'units',
        'mmHg', 'bpm', 'breaths/min',
        'mg/kg', 'mcg/kg', 'mL/kg'
    ]

    def __init__(self, metadata, rag_system=None):
        """
        Initialize medical expert agent.

        Args:
            metadata: AgentMetadata with agent details
            rag_system: MedicalRAGSystem instance for citation-backed responses
        """
        super().__init__(metadata)
        self.rag = rag_system
        self._register_common_medical_tools()

    def _register_common_medical_tools(self):
        """Register tools common to all medical experts"""
        self.register_tool(
            "generate_mcq",
            self._generate_mcq,
            "Generate MCQ question with Australian guideline compliance"
        )
        self.register_tool(
            "generate_osce",
            self._generate_osce_scenario,
            "Generate OSCE scenario for AMC Clinical Exam"
        )
        self.register_tool(
            "generate_clinical_case",
            self._generate_clinical_case,
            "Generate clinical case with differential diagnosis"
        )
        self.register_tool(
            "validate_citation",
            self._validate_citation_format,
            "Validate citation has exact page/section numbers"
        )

    @abstractmethod
    def _get_specialty_sources(self) -> List[str]:
        """
        Return list of primary sources for this specialty.

        Example:
            ['Therapeutic Guidelines: Cardiovascular',
             'Talley & O\'Connor\'s Clinical Examination']
        """
        pass

    @abstractmethod
    def _get_specialty_topics(self) -> List[str]:
        """
        Return list of high-yield topics for this specialty.

        Example:
            ['Acute Coronary Syndrome', 'Heart Failure', 'Arrhythmias']
        """
        pass

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute medical expert task"""
        self.logger.info(f"Executing medical task: {task.title}")

        try:
            task_type = task.metadata.get('type', 'general')

            if task_type == 'generate_mcq':
                result = self._generate_mcq(task)
            elif task_type == 'generate_osce':
                result = self._generate_osce_scenario(task)
            elif task_type == 'generate_clinical_case':
                result = self._generate_clinical_case(task)
            elif task_type == 'validate_content':
                result = self._validate_medical_content(task)
            else:
                result = self._handle_general_query(task)

            return {
                'status': 'success',
                'output': result,
                'artifacts': [],
                'validation_passed': True
            }

        except Exception as e:
            self.logger.error(f"Task execution failed: {e}", exc_info=True)
            return {
                'status': 'error',
                'error': str(e),
                'error_type': type(e).__name__
            }

    def validate_output(self, task: AgentTask, output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Validate medical accuracy and Australian compliance.

        Checks:
        1. Citation format (exact page/section numbers)
        2. Australian terminology (no American terms)
        3. Australian drug names (no American drug names)
        4. SI units (proper medical units)
        5. Red flags identified (for emergency conditions)
        """
        errors = []
        result = output.get('output', {})

        # Check 1: Citation validation
        if not self._has_valid_citations(result):
            errors.append("Missing or invalid citations (must include page/section numbers)")

        # Check 2: Australian terminology
        american_terms = self._find_american_terminology(result)
        if american_terms:
            errors.append(f"Contains American terminology: {', '.join(american_terms)}")

        # Check 3: Australian drug names
        american_drugs = self._find_american_drug_names(result)
        if american_drugs:
            errors.append(f"Contains American drug names: {', '.join(american_drugs)}")

        # Check 4: Unit validation
        if 'dosage' in result or 'dose' in str(result).lower():
            if not self._has_proper_units(result):
                errors.append("Drug dosages must include proper units (mg, mcg, mL, etc.)")

        # Check 5: Red flag validation (for emergency scenarios)
        if self._is_emergency_scenario(task) and not result.get('red_flags'):
            errors.append("Emergency scenario must identify red flags")

        # Check 6: Emergency number validation
        if '911' in str(result):
            errors.append("Use Australian emergency number '000' not '911'")

        return len(errors) == 0, errors

    def _has_valid_citations(self, data: Dict) -> bool:
        """Check if citations have exact page/section numbers"""
        citations = data.get('citations') or data.get('references') or []

        if not citations:
            citation_text = str(data)
            # Look for citation patterns in text
            citation_patterns = [
                r'\(.*?p\.\s*\d+.*?\)',  # Book with page number
                r'\(.*?Section\s+\d+\..*?\)',  # eTG with section number
            ]

            has_citation = any(
                re.search(pattern, citation_text)
                for pattern in citation_patterns
            )

            return has_citation

        # Check each citation
        for citation in citations:
            citation_str = str(citation)
            # Must have page number (p.123) OR section number (Section 2.3)
            has_page = 'p.' in citation_str and re.search(r'p\.\s*\d+', citation_str)
            has_section = 'Section' in citation_str and re.search(r'Section\s+\d+', citation_str)

            if not (has_page or has_section):
                return False

        return True

    def _find_american_terminology(self, data: Dict) -> List[str]:
        """Find American medical terminology in output"""
        found_terms = []
        text = str(data).lower()

        for american_term, australian_term in self.AUSTRALIAN_TERMS.items():
            if american_term.lower() in text:
                found_terms.append(f"{american_term} (use {australian_term})")

        return found_terms

    def _find_american_drug_names(self, data: Dict) -> List[str]:
        """Find American drug names in output"""
        found_drugs = []
        text = str(data).lower()

        for american_drug, australian_drug in self.AUSTRALIAN_DRUG_NAMES.items():
            if american_drug.lower() in text:
                found_drugs.append(f"{american_drug} (use {australian_drug})")

        return found_drugs

    def _has_proper_units(self, data: Any) -> bool:
        """Check if dosages have proper units"""
        text = str(data)

        # Check for at least one valid unit
        has_unit = any(unit in text for unit in self.VALID_UNITS)

        # Check for numbers without units (dosage error)
        # Pattern: number followed by space/newline without unit
        dosage_pattern = r'\d+\s*(?:mg|mcg|g|mL|L|IU|units|mmol)'
        has_dosage_with_unit = re.search(dosage_pattern, text)

        return has_unit and has_dosage_with_unit is not None

    def _is_emergency_scenario(self, task: AgentTask) -> bool:
        """Check if task involves emergency scenario"""
        emergency_keywords = [
            'emergency', 'acute', 'cardiac arrest', 'anaphylaxis',
            'stroke', 'trauma', 'seizure', 'sepsis', 'MI', 'PE'
        ]

        text = (task.title + ' ' + task.description).lower()
        return any(keyword in text for keyword in emergency_keywords)

    def _validate_citation_format(self, citation: str) -> tuple[bool, str]:
        """
        Validate citation format.

        Valid formats:
        - (Talley & O'Connor's Clinical Examination, 8th ed, p.145)
        - (Therapeutic Guidelines: Cardiovascular, Section 5.2.1, 2024)

        Invalid:
        - (eTG 2024) - too vague
        - (Talley) - no page number
        """
        # Check for book citation with page
        book_pattern = r'\(.*?,.*?p\.\s*\d+.*?\)'
        if re.match(book_pattern, citation):
            return True, "Valid book citation with page number"

        # Check for eTG citation with section
        etg_pattern = r'\(Therapeutic Guidelines:.*?Section\s+\d+.*?\)'
        if re.match(etg_pattern, citation):
            return True, "Valid eTG citation with section number"

        return False, "Citation must include page number (books) or section number (eTG)"

    def _generate_mcq(self, task: AgentTask) -> Dict[str, Any]:
        """
        Generate MCQ question (to be customized by each specialty).

        Override this in subclasses for specialty-specific generation.
        """
        topic = task.metadata.get('topic', 'general')
        difficulty = task.metadata.get('difficulty', 'medium')

        self.logger.info(f"Generating MCQ for topic: {topic}, difficulty: {difficulty}")

        # This is a template - subclasses should override with RAG integration
        return {
            'question_stem': f"Template MCQ question about {topic}",
            'options': {
                'A': 'Option A',
                'B': 'Option B',
                'C': 'Option C',
                'D': 'Option D',
                'E': 'Option E',
            },
            'correct_answer': 'C',
            'explanation': f"Template explanation for {topic}",
            'citations': [],
            'specialty': self.metadata.specializations[0] if self.metadata.specializations else 'general',
            'difficulty': difficulty,
            'amc_frequency': 'medium',
        }

    def _generate_osce_scenario(self, task: AgentTask) -> Dict[str, Any]:
        """Generate OSCE scenario (template - override in subclasses)"""
        station_type = task.metadata.get('station_type', 'history_taking')

        return {
            'station_type': station_type,
            'specialty': self.metadata.specializations[0] if self.metadata.specializations else 'general',
            'time_limit': 8,
            'candidate_instructions': 'Template candidate instructions',
            'actor_instructions': 'Template actor instructions',
            'examiner_instructions': 'Template examiner instructions',
            'marking_criteria': {},
        }

    def _generate_clinical_case(self, task: AgentTask) -> Dict[str, Any]:
        """Generate clinical case (template - override in subclasses)"""
        topic = task.metadata.get('topic', 'general')

        return {
            'title': f"Clinical case: {topic}",
            'presentation': 'Template presentation',
            'history': 'Template history',
            'examination': 'Template examination findings',
            'investigations': 'Template investigations',
            'differential_diagnosis': [],
            'management': 'Template management',
            'citations': [],
        }

    def _validate_medical_content(self, task: AgentTask) -> Dict[str, Any]:
        """Validate medical content against guidelines"""
        content = task.metadata.get('content', {})

        validation_result = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
        }

        # Run validation checks
        is_valid, errors = self.validate_output(task, {'output': content})

        validation_result['is_valid'] = is_valid
        validation_result['errors'] = errors

        return validation_result

    def _handle_general_query(self, task: AgentTask) -> Dict[str, Any]:
        """Handle general medical query"""
        self.logger.info(f"Handling general query: {task.description}")

        # This would integrate with RAG system in production
        return {
            'answer': 'General medical query response',
            'citations': [],
            'confidence': 0.0,
        }
