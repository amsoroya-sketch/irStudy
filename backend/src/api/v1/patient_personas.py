"""
Patient Persona endpoints for AI OSCE Simulation

Routes:
- GET /api/v1/patient-personas - List personas (filter by specialty/difficulty)
- GET /api/v1/patient-personas/{persona_id} - Get single persona with full details

SECURITY:
- JWT authentication required on all endpoints
- UUID validation for persona_id
- No PHI leaks in error messages
- Input sanitization via Pydantic schemas

AMC CLINICAL EXAM CONTEXT:
- 360 unique patient personas (specialties × difficulty levels)
- Progressive disclosure: Information revealed based on student questions
- Emotional intelligence: Patient state changes based on student interaction
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from uuid import UUID

from src.db.base import get_db
from src.db.models import PatientPersona, User
from src.auth.dependencies import get_current_active_user


router = APIRouter(prefix="/patient-personas", tags=["ai-osce"])


@router.get("/", response_model=List[dict])
async def list_patient_personas(
    specialty: Optional[str] = Query(None, description="Filter by specialty"),
    difficulty: Optional[str] = Query(None, description="foundation, intermediate, or advanced"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List patient personas for AI OSCE practice.

    Query parameters:
    - specialty: Filter by medical specialty (cardiology, respiratory, etc.)
    - difficulty: Filter by difficulty level (foundation, intermediate, advanced)
    - skip: Pagination offset
    - limit: Maximum results (default 20, max 100)

    Returns:
    - List of persona summaries (without full progressive disclosure details)

    Example response:
    [
        {
            "persona_id": "123e4567-e89b-12d3-a456-426614174000",
            "persona_code": "CARD-001-CHEST-PAIN",
            "name": "John Smith",
            "age": 58,
            "gender": "male",
            "specialty": "cardiology",
            "chief_complaint": "Chest pain for 2 hours",
            "difficulty_level": "intermediate",
            "estimated_pass_rate": 0.65,
            "amc_blueprint_area": "Cardiovascular system"
        }
    ]
    """
    query = db.query(PatientPersona).filter(PatientPersona.is_active == True)

    if specialty:
        query = query.filter(PatientPersona.specialty == specialty)

    if difficulty:
        query = query.filter(PatientPersona.difficulty_level == difficulty)

    personas = query.offset(skip).limit(limit).all()

    # Return summary view (exclude full progressive disclosure)
    return [
        {
            "persona_id": str(p.persona_id),
            "persona_code": p.persona_code,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "specialty": p.specialty,
            "chief_complaint": p.chief_complaint,
            "difficulty_level": p.difficulty_level,
            "estimated_pass_rate": float(p.estimated_pass_rate) if p.estimated_pass_rate else None,
            "amc_blueprint_area": p.amc_blueprint_area,
        }
        for p in personas
    ]


@router.get("/{persona_id}", response_model=dict)
async def get_patient_persona(
    persona_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get complete patient persona details.

    Includes:
    - Full demographics
    - Opening statement (what AI Patient says first)
    - Progressive disclosure structure (symptoms, medical history)
    - Emotional profile (state machine for AI behavior)
    - Critical actions and differentials

    Use this after selecting a persona to start an OSCE session.

    Args:
    - persona_id: UUID of patient persona

    Returns:
    - Complete persona details with progressive disclosure structure

    Raises:
    - 404: Patient persona not found

    Example response:
    {
        "persona_id": "123e4567-e89b-12d3-a456-426614174000",
        "persona_code": "CARD-001-CHEST-PAIN",
        "name": "John Smith",
        "age": 58,
        "opening_statement": "Doctor, I've been having this terrible chest pain...",
        "symptoms": {
            "immediate": ["chest pain", "shortness of breath"],
            "on_questioning": ["pain radiates to left arm", "nausea"]
        },
        "medical_history": {
            "past_medical": ["hypertension", "type 2 diabetes"],
            "medications": ["metformin", "amlodipine"]
        },
        "emotional_profile": {
            "initial_state": "anxious",
            "triggers": {"reassurance": "calm", "dismissive": "agitated"}
        },
        "key_differentials": ["STEMI", "unstable angina", "aortic dissection"],
        "critical_actions": ["ECG within 10 minutes", "aspirin 300mg"]
    }
    """
    persona = db.query(PatientPersona).filter(
        PatientPersona.persona_id == str(persona_id),
        PatientPersona.is_active == True
    ).first()

    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient persona not found"
        )

    return {
        "persona_id": str(persona.persona_id),
        "persona_code": persona.persona_code,
        "name": persona.name,
        "age": persona.age,
        "gender": persona.gender,
        "occupation": persona.occupation,
        "cultural_background": persona.cultural_background,
        "preferred_language": persona.preferred_language,
        "specialty": persona.specialty,
        "chief_complaint": persona.chief_complaint,
        "opening_statement": persona.opening_statement,
        "symptoms": persona.symptoms,
        "medical_history": persona.medical_history,
        "emotional_profile": persona.emotional_profile,
        "rag_query_hints": persona.rag_query_hints,
        "key_differentials": persona.key_differentials,
        "critical_actions": persona.critical_actions,
        "difficulty_level": persona.difficulty_level,
        "estimated_pass_rate": float(persona.estimated_pass_rate) if persona.estimated_pass_rate else None,
        "amc_blueprint_area": persona.amc_blueprint_area,
        "amc_competencies": persona.amc_competencies,
    }
