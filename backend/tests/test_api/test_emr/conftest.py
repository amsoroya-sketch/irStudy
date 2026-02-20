"""
Pytest fixtures for EMR testing

Provides:
- Database session fixtures
- Mock patient data
- Mock EMR sessions
- Authentication headers
- Mock Claude AI responses
"""

import pytest
import json
from datetime import datetime, timedelta
from uuid import uuid4
from typing import Dict, Any

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.db.base import Base, get_db
from src.db.models import User, UserRole
from src.auth.security import get_password_hash


# ============================================================================
# TEST DATABASE SETUP
# ============================================================================

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for tests"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


# ============================================================================
# DATABASE FIXTURES
# ============================================================================


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def empty_db(db_session):
    """Empty database for testing edge cases"""
    return db_session


# ============================================================================
# USER FIXTURES
# ============================================================================


@pytest.fixture
def test_user(db_session):
    """Create test student user"""
    user = User(
        email="student@test.com",
        password_hash=get_password_hash("TestPassword123"),
        full_name="Test Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_educator(db_session):
    """Create test educator user"""
    user = User(
        email="educator@test.com",
        password_hash=get_password_hash("EducatorPass123"),
        full_name="Test Educator",
        role=UserRole.EDUCATOR,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def other_user(db_session):
    """Create another test user (for testing authorization)"""
    user = User(
        email="other@test.com",
        password_hash=get_password_hash("OtherPass123"),
        full_name="Other Student",
        role=UserRole.STUDENT,
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


# ============================================================================
# AUTHENTICATION FIXTURES
# ============================================================================


@pytest.fixture
def auth_headers(test_user):
    """Get JWT authentication headers for test user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "student@test.com",
            "password": "TestPassword123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def educator_headers(test_educator):
    """Get JWT authentication headers for educator"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "educator@test.com",
            "password": "EducatorPass123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def other_user_headers(other_user):
    """Get JWT authentication headers for other user"""
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "other@test.com",
            "password": "OtherPass123",
        },
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


# ============================================================================
# MOCK PATIENT FIXTURES
# ============================================================================


@pytest.fixture
def mock_patient_cardiology(db_session) -> Dict[str, Any]:
    """
    Mock cardiology patient - Acute Coronary Syndrome (STEMI)
    
    This would normally be a MockPatient database model,
    but for now we return a dict representation.
    """
    patient_data = {
        "id": str(uuid4()),
        "mrn": "MRN12345678",
        "medicare_number": "2912345671",
        "name": "John Smith",
        "age": 58,
        "gender": "male",
        "aboriginal_tsi_status": "Neither",
        "demographics": {
            "address": "12 King Street, Sydney NSW 2000",
            "phone": "0412 345 678",
            "emergency_contact": {
                "name": "Mary Smith",
                "relationship": "Wife",
                "phone": "0412 345 679"
            },
            "gp_details": {
                "name": "Dr. Jane Doe",
                "clinic": "Sydney Medical Centre",
                "phone": "02 9876 5432"
            }
        },
        "presenting_complaint": "Central chest pain for 2 hours",
        "medical_history": {
            "pmhx": ["Hypertension", "Type 2 Diabetes", "Hyperlipidaemia"],
            "surgical_history": [],
            "family_history": "Father had MI at 60",
            "social_history": "Smoker 30 pack-years, drinks 2 standard drinks/day"
        },
        "medications": [
            {
                "name": "Amlodipine",
                "dose": "5mg",
                "frequency": "daily",
                "route": "PO"
            },
            {
                "name": "Metformin",
                "dose": "500mg",
                "frequency": "BD",
                "route": "PO"
            },
            {
                "name": "Atorvastatin",
                "dose": "40mg",
                "frequency": "nocte",
                "route": "PO"
            }
        ],
        "allergies": [
            {
                "allergen": "Penicillin",
                "reaction": "Rash",
                "severity": "mild"
            }
        ],
        "vital_signs": {
            "hr": 95,
            "bp_systolic": 155,
            "bp_diastolic": 92,
            "rr": 20,
            "spo2": 96,
            "temp": 36.8,
            "pain_score": 7
        },
        "physical_exam_findings": {
            "general": "Alert, distressed, diaphoretic",
            "cvs": "Regular rhythm, no murmurs, nil JVP elevation",
            "rs": "Clear lung fields bilaterally, no wheeze/crackles",
            "abdomen": "Soft, non-tender, no masses",
            "neuro": "GCS 15, pupils equal and reactive"
        },
        "investigation_results": {
            "ecg": {
                "findings": "ST elevation 2mm in leads II, III, aVF. Reciprocal ST depression in I, aVL",
                "interpretation": "Inferior STEMI"
            },
            "labs": {
                "troponin_i": {
                    "value": 1.2,
                    "unit": "ng/mL",
                    "reference_range": "0-0.04",
                    "flag": "HIGH"
                },
                "fbc": {
                    "hb": 145,
                    "wcc": 9.2,
                    "plt": 250
                },
                "uec": {
                    "na": 138,
                    "k": 4.2,
                    "cr": 85,
                    "egfr": 90
                },
                "bsl": {
                    "value": 8.2,
                    "unit": "mmol/L"
                }
            },
            "cxr": {
                "findings": "Clear lung fields, normal heart size",
                "interpretation": "Normal"
            }
        },
        "specialty": "cardiology",
        "difficulty": "medium",
        "validation_criteria": {
            "expected_diagnosis": ["Acute Coronary Syndrome", "STEMI", "Myocardial Infarction"],
            "expected_investigations": ["ECG", "Troponin", "FBC", "UEC", "CXR"],
            "expected_management": [
                "Call 000 / Activate cath lab",
                "Aspirin 300mg STAT",
                "Clopidogrel or Ticagrelor",
                "Morphine for pain relief",
                "GTN spray",
                "Oxygen if SpO2 <94%"
            ],
            "red_flags": [
                "STEMI criteria met - urgent cardiology referral",
                "Cath lab activation within 90 minutes"
            ],
            "rubric": {
                "history_examination": {
                    "marks": 3,
                    "criteria": [
                        "SOCRATES pain assessment",
                        "Cardiovascular risk factors elicited",
                        "Systematic examination documented"
                    ]
                },
                "clinical_reasoning": {
                    "marks": 3,
                    "criteria": [
                        "Appropriate differential diagnosis",
                        "Correct ECG interpretation",
                        "Risk stratification documented"
                    ]
                },
                "communication": {
                    "marks": 3,
                    "criteria": [
                        "Clear, structured documentation",
                        "Safety netting advice",
                        "Handover to cardiology team"
                    ]
                },
                "patient_safety": {
                    "marks": 3,
                    "criteria": [
                        "Urgent referral arranged",
                        "Antiplatelet therapy initiated",
                        "Monitoring plan documented"
                    ]
                },
                "professionalism": {
                    "marks": 3,
                    "criteria": [
                        "Australian terminology used",
                        "eTG guideline compliance",
                        "Timely escalation"
                    ]
                }
            }
        }
    }
    return patient_data


@pytest.fixture
def mock_patient_respiratory(db_session) -> Dict[str, Any]:
    """Mock respiratory patient - Acute Asthma Exacerbation"""
    patient_data = {
        "id": str(uuid4()),
        "mrn": "MRN87654321",
        "medicare_number": "3912345678",
        "name": "Sarah Johnson",
        "age": 32,
        "gender": "female",
        "aboriginal_tsi_status": "Aboriginal",
        "demographics": {
            "address": "45 George Street, Parramatta NSW 2150",
            "phone": "0423 456 789"
        },
        "presenting_complaint": "Worsening shortness of breath for 2 days",
        "medical_history": {
            "pmhx": ["Asthma (since childhood)", "Allergic rhinitis"],
            "surgical_history": [],
            "family_history": "Mother has asthma",
            "social_history": "Non-smoker, no pets, works as teacher"
        },
        "medications": [
            {
                "name": "Salbutamol",
                "dose": "100mcg",
                "frequency": "PRN",
                "route": "inhaled"
            },
            {
                "name": "Fluticasone",
                "dose": "250mcg",
                "frequency": "BD",
                "route": "inhaled"
            }
        ],
        "allergies": [
            {
                "allergen": "NKDA",
                "reaction": None,
                "severity": None
            }
        ],
        "vital_signs": {
            "hr": 110,
            "bp_systolic": 130,
            "bp_diastolic": 80,
            "rr": 28,
            "spo2": 91,
            "temp": 36.9,
            "pain_score": 0
        },
        "physical_exam_findings": {
            "general": "Alert, dyspneic, speaking in short sentences",
            "cvs": "Tachycardic, regular rhythm",
            "rs": "Widespread wheeze bilaterally, prolonged expiratory phase, poor air entry",
            "abdomen": "Not examined (patient too dyspneic)",
            "neuro": "GCS 15"
        },
        "investigation_results": {
            "peak_flow": {
                "value": 250,
                "unit": "L/min",
                "predicted": 450,
                "percentage": 55,
                "flag": "SEVERE"
            },
            "abg": {
                "ph": 7.42,
                "pco2": 35,
                "po2": 65,
                "hco3": 23,
                "interpretation": "Type 1 respiratory failure"
            },
            "cxr": {
                "findings": "Hyperinflation, no consolidation",
                "interpretation": "Consistent with acute asthma"
            }
        },
        "specialty": "respiratory",
        "difficulty": "medium",
        "validation_criteria": {
            "expected_diagnosis": ["Acute asthma exacerbation", "Severe asthma"],
            "expected_investigations": ["Peak flow", "ABG", "CXR"],
            "expected_management": [
                "Oxygen to maintain SpO2 >94%",
                "Salbutamol nebuliser 5mg continuous",
                "Ipratropium nebuliser 500mcg",
                "Hydrocortisone 100mg IV or prednisolone 50mg PO",
                "Consider magnesium sulfate if severe"
            ]
        }
    }
    return patient_data


# ============================================================================
# MOCK EMR SESSION FIXTURES
# ============================================================================


@pytest.fixture
def mock_session_in_progress(db_session, test_user, mock_patient_cardiology) -> Dict[str, Any]:
    """Mock EMR session in progress"""
    session_data = {
        "id": str(uuid4()),
        "user_id": test_user.id,
        "patient_id": mock_patient_cardiology["id"],
        "specialty": "cardiology",
        "difficulty": "medium",
        "started_at": datetime.utcnow().isoformat(),
        "submitted_at": None,
        "elapsed_time_seconds": 900,  # 15 minutes
        "validation_score": None,
        "status": "in_progress",
        "auto_save_count": 2,
        "last_auto_save_at": (datetime.utcnow() - timedelta(seconds=30)).isoformat()
    }
    return session_data


@pytest.fixture
def mock_session_graded(db_session, test_user, mock_patient_cardiology) -> Dict[str, Any]:
    """Mock EMR session that has been graded"""
    session_data = {
        "id": str(uuid4()),
        "user_id": test_user.id,
        "patient_id": mock_patient_cardiology["id"],
        "specialty": "cardiology",
        "difficulty": "medium",
        "started_at": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
        "submitted_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
        "elapsed_time_seconds": 1800,  # 30 minutes
        "validation_score": 12.5,
        "status": "graded",
        "auto_save_count": 5,
        "score_breakdown": {
            "history_examination": 3.0,
            "clinical_reasoning": 2.5,
            "communication": 3.0,
            "patient_safety": 2.0,
            "professionalism": 2.0
        },
        "typing_metrics": {
            "total_words": 450,
            "average_wpm": 35,
            "total_typing_time_seconds": 770,
            "backspace_count": 42,
            "accuracy": 0.92
        }
    }
    return session_data


# ============================================================================
# MOCK SOAP NOTE FIXTURES
# ============================================================================


@pytest.fixture
def valid_soap_note() -> Dict[str, str]:
    """Valid SOAP note meeting all validation criteria"""
    return {
        "subjective": (
            "58-year-old male presenting with 2-hour history of central crushing chest pain "
            "7/10 severity, radiating to left arm. Pain started at rest while watching television. "
            "Associated symptoms include sweating, nausea, and feeling of impending doom. "
            "Pain is constant, not relieved by rest. Patient has tried GTN spray at home "
            "without relief. PMHx includes hypertension (on amlodipine 5mg daily), "
            "type 2 diabetes (on metformin 500mg BD), and hyperlipidaemia (on atorvastatin 40mg nocte). "
            "Smoker with 30 pack-year history. Father had MI at age 60. "
            "Denies recent illness, trauma, or exertion. No previous cardiac history."
        ),
        "objective": (
            "Observations: Alert, distressed appearance, diaphoretic. HR 95 bpm (regular), "
            "BP 155/92 mmHg, RR 20/min, SpO2 96% on room air, Temp 36.8°C, Pain score 7/10. "
            "CVS: Regular rhythm, no murmurs, nil JVP elevation, peripheral pulses palpable. "
            "RS: Clear lung fields bilaterally, no wheeze or crackles, equal air entry. "
            "Abdomen: Soft, non-tender, no masses, bowel sounds present. "
            "Neuro: GCS 15/15, pupils equal and reactive to light (PERL), no focal neurology. "
            "ECG: ST elevation 2mm in leads II, III, aVF with reciprocal ST depression in I, aVL. "
            "Troponin I: 1.2 ng/mL (reference <0.04 ng/mL)."
        ),
        "assessment": (
            "Acute Coronary Syndrome - Inferior STEMI (ST-Elevation Myocardial Infarction). "
            "ECG shows diagnostic ST elevation in inferior leads II, III, aVF with reciprocal changes. "
            "Elevated troponin I confirms myocardial injury. Clinical presentation with chest pain, "
            "radiation to left arm, diaphoresis, and cardiovascular risk factors (age, male gender, "
            "smoking, hypertension, diabetes, hyperlipidaemia, family history) consistent with ACS. "
            "Differential diagnoses considered and excluded: PE unlikely (no risk factors, normal SpO2), "
            "aortic dissection unlikely (equal pulses, no tearing pain), gastritis unlikely (ECG changes)."
        ),
        "plan": (
            "IMMEDIATE MANAGEMENT: Call 000 / Activate cath lab for primary PCI (target door-to-balloon <90 minutes). "
            "Dual antiplatelet therapy: Aspirin 300mg STAT PO (loaded), Ticagrelor 180mg STAT PO (or Clopidogrel 300mg if contraindication). "
            "Pain relief: Morphine 2.5mg IV with 10mg metoclopramide IV for nausea. "
            "GTN spray 400mcg sublingual (caution with BP). Oxygen therapy if SpO2 <94% (currently 96%). "
            "Continuous cardiac monitoring, IV access x2, serial troponins at 0h and 3h. "
            "Admit to CCU under cardiology. Beta-blocker and ACE inhibitor post-PCI as per eTG guidelines. "
            "Cardiology consult URGENT - Dr. Smith paged at 1430. Patient informed of diagnosis, "
            "treatment plan explained, consent obtained for PCI. Family contacted and en route to hospital."
        )
    }


@pytest.fixture
def incomplete_soap_note() -> Dict[str, str]:
    """SOAP note with incomplete sections (fails validation)"""
    return {
        "subjective": "Chest pain for 2 hours",  # Too short (<50 chars)
        "objective": "HR 95, BP 155/92",  # Too short (<30 chars)
        "assessment": "ACS",  # Too short (<20 chars)
        "plan": "Give aspirin"  # Too short (<30 chars)
    }


# ============================================================================
# MOCK CLAUDE AI RESPONSE FIXTURES
# ============================================================================


@pytest.fixture
def mock_claude_response_high_score() -> Dict[str, Any]:
    """Mock Claude AI response with high validation score (12.5/15)"""
    return {
        "content": [{
            "text": json.dumps({
                "overall_score": 12.5,
                "category_scores": {
                    "history_examination": 3.0,
                    "clinical_reasoning": 2.5,
                    "communication": 3.0,
                    "patient_safety": 2.0,
                    "professionalism": 2.0
                },
                "strengths": [
                    "Excellent SOCRATES pain assessment with all components (Site, Onset, Character, Radiation, Associated symptoms, Time course, Exacerbating/relieving factors, Severity)",
                    "Comprehensive cardiovascular risk factor documentation (age, gender, smoking, HTN, DM, hyperlipidaemia, family history)",
                    "Appropriate differential diagnosis considered (ACS, PE, aortic dissection, gastritis) with reasoning",
                    "Safety netting with clear red flag advice and urgent escalation to cardiology",
                    "Correct use of Australian terminology (paracetamol not acetaminophen, adrenaline not epinephrine)"
                ],
                "improvements": [
                    "Consider asking about radiation to jaw/neck/back (common in ACS presentations)",
                    "Add cardiovascular examination findings for carotid bruits and peripheral vascular disease",
                    "Specify exact troponin timing in plan (serial troponins at 0h, 3h, 6h for monitoring trend)"
                ],
                "red_flags": [
                    "STEMI criteria met (ST elevation >1mm in 2 contiguous leads) - URGENT cardiology referral needed immediately",
                    "Patient requires immediate cath lab activation within 90 minutes (door-to-balloon time target)",
                    "High risk of cardiogenic shock - continuous monitoring essential"
                ],
                "australian_compliance": {
                    "terminology": "✓ Correct (paracetamol not acetaminophen, adrenaline not epinephrine, documented in eTG format)",
                    "emergency_number": "✓ Mentioned 000 for emergency activation (not 911)",
                    "etg_alignment": "✓ Follows eTG Cardiovascular guidelines for ACS management (dual antiplatelet, beta-blocker, ACE inhibitor post-PCI)"
                }
            })
        }]
    }


@pytest.fixture
def mock_claude_response_low_score() -> Dict[str, Any]:
    """Mock Claude AI response with low validation score (6.0/15 - fail)"""
    return {
        "content": [{
            "text": json.dumps({
                "overall_score": 6.0,
                "category_scores": {
                    "history_examination": 1.0,
                    "clinical_reasoning": 1.0,
                    "communication": 2.0,
                    "patient_safety": 1.0,
                    "professionalism": 1.0
                },
                "strengths": [
                    "Basic vital signs documented",
                    "Recognized chest pain as concerning symptom"
                ],
                "improvements": [
                    "SOCRATES pain assessment incomplete - missing radiation, associated symptoms, exacerbating/relieving factors",
                    "No cardiovascular risk factors documented (smoking, family history, comorbidities)",
                    "Differential diagnosis not documented - only considered ACS",
                    "No ECG interpretation documented despite abnormal ECG",
                    "Management plan missing dual antiplatelet therapy (no Ticagrelor or Clopidogrel)",
                    "No mention of cardiology referral urgency or cath lab activation",
                    "Pain relief plan inadequate (no morphine dosing)"
                ],
                "red_flags": [
                    "CRITICAL: STEMI not recognized despite ECG showing ST elevation",
                    "CRITICAL: No urgent cardiology referral arranged",
                    "CRITICAL: Dual antiplatelet therapy not initiated (standard of care for STEMI)",
                    "Patient safety compromised - inadequate management plan for life-threatening condition"
                ],
                "australian_compliance": {
                    "terminology": "⚠ Mixed (used some Australian terms but inconsistent)",
                    "emergency_number": "✗ Did not mention 000 for emergency escalation",
                    "etg_alignment": "✗ Does not follow eTG Cardiovascular guidelines (missing key medications)"
                }
            })
        }]
    }


# ============================================================================
# MOCK PRESCRIPTION FIXTURES
# ============================================================================


@pytest.fixture
def valid_prescription() -> Dict[str, Any]:
    """Valid PBS-compliant prescription"""
    return {
        "medication_name": "Aspirin",
        "dose": "100mg",
        "frequency": "daily",
        "route": "PO",
        "repeats": 5,
        "indication": "Secondary prevention post-STEMI",
        "pbs_listed": True,
        "authority_required": False
    }


@pytest.fixture
def invalid_prescription_exceeds_repeats() -> Dict[str, Any]:
    """Invalid prescription - exceeds PBS max 5 repeats"""
    return {
        "medication_name": "Amlodipine",
        "dose": "5mg",
        "frequency": "daily",
        "route": "PO",
        "repeats": 6,  # EXCEEDS MAX 5
        "indication": "Hypertension"
    }


# ============================================================================
# MOCK PATHOLOGY ORDER FIXTURES
# ============================================================================


@pytest.fixture
def valid_pathology_order() -> Dict[str, Any]:
    """Valid MBS-compliant pathology order"""
    return {
        "test_name": "Troponin I",
        "mbs_item_number": "66800",
        "urgency": "emergency",
        "indication": "Suspected STEMI - serial troponins required",
        "appropriate": True
    }


@pytest.fixture
def inappropriate_pathology_order() -> Dict[str, Any]:
    """Inappropriate pathology order (overuse)"""
    return {
        "test_name": "Full body MRI",
        "mbs_item_number": None,
        "urgency": "routine",
        "indication": "Chest pain",  # Inappropriate investigation for ACS
        "appropriate": False
    }
