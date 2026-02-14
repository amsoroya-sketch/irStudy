#!/usr/bin/env python3
"""
Resource Update Checker

Automatically checks for updates to medical resources by:
- Querying APIs (StatPearls, Cochrane, etc.)
- Checking HTTP headers for Last-Modified dates
- Scraping version information from websites
- Comparing with database records

Usage:
    python3 scripts/check_resource_updates.py --all
    python3 scripts/check_resource_updates.py --resource RES-001
    python3 scripts/check_resource_updates.py --priority HIGH
"""

import argparse
import json
import sys
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List
import time

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_JSON = PROJECT_ROOT / "resource_database.json"


class ResourceUpdateChecker:
    """Checks for updates to medical resources"""

    def __init__(self, database_path: Path = DATABASE_JSON):
        self.database_path = database_path
        self.data = self._load_database()
        self.update_results = []

    def _load_database(self) -> Dict:
        """Load the JSON database"""
        with open(self.database_path, 'r') as f:
            return json.load(f)

    def check_all_updates(self, priority_filter: Optional[str] = None):
        """Check all resources for updates"""
        print("\n" + "="*80)
        print("CHECKING FOR RESOURCE UPDATES")
        print("="*80)
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        resources_to_check = self.data['resources']
        if priority_filter:
            resources_to_check = [
                r for r in resources_to_check
                if r['priority'] == priority_filter.upper()
            ]

        for idx, resource in enumerate(resources_to_check, 1):
            print(f"\n[{idx}/{len(resources_to_check)}] Checking: {resource['name']} ({resource['id']})")
            print("-" * 80)

            result = self.check_resource_update(resource)
            self.update_results.append(result)

            # Small delay to avoid rate limiting
            time.sleep(1)

        self._print_summary()

    def check_resource_update(self, resource: Dict) -> Dict:
        """Check a single resource for updates"""
        result = {
            'resource_id': resource['id'],
            'resource_name': resource['name'],
            'current_version': resource['version']['current'],
            'current_release_date': resource['version']['latest_release_date'],
            'check_date': datetime.now().strftime('%Y-%m-%d'),
            'update_available': False,
            'new_version': None,
            'new_release_date': None,
            'check_method': None,
            'error': None
        }

        # Different check methods based on resource type
        resource_id = resource['id']

        try:
            if resource_id == 'RES-001':  # StatPearls
                self._check_statpearls(resource, result)

            elif resource_id == 'RES-002':  # Cochrane
                self._check_cochrane(resource, result)

            elif resource_id == 'RES-003':  # RACGP Red Book
                self._check_racgp(resource, result)

            elif resource_id == 'RES-004':  # RANZCOG
                self._check_ranzcog(resource, result)

            elif resource_id == 'RES-005':  # RANZCP
                self._check_ranzcp(resource, result)

            elif resource_id == 'RES-006':  # MeSH
                self._check_mesh(resource, result)

            elif resource_id == 'RES-007':  # Immunisation Handbook
                self._check_immunisation_handbook(resource, result)

            elif resource_id == 'RES-008':  # Stroke Guidelines
                self._check_stroke_guidelines(resource, result)

            elif resource_id == 'RES-009':  # NSW Health
                self._check_nsw_health(resource, result)

            else:
                result['check_method'] = 'manual'
                print(f"   ℹ️  Manual check required - automated checking not available")

        except Exception as e:
            result['error'] = str(e)
            print(f"   ❌ Error: {e}")

        return result

    def _check_statpearls(self, resource: Dict, result: Dict):
        """Check StatPearls for updates via NCBI API"""
        result['check_method'] = 'NCBI E-utilities API'

        # Check if StatPearls database has been updated
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        params = {
            'db': 'books',
            'id': 'NBK430685',  # StatPearls main book ID
            'retmode': 'json'
        }

        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        if 'result' in data and 'NBK430685' in data['result']:
            book_info = data['result']['NBK430685']
            last_update = book_info.get('lastUpdate', '')

            if last_update:
                result['new_release_date'] = last_update
                result['new_version'] = f"Updated {last_update}"

                if last_update > resource['version']['latest_release_date']:
                    result['update_available'] = True
                    print(f"   ✅ Update available! New release: {last_update}")
                else:
                    print(f"   ✓  Up to date (last release: {last_update})")
            else:
                print(f"   ⚠️  Could not determine last update date")

    def _check_http_last_modified(self, url: str, resource: Dict, result: Dict):
        """Generic check using HTTP Last-Modified header"""
        result['check_method'] = 'HTTP Last-Modified header'

        response = requests.head(url, timeout=30, allow_redirects=True)
        last_modified = response.headers.get('Last-Modified')

        if last_modified:
            # Parse Last-Modified header
            last_mod_date = datetime.strptime(
                last_modified, '%a, %d %b %Y %H:%M:%S %Z'
            ).strftime('%Y-%m-%d')

            result['new_release_date'] = last_mod_date

            if last_mod_date > resource['version']['latest_release_date']:
                result['update_available'] = True
                print(f"   ✅ Update available! Last modified: {last_mod_date}")
            else:
                print(f"   ✓  Up to date (last modified: {last_mod_date})")
        else:
            print(f"   ⚠️  No Last-Modified header found")

    def _check_cochrane(self, resource: Dict, result: Dict):
        """Check Cochrane Library for new reviews"""
        result['check_method'] = 'Cochrane website check'
        print(f"   ℹ️  Manual check recommended: Visit https://www.cochranelibrary.com/")
        print(f"   Current version: {resource['version']['current']}")
        print(f"   Last release: {resource['version']['latest_release_date']}")

    def _check_racgp(self, resource: Dict, result: Dict):
        """Check RACGP Red Book for updates"""
        url = "https://www.racgp.org.au/clinical-resources/clinical-guidelines/key-racgp-guidelines/view-all-racgp-guidelines/red-book"
        try:
            self._check_http_last_modified(url, resource, result)
        except:
            result['check_method'] = 'manual'
            print(f"   ℹ️  Manual check recommended: {url}")

    def _check_ranzcog(self, resource: Dict, result: Dict):
        """Check RANZCOG for new statements"""
        result['check_method'] = 'RANZCOG website check'
        print(f"   ℹ️  Manual check recommended: Visit https://ranzcog.edu.au/statements-guidelines")
        print(f"   Check for statements updated after: {resource['version']['latest_release_date']}")

    def _check_ranzcp(self, resource: Dict, result: Dict):
        """Check RANZCP for guideline updates"""
        result['check_method'] = 'RANZCP website check'
        print(f"   ℹ️  Manual check recommended: Visit https://www.ranzcp.org/clinical-guidelines-publications")
        print(f"   Check for guidelines updated after: {resource['version']['latest_release_date']}")

    def _check_mesh(self, resource: Dict, result: Dict):
        """Check MeSH for new release"""
        url = "https://nlmpubs.nlm.nih.gov/projects/mesh/MESH_FILES/meshtrees/mtrees2026.bin"
        try:
            self._check_http_last_modified(url, resource, result)
        except:
            result['check_method'] = 'manual'
            print(f"   ℹ️  MeSH releases annually in December")
            print(f"   Current: {resource['version']['current']}")
            print(f"   Next expected: {resource['version'].get('next_expected_release', 'N/A')}")

    def _check_immunisation_handbook(self, resource: Dict, result: Dict):
        """Check Australian Immunisation Handbook"""
        url = "https://immunisationhandbook.health.gov.au/"
        result['check_method'] = 'Website check'
        print(f"   ℹ️  Manual check recommended: {url}")
        print(f"   Current version: {resource['version']['current']}")
        print(f"   Last update: {resource['version']['latest_release_date']}")

    def _check_stroke_guidelines(self, resource: Dict, result: Dict):
        """Check Stroke Foundation Guidelines (Living Guidelines)"""
        url = "https://informme.org.au/guidelines/clinical-guidelines-for-stroke-management"
        result['check_method'] = 'Living guidelines - continuous updates'
        print(f"   ℹ️  Living guidelines updated continuously")
        print(f"   Manual check recommended: {url}")
        print(f"   Last checked: {resource['version']['latest_release_date']}")

    def _check_nsw_health(self, resource: Dict, result: Dict):
        """Check NSW Health for new policies"""
        result['check_method'] = 'NSW Health policy database'
        print(f"   ℹ️  Manual check recommended: Visit https://www.health.nsw.gov.au/policies/")
        print(f"   Check for policies released after: {resource['version']['latest_release_date']}")

    def _print_summary(self):
        """Print summary of update checks"""
        print("\n" + "="*80)
        print("UPDATE CHECK SUMMARY")
        print("="*80)

        updates_available = [r for r in self.update_results if r['update_available']]
        manual_checks = [r for r in self.update_results if r['check_method'] == 'manual']
        errors = [r for r in self.update_results if r['error']]

        print(f"\nTotal Checked: {len(self.update_results)}")
        print(f"✅ Updates Available: {len(updates_available)}")
        print(f"ℹ️  Manual Checks Required: {len(manual_checks)}")
        print(f"❌ Errors: {len(errors)}")

        if updates_available:
            print("\n📦 UPDATES AVAILABLE:")
            for result in updates_available:
                print(f"\n   {result['resource_id']}: {result['resource_name']}")
                print(f"   Current: {result['current_version']} ({result['current_release_date']})")
                print(f"   New: {result.get('new_version', 'Unknown')} ({result.get('new_release_date', 'Unknown')})")

        if errors:
            print("\n❌ ERRORS:")
            for result in errors:
                print(f"\n   {result['resource_id']}: {result['resource_name']}")
                print(f"   Error: {result['error']}")

        print("\n" + "="*80)

    def save_check_results(self, output_path: Path):
        """Save check results to JSON file"""
        output_data = {
            'check_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_checked': len(self.update_results),
            'updates_available': sum(1 for r in self.update_results if r['update_available']),
            'results': self.update_results
        }

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\n✅ Results saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Check medical resources for updates",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Check all resources for updates'
    )

    parser.add_argument(
        '--resource',
        help='Check specific resource by ID (e.g., RES-001)'
    )

    parser.add_argument(
        '--priority',
        choices=['HIGH', 'MEDIUM', 'LOW'],
        help='Check only resources with specific priority'
    )

    parser.add_argument(
        '--output',
        help='Save results to JSON file'
    )

    args = parser.parse_args()

    if not (args.all or args.resource or args.priority):
        parser.print_help()
        return 1

    checker = ResourceUpdateChecker()

    if args.resource:
        # Check single resource
        resource = None
        for r in checker.data['resources']:
            if r['id'] == args.resource:
                resource = r
                break

        if not resource:
            print(f"❌ Resource not found: {args.resource}")
            return 1

        print(f"\nChecking: {resource['name']} ({resource['id']})")
        print("-" * 80)
        result = checker.check_resource_update(resource)
        checker.update_results.append(result)

    else:
        # Check all or filtered resources
        checker.check_all_updates(priority_filter=args.priority)

    if args.output:
        output_path = Path(args.output)
        checker.save_check_results(output_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
