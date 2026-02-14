# MED-009 Psychiatry Agent Expansion Plan
**Agent ID:** MED-009
**Specialty:** Psychiatry & Mental Health
**Timeline:** Week 1-2 (2026-01-24 to 2026-02-07)
**Status:** 🟡 IN PROGRESS

---

## Expansion Overview

### Current State
- **File:** `src/agents/medical/med_009_psychiatry.py`
- **Current LOC:** 115 lines
- **Current Capabilities:**
  - Basic psychiatric diagnosis (DSM-5 criteria)
  - Common medication classes (antidepressants, antipsychotics)
  - Simple MCQ generation

### Target State (End of Week 2)
- **Target LOC:** 850+ lines
- **Expansion:** 735 LOC (639% increase)
- **New Capabilities:**
  - Mental State Examination (MSE) framework
  - Comprehensive risk assessment tools
  - Australian Mental Health Act compliance
  - Psychiatric medication side effects
  - ECT counseling framework
  - All 17 psychiatry topics coverage

---

## Week 1 Expansion (115 → 400 LOC)

### Component 1: Mental State Examination Framework
**LOC:** 120 lines
**Priority:** P0 (Critical for OSCE stations)
**Status:** 🟡 PENDING

#### Functionality
```python
class MentalStateExamination:
    """
    Structured MSE assessment tool for psychiatry OSCE stations

    Components:
    1. Appearance and Behavior
       - Grooming, hygiene, eye contact
       - Psychomotor activity (agitation, retardation)
       - Abnormal movements (tardive dyskinesia, tremor)

    2. Speech
       - Rate (pressured, slow)
       - Volume (loud, soft)
       - Spontaneity
       - Content (circumstantial, tangential, flight of ideas)

    3. Mood and Affect
       - Subjective mood (patient's words)
       - Objective affect (observed)
       - Range (full, restricted, blunted, flat)
       - Appropriateness (congruent, incongruent)

    4. Thought Form and Content
       - Form: Logical, goal-directed vs. disorganized
       - Content: Delusions (persecutory, grandiose, referential)
       - Suicidal ideation, homicidal ideation
       - Obsessions, compulsions

    5. Perception
       - Hallucinations (auditory, visual, tactile)
       - Illusions
       - Depersonalization, derealization

    6. Cognition
       - Orientation (person, place, time, situation)
       - Attention and concentration
       - Memory (immediate, recent, remote)
       - Executive function

    7. Insight and Judgment
       - Awareness of illness
       - Understanding of need for treatment
       - Adherence to treatment plan
    """

    def generate_mse_template(self, condition: str) -> dict:
        """Generate MSE findings template for specific condition"""
        pass

    def generate_mse_osce_station(self, difficulty: str) -> dict:
        """Generate OSCE station for MSE assessment"""
        pass

    def generate_mse_mcqs(self, topic: str, count: int) -> list:
        """Generate MCQs testing MSE knowledge"""
        pass
```

#### Deliverables
- [ ] MSE structured assessment tool (60 LOC)
- [ ] MSE OSCE station generator (30 LOC)
- [ ] MSE MCQ generator (30 LOC)

#### Success Criteria
- ✅ Can generate MSE findings for 10 common psychiatric conditions
- ✅ Can create 8-minute OSCE stations with marking rubrics
- ✅ Can generate 20 MSE-related MCQs with citations

---

### Component 2: Risk Assessment Tools
**LOC:** 100 lines
**Priority:** P0 (Critical for safety assessment)
**Status:** 🟡 PENDING

#### Functionality
```python
class RiskAssessmentTools:
    """
    Comprehensive suicide and violence risk assessment

    Tools:
    1. Suicide Risk Assessment
       - SAD PERSONS scale
       - Columbia Suicide Severity Rating Scale (C-SSRS)
       - Risk factors (demographics, psychiatric, psychosocial)
       - Protective factors (support, reasons for living)
       - Immediate vs. ongoing risk stratification

    2. Violence Risk Assessment
       - Historical factors (past violence, criminal history)
       - Clinical factors (psychosis, substance use)
       - Risk management factors (treatment adherence, support)

    3. Self-Harm Risk
       - Non-suicidal self-injury (NSSI) patterns
       - Functions of self-harm (emotion regulation, self-punishment)
       - Escalation patterns

    4. Safety Planning
       - Warning signs recognition
       - Coping strategies
       - Support persons and contacts
       - Crisis resources (Lifeline 13 11 14, Beyond Blue)
       - Means restriction (firearms, medications)
    """

    def assess_suicide_risk(self, patient_data: dict) -> dict:
        """
        Stratify suicide risk: LOW, MODERATE, HIGH, IMMINENT

        Returns:
            risk_level: str
            risk_factors: list
            protective_factors: list
            recommendations: list (safety plan, referral, admission)
        """
        pass

    def generate_safety_plan(self, patient_data: dict) -> dict:
        """Generate personalized safety plan"""
        pass

    def generate_risk_mcqs(self, scenario_type: str, count: int) -> list:
        """Generate MCQs on risk assessment scenarios"""
        pass
```

#### Australian Clinical Context
- **Crisis Resources:**
  - Lifeline: 13 11 14 (24/7 crisis support)
  - Beyond Blue: 1300 22 4636
  - Suicide Call Back Service: 1300 659 467
  - Kids Helpline: 1800 55 1800
  - MensLine Australia: 1300 78 99 78

- **Referral Pathways:**
  - Emergency Department (acute risk)
  - Crisis Assessment and Treatment Team (CATT) - community
  - General Practitioner (low-moderate risk, follow-up)
  - Private psychiatrist or psychologist
  - Headspace (youth <25 years)

#### Deliverables
- [ ] Suicide risk assessment tool (40 LOC)
- [ ] Violence risk assessment tool (20 LOC)
- [ ] Safety planning generator (20 LOC)
- [ ] Risk assessment MCQ generator (20 LOC)

#### Success Criteria
- ✅ Risk stratification validated against RANZCP guidelines
- ✅ Safety plans include Australian crisis resources
- ✅ Can generate 15 risk assessment MCQs
- ✅ Correctly identifies Mental Health Act scenarios

---

### Component 3: Australian Mental Health Act Compliance
**LOC:** 80 lines
**Priority:** P1 (AMC exam requirement)
**Status:** 🟡 PENDING

#### Functionality
```python
class MentalHealthActCompliance:
    """
    Australian Mental Health Act provisions (state-specific)

    States Covered:
    - NSW Mental Health Act 2007
    - Victorian Mental Health Act 2014
    - Queensland Mental Health Act 2016

    Common Elements:
    1. Criteria for Involuntary Admission
       - Mental illness (as defined in Act)
       - Risk to self or others
       - Treatment available
       - Least restrictive alternative

    2. Schedule Types
       - Emergency detention (police, ambulance)
       - Short-term admission (72 hours to 28 days)
       - Continuing treatment order
       - Community Treatment Order (CTO)

    3. Rights and Safeguards
       - Right to legal representation
       - Mental Health Review Tribunal
       - Second psychiatric opinion
       - Advance directives (where applicable)

    4. ECT Provisions
       - Consent requirements
       - Tribunal approval (for involuntary patients)
       - Emergency ECT
    """

    def check_involuntary_criteria(self, state: str, patient_data: dict) -> dict:
        """
        Check if patient meets criteria for involuntary admission

        Returns:
            meets_criteria: bool
            criteria_met: list (mental illness, risk, treatment)
            criteria_not_met: list
            schedule_type: str
            documentation_required: list
        """
        pass

    def generate_mha_mcqs(self, state: str, count: int) -> list:
        """Generate MCQs on Mental Health Act scenarios"""
        pass
```

#### State-Specific Criteria Summary

**NSW Mental Health Act 2007:**
- Mental illness definition: requires functional impairment
- Involuntary admission: Sections 27-33
- CTO: Section 49-58
- ECT: Sections 93-100

**Victorian Mental Health Act 2014:**
- Recovery-oriented framework
- Compulsory assessment order (CAO)
- Temporary treatment order (TTO)
- Treatment order (TO)
- ECT safeguards (strongest in Australia)

**Queensland Mental Health Act 2016:**
- Least restrictive alternative principle
- Emergency Examination Authority (EEA)
- Recommendation for Assessment (RFA)
- Treatment Authority (TA)
- Forensic order provisions

#### Deliverables
- [ ] Involuntary admission criteria checker (30 LOC)
- [ ] Schedule type recommender (20 LOC)
- [ ] Documentation generator (15 LOC)
- [ ] Mental Health Act MCQ generator (15 LOC)

#### Success Criteria
- ✅ Criteria correctly applied for NSW, VIC, QLD
- ✅ Can generate 10 Mental Health Act MCQs
- ✅ Legal terminology accurate
- ✅ RANZCP ethical principles integrated

---

### Week 1 Summary
**Starting LOC:** 115
**New Code:** 300 LOC (MSE 120 + Risk 100 + MHA 80)
**Ending LOC:** 415 ✅ (Exceeds 400 target)
**Progress:** 50% of 850 LOC target

---

## Week 2 Expansion (400 → 850 LOC)

### Component 4: Psychiatric Medication Side Effects
**LOC:** 180 lines
**Priority:** P0 (High-yield for AMC)
**Status:** ⏳ PENDING

#### Functionality
```python
class PsychiatricMedicationTools:
    """
    Comprehensive psychiatric medication side effects and monitoring

    Medication Classes:
    1. Antidepressants
       - SSRIs (sertraline, escitalopram, fluoxetine)
       - SNRIs (venlafaxine, duloxetine)
       - TCAs (amitriptyline, nortriptyline)
       - MAOIs (moclobemide)
       - Others (mirtazapine, agomelatine)

    2. Antipsychotics
       - Typical (haloperidol, chlorpromazine)
       - Atypical (quetiapine, olanzapine, risperidone, aripiprazole)
       - Clozapine (special monitoring)

    3. Mood Stabilizers
       - Lithium (narrow therapeutic index)
       - Valproate (teratogenicity)
       - Lamotrigine (Stevens-Johnson syndrome risk)
       - Carbamazepine

    4. Benzodiazepines
       - Diazepam, lorazepam, alprazolam
       - Dependence and withdrawal

    Side Effects Coverage:
    - Extrapyramidal symptoms (EPS): Parkinsonism, akathisia, dystonia
    - Tardive dyskinesia (irreversible)
    - Neuroleptic malignant syndrome (medical emergency)
    - Serotonin syndrome (SSRI + MAOI combination)
    - QTc prolongation (antipsychotics)
    - Metabolic syndrome (atypical antipsychotics)
    - Sexual dysfunction (SSRIs, antipsychotics)
    - Weight gain (olanzapine, mirtazapine)
    - Lithium toxicity (tremor, confusion, seizures)
    - Clozapine: Agranulocytosis, myocarditis
    """

    def get_side_effects(self, medication: str, severity: str = 'all') -> list:
        """Get side effects for medication (common, serious, rare)"""
        pass

    def get_monitoring_requirements(self, medication: str) -> dict:
        """
        Get TGA-mandated monitoring requirements

        Examples:
        - Clozapine: Weekly FBC for 18 weeks, then fortnightly
        - Lithium: Levels 5 days post-dose change, then 3-monthly
        - Valproate: LFTs, FBC at baseline and 6 months
        """
        pass

    def check_drug_interactions(self, medications: list) -> list:
        """Check for dangerous interactions (e.g., SSRI + MAOI)"""
        pass

    def generate_medication_mcqs(self, topic: str, count: int) -> list:
        """Generate MCQs on medication management"""
        pass
```

#### TGA Special Monitoring Programs
- **Clozapine:** Mandatory registration with Clozapine Patient Monitoring System (CPMS)
- **Lithium:** Therapeutic range 0.6-1.2 mmol/L, toxicity >1.5 mmol/L
- **Valproate:** Pregnancy prevention program (teratogenicity)

#### Deliverables
- [ ] Medication side effects database (60 LOC)
- [ ] TGA monitoring requirements (40 LOC)
- [ ] Drug interaction checker (30 LOC)
- [ ] Medication MCQ generator (50 LOC)

#### Success Criteria
- ✅ Covers all 20+ common psychiatric medications
- ✅ TGA monitoring requirements accurate
- ✅ Can generate 50 medication-related MCQs
- ✅ Australian medication names (not US brand names)

---

### Component 5: ECT Counseling Framework
**LOC:** 120 lines
**Priority:** P1 (OSCE communication skill)
**Status:** ⏳ PENDING

#### Functionality
```python
class ECTCounselingFramework:
    """
    Electroconvulsive therapy counseling and consent

    Topics to Cover:
    1. Indications for ECT
       - Severe major depressive disorder (first-line if catatonia, psychotic features)
       - Treatment-resistant depression
       - Acute mania (medication failure)
       - Catatonia
       - Schizophrenia (severe psychotic symptoms)

    2. Procedure Explanation
       - General anaesthesia (brief)
       - Muscle relaxant
       - Electrical stimulus to brain
       - Induced seizure (controlled)
       - Duration: 5-10 minutes total
       - Course: 6-12 treatments (3x per week)

    3. Efficacy
       - 70-90% response rate in severe depression
       - Often effective when medications fail
       - Faster onset than medications (2-4 weeks)

    4. Side Effects
       - Short-term memory loss (most common)
       - Confusion immediately post-treatment
       - Headache, muscle aches
       - Rare: Status epilepticus, prolonged seizure

    5. Consent Process
       - Written consent required
       - Capacity assessment
       - Involuntary patients: Tribunal approval (VIC, QLD)
       - Advance directive considerations

    6. Australian Context
       - Medicare rebate available (item 14224)
       - Private vs. public hospital access
       - Maintenance ECT for relapse prevention
    """

    def generate_ect_osce_station(self, difficulty: str) -> dict:
        """
        Generate OSCE station: Counseling patient about ECT

        Marking criteria:
        - Indications explained (3 points)
        - Procedure described (3 points)
        - Side effects discussed (4 points)
        - Patient questions addressed (4 points)
        - Consent obtained (3 points)
        - Empathy and communication (3 points)
        Total: 20 points
        """
        pass

    def generate_ect_mcqs(self, count: int) -> list:
        """Generate MCQs on ECT indications, consent, side effects"""
        pass
```

#### Deliverables
- [ ] ECT counseling framework (50 LOC)
- [ ] ECT OSCE station generator (40 LOC)
- [ ] ECT MCQ generator (30 LOC)

#### Success Criteria
- ✅ Can generate ECT counseling OSCE stations
- ✅ Victorian Mental Health Act ECT provisions accurate
- ✅ Can generate 10 ECT-related MCQs
- ✅ Medicare item numbers correct

---

### Component 6: 17 Psychiatry Topics Coverage
**LOC:** 150 lines
**Priority:** P1 (Comprehensive coverage)
**Status:** ⏳ PENDING

#### Topic Coverage Validation
```python
class PsychiatryTopicsCoverage:
    """
    Validate agent covers all 17 high-yield psychiatry topics

    Topics:
    1. Major Depressive Disorder ✅
    2. Bipolar Disorder ✅
    3. Generalized Anxiety Disorder ✅
    4. Panic Disorder ✅
    5. Social Anxiety Disorder ✅
    6. PTSD ✅
    7. OCD (Obsessive-Compulsive Disorder)
    8. Schizophrenia ✅
    9. Schizoaffective Disorder
    10. Delusional Disorder
    11. Eating Disorders (Anorexia, Bulimia)
    12. Substance Use Disorders (Alcohol, Opioids, Stimulants)
    13. Personality Disorders (Borderline, Antisocial)
    14. ADHD (Adult diagnosis and treatment)
    15. Dementia (Alzheimer's, Vascular, Lewy Body)
    16. Delirium (vs. Dementia vs. Depression)
    17. Grief and Bereavement (normal vs. pathological)

    For Each Topic:
    - DSM-5 diagnostic criteria
    - First-line treatment (medication + therapy)
    - Australian guideline alignment (RANZCP)
    - 10 MCQs generated
    - 1 OSCE station created
    """

    def validate_topic_coverage(self) -> dict:
        """Check if all 17 topics have complete coverage"""
        pass

    def generate_topic_mcqs(self, topic: str, count: int = 10) -> list:
        """Generate MCQs for specific topic"""
        pass

    def generate_topic_osce(self, topic: str) -> dict:
        """Generate OSCE station for specific topic"""
        pass
```

#### Deliverables
- [ ] Topic coverage validator (30 LOC)
- [ ] Missing topic content generator (70 LOC)
- [ ] Topic-specific MCQ generator (50 LOC)

#### Success Criteria
- ✅ All 17 topics validated
- ✅ Can generate 10 MCQs per topic (170 total)
- ✅ Can generate 1 OSCE station per topic (17 total)
- ✅ RANZCP guideline compliance for all topics

---

### Week 2 Summary
**Starting LOC:** 400
**New Code:** 450 LOC (Medications 180 + ECT 120 + Topics 150)
**Ending LOC:** 850 ✅
**Progress:** 100% of target

---

## Integration with RAG System

### RAG Query Patterns for Psychiatry

#### Pattern 1: Diagnostic Criteria
```python
query = "DSM-5 criteria for major depressive disorder"
results = rag.query(query, top_k=3)
# Expected sources:
# - DSM-5 Diagnostic and Statistical Manual
# - RANZCP Clinical Practice Guidelines - Depression
# - UpToDate: Major Depressive Disorder
```

#### Pattern 2: Treatment Guidelines
```python
query = "First-line treatment severe depression RANZCP"
results = rag.query(query, top_k=3)
# Expected sources:
# - RANZCP CPG: Mood Disorders
# - Therapeutic Guidelines: Psychotropic
# - Australian Medicines Handbook: Antidepressants
```

#### Pattern 3: Medication Side Effects
```python
query = "Clozapine agranulocytosis monitoring TGA"
results = rag.query(query, top_k=3)
# Expected sources:
# - TGA Clozapine Patient Monitoring System guidelines
# - Australian Medicines Handbook: Antipsychotics
# - RANZCP Clozapine guidelines
```

#### Pattern 4: Legal/Ethical
```python
query = "NSW Mental Health Act involuntary admission criteria"
results = rag.query(query, top_k=3)
# Expected sources:
# - NSW Mental Health Act 2007
# - RANZCP Position Statement: Involuntary Treatment
# - NSW Health Mental Health Act Guidelines
```

### Citation Extraction
All generated MCQs and OSCE modules must include:
- **Primary source:** Australian guideline (RANZCP, eTG Psychotropic, AMH)
- **Secondary source:** Major textbook (Davidson's, Harrison's) or DSM-5
- **Page numbers:** Exact page citation from RAG metadata
- **Confidence score:** >0.90 for auto-approval

---

## Testing & Validation

### Unit Tests
```python
# tests/test_med_009_psychiatry.py

def test_mse_template_generation():
    """Test MSE template for schizophrenia"""
    agent = MED009PsychiatryExpert()
    mse = agent.mse.generate_mse_template('schizophrenia')

    assert 'thought_content' in mse
    assert 'delusions' in mse['thought_content']
    assert 'perception' in mse
    assert 'hallucinations' in mse['perception']

def test_suicide_risk_assessment():
    """Test suicide risk stratification"""
    agent = MED009PsychiatryExpert()
    patient = {
        'age': 35,
        'gender': 'male',
        'depression': True,
        'suicidal_ideation': True,
        'plan': True,
        'means_access': True,
        'prior_attempts': 1
    }
    risk = agent.risk.assess_suicide_risk(patient)

    assert risk['risk_level'] == 'HIGH'
    assert 'prior_attempt' in risk['risk_factors']
    assert 'recommendations' in risk
    assert 'Emergency Department' in risk['recommendations'][0]

def test_mental_health_act_criteria():
    """Test MHA involuntary admission criteria"""
    agent = MED009PsychiatryExpert()
    patient = {
        'state': 'NSW',
        'mental_illness': True,
        'risk_to_self': True,
        'treatment_available': True,
        'capacity_to_consent': False
    }
    result = agent.mha.check_involuntary_criteria('NSW', patient)

    assert result['meets_criteria'] == True
    assert len(result['criteria_met']) == 3
    assert 'Section 27' in result['schedule_type']
```

### Integration Tests
- [ ] Generate 100 psychiatry MCQs end-to-end
- [ ] Generate 17 psychiatry OSCE modules
- [ ] Validate all citations against RAG database
- [ ] Test QA-003 automated validation (>90% pass rate)

### Manual Review (10% Sample)
- [ ] 10 MCQs reviewed by psychiatrist
- [ ] 2 OSCE modules reviewed for clinical accuracy
- [ ] Mental Health Act provisions verified by legal expert
- [ ] Target quality score: 4.5/5.0

---

## Success Metrics

| Metric | Target | Status | Notes |
|--------|--------|--------|-------|
| **Final LOC** | 850+ | 🟡 IN PROGRESS | Week 2 target |
| **MSE Framework** | Complete | 🟡 PENDING | Week 1 |
| **Risk Assessment** | Complete | 🟡 PENDING | Week 1 |
| **Mental Health Act** | 3 states | 🟡 PENDING | Week 1 |
| **Medication Tools** | 20+ drugs | 🟡 PENDING | Week 2 |
| **ECT Counseling** | Complete | 🟡 PENDING | Week 2 |
| **Topic Coverage** | 17 topics | 🟡 PENDING | Week 2 |
| **MCQ Generation** | 400 total | 🟡 IN PROGRESS | Week 1-2 |
| **OSCE Generation** | 17 total | 🟡 IN PROGRESS | Week 1-2 |
| **Test Coverage** | 80%+ | 🟡 PENDING | Week 2 |

---

## Related Documents
- [Week 1 Execution Plan](../weekly/WEEK_01_EXECUTION.md)
- [Week 2 Execution Plan](../weekly/WEEK_02_EXECUTION.md)
- [Psychiatry Content Plan](../../02_CONTENT_PLANS/by_specialty/psychiatry_plan.md)
- [QA-003 Upgrade Plan](../QA_003_UPGRADE_PLAN.md)

---

**Last Updated:** 2026-01-24
**Status:** 🟡 IN PROGRESS (Week 1)
**Owner:** MED-009 Psychiatry Expert Agent
**Next Review:** 2026-01-31 (End of Week 1)
**Final Review:** 2026-02-07 (End of Week 2)
