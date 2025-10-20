# Petting Zootopia MCP Server

A Model Context Protocol (MCP) server that provides animal image tools with AI-powered client support.

## 🐾 Tools Available

- **`greet(name)`** - Greet someone by name
- **`duck()`** - Get a random duck GIF from random-d.uk
- **`dog()`** - Get a random dog image from dog.ceo
- **`cat()`** - Get a random cat image from thecatapi.com

## 🚀 Quick Start

### 1. Automated Setup (Recommended)
```bash
# Run the setup script (only installs missing dependencies)
./setup.sh
```

### 1b. Manual Setup
```bash
# Install Python dependencies (only if missing)
pip install fastmcp httpx anthropic python-dotenv requests

# Install Ollama (for local AI) - only if not already installed
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Start Ollama (for local AI)
```bash
# Start Ollama service
ollama serve

# In another terminal, pull a model
ollama pull llama3.2:3b
```

### 3. Run the Server
```bash
# Start the MCP server
python server/petting_zootopia.py
```

### 4. Use the AI Client
```bash
# Use with Ollama (free, local)
python client/ai_mcp_client.py server/petting_zootopia.py

# Use with Claude (requires API key)
AI_BACKEND=claude_cheaper python client/ai_mcp_client.py server/petting_zootopia.py
```

## 🤖 AI Backend Options

### Ollama (Recommended for Learning)
- ✅ **Free** - no API costs
- ✅ **Local** - runs on your machine
- ✅ **Offline** - no internet required
- ✅ **Fast** - no network latency

### Claude Cheaper (Haiku)
- 💰 **Cheap** - $0.25/$1.25 per 1M tokens
- 🌐 **Online** - requires internet
- ⚡ **Fast** - good for development

### Claude Expensive (Sonnet)
- 💰 **Expensive** - $3.00/$15.00 per 1M tokens
- 🌐 **Online** - requires internet
- 🎯 **Best Quality** - for production use

## 🔧 Configuration

Create a `.env` file in your project root:

```bash
# AI Backend Configuration
AI_BACKEND=ollama_dev  # or claude_cheaper, claude_expensive

# Ollama Configuration (when AI_BACKEND=ollama_dev)
OLLAMA_MODEL=llama3.2:3b

# Claude Configuration (when AI_BACKEND starts with claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## 📖 Usage Examples

### Direct Tool Calls
```python
# The server provides these tools:
await greet("Alice")           # Returns: "Hello, Alice!"
await duck()                   # Returns: "https://random-d.uk/api/gifs/12.gif"
await dog()                    # Returns: "https://images.dog.ceo/breeds/..."
await cat()                    # Returns: "https://cdn2.thecatapi.com/images/..."
```

### AI-Powered Client
```bash
# Start the AI client
python client/ai_mcp_client.py server/petting_zootopia.py

# Then interact naturally:
Query: Show me a duck
Query: Hello Alice
Query: I want a cat picture
Query: Get me a dog
```

## 🏗️ Architecture

### Server (`server/petting_zootopia.py`)
- **Type**: FastMCP server
- **Transport**: STDIO (local communication)
- **Tools**: 4 animal image tools
- **APIs**: random-d.uk, dog.ceo, thecatapi.com

### Client (`client/ai_mcp_client.py`)
- **Type**: Pure functional Python
- **Features**: Multi-backend AI support
- **Backends**: Ollama (local), Claude (cloud)
- **AI Models**: Llama 3.2, Claude Haiku, Claude Sonnet

## 🛠️ Development

### Adding New Tools
1. Add tool function to `server/petting_zootopia.py`
2. Use `@mcp.tool` decorator
3. Add proper error handling
4. Test with client

### Adding New AI Backends
See `ADDING_BACKENDS.md` for detailed instructions.

## 📚 Documentation

- **`CLIENT_CONFIG.md`** - Detailed client configuration
- **`ADDING_BACKENDS.md`** - How to add new AI backends
- **`server/petting_zootopia.py`** - Server implementation
- **`client/ai_mcp_client.py`** - AI client implementation

## 🎯 Assignment Requirements

This project fulfills the Week 3 MCP assignment requirements:

- ✅ **External API integration** - 3 animal image APIs
- ✅ **2+ MCP tools** - 4 tools total
- ✅ **Error handling** - Graceful HTTP failures and timeouts
- ✅ **Clear documentation** - This README and setup instructions
- ✅ **Local deployment** - STDIO server for Claude Desktop
- ✅ **Example usage** - AI client with natural language interaction

## 🚨 Troubleshooting

### Ollama Issues
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Restart Ollama
ollama serve
```

### Claude Issues
```bash
# Check API key
echo $ANTHROPIC_API_KEY

# Test with environment variable
AI_BACKEND=claude_cheaper python client/ai_mcp_client.py server/petting_zootopia.py
```

### Server Issues
```bash
# Check server is running
python server/petting_zootopia.py

# Should show: "MCP server started"
```

## 📄 License

This project is part of the Stanford Modern Software Development course.