# Code Architecture & Patterns

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Code Architecture & Patterns

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

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
