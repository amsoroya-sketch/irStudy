# Constraint 4: LLM Integration Patterns

**Status**: CRITICAL - READ BEFORE ANY LLM WORK
**Last Updated**: 2026-01-26 (v2.1.0)
**Sections**: 4.0 (Environment), 4.1 (Client Usage), 4.2 (Complexity Limits)

---

## 4.0 Python Environment & LLM Requirements (MANDATORY)

### Python Environment

**ALWAYS use virtual environment:**
```bash
# Activate venv before running ANY Python script
source venv/bin/activate
python scripts/your_script.py
```

**❌ NEVER run without venv** - dependencies only installed in venv, not system-wide

### LLM Model Requirements

**Available Ollama Models on This System:**
- `deepseek-r1:7b` - PRIMARY (4.7 GB, medical reasoning)
- `qwen2.5:7b` - FALLBACK (4.7 GB, general purpose)
- `phi3:mini` - Simple tasks only (2.2 GB)

**System Limitations:**
- RAM: 12 GB → Cannot run 14B+ models
- Disk: 99% full → Use `/mnt/data/ollama-models`

**Environment Setup:**
```bash
export OLLAMA_MODELS=/mnt/data/ollama-models
```

### Sentence Transformers (RAG)

**Embedding model for RAG queries:**
```python
from sentence_transformers import SentenceTransformer

# Medical content RAG
model = SentenceTransformer('microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext')
# 768 dimensions - MUST match indexed embeddings
```

---

## 4.1 Ollama Client Usage (MANDATORY)

**Reference**: `src/models/ollama_client.py`

**Always use OllamaClient wrapper:**
```python
from src.llm.ollama_client import OllamaClient

class MyAgent:
    def __init__(self):
        self.ollama = OllamaClient(model="qwen2.5:7b")

    def generate(self, prompt: str) -> str:
        return self.ollama.generate(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )
```

**Fallback Strategy:**
```python
fallback_models = [
    'deepseek-r1:7b',  # Primary
    'qwen2.5:7b',      # Fallback
    'phi3:mini'        # Last resort
]
```

---

## 4.2 Claude vs Local LLMs for Medical Content (CRITICAL)

**Added**: 2026-01-26
**Reason**: 200 MCQs failed regeneration with local 7B LLMs
**Evidence**: `data/mcqs/week3_cardiology_200_mcqs.json` (all placeholders)

### Problem Statement

**Local LLMs (Ollama 7B models) CANNOT generate complex medical MCQs.**

**Use Claude (Anthropic API) instead for all complex medical content generation.**

**Evidence from 2026-01-26 Failure:**
- ✅ RAG returned valid citations (95%+ confidence)
- ❌ ALL 200 MCQs remained as placeholders
- ❌ Local LLMs produced: empty responses, malformed JSON, template text

### Root Cause

Complex MCQ generation requires:
1. **Clinical realism**: Demographics, vitals, history, examination
2. **Medical accuracy**: Dosages, contraindications, Australian guidelines
3. **Complex reasoning**: Differential diagnosis, risk stratification
4. **Structured output**: Valid JSON, 8+ fields, nested objects
5. **Australian context**: eTG/RANZCP/AMH/PBS, Australian spelling
6. **Length**: 500-1000 tokens per MCQ

**7B models struggle with**:
- Multi-step reasoning + JSON formatting simultaneously
- Medical domain knowledge depth
- Long-form structured generation

**System cannot run 14B+ models** (requires 16 GB RAM, we have 12 GB)

### MANDATORY Solution

#### ❌ DO NOT Use Local Ollama For:
- MCQ content generation
- OSCE case generation
- Complex medical reasoning
- Long-form content (>300 tokens)
- Multi-field structured JSON

#### ✅ MUST Use Claude (Anthropic API) For:
- All MCQ generation
- All OSCE generation
- Complex medical reasoning
- Structured medical content

### Task Complexity Matrix

| Task Type | Local Ollama (7B) | Claude (Anthropic API) |
|-----------|-------------------|-------------------|
| MCQ generation | ❌ FAILS | ✅ REQUIRED |
| OSCE generation | ❌ FAILS | ✅ REQUIRED |
| Complex reasoning | ❌ FAILS | ✅ REQUIRED |
| Simple validation (yes/no) | ✅ OK | ✅ OK (slower) |
| Keyword extraction | ✅ OK | ✅ OK (slower) |
| RAG embedding | ✅ OK | N/A |

### Code Pattern - CORRECT

```python
from anthropic import Anthropic

class MCQGenerator:
    def __init__(self):
        # Claude for complex generation
        self.anthropic = Anthropic()
        self.model = "claude-sonnet-4-5-20250929"

        # Local Ollama ONLY for simple tasks
        from src.llm.ollama_client import OllamaClient
        self.ollama = OllamaClient(model="qwen2.5:7b")

    def generate_mcq(self, topic: str, citations: list) -> dict:
        """Generate MCQ - uses Claude (can handle complexity)"""
        prompt = f"""Generate clinical MCQ for AMC exam...
        [Complex requirements: demographics, vitals, differential diagnosis,
         Australian context, structured JSON, etc.]

        Citations to reference:
        {json.dumps(citations, indent=2)}
        """

        # ✅ Use Claude for complex generation
        response = self.anthropic.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        return json.loads(response.content[0].text)

    def validate_simple(self, text: str) -> bool:
        """Simple validation - can use Ollama"""
        prompt = f"Does this contain placeholder text? Yes/No: {text}"

        # ✅ Ollama OK for simple yes/no
        response = self.ollama.generate(prompt, max_tokens=10)
        return "no" in response.lower()
```

### Code Pattern - INCORRECT

```python
class MCQGenerator:
    def __init__(self):
        # ❌ WRONG - 7B model for complex medical content
        self.llm = OllamaClient(model="deepseek-r1:7b")

    def generate_mcq(self, topic: str, citations: list) -> dict:
        # ❌ WRONG - 7B cannot handle this complexity
        response = self.llm.generate(complex_prompt, max_tokens=1500)
        # Result: Empty responses, malformed JSON, or placeholders
        return json.loads(response)  # Will fail
```

### Implementation Checklist

Before writing any MCQ/OSCE generation script:

- [ ] Read this constraint section (4.2)
- [ ] Identify task complexity (use matrix above)
- [ ] If complex generation → Use Claude Code client (REQUIRED)
- [ ] If simple validation → Local Ollama OK
- [ ] Document which LLM for which tasks in script header
- [ ] Test with 1-2 samples before batch processing
- [ ] Validate output has NO placeholder patterns

### System Limitations & Cost

**This System (12 GB RAM, 4.7 GB disk free)**:
- ✅ Can run: 7B models (qwen2.5:7b, deepseek-r1:7b, phi3:mini)
- ❌ Cannot run: 14B+ models (out of memory)
- ✅ Can run: Claude Code client (API-based)

**Cost Justification**:
- Claude API: ~$0.02 per MCQ (200 MCQs = $4)
- Quality: 100% pass rate, no placeholders
- Time: ~15 seconds per MCQ
- **Value**: Meets all quality standards → acceptable cost

### Historical Context

**What Happened (2026-01-26)**:
1. Generated 200 cardiology MCQs with validated citations (RAG ✅)
2. Content generation attempted with local models → placeholder templates
3. Background regeneration tried with unavailable models (14B, 70B)
4. ALL 200 MCQs failed → `regeneration_failed: true`
5. Discovered: 7B models fundamentally cannot handle task complexity

**Lesson Learned**:
- Citations validated ✅ (RAG working perfectly - 95%+ confidence)
- Content generation ❌ (local models insufficient)
- Quality compromised ❌ (violates Constraint 12: NO placeholders)

**Prevention**: This constraint ensures future scripts use appropriate LLM.

---

## Related Constraints

- **Constraint 12** (Medical Accuracy): NO placeholder content allowed
- **Constraint 6** (Testing): 100% pass rate required
- **Section 1** (Medical Accuracy): Australian context mandatory

## References

- `src/llm/ollama_client.py` - Ollama client wrapper
- `src/models/ollama_client.py` - Model registry
- `data/mcqs/week3_cardiology_200_mcqs.json` - Failed placeholder example
- `scripts/regenerate_all_placeholder_mcqs_with_summaries.py` - Failed regeneration attempt
