#!/usr/bin/env python3
"""
Match Medical Images to MCQs and OSCEs

This script:
1. Loads image catalog
2. Queries database for MCQs and OSCEs
3. Matches images to questions based on:
   - Specialty matching
   - Topic/keyword matching in question text
   - Tags matching
4. Generates matching report
5. Creates SQL update statements to link images

Usage:
    python3 scripts/match_images_to_questions.py --dry-run
    python3 scripts/match_images_to_questions.py --execute
"""

import json
import psycopg2
from pathlib import Path
import re
from collections import defaultdict
import argparse

# Database connection
def get_db_config():
    """Load database config from secrets"""
    from pathlib import Path
    password_file = Path('secrets/db_password.txt')
    if password_file.exists():
        password = password_file.read_text().strip()
    else:
        password = 'postgres'  # Fallback

    return {
        'host': 'localhost',
        'port': 5433,
        'database': 'irstudy_medical',
        'user': 'postgres',
        'password': password
    }

def load_image_catalog():
    """Load image catalog JSON"""
    catalog_file = Path('data/medical_images_catalog.json')
    with open(catalog_file) as f:
        return json.load(f)

def get_mcqs_from_db(conn):
    """Fetch all MCQs from database"""
    query = """
        SELECT
            id,
            question_id,
            question_text,
            specialty,
            difficulty,
            tags,
            image_url
        FROM mcqs
        WHERE is_published = true
        ORDER BY specialty, id
    """

    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def get_osces_from_db(conn):
    """Fetch all OSCEs from database"""
    query = """
        SELECT
            id,
            osce_id,
            station_title,
            station_type,
            candidate_instructions,
            specialty,
            difficulty,
            tags,
            supporting_documents
        FROM osces
        WHERE is_published = true
        ORDER BY specialty, id
    """

    with conn.cursor() as cur:
        cur.execute(query)
        columns = [desc[0] for desc in cur.description]
        return [dict(zip(columns, row)) for row in cur.fetchall()]

def extract_keywords_from_text(text):
    """Extract medical keywords from question text"""
    if not text:
        return set()

    # Convert to lowercase and extract medical terms
    text_lower = text.lower()
    keywords = set()

    # Common medical terms
    medical_terms = [
        # Cardiology
        'stemi', 'nstemi', 'mi', 'myocardial infarction', 'ecg', 'ekg',
        'st elevation', 'st depression', 't wave inversion',
        'atrial fibrillation', 'atrial flutter', 'afib', 'af',
        'bradycardia', 'tachycardia', 'arrhythmia',
        'av block', 'bundle branch block', 'lbbb', 'rbbb',
        'angina', 'chest pain', 'acute coronary syndrome', 'acs',
        'pericarditis', 'hypertension', 'heart failure',
        'ventricular tachycardia', 'vt', 'ventricular fibrillation', 'vf',
        'svt', 'supraventricular tachycardia',
        'hyperkalemia', 'hypokalemia',

        # Hematology
        'anemia', 'iron deficiency', 'megaloblastic', 'pernicious',
        'thalassemia', 'sickle cell',
        'leukemia', 'aml', 'all', 'cml', 'cll',
        'lymphoma', 'myeloma',
        'thrombocytopenia', 'thrombocytosis',
        'neutropenia', 'leukocytosis',
        'blood smear', 'blast cells', 'auer rods',

        # Dermatology
        'rash', 'skin lesion', 'melanoma', 'basal cell', 'squamous cell',
        'psoriasis', 'eczema', 'dermatitis',
        'cellulitis', 'abscess', 'impetigo',
        'herpes', 'zoster', 'shingles',
        'urticaria', 'angioedema',
        'acne', 'rosacea',

        # Respiratory
        'pneumonia', 'copd', 'asthma', 'pneumothorax',
        'chest x-ray', 'cxr', 'xray',
        'pleural effusion', 'pulmonary edema',
        'tuberculosis', 'tb',
        'pulmonary embolism', 'pe',

        # Gastroenterology
        'abdominal pain', 'appendicitis', 'cholecystitis',
        'pancreatitis', 'cirrhosis', 'hepatitis',
        'ibd', 'crohn', 'ulcerative colitis',
        'gi bleed', 'melena', 'hematochezia',

        # Neurology
        'stroke', 'tia', 'headache', 'migraine',
        'seizure', 'epilepsy',
        'parkinson', 'alzheimer', 'dementia',
        'multiple sclerosis', 'ms',
        'guillain-barre', 'gbs',

        # Endocrinology
        'diabetes', 'hyperthyroid', 'hypothyroid',
        'addison', 'cushing',
        'hypoglycemia', 'hyperglycemia', 'dka',
        'pituitary', 'acromegaly',
    ]

    for term in medical_terms:
        if term in text_lower:
            keywords.add(term)

    return keywords

def calculate_match_score(image, question):
    """Calculate matching score between image and question"""
    score = 0
    reasons = []

    # Specialty match (highest weight)
    if image['db_specialty'] == question['specialty']:
        score += 100
        reasons.append(f"Specialty match: {image['db_specialty']}")

    # Extract keywords from question
    question_text = question.get('question_text', '') or question.get('candidate_instructions', '')
    question_keywords = extract_keywords_from_text(question_text)

    # Topic/keyword matching
    image_topic = (image['topic'] or '').lower()

    for keyword in question_keywords:
        if keyword in image_topic:
            score += 50
            reasons.append(f"Topic keyword match: '{keyword}' in '{image['topic']}'")

    # Image type relevance
    if image['image_type'] == 'ECG' and ('ecg' in question_text.lower() or 'ekg' in question_text.lower()):
        score += 30
        reasons.append("ECG image for ECG-related question")

    if image['image_type'] == 'Microscopy' and any(term in question_text.lower() for term in ['blood smear', 'cells', 'microscopy']):
        score += 30
        reasons.append("Microscopy image for blood/cell-related question")

    return score, reasons

def match_images_to_questions(catalog, mcqs, osces):
    """Match images to MCQs and OSCEs"""
    matches = {
        'mcqs': defaultdict(list),
        'osces': defaultdict(list),
        'unmatched_images': [],
        'stats': {
            'total_images': len(catalog['images']),
            'matched_images': 0,
            'total_mcqs': len(mcqs),
            'mcqs_with_images': 0,
            'total_osces': len(osces),
            'osces_with_images': 0,
        }
    }

    # Match images to MCQs
    for image in catalog['images']:
        best_match = None
        best_score = 0
        best_reasons = []

        for mcq in mcqs:
            # Skip if already has image
            if mcq['image_url']:
                continue

            score, reasons = calculate_match_score(image, mcq)

            if score > best_score and score >= 100:  # Minimum threshold: specialty match
                best_score = score
                best_match = mcq
                best_reasons = reasons

        if best_match:
            matches['mcqs'][image['filepath']].append({
                'mcq_id': best_match['id'],
                'question_id': best_match['question_id'],
                'score': best_score,
                'reasons': best_reasons,
                'image': image
            })
            matches['stats']['matched_images'] += 1

    # Match images to OSCEs
    for image in catalog['images']:
        best_match = None
        best_score = 0
        best_reasons = []

        for osce in osces:
            # Skip if already has supporting documents
            if osce['supporting_documents'] and osce['supporting_documents'] != '[]':
                continue

            score, reasons = calculate_match_score(image, osce)

            if score > best_score and score >= 100:
                best_score = score
                best_match = osce
                best_reasons = reasons

        if best_match:
            matches['osces'][image['filepath']].append({
                'osce_id': best_match['id'],
                'osce_code': best_match['osce_id'],
                'score': best_score,
                'reasons': best_reasons,
                'image': image
            })

    # Count matched questions
    matches['stats']['mcqs_with_images'] = len(matches['mcqs'])
    matches['stats']['osces_with_images'] = len(matches['osces'])

    return matches

def generate_sql_updates(matches, dry_run=True):
    """Generate SQL UPDATE statements"""
    sql_statements = []

    # MCQ updates
    for filepath, match_list in matches['mcqs'].items():
        if match_list:
            # Use best match (highest score)
            best = max(match_list, key=lambda x: x['score'])
            image_path = f"/images/{filepath.replace('data/medical_images/', '')}"

            sql = f"""
UPDATE mcqs
SET image_url = '{image_path}',
    image_caption = '{best['image']['topic']}'
WHERE id = {best['mcq_id']};
-- Match: {best['question_id']} <- {best['image']['topic']} (score: {best['score']})
"""
            sql_statements.append(sql)

    # OSCE updates
    for filepath, match_list in matches['osces'].items():
        if match_list:
            best = max(match_list, key=lambda x: x['score'])
            image_path = f"/images/{filepath.replace('data/medical_images/', '')}"

            doc_json = json.dumps([{
                "type": best['image']['image_type'],
                "url": image_path,
                "caption": best['image']['topic']
            }])

            sql = f"""
UPDATE osces
SET supporting_documents = '{doc_json}'::json
WHERE id = {best['osce_id']};
-- Match: {best['osce_code']} <- {best['image']['topic']} (score: {best['score']})
"""
            sql_statements.append(sql)

    return sql_statements

def main():
    parser = argparse.ArgumentParser(description='Match images to MCQs and OSCEs')
    parser.add_argument('--execute', action='store_true', help='Execute SQL updates (default: dry-run)')
    args = parser.parse_args()

    dry_run = not args.execute

    print("Loading image catalog...")
    catalog = load_image_catalog()
    print(f"  Loaded {catalog['total_images']} images")

    print("\nConnecting to database...")
    DB_CONFIG = get_db_config()
    conn = psycopg2.connect(**DB_CONFIG)

    print("Fetching MCQs...")
    mcqs = get_mcqs_from_db(conn)
    print(f"  Found {len(mcqs)} MCQs")

    print("Fetching OSCEs...")
    osces = get_osces_from_db(conn)
    print(f"  Found {len(osces)} OSCEs")

    print("\nMatching images to questions...")
    matches = match_images_to_questions(catalog, mcqs, osces)

    print("\n" + "="*80)
    print("MATCHING RESULTS")
    print("="*80)
    print(f"Total images: {matches['stats']['total_images']}")
    print(f"Matched images: {matches['stats']['matched_images']}")
    print(f"\nMCQs:")
    print(f"  Total: {matches['stats']['total_mcqs']}")
    print(f"  Can receive images: {matches['stats']['mcqs_with_images']}")
    print(f"\nOSCEs:")
    print(f"  Total: {matches['stats']['total_osces']}")
    print(f"  Can receive images: {matches['stats']['osces_with_images']}")

    # Generate SQL
    sql_statements = generate_sql_updates(matches, dry_run)

    # Save SQL to file
    sql_file = Path('data/image_matching_updates.sql')
    with open(sql_file, 'w') as f:
        f.write("-- Auto-generated image matching SQL\n")
        f.write(f"-- Generated: {catalog['generated_at']}\n")
        f.write(f"-- Total updates: {len(sql_statements)}\n\n")
        f.write("\n".join(sql_statements))

    print(f"\n✅ SQL statements saved to: {sql_file}")
    print(f"   Total statements: {len(sql_statements)}")

    if dry_run:
        print("\n⚠️  DRY RUN MODE - No database changes made")
        print("   Run with --execute to apply changes")
    else:
        print("\nExecuting SQL updates...")
        with conn.cursor() as cur:
            for sql in sql_statements:
                cur.execute(sql.split('--')[0])  # Remove comments
        conn.commit()
        print("✅ Database updated successfully")

    conn.close()

    # Save detailed matching report
    report_file = Path('data/image_matching_report.json')
    with open(report_file, 'w') as f:
        # Convert matches to serializable format
        report = {
            'stats': matches['stats'],
            'mcq_matches': {k: v for k, v in list(matches['mcqs'].items())[:10]},  # Sample
            'osce_matches': {k: v for k, v in list(matches['osces'].items())[:10]},  # Sample
        }
        json.dump(report, f, indent=2)

    print(f"✅ Detailed report saved to: {report_file}")

if __name__ == '__main__':
    main()
