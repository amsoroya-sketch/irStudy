# Lessons Learned: Content Generation Mistakes & Root Causes

**Date**: 2026-01-26
**Purpose**: Document all mistakes from previous generation attempts to prevent recurrence
**Outcome**: Fresh start with proper Agent OS integration

---

## Executive Summary

**Total Content Generated**: 2,958 MCQs + 210 OSCEs + 140 Study Cards
**Valid Content**: 750 MCQs (25%), 210 OSCEs (100%), 140 Study Cards (100%)
**Failed Content**: 2,208 MCQs (75%) with 12,732 placeholder patterns
**Root Cause**: Template-based generation instead of LLM-powered Agent OS experts

---

## Critical Mistake #1: NOT Using Agent OS Medical Experts

### What Happened
- Generated content using generic `OllamaClient`
- Did NOT route by specialty to medical expert agents
- Ignored existing Agent OS infrastructure:
  - MED-001 Cardiology (46KB, ECG tools, GRACE/TIMI calculators)
  - MED-002 Respiratory (42KB, Spirometry, Wells PE, CURB-65)
  - MED-009 Psychiatry (91KB, 24 psychiatric assessment tools)
  - Plus 7 other specialty agents

### Why It Happened
- Scripts delegated to general-purpose agent without explicit Agent OS requirement
- Task prompt didn't specify "use MED-001 for cardiology MCQs"
- No specialty routing logic in generation scripts

### Impact
- 1,508 MCQs with placeholder content (template-only generation)
- 12,732 placeholder patterns detected
- No specialty-specific tools applied (ECG interpretation, spirometry, MSE)
- Generic clinical scenarios instead of specialty-specific presentations

### Correct Approach (Agent OS)
```python
# WRONG (what we did):
ollama_client = OllamaClient()
mcq = ollama_client.generate(topic="cardiology")

# RIGHT (what we should do):
from src.agents.medical.med_001_cardiology import CardiologyExpert
cardio_agent = CardiologyExpert()
mcq = cardio_agent.generate_mcq(
    topic="ACS",
    tools=["ECG_interpretation", "GRACE_score", "TIMI_risk"]
)
```

---

## Critical Mistake #2: Template-Based Generation (Violates Constraint 12)

### What Happened
- Scripts used string templates with placeholder text:
  ```python
  scenario = f"Clinical scenario for {topic}"  # WRONG!
  stem = f"Question about {topic}?"  # WRONG!
  options = {"A": "Option A", "B": "Option B"}  # WRONG!
  ```
- Did NOT extract RAG citation content for LLM input
- LLM never saw actual medical knowledge from citations

### Why It Happened
- Generation scripts focused on structure over content
- RAG citations fetched but content field not passed to LLM
- No validation between RAG fetch and LLM generation steps

### Impact
- 12,732 placeholder patterns:
  - "Clinical scenario for..." (2,208 instances)
  - "Question about..." (2,208 instances)
  - "Option A/B/C/D" (8,832 instances)
  - "Explanation for..." (2,208 instances)
- Zero educational value
- Clinical safety risk if used by students

### Correct Approach (LLM-Powered)
```python
# Fetch RAG citations
citations = rag_query(topic="myocardial_infarction")

# Extract content for LLM context
citation_text = "\n\n".join([c['content'] for c in citations])

# Generate with LLM using real medical knowledge
llm_prompt = f"""
Generate a clinical MCQ about myocardial infarction.

Medical Knowledge Context:
{citation_text}

Requirements:
- Real clinical presentation with age, gender, vital signs
- Specific question stem (not "Question about...")
- 4 detailed options based on guidelines
- Comprehensive explanation referencing eTG/RANZCP
"""

mcq = llama.generate(llm_prompt)  # REAL content, not templates!
```

---

## Critical Mistake #3: Insufficient Constraint Enforcement

### What Happened
- **Constraint 11 (3 citations per MCQ)**: Not enforced during generation
  - Some MCQs had 2 citations, some had 0
  - No fail-fast when citation count < 3
- **Constraint 12 (LLM-powered)**: Not enforced
  - Template generation allowed
  - No check for placeholder patterns before saving

### Why It Happened
- Constraints documented but not implemented as blocking gates
- Generation scripts didn't validate constraints incrementally
- Pre-commit hook created AFTER content generated (should be BEFORE)

### Impact
- 938 items from commit 0d7de50 unusable
- Additional 1,270 items from Week 1-3 unusable
- Total rework required: 2,208 MCQs

### Correct Approach (Fail-Fast Validation)
```python
def generate_mcq_with_constraints(topic):
    # STEP 1: Pre-generation validation
    assert rag_system.is_connected(), "RAG not available"
    assert llm_client.is_connected(), "LLM not available"

    # STEP 2: Fetch citations (Constraint 11)
    citations = rag_query(topic, limit=5)
    assert len(citations) >= 3, f"Need 3 citations, got {len(citations)}"
    citations = citations[:3]  # Exactly 3

    # STEP 3: Generate with LLM (Constraint 12)
    citation_content = extract_content(citations)
    mcq = llm_generate(topic, citation_content)

    # STEP 4: Incremental validation
    assert "Clinical scenario for" not in mcq['scenario'], "Placeholder detected!"
    assert len(mcq['references']) == 3, "Must have 3 citations"
    assert mcq['summary'], "Summary required"

    return mcq
```

---

## Critical Mistake #4: No Specialty Routing

### What Happened
- All MCQs generated with single generic approach
- Cardiology MCQs didn't use ECG interpretation tools
- Respiratory MCQs didn't use spirometry/CXR tools
- Psychiatry MCQs didn't use MSE/risk assessment tools

### Why It Happened
- No specialty detection logic
- No Agent OS routing by topic/specialty
- Single monolithic script instead of specialty-specific agents

### Impact
- Lost opportunity for specialty-specific enhancements:
  - Cardiology: No ECG images, no GRACE/TIMI scores
  - Respiratory: No spirometry data, no CXR findings
  - Psychiatry: No MSE format, no screening tools (PHQ-9, GAD-7)

### Correct Approach (Agent OS Routing)
```python
SPECIALTY_ROUTING = {
    'cardiology': 'MED-001',
    'respiratory': 'MED-002',
    'gastroenterology': 'MED-003',
    'endocrinology': 'MED-004',
    'neurology': 'MED-005',
    'emergency': 'MED-006',
    'obgyn': 'MED-007',
    'paediatrics': 'MED-008',
    'psychiatry': 'MED-009',
    'general_practice': 'MED-010'
}

def route_to_agent(topic, specialty):
    agent_id = SPECIALTY_ROUTING.get(specialty)
    if not agent_id:
        raise ValueError(f"No agent for specialty: {specialty}")

    # Use Agent OS Task tool to delegate
    return task_delegate(
        agent=agent_id,
        prompt=f"Generate MCQ for {topic} with specialty tools"
    )
```

---

## Critical Mistake #5: Post-Generation Validation (Should Be Pre + During)

### What Happened
- Validation scripts created AFTER 2,958 items generated
- No incremental validation during generation
- Placeholder content saved to git before detection

### Why It Happened
- "Generate first, validate later" approach
- No fail-fast philosophy
- Pre-commit hook not installed until Agent OS review

### Impact
- Wasted time: 2-4 hours generating invalid content
- Wasted storage: 12MB of placeholder JSON files
- Wasted audit time: 1 hour validating 33 files
- Now need complete regeneration: 2-4 hours more

### Correct Approach (Fail-Fast Pipeline)
```
┌─────────────────────────────────────────────────────────────┐
│ GENERATION PIPELINE (Fail-Fast at Every Step)              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  PRE-GENERATION VALIDATION (BLOCKING)                      │
│  ├─ RAG system operational?         [FAIL → STOP]         │
│  ├─ LLM client operational?         [FAIL → STOP]         │
│  ├─ Ollama models available?        [FAIL → STOP]         │
│  └─ Agent OS medical experts loaded? [FAIL → STOP]        │
│                                                             │
│  FOR EACH MCQ (Incremental):                               │
│  ├─ Fetch 3 RAG citations           [<3 → RETRY → FAIL]   │
│  ├─ Extract citation content        [Empty → FAIL]        │
│  ├─ Generate with LLM + content     [Placeholder → RETRY] │
│  ├─ Validate placeholder patterns   [Found → RETRY]       │
│  ├─ Validate citation count         [≠3 → RETRY]          │
│  ├─ Validate summary exists         [Missing → RETRY]     │
│  └─ Save MCQ                        [Success → Continue]  │
│                                                             │
│  POST-GENERATION VALIDATION (BLOCKING)                     │
│  ├─ Content substance check         [FAIL → STOP]         │
│  ├─ QA-003 RAG validator            [FAIL → STOP]         │
│  ├─ QA-001 Australian compliance    [FAIL → STOP]         │
│  └─ QA-002 Clinical accuracy        [FAIL → STOP]         │
│                                                             │
│  PRE-COMMIT HOOK (BLOCKING)                                │
│  └─ Final placeholder scan          [Found → BLOCK]       │
└─────────────────────────────────────────────────────────────┘
```

---

## Critical Mistake #6: No Summary Field (User Requirement)

### What Happened
- User explicitly requested summaries: "for mcq we need summary as well"
- Generated 750 valid MCQs WITHOUT summaries
- Summaries added to plan but not to existing valid content

### Why It Happened
- Summary requirement arrived AFTER initial generation
- Focused on regenerating placeholder content
- Didn't retrofit summaries to valid content

### Impact
- 400 valid MCQs need updates (add summaries)
- 1,508 placeholder MCQs need full regeneration WITH summaries
- Inconsistent MCQ structure across dataset

### Correct Approach
```python
# ALL MCQs must have summary field from day 1
mcq_structure = {
    "id": "...",
    "question": {...},
    "explanation": {...},
    "summary": "1-2 sentences capturing key learning point",  # REQUIRED
    "references": [...]  # 3 citations
}

# Summary generation by LLM
def generate_summary(explanation):
    prompt = f"""
    Summarize this medical explanation in 1-2 sentences.
    Focus on the key learning point for AMC exam preparation.

    Explanation: {explanation['why_correct']}
    Key Points: {explanation['key_points']}
    """
    return llm.generate(prompt, max_tokens=100)
```

---

## Critical Mistake #7: Duplicate Files (_with_images)

### What Happened
- Created duplicate files: `week3_respiratory_200_mcqs.json` AND `week3_respiratory_200_mcqs_with_images.json`
- Both have identical placeholder content
- Doubled placeholder count (1,508 → 2,208 when counting duplicates)

### Why It Happened
- Image integration as separate step
- Copied placeholder content to image versions
- No deduplication logic

### Impact
- Inflated audit numbers (2,208 vs 1,508 unique MCQs)
- Extra validation time (12 files vs 7 unique files)
- Confusion about actual scope

### Correct Approach
```python
# Generate base MCQ ONCE with LLM
mcq = generate_mcq_with_agent_os(topic, specialty)

# Save base version
save_json(mcq, "base_mcqs.json")

# Create image version by REFERENCE (not copy)
if needs_images(mcq):
    mcq_with_images = add_images(mcq)
    save_json(mcq_with_images, "mcqs_with_images.json")

# NEVER copy placeholder content to create variants!
```

---

## Root Cause Analysis

### Why Did This Happen?

1. **Lack of Agent OS Integration from Start**
   - Used generic agent instead of medical expert agents
   - No specialty routing specified in task prompts
   - Agent OS infrastructure existed but not utilized

2. **Insufficient Constraint Enforcement**
   - Constraints documented (11, 12) but not implemented as gates
   - No incremental validation during generation
   - Validation scripts created reactively, not proactively

3. **Template-First Approach (Wrong)**
   - Focused on JSON structure before content quality
   - RAG citations fetched but not used by LLM
   - String interpolation instead of LLM generation

4. **No Fail-Fast Philosophy**
   - Generated all 2,958 items before validation
   - Discovered 12,732 errors after completion
   - Should have failed fast after first placeholder detected

---

## Prevention Measures (Already Deployed)

| Measure | Status | Location |
|---------|--------|----------|
| **Content Substance Validator** | ✅ Created | `scripts/validate_content_substance.sh` |
| **Pre-commit Hook** | ✅ Installed | `.git/hooks/pre-commit` |
| **Placeholder Pattern Detection** | ✅ Active | 6 patterns detected |
| **Agent OS Review System** | ✅ Complete | 3 expert reviews (20K words) |
| **Comprehensive Audit** | ✅ Done | 33 files audited, report saved |

---

## Lessons for Fresh Start (Jan-26 Generation)

### ✅ DO THIS:

1. **Use Agent OS Medical Experts**
   - Route Cardiology → MED-001
   - Route Respiratory → MED-002
   - Route Psychiatry → MED-009
   - Apply specialty-specific tools

2. **LLM-Powered Generation (Constraint 12)**
   - Extract RAG citation content
   - Pass to LLM as context
   - Generate real clinical scenarios
   - NO string templates!

3. **Enforce Constraints (11, 12)**
   - 3 citations per MCQ (fail-fast if <3)
   - LLM-powered generation (validate no placeholders)
   - Summary field required (validate length 50-200 chars)

4. **Fail-Fast Pipeline**
   - Pre-generation validation (RAG, LLM, Agent OS)
   - Incremental validation (per-MCQ)
   - Post-generation validation (QA-003, QA-001)
   - Pre-commit hook blocks invalid content

5. **Agent OS Task Delegation**
   ```python
   Task(
       subagent_type="medical-expert",
       specialty="cardiology",
       agent_id="MED-001",
       prompt="""
       Generate 200 cardiology MCQs using:
       - ECG interpretation tools
       - GRACE/TIMI calculators
       - Australian guidelines (eTG Cardiovascular)
       - RAG-verified citations (3 per MCQ)
       - Summary field (1-2 sentences)

       Validate incrementally:
       - No placeholder patterns
       - Patient demographics (age, gender)
       - Australian context (PBS, eTG references)
       """
   )
   ```

6. **Track Progress Properly**
   - Fully Regenerated vs Updated
   - Citations validated count
   - Placeholder patterns removed count
   - Agent OS usage confirmed

### ❌ DON'T DO THIS:

1. ❌ Generic OllamaClient without Agent OS routing
2. ❌ String templates ("Clinical scenario for...")
3. ❌ Generate first, validate later
4. ❌ Copy placeholder content to create variants
5. ❌ Skip specialty-specific tools
6. ❌ Assume RAG citations are enough (must pass to LLM!)
7. ❌ Create duplicate files (_with_images) during generation

---

## Success Metrics for Jan-26 Generation

| Metric | Target | Validation |
|--------|--------|------------|
| **Agent OS Usage** | 100% | All MCQs via MED-001/002/009 |
| **Placeholder Patterns** | 0 | Content substance validator |
| **Citation Count** | 3 per MCQ | Constraint 11 enforcement |
| **Summary Field** | 100% MCQs | Length 50-200 chars |
| **LLM-Powered** | 100% | No templates, all LLM-generated |
| **Specialty Tools** | Applied | ECG, spirometry, MSE used |
| **Australian Context** | 100% | eTG, RANZCP, AMH references |
| **QA-003 Auto-Approval** | >70% | Tier 1 confidence >0.90 |

---

## File Management (Jan-26)

### Old Data (Discard):
- `data/mcqs/` - 2,208 MCQs with placeholders (75% failure rate)
- Keep only: 400 valid MCQs for reference

### New Data (Jan-26):
- `data-jan-26/mcqs/` - Fresh generation with Agent OS
- `data-jan-26/osces/` - Fresh generation with Agent OS
- `data-jan-26/study_cards/` - Fresh generation with Agent OS

### Scripts:
- `scripts-jan-26/` - New scripts with Agent OS integration
- Archive old scripts to `scripts-archive/` for reference

---

**Document Owner**: Agent OS Review System
**Date**: 2026-01-26
**Next Action**: Create comprehensive Agent OS regeneration plan
**Reference**: CONTENT_AUDIT_REPORT.json, AGENT_OS_REVIEW_SUMMARY.md
