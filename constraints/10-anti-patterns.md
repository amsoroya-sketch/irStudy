# Anti-Patterns (What NOT to Do)

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## Anti-Patterns (What NOT to Do)

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

### 10.8 Docker/Deployment Anti-Patterns (CRITICAL)

**Date Discovered**: 2026-02-02
**Issue**: Python 3.12 + PyTorch 2.1.2 Compatibility
**Impact**: Docker build failure for flower, celery-worker, celery-beat services

```dockerfile
# ❌ NEVER use outdated Python packages incompatible with Docker Python version
FROM python:3.12-slim
# Then in requirements.txt:
torch==2.1.2  # ❌ FAILS: Only supports Python ≤3.11
sentence-transformers==2.3.1  # ❌ FAILS: Requires torch 2.1.2

# ✅ CORRECT: Use Python 3.12 compatible versions
FROM python:3.12-slim
# requirements.txt:
torch==2.10.0  # ✅ Supports Python 3.12
sentence-transformers==3.3.1  # ✅ Compatible with torch 2.10+
transformers==4.48.0  # ✅ Latest stable
```

**Error Signature**:
```
ERROR: Could not find a version that satisfies the requirement torch==2.1.2
ERROR: Ignored the following versions that require a different python version
```

**Root Cause**:
- PyTorch 2.1.x only supports Python 3.8-3.11
- PyTorch 2.2.0+ required for Python 3.12
- sentence-transformers has transitive dependency on torch

**Fix Applied**:
```bash
# File: backend/requirements.txt (line 47-50)
- sentence-transformers==2.3.1
- torch==2.1.2
- transformers==4.37.0
+ sentence-transformers==3.3.1  # Python 3.12 compatible
+ torch==2.10.0                 # Latest, supports 3.12
+ transformers==4.48.0          # Latest stable
```

**Prevention**:
1. ✅ Check Python version compatibility matrix before pinning package versions
2. ✅ Test Docker builds locally before committing requirements.txt changes
3. ✅ Use `python:3.11-slim` if packages don't support 3.12 yet
4. ✅ Review PyTorch release notes for Python version support

**Related Services Affected**:
- `flower` (Celery monitoring) - Uses backend/requirements.txt
- `celery-worker` (Task queue workers) - Uses backend/requirements.txt
- `celery-beat` (Scheduled tasks) - Uses backend/requirements.txt
- `backend` (FastAPI) - Uses backend/requirements.txt

**Verification**:
```bash
# Test Docker build after fix
docker compose build flower celery-worker celery-beat backend

# Verify services start successfully
docker compose up -d
docker compose ps  # All services should show "Up (healthy)"
```

---

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
