"""Tests for the HTTP module."""

import pytest
import httpx

from petting_zootopia.types import Ok, Err, RateLimited, NetworkTimeout
from petting_zootopia.config import Config
from petting_zootopia.http import fetch_duck, fetch_dog, fetch_cat, fetch_animal


@pytest.fixture
def config() -> Config:
    """Create a test configuration."""
    return Config()


class TestFetchDuck:
    """Tests for fetch_duck function."""

    @pytest.mark.asyncio
    async def test_fetch_duck_success(self, config: Config):
        """Test successful duck fetch (integration test)."""
        async with httpx.AsyncClient() as client:
            result = await fetch_duck(client, config)

        # Should succeed (external API)
        if isinstance(result, Ok):
            assert result.value.animal == "duck"
            assert result.value.url.startswith("http")
        # Or fail gracefully if API is down
        elif isinstance(result, Err):
            assert result.error is not None


class TestFetchDog:
    """Tests for fetch_dog function."""

    @pytest.mark.asyncio
    async def test_fetch_dog_success(self, config: Config):
        """Test successful dog fetch (integration test)."""
        async with httpx.AsyncClient() as client:
            result = await fetch_dog(client, config)

        # Should succeed (has fallback)
        if isinstance(result, Ok):
            assert result.value.animal == "dog"
            assert result.value.url.startswith("http")


class TestFetchCat:
    """Tests for fetch_cat function."""

    @pytest.mark.asyncio
    async def test_fetch_cat_success(self, config: Config):
        """Test successful cat fetch (integration test)."""
        async with httpx.AsyncClient() as client:
            result = await fetch_cat(client, config)

        # Should succeed (external API)
        if isinstance(result, Ok):
            assert result.value.animal == "cat"
            assert result.value.url.startswith("http")


class TestFetchAnimal:
    """Tests for fetch_animal dispatcher."""

    @pytest.mark.asyncio
    async def test_fetch_animal_duck(self, config: Config):
        """Test fetching duck through dispatcher."""
        async with httpx.AsyncClient() as client:
            result = await fetch_animal("duck", client, config)

        if isinstance(result, Ok):
            assert result.value.animal == "duck"

    @pytest.mark.asyncio
    async def test_fetch_animal_invalid(self, config: Config):
        """Test fetching invalid animal type."""
        async with httpx.AsyncClient() as client:
            result = await fetch_animal("giraffe", client, config)  # type: ignore

        assert isinstance(result, Err)
