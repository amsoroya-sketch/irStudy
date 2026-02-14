# RAG Validation Specification for Medical Accuracy

**Source**: AI_OSCE_CLINICAL_REVIEW_REPORT.md Section 3 + PRD 1
**Purpose**: Prevent AI Patient from providing medically incorrect or dangerous information
**Created**: 2026-02-10
**Australian Context**: Mandatory Australian sources, no US-only guidelines

---

## Purpose

This specification defines how Retrieval Augmented Generation (RAG) must validate all medical claims made by AI Patient and AI Examiner to prevent:
- Medical inaccuracies
- Dangerous clinical advice
- Non-Australian medical context (US guidelines, US drug names, US emergency numbers)
- Hallucinated medical "facts"

---

## 1. Confidence Threshold Requirements

### 1.1 Minimum Confidence Levels

**MANDATORY THRESHOLDS** (per PROJECT_CONSTRAINTS.md line 26):
- **Minimum confidence**: >0.65 for ALL medical statements
- **Ideal confidence**: >0.80 for critical medical information
- **Reject chunks**: confidence <0.65 (MUST NOT use)

### 1.2 Critical vs Non-Critical Information

**Critical Medical Information** (requires >0.80 confidence):
- Medication dosing (e.g., "Aspirin 300mg for ACS" NOT "100mg")
- Emergency management (e.g., "Call 000", "ECG within 10 minutes")
- Red flags (e.g., "Crushing chest pain >20 minutes = MI")
- Contraindications (e.g., "Don't give aspirin if active bleeding")
- Auto-fail triggers (e.g., "Missing STEMI diagnosis = patient safety violation")

**Non-Critical Information** (requires >0.65 confidence):
- Patient demographic details
- General health advice
- Non-urgent investigation timeframes
- Background medical information

### 1.3 What Happens If Confidence Too Low?

**If confidence <0.65**:
1. AI MUST NOT make that medical claim
2. AI should respond: "I don't have enough information to answer that accurately. Let me check..."
3. Fallback to safe, generic response OR ask clarifying question
4. Log the failed query for later RAG improvement

**Example**:
```
Student: "What dose of metoprolol should I give for acute MI?"
RAG Chunks: Top result confidence = 0.58 (TOO LOW)
AI Response: "I don't have the specific dosing information readily available. For post-MI beta-blocker therapy, I'd recommend checking the Therapeutic Guidelines or consulting cardiology."
```

---

## 2. Australian Source Filtering

### 2.1 APPROVED SOURCES ONLY

AI MUST ONLY use chunks from these Australian medical sources:

**Primary Australian Sources**:
- ✅ **eTG** (Therapeutic Guidelines) - ALL specialties
- ✅ **AMH** (Australian Medicines Handbook)
- ✅ **PBS** (Pharmaceutical Benefits Scheme)
- ✅ **AMC Clinical Examination Handbook**
- ✅ **Talley & O'Connor's Clinical Examination** (8th edition, Australian)

**Australian College Guidelines**:
- ✅ **RANZCOG** (Royal Australian and New Zealand College of Obstetricians and Gynaecologists)
- ✅ **RACGP** (Royal Australian College of General Practitioners)
- ✅ **RACP** (Royal Australasian College of Physicians)
- ✅ **ACEM** (Australasian College for Emergency Medicine)
- ✅ **ANZCA** (Australian and New Zealand College of Anaesthetists)

**Australian State Health Protocols**:
- ✅ **NSW Health** clinical protocols
- ✅ **Queensland Health** guidelines
- ✅ **Victorian Department of Health** guidelines
- ✅ **Australian Resuscitation Council** guidelines

**Evidence-Based International (with Australian context)**:
- ✅ **Cochrane Reviews** (IF accompanied by Australian clinical interpretation)
- ✅ **BMJ Best Practice** (IF Australian content sections used)
- ✅ **WHO Guidelines** (IF explicitly referenced in Australian guidelines)

### 2.2 NEVER USE - US-Only Sources

**REJECTED SOURCES** (even if high confidence):
- ❌ **UpToDate** (US-based, different drug names, different management)
- ❌ **USMLE** materials (US medical licensing exam - not relevant to AMC)
- ❌ **ACOG** (American College of Obstetricians and Gynecologists - use RANZCOG instead)
- ❌ **AHA/ACC** (American Heart Association - use Australian Clinical Guidelines for ACS instead)
- ❌ **CDC** (Centers for Disease Control - use Australian Department of Health)
- ❌ **FDA** (US drug regulator - use TGA/PBS instead)

### 2.3 Source Filtering Algorithm

```python
APPROVED_SOURCES = [
    'therapeutic guidelines', 'etg', 'amh', 'australian medicines handbook',
    'pbs', 'pharmaceutical benefits scheme', 'amc', 'talley', "o'connor",
    'ranzcog', 'racgp', 'racp', 'acem', 'anzca',
    'nsw health', 'queensland health', 'victorian health',
    'australian resuscitation council', 'cochrane'
]

def validate_source(chunk_metadata: dict) -> bool:
    """
    Returns True if chunk comes from approved Australian source.
    """
    source = chunk_metadata.get('source', '').lower()

    # Check if any approved source is in the chunk source
    return any(approved in source for approved in APPROVED_SOURCES)
```

---

## 3. Hallucination Detection

### 3.1 What is Hallucination?

**Hallucination**: AI generating "facts" that are NOT supported by RAG chunks.

**Common Hallucinations in Medical AI**:
- Inventing medication doses (e.g., "Give paracetamol 500mg QID" when correct is 1g QID)
- Making up investigation timeframes (e.g., "ECG within 30 minutes" when guideline says 10 minutes)
- Creating fake citations (e.g., "Per eTG Section 5.2.1" when that section doesn't exist)
- Fabricating red flags not mentioned in source material

### 3.2 VERIFY CRITICAL STATEMENTS

**MANDATORY verification for**:
1. **Medication dosing** → MUST match AMH exactly
2. **Investigation timeframes** → MUST match Australian guidelines exactly
3. **Critical actions** → MUST have eTG/AMH/AMC citation
4. **Red flags** → MUST have evidence in RAG chunks

### 3.3 Validation Algorithm

```python
def validate_ai_response(response: str, rag_chunks: list) -> tuple[bool, list]:
    """
    Validates AI Patient/Examiner response against RAG chunks.
    Returns (is_valid, citations_list)
    """

    # Step 1: Confidence threshold filter
    valid_chunks = [c for c in rag_chunks if c['score'] > 0.65]

    # Step 2: Australian sources only
    valid_chunks = [
        c for c in valid_chunks
        if any(source in c['metadata']['source'].lower()
               for source in APPROVED_SOURCES)
    ]

    # Step 3: Minimum 1 citation required for medical claims
    if len(valid_chunks) < 1:
        return False, []  # INVALID - no supporting evidence

    # Step 4: Extract top 3 citations (max)
    citations = [
        format_citation(c['metadata'])
        for c in valid_chunks[:3]
    ]

    return True, citations


def format_citation(metadata: dict) -> str:
    """
    Format citation in AMC-acceptable format.

    Example output:
    "(Therapeutic Guidelines: Cardiovascular, Section 5.2.1, 2024: ACS management)"
    """
    source = metadata.get('source', 'Unknown')
    section = metadata.get('section', '')
    page = metadata.get('page', '')
    year = metadata.get('year', '2024')
    topic = metadata.get('topic', '')

    # Format with section OR page (whichever available)
    if section:
        location = f"Section {section}"
    elif page:
        location = f"p.{page}"
    else:
        location = ""

    # Build citation
    citation_parts = [source]
    if location:
        citation_parts.append(location)
    if year:
        citation_parts.append(year)
    if topic:
        citation_parts.append(topic)

    return f"({', '.join(citation_parts)})"
```

### 3.4 Example Validation

**Student asks AI Patient**: "What symptoms are you experiencing?"

**AI Patient wants to say**: "I have crushing central chest pain radiating to my left arm and jaw, with sweating and nausea."

**RAG Query**: "chest pain symptoms myocardial infarction"

**RAG Chunks Returned**:
```python
[
    {
        'content': 'Typical MI pain: crushing central chest pain, >20 minutes duration, radiation to left arm/jaw/back, associated diaphoresis...',
        'score': 0.87,
        'metadata': {
            'source': "Talley & O'Connor's Clinical Examination, 8th ed",
            'page': '145',
            'topic': 'Chest pain characteristics'
        }
    },
    {
        'content': 'MI red flags include: crushing pain, radiation to arm/jaw, sweating (diaphoresis), nausea/vomiting...',
        'score': 0.79,
        'metadata': {
            'source': 'Therapeutic Guidelines: Cardiovascular',
            'section': '5.1',
            'year': '2024',
            'topic': 'ACS presentation'
        }
    }
]
```

**Validation Result**:
```python
is_valid, citations = validate_ai_response(ai_response, rag_chunks)
# is_valid = True (confidence >0.65, Australian sources)
# citations = [
#     "(Talley & O'Connor's Clinical Examination, 8th ed, p.145: Chest pain characteristics)",
#     "(Therapeutic Guidelines: Cardiovascular, Section 5.1, 2024: ACS presentation)"
# ]
```

**AI Patient response includes citation** (displayed in logs, not to student):
```
Patient: "I have crushing central chest pain radiating to my left arm and jaw, with sweating and nausea."

[Internal RAG validation: ✅ Valid - 2 citations, confidence 0.87/0.79]
[Citations: (Talley & O'Connor 8th ed, p.145), (eTG Cardiovascular 5.1, 2024)]
```

---

## 4. Expert Validation Process

### 4.1 Golden Dataset Validation

**Purpose**: Ensure RAG system retrieves clinically accurate information.

**Process**:
1. Create 200 Golden Dataset scenarios (see GOLDEN_DATASET_SPECIFICATION.md)
2. For each scenario, clinical expert validates:
   - ✅ All medical claims have RAG citations with >0.65 confidence
   - ✅ Citations come from approved Australian sources
   - ✅ No hallucinated information
   - ✅ Medication doses match AMH exactly
   - ✅ Critical actions match eTG/guidelines exactly

### 4.2 AI vs Human Examiner Scoring

**Tolerance**: AI Examiner score vs Human Examiner score ±2 marks

**Process**:
1. Medical student completes OSCE with AI Patient
2. AI Examiner scores using 15-mark rubric
3. 3 independent human AMC examiners score same transcript (blinded to AI score)
4. Compare scores:
   - ✅ PASS: AI within ±2 marks of ALL 3 human examiners
   - ❌ FAIL: AI differs by >±2 marks from ANY human examiner

**If validation fails**: Adjust AI Examiner prompt, re-validate.

### 4.3 Quarterly Recalibration

**Frequency**: Every 3 months

**Process**:
1. Re-validate 20 random scenarios from Golden Dataset (10%)
2. Run AI Examiner scoring
3. New human examiner panel scores same transcripts
4. Compare variance (must remain ≤±2 marks)
5. Document any drift in scoring patterns
6. Update AI prompts if needed

---

## 5. Citation Format Requirements

### 5.1 Standard Citation Format

**Format**: `(Source, Location, Year: Topic)`

**Examples**:
- `(Therapeutic Guidelines: Antibiotic, Section 2.3.2, 2024: CAP treatment in penicillin-allergic patients)`
- `(Talley & O'Connor's Clinical Examination, 8th ed, p.267-269: Bronchiectasis examination)`
- `(NSW Health Respiratory Infections Protocol, Section 4.1, 2024: CAP management)`
- `(AMC Handbook of Clinical Assessment, p.23-25: Communication Skills Marking Criteria)`

### 5.2 Minimum Citation Requirements

**For AI Patient responses**:
- ✅ Minimum 1 RAG citation per medical claim
- ✅ Maximum 3 citations per response (avoid overwhelming logs)
- ✅ Citations appear in internal logs (NOT displayed to student during OSCE)

**For AI Examiner feedback**:
- ✅ Minimum 1 RAG citation per scoring domain
- ✅ Critical errors MUST have citation supporting the "why it's critical"
- ✅ Citations appear in structured feedback JSON

### 5.3 Where Citations Appear

**AI Patient** (during OSCE):
- Citations in backend logs only
- NOT displayed to student (would break immersion)
- Available for quality assurance review

**AI Examiner** (feedback after OSCE):
- Citations in structured JSON feedback
- Example:
```json
{
  "communication_score": 2,
  "communication_feedback": "Adequate rapport established; mostly patient-centered with occasional interruptions",
  "communication_citation": "(AMC Handbook of Clinical Assessment, p.23-25: Communication Skills Marking Criteria)"
}
```

---

## 6. Implementation Requirements

### 6.1 Code Integration Points

**File**: `backend/src/services/rag_query_service.py`

**Functions to implement**:
```python
class RAGValidationService:
    def validate_chunks(self, chunks: list) -> list:
        """Filter chunks by confidence >0.65 and Australian sources."""
        pass

    def detect_hallucination(self, ai_response: str, chunks: list) -> bool:
        """Check if AI response is grounded in RAG chunks."""
        pass

    def format_citations(self, chunks: list, max_citations: int = 3) -> list:
        """Format top N chunks as AMC-style citations."""
        pass

    def log_validation_failure(self, query: str, reason: str):
        """Log when RAG validation fails for monitoring."""
        pass
```

### 6.2 Database Schema Requirements

**Add to patient_personas table**:
```sql
-- RAG Citation Validation
rag_citations JSONB,  -- ALL clinical claims must have citations
/*
{
  "diagnosis": "(Talley & O'Connor, 8th ed, p.145)",
  "management": "(eTG Cardiovascular, Section 5.2.1, 2024)",
  "red_flags": "(AMC Handbook, p.89)"
}
*/

-- Quality Assurance
clinical_accuracy_validated BOOLEAN DEFAULT FALSE,
validated_by_clinician UUID REFERENCES users(user_id),
validation_notes TEXT
```

### 6.3 Monitoring & Logging

**Log all RAG validations**:
```json
{
  "timestamp": "2026-02-10T10:30:45Z",
  "query": "chest pain red flags MI",
  "top_chunk_confidence": 0.87,
  "num_valid_chunks": 2,
  "all_australian_sources": true,
  "validation_passed": true,
  "citations": [
    "(Talley & O'Connor 8th ed, p.145)",
    "(eTG Cardiovascular 5.1, 2024)"
  ]
}
```

**Alert if validation failures exceed threshold**:
- >5% of queries returning confidence <0.65 → Alert: RAG embeddings may need reindexing
- Any query using non-Australian source → Alert: Source filtering broken
- Hallucination detected → Alert: Critical - AI making unsupported claims

---

## 7. Success Criteria

**PRD 1 Complete when**:
✅ All AI Patient responses have ≥1 RAG citation with confidence >0.65
✅ 100% Australian sources (no US-only materials detected in 7-day monitoring period)
✅ Critical medical statements verified against RAG chunks (0 hallucination incidents)
✅ Golden Dataset validation: AI vs human examiner variance ≤±2 marks (all 200 scenarios)
✅ RAG validation code implemented in `backend/src/services/rag_query_service.py`
✅ Database schema updated with `rag_citations` JSONB column
✅ Monitoring dashboard shows 0 validation failures for 48 hours

---

## 8. Australian Terminology Enforcement

### 8.1 Drug Name Mapping (US → Australian)

**AI MUST use Australian drug names**:

| ❌ US Name | ✅ Australian Name |
|-----------|-------------------|
| Acetaminophen | Paracetamol |
| Albuterol | Salbutamol |
| Epinephrine | Adrenaline |
| Norepinephrine | Noradrenaline |
| Furosemide | Frusemide |
| Acetylsalicylic acid | Aspirin |

**Validation**: RAG chunks from AMH always use Australian names. If AI uses US name → hallucination detected.

### 8.2 Healthcare System Terminology

| ❌ US Term | ✅ Australian Term |
|-----------|------------------|
| ER (Emergency Room) | ED (Emergency Department) |
| Call 911 | Call 000 |
| Medicaid | Medicare / PBS |
| Co-pay | PBS co-payment |
| Attending physician | Consultant |
| Resident | Registrar |

### 8.3 Spelling Differences

**Australian English required**:
- ✅ Haemoglobin (NOT hemoglobin)
- ✅ Anaemia (NOT anemia)
- ✅ Oesophagus (NOT esophagus)
- ✅ Paediatric (NOT pediatric)
- ✅ Haematology (NOT hematology)

**RAG chunks from Australian sources use Australian spelling** → Natural enforcement.

---

## 9. Common Validation Edge Cases

### 9.1 What if no RAG chunks found?

**Scenario**: Student asks unusual question, RAG returns 0 chunks with confidence >0.65.

**AI Patient response**:
```
"I'm not sure about that specific detail. Can you tell me more about what you're asking?"
```

**Log**:
```json
{
  "validation_failed": true,
  "reason": "No chunks with confidence >0.65",
  "query": "rare metabolic disorder porphyria cutanea tarda",
  "fallback_response_used": true
}
```

### 9.2 What if RAG returns US guideline?

**Scenario**: RAG returns ACOG guideline (US obstetrics) instead of RANZCOG.

**Validation**: Filter rejects chunk (not in APPROVED_SOURCES).

**Result**: AI cannot make that clinical claim OR falls back to safe response.

### 9.3 What if citation page number wrong?

**Scenario**: RAG chunk metadata says "p.145" but actual page is 146 (OCR error during PDF processing).

**Mitigation**:
- Golden Dataset validation catches this (clinical expert reviews citations)
- Quarterly recalibration re-checks 10% of scenarios
- Citation format includes page range when uncertain: `p.145-147`

---

**End of RAG Validation Specification** - Ready for Clinical Advisor review
