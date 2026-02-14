#!/usr/bin/env python3
"""
Add 'specialty' field to all MCQ JSON files for optimal image matching.

This script maps MCQ topics to medical specialties using comprehensive keyword matching,
enabling the image matching algorithm to correctly categorize MCQs.

Expected Impact:
- Match rate: 14.1% → 40-60% (3-4x improvement)
- Psychiatry: 0% → 50-65% (+400-520 matches)
- Cardiology: 19.0% → 35-45% (+259-422 matches)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple
import sys
from collections import defaultdict
import argparse

# Comprehensive topic-to-specialty mapping (case-insensitive exact matches)
TOPIC_TO_SPECIALTY_MAP = {
    # Psychiatry
    'depression': 'psychiatry',
    'major depressive disorder': 'psychiatry',
    'mdd': 'psychiatry',
    'anxiety': 'psychiatry',
    'gad': 'psychiatry',
    'panic disorder': 'psychiatry',
    'social anxiety': 'psychiatry',
    'psychosis': 'psychiatry',
    'schizophrenia': 'psychiatry',
    'bipolar': 'psychiatry',
    'bipolar disorder': 'psychiatry',
    'mania': 'psychiatry',
    'hypomania': 'psychiatry',
    'suicide risk': 'psychiatry',
    'suicidal ideation': 'psychiatry',
    'self-harm': 'psychiatry',
    'ptsd': 'psychiatry',
    'post-traumatic stress disorder': 'psychiatry',
    'ocd': 'psychiatry',
    'obsessive compulsive disorder': 'psychiatry',
    'eating disorders': 'psychiatry',
    'anorexia': 'psychiatry',
    'bulimia': 'psychiatry',
    'personality disorder': 'psychiatry',
    'borderline personality': 'psychiatry',
    'substance abuse': 'psychiatry',
    'alcohol dependence': 'psychiatry',
    'drug abuse': 'psychiatry',
    'addiction': 'psychiatry',
    'dementia': 'psychiatry',
    'alzheimer': 'psychiatry',
    'delirium': 'psychiatry',
    'mental health act': 'psychiatry',
    'mha': 'psychiatry',
    'psychotic disorders': 'psychiatry',
    'mood disorders': 'psychiatry',
    'arfid': 'psychiatry',
    'opioid': 'psychiatry',
    'opioid use disorder': 'psychiatry',
    'stimulant use disorder': 'psychiatry',
    'buprenorphine': 'psychiatry',
    'naltrexone': 'psychiatry',
    'dbt': 'psychiatry',
    'dialectical behaviour therapy': 'psychiatry',
    'antisocial personality': 'psychiatry',
    'adhd': 'psychiatry',
    'attention deficit': 'psychiatry',
    'autism': 'psychiatry',
    'autism spectrum': 'psychiatry',
    'asd': 'psychiatry',
    'intellectual disability': 'psychiatry',
    'sleep disorders': 'psychiatry',
    'insomnia': 'psychiatry',
    'sleep hygiene': 'psychiatry',
    'circadian rhythm': 'psychiatry',
    'somatoform': 'psychiatry',
    'somatoform disorders': 'psychiatry',
    'conversion disorder': 'psychiatry',
    'factitious disorder': 'psychiatry',
    'malingering': 'psychiatry',
    'somatization disorder': 'psychiatry',
    'somatization': 'psychiatry',
    'loneliness': 'psychiatry',
    'empty nest syndrome': 'psychiatry',
    'grief': 'psychiatry',
    'bereavement': 'psychiatry',
    'agoraphobia': 'psychiatry',
    'post-partum blues': 'psychiatry',
    'postpartum blues': 'psychiatry',

    # Cardiology
    'stemi': 'cardiology',
    'nstemi': 'cardiology',
    'mi': 'cardiology',
    'myocardial infarction': 'cardiology',
    'acs': 'cardiology',
    'acute coronary syndrome': 'cardiology',
    'angina': 'cardiology',
    'chest pain': 'cardiology',
    'atrial fibrillation': 'cardiology',
    'af': 'cardiology',
    'arrhythmia': 'cardiology',
    'bradycardia': 'cardiology',
    'tachycardia': 'cardiology',
    'svt': 'cardiology',
    'ventricular tachycardia': 'cardiology',
    'vt': 'cardiology',
    'heart failure': 'cardiology',
    'hf': 'cardiology',
    'chf': 'cardiology',
    'hypertension': 'cardiology',
    'htn': 'cardiology',
    'cardiomyopathy': 'cardiology',
    'dilated cardiomyopathy': 'cardiology',
    'hcm': 'cardiology',
    'valvular disease': 'cardiology',
    'mitral stenosis': 'cardiology',
    'mitral regurgitation': 'cardiology',
    'aortic stenosis': 'cardiology',
    'aortic regurgitation': 'cardiology',
    'pericarditis': 'cardiology',
    'endocarditis': 'cardiology',
    'myocarditis': 'cardiology',
    'aortic dissection': 'cardiology',
    'aortic aneurysm': 'cardiology',
    'peripheral vascular disease': 'cardiology',
    'pvd': 'cardiology',
    'lipids': 'cardiology',
    'hyperlipidemia': 'cardiology',
    'pericardial': 'cardiology',

    # Respiratory
    'pneumonia': 'respiratory',
    'cap': 'respiratory',
    'community-acquired pneumonia': 'respiratory',
    'copd': 'respiratory',
    'chronic obstructive pulmonary disease': 'respiratory',
    'asthma': 'respiratory',
    'pneumothorax': 'respiratory',
    'pe': 'respiratory',
    'pulmonary embolism': 'respiratory',
    'vte': 'respiratory',
    'dvt': 'respiratory',
    'tb': 'respiratory',
    'tuberculosis': 'respiratory',
    'bronchiectasis': 'respiratory',
    'ild': 'respiratory',
    'interstitial lung disease': 'respiratory',
    'ards': 'respiratory',
    'pleural effusion': 'respiratory',
    'lung cancer': 'respiratory',
    'bronchial carcinoma': 'respiratory',
    'atypical pneumonia': 'respiratory',
    'inhalers': 'respiratory',
    'biologics': 'respiratory',
    'thrombophilia': 'respiratory',
    'ventilation': 'respiratory',
    'pleural disease': 'respiratory',
    'sleep apnoea': 'respiratory',
    'sleep apnea': 'respiratory',
    'pulmonary function tests': 'respiratory',
    'pft': 'respiratory',
    'pneumoconiosis': 'respiratory',
    'cftr modulator': 'respiratory',
    'cystic fibrosis': 'respiratory',
    'omalizumab': 'respiratory',
    'hypersensitivity pneumonitis': 'respiratory',
    'sarcoidosis': 'respiratory',

    # Obstetrics & Gynaecology
    'pregnancy': 'obstetrics_gynaecology',
    'antenatal': 'obstetrics_gynaecology',
    'prenatal': 'obstetrics_gynaecology',
    'ectopic pregnancy': 'obstetrics_gynaecology',
    'miscarriage': 'obstetrics_gynaecology',
    'labour': 'obstetrics_gynaecology',
    'labor': 'obstetrics_gynaecology',
    'delivery': 'obstetrics_gynaecology',
    'postpartum': 'obstetrics_gynaecology',
    'placenta': 'obstetrics_gynaecology',
    'foetal': 'obstetrics_gynaecology',
    'fetal': 'obstetrics_gynaecology',
    'menstrual': 'obstetrics_gynaecology',
    'menstruation': 'obstetrics_gynaecology',
    'contraception': 'obstetrics_gynaecology',
    'menopause': 'obstetrics_gynaecology',
    'ovarian': 'obstetrics_gynaecology',
    'uterine': 'obstetrics_gynaecology',
    'cervical': 'obstetrics_gynaecology',
    'vaginal bleeding': 'obstetrics_gynaecology',
    'pelvic pain': 'obstetrics_gynaecology',
    'endometriosis': 'obstetrics_gynaecology',
    'pcos': 'obstetrics_gynaecology',

    # Paediatrics
    'neonatal': 'paediatrics',
    'infant': 'paediatrics',
    'child': 'paediatrics',
    'paediatric': 'paediatrics',
    'pediatric': 'paediatrics',
    'developmental': 'paediatrics',
    'vaccination': 'paediatrics',
    'immunisation': 'paediatrics',
    'immunization': 'paediatrics',
    'growth': 'paediatrics',
    'rickets': 'paediatrics',
    'newborn': 'paediatrics',

    # Neurology
    'stroke': 'neurology',
    'cva': 'neurology',
    'tia': 'neurology',
    'seizure': 'neurology',
    'epilepsy': 'neurology',
    'meningitis': 'neurology',
    'encephalitis': 'neurology',
    'multiple sclerosis': 'neurology',
    'ms': 'neurology',
    'parkinson': 'neurology',
    'headache': 'neurology',
    'migraine': 'neurology',
    'neuropathy': 'neurology',
    'guillain-barre': 'neurology',
    'myasthenia gravis': 'neurology',

    # Gastroenterology
    'gi bleeding': 'gastroenterology',
    'gastrointestinal bleeding': 'gastroenterology',
    'peptic ulcer': 'gastroenterology',
    'ibd': 'gastroenterology',
    'crohn': 'gastroenterology',
    'colitis': 'gastroenterology',
    'ulcerative colitis': 'gastroenterology',
    'cirrhosis': 'gastroenterology',
    'hepatitis': 'gastroenterology',
    'pancreatitis': 'gastroenterology',
    'cholecystitis': 'gastroenterology',
    'appendicitis': 'gastroenterology',
    'bowel obstruction': 'gastroenterology',
    'diarrhoea': 'gastroenterology',
    'diarrhea': 'gastroenterology',
    'constipation': 'gastroenterology',
    'dyspepsia': 'gastroenterology',
    'gord': 'gastroenterology',
    'gerd': 'gastroenterology',

    # Endocrinology
    'diabetes': 'endocrinology',
    'dm': 'endocrinology',
    'dka': 'endocrinology',
    'diabetic ketoacidosis': 'endocrinology',
    'thyroid': 'endocrinology',
    'hyperthyroidism': 'endocrinology',
    'hypothyroidism': 'endocrinology',
    'graves disease': 'endocrinology',
    'adrenal': 'endocrinology',
    'cushing': 'endocrinology',
    'addison': 'endocrinology',
    'pituitary': 'endocrinology',
    'acromegaly': 'endocrinology',

    # Haematology
    'anaemia': 'haematology',
    'anemia': 'haematology',
    'iron deficiency': 'haematology',
    'leukaemia': 'haematology',
    'leukemia': 'haematology',
    'lymphoma': 'haematology',
    'myeloma': 'haematology',
    'thrombocytopenia': 'haematology',
    'coagulation': 'haematology',
    'bleeding disorder': 'haematology',
    'haemophilia': 'haematology',
    'hemophilia': 'haematology',

    # Emergency Medicine
    'trauma': 'emergency_medicine',
    'shock': 'emergency_medicine',
    'sepsis': 'emergency_medicine',
    'anaphylaxis': 'emergency_medicine',
    'poisoning': 'emergency_medicine',
    'overdose': 'emergency_medicine',
    'burns': 'emergency_medicine',
    'resuscitation': 'emergency_medicine',

    # Dermatology
    'rash': 'dermatology',
    'eczema': 'dermatology',
    'psoriasis': 'dermatology',
    'melanoma': 'dermatology',
    'skin cancer': 'dermatology',
    'dermatitis': 'dermatology',
    'cellulitis': 'dermatology',

    # Surgery
    'hernia': 'surgery',
    'fracture': 'surgery',
    'wound': 'surgery',
    'post-operative': 'surgery',
    'pre-operative': 'surgery',
    'surgical': 'surgery',
}

# Keyword-based mapping for partial matches
KEYWORD_TO_SPECIALTY = {
    'psychiatry': [
        'depression', 'depressive', 'anxiety', 'anxious', 'panic', 'psychosis', 'psychotic',
        'schizophrenia', 'bipolar', 'mania', 'manic', 'suicide', 'suicidal', 'self-harm',
        'ptsd', 'trauma', 'ocd', 'obsessive', 'compulsive', 'eating disorder', 'anorexia',
        'bulimia', 'personality disorder', 'borderline', 'substance', 'alcohol', 'drug abuse',
        'addiction', 'dementia', 'alzheimer', 'delirium', 'mental health', 'psychiatric',
        'mood disorder', 'arfid', 'opioid', 'buprenorphine', 'naltrexone', 'methadone',
        'adhd', 'attention deficit', 'autism', 'antisocial', 'dbt', 'intellectual disability',
        'sleep disorder', 'insomnia', 'circadian', 'somatoform', 'somatization', 'conversion', 'factitious',
        'malingering', 'stimulant', 'sleep', 'hygiene', 'loneliness', 'empty nest', 'grief',
        'bereavement', 'agoraphobia', 'post-partum', 'postpartum blues'
    ],
    'cardiology': [
        'stemi', 'nstemi', 'myocardial', 'cardiac', 'heart', 'coronary', 'angina',
        'atrial', 'ventricular', 'arrhythmia', 'fibrillation', 'tachycardia', 'bradycardia',
        'hypertension', 'hypertensive', 'cardiomyopathy', 'valvular', 'valve', 'mitral',
        'aortic', 'pericarditis', 'pericardial', 'endocarditis', 'myocarditis',
        'cardiovascular', 'ecg', 'chest pain'
    ],
    'respiratory': [
        'pneumonia', 'copd', 'asthma', 'pneumothorax', 'pulmonary', 'lung', 'bronchial',
        'bronchiectasis', 'tuberculosis', 'pleural', 'respiratory', 'breathing', 'dyspnoea',
        'dyspnea', 'cough', 'sputum', 'wheez', 'inhaler', 'nebuliser', 'nebulizer',
        'oxygen', 'ventilation', 'embolism', 'thrombosis', 'vte', 'ild', 'cystic fibrosis',
        'cftr', 'omalizumab', 'hypersensitivity pneumonitis', 'sarcoidosis'
    ],
    'obstetrics_gynaecology': [
        'pregnancy', 'pregnant', 'antenatal', 'prenatal', 'ectopic', 'miscarriage',
        'labour', 'labor', 'delivery', 'postpartum', 'placenta', 'foetal', 'fetal',
        'obstetric', 'menstrual', 'contraception', 'menopause', 'ovarian', 'uterine',
        'cervical', 'vaginal', 'gynaecolog', 'gynecolog', 'pelvic', 'endometri'
    ],
    'paediatrics': [
        'neonatal', 'neonate', 'infant', 'child', 'children', 'paediatric', 'pediatric',
        'developmental', 'vaccination', 'immunisation', 'immunization', 'newborn', 'baby'
    ],
    'neurology': [
        'stroke', 'neurological', 'seizure', 'epilep', 'meningitis', 'encephalitis',
        'sclerosis', 'parkinson', 'headache', 'migraine', 'neuropathy', 'nerve',
        'brain', 'cerebral', 'spinal', 'guillain'
    ],
    'gastroenterology': [
        'gastrointestinal', 'gastro', 'gi ', 'peptic', 'ulcer', 'ibd', 'crohn', 'colitis',
        'cirrhosis', 'hepatitis', 'liver', 'pancreatitis', 'pancreas', 'cholecystitis',
        'appendicitis', 'bowel', 'intestin', 'diarrhoea', 'diarrhea', 'constipation',
        'abdominal', 'dyspepsia', 'reflux', 'gord', 'gerd'
    ],
    'endocrinology': [
        'diabetes', 'diabetic', 'dka', 'thyroid', 'hyperthyroid', 'hypothyroid',
        'adrenal', 'cushing', 'addison', 'pituitary', 'hormone', 'endocrine'
    ],
    'haematology': [
        'anaemia', 'anemia', 'blood', 'leukaemia', 'leukemia', 'lymphoma', 'myeloma',
        'thrombocytopenia', 'coagulation', 'bleeding', 'haemophilia', 'hemophilia',
        'haematolog', 'hematolog'
    ],
    'emergency_medicine': [
        'trauma', 'shock', 'sepsis', 'septic', 'anaphylaxis', 'anaphylactic',
        'poisoning', 'overdose', 'burns', 'resuscitation', 'emergency', 'acute'
    ],
    'dermatology': [
        'rash', 'eczema', 'psoriasis', 'melanoma', 'skin', 'dermatitis', 'cellulitis',
        'dermatolog'
    ],
    'surgery': [
        'hernia', 'fracture', 'wound', 'operative', 'surgical', 'surgery', 'trauma'
    ],
}


def map_topic_to_specialty(topic: str, subtopic: str = "") -> str:
    """
    Map MCQ topic to specialty using comprehensive rules.

    Args:
        topic: Primary topic of the MCQ
        subtopic: Secondary topic/subtopic (optional)

    Returns:
        Specialty name (e.g., 'psychiatry', 'cardiology', 'unknown')
    """
    # Combine topic and subtopic for better matching
    combined_text = f"{topic} {subtopic}".lower().strip()
    topic_lower = topic.lower().strip()

    # 1. Try exact match on topic
    if topic_lower in TOPIC_TO_SPECIALTY_MAP:
        return TOPIC_TO_SPECIALTY_MAP[topic_lower]

    # 2. Try exact match on combined text
    if combined_text in TOPIC_TO_SPECIALTY_MAP:
        return TOPIC_TO_SPECIALTY_MAP[combined_text]

    # 3. Try keyword matching (most comprehensive)
    specialty_scores = defaultdict(int)

    for specialty, keywords in KEYWORD_TO_SPECIALTY.items():
        for keyword in keywords:
            # Count occurrences of each keyword
            if keyword in combined_text:
                specialty_scores[specialty] += 1

    # Return specialty with highest match score
    if specialty_scores:
        return max(specialty_scores.items(), key=lambda x: x[1])[0]

    # 4. Default to unknown
    return 'unknown'


def process_mcq_file(file_path: Path, dry_run: bool = False, replace_unknown: bool = True) -> Dict:
    """
    Process a single MCQ JSON file and add specialty fields.

    Args:
        file_path: Path to JSON file
        dry_run: If True, don't save changes
        replace_unknown: If True, replace existing "unknown" specialties

    Returns:
        Statistics dict with processing results
    """
    stats = {
        'file': file_path.name,
        'total_mcqs': 0,
        'mcqs_updated': 0,
        'mcqs_skipped': 0,
        'specialty_distribution': defaultdict(int),
        'unmapped_topics': defaultdict(int),
        'errors': []
    }

    try:
        # Load JSON file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Determine JSON structure
        mcqs_list = None
        if isinstance(data, list):
            # Direct array of MCQs
            mcqs_list = data
        elif isinstance(data, dict) and 'mcqs' in data:
            # Wrapped structure with metadata
            mcqs_list = data['mcqs']
        else:
            stats['errors'].append(f"Unknown JSON structure: {list(data.keys())}")
            return stats

        stats['total_mcqs'] = len(mcqs_list)

        # Process each MCQ
        for mcq in mcqs_list:
            if not isinstance(mcq, dict):
                stats['mcqs_skipped'] += 1
                continue

            # Check if specialty already exists
            if 'specialty' in mcq:
                # Replace "unknown" if requested
                if replace_unknown and mcq['specialty'] == 'unknown':
                    pass  # Continue to remap
                else:
                    stats['mcqs_skipped'] += 1
                    stats['specialty_distribution'][mcq['specialty']] += 1
                    continue

            # Get topic and subtopic (try multiple locations)
            topic = mcq.get('topic', '')
            subtopic = mcq.get('subtopic', '')

            # Some MCQs have topic in metadata.topic
            if not topic and 'metadata' in mcq:
                topic = mcq.get('metadata', {}).get('topic', '')

            if not topic:
                stats['mcqs_skipped'] += 1
                stats['errors'].append(f"MCQ {mcq.get('id', 'unknown')} has no topic")
                continue

            # Map to specialty
            specialty = map_topic_to_specialty(topic, subtopic)

            # Add specialty field
            mcq['specialty'] = specialty
            stats['mcqs_updated'] += 1
            stats['specialty_distribution'][specialty] += 1

            # Track unmapped topics
            if specialty == 'unknown':
                stats['unmapped_topics'][topic] += 1

        # Save updated file (if not dry run)
        if not dry_run and stats['mcqs_updated'] > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        # Calculate coverage
        coverage_pct = (stats['mcqs_updated'] / stats['total_mcqs'] * 100) if stats['total_mcqs'] > 0 else 0
        stats['coverage_percent'] = round(coverage_pct, 1)

    except json.JSONDecodeError as e:
        stats['errors'].append(f"JSON decode error: {e}")
    except Exception as e:
        stats['errors'].append(f"Unexpected error: {e}")

    return stats


def print_report(all_stats: List[Dict], dry_run: bool = False):
    """Print comprehensive processing report."""
    print("\n" + "="*80)
    print(f"MCQ SPECIALTY FIELD ADDITION REPORT {'(DRY RUN)' if dry_run else ''}")
    print("="*80)

    total_files = len(all_stats)
    total_mcqs = sum(s['total_mcqs'] for s in all_stats)
    total_updated = sum(s['mcqs_updated'] for s in all_stats)
    total_skipped = sum(s['mcqs_skipped'] for s in all_stats)

    print(f"\nFiles processed: {total_files}")
    print(f"Total MCQs found: {total_mcqs}")
    print(f"MCQs with specialty added: {total_updated}")
    print(f"MCQs skipped (already had specialty): {total_skipped}")

    if total_mcqs > 0:
        coverage_pct = (total_updated / total_mcqs * 100)
        print(f"Coverage: {coverage_pct:.1f}%")

    # Specialty distribution
    specialty_totals = defaultdict(int)
    for stats in all_stats:
        for specialty, count in stats['specialty_distribution'].items():
            specialty_totals[specialty] += count

    print(f"\nSpecialty distribution:")
    for specialty, count in sorted(specialty_totals.items(), key=lambda x: x[1], reverse=True):
        pct = (count / total_mcqs * 100) if total_mcqs > 0 else 0
        print(f"  {specialty:30s}: {count:5d} ({pct:5.1f}%)")

    # Unmapped topics
    unmapped_totals = defaultdict(int)
    for stats in all_stats:
        for topic, count in stats['unmapped_topics'].items():
            unmapped_totals[topic] += count

    if unmapped_totals:
        print(f"\nUnmapped topics (need manual review):")
        for topic, count in sorted(unmapped_totals.items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"  \"{topic}\" ({count} MCQs)")

    # Errors
    total_errors = sum(len(s['errors']) for s in all_stats)
    if total_errors > 0:
        print(f"\n⚠ Errors encountered: {total_errors}")
        for stats in all_stats:
            if stats['errors']:
                print(f"\n  {stats['file']}:")
                for error in stats['errors'][:5]:
                    print(f"    - {error}")

    # File-by-file details
    print(f"\nDetailed file statistics:")
    for stats in sorted(all_stats, key=lambda x: x['total_mcqs'], reverse=True):
        if stats['total_mcqs'] > 0:
            print(f"\n  {stats['file']}:")
            print(f"    Total MCQs: {stats['total_mcqs']}")
            print(f"    Updated: {stats['mcqs_updated']}")
            print(f"    Coverage: {stats['coverage_percent']:.1f}%")

    print("\n" + "="*80)
    if not dry_run and total_updated > 0:
        print("✓ Script completed successfully")
        print("✓ Re-run matching: python3 scripts/link_images_to_mcqs.py")
    elif dry_run:
        print("✓ Dry run completed - no files modified")
        print("  Run without --dry-run to apply changes")
    else:
        print("✓ No changes needed - all MCQs already have specialty field")
    print("="*80 + "\n")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description='Add specialty field to MCQ JSON files for optimal image matching'
    )
    parser.add_argument(
        '--mcq-dir',
        type=Path,
        default=Path('data/mcqs'),
        help='Directory containing MCQ JSON files (default: data/mcqs)'
    )
    parser.add_argument(
        '--test-file',
        type=Path,
        help='Process only a specific file for testing'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without modifying files'
    )

    args = parser.parse_args()

    # Get list of files to process
    if args.test_file:
        if not args.test_file.exists():
            print(f"Error: Test file not found: {args.test_file}")
            sys.exit(1)
        json_files = [args.test_file]
    else:
        mcq_dir = Path(args.mcq_dir)
        if not mcq_dir.exists():
            print(f"Error: MCQ directory not found: {mcq_dir}")
            sys.exit(1)

        # Find all JSON files (exclude backup files)
        json_files = [
            f for f in mcq_dir.glob('*.json')
            if not any(x in f.name for x in ['backup', '.backup', 'matches', 'report'])
        ]

    if not json_files:
        print(f"No MCQ JSON files found in {args.mcq_dir}")
        sys.exit(1)

    print(f"Processing {len(json_files)} MCQ files...")
    if args.dry_run:
        print("(DRY RUN - no files will be modified)")
    print()

    # Process all files
    all_stats = []
    for i, file_path in enumerate(sorted(json_files), 1):
        print(f"[{i}/{len(json_files)}] Processing {file_path.name}...", end=' ')
        stats = process_mcq_file(file_path, dry_run=args.dry_run, replace_unknown=True)
        all_stats.append(stats)

        if stats['errors']:
            print(f"⚠ {len(stats['errors'])} errors")
        else:
            print(f"✓ {stats['mcqs_updated']}/{stats['total_mcqs']} updated")

    # Print comprehensive report
    print_report(all_stats, dry_run=args.dry_run)

    return 0


if __name__ == '__main__':
    sys.exit(main())
