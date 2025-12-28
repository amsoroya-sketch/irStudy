#!/usr/bin/env python3
"""
Process citations.json and add citations to medical claims.
Focuses on first 100 CRITICAL severity claims.
"""

import json
import os
from pathlib import Path

# Read citations.json
citations_file = Path("/home/dev/Development/irStudy/validation_reports/citations.json")
with open(citations_file, 'r') as f:
    all_claims = json.load(f)

# Filter for CRITICAL severity only
critical_claims = [c for c in all_claims if c.get('severity') == 'critical']

print(f"Total claims in file: {len(all_claims)}")
print(f"CRITICAL severity claims: {len(critical_claims)}")
print(f"\nProcessing first 100 CRITICAL claims...")

# Take first 100 critical claims
claims_to_process = critical_claims[:100]

# Group by file for efficient processing
claims_by_file = {}
for claim in claims_to_process:
    file_path = claim['file']
    if file_path not in claims_by_file:
        claims_by_file[file_path] = []
    claims_by_file[file_path].append(claim)

print(f"\nClaims grouped into {len(claims_by_file)} files")
print("\nFiles to modify:")
for file_path, claims in claims_by_file.items():
    print(f"  {file_path}: {len(claims)} claims")

# Save this working set for reference
output = {
    'total_claims': len(all_claims),
    'critical_claims': len(critical_claims),
    'processing_count': len(claims_to_process),
    'files_to_modify': len(claims_by_file),
    'claims_by_file': claims_by_file
}

with open('/home/dev/Development/irStudy/citation_work_batch.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nWork batch saved to: citation_work_batch.json")
