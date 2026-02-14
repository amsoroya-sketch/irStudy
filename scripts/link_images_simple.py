#!/usr/bin/env python3
"""
Simple image linking script using direct PostgreSQL connection

Usage:
    python scripts/link_images_simple.py --dry-run  # Preview
    python scripts/link_images_simple.py --commit   # Commit changes
"""

import json
import os
import psycopg2
import argparse
from pathlib import Path


def load_image_metadata():
    """Load HEAL image metadata"""
    metadata_path = 'data/medical_images/heal/heal_comprehensive_metadata.json'

    print(f"📂 Loading image metadata from {metadata_path}")

    with open(metadata_path) as f:
        data = json.load(f)

    # Organize by condition for quick lookup
    images_by_condition = {}

    for img in data['images']:
        path = img['filepath']
        parts = path.split('/')

        if len(parts) < 5:
            continue

        condition = parts[4]  # e.g., 'atrial_fibrillation_ECG'

        if condition not in images_by_condition:
            images_by_condition[condition] = {
                'filepath': path,
                'title': img['title'],
                'specialty': parts[3]
            }

    print(f"✅ Loaded {len(data['images'])} images ({len(images_by_condition)} unique conditions)")

    return images_by_condition


def normalize_tag(tag):
    """Normalize tag for matching"""
    return tag.lower().replace('_', ' ').replace('-', ' ').strip()


def find_matching_image(tags, images_by_condition):
    """Find best matching image for given tags"""
    if not tags:
        return None

    # Try exact match first
    for tag in tags:
        if tag in images_by_condition:
            return images_by_condition[tag]

    # Try partial match
    norm_tags = [normalize_tag(tag) for tag in tags]

    for tag in norm_tags:
        for condition, img_info in images_by_condition.items():
            norm_condition = normalize_tag(condition)

            if tag in norm_condition or norm_condition in tag:
                return img_info

    # Keyword matching for common terms
    keywords_map = {
        'atrial fibrillation': 'atrial_fibrillation_ECG',
        'atrial flutter': 'atrial_flutter_ECG',
        'stemi': 'ST_elevation_myocardial_infarction',
        'av block': 'first_degree_AV_block',
        'ventricular tachycardia': 'ventricular_tachycardia_ECG',
    }

    for norm_tag in norm_tags:
        for keyword, condition in keywords_map.items():
            if keyword in norm_tag and condition in images_by_condition:
                return images_by_condition[condition]

    return None


def link_images_to_osces(conn, images_by_condition, specialty=None, limit=None, dry_run=True):
    """Link images to OSCEs"""
    cursor = conn.cursor()

    # Query OSCEs
    query = "SELECT id, osce_id, station_title, specialty, learning_objectives, supporting_documents FROM osces"
    conditions = []
    params = []

    if specialty:
        conditions.append("specialty = %s")
        params.append(specialty)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    osces = cursor.fetchall()

    print(f"\n🔗 Linking images to {len(osces)} OSCEs (specialty={specialty or 'ALL'}, dry_run={dry_run})")

    linked_count = 0
    update_queries = []

    for osce_id, osce_code, station_title, osce_specialty, learning_objectives, supporting_docs in osces:
        # Skip if already has images
        if supporting_docs:
            import json
            docs = json.loads(supporting_docs) if isinstance(supporting_docs, str) else supporting_docs
            if any('heal' in str(doc).lower() for doc in docs):
                continue

        # Extract tags from station_title (e.g., "Acute Coronary Syndrome: STEMI" → ["stemi", "acute", "coronary"])
        tags = []
        if station_title:
            # Split by colon and extract words
            parts = station_title.lower().split(':')
            for part in parts:
                # Split by spaces and common separators
                words = part.replace('-', ' ').replace('(', ' ').replace(')', ' ').split()
                tags.extend([w.strip() for w in words if len(w.strip()) > 3])  # Only words >3 chars

        # Find matching image
        img = find_matching_image(tags, images_by_condition)

        if img:
            linked_count += 1

            if not dry_run:
                # Add image to supporting_documents
                import json
                if not supporting_docs:
                    docs = []
                else:
                    docs = json.loads(supporting_docs) if isinstance(supporting_docs, str) else supporting_docs

                docs.append({
                    'type': 'image',
                    'url': img['filepath'],
                    'caption': img['title']
                })

                update_queries.append((json.dumps(docs), osce_id))

            print(f"  ✓ {osce_code:30s} → {Path(img['filepath']).parts[-2]:40s}")

    # Execute updates
    if not dry_run and update_queries:
        cursor.executemany(
            "UPDATE osces SET supporting_documents = %s WHERE id = %s",
            update_queries
        )
        conn.commit()
        print(f"✅ Committed {linked_count} image links to database")
    else:
        print(f"🔍 DRY RUN: Would link {linked_count} images (not committed)")

    cursor.close()
    return linked_count


def link_images_to_mcqs(conn, images_by_condition, specialty=None, limit=None, dry_run=True):
    """Link images to MCQs"""
    cursor = conn.cursor()

    # Query MCQs
    query = "SELECT id, question_id, specialty, tags, image_url FROM mcqs"
    conditions = []
    params = []

    if specialty:
        conditions.append("specialty = %s")
        params.append(specialty)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    if limit:
        query += f" LIMIT {limit}"

    cursor.execute(query, params)
    mcqs = cursor.fetchall()

    print(f"\n🔗 Linking images to {len(mcqs)} MCQs (specialty={specialty or 'ALL'}, dry_run={dry_run})")

    linked_count = 0
    update_queries = []

    for mcq_id, question_id, mcq_specialty, tags, current_image_url in mcqs:
        # Skip if already has image
        if current_image_url:
            continue

        # Parse tags (JSON array)
        if not tags:
            continue

        # Find matching image
        img = find_matching_image(tags, images_by_condition)

        if img:
            linked_count += 1

            if not dry_run:
                update_queries.append((img['filepath'], img['title'], mcq_id))

            print(f"  ✓ {question_id:30s} → {Path(img['filepath']).parts[-2]:40s}")

    # Execute updates
    if not dry_run and update_queries:
        cursor.executemany(
            "UPDATE mcqs SET image_url = %s, image_caption = %s WHERE id = %s",
            update_queries
        )
        conn.commit()
        print(f"✅ Committed {linked_count} image links to database")
    else:
        print(f"🔍 DRY RUN: Would link {linked_count} images (not committed)")

    cursor.close()
    return linked_count


def main():
    parser = argparse.ArgumentParser(description='Link HEAL images to MCQs and OSCEs')
    parser.add_argument('--specialty', type=str, help='Filter by specialty (cardiology, etc.)')
    parser.add_argument('--limit', type=int, help='Limit number of items to process')
    parser.add_argument('--mcqs-only', action='store_true', help='Only link MCQs')
    parser.add_argument('--osces-only', action='store_true', help='Only link OSCEs')
    parser.add_argument('--dry-run', action='store_true', help='Preview without committing')
    parser.add_argument('--commit', action='store_true', help='Commit changes')

    args = parser.parse_args()

    if args.dry_run and args.commit:
        print("❌ Error: Cannot use both --dry-run and --commit")
        return 1

    dry_run = not args.commit

    # Load image metadata
    images_by_condition = load_image_metadata()

    # Connect to database
    print("\n🔌 Connecting to database...")

    # Get database credentials (same approach as backend)
    database_url = os.getenv('DATABASE_URL')

    if database_url:
        # Use DATABASE_URL if available (Docker environment)
        conn = psycopg2.connect(database_url)
        print("✅ Connected via DATABASE_URL")
    else:
        # Manual connection
        database = os.getenv('DATABASE_NAME', 'irstudy_medical')
        user = os.getenv('DATABASE_USER', 'postgres')

        # Try Docker secret first (when running inside container)
        secret_path = '/run/secrets/db_password'
        if os.path.exists(secret_path):
            # Running inside Docker container
            with open(secret_path) as f:
                password = f.read().strip()
            host = os.getenv('DATABASE_HOST', 'postgres')  # Docker service name
            port = int(os.getenv('DATABASE_PORT', '5432'))  # Internal port
            print("🐳 Running inside Docker container")
        else:
            # Running on host machine
            password = os.getenv('DATABASE_PASSWORD', 'postgres')
            host = os.getenv('DATABASE_HOST', 'localhost')
            port = int(os.getenv('DATABASE_PORT', '5433'))  # External port
            print("🖥️ Running on host machine")

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print(f"✅ Connected to {host}:{port}/{database}")

    try:
        total_mcqs = 0
        total_osces = 0

        # Link MCQs (unless --osces-only)
        if not args.osces_only:
            total_mcqs = link_images_to_mcqs(
                conn,
                images_by_condition,
                specialty=args.specialty,
                limit=args.limit,
                dry_run=dry_run
            )

        # Link OSCEs (unless --mcqs-only)
        if not args.mcqs_only:
            total_osces = link_images_to_osces(
                conn,
                images_by_condition,
                specialty=args.specialty,
                limit=args.limit,
                dry_run=dry_run
            )

        print("\n" + "=" * 80)
        print(f"📊 SUMMARY: Linked {total_mcqs} MCQ images + {total_osces} OSCE images")
        print("=" * 80)

    finally:
        conn.close()

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
