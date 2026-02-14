#!/usr/bin/env python3
"""
Download MedPix cases via web scraping

Note: MedPix doesn't have a public REST API, so this uses
respectful web scraping with rate limiting.

Usage:
    python3 download_medpix_api.py

Requirements:
    pip3 install requests beautifulsoup4 tqdm
"""

import requests
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path
import time
import getpass
from tqdm import tqdm

class MedPixDownloader:
    """
    Download MedPix cases via web scraping (respectful rate limiting)
    """

    def __init__(self, username, password):
        self.base_url = "https://medpix.nlm.nih.gov"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Educational Research Bot)'
        })
        self.login(username, password)

    def login(self, username, password):
        """Login to MedPix"""
        login_url = f"{self.base_url}/login"
        payload = {
            'username': username,
            'password': password
        }

        try:
            response = self.session.post(login_url, data=payload)
            if response.status_code == 200 and 'logout' in response.text.lower():
                print("✓ Logged in to MedPix")
            else:
                raise Exception("Login failed - check credentials")
        except Exception as e:
            raise Exception(f"Login error: {e}")

    def search_cases(self, query, max_results=20):
        """Search for cases by keyword"""
        search_url = f"{self.base_url}/search"
        params = {
            'query': query,
            'limit': max_results
        }

        try:
            response = self.session.get(search_url, params=params)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Parse case IDs from search results
            case_ids = []
            for link in soup.find_all('a', href=True):
                if '/case/' in link['href']:
                    case_id = link['href'].split('/case/')[-1].split('/')[0].split('?')[0]
                    if case_id.isdigit() and case_id not in case_ids:
                        case_ids.append(case_id)

            print(f"  Found {len(case_ids)} cases for '{query}'")
            return case_ids[:max_results]

        except Exception as e:
            print(f"  Search error: {e}")
            return []

    def download_case(self, case_id, output_dir):
        """Download a single case with metadata"""
        case_url = f"{self.base_url}/case/{case_id}"

        try:
            response = self.session.get(case_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract metadata
            metadata = {
                'case_id': case_id,
                'title': soup.find('h1').text.strip() if soup.find('h1') else 'Unknown',
                'diagnosis': self._extract_field(soup, 'Diagnosis'),
                'modality': self._extract_field(soup, 'Modality'),
                'patient_age': self._extract_field(soup, 'Age'),
                'patient_sex': self._extract_field(soup, 'Sex'),
                'clinical_history': self._extract_field(soup, 'History'),
                'findings': self._extract_field(soup, 'Findings'),
                'citation': f"(MedPix Case #{case_id}, Public Domain, accessed 2026-02-03)",
                'source': 'medpix',
                'license': 'Public Domain',
                'source_url': case_url
            }

            # Download images
            image_urls = []
            for img in soup.find_all('img'):
                src = img.get('src', '')
                if 'case_images' in src or 'images' in src:
                    if not src.startswith('http'):
                        src = self.base_url + src
                    image_urls.append(src)

            # Save images
            case_dir = Path(output_dir) / f"case_{case_id}"
            case_dir.mkdir(parents=True, exist_ok=True)

            downloaded_images = []
            for i, img_url in enumerate(image_urls[:5]):  # Limit to 5 images per case
                try:
                    img_response = self.session.get(img_url, timeout=10)
                    if img_response.status_code == 200:
                        img_path = case_dir / f"image_{i+1}.jpg"
                        with open(img_path, 'wb') as f:
                            f.write(img_response.content)
                        downloaded_images.append(str(img_path))
                except Exception as e:
                    print(f"    Image download error: {e}")

            metadata['images'] = downloaded_images
            metadata['image_count'] = len(downloaded_images)

            # Save metadata
            metadata_path = case_dir / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)

            return metadata

        except Exception as e:
            print(f"  Case download error: {e}")
            return None

    def _extract_field(self, soup, field_name):
        """Extract metadata field from case page"""
        # Try multiple patterns
        patterns = [
            lambda: soup.find(text=lambda t: t and field_name in t),
            lambda: soup.find('dt', text=lambda t: t and field_name in t),
            lambda: soup.find('label', text=lambda t: t and field_name in t)
        ]

        for pattern in patterns:
            try:
                field_elem = pattern()
                if field_elem:
                    parent = field_elem.parent
                    # Look for next sibling or dd element
                    value = parent.find_next_sibling() or parent.find_next('dd')
                    if value:
                        return value.text.strip()
            except:
                continue

        return None

def main():
    """Main download workflow"""

    print("=================================")
    print("MedPix Dataset Downloader")
    print("=================================\n")

    # Get credentials
    print("Enter MedPix credentials:")
    username = input("Username: ")
    password = getpass.getpass("Password: ")
    print()

    # Initialize downloader
    try:
        downloader = MedPixDownloader(username, password)
    except Exception as e:
        print(f"✗ Login failed: {e}")
        return

    # Define search queries for AMC exam topics
    specialties = {
        'cardiology': [
            'myocardial infarction',
            'heart failure',
            'atrial fibrillation'
        ],
        'dermatology': [
            'melanoma',
            'psoriasis',
            'eczema',
            'basal cell carcinoma'
        ],
        'pulmonology': [
            'pneumonia',
            'pulmonary embolism',
            'COPD',
            'asthma'
        ],
        'neurology': [
            'stroke',
            'seizure',
            'meningitis'
        ],
        'emergency': [
            'trauma',
            'acute abdomen',
            'fracture'
        ]
    }

    output_base = Path('data/medical_images/medpix')
    output_base.mkdir(parents=True, exist_ok=True)

    total_cases = 0
    all_metadata = []

    # Download cases by specialty
    for specialty, queries in specialties.items():
        print(f"\n{'='*50}")
        print(f"Downloading {specialty.upper()} cases")
        print(f"{'='*50}\n")

        output_dir = output_base / specialty
        output_dir.mkdir(exist_ok=True)

        for query in queries:
            print(f"Searching: {query}")
            case_ids = downloader.search_cases(query, max_results=7)

            for case_id in tqdm(case_ids, desc=f"  Downloading"):
                metadata = downloader.download_case(case_id, output_dir)
                if metadata:
                    all_metadata.append(metadata)
                    total_cases += 1

                # Rate limiting (be respectful to server)
                time.sleep(2)

            # Extra delay between queries
            time.sleep(3)

    # Save combined metadata
    combined_metadata_path = output_base / 'all_cases_metadata.json'
    with open(combined_metadata_path, 'w') as f:
        json.dump(all_metadata, f, indent=2)

    print(f"\n{'='*50}")
    print("Download Complete!")
    print(f"{'='*50}")
    print(f"Total cases downloaded: {total_cases}")
    print(f"Output directory: {output_base}")
    print(f"Metadata file: {combined_metadata_path}")
    print(f"\nNext step: python3 scripts/process_image_metadata.py")

if __name__ == '__main__':
    main()
