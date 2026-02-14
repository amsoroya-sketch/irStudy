#!/usr/bin/env python3
"""
Download Medical Images from HEAL using Taxonomy
Supports parallel downloads across multiple specialties
"""

import json
import asyncio
import aiohttp
import argparse
from pathlib import Path
from typing import List, Dict
import time
from urllib.parse import quote_plus

class HEALImageDownloader:
    """Download images from HEAL based on taxonomy search terms"""
    
    HEAL_SEARCH_URL = "https://library.med.utah.edu/heal/search"
    HEAL_IMAGE_BASE = "https://library.med.utah.edu/heal/image"
    
    def __init__(self, taxonomy_file: str, output_dir: str = "data/medical_images", 
                 rate_limit: float = 2.0, max_per_node: int = 5):
        self.taxonomy_file = Path(taxonomy_file)
        self.output_dir = Path(output_dir)
        self.rate_limit = rate_limit  # seconds between requests
        self.max_per_node = max_per_node
        self.session = None
        self.downloaded_count = 0
        self.failed_count = 0
        
    async def init_session(self):
        """Initialize aiohttp session"""
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'AMC-Medical-Education/1.0'}
        )
    
    async def close_session(self):
        """Close aiohttp session"""
        if self.session:
            await self.session.close()
    
    def load_taxonomy(self) -> Dict:
        """Load taxonomy from JSON file"""
        with open(self.taxonomy_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['taxonomy']
    
    def get_all_nodes(self, specialties: List[str] = None) -> List[Dict]:
        """Extract all image nodes from taxonomy"""
        taxonomy = self.load_taxonomy()
        nodes = []
        
        for spec_name, spec_data in taxonomy.items():
            if specialties and spec_name not in specialties:
                continue
                
            for subcat_name, subcat_data in spec_data['subcategories'].items():
                for topic_name, topic_data in subcat_data['topics'].items():
                    for subtopic_name, subtopic_data in topic_data['subtopics'].items():
                        node = {
                            'specialty': spec_name,
                            'subcategory': subcat_name,
                            'topic': topic_name,
                            'subtopic': subtopic_name,
                            'search_terms': subtopic_data['search_terms'],
                            'image_types': subtopic_data['image_types'],
                            'amc_relevance': subtopic_data['amc_relevance'],
                            'folder_path': subtopic_data['folder_path']
                        }
                        nodes.append(node)
        
        return nodes
    
    async def search_heal(self, search_term: str) -> List[str]:
        """
        Search HEAL for images (placeholder - requires actual HEAL API integration)
        
        NOTE: This is a template. Actual HEAL integration requires:
        1. HEAL API key/authentication
        2. Proper API endpoint discovery
        3. Image URL extraction from search results
        """
        # Placeholder - returns empty list
        # In production, this would make actual API calls to HEAL
        await asyncio.sleep(self.rate_limit)  # Rate limiting
        return []
    
    async def download_image(self, image_url: str, output_path: Path) -> bool:
        """Download single image"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            async with self.session.get(image_url) as response:
                if response.status == 200:
                    content = await response.read()
                    with open(output_path, 'wb') as f:
                        f.write(content)
                    self.downloaded_count += 1
                    return True
                else:
                    self.failed_count += 1
                    return False
        except Exception as e:
            print(f"Error downloading {image_url}: {e}")
            self.failed_count += 1
            return False
    
    async def process_node(self, node: Dict) -> int:
        """Process single taxonomy node - search and download images"""
        print(f"Processing: {node['specialty']}/{node['subtopic']} (AMC: {node['amc_relevance']}/5)")
        
        images_downloaded = 0
        
        # Try each search term
        for search_term in node['search_terms']:
            if images_downloaded >= self.max_per_node:
                break
            
            # Search HEAL
            image_urls = await self.search_heal(search_term)
            
            # Download images
            for i, url in enumerate(image_urls):
                if images_downloaded >= self.max_per_node:
                    break
                
                # Create output path
                filename = f"{node['subtopic']}_{i+1}.jpg"
                output_path = self.output_dir / node['folder_path'] / filename
                
                success = await self.download_image(url, output_path)
                if success:
                    images_downloaded += 1
        
        return images_downloaded
    
    async def download_parallel(self, specialties: List[str] = None, 
                               max_concurrent: int = 5):
        """Download images for all nodes in parallel"""
        await self.init_session()
        
        # Get all nodes to process
        nodes = self.get_all_nodes(specialties)
        
        print(f"\nStarting parallel downloads:")
        print(f"  Nodes to process: {len(nodes)}")
        print(f"  Max images per node: {self.max_per_node}")
        print(f"  Max concurrent downloads: {max_concurrent}")
        print(f"  Rate limit: {self.rate_limit}s between requests\n")
        
        # Process nodes in batches
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def bounded_process(node):
            async with semaphore:
                return await self.process_node(node)
        
        tasks = [bounded_process(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        await self.close_session()
        
        # Report results
        total_images = sum(r for r in results if isinstance(r, int))
        print(f"\n{'='*60}")
        print(f"Download Complete:")
        print(f"  Nodes processed: {len(nodes)}")
        print(f"  Images downloaded: {self.downloaded_count}")
        print(f"  Failed downloads: {self.failed_count}")
        print(f"{'='*60}")
    
    def generate_download_commands(self, specialties: List[str] = None, 
                                  output_file: str = "download_commands.sh"):
        """Generate shell script with wget/curl commands for manual download"""
        nodes = self.get_all_nodes(specialties)
        
        with open(output_file, 'w') as f:
            f.write("#!/bin/bash\n")
            f.write("# HEAL Image Download Commands\n")
            f.write("# Generated from medical_image_taxonomy_v1.json\n\n")
            
            for node in nodes:
                f.write(f"# {node['specialty']}/{node['subtopic']}\n")
                f.write(f"# AMC Relevance: {node['amc_relevance']}/5\n")
                f.write(f"mkdir -p {self.output_dir / node['folder_path']}\n")
                
                for i, term in enumerate(node['search_terms']):
                    f.write(f"# Search term {i+1}: {term}\n")
                    # Placeholder - would generate actual HEAL URLs
                    encoded_term = quote_plus(term)
                    f.write(f"# wget \"https://library.med.utah.edu/heal/search?q={encoded_term}\"\n")
                
                f.write("\n")
        
        print(f"✅ Generated download commands: {output_file}")
        print(f"   Total nodes: {len(nodes)}")


def main():
    parser = argparse.ArgumentParser(
        description='Download medical images from HEAL using taxonomy'
    )
    parser.add_argument(
        '--taxonomy',
        default='data/medical_image_taxonomy_v1.json',
        help='Path to taxonomy JSON file'
    )
    parser.add_argument(
        '--output',
        default='data/medical_images',
        help='Output directory for images'
    )
    parser.add_argument(
        '--specialties',
        nargs='+',
        help='Specific specialties to download (e.g., cardiology respiratory)'
    )
    parser.add_argument(
        '--max-per-node',
        type=int,
        default=5,
        help='Maximum images to download per node'
    )
    parser.add_argument(
        '--rate-limit',
        type=float,
        default=2.0,
        help='Seconds between requests'
    )
    parser.add_argument(
        '--max-concurrent',
        type=int,
        default=5,
        help='Maximum concurrent downloads'
    )
    parser.add_argument(
        '--generate-commands',
        action='store_true',
        help='Generate shell script with download commands instead of downloading'
    )
    
    args = parser.parse_args()
    
    downloader = HEALImageDownloader(
        taxonomy_file=args.taxonomy,
        output_dir=args.output,
        rate_limit=args.rate_limit,
        max_per_node=args.max_per_node
    )
    
    if args.generate_commands:
        # Generate download commands
        downloader.generate_download_commands(
            specialties=args.specialties,
            output_file='heal_download_commands.sh'
        )
    else:
        # Run parallel downloads
        asyncio.run(downloader.download_parallel(
            specialties=args.specialties,
            max_concurrent=args.max_concurrent
        ))


if __name__ == '__main__':
    main()
