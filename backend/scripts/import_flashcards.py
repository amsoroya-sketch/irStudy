#!/usr/bin/env python3
"""
Import cleaned flashcards from JSON into the study_cards PostgreSQL table.

DEV-004 — Database Engineer
Purpose: Idempotent bulk import of 310 public study cards.

Usage:
    cd /home/dev/Development/irStudy/backend
    source venv/bin/activate
    python scripts/import_flashcards.py --cleaned-json ../ICRP_Program_Resources/Flashcards/flashcard_data_cleaned.json
    python scripts/import_flashcards.py --cleaned-json ../ICRP_Program_Resources/Flashcards/flashcard_data_cleaned.json --dry-run
    python scripts/import_flashcards.py --cleaned-json ../ICRP_Program_Resources/Flashcards/flashcard_data_cleaned.json --db-url postgresql://user:pass@host:port/db
"""

import sys
import json
import re
import argparse
import logging
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.db.models import StudyCard, MedicalSpecialty, DifficultyLevel
from src.db.base import Base, get_database_url


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# Pre-compute valid enum values for fast validation
VALID_SPECIALTIES = {e.value for e in MedicalSpecialty}
VALID_DIFFICULTIES = {e.value for e in DifficultyLevel}
CARD_ID_RE = re.compile(r"^[A-Z]+-CARD-\d{4}$")
BATCH_SIZE = 50


def load_cards(json_path: Path) -> list[dict[str, Any]]:
    """Load and return the list of card dicts from the cleaned JSON."""
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    cards = data.get("cards", [])
    if not cards:
        # Fallback: maybe the JSON is a flat list
        if isinstance(data, list):
            cards = data

    logger.info(f"Loaded {len(cards)} cards from {json_path}")
    return cards


def validate_card(card: dict[str, Any], index: int) -> tuple[bool, list[str]]:
    """
    Validate a single card dict.
    Returns (is_valid, list_of_error_messages).
    """
    errors: list[str] = []

    # card_id
    card_id = card.get("card_id", "")
    if not card_id:
        errors.append("missing card_id")
    elif not CARD_ID_RE.match(str(card_id)):
        errors.append(f"card_id '{card_id}' does not match regex ^[A-Z]+-CARD-\\d{{4}}$")

    # specialty
    specialty = card.get("specialty", "")
    if not specialty:
        errors.append("missing specialty")
    elif specialty not in VALID_SPECIALTIES:
        errors.append(f"invalid specialty '{specialty}'")

    # difficulty
    difficulty = card.get("difficulty", "")
    if not difficulty:
        errors.append("missing difficulty")
    elif difficulty not in VALID_DIFFICULTIES:
        errors.append(f"invalid difficulty '{difficulty}'")

    # question
    question = card.get("question", "")
    if not question or not str(question).strip():
        errors.append("empty question")

    # answer
    answer = card.get("answer", "")
    if not answer or not str(answer).strip():
        errors.append("empty answer")

    # citations
    citations = card.get("citations", [])
    if not isinstance(citations, list):
        errors.append("citations is not a list")
    elif len(citations) == 0:
        errors.append("citations list is empty")
    else:
        if not all(isinstance(c, dict) for c in citations):
            errors.append("citations contains non-dict items")

    return len(errors) == 0, errors


def build_studycard(card: dict[str, Any]) -> StudyCard:
    """Construct a StudyCard ORM instance from a validated dict."""
    difficulty_str = card.get("difficulty", "medium")
    specialty_str = card.get("specialty", "general_practice")

    # Map strings to enum members
    difficulty = DifficultyLevel(difficulty_str)
    specialty = MedicalSpecialty(specialty_str)

    return StudyCard(
        user_id=None,
        session_id=None,
        card_id=str(card["card_id"]).strip(),
        specialty=specialty,
        topic=str(card.get("topic", "")).strip(),
        subtopic=str(card.get("subtopic", "")).strip() if card.get("subtopic") else None,
        question=str(card["question"]).strip(),
        answer=str(card["answer"]).strip(),
        explanation=str(card["explanation"]).strip() if card.get("explanation") else None,
        citations=card["citations"],
        difficulty=difficulty,
        tags=card.get("tags") if card.get("tags") else None,
        card_type=str(card.get("card_type", "concept")).strip(),
        next_review_date=datetime.now(timezone.utc),
        interval_days=1,
        ease_factor=2.5,
        repetitions=0,
        is_active=True,
    )


def import_flashcards(
    cleaned_json: str,
    db_url: str | None = None,
    dry_run: bool = False,
) -> int:
    """
    Main import routine.
    Returns exit code (0 = success, 1 = failure).
    """
    print("=" * 60)
    print("Flashcard Import Pipeline — DEV-004")
    print("=" * 60)
    print(f"Source JSON : {cleaned_json}")
    print(f"Mode        : {'DRY RUN' if dry_run else 'LIVE IMPORT'}")
    print(f"DB override : {'yes' if db_url else 'no (using project defaults)'}")
    print("")

    json_path = Path(cleaned_json)
    if not json_path.exists():
        logger.error(f"JSON file not found: {json_path}")
        return 1

    # ------------------------------------------------------------------
    # 1. Load cards
    # ------------------------------------------------------------------
    try:
        cards = load_cards(json_path)
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load JSON: {e}")
        return 1

    if not cards:
        logger.warning("No cards found in JSON.")
        return 0

    # ------------------------------------------------------------------
    # 2. Validate all cards up-front
    # ------------------------------------------------------------------
    valid_cards: list[dict[str, Any]] = []
    validation_failures: list[tuple[int, str, list[str]]] = []

    for idx, card in enumerate(cards, start=1):
        is_valid, errors = validate_card(card, idx)
        if is_valid:
            valid_cards.append(card)
        else:
            validation_failures.append((idx, card.get("card_id", "N/A"), errors))

    logger.info(f"Validation: {len(valid_cards)} passed, {len(validation_failures)} failed")

    if validation_failures:
        print("\n⚠️  Validation failures (will be skipped):")
        for idx, card_id, errors in validation_failures:
            print(f"  Card #{idx} (id={card_id}): {', '.join(errors)}")
        print("")

    if dry_run:
        print("\n🏁 DRY RUN complete. No database changes made.")
        print(f"  Would import : {len(valid_cards)}")
        print(f"  Would skip   : {len(validation_failures)} (validation)")
        return 0

    if not valid_cards:
        logger.warning("No valid cards to import.")
        return 0

    # ------------------------------------------------------------------
    # 3. Connect to database
    # ------------------------------------------------------------------
    try:
        if db_url:
            final_db_url = db_url
        else:
            final_db_url = get_database_url()

        engine = create_engine(final_db_url)
        # Ensure tables exist (no-op if alembic already ran)
        Base.metadata.create_all(engine)
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return 1

    # ------------------------------------------------------------------
    # 4. Import in batches (idempotent)
    # ------------------------------------------------------------------
    imported_count = 0
    skipped_count = 0
    error_count = 0
    batch: list[StudyCard] = []

    print("Importing cards...")
    print("-" * 60)

    for card in valid_cards:
        card_id = str(card["card_id"]).strip()

        try:
            # Idempotency check
            existing = db.query(StudyCard).filter(StudyCard.card_id == card_id).first()
            if existing:
                skipped_count += 1
                continue

            studycard = build_studycard(card)
            batch.append(studycard)

            # Commit batch when full
            if len(batch) >= BATCH_SIZE:
                db.add_all(batch)
                db.commit()
                imported_count += len(batch)
                logger.info(f"  Committed batch of {len(batch)} (total imported: {imported_count})")
                batch.clear()

        except IntegrityError:
            db.rollback()
            skipped_count += 1
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"  DB error on card {card_id}: {e}")
            error_count += 1
        except Exception as e:
            db.rollback()
            logger.error(f"  Unexpected error on card {card_id}: {e}")
            error_count += 1

    # Commit remaining cards in final partial batch
    if batch:
        try:
            db.add_all(batch)
            db.commit()
            imported_count += len(batch)
            logger.info(f"  Committed final batch of {len(batch)} (total imported: {imported_count})")
        except IntegrityError:
            db.rollback()
            skipped_count += len(batch)
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"  DB error on final batch: {e}")
            error_count += len(batch)

    # ------------------------------------------------------------------
    # 5. Summary
    # ------------------------------------------------------------------
    total_in_db = db.query(StudyCard).count()
    db.close()

    print("-" * 60)
    print("\n✅ Import complete!")
    print(f"  Imported         : {imported_count}")
    print(f"  Skipped (exist)  : {skipped_count}")
    print(f"  Validation fails : {len(validation_failures)}")
    print(f"  Errors           : {error_count}")
    print(f"  Total in DB now  : {total_in_db}")
    print("")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import cleaned flashcards into PostgreSQL")
    parser.add_argument(
        "--cleaned-json",
        required=True,
        help="Path to flashcard_data_cleaned.json",
    )
    parser.add_argument(
        "--db-url",
        default=None,
        help="Override database URL (e.g., postgresql://user:pass@localhost:5432/db)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only; do not write to database",
    )

    args = parser.parse_args()

    exit_code = import_flashcards(
        cleaned_json=args.cleaned_json,
        db_url=args.db_url,
        dry_run=args.dry_run,
    )
    sys.exit(exit_code)
