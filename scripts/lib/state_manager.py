#!/usr/bin/env python3
"""
Weekly Update State Manager

Manages persistent state for weekly medical resources updates, including:
- Last run timestamps
- Download statistics per resource
- Error tracking
- Resume capability

The state file allows the system to:
- Resume from crashes without re-downloading
- Track incremental progress
- Generate weekly diff reports
- Detect new/updated resources

State File Schema:
{
  "version": "1.0",
  "last_run": "2026-01-24T00:00:00Z",
  "resources": {
    "RES-001": {
      "name": "StatPearls",
      "last_check": "2026-01-24T02:00:00Z",
      "last_successful_download": "2026-01-24T04:30:00Z",
      "status": "completed|in_progress|failed",
      "statistics": {
        "total_items": 10000,
        "items_new_this_run": 3,
        "items_updated_this_run": 15,
        "items_failed": 0,
        "size_downloaded_mb": 250
      },
      "errors": [],
      "next_scheduled_check": "2026-01-31T02:00:00Z"
    }
  },
  "run_summary": {
    "total_new_resources": 5,
    "total_updated_resources": 15,
    "total_failed": 1,
    "total_size_downloaded_gb": 0.27,
    "execution_time_minutes": 45
  }
}
"""

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class WeeklyUpdateState:
    """Manages persistent state for weekly medical resources updates"""

    STATE_VERSION = "1.0"
    MAX_BACKUPS = 5

    def __init__(self, state_file: Path):
        """
        Initialize state manager.

        Args:
            state_file: Path to state JSON file (e.g., /mnt/data/medical_resources/weekly_update_state.json)
        """
        self.state_file = Path(state_file)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        """Load state from JSON file or create new state"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    state = json.load(f)

                # Validate version
                if state.get('version') != self.STATE_VERSION:
                    logger.warning(f"State file version mismatch. Expected {self.STATE_VERSION}, got {state.get('version')}")
                    logger.info("Creating backup and initializing new state")
                    self._create_backup()
                    return self._create_initial_state()

                logger.info(f"Loaded state from {self.state_file}")
                return state

            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Corrupted state file: {e}")
                logger.info("Attempting to restore from backup...")

                # Try to restore from backup
                restored = self._restore_from_backup()
                if restored:
                    return restored

                logger.warning("No valid backup found. Creating new state.")
                return self._create_initial_state()
        else:
            logger.info("State file not found. Creating new state.")
            return self._create_initial_state()

    def _create_initial_state(self) -> Dict:
        """Create initial state structure"""
        return {
            "version": self.STATE_VERSION,
            "created_at": self._utc_now(),
            "last_run": None,
            "resources": {},
            "run_summary": {
                "total_runs": 0,
                "last_run_status": None,
                "total_new_resources_all_time": 0,
                "total_updated_resources_all_time": 0,
                "total_failures_all_time": 0
            }
        }

    def _utc_now(self) -> str:
        """Get current UTC timestamp as ISO string"""
        return datetime.now(timezone.utc).isoformat()

    def save_state(self):
        """
        Save state to JSON file with atomic write and backup.

        Uses atomic write pattern:
        1. Write to temporary file
        2. Create backup of current state
        3. Move temp file to actual location
        """
        try:
            # Update last_run timestamp
            self.state['last_run'] = self._utc_now()

            # Write to temporary file first
            temp_file = self.state_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(self.state, f, indent=2)

            # Create backup of current state before overwriting
            if self.state_file.exists():
                self._create_backup()

            # Atomic move
            shutil.move(str(temp_file), str(self.state_file))

            logger.info(f"✅ State saved: {self.state_file}")

        except Exception as e:
            logger.error(f"Failed to save state: {e}")
            raise

    def _create_backup(self):
        """Create numbered backup of current state file"""
        if not self.state_file.exists():
            return

        # Rotate existing backups
        for i in range(self.MAX_BACKUPS - 1, 0, -1):
            old_backup = self.state_file.with_suffix(f'.backup.{i}')
            new_backup = self.state_file.with_suffix(f'.backup.{i+1}')

            if old_backup.exists():
                if new_backup.exists():
                    new_backup.unlink()
                old_backup.rename(new_backup)

        # Create new backup.1
        backup_file = self.state_file.with_suffix('.backup.1')
        shutil.copy2(self.state_file, backup_file)
        logger.info(f"Created backup: {backup_file}")

    def _restore_from_backup(self) -> Optional[Dict]:
        """Attempt to restore state from most recent valid backup"""
        for i in range(1, self.MAX_BACKUPS + 1):
            backup_file = self.state_file.with_suffix(f'.backup.{i}')

            if not backup_file.exists():
                continue

            try:
                with open(backup_file, 'r') as f:
                    state = json.load(f)

                if state.get('version') == self.STATE_VERSION:
                    logger.info(f"✅ Restored state from {backup_file}")
                    # Copy backup to main state file
                    shutil.copy2(backup_file, self.state_file)
                    return state

            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Backup {backup_file} is invalid: {e}")
                continue

        return None

    def get_resource_state(self, resource_id: str) -> Optional[Dict]:
        """Get state for a specific resource"""
        return self.state['resources'].get(resource_id)

    def init_resource(self, resource_id: str, resource_name: str):
        """Initialize state for a new resource"""
        if resource_id not in self.state['resources']:
            self.state['resources'][resource_id] = {
                "name": resource_name,
                "first_run": self._utc_now(),
                "last_check": None,
                "last_successful_download": None,
                "status": "pending",
                "statistics": {
                    "total_items": 0,
                    "items_new_this_run": 0,
                    "items_updated_this_run": 0,
                    "items_failed": 0,
                    "size_downloaded_mb": 0
                },
                "errors": [],
                "next_scheduled_check": None
            }
            logger.info(f"Initialized state for resource: {resource_id} ({resource_name})")

    def mark_resource_started(self, resource_id: str):
        """Mark resource download as started"""
        if resource_id in self.state['resources']:
            self.state['resources'][resource_id]['status'] = 'in_progress'
            self.state['resources'][resource_id]['last_check'] = self._utc_now()
            # Reset current run statistics
            self.state['resources'][resource_id]['statistics']['items_new_this_run'] = 0
            self.state['resources'][resource_id]['statistics']['items_updated_this_run'] = 0
            self.state['resources'][resource_id]['statistics']['items_failed'] = 0
            self.state['resources'][resource_id]['statistics']['size_downloaded_mb'] = 0
            self.state['resources'][resource_id]['errors'] = []
            logger.info(f"Marked {resource_id} as in_progress")

    def mark_resource_completed(self, resource_id: str, statistics: Dict):
        """
        Mark resource download as completed and update statistics.

        Args:
            resource_id: Resource identifier (e.g., "RES-001")
            statistics: Dict with keys:
                - items_new_this_run
                - items_updated_this_run
                - items_failed
                - size_downloaded_mb
                - total_items (optional)
        """
        if resource_id in self.state['resources']:
            self.state['resources'][resource_id]['status'] = 'completed'
            self.state['resources'][resource_id]['last_successful_download'] = self._utc_now()

            # Update statistics
            self.state['resources'][resource_id]['statistics'].update(statistics)

            logger.info(f"✅ Marked {resource_id} as completed")
            logger.info(f"   New: {statistics.get('items_new_this_run', 0)}, "
                       f"Updated: {statistics.get('items_updated_this_run', 0)}, "
                       f"Failed: {statistics.get('items_failed', 0)}")

    def mark_resource_failed(self, resource_id: str, error: str):
        """Mark resource download as failed"""
        if resource_id in self.state['resources']:
            self.state['resources'][resource_id]['status'] = 'failed'
            self.state['resources'][resource_id]['errors'].append({
                "timestamp": self._utc_now(),
                "error": error
            })
            logger.error(f"❌ Marked {resource_id} as failed: {error}")

    def add_resource_error(self, resource_id: str, error: str):
        """Add an error to resource (without changing status)"""
        if resource_id in self.state['resources']:
            self.state['resources'][resource_id]['errors'].append({
                "timestamp": self._utc_now(),
                "error": error
            })

    def update_run_summary(self, summary: Dict):
        """
        Update overall run summary.

        Args:
            summary: Dict with keys:
                - total_new_resources
                - total_updated_resources
                - total_failed
                - total_size_downloaded_gb
                - execution_time_minutes
        """
        self.state['run_summary']['last_run_status'] = summary.get('status', 'completed')
        self.state['run_summary']['total_runs'] += 1

        # Accumulate all-time statistics
        self.state['run_summary']['total_new_resources_all_time'] += summary.get('total_new_resources', 0)
        self.state['run_summary']['total_updated_resources_all_time'] += summary.get('total_updated_resources', 0)
        self.state['run_summary']['total_failures_all_time'] += summary.get('total_failed', 0)

        # Store this run's summary
        self.state['run_summary']['last_run'] = {
            "timestamp": self._utc_now(),
            "total_new_resources": summary.get('total_new_resources', 0),
            "total_updated_resources": summary.get('total_updated_resources', 0),
            "total_failed": summary.get('total_failed', 0),
            "total_size_downloaded_gb": summary.get('total_size_downloaded_gb', 0),
            "execution_time_minutes": summary.get('execution_time_minutes', 0)
        }

    def get_last_check_date(self, resource_id: str) -> Optional[datetime]:
        """Get last check date for a resource as datetime object"""
        resource = self.get_resource_state(resource_id)
        if not resource or not resource.get('last_check'):
            return None

        try:
            return datetime.fromisoformat(resource['last_check'])
        except (ValueError, TypeError):
            return None

    def should_check_resource(self, resource_id: str, frequency_days: int = 7) -> bool:
        """
        Determine if a resource should be checked based on frequency.

        Args:
            resource_id: Resource identifier
            frequency_days: Days between checks (default: 7 for weekly)

        Returns:
            True if resource should be checked
        """
        last_check = self.get_last_check_date(resource_id)
        if not last_check:
            return True  # Never checked, should check

        days_since_check = (datetime.now(timezone.utc) - last_check).days
        return days_since_check >= frequency_days

    def get_summary(self) -> Dict:
        """Get summary of current state"""
        total_resources = len(self.state['resources'])
        completed = sum(1 for r in self.state['resources'].values() if r['status'] == 'completed')
        in_progress = sum(1 for r in self.state['resources'].values() if r['status'] == 'in_progress')
        failed = sum(1 for r in self.state['resources'].values() if r['status'] == 'failed')

        return {
            "total_resources": total_resources,
            "completed": completed,
            "in_progress": in_progress,
            "failed": failed,
            "last_run": self.state.get('last_run'),
            "total_runs": self.state['run_summary']['total_runs']
        }

    def print_status(self):
        """Print human-readable status"""
        summary = self.get_summary()

        print("=" * 70)
        print("WEEKLY UPDATE STATE")
        print("=" * 70)
        print(f"Last Run: {summary['last_run'] or 'Never'}")
        print(f"Total Runs: {summary['total_runs']}")
        print(f"\nResources: {summary['total_resources']}")
        print(f"  ✅ Completed: {summary['completed']}")
        print(f"  ⏳ In Progress: {summary['in_progress']}")
        print(f"  ❌ Failed: {summary['failed']}")
        print()

        # Print per-resource status
        for resource_id, resource in self.state['resources'].items():
            status_icon = {
                'completed': '✅',
                'in_progress': '⏳',
                'failed': '❌',
                'pending': '⏸️'
            }.get(resource['status'], '❓')

            print(f"{status_icon} {resource_id}: {resource['name']}")
            print(f"   Status: {resource['status']}")
            print(f"   Last Check: {resource['last_check'] or 'Never'}")
            stats = resource['statistics']
            print(f"   This Run: +{stats['items_new_this_run']} new, "
                  f"~{stats['items_updated_this_run']} updated, "
                  f"✗{stats['items_failed']} failed")

            if resource['errors']:
                print(f"   ⚠️  {len(resource['errors'])} errors")
            print()

        print("=" * 70)
