# Track 2: Content Generation
**Duration:** Weeks 1-20
**Goal:** Generate 5,000+ MCQs, 164 OSCE modules, 150+ evidence summaries
**Status:** 🟡 WEEK 1 IN PROGRESS

---

## Overview

This track generates all new educational content using:
- **RAG-verified citations** from 42,647 indexed vectors
- **Medical expert agents** (MED-001 to MED-010)
- **Automated QA validation** (QA-003)
- **100% Australian guideline compliance**

---

## Content Targets

### MCQ Generation (5,000+ questions)

| Specialty | Target MCQs | Week Start | Status | Progress |
|-----------|-------------|------------|--------|----------|
| **Psychiatry** | 400 | Week 1 | 🟡 ACTIVE | 0/400 |
| **Cardiology** | 600 | Week 3 | ⏳ PENDING | 0/600 |
| **Respiratory** | 600 | Week 3 | ⏳ PENDING | 0/600 |
| **Gastroenterology** | 300 | Week 3 | ⏳ PENDING | 0/300 |
| **Endocrinology** | 300 | Week 3 | ⏳ PENDING | 0/300 |
| **Neurology** | 600 | Week 5 | ⏳ PENDING | 0/600 |
| **Emergency Medicine** | 600 | Week 5 | ⏳ PENDING | 0/600 |
| **ObGyn** | 600 | Week 7 | ⏳ PENDING | 0/600 |
| **Paediatrics** | 600 | Week 7 | ⏳ PENDING | 0/600 |
| **General Practice** | 500 | Week 7 | ⏳ PENDING | 0/500 |
| **TOTAL** | **5,100** | - | - | **0/5,100** |

### OSCE Module Generation (164 modules)

| Category | Target | Week Start | Status | Progress |
|----------|--------|------------|--------|----------|
| **Psychiatry** | 17 | Week 1 | 🟡 ACTIVE | 0/17 |
| **Emergency Medicine** | 15 | Week 6 | ⏳ PENDING | 0/15 |
| **ObGyn** | 20 | Week 7 | ⏳ PENDING | 0/20 |
| **Paediatrics** | 15 | Week 8 | ⏳ PENDING | 0/15 |
| **General Practice** | 25 | Week 9 | ⏳ PENDING | 0/25 |
| **Marwan Medicine Cases** | 30 | Week 11 | ⏳ PENDING | 0/30 |
| **Other Specialties** | 42 | Week 11-14 | ⏳ PENDING | 0/42 |
| **TOTAL** | **164** | - | - | **0/164** |

### Other Content

| Content Type | Target | Week Start | Status | Progress |
|--------------|--------|------------|--------|----------|
| **Evidence Summaries** | 150+ | Week 1+ | 🟡 ONGOING | 0/150 |
| **Clinical Pathways** | 30+ | Week 11 | ⏳ PENDING | 0/30 |
| **Pharmacology Cards** | 50+ | Week 11 | ⏳ PENDING | 0/50 |
| **Prediction Rules** | 20+ | Week 11 | ⏳ PENDING | 0/20 |
| **Red Flags** | 10+ | Week 13 | ⏳ PENDING | 0/10 |

---

## MCQ Generation Process

### Template Structure

```json
{
  "id": "PSY-001",
  "specialty": "Psychiatry",
  "topic": "Major Depressive Disorder",
  "difficulty": "medium",
  "amc_frequency": "very_high",

  "question": {
    "scenario": "A 45-year-old woman presents to her GP with 6 weeks of low mood...",
    "stem": "What is the most appropriate first-line treatment?",
    "options": {
      "A": "Cognitive behavioral therapy (CBT) alone",
      "B": "Sertraline 50mg daily",
      "C": "Amitriptyline 25mg at night",
      "D": "Referral to psychiatrist",
      "E": "Electroconvulsive therapy (ECT)"
    },
    "correct_answer": "B"
  },

  "explanation": {
    "why_correct": "Sertraline (SSRI) is first-line for moderate-severe depression...",
    "why_incorrect": {
      "A": "CBT alone is for mild depression or adjunct to medication",
      "C": "TCAs are second-line due to side effects",
      "D": "GP management appropriate first, refer if treatment-resistant",
      "E": "ECT reserved for severe depression with psychotic features"
    },
    "key_points": [
      "SSRIs are first-line for moderate-severe depression",
      "Start low dose, titrate after 2-4 weeks",
      "Review in 2 weeks for side effects and suicidality"
    ]
  },

  "references": [
    {
      "title": "RANZCP Clinical Practice Guidelines: Mood Disorders",
      "page": "45-47",
      "year": 2023,
      "rag_confidence": 0.94
    },
    {
      "title": "Therapeutic Guidelines: Psychotropic",
      "page": "89",
      "year": 2024,
      "rag_confidence": 0.91
    }
  ],

  "metadata": {
    "generated_by": "MED-009-Psychiatry",
    "generated_date": "2026-01-24",
    "qa_validated": true,
    "qa_confidence": 0.93,
    "manual_review": false
  }
}
```

### Generation Workflow

```python
class MCQGenerator:
    """
    Automated MCQ generation with RAG citations
    """

    def generate_mcq(self, topic: str, difficulty: str) -> dict:
        """
        Generate single MCQ

        Steps:
        1. Create clinical scenario (age, presentation, duration)
        2. Generate question stem (diagnosis/investigation/management)
        3. Generate 5 options (1 correct, 4 plausible distractors)
        4. Query RAG for citations (top 2 Australian sources)
        5. Generate explanation (why correct, why incorrect)
        6. Validate with QA-003
        7. Return complete MCQ
        """

        # Step 1: Clinical scenario
        scenario = self._generate_scenario(topic, difficulty)

        # Step 2: Question stem
        stem = self._generate_stem(scenario, question_type='management')

        # Step 3: Options
        options = self._generate_options(scenario, stem)

        # Step 4: RAG citations
        query = f"{topic} {stem}"
        rag_results = self.rag.query(query, top_k=5, filter={'country': 'Australia'})
        citations = rag_results[:2]  # Top 2 Australian sources

        # Step 5: Explanation
        explanation = self._generate_explanation(
            scenario, stem, options, citations
        )

        # Step 6: Validate
        mcq = {
            'id': self._generate_id(),
            'specialty': self.specialty,
            'topic': topic,
            'difficulty': difficulty,
            'question': {'scenario': scenario, 'stem': stem, 'options': options},
            'explanation': explanation,
            'references': citations
        }

        validation_result = self.qa.validate_mcq(mcq)

        if validation_result['recommendation'] == 'approve':
            mcq['metadata']['qa_validated'] = True
            mcq['metadata']['qa_confidence'] = validation_result['overall_confidence']
            return mcq
        else:
            # Regenerate if rejected
            return self.generate_mcq(topic, difficulty)
```

---

## Week-by-Week MCQ Generation Schedule

### Phase A: Foundation (Weeks 1-4)

#### Week 1: Psychiatry (100 MCQs)
**Agent:** MED-009 Psychiatry
**Status:** 🟡 ACTIVE

**Breakdown:**
- Depression (25 MCQs)
  - Major depressive disorder diagnosis (10)
  - Antidepressant selection (10)
  - Treatment-resistant depression (5)
- Anxiety Disorders (20 MCQs)
  - GAD, panic disorder, PTSD (15)
  - Pharmacotherapy (5)
- Psychotic Disorders (25 MCQs)
  - Schizophrenia diagnosis/treatment (15)
  - Antipsychotic medications (10)
- Bipolar Disorder (15 MCQs)
  - Mania diagnosis (7)
  - Mood stabilizers (8)
- Suicide Risk & MHA (15 MCQs)
  - Risk assessment (8)
  - Involuntary admission (7)

**Daily Targets:**
- Day 1: 20 MCQs (depression)
- Day 2: 20 MCQs (anxiety + bipolar)
- Day 3: 25 MCQs (psychosis)
- Day 4: 20 MCQs (suicide + MHA)
- Day 5: 15 MCQs (review + gaps)

**Success Criteria:**
- ✅ 100 MCQs with RAG citations (>0.90 confidence)
- ✅ 90%+ pass QA-003 validation
- ✅ Difficulty: 40% easy, 40% medium, 20% hard

---

#### Week 2: Psychiatry Continuation (300 MCQs → 400 total)
**Agent:** MED-009 Psychiatry
**Status:** ⏳ PENDING

**Breakdown:**
- Additional depression MCQs (75)
- Additional psychotic disorders (75)
- OCD (30)
- Eating disorders (30)
- Substance use disorders (30)
- Personality disorders (30)
- ADHD (15)
- Dementia/delirium (15)

**Target:** 400 total psychiatry MCQs by end of Week 2

---

#### Week 3: Cardiology + Respiratory Start (400 MCQs)
**Agents:** MED-001 Cardiology, MED-002 Respiratory
**Status:** ⏳ PENDING

**Cardiology (200 MCQs):**
- Acute coronary syndromes (50)
- Heart failure (40)
- Arrhythmias (40)
- Valvular disease (30)
- Hypertension (25)
- Other (15)

**Respiratory (200 MCQs):**
- Asthma (40)
- COPD (40)
- Pneumonia (30)
- Pulmonary embolism (20)
- Lung cancer (20)
- Other (50)

**Cumulative:** 900 MCQs (400 psychiatry + 200 cardio + 200 resp)

---

#### Week 4: GI + Endocrine Start (600 MCQs → 1,500 total)
**Agents:** MED-003 Gastroenterology, MED-004 Endocrinology
**Status:** ⏳ PENDING

**GI (200 MCQs):**
- Liver disease (50)
- IBD (40)
- Upper GI (40)
- Lower GI (40)
- Pancreatic/biliary (30)

**Endocrine (200 MCQs):**
- Diabetes (80)
- Thyroid (50)
- Lipids (30)
- Adrenal (20)
- Pituitary (20)

**Additional Cardio/Resp (200 MCQs):**
- Complete to 300 each

**Cumulative:** 1,500 MCQs

---

### Phase B: Scaling (Weeks 5-10)

#### Week 5-6: Neurology + Emergency Medicine (1,200 MCQs → 2,800 total)
**Agents:** MED-005 Neurology, MED-006 Emergency Medicine

**Neurology (600 MCQs):**
- Stroke (120)
- Seizures/epilepsy (100)
- Headache (80)
- Movement disorders (80)
- Demyelinating diseases (80)
- Peripheral neuropathy (80)
- Other (60)

**Emergency Medicine (600 MCQs):**
- Resuscitation (100)
- Trauma (100)
- Shock (80)
- Toxicology (80)
- Anaphylaxis (40)
- Environmental emergencies (80)
- Procedural sedation (40)
- Other (80)

**Cumulative:** 2,800 MCQs

---

#### Week 7-8: ObGyn + Paediatrics (1,200 MCQs → 4,200 total)
**Agents:** MED-007 ObGyn, MED-008 Paediatrics

**ObGyn (600 MCQs):**
- Antenatal care (120)
- Pregnancy complications (120)
- Labor & delivery (100)
- Contraception (80)
- Gynecological conditions (100)
- Gynae oncology (80)

**Paediatrics (600 MCQs):**
- Development (80)
- Immunization (60)
- Growth (40)
- Common pediatric conditions (200)
- Neonatal care (100)
- Pediatric emergencies (120)

**Cumulative:** 4,200 MCQs

---

#### Week 9-10: General Practice + Final Push (800 MCQs → 5,000 total)
**Agent:** MED-010 General Practice

**GP (500 MCQs):**
- Preventive health (100)
- Chronic disease management (100)
- Mental health in primary care (80)
- Geriatric assessment (80)
- Musculoskeletal (80)
- Common presentations (60)

**Additional across all specialties (300 MCQs):**
- Fill gaps identified in QA review
- High-yield topics needing more coverage

**Cumulative:** 5,000+ MCQs ✅

---

## OSCE Module Generation

### OSCE Structure

```markdown
# OSCE Station: [Title]
**Duration:** 8 minutes
**Type:** History Taking / Examination / Communication / Emergency Management
**Specialty:** [Specialty]
**Difficulty:** Easy / Medium / Hard

---

## Candidate Instructions

You have 8 minutes to complete this station.

**Task:**
[Clear description of what candidate must do]

**You will be assessed on:**
- [Assessment criterion 1]
- [Assessment criterion 2]
- [Assessment criterion 3]

---

## Patient/Actor Instructions

**Role:** You are [description of patient/scenario]

**Background:**
[Backstory, current situation, emotions]

**If asked about:**
- [Symptom 1]: [What to say]
- [Symptom 2]: [What to say]

**Do not volunteer information unless specifically asked.**

---

## Examiner Marking Sheet

**Candidate Name:** ________________
**Candidate Number:** ________________

### Domain 1: [e.g., History Taking] (8 points)
- [ ] Introduces self and confirms patient identity (1 point)
- [ ] Asks about onset and duration (1 point)
- [ ] Characterizes symptoms (SOCRATES) (2 points)
- [ ] Asks about red flags (2 points)
- [ ] Identifies risk factors (1 point)
- [ ] Assesses impact on daily life (1 point)

### Domain 2: [e.g., Clinical Reasoning] (6 points)
- [ ] Generates appropriate differential diagnosis (2 points)
- [ ] Identifies most likely diagnosis (2 points)
- [ ] Suggests appropriate investigations (2 points)

### Domain 3: [e.g., Management] (4 points)
- [ ] Suggests appropriate initial management (2 points)
- [ ] Discusses referral/follow-up (2 points)

### Domain 4: Communication & Professionalism (2 points)
- [ ] Demonstrates empathy (1 point)
- [ ] Uses clear, jargon-free language (1 point)

**Total: _____ / 20 points**

**Pass Mark:** 14/20 (70%)

---

## Model Answer

**Expected Approach:**
1. Introduction and rapport building
2. Systematic history taking (SOCRATES)
3. Red flags assessment
4. Risk factor identification
5. Differential diagnosis formulation
6. Management plan discussion

**Key Learning Points:**
- [Learning point 1]
- [Learning point 2]
- [Learning point 3]

**Common Mistakes:**
- [Mistake 1]
- [Mistake 2]

---

## References

1. [Australian Guideline], p.[page numbers], [year]
2. [Major Textbook], Chapter [X], p.[page numbers], [year]

**RAG Confidence:** 0.92

---

**Created By:** MED-009 Psychiatry Agent
**Created Date:** 2026-01-24
**QA Validated:** Yes
```

### Week-by-Week OSCE Generation

#### Week 1: 5 Psychiatry OSCE Modules
1. Major Depressive Disorder History
2. Mental State Examination
3. Suicide Risk Assessment
4. Explain Antidepressant Therapy
5. Mental Health Act Scenario

#### Week 2: 12 More Psychiatry OSCE (17 total)
6-17: Bipolar disorder, schizophrenia, anxiety disorders, ECT counseling, etc.

#### Week 6: 15 Emergency Medicine OSCE
- Anaphylaxis management
- Trauma assessment
- Sepsis recognition
- Stroke management
- Resuscitation scenarios

#### Week 7: 20 ObGyn OSCE
- Antenatal counseling
- Pregnancy complications
- Contraception counseling
- Labor management
- Gynecological examinations

#### Week 8: 15 Paediatrics OSCE
- Developmental assessment
- Immunization counseling
- Pediatric examination
- Neonatal assessment
- Safeguarding scenarios

#### Week 9: 25 General Practice OSCE
- Preventive health counseling
- Chronic disease management
- Mental health assessment
- Geriatric assessment
- Common GP presentations

#### Week 11-12: 30 Marwan Medicine Cases (OSCE format)
- Complex internal medicine cases
- Multiple comorbidities
- Diagnostic challenges

#### Week 13-14: 42 Additional OSCE Modules
- Complete coverage of all specialties
- High-yield AMC topics
- Gap filling from QA review

**Total:** 164 OSCE modules ✅

---

## Evidence Summaries

### Structure

```markdown
# Evidence Summary: [Topic]

## Clinical Question
[PICO format: Population, Intervention, Comparison, Outcome]

## Summary
[2-3 paragraphs summarizing current evidence]

## Key Recommendations
1. [Recommendation 1] (Grade A evidence)
2. [Recommendation 2] (Grade B evidence)
3. [Recommendation 3] (Grade C evidence)

## Evidence Level
- **Guideline:** [Australian guideline name]
- **Level of Evidence:** [I, II, III, IV, V]
- **Grade of Recommendation:** [A, B, C, D]

## References
1. [Australian Guideline], p.[pages], [year] (RAG confidence: 0.94)
2. [Systematic Review], [journal], [year] (RAG confidence: 0.89)
3. [RCT], [journal], [year] (RAG confidence: 0.86)

---
**Generated:** [Date]
**Agent:** [MED-XXX]
**QA Validated:** Yes
```

### Generation Schedule
- **Week 1-4:** 50 summaries (concurrent with MCQ generation)
- **Week 5-10:** 100 more summaries (150 total)
- **Week 11-16:** Additional summaries as needed

---

## Success Metrics

| Metric | Target | Current | Week 4 | Week 10 | Week 16 |
|--------|--------|---------|--------|---------|---------|
| **MCQs Generated** | 5,000 | 0 | 1,500 | 5,000 ✅ | 5,000+ |
| **QA Pass Rate** | >90% | - | 92% | 94% | 95% |
| **Citation Confidence** | >0.90 | - | 0.92 | 0.93 | 0.94 |
| **OSCE Modules** | 164 | 0 | 17 | 100 | 164 ✅ |
| **Evidence Summaries** | 150+ | 0 | 50 | 150 ✅ | 200+ |
| **Generation Speed** | <10s/MCQ | - | 8s | 6s | 5s |

---

## Quality Standards

### MCQ Quality
- **Clinical Accuracy:** 100% (guideline-compliant)
- **Australian Context:** 100% (medication names, units, healthcare system)
- **Citation Accuracy:** 100% (RAG-verified, page numbers correct)
- **Difficulty Calibration:** 40% easy, 40% medium, 20% hard
- **Distractor Quality:** All plausible, educational value

### OSCE Quality
- **Timing:** 8 minutes validated
- **Marking Rubrics:** Complete (20 points total, 70% pass mark)
- **Australian Context:** 100% (guidelines, healthcare system)
- **Citations:** Minimum 2 references per module
- **Feasibility:** Tested for practicality

---

## Related Documents
- [Track 1: Agent Expansion](TRACK_01_AGENT_EXPANSION.md)
- [Track 3: Quality Assurance](TRACK_03_QUALITY_ASSURANCE.md)
- [Week 1 Execution](../weekly/WEEK_01_EXECUTION.md)
- [QA-003 Upgrade](../QA_003_UPGRADE_PLAN.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟡 WEEK 1 IN PROGRESS (100 psychiatry MCQs + 5 OSCE)
**Next Milestone:** End of Week 2 (400 psychiatry MCQs + 17 OSCE)
**Final Milestone:** End of Week 16 (5,000+ MCQs + 164 OSCE)
