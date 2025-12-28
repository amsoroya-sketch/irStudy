#!/usr/bin/env python3
import json

with open('/home/dev/Development/irStudy/validation_reports/citations.json', 'r') as f:
    claims = json.load(f)

# Get first 20 CRITICAL claims for manual processing
critical = [c for c in claims if c.get('severity') == 'critical'][:20]

print(f"Total claims: {len(claims)}")
print(f"Total critical: {len([c for c in claims if c.get('severity') == 'critical'])}")
print(f"\nFirst 20 CRITICAL claims for manual processing:\n")

for i, claim in enumerate(critical, 1):
    print(f"{i}. FILE: {claim['file']}")
    print(f"   LINE: {claim['line']}")
    print(f"   CLAIM: {claim['claim'][:120]}")
    print()
