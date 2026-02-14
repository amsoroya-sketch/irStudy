#!/usr/bin/env python3
"""
Initialize Weekly Update State File

Creates the initial state file for the weekly medical resources update system
and populates it with resources from resource_database.json.

Usage:
    python3 scripts/init_weekly_state.py
"""

import json
import sys
from pathlib import Path

# Add scripts/lib to Python path
sys.path.insert(0, str(Path(__file__).parent))

from lib.state_manager import WeeklyUpdateState
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
RESOURCE_DB_PATH = PROJECT_ROOT / "resource_database.json"
STATE_FILE_PATH = Path("/mnt/data/medical_resources/weekly_update_state.json")


def main():
    """Initialize weekly update state from resource database"""

    # Load resource database
    if not RESOURCE_DB_PATH.exists():
        logger.error(f"Resource database not found: {RESOURCE_DB_PATH}")
        sys.exit(1)

    with open(RESOURCE_DB_PATH, 'r') as f:
        resource_db = json.load(f)

    logger.info(f"Loaded resource database: {resource_db['metadata']['total_resources']} resources")

    # Initialize state manager
    state_mgr = WeeklyUpdateState(STATE_FILE_PATH)

    # Add all resources from database
    for resource in resource_db['resources']:
        resource_id = resource['id']
        resource_name = resource['name']

        logger.info(f"Initializing resource: {resource_id} - {resource_name}")
        state_mgr.init_resource(resource_id, resource_name)

    # Save initial state
    state_mgr.save_state()

    # Print status
    print("\n")
    state_mgr.print_status()

    print(f"\n✅ State file initialized: {STATE_FILE_PATH}")
    print(f"   Total resources: {len(resource_db['resources'])}")


if __name__ == '__main__':
    main()
