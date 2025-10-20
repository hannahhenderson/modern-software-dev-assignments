from fastmcp import FastMCP
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

mcp = FastMCP("Petting Zootopia MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}!"

@mcp.tool
async def duck() -> str:
    """Get a random duck GIF from the random-d.uk API."""
    duck_url = "https://random-d.uk/api/v2/random"
    
    try:
        logger.info(f"Fetching duck from {duck_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(duck_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            url = data.get("url", "No duck URL found")
            logger.info(f"Successfully fetched duck: {url}")
            return url
    except httpx.TimeoutException:
        logger.error("Timeout fetching duck")
        return "Error: Request timed out while fetching duck"
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching duck: {e.response.status_code}")
        return f"Error: HTTP {e.response.status_code} while fetching duck"
    except Exception as e:
        logger.error(f"Unexpected error fetching duck: {str(e)}")
        return f"Error fetching duck: {str(e)}"

@mcp.tool
async def dog() -> str:
    """Get a random dog image from the dog.ceo API."""
    dog_url = "https://dog.ceo/api/breeds/image/random"
    
    try:
        logger.info(f"Fetching dog from {dog_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(dog_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            url = data.get("message", "No dog URL found")
            logger.info(f"Successfully fetched dog: {url}")
            return url
    except httpx.TimeoutException:
        logger.error("Timeout fetching dog")
        return "Error: Request timed out while fetching dog"
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching dog: {e.response.status_code}")
        return f"Error: HTTP {e.response.status_code} while fetching dog"
    except Exception as e:
        logger.error(f"Unexpected error fetching dog: {str(e)}")
        return f"Error fetching dog: {str(e)}"

@mcp.tool
async def cat() -> str:
    """Get a random cat image from the cat.ceo API."""
    cat_url = "https://api.thecatapi.com/v1/images/search"
    
    try:
        logger.info(f"Fetching cat from {cat_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(cat_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            # The cat API returns an array, so we need to get the first item
            if data and len(data) > 0:
                url = data[0].get("url", "No cat URL found")
                logger.info(f"Successfully fetched cat: {url}")
                return url
            else:
                logger.warning("No cat images found in API response")
                return "No cat images available"
    except httpx.TimeoutException:
        logger.error("Timeout fetching cat")
        return "Error: Request timed out while fetching cat"
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching cat: {e.response.status_code}")
        return f"Error: HTTP {e.response.status_code} while fetching cat"
    except Exception as e:
        logger.error(f"Unexpected error fetching cat: {str(e)}")
        return f"Error fetching cat: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Petting Zootopia MCP Server...")
    mcp.run()