#!/usr/bin/env python3
"""
Download Cochrane PDFs using Playwright with Firefox

Uses Playwright to automate Firefox and download PDFs.
Can connect to existing Firefox session if cookies are available.

Usage:
    python download_cochrane_playwright.py --input ~/Downloads/citation-export(2).txt --output ~/cochrane_downloads --limit 10
"""

import argparse
import re
import time
import asyncio
import logging
from pathlib import Path
from typing import List, Dict
from playwright.async_api import async_playwright, Browser, Page

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


class CochranePlaywrightDownloader:
    """Downloads Cochrane PDFs using Playwright"""

    def __init__(self, output_dir: Path, headless: bool = False):
        self.output_dir = output_dir
        self.headless = headless
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'skipped': 0
        }

    async def download_all(self, reviews: List[CochraneReview]) -> Dict[str, int]:
        """Download all reviews using Playwright"""

        self.stats['total'] = len(reviews)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"\n{'='*70}")
        logger.info(f"Starting download of {len(reviews)} Cochrane Review PDFs")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Using Playwright with Firefox")
        logger.info(f"{'='*70}\n")

        async with async_playwright() as p:
            # Launch Firefox
            logger.info("Launching Firefox browser...")
            browser = await p.firefox.launch(headless=self.headless)

            # Create a new context with downloads enabled
            context = await browser.new_context(
                accept_downloads=True,
                viewport={'width': 1920, 'height': 1080}
            )

            page = await context.new_page()

            # Set up download handling
            downloads = []

            async def handle_download(download):
                downloads.append(download)

            start_time = time.time()

            for i, review in enumerate(reviews, 1):
                logger.info(f"[{i}/{len(reviews)}] Processing {review.record_id}...")

                success = await self._download_review(page, review)

                if success:
                    self.stats['success'] += 1
                else:
                    self.stats['failed'] += 1

                # Progress update every 25 downloads
                if i % 25 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / i
                    remaining = (len(reviews) - i) * avg_time

                    logger.info(f"\n--- Progress Update ---")
                    logger.info(f"  Processed: {i}/{len(reviews)} ({i/len(reviews)*100:.1f}%)")
                    logger.info(f"  Success: {self.stats['success']}, Failed: {self.stats['failed']}")
                    logger.info(f"  Time elapsed: {elapsed/60:.1f} min")
                    logger.info(f"  Estimated remaining: {remaining/60:.1f} min")
                    logger.info(f"-----------------------\n")

                # Small delay
                await asyncio.sleep(1.5)

            await browser.close()

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

    async def _download_review(self, page: Page, review: CochraneReview) -> bool:
        """Download a single review PDF"""

        output_path = self.output_dir / review.get_safe_filename()

        # Skip if already exists
        if output_path.exists() and output_path.stat().st_size > 10000:
            logger.info(f"✓ Already exists: {review.record_id}")
            self.stats['skipped'] += 1
            return True

        pdf_url = review.get_pdf_url()
        if not pdf_url:
            logger.warning(f"✗ No DOI for {review.record_id}")
            return False

        logger.info(f"  URL: {pdf_url}")

        try:
            # Set up download handler
            downloads_list = []

            async def handle_download(download):
                await download.save_as(output_path)
                downloads_list.append(download)

            page.on("download", handle_download)

            # Navigate to PDF URL - this should trigger download
            logger.info(f"  Opening PDF URL...")
            try:
                await page.goto(pdf_url, timeout=20000, wait_until='commit')
            except Exception as nav_error:
                # Download might have started immediately
                if "Download is starting" in str(nav_error):
                    logger.info(f"  Download triggered...")
                else:
                    logger.warning(f"✗ Navigation failed: {nav_error}")
                    return False

            # Wait for download to complete
            await asyncio.sleep(8)

            # Check if PDF was downloaded
            if output_path.exists() and output_path.stat().st_size > 10000:
                # Verify it's a PDF
                with open(output_path, 'rb') as f:
                    header = f.read(4)
                    if header == b'%PDF':
                        file_size = output_path.stat().st_size / 1024
                        logger.info(f"✓ Downloaded: {output_path.name} ({file_size:.1f} KB)")
                        return True

                logger.warning(f"✗ Not a valid PDF: {review.record_id}")
                output_path.unlink()
                return False
            else:
                logger.warning(f"✗ Download failed or file too small: {review.record_id}")
                return False

        except Exception as e:
            logger.error(f"✗ Download failed: {review.record_id} - {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Download Cochrane PDFs using Playwright + Firefox'
    )
    parser.add_argument('--input', type=Path, required=True, help='Citation export file')
    parser.add_argument('--output', type=Path, default=Path.home() / 'cochrane_downloads', help='Output directory')
    parser.add_argument('--limit', type=int, help='Limit number of downloads')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--resume', type=int, default=0, help='Resume from review number N')

    args = parser.parse_args()

    if not args.input.exists():
        logger.error(f"Citation file not found: {args.input}")
        return 1

    # Parse citation file
    logger.info(f"Parsing citation file: {args.input}")
    parser_obj = CochraneCitationParser()
    reviews = parser_obj.parse_export_file(args.input)

    if not reviews:
        logger.error("No reviews found")
        return 1

    # Apply limit
    if args.limit:
        logger.info(f"Limiting to first {args.limit} reviews (testing mode)")
        reviews = reviews[:args.limit]

    if args.resume > 0:
        logger.info(f"Resuming from review #{args.resume}")
        reviews = reviews[args.resume-1:]

    # Download
    downloader = CochranePlaywrightDownloader(args.output, headless=args.headless)
    stats = asyncio.run(downloader.download_all(reviews))

    logger.info(f"\nFiles saved to: {args.output}")

    if stats['success'] > 0:
        logger.info(f"✓ SUCCESS: Downloaded {stats['success']} PDFs")

    return 0


if __name__ == '__main__':
    exit(main())
