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
import uvicorn

# Import our MCP client
from client.ai_mcp_client import create_mcp_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Petting Zootopia MCP Web Interface", version="1.0.0")

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
        "animal": "duck|dog|cat",
        "message": "I want a duck!"
    }
    """
    global mcp_client
    
    if not mcp_client:
        raise HTTPException(status_code=500, detail="MCP client not initialized")
    
    try:
        animal_type = request.get("animal", "").lower()
        message = request.get("message", f"I want a {animal_type}!")
        
        if animal_type not in ["duck", "dog", "cat"]:
            raise HTTPException(status_code=400, detail="Invalid animal type. Must be duck, dog, or cat")
        
        logger.info(f"Processing request for {animal_type}: {message}")
        
        # Use the MCP client to process the query - this is the proper MCP flow!
        result = await mcp_client["process_query"](message)
        
        if not result or not result.strip():
            raise HTTPException(status_code=500, detail="No result from MCP client")
        
        # The result should be a URL to an image
        return {
            "success": True,
            "imageUrl": result.strip(),
            "animal": animal_type,
            "message": message
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