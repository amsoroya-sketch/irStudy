# RAG Citation Requirements

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)

---

## 11. RAG Citation Requirements

### CONTEXT: Week 1 Critical Mistake (2026-01-22)

**Issue**: Generated 100 MCQs + 5 OSCEs with 212/212 citations showing `"title": "Unknown"`

**Root Cause**: Qdrant database missing bibliographic metadata (title, author, year, edition)
- Metadata was extracted during PDF processing
- But LOST during chunking phase (not propagated to chunks)
- Never indexed to Qdrant database
- RAG returned chunks with no bibliographic information

**Impact**: All Week 1 content citations were invalid, violating QA-003 standards

**Prevention**: This constraint file documents MANDATORY validation requirements to prevent recurrence

---

## 11.1 Mandatory Metadata Fields (ZERO TOLERANCE)

**ALL chunks indexed to Qdrant MUST contain complete bibliographic metadata:**

```python
# ✅ REQUIRED - Every chunk must have these fields
chunk_metadata = {
    'title': str,          # Book/article title (NOT "Unknown")
    'author': str,         # Primary author or "Unknown Author" (acceptable for 16% of books)
    'year': str,           # Publication year (1990-2026)
    'edition': str,        # Edition (e.g., "7th", "2nd", or "" for articles)
    'source': str,         # Source file name
    'page': int,           # Page number (must be >0)
    'chunk_id': str,       # Unique identifier
    'text': str            # Chunk text content
}
```

**Reference Files**:
- `/home/dev/Development/irStudy/scripts/chunk_medical_texts.py` (lines 130-134, 148-152, 163-166, 189-192)
- `/home/dev/Development/irStudy/scripts/index_qdrant.py` (lines 79-83)

### Validation Criteria (100% Compliance Required)

| Field | Requirement | Acceptable | Unacceptable |
|-------|------------|------------|--------------|
| `title` | Not "Unknown", not empty | Valid book/article title | "Unknown", "", null |
| `author` | Not "Unknown" (preferred) | "Unknown Author" (16% books OK) | "", null |
| `year` | 1990-2026 range | "2020", "2023" | "Unknown", "", <1990, >2026 |
| `edition` | Valid or empty | "7th", "2nd", "" | "Unknown", invalid format |
| `page` | Integer >0 | 1, 42, 1234 | 0, -1, null, "N/A" |

**Critical**: `title` MUST NEVER be "Unknown". This is the primary citation field.

---

## 11.2 Pre-Flight Validation Checklist (MANDATORY)

**BEFORE generating ANY MCQs or OSCEs, run the pre-flight validation:**

```bash
# MANDATORY: Run this before ANY content generation
./scripts/pre_flight_validation.sh
```

**Validation Script**: `/home/dev/Development/irStudy/scripts/pre_flight_validation.sh`

**What it checks:**

### Check 1: Qdrant Service Health
```bash
# Verifies Qdrant is running and accessible
curl -s http://localhost:6333/health
# EXIT CODE 1 = Service down (DO NOT PROCEED)
```

### Check 2: RAG Database Metadata Completeness
```bash
# Validates 1,000 random chunks for metadata compliance
python scripts/validate_rag_database_metadata.py \
    --collection medical_knowledge \
    --sample-size 1000

# PASS CRITERIA (100% compliance):
#   ✓ 0% chunks with title == "Unknown"
#   ✓ 0% chunks with invalid year (<1990 or >2026)
#   ✓ 0% chunks with invalid page (<=0)
# NOTE: "Unknown Author" is WARNING only (16% acceptable)
```

### Check 3: RAG Citation Quality
```bash
# Tests RAG with 20 real medical queries
python scripts/test_rag_citation_quality.py \
    --queries 20 \
    --min-confidence 0.65

# PASS CRITERIA:
#   ✓ ≥80% queries return valid citations
#   ✓ Average confidence ≥0.65
```

### Check 4: Collection Size Check
```bash
# Verifies sufficient data points
# GOOD: ≥5,000 points
# ACCEPTABLE: 1,000-5,000 points
# WARNING: <1,000 points
```

**EXIT CODES**:
- `0` = All checks passed (SAFE to proceed with generation)
- `1` = Validation failed (DO NOT PROCEED - fix issues first)

---

## 11.3 Data Pipeline Quality Gates

**Metadata must propagate through EVERY stage of the pipeline:**

```
PDF Extraction → Chunking → Embedding → Qdrant Indexing → RAG Retrieval
   ↓               ↓           ↓            ↓                ↓
metadata      metadata    metadata     metadata         metadata
preserved     propagated  preserved    indexed          returned
```

### Stage 1: PDF Extraction (`scripts/extract_pdfs.py`)

**MUST extract:**
```python
book_data = {
    'title': extract_title(pdf_path),      # From filename or PDF metadata
    'author': extract_author(pdf_path),    # From filename or PDF metadata
    'year': extract_year(pdf_path),        # From filename (4-digit)
    'edition': extract_edition(pdf_path),  # From filename (e.g., "7th")
    'source': pdf_path.name,
    'pages': extract_pages(pdf)
}
```

**Reference**: `/home/dev/Development/irStudy/scripts/fix_rag_metadata.py` - regex patterns

### Stage 2: Chunking (`scripts/chunk_medical_texts.py`)

**CRITICAL - Lines 130-134, 148-152, 163-166, 189-192:**

```python
# ✅ CORRECT - Propagate ALL metadata to chunks
chunk = {
    'text': chunk_text,
    'metadata': {
        'source': source_metadata['source'],
        'page': page_num,
        'chunk_id': f"{source_metadata['source']}-p{page_num}-chunk{chunk_idx}",
        # CRITICAL: Preserve bibliographic metadata for RAG citations
        'title': source_metadata.get('title', ''),
        'author': source_metadata.get('author', ''),
        'year': source_metadata.get('year', ''),
        'edition': source_metadata.get('edition', ''),
    }
}

# ❌ INCORRECT - Missing bibliographic metadata (Week 1 mistake)
chunk = {
    'text': chunk_text,
    'metadata': {
        'source': source_metadata['source'],
        'page': page_num,
        # ❌ Missing title, author, year, edition
    }
}
```

### Stage 3: Embedding (`scripts/generate_embeddings.py`)

**Preserve metadata alongside embeddings:**

```python
# ✅ CORRECT - Keep metadata with embeddings
embedded_chunks.append({
    'text': chunk['text'],
    'embedding': embedding.tolist(),
    'metadata': chunk['metadata']  # MUST preserve ALL metadata
})

# ❌ INCORRECT - Metadata lost
embedded_chunks.append({
    'embedding': embedding.tolist()  # ❌ No metadata
})
```

### Stage 4: Qdrant Indexing (`scripts/index_qdrant.py`)

**CRITICAL - Lines 79-83:**

```python
# ✅ CORRECT - Index ALL bibliographic metadata
client.upsert(
    collection_name="medical_knowledge",
    points=[
        PointStruct(
            id=i,
            vector=chunk['embedding'],
            payload={
                'text': chunk['text'],
                'source': chunk['metadata'].get('source', ''),
                'page': chunk['metadata'].get('page', 0),
                'chunk_id': chunk['metadata'].get('chunk_id', ''),
                # CRITICAL: Bibliographic metadata for RAG citations
                'title': chunk['metadata'].get('title', ''),
                'author': chunk['metadata'].get('author', ''),
                'year': chunk['metadata'].get('year', ''),
                'edition': chunk['metadata'].get('edition', ''),
            }
        )
    ]
)

# ❌ INCORRECT - Missing bibliographic metadata (Week 1 mistake)
payload = {
    'text': chunk['text'],
    'source': chunk['metadata'].get('source', ''),
    'page': chunk['metadata'].get('page', 0),
    # ❌ Missing title, author, year, edition
}
```

---

## 11.4 Citation Validation in Generation Scripts

**EVERY MCQ/OSCE generation script MUST validate citations BEFORE using them:**

### Pre-Generation Validation

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

def validate_rag_before_generation():
    """
    MANDATORY: Run before generating any content

    Validates that RAG system returns citations with complete metadata

    Raises:
        ValueError: If RAG returns invalid citations
    """
    client = QdrantClient(url="http://localhost:6333")
    embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    # Test query
    test_query = "depression SSRI first-line treatment"
    query_embedding = embedder.encode(test_query)

    results = client.search(
        collection_name="medical_knowledge",
        query_vector=query_embedding.tolist(),
        limit=1
    )

    if not results:
        raise ValueError("RAG returned no results - database may be empty")

    top_result = results[0]
    payload = top_result.payload

    # Validate metadata
    title = payload.get('title')
    if not title or title == 'Unknown':
        raise ValueError(
            f"RAG returned invalid title: '{title}'\n"
            "Run: ./scripts/pre_flight_validation.sh"
        )

    year = payload.get('year')
    if not year or not (1990 <= int(year) <= 2026):
        raise ValueError(
            f"RAG returned invalid year: '{year}'\n"
            "Run: ./scripts/pre_flight_validation.sh"
        )

    page = payload.get('page')
    if not page or page <= 0:
        raise ValueError(
            f"RAG returned invalid page: '{page}'\n"
            "Run: ./scripts/pre_flight_validation.sh"
        )

    print("✅ RAG validation passed - safe to generate content")
```

### Incremental Validation (Fail-Fast)

```python
def validate_citation(citation: dict, question_id: str) -> None:
    """
    Validate a single citation immediately after RAG retrieval

    Args:
        citation: Citation dict from RAG
        question_id: Question ID for error reporting

    Raises:
        ValueError: If citation has invalid metadata
    """
    # Validate title
    title = citation.get('title')
    if not title or title == 'Unknown':
        raise ValueError(
            f"Question {question_id}: Invalid citation title '{title}'\n"
            f"This indicates RAG database corruption.\n"
            f"Run: ./scripts/pre_flight_validation.sh"
        )

    # Validate author (warning only)
    author = citation.get('author')
    if not author or author == 'Unknown Author':
        logger.warning(
            f"Question {question_id}: Citation has 'Unknown Author' "
            f"(title: {title}, year: {citation.get('year')})"
        )

    # Validate year
    year = citation.get('year')
    try:
        year_int = int(year)
        if not (1990 <= year_int <= 2026):
            raise ValueError(
                f"Question {question_id}: Invalid year {year} (not in 1990-2026)"
            )
    except (ValueError, TypeError):
        raise ValueError(
            f"Question {question_id}: Invalid year format '{year}'"
        )

    # Validate page
    page = citation.get('page')
    if not page or page <= 0:
        raise ValueError(
            f"Question {question_id}: Invalid page number '{page}'"
        )

    logger.info(
        f"Question {question_id}: Citation validated - "
        f"{title} ({author}, {year}), p. {page}"
    )

# Usage in generation loop
for i in range(num_questions):
    # ... generate question ...

    # Get RAG citations
    citations = rag_search(question_context)

    # CRITICAL: Validate IMMEDIATELY (fail-fast)
    for citation in citations:
        validate_citation(citation, question_id=f"MCQ-{i+1:03d}")

    # Only proceed if validation passed
    mcq = create_mcq(question_data, citations)
```

---

## 11.5 Remediation Process (If Validation Fails)

**If pre-flight validation fails, follow these steps:**

### Step 1: Fix Metadata in Chunks

```bash
# Extract metadata from PDF filenames
python scripts/fix_rag_metadata.py

# Verify chunks.json has complete metadata
head -100 data/chunks.json | grep -E '"title"|"author"|"year"'
```

### Step 2: Update Embeddings Metadata

```bash
# Merge existing embeddings with fixed metadata (fast, no re-embedding)
python scripts/update_embeddings_metadata.py \
    --embeddings data/embeddings/medical_embeddings.pkl \
    --chunks data/chunks.json \
    --output data/embeddings/medical_embeddings_fixed.pkl
```

### Step 3: Re-Index Qdrant

```bash
# Index updated embeddings to Qdrant
source venv/bin/activate
python scripts/index_qdrant.py \
    --embeddings data/embeddings/medical_embeddings_fixed.pkl \
    --collection medical_knowledge
```

### Step 4: Re-Run Validation

```bash
# Verify fix worked
./scripts/pre_flight_validation.sh

# Expected output:
# ✅ ALL CRITICAL CHECKS PASSED
# Safe to proceed with content generation
```

---

## 11.6 Quality Assurance Integration

**QA-003 Validator Enhancement (Phase 3):**

The QA-003 validator (`scripts/validate_mcqs_qa003.py`) MUST check citation metadata:

```python
def validate_citation_metadata(citation: dict, question_id: str) -> dict:
    """
    QA-003: Validate citation has complete metadata

    Returns:
        {
            'compliant': bool,
            'tier': 1 | 2 | 3,
            'issues': list[str]
        }
    """
    issues = []

    # CRITICAL: Title must not be "Unknown"
    title = citation.get('title')
    if not title or title == 'Unknown':
        issues.append(f"Invalid title: '{title}'")

    # Author can be "Unknown Author" (warning only)
    author = citation.get('author')
    if not author or author == 'Unknown':
        issues.append(f"Missing author (non-critical)")

    # Year must be valid
    year = citation.get('year')
    try:
        year_int = int(year)
        if not (1990 <= year_int <= 2026):
            issues.append(f"Year {year} out of range (1990-2026)")
    except (ValueError, TypeError):
        issues.append(f"Invalid year format: '{year}'")

    # Page must be >0
    page = citation.get('page')
    if not page or page <= 0:
        issues.append(f"Invalid page: '{page}'")

    # Determine tier
    if not issues:
        tier = 1  # Auto-approve
    elif len(issues) == 1 and "author" in issues[0]:
        tier = 1  # Unknown author is acceptable
    else:
        tier = 3  # Reject - critical metadata missing

    return {
        'compliant': tier == 1,
        'tier': tier,
        'issues': issues
    }
```

---

## 11.7 Agent Requirements (Integration with 08-agent-requirements.md)

**ALL agents generating MCQs/OSCEs MUST:**

1. **Read this constraint file** before starting work
2. **Run pre-flight validation** before generating content:
   ```bash
   ./scripts/pre_flight_validation.sh
   ```
3. **Validate citations incrementally** (fail-fast on first invalid citation)
4. **Never proceed** if validation fails
5. **Document** any RAG metadata issues in agent output

**Example Agent Workflow:**

```markdown
Agent Task: Generate 20 psychiatry MCQs for Week 2 Day 6

CONSTRAINTS:
1. Read: constraints/11-rag-citation-requirements.md
2. Pre-Flight: Run ./scripts/pre_flight_validation.sh
   - EXIT CODE 0 = proceed
   - EXIT CODE 1 = STOP and report validation failures
3. Incremental Validation:
   - For EACH MCQ, validate citations IMMEDIATELY after RAG retrieval
   - If title == "Unknown", STOP and raise error
   - If year invalid, STOP and raise error
   - If page invalid, STOP and raise error
4. Final Validation: Run scripts/validate_mcqs_qa003.py on output

CHECKLIST (verify before returning):
[ ] Pre-flight validation passed (EXIT CODE 0)
[ ] All 20 MCQs have valid citations (title != "Unknown")
[ ] All citations have year in 1990-2026 range
[ ] All citations have page > 0
[ ] QA-003 validation passed (100% compliance)
```

---

## 11.8 Testing Requirements (Integration with 06-testing-requirements.md)

**Automated tests for RAG citation validation:**

```python
# tests/test_rag_citations.py

import pytest
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

def test_rag_database_metadata_completeness():
    """Test that ALL chunks in Qdrant have complete metadata"""
    client = QdrantClient(url="http://localhost:6333")

    # Sample 100 random chunks
    results = client.scroll(
        collection_name="medical_knowledge",
        limit=100,
        with_payload=True
    )

    chunks = results[0]
    assert len(chunks) > 0, "No chunks in database"

    for chunk in chunks:
        payload = chunk.payload

        # Title must not be "Unknown"
        assert payload.get('title') != 'Unknown', \
            f"Chunk {chunk.id} has title='Unknown'"

        # Year must be valid
        year = int(payload.get('year', 0))
        assert 1990 <= year <= 2026, \
            f"Chunk {chunk.id} has invalid year: {year}"

        # Page must be > 0
        page = payload.get('page', 0)
        assert page > 0, \
            f"Chunk {chunk.id} has invalid page: {page}"

def test_rag_citation_quality():
    """Test that RAG returns high-quality citations"""
    client = QdrantClient(url="http://localhost:6333")
    embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    test_queries = [
        "depression SSRI first-line treatment",
        "hypertension first-line medication",
        "asthma management guidelines"
    ]

    for query in test_queries:
        query_embedding = embedder.encode(query)
        results = client.search(
            collection_name="medical_knowledge",
            query_vector=query_embedding.tolist(),
            limit=3
        )

        assert len(results) > 0, f"No results for query: {query}"

        top_result = results[0]
        assert top_result.score >= 0.65, \
            f"Low confidence for query '{query}': {top_result.score}"

        payload = top_result.payload
        assert payload.get('title') != 'Unknown', \
            f"Query '{query}' returned Unknown title"
```

---

## 11.9 Documentation Requirements

**EVERY content generation session MUST document RAG validation status:**

### Session Log Example

```markdown
# Week 2 Day 6 MCQ Generation - Session Log

## Pre-Flight Validation
- Date: 2026-01-25 13:13:21
- Script: ./scripts/pre_flight_validation.sh
- Result: ✅ PASSED
  - Qdrant service: Running
  - Metadata completeness: 1,000/1,000 chunks valid (100%)
  - Citation quality: 20/20 queries passed (100%)
  - Average confidence: 0.770
  - Collection size: 9,950 points

## Content Generation
- Questions generated: 20 MCQs
- Citations validated: 60 citations (3 per MCQ)
- Validation failures: 0
- QA-003 compliance: 100%

## Post-Generation Validation
- Script: scripts/validate_mcqs_qa003.py
- Result: ✅ PASSED
  - Tier 1: 20 MCQs (100%)
  - Tier 2: 0 MCQs
  - Tier 3: 0 MCQs
```

---

## 11.10 Anti-Patterns (NEVER DO THIS)

### ❌ Anti-Pattern 1: Skipping Pre-Flight Validation

```bash
# ❌ INCORRECT - Generating without validation
python scripts/generate_week2_day6_mcqs.py

# ✅ CORRECT - Always validate first
./scripts/pre_flight_validation.sh && \
    python scripts/generate_week2_day6_mcqs.py
```

### ❌ Anti-Pattern 2: Accepting "Unknown" Citations

```python
# ❌ INCORRECT - Accepting invalid citations
title = citation.get('title', 'Unknown')  # ❌ Default to "Unknown"

# ✅ CORRECT - Fail if citation is invalid
title = citation.get('title')
if not title or title == 'Unknown':
    raise ValueError(f"Invalid citation for {question_id}")
```

### ❌ Anti-Pattern 3: Batch Validation (vs Incremental)

```python
# ❌ INCORRECT - Validate after generating all MCQs
mcqs = [generate_mcq() for _ in range(100)]  # Generate all 100
validate_all(mcqs)  # Discover issue at MCQ #87 (wasted 86 MCQs)

# ✅ CORRECT - Validate incrementally (fail-fast)
mcqs = []
for i in range(100):
    mcq = generate_mcq()
    validate_citation(mcq['citations'], f"MCQ-{i+1:03d}")  # Fail at first issue
    mcqs.append(mcq)
```

### ❌ Anti-Pattern 4: Ignoring Validation Failures

```python
# ❌ INCORRECT - Catching and ignoring validation errors
try:
    validate_rag_before_generation()
except ValueError as e:
    logger.warning(f"Validation failed: {e}")  # ❌ Continue anyway
    # Generate content despite validation failure

# ✅ CORRECT - Fail immediately on validation error
validate_rag_before_generation()  # Let exception propagate
# Only reach here if validation passed
```

---

## 11.11 Success Metrics

**How to know the prevention system is working:**

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Pre-flight validation pass rate | 100% before generation | 100% | ✅ |
| Chunks with valid title | 100% | 100% | ✅ |
| Chunks with valid year | 100% | 100% | ✅ |
| Chunks with valid page | 100% | 100% | ✅ |
| Chunks with "Unknown Author" | <20% | 16.4% | ✅ |
| RAG citation quality (≥0.65) | 100% | 100% | ✅ |
| Average RAG confidence | ≥0.70 | 0.770 | ✅ |
| MCQs with invalid citations | 0% | 0% (Week 2+) | ✅ |

**Week 1 Baseline (Mistake):**
- MCQs with valid citations: 0% (212/212 "Unknown")
- Pre-flight validation: NOT RUN
- Incremental validation: NOT IMPLEMENTED

**Week 2 Target (Prevention):**
- MCQs with valid citations: 100%
- Pre-flight validation: MANDATORY before generation
- Incremental validation: FAIL-FAST on first invalid citation

---

## 11.12 Historical Context

**Why This Constraint File Exists:**

On 2026-01-22, we generated Week 1 content (100 MCQs + 5 OSCEs) without validating the RAG database. All 212 citations showed:

```json
{
    "title": "Unknown",
    "author": "Unknown",
    "year": "Unknown",
    "page": "N/A"
}
```

**Root Cause**: Metadata was extracted during PDF processing but lost during chunking. The chunking script didn't propagate `title`, `author`, `year`, and `edition` to chunks, so they were never indexed to Qdrant.

**Fix**: 4-phase prevention system:
1. **Phase 1**: Fixed data pipeline (chunking, indexing, embedding)
2. **Phase 2**: Created validation infrastructure (pre-flight checks, quality tests)
3. **Phase 3**: Enhanced QA-003 validator, added incremental validation
4. **Phase 4**: Updated constraint documentation (this file)

**Lesson**: ALWAYS validate RAG database BEFORE generating content. Pre-flight validation is MANDATORY, not optional.

---

## 11.13 Related Constraints

- **[01-medical-accuracy.md](01-medical-accuracy.md)**: Australian medical standards requiring accurate citations
- **[05-data-processing.md](05-data-processing.md)**: Data pipeline metadata propagation standards
- **[06-testing-requirements.md](06-testing-requirements.md)**: Automated testing requirements for RAG
- **[08-agent-requirements.md](08-agent-requirements.md)**: Agent workflows and validation requirements

---

## 11.14 Quick Reference

**Before generating ANY content, run:**
```bash
./scripts/pre_flight_validation.sh
```

**If validation fails:**
```bash
# Fix metadata
python scripts/fix_rag_metadata.py

# Update embeddings (fast, no re-embedding)
python scripts/update_embeddings_metadata.py

# Re-index Qdrant
source venv/bin/activate
python scripts/index_qdrant.py --embeddings data/embeddings/medical_embeddings_fixed.pkl

# Re-run validation
./scripts/pre_flight_validation.sh
```

**In generation scripts, validate EVERY citation:**
```python
for citation in rag_citations:
    if citation.get('title') == 'Unknown':
        raise ValueError("Invalid RAG citation - run pre-flight validation")
```

---

**Last Updated**: 2026-01-25
**Version**: 1.0
**Status**: MANDATORY for all content generation

[← Back to Index](README.md) | [Quick Start](QUICK_START.md)
