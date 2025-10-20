import asyncio
import json
import requests
import os
from typing import Optional, Dict, Any, Callable, Awaitable
from contextlib import AsyncExitStack
from functools import partial

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

# Pure functional backend implementations
def create_ollama_processor(model: str = "llama3.2:3b"):
    """Create an Ollama processor using pure functional composition"""
    ollama_url = "http://localhost:11434/api/generate"
    
    def call_ollama(prompt: str) -> str:
        """Call Ollama API with the given prompt"""
        try:
            response = requests.post(
                ollama_url,
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            response.raise_for_status()
            return response.json()["response"]
        except Exception as e:
            return f"Error calling Ollama: {str(e)}"
    
    async def process_query(query: str, available_tools: list, session: ClientSession) -> str:
        """Process query using Ollama"""
        tools_info = [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["input_schema"].get("properties", {}) if tool["input_schema"] else {}
            }
            for tool in available_tools
        ]

        tools_json = json.dumps(tools_info, indent=2)
        prompt = f"""You are an AI assistant that can call tools. 

Available tools:
{tools_json}

User query: {query}

Based on the user query, determine which tool to call and what parameters to use.
Respond with ONLY a JSON object in this format:
{{"tool": "tool_name", "parameters": {{"param1": "value1", "param2": "value2"}}}}

If no tool is needed or the query doesn't match any available tools, respond with: {{"tool": null, "parameters": {{}}}}

Examples:
- "Show me a duck" → {{"tool": "duck", "parameters": {{}}}}
- "Hello Alice" → {{"tool": "greet", "parameters": {{"name": "Alice"}}}}
- "Hi there" → {{"tool": "greet", "parameters": {{"name": "there"}}}}
- "I want a giraffe" → {{"tool": null, "parameters": {{}}}} (no giraffe tool available)
- "What's the weather?" → {{"tool": null, "parameters": {{}}}} (no weather tool available)
"""

        ollama_response = call_ollama(prompt)
        
        try:
            tool_call = json.loads(ollama_response.strip())
            
            if tool_call.get("tool") and tool_call.get("tool") != "null":
                tool_name = tool_call["tool"]
                tool_params = tool_call.get("parameters", {})
                
                result = await session.call_tool(tool_name, tool_params)
                return f"Tool '{tool_name}' called with parameters {tool_params}.\nResult: {result.content}"
            else:
                return "Sorry, I don't have tools available for that request. I can only help with ducks, dogs, cats, greetings, and health checks."
                
        except json.JSONDecodeError:
            return f"Could not parse Ollama response as JSON: {ollama_response}"
        except Exception as e:
            return f"Error processing query: {str(e)}"
    
    return process_query

def create_claude_processor(model: str, max_tokens: int):
    """Create a Claude processor using pure functional composition"""
    anthropic = Anthropic()
    
    async def process_query(query: str, available_tools: list, session: ClientSession) -> str:
        """Process query using Claude"""
        messages = [{"role": "user", "content": query}]

        # Initial Claude API call
        response = anthropic.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        for content in response.content:
            if content.type == 'text':
                final_text.append(content.text)
            elif content.type == 'tool_use':
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await session.call_tool(tool_name, tool_args)
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")

                # Continue conversation with tool results
                if hasattr(content, 'text') and content.text:
                    messages.append({
                      "role": "assistant",
                      "content": content.text
                    })
                messages.append({
                    "role": "user", 
                    "content": result.content
                })

                # Get next response from Claude
                response = anthropic.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=messages,
                )

                final_text.append(response.content[0].text)

        return "\n".join(final_text)
    
    return process_query

# Pure functional configuration
def get_backend_processor():
    """Get backend processor using pure functional composition"""
    backend_name = os.getenv('AI_BACKEND', 'ollama_dev').lower()
    
    # Backend processor factory functions
    processor_factories = {
        'ollama_dev': lambda: create_ollama_processor(
            model=os.getenv('OLLAMA_MODEL', 'llama3.2:3b')
        ),
        'claude_cheaper': lambda: create_claude_processor(
            model='claude-haiku-20240307',
            max_tokens=300
        ),
        'claude_expensive': lambda: create_claude_processor(
            model='claude-sonnet-4-5',
            max_tokens=1000
        )
    }
    
    if backend_name not in processor_factories:
        raise ValueError(f"Unknown backend: {backend_name}. Available: {list(processor_factories.keys())}")
    
    return backend_name, processor_factories[backend_name]()

# Pure functional client implementation
def create_mcp_client():
    """Create an MCP client using pure functional composition"""
    session = None
    exit_stack = AsyncExitStack()
    backend_name, backend_processor = get_backend_processor()
    
    async def connect_to_server(server_script_path: str):
        """Connect to an MCP server"""
        nonlocal session
        
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await exit_stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await exit_stack.enter_async_context(ClientSession(stdio, write))
        
        await session.initialize()
        
        # List available tools
        response = await session.list_tools()
        tools = response.tools
        print(f"\nConnected to server with tools: {[tool.name for tool in tools]}")
        print(f"Using backend: {backend_name}")
    
    async def process_query(query: str) -> str:
        """Process a query using the configured backend"""
        if not session:
            raise ValueError("Not connected to server")
        
        # Get available tools
        response = await session.list_tools()
        available_tools = [{ 
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.inputSchema
        } for tool in response.tools]

        # Delegate to the configured backend processor - pure functional composition!
        return await backend_processor(query, available_tools, session)
    
    async def chat_loop():
        """Run an interactive chat loop"""
        print(f"\nPure Functional Petting Zootopia Client Started! (Backend: {backend_name})")
        print("Type your queries or 'quit' to exit.")
        print("Examples:")
        print("- 'Show me a duck'")
        print("- 'Hello Alice'")
        print("- 'I want a GIF'")
        print("- 'Greet me as Bob'")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup():
        """Clean up resources"""
        await exit_stack.aclose()
    
    return {
        'connect_to_server': connect_to_server,
        'process_query': process_query,
        'chat_loop': chat_loop,
        'cleanup': cleanup
    }

# Main execution
async def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python ai_mcp_client.py <path_to_server_script>")
        print("Example: python ai_mcp_client.py ../server/petting_zootopia.py")
        sys.exit(1)
    
    # Create client using pure functional composition
    client = create_mcp_client()
    
    try:
        await client['connect_to_server'](sys.argv[1])
        await client['chat_loop']()
    finally:
        await client['cleanup']()

if __name__ == "__main__":
    asyncio.run(main())
