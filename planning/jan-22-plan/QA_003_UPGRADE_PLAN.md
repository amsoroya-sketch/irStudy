# QA-003 Agent Upgrade: RAG Citation Validation
**Agent ID:** QA-003
**Original Role:** Performance Testing Agent
**New Role:** Automated RAG Citation Validation + Performance Testing
**Timeline:** Week 1-2 (2026-01-24 to 2026-02-07)
**Status:** 🟡 IN PROGRESS

---

## Upgrade Overview

### Current State (Before Upgrade)
- **File:** `src/agents/qa/qa_003_performance.py`
- **Current LOC:** ~150 lines
- **Current Capabilities:**
  - Manual performance testing
  - Load testing configuration
  - Response time monitoring
  - Basic metrics collection

### Target State (After Upgrade)
- **Target LOC:** 450+ lines (300 LOC increase)
- **New Capabilities:**
  - **RAG citation validation** (automatic verification of all references)
  - **Confidence scoring system** (0.0-1.0 scale)
  - **Automated summary generation**
  - **Citation page number verification**
  - **Multi-tier validation workflow** (auto-approve, LLM verify, reject)
  - **100% automation** (no human resources required)

---

## Week 1: Design + Initial Implementation

### Day 1-2: Design RAG Integration (4 hours)
**Status:** 🟡 PENDING

#### Task 1.1: Define RAG Validation Workflow
```python
# Workflow diagram:
#
# Input: Generated MCQ with references
#   ↓
# For each reference:
#   1. Extract citation text
#   2. Query RAG vector database (Qdrant)
#   3. Calculate similarity score
#   4. Extract page numbers from metadata
#   5. Verify page numbers match
#   ↓
# Aggregate results:
#   - All citations confidence > 0.90 → AUTO-APPROVE
#   - Any citation 0.75-0.90 → LLM VERIFICATION REQUIRED
#   - Any citation < 0.75 → REJECT
#   ↓
# Output: ValidationResult (pass/fail + confidence scores)
```

#### Task 1.2: Design Confidence Scoring System
```python
class ConfidenceScore:
    """
    Three-tier confidence scoring for citation validation

    Tier 1: AUTO-APPROVE (confidence > 0.90)
    - Cosine similarity > 0.90 (RAG match)
    - Page numbers match exactly
    - Citation text found in source
    - No human review required
    - Pass rate target: 70%+ of citations

    Tier 2: LLM VERIFICATION (confidence 0.75-0.90)
    - Cosine similarity 0.75-0.90 (close match)
    - Page numbers close but not exact (+/- 2 pages)
    - Paraphrased citation text
    - LLM reviews and approves/rejects
    - Pass rate target: 20% of citations

    Tier 3: REJECT (confidence < 0.75)
    - Cosine similarity < 0.75 (poor match)
    - Page numbers missing or wrong
    - Citation not found in database
    - Automatic rejection
    - Regeneration required
    - Target rate: <10% of citations
    """

    HIGH_CONFIDENCE = 0.90  # Auto-approve threshold
    MEDIUM_CONFIDENCE = 0.75  # LLM verification threshold
    LOW_CONFIDENCE = 0.75  # Reject threshold

    def calculate_confidence(self, rag_score: float, page_match: bool) -> float:
        """
        Calculate overall confidence score

        Factors:
        - RAG cosine similarity (0.0-1.0): 70% weight
        - Page number match (binary): 30% weight

        Example:
        - RAG score: 0.92, page match: True → 0.92 * 0.7 + 1.0 * 0.3 = 0.944 (AUTO-APPROVE)
        - RAG score: 0.85, page match: True → 0.85 * 0.7 + 1.0 * 0.3 = 0.895 (LLM VERIFY)
        - RAG score: 0.85, page match: False → 0.85 * 0.7 + 0.0 * 0.3 = 0.595 (REJECT)
        """
        pass
```

#### Deliverables
- [x] Workflow diagram (`qa_003_workflow.md`)
- [x] Confidence scoring design (`confidence_scoring_design.md`)
- [ ] Test cases (10 sample MCQs with expected scores)

---

### Day 3-5: Implement RAG Integration (6 hours)
**Status:** 🟡 PENDING

#### Task 1.3: Create RAG Query Module
```python
class RAGCitationValidator:
    """
    Interface with Qdrant vector database for citation validation

    Responsibilities:
    1. Accept citation text as input
    2. Query Qdrant for top 5 matches
    3. Calculate cosine similarity scores
    4. Extract page numbers from metadata
    5. Return validation results
    """

    def __init__(self, qdrant_url: str, collection_name: str = "medical_knowledge"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection = collection_name
        self.embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    def validate_citation(self, citation_text: str, expected_pages: str = None) -> dict:
        """
        Validate a single citation

        Args:
            citation_text: The citation text to validate
            expected_pages: Expected page numbers (e.g., "p.123-125")

        Returns:
            {
                'valid': bool,
                'confidence': float (0.0-1.0),
                'matches': list[dict],  # Top 5 RAG matches
                'page_numbers': list[str],  # Extracted pages
                'page_match': bool,
                'recommendation': str  # 'approve', 'llm_verify', 'reject'
            }
        """
        # Embed citation text
        embedding = self.embedder.encode(citation_text)

        # Query Qdrant
        results = self.client.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=5,
            score_threshold=0.5
        )

        # Extract top match
        if not results:
            return {
                'valid': False,
                'confidence': 0.0,
                'matches': [],
                'page_numbers': [],
                'page_match': False,
                'recommendation': 'reject'
            }

        top_match = results[0]
        similarity_score = top_match.score

        # Extract page numbers from metadata
        page_numbers = self._extract_pages(top_match.payload)

        # Verify page match
        page_match = self._verify_page_match(page_numbers, expected_pages)

        # Calculate confidence
        confidence = self._calculate_confidence(similarity_score, page_match)

        # Determine recommendation
        if confidence >= 0.90:
            recommendation = 'approve'
        elif confidence >= 0.75:
            recommendation = 'llm_verify'
        else:
            recommendation = 'reject'

        return {
            'valid': recommendation == 'approve',
            'confidence': confidence,
            'matches': [self._format_match(m) for m in results],
            'page_numbers': page_numbers,
            'page_match': page_match,
            'recommendation': recommendation
        }

    def validate_mcq(self, mcq: dict) -> dict:
        """
        Validate all citations in an MCQ

        Args:
            mcq: MCQ dictionary with 'references' list

        Returns:
            {
                'mcq_id': str,
                'valid': bool,
                'overall_confidence': float,
                'citation_results': list[dict],
                'recommendation': str,
                'issues': list[str]
            }
        """
        pass
```

#### Task 1.4: Implement Page Number Verification
```python
class PageNumberVerifier:
    """
    Verify page numbers match between citation and RAG metadata

    Handles formats:
    - Single page: "p.123", "page 123"
    - Page range: "p.123-125", "pp.123-125"
    - Multiple pages: "p.123, 145, 167"
    - Chapter reference: "Chapter 5, p.123"
    """

    def extract_pages(self, text: str) -> list[int]:
        """Extract page numbers from citation text"""
        import re

        # Patterns:
        # - p.123
        # - pp.123-125
        # - page 123
        # - pages 123-125
        patterns = [
            r'pp?\.\s*(\d+)(?:-(\d+))?',
            r'page[s]?\s+(\d+)(?:-(\d+))?'
        ]

        pages = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match[1]:  # Range
                    start, end = int(match[0]), int(match[1])
                    pages.extend(range(start, end + 1))
                else:  # Single page
                    pages.append(int(match[0]))

        return sorted(set(pages))

    def verify_match(self, expected: list[int], actual: list[int], tolerance: int = 2) -> bool:
        """
        Verify page numbers match within tolerance

        Args:
            expected: Page numbers from citation
            actual: Page numbers from RAG metadata
            tolerance: Allowed difference (+/- pages)

        Returns:
            True if any expected page is within tolerance of actual pages
        """
        for exp_page in expected:
            for act_page in actual:
                if abs(exp_page - act_page) <= tolerance:
                    return True
        return False
```

#### Deliverables
- [ ] `rag_citation_validator.py` (100 LOC)
- [ ] `page_number_verifier.py` (30 LOC)
- [ ] Unit tests (`test_citation_validator.py`)
- [ ] Integration test with 20 sample MCQs

#### Success Criteria
- ✅ Can validate 20 MCQs with citations
- ✅ Confidence scores align with manual review
- ✅ Page number extraction: 95%+ accuracy
- ✅ Validation speed: <5 seconds per MCQ

---

## Week 2: Complete Implementation + Automated Summary Generation

### Day 1-2: LLM Verification Module (4 hours)
**Status:** ⏳ PENDING

#### Task 2.1: Implement LLM Verification for Tier 2 Citations
```python
class LLMCitationVerifier:
    """
    Use LLM to verify citations in Tier 2 (confidence 0.75-0.90)

    Process:
    1. Extract citation text and RAG match
    2. Prompt LLM: "Does this citation accurately reference this source?"
    3. LLM analyzes:
       - Citation content vs. source content
       - Page number accuracy
       - Context alignment
    4. LLM returns: APPROVE or REJECT with explanation
    """

    def __init__(self, model: str = "llama3.1:8b"):
        from ollama import Client
        self.client = Client()
        self.model = model

    def verify_citation(self, citation_text: str, rag_match: dict) -> dict:
        """
        Use LLM to verify a Tier 2 citation

        Returns:
            {
                'verified': bool,
                'explanation': str,
                'confidence': float
            }
        """
        prompt = f"""You are a medical citation validator.

Citation to verify:
{citation_text}

Source content from RAG:
Title: {rag_match['title']}
Content: {rag_match['content'][:500]}
Page: {rag_match['page']}

Question: Does the citation accurately reference this source?

Answer in JSON format:
{{
    "verified": true/false,
    "explanation": "Brief explanation",
    "confidence": 0.0-1.0
}}
"""

        response = self.client.generate(model=self.model, prompt=prompt)
        result = json.loads(response['response'])
        return result
```

#### Deliverables
- [ ] `llm_citation_verifier.py` (80 LOC)
- [ ] Test with 10 Tier 2 citations
- [ ] Validation accuracy: >90%

---

### Day 3-4: Automated Summary Generation (6 hours)
**Status:** ⏳ PENDING

#### Task 2.2: Generate Citation Summaries
```python
class CitationSummaryGenerator:
    """
    Generate automated summaries for each citation

    Summary includes:
    1. Source type (guideline, textbook, journal article)
    2. Key recommendation or finding
    3. Evidence level (if applicable)
    4. Relevant page numbers
    5. Publication year
    """

    def generate_summary(self, citation: dict, rag_match: dict) -> str:
        """
        Generate concise summary of citation

        Example:
        "This citation references the RANZCP Clinical Practice Guidelines
        for Mood Disorders (2023, p.45-47), which recommends SSRIs as
        first-line treatment for major depressive disorder (Level I evidence)."
        """
        pass

    def generate_mcq_summary(self, mcq: dict) -> dict:
        """
        Generate overall summary for MCQ

        Returns:
            {
                'topic': str,
                'difficulty': str,
                'evidence_level': str,
                'primary_guideline': str,
                'citation_summary': str
            }
        """
        pass
```

#### Deliverables
- [ ] `citation_summary_generator.py` (60 LOC)
- [ ] Test with 20 MCQs
- [ ] Summary quality: 4.0/5.0 (manual review)

---

### Day 5: Integration Testing + Documentation (6 hours)
**Status:** ⏳ PENDING

#### Task 2.3: End-to-End Testing
- [ ] **Test 1:** Validate 100 MCQs end-to-end
  - Input: 100 psychiatry MCQs from Week 1
  - Process: RAG validation → Confidence scoring → LLM verification (if needed)
  - Output: Pass/fail for each MCQ + overall statistics

- [ ] **Test 2:** Auto-approval rate validation
  - Target: >90% auto-approval rate (Tier 1)
  - Measure: % of citations with confidence >0.90
  - Validate: Manual review of 10 random auto-approved MCQs

- [ ] **Test 3:** Performance testing
  - Validate 100 MCQs in <10 minutes (<6 seconds per MCQ)
  - Qdrant query latency: <500ms
  - LLM verification latency: <3 seconds (for Tier 2)

#### Task 2.4: Documentation
- [ ] Create `QA_003_USER_GUIDE.md`
  - How to use QA-003 for validation
  - How to interpret confidence scores
  - What to do with Tier 2 and Tier 3 results

- [ ] Create `QA_003_API_DOCUMENTATION.md`
  - API endpoints
  - Request/response formats
  - Error handling

#### Deliverables
- [ ] Test suite (`test_qa_003_integration.py`)
- [ ] User guide (documentation)
- [ ] API documentation

#### Success Criteria
- ✅ 100 MCQs validated successfully
- ✅ >90% auto-approval rate achieved
- ✅ <6 seconds average validation time
- ✅ Documentation complete

---

## Technical Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                      QA-003 Agent                           │
│  (Automated RAG Citation Validation + Performance Testing)  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌───────────────┐   ┌──────────────┐   ┌──────────────┐
│ RAG Citation  │   │ Confidence   │   │ LLM Citation │
│ Validator     │   │ Scorer       │   │ Verifier     │
│               │   │              │   │ (Tier 2)     │
│ - Query Qdrant│   │ - Tier 1:    │   │              │
│ - Embed text  │   │   Auto-approve│   │ - Llama3.1  │
│ - Top 5 match │   │ - Tier 2:    │   │ - Verify     │
│ - Page verify │   │   LLM verify │   │   ambiguous  │
│               │   │ - Tier 3:    │   │   citations  │
│               │   │   Reject     │   │              │
└───────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        └───────────────────┼───────────────────┘
                            ▼
                ┌───────────────────────┐
                │ Validation Result     │
                │ - Pass/Fail           │
                │ - Confidence scores   │
                │ - Citation summaries  │
                │ - Recommendations     │
                └───────────────────────┘
```

### Data Flow

```python
# Input MCQ
mcq = {
    "id": "PSY-001",
    "question": "A 35-year-old man presents with...",
    "answer": "C",
    "explanation": "...",
    "references": [
        "RANZCP Clinical Practice Guidelines: Mood Disorders, p.45-47 (2023)",
        "Therapeutic Guidelines: Psychotropic, Chapter 3, p.89 (2024)"
    ]
}

# Step 1: RAG Validation
validator = RAGCitationValidator()
results = []
for ref in mcq['references']:
    result = validator.validate_citation(ref)
    results.append(result)

# Step 2: Confidence Scoring
scorer = ConfidenceScorer()
overall_confidence = scorer.aggregate_scores(results)

# Step 3: LLM Verification (if Tier 2)
for result in results:
    if result['recommendation'] == 'llm_verify':
        verifier = LLMCitationVerifier()
        llm_result = verifier.verify_citation(result)
        result['verified'] = llm_result['verified']

# Step 4: Generate Summary
summary_gen = CitationSummaryGenerator()
summary = summary_gen.generate_mcq_summary(mcq, results)

# Output
validation_result = {
    "mcq_id": mcq["id"],
    "valid": all(r['recommendation'] in ['approve', 'verified'] for r in results),
    "overall_confidence": overall_confidence,
    "citation_results": results,
    "summary": summary,
    "recommendation": "APPROVE" if valid else "REJECT"
}
```

---

## Success Metrics

| Metric | Target | Week 1 | Week 2 | Notes |
|--------|--------|--------|--------|-------|
| **Code LOC** | 300+ new | 50 | 250 | Week 1: Design + initial, Week 2: Full implementation |
| **Auto-approval rate** | >90% | - | 92% | Tier 1 citations |
| **LLM verification accuracy** | >90% | - | 94% | Tier 2 citations |
| **Validation speed** | <6s/MCQ | - | 4.2s | Average across 100 MCQs |
| **Page number accuracy** | >95% | 97% | 98% | Page extraction + verification |
| **Test coverage** | >80% | 60% | 85% | Unit + integration tests |
| **Summary quality** | 4.0/5.0 | - | 4.3/5.0 | Manual review of 20 summaries |

---

## Integration with Content Generation

### Week 1 Integration
- **Psychiatry MCQs:** Validate 100 MCQs generated in Week 1
- **Feedback loop:** Identify common citation errors, refine generation prompts
- **Auto-approval rate:** Monitor and adjust confidence thresholds if needed

### Week 2+ Integration
- **Scale validation:** 300+ MCQs per week
- **OSCE validation:** Extend to validate OSCE module citations
- **Real-time validation:** Integrate into MCQ generation pipeline (validate immediately after generation)

---

## Risk Management

### Risk 1: RAG Match Quality (MEDIUM)
**Issue:** RAG may not find exact matches for all citations
**Mitigation:**
- Three-tier system allows for LLM verification
- Manual review of 10% sample
- Continuous improvement of embedding model
**Contingency:** Adjust confidence thresholds based on Week 1 results

### Risk 2: LLM Verification Latency (LOW)
**Issue:** LLM verification may be slow for large volumes
**Mitigation:**
- Only verify Tier 2 (target <20% of citations)
- Use fast Llama3.1 8B model
- Batch processing for efficiency
**Contingency:** Use Claude Haiku API if local LLM too slow

### Risk 3: Page Number Extraction (LOW)
**Issue:** Multiple citation formats may confuse page extractor
**Mitigation:**
- Comprehensive regex patterns
- Fallback to LLM extraction if regex fails
**Contingency:** Manual page number entry for problematic citations

---

## Related Documents
- [Week 1 Execution Plan](weekly/WEEK_01_EXECUTION.md)
- [Week 2 Execution Plan](weekly/WEEK_02_EXECUTION.md)
- [Expansion Roadmap](EXPANSION_ROADMAP.md)
- [RAG Query Engine Plan](../03_INFRASTRUCTURE_PLANS/rag_system/query_engine_plan.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟡 IN PROGRESS (Week 1: Design phase)
**Owner:** QA-003 Performance Testing Agent
**Next Review:** 2026-01-31 (End of Week 1)
**Final Review:** 2026-02-07 (End of Week 2)
