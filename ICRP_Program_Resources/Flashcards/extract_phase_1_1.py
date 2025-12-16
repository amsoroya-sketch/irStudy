#!/usr/bin/env python3
"""
Phase 1.1 Flashcard Extraction Script
Extracts remaining 409 flashcards to reach 750 total

Current: 341 cards
Target: 750 cards
To extract: 409 cards

Category gaps:
- differentials: 102 more (currently 48/150)
- img_mistake: 104 more (currently 46/150)
- physical_exam: 101 more (currently 49/150)
- australian: 86 more (currently 64/150)
- red_flag: 61 more (currently 89/150)
- communication: 58 more (currently 42/100)
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from collections import defaultdict

BASE_DIR = Path("/home/dev/Development/irStudy/ICRP_OSCE_Preparation")
FLASHCARD_FILE = Path("/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json")

# Category targets and current counts
CATEGORY_INFO = {
    "differentials": {"current": 51, "target": 150, "needed": 99},  # Note: combining 48 + 3
    "img_mistake": {"current": 46, "target": 150, "needed": 104},
    "physical_exam": {"current": 49, "target": 150, "needed": 101},
    "australian": {"current": 64, "target": 150, "needed": 86},
    "red_flag": {"current": 89, "target": 150, "needed": 61},
    "communication": {"current": 42, "target": 100, "needed": 58}
}


def load_existing_flashcards():
    """Load existing flashcards from JSON file"""
    with open(FLASHCARD_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def extract_list_items_from_section(soup, section_heading, max_items=10):
    """Extract list items following a section heading"""
    items = []

    # Find next sibling elements until we hit another heading
    current = section_heading.find_next_sibling()

    while current and len(items) < max_items:
        if current.name and current.name.startswith('h'):  # Stop at next heading
            break

        if current.name in ['ul', 'ol']:
            li_elements = current.find_all('li', recursive=False)
            for li in li_elements:
                text = li.get_text(separator=' ', strip=True)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                if len(text) > 20 and len(text) < 600:
                    items.append(text)

                if len(items) >= max_items:
                    break

        current = current.find_next_sibling()

    return items


def extract_differentials(html_file):
    """Extract differential diagnosis flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find differential sections
    patterns = [
        re.compile(r'differential.*diagnosis', re.IGNORECASE),
        re.compile(r'top\s+\d+\s+differential', re.IGNORECASE),
        re.compile(r'causes?\s+of', re.IGNORECASE),
    ]

    for pattern in patterns:
        headings = soup.find_all(['h2', 'h3', 'h4'], string=pattern)

        for heading in headings:
            section_title = heading.get_text(strip=True)
            items = extract_list_items_from_section(soup, heading, max_items=5)

            for item in items:
                # Try to split into diagnosis name and features
                if ':' in item:
                    parts = item.split(':', 1)
                    diagnosis = parts[0].strip()
                    features = parts[1].strip()

                    # Remove common prefixes
                    diagnosis = re.sub(r'^\d+\.\s*', '', diagnosis)
                    diagnosis = re.sub(r'^[❌✓✗]\s*', '', diagnosis)

                    card = {
                        "front": f"Differential: {diagnosis}",
                        "back": features,
                        "deck": "Medicine",
                        "tags": ["differentials", "medium"],
                        "source": str(html_file.relative_to(BASE_DIR.parent)),
                        "difficulty": "medium",
                        "category": "differentials"
                    }
                    cards.append(card)
                else:
                    # Use section title as context
                    condition = section_title.replace('Differential Diagnosis', '').replace(':', '').strip()

                    card = {
                        "front": f"Differential for {condition}:",
                        "back": item,
                        "deck": "Medicine",
                        "tags": ["differentials", "medium"],
                        "source": str(html_file.relative_to(BASE_DIR.parent)),
                        "difficulty": "medium",
                        "category": "differentials"
                    }
                    cards.append(card)

    return cards


def extract_img_mistakes(html_file):
    """Extract IMG mistakes flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find IMG mistake sections
    mistake_headings = soup.find_all(['h2', 'h3', 'h4'],
                                     string=re.compile(r'IMG.*mistake|common.*error|pitfall', re.IGNORECASE))

    for heading in mistake_headings:
        section_title = heading.get_text(strip=True)
        items = extract_list_items_from_section(soup, heading, max_items=8)

        for item in items:
            # Clean up the mistake text
            item = re.sub(r'^[❌✗X]\s*', '', item)
            item = re.sub(r'^\d+\.\s*', '', item)

            # Try to extract mistake and correction
            if '→' in item or '->' in item:
                parts = re.split(r'→|->',item)
                mistake = parts[0].strip()
                correction = parts[1].strip() if len(parts) > 1 else ""

                card = {
                    "front": f"IMG Mistake: {mistake}",
                    "back": f"Correct approach: {correction}",
                    "deck": "IMG Common Mistakes",
                    "tags": ["img_mistake", "medium"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "medium",
                    "category": "img_mistake"
                }
            elif 'NOT' in item or 'Don\'t' in item or 'Never' in item:
                card = {
                    "front": "What to avoid:",
                    "back": item,
                    "deck": "IMG Common Mistakes",
                    "tags": ["img_mistake", "medium"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "medium",
                    "category": "img_mistake"
                }
            else:
                card = {
                    "front": f"Common IMG mistake in {section_title.split(':')[0].strip()}:",
                    "back": item,
                    "deck": "IMG Common Mistakes",
                    "tags": ["img_mistake", "medium"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "medium",
                    "category": "img_mistake"
                }

            cards.append(card)

    return cards


def extract_physical_exam(html_file):
    """Extract physical examination flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # IPPA components
    ippa_components = ['Inspection', 'Palpation', 'Percussion', 'Auscultation']

    for component in ippa_components:
        headings = soup.find_all(['h2', 'h3', 'h4'], string=re.compile(component, re.IGNORECASE))

        for heading in headings:
            section_title = heading.get_text(strip=True)
            items = extract_list_items_from_section(soup, heading, max_items=4)

            # Determine exam type from file name
            file_name = html_file.stem
            exam_type = "General"

            if "Cardiovascular" in file_name or "Respiratory" in file_name:
                exam_type = "Cardiovascular/Respiratory"
            elif "Abdominal" in file_name:
                exam_type = "Abdominal"
            elif "Neurological" in file_name:
                exam_type = "Neurological"
            elif "Musculoskeletal" in file_name:
                exam_type = "Musculoskeletal"

            for item in items:
                card = {
                    "front": f"Physical Exam ({component}) - {exam_type}:",
                    "back": item,
                    "deck": "Physical Examination",
                    "tags": ["physical_exam", "medium"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "medium",
                    "category": "physical_exam"
                }
                cards.append(card)

    return cards


def extract_red_flags(html_file):
    """Extract red flag flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find red flag sections
    red_flag_headings = soup.find_all(['h2', 'h3', 'h4'],
                                      string=re.compile(r'red flag|emergency|must not miss|critical', re.IGNORECASE))

    for heading in red_flag_headings:
        items = extract_list_items_from_section(soup, heading, max_items=6)

        for item in items:
            # Clean up
            item = re.sub(r'^[🚨⚠]\s*', '', item)

            # Extract condition if present
            if ':' in item:
                parts = item.split(':', 1)
                condition = parts[0].strip()
                features = parts[1].strip()

                card = {
                    "front": f"🚨 RED FLAG: {condition}",
                    "back": features,
                    "deck": "Red Flags",
                    "tags": ["red_flag", "hard"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "hard",
                    "category": "red_flag"
                }
            else:
                card = {
                    "front": "🚨 RED FLAG:",
                    "back": item,
                    "deck": "Red Flags",
                    "tags": ["red_flag", "hard"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "hard",
                    "category": "red_flag"
                }

            cards.append(card)

    return cards


def extract_communication(html_file):
    """Extract communication flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # Find communication-related sections
    comm_headings = soup.find_all(['h2', 'h3', 'h4'],
                                  string=re.compile(r'SPIKES|communication|empathy|breaking bad news|what to say|phrases?', re.IGNORECASE))

    for heading in comm_headings:
        section_title = heading.get_text(strip=True)
        items = extract_list_items_from_section(soup, heading, max_items=5)

        for item in items:
            # Check if it contains a direct quote
            quotes = re.findall(r'"([^"]+)"', item)

            if quotes:
                for quote in quotes:
                    if len(quote) > 15:
                        card = {
                            "front": f"Communication phrase: {section_title.split(':')[0].strip()}",
                            "back": f'"{quote}"',
                            "deck": "Communication",
                            "tags": ["communication", "easy"],
                            "source": str(html_file.relative_to(BASE_DIR.parent)),
                            "difficulty": "easy",
                            "category": "communication"
                        }
                        cards.append(card)
            else:
                card = {
                    "front": f"Communication strategy: {section_title.split(':')[0].strip()}",
                    "back": item,
                    "deck": "Communication",
                    "tags": ["communication", "medium"],
                    "source": str(html_file.relative_to(BASE_DIR.parent)),
                    "difficulty": "medium",
                    "category": "communication"
                }
                cards.append(card)

    return cards


def extract_australian_context(html_file):
    """Extract Australian context flashcards"""
    cards = []

    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
        soup = BeautifulSoup(content, 'html.parser')

    # Extract eTG references
    etg_pattern = r'eTG\s+\d{4}[^<\n.]{10,300}'
    matches = re.finditer(etg_pattern, content, re.IGNORECASE)

    for match in matches:
        text = match.group(0).strip()
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags

        if len(text) > 20 and len(text) < 400:
            card = {
                "front": "Australian guideline (eTG):",
                "back": text,
                "deck": "Australian Context",
                "tags": ["australian", "easy"],
                "source": str(html_file.relative_to(BASE_DIR.parent)),
                "difficulty": "easy",
                "category": "australian"
            }
            cards.append(card)

    # Extract PBS mentions
    pbs_pattern = r'PBS[^<\n.]{10,200}'
    matches = re.finditer(pbs_pattern, content, re.IGNORECASE)

    for match in matches:
        text = match.group(0).strip()
        text = re.sub(r'<[^>]+>', '', text)

        if len(text) > 20 and len(text) < 300:
            card = {
                "front": "PBS (Pharmaceutical Benefits Scheme):",
                "back": text,
                "deck": "Australian Context",
                "tags": ["australian", "easy"],
                "source": str(html_file.relative_to(BASE_DIR.parent)),
                "difficulty": "easy",
                "category": "australian"
            }
            cards.append(card)

    # Extract Medicare references
    medicare_pattern = r'Medicare[^<\n.]{10,200}'
    matches = re.finditer(medicare_pattern, content, re.IGNORECASE)

    for match in matches:
        text = match.group(0).strip()
        text = re.sub(r'<[^>]+>', '', text)

        if len(text) > 20 and len(text) < 300:
            card = {
                "front": "Medicare in Australia:",
                "back": text,
                "deck": "Australian Context",
                "tags": ["australian", "easy"],
                "source": str(html_file.relative_to(BASE_DIR.parent)),
                "difficulty": "easy",
                "category": "australian"
            }
            cards.append(card)

    return cards


def main():
    """Main extraction process"""
    print("="*80)
    print("PHASE 1.1 FLASHCARD EXTRACTION")
    print("="*80)
    print()

    # Load existing flashcards
    print("Loading existing flashcards...")
    existing_data = load_existing_flashcards()
    current_count = len(existing_data['cards'])
    next_id = max(card['id'] for card in existing_data['cards']) + 1

    print(f"Current flashcards: {current_count}")
    print(f"Next card ID: {next_id}")
    print()

    # Get all HTML files
    all_html_files = list(BASE_DIR.glob("**/*.html"))
    print(f"Found {len(all_html_files)} HTML files")
    print()

    # Extract by category priority
    new_cards_by_category = defaultdict(list)

    # Track existing card content to avoid duplicates
    existing_backs = set()
    for card in existing_data['cards']:
        existing_backs.add(card['back'].lower().strip())

    print("Extracting flashcards by category...")
    print("-"*80)

    for html_file in all_html_files:
        try:
            # Extract each category
            for category, extractor in [
                ('differentials', extract_differentials),
                ('img_mistake', extract_img_mistakes),
                ('physical_exam', extract_physical_exam),
                ('red_flag', extract_red_flags),
                ('communication', extract_communication),
                ('australian', extract_australian_context)
            ]:
                cards = extractor(html_file)

                # Filter out duplicates
                for card in cards:
                    back_normalized = card['back'].lower().strip()
                    if back_normalized not in existing_backs:
                        new_cards_by_category[category].append(card)
                        existing_backs.add(back_normalized)

        except Exception as e:
            print(f"  Error processing {html_file.name}: {e}")

    print()
    print("Extraction complete. Cards extracted by category:")
    for category, cards in new_cards_by_category.items():
        print(f"  {category}: {len(cards)} new cards")

    # Balance categories to meet targets
    print()
    print("Balancing categories to meet targets...")
    print("-"*80)

    final_new_cards = []

    for category, info in CATEGORY_INFO.items():
        needed = info['needed']
        available = new_cards_by_category[category]

        # Take what we need (or all if we don't have enough)
        cards_to_add = available[:needed]
        final_new_cards.extend(cards_to_add)

        print(f"  {category:20s}: needed {needed:3d}, found {len(available):3d}, adding {len(cards_to_add):3d}")

    # Assign IDs to new cards
    for i, card in enumerate(final_new_cards):
        card['id'] = next_id + i

    # Combine with existing cards
    all_cards = existing_data['cards'] + final_new_cards

    # Update data structure
    final_data = {
        "metadata": {
            "total_cards": len(all_cards),
            "created": "2025-12-16",
            "last_updated": "2025-12-16",
            "version": "1.1",
            "description": "ICRP AMC Clinical OSCE flashcards - Australian context"
        },
        "cards": all_cards
    }

    # Save to file
    print()
    print("Saving flashcards...")

    with open(FLASHCARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)

    print(f"✓ Saved to: {FLASHCARD_FILE}")

    # Generate verification report
    print()
    print("="*80)
    print("VERIFICATION REPORT")
    print("="*80)
    print()

    # Count final categories
    final_counts = defaultdict(int)
    for card in all_cards:
        cat = card.get('category', 'unknown')
        # Normalize category name
        if cat == 'differential':
            cat = 'differentials'
        final_counts[cat] += 1

    print(f"Total flashcards: {len(all_cards)}")
    print(f"New cards added: {len(final_new_cards)}")
    print()
    print("Category breakdown:")
    print("-"*80)

    for category, info in CATEGORY_INFO.items():
        count = final_counts[category]
        target = info['target']
        progress = (count / target * 100) if target > 0 else 0
        status = "✓" if count >= target * 0.9 else "→"

        print(f"  {status} {category:20s}: {count:3d}/{target:3d} ({progress:5.1f}%)")

    print()
    print("="*80)
    print("EXTRACTION COMPLETE!")
    print("="*80)


if __name__ == "__main__":
    main()
