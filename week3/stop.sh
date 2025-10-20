#!/bin/bash

# Stop all Petting Zootopia processes
echo "🛑 Stopping all Petting Zootopia processes..."

# Kill MCP server
echo "Stopping MCP server..."
pkill -f "petting_zootopia.py" 2>/dev/null

# Kill MCP client
echo "Stopping MCP client..."
pkill -f "ai_mcp_client.py" 2>/dev/null

# Kill web_client server
echo "Stopping web_client server..."
pkill -f "app.py" 2>/dev/null

# Kill any uvicorn processes
echo "Stopping uvicorn..."
pkill -f "uvicorn" 2>/dev/null

echo "✅ All processes stopped!"
echo ""
echo "To start again, run: ./setup.sh"
