from fastmcp import FastMCP
import httpx
import logging
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rate_limiter import wait_for_rate_limit, check_api_rate_limit
from error_handling import handle_httpx_error, get_user_friendly_message, validate_input, PettingZooError
from health_check import get_health_status

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Petting Zootopia MCP Server")

@mcp.tool
def greet(name: str) -> str:
    """Greet a person by name."""
    try:
        validate_input(name)
        return f"Hello, {name}!"
    except PettingZooError as e:
        logger.error(f"Validation error in greet: {e.message}")
        return f"Error: {e.message}"
    except Exception as e:
        logger.error(f"Unexpected error in greet: {str(e)}")
        return f"Error: {str(e)}"

@mcp.tool
async def duck() -> str:
    """Get a random duck GIF from the random-d.uk API."""
    try:
        # Check rate limit first
        rate_info = await check_api_rate_limit('duck')
        if rate_info.status.value == 'exceeded':
            logger.warning("Duck API rate limit exceeded")
            return "Error: Duck API rate limit exceeded. Please try again later."
        
        # Wait for rate limit if needed
        await wait_for_rate_limit('duck')
        
        duck_url = "https://random-d.uk/api/v2/random"
        logger.info(f"Fetching duck from {duck_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(duck_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            url = data.get("url", "No duck URL found")
            logger.info(f"Successfully fetched duck: {url}")
            return url
    
    except httpx.HTTPError as e:
        error = handle_httpx_error(e, "duck")
        logger.error(f"Duck API error: {error.message}")
        return get_user_friendly_message(error, "duck")
    except Exception as e:
        logger.error(f"Unexpected error fetching duck: {str(e)}")
        return f"Error fetching duck: {str(e)}"

@mcp.tool
async def dog() -> str:
    """Get a random dog image from random.dog API."""
    try:
        # Check rate limit first
        rate_info = await check_api_rate_limit('dog')
        if rate_info.status.value == 'exceeded':
            logger.warning("Dog API rate limit exceeded")
            return "Error: Dog API rate limit exceeded. Please try again later."
        
        # Wait for rate limit if needed
        await wait_for_rate_limit('dog')
        
        dog_url = "https://random.dog/woof.json"
        logger.info(f"Fetching dog from {dog_url}")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(dog_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            # Random.dog returns direct image URLs
            if data and 'url' in data and data['url']:
                url = data['url']
                logger.info(f"Successfully fetched dog: {url}")
                return url
            else:
                logger.warning("No dog image found in API response, trying fallback")
                # Fallback to original dog.ceo API
                fallback_url = "https://dog.ceo/api/breeds/image/random"
                fallback_response = await client.get(fallback_url, timeout=10.0)
                fallback_response.raise_for_status()
                fallback_data = fallback_response.json()
                url = fallback_data.get("message", "No dog URL found")
                logger.info(f"Successfully fetched dog from fallback: {url}")
                return url
    
    except httpx.HTTPError as e:
        error = handle_httpx_error(e, "dog")
        logger.error(f"Dog API error: {error.message}")
        return get_user_friendly_message(error, "dog")
    except Exception as e:
        logger.error(f"Unexpected error fetching dog: {str(e)}")
        return f"Error fetching dog: {str(e)}"

@mcp.tool
async def cat() -> str:
    """Get a random cat image from the cat.ceo API."""
    try:
        # Check rate limit first
        rate_info = await check_api_rate_limit('cat')
        if rate_info.status.value == 'exceeded':
            logger.warning("Cat API rate limit exceeded")
            return "Error: Cat API rate limit exceeded. Please try again later."
        
        # Wait for rate limit if needed
        await wait_for_rate_limit('cat')
        
        cat_url = "https://api.thecatapi.com/v1/images/search"
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
    
    except httpx.HTTPError as e:
        error = handle_httpx_error(e, "cat")
        logger.error(f"Cat API error: {error.message}")
        return get_user_friendly_message(error, "cat")
    except Exception as e:
        logger.error(f"Unexpected error fetching cat: {str(e)}")
        return f"Error fetching cat: {str(e)}"


@mcp.tool
def ping() -> str:
    """Simple ping endpoint to check if the MCP server is running."""
    try:
        logger.info("Ping request received")
        return "pong"
    except Exception as e:
        logger.error(f"Ping failed: {str(e)}")
        return f"Ping failed: {str(e)}"


if __name__ == "__main__":
    logger.info("Starting Petting Zootopia MCP Server...")
    mcp.run()