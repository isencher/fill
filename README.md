# fill

A web application for automatically filling 2D table data into template files.

## Project Overview

**fill** is a document automation tool that:
- Reads structured 2D table data (Excel, CSV, database)
- Maps data fields to template placeholders
- Generates filled documents (DOCX, PDF, etc.)

## Tech Stack

**Status**: Tech stack not yet selected

**Recommended Options**:
- **Python**: FastAPI + pytest (recommended for document processing)
- **Node.js**: Express/Fastify + Vitest

## Project Structure

```
fill/                      # Application project root
├── src/                   # Source code (empty - awaiting implementation)
│   ├── api/              # API endpoints
│   ├── services/         # Business logic
│   ├── models/           # Data models
│   └── utils/            # Utilities
├── tests/                 # Test code (to be created)
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── e2e/              # End-to-end tests
├── .ralph/               # Ralph AI agent configuration
│   ├── AGENT.md          # Build instructions & quality standards
│   ├── PROMPT.md         # Project prompt
│   └── fix_plan.md       # Development tasks
├── .ralphrc              # Ralph configuration
├── pyproject.toml        # Python config (to be created)
├── requirements.txt      # Python dependencies (to be created)
├── package.json          # Node.js config (to be created - optional)
├── Dockerfile            # Container image (to be created)
└── README.md             # This file
```

## Quick Start

### Prerequisites

This project requires the **fill-dev-env** development environment:

```bash
# Set up the development environment (in parent directory)
cd ../
docker-compose up -d
docker-compose exec app bash
```

### Development

```bash
# Inside the development container
cd /app/fill

# Install dependencies (Python - when implemented)
pip install -r requirements.txt

# Run tests
pytest

# Run development server
uvicorn src.main:app --reload
```

## Development Standards

This project follows strict quality standards defined in `.ralph/AGENT.md`:

- **Minimum Test Coverage**: 85%
- **Test Pass Rate**: 100%
- **All Tests Must Pass** before committing
- **Conventional Commits** required
- **All changes pushed** to remote before moving to next feature

## Features

**Status**: Project in setup phase - no features implemented yet

**Planned Features**:
- [ ] File upload (Excel, CSV)
- [ ] Template management
- [ ] Field mapping UI
- [ ] Document generation (DOCX, PDF)
- [ ] Batch processing
- [ ] API for programmatic access

## Testing

```
Target Coverage:
├── Unit Tests:     >90%  (business logic, services)
├── Integration:   >85%  (API endpoints, database)
└── E2E Tests:     100%  (critical user workflows)

Execution Time:
├── Unit + Integration: <30 seconds
└── E2E:              <2 minutes
```

## Documentation

- [Build Instructions](.ralph/AGENT.md) - Setup and quality standards
- [Development Tasks](.ralph/fix_plan.md) - Current development plan
- [Project Context](.ralph/PROMPT.md) - AI agent project prompt

## Parent Project

This application is developed within the **fill-dev-env** infrastructure:

- [fill-dev-env README](../README.md)
- [Docker Requirements](../docker-requirements.md)

## License

[Specify your license]

## Contact

[Specify contact information]
