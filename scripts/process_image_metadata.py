#!/usr/bin/env python3
"""
Process downloaded medical images and extract metadata

Usage:
    python3 scripts/process_image_metadata.py \
        --source data/medical_images \
        --output data/image_metadata.json

Requirements:
    pip3 install Pillow tqdm
"""

import json
import os
from pathlib import Path
from PIL import Image
import hashlib
from tqdm import tqdm
import argparse

def calculate_file_hash(file_path):
    """Calculate MD5 hash for deduplication"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def extract_source_from_path(file_path):
    """Extract source repository from file path"""
    path_str = str(file_path).lower()

    if 'medpix' in path_str:
        return 'medpix'
    elif 'heal' in path_str:
        return 'heal'
    elif 'nih_chest_xray' in path_str or 'chest-xray' in path_str:
        return 'nih_chest_xray'
    elif 'malaria' in path_str:
        return 'malaria'
    else:
        return 'unknown'

def extract_specialty_from_path(file_path):
    """Extract medical specialty from file path"""
    path_str = str(file_path).lower()

    specialties = {
        'cardiology': 'cardiology',
        'cardiac': 'cardiology',
        'dermatology': 'dermatology',
        'derm': 'dermatology',
        'skin': 'dermatology',
        'pulmonology': 'pulmonology',
        'respiratory': 'pulmonology',
        'chest': 'pulmonology',
        'neurology': 'neurology',
        'neuro': 'neurology',
        'brain': 'neurology',
        'emergency': 'emergency',
        'trauma': 'emergency',
        'radiology': 'radiology',
        'pathology': 'pathology'
    }

    for key, specialty in specialties.items():
        if key in path_str:
            return specialty

    return None

def load_existing_metadata(file_path):
    """Load existing JSON metadata if available"""
    metadata_file = file_path.parent / 'metadata.json'
    if metadata_file.exists():
        try:
            with open(metadata_file) as f:
                return json.load(f)
        except:
            pass
    return {}

def process_directory(source_dir, output_json, verbose=True):
    """Process all images in directory and extract metadata"""

    images = []
    source_path = Path(source_dir)

    # Find all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
    image_files = []

    for ext in image_extensions:
        image_files.extend(source_path.rglob(ext))

    if verbose:
        print(f"Found {len(image_files)} images in {source_dir}")

    # Process each image
    for img_file in tqdm(image_files, desc="Processing images", disable=not verbose):
        try:
            # Open image to get dimensions
            with Image.open(img_file) as img:
                width, height = img.size
                format_type = img.format

            # Calculate file hash for deduplication
            file_hash = calculate_file_hash(img_file)

            # Extract basic metadata
            relative_path = img_file.relative_to(source_path)
            source = extract_source_from_path(relative_path)
            specialty = extract_specialty_from_path(relative_path)

            # Load existing metadata (from MedPix download, etc.)
            existing_meta = load_existing_metadata(img_file)

            # Build metadata object
            metadata = {
                'file_path': str(relative_path),
                'file_name': img_file.name,
                'file_size_kb': img_file.stat().st_size // 1024,
                'width': width,
                'height': height,
                'format': format_type,
                'file_hash': file_hash,

                # Source information
                'source': existing_meta.get('source', source),
                'external_id': existing_meta.get('case_id') or existing_meta.get('heal_id'),

                # Clinical metadata
                'title': existing_meta.get('title'),
                'modality': existing_meta.get('modality'),
                'specialty': existing_meta.get('specialty', specialty),
                'diagnosis': existing_meta.get('diagnosis'),
                'body_part': existing_meta.get('body_part'),

                # Patient information (de-identified)
                'patient_age': existing_meta.get('patient_age'),
                'patient_sex': existing_meta.get('patient_sex'),
                'clinical_history': existing_meta.get('clinical_history'),
                'findings': existing_meta.get('findings'),

                # Citation and licensing
                'citation': existing_meta.get('citation'),
                'license': existing_meta.get('license'),
                'source_url': existing_meta.get('source_url'),

                # Placeholder for CDN URL (added after upload)
                'cdn_url': None,
                'thumbnail_url': None,

                # Quality flags
                'amc_relevance': None,  # To be rated 1-5
                'tags': []
            }

            images.append(metadata)

        except Exception as e:
            if verbose:
                print(f"Error processing {img_file}: {e}")

    # Remove duplicates based on file hash
    unique_images = {}
    for img in images:
        file_hash = img['file_hash']
        if file_hash not in unique_images:
            unique_images[file_hash] = img
        else:
            if verbose:
                print(f"Duplicate found: {img['file_name']} (keeping first occurrence)")

    images = list(unique_images.values())

    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(images, f, indent=2)

    if verbose:
        print(f"\n{'='*50}")
        print("Processing Complete")
        print(f"{'='*50}")
        print(f"Total images processed: {len(image_files)}")
        print(f"Unique images: {len(images)}")
        print(f"Duplicates removed: {len(image_files) - len(images)}")
        print(f"Metadata saved to: {output_json}")

        # Print summary by source
        print(f"\nBreakdown by source:")
        sources = {}
        for img in images:
            source = img['source']
            sources[source] = sources.get(source, 0) + 1

        for source, count in sorted(sources.items()):
            print(f"  {source}: {count} images")

        # Print summary by specialty
        print(f"\nBreakdown by specialty:")
        specialties = {}
        for img in images:
            specialty = img['specialty'] or 'unclassified'
            specialties[specialty] = specialties.get(specialty, 0) + 1

        for specialty, count in sorted(specialties.items()):
            print(f"  {specialty}: {count} images")

        print(f"\nNext steps:")
        print(f"1. Review and enrich metadata in {output_json}")
        print(f"2. Add missing fields: diagnosis, modality, amc_relevance")
        print(f"3. Upload to CDN: python3 scripts/upload_to_cdn.py")

def main():
    parser = argparse.ArgumentParser(
        description='Process medical image metadata',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process all downloaded images
  python3 scripts/process_image_metadata.py \\
      --source data/medical_images \\
      --output data/image_metadata.json

  # Process specific directory
  python3 scripts/process_image_metadata.py \\
      --source data/medical_images/medpix \\
      --output data/medpix_metadata.json
        '''
    )

    parser.add_argument(
        '--source',
        required=True,
        help='Source directory containing medical images'
    )
    parser.add_argument(
        '--output',
        default='image_metadata.json',
        help='Output JSON file for metadata (default: image_metadata.json)'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )

    args = parser.parse_args()

    # Validate source directory
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"Error: Source directory not found: {args.source}")
        return 1

    # Process images
    process_directory(args.source, args.output, verbose=not args.quiet)

    return 0

if __name__ == '__main__':
    exit(main())
