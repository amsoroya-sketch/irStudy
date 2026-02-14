#!/usr/bin/env python3
"""
Link HEAL images to MCQs and OSCEs based on topic matching

This script:
1. Loads HEAL image metadata
2. Queries MCQs/OSCEs from database
3. Matches content tags to image conditions
4. Updates image_url fields in database

Usage:
    python scripts/link_images_to_content.py --specialty cardiology --dry-run
    python scripts/link_images_to_content.py --all --commit
"""

import json
import os
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import argparse

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'src'))
sys.path.insert(0, '/app/src')  # For Docker container

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    from db.models import MCQ, OSCE
    from db.base import get_db_url
except ImportError:
    # Try alternative import for Docker
    from src.db.models import MCQ, OSCE
    from src.db.base import get_db_url


class ImageLinker:
    """Links medical images to MCQs and OSCEs based on topic matching"""

    def __init__(self, metadata_path: str = 'data/medical_images/heal/heal_comprehensive_metadata.json'):
        self.metadata_path = metadata_path
        self.images_by_specialty = defaultdict(list)
        self.images_by_condition = defaultdict(list)
        self.load_image_metadata()

        # Create database session
        db_url = get_db_url()
        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        self.session = Session()

        # Statistics
        self.stats = {
            'mcqs_checked': 0,
            'mcqs_linked': 0,
            'osces_checked': 0,
            'osces_linked': 0,
            'images_used': set(),
        }

    def load_image_metadata(self):
        """Load HEAL image metadata and organize by specialty/condition"""
        print(f"📂 Loading image metadata from {self.metadata_path}")

        with open(self.metadata_path) as f:
            data = json.load(f)

        for img in data['images']:
            path = img['filepath']
            parts = path.split('/')

            if len(parts) < 5:
                continue

            specialty = parts[3]  # e.g., 'cardiology'
            condition = parts[4]  # e.g., 'atrial_fibrillation_ECG'

            img_info = {
                'filepath': path,
                'condition': condition,
                'title': img['title'],
                'description': img.get('description', ''),
                'specialty': specialty
            }

            self.images_by_specialty[specialty].append(img_info)
            self.images_by_condition[condition].append(img_info)

        print(f"✅ Loaded {len(data['images'])} images:")
        for spec, imgs in sorted(self.images_by_specialty.items()):
            print(f"  - {spec:15s}: {len(imgs):3d} images ({len(self.images_by_condition):3d} conditions)")

    def normalize_tag(self, tag: str) -> str:
        """Normalize tag for matching (lowercase, remove special chars)"""
        # Remove underscores, hyphens, convert to lowercase
        normalized = tag.lower().replace('_', ' ').replace('-', ' ')
        # Remove common suffixes
        normalized = re.sub(r'\s+(ecg|criteria|diagnosis|management)$', '', normalized)
        return normalized.strip()

    def find_matching_image(self, tags: List[str], specialty: str) -> Optional[Dict]:
        """
        Find the best matching image for given tags and specialty

        Matching algorithm:
        1. Exact condition match (e.g., 'atrial_fibrillation' → 'atrial_fibrillation_ECG')
        2. Partial match (e.g., 'stemi' → 'ST_elevation_myocardial_infarction')
        3. Specialty fallback (random image from specialty)

        Returns:
            Image info dict or None
        """
        if not tags:
            return None

        # Normalize tags for matching
        normalized_tags = [self.normalize_tag(tag) for tag in tags]

        # Try exact condition match first
        for tag in tags:
            if tag in self.images_by_condition:
                return self.images_by_condition[tag][0]

        # Try partial match with normalized tags
        for norm_tag in normalized_tags:
            for condition, imgs in self.images_by_condition.items():
                norm_condition = self.normalize_tag(condition)

                # Check if tag matches condition or vice versa
                if norm_tag in norm_condition or norm_condition in norm_tag:
                    return imgs[0]

        # Keyword matching for common medical terms
        keywords_map = {
            'atrial fibrillation': 'atrial_fibrillation_ECG',
            'atrial flutter': 'atrial_flutter_ECG',
            'stemi': 'ST_elevation_myocardial_infarction',
            'myocardial infarction': 'ST_elevation_myocardial_infarction',
            'av block': 'first_degree_AV_block',
            'heart block': 'first_degree_AV_block',
            'junctional': 'junctional_tachycardia_ECG',
            'ventricular tachycardia': 'ventricular_tachycardia_ECG',
            'aml': 'acute_myeloid_leukemia',
            'cml': 'chronic_myeloid_leukemia',
            'melanoma': 'melanoma',
            'basal cell': 'basal_cell_carcinoma',
        }

        for norm_tag in normalized_tags:
            for keyword, condition in keywords_map.items():
                if keyword in norm_tag and condition in self.images_by_condition:
                    return self.images_by_condition[condition][0]

        # Fallback: return None (no image for this MCQ)
        # We don't want to assign random images as it may be misleading
        return None

    def link_mcqs(self, specialty: Optional[str] = None, limit: Optional[int] = None, dry_run: bool = True):
        """
        Link images to MCQs

        Args:
            specialty: Filter by specialty (e.g., 'cardiology'), or None for all
            limit: Maximum number of MCQs to process (for testing)
            dry_run: If True, don't commit changes to database
        """
        print(f"\n🔗 Linking images to MCQs (specialty={specialty or 'ALL'}, dry_run={dry_run})")

        # Query MCQs
        query = self.session.query(MCQ)
        if specialty:
            query = query.filter(MCQ.specialty == specialty)
        if limit:
            query = query.limit(limit)

        mcqs = query.all()
        print(f"📊 Found {len(mcqs)} MCQs to process")

        linked_count = 0

        for mcq in mcqs:
            self.stats['mcqs_checked'] += 1

            # Skip if already has image
            if mcq.image_url:
                continue

            # Get tags (JSON array in database)
            tags = mcq.tags if mcq.tags else []

            # Find matching image
            img = self.find_matching_image(tags, mcq.specialty)

            if img:
                linked_count += 1
                self.stats['mcqs_linked'] += 1
                self.stats['images_used'].add(img['filepath'])

                # Update MCQ
                if not dry_run:
                    mcq.image_url = img['filepath']
                    mcq.image_caption = img['title']

                print(f"  ✓ MCQ {mcq.question_id:30s} → {img['condition']:40s}")

                if linked_count % 10 == 0:
                    print(f"    Progress: {linked_count}/{len(mcqs)} linked")

        if not dry_run:
            self.session.commit()
            print(f"✅ Committed {linked_count} image links to database")
        else:
            print(f"🔍 DRY RUN: Would link {linked_count} images (not committed)")

        return linked_count

    def link_osces(self, specialty: Optional[str] = None, limit: Optional[int] = None, dry_run: bool = True):
        """
        Link images to OSCEs

        Args:
            specialty: Filter by specialty, or None for all
            limit: Maximum number of OSCEs to process
            dry_run: If True, don't commit changes
        """
        print(f"\n🔗 Linking images to OSCEs (specialty={specialty or 'ALL'}, dry_run={dry_run})")

        # Query OSCEs
        query = self.session.query(OSCE)
        if specialty:
            query = query.filter(OSCE.specialty == specialty)
        if limit:
            query = query.limit(limit)

        osces = query.all()
        print(f"📊 Found {len(osces)} OSCEs to process")

        linked_count = 0

        for osce in osces:
            self.stats['osces_checked'] += 1

            # Get supporting_documents (JSON array)
            supporting_docs = osce.supporting_documents if osce.supporting_documents else []

            # Skip if already has images
            if supporting_docs and any('heal' in str(doc).lower() for doc in supporting_docs):
                continue

            # Get tags from learning objectives or key points
            tags = []
            if osce.learning_objectives:
                # Extract keywords from learning objectives
                tags.extend([obj.lower() for obj in osce.learning_objectives if isinstance(obj, str)])

            # Find matching image
            img = self.find_matching_image(tags, osce.specialty)

            if img:
                linked_count += 1
                self.stats['osces_linked'] += 1
                self.stats['images_used'].add(img['filepath'])

                # Update OSCE supporting_documents
                if not dry_run:
                    if not supporting_docs:
                        supporting_docs = []
                    supporting_docs.append({
                        'type': 'image',
                        'url': img['filepath'],
                        'caption': img['title']
                    })
                    osce.supporting_documents = supporting_docs

                print(f"  ✓ OSCE {osce.osce_id:30s} → {img['condition']:40s}")

        if not dry_run:
            self.session.commit()
            print(f"✅ Committed {linked_count} image links to database")
        else:
            print(f"🔍 DRY RUN: Would link {linked_count} images (not committed)")

        return linked_count

    def print_summary(self):
        """Print final statistics"""
        print("\n" + "=" * 80)
        print("📊 IMAGE LINKING SUMMARY")
        print("=" * 80)
        print(f"MCQs checked:       {self.stats['mcqs_checked']:4d}")
        print(f"MCQs linked:        {self.stats['mcqs_linked']:4d} ({self.stats['mcqs_linked']/max(1,self.stats['mcqs_checked'])*100:.1f}%)")
        print(f"OSCEs checked:      {self.stats['osces_checked']:4d}")
        print(f"OSCEs linked:       {self.stats['osces_linked']:4d} ({self.stats['osces_linked']/max(1,self.stats['osces_checked'])*100:.1f}%)")
        print(f"Unique images used: {len(self.stats['images_used']):4d}")
        print("=" * 80)

    def close(self):
        """Close database session"""
        self.session.close()


def main():
    parser = argparse.ArgumentParser(description='Link HEAL images to MCQs and OSCEs')
    parser.add_argument('--specialty', type=str, help='Filter by specialty (cardiology, hematology, dermatology)')
    parser.add_argument('--all', action='store_true', help='Process all specialties')
    parser.add_argument('--mcqs-only', action='store_true', help='Only link MCQs')
    parser.add_argument('--osces-only', action='store_true', help='Only link OSCEs')
    parser.add_argument('--limit', type=int, help='Limit number of items to process (for testing)')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without committing')
    parser.add_argument('--commit', action='store_true', help='Commit changes to database')

    args = parser.parse_args()

    # Validate arguments
    if not args.all and not args.specialty:
        print("❌ Error: Must specify --specialty or --all")
        parser.print_help()
        return 1

    if args.dry_run and args.commit:
        print("❌ Error: Cannot use both --dry-run and --commit")
        return 1

    # Default to dry run if neither specified
    dry_run = not args.commit

    try:
        linker = ImageLinker()

        specialties = [args.specialty] if args.specialty else ['cardiology', 'hematology', 'dermatology']

        for specialty in specialties:
            if not args.osces_only:
                linker.link_mcqs(specialty=specialty, limit=args.limit, dry_run=dry_run)

            if not args.mcqs_only:
                linker.link_osces(specialty=specialty, limit=args.limit, dry_run=dry_run)

        linker.print_summary()
        linker.close()

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
