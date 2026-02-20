# RAG Validation Specification - Clinical Content Quality Assurance

**Document Version**: 1.0
**Purpose**: Define validation rules for Retrieval-Augmented Generation (RAG) system to ensure clinical accuracy and Australian standards compliance
**Created**: 2026-02-15
**Target Users**: Backend developers, QA engineers, Clinical Advisor

---

## Executive Summary

This document specifies validation rules for the RAG system that generates and validates clinical content (MCQs, OSCE scenarios, explanations) for the irStudy platform. All AI-generated clinical content MUST pass these validation checks before being presented to users.

**Zero-Tolerance Policy**: Clinical content that fails validation MUST be rejected and never shown to students.

**Quality Gates**:
- ✅ Confidence threshold: >0.65 (65%)
- ✅ Australian source validation: 100% compliance
- ✅ Citation requirements: Complete source + page/section
- ✅ Guideline recency: ≤2 years old (medical content changes frequently)
- ✅ Terminology compliance: Australian medical terminology mandatory

---

## 1. RAG System Architecture Overview

### Components

```
┌─────────────────────┐
│   User Request      │  (e.g., "Generate MCQ on pre-eclampsia")
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Query Embedding    │  (Convert to vector using sentence-transformers)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Vector DB Retrieval │  (Qdrant: Search Australian medical guidelines)
│  (Top-K Results)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  RAG Validation     │  ◄── THIS DOCUMENT SPECIFIES RULES HERE
│   (This Spec)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  LLM Generation     │  (Claude 3.5 Sonnet via API - if validation passes)
│  (Clinical Content) │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Post-Generation    │  (Citation verification, terminology check)
│    Validation       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Return to User     │  (or REJECT if fails validation)
└─────────────────────┘
```

---

## 2. Confidence Threshold Rules

### Minimum Confidence Score: 0.65 (65%)

**Rationale**: Medical content requires high confidence to ensure accuracy. Below 65% confidence indicates insufficient evidence in knowledge base.

**Implementation**:

```python
def validate_confidence(retrieval_results):
    """
    Validate that retrieved documents meet minimum confidence threshold.

    Args:
        retrieval_results: List of (document, score) tuples from vector DB

    Returns:
        ValidationResult with pass/fail and justification
    """
    if not retrieval_results:
        return ValidationResult(
            passed=False,
            reason="No documents retrieved from knowledge base",
            confidence=0.0
        )

    # Get highest confidence score
    max_confidence = max(score for _, score in retrieval_results)

    if max_confidence < 0.65:
        return ValidationResult(
            passed=False,
            reason=f"Confidence too low ({max_confidence:.2f} < 0.65). Insufficient evidence in knowledge base.",
            confidence=max_confidence,
            action="REJECT - Do not generate content"
        )

    # Log all sources with confidence scores
    sources = [
        {"document": doc.metadata["source"], "confidence": score}
        for doc, score in retrieval_results
    ]

    return ValidationResult(
        passed=True,
        confidence=max_confidence,
        sources=sources,
        action="PROCEED with generation"
    )
```

**Confidence Score Interpretation**:

| Score Range | Interpretation | Action |
|-------------|---------------|---------|
| 0.85 - 1.00 | Excellent match | Proceed with high confidence |
| 0.65 - 0.84 | Good match | Proceed, log for review |
| 0.50 - 0.64 | Marginal match | REJECT - insufficient confidence |
| 0.00 - 0.49 | Poor match | REJECT - insufficient confidence |

**Special Cases**:

1. **Multiple high-confidence sources**: If ≥3 sources all score >0.70, average confidence can be used
2. **Conflicting sources**: If high-confidence sources conflict, REJECT and flag for human review
3. **No sources found**: Immediate rejection, don't attempt generation

---

## 3. Australian Source Validation

### Approved Australian Medical Sources

**Tier 1: Primary Australian Clinical Guidelines** (Highest priority):
- ✅ **Therapeutic Guidelines (eTG)**: Complete series (Cardiovascular, Antibiotic, Respiratory, etc.)
- ✅ **Australian Medicines Handbook (AMH)**: Medication dosing, interactions
- ✅ **RACGP (Royal Australian College of General Practitioners)**: Red Book, Green Book
- ✅ **RANZCOG**: Obstetrics and gynaecology guidelines
- ✅ **ANZCA**: Anaesthetics and pain management
- ✅ **NHMRC**: National Health and Medical Research Council guidelines
- ✅ **State Health Department Protocols**:
  - NSW Health Clinical Guidelines
  - Queensland Clinical Guidelines
  - Victoria Health Clinical Practice
  - SA Health Guidelines

**Tier 2: Australian Clinical Resources** (Secondary sources):
- ✅ **AMC Resources**: Australian Medical Council clinical exam materials
- ✅ **AHPRA**: Professional standards, codes of conduct
- ✅ **PBS (Pharmaceutical Benefits Scheme)**: Medication listings, subsidies
- ✅ **NPS MedicineWise**: Medication education
- ✅ **Australian Resuscitation Council**: CPR and emergency protocols

**Tier 3: Acceptable International Sources** (ONLY if Australian-adapted or no Australian equivalent):
- ⚠️ **WHO**: If no Australian guideline exists (e.g., rare tropical diseases)
- ⚠️ **Cochrane Reviews**: Evidence-based medicine (no specific country protocols)
- ⚠️ **NICE Guidelines (UK)**: Only if specifically labeled "Australian adaptation available"

**REJECTED Sources** (Do NOT use):
- ❌ **American sources without Australian adaptation**:
  - UpToDate (American medication names, doses, protocols)
  - American College of Cardiology
  - American Heart Association
  - CDC guidelines
- ❌ **Wikipedia**: Not a medical authority
- ❌ **Patient information websites**: Unless Australian government (e.g., HealthDirect.gov.au acceptable for patient education)
- ❌ **Outdated guidelines**: >2 years old (see Section 4)

### Validation Implementation

```python
APPROVED_AUSTRALIAN_SOURCES = [
    # Tier 1
    "therapeutic guidelines", "etg", "tg complete",
    "australian medicines handbook", "amh",
    "racgp", "red book", "green book",
    "ranzcog",
    "nhmrc",
    "nsw health", "queensland health", "victoria health", "qld clinical guidelines",

    # Tier 2
    "amc", "australian medical council",
    "ahpra",
    "pbs", "pharmaceutical benefits scheme",
    "nps medicinewise",
    "australian resuscitation council",

    # Tier 3 (conditional)
    "who", "world health organization",
    "cochrane",
    "nice" # Only if Australian adaptation noted
]

REJECTED_SOURCES = [
    "uptodate",
    "american college",
    "american heart association",
    "cdc", "centers for disease control",
    "wikipedia",
    "webmd",
    "healthline"
]

def validate_source_australian(document_metadata):
    """
    Validate that source is from approved Australian medical authority.

    Args:
        document_metadata: Dict with keys "source", "title", "url"

    Returns:
        ValidationResult
    """
    source_text = (
        document_metadata.get("source", "") + " " +
        document_metadata.get("title", "") + " " +
        document_metadata.get("url", "")
    ).lower()

    # Check for rejected sources FIRST (takes priority)
    for rejected in REJECTED_SOURCES:
        if rejected in source_text:
            return ValidationResult(
                passed=False,
                reason=f"Rejected source detected: {rejected}. Must use Australian clinical guidelines.",
                source=document_metadata.get("source"),
                action="REJECT - Non-Australian source"
            )

    # Check for approved Australian sources
    for approved in APPROVED_AUSTRALIAN_SOURCES:
        if approved in source_text:
            return ValidationResult(
                passed=True,
                source=document_metadata.get("source"),
                tier=get_source_tier(approved),
                action="APPROVED"
            )

    # If no match found, reject
    return ValidationResult(
        passed=False,
        reason="Source not in approved Australian medical sources list",
        source=document_metadata.get("source"),
        action="REJECT - Unknown source, manual review required"
    )

def get_source_tier(source):
    tier1 = ["therapeutic guidelines", "etg", "amh", "racgp", "ranzcog", "nhmrc", "nsw health", "queensland health"]
    tier2 = ["amc", "ahpra", "pbs", "nps medicinewise", "australian resuscitation"]
    tier3 = ["who", "cochrane", "nice"]

    if any(t1 in source for t1 in tier1):
        return 1
    elif any(t2 in source for t2 in tier2):
        return 2
    elif any(t3 in source for t3 in tier3):
        return 3
    else:
        return None
```

---

## 4. Guideline Recency Requirements

### Maximum Age: 2 Years

**Rationale**: Medical evidence evolves rapidly. Guidelines >2 years old may contain outdated recommendations.

**Exceptions**:
- Foundational anatomy/physiology (doesn't change)
- Historical medical cases (for context)
- Explicitly labeled "current as of [date]" and validated as still accurate

**Implementation**:

```python
from datetime import datetime, timedelta

def validate_guideline_recency(document_metadata):
    """
    Validate that guideline is ≤2 years old.

    Args:
        document_metadata: Dict with key "publication_date" (ISO format: YYYY-MM-DD)

    Returns:
        ValidationResult
    """
    pub_date_str = document_metadata.get("publication_date")

    if not pub_date_str:
        return ValidationResult(
            passed=False,
            reason="No publication date found in metadata",
            action="REJECT - Cannot verify recency"
        )

    try:
        pub_date = datetime.strptime(pub_date_str, "%Y-%m-%d")
    except ValueError:
        return ValidationResult(
            passed=False,
            reason=f"Invalid publication date format: {pub_date_str}",
            action="REJECT - Date parse error"
        )

    today = datetime.now()
    age_days = (today - pub_date).days
    age_years = age_days / 365.25

    if age_years > 2:
        return ValidationResult(
            passed=False,
            reason=f"Guideline too old: {age_years:.1f} years (published {pub_date_str}). Must be ≤2 years.",
            age_years=age_years,
            action="REJECT - Outdated guideline"
        )

    return ValidationResult(
        passed=True,
        age_years=age_years,
        publication_date=pub_date_str,
        action="APPROVED - Guideline current"
    )
```

**Special Handling for Updated Guidelines**:

If guideline has been updated:
- Use ONLY the latest version
- Mark older versions as "SUPERSEDED" in vector DB
- Do NOT retrieve superseded versions

Example:
- eTG Cardiovascular (2024 edition): ✅ Use this
- eTG Cardiovascular (2021 edition): ❌ Do not use (superseded)

---

## 5. Citation Requirements

### Complete Citation Format

Every piece of clinical content generated MUST include:

1. **Source Name**: Full name of guideline/resource
2. **Section/Page**: Specific location within source
3. **Publication Date**: YYYY or YYYY-MM-DD format
4. **Edition/Version**: If applicable

**Example Citation Formats**:

✅ **Correct**:
> "Therapeutic Guidelines: Cardiovascular, Section 5.2.1 'Acute Coronary Syndrome Management' (2024 edition)"

✅ **Correct**:
> "Australian Medicines Handbook, Chapter 8 'Cardiovascular Drugs', p.245 (2024)"

✅ **Correct**:
> "RACGP Red Book, Part 2.3 'Adult Health Checks', p.87 (2023)"

❌ **Incorrect** (too vague):
> "Therapeutic Guidelines"

❌ **Incorrect** (no section):
> "AMH (2024)"

❌ **Incorrect** (no date):
> "RACGP Red Book, Part 2.3"

### Implementation

```python
def validate_citation_completeness(citation):
    """
    Validate that citation includes all required components.

    Args:
        citation: Dict with keys "source", "section", "page", "publication_date", "edition"

    Returns:
        ValidationResult
    """
    required_fields = ["source", "publication_date"]
    optional_but_recommended = ["section", "page", "edition"]

    # Check required fields
    missing_required = [field for field in required_fields if not citation.get(field)]
    if missing_required:
        return ValidationResult(
            passed=False,
            reason=f"Missing required citation fields: {', '.join(missing_required)}",
            action="REJECT - Incomplete citation"
        )

    # Check at least ONE of: section, page, or edition
    has_location = any(citation.get(field) for field in optional_but_recommended)
    if not has_location:
        return ValidationResult(
            passed=False,
            reason="Citation must include at least one of: section, page, or edition for specificity",
            action="REJECT - Citation too vague"
        )

    # Validate publication date format
    pub_date = citation.get("publication_date")
    if not re.match(r'^\d{4}(-\d{2}-\d{2})?$', pub_date):
        return ValidationResult(
            passed=False,
            reason=f"Invalid publication date format: {pub_date}. Must be YYYY or YYYY-MM-DD",
            action="REJECT - Invalid date format"
        )

    # Format citation string
    citation_str = format_citation(citation)

    return ValidationResult(
        passed=True,
        citation_formatted=citation_str,
        action="APPROVED - Complete citation"
    )

def format_citation(citation):
    """Format citation according to Australian medical standards."""
    parts = [citation["source"]]

    if citation.get("section"):
        parts.append(f"Section {citation['section']}")

    if citation.get("page"):
        parts.append(f"p.{citation['page']}")

    if citation.get("edition"):
        parts.append(f"({citation['edition']})")
    elif citation.get("publication_date"):
        parts.append(f"({citation['publication_date']})")

    return ", ".join(parts)
```

---

## 6. Australian Terminology Validation

### Mandatory Australian Medical Terminology

**Drug Names**:

| ❌ American | ✅ Australian | Drug Class |
|-------------|--------------|------------|
| Acetaminophen | **Paracetamol** | Analgesic |
| Albuterol | **Salbutamol** | Beta-2 agonist |
| Epinephrine | **Adrenaline** | Emergency medication |
| Tylenol | **Panadol** or paracetamol | Brand vs generic |

**Medical Terms**:

| ❌ American | ✅ Australian | Context |
|-------------|--------------|---------|
| Fall (season) | **Autumn** | Seasonal variations |
| ER | **ED** (Emergency Department) | Hospital department |
| Primary care physician | **GP** (General Practitioner) | Preferred term |
| Internist | **Physician** or General Physician | Specialist |
| Call 911 | **Call 000** | CRITICAL ERROR if wrong |

**Healthcare System Terms**:

| ❌ American | ✅ Australian | Context |
|-------------|--------------|---------|
| Health insurance | **Medicare** | Public health system |
| Copay | **Gap fee** or co-payment | Out-of-pocket costs |
| Prescription coverage | **PBS** (Pharmaceutical Benefits Scheme) | Subsidized medications |

### Implementation

```python
AMERICAN_AUSTRALIAN_MAP = {
    # Drug names
    "acetaminophen": "paracetamol",
    "albuterol": "salbutamol",
    "epinephrine": "adrenaline",
    "tylenol": "panadol",

    # Medical terms
    "call 911": "call 000",
    "911": "000",
    "er ": "ed ",
    "emergency room": "emergency department",
    "primary care physician": "gp",
    "pcp": "gp",

    # Healthcare system
    "health insurance": "medicare",
    "copay": "gap fee",
    "prescription coverage": "pbs"
}

def validate_australian_terminology(generated_content):
    """
    Check for American terminology and flag/replace with Australian equivalents.

    Args:
        generated_content: String of generated clinical content

    Returns:
        ValidationResult with flagged terms and suggested corrections
    """
    content_lower = generated_content.lower()
    flagged_terms = []

    for american_term, australian_term in AMERICAN_AUSTRALIAN_MAP.items():
        if american_term in content_lower:
            # Critical errors (auto-fail)
            if american_term in ["911", "call 911"]:
                return ValidationResult(
                    passed=False,
                    reason=f"CRITICAL: Used American emergency number '{american_term}'. Must use '000' in Australia.",
                    flagged_terms=[{"american": american_term, "australian": australian_term, "critical": True}],
                    action="REJECT - Critical terminology error"
                )

            # Non-critical but must be corrected
            flagged_terms.append({
                "american": american_term,
                "australian": australian_term,
                "critical": False
            })

    if flagged_terms:
        return ValidationResult(
            passed=False,
            reason=f"American terminology detected. Must use Australian medical terminology.",
            flagged_terms=flagged_terms,
            action="REJECT - Replace with Australian terms and regenerate"
        )

    return ValidationResult(
        passed=True,
        action="APPROVED - Australian terminology compliant"
    )
```

---

## 7. Multi-Stage Validation Pipeline

### Complete Validation Workflow

```python
class RAGValidator:
    """
    Multi-stage validation pipeline for RAG-generated clinical content.
    """

    def validate_retrieval(self, query, retrieval_results):
        """
        Stage 1: Validate retrieved documents before generation.

        Returns:
            ValidationResult (if failed, do NOT proceed to generation)
        """
        # Step 1: Check confidence threshold
        confidence_result = validate_confidence(retrieval_results)
        if not confidence_result.passed:
            return confidence_result

        # Step 2: Validate sources are Australian
        for document, score in retrieval_results:
            source_result = validate_source_australian(document.metadata)
            if not source_result.passed:
                return source_result

        # Step 3: Check guideline recency
        for document, score in retrieval_results:
            recency_result = validate_guideline_recency(document.metadata)
            if not recency_result.passed:
                return recency_result

        # Step 4: Validate citations are complete
        for document, score in retrieval_results:
            citation = extract_citation(document.metadata)
            citation_result = validate_citation_completeness(citation)
            if not citation_result.passed:
                return citation_result

        # All checks passed
        return ValidationResult(
            passed=True,
            stage="retrieval",
            action="PROCEED to generation",
            metadata={
                "confidence": confidence_result.confidence,
                "sources": [doc.metadata["source"] for doc, _ in retrieval_results],
                "publication_dates": [doc.metadata["publication_date"] for doc, _ in retrieval_results]
            }
        )

    def validate_generation(self, generated_content, citations):
        """
        Stage 2: Validate generated content after LLM generation.

        Returns:
            ValidationResult (if failed, reject content and log error)
        """
        # Step 1: Check Australian terminology
        terminology_result = validate_australian_terminology(generated_content)
        if not terminology_result.passed:
            return terminology_result

        # Step 2: Verify citations included
        if not citations:
            return ValidationResult(
                passed=False,
                reason="No citations included in generated content",
                action="REJECT - Citations mandatory"
            )

        # Step 3: Validate each citation
        for citation in citations:
            citation_result = validate_citation_completeness(citation)
            if not citation_result.passed:
                return citation_result

        # Step 4: Content-specific validation (MCQ, OSCE, etc.)
        content_type = detect_content_type(generated_content)
        if content_type == "MCQ":
            mcq_result = validate_mcq_structure(generated_content)
            if not mcq_result.passed:
                return mcq_result

        # All checks passed
        return ValidationResult(
            passed=True,
            stage="generation",
            action="APPROVED for user presentation",
            metadata={
                "content_type": content_type,
                "citations_count": len(citations),
                "australian_terminology": True
            }
        )
```

---

## 8. Error Handling & Logging

### Rejection Logging

All rejected content MUST be logged for review:

```python
def log_validation_failure(validation_result, query, context):
    """
    Log validation failures for audit and improvement.

    Args:
        validation_result: ValidationResult with failure details
        query: Original user query
        context: Additional context (user_id, content_type, etc.)
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": context.get("user_id"),
        "query": query,
        "failure_stage": validation_result.stage,
        "failure_reason": validation_result.reason,
        "confidence": validation_result.confidence,
        "sources": validation_result.sources,
        "action_taken": validation_result.action,
        "flagged_terms": validation_result.flagged_terms if hasattr(validation_result, "flagged_terms") else None
    }

    # Log to database
    db.validation_failures.insert(log_entry)

    # Alert if critical error (e.g., "911" detected)
    if hasattr(validation_result, "critical") and validation_result.critical:
        send_alert_to_clinical_team(log_entry)
```

### User-Facing Error Messages

When validation fails, return helpful error messages:

```python
def get_user_error_message(validation_result):
    """
    Convert technical validation failure to user-friendly message.
    """
    if "confidence" in validation_result.reason.lower():
        return "We couldn't find enough reliable information in our knowledge base to answer this question accurately. Please try rephrasing or contact support."

    if "australian source" in validation_result.reason.lower():
        return "This content could not be generated using Australian clinical guidelines. Please contact support if you believe this is an error."

    if "outdated" in validation_result.reason.lower():
        return "The available guidelines for this topic are outdated. We're working on updating our knowledge base. Please check back soon."

    if "terminology" in validation_result.reason.lower():
        return "There was an error in medical terminology. Our team has been notified and will fix this shortly."

    # Generic fallback
    return "We couldn't generate accurate clinical content for this request. Our team has been notified. Please try again later or contact support."
```

---

## 9. Quality Assurance & Testing

### Test Cases for Validation

```python
# Test Case 1: Low confidence should reject
def test_low_confidence_rejection():
    retrieval_results = [
        (Document("Some text"), 0.45)  # Below 0.65 threshold
    ]
    result = validate_confidence(retrieval_results)
    assert result.passed == False
    assert "Confidence too low" in result.reason

# Test Case 2: American source should reject
def test_american_source_rejection():
    metadata = {
        "source": "UpToDate: Acute Coronary Syndrome",
        "publication_date": "2024-01-01"
    }
    result = validate_source_australian(metadata)
    assert result.passed == False
    assert "Rejected source" in result.reason

# Test Case 3: Outdated guideline should reject
def test_outdated_guideline_rejection():
    metadata = {
        "source": "Therapeutic Guidelines: Cardiovascular",
        "publication_date": "2020-01-01"  # >2 years old
    }
    result = validate_guideline_recency(metadata)
    assert result.passed == False
    assert "Guideline too old" in result.reason

# Test Case 4: American terminology should reject
def test_american_terminology_rejection():
    content = "Give acetaminophen 500mg for pain. If severe, call 911."
    result = validate_australian_terminology(content)
    assert result.passed == False
    assert "911" in [term["american"] for term in result.flagged_terms]

# Test Case 5: Incomplete citation should reject
def test_incomplete_citation_rejection():
    citation = {
        "source": "Therapeutic Guidelines",
        # Missing: section, page, publication_date
    }
    result = validate_citation_completeness(citation)
    assert result.passed == False
    assert "Missing required citation fields" in result.reason
```

---

## 10. Continuous Improvement

### Monitoring Metrics

Track validation performance:

| Metric | Target | Current | Action if Below Target |
|--------|--------|---------|----------------------|
| Validation pass rate | ≥80% | TBD | Review query patterns, expand knowledge base |
| Average confidence | ≥0.75 | TBD | Add more sources to vector DB |
| American source attempts | <5% | TBD | Improve source filtering |
| Outdated guideline hits | <10% | TBD | Update knowledge base quarterly |
| User error rate | <15% | TBD | Improve error messages, add FAQ |

### Quarterly Knowledge Base Updates

Every 3 months:
1. Review all Australian clinical guidelines for updates
2. Mark superseded versions as "DEPRECATED"
3. Add latest editions to vector DB
4. Re-run validation tests
5. Update this specification document if rules change

---

**Document Status**: ✅ Ready for Clinical Advisor Review
**Created**: 2026-02-15
**Next Review**: 2026-05-15 (Quarterly)
**Owner**: Backend Development Team

---

**END OF DOCUMENT**
