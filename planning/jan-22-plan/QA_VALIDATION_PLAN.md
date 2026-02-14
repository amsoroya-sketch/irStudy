# 100% Automated QA Validation Plan
**Zero Human Resources | RAG-Verified Citations | Version 1.0**

---

## Executive Summary

**Goal:** 100% automated quality assurance for all medical content with ZERO human intervention
**Core Principle:** Automation + RAG verification + Multi-tier validation = Consistent quality at scale
**Success Metric:** >90% auto-approval rate with <5% rejection rate

---

## 1. QA System Architecture

### 1.1 Current QA Agents (Operational)

**QA-001: Australian Standards Compliance** (223 LOC)
- ✅ Validates Australian terminology (paediatric not pediatric)
- ✅ Validates Australian drug names (paracetamol not acetaminophen)
- ✅ Validates Australian guidelines (eTG, AMH, PBS, AHPRA)
- ✅ Validates emergency protocols (000 not 911, MET call criteria)
- Status: Operational, no upgrade needed

**QA-002: Clinical Accuracy Validation** (240 LOC)
- ✅ Validates medication doses against AMH
- ✅ Validates clinical management against guidelines
- ✅ Checks for dangerous clinical errors
- ✅ Validates evidence-based recommendations
- Status: Operational, no upgrade needed

**QA-003: Citation Validator** (73 LOC) → **NEEDS MAJOR UPGRADE**
- ❌ Current: Basic citation presence checking only
- ❌ No RAG verification
- ❌ No confidence scoring
- ❌ No automated summary generation
- ❌ No page number verification
- Status: **REQUIRES UPGRADE TO 300+ LOC**

**QA-004: Format Validator** (115 LOC)
- ✅ Validates MCQ format (stem + 5 options)
- ✅ Validates OSCE format (8-minute stations)
- ✅ Validates markdown formatting
- ✅ Validates required fields present
- Status: Operational, no upgrade needed

### 1.2 New QA Architecture (Post-Upgrade)

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTENT GENERATION                            │
│   (MED-001 through MED-010 generate MCQs, OSCE, etc.)          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    QA VALIDATION PIPELINE                        │
│                    (4-Stage Sequential)                          │
└─────────────────────────────────────────────────────────────────┘
                         │
                         ├──► Stage 1: QA-001 (Australian Compliance)
                         │    ├─ PASS → Continue to Stage 2
                         │    └─ FAIL → Reject & Regenerate
                         │
                         ├──► Stage 2: QA-002 (Clinical Accuracy)
                         │    ├─ PASS → Continue to Stage 3
                         │    └─ FAIL → Reject & Regenerate
                         │
                         ├──► Stage 3: QA-003 (RAG Citation Verification) ⭐ NEW
                         │    ├─ Confidence >0.90 → Auto-Approve
                         │    ├─ Confidence 0.75-0.90 → LLM Verify (automated)
                         │    ├─ Confidence <0.75 → Reject & Regenerate
                         │    └─ Generate summary from citation
                         │
                         └──► Stage 4: QA-004 (Format Validation)
                              ├─ PASS → APPROVED CONTENT ✅
                              └─ FAIL → Reject & Regenerate

┌─────────────────────────────────────────────────────────────────┐
│                    APPROVED CONTENT DATABASE                     │
│    (Only content passing ALL 4 stages is stored)               │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. QA-003 Upgrade Specifications

### 2.1 Current State Analysis

**File:** `src/agents/qa_003_citation_validator.py`
**Current LOC:** 73 lines
**Current Functionality:**
```python
class QA003CitationValidator(BaseAgent):
    def validate_content(self, content: dict) -> ValidationResult:
        """
        Basic citation presence checking

        Checks:
        - Does content have a 'references' field?
        - Are there at least 1 reference listed?

        Does NOT check:
        - Citation accuracy (are claims actually in the cited source?)
        - Page number verification
        - Summary generation
        """
        has_references = 'references' in content and len(content['references']) > 0
        return ValidationResult(is_valid=has_references)
```

**Limitations:**
- ❌ No verification that citation actually supports the claim
- ❌ No page number checking
- ❌ No summary generation from citation
- ❌ No confidence scoring
- ❌ No RAG integration
- ❌ Can approve content with fake/incorrect citations

### 2.2 Target State Specification

**File:** `src/agents/qa_003_citation_validator.py`
**Target LOC:** 300+ lines
**Target Functionality:**

#### Component 1: RAG Integration (100 LOC)

```python
class QA003CitationValidator(BaseAgent):
    def __init__(self):
        super().__init__(agent_id="QA-003", name="Citation Validator", role=AgentRole.QA)
        self.qdrant_client = QdrantClient(url="http://localhost:6333")
        self.embedding_model = SentenceTransformer(
            'microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract-fulltext'
        )
        self.collection_name = "medical_knowledge"

    def verify_citation_with_rag(
        self,
        claim: str,
        citation: dict
    ) -> Tuple[float, List[dict]]:
        """
        Verify citation accuracy using RAG system

        Args:
            claim: Medical claim to verify
                   Example: "Primary PCI is the gold standard for STEMI management"
            citation: Citation information
                   Example: {
                       "source": "Therapeutic Guidelines: Cardiovascular",
                       "section": "5.2",
                       "page": 234
                   }

        Returns:
            (confidence_score, retrieved_chunks)
            confidence_score: 0.0-1.0 semantic similarity
            retrieved_chunks: Top 5 relevant chunks from RAG

        Process:
        1. Encode claim using PubMedBERT
        2. Query Qdrant with claim embedding
        3. Filter by source if specified in citation
        4. Retrieve top 5 most similar chunks
        5. Calculate confidence score (best match similarity)
        6. Verify page number if specified
        """
        # Step 1: Encode claim
        query_embedding = self.embedding_model.encode(claim).tolist()

        # Step 2: Build search filter
        search_filter = None
        if citation.get('source'):
            search_filter = Filter(
                must=[
                    FieldCondition(
                        key='source',
                        match=MatchValue(value=citation['source'])
                    )
                ]
            )

        # Step 3: Query Qdrant
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=5
        )

        # Step 4: Calculate confidence score
        if not results:
            return 0.0, []

        best_score = results[0].score

        # Step 5: Page number verification bonus
        if citation.get('page'):
            for result in results:
                if result.payload.get('page') == citation['page']:
                    # Boost confidence if page number matches
                    best_score = min(1.0, best_score + 0.05)
                    break

        # Step 6: Return confidence and chunks
        retrieved_chunks = [
            {
                'text': r.payload['text'],
                'source': r.payload['source'],
                'page': r.payload.get('page', 'N/A'),
                'score': r.score
            }
            for r in results
        ]

        return best_score, retrieved_chunks
```

#### Component 2: Confidence Scoring System (80 LOC)

```python
    def classify_confidence(
        self,
        confidence_score: float,
        claim: str,
        citation: dict,
        retrieved_chunks: List[dict]
    ) -> Tuple[str, str]:
        """
        Classify confidence level and determine action

        Args:
            confidence_score: RAG similarity score (0.0-1.0)
            claim: Original medical claim
            citation: Citation information
            retrieved_chunks: RAG retrieval results

        Returns:
            (decision, reason)
            decision: "AUTO_APPROVE" | "LLM_VERIFY" | "REJECT"
            reason: Human-readable explanation

        Confidence Tiers:
        - >0.90: AUTO-APPROVE (high confidence, no human needed)
        - 0.75-0.90: LLM-VERIFY (medium confidence, needs LLM check)
        - <0.75: REJECT (low confidence, regenerate content)
        """
        if confidence_score >= 0.90:
            return (
                "AUTO_APPROVE",
                f"High confidence ({confidence_score:.2f}). "
                f"Claim verified in {citation['source']} with strong semantic match."
            )

        elif confidence_score >= 0.75:
            return (
                "LLM_VERIFY",
                f"Medium confidence ({confidence_score:.2f}). "
                f"Requires LLM verification to confirm claim accuracy."
            )

        else:
            return (
                "REJECT",
                f"Low confidence ({confidence_score:.2f}). "
                f"Claim not found in cited source. Content must be regenerated."
            )

    async def llm_verify_citation(
        self,
        claim: str,
        citation: dict,
        retrieved_chunks: List[dict]
    ) -> bool:
        """
        Use LLM to verify citation when RAG confidence is medium (0.75-0.90)

        Args:
            claim: Medical claim
            citation: Citation info
            retrieved_chunks: Top RAG results

        Returns:
            True if LLM confirms citation supports claim
            False if LLM determines citation does not support claim

        Process:
        1. Build prompt with claim and retrieved context
        2. Ask Claude to verify if context supports claim
        3. Parse LLM response (YES/NO)
        4. Return decision

        Note: This is still 100% automated (no human)
        """
        # Build verification prompt
        context = "\n\n".join([
            f"[Chunk {i+1}] {chunk['text'][:500]}..."
            for i, chunk in enumerate(retrieved_chunks[:3])
        ])

        prompt = f"""You are verifying medical citation accuracy.

CLAIM: "{claim}"

CITED SOURCE: {citation['source']}
{f"Page: {citation['page']}" if citation.get('page') else ""}

RETRIEVED CONTEXT FROM SOURCE:
{context}

QUESTION: Does the retrieved context support the claim?

Answer with ONLY "YES" or "NO" followed by a brief reason (one sentence).

Format: YES/NO | Reason"""

        # Call Claude for verification (100% automated)
        response = await self.llm_client.generate(
            prompt=prompt,
            temperature=0.1,  # Low temperature for consistent decisions
            max_tokens=100
        )

        # Parse response
        decision = response.strip().split('|')[0].strip().upper()
        return decision == "YES"
```

#### Component 3: Automated Summary Generation (60 LOC)

```python
    def generate_summary_from_citation(
        self,
        concept: str,
        citation: dict,
        confidence_score: float
    ) -> str:
        """
        Generate 2-3 sentence summary from cited source using RAG

        Required by jan22-review/instructions.txt:
        "For all mcq there should be link or citation as well as
        summary from citation for the correct answer"

        Args:
            concept: Medical concept (e.g., "STEMI management")
            citation: Citation with source and page
            confidence_score: RAG confidence (must be >0.75)

        Returns:
            summary: 2-3 sentences extracted from source

        Process:
        1. Query RAG with concept
        2. Filter by cited source and page
        3. Extract most relevant chunk
        4. Extract 2-3 key sentences
        5. Return summary with inline citation
        """
        if confidence_score < 0.75:
            return "[ERROR: Cannot generate summary - citation confidence too low]"

        # Query RAG for concept
        query_embedding = self.embedding_model.encode(concept).tolist()

        # Filter by source and page
        search_filter = Filter(
            must=[
                FieldCondition(key='source', match=MatchValue(value=citation['source']))
            ]
        )

        if citation.get('page'):
            search_filter.must.append(
                FieldCondition(key='page', match=MatchValue(value=citation['page']))
            )

        # Retrieve best chunk
        results = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            query_filter=search_filter,
            limit=1
        )

        if not results:
            return f"[ERROR: Content not found in {citation['source']}]"

        # Extract chunk text
        chunk_text = results[0].payload['text']

        # Extract 2-3 key sentences
        sentences = self._split_sentences(chunk_text)
        summary_sentences = sentences[:3]  # Take first 3 sentences
        summary = " ".join(summary_sentences)

        # Add inline citation
        page_ref = f", p. {citation['page']}" if citation.get('page') else ""
        summary_with_citation = f"According to {citation['source']}{page_ref}: {summary}"

        return summary_with_citation

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences (simple implementation)"""
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]
```

#### Component 4: Image Validation (60 LOC)

```python
    def validate_images(self, content: dict) -> ValidationResult:
        """
        Validate images in content

        Requirements from jan22-review/instructions.txt:
        "Include pictures from the source in the included books or material
        as well, if possible, find picture from internet and then include."

        Checks:
        1. Does content reference visual concepts (ECG, CXR, rash, etc.)?
        2. If yes, is image included?
        3. If image included, does it have proper citation?

        Process:
        - Scan content text for visual keywords
        - Check if 'images' field exists and populated
        - Validate image citations (figure number, page, source)
        - Flag for manual image addition if needed

        Returns:
            ValidationResult with image validation status
        """
        visual_keywords = [
            'ECG', 'EKG', 'chest X-ray', 'CXR', 'CT scan',
            'MRI', 'ultrasound', 'rash', 'lesion', 'fundoscopy',
            'dermatology', 'skin finding', 'photograph', 'image shows',
            'figure', 'illustration', 'diagram'
        ]

        content_text = self._extract_text(content)

        # Check if visual content is referenced
        has_visual_reference = any(
            keyword.lower() in content_text.lower()
            for keyword in visual_keywords
        )

        if not has_visual_reference:
            return ValidationResult(
                is_valid=True,
                warnings=["No visual content referenced - image not required"]
            )

        # Visual content referenced - check if image included
        has_images = 'images' in content and len(content['images']) > 0

        if not has_images:
            return ValidationResult(
                is_valid=False,
                issues=["Visual content referenced but no image included"],
                suggestions=[
                    "Add image from source material",
                    "Or find appropriate image from internet",
                    "Include proper citation (figure number, page, source)"
                ]
            )

        # Validate image citations
        for idx, image in enumerate(content['images']):
            if not image.get('citation'):
                return ValidationResult(
                    is_valid=False,
                    issues=[f"Image {idx+1} missing citation"]
                )

        return ValidationResult(is_valid=True)
```

#### Component 5: Main Validation Pipeline (100 LOC)

```python
    async def validate_content(self, content: dict) -> ValidationResult:
        """
        Main validation pipeline for QA-003

        Process:
        1. Extract all claims and citations from content
        2. For each claim-citation pair:
           a. Verify with RAG
           b. Calculate confidence score
           c. Classify confidence tier
           d. Take action (approve/verify/reject)
        3. Generate summaries for all citations
        4. Validate images
        5. Return comprehensive validation result

        Args:
            content: MCQ, OSCE, or other medical content

        Returns:
            ValidationResult with:
            - is_valid: bool
            - confidence: float (average across all citations)
            - issues: List[str]
            - warnings: List[str]
            - suggestions: List[str]
            - summaries_generated: dict
            - statistics: dict
        """
        validation_results = []
        summaries_generated = {}
        statistics = {
            'total_citations': 0,
            'auto_approved': 0,
            'llm_verified': 0,
            'rejected': 0,
            'average_confidence': 0.0
        }

        # Step 1: Extract claims and citations
        claim_citation_pairs = self._extract_claims_and_citations(content)
        statistics['total_citations'] = len(claim_citation_pairs)

        if not claim_citation_pairs:
            return ValidationResult(
                is_valid=False,
                issues=["No citations found in content"],
                suggestions=["Add minimum 2 citations with sources and page numbers"]
            )

        # Step 2: Validate each citation
        confidence_scores = []

        for claim, citation in claim_citation_pairs:
            # Verify with RAG
            confidence, chunks = self.verify_citation_with_rag(claim, citation)
            confidence_scores.append(confidence)

            # Classify confidence
            decision, reason = self.classify_confidence(
                confidence, claim, citation, chunks
            )

            # Take action based on decision
            if decision == "AUTO_APPROVE":
                statistics['auto_approved'] += 1
                validation_results.append({
                    'claim': claim,
                    'citation': citation,
                    'decision': 'APPROVED',
                    'confidence': confidence,
                    'reason': reason
                })

            elif decision == "LLM_VERIFY":
                # Automated LLM verification (no human)
                llm_approved = await self.llm_verify_citation(claim, citation, chunks)

                if llm_approved:
                    statistics['llm_verified'] += 1
                    validation_results.append({
                        'claim': claim,
                        'citation': citation,
                        'decision': 'APPROVED (LLM)',
                        'confidence': confidence,
                        'reason': f"LLM confirmed citation accuracy ({confidence:.2f})"
                    })
                else:
                    statistics['rejected'] += 1
                    return ValidationResult(
                        is_valid=False,
                        confidence=confidence,
                        issues=[f"LLM verification failed for claim: '{claim[:50]}...'"],
                        suggestions=["Regenerate content with accurate citations"]
                    )

            else:  # REJECT
                statistics['rejected'] += 1
                return ValidationResult(
                    is_valid=False,
                    confidence=confidence,
                    issues=[f"Low confidence ({confidence:.2f}) for claim: '{claim[:50]}...'"],
                    suggestions=["Regenerate content with citations from RAG-verified sources"]
                )

        # Step 3: Generate summaries for all approved citations
        for claim, citation in claim_citation_pairs:
            concept = self._extract_concept(claim)
            summary = self.generate_summary_from_citation(
                concept,
                citation,
                max(confidence_scores)  # Use best confidence
            )
            summaries_generated[concept] = summary

        # Step 4: Validate images
        image_validation = self.validate_images(content)
        if not image_validation.is_valid:
            return image_validation  # Return image validation failure

        # Step 5: Calculate statistics
        statistics['average_confidence'] = sum(confidence_scores) / len(confidence_scores)

        # Step 6: Return comprehensive result
        return ValidationResult(
            is_valid=True,
            confidence=statistics['average_confidence'],
            issues=[],
            warnings=image_validation.warnings if image_validation.warnings else [],
            suggestions=[],
            summaries_generated=summaries_generated,
            statistics=statistics,
            details=validation_results
        )

    def _extract_claims_and_citations(self, content: dict) -> List[Tuple[str, dict]]:
        """Extract all claim-citation pairs from content"""
        # Implementation depends on content structure
        # For MCQs: extract from explanation + references
        # For OSCE: extract from marking criteria + references
        pass

    def _extract_concept(self, claim: str) -> str:
        """Extract main medical concept from claim"""
        # Simple implementation: use first 5 words
        words = claim.split()[:5]
        return " ".join(words)

    def _extract_text(self, content: dict) -> str:
        """Extract all text from content for keyword scanning"""
        texts = []
        if 'question_stem' in content:
            texts.append(content['question_stem'])
        if 'explanation' in content:
            texts.append(content['explanation'])
        if 'scenario' in content:
            texts.append(content['scenario'])
        return " ".join(texts)
```

---

## 3. Automated QA Pipeline Flow

### 3.1 Content Generation → QA Pipeline

```python
# Example: MCQ Generation with QA Validation

async def generate_and_validate_mcq(
    agent: MedicalExpertAgent,
    topic: str,
    specialty: str
) -> dict:
    """
    Generate MCQ and validate through 4-stage QA pipeline

    Returns:
        Approved MCQ content or None if validation fails
    """
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        attempt += 1

        # Generate content
        mcq = await agent.generate_mcq(topic, specialty)

        # Stage 1: QA-001 (Australian Compliance)
        qa001_result = await qa001_agent.validate_content(mcq)
        if not qa001_result.is_valid:
            logger.info(f"QA-001 FAIL (attempt {attempt}): {qa001_result.issues}")
            continue  # Regenerate

        # Stage 2: QA-002 (Clinical Accuracy)
        qa002_result = await qa002_agent.validate_content(mcq)
        if not qa002_result.is_valid:
            logger.info(f"QA-002 FAIL (attempt {attempt}): {qa002_result.issues}")
            continue  # Regenerate

        # Stage 3: QA-003 (RAG Citation Verification) ⭐ NEW
        qa003_result = await qa003_agent.validate_content(mcq)
        if not qa003_result.is_valid:
            logger.info(f"QA-003 FAIL (attempt {attempt}): {qa003_result.issues}")
            continue  # Regenerate

        # Add summaries to MCQ (from QA-003)
        mcq['citation_summaries'] = qa003_result.summaries_generated

        # Stage 4: QA-004 (Format Validation)
        qa004_result = await qa004_agent.validate_content(mcq)
        if not qa004_result.is_valid:
            logger.info(f"QA-004 FAIL (attempt {attempt}): {qa004_result.issues}")
            continue  # Regenerate

        # ALL STAGES PASSED
        logger.info(f"QA PASS (attempt {attempt}): {mcq['id']}")
        logger.info(f"  Confidence: {qa003_result.confidence:.2f}")
        logger.info(f"  Auto-approved: {qa003_result.statistics['auto_approved']}")
        logger.info(f"  LLM-verified: {qa003_result.statistics['llm_verified']}")

        return mcq

    # Failed after 3 attempts
    logger.error(f"QA FAIL: Could not generate valid MCQ after {max_attempts} attempts")
    return None
```

### 3.2 Success Metrics

**Target Metrics:**
- **Auto-Approval Rate:** >90% (citations pass with confidence >0.90)
- **LLM Verification Rate:** 5-10% (citations need LLM check at 0.75-0.90)
- **Rejection Rate:** <5% (citations fail with confidence <0.75)
- **First-Pass Success:** >85% (content passes all 4 stages on first attempt)
- **Max Attempts:** 3 (if fails 3 times, flag for review of generation prompts)

---

## 4. Testing & Validation

### 4.1 Unit Testing (Week 1)

**Test File:** `tests/agents/test_qa_003_upgraded.py`

```python
import pytest
from src.agents.qa_003_citation_validator import QA003CitationValidator

class TestQA003Upgraded:
    """Unit tests for upgraded QA-003 agent"""

    @pytest.fixture
    def qa003_agent(self):
        return QA003CitationValidator()

    def test_high_confidence_auto_approve(self, qa003_agent):
        """Test auto-approval for high confidence citations"""
        claim = "Primary PCI is the gold standard for STEMI management within 90 minutes"
        citation = {
            "source": "Therapeutic Guidelines: Cardiovascular",
            "section": "5.2",
            "page": 234
        }

        confidence, chunks = qa003_agent.verify_citation_with_rag(claim, citation)

        assert confidence >= 0.90, f"Expected high confidence, got {confidence}"
        assert len(chunks) > 0, "Expected retrieved chunks"

        decision, reason = qa003_agent.classify_confidence(
            confidence, claim, citation, chunks
        )

        assert decision == "AUTO_APPROVE"

    def test_medium_confidence_llm_verify(self, qa003_agent):
        """Test LLM verification for medium confidence citations"""
        claim = "Beta blockers are used in heart failure management"
        citation = {
            "source": "Therapeutic Guidelines: Cardiovascular",
            "page": 180
        }

        confidence, chunks = qa003_agent.verify_citation_with_rag(claim, citation)

        assert 0.75 <= confidence < 0.90, f"Expected medium confidence, got {confidence}"

        decision, reason = qa003_agent.classify_confidence(
            confidence, claim, citation, chunks
        )

        assert decision == "LLM_VERIFY"

    def test_low_confidence_reject(self, qa003_agent):
        """Test rejection for low confidence citations"""
        claim = "Homeopathy is effective for treating diabetes"
        citation = {
            "source": "Therapeutic Guidelines: Cardiovascular",  # Wrong source
            "page": 999  # Non-existent page
        }

        confidence, chunks = qa003_agent.verify_citation_with_rag(claim, citation)

        assert confidence < 0.75, f"Expected low confidence, got {confidence}"

        decision, reason = qa003_agent.classify_confidence(
            confidence, claim, citation, chunks
        )

        assert decision == "REJECT"

    def test_summary_generation(self, qa003_agent):
        """Test automated summary generation from citations"""
        concept = "STEMI management"
        citation = {
            "source": "Therapeutic Guidelines: Cardiovascular",
            "page": 234
        }
        confidence = 0.95

        summary = qa003_agent.generate_summary_from_citation(
            concept, citation, confidence
        )

        assert len(summary) > 50, "Summary too short"
        assert citation['source'] in summary, "Summary missing source citation"
        assert "According to" in summary, "Summary missing attribution"

    def test_image_validation_required(self, qa003_agent):
        """Test image validation when visual content referenced"""
        content = {
            "question_stem": "The ECG shows ST elevation in leads II, III, aVF...",
            "explanation": "The ECG demonstrates inferior STEMI...",
            "references": ["eTG Cardiovascular"]
            # No images field
        }

        result = qa003_agent.validate_images(content)

        assert not result.is_valid, "Should fail - visual content without image"
        assert "no image included" in result.issues[0].lower()

    def test_image_validation_pass(self, qa003_agent):
        """Test image validation when image properly included"""
        content = {
            "question_stem": "The ECG shows ST elevation in leads II, III, aVF...",
            "images": [
                {
                    "file": "inferior_stemi_ecg.png",
                    "citation": "ECG Made Easy, 8th Ed, Figure 12.3, p. 145"
                }
            ]
        }

        result = qa003_agent.validate_images(content)

        assert result.is_valid, "Should pass - visual content with proper image"
```

### 4.2 Integration Testing (Week 2)

**Test File:** `tests/integration/test_qa_pipeline.py`

```python
import pytest
from src.agents.medical.med_001_cardiology import MED001Cardiology
from src.agents.qa_001_australian_compliance import QA001AustralianCompliance
from src.agents.qa_002_clinical_accuracy import QA002ClinicalAccuracy
from src.agents.qa_003_citation_validator import QA003CitationValidator
from src.agents.qa_004_format_validator import QA004FormatValidator

class TestQAPipeline:
    """Integration tests for full QA pipeline"""

    @pytest.fixture
    async def qa_pipeline(self):
        return {
            'qa001': QA001AustralianCompliance(),
            'qa002': QA002ClinicalAccuracy(),
            'qa003': QA003CitationValidator(),
            'qa004': QA004FormatValidator()
        }

    @pytest.fixture
    async def med001_agent(self):
        return MED001Cardiology()

    @pytest.mark.asyncio
    async def test_full_pipeline_pass(self, med001_agent, qa_pipeline):
        """Test MCQ generation passing all 4 QA stages"""
        # Generate MCQ
        mcq = await med001_agent.generate_mcq(
            topic="acute coronary syndrome",
            difficulty="medium"
        )

        # Stage 1: Australian compliance
        qa001_result = await qa_pipeline['qa001'].validate_content(mcq)
        assert qa001_result.is_valid, f"QA-001 failed: {qa001_result.issues}"

        # Stage 2: Clinical accuracy
        qa002_result = await qa_pipeline['qa002'].validate_content(mcq)
        assert qa002_result.is_valid, f"QA-002 failed: {qa002_result.issues}"

        # Stage 3: Citation verification (RAG)
        qa003_result = await qa_pipeline['qa003'].validate_content(mcq)
        assert qa003_result.is_valid, f"QA-003 failed: {qa003_result.issues}"
        assert qa003_result.confidence >= 0.75, "Confidence too low"
        assert len(qa003_result.summaries_generated) > 0, "No summaries generated"

        # Stage 4: Format validation
        qa004_result = await qa_pipeline['qa004'].validate_content(mcq)
        assert qa004_result.is_valid, f"QA-004 failed: {qa004_result.issues}"

        # Verify final MCQ has summaries
        assert 'citation_summaries' in mcq or qa003_result.summaries_generated

    @pytest.mark.asyncio
    async def test_pipeline_rejection_and_retry(self, med001_agent, qa_pipeline):
        """Test pipeline rejection triggers regeneration"""
        max_attempts = 3
        attempts = 0
        passed = False

        while attempts < max_attempts and not passed:
            attempts += 1

            # Generate MCQ
            mcq = await med001_agent.generate_mcq(
                topic="hypertension management",
                difficulty="easy"
            )

            # Run through pipeline
            try:
                # All 4 stages
                qa001_result = await qa_pipeline['qa001'].validate_content(mcq)
                if not qa001_result.is_valid:
                    continue

                qa002_result = await qa_pipeline['qa002'].validate_content(mcq)
                if not qa002_result.is_valid:
                    continue

                qa003_result = await qa_pipeline['qa003'].validate_content(mcq)
                if not qa003_result.is_valid:
                    continue

                qa004_result = await qa_pipeline['qa004'].validate_content(mcq)
                if not qa004_result.is_valid:
                    continue

                # All stages passed
                passed = True

            except Exception as e:
                print(f"Attempt {attempts} failed with exception: {e}")
                continue

        assert passed, f"Failed to generate valid MCQ after {max_attempts} attempts"
        assert attempts <= 2, "Should pass within 2 attempts typically"
```

### 4.3 Performance Testing (Week 2)

```python
import pytest
import time
from src.agents.qa_003_citation_validator import QA003CitationValidator

class TestQA003Performance:
    """Performance tests for QA-003"""

    def test_rag_query_latency(self):
        """Test RAG query response time"""
        qa003 = QA003CitationValidator()

        claim = "Aspirin is used in acute coronary syndrome"
        citation = {"source": "Therapeutic Guidelines: Cardiovascular"}

        start = time.time()
        confidence, chunks = qa003.verify_citation_with_rag(claim, citation)
        elapsed = time.time() - start

        assert elapsed < 0.5, f"RAG query too slow: {elapsed:.2f}s (target <0.5s)"

    def test_full_validation_latency(self):
        """Test full validation pipeline latency"""
        qa003 = QA003CitationValidator()

        mcq = {
            "question_stem": "A 65-year-old man presents with chest pain...",
            "options": {"A": "...", "B": "...", "C": "...", "D": "...", "E": "..."},
            "correct_answer": "C",
            "explanation": "Primary PCI is the gold standard for STEMI...",
            "references": [
                {
                    "source": "Therapeutic Guidelines: Cardiovascular",
                    "page": 234,
                    "claim": "Primary PCI is gold standard for STEMI"
                }
            ]
        }

        start = time.time()
        result = qa003.validate_content(mcq)
        elapsed = time.time() - start

        assert elapsed < 2.0, f"Validation too slow: {elapsed:.2f}s (target <2s)"

    def test_batch_validation_throughput(self):
        """Test batch validation throughput"""
        qa003 = QA003CitationValidator()

        # Create 100 test MCQs
        mcqs = [create_test_mcq(i) for i in range(100)]

        start = time.time()
        results = [qa003.validate_content(mcq) for mcq in mcqs]
        elapsed = time.time() - start

        throughput = len(mcqs) / elapsed

        assert throughput >= 10, f"Throughput too low: {throughput:.1f} MCQs/sec (target >=10)"
```

---

## 5. Implementation Timeline

### Week 1: Core Development
- **Day 1-2:** RAG integration implementation (100 LOC)
- **Day 3-4:** Confidence scoring system (80 LOC)
- **Day 5:** Automated summary generation (60 LOC)

### Week 2: Extended Features + Testing
- **Day 1-2:** Image validation (60 LOC)
- **Day 3:** Main validation pipeline (100 LOC)
- **Day 4:** Unit testing (20+ tests)
- **Day 5:** Integration testing + performance testing

### Week 1-2 Deliverables:
- ✅ QA-003 upgraded from 73 LOC → 300+ LOC
- ✅ RAG integration operational
- ✅ Confidence scoring system validated
- ✅ Automated summary generation working
- ✅ 100% automation confirmed (no human resources)
- ✅ Test coverage >80%
- ✅ Performance targets met (<2s per validation)

---

## 6. Monitoring & Statistics

### 6.1 Real-Time Monitoring Dashboard

```python
class QAStatisticsTracker:
    """Track QA-003 performance in real-time"""

    def __init__(self):
        self.stats = {
            'total_validations': 0,
            'auto_approved': 0,
            'llm_verified': 0,
            'rejected': 0,
            'average_confidence': [],
            'validation_times': [],
            'summaries_generated': 0
        }

    def record_validation(self, result: ValidationResult, elapsed_time: float):
        """Record validation result"""
        self.stats['total_validations'] += 1

        if result.is_valid:
            if result.statistics['auto_approved'] > 0:
                self.stats['auto_approved'] += result.statistics['auto_approved']
            if result.statistics['llm_verified'] > 0:
                self.stats['llm_verified'] += result.statistics['llm_verified']
        else:
            self.stats['rejected'] += 1

        self.stats['average_confidence'].append(result.confidence)
        self.stats['validation_times'].append(elapsed_time)
        self.stats['summaries_generated'] += len(result.summaries_generated)

    def get_summary(self) -> dict:
        """Get statistics summary"""
        total = self.stats['total_validations']
        if total == 0:
            return {}

        return {
            'total_validations': total,
            'auto_approval_rate': self.stats['auto_approved'] / total * 100,
            'llm_verification_rate': self.stats['llm_verified'] / total * 100,
            'rejection_rate': self.stats['rejected'] / total * 100,
            'average_confidence': sum(self.stats['average_confidence']) / len(self.stats['average_confidence']),
            'average_validation_time': sum(self.stats['validation_times']) / len(self.stats['validation_times']),
            'total_summaries_generated': self.stats['summaries_generated']
        }
```

### 6.2 Weekly Automated Reports

**Report Generated:** Every Friday at 5pm

```
========================================
QA-003 WEEKLY PERFORMANCE REPORT
Week 1: 2026-01-24 to 2026-01-31
========================================

VALIDATION STATISTICS:
- Total Validations: 1,247
- Auto-Approved: 1,123 (90.1%) ✅ TARGET MET
- LLM-Verified: 89 (7.1%)
- Rejected: 35 (2.8%) ✅ TARGET MET

CONFIDENCE SCORES:
- Average Confidence: 0.93 ✅ EXCELLENT
- Min Confidence: 0.67
- Max Confidence: 0.99
- Std Deviation: 0.08

PERFORMANCE:
- Average Validation Time: 1.2s ✅ TARGET MET
- Max Validation Time: 3.8s
- Throughput: 15 validations/sec ✅ TARGET MET

SUMMARIES GENERATED:
- Total Summaries: 2,494 (avg 2 per MCQ)
- Summary Generation Success: 100%

ISSUES DETECTED:
- Low confidence (<0.75): 35 cases
- Missing page numbers: 12 cases
- Image validation failures: 8 cases

ACTIONS TAKEN:
- 35 content items regenerated automatically
- 8 items flagged for image addition
- Prompts refined based on common issues

========================================
STATUS: ✅ ALL TARGETS MET
RECOMMENDATION: Continue current configuration
========================================
```

---

## 7. Success Criteria Checklist

### Implementation Checklist

- [ ] QA-003 upgraded from 73 LOC → 300+ LOC
- [ ] RAG integration implemented (Qdrant + PubMedBERT)
- [ ] Confidence scoring system operational (>0.90, 0.75-0.90, <0.75)
- [ ] Automated LLM verification implemented (Claude API)
- [ ] Summary generation from citations working
- [ ] Image validation implemented
- [ ] Main validation pipeline integrated
- [ ] Unit tests written (>20 tests, >80% coverage)
- [ ] Integration tests passing (full 4-stage pipeline)
- [ ] Performance tests passing (<2s validation, >10 MCQ/sec throughput)

### Operational Checklist

- [ ] 100% automation confirmed (zero human intervention required)
- [ ] Auto-approval rate >90% achieved
- [ ] Rejection rate <5% achieved
- [ ] Average confidence >0.90 achieved
- [ ] Validation latency <2s achieved
- [ ] Summaries generated for 100% of approved content
- [ ] Statistics tracking operational
- [ ] Weekly automated reports generating
- [ ] Error handling and regeneration working
- [ ] Integration with all 4 QA agents tested

### Quality Checklist

- [ ] Citations verified against RAG (42,647 vectors)
- [ ] Page numbers validated where specified
- [ ] Summaries extracted from actual source text
- [ ] Australian compliance maintained (QA-001)
- [ ] Clinical accuracy maintained (QA-002)
- [ ] Format validation maintained (QA-004)
- [ ] No false positives (high confidence but incorrect citations)
- [ ] No false negatives (correct citations rejected)
- [ ] Consistent decisions across similar content
- [ ] Scalable to 5,000+ MCQs without degradation

---

## 8. Next Steps

### Immediate (Week 1)
1. Begin QA-003 upgrade implementation (Day 1)
2. Implement RAG integration (Day 1-2)
3. Implement confidence scoring (Day 3-4)
4. Implement summary generation (Day 5)

### Week 2
1. Implement image validation (Day 1-2)
2. Integrate main pipeline (Day 3)
3. Write comprehensive tests (Day 4)
4. Performance validation (Day 5)

### Week 3+
1. Deploy upgraded QA-003 to production
2. Monitor statistics daily
3. Generate first weekly report
4. Refine based on real-world performance
5. Scale to handle 5,000+ MCQ validation

---

**Last Updated:** 2026-01-24
**Status:** 📝 PLANNING COMPLETE - READY FOR IMPLEMENTATION
**Next Action:** Begin QA-003 upgrade implementation (Week 1, Day 1)
**Owner:** QA Team + RAG System Integration Team
