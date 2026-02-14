# MCQ Generation Plan
## Automated AMC-Style Multiple Choice Question Creation

**Format:** Single Best Answer MCQs (5 options: A-E)
**Target:** 5,000+ questions across all specialties
**Priority:** P1 (Core content generation)
**Responsible Agent:** AI-001 (RAG Architect) + MED-001 to MED-010
**Timeline:** Week 8-10 of Phase 3

---

## Objectives

1. Build fully automated MCQ generation pipeline
2. Ensure 100% Australian guideline compliance
3. Generate questions with educational distractors
4. Include detailed explanations with citations
5. Calibrate difficulty appropriately (ICRP to AMC level)
6. Achieve 90%+ automated quality validation pass rate

---

## AMC MCQ Format Specification

### Standard Format
```
Question Stem (Clinical Scenario):
A 65-year-old man with a history of hypertension and type 2 diabetes
presents to the emergency department with 3 hours of severe central
chest pain radiating to the left arm and jaw. He is diaphoretic and
appears unwell. Blood pressure is 90/60 mmHg, heart rate 110 bpm.
ECG shows 3mm ST elevation in leads II, III, and aVF.

What is the most appropriate immediate management?

Options:
A. Aspirin 300mg immediately and ticagrelor 180mg loading dose
B. Commence IV tenecteplase thrombolysis
C. Arrange urgent coronary angiography with primary PCI
D. Give GTN sublingual and observe serial troponins
E. Commence IV heparin infusion and transfer to CCU

Correct Answer: C

Explanation:
This patient has an inferior STEMI (ST elevation in II, III, aVF) with
cardiogenic shock (hypotension, tachycardia). Primary PCI within 90 minutes
is the gold standard treatment for STEMI and is superior to thrombolysis,
particularly in the setting of cardiogenic shock. While dual antiplatelet
therapy (option A) should be given, the definitive management is urgent
revascularization with PCI.

Thrombolysis (option B) is relatively contraindicated in cardiogenic shock
and is second-line to PCI when available. GTN and observation (option D)
would be inappropriate given the clear STEMI. IV heparin alone (option E)
is insufficient without definitive revascularization.

References:
1. Therapeutic Guidelines: Cardiovascular, Chapter 3: Acute Coronary
   Syndromes, p.123-125 (2024)
2. NHFA/CSANZ Guidelines for the Management of Acute Coronary Syndromes,
   p.45-47 (2023)

AMC Frequency: ⭐⭐⭐ (Very High)
Difficulty: Medium (AMC level)
Specialty: Cardiology
```

---

## Generation Pipeline Architecture

### Component 1: Clinical Scenario Generator

```python
# File: src/generation/scenario_generator.py

class ClinicalScenarioGenerator:
    """
    Generate realistic clinical scenarios for MCQs

    Draws from:
    - Textbook case presentations
    - Australian guideline examples
    - Common AMC exam scenarios
    """

    def generate_scenario(
        self,
        topic: str,
        specialty: str,
        difficulty: str,
        amc_frequency: str
    ) -> dict:
        """
        Generate patient presentation

        Components:
        1. Patient demographics (age, gender, relevant PMH)
        2. Presenting complaint (chief concern)
        3. History of presenting complaint (timeline, character)
        4. Relevant past medical history
        5. Examination findings (key positives/negatives)
        6. Investigation results (if relevant)

        Australian Context:
        - Use Australian medication names
        - Reference Australian healthcare system
        - Include PBS/MBS context where relevant
        """
```

**Implementation Details:**

**1. Patient Demographics (Evidence-Based):**
- Age: Match typical age for condition
  - Example: STEMI → 60-70 years (peak incidence)
  - Example: Meningitis → 18-25 years (young adults)
- Gender: Consider gender-specific conditions
  - Example: Ovarian cancer → female
  - Example: Prostate cancer → male
- Risk factors: Include 2-3 relevant risk factors
  - Example: ACS → HTN, DM, hyperlipidemia, smoking

**2. Presenting Complaint:**
- Clear, specific symptom
- Duration specified
- Severity indicated
- Quality described (if pain)

**3. Key Clinical Details:**
- Include enough information to answer question
- Avoid unnecessary "red herrings"
- Include relevant negatives
- Add examination findings that support diagnosis

**4. Investigation Results:**
- Only include if necessary for question
- Use Australian normal ranges
- Use appropriate units (mmol/L not mg/dL)

---

### Component 2: Question Type Generator

**Question Types by Cognitive Level:**

**Level 1: Recall (20% of questions)**
- Direct factual knowledge
- Example: "What is the first-line antibiotic for community-acquired pneumonia?"
- Difficulty: Easy (ICRP level)

**Level 2: Application (50% of questions)**
- Apply knowledge to clinical scenario
- Example: "Which investigation should be ordered next?"
- Difficulty: Medium (AMC level)

**Level 3: Analysis/Synthesis (30% of questions)**
- Complex clinical reasoning
- Multiple steps required
- Example: "Patient has multiple comorbidities - what is safest management?"
- Difficulty: Medium to Hard

**Question Stems:**
```python
QUESTION_TEMPLATES = {
    "management": [
        "What is the most appropriate immediate management?",
        "What is the most appropriate next step in management?",
        "What is the best initial treatment?",
        "What is the definitive management?"
    ],
    "diagnosis": [
        "What is the most likely diagnosis?",
        "Which diagnosis best explains these findings?",
        "What is the underlying cause?"
    ],
    "investigation": [
        "What is the most appropriate next investigation?",
        "Which investigation would be most helpful?",
        "What is the gold standard investigation?"
    ],
    "interpretation": [
        "How should this result be interpreted?",
        "What does this finding indicate?",
        "What is the significance of this result?"
    ]
}
```

---

### Component 3: Distractor Generation

**Philosophy:** Distractors should be:
1. **Plausible** - Could be chosen by students
2. **Educational** - Teach common mistakes
3. **Evidence-based** - Real clinical pitfalls
4. **Not obviously wrong** - Require knowledge to eliminate

**Distractor Types:**

**Type 1: Common Misconceptions (30%)**
```python
# Example: ACS management
Correct: "Primary PCI within 90 minutes"
Distractor: "Aspirin alone is sufficient"  # Outdated practice
```

**Type 2: Dose/Timing Errors (20%)**
```python
# Example: Asthma management
Correct: "Salbutamol 8-12 puffs via spacer"
Distractor: "Salbutamol 2 puffs via spacer"  # Insufficient dose for acute asthma
```

**Type 3: Incomplete Management (20%)**
```python
# Example: Anaphylaxis
Correct: "IM adrenaline 0.5mg immediately"
Distractor: "IV antihistamine and observation"  # Missing life-saving intervention
```

**Type 4: Overtreatment (15%)**
```python
# Example: Simple UTI
Correct: "Oral trimethoprim 300mg daily for 3 days"
Distractor: "IV piperacillin-tazobactam for 7 days"  # Unnecessary escalation
```

**Type 5: Wrong Sequence (15%)**
```python
# Example: STEMI
Correct: "Primary PCI within 90 minutes"
Distractor: "Arrange outpatient stress test"  # Inappropriate delay
```

**Distractor Generation Algorithm:**
```python
def generate_distractors(
    correct_answer: str,
    topic: str,
    guidelines: dict
) -> List[str]:
    """
    Generate 4 plausible incorrect options

    Strategy:
    1. Query RAG for common mistakes (medical literature)
    2. Find outdated guidelines (historical practices)
    3. Generate dose variations (too high/low)
    4. Create sequence errors (right intervention, wrong timing)
    5. Ensure grammatical parallelism with correct answer
    """

    distractors = []

    # Type 1: Common misconception
    distractors.append(
        self.rag.query(f"common mistakes in {topic} management")
    )

    # Type 2: Dose error
    distractors.append(
        self.modify_dose(correct_answer, factor=0.25)  # Too low
    )

    # Type 3: Incomplete management
    distractors.append(
        self.remove_key_component(correct_answer)
    )

    # Type 4: Overtreatment
    distractors.append(
        self.escalate_unnecessarily(correct_answer)
    )

    return distractors
```

---

### Component 4: Explanation Generator

**Explanation Structure:**

1. **Why Correct Answer is Correct (2-3 sentences)**
   - Cite guideline explicitly
   - Explain mechanism/reasoning
   - Reference evidence level

2. **Why Each Distractor is Incorrect (1 sentence each)**
   - Brief explanation of why wrong
   - Educational value (teach common mistake)

3. **Key Learning Points (2-3 bullet points)**
   - Important concepts to remember
   - Red flags or critical features
   - Common pitfalls to avoid

4. **References (Minimum 2, Maximum 5)**
   - Primary: Australian guidelines (eTG, TG, RACGP)
   - Secondary: Major textbooks
   - Tertiary: Landmark studies (if relevant)
   - Format: Title, page numbers, year

**Example Explanation:**
```
The correct answer is C: Arrange urgent coronary angiography with
primary PCI.

This patient has an inferior STEMI (ST elevation in leads II, III, aVF)
complicated by cardiogenic shock (hypotension, tachycardia). Primary PCI
is the gold standard reperfusion strategy for STEMI and must be performed
within 90 minutes of presentation (door-to-balloon time). It is superior
to thrombolysis, particularly in high-risk presentations such as
cardiogenic shock (Class I, Level A evidence).

Option A (dual antiplatelet therapy) is essential but not the definitive
management - it should be given alongside PCI, not instead of it.

Option B (thrombolysis) is second-line when PCI is unavailable, and is
relatively contraindicated in cardiogenic shock due to increased bleeding
risk without superior outcomes.

Option D (GTN and observation) dangerously delays definitive treatment in
a life-threatening condition with clear indications for urgent
revascularization.

Option E (heparin alone) provides anticoagulation but does not address
the underlying coronary occlusion requiring mechanical revascularization.

Key Learning Points:
• Primary PCI is superior to thrombolysis for STEMI when available
  within 90 minutes
• Cardiogenic shock requires immediate mechanical revascularization
• Door-to-balloon time <90 minutes is the quality indicator for STEMI care

References:
1. Therapeutic Guidelines: Cardiovascular, Chapter 3: Acute Coronary
   Syndromes, p.123-125 (2024 edition)
2. NHFA/CSANZ Guidelines for Management of Acute Coronary Syndromes 2023,
   Section 4.2: Primary PCI, p.45-47
3. Ibanez B, et al. 2017 ESC Guidelines for STEMI. Eur Heart J.
   2018;39(2):119-177
```

---

### Component 5: Quality Validation

**Automated Validation Checks:**

```python
class MCQValidator:
    """
    Automated quality checks for generated MCQs
    """

    def validate(self, question: dict) -> ValidationResult:
        """
        Run comprehensive validation

        Returns pass/fail with specific issues identified
        """

        checks = [
            self.check_clinical_accuracy(),
            self.check_guideline_compliance(),
            self.check_australian_context(),
            self.check_citation_validity(),
            self.check_question_clarity(),
            self.check_grammatical_parallelism(),
            self.check_difficulty_appropriateness(),
            self.check_distractor_quality()
        ]

        return self.aggregate_results(checks)
```

**Validation Checklist:**

**1. Clinical Accuracy (Critical)**
- [ ] Correct answer matches current guidelines
- [ ] No clinical errors in scenario/options
- [ ] Medication doses from AMH
- [ ] Guidelines published within 5 years

**2. Australian Context (Critical)**
- [ ] Australian medication names (not US brands)
- [ ] Australian units (mmol/L not mg/dL)
- [ ] Australian healthcare system terminology
- [ ] PBS/MBS references where appropriate

**3. Citation Validity (Critical)**
- [ ] All references exist
- [ ] Page numbers are correct
- [ ] Australian sources cited primarily
- [ ] Minimum 2 references included

**4. Question Quality (High Priority)**
- [ ] Question stem is clear and unambiguous
- [ ] Single best answer exists
- [ ] No "All of the above" or "None of the above"
- [ ] Options are grammatically parallel

**5. Distractor Quality (High Priority)**
- [ ] All distractors are plausible
- [ ] No obviously wrong options
- [ ] Educational value (teach common mistakes)
- [ ] Not too similar to each other

**6. Explanation Quality (Medium Priority)**
- [ ] Explains why correct answer is correct
- [ ] Addresses why distractors are incorrect
- [ ] Includes key learning points
- [ ] Well-structured and clear

**7. Metadata Completeness (Medium Priority)**
- [ ] Specialty assigned
- [ ] Difficulty level assigned
- [ ] AMC frequency indicated
- [ ] Topic tags included

---

## Production Workflow

### Step 1: Batch Generation
```bash
# Generate 100 questions at a time
python src/generation/batch_generate_mcqs.py \
  --specialty cardiology \
  --count 100 \
  --difficulty-distribution "40:40:20" \
  --output data/questions/cardiology_batch_001.json
```

### Step 2: Automated Validation
```bash
# Run QA-001 agent on batch
python src/agents/qa/qa001_validator.py \
  --input data/questions/cardiology_batch_001.json \
  --output data/questions/cardiology_batch_001_validated.json \
  --threshold 0.9
```

### Step 3: Manual Review (10% Sample)
```bash
# Extract random sample for manual review
python scripts/sample_questions.py \
  --input data/questions/cardiology_batch_001_validated.json \
  --sample-size 10 \
  --output data/review/cardiology_sample_001.json
```

### Step 4: Refinement & Iteration
```bash
# Update generation prompts based on feedback
python scripts/update_generation_config.py \
  --feedback data/review/feedback_001.json \
  --apply
```

---

## Quality Metrics & Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| QA-001 Pass Rate | ≥90% | Automated validation |
| Clinical Accuracy | 100% | Manual expert review |
| Citation Accuracy | 100% | Automated verification |
| Australian Context | 100% | Automated check |
| Manual Review Quality | ≥4.0/5.0 | Expert ratings |
| Distractor Plausibility | ≥85% | Expert assessment |
| Question Clarity | ≥4.0/5.0 | Readability scores |
| Generation Speed | 50-100/hour | System performance |

---

## Difficulty Calibration

### Easy (ICRP Level) - 40% of Questions
**Characteristics:**
- Straightforward clinical scenario
- Single clear answer
- Common presentation
- Clear management algorithm
- Minimal complicating factors

**Example Topics:**
- Uncomplicated UTI management
- Simple asthma exacerbation
- Routine diabetes management
- Standard hypertension treatment

**Target Pass Rate:** 80-90% for ICRP candidates

---

### Medium (AMC Level) - 40% of Questions
**Characteristics:**
- Typical presentation with 1-2 complications
- Requires application of guidelines
- May need dose adjustment or sequencing
- Multiple reasonable approaches (must pick best)

**Example Topics:**
- STEMI with renal impairment
- Asthma in pregnancy
- Heart failure with COPD
- Multiple comorbidities requiring management

**Target Pass Rate:** 60-70% for AMC candidates

---

### Hard (Advanced) - 20% of Questions
**Characteristics:**
- Rare presentation or complication
- Multiple competing priorities
- Requires synthesis of information
- May have controversial management

**Example Topics:**
- Pregnant woman with STEMI
- Severe anaphylaxis with beta-blocker use
- Complex drug interactions
- Rare adverse drug reactions

**Target Pass Rate:** 40-50% for AMC candidates

---

## Australian Context Requirements

### Medication Names
**Always Use Australian Generic/Brand Names:**
- ✅ "ticagrelor" (not "Brilinta")
- ✅ "prasugrel" (not "Effient")
- ✅ "paracetamol" (not "acetaminophen")
- ✅ "GTN" (not "nitroglycerin")

### Units
**Use Australian SI Units:**
- ✅ Glucose: mmol/L (not mg/dL)
- ✅ Cholesterol: mmol/L (not mg/dL)
- ✅ HbA1c: % or mmol/mol (not just %)
- ✅ Creatinine: μmol/L (not mg/dL)

### Healthcare System
**Use Australian Terminology:**
- ✅ "Emergency Department" (not "ER")
- ✅ "General Practitioner" (not "PCP")
- ✅ "Public hospital" (not "county hospital")
- ✅ "PBS" (Pharmaceutical Benefits Scheme)
- ✅ "MBS" (Medicare Benefits Schedule)

### Guidelines
**Primary Sources (in order):**
1. Therapeutic Guidelines (eTG)
2. Australian Medicines Handbook (AMH)
3. RACGP Guidelines
4. ANZCA/ANZICS Guidelines
5. State-based guidelines (NSW Health, etc.)
6. International guidelines (secondary reference only)

---

## Success Criteria

**Phase 3 Goals (Week 8-10):**
- ✅ 500 questions generated and validated
- ✅ 90%+ pass QA-001 validation
- ✅ 100% citation compliance
- ✅ 100% Australian context
- ✅ Manual review score ≥4.0/5.0

**Phase 5 Goals (Week 15-18 with Agents):**
- ✅ 5,000 questions across all specialties
- ✅ Automated generation: 100-200 questions/hour
- ✅ 95%+ pass rate on first generation
- ✅ Consistent quality across specialties

---

## Related Documents

- [Phase 3: RAG & Generation](../../01_PHASE_EXECUTION/phase3_rag_generation.md)
- [Cardiology Content Plan](../by_specialty/cardiology_plan.md)
- [QA-001 Validator Agent](../../04_AGENT_PLANS/qa_agents/qa001_medical_validator_plan.md)
- [RAG System Architecture](../../03_INFRASTRUCTURE_PLANS/rag_system/query_engine_plan.md)

---

**Last Updated:** January 17, 2026
**Status:** ⏳ NOT STARTED (awaiting Phase 1 + books)
**Owner:** AI-001 (RAG Architect) + All Medical Agents
**Dependencies:** Phase 1 complete, Books acquired, RAG system operational
