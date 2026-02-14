#!/usr/bin/env python3
"""
Rebuild Complete HEAL Metadata Catalog
Consolidates all HEAL topic metadata files into unified catalog
"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

class HEALCatalogRebuilder:
    """Rebuild HEAL catalog by consolidating all topic metadata files"""

    def __init__(self, heal_dir: str = "data/medical_images/heal"):
        self.heal_dir = Path(heal_dir)
        self.catalog = {
            'generated_at': datetime.now().isoformat(),
            'total_images': 0,
            'by_specialty': {},
            'by_topic': {},
            'by_source': {'HEAL': 0},
            'images': []
        }

    def consolidate_metadata_files(self) -> List[Dict]:
        """Consolidate all HEAL topic metadata JSON files"""

        print(f"Scanning HEAL directory: {self.heal_dir}")

        # Find all metadata JSON files (excluding summary files)
        metadata_files = [
            f for f in self.heal_dir.rglob('*_metadata.json')
            if 'summary' not in f.name and 'comprehensive' not in f.name
        ]

        print(f"Found {len(metadata_files)} metadata files")

        all_images = []

        for meta_file in sorted(metadata_files):
            try:
                # Load metadata
                with open(meta_file) as f:
                    metadata = json.load(f)

                # Extract specialty from path
                # Path: data/medical_images/heal/{specialty}/{topic}/{topic}_metadata.json
                specialty = meta_file.parent.parent.name
                topic = meta_file.parent.name

                # HEAL metadata files are directly a list of image objects
                images_list = metadata if isinstance(metadata, list) else metadata.get('images', [])

                # Process each image in this topic
                for img in images_list:
                    image_data = {
                        'id': f"heal_{img.get('file_id', '')}",
                        'file_id': img.get('file_id', ''),
                        'filename': img.get('filepath', ''),
                        'specialty': specialty,
                        'topic': topic,
                        'source': 'HEAL',
                        'url': img.get('details_url', ''),
                        'image_url': img.get('image_url', ''),
                        'title': img.get('title', ''),
                        'description': img.get('description', ''),
                        'collection': img.get('collection', ''),
                        'creator': img.get('creator', ''),
                        'date': img.get('date', ''),
                        'rights': img.get('rights', ''),
                        'file_size_kb': img.get('file_size_kb', 0),
                        'downloaded_at': img.get('downloaded_at', ''),
                        'taxonomy_node': f"{specialty}/{topic}"
                    }

                    all_images.append(image_data)

                    # Update counts
                    self.catalog['by_specialty'][specialty] = self.catalog['by_specialty'].get(specialty, 0) + 1
                    self.catalog['by_topic'][topic] = self.catalog['by_topic'].get(topic, 0) + 1

            except Exception as e:
                print(f"  ✗ Error processing {meta_file}: {e}")

        print(f"  ✓ Consolidated {len(all_images)} images from {len(metadata_files)} files")

        return all_images

    def rebuild_catalog(self) -> Dict:
        """Rebuild complete catalog from all metadata files"""

        print("\n" + "="*70)
        print("Rebuilding HEAL Metadata Catalog")
        print("="*70 + "\n")

        # Consolidate all metadata files
        images_data = self.consolidate_metadata_files()

        self.catalog['images'] = images_data
        self.catalog['total_images'] = len(images_data)
        self.catalog['by_source']['HEAL'] = len(images_data)

        # Print statistics
        print("\n" + "="*70)
        print("Catalog Statistics")
        print("="*70)
        print(f"Total images: {self.catalog['total_images']}")
        print(f"\nSpecialties: {len(self.catalog['by_specialty'])}")
        for spec, count in sorted(self.catalog['by_specialty'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {spec}: {count} images")

        print(f"\nTop topics: {len(self.catalog['by_topic'])}")
        top_topics = sorted(self.catalog['by_topic'].items(), key=lambda x: x[1], reverse=True)[:15]
        for topic, count in top_topics:
            print(f"  {topic}: {count} images")

        return self.catalog

    def save_catalog(self, output_file: str = None):
        """Save rebuilt catalog to JSON file"""

        if output_file is None:
            output_file = self.heal_dir / 'heal_metadata_complete.json'
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
        description='Rebuild HEAL metadata catalog by consolidating all topic metadata files'
    )
    parser.add_argument(
        '--input-dir',
        default='data/medical_images/heal',
        help='HEAL images directory (default: data/medical_images/heal)'
    )
    parser.add_argument(
        '--output',
        default='data/medical_images/heal/heal_metadata_complete.json',
        help='Output catalog file (default: data/medical_images/heal/heal_metadata_complete.json)'
    )

    args = parser.parse_args()

    # Rebuild catalog
    rebuilder = HEALCatalogRebuilder(heal_dir=args.input_dir)
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
