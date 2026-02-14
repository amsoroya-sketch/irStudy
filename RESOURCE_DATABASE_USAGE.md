# Resource Database Usage Guide

## Overview

The Medical Resources Database system provides comprehensive tracking and management of all downloadable medical resources for ICRP study preparation.

## Files

1. **RESOURCE_DATABASE.md** - Human-readable markdown documentation
2. **resource_database.json** - Machine-readable JSON database
3. **scripts/manage_resource_database.py** - Database management tool
4. **scripts/check_resource_updates.py** - Automated update checker

---

## Quick Start

### 1. View All Resources

```bash
python3 scripts/manage_resource_database.py list
```

### 2. Filter by Priority

```bash
# Show only HIGH priority resources
python3 scripts/manage_resource_database.py list --priority HIGH

# Show only MEDIUM priority resources
python3 scripts/manage_resource_database.py list --priority MEDIUM
```

### 3. Generate Status Report

```bash
python3 scripts/manage_resource_database.py status
```

### 4. Check for Updates

```bash
# Check all resources
python3 scripts/check_resource_updates.py --all

# Check only HIGH priority resources
python3 scripts/check_resource_updates.py --priority HIGH

# Check specific resource
python3 scripts/check_resource_updates.py --resource RES-001
```

---

## Database Management

### Update Resource After Download

When you download a resource, update the database:

```bash
python3 scripts/manage_resource_database.py update RES-001 --downloaded
```

### Update Version Information

```bash
python3 scripts/manage_resource_database.py update RES-001 \
  --version "2026-01-20" \
  --downloaded
```

### Mark Resource as Processed

After processing PDFs and extracting text:

```bash
python3 scripts/manage_resource_database.py update RES-001 --processed
```

### Mark Resource as Indexed

After adding to vector database:

```bash
python3 scripts/manage_resource_database.py update RES-001 --indexed
```

### Complete Integration Workflow

```bash
python3 scripts/manage_resource_database.py update RES-001 \
  --downloaded \
  --processed \
  --indexed \
  --citation-validated
```

---

## Update Checking

### Check All Resources

```bash
python3 scripts/check_resource_updates.py --all
```

Sample output:
```
[1/12] Checking: StatPearls Publishing Database (RES-001)
--------------------------------------------------------------------------------
   ✅ Update available! New release: 2026-01-20

[2/12] Checking: Cochrane Systematic Reviews (RES-002)
--------------------------------------------------------------------------------
   ℹ️  Manual check recommended: Visit https://www.cochranelibrary.com/
```

### Save Update Check Results

```bash
python3 scripts/check_resource_updates.py --all --output update_check_results.json
```

### Check Resources Due for Updates

```bash
python3 scripts/manage_resource_database.py check-updates
```

Sample output:
```
RESOURCES REQUIRING UPDATE CHECKS
================================================================================

🔴 DUE TODAY
   ID: RES-001
   Name: StatPearls Publishing Database
   Current Version: Continuous
   Last Release: 2026-01-17
   Next Check: 2026-01-24
   Check Command: python3 scripts/check_statpearls_updates.py --last-check-date 2026-01-17

🟡 Due in 3 days
   ID: RES-002
   Name: Cochrane Systematic Reviews
   ...
```

---

## Export Database

### Export to CSV

```bash
python3 scripts/manage_resource_database.py export --output resources.csv
```

This creates a CSV file with all resource metadata for use in spreadsheets or other tools.

---

## Common Workflows

### Workflow 1: After Downloading a Resource

```bash
# 1. Update database to mark as downloaded
python3 scripts/manage_resource_database.py update RES-001 --downloaded

# 2. Check status
python3 scripts/manage_resource_database.py status
```

### Workflow 2: Weekly Maintenance

```bash
# 1. Check which resources need updates
python3 scripts/manage_resource_database.py check-updates

# 2. Run automated update checker
python3 scripts/check_resource_updates.py --all --output weekly_check.json

# 3. Generate status report
python3 scripts/manage_resource_database.py status
```

### Workflow 3: Complete Resource Integration

```bash
# After downloading StatPearls:
python3 scripts/manage_resource_database.py update RES-001 \
  --version "2026-01-20" \
  --downloaded

# After processing
python3 scripts/manage_resource_database.py update RES-001 --processed

# After indexing in vector database
python3 scripts/manage_resource_database.py update RES-001 --indexed

# After citation validation
python3 scripts/manage_resource_database.py update RES-001 --citation-validated

# Check final status
python3 scripts/manage_resource_database.py list | grep RES-001
```

---

## Database Fields Explanation

### Version Tracking

- **current**: Current version identifier
- **release_date**: Initial release date of current version
- **latest_release_date**: Most recent update/release date
- **release_frequency**: How often resource is updated
- **next_check_date**: When to check for next update
- **next_expected_release**: Expected date of next release

### Download Tracking

- **method**: Automated, Manual, or Approval required
- **status**: Current availability status
- **last_downloaded**: Date resource was last downloaded
- **download_duration_hours**: Estimated time to download

### Integration Tracking

- **processed**: PDF parsing and text extraction completed
- **indexed**: Added to vector database (Qdrant)
- **citation_validated**: Citations verified and working

---

## Resource IDs

| ID | Resource |
|----|----------|
| RES-001 | StatPearls Database |
| RES-002 | Cochrane Reviews |
| RES-003 | RACGP Red Book |
| RES-004 | RANZCOG Guidelines |
| RES-005 | RANZCP Guidelines |
| RES-006 | MeSH Database |
| RES-007 | Immunisation Handbook |
| RES-008 | Stroke Guidelines |
| RES-009 | NSW Health Protocols |
| RES-010 | Therapeutic Guidelines (eTG) |
| RES-011 | UMLS/SNOMED CT |
| RES-012 | MIMIC-III Database |

---

## Automation Schedule

### Weekly (Every Monday)
```bash
# Check StatPearls for updates
python3 scripts/check_resource_updates.py --resource RES-001
```

### Monthly (1st of month)
```bash
# Check all monthly resources
python3 scripts/check_resource_updates.py --all
```

### Quarterly
```bash
# Check quarterly resources (manual)
# RES-003 (RACGP), RES-005 (RANZCP), RES-007 (Immunisation)
```

### Annual
```bash
# Check MeSH in December
python3 scripts/check_resource_updates.py --resource RES-006
```

---

## Troubleshooting

### Database Not Found Error

```bash
# Verify database exists
ls -lh resource_database.json

# If missing, the database files are in the project root:
# /home/dev/Development/irStudy/resource_database.json
# /home/dev/Development/irStudy/RESOURCE_DATABASE.md
```

### Update Checker Fails

```bash
# Check internet connection
ping -c 3 google.com

# For NCBI API (StatPearls), ensure API key is set:
export NCBI_API_KEY='your_key_here'
```

### Permission Denied

```bash
# Make scripts executable
chmod +x scripts/manage_resource_database.py
chmod +x scripts/check_resource_updates.py
```

---

## Integration with Download Scripts

### Before Downloading

```bash
# Check current status
python3 scripts/manage_resource_database.py list --priority HIGH
```

### During Download

```bash
# Monitor progress manually, then update database
```

### After Download

```bash
# Update all downloaded resources
python3 scripts/manage_resource_database.py update RES-001 --downloaded
python3 scripts/manage_resource_database.py update RES-002 --downloaded
# etc.
```

---

## Advanced Usage

### Scripting with JSON Database

```python
import json

# Load database
with open('resource_database.json', 'r') as f:
    db = json.load(f)

# Get all HIGH priority resources
high_priority = [
    r for r in db['resources']
    if r['priority'] == 'HIGH'
]

# Get all automated resources
automated = [
    r['id'] for r in db['resources']
    if r['download']['method'] == 'Automated'
]
```

### Custom Reporting

```bash
# Export to CSV for analysis
python3 scripts/manage_resource_database.py export --output resources.csv

# Open in LibreOffice Calc or Excel for pivot tables
libreoffice resources.csv
```

---

## Next Steps

1. **Download Resources**: Use the download scripts with external disk
2. **Update Database**: Mark resources as downloaded
3. **Process Resources**: Extract text from PDFs
4. **Index Resources**: Add to Qdrant vector database
5. **Validate Citations**: Verify all citations work
6. **Regular Updates**: Run weekly/monthly update checks

---

**Last Updated:** 2026-01-17
**Version:** 1.0.0
