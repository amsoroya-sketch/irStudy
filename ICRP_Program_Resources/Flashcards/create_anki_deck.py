#!/usr/bin/env python3
"""
ICRP AMC Clinical Anki Deck Generator

Purpose: Creates a professional Anki deck (.apkg) from flashcard_data.json
         with proper subdeck hierarchy and Australian medical styling.

Usage:
    python3 create_anki_deck.py
    OR
    ./venv/bin/python create_anki_deck.py

Output: ICRP_AMC_Clinical.apkg (ready to import into Anki)

Requirements: genanki (pip install genanki)
"""

import json
import genanki
import random
from collections import defaultdict
from datetime import datetime

# Define the model ID (must be unique and consistent)
MODEL_ID = random.randrange(1 << 30, 1 << 31)

# Custom CSS styling for Australian medical context
AUSTRALIAN_MEDICAL_CSS = """
.card {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 20px;
    text-align: left;
    color: #2c3e50;
    background-color: #ffffff;
    padding: 20px;
    line-height: 1.6;
}

/* Front side styling */
.front {
    font-size: 22px;
    font-weight: 600;
    color: #34495e;
    margin-bottom: 15px;
    border-left: 4px solid #3498db;
    padding-left: 15px;
}

/* Back side styling */
.back {
    font-size: 19px;
    color: #2c3e50;
    margin-top: 15px;
}

/* Red flag styling */
.red-flag {
    background-color: #ffe5e5;
    border-left: 4px solid #e74c3c;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

.red-flag .front {
    color: #c0392b;
    border-left: none;
}

/* Tags and metadata */
.tags {
    font-size: 14px;
    color: #7f8c8d;
    margin-top: 20px;
    font-style: italic;
}

.source {
    font-size: 12px;
    color: #95a5a6;
    margin-top: 10px;
    border-top: 1px solid #ecf0f1;
    padding-top: 10px;
}

/* Mobile-friendly adjustments */
@media (max-width: 600px) {
    .card {
        font-size: 18px;
        padding: 15px;
    }
    .front {
        font-size: 20px;
    }
    .back {
        font-size: 17px;
    }
}

/* Difficulty indicators */
.difficulty-easy {
    color: #27ae60;
    font-weight: bold;
}

.difficulty-medium {
    color: #f39c12;
    font-weight: bold;
}

.difficulty-hard {
    color: #e74c3c;
    font-weight: bold;
}

/* Australian flag emoji for Australian context cards */
.australian-context::before {
    content: "🇦🇺 ";
}

/* IMG mistake indicator */
.img-mistake {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
}

/* Critical/Emergency styling */
.critical {
    font-weight: bold;
}

.critical::before {
    content: "🚨 ";
}

/* List styling */
ul, ol {
    margin: 10px 0;
    padding-left: 25px;
}

li {
    margin: 5px 0;
}

/* Code/medical term styling */
code {
    background-color: #f8f9fa;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}
"""

# HTML template for front of card
FRONT_TEMPLATE = """
<div class="card {{Tags}}">
    <div class="front">{{Front}}</div>
</div>
"""

# HTML template for back of card
BACK_TEMPLATE = """
<div class="card {{Tags}}">
    <div class="front">{{Front}}</div>
    <hr>
    <div class="back">{{Back}}</div>
    <div class="tags">Tags: {{Tags}}</div>
    <div class="source">Source: {{Source}}</div>
</div>
"""

# Create custom note model for ICRP flashcards
def create_note_model():
    """Creates a custom Anki note model with Australian medical styling"""
    model = genanki.Model(
        MODEL_ID,
        'ICRP AMC Clinical Model',
        fields=[
            {'name': 'Front'},
            {'name': 'Back'},
            {'name': 'Tags'},
            {'name': 'Source'},
        ],
        templates=[
            {
                'name': 'ICRP Card',
                'qfmt': FRONT_TEMPLATE,
                'afmt': BACK_TEMPLATE,
            },
        ],
        css=AUSTRALIAN_MEDICAL_CSS
    )
    return model


def parse_deck_hierarchy(deck_name):
    """
    Parses deck name into hierarchical structure.

    Examples:
        'Medicine_Cardiology' -> 'ICRP_AMC_Clinical::Medicine::Cardiology'
        'ObGyn' -> 'ICRP_AMC_Clinical::ObGyn'
        'Red Flags' -> 'ICRP_AMC_Clinical::Red_Flags_Critical'
    """
    # Base deck name
    base = "ICRP_AMC_Clinical"

    # Special mappings for cleaner hierarchy
    deck_mappings = {
        'Red Flags': 'Red_Flags_Critical',
        'Australian Context': 'Australian_Context',
        'IMG Common Mistakes': 'IMG_Common_Mistakes',
        'Physical Examination': 'Physical_Examination',
    }

    # Apply mapping if exists
    if deck_name in deck_mappings:
        deck_name = deck_mappings[deck_name]

    # Handle Medicine subspecialties
    if deck_name.startswith('Medicine_'):
        parts = deck_name.split('_')
        if len(parts) == 2 and parts[1] != 'General':
            return f"{base}::Medicine::{parts[1]}"
        elif parts[1] == 'General':
            return f"{base}::Medicine"

    # Replace spaces and underscores
    deck_name = deck_name.replace(' ', '_')

    return f"{base}::{deck_name}"


def create_anki_deck():
    """Main function to create the Anki deck from flashcard_data.json"""

    print("=" * 60)
    print("ICRP AMC Clinical Anki Deck Generator")
    print("=" * 60)
    print()

    # Load flashcard data
    print("Loading flashcard data...")
    with open('flashcard_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    metadata = data['metadata']
    cards = data['cards']

    print(f"✓ Loaded {metadata['total_cards']} cards")
    print(f"  Created: {metadata['created']}")
    print(f"  Version: {metadata['version']}")
    print()

    # Create the note model
    note_model = create_note_model()

    # Group cards by deck
    deck_groups = defaultdict(list)
    for card in cards:
        deck_name = card['deck']
        deck_groups[deck_name].append(card)

    print("Deck structure:")
    for deck_name, deck_cards in sorted(deck_groups.items()):
        print(f"  {deck_name}: {len(deck_cards)} cards")
    print()

    # Create deck objects for each subdeck
    decks_dict = {}
    for deck_name in deck_groups.keys():
        hierarchical_name = parse_deck_hierarchy(deck_name)
        # Generate unique deck ID based on hierarchical name
        deck_id = random.randrange(1 << 30, 1 << 31)
        deck = genanki.Deck(deck_id, hierarchical_name)
        decks_dict[deck_name] = deck

    # Add notes to respective decks
    print("Creating notes...")
    card_count = 0

    for card in cards:
        deck_name = card['deck']
        deck = decks_dict[deck_name]

        # Prepare fields
        front = card['front']
        back = card['back']
        tags = ' '.join(card.get('tags', []))
        source = card.get('source', 'Unknown')

        # Add CSS classes based on card attributes
        css_classes = []

        # Add difficulty class
        difficulty = card.get('difficulty', 'medium')
        css_classes.append(f'difficulty-{difficulty}')

        # Add category class
        category = card.get('category', '')
        if category:
            css_classes.append(category.replace('_', '-'))

        # Add red flag class
        if 'red-flag' in card.get('tags', []) or 'red_flag' in card.get('tags', []):
            css_classes.append('red-flag')

        # Add IMG mistake class
        if 'img_mistake' in card.get('tags', []):
            css_classes.append('img-mistake')

        # Add critical class
        if 'critical' in card.get('tags', []):
            css_classes.append('critical')

        # Add Australian context class
        if 'australian' in card.get('tags', []):
            css_classes.append('australian-context')

        # Create tags field with CSS classes
        tags_with_classes = ' '.join(css_classes) + ' ' + tags

        # Create the note
        note = genanki.Note(
            model=note_model,
            fields=[front, back, tags_with_classes, source],
            tags=card.get('tags', [])
        )

        deck.add_note(note)
        card_count += 1

    print(f"✓ Created {card_count} notes")
    print()

    # Create package with all decks
    print("Generating .apkg file...")
    package = genanki.Package(list(decks_dict.values()))

    # Save the package
    output_file = 'ICRP_AMC_Clinical.apkg'
    package.write_to_file(output_file)

    print(f"✓ Successfully created: {output_file}")
    print()

    # Print summary
    print("=" * 60)
    print("DECK CREATION SUMMARY")
    print("=" * 60)
    print()
    print(f"Output file: {output_file}")
    print(f"Total cards: {card_count}")
    print(f"Total decks: {len(decks_dict)}")
    print()

    print("Subdeck hierarchy:")
    for deck_name in sorted(deck_groups.keys()):
        hierarchical_name = parse_deck_hierarchy(deck_name)
        card_count_per_deck = len(deck_groups[deck_name])
        print(f"  {hierarchical_name}")
        print(f"    └─ {card_count_per_deck} cards")
    print()

    # Card statistics
    print("Card statistics by category:")
    category_counts = defaultdict(int)
    for card in cards:
        category = card.get('category', 'general')
        category_counts[category] += 1

    for category, count in sorted(category_counts.items()):
        print(f"  {category}: {count} cards")
    print()

    print("Card statistics by difficulty:")
    difficulty_counts = defaultdict(int)
    for card in cards:
        difficulty = card.get('difficulty', 'medium')
        difficulty_counts[difficulty] += 1

    for difficulty, count in sorted(difficulty_counts.items()):
        print(f"  {difficulty}: {count} cards")
    print()

    print("=" * 60)
    print("NEXT STEPS")
    print("=" * 60)
    print()
    print("1. Open Anki Desktop")
    print("2. Click 'File > Import'")
    print("3. Select: ICRP_AMC_Clinical.apkg")
    print("4. Verify all 750 cards imported correctly")
    print("5. Check subdeck structure matches requirements")
    print("6. Start studying!")
    print()
    print("Mobile sync:")
    print("- Sync to AnkiWeb (free account)")
    print("- Download AnkiMobile (iOS) or AnkiDroid (Android)")
    print("- Sign in and sync")
    print()
    print("=" * 60)


if __name__ == '__main__':
    try:
        create_anki_deck()
    except FileNotFoundError:
        print("ERROR: flashcard_data.json not found in current directory")
        print("Please run this script from the Flashcards directory")
        exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
