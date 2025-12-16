# Anki Import Instructions

## Quick Start

### Option 1: Use Existing Anki Import File (Easiest)

1. Open Anki Desktop
2. Click **File → Import**
3. Select: `/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/anki_import.txt`
4. Configure import settings:
   - **Type:** Basic
   - **Deck:** Create new deck "ICRP_AMC_Clinical"
   - **Fields separated by:** Tab
   - **Allow HTML in fields:** Yes
5. Click **Import**

### Option 2: Use JSON Data (For Custom Import)

1. Install the **CrowdAnki** add-on in Anki:
   - Tools → Add-ons → Get Add-ons
   - Code: `1788670778`
2. File → CrowdAnki: Import from disk
3. Select the Flashcards directory
4. Import will automatically create deck structure

### Option 3: Manual CSV Import

If you need to create a CSV from the JSON:

```bash
cd /home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards
python3 << 'EOF'
import json
import csv

with open('flashcard_data.json', 'r') as f:
    data = json.load(f)

with open('flashcard_export.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['Front', 'Back', 'Tags', 'Source'])

    for card in data['cards']:
        front = card['front']
        back = card['back']
        tags = ' '.join([f"#{tag}" for tag in card.get('tags', [])])
        source = card.get('source', '')

        writer.writerow([front, back, tags, source])

print("Created flashcard_export.csv")
EOF
```

Then import flashcard_export.csv into Anki.

---

## Deck Structure Recommendation

Create the following deck hierarchy in Anki:

```
ICRP_AMC_Clinical
├── 01_Differentials (138 cards)
├── 02_IMG_Mistakes (135 cards)
├── 03_Physical_Exam (137 cards)
├── 04_Red_Flags (128 cards)
├── 05_Australian_Context (128 cards)
└── 06_Communication (84 cards)
```

---

## Study Schedule Recommendation

### Phase 1: Foundation (Weeks 1-4)
- **New cards per day:** 30-40
- **Review cards:** All due cards
- **Daily time:** 45-60 minutes
- **Focus:** Red Flags + Differentials + IMG Mistakes

### Phase 2: Expansion (Weeks 5-8)
- **New cards per day:** 25-35
- **Review cards:** All due cards
- **Daily time:** 60-75 minutes
- **Focus:** Add Physical Exam + Communication

### Phase 3: Refinement (Weeks 9-12)
- **New cards per day:** 20-30
- **Review cards:** All due cards
- **Daily time:** 60-90 minutes
- **Focus:** Complete all decks + Australian Context

---

## Anki Settings for Medical Study

### New Cards Tab
- **Learning steps:** 1m 10m 1d 3d
- **Graduating interval:** 7 days
- **Easy interval:** 10 days
- **Starting ease:** 250%

### Reviews Tab
- **Maximum reviews/day:** 500
- **Easy bonus:** 130%
- **Interval modifier:** 100%
- **Hard interval:** 120%

### Lapses Tab
- **Relearning steps:** 10m 1d
- **Minimum interval:** 1 day
- **Leech threshold:** 8 lapses

---

## Tags Overview

All cards have been tagged with:
1. **Category tag:** differentials, img_mistake, physical_exam, red_flags, communication, australian
2. **Difficulty tag:** easy, medium, hard

Use Anki's tag browser to filter cards:
- Study only "hard" difficulty cards
- Focus on specific categories (e.g., #red_flags)
- Combine tags (e.g., #differentials AND #hard)

---

## Mobile Sync (Optional)

### AnkiWeb Setup
1. Create account at: https://ankiweb.net/account/register
2. In Anki Desktop: Tools → Preferences → Network → AnkiWeb Account
3. Enter your credentials
4. Click "Sync" button (top right)

### AnkiMobile (iOS) or AnkiDroid (Android)
1. Download app from app store
2. Sign in with AnkiWeb account
3. Sync to download your decks
4. Study anywhere!

---

## Quality Assurance

All 750 flashcards have been:
- ✅ Checked for Australian spelling
- ✅ De-duplicated (no duplicate content)
- ✅ Source-attributed (traceable to original modules)
- ✅ Difficulty-rated (easy/medium/hard)
- ✅ Categorized into 6 main domains

---

## Troubleshooting

### Problem: Import shows errors
**Solution:** Ensure "Allow HTML in fields" is enabled in import settings

### Problem: Cards appear in wrong deck
**Solution:** After import, select all cards → Move to correct deck

### Problem: Tags not importing
**Solution:** Re-import with "Update existing notes when first field matches" checked

### Problem: Characters display incorrectly
**Solution:** Ensure import encoding is set to UTF-8

---

## Additional Resources

- **Anki Manual:** https://docs.ankiweb.net/
- **Anki Subreddit:** https://reddit.com/r/Anki
- **Medical School Anki Guide:** https://www.reddit.com/r/medicalschoolanki/

---

**Last Updated:** 2025-12-16
**Flashcard Count:** 750 cards
**Ready for:** AMC Clinical OSCE preparation
