#!/bin/bash

# Start the Petting Zootopia web server
echo "🐾 Starting Petting Zootopia Web Server..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Warning: No virtual environment detected."
    echo "   Consider running: python -m venv venv && source venv/bin/activate"
    echo ""
fi

# Install dependencies if needed
echo "📦 Installing web server dependencies..."
pip install -r requirements.txt

# Check if MCP server exists
if [ ! -f "../server/petting_zootopia.py" ]; then
    echo "❌ Error: MCP server not found at ../server/petting_zootopia.py"
    echo "   Make sure you're running this from the web/ directory"
    exit 1
fi

# Check if MCP client exists
if [ ! -f "../client/ai_mcp_client.py" ]; then
    echo "❌ Error: MCP client not found at ../client/ai_mcp_client.py"
    echo "   Make sure you're running this from the web/ directory"
    exit 1
fi

echo "✅ MCP server and client found"
echo ""
echo "🚀 Starting web server on http://localhost:8000"
echo "   Note: Make sure MCP client and server are running separately"
echo "   Press Ctrl+C to stop"
echo ""

python app.py
