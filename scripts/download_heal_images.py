#!/usr/bin/env python3
"""
Download images from HEAL collection via web scraping

Requirements:
    pip3 install requests beautifulsoup4 tqdm

Usage:
    python3 scripts/download_heal_images.py \
        --query "melanoma" \
        --collection dermatology \
        --max-images 30
"""

import requests
from bs4 import BeautifulSoup
import json
import time
from pathlib import Path
from tqdm import tqdm
import argparse
import csv

class HEALDownloader:
    """Download images from HEAL collection"""

    def __init__(self):
        self.base_url = "https://collections.lib.utah.edu"
        self.heal_filter = "facet_setname_s=ehsl_heal"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot - irStudy AMC Prep)'
        })

    def search_collection(self, query, max_results=50):
        """Search HEAL collection"""
        search_url = f"{self.base_url}/search"
        params = {
            'q': query,
            'facet_setname_s': 'ehsl_heal',
            'rows': max_results
        }

        try:
            response = self.session.get(search_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all result items
            results = []
            for item in soup.find_all('div', class_='search-result'):
                # Extract ARK identifier and title
                link = item.find('a', href=True)
                if link and '/ark:/' in link['href']:
                    ark_id = link['href'].split('/ark:/')[-1].split('/')[0]
                    title = link.text.strip()

                    results.append({
                        'heal_id': f"ark:/87278/{ark_id}",
                        'url': self.base_url + link['href'],
                        'title': title
                    })

            print(f"Found {len(results)} results for '{query}'")
            return results

        except Exception as e:
            print(f"Search error: {e}")
            return []

    def download_item(self, item_url, output_dir):
        """Download single item with metadata"""
        try:
            response = self.session.get(item_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract metadata
            metadata = {
                'url': item_url,
                'title': self._extract_meta(soup, 'title'),
                'description': self._extract_meta(soup, 'description'),
                'subject': self._extract_meta(soup, 'subject'),
                'collection': self._extract_meta(soup, 'collection'),
                'rights': self._extract_meta(soup, 'rights'),
                'format': self._extract_meta(soup, 'format'),
                'date': self._extract_meta(soup, 'date'),
            }

            # Find download link
            download_link = soup.find('a', text=lambda t: t and 'Download' in t)
            if not download_link:
                # Try finding image directly
                img_tag = soup.find('img', class_='item-image')
                if img_tag and img_tag.get('src'):
                    img_url = img_tag['src']
                    if not img_url.startswith('http'):
                        img_url = self.base_url + img_url
                else:
                    print(f"  No image found for {item_url}")
                    return None
            else:
                img_url = download_link['href']
                if not img_url.startswith('http'):
                    img_url = self.base_url + img_url

            # Download image
            img_response = self.session.get(img_url, timeout=30)
            if img_response.status_code == 200:
                # Generate filename from ARK ID
                ark_id = item_url.split('/ark:/')[-1].replace('/', '_')
                filename = f"heal_{ark_id}.jpg"
                filepath = Path(output_dir) / filename

                with open(filepath, 'wb') as f:
                    f.write(img_response.content)

                metadata['filepath'] = str(filepath)
                metadata['filename'] = filename
                metadata['heal_id'] = f"ark:/{item_url.split('/ark:/')[-1]}"
                metadata['file_size_kb'] = len(img_response.content) // 1024

                return metadata

        except Exception as e:
            print(f"  Download error: {e}")
            return None

    def _extract_meta(self, soup, field_name):
        """Extract metadata field"""
        # Try multiple patterns
        patterns = [
            lambda: soup.find('dt', text=lambda t: t and field_name.lower() in t.lower()),
            lambda: soup.find('meta', {'name': field_name}),
            lambda: soup.find('meta', {'property': f'og:{field_name}'})
        ]

        for pattern in patterns:
            try:
                elem = pattern()
                if elem:
                    if elem.name == 'dt':
                        dd = elem.find_next_sibling('dd')
                        if dd:
                            return dd.text.strip()
                    elif elem.name == 'meta':
                        return elem.get('content', '')
            except:
                continue

        return None

def main():
    parser = argparse.ArgumentParser(
        description='Download images from HEAL collection',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download 30 dermatology images
  python3 scripts/download_heal_images.py \\
      --query "melanoma OR psoriasis OR eczema" \\
      --collection dermatology \\
      --max-images 30

  # Download ECG images
  python3 scripts/download_heal_images.py \\
      --query "electrocardiogram OR ECG" \\
      --collection ecg \\
      --max-images 10
        '''
    )

    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--collection', required=True, help='Collection name (dermatology, ecg, histology)')
    parser.add_argument('--max-images', type=int, default=50, help='Maximum images to download')
    parser.add_argument('--output', default='data/medical_images/heal', help='Output directory')

    args = parser.parse_args()

    print(f"\n{'='*60}")
    print(f"HEAL Collection Downloader")
    print(f"{'='*60}\n")

    # Create output directory
    output_dir = Path(args.output) / args.collection
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize downloader
    downloader = HEALDownloader()

    # Search collection
    print(f"Searching HEAL for: '{args.query}'")
    results = downloader.search_collection(args.query, args.max_images)

    if not results:
        print("No results found")
        return

    # Download items
    downloaded = []
    for item in tqdm(results, desc="Downloading"):
        metadata = downloader.download_item(item['url'], output_dir)
        if metadata:
            downloaded.append(metadata)

        # Rate limiting (be respectful)
        time.sleep(2)

    # Save metadata
    if downloaded:
        metadata_file = output_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(downloaded, f, indent=2)

        # Save CSV for easy review
        csv_file = output_dir / 'metadata.csv'
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=downloaded[0].keys())
            writer.writeheader()
            writer.writerows(downloaded)

        print(f"\n{'='*60}")
        print(f"Download Complete")
        print(f"{'='*60}")
        print(f"Downloaded: {len(downloaded)} images")
        print(f"Location: {output_dir}")
        print(f"Metadata: {metadata_file}")

if __name__ == '__main__':
    main()
