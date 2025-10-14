# Action Item Extraction Configuration

## Environment Variables

### EXTRACTION_METHOD
Controls which extraction method to use:
- `heuristic` - Rule-based extraction (fastest, most reliable)
- `ollama` - Full LLM extraction with detailed prompts
- `simple_ollama` - Simplified LLM extraction (default)

### LLM_MODEL
Controls which Ollama model to use for LLM extraction:
- `qwen2.5:0.5b` - 0.5B parameters, very fast, basic extraction
- `phi3:mini` - 3.8B parameters, good balance (default)
- `llama3.2:1b` - 1B parameters, slightly better reasoning

## Usage Examples

```bash
# Use heuristic method (fastest)
export EXTRACTION_METHOD=heuristic

# Use simple LLM with phi3:mini (default)
export EXTRACTION_METHOD=simple_ollama
export LLM_MODEL=phi3:mini

# Use simple LLM with smallest model
export EXTRACTION_METHOD=simple_ollama
export LLM_MODEL=qwen2.5:0.5b

# Use full LLM extraction
export EXTRACTION_METHOD=ollama
export LLM_MODEL=phi3:mini
```

## Performance Characteristics

| Method | Speed | Accuracy | Reliability | Notes |
|--------|-------|----------|-------------|-------|
| heuristic | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Most reliable, but limited to line-by-line patterns |
| simple_ollama (phi3:mini) | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | Good balance, sometimes misses items or adds extras |
| simple_ollama (qwen2.5:0.5b) | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | Very fast but inconsistent, often adds creative content |
| ollama (phi3:mini) | ⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | More detailed extraction, better at complex cases |

## Recommendations

- **Production**: Use `heuristic` for maximum reliability and consistency
- **Development**: Use `simple_ollama` with `phi3:mini` for good balance (default)
- **Testing**: Use `simple_ollama` with `qwen2.5:0.5b` for speed (may be inconsistent)
- **Complex Cases**: Use `ollama` with `phi3:mini` for better reasoning
- **Fallback**: LLM methods automatically fall back to heuristic on failure

## Current Status

The LLM methods have been optimized with:
- ✅ Chain-of-thought prompting for better reasoning
- ✅ Model-specific parameters (temperature, top_p, num_predict)
- ✅ Enhanced stop sequences to prevent rambling
- ✅ Improved validation to filter out commentary
- ✅ Error handling with automatic fallback to heuristic

**Note**: Small models (qwen2.5:0.5b) may still be inconsistent and add creative content. For production use, consider the heuristic method for maximum reliability.

## Accuracy Limitations

### Heuristic Method (3 stars)
- ✅ Excellent for standard bullet points, checkboxes, numbered lists
- ❌ Cannot extract actions embedded in sentences ("We need to todo: fix the bug")
- ❌ Extracts entire lines with mixed content ("Meeting notes: - [ ] Task")
- ❌ Very literal, no context understanding

### LLM Methods (3-4 stars)
- ✅ Can understand context and extract embedded actions
- ✅ Better at handling complex, mixed content
- ❌ Sometimes inconsistent or adds creative content
- ❌ May miss items or add extras depending on model size
