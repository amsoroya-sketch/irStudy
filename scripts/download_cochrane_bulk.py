#!/usr/bin/env python3
"""
Cochrane Library Bulk Downloader

Downloads Cochrane Reviews from search results pages.
Can handle 2000+ results by pagination.

Usage:
    # Download from search URL
    python download_cochrane_bulk.py --url "https://www.cochranelibrary.com/search?q=cardiology" --output ~/Downloads/cochrane

    # Or use search term
    python download_cochrane_bulk.py --search "cardiology" --output ~/Downloads/cochrane --limit 100
"""

import argparse
import re
import time
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse, parse_qs, urlencode
import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CochraneSearchDownloader:
    """Downloads Cochrane Reviews from search results"""

    def __init__(self, output_dir: Path, delay: float = 3.0):
        self.output_dir = output_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        self.base_url = "https://www.cochranelibrary.com"
        self.downloaded_ids = set()

    def search(self, query: str, reviews_only: bool = True, max_results: int = None) -> List[Dict]:
        """Search Cochrane Library and return all results"""

        # Build search URL
        params = {
            'searchText': query,
            'contentType': 'cochrane-reviews' if reviews_only else '',
            'resultsPerPage': 25  # Cochrane default
        }

        search_url = f"{self.base_url}/search"

        all_results = []
        page = 1

        while True:
            logger.info(f"Fetching page {page}...")

            params['page'] = page

            try:
                response = self.session.get(search_url, params=params, timeout=30)

                if response.status_code != 200:
                    logger.error(f"Search failed: HTTP {response.status_code}")
                    break

                soup = BeautifulSoup(response.text, 'html.parser')

                # Find all review results
                results = self._parse_search_page(soup)

                if not results:
                    logger.info(f"No more results on page {page}")
                    break

                all_results.extend(results)
                logger.info(f"  Found {len(results)} reviews on page {page} (total: {len(all_results)})")

                # Check if we've hit the limit
                if max_results and len(all_results) >= max_results:
                    logger.info(f"Reached limit of {max_results} results")
                    all_results = all_results[:max_results]
                    break

                # Check if there's a next page
                next_button = soup.find('a', {'aria-label': 'Next page'}) or soup.find('a', text=re.compile('Next', re.I))

                if not next_button or 'disabled' in next_button.get('class', []):
                    logger.info("No more pages available")
                    break

                page += 1
                time.sleep(self.delay)

            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                break

        logger.info(f"\nTotal reviews found: {len(all_results)}")
        return all_results

    def _parse_search_page(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse search results page and extract review metadata"""
        results = []

        # Cochrane uses different selectors - try multiple patterns
        result_items = (
            soup.find_all('div', class_=re.compile('search-result', re.I)) or
            soup.find_all('article', class_=re.compile('result', re.I)) or
            soup.find_all('li', class_=re.compile('search-results-item', re.I))
        )

        for item in result_items:
            try:
                # Extract title and link
                title_elem = item.find('h3') or item.find('h2') or item.find('a', class_=re.compile('title', re.I))

                if not title_elem:
                    continue

                link_elem = title_elem.find('a') if title_elem.name != 'a' else title_elem

                if not link_elem:
                    continue

                title = link_elem.get_text(strip=True)
                href = link_elem.get('href', '')

                if not href:
                    continue

                # Build full URL
                full_url = urljoin(self.base_url, href)

                # Extract DOI/ID from URL
                doi_match = re.search(r'(CD\d+)', href) or re.search(r'10\.1002/14651858\.(CD\d+)', href)
                review_id = doi_match.group(1) if doi_match else None

                # Extract year if available
                year_elem = item.find(text=re.compile(r'\b(19|20)\d{2}\b'))
                year = re.search(r'\b(19|20)\d{2}\b', year_elem).group(1) if year_elem else None

                # Extract authors if available
                authors_elem = item.find('div', class_=re.compile('author', re.I))
                authors = authors_elem.get_text(strip=True) if authors_elem else ""

                results.append({
                    'id': review_id,
                    'title': title,
                    'url': full_url,
                    'year': year,
                    'authors': authors
                })

            except Exception as e:
                logger.warning(f"Failed to parse result item: {e}")
                continue

        return results

    def download_review(self, review: Dict, specialty: str = "general") -> bool:
        """Download HTML version of a single review"""

        review_id = review.get('id', 'unknown')

        # Skip if already downloaded
        if review_id in self.downloaded_ids:
            logger.info(f"✓ Already downloaded: {review_id}")
            return True

        specialty_dir = self.output_dir / specialty
        specialty_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        safe_title = re.sub(r'[^\w\s-]', '', review['title'].lower())
        safe_title = re.sub(r'[\s_]+', '_', safe_title)[:50]
        filename = f"{review_id}_{safe_title}.html" if review_id else f"{safe_title}.html"

        output_path = specialty_dir / filename

        if output_path.exists():
            logger.info(f"✓ Already exists: {filename}")
            self.downloaded_ids.add(review_id)
            return True

        logger.info(f"Downloading: {review['title'][:60]}...")
        logger.info(f"  ID: {review_id}, URL: {review['url']}")

        try:
            response = self.session.get(review['url'], timeout=30)

            if response.status_code == 200:
                # Save HTML
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                file_size = len(response.text) / 1024
                logger.info(f"✓ Downloaded: {filename} ({file_size:.1f} KB)")

                # Save metadata
                metadata = {
                    'id': review_id,
                    'title': review['title'],
                    'url': review['url'],
                    'year': review.get('year'),
                    'authors': review.get('authors'),
                    'downloaded': time.strftime('%Y-%m-%d %H:%M:%S')
                }

                metadata_path = specialty_dir / f"{review_id}_metadata.json" if review_id else specialty_dir / f"{safe_title}_metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)

                self.downloaded_ids.add(review_id)
                return True

            else:
                logger.warning(f"✗ Failed: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"✗ Download failed: {e}")
            return False

    def download_all(self, reviews: List[Dict], specialty: str = "general") -> Dict[str, int]:
        """Download all reviews with progress tracking"""

        stats = {'total': len(reviews), 'success': 0, 'failed': 0, 'skipped': 0}

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Reviews")
        logger.info(f"Output directory: {self.output_dir / specialty}")
        logger.info(f"{'='*60}\n")

        for i, review in enumerate(reviews, 1):
            logger.info(f"[{i}/{len(reviews)}] Processing {review.get('id', 'unknown')}...")

            success = self.download_review(review, specialty)

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

            # Respectful delay
            if i < len(reviews):
                time.sleep(self.delay)

        logger.info(f"\n{'='*60}")
        logger.info(f"Download Summary:")
        logger.info(f"  Total reviews: {stats['total']}")
        logger.info(f"  ✓ Successfully downloaded: {stats['success']}")
        logger.info(f"  ✗ Failed: {stats['failed']}")
        logger.info(f"{'='*60}\n")

        return stats


def main():
    parser = argparse.ArgumentParser(description='Download Cochrane Reviews from search results')
    parser.add_argument('--search', type=str, help='Search query (e.g., "cardiology")')
    parser.add_argument('--url', type=str, help='Direct search results URL')
    parser.add_argument('--output', type=Path, default=Path.home() / 'Downloads' / 'cochrane', help='Output directory')
    parser.add_argument('--specialty', type=str, default='general', help='Specialty subdirectory')
    parser.add_argument('--limit', type=int, help='Maximum number of reviews to download')
    parser.add_argument('--delay', type=float, default=3.0, help='Delay between downloads (seconds)')
    parser.add_argument('--reviews-only', action='store_true', default=True, help='Only download Cochrane Reviews (not protocols, etc.)')

    args = parser.parse_args()

    if not args.search and not args.url:
        logger.error("Must provide either --search or --url")
        return 1

    downloader = CochraneSearchDownloader(args.output, delay=args.delay)

    # Get search results
    if args.search:
        logger.info(f"Searching Cochrane Library for: '{args.search}'")
        reviews = downloader.search(args.search, reviews_only=args.reviews_only, max_results=args.limit)
    else:
        logger.info(f"Fetching reviews from URL: {args.url}")
        # Parse URL to extract search parameters
        # For now, just use search parameter from URL
        parsed = urlparse(args.url)
        params = parse_qs(parsed.query)
        search_query = params.get('q', params.get('searchText', ['']))[0]

        if search_query:
            reviews = downloader.search(search_query, reviews_only=args.reviews_only, max_results=args.limit)
        else:
            logger.error("Could not extract search query from URL")
            return 1

    if not reviews:
        logger.error("No reviews found")
        return 1

    # Download all reviews
    stats = downloader.download_all(reviews, specialty=args.specialty)

    if stats['success'] == 0:
        logger.error("All downloads failed")
        return 1

    logger.info(f"\n✓ Download complete! Files saved to: {args.output / args.specialty}")
    return 0


if __name__ == '__main__':
    exit(main())
