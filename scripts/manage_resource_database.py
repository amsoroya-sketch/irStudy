#!/usr/bin/env python3
"""
Medical Resources Database Management Tool

This script manages the medical resources database, including:
- Updating resource metadata (versions, download dates, etc.)
- Checking for resource updates
- Generating status reports
- Tracking download progress

Usage:
    python3 scripts/manage_resource_database.py --help
    python3 scripts/manage_resource_database.py list
    python3 scripts/manage_resource_database.py update RES-001 --version "2026-01-17" --downloaded
    python3 scripts/manage_resource_database.py status
    python3 scripts/manage_resource_database.py check-updates
"""

import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import sys

# Database paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_JSON = PROJECT_ROOT / "resource_database.json"
DATABASE_MD = PROJECT_ROOT / "RESOURCE_DATABASE.md"


class ResourceDatabaseManager:
    """Manages the medical resources database"""

    def __init__(self, database_path: Path = DATABASE_JSON):
        self.database_path = database_path
        self.data = self.load_database()

    def load_database(self) -> Dict:
        """Load the JSON database"""
        if not self.database_path.exists():
            raise FileNotFoundError(f"Database not found: {self.database_path}")

        with open(self.database_path, 'r') as f:
            return json.load(f)

    def save_database(self):
        """Save the JSON database"""
        # Update last_updated timestamp
        self.data['metadata']['last_updated'] = datetime.now().strftime("%Y-%m-%d")

        with open(self.database_path, 'w') as f:
            json.dump(self.data, f, indent=2)

        print(f"✅ Database saved: {self.database_path}")

    def get_resource(self, resource_id: str) -> Optional[Dict]:
        """Get a resource by ID"""
        for resource in self.data['resources']:
            if resource['id'] == resource_id:
                return resource
        return None

    def list_resources(self, filter_priority: Optional[str] = None, filter_status: Optional[str] = None):
        """List all resources with optional filters"""
        print("\n" + "="*80)
        print("MEDICAL RESOURCES DATABASE")
        print("="*80)
        print(f"Total Resources: {self.data['metadata']['total_resources']}")
        print(f"Total Size: {self.data['metadata']['total_size_gb_min']}-{self.data['metadata']['total_size_gb_max']} GB")
        print(f"Last Updated: {self.data['metadata']['last_updated']}")
        print("="*80 + "\n")

        for resource in self.data['resources']:
            # Apply filters
            if filter_priority and resource['priority'] != filter_priority.upper():
                continue
            if filter_status and resource['download']['status'] != filter_status:
                continue

            # Display resource info
            status_icon = self._get_status_icon(resource)
            priority_badge = self._get_priority_badge(resource['priority'])

            print(f"{status_icon} {resource['id']}: {resource['name']}")
            print(f"   Priority: {priority_badge} | Category: {resource['category']}")
            print(f"   Size: {resource['size']['estimated_gb']} {resource['size']['unit']}")
            print(f"   Version: {resource['version']['current']}")
            print(f"   Latest Release: {resource['version']['latest_release_date']}")
            print(f"   Next Check: {resource['version']['next_check_date']}")
            print(f"   Download: {resource['download']['method']} | Status: {resource['download']['status']}")
            print(f"   Last Downloaded: {resource['download']['last_downloaded'] or 'Never'}")
            print()

    def _get_status_icon(self, resource: Dict) -> str:
        """Get status icon for resource"""
        status = resource['download']['status']
        if 'Available' in status or 'Automated' in status:
            return "✅"
        elif 'Manual' in status:
            return "⚠️"
        elif 'Requires' in status:
            return "⏳"
        else:
            return "❓"

    def _get_priority_badge(self, priority: str) -> str:
        """Get colored priority badge"""
        if priority == "HIGH":
            return "🔴 HIGH"
        elif priority == "MEDIUM":
            return "🟡 MEDIUM"
        else:
            return "🟢 LOW"

    def update_resource(self, resource_id: str, **kwargs):
        """Update resource metadata"""
        resource = self.get_resource(resource_id)
        if not resource:
            print(f"❌ Resource not found: {resource_id}")
            return False

        # Update version info
        if 'version' in kwargs:
            resource['version']['current'] = kwargs['version']
            resource['version']['latest_release_date'] = datetime.now().strftime("%Y-%m-%d")

        # Update download status
        if 'downloaded' in kwargs and kwargs['downloaded']:
            resource['download']['last_downloaded'] = datetime.now().strftime("%Y-%m-%d")

        # Update integration status
        if 'processed' in kwargs:
            resource['integration']['processed'] = kwargs['processed']
        if 'indexed' in kwargs:
            resource['integration']['indexed'] = kwargs['indexed']
        if 'citation_validated' in kwargs:
            resource['integration']['citation_validated'] = kwargs['citation_validated']

        # Update custom fields
        if 'next_check_date' in kwargs:
            resource['version']['next_check_date'] = kwargs['next_check_date']

        self.save_database()
        print(f"✅ Updated resource: {resource_id}")
        return True

    def generate_status_report(self):
        """Generate comprehensive status report"""
        print("\n" + "="*80)
        print("RESOURCE DATABASE STATUS REPORT")
        print("="*80)
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80 + "\n")

        # Summary by priority
        print("📊 BY PRIORITY:")
        for priority in ['HIGH', 'MEDIUM', 'LOW']:
            count = sum(1 for r in self.data['resources'] if r['priority'] == priority)
            print(f"   {self._get_priority_badge(priority)}: {count} resources")
        print()

        # Summary by download method
        print("📥 BY DOWNLOAD METHOD:")
        automated = len(self.data['automation']['fully_automated'])
        partial = len(self.data['automation']['partially_automated'])
        manual = len(self.data['automation']['manual_only'])
        print(f"   ✅ Fully Automated: {automated} resources")
        print(f"   ⚙️  Partially Automated: {partial} resources")
        print(f"   ⚠️  Manual Only: {manual} resources")
        print()

        # Summary by integration status
        print("🔗 INTEGRATION STATUS:")
        downloaded = sum(1 for r in self.data['resources'] if r['download']['last_downloaded'])
        processed = sum(1 for r in self.data['resources'] if r['integration']['processed'])
        indexed = sum(1 for r in self.data['resources'] if r['integration']['indexed'])
        validated = sum(1 for r in self.data['resources'] if r['integration']['citation_validated'])

        total = len(self.data['resources'])
        print(f"   📥 Downloaded: {downloaded}/{total} ({downloaded/total*100:.1f}%)")
        print(f"   ⚙️  Processed: {processed}/{total} ({processed/total*100:.1f}%)")
        print(f"   🗄️  Indexed: {indexed}/{total} ({indexed/total*100:.1f}%)")
        print(f"   ✅ Citation Validated: {validated}/{total} ({validated/total*100:.1f}%)")
        print()

        # Resources needing updates
        print("🔄 UPDATE STATUS:")
        today = datetime.now()
        needs_update = []

        for resource in self.data['resources']:
            next_check = datetime.strptime(resource['version']['next_check_date'], "%Y-%m-%d")
            if next_check <= today:
                needs_update.append(resource)

        if needs_update:
            print(f"   ⚠️  {len(needs_update)} resources need update check:")
            for resource in needs_update:
                print(f"      - {resource['id']}: {resource['name']} (due: {resource['version']['next_check_date']})")
        else:
            print(f"   ✅ All resources are up to date")
        print()

        # Storage summary
        print("💾 STORAGE SUMMARY:")
        total_size = sum(r['size']['estimated_gb'] for r in self.data['resources'])
        downloaded_size = sum(
            r['size']['estimated_gb'] for r in self.data['resources']
            if r['download']['last_downloaded']
        )
        print(f"   Total Estimated: {total_size:.1f} GB")
        print(f"   Downloaded: {downloaded_size:.1f} GB")
        print(f"   Remaining: {total_size - downloaded_size:.1f} GB")
        print()

    def check_updates_needed(self):
        """Check which resources need update checks"""
        print("\n" + "="*80)
        print("RESOURCES REQUIRING UPDATE CHECKS")
        print("="*80 + "\n")

        today = datetime.now()
        needs_update = []

        for resource in self.data['resources']:
            next_check = datetime.strptime(resource['version']['next_check_date'], "%Y-%m-%d")
            days_until = (next_check - today).days

            if days_until <= 7:  # Due within a week
                needs_update.append((resource, days_until))

        if not needs_update:
            print("✅ No resources require immediate update checks\n")
            return

        # Sort by days until due
        needs_update.sort(key=lambda x: x[1])

        for resource, days_until in needs_update:
            if days_until < 0:
                status = f"⚠️  OVERDUE by {abs(days_until)} days"
            elif days_until == 0:
                status = "🔴 DUE TODAY"
            else:
                status = f"🟡 Due in {days_until} days"

            print(f"{status}")
            print(f"   ID: {resource['id']}")
            print(f"   Name: {resource['name']}")
            print(f"   Current Version: {resource['version']['current']}")
            print(f"   Last Release: {resource['version']['latest_release_date']}")
            print(f"   Next Check: {resource['version']['next_check_date']}")
            print(f"   Check Command: {resource.get('update_check_command', 'Manual check required')}")
            print()

    def export_csv(self, output_path: Path):
        """Export database to CSV format"""
        import csv

        with open(output_path, 'w', newline='') as f:
            writer = csv.writer(f)

            # Header
            writer.writerow([
                'ID', 'Name', 'Category', 'Priority', 'Size (GB)',
                'Latest Version', 'Latest Release Date', 'Release Frequency',
                'Next Check Date', 'Next Expected Release',
                'Download Method', 'Download Status', 'Last Downloaded',
                'Processed', 'Indexed', 'Citation Validated'
            ])

            # Data rows
            for resource in self.data['resources']:
                writer.writerow([
                    resource['id'],
                    resource['name'],
                    resource['category'],
                    resource['priority'],
                    resource['size']['estimated_gb'],
                    resource['version']['current'],
                    resource['version']['latest_release_date'],
                    resource['version']['release_frequency'],
                    resource['version']['next_check_date'],
                    resource['version'].get('next_expected_release', 'N/A'),
                    resource['download']['method'],
                    resource['download']['status'],
                    resource['download']['last_downloaded'] or 'Never',
                    resource['integration']['processed'],
                    resource['integration']['indexed'],
                    resource['integration']['citation_validated']
                ])

        print(f"✅ Exported to CSV: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Medical Resources Database Management Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all resources
  python3 scripts/manage_resource_database.py list

  # List only HIGH priority resources
  python3 scripts/manage_resource_database.py list --priority HIGH

  # Update resource after download
  python3 scripts/manage_resource_database.py update RES-001 --downloaded

  # Update version and mark as processed
  python3 scripts/manage_resource_database.py update RES-001 --version "2026-01-20" --processed

  # Generate status report
  python3 scripts/manage_resource_database.py status

  # Check which resources need updates
  python3 scripts/manage_resource_database.py check-updates

  # Export to CSV
  python3 scripts/manage_resource_database.py export --output resources.csv
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # List command
    list_parser = subparsers.add_parser('list', help='List all resources')
    list_parser.add_argument('--priority', choices=['HIGH', 'MEDIUM', 'LOW'], help='Filter by priority')
    list_parser.add_argument('--status', help='Filter by download status')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update resource metadata')
    update_parser.add_argument('resource_id', help='Resource ID (e.g., RES-001)')
    update_parser.add_argument('--version', help='Update version number')
    update_parser.add_argument('--downloaded', action='store_true', help='Mark as downloaded today')
    update_parser.add_argument('--processed', action='store_true', help='Mark as processed')
    update_parser.add_argument('--indexed', action='store_true', help='Mark as indexed')
    update_parser.add_argument('--citation-validated', action='store_true', help='Mark as citation validated')
    update_parser.add_argument('--next-check-date', help='Set next check date (YYYY-MM-DD)')

    # Status command
    status_parser = subparsers.add_parser('status', help='Generate status report')

    # Check updates command
    check_parser = subparsers.add_parser('check-updates', help='Check which resources need updates')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export database to CSV')
    export_parser.add_argument('--output', default='resources.csv', help='Output CSV file path')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Initialize database manager
    try:
        manager = ResourceDatabaseManager()
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        return 1

    # Execute command
    if args.command == 'list':
        manager.list_resources(filter_priority=args.priority, filter_status=args.status)

    elif args.command == 'update':
        kwargs = {}
        if args.version:
            kwargs['version'] = args.version
        if args.downloaded:
            kwargs['downloaded'] = True
        if args.processed:
            kwargs['processed'] = True
        if args.indexed:
            kwargs['indexed'] = True
        if args.citation_validated:
            kwargs['citation_validated'] = True
        if args.next_check_date:
            kwargs['next_check_date'] = args.next_check_date

        manager.update_resource(args.resource_id, **kwargs)

    elif args.command == 'status':
        manager.generate_status_report()

    elif args.command == 'check-updates':
        manager.check_updates_needed()

    elif args.command == 'export':
        output_path = Path(args.output)
        manager.export_csv(output_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
