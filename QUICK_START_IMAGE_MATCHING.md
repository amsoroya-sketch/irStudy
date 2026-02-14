# Quick Start: MCQ Image Matching

## Run Image Matching

```bash
# From project root
python3 scripts/link_images_to_mcqs.py
```

**Output:** `data/mcqs/mcq_image_matches.json`

---

## Check Results

```bash
# Summary statistics
python3 -c "import json; r = json.load(open('data/mcqs/mcq_image_matches.json')); print(f\"Matched: {r['total_mcqs_matched']}/{r['total_mcqs_processed']} ({r['match_rate']})\")"

# View top matches
python3 -c "import json; r = json.load(open('data/mcqs/mcq_image_matches.json')); [print(f'{k}: Score {m[0][\"match_score\"]} - {m[0][\"image_title\"][:50]}') for k,m in list(r['matches'].items())[:10]]"
```

---

## Re-run After Adding Images

```bash
# 1. Download new images (update catalog)
python3 scripts/create_image_catalog.py

# 2. Re-run matching
python3 scripts/link_images_to_mcqs.py
```

---

## Output Format

```json
{
  "generated_at": "2026-02-07T12:23:56",
  "total_mcqs_processed": 5608,
  "total_mcqs_matched": 733,
  "match_rate": "13.1%",
  "matches": {
    "MCQ_ID": [
      {
        "image_id": "heal_870088",
        "path": "data/medical_images/heal/cardiology/inferior_wall_MI/heal_870088.png",
        "match_score": 70,
        "match_reason": "specialty_keywords: 2 matches (acute, mi)",
        "image_title": "Acute infero-postero-lateral MI",
        "source": "HEAL"
      }
    ]
  },
  "statistics": {...}
}
```

---

## Current Status

- **MCQs matched:** 733 / 5,608 (13.1%)
- **Match quality:** 23.2% excellent, 76.8% good/fair
- **Best specialty:** Respiratory (26.2% match rate)

---

## Next Steps

1. Download images for missing specialties:
   - Psychiatry (800 MCQs, 0 images)
   - Neurology clinical cases
   - Gastroenterology
   - Endocrinology

2. Re-run matching (expected: 50-70% match rate)

3. Manual curation of matches

4. Integrate approved images into MCQ database

---

**Full Documentation:** `MCQ_IMAGE_MATCHING_COMPLETE.md`
**Strategy:** `IMAGE_LINKING_STRATEGY.md`
