#!/usr/bin/env python3
"""
Download Medical Images from OpenI (Open Access Biomedical Image Search)
Provider: U.S. National Library of Medicine (NIH)
License: Open Access (CC BY, Public Domain)
API: https://openi.nlm.nih.gov/services
"""

import requests
from pathlib import Path
from typing import List, Dict, Optional
import time
import argparse
import json
from datetime import datetime
from tqdm import tqdm

class OpenIDownloader:
    """Download medical images from OpenI database"""

    BASE_URL = "https://openi.nlm.nih.gov"
    SEARCH_API = f"{BASE_URL}/api/search"

    def __init__(self, output_dir: str = "data/medical_images/openi",
                 rate_limit: float = 2.0, max_per_topic: int = 10):
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit
        self.max_per_topic = max_per_topic
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'AMC-Medical-Education/1.0 (Educational Use; Contact: medical-education@example.com)'
        })
        self.downloaded_count = 0
        self.failed_count = 0
        self.metadata = []

    def search(self, query: str, max_results: int = None) -> List[Dict]:
        """
        Search OpenI for images

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of image metadata dictionaries
        """
        if max_results is None:
            max_results = self.max_per_topic

        params = {
            'query': query,
            'm': max_results
            # No 'it' parameter - API defaults to JSON
        }

        try:
            print(f"Searching OpenI: {query} (max {max_results} results)")
            response = self.session.get(self.SEARCH_API, params=params, timeout=30)
            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            images = []
            for item in data.get('list', []):
                # Extract image URLs (they're at top level, not in 'image' object)
                img_large = item.get('imgLarge', '')
                img_thumb = item.get('imgThumb', '')

                # Make URLs absolute if they're relative
                if img_large and not img_large.startswith('http'):
                    img_large = f"{self.BASE_URL}{img_large}"
                if img_thumb and not img_thumb.startswith('http'):
                    img_thumb = f"{self.BASE_URL}{img_thumb}"

                image_data = {
                    'id': item.get('uid', ''),
                    'pmcid': item.get('pmcid', ''),
                    'url': img_large,
                    'thumbnail_url': img_thumb,
                    'title': item.get('title', ''),
                    'journal': item.get('journal_title', ''),
                    'year': item.get('journal_date', {}).get('year', '') if isinstance(item.get('journal_date'), dict) else '',
                    'pmid': item.get('pmid', ''),
                    'pmc_url': item.get('pmc_url', ''),
                    'caption': item.get('image', {}).get('caption', '') if 'image' in item else ''
                }

                # Only add if we have an image URL
                if image_data['url'] and image_data['id']:
                    images.append(image_data)

            # Show total available
            total_available = data.get('total', 0)
            print(f"  ✓ Found {len(images)} images (total available: {total_available:,})")
            time.sleep(self.rate_limit)
            return images

        except Exception as e:
            print(f"  ✗ Error searching OpenI: {e}")
            return []

    def download_image(self, image_data: Dict, output_path: Path) -> bool:
        """
        Download single image from OpenI

        Args:
            image_data: Image metadata dictionary with 'url' field
            output_path: Path to save image

        Returns:
            True if successful, False otherwise
        """
        try:
            url = image_data['url']

            # OpenI URLs are often relative, make absolute
            if not url.startswith('http'):
                url = f"{self.BASE_URL}{url}"

            response = self.session.get(url, timeout=30, stream=True)
            response.raise_for_status()

            # Create directory
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Save image
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.downloaded_count += 1
            time.sleep(self.rate_limit)
            return True

        except Exception as e:
            print(f"  ✗ Error downloading {image_data.get('id', 'unknown')}: {e}")
            self.failed_count += 1
            return False

    def download_topic(self, topic_name: str, search_terms: List[str],
                      specialty: str) -> int:
        """
        Download images for a single topic

        Args:
            topic_name: Name of the topic (used for folder)
            search_terms: List of search queries to try
            specialty: Specialty name

        Returns:
            Number of images downloaded
        """
        print(f"\n{'='*70}")
        print(f"Topic: {topic_name}")
        print(f"Specialty: {specialty}")
        print(f"{'='*70}")

        # Create topic directory
        topic_dir = self.output_dir / specialty / topic_name.replace(' ', '_').lower()
        topic_dir.mkdir(parents=True, exist_ok=True)

        images_downloaded = 0
        all_images = []

        # Try each search term
        for term in search_terms:
            if images_downloaded >= self.max_per_topic:
                break

            images = self.search(term, max_results=self.max_per_topic - images_downloaded)

            # Filter out duplicates (by ID)
            existing_ids = {img['id'] for img in all_images}
            new_images = [img for img in images if img['id'] not in existing_ids]
            all_images.extend(new_images)

            # Download new images
            for img in new_images:
                if images_downloaded >= self.max_per_topic:
                    break

                # Create filename
                img_id = img['id'].replace('/', '_').replace(':', '_')
                filename = f"openi_{img_id}.png"
                output_path = topic_dir / filename

                # Skip if already exists
                if output_path.exists():
                    print(f"  ⊙ Skipping {img_id} (already exists)")
                    images_downloaded += 1
                    continue

                # Download
                if self.download_image(img, output_path):
                    print(f"  ✓ Downloaded {img_id}")

                    # Save metadata
                    self.metadata.append({
                        'id': img['id'],
                        'filename': str(output_path),
                        'specialty': specialty,
                        'topic': topic_name,
                        'search_term': term,
                        'source': 'OpenI',
                        'url': img.get('url', ''),
                        'title': img.get('title', ''),
                        'journal': img.get('journal', ''),
                        'year': img.get('year', ''),
                        'downloaded_at': datetime.now().isoformat()
                    })

                    images_downloaded += 1

        print(f"\n✓ Downloaded {images_downloaded} images for {topic_name}")
        return images_downloaded

def load_taxonomy_search_terms(taxonomy_file: str, specialties: List[str] = None) -> Dict:
    """Load search terms from taxonomy file"""
    with open(taxonomy_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    taxonomy = data['taxonomy']
    topics = {}

    for spec_name, spec_data in taxonomy.items():
        if specialties and spec_name not in specialties:
            continue

        topics[spec_name] = []

        for subcat_name, subcat_data in spec_data['subcategories'].items():
            for topic_name, topic_data in subcat_data['topics'].items():
                for subtopic_name, subtopic_data in topic_data['subtopics'].items():
                    topics[spec_name].append({
                        'name': subtopic_name,
                        'search_terms': subtopic_data['search_terms'],
                        'amc_relevance': subtopic_data['amc_relevance']
                    })

    return topics


def main():
    parser = argparse.ArgumentParser(
        description='Download medical images from OpenI (NIH Open Access)'
    )
    parser.add_argument(
        '--taxonomy',
        default='data/medical_image_taxonomy_v1.json',
        help='Path to taxonomy JSON file'
    )
    parser.add_argument(
        '--specialties',
        nargs='+',
        required=True,
        help='Specialties to download (e.g., emergency_medicine neurology)'
    )
    parser.add_argument(
        '--images-per-topic',
        type=int,
        default=10,
        help='Maximum images per topic (default: 10)'
    )
    parser.add_argument(
        '--output',
        default='data/medical_images/openi',
        help='Output directory (default: data/medical_images/openi)'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--priority-only',
        action='store_true',
        help='Only download high-priority topics (AMC relevance 4-5)'
    )

    args = parser.parse_args()

    # Load taxonomy
    print(f"Loading taxonomy from {args.taxonomy}...")
    topics_by_specialty = load_taxonomy_search_terms(args.taxonomy, args.specialties)

    # Initialize downloader
    downloader = OpenIDownloader(
        output_dir=args.output,
        rate_limit=args.rate_limit,
        max_per_topic=args.images_per_topic
    )

    # Download for each specialty
    total_images = 0
    start_time = datetime.now()

    for specialty, topics in topics_by_specialty.items():
        print(f"\n{'#'*70}")
        print(f"# SPECIALTY: {specialty.upper()}")
        print(f"# Topics: {len(topics)}")
        print(f"{'#'*70}")

        # Filter by priority if requested
        if args.priority_only:
            topics = [t for t in topics if t['amc_relevance'] >= 4]
            print(f"# High-priority topics: {len(topics)}")

        # Download each topic
        for i, topic in enumerate(topics, 1):
            print(f"\n[{i}/{len(topics)}]")

            images_count = downloader.download_topic(
                topic_name=topic['name'],
                search_terms=topic['search_terms'],
                specialty=specialty
            )
            total_images += images_count

    # Save metadata
    metadata_file = Path(args.output) / 'openi_metadata.json'
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump({
            'download_date': datetime.now().isoformat(),
            'total_images': downloader.downloaded_count,
            'failed_downloads': downloader.failed_count,
            'specialties': args.specialties,
            'images_per_topic': args.images_per_topic,
            'images': downloader.metadata
        }, f, indent=2)

    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print(f"\n{'='*70}")
    print(f"DOWNLOAD COMPLETE")
    print(f"{'='*70}")
    print(f"Total images downloaded: {downloader.downloaded_count}")
    print(f"Failed downloads: {downloader.failed_count}")
    print(f"Duration: {duration/60:.1f} minutes")
    print(f"Metadata saved to: {metadata_file}")
    print(f"{'='*70}")


if __name__ == '__main__':
    main()
