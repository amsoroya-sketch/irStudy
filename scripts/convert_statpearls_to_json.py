#!/usr/bin/env python3
"""
Convert StatPearls .txt files to JSON format for chunking pipeline
"""

import json
import logging
from pathlib import Path
from tqdm import tqdm
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def convert_statpearls_txt_to_json(txt_file: Path) -> dict:
    """
    Convert a single StatPearls .txt file to JSON format

    Args:
        txt_file: Path to .txt file

    Returns:
        Dictionary in the format expected by chunker
    """
    # Read content
    with open(txt_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract title (first line after # marker)
    title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
    title = title_match.group(1) if title_match else txt_file.stem

    # Extract authors
    authors_match = re.search(r'\*\*Authors:\*\* (.+)$', content, re.MULTILINE)
    authors = authors_match.group(1) if authors_match else "Unknown"

    # Create JSON structure
    return {
        "filename": txt_file.name,
        "source_path": str(txt_file),
        "metadata": {
            "title": title,
            "author": authors,
            "source": "StatPearls"
        },
        "pages": [
            {
                "page_number": 1,  # Changed from 'page_num' to 'page_number'
                "text": content
            }
        ]
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Convert StatPearls .txt to JSON format")
    parser.add_argument("--input", default="data/processed/statpearls", help="Input directory with .txt files")
    parser.add_argument("--output", default="data/processed/statpearls_json", help="Output directory for JSON files")

    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all .txt files
    txt_files = list(input_dir.glob("*.txt"))

    if not txt_files:
        logger.error(f"No .txt files found in {input_dir}")
        return

    logger.info(f"Found {len(txt_files)} StatPearls articles to convert")

    success_count = 0
    failed_count = 0

    for txt_file in tqdm(txt_files, desc="Converting StatPearls"):
        try:
            # Convert
            json_data = convert_statpearls_txt_to_json(txt_file)

            # Save as JSON
            json_file = output_dir / f"{txt_file.stem}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)

            success_count += 1

        except Exception as e:
            logger.error(f"Failed to convert {txt_file.name}: {e}")
            failed_count += 1
            continue

    logger.info(f"\n✓ Conversion complete!")
    logger.info(f"  Successful: {success_count:,}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Output: {output_dir}")


if __name__ == "__main__":
    main()
