#!/usr/bin/env python3
"""
Simple HTTP server for the Petting Zootopia web interface.
This is a basic web server that serves the HTML interface.
"""

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import uvicorn

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Petting Zootopia Web Interface", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    """Web server startup."""
    logger.info("Petting Zootopia web server starting...")
    logger.info("Note: Make sure MCP client and server are running separately")

@app.on_event("shutdown")
async def shutdown_event():
    """Web server shutdown."""
    logger.info("Petting Zootopia web server shutting down...")

@app.get("/")
async def serve_index():
    """Serve the main HTML page."""
    return FileResponse("index.html")

@app.post("/api/animal")
async def get_animal(request: dict):
    """
    Get an animal image - placeholder endpoint.
    
    Expected request body:
    {
        "animal": "rabbit|dog|cat",
        "message": "I want a rabbit!"
    }
    """
    try:
        animal_type = request.get("animal", "").lower()
        message = request.get("message", f"I want a {animal_type}!")
        
        if animal_type not in ["rabbit", "dog", "cat"]:
            raise HTTPException(status_code=400, detail="Invalid animal type. Must be rabbit, dog, or cat")
        
        logger.info(f"Processing request for {animal_type}: {message}")
        
        # TODO: This is a placeholder - the web interface needs to be connected
        # to a running MCP client and server to work properly
        return {
            "success": False,
            "error": "MCP client and server not connected. Please run setup.sh option 1 to start all services.",
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
    return {"status": "healthy", "web_server": "running", "mcp_connected": False}

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