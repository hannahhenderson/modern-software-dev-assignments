import asyncio
from fastmcp import Client

client = Client("http://localhost:8000/mcp")

async def list_tools():
    """List all available tools from the MCP server."""
    async with client:
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        return tools

async def call_tool(name: str):
    async with client:
        result = await client.call_tool("greet", {"name": name})
        print(result)

# Test the list_tools function
asyncio.run(list_tools())
