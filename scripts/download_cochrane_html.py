#!/usr/bin/env python3
"""
Automated Cochrane Review HTML Downloader (FREE VERSION)

Downloads FREE HTML versions of Cochrane Reviews instead of PDFs.
Cochrane Library provides free access to full-text HTML, but PDFs require subscription.

Usage:
    python download_cochrane_html.py --input citation-export.txt --output ~/cochrane_downloads/
"""

import argparse
import re
import time
import logging
from pathlib import Path
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class CochraneReview:
    """Represents a single Cochrane Review"""

    def __init__(self, record_id: str, doi: str, title: str, authors: List[str], year: str):
        self.record_id = record_id
        self.doi = doi
        self.title = title
        self.authors = authors
        self.year = year

    def get_safe_filename(self, extension='html') -> str:
        """Generate safe filename"""
        clean_title = re.sub(r'[^\w\s-]', '', self.title.lower())
        clean_title = re.sub(r'[\s_]+', '_', clean_title)
        clean_title = clean_title[:50]
        return f"{self.record_id}_{clean_title}.{extension}"

    def get_html_url(self) -> str:
        """Construct HTML full-text URL"""
        if self.doi:
            return f"https://www.cochranelibrary.com/cdsr/doi/{self.doi}/full"
        else:
            return f"https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.{self.record_id}/full"

    def __repr__(self):
        return f"CochraneReview({self.record_id}: {self.title[:50]}...)"


class CochraneCitationParser:
    """Parser for Cochrane citation export files"""

    @staticmethod
    def parse_export_file(filepath: Path) -> List[CochraneReview]:
        """Parse citation export text file"""
        reviews = []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        record_pattern = r'Record #\d+ of \d+\n(.*?)(?=Record #\d+ of \d+|\Z)'
        records = re.findall(record_pattern, content, re.DOTALL)

        logger.info(f"Found {len(records)} records in citation file")

        for record_text in records:
            try:
                review = CochraneCitationParser._parse_single_record(record_text)
                if review:
                    reviews.append(review)
            except Exception as e:
                logger.warning(f"Failed to parse record: {e}")
                continue

        logger.info(f"Successfully parsed {len(reviews)} Cochrane Reviews")
        return reviews

    @staticmethod
    def _parse_single_record(record_text: str) -> CochraneReview:
        """Parse a single record"""
        record_id_match = re.search(r'ID:\s*(\w+)', record_text)
        doi_match = re.search(r'DOI:\s*([\d\.\/]+)', record_text)
        title_match = re.search(r'TI:\s*(.+?)(?=\n[A-Z]{2}:|\n\n)', record_text, re.DOTALL)
        year_match = re.search(r'YR:\s*(\d{4})', record_text)
        authors = re.findall(r'AU:\s*(.+)', record_text)

        if not record_id_match or not title_match:
            return None

        return CochraneReview(
            record_id=record_id_match.group(1),
            doi=doi_match.group(1) if doi_match else None,
            title=title_match.group(1).strip().replace('\n', ' '),
            year=year_match.group(1) if year_match else "Unknown",
            authors=authors
        )


class CochraneHTMLDownloader:
    """Downloads Cochrane Review HTML versions (FREE)"""

    def __init__(self, output_dir: Path, delay: float = 2.0):
        self.output_dir = output_dir
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })

    def download_review(self, review: CochraneReview, specialty: str = "general") -> bool:
        """Download FREE HTML version of review"""
        specialty_dir = self.output_dir / specialty
        specialty_dir.mkdir(parents=True, exist_ok=True)

        output_path = specialty_dir / review.get_safe_filename('html')

        if output_path.exists():
            logger.info(f"✓ Already exists: {review.record_id}")
            return True

        html_url = review.get_html_url()
        logger.info(f"Downloading {review.record_id}: {review.title[:60]}...")
        logger.info(f"  URL: {html_url}")

        try:
            response = self.session.get(html_url, timeout=30, allow_redirects=True)

            if response.status_code == 200:
                # Save full HTML
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)

                file_size = len(response.text) / 1024
                logger.info(f"✓ Downloaded: {output_path.name} ({file_size:.1f} KB)")

                # Also create a clean text version
                try:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Extract main content
                    main_content = soup.find('div', class_='main-content') or soup.find('article')

                    if main_content:
                        text_path = specialty_dir / review.get_safe_filename('txt')
                        with open(text_path, 'w', encoding='utf-8') as f:
                            f.write(f"COCHRANE REVIEW: {review.title}\n")
                            f.write(f"ID: {review.record_id}\n")
                            f.write(f"DOI: {review.doi}\n")
                            f.write(f"Year: {review.year}\n")
                            f.write(f"Authors: {', '.join(review.authors[:5])}\n")
                            f.write("="*80 + "\n\n")
                            f.write(main_content.get_text(separator='\n', strip=True))

                        logger.info(f"  ✓ Saved text version: {text_path.name}")

                except Exception as e:
                    logger.warning(f"  Could not create text version: {e}")

                return True

            elif response.status_code == 403 or response.status_code == 401:
                logger.warning(f"✗ Access denied for {review.record_id}")
                return False

            else:
                logger.warning(f"✗ Failed: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Download failed: {e}")
            return False

    def download_all(self, reviews: List[CochraneReview], specialty: str = "general") -> Dict[str, int]:
        """Download all reviews"""
        stats = {'total': len(reviews), 'success': 0, 'failed': 0}

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Reviews (HTML)")
        logger.info(f"Output directory: {self.output_dir / specialty}")
        logger.info(f"{'='*60}\n")

        for i, review in enumerate(reviews, 1):
            logger.info(f"[{i}/{len(reviews)}] Processing {review.record_id}...")

            success = self.download_review(review, specialty)

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

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
    parser = argparse.ArgumentParser(
        description='Download FREE Cochrane Review HTML versions'
    )
    parser.add_argument(
        '--input', type=Path,
        default=Path.home() / 'Downloads' / 'citation-export(1).txt'
    )
    parser.add_argument(
        '--output', type=Path,
        default=Path.home() / 'cochrane_downloads'
    )
    parser.add_argument('--specialty', type=str, default='cardiology')
    parser.add_argument('--delay', type=float, default=2.0)
    parser.add_argument('--limit', type=int, default=None)

    args = parser.parse_args()

    if not args.input.exists():
        logger.error(f"Citation file not found: {args.input}")
        return 1

    parser_obj = CochraneCitationParser()
    reviews = parser_obj.parse_export_file(args.input)

    if not reviews:
        logger.error("No reviews found")
        return 1

    if args.limit:
        logger.info(f"Limiting to first {args.limit} reviews")
        reviews = reviews[:args.limit]

    downloader = CochraneHTMLDownloader(args.output, delay=args.delay)
    stats = downloader.download_all(reviews, specialty=args.specialty)

    if stats['success'] == 0 and stats['total'] > 0:
        logger.error("All downloads failed")
        return 1

    logger.info(f"\nFiles saved to: {args.output / args.specialty}")
    logger.info("You can read HTML files in browser or convert to PDF later")

    return 0


if __name__ == '__main__':
    exit(main())
