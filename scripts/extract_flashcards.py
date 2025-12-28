#!/usr/bin/env python3
"""
Flashcard Extraction Script for ICRP OSCE Materials
Extracts flashcards from HTML files following priority order:
1. Red flags
2. Differentials
3. Physical exam steps
4. Communication phrases
5. Australian context
6. IMG mistakes
"""

import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

# Base path
BASE_PATH = Path("/home/dev/Development/irStudy/ICRP_OSCE_Preparation")
OUTPUT_FILE = Path("/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json")

# Load existing flashcards
with open(OUTPUT_FILE, 'r') as f:
    data = json.load(f)

existing_cards = data['cards']
next_id = len(existing_cards) + 1
new_cards = []

# Difficulty mapping
DIFFICULTY_PATTERNS = {
    'hard': ['life-threatening', 'CRITICAL', 'EMERGENCY', 'MUST NOT MISS', '🚨'],
    'medium': ['important', 'significant', 'common', 'typical'],
    'easy': ['definition', 'classification', 'recall']
}

def determine_difficulty(text):
    """Determine difficulty based on content"""
    text_lower = text.lower()
    if any(pattern.lower() in text_lower for pattern in DIFFICULTY_PATTERNS['hard']):
        return 'hard'
    elif any(pattern.lower() in text_lower for pattern in DIFFICULTY_PATTERNS['medium']):
        return 'medium'
    return 'easy'

def determine_deck(file_path):
    """Determine deck based on file path"""
    path_str = str(file_path)
    if 'Medicine' in path_str:
        if 'Cardio' in path_str:
            return 'Medicine_Cardiorespiratory'
        elif 'GI' in path_str or 'Abdominal' in path_str:
            return 'Medicine_Gastroenterology'
        elif 'Neuro' in path_str:
            return 'Medicine_Neurology'
        elif 'Endocrin' in path_str:
            return 'Medicine_Endocrinology'
        elif 'ECG' in path_str:
            return 'Medicine_Cardiology'
        elif 'Emergency' in path_str or 'Anaphylaxis' in path_str or 'Seizure' in path_str:
            return 'Medicine_Emergency'
        elif 'ENT' in path_str:
            return 'Medicine_ENT'
        else:
            return 'Medicine_General'
    elif 'Surgery' in path_str:
        return 'Surgery'
    elif 'ObGyn' in path_str:
        return 'ObGyn'
    elif 'Paediatrics' in path_str or 'Paediatric' in path_str:
        return 'Paediatrics'
    elif 'Psychiatry' in path_str:
        return 'Psychiatry'
    elif 'Ethics' in path_str or 'Communication' in path_str:
        return 'Ethics_Communication'
    return 'General'

def extract_red_flags(soup, file_path):
    """Extract red flag flashcards"""
    cards = []

    # Pattern 1: Look for red flag sections
    red_flag_markers = soup.find_all(string=re.compile(r'🚨|RED FLAG|CRITICAL|MUST NOT MISS', re.IGNORECASE))

    for marker in red_flag_markers[:30]:  # Limit per file
        parent = marker.find_parent(['li', 'p', 'td', 'strong', 'h3', 'h4'])
        if not parent:
            continue

        text = parent.get_text(strip=True)
        if len(text) < 20 or len(text) > 500:
            continue

        # Check if it looks like a red flag description
        if any(phrase in text.lower() for phrase in ['pattern:', 'classic triad', 'action:', 'immediate', 'urgent']):
            # Try to extract structured content
            lines = text.split('\n')
            if len(lines) >= 2:
                front = lines[0].strip()
                back = ' '.join(lines[1:]).strip()

                # Clean up
                front = re.sub(r'🚨+', '🚨', front)
                front = re.sub(r'\s+', ' ', front)
                back = re.sub(r'\s+', ' ', back)

                if len(front) > 10 and len(back) > 10:
                    cards.append({
                        'front': f"🚨 RED FLAG: {front[:100]}" if not front.startswith('🚨') else front[:150],
                        'back': back[:300],
                        'category': 'red_flags',
                        'difficulty': 'hard'
                    })

    return cards

def extract_differentials(soup, file_path):
    """Extract differential diagnosis flashcards"""
    cards = []

    # Look for differential tables
    tables = soup.find_all('table')
    for table in tables[:5]:  # Limit tables per file
        headers = [th.get_text(strip=True) for th in table.find_all('th')]
        if any('differential' in h.lower() or 'diagnosis' in h.lower() or 'causes' in h.lower() for h in headers):
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows[:10]:  # Limit rows
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2:
                    front = f"Differentials: {cells[0]}"
                    back = ' | '.join(cells[1:])
                    back = re.sub(r'\s+', ' ', back)

                    cards.append({
                        'front': front[:150],
                        'back': back[:400],
                        'category': 'differential',
                        'difficulty': 'medium'
                    })

    # Look for lists of differentials
    diff_markers = soup.find_all(string=re.compile(r'Differential|Causes of|Consider:', re.IGNORECASE))
    for marker in diff_markers[:10]:
        parent = marker.find_parent(['ul', 'ol', 'p'])
        if parent and parent.name in ['ul', 'ol']:
            items = [li.get_text(strip=True) for li in parent.find_all('li')]
            if 2 <= len(items) <= 10:
                title_elem = parent.find_previous(['h2', 'h3', 'h4', 'strong'])
                title = title_elem.get_text(strip=True) if title_elem else "Differential diagnosis"

                front = f"Differentials: {title[:80]}"
                back = '• ' + '\n• '.join(items)

                cards.append({
                    'front': front,
                    'back': back[:400],
                    'category': 'differential',
                    'difficulty': 'medium'
                })

    return cards

def extract_physical_exam(soup, file_path):
    """Extract physical examination steps"""
    cards = []

    # Look for 5 Ps framework, IPPA, examination steps
    exam_markers = soup.find_all(string=re.compile(r'Preparation|Position|Permission|Inspection|Palpation|Percussion|Auscultation|5 Ps|IPPA', re.IGNORECASE))

    for marker in exam_markers[:15]:
        parent = marker.find_parent(['ol', 'ul', 'div'])
        if not parent:
            continue

        # Try to extract a sequence
        items = parent.find_all('li')
        if 3 <= len(items) <= 8:
            title_elem = parent.find_previous(['h2', 'h3', 'h4'])
            title = title_elem.get_text(strip=True) if title_elem else "Physical examination"

            front = f"Physical exam: {title[:80]}"
            back = '\n'.join([f"{i+1}. {li.get_text(strip=True)[:150]}" for i, li in enumerate(items[:6])])

            cards.append({
                'front': front,
                'back': back[:400],
                'category': 'physical_exam',
                'difficulty': 'medium'
            })

    return cards

def extract_communication(soup, file_path):
    """Extract communication phrases"""
    cards = []

    if 'Communication' not in str(file_path) and 'Breaking' not in str(file_path):
        return cards

    # Look for communication phrases and scripts
    comm_markers = soup.find_all(string=re.compile(r'What to say|SPIKES|Breaking bad news|"', re.IGNORECASE))

    for marker in comm_markers[:15]:
        # Look for quoted phrases
        parent = marker.find_parent(['p', 'li', 'blockquote'])
        if not parent:
            continue

        text = parent.get_text(strip=True)

        # Extract phrases in quotes
        quotes = re.findall(r'"([^"]{20,300})"', text)
        for quote in quotes[:3]:
            # Try to find context
            context_elem = parent.find_previous(['h3', 'h4', 'strong'])
            context = context_elem.get_text(strip=True) if context_elem else "Communication"

            front = f"Communication: {context[:80]}"
            back = f'"{quote}"'

            cards.append({
                'front': front,
                'back': back[:300],
                'category': 'communication',
                'difficulty': 'medium'
            })

    return cards

def extract_australian_context(soup, file_path):
    """Extract Australian-specific content"""
    cards = []

    # Look for Australian references
    aus_markers = soup.find_all(string=re.compile(r'eTG|PBS|RACGP|ANZCOR|Australian|Australia|NSW|Medicare', re.IGNORECASE))

    for marker in aus_markers[:15]:
        parent = marker.find_parent(['li', 'p', 'td'])
        if not parent:
            continue

        text = parent.get_text(strip=True)
        if len(text) < 30 or len(text) > 400:
            continue

        # Check if it's substantive Australian content
        if any(term in text for term in ['eTG', 'PBS', 'Medicare', 'Australian guideline', 'RACGP']):
            # Try to extract key-value
            sentences = re.split(r'[.!?]', text)
            if len(sentences) >= 1:
                front = f"Australian context: {sentences[0][:100]}"
                back = ' '.join(sentences[1:])[:300] if len(sentences) > 1 else text[:300]

                cards.append({
                    'front': front,
                    'back': back,
                    'category': 'australian',
                    'difficulty': 'medium'
                })

    return cards

def extract_img_mistakes(soup, file_path):
    """Extract IMG common mistakes"""
    cards = []

    # Look for IMG mistakes sections
    img_sections = soup.find_all(string=re.compile(r'Common IMG Mistakes|IMG Common|Mistakes|AVOID', re.IGNORECASE))

    for section in img_sections[:3]:
        parent = section.find_parent(['div', 'section'])
        if not parent:
            parent = section.find_parent(['h2', 'h3'])
            if parent:
                parent = parent.find_next_sibling(['ul', 'ol', 'div'])

        if not parent:
            continue

        # Extract mistake items
        items = parent.find_all('li')
        for item in items[:10]:
            text = item.get_text(strip=True)
            if len(text) < 20:
                continue

            # Try to split into mistake and why/fix
            parts = re.split(r'[:–-]', text, maxsplit=1)
            if len(parts) == 2:
                front = f"IMG Mistake: {parts[0].strip()[:100]}"
                back = parts[1].strip()[:300]
            else:
                front = f"IMG Mistake: {text[:100]}"
                back = text[:300]

            cards.append({
                'front': front,
                'back': back,
                'category': 'img_mistake',
                'difficulty': 'medium'
            })

    return cards

def process_file(file_path):
    """Process a single HTML file"""
    global next_id, new_cards

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Extract different types of cards
        all_cards = []
        all_cards.extend(extract_red_flags(soup, file_path))
        all_cards.extend(extract_differentials(soup, file_path))
        all_cards.extend(extract_physical_exam(soup, file_path))
        all_cards.extend(extract_communication(soup, file_path))
        all_cards.extend(extract_australian_context(soup, file_path))
        all_cards.extend(extract_img_mistakes(soup, file_path))

        # Add metadata to cards
        deck = determine_deck(file_path)
        source_rel = str(file_path).replace(str(BASE_PATH) + '/', '')

        for card in all_cards:
            new_cards.append({
                'id': next_id,
                'front': card['front'],
                'back': card['back'],
                'deck': deck,
                'tags': [card['category'], card['difficulty']],
                'source': source_rel,
                'difficulty': card['difficulty'],
                'category': card['category']
            })
            next_id += 1

        print(f"✓ {source_rel}: {len(all_cards)} cards")
        return len(all_cards)

    except Exception as e:
        print(f"✗ Error processing {file_path}: {e}")
        return 0

def main():
    """Main extraction process"""
    print("=" * 60)
    print("FLASHCARD EXTRACTION - Phase 1.1")
    print("=" * 60)
    print(f"Starting ID: {next_id}")
    print(f"Target: 750 total cards (need {750 - len(existing_cards)} more)")
    print()

    # Get all HTML files
    html_files = list(BASE_PATH.rglob("*.html"))
    html_files = [f for f in html_files if 'MASTER_INDEX' not in str(f) and 'START_HERE' not in str(f)]

    print(f"Found {len(html_files)} HTML files to process")
    print()

    # Process by priority
    priority_order = [
        ('Medicine', 60),
        ('Surgery', 30),
        ('ObGyn', 20),
        ('Psychiatry', 20),
        ('Paediatrics', 10),
        ('Ethics_Communication', 10)
    ]

    total_extracted = 0

    for folder, target in priority_order:
        print(f"\n{folder} modules (target: ~{target} cards)")
        print("-" * 60)

        folder_files = [f for f in html_files if folder in str(f)]
        folder_count = 0

        for file in folder_files:
            count = process_file(file)
            folder_count += count
            total_extracted += count

            # Stop if we've reached target
            if total_extracted >= 737:
                break

        print(f"Subtotal: {folder_count} cards from {folder}")

        if total_extracted >= 737:
            break

    print()
    print("=" * 60)
    print(f"EXTRACTION COMPLETE")
    print("=" * 60)
    print(f"New cards extracted: {len(new_cards)}")
    print(f"Total cards: {len(existing_cards) + len(new_cards)}")
    print()

    # Save updated flashcards
    data['cards'].extend(new_cards)
    data['metadata']['total_cards'] = len(data['cards'])
    data['metadata']['last_updated'] = datetime.now().isoformat()

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to {OUTPUT_FILE}")

    # Statistics
    print()
    print("STATISTICS BY CATEGORY:")
    print("-" * 60)
    categories = {}
    for card in new_cards:
        cat = card['category']
        categories[cat] = categories.get(cat, 0) + 1

    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat:20s}: {count:4d} cards")

    print()
    print("STATISTICS BY DECK:")
    print("-" * 60)
    decks = {}
    for card in new_cards:
        deck = card['deck']
        decks[deck] = decks.get(deck, 0) + 1

    for deck, count in sorted(decks.items(), key=lambda x: x[1], reverse=True):
        print(f"  {deck:30s}: {count:4d} cards")

if __name__ == '__main__':
    main()
