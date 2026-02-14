#!/usr/bin/env python3
"""
Import All OSCE Markdown Files - Option 3
==========================================

Imports all remaining OSCE markdown files from ICRP_OSCE_Preparation:
- Mock Stations (8 files) - Complete OSCE structure
- History Taking OSCEs (15 files) - Convert study notes to OSCE format
- Communication OSCEs (7 files) - Breaking bad news scenarios
- Remaining Physical Examinations (5 files) - With video resources

Usage:
    python scripts/import_all_osces_option3.py [--dry-run]

Options:
    --dry-run    Show what would be imported without actually inserting

Total Target: 35 OSCEs to import
"""

import sys
import os
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from sqlalchemy import text
from src.db.base import SessionLocal
from src.db.models import OSCE, OSCEType, Difficulty, Specialty

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    END = '\033[0m'
    BOLD = '\033[1m'


class OSCEImporter:
    """Import OSCEs from markdown files"""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.base_path = Path(__file__).parent.parent / "ICRP_OSCE_Preparation"
        self.imported_count = 0
        self.skipped_count = 0
        self.error_count = 0

    def find_markdown_files(self) -> Dict[str, List[Path]]:
        """Find all OSCE markdown files organized by category"""
        files = {
            'mock_stations': [],
            'medicine': [],
            'surgery': [],
            'obgyn': [],
            'paediatrics': [],
            'psychiatry': [],
            'communication': []
        }

        # Mock Stations
        mock_path = self.base_path / "Mock_Stations"
        if mock_path.exists():
            for f in mock_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO', 'CHEATSHEET']):
                    files['mock_stations'].append(f)

        # Medicine
        med_path = self.base_path / "Medicine"
        if med_path.exists():
            for f in med_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['medicine'].append(f)

        # Surgery
        surg_path = self.base_path / "Surgery"
        if surg_path.exists():
            for f in surg_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['surgery'].append(f)

        # ObGyn
        obgyn_path = self.base_path / "ObGyn"
        if obgyn_path.exists():
            for f in obgyn_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['obgyn'].append(f)

        # Paediatrics
        paeds_path = self.base_path / "Paediatrics"
        if paeds_path.exists():
            for f in paeds_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['paediatrics'].append(f)

        # Psychiatry
        psych_path = self.base_path / "Psychiatry"
        if psych_path.exists():
            for f in psych_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['psychiatry'].append(f)

        # Communication
        comm_path = self.base_path / "Ethics_Communication"
        if comm_path.exists():
            for f in comm_path.glob("*.md"):
                if not any(skip in f.name for skip in ['00_', 'MASTER', 'VIDEO']):
                    files['communication'].append(f)

        return files

    def extract_mock_station(self, file_path: Path) -> Optional[Dict]:
        """Extract OSCE data from Mock Station markdown file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract title
            title_match = re.search(r'# Mock OSCE Station - (.+?)(?:\n|$)', content)
            if not title_match:
                # Try alternative format
                title_match = re.search(r'# (.+?)(?:\n|##)', content)
            title = title_match.group(1).strip() if title_match else file_path.stem

            # Extract time limit
            time_match = re.search(r'\*\*Time\*\*:\s*(\d+)\s*minutes?', content)
            time_limit = int(time_match.group(1)) if time_match else 8

            # Extract difficulty
            difficulty_match = re.search(r'\*\*Difficulty\*\*:\s*(\w+)', content, re.IGNORECASE)
            difficulty_str = difficulty_match.group(1).lower() if difficulty_match else 'medium'
            difficulty = self._map_difficulty(difficulty_str)

            # Extract specialty from System field or path
            specialty_match = re.search(r'\*\*System\*\*:\s*(\w+)', content)
            if specialty_match:
                specialty = self._map_specialty(specialty_match.group(1))
            else:
                # Infer from title or path
                specialty = self._infer_specialty(title)

            # Extract candidate instructions
            candidate_section = re.search(
                r'## FOR THE CANDIDATE\s*(?:### INSTRUCTIONS.*?)?(.*?)(?:---|\n##)',
                content,
                re.DOTALL
            )
            candidate_instructions = candidate_section.group(1).strip() if candidate_section else ""

            # Extract patient instructions
            patient_section = re.search(
                r'## FOR THE SIMULATED PATIENT(.*?)(?:---|\n## FOR THE EXAMINER)',
                content,
                re.DOTALL
            )
            patient_instructions = patient_section.group(1).strip() if patient_section else ""

            # Extract examiner instructions and rubric
            examiner_section = re.search(
                r'## FOR THE EXAMINER(.*?)(?:$)',
                content,
                re.DOTALL
            )
            examiner_content = examiner_section.group(1).strip() if examiner_section else ""

            # Split into instructions and rubric
            rubric_match = re.search(r'## EXAMINER MARKING CHECKLIST(.*)', examiner_content, re.DOTALL)
            if rubric_match:
                rubric = rubric_match.group(1).strip()
                examiner_instructions = examiner_content[:rubric_match.start()].strip()
            else:
                rubric = examiner_content
                examiner_instructions = examiner_content[:500]  # First part as instructions

            # Extract learning objectives
            objectives_match = re.search(
                r'### STATION OBJECTIVES(.*?)(?:\n##|\n###|---)',
                content,
                re.DOTALL
            )
            learning_objectives = objectives_match.group(1).strip() if objectives_match else ""

            # Extract key points from high-yield indicator
            key_points_match = re.search(
                r'\*\*Why High-Yield:\*\*\s*(.*?)(?:\n\*\*|---)',
                content,
                re.DOTALL
            )
            key_points = key_points_match.group(1).strip() if key_points_match else ""

            # Determine station type
            station_type = self._determine_station_type(title, content)

            # Generate OSCE ID
            specialty_prefix = specialty.value[:4].upper() if specialty else 'MOCK'
            osce_id = self._generate_osce_id(specialty_prefix, title)

            return {
                'osce_id': osce_id,
                'station_title': title,
                'station_type': station_type,
                'specialty': specialty,
                'difficulty': difficulty,
                'time_limit_minutes': time_limit,
                'patient_instructions': patient_instructions,
                'candidate_instructions': candidate_instructions,
                'examiner_instructions': examiner_instructions,
                'rubric': rubric,
                'learning_objectives': learning_objectives,
                'key_points': key_points,
                'is_published': True,
                'tags': self._extract_tags(content, title),
                'video_resources': None  # Mock stations typically don't have videos
            }

        except Exception as e:
            print(f"{Colors.RED}Error extracting mock station from {file_path.name}: {e}{Colors.END}")
            return None

    def extract_study_notes(self, file_path: Path, category: str) -> List[Dict]:
        """Convert study notes into OSCE station(s)"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            osces = []

            # Extract main title
            title_match = re.search(r'^# (.+?)(?:\n|$)', content, re.MULTILINE)
            base_title = title_match.group(1).strip() if title_match else file_path.stem

            # Remove prefix like "Medicine OSCE Master Notes -"
            base_title = re.sub(r'^.*?OSCE.*?Notes\s*-\s*', '', base_title)
            base_title = re.sub(r'^.*?Master Notes\s*-\s*', '', base_title)

            # Check if this is a physical examination with videos
            has_videos = "RECOMMENDED VIDEO DEMONSTRATIONS" in content

            # Determine specialty
            specialty = self._map_specialty_from_category(category, base_title)

            # For physical examinations, create one OSCE
            if "examination" in base_title.lower() or "physical" in file_path.name.lower():
                station_type = OSCEType.PHYSICAL_EXAMINATION
                osce = self._create_osce_from_notes(
                    content, base_title, specialty, station_type, has_videos, category
                )
                if osce:
                    osces.append(osce)
            else:
                # For history-taking notes, create OSCEs for each major section
                sections = self._split_into_sections(content)
                for section_title, section_content in sections:
                    full_title = f"{base_title}: {section_title}" if section_title != base_title else base_title
                    station_type = self._determine_station_type(full_title, section_content)
                    osce = self._create_osce_from_notes(
                        section_content, full_title, specialty, station_type, False, category
                    )
                    if osce:
                        osces.append(osce)

            return osces

        except Exception as e:
            print(f"{Colors.RED}Error extracting study notes from {file_path.name}: {e}{Colors.END}")
            return []

    def _create_osce_from_notes(
        self, content: str, title: str, specialty: Specialty,
        station_type: OSCEType, has_videos: bool, category: str
    ) -> Optional[Dict]:
        """Create OSCE entry from study notes content"""

        # Extract key information
        differentials = self._extract_differentials(content)
        investigations = self._extract_investigations(content)
        key_points = self._extract_key_points_from_content(content)

        # Create candidate instructions
        candidate_instructions = f"""You are a junior doctor at an Australian teaching hospital.

**Task**: Take a focused history from this patient presenting with {title.lower()}.

**Time**: 8 minutes

**Instructions**:
1. Take a systematic history using appropriate framework
2. Identify red flags requiring urgent attention
3. Generate differential diagnoses
4. Suggest appropriate investigations

At the 7-minute mark, you will be asked to summarize your findings and provide your top 3 differential diagnoses.
"""

        # Create patient instructions
        patient_instructions = self._generate_patient_instructions(title, content)

        # Create examiner instructions
        examiner_instructions = f"""**Your Role**:
- Observe the candidate silently
- Mark using the rubric below
- At 7 minutes, ask for summary and differential diagnoses
- At 8 minutes, thank the candidate

**Station Objectives**:
This station assesses the candidate's ability to:
1. Take a systematic history relevant to {title.lower()}
2. Identify red flags and concerning features
3. Generate appropriate differential diagnoses
4. Suggest relevant investigations for Australian context
"""

        # Create rubric
        rubric = self._generate_rubric(title, station_type)

        # Create learning objectives
        learning_objectives = f"""1. Demonstrate systematic approach to {title.lower()}
2. Identify key differentials: {', '.join(differentials[:3]) if differentials else 'common presentations'}
3. Recognize red flags requiring urgent assessment
4. Suggest appropriate Australian-context investigations: {', '.join(investigations[:5]) if investigations else 'relevant tests'}
"""

        # Generate OSCE ID
        specialty_prefix = specialty.value[:4].upper() if specialty else 'GEN'
        category_prefix = category[:3].upper()
        osce_id = f"OSCE-{specialty_prefix}-{category_prefix}-{abs(hash(title)) % 1000:03d}"

        # Extract video resources if physical examination
        video_resources = None
        if has_videos and station_type == OSCEType.PHYSICAL_EXAMINATION:
            video_resources = self._extract_video_resources(content)

        return {
            'osce_id': osce_id,
            'station_title': title,
            'station_type': station_type,
            'specialty': specialty,
            'difficulty': Difficulty.MEDIUM,
            'time_limit_minutes': 8,
            'patient_instructions': patient_instructions,
            'candidate_instructions': candidate_instructions,
            'examiner_instructions': examiner_instructions,
            'rubric': rubric,
            'learning_objectives': learning_objectives,
            'key_points': key_points,
            'is_published': True,
            'tags': self._extract_tags(content, title),
            'video_resources': json.dumps(video_resources) if video_resources else None
        }

    def _extract_differentials(self, content: str) -> List[str]:
        """Extract differential diagnoses from content"""
        differentials = []

        # Look for differential sections
        diff_section = re.search(
            r'(?:Top \d+ Differentials|Differential Diagnos(?:i|e)s)(.*?)(?:\n##|\n\*\*)',
            content,
            re.DOTALL | re.IGNORECASE
        )

        if diff_section:
            # Extract numbered or bulleted items
            items = re.findall(r'(?:\d+\.|[-*])\s*\*\*(.+?)\*\*', diff_section.group(1))
            differentials.extend(items[:5])

        return differentials

    def _extract_investigations(self, content: str) -> List[str]:
        """Extract investigations from content"""
        investigations = []

        inv_section = re.search(
            r'(?:Investigations?|Tests?)(.*?)(?:\n##|\n\*\*)',
            content,
            re.DOTALL | re.IGNORECASE
        )

        if inv_section:
            # Extract items in bold or lists
            items = re.findall(r'[-*]\s*\*\*(.+?)\*\*', inv_section.group(1))
            investigations.extend(items[:10])

        return investigations

    def _extract_key_points_from_content(self, content: str) -> str:
        """Extract key points from content"""
        # Try to find high-yield indicator
        high_yield = re.search(
            r'\*\*Why High-Yield:\*\*\s*(.*?)(?:\n\*\*|---)',
            content,
            re.DOTALL
        )
        if high_yield:
            return high_yield.group(1).strip()

        # Try to find red flags section
        red_flags = re.search(
            r'(?:Red Flags?|Warning Signs?)(.*?)(?:\n##|\n\*\*)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if red_flags:
            return red_flags.group(1).strip()

        return ""

    def _extract_video_resources(self, content: str) -> Optional[Dict]:
        """Extract video resources from content"""
        video_section = re.search(
            r'## 📺 RECOMMENDED VIDEO DEMONSTRATIONS(.*?)(?:\n##|$)',
            content,
            re.DOTALL
        )

        if not video_section:
            return None

        video_text = video_section.group(1)

        # Extract videos
        essential_videos = []
        video_pattern = re.compile(
            r'\*\*(.+?)\*\*.*?'
            r'- \*\*URL\*\*:\s*(https?://\S+).*?'
            r'- \*\*Source\*\*:\s*(.+?)(?:\n|$).*?'
            r'(?:- \*\*Duration\*\*:\s*(\d+)\s*min(?:ute)?s?)?.*?'
            r'- \*\*Focus\*\*:\s*(.+?)(?:\n|$).*?'
            r'- \*\*Why Recommended\*\*:\s*(.+?)(?:\n|$)',
            re.DOTALL
        )

        for match in video_pattern.finditer(video_text):
            video = {
                'title': match.group(1).strip(),
                'url': match.group(2).strip(),
                'source': match.group(3).strip(),
                'duration_minutes': int(match.group(4)) if match.group(4) else None,
                'focus': match.group(5).strip(),
                'why_recommended': match.group(6).strip(),
                'australian_relevance': 'Compatible with AMC Clinical exam requirements'
            }
            essential_videos.append(video)

            if len(essential_videos) >= 4:  # Max 4 essential videos
                break

        if essential_videos:
            return {
                'essential_videos': essential_videos,
                'supplementary_videos': []
            }

        return None

    def _generate_patient_instructions(self, title: str, content: str) -> str:
        """Generate patient instructions from study notes"""
        # Try to extract presenting complaint
        presenting_complaint = title.split(':')[-1].strip().lower()

        return f"""**Your Role**: You are a patient presenting to the Emergency Department/Clinic.

**Presenting Complaint**: {presenting_complaint}

**Background**: You should present as described in the scenario below, answering the doctor's questions naturally. You may be worried about your symptoms, especially if you have concerning features.

**Note**: The specific scenario details will be provided by the examiner. Answer questions based on the clinical presentation being tested.

**Emotion**: Show appropriate concern for your symptoms. If the doctor shows empathy, be more forthcoming with information. If rushed or dismissive, become more guarded.
"""

    def _generate_rubric(self, title: str, station_type: OSCEType) -> str:
        """Generate marking rubric"""
        if station_type == OSCEType.HISTORY_TAKING:
            return """### MARKING RUBRIC

**SECTION 1: Introduction & Communication (10 points)**
- Hand hygiene
- Introduction and consent
- Empathy and rapport
- Active listening

**SECTION 2: History of Presenting Complaint (25 points)**
- Systematic approach (SOCRATES/framework)
- Relevant questions
- Identifies red flags

**SECTION 3: Past Medical/Social History (15 points)**
- Past medical history
- Medications and allergies
- Social history (smoking, alcohol)
- Family history

**SECTION 4: Differential Diagnosis (20 points)**
- Identifies top 3 differentials
- Justifies with clinical features
- Prioritizes by urgency

**SECTION 5: Investigations & Management (20 points)**
- Appropriate investigations
- Australian context awareness
- Safety netting

**SECTION 6: Professionalism (10 points)**
- Professional manner
- Time management
- Summary and closure

**TOTAL: 100 points**
"""
        else:
            return """### MARKING RUBRIC

**SECTION 1: Introduction & Consent (10 points)**
- Hand hygiene
- Introduction
- Explanation and consent
- Patient comfort

**SECTION 2: Systematic Examination (50 points)**
- Inspection
- Palpation
- Percussion (if applicable)
- Auscultation (if applicable)
- Special tests

**SECTION 3: Technique (20 points)**
- Correct technique
- Appropriate exposure
- Patient comfort maintained

**SECTION 4: Findings & Interpretation (10 points)**
- Identifies key findings
- Interprets correctly

**SECTION 5: Professionalism (10 points)**
- Professional manner
- Thanks patient
- Offers to help patient dress

**TOTAL: 100 points**
"""

    def _split_into_sections(self, content: str) -> List[Tuple[str, str]]:
        """Split content into major sections (e.g., CHEST PAIN, SHORTNESS OF BREATH)"""
        sections = []

        # Find all level 2 headings (##) that are not metadata
        section_pattern = re.compile(r'^## ([A-Z][A-Z\s&/]+)$', re.MULTILINE)
        matches = list(section_pattern.finditer(content))

        for i, match in enumerate(matches):
            section_title = match.group(1).strip()

            # Skip metadata sections
            if any(skip in section_title.upper() for skip in [
                'AMC', 'PURPOSE', 'FORMAT', 'CREATED', 'UPDATED', 'INDICATOR'
            ]):
                continue

            # Get section content
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
            section_content = content[start:end].strip()

            if len(section_content) > 200:  # Only if substantial content
                sections.append((section_title.title(), section_content))

        # If no sections found, return the whole content as one section
        if not sections:
            title_match = re.search(r'^# (.+?)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else "Clinical Assessment"
            sections.append((title, content))

        return sections[:3]  # Limit to first 3 sections to avoid too many OSCEs

    def _map_difficulty(self, difficulty_str: str) -> Difficulty:
        """Map difficulty string to enum"""
        mapping = {
            'easy': Difficulty.EASY,
            'medium': Difficulty.MEDIUM,
            'intermediate': Difficulty.MEDIUM,
            'hard': Difficulty.HARD,
            'difficult': Difficulty.HARD
        }
        return mapping.get(difficulty_str.lower(), Difficulty.MEDIUM)

    def _map_specialty(self, specialty_str: str) -> Specialty:
        """Map specialty string to enum"""
        specialty_str = specialty_str.lower()

        if 'cardio' in specialty_str or 'cardiac' in specialty_str:
            return Specialty.CARDIOLOGY
        elif 'resp' in specialty_str or 'pulmon' in specialty_str:
            return Specialty.RESPIRATORY
        elif 'gastro' in specialty_str or 'gi' in specialty_str or 'abdo' in specialty_str:
            return Specialty.GASTROENTEROLOGY
        elif 'neuro' in specialty_str:
            return Specialty.NEUROLOGY
        elif 'psych' in specialty_str:
            return Specialty.PSYCHIATRY
        elif 'obst' in specialty_str or 'gyn' in specialty_str:
            return Specialty.OBSTETRICS_GYNAECOLOGY
        elif 'paed' in specialty_str:
            return Specialty.PAEDIATRICS
        elif 'surg' in specialty_str:
            return Specialty.SURGERY
        elif 'ortho' in specialty_str:
            return Specialty.ORTHOPAEDICS
        elif 'emerg' in specialty_str:
            return Specialty.EMERGENCY_MEDICINE
        else:
            return Specialty.GENERAL_MEDICINE

    def _map_specialty_from_category(self, category: str, title: str) -> Specialty:
        """Map category and title to specialty"""
        combined = (category + " " + title).lower()

        if 'obgyn' in category.lower():
            return Specialty.OBSTETRICS_GYNAECOLOGY
        elif 'paed' in category.lower():
            return Specialty.PAEDIATRICS
        elif 'psych' in category.lower():
            return Specialty.PSYCHIATRY
        elif 'surg' in category.lower():
            return Specialty.SURGERY
        elif 'cardio' in combined:
            return Specialty.CARDIOLOGY
        elif 'resp' in combined:
            return Specialty.RESPIRATORY
        elif 'gastro' in combined or 'abdo' in combined:
            return Specialty.GASTROENTEROLOGY
        elif 'neuro' in combined:
            return Specialty.NEUROLOGY
        else:
            return Specialty.GENERAL_MEDICINE

    def _infer_specialty(self, title: str) -> Specialty:
        """Infer specialty from title"""
        return self._map_specialty(title)

    def _determine_station_type(self, title: str, content: str) -> OSCEType:
        """Determine OSCE station type"""
        title_lower = title.lower()
        content_lower = content.lower()

        if 'physical examination' in title_lower or 'examination' in title_lower:
            return OSCEType.PHYSICAL_EXAMINATION
        elif 'procedure' in title_lower or 'skill' in title_lower:
            return OSCEType.PROCEDURE
        elif 'emergency' in title_lower or 'trauma' in title_lower or 'acute' in title_lower:
            return OSCEType.EMERGENCY_SCENARIO
        elif 'communication' in title_lower or 'breaking bad news' in title_lower or 'counsel' in title_lower:
            return OSCEType.COMMUNICATION
        elif 'history' in title_lower or 'differential' in title_lower:
            return OSCEType.HISTORY_TAKING
        else:
            # Default based on content
            if 'simulated patient' in content_lower and 'examiner marking' in content_lower:
                if 'examination' in content_lower[:500]:
                    return OSCEType.PHYSICAL_EXAMINATION
                else:
                    return OSCEType.HISTORY_TAKING
            return OSCEType.HISTORY_TAKING

    def _generate_osce_id(self, prefix: str, title: str) -> str:
        """Generate unique OSCE ID"""
        # Create a hash from title and add prefix
        title_hash = abs(hash(title)) % 1000
        return f"OSCE-{prefix}-{title_hash:03d}"

    def _extract_tags(self, content: str, title: str) -> List[str]:
        """Extract tags from content"""
        tags = []

        # Add AMC if mentioned
        if 'AMC' in content or 'amc' in content.lower():
            tags.append('amc_clinical')

        # Add high-yield if indicated
        if 'HIGH-YIELD' in content or 'high-yield' in content.lower():
            tags.append('high_yield')

        # Add specialty tags
        if 'cardiovascular' in title.lower() or 'cardiac' in title.lower():
            tags.append('cardiovascular')
        if 'respiratory' in title.lower() or 'lung' in title.lower():
            tags.append('respiratory')

        return tags[:5]  # Limit to 5 tags

    def import_osce(self, osce_data: Dict, db: Session) -> bool:
        """Import a single OSCE into database"""
        try:
            # Check if already exists
            existing = db.query(OSCE).filter(OSCE.osce_id == osce_data['osce_id']).first()
            if existing:
                print(f"{Colors.YELLOW}   Skipping {osce_data['osce_id']} - already exists{Colors.END}")
                self.skipped_count += 1
                return False

            if self.dry_run:
                print(f"{Colors.CYAN}   [DRY RUN] Would import: {osce_data['station_title']}{Colors.END}")
                print(f"             ID: {osce_data['osce_id']}")
                print(f"             Type: {osce_data['station_type'].value}")
                print(f"             Specialty: {osce_data['specialty'].value}")
                return True

            # Create OSCE object
            osce = OSCE(
                osce_id=osce_data['osce_id'],
                station_title=osce_data['station_title'],
                station_type=osce_data['station_type'],
                specialty=osce_data['specialty'],
                difficulty=osce_data['difficulty'],
                time_limit_minutes=osce_data['time_limit_minutes'],
                patient_instructions=osce_data['patient_instructions'],
                candidate_instructions=osce_data['candidate_instructions'],
                examiner_instructions=osce_data['examiner_instructions'],
                rubric=osce_data['rubric'],
                learning_objectives=osce_data['learning_objectives'],
                key_points=osce_data['key_points'],
                is_published=osce_data['is_published'],
                tags=osce_data.get('tags', []),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            # Handle video resources if present
            if osce_data.get('video_resources'):
                if isinstance(osce_data['video_resources'], str):
                    osce.video_resources = json.loads(osce_data['video_resources'])
                else:
                    osce.video_resources = osce_data['video_resources']

            db.add(osce)
            db.commit()

            print(f"{Colors.GREEN}   ✅ Imported: {osce_data['station_title']}{Colors.END}")
            self.imported_count += 1
            return True

        except Exception as e:
            print(f"{Colors.RED}   ❌ Error importing {osce_data.get('osce_id', 'unknown')}: {e}{Colors.END}")
            self.error_count += 1
            db.rollback()
            return False

    def run(self):
        """Main import process"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}Option 3: Import All OSCE Content{Colors.END}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

        if self.dry_run:
            print(f"{Colors.YELLOW}🔍 DRY RUN MODE - No changes will be made to database{Colors.END}\n")

        # Find all files
        print(f"{Colors.BLUE}📁 Scanning for OSCE markdown files...{Colors.END}")
        files = self.find_markdown_files()

        total_files = sum(len(f) for f in files.values())
        print(f"   Found {total_files} files:")
        for category, file_list in files.items():
            if file_list:
                print(f"     - {category}: {len(file_list)} files")
        print()

        # Process files
        db = SessionLocal()
        try:
            # 1. Import Mock Stations (easiest - already structured)
            if files['mock_stations']:
                print(f"{Colors.BOLD}{Colors.GREEN}Phase 1: Importing Mock Stations{Colors.END}")
                for file_path in files['mock_stations']:
                    print(f"  Processing: {file_path.name}")
                    osce_data = self.extract_mock_station(file_path)
                    if osce_data:
                        self.import_osce(osce_data, db)
                print()

            # 2. Import remaining categories
            for category in ['medicine', 'surgery', 'obgyn', 'paediatrics', 'psychiatry', 'communication']:
                if files[category]:
                    print(f"{Colors.BOLD}{Colors.GREEN}Phase 2: Importing {category.title()} OSCEs{Colors.END}")
                    for file_path in files[category]:
                        print(f"  Processing: {file_path.name}")
                        osces = self.extract_study_notes(file_path, category)
                        for osce_data in osces:
                            self.import_osce(osce_data, db)
                    print()

            # Summary
            print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}Import Summary{Colors.END}")
            print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")
            print(f"  {Colors.GREEN}✅ Imported: {self.imported_count}{Colors.END}")
            print(f"  {Colors.YELLOW}⏭️  Skipped: {self.skipped_count}{Colors.END}")
            print(f"  {Colors.RED}❌ Errors: {self.error_count}{Colors.END}")
            print(f"  {Colors.BOLD}📊 Total Processed: {self.imported_count + self.skipped_count + self.error_count}{Colors.END}\n")

            if not self.dry_run and self.imported_count > 0:
                # Query final count
                total_osces = db.query(OSCE).count()
                print(f"{Colors.BOLD}Total OSCEs in database: {total_osces}{Colors.END}\n")

        finally:
            db.close()


def main():
    parser = argparse.ArgumentParser(description='Import all OSCE markdown files (Option 3)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be imported without actually inserting')
    args = parser.parse_args()

    importer = OSCEImporter(dry_run=args.dry_run)
    importer.run()


if __name__ == "__main__":
    main()
