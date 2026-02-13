# Agent Build Instructions - fill Project

## Project Setup
```bash
# Install dependencies
cd /app/fill-dev-env/fill
pip install -r requirements.txt
```

## Running Tests
```bash
# Run all tests
cd /app/fill-dev-env/fill
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_main.py

# Run with coverage report
pytest --cov=src --cov-report=html
```

## Development Server
```bash
# Start development server with auto-reload
cd /app/fill-dev-env/fill
uvicorn src.main:app --reload --host 0.0.0.0 --port 3000

# Or use the module syntax
python -m uvicorn src.main:app --reload --port 3000
```

## API Documentation
When the server is running, access:
- API Docs (Swagger UI): http://localhost:3000/docs
- ReDoc: http://localhost:3000/redoc
- OpenAPI JSON: http://localhost:3000/openapi.json

## Testing the API
```bash
# Test root endpoint
curl http://localhost:3000/

# Or use TestClient in Python tests
```

## Key Learnings
- FastAPI provides auto-generated OpenAPI docs at /docs
- Use TestClient for HTTP testing without starting a server
- Coverage threshold is set to 85% in pyproject.toml
- Tests use pytest with asyncio, mock, and faker fixtures

## Project Structure
- `src/main.py`: FastAPI application entry point
- `src/api/`: API endpoint modules (future)
- `src/services/`: Business logic layer (future)
- `src/models/`: Data models (future)
- `tests/unit/`: Unit tests for individual components
- `tests/integration/`: Integration tests for API endpoints (future)
- `tests/e2e/`: End-to-end tests with Playwright (future)
