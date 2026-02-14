#!/usr/bin/env python3
"""
Automated Cochrane Review PDF Downloader

Parses citation export files and downloads PDF versions of Cochrane Reviews.
Works with Cochrane Library's public access system.

Usage:
    python download_cochrane_pdfs.py --input citation-export.txt --output /mnt/data/medical_resources/cochrane/
"""

import argparse
import re
import time
import logging
from pathlib import Path
from typing import List, Dict
import requests
from urllib.parse import urljoin

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
        self.record_id = record_id  # e.g., "CD011429"
        self.doi = doi
        self.title = title
        self.authors = authors
        self.year = year
        self.specialty = None

    def get_safe_filename(self) -> str:
        """Generate safe filename for PDF"""
        # Clean title: remove special characters, limit length
        clean_title = re.sub(r'[^\w\s-]', '', self.title.lower())
        clean_title = re.sub(r'[\s_]+', '_', clean_title)
        clean_title = clean_title[:50]  # Limit length

        return f"{self.record_id}_{clean_title}.pdf"

    def get_pdf_url(self) -> str:
        """Construct PDF download URL from DOI"""
        # Cochrane PDF URLs follow pattern:
        # https://www.cochranelibrary.com/cdsr/doi/{DOI}/pdf
        if self.doi:
            return f"https://www.cochranelibrary.com/cdsr/doi/{self.doi}/pdf"
        else:
            # Fallback: construct from record ID
            return f"https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.{self.record_id}/pdf"

    def __repr__(self):
        return f"CochraneReview({self.record_id}: {self.title[:50]}...)"


class CochraneCitationParser:
    """Parser for Cochrane citation export files"""

    @staticmethod
    def parse_export_file(filepath: Path) -> List[CochraneReview]:
        """Parse citation export text file and extract review metadata"""
        reviews = []

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split into individual records
        # Format: "Record #N of M" followed by fields
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
        """Parse a single record from citation export"""
        # Extract fields using regex
        record_id_match = re.search(r'ID:\s*(\w+)', record_text)
        doi_match = re.search(r'DOI:\s*([\d\.\/]+)', record_text)
        title_match = re.search(r'TI:\s*(.+?)(?=\n[A-Z]{2}:|\n\n)', record_text, re.DOTALL)
        year_match = re.search(r'YR:\s*(\d{4})', record_text)

        # Extract authors (AU: fields)
        authors = re.findall(r'AU:\s*(.+)', record_text)

        if not record_id_match or not title_match:
            logger.warning("Missing required fields (ID or Title)")
            return None

        record_id = record_id_match.group(1)
        doi = doi_match.group(1) if doi_match else None
        title = title_match.group(1).strip().replace('\n', ' ')
        year = year_match.group(1) if year_match else "Unknown"

        return CochraneReview(
            record_id=record_id,
            doi=doi,
            title=title,
            authors=authors,
            year=year
        )


class CochraneDownloader:
    """Downloads Cochrane Review PDFs"""

    def __init__(self, output_dir: Path, delay: float = 2.0):
        self.output_dir = output_dir
        self.delay = delay  # Delay between downloads (be respectful)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def download_review(self, review: CochraneReview, specialty: str = "general") -> bool:
        """Download a single Cochrane Review PDF"""
        # Create specialty subdirectory
        specialty_dir = self.output_dir / specialty
        specialty_dir.mkdir(parents=True, exist_ok=True)

        output_path = specialty_dir / review.get_safe_filename()

        # Skip if already downloaded
        if output_path.exists():
            logger.info(f"✓ Already exists: {review.record_id}")
            return True

        pdf_url = review.get_pdf_url()
        logger.info(f"Downloading {review.record_id}: {review.title[:60]}...")
        logger.info(f"  URL: {pdf_url}")

        try:
            # Try to download PDF
            response = self.session.get(pdf_url, timeout=30, allow_redirects=True)

            # Check if we got a PDF
            content_type = response.headers.get('Content-Type', '')

            if response.status_code == 200 and 'pdf' in content_type.lower():
                # Save PDF
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                file_size = len(response.content) / 1024  # KB
                logger.info(f"✓ Downloaded: {output_path.name} ({file_size:.1f} KB)")
                return True

            elif response.status_code == 403 or response.status_code == 401:
                logger.warning(f"✗ Access denied for {review.record_id} (requires subscription)")
                return False

            elif 'html' in content_type.lower():
                # Got HTML instead of PDF - might be login page or paywall
                logger.warning(f"✗ PDF not available for {review.record_id} (got HTML, may require subscription)")

                # Try alternative: direct DOI resolution
                if review.doi:
                    alt_url = f"https://doi.org/{review.doi}"
                    logger.info(f"  Trying alternative URL: {alt_url}")
                    response2 = self.session.get(alt_url, timeout=30)

                    if response2.status_code == 200 and 'pdf' in response2.headers.get('Content-Type', '').lower():
                        with open(output_path, 'wb') as f:
                            f.write(response2.content)
                        logger.info(f"✓ Downloaded via DOI: {output_path.name}")
                        return True

                return False

            else:
                logger.warning(f"✗ Unexpected response for {review.record_id}: {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Download failed for {review.record_id}: {e}")
            return False

    def download_all(self, reviews: List[CochraneReview], specialty: str = "general") -> Dict[str, int]:
        """Download all reviews with progress tracking"""
        stats = {
            'total': len(reviews),
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

        logger.info(f"\n{'='*60}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Reviews")
        logger.info(f"Output directory: {self.output_dir / specialty}")
        logger.info(f"{'='*60}\n")

        for i, review in enumerate(reviews, 1):
            logger.info(f"[{i}/{len(reviews)}] Processing {review.record_id}...")

            success = self.download_review(review, specialty)

            if success:
                stats['success'] += 1
            else:
                stats['failed'] += 1

            # Respectful delay between downloads
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
        description='Download Cochrane Review PDFs from citation export file'
    )
    parser.add_argument(
        '--input',
        type=Path,
        default=Path.home() / 'Downloads' / 'citation-export(1).txt',
        help='Path to citation export file (default: ~/Downloads/citation-export(1).txt)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path('/mnt/data/medical_resources/cochrane'),
        help='Output directory for PDFs (default: /mnt/data/medical_resources/cochrane)'
    )
    parser.add_argument(
        '--specialty',
        type=str,
        default='cardiology',
        help='Specialty subdirectory name (default: cardiology)'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between downloads in seconds (default: 2.0)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit number of downloads (for testing)'
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        logger.error(f"Citation file not found: {args.input}")
        return 1

    # Parse citation file
    logger.info(f"Parsing citation file: {args.input}")
    parser_obj = CochraneCitationParser()
    reviews = parser_obj.parse_export_file(args.input)

    if not reviews:
        logger.error("No reviews found in citation file")
        return 1

    # Apply limit if specified (for testing)
    if args.limit:
        logger.info(f"Limiting to first {args.limit} reviews (testing mode)")
        reviews = reviews[:args.limit]

    # Download PDFs
    downloader = CochraneDownloader(args.output, delay=args.delay)
    stats = downloader.download_all(reviews, specialty=args.specialty)

    # Exit with error if all downloads failed
    if stats['success'] == 0 and stats['total'] > 0:
        logger.error("All downloads failed - check network connection or access permissions")
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
