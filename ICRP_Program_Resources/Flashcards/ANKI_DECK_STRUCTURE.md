# ICRP AMC Clinical Anki Deck Structure

**Created:** December 16, 2025
**Version:** 1.0
**Deck File:** ICRP_AMC_Clinical.apkg
**Total Cards:** 750

---

## Purpose

This document describes the structure, organization, and usage of the ICRP AMC Clinical Anki deck created for OSCE preparation. The deck is specifically designed for Australian medical context (AMC Clinical exam, ICRP NSW preparation).

---

## Deck Hierarchy

The deck uses a hierarchical structure with a master deck and multiple subdecks:

```
ICRP_AMC_Clinical (Master Deck - 750 cards)
│
├── Medicine (99 cards)
│   ├── Cardiology (10 cards)
│   ├── Cardiorespiratory (15 cards)
│   ├── ENT (5 cards)
│   ├── Emergency (12 cards)
│   ├── Endocrinology (10 cards)
│   ├── Gastroenterology (30 cards)
│   └── Neurology (22 cards)
│
├── Surgery (33 cards)
│
├── ObGyn (25 cards)
│
├── Paediatrics (21 cards)
│
├── Psychiatry (18 cards)
│
├── Ethics_Communication (16 cards)
│
├── Communication (58 cards)
│
├── Physical_Examination (101 cards)
│
├── Red_Flags_Critical (61 cards)
│
├── IMG_Common_Mistakes (104 cards)
│
├── Australian_Context (86 cards)
│
└── General (22 cards)
```

---

## Card Structure

Each flashcard contains the following fields:

### 1. Front (Question)
- Clear, concise question or prompt
- Red flags marked with 🚨 emoji
- Australian context marked with 🇦🇺 emoji

### 2. Back (Answer)
- Comprehensive answer with clinical details
- Evidence-based information
- Australian guidelines referenced (eTG, AMH)

### 3. Tags
- **Category tags:** red-flag, critical, communication, physical_exam, differentials, australian, img_mistake
- **Difficulty tags:** easy, medium, hard
- **Specialty tags:** Based on subdeck

### 4. Source
- Reference to original HTML file
- Example: `Medicine/01_GI_Abdominal_Pain_Differentials.html`

---

## Card Categories & Statistics

### By Category (750 total)
| Category | Count | Description |
|----------|-------|-------------|
| **Red Flags** | 128 cards | Critical emergency presentations, don't-miss diagnoses |
| **Differentials** | 138 cards | Differential diagnoses for common presentations |
| **Physical Exam** | 137 cards | Examination techniques, findings, interpretations |
| **IMG Mistakes** | 135 cards | Common errors international medical graduates make |
| **Australian Context** | 128 cards | Australia-specific guidelines, terminology, practices |
| **Communication** | 84 cards | Patient communication, counselling, breaking bad news |

### By Difficulty (750 total)
| Difficulty | Count | Percentage |
|------------|-------|------------|
| **Easy** | 132 cards | 17.6% |
| **Medium** | 465 cards | 62.0% |
| **Hard** | 153 cards | 20.4% |

### By Specialty (Primary Decks)
| Specialty | Cards | Key Topics |
|-----------|-------|------------|
| **Medicine** | 205 total | Cardiology, Respiratory, GI, Neurology, Endocrinology, Emergency |
| **Physical Examination** | 101 cards | All systems examinations |
| **IMG Common Mistakes** | 104 cards | Cultural, clinical, communication pitfalls |
| **Australian Context** | 86 cards | Guidelines, Medicare, PBS, terminology |
| **Red Flags Critical** | 61 cards | Emergency presentations requiring immediate action |
| **Communication** | 58 cards | Patient-centered communication skills |
| **Surgery** | 33 cards | Acute abdomen, trauma, surgical emergencies |
| **ObGyn** | 25 cards | Pregnancy, gynecological complaints, contraception |
| **Paediatrics** | 21 cards | Childhood illnesses, developmental assessment |
| **Psychiatry** | 18 cards | Mental state exam, risk assessment |
| **Ethics Communication** | 16 cards | Consent, confidentiality, cultural safety |
| **General** | 22 cards | Cross-specialty topics |

---

## Styling Features

### Australian Medical Styling
- **Professional Design:** Clean, medical-grade appearance
- **Mobile-Friendly:** Responsive design for phone/tablet studying
- **Color-Coded:**
  - Red flags: Red background (#ffe5e5)
  - IMG mistakes: Yellow background (#fff3cd)
  - Regular cards: White background
- **Difficulty Indicators:**
  - Easy: Green text
  - Medium: Orange text
  - Hard: Red text

### CSS Classes Applied
- `.red-flag` - Emergency/critical cards
- `.img-mistake` - Common IMG errors
- `.australian-context` - Australia-specific content
- `.critical` - Urgent presentations
- `.difficulty-easy/medium/hard` - Difficulty levels

---

## How to Import the Deck

### Desktop (Anki Desktop)

1. **Download Anki:**
   - Visit: https://apps.ankiweb.net/
   - Download for Windows/Mac/Linux
   - Install and open Anki

2. **Import the Deck:**
   - Click `File > Import`
   - Navigate to: `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/`
   - Select: `ICRP_AMC_Clinical.apkg`
   - Click `Open`

3. **Verify Import:**
   - Check that `ICRP_AMC_Clinical` appears in deck list
   - Click on deck to see subdecks
   - Verify 750 cards total

### Mobile (AnkiMobile / AnkiDroid)

1. **Create AnkiWeb Account (Free):**
   - Visit: https://ankiweb.net/
   - Sign up for free account

2. **Sync from Desktop:**
   - In Anki Desktop: Click `Sync` button
   - Sign in with AnkiWeb credentials
   - Wait for upload to complete

3. **Download Mobile App:**
   - **iOS:** AnkiMobile Flashcards (paid, ~$35 AUD) - Official app
   - **Android:** AnkiDroid (FREE) - Open source
   - Install from App Store / Google Play

4. **Sync to Mobile:**
   - Open AnkiMobile/AnkiDroid
   - Sign in with same AnkiWeb account
   - Tap `Sync`
   - Deck will download automatically

---

## Study Recommendations

### Daily Practice (December 2025 - February 2026)

**New Cards per Day:** 25-30 cards
- This will complete all 750 cards in ~1 month
- Allows time for reviews before ICRP start (March 2, 2026)

**Review Schedule:**
- Follow Anki's spaced repetition algorithm
- Expect 50-100 reviews per day after first week

**Time Estimate:**
- New cards: 15-20 minutes (25 cards × 30-45 sec each)
- Reviews: 20-30 minutes (80 cards × 15-20 sec each)
- **Total daily time:** 35-50 minutes

### Study Strategy

#### Week 1-2: Foundation Building
1. Start with **Red Flags Critical** deck (61 cards)
   - Master emergency presentations first
   - These are highest-yield for OSCE safety
2. Add **Australian Context** (86 cards)
   - Learn terminology, guidelines, systems
3. Add **IMG Common Mistakes** (104 cards)
   - Avoid common pitfalls early

#### Week 3-4: Core Clinical Skills
1. Study **Physical Examination** (101 cards)
   - Essential for OSCE stations
2. Study **Communication** + **Ethics** (74 cards combined)
   - Practice exact phrases, patient-centered approach

#### Week 5-8: Specialty Content
1. Study all **Medicine** subdecks (205 cards)
   - Highest number of cards, most common presentations
2. Study **Surgery** (33 cards)
3. Study **ObGyn**, **Paediatrics**, **Psychiatry** (64 cards combined)

#### Week 9-12: Review & Integration
1. Review all cards multiple times
2. Focus on cards you've marked as difficult
3. Practice mock OSCE stations while reviewing relevant cards

### Custom Study Sessions

Anki allows filtering by tags. Use these for focused study:

```
tag:red-flag          # Emergency presentations only
tag:critical          # Critical/urgent cards
tag:img_mistake       # IMG common mistakes
tag:australian        # Australian context
tag:communication     # Communication skills
tag:physical_exam     # Physical examination
deck:Medicine*        # All Medicine subdecks
```

---

## Deck Customization

### Adjusting New Cards per Day

1. Click on `ICRP_AMC_Clinical` deck
2. Click gear icon ⚙️ (Options)
3. Under `New Cards` tab:
   - Adjust `New cards/day` (default: 20, recommended: 25-30)
4. Click `Save`

### Adjusting Review Limits

1. Same Options menu
2. Under `Reviews` tab:
   - Set `Maximum reviews/day` (recommended: 200)
   - Prevents backlog from building up

### Changing Card Order

Options for new card order:
- **Random:** Mix all specialties (default)
- **Sequential:** Study decks in order
- **Recommendation:** Random to avoid monotony

---

## Integration with ICRP Study Plan

### Alignment with ICRP Goals

This Anki deck directly supports your ICRP preparation targets:

1. **History Taking (400+ practice):**
   - Differentials cards provide frameworks
   - IMG mistake cards show common history-taking errors
   - Communication cards teach proper questioning

2. **Physical Examination (100+ practice):**
   - Physical Examination deck covers all systems
   - Step-by-step techniques with exact wording

3. **Clinical Documentation:**
   - Australian Context cards cover EMR systems, Medicare, PBS
   - Helps with proper terminology in notes

4. **OSCE Readiness:**
   - Red Flags ensure safety
   - Communication cards practice exact phrases examiners expect
   - Specialty cards cover all OSCE domains

### Complementary Resources

Use this Anki deck alongside:
- `/ICRP_OSCE_Preparation/` - Full OSCE guides
- `/ICRP_Program_Resources/Case_Scenarios/` - Practice cases
- `/ICRP_Program_Resources/Templates/` - SOAP note templates
- Mock OSCE practice with peers

---

## Troubleshooting

### Import Issues

**Problem:** "This file appears to be damaged"
- **Solution:** Re-download the .apkg file, ensure it wasn't corrupted during transfer

**Problem:** Cards not showing formatting
- **Solution:** Update Anki to latest version (2.1.65+)

**Problem:** Subdecks not appearing
- **Solution:** Click the `▶` arrow next to `ICRP_AMC_Clinical` to expand

### Sync Issues

**Problem:** Sync taking very long
- **Solution:** First sync always uploads all cards (may take 5-10 min). Subsequent syncs are fast.

**Problem:** "Media sync failed"
- **Solution:** This deck has no media (images/audio), error can be ignored

### Study Issues

**Problem:** Too many reviews piling up
- **Solution:**
  1. Reduce new cards per day temporarily
  2. Increase maximum reviews/day limit
  3. Consider extending study period

**Problem:** Cards too hard
- **Solution:** Use the `Hard` button during reviews to see them more frequently

---

## Performance Metrics

### Expected Progress Milestones

**After 1 Week:**
- ✓ 150-200 cards introduced
- ✓ Red flags mastered
- ✓ Australian terminology familiar

**After 1 Month:**
- ✓ All 750 cards seen at least once
- ✓ 60-70% retention rate expected
- ✓ 200-300 cards in "mature" state (21+ day interval)

**After 2 Months (Pre-ICRP):**
- ✓ 85%+ retention rate
- ✓ 500+ cards in "mature" state
- ✓ Most cards reviewed 3-5 times
- ✓ Red flags instantly recallable

**During ICRP (March-May 2026):**
- Continue daily reviews (10-15 min/day)
- Mark any cards you encounter in real practice
- Add custom cards for new learning

---

## Regenerating the Deck

If you need to recreate the deck (e.g., after updating flashcard_data.json):

### Prerequisites
```bash
cd /home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards
python3 -m venv venv  # If venv doesn't exist
./venv/bin/pip install genanki
```

### Generate Deck
```bash
./venv/bin/python create_anki_deck.py
```

This will:
1. Read `flashcard_data.json`
2. Create hierarchical deck structure
3. Apply Australian medical styling
4. Generate `ICRP_AMC_Clinical.apkg`

### Import Updated Deck

**Important:** Anki will merge updates with existing cards based on note IDs.

**Recommended approach:**
1. In Anki Desktop: `File > Export`
   - Export your current deck (to backup progress)
   - Include scheduling information
2. Delete old `ICRP_AMC_Clinical` deck
3. Import new `ICRP_AMC_Clinical.apkg`
4. If needed, import your backup to restore scheduling

---

## Advanced Features

### Custom Fields Available

The note model includes these fields (can be edited):
- **Front:** Question text
- **Back:** Answer text
- **Tags:** Space-separated tags
- **Source:** Reference file

### Adding Custom Cards

1. In Anki Desktop, click `Add` button
2. Select note type: `ICRP AMC Clinical Model`
3. Fill in fields:
   - Front: Your question
   - Back: Your answer
   - Tags: Relevant tags (e.g., custom australian)
   - Source: Your reference
4. Select deck: Choose appropriate subdeck
5. Click `Add`

### Tagging Strategy

Create custom filtered decks based on your weak areas:

**Example 1:** Create "Weak Areas" deck
```
tag:hard rated:1  # Cards you've marked "Again" recently
```

**Example 2:** Create "High-Yield OSCE" deck
```
tag:red-flag OR tag:communication OR tag:australian
```

---

## Mobile Study Tips

### Optimal Settings for Phone/Tablet

1. **Enable Night Mode:**
   - Settings > Night Mode > Automatic
   - Easier on eyes during late-night study

2. **Gesture Controls (AnkiDroid):**
   - Swipe left: "Again"
   - Swipe right: "Good"
   - Tap center: Reveal answer

3. **Study in Commute:**
   - Cards designed for quick review (15-30 sec each)
   - Perfect for bus/train study sessions

4. **Offline Access:**
   - Both AnkiMobile and AnkiDroid work offline
   - Sync when WiFi available

---

## Quality Assurance

### Deck Validation Checklist

All 750 cards have been validated for:
- ✓ Australian spelling (colour, paediatric, anaemia)
- ✓ Australian guidelines (eTG, AMH references)
- ✓ Australian terminology (GP not PCP, ED not ER)
- ✓ SI units (mmol/L not mg/dL)
- ✓ Medicare/PBS context
- ✓ Proper HTML escaping (mostly - some medical values like `<100` trigger warnings)
- ✓ Mobile-friendly display
- ✓ Accurate sources referenced

### Known Issues

**HTML Warnings:**
- Some cards contain medical values like `<100` (less than 100)
- These appear as HTML tag warnings but display correctly
- Does not affect card functionality

**Deck Hierarchy:**
- `Medicine_General` appears as separate from main `Medicine` deck
- This is intentional to distinguish general medicine cards from subspecialty cards

---

## Version History

### Version 1.0 (December 16, 2025)
- Initial release
- 750 cards across 20 decks
- Full Australian medical context
- Mobile-responsive styling
- Complete subdeck hierarchy

---

## Support & Feedback

### Reporting Issues

If you find errors in cards:
1. Note the card ID (if visible) or exact question text
2. Document the error (spelling, clinical inaccuracy, etc.)
3. Update `flashcard_data.json`
4. Regenerate deck using `create_anki_deck.py`

### Suggesting Improvements

Enhancement ideas:
- Additional cards for specific topics
- Better organization of subdecks
- Improved CSS styling
- Audio/image media additions

---

## License & Attribution

**Created for:** ICRP NSW Preparation (Young District Hospital)
**Target Exam:** AMC Clinical Examination
**Created:** December 16, 2025
**Last Updated:** December 16, 2025

**Sources:**
- All cards generated from ICRP_OSCE_Preparation HTML files
- Based on Australian medical guidelines (eTG, AMH)
- Aligned with AMC Clinical exam structure

---

## Quick Reference

### File Locations
- **Deck file:** `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/ICRP_AMC_Clinical.apkg`
- **Source data:** `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json`
- **Generator script:** `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/create_anki_deck.py`
- **Documentation:** `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/ANKI_DECK_STRUCTURE.md`

### Important Numbers
- **Total cards:** 750
- **Total decks:** 20 (1 master + 19 subdecks)
- **Recommended daily new cards:** 25-30
- **Expected daily study time:** 35-50 minutes
- **File size:** 453KB

### Key Tags
- `red-flag` - Emergency presentations
- `critical` - Urgent/critical cases
- `img_mistake` - Common IMG errors
- `australian` - Australian context
- `communication` - Communication skills
- `physical_exam` - Physical examination

### Useful Anki Shortcuts
- **Space:** Reveal answer
- **1:** Again (review soon)
- **2:** Hard (review sooner than Good)
- **3:** Good (standard interval)
- **4:** Easy (long interval)
- **Ctrl+Z:** Undo last answer
- **@:** Suspend card (hide temporarily)

---

**Ready to Start?**
1. Import `ICRP_AMC_Clinical.apkg` into Anki
2. Set new cards to 25-30 per day
3. Study daily for 35-50 minutes
4. Master all 750 cards before March 2, 2026
5. Ace your ICRP rotation!

**Good luck with your OSCE preparation!** 🎓🇦🇺
