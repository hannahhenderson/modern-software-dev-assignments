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

| Method | Speed | Accuracy | Reliability |
|--------|-------|----------|-------------|
| heuristic | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| simple_ollama (phi3:mini) | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| simple_ollama (qwen2.5:0.5b) | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ |
| ollama (phi3:mini) | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

## Recommendations

- **Production**: Use `heuristic` for reliability
- **Development**: Use `simple_ollama` with `phi3:mini` for good balance
- **Testing**: Use `simple_ollama` with `qwen2.5:0.5b` for speed
- **Fallback**: LLM methods automatically fall back to heuristic on failure
