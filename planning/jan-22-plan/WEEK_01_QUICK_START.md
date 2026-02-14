# Week 1 Quick Start Guide
**Date:** 2026-01-24 (Day 1)
**Duration:** 5 days (Monday-Friday)
**Goal:** Start MED-009 Psychiatry expansion + Generate 100 MCQs + 5 OSCE modules

---

## 🎯 This Week's Objectives

1. **MED-009 Psychiatry:** Expand from 115 LOC → 400 LOC (50%)
2. **Generate:** 100 psychiatry MCQs with RAG citations
3. **Create:** 5 psychiatry OSCE modules
4. **QA-003:** Design + implement RAG validation (50 LOC)
5. **Audit:** Catalog all 46 existing OSCE modules

---

## ✅ Prerequisites (Already Complete)

- [x] RAG system operational (42,647 vectors)
- [x] Qdrant vector database running
- [x] S-PubMedBert embedding model deployed
- [x] Citation extraction working
- [x] All planning documents created

**You are ready to begin! 🚀**

---

## 📅 Daily Breakdown

### **Day 1 (Monday) - TODAY**

#### Morning (4 hours): MED-009 Mental State Examination
**File:** `src/agents/medical/med_009_psychiatry.py`

**Task:** Add Mental State Examination (MSE) framework (120 LOC)

```python
class MentalStateExamination:
    """
    Structured MSE assessment tool
    """

    def generate_mse_template(self, condition: str) -> dict:
        """
        Generate MSE findings for psychiatric condition

        Components:
        1. Appearance and Behavior
        2. Speech
        3. Mood and Affect
        4. Thought Form and Content
        5. Perception
        6. Cognition
        7. Insight and Judgment
        """
        pass

    def generate_mse_osce_station(self, difficulty: str) -> dict:
        """Create OSCE station for MSE assessment"""
        pass

    def generate_mse_mcqs(self, topic: str, count: int) -> list:
        """Generate MCQs testing MSE knowledge"""
        pass
```

**Success Criteria:**
- [ ] MSE framework code complete (120 LOC)
- [ ] Can generate MSE template for schizophrenia
- [ ] Unit tests passing

---

#### Afternoon (4 hours): Generate 20 Depression MCQs

**Task:** Generate first batch of MCQs

**Process:**
1. Use MED-009 agent to generate MCQs
2. RAG queries for citations
3. QA-003 validation

**Example Command:**
```python
# Generate 20 depression MCQs
from src.agents.medical.med_009_psychiatry import MED009PsychiatryExpert
from src.rag.query_engine import query_rag

agent = MED009PsychiatryExpert()

topics = [
    'major_depressive_disorder_diagnosis',
    'antidepressant_selection_ssri',
    'treatment_resistant_depression',
    'depression_in_elderly',
    'postpartum_depression'
]

mcqs = []
for topic in topics[:4]:  # 4 topics × 5 MCQs = 20
    batch = agent.generate_mcqs(
        topic=topic,
        count=5,
        difficulty='medium'
    )
    mcqs.extend(batch)

# Save
save_mcqs(mcqs, 'data/mcqs/psychiatry_depression_day1.json')
```

**Success Criteria:**
- [ ] 20 depression MCQs generated
- [ ] All have RAG citations (confidence >0.90)
- [ ] Saved to `data/mcqs/psychiatry_depression_day1.json`

---

### **Day 2 (Tuesday)**

#### Morning (4 hours): MED-009 Risk Assessment Tools
**File:** `src/agents/medical/med_009_psychiatry.py`

**Task:** Add suicide and violence risk assessment (100 LOC)

```python
class RiskAssessmentTools:
    """
    Suicide and violence risk assessment
    """

    def assess_suicide_risk(self, patient_data: dict) -> dict:
        """
        Stratify suicide risk: LOW, MODERATE, HIGH, IMMINENT

        Factors:
        - Demographics (age, gender)
        - Psychiatric history
        - Suicidal ideation, plan, means
        - Prior attempts
        - Protective factors
        """
        pass

    def generate_safety_plan(self, patient_data: dict) -> dict:
        """Generate personalized safety plan"""
        pass

    def generate_risk_mcqs(self, scenario_type: str, count: int) -> list:
        """Generate risk assessment MCQs"""
        pass
```

**Success Criteria:**
- [ ] Risk assessment code complete (100 LOC)
- [ ] Can stratify suicide risk (LOW/MODERATE/HIGH/IMMINENT)
- [ ] Includes Australian crisis resources (Lifeline 13 11 14)

---

#### Afternoon (4 hours): Generate 20 Anxiety + Bipolar MCQs

**Topics:**
- Generalized anxiety disorder (GAD)
- Panic disorder
- PTSD
- Bipolar disorder (mania)
- Mood stabilizers (lithium, valproate)

**Target:** 20 MCQs (10 anxiety + 10 bipolar)

---

### **Day 3 (Wednesday)**

#### Morning (4 hours): MED-009 Mental Health Act Compliance
**File:** `src/agents/medical/med_009_psychiatry.py`

**Task:** Add Australian Mental Health Act provisions (80 LOC)

```python
class MentalHealthActCompliance:
    """
    NSW/VIC/QLD Mental Health Act provisions
    """

    def check_involuntary_criteria(self, state: str, patient_data: dict) -> dict:
        """
        Check if patient meets criteria for involuntary admission

        NSW Mental Health Act 2007:
        - Mental illness (functional impairment)
        - Risk to self or others
        - Treatment available
        - Least restrictive alternative

        Returns:
            meets_criteria: bool
            schedule_type: str (e.g., "Section 27")
        """
        pass

    def generate_mha_mcqs(self, state: str, count: int) -> list:
        """Generate Mental Health Act MCQs"""
        pass
```

**Success Criteria:**
- [ ] Mental Health Act code complete (80 LOC)
- [ ] Covers NSW, VIC, QLD provisions
- [ ] Can generate 10 MHA MCQs

---

#### Afternoon (4 hours): Generate 25 Psychotic Disorder MCQs + QA-003 Design

**MCQ Topics:**
- Schizophrenia diagnosis (DSM-5)
- First-episode psychosis
- Antipsychotic medications (typical vs. atypical)
- Clozapine monitoring (TGA requirements)
- Medication side effects (EPS, metabolic syndrome)

**Target:** 25 MCQs

**QA-003:** Start design document
- [ ] RAG validation workflow diagram
- [ ] Three-tier confidence scoring design
- [ ] Test cases (10 sample MCQs with expected scores)

---

### **Day 4 (Thursday)**

#### Morning (4 hours): Generate 20 Suicide Risk + MHA MCQs

**Topics:**
- Suicide risk assessment (SAD PERSONS scale)
- Columbia Suicide Severity Rating Scale
- NSW Mental Health Act involuntary admission
- Community Treatment Orders (CTOs)
- Emergency detention powers

**Target:** 20 MCQs (15 suicide risk + 5 MHA)

---

#### Afternoon (4 hours): QA-003 Implementation Start

**File:** `src/agents/qa/qa_003_rag_validator.py`

**Task:** Implement RAG citation validator (50 LOC initial)

```python
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

class RAGCitationValidator:
    """
    Validate citations using RAG system
    """

    def __init__(self, qdrant_url: str = "http://localhost:6333"):
        self.client = QdrantClient(url=qdrant_url)
        self.collection = "medical_knowledge"
        self.embedder = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    def validate_citation(self, citation_text: str, expected_pages: str = None) -> dict:
        """
        Validate a single citation

        Returns:
            {
                'valid': bool,
                'confidence': float (0.0-1.0),
                'matches': list[dict],
                'recommendation': str  # 'approve', 'llm_verify', 'reject'
            }
        """
        # Embed citation
        embedding = self.embedder.encode(citation_text)

        # Query Qdrant
        results = self.client.search(
            collection_name=self.collection,
            query_vector=embedding,
            limit=5
        )

        # Calculate confidence
        if not results:
            return {'valid': False, 'confidence': 0.0, 'recommendation': 'reject'}

        top_score = results[0].score
        confidence = top_score

        # Determine recommendation
        if confidence >= 0.90:
            return {'valid': True, 'confidence': confidence, 'recommendation': 'approve'}
        elif confidence >= 0.75:
            return {'valid': True, 'confidence': confidence, 'recommendation': 'llm_verify'}
        else:
            return {'valid': False, 'confidence': confidence, 'recommendation': 'reject'}
```

**Success Criteria:**
- [ ] RAGCitationValidator class implemented (50 LOC)
- [ ] Can validate 20 sample MCQs
- [ ] Validation time <5 seconds per MCQ

---

### **Day 5 (Friday)**

#### Morning (4 hours): Generate 5 OSCE Modules + Final 15 MCQs

**OSCE Modules:**
1. Major Depressive Disorder History (8 minutes)
2. Mental State Examination (8 minutes)
3. Suicide Risk Assessment (8 minutes)
4. Explain Antidepressant Therapy (8 minutes)
5. Mental Health Act Scenario (8 minutes)

**Final MCQs:** 15 MCQs to reach 100 total
- Fill any topic gaps
- Review difficulty distribution (40% easy, 40% medium, 20% hard)

---

#### Afternoon (4 hours): OSCE Audit + Week Review

**OSCE Audit:**
- [ ] List all 46 existing OSCE modules
- [ ] Categorize by specialty
- [ ] Identify modules without citations
- [ ] Create `existing_osce_audit.csv`

**QA-003 Testing:**
- [ ] Test validator on 20 MCQs
- [ ] Calculate auto-approval rate
- [ ] Document any issues

**Week Review:**
- [ ] Count total MCQs generated (target: 100)
- [ ] Count total OSCE modules (target: 5)
- [ ] Check MED-009 LOC count (target: 400)
- [ ] Update PROJECT_STATUS_TRACKER.md

---

## 📊 Success Criteria (End of Week 1)

### Code
- [ ] **MED-009:** 400 LOC (115 → 400)
  - [ ] Mental State Examination (120 LOC)
  - [ ] Risk Assessment Tools (100 LOC)
  - [ ] Mental Health Act Compliance (80 LOC)

### Content
- [ ] **MCQs:** 100 psychiatry MCQs
  - [ ] Depression (25)
  - [ ] Anxiety (20)
  - [ ] Psychotic disorders (25)
  - [ ] Bipolar disorder (15)
  - [ ] Suicide risk + MHA (15)
- [ ] **OSCE:** 5 psychiatry modules
- [ ] **QA-003:** Design document + 50 LOC implementation

### Quality
- [ ] **Citations:** All MCQs have 2+ Australian references
- [ ] **RAG Confidence:** >0.90 average
- [ ] **Difficulty:** 40% easy, 40% medium, 20% hard
- [ ] **OSCE Audit:** 46 modules catalogued

---

## 🚨 Potential Issues & Solutions

### Issue 1: RAG Citations Not Found
**Symptom:** RAG returns low confidence (<0.75)
**Solution:**
- Refine query (add more context)
- Try alternative phrasing
- Check if source in database (42,647 vectors)
- Fallback to manual citation if needed

### Issue 2: MCQ Generation Slow
**Symptom:** >10 seconds per MCQ
**Solution:**
- Optimize RAG query (reduce top_k from 5 to 3)
- Cache common citations
- Generate in batches

### Issue 3: MED-009 Code Complexity
**Symptom:** Components taking longer than expected
**Solution:**
- Focus on core functionality first
- Defer advanced features to Week 2
- Use simpler implementation if needed

---

## 📁 File Structure (Week 1)

```
src/agents/medical/
└── med_009_psychiatry.py ← Expand 115 → 400 LOC
    ├── MentalStateExamination (NEW)
    ├── RiskAssessmentTools (NEW)
    └── MentalHealthActCompliance (NEW)

src/agents/qa/
└── qa_003_rag_validator.py ← Create new file (50 LOC)
    └── RAGCitationValidator (NEW)

data/mcqs/
├── psychiatry_depression_day1.json (20 MCQs)
├── psychiatry_anxiety_bipolar_day2.json (20 MCQs)
├── psychiatry_psychosis_day3.json (25 MCQs)
├── psychiatry_suicide_mha_day4.json (20 MCQs)
└── psychiatry_final_day5.json (15 MCQs)
→ Total: 100 MCQs

data/osce/
└── psychiatry/
    ├── depression_history.md
    ├── mental_state_examination.md
    ├── suicide_risk_assessment.md
    ├── antidepressant_counseling.md
    └── mental_health_act_scenario.md
→ Total: 5 OSCE modules

planning/jan-22-plan/
├── existing_osce_audit.csv (NEW)
└── qa_003_design.md (NEW)
```

---

## 🔗 Quick Links

### Documentation
- **[Week 1 Detailed Plan](weekly/WEEK_01_EXECUTION.md)** - Full 40-page breakdown
- **[MED-009 Expansion Plan](agents/MED_009_PSYCHIATRY_EXPANSION.md)** - Agent details
- **[QA-003 Upgrade Plan](QA_003_UPGRADE_PLAN.md)** - QA validation
- **[Project Status Tracker](PROJECT_STATUS_TRACKER.md)** - Real-time dashboard

### Code Examples
- See Week 1 Execution Plan for detailed code snippets
- RAG query examples in RAG_INTEGRATION_STATUS.md
- MCQ template in Track 2 plan

### Support
- **Questions?** Check planning/jan-22-plan/README.md
- **Blocked?** Update PROJECT_STATUS_TRACKER.md with blocker
- **Issues?** Document in weekly execution plan

---

## 💡 Pro Tips

1. **Start small:** Generate 5 MCQs first, validate, then scale to 20
2. **Use RAG early:** Query RAG for citations before writing MCQs
3. **Test immediately:** Validate each component as you build it
4. **Update tracker:** Update PROJECT_STATUS_TRACKER.md daily
5. **Don't aim for perfection:** Week 1 is about getting started, Week 2 is refinement

---

## 📞 Daily Check-In Questions

**End of Each Day:**
- [ ] Did I complete today's LOC target?
- [ ] Did I generate today's MCQ target?
- [ ] Are all citations RAG-verified?
- [ ] Did I update the status tracker?
- [ ] Any blockers for tomorrow?

---

**Let's Begin! 🚀**

**Today (Day 1):**
1. Implement Mental State Examination (4 hours)
2. Generate 20 depression MCQs (4 hours)
3. Update status tracker

**Tomorrow Preview:**
- Risk assessment tools
- 20 anxiety/bipolar MCQs

---

**Last Updated:** 2026-01-24 (Day 1 Morning)
**Status:** 🟢 READY TO START
**Next Update:** End of Day 1
