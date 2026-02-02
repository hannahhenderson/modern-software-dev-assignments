# Petting Zootopia

A functional MCP (Model Context Protocol) server for fetching random animal images. Built with Python using functional programming principles.

## Quickstart

### Option 1: Docker (Recommended)

```bash
docker-compose up
```

Open http://localhost:8000 in your browser.

### Option 2: Local Installation

```bash
# Install dependencies
make dev

# Copy and configure environment
cp .env.example .env

# Start the web server
make run-web
```

Open http://localhost:8000 in your browser.

## Features

- **MCP Server**: Exposes tools for fetching duck, dog, and cat images
- **Web Interface**: Beautiful UI for browsing animal images
- **AI Client**: Natural language queries with Ollama or Claude backends
- **Functional Design**: Result types, immutable data, explicit dependencies

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Web Client    │────▶│   FastAPI Web   │────▶│  External APIs  │
│   (Browser)     │     │     Server      │     │ (duck/dog/cat)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘

┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   AI Client     │────▶│   MCP Server    │────▶│  External APIs  │
│ (Ollama/Claude) │     │  (FastMCP)      │     │ (duck/dog/cat)  │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Usage

### Web Interface

```bash
make run-web
# Visit http://localhost:8000
```

### MCP Server (for AI clients)

```bash
make run-server
```

### Interactive CLI Client

```bash
# Requires Ollama running locally (or configure Claude)
make run-client
```

Example queries:
- "Show me a duck"
- "I want to see a cute cat"
- "Give me a random dog"

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

### AI Backends

| Backend | Description | Setup |
|---------|-------------|-------|
| `ollama` | Free, local LLM | [Install Ollama](https://ollama.ai), run `ollama pull llama3.2:3b` |
| `claude_haiku` | Fast, cheap Claude | Set `ANTHROPIC_API_KEY` |
| `claude_sonnet` | High-quality Claude | Set `ANTHROPIC_API_KEY` |

### Key Settings

```env
AI_BACKEND=ollama           # ollama, claude_haiku, or claude_sonnet
PORT=8000                   # Web server port
RATE_LIMIT=10/minute        # API rate limiting
LOG_LEVEL=info              # debug, info, warning, error
```

## API Reference

### REST Endpoints

#### `POST /api/animal`

Fetch a random animal image.

```bash
curl -X POST http://localhost:8000/api/animal \
  -H "Content-Type: application/json" \
  -d '{"animal": "duck"}'
```

Response:
```json
{
  "success": true,
  "image_url": "https://random-d.uk/api/123.jpg",
  "animal": "duck",
  "message": "Here's a duck!"
}
```

#### `GET /api/animals`

List available animal types.

```bash
curl http://localhost:8000/api/animals
```

Response:
```json
{
  "animals": ["duck", "dog", "cat"]
}
```

#### `GET /api/health`

Health check endpoint.

### MCP Tools

When running as an MCP server, these tools are available:

| Tool | Description |
|------|-------------|
| `duck()` | Get a random duck image |
| `dog()` | Get a random dog image |
| `cat()` | Get a random cat image |
| `ping()` | Health check |
| `health_check()` | Check all external APIs |

## Development

### Setup

```bash
make dev          # Install with dev dependencies
```

### Commands

```bash
make test         # Run tests
make lint         # Run linter
make format       # Format code
make typecheck    # Run type checker
make clean        # Remove build artifacts
```

### Project Structure

```
petting-zootopia/
├── src/petting_zootopia/
│   ├── __init__.py       # Package exports
│   ├── types.py          # Result types, error types, data models
│   ├── config.py         # Pydantic settings
│   ├── http.py           # Pure HTTP fetch functions
│   ├── server.py         # MCP server
│   ├── client.py         # AI-powered MCP client
│   └── web.py            # FastAPI web server
├── web/
│   ├── index.html        # Main web page
│   ├── about.html        # About page
│   └── assets/           # Static assets
├── tests/                # Test suite
├── pyproject.toml        # Dependencies and config
├── Makefile              # Development commands
├── Dockerfile            # Container image
└── docker-compose.yml    # Multi-service setup
```

## Functional Programming Patterns

This codebase demonstrates several functional programming patterns in Python:

### Result Types

Instead of exceptions, functions return `Result[T, E]` (either `Ok(value)` or `Err(error)`):

```python
async def fetch_duck(client, config) -> Result[AnimalImage, APIError]:
    # Returns Ok(image) on success, Err(error) on failure
    ...

# Usage with pattern matching
match await fetch_duck(client, config):
    case Ok(image):
        return image.url
    case Err(RateLimited(retry_after=seconds)):
        raise HTTPException(429, headers={"Retry-After": str(seconds)})
    case Err(error):
        return fallback_url
```

### Immutable Data

All data structures are frozen dataclasses:

```python
@dataclass(frozen=True, slots=True)
class AnimalImage:
    url: str
    animal: AnimalType
```

### Explicit Dependencies

No global state. All dependencies are passed explicitly:

```python
def create_app(config: Config) -> FastAPI:
    # Config injected, not imported from globals
    ...

async def fetch_duck(client: httpx.AsyncClient, config: Config) -> Result[...]:
    # HTTP client and config are explicit parameters
    ...
```

### Function Factories

Higher-order functions create specialized functions:

```python
def create_ollama_processor(url: str, model: str) -> QueryProcessor:
    # Returns a function configured with url and model
    async def process_query(query, tools, session) -> str:
        ...
    return process_query
```

## External APIs

This project uses these free, public APIs:

| API | URL | Rate Limit |
|-----|-----|------------|
| Random Duck | random-d.uk | ~100/hour |
| Random Dog | random.dog | ~1000/hour |
| Dog CEO | dog.ceo | Generous |
| The Cat API | thecatapi.com | 10/minute |

## License

MIT
