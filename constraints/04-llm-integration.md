# LLM Integration Patterns

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## LLM Integration Patterns

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

---

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
