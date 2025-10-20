# Petting Zootopia MCP Server

A Model Context Protocol (MCP) server that provides animal image tools with AI-powered client support.

## 🐾 Tools Available

- **`greet(name)`** - Greet someone by name
- **`duck()`** - Get a random duck GIF from random-d.uk
- **`dog()`** - Get a random dog image from dog.ceo
- **`cat()`** - Get a random cat image from thecatapi.com

## 🌐 Web Interface

A beautiful web interface is available for easy interaction:

- **🎨 Modern UI** - Responsive design with smooth animations
- **🖼️ Visual Interface** - Click buttons to get animal images
- **🔗 REST API** - FastAPI backend with MCP integration
- **📱 Mobile Friendly** - Works on all devices

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

### 4. Choose Your Interface

#### 🌐 Web Interface (Recommended)
```bash
# Start everything with web interface
./setup.sh
# Choose option 1, then open http://localhost:8000
```

#### 🤖 Command Line Interface
```bash
# Start interactive MCP client
./setup.sh
# Choose option 2, then type natural language queries
```

#### 🔧 Development Mode
```bash
# Start just the MCP server
./setup.sh
# Choose option 3 for development/testing
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

### 🌐 Web Interface
```bash
# Start web interface
./setup.sh
# Choose option 1, then open http://localhost:8000
# Click animal buttons to get images via MCP client/server!
```

### 🤖 Command Line Interface
```bash
# Start interactive MCP client
./setup.sh
# Choose option 2, then type queries:

Query: Show me a duck
Query: Hello Alice  
Query: I want a cat picture
Query: Get me a dog
```

### 🔧 Direct MCP Server Usage
```python
# The MCP server provides these tools:
await greet("Alice")           # Returns: "Hello, Alice!"
await duck()                   # Returns: "https://random-d.uk/api/gifs/12.gif"
await dog()                    # Returns: "https://images.dog.ceo/breeds/..."
await cat()                    # Returns: "https://cdn2.thecatapi.com/images/..."
```

## 🏗️ Architecture

### Web Interface (`web_client/`)
- **Frontend**: HTML/CSS/JavaScript with responsive design
- **Backend**: FastAPI server with MCP integration
- **Features**: Visual buttons, loading states, error handling
- **Port**: 8000 (http://localhost:8000)

### Server (`server/petting_zootopia.py`)
- **Type**: FastMCP server
- **Transport**: STDIO (local communication)
- **Tools**: 4 animal image tools
- **APIs**: random-d.uk, dog.ceo, thecatapi.com

### Client (`mcp_client/ai_mcp_client.py`)
- **Type**: Pure functional Python
- **Features**: Multi-backend AI support
- **Backends**: Ollama (local), Claude (cloud)
- **AI Models**: Llama 3.2, Claude Haiku, Claude Sonnet

## 🛠️ Development

### Adding New Tools
1. Add tool function to `server/petting_zootopia.py`
2. Use `@mcp.tool` decorator
3. Add proper error handling
4. Test with web interface and client

### Adding New Web Features
1. Add button to `web_client/index.html`
2. Update JavaScript in `web_client/index.html`
3. Add API endpoint to `web_client/app.py`
4. Test the complete flow

### Adding New AI Backends
See the "Adding New AI Backends" section below for detailed instructions.

## ⚙️ Advanced Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# AI Backend Configuration
# Choose one of: ollama_dev, claude_cheaper, claude_expensive
AI_BACKEND=ollama_dev

# Ollama Configuration (when AI_BACKEND=ollama_dev)
OLLAMA_MODEL=llama3.2:3b

# Claude Configuration (when AI_BACKEND starts with claude)
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

### Detailed Backend Setup

#### Ollama (Recommended for Learning)
```bash
AI_BACKEND=ollama_dev
OLLAMA_MODEL=llama3.2:3b
```
- ✅ **Free** - no API costs
- ✅ **Local** - runs on your machine
- ✅ **Offline** - no internet required
- ✅ **Fast** - no network latency

#### Claude Cheaper (Haiku)
```bash
AI_BACKEND=claude_cheaper
ANTHROPIC_API_KEY=your_key_here
```
- 💰 **Cheap** - $0.25/$1.25 per 1M tokens
- 🌐 **Online** - requires internet
- ⚡ **Fast** - good for development
- 🎯 **Model**: Claude Haiku

#### Claude Expensive (Sonnet)
```bash
AI_BACKEND=claude_expensive
ANTHROPIC_API_KEY=your_key_here
```
- 💰 **Expensive** - $3.00/$15.00 per 1M tokens
- 🌐 **Online** - requires internet
- 🎯 **Best Quality** - for production use
- 🎯 **Model**: Claude Sonnet 4.5

### Virtual Environment Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Adding New AI Backends

The client uses pure functional programming with function factories. Here's how to add new backends:

### 1. Create the Processor Function

```python
def create_openai_processor(model: str, max_tokens: int):
    """Create an OpenAI processor using pure functional composition"""
    openai = OpenAI()
    
    async def process_query(query: str, available_tools: list, session: ClientSession) -> str:
        """Process query using OpenAI"""
        messages = [{"role": "user", "content": query}]

        # OpenAI API call
        response = openai.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []
        for choice in response.choices:
            if choice.message.content:
                final_text.append(choice.message.content)
            
            if choice.message.tool_calls:
                for tool_call in choice.message.tool_calls:
                    tool_name = tool_call.function.name
                    tool_args = json.loads(tool_call.function.arguments)
                    
                    # Execute tool call
                    result = await session.call_tool(tool_name, tool_args)
                    final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                    final_text.append(f"Result: {result.content}")

        return "\n".join(final_text)
    
    return process_query  # Returns a function, not a class
```

### 2. Add to Factory Functions

```python
processor_factories = {
    # ... existing backends ...
    'openai_cheaper': lambda: create_openai_processor(
        model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '500'))
    ),
    'openai_expensive': lambda: create_openai_processor(
        model=os.getenv('OPENAI_MODEL', 'gpt-4'),
        max_tokens=int(os.getenv('OPENAI_MAX_TOKENS', '1000'))
    )
}
```

### 3. Use the New Backend

```bash
AI_BACKEND=openai_cheaper python mcp_client/ai_mcp_client.py server/petting_zootopia.py
```

### Benefits of This Functional Design

- ✅ **Zero classes** - pure functional programming
- ✅ **Function factories** - create configured functions
- ✅ **Closures** - capture state without classes
- ✅ **Higher-order functions** - functions that return functions
- ✅ **Function composition** - combine functions elegantly
- ✅ **Pure functions** - no side effects
- ✅ **Easy to extend** - just add to factory functions

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
AI_BACKEND=claude_cheaper python mcp_client/ai_mcp_client.py server/petting_zootopia.py
```

### Server Issues
```bash
# Check server is running
python server/petting_zootopia.py

# Should show: "MCP server started"
```

### Web Interface Issues
```bash
# Check web server dependencies
cd web
pip install -r requirements.txt

# Start web server
./start.sh

# Check if running on http://localhost:8000
curl http://localhost:8000/api/health
```

## 📄 License

This project is part of the [Stanford Modern Software Development](https://themodernsoftware.dev/) course.