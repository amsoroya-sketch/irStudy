"""
Compare OSCE Markdown Files vs Database

Analyzes all OSCE markdown files in ICRP_OSCE_Preparation folder
and compares with database content to identify:
- OSCEs in markdown but not in database
- OSCEs in database but not in markdown
- Matching OSCEs
- Video resources status

Usage:
    python scripts/compare_osces_md_vs_db.py
"""

import sys
import os
import re
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from src.db.base import SessionLocal
from src.db.models import OSCE, OSCEType

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


def find_all_osce_markdown_files():
    """Find all OSCE markdown files in the project"""
    base_path = Path(__file__).parent.parent / "ICRP_OSCE_Preparation"

    markdown_files = []

    # Find all .md files
    for md_file in base_path.rglob("*.md"):
        # Skip master lists and index files
        if "VIDEO_RESOURCES" in md_file.name or "MASTER_INDEX" in md_file.name or "00_" in md_file.name:
            continue

        markdown_files.append(md_file)

    return sorted(markdown_files)


def extract_title_from_markdown(file_path):
    """Extract the main title from a markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

            # Look for first heading
            match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            if match:
                title = match.group(1).strip()
                # Remove "OSCE Notes -" or similar prefixes
                title = re.sub(r'^.*?OSCE Notes\s*-\s*', '', title)
                title = re.sub(r'^\s*-\s*', '', title)
                return title
    except Exception as e:
        return None

    return None


def categorize_osce_type(file_path, title):
    """Determine the OSCE type based on file path and title"""
    path_str = str(file_path).lower()
    title_lower = title.lower() if title else ""

    # Physical Examination
    if "physical_examination" in path_str or "examination" in title_lower:
        if "history" not in title_lower and "taking" not in title_lower:
            return "physical_examination"

    # History Taking
    if "history" in path_str or ("history" in title_lower and "taking" in title_lower):
        return "history_taking"

    # Procedures
    if "procedure" in path_str or "skill" in path_str:
        return "procedure"

    # Emergency scenarios
    if "emergency" in path_str or "trauma" in path_str or "acute" in title_lower:
        return "emergency_scenario"

    # Communication
    if "communication" in path_str or "breaking_bad_news" in path_str:
        return "communication"

    # Default to history_taking for differentials
    if "differential" in title_lower:
        return "history_taking"

    return "unknown"


def has_video_resources(file_path):
    """Check if markdown file has video resources section"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            return "## 📺 RECOMMENDED VIDEO DEMONSTRATIONS" in content or "VIDEO" in content.upper()
    except:
        return False


def main():
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}OSCE Markdown Files vs Database Comparison{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

    # Get markdown files
    print(f"{Colors.BLUE}📁 Scanning for OSCE markdown files...{Colors.END}")
    markdown_files = find_all_osce_markdown_files()
    print(f"   Found {len(markdown_files)} markdown files\n")

    # Process markdown files
    md_osces = []
    for md_file in markdown_files:
        title = extract_title_from_markdown(md_file)
        osce_type = categorize_osce_type(md_file, title)
        has_videos = has_video_resources(md_file)

        md_osces.append({
            'file_path': md_file,
            'title': title or md_file.stem,
            'type': osce_type,
            'has_videos': has_videos,
            'category': md_file.parent.name
        })

    # Get database OSCEs
    print(f"{Colors.BLUE}🗄️  Querying database OSCEs...{Colors.END}")
    db = SessionLocal()
    try:
        db_osces = db.query(OSCE).all()
        print(f"   Found {len(db_osces)} OSCEs in database\n")

        # Count by type
        db_by_type = {}
        db_with_videos = 0
        for osce in db_osces:
            type_str = osce.station_type.value
            db_by_type[type_str] = db_by_type.get(type_str, 0) + 1
            if osce.video_resources is not None:
                db_with_videos += 1

        # Count markdown by type
        md_by_type = {}
        md_with_videos = 0
        for osce in md_osces:
            type_str = osce['type']
            md_by_type[type_str] = md_by_type.get(type_str, 0) + 1
            if osce['has_videos']:
                md_with_videos += 1

        # Print summary
        print(f"{Colors.BOLD}{Colors.GREEN}📊 Summary Statistics{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        print(f"{Colors.CYAN}Markdown Files:{Colors.END}")
        print(f"  Total files: {len(md_osces)}")
        print(f"  Files with video sections: {md_with_videos}")
        print(f"\n  By Type:")
        for osce_type, count in sorted(md_by_type.items()):
            print(f"    - {osce_type}: {count}")

        print(f"\n{Colors.CYAN}Database:{Colors.END}")
        print(f"  Total OSCEs: {len(db_osces)}")
        print(f"  OSCEs with videos: {db_with_videos}")
        print(f"\n  By Type:")
        for osce_type, count in sorted(db_by_type.items()):
            print(f"    - {osce_type}: {count}")

        # Detailed comparison
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📋 Detailed Markdown Files{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        # Group by category
        by_category = {}
        for osce in md_osces:
            cat = osce['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(osce)

        for category in sorted(by_category.keys()):
            print(f"\n{Colors.BOLD}{Colors.CYAN}{category}:{Colors.END}")
            for osce in by_category[category]:
                video_indicator = "📹" if osce['has_videos'] else "  "
                type_color = Colors.GREEN if osce['type'] == 'physical_examination' else Colors.YELLOW
                print(f"  {video_indicator} {type_color}[{osce['type']}]{Colors.END} {osce['title']}")

        # Physical examination OSCEs with videos
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ Physical Examination OSCEs in Database with Videos{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        phys_exam_with_videos = [osce for osce in db_osces
                                 if osce.station_type == OSCEType.PHYSICAL_EXAMINATION
                                 and osce.video_resources is not None]

        if phys_exam_with_videos:
            for osce in phys_exam_with_videos:
                video_count = len(osce.video_resources.get('essential_videos', [])) if isinstance(osce.video_resources, dict) else 0
                print(f"  ✅ {osce.station_title}")
                print(f"      ID: {osce.osce_id} | Videos: {video_count} essential")
        else:
            print(f"  {Colors.RED}❌ No physical examination OSCEs with videos found in database{Colors.END}")

        # Recommendations
        print(f"\n{Colors.BOLD}{Colors.CYAN}💡 Recommendations{Colors.END}")
        print(f"{Colors.BOLD}{'='*80}{Colors.END}\n")

        if md_with_videos > db_with_videos:
            print(f"  📹 {md_with_videos - db_with_videos} markdown files have video sections not yet in database")

        md_phys_exam = [o for o in md_osces if o['type'] == 'physical_examination']
        db_phys_exam = len([o for o in db_osces if o.station_type == OSCEType.PHYSICAL_EXAMINATION])

        if len(md_phys_exam) > db_phys_exam:
            print(f"  🏥 {len(md_phys_exam) - db_phys_exam} physical examination markdown files not yet in database")
            print(f"      Consider importing:")
            for osce in md_phys_exam[:5]:  # Show first 5
                if has_video_resources(osce['file_path']):
                    print(f"      - {osce['title']} (has videos)")

        if len(md_osces) > len(db_osces):
            print(f"  📝 {len(md_osces) - len(db_osces)} total markdown files not yet imported")
            print(f"      Next steps: Create importers for history_taking, communication, etc.")

        print()

    finally:
        db.close()


if __name__ == "__main__":
    main()
