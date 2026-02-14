#!/usr/bin/env python3
"""
Weekly Medical Resources Update Orchestrator

Automated weekly update system that:
- Detects new and updated medical resources
- Downloads only new/updated items (incremental)
- Resumes from crashes
- Generates weekly summary reports
- Continues on errors with final error report

Usage:
    python3 scripts/weekly_medical_update.py                    # Full update
    python3 scripts/weekly_medical_update.py --dry-run          # Preview only
    python3 scripts/weekly_medical_update.py --resource RES-001 # Specific resource
    python3 scripts/weekly_medical_update.py --force            # Force full scan

Environment Variables:
    NCBI_API_KEY: Required for StatPearls updates

Example:
    export NCBI_API_KEY='your_key_here'
    python3 scripts/weekly_medical_update.py
"""

import argparse
import json
import logging
import os
import sys
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

# Add scripts/lib to Python path
sys.path.insert(0, str(Path(__file__).parent))

from lib.state_manager import WeeklyUpdateState
from lib.update_detector import create_detector, UpdateResult

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESOURCE_DB_PATH = PROJECT_ROOT / "resource_database.json"
STATE_FILE_PATH = Path("/mnt/data/medical_resources/weekly_update_state.json")
DOWNLOAD_DIR = Path("/mnt/data/medical_resources")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(DOWNLOAD_DIR / 'logs' / f'weekly_update_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)
logger = logging.getLogger(__name__)


class WeeklyUpdateOrchestrator:
    """Orchestrates weekly medical resources updates"""

    def __init__(self, dry_run: bool = False, force: bool = False):
        self.dry_run = dry_run
        self.force = force
        self.state_mgr = WeeklyUpdateState(STATE_FILE_PATH)
        self.api_key = os.getenv('NCBI_API_KEY')
        self.resource_db = self._load_resource_db()
        self.start_time = datetime.now(timezone.utc)

        # Statistics
        self.total_new = 0
        self.total_updated = 0
        self.total_failed = 0
        self.total_size_mb = 0

    def _load_resource_db(self) -> Dict:
        """Load resource database"""
        if not RESOURCE_DB_PATH.exists():
            logger.error(f"Resource database not found: {RESOURCE_DB_PATH}")
            sys.exit(1)

        with open(RESOURCE_DB_PATH, 'r') as f:
            return json.load(f)

    def check_prerequisites(self):
        """Check that all prerequisites are met"""
        logger.info("Checking prerequisites...")

        # Check external drive mounted
        if not DOWNLOAD_DIR.exists():
            logger.error(f"Download directory not found: {DOWNLOAD_DIR}")
            logger.error("Please mount external drive at /mnt/data")
            sys.exit(1)

        # Check NCBI API key for StatPearls
        if not self.api_key:
            logger.warning("NCBI_API_KEY not set - StatPearls updates will be skipped")
            logger.info("To enable StatPearls: export NCBI_API_KEY='your_key'")

        # Check disk space
        stat = os.statvfs(DOWNLOAD_DIR)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        logger.info(f"Available disk space: {free_gb:.1f} GB")

        if free_gb < 10:
            logger.warning(f"Low disk space: {free_gb:.1f} GB available")

        logger.info("✅ Prerequisites check complete")

    def update_resource(self, resource_id: str, resource_info: Dict) -> bool:
        """
        Update a single resource.

        Returns:
            True if successful, False if failed
        """
        resource_name = resource_info['name']
        logger.info(f"\n{'='*70}")
        logger.info(f"Processing: {resource_id} - {resource_name}")
        logger.info(f"{'='*70}")

        # Initialize resource in state if needed
        self.state_mgr.init_resource(resource_id, resource_name)

        # Mark as started
        self.state_mgr.mark_resource_started(resource_id)
        self.state_mgr.save_state()  # Save immediately (crash-safe)

        try:
            # Step 1: Detect updates
            logger.info("Step 1: Detecting updates...")
            detector = create_detector(resource_id, resource_info, api_key=self.api_key)

            if not detector:
                logger.warning(f"No update detector available for {resource_id}")
                self.state_mgr.mark_resource_failed(resource_id, "No detector available")
                self.state_mgr.save_state()
                return False

            # Get last check date
            last_check = self.state_mgr.get_last_check_date(resource_id)
            if self.force:
                last_check = None  # Force full scan

            # Get known items (from metadata files)
            known_items = self._get_known_items(resource_id)

            # Detect updates
            updates = detector.detect_updates(since_date=last_check, known_items=known_items)

            if updates.error:
                logger.error(f"Update detection failed: {updates.error}")
                self.state_mgr.mark_resource_failed(resource_id, updates.error)
                self.state_mgr.save_state()
                return False

            logger.info(f"✨ Found: {len(updates.new_items)} new, {len(updates.updated_items)} updated")

            if not updates.has_updates() and not self.force:
                logger.info(f"✓ {resource_name} is up-to-date - skipping download")
                self.state_mgr.mark_resource_completed(resource_id, {
                    'items_new_this_run': 0,
                    'items_updated_this_run': 0,
                    'items_failed': 0,
                    'size_downloaded_mb': 0
                })
                self.state_mgr.save_state()
                return True

            # Step 2: Download updates
            if self.dry_run:
                logger.info(f"[DRY RUN] Would download {updates.total_updates()} items")
                return True

            logger.info(f"Step 2: Downloading {updates.total_updates()} items...")
            download_result = self._download_resource(resource_id, resource_info, updates)

            if not download_result['success']:
                logger.error(f"Download failed: {download_result['error']}")
                self.state_mgr.mark_resource_failed(resource_id, download_result['error'])
                self.state_mgr.save_state()
                return False

            # Step 3: Update statistics
            stats = {
                'items_new_this_run': len(updates.new_items),
                'items_updated_this_run': len(updates.updated_items),
                'items_failed': download_result.get('failed', 0),
                'size_downloaded_mb': download_result.get('size_mb', 0)
            }

            self.total_new += stats['items_new_this_run']
            self.total_updated += stats['items_updated_this_run']
            self.total_size_mb += stats['size_downloaded_mb']

            self.state_mgr.mark_resource_completed(resource_id, stats)
            self.state_mgr.save_state()

            logger.info(f"✅ {resource_name} update complete!")
            return True

        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            self.state_mgr.mark_resource_failed(resource_id, str(e))
            self.state_mgr.save_state()
            self.total_failed += 1
            return False

    def _get_known_items(self, resource_id: str) -> Optional[set]:
        """Get set of already-downloaded items from metadata files"""
        # StatPearls metadata
        if resource_id == "RES-001":
            metadata_file = DOWNLOAD_DIR / "statpearls" / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    return set(metadata.get('downloaded', []))

        # Cochrane metadata
        elif resource_id == "RES-002":
            metadata_file = DOWNLOAD_DIR / "cochrane" / "metadata.json"
            if metadata_file.exists():
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                    return set(metadata.get('downloaded', []))

        return None

    def _download_resource(self, resource_id: str, resource_info: Dict, updates: UpdateResult) -> Dict:
        """
        Download a resource using appropriate script.

        Returns:
            Dict with keys: success, error, failed, size_mb
        """
        try:
            if resource_id == "RES-001":  # StatPearls
                return self._download_statpearls(updates)
            elif resource_id == "RES-002":  # Cochrane
                return self._download_cochrane(updates)
            elif resource_id in ["RES-003", "RES-004", "RES-005", "RES-006", "RES-008", "RES-009"]:
                return self._download_guidelines(resource_id, resource_info)
            else:
                return {'success': False, 'error': 'No download script available'}

        except Exception as e:
            logger.error(f"Download error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}

    def _download_statpearls(self, updates: UpdateResult) -> Dict:
        """Download StatPearls using enhanced script"""
        logger.info("Calling download_statpearls.py...")

        cmd = [
            'python3',
            str(PROJECT_ROOT / 'scripts' / 'download_statpearls.py'),
            '--output', str(DOWNLOAD_DIR / 'statpearls'),
            '--api-key', self.api_key
        ]

        # TODO: Add --incremental flag when script is enhanced
        # For now, script's existing resume capability will handle it

        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=14400  # 4 hours timeout
            )

            logger.info("StatPearls download completed successfully")
            return {
                'success': True,
                'failed': 0,
                'size_mb': 0  # TODO: Parse from script output
            }

        except subprocess.CalledProcessError as e:
            logger.error(f"StatPearls download failed: {e.stderr}")
            return {'success': False, 'error': e.stderr}
        except subprocess.TimeoutExpired:
            logger.error("StatPearls download timed out")
            return {'success': False, 'error': 'Timeout after 4 hours'}

    def _download_cochrane(self, updates: UpdateResult) -> Dict:
        """Download Cochrane using enhanced script"""
        logger.info("Cochrane download not yet implemented")
        return {'success': False, 'error': 'Not implemented'}

    def _download_guidelines(self, resource_id: str, resource_info: Dict) -> Dict:
        """Download guidelines using enhanced script"""
        logger.info(f"Guidelines download not yet fully automated: {resource_info['name']}")
        return {'success': False, 'error': 'Manual download required'}

    def run(self, resource_filter: Optional[str] = None):
        """
        Run weekly update for all or specific resources.

        Args:
            resource_filter: If provided, only update this resource ID
        """
        logger.info("="*70)
        logger.info("WEEKLY MEDICAL RESOURCES UPDATE")
        logger.info("="*70)
        logger.info(f"Started: {self.start_time}")
        logger.info(f"Mode: {'DRY RUN' if self.dry_run else 'LIVE UPDATE'}")
        logger.info(f"Force full scan: {self.force}")
        logger.info("="*70)

        # Check prerequisites
        self.check_prerequisites()

        # Get resources to update
        resources_to_update = []
        for resource in self.resource_db['resources']:
            resource_id = resource['id']

            # Apply filter if provided
            if resource_filter and resource_id != resource_filter:
                continue

            # Check priority (skip optional resources unless forced)
            if resource.get('priority') == 'OPTIONAL' and not self.force:
                logger.info(f"Skipping optional resource: {resource_id} (use --force to include)")
                continue

            resources_to_update.append((resource_id, resource))

        logger.info(f"\nUpdating {len(resources_to_update)} resources...")
        logger.info("")

        # Update each resource (continue on errors)
        successful = []
        failed = []

        for resource_id, resource_info in resources_to_update:
            try:
                success = self.update_resource(resource_id, resource_info)
                if success:
                    successful.append(resource_id)
                else:
                    failed.append(resource_id)

            except Exception as e:
                logger.error(f"Unhandled exception for {resource_id}: {e}", exc_info=True)
                failed.append(resource_id)
                self.total_failed += 1

        # Final summary
        end_time = datetime.now(timezone.utc)
        execution_time = (end_time - self.start_time).total_seconds() / 60

        logger.info("")
        logger.info("="*70)
        logger.info("UPDATE COMPLETE")
        logger.info("="*70)
        logger.info(f"Execution time: {execution_time:.1f} minutes")
        logger.info(f"Resources processed: {len(resources_to_update)}")
        logger.info(f"  ✅ Successful: {len(successful)}")
        logger.info(f"  ❌ Failed: {len(failed)}")
        logger.info(f"\nNew resources: {self.total_new}")
        logger.info(f"Updated resources: {self.total_updated}")
        logger.info(f"Total downloaded: {self.total_size_mb / 1024:.2f} GB")

        if failed:
            logger.info(f"\nFailed resources:")
            for resource_id in failed:
                logger.info(f"  - {resource_id}")

        # Update run summary
        self.state_mgr.update_run_summary({
            'status': 'completed',
            'total_new_resources': self.total_new,
            'total_updated_resources': self.total_updated,
            'total_failed': self.total_failed,
            'total_size_downloaded_gb': self.total_size_mb / 1024,
            'execution_time_minutes': execution_time
        })
        self.state_mgr.save_state()

        logger.info(f"\nState saved: {STATE_FILE_PATH}")
        logger.info("="*70)

        # Exit code
        sys.exit(1 if failed else 0)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Weekly Medical Resources Update System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview updates without downloading'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Force full scan (ignore last check dates)'
    )

    parser.add_argument(
        '--resource',
        type=str,
        help='Update specific resource only (e.g., RES-001)'
    )

    args = parser.parse_args()

    # Create and run orchestrator
    orchestrator = WeeklyUpdateOrchestrator(
        dry_run=args.dry_run,
        force=args.force
    )

    orchestrator.run(resource_filter=args.resource)


if __name__ == '__main__':
    main()
