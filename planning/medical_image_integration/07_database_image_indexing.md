# Task 07: Database Image Indexing

**Duration:** 3 hours
**Priority:** P1
**Dependencies:** Task 05 (Citation Enrichment), Task 06 (CDN Upload)
**Output:** Images indexed in PostgreSQL with full-text search

---

## Objective

Create PostgreSQL database tables for medical images with comprehensive indexing, full-text search capabilities, and relationships ready for linking to MCQs/OSCEs.

---

## Scope

### In Scope
- Design database schema for medical images
- Create migration scripts (Alembic)
- Load metadata JSON into database
- Create indexes for fast queries
- Implement full-text search (PostgreSQL tsvector)
- Create views for common queries
- Validate data integrity

### Out of Scope
- Linking images to MCQs/OSCEs (Task 09)
- RAG integration (Task 08)
- Image content analysis (future AI feature)

---

## Prerequisites

### Completed Tasks
- ✅ Task 05: Citations added to metadata
- ✅ Task 06: CDN URLs available

### Database
- PostgreSQL 15+ running
- Alembic migrations configured
- Database URL available

### Metadata
- `data/processed_metadata/heal_metadata_cited.json` complete

---

## Implementation Steps

### Step 1: Database Schema Design (30 min)

**File:** `backend/src/db/models.py` (add new models)

```python
from sqlalchemy import (
    Column, String, Integer, Text, JSON, DateTime, Index,
    ForeignKey, Enum as SQLEnum, Float
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from .base import Base
import enum


class ImageModality(str, enum.Enum):
    """Medical image modality types"""
    ECG = "ECG"
    XRAY = "X-Ray"
    CT = "CT Scan"
    MRI = "MRI"
    ULTRASOUND = "Ultrasound"
    MICROSCOPY = "Microscopy"
    CLINICAL_PHOTO = "Clinical Photography"
    HISTOLOGY = "Histology"
    ENDOSCOPY = "Endoscopy"
    UNKNOWN = "Unknown"


class ImageSource(str, enum.Enum):
    """Image source databases"""
    HEAL = "heal"
    MEDPIX = "medpix"
    NIH = "nih"
    ZANATOMY = "zanatomy"
    OTHER = "other"


class MedicalImage(Base):
    """Medical images with metadata and citations"""
    __tablename__ = "medical_images"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Unique identifiers
    image_id = Column(String(50), unique=True, index=True, nullable=False)
    source = Column(SQLEnum(ImageSource), index=True, nullable=False)
    source_image_id = Column(String(100), nullable=True)  # Original ID from source

    # File information
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=True)  # Local path (if exists)
    cdn_url = Column(String(500), nullable=False)  # Cloudflare R2 URL
    object_key = Column(String(500), nullable=True)  # R2 object key

    # Medical classification
    specialty = Column(SQLEnum(MedicalSpecialty), index=True, nullable=False)
    topic = Column(String(255), index=True, nullable=False)
    subtopic = Column(String(255), nullable=True)
    clinical_finding = Column(Text, nullable=True)  # What the image shows
    modality = Column(SQLEnum(ImageModality), index=True, nullable=True)
    body_part = Column(String(100), nullable=True)
    age_group = Column(String(50), nullable=True)  # Adult, Pediatric, Neonate

    # Image metadata
    width_px = Column(Integer, nullable=True)
    height_px = Column(Integer, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    format = Column(String(20), nullable=True)  # JPEG, PNG

    # Citations and licensing
    citation = Column(Text, nullable=False)
    citation_short = Column(String(255), nullable=True)
    source_url = Column(String(500), nullable=True)
    license = Column(String(100), nullable=False)
    attribution = Column(Text, nullable=False)
    publisher = Column(String(255), nullable=True)
    accessed_date = Column(String(20), nullable=True)  # YYYY-MM-DD

    # Search optimization
    search_vector = Column(TSVECTOR, nullable=True)  # Full-text search

    # Tags for flexible categorization
    tags = Column(JSON, nullable=True)  # List of strings

    # Relationships (for future use)
    # mcq_links = relationship("MCQImageLink", back_populates="image")
    # osce_links = relationship("OSCEImageLink", back_populates="image")

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        # Composite indexes for common queries
        Index('idx_images_specialty_topic', 'specialty', 'topic'),
        Index('idx_images_specialty_modality', 'specialty', 'modality'),
        Index('idx_images_source_specialty', 'source', 'specialty'),

        # Full-text search index
        Index('idx_images_search', 'search_vector', postgresql_using='gin'),
    )


class MCQImageLink(Base):
    """Junction table linking MCQs to medical images"""
    __tablename__ = "mcq_image_links"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    mcq_id = Column(Integer, ForeignKey('mcqs.id', ondelete='CASCADE'), nullable=False)
    image_id = Column(Integer, ForeignKey('medical_images.id', ondelete='CASCADE'), nullable=False)

    # Link metadata
    relevance_score = Column(Float, nullable=True)  # 0.0 to 1.0
    link_type = Column(String(50), nullable=True)  # 'primary', 'supplementary'
    match_method = Column(String(50), nullable=True)  # 'automated', 'manual', 'expert_review'
    verified = Column(Boolean, default=False)  # Medical expert verified

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)  # User or system

    # Relationships
    mcq = relationship("MCQ", back_populates="image_links")
    image = relationship("MedicalImage", back_populates="mcq_links")

    __table_args__ = (
        # Unique constraint: one MCQ can't have same image twice
        UniqueConstraint('mcq_id', 'image_id', name='uq_mcq_image'),
        Index('idx_mcq_image_mcq', 'mcq_id'),
        Index('idx_mcq_image_image', 'image_id'),
    )


class OSCEImageLink(Base):
    """Junction table linking OSCEs to medical images"""
    __tablename__ = "osce_image_links"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys
    osce_id = Column(Integer, ForeignKey('osces.id', ondelete='CASCADE'), nullable=False)
    image_id = Column(Integer, ForeignKey('medical_images.id', ondelete='CASCADE'), nullable=False)

    # Link metadata
    relevance_score = Column(Float, nullable=True)
    link_type = Column(String(50), nullable=True)
    match_method = Column(String(50), nullable=True)
    verified = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)

    # Relationships
    osce = relationship("OSCE", back_populates="image_links")
    image = relationship("MedicalImage", back_populates="osce_links")

    __table_args__ = (
        UniqueConstraint('osce_id', 'image_id', name='uq_osce_image'),
        Index('idx_osce_image_osce', 'osce_id'),
        Index('idx_osce_image_image', 'image_id'),
    )
```

---

### Step 2: Alembic Migration (30 min)

**Create migration:**

```bash
cd backend
alembic revision --autogenerate -m "Add medical images tables"
```

**File:** `backend/alembic/versions/YYYYMMDD_HHMM_add_medical_images_tables.py`

```python
"""Add medical images tables

Revision ID: abc123def456
Revises: 20260201_1430_001_initial_schema
Create Date: 2026-02-03 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'abc123def456'
down_revision = '20260201_1430_001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    # Create ImageSource enum
    image_source_enum = postgresql.ENUM(
        'heal', 'medpix', 'nih', 'zanatomy', 'other',
        name='imagesource'
    )
    image_source_enum.create(op.get_bind())

    # Create ImageModality enum
    image_modality_enum = postgresql.ENUM(
        'ECG', 'X-Ray', 'CT Scan', 'MRI', 'Ultrasound',
        'Microscopy', 'Clinical Photography', 'Histology',
        'Endoscopy', 'Unknown',
        name='imagemodality'
    )
    image_modality_enum.create(op.get_bind())

    # Create medical_images table
    op.create_table(
        'medical_images',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.String(50), nullable=False),
        sa.Column('source', image_source_enum, nullable=False),
        sa.Column('source_image_id', sa.String(100), nullable=True),
        sa.Column('filename', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(500), nullable=True),
        sa.Column('cdn_url', sa.String(500), nullable=False),
        sa.Column('object_key', sa.String(500), nullable=True),
        sa.Column('specialty', sa.Enum('MedicalSpecialty'), nullable=False),
        sa.Column('topic', sa.String(255), nullable=False),
        sa.Column('subtopic', sa.String(255), nullable=True),
        sa.Column('clinical_finding', sa.Text(), nullable=True),
        sa.Column('modality', image_modality_enum, nullable=True),
        sa.Column('body_part', sa.String(100), nullable=True),
        sa.Column('age_group', sa.String(50), nullable=True),
        sa.Column('width_px', sa.Integer(), nullable=True),
        sa.Column('height_px', sa.Integer(), nullable=True),
        sa.Column('file_size_bytes', sa.Integer(), nullable=True),
        sa.Column('format', sa.String(20), nullable=True),
        sa.Column('citation', sa.Text(), nullable=False),
        sa.Column('citation_short', sa.String(255), nullable=True),
        sa.Column('source_url', sa.String(500), nullable=True),
        sa.Column('license', sa.String(100), nullable=False),
        sa.Column('attribution', sa.Text(), nullable=False),
        sa.Column('publisher', sa.String(255), nullable=True),
        sa.Column('accessed_date', sa.String(20), nullable=True),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column('tags', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index('idx_images_image_id', 'medical_images', ['image_id'], unique=True)
    op.create_index('idx_images_source', 'medical_images', ['source'])
    op.create_index('idx_images_specialty', 'medical_images', ['specialty'])
    op.create_index('idx_images_topic', 'medical_images', ['topic'])
    op.create_index('idx_images_modality', 'medical_images', ['modality'])
    op.create_index('idx_images_specialty_topic', 'medical_images', ['specialty', 'topic'])
    op.create_index('idx_images_specialty_modality', 'medical_images', ['specialty', 'modality'])
    op.create_index('idx_images_source_specialty', 'medical_images', ['source', 'specialty'])
    op.create_index('idx_images_search', 'medical_images', ['search_vector'], postgresql_using='gin')

    # Create MCQ-Image link table
    op.create_table(
        'mcq_image_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mcq_id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('link_type', sa.String(50), nullable=True),
        sa.Column('match_method', sa.String(50), nullable=True),
        sa.Column('verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['mcq_id'], ['mcqs.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['medical_images.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('mcq_id', 'image_id', name='uq_mcq_image')
    )

    op.create_index('idx_mcq_image_mcq', 'mcq_image_links', ['mcq_id'])
    op.create_index('idx_mcq_image_image', 'mcq_image_links', ['image_id'])

    # Create OSCE-Image link table
    op.create_table(
        'osce_image_links',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('osce_id', sa.Integer(), nullable=False),
        sa.Column('image_id', sa.Integer(), nullable=False),
        sa.Column('relevance_score', sa.Float(), nullable=True),
        sa.Column('link_type', sa.String(50), nullable=True),
        sa.Column('match_method', sa.String(50), nullable=True),
        sa.Column('verified', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['osce_id'], ['osces.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['image_id'], ['medical_images.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('osce_id', 'image_id', name='uq_osce_image')
    )

    op.create_index('idx_osce_image_osce', 'osce_image_links', ['osce_id'])
    op.create_index('idx_osce_image_image', 'osce_image_links', ['image_id'])

    # Create trigger for search_vector auto-update
    op.execute("""
        CREATE FUNCTION medical_images_search_trigger() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector :=
            setweight(to_tsvector('english', COALESCE(NEW.topic, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(NEW.clinical_finding, '')), 'B') ||
            setweight(to_tsvector('english', COALESCE(NEW.subtopic, '')), 'C') ||
            setweight(to_tsvector('english', COALESCE(NEW.specialty::text, '')), 'D');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;

        CREATE TRIGGER medical_images_search_update
        BEFORE INSERT OR UPDATE ON medical_images
        FOR EACH ROW EXECUTE FUNCTION medical_images_search_trigger();
    """)


def downgrade():
    # Drop trigger
    op.execute("DROP TRIGGER IF EXISTS medical_images_search_update ON medical_images;")
    op.execute("DROP FUNCTION IF EXISTS medical_images_search_trigger();")

    # Drop tables
    op.drop_table('osce_image_links')
    op.drop_table('mcq_image_links')
    op.drop_table('medical_images')

    # Drop enums
    op.execute('DROP TYPE IF EXISTS imagemodality;')
    op.execute('DROP TYPE IF EXISTS imagesource;')
```

**Run migration:**

```bash
alembic upgrade head
```

---

### Step 3: Data Loading Script (1 hour)

**File:** `scripts/index_images.py`

```python
#!/usr/bin/env python3
"""
Load medical image metadata into PostgreSQL database.

Usage:
    python3 scripts/index_images.py \\
        --metadata data/processed_metadata/heal_metadata_cited.json \\
        --db-url postgresql://user:pass@localhost/irstudy
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tqdm import tqdm

from src.db.models import MedicalImage, ImageSource, ImageModality, MedicalSpecialty


def normalize_enum(value: str, enum_class):
    """Normalize string to enum value"""
    try:
        # Try direct match
        return enum_class[value.upper().replace(' ', '_').replace('-', '_')]
    except KeyError:
        # Try value match
        for member in enum_class:
            if member.value.lower() == value.lower():
                return member
        # Return first member as fallback
        return list(enum_class)[0]


def load_images_to_database(
    metadata_file: Path,
    db_url: str
) -> Dict:
    """Load medical images into database"""

    # Load metadata
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images_data = data['images']

    print(f"\n{'='*70}")
    print(f"Medical Image Database Indexing")
    print(f"{'='*70}")
    print(f"Metadata file: {metadata_file}")
    print(f"Total images: {len(images_data)}")
    print()

    # Create database connection
    engine = create_engine(db_url)

    stats = {
        'total_images': len(images_data),
        'inserted': 0,
        'updated': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }

    with Session(engine) as db:
        for img_data in tqdm(images_data, desc="Indexing images"):
            try:
                # Check if image already exists
                existing = db.query(MedicalImage).filter(
                    MedicalImage.image_id == img_data['image_id']
                ).first()

                # Normalize enums
                source = normalize_enum(img_data['source'], ImageSource)
                specialty = normalize_enum(img_data['specialty'], MedicalSpecialty)
                modality = normalize_enum(img_data.get('modality', 'Unknown'), ImageModality)

                # Prepare image object
                image = MedicalImage(
                    image_id=img_data['image_id'],
                    source=source,
                    source_image_id=img_data.get('source_image_id'),
                    filename=img_data['filename'],
                    file_path=img_data.get('file_path'),
                    cdn_url=img_data['cdn_url'],
                    object_key=img_data.get('object_key'),
                    specialty=specialty,
                    topic=img_data['topic'],
                    subtopic=img_data.get('subtopic'),
                    clinical_finding=img_data.get('clinical_finding'),
                    modality=modality,
                    body_part=img_data.get('body_part'),
                    age_group=img_data.get('age_group'),
                    width_px=img_data.get('width_px'),
                    height_px=img_data.get('height_px'),
                    file_size_bytes=img_data.get('file_size_bytes'),
                    format=img_data.get('format'),
                    citation=img_data['citation'],
                    citation_short=img_data.get('citation_short'),
                    source_url=img_data.get('source_url'),
                    license=img_data['license'],
                    attribution=img_data['attribution'],
                    publisher=img_data.get('publisher'),
                    accessed_date=img_data.get('accessed_date'),
                    tags=img_data.get('tags', []),
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )

                if existing:
                    # Update existing
                    for key, value in image.__dict__.items():
                        if key not in ['_sa_instance_state', 'id', 'created_at']:
                            setattr(existing, key, value)
                    stats['updated'] += 1
                else:
                    # Insert new
                    db.add(image)
                    stats['inserted'] += 1

            except Exception as e:
                stats['failed'] += 1
                stats['errors'].append({
                    'image_id': img_data.get('image_id', 'UNKNOWN'),
                    'error': str(e)
                })

        # Commit all changes
        db.commit()

    print(f"\n{'='*70}")
    print(f"Indexing Complete!")
    print(f"{'='*70}")
    print(f"Inserted: {stats['inserted']}")
    print(f"Updated: {stats['updated']}")
    print(f"Failed: {stats['failed']}")

    if stats['errors']:
        print(f"\nErrors ({len(stats['errors'])}):")
        for err in stats['errors'][:5]:
            print(f"  - {err['image_id']}: {err['error']}")

    return stats


def main():
    parser = argparse.ArgumentParser(description='Index medical images in database')

    parser.add_argument(
        '--metadata',
        type=Path,
        required=True,
        help='Metadata JSON file'
    )

    parser.add_argument(
        '--db-url',
        default=None,
        help='Database URL (or use DATABASE_URL env)'
    )

    args = parser.parse_args()

    db_url = args.db_url or os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1

    stats = load_images_to_database(args.metadata, db_url)

    print("\n✓ Indexing complete!")
    return 0


if __name__ == "__main__":
    import os
    exit(main())
```

---

### Step 4: Full-Text Search Testing (30 min)

**Test search queries:**

```sql
-- Search by topic
SELECT image_id, topic, specialty, modality
FROM medical_images
WHERE search_vector @@ to_tsquery('english', 'melanoma');

-- Search by clinical finding
SELECT image_id, clinical_finding, topic
FROM medical_images
WHERE search_vector @@ to_tsquery('english', 'acute & myeloid & leukemia');

-- Ranked search
SELECT
    image_id,
    topic,
    ts_rank(search_vector, query) AS rank
FROM
    medical_images,
    to_tsquery('english', 'ecg | electrocardiogram') AS query
WHERE
    search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- Combined filters
SELECT COUNT(*)
FROM medical_images
WHERE specialty = 'CARDIOLOGY'
  AND modality = 'ECG'
  AND search_vector @@ to_tsquery('english', 'atrial & fibrillation');
```

---

## Testing

### Integration Test

```bash
# Run migration
cd backend
alembic upgrade head

# Verify tables created
psql -d irstudy -c "\\dt"

# Load images
python3 scripts/index_images.py \
    --metadata data/processed_metadata/heal_metadata_cited.json \
    --db-url postgresql://user:pass@localhost/irstudy

# Verify data
psql -d irstudy -c "SELECT COUNT(*) FROM medical_images;"
# Expected: 1137

# Test search
psql -d irstudy -c "SELECT image_id, topic FROM medical_images WHERE search_vector @@ to_tsquery('melanoma') LIMIT 5;"
```

---

## Success Criteria

- ✅ Database migration runs successfully
- ✅ All 3 tables created (medical_images, mcq_image_links, osce_image_links)
- ✅ All indexes created
- ✅ All 1,137 images indexed
- ✅ Full-text search works (<50ms query time)
- ✅ No data integrity errors
- ✅ Enums correctly mapped
- ✅ Search trigger functioning

---

## Next Task

After completion, proceed to **Task 09: Image Content Linking**

File: `09_image_content_linking.md`

**Note:** Task 08 (RAG Integration) can be done in parallel or after Task 09.
