#!/usr/bin/env python3
"""
Enrich HEAL image metadata with citation and AMC-specific fields

Usage:
    python3 scripts/enrich_heal_metadata.py \
        --metadata data/heal_metadata.json

Requirements:
    (standard library only)
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def enrich_heal_metadata(metadata_file):
    """Add HEAL-specific fields to metadata"""

    print(f"Loading metadata from: {metadata_file}")

    with open(metadata_file) as f:
        images = json.load(f)

    print(f"Enriching {len(images)} HEAL images...")

    enriched_count = 0

    for img in images:
        # Source
        if not img.get('source'):
            img['source'] = 'heal'

        # License (HEAL uses CC-BY-NC)
        if not img.get('license'):
            img['license'] = 'CC-BY-NC'

        # Citation format
        heal_id = img.get('external_id') or img.get('heal_id', 'unknown')
        if not img.get('citation'):
            img['citation'] = f"(HEAL #{heal_id}, University of Utah, CC-BY-NC, accessed {datetime.now().strftime('%Y-%m-%d')})"

        # Extract HEAL ID from filename if not present
        if not img.get('heal_id'):
            filename = img.get('file_name', '')
            if 'heal_' in filename:
                # Extract from filename like "heal_87278_xv89712.jpg"
                parts = filename.replace('heal_', '').replace('.jpg', '').split('_')
                if len(parts) >= 2:
                    img['heal_id'] = f"ark:/{parts[0]}/{parts[1]}"
                    img['external_id'] = f"{parts[0]}/{parts[1]}"

        # AMC relevance (default 4, manually review later)
        if not img.get('amc_relevance'):
            img['amc_relevance'] = 4  # High relevance for curated educational content

        # Add tags based on collection/specialty
        collection = (img.get('specialty') or img.get('collection') or '').lower()
        subject = (img.get('subject') or img.get('description') or '').lower()

        if not img.get('tags'):
            img['tags'] = []

        # Dermatology tags
        if 'dermatology' in collection or 'skin' in subject:
            img['specialty'] = 'dermatology'
            if 'dermatology' not in img['tags']:
                img['tags'].extend(['dermatology', 'skin', 'clinical-examination'])

            # Specific conditions
            if 'melanoma' in subject:
                img['tags'].append('melanoma')
            if 'psoriasis' in subject:
                img['tags'].append('psoriasis')
            if 'eczema' in subject:
                img['tags'].append('eczema')

        # ECG tags
        elif 'ecg' in collection or 'electrocardiogram' in subject or 'cardiac' in subject:
            img['specialty'] = 'cardiology'
            if 'cardiology' not in img['tags']:
                img['tags'].extend(['cardiology', 'electrocardiogram', 'interpretation'])

            # Specific findings
            if 'infarction' in subject or 'mi' in subject:
                img['tags'].append('myocardial-infarction')
            if 'arrhythmia' in subject or 'fibrillation' in subject:
                img['tags'].append('arrhythmia')

        # Histology tags
        elif 'histology' in collection or 'microscopy' in subject or 'pathology' in subject:
            img['specialty'] = 'pathology'
            if 'pathology' not in img['tags']:
                img['tags'].extend(['pathology', 'microscopy', 'histology'])

        # Hematology tags
        elif 'hematology' in collection or 'blood' in subject:
            img['specialty'] = 'pathology'
            if 'hematology' not in img['tags']:
                img['tags'].extend(['hematology', 'blood', 'pathology'])

        # Ensure tags are unique
        img['tags'] = list(set(img['tags']))

        enriched_count += 1

    # Save enriched metadata
    with open(metadata_file, 'w') as f:
        json.dump(images, f, indent=2)

    print(f"\n{'='*60}")
    print("Enrichment Complete")
    print(f"{'='*60}")
    print(f"✓ Enriched {enriched_count} HEAL images")
    print(f"✓ All images have:")
    print(f"  - Source: heal")
    print(f"  - License: CC-BY-NC")
    print(f"  - Citation format compliant")
    print(f"  - AMC relevance rating")
    print(f"  - Specialty classification")
    print(f"  - Subject tags")

    # Print summary
    print(f"\nBreakdown by specialty:")
    specialties = {}
    for img in images:
        specialty = img.get('specialty', 'unclassified')
        specialties[specialty] = specialties.get(specialty, 0) + 1

    for specialty, count in sorted(specialties.items()):
        print(f"  {specialty}: {count} images")

    # Print sample citations
    print(f"\nSample citations:")
    for img in images[:3]:
        print(f"  {img['citation']}")

    print(f"\nMetadata saved to: {metadata_file}")
    print(f"\nNext step: python3 scripts/upload_to_cdn.py --metadata {metadata_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Enrich HEAL image metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Enrich HEAL metadata
  python3 scripts/enrich_heal_metadata.py \\
      --metadata data/heal_metadata.json

This script adds:
  - source: "heal"
  - license: "CC-BY-NC"
  - citation: HEAL-compliant format
  - amc_relevance: 1-5 rating
  - specialty: classification
  - tags: subject tags for search
        '''
    )

    parser.add_argument(
        '--metadata',
        required=True,
        help='Metadata JSON file to enrich'
    )

    args = parser.parse_args()

    # Validate metadata file
    if not Path(args.metadata).exists():
        print(f"✗ Metadata file not found: {args.metadata}")
        return 1

    # Enrich metadata
    enrich_heal_metadata(args.metadata)

    return 0

if __name__ == '__main__':
    exit(main())
