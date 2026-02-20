# ADR-001: AMC 15-Mark OSCE Rubric Design for Automated Scoring

**Status**: ✅ Approved
**Date**: 2026-02-15
**Decision Makers**: Project Manager Coordinator, ABA Clinical Expert
**Stakeholders**: Backend developers, Clinical Advisor, QA engineers

---

## Context

The irStudy platform requires an automated OSCE (Objective Structured Clinical Examination) scoring system that can evaluate student responses using the AMC (Australian Medical Council) 15-mark rubric. The system must:

1. Provide consistent, fair scoring aligned with AMC Clinical Examination standards
2. Support automated NLP-based scoring validation
3. Include behavioral anchors for machine-readable success patterns
4. Comply with Australian medical education standards (not ICRP or US-based)
5. Detect critical errors that trigger automatic failure (patient safety violations)
6. Enable expert review and inter-rater reliability testing

---

## Decision

We will implement a **comprehensive 5-domain AMC rubric** with granular behavioral anchors for each mark level:

### Domain Structure

| Domain | Marks | Weight | Critical? |
|--------|-------|--------|-----------|
| Communication Skills | 0-3 | 20% | Yes |
| Clinical Reasoning | 0-4 | 27% | Yes |
| Information Gathering | 0-3 | 20% | Yes |
| Management Plan | 0-3 | 20% | Station-dependent |
| Professionalism & Ethics | 0-2 | 13% | Yes |
| **TOTAL** | **15** | **100%** | - |

### Pass/Fail Logic

**Pass Criteria** (ALL must be met):
- Total score ≥9/15 (60%)
- Minimum domain scores met:
  - Communication ≥1
  - Clinical Reasoning ≥2
  - Information Gathering ≥2
  - Professionalism ≥1
- No critical errors

**Borderline**: 8/15 (may pass if strong performance in other stations)

**Auto-Fail** (overrides total score):
- Patient safety violations (e.g., sends STEMI patient home)
- Professional misconduct (discriminatory comments)
- Critical cultural safety failures (refuses interpreter for CALD patient)
- Uses American emergency number "911" instead of "000" (CRITICAL ERROR)

### Behavioral Anchors

Each mark level includes:
- **Observable behaviors**: Specific actions/phrases that earn marks
- **NLP detection patterns**: Machine-readable patterns for automated scoring
- **Example quotes**: Student responses demonstrating that mark level
- **Common mistakes**: What loses marks at that level

**Example (Communication 3/3)**:
```
Observable Behaviors:
- Introduces self with name and role clearly
- Uses ≥60% open-ended questions
- Shows empathy (≥3 empathy phrases detected)
- Checks understanding regularly
- No medical jargon without explanation

NLP Patterns:
- Introduction detected in first 100 words
- Empathy phrases: "must be [emotion]", "I can understand"
- Open question patterns: "Can you tell me", "What was", "How did"
- Understanding checks: "Does that make sense", "Any questions"
- Max 1 unexplained medical term

Example Quotes:
- "That must be really frightening when you felt the chest pain"
- "Can you tell me more about what happened?"
- "Does that make sense so far?"
```

### Australian-Specific Requirements

**Mandatory Terminology**:
- Paracetamol (NOT acetaminophen)
- Salbutamol (NOT albuterol)
- Adrenaline (NOT epinephrine)
- Call 000 (NOT 911 - CRITICAL if violated)

**Cultural Competence**:
- Aboriginal/Torres Strait Islander patients: Offer Aboriginal Health Worker, acknowledge social determinants
- CALD patients: Offer interpreter (TIS 131 450), respect cultural beliefs
- No stereotyping or judgmental language

**Clinical Guidelines**:
- eTG (Therapeutic Guidelines) - primary reference
- AMH (Australian Medicines Handbook)
- RACGP, RANZCOG, NHMRC guidelines
- State health protocols (NSW, QLD, VIC Health)

---

## Rationale

### Why 5 Domains (Not More/Less)?

**Evidence**: AMC Clinical Examination assessment framework uses these 5 core competencies as foundational to medical practice in Australia.

**Alternatives Considered**:
- ❌ **More domains** (7-8): Rejected - too granular, difficult to score consistently, over-complicates rubric
- ❌ **Fewer domains** (3): Rejected - insufficient granularity to distinguish competency levels
- ✅ **5 domains**: Optimal balance between granularity and usability

### Why Minimum Domain Scores?

**Problem**: Student could score 15/15 on Communication but 0/15 on Clinical Reasoning and still pass with 60% (9/15 total) if only total score counted.

**Solution**: Minimum domain scores ensure competency across ALL critical areas:
- Communication ≥1 (can communicate at basic level)
- Clinical Reasoning ≥2 (can formulate differential diagnosis)
- Information Gathering ≥2 (can take adequate history)
- Professionalism ≥1 (meets basic professional standards)

This prevents "compensation" where excellence in one domain masks dangerous deficiency in another.

### Why Auto-Fail Criteria?

**Patient Safety**: Some errors are so critical they override any other competencies demonstrated.

**Examples**:
- Sending STEMI patient home = potential patient death
- Discriminatory comments = professional misconduct
- Using "911" instead of "000" = wrong country protocol, could delay emergency response

**Justification**: Medical education has zero tolerance for patient safety violations. Better to fail a borderline student than graduate an unsafe practitioner.

### Why Behavioral Anchors?

**Traditional rubric problem**: Subjective scoring ("Did the student communicate well?")

**Behavioral anchor solution**: Objective criteria ("Did the student use ≥60% open-ended questions? Yes/No")

**Benefits**:
1. **Consistency**: Two examiners scoring same response get same result (inter-rater reliability κ ≥0.80)
2. **Automated scoring**: NLP algorithms can detect behavioral patterns
3. **Transparency**: Students know exactly what earns marks
4. **Defensibility**: Can defend scores with evidence (quotes from transcript)

### Why Australian-Specific Requirements?

**Legal Requirement**: AMC is the Australian medical registration authority. All assessment must align with AHPRA standards and Australian healthcare system.

**Patient Safety**: Using American medication names/doses or emergency protocols in Australia could harm patients:
- Acetaminophen 500mg ≠ Paracetamol 500mg (different formulations in some countries)
- Calling "911" in Australia delays emergency response (correct: 000)

**Cultural Competence**: Australia has unique cultural considerations (Aboriginal health, CALD populations) not found in US/UK exams.

---

## Consequences

### Positive

✅ **Consistency**: Behavioral anchors enable ≥85% agreement between automated and human scoring

✅ **Fairness**: Objective criteria reduce examiner bias

✅ **Transparency**: Students know exactly what's expected

✅ **Safety**: Auto-fail criteria prevent unsafe practitioners from passing

✅ **Cultural Competence**: Integrates Aboriginal and CALD patient considerations

✅ **Production-Ready**: Database schema, API specs, NLP patterns all included in rubric

### Negative

⚠️ **Complexity**: 15 mark levels × 5 domains = 75 behavioral anchor sets to document

⚠️ **Maintenance**: Rubric must be updated when AMC changes assessment criteria

⚠️ **Expert Effort**: Requires FRACGP-qualified reviewer to validate all scoring examples (200 hours for Golden Dataset)

⚠️ **Edge Cases**: Some responses may not fit neatly into mark levels (requires human review)

### Mitigation Strategies

**Complexity**:
- Created comprehensive documentation (800+ lines)
- Included 4 complete scoring examples (Excellent/Pass/Fail/Auto-Fail)
- Provided NLP detection patterns for developers

**Maintenance**:
- Annual review cycle documented
- Quarterly AMC guideline checks
- Version control for rubric updates

**Expert Effort**:
- 12-week Golden Dataset timeline planned
- Two expert reviewers for inter-rater reliability (κ ≥0.80 target)
- Clinical Advisor final approval

**Edge Cases**:
- Human review flag if automated score confidence <0.80
- Disputed scores escalated to Clinical Advisor
- Monthly review of borderline cases (7-9/15 scores)

---

## Implementation

### Database Schema

```sql
CREATE TABLE osce_scores (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    scenario_id UUID REFERENCES osce_scenarios(id),

    -- Domain scores
    communication_score INTEGER CHECK (communication_score BETWEEN 0 AND 3),
    clinical_reasoning_score INTEGER CHECK (clinical_reasoning_score BETWEEN 0 AND 4),
    information_gathering_score INTEGER CHECK (information_gathering_score BETWEEN 0 AND 3),
    management_score INTEGER CHECK (management_score BETWEEN 0 AND 3),
    professionalism_score INTEGER CHECK (professionalism_score BETWEEN 0 AND 2),

    -- Total score (auto-calculated by trigger)
    total_score INTEGER GENERATED ALWAYS AS (
        communication_score + clinical_reasoning_score +
        information_gathering_score + management_score +
        professionalism_score
    ) STORED,

    -- Pass/fail logic
    meets_minimum_thresholds BOOLEAN DEFAULT FALSE,
    has_critical_error BOOLEAN DEFAULT FALSE,
    overall_result VARCHAR(20) CHECK (overall_result IN ('PASS', 'BORDERLINE', 'FAIL')),

    -- Critical errors (JSONB for flexibility)
    critical_errors JSONB DEFAULT '[]',

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Trigger: Auto-calculate pass/fail
CREATE TRIGGER calculate_amc_pass_fail
BEFORE INSERT OR UPDATE ON osce_scores
FOR EACH ROW
EXECUTE FUNCTION calculate_amc_pass_fail();
```

### API Endpoint

```
POST /api/v1/osce/score
Request: { user_id, scenario_id, transcript }
Response: {
    scores: { communication: 3, clinical_reasoning: 4, ... },
    total_score: 14,
    overall_result: "PASS",
    justifications: { ... },
    citations: [ ... ]
}
```

### NLP Scoring Algorithm

```python
def score_communication(transcript):
    score = 0

    # Check introduction (first 100 words)
    if has_introduction(transcript[:100]):
        score += 0.5

    # Count empathy phrases
    empathy_count = count_empathy_phrases(transcript)
    if empathy_count >= 3:
        score += 0.5

    # Analyze question types
    open_questions = count_open_questions(transcript)
    total_questions = count_all_questions(transcript)
    if open_questions / total_questions >= 0.6:
        score += 0.5

    # Check understanding verification
    if has_understanding_checks(transcript):
        score += 0.5

    # Penalty for unexplained jargon
    unexplained_jargon = count_unexplained_medical_terms(transcript)
    if unexplained_jargon >= 3:
        score -= 0.5

    # Round to nearest valid score (0, 1, 2, 3)
    return round_to_valid_score(score, max=3)
```

---

## Validation

### Clinical Advisor Review

**Reviewer**: FRACGP-qualified GP with AMC examiner experience
**Timeline**: 5 business days
**Checklist**:
- [ ] All 5 domains align with AMC standards
- [ ] Behavioral anchors clinically accurate
- [ ] Auto-fail criteria appropriate (not overly punitive)
- [ ] Australian terminology comprehensive
- [ ] Cultural competence requirements appropriate
- [ ] Scoring examples realistic

### Golden Dataset Testing

**Method**: 200 scenarios × 6 response levels = 1,200 expert-scored responses

**Inter-Rater Reliability**:
- Two FRACGP reviewers score 20% sample (240 responses)
- Calculate Cohen's kappa (κ) for each domain
- Target: κ ≥0.80 (substantial agreement)
- If κ <0.80: Refine rubric and re-test

**Automated Scoring Validation**:
- Run NLP algorithm on all 1,200 responses
- Compare to expert scores
- Target: ≥85% agreement on pass/fail
- Target: ±1 mark accuracy on 75% of domain scores

---

## Alternatives Considered

### Alternative 1: Simple 5-Point Scale (0-5 total)

**Approach**: Single overall score (Fail=0-1, Poor=2, Borderline=3, Good=4, Excellent=5)

**Pros**:
- Simple to implement
- Quick to score
- Easy for students to understand

**Cons**:
- ❌ Insufficient granularity (can't distinguish competency areas)
- ❌ No domain-specific feedback
- ❌ Allows dangerous compensation (excellent communication masks unsafe clinical reasoning)
- ❌ Not aligned with AMC standards

**Rejected**: Insufficient for medical education assessment

### Alternative 2: Pass/Fail Only (Binary)

**Approach**: Student either passes or fails entire station (no numerical score)

**Pros**:
- Extremely simple
- Reduces scoring time
- Clear outcome

**Cons**:
- ❌ No feedback on areas for improvement
- ❌ Can't track progress over time
- ❌ Insufficient for high-stakes AMC preparation
- ❌ No borderline category

**Rejected**: Too blunt for formative assessment

### Alternative 3: US USMLE-Style Rubric

**Approach**: Use American medical licensing exam rubric

**Pros**:
- Well-established
- Extensive research validation
- Large body of practice materials

**Cons**:
- ❌ Not aligned with Australian medical practice
- ❌ American terminology (acetaminophen, 911, etc.)
- ❌ No cultural competence for Aboriginal/CALD patients
- ❌ Different healthcare system context
- ❌ Not accepted by AMC

**Rejected**: Must use Australian standards for Australian exam preparation

---

## Monitoring & Review

### Success Metrics

| Metric | Target | Measurement Method | Frequency |
|--------|--------|-------------------|-----------|
| **Inter-rater reliability (κ)** | ≥0.80 | Cohen's kappa on 20% sample | Annually |
| **Automated scoring accuracy** | ≥85% pass/fail | NLP vs expert comparison | Monthly |
| **Domain score accuracy** | ±1 mark on 75% | NLP vs expert comparison | Monthly |
| **Critical error detection** | 100% | Auto-fail cases identified | Per case |
| **Student satisfaction** | ≥4.0/5.0 | Post-exam survey | Per cohort |

### Annual Review Cycle

**Q1 (January)**:
- Review AMC Clinical Exam blueprint updates
- Check for guideline changes (eTG, AMH, RACGP)
- Update Australian terminology if needed

**Q2 (April)**:
- Analyze inter-rater reliability from past year
- Refine behavioral anchors if κ <0.80
- Update Golden Dataset with new scenarios

**Q3 (July)**:
- Review automated scoring accuracy
- Tune NLP algorithms if accuracy <85%
- Document edge cases

**Q4 (October)**:
- Clinical Advisor annual review
- Update rubric version (e.g., v1.0 → v1.1)
- Plan improvements for next year

### Trigger for Emergency Review

**Immediate review required if**:
- AMC changes assessment criteria mid-year
- Critical error false positive (student incorrectly failed)
- Critical error false negative (unsafe student incorrectly passed)
- Inter-rater reliability drops below 0.70
- Automated scoring accuracy drops below 75%

---

## References

1. **AMC Clinical Examination Handbook** (2024)
   https://www.amc.org.au - AMC assessment standards

2. **AHPRA Code of Conduct for Medical Practitioners** (2024)
   https://www.ahpra.gov.au - Professional standards

3. **Therapeutic Guidelines** (2024)
   https://www.tg.org.au - Australian clinical guidelines

4. **RACGP Standards** (2023)
   https://www.racgp.org.au - General practice standards

5. **Cohen's Kappa Calculator**
   Inter-rater reliability measurement method

6. **Educational Psychology Research**: Behaviorally Anchored Rating Scales (BARS)
   Academic foundation for behavioral anchor approach

---

## Related ADRs

- ADR-002: RAG Validation Specification (Australian source validation)
- ADR-003: Golden Dataset Design (200 scenarios for validation)
- ADR-004: Database Schema for OSCE Scoring (implementation details)

---

## Version History

| Version | Date | Changes | Approver |
|---------|------|---------|----------|
| 1.0 | 2026-02-15 | Initial rubric design | PM Coordinator + ABA Clinical Expert |
| 1.1 | Pending | After Clinical Advisor approval | Clinical Advisor |

---

**Status**: ✅ Approved for Clinical Advisor review
**Next Review**: After Clinical Advisor feedback (5 business days)
**Production Deployment**: After approval + Golden Dataset validation

**Document Owner**: Project Manager Coordinator
**Technical Owner**: Backend Development Team
**Clinical Owner**: Clinical Advisor (FRACGP)

---

**END OF ADR-001**
