"""Configuration management for action item extraction."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Literal, TypedDict

logger = logging.getLogger(__name__)

# Type definitions
ExtractionMethod = Literal["heuristic", "llm_detailed", "llm_simple"]
ModelName = Literal["qwen2.5:0.5b", "phi3:mini", "llama3.2:1b"]


class LLMConfigDict(TypedDict):
    """Configuration for LLM model parameters."""

    model: str
    temperature: float
    top_p: float
    num_predict: int
    stop_sequences: list[str]


# Constants
MAX_ACTION_LENGTH = 200
MAX_TOKENS_DETAILED = 150
MAX_TOKENS_SIMPLE = 50

# Model-specific stop sequences
QWEN_STOP_SEQUENCES = [
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
]

PHI_STOP_SEQUENCES = [
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
]

DEFAULT_STOP_SEQUENCES = ["\n\n", "Explanation:", "```", "{", "["]


@lru_cache(maxsize=32)
def get_llm_config(model: str) -> LLMConfigDict:
    """
    Get LLM configuration for a specific model.

    Args:
        model: The model name (e.g., 'qwen2.5:0.5b', 'phi3:mini')

    Returns:
        Dictionary containing model configuration parameters

    Raises:
        ValueError: If model is not supported
    """
    if model == "qwen2.5:0.5b":
        return LLMConfigDict(
            model=model,
            temperature=0.0,
            top_p=0.05,
            num_predict=MAX_TOKENS_SIMPLE,
            stop_sequences=QWEN_STOP_SEQUENCES.copy(),
        )
    elif model == "phi3:mini":
        return LLMConfigDict(
            model=model,
            temperature=0.0,
            top_p=0.3,
            num_predict=MAX_TOKENS_DETAILED,
            stop_sequences=PHI_STOP_SEQUENCES.copy(),
        )
    elif model == "llama3.2:1b":
        return LLMConfigDict(
            model=model,
            temperature=0.0,
            top_p=0.3,
            num_predict=MAX_TOKENS_DETAILED,
            stop_sequences=PHI_STOP_SEQUENCES.copy(),
        )
    else:
        logger.warning(f"Unknown model '{model}', using default configuration")
        return LLMConfigDict(
            model=model,
            temperature=0.0,
            top_p=0.3,
            num_predict=MAX_TOKENS_DETAILED,
            stop_sequences=DEFAULT_STOP_SEQUENCES.copy(),
        )


def get_extraction_method() -> ExtractionMethod:
    """Get the configured extraction method."""
    method = os.getenv("EXTRACTION_METHOD", "heuristic")
    if method not in ("heuristic", "llm_detailed", "llm_simple"):
        logger.warning(f"Invalid EXTRACTION_METHOD '{method}', using 'heuristic'")
        return "heuristic"
    return method  # type: ignore[return-value]


def get_llm_model() -> str:
    """Get the configured LLM model."""
    model = os.getenv("LLM_MODEL", "phi3:mini")
    # Validate that it's a supported model
    if model not in ("qwen2.5:0.5b", "phi3:mini", "llama3.2:1b"):
        logger.warning(f"Unknown model '{model}', using 'phi3:mini'")
        return "phi3:mini"
    return model
