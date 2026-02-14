# Task 09: Image Content Linking

**Duration:** 8 hours
**Priority:** P0 (Critical Path)
**Dependencies:** Task 07 (Database Image Indexing)
**Output:** 70%+ MCQs/OSCEs linked to relevant images

---

## Objective

Automatically link medical images to MCQs and OSCEs using topic matching, keyword extraction, and fuzzy matching, with manual verification for high-confidence assignments.

---

## Scope

### In Scope
- Automated linking based on specialty + topic matching
- Keyword-based matching for subtopics
- Fuzzy string matching for topic variations
- Relevance scoring for each link
- Manual verification workflow
- Generate linking report for medical expert review
- Update MCQ/OSCE records with image URLs
- Handle edge cases (no matches, multiple matches)

### Out of Scope
- AI-based image content analysis (future)
- Automatic link updates when new images added (future)
- User-generated image uploads

---

## Prerequisites

### Completed Tasks
- ✅ Task 01: MCQs/OSCEs in database
- ✅ Task 07: Images indexed in database

### Database State
- 1,000+ MCQs in `mcqs` table
- 140+ OSCEs in `osces` table
- 1,137 images in `medical_images` table

---

## Implementation Steps

### Step 1: Topic Mapping Table (30 min)

Create mapping between MCQ/OSCE topics and image topics to handle variations.

**File:** `data/config/topic_mapping.json`

```json
{
  "specialty_mappings": {
    "CARDIOLOGY": "cardiology",
    "RESPIRATORY": "respiratory",
    "PSYCHIATRY": "psychiatry"
  },
  "topic_mappings": {
    "Acute Coronary Syndrome": [
      "ST Elevation Myocardial Infarction",
      "STEMI ECG",
      "Non-ST Elevation MI",
      "NSTEMI",
      "Unstable Angina"
    ],
    "Atrial Fibrillation": [
      "Atrial Fibrillation ECG",
      "AF ECG",
      "AFib"
    ],
    "Acute Myeloid Leukemia": [
      "Acute Myeloid Leukemia",
      "AML",
      "Acute Leukemia"
    ],
    "Melanoma": [
      "Melanoma",
      "Malignant Melanoma",
      "Skin Cancer Melanoma"
    ]
  },
  "keyword_rules": {
    "ECG": {
      "requires_modality": "ECG",
      "boost_score": 0.2
    },
    "X-ray": {
      "requires_modality": "X-Ray",
      "boost_score": 0.2
    },
    "Histology": {
      "requires_modality": ["Microscopy", "Histology"],
      "boost_score": 0.2
    }
  }
}
```

---

### Step 2: Image Linking Algorithm (2 hours)

**File:** `scripts/link_images_to_content.py`

```python
#!/usr/bin/env python3
"""
Link medical images to MCQs and OSCEs.

Linking strategies:
1. Exact specialty + topic match (score: 1.0)
2. Specialty + fuzzy topic match (score: 0.7-0.9)
3. Specialty + keyword match in subtopic (score: 0.5-0.7)
4. Manual verification for score <0.8

Usage:
    python3 scripts/link_images_to_content.py \\
        --db-url postgresql://user:pass@localhost/irstudy \\
        --mapping data/config/topic_mapping.json \\
        --min-score 0.5 \\
        --dry-run
"""

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from fuzzywuzzy import fuzz
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.db.models import MCQ, OSCE, MedicalImage, MCQImageLink, OSCEImageLink


class ImageLinker:
    """Link images to MCQs and OSCEs"""

    def __init__(self, mapping_file: Path, min_score: float = 0.5):
        """
        Initialize linker.

        Args:
            mapping_file: Topic mapping JSON file
            min_score: Minimum relevance score (0.0-1.0)
        """
        self.min_score = min_score

        # Load mappings
        with open(mapping_file, 'r') as f:
            mappings = json.load(f)

        self.topic_mappings = mappings.get('topic_mappings', {})
        self.keyword_rules = mappings.get('keyword_rules', {})

    def find_matching_images(
        self,
        specialty: str,
        topic: str,
        subtopic: Optional[str],
        db: Session
    ) -> List[Tuple[MedicalImage, float]]:
        """
        Find images matching MCQ/OSCE topic.

        Returns:
            List of (image, score) tuples, sorted by score descending
        """
        matches = []

        # Query images by specialty
        images = db.query(MedicalImage).filter(
            MedicalImage.specialty == specialty.lower()
        ).all()

        for img in images:
            score = self._calculate_relevance_score(
                mcq_topic=topic,
                mcq_subtopic=subtopic,
                img_topic=img.topic,
                img_clinical_finding=img.clinical_finding,
                img_modality=img.modality
            )

            if score >= self.min_score:
                matches.append((img, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)

        return matches

    def _calculate_relevance_score(
        self,
        mcq_topic: str,
        mcq_subtopic: Optional[str],
        img_topic: str,
        img_clinical_finding: Optional[str],
        img_modality: Optional[str]
    ) -> float:
        """
        Calculate relevance score between MCQ and image.

        Scoring:
        - Exact topic match: 1.0
        - High fuzzy match (>90): 0.9
        - Medium fuzzy match (70-90): 0.7
        - Keyword match in subtopic: +0.2
        - Modality match: +0.1

        Returns:
            Score from 0.0 to 1.0
        """
        # Check topic mappings first
        if mcq_topic in self.topic_mappings:
            mapped_topics = self.topic_mappings[mcq_topic]
            if img_topic in mapped_topics:
                return 1.0  # Exact mapped match

        # Fuzzy matching on topic
        topic_ratio = fuzz.ratio(mcq_topic.lower(), img_topic.lower()) / 100.0

        # Fuzzy matching on clinical finding (if available)
        finding_ratio = 0.0
        if img_clinical_finding:
            finding_ratio = fuzz.ratio(mcq_topic.lower(), img_clinical_finding.lower()) / 100.0

        # Take best match
        base_score = max(topic_ratio, finding_ratio)

        # Boost for keyword match in subtopic
        keyword_boost = 0.0
        if mcq_subtopic:
            for keyword, rule in self.keyword_rules.items():
                if keyword.lower() in mcq_subtopic.lower():
                    # Check if modality matches
                    if 'requires_modality' in rule:
                        required_modality = rule['requires_modality']
                        if isinstance(required_modality, list):
                            if img_modality and img_modality.value in required_modality:
                                keyword_boost += rule.get('boost_score', 0.2)
                        elif img_modality and img_modality.value == required_modality:
                            keyword_boost += rule.get('boost_score', 0.2)

        # Combine scores (cap at 1.0)
        final_score = min(base_score + keyword_boost, 1.0)

        return final_score


def link_mcqs_to_images(
    db: Session,
    linker: ImageLinker,
    dry_run: bool = False,
    max_images_per_mcq: int = 1
) -> Dict:
    """Link MCQs to images"""

    stats = {
        'total_mcqs': 0,
        'mcqs_with_images': 0,
        'mcqs_without_images': 0,
        'total_links': 0,
        'high_confidence': 0,  # score >= 0.8
        'medium_confidence': 0,  # 0.5 <= score < 0.8
        'links_by_specialty': {}
    }

    # Get all MCQs
    mcqs = db.query(MCQ).all()
    stats['total_mcqs'] = len(mcqs)

    print(f"\n{'='*70}")
    print(f"Linking MCQs to Images")
    print(f"{'='*70}")
    print(f"Total MCQs: {len(mcqs)}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    for mcq in mcqs:
        # Find matching images
        matches = linker.find_matching_images(
            specialty=mcq.specialty.value,
            topic=mcq.topic or "",
            subtopic=mcq.subtopic,
            db=db
        )

        if matches:
            stats['mcqs_with_images'] += 1

            # Take top N images
            for img, score in matches[:max_images_per_mcq]:
                # Track statistics
                if score >= 0.8:
                    stats['high_confidence'] += 1
                else:
                    stats['medium_confidence'] += 1

                specialty = mcq.specialty.value
                stats['links_by_specialty'][specialty] = stats['links_by_specialty'].get(specialty, 0) + 1

                # Create link
                if not dry_run:
                    link = MCQImageLink(
                        mcq_id=mcq.id,
                        image_id=img.id,
                        relevance_score=score,
                        link_type='primary' if score >= 0.8 else 'supplementary',
                        match_method='automated',
                        verified=score >= 0.9,  # Auto-verify very high confidence
                        created_by='system'
                    )

                    db.add(link)

                    # Update MCQ image_url (for backward compatibility)
                    if score >= 0.8 and not mcq.image_url:
                        mcq.image_url = img.cdn_url
                        mcq.image_caption = f"{img.topic} - {img.clinical_finding or img.topic}"

                stats['total_links'] += 1

                print(f"✓ MCQ {mcq.question_id} → Image {img.image_id} (score: {score:.2f})")

        else:
            stats['mcqs_without_images'] += 1
            print(f"⚠ No images found for MCQ {mcq.question_id} ({mcq.specialty.value}, {mcq.topic})")

    if not dry_run:
        db.commit()

    return stats


def link_osces_to_images(
    db: Session,
    linker: ImageLinker,
    dry_run: bool = False,
    max_images_per_osce: int = 3
) -> Dict:
    """Link OSCEs to images"""

    stats = {
        'total_osces': 0,
        'osces_with_images': 0,
        'osces_without_images': 0,
        'total_links': 0,
        'high_confidence': 0,
        'medium_confidence': 0,
        'links_by_specialty': {}
    }

    # Get all OSCEs
    osces = db.query(OSCE).all()
    stats['total_osces'] = len(osces)

    print(f"\n{'='*70}")
    print(f"Linking OSCEs to Images")
    print(f"{'='*70}")
    print(f"Total OSCEs: {len(osces)}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print()

    for osce in osces:
        # Find matching images
        matches = linker.find_matching_images(
            specialty=osce.specialty.value,
            topic=osce.topic or "",
            subtopic=None,
            db=db
        )

        if matches:
            stats['osces_with_images'] += 1

            # Take top N images
            for img, score in matches[:max_images_per_osce]:
                if score >= 0.8:
                    stats['high_confidence'] += 1
                else:
                    stats['medium_confidence'] += 1

                specialty = osce.specialty.value
                stats['links_by_specialty'][specialty] = stats['links_by_specialty'].get(specialty, 0) + 1

                # Create link
                if not dry_run:
                    link = OSCEImageLink(
                        osce_id=osce.id,
                        image_id=img.id,
                        relevance_score=score,
                        link_type='primary' if score >= 0.8 else 'supplementary',
                        match_method='automated',
                        verified=score >= 0.9,
                        created_by='system'
                    )

                    db.add(link)

                    # Update OSCE supporting_documents
                    if not osce.supporting_documents:
                        osce.supporting_documents = {'images': []}

                    if 'images' not in osce.supporting_documents:
                        osce.supporting_documents['images'] = []

                    osce.supporting_documents['images'].append({
                        'url': img.cdn_url,
                        'caption': f"{img.topic} - {img.clinical_finding or img.topic}",
                        'citation': img.citation_short
                    })

                stats['total_links'] += 1

                print(f"✓ OSCE {osce.osce_id} → Image {img.image_id} (score: {score:.2f})")

        else:
            stats['osces_without_images'] += 1
            print(f"⚠ No images found for OSCE {osce.osce_id} ({osce.specialty.value}, {osce.topic})")

    if not dry_run:
        db.commit()

    return stats


def generate_linking_report(
    mcq_stats: Dict,
    osce_stats: Dict,
    output_file: Path
):
    """Generate human-readable linking report"""

    report = []
    report.append("# Medical Image Linking Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("\n---\n")

    # MCQ Statistics
    report.append("## MCQ Image Linking\n")
    report.append(f"- Total MCQs: {mcq_stats['total_mcqs']}")
    report.append(f"- MCQs with images: {mcq_stats['mcqs_with_images']} ({mcq_stats['mcqs_with_images'] / mcq_stats['total_mcqs'] * 100:.1f}%)")
    report.append(f"- MCQs without images: {mcq_stats['mcqs_without_images']}")
    report.append(f"- Total links created: {mcq_stats['total_links']}")
    report.append(f"  - High confidence (≥0.8): {mcq_stats['high_confidence']}")
    report.append(f"  - Medium confidence (0.5-0.8): {mcq_stats['medium_confidence']}")

    report.append("\n### Links by Specialty\n")
    for specialty, count in sorted(mcq_stats['links_by_specialty'].items()):
        report.append(f"- {specialty}: {count}")

    # OSCE Statistics
    report.append("\n---\n")
    report.append("## OSCE Image Linking\n")
    report.append(f"- Total OSCEs: {osce_stats['total_osces']}")
    report.append(f"- OSCEs with images: {osce_stats['osces_with_images']} ({osce_stats['osces_with_images'] / osce_stats['total_osces'] * 100:.1f}%)")
    report.append(f"- OSCEs without images: {osce_stats['osces_without_images']}")
    report.append(f"- Total links created: {osce_stats['total_links']}")
    report.append(f"  - High confidence (≥0.8): {osce_stats['high_confidence']}")
    report.append(f"  - Medium confidence (0.5-0.8): {osce_stats['medium_confidence']}")

    report.append("\n### Links by Specialty\n")
    for specialty, count in sorted(osce_stats['links_by_specialty'].items()):
        report.append(f"- {specialty}: {count}")

    # Overall Summary
    total_content = mcq_stats['total_mcqs'] + osce_stats['total_osces']
    total_linked = mcq_stats['mcqs_with_images'] + osce_stats['osces_with_images']
    coverage_percent = (total_linked / total_content) * 100

    report.append("\n---\n")
    report.append("## Overall Summary\n")
    report.append(f"- Total content items: {total_content}")
    report.append(f"- Items with images: {total_linked}")
    report.append(f"- **Coverage: {coverage_percent:.1f}%**")

    if coverage_percent >= 70:
        report.append("\n✓ **SUCCESS:** Target coverage (≥70%) achieved!")
    else:
        report.append(f"\n⚠ **WARNING:** Coverage below 70% target (current: {coverage_percent:.1f}%)")

    # Recommendations
    report.append("\n---\n")
    report.append("## Recommendations\n")

    if mcq_stats['medium_confidence'] > 0:
        report.append(f"- Review {mcq_stats['medium_confidence']} medium-confidence MCQ links")

    if osce_stats['medium_confidence'] > 0:
        report.append(f"- Review {osce_stats['medium_confidence']} medium-confidence OSCE links")

    if mcq_stats['mcqs_without_images'] > 0:
        report.append(f"- Find images for {mcq_stats['mcqs_without_images']} MCQs (download from MedPix, NIH)")

    if osce_stats['osces_without_images'] > 0:
        report.append(f"- Find images for {osce_stats['osces_without_images']} OSCEs")

    # Write report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write('\n'.join(report))

    print(f"\nLinking report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Link medical images to MCQs and OSCEs',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--db-url',
        default=None,
        help='Database URL (or use DATABASE_URL env)'
    )

    parser.add_argument(
        '--mapping',
        type=Path,
        default=Path('data/config/topic_mapping.json'),
        help='Topic mapping JSON file'
    )

    parser.add_argument(
        '--min-score',
        type=float,
        default=0.5,
        help='Minimum relevance score (0.0-1.0)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Run without creating links'
    )

    parser.add_argument(
        '--report-output',
        type=Path,
        default=Path('data/reports/image_linking_report.md'),
        help='Linking report output path'
    )

    args = parser.parse_args()

    db_url = args.db_url or os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not set")
        return 1

    # Create linker
    linker = ImageLinker(
        mapping_file=args.mapping,
        min_score=args.min_score
    )

    # Create database connection
    engine = create_engine(db_url)

    with Session(engine) as db:
        # Link MCQs
        mcq_stats = link_mcqs_to_images(db, linker, dry_run=args.dry_run)

        # Link OSCEs
        osce_stats = link_osces_to_images(db, linker, dry_run=args.dry_run)

        # Generate report
        generate_linking_report(mcq_stats, osce_stats, args.report_output)

    print("\n✓ Image linking complete!")
    return 0


if __name__ == "__main__":
    import os
    exit(main())
```

---

## Testing

### Dry Run Test

```bash
# Test without creating links
python3 scripts/link_images_to_content.py \
    --db-url postgresql://user:pass@localhost/irstudy \
    --mapping data/config/topic_mapping.json \
    --min-score 0.5 \
    --dry-run

# Review output to verify matching logic
```

### Live Run

```bash
# Create actual links
python3 scripts/link_images_to_content.py \
    --db-url postgresql://user:pass@localhost/irstudy \
    --mapping data/config/topic_mapping.json \
    --min-score 0.5 \
    --report-output data/reports/image_linking_report.md

# Review report
cat data/reports/image_linking_report.md
```

### Verification Queries

```sql
-- Check MCQs with images
SELECT COUNT(*) FROM mcqs WHERE image_url IS NOT NULL;

-- Check MCQ-image links
SELECT
    m.specialty,
    COUNT(*) as mcqs_with_images,
    AVG(l.relevance_score) as avg_score
FROM mcq_image_links l
JOIN mcqs m ON l.mcq_id = m.id
GROUP BY m.specialty;

-- Check OSCE-image links
SELECT
    o.specialty,
    COUNT(*) as osces_with_images,
    AVG(l.relevance_score) as avg_score
FROM osce_image_links l
JOIN osces o ON l.osce_id = o.id
GROUP BY o.specialty;

-- Find medium-confidence links for review
SELECT
    m.question_id,
    m.topic,
    i.topic as image_topic,
    l.relevance_score
FROM mcq_image_links l
JOIN mcqs m ON l.mcq_id = m.id
JOIN medical_images i ON l.image_id = i.id
WHERE l.relevance_score < 0.8 AND l.verified = FALSE
ORDER BY l.relevance_score DESC
LIMIT 20;
```

---

## Success Criteria

- ✅ 70%+ MCQs linked to images
- ✅ 50%+ OSCEs linked to images
- ✅ 80%+ links are high confidence (score ≥0.8)
- ✅ Cardiology MCQs have 90%+ image coverage (HEAL has ECGs)
- ✅ Hematology MCQs have 80%+ image coverage (HEAL has microscopy)
- ✅ Dermatology MCQs have 70%+ image coverage (HEAL has skin photos)
- ✅ Linking report generated
- ✅ No duplicate links (enforced by unique constraint)
- ✅ Medical expert review completed for medium-confidence links

---

## Manual Verification Workflow

For medium-confidence links (score 0.5-0.8):

1. **Export for review:**
   ```sql
   COPY (
       SELECT
           m.question_id,
           m.topic as mcq_topic,
           i.image_id,
           i.topic as image_topic,
           i.cdn_url,
           l.relevance_score
       FROM mcq_image_links l
       JOIN mcqs m ON l.mcq_id = m.id
       JOIN medical_images i ON l.image_id = i.id
       WHERE l.relevance_score < 0.8 AND l.verified = FALSE
   ) TO '/tmp/links_for_review.csv' WITH CSV HEADER;
   ```

2. **Medical expert reviews** CSV file

3. **Update verified status:**
   ```sql
   UPDATE mcq_image_links
   SET verified = TRUE
   WHERE id IN (1, 2, 3, ...);  -- Approved link IDs
   ```

---

## Rollback Plan

If linking creates incorrect associations:

```sql
-- Delete all automated links
DELETE FROM mcq_image_links WHERE match_method = 'automated';
DELETE FROM osce_image_links WHERE match_method = 'automated';

-- Clear MCQ image_url fields
UPDATE mcqs SET image_url = NULL, image_caption = NULL;

-- Clear OSCE supporting_documents
UPDATE osces SET supporting_documents = '{}';

-- Re-run linking script with adjusted parameters
```

---

## Next Steps After Completion

1. **Medical expert review** of medium-confidence links
2. **Frontend update** to display linked images
3. **Download additional sources** (MedPix, NIH) for missing specialties
4. **Implement manual linking UI** for edge cases
5. **Monitor user feedback** on image relevance

---

**🎉 This completes the Medical Image Integration project!**

All 9 tasks documented and ready for implementation.
