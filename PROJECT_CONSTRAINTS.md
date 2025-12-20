# Project Constraints & Standards

**Project**: irStudy - ICRP Medical Education AI System
**Version**: 2.0.0
**Last Updated**: 2025-12-18
**Purpose**: Standards and constraints for implementing 46 medical AI agents + ICRP clinical preparation
**Critical**: ALL agents MUST read this file BEFORE starting any work

---

## Table of Contents

1. [Medical Accuracy Standards](#1-medical-accuracy-standards)
2. [Code Architecture & Patterns](#2-code-architecture--patterns)
3. [Security & Configuration](#3-security--configuration)
4. [LLM Integration Patterns](#4-llm-integration-patterns)
5. [Data Processing Standards](#5-data-processing-standards)
6. [Testing Requirements](#6-testing-requirements)
7. [Documentation Standards](#7-documentation-standards)
8. [Agent-Specific Requirements](#8-agent-specific-requirements)
9. [Project-Specific Context](#9-project-specific-context)
10. [Anti-Patterns (What NOT to Do)](#10-anti-patterns-what-not-to-do)
11. [ICRP Clinical Training Standards](#11-icrp-clinical-training-standards)

---

## 1. Medical Accuracy Standards

### 1.1 Australian Medical Context (MANDATORY)

**ALWAYS use Australian standards and resources:**

- **Primary Sources**:
  - Therapeutic Guidelines (eTG) - Australian treatment guidelines
  - PBS (Pharmaceutical Benefits Scheme) - Australian drug listings
  - AHPRA - Australian Health Practitioner Regulation Agency standards
  - NSW Health guidelines - Local health district protocols
  - AMC (Australian Medical Council) - Exam standards
  - AMH (Australian Medicines Handbook)

**NEVER use:**
- American drug names without Australian equivalents
- Non-Australian treatment protocols without qualification
- Non-AHPRA standards
- UpToDate without Australian context

### 1.2 Australian Spelling & Terminology (MANDATORY)

**CORRECT Australian Spelling:**
```
paediatric (NOT pediatric)
anaesthesia (NOT anesthesia)
oesophagus (NOT esophagus)
haemoglobin (NOT hemoglobin)
anaemia (NOT anemia)
paracetamol (NOT acetaminophen - different drug name!)
adrenaline (NOT epinephrine)
salbutamol (NOT albuterol)
colour (NOT color)
oestrogen (NOT estrogen)
```

**Australian Medical Terms:**
```
GP (NOT PCP or primary care physician)
Emergency Department (NOT ER or emergency room)
Specialist (NOT attending)
Referral (NOT consult)
Bulk-billed (NOT covered by insurance)
Medicare (NOT insurance)
```

**Example - CORRECT:**
```python
drug_info = {
    'name': 'paracetamol',  # Australian name
    'indication': 'Management of paediatric fever',
    'dose': '15 mg/kg',
    'max_dose': '60 mg/kg/day',
    'source': 'Therapeutic Guidelines: Paediatric, Section 2.1'
}
```

**Example - INCORRECT:**
```python
drug_info = {
    'name': 'acetaminophen',  # ❌ American name
    'indication': 'Management of pediatric fever',  # ❌ American spelling
    'source': 'UpToDate'  # ❌ American source without context
}
```

### 1.3 Clinical Accuracy Requirements

**Drug Dosages:**
- ALWAYS include units (mg, mcg, mL, units/kg)
- ALWAYS specify age/weight ranges
- ALWAYS cite Therapeutic Guidelines or PBS
- ALWAYS note PBS restrictions if applicable

**Example - CORRECT:**
```python
dosage = {
    'drug': 'amoxicillin',
    'dose': '500 mg',
    'frequency': 'three times daily (TDS)',
    'duration': '5-7 days',
    'indication': 'Community-acquired pneumonia',
    'citation': 'Therapeutic Guidelines: Antibiotic, Section 2.3.1 (2024)',
    'pbs_listed': True,
    'restrictions': 'None'
}
```

**Red Flags:**
- ALWAYS flag life-threatening conditions
- ALWAYS recommend immediate referral for emergencies
- ALWAYS include safety warnings
- ALWAYS use "000" for emergency calls (Australian emergency number)

**Example - CORRECT:**
```python
if symptoms_include(['chest_pain', 'radiation_to_arm', 'diaphoresis']):
    return {
        'red_flag': True,
        'severity': 'CRITICAL',
        'action': 'Call ambulance (000) immediately - suspect acute coronary syndrome',
        'immediate_management': 'Aspirin 300mg PO, oxygen if hypoxic, IV access',
        'citation': 'NSW Health: Acute Coronary Syndrome Protocol (2024)'
    }
```

**SI Units (Australian Standard):**
```python
# ✅ CORRECT - SI units
glucose = {'value': 5.5, 'unit': 'mmol/L'}
sodium = {'value': 140, 'unit': 'mmol/L'}

# ❌ INCORRECT - American units
glucose = {'value': 100, 'unit': 'mg/dL'}  # Don't use mg/dL
```

### 1.4 Citation Requirements (MANDATORY)

**EVERY medical claim MUST have a citation:**

```python
# ✅ CORRECT
question = {
    'stem': 'First-line treatment for type 2 diabetes is...',
    'answer': 'Metformin',
    'explanation': 'Metformin is first-line as per Therapeutic Guidelines: Endocrinology.',
    'citation': 'Therapeutic Guidelines: Endocrinology, Section 3.2.1 (2024)',
    'evidence_level': 'Grade A recommendation'
}

# ❌ INCORRECT - No citation
question = {
    'stem': 'First-line treatment for type 2 diabetes is...',
    'answer': 'Metformin',
    'explanation': 'Metformin is first-line.'  # ❌ Missing citation
}
```

**Acceptable Citations:**
- Therapeutic Guidelines: [Specialty], Section X.Y.Z (Year)
- Harrison's Internal Medicine, Chapter XYZ
- Talley & O'Connor's Clinical Examination, Page XYZ
- AMC Clinical Exam Handbook
- NSW Health Clinical Practice Guidelines
- RACGP (Royal Australian College of General Practitioners) Guidelines
- Australian Medicines Handbook (AMH)

---

## 2. Code Architecture & Patterns

### 2.1 BaseAgent Inheritance Pattern (MANDATORY)

**ALL agents MUST extend BaseAgent:**

**Reference File**: `/home/dev/Development/irStudy/src/agents/base_agent.py`

**Example - CORRECT:**
```python
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole, AgentTask, TaskStatus
from typing import Dict, List, Any

class CardiologyExpert(BaseAgent):
    """
    MED-001: Cardiology Clinical Expert

    Specialized in Australian cardiology guidelines, AMC Clinical Exam prep,
    and evidence-based cardiovascular medicine.
    """

    def __init__(self):
        metadata = AgentMetadata(
            agent_id="MED-001",  # Format: PREFIX-XXX
            name="Cardiology Clinical Expert",
            role=AgentRole.MEDICAL_EXPERT,
            experience_years=15,
            technologies=[
                "Therapeutic Guidelines: Cardiovascular",
                "Cardiology",
                "ECG Interpretation",
                "Echocardiography"
            ],
            specializations=[
                "Acute Coronary Syndrome",
                "Heart Failure",
                "Arrhythmias",
                "Valvular Disease",
                "AMC Clinical Exam preparation"
            ],
            pros=[
                "Expert in Australian cardiology guidelines (eTG)",
                "15+ years clinical cardiology experience",
                "Specialized in AMC Clinical Exam preparation",
                "Evidence-based approach with citations"
            ],
            cons=[
                "Limited to cardiology domain",
                "Requires validation for paediatric cases",
                "May be overly detailed for simple queries"
            ],
            max_concurrent_tasks=5,
            quality_gate_required=True
        )
        super().__init__(metadata)

        # Register agent-specific tools
        self._register_cardiology_tools()

    def _register_cardiology_tools(self):
        """Register cardiology-specific tools"""
        self.register_tool(
            "interpret_ecg",
            self._interpret_ecg,
            "Interpret ECG findings and provide differential diagnosis"
        )
        self.register_tool(
            "calculate_risk_score",
            self._calculate_cardiac_risk,
            "Calculate cardiac risk scores (GRACE, TIMI, CHA2DS2-VASc)"
        )

    def execute_task(self, task: AgentTask) -> Dict[str, Any]:
        """Execute cardiology-specific task"""
        self.logger.info(f"Executing cardiology task: {task.title}")

        try:
            task_type = task.metadata.get('type', 'general')

            if task_type == 'generate_mcq':
                result = self._generate_cardiology_mcq(task)
            elif task_type == 'interpret_ecg':
                result = self._interpret_ecg(task)
            elif task_type == 'risk_assessment':
                result = self._calculate_cardiac_risk(task)
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
        """Validate medical accuracy of output"""
        errors = []

        result = output.get('output', {})

        # Check for required citation
        if not result.get('citation'):
            errors.append("Missing citation for medical claim")

        # Check for Australian terminology
        if self._contains_american_terminology(result):
            errors.append("Contains American terminology (must use Australian)")

        # Check for proper drug names
        if self._contains_american_drug_names(result):
            errors.append("Contains American drug names (e.g., acetaminophen instead of paracetamol)")

        # Check for dosage units
        if 'dosage' in result and not self._has_proper_units(result['dosage']):
            errors.append("Dosage missing units (must include mg, mcg, mL, etc.)")

        # Check for red flag identification
        if 'emergency' in task.description.lower() and not result.get('red_flag'):
            errors.append("Failed to identify red flag condition")

        return len(errors) == 0, errors

    def _contains_american_terminology(self, data: Dict) -> bool:
        """Check for American medical terminology"""
        american_terms = [
            'pediatric', 'anesthesia', 'esophagus', 'hemoglobin',
            'anemia', 'acetaminophen', 'epinephrine', 'albuterol',
            'color', 'estrogen', 'ER', 'PCP', 'attending'
        ]

        text = str(data).lower()
        return any(term in text for term in american_terms)

    def _contains_american_drug_names(self, data: Dict) -> bool:
        """Check for American drug names"""
        american_drugs = {
            'acetaminophen': 'paracetamol',
            'epinephrine': 'adrenaline',
            'albuterol': 'salbutamol',
            'tylenol': 'panadol'
        }

        text = str(data).lower()
        return any(drug in text for drug in american_drugs.keys())

    def _has_proper_units(self, dosage_info: Any) -> bool:
        """Check if dosage has proper units"""
        required_units = ['mg', 'mcg', 'g', 'mL', 'units', 'IU']
        text = str(dosage_info)
        return any(unit in text for unit in required_units)

    # Implementation methods...
    def _generate_cardiology_mcq(self, task: AgentTask) -> Dict:
        """Generate cardiology MCQ"""
        # Implementation here
        pass
```

**Example - INCORRECT:**
```python
# ❌ Does not extend BaseAgent
class CardiologyExpert:
    def __init__(self):
        self.name = "Cardiology Expert"

    def generate_question(self):  # ❌ Wrong method name
        pass
```

### 2.2 Agent ID Format (MANDATORY)

**Format**: `PREFIX-XXX` where XXX is 3-digit number (zero-padded)

**Prefixes:**
- `PM-XXX`: Project Management (e.g., PM-001)
- `DEV-XXX`: Software Development (e.g., DEV-001, DEV-002)
- `MED-XXX`: Medical Experts (e.g., MED-001 to MED-015)
- `AI-XXX`: Data & AI Engineering (e.g., AI-001 to AI-008)
- `QA-XXX`: Quality Assurance (e.g., QA-001 to QA-004)
- `DEVOPS-XXX`: DevOps & Infrastructure (e.g., DEVOPS-001)
- `SEC-XXX`: Security (e.g., SEC-001)

**Examples:**
```python
# ✅ CORRECT
agent_id = "MED-001"  # Cardiology Expert
agent_id = "DEV-004"  # Database Engineer
agent_id = "AI-001"   # RAG System
agent_id = "QA-001"   # Medical Content QA

# ❌ INCORRECT
agent_id = "cardiology_expert"    # Wrong format
agent_id = "MED-1"                # Not 3 digits
agent_id = "MEDICAL-001"          # Wrong prefix
agent_id = "med-001"              # Must be uppercase
```

### 2.3 Logging Standards (MANDATORY)

**ALWAYS use structured logging with self.logger:**

**Reference**: BaseAgent._setup_logger() in `/home/dev/Development/irStudy/src/agents/base_agent.py`

```python
# ✅ CORRECT - Use agent's logger
self.logger.debug(f"Processing task with parameters: {params}")
self.logger.info(f"Starting task: {task.title}")
self.logger.warning(f"Validation warning: {warning_message}")
self.logger.error(f"Task failed: {error}", exc_info=True)
self.logger.critical(f"System failure: {critical_error}")

# ❌ INCORRECT
print("Starting task")  # Don't use print()
logging.info("Task started")  # Don't use root logger
```

**Log Levels:**
- `DEBUG`: Detailed diagnostic information (parameter values, internal state)
- `INFO`: Confirmation of expected operation (task started, completed)
- `WARNING`: Something unexpected but not fatal (validation warning, fallback triggered)
- `ERROR`: Serious problem, task may fail (exception caught, invalid input)
- `CRITICAL`: System-level failure (database down, model unavailable)

**Log Format** (automatically configured by BaseAgent):
```
[AGENT-ID] TIMESTAMP - LEVEL - MESSAGE
Example: [MED-001] 2025-12-18 10:30:45 - INFO - Starting task: Generate Cardiology MCQ
```

### 2.4 Error Handling Pattern (MANDATORY)

**ALWAYS use try-except blocks with specific exceptions:**

```python
# ✅ CORRECT
def execute_task(self, task: AgentTask) -> Dict[str, Any]:
    try:
        # Validate inputs first
        if not task.description:
            raise ValueError("Task description is required")

        if not task.metadata.get('topic'):
            raise ValueError("Task metadata must include 'topic'")

        # Execute work
        self.logger.info(f"Executing: {task.title}")
        result = self._do_work(task)

        # Validate outputs
        validation_passed, errors = self.validate_output(task, result)
        if not validation_passed:
            raise ValueError(f"Validation failed: {', '.join(errors)}")

        return {
            'status': 'success',
            'output': result,
            'validation_passed': True
        }

    except ValueError as e:
        # Expected validation errors
        self.logger.error(f"Validation error: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'error_type': 'validation_error'
        }

    except FileNotFoundError as e:
        # Missing resource
        self.logger.error(f"Resource not found: {e}")
        return {
            'status': 'error',
            'error': str(e),
            'error_type': 'resource_error'
        }

    except Exception as e:
        # Unexpected errors
        self.logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'status': 'error',
            'error': str(e),
            'error_type': 'unexpected_error'
        }

# ❌ INCORRECT - Bare except
try:
    result = do_something()
except:  # ❌ Don't use bare except
    pass  # ❌ Don't silently fail
```

### 2.5 Task Execution Pattern (MANDATORY)

**Standard task execution flow is handled by BaseAgent.run_task():**

**Reference**: BaseAgent.run_task() in `/home/dev/Development/irStudy/src/agents/base_agent.py`

The flow is:
1. Mark task as `TaskStatus.IN_PROGRESS`
2. Call `execute_task(task)` - Your implementation
3. Call `validate_output(task, output)` if quality_gate_required=True
4. Mark as `TaskStatus.COMPLETED` or `TaskStatus.FAILED`
5. Move task to completed_tasks list
6. Return updated task

**Usage:**
```python
# ✅ CORRECT - Let BaseAgent handle workflow
agent = CardiologyExpert()
task = AgentTask(title="Generate MCQ", description="...")
result_task = agent.run_task(task)

if result_task.status == TaskStatus.COMPLETED:
    print(f"Success: {result_task.result}")
else:
    print(f"Failed: {result_task.error}")

# ❌ INCORRECT - Don't bypass BaseAgent
result = agent.execute_task(task)  # Skips status tracking and validation!
```

---

## 3. Security & Configuration

### 3.1 NO Hardcoded Secrets (CRITICAL - ZERO TOLERANCE)

**NEVER EVER hardcode:**
- API keys
- Database passwords
- Encryption keys
- User IDs (even for testing)
- File paths with credentials
- Secret tokens

**This is a ZERO TOLERANCE policy. Any hardcoded secret will require immediate fix.**

**Example - CORRECT:**
```python
import os
from pathlib import Path

# ✅ Use environment variables
DATABASE_URL = os.getenv('DATABASE_URL')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
QDRANT_API_KEY = os.getenv('QDRANT_API_KEY')
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# ✅ Use config files (excluded from git via .gitignore)
from config import load_config
config = load_config()
db_password = config['database']['password']

# ✅ For testing, use test fixtures
@pytest.fixture
def test_user_id():
    return "test-user-" + str(uuid.uuid4())
```

**Example - INCORRECT:**
```python
# ❌ NEVER do this
DATABASE_URL = "postgresql://user:password123@localhost:5432/db"
OPENAI_API_KEY = "sk-1234567890abcdef"
USER_ID = "mock-user-id-12345"  # Even for testing!
QDRANT_API_KEY = "abc123xyz"
SECRET_KEY = "my-super-secret-key"
```

### 3.2 Configuration Management (MANDATORY)

**Use configuration hierarchy:**

1. Environment variables (highest priority)
2. Config files (`.env`, `config.yaml` - in .gitignore)
3. Default values (lowest priority, only for non-sensitive)

**Example - CORRECT:**
```python
from pathlib import Path
import os
from typing import Optional

class Config:
    """Application configuration with environment variable override"""

    # Paths - safe to hardcode
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    PROCESSED_DIR = DATA_DIR / "processed"
    BOOKS_DIR = BASE_DIR / "Books"

    # Database - from env vars (REQUIRED)
    DATABASE_URL: str = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is required")

    # Ollama - from env vars with safe default
    OLLAMA_BASE_URL: str = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

    # Model selection - from env vars with defaults
    DEFAULT_MEDICAL_MODEL: str = os.getenv('MEDICAL_MODEL', 'meditron:7b')
    DEFAULT_QA_MODEL: str = os.getenv('QA_MODEL', 'llama3.1:70b')

    # Optional API keys - may be None
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    QDRANT_API_KEY: Optional[str] = os.getenv('QDRANT_API_KEY')

    @classmethod
    def validate(cls) -> None:
        """Validate required configuration is present"""
        required = ['DATABASE_URL']
        missing = [key for key in required if not getattr(cls, key)]

        if missing:
            raise ValueError(f"Missing required configuration: {missing}")

# Validate config on import
Config.validate()
```

### 3.3 File Path Conventions (MANDATORY)

**ALWAYS use pathlib.Path, NEVER string concatenation:**

**Reference**: All scripts in `/home/dev/Development/irStudy/scripts/` use this pattern

```python
from pathlib import Path

# ✅ CORRECT
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PROCESSED_DIR = DATA_DIR / "processed"
PDF_FILE = DATA_DIR / "books" / "clinical_exam.pdf"

# Create directories
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Check existence
if PDF_FILE.exists():
    with open(PDF_FILE, 'rb') as f:
        content = f.read()

# Get all PDFs in directory
pdf_files = list(DATA_DIR.glob("*.pdf"))

# Recursive search
all_pdfs = list(DATA_DIR.rglob("*.pdf"))

# ❌ INCORRECT
DATA_DIR = "data"  # String path
PDF_FILE = DATA_DIR + "/books/" + "clinical_exam.pdf"  # String concatenation
PDF_FILE = os.path.join(DATA_DIR, "books", "clinical_exam.pdf")  # Old style
```

### 3.4 Sensitive Data Handling

**Medical data is sensitive - anonymize before logging:**

```python
# ✅ CORRECT - Anonymize before logging
patient_id = "12345678"
self.logger.info(f"Processing patient case: {patient_id[:4]}***")  # Show only first 4 digits

case_id = "CASE-2025-001234"
self.logger.info(f"Processing case: {case_id[:13]}...")  # Truncate

# ❌ INCORRECT - Logging sensitive data
self.logger.info(f"Processing patient: John Smith, DOB: 1985-03-15, MRN: 12345678")
self.logger.info(f"Patient email: john.smith@email.com")
```

---

## 4. LLM Integration Patterns

### 4.1 Ollama Client Usage (MANDATORY)

**Reference File**: `/home/dev/Development/irStudy/src/models/ollama_client.py`

**ALWAYS use OllamaClient for LLM access:**

```python
from src.models.ollama_client import OllamaClient

class MedicalContentGenerator(BaseAgent):
    def __init__(self):
        super().__init__(metadata)

        # Initialize Ollama client
        self.ollama = OllamaClient(
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        )

    def generate_mcq(self, topic: str) -> Dict:
        """Generate medical MCQ using LLM"""

        # Get recommended model for this task
        model_name = self.ollama.recommend_model('question_generation')
        self.logger.info(f"Using model: {model_name}")

        # Construct prompt
        prompt = f"""Generate a medical MCQ question about {topic}.

Requirements:
- Use Australian medical terminology and spelling
- Cite Therapeutic Guidelines or equivalent Australian source
- Include 5 options (A-E) with one clearly correct answer
- Provide detailed explanation with citation
- Target audience: ICRP candidates preparing for AMC Clinical Exam

Format output as JSON:
{{
    "stem": "question text",
    "options": {{"A": "...", "B": "...", ...}},
    "correct_answer": "B",
    "explanation": "...",
    "citation": "..."
}}
"""

        # Generate with appropriate temperature
        response = self.ollama.generate(
            prompt=prompt,
            model_name=model_name,
            temperature=0.7  # Higher for creative tasks
        )

        # Parse and validate response
        return self._parse_mcq_response(response)
```

### 4.2 Model Selection Guidelines (MANDATORY)

**Model Registry** (from `/home/dev/Development/irStudy/src/models/ollama_client.py`):

| Model | Best For | Temperature | Notes |
|-------|----------|-------------|-------|
| `meditron:7b` | Medical facts, clinical reasoning, medical QA | 0.3 | Medical-specific training |
| `biomistral:7b` | Biomedical text, research, terminology | 0.3 | BioMedical LLM |
| `llama3.1:70b` | Complex reasoning, validation, quality checks | 0.3-0.7 | Best overall quality |
| `mixtral:8x7b` | MCQ creation, explanations, content generation | 0.7 | Mixture of Experts |
| `deepseek-coder:6.7b` | Structured JSON output, code generation | 0.2 | Best for structured data |
| `qwen2.5:7b` | General tasks, fast inference, simple QA | 0.5 | Fast and reliable |
| `qwen2.5vl:7b` | Image analysis, diagram interpretation | 0.5 | Vision-language model |
| `phi3:mini` | Simple classification, quick tasks | 0.3 | Fastest, lightweight |

**Usage Examples:**

```python
# Medical facts - use low temperature for accuracy
medical_facts = self.ollama.generate(
    "What are contraindications for metformin in Australian practice?",
    model_name="meditron:7b",
    temperature=0.3  # Low = factual, consistent
)

# Creative question generation - use high temperature
creative_question = self.ollama.generate(
    "Generate a novel clinical vignette for acute coronary syndrome",
    model_name="mixtral:8x7b",
    temperature=0.7  # High = creative, diverse
)

# Structured JSON output - use very low temperature
structured_output = self.ollama.generate(
    prompt_with_json_schema,
    model_name="deepseek-coder:6.7b",
    temperature=0.2  # Very low = consistent structure
)

# Validation/QA - use medium-low temperature
validation = self.ollama.generate(
    "Validate this medical content for accuracy",
    model_name="llama3.1:70b",
    temperature=0.3  # Medium-low = thorough, consistent
)
```

### 4.3 Prompt Engineering Standards (MANDATORY)

**Use structured, well-formatted prompts:**

```python
# ✅ CORRECT - Structured prompt template
CARDIOLOGY_MCQ_PROMPT = """You are a medical education expert specializing in Australian cardiology practice.

TASK: Generate a multiple-choice question (MCQ) for ICRP candidates preparing for the AMC Clinical Exam.

CONTEXT:
- Target audience: International Medical Graduates (IMGs) in Australia
- Geographic context: NSW, Australia
- Standards: Therapeutic Guidelines: Cardiovascular, AHPRA guidelines, NSW Health protocols
- Exam format: AMC Clinical Exam (OSCE-style)

TOPIC: {topic}
DIFFICULTY: {difficulty}

REQUIREMENTS:
1. Use Australian spelling (paediatric, anaesthesia, anaemia, paracetamol)
2. Use Australian drug names (adrenaline not epinephrine, salbutamol not albuterol)
3. Cite Therapeutic Guidelines or equivalent Australian source
4. Include realistic clinical vignette (age, presentation, examination findings)
5. Provide 5 plausible options (A-E) with one clearly correct answer
6. Include detailed explanation with pathophysiology and clinical reasoning
7. Flag any red flag conditions that require immediate action
8. Include "Call 000" for emergencies (Australian emergency number)

OUTPUT FORMAT (JSON):
{{
    "question_id": "MCQ-CARD-XXX",
    "specialty": "cardiology",
    "topic": "{topic}",
    "difficulty": "{difficulty}",
    "stem": "Clinical vignette here (patient age, presentation, examination, investigations)",
    "options": {{
        "A": "First option",
        "B": "Second option (correct)",
        "C": "Third option",
        "D": "Fourth option",
        "E": "Fifth option"
    }},
    "correct_answer": "B",
    "explanation": "Detailed explanation with reasoning, pathophysiology, and why other options are incorrect",
    "citation": "Therapeutic Guidelines: Cardiovascular, Section X.Y.Z (2024)",
    "red_flags": ["List any red flag conditions if applicable"],
    "learning_points": ["Key learning points for ICRP candidates"]
}}

INPUT DATA:
{input_context}

Generate the MCQ now:
"""

# Use the template
prompt = CARDIOLOGY_MCQ_PROMPT.format(
    topic="acute coronary syndrome",
    difficulty="medium",
    input_context=rag_context
)
```

**Prompt Best Practices:**
1. **Be specific**: State exact requirements (Australian spelling, citations, format)
2. **Provide context**: Who is the audience? What standards apply?
3. **Give examples**: Show the format you want
4. **State constraints**: What NOT to do (no American terms, no missing citations)
5. **Structure output**: Specify JSON schema or format

### 4.4 Token Limits & Context Management (MANDATORY)

**Model token limits:**
- Most models: 4,096 tokens (~16,000 characters)
- llama3.1:70b: 8,192 tokens (~32,000 characters)

**Chunking Strategy:**

```python
def chunk_for_llm(self, text: str, max_tokens: int = 3000) -> List[str]:
    """
    Chunk text to fit within token limits with overlap.

    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk (default: 3000 to leave room for prompt)

    Returns:
        List of text chunks
    """
    # Rough approximation: 1 token ≈ 4 characters
    max_chars = max_tokens * 4
    overlap_chars = 600  # ~150 tokens overlap to preserve context

    if len(text) <= max_chars:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        # Get chunk
        end = start + max_chars

        if end < len(text):
            # Find last paragraph break within chunk
            para_break = text.rfind('\n\n', start, end)
            if para_break > start:
                end = para_break

        chunk = text[start:end]
        chunks.append(chunk)

        # Move start with overlap
        start = end - overlap_chars

    return chunks
```

### 4.5 LLM Fallback Strategy (MANDATORY)

**ALWAYS have fallback for LLM failures:**

```python
def generate_with_fallback(self, prompt: str, task_type: str = 'general') -> str:
    """
    Generate with model fallback strategy.

    Tries models in order of preference until one succeeds.

    Args:
        prompt: Input prompt
        task_type: Type of task for model recommendation

    Returns:
        Generated text

    Raises:
        RuntimeError: If all models fail
    """

    # Get recommended model for task
    primary_model = self.ollama.recommend_model(task_type)

    # Fallback chain
    fallback_models = [
        primary_model,
        'meditron:7b',      # Medical-specific fallback
        'qwen2.5:7b',       # Fast general fallback
        'phi3:mini'         # Lightweight last resort
    ]

    # Remove duplicates while preserving order
    models = list(dict.fromkeys(fallback_models))

    for i, model_name in enumerate(models):
        try:
            self.logger.info(f"Attempting generation with {model_name} (attempt {i+1}/{len(models)})")

            response = self.ollama.generate(
                prompt=prompt,
                model_name=model_name
            )

            self.logger.info(f"Generation successful with {model_name}")
            return response

        except Exception as e:
            self.logger.warning(f"Model {model_name} failed: {e}")

            if i == len(models) - 1:
                # Last model failed
                self.logger.error("All fallback models failed")
                raise RuntimeError(f"LLM generation failed after {len(models)} attempts") from e

            # Continue to next fallback
            continue
```

---

## 5. Data Processing Standards

### 5.1 JSON File Handling (MANDATORY)

**Reference Files**:
- `/home/dev/Development/irStudy/scripts/extract_pdfs.py`
- `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py`

**ALWAYS specify encoding='utf-8':**

```python
import json
from pathlib import Path
from typing import Dict, Any

# ✅ CORRECT - Load JSON with proper encoding and error handling
def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load JSON file with proper encoding and error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON data as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    if not file_path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.logger.info(f"Loaded JSON from {file_path} ({file_path.stat().st_size} bytes)")
        return data

    except json.JSONDecodeError as e:
        self.logger.error(f"Invalid JSON in {file_path}: {e}")
        raise
    except Exception as e:
        self.logger.error(f"Failed to load {file_path}: {e}")
        raise

# ✅ CORRECT - Save JSON with proper encoding and formatting
def save_json(data: Dict[str, Any], file_path: Path, indent: int = 2) -> None:
    """
    Save data to JSON file with proper encoding.

    Args:
        data: Data to save
        file_path: Output file path
        indent: JSON indentation (default: 2 spaces)
    """
    try:
        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,  # Preserve Unicode characters
                indent=indent
            )

        file_size = file_path.stat().st_size
        self.logger.info(f"Saved JSON to {file_path} ({file_size:,} bytes)")

    except Exception as e:
        self.logger.error(f"Failed to save {file_path}: {e}")
        raise

# ❌ INCORRECT - Missing encoding
with open('file.json', 'r') as f:  # ❌ Missing encoding='utf-8'
    data = json.load(f)

# ❌ INCORRECT - No error handling
data = json.load(open('file.json'))  # ❌ No try-except, no encoding
```

### 5.2 Large File Processing (MANDATORY)

**ALWAYS use progress bars (tqdm) for long operations:**

**Reference File**: `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py`

```python
from tqdm import tqdm
from typing import List, Any

# ✅ CORRECT - Process with progress bar
def process_large_dataset(self, items: List[Any], description: str = "Processing") -> List[Any]:
    """
    Process large dataset with progress tracking and error handling.

    Args:
        items: List of items to process
        description: Progress bar description

    Returns:
        List of successfully processed results
    """
    results = []
    errors = []

    for item in tqdm(items, desc=description, unit="item"):
        try:
            result = self._process_item(item)
            results.append(result)
        except Exception as e:
            self.logger.warning(f"Failed to process item {item}: {e}")
            errors.append({'item': item, 'error': str(e)})
            continue

    self.logger.info(f"Processed {len(results)}/{len(items)} items ({len(errors)} errors)")

    if errors:
        self.logger.warning(f"Errors occurred: {errors}")

    return results

# ✅ CORRECT - Batch processing for memory efficiency
def process_in_batches(
    self,
    items: List[Any],
    batch_size: int = 100,
    description: str = "Processing batches"
) -> List[Any]:
    """
    Process items in batches to manage memory usage.

    Args:
        items: List of items to process
        batch_size: Number of items per batch
        description: Progress bar description

    Returns:
        List of all processed results
    """
    results = []
    num_batches = (len(items) + batch_size - 1) // batch_size

    for i in tqdm(range(0, len(items), batch_size), desc=description, total=num_batches, unit="batch"):
        batch = items[i:i+batch_size]

        try:
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
        except Exception as e:
            self.logger.error(f"Batch {i//batch_size + 1} failed: {e}")
            continue

    return results

# ❌ INCORRECT - No progress indicator
for item in large_list:  # ❌ No tqdm, user has no idea of progress
    process(item)

# ❌ INCORRECT - Loading entire large file into memory
with open('huge_file.json', 'r') as f:
    data = json.load(f)  # ❌ Could be GBs, may crash
```

### 5.3 Pickle vs JSON Usage Guidelines

**Guidelines:**

**Use JSON when:**
- Data needs to be human-readable
- Data will be shared between systems or languages
- Data needs to be version-controlled (git-friendly)
- Data structure is simple (dicts, lists, strings, numbers, booleans)
- Security is a concern (JSON is safer than pickle)

**Use Pickle when:**
- Storing complex Python objects (numpy arrays, models, embeddings)
- Performance is critical (pickle is faster for large data)
- Data stays within Python ecosystem
- Object structure preservation is important

**Examples:**

```python
import pickle
import json
import numpy as np

# ✅ JSON for MCQ questions (human-readable, shareable)
questions = [
    {'id': 'MCQ-001', 'stem': '...', 'answer': 'B'},
    {'id': 'MCQ-002', 'stem': '...', 'answer': 'A'}
]
with open('questions.json', 'w', encoding='utf-8') as f:
    json.dump(questions, f, indent=2)

# ✅ Pickle for embeddings (binary, fast, numpy arrays)
embeddings = np.array([[0.1, 0.2, ...], [0.3, 0.4, ...]])  # 768-dim vectors
with open('embeddings.pkl', 'wb') as f:
    pickle.dump(embeddings, f)

# ✅ JSON for configuration (human-editable)
config = {
    'model': 'meditron:7b',
    'temperature': 0.3,
    'max_tokens': 4096
}
with open('config.json', 'w') as f:
    json.dump(config, f, indent=2)

# ✅ Pickle for trained model (complex object)
trained_model = some_ml_model.fit(X, y)
with open('model.pkl', 'wb') as f:
    pickle.dump(trained_model, f)
```

### 5.4 Path Management Best Practices

**Define all paths upfront in a configuration class:**

```python
from pathlib import Path

class DataPaths:
    """Centralized path management for data processing"""

    # Base directories
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DIR = DATA_DIR / "raw"
    PROCESSED_DIR = DATA_DIR / "processed"
    BOOKS_DIR = BASE_DIR / "Books"
    SCRIPTS_DIR = BASE_DIR / "scripts"

    # Output directories
    CHUNKS_DIR = PROCESSED_DIR / "chunks"
    EMBEDDINGS_DIR = PROCESSED_DIR / "embeddings"
    QUESTIONS_DIR = PROCESSED_DIR / "questions"

    # Specific files
    CHUNKS_JSON = DATA_DIR / "chunks.json"
    FLASHCARDS_JSON = BASE_DIR / "ICRP_Program_Resources" / "Flashcards" / "flashcard_data.json"

    @classmethod
    def initialize(cls) -> None:
        """Create all necessary directories"""
        directories = [
            cls.DATA_DIR,
            cls.RAW_DIR,
            cls.PROCESSED_DIR,
            cls.CHUNKS_DIR,
            cls.EMBEDDINGS_DIR,
            cls.QUESTIONS_DIR
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_processed_file(cls, book_name: str) -> Path:
        """Get path for processed book JSON"""
        safe_name = book_name.replace(' ', '_').replace('/', '_')
        return cls.PROCESSED_DIR / f"{safe_name}.json"

    @classmethod
    def get_book_chunks(cls, book_name: str) -> Path:
        """Get path for book chunks"""
        safe_name = book_name.replace(' ', '_').replace('/', '_')
        return cls.CHUNKS_DIR / f"{safe_name}_chunks.json"

# Initialize paths on import
DataPaths.initialize()

# Usage in scripts
pdf_file = DataPaths.BOOKS_DIR / "clinical_exam.pdf"
output_file = DataPaths.get_processed_file("Clinical Examination")
```

---

## 6. Testing Requirements

### 6.1 Unit Test Standards (MANDATORY)

**ALL agent methods MUST have unit tests with 80%+ coverage:**

```python
import pytest
from src.agents.med_001_cardiology import CardiologyExpert
from src.agents.base_agent import AgentTask, TaskStatus, AgentRole

class TestCardiologyExpert:
    """
    Test suite for Cardiology Expert (MED-001).

    Tests cover:
    - Agent initialization
    - Task execution
    - Output validation
    - Medical accuracy checks
    - Australian terminology validation
    """

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing"""
        return CardiologyExpert()

    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return AgentTask(
            title="Generate ACS MCQ",
            description="Generate MCQ about acute coronary syndrome",
            metadata={
                'type': 'generate_mcq',
                'topic': 'acute_coronary_syndrome',
                'difficulty': 'medium'
            }
        )

    # Test 1: Agent Initialization
    def test_agent_initialization(self, agent):
        """Test agent initializes with correct metadata"""
        assert agent.metadata.agent_id == "MED-001"
        assert agent.metadata.name == "Cardiology Clinical Expert"
        assert agent.metadata.role == AgentRole.MEDICAL_EXPERT
        assert agent.metadata.experience_years == 15
        assert "Cardiology" in agent.metadata.specializations
        assert "Acute Coronary Syndrome" in agent.metadata.specializations
        assert len(agent.metadata.pros) > 0
        assert len(agent.metadata.cons) > 0

    # Test 2: Successful Task Execution
    def test_execute_task_success(self, agent, sample_task):
        """Test successful task execution returns expected format"""
        result = agent.execute_task(sample_task)

        assert result['status'] == 'success'
        assert 'output' in result
        assert result['validation_passed'] is True

        # Check output structure
        output = result['output']
        assert 'question_id' in output
        assert 'stem' in output
        assert 'options' in output
        assert 'correct_answer' in output
        assert 'explanation' in output
        assert 'citation' in output

    # Test 3: Validation Requires Citation
    def test_validate_output_requires_citation(self, agent, sample_task):
        """Test validation fails when citation is missing"""
        output = {
            'output': {
                'question': 'What is first-line for ACS?',
                'answer': 'Aspirin',
                # Missing citation!
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('citation' in error.lower() for error in errors)

    # Test 4: Australian Spelling Validation
    def test_australian_spelling_validation(self, agent, sample_task):
        """Test validation catches American spelling"""
        output = {
            'output': {
                'stem': 'A pediatric patient presents...',  # American spelling
                'citation': 'Some source'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any(
            'american' in error.lower() or 'spelling' in error.lower() or 'terminology' in error.lower()
            for error in errors
        )

    # Test 5: American Drug Names Validation
    def test_american_drug_names_rejected(self, agent, sample_task):
        """Test validation catches American drug names"""
        output = {
            'output': {
                'explanation': 'Give acetaminophen for pain',  # Should be paracetamol
                'citation': 'Therapeutic Guidelines'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('drug' in error.lower() or 'american' in error.lower() for error in errors)

    # Test 6: Dosage Units Required
    def test_dosage_requires_units(self, agent, sample_task):
        """Test validation requires dosage units"""
        output = {
            'output': {
                'dosage': '500',  # Missing units!
                'citation': 'Therapeutic Guidelines'
            }
        }

        passed, errors = agent.validate_output(sample_task, output)

        assert not passed
        assert any('unit' in error.lower() or 'dosage' in error.lower() for error in errors)

    # Test 7: Red Flag Detection
    def test_red_flag_detection(self, agent):
        """Test red flag conditions are properly identified"""
        emergency_task = AgentTask(
            title="Emergency case",
            description="Patient with chest pain radiating to arm with diaphoresis",
            metadata={'type': 'assessment'}
        )

        result = agent.execute_task(emergency_task)
        output = result['output']

        assert output.get('red_flag') is True
        assert 'acute coronary syndrome' in output.get('suspected_condition', '').lower()
        assert '000' in output.get('action', '')  # Australian emergency number

    # Test 8: Task Capacity Management
    def test_agent_capacity_management(self, agent):
        """Test agent respects max_concurrent_tasks limit"""
        # Agent max_concurrent_tasks = 5 (from metadata)

        # Assign 5 tasks (should succeed)
        for i in range(5):
            task = AgentTask(title=f"Task {i}")
            success = agent.assign_task(task)
            assert success is True

        # Try to assign 6th task (should fail)
        extra_task = AgentTask(title="Extra task")
        success = agent.assign_task(extra_task)
        assert success is False

    # Test 9: Error Handling
    def test_error_handling(self, agent):
        """Test agent handles errors gracefully"""
        invalid_task = AgentTask(
            title="Invalid task",
            description="",  # Empty description should cause error
            metadata={}  # Missing required metadata
        )

        result = agent.execute_task(invalid_task)

        assert result['status'] == 'error'
        assert 'error' in result
        assert 'error_type' in result

    # Test 10: Run Task Workflow
    def test_run_task_workflow(self, agent, sample_task):
        """Test complete task workflow via run_task()"""
        # Initial state
        assert sample_task.status == TaskStatus.PENDING

        # Run task (uses BaseAgent.run_task)
        result_task = agent.run_task(sample_task)

        # Check final state
        assert result_task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]

        if result_task.status == TaskStatus.COMPLETED:
            assert result_task.result is not None
            assert result_task.completed_at is not None
        else:
            assert result_task.error is not None
```

### 6.2 Integration Test Requirements

**Test multi-agent workflows:**

```python
import pytest
from src.agents.pm_001_project_manager import ProjectManagerAgent
from src.agents.med_001_cardiology import CardiologyExpert
from src.agents.qa_001_medical_qa import MedicalQAAgent
from src.agents.ai_001_rag_system import RAGSystemAgent

class TestMCQGenerationWorkflow:
    """Integration tests for MCQ generation workflow"""

    @pytest.fixture
    def setup_agents(self):
        """Setup all agents for workflow"""
        pm = ProjectManagerAgent()
        rag = RAGSystemAgent()
        medical = CardiologyExpert()
        qa = MedicalQAAgent()

        # Register agents with PM
        pm.register_agent(rag)
        pm.register_agent(medical)
        pm.register_agent(qa)

        return pm, rag, medical, qa

    def test_complete_mcq_workflow(self, setup_agents):
        """Test complete MCQ generation workflow end-to-end"""
        pm, rag, medical, qa = setup_agents

        # Create workflow task
        task = AgentTask(
            title="Generate Cardiology MCQ",
            description="Generate MCQ about acute coronary syndrome for ICRP preparation",
            metadata={
                'type': 'coordinate_agents',
                'workflow': [
                    {
                        'agent_id': 'AI-001',
                        'task_title': 'Retrieve ACS context from medical texts',
                        'task_description': 'Retrieve relevant context about acute coronary syndrome'
                    },
                    {
                        'agent_id': 'MED-001',
                        'task_title': 'Generate ACS MCQ',
                        'task_description': 'Generate MCQ based on retrieved context'
                    },
                    {
                        'agent_id': 'QA-001',
                        'task_title': 'Validate MCQ accuracy',
                        'task_description': 'Validate clinical accuracy and Australian context'
                    }
                ]
            }
        )

        # Execute workflow
        result = pm.execute_task(task)

        # Verify workflow succeeded
        assert result['status'] == 'success'
        assert len(result['workflow_results']) == 3

        # Verify each step
        for step_result in result['workflow_results']:
            assert step_result['assigned'] is True

        # Verify final MCQ quality
        # (In real test, would retrieve MCQ from medical agent's completed tasks)

    def test_workflow_with_qa_failure(self, setup_agents):
        """Test workflow handles QA rejection correctly"""
        # Test that workflow retries if QA fails validation
        # Maximum 3 attempts before failing completely
        pass

    def test_parallel_agent_execution(self, setup_agents):
        """Test multiple agents can work simultaneously"""
        pm, rag, medical, qa = setup_agents

        # Create multiple independent tasks
        tasks = [
            AgentTask(title=f"Task {i}", metadata={'type': 'independent'})
            for i in range(3)
        ]

        # Assign to different agents
        pm.assign_task_to_agent(tasks[0], 'AI-001')
        pm.assign_task_to_agent(tasks[1], 'MED-001')
        pm.assign_task_to_agent(tasks[2], 'QA-001')

        # Verify all accepted
        assert len(rag.current_tasks) == 1
        assert len(medical.current_tasks) == 1
        assert len(qa.current_tasks) == 1
```

### 6.3 Medical Accuracy Validation Tests

**Automated medical accuracy checks:**

```python
import pytest

class TestMedicalAccuracy:
    """Tests for medical accuracy validation"""

    def test_drug_dosage_validation(self):
        """Test drug dosage includes all required information"""
        from src.validators.medical_validator import MedicalContentValidator

        # Valid dosage info
        dosage_info = {
            'drug': 'amoxicillin',
            'dose': '500 mg',  # ✓ Has units
            'frequency': 'TDS',  # ✓ Has frequency
            'duration': '5 days',  # ✓ Has duration
            'indication': 'Community-acquired pneumonia',
            'citation': 'Therapeutic Guidelines: Antibiotic, Section 2.3'  # ✓ Has citation
        }

        validator = MedicalContentValidator()
        is_valid, errors = validator.validate_drug_info(dosage_info)

        assert is_valid
        assert len(errors) == 0

        # Invalid dosage info - missing units
        invalid_dosage = {
            'drug': 'amoxicillin',
            'dose': '500',  # ❌ Missing units
            'frequency': 'TDS',
            'citation': 'Therapeutic Guidelines'
        }

        is_valid, errors = validator.validate_drug_info(invalid_dosage)
        assert not is_valid
        assert any('unit' in error.lower() for error in errors)

    def test_red_flag_detection(self):
        """Test red flag conditions are properly detected"""
        from src.validators.red_flag_detector import RedFlagDetector

        # Critical presentation
        symptoms = {
            'chest_pain': True,
            'radiation': 'left arm',
            'diaphoresis': True,
            'nausea': True
        }

        detector = RedFlagDetector()
        result = detector.check_symptoms(symptoms)

        assert result['is_red_flag'] is True
        assert 'acute coronary syndrome' in result['suspected_condition'].lower()
        assert 'immediate' in result['recommended_action'].lower()
        assert '000' in result['recommended_action']  # Australian emergency number

        # Non-critical presentation
        symptoms = {
            'chest_pain': True,
            'worse_with_deep_breath': True,
            'pleuritic': True
        }

        result = detector.check_symptoms(symptoms)

        # May still be concerning but not immediately life-threatening
        assert 'pulmonary embolism' in result['differential_diagnoses']

    def test_australian_terminology_validation(self):
        """Test Australian medical terminology is enforced"""
        from src.validators.terminology_validator import TerminologyValidator

        validator = TerminologyValidator(region='australia')

        # Test spelling
        assert validator.is_valid_term('paediatric') is True
        assert validator.is_valid_term('pediatric') is False

        # Test drug names
        assert validator.is_valid_drug_name('paracetamol') is True
        assert validator.is_valid_drug_name('acetaminophen') is False

        # Test healthcare terms
        assert validator.is_valid_term('GP') is True
        assert validator.is_valid_term('PCP') is False
```

### 6.4 Performance Benchmarks

**Set and test performance targets:**

```python
import pytest
import time
from src.agents.ai_001_rag_system import RAGSystemAgent

class TestPerformance:
    """Performance benchmark tests"""

    def test_rag_retrieval_performance(self):
        """Test RAG retrieval meets <500ms target"""
        rag = RAGSystemAgent()
        query = "What is the treatment for acute coronary syndrome in Australia?"

        start_time = time.time()
        results = rag.semantic_search(query, top_k=5)
        elapsed_ms = (time.time() - start_time) * 1000

        # Performance target: < 500ms
        assert elapsed_ms < 500, f"RAG retrieval took {elapsed_ms:.1f}ms (target: <500ms)"
        assert len(results) == 5

        # Verify result quality
        for result in results:
            assert 'text' in result
            assert 'source' in result
            assert 'score' in result
            assert result['score'] > 0.5  # Relevance threshold

    def test_mcq_generation_performance(self):
        """Test MCQ generation completes in reasonable time"""
        from src.agents.med_001_cardiology import CardiologyExpert

        agent = CardiologyExpert()
        task = AgentTask(
            title="Generate MCQ",
            metadata={'type': 'generate_mcq', 'topic': 'ACS'}
        )

        start_time = time.time()
        result = agent.execute_task(task)
        elapsed_sec = time.time() - start_time

        # Performance target: < 15 seconds
        assert elapsed_sec < 15, f"MCQ generation took {elapsed_sec:.1f}s (target: <15s)"
        assert result['status'] == 'success'

    def test_batch_processing_efficiency(self):
        """Test batch processing scales efficiently"""
        from src.processors.medical_text_processor import MedicalTextProcessor

        processor = MedicalTextProcessor()

        # Test with increasing batch sizes
        for num_items in [10, 50, 100, 500]:
            items = [f"item_{i}" for i in range(num_items)]

            start_time = time.time()
            results = processor.process_batch(items, batch_size=100)
            elapsed = time.time() - start_time

            items_per_second = num_items / elapsed

            # Should process at least 50 items/second
            assert items_per_second > 50, f"Only {items_per_second:.1f} items/sec (target: >50)"
```

---

## 7. Documentation Standards

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

## 8. Agent-Specific Requirements

### 8.1 Medical Expert Agents (MED-XXX)

**Mandatory Requirements:**

1. **Citations**: MUST cite Therapeutic Guidelines or equivalent for every medical claim
2. **Terminology**: MUST use Australian spelling and drug names
3. **Validation**: MUST validate clinical accuracy in `validate_output()`
4. **Red Flags**: MUST identify and flag life-threatening conditions
5. **Dosages**: MUST specify drug dosages with units (mg, mcg, mL)
6. **SI Units**: MUST use SI units (mmol/L, not mg/dL)
7. **Emergency**: MUST use "Call 000" for emergencies (Australian number)

**Agent List:**
- MED-001: Cardiology Clinical Expert
- MED-002: Emergency Medicine Expert
- MED-003: General Practice Expert
- MED-004: Paediatrics Expert
- MED-005: Obstetrics & Gynaecology Expert
- MED-006: Surgery Expert
- MED-007: Psychiatry Expert
- MED-008: Endocrinology Expert
- MED-009: Gastroenterology Expert
- MED-010: Respiratory Medicine Expert
- MED-011: Neurology Expert
- MED-012: Rheumatology Expert
- MED-013: Infectious Diseases Expert
- MED-014: Dermatology Expert
- MED-015: Medical QA Validator (quality assurance for all medical content)

### 8.2 Development Agents (DEV-XXX)

**Mandatory Requirements:**

1. **Testing**: MUST write unit tests with 80%+ coverage
2. **Code Style**: MUST follow PEP 8 (Python) or ESLint/Prettier (TypeScript)
3. **Documentation**: MUST document APIs with OpenAPI (FastAPI) or TypeDoc (TypeScript)
4. **Error Handling**: MUST handle errors gracefully with specific exceptions
5. **Type Safety**: MUST use type hints (Python) or TypeScript types
6. **Logging**: MUST use structured logging (not print statements)
7. **Security**: MUST follow OWASP Top 10 security practices

**Agent List:**
- DEV-001: Senior Backend Architect (Python/FastAPI)
- DEV-002: Senior Frontend Architect (Next.js/React)
- DEV-003: UI/UX Specialist & Design System Engineer
- DEV-004: Database Engineer (PostgreSQL/SQLAlchemy)
- DEV-005: Authentication & Authorization Engineer (OAuth2/JWT)
- DEV-006: API Integration Engineer
- DEV-007: WebSocket & Real-time Engineer
- DEV-008: Payment Systems Engineer
- DEV-009: Email & Notifications Engineer
- DEV-010: Search Engineer (Elasticsearch)
- DEV-011: File Storage Engineer
- DEV-012: Caching Engineer (Redis)

### 8.3 AI/Data Agents (AI-XXX)

**Mandatory Requirements:**

1. **LLM Access**: MUST use OllamaClient for LLM access (never direct API calls)
2. **Token Limits**: MUST handle token limits (4K-8K tokens)
3. **Fallback**: MUST implement fallback strategies for LLM failures
4. **Performance**: MUST track and report performance metrics
5. **Quality**: MUST validate embeddings quality and search relevance
6. **Progress**: MUST use tqdm for long-running operations
7. **Memory**: MUST batch process large datasets

**Agent List:**
- AI-001: RAG System Engineer (Qdrant + PubMedBERT embeddings)
- AI-002: LLM Operations Engineer (Prompt engineering, model selection)
- AI-003: Medical NLP Engineer (Named Entity Recognition)
- AI-004: ETL Engineer (PDF → Text → Chunks → Embeddings → Qdrant)
- AI-005: Question Generator (MCQ generation with medical accuracy)
- AI-006: Answer Validator (Validate correctness and clinical accuracy)
- AI-007: Semantic Search Engineer (Vector search optimization)
- AI-008: ML Model Trainer (Train/fine-tune medical models)

### 8.4 QA Agents (QA-XXX)

**Mandatory Requirements:**

1. **Quality Gates**: MUST run all configured quality gates
2. **Coverage**: MUST achieve 80%+ test coverage
3. **Security**: MUST catch and report security vulnerabilities
4. **Medical**: MUST validate medical accuracy for medical content
5. **Accessibility**: MUST test WCAG 2.1 AA compliance
6. **Performance**: MUST validate performance targets met
7. **Reporting**: MUST generate detailed test reports

**Agent List:**
- QA-001: Medical Content QA (Clinical accuracy validator)
- QA-002: E2E Testing Engineer (Playwright, integration tests)
- QA-003: Performance Testing Engineer (Load tests, stress tests)
- QA-004: Security Testing Engineer (OWASP Top 10, vulnerability scanning)

### 8.5 DevOps & Infrastructure Agents (DEVOPS-XXX)

**Mandatory Requirements:**

1. **CI/CD**: MUST maintain CI/CD pipelines
2. **Monitoring**: MUST implement comprehensive monitoring
3. **Logging**: MUST aggregate and analyze logs
4. **Scaling**: MUST handle auto-scaling configurations
5. **Backup**: MUST implement backup and disaster recovery
6. **Security**: MUST apply security patches promptly
7. **Documentation**: MUST document infrastructure as code

**Agent List:**
- DEVOPS-001: Kubernetes Engineer (K8s, Helm charts)
- DEVOPS-002: CI/CD Engineer (GitHub Actions, deployment pipelines)
- DEVOPS-003: Monitoring & Observability Engineer (Prometheus, Grafana)
- DEVOPS-004: Database DevOps Engineer (PostgreSQL, Qdrant management)
- DEVOPS-005: Cloud Infrastructure Engineer (AWS/Azure/GCP)
- DEVOPS-006: Security & Compliance Engineer (Secrets management, compliance)

### 8.6 Inter-Agent Communication Pattern

**Standard task delegation via PM-001:**

```python
# ✅ CORRECT - PM delegates to specialist
from src.agents.pm_001_project_manager import ProjectManagerAgent
from src.agents.med_001_cardiology import CardiologyExpert

pm = ProjectManagerAgent()
cardiology_agent = CardiologyExpert()

# Register agent with PM
pm.register_agent(cardiology_agent)

# Create task
task = AgentTask(
    title="Generate Cardiology MCQ",
    description="Generate medium difficulty MCQ about acute coronary syndrome",
    metadata={
        'type': 'generate_mcq',
        'topic': 'acute_coronary_syndrome',
        'difficulty': 'medium'
    }
)

# Delegate via PM
success = pm.assign_task_to_agent(task, agent_id="MED-001")

if success:
    # Agent executes via run_task (handles validation)
    result = cardiology_agent.run_task(task)

    if result.status == TaskStatus.COMPLETED:
        print(f"MCQ generated successfully: {result.result}")
    else:
        print(f"Task failed: {result.error}")
```

---

## 9. Project-Specific Context

### 9.1 Target Audience

**ICRP Candidates (International Medical Graduates)**

- **Background**: Qualified doctors from overseas seeking Australian medical registration
- **Goal**: Pass AMC Clinical Exam (OSCE format) to practice medicine in Australia
- **Timeline**: March 2 - May 22, 2026 (Young District Hospital ICRP program)
- **Location**: NSW, Australia
- **Exam Type**: AMC Clinical Exam - 16 OSCE stations × 8 minutes each

**Key Needs:**
- Australian medical practice standards and terminology
- NSW Health protocols and guidelines
- Clinical examination techniques (Australian context)
- Case-based scenario practice
- Red flag recognition and emergency management
- Communication skills for Australian healthcare system

### 9.2 Exam Context - AMC Clinical Exam (OSCE)

**Format**: 16 stations × 8 minutes each

**Content Distribution:**
- History taking (40%)
- Physical examination (30%)
- Diagnosis & management (20%)
- Communication skills (10%)

**Key Skills Tested:**
- Clinical reasoning with Australian context
- Physical examination techniques (proper consent, draping)
- Red flag recognition (emergency identification)
- Patient communication (Australian cultural norms)
- Australian medical system navigation (GP referrals, Medicare, PBS)

**Common Station Types:**
- History taking (chest pain, abdominal pain, shortness of breath)
- Cardiovascular examination
- Respiratory examination
- Abdominal examination
- Neurological examination
- Breaking bad news
- Informed consent discussions
- Medication counseling (PBS medications)

### 9.3 Clinical Context - Young Hospital ICRP Program

**Program Details:**
- **Location**: Young District Hospital, NSW, Australia
- **Duration**: 12 weeks (March 2 - May 22, 2026)
- **Supervision**: Senior medical staff (registrars, consultants)
- **Rotations**: Emergency Department, General Medicine, Surgery, GP clinics
- **Goal**: Prepare candidates for AMC Clinical Exam through supervised practice

**Clinical Focus:**
- Common presentations: chest pain, abdominal pain, SOB, headache, fever
- Emergency medicine scenarios: sepsis, ACS, stroke, trauma
- Chronic disease management: diabetes, hypertension, COPD, heart failure
- Preventive health: cancer screening, cardiovascular risk assessment, immunization
- Aboriginal & Torres Strait Islander health considerations

### 9.4 Geographic Context - NSW Health System

**Healthcare Structure:**

**Primary Care:**
- GP clinics (bulk-billed or private)
- Aboriginal Medical Services (AMS)
- Community health centers

**Emergency Care:**
- Emergency Departments (public hospitals)
- Triage system (categories 1-5)
- Ambulance service (call 000)

**Specialty Care:**
- Referral via GP (gatekeeping model)
- Public hospital outpatient clinics
- Private specialists

**Medications:**
- PBS (Pharmaceutical Benefits Scheme) - subsidized medications
- Authority prescriptions for restricted PBS medications
- TGA (Therapeutic Goods Administration) approval required

**Guidelines:**
- NSW Health Clinical Practice Guidelines
- Therapeutic Guidelines (eTG) - national standards
- AMH (Australian Medicines Handbook)

### 9.5 Timeline & Milestones

**Current Phase**: Development (December 2025)

**Preparation Phase** (December 2025 - February 2026):
- Develop 46-agent AI system
- Create MCQ question bank (1000+ questions)
- Build OSCE practice platform
- Generate clinical vignettes and flashcards

**ICRP Phase** (March 2 - May 22, 2026):
- Candidates use platform for study
- Practice OSCE stations
- Review clinical guidelines
- Prepare for AMC Clinical Exam

**Target Outcomes:**
- 90%+ pass rate for AMC Clinical Exam
- Confident in Australian medical practice
- Ready for PGY1/resident positions in Australia

---

## 10. Anti-Patterns (What NOT to Do)

### 10.1 Security Anti-Patterns (CRITICAL)

```python
# ❌ NEVER hardcode credentials
DATABASE_URL = "postgresql://user:password@localhost/db"
API_KEY = "sk-abc123..."
SECRET_KEY = "my-secret-key"

# ❌ NEVER commit secrets to git
.env file with real credentials committed

# ❌ NEVER log sensitive data
logger.info(f"User password: {password}")
logger.info(f"API key: {api_key}")

# ❌ NEVER use weak crypto
password_hash = md5(password)  # MD5 is broken
jwt_token = jwt.encode(payload, 'secret', algorithm='none')  # No encryption!
```

### 10.2 Medical Anti-Patterns (CRITICAL)

```python
# ❌ NEVER use American spelling
drug_name = "acetaminophen"  # Should be "paracetamol"
condition = "pediatric anemia"  # Should be "paediatric anaemia"

# ❌ NEVER omit dosage units
dosage = "500"  # Should be "500 mg"
dose = "15"  # Should be "15 mg/kg"

# ❌ NEVER skip citations
explanation = "Metformin is first-line for diabetes"  # Missing citation

# ❌ NEVER use non-Australian guidelines without context
reference = "UpToDate"  # Use Therapeutic Guidelines instead

# ❌ NEVER use American units
glucose = "100 mg/dL"  # Should be "5.5 mmol/L" (SI units)

# ❌ NEVER use American emergency number
action = "Call 911"  # Should be "Call 000" (Australian)

# ❌ NEVER miss red flags
if chest_pain:
    return "Take aspirin"  # Should assess for ACS and call 000 if indicated
```

### 10.3 Code Anti-Patterns (CRITICAL)

```python
# ❌ NEVER bypass BaseAgent
class MyAgent:  # Should extend BaseAgent
    pass

# ❌ NEVER use print() for logging
print("Task started")  # Use self.logger.info()

# ❌ NEVER ignore exceptions
try:
    risky_operation()
except:  # Bare except
    pass  # Silent failure!

# ❌ NEVER use string paths
path = "data" + "/" + "file.json"  # Use pathlib.Path()

# ❌ NEVER skip type hints
def process(data):  # What type is data?
    pass

# ❌ NEVER hardcode file paths with credentials
path = "/home/user/.ssh/id_rsa"  # Never hardcode sensitive paths

# ❌ NEVER use mutable default arguments
def process(items=[]):  # Bug: mutable default!
    items.append("new")
    return items
```

### 10.4 Performance Anti-Patterns

```python
# ❌ NEVER load entire large file into memory
with open('large_file.json') as f:
    data = json.load(f)  # Could be GBs!

# ❌ NEVER make synchronous calls in loops
for item in items:
    result = slow_api_call(item)  # Should batch or use async

# ❌ NEVER skip progress indicators
for item in large_list:  # Should use tqdm()
    process(item)

# ❌ NEVER re-process already processed data
# Should check if output exists before re-processing

# ❌ NEVER use inefficient algorithms
for i in range(len(list1)):  # O(n²)
    for j in range(len(list2)):
        if list1[i] == list2[j]:
            # Should use set intersection O(n)
```

### 10.5 Testing Anti-Patterns

```python
# ❌ NEVER skip validation
result = agent.execute_task(task)  # Should use run_task()

# ❌ NEVER hardcode test data
user_id = "test-user-123"  # Use fixtures with uuid

# ❌ NEVER skip error cases
def test_success_only():  # Should also test failures
    assert result['status'] == 'success'

# ❌ NEVER skip integration tests
# Only unit tests without integration tests

# ❌ NEVER skip performance tests
# No benchmarks or performance validation
```

### 10.6 Documentation Anti-Patterns

```python
# ❌ NEVER skip docstrings
def complex_function(x, y, z):  # Needs docstring!
    pass

# ❌ NEVER skip type hints
def process(data):  # What type is data?
    pass

# ❌ NEVER use vague comments
# Fix bug
x += 1  # What bug? Why this fix?

# ❌ NEVER skip README for modules
# No README.md in module directory

# ❌ NEVER skip examples in documentation
# No usage examples provided
```

### 10.7 LLM Integration Anti-Patterns

```python
# ❌ NEVER use LLM directly without OllamaClient
import requests
response = requests.post('http://localhost:11434/api/generate', ...)  # Use OllamaClient!

# ❌ NEVER ignore token limits
prompt = long_text_with_50000_chars  # Exceeds 4K token limit!

# ❌ NEVER skip fallback strategy
response = ollama.generate(prompt, model='llama3.1:70b')  # What if it fails?

# ❌ NEVER use wrong temperature
medical_facts = ollama.generate(prompt, temperature=0.9)  # Too high for facts!
creative_task = ollama.generate(prompt, temperature=0.1)  # Too low for creativity!
```

---

## 11. ICRP Clinical Training Standards

### 11.1 History Taking Structure (9-Step System)

**ALL history-taking content MUST follow this structure:**

1. **Presenting Complaint**: Patient's chief complaint in their own words
2. **History of Presenting Complaint (HPC)**:
   - Use SOCRATES for pain: Site, Onset, Character, Radiation, Associated symptoms, Timing, Exacerbating/Relieving factors, Severity
   - Systematic exploration of current symptoms
3. **Past Medical History (PMH)**: Previous medical conditions, hospitalizations, surgeries
4. **Medications**: Current medications (include dose, frequency), over-the-counter, supplements
5. **Allergies**: Drug allergies and reactions (specify type of reaction)
6. **Family History (FHx)**: Relevant family medical history (especially hereditary conditions)
7. **Social History (SHx)**: Smoking, alcohol, drugs, occupation, living situation
8. **Review of Systems (ROS)**: Systematic review of other systems
9. **Summary**: Concise summary of key findings and differential diagnoses

**Reference**: `/home/dev/Development/irStudy/ICRP_Program_Resources/01_History_Taking_Mastery_Guide.md`

### 11.2 Physical Examination Framework (5 Ps)

**ALL physical examination content MUST follow this framework:**

1. **Preparation**:
   - Wash hands
   - Introduce self
   - Confirm patient identity
   - Explain procedure
   - Ensure privacy

2. **Position**:
   - Position patient appropriately for examination
   - Ensure patient comfort
   - Ensure adequate exposure with appropriate draping

3. **Permission**:
   - "Is it okay if I examine your [area]?"
   - Obtain verbal consent
   - Offer chaperone if appropriate

4. **Perform**:
   - Systematic examination following standard sequence
   - Inspection → Palpation → Percussion → Auscultation (where applicable)
   - Look for general signs first, then specific findings

5. **Present**:
   - Present findings to examiner
   - Summarize positive and relevant negative findings
   - Provide differential diagnoses
   - Suggest appropriate investigations

**Reference**: `/home/dev/Development/irStudy/ICRP_Program_Resources/02_Physical_Examination_Skills_Guide.md`

### 11.3 SOAP Note Format (Australian Clinical Context)

**ALL clinical documentation MUST use SOAP format:**

```
S - Subjective (Patient's complaint in their words)
    - Presenting complaint
    - History of presenting complaint
    - Relevant PMHx, medications, allergies

O - Objective (Examination findings, vitals, investigations)
    - Vital signs: BP, HR, RR, Temp, SpO2
    - Physical examination findings
    - Investigation results (bloods, imaging, ECG)

A - Assessment (Diagnosis/differential diagnosis)
    - Primary diagnosis
    - Differential diagnoses (ranked by likelihood)
    - Clinical reasoning

P - Plan (Management plan, follow-up)
    - Immediate management
    - Investigations ordered
    - Treatment initiated (medications with doses)
    - Follow-up arrangements
    - Safety-netting advice
```

**Reference**: Original PROJECT_CONSTRAINTS.md section "Medical Documentation Standards"

### 11.4 OSCE Structure Requirements

**ALL OSCE materials MUST include these 7 elements:**

1. **Opening Statement** (30 seconds):
   - Examiner-friendly introduction
   - Clear task description
   - Example: "I'm going to take a focused cardiovascular history from this patient presenting with chest pain."

2. **Focused History**:
   - Systematic approach with key questions
   - Use SOCRATES for pain
   - Include red flag questions

3. **Examination Steps**:
   - Clear, sequential physical examination
   - Follow 5 Ps framework
   - Completable in 8 minutes

4. **Differentials**:
   - Top 3 differential diagnoses
   - Ranked by likelihood
   - Brief justification for each

5. **Investigations**:
   - Appropriate for Australian primary care context
   - Note if Medicare bulk-billed or out-of-pocket
   - Include rationale

6. **Management**:
   - According to Australian guidelines (eTG, AMH)
   - Medications: Australian drug names, dosages with units, PBS status
   - Referrals: GP, specialist, Emergency Department

7. **Counselling & Safety-netting**:
   - Patient communication skills
   - Red flags to return for immediately
   - Follow-up plan
   - Example: "If you develop severe chest pain, shortness of breath, or pain radiating to your arm, call 000 immediately."

**Reference**: Original PROJECT_CONSTRAINTS.md section "AMC Clinical / OSCE Standards"

### 11.5 Time Estimates & Practice Standards

**Daily Practice Minimums:**
- History Taking: 2-3 practice histories (15-20 min each)
- Physical Examination: 1 complete examination (15-20 min)
- Typing Practice: 30-60 minutes daily
- Documentation: 1-2 SOAP notes (real or simulated cases)

**Weekly Targets:**
- History Taking: 15-20 histories per week
- Physical Examination: 7-10 examinations per week
- Typing Practice: 3.5-7 hours per week
- Total Study Time: 15-20 hours per week

**By March 2, 2026 (ICRP Start):**
- 400+ history taking practice scenarios completed
- 100+ physical examinations performed
- 40+ WPM typing speed with 95%+ accuracy
- Clinical notes completed in 10-15 minutes
- SOAP note format mastered

**Reference**: Original PROJECT_CONSTRAINTS.md section "Practice Standards"

---

## Validation Checklist

**Before submitting ANY code, verify:**

### Code Quality
- [ ] Extended BaseAgent (if creating new agent)
- [ ] Used correct agent_id format (PREFIX-XXX)
- [ ] Type hints on all functions
- [ ] Docstrings (Google-style) on all functions
- [ ] Error handling (try-except with specific exceptions)
- [ ] Logging with self.logger (not print statements)

### Security
- [ ] NO hardcoded credentials or secrets
- [ ] NO sensitive data in logs
- [ ] Used environment variables for configuration
- [ ] Used pathlib.Path (not string paths)

### Medical Accuracy
- [ ] Australian spelling for medical terms (paediatric, anaesthesia)
- [ ] Australian drug names (paracetamol, adrenaline)
- [ ] Citations for all medical claims (Therapeutic Guidelines)
- [ ] Dosage units specified (mg, mcg, mL)
- [ ] Red flags identified for emergencies
- [ ] SI units used (mmol/L, not mg/dL)
- [ ] Australian emergency number (000, not 911)

### Testing
- [ ] Unit tests written (80%+ coverage target)
- [ ] Integration tests for multi-agent workflows
- [ ] Medical accuracy validation tests
- [ ] Performance benchmarks met
- [ ] All tests passing

### Data Processing
- [ ] JSON files use encoding='utf-8'
- [ ] Progress bars for long operations (tqdm)
- [ ] Batch processing for large datasets
- [ ] Proper error handling for file operations

### LLM Integration
- [ ] Used OllamaClient (not direct API calls)
- [ ] Handled token limits (4K-8K tokens)
- [ ] Implemented fallback strategy
- [ ] Used appropriate temperature for task type
- [ ] Structured prompts with clear requirements

### Documentation
- [ ] README.md created/updated
- [ ] Module docstring present
- [ ] Usage examples provided
- [ ] Performance metrics documented
- [ ] Dependencies listed

---

## References

### Key Project Files

**Agent Framework:**
- `/home/dev/Development/irStudy/src/agents/base_agent.py` - BaseAgent class (MUST READ)
- `/home/dev/Development/irStudy/src/agents/pm_001_project_manager.py` - PM example
- `/home/dev/Development/irStudy/src/agents/workflows/orchestration.py` - Multi-agent workflows

**LLM Integration:**
- `/home/dev/Development/irStudy/src/models/ollama_client.py` - LLM client (MUST READ)

**Data Processing:**
- `/home/dev/Development/irStudy/scripts/extract_pdfs.py` - PDF extraction example
- `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py` - Text chunking example
- `/home/dev/Development/irStudy/scripts/generate_embeddings.py` - Embedding generation
- `/home/dev/Development/irStudy/scripts/index_qdrant.py` - Vector database indexing

**Documentation:**
- `/home/dev/Development/irStudy/docs/AGENT_SPECIFICATIONS.md` - Agent architecture
- `/home/dev/Development/irStudy/00_PROJECT_OVERVIEW.md` - Project overview

### External Australian Medical Standards

**Primary Guidelines:**
- [Therapeutic Guidelines](https://tg.org.au/) - Primary Australian treatment guidelines
- [Australian Medicines Handbook (AMH)](https://amhonline.amh.net.au/) - Drug information
- [PBS](https://www.pbs.gov.au/) - Pharmaceutical Benefits Scheme
- [AHPRA](https://www.ahpra.gov.au/) - Australian Health Practitioner Regulation Agency
- [AMC](https://www.amc.org.au/) - Australian Medical Council
- [NSW Health](https://www.health.nsw.gov.au/) - NSW Health guidelines

**Clinical Resources:**
- Harrison's Principles of Internal Medicine (21st Edition)
- Talley & O'Connor's Clinical Examination (8th Edition)
- Murtagh's General Practice (8th Edition)
- Oxford Handbook of Emergency Medicine (5th Edition)

### Coding Standards

**Python:**
- [PEP 8](https://pep8.org/) - Python style guide
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Type Hints - PEP 484](https://www.python.org/dev/peps/pep-0484/)

**TypeScript:**
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [ESLint](https://eslint.org/)
- [Prettier](https://prettier.io/)

**Testing:**
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Playwright](https://playwright.dev/)

---

## Version History

- **2.0.0** (2025-12-18): Comprehensive multi-agent system standards
  - Added 10 sections covering all aspects of agent development
  - Medical accuracy standards (Australian context)
  - Code architecture patterns (BaseAgent)
  - Security & configuration (zero tolerance for hardcoded secrets)
  - LLM integration patterns (OllamaClient)
  - Data processing standards (JSON, tqdm, Path)
  - Testing requirements (80%+ coverage)
  - Documentation standards (Google-style docstrings)
  - Agent-specific requirements (46 agents across 6 categories)
  - Project-specific context (ICRP program details)
  - Anti-patterns (what NOT to do)
  - ICRP clinical training standards (preserved from v1.1)

- **1.1** (2025-12-14): Added AMC Clinical / OSCE Standards
- **1.0** (2025-12-13): Initial version (ICRP clinical training focus)

---

## Critical Reminders

### For ALL Agents:
1. **READ THIS FILE FIRST** before starting ANY work
2. **Follow Australian medical standards** - no exceptions
3. **Extend BaseAgent** - don't create agents from scratch
4. **NO hardcoded secrets** - zero tolerance policy
5. **Use OllamaClient** for LLM access - no direct API calls
6. **Write tests** - 80%+ coverage required
7. **Document everything** - docstrings, type hints, READMEs

### For Medical Agents (MED-XXX):
1. **Australian spelling** - paediatric, anaesthesia, anaemia
2. **Australian drug names** - paracetamol, adrenaline, salbutamol
3. **Cite Therapeutic Guidelines** - every medical claim
4. **Include dosage units** - mg, mcg, mL
5. **Identify red flags** - life-threatening conditions
6. **Use SI units** - mmol/L, not mg/dL
7. **Call 000 for emergencies** - not 911

### For Development Agents (DEV-XXX):
1. **Type hints** - on all functions
2. **Error handling** - specific exceptions, no bare except
3. **Logging** - structured logging, not print()
4. **Testing** - unit + integration tests
5. **Security** - follow OWASP Top 10
6. **Performance** - optimize for speed and memory
7. **Documentation** - OpenAPI for APIs, READMEs for modules

### For AI/Data Agents (AI-XXX):
1. **OllamaClient** - always use the client
2. **Token limits** - chunk if needed (4K-8K tokens)
3. **Fallback strategy** - multiple model attempts
4. **Progress bars** - tqdm for long operations
5. **Batch processing** - manage memory usage
6. **Performance tracking** - log metrics
7. **Quality validation** - test search relevance

### Questions?
If ANY constraint is unclear:
1. Read the relevant reference files listed above
2. Search for similar existing code in the project
3. Ask the Project Manager (PM-001) BEFORE proceeding
4. DO NOT guess or assume - clarity prevents mistakes

### Updates
This document will be updated as new patterns emerge. **Always use the latest version.**

---

**Last Updated**: 2025-12-18
**Version**: 2.0.0
**Maintained By**: PM-001 (Project Manager)
**Status**: **MANDATORY READING FOR ALL AGENTS**
