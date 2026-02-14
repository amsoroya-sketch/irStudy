# irStudy Medical Education Platform
## UI Module & Navigation Architecture

**Date:** 2026-02-06  
**Purpose:** Define how MCQ, OSCE, EPM, AI Lab Clinical Exam, Medical Science Sub-topics, and EMR modules are grouped in the UI

---

## 📐 OVERVIEW: HIERARCHICAL UI STRUCTURE

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         IRSTUDY PLATFORM NAVIGATION                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  PRIMARY NAVIGATION (Top/Sidebar)                                               │
│  ├── 🏠 Dashboard                                                               │
│  ├── 📚 Study Hub                    [Core Learning Modules]                    │
│  ├── 🎯 Practice Arena               [Assessment & Simulation]                  │
│  ├── 🏥 Clinical Lab                 [EMR & Clinical Skills]                    │
│  ├── 📊 Progress & Analytics                                                    │
│  └── ⚙️ Settings                                                                │
│                                                                                 │
│  SECONDARY NAVIGATION (Contextual)                                              │
│  ├── 🔍 Quick Search (Global)                                                   │
│  ├── 📖 Study Plan (Current Phase)                                              │
│  └── 🔔 Notifications                                                           │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📚 MODULE 1: STUDY HUB (Primary Learning)

### 1.1 MCQ Module (Multiple Choice Questions)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  📚 STUDY HUB → MCQs                                                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  NAVIGATION TABS:                                                               │
│  ├── By Specialty                    [Organized by medical discipline]          │
│  ├── By Topic                        [Organized by disease/condition]           │
│  ├── By System                       [Organized by body system]                 │
│  ├── By Difficulty                   [Easy/Medium/Hard]                         │
│  ├── By Frequency                    [High/Medium/Low yield for AMC]            │
│  └── Adaptive Mix                    [AI-powered personalized queue]            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  BY SPECIALTY (18,000+ Questions organized hierarchically)              │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                          │   │
│  │  🫀 Cardiology (2,500+ MCQs)                                             │   │
│  │     ├── Arrhythmias (AF, SVT, VT, Bradyarrhythmias)                     │   │
│  │     ├── Coronary Artery Disease (ACS, NSTEMI, STEMI)                    │   │
│  │     ├── Heart Failure (Acute/Chronic, Systolic/Diastolic)               │   │
│  │     ├── Valvular Disease (AS, AR, MS, MR)                               │   │
│  │     ├── Hypertension (Essential, Secondary, Emergencies)                │   │
│  │     ├── Pericardial Disease (Pericarditis, Tamponade)                   │   │
│  │     ├── Cardiomyopathies (DCM, HCM, RCM)                                │   │
│  │     └── Vascular Disease (Aortic, PAD, Aneurysms)                       │   │
│  │                                                                          │   │
│  │  🫁 Respiratory (2,000+ MCQs)                                            │   │
│  │     ├── Obstructive Disease (Asthma, COPD, Bronchiectasis)              │   │
│  │     ├── Infections (CAP, TB, Atypical, Fungal)                          │   │
│  │     ├── Interstitial Lung Disease (IPF, Sarcoidosis, Pneumoconiosis)    │   │
│  │     ├── Vascular (PE, Pulmonary Hypertension)                           │   │
│  │     ├── Pleural Disease (Effusion, Pneumothorax, Empyema)               │   │
│  │     ├── Sleep Medicine (OSA, Obesity Hypoventilation)                   │   │
│  │     ├── Lung Cancer (NSCLC, SCLC, Screening)                            │   │
│  │     └── Respiratory Failure (ARDS, Mechanical Ventilation)              │   │
│  │                                                                          │   │
│  │  🧠 Psychiatry (1,500+ MCQs)                                             │   │
│  │     ├── Mood Disorders (Depression, Bipolar)                            │   │
│  │     ├── Anxiety Disorders (GAD, Panic, Phobias, PTSD)                   │   │
│  │     ├── Psychotic Disorders (Schizophrenia, Delusional)                 │   │
│  │     ├── Personality Disorders                                           │   │
│  │     ├── Substance Use Disorders                                         │   │
│  │     ├── Eating Disorders (Anorexia, Bulimia)                            │   │
│  │     ├── Child/Adolescent Psychiatry (ADHD, Autism)                      │   │
│  │     ├── Geriatric Psychiatry (Dementia, Late-onset)                     │   │
│  │     └── Emergency Psychiatry (Suicide, Aggression, MHA)                 │   │
│  │                                                                          │   │
│  │  🧬 Other Specialties                                                    │   │
│  │     ├── Gastroenterology (1,800+ MCQs)                                  │   │
│  │     ├── Neurology (1,500+ MCQs)                                         │   │
│  │     ├── Endocrinology (1,200+ MCQs)                                     │   │
│  │     ├── Nephrology (1,000+ MCQs)                                        │   │
│  │     ├── Hematology (900+ MCQs)                                          │   │
│  │     ├── Infectious Disease (1,500+ MCQs)                                │   │
│  │     ├── Rheumatology (800+ MCQs)                                        │   │
│  │     ├── Dermatology (700+ MCQs)                                         │   │
│  │     ├── Obstetrics & Gynaecology (1,500+ MCQs)                          │   │
│  │     ├── Paediatrics (1,200+ MCQs)                                       │   │
│  │     ├── Surgery (1,500+ MCQs)                                           │   │
│  │     ├── Orthopaedics (600+ MCQs)                                        │   │
│  │     ├── Ophthalmology (400+ MCQs)                                       │   │
│  │     ├── ENT (400+ MCQs)                                                 │   │
│  │     └── Emergency Medicine (1,000+ MCQs)                                │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  BY SYSTEM (Body System Organization)                                   │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  ├── Cardiovascular System                                              │   │
│  │  ├── Respiratory System                                                 │   │
│  │  ├── Gastrointestinal System                                            │   │
│  │  ├── Nervous System (CNS & PNS)                                         │   │
│  │  ├── Endocrine System                                                   │   │
│  │  ├── Renal/Urinary System                                               │   │
│  │  ├── Reproductive System (Male & Female)                                │   │
│  │  ├── Musculoskeletal System                                             │   │
│  │  ├── Immune/Hematologic System                                          │   │
│  │  ├── Integumentary System (Skin)                                        │   │
│  │  └── Special Senses (Eye, Ear, Nose)                                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  BY FREQUENCY (AMC Exam Yield)                                          │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  🔥 High Yield (40% of exam) - 7,200 MCQs                               │   │
│  │     • Cardiology, Respiratory, GI, Emergency                            │   │
│  │  ⚡ Medium Yield (35% of exam) - 6,300 MCQs                             │   │
│  │     • Neurology, Psychiatry, Endocrine, Renal, Infectious               │   │
│  │  📌 Low Yield (25% of exam) - 4,500 MCQs                                │   │
│  │     • Dermatology, ENT, Ophthalmology, Orthopaedics                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 OSCE Module (Objective Structured Clinical Examination)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  📚 STUDY HUB → OSCEs                                                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  NAVIGATION TABS:                                                               │
│  ├── By Skill Type                   [History, Examination, Communication]      │
│  ├── By Specialty                    [Medical, Surgical, Paediatric, etc.]      │
│  ├── By Station Type                 [Static, Interactive, Procedure]           │
│  └── Mock Exams                      [Full 16-station simulations]              │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  BY SKILL TYPE (3,000+ OSCE Scenarios)                                  │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                          │   │
│  │  🗣️ History Taking (800+ scenarios)                                     │   │
│  │     ├── Cardiovascular History (Chest pain, SOB, Palpitations)          │   │
│  │     ├── Respiratory History (Cough, Hemoptysis, Wheeze)                 │   │
│  │     ├── GI History (Abdominal pain, Change in bowel habits)             │   │
│  │     ├── Neurological History (Headache, Seizures, Weakness)             │   │
│  │     ├── Musculoskeletal History (Joint pain, Back pain)                 │   │
│  │     ├── Psychiatric History (Depression, Anxiety, Psychosis)            │   │
│  │     ├── Paediatric History (Fever, Development, Immunization)           │   │
│  │     ├── Obstetric History (Antenatal, Pregnancy complications)          │   │
│  │     └── Gynaecological History (Menstrual, Discharge, Menopause)        │   │
│  │                                                                          │   │
│  │  🩺 Physical Examination (900+ scenarios)                               │   │
│  │     ├── Cardiovascular Examination (HIPJAP framework)                   │   │
│  │     ├── Respiratory Examination (IPTAP framework)                       │   │
│  │     ├── Abdominal Examination (9-region systematic)                     │   │
│  │     ├── Neurological Examination (Cranial nerves, Motor, Sensory)       │   │
│  │     ├── Musculoskeletal Examination (GALS, Joint-specific)              │   │
│  │     ├── Thyroid Examination                                             │   │
│  │     ├── Peripheral Vascular Examination                                 │   │
│  │     ├── Lymph Node Examination                                          │   │
│  │     ├── Paediatric Examination (Age-appropriate)                        │   │
│  │     ├── Obstetric Examination (Fundal height, Leopold's)                │   │
│  │     └── Gynaecological Examination                                      │   │
│  │                                                                          │   │
│  │  💬 Communication Skills (700+ scenarios)                               │   │
│  │     ├── Breaking Bad News (SPIKES framework)                            │   │
│  │     ├── Informed Consent                                                │   │
│  │     ├── Explaining Diagnosis/Investigations                             │   │
│  │     ├── Discussing Management Options                                   │   │
│  │     ├── Dealing with Angry/Difficult Patients                           │   │
│  │     ├── Cultural Sensitivity & Interpreter Use                          │   │
│  │     ├── Addressing Patient Concerns                                     │   │
│  │     ├── End-of-Life Discussions                                         │   │
│  │     └── Counselling (Lifestyle, Contraception)                          │   │
│  │                                                                          │   │
│  │  🏥 Emergency/Acute Scenarios (400+ scenarios)                          │   │
│  │     ├── Cardiac Emergencies (ACS, Arrhythmias)                          │   │
│  │     ├── Respiratory Emergencies (Asthma, PE, Pneumothorax)              │   │
│  │     ├── Neurological Emergencies (Stroke, Seizures)                     │   │
│  │     ├── GI Emergencies (GI Bleed, Acute Abdomen)                        │   │
│  │     ├── Anaphylaxis & Allergic Reactions                                │   │
│  │     ├── Sepsis Recognition                                              │   │
│  │     ├── Trauma Assessment (ATLS)                                        │   │
│  │     └── Toxicology/Overdose                                             │   │
│  │                                                                          │   │
│  │  📝 Interpretation Skills (200+ scenarios)                              │   │
│  │     ├── ECG Interpretation                                              │   │
│  │     ├── Chest X-ray Interpretation                                      │   │
│  │     ├── Blood Results (FBC, UEC, LFT, Troponin)                         │   │
│  │     ├── ABG Interpretation                                              │   │
│  │     └── Imaging (CT, MRI, Ultrasound basics)                            │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  BY STATION TYPE                                                        │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  📋 Static Stations (Read & Respond)                                    │   │
│  │     • Written responses to clinical scenarios                           │   │
│  │     • 8-minute time limit                                               │   │
│  │                                                                          │   │
│  │  🎭 Interactive Stations (AI Simulation)                                │   │
│  │     • AI Patient conversations (Text/Voice)                             │   │
│  │     • AI Examiner scoring                                               │   │
│  │     • Real-time feedback                                                │   │
│  │                                                                          │   │
│  │  🖐️ Procedural Stations                                                 │   │
│  │     • Suturing techniques                                               │   │
│  │     • IV cannulation (theory)                                           │   │
│  │     • Basic life support algorithms                                     │   │
│  │     • Procedure explanations                                            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.3 EPM Module (Extended Matching Questions / Emergency Medicine)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  📚 STUDY HUB → EPM (Extended Practice Module)                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Note: EPM can represent either:                                                │
│  • Extended Matching Questions (Question format with multiple stems)            │
│  • Emergency Practice Module (Emergency medicine focus)                         │
│                                                                                 │
│  NAVIGATION:                                                                    │
│  ├── Extended Matching Questions       [AMC Part 1 Format]                      │
│  └── Emergency Medicine Focus          [High-acuity scenarios]                  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  EXTENDED MATCHING QUESTIONS (EMQ) FORMAT                               │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  AMC Part 1 EMQ Structure:                                              │   │
│  │  • Theme (e.g., "Causes of Chest Pain")                                 │   │
│  │  • Option list (10-15 possible answers)                                 │   │
│  │  • 3-5 clinical stems to match                                          │   │
│  │                                                                          │   │
│  │  CATEGORIES:                                                            │   │
│  │  ├── Diagnosis EMQs (Match presentation to diagnosis)                   │   │
│  │  ├── Investigation EMQs (Match scenario to best investigation)          │   │
│  │  ├── Management EMQs (Match condition to best treatment)                │   │
│  │  ├── Drug Side Effects EMQs                                             │   │
│  │  └── Anatomy/Localization EMQs                                          │   │
│  │                                                                          │   │
│  │  EXAMPLES:                                                              │   │
│  │  Theme: Causes of Acute Chest Pain                                      │   │
│  │  Options: A. ACS  B. PE  C. Pneumothorax  D. Pericarditis...            │   │
│  │  Stem 1: 45yo smoker with crushing central chest pain radiating to arm  │   │
│  │  Stem 2: 30yo with sudden pleuritic pain and breathlessness             │   │
│  │  Stem 3: Young male with sharp pain after lifting weights               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  EMERGENCY MEDICINE PRACTICE MODULE                                     │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  High-acuity scenarios requiring rapid decision-making:                 │   │
│  │                                                                          │   │
│  │  TRIAGE CATEGORIES:                                                     │   │
│  │  🔴 Category 1: Immediately Life-Threatening                            │   │
│  │     • Cardiac arrest algorithms                                         │   │
│  │     • Airway obstruction                                                │   │
│  │     • Severe asthma/Anaphylaxis                                         │   │
│  │                                                                          │   │
│  │  🟠 Category 2: Potentially Life-Threatening                            │   │
│  │     • ACS with STEMI                                                    │   │
│  │     • Sepsis with hypotension                                           │   │
│  │     • Stroke with thrombolysis candidate                                │   │
│  │                                                                          │   │
│  │  🟡 Category 3: Urgent but Stable                                       │   │
│  │     • Moderate trauma                                                   │   │
│  │     • Moderate exacerbation of chronic disease                          │   │
│  │                                                                          │   │
│  │  🟢 Category 4 & 5: Less Urgent                                         │   │
│  │     • Minor injuries                                                    │   │
│  │     • Non-urgent presentations                                          │   │
│  │                                                                          │   │
│  │  FORMAT OPTIONS:                                                        │   │
│  │  • Timed rapid-fire questions (30 seconds per question)                 │   │
│  │  • ABCDE approach scenarios                                             │   │
│  │  • Resuscitation algorithm walkthroughs                                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 MODULE 2: PRACTICE ARENA (Assessment & Simulation)

### 2.1 AI Lab Clinical Exam (AMC Simulation)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🎯 PRACTICE ARENA → AI Lab Clinical Exam                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  SUB-MODULES:                                                                   │
│  ├── AI Patient Simulator              [Conversational OSCE practice]           │
│  ├── AI Examiner Scoring               [Real-time rubric-based scoring]         │
│  ├── Full Mock Exams                   [16-station simulations]                 │
│  └── Voice/Video Practice              [WebRTC-based simulation]                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  AI PATIENT SIMULATOR                                                   │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Interactive conversation practice with AI-powered virtual patients:    │   │
│  │                                                                          │   │
│  │  PRACTICE MODES:                                                        │   │
│  │  ├── Free Practice Mode                                                 │   │
│  │  │   • Choose any OSCE scenario                                          │   │
│  │  │   • No time limit                                                     │   │
│  │  │   • Hints available                                                   │   │
│  │  │   • Pause and review                                                  │   │
│  │  ├── Timed Exam Mode (8 minutes/station)                                │   │
│  │  │   • Real exam conditions                                              │   │
│  │  │   • No hints                                                          │   │
│  │  │   • Automatic cutoff                                                  │   │
│  │  └── Guided Learning Mode                                               │   │
│  │      • AI prompts when stuck                                              │   │
│  │      • Suggested next questions                                           │   │
│  │      • Real-time coaching                                                 │   │
│  │                                                                          │   │
│  │  EMOTIONAL STATES:                                                      │   │
│  │  • Neutral/Calm • Anxious • Tearful/Sad • Angry/Frustrated              │   │
│  │  • Confused • Defensive • Euphoric (Mania)                              │   │
│  │                                                                          │   │
│  │  VOICE OPTIONS:                                                         │   │
│  │  • Text chat only                                                       │   │
│  │  • AI Voice (ElevenLabs - Australian accent)                            │   │
│  │  • Voice recognition (Whisper STT)                                      │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  AI EXAMINER SCORING                                                    │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Real-time performance assessment using 15-mark rubrics:                │   │
│  │                                                                          │   │
│  │  SCORING CRITERIA (15 marks total):                                     │   │
│  │  ├── History Taking (3 marks)                                           │   │
│  │  │   • Systematic approach                                               │   │
│  │  │   • Appropriate questions                                             │   │
│  │  │   • Red flag identification                                           │   │
│  │  ├── Communication Skills (3 marks)                                     │   │
│  │  │   • Rapport building                                                  │   │
│  │  │   • Empathy shown                                                     │   │
│  │  │   • Clear explanation                                                 │   │
│  │  ├── Clinical Reasoning (3 marks)                                       │   │
│  │  │   • Differential diagnosis                                            │   │
│  │  │   • Appropriate investigations                                        │   │
│  │  │   • Management plan                                                   │   │
│  │  ├── Professionalism (2 marks)                                          │   │
│  │  │   • Introduction/Consent                                              │   │
│  │  │   • Safety netting                                                    │   │
│  │  └── Structure & Time Management (2 marks)                              │   │
│  │      • Organized approach                                               │   │
│  │      • Completes within time                                            │   │
│  │                                                                          │   │
│  │  FEEDBACK FEATURES:                                                     │   │
│  │  • Live score updates during conversation                               │   │
│  │  • Detailed post-session analysis                                       │   │
│  │  • Comparison to model answer                                           │   │
│  │  • Specific improvement suggestions                                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  FULL MOCK EXAMS                                                        │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Complete 16-station AMC Clinical Exam simulations:                     │   │
│  │                                                                          │   │
│  │  EXAM FORMAT:                                                           │   │
│  │  • 16 stations × 8 minutes each = 128 minutes                           │   │
│  │  • 2 rest stations (after stations 5 and 10)                            │   │
│  │  • Mix of history, examination, and communication stations              │   │
│  │                                                                          │   │
│  │  MOCK EXAM OPTIONS:                                                     │   │
│  │  ├── Quick Mock (4 stations, 32 minutes)                                │   │
│  │  ├── Half Mock (8 stations, 64 minutes)                                 │   │
│  │  ├── Full Mock (16 stations, 128 minutes)                               │   │
│  │  └── Custom Mock (User-selected stations)                               │   │
│  │                                                                          │   │
│  │  EXAM CATEGORIES:                                                       │   │
│  │  • Standard Mock (Balanced across all specialties)                      │   │
│  │  • Weakness Focus (Targets user's weak areas)                           │   │
│  │  • High-Yield Only (Most common exam scenarios)                         │   │
│  │  • Random Mix (Simulates real exam unpredictability)                    │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏥 MODULE 3: CLINICAL LAB (EMR & Clinical Skills)

### 3.1 EMR Practice System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  🏥 CLINICAL LAB → EMR Practice                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  INTERFACE OPTIONS:                                                             │
│  ├── Cerner PowerChart Simulation      [Dark theme, sidebar nav]                │
│  ├── Epic EHR Simulation               [Purple theme, icon nav]                 │
│  └── Generic EMR                       [Simplified interface]                   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PRACTICE MODULES                                                       │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │                                                                          │   │
│  │  📝 SOAP NOTE PRACTICE                                                  │   │
│  │     ├── Patient Review (Demographics, Vitals, History)                  │   │
│  │     ├── Subjective (HPI, PMHx, Medications, Allergies)                  │   │
│  │     ├── Objective (Physical exam findings, Investigations)              │   │
│  │     ├── Assessment (Differential diagnosis, Problem list)               │   │
│  │     └── Plan (Investigations, Treatment, Follow-up)                     │   │
│  │                                                                          │   │
│  │     VALIDATION:                                                         │   │
│  │     • Structure completeness                                            │   │
│  │     • Australian terminology check                                      │   │
│  │     • Red flag identification                                           │   │
│  │     • Clinical accuracy vs. scenario                                    │   │
│  │                                                                          │   │
│  │  💊 PRESCRIPTION WRITING                                                │   │
│  │     ├── PBS Medication Search (4,000+ medications)                      │   │
│  │     ├── Dose Calculator (Weight/age-based)                              │   │
│  │     ├── Route & Frequency Selection                                     │   │
│  │     ├── Quantity & Repeats (Max 5 repeats)                              │   │
│  │     ├── Indication Entry (PBS requirement)                              │   │
│  │     └── Authority Requirements Check                                    │   │
│  │                                                                          │   │
│  │     VALIDATION:                                                         │   │
│  │     • PBS compliance                                                    │   │
│  │     • Drug interactions                                                 │   │
│  │     • Allergy checking                                                  │   │
│  │     • Dose appropriateness                                              │   │
│  │     • Pregnancy category                                                │   │
│  │                                                                          │   │
│  │  🧪 PATHOLOGY ORDERING                                                    │   │
│  │     ├── MBS Item Number Search                                          │   │
│  │     ├── Common Panels (FBC, UEC, LFT, etc.)                             │   │
│  │     ├── Individual Test Selection                                       │   │
│  │     ├── Indication Entry                                                │   │
│  │     ├── Urgency Selection (Routine/Urgent/Emergency)                    │   │
│  │     └── Collection Instructions                                         │   │
│  │                                                                          │   │
│  │     VALIDATION:                                                         │   │
│  │     • MBS compliance                                                    │   │
│  │     • Indication appropriateness                                        │   │
│  │     • Frequency limits (e.g., lipids once/12 months)                    │   │
│  │     • Cost-effectiveness check                                          │   │
│  │                                                                          │   │
│  │  📋 REFERRAL LETTERS                                                      │   │
│  │     ├── Specialist Selection                                            │   │
│  │     ├── Reason for Referral                                             │   │
│  │     ├── Clinical Summary                                                │   │
│  │     ├── Urgency & Timeframe                                             │   │
│  │     └── Medicare Referral Requirements                                  │   │
│  │                                                                          │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PATIENT SCENARIOS (200+ Cases)                                         │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Organized by specialty with realistic Australian demographics:         │   │
│  │                                                                          │   │
│  │  ├── Medical Inpatients (50 cases)                                      │   │
│  │  ├── Surgical Inpatients (40 cases)                                     │   │
│  │  ├── Emergency Presentations (50 cases)                                 │   │
│  │  ├── Outpatient Clinics (40 cases)                                      │   │
│  │  └── GP Consultations (20 cases)                                        │   │
│  │                                                                          │   │
│  │  Each case includes:                                                    │   │
│  │  • Full patient demographics & history                                  │   │
│  │  • Presenting complaint & context                                       │   │
│  │  • Current medications & allergies                                      │   │
│  │  • Recent investigations                                                │   │
│  │  • Expected documentation standards                                     │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 MODULE 4: MEDICAL SCIENCE SUB-TOPICS

### 4.1 Basic Sciences Integration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  📚 STUDY HUB → Medical Science                                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  Foundational sciences integrated into clinical context:                        │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ANATOMY                                                                │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Organized by region with clinical correlations:                        │   │
│  │  ├── Thoracic Anatomy (Heart, Lungs, Mediastinum)                       │   │
│  │  ├── Abdominal Anatomy (GI, Hepatobiliary, GU)                          │   │
│  │  ├── Pelvic Anatomy (Reproductive, Urinary)                             │   │
│  │  ├── Head & Neck Anatomy                                                │   │
│  │  ├── Neuroanatomy (Brain, Spinal cord, Peripheral nerves)               │   │
│  │  ├── Musculoskeletal Anatomy                                            │   │
│  │  └── Surface Anatomy (Examination landmarks)                            │   │
│  │                                                                          │   │
│  │  INTEGRATION: Each topic links to relevant OSCE examinations            │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PHYSIOLOGY                                                             │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Systems-based with pathophysiology bridges:                            │   │
│  │  ├── Cardiovascular Physiology (ECG interpretation basics)              │   │
│  │  ├── Respiratory Physiology (ABG interpretation, Lung function)         │   │
│  │  ├── Renal Physiology (Fluid/electrolyte balance)                       │   │
│  │  ├── GI Physiology (Digestion, Absorption)                              │   │
│  │  ├── Endocrine Physiology (Hormone axes, Feedback loops)                │   │
│  │  ├── Neurophysiology (Reflexes, Sensory/motor pathways)                 │   │
│  │  └── Exercise Physiology (Stress testing, Rehabilitation)               │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PATHOLOGY                                                              │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Disease mechanisms organized by system:                                │   │
│  │  ├── General Pathology (Inflammation, Neoplasia, Degeneration)          │   │
│  │  ├── Cardiovascular Pathology (Atherosclerosis, Heart failure)          │   │
│  │  ├── Respiratory Pathology (COPD, Fibrosis, Infections)                 │   │
│  │  ├── GI Pathology (Ulcers, IBD, Malignancy)                             │   │
│  │  ├── Renal Pathology (GN, ATN, CKD progression)                         │   │
│  │  ├── Endocrine Pathology (Diabetes, Thyroid, Adrenal)                   │   │
│  │  ├── Haematopathology (Anemias, Leukemia, Lymphoma)                     │   │
│  │  └── Dermatopathology (Skin conditions, Melanoma)                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PHARMACOLOGY                                                           │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Australian-focused drug knowledge:                                     │   │
│  │  ├── Cardiovascular Drugs (Antihypertensives, Antiarrhythmics)          │   │
│  │  ├── Respiratory Drugs (Bronchodilators, Corticosteroids)               │   │
│  │  ├── Antibiotics (Empiric therapy, Resistance patterns)                 │   │
│  │  ├── Analgesics (WHO ladder, Opioid prescribing)                        │   │
│  │  ├── Anticoagulants (Warfarin, DOACs, Reversal)                         │   │
│  │  ├── Diabetes Medications (Metformin, Insulin, GLP-1)                   │   │
│  │  ├── Psychiatric Medications (Antidepressants, Antipsychotics)          │   │
│  │  ├── Emergency Drugs (ACLS protocols)                                   │   │
│  │  └── Toxicology (Overdose management)                                   │   │
│  │                                                                          │   │
│  │  FEATURES:                                                              │   │
│  │  • PBS status for each medication                                       │   │
│  │  • Drug interaction checker                                             │   │
│  │  • Dosing calculators                                                   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  CLINICAL BIOCHEMISTRY & HAEMATOLOGY                                    │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  Laboratory interpretation skills:                                      │   │
│  │  ├── Common Tests (FBC, UEC, LFT, CRP, Glucose)                         │   │
│  │  ├── Cardiac Markers (Troponin, BNP)                                    │   │
│  │  ├── Coagulation Studies (INR, aPTT, D-dimer)                           │   │
│  │  ├── ABG Interpretation (Acid-base, Oxygenation)                        │   │
│  │  ├── Iron Studies & B12/Folate                                          │   │
│  │  ├── Thyroid Function Tests                                             │   │
│  │  ├── Tumour Markers (PSA, CA-125, CEA)                                  │   │
│  │  └── Urinalysis & Microscopy                                            │   │
│  │                                                                          │   │
│  │  FORMAT:                                                                │   │
│  │  • Image-based case studies                                             │   │
│  │  • Interpretation questions                                             │   │
│  │  • Clinical correlation exercises                                       │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 MODULE 5: PROGRESS & ANALYTICS

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  📊 PROGRESS & ANALYTICS                                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  DASHBOARD SECTIONS:                                                            │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  OVERVIEW CARDS                                                         │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐   │   │
│  │  │   QUESTIONS  │ │   ACCURACY   │ │  READINESS   │ │    STREAK    │   │   │
│  │  │    2,847     │ │     76%      │ │     68%      │ │   12 days    │   │   │
│  │  │   answered   │ │              │ │              │ │      🔥      │   │   │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └──────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  PERFORMANCE BY MODULE                                                  │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  MCQs:        ████████████████████░░░░ 76% (2,847 questions)            │   │
│  │  OSCEs:       ██████████████░░░░░░░░░░ 58% (145 scenarios)              │   │
│  │  EMR Practice:███████████████░░░░░░░░░ 65% (23 sessions)                │   │
│  │  AI Sim:      ██████████░░░░░░░░░░░░░░ 42% (8 stations)                 │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  SPECIALTY BREAKDOWN (Spider/Radar Chart)                               │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │       Cardio ████████████████████░░░░ 78%                               │   │
│  │       Resp   ██████████████████░░░░░░ 72%                               │   │
│  │       Psych  ████████████████████░░░░ 80% ⭐ Strong                     │   │
│  │       GI     ██████████████░░░░░░░░░ 60%                                │   │
│  │       Neuro  ████████████████░░░░░░░ 65%                                │   │
│  │       Surgery ██████████████░░░░░░░░ 58% ⚠️ Weak                        │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │  ACHIEVEMENTS & GAMIFICATION                                            │   │
│  ├─────────────────────────────────────────────────────────────────────────┤   │
│  │  🏆 Learning:    Centurion (100 Qs) ✓  Scholar (1,000) ⏳               │   │
│  │  🎯 Accuracy:    High Performer (80%) ⏳  Elite (90%) 🔒                │   │
│  │  🔥 Consistency: Dedicated (14 days) ✓  Committed (30) 🔒               │   │
│  │  🎖️ Mastery:     Cardiologist (90%) 🔒  All-Rounder 🔒                  │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 UI COMPONENT ARCHITECTURE

### Shared Components Across Modules

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     SHARED UI COMPONENT LIBRARY                                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  LAYOUT COMPONENTS                                                              │
│  ├── AppShell (Header, Sidebar, Footer, Main content area)                      │
│  ├── PageHeader (Title, Breadcrumbs, Actions)                                   │
│  ├── SidebarNavigation (Collapsible menu tree)                                  │
│  └── ResponsiveGrid (Adaptive column layouts)                                   │
│                                                                                 │
│  NAVIGATION COMPONENTS                                                          │
│  ├── TabGroup (Horizontal/Vertical tabs)                                        │
│  ├── AccordionTree (Hierarchical topic tree)                                    │
│  ├── BreadcrumbTrail (Navigation path)                                          │
│  ├── Pagination (Page/Question navigation)                                      │
│  └── ProgressSteps (Multi-step wizard)                                          │
│                                                                                 │
│  CONTENT COMPONENTS                                                             │
│  ├── QuestionCard (MCQ display with options)                                    │
│  ├── ScenarioPanel (OSCE case presentation)                                     │
│  ├── ExplanationPanel (Answer explanation with citations)                       │
│  ├── ImageViewer (Medical images with annotations)                              │
│  ├── VideoPlayer (Clinical skills videos)                                       │
│  └── AudioPlayer (For AI simulation recordings)                                 │
│                                                                                 │
│  INTERACTION COMPONENTS                                                         │
│  ├── TimerDisplay (Countdown/up with warnings)                                  │
│  ├── ChatInterface (AI patient conversation)                                    │
│  ├── FormBuilder (Dynamic form generation)                                      │
│  ├── RichTextEditor (SOAP note editing)                                         │
│  ├── SearchBox (Global content search)                                          │
│  └── FilterPanel (Advanced filtering controls)                                  │
│                                                                                 │
│  FEEDBACK COMPONENTS                                                            │
│  ├── ScoreBadge (Numeric score with color coding)                               │
│  ├── ProgressBar (Linear progress indicator)                                    │
│  ├── RadarChart (Multi-dimensional performance)                                 │
│  ├── StreakCounter (Consecutive days indicator)                                 │
│  ├── AchievementBadge (Unlockable achievements)                                 │
│  ├── ValidationPanel (Multi-layer feedback)                                     │
│  └── ComparisonTable (Side-by-side analysis)                                    │
│                                                                                 │
│  EMR-SPECIFIC COMPONENTS                                                        │
│  ├── PatientBanner (Demographics bar)                                           │
│  ├── VitalSignsDisplay (Formatted vital signs)                                  │
│  ├── MedicationList (Prescription display)                                      │
│  ├── LabResultsTable (Pathology results)                                        │
│  ├── SOAPEditor (4-section note editor)                                         │
│  ├── DrugSearch (PBS medication lookup)                                         │
│  └── OrderEntryForm (Pathology ordering)                                        │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📱 RESPONSIVE BREAKPOINTS

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     RESPONSIVE DESIGN STRATEGY                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  BREAKPOINTS:                                                                   │
│  ├── Mobile: < 768px           [Single column, bottom nav, collapsed sidebar]   │
│  ├── Tablet: 768px - 1024px    [Two columns, collapsible sidebar]               │
│  ├── Desktop: 1024px - 1440px  [Full layout, fixed sidebar]                     │
│  └── Large: > 1440px           [Enhanced layouts, wider content]                │
│                                                                                 │
│  MODULE-SPECIFIC ADAPTATIONS:                                                   │
│                                                                                 │
│  MCQ Module:                                                                    │
│  • Mobile: Question + options stacked, swipe navigation                         │
│  • Desktop: Question on left, options right, explanation below                  │
│                                                                                 │
│  OSCE Module:                                                                   │
│  • Mobile: Scenario card, expandable sections                                   │
│  • Desktop: Scenario left, checklist right, timer top                           │
│                                                                                 │
│  EMR Module:                                                                    │
│  • Mobile: Simplified interface, single-panel view                              │
│  • Desktop: Full Cerner/Epic multi-panel layout                                 │
│                                                                                 │
│  AI Simulation:                                                                 │
│  • Mobile: Audio-only mode (no video to save bandwidth)                         │
│  • Desktop: Full WebRTC with video avatar                                       │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔐 ACCESS CONTROL BY SUBSCRIPTION

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                     FEATURE ACCESS MATRIX                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  FREE TIER:                                                                     │
│  ├── 200 MCQs (Mixed specialties)                                               │
│  ├── 10 OSCE scenarios (History taking only)                                    │
│  ├── Basic progress tracking                                                    │
│  └── Mobile PWA access                                                          │
│                                                                                 │
│  PRO TIER ($49/month):                                                          │
│  ├── 18,000+ MCQs (All specialties, all formats)                                │
│  ├── 3,000+ OSCE scenarios (All types)                                          │
│  ├── EMR Practice System (Cerner + Epic)                                        │
│  ├── AI Tutor (100 queries/month)                                               │
│  ├── Study plans & analytics                                                    │
│  ├── Offline mode                                                               │
│  └── Extended Matching Questions                                                │
│                                                                                 │
│  ULTIMATE TIER ($79/month):                                                     │
│  ├── Everything in Pro                                                          │
│  ├── AI Lab Clinical Exam (Unlimited simulations)                               │
│  ├── AI Patient with voice synthesis                                            │
│  ├── AI Examiner scoring                                                        │
│  ├── 1-on-1 OSCE practice sessions                                              │
│  ├── Unlimited AI tutor queries                                                 │
│  └── Priority support                                                           │
│                                                                                 │
│  INSTITUTIONAL:                                                                 │
│  ├── Bulk user management                                                       │
│  ├── Progress dashboard for all students                                        │
│  ├── Custom branding                                                            │
│  ├── LMS integration                                                            │
│  └── White-label option                                                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 RELATED DOCUMENTS

| Document | Purpose |
|----------|---------|
| `MODULE_ARCHITECTURE_COMPARISON_ANALYSIS.md` | Overall system comparison |
| `planning/feature-modules-2026-02-01/README.md` | Implementation roadmap |
| `EMR_PRACTICE_SYSTEM_PRD_COMPLETE.md` | EMR system specification |
| `INDIVIDUALIZED_LEARNING_SYSTEM_SPEC.md` | Adaptive learning details |
| `AMC_BLUEPRINT_COVERAGE_ANALYSIS_REPORT.md` | Content coverage analysis |

---

**Last Updated:** 2026-02-06  
**Status:** Architecture Specification Complete  
**Next Steps:** UI Component Implementation
