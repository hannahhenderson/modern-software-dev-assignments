"""
MCP Server for Petting Zootopia.

Exposes tools for fetching random animal images via the Model Context Protocol.
Uses functional patterns with explicit dependencies and Result types.
"""

from __future__ import annotations

import asyncio
import logging
import sys

import httpx
from fastmcp import FastMCP

from petting_zootopia.config import Config, load_config
from petting_zootopia.types import (
    Ok,
    Err,
    AnimalImage,
    HealthStatus,
    OverallHealth,
    format_error_message,
    FALLBACK_IMAGES,
)
from petting_zootopia.http import fetch_duck, fetch_dog, fetch_cat

logger = logging.getLogger(__name__)


def create_mcp_server(config: Config) -> FastMCP:
    """
    Create and configure the MCP server.

    All dependencies are explicitly passed. Returns a configured server instance.
    """
    mcp = FastMCP("Petting Zootopia")

    # Create a shared HTTP client - will be used across tool calls
    # This is a controlled side effect, managed at the application boundary
    http_client: httpx.AsyncClient | None = None

    async def get_client() -> httpx.AsyncClient:
        nonlocal http_client
        if http_client is None:
            http_client = httpx.AsyncClient()
        return http_client

    @mcp.tool
    async def duck() -> str:
        """Get a random duck image from the random-d.uk API."""
        client = await get_client()
        result = await fetch_duck(client, config)

        match result:
            case Ok(image):
                return image.url
            case Err(error):
                logger.warning(f"Duck fetch failed: {error}")
                return format_error_message(error)

    @mcp.tool
    async def dog() -> str:
        """Get a random dog image from random.dog or dog.ceo API."""
        client = await get_client()
        result = await fetch_dog(client, config)

        match result:
            case Ok(image):
                return image.url
            case Err(error):
                logger.warning(f"Dog fetch failed: {error}")
                # For dogs, we have a reliable fallback
                return FALLBACK_IMAGES["dog"]

    @mcp.tool
    async def cat() -> str:
        """Get a random cat image from thecatapi.com."""
        client = await get_client()
        result = await fetch_cat(client, config)

        match result:
            case Ok(image):
                return image.url
            case Err(error):
                logger.warning(f"Cat fetch failed: {error}")
                return format_error_message(error)

    @mcp.tool
    def ping() -> str:
        """Check if the MCP server is running."""
        return "pong"

    @mcp.tool
    async def health_check() -> str:
        """Check the health status of all external animal APIs."""
        client = await get_client()
        health = await check_all_apis(client, config)

        lines = [
            f"Overall Status: {health.status.upper()}",
            f"Healthy APIs: {health.healthy_count}/{health.total_count}",
            "",
        ]

        for api in health.apis:
            status = "HEALTHY" if api.healthy else "UNHEALTHY"
            time_str = f" ({api.response_time_ms:.0f}ms)" if api.response_time_ms else ""
            error_str = f" - {api.error}" if api.error else ""
            lines.append(f"{api.api.upper()}: {status}{time_str}{error_str}")

        return "\n".join(lines)

    return mcp


async def check_api_health(
    name: str, url: str, client: httpx.AsyncClient, timeout: float
) -> HealthStatus:
    """Check health of a single API endpoint."""
    import time

    start = time.monotonic()
    try:
        response = await client.get(url, timeout=timeout)
        elapsed_ms = (time.monotonic() - start) * 1000

        if response.status_code == 200:
            return HealthStatus(api=name, healthy=True, response_time_ms=elapsed_ms)
        else:
            return HealthStatus(
                api=name,
                healthy=False,
                response_time_ms=elapsed_ms,
                error=f"Status {response.status_code}",
            )
    except Exception as e:
        elapsed_ms = (time.monotonic() - start) * 1000
        return HealthStatus(api=name, healthy=False, response_time_ms=elapsed_ms, error=str(e))


async def check_all_apis(client: httpx.AsyncClient, config: Config) -> OverallHealth:
    """Check health of all configured APIs concurrently."""
    apis = [
        ("duck", config.duck_api_url),
        ("dog", config.dog_api_url),
        ("cat", config.cat_api_url),
    ]

    # Check all APIs concurrently
    results = await asyncio.gather(
        *[check_api_health(name, url, client, config.http_timeout) for name, url in apis]
    )

    # Determine overall status
    healthy_count = sum(1 for r in results if r.healthy)
    total = len(results)

    if healthy_count == total:
        status = "healthy"
    elif healthy_count > 0:
        status = "degraded"
    else:
        status = "unhealthy"

    return OverallHealth(status=status, apis=tuple(results))


def main() -> None:
    """Entry point for the MCP server."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    config = load_config()
    logger.info("Starting Petting Zootopia MCP Server...")

    mcp = create_mcp_server(config)
    mcp.run()


if __name__ == "__main__":
    main()
