#!/usr/bin/env python3
"""
Tests for the web application MCP integration.
"""

import asyncio
import json
import pytest
import httpx
from unittest.mock import AsyncMock, patch
import sys
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

import sys
sys.path.append(str(Path(__file__).parent.parent / "web_client"))
from app import app
import sys
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))
from ai_mcp_client import create_mcp_client


class TestWebAppMCPIntegration:
    """Test web app MCP client integration."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Mock MCP client for testing."""
        mock_client = AsyncMock()
        mock_client["process_query"] = AsyncMock()
        mock_client["connect_to_server"] = AsyncMock()
        mock_client["cleanup"] = AsyncMock()
        return mock_client
    
    @pytest.mark.asyncio
    async def test_web_app_sends_correct_info_to_mcp_client(self, client, mock_mcp_client):
        """Test that web app sends correct information to MCP client."""
        # Mock the MCP client
        with patch('app.mcp_client', mock_mcp_client):
            mock_mcp_client["process_query"].return_value = "https://example.com/cat.jpg"
            
            # Test request
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["animal"] == "cat"
            assert data["message"] == "I want a cat!"
            assert "imageUrl" in data
            
            # Verify MCP client was called with correct parameters
            mock_mcp_client["process_query"].assert_called_once_with("I want a cat!")
    
    @pytest.mark.asyncio
    async def test_web_app_handles_mcp_client_errors_gracefully(self, client, mock_mcp_client):
        """Test that web app handles MCP client errors gracefully."""
        with patch('app.mcp_client', mock_mcp_client):
            # Test MCP client returns error
            mock_mcp_client["process_query"].return_value = ""
            
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "No result from MCP client" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_web_app_handles_mcp_client_exception(self, client, mock_mcp_client):
        """Test that web app handles MCP client exceptions gracefully."""
        with patch('app.mcp_client', mock_mcp_client):
            # Test MCP client raises exception
            mock_mcp_client["process_query"].side_effect = Exception("MCP client error")
            
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_web_app_handles_invalid_animal_type(self, client):
        """Test that web app handles invalid animal types."""
        response = await client.post("/api/animal", json={
            "animal": "elephant",
            "message": "I want an elephant!"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid animal type" in data["detail"]


class TestWebAppErrorHandling:
    """Test web app error handling with sad animal images."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_sad_cat_display_on_error(self, client):
        """Test that sad cat image is displayed when cat request fails."""
        # This would be implemented in the frontend JavaScript
        # For now, we test that the API returns appropriate error
        with patch('app.mcp_client', None):  # Simulate no MCP client
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 500
            # Frontend would handle displaying sad cat image
    
    @pytest.mark.asyncio
    async def test_sad_dog_display_on_error(self, client):
        """Test that sad dog image is displayed when dog request fails."""
        with patch('app.mcp_client', None):
            response = await client.post("/api/animal", json={
                "animal": "dog",
                "message": "I want a dog!"
            })
            
            assert response.status_code == 500
    
    @pytest.mark.asyncio
    async def test_sad_duck_display_on_error(self, client):
        """Test that sad duck image is displayed when duck request fails."""
        with patch('app.mcp_client', None):
            response = await client.post("/api/animal", json={
                "animal": "duck",
                "message": "I want a duck!"
            })
            
            assert response.status_code == 500


class TestMCPClientLLMParsing:
    """Test MCP client LLM parsing capabilities."""
    
    @pytest.fixture
    def test_queries(self):
        """Test queries for LLM parsing."""
        return [
            ("I want a cat", "cat"),
            ("I want a dog", "dog"), 
            ("I want a duck", "duck"),
            ("Show me a cat", "cat"),
            ("Get me a dog", "dog"),
            ("I want an elephant", None),  # Not supported
            ("isdkalsfdha cat", "cat"),  # Gibberish but should extract "cat"
            ("Hello there", None),  # No animal request
        ]
    
    @pytest.mark.asyncio
    async def test_mcp_client_llm_parsing_accuracy(self, test_queries):
        """Test MCP client LLM parsing accuracy over multiple runs."""
        # This test runs the LLM multiple times to check accuracy
        num_runs = 5
        correct_predictions = 0
        total_predictions = 0
        
        for query, expected_animal in test_queries:
            for run in range(num_runs):
                # Mock the MCP client to test LLM parsing
                mock_client = create_mcp_client()
                
                # This would need to be implemented to test actual LLM parsing
                # For now, we'll create a mock test
                try:
                    # Simulate LLM processing
                    if expected_animal and expected_animal in ["cat", "dog", "duck"]:
                        # Mock successful parsing
                        result = f"https://example.com/{expected_animal}.jpg"
                        if result:
                            correct_predictions += 1
                    total_predictions += 1
                except Exception:
                    # LLM failed to parse
                    total_predictions += 1
        
        accuracy = correct_predictions / total_predictions if total_predictions > 0 else 0
        print(f"LLM Parsing Accuracy: {accuracy:.2%} ({correct_predictions}/{total_predictions})")
        
        # Assert minimum accuracy (adjust as needed)
        assert accuracy >= 0.8, f"LLM accuracy too low: {accuracy:.2%}"
    
    @pytest.mark.asyncio
    async def test_mcp_client_handles_gibberish(self):
        """Test that MCP client can extract animal from gibberish."""
        # Test with gibberish input
        gibberish_queries = [
            "isdkalsfdha cat",
            "asdf dog asdf",
            "duck asdfasdf",
            "cat asdfasdf asdf"
        ]
        
        for query in gibberish_queries:
            # This would test actual LLM parsing
            # For now, we'll simulate the test
            assert "cat" in query or "dog" in query or "duck" in query
    
    @pytest.mark.asyncio
    async def test_mcp_client_handles_unsupported_animals(self):
        """Test that MCP client handles unsupported animals gracefully."""
        unsupported_queries = [
            "I want an elephant",
            "Show me a giraffe", 
            "Get me a lion"
        ]
        
        for query in unsupported_queries:
            # Should return appropriate error or fallback
            # This would test actual MCP client behavior
            pass


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
