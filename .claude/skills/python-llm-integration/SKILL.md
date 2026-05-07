---
description: |
  Python venv + LLM integration patterns for medical content generation.
  Critical: ALWAYS activate venv, NEVER use local LLMs for MCQ/OSCE generation (Claude API required).
  Use when: running Python scripts, LLM integration, medical content generation
allowed-tools:
  - Read
  - Bash
  - Grep
  - Edit
user-invocable: true
effort: medium
paths:
  - "scripts/**/*.py"
  - "backend/**/*.py"
  - "venv/**"
---

# Python + LLM Integration Skill

**Primary Reference**: `constraints/4-llm-integration.md`

**Read constraints now**:
```bash
!`cat constraints/4-llm-integration.md 2>/dev/null | head -100`
```

## Critical Rule #1: Python venv ALWAYS Required 🚨

**Before EVERY Python script execution**:
```bash
source venv/bin/activate
```

**Validation**:
```bash
!`python --version && which python | grep venv || echo "❌ VENV NOT ACTIVATED"`
```

### ❌ WRONG: Running without venv
```bash
python scripts/generate_mcqs.py  # Will fail or use wrong Python
```

### ✅ CORRECT: Always activate venv first
```bash
source venv/bin/activate
python scripts/generate_mcqs.py
```

---

## Critical Rule #2: Claude API for Medical Content 🚨

**Discovery (2026-01-26)**:
- Local LLMs (Ollama 7B models) **CANNOT** generate complex medical content
- **Evidence**: 200 MCQs failed → all returned placeholders/templates
- **Solution**: MUST use Claude (Anthropic API) for MCQ/OSCE generation

### Task Complexity Matrix

| Task Type | Local LLMs (Ollama) | Claude API (Anthropic) | Cost |
|-----------|---------------------|------------------------|------|
| MCQ generation | ❌ FAILS (placeholders) | ✅ REQUIRED | ~$0.02/MCQ |
| OSCE persona generation | ❌ FAILS | ✅ REQUIRED | ~$0.05/persona |
| Clinical content | ❌ FAILS | ✅ REQUIRED | ~$0.03/item |
| Simple validation | ✅ OK | ✅ OK | Free/low |
| Text classification | ✅ OK | ✅ OK | Free/low |

### ❌ WRONG: Using local LLMs for content generation
```python
import ollama

# DON'T DO THIS - produces placeholder content
client = ollama.Client()
response = client.generate(
    model="llama3:7b",
    prompt="Generate an MCQ about hypertension..."
)
# Result: "Option A", "Clinical scenario for...", etc.
```

### ✅ CORRECT: Use Claude API
```python
import anthropic
import os

# ALWAYS use Claude for medical content generation
client = anthropic.Anthropic(
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

response = client.messages.create(
    model="claude-sonnet-4",
    max_tokens=4000,
    messages=[{
        "role": "user",
        "content": """Generate a clinically accurate MCQ about hypertension management.

        Requirements:
        - Australian medical context (use paracetamol, not acetaminophen)
        - Include 3 RAG citations with qdrant_point_id
        - FRACP validation criteria
        - No placeholder content
        """
    }]
)

content = response.content[0].text
```

---

## Critical Rule #3: UTF-8 Encoding 🚨

**ALWAYS use UTF-8 encoding** for JSON/text file operations:

### ❌ WRONG: No encoding specified
```python
with open("data/mcqs.json", "r") as f:
    data = json.load(f)  # May fail on special characters
```

### ✅ CORRECT: Explicit UTF-8 encoding
```python
with open("data/mcqs.json", "r", encoding="utf-8") as f:
    data = json.load(f)
```

---

## Environment Setup Validation

**Pre-flight checklist**:
```bash
# Run pre-flight validation script
!`bash scripts/pre_flight_validation.sh 2>/dev/null || echo "⚠️  Pre-flight script missing"`
```

**Manual checks**:
```python
import sys
import os

# 1. Check Python version (3.8+)
print(f"Python: {sys.version}")

# 2. Check venv activated
if "venv" in sys.executable:
    print("✅ venv activated")
else:
    print("❌ venv NOT activated - run: source venv/bin/activate")

# 3. Check Claude API key
if os.getenv("ANTHROPIC_API_KEY"):
    print("✅ ANTHROPIC_API_KEY configured")
else:
    print("❌ ANTHROPIC_API_KEY missing - set in .env or environment")

# 4. Check required packages
try:
    import anthropic
    import qdrant_client
    print("✅ Required packages installed")
except ImportError as e:
    print(f"❌ Missing package: {e}")
```

---

## Common Patterns

### Pattern 1: Batch Processing with Claude API

```python
import anthropic
import json
from pathlib import Path

def generate_medical_content_batch(prompts: list[str]) -> list[dict]:
    """Generate medical content using Claude API with rate limiting"""

    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    results = []

    for i, prompt in enumerate(prompts):
        print(f"Processing {i+1}/{len(prompts)}...")

        try:
            response = client.messages.create(
                model="claude-sonnet-4",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.content[0].text
            results.append(json.loads(content))

            # Rate limiting (if needed)
            if (i + 1) % 10 == 0:
                time.sleep(60)  # 1 minute pause every 10 requests

        except Exception as e:
            print(f"Error on item {i+1}: {e}")
            results.append({"error": str(e)})

    return results
```

### Pattern 2: Checkpoint/Resume for Long Jobs

```python
import json
from pathlib import Path

def process_with_checkpoints(items: list, output_dir: Path):
    """Process items with checkpoint/resume capability"""

    checkpoint_file = output_dir / "checkpoint.json"

    # Load checkpoint if exists
    if checkpoint_file.exists():
        with open(checkpoint_file, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)
            processed_ids = set(checkpoint.get("processed", []))
    else:
        processed_ids = set()

    for item in items:
        if item["id"] in processed_ids:
            continue  # Skip already processed

        # Process item
        result = generate_medical_content(item)

        # Save result
        output_file = output_dir / f"{item['id']}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Update checkpoint
        processed_ids.add(item["id"])
        with open(checkpoint_file, "w", encoding="utf-8") as f:
            json.dump({"processed": list(processed_ids)}, f)
```

### Pattern 3: Ollama for Simple Tasks (Non-Content Generation)

```python
import ollama

def validate_simple_task(text: str) -> bool:
    """Use Ollama for simple validation tasks (NOT content generation)"""

    client = ollama.Client()

    # Simple classification task - OK for local LLMs
    response = client.generate(
        model="llama3:7b",
        prompt=f"Is this text medical content? Answer yes or no only.\n\nText: {text}"
    )

    return "yes" in response['response'].lower()
```

---

## Validation Checklist

Before running any Python script:

- [ ] `source venv/bin/activate` executed
- [ ] Python version 3.8+ confirmed
- [ ] ANTHROPIC_API_KEY environment variable set
- [ ] For medical content generation: Using Claude API (NOT Ollama)
- [ ] All file operations use `encoding="utf-8"`
- [ ] Pre-flight validation script passes

**Quick validation**:
```bash
!`python -c "import sys, os; print('✅ venv' if 'venv' in sys.executable else '❌ no venv'); print('✅ API key' if os.getenv('ANTHROPIC_API_KEY') else '❌ no API key')"`
```

---

## Cost Estimation

**Claude API costs for medical content** (approximate):
- MCQ generation: ~$0.02 per MCQ (4-5 questions)
- OSCE persona: ~$0.05 per complete persona
- Batch of 200 personas: ~$10 total

**vs. Quality tradeoff**:
- Local LLMs: $0 cost, 0% usable content (100% placeholders)
- Claude API: ~$10/200 items, 96.5% deployment ready

**Recommendation**: Always use Claude API for medical content - cost is negligible vs. quality.

---

## References

- **See**: `constraints/4-llm-integration.md` - Full LLM integration patterns
- **See**: `constraints/5-data-processing.md` - Data processing standards
- **See**: `reference/claude-api-examples.md` - More Claude API examples
- **See**: `scripts/pre_flight_validation.sh` - Environment validation
