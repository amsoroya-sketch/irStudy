#!/usr/bin/env python3
"""
HuggingFace Medical Datasets Download Script
Downloads free medical education datasets as alternative to purchasing textbooks

Usage:
    python scripts/download_huggingface_datasets.py --all
    python scripts/download_huggingface_datasets.py --dataset medmcqa
    python scripts/download_huggingface_datasets.py --priority-only
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
import argparse
from datasets import load_dataset
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Base directory
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data" / "huggingface_datasets"

# Dataset configurations
DATASETS = {
    # Priority 1: Essential datasets
    "medrag_textbooks": {
        "hf_name": "MedRAG/textbooks",
        "priority": 1,
        "size": "~50MB",
        "description": "126k chunks from 18 medical textbooks (USMLE)",
        "use_case": "Knowledge base for RAG",
        "license": "Check repository"
    },
    "usmle_questions": {
        "hf_name": "GBaker/MedQA-USMLE-4-options",
        "priority": 1,
        "size": "~10MB",
        "description": "11.5k USMLE exam questions (Steps 1, 2, 3)",
        "use_case": "Clinical reasoning practice (similar to AMC)",
        "license": "CC-BY-4.0"
    },
    "medmcqa": {
        "hf_name": "openlifescienceai/medmcqa",
        "priority": 1,
        "size": "~88MB",
        "description": "193k Indian medical entrance exam questions",
        "use_case": "Large question bank across 21 specialties",
        "license": "Apache 2.0"
    },
    "statpearls": {
        "hf_name": "MedRAG/statpearls",
        "priority": 1,
        "size": "~100MB",
        "description": "301k educational snippets from NCBI Bookshelf",
        "use_case": "Gold standard medical education content",
        "license": "NCBI Bookshelf (educational use)"
    },

    # Priority 2: Clinical guidelines and expert questions
    "clinical_guidelines": {
        "hf_name": "epfl-llm/guidelines",
        "priority": 2,
        "size": "~200MB",
        "description": "47k clinical practice guidelines",
        "use_case": "Clinical decision support",
        "license": "Mixed - CHECK BEFORE USE"
    },
    "medxpert_qa": {
        "hf_name": "TsinghuaC3I/MedXpertQA",
        "priority": 2,
        "size": "~5MB",
        "description": "4.4k expert-level medical questions",
        "use_case": "Advanced clinical reasoning",
        "license": "Check repository"
    },

    # Priority 3: Additional resources
    "wikidoc": {
        "hf_name": "medalpaca/medical_meadow_wikidoc",
        "priority": 3,
        "size": "~5MB",
        "description": "10k medical Q&A from WikiDoc",
        "use_case": "General medical knowledge",
        "license": "Creative Commons"
    },
    "pubmedqa": {
        "hf_name": "qiaojin/PubMedQA",
        "priority": 3,
        "size": "~50MB",
        "description": "273k biomedical research questions",
        "use_case": "Evidence-based medicine",
        "license": "MIT"
    },
    "medical_flashcards": {
        "hf_name": "medalpaca/medical_meadow_medical_flashcards",
        "priority": 3,
        "size": "~20MB",
        "description": "34k medical flashcards",
        "use_case": "Quick review and memorization",
        "license": "Creative Commons"
    }
}


def download_dataset(dataset_key: str, force: bool = False) -> bool:
    """Download a specific dataset from HuggingFace"""

    if dataset_key not in DATASETS:
        logger.error(f"Unknown dataset: {dataset_key}")
        logger.info(f"Available datasets: {', '.join(DATASETS.keys())}")
        return False

    config = DATASETS[dataset_key]
    output_dir = DATA_DIR / dataset_key

    # Check if already downloaded
    if output_dir.exists() and not force:
        logger.info(f"✓ {dataset_key} already downloaded. Use --force to re-download.")
        return True

    logger.info(f"\n{'='*70}")
    logger.info(f"Downloading: {dataset_key}")
    logger.info(f"Source: {config['hf_name']}")
    logger.info(f"Description: {config['description']}")
    logger.info(f"Size: {config['size']}")
    logger.info(f"License: {config['license']}")
    logger.info(f"Use case: {config['use_case']}")
    logger.info(f"{'='*70}\n")

    try:
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Download dataset
        logger.info(f"Downloading from HuggingFace: {config['hf_name']}")
        dataset = load_dataset(config['hf_name'])

        # Save to disk
        logger.info(f"Saving to: {output_dir}")
        dataset.save_to_disk(str(output_dir))

        # Save metadata
        metadata = {
            "dataset_key": dataset_key,
            "hf_name": config['hf_name'],
            "description": config['description'],
            "license": config['license'],
            "use_case": config['use_case'],
            "priority": config['priority'],
            "download_date": str(Path(output_dir / "dataset_info.json").stat().st_mtime) if (output_dir / "dataset_info.json").exists() else "unknown"
        }

        import json
        with open(output_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"✓ Successfully downloaded {dataset_key}")
        logger.info(f"  Location: {output_dir}")

        # Print dataset info
        if hasattr(dataset, 'info'):
            logger.info(f"  Splits: {list(dataset.keys())}")
            for split_name, split_data in dataset.items():
                logger.info(f"    - {split_name}: {len(split_data)} examples")

        return True

    except Exception as e:
        logger.error(f"✗ Failed to download {dataset_key}: {str(e)}")
        return False


def download_priority_datasets(priority: int = 1, force: bool = False) -> dict:
    """Download all datasets of a specific priority level"""

    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }

    priority_datasets = {k: v for k, v in DATASETS.items() if v['priority'] == priority}

    logger.info(f"\n{'='*70}")
    logger.info(f"Downloading Priority {priority} Datasets ({len(priority_datasets)} datasets)")
    logger.info(f"{'='*70}\n")

    for dataset_key in priority_datasets.keys():
        success = download_dataset(dataset_key, force)
        if success:
            results["success"].append(dataset_key)
        else:
            results["failed"].append(dataset_key)

    return results


def download_all_datasets(force: bool = False) -> dict:
    """Download all available datasets"""

    results = {
        "success": [],
        "failed": [],
        "skipped": []
    }

    logger.info(f"\n{'='*70}")
    logger.info(f"Downloading ALL Datasets ({len(DATASETS)} total)")
    logger.info(f"{'='*70}\n")

    # Download by priority
    for priority in [1, 2, 3]:
        priority_results = download_priority_datasets(priority, force)
        results["success"].extend(priority_results["success"])
        results["failed"].extend(priority_results["failed"])
        results["skipped"].extend(priority_results["skipped"])

    return results


def list_datasets():
    """List all available datasets"""

    print(f"\n{'='*70}")
    print("Available HuggingFace Medical Datasets")
    print(f"{'='*70}\n")

    for priority in [1, 2, 3]:
        priority_datasets = {k: v for k, v in DATASETS.items() if v['priority'] == priority}

        if not priority_datasets:
            continue

        print(f"\nPriority {priority} ({len(priority_datasets)} datasets):")
        print("-" * 70)

        for key, config in priority_datasets.items():
            status = "✓ Downloaded" if (DATA_DIR / key).exists() else "○ Not downloaded"
            print(f"\n  {status} - {key}")
            print(f"    Source: {config['hf_name']}")
            print(f"    Description: {config['description']}")
            print(f"    Size: {config['size']}")
            print(f"    License: {config['license']}")
            print(f"    Use case: {config['use_case']}")

    print(f"\n{'='*70}\n")


def check_downloads():
    """Check which datasets have been downloaded"""

    print(f"\n{'='*70}")
    print("Downloaded Datasets Status")
    print(f"{'='*70}\n")

    downloaded = []
    not_downloaded = []

    for key in DATASETS.keys():
        if (DATA_DIR / key).exists():
            downloaded.append(key)
        else:
            not_downloaded.append(key)

    print(f"Downloaded ({len(downloaded)}/{len(DATASETS)}):")
    for key in downloaded:
        size = sum(f.stat().st_size for f in (DATA_DIR / key).rglob('*') if f.is_file())
        size_mb = size / (1024 * 1024)
        print(f"  ✓ {key} ({size_mb:.1f} MB)")

    if not_downloaded:
        print(f"\nNot Downloaded ({len(not_downloaded)}):")
        for key in not_downloaded:
            print(f"  ○ {key}")

    total_size = sum(
        sum(f.stat().st_size for f in (DATA_DIR / key).rglob('*') if f.is_file())
        for key in downloaded
    )
    total_size_mb = total_size / (1024 * 1024)

    print(f"\nTotal downloaded: {total_size_mb:.1f} MB")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Download medical education datasets from HuggingFace",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all priority 1 datasets (recommended)
  python scripts/download_huggingface_datasets.py --priority-only

  # Download all datasets
  python scripts/download_huggingface_datasets.py --all

  # Download specific dataset
  python scripts/download_huggingface_datasets.py --dataset medmcqa

  # List available datasets
  python scripts/download_huggingface_datasets.py --list

  # Check download status
  python scripts/download_huggingface_datasets.py --check
        """
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Download all available datasets"
    )
    parser.add_argument(
        "--priority-only",
        action="store_true",
        help="Download only priority 1 datasets (recommended for starting)"
    )
    parser.add_argument(
        "--priority",
        type=int,
        choices=[1, 2, 3],
        help="Download all datasets of specific priority level"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Download specific dataset by key"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available datasets"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check which datasets are already downloaded"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-download even if dataset already exists"
    )

    args = parser.parse_args()

    # Handle list command
    if args.list:
        list_datasets()
        return

    # Handle check command
    if args.check:
        check_downloads()
        return

    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Download datasets
    results = None

    if args.all:
        results = download_all_datasets(args.force)
    elif args.priority_only or args.priority == 1:
        results = download_priority_datasets(1, args.force)
    elif args.priority:
        results = download_priority_datasets(args.priority, args.force)
    elif args.dataset:
        success = download_dataset(args.dataset, args.force)
        results = {
            "success": [args.dataset] if success else [],
            "failed": [] if success else [args.dataset],
            "skipped": []
        }
    else:
        parser.print_help()
        return

    # Print summary
    if results:
        print(f"\n{'='*70}")
        print("Download Summary")
        print(f"{'='*70}")
        print(f"Success: {len(results['success'])}")
        print(f"Failed: {len(results['failed'])}")
        print(f"Skipped: {len(results['skipped'])}")

        if results['success']:
            print(f"\nSuccessfully downloaded:")
            for ds in results['success']:
                print(f"  ✓ {ds}")

        if results['failed']:
            print(f"\nFailed to download:")
            for ds in results['failed']:
                print(f"  ✗ {ds}")

        print(f"{'='*70}\n")

        # Next steps
        print("Next steps:")
        print("  1. Check downloads: python scripts/download_huggingface_datasets.py --check")
        print("  2. Process datasets: python scripts/process_huggingface_datasets.py")
        print("  3. Index in Qdrant: python scripts/index_qdrant.py --source huggingface")
        print()


if __name__ == "__main__":
    main()
