#!/usr/bin/env python3
"""
Comprehensive HEAL batch downloader with full topic coverage

Based on HEAL topic analysis (HEAL_TOPIC_ANALYSIS.md), this script downloads
images across all available specialties with proper organization and rate limiting.

Features:
- Organizes downloads by specialty > topic folders
- Configurable delays between requests (default: 2s per image, 5s per topic)
- Phase-based downloading (P0, P1, P2)
- Progress tracking and resumption support
- Comprehensive error handling

Requirements:
    pip3 install playwright beautifulsoup4 tqdm
    playwright install chromium

Usage:
    # Phase 1 (P0): High-priority specialties (~300-400 images, 1-2 hours)
    python3 scripts/download_heal_comprehensive.py --phase 1

    # Phase 2 (P1): Medium-priority specialties (~200-300 images, 1-1.5 hours)
    python3 scripts/download_heal_comprehensive.py --phase 2

    # Phase 3 (P2): Low-priority specialties (~50-100 images, 30 min)
    python3 scripts/download_heal_comprehensive.py --phase 3

    # All phases (~550-800 images, 3-4 hours)
    python3 scripts/download_heal_comprehensive.py --phase all

    # Custom: Specific specialties only
    python3 scripts/download_heal_comprehensive.py \
        --specialties hematology dermatology \
        --images-per-topic 20

    # Test run (5 images each, no delay)
    python3 scripts/download_heal_comprehensive.py \
        --phase 1 \
        --images-per-topic 5 \
        --no-delay \
        --show-browser
"""

import asyncio
import argparse
from pathlib import Path
import json
from datetime import datetime
import sys
import time

# Import the playwright downloader
sys.path.insert(0, str(Path(__file__).parent))
from download_heal_playwright import HEALPlaywrightDownloader, save_metadata

# Comprehensive topic coverage based on HEAL analysis
HEAL_TOPICS = {
    # ==========================================
    # PHASE 1 (P0): EXCEPTIONAL COVERAGE + HIGH AMC RELEVANCE
    # ==========================================
    'hematology': {
        'priority': 0,
        'total_available': 1500,
        'recommended_download': 150,
        'amc_relevance': 5,
        'topics': [
            # Leukemia (10 topics)
            'acute myeloid leukemia',
            'acute lymphoblastic leukemia',
            'chronic myeloid leukemia',
            'chronic lymphocytic leukemia',
            'hairy cell leukemia',
            'acute promyelocytic leukemia',
            'myelodysplastic syndrome',
            'myeloproliferative neoplasm',
            'auer rods leukemia',
            'blast cells leukemia',

            # Anemia (8 topics)
            'iron deficiency anemia',
            'megaloblastic anemia',
            'sickle cell anemia',
            'thalassemia',
            'hemolytic anemia',
            'aplastic anemia',
            'anemia chronic disease',
            'pernicious anemia',

            # Red Cell Disorders (5 topics)
            'spherocytosis',
            'elliptocytosis',
            'target cells',
            'schistocytes',
            'rouleaux formation',

            # White Cell Disorders (5 topics)
            'neutropenia',
            'leukocytosis',
            'lymphocytosis',
            'monocytosis',
            'eosinophilia',

            # Coagulation (8 topics)
            'disseminated intravascular coagulation',
            'thrombocytopenia',
            'thrombocytosis',
            'von willebrand disease',
            'hemophilia',
            'purpura',
            'antiphospholipid syndrome',
            'heparin induced thrombocytopenia',

            # Bone Marrow (6 topics)
            'bone marrow aspirate',
            'bone marrow biopsy',
            'multiple myeloma',
            'plasma cells',
            'hemophagocytosis',
            'bone marrow hypoplasia',

            # Blood Smear Morphology (8 topics)
            'blood smear normal',
            'blood smear abnormal',
            'atypical lymphocytes',
            'downey cells',
            'immature granulocytes',
            'blast differential',
            'reticulocytes',
            'platelet morphology',
        ]
    },

    'dermatology': {
        'priority': 0,
        'total_available': 330,
        'recommended_download': 75,
        'amc_relevance': 5,
        'topics': [
            # Cancers (5 topics)
            'melanoma',
            'basal cell carcinoma',
            'squamous cell carcinoma',
            'keratoacanthoma',
            'kaposi sarcoma',

            # Inflammatory (8 topics)
            'atopic dermatitis',
            'contact dermatitis',
            'seborrheic dermatitis',
            'nummular dermatitis',
            'stasis dermatitis',
            'psoriasis',
            'lichen planus',
            'pityriasis rosea',

            # Infections (6 topics)
            'cellulitis',
            'erysipelas',
            'impetigo',
            'herpes zoster',
            'herpes simplex',
            'fungal infection skin',

            # Allergic (4 topics)
            'urticaria',
            'angioedema',
            'drug eruption',
            'stevens johnson syndrome',

            # Acne/Rosacea (3 topics)
            'acne vulgaris',
            'acne rosacea',
            'perioral dermatitis',

            # Autoimmune (4 topics)
            'vitiligo',
            'alopecia areata',
            'pemphigus',
            'bullous pemphigoid',

            # Other (5 topics)
            'scabies',
            'molluscum contagiosum',
            'warts',
            'seborrheic keratosis',
            'skin tag',
        ]
    },

    'cardiology': {
        'priority': 0,
        'total_available': 248,
        'recommended_download': 75,
        'amc_relevance': 5,
        'topics': [
            # Arrhythmias (10 topics)
            'atrial fibrillation ECG',
            'atrial flutter ECG',
            'supraventricular tachycardia ECG',
            'ventricular tachycardia ECG',
            'ventricular fibrillation ECG',
            'junctional tachycardia ECG',
            'sinus tachycardia ECG',
            'sinus bradycardia ECG',
            'premature atrial contraction',
            'premature ventricular contraction',

            # Conduction Blocks (6 topics)
            'left bundle branch block',
            'right bundle branch block',
            'first degree AV block',
            'second degree AV block',
            'third degree AV block',
            'bifascicular block',

            # Ischemia/MI (8 topics)
            'ST elevation myocardial infarction',
            'non ST elevation myocardial infarction',
            'anterior wall MI',
            'inferior wall MI',
            'lateral wall MI',
            'posterior wall MI',
            'acute coronary syndrome ECG',
            'angina ECG',

            # Hypertrophy/Enlargement (5 topics)
            'left ventricular hypertrophy ECG',
            'right ventricular hypertrophy ECG',
            'left atrial enlargement ECG',
            'right atrial enlargement ECG',
            'biventricular hypertrophy',

            # Other (6 topics)
            'pacemaker ECG',
            'pericarditis ECG',
            'hyperkalemia ECG',
            'hypokalemia ECG',
            'long QT syndrome',
            'brugada syndrome',
        ]
    },

    # ==========================================
    # PHASE 2 (P1): GOOD COVERAGE + HIGH AMC RELEVANCE
    # ==========================================
    'anatomy': {
        'priority': 1,
        'total_available': 690,
        'recommended_download': 75,
        'amc_relevance': 4,
        'topics': [
            # Cardiovascular (5 topics)
            'heart anatomy',
            'cardiac vasculature',
            'aorta anatomy',
            'venous system',
            'coronary arteries',

            # Respiratory (4 topics)
            'lung anatomy',
            'bronchial tree',
            'pleura anatomy',
            'mediastinum anatomy',

            # Neuroanatomy (10 topics)
            'brain anatomy',
            'cerebellum anatomy',
            'brainstem anatomy',
            'spinal cord anatomy',
            'cranial nerves',
            'peripheral nerves',
            'brachial plexus',
            'lumbar plexus',
            'autonomic nervous system',
            'meninges anatomy',

            # Musculoskeletal (8 topics)
            'shoulder anatomy',
            'elbow anatomy',
            'wrist hand anatomy',
            'hip anatomy',
            'knee anatomy',
            'ankle foot anatomy',
            'spine anatomy',
            'skull anatomy',

            # Abdomen (5 topics)
            'abdominal organs',
            'liver anatomy',
            'kidney anatomy',
            'gastrointestinal anatomy',
            'retroperitoneum',
        ]
    },

    'bone_marrow': {
        'priority': 1,
        'total_available': 386,
        'recommended_download': 40,
        'amc_relevance': 4,
        'topics': [
            # Bone Marrow (8 topics)
            'bone marrow normal',
            'bone marrow cellularity',
            'erythroid lineage',
            'myeloid lineage',
            'megakaryocytes',
            'bone marrow fibrosis',
            'bone marrow infiltration',
            'hematopoiesis',

            # Bone Histology (6 topics)
            'compact bone',
            'trabecular bone',
            'osteoblasts',
            'osteoclasts',
            'bone remodeling',
            'bone matrix',
        ]
    },

    'respiratory': {
        'priority': 1,
        'total_available': 189,
        'recommended_download': 30,
        'amc_relevance': 4,
        'topics': [
            # Lung Pathology (6 topics)
            'pneumonia chest',
            'pulmonary edema',
            'atelectasis',
            'pneumothorax',
            'pleural effusion',
            'lung nodule',

            # Chronic Conditions (4 topics)
            'chronic obstructive pulmonary disease',
            'asthma',
            'interstitial lung disease',
            'pulmonary fibrosis',
        ]
    },

    'pediatrics': {
        'priority': 1,
        'total_available': 121,
        'recommended_download': 25,
        'amc_relevance': 4,
        'topics': [
            # Pediatric Conditions (10 topics)
            'pediatric rash',
            'pediatric infection',
            'pediatric anemia',
            'pediatric asthma',
            'pediatric seizure',
            'neonatal jaundice',
            'congenital abnormality',
            'pediatric development',
            'pediatric vaccination',
            'pediatric growth',
        ]
    },

    'pathology': {
        'priority': 1,
        'total_available': 108,
        'recommended_download': 40,
        'amc_relevance': 4,
        'topics': [
            # Tumors (10 topics)
            'adenocarcinoma',
            'squamous cell carcinoma pathology',
            'carcinoma in situ',
            'metastatic carcinoma',
            'lymphoma pathology',
            'sarcoma',
            'glioma',
            'meningioma',
            'pheochromocytoma',
            'thyroid carcinoma',

            # Inflammation (5 topics)
            'acute inflammation',
            'chronic inflammation',
            'granuloma',
            'abscess pathology',
            'necrosis',

            # Organ Pathology (5 topics)
            'liver cirrhosis',
            'fatty liver',
            'kidney pathology',
            'heart pathology',
            'lung pathology',
        ]
    },

    # ==========================================
    # PHASE 3 (P2): LIMITED COVERAGE
    # ==========================================
    'gastrointestinal': {
        'priority': 2,
        'total_available': 75,
        'recommended_download': 15,
        'amc_relevance': 3,
        'topics': [
            'peptic ulcer',
            'inflammatory bowel disease',
            'colorectal cancer',
            'gastroesophageal reflux',
            'pancreatitis',
            'hepatitis',
            'cholecystitis',
            'appendicitis imaging',
        ]
    },

    'infectious_disease': {
        'priority': 3,
        'total_available': 11,
        'recommended_download': 10,
        'amc_relevance': 2,
        'topics': [
            'infectious mononucleosis',
            'sepsis blood',
            'bacterial infection blood',
            'viral infection blood',
        ]
    },
}

# Phase definitions
PHASES = {
    '1': ['hematology', 'dermatology', 'cardiology'],
    '2': ['anatomy', 'bone_marrow', 'respiratory', 'pediatrics', 'pathology'],
    '3': ['gastrointestinal', 'infectious_disease'],
    'all': list(HEAL_TOPICS.keys()),
}

async def download_topic(downloader, specialty, topic, max_images, output_base, delays):
    """Download images for a single topic into its own folder"""

    # Create topic-specific folder: specialty/topic_name
    topic_folder_name = topic.replace(' ', '_').replace('/', '_')
    output_dir = Path(output_base) / specialty / topic_folder_name
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n  Topic: {topic}")
    print(f"  Folder: {output_dir}")

    try:
        # Search and extract IDs
        results = await downloader.search_and_extract_ids(topic, max_results=max_images)

        if not results:
            print(f"    ⚠ No results found")
            return []

        print(f"    ✓ Found {len(results)} items")

        # Download images
        downloaded = await downloader.download_images(results, output_dir)

        if downloaded:
            # Save topic metadata
            json_file, csv_file = save_metadata(downloaded, output_dir, topic_folder_name)
            print(f"    ✓ Downloaded {len(downloaded)} images")
            print(f"    ✓ Metadata: {json_file.name}")

            # Topic delay
            if delays['topic'] > 0:
                await asyncio.sleep(delays['topic'])

            return downloaded
        else:
            print(f"    ⚠ No images downloaded")
            return []

    except Exception as e:
        print(f"    ✗ Error: {e}")
        return []

async def download_specialty(specialty, config, max_per_topic, output_base, show_browser=False, delays=None):
    """Download all topics for a single specialty"""

    if delays is None:
        delays = {'image': 2, 'topic': 5}

    topics = config['topics']
    priority = config['priority']
    total_available = config['total_available']
    recommended = config['recommended_download']

    print(f"\n{'='*70}")
    print(f"SPECIALTY: {specialty.upper().replace('_', ' ')}")
    print(f"{'='*70}")
    print(f"Priority: P{priority}")
    print(f"Available in HEAL: {total_available} items")
    print(f"Topics to search: {len(topics)}")
    print(f"Max per topic: {max_per_topic}")
    print(f"Recommended total: {recommended} images")
    print(f"Estimated downloads: {len(topics) * max_per_topic} images")

    output_dir = Path(output_base) / specialty
    output_dir.mkdir(parents=True, exist_ok=True)

    all_downloads = []

    downloader = HEALPlaywrightDownloader(
        headless=not show_browser,
        slow_mo=500 if show_browser else 0
    )

    # Download each topic in separate folder
    for idx, topic in enumerate(topics, 1):
        print(f"\n[{idx}/{len(topics)}]", end=" ")

        downloaded = await download_topic(
            downloader,
            specialty,
            topic,
            max_per_topic,
            output_base,
            delays
        )

        all_downloads.extend(downloaded)

    # Save specialty summary
    if all_downloads:
        specialty_summary = {
            'specialty': specialty,
            'priority': priority,
            'topics_searched': len(topics),
            'images_downloaded': len(all_downloads),
            'download_time': datetime.now().isoformat(),
        }

        summary_file = output_dir / f'{specialty}_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(specialty_summary, f, indent=2)

        print(f"\n✓ Specialty complete: {specialty}")
        print(f"  Downloaded: {len(all_downloads)} images across {len(topics)} topics")
        print(f"  Summary: {summary_file}")

    return all_downloads

async def main():
    parser = argparse.ArgumentParser(
        description='Comprehensive HEAL batch downloader with full topic coverage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Phase 1: High-priority (hematology, dermatology, cardiology)
  python3 scripts/download_heal_comprehensive.py --phase 1

  # Phase 2: Medium-priority (anatomy, respiratory, etc.)
  python3 scripts/download_heal_comprehensive.py --phase 2

  # All phases (complete download)
  python3 scripts/download_heal_comprehensive.py --phase all

  # Custom specialties
  python3 scripts/download_heal_comprehensive.py \\
      --specialties hematology dermatology \\
      --images-per-topic 20

  # Test run (fast, with browser)
  python3 scripts/download_heal_comprehensive.py \\
      --phase 1 \\
      --images-per-topic 5 \\
      --no-delay \\
      --show-browser
        '''
    )

    parser.add_argument(
        '--phase',
        choices=['1', '2', '3', 'all'],
        help='Download phase (1=P0 high-priority, 2=P1 medium, 3=P2 low, all=everything)'
    )

    parser.add_argument(
        '--specialties',
        nargs='+',
        choices=list(HEAL_TOPICS.keys()),
        help='Specific specialties to download (overrides --phase)'
    )

    parser.add_argument(
        '--images-per-topic',
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
        '--image-delay',
        type=float,
        default=2.0,
        help='Delay between image downloads in seconds (default: 2.0)'
    )

    parser.add_argument(
        '--topic-delay',
        type=float,
        default=5.0,
        help='Delay between topics in seconds (default: 5.0)'
    )

    parser.add_argument(
        '--no-delay',
        action='store_true',
        help='Disable all delays (faster, but less respectful to server)'
    )

    parser.add_argument(
        '--show-browser',
        action='store_true',
        help='Show browser (not headless, for debugging)'
    )

    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Auto-start without confirmation prompt (for automated runs)'
    )

    args = parser.parse_args()

    # Determine which specialties to download
    if args.specialties:
        specialties = args.specialties
    elif args.phase:
        specialties = PHASES[args.phase]
    else:
        parser.error('Must specify either --phase or --specialties')

    # Configure delays
    if args.no_delay:
        delays = {'image': 0, 'topic': 0}
    else:
        delays = {'image': args.image_delay, 'topic': args.topic_delay}

    # Display configuration
    print(f"\n{'='*70}")
    print(f"HEAL Comprehensive Batch Downloader")
    print(f"{'='*70}")
    print(f"Phase: {args.phase if args.phase else 'Custom'}")
    print(f"Specialties: {', '.join(specialties)}")
    print(f"Images per topic: {args.images_per_topic}")
    print(f"Delays: {args.image_delay}s/image, {args.topic_delay}s/topic")
    print(f"Output: {args.output}")
    print(f"")

    # Calculate estimates
    total_topics = sum(len(HEAL_TOPICS[s]['topics']) for s in specialties)
    estimated_images = total_topics * args.images_per_topic
    estimated_time_min = (estimated_images * delays['image'] + total_topics * delays['topic']) / 60

    print(f"Estimates:")
    print(f"  Total topics: {total_topics}")
    print(f"  Max images: {estimated_images}")
    print(f"  Estimated time: {estimated_time_min:.0f} minutes ({estimated_time_min/60:.1f} hours)")
    print(f"")

    # Show specialty breakdown
    print(f"Specialty breakdown:")
    for specialty in specialties:
        config = HEAL_TOPICS[specialty]
        print(f"  {specialty}: {len(config['topics'])} topics × {args.images_per_topic} = {len(config['topics']) * args.images_per_topic} images (P{config['priority']})")
    print(f"")

    if not args.no_delay and not args.yes:
        input("Press Enter to start downloading (Ctrl+C to cancel)...")

    # Download each specialty
    start_time = datetime.now()
    all_downloads = []

    for specialty in specialties:
        config = HEAL_TOPICS[specialty]
        results = await download_specialty(
            specialty,
            config,
            args.images_per_topic,
            args.output,
            show_browser=args.show_browser,
            delays=delays
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
    print(f"  Specialties: {len(specialties)}")
    print(f"  Topics: {total_topics}")
    print(f"  Images downloaded: {len(all_downloads)}")
    print(f"  Total time: {int(duration // 60)}m {int(duration % 60)}s")
    print(f"  Output: {args.output}")
    print(f"")

    # Breakdown by specialty
    print(f"Breakdown:")
    for specialty in specialties:
        count = len([d for d in all_downloads if specialty in d.get('filepath', '')])
        topics_count = len(HEAL_TOPICS[specialty]['topics'])
        print(f"  {specialty}: {count} images ({topics_count} topics)")

    # Save combined metadata
    output_path = Path(args.output)
    combined_json = output_path / f'heal_comprehensive_metadata.json'
    with open(combined_json, 'w') as f:
        json.dump({
            'download_date': end_time.isoformat(),
            'phase': args.phase if args.phase else 'custom',
            'specialties': specialties,
            'total_images': len(all_downloads),
            'images': all_downloads,
        }, f, indent=2)

    print(f"")
    print(f"Combined metadata: {combined_json}")
    print(f"")
    print(f"Next steps:")
    print(f"1. Review images: ls -lh {args.output}/*/*/*.jpg | head -20")
    print(f"2. Check metadata: cat {combined_json} | jq '.total_images'")
    print(f"3. Process metadata: python3 scripts/process_image_metadata.py --source {args.output}")
    print(f"4. Integrate with RAG system")

if __name__ == '__main__':
    asyncio.run(main())
