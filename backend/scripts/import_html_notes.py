"""
Import HTML OSCE Notes Metadata

Scans 65 HTML files in /ICRP_OSCE_Preparation/ and imports metadata to database.
Files are served as static content - only metadata is stored.

USAGE:
    export DATABASE_PASSWORD=your_password
    python scripts/import_html_notes.py
"""

import os
import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db.base import get_database_url
from db.models import HTMLOSCENote


# Specialty mapping from directory names
SPECIALTY_MAP = {
    'Medicine': 'Medicine',
    'Surgery': 'Surgery',
    'Psychiatry': 'Psychiatry',
    'Paediatrics': 'Paediatrics',
    'ObGyn': 'Obstetrics & Gynecology',
    'Ethics_Communication': 'Ethics & Communication',
    'Mock_Stations': 'Mock OSCE Stations',
    'Musculoskeletal': 'Musculoskeletal',
    'Urology': 'Urology',
    'Ophthalmology': 'Ophthalmology',
}

# Category extraction patterns
CATEGORY_PATTERNS = {
    'History': r'(history|differentials)',
    'Physical Examination': r'(physical examination|exam)',
    'Emergency': r'(emergency|anaphylaxis|seizure|trauma)',
    'Communication': r'(communication|breaking bad news|counselling)',
    'Management': r'(management|treatment)',
    'Assessment': r'(assessment)',
}


def extract_title_from_html(html_content: str) -> str:
    """Extract title from HTML <title> tag"""
    soup = BeautifulSoup(html_content, 'html.parser')
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()

    # Fallback: try to find h1
    h1_tag = soup.find('h1')
    if h1_tag:
        return h1_tag.get_text().strip()

    return "Untitled OSCE Note"


def extract_preview_text(html_content: str) -> str:
    """Extract first 200 characters of text content"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style tags
    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = ' '.join(chunk for chunk in chunks if chunk)

    return text[:200] + "..." if len(text) > 200 else text


def extract_topics_from_html(html_content: str) -> list:
    """Extract topic keywords from HTML content"""
    soup = BeautifulSoup(html_content, 'html.parser')
    topics = []

    # Extract from h2 and h3 tags
    for header in soup.find_all(['h2', 'h3']):
        topic = header.get_text().strip()
        if len(topic) < 100 and topic not in topics:
            topics.append(topic)

    return topics[:5]  # Limit to 5 topics


def categorize_note(filename: str, title: str) -> str:
    """Determine category based on filename and title"""
    text = (filename + " " + title).lower()

    for category, pattern in CATEGORY_PATTERNS.items():
        if re.search(pattern, text):
            return category

    return "General"


def import_html_notes():
    """
    Scan and import HTML OSCE notes from /ICRP_OSCE_Preparation/
    """
    # Get base path (project root / ICRP_OSCE_Preparation)
    project_root = Path(__file__).parent.parent.parent
    base_path = project_root / 'ICRP_OSCE_Preparation'

    if not base_path.exists():
        print(f"❌ Directory not found: {base_path}")
        return

    print("📁 Scanning HTML OSCE Notes...")
    print(f"   Base path: {base_path}")
    print("=" * 70)

    # Connect to database
    try:
        engine = create_engine(get_database_url())
        session = Session(engine)
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        print("\n💡 Set DATABASE_PASSWORD environment variable:")
        print("   export DATABASE_PASSWORD=your_password")
        sys.exit(1)

    imported_count = 0
    skipped_count = 0
    specialty_counts = {}

    # Idempotency: load already-imported file paths and existing note_id counters
    existing_paths = {row[0] for row in session.query(HTMLOSCENote.file_path).all()}
    prefix_counters = {}
    for (nid,) in session.query(HTMLOSCENote.note_id).all():
        # note_id form: HTML-<PREFIX>-<NNN>
        parts = nid.split('-')
        if len(parts) == 3 and parts[2].isdigit():
            prefix_counters[parts[1]] = max(prefix_counters.get(parts[1], 0), int(parts[2]))

    # Scan each specialty directory
    for specialty_dir in sorted(base_path.iterdir()):
        if not specialty_dir.is_dir():
            continue

        specialty_name = SPECIALTY_MAP.get(specialty_dir.name, specialty_dir.name)
        html_files = list(specialty_dir.glob('*.html'))

        if not html_files:
            continue

        print(f"\n📚 {specialty_name} ({len(html_files)} files)")
        specialty_counts[specialty_name] = 0

        for html_file in sorted(html_files):
            try:
                relative_path_early = str(html_file.relative_to(base_path))
                if relative_path_early in existing_paths:
                    skipped_count += 1
                    continue
                # Read HTML file
                html_content = html_file.read_text(encoding='utf-8')

                # Extract metadata
                title = extract_title_from_html(html_content)
                preview = extract_preview_text(html_content)
                topics = extract_topics_from_html(html_content)
                category = categorize_note(html_file.name, title)

                # Calculate file size and reading time
                file_size_kb = html_file.stat().st_size // 1024
                word_count = len(html_content.split())
                reading_minutes = max(1, round(word_count / 200))

                # Generate a collision-safe note_id: continue per-prefix numbering
                prefix = specialty_dir.name.upper()[:3]
                prefix_counters[prefix] = prefix_counters.get(prefix, 0) + 1
                note_id = f"HTML-{prefix}-{prefix_counters[prefix]:03d}"

                # Relative path from ICRP_OSCE_Preparation
                relative_path = relative_path_early

                # Create database record
                note = HTMLOSCENote(
                    note_id=note_id,
                    title=title,
                    file_path=relative_path,
                    specialty=specialty_name,
                    category=category,
                    topics=topics,
                    preview_text=preview,
                    file_size_kb=file_size_kb,
                    estimated_reading_minutes=reading_minutes,
                    is_published=True
                )

                session.add(note)
                imported_count += 1
                specialty_counts[specialty_name] += 1

                print(f"   ✅ {html_file.name[:50]:50s} → {note_id}")

            except Exception as e:
                print(f"   ❌ {html_file.name}: {str(e)}")

    # Commit to database
    try:
        session.commit()
        print("\n" + "=" * 70)
        print(f"✅ Successfully imported {imported_count} HTML OSCE notes "
              f"({skipped_count} already-present skipped)\n")

        print("📊 Breakdown by Specialty:")
        for specialty, count in sorted(specialty_counts.items()):
            print(f"   {specialty:30s}: {count:2d} notes")

        print("\n🔗 API Endpoints:")
        print("   GET /api/v1/html-notes")
        print("   GET /api/v1/html-notes/{note_id}")
        print("   GET /api/v1/html-notes/by-specialty/{specialty}")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Database commit failed: {str(e)}")
        sys.exit(1)
    finally:
        session.close()


if __name__ == '__main__':
    import_html_notes()
