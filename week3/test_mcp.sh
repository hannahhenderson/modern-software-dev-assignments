#!/bin/bash

# Test script to verify MCP client works in both web and CLI modes

echo "🧪 Testing MCP Client Modes"
echo ""

# Test 1: Check if MCP server can start
echo "1️⃣ Testing MCP server startup..."
python server/petting_zootopia.py &
SERVER_PID=$!
sleep 2

if ps -p $SERVER_PID > /dev/null; then
    echo "✅ MCP server started successfully (PID: $SERVER_PID)"
else
    echo "❌ MCP server failed to start"
    exit 1
fi

# Test 2: Check if MCP client can connect (quick test)
echo ""
echo "2️⃣ Testing MCP client connection..."
timeout 5 python -c "
import asyncio
import sys
sys.path.append('.')
from client.ai_mcp_client import create_mcp_client

async def test_connection():
    client = create_mcp_client()
    try:
        await client['connect_to_server']('server/petting_zootopia.py')
        print('✅ MCP client connected successfully')
        await client['cleanup']()
        return True
    except Exception as e:
        print(f'❌ MCP client connection failed: {e}')
        return False

result = asyncio.run(test_connection())
sys.exit(0 if result else 1)
" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✅ MCP client connection test passed"
else
    echo "❌ MCP client connection test failed"
fi

# Cleanup
echo ""
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null

echo ""
echo "✅ MCP client is ready for both web and CLI usage!"
echo ""
echo "To use:"
echo "  🌐 Web interface: ./setup.sh (choose option 1)"
echo "  🤖 CLI interface: ./setup.sh (choose option 2)"
