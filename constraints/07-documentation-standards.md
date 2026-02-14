# Documentation Standards

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Documentation Standards

### 7.1 Docstring Format (MANDATORY)

**Use Google-style docstrings for ALL functions, classes, and methods:**

```python
def generate_mcq(
    self,
    topic: str,
    difficulty: str = "medium",
    num_options: int = 5,
    context: Optional[str] = None
) -> Dict[str, Any]:
    """
    Generate a medical MCQ question on specified topic.

    This method uses the configured LLM to generate a clinically accurate
    multiple-choice question following Australian medical standards and
    Therapeutic Guidelines. Questions are automatically validated for
    Australian terminology, proper citations, and clinical accuracy.

    Args:
        topic: Medical topic for the question (e.g., "acute coronary syndrome").
            Should be specific enough to generate focused content.
        difficulty: Question difficulty level. Must be one of: "easy", "medium", "hard".
            - "easy": Basic recall and recognition
            - "medium": Application and analysis
            - "hard": Synthesis and evaluation
            Default: "medium"
        num_options: Number of answer options (2-5). Default: 5 (A-E format).
        context: Optional additional context from RAG system or textbooks.
            If provided, will be incorporated into question generation.

    Returns:
        Dictionary containing:
            - question_id (str): Unique identifier (format: "MCQ-SPEC-XXX")
            - specialty (str): Medical specialty (e.g., "cardiology")
            - topic (str): Topic as provided
            - difficulty (str): Difficulty level
            - stem (str): Question text with clinical vignette
            - options (Dict[str, str]): Answer options (A-E)
            - correct_answer (str): Correct option letter
            - explanation (str): Detailed explanation with reasoning
            - citation (str): Source reference (Therapeutic Guidelines, etc.)
            - red_flags (List[str]): Any red flag conditions identified
            - learning_points (List[str]): Key learning points

    Raises:
        ValueError: If topic is empty, difficulty is invalid, or num_options not in 2-5
        LLMError: If LLM generation fails after all retry attempts
        ValidationError: If generated question fails validation checks

    Example:
        >>> agent = CardiologyExpert()
        >>> question = agent.generate_mcq(
        ...     topic="acute coronary syndrome",
        ...     difficulty="medium",
        ...     num_options=5
        ... )
        >>> print(question['stem'])
        "A 55-year-old man presents to ED with 30 minutes of crushing
        retrosternal chest pain radiating to left arm..."
        >>> print(question['correct_answer'])
        "B"
        >>> print(question['citation'])
        "Therapeutic Guidelines: Cardiovascular, Section 3.1.2 (2024)"

    Note:
        - Questions are automatically validated for Australian terminology
        - All drug names are checked against PBS and Australian formulary
        - Citations are verified against Therapeutic Guidelines catalog
        - Red flag conditions automatically trigger emergency action recommendations

    See Also:
        validate_output: Validation logic for generated questions
        _format_clinical_vignette: Internal method for vignette formatting
    """
    # Implementation here
    pass
```

### 7.2 Type Hints (MANDATORY)

**ALWAYS use type hints for ALL function signatures:**

```python
from typing import Dict, List, Optional, Any, Tuple, Union
from pathlib import Path

# ✅ CORRECT - Complete type hints
def process_pdf(
    self,
    pdf_path: Path,
    chunk_size: int = 1000,
    overlap: int = 150,
    extract_images: bool = False
) -> Dict[str, Any]:
    """Process PDF and return structured data"""
    pass

def validate_question(
    self,
    question: Dict[str, str],
    strict_mode: bool = True
) -> Tuple[bool, List[str]]:
    """Validate question format and content"""
    pass

def get_agent_by_id(self, agent_id: str) -> Optional[BaseAgent]:
    """Get agent by ID, returns None if not found"""
    pass

def parse_dosage(self, text: str) -> Union[Dict[str, Any], None]:
    """Parse dosage from text, returns dict or None if invalid"""
    pass

# ❌ INCORRECT - Missing type hints
def process_pdf(self, pdf_path, chunk_size=1000):  # No type hints
    pass

def validate_question(self, question):  # No type hints
    pass
```

### 7.3 Module and Class Documentation

**Every module MUST have a module-level docstring:**

```python
#!/usr/bin/env python3
"""
Cardiology Clinical Expert Agent (MED-001)

This module implements the Cardiology Clinical Expert agent for the irStudy
ICRP medical education platform. The agent specializes in:

- Australian cardiology guidelines (Therapeutic Guidelines: Cardiovascular)
- AMC Clinical Exam preparation for cardiology stations
- Evidence-based cardiovascular medicine
- ECG interpretation
- Cardiac risk assessment (GRACE, TIMI, CHA2DS2-VASc scores)

The agent is designed to generate clinically accurate educational content
for International Medical Graduates (IMGs) preparing for Australian medical
practice and the AMC Clinical Exam.

Classes:
    CardiologyExpert: Main agent class extending BaseAgent
    ECGInterpreter: Helper class for ECG analysis
    RiskCalculator: Cardiac risk score calculations

Functions:
    load_cardiology_guidelines: Load Therapeutic Guidelines data
    format_cardiac_vignette: Format clinical vignette for cardiology

Example:
    >>> from src.agents.med_001_cardiology import CardiologyExpert
    >>> agent = CardiologyExpert()
    >>> task = AgentTask(title="Generate ACS MCQ", ...)
    >>> result = agent.execute_task(task)

Dependencies:
    - ollama: Local LLM for content generation
    - src.models.ollama_client: LLM client wrapper
    - src.agents.base_agent: Base agent framework

References:
    - Therapeutic Guidelines: Cardiovascular (2024)
    - Harrison's Principles of Internal Medicine, 21st Edition
    - Talley & O'Connor's Clinical Examination
    - AMC Clinical Exam Handbook

Author: AI Agent System
Created: 2025-12-18
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole
# ... rest of imports
```

### 7.4 README Requirements

**Every module/package MUST have a README.md:**

```markdown
# Cardiology Clinical Expert (MED-001)

**Agent ID**: MED-001
**Role**: Medical Expert - Cardiology
**Version**: 1.0.0

## Overview

The Cardiology Clinical Expert agent specializes in Australian cardiology practice,
AMC Clinical Exam preparation, and evidence-based cardiovascular medicine. The agent
generates clinically accurate educational content for ICRP candidates.

## Capabilities

- Generate cardiology MCQ questions
- Interpret ECG findings
- Calculate cardiac risk scores (GRACE, TIMI, CHA2DS2-VASc)
- Provide evidence-based management recommendations
- Validate clinical accuracy of cardiology content

## Specializations

- Acute Coronary Syndrome (ACS)
- Heart Failure (acute and chronic)
- Arrhythmias (AF, VT, SVT)
- Valvular Disease
- ECG Interpretation
- Cardiac Risk Assessment

## Usage Example

```python
from src.agents.med_001_cardiology import CardiologyExpert
from src.agents.base_agent import AgentTask

# Initialize agent
agent = CardiologyExpert()

# Create task
task = AgentTask(
    title="Generate ACS MCQ",
    description="Generate medium difficulty MCQ about acute coronary syndrome",
    metadata={
        'type': 'generate_mcq',
        'topic': 'acute_coronary_syndrome',
        'difficulty': 'medium'
    }
)

# Execute task
result = agent.run_task(task)

if result.status == TaskStatus.COMPLETED:
    mcq = result.result['output']
    print(f"Question: {mcq['stem']}")
    print(f"Answer: {mcq['correct_answer']}")
    print(f"Citation: {mcq['citation']}")
```

## Testing

Run unit tests:
```bash
pytest tests/agents/medical/test_cardiology.py -v
```

Run with coverage:
```bash
pytest tests/agents/medical/test_cardiology.py --cov=src.agents.med_001_cardiology
```

## Performance Metrics

- Average MCQ generation time: 8.3 seconds
- Token usage per MCQ: ~2000 tokens
- Validation pass rate: 95%+ (first attempt)
- RAG retrieval time: <500ms

## Dependencies

### Python Packages
- ollama (local LLM)
- langchain
- pydantic

### External Resources
- Therapeutic Guidelines: Cardiovascular (2024)
- Australian Medicines Handbook (AMH)
- PBS (Pharmaceutical Benefits Scheme)

### Internal Dependencies
- src.models.ollama_client: LLM client
- src.agents.base_agent: Base agent framework
- src.validators.medical_validator: Medical accuracy validation

## Configuration

Environment variables:
```bash
OLLAMA_BASE_URL=http://localhost:11434
MEDICAL_MODEL=meditron:7b
QA_MODEL=llama3.1:70b
```

## Medical Standards

This agent follows:
- Therapeutic Guidelines: Cardiovascular (Australian guidelines)
- AHPRA clinical standards
- AMC Clinical Exam requirements
- NSW Health protocols

All content uses:
- Australian spelling (paediatric, anaesthesia)
- Australian drug names (paracetamol, adrenaline)
- SI units (mmol/L, not mg/dL)
- Australian emergency number (000)

## Validation

All generated content is validated for:
- ✅ Australian terminology (no American terms)
- ✅ Proper citations (Therapeutic Guidelines)
- ✅ Drug dosage units (mg, mcg, mL)
- ✅ Red flag identification
- ✅ Clinical accuracy

## Known Limitations

- Limited to cardiology domain (refer to other specialists for non-cardiac)
- Requires validation for pediatric cases (age <18)
- May be overly detailed for simple queries
- Dependent on Ollama LLM availability

## Troubleshooting

**Issue**: Agent fails to generate content
**Solution**: Check Ollama service is running: `ollama list`

**Issue**: Validation fails with American terminology
**Solution**: Check LLM model - meditron:7b performs best for Australian context

**Issue**: Slow generation (>15 seconds)
**Solution**: Use faster model (qwen2.5:7b) or reduce context size

## Contributing

When modifying this agent:
1. Read PROJECT_CONSTRAINTS.md first
2. Maintain Australian medical standards
3. Add unit tests for new functionality
4. Update this README with changes
5. Run validation tests before committing

## References

- [Therapeutic Guidelines](https://tg.org.au/)
- [AMC Clinical Exam](https://www.amc.org.au/assessment/clinical-examination/)
- [AHPRA Standards](https://www.ahpra.gov.au/)
- [NSW Health Guidelines](https://www.health.nsw.gov.au/)

## License

Internal use only - irStudy ICRP Medical Education Platform

---

**Last Updated**: 2025-12-18
**Maintained By**: AI Agent Development Team
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
