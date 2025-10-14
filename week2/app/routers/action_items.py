from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, status

from .. import db
from ..models import (
    ActionItemResponse,
    ExtractLLMRequest,
    ExtractRequest,
    ExtractResponse,
    MarkDoneRequest,
    MarkDoneResponse,
)
from ..services.extract import (
    extract_action_items_unified,
    extract_with_ollama_detailed,
    extract_with_ollama_simple,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/action-items", tags=["action-items"])


@router.post("/extract", response_model=ExtractResponse)
def extract(request: ExtractRequest) -> ExtractResponse:
    """
    Extract action items from text using the configured method.

    Args:
        request: Extraction request with text and options

    Returns:
        ExtractResponse with extracted action items

    Raises:
        HTTPException: If extraction fails
    """
    try:
        note_id: int | None = None
        if request.save_note:
            note_id = db.insert_note(request.text)

        items = extract_action_items_unified(request.text)
        ids = db.insert_action_items(items, note_id=note_id)

        action_items = [
            ActionItemResponse(
                id=item_id,
                text=item_text,
                done=False,
                created_at="",  # Will be filled by database
                note_id=note_id,
            )
            for item_id, item_text in zip(ids, items, strict=False)
        ]

        logger.info(f"Extracted {len(action_items)} action items")
        return ExtractResponse(note_id=note_id, items=action_items, method=None)

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Extraction failed: {str(e)}"
        ) from e


@router.post("/extract-llm", response_model=ExtractResponse)
def extract_llm(request: ExtractLLMRequest) -> ExtractResponse:
    """
    Extract action items from text using LLM methods.

    Args:
        request: LLM extraction request with text, method, and options

    Returns:
        ExtractResponse with extracted action items

    Raises:
        HTTPException: If extraction fails
    """
    try:
        note_id: int | None = None
        if request.save_note:
            note_id = db.insert_note(request.text)

        # Use the specified LLM method
        if request.method == "detailed":
            items = extract_with_ollama_detailed(request.text)
        else:  # default to simple
            items = extract_with_ollama_simple(request.text)

        ids = db.insert_action_items(items, note_id=note_id)

        action_items = [
            ActionItemResponse(
                id=item_id,
                text=item_text,
                done=False,
                created_at="",  # Will be filled by database
                note_id=note_id,
            )
            for item_id, item_text in zip(ids, items, strict=False)
        ]

        logger.info(
            f"Extracted {len(action_items)} action items using LLM method: {request.method}"
        )
        return ExtractResponse(note_id=note_id, items=action_items, method=request.method)

    except Exception as e:
        logger.error(f"LLM extraction failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM extraction failed: {str(e)}",
        ) from e


@router.get("", response_model=list[ActionItemResponse])
def list_all(note_id: int | None = None) -> list[ActionItemResponse]:
    """
    List all action items, optionally filtered by note ID.

    Args:
        note_id: Optional note ID to filter by

    Returns:
        List of action items

    Raises:
        HTTPException: If database operation fails
    """
    try:
        rows = db.list_action_items(note_id=note_id)
        action_items = [
            ActionItemResponse(
                id=r["id"],
                note_id=r["note_id"],
                text=r["text"],
                done=bool(r["done"]),
                created_at=r["created_at"],
            )
            for r in rows
        ]
        logger.info(f"Retrieved {len(action_items)} action items")
        return action_items
    except Exception as e:
        logger.error(f"Failed to list action items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list action items: {str(e)}",
        ) from e


@router.post("/{action_item_id}/done", response_model=MarkDoneResponse)
def mark_done(action_item_id: int, request: MarkDoneRequest) -> MarkDoneResponse:
    """
    Mark an action item as done or not done.

    Args:
        action_item_id: The ID of the action item to update
        request: Request with done status

    Returns:
        MarkDoneResponse with updated status

    Raises:
        HTTPException: If update fails
    """
    try:
        db.mark_action_item_done(action_item_id, request.done)
        logger.info(
            f"Marked action item {action_item_id} as {'done' if request.done else 'not done'}"
        )
        return MarkDoneResponse(id=action_item_id, done=request.done)
    except Exception as e:
        logger.error(f"Failed to mark action item {action_item_id} as done: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark action item as done: {str(e)}",
        ) from e
