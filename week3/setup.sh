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
echo "🎯 Next steps:"
echo "1. Start the server: python server/petting_zootopia.py"
echo "2. Use the AI client: python client/ai_mcp_client.py server/petting_zootopia.py"
echo ""
echo "📚 For more information, see README.md"
