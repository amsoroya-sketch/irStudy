#!/usr/bin/env python3
"""
Flashcard Extraction Script for ICRP OSCE Preparation
Extracts 700-800 flashcard items from HTML modules

Categories:
1. Red flags (150 cards)
2. Differential diagnoses (200 cards)
3. Physical examination steps (150 cards)
4. Communication phrases (100 cards)
5. Australian clinical context (100 cards)
6. Common IMG mistakes (100 cards)
"""

import re
import json
import glob
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Tuple

class FlashcardExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.flashcards = []
        self.current_tag = None
        self.current_data = []
        self.in_alert = False
        self.alert_type = None
        self.current_section = None
        self.current_file = None
        self.current_line = 0

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        attrs_dict = dict(attrs)

        # Detect alert boxes (red flags, warnings)
        if 'class' in attrs_dict:
            if 'alert-red' in attrs_dict['class']:
                self.in_alert = True
                self.alert_type = 'red-flag'
            elif 'alert-yellow' in attrs_dict['class']:
                self.in_alert = True
                self.alert_type = 'warning'
            elif 'alert-blue' in attrs_dict['class']:
                self.in_alert = True
                self.alert_type = 'info'

    def handle_endtag(self, tag):
        if self.in_alert and tag == 'div':
            self.in_alert = False
            self.alert_type = None
        self.current_tag = None

    def handle_data(self, data):
        data = data.strip()
        if data:
            self.current_data.append(data)

def extract_red_flags(html_content: str, source_file: str) -> List[Dict]:
    """Extract red flag items (150 target)"""
    cards = []

    # Pattern 1: RED FLAG mentions
    red_flag_patterns = [
        r'🚨.*?RED FLAG.*?:?\s*([^<\n]+)',
        r'RED FLAG.*?:?\s*([^<\n]+)',
        r'MUST NOT MISS.*?:?\s*([^<\n]+)',
        r'CRITICAL.*?:?\s*([^<\n]+)',
        r'EMERGENCY.*?features?.*?:?\s*([^<\n]+)',
    ]

    for pattern in red_flag_patterns:
        matches = re.finditer(pattern, html_content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            content = match.group(1).strip()
            if len(content) > 10 and len(content) < 300:
                cards.append({
                    'front': f'What is a red flag for this condition?',
                    'back': content,
                    'tags': ['red-flag', 'critical'],
                    'source': source_file,
                    'difficulty': 'high'
                })

    # Pattern 2: Alert boxes with red/critical content
    alert_pattern = r'<div class="alert alert-red">(.*?)</div>'
    alerts = re.finditer(alert_pattern, html_content, re.DOTALL)
    for alert in alerts:
        alert_text = re.sub(r'<[^>]+>', ' ', alert.group(1)).strip()
        if len(alert_text) > 15 and len(alert_text) < 500:
            # Split by sentences if too long
            sentences = re.split(r'[.!?]\s+', alert_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 15:
                    cards.append({
                        'front': 'Red flag warning:',
                        'back': sentence,
                        'tags': ['red-flag', 'warning'],
                        'source': source_file,
                        'difficulty': 'high'
                    })

    return cards

def extract_differentials(html_content: str, source_file: str) -> List[Dict]:
    """Extract differential diagnosis items (200 target)"""
    cards = []

    # Pattern 1: Top 3 Differentials sections
    diff_section_pattern = r'Top\s+3\s+Differentials.*?</h\d>(.*?)(?=<h[234]|<hr|$)'
    sections = re.finditer(diff_section_pattern, html_content, re.DOTALL | re.IGNORECASE)

    for section in sections:
        content = section.group(1)
        # Extract list items
        list_items = re.findall(r'<li[^>]*>(.*?)</li>', content, re.DOTALL)
        for item in list_items:
            clean_item = re.sub(r'<[^>]+>', ' ', item).strip()
            if 'differential' in clean_item.lower() or len(clean_item) > 20:
                # Extract diagnosis name and key features
                diagnosis_match = re.match(r'^([^:(-]+)[:(]?(.+)?', clean_item)
                if diagnosis_match:
                    diagnosis = diagnosis_match.group(1).strip()
                    features = diagnosis_match.group(2).strip() if diagnosis_match.group(2) else ""

                    cards.append({
                        'front': f'Key features of {diagnosis}?',
                        'back': features if features else clean_item,
                        'tags': ['differential', 'diagnosis'],
                        'source': source_file,
                        'difficulty': 'medium'
                    })

    # Pattern 2: Table rows with differentials
    table_pattern = r'<table.*?>(.*?)</table>'
    tables = re.finditer(table_pattern, html_content, re.DOTALL)
    for table in tables:
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table.group(1), re.DOTALL)
        for row in rows[1:]:  # Skip header row
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if len(cells) >= 2:
                diagnosis = re.sub(r'<[^>]+>', '', cells[0]).strip()
                features = re.sub(r'<[^>]+>', '', cells[1]).strip()
                if diagnosis and features and len(diagnosis) > 2:
                    cards.append({
                        'front': f'Clinical features of {diagnosis}?',
                        'back': features,
                        'tags': ['differential', 'clinical-features'],
                        'source': source_file,
                        'difficulty': 'medium'
                    })

    return cards

def extract_physical_exam_steps(html_content: str, source_file: str) -> List[Dict]:
    """Extract physical examination steps (150 target)"""
    cards = []

    # Pattern 1: The 5 Ps framework
    five_ps_pattern = r'(Preparation|Position|Permission|Perform|Present).*?:?\s*([^<\n]{20,300})'
    matches = re.finditer(five_ps_pattern, html_content, re.IGNORECASE)
    for match in matches:
        step = match.group(1)
        instruction = match.group(2).strip()
        cards.append({
            'front': f'Physical exam - {step} step:',
            'back': instruction,
            'tags': ['physical-exam', '5-ps', 'examination'],
            'source': source_file,
            'difficulty': 'easy'
        })

    # Pattern 2: Examination technique descriptions
    exam_patterns = [
        r'Palpation.*?:?\s*([^<\n]{30,300})',
        r'Percussion.*?:?\s*([^<\n]{30,300})',
        r'Auscultation.*?:?\s*([^<\n]{30,300})',
        r'Inspection.*?:?\s*([^<\n]{30,300})',
    ]

    for pattern in exam_patterns:
        matches = re.finditer(pattern, html_content, re.IGNORECASE)
        for match in matches:
            technique = match.group(0).split(':')[0].strip()
            instruction = match.group(1).strip()
            cards.append({
                'front': f'How to perform {technique.lower()}?',
                'back': instruction,
                'tags': ['physical-exam', 'technique'],
                'source': source_file,
                'difficulty': 'medium'
            })

    return cards

def extract_communication_phrases(html_content: str, source_file: str) -> List[Dict]:
    """Extract communication phrases (100 target)"""
    cards = []

    # Pattern 1: "What to say" boxes
    what_to_say_pattern = r'What to say.*?:?\s*["\']([^"\']{20,300})["\'"]'
    matches = re.finditer(what_to_say_pattern, html_content, re.IGNORECASE)
    for match in matches:
        phrase = match.group(1).strip()
        cards.append({
            'front': 'Communication phrase:',
            'back': phrase,
            'tags': ['communication', 'phrase', 'what-to-say'],
            'source': source_file,
            'difficulty': 'easy'
        })

    # Pattern 2: SPIKES framework elements
    spikes_pattern = r'(Setting|Perception|Invitation|Knowledge|Emotions|Strategy|Summary).*?:?\s*([^<\n]{30,400})'
    matches = re.finditer(spikes_pattern, html_content, re.IGNORECASE)
    for match in matches:
        if 'SPIKES' not in match.group(0):  # Avoid section headers
            step = match.group(1)
            content = match.group(2).strip()
            cards.append({
                'front': f'SPIKES - {step} step:',
                'back': content,
                'tags': ['communication', 'spikes', 'breaking-bad-news'],
                'source': source_file,
                'difficulty': 'medium'
            })

    # Pattern 3: Quoted communication examples
    quote_pattern = r'"([^"]{40,200})"'
    quotes = re.finditer(quote_pattern, html_content)
    for quote in quotes:
        text = quote.group(1).strip()
        # Filter for communication-related quotes
        if any(word in text.lower() for word in ['understand', 'feel', 'sorry', 'help', 'concerned', 'worried', 'explain']):
            cards.append({
                'front': 'Empathetic communication phrase:',
                'back': f'"{text}"',
                'tags': ['communication', 'empathy', 'phrase'],
                'source': source_file,
                'difficulty': 'easy'
            })

    return cards

def extract_australian_context(html_content: str, source_file: str) -> List[Dict]:
    """Extract Australian clinical context items (100 target)"""
    cards = []

    # Pattern 1: Australian drug names
    australian_drugs = {
        'paracetamol': 'NOT acetaminophen',
        'salbutamol': 'NOT albuterol',
        'GTN': 'NOT nitroglycerin',
        'adrenaline': 'NOT epinephrine',
    }

    for aus_drug, us_drug in australian_drugs.items():
        if aus_drug in html_content:
            cards.append({
                'front': f'Australian drug name (not US):',
                'back': f'{aus_drug.capitalize()} ({us_drug})',
                'tags': ['australian', 'medication', 'terminology'],
                'source': source_file,
                'difficulty': 'easy'
            })

    # Pattern 2: eTG/PBS references
    etg_pattern = r'eTG\s+\d{4}.*?:?\s*([^<\n]{20,300})'
    matches = re.finditer(etg_pattern, html_content, re.IGNORECASE)
    for match in matches:
        guideline = match.group(0).strip()
        cards.append({
            'front': 'Australian guideline (eTG):',
            'back': guideline,
            'tags': ['australian', 'etg', 'guidelines'],
            'source': source_file,
            'difficulty': 'medium'
        })

    # Pattern 3: PBS listings
    pbs_pattern = r'PBS[-\s]listed?.*?:?\s*([^<\n]{10,200})'
    matches = re.finditer(pbs_pattern, html_content, re.IGNORECASE)
    for match in matches:
        pbs_info = match.group(0).strip()
        cards.append({
            'front': 'PBS medication information:',
            'back': pbs_info,
            'tags': ['australian', 'pbs', 'medication'],
            'source': source_file,
            'difficulty': 'medium'
        })

    # Pattern 4: Australian spelling examples
    spelling_pairs = [
        ('paediatric', 'NOT pediatric'),
        ('anaemia', 'NOT anemia'),
        ('oestrogen', 'NOT estrogen'),
        ('colour', 'NOT color'),
    ]

    for aus_spell, us_spell in spelling_pairs:
        if aus_spell in html_content.lower():
            cards.append({
                'front': f'Australian spelling:',
                'back': f'{aus_spell} ({us_spell})',
                'tags': ['australian', 'spelling', 'terminology'],
                'source': source_file,
                'difficulty': 'easy'
            })

    return cards

def extract_img_mistakes(html_content: str, source_file: str) -> List[Dict]:
    """Extract common IMG mistakes (100 target)"""
    cards = []

    # Pattern 1: IMG mistake sections
    img_section_pattern = r'Common IMG Mistakes?.*?</h\d>(.*?)(?=<h[234]|<hr|$)'
    sections = re.finditer(img_section_pattern, html_content, re.DOTALL | re.IGNORECASE)

    for section in sections:
        content = section.group(1)
        # Extract list items with ❌ or X markers
        mistake_items = re.findall(r'[❌✗X]\s*([^<\n]{15,300})', content)
        for mistake in mistake_items:
            mistake = mistake.strip()
            if mistake:
                cards.append({
                    'front': 'Common IMG mistake to avoid:',
                    'back': f'❌ {mistake}',
                    'tags': ['img-mistake', 'error', 'avoid'],
                    'source': source_file,
                    'difficulty': 'high'
                })

    # Pattern 2: Explicit "NOT" statements
    not_pattern = r'(?:NOT|Don\'t|Never|Avoid):\s*([^<\n]{20,300})'
    matches = re.finditer(not_pattern, html_content, re.IGNORECASE)
    for match in matches:
        mistake = match.group(0).strip()
        cards.append({
            'front': 'What NOT to do:',
            'back': mistake,
            'tags': ['img-mistake', 'avoid', 'error'],
            'source': source_file,
            'difficulty': 'medium'
        })

    return cards

def process_all_modules(base_path: str) -> Dict:
    """Process all HTML modules and extract flashcards"""

    all_cards = {
        'red_flags': [],
        'differentials': [],
        'physical_exam': [],
        'communication': [],
        'australian': [],
        'img_mistakes': []
    }

    # Find all HTML files
    html_files = []
    for pattern in ['Medicine/*.html', 'Surgery/*.html', 'Paediatrics/*.html',
                    'ObGyn/*.html', 'Psychiatry/*.html', 'Ethics_Communication/*.html',
                    'Mock_Stations/*.html']:
        html_files.extend(glob.glob(f"{base_path}/{pattern}"))

    print(f"Processing {len(html_files)} HTML files...")

    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()

            source = html_file.replace(base_path + '/', '')

            # Extract each category
            all_cards['red_flags'].extend(extract_red_flags(content, source))
            all_cards['differentials'].extend(extract_differentials(content, source))
            all_cards['physical_exam'].extend(extract_physical_exam_steps(content, source))
            all_cards['communication'].extend(extract_communication_phrases(content, source))
            all_cards['australian'].extend(extract_australian_context(content, source))
            all_cards['img_mistakes'].extend(extract_img_mistakes(content, source))

            print(f"  Processed: {source}")

        except Exception as e:
            print(f"  ERROR processing {html_file}: {e}")

    return all_cards

def deduplicate_cards(cards: List[Dict]) -> List[Dict]:
    """Remove duplicate flashcards based on back content"""
    seen = set()
    unique_cards = []

    for card in cards:
        # Use back content as unique identifier
        identifier = card['back'].lower().strip()
        if identifier not in seen:
            seen.add(identifier)
            unique_cards.append(card)

    return unique_cards

def balance_categories(all_cards: Dict, targets: Dict) -> Dict:
    """Balance flashcard counts to meet target numbers"""
    balanced = {}

    for category, target in targets.items():
        cards = all_cards[category]
        # Deduplicate
        cards = deduplicate_cards(cards)

        # Sample to target (or keep all if less than target)
        if len(cards) > target:
            # Prioritize high difficulty and diverse sources
            cards.sort(key=lambda x: (x.get('difficulty', 'medium'), x.get('source', '')))
            balanced[category] = cards[:target]
        else:
            balanced[category] = cards

    return balanced

def main():
    """Main execution function"""

    base_path = '/home/dev/Development/irStudy/ICRP_OSCE_Preparation'
    output_dir = '/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards'

    # Target counts
    targets = {
        'red_flags': 150,
        'differentials': 200,
        'physical_exam': 150,
        'communication': 100,
        'australian': 100,
        'img_mistakes': 100
    }

    print("=" * 60)
    print("ICRP OSCE Flashcard Extraction Tool")
    print("=" * 60)
    print()

    # Extract all flashcards
    all_cards = process_all_modules(base_path)

    print()
    print("Extraction complete. Raw counts:")
    for category, cards in all_cards.items():
        print(f"  {category}: {len(cards)} cards")

    # Balance to targets
    print()
    print("Balancing and deduplicating...")
    balanced_cards = balance_categories(all_cards, targets)

    print()
    print("Final counts after deduplication and balancing:")
    total = 0
    for category, cards in balanced_cards.items():
        count = len(cards)
        total += count
        target = targets[category]
        status = "✓" if count >= target * 0.9 else "⚠"
        print(f"  {status} {category}: {count}/{target} cards")

    print(f"\nTotal flashcards: {total}")

    # Create final JSON structure
    print()
    print("Creating flashcard data structure...")

    flashcard_data = {
        "deck": "ICRP_AMC_Clinical",
        "created": "2025-12-16",
        "version": "1.0",
        "total_cards": total,
        "categories": {},
        "cards": []
    }

    # Add cards with IDs
    card_id = 1
    for category, cards in balanced_cards.items():
        category_name = category.replace('_', '-')
        flashcard_data['categories'][category_name] = len(cards)

        for card in cards:
            card['id'] = card_id
            card['deck'] = f"ICRP_AMC_Clinical/{category_name}"
            flashcard_data['cards'].append(card)
            card_id += 1

    # Write JSON file
    json_path = f"{output_dir}/flashcard_data.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(flashcard_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Created: {json_path}")

    # Create Anki import file (tab-separated)
    print("Creating Anki import file...")
    anki_path = f"{output_dir}/anki_import.txt"

    with open(anki_path, 'w', encoding='utf-8') as f:
        for card in flashcard_data['cards']:
            front = card['front'].replace('\t', ' ').replace('\n', ' ')
            back = card['back'].replace('\t', ' ').replace('\n', ' ')
            tags = ' '.join([f"#{tag}" for tag in card.get('tags', [])])
            source = card.get('source', '')

            # Tab-separated format: Front [TAB] Back [TAB] Tags [TAB] Source
            f.write(f"{front}\t{back}\t{tags}\t{source}\n")

    print(f"✓ Created: {anki_path}")

    # Create summary report
    print()
    print("Creating summary report...")
    report_path = f"{output_dir}/extraction_summary.txt"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("ICRP OSCE Flashcard Extraction Summary\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: 2025-12-16\n")
        f.write(f"Total Cards Generated: {total}\n\n")

        f.write("Cards by Category:\n")
        f.write("-" * 70 + "\n")
        for category, count in flashcard_data['categories'].items():
            target = targets.get(category.replace('-', '_'), 0)
            percentage = (count / target * 100) if target > 0 else 0
            f.write(f"  {category:20s}: {count:3d}/{target:3d} ({percentage:5.1f}%)\n")

        f.write("\n")
        f.write("Tags Distribution:\n")
        f.write("-" * 70 + "\n")
        tag_counts = {}
        for card in flashcard_data['cards']:
            for tag in card.get('tags', []):
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
            f.write(f"  #{tag:25s}: {count:4d} cards\n")

        f.write("\n")
        f.write("Difficulty Distribution:\n")
        f.write("-" * 70 + "\n")
        diff_counts = {}
        for card in flashcard_data['cards']:
            diff = card.get('difficulty', 'medium')
            diff_counts[diff] = diff_counts.get(diff, 0) + 1

        for diff in ['easy', 'medium', 'high']:
            count = diff_counts.get(diff, 0)
            percentage = (count / total * 100) if total > 0 else 0
            f.write(f"  {diff.capitalize():10s}: {count:4d} ({percentage:5.1f}%)\n")

        f.write("\n")
        f.write("Files Created:\n")
        f.write("-" * 70 + "\n")
        f.write(f"  1. {json_path}\n")
        f.write(f"  2. {anki_path}\n")
        f.write(f"  3. {report_path}\n")

        f.write("\n")
        f.write("Next Steps:\n")
        f.write("-" * 70 + "\n")
        f.write("  1. Import anki_import.txt into Anki Desktop\n")
        f.write("  2. Review flashcard_data.json for quality\n")
        f.write("  3. Add custom cards as needed\n")
        f.write("  4. Begin spaced repetition study\n")

    print(f"✓ Created: {report_path}\n")

    print("=" * 60)
    print("Flashcard extraction complete!")
    print("=" * 60)
    print()
    print(f"Generated {total} flashcards across 6 categories")
    print()
    print("Files created:")
    print(f"  1. flashcard_data.json ({total} cards)")
    print(f"  2. anki_import.txt (Anki-compatible)")
    print(f"  3. extraction_summary.txt (detailed report)")
    print()

if __name__ == '__main__':
    main()
