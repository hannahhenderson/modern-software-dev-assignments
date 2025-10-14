# Action Item Extractor

A modern FastAPI application for extracting actionable items from text using both heuristic and LLM-powered methods. The application provides a web interface and REST API for processing notes and managing action items with persistent storage.

## 🚀 Features

- **Multiple Extraction Methods**: Heuristic pattern matching and LLM-powered extraction
- **Interactive Web Interface**: Clean, responsive frontend for easy use
- **REST API**: Comprehensive API with automatic documentation
- **Persistent Storage**: SQLite database for notes and action items
- **Real-time Management**: Mark action items as done/not done
- **Modern Python**: Built with Python 3.12+ features and best practices
- **Type Safety**: Full type hints with MyPy validation
- **Code Quality**: Ruff linting and formatting, comprehensive testing

## 🏗️ Architecture

```
app/
├── main.py              # FastAPI application entry point
├── models.py            # Pydantic models for API validation
├── db.py               # Database operations and connection management
├── routers/            # API route handlers
│   ├── action_items.py # Action item endpoints
│   └── notes.py        # Note management endpoints
└── services/           # Business logic
    ├── config.py       # LLM configuration management
    ├── extract.py      # Extraction algorithms
    └── validation.py   # Input validation and sanitization
```

## 🛠️ Setup and Installation

### Prerequisites

- Python 3.12+
- Virtual environment (recommended)

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd week2
   ```

2. **Create and activate virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn pydantic ollama pytest mypy ruff
   ```

4. **Initialize the database** (automatic on first run):
   ```bash
   python -c "from app.db import init_db; init_db()"
   ```

### Running the Application

**Start the development server**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The application will be available at:
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📡 API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Web interface |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Interactive API documentation |

### Action Items

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/action-items/extract` | Extract action items (heuristic method) |
| `POST` | `/action-items/extract-llm` | Extract action items (LLM method) |
| `GET` | `/action-items` | List all action items |
| `GET` | `/action-items/all-records` | Get all notes and action items |
| `POST` | `/action-items/{id}/done` | Mark action item as done/not done |

### Notes

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/notes` | Create a new note |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/{id}` | Get specific note |

### Request/Response Examples

**Extract Action Items**:
```bash
curl -X POST "http://localhost:8000/action-items/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Meeting notes:\n- [ ] Set up database\n- [ ] Implement API\n- [ ] Write tests",
    "save_note": true
  }'
```

**List All Records**:
```bash
curl -X GET "http://localhost:8000/action-items/all-records"
```

## 🧪 Testing

### Run Test Suite

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test file
pytest tests/test_extract.py -v
```

### Test Coverage

The test suite covers:
- ✅ Heuristic extraction algorithms
- ✅ LLM-powered extraction methods
- ✅ Input validation and edge cases
- ✅ Database operations
- ✅ API endpoint functionality

## 🔧 Development Tools

### Code Quality

**Linting and Formatting**:
```bash
# Check code style and fix issues
ruff check . && ruff format .

# Type checking
mypy app/
```

**Run All Quality Checks**:
```bash
ruff check . && ruff format . && mypy app/ && pytest tests/ -v
```

### Database Management

**View Database Contents**:
```bash
sqlite3 data/app.db "SELECT COUNT(*) FROM notes;"
sqlite3 data/app.db "SELECT COUNT(*) FROM action_items;"
```

**Reset Database**:
```bash
rm data/app.db
python -c "from app.db import init_db; init_db()"
```

## 🎯 Usage Examples

### Web Interface

1. Navigate to http://localhost:8000
2. Paste your notes in the text area
3. Choose extraction method:
   - **Extract**: Heuristic pattern matching
   - **Extract LLM**: AI-powered extraction
   - **List Notes**: View all stored records
4. Toggle "Save as note" to persist the original text
5. Check/uncheck action items to mark them as done

### API Integration

**Python Example**:
```python
import requests

# Extract action items
response = requests.post("http://localhost:8000/action-items/extract", json={
    "text": "Project tasks:\n- [ ] Design database schema\n- [ ] Implement API endpoints",
    "save_note": True
})

action_items = response.json()["items"]
print(f"Extracted {len(action_items)} action items")
```

**JavaScript Example**:
```javascript
// Extract action items
const response = await fetch('/action-items/extract', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: 'Meeting notes:\n- [ ] Review proposal\n- [ ] Schedule follow-up',
        save_note: true
    })
});

const data = await response.json();
console.log('Action items:', data.items);
```

## 🔧 Configuration

### Environment Variables

The application supports the following environment variables:

- `OLLAMA_HOST`: Ollama server URL (default: `http://localhost:11434`)
- `OLLAMA_MODEL`: Default LLM model (default: `qwen2.5:0.5b`)

### LLM Models

Supported models for extraction:
- `qwen2.5:0.5b` (default)
- `qwen2.5:1.5b`
- `qwen2.5:3b`
- `qwen2.5:7b`

## 🚨 Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Check if database file exists
ls -la data/app.db

# Recreate database
rm data/app.db
python -c "from app.db import init_db; init_db()"
```

**LLM Connection Issues**:
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama server
ollama serve
```

**Port Already in Use**:
```bash
# Use different port
uvicorn app.main:app --reload --port 8001
```

### Logs and Debugging

**Enable Debug Logging**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**View Application Logs**:
The application logs to stdout with structured logging including timestamps, log levels, and contextual information.

## 📊 Performance

### Benchmarks

The application includes benchmark scripts in the `scripts/` directory:

```bash
# Run performance benchmarks
python scripts/benchmark.py

# Compare extraction methods
python scripts/compare_methods.py
```

### Optimization Tips

- Use heuristic extraction for simple, well-formatted text
- Use LLM extraction for complex, unstructured content
- Enable database indexing for large datasets
- Consider connection pooling for high-traffic scenarios

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make changes with proper tests
4. Run quality checks: `ruff check . && mypy app/ && pytest tests/`
5. Submit a pull request

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Include tests for new features
- Use meaningful variable and function names

## 📄 License

This project is part of a Stanford Modern Software Development course assignment.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the API documentation at `/docs`
3. Examine the test cases for usage examples
4. Check application logs for error details

---

**Built with ❤️ using FastAPI, Python 3.12+, and modern development practices.**
