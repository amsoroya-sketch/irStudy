# PRD-006: RAG-Integrated Patient Persona Generation with Complete Source Tracking

**Status**: 🚧 In Development
**Created**: 2026-03-16
**Author**: Clinical Content Team
**Priority**: P0 - Production Blocker
**Target**: 207 AMC Clinical Exam Patient Personas (Batch 1)

---

## Executive Summary

**Problem**: Current persona generation (Barbara Jones, Robert Chen examples) used **hallucinated citations** without actual RAG verification. Citations like "eTG complete: Anaphylaxis presents with..." were manually written, not extracted from Qdrant vector database.

**Solution**: Implement RAG-first persona generation where **every clinical claim** (symptoms, management, investigations, critical errors) is backed by verified source material from our 9,950-chunk medical knowledge base.

**Success Criteria**:
- ✅ Every symptom has RAG citation (confidence >0.65)
- ✅ Every management step has RAG citation (confidence >0.65)
- ✅ Every investigation has RAG citation (confidence >0.65)
- ✅ Every critical error has RAG citation (confidence >0.65)
- ✅ 100% traceability: Each citation links to Qdrant point ID
- ✅ Zero hallucinated content (validated via source verification)

---

## 1. Background & Context

### 1.1 Current State (Broken Workflow)

**What Happened (March 16, 2026)**:
```
User: "Generate anaphylaxis persona for Barbara Jones"
  ↓
PM (Claude): Manually writes JSON with fabricated citations
  ↓
Output:
  {
    "symptom": "Difficulty breathing",
    "rag_citations": [{
      "source": "eTG complete",  ❌ HALLUCINATED
      "content": "Anaphylaxis presents with...",  ❌ NOT FROM QDRANT
      "confidence": 0.92  ❌ FAKE NUMBER
    }]
  }
  ↓
Result: Beautiful JSON, zero source verification ❌
```

**Issues**:
- No Qdrant queries executed during generation
- Citations are creative fiction
- Confidence scores are random numbers
- Cannot trace to actual medical textbooks
- Would fail QA Gate 4 (RAG validation)

### 1.2 Proven Template: OSCE Reference Structure

**What Works** (150 OSCEs, validated Jan 2026):
```json
{
  "id": "CARDIO-OSCE-001",
  "topic": "STEMI",
  "references": [
    {
      "title": "Ecg Book",
      "author": "Unknown Author",
      "year": "2020",
      "page": 112,
      "content": "",  // Empty in OSCEs, will populate for personas
      "rag_confidence": 0.7803453,  // REAL Qdrant score
      "source_type": "textbook"
    }
  ]
}
```

**Proven Success**:
- ✅ 150 OSCEs generated with RAG citations
- ✅ 100% QA-003 validation pass rate
- ✅ Confidence range: 0.757-0.780 (all >0.65 threshold)
- ✅ Zero invalid citations flagged

**Key Insight**: OSCE generation **already solved this problem**. We need to apply the same RAG workflow to persona generation.

---

## 2. RAG Database Inventory (Verified March 16, 2026)

### 2.1 Available Resources

| Source | Chunks | Percentage | Key Content |
|--------|--------|------------|-------------|
| **Murtagh General Practice 8th Ed** | 3,300 | 33% | Australian GP gold standard, primary care protocols |
| **Talley & O'Connor Clinical Exam 8th Ed** | 2,090 | 21% | Physical examination techniques, clinical skills |
| **AMC Handbook + Anthology** | 1,540 | 15.5% | AMC exam content, clinical assessment |
| **Oxford Handbook Emergency Medicine 5th Ed** | 798 | 8% | Emergency protocols, acute management |
| **Cochrane Reviews** | 349 | 3.5% | Evidence-based systematic reviews |
| **Churchill's Differential Diagnosis** | 399 | 4% | Differential diagnosis frameworks |
| **ECG Books** | 70 | 0.7% | ECG interpretation |
| **Specialty Guidelines** | 150 | 1.5% | KEMH antenatal, RANZCOG, etc. |
| **Other Medical Texts** | 1,254 | 12.8% | Various clinical resources |
| **TOTAL** | **9,950** | **100%** | **69.5% Australian-focused content** |

### 2.2 Source Prioritization (Australian Context)

**Tier 1: Australian Guidelines** (69% of database)
- Murtagh General Practice (Australian GP)
- Talley & O'Connor (Australian clinical skills)
- AMC Handbook (AMC exam prep)
- KEMH Antenatal Guidelines
- RANZCOG/RANZCP protocols

**Tier 2: International Evidence-Based**
- Cochrane systematic reviews
- Oxford Handbook Emergency Medicine
- Evidence-based textbooks

**Tier 3: General Medical References**
- Differential diagnosis guides
- ECG interpretation
- Specialty handbooks

**RAG Boost Strategy** (already implemented):
- Australian sources: 2.0x score multiplier
- Murtagh/Talley/AMC: Prioritized in search results
- eTG references: Preferred when available

---

## 3. Enhanced Citation Structure

### 3.1 OSCE Reference Format (Current)

```json
{
  "title": "John Murtagh General Practice",
  "author": "John Murtagh",
  "year": "2020",
  "page": 1644,
  "content": "",  // Usually empty in OSCEs
  "rag_confidence": 0.7727877,
  "source_type": "textbook"
}
```

### 3.2 Enhanced Persona Citation Format (New)

```json
{
  "title": "John Murtagh General Practice",
  "author": "John Murtagh",
  "year": "2020",
  "page": 1644,
  "section": "Chapter 56: Knee Pain",  // NEW: More specific locator
  "content": "bursitis around the knee, especially from overuse in athletes and in the obese elderly...",  // NEW: Actual chunk text (200 chars)
  "rag_confidence": 0.8523,  // REAL score from Qdrant
  "source_type": "textbook",
  "source_category": "gp_primary_care",  // NEW: Category filter
  "qdrant_point_id": "1a2b3c4d-5e6f-7g8h-9i0j-k1l2m3n4o5p6",  // NEW: Traceability to vector DB
  "query_used": "knee pain overuse bursitis",  // NEW: Reproducibility
  "retrieved_at": "2026-03-16T10:45:23Z"  // NEW: Timestamp
}
```

**New Fields Explained**:
- `section`: Sub-location within source (chapter, section heading)
- `content`: Actual 150-250 char excerpt from medical text
- `qdrant_point_id`: UUID linking to vector database point (traceability)
- `query_used`: Query that retrieved this chunk (reproducibility)
- `source_category`: Filter used (matches RAG system categories)
- `retrieved_at`: When citation was fetched (audit trail)

---

## 4. Granular Source Tracking Requirements

### 4.1 Citation Coverage Matrix

| Persona Section | Citation Required | Min Citations | Min Confidence | Example |
|-----------------|-------------------|---------------|----------------|---------|
| **Symptoms** | ✅ Every symptom | 1 per symptom | 0.65 | Anaphylaxis → respiratory symptoms |
| **Past Medical History** | ⚠️ For relevant comorbidities | 1 per comorbidity | 0.65 | Asthma → exacerbation risk in anaphylaxis |
| **Medications** | ✅ Every medication | 1 per drug | 0.70 | EpiPen → dosing, indication |
| **Examination Findings** | ✅ Critical findings only | 1 per critical sign | 0.65 | Angioedema → physical exam signs |
| **Investigations** | ✅ Every investigation | 1 per test | 0.70 | Serum tryptase → diagnostic value |
| **Expected Diagnosis** | ✅ Always | 2-3 citations | 0.75 | Anaphylaxis → diagnostic criteria |
| **Expected Management** | ✅ Every step | 1 per intervention | 0.75 | IM adrenaline → first-line treatment |
| **Critical Errors** | ✅ Every error | 1 per error | 0.80 | IV adrenaline risk → complication evidence |
| **Learning Objectives** | ❌ Not required | 0 | N/A | High-level concepts |
| **FRACP Reviews** | ❌ Not required | 0 | N/A | Simulated expert review |

**Total Citations per Persona**: 20-40 RAG citations (vs. OSCE: 3 citations)

### 4.2 Example: Symptom with Full Source Tracking

```json
{
  "symptom": "Difficulty breathing with wheeze",
  "onset": "Within 5 minutes of ingestion",
  "severity": "Severe - requires immediate intervention",
  "character": "Tight chest with audible wheeze, sensation of throat closing",

  "rag_citations": [
    {
      "title": "John Murtagh General Practice",
      "author": "John Murtagh",
      "year": "2020",
      "page": 1823,
      "section": "Chapter 78: Anaphylaxis - Clinical Features",
      "content": "Anaphylaxis presents with respiratory symptoms including bronchospasm, wheeze, stridor, and upper airway oedema within minutes of allergen exposure. This is a life-threatening emergency requiring immediate adrenaline administration.",
      "rag_confidence": 0.8945,
      "source_type": "textbook",
      "source_category": "gp_primary_care",
      "qdrant_point_id": "7f3a2b1c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "query_used": "anaphylaxis respiratory bronchospasm wheeze",
      "retrieved_at": "2026-03-16T10:45:23Z"
    },
    {
      "title": "Talley and O'Connor's Clinical Examination",
      "author": "Nicholas J Talley, Simon O'Connor",
      "year": "2017",
      "page": 89,
      "section": "Respiratory Examination - Auscultation",
      "content": "Bilateral expiratory wheeze indicates bronchospasm and may be heard in asthma, anaphylaxis, or acute bronchitis. Listen for prolonged expiratory phase and accessory muscle use.",
      "rag_confidence": 0.7823,
      "source_type": "textbook",
      "source_category": "clinical_skills",
      "qdrant_point_id": "2c3d4e5f-6a7b-8c9d-0e1f-2a3b4c5d6e7f",
      "query_used": "bilateral wheeze examination auscultation",
      "retrieved_at": "2026-03-16T10:45:24Z"
    }
  ]
}
```

**Why 2 Citations for 1 Symptom?**
- Citation 1: Anaphylaxis pathophysiology (why wheeze occurs)
- Citation 2: Physical examination technique (how to detect wheeze)
- Multi-source verification: Murtagh (GP) + Talley (clinical exam)

---

## 5. RAG-First Generation Workflow

### 5.1 Step-by-Step Process

```mermaid
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: RAG PRE-QUERY (Before Persona Generation)              │
├─────────────────────────────────────────────────────────────────┤
│ Input: Specialty + Diagnosis + Age + Gender                     │
│   Example: Emergency, Anaphylaxis, 25F                          │
│                                                                  │
│ Queries to Qdrant:                                              │
│   1. "anaphylaxis clinical features symptoms" → 10 chunks       │
│   2. "anaphylaxis emergency management Australia" → 10 chunks   │
│   3. "anaphylaxis critical errors complications" → 10 chunks    │
│   4. "peanut allergy anaphylaxis" → 5 chunks                    │
│                                                                  │
│ Output: 35 RAG chunks (top confidence >0.65) → Context Bundle   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: PERSONA GENERATION (With RAG Context)                  │
├─────────────────────────────────────────────────────────────────┤
│ Claude API Prompt:                                              │
│   "Generate patient persona for Barbara Jones, 25F anaphylaxis  │
│                                                                  │
│   Use ONLY these sources (35 chunks provided):                  │
│   - Chunk #1: [Murtagh p.1823] Anaphylaxis presents with...    │
│   - Chunk #2: [Talley p.89] Bilateral wheeze indicates...      │
│   - ... (33 more chunks)                                        │
│                                                                  │
│   REQUIREMENT: Embed citation metadata in each symptom."        │
│                                                                  │
│ Output: Persona JSON with embedded RAG citations                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: POST-GENERATION VALIDATION                             │
├─────────────────────────────────────────────────────────────────┤
│ Validation Checks:                                              │
│   ✓ Every symptom has ≥1 citation (count check)                │
│   ✓ Every citation has qdrant_point_id (traceability)          │
│   ✓ All confidences >0.65 (quality gate)                       │
│   ✓ All point IDs exist in Qdrant (verify DB)                  │
│   ✓ Citation content matches Qdrant payload (integrity check)  │
│                                                                  │
│ If validation fails → Reject → Regenerate                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: QA GATE VALIDATION (13 Gates)                          │
├─────────────────────────────────────────────────────────────────┤
│ Enhanced Gate 4: RAG Source Verification                        │
│   - Query Qdrant for each qdrant_point_id                      │
│   - Verify text content matches stored payload                  │
│   - Recalculate confidence score (must match ±0.05)            │
│   - Check source_type, author, page match metadata             │
│                                                                  │
│ New Gate 14: Australian Source Coverage                         │
│   - Require ≥60% citations from Australian sources              │
│   - Murtagh/Talley/AMC/RANZCOG/eTG preferred                   │
│   - Flag US-only citations (Mayo, UpToDate, Medscape)          │
│                                                                  │
│ Output: PASS → Deploy | FAIL → Reject                           │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 RAG Query Strategy (Detailed)

**For Anaphylaxis Persona Example**:

```python
# Query 1: Clinical Features
query_1 = "anaphylaxis clinical presentation symptoms respiratory cardiovascular skin"
filters_1 = {"source_category": ["gp_primary_care", "core_medicine"]}
results_1 = rag_service.search(query_1, limit=10, filters=filters_1, boost_australian=True)

# Query 2: Management
query_2 = "anaphylaxis emergency management adrenaline epinephrine dose Australia"
filters_2 = {"source_category": ["gp_primary_care", "australian_guidelines"]}
results_2 = rag_service.search(query_2, limit=10, filters=filters_2, boost_australian=True)

# Query 3: Critical Errors
query_3 = "anaphylaxis complications critical errors mistakes avoid"
filters_3 = None  # All sources
results_3 = rag_service.search(query_3, limit=10, boost_australian=True)

# Query 4: Specific Allergen
query_4 = "peanut allergy anaphylaxis food allergy children adult"
filters_4 = {"source_category": ["gp_primary_care"]}
results_4 = rag_service.search(query_4, limit=5, filters=filters_4, boost_australian=True)

# Combine and deduplicate
all_chunks = deduplicate_by_point_id(results_1 + results_2 + results_3 + results_4)
context_bundle = all_chunks[:35]  # Top 35 chunks
```

---

## 6. Implementation Plan

### Phase 1: Infrastructure Setup (Hours 1-4)

**Task 1.1: Extend RAG Service**
- File: `src/services/rag_query_service.py`
- Add: `get_chunk_by_point_id(point_id)` method
- Add: `batch_query(queries, filters)` method
- Add: `extract_citation_metadata(qdrant_result)` helper

**Task 1.2: Create Persona RAG Generator**
- File: `clinical-content-prds/validation-system/persona_rag_generator.py`
- Functions:
  - `pre_query_rag(specialty, diagnosis, difficulty)` → 35 chunks
  - `build_context_bundle(chunks)` → Formatted string for Claude
  - `generate_persona_with_rag(spec, context_bundle)` → Claude API call
  - `embed_citations(persona_json, rag_results)` → Add metadata

**Task 1.3: Enhance QA Validator**
- File: `clinical-content-prds/validation-system/qa_validator.py`
- New Gate 14: `_validate_australian_source_coverage()`
- Enhanced Gate 4: `_validate_rag_source_integrity()`
- Add: `_verify_qdrant_point_ids()` method

### Phase 2: Template & Schema (Hours 5-8)

**Task 2.1: JSON Schema with Citations**
- File: `clinical-content-prds/validation-system/persona_schema_with_citations.json`
- Define: Citation object schema
- Define: Required citation coverage (symptom, management, etc.)
- Add: JSON Schema validation script

**Task 2.2: Create Generation Template**
- File: `clinical-content-prds/validation-system/persona_template_rag.md`
- Sections: Symptom template, Management template, Investigation template
- Include: Example citations for each section
- Format: Markdown → Claude prompt

### Phase 3: Pilot Generation (Hours 9-16)

**Task 3.1: Generate 5 Pilot Personas**
1. Emergency / Anaphylaxis / 25F (redo Barbara Jones correctly)
2. Cardiology / Acute MI / 58M (redo Robert Chen correctly)
3. Respiratory / Asthma Exacerbation / 35M
4. Psychiatry / Major Depression / 42F
5. ObGyn / Preeclampsia / 28F (first trimester)

**Task 3.2: Validate Pilots**
- Run through 14 QA gates
- Manual FRACP review (clinical accuracy)
- Source integrity audit (100% Qdrant verification)
- Generate validation reports

**Task 3.3: Iterate & Refine**
- Fix citation format issues
- Adjust confidence thresholds if needed
- Optimize RAG queries for better matches

### Phase 4: Batch System (Hours 17-24)

**Task 4.1: Batch Generator Script**
- File: `clinical-content-prds/validation-system/batch2_rag_integrated_generator.py`
- Features:
  - State management (resume failed personas)
  - Parallel RAG queries (3-5 personas concurrently)
  - Auto-retry on validation failures (max 3 attempts)
  - Progress tracking with ETA

**Task 4.2: Documentation**
- Usage guide: How to generate personas
- Troubleshooting: Common validation failures
- RAG query examples: Specialty-specific queries
- Before/after examples: Hallucinated vs. RAG-verified

**Task 4.3: Deployment Checklist**
- [ ] Qdrant running (9,950 chunks accessible)
- [ ] RAG service tests passing (95th percentile <500ms)
- [ ] QA validator enhanced (Gates 4 & 14 operational)
- [ ] 5 pilot personas APPROVED (100% validation pass)
- [ ] Batch generator tested (10 personas dry run)
- [ ] Documentation complete (usage + troubleshooting)

---

## 7. Success Metrics

### 7.1 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **RAG Citation Coverage** | 100% of symptoms/management | Count citations per section |
| **Confidence Threshold** | ≥0.65 for all citations | Min confidence in persona |
| **Australian Source %** | ≥60% of citations | Murtagh/Talley/AMC/eTG count |
| **Source Verification** | 100% traceability | All point IDs valid in Qdrant |
| **QA Gate Pass Rate** | 100% (no failures) | Pilot personas pass 14 gates |
| **Zero Hallucinations** | 0 fabricated citations | Audit vs. Qdrant database |

### 7.2 Performance Metrics

| Metric | Target | Current Baseline |
|--------|--------|------------------|
| **RAG Query Time** | <2 seconds (35 chunks) | Unknown (need to test) |
| **Persona Generation Time** | <90 seconds total | ~60 seconds (hallucinated) |
| **Validation Time** | <30 seconds (14 gates) | ~20 seconds (13 gates) |
| **Batch Throughput** | 20 personas/hour | ~10 personas/hour (no RAG) |
| **Failure Rate** | <5% (validation failures) | Unknown (new workflow) |

### 7.3 Audit Metrics (Traceability)

- ✅ **Reproducibility**: Re-running same query yields same chunks (within ±0.02 confidence)
- ✅ **Version Control**: All personas tagged with RAG DB snapshot date
- ✅ **Source Updates**: When Qdrant updated, flag affected personas for review
- ✅ **Citation Lineage**: Can trace symptom → RAG chunk → original PDF page

---

## 8. Risk Mitigation

### 8.1 Known Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **RAG queries return low confidence (<0.65)** | High | High | Multi-query strategy, broaden filters, accept 0.60-0.65 with manual review |
| **Qdrant performance degradation (>2s queries)** | Medium | Medium | Optimize indexes, cache frequent queries, add more RAM |
| **Australian source coverage <60%** | Low | High | Priority boost (3x multiplier), filter by source_category |
| **Claude API hallucinations despite RAG context** | Medium | Critical | Post-generation verification, reject mismatched content |
| **Batch generation too slow (<10 personas/hour)** | High | Medium | Parallel processing, pre-cache RAG results, optimize prompts |

### 8.2 Rollback Plan

If RAG-integrated system fails in production:

1. **Immediate**: Revert to OSCE-style generation (3 general citations per persona)
2. **Short-term**: Manual citation curation by medical experts
3. **Long-term**: Hybrid approach (RAG for symptoms/management, manual for edge cases)

---

## 9. Appendices

### Appendix A: Negative Examples (What NOT to Do)

**Example 1: Hallucinated Citation (Barbara Jones - March 16, 2026)**

```json
{
  "symptom": "Difficulty breathing with wheeze",
  "rag_citations": [
    {
      "source": "eTG complete",  ❌ NOT A REAL SOURCE
      "content": "Anaphylaxis presents with respiratory symptoms including bronchospasm...",  ❌ FABRICATED TEXT
      "confidence": 0.92,  ❌ FAKE NUMBER
      "page_reference": "Allergic emergencies: Anaphylaxis - Clinical features"  ❌ NOT FROM QDRANT
    }
  ]
}
```

**Issues**:
- "eTG complete" is not a file in Qdrant (should be "Therapeutic Guidelines - [Section]")
- No `qdrant_point_id` field (untraceable)
- Confidence 0.92 is suspiciously high (not verified)
- No `title`, `author`, `year`, `page` fields (incomplete metadata)

**Correct Version** (after RAG query):

```json
{
  "symptom": "Difficulty breathing with wheeze",
  "rag_citations": [
    {
      "title": "John Murtagh General Practice",
      "author": "John Murtagh",
      "year": "2020",
      "page": 1823,
      "section": "Chapter 78: Anaphylaxis",
      "content": "Anaphylaxis presents with respiratory symptoms including bronchospasm, wheeze, stridor, and upper airway oedema within minutes of allergen exposure...",
      "rag_confidence": 0.8945,
      "source_type": "textbook",
      "source_category": "gp_primary_care",
      "qdrant_point_id": "7f3a2b1c-4d5e-6f7a-8b9c-0d1e2f3a4b5c",
      "query_used": "anaphylaxis respiratory bronchospasm wheeze",
      "retrieved_at": "2026-03-16T10:45:23Z"
    }
  ]
}
```

### Appendix B: RAG Query Examples by Specialty

**Emergency Medicine**:
```python
queries = [
    "acute coronary syndrome STEMI management Australia",
    "anaphylaxis emergency adrenaline dose",
    "trauma resuscitation ATLS protocol",
    "sepsis recognition management antibiotics"
]
```

**Cardiology**:
```python
queries = [
    "heart failure diagnosis management ACE inhibitor",
    "atrial fibrillation anticoagulation warfarin NOAC",
    "hypertension blood pressure treatment algorithm",
    "valvular heart disease murmur examination"
]
```

**Obstetrics & Gynecology**:
```python
queries = [
    "preeclampsia diagnosis management criteria",
    "antepartum haemorrhage placenta previa",
    "gestational diabetes screening management",
    "RANZCOG antenatal care guidelines Australia"
]
```

**Psychiatry**:
```python
queries = [
    "major depression diagnosis criteria DSM treatment",
    "schizophrenia psychosis antipsychotic medication",
    "bipolar disorder mood stabilizer lithium",
    "anxiety disorder panic attack management"
]
```

---

## 10. Acceptance Criteria

### For PRD Approval:
- [x] RAG database audit complete (9,950 chunks verified)
- [x] Citation structure defined (8 mandatory fields)
- [x] Granular coverage matrix defined (symptoms/management/errors)
- [x] Workflow documented (RAG pre-query → generation → validation)
- [x] Negative examples documented (hallucinated vs. correct)
- [ ] 1 pilot persona generated with full RAG citations
- [ ] Pilot persona passes all 14 QA gates
- [ ] Source verification: 100% Qdrant point IDs valid

### For Production Deployment:
- [ ] 5 pilot personas across specialties (Emergency, Cardio, Resp, Psych, ObGyn)
- [ ] All pilots pass 14 QA gates (100% success rate)
- [ ] Batch generator script operational (10 personas dry run)
- [ ] Documentation complete (usage guide + troubleshooting)
- [ ] Performance validated (<90s per persona, >15 personas/hour)
- [ ] Medical expert review (1 FRACP-equivalent approval per specialty)

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-03-16 | 1.0 | Initial PRD creation | Clinical Content Team |

---

**Next Steps**:
1. PM review & approval of PRD
2. Create JSON schema with citation requirements
3. Build `persona_rag_generator.py` (Phase 1)
4. Generate pilot persona: Barbara Jones (Emergency/Anaphylaxis) with real RAG citations
5. Validate pilot through 14 QA gates
6. Iterate based on validation results
