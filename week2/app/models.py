"""Pydantic models for API request/response validation."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, validator


class ExtractRequest(BaseModel):
    """Request model for action item extraction."""

    text: str = Field(
        ..., min_length=1, max_length=1_000_000, description="Text to extract action items from"
    )
    save_note: bool = Field(default=False, description="Whether to save the text as a note")

    @validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate and normalize text input."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class ExtractLLMRequest(BaseModel):
    """Request model for LLM-based action item extraction."""

    text: str = Field(
        ..., min_length=1, max_length=1_000_000, description="Text to extract action items from"
    )
    method: Literal["simple", "detailed"] = Field(
        default="simple", description="LLM extraction method"
    )
    save_note: bool = Field(default=False, description="Whether to save the text as a note")

    @validator("text")
    def validate_text(cls, v: str) -> str:
        """Validate and normalize text input."""
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class ActionItemResponse(BaseModel):
    """Response model for action items."""

    id: int = Field(..., description="Action item ID")
    text: str = Field(..., description="Action item text")
    done: bool = Field(..., description="Whether the item is done")
    created_at: str = Field(..., description="Creation timestamp")
    note_id: int | None = Field(None, description="Associated note ID")


class ExtractResponse(BaseModel):
    """Response model for extraction operations."""

    note_id: int | None = Field(None, description="ID of the created note (if save_note was True)")
    items: list[ActionItemResponse] = Field(..., description="Extracted action items")
    method: str | None = Field(None, description="Extraction method used (for LLM requests)")


class NoteRequest(BaseModel):
    """Request model for creating notes."""

    content: str = Field(..., min_length=1, max_length=1_000_000, description="Note content")

    @validator("content")
    def validate_content(cls, v: str) -> str:
        """Validate and normalize note content."""
        if not v or not v.strip():
            raise ValueError("Note content cannot be empty")
        return v.strip()


class NoteResponse(BaseModel):
    """Response model for notes."""

    id: int = Field(..., description="Note ID")
    content: str = Field(..., description="Note content")
    created_at: str = Field(..., description="Creation timestamp")


class MarkDoneRequest(BaseModel):
    """Request model for marking action items as done."""

    done: bool = Field(..., description="Whether the item is done")


class MarkDoneResponse(BaseModel):
    """Response model for marking action items as done."""

    id: int = Field(..., description="Action item ID")
    done: bool = Field(..., description="Whether the item is done")


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str = Field(..., description="Error message")
    detail: str | None = Field(None, description="Additional error details")
    status_code: int = Field(..., description="HTTP status code")
