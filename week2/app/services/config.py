"""Configuration management for action item extraction."""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

logger = logging.getLogger(__name__)

# Type definitions
ExtractionMethod = Literal["heuristic", "llm_detailed", "llm_simple"]
ModelName = Literal["qwen2.5:0.5b", "phi3:mini", "llama3.2:1b"]


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for LLM model parameters."""

    model: str
    temperature: float
    top_p: float
    num_predict: int
    stop_sequences: tuple[str, ...]


# Constants
MAX_ACTION_LENGTH = 200
MAX_TOKENS_DETAILED = 150
MAX_TOKENS_SIMPLE = 50

# Model-specific stop sequences
QWEN_STOP_SEQUENCES = (
    "\n\n",
    "Explanation:",
    "Note:",
    "Summary:",
    "```",
    "```json",
    "{",
    "[",
    "Step",
    "Process",
    "Scan",
    "Check",
    "Identify",
    "Action",
    "Items",
    "Found",
)

PHI_STOP_SEQUENCES = (
    "\n\n",
    "Output Explanation:",
    "Explanation:",
    "Note:",
    "Summary:",
    "Output:",
    "Result:",
    "Here are",
    "The extracted",
    "```",
    "```json",
    "{",
    "[",
    "Step",
    "Process",
)

DEFAULT_STOP_SEQUENCES = ("\n\n", "Explanation:", "```", "{", "[")


@lru_cache(maxsize=32)
def get_llm_config(model: str) -> LLMConfig:
    """
    Get LLM configuration for a specific model.

    Args:
        model: The model name (e.g., 'qwen2.5:0.5b', 'phi3:mini')

    Returns:
        LLMConfig object containing model configuration parameters

    Raises:
        ValueError: If model is not supported
    """
    if not isinstance(model, str) or not model.strip():
        raise ValueError("Model name must be a non-empty string")

    model = model.strip()

    match model:
        case "qwen2.5:0.5b":
            return LLMConfig(
                model=model,
                temperature=0.0,
                top_p=0.05,
                num_predict=MAX_TOKENS_SIMPLE,
                stop_sequences=QWEN_STOP_SEQUENCES,
            )
        case "phi3:mini":
            return LLMConfig(
                model=model,
                temperature=0.0,
                top_p=0.3,
                num_predict=MAX_TOKENS_DETAILED,
                stop_sequences=PHI_STOP_SEQUENCES,
            )
        case "llama3.2:1b":
            return LLMConfig(
                model=model,
                temperature=0.0,
                top_p=0.3,
                num_predict=MAX_TOKENS_DETAILED,
                stop_sequences=PHI_STOP_SEQUENCES,
            )
        case _:
            logger.warning(f"Unknown model '{model}', using default configuration")
            return LLMConfig(
                model=model,
                temperature=0.0,
                top_p=0.3,
                num_predict=MAX_TOKENS_DETAILED,
                stop_sequences=DEFAULT_STOP_SEQUENCES,
            )


def get_extraction_method() -> ExtractionMethod:
    """Get the configured extraction method."""
    method = os.getenv("EXTRACTION_METHOD", "heuristic")
    if not isinstance(method, str):
        logger.warning("EXTRACTION_METHOD environment variable is not a string, using 'heuristic'")
        return "heuristic"

    method = method.strip().lower()
    if method not in ("heuristic", "llm_detailed", "llm_simple"):
        logger.warning(f"Invalid EXTRACTION_METHOD '{method}', using 'heuristic'")
        return "heuristic"

    return method  # type: ignore[return-value]


def get_llm_model() -> str:
    """Get the configured LLM model."""
    model = os.getenv("LLM_MODEL", "phi3:mini")
    if not isinstance(model, str):
        logger.warning("LLM_MODEL environment variable is not a string, using 'phi3:mini'")
        return "phi3:mini"

    model = model.strip()
    # Validate that it's a supported model
    if model not in ("qwen2.5:0.5b", "phi3:mini", "llama3.2:1b"):
        logger.warning(f"Unknown model '{model}', using 'phi3:mini'")
        return "phi3:mini"

    return model
