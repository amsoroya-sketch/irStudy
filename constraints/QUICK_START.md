# Quick Start for Agents

**Read this FIRST before any task. Time: 2 minutes.**

[← Back to Index](README.md)

---

## 🚨 Critical Rules (Top 10)

### 1. Australian Medical Context ONLY
- **Use**: paracetamol, paediatric, anaesthesia, paed haemoglobin, anaemia
- **Never**: acetaminophen, pediatric, anesthesia, hemoglobin, anemia
- **Sources**: Therapeutic Guidelines (eTG), PBS, AHPRA, AMC, NSW Health
- **Not**: American guidelines, UpToDate without context

### 2. Security: NEVER Hardcode Credentials
- ✅ `ref.read(databaseConfigProvider)` or environment variables
- ❌ `const userId = 'mock-user-id'`
- ❌ `dbPath: 'path/to/db'` directly in code
- ❌ API keys, passwords, encryption keys in code
- **Zero tolerance policy** - immediate fix required

### 3. Extend BaseAgent for All Agents
- ✅ `class MyAgent(BaseAgent):`
- ❌ Custom agent classes from scratch
- Required: AgentMetadata with proper agent_id format (PREFIX-XXX)
- Auto-handles: logging, task tracking, validation workflow

### 4. RAG-Verify All Medical Citations
- **Books**: MUST include page numbers `(Talley & O'Connor's Clinical Examination, 8th ed, p.145)`
- **eTG**: MUST include section numbers `(Therapeutic Guidelines: Paediatric, Section 2.3.1, 2024)`
- **RAG confidence**: >0.65 threshold for auto-citations
- ❌ Generic citations without page/section numbers

### 5. Use Structured Logging (Never print())
- ✅ `self.logger.info(f"Starting task: {task.title}")`
- ✅ `self.logger.error(f"Error: {e}", exc_info=True)`
- ❌ `print("Starting task")`
- Format: `[AGENT-ID] TIMESTAMP - LEVEL - MESSAGE`

### 6. Async LLM Calls (Never Block UI)
- ✅ Use `OllamaClient` with async operations
- ✅ Implement timeout and rate limiting
- ✅ Handle errors gracefully with fallback strategies
- ❌ Synchronous calls that freeze the interface

### 7. Drug Dosages: Always Include Units
- ✅ `500 mg three times daily (TDS)`
- ✅ `15 mg/kg (max 60 mg/kg/day)`
- ❌ Just numbers without units
- Required: dose, frequency, duration, indication, citation

### 8. Identify Red Flags
- Life-threatening conditions MUST be flagged
- Use "Call 000" for emergencies (Australian number, not 911)
- Include immediate management steps
- Cite NSW Health protocols

### 9. Use SI Units (Australian Standard)
- ✅ `glucose: 5.5 mmol/L`
- ❌ `glucose: 100 mg/dL` (American units)
- Apply to: glucose, sodium, potassium, creatinine, etc.

### 10. Write Tests (80%+ Coverage Required)
- TDD: Write failing tests FIRST, then implementation
- Target: 100% pass rate, ≥70-80% coverage
- Use pytest with proper fixtures
- Quality gates enforced by hooks

---

## 🎯 Quick Decision Tree

### I'm implementing a new agent:
1. Read: [08-agent-requirements.md](08-agent-requirements.md) - Agent specifications
2. Then: [02-code-architecture.md](02-code-architecture.md) - BaseAgent inheritance pattern
3. Check: [CHECKLIST.md](CHECKLIST.md) - Pre-flight validation

**Template:**
```python
from src.agents.base_agent import BaseAgent, AgentMetadata, AgentRole

class MyAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            agent_id="PREFIX-XXX",  # MED-001, DEV-001, AI-001, etc.
            name="Agent Name",
            role=AgentRole.MEDICAL_EXPERT,  # or DEVELOPER, AI_ENGINEER, etc.
            # ... rest of metadata
        )
        super().__init__(metadata)
```

### I'm adding LLM calls:
1. Read: [04-llm-integration.md](04-llm-integration.md) - OllamaClient usage
2. Check: [CHECKLIST.md](CHECKLIST.md) - LLM validation section
3. Ensure: Async calls, rate limiting, error handling

**Template:**
```python
from src.models.ollama_client import OllamaClient

self.llm_client = OllamaClient()
response = await self.llm_client.generate_async(
    prompt=prompt,
    model="llama3.2:3b",
    temperature=0.7,
    max_tokens=1000
)
```

### I'm writing medical content:
1. Read: [01-medical-accuracy.md](01-medical-accuracy.md) - Australian standards
2. Must: RAG-verify all citations with exact page/section numbers
3. Must: Use Australian spelling, drug names, SI units
4. Check: No American terminology slips through

**Key Requirements:**
- Australian drug names: paracetamol (NOT acetaminophen), adrenaline (NOT epinephrine)
- Australian spelling: paediatric, anaesthesia, oesophagus, haemoglobin
- Citations: `(Source, Section X.Y.Z, year)` or `(Source, p.XXX)`
- Dosages: Include units, frequency, duration, citation

### I'm adding Flutter UI:
1. Read: [02-code-architecture.md](02-code-architecture.md) section 2.3
2. Never: Hardcode database config (see [03-security-configuration.md](03-security-configuration.md))
3. Pattern: Use `ref.read(databaseConfigProvider)` for all FFI calls

**Anti-Pattern (124 violations found in past):**
```dart
// ❌ WRONG - Hardcoded credentials
await ffi.method(
  userId: 'mock-user-id',  // NEVER hardcode
  dbPath: 'path/to/db',     // NEVER hardcode
  dbKey: 'secret-key'       // NEVER hardcode
);

// ✅ CORRECT - Use provider
final dbConfig = ref.read(databaseConfigProvider);
await ffi.method(
  userId: dbConfig.userId,
  dbPath: dbConfig.dbPath,
  dbKey: dbConfig.dbKey
);
```

### I'm processing patient data:
1. Read: [05-data-processing.md](05-data-processing.md) - PHI protection
2. Must: De-identify all personal health information
3. Must: Use UTF-8 encoding for all file I/O
4. Check: No sensitive data in logs

**De-identification Required:**
- Names → "Patient A", "Patient B"
- Dates → Relative ("3 days ago") or year only
- Locations → General ("Sydney hospital") not specific
- Contact info → NEVER log or store

### I'm writing tests:
1. Read: [06-testing-requirements.md](06-testing-requirements.md) - TDD workflow
2. Goal: 100% pass rate, ≥70-80% coverage
3. TDD: Write failing test → Implement → Pass → Refactor

**TDD Example:**
```python
# Step 1: Write failing test FIRST
def test_agent_validates_citation():
    agent = MyAgent()
    task = AgentTask(...)
    output = {'result': {'citation': None}}  # Missing citation
    
    is_valid, errors = agent.validate_output(task, output)
    assert not is_valid
    assert "Missing citation" in errors

# Step 2: Run test - should FAIL
# Step 3: Implement validation logic
# Step 4: Run test - should PASS
```

---

## ❌ Top Anti-Patterns (From 10-anti-patterns.md)

### 1. Using American Drug Names/Spelling
```python
# ❌ WRONG
drug = "acetaminophen"  # American name
condition = "pediatric anemia"  # American spelling

# ✅ CORRECT
drug = "paracetamol"  # Australian name
condition = "paediatric anaemia"  # Australian spelling
```

### 2. Hardcoding Credentials (Zero Tolerance)
```python
# ❌ WRONG - 124 violations found in past sprint
DATABASE_URL = "postgresql://user:password@localhost/db"
userId = 'mock-user-id'

# ✅ CORRECT
DATABASE_URL = os.getenv('DATABASE_URL')
userId = config.get('user_id')
```

### 3. Not Extending BaseAgent
```python
# ❌ WRONG
class MyAgent:
    def __init__(self):
        pass

# ✅ CORRECT
class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(metadata)
```

### 4. Missing RAG Citation Validation
```python
# ❌ WRONG
citation = "(Therapeutic Guidelines, 2024)"  # Too generic

# ✅ CORRECT
citation = "(Therapeutic Guidelines: Paediatric, Section 2.3.1, 2024)"
# With RAG confidence >0.65
```

### 5. Synchronous LLM Calls Blocking UI
```python
# ❌ WRONG
response = llm.generate(prompt)  # Blocks UI thread

# ✅ CORRECT
response = await llm.generate_async(prompt)  # Non-blocking
```

### 6. Using print() Instead of Logging
```python
# ❌ WRONG
print("Task started")

# ✅ CORRECT
self.logger.info("Task started")
```

### 7. Bare Except Clauses
```python
# ❌ WRONG
try:
    do_something()
except:  # Catches everything, even KeyboardInterrupt
    pass

# ✅ CORRECT
try:
    do_something()
except ValueError as e:
    self.logger.error(f"Validation error: {e}")
except Exception as e:
    self.logger.error(f"Unexpected error: {e}", exc_info=True)
```

### 8. Missing Units in Drug Dosages
```python
# ❌ WRONG
dosage = {"dose": "500"}  # No units!

# ✅ CORRECT
dosage = {
    "dose": "500 mg",
    "frequency": "TDS",
    "duration": "5-7 days",
    "citation": "(Therapeutic Guidelines: Antibiotic, Section 2.3.1, 2024)"
}
```

### 9. Using American Emergency Number
```python
# ❌ WRONG
action = "Call 911"  # American emergency number

# ✅ CORRECT
action = "Call 000"  # Australian emergency number
```

### 10. Committing Secrets to Git
```bash
# ❌ WRONG
git add .env  # Contains real API keys!

# ✅ CORRECT
# .env should be in .gitignore
# Use .env.example with placeholder values
```

---

## ✅ Before You Start Checklist

**Run this checklist before ANY task:** [CHECKLIST.md](CHECKLIST.md)

Quick version:
- [ ] Read relevant constraint files for your task type
- [ ] Using Australian spelling/drug names/sources
- [ ] Agent extends BaseAgent (if creating agent)
- [ ] No hardcoded credentials (zero tolerance)
- [ ] Citations have page/section numbers (RAG-verified)
- [ ] Using `self.logger`, not `print()`
- [ ] LLM calls are async (if applicable)
- [ ] Tests written (TDD if new feature)
- [ ] Drug dosages have units
- [ ] Red flags identified (if medical content)
- [ ] SI units used (mmol/L not mg/dL)
- [ ] Emergency number is "000" (not 911)

---

## 📚 Full Documentation Index

For detailed standards, see: [Full Index (README.md)](README.md)

**By Topic:**
1. [Medical Accuracy](01-medical-accuracy.md) - Australian context, citations, clinical accuracy
2. [Code Architecture](02-code-architecture.md) - BaseAgent, logging, error handling
3. [Security](03-security-configuration.md) - NO hardcoded secrets, config management
4. [LLM Integration](04-llm-integration.md) - OllamaClient, async calls, rate limiting
5. [Data Processing](05-data-processing.md) - JSON handling, PHI protection, pipelines
6. [Testing](06-testing-requirements.md) - TDD, coverage, quality gates
7. [Documentation](07-documentation-standards.md) - Docstrings, README templates
8. [Agent Requirements](08-agent-requirements.md) - 46 medical agent specifications
9. [ICRP Training](09-icrp-clinical-training.md) - SOAP notes, AMC Clinical Exam prep
10. [Anti-Patterns](10-anti-patterns.md) - Common mistakes to avoid

---

## ⚡ Hook-Based Quality Gates

**Automatic validation after Edit/Write operations:**

| Hook | Trigger | Checks | Exit Code |
|------|---------|--------|-----------|
| flutter-analyze | `.dart` files | Compilation errors | 2 = errors found |
| security-scan | `.dart`, `.rs` files | Hardcoded credentials | 2 = violations |
| test-runner | Code files | Affected tests | 2 = test failures |

**Violations caught immediately** - not at end of sprint!

---

## 🚀 Three-Stage Pipeline (Best Practice)

**For major features, use HITL (Human-in-the-Loop) approval:**

1. **PM-Spec**: Analyze request → Write specification → Ask clarifying questions
2. **Architect-Review**: Validate design → Produce ADR → Set `READY_FOR_BUILD` flag
3. **Implementer-Tester**: Implement code → Update tests → Mark `DONE`

**Approval points**: After spec (before architecture), after ADR (before implementation)

---

## ❓ Questions?

If ANY constraint is unclear:
1. Read the relevant detailed constraint file (01-10)
2. Search for similar existing code in the project
3. Ask the Project Manager (PM-001) BEFORE proceeding
4. **DO NOT guess or assume** - clarity prevents mistakes (like the 124 hardcoded credentials we had to fix)

---

**Last Updated**: 2025-12-18  
**Version**: 2.0.0  
**Time to Read**: 2 minutes  
**Next Step**: [Run Pre-Flight Checklist](CHECKLIST.md)
