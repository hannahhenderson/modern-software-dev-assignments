"""
Core types for Petting Zootopia.

Implements Result types for explicit error handling following functional programming
principles. Inspired by Rust's Result type and similar patterns in typed functional
programming.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import TypeVar, Generic, Callable, Literal

T = TypeVar("T")
U = TypeVar("U")
E = TypeVar("E")


# =============================================================================
# Result Type - Explicit Error Handling
# =============================================================================


@dataclass(frozen=True, slots=True)
class Ok(Generic[T]):
    """Represents a successful result containing a value."""

    value: T

    def is_ok(self) -> bool:
        return True

    def is_err(self) -> bool:
        return False

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """Apply a function to the contained value if Ok."""
        return Ok(fn(self.value))

    def unwrap(self) -> T:
        """Get the value. Safe to call on Ok."""
        return self.value

    def unwrap_or(self, default: T) -> T:
        """Get the value or return default."""
        return self.value


@dataclass(frozen=True, slots=True)
class Err(Generic[E]):
    """Represents a failed result containing an error."""

    error: E

    def is_ok(self) -> bool:
        return False

    def is_err(self) -> bool:
        return True

    def map(self, fn: Callable[[T], U]) -> Result[U, E]:
        """Return self unchanged since this is an error."""
        return self  # type: ignore

    def unwrap(self) -> T:
        """Raises the error since this is an Err."""
        raise ValueError(f"Called unwrap on Err: {self.error}")

    def unwrap_or(self, default: T) -> T:
        """Return the default since this is an error."""
        return default


# Union type for Result
Result = Ok[T] | Err[E]


# =============================================================================
# Animal Types
# =============================================================================

AnimalType = Literal["duck", "dog", "cat"]

SUPPORTED_ANIMALS: tuple[AnimalType, ...] = ("duck", "dog", "cat")


# =============================================================================
# Error Types - Immutable, Exhaustive
# =============================================================================


class ErrorKind(Enum):
    """Enumeration of all possible error kinds."""

    NETWORK_TIMEOUT = auto()
    RATE_LIMITED = auto()
    HTTP_ERROR = auto()
    CONNECTION_FAILED = auto()
    PARSE_ERROR = auto()
    VALIDATION_ERROR = auto()
    NOT_FOUND = auto()
    UNKNOWN = auto()


@dataclass(frozen=True, slots=True)
class NetworkTimeout:
    """Request timed out."""

    animal: AnimalType
    timeout_seconds: float

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.NETWORK_TIMEOUT


@dataclass(frozen=True, slots=True)
class RateLimited:
    """External API rate limit exceeded."""

    animal: AnimalType
    retry_after: str | None = None

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.RATE_LIMITED


@dataclass(frozen=True, slots=True)
class HttpError:
    """HTTP error from external API."""

    animal: AnimalType
    status_code: int
    message: str = ""

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.HTTP_ERROR


@dataclass(frozen=True, slots=True)
class ConnectionFailed:
    """Could not connect to external API."""

    animal: AnimalType
    reason: str = ""

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.CONNECTION_FAILED


@dataclass(frozen=True, slots=True)
class ParseError:
    """Failed to parse API response."""

    animal: AnimalType
    details: str = ""

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.PARSE_ERROR


@dataclass(frozen=True, slots=True)
class ValidationError:
    """Input validation failed."""

    field: str
    message: str

    @property
    def kind(self) -> ErrorKind:
        return ErrorKind.VALIDATION_ERROR


# Union of all API errors
APIError = NetworkTimeout | RateLimited | HttpError | ConnectionFailed | ParseError


# =============================================================================
# Response Types
# =============================================================================


@dataclass(frozen=True, slots=True)
class AnimalImage:
    """Successful animal image response."""

    url: str
    animal: AnimalType


@dataclass(frozen=True, slots=True)
class HealthStatus:
    """Health check result for an API."""

    api: str
    healthy: bool
    response_time_ms: float | None = None
    error: str | None = None


@dataclass(frozen=True, slots=True)
class OverallHealth:
    """Overall system health."""

    status: Literal["healthy", "degraded", "unhealthy"]
    apis: tuple[HealthStatus, ...]

    @property
    def healthy_count(self) -> int:
        return sum(1 for api in self.apis if api.healthy)

    @property
    def total_count(self) -> int:
        return len(self.apis)


# =============================================================================
# User-Friendly Error Messages
# =============================================================================


def format_error_message(error: APIError) -> str:
    """Convert an API error to a user-friendly message."""
    match error:
        case RateLimited(animal=animal):
            return f"The {animal} API is busy right now. Please try again in a moment."
        case NetworkTimeout(animal=animal):
            return f"The {animal}s are being shy and taking their time. Please try again!"
        case HttpError(animal=animal, status_code=code) if code >= 500:
            return f"The {animal} API is temporarily unavailable. Please try again later."
        case HttpError(animal=animal):
            return f"The {animal} API is having issues. Please try again later."
        case ConnectionFailed(animal=animal):
            return f"Unable to connect to the {animal} API. Please check your connection."
        case ParseError(animal=animal):
            return f"Got an unexpected response from the {animal} API. Please try again."
        case _:
            return "Something went wrong. Please try again later."


# Fallback images for when APIs fail
FALLBACK_IMAGES: dict[AnimalType, str] = {
    "duck": "https://i.pinimg.com/736x/c2/16/df/c216df7a2af5dc737c9b2041ef295835.jpg",
    "dog": "https://images.dog.ceo/breeds/retriever-golden/n02099601_1004.jpg",
    "cat": "https://cdn2.thecatapi.com/images/MTY3ODIyMQ.jpg",
}
