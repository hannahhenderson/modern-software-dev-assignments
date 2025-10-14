#!/usr/bin/env python3
"""
Test script to compare different extraction methods.
Run with: python test_extraction_methods.py
"""

import os
import sys
sys.path.append('.')

from app.services.extract import (
    extract_action_items,
    extract_with_ollama, 
    simple_extract_with_ollama
)

def test_extraction_methods():
    """Compare all three extraction methods on the same text"""
    
    test_text = """
    Meeting notes from project planning:
    
    - [ ] Set up database connection
    * Implement user authentication
    1. Write unit tests for API
    todo: Deploy to staging environment
    action: Update documentation
    next: Review code with team
    
    Some regular narrative text that shouldn't be extracted.
    The team discussed various approaches to the problem.
    """.strip()
    
    print("=" * 60)
    print("EXTRACTION METHOD COMPARISON")
    print("=" * 60)
    print(f"Input text:\n{test_text}\n")
    
    # Test heuristic method
    print("1. HEURISTIC EXTRACTION (Rule-based):")
    print("-" * 40)
    try:
        heuristic_items = extract_action_items(test_text)
        for i, item in enumerate(heuristic_items, 1):
            print(f"  {i}. {item}")
        print(f"  Total: {len(heuristic_items)} items")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    # Test LLM method (phi3:mini)
    print("2. LLM EXTRACTION (phi3:mini):")
    print("-" * 40)
    try:
        ollama_items = extract_with_ollama(test_text)
        for i, item in enumerate(ollama_items, 1):
            print(f"  {i}. {item}")
        print(f"  Total: {len(ollama_items)} items")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    # Test simple LLM method (qwen2.5:0.5b)
    print("3. SIMPLE LLM EXTRACTION (qwen2.5:0.5b):")
    print("-" * 40)
    try:
        simple_items = simple_extract_with_ollama(test_text)
        for i, item in enumerate(simple_items, 1):
            print(f"  {i}. {item}")
        print(f"  Total: {len(simple_items)} items")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("To switch extraction methods, set the EXTRACTION_METHOD environment variable:")
    print("  export EXTRACTION_METHOD=heuristic     # Rule-based")
    print("  export EXTRACTION_METHOD=ollama       # LLM with phi3:mini")
    print("  export EXTRACTION_METHOD=simple_ollama # LLM with qwen2.5:0.5b")
    print()
    print("Current setting:", os.getenv("EXTRACTION_METHOD", "simple_ollama"))

if __name__ == "__main__":
    test_extraction_methods()
