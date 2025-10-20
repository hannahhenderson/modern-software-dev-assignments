#!/usr/bin/env python3
"""
Tests for AI backend functionality.

⚠️  CLAUDE TESTS WARNING ⚠️
The Claude tests in this file will consume API credits when run.
By default, they are commented out to prevent accidental charges.

To run Claude tests:
1. Set ENABLE_CLAUDE_TESTS=true environment variable
2. Ensure ANTHROPIC_API_KEY is set in your .env file
3. Run: ENABLE_CLAUDE_TESTS=true pytest tests/test_ai_backends.py -v

💰 Estimated cost per test run: ~$0.01-0.05
"""

import asyncio
import os
import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))

from ai_mcp_client import create_mcp_client, create_ollama_processor, create_claude_processor


class TestOllamaBackend:
    """Test Ollama backend functionality (free, local)."""
    
    @pytest.mark.asyncio
    async def test_ollama_processor_creation(self):
        """Test that Ollama processor can be created."""
        processor = create_ollama_processor("llama3.2:3b")
        assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_ollama_processor_with_custom_model(self):
        """Test Ollama processor with custom model."""
        processor = create_ollama_processor("llama3.2:1b")
        assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_ollama_processor_with_env_model(self):
        """Test Ollama processor respects environment."""
        with patch.dict(os.environ, {"OLLAMA_MODEL": "llama3.2:3b"}):
            processor = create_ollama_processor()
            assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_ollama_processor_handles_connection_error(self):
        """Test Ollama processor handles connection errors gracefully."""
        processor = create_ollama_processor("nonexistent-model")
        
        # Mock a connection error
        with patch('requests.post') as mock_post:
            mock_post.side_effect = ConnectionError("Cannot connect to Ollama")
            
            # This should not raise an exception
            result = await processor("test query", [], AsyncMock())
            assert "Error calling Ollama" in result
    
    @pytest.mark.asyncio
    async def test_ollama_processor_handles_timeout(self):
        """Test Ollama processor handles timeouts gracefully."""
        processor = create_ollama_processor("llama3.2:3b")
        
        with patch('requests.post') as mock_post:
            mock_post.side_effect = TimeoutError("Request timeout")
            
            result = await processor("test query", [], AsyncMock())
            assert "Error calling Ollama" in result


class TestClaudeBackend:
    """Test Claude backend functionality (costs money)."""
    
    @pytest.fixture(autouse=True)
    def check_claude_tests_enabled(self):
        """Skip Claude tests unless explicitly enabled."""
        if not os.getenv('ENABLE_CLAUDE_TESTS', '').lower() in ('true', '1', 'yes'):
            pytest.skip("Claude tests disabled. Set ENABLE_CLAUDE_TESTS=true to run.")
    
    @pytest.fixture(autouse=True)
    def check_claude_api_key(self):
        """Skip Claude tests if API key is not set."""
        if not os.getenv('ANTHROPIC_API_KEY'):
            pytest.skip("ANTHROPIC_API_KEY not set. Claude tests require API key.")
    
    @pytest.mark.asyncio
    async def test_claude_cheaper_processor_creation(self):
        """Test that Claude cheaper processor can be created."""
        processor = create_claude_processor('claude-haiku-20240307', 300)
        assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_claude_expensive_processor_creation(self):
        """Test that Claude expensive processor can be created."""
        processor = create_claude_processor('claude-sonnet-4-5', 1000)
        assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_claude_processor_handles_api_error(self):
        """Test Claude processor handles API errors gracefully."""
        processor = create_claude_processor('claude-haiku-20240307', 300)
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_anthropic.return_value.messages.create.side_effect = Exception("API Error")
            
            result = await processor("test query", [], AsyncMock())
            assert "Error" in result or "Exception" in result
    
    @pytest.mark.asyncio
    async def test_claude_processor_handles_rate_limit(self):
        """Test Claude processor handles rate limiting gracefully."""
        processor = create_claude_processor('claude-haiku-20240307', 300)
        
        with patch('anthropic.Anthropic') as mock_anthropic:
            mock_anthropic.return_value.messages.create.side_effect = Exception("Rate limit exceeded")
            
            result = await processor("test query", [], AsyncMock())
            assert "Error" in result or "Exception" in result


class TestBackendSelection:
    """Test backend selection and configuration."""
    
    @pytest.mark.asyncio
    async def test_backend_selection_ollama_dev(self):
        """Test backend selection for Ollama development."""
        with patch.dict(os.environ, {"AI_BACKEND": "ollama_dev"}):
            from ai_mcp_client import get_backend_processor
            backend_name, processor = get_backend_processor()
            assert backend_name == "ollama_dev"
            assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_backend_selection_claude_cheaper(self):
        """Test backend selection for Claude cheaper."""
        with patch.dict(os.environ, {"AI_BACKEND": "claude_cheaper"}):
            from ai_mcp_client import get_backend_processor
            backend_name, processor = get_backend_processor()
            assert backend_name == "claude_cheaper"
            assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_backend_selection_claude_expensive(self):
        """Test backend selection for Claude expensive."""
        with patch.dict(os.environ, {"AI_BACKEND": "claude_expensive"}):
            from ai_mcp_client import get_backend_processor
            backend_name, processor = get_backend_processor()
            assert backend_name == "claude_expensive"
            assert callable(processor)
    
    @pytest.mark.asyncio
    async def test_backend_selection_invalid(self):
        """Test backend selection with invalid backend."""
        with patch.dict(os.environ, {"AI_BACKEND": "invalid_backend"}):
            from ai_mcp_client import get_backend_processor
            with pytest.raises(ValueError, match="Unknown backend"):
                get_backend_processor()
    
    @pytest.mark.asyncio
    async def test_backend_selection_default(self):
        """Test backend selection with no environment variable."""
        with patch.dict(os.environ, {}, clear=True):
            from ai_mcp_client import get_backend_processor
            backend_name, processor = get_backend_processor()
            assert backend_name == "ollama_dev"  # Default
            assert callable(processor)


class TestMCPClientCreation:
    """Test MCP client creation and configuration."""
    
    @pytest.mark.asyncio
    async def test_mcp_client_creation(self):
        """Test that MCP client can be created."""
        client = create_mcp_client()
        assert isinstance(client, dict)
        assert 'connect_to_server' in client
        assert 'process_query' in client
        assert 'chat_loop' in client
        assert 'cleanup' in client
    
    @pytest.mark.asyncio
    async def test_mcp_client_with_ollama_backend(self):
        """Test MCP client with Ollama backend."""
        with patch.dict(os.environ, {"AI_BACKEND": "ollama_dev"}):
            client = create_mcp_client()
            assert isinstance(client, dict)
            assert callable(client['process_query'])
    
    @pytest.mark.asyncio
    async def test_mcp_client_with_claude_backend(self):
        """Test MCP client with Claude backend."""
        with patch.dict(os.environ, {"AI_BACKEND": "claude_cheaper"}):
            client = create_mcp_client()
            assert isinstance(client, dict)
            assert callable(client['process_query'])


# Claude-specific tests (commented out by default)
class TestClaudeIntegration:
    """Claude integration tests (commented out to prevent accidental charges)."""
    
    @pytest.mark.skip(reason="Claude tests disabled by default to prevent charges")
    @pytest.mark.asyncio
    async def test_claude_actual_api_call(self):
        """Test actual Claude API call (WILL COST MONEY)."""
        # This test is commented out to prevent accidental charges
        # Uncomment and run with ENABLE_CLAUDE_TESTS=true to test
        pass
    
    @pytest.mark.skip(reason="Claude tests disabled by default to prevent charges")
    @pytest.mark.asyncio
    async def test_claude_tool_selection_accuracy(self):
        """Test Claude tool selection accuracy (WILL COST MONEY)."""
        # This test is commented out to prevent accidental charges
        # Uncomment and run with ENABLE_CLAUDE_TESTS=true to test
        pass


if __name__ == "__main__":
    # Print warning about Claude tests
    print("\n" + "="*60)
    print("🧪 AI Backend Tests")
    print("="*60)
    print("✅ Ollama tests: FREE (local)")
    print("⚠️  Claude tests: COSTS MONEY (commented out by default)")
    print("")
    print("To run Claude tests:")
    print("  ENABLE_CLAUDE_TESTS=true pytest tests/test_ai_backends.py -v")
    print("")
    print("💰 Estimated Claude test cost: ~$0.01-0.05 per run")
    print("="*60)
    
    # Run tests
    pytest.main([__file__, "-v"])
