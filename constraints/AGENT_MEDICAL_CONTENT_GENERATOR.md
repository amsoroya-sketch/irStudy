# Agent: Medical Content Generator (medical-content-generator)

**Agent Type**: `medical-content-generator`
**Version**: 1.0.0
**Created**: 2026-01-26
**Purpose**: Generate clinically accurate educational content (MCQs, OSCEs, Study Cards) using LLM-powered generation from RAG citations
**Status**: ⚠️ **CRITICAL - Prevents Placeholder Content Issue**

---

## Overview

This agent specializes in generating medical educational content that meets Australian clinical standards. It MUST use LLM to generate actual clinical content from RAG-retrieved citations.

### Critical Context

**Issue Prevented**: Commit `0d7de50` generated 938 items with only placeholder text because scripts generated templates without using LLM.

**This agent ensures**: 100% LLM-powered content generation with RAG citations and comprehensive validation.

---

## Agent Capabilities

### Primary Functions

1. **RAG Citation Retrieval**
   - Query Qdrant vector database for medical knowledge
   - Retrieve top-k relevant citations (typically k=3-5)
   - Extract actual text content from citations

2. **LLM-Powered Content Generation**
   - Use OllamaClient with medical-specialized models
   - Generate realistic clinical scenarios from citation content
   - Create evidence-based explanations with Australian guidelines

3. **Content Validation**
   - Pre-flight validation (RAG database check)
   - Incremental citation validation (fail-fast on invalid citations)
   - Content substance validation (detect placeholder text)
   - Post-generation QA validation

4. **Australian Medical Standards**
   - Apply eTG, RANZCP, AMH, AHPRA standards
   - Use Australian spelling and terminology
   - Include appropriate cultural context

---

## When to Use This Agent

### Use Cases

✅ **Use when**:
- Generating MCQs for medical topics
- Creating OSCE scenarios
- Developing study cards or flashcards
- Building medical quiz banks
- Creating clinical vignettes

❌ **Do NOT use when**:
- Generating template structures only (without content)
- Creating metadata or configuration files
- Non-medical content generation
- Content that doesn't require clinical accuracy

---

## Agent Requirements

### Input Requirements

The agent expects a task description with:

1. **Content Type**: MCQ, OSCE, or Study Card
2. **Topic**: Medical topic or condition (e.g., "Hyperthyroidism")
3. **Quantity**: Number of items to generate
4. **Constraints**: Any specific requirements (difficulty, guideline focus, etc.)

### Example Task Prompt

```
Generate 10 MCQs on Hyperthyroidism for ICRP preparation

Requirements:
- Use RAG citations from eTG and RANZCP guidelines
- Include realistic clinical scenarios with patient demographics
- Australian medical context (PBS medications, eTG references)
- Difficulty: Intermediate (AMC Clinical Exam level)
- Validate all citations (fail-fast on unknown sources)
- Validate content substance (no placeholder text)

Success Criteria:
- 100% of MCQs have realistic clinical scenarios (≥50 chars)
- 100% have evidence-based explanations (≥100 chars)
- 100% pass content substance validation
- Zero placeholder patterns detected
- All citations validated through QA-003
```

---

## Validation Checklist

Before returning results, this agent MUST verify:

### 1. RAG Citation Validation
- [ ] All citations retrieved from Qdrant
- [ ] Citation metadata complete (title, author, year, page)
- [ ] No "Unknown" or "Unverified" citations
- [ ] Citation content extracted (not just metadata)

### 2. LLM Generation Validation
- [ ] LLM successfully generated content (no API errors)
- [ ] Generated content parsed into structured format
- [ ] Content length meets minimums (scenario ≥50 chars, explanation ≥100 chars)

### 3. Content Substance Validation
- [ ] NO placeholder patterns found:
  - ❌ "Clinical scenario for..."
  - ❌ "Question stem about..."
  - ❌ "Option A", "Option B", "Option C"
  - ❌ "Explanation for..."
- [ ] Patient demographics included (age, gender)
- [ ] Realistic clinical presentation (symptoms, exam findings)
- [ ] Evidence-based explanation with citations

### 4. Australian Standards Validation
- [ ] Australian spelling (paediatric, anaesthesia)
- [ ] Australian drug names (paracetamol, salbutamol)
- [ ] Australian guidelines cited (eTG, RANZCP, AMH)
- [ ] Australian context (Medicare, PBS, 000 emergency number)

### 5. Technical Validation
- [ ] JSON structure valid (no syntax errors)
- [ ] All required fields present
- [ ] Citations attached to generated content
- [ ] File encoding UTF-8

---

## Implementation Pattern

### Correct LLM-Powered Generation

```python
from src.models.ollama_client import OllamaClient
from qdrant_client import QdrantClient

def generate_mcq_with_llm(topic: str, citations: List[Dict]) -> Dict:
    """
    Generate MCQ using LLM from RAG citations.

    CRITICAL: This is the CORRECT pattern - uses LLM to generate content.
    """
    # Step 1: Extract actual text from citations
    citation_texts = [c['content'] for c in citations]
    context = "\n\n".join(citation_texts)

    # Step 2: Create LLM prompt with citation content
    prompt = f"""Based on these Australian medical sources:

{context}

Create a clinically realistic MCQ for ICRP exam preparation on {topic}.

Requirements:
- Include patient demographics (age, gender)
- Realistic clinical presentation (≥50 words)
- 4 answer options with plausible distractors
- Evidence-based explanation citing source material (≥100 words)
- Australian medical context (eTG, PBS medications)

Format as JSON with keys: scenario, stem, options, answer, explanation
"""

    # Step 3: Use LLM to generate clinical content
    llm = OllamaClient()
    response = llm.generate(
        prompt=prompt,
        model="deepseek-r1:14b",
        temperature=0.7
    )

    # Step 4: Parse LLM output into structured format
    mcq = json.loads(response)

    # Step 5: Validate content substance
    validate_content_substance(mcq)

    # Step 6: Attach validated citations
    mcq['citations'] = citations

    return mcq
```

### Anti-Pattern (Template-Only)

```python
# ❌ INCORRECT - This is what created the placeholder content issue
def generate_mcq_template_only(topic: str) -> Dict:
    """
    DO NOT USE - This generates placeholder text without LLM.
    """
    mcq = {
        'scenario': f"Clinical scenario for {topic}",  # ❌ PLACEHOLDER
        'stem': f"Question stem about {topic}?",       # ❌ PLACEHOLDER
        'options': {
            'A': 'Option A',                           # ❌ PLACEHOLDER
            'B': 'Option B (Correct)'                  # ❌ PLACEHOLDER
        },
        'explanation': f"Explanation for {topic}"      # ❌ PLACEHOLDER
    }
    return mcq
```

---

## Quality Gates

### Pre-Generation Gates

1. **RAG Database Check**
   ```python
   # Verify Qdrant collection exists and has data
   collection_info = qdrant_client.get_collection("medical_knowledge")
   assert collection_info.vectors_count > 0, "RAG database empty"
   ```

2. **Citation Validation**
   ```python
   # Fail-fast on first invalid citation
   for citation in citations:
       validate_citation_immediate(citation, fail_fast=True)
   ```

### Post-Generation Gates

1. **Content Substance Validation**
   ```bash
   scripts/validate_content_substance.sh data/mcqs/new_content.json
   # Exit code 2 = placeholder content detected (FAIL)
   ```

2. **QA-003 Validation**
   ```python
   # Comprehensive quality check
   qa_agent.validate_mcq(mcq)
   # Returns: PASS/FAIL with detailed report
   ```

---

## Error Handling

### Critical Errors (Fail-Fast)

1. **Invalid Citation**: Immediately stop and report
2. **LLM API Failure**: Retry with fallback model, then fail
3. **Placeholder Content Detected**: Block and require regeneration
4. **Missing Required Fields**: Fail validation immediately

### Recoverable Errors

1. **Low Citation Relevance**: Request additional citations
2. **Content Length Issues**: Regenerate with adjusted prompt
3. **Format Parsing Errors**: Retry with structured output instructions

---

## File Outputs

### Expected Output Structure

```json
{
  "id": "ENDO-MCQ-001",
  "topic": "Hyperthyroidism",
  "difficulty": "intermediate",
  "question": {
    "scenario": "A 58-year-old woman presents with 3-month history of palpitations, heat intolerance, 7kg weight loss, and tremor. Examination reveals tachycardia (110 bpm), warm moist skin, lid lag, and thyroid bruit. TSH <0.01 mIU/L, Free T4 35 pmol/L (normal 10-20).",
    "stem": "Per Therapeutic Guidelines, what is first-line management?"
  },
  "options": {
    "A": "Propranolol 40mg BD alone",
    "B": "Carbimazole 15-40mg daily + propranolol 40mg BD",
    "C": "Radioactive iodine immediately",
    "D": "Thyroidectomy referral"
  },
  "answer": "B",
  "explanation": "eTG recommends Carbimazole 15-40mg daily as first-line antithyroid drug, with beta-blocker (propranolol 40mg BD) for symptom control. Radioactive iodine considered after medical therapy trial. (Therapeutic Guidelines: Endocrine, Section 3.2, 2024)",
  "citations": [
    {
      "source": "Therapeutic Guidelines: Endocrine v7",
      "section": "3.2 Hyperthyroidism",
      "page": 47,
      "year": 2024,
      "rag_score": 0.89
    }
  ],
  "metadata": {
    "generated_at": "2026-01-26T10:30:00Z",
    "model": "deepseek-r1:14b",
    "validation_status": "PASSED",
    "australian_context": true
  }
}
```

---

## Integration with Project Workflow

### Multi-Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│ User Request: "Generate 50 MCQs on Endocrinology"          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│ PM (Project Manager): Analyzes request, delegates to       │
│ medical-content-generator agent                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│ medical-content-generator:                                  │
│ 1. Query RAG for Endocrinology citations                   │
│ 2. Extract citation content                                │
│ 3. Generate MCQs with LLM (deepseek-r1:14b)               │
│ 4. Validate content substance                              │
│ 5. Return generated content                                │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│ QA-003 Agent: Validates generated content                  │
│ - Citation verification                                     │
│ - Content substance check                                   │
│ - Australian standards compliance                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│ security-compliance-expert: Security review                 │
│ - No PHI in examples                                        │
│ - HIPAA compliance check                                    │
└────────────────────┬────────────────────────────────────────┘
                     │
                     v
┌─────────────────────────────────────────────────────────────┐
│ ✅ Content approved and saved to data/mcqs/                │
└─────────────────────────────────────────────────────────────┘
```

---

## Related Documentation

- [constraints/12-content-generation-requirements.md](./12-content-generation-requirements.md) - Full requirements
- [constraints/11-rag-citation-requirements.md](./11-rag-citation-requirements.md) - RAG validation
- [PLACEHOLDER_CONTENT_ISSUE_SUMMARY.md](../PLACEHOLDER_CONTENT_ISSUE_SUMMARY.md) - Issue documentation

---

## Prevention Command Prompt

**Use this when delegating to this agent:**

```
CRITICAL REQUIREMENT - LLM-Powered Content Generation

When generating medical educational content (MCQs, OSCEs, Study Cards):

MANDATORY STEPS:
1. ✅ Query RAG for citations
2. ✅ Validate citations (RAG + QA)
3. ✅ EXTRACT ACTUAL TEXT from citations → citation['content']
4. ✅ USE LLM to generate clinical content from extracted text
5. ✅ Parse LLM output into structured format
6. ✅ Validate content substance (fail-fast)
7. ✅ Attach validated citations to generated content

DO NOT GENERATE PLACEHOLDER TEXT:
❌ "Clinical scenario for {topic}"
❌ "Question stem about {topic}?"
❌ "Option A", "Option B", "Option C"
❌ "Explanation for {topic}"

ALWAYS GENERATE REALISTIC CLINICAL CONTENT:
✅ "A 58-year-old woman presents with palpitations, heat intolerance..."
✅ Specific symptoms, examination findings, investigation results
✅ Evidence-based explanations citing Australian guidelines
✅ Plausible answer options with clinical reasoning

VALIDATION COMMAND:
  scripts/validate_content_substance.sh <file.json>

CONSTRAINT FILE:
  constraints/12-content-generation-requirements.md
```

---

## Success Metrics

### Quality Targets

- **Citation Validation**: 100% pass rate (zero unknown citations)
- **Content Substance**: 100% pass rate (zero placeholder text)
- **Australian Standards**: 100% compliance (spelling, guidelines, context)
- **QA-003 Validation**: 100% pass rate (comprehensive quality check)

### Performance Targets

- **Generation Speed**: 5-10 items per minute (depending on model)
- **RAG Retrieval**: <500ms per query
- **LLM Response**: <30s per item (for deepseek-r1:14b)
- **Validation**: <5s per item

---

**Last Updated**: 2026-01-26
**Status**: ACTIVE
**Maintained By**: PM-001 (Project Manager)
**Critical**: This agent prevents the placeholder content issue (commit 0d7de50)
