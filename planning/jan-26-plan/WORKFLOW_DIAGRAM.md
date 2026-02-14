# Agent OS Content Generation Workflow
**Visual Reference for Execution**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AGENT OS MEDICAL CONTENT GENERATION                     │
│                          Fresh Start: Jan 26, 2026                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 0: PREPARATION                                                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PM] Review LESSONS_LEARNED_AND_MISTAKES.md                                │
│    ↓                                                                        │
│  [PM] Review AGENT_OS_REGENERATION_PLAN.md (this plan)                      │
│    ↓                                                                        │
│  [PM] Get user approval for fresh start approach                            │
│    ↓                                                                        │
│  [PM] Create scripts-jan-26/ directory                                      │
│    ↓                                                                        │
│  [PM] Create data-jan-26/mcqs/{respiratory,cardiology,psychiatry}/          │
│    ↓                                                                        │
│  [PM] Run: pre_generation_check.sh                                          │
│    ├─ Check RAG system (Qdrant collection "medical_knowledge")              │
│    ├─ Check LLM client (Ollama llama3.2:latest)                             │
│    ├─ Check Agent OS imports (MED-001, MED-002, MED-009)                    │
│    └─ Check output directories (writable)                                   │
│         ↓                                                                   │
│         [PASS] → Continue                                                   │
│         [FAIL] → FIX ISSUES, DO NOT PROCEED                                 │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 1: RESPIRATORY MCQs (Priority 1) - Day 1-2                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PM] Delegate to MED-002 (RespiratoryExpert)                               │
│    │                                                                        │
│    ├─ Topic: Asthma (40 MCQs)                                               │
│    │   └─ FOR EACH MCQ (1 to 40):                                           │
│    │       ├─ [MED-002] Fetch 5 RAG citations for "asthma"                  │
│    │       │   └─ Select top 3 with confidence >0.70                        │
│    │       ├─ [MED-002] Extract citation CONTENT (500-1000 words)           │
│    │       ├─ [MED-002] Generate MCQ with LLM (pass content as context)     │
│    │       │   └─ Apply tools: spirometry, asthma_control_test              │
│    │       ├─ [VALIDATOR] validate_mcq_incremental(mcq)                     │
│    │       │   ├─ Check placeholder patterns (6 patterns)                   │
│    │       │   ├─ Check citation count (exactly 3)                          │
│    │       │   ├─ Check summary field (50-200 chars)                        │
│    │       │   ├─ Check patient demographics (age, gender)                  │
│    │       │   ├─ Check Australian context (eTG reference)                  │
│    │       │   └─ Check Australian spelling (paediatric, etc.)              │
│    │       │       ↓                                                        │
│    │       │       [PASS] → Save MCQ to asthma.json                         │
│    │       │       [FAIL] → RETRY (max 2 retries) → Skip if still fails    │
│    │       └─ Log: MCQ resp-asthma-001 saved                                │
│    │                                                                        │
│    ├─ Topic: COPD (40 MCQs) - Same process                                  │
│    ├─ Topic: Pneumonia (40 MCQs) - Same process                             │
│    ├─ Topic: Pulmonary Embolism (40 MCQs) - Same process                    │
│    └─ Topic: Other Respiratory (40 MCQs) - Same process                     │
│         ↓                                                                   │
│  [PM] Merge all topics → respiratory_200_mcqs.json                          │
│         ↓                                                                   │
│  [PM] Run: post_generation_check.sh respiratory                             │
│    ├─ Content substance validator (0 placeholders)                          │
│    ├─ QA-003 RAG validator (>70% Tier 1 approval)                           │
│    ├─ Australian compliance validator (100%)                                │
│    └─ Summary statistics                                                    │
│         ↓                                                                   │
│         [PASS] → Commit & proceed to Cardiology                             │
│         [FAIL] → FIX ISSUES before proceeding                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 2: CARDIOLOGY MCQs (Priority 2) - Day 2-3                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PM] Delegate to MED-001 (CardiologyExpert)                                │
│    │                                                                        │
│    ├─ Topic: Acute Coronary Syndrome (50 MCQs)                              │
│    │   └─ FOR EACH MCQ: Same validation pipeline as Respiratory             │
│    │       └─ Apply tools: ECG_interpretation, GRACE_score, TIMI_risk       │
│    │                                                                        │
│    ├─ Topic: Heart Failure (50 MCQs)                                        │
│    ├─ Topic: Arrhythmias (50 MCQs)                                          │
│    ├─ Topic: Hypertension (30 MCQs)                                         │
│    └─ Topic: Other Cardiology (20 MCQs)                                     │
│         ↓                                                                   │
│  [PM] Merge → cardiology_200_mcqs.json                                      │
│         ↓                                                                   │
│  [PM] Run: post_generation_check.sh cardiology                              │
│         ↓                                                                   │
│         [PASS] → Commit & proceed to Psychiatry                             │
│         [FAIL] → FIX ISSUES before proceeding                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 3: PSYCHIATRY MCQs (Priority 3) - Day 3-4                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PM] Delegate to MED-009 (PsychiatryExpert)                                │
│    │                                                                        │
│    ├─ Topic: Depression (50 MCQs)                                           │
│    │   └─ FOR EACH MCQ: Same validation pipeline                            │
│    │       └─ Apply tools: PHQ9, GAD7, MSE_assessment, suicide_risk         │
│    │                                                                        │
│    ├─ Topic: Anxiety Disorders (40 MCQs)                                    │
│    ├─ Topic: Psychotic Disorders (40 MCQs)                                  │
│    ├─ Topic: Bipolar Disorder (30 MCQs)                                     │
│    └─ Topic: Other Psychiatry (40 MCQs)                                     │
│         ↓                                                                   │
│  [PM] Merge → psychiatry_200_mcqs.json                                      │
│         ↓                                                                   │
│  [PM] Run: post_generation_check.sh psychiatry                              │
│         ↓                                                                   │
│         [PASS] → Proceed to final validation                                │
│         [FAIL] → FIX ISSUES before proceeding                               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ STAGE 4: FINAL VALIDATION & DOCUMENTATION - Day 5                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [PM] Merge all specialties → combined_600_mcqs.json                        │
│    ↓                                                                        │
│  [PM] Comprehensive QA-003 validation on all 600 MCQs                       │
│    ↓                                                                        │
│  [Medical Expert] Manual review of 10% sample (60 MCQs)                     │
│    ↓                                                                        │
│  [PM] Generate GENERATION_REPORT_JAN26.md                                   │
│    ├─ Success metrics achieved                                              │
│    ├─ Validation results summary                                            │
│    ├─ Agent OS usage statistics                                             │
│    └─ Lessons learned & next steps                                          │
│         ↓                                                                   │
│  [PM] Update documentation (README, API docs)                               │
│    ↓                                                                        │
│  [PM] Git commit all deliverables                                           │
│    ├─ Commit 1: Respiratory MCQs                                            │
│    ├─ Commit 2: Cardiology MCQs                                             │
│    ├─ Commit 3: Psychiatry MCQs                                             │
│    ├─ Commit 4: Combined MCQs & reports                                     │
│    └─ Commit 5: Documentation updates                                       │
│         ↓                                                                   │
│  [PM] Create PR for review                                                  │
│    └─ PR #1: Agent OS Content Generation (600 MCQs)                         │
│         ↓                                                                   │
│  [Team] Retrospective meeting                                               │
│    ├─ What worked well                                                      │
│    ├─ What didn't work                                                      │
│    └─ Improvements for Phase 2 (7 more specialties)                         │
│         ↓                                                                   │
│  ✅ SUCCESS DECLARED                                                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ VALIDATION GATES (Fail-Fast Philosophy)                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Gate 1: Pre-Generation Check (BLOCKS start if fails)                       │
│    └─ RAG, LLM, Agent OS operational                                        │
│                                                                             │
│  Gate 2: Incremental Validation (BLOCKS each MCQ if fails)                  │
│    ├─ Placeholder patterns (6 patterns checked)                             │
│    ├─ Citation count (exactly 3)                                            │
│    ├─ Citation confidence (>0.70)                                           │
│    ├─ Summary field (50-200 chars)                                          │
│    ├─ Patient demographics (age, gender)                                    │
│    ├─ Australian context (eTG/RANZCP/PBS)                                   │
│    └─ Australian spelling (paediatric, paracetamol, etc.)                   │
│                                                                             │
│  Gate 3: Post-Generation Check (BLOCKS next specialty if fails)             │
│    ├─ Content substance validator (0 placeholders)                          │
│    ├─ QA-003 RAG validator (>70% Tier 1 approval)                           │
│    ├─ Australian compliance (100%)                                          │
│    └─ Summary statistics                                                    │
│                                                                             │
│  Gate 4: Pre-Commit Hook (BLOCKS git commit if fails)                       │
│    └─ Final placeholder scan (must be 0)                                    │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ AGENT OS ROUTING (Specialty → Agent)                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Respiratory   →   MED-002 (RespiratoryExpert)                              │
│    Tools: spirometry, CXR, Wells_PE, CURB65, asthma_control_test            │
│    Guidelines: eTG Respiratory Section 4.x                                  │
│                                                                             │
│  Cardiology    →   MED-001 (CardiologyExpert)                               │
│    Tools: ECG, GRACE, TIMI, CHA2DS2_VASc, HAS_BLED, heart_failure_risk      │
│    Guidelines: eTG Cardiovascular Section 5.x                               │
│                                                                             │
│  Psychiatry    →   MED-009 (PsychiatryExpert)                               │
│    Tools: PHQ9, GAD7, MSE, BPRS, YMRS, Y_BOCS, suicide_risk, AUDIT          │
│    Guidelines: RANZCP Clinical Practice Guidelines                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ ROLLBACK PLAN (If Agent OS Approach Fails)                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Failure Criteria:                                                          │
│    - Placeholder rate >5% after 100 MCQs                                    │
│    - QA-003 Tier 1 approval <50%                                            │
│    - Generation time >2 minutes per MCQ                                     │
│                                                                             │
│  Rollback Steps:                                                            │
│    1. STOP generation immediately (pkill -f generate_.*_mcqs.py)            │
│    2. Do NOT commit partial data (git reset --hard HEAD)                    │
│    3. Diagnose root cause (Agent OS imports, RAG connectivity, LLM quality) │
│    4. Fallback Options:                                                     │
│       A. Fix agent prompts and retry                                        │
│       B. Hybrid approach (Agent OS tools + enhanced OllamaClient)           │
│       C. Manual curation (generate + intensive manual review)               │
│    5. Document failure in LESSONS_LEARNED_AND_MISTAKES.md                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│ SUCCESS METRICS (Target vs Actual)                                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  Metric                          Target    Measurement                      │
│  ─────────────────────────────   ──────    ─────────────────────────────    │
│  Agent OS Usage                  100%      metadata.agent_id field          │
│  Placeholder Patterns            0         Content substance validator      │
│  Citation Count                  3/MCQ     Exactly 3 references             │
│  Citation Confidence             >0.70     All citations >0.70              │
│  Summary Compliance              100%      50-200 chars per MCQ             │
│  Australian Compliance           100%      QA-001 validator                 │
│  QA-003 Tier 1 Approval          >70%      Auto-approval rate calculation   │
│  Patient Demographics            100%      Age + gender in scenario         │
│  Specialty Tool Usage            100%      metadata.tools_used non-empty    │
│  LLM-Powered Generation          100%      Inverse of placeholder count     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

**Legend**:
- `[PM]` = Project Manager (coordinator)
- `[MED-001]` = Cardiology Expert Agent
- `[MED-002]` = Respiratory Expert Agent
- `[MED-009]` = Psychiatry Expert Agent
- `[VALIDATOR]` = Automated validation script
- `[Medical Expert]` = Human medical review
- `[Team]` = PM + specialists + user

**Critical Path**: Pre-Gen Check → Respiratory → Cardiology → Psychiatry → Final Validation
**Blocking Points**: Any quality gate failure stops progression
**Human Approval**: Required before Stage 0 execution
