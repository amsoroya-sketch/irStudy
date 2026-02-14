# HEAL Integration Guide
**Downloading and Integrating HEAL Images into AMC Exam Preparation System**

**Date:** 2026-02-03
**Version:** 1.0
**Repository:** Health Education Assets Library (University of Utah)

---

## Table of Contents

1. [Overview](#overview)
2. [Manual Download (Recommended for Phase 1)](#manual-download-recommended-for-phase-1)
3. [Semi-Automated Download](#semi-automated-download)
4. [OAI-PMH Metadata Harvesting](#oai-pmh-metadata-harvesting)
5. [Integration with Existing System](#integration-with-existing-system)
6. [Citation Compliance](#citation-compliance)

---

## Overview

### About HEAL

- **Full Name:** Health Education Assets Library
- **Host:** University of Utah, J. Willard Marriott Digital Library
- **Size:** 22,000+ medical education resources
- **Content:** Images, videos, animations, audio files
- **License:** CC-BY-NC (Creative Commons Attribution Non-Commercial)
- **URL:** https://collections.lib.utah.edu/ (filter by HEAL collection)

### Key Collections for AMC Exam Prep

| Collection | Size | AMC Relevance | Priority |
|------------|------|---------------|----------|
| **Knowledge Weavers Dermatology** | 1,000+ | ⭐⭐⭐⭐⭐ (5/5) | HIGH |
| **Pathology Education (PEIR)** | 5,000+ | ⭐⭐⭐⭐ (4/5) | MEDIUM |
| **Poja Histology Collection** | 3,000+ | ⭐⭐⭐⭐ (4/5) | MEDIUM |
| **Knowledge Weavers ECG** | 500+ | ⭐⭐⭐⭐⭐ (5/5) | HIGH |
| **Albert Einstein Hematology** | 300+ | ⭐⭐⭐⭐ (4/5) | MEDIUM |

---

## Manual Download (Recommended for Phase 1)

**Best for:** Curating high-quality images (50-100 images)
**Time:** 2-3 hours
**Control:** Full quality control

### Step 1: Browse HEAL Collection

```bash
# Visit HEAL collection
open https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal
```

**Or browse by specific collection:**
- Dermatology: Search "dermatology" + filter HEAL
- ECG: Search "ECG" or "electrocardiogram" + filter HEAL
- Histology: Search "histology" + filter HEAL

### Step 2: Download Images

**For each image:**

1. **Click thumbnail** to open full record
2. **Review metadata:**
   - Title
   - Description
   - Subject tags
   - Rights statement
   - Collection name
3. **Download image:**
   - Click "Download" or right-click → Save Image As
   - Save to: `data/medical_images/heal/<collection>/<filename>.jpg`
4. **Record metadata:**
   - HEAL ID (from URL: `/ark:/...` identifier)
   - Title
   - Description
   - Collection
   - Citation

### Step 3: Metadata Capture Template

Create `data/medical_images/heal/download_log.csv`:

```csv
heal_id,filename,title,description,collection,subject,rights,downloaded_date
87278/xv89712,melanoma_001.jpg,"Melanoma - Clinical Presentation","Irregular pigmented lesion",Knowledge Weavers Dermatology,"melanoma;skin cancer;dermatology",CC-BY-NC,2026-02-03
```

**Manual download script helper:**

```bash
#!/bin/bash
# Helper script for manual HEAL downloads

# Create directory structure
mkdir -p data/medical_images/heal/{dermatology,ecg,histology,pathology,hematology}

echo "HEAL Manual Download Helper"
echo "=========================="
echo ""
echo "1. Visit: https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal"
echo "2. Search for topic (e.g., 'melanoma', 'ECG', 'pneumonia')"
echo "3. For each image:"
echo "   - Click thumbnail"
echo "   - Note HEAL ID from URL (e.g., ark:/87278/xv89712)"
echo "   - Click 'Download' button"
echo "   - Save to: data/medical_images/heal/<collection>/"
echo "   - Record metadata in download_log.csv"
echo ""
echo "Target for Phase 1 Pilot: 50 images"
echo "Recommended breakdown:"
echo "  - Dermatology: 30 images (common skin conditions)"
echo "  - ECG: 10 images (arrhythmias, MI patterns)"
echo "  - Histology: 10 images (pathology slides)"
echo ""
echo "Estimated time: 2-3 hours"
```

---

## Semi-Automated Download

**Best for:** Downloading 100-500 images with some automation
**Time:** 1 hour setup + automated downloading
**Control:** Good balance of speed and quality

### HEAL Downloader Script

Create `scripts/download_heal_images.py`:

```python
#!/usr/bin/env python3
"""
Download images from HEAL collection via web scraping

Requirements:
    pip3 install requests beautifulsoup4 tqdm selenium

Usage:
    python3 scripts/download_heal_images.py \
        --query "melanoma" \
        --collection dermatology \
        --max-images 30
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from tqdm import tqdm
import argparse
import csv

class HEALDownloader:
    """Download images from HEAL collection"""

    def __init__(self):
        self.base_url = "https://collections.lib.utah.edu"
        self.heal_filter = "facet_setname_s=ehsl_heal"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot - irStudy AMC Prep)'
        })

    def search_collection(self, query, max_results=50):
        """Search HEAL collection"""
        search_url = f"{self.base_url}/search"
        params = {
            'q': query,
            'facet_setname_s': 'ehsl_heal',
            'rows': max_results
        }

        try:
            response = self.session.get(search_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all result items
            results = []
            for item in soup.find_all('div', class_='search-result'):
                # Extract ARK identifier and title
                link = item.find('a', href=True)
                if link and '/ark:/' in link['href']:
                    ark_id = link['href'].split('/ark:/')[-1].split('/')[0]
                    title = link.text.strip()

                    results.append({
                        'heal_id': f"ark:/87278/{ark_id}",
                        'url': self.base_url + link['href'],
                        'title': title
                    })

            print(f"Found {len(results)} results for '{query}'")
            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def download_item(self, item_url, output_dir):
        """Download single item with metadata"""
        try:
            response = self.session.get(item_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract metadata
            metadata = {
                'url': item_url,
                'title': self._extract_meta(soup, 'title'),
                'description': self._extract_meta(soup, 'description'),
                'subject': self._extract_meta(soup, 'subject'),
                'collection': self._extract_meta(soup, 'collection'),
                'rights': self._extract_meta(soup, 'rights'),
                'format': self._extract_meta(soup, 'format'),
                'date': self._extract_meta(soup, 'date'),
            }

            # Find download link
            download_link = soup.find('a', text=lambda t: t and 'Download' in t)
            if not download_link:
                # Try finding image directly
                img_tag = soup.find('img', class_='item-image')
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
                    if not img_url.startswith('http'):
                        img_url = self.base_url + img_url
                else:
                    print(f"  No image found for {item_url}")
                    return None
            else:
                img_url = download_link['href']
                if not img_url.startswith('http'):
                    img_url = self.base_url + img_url

            # Download image
            img_response = self.session.get(img_url, timeout=30)
            if img_response.status_code == 200:
                # Generate filename from ARK ID
                ark_id = item_url.split('/ark:/')[-1].replace('/', '_')
                filename = f"heal_{ark_id}.jpg"
                filepath = Path(output_dir) / filename

                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

                metadata['filepath'] = str(filepath)
                metadata['filename'] = filename
                metadata['heal_id'] = f"ark:/{item_url.split('/ark:/')[-1]}"
                metadata['file_size_kb'] = len(img_response.content) // 1024

                return metadata

        except Exception as e:
            print(f"  Download error: {e}")
            return None

    def _extract_meta(self, soup, field_name):
        """Extract metadata field"""
        # Try multiple patterns
        patterns = [
            lambda: soup.find('dt', text=lambda t: t and field_name.lower() in t.lower()),
            lambda: soup.find('meta', {'name': field_name}),
            lambda: soup.find('meta', {'property': f'og:{field_name}'})
        ]

        for pattern in patterns:
            try:
                elem = pattern()
                if elem:
                    if elem.name == 'dt':
                        dd = elem.find_next_sibling('dd')
                        if dd:
                            return dd.text.strip()
                    elif elem.name == 'meta':
                        return elem.get('content', '')
            except:
                continue

        return None

def main():
    parser = argparse.ArgumentParser(
        description='Download images from HEAL collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download 30 dermatology images
  python3 scripts/download_heal_images.py \\
      --query "melanoma OR psoriasis OR eczema" \\
      --collection dermatology \\
      --max-images 30

  # Download ECG images
  python3 scripts/download_heal_images.py \\
      --query "electrocardiogram OR ECG" \\
      --collection ecg \\
      --max-images 10
        '''
    )

    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--collection', required=True, help='Collection name (dermatology, ecg, histology)')
    parser.add_argument('--max-images', type=int, default=50, help='Maximum images to download')
    parser.add_argument('--output', default='data/medical_images/heal', help='Output directory')

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"HEAL Collection Downloader")
    print(f"{'='*60}\n")

    # Create output directory
    output_dir = Path(args.output) / args.collection
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize downloader
    downloader = HEALDownloader()

    # Search collection
    print(f"Searching HEAL for: '{args.query}'")
    results = downloader.search_collection(args.query, args.max_images)

    if not results:
        print("No results found")
        return

    # Download items
    downloaded = []
    for item in tqdm(results, desc="Downloading"):
        metadata = downloader.download_item(item['url'], output_dir)
        if metadata:
            downloaded.append(metadata)

        # Rate limiting (be respectful)
        time.sleep(2)

    # Save metadata
    if downloaded:
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(downloaded, f, indent=2)

        # Save CSV for easy review
        csv_file = output_dir / 'metadata.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=downloaded[0].keys())
            writer.writeheader()
            writer.writerows(downloaded)

        print(f"\n{'='*60}")
        print(f"Download Complete")
        print(f"{'='*60}")
        print(f"Downloaded: {len(downloaded)} images")
        print(f"Location: {output_dir}")
        print(f"Metadata: {metadata_file}")

if __name__ == '__main__':
    main()
```

Make it executable:

```bash
chmod +x scripts/download_heal_images.py
```

**Usage examples:**

```bash
# Dermatology (30 images)
python3 scripts/download_heal_images.py \
    --query "melanoma OR psoriasis OR eczema OR dermatitis" \
    --collection dermatology \
    --max-images 30

# ECG (10 images)
python3 scripts/download_heal_images.py \
    --query "electrocardiogram OR ECG OR arrhythmia" \
    --collection ecg \
    --max-images 10

# Histology (10 images)
python3 scripts/download_heal_images.py \
    --query "histology OR microscopy" \
    --collection histology \
    --max-images 10
```

---

## OAI-PMH Metadata Harvesting

**Best for:** Bulk metadata extraction (for large-scale operations)
**Complexity:** Advanced
**Note:** Provides metadata only, not image files

### OAI-PMH Endpoint

University of Utah provides OAI-PMH harvesting:

```bash
# OAI-PMH endpoint (typical structure)
https://collections.lib.utah.edu/oai-pmh?verb=Identify
```

### Harvest Metadata Script

```python
#!/usr/bin/env python3
"""
Harvest HEAL metadata via OAI-PMH

Requirements:
    pip3 install sickle

Usage:
    python3 scripts/harvest_heal_metadata.py
"""

from sickle import Sickle
import json
from datetime import datetime

# Initialize OAI-PMH client
sickle = Sickle('https://collections.lib.utah.edu/oai-pmh')

# List all sets (to find HEAL set spec)
print("Available sets:")
for s in sickle.ListSets():
    print(f"  {s.setSpec}: {s.setName}")

# Harvest HEAL collection records
# (Replace 'ehsl_heal' with actual set spec if different)
records = sickle.ListRecords(
    metadataPrefix='oai_dc',
    set='ehsl_heal',
    ignore_deleted=True
)

heal_metadata = []
for record in records:
    metadata = record.metadata

    heal_metadata.append({
        'identifier': record.header.identifier,
        'title': metadata.get('title', [None])[0],
        'description': metadata.get('description', [None])[0],
        'subject': metadata.get('subject', []),
        'type': metadata.get('type', []),
        'rights': metadata.get('rights', [None])[0],
        'format': metadata.get('format', []),
        'date': metadata.get('date', [None])[0],
    })

# Save metadata
output_file = 'data/heal_oai_metadata.json'
with open(output_file, 'w') as f:
    json.dump(heal_metadata, f, indent=2)

print(f"Harvested {len(heal_metadata)} records")
print(f"Saved to: {output_file}")
```

**Note:** OAI-PMH gives you metadata but NOT image files. You still need to download images separately using ARK identifiers from the metadata.

---

## Integration with Existing System

### Step 1: Download Images (Choose Method)

```bash
# Option A: Manual (recommended for Phase 1)
# Follow "Manual Download" section above
# Target: 50 images

# Option B: Semi-automated
python3 scripts/download_heal_images.py \
    --query "dermatology" \
    --collection dermatology \
    --max-images 50
```

### Step 2: Process Metadata

Use your existing metadata processor with HEAL-specific enrichment:

```bash
# Process downloaded HEAL images
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/heal_metadata.json
```

**Enrich metadata for HEAL:**

```python
# scripts/enrich_heal_metadata.py

import json
from pathlib import Path

def enrich_heal_metadata(metadata_file):
    """Add HEAL-specific fields to metadata"""

    with open(metadata_file) as f:
        images = json.load(f)

    for img in images:
        # Source
        img['source'] = 'heal'

        # License (HEAL uses CC-BY-NC)
        img['license'] = 'CC-BY-NC'

        # Citation format
        heal_id = img.get('external_id') or img.get('heal_id')
        img['citation'] = f"(HEAL #{heal_id}, University of Utah, CC-BY-NC, accessed 2026-02-03)"

        # AMC relevance (default 4, manually review)
        if not img.get('amc_relevance'):
            img['amc_relevance'] = 4  # High relevance for curated educational content

        # Add tags based on collection
        collection = img.get('specialty') or img.get('collection', '').lower()
        if 'dermatology' in collection:
            if not img.get('tags'):
                img['tags'] = ['dermatology', 'skin', 'clinical-examination']
        elif 'ecg' in collection:
            if not img.get('tags'):
                img['tags'] = ['cardiology', 'electrocardiogram', 'interpretation']
        elif 'histology' in collection:
            if not img.get('tags'):
                img['tags'] = ['pathology', 'microscopy', 'histology']

    # Save enriched metadata
    with open(metadata_file, 'w') as f:
        json.dump(images, f, indent=2)

    print(f"✓ Enriched {len(images)} HEAL images")

# Usage
enrich_heal_metadata('data/heal_metadata.json')
```

### Step 3: Upload to CDN

```bash
# Same process as other repositories
export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-key>"
export R2_SECRET_ACCESS_KEY="<your-secret>"

python3 scripts/upload_to_cdn.py \
    --source data/medical_images/heal \
    --bucket irstudy-medical-images \
    --metadata data/heal_metadata.json \
    --cdn-url https://cdn.irstudy.com
```

### Step 4: Index in Database

```bash
# Index HEAL images alongside MedPix, NIH, etc.
export DATABASE_URL="postgresql://user:pass@localhost/irstudy"

python3 scripts/index_images.py \
    --metadata data/heal_metadata.json
```

### Step 5: Query via Multimodal RAG

**Python API:**

```python
from src.services.multimodal_rag_service import MultimodalRAGService

rag = MultimodalRAGService()

# Query for dermatology images
result = rag.query_with_images(
    query="melanoma clinical presentation",
    specialty="dermatology",
    include_images=True,
    max_images=2
)

# Filter specifically for HEAL images
heal_images = [
    img for img in result['images']
    if img['source'] == 'heal'
]
```

**SQL Query:**

```sql
-- Find HEAL dermatology images
SELECT
    external_id,
    title,
    diagnosis,
    cdn_url,
    citation_text,
    amc_relevance
FROM medical_images
WHERE source = 'heal'
  AND specialty = 'dermatology'
  AND diagnosis ILIKE '%melanoma%'
ORDER BY amc_relevance DESC
LIMIT 10;
```

---

## Citation Compliance

### HEAL Citation Format

**Official format:**
```markdown
Image Title. Health Education Assets Library (HEAL).
University of Utah, J. Willard Marriott Digital Library.
ARK: [ARK identifier]. License: CC-BY-NC.
```

**Simplified format for your system:**
```markdown
(HEAL #[ID], University of Utah, CC-BY-NC, accessed YYYY-MM-DD)

Examples:
(HEAL #87278/xv89712, University of Utah, CC-BY-NC, accessed 2026-02-03)
(HEAL Dermatology Collection, University of Utah, CC-BY-NC)
```

### Integration with Existing RAG Citations

**MCQ with combined citations:**

```python
mcq = {
    'question': {
        'scenario': '''
A 65-year-old man presents with an irregular pigmented lesion on his back.
He reports the lesion has changed in size and color over 6 months.
Dermoscopy image shown below.
        ''',
        'image': {
            'cdn_url': 'https://cdn.irstudy.com/images/heal/dermatology/melanoma_001.jpg',
            'caption': 'Dermoscopy showing irregular borders and color variation',
            'citation': '(HEAL #87278/xv89712, University of Utah, CC-BY-NC)'
        },
        'stem': 'What is the most appropriate next step?',
        'options': {
            'A': 'Reassure and review in 3 months',
            'B': 'Excision biopsy',  # Correct
            'C': 'Cryotherapy',
            'D': 'Topical steroid cream'
        }
    },
    'correct_answer': 'B',
    'explanation': '''
The dermoscopy findings suggest melanoma (irregular borders, color variation).
Excision biopsy is required for definitive diagnosis and staging.

Melanoma management follows Australian guidelines (eTG Dermatology, Section 5.2.1).
    ''',
    'references': [
        {
            'type': 'image',
            'source': 'heal',
            'id': '87278/xv89712',
            'citation': '(HEAL #87278/xv89712, University of Utah, CC-BY-NC)',
            'license': 'CC-BY-NC'
        },
        {
            'type': 'text',
            'title': 'Therapeutic Guidelines: Dermatology',
            'section': '5.2.1',
            'year': '2024',
            'citation': '(Therapeutic Guidelines: Dermatology, Section 5.2.1, 2024)',
            'rag_confidence': 0.89
        }
    ]
}
```

### License Compliance Check

```python
# scripts/validate_heal_license.py

def validate_heal_compliance(mcq):
    """
    Validate HEAL license compliance

    CC-BY-NC requirements:
    - Attribution: ✅ Required (cite source)
    - Non-commercial: ⚠️ Educational use OK, but verify platform is non-commercial
    - Derivatives: ✅ Allowed with same license
    """

    heal_images = [
        ref for ref in mcq['references']
        if ref.get('source') == 'heal'
    ]

    for img in heal_images:
        # Check attribution present
        if not img.get('citation'):
            raise ValueError(f"HEAL image missing citation: {img.get('id')}")

        # Check license field
        if img.get('license') != 'CC-BY-NC':
            raise ValueError(f"HEAL image incorrect license: {img.get('license')}")

        # Check citation format
        citation = img['citation']
        if 'HEAL' not in citation or 'University of Utah' not in citation:
            raise ValueError(f"HEAL citation incomplete: {citation}")

    return True
```

---

## Complete Workflow Example

### Phase 1 Pilot: Download 50 HEAL Images

```bash
# Step 1: Manual download (2-3 hours)
# Visit: https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal
# Search "melanoma" → Download 15 images
# Search "psoriasis" → Download 10 images
# Search "eczema" → Download 10 images
# Search "electrocardiogram" → Download 10 images
# Search "histology" → Download 5 images
# Save all to: data/medical_images/heal/<collection>/

# Step 2: Process metadata
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/heal_metadata.json

# Step 3: Enrich HEAL-specific fields
python3 scripts/enrich_heal_metadata.py \
    --metadata data/heal_metadata.json

# Step 4: Upload to CDN
python3 scripts/upload_to_cdn.py \
    --source data/medical_images/heal \
    --bucket irstudy-medical-images \
    --metadata data/heal_metadata.json

# Step 5: Index in database
python3 scripts/index_images.py \
    --metadata data/heal_metadata.json

# Step 6: Verify
psql $DATABASE_URL -c "
    SELECT COUNT(*), specialty
    FROM medical_images
    WHERE source = 'heal'
    GROUP BY specialty;
"
```

### Expected Output

```
  count | specialty
--------+-------------
     35 | dermatology
     10 | cardiology
      5 | pathology

Total: 50 HEAL images indexed
```

---

## Summary

### Available Methods

| Method | Speed | Quality Control | Complexity | Recommended For |
|--------|-------|-----------------|------------|-----------------|
| **Manual Download** | Slow (2-3 hrs) | Excellent | Low | Phase 1 Pilot |
| **Semi-Automated** | Medium (1 hr) | Good | Medium | Phase 2 Scaling |
| **OAI-PMH** | Fast | N/A (metadata only) | High | Research/Analysis |

### Phase 1 Recommendation

✅ **Use Manual Download**
- Download 50 high-quality images
- Full control over selection
- Complete metadata capture
- 2-3 hours total time
- Perfect for pilot validation

### Integration Checklist

- [ ] Download 50 HEAL images (dermatology priority)
- [ ] Process metadata with `process_image_metadata.py`
- [ ] Enrich with HEAL-specific fields (CC-BY-NC license, citation)
- [ ] Upload to CDN with thumbnails
- [ ] Index in PostgreSQL database
- [ ] Test multimodal RAG queries
- [ ] Validate citation format (QA-003)
- [ ] Generate 5 MCQs using HEAL images
- [ ] Verify license compliance

---

## Next Steps

1. **Start manual download** (today):
   ```bash
   open https://collections.lib.utah.edu/search?facet_setname_s=ehsl_heal
   ```

2. **Process and upload** (tomorrow):
   ```bash
   python3 scripts/process_image_metadata.py --source data/medical_images/heal
   python3 scripts/upload_to_cdn.py --source data/medical_images/heal ...
   ```

3. **Test integration** (end of week):
   - Query via multimodal RAG
   - Generate MCQs with HEAL images
   - Validate citations

---

**Document Version:** 1.0
**Date:** 2026-02-03
**Status:** Ready for Implementation
**Estimated Time:** 3-4 hours for complete HEAL integration
