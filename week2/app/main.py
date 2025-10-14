from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .models import ErrorResponse
from .routers import action_items, notes

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {e}")
    raise RuntimeError(f"Failed to initialize database: {e}") from e

# Create FastAPI app
app = FastAPI(
    title="Action Item Extractor",
    description="A FastAPI application for extracting action items from text using multiple methods",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Handle validation errors with custom response format."""
    logger.warning(f"Validation error on {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            error="Validation Error",
            detail=str(exc),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ).dict(),
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions with custom response format."""
    logger.warning(f"HTTP error on {request.url}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error=exc.detail, detail=None, status_code=exc.status_code).dict(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions with custom response format."""
    logger.error(f"Unexpected error on {request.url}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail="An unexpected error occurred",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ).dict(),
    )


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    """Serve the main HTML page."""
    try:
        html_path = Path(__file__).resolve().parents[1] / "frontend" / "index.html"
        if not html_path.exists():
            logger.error(f"Frontend file not found: {html_path}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Frontend file not found"
            )
        return html_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error(f"Failed to serve frontend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to serve frontend"
        ) from e


@app.get("/health")
def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy", "service": "action-item-extractor"}


# Include routers
app.include_router(notes.router)
app.include_router(action_items.router)

# Mount static files
static_dir = Path(__file__).resolve().parents[1] / "frontend"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    logger.info(f"Static files mounted at /static from {static_dir}")
else:
    logger.warning(f"Static directory not found: {static_dir}")
