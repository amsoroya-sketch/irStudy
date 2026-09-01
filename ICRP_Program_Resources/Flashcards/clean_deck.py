#!/usr/bin/env python3
"""
Flashcard Deck Cleaner for Medical Education Platform
Cleans 750-card ICRP flashcard deck for database import.
"""

import json
import re
from collections import Counter
from datetime import datetime

INPUT_PATH = '/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json'
OUTPUT_PATH = '/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data_cleaned.json'

# ---------------------------------------------------------------------------
# 1. Read input
# ---------------------------------------------------------------------------
with open(INPUT_PATH) as f:
    data = json.load(f)

cards = data['cards']
original_count = len(cards)

# ---------------------------------------------------------------------------
# 2. Cleaning helpers
# ---------------------------------------------------------------------------

# Deck name → specialty mapping
DECK_TO_SPECIALTY = {
    "Medicine": "general_practice",
    "Medicine_General": "general_practice",
    "General": "general_practice",
    "Medicine_Gastroenterology": "gastroenterology",
    "Medicine_Neurology": "neurology",
    "Medicine_Cardiorespiratory": "cardiology",
    "Medicine_Cardiology": "cardiology",
    "Medicine_Emergency": "emergency_medicine",
    "Medicine_Endocrinology": "endocrinology",
    "Medicine_ENT": "general_practice",
    "Surgery": "surgery",
    "ObGyn": "obstetrics_gynaecology",
    "Paediatrics": "paediatrics",
    "Psychiatry": "psychiatry",
    "Australian Context": "general_practice",
    "IMG Common Mistakes": "general_practice",
    "Red Flags": "general_practice",
    "Communication": "general_practice",
    "Physical Examination": "general_practice",
    "Ethics_Communication": "general_practice",
}

# Category → card_type mapping
CATEGORY_TO_CARD_TYPE = {
    "red_flags": "clinical_pearl",
    "differentials": "concept",
    "physical_exam": "clinical_pearl",
    "communication": "concept",
    "australian": "concept",
    "img_mistake": "clinical_pearl",
}


def clean_front(text: str) -> str:
    """Strip template artifacts and normalize spacing."""
    text = text.strip()

    # Run artifact stripping repeatedly until stable (handles nested prefixes)
    for _ in range(10):  # safety limit
        prev = text

        # r'^(Differential for\s*)?\(?Generated IMMEDIATELY\)?:\s*'
        text = re.sub(r'^(Differential for\s*)?\(?Generated IMMEDIATELY\)?:\s*', '', text, flags=re.IGNORECASE)

        # r'^Common IMG mistake in\s*\d*\.?\s*Common IMG Mistakes\s*[❌:]?\s*'
        text = re.sub(r'^Common IMG mistake in\s*\d*\.?\s*Common IMG Mistakes\s*[❌:]?\s*', '', text, flags=re.IGNORECASE)

        # r'^Physical Exam \(([^)]+)\)\s*-\s*[^:]+:\s*' → replace with just the exam type
        def _physical_exam_repl(m):
            return m.group(1)
        text = re.sub(r'^Physical Exam \(([^)]+)\)\s*-\s*[^:]+:\s*', _physical_exam_repl, text, flags=re.IGNORECASE)

        # r'^Differential[:\s]+' → 'Differential: '
        text = re.sub(r'^Differential[\s:]*', 'Differential: ', text, flags=re.IGNORECASE)

        # r'^PBS \(Pharmaceutical Benefits Scheme\):?\s*' → keep the useful part
        text = re.sub(r'^PBS \(Pharmaceutical Benefits Scheme\):?\s*', '', text, flags=re.IGNORECASE)

        # r'^Medicare in Australia:?\s*' → keep the useful part
        text = re.sub(r'^Medicare in Australia:?\s*', '', text, flags=re.IGNORECASE)

        # r'^Australian context:?\s*' → keep the useful part
        text = re.sub(r'^Australian context:?\s*', '', text, flags=re.IGNORECASE)

        # r'^Australian:?\s*' → keep the useful part
        text = re.sub(r'^Australian:?\s*', '', text, flags=re.IGNORECASE)

        # r'^🚨 RED FLAG:\s*' → keep but standardize spacing
        text = re.sub(r'^🚨\s*RED FLAG:\s*', '🚨 RED FLAG: ', text)

        if text == prev:
            break

    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text)

    return text.strip()


def normalize_difficulty(d: str) -> str:
    d = (d or "").strip().lower()
    if d == "high":
        return "hard"
    if d in ("easy", "medium", "hard"):
        return d
    return "medium"


def generate_card_id(index: int, specialty: str) -> str:
    prefix = specialty.upper()[:4]
    return f"{prefix}-CARD-{index + 1:04d}"


def build_citations(card: dict) -> list:
    return [{
        "title": card.get("source") or "ICRP OSCE Preparation",
        "author": "ICRP",
        "year": "2025",
        "page": None,
        "content": "",
        "rag_confidence": None,
        "source_type": "textbook"
    }]


# ---------------------------------------------------------------------------
# 3. Clean each card
# ---------------------------------------------------------------------------
cleaned_cards = []
seen_norm_fronts = set()
removed_empty = 0
removed_duplicates = 0
removed_empty_front = 0

for card in cards:
    back = (card.get("back") or "").strip()
    front = (card.get("front") or "").strip()

    # Remove empty backs
    if len(back) < 10:
        removed_empty += 1
        continue

    # Clean front
    cleaned_front = clean_front(front)

    # Skip if front became empty after cleaning (no clinically meaningful question)
    if not cleaned_front:
        removed_empty_front += 1
        continue

    # Deduplicate by normalized front
    norm_front = cleaned_front.lower().strip()
    if norm_front in seen_norm_fronts:
        removed_duplicates += 1
        continue
    seen_norm_fronts.add(norm_front)

    # Normalize deck → specialty
    deck = card.get("deck", "")
    specialty = DECK_TO_SPECIALTY.get(deck, "general_practice")

    # Normalize difficulty
    difficulty = normalize_difficulty(card.get("difficulty"))

    # Map category
    category = card.get("category", "")
    card_type = CATEGORY_TO_CARD_TYPE.get(category, "concept")

    cleaned_cards.append({
        "_specialty": specialty,
        "_index": len(cleaned_cards),
        "topic": deck,
        "subtopic": category,
        "question": cleaned_front,
        "answer": back,
        "explanation": card.get("source") or "ICRP OSCE Preparation",
        "citations": build_citations(card),
        "difficulty": difficulty,
        "tags": card.get("tags", []),
        "card_type": card_type,
    })

# Assign final card_ids sequentially
for card in cleaned_cards:
    card["card_id"] = generate_card_id(card["_index"], card["_specialty"])
    card["specialty"] = card["_specialty"]
    del card["_specialty"]
    del card["_index"]

# ---------------------------------------------------------------------------
# 4. Build output
# ---------------------------------------------------------------------------
output = {
    "metadata": {
        "original_count": original_count,
        "cleaned_count": len(cleaned_cards),
        "removed_empty": removed_empty,
        "removed_duplicates": removed_duplicates,
        "removed_empty_front": removed_empty_front,
        "date_cleaned": "2026-05-26"
    },
    "cards": cleaned_cards
}

with open(OUTPUT_PATH, 'w') as f:
    json.dump(output, f, indent=2)

# ---------------------------------------------------------------------------
# 5. Print summary
# ---------------------------------------------------------------------------
print("=" * 60)
print("FLASHCARD DECK CLEANING SUMMARY")
print("=" * 60)
print(f"Original count:        {original_count}")
print(f"Cleaned count:         {len(cleaned_cards)}")
print(f"Removed (empty back):  {removed_empty}")
print(f"Removed (duplicates):  {removed_duplicates}")
print(f"Removed (empty front): {removed_empty_front}")
print(f"Total removed:         {original_count - len(cleaned_cards)}")
print()

# Breakdown by specialty
specialty_counts = Counter(c["specialty"] for c in cleaned_cards)
print("Breakdown by specialty:")
for spec, count in specialty_counts.most_common():
    print(f"  {spec:25s} {count:4d}")
print()

# Breakdown by difficulty
diff_counts = Counter(c["difficulty"] for c in cleaned_cards)
print("Breakdown by difficulty:")
for diff, count in diff_counts.most_common():
    print(f"  {diff:25s} {count:4d}")
print()

print(f"Output written to: {OUTPUT_PATH}")
print("=" * 60)
