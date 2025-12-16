# ICRP AMC Clinical OSCE Flashcards

**Status:** ✅ Phase 1.1 Complete
**Total Cards:** 750 unique flashcards
**Last Updated:** 2025-12-16

---

## Quick Links

- 📊 [Verification Report](./PHASE_1_1_VERIFICATION_REPORT.md) - Detailed extraction report
- 📥 [Anki Import Instructions](./ANKI_IMPORT_INSTRUCTIONS.md) - How to import into Anki
- 💾 [Flashcard Data](./flashcard_data.json) - Raw JSON data (750 cards)
- 📝 [Anki Import File](./anki_import.txt) - Tab-separated format for Anki

---

## Overview

This flashcard collection contains **750 high-quality flashcards** extracted from the ICRP OSCE Preparation materials, specifically designed for AMC Clinical exam preparation in the Australian medical context.

### Categories

| Category | Cards | Description |
|----------|-------|-------------|
| **Differentials** | 138 | Differential diagnoses by presentation |
| **IMG Mistakes** | 135 | Common mistakes IMGs make in OSCE |
| **Physical Exam** | 137 | IPPA sequences and examination techniques |
| **Red Flags** | 128 | Emergency presentations and critical features |
| **Australian Context** | 128 | eTG, PBS, Medicare, Australian guidelines |
| **Communication** | 84 | SPIKES, empathy phrases, patient communication |
| **TOTAL** | **750** | |

### Difficulty Distribution

- **Easy:** 123 cards (16.4%) - Terminology, basic facts
- **Medium:** 457 cards (60.9%) - Clinical reasoning, differentials
- **Hard:** 170 cards (22.7%) - Red flags, complex scenarios

---

## Features

✅ **Australian Spelling & Context**
- Paediatric (not pediatric)
- Anaemia (not anemia)
- eTG 2024 guidelines
- PBS-listed medications
- Medicare-funded investigations

✅ **Quality Assured**
- No duplicate content (100 duplicates removed)
- Source attribution for all cards
- Clinically accurate (based on eTG 2024)
- Ready for immediate use

✅ **Comprehensive Coverage**
- Medicine (Cardiology, Respiratory, GI, Neurology, Endocrinology)
- Surgery (Acute abdomen, Trauma, Pre/post-op)
- Paediatrics (Common presentations, Development, Red flags)
- Obstetrics & Gynaecology (Pregnancy, Gynaecological complaints)
- Psychiatry (MSE, Risk assessment, Capacity)
- Ethics & Communication (Breaking bad news, Consent, Cultural safety)

---

## Getting Started

### 1. Import into Anki (Recommended)

```bash
# Open Anki Desktop
File → Import → Select: anki_import.txt

# Configure:
- Type: Basic
- Deck: ICRP_AMC_Clinical
- Fields separated by: Tab
- Allow HTML: Yes
```

See [ANKI_IMPORT_INSTRUCTIONS.md](./ANKI_IMPORT_INSTRUCTIONS.md) for detailed steps.

### 2. Study Schedule

**Recommended approach:**
- Start: 30-40 new cards/day
- Review: All due cards daily
- Time: 45-75 minutes/day
- Duration: 8-12 weeks to complete all 750 cards

### 3. Focus Areas by Week

**Weeks 1-4:** Red Flags + Differentials (priority for AMC Clinical)
**Weeks 5-8:** Physical Exam + IMG Mistakes
**Weeks 9-12:** Communication + Australian Context

---

## File Structure

```
Flashcards/
├── README.md (this file)
├── flashcard_data.json (750 cards in JSON format)
├── anki_import.txt (Anki-compatible import file)
├── PHASE_1_1_VERIFICATION_REPORT.md (detailed report)
├── ANKI_IMPORT_INSTRUCTIONS.md (import guide)
├── extract_flashcards.py (original extraction script)
└── extract_phase_1_1.py (Phase 1.1 extraction script)
```

---

## Sample Cards

### Red Flag
```
Front: 🚨 RED FLAG: Ectopic pregnancy
Back:  Amenorrhoea + abdominal pain + vaginal bleeding → βhCG + urgent USS.
       Haemodynamic instability = ruptured ectopic → IMMEDIATE surgical referral
```

### Differential
```
Front: Differential: Acute Coronary Syndrome (ACS)
Back:  Central crushing chest pain, radiating to jaw/arm, diaphoresis, nausea,
       dyspnoea. Risk factors: age >45, smoking, DM, HTN, family history
```

### IMG Mistake
```
Front: IMG Mistake: Breaking bad news too quickly
Back:  Correct approach: Use SPIKES framework, check patient's understanding first,
       deliver news in small chunks, pause for questions, provide support
```

### Physical Exam
```
Front: Physical Exam (Inspection) - Cardiovascular/Respiratory:
Back:  Check for: central cyanosis (tongue/lips), peripheral cyanosis (fingers),
       accessory muscle use, respiratory rate, chest wall deformities, scars
```

---

## Source Materials

All flashcards extracted from:
- ICRP_OSCE_Preparation/ (48 HTML modules)
- Covers all AMC Clinical domains
- Based on Australian guidelines (eTG 2024, AMH)
- Aligned with AMC Clinical exam format (8-minute stations)

---

## Statistics

**Extraction Phase:** 1.1
**Date Completed:** 2025-12-16
**Starting Count:** 341 cards
**New Cards Extracted:** 509 cards
**Duplicates Removed:** 100 cards
**Final Count:** 750 unique cards

**Quality Metrics:**
- 0 duplicate IDs
- 0 duplicate content
- 0 US spellings
- 0 missing sources
- 750 properly formatted cards

---

## Next Steps

### Immediate (Start Today)
1. Import flashcards into Anki
2. Create deck structure (see ANKI_IMPORT_INSTRUCTIONS.md)
3. Start with 30 new cards/day
4. Focus on Red Flags + Differentials first

### Short Term (Weeks 1-4)
1. Complete Red Flags deck (128 cards)
2. Complete Differentials deck (138 cards)
3. Begin IMG Mistakes deck (135 cards)
4. Maintain daily reviews

### Medium Term (Weeks 5-12)
1. Complete all 750 cards
2. Focus on weak areas (use Anki statistics)
3. Create additional custom cards if needed
4. Practice OSCE stations alongside flashcard study

---

## Support & Questions

For issues or questions:
1. Check [ANKI_IMPORT_INSTRUCTIONS.md](./ANKI_IMPORT_INSTRUCTIONS.md)
2. Review [PHASE_1_1_VERIFICATION_REPORT.md](./PHASE_1_1_VERIFICATION_REPORT.md)
3. Consult Anki documentation: https://docs.ankiweb.net/

---

## Version History

**v1.1** (2025-12-16) - Phase 1.1 Complete
- Added 409 new cards (341 → 750 total)
- All categories balanced
- Removed 100 duplicates
- Fixed US spellings
- Comprehensive verification

**v1.0** (2025-12-16) - Initial extraction
- 341 cards extracted
- Basic category coverage

---

**Created:** 2025-12-16
**Status:** ✅ Ready for use
**Target:** AMC Clinical OSCE preparation
