# Scripts

Utility scripts for testing and benchmarking the action item extraction system.

## Available Scripts

### `compare_methods.py`
Compare all extraction methods side-by-side on the same input text.
```bash
python scripts/compare_methods.py
```

### `benchmark.py`
Benchmark performance of different extraction methods and models.
```bash
python scripts/benchmark.py
```

## Requirements

- Virtual environment activated: `source venv/bin/activate`
- Ollama models pulled: `ollama pull phi3:mini`
