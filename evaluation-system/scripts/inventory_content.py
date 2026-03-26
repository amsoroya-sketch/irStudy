#!/usr/bin/env python3
"""
Content Inventory Scanner for irStudy Medical Education Platform
Scans all content directories and generates comprehensive inventory for evaluation system.

Supports:
- Patient Personas (OSCE simulation patients)
- MCQs (Multiple Choice Questions)
- OSCE Scripts (clinical exam scenarios)
- Study Cards (flashcard content)
- Images (radiological/clinical images)
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import hashlib

# Base directory
BASE_DIR = Path(__file__).parent.parent.parent
EVALUATION_DIR = BASE_DIR / "evaluation-system"

# Content directories to scan
CONTENT_DIRS = {
    "patient_persona": [
        "clinical-content-prds/validation-system/batch1_personas",
        "clinical-content-prds/validation-system/batch2_personas",
        "clinical-content-prds/validation-system/batch3_personas",
    ],
    "mcq": [
        "data/mcqs",
    ],
    "osce_script": [
        "data/osces",
    ],
    "study_card": [
        "data/study_cards",
    ],
    "clinical_image": [
        "data/images/radiology",
        "data/images/dermatology",
        "data/images/ophthalmology",
    ]
}

# Specialty mapping from filenames
SPECIALTY_PATTERNS = {
    "cardiology": ["cardiology", "cardiac", "cvs", "heart"],
    "respiratory": ["respiratory", "pulmonary", "lung", "asthma", "copd"],
    "neurology": ["neurology", "neurological", "stroke", "seizure", "headache"],
    "gastroenterology": ["gastro", "gi", "abdominal", "liver", "ibd"],
    "endocrinology": ["endocrine", "diabetes", "thyroid", "adrenal"],
    "nephrology": ["renal", "kidney", "nephrology"],
    "rheumatology": ["rheumatology", "arthritis", "sle", "gout"],
    "haematology": ["haematology", "haem", "anaemia", "leukaemia"],
    "infectious_diseases": ["infection", "infectious", "sepsis", "pneumonia"],
    "emergency": ["emergency", "trauma", "acute", "critical"],
    "paediatrics": ["paediatric", "pediatric", "child", "infant"],
    "psychiatry": ["psychiatry", "mental", "depression", "anxiety", "psychosis"],
    "obstetrics_gynaecology": ["obstetric", "gynaecology", "pregnancy", "labour"],
    "general_practice": ["general_practice", "gp", "primary_care"],
    "dermatology": ["dermatology", "skin", "rash", "eczema"],
    "ophthalmology": ["ophthalmology", "eye", "vision", "retina"],
}


def extract_specialty(filename: str, content: Dict = None) -> str:
    """Extract specialty from filename or content."""
    filename_lower = filename.lower()

    # Check filename patterns
    for specialty, patterns in SPECIALTY_PATTERNS.items():
        if any(pattern in filename_lower for pattern in patterns):
            return specialty

    # Check content if provided
    if content:
        if "specialty" in content:
            return content["specialty"]
        if "category" in content:
            return content["category"]

    return "general"


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA256 hash of file content."""
    hasher = hashlib.sha256()
    with open(filepath, 'rb') as f:
        hasher.update(f.read())
    return hasher.hexdigest()[:16]  # Short hash


def scan_patient_personas(base_dir: Path, content_dirs: List[str]) -> List[Dict]:
    """Scan patient persona JSON files."""
    items = []

    for content_dir in content_dirs:
        dir_path = base_dir / content_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue

        persona_files = list(dir_path.glob("*_persona.json"))
        qa_report_files = list(dir_path.glob("*_qa_report.json"))

        print(f"📁 {content_dir}: {len(persona_files)} personas, {len(qa_report_files)} QA reports")

        for persona_file in persona_files:
            try:
                with open(persona_file, 'r') as f:
                    content = json.load(f)

                # Check if QA report exists
                qa_report_path = persona_file.parent / persona_file.name.replace("_persona.json", "_persona_qa_report.json")
                has_qa_report = qa_report_path.exists()

                # Extract specialty
                specialty = extract_specialty(persona_file.name, content)

                item = {
                    "item_id": f"persona_{persona_file.stem}",
                    "item_type": "patient_persona",
                    "file_path": str(persona_file.relative_to(base_dir)),
                    "specialty": specialty,
                    "persona_code": content.get("persona_code", "UNKNOWN"),
                    "chief_complaint": content.get("chief_complaint", ""),
                    "age": content.get("age"),
                    "gender": content.get("gender"),
                    "file_hash": calculate_file_hash(persona_file),
                    "file_size": persona_file.stat().st_size,
                    "last_modified": datetime.fromtimestamp(persona_file.stat().st_mtime).isoformat(),
                    "evaluation_status": "completed" if has_qa_report else "pending",
                    "qa_report_path": str(qa_report_path.relative_to(base_dir)) if has_qa_report else None,
                    "assigned_agents": [],
                    "evaluation_scores": {},
                }

                items.append(item)

            except Exception as e:
                print(f"❌ Error processing {persona_file.name}: {e}")

    return items


def scan_mcqs(base_dir: Path, content_dirs: List[str]) -> List[Dict]:
    """Scan MCQ JSON files."""
    items = []

    for content_dir in content_dirs:
        dir_path = base_dir / content_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue

        mcq_files = list(dir_path.glob("*.json"))
        print(f"📁 {content_dir}: {len(mcq_files)} MCQ files")

        for mcq_file in mcq_files:
            # Skip backup files
            if "backup" in mcq_file.name.lower():
                continue

            try:
                with open(mcq_file, 'r') as f:
                    content = json.load(f)

                # MCQ files contain arrays of questions
                mcq_array = content if isinstance(content, list) else content.get("mcqs", [])

                for idx, mcq in enumerate(mcq_array):
                    specialty = extract_specialty(mcq_file.name, mcq)

                    item = {
                        "item_id": f"mcq_{mcq_file.stem}_{idx:03d}",
                        "item_type": "mcq",
                        "file_path": str(mcq_file.relative_to(base_dir)),
                        "array_index": idx,
                        "specialty": specialty,
                        "question_id": mcq.get("question_id", f"Q{idx:03d}"),
                        "topic": mcq.get("topic", ""),
                        "difficulty": mcq.get("difficulty", "medium"),
                        "has_image": bool(mcq.get("image_url") or mcq.get("image_path")),
                        "file_hash": calculate_file_hash(mcq_file),
                        "file_size": mcq_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(mcq_file.stat().st_mtime).isoformat(),
                        "evaluation_status": "pending",
                        "assigned_agents": [],
                        "evaluation_scores": {},
                    }

                    items.append(item)

            except Exception as e:
                print(f"❌ Error processing {mcq_file.name}: {e}")

    return items


def scan_osce_scripts(base_dir: Path, content_dirs: List[str]) -> List[Dict]:
    """Scan OSCE script JSON files."""
    items = []

    for content_dir in content_dirs:
        dir_path = base_dir / content_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue

        osce_files = list(dir_path.glob("*.json"))
        print(f"📁 {content_dir}: {len(osce_files)} OSCE files")

        for osce_file in osce_files:
            # Skip QA reports
            if "qa_report" in osce_file.name.lower():
                continue

            try:
                with open(osce_file, 'r') as f:
                    content = json.load(f)

                # OSCE files contain arrays of scripts
                osce_array = content if isinstance(content, list) else content.get("osces", [])

                for idx, osce in enumerate(osce_array):
                    specialty = extract_specialty(osce_file.name, osce)

                    item = {
                        "item_id": f"osce_{osce_file.stem}_{idx:03d}",
                        "item_type": "osce_script",
                        "file_path": str(osce_file.relative_to(base_dir)),
                        "array_index": idx,
                        "specialty": specialty,
                        "station_name": osce.get("station_name", ""),
                        "scenario_type": osce.get("scenario_type", ""),
                        "duration_minutes": osce.get("duration_minutes", 8),
                        "file_hash": calculate_file_hash(osce_file),
                        "file_size": osce_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(osce_file.stat().st_mtime).isoformat(),
                        "evaluation_status": "pending",
                        "assigned_agents": [],
                        "evaluation_scores": {},
                    }

                    items.append(item)

            except Exception as e:
                print(f"❌ Error processing {osce_file.name}: {e}")

    return items


def scan_study_cards(base_dir: Path, content_dirs: List[str]) -> List[Dict]:
    """Scan study card JSON files."""
    items = []

    for content_dir in content_dirs:
        dir_path = base_dir / content_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue

        card_files = list(dir_path.glob("*.json"))
        print(f"📁 {content_dir}: {len(card_files)} study card files")

        for card_file in card_files:
            try:
                with open(card_file, 'r') as f:
                    content = json.load(f)

                # Study card files contain arrays of cards
                card_array = content if isinstance(content, list) else content.get("cards", content.get("study_cards", []))

                for idx, card in enumerate(card_array):
                    specialty = extract_specialty(card_file.name, card)

                    item = {
                        "item_id": f"study_card_{card_file.stem}_{idx:03d}",
                        "item_type": "study_card",
                        "file_path": str(card_file.relative_to(base_dir)),
                        "array_index": idx,
                        "specialty": specialty,
                        "card_id": card.get("card_id", f"SC{idx:03d}"),
                        "topic": card.get("topic", ""),
                        "subtopic": card.get("subtopic", ""),
                        "file_hash": calculate_file_hash(card_file),
                        "file_size": card_file.stat().st_size,
                        "last_modified": datetime.fromtimestamp(card_file.stat().st_mtime).isoformat(),
                        "evaluation_status": "pending",
                        "assigned_agents": [],
                        "evaluation_scores": {},
                    }

                    items.append(item)

            except Exception as e:
                print(f"❌ Error processing {card_file.name}: {e}")

    return items


def scan_clinical_images(base_dir: Path, content_dirs: List[str]) -> List[Dict]:
    """Scan clinical image files."""
    items = []

    for content_dir in content_dirs:
        dir_path = base_dir / content_dir
        if not dir_path.exists():
            print(f"⚠️  Directory not found: {dir_path}")
            continue

        # Scan for image files
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']
        image_files = []
        for ext in image_extensions:
            image_files.extend(dir_path.glob(f"*{ext}"))
            image_files.extend(dir_path.glob(f"*{ext.upper()}"))

        print(f"📁 {content_dir}: {len(image_files)} images")

        for image_file in image_files:
            specialty = extract_specialty(content_dir)

            item = {
                "item_id": f"image_{image_file.stem}",
                "item_type": "clinical_image",
                "file_path": str(image_file.relative_to(base_dir)),
                "specialty": specialty,
                "image_category": Path(content_dir).name,
                "file_extension": image_file.suffix,
                "file_hash": calculate_file_hash(image_file),
                "file_size": image_file.stat().st_size,
                "last_modified": datetime.fromtimestamp(image_file.stat().st_mtime).isoformat(),
                "evaluation_status": "pending",
                "assigned_agents": [],
                "evaluation_scores": {},
            }

            items.append(item)

    return items


def generate_inventory_report(items: List[Dict]) -> Dict:
    """Generate summary statistics."""
    total_items = len(items)

    # Count by item type
    by_type = {}
    for item in items:
        item_type = item["item_type"]
        by_type[item_type] = by_type.get(item_type, 0) + 1

    # Count by specialty
    by_specialty = {}
    for item in items:
        specialty = item.get("specialty", "unknown")
        by_specialty[specialty] = by_specialty.get(specialty, 0) + 1

    # Count by evaluation status
    by_status = {}
    for item in items:
        status = item["evaluation_status"]
        by_status[status] = by_status.get(status, 0) + 1

    return {
        "total_items": total_items,
        "by_type": by_type,
        "by_specialty": dict(sorted(by_specialty.items())),
        "by_status": by_status,
        "completed_items": by_status.get("completed", 0),
        "pending_items": by_status.get("pending", 0),
    }


def main():
    """Main execution function."""
    print("=" * 80)
    print("irStudy Content Inventory Scanner")
    print("=" * 80)
    print(f"Base directory: {BASE_DIR}")
    print(f"Evaluation directory: {EVALUATION_DIR}")
    print()

    all_items = []

    # Scan all content types
    print("🔍 Scanning Patient Personas...")
    all_items.extend(scan_patient_personas(BASE_DIR, CONTENT_DIRS["patient_persona"]))

    print("\n🔍 Scanning MCQs...")
    all_items.extend(scan_mcqs(BASE_DIR, CONTENT_DIRS["mcq"]))

    print("\n🔍 Scanning OSCE Scripts...")
    all_items.extend(scan_osce_scripts(BASE_DIR, CONTENT_DIRS["osce_script"]))

    print("\n🔍 Scanning Study Cards...")
    all_items.extend(scan_study_cards(BASE_DIR, CONTENT_DIRS["study_card"]))

    print("\n🔍 Scanning Clinical Images...")
    all_items.extend(scan_clinical_images(BASE_DIR, CONTENT_DIRS["clinical_image"]))

    # Generate statistics
    print("\n" + "=" * 80)
    print("📊 Inventory Summary")
    print("=" * 80)

    stats = generate_inventory_report(all_items)
    print(f"Total Items: {stats['total_items']}")
    print(f"\nBy Type:")
    for item_type, count in stats['by_type'].items():
        print(f"  - {item_type}: {count}")
    print(f"\nBy Status:")
    for status, count in stats['by_status'].items():
        print(f"  - {status}: {count}")
    print(f"\nTop 10 Specialties:")
    sorted_specialties = sorted(stats['by_specialty'].items(), key=lambda x: x[1], reverse=True)
    for specialty, count in sorted_specialties[:10]:
        print(f"  - {specialty}: {count}")

    # Create registry JSON
    registry = {
        "registry_version": "1.0.0",
        "generated_at": datetime.now().isoformat(),
        "statistics": stats,
        "knowledge_items": all_items,
    }

    # Save to file
    output_path = EVALUATION_DIR / "data" / "knowledge_item_registry.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(registry, f, indent=2)

    print(f"\n✅ Registry saved to: {output_path}")
    print(f"📦 File size: {output_path.stat().st_size / 1024:.2f} KB")

    return 0


if __name__ == "__main__":
    sys.exit(main())
