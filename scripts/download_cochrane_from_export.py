#!/usr/bin/env python3
"""
Download Cochrane PDFs from Citation Export File

Uses the DOI from citation export to construct PDF download URLs.
Pattern: https://www.cochranelibrary.com/cdsr/doi/{DOI}/pdf/full

Usage:
    python download_cochrane_from_export.py --input ~/Downloads/citation-export(2).txt --output ~/cochrane_downloads
"""

import argparse
import re
import time
import random
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
        # Pattern: https://www.cochranelibrary.com/cdsr/doi/10.1002/14651858.CD002137.pub3/pdf/CDSR/CD002137/CD002137.pdf
        if self.doi and self.record_id:
            return f"https://www.cochranelibrary.com/cdsr/doi/{self.doi}/pdf/CDSR/{self.record_id}/{self.record_id}.pdf"
        else:
            logger.warning(f"No DOI or record_id for {self.record_id}")
            return None

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

        # Split into individual records
        record_pattern = r'Record #\d+ of \d+\n(.*?)(?=Record #\d+ of \d+|\Z)'
        records = re.findall(record_pattern, content, re.DOTALL)

        logger.info(f"Found {len(records)} records in citation file")

        for i, record_text in enumerate(records, 1):
            try:
                review = CochraneCitationParser._parse_single_record(record_text)
                if review:
                    reviews.append(review)

                # Progress indicator
                if i % 100 == 0:
                    logger.info(f"  Parsed {i}/{len(records)} records...")

            except Exception as e:
                logger.warning(f"Failed to parse record {i}: {e}")
                continue

        logger.info(f"Successfully parsed {len(reviews)} Cochrane Reviews")
        return reviews

    @staticmethod
    def _parse_single_record(record_text: str) -> CochraneReview:
        """Parse a single record from citation export"""
        # Extract fields
        record_id_match = re.search(r'ID:\s*(\w+)', record_text)
        doi_match = re.search(r'DOI:\s*([\d\.\w\/]+)', record_text)
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


class CochranePDFDownloader:
    """Downloads Cochrane Review PDFs using wget"""

    def __init__(self, output_dir: Path, delay: float = 2.0):
        self.output_dir = output_dir
        self.delay = delay
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'access_denied': 0,
            'html_instead': 0,
            'skipped': 0
        }

    def download_review(self, review: CochraneReview) -> bool:
        """Download a single Cochrane Review PDF using wget"""

        output_path = self.output_dir / review.get_safe_filename()

        # Skip if already downloaded
        if output_path.exists():
            file_size = output_path.stat().st_size
            if file_size > 10000:  # At least 10KB
                logger.info(f"✓ Already exists: {review.record_id} ({file_size/1024:.1f} KB)")
                self.stats['skipped'] += 1
                return True

        pdf_url = review.get_pdf_url()
        if not pdf_url:
            self.stats['failed'] += 1
            return False

        logger.info(f"Downloading {review.record_id}: {review.title[:60]}...")
        logger.info(f"  URL: {pdf_url}")

        try:
            # Use wget to download PDF with realistic headers
            cmd = [
                'wget',
                '--quiet',
                '--timeout=60',
                '--tries=2',
                '--user-agent=Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
                '--header=Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                '--header=Accept-Language: en-US,en;q=0.5',
                '--header=DNT: 1',
                '--header=Connection: keep-alive',
                '--header=Upgrade-Insecure-Requests: 1',
                '-O', str(output_path),
                pdf_url
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=120)

            # Check if download was successful
            if result.returncode == 0 and output_path.exists():
                file_size = output_path.stat().st_size

                # Verify it's a real PDF (not HTML error page)
                if file_size > 10000:  # At least 10KB
                    # Check PDF header
                    with open(output_path, 'rb') as f:
                        header = f.read(4)
                        if header == b'%PDF':
                            logger.info(f"✓ Downloaded: {output_path.name} ({file_size/1024:.1f} KB)")
                            self.stats['success'] += 1
                            return True

                # Not a valid PDF
                logger.warning(f"✗ Downloaded file is not a PDF: {review.record_id}")
                output_path.unlink()  # Delete
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

    def download_all(self, reviews: List[CochraneReview], resume_from: int = 0) -> Dict[str, int]:
        """Download all reviews with progress tracking"""

        self.stats['total'] = len(reviews)

        logger.info(f"\n{'='*70}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Review PDFs")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"{'='*70}\n")

        start_time = time.time()

        for i, review in enumerate(reviews, 1):
            if i < resume_from:
                continue

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

            # Respectful delay with randomization to avoid CAPTCHA
            if i < len(reviews):
                # Random delay between delay and delay*2
                random_delay = self.delay + random.uniform(0, self.delay)
                time.sleep(random_delay)

        elapsed = time.time() - start_time

        logger.info(f"\n{'='*70}")
        logger.info(f"Download Complete!")
        logger.info(f"{'='*70}")
        logger.info(f"  Total reviews: {self.stats['total']}")
        logger.info(f"  ✓ Successfully downloaded: {self.stats['success']}")
        logger.info(f"  ⊘ Already existed (skipped): {self.stats['skipped']}")
        logger.info(f"  ⚠ HTML instead of PDF: {self.stats['html_instead']}")
        logger.info(f"  ✗ Access denied: {self.stats['access_denied']}")
        logger.info(f"  ✗ Other failures: {self.stats['failed']}")
        logger.info(f"  Total time: {elapsed/60:.1f} minutes")
        logger.info(f"{'='*70}\n")

        return self.stats


def main():
    parser = argparse.ArgumentParser(
        description='Download Cochrane Review PDFs from citation export file'
    )
    parser.add_argument(
        '--input',
        type=Path,
        required=True,
        help='Path to citation export file'
    )
    parser.add_argument(
        '--output',
        type=Path,
        default=Path.home() / 'cochrane_downloads',
        help='Output directory for PDFs'
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
    parser.add_argument(
        '--resume',
        type=int,
        default=0,
        help='Resume from review number N'
    )

    args = parser.parse_args()

    # Validate input file
    if not args.input.exists():
        logger.error(f"Citation file not found: {args.input}")
        return 1

    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)

    # Parse citation file
    logger.info(f"Parsing citation file: {args.input}")
    parser_obj = CochraneCitationParser()
    reviews = parser_obj.parse_export_file(args.input)

    if not reviews:
        logger.error("No reviews found in citation file")
        return 1

    # Apply limit if specified
    if args.limit:
        logger.info(f"Limiting to first {args.limit} reviews (testing mode)")
        reviews = reviews[:args.limit]

    # Download PDFs
    downloader = CochranePDFDownloader(args.output, delay=args.delay)
    stats = downloader.download_all(reviews, resume_from=args.resume)

    # Summary
    logger.info(f"\nFiles saved to: {args.output}")
    logger.info(f"Total PDF files: {stats['success']}")

    if stats['success'] > 0:
        logger.info(f"\n✓ SUCCESS: Downloaded {stats['success']} PDF files")

    if stats['access_denied'] > 0:
        logger.info(f"\n⚠ WARNING: {stats['access_denied']} files require subscription")
        logger.info("  Consider accessing through university/hospital network")

    return 0


if __name__ == '__main__':
    exit(main())
