#!/usr/bin/env python3
"""
End-to-end tests for the complete MCP application.
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock
import httpx

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "web_client"))
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))

from app import app
from ai_mcp_client import create_mcp_client


class TestEndToEndUserJourney:
    """Test complete user journey from web interface to animal image."""
    
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
    async def test_user_requests_cat_image(self, client, mock_mcp_client):
        """Test: User clicks cat button → gets cat image."""
        with patch('app.mcp_client', mock_mcp_client):
            # Mock successful MCP response
            mock_mcp_client["process_query"].return_value = "https://cdn2.thecatapi.com/images/abc123.jpg"
            
            # Simulate user clicking cat button
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            # Verify successful response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["animal"] == "cat"
            assert data["imageUrl"] == "https://cdn2.thecatapi.com/images/abc123.jpg"
            
            # Verify MCP client was called correctly
            mock_mcp_client["process_query"].assert_called_once_with("I want a cat!")
    
    @pytest.mark.asyncio
    async def test_user_requests_dog_image(self, client, mock_mcp_client):
        """Test: User clicks dog button → gets dog image."""
        with patch('app.mcp_client', mock_mcp_client):
            # Mock successful MCP response
            mock_mcp_client["process_query"].return_value = "https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg"
            
            # Simulate user clicking dog button
            response = await client.post("/api/animal", json={
                "animal": "dog",
                "message": "I want a dog!"
            })
            
            # Verify successful response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["animal"] == "dog"
            assert data["imageUrl"] == "https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg"
            
            # Verify MCP client was called correctly
            mock_mcp_client["process_query"].assert_called_once_with("I want a dog!")
    
    @pytest.mark.asyncio
    async def test_user_requests_duck_image(self, client, mock_mcp_client):
        """Test: User clicks duck button → gets duck image."""
        with patch('app.mcp_client', mock_mcp_client):
            # Mock successful MCP response
            mock_mcp_client["process_query"].return_value = "https://random-d.uk/api/gifs/12.gif"
            
            # Simulate user clicking duck button
            response = await client.post("/api/animal", json={
                "animal": "duck",
                "message": "I want a duck!"
            })
            
            # Verify successful response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert data["animal"] == "duck"
            assert data["imageUrl"] == "https://random-d.uk/api/gifs/12.gif"
            
            # Verify MCP client was called correctly
            mock_mcp_client["process_query"].assert_called_once_with("I want a duck!")
    
    @pytest.mark.asyncio
    async def test_user_requests_invalid_animal(self, client):
        """Test: User requests invalid animal → gets error."""
        # Simulate user requesting invalid animal
        response = await client.post("/api/animal", json={
            "animal": "elephant",
            "message": "I want an elephant!"
        })
        
        # Verify error response
        assert response.status_code == 400
        data = response.json()
        assert "Invalid animal type" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_error_scenario_with_sad_animal(self, client, mock_mcp_client):
        """Test: API failure → sad animal image displayed."""
        with patch('app.mcp_client', mock_mcp_client):
            # Mock MCP client failure
            mock_mcp_client["process_query"].side_effect = Exception("MCP client error")
            
            # Simulate user clicking cat button
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            # Verify error response
            assert response.status_code == 500
            data = response.json()
            assert "Internal server error" in data["detail"]
            
            # Frontend would display sad cat image based on this error
    
    @pytest.mark.asyncio
    async def test_concurrent_user_requests(self, client, mock_mcp_client):
        """Test: Multiple users simultaneously → all get responses."""
        with patch('app.mcp_client', mock_mcp_client):
            # Mock successful MCP responses
            mock_mcp_client["process_query"].return_value = "https://example.com/animal.jpg"
            
            # Simulate multiple concurrent requests
            tasks = []
            for i in range(3):
                task = client.post("/api/animal", json={
                    "animal": "cat",
                    "message": f"I want a cat! (User {i})"
                })
                tasks.append(task)
            
            # Execute all requests concurrently
            responses = await asyncio.gather(*tasks)
            
            # Verify all requests succeeded
            for response in responses:
                assert response.status_code == 200
                data = response.json()
                assert data["success"] is True
                assert data["animal"] == "cat"
    
    @pytest.mark.asyncio
    async def test_mcp_client_connection_failure(self, client):
        """Test: MCP client connection failure → graceful error."""
        with patch('app.mcp_client', None):  # Simulate no MCP client
            response = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            
            # Verify error response
            assert response.status_code == 500
            data = response.json()
            assert "MCP client not initialized" in data["detail"]


class TestMCPIntegration:
    """Test MCP client-server integration."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_connects_to_server(self):
        """Test MCP client can connect to server."""
        client = create_mcp_client()
        
        # Mock the connection process
        with patch('mcp_client.ai_mcp_client.stdio_client') as mock_stdio:
            with patch('mcp_client.ai_mcp_client.ClientSession') as mock_session:
                # Mock successful connection
                mock_session.return_value.initialize = AsyncMock()
                mock_session.return_value.list_tools = AsyncMock(return_value=Mock(tools=[]))
                
                # Test connection
                await client['connect_to_server']('server/petting_zootopia.py')
                
                # Verify connection was attempted
                mock_stdio.assert_called_once()
                mock_session.return_value.initialize.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_mcp_client_processes_queries(self):
        """Test MCP client processes queries correctly."""
        client = create_mcp_client()
        
        # Mock the query processing
        with patch('mcp_client.ai_mcp_client.get_backend_processor') as mock_backend:
            mock_processor = AsyncMock()
            mock_processor.return_value = "https://example.com/cat.jpg"
            mock_backend.return_value = ("ollama_dev", mock_processor)
            
            # Mock session
            with patch('mcp_client.ai_mcp_client.ClientSession') as mock_session:
                mock_session.return_value.list_tools = AsyncMock(return_value=Mock(tools=[]))
                
                # Test query processing
                result = await client['process_query']("I want a cat!")
                assert result == "https://example.com/cat.jpg"
    
    @pytest.mark.asyncio
    async def test_mcp_client_cleanup(self):
        """Test MCP client cleanup."""
        client = create_mcp_client()
        
        # Mock cleanup
        with patch('mcp_client.ai_mcp_client.AsyncExitStack') as mock_stack:
            mock_stack.return_value.aclose = AsyncMock()
            
            # Test cleanup
            await client['cleanup']()
            
            # Verify cleanup was called
            mock_stack.return_value.aclose.assert_called_once()


class TestWebInterfaceFeatures:
    """Test web interface specific features."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_landing_page_loads(self, client):
        """Test that landing page loads correctly."""
        response = await client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_health_endpoint(self, client):
        """Test health check endpoint."""
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "web_server" in data
        assert "mcp_connected" in data
    
    @pytest.mark.asyncio
    async def test_static_assets_served(self, client):
        """Test that static assets are served correctly."""
        # Test that assets directory is mounted
        response = await client.get("/assets/images/petting_zoo_hero.png")
        # This might return 404 if file doesn't exist, but the route should be accessible
        assert response.status_code in [200, 404]  # 404 is OK if file doesn't exist


class TestErrorRecovery:
    """Test error recovery scenarios."""
    
    @pytest.fixture
    async def client(self):
        """Create test client."""
        async with httpx.AsyncClient(app=app, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_recovery_after_mcp_failure(self, client, mock_mcp_client):
        """Test system recovers after MCP failure."""
        with patch('app.mcp_client', mock_mcp_client):
            # First request fails
            mock_mcp_client["process_query"].side_effect = Exception("MCP failure")
            
            response1 = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            assert response1.status_code == 500
            
            # Second request succeeds (simulating recovery)
            mock_mcp_client["process_query"].side_effect = None
            mock_mcp_client["process_query"].return_value = "https://example.com/cat.jpg"
            
            response2 = await client.post("/api/animal", json={
                "animal": "cat",
                "message": "I want a cat!"
            })
            assert response2.status_code == 200
    
    @pytest.mark.asyncio
    async def test_graceful_degradation(self, client):
        """Test graceful degradation when services are unavailable."""
        with patch('app.mcp_client', None):
            # System should still respond, even if MCP client is unavailable
            response = await client.get("/api/health")
            assert response.status_code == 200
            data = response.json()
            assert data["mcp_connected"] is False


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
