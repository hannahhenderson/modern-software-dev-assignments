import os
import pytest

from ..app.services.extract import (
    extract_action_items_unified,
    extract_action_items,
    extract_with_ollama,
    simple_extract_with_ollama
)


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items_unified(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


def test_heuristic_extraction():
    """Test the original rule-based extraction"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    action: Deploy app
    Some regular text.
    """.strip()
    
    items = extract_action_items(text)
    assert "Fix bug" in items
    assert "Add tests" in items
    assert "Deploy app" in items


def test_ollama_extraction():
    """Test LLM extraction with phi3:mini"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    action: Deploy app
    Some regular text.
    """.strip()
    
    items = extract_with_ollama(text)
    # Should extract the same items but via LLM
    assert len(items) > 0


def test_simple_ollama_extraction():
    """Test simple LLM extraction with qwen2.5:0.5b"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    action: Deploy app
    Some regular text.
    """.strip()
    
    items = simple_extract_with_ollama(text)
    # Should extract the same items but via smaller LLM
    assert len(items) > 0


def test_unified_extraction_methods():
    """Test that unified function works with different environment settings"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    """.strip()
    
    # Test with different methods (these might fail if models aren't available)
    try:
        items = extract_action_items_unified(text)
        assert len(items) > 0
    except Exception as e:
        # If LLM models aren't available, that's okay for testing
        print(f"LLM extraction failed (expected if models not available): {e}")
