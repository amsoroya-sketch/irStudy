#!/usr/bin/env python3
"""
Create Unified Image Catalog
Combines OpenI and HEAL metadata into searchable catalog for MCQ/OSCE linking
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set
from datetime import datetime

class ImageCatalogBuilder:
    """Build unified catalog from OpenI and HEAL images"""

    def __init__(self, output_dir: str = "data/medical_images"):
        self.output_dir = Path(output_dir)
        self.catalog = {
            'generated_at': datetime.now().isoformat(),
            'total_images': 0,
            'by_specialty': {},
            'by_topic': {},
            'by_source': {'OpenI': 0, 'HEAL': 0},
            'images': []
        }

    def extract_clinical_keywords(self, text: str) -> List[str]:
        """Extract clinical keywords from text using medical terminology patterns"""

        if not text:
            return []

        # Common medical keyword patterns
        patterns = [
            # Conditions
            r'\b(pneumothorax|haemothorax|pneumonia|tuberculosis|TB|empyema)\b',
            r'\b(STEMI|NSTEMI|myocardial infarction|MI|angina|pericarditis)\b',
            r'\b(stroke|haemorrhage|hemorrhage|infarction|ischaemia|ischemia)\b',
            r'\b(fracture|dislocation|trauma|injury|rupture)\b',
            r'\b(meningitis|encephalitis|abscess|infection)\b',
            r'\b(cancer|carcinoma|tumour|tumor|neoplasm|malignancy)\b',
            r'\b(cirrhosis|hepatitis|pancreatitis|cholecystitis)\b',
            r'\b(diabetes|hypoglycaemia|hypoglycemia|DKA|ketoacidosis)\b',
            r'\b(aneurysm|dissection|thrombosis|embolism|PE)\b',

            # Imaging modalities
            r'\b(CT|MRI|X-ray|ultrasound|ECG|EEG|echo|angiography)\b',

            # Anatomical locations
            r'\b(brain|skull|cerebral|intracranial|spinal)\b',
            r'\b(chest|lung|pulmonary|cardiac|thoracic)\b',
            r'\b(abdomen|abdominal|liver|spleen|kidney|pancreas)\b',
            r'\b(pelvis|pelvic|uterus|ovary|bladder)\b',

            # Clinical findings
            r'\b(acute|chronic|severe|mild|bilateral|unilateral)\b',
            r'\b(ST elevation|T wave|QRS|arrhythmia|bradycardia|tachycardia)\b',
            r'\b(consolidation|infiltrate|effusion|oedema|edema)\b',
        ]

        keywords = set()
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.update([m.lower() for m in matches])

        return list(keywords)

    def map_to_taxonomy_node(self, specialty: str, topic: str) -> str:
        """Map image to taxonomy node path"""

        # Normalize specialty name
        specialty_map = {
            'emergency_medicine': 'emergency_medicine',
            'neurology': 'neurology',
            'respiratory': 'respiratory',
            'gastroenterology': 'gastroenterology',
            'endocrinology': 'endocrinology',
            'cardiology': 'cardiology',
            'dermatology': 'dermatology',
            'haematology': 'haematology',
            'hematology': 'haematology',
            'obstetrics_gynaecology': 'obstetrics_gynaecology',
            'paediatrics': 'paediatrics',
            'pediatrics': 'paediatrics',
            'psychiatry': 'psychiatry'
        }

        normalized_specialty = specialty_map.get(specialty.lower(), specialty)
        return f"{normalized_specialty}/{topic}"

    def process_openi_metadata(self) -> List[Dict]:
        """Process OpenI metadata JSON file"""

        # Try complete metadata file first, fallback to regular
        openi_meta_file = self.output_dir / 'openi' / 'openi_metadata_complete.json'
        if not openi_meta_file.exists():
            openi_meta_file = self.output_dir / 'openi' / 'openi_metadata.json'

        if not openi_meta_file.exists():
            print(f"Warning: OpenI metadata not found at {openi_meta_file}")
            return []

        print(f"Loading OpenI metadata from {openi_meta_file}")
        openi_meta = json.load(open(openi_meta_file))

        images = []
        for img in openi_meta.get('images', []):
            # Extract keywords from title and caption
            title = img.get('title', '')
            search_term = img.get('search_term', '')
            combined_text = f"{title} {search_term}"
            keywords = self.extract_clinical_keywords(combined_text)

            image_data = {
                'id': f"openi_{img['id'].replace('/', '_').replace(':', '_')}",
                'path': img['filename'],
                'source': 'OpenI',
                'specialty': img['specialty'],
                'topic': img['topic'],
                'search_term': search_term,
                'title': title,
                'journal': img.get('journal', ''),
                'year': img.get('year', ''),
                'url': img.get('url', ''),
                'pmcid': img.get('id', ''),
                'keywords': keywords,
                'taxonomy_node': self.map_to_taxonomy_node(img['specialty'], img['topic']),
                'downloaded_at': img.get('downloaded_at', '')
            }

            images.append(image_data)

            # Update specialty count
            spec = img['specialty']
            self.catalog['by_specialty'][spec] = self.catalog['by_specialty'].get(spec, 0) + 1

            # Update topic count
            topic = img['topic']
            self.catalog['by_topic'][topic] = self.catalog['by_topic'].get(topic, 0) + 1

        self.catalog['by_source']['OpenI'] = len(images)
        print(f"  ✓ Processed {len(images)} OpenI images")

        return images

    def process_heal_metadata(self) -> List[Dict]:
        """Process HEAL metadata JSON files"""

        heal_dir = self.output_dir / 'heal'

        if not heal_dir.exists():
            print(f"Warning: HEAL directory not found at {heal_dir}")
            return []

        # Try complete metadata file first
        heal_meta_file = heal_dir / 'heal_metadata_complete.json'
        if heal_meta_file.exists():
            print(f"Loading HEAL metadata from {heal_meta_file}")
            heal_meta = json.load(open(heal_meta_file))

            images = heal_meta.get('images', [])

            # Update counts from complete metadata
            for img in images:
                specialty = img.get('specialty', '')
                self.catalog['by_specialty'][specialty] = self.catalog['by_specialty'].get(specialty, 0) + 1

            self.catalog['by_source']['HEAL'] = len(images)
            print(f"  ✓ Processed {len(images)} HEAL images")

            return images

        # Fallback to scanning individual files
        print(f"Loading HEAL metadata from individual files in {heal_dir}")

        images = []
        metadata_files = list(heal_dir.glob('*/*_metadata.json'))

        for meta_file in metadata_files:
            try:
                heal_meta = json.load(open(meta_file))

                # Extract specialty from path
                specialty = meta_file.parent.name

                for img in heal_meta.get('items', []):
                    # Extract keywords from title and description
                    title = img.get('title', '')
                    description = img.get('description', '')
                    combined_text = f"{title} {description}"
                    keywords = self.extract_clinical_keywords(combined_text)

                    image_data = {
                        'id': f"heal_{img['id']}",
                        'path': img.get('local_path', ''),
                        'source': 'HEAL',
                        'specialty': specialty,
                        'topic': img.get('title', '').replace(' ', '_').lower(),
                        'search_term': '',
                        'title': title,
                        'description': description,
                        'url': img.get('url', ''),
                        'collection': img.get('collection', ''),
                        'keywords': keywords,
                        'taxonomy_node': self.map_to_taxonomy_node(specialty, title),
                        'downloaded_at': img.get('downloaded_at', '')
                    }

                    images.append(image_data)

                    # Update counts
                    self.catalog['by_specialty'][specialty] = self.catalog['by_specialty'].get(specialty, 0) + 1

            except Exception as e:
                print(f"  ✗ Error processing {meta_file}: {e}")

        self.catalog['by_source']['HEAL'] = len(images)
        print(f"  ✓ Processed {len(images)} HEAL images")

        return images

    def build_catalog(self) -> Dict:
        """Build complete unified catalog"""

        print("\n" + "="*70)
        print("Building Unified Image Catalog")
        print("="*70 + "\n")

        # Process both sources
        openi_images = self.process_openi_metadata()
        heal_images = self.process_heal_metadata()

        # Combine all images
        all_images = openi_images + heal_images
        self.catalog['images'] = all_images
        self.catalog['total_images'] = len(all_images)

        # Generate statistics
        print("\n" + "="*70)
        print("Catalog Statistics")
        print("="*70)
        print(f"Total images: {self.catalog['total_images']}")
        print(f"  OpenI: {self.catalog['by_source']['OpenI']}")
        print(f"  HEAL: {self.catalog['by_source']['HEAL']}")
        print(f"\nSpecialties: {len(self.catalog['by_specialty'])}")
        for spec, count in sorted(self.catalog['by_specialty'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {spec}: {count} images")

        return self.catalog

    def save_catalog(self, output_file: str = None):
        """Save catalog to JSON file"""

        if output_file is None:
            output_file = self.output_dir / 'unified_image_catalog.json'
        else:
            output_file = Path(output_file)

        print(f"\nSaving catalog to {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=2, ensure_ascii=False)

        print(f"  ✓ Catalog saved ({output_file.stat().st_size / 1024:.1f} KB)")

        # Also save a summary
        summary_file = output_file.parent / 'catalog_summary.json'
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
        description='Create unified image catalog from OpenI and HEAL metadata'
    )
    parser.add_argument(
        '--input-dir',
        default='data/medical_images',
        help='Input directory containing OpenI and HEAL images (default: data/medical_images)'
    )
    parser.add_argument(
        '--output',
        default='data/medical_images/unified_image_catalog.json',
        help='Output catalog file (default: data/medical_images/unified_image_catalog.json)'
    )

    args = parser.parse_args()

    # Build catalog
    builder = ImageCatalogBuilder(output_dir=args.input_dir)
    catalog = builder.build_catalog()
    builder.save_catalog(args.output)

    print("\n" + "="*70)
    print("Catalog Generation Complete")
    print("="*70)
    print(f"\nNext steps:")
    print(f"1. Review catalog: cat {args.output} | jq '.total_images'")
    print(f"2. Run MCQ matching: python3 scripts/link_images_to_mcqs.py")
    print(f"3. Run OSCE matching: python3 scripts/link_images_to_osces.py")


if __name__ == '__main__':
    main()
