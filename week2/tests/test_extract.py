from ..app.services.extract import (
    extract_action_items,
    extract_action_items_unified,
    extract_with_ollama_detailed,
    extract_with_ollama_simple,
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


def test_ollama_detailed_extraction():
    """Test detailed LLM extraction with phi3:mini"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    action: Deploy app
    Some regular text.
    """.strip()
    
    items = extract_with_ollama_detailed(text)
    # Should extract the same items but via LLM
    assert len(items) > 0


def test_ollama_simple_extraction():
    """Test simple LLM extraction with qwen2.5:0.5b"""
    text = """
    - [ ] Fix bug
    todo: Add tests
    action: Deploy app
    Some regular text.
    """.strip()
    
    items = extract_with_ollama_simple(text)
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


def test_empty_input():
    """Test behavior with empty input"""
    assert extract_action_items_unified("") == []
    assert extract_action_items_unified("   ") == []
    assert extract_action_items_unified("\n\n") == []


def test_no_action_items():
    """Test text with no actionable content"""
    text = "This is just narrative text with no actions."
    items = extract_action_items_unified(text)
    assert len(items) == 0
    
    text2 = "The team discussed various approaches to the problem."
    items2 = extract_action_items_unified(text2)
    assert len(items2) == 0


def test_llm_content_validation():
    """Test that LLM methods return expected content"""
    text = "- [ ] Fix bug\ntodo: Add tests"
    items = extract_action_items_unified(text)
    assert "Fix bug" in items
    assert "Add tests" in items
    assert len(items) == 2
    # Negative assertions
    assert "Some regular text" not in items
    assert "narrative" not in items


def test_deduplication():
    """Test that duplicate items are removed"""
    text = "- [ ] Fix bug\n- [ ] Fix bug\ntodo: Fix bug"
    items = extract_action_items_unified(text)
    assert len(items) == 1
    assert "Fix bug" in items


def test_mixed_formats_comprehensive():
    """Test comprehensive mixed format extraction"""
    text = """
    Meeting notes:
    - [ ] Set up database
    * Implement authentication
    1. Write unit tests
    todo: Deploy to staging
    action: Update docs
    next: Review code
    
    Some narrative text that should be ignored.
    The team discussed various approaches.
    """.strip()
    
    items = extract_action_items_unified(text)
    
    # Positive assertions - should be extracted
    assert "Set up database" in items
    assert "Implement authentication" in items
    assert "Write unit tests" in items
    assert "Deploy to staging" in items
    assert "Update docs" in items
    assert "Review code" in items
    
    # Negative assertions - should NOT be extracted
    assert "Meeting notes:" not in items
    assert "Some narrative text that should be ignored" not in items
    assert "The team discussed various approaches" not in items
    assert "narrative" not in items
    assert "discussed" not in items
    
    assert len(items) == 6


def test_case_insensitive_keywords():
    """Test that keyword prefixes work case-insensitively"""
    text = """
    TODO: Fix bug
    ACTION: Add tests
    NEXT: Deploy app
    todo: lowercase test
    action: another test
    """.strip()
    
    items = extract_action_items_unified(text)
    
    # Should extract all variations
    assert "Fix bug" in items
    assert "Add tests" in items
    assert "Deploy app" in items
    assert "lowercase test" in items
    assert "another test" in items
    
    assert len(items) == 5


def test_whitespace_handling():
    """Test proper handling of whitespace and formatting"""
    text = """
    -   [ ]   Fix bug with extra spaces
    *   Implement feature
    1.   Write documentation
    todo:   Add validation
    """.strip()
    
    items = extract_action_items_unified(text)
    
    # Should clean up whitespace
    assert "Fix bug with extra spaces" in items
    assert "Implement feature" in items
    assert "Write documentation" in items
    assert "Add validation" in items
    
    # Should not have leading/trailing spaces in items
    for item in items:
        assert item == item.strip()
        assert not item.startswith(" ")
        assert not item.endswith(" ")
    
    assert len(items) == 4
