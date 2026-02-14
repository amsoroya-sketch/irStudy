#!/usr/bin/env python3
"""
Extract cookies from Firefox for Cochrane Library

Reads Firefox's cookies.sqlite database and exports cookies
in Netscape format for use with wget/curl.
"""

import sqlite3
import os
from pathlib import Path
import shutil

def find_firefox_profile():
    """Find Firefox profile directory"""
    firefox_dir = Path.home() / '.mozilla' / 'firefox'

    if not firefox_dir.exists():
        print(f"Firefox directory not found: {firefox_dir}")
        return None

    # Look for default profile
    profiles = list(firefox_dir.glob('*.default*'))

    if not profiles:
        # Try to find any profile
        profiles = [p for p in firefox_dir.iterdir() if p.is_dir() and not p.name.startswith('.')]

    if profiles:
        return profiles[0]

    return None

def extract_cookies(profile_dir: Path, output_file: Path, domain: str = 'cochranelibrary.com'):
    """Extract cookies from Firefox database"""

    cookies_db = profile_dir / 'cookies.sqlite'

    if not cookies_db.exists():
        print(f"Cookies database not found: {cookies_db}")
        return False

    # Copy database to temp location (Firefox might have it locked)
    temp_db = Path('/tmp/cookies_temp.sqlite')
    shutil.copy2(cookies_db, temp_db)

    try:
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()

        # Query cookies for Cochrane Library
        cursor.execute("""
            SELECT host, name, value, path, expiry, isSecure
            FROM moz_cookies
            WHERE host LIKE ?
        """, (f'%{domain}%',))

        cookies = cursor.fetchall()

        if not cookies:
            print(f"No cookies found for {domain}")
            conn.close()
            return False

        # Write cookies in Netscape format
        with open(output_file, 'w') as f:
            f.write("# Netscape HTTP Cookie File\n")
            f.write("# This is a generated file! Do not edit.\n\n")

            for host, name, value, path, expiry, is_secure in cookies:
                # Netscape format:
                # domain  flag  path  secure  expiration  name  value
                domain_flag = 'TRUE' if host.startswith('.') else 'FALSE'
                secure_flag = 'TRUE' if is_secure else 'FALSE'

                f.write(f"{host}\t{domain_flag}\t{path}\t{secure_flag}\t{expiry}\t{name}\t{value}\n")

        conn.close()

        print(f"✓ Extracted {len(cookies)} cookies for {domain}")
        print(f"✓ Saved to: {output_file}")
        return True

    except Exception as e:
        print(f"Error extracting cookies: {e}")
        return False

    finally:
        if temp_db.exists():
            temp_db.unlink()

def main():
    print("Firefox Cookie Extractor")
    print("=" * 50)

    # Find Firefox profile
    profile = find_firefox_profile()

    if not profile:
        print("✗ Could not find Firefox profile")
        print("\nPlease close Firefox and try again, or specify profile manually.")
        return 1

    print(f"✓ Found Firefox profile: {profile.name}")

    # Extract cookies
    output_file = Path.home() / 'Downloads' / 'cochrane_cookies.txt'

    success = extract_cookies(profile, output_file, domain='cochranelibrary.com')

    if success:
        print("\n" + "=" * 50)
        print("SUCCESS! Cookies exported.")
        print("=" * 50)
        print(f"\nNow run:")
        print(f"python3 scripts/download_cochrane_with_cookies.py \\")
        print(f"  --input ~/Downloads/citation-export\\(2\\).txt \\")
        print(f"  --cookies {output_file} \\")
        print(f"  --output ~/cochrane_downloads \\")
        print(f"  --limit 5")
        return 0
    else:
        print("\n✗ Failed to extract cookies")
        print("\nTroubleshooting:")
        print("1. Close Firefox completely")
        print("2. Make sure you're logged into Cochrane Library in Firefox")
        print("3. Try running this script again")
        return 1

if __name__ == '__main__':
    exit(main())
