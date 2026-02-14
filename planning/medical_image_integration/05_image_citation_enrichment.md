# Task 05: Image Citation Enrichment

**Duration:** 2 hours
**Priority:** P1
**Dependencies:** Task 04 (Image Metadata Processing)
**Output:** Metadata with proper citations and source attribution

---

## Objective

Add proper academic citations and source attribution to all medical images, ensuring compliance with Australian academic standards and licensing requirements for AMC exam preparation.

---

## Scope

### In Scope
- Generate proper citations for HEAL images
- Add copyright/license information
- Include source URLs
- Format citations according to Australian academic standards (Vancouver style)
- Validate license compatibility (CC-BY-NC, Public Domain)
- Document attribution requirements for each source
- Generate citation report for medical expert review

### Out of Scope
- Copyright legal review (requires legal expert)
- Obtaining new licenses
- Modifying images (watermarking)
- Citation generation for unpublished sources

---

## Prerequisites

### Completed Tasks
- ✅ Task 04: Unified metadata JSON generated

### Required Files
- `data/processed_metadata/heal_metadata.json`
- HEAL comprehensive metadata (if available)

### Citation Standards
- Vancouver style (medical/scientific standard)
- AMC recommended citation format
- Australian academic guidelines

---

## Implementation Steps

### Step 1: Script Structure (15 min)

**File:** `scripts/enrich_image_citations.py`

```python
#!/usr/bin/env python3
"""
Enrich medical image metadata with proper citations and source attribution.

Usage:
    python3 scripts/enrich_image_citations.py \\
        --input data/processed_metadata/heal_metadata.json \\
        --output data/processed_metadata/heal_metadata_cited.json \\
        --citation-style vancouver
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass

@dataclass
class Citation:
    """Citation information for medical images"""
    source_name: str
    source_url: str
    accessed_date: str
    license: str
    attribution: str
    citation_text: str  # Formatted citation
    doi: Optional[str] = None
    publisher: Optional[str] = None


class CitationGenerator:
    """Generate citations for medical images"""

    def __init__(self, style: str = 'vancouver'):
        self.style = style
        self.accessed_date = datetime.now().strftime("%Y-%m-%d")

    def generate_citation(
        self,
        source: str,
        topic: str,
        specialty: str,
        image_id: str,
        metadata: Dict
    ) -> Citation:
        """Generate citation based on source type"""

        if source == 'heal':
            return self.generate_heal_citation(topic, specialty, image_id, metadata)
        elif source == 'medpix':
            return self.generate_medpix_citation(topic, specialty, image_id, metadata)
        elif source == 'nih':
            return self.generate_nih_citation(topic, specialty, image_id, metadata)
        else:
            return self.generate_generic_citation(source, topic, specialty, image_id)

    def generate_heal_citation(
        self,
        topic: str,
        specialty: str,
        image_id: str,
        metadata: Dict
    ) -> Citation:
        """Generate citation for HEAL images"""

        # HEAL citation format (Vancouver style):
        # Health Education Assets Library (HEAL). [Topic]. [Specialty].
        # Available from: https://library.med.utah.edu/heal/
        # [Accessed: YYYY-MM-DD]. License: CC-BY-NC 4.0

        source_url = "https://library.med.utah.edu/heal/"

        # Vancouver-style citation
        citation_text = (
            f"Health Education Assets Library (HEAL). {topic}. "
            f"{specialty.title()}. "
            f"Available from: {source_url} "
            f"[Accessed: {self.accessed_date}]."
        )

        attribution = (
            f"Image courtesy of Health Education Assets Library (HEAL), "
            f"University of Utah. Licensed under CC-BY-NC 4.0."
        )

        return Citation(
            source_name="Health Education Assets Library (HEAL)",
            source_url=source_url,
            accessed_date=self.accessed_date,
            license="CC-BY-NC-4.0",
            attribution=attribution,
            citation_text=citation_text,
            publisher="University of Utah School of Medicine"
        )

    def generate_medpix_citation(
        self,
        topic: str,
        specialty: str,
        image_id: str,
        metadata: Dict
    ) -> Citation:
        """Generate citation for MedPix images (future)"""

        # MedPix citation format:
        # MedPix Medical Image Database. [Topic]. Case ID: [ID].
        # Bethesda (MD): National Library of Medicine;
        # Available from: https://medpix.nlm.nih.gov/
        # [Accessed: YYYY-MM-DD]. License: Public Domain

        source_url = f"https://medpix.nlm.nih.gov/case/{image_id}"

        citation_text = (
            f"MedPix Medical Image Database. {topic}. "
            f"Case ID: {image_id}. "
            f"Bethesda (MD): National Library of Medicine; "
            f"Available from: {source_url} "
            f"[Accessed: {self.accessed_date}]."
        )

        attribution = (
            f"Image from MedPix® Medical Image Database "
            f"(National Library of Medicine). Public Domain."
        )

        return Citation(
            source_name="MedPix Medical Image Database",
            source_url=source_url,
            accessed_date=self.accessed_date,
            license="Public Domain",
            attribution=attribution,
            citation_text=citation_text,
            publisher="National Library of Medicine"
        )

    def generate_nih_citation(
        self,
        topic: str,
        specialty: str,
        image_id: str,
        metadata: Dict
    ) -> Citation:
        """Generate citation for NIH images (future)"""

        source_url = "https://nihcc.app.box.com/v/ChestXray-NIHCC"

        citation_text = (
            f"National Institutes of Health Clinical Center. {topic}. "
            f"NIH Chest X-ray Dataset. "
            f"Available from: {source_url} "
            f"[Accessed: {self.accessed_date}]."
        )

        attribution = (
            f"Image from NIH Clinical Center Chest X-ray Dataset. "
            f"Public Domain (US Government Work)."
        )

        return Citation(
            source_name="NIH Clinical Center",
            source_url=source_url,
            accessed_date=self.accessed_date,
            license="Public Domain (US Government Work)",
            attribution=attribution,
            citation_text=citation_text,
            publisher="National Institutes of Health"
        )

    def generate_generic_citation(
        self,
        source: str,
        topic: str,
        specialty: str,
        image_id: str
    ) -> Citation:
        """Generate generic citation for unknown sources"""

        citation_text = (
            f"{source.upper()}. {topic}. "
            f"Image ID: {image_id}. "
            f"[Accessed: {self.accessed_date}]."
        )

        return Citation(
            source_name=source.upper(),
            source_url="",
            accessed_date=self.accessed_date,
            license="Unknown",
            attribution=f"Image from {source.upper()}",
            citation_text=citation_text
        )
```

---

### Step 2: Metadata Enrichment (30 min)

```python
def enrich_metadata_with_citations(
    input_file: Path,
    output_file: Path,
    citation_style: str = 'vancouver'
) -> Dict:
    """Add citations to all images in metadata file"""

    # Load existing metadata
    with open(input_file, 'r') as f:
        data = json.load(f)

    images = data['images']
    generator = CitationGenerator(style=citation_style)

    print(f"\n{'='*70}")
    print(f"Image Citation Enrichment")
    print(f"{'='*70}")
    print(f"Input: {input_file}")
    print(f"Total images: {len(images)}")
    print(f"Citation style: {citation_style}")
    print()

    # Track statistics
    stats = {
        'total_images': len(images),
        'cited_images': 0,
        'by_license': {},
        'by_source': {},
        'missing_citations': 0
    }

    # Enrich each image
    for idx, img in enumerate(images, 1):
        if idx % 100 == 0:
            print(f"Processing: {idx}/{len(images)}")

        # Generate citation
        citation = generator.generate_citation(
            source=img['source'],
            topic=img['topic'],
            specialty=img['specialty'],
            image_id=img['image_id'],
            metadata=img
        )

        # Add citation fields
        img['citation'] = citation.citation_text
        img['citation_short'] = f"{citation.source_name}, {img['topic']}"
        img['source_url'] = citation.source_url
        img['license'] = citation.license
        img['attribution'] = citation.attribution
        img['accessed_date'] = citation.accessed_date

        if citation.publisher:
            img['publisher'] = citation.publisher

        # Update statistics
        stats['cited_images'] += 1
        stats['by_license'][citation.license] = stats['by_license'].get(citation.license, 0) + 1
        stats['by_source'][img['source']] = stats['by_source'].get(img['source'], 0) + 1

    # Update metadata
    data['images'] = images
    data['citation_metadata'] = {
        'style': citation_style,
        'generated_at': datetime.now().isoformat(),
        'statistics': stats
    }

    # Write output
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Citation Enrichment Complete!")
    print(f"{'='*70}")
    print(f"Output: {output_file}")
    print(f"Cited images: {stats['cited_images']}/{stats['total_images']}")
    print(f"\nBy License:")
    for license_type, count in sorted(stats['by_license'].items()):
        print(f"  {license_type}: {count}")
    print(f"\nBy Source:")
    for source, count in sorted(stats['by_source'].items()):
        print(f"  {source}: {count}")

    return stats
```

---

### Step 3: License Validation (20 min)

```python
class LicenseValidator:
    """Validate image licenses for educational use"""

    ALLOWED_LICENSES = [
        'CC-BY-NC-4.0',
        'CC-BY-NC-SA-4.0',
        'CC-BY-4.0',
        'Public Domain',
        'US Government Work',
    ]

    EDUCATIONAL_USE_OK = [
        'CC-BY-NC-4.0',  # Non-commercial OK (exam prep is educational)
        'CC-BY-NC-SA-4.0',
        'CC-BY-4.0',
        'Public Domain',
        'US Government Work',
    ]

    def validate_license(self, license: str) -> Dict:
        """
        Validate if license allows educational use.

        Returns:
            {
                'allowed': bool,
                'educational_use': bool,
                'attribution_required': bool,
                'warnings': List[str]
            }
        """
        warnings = []

        # Check if license is allowed
        allowed = license in self.ALLOWED_LICENSES
        if not allowed:
            warnings.append(f"License '{license}' not in allowed list")

        # Check educational use
        educational_use = license in self.EDUCATIONAL_USE_OK

        # Attribution requirements
        attribution_required = 'CC' in license or license == 'US Government Work'

        # Specific warnings
        if 'NC' in license:
            warnings.append("Non-commercial license - verify exam prep qualifies")

        if 'SA' in license:
            warnings.append("Share-Alike requirement - derivatives must use same license")

        return {
            'allowed': allowed,
            'educational_use': educational_use,
            'attribution_required': attribution_required,
            'warnings': warnings
        }


def validate_all_licenses(metadata_file: Path) -> Dict:
    """Validate licenses for all images"""

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    validator = LicenseValidator()
    images = data['images']

    validation_report = {
        'total_images': len(images),
        'valid_licenses': 0,
        'invalid_licenses': 0,
        'warnings': [],
        'by_license': {}
    }

    for img in images:
        license = img.get('license', 'Unknown')
        result = validator.validate_license(license)

        if result['allowed']:
            validation_report['valid_licenses'] += 1
        else:
            validation_report['invalid_licenses'] += 1
            validation_report['warnings'].append({
                'image_id': img['image_id'],
                'license': license,
                'issue': result['warnings']
            })

        # Count by license
        validation_report['by_license'][license] = validation_report['by_license'].get(license, 0) + 1

    return validation_report
```

---

### Step 4: Citation Report Generation (25 min)

```python
def generate_citation_report(
    metadata_file: Path,
    output_file: Path
):
    """Generate human-readable citation report for review"""

    with open(metadata_file, 'r') as f:
        data = json.load(f)

    images = data['images']
    stats = data.get('citation_metadata', {}).get('statistics', {})

    # Generate markdown report
    report = []
    report.append("# Medical Image Citation Report")
    report.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n**Total Images:** {len(images)}")
    report.append(f"\n---\n")

    # Summary statistics
    report.append("## Summary Statistics\n")
    report.append(f"- Total images: {stats.get('total_images', 0)}")
    report.append(f"- Cited images: {stats.get('cited_images', 0)}")
    report.append(f"- Missing citations: {stats.get('missing_citations', 0)}")
    report.append("\n### By License\n")
    for license_type, count in sorted(stats.get('by_license', {}).items()):
        report.append(f"- {license_type}: {count}")

    report.append("\n### By Source\n")
    for source, count in sorted(stats.get('by_source', {}).items()):
        report.append(f"- {source}: {count}")

    # License validation
    report.append("\n---\n")
    report.append("## License Validation\n")

    validation = validate_all_licenses(metadata_file)
    report.append(f"- Valid licenses: {validation['valid_licenses']}")
    report.append(f"- Invalid licenses: {validation['invalid_licenses']}")

    if validation['warnings']:
        report.append("\n### Warnings\n")
        for warning in validation['warnings'][:10]:  # Show first 10
            report.append(f"- **{warning['image_id']}**: {warning['license']}")
            for issue in warning['issue']:
                report.append(f"  - {issue}")

    # Sample citations
    report.append("\n---\n")
    report.append("## Sample Citations\n")
    report.append("\nFirst 10 images:\n")

    for img in images[:10]:
        report.append(f"\n### {img['image_id']}")
        report.append(f"**Topic:** {img['topic']}")
        report.append(f"**Specialty:** {img['specialty']}")
        report.append(f"**Source:** {img['source']}")
        report.append(f"\n**Citation:**")
        report.append(f"> {img['citation']}")
        report.append(f"\n**Attribution:**")
        report.append(f"> {img['attribution']}")

    # Attribution requirements
    report.append("\n---\n")
    report.append("## Attribution Requirements\n")
    report.append("\n### HEAL Images (CC-BY-NC-4.0)\n")
    report.append("- **Requirement:** Attribute to University of Utah HEAL")
    report.append("- **Format:** 'Image courtesy of Health Education Assets Library (HEAL), University of Utah'")
    report.append("- **Commercial use:** Not allowed")
    report.append("- **Derivatives:** Allowed with attribution")

    report.append("\n### MedPix Images (Public Domain)\n")
    report.append("- **Requirement:** No attribution required (but recommended)")
    report.append("- **Format:** 'Image from MedPix® Medical Image Database (NLM)'")
    report.append("- **Commercial use:** Allowed")
    report.append("- **Derivatives:** Allowed")

    report.append("\n### NIH Images (Public Domain - US Govt Work)\n")
    report.append("- **Requirement:** No attribution required")
    report.append("- **Format:** 'Image from NIH Clinical Center'")
    report.append("- **Commercial use:** Allowed")
    report.append("- **Derivatives:** Allowed")

    # Write report
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"\nCitation report generated: {output_file}")
```

---

### Step 5: CLI Interface (10 min)

```python
def main():
    parser = argparse.ArgumentParser(
        description='Enrich medical image metadata with citations',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Input metadata JSON file'
    )

    parser.add_argument(
        '--output',
        type=Path,
        required=True,
        help='Output metadata JSON file with citations'
    )

    parser.add_argument(
        '--citation-style',
        choices=['vancouver', 'apa', 'chicago'],
        default='vancouver',
        help='Citation style (default: vancouver)'
    )

    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='Generate human-readable citation report'
    )

    parser.add_argument(
        '--report-output',
        type=Path,
        default=Path('data/reports/citation_report.md'),
        help='Citation report output path'
    )

    args = parser.parse_args()

    # Enrich metadata
    stats = enrich_metadata_with_citations(
        input_file=args.input,
        output_file=args.output,
        citation_style=args.citation_style
    )

    # Generate report if requested
    if args.generate_report:
        generate_citation_report(
            metadata_file=args.output,
            output_file=args.report_output
        )

    print("\n✓ Citation enrichment complete!")
    return 0


if __name__ == "__main__":
    exit(main())
```

---

## Testing

### Integration Test

```bash
# Enrich HEAL metadata with citations
python3 scripts/enrich_image_citations.py \
    --input data/processed_metadata/heal_metadata.json \
    --output data/processed_metadata/heal_metadata_cited.json \
    --citation-style vancouver \
    --generate-report \
    --report-output data/reports/heal_citation_report.md

# Verify output
cat data/processed_metadata/heal_metadata_cited.json | jq '.images[0].citation'

# Expected:
"Health Education Assets Library (HEAL). Acute Myeloid Leukemia. Hematology. Available from: https://library.med.utah.edu/heal/ [Accessed: 2026-02-03]."

# Review report
cat data/reports/heal_citation_report.md
```

---

## Success Criteria

- ✅ All images have proper citations (Vancouver style)
- ✅ Licenses validated (CC-BY-NC-4.0, Public Domain)
- ✅ Attribution requirements documented
- ✅ Source URLs included
- ✅ Citation report generated for review
- ✅ 100% of HEAL images comply with CC-BY-NC-4.0
- ✅ No copyright violations detected
- ✅ Citations meet Australian academic standards

---

## Output Format

**Enhanced metadata:**

```json
{
  "image_id": "heal_a1b2c3d4e5f6",
  "source": "heal",
  "topic": "Acute Myeloid Leukemia",
  "specialty": "hematology",
  "citation": "Health Education Assets Library (HEAL). Acute Myeloid Leukemia. Hematology. Available from: https://library.med.utah.edu/heal/ [Accessed: 2026-02-03].",
  "citation_short": "HEAL, Acute Myeloid Leukemia",
  "source_url": "https://library.med.utah.edu/heal/",
  "license": "CC-BY-NC-4.0",
  "attribution": "Image courtesy of Health Education Assets Library (HEAL), University of Utah. Licensed under CC-BY-NC 4.0.",
  "accessed_date": "2026-02-03",
  "publisher": "University of Utah School of Medicine"
}
```

---

## Next Task

After completion, proceed to **Task 07: Database Image Indexing**

File: `07_database_image_indexing.md`

**Note:** Task 06 (CDN Upload) can be done in parallel, but indexing is needed before linking (Task 09).
