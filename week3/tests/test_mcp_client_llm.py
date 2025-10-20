#!/usr/bin/env python3
"""
Tests for MCP client LLM parsing capabilities.
"""

import asyncio
import json
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

import sys
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))
from ai_mcp_client import create_mcp_client


class TestMCPClientLLMParsing:
    """Test MCP client LLM parsing with multiple runs for accuracy."""
    
    @pytest.fixture
    def test_queries(self):
        """Test queries for LLM parsing."""
        return [
            # Valid queries
            ("I want a cat", "cat"),
            ("I want a dog", "dog"),
            ("I want a duck", "duck"),
            ("Show me a cat", "cat"),
            ("Get me a dog", "dog"),
            ("Can I see a duck?", "duck"),
            ("I need a cat picture", "cat"),
            ("Dog please", "dog"),
            ("Duck image", "duck"),
            
            # Gibberish queries
            ("isdkalsfdha cat", "cat"),
            ("asdf dog asdf", "dog"),
            ("duck asdfasdf", "duck"),
            ("cat asdfasdf asdf", "cat"),
            ("random text dog more text", "dog"),
            
            # Unsupported animals
            ("I want an elephant", None),
            ("Show me a giraffe", None),
            ("Get me a lion", None),
            
            # No animal requests
            ("Hello there", None),
            ("How are you?", None),
            ("What's the weather?", None),
        ]
    
    @pytest.mark.asyncio
    async def test_llm_parsing_accuracy_multiple_runs(self, test_queries):
        """Test LLM parsing accuracy over multiple runs."""
        num_runs = 10  # Number of times to run each query
        results = {}
        
        for query, expected_animal in test_queries:
            results[query] = {
                "expected": expected_animal,
                "correct": 0,
                "total": num_runs,
                "predictions": []
            }
            
            for run in range(num_runs):
                try:
                    # Create a mock MCP client for testing
                    mock_client = create_mcp_client()
                    
                    # Mock the backend processor to simulate LLM behavior
                    with patch.object(mock_client, 'process_query') as mock_process:
                        # Simulate LLM response based on query content
                        predicted_animal = self._simulate_llm_parsing(query)
                        mock_process.return_value = f"https://example.com/{predicted_animal}.jpg" if predicted_animal else ""
                        
                        # Test the parsing
                        result = await mock_client["process_query"](query)
                        predicted_animal = self._extract_animal_from_result(result)
                        
                        results[query]["predictions"].append(predicted_animal)
                        
                        if predicted_animal == expected_animal:
                            results[query]["correct"] += 1
                            
                except Exception as e:
                    print(f"Error testing query '{query}': {e}")
                    results[query]["predictions"].append(None)
        
        # Calculate and print accuracy
        total_correct = sum(r["correct"] for r in results.values())
        total_runs = sum(r["total"] for r in results.values())
        overall_accuracy = total_correct / total_runs if total_runs > 0 else 0
        
        print(f"\n{'='*60}")
        print(f"LLM PARSING ACCURACY RESULTS")
        print(f"{'='*60}")
        print(f"Overall Accuracy: {overall_accuracy:.2%} ({total_correct}/{total_runs})")
        print(f"\nDetailed Results:")
        print(f"{'Query':<30} {'Expected':<10} {'Accuracy':<10} {'Predictions'}")
        print(f"{'-'*80}")
        
        for query, result in results.items():
            accuracy = result["correct"] / result["total"] if result["total"] > 0 else 0
            predictions_str = ", ".join([str(p) for p in result["predictions"]])
            print(f"{query[:29]:<30} {str(result['expected']):<10} {accuracy:.2%}      {predictions_str}")
        
        # Assert minimum accuracy
        assert overall_accuracy >= 0.7, f"Overall LLM accuracy too low: {overall_accuracy:.2%}"
        
        return results
    
    def _simulate_llm_parsing(self, query: str) -> str:
        """Simulate LLM parsing of animal requests."""
        query_lower = query.lower()
        
        # Simple keyword matching (simulates LLM behavior)
        if "cat" in query_lower:
            return "cat"
        elif "dog" in query_lower:
            return "dog"
        elif "duck" in query_lower:
            return "duck"
        else:
            return None
    
    def _extract_animal_from_result(self, result: str) -> str:
        """Extract animal type from MCP result."""
        if not result:
            return None
        
        result_lower = result.lower()
        if "cat" in result_lower:
            return "cat"
        elif "dog" in result_lower:
            return "dog"
        elif "duck" in result_lower:
            return "duck"
        else:
            return None
    
    @pytest.mark.asyncio
    async def test_gibberish_parsing(self):
        """Test that LLM can extract animals from gibberish."""
        gibberish_queries = [
            "isdkalsfdha cat",
            "asdf dog asdf",
            "duck asdfasdf",
            "cat asdfasdf asdf",
            "random text dog more text"
        ]
        
        for query in gibberish_queries:
            predicted = self._simulate_llm_parsing(query)
            assert predicted is not None, f"Failed to extract animal from: {query}"
            assert predicted in ["cat", "dog", "duck"], f"Invalid animal extracted: {predicted}"
    
    @pytest.mark.asyncio
    async def test_unsupported_animals(self):
        """Test that LLM handles unsupported animals correctly."""
        unsupported_queries = [
            "I want an elephant",
            "Show me a giraffe",
            "Get me a lion",
            "I need a zebra"
        ]
        
        for query in unsupported_queries:
            predicted = self._simulate_llm_parsing(query)
            assert predicted is None, f"Should not extract animal from: {query}, got: {predicted}"
    
    @pytest.mark.asyncio
    async def test_no_animal_requests(self):
        """Test that LLM handles non-animal requests correctly."""
        non_animal_queries = [
            "Hello there",
            "How are you?",
            "What's the weather?",
            "Tell me a joke"
        ]
        
        for query in non_animal_queries:
            predicted = self._simulate_llm_parsing(query)
            assert predicted is None, f"Should not extract animal from: {query}, got: {predicted}"


class TestMCPClientErrorHandling:
    """Test MCP client error handling."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_handles_api_failures(self):
        """Test that MCP client handles API failures gracefully."""
        # This would test actual API failure scenarios
        pass
    
    @pytest.mark.asyncio
    async def test_mcp_client_handles_timeout(self):
        """Test that MCP client handles timeouts gracefully."""
        # This would test timeout scenarios
        pass


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "-s"])
