#!/bin/bash

# Petting Zootopia MCP Server Setup Script

echo "🐾 Setting up Petting Zootopia MCP Server..."

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
else
    echo "⚠️  No virtual environment detected. Consider using:"
    echo "   python -m venv venv && source venv/bin/activate"
    echo ""
fi

# Install Python dependencies (only if missing)
echo "📦 Checking Python dependencies..."

# Function to check if package is installed
check_package() {
    python -c "import $1" 2>/dev/null
}

# Install only missing packages
packages=("fastmcp" "httpx" "anthropic" "dotenv" "requests")
missing_packages=()

for package in "${packages[@]}"; do
    if ! check_package "$package"; then
        missing_packages+=("$package")
    fi
done

if [ ${#missing_packages[@]} -eq 0 ]; then
    echo "✅ All Python dependencies already installed!"
else
    echo "📦 Installing missing packages: ${missing_packages[*]}"
    pip install "${missing_packages[@]}"
fi

# Install web interface dependencies
echo "🌐 Checking web interface dependencies..."
web_packages=("fastapi" "uvicorn")
web_missing_packages=()

for package in "${web_packages[@]}"; do
    if ! check_package "$package"; then
        web_missing_packages+=("$package")
    fi
done

if [ ${#web_missing_packages[@]} -eq 0 ]; then
    echo "✅ Web interface dependencies already installed!"
else
    echo "📦 Installing web interface packages: ${web_missing_packages[*]}"
    pip install "${web_missing_packages[@]}"
fi

# Make web start script executable
if [ -f "web/start.sh" ]; then
    chmod +x web/start.sh
    echo "✅ Web start script is ready!"
else
    echo "⚠️  Web start script not found. Make sure you're in the project root."
fi

# Install Ollama
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    curl -fsSL https://ollama.ai/install.sh | sh
    echo "✅ Ollama installed successfully!"
else
    echo "✅ Ollama already installed!"
fi

# Start Ollama service
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait a moment for Ollama to start
sleep 3

# Pull the model (only if not already present)
echo "📥 Checking for Llama 3.2 model..."
if ollama list | grep -q "llama3.2:3b"; then
    echo "✅ Llama 3.2 model already installed!"
else
    echo "📥 Pulling Llama 3.2 model..."
    ollama pull llama3.2:3b
fi

echo "✅ Setup complete!"
echo ""
echo "🎯 What would you like to run?"
echo ""
echo "1) 🌐 WEB APP + MCP CLIENT + MCP SERVER (Recommended)"
echo "   - Starts everything needed for the web interface"
echo "   - Opens web browser automatically"
echo ""
echo "2) 🤖 MCP CLIENT + MCP SERVER (Command line only)"
echo "   - Just the AI-powered command line interface"
echo ""
echo "3) 🔧 MCP SERVER ONLY (Development)"
echo "   - Just the MCP server for testing"
echo ""
echo "4) 📚 Show me the options again"
echo ""
read -p "Enter your choice (1-4): " choice
echo ""

case $choice in
    1)
        echo "🌐 Starting web app with MCP client and server..."
        echo ""
        echo "Starting MCP server in background..."
        python server/petting_zootopia.py &
        MCP_SERVER_PID=$!
        sleep 2
        
        echo "Starting MCP client in background..."
        python client/ai_mcp_client.py server/petting_zootopia.py &
        MCP_CLIENT_PID=$!
        sleep 2
        
        echo "Starting web server..."
        cd web && ./start.sh &
        WEB_PID=$!
        sleep 3
        
        echo "✅ All services started!"
        echo "   Web interface: http://localhost:8000"
        echo "   MCP server PID: $MCP_SERVER_PID"
        echo "   MCP client PID: $MCP_CLIENT_PID"
        echo "   Web server PID: $WEB_PID"
        echo ""
        echo "Press Ctrl+C to stop all services"
        wait
        ;;
    2)
        echo "🤖 Starting MCP client and server..."
        echo "   Press Ctrl+C to stop"
        python client/ai_mcp_client.py server/petting_zootopia.py
        ;;
    3)
        echo "🔧 Starting MCP server only..."
        echo "   Press Ctrl+C to stop"
        python server/petting_zootopia.py
        ;;
    4)
        echo "📚 Options:"
        echo "   1) Web app + MCP client + MCP server (easiest)"
        echo "   2) MCP client + MCP server (command line)"
        echo "   3) MCP server only (development)"
        echo "   4) Show options again"
        echo ""
        echo "Run ./setup.sh again to choose"
        ;;
    *)
        echo "❌ Invalid choice. Please run ./setup.sh again"
        exit 1
        ;;
esac
