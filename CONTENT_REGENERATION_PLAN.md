# Content Regeneration Plan

**Date:** 2026-03-28
**Status:** CRITICAL - 98.6% of OSCEs and Study Cards are placeholders
**Scope:** 345 items need full regeneration

---

## Current Status

### Placeholder Detection Results

| Content Type | Total Files | Items | Placeholders | Rate |
|--------------|-------------|-------|--------------|------|
| **OSCEs** | 6 files | 210 | 205 | 97.6% |
| **Study Cards** | 5 files | 140 | 140 | 100% |
| **TOTAL** | 11 files | 350 | 345 | 98.6% |

**Only 1 file is OK:** `data/osces/psychiatry_week1_osces.json` (5 OSCEs)

### Breakdown by File

**OSCEs (255 items, 205 placeholders):**
- ❌ cardiology_50_osces.json: 50/50 (100%)
- ❌ missing_psychiatry_13_osces.json: 13/13 (100%)
- ❌ missing_topics_comprehensive_osces.json: 52/52 (100%)
- ❌ psychiatry_40_osces.json: 40/40 (100%)
- ✅ psychiatry_week1_osces.json: 0/5 (0%) ← GOOD
- ❌ respiratory_50_osces.json: 50/50 (100%)

**Study Cards (140 items, 140 placeholders):**
- ❌ cardiology_study_cards.json: 25/25 (100%)
- ❌ missing_psychiatry_13_cards.json: 13/13 (100%)
- ❌ missing_topics_comprehensive_cards.json: 52/52 (100%)
- ❌ psychiatry_study_cards.json: 25/25 (100%)
- ❌ respiratory_study_cards.json: 25/25 (100%)

---

## Regeneration Strategy

### Phase 1: Immediate Quick Wins (Priority Files)

**Target:** High-value, high-frequency specialties
**Estimated Time:** 8-10 hours
**Items:** 155

1. **Psychiatry OSCEs** (40 items) - Week 1-2 of AMC preparation
   - File: `psychiatry_40_osces.json`
   - Priority: 🔴 CRITICAL (Week 1 topic)
   - Use: `psychiatry_week1_osces.json` as template (5 good OSCEs)
   - Agent: mental-health-crisis-expert + history-taking-expert

2. **Cardiology OSCEs** (50 items) - Week 3 of AMC preparation
   - File: `cardiology_50_osces.json`
   - Priority: 🔴 CRITICAL (very high AMC frequency)
   - Topics: STEMI, NSTEMI, heart failure, arrhythmias
   - Agent: medication-management-expert + physical-examination-expert

3. **Respiratory OSCEs** (50 items) - Week 3 of AMC preparation
   - File: `respiratory_50_osces.json`
   - Priority: 🔴 CRITICAL (very high AMC frequency)
   - Topics: Asthma, COPD, pneumonia, PE
   - Agent: physical-examination-expert

4. **Psychiatry Study Cards** (25 items)
   - File: `psychiatry_study_cards.json`
   - Priority: 🟡 HIGH
   - Use fixed psychiatry MCQs as source material
   - Agent: mental-health-crisis-expert

5. **Cardiology Study Cards** (25 items)
   - File: `cardiology_study_cards.json`
   - Priority: 🟡 HIGH
   - Topics: ECG interpretation, ACS management, heart failure
   - Agent: medication-management-expert

6. **Respiratory Study Cards** (25 items)
   - File: `respiratory_study_cards.json`
   - Priority: 🟡 HIGH
   - Topics: Spirometry, asthma management, COPD
   - Agent: medication-management-expert

### Phase 2: Missing Topics (Lower Priority)

**Target:** Comprehensive coverage (endocrine, dermatology, etc.)
**Estimated Time:** 6-8 hours
**Items:** 65

1. **Missing Psychiatry OSCEs** (13 items)
   - File: `missing_psychiatry_13_osces.json`
   - Topics: Loneliness, grief, post-partum blues
   - Agent: mental-health-crisis-expert

2. **Missing Topics OSCEs** (52 items)
   - File: `missing_topics_comprehensive_osces.json`
   - Topics: Endocrine, dermatology, ENT, ophthalmology, rheumatology
   - Agent: Specialty-specific agents

3. **Missing Topics Study Cards** (52 items + 13 items)
   - Files: `missing_topics_comprehensive_cards.json`, `missing_psychiatry_13_cards.json`
   - Same topics as OSCEs

---

## Technical Approach

### Option A: Manual Regeneration with Claude Code (Recommended)

**Process:**
1. Use `psychiatry_week1_osces.json` as gold standard template
2. Create generation script that:
   - Reads topic from placeholder OSCE
   - Calls Claude API with comprehensive prompt (includes Constraint 15 for psychiatry)
   - Generates complete clinical case
   - Validates no placeholders
   - Saves to new file

**Advantages:**
- Full control over quality
- Can iterate if generation fails
- Can use constraints (Constraint 15 for psychiatry)

**Disadvantages:**
- Time-intensive (10-15 hours for 345 items)

### Option B: Ralph Loop Automation (Future)

**Process:**
1. Create T-RALPH PRDs for OSCE and Study Card generation
2. Ralph executes PRDs autonomously
3. Validation runs automatically

**Advantages:**
- Scalable to thousands of items
- Consistent quality (PRD-driven)
- Automated validation

**Disadvantages:**
- Requires PRD creation first (4-6 hours)
- Ralph execution time (8-10 hours)
- Total: 12-16 hours

### Recommended: Hybrid Approach

**Phase 1 (Immediate):** Manual regeneration for top 3 files (140 items, 6-8 hours)
- psychiatry_40_osces.json
- cardiology_50_osces.json
- respiratory_50_osces.json

**Phase 2 (Next week):** Ralph PRDs for remaining items (205 items)
- Create comprehensive PRDs
- Ralph executes autonomously

---

## OSCE Generation Requirements

### Mandatory Content (From Constraint 15 + Analysis)

**1. Patient Demographics**
- Age, gender, occupation
- Presenting complaint (specific, not "a patient presents with...")
- Timeline (duration of symptoms)

**2. Complete History (9 Steps)**
- Presenting complaint
- History of presenting complaint (SOCRATES for pain)
- Past medical history
- Medications (specific, not "per guidelines")
- Allergies
- Family history
- Social history
- Systems review
- Ideas, Concerns, Expectations (ICE)

**3. Mental Status Examination (if psychiatry)**
- 8 domains: Appearance, Behavior, Speech, Mood, Affect, Thought form/content, Perceptions, Cognition, Insight/Judgment

**4. Physical Examination**
- Systematic approach (inspection → palpation → percussion → auscultation)
- Specific findings (not "examination findings for...")
- Vital signs (realistic, not template "120/80")

**5. Expected Answers**
- **Assessment:** Specific clinical findings (not "systematic assessment findings for...")
- **Diagnosis:** Primary + differential (not "primary diagnosis: X")
- **Management:**
  - Specific medications with doses (e.g., "Aspirin 300mg PO stat, Ticagrelor 180mg PO stat")
  - PBS codes (e.g., "PBS 8721K")
  - Monitoring requirements
  - Safety netting

**6. References**
- **Content field MUST be populated** (not empty "")
- RAG confidence > 0.65
- Australian sources (RANZCP, eTG, MBS)

**7. Psychiatry-Specific (From Constraint 15)**
- **SAFE-T protocol:** Specific plan, Access, Feelings, Earlier attempts, Threat
- **Mental Health Act criteria** (if high risk): 4 criteria for involuntary admission
- **Australian crisis contacts:** Lifeline 13 11 14, Beyond Blue 1300 224 636
- **Cultural safety:** Aboriginal/TSI, LGBTQIA+, CALD considerations

### Quality Gates

**Pre-Generation:**
- [ ] Placeholder detection script passes
- [ ] Topic-specific template loaded
- [ ] Constraint 15 loaded (if psychiatry)

**Post-Generation:**
- [ ] No generic phrases ("A patient presents for...", "According to Australian guidelines...")
- [ ] All reference content fields populated
- [ ] Medications have specific doses + PBS codes
- [ ] SAFE-T present (if psychiatry)
- [ ] Length > 1000 characters for expected answers

---

## Study Card Generation Requirements

### Mandatory Content

**1. Front (Question)**
- Specific clinical scenario (not "What are the key points about...")
- Or: Specific fact question (e.g., "What is the first-line treatment for moderate depression in Australia?")

**2. Back (Answer)**
- Specific key facts (not "Key points for X:")
- Clinical pearl with Australian context
- Example: "SSRIs are first-line. Start with sertraline 50mg daily or escitalopram 10mg daily (PBS-listed). Monitor for suicidality in first 2 weeks."

**3. References**
- Content field populated
- RAG confidence > 0.65
- Australian sources

**4. Tags**
- Specialty, topic, subtopic
- Difficulty level

### Quality Gates

**Post-Generation:**
- [ ] No generic phrases ("Key points for...", "Definition and clinical significance of...")
- [ ] Back has ≥3 specific facts
- [ ] Clinical pearl is Australian-specific
- [ ] All reference content populated

---

## Execution Timeline

### Week 1 (This Week)

**Monday-Tuesday:** Psychiatry OSCEs (40 items, 4-5 hours)
- Create generation script
- Use Constraint 15 + psychiatry_week1_osces.json as templates
- Generate 40 psychiatry OSCEs
- Validate with placeholder detection script

**Wednesday-Thursday:** Cardiology OSCEs (50 items, 4-5 hours)
- Generate 50 cardiology OSCEs
- Focus: STEMI/NSTEMI management, ECG interpretation

**Friday:** Respiratory OSCEs (50 items, 4-5 hours)
- Generate 50 respiratory OSCEs
- Focus: Asthma/COPD management, spirometry

**Total Week 1:** 140 OSCEs regenerated (66% of placeholder OSCEs)

### Week 2

**Monday:** Study Cards (75 items, 3-4 hours)
- Psychiatry: 25 cards
- Cardiology: 25 cards
- Respiratory: 25 cards

**Tuesday-Thursday:** Missing Topics (65 items, 6-8 hours)
- Missing psychiatry OSCEs: 13
- Missing topics OSCEs: 52

**Friday:** Missing Topics Study Cards (65 items, 3-4 hours)

**Total Week 2:** 205 items regenerated (remaining 34%)

---

## Success Criteria

### Immediate (End of Week 1)
- ✅ 140 OSCEs regenerated (3 main specialties)
- ✅ 0% placeholder rate on regenerated files
- ✅ Evaluation scores > 7.0/10 (vs 0.36 currently)

### Short-term (End of Week 2)
- ✅ All 345 placeholder items regenerated
- ✅ 100% content completeness
- ✅ Ready for AMC practice use

### Long-term (Week 3+)
- ✅ Create Constraints 16-17 to prevent future placeholders
- ✅ Integrate with generation pipeline
- ✅ Add to automated testing (placeholder detection in CI/CD)

---

## Resources Required

**Scripts:**
- ✅ `scripts/detect_placeholder_content.py` (created)
- ⏳ `scripts/regenerate_osces.py` (to create)
- ⏳ `scripts/regenerate_study_cards.py` (to create)

**Templates:**
- ✅ `data/osces/psychiatry_week1_osces.json` (5 good OSCEs)
- ✅ `constraints/15-psychiatry-mcq-requirements.md` (for psychiatry)
- ⏳ Gold standard MCQs (for study card content)

**API Access:**
- Claude API (claude-sonnet-4-20250514)
- Rate limit: 90 requests/min
- Estimated API calls: ~1,000-1,500 (3-5 calls per item)

---

**Status:** Plan complete, ready for execution
**Last Updated:** 2026-03-28
