# Improved RAG Query Templates
**Week 2 Day 1 - Achieving 0.85+ Semantic Scores**

**Problem:** Current RAG queries too generic → semantic scores of 0.70-0.75
**Goal:** Specific medical queries → semantic scores of 0.85-0.95
**Target:** 90%+ Tier 1 auto-approval rate

---

## Current vs. Improved Query Patterns

### Pattern 1: Depression Treatment

**❌ Current (Generic):**
```
"depression treatment guidelines SSRI selection"
```
**Result:** Semantic score ~0.74

**✅ Improved (Specific):**
```
"major depressive disorder F32.9 DSM-5 criteria SSRI antidepressant first-line therapy sertraline therapeutic guidelines eTG psychiatry Australia"
```
**Expected:** Semantic score ~0.88

**Key additions:**
- ICD-10 code: F32.9
- Classification: DSM-5
- Specific medication: sertraline
- Australian source: eTG
- Geographic: Australia

---

### Pattern 2: Suicide Risk Assessment

**❌ Current (Generic):**
```
"suicide risk assessment tools"
```
**Result:** Semantic score ~0.72

**✅ Improved (Specific):**
```
"suicide risk stratification SAD PERSONS scale Columbia C-SSRS emergency psychiatry immediate risk factors protective factors therapeutic guidelines Australia RANZCP"
```
**Expected:** Semantic score ~0.87

**Key additions:**
- Specific tools: SAD PERSONS, Columbia C-SSRS
- Clinical context: emergency psychiatry
- Risk terminology: immediate risk, protective factors
- Australian guidelines: eTG, RANZCP

---

### Pattern 3: Mental Health Act

**❌ Current (Generic):**
```
"mental health act involuntary admission"
```
**Result:** Semantic score ~0.71

**✅ Improved (Specific):**
```
"Mental Health Act 2007 NSW section 19 section 27 involuntary admission criteria mentally ill risk of harm treatment required less restrictive alternative emergency detention Australia"
```
**Expected:** Semantic score ~0.90

**Key additions:**
- Specific legislation: Mental Health Act 2007 (NSW)
- Sections: 19, 27
- Legal criteria: 4 criteria explicitly named
- Geographic: NSW, Australia

---

### Pattern 4: Antipsychotic Medications

**❌ Current (Generic):**
```
"antipsychotic medication schizophrenia"
```
**Result:** Semantic score ~0.73

**✅ Improved (Specific):**
```
"first-episode psychosis FEP antipsychotic medication olanzapine risperidone clozapine TGA monitoring metabolic syndrome extrapyramidal symptoms EPS therapeutic guidelines eTG psychiatry section 11 Australia"
```
**Expected:** Semantic score ~0.89

**Key additions:**
- Clinical terminology: FEP, EPS
- Specific medications: olanzapine, risperidone, clozapine
- Monitoring: TGA requirements, metabolic syndrome
- eTG section: Section 11
- Regulatory: TGA (Australia)

---

### Pattern 5: Bipolar Disorder

**❌ Current (Generic):**
```
"bipolar disorder mood stabilizer lithium"
```
**Result:** Semantic score ~0.72

**✅ Improved (Specific):**
```
"bipolar affective disorder F31 DSM-5 criteria manic episode mood stabilizer lithium valproate monitoring therapeutic range 0.6-1.2 mmol/L TFTs renal function therapeutic guidelines eTG Australia"
```
**Expected:** Semantic score ~0.88

**Key additions:**
- ICD-10: F31
- Specific drugs: lithium, valproate
- Therapeutic range: 0.6-1.2 mmol/L
- Monitoring: TFTs, renal function
- Australian guidelines

---

## Query Construction Formula

### Standard Template:
```
[Diagnosis/Condition] + [ICD/DSM Code] + [Classification] + [Specific Treatment/Tool] + [Monitoring/Side Effects] + [Australian Guideline] + [Geographic Specificity]
```

### Example Application (Eating Disorders):

**Components:**
1. Diagnosis: "anorexia nervosa"
2. ICD Code: "F50.0"
3. Classification: "DSM-5 criteria"
4. Treatment: "refeeding syndrome prevention medical admission BMI <15"
5. Monitoring: "phosphate monitoring cardiac monitoring"
6. Australian Guideline: "therapeutic guidelines eTG"
7. Geographic: "Australia"

**Final Query:**
```
"anorexia nervosa F50.0 DSM-5 criteria eating disorder medical admission BMI less than 15 refeeding syndrome risk phosphate monitoring cardiac monitoring therapeutic guidelines eTG Australia"
```

---

## Australian Source Prioritization

### Always Include One or More:
- "therapeutic guidelines" / "eTG"
- "RANZCP" (Royal Australian and New Zealand College of Psychiatrists)
- "NSW Health" / "Mental Health Act 2007 NSW"
- "Talley O'Connor" / "Talley and O'Connor"
- "AMH" (Australian Medicines Handbook)
- "MIMS" (Monthly Index of Medical Specialties)
- "TGA" (Therapeutic Goods Administration)
- "Australia" / "Australian"

### Boost Value:
- +0.15 confidence for Australian sources
- Critical for ICRP preparation

---

## Implementation Strategy

### For MCQ Generation Scripts:

**Before (Week 1):**
```python
def query_rag_for_citations(self, query: str, top_k: int = 5):
    # Simple query
    query = "depression treatment SSRI"
    ...
```

**After (Week 2):**
```python
def query_rag_for_citations_improved(
    self,
    topic: str,
    icd_code: str = None,
    classification: str = None,
    specific_terms: list = None,
    australian_source: str = "therapeutic guidelines eTG",
    top_k: int = 5
):
    # Construct specific query
    query_parts = [topic]

    if icd_code:
        query_parts.append(icd_code)
    if classification:
        query_parts.append(classification)
    if specific_terms:
        query_parts.extend(specific_terms)
    query_parts.append(australian_source)
    query_parts.append("Australia")

    query = " ".join(query_parts)
    # Example: "major depressive disorder F32.9 DSM-5 criteria SSRI therapeutic guidelines eTG Australia"
    ...
```

---

## Expected Impact

### Conservative Estimate:
- Current semantic scores: 0.70-0.75
- Improved semantic scores: 0.85-0.90
- With existing weights (60/20/10/10): Overall confidence 0.88-0.92
- **Result: 60-80% Tier 1 rate**

### Optimistic Estimate:
- Improved semantic scores: 0.88-0.95
- With weights: Overall confidence 0.90-0.95
- **Result: 80-95% Tier 1 rate**

### Combined with Other Improvements:
- Australian source boost: +0.015 per citation
- Page tolerance ±5: reduces false negatives
- **Result: 90%+ Tier 1 rate achievable**

---

## Testing Plan

### Phase 1: Proof of Concept (Day 1)
1. Create 5 test MCQs with improved queries
2. Measure semantic scores
3. Target: 80%+ (4/5) have semantic >0.85

### Phase 2: Scale (Day 2)
1. Regenerate 10 Tier 3 MCQs
2. Validate improvement
3. Target: 70%+ move to Tier 1

### Phase 3: Full Rollout (Day 3-4)
1. Update all MCQ generation scripts
2. Regenerate remaining Tier 3 MCQs
3. Generate new cardiology MCQs with improved queries
4. Target: 90%+ Tier 1 on new content

---

## Checklist for Each Query

Before querying RAG, ensure query includes:

- [ ] Specific diagnosis/condition (not generic)
- [ ] ICD-10 or DSM-5 code (if applicable)
- [ ] Specific medications/tools/scales (not "antidepressant" but "sertraline")
- [ ] Monitoring/side effects (specific parameters)
- [ ] Australian guideline reference (eTG, RANZCP, etc.)
- [ ] Geographic specificity ("Australia", "NSW")
- [ ] Clinical context (e.g., "emergency", "first-line", "treatment-resistant")

**Target length:** 15-25 words per query (specific but not excessive)

---

**Status:** Template created, ready for implementation
**Next:** Test on 5 sample MCQs
**Expected Result:** Semantic scores 0.85-0.95, Tier 1 rate 80%+
