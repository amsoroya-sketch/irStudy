# Medical Image Dataset Download Guide
**AMC Clinical Exam Preparation - irStudy Project**

**Date:** 2026-02-03
**Version:** 1.0

---

## Table of Contents

1. [Quick Start - Download Scripts](#quick-start---download-scripts)
2. [NIH/NLM Datasets (LHC Downloads)](#nihnlm-datasets-lhc-downloads)
3. [MedPix Database](#medpix-database)
4. [Other Recommended Repositories](#other-recommended-repositories)
5. [Automated Download Scripts](#automated-download-scripts)
6. [Post-Download Processing](#post-download-processing)

---

## Quick Start - Download Scripts

### Prerequisites

```bash
# Install required tools
sudo apt-get update
sudo apt-get install -y wget curl unzip python3 python3-pip

# Install Python dependencies
pip3 install requests beautifulsoup4 selenium tqdm
```

### Download All Phase 1 Datasets (Automated)

```bash
# Run the master download script
cd /home/dev/Development/irStudy
chmod +x scripts/download_medical_images.sh
./scripts/download_medical_images.sh --phase 1

# This will download:
# - NIH Chest X-Ray Dataset (100+ images sample)
# - Malaria Screener Dataset (for pathology examples)
# - MedPix sample cases (50 cases via manual API)
```

---

## NIH/NLM Datasets (LHC Downloads)

**Source:** https://lhncbc.nlm.nih.gov/LHC-downloads/downloads.html

### 1. NIH Chest X-Ray Dataset

**Best for:** Radiology MCQs, chest X-ray interpretation

**Download Method:**

```bash
# Create directory
mkdir -p data/medical_images/nih_chest_xray
cd data/medical_images/nih_chest_xray

# Option A: Direct download from NIH Box
# Visit: https://nihcc.app.box.com/v/ChestXray-NIHCC
# Download files manually (requires Box account - free)

# Option B: Kaggle dataset (easier)
pip3 install kaggle

# Setup Kaggle credentials
# 1. Get API token from https://www.kaggle.com/settings
# 2. Place in ~/.kaggle/kaggle.json

kaggle datasets download -d nih-chest-xrays/data
unzip data.zip
```

**Dataset Details:**
- **Size:** 112,120 chest X-ray images (42 GB compressed)
- **Format:** 1024x1024 PNG
- **Labels:** 14 thoracic disease labels
- **License:** CC0 (Public Domain)
- **Citation:** Wang et al. (2017), ChestX-ray8 Database

**For Pilot Phase 1 (100 images sample):**

```bash
# Download sample subset only
python3 << 'EOF'
import os
import shutil
from pathlib import Path

# Assuming full dataset downloaded
source_dir = Path("data/medical_images/nih_chest_xray/images")
sample_dir = Path("data/medical_images/nih_chest_xray_sample")
sample_dir.mkdir(exist_ok=True)

# Select first 100 images
for i, img_file in enumerate(source_dir.glob("*.png")):
    if i >= 100:
        break
    shutil.copy(img_file, sample_dir / img_file.name)
    print(f"Copied {i+1}/100: {img_file.name}")

print("Sample dataset created!")
EOF
```

---

### 2. Malaria Screener Dataset

**Best for:** Pathology/microscopy examples, infectious disease MCQs

**Download Method:**

```bash
# Create directory
mkdir -p data/medical_images/malaria
cd data/medical_images/malaria

# Download from NLM datasheet
wget https://lhncbc.nlm.nih.gov/LHC-downloads/dataset/NLM-MalariaDataset.zip

# Unzip
unzip NLM-MalariaDataset.zip

# Alternative: Kaggle dataset
kaggle datasets download -d iarunava/cell-images-for-detecting-malaria
unzip cell-images-for-detecting-malaria.zip
```

**Dataset Details:**
- **Size:** 27,558 cell images
- **Components:**
  - P. falciparum: 150 thick smear slides
  - P. vivax: 171 thin smears
  - Uninfected cells: control samples
- **Format:** PNG images (microscopy)
- **License:** IRB-approved, de-identified (free for research/education)
- **Citation:** Rajaraman et al. (2018)

**Use Case for AMC:**
- Infectious disease MCQs (malaria diagnosis)
- Pathology interpretation practice
- Blood smear interpretation

---

### 3. Lung Segmentation Dataset

**Best for:** Advanced radiology, image processing examples

**Download Method:**

```bash
mkdir -p data/medical_images/lung_segmentation
cd data/medical_images/lung_segmentation

# Download lung masks (Indiana dataset)
wget https://lhncbc.nlm.nih.gov/LHC-downloads/downloads/indiana.zip
unzip indiana.zip

# Download lung segmentation tool
wget https://lhncbc.nlm.nih.gov/LHC-downloads/downloads/ChestXRayAtlasSeg.zip
unzip ChestXRayAtlasSeg.zip
```

**Dataset Details:**
- **Size:** 55 frontal contrast-enhanced chest X-rays
- **Format:** DICOM, TIFF, PNG, BMP, JPEG
- **Annotations:** Lung boundary masks
- **License:** Free with citation
- **Citation:** Candemir et al. (2014)

**Use Case for AMC:**
- Less relevant for clinical exam prep (more for AI research)
- Could use for advanced radiology questions
- **Priority:** LOW for Phase 1

---

## MedPix Database

**Best for:** Clinical case-based learning (TOP PRIORITY)

**Source:** https://medpix.nlm.nih.gov/

### Registration (Required)

```bash
# 1. Visit MedPix registration page
open https://medpix.nlm.nih.gov/register

# 2. Fill out registration form (free)
# - Name, email, institution
# - Purpose: Educational / Research
# - Takes 2-3 minutes

# 3. Verify email
# - Check inbox for verification link
# - Click to activate account
```

### Download Methods

#### Option A: Manual Download (Recommended for Pilot)

**Best for:** Curating high-quality cases

```bash
# 1. Login to MedPix
# 2. Search by specialty:
#    - "pneumonia" (radiology)
#    - "melanoma" (dermatology)
#    - "myocardial infarction" (cardiology)

# 3. For each case:
#    - Click case number
#    - View images
#    - Right-click → Save Image As
#    - Save to: data/medical_images/medpix/<specialty>/

# 4. Record metadata:
#    - Case ID
#    - Diagnosis
#    - Patient demographics
#    - Clinical history
```

**Pilot Phase 1 Target: 100 cases**
- Cardiology: 20 cases (MI, HF, arrhythmias)
- Dermatology: 20 cases (melanoma, psoriasis, eczema)
- Pulmonology: 20 cases (pneumonia, PE, COPD)
- Neurology: 20 cases (stroke, seizures, headache)
- Emergency: 20 cases (trauma, acute abdomen)

---

#### Option B: API Download (Automated)

**MedPix RSNA MIRC API**

```python
# scripts/download_medpix_api.py

import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path

class MedPixDownloader:
    """
    Download MedPix cases via RSNA MIRC API

    Note: MedPix doesn't have a public REST API,
    so this uses web scraping (respectful rate limiting)
    """

    def __init__(self, username, password):
        self.base_url = "https://medpix.nlm.nih.gov"
        self.session = requests.Session()
        self.login(username, password)

    def login(self, username, password):
        """Login to MedPix"""
        login_url = f"{self.base_url}/login"
        payload = {
            'username': username,
            'password': password
        }
        response = self.session.post(login_url, data=payload)
        if response.status_code != 200:
            raise Exception("Login failed")
        print("✓ Logged in to MedPix")

    def search_cases(self, query, max_results=20):
        """Search for cases by keyword"""
        search_url = f"{self.base_url}/search"
        params = {
            'query': query,
            'limit': max_results
        }
        response = self.session.get(search_url, params=params)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Parse case IDs from search results
        case_ids = []
        for link in soup.find_all('a', href=True):
            if '/case/' in link['href']:
                case_id = link['href'].split('/case/')[-1]
                case_ids.append(case_id)

        return case_ids[:max_results]

    def download_case(self, case_id, output_dir):
        """Download a single case with metadata"""
        case_url = f"{self.base_url}/case/{case_id}"
        response = self.session.get(case_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract metadata
        metadata = {
            'case_id': case_id,
            'title': soup.find('h1').text.strip() if soup.find('h1') else 'Unknown',
            'diagnosis': self._extract_field(soup, 'Diagnosis'),
            'modality': self._extract_field(soup, 'Modality'),
            'patient_age': self._extract_field(soup, 'Age'),
            'patient_sex': self._extract_field(soup, 'Sex'),
            'clinical_history': self._extract_field(soup, 'History'),
            'findings': self._extract_field(soup, 'Findings'),
            'citation': f"(MedPix Case #{case_id}, Public Domain)",
            'source_url': case_url
        }

        # Download images
        image_urls = []
        for img in soup.find_all('img', class_='case-image'):
            if img.get('src'):
                img_url = self.base_url + img['src']
                image_urls.append(img_url)

        # Save images
        case_dir = Path(output_dir) / f"case_{case_id}"
        case_dir.mkdir(parents=True, exist_ok=True)

        for i, img_url in enumerate(image_urls):
            img_response = self.session.get(img_url)
            img_path = case_dir / f"image_{i+1}.jpg"
            with open(img_path, 'wb') as f:
                f.write(img_response.content)
            print(f"  Downloaded: {img_path}")

        # Save metadata
        metadata_path = case_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        return metadata

    def _extract_field(self, soup, field_name):
        """Extract metadata field from case page"""
        field_elem = soup.find(text=lambda t: t and field_name in t)
        if field_elem:
            parent = field_elem.parent
            value = parent.find_next_sibling()
            if value:
                return value.text.strip()
        return None

# Usage
if __name__ == '__main__':
    # Get credentials
    import getpass
    username = input("MedPix username: ")
    password = getpass.getpass("MedPix password: ")

    # Initialize downloader
    downloader = MedPixDownloader(username, password)

    # Download cases by specialty
    specialties = {
        'cardiology': ['myocardial infarction', 'heart failure', 'arrhythmia'],
        'dermatology': ['melanoma', 'psoriasis', 'eczema'],
        'pulmonology': ['pneumonia', 'pulmonary embolism', 'COPD'],
        'neurology': ['stroke', 'seizure', 'meningitis'],
        'emergency': ['trauma', 'acute abdomen', 'fracture']
    }

    for specialty, queries in specialties.items():
        print(f"\n=== Downloading {specialty.upper()} cases ===")
        output_dir = f"data/medical_images/medpix/{specialty}"

        for query in queries:
            print(f"\nSearching: {query}")
            case_ids = downloader.search_cases(query, max_results=7)

            for case_id in case_ids:
                print(f"Downloading case {case_id}...")
                try:
                    downloader.download_case(case_id, output_dir)
                except Exception as e:
                    print(f"  Error: {e}")

                # Rate limiting (be respectful)
                import time
                time.sleep(2)

    print("\n✓ Download complete!")
```

**Run the script:**

```bash
cd /home/dev/Development/irStudy
python3 scripts/download_medpix_api.py

# Enter your MedPix credentials when prompted
```

---

#### Option C: Bulk Export (Contact NLM)

For large-scale downloads (>1000 cases):

```bash
# Contact NLM for bulk access
# Email: medpix@mail.nih.gov
# Subject: Bulk dataset request for educational platform
# Include:
# - Project description (AMC exam preparation)
# - Number of cases needed
# - Use case (educational MCQ/OSCE generation)
# - Citation commitment

# NLM may provide:
# - FTP access to bulk dataset
# - CSV with metadata
# - Batch download scripts
```

---

## Other Recommended Repositories

### HEAL (Health Education Assets Library)

**Source:** https://library.med.utah.edu/heal/

**Download Method:**

```bash
# HEAL requires manual download (no bulk API)

# 1. Visit HEAL website
open https://library.med.utah.edu/heal/

# 2. Browse collections:
#    - Dermatology
#    - Histology
#    - Neuroscience
#    - Radiology

# 3. For each image:
#    - Click thumbnail
#    - Click "Download" button
#    - Save to: data/medical_images/heal/<collection>/

# 4. Record HEAL ID and citation from image page
```

**Pilot Phase 1 Target: 50 images**
- Dermatology: 30 images (common skin conditions)
- Histology: 10 images (pathology slides)
- Neuroscience: 10 images (brain anatomy)

**Metadata Template:**

```json
{
  "heal_id": "8234",
  "title": "Melanoma - Clinical Presentation",
  "collection": "Dermatology",
  "citation": "(HEAL #8234, University of Utah, CC-BY-NC, accessed 2026-02-03)",
  "license": "CC-BY-NC",
  "file_path": "data/medical_images/heal/dermatology/melanoma_8234.jpg"
}
```

---

### Z-Anatomy (3D Models)

**Source:** https://www.z-anatomy.com/

**No Download Required** - Use web iframe:

```html
<!-- Embed in React/HTML -->
<iframe
  src="https://z-anatomy.com/viewer?structure=rotator_cuff"
  width="1024"
  height="768"
  frameborder="0"
  allowfullscreen>
</iframe>
```

**For offline use (optional):**

```bash
# Download Unity desktop app
wget https://z-anatomy.itch.io/z-anatomy/download
# Or visit: https://z-anatomy.itch.io/z-anatomy

# Download Blender models (advanced)
git clone https://github.com/Z-Anatomy/Z-Anatomy-Blender.git
cd Z-Anatomy-Blender
# Requires Blender 3.0+
```

---

## Automated Download Scripts

### Master Download Script

Create `/home/dev/Development/irStudy/scripts/download_medical_images.sh`:

```bash
#!/bin/bash
# Master script to download all Phase 1 medical images

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="$PROJECT_DIR/data/medical_images"

echo "==================================="
echo "Medical Image Dataset Downloader"
echo "Phase 1: Pilot (150 images)"
echo "==================================="
echo ""

# Create directory structure
mkdir -p "$DATA_DIR"/{nih_chest_xray,malaria,medpix,heal}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo "Checking prerequisites..."
for cmd in wget curl unzip python3; do
    if ! command_exists $cmd; then
        echo "Error: $cmd not found. Please install it."
        exit 1
    fi
done
echo "✓ All prerequisites installed"
echo ""

# 1. Download NIH Chest X-Ray sample
echo "=== Step 1: NIH Chest X-Ray Dataset ==="
if [ ! -d "$DATA_DIR/nih_chest_xray_sample" ]; then
    echo "Note: Full dataset is 42GB. For pilot, we'll use Kaggle sample."
    echo "To download:"
    echo "  1. Install kaggle: pip3 install kaggle"
    echo "  2. Setup credentials: ~/.kaggle/kaggle.json"
    echo "  3. Run: kaggle datasets download -d nih-chest-xrays/sample"
    echo ""
    echo "Skipping automated download (requires Kaggle setup)"
else
    echo "✓ NIH Chest X-Ray sample already downloaded"
fi
echo ""

# 2. Download Malaria dataset
echo "=== Step 2: Malaria Screener Dataset ==="
if [ ! -f "$DATA_DIR/malaria/NLM-MalariaDataset.zip" ]; then
    echo "Downloading from NLM..."
    cd "$DATA_DIR/malaria"

    # Try direct download
    wget -O NLM-MalariaDataset.zip \
        "https://lhncbc.nlm.nih.gov/LHC-downloads/dataset/NLM-MalariaDataset.zip" \
        || echo "Warning: Direct download failed. Try manual download."

    if [ -f "NLM-MalariaDataset.zip" ]; then
        echo "Unzipping..."
        unzip -q NLM-MalariaDataset.zip
        echo "✓ Malaria dataset downloaded"
    fi
else
    echo "✓ Malaria dataset already downloaded"
fi
cd "$PROJECT_DIR"
echo ""

# 3. MedPix (requires credentials)
echo "=== Step 3: MedPix Cases ==="
echo "MedPix requires account credentials."
echo "Options:"
echo "  A) Manual download (recommended for pilot)"
echo "     - Visit: https://medpix.nlm.nih.gov/"
echo "     - Search and download 100 cases"
echo "  B) Automated download"
echo "     - Run: python3 scripts/download_medpix_api.py"
echo ""
read -p "Run automated MedPix download? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f "$SCRIPT_DIR/download_medpix_api.py" ]; then
        python3 "$SCRIPT_DIR/download_medpix_api.py"
    else
        echo "Error: download_medpix_api.py not found"
    fi
else
    echo "Skipping automated MedPix download"
fi
echo ""

# 4. HEAL (manual only)
echo "=== Step 4: HEAL Images ==="
echo "HEAL requires manual download."
echo "  1. Visit: https://library.med.utah.edu/heal/"
echo "  2. Browse Dermatology collection"
echo "  3. Download 50 images"
echo "  4. Save to: $DATA_DIR/heal/"
echo ""

# Summary
echo "==================================="
echo "Download Summary"
echo "==================================="
echo "Downloaded to: $DATA_DIR"
echo ""
echo "Next steps:"
echo "  1. Complete manual downloads (MedPix, HEAL)"
echo "  2. Process metadata: python3 scripts/process_image_metadata.py"
echo "  3. Upload to CDN: python3 scripts/upload_to_cdn.py"
echo "  4. Index in database: python3 scripts/index_images.py"
echo ""
echo "See DATASET_DOWNLOAD_GUIDE.md for detailed instructions."
```

Make it executable:

```bash
chmod +x scripts/download_medical_images.sh
```

---

## Post-Download Processing

### 1. Extract Metadata

Create `scripts/process_image_metadata.py`:

```python
#!/usr/bin/env python3
"""
Process downloaded medical images and extract metadata
"""

import json
import os
from pathlib import Path
from PIL import Image
import hashlib

def process_directory(source_dir, output_json):
    """Process all images in directory and extract metadata"""

    images = []
    source_path = Path(source_dir)

    for img_file in source_path.rglob("*.jpg"):
        try:
            # Open image to get dimensions
            with Image.open(img_file) as img:
                width, height = img.size

            # Calculate file hash for deduplication
            with open(img_file, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()

            # Extract metadata
            metadata = {
                'file_path': str(img_file.relative_to(source_path)),
                'file_name': img_file.name,
                'file_size_kb': img_file.stat().st_size // 1024,
                'width': width,
                'height': height,
                'file_hash': file_hash,
                'source': 'unknown',  # Set manually
                'external_id': None,   # Set manually
                'modality': None,      # Set manually
                'diagnosis': None,     # Set manually
                'citation': None       # Set manually
            }

            images.append(metadata)
            print(f"Processed: {img_file.name}")

        except Exception as e:
            print(f"Error processing {img_file}: {e}")

    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(images, f, indent=2)

    print(f"\n✓ Processed {len(images)} images")
    print(f"✓ Metadata saved to: {output_json}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Process medical image metadata')
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--output', default='image_metadata.json', help='Output JSON file')

    args = parser.parse_args()

    process_directory(args.source, args.output)
```

**Usage:**

```bash
# Process all downloaded images
python3 scripts/process_image_metadata.py \
    --source data/medical_images \
    --output data/image_metadata.json

# Manually enrich metadata (edit JSON file)
# Add: source, external_id, diagnosis, citation
```

---

### 2. Upload to CDN

Create `scripts/upload_to_cdn.py`:

```python
#!/usr/bin/env python3
"""
Upload medical images to Cloudflare R2 (S3-compatible)
"""

import boto3
from pathlib import Path
from tqdm import tqdm
import json
import os

def upload_to_r2(source_dir, bucket_name, metadata_json):
    """Upload images to Cloudflare R2"""

    # Configure R2 client (S3-compatible)
    s3 = boto3.client(
        's3',
        endpoint_url=os.getenv('R2_ENDPOINT_URL'),
        aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
        region_name='auto'
    )

    # Load metadata
    with open(metadata_json) as f:
        images = json.load(f)

    # Upload each image
    for img_meta in tqdm(images, desc="Uploading"):
        local_path = Path(source_dir) / img_meta['file_path']
        s3_key = f"images/{img_meta['file_path']}"

        try:
            # Upload with metadata
            s3.upload_file(
                str(local_path),
                bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': 'image/jpeg',
                    'Metadata': {
                        'source': img_meta.get('source', ''),
                        'external-id': img_meta.get('external_id', ''),
                        'diagnosis': img_meta.get('diagnosis', '')
                    }
                }
            )

            # Update CDN URL in metadata
            cdn_url = f"https://cdn.irstudy.com/{s3_key}"
            img_meta['cdn_url'] = cdn_url

        except Exception as e:
            print(f"Error uploading {local_path}: {e}")

    # Save updated metadata
    with open(metadata_json, 'w') as f:
        json.dump(images, f, indent=2)

    print(f"✓ Uploaded {len(images)} images to CDN")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload images to CDN')
    parser.add_argument('--source', required=True, help='Source directory')
    parser.add_argument('--bucket', required=True, help='R2 bucket name')
    parser.add_argument('--metadata', required=True, help='Metadata JSON file')

    args = parser.parse_args()

    upload_to_r2(args.source, args.bucket, args.metadata)
```

**Usage:**

```bash
# Setup environment variables
export R2_ENDPOINT_URL="https://<account-id>.r2.cloudflarestorage.com"
export R2_ACCESS_KEY_ID="<your-access-key>"
export R2_SECRET_ACCESS_KEY="<your-secret-key>"

# Upload images
python3 scripts/upload_to_cdn.py \
    --source data/medical_images \
    --bucket irstudy-medical-images \
    --metadata data/image_metadata.json
```

---

## Summary: Phase 1 Download Checklist

**Week 1-2 Target: 150 images**

- [ ] **NIH Chest X-Ray** (100 images)
  - [ ] Setup Kaggle account + API credentials
  - [ ] Download sample dataset
  - [ ] Extract 100 diverse cases

- [ ] **MedPix** (50 cases via manual selection)
  - [ ] Register for MedPix account
  - [ ] Search by specialty (cardiology, dermatology, etc.)
  - [ ] Download 50 high-quality cases with metadata
  - [ ] Record case IDs and citations

- [ ] **HEAL** (50 images)
  - [ ] Browse dermatology collection
  - [ ] Download 50 skin condition images
  - [ ] Record HEAL IDs and citations

- [ ] **Processing**
  - [ ] Run metadata extraction script
  - [ ] Manually enrich metadata (diagnosis, modality)
  - [ ] Validate citations

- [ ] **Upload**
  - [ ] Setup Cloudflare R2 bucket
  - [ ] Upload images to CDN
  - [ ] Generate thumbnail versions

**Total Storage:** ~5 GB (150 images + thumbnails)
**Total Time:** 8-12 hours manual work

---

## Quick Reference Commands

```bash
# Download everything (semi-automated)
./scripts/download_medical_images.sh --phase 1

# Process metadata
python3 scripts/process_image_metadata.py \
    --source data/medical_images \
    --output data/image_metadata.json

# Upload to CDN
python3 scripts/upload_to_cdn.py \
    --source data/medical_images \
    --bucket irstudy-medical-images \
    --metadata data/image_metadata.json

# Index in database
python3 scripts/index_images.py \
    --metadata data/image_metadata.json \
    --db-url postgresql://user:pass@localhost/irstudy
```

---

**Document Version:** 1.0
**Date:** 2026-02-03
**Status:** Ready for Implementation
