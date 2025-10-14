from __future__ import annotations

import os
import re
from typing import List, Dict, Any
from ollama import chat, Client
from dotenv import load_dotenv

load_dotenv()

# Initialize the client
client = Client()

# Constants
MAX_ACTION_LENGTH = 200  # Filter out overly long responses
MAX_TOKENS_DETAILED = 150  # Limit response length for detailed extraction
MAX_TOKENS_SIMPLE = 50    # Limit response length for simple extraction

# Configuration for extraction method
EXTRACTION_METHOD = os.getenv("EXTRACTION_METHOD", "llm_simple")  # "heuristic", "llm_detailed", or "llm_simple"

# Model selection for LLM methods
LLM_MODEL = os.getenv("LLM_MODEL", "phi3:mini")  # Default to phi3:mini for better reliability

def get_llm_config(model: str) -> Dict[str, Any]:
    """
    Get LLM configuration for a specific model.
    
    Args:
        model: The model name (e.g., 'qwen2.5:0.5b', 'phi3:mini')
        
    Returns:
        Dictionary containing model configuration parameters
    """
    configs = {
        "qwen2.5:0.5b": {
            "model": model,
            "temperature": 0.0,
            "top_p": 0.05,
            "num_predict": MAX_TOKENS_SIMPLE,
            "stop_sequences": [
                "\n\n", "Explanation:", "Note:", "Summary:", "```", "```json", 
                "{", "[", "Step", "Process", "Scan", "Check", "Identify", 
                "Action", "Items", "Found"
            ]
        },
        "phi3:mini": {
            "model": model,
            "temperature": 0.0,
            "top_p": 0.3,
            "num_predict": MAX_TOKENS_DETAILED,
            "stop_sequences": [
                "\n\n", "Output Explanation:", "Explanation:", "Note:", "Summary:", 
                "Output:", "Result:", "Here are", "The extracted", "```", "```json", 
                "{", "[", "Step", "Process"
            ]
        }
    }
    
    # Return config for model, or default to phi3:mini if unknown
    return configs.get(model, configs["phi3:mini"])

# Pull the default model
client.pull("phi3:mini")

# Keyword categories for filtering LLM responses
COMMENTARY_KEYWORDS = [
    'output:', 'result:', 'here are', 'the extracted', 'summary:', 'explanation:',
    'no action items found', 'i\'m sorry', 'cannot provide', 'not provided',
    'step 1:', 'step 2:', 'step 3:', 'step 4:', 'step 5:', 'step 6:',
    'scan', 'check', 'identify', 'process', 'read each line',
    'action items extracted', 'from the text', 'are:',
    'as there are no', 'there are no action items', 'no action items found',
    'i am unable', 'unable to extract', 'no specific tasks',
    'if you have', 'different passage', 'explicit instructions',
    'cannot extract', 'unable to identify', 'no tasks', 'no directives',
    'no actionable content', 'i cannot', 'cannot provide'
]

JSON_ARTIFACTS = [
    '```', '```json', '{', '}', '[', ']', '{"', '"}', '"action":', '"description":',
    '"next":', '"todo":', '",', '"', 'json'
]

def _call_llm_with_fallback(text: str, prompt: str, config: Dict[str, Any]) -> List[str]:
    """
    Common LLM calling logic with fallback to heuristic method.
    
    Args:
        text: Input text to extract action items from
        prompt: The prompt to send to the LLM
        config: LLM configuration dictionary
        
    Returns:
        List of extracted action items, or heuristic fallback on error
    """
    try:
        response = client.chat(
            model=config["model"],
            messages=[
                {
                    'role': 'system', 
                    'content': 'You are a precise action item extractor. Return only cleaned action items, one per line. No explanations or commentary.'
                },
                {
                    'role': 'user', 
                    'content': prompt
                }
            ],
            options={
                'temperature': config["temperature"],
                'top_p': config["top_p"],
                'num_predict': config["num_predict"],
                'stop': config["stop_sequences"]
            }
        )
        
        # Parse and validate response
        actions = response['message']['content'].strip().split('\n')
        validated_actions = _validate_llm_response(actions)
        sanitized_actions = _sanitize_llm_output(validated_actions)
        return _deduplicate_actions(sanitized_actions)
    except Exception as e:
        # Fallback to heuristic method if LLM fails
        print(f"LLM extraction failed: {e}, falling back to heuristic method")
        return extract_action_items(text)

def extract_with_ollama_detailed(text: str) -> List[str]:
    """
    Extract action items using detailed LLM prompting.
    
    Uses comprehensive prompting for complex cases. Falls back to heuristic method if LLM fails.
    
    Args:
        text: Input text to extract action items from
        
    Returns:
        List of cleaned action items
        
    Raises:
        No exceptions (falls back to heuristic on error)
    """
    # Handle edge cases before calling LLM
    if not text or not text.strip():
        return []
    
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
{text}"""

    config = get_llm_config(LLM_MODEL)
    return _call_llm_with_fallback(text, prompt, config)


def _validate_llm_response(actions: List[str]) -> List[str]:
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
        if action.startswith('As there are no'):
            continue
            
        validated.append(action)
    
    return validated


def extract_with_ollama_simple(text: str) -> List[str]:
    """
    Extract action items using simple LLM prompting.
    
    Uses basic prompting for fast extraction. Falls back to heuristic method if LLM fails.
    
    Args:
        text: Input text to extract action items from
        
    Returns:
        List of cleaned action items
        
    Raises:
        No exceptions (falls back to heuristic on error)
    """
    # Handle edge cases before calling LLM
    if not text or not text.strip():
        return []
    
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
{text}"""

    config = get_llm_config(LLM_MODEL)
    return _call_llm_with_fallback(text, prompt, config)


def _sanitize_llm_output(actions: List[str]) -> List[str]:
    """
    Sanitize LLM output to remove formatting artifacts.
    Only handles cleaning, not deduplication.
    """
    cleaned = []
    
    for action in actions:
        if not action.strip():
            continue
            
        # Remove leading bullets and numbering
        action = re.sub(r'^[-*•]\s+', '', action.strip())
        action = re.sub(r'^\d+\.\s+', '', action)
        
        # Remove checkbox markers
        action = re.sub(r'^\[(?:\s|todo)\]\s*', '', action)
        
        # Remove keyword prefixes (case-insensitive)
        action = re.sub(r'^(?:todo|action|next):\s*', '', action, flags=re.IGNORECASE)
        
        # Remove any remaining leading/trailing whitespace
        action = action.strip()
        
        if not action:
            continue
            
        cleaned.append(action)
    
    return cleaned

def _deduplicate_actions(actions: List[str]) -> List[str]:
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


def extract_action_items_unified(text: str) -> List[str]:
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
    """
    if EXTRACTION_METHOD == "heuristic":
        return extract_action_items(text)
    elif EXTRACTION_METHOD == "llm_simple":
        return extract_with_ollama_simple(text)
    elif EXTRACTION_METHOD == "llm_detailed":
        return extract_with_ollama_detailed(text)
    else:
        raise ValueError(f"Unknown EXTRACTION_METHOD: {EXTRACTION_METHOD}. Use 'heuristic', 'llm_detailed', or 'llm_simple'")


BULLET_PREFIX_PATTERN = re.compile(r"^\s*([-*•]|\d+\.)\s+")
KEYWORD_PREFIXES = (
    "todo:",
    "action:",
    "next:",
)


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


def extract_action_items(text: str) -> List[str]:
    lines = text.splitlines()
    extracted: List[str] = []
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
                    cleaned = cleaned[len(prefix):].strip()
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
    unique: List[str] = []
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
