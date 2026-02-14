#!/usr/bin/env python3
"""
StatPearls Medical Database Downloader
Downloads free medical articles from NCBI StatPearls collection

Requirements:
- NCBI E-utilities API key (free): https://www.ncbi.nlm.nih.gov/account/settings/
- Set environment variable: export NCBI_API_KEY='your_key_here'

Usage:
    python download_statpearls.py --output /path/to/output/directory
"""

import os
import sys
import time
import argparse
import requests
from pathlib import Path
from typing import List, Dict
import xml.etree.ElementTree as ET
from tqdm import tqdm
import json

# NCBI E-utilities base URLs
ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
EFETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
ELINK_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"

# Rate limiting (NCBI allows 3 requests/second without API key, 10/second with key)
RATE_LIMIT_DELAY = 0.1  # 100ms between requests (with API key)


class StatPearlsDownloader:
    """Download StatPearls medical articles from NCBI Bookshelf"""

    def __init__(self, api_key: str = None, output_dir: str = "statpearls"):
        self.api_key = api_key or os.getenv("NCBI_API_KEY")
        if not self.api_key:
            print("WARNING: No NCBI API key found. Rate limited to 3 requests/second.")
            print("Get a free API key at: https://www.ncbi.nlm.nih.gov/account/settings/")
            self.rate_limit_delay = 0.34  # 3 requests/second
        else:
            self.rate_limit_delay = RATE_LIMIT_DELAY

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.output_dir / "metadata.json"
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict:
        """Load existing download metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"downloaded": [], "failed": [], "total": 0}

    def _save_metadata(self):
        """Save download metadata"""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _api_request(self, url: str, params: Dict) -> requests.Response:
        """Make API request with rate limiting"""
        if self.api_key:
            params['api_key'] = self.api_key

        time.sleep(self.rate_limit_delay)  # Rate limiting
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response

    def search_statpearls_books(self) -> List[str]:
        """
        Search for all StatPearls articles in PubMed.

        Note: StatPearls full-text is NOT available via NCBI API.
        We can only download abstracts + metadata + section outlines.

        Returns:
            List of PubMed IDs
        """
        print("Searching for StatPearls articles...")

        params = {
            'db': 'pubmed',  # Changed from 'books' to 'pubmed'
            'term': 'StatPearls[Book]',
            'retmax': 10000,  # Maximum results
            'retmode': 'xml'
        }

        response = self._api_request(ESEARCH_URL, params)
        root = ET.fromstring(response.content)

        # Extract article IDs
        id_list = root.find('IdList')
        if id_list is None:
            print("ERROR: No articles found")
            return []

        article_ids = [id_elem.text for id_elem in id_list.findall('Id')]
        print(f"Found {len(article_ids)} StatPearls articles")

        return article_ids

    def download_book(self, article_id: str) -> bool:
        """
        Download a single StatPearls article from PubMed.

        Note: Only downloads abstract + metadata + section outlines.
        Full-text is NOT available via NCBI API.

        Args:
            article_id: PubMed article ID

        Returns:
            True if successful, False otherwise
        """
        # Check if already downloaded
        if article_id in self.metadata['downloaded']:
            # Skip silently (already downloaded)
            return True

        try:
            # Fetch article content from PubMed
            params = {
                'db': 'pubmed',  # Changed from 'books'
                'id': article_id,
                'retmode': 'xml'
            }

            response = self._api_request(EFETCH_URL, params)

            # Parse XML to get title
            root = ET.fromstring(response.content)
            title_elem = root.find('.//ArticleTitle')
            title = title_elem.text if title_elem is not None else f"Article_{article_id}"

            # Clean title for filename
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title.replace(' ', '_')[:100]  # Limit length

            # Save XML content
            xml_file = self.output_dir / f"{safe_title}_{article_id}.xml"
            with open(xml_file, 'wb') as f:
                f.write(response.content)

            # Also save as text for easier processing
            text_content = self._extract_text_from_xml(root)
            text_file = self.output_dir / f"{safe_title}_{article_id}.txt"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(text_content)

            self.metadata['downloaded'].append(article_id)
            self._save_metadata()

            return True

        except Exception as e:
            print(f"  ERROR downloading {article_id}: {e}")
            self.metadata['failed'].append({'id': article_id, 'error': str(e)})
            self._save_metadata()
            return False

    def _extract_text_from_xml(self, root: ET.Element) -> str:
        """
        Extract readable text from PubMed XML.

        Note: StatPearls full-text is NOT available via NCBI API.
        This extracts: title, authors, abstract, section outlines, references.
        """
        text_parts = []

        # Extract article title
        title = root.find('.//ArticleTitle')
        if title is not None and title.text:
            text_parts.append(f"# {title.text}\n\n")

        # Extract authors
        authors = []
        for author in root.findall('.//Author'):
            lastname = author.find('LastName')
            forename = author.find('ForeName')
            if lastname is not None:
                name = lastname.text
                if forename is not None:
                    name = f"{forename.text} {name}"
                authors.append(name)

        if authors:
            text_parts.append(f"**Authors:** {', '.join(authors)}\n\n")

        # Extract book info
        book_title = root.find('.//BookTitle')
        publisher = root.find('.//PublisherName')
        if book_title is not None or publisher is not None:
            text_parts.append(f"**Source:** {book_title.text if book_title is not None else 'StatPearls'}")
            if publisher is not None:
                text_parts.append(f" - {publisher.text}")
            text_parts.append("\n\n")

        # Extract abstract
        abstract = root.find('.//Abstract/AbstractText')
        if abstract is not None:
            abstract_text = ''.join(abstract.itertext())
            if abstract_text.strip():
                text_parts.append(f"## Abstract\n\n{abstract_text.strip()}\n\n")

        # Extract section outline (titles only, no body text available)
        sections = root.find('.//Sections')
        if sections is not None:
            section_titles = []
            for section in sections.findall('.//Section'):
                sec_title = section.find('.//SectionTitle')
                if sec_title is not None and sec_title.text:
                    section_titles.append(sec_title.text)

            if section_titles:
                text_parts.append("## Section Outline\n\n")
                text_parts.append("NOTE: Full-text is not available via NCBI API. Only section titles are shown below.\n\n")
                for i, sec in enumerate(section_titles, 1):
                    text_parts.append(f"{i}. {sec}\n")
                text_parts.append("\n")

        # Extract references
        references = root.findall('.//Reference/Citation')
        if references:
            text_parts.append("## References\n\n")
            for i, ref in enumerate(references, 1):
                ref_text = ''.join(ref.itertext()).strip()
                if ref_text:
                    text_parts.append(f"{i}. {ref_text}\n")
            text_parts.append("\n")

        return ''.join(text_parts)

    def download_all(self):
        """Download all StatPearls books"""
        book_ids = self.search_statpearls_books()

        if not book_ids:
            print("No books found to download")
            return

        self.metadata['total'] = len(book_ids)
        self._save_metadata()

        print(f"\nDownloading {len(book_ids)} books...")
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Rate limit: {1/self.rate_limit_delay:.1f} requests/second")
        print()

        # Filter out already downloaded
        remaining = [bid for bid in book_ids if bid not in self.metadata['downloaded']]
        print(f"Already downloaded: {len(book_ids) - len(remaining)}")
        print(f"Remaining: {len(remaining)}")
        print()

        # Download with progress bar
        for book_id in tqdm(remaining, desc="Downloading books"):
            self.download_book(book_id)

        # Summary
        print("\n" + "="*50)
        print("DOWNLOAD SUMMARY")
        print("="*50)
        print(f"Total books: {self.metadata['total']}")
        print(f"Downloaded: {len(self.metadata['downloaded'])}")
        print(f"Failed: {len(self.metadata['failed'])}")
        print(f"Success rate: {len(self.metadata['downloaded'])/self.metadata['total']*100:.1f}%")
        print()
        print(f"Output directory: {self.output_dir.absolute()}")
        print(f"Metadata file: {self.metadata_file.absolute()}")
        print("="*50)

        if self.metadata['failed']:
            print("\nFailed downloads:")
            for fail in self.metadata['failed']:
                print(f"  - {fail['id']}: {fail['error']}")


def main():
    parser = argparse.ArgumentParser(
        description="Download StatPearls medical database from NCBI Bookshelf",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download to default directory (statpearls/)
    python download_statpearls.py

    # Download to custom directory
    python download_statpearls.py --output /mnt/external/medical_resources/statpearls

    # Set API key via environment variable (recommended)
    export NCBI_API_KEY='your_key_here'
    python download_statpearls.py --output /path/to/output

    # Or pass API key directly (not recommended for security)
    python download_statpearls.py --api-key YOUR_KEY --output /path/to/output

Get your free NCBI API key:
    https://www.ncbi.nlm.nih.gov/account/settings/
        """
    )

    parser.add_argument(
        '--output', '-o',
        type=str,
        default='statpearls',
        help='Output directory for downloaded books (default: statpearls/)'
    )

    parser.add_argument(
        '--api-key', '-k',
        type=str,
        help='NCBI E-utilities API key (or set NCBI_API_KEY environment variable)'
    )

    args = parser.parse_args()

    # Initialize downloader
    downloader = StatPearlsDownloader(
        api_key=args.api_key,
        output_dir=args.output
    )

    # Download all books
    downloader.download_all()


if __name__ == "__main__":
    main()
