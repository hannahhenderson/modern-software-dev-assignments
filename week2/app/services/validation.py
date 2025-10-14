"""Input validation for action item extraction."""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)

def validate_text_input(text: Any) -> str:
    """
    Validate and normalize text input for extraction.
    
    Args:
        text: Input text to validate
        
    Returns:
        Normalized text string
        
    Raises:
        ValueError: If text is invalid
        TypeError: If text is not a string-like object
    """
    if text is None:
        raise ValueError("Text cannot be None")
    
    if not isinstance(text, (str, bytes)):
        raise TypeError(f"Expected string, got {type(text).__name__}")
    
    # Convert bytes to string if needed
    if isinstance(text, bytes):
        try:
            text = text.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 encoding: {e}") from e
    
    # Normalize whitespace
    normalized = text.strip()
    
    if not normalized:
        logger.debug("Empty text input provided")
        return ""
    
    # Check for reasonable length (prevent abuse)
    if len(normalized) > 1_000_000:  # 1MB limit
        raise ValueError(f"Text too long: {len(normalized)} characters (max: 1,000,000)")
    
    return normalized

def validate_action_items(items: list[str]) -> list[str]:
    """
    Validate and clean a list of action items.
    
    Args:
        items: List of action items to validate
        
    Returns:
        Cleaned list of action items
        
    Raises:
        TypeError: If items is not a list
    """
    if not isinstance(items, list):
        raise TypeError(f"Expected list, got {type(items).__name__}")
    
    cleaned = []
    for item in items:
        if not isinstance(item, str):
            logger.warning(f"Skipping non-string item: {type(item).__name__}")
            continue
        
        # Clean and validate each item
        cleaned_item = item.strip()
        if cleaned_item and len(cleaned_item) <= 1000:  # Reasonable length limit
            cleaned.append(cleaned_item)
        elif len(cleaned_item) > 1000:
            logger.warning(f"Skipping overly long action item: {len(cleaned_item)} chars")
    
    return cleaned
