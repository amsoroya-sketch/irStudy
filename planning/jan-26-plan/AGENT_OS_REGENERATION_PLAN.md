# Agent OS Medical Content Generation Plan
**Fresh Start: January 26, 2026**

**Status**: READY FOR EXECUTION
**Duration**: 3-5 days (realistic with quality gates)
**Quality Policy**: ZERO-ERROR (blocking validation at every step)

---

## Executive Summary

### Problem Statement
Previous generation produced **2,208 MCQs with 12,732 placeholder patterns (75% failure rate)** due to:
1. Generic `OllamaClient` used instead of Agent OS medical experts
2. Template-based generation violating Constraint 12 (LLM-powered)
3. No specialty routing (MED-001, MED-002, MED-009)
4. Post-generation validation instead of fail-fast pipeline

### Solution: Agent OS Architecture
- **Route by specialty** to medical expert agents (MED-001 through MED-010)
- **LLM-powered generation** with RAG citation content as context
- **Fail-fast validation** at pre-generation, incremental, and post-generation stages
- **Specialty-specific tools** (ECG interpretation, spirometry, MSE assessment)

### Scope (Proof of Concept)
- **Priority 1**: 200 Respiratory MCQs via MED-002
- **Priority 2**: 200 Cardiology MCQs via MED-001
- **Priority 3**: 200 Psychiatry MCQs via MED-009
- **Total**: 600 MCQs with 0 placeholders, 100% citations, summaries

---

## 1. Agent OS Routing Architecture

### 1.1 Specialty-to-Agent Mapping

```python
SPECIALTY_ROUTING = {
    # High-priority specialties (Jan-26 fresh start)
    'cardiology': {
        'agent_id': 'MED-001',
        'agent_class': 'CardiologyExpert',
        'file': 'src/agents/medical/med_001_cardiology.py',
        'size': '46KB',
        'tools': [
            'ECG_interpretation',
            'GRACE_score',
            'TIMI_risk',
            'CHA2DS2_VASc',
            'HAS_BLED',
            'heart_failure_risk'
        ],
        'focus_areas': [
            'Acute Coronary Syndrome',
            'Heart Failure',
            'Arrhythmias',
            'Hypertension',
            'Valvular Disease'
        ],
        'australian_guidelines': 'eTG Cardiovascular Section 5.x',
        'target_mcqs': 200
    },
    'respiratory': {
        'agent_id': 'MED-002',
        'agent_class': 'RespiratoryExpert',
        'file': 'src/agents/medical/med_002_respiratory.py',
        'size': '42KB',
        'tools': [
            'spirometry_interpretation',
            'CXR_interpretation',
            'Wells_PE_score',
            'CURB65_pneumonia',
            'asthma_control_test',
            'oxygen_delivery_calculator'
        ],
        'focus_areas': [
            'Asthma/COPD',
            'Pneumonia',
            'Pulmonary Embolism',
            'Respiratory Failure',
            'TB/Bronchiectasis'
        ],
        'australian_guidelines': 'eTG Respiratory Section 4.x',
        'target_mcqs': 200
    },
    'psychiatry': {
        'agent_id': 'MED-009',
        'agent_class': 'PsychiatryExpert',
        'file': 'src/agents/medical/med_009_psychiatry.py',
        'size': '91KB',
        'tools': [
            'PHQ9',
            'GAD7',
            'MSE_assessment',
            'BPRS',
            'YMRS',
            'Y_BOCS',
            'suicide_risk_assessment',
            'substance_use_screening'
        ],
        'focus_areas': [
            'Depression',
            'Anxiety Disorders',
            'Psychosis',
            'Bipolar Disorder',
            'Substance Use',
            'Dementia/Delirium'
        ],
        'australian_guidelines': 'RANZCP Clinical Practice Guidelines',
        'target_mcqs': 200
    }
}
```

### 1.2 Agent OS Task Delegation Pattern

```python
from src.agents.medical.med_001_cardiology import CardiologyExpert
from src.agents.medical.med_002_respiratory import RespiratoryExpert
from src.agents.medical.med_009_psychiatry import PsychiatryExpert

def route_to_agent(specialty: str, topic: str, mcq_count: int):
    """
    Route content generation to appropriate Agent OS medical expert
    
    Args:
        specialty: 'cardiology', 'respiratory', 'psychiatry'
        topic: Specific clinical topic (e.g., 'acute_coronary_syndrome')
        mcq_count: Number of MCQs to generate
    
    Returns:
        List of MCQs with 0 placeholders, 100% citations, summaries
    """
    routing = SPECIALTY_ROUTING.get(specialty)
    if not routing:
        raise ValueError(f"No Agent OS expert for specialty: {specialty}")
    
    # Initialize agent
    if specialty == 'cardiology':
        agent = CardiologyExpert(rag_system=rag_system)
    elif specialty == 'respiratory':
        agent = RespiratoryExpert(rag_system=rag_system)
    elif specialty == 'psychiatry':
        agent = PsychiatryExpert(rag_system=rag_system)
    
    # Generate MCQs with specialty-specific tools
    mcqs = agent.generate_mcqs(
        topic=topic,
        count=mcq_count,
        tools=routing['tools'],
        guidelines=routing['australian_guidelines'],
        constraints={
            'citations_per_mcq': 3,  # Constraint 11
            'llm_powered': True,     # Constraint 12
            'summary_required': True,
            'australian_context': True,
            'patient_demographics': True
        }
    )
    
    return mcqs
```

### 1.3 Agent Capabilities Matrix

| Agent ID | Specialty | Tools | Guidelines | Target MCQs | Priority |
|----------|-----------|-------|------------|-------------|----------|
| MED-001 | Cardiology | 6 tools (ECG, GRACE, TIMI, etc.) | eTG Cardiovascular 5.x | 200 | P2 |
| MED-002 | Respiratory | 6 tools (Spirometry, CXR, Wells, etc.) | eTG Respiratory 4.x | 200 | P1 |
| MED-009 | Psychiatry | 24 tools (PHQ-9, GAD-7, MSE, etc.) | RANZCP Guidelines | 200 | P3 |
| MED-003 | Gastroenterology | Future | eTG Gastro | 0 | Future |
| MED-004 | Endocrinology | Future | eTG Endocrine | 0 | Future |
| MED-005 | Neurology | Future | eTG Neurology | 0 | Future |
| MED-006 | Emergency | Future | eTG Emergency | 0 | Future |
| MED-007 | OB/GYN | Future | RANZCOG | 0 | Future |
| MED-008 | Paediatrics | Future | eTG Paediatric | 0 | Future |
| MED-010 | General Practice | Future | RACGP | 0 | Future |

---

## 2. Fail-Fast Validation Pipeline

### 2.1 Three-Stage Validation

```
┌────────────────────────────────────────────────────────────────────┐
│                  FAIL-FAST VALIDATION PIPELINE                     │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  STAGE 1: PRE-GENERATION VALIDATION (Blocking)                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 1. RAG System Operational?                               │    │
│  │    - Qdrant collection "medical_knowledge" exists        │    │
│  │    - 9,672+ chunks available                             │    │
│  │    - Embedding model loaded (S-PubMedBert-MS-MARCO)      │    │
│  │    - Query test: fetch 5 citations (expect >0.65 conf)   │    │
│  │    [FAIL → STOP - Fix RAG system before continuing]      │    │
│  │                                                           │    │
│  │ 2. LLM Client Operational?                               │    │
│  │    - Ollama service running (http://localhost:11434)     │    │
│  │    - Model available: llama3.2:latest                    │    │
│  │    - Health check: generate test response                │    │
│  │    [FAIL → STOP - Start Ollama before continuing]        │    │
│  │                                                           │    │
│  │ 3. Agent OS Medical Experts Loaded?                      │    │
│  │    - MED-001 CardiologyExpert imported                   │    │
│  │    - MED-002 RespiratoryExpert imported                  │    │
│  │    - MED-009 PsychiatryExpert imported                   │    │
│  │    - Each agent has RAG system injected                  │    │
│  │    [FAIL → STOP - Fix agent imports]                     │    │
│  │                                                           │    │
│  │ 4. Output Directory Ready?                               │    │
│  │    - Create: data-jan-26/mcqs/{specialty}/               │    │
│  │    - Permissions: writable                               │    │
│  │    [FAIL → STOP - Fix directory permissions]             │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  STAGE 2: INCREMENTAL VALIDATION (Per MCQ, 600 iterations)       │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ FOR EACH MCQ (1 to 600):                                 │    │
│  │                                                           │    │
│  │ 1. RAG Citation Fetch (Constraint 11)                    │    │
│  │    - Query RAG for topic (e.g., "myocardial_infarction") │    │
│  │    - Expect: 5 candidates, take top 3                    │    │
│  │    - Confidence threshold: >0.70                         │    │
│  │    [<3 citations → RETRY → FAIL → Skip topic]            │    │
│  │                                                           │    │
│  │ 2. Citation Content Extraction                           │    │
│  │    - Extract 'content' field from each citation          │    │
│  │    - Concatenate to form LLM context (500-1000 words)    │    │
│  │    - Validate: content not empty                         │    │
│  │    [Empty content → RETRY → FAIL → Skip citation]        │    │
│  │                                                           │    │
│  │ 3. LLM-Powered Generation (Constraint 12)                │    │
│  │    - Pass citation content to agent.generate_mcq()       │    │
│  │    - Agent uses specialty tools (ECG, spirometry, etc.)  │    │
│  │    - Generate: scenario, stem, options, explanation      │    │
│  │    - NO templates ("Clinical scenario for...")           │    │
│  │    [Placeholder detected → RETRY → FAIL → Skip]          │    │
│  │                                                           │    │
│  │ 4. Placeholder Pattern Scan (Immediate)                  │    │
│  │    - Check for: "Clinical scenario for"                  │    │
│  │    - Check for: "Question about"                         │    │
│  │    - Check for: "Option A", "Option B"                   │    │
│  │    - Check for: "Explanation for"                        │    │
│  │    [ANY found → RETRY (max 2) → FAIL → Skip MCQ]         │    │
│  │                                                           │    │
│  │ 5. Citation Count Validation                             │    │
│  │    - Count references in MCQ['references']               │    │
│  │    - Expect: exactly 3                                   │    │
│  │    [≠3 → RETRY → FAIL → Skip MCQ]                        │    │
│  │                                                           │    │
│  │ 6. Summary Field Validation                              │    │
│  │    - Check: MCQ['summary'] exists                        │    │
│  │    - Length: 50-200 characters                           │    │
│  │    - Content: 1-2 sentences                              │    │
│  │    [Missing/invalid → RETRY → FAIL → Skip MCQ]           │    │
│  │                                                           │    │
│  │ 7. Australian Context Validation                         │    │
│  │    - Check for: eTG reference OR RANZCP OR PBS           │    │
│  │    - Check for: Australian spelling (paediatric, etc.)   │    │
│  │    - Check for: Australian drug names (paracetamol)      │    │
│  │    [Missing → RETRY → FAIL → Skip MCQ]                   │    │
│  │                                                           │    │
│  │ 8. Patient Demographics Validation                       │    │
│  │    - Scenario includes: age (e.g., "45-year-old")        │    │
│  │    - Scenario includes: gender (male/female/other)       │    │
│  │    [Missing → RETRY → FAIL → Skip MCQ]                   │    │
│  │                                                           │    │
│  │ 9. Save MCQ (Only if ALL validations pass)               │    │
│  │    - Append to specialty JSON file                       │    │
│  │    - Log success: MCQ #{n} saved                         │    │
│  │    [Any validation failed → MCQ NOT saved]               │    │
│  └──────────────────────────────────────────────────────────┘    │
│                                                                    │
│  STAGE 3: POST-GENERATION VALIDATION (Blocking)                  │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ 1. Content Substance Check                               │    │
│  │    - Run: scripts/validate_content_substance.sh          │    │
│  │    - Expect: 0 placeholder patterns                      │    │
│  │    - Scan all files in data-jan-26/mcqs/                 │    │
│  │    [>0 placeholders → FAIL → Regenerate affected MCQs]   │    │
│  │                                                           │    │
│  │ 2. QA-003 RAG Citation Validator                         │    │
│  │    - Run: scripts/validate_mcqs_qa003.py                 │    │
│  │    - Expect: 100% Tier 1 auto-approval (confidence >0.90)│    │
│  │    - Check: All citations RAG-verified                   │    │
│  │    [<100% → REVIEW → Manual fix OR regenerate]           │    │
│  │                                                           │    │
│  │ 3. QA-001 Australian Compliance                          │    │
│  │    - Run: scripts/validate_australian_compliance.py      │    │
│  │    - Expect: 100% Australian spelling                    │    │
│  │    - Expect: 100% eTG/RANZCP/PBS citations               │    │
│  │    [<100% → FAIL → Regenerate non-compliant MCQs]        │    │
│  │                                                           │    │
│  │ 4. QA-002 Clinical Accuracy (Manual Review)              │    │
│  │    - Sample: 10% of MCQs (60 out of 600)                 │    │
│  │    - Check: Drug dosages correct                         │    │
│  │    - Check: Management appropriate                       │    │
│  │    - Check: Red flags identified                         │    │
│  │    [Errors found → Fix OR regenerate]                    │    │
│  │                                                           │    │
│  │ 5. Pre-Commit Hook (Final Gate)                          │    │
│  │    - Auto-runs on: git add data-jan-26/mcqs/             │    │
│  │    - Scans for: All 6 placeholder patterns               │    │
│  │    - Exit code 1 → BLOCKS commit                         │    │
│  │    [Placeholders found → CANNOT commit → Fix first]      │    │
│  └──────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────────┘
```

### 2.2 Validation Scripts Integration

| Script | Purpose | Exit Code | Blocking? |
|--------|---------|-----------|-----------|
| `validate_content_substance.sh` | Detect placeholder patterns | 1 if found | YES |
| `validate_mcqs_qa003.py` | RAG citation verification | 1 if <100% | YES |
| `validate_australian_compliance.py` | Australian standards check | 1 if violations | YES |
| `.git/hooks/pre-commit` | Final gate before commit | 1 if placeholders | YES |
| `validate_osces_qa003.py` | OSCE content validation | 1 if <100% | Future |

### 2.3 Retry Logic

```python
MAX_RETRIES = 2  # Total attempts: 1 initial + 2 retries = 3

def generate_mcq_with_retry(agent, topic, citations):
    """
    Generate MCQ with retry logic for transient failures
    
    Args:
        agent: Agent OS medical expert (MED-001, MED-002, MED-009)
        topic: Clinical topic (e.g., "myocardial_infarction")
        citations: List of 3 RAG citations with content
    
    Returns:
        MCQ dict if successful, None if all retries exhausted
    """
    for attempt in range(MAX_RETRIES + 1):
        try:
            # Generate MCQ
            mcq = agent.generate_mcq(topic, citations)
            
            # Incremental validation
            errors = validate_mcq_incremental(mcq)
            
            if not errors:
                return mcq  # SUCCESS
            
            if attempt < MAX_RETRIES:
                logger.warning(f"MCQ validation failed (attempt {attempt+1}/{MAX_RETRIES+1}): {errors}")
                logger.info(f"Retrying generation for topic: {topic}")
                continue
            else:
                logger.error(f"MCQ generation failed after {MAX_RETRIES+1} attempts: {topic}")
                return None  # EXHAUSTED RETRIES
        
        except Exception as e:
            if attempt < MAX_RETRIES:
                logger.warning(f"Exception during generation (attempt {attempt+1}): {e}")
                continue
            else:
                logger.error(f"Exception persisted after {MAX_RETRIES+1} attempts: {e}")
                return None
    
    return None  # Should not reach here
```

---

## 3. Specialty-Specific Generation Process

### 3.1 Priority 1: Respiratory MCQs (MED-002)

**Target**: 200 MCQs
**Agent**: `src/agents/medical/med_002_respiratory.py`
**Timeline**: Day 1-2

#### Topic Breakdown
1. **Asthma** (40 MCQs)
   - Acute asthma management
   - Chronic asthma control (stepwise approach)
   - Exercise-induced asthma
   - Occupational asthma
   - Asthma in pregnancy

2. **COPD** (40 MCQs)
   - COPD diagnosis (spirometry)
   - Acute exacerbation management
   - Oxygen therapy
   - Pulmonary rehabilitation
   - End-of-life care

3. **Pneumonia** (40 MCQs)
   - Community-acquired pneumonia (CURB-65)
   - Hospital-acquired pneumonia
   - Aspiration pneumonia
   - Atypical pneumonia
   - COVID-19 pneumonia

4. **Pulmonary Embolism** (40 MCQs)
   - Wells PE score
   - D-dimer interpretation
   - CTPA indications
   - Anticoagulation (DOACs vs warfarin)
   - DVT prophylaxis

5. **Other Respiratory** (40 MCQs)
   - Pleural effusion
   - Pneumothorax
   - Bronchiectasis
   - Interstitial lung disease
   - Tuberculosis

#### Agent OS Tools Applied
- **spirometry_interpretation**: FEV1/FVC ratios, obstruction patterns
- **CXR_interpretation**: Consolidation, pleural effusion, pneumothorax
- **Wells_PE_score**: PE risk stratification
- **CURB65_pneumonia**: Pneumonia severity assessment
- **asthma_control_test**: Symptom control scoring
- **oxygen_delivery_calculator**: Target saturations, delivery devices

#### Generation Prompt Template
```python
RESPIRATORY_MCQ_PROMPT = """
You are MED-002, a Respiratory Medicine Expert with 15+ years experience.

TASK: Generate {count} AMC-standard MCQs for {topic}.

MEDICAL KNOWLEDGE CONTEXT (RAG Citations):
{citation_content}

CONSTRAINTS:
1. Use Therapeutic Guidelines: Respiratory Section 4.x
2. Australian drug names: salbutamol (NOT albuterol), paracetamol (NOT acetaminophen)
3. Australian spelling: paediatric, anaesthesia, oesophagus
4. Patient demographics: age, gender in scenario (e.g., "52-year-old male")
5. Apply specialty tools: {tools}
6. Summary: 1-2 sentences (50-200 chars) capturing key learning point

MCQ STRUCTURE:
{{
  "id": "resp-{topic}-001",
  "question": {{
    "scenario": "Real clinical presentation with age, gender, vitals, imaging, labs",
    "stem": "Specific clinical question (NOT 'Question about...')",
    "options": {{
      "A": "Detailed option based on guidelines",
      "B": "Detailed option based on guidelines",
      "C": "Detailed option based on guidelines",
      "D": "Detailed option based on guidelines"
    }},
    "correct_answer": "A"
  }},
  "explanation": {{
    "why_correct": "Comprehensive explanation with eTG Section 4.x reference",
    "why_others_wrong": "Why B, C, D are incorrect",
    "key_points": ["Point 1", "Point 2", "Point 3"],
    "clinical_pearls": "Australian context (e.g., PBS restrictions)"
  }},
  "summary": "1-2 sentence summary of key learning point",
  "references": [
    {{
      "citation": "(Therapeutic Guidelines: Respiratory, Section 4.2.1, 2024)",
      "rag_confidence": 0.87,
      "page": "Section 4.2.1"
    }},
    {{
      "citation": "(Australian Asthma Handbook, p.45, 2023)",
      "rag_confidence": 0.82,
      "page": "45"
    }},
    {{
      "citation": "(Murtagh's General Practice, 8th ed, p.892)",
      "rag_confidence": 0.78,
      "page": "892"
    }}
  ],
  "metadata": {{
    "specialty": "respiratory",
    "topic": "{topic}",
    "difficulty": "intermediate",
    "australian_context": true,
    "tools_used": {tools}
  }}
}}

VALIDATION CHECKLIST (Self-Validate Before Returning):
- [ ] NO placeholder text ("Clinical scenario for", "Question about", "Option A")
- [ ] Exactly 3 RAG-verified citations (confidence >0.70)
- [ ] Summary field present (50-200 chars)
- [ ] Patient demographics (age, gender)
- [ ] Australian spelling and drug names
- [ ] eTG Respiratory Section 4.x referenced
- [ ] Specialty tools applied (spirometry, CXR, Wells, CURB-65)

Generate {count} MCQs meeting ALL requirements.
"""
```

#### Expected Output
```json
{
  "specialty": "respiratory",
  "agent_id": "MED-002",
  "generation_date": "2026-01-26",
  "mcq_count": 200,
  "mcqs": [
    {
      "id": "resp-asthma-001",
      "question": {
        "scenario": "A 28-year-old female presents to the ED with acute dyspnoea, wheeze, and chest tightness. She has a history of asthma. On examination, she is unable to speak in full sentences, respiratory rate 32/min, oxygen saturation 90% on room air, and peak expiratory flow 40% of her best. Chest auscultation reveals widespread wheeze.",
        "stem": "What is the most appropriate initial management?",
        "options": {
          "A": "Salbutamol 12 puffs via spacer, ipratropium bromide 8 puffs via spacer, oral prednisolone 50mg, oxygen to maintain saturation >93%",
          "B": "Nebulised salbutamol 5mg, oral prednisolone 25mg, observe for 30 minutes",
          "C": "Intravenous hydrocortisone 100mg, nebulised adrenaline, prepare for intubation",
          "D": "Oral prednisolone 50mg, discharge with asthma action plan review in 48 hours"
        },
        "correct_answer": "A"
      },
      "explanation": {
        "why_correct": "This patient has life-threatening asthma (unable to speak in sentences, RR >30, SpO2 <92%, PEF <50%). Initial management includes high-dose salbutamol (12 puffs), ipratropium (8 puffs), systemic corticosteroids (prednisolone 50mg), and supplemental oxygen. This is first-line therapy per eTG Respiratory Section 4.1.2.",
        "why_others_wrong": "B is inadequate dosing for life-threatening asthma. C is premature - intubation is reserved for near-fatal asthma after maximal medical therapy fails. D is dangerous - this patient requires immediate treatment and monitoring, not discharge.",
        "key_points": [
          "Life-threatening asthma: unable to speak in sentences, RR >30, SpO2 <92%, PEF <50%",
          "First-line: High-dose beta-agonist + ipratropium + systemic corticosteroids + oxygen",
          "eTG Respiratory Section 4.1.2 - Acute asthma management protocol"
        ],
        "clinical_pearls": "In Australia, salbutamol (NOT albuterol) is first-line. PBS listing allows 2 inhalers per month for asthma patients."
      },
      "summary": "Life-threatening asthma requires immediate high-dose bronchodilators, systemic corticosteroids, and oxygen therapy per eTG guidelines.",
      "references": [
        {
          "citation": "(Therapeutic Guidelines: Respiratory, Section 4.1.2, 2024)",
          "rag_confidence": 0.92,
          "page": "Section 4.1.2"
        },
        {
          "citation": "(Australian Asthma Handbook, p.67, 2023)",
          "rag_confidence": 0.88,
          "page": "67"
        },
        {
          "citation": "(AMC Clinical Exam Handbook, p.234)",
          "rag_confidence": 0.81,
          "page": "234"
        }
      ],
      "metadata": {
        "specialty": "respiratory",
        "topic": "asthma",
        "difficulty": "intermediate",
        "australian_context": true,
        "tools_used": ["asthma_severity_assessment", "oxygen_delivery_calculator"]
      }
    }
    // ... 199 more MCQs
  ],
  "validation_results": {
    "placeholder_patterns": 0,
    "citation_compliance": "100%",
    "summary_compliance": "100%",
    "australian_compliance": "100%",
    "qa003_tier1_approval": "95%"
  }
}
```

---

### 3.2 Priority 2: Cardiology MCQs (MED-001)

**Target**: 200 MCQs
**Agent**: `src/agents/medical/med_001_cardiology.py`
**Timeline**: Day 2-3

#### Topic Breakdown
1. **Acute Coronary Syndrome** (50 MCQs)
   - STEMI management
   - NSTEMI/unstable angina (GRACE/TIMI scoring)
   - Dual antiplatelet therapy
   - Post-MI complications
   - Secondary prevention

2. **Heart Failure** (50 MCQs)
   - Acute decompensated heart failure
   - Chronic HF management (GDMT)
   - HFrEF vs HFpEF
   - Diuretic therapy
   - Device therapy (ICD, CRT)

3. **Arrhythmias** (50 MCQs)
   - Atrial fibrillation (CHA2DS2-VASc, HAS-BLED)
   - Supraventricular tachycardia
   - Ventricular tachycardia
   - Heart blocks
   - Bradycardia management

4. **Hypertension** (30 MCQs)
   - Hypertensive emergency
   - First-line therapy
   - Resistant hypertension
   - Secondary hypertension
   - Target blood pressures

5. **Other Cardiology** (20 MCQs)
   - Valvular disease (AS, AR, MR, MS)
   - Pericardial disease
   - Cardiomyopathies
   - Infective endocarditis
   - Lipid management

#### Agent OS Tools Applied
- **ECG_interpretation**: STEMI criteria, arrhythmia diagnosis
- **GRACE_score**: ACS risk stratification
- **TIMI_risk**: Bleeding risk with anticoagulation
- **CHA2DS2_VASc**: Stroke risk in atrial fibrillation
- **HAS_BLED**: Bleeding risk in anticoagulation
- **heart_failure_risk**: Prognosis calculation

#### Generation Prompt (Similar structure to Respiratory)

---

### 3.3 Priority 3: Psychiatry MCQs (MED-009)

**Target**: 200 MCQs
**Agent**: `src/agents/medical/med_009_psychiatry.py`
**Timeline**: Day 3-4

#### Topic Breakdown
1. **Depression** (50 MCQs)
   - Major depressive disorder (PHQ-9)
   - Treatment-resistant depression
   - Antidepressant selection (SSRIs, SNRIs, TCAs)
   - ECT indications
   - Suicide risk assessment

2. **Anxiety Disorders** (40 MCQs)
   - Generalised anxiety disorder (GAD-7)
   - Panic disorder
   - Social anxiety disorder
   - OCD (Y-BOCS scoring)
   - PTSD

3. **Psychotic Disorders** (40 MCQs)
   - First-episode psychosis
   - Schizophrenia management
   - Antipsychotic selection
   - Extrapyramidal side effects
   - Clozapine monitoring

4. **Bipolar Disorder** (30 MCQs)
   - Manic episode (YMRS)
   - Depressive episode
   - Mood stabilisers (lithium, valproate)
   - Rapid cycling
   - Bipolar in pregnancy

5. **Other Psychiatry** (40 MCQs)
   - Substance use disorders
   - Dementia vs delirium
   - Eating disorders
   - Personality disorders
   - Mental Health Act (NSW)

#### Agent OS Tools Applied
- **PHQ9**: Depression severity screening
- **GAD7**: Anxiety severity screening
- **MSE_assessment**: Mental state examination framework
- **BPRS**: Brief psychiatric rating scale
- **YMRS**: Young mania rating scale
- **Y_BOCS**: Yale-Brown OCD scale
- **suicide_risk_assessment**: Risk stratification
- **substance_use_screening**: AUDIT, DAST tools

#### Unique Psychiatry Requirements
1. **RANZCP Guidelines**: Australian psychiatry standards
2. **Mental Health Act NSW**: Involuntary treatment criteria
3. **PBS Restrictions**: Authority requirements for clozapine, antipsychotics
4. **MSE Format**: Standardised psychiatric assessment structure

---

## 4. Quality Gates (Blocking Validation)

### 4.1 Pre-Generation Quality Gate

**Script**: `scripts-jan-26/pre_generation_check.sh`

```bash
#!/bin/bash
# Pre-generation quality gate (BLOCKING)

echo "=== PRE-GENERATION QUALITY GATE ==="

# 1. Check RAG system
echo "[1/4] Checking RAG system..."
if ! curl -s http://localhost:6333/collections/medical_knowledge > /dev/null; then
    echo "❌ FAIL: Qdrant not running. Start with: docker compose up -d qdrant"
    exit 1
fi

collection_info=$(curl -s http://localhost:6333/collections/medical_knowledge)
chunk_count=$(echo "$collection_info" | jq -r '.result.vectors_count // 0')

if [ "$chunk_count" -lt 9000 ]; then
    echo "❌ FAIL: RAG collection has only $chunk_count chunks (expect 9,672+)"
    exit 1
fi
echo "✅ PASS: RAG system operational ($chunk_count chunks)"

# 2. Check LLM client
echo "[2/4] Checking Ollama LLM..."
if ! curl -s http://localhost:11434/api/tags > /dev/null; then
    echo "❌ FAIL: Ollama not running. Start with: ollama serve"
    exit 1
fi

if ! ollama list | grep -q "llama3.2:latest"; then
    echo "❌ FAIL: llama3.2:latest not available. Pull with: ollama pull llama3.2:latest"
    exit 1
fi
echo "✅ PASS: Ollama operational (llama3.2:latest available)"

# 3. Check Agent OS medical experts
echo "[3/4] Checking Agent OS medical experts..."
for agent in med_001_cardiology med_002_respiratory med_009_psychiatry; do
    if ! python3 -c "from src.agents.medical.$agent import *" 2>/dev/null; then
        echo "❌ FAIL: Cannot import src.agents.medical.$agent"
        exit 1
    fi
done
echo "✅ PASS: All Agent OS medical experts imported successfully"

# 4. Check output directories
echo "[4/4] Checking output directories..."
mkdir -p data-jan-26/mcqs/{respiratory,cardiology,psychiatry}
if [ ! -w data-jan-26/mcqs/ ]; then
    echo "❌ FAIL: data-jan-26/mcqs/ not writable"
    exit 1
fi
echo "✅ PASS: Output directories ready"

echo ""
echo "========================================="
echo "✅ ALL PRE-GENERATION CHECKS PASSED"
echo "========================================="
echo "Ready to generate content with Agent OS"
exit 0
```

**Usage**:
```bash
cd /home/dev/Development/irStudy
./scripts-jan-26/pre_generation_check.sh

# Only proceed if exit code 0
if [ $? -eq 0 ]; then
    python3 scripts-jan-26/generate_respiratory_mcqs.py
fi
```

---

### 4.2 Incremental Quality Gate (Per MCQ)

**Function**: `validate_mcq_incremental(mcq)`

```python
def validate_mcq_incremental(mcq: dict) -> List[str]:
    """
    Validate single MCQ during generation (fail-fast)
    
    Args:
        mcq: MCQ dictionary from agent.generate_mcq()
    
    Returns:
        List of error messages (empty list = PASS)
    """
    errors = []
    
    # 1. Placeholder pattern check
    PLACEHOLDER_PATTERNS = [
        r"Clinical scenario for",
        r"Question about",
        r"^Option [A-D]$",
        r"Explanation for",
        r"Brief summary of",
        r"This MCQ tests"
    ]
    
    scenario = mcq.get('question', {}).get('scenario', '')
    stem = mcq.get('question', {}).get('stem', '')
    options = mcq.get('question', {}).get('options', {})
    explanation = str(mcq.get('explanation', {}))
    summary = mcq.get('summary', '')
    
    for pattern in PLACEHOLDER_PATTERNS:
        if re.search(pattern, scenario, re.IGNORECASE):
            errors.append(f"Placeholder in scenario: {pattern}")
        if re.search(pattern, stem, re.IGNORECASE):
            errors.append(f"Placeholder in stem: {pattern}")
        for opt_key, opt_val in options.items():
            if re.search(pattern, opt_val, re.IGNORECASE):
                errors.append(f"Placeholder in option {opt_key}: {pattern}")
        if re.search(pattern, explanation, re.IGNORECASE):
            errors.append(f"Placeholder in explanation: {pattern}")
        if re.search(pattern, summary, re.IGNORECASE):
            errors.append(f"Placeholder in summary: {pattern}")
    
    # 2. Citation count (Constraint 11)
    references = mcq.get('references', [])
    if len(references) != 3:
        errors.append(f"Expected 3 citations, got {len(references)}")
    
    # 3. Citation confidence threshold
    for ref in references:
        confidence = ref.get('rag_confidence', 0.0)
        if confidence < 0.70:
            errors.append(f"Citation confidence too low: {confidence} < 0.70")
    
    # 4. Summary field validation
    if not summary:
        errors.append("Summary field missing")
    elif len(summary) < 50 or len(summary) > 200:
        errors.append(f"Summary length {len(summary)} chars (expect 50-200)")
    
    # 5. Patient demographics check
    if not re.search(r'\d+-year-old', scenario):
        errors.append("Scenario missing patient age (e.g., '45-year-old')")
    if not re.search(r'(male|female|man|woman)', scenario, re.IGNORECASE):
        errors.append("Scenario missing patient gender")
    
    # 6. Australian context check
    australian_terms = [
        'Therapeutic Guidelines',
        'eTG',
        'RANZCP',
        'PBS',
        'Australian',
        'AMH',
        'RACGP'
    ]
    has_australian_ref = any(
        term in str(mcq.get('references', [])) for term in australian_terms
    )
    if not has_australian_ref:
        errors.append("No Australian guideline reference found")
    
    # 7. Australian spelling check (common mistakes)
    american_spellings = {
        'pediatric': 'paediatric',
        'anesthesia': 'anaesthesia',
        'esophagus': 'oesophagus',
        'hemoglobin': 'haemoglobin',
        'anemia': 'anaemia',
        'acetaminophen': 'paracetamol',
        'albuterol': 'salbutamol',
        'epinephrine': 'adrenaline'
    }
    mcq_text = str(mcq).lower()
    for american, australian in american_spellings.items():
        if american in mcq_text:
            errors.append(f"American spelling '{american}' found (use '{australian}')")
    
    return errors
```

---

### 4.3 Post-Generation Quality Gate

**Script**: `scripts-jan-26/post_generation_check.sh`

```bash
#!/bin/bash
# Post-generation quality gate (BLOCKING)

SPECIALTY=$1  # respiratory, cardiology, psychiatry
MCQ_FILE="data-jan-26/mcqs/${SPECIALTY}/${SPECIALTY}_200_mcqs.json"

echo "=== POST-GENERATION QUALITY GATE: $SPECIALTY ==="

# 1. Content substance check
echo "[1/4] Running content substance validator..."
if ! ./scripts/validate_content_substance.sh "$MCQ_FILE"; then
    echo "❌ FAIL: Placeholder patterns detected"
    echo "Action: Review $MCQ_FILE and regenerate affected MCQs"
    exit 1
fi
echo "✅ PASS: No placeholder patterns"

# 2. QA-003 RAG citation validator
echo "[2/4] Running QA-003 RAG citation validator..."
python3 scripts/validate_mcqs_qa003.py --file "$MCQ_FILE" --output "reports/${SPECIALTY}_qa003.json"
if [ $? -ne 0 ]; then
    echo "❌ FAIL: QA-003 validation failed"
    echo "Action: Review reports/${SPECIALTY}_qa003.json"
    exit 1
fi

# Check Tier 1 auto-approval rate
tier1_rate=$(jq -r '.summary.tier1_auto_approval_rate' "reports/${SPECIALTY}_qa003.json")
if (( $(echo "$tier1_rate < 0.70" | bc -l) )); then
    echo "❌ FAIL: Tier 1 auto-approval rate $tier1_rate < 70%"
    echo "Action: Regenerate low-confidence MCQs"
    exit 1
fi
echo "✅ PASS: QA-003 Tier 1 auto-approval rate: $tier1_rate"

# 3. Australian compliance check
echo "[3/4] Running Australian compliance validator..."
python3 scripts/validate_australian_compliance.py --file "$MCQ_FILE" --output "reports/${SPECIALTY}_australian.json"
if [ $? -ne 0 ]; then
    echo "❌ FAIL: Australian compliance violations found"
    echo "Action: Review reports/${SPECIALTY}_australian.json"
    exit 1
fi
echo "✅ PASS: 100% Australian compliance"

# 4. Summary statistics
echo "[4/4] Generating summary statistics..."
mcq_count=$(jq '. | length' "$MCQ_FILE")
summary_count=$(jq '[.[] | select(.summary != null)] | length' "$MCQ_FILE")
citation_count=$(jq '[.[] | .references | length] | add' "$MCQ_FILE")
avg_citations=$(echo "scale=2; $citation_count / $mcq_count" | bc)

echo ""
echo "========================================="
echo "GENERATION SUMMARY: $SPECIALTY"
echo "========================================="
echo "Total MCQs: $mcq_count"
echo "MCQs with summaries: $summary_count ($(echo "scale=1; 100 * $summary_count / $mcq_count" | bc)%)"
echo "Average citations per MCQ: $avg_citations"
echo "QA-003 Tier 1 approval: $tier1_rate"
echo ""
echo "✅ ALL POST-GENERATION CHECKS PASSED"
echo "========================================="

exit 0
```

**Usage**:
```bash
# After generating 200 respiratory MCQs
./scripts-jan-26/post_generation_check.sh respiratory

# Only proceed to next specialty if exit code 0
if [ $? -eq 0 ]; then
    echo "Respiratory MCQs validated. Proceeding to cardiology..."
    python3 scripts-jan-26/generate_cardiology_mcqs.py
fi
```

---

### 4.4 Pre-Commit Hook (Final Gate)

**File**: `.git/hooks/pre-commit` (already installed)

```bash
#!/bin/bash
# Pre-commit hook: Block placeholder content from being committed

echo "Running pre-commit validation..."

# Check only staged JSON files in data-jan-26/
staged_files=$(git diff --cached --name-only --diff-filter=ACM | grep '^data-jan-26/.*\.json$')

if [ -z "$staged_files" ]; then
    echo "No JSON files in data-jan-26/ staged for commit"
    exit 0
fi

# Run content substance validator on staged files
errors_found=0
for file in $staged_files; do
    if ./scripts/validate_content_substance.sh "$file"; then
        echo "✅ $file: PASS"
    else
        echo "❌ $file: FAIL (placeholder patterns detected)"
        errors_found=1
    fi
done

if [ $errors_found -eq 1 ]; then
    echo ""
    echo "========================================="
    echo "❌ COMMIT BLOCKED: Placeholder patterns detected"
    echo "========================================="
    echo "Action: Fix placeholder content before committing"
    echo "Run: ./scripts/validate_content_substance.sh <file>"
    exit 1
fi

echo "✅ All staged files passed validation"
exit 0
```

---

## 5. Success Metrics

### 5.1 Quantitative Metrics

| Metric | Target | Measurement | Validation |
|--------|--------|-------------|------------|
| **Agent OS Usage** | 100% | All 600 MCQs via MED-001/002/009 | Check `metadata.agent_id` field |
| **Placeholder Patterns** | 0 | Content substance validator | Exit code must be 0 |
| **Citation Count** | 3 per MCQ | Count `references` array | Exactly 3, no more, no less |
| **Citation Confidence** | >0.70 | Check `rag_confidence` field | All citations >0.70 |
| **Summary Compliance** | 100% | Check `summary` field exists | Length 50-200 chars |
| **Australian Compliance** | 100% | Spelling, drug names, guidelines | QA-001 validator exit code 0 |
| **QA-003 Tier 1 Approval** | >70% | RAG verification confidence >0.90 | Auto-approval rate calculation |
| **Patient Demographics** | 100% | Age + gender in scenario | Regex validation |
| **Specialty Tool Usage** | 100% | Check `metadata.tools_used` | Non-empty array |
| **LLM-Powered Generation** | 100% | No templates, all LLM output | Inverse of placeholder count |

### 5.2 Qualitative Metrics

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **Clinical Accuracy** | 100% | Manual review of 10% sample (60 MCQs) by medical expert |
| **Appropriate Difficulty** | Intermediate | AMC exam standard (Year 4-6 medical student) |
| **Realistic Scenarios** | 100% | Patient demographics, clinical presentation plausible |
| **Distractors Quality** | High | Incorrect options are plausible but clearly wrong |
| **Explanation Clarity** | High | Why correct answer is right AND why others are wrong |

### 5.3 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Generation Speed** | <30 seconds per MCQ | Time from RAG query to MCQ saved |
| **Retry Rate** | <10% | MCQs requiring retry due to validation failures |
| **Success Rate** | >90% | MCQs passing incremental validation on first attempt |
| **Total Generation Time** | 3-5 hours per specialty | 200 MCQs @ 30 sec each = 100 min + validation |

### 5.4 Success Criteria (Go/No-Go Decision)

**GO (Proceed to Next Specialty):**
- Placeholder patterns: 0
- QA-003 Tier 1 approval: >70%
- Australian compliance: 100%
- Summary compliance: 100%
- Citation compliance: 100% (3 per MCQ, all >0.70 confidence)

**NO-GO (Fix Before Proceeding):**
- Any placeholder pattern detected
- QA-003 Tier 1 approval <70%
- Australian compliance violations found
- Missing summaries detected
- Citation count ≠3 or confidence <0.70

---

## 6. Execution Timeline

### Day 1-2: Respiratory MCQs (MED-002)
**Duration**: 8-10 hours

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 0:00-0:30 | Pre-generation validation | PM | All quality gates PASS |
| 0:30-1:00 | Setup Agent OS routing | PM | `scripts-jan-26/generate_respiratory_mcqs.py` |
| 1:00-2:00 | Generate Asthma MCQs (40) | MED-002 | `data-jan-26/mcqs/respiratory/asthma.json` |
| 2:00-3:00 | Generate COPD MCQs (40) | MED-002 | `data-jan-26/mcqs/respiratory/copd.json` |
| 3:00-4:00 | Generate Pneumonia MCQs (40) | MED-002 | `data-jan-26/mcqs/respiratory/pneumonia.json` |
| 4:00-5:00 | Generate PE MCQs (40) | MED-002 | `data-jan-26/mcqs/respiratory/pe.json` |
| 5:00-6:00 | Generate Other MCQs (40) | MED-002 | `data-jan-26/mcqs/respiratory/other.json` |
| 6:00-7:00 | Merge to single file | PM | `data-jan-26/mcqs/respiratory/respiratory_200_mcqs.json` |
| 7:00-8:00 | Post-generation validation | PM | All quality gates PASS |
| 8:00-9:00 | Manual review (10% sample) | Medical Expert | 20 MCQs reviewed, feedback documented |
| 9:00-10:00 | Fix any issues, git commit | PM | Commit: "feat: Add 200 respiratory MCQs (MED-002)" |

**GO/NO-GO Decision**: Review validation results. If PASS → Proceed to Cardiology. If FAIL → Fix issues first.

---

### Day 2-3: Cardiology MCQs (MED-001)
**Duration**: 8-10 hours

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 0:00-0:30 | Lessons learned from Respiratory | PM | Updated generation script if needed |
| 0:30-1:30 | Generate ACS MCQs (50) | MED-001 | `data-jan-26/mcqs/cardiology/acs.json` |
| 1:30-2:30 | Generate Heart Failure MCQs (50) | MED-001 | `data-jan-26/mcqs/cardiology/heart_failure.json` |
| 2:30-3:30 | Generate Arrhythmia MCQs (50) | MED-001 | `data-jan-26/mcqs/cardiology/arrhythmias.json` |
| 3:30-4:30 | Generate Hypertension MCQs (30) | MED-001 | `data-jan-26/mcqs/cardiology/hypertension.json` |
| 4:30-5:30 | Generate Other MCQs (20) | MED-001 | `data-jan-26/mcqs/cardiology/other.json` |
| 5:30-6:30 | Merge to single file | PM | `data-jan-26/mcqs/cardiology/cardiology_200_mcqs.json` |
| 6:30-7:30 | Post-generation validation | PM | All quality gates PASS |
| 7:30-8:30 | Manual review (10% sample) | Medical Expert | 20 MCQs reviewed |
| 8:30-9:30 | Fix any issues, git commit | PM | Commit: "feat: Add 200 cardiology MCQs (MED-001)" |

---

### Day 3-4: Psychiatry MCQs (MED-009)
**Duration**: 8-10 hours

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 0:00-0:30 | Lessons learned from previous 400 MCQs | PM | Final script optimizations |
| 0:30-1:30 | Generate Depression MCQs (50) | MED-009 | `data-jan-26/mcqs/psychiatry/depression.json` |
| 1:30-2:30 | Generate Anxiety MCQs (40) | MED-009 | `data-jan-26/mcqs/psychiatry/anxiety.json` |
| 2:30-3:30 | Generate Psychosis MCQs (40) | MED-009 | `data-jan-26/mcqs/psychiatry/psychosis.json` |
| 3:30-4:30 | Generate Bipolar MCQs (30) | MED-009 | `data-jan-26/mcqs/psychiatry/bipolar.json` |
| 4:30-5:30 | Generate Other MCQs (40) | MED-009 | `data-jan-26/mcqs/psychiatry/other.json` |
| 5:30-6:30 | Merge to single file | PM | `data-jan-26/mcqs/psychiatry/psychiatry_200_mcqs.json` |
| 6:30-7:30 | Post-generation validation | PM | All quality gates PASS |
| 7:30-8:30 | Manual review (10% sample) | Medical Expert | 20 MCQs reviewed |
| 8:30-9:30 | Fix any issues, git commit | PM | Commit: "feat: Add 200 psychiatry MCQs (MED-009)" |

---

### Day 5: Final Validation & Documentation
**Duration**: 4-6 hours

| Time | Task | Owner | Deliverable |
|------|------|-------|-------------|
| 0:00-1:00 | Comprehensive QA-003 validation | PM | 600 MCQs RAG-verified |
| 1:00-2:00 | Generate combined statistics | PM | GENERATION_REPORT_JAN26.md |
| 2:00-3:00 | Manual review final sample | Medical Expert | 30 additional MCQs reviewed |
| 3:00-4:00 | Update documentation | PM | README, API docs updated |
| 4:00-5:00 | Create PR for review | PM | PR #1: Agent OS Content Generation (600 MCQs) |
| 5:00-6:00 | Retrospective meeting | Team | Lessons learned documented |

---

## 7. Rollback Plan

### 7.1 If Agent OS Approach Fails

**Failure Criteria:**
- Placeholder pattern rate >5% after 100 MCQs generated
- QA-003 Tier 1 approval rate <50%
- Agent OS tools not being applied correctly
- Generation time >2 minutes per MCQ (performance issue)

**Rollback Steps:**

1. **Stop Generation Immediately**
   ```bash
   # Kill generation process
   pkill -f generate_.*_mcqs.py
   
   # Do NOT commit partial data
   git reset --hard HEAD
   ```

2. **Diagnose Root Cause**
   - Check Agent OS agent import errors
   - Verify RAG system connectivity
   - Test LLM client response quality
   - Review agent generation prompts

3. **Fallback Option A: Fix Agent Prompts**
   - Update agent generation templates
   - Add more explicit constraint enforcement
   - Improve RAG citation content extraction
   - Retry with fixed prompts

4. **Fallback Option B: Hybrid Approach**
   - Use Agent OS for specialty tools only
   - Enhance generic OllamaClient with Agent OS tools
   - Keep LLM-powered generation (Constraint 12)
   - Maintain fail-fast validation

5. **Fallback Option C: Manual Curation**
   - Generate 600 MCQs with Agent OS (accept higher failure rate)
   - Post-process with intensive manual review
   - Fix placeholder patterns manually
   - Validate citations manually with RAG system

6. **Document Failure & Lessons**
   - Update `LESSONS_LEARNED_AND_MISTAKES.md`
   - Capture specific failure modes
   - Propose alternative approaches for next iteration

### 7.2 Partial Success Handling

**Scenario**: 150 respiratory MCQs generated successfully, then failures increase

**Response**:
1. **Commit Successful MCQs**
   ```bash
   git add data-jan-26/mcqs/respiratory/asthma.json
   git add data-jan-26/mcqs/respiratory/copd.json
   git add data-jan-26/mcqs/respiratory/pneumonia.json
   git commit -m "feat: Add 120 respiratory MCQs (asthma, COPD, pneumonia)"
   ```

2. **Diagnose Why Failures Started**
   - Check if RAG system degraded (vector DB issue?)
   - Check if LLM client became slow (Ollama crash?)
   - Check if agent logic changed (code update?)

3. **Fix Issue & Resume**
   - Fix specific problem
   - Resume from last successful topic
   - Continue until 200 MCQs complete

---

## 8. Risk Mitigation

### 8.1 Identified Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **RAG system downtime** | Low | High | Pre-generation check detects this (fail-fast) |
| **Ollama LLM slow/crashes** | Medium | High | Timeout handling, retry logic, fallback to OpenAI |
| **Agent OS import errors** | Low | High | Pre-generation check validates imports |
| **Placeholder patterns persist** | Medium | Medium | Incremental validation catches per-MCQ, max 2 retries |
| **Low QA-003 approval rate** | Medium | Medium | Post-generation check blocks progression |
| **Citation confidence too low** | Medium | Medium | Increase RAG limit to 10, select top 3 with >0.70 |
| **Generation too slow** | Low | Medium | Optimize agent prompts, reduce LLM max tokens |
| **Disk space exhaustion** | Very Low | Low | 600 MCQs = ~3MB, plenty of space |

### 8.2 Contingency Plans

**If RAG System Fails:**
- Restart Qdrant: `docker compose restart qdrant`
- Re-index if needed: `python3 scripts/index_qdrant.py`
- Verify collection: `curl http://localhost:6333/collections/medical_knowledge`

**If Ollama Fails:**
- Restart Ollama: `ollama serve`
- Check GPU memory: `nvidia-smi`
- Fallback to OpenAI API if local LLM unavailable

**If Agent OS Agents Fail:**
- Check Python imports: `python3 -c "from src.agents.medical.med_001_cardiology import CardiologyExpert"`
- Review agent __init__ for errors
- Check base_medical_expert.py for breaking changes

**If Validation Keeps Failing:**
- Lower thresholds temporarily (e.g., citation confidence 0.65 instead of 0.70)
- Increase max retries from 2 to 5
- Manual review and fix instead of regeneration

---

## 9. Monitoring & Logging

### 9.1 Real-Time Monitoring

**Script**: `scripts-jan-26/monitor_generation.sh`

```bash
#!/bin/bash
# Real-time monitoring of MCQ generation

SPECIALTY=$1
LOG_FILE="logs/generation_${SPECIALTY}_$(date +%Y%m%d_%H%M%S).log"

echo "Monitoring generation for: $SPECIALTY"
echo "Log file: $LOG_FILE"

while true; do
    clear
    echo "========================================="
    echo "AGENT OS GENERATION MONITOR: $SPECIALTY"
    echo "========================================="
    echo ""
    
    # Count MCQs generated
    mcq_count=$(jq '. | length' "data-jan-26/mcqs/${SPECIALTY}/${SPECIALTY}_mcqs.json" 2>/dev/null || echo "0")
    echo "MCQs generated: $mcq_count / 200"
    
    # Count placeholder patterns
    placeholder_count=$(grep -i "Clinical scenario for\|Question about\|Option A\|Explanation for" \
        "data-jan-26/mcqs/${SPECIALTY}/${SPECIALTY}_mcqs.json" 2>/dev/null | wc -l)
    echo "Placeholder patterns: $placeholder_count (target: 0)"
    
    # Count citations
    citation_count=$(jq '[.[] | .references | length] | add' \
        "data-jan-26/mcqs/${SPECIALTY}/${SPECIALTY}_mcqs.json" 2>/dev/null || echo "0")
    if [ "$mcq_count" -gt 0 ]; then
        avg_citations=$(echo "scale=2; $citation_count / $mcq_count" | bc)
        echo "Average citations per MCQ: $avg_citations (target: 3.00)"
    fi
    
    # Count summaries
    summary_count=$(jq '[.[] | select(.summary != null)] | length' \
        "data-jan-26/mcqs/${SPECIALTY}/${SPECIALTY}_mcqs.json" 2>/dev/null || echo "0")
    if [ "$mcq_count" -gt 0 ]; then
        summary_pct=$(echo "scale=1; 100 * $summary_count / $mcq_count" | bc)
        echo "MCQs with summaries: $summary_count / $mcq_count ($summary_pct%) (target: 100%)"
    fi
    
    # Generation speed
    if [ -f "$LOG_FILE" ]; then
        recent_mcqs=$(tail -n 10 "$LOG_FILE" | grep "MCQ.*saved" | wc -l)
        echo "Recent generation rate: $recent_mcqs MCQs in last 10 log entries"
    fi
    
    echo ""
    echo "Last 5 log entries:"
    tail -n 5 "$LOG_FILE" 2>/dev/null || echo "No logs yet"
    
    sleep 10
done
```

**Usage**:
```bash
# Terminal 1: Run generation
python3 scripts-jan-26/generate_respiratory_mcqs.py | tee logs/generation_respiratory_$(date +%Y%m%d_%H%M%S).log

# Terminal 2: Monitor progress
./scripts-jan-26/monitor_generation.sh respiratory
```

### 9.2 Logging Standards

**Log Levels**:
- `[INFO]`: Normal operation (MCQ generated, validation passed)
- `[WARNING]`: Retry triggered, low confidence citation
- `[ERROR]`: Validation failed after max retries, agent exception
- `[CRITICAL]`: RAG system down, LLM client down, pre-generation check failed

**Log Format**:
```
[2026-01-26 14:23:45] [INFO] [MED-002] Generating MCQ for topic: asthma_acute
[2026-01-26 14:23:47] [INFO] [MED-002] Fetched 5 RAG citations (confidence: 0.92, 0.88, 0.84, 0.79, 0.76)
[2026-01-26 14:23:47] [INFO] [MED-002] Selected top 3 citations (avg confidence: 0.88)
[2026-01-26 14:23:52] [INFO] [MED-002] LLM generation complete (5.2 seconds)
[2026-01-26 14:23:52] [INFO] [MED-002] Incremental validation: PASS (0 errors)
[2026-01-26 14:23:52] [INFO] [MED-002] MCQ resp-asthma-001 saved to data-jan-26/mcqs/respiratory/asthma.json
```

---

## 10. Deliverables Checklist

### 10.1 Code Artifacts

- [ ] `scripts-jan-26/pre_generation_check.sh` - Pre-generation quality gate
- [ ] `scripts-jan-26/generate_respiratory_mcqs.py` - MED-002 generation script
- [ ] `scripts-jan-26/generate_cardiology_mcqs.py` - MED-001 generation script
- [ ] `scripts-jan-26/generate_psychiatry_mcqs.py` - MED-009 generation script
- [ ] `scripts-jan-26/post_generation_check.sh` - Post-generation quality gate
- [ ] `scripts-jan-26/monitor_generation.sh` - Real-time monitoring
- [ ] `scripts-jan-26/validate_mcq_incremental.py` - Per-MCQ validation function
- [ ] `scripts-jan-26/agent_os_router.py` - Specialty routing logic

### 10.2 Data Artifacts

- [ ] `data-jan-26/mcqs/respiratory/respiratory_200_mcqs.json` - 200 MCQs, 0 placeholders
- [ ] `data-jan-26/mcqs/cardiology/cardiology_200_mcqs.json` - 200 MCQs, 0 placeholders
- [ ] `data-jan-26/mcqs/psychiatry/psychiatry_200_mcqs.json` - 200 MCQs, 0 placeholders
- [ ] `data-jan-26/mcqs/combined_600_mcqs.json` - All 600 MCQs merged

### 10.3 Validation Reports

- [ ] `reports/respiratory_qa003.json` - QA-003 validation for respiratory
- [ ] `reports/cardiology_qa003.json` - QA-003 validation for cardiology
- [ ] `reports/psychiatry_qa003.json` - QA-003 validation for psychiatry
- [ ] `reports/respiratory_australian.json` - Australian compliance for respiratory
- [ ] `reports/cardiology_australian.json` - Australian compliance for cardiology
- [ ] `reports/psychiatry_australian.json` - Australian compliance for psychiatry
- [ ] `reports/combined_validation_report.json` - Overall validation summary

### 10.4 Documentation

- [ ] `planning/jan-26-plan/AGENT_OS_REGENERATION_PLAN.md` - This document
- [ ] `planning/jan-26-plan/GENERATION_REPORT_JAN26.md` - Final statistics, lessons learned
- [ ] `planning/jan-26-plan/RETROSPECTIVE.md` - What worked, what didn't, next steps
- [ ] Updated `README.md` - Reflect new Agent OS approach
- [ ] Updated `docs/AGENT_OS_INTEGRATION.md` - Document integration patterns

### 10.5 Git Commits

- [ ] Commit 1: `feat: Add 200 respiratory MCQs via Agent OS MED-002`
- [ ] Commit 2: `feat: Add 200 cardiology MCQs via Agent OS MED-001`
- [ ] Commit 3: `feat: Add 200 psychiatry MCQs via Agent OS MED-009`
- [ ] Commit 4: `docs: Add Agent OS regeneration plan and reports`
- [ ] Commit 5: `chore: Archive old placeholder content, mark deprecated`

---

## 11. Success Declaration

**SUCCESS is declared when:**

1. ✅ **600 MCQs Generated**
   - 200 Respiratory (MED-002)
   - 200 Cardiology (MED-001)
   - 200 Psychiatry (MED-009)

2. ✅ **Zero-Error Policy Met**
   - 0 placeholder patterns detected
   - 0 pre-commit hook blocks
   - 0 content substance validator failures

3. ✅ **Constraint Compliance**
   - Constraint 11: 3 citations per MCQ (100%)
   - Constraint 12: LLM-powered generation (100%)
   - Summary field: 100% present, 50-200 chars
   - Australian context: 100%
   - Patient demographics: 100%

4. ✅ **Quality Validation**
   - QA-003 Tier 1 auto-approval: >70%
   - Australian compliance: 100%
   - Manual review: No critical errors in 10% sample
   - Specialty tools applied: 100%

5. ✅ **Documentation Complete**
   - All scripts documented with usage examples
   - All validation reports generated
   - Lessons learned documented
   - Retrospective completed

---

## 12. Next Steps (Post-Success)

### Phase 2: Expand to 7 More Specialties (Future)
- MED-003 Gastroenterology: 200 MCQs
- MED-004 Endocrinology: 200 MCQs
- MED-005 Neurology: 200 MCQs
- MED-006 Emergency Medicine: 200 MCQs
- MED-007 OB/GYN: 200 MCQs
- MED-008 Paediatrics: 200 MCQs
- MED-010 General Practice: 200 MCQs

**Total**: 1,400 additional MCQs (2,000 MCQs total)

### Phase 3: OSCE Generation with Agent OS
- Respiratory OSCEs (MED-002): 20 scenarios
- Cardiology OSCEs (MED-001): 20 scenarios
- Psychiatry OSCEs (MED-009): 20 scenarios

### Phase 4: Study Cards with Agent OS
- Rapid recall cards
- Clinical pearls
- Red flag reminders
- Australian guideline quick reference

### Phase 5: Automated Image Integration
- ECG images for cardiology MCQs (MED-001)
- CXR images for respiratory MCQs (MED-002)
- MSE diagrams for psychiatry MCQs (MED-009)

---

**Plan Version**: 1.0
**Author**: Project Manager (Agent OS Coordinator)
**Date**: 2026-01-26
**Status**: READY FOR EXECUTION
**Approval**: Pending user review

---

**CRITICAL REMINDER**: This is a FRESH START. Old data (2,208 MCQs with placeholders) is DEPRECATED. We are building from scratch with Agent OS medical experts, fail-fast validation, and zero-error policy enforcement.

**Delegation**: Once approved, PM will delegate to specialist agents:
- `MED-002` for respiratory MCQs
- `MED-001` for cardiology MCQs
- `MED-009` for psychiatry MCQs

**Human-in-the-Loop**: User approval required before execution. PM awaits confirmation.
