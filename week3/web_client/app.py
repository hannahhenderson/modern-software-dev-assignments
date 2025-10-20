#!/usr/bin/env python3
"""
HTTP server that demonstrates MCP client/server interaction.
This web interface properly uses the MCP client to communicate with the MCP server.
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the MCP client
sys.path.append(str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

# Import our MCP client
import sys
sys.path.append(str(Path(__file__).parent.parent / "mcp_client"))
from ai_mcp_client import create_mcp_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Petting Zootopia MCP Web Interface", version="1.0.0")

# Mount static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# Global variable to store the MCP client
mcp_client = None

@app.on_event("startup")
async def startup_event():
    """Initialize the MCP client when the server starts."""
    global mcp_client
    try:
        # Get the server path
        server_path = Path(__file__).parent.parent / "server" / "petting_zootopia.py"
        
        if not server_path.exists():
            raise FileNotFoundError(f"Server file not found: {server_path}")
        
        # Create the MCP client
        mcp_client = create_mcp_client()
        
        # Connect to the server
        await mcp_client["connect_to_server"](str(server_path))
        logger.info("Successfully connected to MCP server")
        
    except Exception as e:
        logger.error(f"Failed to initialize MCP client: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up when the server shuts down."""
    global mcp_client
    if mcp_client:
        try:
            await mcp_client["cleanup"]()
            logger.info("MCP client cleaned up")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    return FileResponse("index.html")

@app.post("/api/animal")
async def get_animal(request: dict):
    """
    Get an animal image using the MCP client.
    This demonstrates proper MCP client/server interaction.
    
    Expected request body:
    {
        "query": "I want a duck!",
        "animal": "duck|dog|cat" (optional, for backward compatibility)
    }
    """
    global mcp_client
    
    if not mcp_client:
        raise HTTPException(status_code=500, detail="MCP client not initialized")
    
    try:
        # Handle new query format or fallback to old format
        query = request.get("query")
        if not query:
            # Backward compatibility
            animal_type = request.get("animal", "").lower()
            query = f"I want a {animal_type}!"
        
        logger.info(f"Processing query: {query}")
        
        # Use the MCP client to process the query - this is the proper MCP flow!
        result = await mcp_client["process_query"](query)
        
        if not result or not result.strip():
            raise HTTPException(status_code=500, detail="No result from MCP client")
        
        # Check if the MCP client indicates no tools are available
        if "no tools" in result.lower() or "no available tools" in result.lower() or "i don't have" in result.lower():
            logger.info("MCP client indicates no tools available for this query")
            return {
                "success": False,
                "noTools": True,
                "message": "Sorry, I don't have tools for that request! Try asking for a duck, dog, or cat.",
                "query": query
            }
        
        # Extract the actual image URL from the MCP response
        # The MCP client returns a conversation that includes metadata
        # We need to find the actual URL in the response
        import re
        
        # Look for URLs in the response - improved regex to handle trailing punctuation
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\],\']+'
        urls = re.findall(url_pattern, result)
        
        if not urls:
            logger.error(f"No URL found in MCP response: {result}")
            return {
                "success": False,
                "error": "No image URL found in response",
                "query": query
            }
        
        # Use the first URL found (should be the image URL)
        image_url = urls[0]
        logger.info(f"Extracted image URL: {image_url}")
        
        # Try to determine animal type from the query for better UX
        animal_type = "animal"
        if "duck" in query.lower():
            animal_type = "duck"
        elif "dog" in query.lower():
            animal_type = "dog"
        elif "cat" in query.lower():
            animal_type = "cat"
        
        return {
            "success": True,
            "imageUrl": image_url,
            "animal": animal_type,
            "message": query
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing animal request: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "web_server": "running", "mcp_connected": mcp_client is not None}

if __name__ == "__main__":
    # Change to the web directory
    import os
    os.chdir(Path(__file__).parent)
    
    # Run the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )