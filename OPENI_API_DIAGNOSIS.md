# OpenI API Diagnosis - Root Cause Found

**Date:** 2026-02-06 17:30
**Status:** ✅ **ISSUE IDENTIFIED AND FIXABLE**

---

## Summary

The OpenI API is **WORKING** but returns **JSON by default**, not XML. Our script was requesting XML format (`it=x`) but the API returns HTTP 500 error when XML is requested, then falls back to JSON.

---

## Failed Download Details

### Website Used
**OpenI (Open Access Biomedical Image Search)**
- URL: https://openi.nlm.nih.gov/
- API Endpoint: https://openi.nlm.nih.gov/api/search
- Provider: U.S. National Library of Medicine (NIH)

### Search Terms That Failed

All 75 emergency medicine topics failed with the same error. Examples:

| Topic | Search Terms Tried | Result |
|-------|-------------------|--------|
| **Skull Fracture** | "skull fracture CT", "linear skull fracture", "depressed skull fracture", "skull fracture X-ray" | 0 images |
| **Extradural Haematoma** | "extradural haematoma CT", "epidural haematoma brain", "EDH lentiform", "acute extradural haemorrhage" | 0 images |
| **Subdural Haematoma** | "subdural haematoma CT", "acute SDH brain", "chronic subdural haematoma", "crescent subdural" | 0 images |
| **Pneumothorax** | "pneumothorax chest X-ray", "tension pneumothorax CT", "traumatic pneumothorax", "PTX imaging emergency" | 0 images |
| **STEMI** | "STEMI ECG", "ST elevation myocardial infarction", "acute MI ECG", "anterior STEMI" | 0 images |

**Total Failed:** 75 topics × 4 search terms each = 300 failed searches

---

## Root Cause Analysis

### Error Message
```
Error searching OpenI: not well-formed (invalid token): line 1, column 0
```

### What We Requested
```python
params = {
    'query': 'pneumothorax',
    'm': 8,
    'it': 'x'  # ← Requesting XML format
}
```

**Example URL:**
```
https://openi.nlm.nih.gov/api/search?query=pneumothorax&m=8&it=x
```

### What OpenI Returned

**HTTP Status:** `500 Internal Server Error`

**Response Headers:**
```
HTTP/1.1 500 500
Date: Fri, 06 Feb 2026 10:55:58 GMT
Server: Apache
Content-Security-Policy: default-src * 'unsafe-eval' 'unsafe-inline' ...
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Frame-Options: SAMEORIGIN
Content-Length: 31
```

**When XML format requested (`it=x`):** HTTP 500 error

**When JSON format used (default or `it=j`):** HTTP 200 success!

### Actual Working Response (JSON)

```bash
curl "https://openi.nlm.nih.gov/api/search?query=pneumothorax&m=5"
```

**Returns:**
```json
{
   "min": 5,
   "max": 10,
   "count": 6,
   "total": 6521,
   "approximage": "false",
   "list": [
      {
         "uid": "PMC2946724",
         "pmcid": "2946724",
         "pmid": "20931041",
         "docSource": "PMC",
         "articleType": "cr",
         "pmc_url": "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2946724",
         "pubMed_url": "http://www.ncbi.nlm.nih.gov/pubmed/20931041",
         "title": "Silicosis with bilateral spontaneous pneumothorax.",
         ...
      }
   ]
}
```

**Key Finding:** OpenI has **6,521 pneumothorax images available!**

---

## The Fix

### Problem
```python
# scripts/download_openi.py (lines 57-63)
params = {
    'query': query,
    'm': max_results,
    'it': 'x'  # ← This causes HTTP 500!
}

response = self.session.get(self.SEARCH_API, params=params, timeout=30)
root = ET.fromstring(response.content)  # ← Tries to parse JSON as XML → fails
```

### Solution

**Option 1: Use JSON instead of XML** (Recommended)
```python
import json

params = {
    'query': query,
    'm': max_results,
    # Remove 'it': 'x' or use 'it': 'j'
}

response = self.session.get(self.SEARCH_API, params=params, timeout=30)
data = response.json()  # Parse as JSON

# Extract image URLs from JSON response
images = []
for item in data.get('list', []):
    image_data = {
        'id': item.get('uid'),
        'pmcid': item.get('pmcid'),
        'title': item.get('title'),
        'journal': item.get('journal_title'),
        # Image URLs need to be extracted from item details
    }
    images.append(image_data)
```

**Option 2: Don't request specific format** (Also works)
```python
params = {
    'query': query,
    'm': max_results,
    # Don't specify 'it' parameter - defaults to JSON
}
```

---

## OpenI JSON Response Structure

### Search Response Fields

```json
{
  "min": 5,           // Results per page
  "max": 10,          // Max results requested
  "count": 6,         // Actual results returned
  "total": 6521,      // Total available for this query
  "approximage": "false",
  "list": [...]       // Array of result objects
}
```

### Individual Result Fields

```json
{
  "uid": "PMC2946724",
  "pmcid": "2946724",
  "pmid": "20931041",
  "docSource": "PMC",
  "articleType": "cr",
  "pmc_url": "http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2946724",
  "pubMed_url": "http://www.ncbi.nlm.nih.gov/pubmed/20931041",
  "title": "Silicosis with bilateral spontaneous pneumothorax.",
  "fulltext_html_url": "",
  "journal_title": "Lung India : official organ of Indian Chest Society",
  "journal_abbr": "Lung India",
  "journal_date": {...},
  "image": {
    "thumb": "https://openi.nlm.nih.gov/imgs/thumb/PMC2946724_LI-27-189-g001.png",
    "large": "https://openi.nlm.nih.gov/imgs/512/PMC2946724_LI-27-189-g001.png"
  }
}
```

**Key Fields:**
- `image.large` - Full-size image URL (512px)
- `image.thumb` - Thumbnail URL
- `pmcid` - PubMed Central ID
- `title` - Article title
- `total` - Total images available for query

---

## Available Content in OpenI

Based on the test query, OpenI has extensive medical imaging:

| Search Term | Total Images | Status |
|-------------|--------------|--------|
| **Pneumothorax** | 6,521 | ✅ Excellent |
| **Skull fracture** | ~2,000-4,000 (estimated) | ✅ Likely good |
| **STEMI** | ~3,000-5,000 (estimated) | ✅ Likely good |
| **Subdural haematoma** | ~1,000-3,000 (estimated) | ✅ Likely good |

**Total Potential:** 10,000+ images for emergency medicine alone!

---

## Implementation Fix

### Quick Fix (5 minutes)

Edit `scripts/download_openi.py`:

**Line 57-63 (search method):**
```python
# OLD (broken):
params = {
    'query': query,
    'm': max_results,
    'it': 'x'  # Remove this line
}

# Parse XML
root = ET.fromstring(response.content)

# NEW (working):
params = {
    'query': query,
    'm': max_results
    # No 'it' parameter - defaults to JSON
}

# Parse JSON
data = response.json()
```

**Lines 80-95 (extract images):**
```python
# OLD (XML parsing):
for doc in root.findall('.//doc'):
    image_data = {}
    for field in doc.findall('.//field'):
        name = field.get('name')
        value = field.text
        # ...

# NEW (JSON parsing):
for item in data.get('list', []):
    image_data = {
        'id': item.get('uid'),
        'url': item.get('image', {}).get('large', ''),
        'thumbnail_url': item.get('image', {}).get('thumb', ''),
        'title': item.get('title', ''),
        'journal': item.get('journal_title', ''),
        'pmcid': item.get('pmcid', ''),
        'year': item.get('journal_date', {}).get('year', '')
    }

    if image_data['url']:  # Only add if image URL exists
        images.append(image_data)
```

---

## Expected Results After Fix

### Emergency Medicine (75 topics)

Estimated downloads with fixed script:

| Topic Category | Topics | Images/Topic | Total Images |
|----------------|--------|--------------|--------------|
| **Head Trauma** | 10 | 8 | 80 |
| **Spinal Trauma** | 5 | 8 | 40 |
| **Chest Trauma** | 8 | 8 | 64 |
| **Abdominal Trauma** | 10 | 8 | 80 |
| **Limb Trauma** | 8 | 8 | 64 |
| **Facial Trauma** | 4 | 8 | 32 |
| **Acute Abdomen** | 10 | 8 | 80 |
| **Cardiovascular** | 10 | 8 | 80 |
| **Respiratory** | 5 | 8 | 40 |
| **Other** | 5 | 8 | 40 |
| **─────────** | **75** | **─────** | **600** |

**Realistic Target:** 400-600 emergency medicine images

---

## Next Steps

### Immediate (10 minutes)

1. **Fix the script:**
   ```bash
   # Edit scripts/download_openi.py
   # Change XML parsing to JSON parsing
   # Test with single query
   ```

2. **Test fix:**
   ```bash
   python3 scripts/download_openi.py \
       --taxonomy data/medical_image_taxonomy_v1.json \
       --specialties emergency_medicine \
       --images-per-topic 2 \
       --output data/medical_images/openi_test
   ```

3. **Run full download:**
   ```bash
   python3 scripts/download_openi.py \
       --taxonomy data/medical_image_taxonomy_v1.json \
       --specialties emergency_medicine \
       --images-per-topic 8 \
       --priority-only \
       --output data/medical_images/openi
   ```

### Expected Timeline

- **Fix script:** 10 minutes
- **Test download:** 5 minutes (10-20 test images)
- **Full emergency medicine download:** 30-45 minutes (400-600 images)
- **Additional specialties:** 1-2 hours (neurology, respiratory, etc.)

**Estimated Total:** 2-3 hours to download 1,500-2,000 images from OpenI

---

## Impact Assessment

### Before Fix
- OpenI images: 0
- Total images: 856
- Emergency medicine: 0/600

### After Fix (Projected)
- OpenI images: 1,500-2,000
- Total images: 2,356-2,856
- Emergency medicine: 400-600/600 ✅
- Neurology: 400-600/800 🟡
- Respiratory: 300-400/305 ✅
- Completion: 37-45% (vs 13.6% current)

---

## Conclusion

**Root Cause:** Script requested XML format (`it=x`), but OpenI API only supports JSON (or defaults to JSON without format parameter).

**Fix Complexity:** Low - Change XML parsing to JSON parsing (~10 lines of code)

**Expected Benefit:** +1,500-2,000 high-quality NIH medical images

**Implementation Time:** 10 minutes to fix + 2-3 hours to download

**Priority:** 🔴 **HIGH** - This will fill the biggest gaps (emergency medicine, neurology, respiratory)

---

**Generated:** 2026-02-06 17:30
**Status:** Ready to fix and retry
**Next Action:** Edit download_openi.py to use JSON instead of XML
