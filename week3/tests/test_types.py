"""Tests for the types module."""

import pytest
from petting_zootopia.types import (
    Ok,
    Err,
    AnimalImage,
    RateLimited,
    NetworkTimeout,
    HttpError,
    format_error_message,
    FALLBACK_IMAGES,
)


class TestResult:
    """Tests for Result type (Ok/Err)."""

    def test_ok_is_ok(self):
        result = Ok("value")
        assert result.is_ok() is True
        assert result.is_err() is False

    def test_err_is_err(self):
        result = Err("error")
        assert result.is_ok() is False
        assert result.is_err() is True

    def test_ok_unwrap(self):
        result = Ok("value")
        assert result.unwrap() == "value"

    def test_err_unwrap_raises(self):
        result = Err("error")
        with pytest.raises(ValueError):
            result.unwrap()

    def test_ok_unwrap_or(self):
        result = Ok("value")
        assert result.unwrap_or("default") == "value"

    def test_err_unwrap_or(self):
        result = Err("error")
        assert result.unwrap_or("default") == "default"

    def test_ok_map(self):
        result = Ok(5)
        mapped = result.map(lambda x: x * 2)
        assert isinstance(mapped, Ok)
        assert mapped.unwrap() == 10

    def test_err_map(self):
        result = Err("error")
        mapped = result.map(lambda x: x * 2)
        assert isinstance(mapped, Err)
        assert mapped.error == "error"

    def test_ok_is_frozen(self):
        result = Ok("value")
        with pytest.raises(AttributeError):
            result.value = "new_value"  # type: ignore

    def test_err_is_frozen(self):
        result = Err("error")
        with pytest.raises(AttributeError):
            result.error = "new_error"  # type: ignore


class TestAnimalImage:
    """Tests for AnimalImage dataclass."""

    def test_creation(self):
        image = AnimalImage(url="https://example.com/duck.jpg", animal="duck")
        assert image.url == "https://example.com/duck.jpg"
        assert image.animal == "duck"

    def test_is_frozen(self):
        image = AnimalImage(url="https://example.com/duck.jpg", animal="duck")
        with pytest.raises(AttributeError):
            image.url = "new_url"  # type: ignore


class TestErrorTypes:
    """Tests for error types."""

    def test_rate_limited(self):
        error = RateLimited(animal="duck", retry_after="60")
        assert error.animal == "duck"
        assert error.retry_after == "60"

    def test_network_timeout(self):
        error = NetworkTimeout(animal="cat", timeout_seconds=10.0)
        assert error.animal == "cat"
        assert error.timeout_seconds == 10.0

    def test_http_error(self):
        error = HttpError(animal="dog", status_code=500, message="Server error")
        assert error.animal == "dog"
        assert error.status_code == 500


class TestFormatErrorMessage:
    """Tests for format_error_message function."""

    def test_rate_limited_message(self):
        error = RateLimited(animal="duck")
        message = format_error_message(error)
        assert "duck" in message
        assert "busy" in message.lower()

    def test_timeout_message(self):
        error = NetworkTimeout(animal="cat", timeout_seconds=10.0)
        message = format_error_message(error)
        assert "cat" in message

    def test_server_error_message(self):
        error = HttpError(animal="dog", status_code=503)
        message = format_error_message(error)
        assert "dog" in message
        assert "unavailable" in message.lower()


class TestFallbackImages:
    """Tests for fallback images."""

    def test_all_animals_have_fallbacks(self):
        for animal in ["duck", "dog", "cat"]:
            assert animal in FALLBACK_IMAGES
            assert FALLBACK_IMAGES[animal].startswith("https://")
