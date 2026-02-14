# Alternative Medical Image Sources - Implementation Plan

**Date:** 2026-02-06
**Purpose:** Download images for 6 missing specialties + fill gaps in existing specialties

---

## Current Gaps

### Missing Specialties (0 images, need alternative sources)

| Specialty | Nodes | Target Images | Priority | Rationale |
|-----------|-------|---------------|----------|-----------|
| **Emergency Medicine** | 75 | 600 | 🔴 Critical | 12-18% AMC weight, 100% high-yield |
| **Neurology** | 100 | 800 | 🔴 Critical | 8-12% AMC weight, 90% high-yield |
| **Respiratory** | 61 | 305 | 🔴 Critical | 10-15% AMC weight (only 5 exist) |
| **Gastroenterology** | 88 | 704 | 🟡 High | 8-12% AMC weight (only 5 exist) |
| **Paediatrics** | 84 | 672 | 🟡 High | 8-12% AMC weight |
| **Obstetrics/Gynaecology** | 79 | 632 | 🟡 High | 8-12% AMC weight |
| **Endocrinology** | 72 | 576 | 🟠 Medium | 6-10% AMC weight |
| **Psychiatry** | 45 | 225 | 🟠 Medium | 6-10% AMC weight (less image-heavy) |
| **──────────** | **604** | **4,514** | **─────** | **───────────** |

**Total Gap:** 4,514 images needed

---

## Alternative Image Sources

### Source 1: OpenI (Open Access Biomedical Image Search)

**URL:** https://openi.nlm.nih.gov/
**Provider:** U.S. National Library of Medicine (NIH)
**License:** Open Access (mostly CC BY or Public Domain)
**API:** Yes - https://openi.nlm.nih.gov/services

**Coverage:**
- ✅ **Excellent:** Radiology (chest X-rays, CT, MRI)
- ✅ **Excellent:** Emergency imaging (trauma, acute presentations)
- ✅ **Good:** Neurology (brain MRI, CT, angiography)
- ✅ **Good:** Respiratory (pneumonia, COPD, PE imaging)
- ✅ **Good:** Gastroenterology (abdominal imaging)
- 🟡 **Fair:** Paediatrics (some pediatric cases)
- 🟡 **Fair:** Obstetrics (limited ultrasound)

**API Details:**
```bash
# Search API
https://openi.nlm.nih.gov/api/search?query=[QUERY]&m=[MAX_RESULTS]

# Image download
https://openi.nlm.nih.gov/imgs/512/[IMAGE_ID].png

# Example:
curl "https://openi.nlm.nih.gov/api/search?query=pneumothorax&m=10"
```

**Pros:**
- Free, open access
- High-quality radiology images
- RESTful API (easy to implement)
- No rate limiting mentioned
- Educational use explicitly allowed

**Cons:**
- Primarily radiology (less clinical photos)
- Limited dermatology, ophthalmology
- Sparse coverage for psychiatry

**Priority:** 🔴 **Implement First** - Best for emergency medicine, neurology, respiratory

---

### Source 2: Radiopaedia

**URL:** https://radiopaedia.org/
**Provider:** Radiopaedia Foundation (Australia-based!)
**License:** CC BY-NC-SA (educational use allowed)
**API:** Limited (requires partnership)

**Coverage:**
- ✅ **Excellent:** All radiology (CT, MRI, X-ray, ultrasound)
- ✅ **Excellent:** Neurology (comprehensive brain/spine imaging)
- ✅ **Excellent:** Emergency radiology (trauma protocols)
- ✅ **Excellent:** Respiratory (extensive chest imaging)
- ✅ **Excellent:** Gastroenterology (GI imaging)
- ✅ **Good:** Obstetrics (obstetric ultrasound)
- 🟡 **Fair:** Paediatrics (pediatric imaging cases)

**Access Methods:**
1. **Web Scraping** (with respect to robots.txt)
2. **Partnership API** (requires formal request)
3. **Manual Download** (for high-priority cases)

**Pros:**
- Australian-based (matches our AMC focus!)
- Exceptional image quality
- Comprehensive case presentations
- Teaching file format (diagnosis + images)

**Cons:**
- No public API (need partnership or scraping)
- CC BY-NC-SA (non-commercial use only)
- Rate limiting likely needed

**Priority:** 🔴 **High Priority** - Excellent for neurology, emergency, respiratory

---

### Source 3: MedPix (Medical Image Database)

**URL:** https://medpix.nlm.nih.gov/
**Provider:** NIH/Uniformed Services University
**License:** Public Domain (U.S. Government work)
**API:** No public API (web interface only)

**Coverage:**
- ✅ **Excellent:** Clinical photos (dermatology, ophthalmology)
- ✅ **Excellent:** Radiology (all modalities)
- ✅ **Good:** Pathology (gross and microscopic)
- ✅ **Good:** Endocrinology (clinical signs, imaging)
- 🟡 **Fair:** All specialties (broad but variable depth)

**Access Methods:**
1. **Web Scraping** (Playwright/Selenium)
2. **Manual Download** (for specific cases)

**Pros:**
- Public domain (no licensing issues)
- Clinical photos + radiology
- Case-based format

**Cons:**
- No API (requires scraping)
- Slower to download (web interface)
- Variable image quality

**Priority:** 🟠 **Medium Priority** - Good for endocrinology, clinical photos

---

### Source 4: Wikimedia Commons Medical Images

**URL:** https://commons.wikimedia.org/
**Provider:** Wikimedia Foundation
**License:** Various (mostly CC BY-SA, Public Domain)
**API:** Yes - MediaWiki API

**Coverage:**
- ✅ **Good:** Dermatology (extensive skin condition photos)
- ✅ **Good:** Ophthalmology (fundoscopy images)
- ✅ **Good:** Clinical signs (physical examination)
- 🟡 **Fair:** Most specialties (variable quality)

**API Details:**
```bash
# Search API
https://commons.wikimedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Medical_images&format=json

# Image download
https://commons.wikimedia.org/wiki/Special:FilePath/[FILENAME]
```

**Pros:**
- Free API access
- Good clinical photos
- Verified licensing
- Easy to implement

**Cons:**
- Variable image quality
- Inconsistent coverage
- Need to verify educational use for each license

**Priority:** 🟠 **Medium Priority** - Supplement for clinical photos

---

### Source 5: PubMed Central Open Access

**URL:** https://www.ncbi.nlm.nih.gov/pmc/
**Provider:** NIH National Library of Medicine
**License:** Open Access subset (CC BY, CC0)
**API:** Yes - E-utilities API

**Coverage:**
- ✅ **Excellent:** All specialties (from journal articles)
- ✅ **Good:** Obstetrics (case reports, ultrasound)
- ✅ **Good:** Paediatrics (pediatric cases)
- ✅ **Good:** Psychiatry (brain imaging, clinical photos)

**API Details:**
```bash
# Search for articles with images
https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pmc&term=pneumothorax+AND+open+access[filter]

# Extract images from articles
https://www.ncbi.nlm.nih.gov/pmc/articles/PMC[PMCID]/bin/
```

**Pros:**
- Authoritative (peer-reviewed journals)
- Open Access subset clearly marked
- Comprehensive coverage
- Free API access

**Cons:**
- Complex extraction (from articles)
- Variable image formats
- Need to parse XML/HTML
- Slower download process

**Priority:** 🟡 **Lower Priority** - Use for specific gaps after other sources

---

## Implementation Strategy

### Phase 1: OpenI Integration (Priority 1) - Today

**Target:** Emergency Medicine, Neurology, Respiratory (critical gaps)

**Steps:**
1. Create `scripts/download_openi.py`
2. Implement OpenI API search and download
3. Map taxonomy search terms to OpenI queries
4. Download 1,000-1,500 images (highest priority)

**Estimated Time:** 2-3 hours implementation + 1-2 hours download

**Expected Results:**
- Emergency Medicine: ~400 images (trauma, acute presentations)
- Neurology: ~500 images (stroke, brain imaging)
- Respiratory: ~300 images (chest X-rays, CT)

---

### Phase 2: HEAL Expansion (Priority 1) - Today

**Target:** Respiratory, Gastroenterology (fill existing gaps)

**Steps:**
1. Re-run HEAL downloads with higher `--images-per-topic` limits
2. Target respiratory: 300 images (currently 5)
3. Target gastrointestinal: 700 images (currently 5)

**Command:**
```bash
# Respiratory
python3 scripts/download_heal_comprehensive.py \
    --specialties respiratory \
    --images-per-topic 50 \
    --yes

# Gastrointestinal
python3 scripts/download_heal_comprehensive.py \
    --specialties gastrointestinal \
    --images-per-topic 80 \
    --yes
```

**Estimated Time:** 30 minutes implementation + 2-3 hours download

---

### Phase 3: Radiopaedia Scraper (Priority 2) - Tomorrow

**Target:** Neurology, Emergency, Obstetrics (high-quality cases)

**Steps:**
1. Create `scripts/download_radiopaedia.py`
2. Implement respectful web scraping (robots.txt compliant)
3. Rate limiting: 5-10 seconds between requests
4. Download 500-800 images

**Estimated Time:** 3-4 hours implementation + 2-3 hours download

---

### Phase 4: MedPix & Wikimedia (Priority 3) - This Week

**Target:** Endocrinology, Paediatrics, Obstetrics (fill remaining gaps)

**Steps:**
1. Create `scripts/download_medpix.py`
2. Create `scripts/download_wikimedia.py`
3. Download 500-800 images

**Estimated Time:** 2-3 hours per source

---

### Phase 5: PubMed Central (Priority 4) - Next Week

**Target:** Psychiatry, remaining gaps (final 10-15%)

**Steps:**
1. Create `scripts/download_pmc.py`
2. Extract images from Open Access articles
3. Download 300-500 images

**Estimated Time:** 4-5 hours (complex extraction)

---

## Expected Timeline

### Today (2026-02-06)
- ✅ **Phase 1:** OpenI implementation (emergency, neurology, respiratory)
- ✅ **Phase 2:** HEAL expansion (respiratory, GI)
- **Target:** +2,000 images (846 → 2,846 = 45% complete)

### Tomorrow (2026-02-07)
- **Phase 3:** Radiopaedia scraper (neurology, emergency, obs)
- **Target:** +800 images (2,846 → 3,646 = 58% complete)

### This Week (2026-02-08 to 2026-02-10)
- **Phase 4:** MedPix + Wikimedia (endocrinology, paediatrics)
- **Target:** +1,500 images (3,646 → 5,146 = 82% complete)

### Next Week (2026-02-11 onwards)
- **Phase 5:** PubMed Central (psychiatry, final gaps)
- **Phase 6:** Quality review and gap filling
- **Target:** 6,300 images (100% complete)

---

## Technical Implementation

### OpenI Downloader Template

```python
#!/usr/bin/env python3
"""
Download images from OpenI (Open Access Biomedical Image Search)
NIH National Library of Medicine
"""

import requests
import json
from pathlib import Path
from typing import List, Dict
import time

class OpenIDownloader:
    """Download medical images from OpenI"""

    BASE_URL = "https://openi.nlm.nih.gov"
    SEARCH_API = f"{BASE_URL}/api/search"
    IMAGE_BASE = f"{BASE_URL}/imgs/512"

    def __init__(self, output_dir: str = "data/medical_images/openi",
                 rate_limit: float = 2.0):
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AMC-Medical-Education/1.0 (Educational Use)'
        })

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """Search OpenI for images"""
        params = {
            'query': query,
            'm': max_results,
            'it': 'x'  # XML format
        }

        response = self.session.get(self.SEARCH_API, params=params)
        response.raise_for_status()

        # Parse XML response
        # Extract image IDs and metadata
        # Return list of image dicts

        time.sleep(self.rate_limit)
        return []

    def download_image(self, image_id: str, output_path: Path) -> bool:
        """Download single image from OpenI"""
        url = f"{self.IMAGE_BASE}/{image_id}.png"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)

            time.sleep(self.rate_limit)
            return True
        except Exception as e:
            print(f"Error downloading {image_id}: {e}")
            return False
```

---

## Success Criteria

### Minimum Viable (MVP)
- 3,000 images (48% of target)
- All 11 specialties covered (at least 50 images each)
- Emergency medicine, neurology fully covered

### Target (Production Ready)
- 6,300 images (100% of target)
- All specialties well-covered (5-8 images per taxonomy node)
- High-quality images for high-AMC-relevance topics

### Stretch Goal
- 8,000+ images (127% of target)
- Redundancy for high-priority topics
- Multiple image types per topic (X-ray, CT, MRI, clinical photos)

---

## Next Steps

**Immediate Actions:**
1. ✅ Implement OpenI downloader (`scripts/download_openi.py`)
2. ✅ Download emergency medicine images from OpenI (~400 images)
3. ✅ Download neurology images from OpenI (~500 images)
4. ✅ Re-run HEAL for respiratory/GI with higher limits (~1,000 images)

**Command to Execute:**
```bash
# Create and run OpenI downloader
python3 scripts/download_openi.py \
    --specialties emergency_medicine neurology respiratory \
    --images-per-topic 10 \
    --output data/medical_images/openi

# HEAL expansion
python3 scripts/download_heal_comprehensive.py \
    --specialties respiratory gastrointestinal \
    --images-per-topic 100 \
    --yes
```

---

**Generated:** 2026-02-06 17:15
**Current Status:** 846 images (13.4%)
**Target:** 6,300 images (100%)
**Priority:** OpenI + HEAL expansion today (+2,000 images)
