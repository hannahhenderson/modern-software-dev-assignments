# AI Petting Zootopia Client Configuration

## Quick Start

1. **Install dependencies**: `pip install fastmcp anthropic python-dotenv requests`
2. **Choose your backend** (see options below)
3. **Set environment variables** in `.env` file
4. **Run the client**: `python client/ai_mcp_client.py ../server/petting_zootopia.py`

## Environment Variables

Create a `.env` file in your project root with these variables:

```bash
# AI Backend Configuration
# Choose one of: ollama_dev, claude_cheaper, claude_expensive
AI_BACKEND=ollama_dev

# Ollama Configuration (when AI_BACKEND=ollama_dev)
OLLAMA_MODEL=llama3.2:3b

# Claude Configuration (when AI_BACKEND starts with claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Backend Options

### 1. Ollama Development (Recommended for Learning)
```bash
AI_BACKEND=ollama_dev
OLLAMA_MODEL=llama3.2:3b
```
- ✅ **Free** - no API costs
- ✅ **Local** - runs on your machine
- ✅ **Offline** - no internet required
- ✅ **Fast** - no network latency

### 2. Claude Cheaper (Haiku)
```bash
AI_BACKEND=claude_cheaper
ANTHROPIC_API_KEY=your_key_here
```
- 💰 **Cheap** - $0.25/$1.25 per 1M tokens
- 🌐 **Online** - requires internet
- ⚡ **Fast** - good for development
- 🎯 **Model**: Claude Haiku

### 3. Claude Expensive (Sonnet)
```bash
AI_BACKEND=claude_expensive
ANTHROPIC_API_KEY=your_key_here
```
- 💰 **Expensive** - $3.00/$15.00 per 1M tokens
- 🌐 **Online** - requires internet
- 🎯 **Best Quality** - for production use
- 🎯 **Model**: Claude Sonnet 4.5

## Usage Examples

```bash
# Use Ollama (default)
python client/ai_mcp_client.py ../server/petting_zootopia.py

# Use Claude Cheaper (Haiku)
AI_BACKEND=claude_cheaper python client/ai_mcp_client.py ../server/petting_zootopia.py

# Use Claude Expensive (Sonnet)
AI_BACKEND=claude_expensive python client/ai_mcp_client.py ../server/petting_zootopia.py
```

## Setup Instructions

### Prerequisites
1. **Python 3.8+** installed
2. **Virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

### For Ollama (Recommended for Learning):
1. **Install Ollama**: `curl -fsSL https://ollama.ai/install.sh | sh`
2. **Start Ollama**: `ollama serve`
3. **Pull model**: `ollama pull llama3.2:3b`
4. **Set environment**: `AI_BACKEND=ollama_dev` in `.env`
5. **Run client**: `python client/ai_mcp_client.py ../server/petting_zootopia.py`

### For Claude:
1. **Get API key** from [Anthropic Console](https://console.anthropic.com/)
2. **Set environment variables** in `.env`:
   ```bash
   AI_BACKEND=claude_cheaper  # or claude_expensive
   ANTHROPIC_API_KEY=your_key_here
   ```
3. **Run client**: `python client/ai_mcp_client.py ../server/petting_zootopia.py`

## Client Types

### Current Implementation
- **File**: `client/ai_mcp_client.py`
- **Type**: Pure functional Python
- **Features**: Multi-backend support, environment-based configuration
- **Backends**: Ollama (local), Claude (cloud)

### Architecture
- **Zero classes** - pure functional programming
- **Function factories** - create configured processors
- **Closures** - capture state without classes
- **Higher-order functions** - functions that return functions
