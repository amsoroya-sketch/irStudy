"""
Study Notes API Endpoints (Week 3-4)

Routes for accessing Dr. Amir OSCE study notes from /ICRP_OSCE_Preparation/
- GET /api/v1/study-notes - List all study notes (filterable)
- GET /api/v1/study-notes/{note_id} - Get single study note
- POST /api/v1/study-notes/bulk-import - Import 106 study notes (admin only)

CONTENT SOURCE:
- 106 markdown files from /ICRP_OSCE_Preparation/
- Dr. Amir's 5 Ps Framework content
- Cross-referenced with OSCEs and MCQs
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.db.base import get_db
from src.db.models import User, OSCEStudyNote, OSCE
from src.auth.dependencies import get_current_active_user


router = APIRouter(prefix="/study-notes", tags=["study-notes"])


# ============================================================================
# LIST STUDY NOTES
# ============================================================================


@router.get("/", response_model=List[dict])
async def list_study_notes(
    specialty: Optional[str] = None,
    amc_relevance: Optional[str] = Query(None, description="high, medium, or low"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all study notes with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty (Medicine, Surgery, Psychiatry, etc.)
    - amc_relevance: Filter by AMC Clinical Exam relevance (high, medium, low)
    - tags: Comma-separated tags (e.g., "red_flags,management,differential_diagnosis")
    - skip: Pagination offset
    - limit: Maximum results (default: 50, max: 100)

    Returns:
        List of study notes with metadata (excludes full markdown content for performance)

    Example response:
        [
            {
                "note_id": "STUDY-CARD-001",
                "title": "Cardiovascular Examination - Complete Guide",
                "specialty": "Medicine",
                "word_count": 3500,
                "reading_time_minutes": 18,
                "topics": ["Cardiovascular", "Physical Examination"],
                "tags": ["systematic_examination", "amc_exam", "inspection_palpation_percussion_auscultation"],
                "amc_relevance": "high",
                "related_osce_count": 5
            },
            ...
        ]
    """
    # Build query
    query = db.query(OSCEStudyNote).filter(OSCEStudyNote.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(OSCEStudyNote.specialty == specialty)

    if amc_relevance:
        query = query.filter(OSCEStudyNote.amc_relevance == amc_relevance)

    if tags:
        # Filter by tags (JSONB contains check)
        tag_list = [tag.strip() for tag in tags.split(",")]
        for tag in tag_list:
            query = query.filter(OSCEStudyNote.tags.contains([tag]))

    # Get total count for pagination metadata
    total = query.count()

    # Apply pagination
    limit = min(limit, 100)  # Max 100 results
    notes = query.offset(skip).limit(limit).all()

    # Format response (exclude full markdown for performance)
    results = []
    for note in notes:
        results.append(
            {
                "note_id": note.note_id,
                "title": note.title,
                "specialty": note.specialty,
                "word_count": note.word_count,
                "reading_time_minutes": note.reading_time_minutes,
                "topics": note.topics or [],
                "tags": note.tags or [],
                "amc_relevance": note.amc_relevance,
                "related_osce_count": len(note.related_osce_ids or []),
                "related_mcq_count": len(note.related_mcq_ids or []),
            }
        )

    return results


# ============================================================================
# GET SINGLE STUDY NOTE
# ============================================================================


@router.get("/{note_id}", response_model=dict)
async def get_study_note(
    note_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get single study note with full markdown content and related resources.

    Args:
        note_id: Study note identifier (e.g., "STUDY-CARD-001")

    Returns:
        {
            "note_id": "STUDY-CARD-001",
            "title": "Cardiovascular Examination - Complete Guide",
            "content_markdown": "# Cardiovascular Examination\n\n## Preparation...",
            "specialty": "Medicine",
            "word_count": 3500,
            "reading_time_minutes": 18,
            "topics": ["Cardiovascular", "Physical Examination"],
            "tags": ["systematic_examination", "amc_exam"],
            "amc_relevance": "high",
            "related_osces": [
                {"osce_id": "OSCE-CARD-001", "title": "Chest Pain Assessment"},
                ...
            ],
            "related_mcqs": [
                {"mcq_id": 45, "question_preview": "A 65-year-old male presents..."},
                ...
            ]
        }

    Raises:
        404: Study note not found or not published
    """
    # Get study note
    note = db.query(OSCEStudyNote).filter(OSCEStudyNote.note_id == note_id, OSCEStudyNote.is_published == True).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Study note {note_id} not found or not published"
        )

    # Get related OSCEs
    related_osces = []
    if note.related_osce_ids:
        osces = db.query(OSCE).filter(OSCE.id.in_(note.related_osce_ids)).all()
        for osce in osces:
            related_osces.append({"osce_id": osce.osce_id, "title": osce.station_title, "specialty": osce.specialty.value})

    # Get related MCQs (placeholder - implement when MCQ linking is done)
    related_mcqs = []

    return {
        "note_id": note.note_id,
        "title": note.title,
        "content_markdown": note.content_markdown,
        "specialty": note.specialty,
        "word_count": note.word_count,
        "reading_time_minutes": note.reading_time_minutes,
        "topics": note.topics or [],
        "tags": note.tags or [],
        "amc_relevance": note.amc_relevance,
        "related_osces": related_osces,
        "related_mcqs": related_mcqs,
        "created_at": note.created_at.isoformat() if note.created_at else None,
        "updated_at": note.updated_at.isoformat() if note.updated_at else None,
    }


# ============================================================================
# GET STUDY NOTES BY SPECIALTY
# ============================================================================


@router.get("/by-specialty/{specialty}", response_model=List[dict])
async def get_study_notes_by_specialty(
    specialty: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all study notes for a specific specialty.

    Args:
        specialty: Medical specialty (e.g., "Medicine", "Surgery", "Psychiatry")

    Returns:
        List of study notes for that specialty (without full markdown content)

    Example:
        GET /api/v1/study-notes/by-specialty/Medicine
    """
    notes = db.query(OSCEStudyNote).filter(
        OSCEStudyNote.specialty == specialty, OSCEStudyNote.is_published == True
    ).all()

    results = []
    for note in notes:
        results.append(
            {
                "note_id": note.note_id,
                "title": note.title,
                "word_count": note.word_count,
                "reading_time_minutes": note.reading_time_minutes,
                "topics": note.topics or [],
                "amc_relevance": note.amc_relevance,
            }
        )

    return results
