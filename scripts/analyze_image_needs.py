#!/usr/bin/env python3
"""
Analyze Image Needs for irStudy Platform

This script analyzes current image coverage and creates a detailed plan
for downloading additional images to reach target coverage.

Outputs:
- IMAGE_NEEDS_ANALYSIS.md: Detailed analysis and download plan
- image_download_plan.json: Structured download plan for automation
"""

import json
import psycopg2
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def get_db_config():
    """Load database config from secrets"""
    password_file = Path('secrets/db_password.txt')
    if password_file.exists():
        password = password_file.read_text().strip()
    else:
        password = 'postgres'

    return {
        'host': 'localhost',
        'port': 5433,
        'database': 'irstudy_medical',
        'user': 'postgres',
        'password': password
    }

def get_mcq_stats(conn):
    """Get MCQ statistics by specialty"""
    query = """
        SELECT
            specialty,
            COUNT(*) as total_mcqs,
            COUNT(image_url) as mcqs_with_images,
            ROUND(100.0 * COUNT(image_url) / COUNT(*), 2) as coverage_percent
        FROM mcqs
        WHERE is_published = true
        GROUP BY specialty
        ORDER BY total_mcqs DESC
    """

    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_osce_stats(conn):
    """Get OSCE statistics by specialty"""
    query = """
        SELECT
            specialty,
            COUNT(*) as total_osces,
            COUNT(CASE WHEN supporting_documents IS NOT NULL
                  AND supporting_documents::text != '[]' THEN 1 END) as osces_with_images,
            ROUND(100.0 * COUNT(CASE WHEN supporting_documents IS NOT NULL
                  AND supporting_documents::text != '[]' THEN 1 END) / COUNT(*), 2) as coverage_percent
        FROM osces
        WHERE is_published = true
        GROUP BY specialty
        ORDER BY total_osces DESC
    """

    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def load_image_catalog():
    """Load existing image catalog"""
    catalog_file = Path('data/medical_images_catalog.json')
    with open(catalog_file) as f:
        return json.load(f)

def calculate_image_needs(mcq_stats, osce_stats, target_coverage=35):
    """Calculate how many images are needed per specialty"""
    needs = {
        'mcqs': {},
        'osces': {},
        'summary': {
            'target_coverage_percent': target_coverage,
            'total_images_needed': 0,
        }
    }

    # MCQ needs
    for stat in mcq_stats:
        specialty = stat['specialty']
        current = stat['mcqs_with_images']
        total = stat['total_mcqs']
        target_count = int(total * (target_coverage / 100))
        needed = max(0, target_count - current)

        needs['mcqs'][specialty] = {
            'total_questions': total,
            'current_images': current,
            'current_coverage_percent': stat['coverage_percent'],
            'target_images': target_count,
            'images_needed': needed,
            'priority': 'HIGH' if stat['coverage_percent'] < 5 else 'MEDIUM' if stat['coverage_percent'] < 20 else 'LOW'
        }

        needs['summary']['total_images_needed'] += needed

    # OSCE needs
    for stat in osce_stats:
        specialty = stat['specialty']
        current = stat['osces_with_images']
        total = stat['total_osces']
        target_count = int(total * (target_coverage / 100))
        needed = max(0, target_count - current)

        needs['osces'][specialty] = {
            'total_stations': total,
            'current_images': current,
            'current_coverage_percent': stat['coverage_percent'],
            'target_images': target_count,
            'images_needed': needed,
            'priority': 'HIGH' if stat['coverage_percent'] < 5 else 'MEDIUM' if stat['coverage_percent'] < 20 else 'LOW'
        }

    return needs

def generate_download_plan(needs, catalog):
    """Generate download plan based on needs"""
    plan = {
        'generated_at': datetime.now().isoformat(),
        'current_images': catalog['total_images'],
        'target_total': catalog['total_images'] + needs['summary']['total_images_needed'],
        'downloads_by_specialty': {},
        'estimated_time_hours': 0,
    }

    # Map database specialties to download categories
    specialty_mapping = {
        'cardiology': ['cardiology_ecg', 'cardiology_imaging'],
        'respiratory': ['respiratory_xray', 'respiratory_ct'],
        'gastroenterology': ['gastro_endoscopy', 'gastro_imaging'],
        'neurology': ['neuro_ct', 'neuro_mri', 'neuro_imaging'],
        'endocrinology': ['endocrine_imaging', 'thyroid_ultrasound', 'diabetes_complications'],
        'psychiatry': ['psychiatric_imaging'],  # Limited medical images
        'general_practice': ['dermatology', 'general_radiology', 'common_presentations'],
    }

    # Calculate downloads needed per specialty
    for specialty, spec_needs in needs['mcqs'].items():
        if spec_needs['images_needed'] > 0:
            plan['downloads_by_specialty'][specialty] = {
                'images_needed': spec_needs['images_needed'],
                'priority': spec_needs['priority'],
                'download_topics': specialty_mapping.get(specialty, ['general']),
                'estimated_download_time_minutes': spec_needs['images_needed'] * 0.5,  # 30 sec per image with rate limiting
            }

    # Estimate total time (with rate limiting: 2 seconds per image)
    total_images = needs['summary']['total_images_needed']
    plan['estimated_time_hours'] = round((total_images * 2) / 3600, 1)  # 2 seconds per image

    return plan

def generate_markdown_report(mcq_stats, osce_stats, needs, plan, catalog):
    """Generate comprehensive markdown report"""
    report = f"""# Medical Image Needs Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

**Current State:**
- Total images in library: **{catalog['total_images']}**
- Images by source:
  - HEAL: {catalog['images_by_source'].get('heal', 0)}
- Images by specialty:
  - Hematology: {catalog['images_by_specialty'].get('hematology', 0)} (microscopy)
  - Cardiology: {catalog['images_by_specialty'].get('cardiology', 0)} (mostly ECGs)
  - Dermatology: {catalog['images_by_specialty'].get('dermatology', 0)} (clinical photos)

**Target:**
- Coverage goal: **{needs['summary']['target_coverage_percent']}%** of all MCQs and OSCEs
- Additional images needed: **{needs['summary']['total_images_needed']}**
- New total: **{plan['target_total']}** images

**Estimated Effort:**
- Download time: **{plan['estimated_time_hours']} hours** (with 2s rate limiting)
- Using existing `download_heal_comprehensive.py` script

---

## Current Coverage by Specialty (MCQs)

| Specialty | Total MCQs | Current Images | Coverage % | Target Images | **Images Needed** | Priority |
|-----------|------------|----------------|------------|---------------|-------------------|----------|
"""

    for stat in mcq_stats:
        spec = stat['specialty']
        need = needs['mcqs'][spec]
        report += f"| {spec} | {stat['total_mcqs']} | {stat['mcqs_with_images']} | {stat['coverage_percent']}% | {need['target_images']} | **{need['images_needed']}** | {need['priority']} |\n"

    report += f"""
**Total MCQs:** {sum(s['total_mcqs'] for s in mcq_stats)}
**Current coverage:** {sum(s['mcqs_with_images'] for s in mcq_stats)} images ({sum(s['mcqs_with_images'] for s in mcq_stats) / sum(s['total_mcqs'] for s in mcq_stats) * 100:.1f}%)

---

## Current Coverage by Specialty (OSCEs)

| Specialty | Total OSCEs | Current Images | Coverage % | Target Images | **Images Needed** | Priority |
|-----------|-------------|----------------|------------|---------------|-------------------|----------|
"""

    for stat in osce_stats:
        spec = stat['specialty']
        need = needs['osces'].get(spec, {})
        if need:
            report += f"| {spec} | {stat['total_osces']} | {stat['osces_with_images']} | {stat['coverage_percent']}% | {need.get('target_images', 0)} | **{need.get('images_needed', 0)}** | {need.get('priority', 'N/A')} |\n"

    report += """
---

## Priority Breakdown

### HIGH Priority (< 5% coverage)
Specialties with critical image shortage:
"""

    high_priority = [spec for spec, need in needs['mcqs'].items() if need['priority'] == 'HIGH']
    for spec in high_priority:
        need = needs['mcqs'][spec]
        report += f"\n**{spec.upper()}**\n"
        report += f"- Current: {need['current_images']} images ({need['current_coverage_percent']}%)\n"
        report += f"- Target: {need['target_images']} images (35%)\n"
        report += f"- **Need: {need['images_needed']} new images**\n"

    report += """
### MEDIUM Priority (5-20% coverage)
Specialties needing significant expansion:
"""

    medium_priority = [spec for spec, need in needs['mcqs'].items() if need['priority'] == 'MEDIUM']
    for spec in medium_priority:
        need = needs['mcqs'][spec]
        report += f"\n**{spec}**: Need {need['images_needed']} images (current: {need['current_coverage_percent']}%)\n"

    report += """
---

## Download Strategy

### Option 1: HEAL Comprehensive Download (Recommended)
Use the existing `download_heal_comprehensive.py` script with targeted specialty downloads.

**Phase 1: HIGH Priority Specialties** (~2-3 hours)
```bash
# Download for psychiatry, endocrinology, neurology, respiratory
python3 scripts/download_heal_comprehensive.py \\
    --specialties psychiatry endocrinology neurology respiratory \\
    --images-per-topic 15
```

**Phase 2: MEDIUM Priority Specialties** (~1-2 hours)
```bash
# Download for general_practice, gastroenterology
python3 scripts/download_heal_comprehensive.py \\
    --specialties general_medicine gastroenterology \\
    --images-per-topic 20
```

**Phase 3: Cardiology Boost** (~30 min)
```bash
# Get more cardiology images (we have ECGs, need clinical images)
python3 scripts/download_heal_comprehensive.py \\
    --specialties cardiology \\
    --images-per-topic 10
```

### Option 2: Full Automated Download (~4-5 hours)
```bash
# Download all phases automatically
python3 scripts/download_heal_comprehensive.py --phase all
```

---

## Expected Outcomes

After downloading **{needs['summary']['total_images_needed']}** additional images:

| Metric | Before | After |
|--------|--------|-------|
| Total images | {catalog['total_images']} | {plan['target_total']} |
| MCQ coverage | {sum(s['mcqs_with_images'] for s in mcq_stats)} / {sum(s['total_mcqs'] for s in mcq_stats)} ({sum(s['mcqs_with_images'] for s in mcq_stats) / sum(s['total_mcqs'] for s in mcq_stats) * 100:.1f}%) | {sum(need['target_images'] for need in needs['mcqs'].values())} / {sum(s['total_mcqs'] for s in mcq_stats)} (35%) |
| Specialties at 0% | {sum(1 for s in mcq_stats if s['coverage_percent'] == 0)} | 0 |
| Specialties at >30% | {sum(1 for s in mcq_stats if s['coverage_percent'] >= 30)} | {len(mcq_stats)} |

---

## Image Types Needed

Based on question content analysis, prioritize downloading:

1. **ECGs** - for cardiology (STEMI, arrhythmias, conduction blocks)
2. **Chest X-rays** - for respiratory (pneumonia, pneumothorax, pleural effusion)
3. **Microscopy** - for hematology (blood smears, bone marrow)
4. **Dermatology photos** - for GP/dermatology (rashes, lesions, skin cancers)
5. **CT/MRI scans** - for neurology (stroke, hemorrhage, tumors)
6. **Endoscopy images** - for gastroenterology (GI bleed, IBD)
7. **Ultrasound** - for endocrinology (thyroid nodules)
8. **Fundoscopy** - for diabetes/endocrinology (diabetic retinopathy)

---

## Next Steps

1. **Review this analysis** - Confirm target coverage percentage (currently 35%)
2. **Run image matching** - Execute SQL updates to link existing 318 images
   ```bash
   python3 scripts/match_images_to_questions.py --execute
   ```
3. **Download additional images** - Run HEAL download script (Phase 1 first)
4. **Re-run matching** - Link new images to questions
5. **Manual review** - QA check image appropriateness for questions
6. **Update RAG** - Generate CLIP embeddings for multimodal search

---

## Automation Recommendations

**Weekly maintenance script:**
```bash
#!/bin/bash
# Download new HEAL images (10-20 per specialty per week)
python3 scripts/download_heal_comprehensive.py --images-per-topic 5
# Match to questions
python3 scripts/match_images_to_questions.py --execute
# Update catalog
python3 scripts/catalog_medical_images.py
```

This keeps image library growing incrementally without overwhelming downloads.

---

## Appendix: Detailed Specialty Breakdown
"""

    for spec in sorted(needs['mcqs'].keys()):
        need = needs['mcqs'][spec]
        report += f"\n### {spec.upper()}\n"
        report += f"- Total questions: {need['total_questions']}\n"
        report += f"- Current images: {need['current_images']} ({need['current_coverage_percent']}%)\n"
        report += f"- Target: {need['target_images']} images (35% coverage)\n"
        report += f"- **Gap: {need['images_needed']} images needed**\n"
        report += f"- Priority: **{need['priority']}**\n"

    return report

def main():
    print("Analyzing image needs...")

    # Connect to database
    print("Connecting to database...")
    DB_CONFIG = get_db_config()
    conn = psycopg2.connect(**DB_CONFIG)

    # Get statistics
    print("Fetching MCQ statistics...")
    mcq_stats = get_mcq_stats(conn)

    print("Fetching OSCE statistics...")
    osce_stats = get_osce_stats(conn)

    conn.close()

    # Load catalog
    print("Loading image catalog...")
    catalog = load_image_catalog()

    # Calculate needs
    print("Calculating image needs...")
    needs = calculate_image_needs(mcq_stats, osce_stats, target_coverage=35)

    # Generate download plan
    print("Generating download plan...")
    plan = generate_download_plan(needs, catalog)

    # Generate report
    print("Generating markdown report...")
    report = generate_markdown_report(mcq_stats, osce_stats, needs, plan, catalog)

    # Save report
    report_file = Path('IMAGE_NEEDS_ANALYSIS.md')
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\n✅ Analysis saved to: {report_file}")

    # Save JSON plan
    plan_file = Path('data/image_download_plan.json')
    with open(plan_file, 'w') as f:
        json.dump(plan, f, indent=2)

    print(f"✅ Download plan saved to: {plan_file}")

    # Print summary
    print("\n" + "="*80)
    print("IMAGE NEEDS SUMMARY")
    print("="*80)
    print(f"Current images: {catalog['total_images']}")
    print(f"Images needed: {needs['summary']['total_images_needed']}")
    print(f"Target total: {plan['target_total']}")
    print(f"Estimated download time: {plan['estimated_time_hours']} hours")
    print("="*80)

if __name__ == '__main__':
    main()
