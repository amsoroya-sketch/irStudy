# QA-003 RAG Citation Validator - Design Document
**Created:** 2026-01-25 (Week 1, Day 3)
**Purpose:** Design automated RAG citation validation for MCQ generation
**Status:** Design Phase
**Implementation:** Week 1 Day 4 + Week 2

---

## 🎯 Overview

QA-003 is an automated citation validation system that uses RAG (Retrieval-Augmented Generation) to verify the accuracy and quality of citations in generated MCQs.

**Key Innovation:** Three-tier confidence scoring enables 90%+ auto-approval rate while maintaining quality.

---

## 📊 Current State Analysis (Day 3)

### MCQ Generation Progress
- **Total MCQs Generated:** 65 (Days 1-3)
- **Citation Quality:** Consistent 0.74-0.77 confidence (Tier 2)
- **Current Bottleneck:** Manual validation not scalable (target: 5,000 MCQs)

### Citation Confidence Distribution (Days 1-3)
```
Tier 1 (>0.90): 0% (0 MCQs) - Auto-approve
Tier 2 (0.75-0.90): 100% (65 MCQs) - LLM verify
Tier 3 (<0.75): 0% (0 MCQs) - Reject
```

**Observation:** All MCQs fall in Tier 2 → LLM verification will process 100% of MCQs initially.

---

## 🏗️ System Architecture

### Component 1: RAG Citation Validator (Week 1)
**File:** `src/agents/qa/qa_003_rag_validator.py`
**LOC Target:** 100 lines

**Responsibilities:**
1. Connect to Qdrant vector database
2. Query RAG system for citation verification
3. Calculate confidence scores (0.0-1.0)
4. Assign tier (1, 2, or 3)

**Key Class:**
```python
class RAGCitationValidator:
    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection = "medical_knowledge"
        self.embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    def validate_citation(
        self,
        citation_text: str,
        expected_pages: str = None
    ) -> dict:
        """
        Validate a single citation

        Returns:
            {
                'valid': bool,
                'confidence': float (0.0-1.0),
                'matches': list[dict],
                'tier': int (1, 2, or 3),
                'recommendation': str  # 'approve', 'llm_verify', 'reject'
            }
        """
        pass
```

### Component 2: Confidence Scorer (Week 1)
**LOC Target:** 50 lines

**Scoring Algorithm:**
```python
def calculate_confidence(rag_matches: list) -> float:
    """
    Multi-factor confidence scoring:

    Factors:
    1. Semantic similarity (RAG score): 60% weight
    2. Page number match: 20% weight
    3. Source type match: 10% weight
    4. Recency (publication year): 10% weight

    Returns:
        float: 0.0-1.0 confidence score
    """
    if not rag_matches:
        return 0.0

    top_match = rag_matches[0]

    # Factor 1: Semantic similarity
    semantic_score = top_match['score']  # 0.0-1.0

    # Factor 2: Page number match
    page_score = 1.0 if page_numbers_match(
        top_match['page'],
        expected_page
    ) else 0.5

    # Factor 3: Source type (guideline > journal > textbook)
    source_score = {
        'guideline': 1.0,
        'journal': 0.9,
        'textbook': 0.8,
        'other': 0.6
    }.get(top_match['source_type'], 0.5)

    # Factor 4: Recency
    recency_score = calculate_recency_score(top_match['year'])

    # Weighted average
    confidence = (
        semantic_score * 0.6 +
        page_score * 0.2 +
        source_score * 0.1 +
        recency_score * 0.1
    )

    return round(confidence, 3)
```

### Component 3: LLM Verifier (Week 2)
**LOC Target:** 80 lines

**Purpose:** Verify Tier 2 citations using Claude/GPT

**Process:**
```python
class LLMCitationVerifier:
    def verify_tier2_citation(
        self,
        mcq: dict,
        rag_matches: list
    ) -> dict:
        """
        Use LLM to verify Tier 2 citations

        LLM Prompt:
        "You are a medical citation validator.

        MCQ Question: {mcq_text}
        Citation Claim: {citation_text}
        RAG Evidence: {rag_matches}

        Verify if the citation accurately supports the MCQ content.
        Score: 1-10
        Justification: [explanation]
        "

        Returns:
            {
                'llm_verified': bool,
                'llm_score': int (1-10),
                'llm_justification': str,
                'final_recommendation': str  # 'approve', 'reject'
            }
        """
        pass
```

### Component 4: Summary Generator (Week 2)
**LOC Target:** 60 lines

**Purpose:** Generate validation summary reports

**Output Format:**
```json
{
  "validation_summary": {
    "total_mcqs": 100,
    "validated": 100,
    "tier1_auto_approved": 85,
    "tier2_llm_verified": 14,
    "tier2_llm_rejected": 1,
    "tier3_rejected": 0,
    "auto_approval_rate": 0.85,
    "total_approved": 99,
    "total_rejected": 1,
    "approval_rate": 0.99
  },
  "issues_found": [
    {
      "mcq_id": "PSY-DEP-20260125-345",
      "issue": "Citation page mismatch",
      "confidence": 0.78,
      "recommendation": "Regenerate with corrected citation"
    }
  ]
}
```

---

## 🎯 Three-Tier Confidence System

### Tier 1: Auto-Approve (>0.90 confidence)
**Action:** Automatically approve, no human/LLM review
**Expected Rate:** 85-90% of MCQs (Week 2+)
**Validation Time:** <2 seconds per MCQ

**Criteria:**
- High semantic similarity (>0.88)
- Page number matches OR source is primary guideline
- Recent source (≤3 years old)
- Australian source (eTG, RANZCP, AMH)

### Tier 2: LLM Verify (0.75-0.90 confidence)
**Action:** LLM verification required
**Expected Rate:** 10-15% of MCQs
**Validation Time:** ~10 seconds per MCQ (LLM call)

**Criteria:**
- Moderate semantic similarity (0.75-0.88)
- Page number mismatch OR missing page
- Older source (3-5 years) OR non-primary source

**Current Reality (Day 3):** 100% of MCQs in Tier 2
- Indicates citation queries need refinement
- Week 2 goal: Improve queries to push 85%+ into Tier 1

### Tier 3: Reject (<0.75 confidence)
**Action:** Automatically reject, regenerate MCQ
**Expected Rate:** 0-5% of MCQs
**Validation Time:** <2 seconds per MCQ

**Criteria:**
- Low semantic similarity (<0.75)
- No page number provided
- Outdated source (>10 years)
- Non-Australian source for Australian-specific content

---

## 📈 Performance Targets

### Week 1 Targets (Design + Initial Implementation)
- [x] Design document complete (Day 3) ✅
- [ ] RAGCitationValidator class implemented (Day 4)
- [ ] Confidence scoring algorithm working (Day 4)
- [ ] Validate 65 existing MCQs (Day 4)
- [ ] Calculate baseline metrics (Day 4)

### Week 2 Targets (Full Implementation)
- [ ] LLM verifier implemented
- [ ] Summary generator implemented
- [ ] Process 100 MCQs end-to-end
- [ ] Achieve 90%+ auto-approval rate
- [ ] Validation time <6s per MCQ (average)

### Quality Metrics
- **Precision:** 95%+ (citations marked valid are actually valid)
- **Recall:** 90%+ (valid citations are detected)
- **Speed:** <10s per MCQ (including LLM verification if needed)
- **Auto-Approval Rate:** >90% (Week 2+)

---

## 🔄 Validation Workflow

### Step 1: MCQ Generation (Current)
```
MED-009 Agent → Generate MCQ → Query RAG → Attach citations → Save MCQ
```

### Step 2: QA-003 Validation (Week 1 Day 4+)
```
Load MCQ → RAGCitationValidator.validate_citation() →
  if Tier 1 (>0.90): Auto-approve ✅
  if Tier 2 (0.75-0.90): Queue for LLM verification ⏳
  if Tier 3 (<0.75): Reject ❌
```

### Step 3: LLM Verification (Week 2)
```
Tier 2 MCQs → LLMVerifier.verify() →
  if LLM score ≥8/10: Approve ✅
  if LLM score <8/10: Reject ❌
```

### Step 4: Summary Report (Week 2)
```
All MCQs validated → Generate summary →
  Report auto-approval rate
  List issues found
  Recommendations for improvement
```

---

## 🚨 Identified Issues & Solutions

### Issue 1: All MCQs in Tier 2 (Current)
**Problem:** 100% of Day 1-3 MCQs have 0.74-0.77 confidence (Tier 2)
**Impact:** Requires LLM verification for ALL MCQs (slow, expensive)

**Root Causes:**
1. RAG queries too generic ("depression treatment Australian guidelines")
2. No page number verification in current implementation
3. Citation templates use placeholders (not RAG-selected sources)

**Solutions (Week 2):**
1. **Refine RAG queries:** More specific queries
   - Bad: "depression treatment Australian guidelines"
   - Good: "sertraline first-line major depressive disorder eTG psychiatry section 11.3"

2. **Page number matching:** Implement page verification
   ```python
   def verify_page_match(rag_page: str, citation_page: str) -> bool:
       # Extract page numbers, allow ±2 page tolerance
       return abs(parse_page(rag_page) - parse_page(citation_page)) <= 2
   ```

3. **Source prioritization:** Prefer eTG > RANZCP > AMH > journals

### Issue 2: Validation Speed
**Target:** <6 seconds per MCQ (average)
**Current:** Not yet measured

**Optimization Strategies:**
1. **Batch processing:** Validate 10 MCQs in parallel
2. **Caching:** Cache RAG results for common queries
3. **LLM batching:** Send multiple Tier 2 MCQs in single LLM call

---

## 📋 Test Cases (Week 1 Day 4)

### Test Case 1: High-Confidence Citation (Tier 1)
```json
{
  "citation": "Therapeutic Guidelines: Psychiatry, Section 11.3.4, 2024",
  "mcq_content": "SSRIs are first-line for major depressive disorder",
  "expected_confidence": 0.92,
  "expected_tier": 1,
  "expected_action": "auto-approve"
}
```

### Test Case 2: Moderate-Confidence Citation (Tier 2)
```json
{
  "citation": "RANZCP CPG Mood Disorders, p.45-47, 2023",
  "mcq_content": "Treatment-resistant depression management",
  "expected_confidence": 0.81,
  "expected_tier": 2,
  "expected_action": "llm_verify"
}
```

### Test Case 3: Low-Confidence Citation (Tier 3)
```json
{
  "citation": "General psychiatry textbook, 2010",
  "mcq_content": "Clozapine TGA monitoring requirements 2024",
  "expected_confidence": 0.62,
  "expected_tier": 3,
  "expected_action": "reject"
}
```

---

## 📊 Success Criteria

### Week 1 (Design + Initial Implementation)
- [x] Design document created (this document) ✅
- [ ] RAGCitationValidator class works (validates 1 MCQ successfully)
- [ ] Confidence scoring implemented and tested
- [ ] 65 Day 1-3 MCQs validated
- [ ] Baseline metrics calculated

### Week 2 (Full Implementation)
- [ ] LLM verifier implemented (processes Tier 2 MCQs)
- [ ] Summary generator produces reports
- [ ] 100 MCQs validated end-to-end
- [ ] 90%+ auto-approval rate achieved
- [ ] Average validation time <6 seconds
- [ ] Documentation updated with usage examples

---

## 🔗 Integration with Existing System

### Current RAG System (Already Operational)
- **Qdrant Database:** http://localhost:6333
- **Collection:** medical_knowledge (42,647 vectors)
- **Embedding Model:** S-PubMedBert-MS-MARCO
- **Sources:** StatPearls, Cochrane, eTG, RANZCP

### QA-003 Will Use:
- Same Qdrant instance
- Same embedding model
- Same collection
- **New:** Confidence scoring + LLM verification

**No infrastructure changes required** ✅

---

## 🎯 Next Steps (Day 4)

1. **Morning:**
   - Generate 20 suicide risk + MHA MCQs (Day 4 content task)

2. **Afternoon:**
   - Implement RAGCitationValidator class (50 LOC)
   - Implement confidence scoring (50 LOC)
   - Test on 10 sample MCQs
   - Validate all 65 Day 1-3 MCQs
   - Calculate baseline metrics

3. **End of Day 4:**
   - QA-003 initial implementation complete (50 LOC)
   - Validation working for existing MCQs
   - Metrics show Tier 1/2/3 distribution

---

**Document Version:** 1.0
**Status:** ✅ Design Complete (Day 3)
**Next Update:** Day 4 (Implementation start)
**Related Documents:**
- [QA-003 Upgrade Plan](QA_003_UPGRADE_PLAN.md)
- [PROJECT_STATUS_TRACKER.md](PROJECT_STATUS_TRACKER.md)
- [WEEK_01_EXECUTION.md](weekly/WEEK_01_EXECUTION.md)
