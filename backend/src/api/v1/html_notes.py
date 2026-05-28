"""
HTML OSCE Notes API Endpoints

Routes for accessing pre-generated HTML OSCE notes (65 files).
Files are served as static content from /ICRP_OSCE_Preparation/

- GET /api/v1/html-notes - List all HTML notes (filterable)
- GET /api/v1/html-notes/{note_id} - Get single HTML note metadata
- GET /api/v1/html-notes/by-specialty/{specialty} - Get notes by specialty
- GET /api/v1/html-notes/{note_id}/content - Serve HTML file content
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from pathlib import Path

from src.db.base import get_db
from src.db.models import User, HTMLOSCENote
from src.auth.dependencies import get_current_active_user


router = APIRouter(prefix="/html-notes", tags=["html-notes"], redirect_slashes=False)


# Base path to HTML files
HTML_NOTES_BASE_PATH = Path(__file__).parent.parent.parent.parent.parent / 'ICRP_OSCE_Preparation'


# ============================================================================
# LIST HTML NOTES
# ============================================================================


@router.get("/", response_model=List[dict])
async def list_html_notes(
    specialty: Optional[str] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    List all HTML OSCE notes with optional filtering.

    Query parameters:
    - specialty: Filter by medical specialty
    - category: Filter by category (History, Physical Examination, Emergency, etc.)
    - skip: Pagination offset
    - limit: Maximum results (default: 100)

    Returns:
        List of HTML notes with metadata

    Example response:
        [
            {
                "note_id": "HTML-MED-001",
                "title": "Emergency OSCE Notes - Anaphylaxis Management",
                "specialty": "Medicine",
                "category": "Emergency",
                "file_size_kb": 45,
                "estimated_reading_minutes": 8,
                "topics": ["Anaphylaxis", "Emergency Management", "ABCDE Approach"],
                "preview_text": "Emergency OSCE Notes - Anaphylaxis Management..."
            },
            ...
        ]
    """
    # Build query
    query = db.query(HTMLOSCENote).filter(HTMLOSCENote.is_published == True)

    # Apply filters
    if specialty:
        query = query.filter(HTMLOSCENote.specialty == specialty)

    if category:
        query = query.filter(HTMLOSCENote.category == category)

    # Apply pagination
    notes = query.offset(skip).limit(limit).all()

    # Format response
    results = []
    for note in notes:
        results.append(
            {
                "note_id": note.note_id,
                "title": note.title,
                "specialty": note.specialty,
                "category": note.category,
                "file_size_kb": note.file_size_kb,
                "estimated_reading_minutes": note.estimated_reading_minutes,
                "topics": note.topics or [],
                "preview_text": note.preview_text,
            }
        )

    return results


# ============================================================================
# GET SINGLE HTML NOTE METADATA
# ============================================================================


@router.get("/{note_id}", response_model=dict)
async def get_html_note(
    note_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get single HTML note metadata (without content).

    Args:
        note_id: HTML note identifier (e.g., "HTML-MED-001")

    Returns:
        Metadata including title, specialty, category, topics, file path

    Raises:
        404: Note not found or not published
    """
    note = db.query(HTMLOSCENote).filter(
        HTMLOSCENote.note_id == note_id,
        HTMLOSCENote.is_published == True
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HTML note {note_id} not found or not published"
        )

    return {
        "note_id": note.note_id,
        "title": note.title,
        "file_path": note.file_path,
        "specialty": note.specialty,
        "category": note.category,
        "topics": note.topics or [],
        "preview_text": note.preview_text,
        "file_size_kb": note.file_size_kb,
        "estimated_reading_minutes": note.estimated_reading_minutes,
        "related_osce_ids": note.related_osce_ids or [],
        "created_at": note.created_at.isoformat() if note.created_at else None,
    }


# ============================================================================
# GET HTML NOTE CONTENT (Serve HTML File)
# ============================================================================


@router.get("/{note_id}/content", response_class=HTMLResponse)
async def get_html_note_content(
    note_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Serve HTML note content (actual HTML file).

    Args:
        note_id: HTML note identifier (e.g., "HTML-MED-001")

    Returns:
        Raw HTML content with embedded CSS

    Raises:
        404: Note not found, not published, or file doesn't exist
    """
    # Get note metadata
    note = db.query(HTMLOSCENote).filter(
        HTMLOSCENote.note_id == note_id,
        HTMLOSCENote.is_published == True
    ).first()

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HTML note {note_id} not found or not published"
        )

    # Construct file path
    html_file_path = HTML_NOTES_BASE_PATH / note.file_path

    if not html_file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"HTML file not found: {note.file_path}"
        )

    # Read and return HTML content
    try:
        html_content = html_file_path.read_text(encoding='utf-8')
        return HTMLResponse(content=html_content, status_code=200)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reading HTML file: {str(e)}"
        )


# ============================================================================
# GET HTML NOTES BY SPECIALTY
# ============================================================================


@router.get("/by-specialty/{specialty}", response_model=List[dict])
async def get_html_notes_by_specialty(
    specialty: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get all HTML notes for a specific specialty.

    Args:
        specialty: Medical specialty (e.g., "Medicine", "Surgery", "Psychiatry")

    Returns:
        List of HTML notes for that specialty

    Example:
        GET /api/v1/html-notes/by-specialty/Medicine
    """
    notes = db.query(HTMLOSCENote).filter(
        HTMLOSCENote.specialty == specialty,
        HTMLOSCENote.is_published == True
    ).all()

    results = []
    for note in notes:
        results.append(
            {
                "note_id": note.note_id,
                "title": note.title,
                "category": note.category,
                "file_size_kb": note.file_size_kb,
                "estimated_reading_minutes": note.estimated_reading_minutes,
                "topics": note.topics or [],
            }
        )

    return results


# ============================================================================
# GET SPECIALTY LIST
# ============================================================================


@router.get("/specialties/list", response_model=List[dict])
async def list_specialties(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Get list of all specialties with note counts.

    Returns:
        [
            {"specialty": "Medicine", "count": 15},
            {"specialty": "Surgery", "count": 7},
            ...
        ]
    """
    from sqlalchemy import func

    results = db.query(
        HTMLOSCENote.specialty,
        func.count(HTMLOSCENote.id).label('count')
    ).filter(
        HTMLOSCENote.is_published == True
    ).group_by(
        HTMLOSCENote.specialty
    ).all()

    return [{"specialty": r.specialty, "count": r.count} for r in results]
