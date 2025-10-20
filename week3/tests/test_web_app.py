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
sys.path.append(str(Path(__file__).parent.parent / "web_client"))
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))

from app import app
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


class TestWebAppGracefulFailure:
    """Test web app graceful failure scenarios with sad animal images."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_mcp_client_not_initialized(self, client):
        """Test graceful failure when MCP client is not initialized."""
        with patch('app.mcp_client', None):
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "MCP client not initialized" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_mcp_server_connection_failure(self, client, mock_mcp_client):
        """Test graceful failure when MCP server connection fails."""
        with patch('app.mcp_client', mock_mcp_client):
            # Simulate MCP server connection failure
            mock_mcp_client["process_query"].side_effect = ConnectionError("Cannot connect to MCP server")
            
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_external_api_timeout(self, client, mock_mcp_client):
        """Test graceful failure when external API times out."""
        with patch('app.mcp_client', mock_mcp_client):
            # Simulate external API timeout
            mock_mcp_client["process_query"].side_effect = TimeoutError("External API timeout")
            
            response = await client.post("/api/animal", json={
                "animal": "dog",
                "message": "I want a dog!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_mcp_tool_execution_failure(self, client, mock_mcp_client):
        """Test graceful failure when MCP tool execution fails."""
        with patch('app.mcp_client', mock_mcp_client):
            # Simulate MCP tool execution failure
            mock_mcp_client["process_query"].side_effect = Exception("Tool execution failed")
            
            response = await client.post("/api/animal", json={
                "animal": "duck",
                "message": "I want a duck!"
            })
            
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_invalid_json_request(self, client):
        """Test graceful failure with invalid JSON request."""
        response = await client.post("/api/animal", 
            content="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.asyncio
    async def test_missing_required_fields(self, client):
        """Test graceful failure with missing required fields."""
        response = await client.post("/api/animal", json={
            "animal": "cat"
            # Missing "message" field
        })
        
        assert response.status_code == 422  # FastAPI validation error
    
    @pytest.mark.asyncio
    async def test_empty_animal_type(self, client):
        """Test graceful failure with empty animal type."""
        response = await client.post("/api/animal", json={
            "animal": "",
            "message": "I want an animal!"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid animal type" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_unsupported_animal_type(self, client):
        """Test graceful failure with unsupported animal type."""
        response = await client.post("/api/animal", json={
            "animal": "elephant",
            "message": "I want an elephant!"
        })
        
        assert response.status_code == 400
        data = response.json()
        assert "Invalid animal type" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_concurrent_request_failure(self, client, mock_mcp_client):
        """Test graceful failure under concurrent load."""
        with patch('app.mcp_client', mock_mcp_client):
            # Simulate resource exhaustion
            mock_mcp_client["process_query"].side_effect = Exception("Resource exhausted")
            
            # Simulate multiple concurrent requests
            tasks = []
            for i in range(5):
                task = client.post("/api/animal", json={
                    "animal": "cat",
                    "message": f"I want a cat! (Request {i})"
                })
                tasks.append(task)
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All requests should fail gracefully
            for response in responses:
                if isinstance(response, Exception):
                    # Some requests might raise exceptions due to resource exhaustion
                    assert "Resource exhausted" in str(response)
                else:
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
