# Task 04: Image Metadata Processing

**Duration:** 3 hours
**Priority:** P1
**Dependencies:** None (can run parallel to Phase 1)
**Output:** Unified metadata JSON for all medical image sources

---

## Objective

Process medical images from multiple sources (HEAL, MedPix, NIH, Z-Anatomy) into a unified metadata format with standardized fields for specialty, topic, finding, modality, and file paths.

---

## Scope

### In Scope
- Parse HEAL image metadata (JSON/CSV files)
- Extract metadata from image filenames and folder structure
- Normalize specialty and topic names
- Generate unique image IDs
- Create unified metadata JSON file
- Validate image file existence
- Calculate image statistics (count, size)
- Support multiple image sources (generic architecture)

### Out of Scope
- Image processing (resizing, optimization) - handled in Task 06
- Citation enrichment - handled in Task 05
- Database insertion - handled in Task 07
- Image linking to MCQs/OSCEs - handled in Task 09

---

## Prerequisites

### Downloaded Images
- HEAL Phase 1 download complete (~1,200 images)
  - Location: `data/medical_images/heal/`
  - Structure: `specialty/topic/*.jpg`
  - Metadata: `*_metadata.json` and `*_metadata.csv` files

### Tools Needed
- Python 3.12+
- Libraries: pandas, json, pathlib, PIL (Pillow)

---

## Implementation Steps

### Step 1: Script Structure (20 min)

**File:** `scripts/process_image_metadata.py`

```python
#!/usr/bin/env python3
"""
Process medical images from multiple sources into unified metadata format.

Supports:
- HEAL (Health Education Assets Library)
- MedPix (future)
- NIH (future)
- Z-Anatomy (future)

Usage:
    python3 scripts/process_image_metadata.py \\
        --source data/medical_images/heal \\
        --output data/processed_metadata/heal_metadata.json \\
        --source-type heal

    python3 scripts/process_image_metadata.py \\
        --source data/medical_images/medpix \\
        --output data/processed_metadata/medpix_metadata.json \\
        --source-type medpix
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
import pandas as pd
from PIL import Image
from datetime import datetime
import hashlib

# Unified metadata schema
class ImageMetadata:
    """Standard metadata structure for all image sources"""

    def __init__(self):
        self.image_id: str = ""  # Unique ID (source_specialty_topic_hash)
        self.source: str = ""  # heal, medpix, nih, zanatomyself.file_path: str = ""  # Relative path from project root
        self.filename: str = ""  # Original filename
        self.specialty: str = ""  # Normalized specialty (lowercase)
        self.topic: str = ""  # Normalized topic
        self.subtopic: Optional[str] = None
        self.clinical_finding: Optional[str] = None  # What the image shows
        self.modality: Optional[str] = None  # X-ray, CT, MRI, Photo, Histology
        self.body_part: Optional[str] = None  # Heart, Lung, Skin, etc.
        self.age_group: Optional[str] = None  # Adult, Pediatric, Neonate
        self.file_size_bytes: int = 0
        self.width_px: int = 0
        self.height_px: int = 0
        self.format: str = ""  # JPEG, PNG
        self.license: str = ""  # CC-BY-NC, Public Domain
        self.citation: Optional[str] = None  # Added in Task 05
        self.url: Optional[str] = None  # CDN URL (added in Task 06)
        self.created_at: str = ""  # ISO timestamp

    def to_dict(self) -> Dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}
```

---

### Step 2: HEAL Metadata Parser (1 hour)

```python
def parse_heal_metadata(source_dir: Path) -> List[ImageMetadata]:
    """
    Parse HEAL image directory structure and metadata files.

    Structure:
        data/medical_images/heal/
        ├── hematology/
        │   ├── acute_myeloid_leukemia/
        │   │   ├── heal_889318.jpg
        │   │   ├── heal_889688.jpg
        │   │   ├── acute_myeloid_leukemia_metadata.json
        │   │   └── acute_myeloid_leukemia_metadata.csv
        │   └── sickle_cell_anemia/
        ├── dermatology/
        └── cardiology/
    """
    images = []

    # Iterate through specialties
    for specialty_dir in source_dir.iterdir():
        if not specialty_dir.is_dir():
            continue

        specialty = specialty_dir.name
        print(f"Processing specialty: {specialty}")

        # Iterate through topics
        for topic_dir in specialty_dir.iterdir():
            if not topic_dir.is_dir():
                continue

            topic = topic_dir.name
            print(f"  Processing topic: {topic}")

            # Load topic metadata if exists
            metadata_json = topic_dir / f"{topic}_metadata.json"
            metadata_csv = topic_dir / f"{topic}_metadata.csv"

            topic_metadata = {}
            if metadata_json.exists():
                with open(metadata_json, 'r') as f:
                    topic_metadata = json.load(f)
            elif metadata_csv.exists():
                df = pd.read_csv(metadata_csv)
                topic_metadata = df.to_dict('records')

            # Process each image
            for img_file in topic_dir.glob("*.jpg"):
                image_meta = process_heal_image(
                    img_file=img_file,
                    specialty=specialty,
                    topic=topic,
                    topic_metadata=topic_metadata,
                    source_dir=source_dir
                )
                if image_meta:
                    images.append(image_meta)

    return images


def process_heal_image(
    img_file: Path,
    specialty: str,
    topic: str,
    topic_metadata: Dict,
    source_dir: Path
) -> Optional[ImageMetadata]:
    """Process single HEAL image"""

    try:
        # Extract HEAL ID from filename
        # Example: heal_889318.jpg -> 889318
        heal_id = img_file.stem.replace('heal_', '')

        # Generate unique image ID
        hash_input = f"heal_{specialty}_{topic}_{heal_id}"
        image_id = hashlib.md5(hash_input.encode()).hexdigest()[:12]

        # Get image dimensions and size
        with Image.open(img_file) as img:
            width, height = img.size
            format_type = img.format

        file_size = img_file.stat().st_size

        # Create metadata object
        meta = ImageMetadata()
        meta.image_id = f"heal_{image_id}"
        meta.source = "heal"
        meta.file_path = str(img_file.relative_to(source_dir.parent.parent))
        meta.filename = img_file.name
        meta.specialty = normalize_specialty(specialty)
        meta.topic = normalize_topic(topic)
        meta.clinical_finding = extract_clinical_finding(topic)
        meta.modality = infer_modality(specialty, topic)
        meta.body_part = infer_body_part(specialty, topic)
        meta.file_size_bytes = file_size
        meta.width_px = width
        meta.height_px = height
        meta.format = format_type
        meta.license = "CC-BY-NC-4.0"  # HEAL default license
        meta.created_at = datetime.now().isoformat()

        # Enrich from topic metadata if available
        if isinstance(topic_metadata, dict) and heal_id in topic_metadata:
            enrich_from_heal_metadata(meta, topic_metadata[heal_id])

        return meta

    except Exception as e:
        print(f"  ⚠ Error processing {img_file.name}: {e}")
        return None


def normalize_specialty(specialty: str) -> str:
    """Normalize specialty name to match database enum"""
    specialty_map = {
        'hematology': 'hematology',
        'dermatology': 'dermatology',
        'cardiology': 'cardiology',
        'respiratory': 'respiratory',
        'psychiatry': 'psychiatry',
        'neurology': 'neurology',
        'emergency': 'emergency_medicine',
        'obstetrics': 'obstetrics_gynaecology',
        'paediatrics': 'paediatrics',
        'surgery': 'surgery',
        'anatomy': 'anatomy',
        'pathology': 'pathology',
    }

    key = specialty.lower().replace(' ', '_').replace('-', '_')
    return specialty_map.get(key, specialty.lower())


def normalize_topic(topic: str) -> str:
    """Normalize topic name (replace underscores, title case)"""
    return topic.replace('_', ' ').title()


def extract_clinical_finding(topic: str) -> str:
    """Extract clinical finding from topic name"""
    # Examples:
    #   acute_myeloid_leukemia -> Acute Myeloid Leukemia
    #   STEMI_ECG -> ST-Elevation Myocardial Infarction (ECG)
    #   atrial_fibrillation_ECG -> Atrial Fibrillation (ECG)

    finding = topic.replace('_', ' ').title()

    # Special handling for ECG
    if 'ECG' in topic.upper():
        finding = finding.replace('Ecg', '(ECG)')

    return finding


def infer_modality(specialty: str, topic: str) -> str:
    """Infer imaging modality from specialty and topic"""
    topic_lower = topic.lower()

    if 'ecg' in topic_lower or 'ekg' in topic_lower:
        return 'ECG'
    elif specialty == 'hematology':
        return 'Microscopy'
    elif specialty == 'dermatology':
        return 'Clinical Photography'
    elif 'xray' in topic_lower or 'x-ray' in topic_lower:
        return 'X-Ray'
    elif 'ct' in topic_lower:
        return 'CT Scan'
    elif 'mri' in topic_lower:
        return 'MRI'
    elif 'ultrasound' in topic_lower or 'echo' in topic_lower:
        return 'Ultrasound'
    else:
        return 'Unknown'


def infer_body_part(specialty: str, topic: str) -> Optional[str]:
    """Infer body part from specialty and topic"""
    if specialty == 'cardiology':
        return 'Heart'
    elif specialty == 'respiratory':
        return 'Lungs'
    elif specialty == 'dermatology':
        return 'Skin'
    elif specialty == 'hematology':
        return 'Blood'
    elif 'brain' in topic.lower():
        return 'Brain'
    elif 'chest' in topic.lower():
        return 'Chest'
    else:
        return None


def enrich_from_heal_metadata(meta: ImageMetadata, heal_data: Dict):
    """Enrich metadata from HEAL-specific fields"""
    if 'description' in heal_data:
        meta.clinical_finding = heal_data['description']

    if 'modality' in heal_data:
        meta.modality = heal_data['modality']

    if 'age_group' in heal_data:
        meta.age_group = heal_data['age_group']
```

---

### Step 3: Generic Source Handler (30 min)

```python
def process_images(source_dir: Path, source_type: str) -> List[ImageMetadata]:
    """
    Process images from any source type.

    Args:
        source_dir: Root directory of images
        source_type: 'heal', 'medpix', 'nih', 'zanatomy'

    Returns:
        List of ImageMetadata objects
    """
    if source_type == 'heal':
        return parse_heal_metadata(source_dir)
    elif source_type == 'medpix':
        return parse_medpix_metadata(source_dir)  # Future
    elif source_type == 'nih':
        return parse_nih_metadata(source_dir)  # Future
    elif source_type == 'zanatomy':
        return parse_zanatomy_metadata(source_dir)  # Future
    else:
        raise ValueError(f"Unknown source type: {source_type}")


def parse_medpix_metadata(source_dir: Path) -> List[ImageMetadata]:
    """Future: Parse MedPix metadata"""
    # TODO: Implement when MedPix is downloaded
    return []


def parse_nih_metadata(source_dir: Path) -> List[ImageMetadata]:
    """Future: Parse NIH metadata"""
    # TODO: Implement when NIH is downloaded
    return []


def parse_zanatomy_metadata(source_dir: Path) -> List[ImageMetadata]:
    """Future: Parse Z-Anatomy metadata"""
    # TODO: Implement when Z-Anatomy is downloaded
    return []
```

---

### Step 4: Output Generation (20 min)

```python
def generate_metadata_json(images: List[ImageMetadata], output_path: Path):
    """Generate unified metadata JSON file"""

    # Convert to dict format
    images_dict = [img.to_dict() for img in images]

    # Generate statistics
    stats = {
        'total_images': len(images),
        'by_specialty': {},
        'by_modality': {},
        'by_source': {},
        'total_size_bytes': sum(img.file_size_bytes for img in images),
        'generated_at': datetime.now().isoformat(),
    }

    # Count by specialty
    for img in images:
        specialty = img.specialty
        stats['by_specialty'][specialty] = stats['by_specialty'].get(specialty, 0) + 1

    # Count by modality
    for img in images:
        modality = img.modality or 'Unknown'
        stats['by_modality'][modality] = stats['by_modality'].get(modality, 0) + 1

    # Count by source
    for img in images:
        source = img.source
        stats['by_source'][source] = stats['by_source'].get(source, 0) + 1

    # Create final output
    output_data = {
        'metadata': {
            'version': '1.0',
            'schema': 'medical_image_metadata_v1',
            'sources': list(stats['by_source'].keys()),
        },
        'statistics': stats,
        'images': images_dict
    }

    # Write to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Metadata Generated Successfully!")
    print(f"{'='*70}")
    print(f"Output: {output_path}")
    print(f"Total images: {stats['total_images']}")
    print(f"Total size: {stats['total_size_bytes'] / 1024 / 1024:.2f} MB")
    print(f"\nBy Specialty:")
    for specialty, count in sorted(stats['by_specialty'].items()):
        print(f"  {specialty}: {count}")
    print(f"\nBy Modality:")
    for modality, count in sorted(stats['by_modality'].items()):
        print(f"  {modality}: {count}")
```

---

### Step 5: CLI Interface (20 min)

```python
def main():
    parser = argparse.ArgumentParser(
        description='Process medical images into unified metadata format',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--source',
        type=Path,
        required=True,
        help='Source directory containing images'
    )

    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output JSON file path'
    )

    parser.add_argument(
        '--source-type',
        choices=['heal', 'medpix', 'nih', 'zanatomy'],
        required=True,
        help='Type of image source'
    )

    parser.add_argument(
        '--validate-images',
        action='store_true',
        help='Validate all image files exist and are readable'
    )

    args = parser.parse_args()

    # Validate source directory
    if not args.source.exists():
        print(f"❌ Source directory not found: {args.source}")
        return 1

    print(f"{'='*70}")
    print(f"Medical Image Metadata Processing")
    print(f"{'='*70}")
    print(f"Source: {args.source}")
    print(f"Type: {args.source_type}")
    print(f"Output: {args.output}")
    print()

    # Process images
    images = process_images(args.source, args.source_type)

    if not images:
        print("⚠ No images found")
        return 1

    # Validate images if requested
    if args.validate_images:
        print("\nValidating images...")
        valid_count = 0
        for img in images:
            img_path = Path(img.file_path)
            if img_path.exists():
                valid_count += 1
            else:
                print(f"  ⚠ Missing: {img_path}")

        print(f"Valid images: {valid_count}/{len(images)}")

    # Generate output
    generate_metadata_json(images, args.output)

    return 0


if __name__ == "__main__":
    exit(main())
```

---

## Testing

### Unit Tests

**File:** `tests/test_metadata_processing.py`

```python
import pytest
from pathlib import Path
from scripts.process_image_metadata import (
    normalize_specialty,
    normalize_topic,
    extract_clinical_finding,
    infer_modality,
)

def test_normalize_specialty():
    assert normalize_specialty("Hematology") == "hematology"
    assert normalize_specialty("CARDIOLOGY") == "cardiology"
    assert normalize_specialty("Emergency Medicine") == "emergency_medicine"

def test_normalize_topic():
    assert normalize_topic("acute_myeloid_leukemia") == "Acute Myeloid Leukemia"
    assert normalize_topic("STEMI_diagnosis") == "Stemi Diagnosis"

def test_extract_clinical_finding():
    assert extract_clinical_finding("atrial_fibrillation_ECG") == "Atrial Fibrillation (ECG)"
    assert extract_clinical_finding("melanoma_stage_3") == "Melanoma Stage 3"

def test_infer_modality():
    assert infer_modality("cardiology", "atrial_fibrillation_ECG") == "ECG"
    assert infer_modality("hematology", "acute_leukemia") == "Microscopy"
    assert infer_modality("dermatology", "melanoma") == "Clinical Photography"
```

### Integration Test

```bash
# Test with HEAL images
python3 scripts/process_image_metadata.py \
    --source data/medical_images/heal \
    --output data/processed_metadata/heal_metadata.json \
    --source-type heal \
    --validate-images

# Verify output
cat data/processed_metadata/heal_metadata.json | jq '.statistics'

# Expected output:
{
  "total_images": 1137,
  "by_specialty": {
    "hematology": 482,
    "dermatology": 328,
    "cardiology": 327
  },
  "by_modality": {
    "Microscopy": 482,
    "Clinical Photography": 328,
    "ECG": 327
  },
  "total_size_bytes": 314572800
}
```

---

## Success Criteria

- ✅ Script processes all HEAL images (~1,200)
- ✅ Unified metadata JSON generated
- ✅ All required fields populated (image_id, specialty, topic, file_path)
- ✅ Specialties normalized to match database enum
- ✅ Image dimensions and file sizes extracted
- ✅ Modality inferred correctly (ECG, Microscopy, Photography)
- ✅ Statistics generated (count by specialty, modality)
- ✅ Generic architecture supports multiple sources
- ✅ All images validated (file existence)
- ✅ No errors during processing

---

## Output Format

**File:** `data/processed_metadata/heal_metadata.json`

```json
{
  "metadata": {
    "version": "1.0",
    "schema": "medical_image_metadata_v1",
    "sources": ["heal"]
  },
  "statistics": {
    "total_images": 1137,
    "by_specialty": {
      "hematology": 482,
      "dermatology": 328,
      "cardiology": 327
    },
    "by_modality": {
      "Microscopy": 482,
      "Clinical Photography": 328,
      "ECG": 327
    },
    "total_size_bytes": 314572800,
    "generated_at": "2026-02-03T14:30:00Z"
  },
  "images": [
    {
      "image_id": "heal_a1b2c3d4e5f6",
      "source": "heal",
      "file_path": "data/medical_images/heal/hematology/acute_myeloid_leukemia/heal_889318.jpg",
      "filename": "heal_889318.jpg",
      "specialty": "hematology",
      "topic": "Acute Myeloid Leukemia",
      "clinical_finding": "Acute Myeloid Leukemia",
      "modality": "Microscopy",
      "body_part": "Blood",
      "file_size_bytes": 276543,
      "width_px": 1024,
      "height_px": 768,
      "format": "JPEG",
      "license": "CC-BY-NC-4.0",
      "created_at": "2026-02-03T14:15:32Z"
    }
  ]
}
```

---

## Next Task

After completion, proceed to **Task 05: Image Citation Enrichment**

File: `05_image_citation_enrichment.md`
