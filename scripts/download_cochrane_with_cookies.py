#!/usr/bin/env python3
"""
Download Cochrane PDFs using Firefox cookies

SETUP:
1. In Firefox, install "cookies.txt" extension
2. Navigate to cochranelibrary.com while logged in
3. Click cookies.txt extension → Export cookies.txt
4. Save to ~/Downloads/cookies.txt
5. Run this script

Usage:
    python download_cochrane_with_cookies.py --input ~/Downloads/citation-export(2).txt --cookies ~/Downloads/cookies.txt --output ~/cochrane_downloads
"""

import argparse
import re
import time
import logging
import subprocess
from pathlib import Path
from typing import List, Dict

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

    def get_safe_filename(self) -> str:
        """Generate safe filename for PDF"""
        clean_title = re.sub(r'[^\w\s-]', '', self.title.lower())
        clean_title = re.sub(r'[\s_]+', '_', clean_title)
        clean_title = clean_title[:60]
        return f"{self.record_id}_{clean_title}.pdf"

    def get_pdf_url(self) -> str:
        """Construct PDF download URL from DOI"""
        if self.doi:
            return f"https://www.cochranelibrary.com/cdsr/doi/{self.doi}/pdf/full"
        return None


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

        for i, record_text in enumerate(records, 1):
            try:
                review = CochraneCitationParser._parse_single_record(record_text)
                if review:
                    reviews.append(review)

                if i % 500 == 0:
                    logger.info(f"  Parsed {i}/{len(records)} records...")

            except Exception as e:
                logger.warning(f"Failed to parse record {i}: {e}")
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


class CochraneCookieDownloader:
    """Downloads Cochrane PDFs using wget with cookies"""

    def __init__(self, output_dir: Path, cookies_file: Path, delay: float = 2.0):
        self.output_dir = output_dir
        self.cookies_file = cookies_file
        self.delay = delay
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    def download_review(self, review: CochraneReview) -> bool:
        """Download a single review using wget with cookies"""

        output_path = self.output_dir / review.get_safe_filename()

        # Skip if already exists
        if output_path.exists() and output_path.stat().st_size > 10000:
            logger.info(f"✓ Already exists: {review.record_id}")
            self.stats['skipped'] += 1
            return True

        pdf_url = review.get_pdf_url()
        if not pdf_url:
            logger.warning(f"✗ No DOI for {review.record_id}")
            self.stats['failed'] += 1
            return False

        logger.info(f"Downloading {review.record_id}: {review.title[:60]}...")

        try:
            # Use wget with cookies
            cmd = [
                'wget',
                '--load-cookies', str(self.cookies_file),
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
                '--timeout=60',
                '--tries=3',
                '-O', str(output_path),
                pdf_url
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )

            # Check if download was successful
            if result.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size

                # Check if we got a real PDF (not HTML error page)
                if file_size > 10000:  # At least 10KB
                    # Verify it's actually a PDF
                    with open(output_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            logger.info(f"✓ Downloaded: {output_path.name} ({file_size/1024:.1f} KB)")
                            self.stats['success'] += 1
                            return True

                # Not a valid PDF
                logger.warning(f"✗ Downloaded file is not a PDF: {review.record_id}")
                output_path.unlink()  # Delete the non-PDF file
                self.stats['failed'] += 1
                return False

            else:
                logger.warning(f"✗ Download failed: {review.record_id}")
                if output_path.exists():
                    output_path.unlink()
                self.stats['failed'] += 1
                return False

        except subprocess.TimeoutExpired:
            logger.error(f"✗ Timeout: {review.record_id}")
            if output_path.exists():
                output_path.unlink()
            self.stats['failed'] += 1
            return False

        except Exception as e:
            logger.error(f"✗ Error: {review.record_id} - {e}")
            if output_path.exists():
                output_path.unlink()
            self.stats['failed'] += 1
            return False

    def download_all(self, reviews: List[CochraneReview]) -> Dict[str, int]:
        """Download all reviews"""

        self.stats['total'] = len(reviews)

        logger.info(f"\n{'='*70}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Review PDFs")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Using cookies from: {self.cookies_file}")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        for i, review in enumerate(reviews, 1):
            logger.info(f"[{i}/{len(reviews)}] Processing {review.record_id}...")

            self.download_review(review)

            # Progress update every 50 downloads
            if i % 50 == 0:
                elapsed = time.time() - start_time
                avg_time = elapsed / i
                remaining = (len(reviews) - i) * avg_time

                logger.info(f"\n--- Progress Update ---")
                logger.info(f"  Processed: {i}/{len(reviews)} ({i/len(reviews)*100:.1f}%)")
                logger.info(f"  Success: {self.stats['success']}, Failed: {self.stats['failed']}")
                logger.info(f"  Time elapsed: {elapsed/60:.1f} min")
                logger.info(f"  Estimated remaining: {remaining/60:.1f} min")
                logger.info(f"-----------------------\n")

            # Delay between downloads
            if i < len(reviews):
                time.sleep(self.delay)

        elapsed = time.time() - start_time

        logger.info(f"\n{'='*70}")
        logger.info(f"Download Complete!")
        logger.info(f"{'='*70}")
        logger.info(f"  Total reviews: {self.stats['total']}")
        logger.info(f"  ✓ Successfully downloaded: {self.stats['success']}")
        logger.info(f"  ⊘ Skipped (already exist): {self.stats['skipped']}")
        logger.info(f"  ✗ Failed: {self.stats['failed']}")
        logger.info(f"  Total time: {elapsed/60:.1f} minutes")
        logger.info(f"{'='*70}\n")

        return self.stats


def main():
    parser = argparse.ArgumentParser(
        description='Download Cochrane PDFs using Firefox cookies'
    )
    parser.add_argument('--input', type=Path, required=True, help='Citation export file')
    parser.add_argument('--cookies', type=Path, required=True, help='Cookies.txt file from Firefox')
    parser.add_argument('--output', type=Path, default=Path.home() / 'cochrane_downloads', help='Output directory')
    parser.add_argument('--delay', type=float, default=2.0, help='Delay between downloads (seconds)')
    parser.add_argument('--limit', type=int, help='Limit number of downloads')

    args = parser.parse_args()

    if not args.input.exists():
        logger.error(f"Citation file not found: {args.input}")
        return 1

    if not args.cookies.exists():
        logger.error(f"Cookies file not found: {args.cookies}")
        logger.error("\nTo export cookies:")
        logger.error("1. Install 'cookies.txt' extension in Firefox")
        logger.error("2. Go to cochranelibrary.com (while logged in)")
        logger.error("3. Click extension → Export cookies.txt")
        logger.error("4. Save to ~/Downloads/cookies.txt")
        return 1

    args.output.mkdir(parents=True, exist_ok=True)

    # Parse citation file
    logger.info(f"Parsing citation file: {args.input}")
    parser_obj = CochraneCitationParser()
    reviews = parser_obj.parse_export_file(args.input)

    if not reviews:
        logger.error("No reviews found")
        return 1

    if args.limit:
        logger.info(f"Limiting to first {args.limit} reviews (testing mode)")
        reviews = reviews[:args.limit]

    # Download
    downloader = CochraneCookieDownloader(args.output, args.cookies, delay=args.delay)
    stats = downloader.download_all(reviews)

    logger.info(f"\nFiles saved to: {args.output}")

    if stats['success'] > 0:
        logger.info(f"✓ SUCCESS: Downloaded {stats['success']} PDFs")

    return 0


if __name__ == '__main__':
    exit(main())
