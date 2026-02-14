#!/usr/bin/env python3
"""
Rebuild Complete OpenI Metadata Catalog
Scans all downloaded OpenI images and creates unified catalog
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class OpenICatalogRebuilder:
    """Rebuild OpenI catalog by scanning actual downloaded images"""

    def __init__(self, openi_dir: str = "data/medical_images/openi"):
        self.openi_dir = Path(openi_dir)
        self.catalog = {
            'generated_at': datetime.now().isoformat(),
            'total_images': 0,
            'by_specialty': {},
            'by_topic': {},
            'by_source': {'OpenI': 0},
            'images': []
        }

    def extract_metadata_from_path(self, image_path: Path) -> Dict:
        """Extract metadata from image file path structure

        Path format: data/medical_images/openi/{specialty}/{topic}/openi_{pmcid}.{ext}
        """
        parts = image_path.parts

        # Find openi directory index
        openi_idx = parts.index('openi')

        specialty = parts[openi_idx + 1] if len(parts) > openi_idx + 1 else 'unknown'
        topic = parts[openi_idx + 2] if len(parts) > openi_idx + 2 else 'unknown'

        # Extract PMCID from filename
        filename = image_path.name
        pmcid_match = re.search(r'openi_(PMC\d+|[A-Za-z0-9_]+)', filename)
        pmcid = pmcid_match.group(1) if pmcid_match else filename.stem

        return {
            'id': pmcid,
            'pmcid': pmcid if pmcid.startswith('PMC') else '',
            'filename': str(image_path),
            'specialty': specialty,
            'topic': topic,
            'source': 'OpenI',
            'url': f'https://openi.nlm.nih.gov/detailedresult?query={pmcid}',
            'title': topic.replace('_', ' ').title(),
            'journal': '',
            'year': '',
            'search_term': topic.replace('_', ' '),
            'reconstructed_at': datetime.now().isoformat()
        }

    def extract_clinical_keywords(self, text: str) -> List[str]:
        """Extract clinical keywords from text"""
        if not text:
            return []

        # Medical keyword patterns
        patterns = [
            r'\b(pneumothorax|haemothorax|pneumonia|tuberculosis|TB|empyema)\b',
            r'\b(STEMI|NSTEMI|myocardial infarction|MI|angina|pericarditis)\b',
            r'\b(stroke|haemorrhage|hemorrhage|infarction|ischaemia|ischemia)\b',
            r'\b(fracture|dislocation|trauma|injury|rupture)\b',
            r'\b(meningitis|encephalitis|abscess|infection)\b',
            r'\b(cancer|carcinoma|tumour|tumor|neoplasm|malignancy)\b',
            r'\b(cirrhosis|hepatitis|pancreatitis|cholecystitis)\b',
            r'\b(diabetes|hypoglycaemia|DKA|ketoacidosis)\b',
            r'\b(aneurysm|dissection|thrombosis|embolism|PE)\b',
            r'\b(CT|MRI|X-ray|ultrasound|ECG|EEG|echo)\b',
        ]

        keywords = set()
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.update([m.lower() for m in matches])

        return list(keywords)

    def scan_openi_directory(self) -> List[Dict]:
        """Scan OpenI directory and extract all image metadata"""

        print(f"Scanning OpenI directory: {self.openi_dir}")

        # Find all image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
        all_images = []

        for ext in image_extensions:
            all_images.extend(self.openi_dir.rglob(f'*{ext}'))

        print(f"Found {len(all_images)} image files")

        images_data = []

        for img_path in sorted(all_images):
            # Skip if in root openi directory (not in specialty/topic structure)
            if img_path.parent == self.openi_dir:
                continue

            # Extract metadata from path
            metadata = self.extract_metadata_from_path(img_path)

            # Add clinical keywords
            combined_text = f"{metadata['topic']} {metadata['title']}"
            metadata['keywords'] = self.extract_clinical_keywords(combined_text)

            # Add taxonomy node
            metadata['taxonomy_node'] = f"{metadata['specialty']}/{metadata['topic']}"

            images_data.append(metadata)

            # Update counts
            spec = metadata['specialty']
            self.catalog['by_specialty'][spec] = self.catalog['by_specialty'].get(spec, 0) + 1

            topic = metadata['topic']
            self.catalog['by_topic'][topic] = self.catalog['by_topic'].get(topic, 0) + 1

        print(f"  ✓ Extracted metadata for {len(images_data)} images")

        return images_data

    def rebuild_catalog(self) -> Dict:
        """Rebuild complete catalog from scanned images"""

        print("\n" + "="*70)
        print("Rebuilding OpenI Metadata Catalog")
        print("="*70 + "\n")

        # Scan all images
        images_data = self.scan_openi_directory()

        self.catalog['images'] = images_data
        self.catalog['total_images'] = len(images_data)
        self.catalog['by_source']['OpenI'] = len(images_data)

        # Print statistics
        print("\n" + "="*70)
        print("Catalog Statistics")
        print("="*70)
        print(f"Total images: {self.catalog['total_images']}")
        print(f"\nSpecialties: {len(self.catalog['by_specialty'])}")
        for spec, count in sorted(self.catalog['by_specialty'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {spec}: {count} images")

        print(f"\nTop topics: {len(self.catalog['by_topic'])}")
        top_topics = sorted(self.catalog['by_topic'].items(), key=lambda x: x[1], reverse=True)[:10]
        for topic, count in top_topics:
            print(f"  {topic}: {count} images")

        return self.catalog

    def save_catalog(self, output_file: str = None):
        """Save rebuilt catalog to JSON file"""

        if output_file is None:
            output_file = self.openi_dir / 'openi_metadata_complete.json'
        else:
            output_file = Path(output_file)

        print(f"\nSaving rebuilt catalog to {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Catalog saved ({output_file.stat().st_size / 1024:.1f} KB)")

        # Also save summary
        summary_file = output_file.parent / 'catalog_summary_complete.json'
        summary = {
            'generated_at': self.catalog['generated_at'],
            'total_images': self.catalog['total_images'],
            'by_source': self.catalog['by_source'],
            'by_specialty': self.catalog['by_specialty'],
            'top_topics': dict(sorted(self.catalog['by_topic'].items(),
                                     key=lambda x: x[1], reverse=True)[:20])
        }

        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)

        print(f"  ✓ Summary saved to {summary_file}")


def main():
    """Main execution"""

    import argparse

    parser = argparse.ArgumentParser(
        description='Rebuild OpenI metadata catalog by scanning actual downloaded images'
    )
    parser.add_argument(
        '--input-dir',
        default='data/medical_images/openi',
        help='OpenI images directory (default: data/medical_images/openi)'
    )
    parser.add_argument(
        '--output',
        default='data/medical_images/openi/openi_metadata_complete.json',
        help='Output catalog file (default: data/medical_images/openi/openi_metadata_complete.json)'
    )

    args = parser.parse_args()

    # Rebuild catalog
    rebuilder = OpenICatalogRebuilder(openi_dir=args.input_dir)
    catalog = rebuilder.rebuild_catalog()
    rebuilder.save_catalog(args.output)

    print("\n" + "="*70)
    print("Catalog Rebuild Complete")
    print("="*70)
    print(f"\nNext steps:")
    print(f"1. Review catalog: jq '.total_images, .by_specialty' {args.output}")
    print(f"2. Run unified catalog builder: python3 scripts/create_image_catalog.py")
    print(f"3. Start image linking: python3 scripts/link_images_to_mcqs.py")


if __name__ == '__main__':
    main()
