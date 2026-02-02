"""
OSCE (Objective Structured Clinical Examination) endpoints

Routes:
- GET /api/v1/osces - List OSCEs (filterable by specialty, type)
- GET /api/v1/osces/{osce_id} - Get single OSCE
- POST /api/v1/osces - Create new OSCE (educator/admin only)
- PUT /api/v1/osces/{osce_id} - Update OSCE (educator/admin only)
- DELETE /api/v1/osces/{osce_id} - Delete OSCE (admin only)
- GET /api/v1/osces/{osce_id}/rubric - Get marking rubric

AMC CLINICAL EXAM FORMAT:
- 15-mark rubric system (5 categories × 3 marks each)
- 8-minute station duration
- Categories: History/Examination, Clinical Reasoning, Communication, Safety, Professionalism
- Australian medical context required
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from db.base import get_db
from db.models import User, OSCE, MedicalSpecialty, OSCEType
from schemas.osce import OSCECreate, OSCEUpdate, OSCEPublic, OSCEWithRubric
from auth.dependencies import get_current_active_user, require_educator


router = APIRouter(prefix="/osces", tags=["osces"])


# ============================================================================
# LIST OSCEs
# ============================================================================

@router.get("/", response_model=List[OSCEPublic])
async def list_osces(
    specialty: Optional[MedicalSpecialty] = None,
    osce_type: Optional[OSCEType] = None,
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List OSCEs with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty
    - osce_type: Filter by station type (history_taking, physical_exam, etc.)
    - tags: Comma-separated tags
    - skip: Number of records to skip (pagination)
    - limit: Maximum number of records (max 100)

    Returns:
    - List of OSCE stations with instructions
    - Includes patient instructions, candidate instructions, time limit
    - Rubric shown separately (prevents accidental viewing during practice)
    """
    query = db.query(OSCE).filter(OSCE.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(OSCE.specialty == specialty)

    if osce_type:
        query = query.filter(OSCE.station_type == osce_type)

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(OSCE.tags.contains([tag]))

    # Pagination
    osces = query.offset(skip).limit(min(limit, 100)).all()

    return osces


# ============================================================================
# GET SINGLE OSCE
# ============================================================================

@router.get("/{osce_id}", response_model=OSCEPublic)
async def get_osce(
    osce_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get single OSCE by ID.

    Args:
    - osce_id: OSCE database ID

    Returns:
    - OSCE station details without rubric
    - Use /osces/{osce_id}/rubric to get marking criteria
    """
    osce = db.query(OSCE).filter(
        OSCE.id == osce_id,
        OSCE.is_published == True
    ).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE not found"
        )

    return osce


# ============================================================================
# GET OSCE RUBRIC
# ============================================================================

@router.get("/{osce_id}/rubric", response_model=OSCEWithRubric)
async def get_osce_rubric(
    osce_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get OSCE station with marking rubric.

    Use this AFTER practice to review marking criteria.

    Args:
    - osce_id: OSCE database ID

    Returns:
    - Complete OSCE with 15-mark AMC format rubric
    - Rubric structure:
      - History/Examination: 0-3 marks
      - Clinical Reasoning: 0-3 marks
      - Communication Skills: 0-3 marks
      - Patient Safety: 0-3 marks
      - Professionalism: 0-3 marks
      - Total: 0-15 marks
    """
    osce = db.query(OSCE).filter(
        OSCE.id == osce_id,
        OSCE.is_published == True
    ).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE not found"
        )

    return osce


# ============================================================================
# CREATE OSCE (Educator/Admin only)
# ============================================================================

@router.post("/", response_model=OSCEWithRubric, status_code=status.HTTP_201_CREATED)
async def create_osce(
    osce_data: OSCECreate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Create new OSCE station (educator/admin only).

    Requirements:
    - osce_id: Unique identifier (format: OSCE-SPEC-XXX)
    - station_title: Descriptive title
    - station_type: Type of station (history_taking, physical_exam, etc.)
    - patient_instructions: Instructions for simulated patient
    - candidate_instructions: Instructions shown to candidate
    - rubric: 15-mark AMC format marking criteria
    - specialty: Medical specialty
    - time_limit_minutes: Default 8 minutes

    AMC Rubric Format (15 marks total):
    ```json
    {
      "history_examination": {
        "criteria": "Systematic approach, completeness, appropriate questions",
        "marks": 3,
        "0": "Did not take history/perform examination",
        "1": "Incomplete/disorganized approach",
        "2": "Good approach with minor omissions",
        "3": "Excellent systematic comprehensive approach"
      },
      "clinical_reasoning": {...},
      "communication": {...},
      "safety": {...},
      "professionalism": {...}
    }
    ```

    Returns:
    - Created OSCE with full details including rubric
    """
    # Check if osce_id already exists
    existing_osce = db.query(OSCE).filter(OSCE.osce_id == osce_data.osce_id).first()
    if existing_osce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OSCE with osce_id '{osce_data.osce_id}' already exists"
        )

    # Validate rubric structure (should have 5 categories totaling 15 marks)
    if isinstance(osce_data.rubric, dict):
        total_marks = sum(
            category.get('marks', 0)
            for category in osce_data.rubric.values()
            if isinstance(category, dict)
        )
        if total_marks != 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric must total 15 marks (AMC format), got {total_marks} marks"
            )

    # Create new OSCE
    new_osce = OSCE(
        osce_id=osce_data.osce_id,
        station_title=osce_data.station_title,
        station_type=osce_data.station_type,
        patient_instructions=osce_data.patient_instructions,
        candidate_instructions=osce_data.candidate_instructions,
        examiner_instructions=osce_data.examiner_instructions,
        rubric=osce_data.rubric,
        specialty=osce_data.specialty,
        time_limit_minutes=osce_data.time_limit_minutes or 8,
        learning_objectives=osce_data.learning_objectives,
        red_flags=osce_data.red_flags,
        australian_guidelines=osce_data.australian_guidelines,
        tags=osce_data.tags,
        is_published=False  # Requires review before publishing
    )

    db.add(new_osce)
    db.commit()
    db.refresh(new_osce)

    return new_osce


# ============================================================================
# UPDATE OSCE (Educator/Admin only)
# ============================================================================

@router.put("/{osce_id}", response_model=OSCEWithRubric)
async def update_osce(
    osce_id: int,
    osce_update: OSCEUpdate,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Update existing OSCE (educator/admin only).

    Args:
    - osce_id: OSCE database ID
    - osce_update: Fields to update (all optional)

    Returns:
    - Updated OSCE with full details

    Note:
    - Updating rubric creates audit trail
    - Consider versioning if OSCE is actively used
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE not found"
        )

    # Update fields
    update_data = osce_update.dict(exclude_unset=True)

    # Validate rubric if provided
    if 'rubric' in update_data and update_data['rubric']:
        total_marks = sum(
            category.get('marks', 0)
            for category in update_data['rubric'].values()
            if isinstance(category, dict)
        )
        if total_marks != 15:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Rubric must total 15 marks (AMC format), got {total_marks} marks"
            )

    for field, value in update_data.items():
        setattr(osce, field, value)

    db.commit()
    db.refresh(osce)

    return osce


# ============================================================================
# DELETE OSCE (Admin only)
# ============================================================================

@router.delete("/{osce_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_osce(
    osce_id: int,
    current_user: User = Depends(require_educator),
    db: Session = Depends(get_db)
):
    """
    Delete OSCE (soft delete for audit trail).

    Args:
    - osce_id: OSCE database ID

    Note:
    - Performs soft delete (sets deleted_at timestamp)
    - OSCE hidden from queries but data retained
    """
    osce = db.query(OSCE).filter(OSCE.id == osce_id).first()

    if not osce:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="OSCE not found"
        )

    # Soft delete
    from datetime import datetime
    osce.deleted_at = datetime.now(datetime.now().astimezone().tzinfo)

    db.commit()

    return None
