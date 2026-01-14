# AMC Frequency Indicator Template
## How to Add Frequency Tags to All OSCE Notes

**Version:** 1.0
**Date:** 2025-12-25
**Purpose:** Standardized template for adding AMC frequency indicators to all OSCE notes

---

## 📋 Template Format

### **For Markdown (.md) Files**

```markdown
# [Module Title]
## AMC Clinical / ICRP NSW Young Hospital Preparation

---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[⭐⭐⭐ HIGH-YIELD]** - Appears in 80%+ of AMC Clinical exams
**Study Priority:** CRITICAL - Practice 10-15 times before exam
**Why High-Yield:** [Brief explanation - e.g., "Chest pain is THE most common presenting complaint in AMC Clinical exams, focusing on safe ACS exclusion"]

---

**Purpose**: [Original purpose text]
**Target Time**: 8 minutes per station
**Format**: Australian teaching hospital standard
**Created**: [Date]
**Last Updated**: [Date with frequency tag addition]

---

[Rest of the document continues as normal...]
```

### **For HTML Files**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[Module Title] - AMC OSCE Preparation</title>
    <style>
        /* Existing styles */

        /* NEW: Frequency indicator banner styles */
        .frequency-banner {
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            border-left: 6px solid;
            font-weight: bold;
        }

        .frequency-high-yield {
            background-color: #ffe6e6;
            border-left-color: #d32f2f;
            color: #b71c1c;
        }

        .frequency-medium-yield {
            background-color: #fff9e6;
            border-left-color: #f57c00;
            color: #e65100;
        }

        .frequency-low-yield {
            background-color: #e8f5e9;
            border-left-color: #388e3c;
            color: #1b5e20;
        }

        .frequency-stars {
            font-size: 1.3em;
            margin-right: 10px;
        }

        .study-priority {
            display: block;
            margin-top: 10px;
            font-size: 0.9em;
            font-weight: normal;
        }

        .why-high-yield {
            display: block;
            margin-top: 8px;
            font-size: 0.85em;
            font-weight: normal;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>[Module Title]</h1>
    <h2>AMC Clinical / ICRP NSW Young Hospital Preparation</h2>

    <hr>

    <!-- NEW: Frequency indicator banner -->
    <div class="frequency-banner frequency-high-yield">
        <span class="frequency-stars">⭐⭐⭐</span>
        <span>HIGH-YIELD - Appears in 80%+ of AMC Clinical exams</span>
        <span class="study-priority">📚 Study Priority: CRITICAL - Practice 10-15 times before exam</span>
        <span class="why-high-yield">💡 Why High-Yield: [Brief explanation specific to this topic]</span>
    </div>

    <hr>

    <p><strong>Purpose:</strong> [Original purpose text]</p>
    <p><strong>Target Time:</strong> 8 minutes per station</p>
    <p><strong>Format:</strong> Australian teaching hospital standard</p>
    <p><strong>Created:</strong> [Date]</p>
    <p><strong>Last Updated:</strong> [Date with frequency tag addition]</p>

    <hr>

    <!-- Rest of the document continues as normal -->
</body>
</html>
```

---

## 🎨 Visual Examples

### **Example 1: High-Yield Topic (⭐⭐⭐)**
**Topic:** Chest Pain History Taking

```markdown
---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[⭐⭐⭐ HIGH-YIELD]** - Appears in 80%+ of AMC Clinical exams
**Study Priority:** CRITICAL - Practice 10-15 times before exam
**Why High-Yield:** Chest pain is THE most commonly tested presenting complaint in AMC Clinical exams. Examiners assess your ability to safely exclude ACS and PE while demonstrating systematic history-taking. This scenario appears in approximately 4 out of 5 candidate reports.

---
```

**Color Scheme (HTML):** 🔴 Red banner with dark red text
**Practice Recommendation:** 10-15 full practice runs
**Time Allocation:** 70% of your study time should be on ⭐⭐⭐ topics

---

### **Example 2: Medium-Yield Topic (⭐⭐)**
**Topic:** Rheumatology Joint Pain Assessment

```markdown
---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[⭐⭐ MEDIUM-YIELD]** - Appears in 30-60% of AMC Clinical exams
**Study Priority:** IMPORTANT - Practice 5-8 times before exam
**Why Medium-Yield:** Joint pain/arthritis scenarios test your systematic approach to musculoskeletal complaints. While not as common as chest pain or SOB, they appear regularly enough to warrant solid preparation. Approximately 2-3 out of 5 candidates encounter this.

---
```

**Color Scheme (HTML):** 🟡 Yellow/orange banner with dark orange text
**Practice Recommendation:** 5-8 full practice runs
**Time Allocation:** 25% of your study time should be on ⭐⭐ topics

---

### **Example 3: Low-Yield Topic (⭐)**
**Topic:** Rare Endocrine Disorder (Addison's Crisis)

```markdown
---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[⭐ LOW-YIELD]** - Appears in <30% of AMC Clinical exams
**Study Priority:** OPTIONAL - Practice 2-3 times if time permits
**Why Low-Yield:** Rare endocrine emergencies like Addison's crisis are uncommon OSCE scenarios. Focus on mastering high-yield topics first. Only review this if you've completed all ⭐⭐⭐ and ⭐⭐ content.

---
```

**Color Scheme (HTML):** 🟢 Green banner with dark green text
**Practice Recommendation:** 2-3 practice runs IF time permits
**Time Allocation:** 5% of your study time (only after mastering ⭐⭐⭐ and ⭐⭐)

---

## 📊 Classification Decision Tree

Use this flowchart to determine frequency classification:

```
START: Is this topic a common presenting complaint or communication skill?
│
├─ YES → Does it appear in >60% of candidate reports/exam resources?
│         │
│         ├─ YES → ⭐⭐⭐ HIGH-YIELD
│         │
│         └─ NO → Does it appear in 30-60% of resources?
│                   │
│                   ├─ YES → ⭐⭐ MEDIUM-YIELD
│                   │
│                   └─ NO → ⭐ LOW-YIELD
│
└─ NO → Is it a life-threatening emergency or ethical scenario?
          │
          ├─ YES → ⭐⭐⭐ HIGH-YIELD (safety priority)
          │
          └─ NO → Is it specialty-specific or procedural?
                    │
                    ├─ Common specialty (Derm, Rheum) → ⭐⭐ MEDIUM-YIELD
                    │
                    └─ Rare specialty/procedure → ⭐ LOW-YIELD
```

---

## 🎯 Topic-by-Topic Frequency Assignments

### **Medicine (⭐⭐⭐ HIGH-YIELD Topics)**
1. ✅ Chest Pain History → ⭐⭐⭐
2. ✅ Shortness of Breath History → ⭐⭐⭐
3. ✅ Abdominal Pain History (all 9 regions) → ⭐⭐⭐
4. ✅ Headache History → ⭐⭐⭐
5. ✅ Cardiovascular Examination → ⭐⭐⭐
6. ✅ Respiratory Examination → ⭐⭐⭐
7. ✅ Abdominal Examination → ⭐⭐⭐
8. ✅ Neurological Examination → ⭐⭐⭐
9. ✅ Diabetes Management → ⭐⭐⭐
10. ✅ Stroke/TIA Assessment → ⭐⭐⭐
11. ✅ Syncope/Dizziness → ⭐⭐⭐
12. ✅ Anaphylaxis Management → ⭐⭐⭐
13. ✅ Seizure Management → ⭐⭐⭐
14. ✅ ECG Interpretation → ⭐⭐⭐
15. ✅ GI Bleeding → ⭐⭐ (downgrade to medium)

### **Medicine (⭐⭐ MEDIUM-YIELD Topics)**
1. ✅ GI Bleeding Differentials → ⭐⭐
2. ✅ Weakness/Limb Examination → ⭐⭐
3. ✅ ENT Physical Examination → ⭐⭐
4. ✅ Peripheral Vascular Examination → ⭐⭐
5. ✅ Musculoskeletal Examination → ⭐⭐
6. ✅ Thyroid Examination → ⭐⭐
7. ✅ Lymph Node Examination → ⭐⭐

### **Surgery (⭐⭐⭐ HIGH-YIELD Topics)**
1. ✅ Acute Abdomen History → ⭐⭐⭐
2. ✅ Acute Abdomen Physical Exam → ⭐⭐⭐
3. ✅ Trauma Assessment (ATLS) → ⭐⭐⭐

### **Surgery (⭐⭐ MEDIUM-YIELD Topics)**
1. ✅ Lumps & Hernias History/Exam → ⭐⭐
2. ✅ Pre/Post-Operative Assessment → ⭐⭐

### **Obstetrics & Gynaecology (⭐⭐⭐ HIGH-YIELD Topics)**
1. ✅ Obstetric History → ⭐⭐⭐
2. ✅ Gynaecological History → ⭐⭐⭐
3. ✅ First Trimester Bleeding → ⭐⭐⭐
4. ✅ Abnormal Vaginal Bleeding → ⭐⭐⭐
5. ✅ Contraception Counselling → ⭐⭐⭐

### **Obstetrics & Gynaecology (⭐⭐ MEDIUM-YIELD Topics)**
1. ✅ Obstetric Examination → ⭐⭐
2. ✅ Gynaecological Examination → ⭐⭐

### **Paediatrics (⭐⭐⭐ HIGH-YIELD Topics)**
1. ✅ Paediatric History (Fever, Rash) → ⭐⭐⭐
2. ✅ Common Paediatric Presentations → ⭐⭐⭐
3. ✅ Parent Communication → ⭐⭐⭐

### **Paediatrics (⭐⭐ MEDIUM-YIELD Topics)**
1. ✅ Paediatric Physical Examination → ⭐⭐
2. ✅ Developmental Assessment → ⭐⭐

### **Psychiatry (⭐⭐⭐ HIGH-YIELD Topics)**
1. ✅ Psychiatric History → ⭐⭐⭐
2. ✅ Mental State Examination → ⭐⭐⭐
3. ✅ Risk Assessment (Suicide/Violence) → ⭐⭐⭐
4. ✅ Common Psychiatric Presentations → ⭐⭐⭐
5. ✅ Capacity Assessment → ⭐⭐⭐

### **Ethics & Communication (⭐⭐⭐ HIGHEST-YIELD Topics)**
1. ✅ Breaking Bad News (ALL scenarios) → ⭐⭐⭐
2. ✅ Communication Skills Role-Play → ⭐⭐⭐
3. ✅ Emotional Reactions Handling → ⭐⭐⭐
4. ✅ Cultural Variations (Australian) → ⭐⭐⭐
5. ✅ Informed Consent → ⭐⭐⭐
6. ✅ Difficult Conversations → ⭐⭐⭐

### **Mock OSCE Stations (Mixed Frequencies)**
1. ✅ Chest Pain Mock → ⭐⭐⭐
2. ✅ Shortness of Breath Mock → ⭐⭐⭐
3. ✅ Breaking Bad News Mocks (ALL) → ⭐⭐⭐
4. ✅ Dizziness/Syncope Mock → ⭐⭐⭐
5. ✅ Acute Confusion/Delirium → ⭐⭐⭐
6. ✅ Diabetes Mock → ⭐⭐⭐
7. ✅ RIF Pain/Appendicitis Mock → ⭐⭐⭐
8. ✅ First Trimester Bleeding Mock → ⭐⭐⭐
9. ✅ Elderly Falls Assessment → ⭐⭐⭐
10. ✅ Groin Lump/Hernia Mock → ⭐⭐
11. ✅ Abnormal Vaginal Bleeding Mock → ⭐⭐⭐
12. ✅ Medication Reconciliation → ⭐⭐

---

## ✅ Implementation Checklist

### **For Each Existing Note (101 files):**

- [ ] Determine frequency classification using decision tree
- [ ] Add frequency banner immediately after title (before Purpose section)
- [ ] Include:
  - [ ] Star rating (⭐⭐⭐ / ⭐⭐ / ⭐)
  - [ ] Appearance percentage (80%+ / 30-60% / <30%)
  - [ ] Study priority (CRITICAL / IMPORTANT / OPTIONAL)
  - [ ] Practice recommendation (10-15 / 5-8 / 2-3 times)
  - [ ] "Why High/Medium/Low-Yield" explanation (2-3 sentences)
- [ ] Update "Last Updated" field with frequency tag date
- [ ] Apply visual styling:
  - [ ] Markdown: Use emoji icons (🔴 / 🟡 / 🟢)
  - [ ] HTML: Apply CSS classes (.frequency-high-yield / .frequency-medium-yield / .frequency-low-yield)
- [ ] Verify banner renders correctly
- [ ] Cross-reference with AMC_FREQUENCY_GUIDE.md for consistency

---

## 📚 Quick Reference: Frequency Criteria

| Rating | Appearance Rate | Study Priority | Practice Times | Time Allocation |
|--------|----------------|----------------|----------------|-----------------|
| ⭐⭐⭐ HIGH-YIELD | 60-80%+ | CRITICAL | 10-15x | 70% |
| ⭐⭐ MEDIUM-YIELD | 30-60% | IMPORTANT | 5-8x | 25% |
| ⭐ LOW-YIELD | <30% | OPTIONAL | 2-3x | 5% |

---

## 🎯 Quality Assurance Checks

After adding frequency tags to all notes:

1. **Consistency Check:** All notes in the same category should have matching frequency
   - Example: All "Breaking Bad News" scenarios → ⭐⭐⭐

2. **Visual Check (HTML):** Banners render with correct colors
   - ⭐⭐⭐ = Red background
   - ⭐⭐ = Yellow/orange background
   - ⭐ = Green background

3. **Content Check:** "Why High-Yield" explanations are specific and evidence-based

4. **Cross-Reference Check:** All frequency assignments match AMC_FREQUENCY_GUIDE.md classifications

5. **User Experience Check:** Frequency indicator is the FIRST thing students see after title

---

## 📝 Example: Full Implementation

### **Before (Original Note)**
```markdown
# Medicine OSCE Master Notes - Cardiovascular & Respiratory
## AMC Clinical / ICRP NSW Young Hospital Preparation

**Purpose**: AMC Clinical-style OSCE notes for medicine history-taking stations
**Target Time**: 8 minutes per station
**Format**: Australian teaching hospital standard
**Created**: December 14, 2025

---

## CHEST PAIN
...
```

### **After (With Frequency Indicator)**
```markdown
# Medicine OSCE Master Notes - Cardiovascular & Respiratory
## AMC Clinical / ICRP NSW Young Hospital Preparation

---

## 🎯 AMC EXAM FREQUENCY INDICATOR

**[⭐⭐⭐ HIGH-YIELD]** - Appears in 80%+ of AMC Clinical exams
**Study Priority:** CRITICAL - Practice 10-15 times before exam
**Why High-Yield:** Chest pain and shortness of breath are THE most frequently tested presenting complaints in AMC Clinical exams. This station assesses your ability to safely exclude life-threatening conditions (ACS, PE) while demonstrating systematic SOCRATES framework. Appears in approximately 4 out of 5 candidate reports and all major prep courses identify this as priority #1.

---

**Purpose**: AMC Clinical-style OSCE notes for medicine history-taking stations
**Target Time**: 8 minutes per station
**Format**: Australian teaching hospital standard
**Created**: December 14, 2025
**Last Updated**: December 25, 2025 (AMC Frequency Indicator added)

---

## CHEST PAIN
...
```

---

## 🚀 Batch Implementation Strategy

### **Week 1: High-Yield Topics First (35 files)**
- Medicine high-yield (15 files)
- Surgery high-yield (3 files)
- ObGyn high-yield (5 files)
- Paediatrics high-yield (3 files)
- Psychiatry high-yield (5 files)
- Ethics/Communication ALL (6 files - all high-yield)

### **Week 2: Medium & Low-Yield Topics (66 remaining files)**
- Medicine medium-yield (7 files)
- Surgery medium-yield (2 files)
- ObGyn medium-yield (2 files)
- Paediatrics medium-yield (2 files)
- All Mock OSCE stations (13 files - mixed frequencies)
- Cheat sheets (4 files)
- Master indexes (2 files)

---

**Template Status:** ✅ READY FOR IMPLEMENTATION
**Next Step:** Begin retroactive tagging of all 101 existing notes
**Estimated Time:** 2-3 days for all files (15-20 minutes per file)

---

*This template complements the AMC_FREQUENCY_GUIDE.md and follows the Structured OSCE Methodology (differential-driven pattern) used throughout this OSCE preparation system.*
