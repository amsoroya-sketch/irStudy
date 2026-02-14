#!/usr/bin/env python3
"""
Batch download HEAL images across multiple topics for AMC exam prep

This script automatically downloads images from HEAL collection for:
- Dermatology (skin conditions)
- Cardiology (ECG, heart conditions)
- Pulmonology (chest X-rays, respiratory)
- Neurology (brain, nervous system)
- Pathology (histology, microscopy)
- Hematology (blood disorders)
- Gastroenterology (GI conditions)
- Orthopedics (musculoskeletal)

Requirements:
    pip3 install playwright beautifulsoup4 tqdm
    playwright install chromium

Usage:
    # Download all topics (recommended for Phase 1)
    python3 scripts/download_heal_batch.py --max-per-topic 10

    # Download specific specialties only
    python3 scripts/download_heal_batch.py \\
        --specialties dermatology cardiology \\
        --max-per-topic 20

    # Show browser for debugging
    python3 scripts/download_heal_batch.py \\
        --max-per-topic 5 \\
        --show-browser
"""

import asyncio
import argparse
from pathlib import Path
import json
from datetime import datetime

# Import the playwright downloader
import sys
sys.path.insert(0, str(Path(__file__).parent))
from download_heal_playwright import HEALPlaywrightDownloader, save_metadata

# AMC Exam-Relevant Topics by Specialty
AMC_TOPICS = {
    'dermatology': [
        'melanoma',
        'basal cell carcinoma',
        'squamous cell carcinoma',
        'psoriasis',
        'eczema',
        'dermatitis',
        'acne',
        'rosacea',
        'urticaria',
        'vitiligo',
        'fungal infection skin',
        'herpes zoster',
        'impetigo',
        'cellulitis',
        'skin ulcer'
    ],
    'cardiology': [
        'electrocardiogram',
        'ECG myocardial infarction',
        'ECG arrhythmia',
        'atrial fibrillation',
        'heart failure',
        'angina',
        'hypertension',
        'cardiomyopathy',
        'valvular heart disease',
        'pericarditis'
    ],
    'pulmonology': [
        'pneumonia chest xray',
        'tuberculosis',
        'asthma',
        'COPD',
        'pulmonary embolism',
        'lung cancer',
        'pleural effusion',
        'pneumothorax',
        'interstitial lung disease',
        'bronchiectasis'
    ],
    'neurology': [
        'stroke CT',
        'stroke MRI',
        'brain tumor',
        'multiple sclerosis',
        'epilepsy',
        'meningitis',
        'encephalitis',
        'peripheral neuropathy',
        'parkinson disease',
        'dementia'
    ],
    'pathology': [
        'histology',
        'microscopy pathology',
        'biopsy',
        'cancer pathology',
        'inflammation pathology',
        'necrosis',
        'fibrosis',
        'granuloma',
        'lymphoma',
        'leukemia'
    ],
    'hematology': [
        'blood smear',
        'anemia',
        'sickle cell',
        'thalassemia',
        'leukemia blood',
        'lymphoma blood',
        'coagulation disorder',
        'thrombocytopenia',
        'bone marrow',
        'peripheral blood'
    ],
    'gastroenterology': [
        'peptic ulcer',
        'inflammatory bowel disease',
        'cirrhosis',
        'hepatitis',
        'pancreatitis',
        'colorectal cancer',
        'esophagitis',
        'gastritis',
        'cholecystitis',
        'appendicitis'
    ],
    'orthopedics': [
        'fracture xray',
        'arthritis',
        'osteoporosis',
        'joint dislocation',
        'bone tumor',
        'osteomyelitis',
        'scoliosis',
        'spinal stenosis',
        'rotator cuff tear',
        'meniscus tear'
    ],
    'emergency': [
        'trauma',
        'head injury',
        'abdominal pain imaging',
        'acute abdomen',
        'chest pain imaging',
        'emergency radiology',
        'fracture emergency',
        'foreign body',
        'acute hemorrhage',
        'sepsis imaging'
    ],
    'pediatrics': [
        'pediatric rash',
        'pediatric chest xray',
        'developmental milestones',
        'pediatric seizure',
        'pediatric asthma',
        'pediatric infection',
        'congenital abnormality',
        'pediatric fracture',
        'pediatric jaundice',
        'neonatal'
    ]
}

async def download_specialty(specialty, topics, max_per_topic, output_base, show_browser=False):
    """Download images for a single specialty"""

    print(f"\n{'='*70}")
    print(f"SPECIALTY: {specialty.upper()}")
    print(f"{'='*70}")
    print(f"Topics: {len(topics)}")
    print(f"Max per topic: {max_per_topic}")

    output_dir = Path(output_base) / specialty
    output_dir.mkdir(parents=True, exist_ok=True)

    all_results = []
    total_downloaded = 0

    downloader = HEALPlaywrightDownloader(
        headless=not show_browser,
        slow_mo=500 if show_browser else 0
    )

    for idx, topic in enumerate(topics, 1):
        print(f"\n[{idx}/{len(topics)}] Topic: {topic}")

        try:
            # Search and extract IDs
            results = await downloader.search_and_extract_ids(topic, max_results=max_per_topic)

            if results:
                print(f"  ✓ Found {len(results)} items")

                # Download images
                downloaded = await downloader.download_images(results, output_dir)

                if downloaded:
                    all_results.extend(downloaded)
                    total_downloaded += len(downloaded)
                    print(f"  ✓ Downloaded {len(downloaded)} images")
                else:
                    print(f"  ⚠ No images downloaded")
            else:
                print(f"  ⚠ No results found")

        except Exception as e:
            print(f"  ✗ Error: {e}")

        # Rate limiting between topics
        await asyncio.sleep(2)

    # Save specialty metadata
    if all_results:
        json_file, csv_file = save_metadata(all_results, output_dir, specialty)
        print(f"\n✓ Specialty complete: {specialty}")
        print(f"  Downloaded: {total_downloaded} images")
        print(f"  Metadata: {json_file}")

    return all_results

async def main():
    parser = argparse.ArgumentParser(
        description='Batch download HEAL images for multiple AMC exam topics',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download all specialties (recommended for Phase 1)
  python3 scripts/download_heal_batch.py --max-per-topic 10

  # Download specific specialties only
  python3 scripts/download_heal_batch.py \\
      --specialties dermatology cardiology pulmonology \\
      --max-per-topic 20

  # Quick test (5 images per topic)
  python3 scripts/download_heal_batch.py \\
      --specialties dermatology \\
      --max-per-topic 5 \\
      --show-browser

Available Specialties:
  - dermatology (15 topics: melanoma, psoriasis, etc.)
  - cardiology (10 topics: ECG, MI, arrhythmia, etc.)
  - pulmonology (10 topics: pneumonia, TB, COPD, etc.)
  - neurology (10 topics: stroke, MS, epilepsy, etc.)
  - pathology (10 topics: histology, biopsy, cancer, etc.)
  - hematology (10 topics: anemia, leukemia, etc.)
  - gastroenterology (10 topics: ulcer, IBD, hepatitis, etc.)
  - orthopedics (10 topics: fracture, arthritis, etc.)
  - emergency (10 topics: trauma, acute abdomen, etc.)
  - pediatrics (10 topics: pediatric conditions)
        '''
    )

    parser.add_argument(
        '--specialties',
        nargs='+',
        choices=list(AMC_TOPICS.keys()) + ['all'],
        default=['all'],
        help='Specialties to download (default: all)'
    )

    parser.add_argument(
        '--max-per-topic',
        type=int,
        default=10,
        help='Maximum images per topic (default: 10)'
    )

    parser.add_argument(
        '--output',
        default='data/medical_images/heal',
        help='Output directory (default: data/medical_images/heal)'
    )

    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser (not headless, for debugging)'
    )

    args = parser.parse_args()

    # Determine which specialties to download
    if 'all' in args.specialties:
        specialties = list(AMC_TOPICS.keys())
    else:
        specialties = args.specialties

    print(f"\n{'='*70}")
    print(f"HEAL Batch Downloader for AMC Exam Prep")
    print(f"{'='*70}")
    print(f"Specialties: {', '.join(specialties)}")
    print(f"Max per topic: {args.max_per_topic}")
    print(f"Output: {args.output}")
    print(f"")

    # Calculate totals
    total_topics = sum(len(AMC_TOPICS[s]) for s in specialties)
    estimated_images = total_topics * args.max_per_topic

    print(f"Estimated downloads:")
    print(f"  Total topics: {total_topics}")
    print(f"  Max images: {estimated_images}")
    print(f"  Estimated time: {estimated_images * 2 // 60} minutes")
    print(f"")

    input("Press Enter to start downloading (Ctrl+C to cancel)...")

    # Download each specialty
    start_time = datetime.now()
    all_downloads = []

    for specialty in specialties:
        topics = AMC_TOPICS[specialty]
        results = await download_specialty(
            specialty,
            topics,
            args.max_per_topic,
            args.output,
            show_browser=args.show_browser
        )
        all_downloads.extend(results)

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Final summary
    print(f"\n{'='*70}")
    print(f"BATCH DOWNLOAD COMPLETE!")
    print(f"{'='*70}")
    print(f"")
    print(f"Summary:")
    print(f"  Specialties processed: {len(specialties)}")
    print(f"  Total images downloaded: {len(all_downloads)}")
    print(f"  Total time: {int(duration // 60)}m {int(duration % 60)}s")
    print(f"  Output directory: {args.output}")
    print(f"")

    # Breakdown by specialty
    print(f"Breakdown by specialty:")
    for specialty in specialties:
        count = len([d for d in all_downloads if specialty in d.get('filepath', '')])
        print(f"  {specialty}: {count} images")

    # Save combined metadata
    output_path = Path(args.output)
    combined_json = output_path / 'all_downloads_metadata.json'
    with open(combined_json, 'w') as f:
        json.dump(all_downloads, f, indent=2)

    print(f"")
    print(f"Combined metadata: {combined_json}")
    print(f"")
    print(f"Next steps:")
    print(f"1. Review downloaded images: ls -lh {args.output}/*/*.jpg")
    print(f"2. Process metadata: python3 scripts/process_image_metadata.py --source {args.output}")
    print(f"3. Enrich metadata: python3 scripts/enrich_heal_metadata.py --metadata data/heal_metadata.json")
    print(f"4. Upload to CDN: python3 scripts/upload_to_cdn.py --source {args.output} ...")
    print(f"5. Index database: python3 scripts/index_images.py --metadata data/heal_metadata.json")

if __name__ == '__main__':
    asyncio.run(main())
