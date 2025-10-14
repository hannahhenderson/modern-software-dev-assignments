#!/usr/bin/env python3
"""
Performance test script to compare extraction methods and models.
"""

import time
import os
from app.services.extract import (
    extract_action_items, 
    extract_with_ollama, 
    simple_extract_with_ollama,
    extract_action_items_unified
)

def test_performance():
    """Test performance of different extraction methods."""
    
    # Test text with various action item formats
    test_text = """
    Meeting Notes:
    
    - [ ] Fix the bug in the login system
    * Implement user authentication
    1. Update documentation
    2. Deploy to staging
    todo: Review code changes
    action: Schedule team meeting
    next: Test the new feature
    
    Other notes:
    The team discussed the project timeline and budget constraints.
    We need to coordinate with the design team.
    """
    
    methods = [
        ("heuristic", "heuristic"),
        ("ollama", "ollama"), 
        ("simple_ollama", "simple_ollama")
    ]
    
    models = ["qwen2.5:0.5b", "phi3:mini"]
    
    print("=== Performance Test Results ===\n")
    
    for method_name, method in methods:
        print(f"Method: {method_name}")
        print("-" * 40)
        
        # Test with different models
        for model in models:
            os.environ["LLM_MODEL"] = model
            os.environ["EXTRACTION_METHOD"] = method
            
            start_time = time.time()
            try:
                result = extract_action_items_unified(test_text)
                end_time = time.time()
                
                print(f"  Model: {model}")
                print(f"  Time: {end_time - start_time:.3f}s")
                print(f"  Results: {len(result)} items")
                print(f"  Items: {result}")
                print()
                
            except Exception as e:
                print(f"  Model: {model} - ERROR: {e}")
                print()
        
        print()

if __name__ == "__main__":
    test_performance()
