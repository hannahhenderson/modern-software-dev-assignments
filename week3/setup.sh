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
if [ -f "web_client/start.sh" ]; then
        chmod +x web_client/start.sh
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

# Start Ollama service (only if not already running)
echo "🚀 Starting Ollama service..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is already running!"
else
    echo "Starting Ollama..."
    ollama serve &
    OLLAMA_PID=$!
    # Wait a moment for Ollama to start
    sleep 3
fi

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
echo "1) 🌐 WEB INTERFACE (Recommended)"
echo "   - Web interface with MCP client/server integration"
echo "   - Access at http://localhost:8000"
echo "   - Demonstrates MCP client/server interaction"
echo ""
echo "2) 🤖 COMMAND LINE INTERFACE"
echo "   - Interactive MCP client with AI backend"
echo "   - Type natural language queries"
echo "   - Direct MCP client/server communication"
echo ""
echo "3) 🔧 MCP SERVER ONLY (Development)"
echo "   - Just the MCP server for testing"
echo "   - Use with external MCP clients"
echo ""
echo "4) 📚 Show me the options again"
echo ""
read -p "Enter your choice (1-4): " choice
echo ""

case $choice in
    1)
        echo "🌐 Starting web interface with MCP integration..."
        echo ""
        echo "Starting MCP server in background..."
        python server/petting_zootopia.py &
        MCP_SERVER_PID=$!
        sleep 3
        
        echo "Starting web server (includes MCP client)..."
        cd web_client && ./start.sh &
        WEB_PID=$!
        sleep 3
        
        echo "✅ Web interface ready!"
        echo "   🌐 Web interface: http://localhost:8000"
        echo "   🔧 MCP server PID: $MCP_SERVER_PID"
        echo "   🌐 Web server PID: $WEB_PID"
        echo ""
        echo "The web interface demonstrates MCP client/server interaction"
        echo "Press Ctrl+C to stop all services"
        
        # Function to cleanup on exit
        cleanup() {
            echo ""
            echo "🛑 Stopping all services..."
            kill $MCP_SERVER_PID 2>/dev/null
            kill $WEB_PID 2>/dev/null
            echo "✅ All services stopped"
            exit 0
        }
        
        # Set up signal handlers
        trap cleanup SIGINT SIGTERM
        
        # Wait for any process to exit
        wait
        ;;
    2)
        echo "🤖 Starting command line MCP client..."
        echo ""
        echo "This will start an interactive MCP client with AI backend"
        echo "You can type natural language queries like:"
        echo "  - 'Show me a duck'"
        echo "  - 'Hello Alice'"
        echo "  - 'I want a cat picture'"
        echo ""
        echo "Press Ctrl+C to stop"
        python mcp_client/ai_mcp_client.py server/petting_zootopia.py
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
