#!/usr/bin/env python3
"""
Index medical images in PostgreSQL database

Usage:
    python3 scripts/index_images.py \
        --metadata data/image_metadata.json \
        --db-url postgresql://user:pass@localhost/irstudy

Requirements:
    pip3 install psycopg2-binary tqdm
"""

import json
import argparse
from pathlib import Path
import psycopg2
from psycopg2.extras import execute_values
from tqdm import tqdm

def create_schema(conn):
    """Create medical_images table if not exists"""

    schema_sql = """
    -- Medical images table
    CREATE TABLE IF NOT EXISTS medical_images (
        id SERIAL PRIMARY KEY,
        external_id VARCHAR(255) UNIQUE NOT NULL,
        source VARCHAR(50) NOT NULL,
        title TEXT NOT NULL,
        modality VARCHAR(100),

        -- Clinical context
        diagnosis TEXT,
        body_part VARCHAR(100),
        patient_age INTEGER,
        patient_sex VARCHAR(10),
        clinical_history TEXT,
        findings TEXT,

        -- Citation metadata
        citation_text TEXT NOT NULL,
        license VARCHAR(50) NOT NULL,
        source_url TEXT,

        -- Storage
        cdn_url TEXT NOT NULL,
        thumbnail_url TEXT,
        file_size_kb INTEGER,
        width INTEGER,
        height INTEGER,
        file_hash VARCHAR(32) UNIQUE,

        -- Search/filtering
        specialty VARCHAR(100),
        amc_relevance SMALLINT CHECK (amc_relevance BETWEEN 1 AND 5),
        tags TEXT[],

        -- Timestamps
        created_at TIMESTAMP DEFAULT NOW(),
        updated_at TIMESTAMP DEFAULT NOW()
    );

    -- Indexes for fast searching
    CREATE INDEX IF NOT EXISTS idx_images_source ON medical_images(source);
    CREATE INDEX IF NOT EXISTS idx_images_modality ON medical_images(modality);
    CREATE INDEX IF NOT EXISTS idx_images_specialty ON medical_images(specialty);
    CREATE INDEX IF NOT EXISTS idx_images_tags ON medical_images USING GIN(tags);
    CREATE INDEX IF NOT EXISTS idx_images_diagnosis ON medical_images USING GIN(to_tsvector('english', diagnosis));

    -- Full-text search index
    CREATE INDEX IF NOT EXISTS idx_images_fulltext
        ON medical_images
        USING GIN(to_tsvector('english', title || ' ' || COALESCE(diagnosis, '') || ' ' || COALESCE(findings, '')));
    """

    with conn.cursor() as cur:
        cur.execute(schema_sql)
        conn.commit()

    print("✓ Database schema created")

def index_images(metadata_json, db_url, skip_existing=True):
    """Index images from metadata JSON into PostgreSQL"""

    # Load metadata
    with open(metadata_json) as f:
        images = json.load(f)

    print(f"Found {len(images)} images in metadata")

    # Filter out images without CDN URLs
    images_with_cdn = [img for img in images if img.get('cdn_url')]
    images_without_cdn = len(images) - len(images_with_cdn)

    if images_without_cdn > 0:
        print(f"⚠️  {images_without_cdn} images skipped (no CDN URL)")
        print(f"   Run: python3 scripts/upload_to_cdn.py first")

    images = images_with_cdn

    if not images:
        print("✗ No images with CDN URLs to index")
        return

    # Connect to database
    try:
        conn = psycopg2.connect(db_url)
        print(f"✓ Connected to database")
    except Exception as e:
        print(f"✗ Database connection error: {e}")
        return

    # Create schema
    create_schema(conn)

    # Prepare data for insertion
    insert_sql = """
    INSERT INTO medical_images (
        external_id, source, title, modality,
        diagnosis, body_part, patient_age, patient_sex,
        clinical_history, findings,
        citation_text, license, source_url,
        cdn_url, thumbnail_url, file_size_kb, width, height, file_hash,
        specialty, amc_relevance, tags
    ) VALUES %s
    ON CONFLICT (external_id) DO UPDATE SET
        title = EXCLUDED.title,
        modality = EXCLUDED.modality,
        diagnosis = EXCLUDED.diagnosis,
        findings = EXCLUDED.findings,
        cdn_url = EXCLUDED.cdn_url,
        thumbnail_url = EXCLUDED.thumbnail_url,
        updated_at = NOW()
    """

    # Build values list
    values = []
    for img in images:
        # Generate external_id if missing
        external_id = img.get('external_id')
        if not external_id:
            source = img.get('source', 'unknown')
            file_hash = img.get('file_hash', 'unknown')
            external_id = f"{source}_{file_hash[:12]}"

        values.append((
            external_id,
            img.get('source', 'unknown'),
            img.get('title', 'Untitled'),
            img.get('modality'),
            img.get('diagnosis'),
            img.get('body_part'),
            img.get('patient_age'),
            img.get('patient_sex'),
            img.get('clinical_history'),
            img.get('findings'),
            img.get('citation', f"({img.get('source', 'Unknown')}, accessed 2026-02-03)"),
            img.get('license', 'Unknown'),
            img.get('source_url'),
            img.get('cdn_url'),
            img.get('thumbnail_url'),
            img.get('file_size_kb'),
            img.get('width'),
            img.get('height'),
            img.get('file_hash'),
            img.get('specialty'),
            img.get('amc_relevance'),
            img.get('tags', [])
        ))

    # Insert in batches
    batch_size = 100
    inserted_count = 0
    updated_count = 0

    with conn.cursor() as cur:
        for i in tqdm(range(0, len(values), batch_size), desc="Indexing images"):
            batch = values[i:i+batch_size]

            try:
                execute_values(cur, insert_sql, batch)
                conn.commit()
                inserted_count += len(batch)
            except Exception as e:
                print(f"\n✗ Batch insert error: {e}")
                conn.rollback()

    # Get statistics
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM medical_images")
        total_in_db = cur.fetchone()[0]

        cur.execute("SELECT source, COUNT(*) FROM medical_images GROUP BY source ORDER BY COUNT(*) DESC")
        source_counts = cur.fetchall()

        cur.execute("SELECT specialty, COUNT(*) FROM medical_images WHERE specialty IS NOT NULL GROUP BY specialty ORDER BY COUNT(*) DESC")
        specialty_counts = cur.fetchall()

    conn.close()

    print(f"\n{'='*50}")
    print("Indexing Complete")
    print(f"{'='*50}")
    print(f"Images processed: {len(values)}")
    print(f"Total in database: {total_in_db}")
    print(f"\nBreakdown by source:")
    for source, count in source_counts:
        print(f"  {source}: {count} images")

    print(f"\nBreakdown by specialty:")
    for specialty, count in specialty_counts:
        print(f"  {specialty}: {count} images")

    print(f"\nNext steps:")
    print(f"1. Test image search: SELECT * FROM medical_images WHERE diagnosis ILIKE '%pneumonia%'")
    print(f"2. Update amc_relevance ratings (1-5)")
    print(f"3. Add tags for better search")
    print(f"4. Integrate with multimodal RAG service")

def main():
    parser = argparse.ArgumentParser(
        description='Index medical images in PostgreSQL database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Index images in database
  python3 scripts/index_images.py \\
      --metadata data/image_metadata.json \\
      --db-url postgresql://irstudy:password@localhost/irstudy

  # Use environment variable for database URL
  export DATABASE_URL="postgresql://user:pass@localhost/irstudy"
  python3 scripts/index_images.py \\
      --metadata data/image_metadata.json

Database Schema:
  The script creates a 'medical_images' table with:
  - Clinical metadata (diagnosis, modality, findings)
  - Patient information (age, sex, history)
  - Citation data (source, license, URL)
  - Storage URLs (CDN, thumbnails)
  - Search indexes (full-text, specialty, tags)
        '''
    )

    parser.add_argument(
        '--metadata',
        required=True,
        help='Metadata JSON file from process_image_metadata.py'
    )
    parser.add_argument(
        '--db-url',
        help='PostgreSQL connection URL (or use DATABASE_URL env var)'
    )

    args = parser.parse_args()

    # Get database URL
    import os
    db_url = args.db_url or os.getenv('DATABASE_URL')

    if not db_url:
        print("✗ Database URL required:")
        print("  - Use --db-url flag, or")
        print("  - Set DATABASE_URL environment variable")
        return 1

    # Validate metadata file
    if not Path(args.metadata).exists():
        print(f"✗ Metadata file not found: {args.metadata}")
        return 1

    # Index images
    index_images(args.metadata, db_url)

    return 0

if __name__ == '__main__':
    exit(main())
