#!/usr/bin/env python3
"""
Tests for MCP server tools and external API integration.
This version properly tests the actual server behavior without hard-coding results.
"""

import asyncio
import pytest
import sys
from pathlib import Path
from unittest.mock import patch, Mock, AsyncMock
import httpx

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

# Import the functions from the server module
import importlib.util
spec = importlib.util.spec_from_file_location("petting_zootopia", str(Path(__file__).parent.parent / "server" / "petting_zootopia.py"))
petting_zootopia = importlib.util.module_from_spec(spec)
spec.loader.exec_module(petting_zootopia)

# Get the functions from the module
greet = petting_zootopia.greet
duck = petting_zootopia.duck
dog = petting_zootopia.dog
cat = petting_zootopia.cat


class TestMCPTools:
    """Test individual MCP tools with CORRECT mocking."""
    
    @pytest.mark.asyncio
    async def test_greet_tool(self):
        """Test greeting functionality."""
        result = await greet("Alice")
        assert result == "Hello, Alice!"
        
        result = await greet("Bob")
        assert result == "Hello, Bob!"
        
        result = await greet("")
        assert result == "Hello, !"
    
    @pytest.mark.asyncio
    async def test_duck_tool_success(self):
        """Test duck tool with successful API response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock the async context manager properly
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "url": "https://random-d.uk/api/gifs/12.gif"
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await duck()
            assert result == "https://random-d.uk/api/gifs/12.gif"
    
    @pytest.mark.asyncio
    async def test_duck_tool_timeout(self):
        """Test duck tool with timeout - should return specific error message."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock timeout exception
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("Request timeout")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await duck()
            # Test the ACTUAL error message the server returns
            assert result == "Error: Request timed out while fetching duck"
    
    @pytest.mark.asyncio
    async def test_duck_tool_http_error(self):
        """Test duck tool with HTTP error - should return specific error message."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock HTTP error
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 404
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Not Found", request=Mock(), response=mock_response
            )
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await duck()
            # Test the ACTUAL error message the server returns
            assert result == "Error: HTTP 404 while fetching duck"
    
    @pytest.mark.asyncio
    async def test_duck_tool_general_exception(self):
        """Test duck tool with general exception - should return specific error message."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock general exception
            mock_client = AsyncMock()
            mock_client.get.side_effect = Exception("Network error")
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await duck()
            # Test the ACTUAL error message the server returns
            assert result == "Error fetching duck: Network error"
    
    @pytest.mark.asyncio
    async def test_dog_tool_success(self):
        """Test dog tool with successful API response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock the async context manager properly
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg"
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await dog()
            assert result == "https://images.dog.ceo/breeds/hound-afghan/n02088094_1003.jpg"
    
    @pytest.mark.asyncio
    async def test_cat_tool_success(self):
        """Test cat tool with successful API response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock the async context manager properly
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [
                {
                    "url": "https://cdn2.thecatapi.com/images/abc123.jpg"
                }
            ]
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await cat()
            assert result == "https://cdn2.thecatapi.com/images/abc123.jpg"


class TestMCPToolsErrorHandling:
    """Test that error handling works correctly - these should FAIL if server code is wrong."""
    
    @pytest.mark.asyncio
    async def test_duck_tool_handles_missing_url_field(self):
        """Test duck tool handles missing URL field in response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock response without 'url' field
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "message": "No URL here"
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await duck()
            # Should return the fallback message from server code
            assert result == "No duck URL found"
    
    @pytest.mark.asyncio
    async def test_dog_tool_handles_missing_message_field(self):
        """Test dog tool handles missing message field in response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock response without 'message' field
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "status": "success"
            }
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await dog()
            # Should return the fallback message from server code
            assert result == "No dog URL found"
    
    @pytest.mark.asyncio
    async def test_cat_tool_handles_empty_array(self):
        """Test cat tool handles empty array response."""
        with patch('httpx.AsyncClient') as mock_client_class:
            # Mock empty array response
            mock_client = AsyncMock()
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_response.raise_for_status.return_value = None
            mock_client.get.return_value = mock_response
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client_class.return_value.__aexit__.return_value = None
            
            result = await cat()
            # Should return the fallback message from server code
            assert result == "No cat URL found"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
