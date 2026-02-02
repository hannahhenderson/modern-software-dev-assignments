"""
AI-powered MCP Client for Petting Zootopia.

Supports multiple AI backends (Ollama, Claude) using functional composition.
All state is explicitly managed through closures and return values.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from dataclasses import dataclass
from typing import Callable, Awaitable, Literal
from contextlib import AsyncExitStack

import httpx
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from petting_zootopia.types import Ok, Err, Result
from petting_zootopia.config import Config, load_config

logger = logging.getLogger(__name__)


# =============================================================================
# Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class Tool:
    """Immutable representation of an MCP tool."""

    name: str
    description: str
    input_schema: dict


@dataclass(frozen=True, slots=True)
class ToolCall:
    """Immutable representation of a tool call request."""

    tool: str | None
    parameters: dict


@dataclass(frozen=True, slots=True)
class ConnectionInfo:
    """Information about a successful connection."""

    tools: tuple[str, ...]
    backend: str


@dataclass(frozen=True, slots=True)
class ClientError:
    """Client operation error."""

    message: str
    details: str = ""


# Type alias for query processor functions
QueryProcessor = Callable[[str, list[Tool], ClientSession], Awaitable[str]]


# =============================================================================
# Backend Processors - Pure Functional Factories
# =============================================================================


def create_ollama_processor(url: str, model: str) -> QueryProcessor:
    """
    Create an Ollama query processor.

    Returns a pure async function that processes queries using Ollama.
    All configuration is captured in the closure.
    """

    def call_ollama(prompt: str) -> Result[str, ClientError]:
        """Synchronous Ollama API call wrapped in Result."""
        try:
            response = httpx.post(
                url,
                json={"model": model, "prompt": prompt, "stream": False},
                timeout=30,
            )
            response.raise_for_status()
            return Ok(response.json()["response"])
        except Exception as e:
            return Err(ClientError(message="Ollama call failed", details=str(e)))

    async def process_query(query: str, tools: list[Tool], session: ClientSession) -> str:
        """Process a query using Ollama for tool selection."""
        tools_json = json.dumps(
            [{"name": t.name, "description": t.description} for t in tools],
            indent=2,
        )

        prompt = f"""You are an AI assistant that can call tools.

Available tools:
{tools_json}

User query: {query}

Respond with ONLY a JSON object: {{"tool": "tool_name", "parameters": {{}}}}
If no tool matches, respond with: {{"tool": null, "parameters": {{}}}}

Examples:
- "Show me a duck" → {{"tool": "duck", "parameters": {{}}}}
- "I want a giraffe" → {{"tool": null, "parameters": {{}}}}
"""

        result = call_ollama(prompt)

        match result:
            case Err(error):
                return f"Error: {error.message} - {error.details}"
            case Ok(response):
                return await _execute_tool_call(response, session)

    return process_query


def create_claude_processor(
    api_key: str | None, model: str, max_tokens: int
) -> QueryProcessor:
    """
    Create a Claude query processor.

    Returns a pure async function that processes queries using Claude.
    """
    client = Anthropic(api_key=api_key) if api_key else Anthropic()

    async def process_query(query: str, tools: list[Tool], session: ClientSession) -> str:
        """Process a query using Claude for tool selection and execution."""
        messages = [{"role": "user", "content": query}]

        # Convert tools to Claude format
        claude_tools = [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in tools
        ]

        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=claude_tools,
        )

        output_parts: list[str] = []

        for content in response.content:
            match content.type:
                case "text":
                    output_parts.append(content.text)
                case "tool_use":
                    tool_result = await session.call_tool(content.name, content.input)
                    output_parts.append(
                        f"[Called {content.name}] Result: {tool_result.content}"
                    )

                    # Continue conversation with tool result
                    messages.append({"role": "user", "content": str(tool_result.content)})
                    followup = client.messages.create(
                        model=model,
                        max_tokens=max_tokens,
                        messages=messages,
                    )
                    if followup.content:
                        output_parts.append(followup.content[0].text)

        return "\n".join(output_parts)

    return process_query


async def _execute_tool_call(response: str, session: ClientSession) -> str:
    """Parse and execute a tool call from LLM response."""
    try:
        call = json.loads(response.strip())
        tool_name = call.get("tool")

        if not tool_name or tool_name == "null":
            return "I don't have a tool for that request."

        params = call.get("parameters", {})
        result = await session.call_tool(tool_name, params)
        return f"Result: {result.content}"

    except json.JSONDecodeError:
        return f"Could not parse response: {response}"
    except Exception as e:
        return f"Error executing tool: {e}"


# =============================================================================
# Client Factory
# =============================================================================


BackendType = Literal["ollama", "claude_haiku", "claude_sonnet"]


def get_processor(config: Config) -> tuple[str, QueryProcessor]:
    """
    Get the appropriate query processor based on configuration.

    Returns (backend_name, processor_function).
    """
    processors: dict[str, tuple[str, QueryProcessor]] = {
        "ollama": (
            "Ollama",
            create_ollama_processor(config.ollama_url, config.ollama_model),
        ),
        "claude_haiku": (
            "Claude Haiku",
            create_claude_processor(config.anthropic_api_key, "claude-haiku-20240307", 300),
        ),
        "claude_sonnet": (
            "Claude Sonnet",
            create_claude_processor(config.anthropic_api_key, "claude-sonnet-4-5", 1000),
        ),
    }

    backend = config.ai_backend
    if backend not in processors:
        raise ValueError(f"Unknown backend: {backend}. Available: {list(processors.keys())}")

    return processors[backend]


def create_client(config: Config) -> dict[str, Callable]:
    """
    Create an MCP client with all operations as pure functions.

    Returns a dictionary of async functions for client operations.
    State is managed through closures, not global variables.
    """
    session: ClientSession | None = None
    exit_stack = AsyncExitStack()
    backend_name, processor = get_processor(config)

    async def connect(server_path: str) -> Result[ConnectionInfo, ClientError]:
        """Connect to an MCP server."""
        nonlocal session

        if not server_path.endswith((".py", ".js")):
            return Err(ClientError("Invalid server path", "Must be .py or .js file"))

        try:
            command = "python" if server_path.endswith(".py") else "node"
            server_params = StdioServerParameters(
                command=command,
                args=[server_path],
                env=None,
            )

            transport = await exit_stack.enter_async_context(stdio_client(server_params))
            stdio, write = transport
            session = await exit_stack.enter_async_context(ClientSession(stdio, write))
            await session.initialize()

            response = await session.list_tools()
            tool_names = tuple(t.name for t in response.tools)

            return Ok(ConnectionInfo(tools=tool_names, backend=backend_name))

        except Exception as e:
            return Err(ClientError("Connection failed", str(e)))

    async def query(text: str) -> Result[str, ClientError]:
        """Process a query through the MCP server."""
        if session is None:
            return Err(ClientError("Not connected", "Call connect() first"))

        try:
            response = await session.list_tools()
            tools = [
                Tool(
                    name=t.name,
                    description=t.description or "",
                    input_schema=t.inputSchema or {},
                )
                for t in response.tools
            ]

            result = await processor(text, tools, session)
            return Ok(result)

        except Exception as e:
            return Err(ClientError("Query failed", str(e)))

    async def cleanup() -> None:
        """Clean up resources."""
        await exit_stack.aclose()

    return {
        "connect": connect,
        "query": query,
        "cleanup": cleanup,
        "backend_name": backend_name,
    }


# =============================================================================
# Interactive CLI
# =============================================================================


async def run_interactive(config: Config, server_path: str) -> None:
    """Run an interactive chat session."""
    client = create_client(config)

    try:
        result = await client["connect"](server_path)

        match result:
            case Err(error):
                print(f"Connection failed: {error.message}")
                return
            case Ok(info):
                print(f"\nConnected! Tools: {', '.join(info.tools)}")
                print(f"Backend: {info.backend}")
                print("\nType queries or 'quit' to exit.")
                print("Examples: 'Show me a duck', 'I want a cat'\n")

        while True:
            try:
                user_input = input("Query: ").strip()
                if user_input.lower() == "quit":
                    break

                result = await client["query"](user_input)
                match result:
                    case Ok(response):
                        print(f"\n{response}\n")
                    case Err(error):
                        print(f"\nError: {error.message}\n")

            except KeyboardInterrupt:
                break
            except EOFError:
                break

    finally:
        await client["cleanup"]()


def main() -> None:
    """Entry point for the MCP client."""
    logging.basicConfig(level=logging.WARNING)

    if len(sys.argv) < 2:
        print("Usage: petting-zootopia-client <path_to_server>")
        print("Example: petting-zootopia-client ./src/petting_zootopia/server.py")
        sys.exit(1)

    config = load_config()
    asyncio.run(run_interactive(config, sys.argv[1]))


if __name__ == "__main__":
    main()
