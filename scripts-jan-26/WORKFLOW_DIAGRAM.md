# MCQ Regeneration Workflow Diagram

## Problem → Solution Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ PROBLEM (2026-01-26)                                            │
├─────────────────────────────────────────────────────────────────┤
│ • 200 Cardiology MCQs generated                                 │
│ • 600 RAG citations validated (✅ 95%+ confidence)              │
│ • Content generation with local 7B LLMs → ❌ ALL PLACEHOLDERS  │
│                                                                 │
│ Evidence:                                                       │
│   "scenario": "Clinical scenario for STEMI..."                 │
│   "options": {"A": "Option A", "B": "Option B"}                │
│                                                                 │
│ Root Cause: 7B models cannot handle:                           │
│   • Complex medical reasoning + JSON simultaneously            │
│   • 500-1000 token outputs with coherence                      │
│   • Australian context + medical accuracy                      │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ SOLUTION (Constraint 4.2)                                       │
├─────────────────────────────────────────────────────────────────┤
│ Use Claude (Anthropic API) for production-grade generation     │
│                                                                 │
│ Model: claude-sonnet-4-5-20250929                              │
│ Cost: ~$0.015 per MCQ × 200 = $3 USD (acceptable)             │
│ Quality: 100% real content, Australian compliant               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Script Architecture (Agent OS)

```
┌─────────────────────────────────────────────────────────────────┐
│ MCQRegenerationPM (Project Manager)                            │
│ scripts-jan-26/regenerate_week3_cardiology_with_claude.py      │
└─────────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Load MCQs    │   │ Delegate to  │   │ Validate &   │
│ + Citations  │ → │ Claude API   │ → │ Save         │
└──────────────┘   └──────────────┘   └──────────────┘
        │                   │                   │
        ↓                   ↓                   ↓
┌──────────────────────────────────────────────────────┐
│ 200 MCQs                                             │
│ 600 Citations (preserved)                            │
│ ✅ Real clinical content                             │
│ ✅ Australian context                                │
│ ✅ Zero placeholders                                 │
└──────────────────────────────────────────────────────┘
```

---

## Execution Workflow

```
START
  │
  ├─── [Prerequisites Check]
  │    • ANTHROPIC_API_KEY set?
  │    • anthropic package installed?
  │    • venv activated?
  │    • Input file exists?
  │         │
  │         ↓ YES
  │    
  ├─── [Load & Backup]
  │    • Load data/mcqs/week3_cardiology_200_mcqs.json
  │    • Count placeholders (200 expected)
  │    • Create timestamped backup
  │         │
  │         ↓
  │    
  ├─── [For Each Placeholder MCQ]
  │    │
  │    ├─── Extract metadata
  │    │    • MCQ ID, topic, subtopic
  │    │    • 3 RAG citations (>0.70 confidence)
  │    │
  │    ├─── Build Claude prompt
  │    │    • Include citation context
  │    │    • Enforce Australian context
  │    │    • Reject placeholder patterns
  │    │
  │    ├─── Call Claude API
  │    │    • Generate real clinical content
  │    │    • Parse JSON response
  │    │    • Validate output quality
  │    │
  │    ├─── Validate generated content
  │    │    • No placeholder patterns?
  │    │    • Australian spelling?
  │    │    • Patient demographics?
  │    │         │
  │    │         ├─── PASS → Update MCQ
  │    │         └─── FAIL → Mark for review
  │    │
  │    ├─── Save progress (every 10 MCQs)
  │    │
  │    └─── Rate limit (wait 2 seconds)
  │         │
  │         ↓
  │    
  ├─── [Final Save]
  │    • Update metadata
  │    • Save statistics
  │    • Close file
  │         │
  │         ↓
  │    
  └─── [Summary]
       • Total regenerated: 200
       • Failed: 0 (or mark for manual review)
       • Backup: preserved
       • Output: updated file
            │
            ↓
          END
```

---

## Validation Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│ Regenerated MCQs                                                │
│ data/mcqs/week3_cardiology_200_mcqs.json                        │
└─────────────────────────────────────────────────────────────────┘
                            │
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ validate_regenerated_mcqs.py                                    │
├─────────────────────────────────────────────────────────────────┤
│ Check 1: No placeholders (Constraint 12)                        │
│   ❌ "Clinical scenario for..."                                 │
│   ❌ "Option A", "Option B"                                     │
│                                                                 │
│ Check 2: Australian spelling (Constraint 1)                     │
│   ❌ pediatric → ✅ paediatric                                  │
│   ❌ anesthesia → ✅ anaesthesia                                │
│                                                                 │
│ Check 3: Australian drugs (Constraint 1)                        │
│   ❌ acetaminophen → ✅ paracetamol                             │
│   ❌ albuterol → ✅ salbutamol                                  │
│                                                                 │
│ Check 4: Citations preserved                                    │
│   ✅ 3 per MCQ                                                  │
│   ✅ >0.70 confidence                                           │
│                                                                 │
│ Check 5: Content substance                                      │
│   ✅ Scenario ≥100 chars                                        │
│   ✅ Explanation ≥200 chars                                     │
│                                                                 │
│ Check 6: Patient demographics                                   │
│   ✅ Age mentioned                                              │
│   ✅ Clinical context                                           │
└─────────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                ↓                       ↓
        ┌──────────────┐        ┌──────────────┐
        │ ALL PASS ✅  │        │ FAIL ❌      │
        │ Exit 0       │        │ Exit 1       │
        └──────────────┘        └──────────────┘
```

---

## Data Flow

```
INPUT (Existing)
├── MCQ Structure
│   ├── id: "WEEK3-CARDIO-001"
│   ├── specialty: "Cardiology"
│   ├── topic: "Acute Coronary Syndrome"
│   ├── subtopic: "STEMI diagnosis ECG criteria"
│   ├── question
│   │   ├── scenario: "Clinical scenario for..." ❌ PLACEHOLDER
│   │   ├── stem: "Question stem about..." ❌ PLACEHOLDER
│   │   └── options: {"A": "Option A"...} ❌ PLACEHOLDER
│   ├── explanation: "Explanation for..." ❌ PLACEHOLDER
│   └── references [✅ VALIDATED]
│       ├── Citation 1 (confidence: 0.79)
│       ├── Citation 2 (confidence: 0.77)
│       └── Citation 3 (confidence: 0.76)
                    │
                    ↓
        ┌───────────────────────┐
        │ Claude API Generation │
        └───────────────────────┘
                    │
                    ↓
OUTPUT (Regenerated)
├── MCQ Structure [SAME IDs, SAME CITATIONS]
│   ├── id: "WEEK3-CARDIO-001" ✅ PRESERVED
│   ├── specialty: "Cardiology" ✅ PRESERVED
│   ├── topic: "Acute Coronary Syndrome" ✅ PRESERVED
│   ├── subtopic: "STEMI diagnosis ECG criteria" ✅ PRESERVED
│   ├── question
│   │   ├── scenario: "A 62-year-old man with history of..." ✅ REAL
│   │   ├── stem: "What is the most appropriate..." ✅ REAL
│   │   └── options: {"A": "Administer aspirin..."} ✅ REAL
│   ├── explanation: "Option A is correct because..." ✅ REAL
│   ├── references [✅ PRESERVED]
│   │   ├── Citation 1 (confidence: 0.79)
│   │   ├── Citation 2 (confidence: 0.77)
│   │   └── Citation 3 (confidence: 0.76)
│   └── regeneration_metadata [✅ ADDED]
│       ├── regeneration_date: "2026-01-27T12:34:56"
│       ├── regeneration_method: "Claude (Anthropic API)"
│       └── regeneration_model: "claude-sonnet-4-5-20250929"
```

---

## Constraint Enforcement Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ Constraint 4.2: LLM Integration                                 │
├─────────────────────────────────────────────────────────────────┤
│ Problem: Local 7B models FAILED (200/200 placeholders)          │
│ Solution: Claude (Anthropic API)                                │
│ Evidence: Section 4.2 of constraints/4-llm-integration.md       │
│ Cost: ~$3 USD (acceptable per constraint)                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓ ENFORCED IN SCRIPT
┌─────────────────────────────────────────────────────────────────┐
│ Constraint 1: Australian Medical Context                        │
├─────────────────────────────────────────────────────────────────┤
│ • Drug names: paracetamol, salbutamol, adrenaline              │
│ • Spelling: paediatric, anaesthesia, haemoglobin               │
│ • Guidelines: eTG, AMH, PBS, RANZCP                            │
│ • Terminology: GP, Emergency Department, Medicare              │
└─────────────────────────────────────────────────────────────────┘
                            ↓ ENFORCED IN PROMPT
┌─────────────────────────────────────────────────────────────────┐
│ Constraint 12: No Placeholder Content                           │
├─────────────────────────────────────────────────────────────────┤
│ Rejected Patterns:                                              │
│ • "Clinical scenario for..."                                    │
│ • "Question stem about..."                                      │
│ • "Option A", "Option B"                                        │
│ • "Explanation for..."                                          │
└─────────────────────────────────────────────────────────────────┘
                            ↓ VALIDATED POST-GENERATION
┌─────────────────────────────────────────────────────────────────┐
│ Output: 200 MCQs with real content                             │
│ ✅ Constraint 4.2: Claude API used                              │
│ ✅ Constraint 1: Australian context enforced                    │
│ ✅ Constraint 12: Zero placeholders                             │
└─────────────────────────────────────────────────────────────────┘
```

---

## File Structure

```
/home/dev/Development/irStudy/
│
├── scripts-jan-26/
│   ├── regenerate_week3_cardiology_with_claude.py ──┐
│   │   • 500+ lines Python                          │
│   │   • Agent OS PM coordination                   │
│   │   • Claude API integration                     │ DELIVERABLES
│   │   • Constraint enforcement                     │
│   │                                                 │
│   ├── validate_regenerated_mcqs.py ────────────────┤
│   │   • 300+ lines Python                          │
│   │   • 6 validation checks                        │
│   │   • Constraint compliance verification         │
│   │                                                 │
│   ├── README_REGENERATION.md ──────────────────────┤
│   │   • 550+ lines markdown                        │
│   │   • Complete documentation                     │
│   │   • Testing checklist                          │
│   │                                                 │
│   ├── DELIVERABLES_SUMMARY.md ─────────────────────┤
│   │   • 400+ lines markdown                        │
│   │   • Constraint analysis                        │
│   │   • Cost justification                         │
│   │                                                 │
│   ├── QUICK_START.md ──────────────────────────────┤
│   │   • 200+ lines markdown                        │
│   │   • Step-by-step guide                         │
│   │   • Troubleshooting                            │
│   │                                                 │
│   └── WORKFLOW_DIAGRAM.md ─────────────────────────┘
│       • Visual workflow
│       • Data flow diagrams
│
├── data/mcqs/
│   ├── week3_cardiology_200_mcqs.json (INPUT/OUTPUT)
│   └── week3_cardiology_200_mcqs_backup_*.json (AUTO-GENERATED)
│
└── constraints/
    ├── 4-llm-integration.md (Section 4.2 - WHY Claude)
    ├── 01-medical-accuracy.md (Section 1 - Australian context)
    └── 12-content-generation-requirements.md (No placeholders)

TOTAL: 2000+ lines of code + documentation
```

---

## Success Metrics

```
┌─────────────────────────────────────────────────────────────────┐
│ Before (2026-01-26)                                             │
├─────────────────────────────────────────────────────────────────┤
│ • MCQs: 200                                                     │
│ • Citations: 600 (validated ✅)                                 │
│ • Real content: 0 (ALL placeholders ❌)                         │
│ • Australian context: 0% ❌                                     │
│ • Educational value: 0 ❌                                       │
└─────────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│ After (Expected)                                                │
├─────────────────────────────────────────────────────────────────┤
│ • MCQs: 200 ✅                                                  │
│ • Citations: 600 (preserved ✅)                                 │
│ • Real content: 200 (100% ✅)                                   │
│ • Australian context: 100% ✅                                   │
│ • Educational value: PRODUCTION-GRADE ✅                        │
│ • Cost: $3-6 USD ✅                                             │
│ • Time: 10-15 minutes ✅                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

**Created**: 2026-01-27  
**Author**: Project Manager (Agent OS)  
**Purpose**: Visual reference for MCQ regeneration workflow
