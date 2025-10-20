#!/bin/bash

# Test runner for Petting Zootopia MCP project

echo "🧪 Running Petting Zootopia Tests"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip install pytest pytest-asyncio httpx
fi

# Run web client tests (includes graceful failure tests)
echo "🌐 Testing Web Client App MCP Integration..."
pytest tests/test_web_app.py -v

echo ""
echo "🛠️ Testing MCP Server Tools..."
pytest tests/test_mcp_tools.py -v

echo ""
echo "🤖 Testing AI Backends (Ollama only)..."
pytest tests/test_ai_backends.py -v

echo ""
echo "🔄 Testing End-to-End User Journey..."
pytest tests/test_e2e.py -v

echo ""
echo "🧠 Testing MCP Client LLM Parsing..."
pytest tests/test_mcp_client_llm.py -v -s

echo ""
echo "✅ All tests completed!"
echo ""
echo "💡 To run Claude tests (costs money):"
echo "   ENABLE_CLAUDE_TESTS=true pytest tests/test_ai_backends.py -v"
