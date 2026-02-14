#!/usr/bin/env python3
"""
Download Australian Clinical Guidelines
- RANZCOG: Obstetrics & Gynaecology statements and guidelines
- RANZCP: Psychiatry clinical practice guidelines
- NSW Health: Clinical protocols and policies

Usage:
    python download_australian_guidelines.py --output /mnt/data/medical_resources
"""

import argparse
import requests
import re
import time
from pathlib import Path
from typing import List, Dict
from bs4 import BeautifulSoup
import logging

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class AustralianGuidelinesDownloader:
    """Download Australian medical guidelines"""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
        })

        self.stats = {
            'ranzcog': {'success': 0, 'failed': 0},
            'ranzcp': {'success': 0, 'failed': 0},
            'nsw_health': {'success': 0, 'failed': 0}
        }

    def download_file(self, url: str, output_path: Path, description: str = "") -> bool:
        """Download a single file"""
        try:
            logger.info(f"Downloading: {description or url}")
            logger.info(f"  URL: {url}")

            response = self.session.get(url, timeout=60, allow_redirects=True)
            response.raise_for_status()

            # Check if it's actually a PDF
            content_type = response.headers.get('Content-Type', '')
            if 'pdf' in content_type or url.endswith('.pdf'):
                with open(output_path, 'wb') as f:
                    f.write(response.content)

                file_size = output_path.stat().st_size
                logger.info(f"  ✓ Downloaded: {output_path.name} ({file_size/1024:.1f} KB)")
                return True
            else:
                logger.warning(f"  ✗ Not a PDF: Content-Type = {content_type}")
                return False

        except Exception as e:
            logger.error(f"  ✗ Download failed: {e}")
            if output_path.exists():
                output_path.unlink()
            return False

    def download_ranzcog(self):
        """Download RANZCOG statements and guidelines"""
        logger.info("\n" + "="*70)
        logger.info("RANZCOG - Obstetrics & Gynaecology Guidelines")
        logger.info("="*70 + "\n")

        ranzcog_dir = self.output_dir / 'ranzcog'
        ranzcog_dir.mkdir(parents=True, exist_ok=True)

        # Known RANZCOG guidelines (these are direct PDF links)
        guidelines = [
            {
                'url': 'https://www.cosrh.org/Common/Uploaded%20files/documents/Contraception-Clinical-Guideline.pdf',
                'filename': 'contraception_clinical_guideline.pdf',
                'description': 'Contraception Clinical Guideline'
            },
            # Add more as we discover them from the directory
        ]

        # Try to scrape the statements directory
        try:
            logger.info("Fetching RANZCOG statements directory...")
            response = self.session.get('https://ranzcog.edu.au/resources/statements-and-guidelines-directory/')

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all PDF links
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))

                logger.info(f"Found {len(pdf_links)} PDF links on directory page")

                for link in pdf_links:
                    pdf_url = link.get('href')

                    # Make absolute URL
                    if pdf_url.startswith('/'):
                        pdf_url = f"https://ranzcog.edu.au{pdf_url}"
                    elif not pdf_url.startswith('http'):
                        pdf_url = f"https://ranzcog.edu.au/{pdf_url}"

                    # Get filename
                    filename = Path(pdf_url).name
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'

                    output_path = ranzcog_dir / filename

                    # Skip if already exists
                    if output_path.exists() and output_path.stat().st_size > 10000:
                        logger.info(f"✓ Already exists: {filename}")
                        self.stats['ranzcog']['success'] += 1
                        continue

                    # Download
                    if self.download_file(pdf_url, output_path, link.get_text(strip=True) or filename):
                        self.stats['ranzcog']['success'] += 1
                    else:
                        self.stats['ranzcog']['failed'] += 1

                    time.sleep(2)  # Be respectful

        except Exception as e:
            logger.error(f"Failed to fetch RANZCOG directory: {e}")

        # Also download the known contraception guideline
        for guideline in guidelines:
            output_path = ranzcog_dir / guideline['filename']

            if output_path.exists() and output_path.stat().st_size > 10000:
                logger.info(f"✓ Already exists: {guideline['filename']}")
                continue

            if self.download_file(guideline['url'], output_path, guideline['description']):
                self.stats['ranzcog']['success'] += 1
            else:
                self.stats['ranzcog']['failed'] += 1

    def download_ranzcp(self):
        """Download RANZCP clinical practice guidelines"""
        logger.info("\n" + "="*70)
        logger.info("RANZCP - Psychiatry Clinical Practice Guidelines")
        logger.info("="*70 + "\n")

        ranzcp_dir = self.output_dir / 'ranzcp'
        ranzcp_dir.mkdir(parents=True, exist_ok=True)

        # Known RANZCP guidelines
        guidelines = [
            {
                'url': 'https://www.ranzcp.org/getmedia/601ddc8c-cb96-4f4c-84e6-ca161e56ddc9/administration-of-rtms-2024.pdf',
                'filename': 'administration_of_rtms_2024.pdf',
                'description': 'Administration of rTMS - 2024'
            },
        ]

        # Try to scrape the clinical guidelines library
        try:
            logger.info("Fetching RANZCP clinical guidelines library...")
            response = self.session.get('https://www.ranzcp.org/clinical-guidelines-publications/clinical-guidelines-publications-library')

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Find all PDF links
                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$|/getmedia/', re.I))

                logger.info(f"Found {len(pdf_links)} potential PDF links")

                for link in pdf_links:
                    pdf_url = link.get('href')

                    # Make absolute URL
                    if pdf_url.startswith('/'):
                        pdf_url = f"https://www.ranzcp.org{pdf_url}"
                    elif not pdf_url.startswith('http'):
                        pdf_url = f"https://www.ranzcp.org/{pdf_url}"

                    # Get filename
                    filename = Path(pdf_url).name
                    if not filename.endswith('.pdf'):
                        filename += '.pdf'

                    # Clean filename
                    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)

                    output_path = ranzcp_dir / filename

                    # Skip if already exists
                    if output_path.exists() and output_path.stat().st_size > 10000:
                        logger.info(f"✓ Already exists: {filename}")
                        self.stats['ranzcp']['success'] += 1
                        continue

                    # Download
                    if self.download_file(pdf_url, output_path, link.get_text(strip=True) or filename):
                        self.stats['ranzcp']['success'] += 1
                    else:
                        self.stats['ranzcp']['failed'] += 1

                    time.sleep(2)  # Be respectful

        except Exception as e:
            logger.error(f"Failed to fetch RANZCP library: {e}")

        # Download known guidelines
        for guideline in guidelines:
            output_path = ranzcp_dir / guideline['filename']

            if output_path.exists() and output_path.stat().st_size > 10000:
                logger.info(f"✓ Already exists: {guideline['filename']}")
                continue

            if self.download_file(guideline['url'], output_path, guideline['description']):
                self.stats['ranzcp']['success'] += 1
            else:
                self.stats['ranzcp']['failed'] += 1

    def download_nsw_health(self):
        """Download NSW Health clinical protocols"""
        logger.info("\n" + "="*70)
        logger.info("NSW Health - Clinical Protocols and Policies")
        logger.info("="*70 + "\n")

        nsw_dir = self.output_dir / 'nsw_health'
        nsw_dir.mkdir(parents=True, exist_ok=True)

        # NSW Health Policy and Procedure Manual chapters
        chapters = [
            {'num': '1', 'name': 'general'},
            {'num': '2', 'name': 'workforce'},
            {'num': '3', 'name': 'clinical_governance'},
            {'num': '4', 'name': 'patient_safety'},
            {'num': '5', 'name': 'infection_control'},
            {'num': '6', 'name': 'medication'},
            {'num': '7', 'name': 'surgery'},
            {'num': '8', 'name': 'maternity'},
            {'num': '9', 'name': 'paediatrics'},
            {'num': '10', 'name': 'emergency'},
            {'num': '11', 'name': 'critical_care'},
            {'num': '12', 'name': 'rehabilitation'},
            {'num': '13', 'name': 'mental_health'},
            {'num': '14', 'name': 'aged_care'},
            {'num': '15', 'name': 'community'},
            {'num': 'index', 'name': 'index'},
        ]

        # Download manual chapters
        for chapter in chapters:
            url = f"https://www.health.nsw.gov.au/policies/manuals/Documents/pmm-{chapter['num']}.pdf"
            filename = f"policy_procedure_manual_chapter_{chapter['num']}_{chapter['name']}.pdf"
            output_path = nsw_dir / filename

            if output_path.exists() and output_path.stat().st_size > 10000:
                logger.info(f"✓ Already exists: {filename}")
                self.stats['nsw_health']['success'] += 1
                continue

            if self.download_file(url, output_path, f"Chapter {chapter['num']}: {chapter['name'].title()}"):
                self.stats['nsw_health']['success'] += 1
            else:
                self.stats['nsw_health']['failed'] += 1

            time.sleep(1.5)

    def download_all(self):
        """Download all Australian guidelines"""
        logger.info("\n" + "="*70)
        logger.info("Australian Clinical Guidelines Downloader")
        logger.info("="*70)
        logger.info(f"Output directory: {self.output_dir}")
        logger.info("="*70 + "\n")

        start_time = time.time()

        # Download each collection
        self.download_ranzcog()
        self.download_ranzcp()
        self.download_nsw_health()

        elapsed = time.time() - start_time

        # Summary
        logger.info("\n" + "="*70)
        logger.info("DOWNLOAD SUMMARY")
        logger.info("="*70)
        logger.info(f"\nRANZCOG (Obstetrics & Gynaecology):")
        logger.info(f"  ✓ Success: {self.stats['ranzcog']['success']}")
        logger.info(f"  ✗ Failed: {self.stats['ranzcog']['failed']}")

        logger.info(f"\nRANZCP (Psychiatry):")
        logger.info(f"  ✓ Success: {self.stats['ranzcp']['success']}")
        logger.info(f"  ✗ Failed: {self.stats['ranzcp']['failed']}")

        logger.info(f"\nNSW Health (Clinical Protocols):")
        logger.info(f"  ✓ Success: {self.stats['nsw_health']['success']}")
        logger.info(f"  ✗ Failed: {self.stats['nsw_health']['failed']}")

        total_success = sum(s['success'] for s in self.stats.values())
        total_failed = sum(s['failed'] for s in self.stats.values())

        logger.info(f"\nTOTAL:")
        logger.info(f"  ✓ Success: {total_success}")
        logger.info(f"  ✗ Failed: {total_failed}")
        logger.info(f"  Time elapsed: {elapsed/60:.1f} minutes")
        logger.info("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Download Australian clinical guidelines (RANZCOG, RANZCP, NSW Health)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        default=Path('/mnt/data/medical_resources'),
        help='Output directory (default: /mnt/data/medical_resources)'
    )

    args = parser.parse_args()

    # Download
    downloader = AustralianGuidelinesDownloader(args.output)
    downloader.download_all()


if __name__ == '__main__':
    main()
