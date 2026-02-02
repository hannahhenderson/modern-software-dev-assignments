"""
Configuration management using Pydantic Settings.

All configuration is loaded from environment variables with sensible defaults.
Configuration is immutable once loaded.
"""

from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    Application configuration loaded from environment variables.

    All fields are immutable after initialization (frozen=True equivalent
    via model_config).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        frozen=True,
    )

    # AI Backend Configuration
    ai_backend: Literal["ollama", "claude_haiku", "claude_sonnet"] = Field(
        default="ollama",
        description="Which AI backend to use for processing queries",
    )
    ollama_url: str = Field(
        default="http://localhost:11434/api/generate",
        description="Ollama API endpoint",
    )
    ollama_model: str = Field(
        default="llama3.2:3b",
        description="Ollama model to use",
    )
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude backends",
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Host to bind to")
    port: int = Field(default=8000, description="Port to bind to")
    reload: bool = Field(default=False, description="Enable auto-reload for development")
    log_level: Literal["debug", "info", "warning", "error"] = Field(
        default="info",
        description="Logging level",
    )

    # HTTP Client Configuration
    http_timeout: float = Field(
        default=10.0,
        description="Timeout for external API requests in seconds",
    )

    # Rate Limiting (web layer)
    rate_limit: str = Field(
        default="10/minute",
        description="Rate limit for API endpoints",
    )

    # External API URLs
    duck_api_url: str = Field(
        default="https://random-d.uk/api/v2/random",
        description="Random duck API endpoint",
    )
    dog_api_url: str = Field(
        default="https://random.dog/woof.json",
        description="Random dog API endpoint",
    )
    dog_fallback_url: str = Field(
        default="https://dog.ceo/api/breeds/image/random",
        description="Fallback dog API endpoint",
    )
    cat_api_url: str = Field(
        default="https://api.thecatapi.com/v1/images/search",
        description="Random cat API endpoint",
    )

    # Observability (optional)
    honeycomb_api_key: str | None = Field(
        default=None,
        description="Honeycomb API key for observability",
    )
    honeycomb_dataset: str = Field(
        default="petting-zootopia",
        description="Honeycomb dataset name",
    )


def load_config() -> Config:
    """Load configuration from environment. Pure function that returns immutable config."""
    return Config()
