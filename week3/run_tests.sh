#!/bin/bash

# Test runner for Petting Zootopia MCP project

echo "🧪 Running Petting Zootopia Tests"
echo ""

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "📦 Installing pytest..."
    pip install pytest pytest-asyncio httpx
fi

# Run web_client app tests
echo "🌐 Testing Web Client App MCP Integration..."
pytest tests/test_web_app.py -v

echo ""
echo "🤖 Testing MCP Client LLM Parsing..."
pytest tests/test_mcp_client_llm.py -v -s

echo ""
echo "✅ All tests completed!"
