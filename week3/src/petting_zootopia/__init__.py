"""
Petting Zootopia - A functional MCP server for fetching random animal images.

This package provides:
- An MCP server with tools for fetching duck, dog, and cat images
- A web interface for interacting with the MCP server
- An AI-powered client supporting multiple backends (Ollama, Claude)

Designed with functional programming principles:
- Result types instead of exceptions
- Immutable data structures
- Explicit dependencies
- Pure functions where possible
"""

from petting_zootopia.types import Ok, Err, Result
from petting_zootopia.config import Config

__version__ = "1.0.0"
__all__ = ["Ok", "Err", "Result", "Config", "__version__"]
