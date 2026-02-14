#!/usr/bin/env python3
"""
Merge flashcard JSON data into the HTML file to create a standalone flashcard app.
"""

import json


def merge_flashcards():
    # Read the JSON data
    with open("flashcard_data.json", "r", encoding="utf-8") as f:
        flashcard_data = json.load(f)

    # Read the HTML template
    with open("ICRP_Flashcards_Interactive.html", "r", encoding="utf-8") as f:
        html_content = f.read()

    # Convert cards data to JavaScript (compact to save space)
    cards_json = json.dumps(flashcard_data["cards"])

    # Replace the empty allCards array with actual data
    html_content = html_content.replace(
        "allCards: [],", f"allCards: {cards_json},", 1  # Only replace first occurrence
    )

    # Modify init() to auto-load the embedded cards
    old_init = """init() {
                this.loadProgress();
                this.setupEventListeners();
            },"""

    new_init = """init() {
                // Auto-load embedded flashcards
                if (this.allCards.length > 0) {
                    this.filteredCards = [...this.allCards];
                    this.showCard(0);
                    this.updateStats();
                    this.updateCategoryFilter();
                    this.updateDeckFilter();
                    document.getElementById('uploadSection').style.display = 'none';
                    document.getElementById('studySection').style.display = 'block';
                }
                this.loadProgress();
                this.setupEventListeners();
            },"""

    html_content = html_content.replace(old_init, new_init)

    # Write the merged HTML file
    with open("flashcards_standalone.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ Created standalone flashcard app: flashcards_standalone.html")
    print(f"📊 Embedded {len(flashcard_data['cards'])} flashcards")
    print(f"🎯 Total cards: {flashcard_data['metadata']['total_cards']}")
    print(f"\n💡 Open 'flashcards_standalone.html' in your browser to use!")
    print(f"\n📁 Location: ICRP_Program_Resources/Flashcards/flashcards_standalone.html")


if __name__ == "__main__":
    merge_flashcards()
