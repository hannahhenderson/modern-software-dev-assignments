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

# Start the server
echo "🚀 Starting server on http://localhost:8000"
echo "   Press Ctrl+C to stop"
echo ""

python app.py
