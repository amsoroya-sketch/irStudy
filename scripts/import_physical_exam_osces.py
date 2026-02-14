"""
Import Physical Examination OSCEs from Markdown Files

Creates physical examination OSCE entries in database based on the comprehensive
markdown files in ICRP_OSCE_Preparation folder.

Usage:
    python scripts/import_physical_exam_osces.py
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from src.db.base import engine, SessionLocal
from src.db.models import OSCE, OSCEType, MedicalSpecialty

# Physical examination OSCEs to create
PHYSICAL_EXAM_OSCES = [
    {
        "osce_id": "OSCE-MED-CARDIO-001",
        "station_title": "Cardiovascular Physical Examination",
        "specialty": MedicalSpecialty.CARDIOLOGY,
        "patient_instructions": """You are a patient attending for a cardiovascular examination.

**Your Symptoms:**
- You have been experiencing occasional chest discomfort on exertion
- You sometimes feel short of breath when climbing stairs
- You have no pain at rest

**Your History:**
- Age: 65 years
- You have high blood pressure (controlled with medication)
- You do not smoke
- Your father had a heart attack at age 70

**During the examination:**
- Allow the doctor to examine your hands, neck, and chest
- Inform them if you feel uncomfortable
- Answer questions honestly about your symptoms""",
        "candidate_instructions": """Perform a systematic cardiovascular examination on this patient.

**Task:**
- Perform a complete cardiovascular examination
- Use the systematic approach (inspection, palpation, percussion, auscultation)
- Present your findings to the examiner

**Time:** 8 minutes

**Note:** The patient has consented to the examination. A chaperone is available if needed.""",
        "examiner_instructions": """Observe the candidate performing a cardiovascular examination.

**Assessment Criteria:**
1. **Preparation** (Wash hands, introduce, gain consent)
2. **Systematic approach** (Hands → Neck → Precordium)
3. **Correct technique** (Proper auscultation sites, positioning)
4. **Communication** (Clear, professional, patient comfort)
5. **Presentation** (Concise summary of findings)

**Expected findings:** Normal cardiovascular examination
**Common mistakes:** Forgetting to expose adequately, incorrect auscultation sites, poor presentation""",
        "rubric": {
            "criteria": [
                {"item": "Hand hygiene and introduction", "points": 2},
                {"item": "Appropriate patient positioning (45 degrees)", "points": 2},
                {"item": "Systematic hand examination (clubbing, cyanosis, splinter hemorrhages)", "points": 3},
                {"item": "Pulse examination (rate, rhythm, character)", "points": 3},
                {"item": "Blood pressure measurement offered", "points": 2},
                {"item": "JVP assessment", "points": 3},
                {"item": "Carotid pulse palpation", "points": 2},
                {"item": "Precordial inspection", "points": 2},
                {"item": "Apex beat palpation", "points": 3},
                {"item": "Auscultation at all 4 areas (APTM)", "points": 4},
                {"item": "Dynamic maneuvers (sitting forward, left lateral)", "points": 3},
                {"item": "Peripheral perfusion check", "points": 2},
                {"item": "Ankle edema check", "points": 2},
                {"item": "Professional communication throughout", "points": 3},
                {"item": "Clear presentation of findings", "points": 4}
            ],
            "total_points": 40,
            "pass_mark": 28
        },
        "learning_objectives": [
            "Perform a systematic cardiovascular examination",
            "Identify normal and abnormal cardiovascular signs",
            "Demonstrate appropriate communication with patients",
            "Present findings concisely to examiners"
        ],
        "key_points": [
            "Always position patient at 45 degrees for JVP assessment",
            "Auscultate at 4 key areas: Aortic, Pulmonary, Tricuspid, Mitral (APTM)",
            "Use dynamic maneuvers to accentuate murmurs",
            "Check for peripheral signs (clubbing, cyanosis, edema)"
        ],
        "station_type": OSCEType.PHYSICAL_EXAMINATION,
        "time_limit_minutes": 8,
        "difficulty": "intermediate",
        "is_published": True
    },
    {
        "osce_id": "OSCE-MED-RESP-001",
        "station_title": "Respiratory Physical Examination",
        "specialty": MedicalSpecialty.RESPIRATORY,
        "patient_instructions": """You are a patient attending for a respiratory examination.

**Your Symptoms:**
- You have been experiencing a persistent cough for 3 weeks
- You sometimes feel short of breath
- You have no chest pain

**Your History:**
- Age: 58 years
- You are a non-smoker
- You work in an office
- No previous lung problems

**During the examination:**
- Allow the doctor to examine your hands, neck, and chest
- Breathe normally unless asked to breathe deeply
- Inform them if you feel uncomfortable""",
        "candidate_instructions": """Perform a systematic respiratory examination on this patient.

**Task:**
- Perform a complete respiratory examination
- Use the systematic approach (inspection, palpation, percussion, auscultation)
- Present your findings to the examiner

**Time:** 8 minutes

**Note:** The patient has consented to the examination.""",
        "examiner_instructions": """Observe the candidate performing a respiratory examination.

**Assessment Criteria:**
1. **Preparation** (Wash hands, introduce, gain consent)
2. **Systematic approach** (Hands → Neck → Chest)
3. **Correct technique** (Proper percussion, auscultation)
4. **Communication** (Clear, professional, patient comfort)
5. **Presentation** (Concise summary of findings)

**Expected findings:** Normal respiratory examination
**Common mistakes:** Inadequate percussion, forgetting tracheal deviation check, poor positioning""",
        "rubric": {
            "criteria": [
                {"item": "Hand hygiene and introduction", "points": 2},
                {"item": "Patient positioning (sitting up, exposed chest)", "points": 2},
                {"item": "Hand examination (clubbing, cyanosis, nicotine staining)", "points": 3},
                {"item": "Respiratory rate and pattern observation", "points": 2},
                {"item": "Tracheal position assessment", "points": 3},
                {"item": "Lymph node examination", "points": 2},
                {"item": "Chest inspection (shape, scars, asymmetry)", "points": 3},
                {"item": "Chest expansion assessment", "points": 3},
                {"item": "Tactile vocal fremitus", "points": 2},
                {"item": "Percussion technique and comparison", "points": 4},
                {"item": "Auscultation (all zones, breath sounds, added sounds)", "points": 5},
                {"item": "Vocal resonance", "points": 2},
                {"item": "Posterior chest examination", "points": 3},
                {"item": "Professional communication", "points": 2},
                {"item": "Clear presentation of findings", "points": 4}
            ],
            "total_points": 42,
            "pass_mark": 29
        },
        "learning_objectives": [
            "Perform systematic respiratory examination",
            "Identify normal and abnormal respiratory signs",
            "Demonstrate proper percussion and auscultation technique",
            "Present findings clearly and concisely"
        ],
        "key_points": [
            "Always check tracheal position first",
            "Compare left and right sides systematically",
            "Proper percussion technique is crucial",
            "Examine both anterior and posterior chest"
        ],
        "station_type": OSCEType.PHYSICAL_EXAMINATION,
        "time_limit_minutes": 8,
        "difficulty": "intermediate",
        "is_published": True
    },
    {
        "osce_id": "OSCE-MED-ABDO-001",
        "station_title": "Abdominal Physical Examination",
        "specialty": MedicalSpecialty.GASTROENTEROLOGY,
        "patient_instructions": """You are a patient attending for an abdominal examination.

**Your Symptoms:**
- You have been experiencing some abdominal discomfort
- The discomfort is mainly in the upper abdomen
- You have no nausea or vomiting

**Your History:**
- Age: 52 years
- No previous abdominal surgery
- No significant medical history
- You drink alcohol occasionally

**During the examination:**
- Lie flat with arms by your side
- Allow the doctor to examine your abdomen
- Tell them if anything hurts""",
        "candidate_instructions": """Perform a systematic abdominal examination on this patient.

**Task:**
- Perform a complete abdominal examination
- Use the systematic IPPA approach
- Present your findings to the examiner

**Time:** 8 minutes

**Note:** The patient has consented to the examination.""",
        "examiner_instructions": """Observe the candidate performing an abdominal examination.

**Assessment Criteria:**
1. **Preparation** (Wash hands, introduce, position patient)
2. **Systematic approach** (Inspection, Palpation, Percussion, Auscultation)
3. **Correct technique** (Light then deep palpation, proper percussion)
4. **Communication** (Checking for pain, professional manner)
5. **Presentation** (Clear summary of findings)

**Expected findings:** Normal abdominal examination
**Common mistakes:** Forgetting to auscultate before palpation, inadequate exposure, not examining for hernias""",
        "rubric": {
            "criteria": [
                {"item": "Hand hygiene and introduction", "points": 2},
                {"item": "Patient positioning (supine, arms by side)", "points": 2},
                {"item": "Adequate exposure (nipples to knees)", "points": 2},
                {"item": "General inspection from end of bed", "points": 2},
                {"item": "Hand examination (palmar erythema, clubbing, Dupuytren)", "points": 2},
                {"item": "Inspection of abdomen (distension, scars, masses)", "points": 3},
                {"item": "Auscultation (bowel sounds)", "points": 3},
                {"item": "Light palpation (all 9 quadrants)", "points": 3},
                {"item": "Deep palpation (assessing for masses)", "points": 3},
                {"item": "Liver palpation (starting in RIF)", "points": 3},
                {"item": "Spleen palpation", "points": 3},
                {"item": "Kidney palpation (bimanual)", "points": 2},
                {"item": "Percussion (liver, spleen, bladder, shifting dullness)", "points": 4},
                {"item": "Hernial orifices examination", "points": 2},
                {"item": "Ankle edema check", "points": 2},
                {"item": "Professional communication", "points": 2},
                {"item": "Clear presentation", "points": 4}
            ],
            "total_points": 44,
            "pass_mark": 31
        },
        "learning_objectives": [
            "Perform systematic abdominal examination",
            "Identify organomegaly and masses",
            "Demonstrate proper palpation technique",
            "Present findings systematically"
        ],
        "key_points": [
            "Always auscultate BEFORE palpation",
            "Start liver palpation in RIF (may be massively enlarged)",
            "Always examine for hernias",
            "Check for shifting dullness if ascites suspected"
        ],
        "station_type": OSCEType.PHYSICAL_EXAMINATION,
        "time_limit_minutes": 8,
        "difficulty": "intermediate",
        "is_published": True
    },
    {
        "osce_id": "OSCE-PSYCH-MSE-001",
        "station_title": "Mental State Examination",
        "specialty": MedicalSpecialty.PSYCHIATRY,
        "patient_instructions": """You are playing the role of a patient attending a psychiatric assessment.

**Your presentation:**
- You have been feeling low in mood for the past few weeks
- You are sleeping poorly and have reduced appetite
- You are able to engage in conversation
- You do not have suicidal thoughts

**During the examination:**
- Answer questions honestly
- Engage appropriately with the doctor
- Display slightly low mood but cooperative""",
        "candidate_instructions": """Perform a Mental State Examination on this patient.

**Task:**
- Assess all components of MSE
- Demonstrate appropriate communication
- Present findings systematically

**Time:** 8 minutes

**Note:** Focus on observation and systematic assessment.""",
        "examiner_instructions": """Observe the candidate performing an MSE.

**Assessment Criteria:**
1. **Systematic approach** (ASEPTIC framework)
2. **Appropriate questioning**
3. **Professional communication**
4. **Risk assessment**
5. **Clear presentation**

**Expected findings:** Low mood, otherwise normal MSE""",
        "rubric": {
            "criteria": [
                {"item": "Introduction and rapport building", "points": 2},
                {"item": "Appearance assessment", "points": 3},
                {"item": "Behavior observation", "points": 3},
                {"item": "Speech assessment", "points": 3},
                {"item": "Mood evaluation (subjective and objective)", "points": 4},
                {"item": "Thought form assessment", "points": 3},
                {"item": "Thought content (delusions, obsessions)", "points": 3},
                {"item": "Perception assessment (hallucinations)", "points": 3},
                {"item": "Cognition screening (orientation, memory, concentration)", "points": 4},
                {"item": "Insight assessment", "points": 3},
                {"item": "Risk assessment (suicide, self-harm, harm to others)", "points": 5},
                {"item": "Professional manner throughout", "points": 2},
                {"item": "Systematic presentation", "points": 4}
            ],
            "total_points": 42,
            "pass_mark": 29
        },
        "learning_objectives": [
            "Perform comprehensive Mental State Examination",
            "Assess psychiatric symptoms systematically",
            "Evaluate risk appropriately",
            "Present MSE findings clearly"
        ],
        "key_points": [
            "Use ASEPTIC mnemonic: Appearance, Speech, Emotion, Perception, Thought, Insight, Cognition",
            "Always assess risk (suicide, self-harm, harm to others)",
            "Distinguish subjective mood (what patient says) from objective mood (what you observe)",
            "Screen cognition systematically (orientation, memory, concentration)"
        ],
        "station_type": OSCEType.PHYSICAL_EXAMINATION,
        "time_limit_minutes": 8,
        "difficulty": "intermediate",
        "is_published": True
    }
]


def create_physical_exam_osces():
    """Create physical examination OSCE entries in database"""

    print("🏥 Physical Examination OSCE Import Script")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        created_count = 0
        skipped_count = 0

        for osce_data in PHYSICAL_EXAM_OSCES:
            # Check if OSCE already exists
            existing = db.query(OSCE).filter(
                OSCE.osce_id == osce_data["osce_id"]
            ).first()

            if existing:
                print(f"⏭️  Skipped: {osce_data['station_title']} (already exists)")
                skipped_count += 1
                continue

            # Create new OSCE
            osce = OSCE(**osce_data)
            db.add(osce)

            print(f"✅ Created: {osce_data['station_title']}")
            print(f"   - OSCE ID: {osce_data['osce_id']}")
            print(f"   - Specialty: {osce_data['specialty'].value}")
            print(f"   - Type: {osce_data['station_type'].value}")
            print()

            created_count += 1

        # Commit all changes
        db.commit()

        print("=" * 60)
        print(f"✅ Import Complete!")
        print(f"   - Created: {created_count} OSCEs")
        print(f"   - Skipped: {skipped_count} OSCEs (already existed)")
        print("=" * 60)

        # Verify
        print()
        print("📊 Verification - Physical Examination OSCEs in Database:")
        print()

        osces = db.query(OSCE).filter(
            OSCE.station_type == OSCEType.PHYSICAL_EXAMINATION
        ).all()

        for osce in osces:
            print(f"   {osce.osce_id}: {osce.station_title}")

        print()
        print(f"Total physical examination OSCEs: {len(osces)}")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_physical_exam_osces()
