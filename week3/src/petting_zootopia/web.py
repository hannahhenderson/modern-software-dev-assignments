"""
Web interface for Petting Zootopia.

FastAPI application that provides a web UI and REST API for fetching animal images.
Uses functional patterns with explicit dependencies and Result types.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

from petting_zootopia.config import Config, load_config
from petting_zootopia.types import Ok, Err, RateLimited, FALLBACK_IMAGES
from petting_zootopia.http import fetch_animal, FETCHERS

logger = logging.getLogger(__name__)


# =============================================================================
# Request/Response Models
# =============================================================================


class AnimalRequest(BaseModel):
    """Request body for animal endpoint."""

    query: str | None = None
    animal: str | None = None  # Legacy support


class AnimalResponse(BaseModel):
    """Successful animal response."""

    success: bool = True
    image_url: str
    animal: str
    message: str | None = None


class ErrorResponse(BaseModel):
    """Error response."""

    success: bool = False
    error: str
    retry_after: int | None = None


# =============================================================================
# Application Factory
# =============================================================================


def extract_animal_from_query(query: str) -> str | None:
    """Extract animal type from a natural language query. Pure function."""
    query_lower = query.lower()
    for animal in FETCHERS.keys():
        if animal in query_lower:
            return animal
    return None


def create_app(config: Config) -> FastAPI:
    """
    Create the FastAPI application with all dependencies injected.

    This is the application factory - all configuration is explicit.
    """
    # Rate limiter setup
    limiter = Limiter(key_func=get_remote_address)

    # Shared HTTP client - managed at app lifecycle level
    http_client: httpx.AsyncClient | None = None

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
        """Manage application lifecycle."""
        nonlocal http_client
        http_client = httpx.AsyncClient()
        logger.info("Petting Zootopia web server started")
        yield
        await http_client.aclose()
        logger.info("Petting Zootopia web server stopped")

    app = FastAPI(
        title="Petting Zootopia",
        description="A functional API for fetching random animal images",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Configure rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Determine paths for static files
    # Support both development (src/petting_zootopia) and installed package
    web_dir = Path(__file__).parent.parent.parent / "web"
    if not web_dir.exists():
        web_dir = Path(__file__).parent / "web"

    # Mount static files if directory exists
    assets_dir = web_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    # =============================================================================
    # Routes
    # =============================================================================

    @app.get("/")
    async def index() -> FileResponse:
        """Serve the main page."""
        index_path = web_dir / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))
        raise HTTPException(status_code=404, detail="Index page not found")

    @app.get("/about.html")
    async def about() -> FileResponse:
        """Serve the about page."""
        about_path = web_dir / "about.html"
        if about_path.exists():
            return FileResponse(str(about_path))
        raise HTTPException(status_code=404, detail="About page not found")

    @app.post("/api/animal")
    @limiter.limit(config.rate_limit)
    async def get_animal(request: Request, body: AnimalRequest) -> JSONResponse:
        """
        Get a random animal image.

        Accepts either a natural language query or explicit animal type.
        Returns Result-style response with explicit success/error states.
        """
        if http_client is None:
            raise HTTPException(status_code=503, detail="Server not ready")

        # Determine which animal to fetch
        animal: str | None = None
        query = body.query or ""

        if body.animal:
            animal = body.animal.lower()
        elif query:
            animal = extract_animal_from_query(query)

        if not animal or animal not in FETCHERS:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=f"Unknown animal. Supported: {', '.join(FETCHERS.keys())}"
                ).model_dump(),
            )

        # Fetch the animal image
        result = await fetch_animal(animal, http_client, config)  # type: ignore

        match result:
            case Ok(image):
                return JSONResponse(
                    content=AnimalResponse(
                        image_url=image.url,
                        animal=image.animal,
                        message=query or f"Here's a {animal}!",
                    ).model_dump()
                )

            case Err(RateLimited(retry_after=retry)):
                retry_seconds = int(retry) if retry else 60
                return JSONResponse(
                    status_code=429,
                    headers={"Retry-After": str(retry_seconds)},
                    content=ErrorResponse(
                        error="External API rate limited. Please try again later.",
                        retry_after=retry_seconds,
                    ).model_dump(),
                )

            case Err(error):
                logger.warning(f"Animal fetch failed: {error}")
                # Return fallback image instead of error
                fallback_url = FALLBACK_IMAGES.get(animal, FALLBACK_IMAGES["dog"])
                return JSONResponse(
                    content=AnimalResponse(
                        image_url=fallback_url,
                        animal=animal,  # type: ignore
                        message=f"Here's a {animal} (from our backup collection)!",
                    ).model_dump()
                )

    @app.get("/api/health")
    @limiter.limit(config.rate_limit)
    async def health_check(request: Request) -> dict:
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": "petting-zootopia-web",
        }

    @app.get("/api/animals")
    async def list_animals() -> dict:
        """List available animal types."""
        return {
            "animals": list(FETCHERS.keys()),
        }

    return app


# =============================================================================
# Entry Points
# =============================================================================


def main() -> None:
    """Entry point for the web server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    config = load_config()
    app = create_app(config)

    logger.info(f"Starting web server on {config.host}:{config.port}")
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level,
    )


# For uvicorn direct invocation: uvicorn petting_zootopia.web:app
def get_app() -> FastAPI:
    """Get app instance for uvicorn."""
    return create_app(load_config())


app = get_app()


if __name__ == "__main__":
    main()
