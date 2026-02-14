# Phase 3: RAG & Content Generation (UPDATED 2026-01-24)
## Comprehensive Medical Content Expansion with RAG-Verified Citations

**Duration:** 14-20 weeks (expanded from original 4 weeks)
**Priority:** P1 (Critical for content scaling)
**Dependencies:** ✅ Phase 1 complete | ✅ RAG Infrastructure COMPLETE
**Status:** 🔄 IN PROGRESS (RAG complete, content generation phase)
**Estimated Effort:** 400-600 hours across 4 parallel tracks

---

## 🎉 RAG SYSTEM: COMPLETE & PRODUCTION-READY

**Completion Date:** 2026-01-24
**Status:** ✅ OPERATIONAL

### Current RAG System Stats

| Metric | Value | Status |
|--------|-------|--------|
| **Total Vectors** | **42,647** | ✅ Complete |
| **Medical Textbooks** | 9,950 chunks (14 books) | ✅ Indexed |
| **StatPearls Articles** | 17,314 chunks (9,627 articles) | ✅ Indexed |
| **Cochrane Reviews** | 15,383 chunks (78 PDFs) | ✅ NEW (added 2026-01-24) |
| **Search Quality** | 0.95+ relevance scores | ✅ Excellent |
| **Response Time** | <100ms (p95) | ✅ Fast |
| **Qdrant Status** | GREEN | ✅ Healthy |

**Growth:** +15,383 vectors (+56%) from original 27,264 baseline

### RAG Content Breakdown

```
Original Content (27,264 vectors):
├── Medical Textbooks: 9,950 chunks
│   ├── John Murtagh GP 8th Ed (~1,400)
│   ├── Talley Clinical Examination 8th Ed (~1,200)
│   ├── Oxford Handbook Emergency Medicine (~800)
│   ├── Churchill's Differential Diagnosis (~700)
│   ├── AMC Anthology (~600)
│   ├── ECG books (~1,000)
│   └── Australian guidelines (~800)
└── StatPearls: 17,314 chunks
    └── 9,627 articles, 12 million words

NEW Content (15,383 vectors):
└── Cochrane Systematic Reviews: 15,383 chunks
    ├── 78 new PDFs (2026-01-24 addition)
    ├── 9,698 pages
    └── ~5 million words of evidence-based medicine

TOTAL: 42,647 vectors (PRODUCTION-READY)
```

### What the Expanded RAG Enables

**1. 100% Citation-Verified Content**
- All generated MCQs include RAG-verified citations with page numbers
- Automated confidence scoring (>0.90 auto-approve, 0.75-0.90 LLM verify, <0.75 reject)
- Summary from citation for correct answers (new requirement)

**2. Evidence-Based Medicine Integration**
- 15,383 new Cochrane systematic review chunks
- Access to gold-standard evidence for clinical questions
- Support for 150+ evidence summaries generation

**3. Comprehensive Specialty Coverage**
- 42,647 searchable chunks across all AMC specialties
- Cardiology, Respiratory, GI, Endocrine, Neuro, Emergency, ObGyn, Paeds, Psych, GP
- Australian guidelines (eTG, AMH, PBS) prioritized in search

**4. Scalable Content Generation**
- Target: 5,000+ MCQs (10x original 500 target)
- Target: 150-170 OSCE modules (from 46)
- 100% automated with QA validation

---

## REVISED PLAN: 14-20 Week Expansion (4 Parallel Tracks)

**Original Plan:** 4 weeks, 500 MCQs, 20 OSCE stations
**Revised Plan:** 14-20 weeks, 5,000+ MCQs, 150-170 OSCE modules, comprehensive expansion

**Duration:** 4 weeks (original) → **14-20 weeks** (expanded)
**Priority:** P1 (Critical for content scaling)
**Dependencies:** ✅ Phase 1 complete | ✅ RAG Infrastructure COMPLETE
**Status:** 🔄 IN PROGRESS (RAG complete, ready for content generation)
**Estimated Effort:** 120-140 hours (original) → **400-600 hours** (expanded across 4 parallel tracks)

---

## Updated Objectives

1. ✅ **RAG System** - COMPLETE (42,647 vectors operational)
2. **Expand Medical Expert Agents** - 8 agents from 115 LOC → 850+ LOC
3. **Upgrade QA System** - QA-003 with RAG integration (100% automated citation validation)
4. **Generate 5,000+ MCQs** - All specialties with RAG-verified citations + summaries
5. **Create 150-170 OSCE Modules** - Including 283 Marwan cases + 17 psychiatry topics
6. **Evidence Summaries & Clinical Pathways** - 150+ summaries, 30+ pathways, 50+ pharm cards
7. **100% Citation Coverage** - All new and existing content with RAG verification
8. **Picture Integration** - 500+ images from source books/internet

---

## 4 PARALLEL EXECUTION TRACKS

### Track 1: Agent Expansion (Weeks 1-8) 🤖

**Goal:** Expand 8 medical expert agents to full 850+ LOC implementation

**Current Status:**
- ✅ MED-001 Cardiology: 1,138 LOC (fully implemented)
- ✅ MED-002 Respiratory: 1,023 LOC (fully implemented)
- ⏳ MED-003 through MED-010: 115 LOC templates (need expansion)

**Priority Order:**

**CRITICAL (Weeks 1-2): MED-009 Psychiatry**
- **Why:** 17 topics identified in handwritten requirements (biggest content gap)
- Expand from 115 LOC → 850+ LOC
- Add specialized tools:
  - Mental state examination framework
  - Risk assessment (suicide, harm to others)
  - Australian Mental Health Act compliance
  - Psychiatric medication side effects
- Topics to cover:
  1. Loneliness/Empty nest syndrome
  2. Normal grief
  3. Post-partum blues
  4. Post-partum depression & melancholia
  5. Mania
  6. GAD (Generalized Anxiety Disorder)
  7. Panic disorder & agoraphobia
  8. Adjustment disorder
  9. Development disability & adjustment disorder
  10. Eating disorders
  11. Conversion aphonia
  12. Somatization
  13. Hypochondriasis
  14. Antisocial personality disorder
  15. Histrionic personality disorder
  16. Medication side effects
  17. Counseling for ECT

**HIGH Priority (Weeks 3-8):**
- Week 3-4: MED-003 Gastroenterology + MED-004 Endocrinology
- Week 5-6: MED-005 Neurology + MED-006 Emergency Medicine
- Week 7-8: MED-007 ObGyn + MED-008 Paediatrics + MED-010 General Practice

**Reference Implementation Pattern:**
- Use MED-001 (1,138 LOC) and MED-002 (1,023 LOC) as templates
- Components to replicate:
  - Specialty-specific scoring tools (200-300 LOC)
  - Clinical assessment methods (200-300 LOC)
  - Content generation with RAG (200-300 LOC)
  - RAG integration for citations (100-150 LOC)
  - Validation methods (50-100 LOC)

---

### Track 2: Content Generation (Weeks 1-20) 📝

**Goal:** Generate comprehensive medical content with 100% RAG-verified citations

#### 2.1 MCQ Generation: 5,000+ Questions

**Distribution by Specialty:**

| Specialty | Target MCQs | Priority | Agent |
|-----------|-------------|----------|-------|
| **Psychiatry** | **500** | **CRITICAL** | MED-009 |
| Cardiology | 500 | HIGH | MED-001 ✅ |
| Respiratory | 500 | HIGH | MED-002 ✅ |
| Gastroenterology | 500 | HIGH | MED-003 |
| Endocrinology | 500 | HIGH | MED-004 |
| Neurology | 500 | HIGH | MED-005 |
| Emergency | 500 | HIGH | MED-006 |
| ObGyn | 500 | MEDIUM | MED-007 |
| Paediatrics | 500 | MEDIUM | MED-008 |
| General Practice | 500 | MEDIUM | MED-010 |
| **TOTAL** | **5,000** | - | - |

**Format Requirements (from jan22-review/instructions.txt):**
- Clinical scenario stem (patient presentation)
- 5 options (A-E), single best answer
- Detailed explanation (100-200 words)
- **Minimum 2 citations with page/section numbers**
- **Summary from citation for correct answer** (NEW REQUIREMENT)
- Images from source books where applicable

**Difficulty Distribution:**
- Easy (ICRP level): 40% (2,000 MCQs)
- Medium (AMC level): 40% (2,000 MCQs)
- Hard (complex cases): 20% (1,000 MCQs)

#### 2.2 OSCE Module Generation: 150-170 Stations

**Current:** 46 OSCE modules
**Target:** 150-170 modules

**Expansion Sources:**

**A. 283 Marwan Medicine Cases** (organized by clusters)
- Cardiovascular cluster: ~30 cases (chest pain, palpitations, syncope)
- Respiratory cluster: ~35 cases (SOB, cough, pneumonia)
- Tiredness cluster: ~15 cases (anemia, hypothyroid, endocarditis)
- GI cluster: ~40 cases (abdominal pain, hepatitis, diarrhea)
- MSK cluster: ~30 cases (limb pain, back pain, joint pain)
- Counseling cluster: ~25 cases
- Miscellaneous: ~50 cases

**B. 17 Psychiatry Topics** (CRITICAL - from handwritten requirements)
- Each topic → 1 complete OSCE module
- Format: Mental state exam + risk assessment + management + MHPA considerations
- 8-minute station design (9-Principle OSCE Framework)

**C. 4 AMC Blueprint Gaps**
1. Anaphylaxis management (HIGH-YIELD)
2. ECG interpretation (20 common patterns)
3. DKA/HHS management
4. Seizures & status epilepticus

**Target Distribution After Expansion:**
- Medicine: 40 modules (8 current + 32 new)
- **Psychiatry: 22 modules** (5 current + 17 new) - CRITICAL
- Emergency: 20 modules (new)
- General Practice: 25 modules (new)
- Paediatrics: 15 modules (5 current + 10 new)
- Surgery: 15 modules (5 current + 10 new)
- ObGyn: 12 modules (4 current + 8 new)
- Ethics/Communication: 10 modules (6 current + 4 new)
- Mock Stations: 5 modules (1 current + 4 new)
- **TOTAL: 164 modules**

#### 2.3 Additional Content Types

**Evidence Summaries: 150+ Topics**
- Format: Clinical question → Evidence from RAG → Australian guidelines → Clinical bottom line
- 500-1000 words per topic
- High-yield AMC topics across all specialties

**Clinical Reasoning Pathways: 30+**
- Differential diagnosis approaches (chest pain, SOB, abdominal pain, headache, etc.)
- Flowchart + detailed text + evidence citations

**Investigation Pathways: 10+**
- Abnormal ECG, CXR, LFTs, TFTs, FBC, renal function, urinalysis, lipids, glucose, coagulation
- Systematic interpretation + next steps

**Australian Pharmacology Cards: 50+**
- Australian drug names (paracetamol NOT acetaminophen)
- PBS restrictions and AMH dosing
- Organized by class: antibiotics, cardiovascular, analgesics, antidiabetics, respiratory, psychiatric

**Clinical Prediction Rules: 20+**
- GRACE, TIMI, CHA2DS2-VASc, HAS-BLED, Wells DVT/PE, CURB-65, PERC, ABCD2, NIHSS, Glasgow-Blatchford, Rockall, FRAX, Framingham, qSOFA, Centor, Ottawa Ankle/Knee Rules

**Red Flags Compilations: 10+ by System**
- Chest pain, SOB, abdominal pain, headache, back pain, neuro, psychiatric, paediatric, obstetric, general red flags
- Include Australian emergency protocols (000, MET call criteria)

**Pictures from Sources: 500+ Target**
- ECGs (100), CXRs (50), Dermatology (100), Ophthalmology (30), Radiology (50), Clinical signs (100), Investigations (70)
- Extract from source books or find from internet
- All with proper citations

---

### Track 3: Quality Assurance (Weeks 1-20) ✅

**Goal:** 100% automated validation with NO human resources

#### 3.1 Upgrade QA-003 Citation Validator

**Current:** 73 LOC, basic citation presence checking
**Target:** 300+ LOC, full RAG integration

**New Features:**

**A. RAG Integration (100 LOC)**
```python
def verify_citation_with_rag(self, claim: str, citation: Dict) -> float:
    """
    Verify citation accuracy using RAG system

    Returns:
        confidence_score: 0.0-1.0
    """
    # Query RAG with claim
    # Check if cited source matches retrieved chunks
    # Verify page/section numbers
    # Return semantic similarity score
```

**B. Confidence Scoring (80 LOC)**
- >0.90 similarity: **Auto-approve** (no human review)
- 0.75-0.90: **Automated LLM verification** (Claude confirms)
- <0.75: **Auto-reject** (regenerate content automatically)

**C. Automated Summary Generation (60 LOC)**
```python
def generate_summary_from_citation(self, concept: str, citation: Dict) -> str:
    """
    Generate 2-3 sentence summary from cited source using RAG

    Required for: MCQ correct answer explanations
    """
    # Query RAG for concept
    # Extract relevant sentences from source
    # Return summary with citation
```

**D. Image Validation (60 LOC)**
- Scan content for visual concepts (ECG, CXR, rash, etc.)
- Check if image exists in source materials
- Flag for internet search if not found
- Validate image citations (figure number, page)

#### 3.2 Maintain 7-Agent QA System

**Current QA Agents:**
- QA-001: Australian Standards Compliance (223 LOC) ✅
- QA-002: Clinical Accuracy Validation (240 LOC) ✅
- QA-003: Citation Validator (73 LOC) → **UPGRADE to 300+ LOC**
- QA-004: Format Validator (115 LOC) ✅

**Automated QA Pipeline:**
```
Content Generation → QA-001 (Australian) → QA-002 (Clinical) →
QA-003 (Citations) → QA-004 (Format) → Approved Content
```

**No Human Intervention:**
- All validation automated
- Rejection triggers automatic regeneration
- Statistics logged for monitoring
- Weekly automated reports

---

### Track 4: Existing Content Enhancement (Weeks 5-15) 🔄

**Goal:** Add 100% RAG citations to all existing content

**Existing Content Status:**
- 46 OSCE modules (need citations)
- 750 flashcards (need citations)
- Various study materials (need citations)

**Enhancement Process:**
1. **Read existing content** (Week 5)
2. **Extract all clinical claims** (Week 6-7)
3. **Query RAG for citations** (Week 8-10)
4. **Generate summaries from citations** (Week 11-12)
5. **Integrate pictures from sources** (Week 13-15)

**Target:**
- 100% of 46 OSCE modules have RAG-verified citations
- 750 flashcards enhanced with citations
- Pictures integrated where applicable

---

## Week 7: RAG System Implementation

### Monday-Tuesday: Core RAG Query Engine (16 hours)
**Goal:** Build the foundation retrieval system

**Task 1: Query Engine Class** (8 hours)
```python
# File: src/rag/query_engine.py

class MedicalRAGSystem:
    """
    Production RAG system for AMC exam content generation

    Pipeline:
    1. Query embedding (S-PubMedBert)
    2. Vector search (Qdrant)
    3. Result reranking (cross-encoder)
    4. Context building (4096 token limit for Meditron)
    5. LLM generation with citations
    """

    def __init__(self):
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.embedding_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        self.reranker = CrossEncoder('ms-marco-MiniLM-L-12-v2')
        self.llm = OllamaClient()

    def query(self, question: str, specialty: str = None, context_limit: int = 10) -> dict:
        """
        RAG query with Australian guideline focus

        Args:
            question: Medical question (e.g., "What is first-line management for STEMI?")
            specialty: Filter by specialty (e.g., "cardiology")
            context_limit: Number of context chunks to use

        Returns:
            {
                "answer": "Generated answer with Australian guidelines",
                "sources": [{"title": "...", "page": 123, "source": "eTG"}],
                "citations": ["eTG Cardiovascular p.45", "Therapeutic Guidelines p.123"],
                "confidence": 0.92
            }
        """
        # Implementation details below
```

**Implementation Steps:**
1. **Query Embedding** (2 hours)
   - Embed user question using S-PubMedBert
   - Handle medical terminology correctly
   - Test with 50 sample AMC questions

2. **Vector Search** (3 hours)
   - Search Qdrant with filters (specialty, source, recency)
   - Retrieve top 50 candidates
   - Test search accuracy (manual validation)

3. **Reranking** (2 hours)
   - Use cross-encoder to rerank results
   - Prioritize Australian guidelines (eTG, TG, NSW Health)
   - Keep top 10 most relevant

4. **Context Building** (1 hour)
   - Assemble context from top chunks
   - Stay within 4096 token limit (Meditron)
   - Include source metadata for citations

**Success Criteria:**
- ✅ Search returns relevant results (>90% accuracy on test set)
- ✅ Reranking improves relevance (A/B test vs no reranking)
- ✅ Context fits within token limit
- ✅ Response time <3 seconds (p95)

---

**Task 2: LLM Integration** (8 hours)
```python
def generate_with_llm(self, query: str, context: List[str]) -> dict:
    """
    Generate answer using local LLM (Meditron or Llama 3.1)

    Model Selection:
    - Meditron 7B: Fast, medical-specific (40-60 tokens/sec)
    - Llama 3.1 70B: Slower, better reasoning (10-20 tokens/sec)
    - Use Meditron for simple Q&A, Llama for complex clinical reasoning
    """

    # Build prompt with Australian context
    prompt = f"""
You are an expert in Australian medical practice preparing content for AMC (Australian Medical Council) examinations.

Context from Australian guidelines and textbooks:
{context}

Question: {query}

Provide a comprehensive answer following Australian medical guidelines (Therapeutic Guidelines, eTG, NSW Health protocols). Include:
1. Direct answer to the question
2. Australian-specific management approaches
3. Relevant investigations and their interpretation
4. Red flags and when to escalate
5. Evidence-based references

Answer:"""

    # Generate with appropriate model
    response = self.llm.generate(
        prompt=prompt,
        model_name=self.select_model(query),
        temperature=0.3,  # Lower for medical accuracy
        max_tokens=800
    )

    return self.parse_response(response)
```

**Implementation Steps:**
1. **Model Router** (2 hours)
   - Implement model selection logic
   - Route simple questions → Meditron 7B
   - Route complex reasoning → Llama 3.1 70B
   - Test routing accuracy

2. **Prompt Engineering** (4 hours)
   - Design system prompt for Australian guidelines
   - Test with 20 AMC-style questions
   - Iteratively improve based on output quality
   - Document best practices

3. **Response Parsing** (2 hours)
   - Extract answer text
   - Extract citations
   - Handle edge cases (incomplete responses, hallucinations)
   - Validate output format

**Success Criteria:**
- ✅ LLM generates medically accurate answers (validated by medical reviewer)
- ✅ Citations are included and correct
- ✅ Australian guidelines are prioritized
- ✅ Response time acceptable (<5s total pipeline)

---

### Wednesday-Thursday: Context Optimization (16 hours)

**Task 1: Advanced Reranking** (8 hours)
```python
# File: src/rag/reranker.py

class AustralianGuidelineReranker:
    """
    Specialized reranker prioritizing Australian medical sources

    Priority Order:
    1. Therapeutic Guidelines (eTG) - highest weight
    2. Australian Medicines Handbook (AMH)
    3. NSW Health guidelines
    4. RACGP Red Book
    5. Australian Immunisation Handbook
    6. International guidelines (lower weight)
    7. Research papers (lowest weight for clinical questions)
    """

    def rerank(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        # Implement weighted reranking
        pass
```

**Features to Implement:**
- Source weighting (eTG = 2.0x, research papers = 0.5x)
- Recency boost (newer guidelines weighted higher)
- Specialty relevance (cardiology question → cardiology section)
- Australian context detection (prioritize Australian data)

**Testing:**
- Create test set of 50 AMC questions
- Compare reranking vs no reranking
- Target: 20%+ improvement in relevance

---

**Task 2: Context Window Management** (8 hours)
```python
# File: src/rag/context_manager.py

class ContextWindowManager:
    """
    Manage context within LLM token limits

    Token Limits:
    - Meditron 7B: 4096 tokens
    - Llama 3.1 70B: 128k tokens (but use 8k for performance)

    Strategy:
    - Reserve 1024 tokens for prompt + question
    - Reserve 1024 tokens for response
    - Use remaining ~2000 tokens for context
    - ~500 words of context (2000 tokens / 4 tokens per word)
    """

    def build_context(self, chunks: List[str], max_tokens: int = 2000) -> str:
        # Implement token-aware context building
        pass

    def compress_context(self, context: str, target_tokens: int) -> str:
        # Summarize if context too long
        pass
```

**Features:**
- Token counting (tiktoken library)
- Smart truncation (keep most relevant parts)
- Context compression (summarization if needed)
- Citation preservation (always keep source info)

---

### Friday: RAG System Testing & Validation (8 hours)

**Task: Comprehensive RAG Testing**
```bash
# Test suite for RAG system
pytest tests/rag/test_query_engine.py
pytest tests/rag/test_reranker.py
pytest tests/rag/test_context_manager.py
```

**Test Categories:**
1. **Unit Tests** (2 hours)
   - Test each component independently
   - Mock external dependencies (Qdrant, LLM)
   - 80%+ code coverage

2. **Integration Tests** (2 hours)
   - Test full RAG pipeline
   - Use real Qdrant instance
   - Use real LLM (test mode)

3. **Quality Tests** (4 hours)
   - Create gold standard Q&A set (50 AMC questions)
   - Human evaluation of answers
   - Measure accuracy, relevance, completeness
   - Document quality issues

**Success Criteria:**
- ✅ All tests passing (100%)
- ✅ Code coverage >80%
- ✅ Answer quality >90% (human evaluation)
- ✅ Performance within targets (<5s)

---

## Week 8: MCQ Generation Pipeline

### Monday-Tuesday: MCQ Generator Core (16 hours)

**Goal:** Generate AMC-style multiple choice questions automatically

```python
# File: src/generation/mcq_generator.py

class MCQGenerator:
    """
    Generate AMC-style MCQs with Australian guideline compliance

    AMC MCQ Format:
    - Single best answer (5 options: A, B, C, D, E)
    - Clinical scenario-based (patient presentation)
    - Australian context (medications, guidelines, healthcare system)
    - Evidence-based distractors (plausible wrong answers)
    - Detailed explanation with references
    """

    def generate_question(
        self,
        topic: str,
        specialty: str,
        difficulty: str = "medium"
    ) -> dict:
        """
        Generate a single MCQ question

        Args:
            topic: e.g., "acute coronary syndrome"
            specialty: e.g., "cardiology"
            difficulty: "easy" (ICRP level) | "medium" (AMC level) | "hard" (complex case)

        Returns:
            {
                "id": "uuid",
                "question_stem": "A 65-year-old man presents with...",
                "options": {
                    "A": "Aspirin 300mg immediately",
                    "B": "Ticagrelor 180mg loading dose",
                    "C": "Primary PCI within 90 minutes",
                    "D": "Thrombolysis with tenecteplase",
                    "E": "Observation and serial troponins"
                },
                "correct_answer": "C",
                "explanation": "Primary PCI is the gold standard...",
                "references": [
                    "Therapeutic Guidelines: Cardiovascular, p.123",
                    "ACS Guidelines 2024, p.45"
                ],
                "specialty": "cardiology",
                "difficulty": "medium",
                "amc_frequency": "high",  # How often this appears in AMC exams
                "created_at": "2026-01-17T10:00:00Z"
            }
        """
```

**Implementation Steps:**

1. **Generate Question Stem** (4 hours)
   ```python
   def generate_stem(self, topic: str, difficulty: str) -> str:
       """
       Create clinical scenario using RAG + LLM

       Components:
       - Patient demographics (age, gender, relevant history)
       - Presenting complaint
       - Relevant history (brief but key details)
       - Examination findings (if relevant)
       - Investigation results (if relevant)

       Example:
       "A 65-year-old man with a history of hypertension and hyperlipidaemia
       presents to the emergency department with 2 hours of crushing central
       chest pain radiating to the left arm. ECG shows ST elevation in leads
       II, III, and aVF. What is the most appropriate immediate management?"
       """
   ```

   - Use RAG to retrieve clinical scenarios from textbooks
   - Use LLM to adapt to Australian context
   - Ensure appropriate difficulty level
   - Test with 20 sample generations

2. **Generate Options** (6 hours)
   ```python
   def generate_options(self, stem: str, topic: str) -> dict:
       """
       Generate 5 plausible options (1 correct, 4 distractors)

       Distractor Types:
       - Common misconceptions
       - Outdated guidelines
       - Incorrect drug doses
       - Wrong sequence of management
       - Over/under-treatment

       Must follow Australian guidelines:
       - Use Australian medication names (not US brand names)
       - Follow eTG/TG dosing
       - Reflect Australian healthcare system
       """
   ```

   - Generate correct answer first (from guidelines)
   - Generate 4 plausible distractors
   - Ensure distractors are educational (common mistakes)
   - Validate all options are clinically reasonable

3. **Generate Explanation** (4 hours)
   ```python
   def generate_explanation(self, stem: str, options: dict, correct: str) -> str:
       """
       Create detailed explanation with citations

       Format:
       1. Why the correct answer is correct (guideline reference)
       2. Why each distractor is incorrect (brief)
       3. Key learning points
       4. Red flags or important considerations
       5. References (minimum 2)

       Must include:
       - Australian guideline citations
       - Page numbers
       - Publication year (recent)
       """
   ```

   - Use RAG to retrieve supporting evidence
   - Cite Australian guidelines primarily
   - Include 2-5 references minimum
   - Ensure educational value

4. **Validation & Quality Control** (2 hours)
   ```python
   def validate_question(self, question: dict) -> tuple[bool, List[str]]:
       """
       Check if question meets quality standards

       Checks:
       - Is question stem clear and unambiguous?
       - Are all 5 options grammatically parallel?
       - Is there one clear correct answer?
       - Are distractors plausible?
       - Are references included?
       - Is Australian context maintained?
       - Is difficulty appropriate?

       Returns:
           (is_valid, list_of_issues)
       """
   ```

**Success Criteria:**
- ✅ Generate 100 MCQs automatically
- ✅ Questions are clinically accurate (validated by QA-001)
- ✅ Australian guidelines followed (100%)
- ✅ Citations included (100%)
- ✅ Appropriate difficulty distribution

---

### Wednesday: Distractor Generation Refinement (8 hours)

**Goal:** Create high-quality, educational wrong answers

**Distractor Generation Strategies:**

1. **Common Misconceptions** (2 hours)
   - Collect common medical misconceptions
   - Generate options based on outdated practices
   - Example: "Give aspirin alone" (outdated ACS management)

2. **Dose/Timing Errors** (2 hours)
   - Generate incorrect medication doses
   - Incorrect timing (too early/late)
   - Example: "Aspirin 75mg" (wrong dose for ACS loading)

3. **Incomplete Management** (2 hours)
   - Missing key steps
   - Example: "ECG only" (missing troponins)

4. **Over-treatment** (2 hours)
   - Unnecessarily aggressive management
   - Example: "Immediate PCI for non-STEMI" (may not be indicated)

**Testing:**
- Generate 50 test questions
- Review distractor quality manually
- Ensure distractors are educational
- Target: 90%+ of distractors are "good" (neither too obvious nor too obscure)

---

### Thursday: Difficulty Calibration (8 hours)

**Goal:** Ensure questions match intended difficulty

**Difficulty Levels:**

1. **Easy (ICRP Level)** - 40% of questions
   - Straightforward clinical scenarios
   - Common presentations
   - Clear management pathways
   - Example: "What is first-line treatment for uncomplicated UTI?"

2. **Medium (AMC Level)** - 40% of questions
   - Typical presentations with minor complexities
   - Requires application of guidelines
   - May have 1-2 complicating factors
   - Example: "65-year-old with STEMI and renal impairment - dose adjustment needed"

3. **Hard (Complex Cases)** - 20% of questions
   - Rare presentations or complications
   - Multiple comorbidities
   - Requires synthesis of information
   - Example: "Pregnant woman with MI - management considerations"

**Calibration Process:**
1. Generate 30 questions (10 each difficulty)
2. Have medical expert rate actual difficulty
3. Adjust generation prompts based on feedback
4. Re-generate and re-test
5. Document difficulty indicators for future generation

---

### Friday: MCQ Generation Testing (8 hours)

**Task: Generate First 100 Questions**

```bash
# Generate questions across specialties
python src/generation/mcq_generator.py --specialty cardiology --count 20 --difficulty medium
python src/generation/mcq_generator.py --specialty respiratory --count 20 --difficulty medium
python src/generation/mcq_generator.py --specialty gastroenterology --count 20 --difficulty medium
python src/generation/mcq_generator.py --specialty endocrinology --count 20 --difficulty medium
python src/generation/mcq_generator.py --specialty neurology --count 20 --difficulty medium
```

**Quality Review:**
1. Automated validation (4 hours)
   - Run QA-001 agent on all 100 questions
   - Check citation accuracy (100%)
   - Check guideline compliance (100%)
   - Document issues found

2. Manual sample review (4 hours)
   - Manually review 20 questions (random sample)
   - Assess clinical accuracy
   - Check for ambiguity
   - Evaluate educational value
   - Document improvements needed

**Success Criteria:**
- ✅ 100 questions generated successfully
- ✅ 90%+ pass automated validation (QA-001)
- ✅ 80%+ deemed "good quality" in manual review
- ✅ All have proper Australian context
- ✅ All have citations with page numbers

---

## Week 9: OSCE Scenario Generation

### Goal: Generate AMC Clinical Exam OSCE stations

**AMC OSCE Format:**
- 16 stations (8 minutes each)
- Mix of history taking, examination, communication, emergency management
- Australian healthcare context essential
- Marking criteria provided

```python
# File: src/generation/osce_generator.py

class OSCEScenarioGenerator:
    """
    Generate AMC Clinical Exam OSCE scenarios

    Station Types:
    1. History Taking (35% of stations)
    2. Physical Examination (25% of stations)
    3. Communication Skills (20% of stations)
    4. Emergency Management (15% of stations)
    5. Procedural Skills (5% of stations)
    """

    def generate_station(
        self,
        station_type: str,
        specialty: str,
        difficulty: str = "amc"
    ) -> dict:
        """
        Generate a complete OSCE station

        Returns:
            {
                "station_number": 1,
                "station_type": "history_taking",
                "specialty": "cardiology",
                "time_limit": 8,  # minutes
                "candidate_instructions": "...",
                "actor_instructions": "...",
                "examiner_instructions": "...",
                "marking_criteria": {
                    "introduction": 1,
                    "presenting_complaint": 2,
                    "history_of_presenting_complaint": 3,
                    "red_flags_identified": 2,
                    "appropriate_questioning": 2,
                    "total": 10
                },
                "sample_answers": "...",
                "learning_points": [...],
                "references": [...]
            }
        """
```

**Implementation:** (32 hours total across Week 9)

1. **Monday: History Taking Stations** (8 hours)
   - Generate patient scenarios (chest pain, abdominal pain, headache, etc.)
   - Include relevant history elements
   - Add red flags to identify
   - Create marking rubrics

2. **Tuesday: Physical Examination Stations** (8 hours)
   - Generate examination scenarios (CVS, RS, abdominal, neuro)
   - Specify examination findings
   - Create systematic examination checklists
   - Include interpretation of findings

3. **Wednesday: Communication Stations** (8 hours)
   - Generate breaking bad news scenarios
   - Create difficult conversation scenarios (angry patient, cultural issues)
   - Include communication skills marking criteria
   - Add emotional response handling

4. **Thursday: Emergency Management** (8 hours)
   - Generate emergency scenarios (anaphylaxis, seizure, cardiac arrest)
   - Include time-critical decision making
   - Add escalation criteria
   - Create management algorithms

**Success Criteria:**
- ✅ 20 OSCE scenarios generated (5 per type)
- ✅ All include complete marking criteria
- ✅ Australian context maintained
- ✅ Appropriate difficulty for AMC Clinical Exam

---

## Week 10: QA System & Content Validation

### Monday-Wednesday: QA-001 Medical Validation Agent (24 hours)

**Goal:** Automated quality assurance for all generated content

```python
# File: src/agents/medical/qa001_medical_validator.py

class QA001MedicalValidator(BaseAgent):
    """
    Automated medical content quality assurance

    Validation Checks:
    1. Clinical Accuracy (guideline compliance)
    2. Citation Verification (all citations valid)
    3. Australian Context (medications, systems, guidelines)
    4. Question Quality (clear, unambiguous, appropriate difficulty)
    5. Educational Value (teaches important concepts)
    """

    async def validate_mcq(self, question: dict) -> ValidationResult:
        """
        Validate a single MCQ question

        Returns:
            ValidationResult(
                is_valid=True/False,
                confidence=0.95,
                issues=[
                    "Medication name should be 'ticagrelor' not 'brilinta' (Australian name)",
                    "Reference page number not found in source"
                ],
                suggestions=[...],
                guideline_compliance=True,
                australian_context=True
            )
        """
```

**Validation Pipeline:**

1. **Clinical Accuracy Check** (8 hours)
   - Verify correct answer matches guidelines
   - Check for clinical errors in stem/options
   - Validate medication doses against AMH
   - Ensure up-to-date guidelines (not outdated)

2. **Citation Verification** (8 hours)
   - Check all references exist
   - Verify page numbers are correct
   - Ensure Australian sources cited
   - Flag missing citations

3. **Australian Context Check** (4 hours)
   - Verify Australian medication names (not US brand names)
   - Check for Australian healthcare system references
   - Ensure PBS/MBS context where relevant
   - Validate AHPRA/RACGP standards

4. **Quality Metrics** (4 hours)
   - Question clarity score
   - Distractor quality score
   - Educational value score
   - Difficulty appropriateness

---

### Thursday: Generate First 500 Questions (8 hours)

**Automated Generation at Scale:**

```bash
# Generate 500 questions across all specialties
python scripts/generate_question_bank.py \
  --total 500 \
  --distribution specialty \
  --validate \
  --output data/questions/amc_question_bank_v1.json

# Distribution:
# Cardiology: 50
# Respiratory: 50
# GI: 50
# Endocrinology: 40
# Neurology: 40
# Emergency: 50
# ObGyn: 40
# Paediatrics: 50
# Psychiatry: 40
# General Practice: 50
# Other: 40
```

**Automated Quality Gates:**
- All questions run through QA-001
- Only questions passing validation are saved
- Failed questions logged for review
- Success rate target: 90%+ pass on first generation

**Success Criteria:**
- ✅ 500+ questions generated
- ✅ 90%+ pass QA-001 validation
- ✅ Even distribution across specialties
- ✅ Mix of difficulties (40% easy, 40% medium, 20% hard)
- ✅ 100% have Australian citations

---

### Friday: Manual Expert Review & Refinement (8 hours)

**Sample Review Process:**

1. **Random Sample Selection** (1 hour)
   - Select 50 questions randomly (10% of 500)
   - Stratify by specialty and difficulty
   - Ensure representative sample

2. **Medical Expert Review** (5 hours)
   - Review for clinical accuracy (100% must be correct)
   - Check for ambiguity (questions must be clear)
   - Assess educational value (must teach important concepts)
   - Verify Australian context (guidelines, medications, system)

3. **Quality Scoring** (1 hour)
   - Rate each question 1-5 stars
   - Document issues found
   - Calculate overall quality score
   - Target: Average 4.0/5.0 stars

4. **Refinement Strategy** (1 hour)
   - Analyze common issues
   - Update generation prompts
   - Improve distractor generation
   - Document lessons learned

**Success Criteria:**
- ✅ 50 questions reviewed by medical expert
- ✅ Average quality score >4.0/5.0
- ✅ <10% of questions require major revision
- ✅ All clinical inaccuracies identified and fixed

---

## Phase 3 Deliverables Checklist

### RAG System
- [ ] Production RAG query engine operational
- [ ] Response time <5 seconds (p95)
- [ ] Citation extraction working (100% accuracy)
- [ ] Australian guideline prioritization implemented
- [ ] Context window management optimized

### MCQ Generation
- [ ] MCQ generator pipeline fully automated
- [ ] 500+ questions generated across specialties
- [ ] Difficulty calibration working (easy/medium/hard)
- [ ] Distractor quality validated (90%+ educational)
- [ ] Australian context in all questions (100%)

### OSCE Generation
- [ ] OSCE scenario generator implemented
- [ ] 20 complete stations generated
- [ ] All station types covered (history, exam, communication, emergency)
- [ ] Marking criteria included for all stations
- [ ] AMC format compliance (8-minute stations)

### QA System
- [ ] QA-001 validation agent deployed
- [ ] Automated clinical accuracy checking
- [ ] Citation verification system working
- [ ] Australian context validation
- [ ] Quality metrics dashboard

### Quality Metrics
- [ ] 500+ validated questions in database
- [ ] 90%+ pass automated QA (QA-001)
- [ ] 80%+ deemed "good quality" in manual review
- [ ] 100% citation compliance
- [ ] 100% Australian guideline alignment

---

## Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Questions generated | 500+ | TBD | ⏳ |
| QA-001 pass rate | 90%+ | TBD | ⏳ |
| Manual review quality | 4.0/5.0 | TBD | ⏳ |
| Citation accuracy | 100% | TBD | ⏳ |
| RAG response time | <5s | TBD | ⏳ |
| Australian context | 100% | TBD | ⏳ |

---

## Next Phase: Phase 4 (Frontend MVP)

**Start Date:** Week 11
**Goal:** Build user interface to consume generated content
**Key Deliverable:** Interactive quiz platform

**See:** [phase4_frontend.md](phase4_frontend.md)

---

**Last Updated:** January 17, 2026
**Phase Owner:** AI-001 (RAG Architect) + MED-001 to MED-010 (Medical Experts)
**Status:** ⏳ NOT STARTED (awaiting Phase 1 completion + book acquisition)
**Next Review:** End of Week 10
