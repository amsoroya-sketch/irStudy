# 12. Content Generation Requirements (CRITICAL)

**Version**: 1.0.0
**Added**: 2026-01-26
**Status**: **BLOCKING CONSTRAINT** - All future content generation MUST use LLM
**Issue**: Commit `0d7de50` generated 938 study items with only placeholder text

---

## 12.1 LLM-Powered Content Generation (MANDATORY)

### Critical Issue Identified

**Date**: 2026-01-26
**Commit**: `0d7de50` - "feat: Complete comprehensive coverage of 65 missing medical topics"
**Problem**: Generated 938 study items (774 MCQs + 65 OSCEs + 65 Study Cards) with only placeholder text, no actual clinical content.

**Root Cause**: Scripts generated metadata structures but did NOT use LLM to generate actual clinical content from RAG-retrieved citations.

### Mandatory Requirement

**ALL medical content generation MUST use LLM to create educational content from RAG citations.**

---

## 12.2 Template-Only vs LLM-Powered Generation

### ❌ INCORRECT (Template-Only Generation)

```python
def generate_mcq(self, topic: str):
    citations = self.query_rag(topic)
    validate_citation_immediate(citations, fail_fast=True)

    # ❌ WRONG: Placeholder text only - NO ACTUAL CONTENT
    mcq = {
        'question': {
            'scenario': f"Clinical scenario for {topic}",  # ❌ PLACEHOLDER
            'stem': f"Question stem about {topic}?",        # ❌ PLACEHOLDER
            'options': {
                'A': 'Option A',                            # ❌ PLACEHOLDER
                'B': 'Option B (Correct)',                  # ❌ PLACEHOLDER
                'C': 'Option C',                            # ❌ PLACEHOLDER
                'D': 'Option D'                             # ❌ PLACEHOLDER
            }
        },
        'correct_answer': 'B',
        'explanation': f"Explanation for {topic}",          # ❌ PLACEHOLDER
        'references': citations  # ✅ Citations valid but UNUSED
    }
    return mcq
```

**Problems**:
- No realistic patient presentation
- No clinical reasoning
- No evidence-based content
- Citations retrieved but not used
- Zero educational value

---

### ✅ CORRECT (LLM-Powered Generation)

```python
def generate_mcq_with_llm(self, topic: str):
    """Generate MCQ using LLM with RAG citations"""

    # Step 1: Query RAG for citations
    citations = self.query_rag(topic)
    validate_citation_immediate(citations, fail_fast=True)

    # Step 2: Extract actual content from RAG citations
    citation_texts = [c['content'] for c in citations]
    context = "\n\n".join(citation_texts)

    # Step 3: Create LLM prompt
    prompt = f"""Based on these Australian medical sources:

{context}

Create a clinically realistic MCQ for ICRP exam preparation:

REQUIREMENTS:
1. Patient demographics (age, gender, relevant history)
2. Realistic clinical presentation with symptoms/signs
3. Investigation results if appropriate
4. 4 plausible answer options (one correct, three distractors)
5. Evidence-based explanation citing specific guidelines
6. Australian context (eTG, RANZCP, AMH, PBS)

Topic: {topic}

FORMAT:
- Scenario: [Detailed clinical presentation]
- Stem: [Specific question]
- Options: A/B/C/D [Plausible choices]
- Answer: [Letter]
- Explanation: [Evidence-based reasoning with citations]
"""

    # Step 4: Generate content using LLM
    from src.llm.ollama_client import OllamaClient
    llm = OllamaClient()
    mcq_content = llm.generate(
        prompt=prompt,
        model="deepseek-r1:14b",  # or llama3.1:70b, claude, gpt-4
        max_tokens=2000
    )

    # Step 5: Parse LLM output into structured format
    mcq = self.parse_llm_output(mcq_content)
    mcq['references'] = citations
    mcq['generation_method'] = 'LLM-powered'
    mcq['llm_model'] = 'deepseek-r1:14b'

    # Step 6: Validate content substance (fail-fast)
    validate_content_substance(mcq)

    return mcq
```

**Benefits**:
- Realistic clinical scenarios with patient demographics
- Evidence-based explanations from RAG sources
- Australian guideline integration
- Plausible distractors for assessment
- Educational value for exam preparation

---

## 12.3 Content Substance Validation

### Validation Function

```python
def validate_content_substance(mcq: Dict):
    """Validate MCQ has actual clinical content, not placeholders

    FAIL-FAST: Raises ValueError on validation failure
    """

    # Check 1: Placeholder patterns
    placeholder_patterns = [
        'Clinical scenario for',
        'Question stem about',
        'Option A', 'Option B', 'Option C', 'Option D',
        'Explanation for',
        'Key points for'
    ]

    scenario = mcq['question'].get('scenario', '')
    stem = mcq['question'].get('stem', '')
    explanation = mcq.get('explanation', '')

    for pattern in placeholder_patterns:
        if pattern in scenario or pattern in stem or pattern in explanation:
            raise ValueError(
                f"❌ Placeholder content detected: '{pattern}'\n"
                f"   LLM generation required for actual clinical content"
            )

    # Check 2: Minimum content length
    if len(scenario) < 50:
        raise ValueError(
            f"❌ Scenario too short ({len(scenario)} chars, minimum 50)\n"
            f"   Needs realistic clinical presentation with patient demographics"
        )

    if len(explanation) < 100:
        raise ValueError(
            f"❌ Explanation too short ({len(explanation)} chars, minimum 100)\n"
            f"   Needs evidence-based content with Australian guidelines"
        )

    # Check 3: Patient demographics
    required_demographics = ['year', 'old', 'aged', 'patient']
    if not any(word in scenario.lower() for word in required_demographics):
        raise ValueError(
            "❌ No patient demographics found in scenario\n"
            "   Required: Age (e.g., '58-year-old'), gender, relevant history"
        )

    # Check 4: Australian context
    australian_markers = ['australian', 'etg', 'ranzcp', 'amh', 'pbs', 'ahpra', 'therapeutic guidelines']
    if not any(marker in explanation.lower() for marker in australian_markers):
        raise ValueError(
            "❌ No Australian context found in explanation\n"
            "   Required: Reference to eTG, RANZCP, AMH, PBS, or AHPRA guidelines"
        )

    return True
```

---

## 12.4 Pre-Commit Validation Hook

### Installation

```bash
# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Content substance validation pre-commit hook
exec scripts/validate_content_substance.sh
EOF

chmod +x .git/hooks/pre-commit
```

### Validation Script

**Location**: `scripts/validate_content_substance.sh`

```bash
#!/bin/bash
# Content Substance Validation Script
# Prevents commit of placeholder medical content

set -e

echo "🔍 CONTENT SUBSTANCE VALIDATION"
echo "================================"

# Get staged medical content files
FILES=$(git diff --cached --name-only | grep -E "data/(mcqs|osces|study_cards)/.*\.json$" || true)

if [ -z "$FILES" ]; then
    echo "ℹ️  No medical content files staged"
    exit 0
fi

ERRORS=0

# Validate each file
for FILE in $FILES; do
    echo "📄 Checking: $FILE"

    # Check for placeholder patterns
    if grep -q "Clinical scenario for" "$FILE"; then
        echo "❌ ERROR: Placeholder scenario detected"
        ((ERRORS++))
    fi

    if grep -q '"A": "Option A"' "$FILE"; then
        echo "❌ ERROR: Placeholder answer options detected"
        ((ERRORS++))
    fi

    # Check minimum explanation length (>20 words)
    EXPLANATION_WORDS=$(jq -r '.[].explanation // .mcqs[].explanation' "$FILE" 2>/dev/null | head -1 | wc -w)
    if [ "$EXPLANATION_WORDS" -lt 20 ]; then
        echo "❌ ERROR: Explanation too short (<20 words)"
        ((ERRORS++))
    fi
done

if [ $ERRORS -gt 0 ]; then
    echo ""
    echo "❌ VALIDATION FAILED"
    echo ""
    echo "Placeholder content detected. Medical content MUST be LLM-generated."
    echo "See constraints/12-content-generation-requirements.md for details"
    exit 2
else
    echo "✅ VALIDATION PASSED"
    exit 0
fi
```

---

## 12.5 Content Validation Checklist

**Before committing any MCQ/OSCE/Study Card, verify:**

- [ ] ✅ Contains realistic patient demographics (age, gender, history)
- [ ] ✅ Clinical scenario has ≥50 characters of substance
- [ ] ✅ Question stem is specific, not generic template
- [ ] ✅ Answer options are plausible (not "Option A/B/C/D")
- [ ] ✅ Explanation has ≥100 characters of evidence-based content
- [ ] ✅ Australian guidelines cited specifically (eTG page X, RANZCP section Y)
- [ ] ✅ No placeholder patterns detected
- [ ] ✅ LLM was used to generate content from RAG citations
- [ ] ✅ `validate_content_substance()` passes

---

## 12.6 Prevention Command Prompt

**Use this prompt for ALL future content generation tasks:**

```
CRITICAL REQUIREMENT - LLM-Powered Content Generation:

When generating medical educational content (MCQs, OSCEs, Study Cards):

MANDATORY STEPS:
1. Query RAG for citations ✅
2. Validate citations (RAG + QA) ✅
3. **EXTRACT ACTUAL TEXT from citations** → citation['content']
4. **USE LLM to generate clinical content** from extracted text
5. Parse LLM output into structured format
6. Validate content substance (fail-fast)
7. Attach validated citations to generated content

DO NOT generate placeholder text like:
❌ "Clinical scenario for {topic}"
❌ "Question stem about {topic}?"
❌ "Option A", "Option B", "Option C"
❌ "Explanation for {topic}"

ALWAYS generate realistic clinical content:
✅ "A 58-year-old woman presents with..."
✅ Specific symptoms, examination findings, investigation results
✅ Evidence-based explanations citing Australian guidelines (eTG Section X.Y)
✅ Plausible answer options with clinical reasoning

VALIDATION: Run scripts/validate_content_substance.sh before commit
CONSTRAINT: See constraints/12-content-generation-requirements.md
```

---

## 12.7 Affected Commit & Remediation Plan

### Affected Commit

**Commit**: `0d7de50` - "feat: Complete comprehensive coverage of 65 missing medical topics"
**Date**: 2026-01-26
**Status**: ⚠️ Contains placeholder content

### Files with Placeholder Content

| File | Items | Status |
|------|-------|--------|
| `data/mcqs/missing_psychiatry_150_mcqs.json` | 150 MCQs | ❌ Placeholder |
| `data/mcqs/missing_topics_comprehensive_mcqs.json` | 774 MCQs | ❌ Placeholder |
| `data/osces/missing_psychiatry_13_osces.json` | 13 OSCEs | ❌ Placeholder |
| `data/osces/missing_topics_comprehensive_osces.json` | 52 OSCEs | ❌ Placeholder |
| `data/study_cards/missing_psychiatry_13_cards.json` | 13 Cards | ❌ Placeholder |
| `data/study_cards/missing_topics_comprehensive_cards.json` | 52 Cards | ❌ Placeholder |

**Total Items Requiring Regeneration**: 938 items (774 MCQs + 65 OSCEs + 65 Study Cards)

### Remediation Options

**Option A** (RECOMMENDED): Keep as template infrastructure, regenerate with LLM
- ✅ Preserve citation infrastructure
- ✅ Preserve RAG integration
- ✅ Regenerate content with LLM using existing templates
- Timeline: 7-10 days

**Option B**: Revert commit and regenerate from scratch
- ❌ Loses citation work
- ✅ Clean slate approach
- Timeline: 10-14 days

**Option C**: Mark files as "TEMPLATE ONLY" and create new LLM versions
- ✅ Keep for reference
- ✅ Create parallel LLM-powered versions
- Timeline: 7-10 days

### Recommended Approach

**Option A** - Use existing files as templates:

1. **Retain** citation infrastructure (RAG queries working)
2. **Regenerate** content using LLM with existing citations
3. **Validate** using new substance validation hooks
4. **Replace** placeholder files with LLM-generated versions

---

## 12.8 Integration with Planning

### Added to Roadmap

**Planning Document**: `planning/jan-22-plan/EXPANSION_ROADMAP.md`

**New Task**: LLM-Powered Content Regeneration
- **Timeline**: Week 4-5 (Phase A completion)
- **Scope**: Regenerate 938 items with LLM
- **Priority**: HIGH (blocks educational use)
- **Dependencies**: LLM integration, validation hooks

**Success Criteria**:
- [ ] All 938 items regenerated with LLM
- [ ] 100% pass content substance validation
- [ ] Zero placeholder patterns detected
- [ ] Australian guidelines integrated
- [ ] 100% RAG citation validation maintained

---

## 12.9 Quality Gates

### Pre-Generation Quality Gate

```python
# MUST run before generating ANY medical content
def pre_generation_quality_gate():
    """Ensure LLM integration is active"""

    # Check 1: LLM client available
    try:
        from src.llm.ollama_client import OllamaClient
        llm = OllamaClient()
    except ImportError:
        raise RuntimeError("❌ LLM client not available - cannot generate content")

    # Check 2: RAG system operational
    from src.agents.qa.incremental_citation_validator import validate_rag_before_generation
    validate_rag_before_generation()

    # Check 3: Validation hooks installed
    if not os.path.exists('scripts/validate_content_substance.sh'):
        raise RuntimeError("❌ Validation hooks not installed")

    print("✅ Pre-generation quality gate PASSED")
    print("   LLM client: Available")
    print("   RAG system: Operational")
    print("   Validation: Installed")
    return True
```

### Post-Generation Quality Gate

```python
# MUST run after generating content
def post_generation_quality_gate(output_file: str):
    """Validate generated content substance"""

    # Run validation script
    result = subprocess.run(
        ['scripts/validate_content_substance.sh', output_file],
        capture_output=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"❌ Post-generation validation FAILED\n"
            f"   File: {output_file}\n"
            f"   Output: {result.stderr.decode()}"
        )

    print(f"✅ Post-generation quality gate PASSED: {output_file}")
    return True
```

---

## 12.10 Example: Complete LLM-Powered Generation

```python
#!/usr/bin/env python3
"""
LLM-Powered MCQ Generation (Correct Implementation)
Demonstrates proper RAG + LLM integration for content generation
"""

from src.llm.ollama_client import OllamaClient
from src.agents.qa.incremental_citation_validator import (
    validate_citation_immediate,
    validate_rag_before_generation
)
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

def generate_mcq_with_llm(topic: str):
    """Generate MCQ using LLM with RAG citations"""

    # Step 1: Pre-generation validation
    validate_rag_before_generation()

    # Step 2: Query RAG for citations
    qdrant = QdrantClient(url="http://localhost:6333")
    embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    query_embedding = embedder.encode(f"{topic} Australian medical guidelines")
    results = qdrant.search(
        collection_name="medical_knowledge",
        query_vector=query_embedding,
        limit=3,
        score_threshold=0.5
    )

    citations = [
        {
            'title': r.payload['title'],
            'author': r.payload.get('author', 'Unknown'),
            'year': str(r.payload.get('year', '2024')),
            'page': int(r.payload.get('page', 1)),
            'content': r.payload['content'],
            'rag_confidence': float(r.score)
        }
        for r in results
    ]

    # Step 3: Validate citations
    validate_citation_immediate(citations, f"MCQ-{topic}", fail_fast=True)

    # Step 4: Extract citation content
    context = "\n\n---\n\n".join([
        f"Source: {c['title']} (p.{c['page']})\n{c['content']}"
        for c in citations
    ])

    # Step 5: Generate with LLM
    llm = OllamaClient()
    prompt = f"""Based on these Australian medical sources:

{context}

Create a clinically realistic MCQ for ICRP exam:

Topic: {topic}

Requirements:
- Patient: age, gender, history
- Symptoms/signs: specific clinical presentation
- Investigations: if relevant
- 4 options: 1 correct, 3 plausible distractors
- Explanation: evidence-based with Australian guidelines

Format as JSON with keys: scenario, stem, options, answer, explanation
"""

    mcq_json = llm.generate(prompt, model="deepseek-r1:14b", max_tokens=2000)
    mcq = json.loads(mcq_json)

    # Step 6: Add metadata
    mcq['references'] = citations
    mcq['topic'] = topic
    mcq['generation_method'] = 'LLM-powered'
    mcq['created_date'] = datetime.now().isoformat()

    # Step 7: Validate substance
    validate_content_substance(mcq)

    return mcq

# Usage
mcq = generate_mcq_with_llm("Hyperthyroidism management")
print(json.dumps(mcq, indent=2))
```

---

## 12.11 Summary

### Key Requirements

1. **LLM Integration**: MANDATORY for all content generation
2. **RAG Citations**: Extract and use actual text from citations
3. **Content Validation**: Fail-fast on placeholder detection
4. **Pre-Commit Hooks**: Automated validation before commit
5. **Quality Gates**: Pre-generation + post-generation validation

### Prevention Measures

- [x] Documentation added (this file)
- [x] PROJECT_CONSTRAINTS.md updated
- [ ] Validation script created (`scripts/validate_content_substance.sh`)
- [ ] Pre-commit hook installed (`.git/hooks/pre-commit`)
- [ ] Planning updated (`EXPANSION_ROADMAP.md`)
- [ ] 938 items marked for regeneration

### Next Steps

1. Install validation script and pre-commit hook
2. Update planning roadmap with regeneration task
3. Regenerate 938 items using LLM-powered approach
4. Validate all new content with substance validation
5. Update commit message with LLM regeneration status

---

**Last Updated**: 2026-01-26
**Version**: 1.0.0
**Status**: **ACTIVE CONSTRAINT**
**Compliance**: MANDATORY for all future content generation
