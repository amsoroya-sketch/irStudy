# Track 3: Quality Assurance & Validation
**Duration:** Weeks 1-20
**Goal:** 100% automated RAG citation validation with >90% auto-approval
**Status:** 🟡 WEEK 1 IN PROGRESS

---

## Overview

This track ensures all generated content meets quality standards through:
- **Automated RAG citation validation** (QA-003 upgrade)
- **Three-tier confidence scoring** (auto-approve, LLM verify, reject)
- **100% automation** (no human resources required for validation)
- **Real-time feedback loops** to content generation

---

## Quality Assurance Agents

### QA-001: Medical Accuracy Validator
**Status:** ✅ OPERATIONAL (Existing)

**Responsibilities:**
- Validate clinical accuracy against Australian guidelines
- Check medication names (Australian vs. US)
- Verify units (mmol/L vs. mg/dL)
- Confirm healthcare system terminology (ED vs. ER, GP vs. PCP)

**Validation Checks:**
```python
class MedicalAccuracyValidator:
    """
    QA-001: Validate clinical accuracy
    """

    def validate_mcq(self, mcq: dict) -> dict:
        """
        Validate medical accuracy

        Checks:
        1. Clinical accuracy (guideline-compliant)
        2. Australian context (medications, units, system)
        3. Question clarity (unambiguous)
        4. Appropriate difficulty level
        """

        checks = []

        # Check 1: Clinical accuracy
        checks.append(self._check_clinical_accuracy(mcq))

        # Check 2: Australian context
        checks.append(self._check_australian_context(mcq))

        # Check 3: Question clarity
        checks.append(self._check_question_clarity(mcq))

        # Check 4: Difficulty appropriateness
        checks.append(self._check_difficulty(mcq))

        # Aggregate
        passed = all(check['passed'] for check in checks)
        issues = [c['issue'] for c in checks if not c['passed']]

        return {
            'agent': 'QA-001',
            'passed': passed,
            'issues': issues,
            'checks': checks
        }
```

---

### QA-002: End-to-End Testing Agent
**Status:** ✅ OPERATIONAL (Existing)

**Responsibilities:**
- Integration testing of content generation pipeline
- Performance testing (generation speed, RAG query latency)
- Load testing (can system handle 100+ MCQs/hour?)

**Test Scenarios:**
1. **End-to-end MCQ generation:**
   - Topic → RAG query → MCQ generation → QA validation → Final output
   - Target: <10 seconds per MCQ

2. **OSCE module generation:**
   - Topic → Scenario creation → Marking rubric → Citations → Validation
   - Target: <30 seconds per module

3. **Load testing:**
   - Generate 100 MCQs concurrently
   - RAG query latency remains <500ms
   - QA validation remains <6s per MCQ

---

### QA-003: Automated RAG Citation Validation
**Status:** 🟡 WEEK 1-2 UPGRADE IN PROGRESS

**Current State (Before Upgrade):**
- Performance testing agent
- Manual citation validation

**Target State (After Upgrade):**
- **Automated RAG citation validation**
- **Three-tier confidence scoring**
- **100% automation (no human review for Tier 1)**
- **Real-time validation in generation pipeline**

**Upgrade Timeline:** See [QA_003_UPGRADE_PLAN.md](../QA_003_UPGRADE_PLAN.md)

---

## Three-Tier Validation System

### Architecture

```
Input: Generated MCQ with citations
         ↓
┌────────────────────────────────────┐
│   QA-003: RAG Citation Validator   │
└────────────────────────────────────┘
         ↓
    For each citation:
    1. Query RAG (top 5 matches)
    2. Calculate cosine similarity
    3. Verify page numbers
    4. Calculate confidence score
         ↓
┌────────────────────────────────────┐
│     Confidence Score (0.0-1.0)     │
└────────────────────────────────────┘
         ↓
    ┌─────────┬─────────┬─────────┐
    │  >0.90  │0.75-0.90│  <0.75  │
    │  TIER 1 │  TIER 2 │  TIER 3 │
    └─────────┴─────────┴─────────┘
         ↓         ↓         ↓
┌──────────┐ ┌─────────┐ ┌────────┐
│   AUTO   │ │   LLM   │ │ REJECT │
│ APPROVE  │ │ VERIFY  │ │        │
└──────────┘ └─────────┘ └────────┘
      ↓           ↓           ↓
   PASS ✅    PASS/FAIL  REGENERATE
```

### Tier 1: Auto-Approve (Confidence >0.90)
**Target:** 70%+ of citations
**Action:** Automatic approval, no human review

**Criteria:**
- RAG cosine similarity >0.90
- Page numbers match exactly
- Citation text found in source
- Australian guideline (primary source)

**Example:**
```json
{
  "citation": "RANZCP Clinical Practice Guidelines: Mood Disorders, p.45-47 (2023)",
  "rag_match": {
    "title": "RANZCP CPG Mood Disorders 2023",
    "content": "First-line treatment for major depression is SSRI...",
    "page": "45-47",
    "similarity": 0.94
  },
  "confidence": 0.94,
  "tier": 1,
  "action": "AUTO_APPROVE"
}
```

---

### Tier 2: LLM Verification (Confidence 0.75-0.90)
**Target:** 20% of citations
**Action:** LLM reviews, decides approve/reject

**Criteria:**
- RAG cosine similarity 0.75-0.90
- Page numbers close but not exact (+/- 2 pages)
- Paraphrased citation text

**LLM Verification Process:**
```python
class LLMCitationVerifier:
    """
    Tier 2: Use LLM to verify ambiguous citations
    """

    def verify_citation(self, citation: str, rag_match: dict) -> dict:
        """
        Use Llama3.1 to verify citation accuracy

        Prompt:
        "You are a medical citation validator. Does this citation
        accurately reference this source?

        Citation: [citation text]
        Source: [RAG match content, page]

        Answer: {'verified': true/false, 'explanation': '...'}"
        """

        prompt = self._build_prompt(citation, rag_match)
        response = self.llm.generate(prompt)
        result = json.loads(response)

        return {
            'verified': result['verified'],
            'explanation': result['explanation'],
            'llm_confidence': result.get('confidence', 0.8)
        }
```

**Example:**
```json
{
  "citation": "Therapeutic Guidelines: Psychotropic, Chapter 3 (2024)",
  "rag_match": {
    "title": "eTG Psychotropic 2024",
    "content": "SSRIs are first-line for depression...",
    "page": "88",  // Citation says "Chapter 3", match is page 88
    "similarity": 0.87
  },
  "confidence": 0.87,
  "tier": 2,
  "llm_verification": {
    "verified": true,
    "explanation": "Chapter 3 corresponds to pages 85-92, match is accurate"
  },
  "action": "LLM_APPROVE"
}
```

---

### Tier 3: Reject (Confidence <0.75)
**Target:** <10% of citations
**Action:** Reject, regenerate citation

**Criteria:**
- RAG cosine similarity <0.75 (poor match)
- Page numbers missing or clearly wrong
- Citation not found in database

**Action:**
1. Flag citation as incorrect
2. Request MED-XXX agent to regenerate
3. Re-query RAG with refined search
4. Re-validate new citation

**Example:**
```json
{
  "citation": "Australian Depression Guidelines 2024, p.100",
  "rag_match": {
    "title": "RANZCP CPG Mood Disorders 2023",  // Different document
    "content": "...",
    "page": "45",  // Different page
    "similarity": 0.62  // Low similarity
  },
  "confidence": 0.62,
  "tier": 3,
  "action": "REJECT",
  "recommendation": "Citation not found in RAG database. Please verify source and page number."
}
```

---

## Validation Workflow

### Real-Time Validation (Integrated into Generation)

```python
# Step 1: Generate MCQ (MED-XXX agent)
mcq = med_agent.generate_mcq(topic='depression', difficulty='medium')

# Step 2: Immediate QA-003 validation
validation_result = qa_003.validate_mcq(mcq)

# Step 3: Handle result
if validation_result['recommendation'] == 'approve':
    # Tier 1: Auto-approved
    mcq['metadata']['qa_validated'] = True
    mcq['metadata']['qa_confidence'] = validation_result['overall_confidence']
    save_mcq(mcq)

elif validation_result['recommendation'] == 'llm_verify':
    # Tier 2: LLM verification
    llm_result = llm_verifier.verify_citations(mcq)

    if llm_result['all_verified']:
        mcq['metadata']['qa_validated'] = True
        mcq['metadata']['qa_confidence'] = llm_result['confidence']
        save_mcq(mcq)
    else:
        # LLM rejected, regenerate
        mcq = med_agent.regenerate_mcq(mcq, issues=llm_result['issues'])

else:
    # Tier 3: Rejected, regenerate
    mcq = med_agent.regenerate_mcq(mcq, issues=validation_result['issues'])
```

---

## Week-by-Week QA Implementation

### Week 1: QA-003 Design + Initial Implementation
**Status:** 🟡 IN PROGRESS

**Tasks:**
- [ ] Design RAG validation workflow
- [ ] Design three-tier confidence scoring
- [ ] Implement RAGCitationValidator (100 LOC)
- [ ] Implement PageNumberVerifier (30 LOC)
- [ ] Test on 20 sample MCQs

**Success Criteria:**
- ✅ Can validate 20 MCQs with citations
- ✅ Confidence scores align with manual review
- ✅ <5 seconds per MCQ validation

---

### Week 2: QA-003 Complete Implementation
**Status:** ⏳ PENDING

**Tasks:**
- [ ] Implement LLMCitationVerifier (80 LOC)
- [ ] Implement CitationSummaryGenerator (60 LOC)
- [ ] Integration testing (100 MCQs end-to-end)
- [ ] Performance testing (target: <6s per MCQ)

**Success Criteria:**
- ✅ 100 MCQs validated successfully
- ✅ >90% auto-approval rate (Tier 1)
- ✅ LLM verification accuracy >90%
- ✅ <6 seconds average validation time

---

### Week 3+: Production Validation
**Status:** ⏳ PENDING

**Scale Targets:**
- Week 3: 400 MCQs validated
- Week 4: 600 MCQs validated
- Week 5-10: 3,000+ MCQs validated
- Week 11-16: 2,000+ MCQs validated

**Quality Monitoring:**
- Daily auto-approval rate tracking
- Weekly rejection pattern analysis
- Monthly confidence threshold tuning

---

## Quality Metrics Dashboard

### Week 1 Targets
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Auto-approval rate** | >80% | - | 🟡 Week 1 |
| **LLM verification rate** | 15-20% | - | 🟡 Week 1 |
| **Rejection rate** | <10% | - | 🟡 Week 1 |
| **Validation speed** | <5s/MCQ | - | 🟡 Week 1 |
| **Page number accuracy** | >95% | - | 🟡 Week 1 |

### Week 2 Targets
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **Auto-approval rate** | >90% | - | ⏳ Week 2 |
| **LLM verification accuracy** | >90% | - | ⏳ Week 2 |
| **Validation speed** | <6s/MCQ | - | ⏳ Week 2 |
| **Test coverage** | >80% | - | ⏳ Week 2 |

### Production Targets (Week 3+)
| Metric | Target | Status |
|--------|--------|--------|
| **Auto-approval rate** | >92% | ⏳ Ongoing |
| **Citation confidence** | >0.92 avg | ⏳ Ongoing |
| **False positive rate** | <2% | ⏳ Monitored |
| **False negative rate** | <3% | ⏳ Monitored |

---

## Manual Review Sampling

### Week 1-2: 20% Sample
**Purpose:** Validate automated QA accuracy

**Process:**
1. QA-003 validates 100 MCQs
2. Random sample 20 MCQs (20%)
3. Expert manual review
4. Compare QA-003 decisions vs. expert decisions
5. Calculate accuracy metrics

**Acceptance Criteria:**
- Agreement >90% (QA-003 vs. expert)
- If <90%, adjust confidence thresholds

---

### Week 3-10: 10% Sample
**Purpose:** Ongoing quality monitoring

**Process:**
1. Weekly random sample (100 MCQs → 10 reviewed)
2. Expert review for clinical accuracy and citation accuracy
3. Calculate running agreement rate
4. Flag systematic errors for prompt refinement

---

### Week 11+: 5% Sample
**Purpose:** Spot checks

**Process:**
- Monthly random sample (500 MCQs → 25 reviewed)
- Focus on edge cases and low-confidence MCQs
- Continuous improvement feedback loop

---

## Error Pattern Analysis

### Common Citation Errors (Week 1 Expected)

**Error Type 1: Page Number Mismatch (20-30%)**
- **Issue:** Citation says "p.45" but RAG has "p.46"
- **Cause:** Different editions, off-by-one errors
- **Solution:** +/- 2 page tolerance, LLM verification

**Error Type 2: Paraphrased Citations (10-15%)**
- **Issue:** Citation wording different from source
- **Cause:** Agent rewrites citation text
- **Solution:** Semantic similarity >0.75, LLM verification

**Error Type 3: Missing Citations (5-10%)**
- **Issue:** Clinical claim has no supporting citation
- **Cause:** Agent skips RAG query
- **Solution:** Enforce minimum 2 citations per MCQ

**Error Type 4: Wrong Source (5%)**
- **Issue:** US guideline instead of Australian
- **Cause:** RAG returns US source as top match
- **Solution:** Filter by country='Australia', boost Australian sources

**Error Type 5: Outdated Guidelines (<5%)**
- **Issue:** Citation is >5 years old
- **Cause:** RAG database has old version
- **Solution:** Flag for manual review if >5 years

---

## Continuous Improvement Loop

### Weekly Cycle

```
Monday:
- Review previous week's QA metrics
- Identify rejection patterns
- Update validation prompts

Tuesday-Thursday:
- Run production validation
- Monitor auto-approval rate
- Flag anomalies

Friday:
- Weekly QA report
- Manual review sample (10%)
- Adjust confidence thresholds if needed
```

### Monthly Cycle

```
Week 1:
- Monthly QA metrics review
- Compare to targets (>90% auto-approval)

Week 2:
- Error pattern analysis
- Identify systematic issues

Week 3:
- Update MED-XXX agent prompts based on error patterns
- Retrain LLM verifier if needed

Week 4:
- Test improvements on 100 MCQ sample
- Measure improvement vs. baseline
```

---

## Integration with Content Generation (Track 2)

### Real-Time Feedback Loop

```python
# Generation loop with QA feedback
for i in range(100):  # Generate 100 MCQs
    # Generate
    mcq = med_agent.generate_mcq(topic, difficulty)

    # Validate
    validation = qa_003.validate_mcq(mcq)

    # Handle result
    if validation['recommendation'] == 'approve':
        save_mcq(mcq)
        success_count += 1

    elif validation['recommendation'] == 'llm_verify':
        llm_result = llm_verifier.verify(mcq)
        if llm_result['verified']:
            save_mcq(mcq)
            success_count += 1
        else:
            # Feedback to agent
            med_agent.learn_from_error(llm_result['issues'])
            i -= 1  # Retry this MCQ

    else:  # Rejected
        # Feedback to agent
        med_agent.learn_from_error(validation['issues'])
        i -= 1  # Retry this MCQ

# Calculate success rate
success_rate = success_count / 100
if success_rate < 0.90:
    print(f"Warning: Success rate {success_rate:.1%} below target 90%")
```

---

## Success Criteria

### Phase A (End of Week 4)
- ✅ QA-003 operational (300+ LOC)
- ✅ >90% auto-approval rate achieved
- ✅ 1,500 MCQs validated
- ✅ <6s average validation time

### Phase B (End of Week 10)
- ✅ 5,000 MCQs validated
- ✅ >92% auto-approval rate
- ✅ <5s average validation time
- ✅ 100% citation coverage

### Phase C (End of Week 16)
- ✅ All content validated (5,000+ MCQs + 164 OSCE)
- ✅ >94% auto-approval rate
- ✅ <4s average validation time
- ✅ 100% Australian compliance

---

## Risk Management

### Risk 1: Auto-Approval Rate Too Low (<90%)
**Impact:** Bottleneck in content generation, manual review required
**Mitigation:**
- Adjust confidence thresholds (lower from 0.90 to 0.85)
- Improve RAG query prompts
- Fine-tune embedding model
**Contingency:** Increase LLM verification capacity

### Risk 2: False Positives (Approve Incorrect Citations)
**Impact:** Low-quality content published
**Mitigation:**
- 10-20% manual review sampling in Week 1-4
- Stringent page number verification
- LLM verification for Tier 2
**Contingency:** Increase manual review to 20% if false positive rate >5%

### Risk 3: Validation Speed Too Slow (>6s/MCQ)
**Impact:** Generation pipeline slows down
**Mitigation:**
- Optimize RAG query (batch processing)
- Cache common citations
- Parallelize validation
**Contingency:** Scale Qdrant to multiple instances

---

## Related Documents
- [QA-003 Upgrade Plan](../QA_003_UPGRADE_PLAN.md)
- [Track 2: Content Generation](TRACK_02_CONTENT_GENERATION.md)
- [Week 1 Execution Plan](../weekly/WEEK_01_EXECUTION.md)
- [RAG Integration Status](../RAG_INTEGRATION_STATUS.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟡 WEEK 1 IN PROGRESS (QA-003 design + implementation)
**Next Milestone:** End of Week 2 (QA-003 complete, >90% auto-approval)
**Final Milestone:** End of Week 16 (All content validated, >94% auto-approval)
