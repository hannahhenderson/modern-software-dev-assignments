from __future__ import annotations

import os
import re
from typing import List
import json
from typing import Any
from ollama import chat, Client
from dotenv import load_dotenv

load_dotenv()

#Initialize the client
client = Client()

# Configuration for extraction method
EXTRACTION_METHOD = os.getenv("EXTRACTION_METHOD", "ollama")  # "heuristic", "ollama", or "simple_ollama"

# Model Recommendations (smallest to larger)
# qwen2.5:0.5b - 0.5B params, very fast, basic extraction
# phi3:mini - 3.8B params, good balance of speed/quality
# llama3.2:1b - 1B params, slightly better reasoning
# qwen2.5:1.5b - 1.5B params, good for structured tasks

# Pull the smallest model
client.pull("phi3:mini")

def extract_with_ollama(text: str) -> List[str]:
    prompt = f"""Extract action items from the input text.

Detection rules:
- Match lines with bullets (-, *, •, 1., 2., …)
- Match lines starting with: todo:, action:, next: (case-insensitive)
- Match lines containing [ ] or [todo]

Cleaning rules:
- Remove leading bullets or numbering
- Remove [ ] and [todo]
- Remove leading prefixes: todo:, action:, next:
- Keep only the core action text

CRITICAL: Return ONLY the cleaned action items. Do not add explanations, summaries, or commentary.

Input:
{text}"""

    response = client.chat(
        model='phi3:mini',
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
            'temperature': 0,  # Maximum determinism
            'num_predict': 200,  # Much shorter limit
            'stop': ["\n\n", "Output Explanation:", "Explanation:", "Note:", "Summary:", "Output:", "Result:", "Here are", "The extracted"]
        }
    )
    
    # Parse and validate response
    actions = response['message']['content'].strip().split('\n')
    validated_actions = _validate_llm_response(actions)
    return _sanitize_llm_output(validated_actions)


def _validate_llm_response(actions: List[str]) -> List[str]:
    """Validate that response contains only action items, no commentary."""
    validated = []
    
    for action in actions:
        action = action.strip()
        if not action:
            continue
        # Skip lines that look like commentary
        if any(commentary in action.lower() for commentary in [
            'output:', 'result:', 'here are', 'the extracted', 'summary:', 'explanation:'
        ]):
            continue
        validated.append(action)
    
    return validated


def simple_extract_with_ollama(text: str) -> List[str]:
    prompt = f"""Find action items in the text.

Rules:
- Detect bullets (-, *, •, 1., 2.), keyword prefixes (todo:, action:, next:), and [ ] or [todo]
- Strip bullets/numbering, [ ]/[todo], and prefixes (todo:, action:, next:)
- Keep only the action text

Output:
- Each action on its own line
- No bullets, numbers, brackets, prefixes, or explanations
- No quotes, no extra text

Text:
{text}"""

    response = client.chat(
        model='qwen2.5:0.5b',  # Even smaller
        messages=[{'role': 'user', 'content': prompt}],
        options={
            'temperature': 0,
            'stop': ["\n\n", "Explanation:", "Note:", "Summary:"]
        }
    )
    
    # Parse and sanitize response
    actions = response['message']['content'].strip().split('\n')
    return _sanitize_llm_output(actions)


def _sanitize_llm_output(actions: List[str]) -> List[str]:
    """
    Sanitize LLM output to remove formatting artifacts and ensure clean action items.
    """
    cleaned = []
    seen = set()
    
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
            
        # Deduplicate case-insensitively
        lowered = action.lower()
        if lowered not in seen:
            seen.add(lowered)
            cleaned.append(action)
    
    return cleaned


def extract_action_items_unified(text: str) -> List[str]:
    """
    Unified extraction function that routes to the configured method.
    Set EXTRACTION_METHOD environment variable to:
    - "heuristic" for rule-based extraction
    - "ollama" for LLM extraction with phi3:mini
    - "simple_ollama" for LLM extraction with qwen2.5:0.5b
    """
    if EXTRACTION_METHOD == "heuristic":
        return extract_action_items(text)
    elif EXTRACTION_METHOD == "simple_ollama":
        return simple_extract_with_ollama(text)
    elif EXTRACTION_METHOD == "ollama":
        return extract_with_ollama(text)
    else:
        raise ValueError(f"Unknown EXTRACTION_METHOD: {EXTRACTION_METHOD}. Use 'heuristic', 'ollama', or 'simple_ollama'")


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
