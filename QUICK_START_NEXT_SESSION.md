# Quick Start - Next Session Guide
**Date:** 2026-02-07
**Status:** Ready for MCQ Structure Fix

---

## What Was Completed

✅ **Image Library Expansion:** 2,548 → 4,537 images (+78%)
✅ **New Specialties:** Psychiatry (162), Obstetrics (347), Paediatrics (423)
✅ **Expanded Specialties:** Cardiology +403%, Dermatology +347%, Haematology +89%
✅ **Infrastructure:** Production-ready catalog rebuild + matching pipeline
✅ **Catalogs:** 100% metadata completeness for all 4,537 images

---

## Current Status

**Image Library:** ✅ **READY**
- 4,537 high-quality medical images
- 13 specialties covered
- NIH peer-reviewed (OpenI) + HEAL collections
- Complete metadata and taxonomy mapping

**MCQ Matching:** ⚠️ **BLOCKED BY STRUCTURE ISSUE**
- Current match rate: 14.1% (791/5,608 MCQs)
- Expected after fix: 40-60% (2,240-3,365 MCQs)
- Issue: MCQs missing "specialty" field
- Solution: Add "specialty" field to MCQ JSON files

---

## The Problem (High Priority - Next Session)

### MCQ Structure Issue

**Current MCQ Format:**
```json
{
  "id": "WEEK1-REGEN-001",
  "topic": "Depression",              // ✅ Has topic
  "subtopic": "Major depressive disorder",  // ✅ Has subtopic
  // ❌ MISSING "specialty" FIELD!
  "question": {...},
  "correct_answer": "B",
  "explanation": "...",
  "references": [...]
}
```

**Matching Algorithm Expects:**
```python
specialty = mcq.get('specialty', 'unknown')  # Returns 'unknown' for most MCQs!
```

**Impact:**
- 1,971 MCQs (35.1%): Marked as "unknown" specialty
- 800 psychiatry MCQs (14.3%): Can't match with 162 psychiatry images
- Primary matching (100-point scores): Impossible
- Secondary matching (60-99 scores): Blocked
- Only tertiary matching (40-59 scores): Working

---

## Solution: Add Specialty Field to MCQs

### Option A: Create Topic-to-Specialty Mapping Script (Recommended)

**Step 1: Create mapping rules**
```python
# scripts/add_specialty_field_to_mcqs.py

TOPIC_TO_SPECIALTY_MAP = {
    # Psychiatry
    'Depression': 'psychiatry',
    'Anxiety': 'psychiatry',
    'Psychosis': 'psychiatry',
    'Bipolar': 'psychiatry',
    'Schizophrenia': 'psychiatry',
    'Suicide Risk': 'psychiatry',
    
    # Cardiology
    'STEMI': 'cardiology',
    'NSTEMI': 'cardiology',
    'Atrial Fibrillation': 'cardiology',
    'Heart Failure': 'cardiology',
    'Hypertension': 'cardiology',
    'Arrhythmia': 'cardiology',
    
    # Respiratory
    'Pneumonia': 'respiratory',
    'COPD': 'respiratory',
    'Asthma': 'respiratory',
    'Pneumothorax': 'respiratory',
    'PE': 'respiratory',
    'Pulmonary Embolism': 'respiratory',
    
    # Add more mappings...
}

def add_specialty_to_mcq(mcq):
    """Add specialty field based on topic"""
    topic = mcq.get('topic', '')
    
    # Check direct mapping
    if topic in TOPIC_TO_SPECIALTY_MAP:
        mcq['specialty'] = TOPIC_TO_SPECIALTY_MAP[topic]
        return mcq
    
    # Check partial matching
    for keyword, specialty in TOPIC_TO_SPECIALTY_MAP.items():
        if keyword.lower() in topic.lower():
            mcq['specialty'] = specialty
            return mcq
    
    # Default to unknown if no match
    mcq['specialty'] = 'unknown'
    return mcq
```

**Step 2: Process all MCQ files**
```python
import json
from pathlib import Path

mcq_dir = Path('data/mcqs')
updated_count = 0

for mcq_file in mcq_dir.glob('*.json'):
    data = json.load(open(mcq_file))
    
    # Handle different JSON structures
    if 'mcqs' in data:
        # Structure: {"metadata": {...}, "mcqs": [...]}
        for mcq in data['mcqs']:
            add_specialty_to_mcq(mcq)
        updated_count += len(data['mcqs'])
    elif isinstance(data, list):
        # Structure: [mcq1, mcq2, ...]
        for mcq in data:
            add_specialty_to_mcq(mcq)
        updated_count += len(data)
    
    # Save updated file
    json.dump(data, open(mcq_file, 'w'), indent=2)

print(f"Updated {updated_count} MCQs across {len(list(mcq_dir.glob('*.json')))} files")
```

**Step 3: Re-run matching**
```bash
python3 scripts/link_images_to_mcqs.py
```

**Expected Result:**
- Match rate: 14.1% → 40-60%
- Psychiatry: 0% → 50-65% (400-520 matches)
- Cardiology: 19.0% → 35-45% (567-730 matches)
- Unknown: 35.1% → <5%

---

## Quick Commands for Next Session

### Check Current Status
```bash
# Check image library
jq '.total_images, .by_specialty' data/medical_images/catalog_summary.json

# Check MCQ matching
python3 -c "import json; r = json.load(open('data/mcqs/mcq_image_matches.json')); print(f\"Matched: {r['total_mcqs_matched']}/{r['total_mcqs_processed']} ({r['match_rate']})\")"

# Check MCQ structure (see if specialty field exists)
jq '.mcqs[0] | keys' data/mcqs/week1_regenerated_100_mcqs.json
```

### Fix MCQ Structure
```bash
# Create the fix script
# (Use the template above in scripts/add_specialty_field_to_mcqs.py)

# Run the fix
python3 scripts/add_specialty_field_to_mcqs.py

# Re-run matching
python3 scripts/link_images_to_mcqs.py

# Check new results
tail -50 logs/mcq_matching_after_fix.log
```

### Verify Results
```bash
# Count psychiatry matches (should be 400-520)
jq '.summary_by_specialty.Psychiatry' data/mcqs/mcq_image_matches.json

# Check overall match rate (should be 40-60%)
jq '.match_rate, .total_mcqs_matched' data/mcqs/mcq_image_matches.json

# View quality distribution
jq '.match_quality_distribution' data/mcqs/mcq_image_matches.json
```

---

## Alternative: Update Matching Algorithm (Option B)

If you prefer to keep MCQ files unchanged, update the matching algorithm:

```python
# In scripts/link_images_to_mcqs.py

def extract_specialty_from_mcq(mcq):
    """Extract specialty from MCQ topic field"""
    
    # First check if specialty field exists
    if 'specialty' in mcq and mcq['specialty'] != 'unknown':
        return mcq['specialty']
    
    # Fall back to topic-based mapping
    topic = mcq.get('topic', '').lower()
    
    # Psychiatry keywords
    if any(kw in topic for kw in ['depression', 'anxiety', 'psychosis', 'bipolar', 'schizophrenia', 'suicide']):
        return 'psychiatry'
    
    # Cardiology keywords
    if any(kw in topic for kw in ['stemi', 'nstemi', 'mi', 'af', 'arrhythmia', 'heart', 'cardiac']):
        return 'cardiology'
    
    # Respiratory keywords
    if any(kw in topic for kw in ['pneumonia', 'copd', 'asthma', 'respiratory', 'pneumothorax', 'pe']):
        return 'respiratory'
    
    # Add more mappings...
    
    return 'unknown'

# Then in the matching loop, replace:
# specialty = mcq.get('specialty', 'unknown')
# with:
specialty = extract_specialty_from_mcq(mcq)
```

**Note:** Option A (adding specialty field) is preferred because:
- Fixes the underlying data structure issue
- Makes data more explicit and maintainable
- Prevents future issues with other tools expecting specialty field

---

## Files to Review

### Documentation
- `SESSION_SUMMARY_2026-02-07_IMAGE_EXPANSION.md` - Complete session summary
- `IMAGE_EXPANSION_COMPLETE.md` - Technical expansion report
- `QUICK_START_NEXT_SESSION.md` - This document

### Data Files
- `data/medical_images/unified_image_catalog.json` - 4,537 images
- `data/mcqs/mcq_image_matches.json` - Current 791 matches
- `data/mcqs/*.json` - All MCQ files (need specialty field added)

### Scripts Ready to Use
- `scripts/rebuild_openi_catalog.py` - Rebuild OpenI metadata
- `scripts/rebuild_heal_catalog.py` - Rebuild HEAL metadata
- `scripts/create_image_catalog.py` - Create unified catalog
- `scripts/link_images_to_mcqs.py` - MCQ matching algorithm

---

## Expected Timeline (Next Session)

**Task 1: Create specialty mapping script** (30 minutes)
- Define topic-to-specialty mappings
- Handle edge cases
- Test on sample file

**Task 2: Update all MCQ files** (15 minutes)
- Run script on all MCQ JSON files
- Verify specialty field added
- Check coverage (aim for >95% classified)

**Task 3: Re-run matching** (5 minutes)
- Execute matching algorithm
- Wait for completion (~2 minutes)
- Review results

**Task 4: Verify results** (15 minutes)
- Check match rate (expect 40-60%)
- Verify psychiatry matches (expect 400-520)
- Review match quality distribution

**Total Estimated Time:** ~65 minutes

---

## Success Criteria

### Task Complete When:
- ✅ All MCQ files have "specialty" field (>95% coverage)
- ✅ Match rate improved to 40-60% (from 14.1%)
- ✅ Psychiatry matches: 400-520 (from 0)
- ✅ Cardiology matches: 567-730 (from 308)
- ✅ Unknown specialty: <5% (from 35.1%)
- ✅ Match quality: 60%+ good/excellent

---

## Contact Points / Questions

**If match rate still low after fix:**
- Check if topic-to-specialty mappings are comprehensive
- Review MCQ topics that remain "unknown"
- Consider expanding keyword matching

**If psychiatry still 0%:**
- Verify psychiatry MCQ files have specialty field
- Check psychiatry images exist in catalog (should be 162)
- Verify matching algorithm normalizes specialty names

**If errors occur:**
- Check JSON file structure (some files may have different formats)
- Verify all MCQ files are valid JSON
- Review error logs for specific file issues

---

## Quick Reference: Image Library Stats

```
Total Images: 4,537
  Neurology: 584
  Gastroenterology: 518  
  Cardiology: 507 (423 OpenI + 84 HEAL)
  Emergency Medicine: 448
  Paediatrics: 423 (NEW)
  Dermatology: 405 (331 OpenI + 74 HEAL)
  Respiratory: 375
  Obstetrics & Gynaecology: 347 (NEW)
  Haematology: 463 (303 OpenI + 160 HEAL)
  Endocrinology: 300
  Psychiatry: 162 (NEW)
  Gastrointestinal: 5

Sources:
  OpenI (NIH): 4,209 images (92.8%)
  HEAL (Utah): 328 images (7.2%)

Topics: 669 unique topics mapped
```

---

## After MCQ Fix: Next Priorities

### Priority 2: OSCE Image Matching
- Create `scripts/link_images_to_osces.py`
- Similar to MCQ matching but scenario-based
- Target: 140+ OSCEs

### Priority 3: Manual Curation
- Review 182 excellent matches (≥80 score)
- Verify clinical accuracy
- Add teaching captions

### Priority 4: Database Integration
- Update MCQ JSON files with approved image paths
- Add display timing, captions, citations
- Test frontend rendering

---

**Status:** ✅ **READY TO START**
**First Task:** Create `scripts/add_specialty_field_to_mcqs.py`
**Expected Outcome:** 14.1% → 40-60% match rate
**Time Estimate:** ~65 minutes
