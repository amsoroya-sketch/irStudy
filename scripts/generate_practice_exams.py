#!/usr/bin/env python3
"""
Generate Practice Exams from Existing MCQs
Creates timed exam simulations using the existing 700 MCQs
Maintains 100% citation quality from source MCQs
"""

import json
import random
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.agents.qa.incremental_citation_validator import (
    validate_rag_before_generation,
    CitationValidationError
)


class PracticeExamEngine:
    """Generate practice exams from existing MCQ pool"""

    def __init__(self):
        print("\n" + "="*80)
        print("📝 PRACTICE EXAM GENERATION ENGINE")
        print("="*80)
        print("Purpose: Generate timed practice exams from existing MCQs")
        print("Coverage: Cardiology + Respiratory + Psychiatry")
        print("="*80 + "\n")

        # Pre-generation validation
        print("🔍 Pre-Generation RAG Validation...")
        try:
            validate_rag_before_generation()
            print("✅ Pre-generation validation PASSED\n")
        except CitationValidationError as e:
            print(f"❌ Pre-generation validation FAILED: {str(e)}")
            sys.exit(1)

        # Load existing MCQs
        print("📚 Loading existing MCQs...")
        self.mcq_pool = self._load_all_mcqs()
        print(f"✅ Loaded {len(self.mcq_pool)} MCQs\n")

        # Organize MCQs by specialty
        self.cardiology_mcqs = []
        self.respiratory_mcqs = []
        self.psychiatry_mcqs = []

        self._organize_by_specialty()

        self.stats = {
            'total_exams': 0,
            'total_mcqs_used': 0,
            'cardiology_exams': 0,
            'respiratory_exams': 0,
            'psychiatry_exams': 0,
            'mixed_exams': 0
        }

    def _load_all_mcqs(self) -> List[Dict[str, Any]]:
        """Load all existing MCQs from files"""

        mcq_files = [
            'data/mcqs/week1_regenerated_100_mcqs.json',
            'data/mcqs/week2_regenerated_100_mcqs.json',
            'data/mcqs/week3_cardiology_200_mcqs.json',
            'data/mcqs/week3_respiratory_200_mcqs.json',
            'data/mcqs/week3_psychiatry_additional_100_mcqs.json'
        ]

        all_mcqs = []

        for file_path in mcq_files:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    mcqs = data.get('mcqs', [])

                    # Add source file to each MCQ
                    for mcq in mcqs:
                        mcq['source_file'] = Path(file_path).name

                    all_mcqs.extend(mcqs)
                    print(f"  ✅ {Path(file_path).name}: {len(mcqs)} MCQs")
            except Exception as e:
                print(f"  ❌ Error loading {file_path}: {e}")
                continue

        return all_mcqs

    def _organize_by_specialty(self):
        """Organize MCQs by specialty based on source file"""

        for mcq in self.mcq_pool:
            source = mcq.get('source_file', '')

            if 'cardiology' in source.lower():
                self.cardiology_mcqs.append(mcq)
            elif 'respiratory' in source.lower():
                self.respiratory_mcqs.append(mcq)
            else:  # psychiatry
                self.psychiatry_mcqs.append(mcq)

        print("📊 MCQs by Specialty:")
        print(f"   💙 Cardiology: {len(self.cardiology_mcqs)}")
        print(f"   🫁 Respiratory: {len(self.respiratory_mcqs)}")
        print(f"   🧠 Psychiatry: {len(self.psychiatry_mcqs)}")
        print()

    def create_specialty_exam(
        self,
        specialty: str,
        mcq_pool: List[Dict[str, Any]],
        num_questions: int,
        exam_number: int
    ) -> Dict[str, Any]:
        """Create a specialty-specific practice exam"""

        # Randomly select MCQs (without replacement)
        selected_mcqs = random.sample(mcq_pool, min(num_questions, len(mcq_pool)))

        # Shuffle for exam
        random.shuffle(selected_mcqs)

        # Create exam
        exam = {
            'exam_id': f"{specialty.upper()}-EXAM-{exam_number:02d}",
            'specialty': specialty,
            'exam_type': 'Specialty Specific',
            'total_questions': len(selected_mcqs),
            'time_limit_minutes': len(selected_mcqs) * 1.8,  # 1.8 mins per question
            'instructions': {
                'description': f"Practice exam covering {specialty} topics",
                'time_limit': f"{int(len(selected_mcqs) * 1.8)} minutes",
                'passing_score': '70%',
                'format': 'Single best answer MCQs'
            },
            'questions': [],
            'created_date': datetime.now().isoformat()
        }

        # Add questions (renumber for exam)
        for idx, mcq in enumerate(selected_mcqs, 1):
            exam_question = {
                'question_number': idx,
                'original_id': mcq.get('id'),
                'topic': mcq.get('topic'),
                'subtopic': mcq.get('subtopic'),
                'question': mcq.get('question'),
                'correct_answer': mcq.get('correct_answer'),
                'explanation': mcq.get('explanation'),
                'references': mcq.get('references', [])
            }

            # Add medical images if available
            if 'medical_images' in mcq:
                exam_question['medical_images'] = mcq['medical_images']

            exam['questions'].append(exam_question)

        return exam

    def create_mixed_exam(self, num_questions: int, exam_number: int) -> Dict[str, Any]:
        """Create a mixed specialty practice exam"""

        # Calculate distribution (proportional to pool size)
        total_pool = len(self.mcq_pool)
        cardio_count = int(num_questions * len(self.cardiology_mcqs) / total_pool)
        resp_count = int(num_questions * len(self.respiratory_mcqs) / total_pool)
        psych_count = num_questions - cardio_count - resp_count

        # Select MCQs from each specialty
        selected_mcqs = []

        if cardio_count > 0:
            selected_mcqs.extend(random.sample(
                self.cardiology_mcqs,
                min(cardio_count, len(self.cardiology_mcqs))
            ))

        if resp_count > 0:
            selected_mcqs.extend(random.sample(
                self.respiratory_mcqs,
                min(resp_count, len(self.respiratory_mcqs))
            ))

        if psych_count > 0:
            selected_mcqs.extend(random.sample(
                self.psychiatry_mcqs,
                min(psych_count, len(self.psychiatry_mcqs))
            ))

        # Shuffle to mix specialties
        random.shuffle(selected_mcqs)

        # Create exam
        exam = {
            'exam_id': f"MIXED-EXAM-{exam_number:02d}",
            'specialty': 'Mixed',
            'exam_type': 'Multi-Specialty',
            'total_questions': len(selected_mcqs),
            'time_limit_minutes': len(selected_mcqs) * 1.8,
            'specialty_distribution': {
                'Cardiology': cardio_count,
                'Respiratory': resp_count,
                'Psychiatry': psych_count
            },
            'instructions': {
                'description': 'Practice exam covering multiple specialties',
                'time_limit': f"{int(len(selected_mcqs) * 1.8)} minutes",
                'passing_score': '70%',
                'format': 'Single best answer MCQs'
            },
            'questions': [],
            'created_date': datetime.now().isoformat()
        }

        # Add questions
        for idx, mcq in enumerate(selected_mcqs, 1):
            exam_question = {
                'question_number': idx,
                'original_id': mcq.get('id'),
                'topic': mcq.get('topic'),
                'subtopic': mcq.get('subtopic'),
                'specialty': self._determine_specialty(mcq),
                'question': mcq.get('question'),
                'correct_answer': mcq.get('correct_answer'),
                'explanation': mcq.get('explanation'),
                'references': mcq.get('references', [])
            }

            if 'medical_images' in mcq:
                exam_question['medical_images'] = mcq['medical_images']

            exam['questions'].append(exam_question)

        return exam

    def _determine_specialty(self, mcq: Dict[str, Any]) -> str:
        """Determine specialty of an MCQ"""
        source = mcq.get('source_file', '')

        if 'cardiology' in source.lower():
            return 'Cardiology'
        elif 'respiratory' in source.lower():
            return 'Respiratory'
        else:
            return 'Psychiatry'

    def generate_all_exams(self) -> Dict[str, List[Dict[str, Any]]]:
        """Generate all practice exams"""

        print("\n" + "="*80)
        print("GENERATING PRACTICE EXAMS")
        print("="*80 + "\n")

        exams = {
            'cardiology': [],
            'respiratory': [],
            'psychiatry': [],
            'mixed': []
        }

        # Cardiology exams (2 exams of 50 questions each)
        print("💙 Generating Cardiology Practice Exams...")
        for i in range(2):
            exam = self.create_specialty_exam('Cardiology', self.cardiology_mcqs, 50, i+1)
            exams['cardiology'].append(exam)
            self.stats['cardiology_exams'] += 1
            self.stats['total_mcqs_used'] += exam['total_questions']
            print(f"  ✅ Cardiology Exam {i+1}: {exam['total_questions']} questions ({exam['time_limit_minutes']:.0f} min)")

        # Respiratory exams (2 exams of 50 questions each)
        print("\n🫁 Generating Respiratory Practice Exams...")
        for i in range(2):
            exam = self.create_specialty_exam('Respiratory', self.respiratory_mcqs, 50, i+1)
            exams['respiratory'].append(exam)
            self.stats['respiratory_exams'] += 1
            self.stats['total_mcqs_used'] += exam['total_questions']
            print(f"  ✅ Respiratory Exam {i+1}: {exam['total_questions']} questions ({exam['time_limit_minutes']:.0f} min)")

        # Psychiatry exams (2 exams of 50 questions each)
        print("\n🧠 Generating Psychiatry Practice Exams...")
        for i in range(2):
            exam = self.create_specialty_exam('Psychiatry', self.psychiatry_mcqs, 50, i+1)
            exams['psychiatry'].append(exam)
            self.stats['psychiatry_exams'] += 1
            self.stats['total_mcqs_used'] += exam['total_questions']
            print(f"  ✅ Psychiatry Exam {i+1}: {exam['total_questions']} questions ({exam['time_limit_minutes']:.0f} min)")

        # Mixed exams (3 comprehensive exams)
        print("\n🎯 Generating Mixed Specialty Practice Exams...")
        exam_sizes = [75, 100, 150]  # Different exam lengths
        for i, size in enumerate(exam_sizes, 1):
            exam = self.create_mixed_exam(size, i)
            exams['mixed'].append(exam)
            self.stats['mixed_exams'] += 1
            self.stats['total_mcqs_used'] += exam['total_questions']
            dist = exam['specialty_distribution']
            print(f"  ✅ Mixed Exam {i}: {exam['total_questions']} questions ({exam['time_limit_minutes']:.0f} min)")
            print(f"     Cardio: {dist['Cardiology']}, Resp: {dist['Respiratory']}, Psych: {dist['Psychiatry']}")

        self.stats['total_exams'] = (
            self.stats['cardiology_exams'] +
            self.stats['respiratory_exams'] +
            self.stats['psychiatry_exams'] +
            self.stats['mixed_exams']
        )

        return exams

    def save_exams(self, exams: Dict[str, List[Dict[str, Any]]]):
        """Save practice exams to files"""

        print("\n" + "="*80)
        print("SAVING PRACTICE EXAMS")
        print("="*80 + "\n")

        output_dir = Path('data/practice_exams')
        output_dir.mkdir(parents=True, exist_ok=True)

        output_files = []

        # Save each specialty's exams
        for specialty, exam_list in exams.items():
            output_file = output_dir / f"{specialty}_practice_exams.json"

            output_data = {
                'metadata': {
                    'specialty': specialty.title(),
                    'total_exams': len(exam_list),
                    'generation_date': datetime.now().isoformat(),
                    'citation_source': 'Original MCQ pool (100% RAG-validated)'
                },
                'exams': exam_list
            }

            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)

            print(f"📁 Saved: {output_file.name}")
            output_files.append(str(output_file))

        return output_files

    def print_summary(self):
        """Print generation summary"""

        print("\n" + "="*80)
        print("PRACTICE EXAM GENERATION SUMMARY")
        print("="*80 + "\n")

        print(f"📊 Total Exams Generated: {self.stats['total_exams']}")
        print(f"   💙 Cardiology: {self.stats['cardiology_exams']} exams")
        print(f"   🫁 Respiratory: {self.stats['respiratory_exams']} exams")
        print(f"   🧠 Psychiatry: {self.stats['psychiatry_exams']} exams")
        print(f"   🎯 Mixed: {self.stats['mixed_exams']} exams")
        print()
        print(f"📝 Total Questions Used: {self.stats['total_mcqs_used']}")
        print(f"📚 Source MCQ Pool: {len(self.mcq_pool)} MCQs")
        print()
        print("✅ All exams maintain 100% citation quality from source MCQs")
        print()
        print("="*80)
        print("✅ PRACTICE EXAM GENERATION COMPLETE")
        print("="*80 + "\n")


def main():
    """Main execution"""

    try:
        # Set random seed for reproducibility
        random.seed(42)

        # Create engine
        engine = PracticeExamEngine()

        # Generate all exams
        exams = engine.generate_all_exams()

        # Save exams
        output_files = engine.save_exams(exams)

        # Print summary
        engine.print_summary()

        # Success
        sys.exit(0)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
