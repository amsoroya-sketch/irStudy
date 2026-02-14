#!/usr/bin/env python3
"""
Load ALL Data to PostgreSQL Database
Loads all available MCQs and OSCEs from JSON files
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend' / 'src'))

from db.models import Base, MCQ, OSCE, MedicalSpecialty, DifficultyLevel, OSCEType
from db.base import get_database_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataLoader:
    """Load sample medical data into PostgreSQL"""

    def __init__(self, database_url: str = None):
        """Initialize database connection"""
        self.database_url = database_url or get_database_url()
        self.engine = create_engine(self.database_url)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        logger.info(f"✓ Connected to database")

    def load_mcqs_from_file(self, filepath: str, limit: int = None) -> int:
        """Load MCQs from JSON file"""
        logger.info(f"Loading MCQs from {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract MCQs from nested structure
        mcqs_data = data.get('mcqs', data) if isinstance(data, dict) else data

        if limit:
            mcqs_data = mcqs_data[:limit]

        loaded_count = 0
        skipped_count = 0

        for mcq_data in mcqs_data:
            # Skip placeholder MCQs
            if mcq_data.get('regeneration_failed', False):
                skipped_count += 1
                continue

            # Check for placeholder content
            options = mcq_data.get('question', {}).get('options', {})
            if any('Option A' in str(v) or 'Option B' in str(v) for v in options.values()):
                skipped_count += 1
                continue

            # Map specialty from topic/subtopic
            specialty = self._map_specialty(mcq_data.get('topic', ''))
            difficulty = self._map_difficulty(mcq_data.get('difficulty', 'medium'))

            # Combine scenario and stem for question_text
            scenario = mcq_data.get('question', {}).get('scenario', '')
            stem = mcq_data.get('question', {}).get('stem', '')
            question_text = f"{scenario}\n\n{stem}" if scenario else stem

            # Generate unique question ID
            specialty_code = specialty.value.upper().replace('_', '-')
            question_id = mcq_data.get('id', f"MCQ-{specialty_code}-{loaded_count + 1:03d}")

            # Format explanation (handle both string and dict formats)
            explanation = self._format_explanation(mcq_data.get('explanation', ''))

            # Create MCQ object
            mcq = MCQ(
                question_id=question_id,
                question_text=question_text,
                options=options,
                correct_answer=mcq_data.get('correct_answer', 'A'),
                explanation=explanation,
                citation=self._format_citation(mcq_data.get('references', [])),
                learning_points=mcq_data.get('learning_objectives', []),
                specialty=specialty,
                difficulty=difficulty,
                tags=self._extract_tags(mcq_data),
            )

            self.session.add(mcq)
            loaded_count += 1

        self.session.commit()
        logger.info(f"✓ Loaded {loaded_count} MCQs (skipped {skipped_count} placeholders)")
        return loaded_count

    def load_osces_from_file(self, filepath: str, limit: int = None) -> int:
        """Load OSCEs from JSON file"""
        logger.info(f"Loading OSCEs from {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract OSCEs from nested structure
        osces_data = data.get('osces', data) if isinstance(data, dict) else data

        if limit:
            osces_data = osces_data[:limit]

        loaded_count = 0

        for osce_data in osces_data:
            # Map specialty and type
            specialty = self._map_specialty(osce_data.get('specialty', ''))
            osce_type = self._map_osce_type(osce_data.get('scenario_type', 'history_taking'))

            # Generate station title from topic/subtopic
            topic = osce_data.get('topic', 'Medical Assessment')
            subtopic = osce_data.get('subtopic', '')
            station_title = f"{topic}: {subtopic}" if subtopic else topic

            # Generate unique OSCE ID
            specialty_code = specialty.value.upper().replace('_', '-')
            osce_id = osce_data.get('id', f"OSCE-{specialty_code}-{loaded_count + 1:03d}")

            # Build rubric from tasks and total_marks
            tasks_raw = osce_data.get('tasks', [])
            total_marks = osce_data.get('total_marks', 15)

            # Extract task descriptions and build rubric
            task_descriptions = []
            rubric_tasks = []
            if isinstance(tasks_raw, list):
                for task in tasks_raw:
                    if isinstance(task, dict):
                        desc = task.get('description', '')
                        marks = task.get('marks', 0)
                        task_descriptions.append(desc)
                        rubric_tasks.append({'description': desc, 'marks': marks})
                    else:
                        task_descriptions.append(str(task))
                        rubric_tasks.append({'description': str(task), 'marks': 0})

            rubric = self._build_rubric_from_tasks(rubric_tasks, total_marks)

            # Format scenario for candidate instructions
            scenario = osce_data.get('scenario', '')
            candidate_instructions = self._format_scenario(scenario)

            # Create OSCE object
            osce = OSCE(
                osce_id=osce_id,
                station_title=station_title,
                station_type=osce_type,
                candidate_instructions=candidate_instructions,
                patient_instructions='\n'.join(task_descriptions),
                examiner_instructions=self._format_expected_answers(osce_data.get('expected_answers', {})),
                rubric=rubric,
                specialty=specialty,
                difficulty=self._map_difficulty(osce_data.get('difficulty', 'medium')),
                time_limit_minutes=osce_data.get('duration_minutes', 8),
                learning_objectives=self._extract_learning_objectives(osce_data.get('references', [])),
                key_points=task_descriptions,
            )

            self.session.add(osce)
            loaded_count += 1

        self.session.commit()
        logger.info(f"✓ Loaded {loaded_count} OSCEs")
        return loaded_count

    def _map_specialty(self, topic: str) -> MedicalSpecialty:
        """Map topic string to MedicalSpecialty enum"""
        topic_lower = topic.lower()

        specialty_map = {
            'cardio': MedicalSpecialty.CARDIOLOGY,
            'heart': MedicalSpecialty.CARDIOLOGY,
            'coronary': MedicalSpecialty.CARDIOLOGY,
            'mi': MedicalSpecialty.CARDIOLOGY,
            'ecg': MedicalSpecialty.CARDIOLOGY,
            'arrhythmia': MedicalSpecialty.CARDIOLOGY,
            'respiratory': MedicalSpecialty.RESPIRATORY,
            'lung': MedicalSpecialty.RESPIRATORY,
            'asthma': MedicalSpecialty.RESPIRATORY,
            'copd': MedicalSpecialty.RESPIRATORY,
            'pneumonia': MedicalSpecialty.RESPIRATORY,
            'psychiatry': MedicalSpecialty.PSYCHIATRY,
            'depression': MedicalSpecialty.PSYCHIATRY,
            'anxiety': MedicalSpecialty.PSYCHIATRY,
            'psychosis': MedicalSpecialty.PSYCHIATRY,
            'gastro': MedicalSpecialty.GASTROENTEROLOGY,
            'neuro': MedicalSpecialty.NEUROLOGY,
            'emergency': MedicalSpecialty.EMERGENCY_MEDICINE,
            'paed': MedicalSpecialty.PAEDIATRICS,
            'obs': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
            'gyn': MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
            'surgery': MedicalSpecialty.SURGERY,
        }

        for keyword, specialty in specialty_map.items():
            if keyword in topic_lower:
                return specialty

        return MedicalSpecialty.GENERAL_PRACTICE

    def _map_difficulty(self, difficulty: str) -> DifficultyLevel:
        """Map difficulty string to DifficultyLevel enum"""
        difficulty_map = {
            'easy': DifficultyLevel.EASY,
            'medium': DifficultyLevel.MEDIUM,
            'hard': DifficultyLevel.HARD,
        }
        return difficulty_map.get(difficulty.lower(), DifficultyLevel.MEDIUM)

    def _map_osce_type(self, osce_type: str) -> OSCEType:
        """Map OSCE type string to OSCEType enum"""
        type_map = {
            'history': OSCEType.HISTORY_TAKING,
            'examination': OSCEType.PHYSICAL_EXAMINATION,
            'counselling': OSCEType.COUNSELLING,
            'communication': OSCEType.COMMUNICATION,
            'diagnosis': OSCEType.DIAGNOSIS_MANAGEMENT,
            'emergency': OSCEType.EMERGENCY_SCENARIO,
        }

        osce_type_lower = osce_type.lower()
        for keyword, mapped_type in type_map.items():
            if keyword in osce_type_lower:
                return mapped_type

        return OSCEType.HISTORY_TAKING

    def _format_explanation(self, explanation: any) -> str:
        """Format explanation (handle both string and dict formats)"""
        if isinstance(explanation, str):
            return explanation

        if isinstance(explanation, dict):
            # Extract key parts from dict explanation
            parts = []

            # Why correct answer is correct
            if 'why_correct' in explanation:
                parts.append(f"Correct: {explanation['why_correct']}")

            # Why incorrect options are wrong
            if 'why_incorrect' in explanation:
                incorrect = explanation['why_incorrect']
                if isinstance(incorrect, dict):
                    for key, value in incorrect.items():
                        parts.append(f"{key}: {value}")
                elif isinstance(incorrect, str):
                    parts.append(f"Incorrect: {incorrect}")

            # Key learning points
            if 'key_learning_points' in explanation:
                points = explanation['key_learning_points']
                if isinstance(points, list):
                    parts.append("Key Points: " + "; ".join(points))
                elif isinstance(points, str):
                    parts.append(f"Key Points: {points}")

            return "\n\n".join(parts) if parts else str(explanation)

        # Fallback to string representation
        return str(explanation) if explanation else ""

    def _format_citation(self, references: list) -> str:
        """Format references into citation string"""
        if not references:
            return ""

        citations = []
        for ref in references[:2]:  # Top 2 references
            title = ref.get('title', '')
            page = ref.get('page', 0)
            if title and page:
                citations.append(f"{title} p.{page}")

        return ", ".join(citations)

    def _extract_tags(self, data: dict) -> list:
        """Extract tags from MCQ/OSCE data"""
        tags = []

        # Add topic/subtopic as tags
        if 'topic' in data:
            tags.append(data['topic'].lower().replace(' ', '_'))
        if 'subtopic' in data:
            tags.append(data['subtopic'].lower().replace(' ', '_'))

        # Add specialty tag
        if 'specialty' in data:
            tags.append(data['specialty'].lower())

        return list(set(tags))  # Remove duplicates

    def _build_rubric_from_tasks(self, rubric_tasks: list, total_marks: int) -> dict:
        """Build OSCE rubric JSON from tasks with marks"""
        if not rubric_tasks:
            return {
                "assessment": {
                    "max_marks": total_marks,
                    "criteria": "Overall clinical performance"
                }
            }

        rubric = {}
        for i, task in enumerate(rubric_tasks):
            key = f"task_{i + 1}"
            rubric[key] = {
                "max_marks": task.get('marks', 0),
                "criteria": task.get('description', '')
            }

        return rubric

    def _format_scenario(self, scenario: any) -> str:
        """Format scenario into candidate instructions text"""
        if isinstance(scenario, str):
            return scenario

        if not isinstance(scenario, dict):
            return str(scenario)

        # Build formatted text from scenario dictionary
        sections = []

        # Patient presentation
        if 'patient_presentation' in scenario:
            sections.append(scenario['patient_presentation'])

        # Clinical history
        if 'history' in scenario:
            sections.append(f"\nClinical History:\n{scenario['history']}")

        # Vital signs
        if 'vital_signs' in scenario and isinstance(scenario['vital_signs'], dict):
            vital_signs = scenario['vital_signs']
            vitals_str = ', '.join(f"{k}: {v}" for k, v in vital_signs.items())
            sections.append(f"\nVital Signs:\n{vitals_str}")

        # Examination findings
        if 'examination_findings' in scenario:
            sections.append(f"\nExamination Findings:\n{scenario['examination_findings']}")

        # Images/investigations (reference only, actual images not embedded)
        if 'images' in scenario and isinstance(scenario['images'], list):
            image_count = len(scenario['images'])
            if image_count > 0:
                sections.append(f"\n[{image_count} investigation image(s) provided]")

        return '\n'.join(sections)

    def _format_expected_answers(self, expected_answers: dict) -> str:
        """Format expected answers into examiner instructions"""
        if not expected_answers:
            return ""

        sections = []
        for key, value in expected_answers.items():
            section_title = key.replace('_', ' ').title()
            if isinstance(value, list):
                items = '\n'.join(f"  • {item}" for item in value)
                sections.append(f"{section_title}:\n{items}")
            else:
                sections.append(f"{section_title}: {value}")

        return '\n\n'.join(sections)

    def _extract_learning_objectives(self, references: list) -> list:
        """Extract learning objectives from references"""
        if not references:
            return []

        # Use reference titles as learning objectives
        objectives = []
        for ref in references[:3]:  # Top 3 references
            title = ref.get('title', '') if isinstance(ref, dict) else str(ref)
            if title:
                objectives.append(f"Review: {title}")

        return objectives

    def get_stats(self):
        """Get database statistics"""
        mcq_count = self.session.query(MCQ).count()
        osce_count = self.session.query(OSCE).count()

        return {
            'mcqs': mcq_count,
            'osces': osce_count,
        }

    def close(self):
        """Close database connection"""
        self.session.close()


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Load ALL data to PostgreSQL")
    parser.add_argument('--clear', action='store_true', help='Clear existing data first')

    args = parser.parse_args()

    # Initialize loader
    loader = DataLoader()

    # Clear existing data if requested
    if args.clear:
        logger.info("Clearing existing data...")
        loader.session.query(MCQ).delete()
        loader.session.query(OSCE).delete()
        loader.session.commit()
        logger.info("✓ Database cleared")

    # Find all MCQ files
    data_dir = Path(__file__).parent.parent / 'data'
    mcq_dir = data_dir / 'mcqs'
    osce_dir = data_dir / 'osces'

    # Load all MCQs (skip backup files to avoid duplicates)
    total_mcqs = 0
    mcq_files = sorted([
        f for f in mcq_dir.glob('*.json')
        if 'backup' not in f.name.lower() and 'with_images' not in f.name.lower()
    ])

    logger.info(f"\n📚 Found {len(mcq_files)} MCQ files (excluding backups)")
    for mcq_file in mcq_files:
        try:
            count = loader.load_mcqs_from_file(str(mcq_file))
            total_mcqs += count
        except Exception as e:
            logger.error(f"❌ Error loading {mcq_file.name}: {e}")
            # Rollback the session to continue with next file
            loader.session.rollback()

    # Load all OSCEs (skip backup files to avoid duplicates)
    total_osces = 0
    osce_files = sorted([
        f for f in osce_dir.glob('*.json')
        if 'backup' not in f.name.lower() and 'with_images' not in f.name.lower()
    ])

    logger.info(f"\n🏥 Found {len(osce_files)} OSCE files (excluding backups)")
    for osce_file in osce_files:
        try:
            count = loader.load_osces_from_file(str(osce_file))
            total_osces += count
        except Exception as e:
            logger.error(f"❌ Error loading {osce_file.name}: {e}")
            # Rollback the session to continue with next file
            loader.session.rollback()

    # Show final stats
    logger.info("\n" + "="*50)
    logger.info("=== FINAL DATABASE STATISTICS ===")
    logger.info("="*50)
    stats = loader.get_stats()
    logger.info(f"Total MCQs: {stats['mcqs']}")
    logger.info(f"Total OSCEs: {stats['osces']}")
    logger.info("="*50)

    loader.close()

    logger.info("\n✓ FULL DATA IMPORT COMPLETE!")
    logger.info("  Test API at: http://localhost:8001/api/docs")


if __name__ == '__main__':
    main()
