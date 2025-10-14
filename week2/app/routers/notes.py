from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..models import NoteRequest, NoteResponse

logger = logging.getLogger(__name__)


router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=NoteResponse)
def create_note(request: NoteRequest) -> NoteResponse:
    """
    Create a new note.

    Args:
        request: Note creation request with content

    Returns:
        NoteResponse with created note details

    Raises:
        HTTPException: If note creation fails
    """
    try:
        note_id = db.insert_note(request.content)
        note = db.get_note(note_id)
        if note is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Note was created but could not be retrieved",
            )

        logger.info(f"Created note with ID {note_id}")
        return NoteResponse(
            id=note["id"],
            content=note["content"],
            created_at=note["created_at"],
        )
    except Exception as e:
        logger.error(f"Failed to create note: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create note: {str(e)}",
        ) from e


@router.get("/{note_id}", response_model=NoteResponse)
def get_single_note(note_id: int) -> NoteResponse:
    """
    Get a specific note by ID.

    Args:
        note_id: The ID of the note to retrieve

    Returns:
        NoteResponse with note details

    Raises:
        HTTPException: If note is not found or retrieval fails
    """
    try:
        row = db.get_note(note_id)
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=f"Note with ID {note_id} not found"
            )

        logger.info(f"Retrieved note with ID {note_id}")
        return NoteResponse(
            id=row["id"],
            content=row["content"],
            created_at=row["created_at"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get note {note_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get note: {str(e)}",
        ) from e


@router.get("", response_model=list[NoteResponse])
def list_notes() -> list[NoteResponse]:
    """
    List all notes.

    Returns:
        List of all notes

    Raises:
        HTTPException: If listing fails
    """
    try:
        rows = db.list_notes()
        notes = [
            NoteResponse(
                id=row["id"],
                content=row["content"],
                created_at=row["created_at"],
            )
            for row in rows
        ]
        logger.info(f"Retrieved {len(notes)} notes")
        return notes
    except Exception as e:
        logger.error(f"Failed to list notes: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list notes: {str(e)}",
        ) from e
