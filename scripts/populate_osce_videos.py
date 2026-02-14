"""
Populate OSCE Video Resources from Master Video List

This script reads the video links from the markdown OSCE files and populates
the database with structured video resource data.

Usage:
    python scripts/populate_osce_videos.py

Requirements:
    - Database must be migrated to include video_resources column
    - Run: alembic upgrade head
"""

import sys
import os

# Add parent directory to path to import from backend
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from src.db.base import engine, Base
from src.db.models import OSCE, OSCEType, MedicalSpecialty

# Video resource data extracted from OSCE notes
OSCE_VIDEO_DATA = {
    # Medicine - Cardiovascular & Respiratory
    "OSCE-MED-001": {
        "station_title_match": "cardiovascular",
        "specialty": MedicalSpecialty.CARDIOLOGY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Cardiovascular Examination - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 10,
                    "focus": "Complete systematic cardiac examination with emphasis on auscultation techniques",
                    "why_recommended": "Gold standard demonstration from Stanford, excellent for murmur identification and dynamic maneuvers",
                    "australian_relevance": "Technique fully compatible with AMC Clinical exam requirements"
                },
                {
                    "title": "Cardiovascular Examination OSCE Guide - Geeky Medics",
                    "url": "https://geekymedics.com/cardiovascular-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "Step-by-step OSCE format with examiner communication",
                    "why_recommended": "Perfect for OSCE practice, includes common findings and presentation structure"
                },
                {
                    "title": "Respiratory Examination - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/lung.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 10,
                    "focus": "Complete respiratory examination including percussion and auscultation techniques",
                    "why_recommended": "Excellent demonstration of proper percussion technique and breath sound interpretation",
                    "australian_relevance": "Systematic approach matches Australian teaching hospital standards"
                },
                {
                    "title": "Respiratory Examination OSCE Guide - Geeky Medics",
                    "url": "https://geekymedics.com/respiratory-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "OSCE-formatted examination with clear communication and presentation",
                    "why_recommended": "Ideal for practicing the 5 Ps framework and OSCE timing"
                }
            ],
            "supplementary_videos": []
        }
    },

    # Medicine - Abdominal & Neurological
    "OSCE-MED-002": {
        "station_title_match": "abdominal",
        "specialty": MedicalSpecialty.GASTROENTEROLOGY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Abdominal Examination - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/abdominal.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 10,
                    "focus": "Complete systematic 9-region abdominal examination with organ-specific techniques",
                    "why_recommended": "Excellent demonstration of liver, spleen, kidney palpation and ascites assessment",
                    "australian_relevance": "Systematic approach aligns with AMC Clinical exam standards"
                },
                {
                    "title": "Abdominal Examination OSCE Guide - Geeky Medics",
                    "url": "https://geekymedics.com/abdominal-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "OSCE-formatted examination with communication and presentation",
                    "why_recommended": "Perfect for practicing the 9-region systematic approach and special tests"
                },
                {
                    "title": "Cranial Nerve Examination - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/cranial.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 12,
                    "focus": "Complete CN I-XII systematic examination",
                    "why_recommended": "Gold standard for cranial nerve testing, excellent for learning proper technique",
                    "australian_relevance": "Technique matches Australian teaching hospital protocols"
                }
            ],
            "supplementary_videos": []
        }
    },

    # Surgery - Acute Abdomen
    "OSCE-SURG-001": {
        "station_title_match": "acute abdomen",
        "specialty": MedicalSpecialty.SURGERY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Abdominal Examination - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/abdominal.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 10,
                    "focus": "Complete abdominal examination including special tests for peritonism",
                    "why_recommended": "Excellent demonstration of systematic palpation and special maneuvers",
                    "australian_relevance": "Technique aligns with AMC Clinical exam surgical station requirements"
                },
                {
                    "title": "Acute Abdominal Examination - Geeky Medics",
                    "url": "https://geekymedics.com/abdominal-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "9-region examination with rebound tenderness, guarding, and special tests",
                    "why_recommended": "Perfect for OSCE practice with systematic approach to acute abdomen"
                }
            ],
            "supplementary_videos": []
        }
    },

    # Surgery - Lumps and Hernias
    "OSCE-SURG-002": {
        "station_title_match": "lump",
        "specialty": MedicalSpecialty.SURGERY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Examination of Lumps - Stanford Medicine 25",
                    "url": "https://stanfordmedicine25.stanford.edu/the25/lumps.html",
                    "source": "Stanford Medicine 25",
                    "duration_minutes": 8,
                    "focus": "7 Ss framework for systematic lump examination",
                    "why_recommended": "Gold standard demonstration of special tests (transillumination, lymph node examination)",
                    "australian_relevance": "Systematic approach matches AMC Clinical exam surgical station requirements"
                },
                {
                    "title": "Hernia Examination - Geeky Medics",
                    "url": "https://geekymedics.com/groin-lump-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "Distinguishing inguinal vs femoral hernias, cough impulse test, reducibility assessment",
                    "why_recommended": "Perfect for OSCE practice with clear demonstration of special tests"
                }
            ],
            "supplementary_videos": []
        }
    },

    # ObGyn - Obstetric Examination
    "OSCE-OBGYN-001": {
        "station_title_match": "obstetric",
        "specialty": MedicalSpecialty.OBSTETRICS_GYNAECOLOGY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Obstetric Examination (Antenatal) - Geeky Medics",
                    "url": "https://geekymedics.com/obstetric-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 10,
                    "focus": "Complete antenatal examination including Leopold's manoeuvres and SFH measurement",
                    "why_recommended": "Excellent OSCE-formatted demonstration with clear communication and systematic approach",
                    "australian_relevance": "Follows Australian antenatal care protocols"
                }
            ],
            "supplementary_videos": []
        }
    },

    # Paediatrics - Physical Examination
    "OSCE-PAED-001": {
        "station_title_match": "paediatric",
        "specialty": MedicalSpecialty.PAEDIATRICS,
        "videos": {
            "essential_videos": [
                {
                    "title": "Newborn Examination - Geeky Medics",
                    "url": "https://geekymedics.com/newborn-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 12,
                    "focus": "Complete newborn examination including hips (Ortolani/Barlow), heart, reflexes",
                    "why_recommended": "Excellent step-by-step demonstration of baby check - most common paediatric OSCE station",
                    "australian_relevance": "Follows Australian newborn screening protocols"
                },
                {
                    "title": "Paediatric Respiratory Examination - Geeky Medics",
                    "url": "https://geekymedics.com/paediatric-respiratory-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 8,
                    "focus": "Examining uncooperative child, distraction techniques, opportunistic examination",
                    "why_recommended": "Perfect for learning age-appropriate examination techniques"
                }
            ],
            "supplementary_videos": []
        }
    },

    # Psychiatry - Mental State Examination
    "OSCE-PSYCH-001": {
        "station_title_match": "mental state",
        "specialty": MedicalSpecialty.PSYCHIATRY,
        "videos": {
            "essential_videos": [
                {
                    "title": "Mental State Examination - Geeky Medics",
                    "url": "https://geekymedics.com/mental-state-examination/",
                    "source": "Geeky Medics",
                    "duration_minutes": 10,
                    "focus": "Complete systematic MSE assessment across all domains",
                    "why_recommended": "Excellent OSCE-formatted demonstration with clear structure and documentation",
                    "australian_relevance": "Follows Australian psychiatric assessment standards"
                },
                {
                    "title": "Cognitive Assessment (MMSE/MoCA) - Geeky Medics",
                    "url": "https://geekymedics.com/mini-mental-state-examination-mmse/",
                    "source": "Geeky Medics",
                    "duration_minutes": 10,
                    "focus": "Systematic cognitive function testing",
                    "why_recommended": "Essential for assessing cognitive impairment in MSE"
                }
            ],
            "supplementary_videos": []
        }
    }
}


def populate_videos():
    """Populate video resources for OSCEs"""

    print("🎬 OSCE Video Resource Population Script")
    print("=" * 60)

    # Create database session
    with Session(engine) as session:
        try:
            # Get all physical examination OSCEs
            osces = session.query(OSCE).filter(
                OSCE.station_type == OSCEType.PHYSICAL_EXAMINATION
            ).all()

            print(f"\n📊 Found {len(osces)} physical examination OSCE stations")

            updated_count = 0
            skipped_count = 0

            for osce in osces:
                # Try to match OSCE with video data
                matched = False

                for osce_id, data in OSCE_VIDEO_DATA.items():
                    title_match = data["station_title_match"]

                    if title_match.lower() in osce.station_title.lower():
                        # Update video resources
                        osce.video_resources = data["videos"]
                        updated_count += 1
                        matched = True

                        print(f"✅ Updated: {osce.station_title}")
                        print(f"   - Essential videos: {len(data['videos']['essential_videos'])}")
                        print(f"   - Supplementary videos: {len(data['videos']['supplementary_videos'])}")
                        break

                if not matched:
                    skipped_count += 1
                    print(f"⏭️  Skipped: {osce.station_title} (no video data available)")

            # Commit changes
            session.commit()

            print("\n" + "=" * 60)
            print(f"✅ Success! Updated {updated_count} OSCEs with video resources")
            print(f"⏭️  Skipped {skipped_count} OSCEs (no matching video data)")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            session.rollback()
            raise


if __name__ == "__main__":
    print("\n⚠️  Make sure you've run the database migration first:")
    print("   cd backend && alembic upgrade head\n")

    response = input("Continue with video population? (y/n): ")

    if response.lower() == 'y':
        populate_videos()
    else:
        print("Cancelled.")
