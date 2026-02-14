#!/usr/bin/env python3
import json

# Quick check of citations.json structure
with open("/home/dev/Development/irStudy/validation_reports/citations.json", "r") as f:
    claims = json.load(f)

print(f"Total claims: {len(claims)}")

# Show first 5 claims to understand structure
print("\nFirst 5 claims:")
for i, claim in enumerate(claims[:5], 1):
    print(f"\n{i}. File: {claim.get('file', 'N/A')}")
    print(f"   Line: {claim.get('line', 'N/A')}")
    print(f"   Severity: {claim.get('severity', 'N/A')}")
    print(f"   Claim: {claim.get('claim', 'N/A')[:100]}...")

# Count by severity
severities = {}
for claim in claims:
    sev = claim.get("severity", "unknown")
    severities[sev] = severities.get(sev, 0) + 1

print(f"\nClaims by severity:")
for sev, count in sorted(severities.items()):
    print(f"  {sev}: {count}")
