#!/usr/bin/env python3
"""
Fix the standalone flashcard file with correct function names.
"""

import json

def fix_standalone():
    # Read the JSON data
    with open('flashcard_data.json', 'r', encoding='utf-8') as f:
        flashcard_data = json.load(f)

    # Read the original HTML template
    with open('ICRP_Flashcards_Interactive.html', 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Convert cards data to JavaScript
    cards_json = json.dumps(flashcard_data['cards'])

    # Replace the empty allCards array with actual data
    html_content = html_content.replace(
        'allCards: [],',
        f'allCards: {cards_json},',
        1
    )

    # Fix the init() function with CORRECT function names from the original code
    old_init = '''init() {
                this.loadProgress();
                this.setupEventListeners();
            },'''

    new_init = '''init() {
                // Auto-load embedded flashcards
                if (this.allCards.length > 0) {
                    this.filteredCards = [...this.allCards];

                    // Hide file input, show app
                    document.getElementById('fileInputWrapper').style.display = 'none';
                    document.getElementById('appContainer').style.display = 'block';

                    // Initialize app (using correct function names from original code)
                    this.populateFilters();
                    this.updateStats();
                    this.showCard();
                }
                this.loadProgress();
                this.setupEventListeners();
            },'''

    html_content = html_content.replace(old_init, new_init)

    # Write the fixed standalone file
    with open('flashcards_standalone.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ Fixed standalone flashcard app: flashcards_standalone.html")
    print(f"📊 Embedded {len(flashcard_data['cards'])} flashcards")
    print(f"🎯 Total cards: {flashcard_data['metadata']['total_cards']}")
    print(f"\n✅ Fixed function names:")
    print(f"   - populateFilters() ✓")
    print(f"   - updateStats() ✓")
    print(f"   - showCard() ✓")
    print(f"\n💡 Open 'flashcards_standalone.html' in your browser to use!")

if __name__ == '__main__':
    fix_standalone()
