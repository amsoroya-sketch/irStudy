# Dr. Amir OSCE UI/UX Implementation Plan

**Document Version:** 1.0
**Date:** 2026-05-27
**Status:** Ready for Implementation
**Target OSCE:** GI-PUD-001 (Upper Abdominal Pain - Peptic Ulcer Disease)

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Design Philosophy](#design-philosophy)
3. [Information Architecture](#information-architecture)
4. [UI Component Specifications](#ui-component-specifications)
5. [User Journey Flows](#user-journey-flows)
6. [Wireframes & Layouts](#wireframes--layouts)
7. [Implementation Roadmap](#implementation-roadmap)
8. [Technical Integration](#technical-integration)
9. [Success Metrics](#success-metrics)

---

## Executive Summary

### The Challenge

Dr. Amir OSCEs contain **15x more content** than typical OSCEs:
- 724 lines of comprehensive clinical content
- 8 marking criteria with 30+ sub-criteria
- 9 learning objectives
- 7 red flag warnings
- 6 common pitfalls
- 4 Australian guideline references
- 9 clinical pearls
- Complete differential diagnosis trees
- Detailed management pathways

**Current UI Problem:** Basic session interface shows only chat, timer, and final score. **95% of valuable content is hidden.**

### The Solution

**Three-Phase Progressive Disclosure UI:**
1. **Pre-Session** - Learning preparation (objectives, key points, clinical context)
2. **During-Session** - Essential clinical support (red flags, rubric reference, quick tips)
3. **Post-Session** - Deep analysis and learning (performance breakdown, evidence links, missed opportunities)

### Key Innovations

✅ **Clinical Context Panel** - Always-visible reference for critical information
✅ **Red Flag Alert System** - Real-time warnings for must-not-miss diagnoses
✅ **Evidence Integration** - Inline citations to Australian guidelines
✅ **Performance Analysis** - Detailed breakdown with benchmarks and recommendations
✅ **Dr. Amir Teaching Points** - Integrated mnemonic and clinical pearls

---

## Design Philosophy

### Core Principles

1. **Medical Education First**
   - Content structured for learning, not just assessment
   - Teaching points prominently displayed
   - Evidence-based learning with citations

2. **Progressive Disclosure**
   - Show what's needed, when it's needed
   - Don't overwhelm with all 724 lines at once
   - Allow deep-diving for motivated learners

3. **Australian Medical Context**
   - PBS codes, eTG guidelines, local medications prominent
   - AMC exam alignment clearly marked
   - Cultural safety considerations integrated

4. **Accessibility & Inclusion**
   - WCAG 2.2 AA compliance maintained
   - Screen reader optimized
   - Keyboard navigation throughout
   - High contrast mode support

5. **Mobile-First Responsive**
   - Full functionality on tablet/mobile
   - Study anywhere, anytime
   - Offline capability for downloaded OSCEs

---

## Information Architecture

### Content Organization Hierarchy

```
GI-PUD-001: Upper Abdominal Pain
│
├── 📋 STATION OVERVIEW (Pre-Session)
│   ├── Quick Facts (8 min, Gastroenterology, Intermediate)
│   ├── Learning Objectives (9 items)
│   ├── Key Teaching Points (8 critical distinctions)
│   └── What You'll Practice (SOCRATES, red flags, DDx)
│
├── 🩺 CLINICAL CONTEXT (Always Available)
│   ├── Patient Scenario Summary
│   │   ├── Demographics (32M, truck driver)
│   │   ├── Chief Complaint
│   │   ├── Current Medications (⚠️ Nurofen 400mg TDS - KEY!)
│   │   └── Risk Factors (alcohol, ex-smoker, family history)
│   │
│   ├── Red Flags Warning Panel
│   │   ├── 🚨 Must Screen For (hematemesis, melena, weight loss)
│   │   ├── Significance of Each Flag
│   │   └── Required Actions
│   │
│   └── Critical Teaching Points
│       ├── Gastric vs Duodenal Timing (Dr. Amir)
│       ├── Malignancy Risk Difference
│       └── NSAID Cessation Priority
│
├── 💬 ACTIVE SESSION
│   ├── AI Patient Interaction (WebSocket chat)
│   ├── Timer (8:00 countdown)
│   ├── Session Controls (pause, end early)
│   ├── Marking Rubric Reference (collapsible)
│   └── Quick Tips Panel (contextual hints)
│
├── 📊 PERFORMANCE ANALYSIS (Post-Session)
│   ├── Score Breakdown (15 marks, per criterion)
│   ├── Transcript Review (what you said vs ideal)
│   ├── Red Flags Assessment (did you screen all 7?)
│   ├── Missed Opportunities
│   ├── Strengths Identified
│   ├── Targeted Improvement Plan
│   └── Peer Benchmarking
│
└── 📚 DEEP LEARNING (Optional Exploration)
    ├── Complete Differential Diagnosis
    ├── Evidence & Guidelines
    │   ├── eTG Guidelines (linked excerpts)
    │   ├── PBS Information
    │   └── Academic References
    ├── Management Pathways (flowcharts)
    ├── Common Pitfalls (6 mistakes to avoid)
    ├── Clinical Pearls (9 practical tips)
    └── Related OSCEs (6 linked stations)
```

---

## UI Component Specifications

### 1. Pre-Session: OSCE Station Card

**Location:** `/practice/osces` (OSCE list view)

```
┌─────────────────────────────────────────────────────────────────┐
│ 🏥 GI-PUD-001: Upper Abdominal Pain - Peptic Ulcer Disease    │
│                                                                 │
│ ⭐⭐⭐ HIGH-YIELD AMC TOPIC                                      │
│                                                                 │
│ 📍 Gastroenterology • Upper GI                                 │
│ 📊 Intermediate                                                │
│ ⏱️ 8 minutes                                                    │
│ 📝 History Taking                                              │
│                                                                 │
│ ────────────────────────────────────────────────────────────── │
│                                                                 │
│ 🎯 KEY LEARNING POINTS                                         │
│   • Distinguish gastric vs duodenal ulcer by pain timing      │
│   • Identify NSAID-induced PUD and management                 │
│   • Screen for red flags (malignancy, bleeding, perforation)  │
│   • Apply Dr. Amir's 5 Ps framework systematically           │
│                                                                 │
│ 🚨 RED FLAGS TO ASSESS (7)                                     │
│   Hematemesis • Melena • Dysphagia • Weight loss • Age >55    │
│                                                                 │
│ 📈 YOUR STATS                                                  │
│   Times Practiced: 0                                           │
│   Best Score: --/15                                            │
│   Average: -- (Platform: 11.2/15)                             │
│                                                                 │
│ ────────────────────────────────────────────────────────────── │
│                                                                 │
│ [📖 VIEW DETAILS]  [▶️ START PRACTICE]  [🎯 MOCK EXAM MODE]   │
└─────────────────────────────────────────────────────────────────┘
```

**Material-UI Components:**
- `Card` with `CardHeader`, `CardContent`, `CardActions`
- `Chip` for tags (HIGH-YIELD, specialty, difficulty)
- `LinearProgress` for user progress
- `Tooltip` for stat explanations

**Interactions:**
- Click card → Expand to show full details
- "VIEW DETAILS" → Navigate to `/practice/osces/308/overview`
- "START PRACTICE" → Navigate to `/practice/osces/308/session`
- "MOCK EXAM MODE" → Harder conditions (no hints, no pause)

---

### 2. Pre-Session: Station Overview Page

**Location:** `/practice/osces/308/overview`

**Layout:** Tabbed interface with 5 tabs

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to OSCE List                                            │
│                                                                 │
│ GI-PUD-001: Upper Abdominal Pain - Peptic Ulcer Disease       │
│ Gastroenterology • Intermediate • 8 min • History Taking       │
│                                                                 │
│ ┌───────────────────────────────────────────────────────────┐ │
│ │ [📋 OVERVIEW] [🎯 OBJECTIVES] [🩺 SCENARIO] [📚 LEARN] [📊] │ │
│ └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│ ╔═══════════════════════════════════════════════════════════╗ │
│ ║ TAB: OVERVIEW                                             ║ │
│ ╚═══════════════════════════════════════════════════════════╝ │
│                                                                 │
│ 📖 WHAT YOU'LL DO                                              │
│   You are a medical officer in General Practice. A 32-year-    │
│   old male truck driver presents with upper abdominal pain.    │
│   Take a focused history in 8 minutes.                         │
│                                                                 │
│ 🎯 KEY TASKS                                                   │
│   ✓ Take systematic SOCRATES pain history                     │
│   ✓ Identify risk factors for peptic ulcer disease           │
│   ✓ Screen for red flag symptoms                              │
│   ✓ Generate appropriate differential diagnosis               │
│   ✓ Outline investigation and management approach             │
│                                                                 │
│ ⭐ DR. AMIR'S CRITICAL TEACHING POINTS                         │
│                                                                 │
│   🔴 GASTRIC ULCER                                            │
│   Pain: IMMEDIATELY after eating                               │
│   Malignancy: CAN become malignant (requires endoscopy)       │
│                                                                 │
│   🔵 DUODENAL ULCER                                           │
│   Pain: 2-3 HOURS after eating                                │
│   Malignancy: Does NOT become malignant                       │
│                                                                 │
│   💊 NSAID CESSATION                                          │
│   Most important management step!                              │
│   Switch: Nurofen (ibuprofen) → Panadol (paracetamol)        │
│                                                                 │
│ 📊 MARKING CRITERIA (15 marks total)                          │
│   Introduction & Rapport           1 mark                      │
│   SOCRATES Pain History            2 marks                     │
│   Risk Factor Identification       2 marks                     │
│   Red Flag Screening               2 marks                     │
│   Differential Diagnosis           3 marks                     │
│   Clinical Reasoning               2 marks                     │
│   Management Plan                  2 marks                     │
│   Communication Skills             1 mark                      │
│                                                                 │
│   Pass Score: 10/15 (67%)                                     │
│                                                                 │
│ ────────────────────────────────────────────────────────────── │
│                                                                 │
│            [▶️ START PRACTICE SESSION]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Tab 2: OBJECTIVES**

```
╔═══════════════════════════════════════════════════════════╗
║ TAB: LEARNING OBJECTIVES (9)                              ║
╚═══════════════════════════════════════════════════════════╝

By completing this OSCE, you will be able to:

✓ Demonstrate systematic approach to upper abdominal pain
  using SOCRATES framework

✓ Identify NSAID-induced peptic ulcer disease as a common
  and preventable condition

✓ Distinguish between gastric and duodenal ulcers based on
  timing of pain relative to meals

✓ Recognize the malignant potential of gastric ulcers
  (requiring endoscopy) versus duodenal ulcers (no
  malignant potential)

✓ Screen effectively for red flag symptoms requiring urgent
  investigation

✓ Generate evidence-based differential diagnosis for
  epigastric pain

✓ Formulate appropriate investigation strategy including
  H. pylori testing

✓ Recommend safe cessation of NSAIDs with appropriate
  alternative analgesia

✓ Apply Australian guidelines for management of peptic
  ulcer disease

────────────────────────────────────────────────────────────

📚 RELATED STUDY RESOURCES

• AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md (13,000 words)
• eTG: Gastrointestinal > Peptic Ulcer Disease
• Talley & O'Connor 9th Ed: Chapter 14 (p. 412-428)
```

**Tab 3: CLINICAL SCENARIO**

```
╔═══════════════════════════════════════════════════════════╗
║ TAB: PATIENT SCENARIO                                     ║
╚═══════════════════════════════════════════════════════════╝

👤 PATIENT DEMOGRAPHICS
   Name: Mark (simulated patient)
   Age: 32 years
   Gender: Male
   Occupation: Long-haul truck driver
   Ethnicity: Caucasian Australian

💊 CURRENT MEDICATIONS (CRITICAL!)

   ⚠️ Ibuprofen (Nurofen) 400mg TDS
      Duration: 6 months
      Indication: Lower back pain
      PBS Code: Not PBS listed (OTC)
      → KEY RISK FACTOR FOR PUD!

   🔹 Quickies antacid tablets 2 tabs PRN
      Duration: 3 weeks
      Indication: Abdominal pain relief

🚫 ALLERGIES
   No known drug allergies

📋 PAST MEDICAL HISTORY
   • Chronic lower back pain (mechanical, work-related)
   • No previous abdominal surgery
   • No history of peptic ulcer disease
   • No known GORD

👪 FAMILY HISTORY
   • Father had duodenal ulcer age 45 ← RELEVANT!
   • Mother has hypertension

🚬 SOCIAL HISTORY
   Smoking: Ex-smoker, quit 2 years ago (10 pack-year)
   Alcohol: 10-15 standard drinks/week (mainly beer)
   Diet: Irregular meals, frequent fast food
   Coffee: 4-5 cups daily
   Work: High stress, long hours, irregular eating

🩺 VITAL SIGNS (On Presentation)
   HR: 78 bpm          BP: 128/82 mmHg
   RR: 16/min          Temp: 36.8°C
   SpO2: 99% (RA)      BMI: 27.5 kg/m²

────────────────────────────────────────────────────────────

🚨 RED FLAGS TO SCREEN FOR

During your history, you MUST screen for these 7 red flags:

1. ⚠️ Hematemesis (vomiting blood/coffee-ground)
   → Upper GI bleeding, urgent endoscopy

2. ⚠️ Melena (black, tarry stools)
   → Significant blood loss, urgent investigation

3. ⚠️ Dysphagia / Odynophagia
   → May indicate gastric cancer or stricture

4. ⚠️ Unintentional weight loss (>5kg/6mo)
   → Red flag for malignancy in gastric ulcer

5. ⚠️ Sudden severe pain with peritonism
   → Perforated ulcer, surgical emergency

6. ⚠️ Age >55 with new-onset dyspepsia
   → Increased gastric cancer risk

7. ⚠️ Persistent symptoms despite 4-8 weeks PPI
   → Complicated ulcer or alternative diagnosis

NOTE: This patient is 32 years old with no red flags present.
However, you should still screen systematically!
```

**Tab 4: DEEP LEARNING**

```
╔═══════════════════════════════════════════════════════════╗
║ TAB: EVIDENCE & GUIDELINES                                ║
╚═══════════════════════════════════════════════════════════╝

📚 AUSTRALIAN GUIDELINES

┌─────────────────────────────────────────────────────────┐
│ eTG: Gastrointestinal > Peptic Ulcer Disease          │
│                                                         │
│ Key Recommendations:                                    │
│ • Test all patients for H. pylori, eradicate if +ve   │
│ • Cease NSAIDs if possible, or use with PPI            │
│ • First-line PPI therapy for 4-8 weeks                │
│ • Endoscopy for red flags or age >55 new dyspepsia    │
│                                                         │
│ [🔗 View Full Guideline]                               │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ PBS: Proton Pump Inhibitors                            │
│                                                         │
│ • Streamlined authority for ongoing PPI (>4-8 weeks)   │
│ • Authority code 4497 for maintenance PUD therapy      │
│                                                         │
│ [🔗 View PBS Criteria]                                 │
└─────────────────────────────────────────────────────────┘

────────────────────────────────────────────────────────────

🧠 CLINICAL PEARLS (9)

💡 Dr. Amir's Mnemonic
   "G for Gastric = Goes with food (immediate pain)"
   "D for Duodenal = Delayed (2-3 hours)"

💡 NSAID Risk
   Even 2-4 weeks NSAID use can cause ulcers in
   susceptible individuals

💡 H. pylori Testing Timing
   MUST cease PPI 2 weeks before urea breath test
   for accurate results

💡 Australian Context
   Truck drivers at increased risk: irregular meals,
   high stress, frequent NSAID use for back pain

💡 PPI Dosing
   Give 30-60 minutes before breakfast for optimal
   acid suppression

[+ 4 more clinical pearls...]

────────────────────────────────────────────────────────────

⚠️ COMMON PITFALLS (6)

❌ Failing to ask about NSAID use
   Impact: Miss most important modifiable risk factor
   Prevention: Screen ALL medications including OTC

❌ Not distinguishing pain timing relative to meals
   Impact: Cannot differentiate gastric vs duodenal
   Prevention: Ask "How long after eating?"

❌ Inadequate red flag screening
   Impact: Miss urgent referral for cancer
   Prevention: Systematic screening of all 7 flags

[+ 3 more common pitfalls...]

────────────────────────────────────────────────────────────

📖 REFERENCES (6)

1. Talley NJ, O'Connor S. Clinical Examination:
   A Systematic Guide to Physical Diagnosis. 9th ed.
   2024. (Abdominal examination p. 412-428)

2. eTG: Gastrointestinal v7. 2024. (PUD management
   and H. pylori eradication protocols)

3. Lanas A, Chan FKL. Peptic ulcer disease.
   Lancet. 2017;390(10094):613-624.

[+ 3 more references...]
```

**Tab 5: STATISTICS**

```
╔═══════════════════════════════════════════════════════════╗
║ TAB: YOUR PERFORMANCE & BENCHMARKS                        ║
╚═══════════════════════════════════════════════════════════╝

📊 YOUR STATS

Practice Sessions: 0
Best Score: --/15
Average Score: --
Time to Pass: --

────────────────────────────────────────────────────────────

📈 PLATFORM BENCHMARKS (n=1,247 students)

Average Score: 11.2/15 (74.7%)
Pass Rate: 82.3%
Average Time Used: 7:23 / 8:00

Score Distribution:
  13-15 (Excellent): ████████░░ 23%
  10-12 (Pass):      ████████████████████ 57%
  0-9 (Fail):        ██████ 20%

────────────────────────────────────────────────────────────

🎯 MOST CHALLENGING CRITERIA (Low scores)

1. Differential Diagnosis (avg 1.8/3)
   → Many students miss gastric vs duodenal distinction

2. Risk Factor Identification (avg 1.2/2)
   → NSAID use often not explored thoroughly

3. Red Flag Screening (avg 1.5/2)
   → Weight loss and dysphagia commonly missed

────────────────────────────────────────────────────────────

💪 HIGHEST SCORING CRITERIA

1. Introduction & Rapport (avg 0.9/1)
2. Communication Skills (avg 0.8/1)
3. SOCRATES Framework (avg 1.7/2)
```

**Material-UI Components:**
- `Tabs` and `TabPanel` for navigation
- `Accordion` for expandable sections
- `Alert` with `AlertTitle` for red flags
- `List` with `ListItem` for objectives
- `Divider` for section separation
- `Link` for external resources

---

### 3. Active Session: Main Practice Interface

**Location:** `/practice/osces/308/session`

**Layout:** Three-panel layout (2-column on desktop, stacked on mobile)

```
┌─────────────────────────────────────────────────────────────────┐
│ GI-PUD-001: Upper Abdominal Pain         ⏱️ 06:23    [⏸️] [⏹️] │
├──────────────────────────────┬──────────────────────────────────┤
│                              │                                  │
│  LEFT: AI PATIENT CHAT       │  RIGHT: CLINICAL CONTEXT PANEL  │
│  (70% width on desktop)      │  (30% width, collapsible)       │
│                              │                                  │
│  ┌──────────────────────┐   │  ┌─────────────────────────┐    │
│  │ 🤖 Dr. Mark (AI)     │   │  │ 📋 PATIENT SUMMARY      │    │
│  │ Hello, I'm Mark. I've│   │  │                         │    │
│  │ been having some     │   │  │ 👤 32M truck driver     │    │
│  │ stomach pain...      │   │  │ 💊 NSAID use (6 mo)     │    │
│  └──────────────────────┘   │  │ 🍺 Alcohol 10-15/wk     │    │
│                              │  │ 🚬 Ex-smoker            │    │
│  ┌──────────────────────┐   │  │ 👪 FHx: PUD in father   │    │
│  │ 👨‍⚕️ You             │   │  └─────────────────────────┘    │
│  │ Good morning Mark.   │   │                                  │
│  │ Can you tell me more │   │  ┌─────────────────────────┐    │
│  │ about this pain?     │   │  │ 🚨 RED FLAGS TO SCREEN  │    │
│  └──────────────────────┘   │  │                         │    │
│                              │  │ ☐ Hematemesis           │    │
│  [Type your question...]    │  │ ☐ Melena                │    │
│                              │  │ ☐ Dysphagia             │    │
│  ┌────────────────────────┐ │  │ ☐ Weight loss           │    │
│  │ 💡 QUICK TIP           │ │  │ ☐ Severe pain           │    │
│  │ Use SOCRATES framework │ │  │ ☐ Age >55               │    │
│  │ to characterize pain:  │ │  │ ☐ Persistent symptoms   │    │
│  │ Site, Onset, Character,│ │  └─────────────────────────┘    │
│  │ Radiation...           │ │                                  │
│  └────────────────────────┘ │  ⭐ KEY TEACHING POINTS         │
│                              │                                  │
│                              │  🔴 GASTRIC: Pain immediate     │
│                              │     after eating, CAN be        │
│                              │     malignant                   │
│                              │                                  │
│                              │  🔵 DUODENAL: Pain 2-3 hrs      │
│                              │     after eating, NOT           │
│                              │     malignant                   │
│                              │                                  │
│                              │  💊 NSAID cessation most        │
│                              │     important step!             │
│                              │                                  │
│                              │  ┌─────────────────────────┐    │
│                              │  │ 📊 RUBRIC REFERENCE     │    │
│                              │  │ [Expand to view]        │    │
│                              │  └─────────────────────────┘    │
│                              │                                  │
└──────────────────────────────┴──────────────────────────────────┘
```

**Desktop Layout (≥1024px):**
- Two-column split (70/30)
- Clinical context always visible (sticky)
- Chat scrollable independently

**Tablet Layout (768-1023px):**
- Clinical context collapsible drawer (swipe from right)
- Floating action button to toggle context panel

**Mobile Layout (<768px):**
- Single column, full-width chat
- Clinical context as bottom sheet (swipe up)
- Red flags checklist always visible at top

**Material-UI Components:**
- `Grid` for responsive layout
- `Paper` for panels
- `Drawer` for mobile context panel
- `Fab` for floating toggle button
- `Checkbox` for red flag tracking
- `Collapse` for expandable sections
- `Alert` with `severity="warning"` for red flags

**Real-Time Features:**

1. **Red Flag Tracking**
   - Checkboxes update as AI detects you've asked about each flag
   - Green checkmarks when screened
   - Red warning icon if time running low and flags missed

2. **Contextual Tips**
   - AI analyzes conversation flow
   - Shows relevant tips at appropriate times
   - Example: If 3 minutes elapsed and no NSAID question → "💡 Have you explored medication history including OTC drugs?"

3. **Timer Warnings**
   - 2:00 remaining → Yellow alert
   - 1:00 remaining → Orange alert with "Time to wrap up and present"
   - 0:30 remaining → Red alert

---

### 4. Active Session: Marking Rubric Reference (Expandable)

**Collapsed State:**
```
┌─────────────────────────────────────────────┐
│ 📊 MARKING RUBRIC REFERENCE                │
│ [Click to expand and view 8 criteria]      │
└─────────────────────────────────────────────┘
```

**Expanded State:**
```
┌─────────────────────────────────────────────────────────┐
│ 📊 MARKING RUBRIC (15 marks total)         [Collapse ▲] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ 1. Introduction & Rapport                      1 mark  │
│    • Introduces self appropriately           (0.25)   │
│    • Confirms patient identity               (0.25)   │
│    • Establishes rapport                     (0.25)   │
│    • Explains purpose                        (0.25)   │
│                                                         │
│ 2. SOCRATES Pain History                      2 marks  │
│    • Site (exact location)                   (0.25)   │
│    • Onset (duration, gradual/sudden)        (0.25)   │
│    • Character (dull, sharp, burning)        (0.25)   │
│    • Radiation (back, chest, other)          (0.25)   │
│    • Associations (nausea, vomiting, meals)  (0.5)    │
│    • Time course (progression, pattern)      (0.25)   │
│    • Exacerbating/Relieving factors          (0.25)   │
│    ⭐ KEY: Gastric pain immediate vs Duodenal 2-3 hrs │
│                                                         │
│ 3. Risk Factor Identification                 2 marks  │
│    • NSAID use (type, dose, duration)        (0.5)    │
│    • Smoking history                         (0.25)   │
│    • Alcohol (quantified)                    (0.25)   │
│    • Dietary factors (coffee, meals)         (0.25)   │
│    • Stress factors                          (0.25)   │
│    • Family history PUD                      (0.25)   │
│    • Previous PUD history                    (0.25)   │
│    ⭐ NSAID cessation most important step!             │
│                                                         │
│ 4. Red Flag Screening                         2 marks  │
│    • Hematemesis                             (0.25)   │
│    • Melena                                  (0.25)   │
│    • Hematochezia                            (0.25)   │
│    • Dysphagia                               (0.25)   │
│    • Odynophagia                             (0.25)   │
│    • Weight loss (quantified)                (0.25)   │
│    • Severe/sudden pain                      (0.25)   │
│    • Constitutional symptoms                 (0.25)   │
│    ⭐ Gastric ulcers CAN → cancer (need scope!)        │
│                                                         │
│ 5. Differential Diagnosis                     3 marks  │
│    • PUD as most likely diagnosis            (0.75)   │
│    • Gastric vs duodenal distinction         (0.5)    │
│    • 2+ alternative diagnoses                (0.75)   │
│    • Must-not-miss diagnoses                 (0.5)    │
│    • Clinical reasoning                      (0.5)    │
│    ⭐ Duodenal NOT malignant, Gastric CAN BE           │
│                                                         │
│ 6. Clinical Reasoning                         2 marks  │
│    • Links NSAID use to PUD pathophysiology  (0.5)    │
│    • Recognizes H. pylori testing need       (0.5)    │
│    • Understands endoscopy indications       (0.5)    │
│    • Investigation sequence                  (0.5)    │
│                                                         │
│ 7. Management Plan                            2 marks  │
│    • Cease NSAIDs                            (0.5)    │
│    • Safe alternative (paracetamol)          (0.25)   │
│    • PPI therapy                             (0.5)    │
│    • H. pylori testing                       (0.25)   │
│    • Investigations (FBC, iron studies)      (0.25)   │
│    • Lifestyle modifications                 (0.25)   │
│    ⭐ Switch Nurofen → Panadol                          │
│                                                         │
│ 8. Communication Skills                       1 mark   │
│    • Clear, jargon-free language             (0.25)   │
│    • Empathy and addressing concerns         (0.25)   │
│    • Verbal and non-verbal communication     (0.25)   │
│    • Systematic and organized                (0.25)   │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ TOTAL: 15 marks  |  PASS: 10/15 (67%)                 │
└─────────────────────────────────────────────────────────┘
```

**Interaction:**
- Click to expand/collapse
- Scrollable within panel
- Teaching points (⭐) highlighted in gold
- Sub-criteria show mark allocation

---

### 5. Post-Session: Performance Analysis Dashboard

**Location:** `/practice/osces/308/results/{session_id}`

**Layout:** Multi-section scroll page with progress tracking sidebar

```
┌─────────────────────────────────────────────────────────────────┐
│ ← Back to Practice                Session #1 - 2026-05-27      │
│                                                                 │
│ GI-PUD-001: Upper Abdominal Pain - Peptic Ulcer Disease       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🎯 YOUR SCORE: 11/15 (73%) ✓ PASS                             │
│                                                                 │
│ Platform Average: 11.2/15 (75%)                                │
│ Time Used: 7:45 / 8:00                                         │
│                                                                 │
│ ████████████████░░░░  73%                                      │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌────────────────────────┬────────────────────────────────────────┐
│ SIDEBAR (sticky)       │ MAIN CONTENT                           │
│                        │                                        │
│ 📊 Jump to Section:    │ ═══════════════════════════════════    │
│                        │ SCORE BREAKDOWN                        │
│ • Score Breakdown      │ ═══════════════════════════════════    │
│ • Transcript Review    │                                        │
│ • Red Flags Analysis   │ ┌────────────────────────────────┐    │
│ • Strengths            │ │ Criterion               Score  │    │
│ • Areas to Improve     │ ├────────────────────────────────┤    │
│ • Action Plan          │ │ 1. Introduction         1/1 ✓  │    │
│ • Peer Comparison      │ │ 2. SOCRATES History     1.5/2  │    │
│                        │ │ 3. Risk Factors         1/2    │    │
│ Completed:             │ │ 4. Red Flag Screening   1.75/2 │    │
│ ▓▓▓▓░░ 4/6 sections    │ │ 5. Differential Dx      2/3    │    │
│                        │ │ 6. Clinical Reasoning   1.5/2  │    │
│                        │ │ 7. Management Plan      1.5/2  │    │
│                        │ │ 8. Communication        0.75/1 │    │
│                        │ └────────────────────────────────┘    │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ 📈 CRITERION ANALYSIS                  │
│                        │                                        │
│                        │ 🟢 STRONG (≥80%)                       │
│                        │    ✓ Introduction & Rapport (100%)    │
│                        │    ✓ Red Flag Screening (88%)         │
│                        │                                        │
│                        │ 🟡 ADEQUATE (60-79%)                   │
│                        │    • SOCRATES History (75%)           │
│                        │    • Clinical Reasoning (75%)         │
│                        │    • Management Plan (75%)            │
│                        │    • Communication (75%)              │
│                        │                                        │
│                        │ 🔴 NEEDS IMPROVEMENT (<60%)            │
│                        │    ✗ Risk Factor Identification (50%) │
│                        │    ✗ Differential Diagnosis (67%)     │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ TRANSCRIPT REVIEW                      │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ View your conversation with the AI     │
│                        │ patient, annotated with scoring and    │
│                        │ missed opportunities.                  │
│                        │                                        │
│                        │ ┌────────────────────────────────┐    │
│                        │ │ 00:15 👨‍⚕️ You                  │    │
│                        │ │ "Good morning, I'm Dr. Smith.  │    │
│                        │ │ Can you tell me about your     │    │
│                        │ │ pain?"                         │    │
│                        │ │ ✓ Good introduction            │    │
│                        │ │                                │    │
│                        │ │ 00:23 🤖 Mark                   │    │
│                        │ │ "Hi doctor, I've had this dull │    │
│                        │ │ ache in my upper stomach for a │    │
│                        │ │ few weeks now..."              │    │
│                        │ │                                │    │
│                        │ │ 01:05 👨‍⚕️ You                  │    │
│                        │ │ "Where exactly is the pain?"   │    │
│                        │ │ ✓ Site (SOCRATES)              │    │
│                        │ │                                │    │
│                        │ │ 01:12 🤖 Mark                   │    │
│                        │ │ "Right here in the middle,     │    │
│                        │ │ just below my ribs"            │    │
│                        │ │ [Points to epigastrium]        │    │
│                        │ │                                │    │
│                        │ │ 02:34 👨‍⚕️ You                  │    │
│                        │ │ "Does the pain change with     │    │
│                        │ │ eating?"                       │    │
│                        │ │ ✓ Associations (SOCRATES)      │    │
│                        │ │                                │    │
│                        │ │ 02:41 🤖 Mark                   │    │
│                        │ │ "Yes, it gets worse after I    │    │
│                        │ │ eat"                           │    │
│                        │ │                                │    │
│                        │ │ ⚠️ MISSED OPPORTUNITY          │    │
│                        │ │ You didn't ask HOW LONG after  │    │
│                        │ │ eating! This is CRITICAL to    │    │
│                        │ │ distinguish gastric vs         │    │
│                        │ │ duodenal ulcer.                │    │
│                        │ │                                │    │
│                        │ │ Ideal follow-up:               │    │
│                        │ │ "How long after eating does    │    │
│                        │ │ the pain start - immediately,  │    │
│                        │ │ or a few hours later?"         │    │
│                        │ │                                │    │
│                        │ │ Dr. Amir Teaching Point:       │    │
│                        │ │ • Gastric: IMMEDIATE pain      │    │
│                        │ │ • Duodenal: 2-3 HOUR delay     │    │
│                        │ │                                │    │
│                        │ │ Impact: Lost 0.5 marks in      │    │
│                        │ │ "Differential Diagnosis"       │    │
│                        │ └────────────────────────────────┘    │
│                        │                                        │
│                        │ [Continue reading transcript...]       │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ RED FLAGS ANALYSIS                     │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ You screened for 6 out of 7 red flags │
│                        │                                        │
│                        │ ✓ Hematemesis (vomiting blood)        │
│                        │   Asked at 03:12                      │
│                        │                                        │
│                        │ ✓ Melena (black stools)               │
│                        │   Asked at 03:18                      │
│                        │                                        │
│                        │ ✓ Dysphagia (difficulty swallowing)   │
│                        │   Asked at 04:02                      │
│                        │                                        │
│                        │ ✓ Weight loss                         │
│                        │   Asked at 04:35                      │
│                        │                                        │
│                        │ ✓ Severe pain (perforation concern)   │
│                        │   Covered in pain characterization    │
│                        │                                        │
│                        │ ✓ Constitutional symptoms             │
│                        │   Asked about fever at 05:21          │
│                        │                                        │
│                        │ ✗ Odynophagia (painful swallowing)    │
│                        │   NOT ASKED                           │
│                        │                                        │
│                        │ Score Impact: -0.25 marks             │
│                        │                                        │
│                        │ 💡 TIP: Odynophagia is distinct from  │
│                        │ dysphagia and can indicate esophageal │
│                        │ involvement or complications.         │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ STRENGTHS IDENTIFIED                   │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ 💪 Excellent Rapport Building          │
│                        │    You established great rapport with │
│                        │    the patient and demonstrated       │
│                        │    empathy throughout. Perfect score  │
│                        │    in Introduction & Rapport (1/1).   │
│                        │                                        │
│                        │ 💪 Comprehensive Red Flag Screening    │
│                        │    You systematically screened for    │
│                        │    most red flags (6/7). This is      │
│                        │    above platform average (4.8/7).    │
│                        │                                        │
│                        │ 💪 Good Use of SOCRATES Framework      │
│                        │    You covered most components of     │
│                        │    SOCRATES, showing systematic       │
│                        │    approach to pain history.          │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ AREAS TO IMPROVE                       │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ 🎯 PRIORITY 1: Medication History      │
│                        │                                        │
│                        │    Score: 1/2 (50%)                   │
│                        │    Issue: You asked "Are you taking   │
│                        │    any medications?" but didn't probe │
│                        │    for OTC medications when patient   │
│                        │    initially said "no prescription    │
│                        │    drugs."                            │
│                        │                                        │
│                        │    Patient was taking:                │
│                        │    • Ibuprofen 400mg TDS (6 months)   │
│                        │    • Quickies antacids PRN            │
│                        │                                        │
│                        │    ⚠️ CRITICAL: NSAID use is THE most │
│                        │    important risk factor! You missed  │
│                        │    it until minute 5:42 when patient  │
│                        │    mentioned "taking painkillers for  │
│                        │    my back."                          │
│                        │                                        │
│                        │    💡 IMPROVEMENT STRATEGY:            │
│                        │    Always ask: "Are you taking any    │
│                        │    medications including over-the-    │
│                        │    counter drugs like painkillers,    │
│                        │    antacids, or vitamins?"            │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ 🎯 PRIORITY 2: Pain Timing            │
│                        │                                        │
│                        │    Score: Lost 0.5 marks in DDx       │
│                        │    Issue: Didn't clarify EXACT timing │
│                        │    of pain relative to meals.         │
│                        │                                        │
│                        │    What you asked:                    │
│                        │    "Does eating affect the pain?"     │
│                        │                                        │
│                        │    What you should ask:               │
│                        │    "How long after eating does the    │
│                        │    pain start - right away, or a few  │
│                        │    hours later?"                      │
│                        │                                        │
│                        │    ⭐ DR. AMIR TEACHING POINT:         │
│                        │    This is THE key to differentiating │
│                        │    gastric vs duodenal ulcer!         │
│                        │                                        │
│                        │    • Gastric: IMMEDIATE               │
│                        │    • Duodenal: 2-3 HOURS              │
│                        │                                        │
│                        │    💡 IMPROVEMENT STRATEGY:            │
│                        │    Practice with "time since eating"  │
│                        │    OSCEs: GI-PUD-002, GI-GORD-001     │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ 🎯 PRIORITY 3: Differential Diagnosis  │
│                        │                                        │
│                        │    Score: 2/3 (67%)                   │
│                        │    Issue: You identified PUD as most  │
│                        │    likely diagnosis ✓ but didn't      │
│                        │    distinguish gastric vs duodenal,   │
│                        │    and didn't mention malignancy risk │
│                        │    difference.                        │
│                        │                                        │
│                        │    What you said:                     │
│                        │    "Most likely peptic ulcer disease  │
│                        │    related to NSAID use. Need to rule │
│                        │    out GORD and gastritis."           │
│                        │                                        │
│                        │    What examiners wanted to hear:     │
│                        │    "Most likely NSAID-induced peptic  │
│                        │    ulcer. Based on timing, could be   │
│                        │    gastric or duodenal - would need   │
│                        │    endoscopy to confirm. Gastric      │
│                        │    ulcers require biopsy to exclude   │
│                        │    malignancy, whereas duodenal       │
│                        │    ulcers don't have malignant        │
│                        │    potential."                        │
│                        │                                        │
│                        │    💡 IMPROVEMENT STRATEGY:            │
│                        │    Review AMC_PEPTIC_ULCER_DISEASE_   │
│                        │    ENHANCEMENT.md Section 1           │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ YOUR PERSONALIZED ACTION PLAN          │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ Based on your performance, here's how │
│                        │ to improve:                           │
│                        │                                        │
│                        │ 📚 STUDY MATERIALS (Before next try)  │
│                        │                                        │
│                        │    1. Read: AMC_PEPTIC_ULCER_DISEASE_ │
│                        │       ENHANCEMENT.md                  │
│                        │       Focus: Sections 1 & 2           │
│                        │       Time: 20 minutes                │
│                        │                                        │
│                        │    2. Review: eTG Guidelines -        │
│                        │       Peptic Ulcer Disease            │
│                        │       Focus: Risk factors & red flags │
│                        │       Time: 10 minutes                │
│                        │                                        │
│                        │    3. Watch: Dr. Amir Video (again)   │
│                        │       Timestamp: 08:15-12:30          │
│                        │       Focus: Gastric vs duodenal      │
│                        │                                        │
│                        │ 🏋️ PRACTICE EXERCISES                  │
│                        │                                        │
│                        │    1. Repeat this OSCE (GI-PUD-001)   │
│                        │       Goal: Score ≥13/15              │
│                        │       Focus: Medication history early │
│                        │              Pain timing specificity  │
│                        │                                        │
│                        │    2. Try related OSCE:               │
│                        │       GI-PUD-002: NSAID-induced       │
│                        │       bleeding (harder difficulty)    │
│                        │                                        │
│                        │    3. Flash cards:                    │
│                        │       • SOCRATES framework             │
│                        │       • PUD red flags (7 cards)       │
│                        │       • Australian medications        │
│                        │                                        │
│                        │ 🎯 TARGET FOR NEXT ATTEMPT            │
│                        │                                        │
│                        │    Minimum Goals:                     │
│                        │    • Explore OTC meds within 2 min    │
│                        │    • Ask pain timing explicitly       │
│                        │    • Mention gastric vs duodenal      │
│                        │    • Score 13+/15                     │
│                        │                                        │
│                        │    Stretch Goals:                     │
│                        │    • Perfect SOCRATES (2/2)           │
│                        │    • All 7 red flags (2/2)            │
│                        │    • Full DDx with reasoning (3/3)    │
│                        │    • Score 14+/15 (Excellent)         │
│                        │                                        │
│                        │ ────────────────────────────────────   │
│                        │                                        │
│                        │ ═══════════════════════════════════    │
│                        │ PEER COMPARISON                        │
│                        │ ═══════════════════════════════════    │
│                        │                                        │
│                        │ 📊 How you compare (n=1,247 students) │
│                        │                                        │
│                        │ Overall Score: 11/15 (73%)            │
│                        │ Your Percentile: 48th                 │
│                        │ Platform Avg: 11.2/15 (75%)           │
│                        │                                        │
│                        │ ───────────────────────────────────    │
│                        │                                        │
│                        │ Criterion Performance vs Peers:       │
│                        │                                        │
│                        │ Introduction & Rapport                │
│                        │ You: ████████████ 100%   Avg: 90%    │
│                        │ ↑ Above average (+10%)                │
│                        │                                        │
│                        │ SOCRATES History                      │
│                        │ You: █████████░░░ 75%    Avg: 85%    │
│                        │ ↓ Below average (-10%)                │
│                        │                                        │
│                        │ Risk Factors                          │
│                        │ You: ██████░░░░░░ 50%    Avg: 60%    │
│                        │ ↓ Below average (-10%)                │
│                        │                                        │
│                        │ Red Flags                             │
│                        │ You: ██████████░░ 88%    Avg: 75%    │
│                        │ ↑ Above average (+13%)                │
│                        │                                        │
│                        │ Differential Dx                       │
│                        │ You: ████████░░░░ 67%    Avg: 60%    │
│                        │ ↑ Above average (+7%)                 │
│                        │                                        │
│                        │ Clinical Reasoning                    │
│                        │ You: █████████░░░ 75%    Avg: 70%    │
│                        │ ↑ Above average (+5%)                 │
│                        │                                        │
│                        │ Management Plan                       │
│                        │ You: █████████░░░ 75%    Avg: 72%    │
│                        │ ↑ Above average (+3%)                 │
│                        │                                        │
│                        │ Communication                         │
│                        │ You: █████████░░░ 75%    Avg: 80%    │
│                        │ ↓ Below average (-5%)                 │
│                        │                                        │
│                        │ ───────────────────────────────────    │
│                        │                                        │
│                        │ 🏆 TOP PERFORMERS (95th percentile)   │
│                        │    Common strategies:                 │
│                        │    • Ask about ALL meds in first 2min │
│                        │    • Use "How long after eating?"     │
│                        │    • Explicitly state gastric vs      │
│                        │      duodenal reasoning               │
│                        │    • Mention malignancy risk          │
│                        │                                        │
│                        │ ───────────────────────────────────    │
│                        │                                        │
│                        │ 📈 YOUR PROGRESS TREND                │
│                        │                                        │
│                        │ Attempt #1: 11/15 (73%) ← YOU ARE HERE│
│                        │                                        │
│                        │ Typical learning curve:               │
│                        │ Attempt #2: 12/15 (80%)               │
│                        │ Attempt #3: 13/15 (87%)               │
│                        │ Attempt #4: 14/15 (93%)               │
│                        │                                        │
│                        │ Students who follow action plan       │
│                        │ improve by average 2.3 marks by 3rd   │
│                        │ attempt.                              │
│                        │                                        │
└────────────────────────┴────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│ [🔁 RETRY THIS OSCE]  [📚 STUDY MATERIALS]  [🏠 DASHBOARD]     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Material-UI Components:**
- `Drawer` or `Sticky` sidebar for navigation
- `Card` with `CardHeader` for each section
- `Table` for score breakdown
- `LinearProgress` for criterion scores
- `Alert` with `severity` for feedback
- `Accordion` for transcript (expandable exchanges)
- `Chip` for tags (✓ strength, ✗ weakness, ⚠️ missed opportunity)
- `List` with checkboxes for red flags
- `Divider` between sections

**Key Features:**

1. **Granular Feedback**
   - Not just "wrong" but WHY it's wrong
   - Show what you should have said
   - Link to teaching points

2. **Actionable Improvement**
   - Specific study materials with time estimates
   - Practice exercises with clear goals
   - Measurable targets for next attempt

3. **Evidence-Based Learning**
   - Citations inline
   - Link to guideline sections
   - Academic references accessible

4. **Gamification Elements**
   - Peer comparison (percentiles)
   - Progress tracking
   - Unlock related OSCEs by scoring well

---

### 6. Mobile Responsive Adaptations

**Mobile Layout (<768px):**

**Pre-Session Card:**
```
┌────────────────────────┐
│ 🏥 GI-PUD-001          │
│ Upper Abdominal Pain   │
│                        │
│ ⭐⭐⭐ HIGH-YIELD        │
│                        │
│ 📍 Gastro • 8 min      │
│ 📊 Intermediate        │
│                        │
│ [▶️ START]  [📖 INFO]  │
└────────────────────────┘
```

**Active Session Mobile:**
```
┌──────────────────────────┐
│ ⏱️ 06:23    [⚙️] [⏹️]    │
├──────────────────────────┤
│ 🚨 RED FLAGS (Swipe up) │
│ ☐ 6/7 screened          │
├──────────────────────────┤
│                          │
│ 🤖 Mark                  │
│ "I've been having        │
│ stomach pain..."         │
│                          │
│ 👨‍⚕️ You                  │
│ "Can you tell me more?" │
│                          │
│ [Type message...]        │
│                          │
│ 💡 TIP                   │
│ Use SOCRATES for pain    │
│                          │
└──────────────────────────┘
│                          │
│ [Bottom Sheet: Pull up]  │
│ ══════════════════════   │
│ 📋 PATIENT INFO          │
│ 🚨 RED FLAGS (7)         │
│ 📊 RUBRIC                │
└──────────────────────────┘
```

**Material-UI Mobile Components:**
- `SwipeableDrawer` for bottom sheet
- `AppBar` with `Toolbar` for sticky header
- `Fab` positioned bottom-right for quick access
- `BottomNavigation` for main navigation
- `Collapse` for expandable tips

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Priority:** Get Dr. Amir content visible

1. **Update OSCE Detail API**
   - Ensure all 724 lines of GI-PUD-001 accessible via API
   - Create `/api/v1/osces/{id}/complete` endpoint
   - Return learning_objectives, key_points, red_flags, etc.

2. **Create Type Definitions**
   ```typescript
   interface DrAmirOSCE extends OSCE {
     learning_objectives: string[];
     key_points: string[];
     red_flags: RedFlag[];
     common_pitfalls: CommonPitfall[];
     australian_guidelines: AustralianGuideline[];
     clinical_pearls: string[];
     examiner_notes: ExaminerNotes;
     amc_exam_alignment: AMCAlignment;
   }
   ```

3. **Build Pre-Session Overview Page**
   - 5-tab interface (Overview, Objectives, Scenario, Learn, Stats)
   - Desktop & mobile responsive
   - All content from JSON displayed

**Deliverable:** Students can view all Dr. Amir content before starting OSCE

---

### Phase 2: During-Session Support (Week 3-4)

**Priority:** Help students during practice

1. **Clinical Context Panel**
   - Patient summary (demographics, medications, risk factors)
   - Red flags checklist (7 items, trackable)
   - Critical teaching points (gastric vs duodenal, NSAID cessation)

2. **Collapsible Marking Rubric**
   - All 8 criteria with sub-criteria
   - Teaching points highlighted
   - Mark allocation visible

3. **Contextual Tips System**
   - AI analyzes conversation
   - Shows relevant tips at right time
   - Example: "Have you asked about medications?"

**Deliverable:** Students have essential reference material during session

---

### Phase 3: Post-Session Analysis (Week 5-6)

**Priority:** Deep learning after completion

1. **Score Breakdown Component**
   - Table with 8 criteria
   - Visual progress bars
   - Color-coded (green/yellow/red)

2. **Transcript Review with Annotations**
   - Conversation replay
   - Inline feedback
   - Missed opportunities highlighted
   - Ideal responses shown

3. **Red Flag Analysis**
   - Which flags screened (6/7)
   - Which missed (odynophagia)
   - Impact on score
   - Tips for improvement

4. **Strengths & Improvement Areas**
   - Automated analysis
   - Priority ranking
   - Specific strategies

5. **Personalized Action Plan**
   - Study materials with time estimates
   - Practice exercises
   - Target goals for next attempt

**Deliverable:** Students get comprehensive feedback and improvement plan

---

### Phase 4: Advanced Features (Week 7-8)

**Priority:** Enhanced learning

1. **Evidence Integration**
   - Inline citations throughout
   - Links to eTG guidelines
   - PBS code information
   - Academic references

2. **Peer Comparison**
   - Percentile scoring
   - Criterion-by-criterion comparison
   - Top performer strategies
   - Progress trends

3. **Related Content Linking**
   - Other PUD OSCEs
   - Related MCQs
   - Study notes (AMC_PEPTIC_ULCER_DISEASE_ENHANCEMENT.md)
   - Flashcard decks

4. **Offline Support**
   - Download OSCEs for offline study
   - PWA capabilities
   - Sync when online

**Deliverable:** Complete Dr. Amir OSCE learning ecosystem

---

## Technical Integration

### API Endpoints Required

```typescript
// Get complete OSCE with all Dr. Amir content
GET /api/v1/osces/{id}/complete
Response: DrAmirOSCE

// Get session results with detailed analysis
GET /api/v1/osces/sessions/{session_id}/analysis
Response: {
  score: ScoreBreakdown,
  transcript: AnnotatedTranscript[],
  red_flags_analysis: RedFlagAnalysis,
  strengths: Strength[],
  improvements: Improvement[],
  action_plan: ActionPlan,
  peer_comparison: PeerStats
}

// Get related learning resources
GET /api/v1/osces/{id}/resources
Response: {
  study_notes: StudyNote[],
  related_osces: OSCE[],
  mcqs: MCQ[],
  guidelines: Guideline[]
}

// Track red flag screening during session
POST /api/v1/osces/sessions/{session_id}/red-flags/{flag_id}
Body: { screened: true, timestamp: "06:23" }
```

### State Management

**Use React Query for:**
- OSCE data fetching and caching
- Session state persistence
- Real-time updates during practice

**Use Context/Zustand for:**
- UI state (panel open/closed, tab selection)
- Timer state
- Red flag tracking

### Real-Time Features

**WebSocket Events:**
```typescript
// AI detects red flag screening
socket.emit('red_flag_detected', {
  flag: 'hematemesis',
  timestamp: '03:12'
});

// Contextual tip triggered
socket.emit('show_tip', {
  message: 'Consider asking about OTC medications',
  priority: 'high'
});

// Session milestone reached
socket.emit('milestone', {
  type: 'halfway',
  message: 'You\'re halfway through! Ensure you\'ve covered risk factors.'
});
```

---

## Success Metrics

### Student Learning Outcomes

**Measure:**
- Score improvement attempt-to-attempt (target: +2 marks by 3rd attempt)
- Time to pass (target: ≤3 attempts for 80% of students)
- Retention (re-test after 30 days, target: maintain 90% of score)

### Engagement Metrics

**Measure:**
- Time spent on Pre-Session Overview (target: 5+ minutes)
- Clinical Context Panel usage during session (target: 80% open panel)
- Post-Session Analysis completion rate (target: 70% read all sections)
- Action Plan execution (target: 60% complete recommended materials)

### Content Utilization

**Measure:**
- Learning objectives viewed (target: 85% before first attempt)
- Red flags checklist interaction (target: 95% use during session)
- Evidence links clicked (target: 40% click at least one guideline)
- Related resources accessed (target: 50% view related OSCEs/MCQs)

### Technical Performance

**Measure:**
- Page load time (target: <2 seconds)
- WebSocket latency (target: <100ms)
- Mobile responsiveness score (target: 100/100 Lighthouse)
- Accessibility score (target: WCAG 2.2 AA, 0 violations)

---

## Appendix: Design System Tokens

### Colors (Material-UI Theme)

```typescript
const theme = createTheme({
  palette: {
    amc: {
      highYield: '#FFD700',      // Gold for high-yield topics
      gastric: '#EF5350',        // Red for gastric ulcer
      duodenal: '#42A5F5',       // Blue for duodenal ulcer
      redFlag: '#D32F2F',        // Dark red for warnings
      pass: '#66BB6A',           // Green for passing
      fail: '#EF5350',           // Red for failing
      teaching: '#FFA726',       // Orange for Dr. Amir points
    },
    clinical: {
      nsaid: '#FF6B6B',          // Danger color for NSAID warnings
      evidence: '#4ECDC4',       // Teal for evidence links
      guideline: '#2E86AB',      // Blue for guidelines
    }
  }
});
```

### Typography

```typescript
typography: {
  h1: { fontSize: '2.5rem', fontWeight: 700 },      // Page titles
  h2: { fontSize: '2rem', fontWeight: 600 },        // Section headers
  h3: { fontSize: '1.5rem', fontWeight: 600 },      // Subsections
  body1: { fontSize: '1rem', lineHeight: 1.6 },     // Body text
  body2: { fontSize: '0.875rem', lineHeight: 1.5 }, // Secondary text
  caption: { fontSize: '0.75rem' },                 // Labels, metadata
  clinicalNote: {                                   // Custom variant
    fontSize: '0.9rem',
    fontStyle: 'italic',
    color: 'text.secondary'
  }
}
```

### Spacing Scale

```typescript
spacing: {
  xs: '4px',
  sm: '8px',
  md: '16px',
  lg: '24px',
  xl: '32px',
  xxl: '48px',
}
```

---

## Conclusion

This UI/UX plan transforms the 724-line Dr. Amir OSCE (GI-PUD-001) into a comprehensive, accessible, and pedagogically sound learning experience.

**Key Achievements:**
✅ Progressive disclosure prevents overwhelm
✅ All content utilized (no waste)
✅ Mobile-first responsive design
✅ Evidence-based learning emphasized
✅ Actionable feedback for improvement
✅ AMC exam alignment clear throughout

**Next Steps:**
1. Review with clinical educators for pedagogical validation
2. Review with UI/UX designer for visual design refinement
3. Create PRDs for each implementation phase
4. Begin Phase 1 development (Pre-Session Overview)

---

**Document Version:** 1.0
**Last Updated:** 2026-05-27
**Author:** Claude (PM Agent)
**Status:** ✅ READY FOR IMPLEMENTATION
**Estimated Development Time:** 8 weeks (4 phases × 2 weeks)
**Priority:** HIGH - Unlocks full value of Dr. Amir video transcript conversion
