#!/usr/bin/env python3
"""
Catalog and Tag Medical Images
Creates comprehensive inventory of all medical images with metadata

Output: data/medical_images_catalog.json
"""

import json
from pathlib import Path
from collections import defaultdict
import hashlib
from datetime import datetime

def get_file_hash(filepath):
    """Generate SHA256 hash for image file"""
    with open(filepath, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]

def extract_metadata_from_path(filepath):
    """Extract specialty, topic, and source from file path"""
    parts = filepath.parts

    metadata = {
        'filepath': str(filepath),
        'filename': filepath.name,
        'file_hash': get_file_hash(filepath),
        'file_size_kb': filepath.stat().st_size // 1024,
        'source': None,
        'specialty': None,
        'topic': None,
        'image_type': None,
    }

    # Parse path structure: data/medical_images/{source}/{specialty}/{topic}/{filename}
    if 'medical_images' in parts:
        idx = parts.index('medical_images')

        if len(parts) > idx + 1:
            metadata['source'] = parts[idx + 1]  # heal, medpix, etc.

        if len(parts) > idx + 2:
            metadata['specialty'] = parts[idx + 2]

        if len(parts) > idx + 3:
            metadata['topic'] = parts[idx + 3].replace('_', ' ')

    # Determine image type from topic/filename
    topic_lower = (metadata['topic'] or '').lower()
    filename_lower = filepath.name.lower()

    if any(term in topic_lower or term in filename_lower for term in ['ecg', 'ekg', 'electrocardiogram']):
        metadata['image_type'] = 'ECG'
    elif any(term in topic_lower or term in filename_lower for term in ['xray', 'x-ray', 'radiograph']):
        metadata['image_type'] = 'X-ray'
    elif any(term in topic_lower or term in filename_lower for term in ['ct', 'computed tomography']):
        metadata['image_type'] = 'CT scan'
    elif any(term in topic_lower or term in filename_lower for term in ['mri', 'magnetic resonance']):
        metadata['image_type'] = 'MRI'
    elif any(term in topic_lower or term in filename_lower for term in ['microscopy', 'blood smear', 'cell', 'leukemia', 'anemia']):
        metadata['image_type'] = 'Microscopy'
    elif any(term in topic_lower or term in filename_lower for term in ['skin', 'rash', 'lesion', 'dermatology']):
        metadata['image_type'] = 'Clinical photo - Dermatology'
    elif any(term in topic_lower or term in filename_lower for term in ['fundus', 'retina', 'ophthal']):
        metadata['image_type'] = 'Fundoscopy'
    elif any(term in topic_lower or term in filename_lower for term in ['ultrasound', 'sonograph']):
        metadata['image_type'] = 'Ultrasound'
    else:
        metadata['image_type'] = 'Clinical photo'

    return metadata

def map_specialty_to_db(specialty):
    """Map directory specialty names to database specialty enum values"""
    mapping = {
        'hematology': 'general_practice',  # Often tested in GP context
        'dermatology': 'general_practice',
        'cardiology': 'cardiology',
        'respiratory': 'respiratory',
        'gastroenterology': 'gastroenterology',
        'neurology': 'neurology',
        'endocrinology': 'endocrinology',
        'psychiatry': 'psychiatry',
        'emergency': 'emergency_medicine',
        'ophthalmology': 'general_practice',
        'ent': 'general_practice',
        'rheumatology': 'general_practice',
        'nephrology': 'general_practice',
        'infectious_disease': 'general_practice',
    }
    return mapping.get(specialty, 'general_practice')

def catalog_images(base_dir='data/medical_images'):
    """Catalog all medical images"""
    base_path = Path(base_dir)

    catalog = {
        'generated_at': datetime.now().isoformat(),
        'total_images': 0,
        'images_by_source': defaultdict(int),
        'images_by_specialty': defaultdict(int),
        'images_by_type': defaultdict(int),
        'images': []
    }

    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'}
    image_files = []

    for ext in image_extensions:
        image_files.extend(base_path.rglob(f'*{ext}'))
        image_files.extend(base_path.rglob(f'*{ext.upper()}'))

    print(f"Found {len(image_files)} image files")

    for filepath in sorted(image_files):
        metadata = extract_metadata_from_path(filepath)

        # Add database-compatible specialty
        metadata['db_specialty'] = map_specialty_to_db(metadata['specialty'])

        # Add to catalog
        catalog['images'].append(metadata)
        catalog['total_images'] += 1

        if metadata['source']:
            catalog['images_by_source'][metadata['source']] += 1
        if metadata['specialty']:
            catalog['images_by_specialty'][metadata['specialty']] += 1
        if metadata['image_type']:
            catalog['images_by_type'][metadata['image_type']] += 1

    # Convert defaultdicts to regular dicts for JSON serialization
    catalog['images_by_source'] = dict(catalog['images_by_source'])
    catalog['images_by_specialty'] = dict(catalog['images_by_specialty'])
    catalog['images_by_type'] = dict(catalog['images_by_type'])

    return catalog

def generate_summary_report(catalog):
    """Generate human-readable summary"""
    print("\n" + "="*80)
    print("MEDICAL IMAGE CATALOG SUMMARY")
    print("="*80)
    print(f"\nTotal Images: {catalog['total_images']}")
    print(f"Generated: {catalog['generated_at']}")

    print("\n" + "-"*80)
    print("BY SOURCE:")
    print("-"*80)
    for source, count in sorted(catalog['images_by_source'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source:30} {count:5} images")

    print("\n" + "-"*80)
    print("BY SPECIALTY:")
    print("-"*80)
    for specialty, count in sorted(catalog['images_by_specialty'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {specialty:30} {count:5} images")

    print("\n" + "-"*80)
    print("BY IMAGE TYPE:")
    print("-"*80)
    for img_type, count in sorted(catalog['images_by_type'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {img_type:30} {count:5} images")

    print("\n" + "="*80)

def main():
    print("Cataloging medical images...")

    # Generate catalog
    catalog = catalog_images()

    # Save to JSON
    output_file = Path('data/medical_images_catalog.json')
    with open(output_file, 'w') as f:
        json.dump(catalog, f, indent=2)

    print(f"\n✅ Catalog saved to: {output_file}")

    # Generate summary report
    generate_summary_report(catalog)

    # Save summary report
    summary_file = Path('data/medical_images_summary.txt')
    with open(summary_file, 'w') as f:
        f.write("MEDICAL IMAGE CATALOG SUMMARY\n")
        f.write("="*80 + "\n\n")
        f.write(f"Total Images: {catalog['total_images']}\n")
        f.write(f"Generated: {catalog['generated_at']}\n\n")

        f.write("-"*80 + "\n")
        f.write("BY SOURCE:\n")
        f.write("-"*80 + "\n")
        for source, count in sorted(catalog['images_by_source'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {source:30} {count:5} images\n")

        f.write("\n" + "-"*80 + "\n")
        f.write("BY SPECIALTY:\n")
        f.write("-"*80 + "\n")
        for specialty, count in sorted(catalog['images_by_specialty'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {specialty:30} {count:5} images\n")

        f.write("\n" + "-"*80 + "\n")
        f.write("BY IMAGE TYPE:\n")
        f.write("-"*80 + "\n")
        for img_type, count in sorted(catalog['images_by_type'].items(), key=lambda x: x[1], reverse=True):
            f.write(f"  {img_type:30} {count:5} images\n")

    print(f"✅ Summary saved to: {summary_file}")

if __name__ == '__main__':
    main()
