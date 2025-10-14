"""Action item extraction service with multiple extraction methods."""

from __future__ import annotations

import logging
import re
import time
from collections.abc import Generator
from contextlib import contextmanager

from dotenv import load_dotenv
from ollama import Client

from .config import (
    MAX_ACTION_LENGTH,
    LLMConfig,
    get_extraction_method,
    get_llm_config,
    get_llm_model,
)
from .validation import validate_text_input

# Load environment variables
load_dotenv()

# Configure logging
logger = logging.getLogger(__name__)

# Global client instance (lazy initialization)
_client: Client | None = None


def _get_client() -> Client:
    """Get or create the Ollama client with lazy initialization."""
    global _client
    if _client is None:
        try:
            _client = Client()
            logger.info("Ollama client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama client: {e}")
            raise RuntimeError(f"Failed to initialize Ollama client: {e}") from e
    return _client


@contextmanager
def _llm_client_with_retry(
    max_retries: int = 3, base_delay: float = 1.0
) -> Generator[Client, None, None]:
    """
    Context manager for LLM client with retry logic.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds

    Yields:
        Client: The Ollama client

    Raises:
        RuntimeError: If all retry attempts fail
    """
    client = _get_client()

    for attempt in range(max_retries + 1):
        try:
            yield client
            return
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries:
                delay = base_delay * (2**attempt)  # Exponential backoff
                logger.warning(
                    f"LLM connection failed (attempt {attempt + 1}/{max_retries + 1}): {e}. Retrying in {delay}s..."
                )
                time.sleep(delay)
            else:
                logger.error(f"LLM connection failed after {max_retries + 1} attempts: {e}")
                raise RuntimeError(
                    f"LLM connection failed after {max_retries + 1} attempts: {e}"
                ) from e
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {e}")
            raise


# Compile regex patterns once for performance
BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = ("todo:", "action:", "next:")

# Keyword categories for filtering LLM responses
COMMENTARY_KEYWORDS = [
    "output:",
    "result:",
    "here are",
    "the extracted",
    "summary:",
    "explanation:",
    "no action items found",
    "i'm sorry",
    "cannot provide",
    "not provided",
    "step 1:",
    "step 2:",
    "step 3:",
    "step 4:",
    "step 5:",
    "step 6:",
    "scan",
    "check",
    "identify",
    "process",
    "read each line",
    "action items extracted",
    "from the text",
    "are:",
    "as there are no",
    "there are no action items",
    "no action items found",
    "i am unable",
    "unable to extract",
    "no specific tasks",
    "if you have",
    "different passage",
    "explicit instructions",
    "cannot extract",
    "unable to identify",
    "no tasks",
    "no directives",
    "no actionable content",
    "i cannot",
    "cannot provide",
]

JSON_ARTIFACTS = [
    "```",
    "```json",
    "{",
    "}",
    "[",
    "]",
    '{"',
    '"}',
    '"action":',
    '"description":',
    '"next":',
    '"todo":',
    '",',
    '"',
    "json",
]


def _ensure_model_available(model_name: str) -> None:
    """
    Ensure the specified model is available, pulling it if necessary.

    Args:
        model_name: Name of the model to ensure is available

    Raises:
        RuntimeError: If model cannot be pulled or is unavailable
    """
    try:
        with _llm_client_with_retry() as client:
            # Try to use the model first
            try:
                client.chat(
                    model=model_name,
                    messages=[{"role": "user", "content": "test"}],
                    options={"num_predict": 1},
                )
                logger.debug(f"Model {model_name} is already available")
                return
            except Exception:
                # Model not available, try to pull it
                logger.info(f"Model {model_name} not available, attempting to pull...")
                client.pull(model_name)
                logger.info(f"Successfully pulled {model_name} model")
    except Exception as e:
        logger.error(f"Failed to ensure model {model_name} is available: {e}")
        raise RuntimeError(f"Failed to ensure model {model_name} is available: {e}") from e


# Initialize default model on module load
try:
    _ensure_model_available("phi3:mini")
except RuntimeError as e:
    logger.warning(f"Could not initialize default model: {e}")


def _call_llm_with_fallback(text: str, prompt: str, config: LLMConfig) -> list[str]:
    """
    Common LLM calling logic with fallback to heuristic method.

    Args:
        text: Input text to extract action items from
        prompt: The prompt to send to the LLM
        config: LLM configuration object

    Returns:
        List of extracted action items, or heuristic fallback on error
    """
    try:
        with _llm_client_with_retry() as client:
            response = client.chat(
                model=config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a precise action item extractor. Return only cleaned action items, one per line. No explanations or commentary.",
                    },
                    {"role": "user", "content": prompt},
                ],
                options={
                    "temperature": config.temperature,
                    "top_p": config.top_p,
                    "num_predict": config.num_predict,
                    "stop": list(config.stop_sequences),
                },
            )

            # Parse and validate response
            content = response.get("message", {}).get("content", "")
            if not content:
                logger.warning("Empty response from LLM")
                return extract_action_items(text)

            actions = content.strip().split("\n")
            validated_actions = _validate_llm_response(actions)
            sanitized_actions = _sanitize_llm_output(validated_actions)
            return _deduplicate_actions(sanitized_actions)

    except (ConnectionError, TimeoutError) as e:
        logger.error(f"LLM connection failed: {e}, falling back to heuristic method")
        return extract_action_items(text)
    except Exception as e:
        logger.error(f"LLM extraction failed: {e}, falling back to heuristic method")
        return extract_action_items(text)


def extract_with_ollama_detailed(text: str) -> list[str]:
    """
    Extract action items using detailed LLM prompting.

    Uses comprehensive prompting for complex cases. Falls back to heuristic method if LLM fails.

    Args:
        text: Input text to extract action items from

    Returns:
        List of cleaned action items

    Raises:
        ValueError: If text is invalid
        TypeError: If text is not a string
    """
    # Validate input
    validated_text = validate_text_input(text)
    if not validated_text:
        return []

    # Ensure model is available
    model_name = get_llm_model()
    try:
        _ensure_model_available(model_name)
    except RuntimeError as e:
        logger.warning(f"Could not ensure model availability: {e}, falling back to heuristic")
        return extract_action_items(validated_text)

    prompt = f"""You are an action item extractor. Your job is to find and extract actionable items from text.

PROCESS:
1. Read each line of the input text
2. Identify lines that contain action items (bullets, keywords, checkboxes)
3. Clean the formatting and extract just the action text
4. Return each action on its own line

PATTERNS TO FIND:
- Lines starting with: -, *, •, 1., 2., todo:, action:, next:
- Lines containing: [ ] or [todo]

EXAMPLES:
"- [ ] Fix bug" becomes "Fix bug"
"* Implement feature" becomes "Implement feature"
"1. Write tests" becomes "Write tests"
"todo: Deploy app" becomes "Deploy app"

Text:
{validated_text}"""

    config = get_llm_config(model_name)
    return _call_llm_with_fallback(validated_text, prompt, config)


def _validate_llm_response(actions: list[str]) -> list[str]:
    """
    Validate that response contains only action items, no commentary.

    Filters out:
    - Commentary and explanations
    - JSON formatting artifacts
    - Overly long responses
    - Common LLM "no results" responses
    """
    validated = []

    for action in actions:
        action = action.strip()
        if not action:
            continue

        # Skip lines that look like commentary or responses
        if any(commentary in action.lower() for commentary in COMMENTARY_KEYWORDS):
            continue

        # Skip JSON formatting artifacts
        if any(json_artifact in action for json_artifact in JSON_ARTIFACTS):
            continue

        # Skip lines that are too long (likely explanations)
        if len(action) > MAX_ACTION_LENGTH:
            continue

        # Skip lines that start with "As there are no" (common LLM response)
        if action.startswith("As there are no"):
            continue

        validated.append(action)

    return validated


def extract_with_ollama_simple(text: str) -> list[str]:
    """
    Extract action items using simple LLM prompting.

    Uses basic prompting for fast extraction. Falls back to heuristic method if LLM fails.

    Args:
        text: Input text to extract action items from

    Returns:
        List of cleaned action items

    Raises:
        ValueError: If text is invalid
        TypeError: If text is not a string
    """
    # Validate input
    validated_text = validate_text_input(text)
    if not validated_text:
        return []

    # Ensure model is available
    model_name = get_llm_model()
    try:
        _ensure_model_available(model_name)
    except RuntimeError as e:
        logger.warning(f"Could not ensure model availability: {e}, falling back to heuristic")
        return extract_action_items(validated_text)

    prompt = f"""Find action items in this text.

Look for:
- Lines starting with: -, *, •, 1., 2., todo:, action:, next:
- Lines with: [ ] or [todo]

Remove bullets, numbers, brackets, prefixes.
Return only the action text, one per line.

Examples:
"- [ ] Fix bug" → "Fix bug"
"* Implement feature" → "Implement feature"
"1. Write tests" → "Write tests"
"todo: Deploy app" → "Deploy app"

Text:
{validated_text}"""

    config = get_llm_config(model_name)
    return _call_llm_with_fallback(validated_text, prompt, config)


def _sanitize_llm_output(actions: list[str]) -> list[str]:
    """
    Sanitize LLM output to remove formatting artifacts.
    Only handles cleaning, not deduplication.
    """
    cleaned = []

    for action in actions:
        if not action.strip():
            continue

        # Remove leading bullets and numbering
        action = re.sub(r"^[-*•]\s+", "", action.strip())
        action = re.sub(r"^\d+\.\s+", "", action)

        # Remove checkbox markers
        action = re.sub(r"^\[(?:\s|todo)\]\s*", "", action)

        # Remove keyword prefixes (case-insensitive)
        action = re.sub(r"^(?:todo|action|next):\s*", "", action, flags=re.IGNORECASE)

        # Remove any remaining leading/trailing whitespace
        action = action.strip()

        if not action:
            continue

        cleaned.append(action)

    return cleaned


def _deduplicate_actions(actions: list[str]) -> list[str]:
    """
    Remove duplicate actions while preserving order.
    Case-insensitive deduplication.
    """
    seen = set()
    unique = []

    for action in actions:
        lowered = action.lower()
        if lowered not in seen:
            seen.add(lowered)
            unique.append(action)

    return unique


def extract_action_items_unified(text: str) -> list[str]:
    """
    Unified extraction function that routes to the configured method.

    Set EXTRACTION_METHOD environment variable to:
    - "heuristic" for rule-based extraction (fastest, most reliable)
    - "llm_detailed" for comprehensive LLM extraction (phi3:mini)
    - "llm_simple" for basic LLM extraction (qwen2.5:0.5b)

    Args:
        text: Input text to extract action items from

    Returns:
        List of extracted action items

    Raises:
        ValueError: If EXTRACTION_METHOD is not recognized
        TypeError: If text is not a string
    """
    # Validate input
    validated_text = validate_text_input(text)
    if not validated_text:
        return []

    method = get_extraction_method()

    try:
        match method:
            case "heuristic":
                return extract_action_items(validated_text)
            case "llm_simple":
                return extract_with_ollama_simple(validated_text)
            case "llm_detailed":
                return extract_with_ollama_detailed(validated_text)
            case _:
                raise ValueError(
                    f"Unknown EXTRACTION_METHOD: {method}. "
                    f"Use 'heuristic', 'llm_detailed', or 'llm_simple'"
                )
    except Exception as e:
        logger.error(f"Extraction failed with method '{method}': {e}")
        # Fallback to heuristic method for any unexpected errors
        logger.info("Falling back to heuristic extraction method")
        return extract_action_items(validated_text)


# These are already defined above, removing duplication


def _is_action_line(line: str) -> bool:
    stripped = line.strip().lower()
    if not stripped:
        return False
    if BULLET_PREFIX_PATTERN.match(stripped):
        return True
    if any(stripped.startswith(prefix) for prefix in KEYWORD_PREFIXES):
        return True
    if "[ ]" in stripped or "[todo]" in stripped:
        return True
    return False


def extract_action_items(text: str) -> list[str]:
    lines = text.splitlines()
    extracted: list[str] = []
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        if _is_action_line(line):
            cleaned = BULLET_PREFIX_PATTERN.sub("", line)
            cleaned = cleaned.strip()
            # Trim common checkbox markers
            cleaned = cleaned.removeprefix("[ ]").strip()
            cleaned = cleaned.removeprefix("[todo]").strip()
            # Remove keyword prefixes
            for prefix in KEYWORD_PREFIXES:
                if cleaned.lower().startswith(prefix):
                    cleaned = cleaned[len(prefix) :].strip()
                    break
            extracted.append(cleaned)
    # Fallback: if nothing matched, heuristically split into sentences and pick imperative-like ones
    if not extracted:
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())
        for sentence in sentences:
            s = sentence.strip()
            if not s:
                continue
            if _looks_imperative(s):
                extracted.append(s)
    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: list[str] = []
    for item in extracted:
        lowered = item.lower()
        if lowered in seen:
            continue
        seen.add(lowered)
        unique.append(item)
    return unique


def _looks_imperative(sentence: str) -> bool:
    words = re.findall(r"[A-Za-z']+", sentence)
    if not words:
        return False
    first = words[0]
    # Crude heuristic: treat these as imperative starters
    imperative_starters = {
        "add",
        "create",
        "implement",
        "fix",
        "update",
        "write",
        "check",
        "verify",
        "refactor",
        "document",
        "design",
        "investigate",
    }
    return first.lower() in imperative_starters
