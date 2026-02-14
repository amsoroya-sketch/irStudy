#!/usr/bin/env python3
"""
Automated HEAL image downloader using Playwright

This script:
1. Searches HEAL collection by query
2. Extracts all file IDs from search results
3. Downloads images using direct file links
4. Saves complete metadata

Requirements:
    pip3 install playwright beautifulsoup4 tqdm
    playwright install chromium

Usage:
    # Download dermatology images
    python3 scripts/download_heal_playwright.py \
        --query "melanoma" \
        --collection dermatology \
        --max-images 30

    # Download ECG images
    python3 scripts/download_heal_playwright.py \
        --query "electrocardiogram" \
        --collection ecg \
        --max-images 10
"""

import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import json
import argparse
from pathlib import Path
from tqdm import tqdm
import time
import csv
from datetime import datetime
import re

class HEALPlaywrightDownloader:
    """Automated HEAL downloader using Playwright"""

    def __init__(self, headless=True, slow_mo=500):
        self.base_url = "https://collections.lib.utah.edu"
        self.search_url = f"{self.base_url}/search"
        self.headless = headless
        self.slow_mo = slow_mo
        self.results = []

    async def search_and_extract_ids(self, query, max_results=50):
        """Search HEAL collection and extract all file IDs"""

        print(f"\n{'='*70}")
        print(f"Searching HEAL Collection")
        print(f"{'='*70}")
        print(f"Query: {query}")
        print(f"Max results: {max_results}")
        print(f"")

        async with async_playwright() as p:
            # Launch browser
            browser = await p.chromium.launch(
                headless=self.headless,
                slow_mo=self.slow_mo
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )

            page = await context.new_page()

            try:
                # Navigate to HEAL search with filter
                search_params = f"?q={query}&facet_setname_s=ehsl_heal&rows={max_results}"
                search_full_url = f"{self.search_url}{search_params}"
                print(f"Navigating to: {search_full_url}")

                await page.goto(search_full_url, wait_until='networkidle', timeout=30000)
                await asyncio.sleep(3)  # Wait for dynamic content

                # Extract page content
                content = await page.content()
                soup = BeautifulSoup(content, 'html.parser')

                # Save HTML for debugging (optional)
                # with open('debug_heal_search.html', 'w') as f:
                #     f.write(content)

                # Find all result items - HEAL uses /details?id= pattern
                print("\nExtracting file IDs from search results...")
                file_ids = []

                # Method 1: Look for /details?id= links
                for link in soup.find_all('a', href=True):
                    href = link['href']

                    # Pattern: /details?id=872205
                    if '/details?id=' in href:
                        match = re.search(r'/details\?id=(\d+)', href)
                        if match:
                            file_id = match.group(1)
                            if file_id not in file_ids:
                                file_ids.append(file_id)
                                print(f"  Found ID: {file_id}")

                # Method 2: Look for /file?id= pattern (alternate)
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if '/file?id=' in href:
                        match = re.search(r'/file\?id=(\d+)', href)
                        if match:
                            file_id = match.group(1)
                            if file_id not in file_ids:
                                file_ids.append(file_id)
                                print(f"  Found ID: {file_id}")

                # Method 3: Look for thumbnail patterns
                for img in soup.find_all('img', src=True):
                    src = img['src']
                    # Thumbnails like: /dl_thumbs/48/ca/48ca3e63d31f5c612df11be135fe0c6efa08c4a1.jpg
                    if '/dl_thumbs/' in src:
                        # Get the parent link
                        parent_link = img.find_parent('a')
                        if parent_link and parent_link.get('href'):
                            href = parent_link['href']
                            if '/details?id=' in href:
                                match = re.search(r'/details\?id=(\d+)', href)
                                if match:
                                    file_id = match.group(1)
                                    if file_id not in file_ids:
                                        file_ids.append(file_id)
                                        print(f"  Found ID (from thumbnail): {file_id}")

                if not file_ids:
                    print("\n⚠️  No file IDs found. Checking page content...")
                    print(f"   Page title: {soup.title.string if soup.title else 'No title'}")
                    print(f"   Total links found: {len(soup.find_all('a', href=True))}")

                    # Show sample links for debugging
                    sample_links = soup.find_all('a', href=True)[:10]
                    print(f"\n   Sample links:")
                    for link in sample_links:
                        print(f"     {link.get('href')}")

                print(f"\n✓ Found {len(file_ids)} unique file IDs")

                if not file_ids:
                    print("\n❌ No results found. This could mean:")
                    print("   1. No items match your search query in HEAL collection")
                    print("   2. The search page structure changed")
                    print("   3. Network/access issue")
                    print(f"\n   Try searching manually: {search_full_url}")
                    return []

                # Extract metadata for each result
                print("\nExtracting metadata...")
                results = []

                for idx, file_id in enumerate(file_ids[:max_results], 1):
                    print(f"  [{idx}/{min(len(file_ids), max_results)}] Processing ID: {file_id}")

                    metadata = await self._extract_item_metadata(page, file_id)
                    if metadata:
                        results.append(metadata)

                    # Rate limiting
                    await asyncio.sleep(1)

                self.results = results
                return results

            except Exception as e:
                print(f"Error during search: {e}")
                import traceback
                traceback.print_exc()
                return []

            finally:
                await browser.close()

    async def _extract_item_metadata(self, page, file_id):
        """Extract metadata for a single item"""

        try:
            # Try details page first
            details_url = f"{self.base_url}/details?id={file_id}"

            await page.goto(details_url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(1)

            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')

            # Extract metadata
            metadata = {
                'file_id': file_id,
                'details_url': details_url,
                'title': self._extract_field(soup, ['title']),
                'description': self._extract_field(soup, ['description', 'abstract', 'summary']),
                'subject': self._extract_field(soup, ['subject', 'keywords', 'topic']),
                'collection': self._extract_field(soup, ['collection', 'set', 'source']),
                'creator': self._extract_field(soup, ['creator', 'author', 'contributor']),
                'date': self._extract_field(soup, ['date', 'created']),
                'rights': self._extract_field(soup, ['rights', 'license', 'usage']),
                'format': self._extract_field(soup, ['format', 'type', 'media type']),
            }

            # Find image download URL
            image_url = None

            # Method 1: Look for /dl_files/ image (actual image file)
            # This is the most reliable method - HEAL stores images at /dl_files/ paths
            for img in soup.find_all('img', src=True):
                src = img['src']
                if '/dl_files/' in src:
                    image_url = src
                    break

            # Method 2: Extract from imagezoom viewer initialization
            # HEAL uses: viewer = new imagezoom('canvas', '/dl_files/...jpg', false, 'high');
            if not image_url:
                script_pattern = r"imagezoom\('canvas',\s*'([^']+)',\s*false,\s*'high'\)"
                for script in soup.find_all('script'):
                    script_text = script.string if script.string else ''
                    match = re.search(script_pattern, script_text)
                    if match:
                        image_url = match.group(1)
                        break

            # Method 3: Look for download link (fallback)
            if not image_url:
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    link_text = link.get_text(strip=True).lower()
                    if 'download' in link_text and '/file?id=' in href:
                        # Note: /file?id= may be blocked, but keep as last resort
                        image_url = href
                        break

            # Make URL absolute
            if image_url and not image_url.startswith('http'):
                image_url = self.base_url + image_url

            metadata['image_url'] = image_url

            return metadata

        except Exception as e:
            print(f"    Error extracting metadata for ID {file_id}: {e}")
            return None

    def _extract_field(self, soup, field_names):
        """Extract metadata field from HTML"""

        for field_name in field_names:
            # Try h1-h6 for title
            if field_name == 'title':
                for tag in ['h1', 'h2', 'h3']:
                    heading = soup.find(tag)
                    if heading:
                        text = heading.get_text(strip=True)
                        if text and len(text) > 5:  # Avoid short/generic titles
                            return text

            # Try dt/dd pattern (common in metadata displays)
            dt_tags = soup.find_all('dt')
            for dt in dt_tags:
                dt_text = dt.get_text(strip=True).lower()
                if field_name.lower() in dt_text:
                    dd = dt.find_next_sibling('dd')
                    if dd:
                        return dd.get_text(strip=True)

            # Try meta tag
            meta = soup.find('meta', {'name': field_name})
            if meta and meta.get('content'):
                return meta.get('content', '')

            # Try property meta tag
            meta = soup.find('meta', {'property': f'og:{field_name}'})
            if meta and meta.get('content'):
                return meta.get('content', '')

            # Try label + value pattern
            labels = soup.find_all(['label', 'span', 'strong', 'b'])
            for label in labels:
                label_text = label.get_text(strip=True).lower()
                if field_name.lower() in label_text:
                    # Get next sibling or parent's next sibling
                    next_elem = label.find_next_sibling()
                    if next_elem:
                        return next_elem.get_text(strip=True)

        return None

    async def download_images(self, results, output_dir):
        """Download all images from results"""

        print(f"\n{'='*70}")
        print(f"Downloading Images")
        print(f"{'='*70}")
        print(f"Total images: {len(results)}")
        print(f"Output: {output_dir}")
        print(f"")

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        downloaded = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await browser.new_context()
            page = await context.new_page()

            for idx, item in enumerate(tqdm(results, desc="Downloading"), 1):
                try:
                    image_url = item.get('image_url')
                    if not image_url:
                        print(f"  [{idx}] Skipping - no image URL")
                        continue

                    # Navigate to image URL
                    response = await page.goto(image_url, wait_until='domcontentloaded', timeout=30000)

                    if response and response.ok:
                        # Get image content
                        image_data = await response.body()

                        # Determine file extension from content-type
                        content_type = response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = 'jpg'
                        elif 'png' in content_type:
                            ext = 'png'
                        elif 'gif' in content_type:
                            ext = 'gif'
                        else:
                            ext = 'jpg'  # default

                        # Generate filename
                        file_id = item['file_id']
                        filename = f"heal_{file_id}.{ext}"
                        filepath = output_path / filename

                        # Save image
                        with open(filepath, 'wb') as f:
                            f.write(image_data)

                        # Update metadata
                        item['filepath'] = str(filepath)
                        item['filename'] = filename
                        item['file_size_kb'] = len(image_data) // 1024
                        item['downloaded_at'] = datetime.now().isoformat()

                        downloaded.append(item)

                    else:
                        print(f"  [{idx}] Failed - HTTP {response.status if response else 'N/A'}: {image_url}")

                except Exception as e:
                    print(f"  [{idx}] Error downloading {item.get('file_id')}: {e}")

                # Rate limiting
                await asyncio.sleep(1)

            await browser.close()

        return downloaded

def save_metadata(results, output_dir, collection_name):
    """Save metadata in multiple formats"""

    output_path = Path(output_dir)

    # JSON format
    json_file = output_path / f"{collection_name}_metadata.json"
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    # CSV format
    if results:
        csv_file = output_path / f"{collection_name}_metadata.csv"
        with open(csv_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=results[0].keys())
            writer.writeheader()
            writer.writerows(results)
        return json_file, csv_file

    return json_file, None

async def main():
    parser = argparse.ArgumentParser(
        description='Automated HEAL image downloader using Playwright',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Download dermatology images
  python3 scripts/download_heal_playwright.py \\
      --query "melanoma" \\
      --collection dermatology \\
      --max-images 30

  # Download ECG images
  python3 scripts/download_heal_playwright.py \\
      --query "electrocardiogram" \\
      --collection ecg \\
      --max-images 10

  # Show browser (for debugging)
  python3 scripts/download_heal_playwright.py \\
      --query "melanoma" \\
      --collection dermatology \\
      --max-images 5 \\
      --show-browser
        '''
    )

    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--collection', required=True, help='Collection name (dermatology, ecg, histology)')
    parser.add_argument('--max-images', type=int, default=50, help='Maximum images to download')
    parser.add_argument('--output', default='data/medical_images/heal', help='Output directory')
    parser.add_argument('--show-browser', action='store_true', help='Show browser (not headless)')

    args = parser.parse_args()

    print(f"\n{'='*70}")
    print(f"HEAL Automated Downloader (Playwright)")
    print(f"{'='*70}\n")

    # Create output directory
    output_dir = Path(args.output) / args.collection
    output_dir.mkdir(parents=True, exist_ok=True)

    # Initialize downloader
    downloader = HEALPlaywrightDownloader(
        headless=not args.show_browser,
        slow_mo=500 if args.show_browser else 0
    )

    # Step 1: Search and extract IDs
    results = await downloader.search_and_extract_ids(args.query, args.max_images)

    if not results:
        print("\n✗ No results found")
        print("\nTroubleshooting:")
        print("1. Try a broader search term (e.g., 'dermatology' instead of 'melanoma')")
        print("2. Check HEAL collection manually:")
        print(f"   https://collections.lib.utah.edu/search?q={args.query}&facet_setname_s=ehsl_heal")
        return

    print(f"\n✓ Found {len(results)} items to download")

    # Step 2: Download images
    downloaded = await downloader.download_images(results, output_dir)

    if not downloaded:
        print("\n✗ No images downloaded")
        return

    # Step 3: Save metadata
    json_file, csv_file = save_metadata(downloaded, output_dir, args.collection)

    # Summary
    print(f"\n{'='*70}")
    print(f"Download Complete!")
    print(f"{'='*70}")
    print(f"✓ Downloaded: {len(downloaded)} images")
    print(f"✓ Location: {output_dir}")
    print(f"✓ Metadata JSON: {json_file}")
    if csv_file:
        print(f"✓ Metadata CSV: {csv_file}")
    print(f"\nNext steps:")
    print(f"1. Review downloaded images: ls -lh {output_dir}")
    print(f"2. Run: python3 scripts/process_image_metadata.py --source {args.output}")
    print(f"3. Run: python3 scripts/enrich_heal_metadata.py --metadata data/heal_metadata.json")

if __name__ == '__main__':
    asyncio.run(main())
