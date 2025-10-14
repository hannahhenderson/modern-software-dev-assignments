"""Input validation for action item extraction."""

from __future__ import annotations

import logging
import re
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
        ValueError: If text is invalid or too long
        TypeError: If text is not a string-like object
    """
    if text is None:
        raise ValueError("Text cannot be None")

    if not isinstance(text, (str, bytes)):
        raise TypeError(f"Expected string or bytes, got {type(text).__name__}")

    # Convert bytes to string if needed
    if isinstance(text, bytes):
        try:
            text = text.decode("utf-8")
        except UnicodeDecodeError as e:
            raise ValueError(f"Invalid UTF-8 encoding: {e}") from e

    # Normalize whitespace and remove control characters except newlines and tabs
    normalized = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", text.strip())

    if not normalized:
        logger.debug("Empty text input provided after normalization")
        return ""

    # Check for reasonable length (prevent abuse)
    max_length = 1_000_000  # 1MB limit
    if len(normalized) > max_length:
        raise ValueError(f"Text too long: {len(normalized)} characters (max: {max_length:,})")

    # Check for suspicious patterns that might indicate injection attempts
    suspicious_patterns = [
        r"<script[^>]*>",
        r"javascript:",
        r"data:text/html",
        r"vbscript:",
        r"on\w+\s*=",
    ]

    for pattern in suspicious_patterns:
        if re.search(pattern, normalized, re.IGNORECASE):
            logger.warning(f"Suspicious pattern detected in input: {pattern}")
            # Don't raise an error, but log the warning
            break

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
        ValueError: If items list is too large
    """
    if not isinstance(items, list):
        raise TypeError(f"Expected list, got {type(items).__name__}")

    # Prevent abuse with too many items
    max_items = 1000
    if len(items) > max_items:
        raise ValueError(f"Too many action items: {len(items)} (max: {max_items})")

    cleaned = []
    max_item_length = 1000  # Reasonable length limit per item

    for i, item in enumerate(items):
        if not isinstance(item, str):
            logger.warning(f"Skipping non-string item at index {i}: {type(item).__name__}")
            continue

        # Clean and validate each item
        cleaned_item = item.strip()

        if not cleaned_item:
            logger.debug(f"Skipping empty item at index {i}")
            continue

        if len(cleaned_item) > max_item_length:
            logger.warning(
                f"Skipping overly long action item at index {i}: "
                f"{len(cleaned_item)} chars (max: {max_item_length})"
            )
            continue

        # Additional validation: check for reasonable content
        if _is_valid_action_item(cleaned_item):
            cleaned.append(cleaned_item)
        else:
            logger.debug(f"Skipping item that doesn't look like an action: {cleaned_item[:50]}...")

    return cleaned


def _is_valid_action_item(item: str) -> bool:
    """
    Check if an item looks like a valid action item.

    Args:
        item: The action item text to validate

    Returns:
        True if the item appears to be a valid action item
    """
    # Must have at least 3 characters
    if len(item) < 3:
        return False

    # Must contain at least one letter
    if not re.search(r"[a-zA-Z]", item):
        return False

    # Should not be just punctuation or numbers
    if re.match(r"^[\d\s\W]+$", item):
        return False

    # Should not be just whitespace
    if not item.strip():
        return False

    return True
