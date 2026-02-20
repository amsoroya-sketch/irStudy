# Epic EHR Practice System - Integration Strategy

**Document Version**: 1.0
**Date**: 2026-02-15
**Status**: Ready for Implementation

---

## Executive Summary

This document specifies the **integration strategy** for converting 221 existing OSCE scenarios into high-fidelity EMR patient cases, and integrating the Epic EHR Practice System with the existing MCQ/OSCE/video content ecosystem.

**Key Integration Points**:
1. OSCE → EMR patient case conversion (221 scenarios → 500+ EMR cases)
2. MCQ medication content → PBS prescription validation
3. Educational videos → EMR case learning resources
4. Unified progress tracking (MCQ + OSCE + EMR dashboard)

---

## 1. OSCE → EMR Patient Case Conversion

### 1.1 Overview

**Current State**:
- 221 OSCE scenarios in database
  - 167 history-taking stations
  - 10 physical examination stations
  - 44 emergency medicine stations
- Each OSCE has:
  - `patient_instructions` (simulated patient details)
  - `candidate_instructions` (task for medical student)
  - `rubric` (AMC 15-mark criteria)
  - `specialty`, `difficulty`, `time_limit_minutes`
  - `video_resources`, `australian_guidelines`

**Target State**:
- 500+ mock_patients entries (each OSCE can generate 1-3 variations)
- Complete patient demographics (MRN, Medicare number, address, GP details)
- Realistic vital signs, investigation results, medications
- Validation criteria extracted from rubric

### 1.2 Conversion Algorithm

**High-Level Workflow**:

```
OSCE Scenario (221 in DB)
        ↓
Parse patient_instructions (NLP extraction)
        ↓
Extract: name, age, gender, presenting complaint, PMHx, medications, allergies
        ↓
Generate: MRN, Medicare number, full demographics, GP details
        ↓
Generate: Realistic vital signs (based on specialty + severity)
        ↓
Generate: Investigation results (labs, ECG, imaging)
        ↓
Map rubric → validation_criteria (JSON)
        ↓
MockPatient entry created
        ↓
Link: source_osce_id (bidirectional reference)
```

### 1.3 Parser Implementation

**Script**: `backend/scripts/convert_osce_to_emr.py`

```python
import re
import json
from typing import Dict, Optional, List
from uuid import uuid4

class OSCEToEMRConverter:
    """
    Convert OSCE scenarios to EMR patient cases.

    Extracts patient data from unstructured text (patient_instructions)
    and generates realistic clinical data for EMR practice.
    """

    def __init__(self):
        self.australian_name_generator = AustralianNameGenerator()
        self.address_generator = AustralianAddressGenerator()

    def convert(self, osce: OSCE) -> MockPatient:
        """Main conversion method."""

        # 1. Parse patient_instructions
        patient_data = self.parse_patient_instructions(osce.patient_instructions)

        # 2. Generate demographics
        demographics = self.generate_demographics(patient_data)

        # 3. Generate clinical data
        vital_signs = self.generate_vital_signs(osce.specialty, patient_data)
        investigation_results = self.generate_investigations(osce.specialty, patient_data)

        # 4. Extract validation criteria from rubric
        validation_criteria = self.extract_validation_criteria(osce)

        # 5. Create MockPatient
        mock_patient = MockPatient(
            mrn=self.generate_mrn(),
            medicare_number=self.generate_medicare_number(),
            name=patient_data.get("name") or self.australian_name_generator.generate(),
            age=patient_data.get("age"),
            gender=patient_data.get("gender"),
            aboriginal_tsi_status=demographics.get("aboriginal_tsi_status", "Prefer not to say"),
            demographics=demographics,
            presenting_complaint=patient_data.get("presenting_complaint"),
            medical_history=patient_data.get("medical_history"),
            medications=patient_data.get("medications"),
            allergies=patient_data.get("allergies", ["NKDA"]),
            vital_signs=vital_signs,
            physical_exam_findings=patient_data.get("physical_exam_findings"),
            investigation_results=investigation_results,
            source_osce_id=osce.id,
            specialty=osce.specialty,
            difficulty=osce.difficulty,
            validation_criteria=validation_criteria
        )

        return mock_patient

    def parse_patient_instructions(self, text: str) -> Dict:
        """
        Parse unstructured patient_instructions text.

        Example input:
        "You are John Smith, 58-year-old male, presenting to ED with central
        chest pain for 2 hours. Pain 7/10, crushing, radiating to left arm.
        Sweating, nauseous. PMHx: Hypertension (on amlodipine 5mg), T2DM (on
        metformin 500mg BD). Smoker 30 pack-years. Allergies: Penicillin (rash)"

        Returns:
        {
            "name": "John Smith",
            "age": 58,
            "gender": "male",
            "presenting_complaint": "Central chest pain",
            "medical_history": {
                "pmhx": ["Hypertension", "Type 2 Diabetes"],
                "shx": {"smoking": "30 pack-years"}
            },
            "medications": [
                {"name": "Amlodipine", "dose": "5mg", "frequency": "daily"},
                {"name": "Metformin", "dose": "500mg", "frequency": "BD"}
            ],
            "allergies": [{"allergen": "Penicillin", "reaction": "Rash"}]
        }
        """

        data = {}

        # Extract name (pattern: "You are [Name]")
        name_match = re.search(r"You are ([A-Z][a-z]+ [A-Z][a-z]+)", text)
        if name_match:
            data["name"] = name_match.group(1)

        # Extract age and gender (pattern: "58-year-old male" or "58M")
        age_gender_match = re.search(r"(\d+)[-\s]?(?:year-old|yo|y\.?o\.?)\s+(male|female|M|F)", text, re.IGNORECASE)
        if age_gender_match:
            data["age"] = int(age_gender_match.group(1))
            gender = age_gender_match.group(2).lower()
            data["gender"] = "male" if gender in ["male", "m"] else "female"

        # Extract presenting complaint (pattern: "presenting with [complaint]")
        complaint_match = re.search(r"presenting (?:to \w+ )?with (.+?)(?:\.|for \d+ hours?|for \d+ days?)", text, re.IGNORECASE)
        if complaint_match:
            data["presenting_complaint"] = complaint_match.group(1).strip()

        # Extract PMHx (Past Medical History)
        pmhx_match = re.search(r"PMHx:\s*(.+?)(?:Medications:|Allergies:|FHx:|SHx:|$)", text, re.IGNORECASE | re.DOTALL)
        if pmhx_match:
            pmhx_text = pmhx_match.group(1)
            # Split by commas or periods
            pmhx_items = [item.strip() for item in re.split(r",|\.", pmhx_text) if item.strip()]
            # Remove medication details in parentheses for PMHx list
            pmhx_clean = [re.sub(r"\s*\(.*?\)", "", item) for item in pmhx_items if item]
            data["medical_history"] = {"pmhx": pmhx_clean}

        # Extract medications (pattern: "on amlodipine 5mg daily")
        medications = []
        med_pattern = r"(\w+)\s+(\d+(?:\.\d+)?)\s*(mg|g|mcg|mL|units)\s+(daily|BD|TDS|QID|PRN|weekly)"
        for match in re.finditer(med_pattern, text, re.IGNORECASE):
            medications.append({
                "name": match.group(1).capitalize(),
                "dose": f"{match.group(2)}{match.group(3)}",
                "frequency": match.group(4),
                "route": "PO"  # Assume oral unless specified
            })
        if medications:
            data["medications"] = medications

        # Extract allergies (pattern: "Allergies: Penicillin (rash)")
        allergies_match = re.search(r"Allergies?:\s*(.+?)(?:\.|$)", text, re.IGNORECASE)
        if allergies_match:
            allergies_text = allergies_match.group(1)
            if "nil" in allergies_text.lower() or "nkda" in allergies_text.lower():
                data["allergies"] = ["NKDA"]
            else:
                # Parse "Penicillin (rash)"
                allergy_pattern = r"([A-Z][a-z]+)\s*\(([^)]+)\)"
                allergies = []
                for match in re.finditer(allergy_pattern, allergies_text):
                    allergies.append({
                        "allergen": match.group(1),
                        "reaction": match.group(2),
                        "severity": "mild"  # Default
                    })
                if allergies:
                    data["allergies"] = allergies

        # Extract smoking history
        smoking_match = re.search(r"(?:Smoker|smoking)\s+(\d+)\s+pack[-\s]?years?", text, re.IGNORECASE)
        if smoking_match:
            if "medical_history" not in data:
                data["medical_history"] = {}
            data["medical_history"]["shx"] = {"smoking": f"{smoking_match.group(1)} pack-years"}

        return data

    def generate_mrn(self) -> str:
        """Generate realistic Medical Record Number (8 digits)."""
        import random
        return f"MRN{random.randint(10000000, 99999999)}"

    def generate_medicare_number(self) -> str:
        """
        Generate realistic Australian Medicare number.
        Format: 2912 34567 1 (10 digits + 1 check digit)
        First digit: 2-6 (card color)
        """
        import random
        first_digit = random.choice([2, 3, 4, 5, 6])
        next_8_digits = random.randint(10000000, 99999999)
        check_digit = random.randint(1, 9)
        number = f"{first_digit}{next_8_digits}"
        return f"{number[:4]} {number[4:9]} {check_digit}"

    def generate_demographics(self, patient_data: Dict) -> Dict:
        """Generate full patient demographics."""

        return {
            "address": self.address_generator.generate_sydney_address(),
            "phone": self.generate_australian_phone(),
            "email": f"{patient_data.get('name', 'patient').lower().replace(' ', '.')}@example.com",
            "emergency_contact": {
                "name": self.australian_name_generator.generate(),
                "relationship": random.choice(["Spouse", "Partner", "Parent", "Sibling", "Child"]),
                "phone": self.generate_australian_phone()
            },
            "gp_details": {
                "name": f"Dr. {self.australian_name_generator.generate()}",
                "clinic": f"{random.choice(['Sydney', 'Parramatta', 'Liverpool', 'Bankstown'])} Medical Centre",
                "phone": self.generate_landline()
            },
            "preferred_language": "English",
            "interpreter_required": False,
            "aboriginal_tsi_status": random.choice([
                "Neither Aboriginal nor Torres Strait Islander",
                "Aboriginal",
                "Torres Strait Islander",
                "Prefer not to say"
            ])
        }

    def generate_australian_phone(self) -> str:
        """Generate Australian mobile number (04XX XXX XXX)."""
        import random
        return f"04{random.randint(10, 99)} {random.randint(100, 999)} {random.randint(100, 999)}"

    def generate_landline(self) -> str:
        """Generate Sydney landline ((02) XXXX XXXX)."""
        import random
        return f"(02) {random.randint(8000, 9999)} {random.randint(1000, 9999)}"

    def generate_vital_signs(self, specialty: str, patient_data: Dict) -> Dict:
        """
        Generate realistic vital signs based on clinical scenario.

        For cardiology (chest pain): Elevated HR/BP
        For respiratory (dyspnea): Low SpO2, high RR
        For neurology (stroke): Variable vitals
        """

        import random

        # Base vitals (normal adult)
        vitals = {
            "hr": 75,
            "bp_systolic": 120,
            "bp_diastolic": 80,
            "rr": 16,
            "spo2": 98,
            "temp": 36.6,
            "pain_score": 0
        }

        # Adjust based on specialty
        if specialty == "cardiology":
            # Chest pain: tachycardia, hypertension
            vitals["hr"] = random.randint(85, 110)
            vitals["bp_systolic"] = random.randint(140, 170)
            vitals["bp_diastolic"] = random.randint(85, 100)
            vitals["pain_score"] = random.randint(5, 9)

        elif specialty == "respiratory":
            # Dyspnea: tachypnea, hypoxia
            vitals["rr"] = random.randint(22, 32)
            vitals["spo2"] = random.randint(88, 94)
            vitals["hr"] = random.randint(90, 115)

        elif specialty == "infectious_diseases":
            # Sepsis: fever, tachycardia, hypotension
            vitals["temp"] = round(random.uniform(38.0, 39.5), 1)
            vitals["hr"] = random.randint(100, 125)
            vitals["bp_systolic"] = random.randint(90, 110)
            vitals["bp_diastolic"] = random.randint(55, 70)

        elif specialty == "neurology":
            # Stroke: variable vitals
            vitals["bp_systolic"] = random.randint(150, 190)
            vitals["bp_diastolic"] = random.randint(90, 110)

        # Add weight, height, BMI (Australian adults)
        vitals["weight"] = random.randint(60, 100)  # kg
        vitals["height"] = random.randint(155, 190)  # cm
        vitals["bmi"] = round(vitals["weight"] / (vitals["height"] / 100) ** 2, 1)
        vitals["gcs"] = 15  # Default Glasgow Coma Scale

        return vitals

    def generate_investigations(self, specialty: str, patient_data: Dict) -> Dict:
        """
        Generate realistic investigation results based on clinical scenario.

        For cardiology (ACS): Troponin elevated, ECG ST changes
        For respiratory (pneumonia): CXR consolidation, elevated WCC
        For endocrinology (DKA): High BSL, acidosis
        """

        import random

        results = {}

        if specialty == "cardiology":
            # Acute Coronary Syndrome
            results["ecg"] = {
                "findings": random.choice([
                    "ST elevation 2mm in leads II, III, aVF (inferior STEMI)",
                    "ST depression V4-V6, T wave inversion (lateral ischaemia)",
                    "Normal sinus rhythm, no acute changes"
                ]),
                "interpretation": "STEMI" if "elevation" in results.get("ecg", {}).get("findings", "") else "No acute changes"
            }

            results["labs"] = {
                "troponin_i": {
                    "value": round(random.uniform(0.8, 2.5), 2) if "STEMI" in results["ecg"]["interpretation"] else 0.02,
                    "unit": "ng/mL",
                    "reference": "<0.04",
                    "flag": "HIGH" if results["ecg"]["interpretation"] == "STEMI" else "NORMAL"
                },
                "fbc": {
                    "hb": {"value": random.randint(130, 160), "unit": "g/L", "reference": "130-180"},
                    "wcc": {"value": round(random.uniform(7, 12), 1), "unit": "x10^9/L", "reference": "4-11"},
                    "platelets": {"value": random.randint(200, 350), "unit": "x10^9/L", "reference": "150-400"}
                },
                "uec": {
                    "sodium": {"value": random.randint(136, 142), "unit": "mmol/L", "reference": "135-145"},
                    "potassium": {"value": round(random.uniform(3.8, 4.8), 1), "unit": "mmol/L", "reference": "3.5-5.0"},
                    "creatinine": {"value": random.randint(70, 110), "unit": "µmol/L", "reference": "60-110"}
                }
            }

        elif specialty == "respiratory":
            # Pneumonia
            results["cxr"] = {
                "findings": random.choice([
                    "Right lower lobe consolidation",
                    "Left lower lobe opacity with air bronchograms",
                    "Bilateral interstitial infiltrates"
                ]),
                "interpretation": "Community-acquired pneumonia"
            }

            results["labs"] = {
                "fbc": {
                    "hb": {"value": random.randint(120, 150), "unit": "g/L", "reference": "130-180"},
                    "wcc": {"value": round(random.uniform(12, 18), 1), "unit": "x10^9/L", "reference": "4-11", "flag": "HIGH"},
                    "neutrophils": {"value": round(random.uniform(8, 14), 1), "unit": "x10^9/L", "reference": "2-7", "flag": "HIGH"}
                },
                "crp": {
                    "value": random.randint(80, 200),
                    "unit": "mg/L",
                    "reference": "<5",
                    "flag": "HIGH"
                }
            }

        elif specialty == "endocrinology":
            # Diabetic Ketoacidosis
            results["labs"] = {
                "bsl": {
                    "value": round(random.uniform(18, 28), 1),
                    "unit": "mmol/L",
                    "reference": "4-7",
                    "flag": "CRITICALLY HIGH"
                },
                "venous_blood_gas": {
                    "ph": {"value": round(random.uniform(7.15, 7.28), 2), "reference": "7.35-7.45", "flag": "LOW"},
                    "hco3": {"value": random.randint(8, 14), "unit": "mmol/L", "reference": "22-28", "flag": "LOW"},
                    "lactate": {"value": round(random.uniform(1.5, 3.5), 1), "unit": "mmol/L", "reference": "<2"}
                },
                "ketones": {
                    "value": round(random.uniform(3.5, 6.0), 1),
                    "unit": "mmol/L",
                    "reference": "<0.6",
                    "flag": "HIGH"
                }
            }

        # Default: Basic labs for all cases
        if "labs" not in results:
            results["labs"] = {
                "fbc": {
                    "hb": {"value": random.randint(130, 160), "unit": "g/L", "reference": "130-180"},
                    "wcc": {"value": round(random.uniform(6, 10), 1), "unit": "x10^9/L", "reference": "4-11"}
                }
            }

        return results

    def extract_validation_criteria(self, osce: OSCE) -> Dict:
        """
        Convert OSCE rubric to EMR validation criteria.

        OSCE rubric (AMC 15-mark format):
        {
            "history_examination": {
                "marks": 3,
                "criteria": "Systematic SOCRATES approach to pain assessment"
            },
            "clinical_reasoning": {
                "marks": 3,
                "criteria": "Appropriate differential diagnosis (ACS, PE, gastritis)"
            },
            ...
        }

        EMR validation_criteria:
        {
            "expected_diagnosis": ["Acute Coronary Syndrome", "STEMI"],
            "key_history_points": ["SOCRATES pain assessment", "Cardiovascular risk factors"],
            "expected_investigations": ["ECG", "Troponin", "FBC"],
            "expected_management": ["Call 000", "Aspirin 300mg STAT", ...],
            "red_flags": ["STEMI criteria - activate cath lab"]
        }
        """

        rubric = osce.rubric
        specialty = osce.specialty

        # Base criteria from rubric
        criteria = {
            "expected_diagnosis": [],
            "key_history_points": [],
            "expected_investigations": [],
            "expected_management": [],
            "red_flags": []
        }

        # Extract from rubric criteria text
        if "history_examination" in rubric:
            history_text = rubric["history_examination"].get("criteria", "")
            # Extract key phrases (e.g., "SOCRATES approach")
            if "SOCRATES" in history_text:
                criteria["key_history_points"].append("SOCRATES pain assessment")
            if "systematic" in history_text.lower():
                criteria["key_history_points"].append("Systematic history taking")

        if "clinical_reasoning" in rubric:
            reasoning_text = rubric["clinical_reasoning"].get("criteria", "")
            # Extract differential diagnosis mentions
            if "differential" in reasoning_text.lower():
                # Parse "(ACS, PE, gastritis)"
                diff_match = re.search(r"\(([^)]+)\)", reasoning_text)
                if diff_match:
                    diagnoses = [d.strip() for d in diff_match.group(1).split(",")]
                    criteria["expected_diagnosis"].extend(diagnoses)

        # Specialty-specific defaults
        if specialty == "cardiology":
            criteria["expected_investigations"].extend(["ECG", "Troponin", "FBC", "UEC", "Lipid panel"])
            criteria["expected_management"].extend([
                "Call 000 if STEMI criteria",
                "Aspirin 300mg STAT",
                "Clopidogrel 300mg STAT",
                "Morphine for pain relief",
                "Urgent cardiology consult"
            ])
            criteria["red_flags"].append("STEMI criteria met - activate cath lab urgently")

        elif specialty == "respiratory":
            criteria["expected_investigations"].extend(["CXR", "FBC", "CRP", "Sputum culture"])
            criteria["expected_management"].extend([
                "Antibiotics (amoxicillin/clavulanate 875/125mg BD)",
                "Analgesia (paracetamol 1g QID)",
                "Safety netting - return if worsening dyspnea"
            ])

        elif specialty == "endocrinology":
            criteria["expected_investigations"].extend(["BSL", "Ketones", "VBG", "UEC"])
            criteria["expected_management"].extend([
                "IV fluids (normal saline 1L over 1h)",
                "IV insulin infusion",
                "Potassium replacement",
                "Hourly BSL monitoring"
            ])
            criteria["red_flags"].append("DKA - requires ICU admission")

        return criteria


# Helper classes

class AustralianNameGenerator:
    """Generate realistic Australian names."""

    FIRST_NAMES_MALE = [
        "William", "Oliver", "Jack", "Noah", "Thomas", "James", "Lucas", "Henry",
        "Alexander", "Ethan", "Mason", "Liam", "Charlie", "Leo", "Oscar"
    ]

    FIRST_NAMES_FEMALE = [
        "Charlotte", "Olivia", "Amelia", "Isla", "Mia", "Ava", "Grace", "Ella",
        "Sophia", "Chloe", "Emily", "Zoe", "Harper", "Ruby", "Lily"
    ]

    SURNAMES = [
        "Smith", "Jones", "Williams", "Brown", "Wilson", "Taylor", "Johnson",
        "White", "Martin", "Anderson", "Thompson", "Nguyen", "Thomas", "Walker",
        "Harris", "Lee", "Ryan", "Robinson", "Clark", "Patel", "Singh"
    ]

    def generate(self, gender: str = None) -> str:
        import random
        if gender == "male":
            first = random.choice(self.FIRST_NAMES_MALE)
        elif gender == "female":
            first = random.choice(self.FIRST_NAMES_FEMALE)
        else:
            first = random.choice(self.FIRST_NAMES_MALE + self.FIRST_NAMES_FEMALE)

        surname = random.choice(self.SURNAMES)
        return f"{first} {surname}"


class AustralianAddressGenerator:
    """Generate realistic Sydney addresses."""

    STREET_NAMES = [
        "George Street", "Pitt Street", "King Street", "Market Street",
        "Elizabeth Street", "York Street", "Sussex Street", "Kent Street",
        "Liverpool Road", "Parramatta Road", "Victoria Road"
    ]

    SUBURBS = [
        ("Sydney", "2000"), ("Parramatta", "2150"), ("Liverpool", "2170"),
        ("Bankstown", "2200"), ("Chatswood", "2067"), ("Bondi", "2026"),
        ("Manly", "2095"), ("Penrith", "2750")
    ]

    def generate_sydney_address(self) -> str:
        import random
        street_number = random.randint(1, 200)
        street_name = random.choice(self.STREET_NAMES)
        suburb, postcode = random.choice(self.SUBURBS)
        return f"{street_number} {street_name}, {suburb} NSW {postcode}"
```

### 1.4 Batch Conversion Script

**Usage**:
```bash
cd /home/dev/Development/irStudy/backend
source venv/bin/activate
python scripts/convert_osce_to_emr.py --priority-specialties cardiology,respiratory,emergency_medicine --limit 50
```

**Script**: `backend/scripts/convert_osce_to_emr.py` (main)

```python
"""
Batch convert OSCE scenarios to EMR patient cases.

Usage:
    python scripts/convert_osce_to_emr.py --all                    # Convert all 221 OSCEs
    python scripts/convert_osce_to_emr.py --limit 50               # Convert first 50
    python scripts/convert_osce_to_emr.py --specialty cardiology   # Convert cardiology only
    python scripts/convert_osce_to_emr.py --priority-specialties cardiology,respiratory,emergency_medicine --limit 50
"""

import asyncio
import argparse
from sqlalchemy.orm import Session

from src.db.database import SessionLocal
from src.db.models import OSCE, MockPatient
from scripts.osce_emr_converter import OSCEToEMRConverter

async def main(args):
    db: Session = SessionLocal()
    converter = OSCEToEMRConverter()

    try:
        # Query OSCEs based on filters
        query = db.query(OSCE).filter(OSCE.deleted_at.is_(None))

        if args.specialty:
            query = query.filter(OSCE.specialty == args.specialty)

        if args.priority_specialties:
            specialties = args.priority_specialties.split(",")
            query = query.filter(OSCE.specialty.in_(specialties))

        if args.limit:
            query = query.limit(args.limit)

        osces = query.all()

        print(f"Found {len(osces)} OSCEs to convert")

        # Convert each OSCE
        created_count = 0
        for osce in osces:
            print(f"Converting OSCE-{osce.id}: {osce.station_title}")

            # Check if already converted
            existing = db.query(MockPatient).filter(
                MockPatient.source_osce_id == osce.id
            ).first()

            if existing:
                print(f"  ⚠️  Already converted (MockPatient ID: {existing.id}), skipping")
                continue

            # Convert
            try:
                mock_patient = converter.convert(osce)
                db.add(mock_patient)
                db.commit()
                db.refresh(mock_patient)

                print(f"  ✅ Created MockPatient: {mock_patient.name} (MRN: {mock_patient.mrn})")
                print(f"     Specialty: {mock_patient.specialty}, Difficulty: {mock_patient.difficulty}")
                print(f"     Presenting complaint: {mock_patient.presenting_complaint}")
                created_count += 1

            except Exception as e:
                print(f"  ❌ Error converting OSCE-{osce.id}: {e}")
                db.rollback()

        print(f"\n✅ Conversion complete: {created_count}/{len(osces)} patients created")

    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert OSCE scenarios to EMR patient cases")
    parser.add_argument("--all", action="store_true", help="Convert all OSCEs")
    parser.add_argument("--limit", type=int, help="Limit number of conversions")
    parser.add_argument("--specialty", type=str, help="Convert specific specialty only")
    parser.add_argument("--priority-specialties", type=str, help="Comma-separated list of priority specialties")

    args = parser.parse_args()

    asyncio.run(main(args))
```

### 1.5 MVP Conversion Plan

**Phase 1: 50 Priority Patients** (Week 2)

| Specialty | OSCEs Available | Target EMR Cases |
|-----------|-----------------|------------------|
| Cardiology | 25 | 20 |
| Respiratory | 20 | 15 |
| Emergency Medicine | 44 | 15 |
| **Total** | **89** | **50** |

**Command**:
```bash
python scripts/convert_osce_to_emr.py \
  --priority-specialties cardiology,respiratory,emergency_medicine \
  --limit 50
```

**Phase 2: Full Conversion** (Post-MVP)

- Convert all 221 OSCEs → 221+ patients
- Generate variations (mild/moderate/severe presentations) → 500+ patients

---

## 2. MCQ Integration Strategy

### 2.1 Medication Content → PBS Validation

**Current State**:
- 1,208 MCQs in database
- Many MCQs about medication management (e.g., hypertension first-line, antibiotic selection)
- 594 MCQs have RAG citations (eTG, AMH, PBS references)

**Integration Opportunity**:

**Example MCQ**:
```
Question: "A 58-year-old man with newly diagnosed hypertension (BP 155/92).
No diabetes, normal renal function. What is the most appropriate first-line agent?"

Options:
A. Amlodipine 5mg daily
B. Atenolol 50mg daily
C. Hydrochlorothiazide 12.5mg daily
D. Ramipril 2.5mg daily

Answer: D (Ramipril - eTG first-line for hypertension without compelling indication)
```

**EMR Integration**:

1. **PBS Search Pre-population**:
   - When student practices EMR case with hypertension
   - PBS medication search shows "ramipril" as top suggestion
   - Tooltip: "eTG first-line for hypertension (see MCQ #789 for rationale)"

2. **Prescription Validation Cross-Reference**:
   - Student prescribes amlodipine (valid but not eTG first-line)
   - Layer 2 validation (Python) flags: "Consider ACE inhibitor as eTG first-line (see MCQ #789)"
   - Link to MCQ for learning reinforcement

3. **Related Content Recommendations**:
   - After EMR session, suggest: "Practice 5 related MCQs on hypertension management"

### 2.2 Implementation

**Database Query**:
```python
# backend/src/services/mcq_emr_linker.py

async def find_related_mcqs(emr_session: EMRSession) -> List[MCQ]:
    """
    Find MCQs related to EMR session based on:
    - Specialty match
    - Medication mentions in SOAP plan
    - Diagnosis keywords
    """

    # Extract medications from SOAP plan
    medications = extract_medications_from_soap(emr_session.soap_note.plan)

    # Query MCQs with matching tags
    related_mcqs = db.query(MCQ).filter(
        MCQ.specialty == emr_session.specialty,
        MCQ.tags.contains(medications)  # JSON array contains
    ).limit(5).all()

    return related_mcqs
```

**Frontend Display** (after EMR submission):
```typescript
// frontend/src/components/emr/EMRValidationPanel.tsx

<Box sx={{ mt: 3 }}>
  <Typography variant="h6">📚 Related Learning Resources</Typography>

  <Stack spacing={2}>
    {relatedMCQs.map(mcq => (
      <Card key={mcq.id}>
        <CardContent>
          <Typography variant="subtitle1">
            MCQ #{mcq.id}: {mcq.question_text.substring(0, 100)}...
          </Typography>
          <Button onClick={() => navigate(`/mcq-practice/${mcq.id}`)}>
            Practice This MCQ
          </Button>
        </CardContent>
      </Card>
    ))}
  </Stack>
</Box>
```

---

## 3. Educational Video Integration

### 3.1 Current Video Resources

**OSCE Video Structure** (4 OSCEs have video_resources):

```json
{
  "essential_videos": [
    {
      "title": "Cardiovascular Examination - Stanford Medicine 25",
      "url": "https://www.youtube.com/watch?v=...",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      "focus": "Complete systematic cardiac examination",
      "why_recommended": "Gold standard demonstration of cardiovascular exam technique",
      "australian_relevance": "AMC Clinical Exam aligned approach"
    }
  ],
  "supplementary_videos": [...]
}
```

### 3.2 EMR Integration Strategy

**Scenario**: Student practicing EMR case "58M with chest pain"

**Video Display Timing**:

1. **Pre-Session** (Patient Case Selection):
   ```
   📹 Recommended Video (5 min):
   "ECG Interpretation for STEMI" - Sydney Medical School
   Watch before starting this case for better ECG interpretation
   ```

2. **During Session** (Contextual Help):
   - Student clicks "Physical Exam Findings" → Video icon appears
   - Tooltip: "Watch video: Cardiovascular Examination Technique"
   - Modal popup with embedded video

3. **Post-Session** (Validation Feedback):
   ```
   💡 Areas for Improvement:
   - Your assessment missed ECG STEMI criteria
   📹 Watch: "ECG Changes in Acute MI" (8 min) - improves clinical reasoning
   ```

### 3.3 Implementation

**Link Videos to MockPatients**:

```python
# During OSCE → EMR conversion
mock_patient.video_resources = osce.video_resources  # Direct copy

# OR generate specialty-specific videos
if mock_patient.specialty == "cardiology":
    mock_patient.video_resources = {
        "essential_videos": [
            {
                "title": "Acute Coronary Syndrome Management",
                "url": "https://...",
                "source": "Australian Resuscitation Council",
                "why_recommended": "STEMI management as per Australian guidelines"
            }
        ]
    }
```

**Frontend Display**:

```typescript
// frontend/src/components/emr/EpicPatientBanner.tsx

{patient.video_resources?.essential_videos.length > 0 && (
  <Chip
    icon={<PlayCircleIcon />}
    label={`${patient.video_resources.essential_videos.length} Videos Available`}
    onClick={() => setShowVideoModal(true)}
    color="primary"
  />
)}

<VideoModal
  open={showVideoModal}
  videos={patient.video_resources.essential_videos}
  onClose={() => setShowVideoModal(false)}
/>
```

---

## 4. Unified Progress Tracking

### 4.1 Current Progress Tracking

**UserProgress Model** (existing):
```python
class UserProgress(Base):
    # MCQ metrics
    total_mcqs_attempted: Integer
    correct_mcqs: Integer
    cardiology_mcqs: Integer
    respiratory_mcqs: Integer
    # ... (10 specialties)

    # OSCE metrics
    total_osces_practiced: Integer
    cardiology_osces: Integer
    respiratory_osces: Integer
    # ... (10 specialties)

    # NEW: EMR metrics (added in migration)
    emr_sessions_completed: Integer
    emr_soap_notes_written: Integer
    emr_average_score: Float
    emr_cardiology_sessions: Integer
    emr_respiratory_sessions: Integer
    # ... (10 specialties)
```

### 4.2 Unified Dashboard Design

**Goal**: Single dashboard showing progress across all three assessment types.

**Frontend Component**: `frontend/src/components/dashboard/DashboardPage.tsx`

```typescript
const DashboardPage = () => {
  const { user } = useAuth();
  const { data: progress } = useQuery({
    queryKey: ['user-progress', user?.id],
    queryFn: async () => {
      const response = await axiosInstance.get(`/users/${user?.id}/progress`);
      return response.data;
    }
  });

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>My Progress</Typography>

      {/* Overview Cards */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StatCard
            title="MCQs Attempted"
            value={progress.total_mcqs_attempted}
            subtitle={`${Math.round(progress.correct_mcqs / progress.total_mcqs_attempted * 100)}% Correct`}
            icon={<QuizIcon />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="OSCEs Practiced"
            value={progress.total_osces_practiced}
            subtitle={`Avg Score: ${progress.osce_average_score?.toFixed(1)}/15`}
            icon={<PersonIcon />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <StatCard
            title="EMR Sessions"
            value={progress.emr_sessions_completed}
            subtitle={`Avg Score: ${progress.emr_average_score?.toFixed(1)}/15`}
            icon={<DescriptionIcon />}
            color="success"
          />
        </Grid>
      </Grid>

      {/* Unified Specialty Breakdown */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Progress by Specialty</Typography>
            <UnifiedSpecialtyChart data={progress} />
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Activity */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Recent MCQs</Typography>
            <RecentMCQsList userId={user?.id} />
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>Recent EMR Sessions</Typography>
            <RecentEMRSessionsList userId={user?.id} />
          </Paper>
        </Grid>
      </Grid>

      {/* Recommendations */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>📊 Recommended Next Steps</Typography>
            <SmartRecommendations progress={progress} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};
```

### 4.3 Unified Specialty Chart

**Visualization**: Grouped bar chart showing MCQ/OSCE/EMR progress per specialty.

```typescript
// frontend/src/components/dashboard/UnifiedSpecialtyChart.tsx

import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const UnifiedSpecialtyChart = ({ data }) => {
  const chartData = [
    {
      specialty: 'Cardiology',
      MCQs: data.cardiology_mcqs,
      OSCEs: data.cardiology_osces,
      EMR: data.emr_cardiology_sessions
    },
    {
      specialty: 'Respiratory',
      MCQs: data.respiratory_mcqs,
      OSCEs: data.respiratory_osces,
      EMR: data.emr_respiratory_sessions
    },
    // ... (all 10 specialties)
  ];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <BarChart data={chartData}>
        <XAxis dataKey="specialty" />
        <YAxis />
        <Tooltip />
        <Legend />
        <Bar dataKey="MCQs" fill="#1976d2" />
        <Bar dataKey="OSCEs" fill="#9c27b0" />
        <Bar dataKey="EMR" fill="#2e7d32" />
      </BarChart>
    </ResponsiveContainer>
  );
};
```

### 4.4 Smart Recommendations Engine

**Algorithm**: Identify weak areas and recommend targeted practice.

```python
# backend/src/services/recommendation_engine.py

def generate_smart_recommendations(user_progress: UserProgress) -> List[Dict]:
    """
    Analyze user progress and recommend next steps.

    Logic:
    1. Find specialties with low EMR practice (< 3 sessions)
    2. Find specialties with low MCQ accuracy (< 60%)
    3. Find specialties with no OSCE practice
    4. Recommend balanced practice across all three
    """

    recommendations = []

    # Analyze by specialty
    specialties = [
        'cardiology', 'respiratory', 'gastroenterology', 'neurology',
        'endocrinology', 'rheumatology', 'haematology', 'renal',
        'infectious_diseases', 'emergency_medicine'
    ]

    for specialty in specialties:
        mcq_count = getattr(user_progress, f"{specialty}_mcqs", 0)
        osce_count = getattr(user_progress, f"{specialty}_osces", 0)
        emr_count = getattr(user_progress, f"emr_{specialty}_sessions", 0)

        # Recommendation 1: Low EMR practice
        if emr_count < 3:
            recommendations.append({
                "type": "emr_practice",
                "specialty": specialty,
                "priority": "high",
                "message": f"Practice EMR documentation for {specialty.title()} (only {emr_count} sessions completed)",
                "action": f"/emr-practice?specialty={specialty}"
            })

        # Recommendation 2: Imbalanced practice
        total = mcq_count + osce_count + emr_count
        if total > 10 and emr_count < total * 0.2:
            recommendations.append({
                "type": "balance",
                "specialty": specialty,
                "priority": "medium",
                "message": f"Balance your {specialty.title()} practice with more EMR sessions",
                "action": f"/emr-practice?specialty={specialty}"
            })

        # Recommendation 3: Cross-reference learning
        if mcq_count > 20 and osce_count > 5 and emr_count == 0:
            recommendations.append({
                "type": "integration",
                "specialty": specialty,
                "priority": "high",
                "message": f"You've mastered {specialty.title()} MCQs and OSCEs - now practice EMR documentation!",
                "action": f"/emr-practice?specialty={specialty}"
            })

    # Sort by priority
    priority_order = {"high": 1, "medium": 2, "low": 3}
    recommendations.sort(key=lambda x: priority_order[x["priority"]])

    return recommendations[:5]  # Top 5 recommendations
```

**Frontend Display**:

```typescript
// frontend/src/components/dashboard/SmartRecommendations.tsx

const SmartRecommendations = ({ progress }) => {
  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', progress.user_id],
    queryFn: async () => {
      const response = await axiosInstance.get(`/analytics/recommendations`);
      return response.data;
    }
  });

  return (
    <Stack spacing={2}>
      {recommendations?.map((rec, index) => (
        <Alert
          key={index}
          severity={rec.priority === 'high' ? 'warning' : 'info'}
          action={
            <Button
              color="inherit"
              size="small"
              onClick={() => navigate(rec.action)}
            >
              Start Practice
            </Button>
          }
        >
          {rec.message}
        </Alert>
      ))}
    </Stack>
  );
};
```

---

## 5. Cross-Platform Linking

### 5.1 Bidirectional Navigation

**OSCE → EMR**:
```typescript
// frontend/src/components/osce/OSCEStationPage.tsx

<Button
  variant="outlined"
  startIcon={<ComputerIcon />}
  onClick={() => {
    // Convert this OSCE to EMR patient case
    navigate(`/emr-practice/from-osce/${osce.id}`);
  }}
>
  Practice This Case in EMR
</Button>
```

**Backend Endpoint**:
```python
@router.get("/patients/from-osce/{osce_id}")
async def get_emr_patient_from_osce(
    osce_id: int,
    db: Session = Depends(get_db)
):
    """Convert OSCE scenario to EMR patient on-the-fly."""

    # Check if already converted
    patient = db.query(MockPatient).filter(
        MockPatient.source_osce_id == osce_id
    ).first()

    if patient:
        return patient

    # Convert on-demand
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()
    if not osce:
        raise HTTPException(status_code=404, detail="OSCE not found")

    converter = OSCEToEMRConverter()
    patient = converter.convert(osce)
    db.add(patient)
    db.commit()

    return patient
```

**EMR → OSCE**:
```typescript
// frontend/src/components/emr/EMRValidationPanel.tsx

{session.patient.source_osce_id && (
  <Alert severity="info">
    📝 This case is based on OSCE Station #{session.patient.source_osce_id}
    <Button onClick={() => navigate(`/osce-practice/${session.patient.source_osce_id}`)}>
      Practice the Full OSCE
    </Button>
  </Alert>
)}
```

### 5.2 Learning Pathway Suggestions

**Scenario**: Student just completed EMR session with score 8/15 (failed)

**Smart Suggestion**:
```
⚠️ You scored 8/15 (53%) - below pass mark (60%)

📚 Recommended Learning Path:
1. Review eTG Cardiovascular Guidelines (5 min read)
2. Watch Video: "ECG Interpretation for ACS" (8 min)
3. Practice 5 MCQs on ACS Management
4. Practice OSCE Station #12: Chest Pain History Taking
5. Retry EMR Session with Similar Case

Start Learning Path → [Button]
```

**Implementation**:
```python
def generate_learning_pathway(session: EMRSession) -> Dict:
    """Generate personalized learning pathway after failed EMR session."""

    if session.validation_score >= 9:
        return {"type": "success", "message": "Great work! Try a harder case."}

    # Failed session - create learning pathway
    pathway_steps = []

    # Step 1: Guidelines review
    if session.patient.specialty == "cardiology":
        pathway_steps.append({
            "type": "reading",
            "title": "Review eTG Cardiovascular Guidelines",
            "url": "https://etg.tg.org.au/cardiovascular/",
            "duration_minutes": 5
        })

    # Step 2: Video
    videos = session.patient.video_resources.get("essential_videos", [])
    if videos:
        pathway_steps.append({
            "type": "video",
            "title": f"Watch: {videos[0]['title']}",
            "url": videos[0]['url'],
            "duration_minutes": videos[0]['duration_minutes']
        })

    # Step 3: MCQs
    related_mcqs = find_related_mcqs(session)
    if related_mcqs:
        pathway_steps.append({
            "type": "mcq",
            "title": f"Practice {len(related_mcqs)} MCQs on {session.specialty.title()}",
            "mcq_ids": [mcq.id for mcq in related_mcqs]
        })

    # Step 4: OSCE
    if session.patient.source_osce_id:
        pathway_steps.append({
            "type": "osce",
            "title": f"Practice OSCE Station #{session.patient.source_osce_id}",
            "osce_id": session.patient.source_osce_id
        })

    # Step 5: Retry EMR
    pathway_steps.append({
        "type": "emr",
        "title": "Retry EMR Session with Similar Case",
        "specialty": session.specialty,
        "difficulty": session.difficulty
    })

    return {
        "type": "learning_pathway",
        "message": f"You scored {session.validation_score}/15 - below pass mark",
        "steps": pathway_steps,
        "estimated_time_minutes": sum(step.get("duration_minutes", 10) for step in pathway_steps)
    }
```

---

## 6. Implementation Timeline

### Week 1: Foundation
- [ ] Create `OSCEToEMRConverter` class with full parsing logic
- [ ] Create `convert_osce_to_emr.py` batch script
- [ ] Test conversion on 5 sample OSCEs (manual verification)
- [ ] Generate Australian name/address/phone helpers

### Week 2: Content Population
- [ ] Convert 50 priority patients (cardiology, respiratory, emergency)
- [ ] Verify 10 randomly selected patients manually (medical expert review)
- [ ] Populate `mock_patients` table
- [ ] Create EMR → OSCE bidirectional links

### Week 3: MCQ & Video Integration
- [ ] Implement `find_related_mcqs()` service
- [ ] Implement PBS medication cross-reference
- [ ] Add video resources to `MockPatient` records
- [ ] Create video modal component

### Week 4: Unified Dashboard
- [ ] Extend `UserProgress` API to return EMR metrics
- [ ] Create `UnifiedSpecialtyChart` component
- [ ] Implement `SmartRecommendations` engine
- [ ] Create learning pathway generator

---

## 7. Success Criteria

- [ ] 50 mock_patients created from priority OSCEs (Week 2)
- [ ] All patients have realistic demographics, vitals, investigations
- [ ] 100% of patients have validation_criteria extracted from OSCE rubrics
- [ ] Bidirectional links working (OSCE ↔ EMR)
- [ ] Related MCQs showing after EMR session (5+ suggestions)
- [ ] Video resources embedded in patient cases
- [ ] Unified dashboard displaying MCQ + OSCE + EMR progress
- [ ] Smart recommendations generating 3-5 actionable suggestions
- [ ] Learning pathways created for failed EMR sessions

---

## Conclusion

This integration strategy creates a **cohesive learning ecosystem** where:

- ✅ **OSCE scenarios become EMR patient cases** (221 → 500+ patients)
- ✅ **MCQ medication content validates EMR prescriptions** (PBS cross-reference)
- ✅ **Educational videos enhance EMR learning** (contextual video suggestions)
- ✅ **Unified progress tracking** (single dashboard for all three assessment types)
- ✅ **Smart recommendations** (AI-powered learning pathway generation)

**Result**: Students practice in a realistic, integrated environment that mirrors real clinical workflows while reinforcing learning across multiple modalities.

---

**Document Status**: ✅ READY FOR IMPLEMENTATION
**Last Updated**: 2026-02-15
**Next Steps**: Begin implementation with database migration and OSCE conversion
