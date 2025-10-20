from fastmcp import FastMCP
import httpx

mcp = FastMCP("My MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

@mcp.tool
async def duck() -> str:
    """Get a random duck GIF from the random-d.uk API."""
    duck_url = "https://random-d.uk/api/v2/random"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(duck_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("url", "No duck URL found")
    except Exception as e:
        return f"Error fetching duck: {str(e)}"

@mcp.tool
async def dog() -> str:
    """Get a random dog image from the dog.ceo API."""
    dog_url = "https://dog.ceo/api/breeds/image/random"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(dog_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("url", "No dog URL found")
    except Exception as e:
        return f"Error fetching dog: {str(e)}"

@mcp.tool
async def cat() -> str:
    """Get a random cat image from the cat.ceo API."""
    cat_url = "https://api.thecatapi.com/v1/images/search"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(cat_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return data.get("url", "No cat URL found")
    except Exception as e:
        return f"Error fetching cat: {str(e)}"


if __name__ == "__main__":
    mcp.run()