"""
HTTP client functions for fetching animal images.

All functions are pure and return Result types for explicit error handling.
No exceptions are raised - all errors are captured in the return type.
"""

from __future__ import annotations

import httpx
import logging

from petting_zootopia.types import (
    Ok,
    Err,
    Result,
    AnimalImage,
    AnimalType,
    APIError,
    NetworkTimeout,
    RateLimited,
    HttpError,
    ConnectionFailed,
    ParseError,
)
from petting_zootopia.config import Config

logger = logging.getLogger(__name__)


def _handle_httpx_error(error: httpx.HTTPError, animal: AnimalType) -> APIError:
    """Convert httpx exceptions to our error types. Pure function."""
    match error:
        case httpx.TimeoutException():
            return NetworkTimeout(animal=animal, timeout_seconds=10.0)
        case httpx.ConnectError():
            return ConnectionFailed(animal=animal, reason=str(error))
        case httpx.HTTPStatusError() as e:
            if e.response.status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                return RateLimited(animal=animal, retry_after=retry_after)
            return HttpError(
                animal=animal,
                status_code=e.response.status_code,
                message=str(error),
            )
        case _:
            return ConnectionFailed(animal=animal, reason=str(error))


async def fetch_duck(client: httpx.AsyncClient, config: Config) -> Result[AnimalImage, APIError]:
    """
    Fetch a random duck image.

    Pure async function - all dependencies are explicit parameters.
    Returns Result type for explicit error handling.
    """
    try:
        logger.debug(f"Fetching duck from {config.duck_api_url}")
        response = await client.get(config.duck_api_url, timeout=config.http_timeout)
        response.raise_for_status()

        data = response.json()
        url = data.get("url")

        if not url:
            return Err(ParseError(animal="duck", details="No 'url' field in response"))

        logger.info(f"Successfully fetched duck: {url}")
        return Ok(AnimalImage(url=url, animal="duck"))

    except httpx.HTTPError as e:
        error = _handle_httpx_error(e, "duck")
        logger.warning(f"Duck API error: {error}")
        return Err(error)
    except Exception as e:
        logger.error(f"Unexpected error fetching duck: {e}")
        return Err(ParseError(animal="duck", details=str(e)))


async def fetch_dog(client: httpx.AsyncClient, config: Config) -> Result[AnimalImage, APIError]:
    """
    Fetch a random dog image with fallback.

    Tries primary API first, falls back to secondary on failure.
    Pure async function with explicit dependencies.
    """
    # Try primary API
    primary_result = await _fetch_dog_primary(client, config)
    if isinstance(primary_result, Ok):
        return primary_result

    # Try fallback API
    logger.info("Primary dog API failed, trying fallback")
    fallback_result = await _fetch_dog_fallback(client, config)
    if isinstance(fallback_result, Ok):
        return fallback_result

    # Return the original error if both fail
    return primary_result


async def _fetch_dog_primary(
    client: httpx.AsyncClient, config: Config
) -> Result[AnimalImage, APIError]:
    """Fetch from primary dog API (random.dog)."""
    try:
        logger.debug(f"Fetching dog from {config.dog_api_url}")
        response = await client.get(config.dog_api_url, timeout=config.http_timeout)
        response.raise_for_status()

        data = response.json()
        url = data.get("url", "")

        # Validate it's an image URL
        if url and url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            logger.info(f"Successfully fetched dog: {url}")
            return Ok(AnimalImage(url=url, animal="dog"))

        return Err(ParseError(animal="dog", details=f"Invalid URL format: {url}"))

    except httpx.HTTPError as e:
        return Err(_handle_httpx_error(e, "dog"))
    except Exception as e:
        return Err(ParseError(animal="dog", details=str(e)))


async def _fetch_dog_fallback(
    client: httpx.AsyncClient, config: Config
) -> Result[AnimalImage, APIError]:
    """Fetch from fallback dog API (dog.ceo)."""
    try:
        logger.debug(f"Fetching dog from fallback: {config.dog_fallback_url}")
        response = await client.get(config.dog_fallback_url, timeout=config.http_timeout)
        response.raise_for_status()

        data = response.json()
        url = data.get("message", "")

        if url and url.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".webp")):
            logger.info(f"Successfully fetched dog from fallback: {url}")
            return Ok(AnimalImage(url=url, animal="dog"))

        return Err(ParseError(animal="dog", details=f"Invalid fallback URL: {url}"))

    except httpx.HTTPError as e:
        return Err(_handle_httpx_error(e, "dog"))
    except Exception as e:
        return Err(ParseError(animal="dog", details=str(e)))


async def fetch_cat(client: httpx.AsyncClient, config: Config) -> Result[AnimalImage, APIError]:
    """
    Fetch a random cat image.

    Pure async function with explicit dependencies.
    """
    try:
        logger.debug(f"Fetching cat from {config.cat_api_url}")
        response = await client.get(config.cat_api_url, timeout=config.http_timeout)
        response.raise_for_status()

        data = response.json()

        # Cat API returns an array
        if not data or len(data) == 0:
            return Err(ParseError(animal="cat", details="Empty response from API"))

        url = data[0].get("url")
        if not url:
            return Err(ParseError(animal="cat", details="No 'url' field in response"))

        logger.info(f"Successfully fetched cat: {url}")
        return Ok(AnimalImage(url=url, animal="cat"))

    except httpx.HTTPError as e:
        error = _handle_httpx_error(e, "cat")
        logger.warning(f"Cat API error: {error}")
        return Err(error)
    except Exception as e:
        logger.error(f"Unexpected error fetching cat: {e}")
        return Err(ParseError(animal="cat", details=str(e)))


# Function dispatch table - maps animal type to fetch function
FETCHERS = {
    "duck": fetch_duck,
    "dog": fetch_dog,
    "cat": fetch_cat,
}


async def fetch_animal(
    animal: AnimalType, client: httpx.AsyncClient, config: Config
) -> Result[AnimalImage, APIError]:
    """
    Fetch an animal image by type.

    Dispatches to the appropriate fetcher function.
    """
    fetcher = FETCHERS.get(animal)
    if fetcher is None:
        return Err(ParseError(animal=animal, details=f"Unknown animal type: {animal}"))
    return await fetcher(client, config)
